"""
AI 学习助手页面 - PySide6 美化版

支持：
- 模型来源切换 (Ollama / 本地 GGUF / API)
- 模型选择和刷新
- 知识库嵌入模型选择
- 知识库检索开关
- 美化对话界面
- 流式响应
"""

import json
import os
from typing import Callable, Optional

import requests  # 性能优化：模块级别导入一次
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# 颜色方案
COLORS = {
    "bg": "#0d0e1a",
    "surface": "#12131f",
    "surface2": "#1a1b2e",
    "surface3": "#1e2035",
    "border": "rgba(80,120,255,0.13)",
    "border2": "rgba(80,120,255,0.22)",
    "accent": "#4a7fff",
    "accent_bg": "rgba(74,127,255,0.1)",
    "accent_glow": "rgba(74,127,255,0.2)",
    "amber": "#f0a500",
    "green": "#3ddc84",
    "red": "#ff5f57",
    "text": "#cdd6f4",
    "text_dim": "#6c7a9c",
    "text_faint": "#3a4260",
}


class AIChatAPI:
    """AI 聊天 API 接口类 - 预留可扩展"""

    def __init__(self):
        self.provider = "ollama"  # ollama / gguf / openai / anthropic / custom

    def chat(
        self,
        model: str,
        messages: list,
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """
        发送聊天请求

        Args:
            model: 模型名称
            messages: 消息列表 [{"role": "user/assistant/system", "content": "..."}]
            stream: 是否流式输出
            callback: 流式输出回调函数

        Returns:
            str: AI 回复内容
        """
        if self.provider == "ollama":
            return self._ollama_chat(model, messages, stream, callback)
        elif self.provider == "openai":
            return self._openai_chat(model, messages, stream, callback)
        elif self.provider == "anthropic":
            return self._anthropic_chat(model, messages, stream, callback)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _ollama_chat(
        self,
        model: str,
        messages: list,
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Ollama API - 性能优化：使用list替代字符串拼接"""
        url = "http://localhost:11434/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        if stream and callback:
            # 流式输出 - 使用list收集内容最后join，避免频繁字符串拼接
            response = requests.post(url, json=payload, stream=True, timeout=120)
            content_parts = []
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    content_parts.append(content)
                    callback(content)
            return "".join(content_parts)
        else:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")

    def _openai_chat(
        self,
        model: str,
        messages: list,
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """OpenAI API - 预留"""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise Exception("OPENAI_API_KEY not set")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=120)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")

    def _anthropic_chat(
        self,
        model: str,
        messages: list,
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Anthropic API - 预留"""
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY not set")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        # 转换消息格式
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "max_tokens": 1024,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=120)
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            raise Exception(f"Anthropic API error: {response.status_code}")

    def set_provider(self, provider: str):
        """设置 API 提供商"""
        self.provider = provider


class OllamaWorker(QThread):
    """Ollama 后台工作线程"""

    response_ready = Signal(str)
    error_occurred = Signal(str)
    thinking_started = Signal()
    thinking_stopped = Signal()

    def __init__(self, api: AIChatAPI, model: str, messages: list):
        super().__init__()
        self.api = api
        self.model = model
        self.messages = messages

    def run(self):
        try:
            self.thinking_started.emit()
            response = self.api.chat(self.model, self.messages, stream=False)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.thinking_stopped.emit()


class OllamaCheckWorker(QThread):
    """Ollama 服务检测后台工作线程 - 性能优化：避免阻塞UI"""

    # 信号：模型列表、嵌入模型列表、错误信息
    check_complete = Signal(list, list, bool, str)

    def run(self):
        """后台检测 Ollama 服务"""
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=5)
            if r.status_code == 200:
                models = r.json().get("models", [])
                chat_models = []
                embed_models = []

                for m in models:
                    name = m.get("name", "")
                    # 嵌入模型通常以 "nomic-embed-text" 或 "-embedding" 结尾
                    if "embed" in name.lower() or "nomic" in name.lower():
                        embed_models.append(name)
                    else:
                        chat_models.append(name)

                self.check_complete.emit(chat_models, embed_models, True, "")
            else:
                self.check_complete.emit([], [], False, f"HTTP {r.status_code}")
        except requests.Timeout:
            self.check_complete.emit([], [], False, "连接超时")
        except requests.ConnectionError:
            self.check_complete.emit([], [], False, "连接失败")
        except Exception as e:
            self.check_complete.emit([], [], False, str(e))


class ChatPage(QWidget):
    """AI 学习助手页面"""

    # 信号
    message_sent = Signal(str)  # 发送消息
    clear_requested = Signal()  # 清空对话

    def __init__(self, mode: str = "learning"):
        super().__init__()
        self.mode = mode
        self.messages = []  # 对话历史
        self.current_model = None
        self.available_models = []  # 对话模型
        self.available_embed_models = []  # 嵌入模型
        self.model_source = "ollama"  # ollama / gguf / api
        self.kb_enabled = True  # 知识库开关
        self.ollama_connected = False
        self.api = AIChatAPI()  # API 接口实例
        self.current_worker = None  # 当前工作线程
        self.ollama_check_worker = None  # Ollama 检测工作线程

        # 系统提示词
        self.system_prompt = self._get_system_prompt()

        self._init_ui()
        self._connect_signals()
        # 性能优化：使用异步方式检测 Ollama，避免阻塞UI
        self._start_ollama_check()
        self._load_embed_models()

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        prompts = {
            "learning": """你是一个CAE学习助手，专注于机械设计和有限元分析领域。

使用费曼学习法回答问题：
1. 用简单的语言解释概念
2. 举出工程实例
3. 如果有公式，说明物理意义

用中文教学式回答，适合大一学生学习。""",
            "mechanical": """你是一个机械设计专家，专注于CAD/CAE领域。

回答要求：
1. 专业准确
2. 结合实际应用
3. 给出设计建议

用中文回答。""",
            "default": """你是一个工程领域的AI助手。

用中文回答问题，保持专业但易懂。""",
        }
        return prompts.get(self.mode, prompts["default"])

    def _init_ui(self):
        """初始化UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg']};
                color: {COLORS['text']};
                font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
                font-size: 13px;
            }}
            QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['surface3']};
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['text_dim']};
            }}
            QScrollBar:horizontal {{
                display: none;
            }}
        """)

        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧面板
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 0)

        # 右侧面板
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 1)

    def _create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        panel.setFixedWidth(280)
        panel.setStyleSheet(f"background-color: {COLORS['surface']};")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 头部
        header = QWidget()
        header.setStyleSheet(f"background-color: {COLORS['surface']}; border-bottom: 1px solid {COLORS['border']};")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 18, 16, 12)

        title = QLabel("AI 学习助手")
        title.setFont(QFont("Microsoft YaHei UI", 15, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        header_layout.addWidget(title)

        layout.addWidget(header)

        # 设置区
        settings = QWidget()
        settings.setStyleSheet(f"background-color: {COLORS['surface']};")
        settings_layout = QVBoxLayout(settings)
        settings_layout.setContentsMargins(16, 16, 16, 16)
        settings_layout.setSpacing(18)

        # 模型来源
        self._add_field(settings_layout, "模型来源", self._create_source_toggle())

        # 选择模型（点击展开）
        self._add_field(settings_layout, "对话模型", self._create_model_selector())

        # 刷新按钮已集成到模型选择器中

        # 嵌入模型（知识库用）
        self._add_field(settings_layout, "知识库嵌入模型", self._create_embed_model_select())

        # API 设置
        self._add_field(settings_layout, "API 设置", self._create_api_settings())

        # 知识库开关
        self._add_field(settings_layout, "功能", self._create_kb_toggle())

        settings_layout.addStretch()
        layout.addWidget(settings, 1)

        # 状态栏
        status = self._create_status_bar()
        layout.addWidget(status)

        return panel

    def _add_field(self, parent, label: str, widget: QWidget):
        """添加设置项"""
        if label:
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Microsoft YaHei UI", 11, QFont.Weight.Bold))
            label_widget.setStyleSheet(f"color: {COLORS['text_dim']}; letter-spacing: 0.06em; margin-top: 8px;")
            parent.addWidget(label_widget)
        parent.addWidget(widget)

    def _create_source_toggle(self) -> QWidget:
        """模型来源切换"""
        container = QWidget()
        container.setStyleSheet(f"""
            background-color: {COLORS['bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 4px;
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.source_group = QButtonGroup(self)
        self.source_group.setExclusive(True)

        # Ollama
        self.ollama_btn = self._create_source_btn("Ollama", True)
        self.ollama_btn.clicked.connect(lambda: self._switch_source("ollama"))
        self.source_group.addButton(self.ollama_btn)
        layout.addWidget(self.ollama_btn, 1)

        # API
        self.api_btn = self._create_source_btn("API", False)
        self.api_btn.clicked.connect(lambda: self._switch_source("api"))
        self.source_group.addButton(self.api_btn)
        layout.addWidget(self.api_btn, 1)

        # GGUF
        self.gguf_btn = self._create_source_btn("GGUF", False)
        self.gguf_btn.clicked.connect(lambda: self._switch_source("gguf"))
        self.source_group.addButton(self.gguf_btn)
        layout.addWidget(self.gguf_btn, 1)

        return container

    def _create_source_btn(self, text: str, is_active: bool) -> QPushButton:
        """创建来源按钮"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(is_active)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Microsoft YaHei UI", 11))
        btn.setFixedHeight(32)

        if is_active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_dim']};
                    border: none;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    color: {COLORS['text']};
                    background-color: {COLORS['surface3']};
                }}
            """)

        return btn

    def _create_model_selector(self) -> QWidget:
        """可展开的模型选择器（默认隐藏，点击展开）"""
        # 创建一个容器，初始只有按钮
        self.model_selector_container = QWidget()
        self.model_selector_container.setStyleSheet(
            f"background-color: {COLORS['bg']}; border: 1px solid {COLORS['border']}; border-radius: 8px;"
        )

        self.model_selector_layout = QVBoxLayout(self.model_selector_container)
        self.model_selector_layout.setContentsMargins(0, 0, 0, 0)
        self.model_selector_layout.setSpacing(0)

        # 点击按钮（默认显示）
        self.model_select_btn = QPushButton("▼ 点击展开选择模型")
        self.model_select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.model_select_btn.setFixedHeight(36)
        self.model_select_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {COLORS['text_dim']};
                font-size: 12px;
                padding: 0 12px;
                text-align: center;
            }}
            QPushButton:hover {{
                color: {COLORS['accent']};
            }}
        """)
        self.model_select_btn.clicked.connect(self._toggle_model_selector)
        self.model_selector_layout.addWidget(self.model_select_btn)

        # 保存引用
        self.model_selector_expanded = False

        return self.model_selector_container

    def _toggle_model_selector(self):
        """切换模型选择器显示"""
        if self.model_selector_expanded:
            # 收起 - 移除展开的内容，只保留按钮
            while self.model_selector_layout.count() > 1:
                item = self.model_selector_layout.takeAt(1)
                if item.widget():
                    item.widget().deleteLater()

            self.model_select_btn.setText("▼ 点击展开选择模型")
            self.model_selector_expanded = False
        else:
            # 展开 - 在按钮下方添加选择框

            # 创建下拉框容器
            selector_content = QWidget()
            selector_content.setStyleSheet(f"background-color: {COLORS['bg']};")
            selector_layout = QVBoxLayout(selector_content)
            selector_layout.setContentsMargins(12, 8, 12, 12)
            selector_layout.setSpacing(10)

            # 模型下拉框
            self.model_combo = QComboBox()
            self.model_combo.setFixedHeight(38)
            self.model_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {COLORS['surface2']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    color: {COLORS['text']};
                    padding: 0 12px;
                    font-size: 12px;
                }}
                QComboBox:hover {{ border-color: {COLORS['border2']}; }}
                QComboBox:focus {{ border-color: {COLORS['accent']}; }}
                QComboBox::drop-down {{ border: none; width: 24px; }}
                QComboBox QAbstractItemView {{
                    background-color: {COLORS['surface2']};
                    border: 1px solid {COLORS['border']};
                    color: {COLORS['text']};
                    selection-background-color: {COLORS['accent']};
                }}
            """)
            self.model_combo.addItem("-- 请选择模型 --")
            if self.available_models:
                self.model_combo.addItems(self.available_models)
            selector_layout.addWidget(self.model_combo)

            # 刷新按钮
            self.refresh_btn = QPushButton("↻ 刷新模型列表")
            self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.refresh_btn.setFixedHeight(34)
            self.refresh_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['surface3']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    color: {COLORS['text_dim']};
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    color: {COLORS['text']};
                    border-color: {COLORS['accent']};
                    background-color: {COLORS['surface2']};
                }}
            """)
            self.refresh_btn.clicked.connect(self._refresh_models)
            selector_layout.addWidget(self.refresh_btn)

            # 添加到容器
            self.model_selector_layout.addWidget(selector_content)

            self.model_select_btn.setText("▲ 点击收起")
            self.model_selector_expanded = True

    def _create_model_select(self) -> QWidget:
        """对话模型选择"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.model_combo = QComboBox()
        self.model_combo.setFixedHeight(36)
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text']};
                padding: 0 12px;
                font-size: 12px;
            }}
            QComboBox:hover {{ border-color: {COLORS['border2']}; }}
            QComboBox:focus {{ border-color: {COLORS['accent']}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['surface2']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['accent']};
            }}
        """)
        self.model_combo.addItem("-- 请选择模型 --")
        layout.addWidget(self.model_combo, 1)

        return container

    def _create_refresh_btn(self) -> QWidget:
        """刷新模型按钮"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.refresh_btn = QPushButton("↻ 刷新模型列表")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setFixedHeight(34)
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface3']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text_dim']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {COLORS['text']};
                border-color: {COLORS['accent']};
                background-color: {COLORS['surface2']};
            }}
        """)
        self.refresh_btn.clicked.connect(self._refresh_models)
        layout.addWidget(self.refresh_btn)

        return container

    def _create_embed_model_select(self) -> QWidget:
        """知识库嵌入模型选择"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.embed_model_combo = QComboBox()
        self.embed_model_combo.setFixedHeight(36)
        self.embed_model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text']};
                padding: 0 12px;
                font-size: 12px;
            }}
            QComboBox:hover {{ border-color: {COLORS['border2']}; }}
            QComboBox:focus {{ border-color: {COLORS['accent']}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['surface2']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['accent']};
            }}
        """)
        self.embed_model_combo.addItem("bge-m3 (默认)")
        self.embed_model_combo.addItem("all-MiniLM-L6-v2")
        self.embed_model_combo.addItem("bge-large-zh-v1.5")
        self.embed_model_combo.addItem("mxbai-embed-large")
        layout.addWidget(self.embed_model_combo, 1)

        return container

    def _create_api_settings(self) -> QWidget:
        """API 设置按钮"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.api_settings_btn = QPushButton("⚙️ 配置 API")
        self.api_settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.api_settings_btn.setFixedHeight(34)
        self.api_settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface3']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text_dim']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {COLORS['text']};
                border-color: {COLORS['amber']};
            }}
        """)
        self.api_settings_btn.clicked.connect(self._show_api_settings_dialog)
        layout.addWidget(self.api_settings_btn)

        return container

    def _create_kb_toggle(self) -> QWidget:
        """知识库开关"""
        container = QWidget()
        container.setCursor(Qt.CursorShape.PointingHandCursor)
        container.setStyleSheet(f"""
            background-color: {COLORS['bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 12px;
        """)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(12, 0, 12, 0)

        self.kb_switch = QFrame()
        self.kb_switch.setFixedSize(36, 20)
        self.kb_switch.setStyleSheet(f"""
            background-color: {COLORS['accent']};
            border-radius: 10px;
        """)
        container_layout.addWidget(self.kb_switch)

        self.kb_label = QLabel("启用知识库检索")
        self.kb_label.setFont(QFont("Microsoft YaHei UI", 12))
        self.kb_label.setStyleSheet(f"color: {COLORS['text_dim']}; border: none;")
        container_layout.addWidget(self.kb_label)

        container_layout.addStretch()

        # 点击事件
        container.mousePressEvent = lambda e: self._toggle_kb()

        return container

    def _create_status_bar(self) -> QWidget:
        """状态栏"""
        status = QWidget()
        status.setStyleSheet(f"background-color: {COLORS['surface']}; border-top: 1px solid {COLORS['border']};")
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(16, 8, 16, 8)

        # 左侧：状态指示
        left_layout = QHBoxLayout()
        left_layout.setSpacing(8)

        self.status_dot = QFrame()
        self.status_dot.setFixedSize(7, 7)
        self.status_dot.setStyleSheet(f"background-color: {COLORS['green']}; border-radius: 3.5px;")
        left_layout.addWidget(self.status_dot)

        self.status_text = QLabel("初始化中...")
        self.status_text.setFont(QFont("Microsoft YaHei UI", 11))
        self.status_text.setStyleSheet(f"color: {COLORS['text_faint']};")
        left_layout.addWidget(self.status_text)

        status_layout.addLayout(left_layout, 1)

        # 右侧：API 测试按钮（API 模式下显示）
        self.api_test_btn = QPushButton("测试 API")
        self.api_test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.api_test_btn.setFixedHeight(26)
        self.api_test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface3']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                color: {COLORS['text_dim']};
                font-size: 10px;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                color: {COLORS['accent']};
                border-color: {COLORS['accent']};
            }}
        """)
        self.api_test_btn.clicked.connect(self._test_api)
        self.api_test_btn.setVisible(False)  # 默认隐藏
        status_layout.addWidget(self.api_test_btn)

        return status

    def _create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {COLORS['bg']};")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部栏
        topbar = self._create_topbar()
        layout.addWidget(topbar)

        # 对话区
        chat_body = self._create_chat_body()
        layout.addWidget(chat_body, 1)

        # 输入区
        input_area = self._create_input_area()
        layout.addWidget(input_area)

        return panel

    def _create_topbar(self) -> QWidget:
        """顶部栏"""
        bar = QWidget()
        bar.setStyleSheet(f"background-color: {COLORS['surface']}; border-bottom: 1px solid {COLORS['border']};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 14, 20, 12)

        title = QLabel("对话历史")
        title.setFont(QFont("Microsoft YaHei UI", 11, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 0.1em;")
        layout.addWidget(title)

        layout.addStretch()

        self.clear_btn = QPushButton("清空对话")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                color: {COLORS['text_faint']};
                padding: 4px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                color: {COLORS['red']};
                border-color: rgba(255,95,87,0.3);
            }}
        """)
        self.clear_btn.clicked.connect(self._clear_chat)
        layout.addWidget(self.clear_btn)

        return bar

    def _create_chat_body(self) -> QWidget:
        """对话区"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(12)
        self.chat_layout.addStretch()

        scroll.setWidget(self.chat_container)
        layout.addWidget(scroll)

        self._show_welcome()

        return container

    def _show_welcome(self):
        """欢迎消息"""
        welcome_text = """你好！我是你的 CAE 学习助手 🤖

📚 我可以帮助你学习：
• 材料力学 - 应力、应变、弹性模量
• 理论力学 - 力、力矩、平衡
• 有限元分析 - 单元类型、网格划分
• 机械设计 - 螺栓连接、轴设计

💡 采用费曼学习法，用简单易懂的语言教学。

有什么问题尽管问我吧！"""
        self._add_message("🤖", welcome_text, is_bot=True)

    def _create_input_area(self) -> QWidget:
        """输入区"""
        area = QWidget()
        area.setStyleSheet(f"background-color: {COLORS['surface']}; border-top: 1px solid {COLORS['border']};")
        layout = QVBoxLayout(area)
        layout.setContentsMargins(20, 14, 20, 16)
        layout.setSpacing(10)

        label = QLabel("提问")
        label.setFont(QFont("Microsoft YaHei UI", 11, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 0.1em;")
        layout.addWidget(label)

        input_row = QWidget()
        input_row.setStyleSheet(f"""
            background-color: {COLORS['bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 10px 14px;
        """)
        input_layout = QHBoxLayout(input_row)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("输入您的问题，例如：什么是应力集中？")
        self.input_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                border: none;
                color: {COLORS['text']};
                font-size: 13px;
                line-height: 1.6;
            }}
            QTextEdit::placeholder {{ color: {COLORS['text_faint']}; }}
        """)
        self.input_text.setMaximumHeight(100)
        self.input_text.textChanged.connect(self._auto_resize_input)
        input_layout.addWidget(self.input_text, 1)

        self.send_btn = QPushButton("提问")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setFixedHeight(38)
        self.send_btn.setMinimumWidth(80)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #5f8fff; }}
            QPushButton:disabled {{ background-color: {COLORS['surface3']}; color: {COLORS['text_dim']}; }}
        """)
        self.send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_btn)

        layout.addWidget(input_row)

        hint = QLabel("Enter 发送 · Shift+Enter 换行")
        hint.setFont(QFont("Microsoft YaHei UI", 10))
        hint.setStyleSheet(f"color: {COLORS['text_faint']};")
        layout.addWidget(hint)

        return area

    def _auto_resize_input(self):
        """自动调整输入框高度"""
        doc_height = self.input_text.document().size().height()
        new_height = min(max(doc_height + 20, 34), 100)
        self.input_text.setFixedHeight(int(new_height))

    def _connect_signals(self):
        """连接信号"""
        self.input_text.installEventFilter(self)

    def eventFilter(self, obj, event):
        """事件过滤器"""
        from PySide6.QtCore import QEvent

        if obj == self.input_text and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers():
                self._send_message()
                return True
        return super().eventFilter(obj, event)

    # ========== 功能方法 ==========

    def _switch_source(self, source: str):
        """切换模型来源"""
        self.model_source = source

        # 更新按钮样式
        btns = {
            "ollama": self.ollama_btn,
            "api": self.api_btn,
            "gguf": self.gguf_btn,
        }

        for key, btn in btns.items():
            if key == source:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['accent']};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLORS['text_dim']};
                        border: none;
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        color: {COLORS['text']};
                        background-color: {COLORS['surface3']};
                    }}
                """)

        # 根据来源执行相应操作
        if source == "ollama":
            self.api.set_provider("ollama")
            self.api_test_btn.setVisible(False)
            self._check_ollama()
        elif source == "api":
            self.api.set_provider("openai")  # 默认用 OpenAI
            self.api_test_btn.setVisible(True)
            self._update_status("API 模式已选择，请先配置 API Key", False)
        else:
            self.api_test_btn.setVisible(False)
            self._update_status("本地 GGUF 模式", True)

    def _start_ollama_check(self):
        """性能优化：异步检查 Ollama 服务，避免阻塞UI"""
        self._update_status("检测中...", False)

        # 如果已有工作线程在运行，先停止
        if self.ollama_check_worker and self.ollama_check_worker.isRunning():
            self.ollama_check_worker.quit()
            self.ollama_check_worker.wait()

        # 创建并启动异步检测工作线程
        self.ollama_check_worker = OllamaCheckWorker()
        self.ollama_check_worker.check_complete.connect(self._on_ollama_check_complete)
        self.ollama_check_worker.start()

    def _on_ollama_check_complete(self, chat_models: list, embed_models: list, connected: bool, error: str):
        """Ollama 检测完成回调"""
        if connected and chat_models:
            self.available_models = chat_models
            self.available_embed_models = embed_models
            self._update_model_combo()
            self.ollama_connected = True
            self._update_status(f"Ollama 已连接 · {len(self.available_models)} 个对话模型", True)
        elif connected and not chat_models:
            self._update_status("无可用模型，请下载", False)
        else:
            self._update_status(f"Ollama {error or '未运行'}", False)

    def _check_ollama(self):
        """同步检查 Ollama 服务（保留用于手动刷新）"""
        self._start_ollama_check()

    def _load_embed_models(self):
        """加载嵌入模型"""
        self.embed_model_combo.clear()
        self.embed_model_combo.addItem("bge-m3 (默认)", "bge-m3")
        self.embed_model_combo.addItem("all-MiniLM-L6-v2", "all-MiniLM-L6-v2")
        self.embed_model_combo.addItem("bge-large-zh-v1.5", "bge-large-zh-v1.5")
        self.embed_model_combo.addItem("mxbai-embed-large", "mxbai-embed-large")

        # 如果有本地嵌入模型，也添加进去
        if self.available_embed_models:
            for m in self.available_embed_models:
                self.embed_model_combo.addItem(m, m)

    def _refresh_models(self):
        """刷新模型列表"""
        if self.model_source == "ollama":
            self._check_ollama()
        elif self.model_source == "gguf":
            self._scan_gguf_models()
        else:
            self._update_status("API 模式无需刷新", True)

        # 如果模型选择器已展开，更新下拉框
        if self.model_selector_expanded and hasattr(self, "model_combo"):
            self.model_combo.blockSignals(True)
            self.model_combo.clear()
            if self.available_models:
                self.model_combo.addItems(self.available_models)
            else:
                self.model_combo.addItem("-- 请选择模型 --")
            self.model_combo.blockSignals(False)

    def _scan_gguf_models(self):
        """扫描本地 GGUF 模型"""
        self.available_models = []
        search_dirs = [
            os.path.expanduser("~/models"),
            os.path.expanduser("~/.cache/llama.cpp"),
            "./models",
        ]

        for d in search_dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.endswith(".gguf"):
                        self.available_models.append(f)

        self._update_model_combo()

        if self.available_models:
            self._update_status(f"本地 {len(self.available_models)} 个 GGUF 模型", True)
        else:
            self._update_status("未找到 GGUF 模型", False)

    def _update_model_combo(self):
        """更新模型下拉框"""
        self.model_combo.blockSignals(True)
        self.model_combo.clear()

        if self.available_models:
            self.model_combo.addItems(self.available_models)
            # 自动选择第一个
            self.model_combo.setCurrentIndex(0)
        else:
            self.model_combo.addItem("-- 请选择模型 --")

        self.model_combo.blockSignals(False)

    def _update_status(self, text: str, connected: bool):
        """更新状态"""
        self.status_text.setText(text)
        if connected:
            self.status_dot.setStyleSheet(f"background-color: {COLORS['green']}; border-radius: 3.5px;")
        else:
            self.status_dot.setStyleSheet(f"background-color: {COLORS['text_dim']}; border-radius: 3.5px;")

    def _test_api(self):
        """测试 API 连接"""
        api_key = os.environ.get("OPENAI_API_KEY", "")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

        if not api_key and not anthropic_key:
            self._update_status("请先在 API 设置中配置 Key", False)
            return

        self._update_status("测试中...", False)
        self.api_test_btn.setEnabled(False)

        try:
            # 测试 OpenAI
            if api_key:
                response = requests.get(
                    "https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=10
                )
                if response.status_code == 200:
                    models = response.json().get("data", [])[:5]
                    model_names = [m.get("id") for m in models]
                    self._update_status(f"OpenAI 可用 · {', '.join(model_names[:3])}", True)
                    self.api_test_btn.setEnabled(True)
                    return

            # 测试 Anthropic
            if anthropic_key:
                response = requests.get(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": anthropic_key, "anthropic-version": "2023-06-01"},
                    timeout=10,
                )
                if response.status_code == 200:
                    self._update_status("Claude API 可用", True)
                    self.api_test_btn.setEnabled(True)
                    return

            self._update_status("API 测试失败", False)

        except Exception as e:
            self._update_status(f"API 测试失败: {str(e)[:30]}", False)

        self.api_test_btn.setEnabled(True)

    def _toggle_kb(self):
        """切换知识库"""
        self.kb_enabled = not self.kb_enabled
        if self.kb_enabled:
            self.kb_switch.setStyleSheet(f"background-color: {COLORS['accent']}; border-radius: 10px;")
            self.kb_label.setText("启用知识库检索")
        else:
            self.kb_switch.setStyleSheet(f"background-color: {COLORS['surface3']}; border-radius: 10px;")
            self.kb_label.setText("禁用知识库检索")

    def _show_api_settings_dialog(self):
        """显示 API 设置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("API 设置")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet(f"background-color: {COLORS['surface']};")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)

        # 标题
        title = QLabel("API 提供商配置")
        title.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        layout.addWidget(title)

        # API 类型
        api_type_label = QLabel("选择 API 类型:")
        api_type_label.setStyleSheet(f"color: {COLORS['text_dim']};")
        layout.addWidget(api_type_label)

        self.api_type_combo = QComboBox()
        self.api_type_combo.addItems(["OpenAI", "Anthropic (Claude)", "自定义 API"])
        self.api_type_combo.setFixedHeight(36)
        self.api_type_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text']};
            }}
        """)
        layout.addWidget(self.api_type_combo)

        # API Key
        key_label = QLabel("API Key:")
        key_label.setStyleSheet(f"color: {COLORS['text_dim']};")
        layout.addWidget(key_label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入 API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setFixedHeight(36)
        self.api_key_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text']};
            }}
        """)
        layout.addWidget(self.api_key_input)

        # API 地址（自定义用）
        url_label = QLabel("API 地址 (自定义时):")
        url_label.setStyleSheet(f"color: {COLORS['text_dim']};")
        layout.addWidget(url_label)

        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://api.example.com/v1/chat")
        self.api_url_input.setFixedHeight(36)
        self.api_url_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 0 12px;
                color: {COLORS['text']};
            }}
        """)
        layout.addWidget(self.api_url_input)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(80, 34)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface3']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                color: {COLORS['text_dim']};
            }}
            QPushButton:hover {{ color: {COLORS['text']}; }}
        """)
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setFixedSize(80, 34)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #5f8fff; }}
        """)
        save_btn.clicked.connect(lambda: self._save_api_settings(dialog))
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    def _save_api_settings(self, dialog: QDialog):
        """保存 API 设置"""
        api_type = self.api_type_combo.currentText()
        api_key = self.api_key_input.text().strip()
        api_url = self.api_url_input.text().strip()

        # 设置环境变量
        if api_type == "OpenAI":
            os.environ["OPENAI_API_KEY"] = api_key
            self.api.set_provider("openai")
        elif api_type == "Anthropic (Claude)":
            os.environ["ANTHROPIC_API_KEY"] = api_key
            self.api.set_provider("anthropic")
        else:
            # 自定义 API - 可以扩展
            if api_url:
                os.environ["CUSTOM_API_URL"] = api_url

        self._update_status(f"{api_type} API 已配置", True)
        dialog.close()

    def _send_message(self):
        """发送消息"""
        text = self.input_text.toPlainText().strip()
        if not text:
            return

        # 检查模型是否选择
        model = self.model_combo.currentText()
        if not model or model == "-- 请选择模型 --":
            self._show_temp_message("请先选择一个模型")
            return

        # 添加用户消息
        self._add_message("👤", text, is_bot=False)
        self.input_text.clear()
        self.input_text.setFixedHeight(34)

        # 禁用发送按钮
        self.send_btn.setEnabled(False)

        # 调用 AI
        self._call_ai(text, model)

    def _show_temp_message(self, text: str):
        """显示临时消息"""
        self._add_message("⚠️", text, is_bot=True)

    def _add_message(self, avatar: str, text: str, is_bot: bool):
        """添加消息"""
        msg_widget = QWidget()
        msg_widget.setStyleSheet("background-color: transparent;")

        if is_bot:
            layout = QHBoxLayout(msg_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

            avatar_label = QLabel(avatar)
            avatar_label.setFixedSize(32, 32)
            avatar_label.setStyleSheet(f"""
                background-color: {COLORS['surface3']};
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
                padding: 0;
                font-size: 14px;
            """)
            avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(avatar_label)

            bubble = QLabel(text)
            bubble.setStyleSheet(f"""
                background-color: {COLORS['surface2']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                color: {COLORS['text']};
                line-height: 1.7;
            """)
            bubble.setWordWrap(True)
            bubble.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(bubble)
            layout.addStretch()

        else:
            layout = QHBoxLayout(msg_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)
            layout.addStretch()

            bubble = QLabel(text)
            bubble.setStyleSheet(f"""
                background-color: {COLORS['accent']};
                border-radius: 8px;
                padding: 12px 16px;
                color: white;
                line-height: 1.7;
            """)
            bubble.setWordWrap(True)
            layout.addWidget(bubble)

            avatar_label = QLabel(avatar)
            avatar_label.setFixedSize(32, 32)
            avatar_label.setStyleSheet(f"""
                background-color: {COLORS['accent']};
                border-radius: 16px;
                padding: 0;
                font-size: 14px;
            """)
            avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(avatar_label)

        count = self.chat_layout.count()
        if count > 0:
            self.chat_layout.insertWidget(count - 1, msg_widget)

        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        """滚动到底部"""
        container = self.chat_container
        scroll = container.parent()
        if hasattr(scroll, "verticalScrollBar"):
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())

    def _call_ai(self, question: str, model: str):
        """调用 AI"""
        # 显示思考中
        thinking = self._add_thinking_message()

        # 构建消息
        messages = []

        # 系统提示词
        if self.kb_enabled:
            # 先检索知识库
            kb_result = self._search_knowledge(question)
            if kb_result:
                messages.append({"role": "system", "content": f"{self.system_prompt}\n\n【知识库参考】\n{kb_result}"})
            else:
                messages.append({"role": "system", "content": self.system_prompt})
        else:
            messages.append({"role": "system", "content": self.system_prompt})

        # 添加历史
        for msg in self.messages[-10:]:
            messages.append(msg)

        messages.append({"role": "user", "content": question})

        # 后台线程调用
        self.current_worker = OllamaWorker(self.api, model, messages)
        self.current_worker.response_ready.connect(lambda r: self._on_ai_response(r, thinking))
        self.current_worker.error_occurred.connect(lambda e: self._on_ai_error(e, thinking))
        self.current_worker.start()

    def _search_knowledge(self, query: str) -> str:
        """检索知识库"""
        try:
            from sw_helper.knowledge import search

            results = search(query, limit=3)
            if results:
                return "\n\n".join([f"【{r.get('title', '未知')}】\n{r.get('content', '')[:500]}" for r in results])
        except Exception:
            pass
        return ""

    def _on_ai_response(self, response: str, thinking_widget: QWidget):
        """AI 响应"""
        # 保存到历史
        self.messages.append({"role": "user", "content": self.input_text.toPlainText().strip()})
        self.messages.append({"role": "assistant", "content": response})

        # 更新思考消息为实际回复
        self._update_thinking(thinking_widget, response)

        # 重新启用发送按钮
        self.send_btn.setEnabled(True)

    def _on_ai_error(self, error: str, thinking_widget: QWidget):
        """AI 错误"""
        self._update_thinking(thinking_widget, f"❌ 错误: {error}")
        self.send_btn.setEnabled(True)

    def _add_thinking_message(self) -> QWidget:
        """添加思考中消息"""
        msg_widget = QWidget()
        msg_widget.setStyleSheet("background-color: transparent;")

        layout = QHBoxLayout(msg_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        avatar = QLabel("🤖")
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet(f"""
            background-color: {COLORS['surface3']};
            border: 1px solid {COLORS['border']};
            border-radius: 16px;
            font-size: 14px;
        """)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(avatar)

        self.thinking_label = QLabel("正在思考中...")
        self.thinking_label.setStyleSheet(f"""
            background-color: {COLORS['surface2']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 12px 16px;
            color: {COLORS['text_dim']};
        """)
        layout.addWidget(self.thinking_label)
        layout.addStretch()

        count = self.chat_layout.count()
        if count > 0:
            self.chat_layout.insertWidget(count - 1, msg_widget)

        QTimer.singleShot(50, self._scroll_to_bottom)

        return msg_widget

    def _update_thinking(self, widget: QWidget, text: str):
        """更新思考消息"""
        widget.hide()
        self.chat_layout.removeWidget(widget)
        widget.deleteLater()

        self._add_message("🤖", text, is_bot=True)

    def _clear_chat(self):
        """清空对话"""
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.messages = []
        self._show_welcome()


def create_chat_page(mode: str = "learning") -> ChatPage:
    """创建聊天页面"""
    return ChatPage(mode)
