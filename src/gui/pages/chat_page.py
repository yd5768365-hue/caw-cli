"""
学习模式页面

此模块提供AI学习助手功能的GUI界面，
支持多轮对话和知识库检索。
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QGroupBox,
    QFormLayout,
    QComboBox,
)
from PySide6.QtCore import Signal, QThread

from ..theme import CAETheme


class ChatPage(QWidget):
    """学习模式页面类"""

    # 信号：回答完成
    answer_completed = Signal(str)

    def __init__(self, mode: str = "learning"):
        super().__init__()
        self.mode = mode
        self.system_prompt = ""
        self._load_system_prompt()
        self._init_ui()
        self._update_title()

    def _load_system_prompt(self):
        """从提示词管理器加载系统提示词"""
        try:
            from sw_helper.ai.prompt_manager import PromptManager
            self.system_prompt = PromptManager.build_system_prompt(self.mode)
        except Exception as e:
            self.system_prompt = f"加载提示词失败: {e}"

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        self._create_title_section(layout)
        self._create_status_section(layout)
        self._create_history_section(layout)
        self._create_input_section(layout)

        layout.addStretch()

    def _create_title_section(self, layout):
        """创建标题区域"""
        self.title = QLabel("AI学习助手")
        self.title.setProperty("heading", True)
        layout.addWidget(self.title)

        self.mode_label = QLabel()
        self.mode_label.setStyleSheet("color: #666;")
        layout.addWidget(self.mode_label)

    def _create_status_section(self, layout):
        """创建服务状态区域"""
        status_group = QGroupBox("服务状态")
        status_layout = QFormLayout()

        self.ollama_status = QLabel("未连接")
        status_layout.addRow("Ollama服务:", self.ollama_status)

        self.model_status = QLabel("未加载")
        status_layout.addRow("当前模型:", self.model_status)

        self.prompt_status = QLabel("未加载")
        prompt_len = len(self.system_prompt)
        if prompt_len > 0:
            self.prompt_status.setText(f"已加载 ({prompt_len}字符)")
        else:
            self.prompt_status.setText("未加载")
        status_layout.addRow("系统提示词:", self.prompt_status)

        connect_btn = QPushButton("连接服务")
        connect_btn.clicked.connect(self._on_connect)
        status_layout.addWidget(connect_btn)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

    def _create_history_section(self, layout):
        """创建对话历史区域"""
        history_group = QGroupBox("对话历史")
        history_layout = QVBoxLayout()

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("对话历史将显示在此处...")
        history_layout.addWidget(self.chat_history)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

    def _create_input_section(self, layout):
        """创建输入区域"""
        input_group = QGroupBox("提问")
        input_layout = QVBoxLayout()

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("输入您的问题...")
        self.question_input.returnPressed.connect(self._on_ask)
        input_layout.addWidget(self.question_input)

        btn_layout = QHBoxLayout()

        ask_btn = QPushButton("提问")
        ask_btn.setProperty("primary", True)
        ask_btn.clicked.connect(self._on_ask)
        btn_layout.addWidget(ask_btn)

        clear_btn = QPushButton("清空历史")
        clear_btn.clicked.connect(self._on_clear)
        btn_layout.addWidget(clear_btn)

        view_prompt_btn = QPushButton("查看提示词")
        view_prompt_btn.clicked.connect(self._on_view_prompt)
        btn_layout.addWidget(view_prompt_btn)

        input_layout.addLayout(btn_layout)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

    def _update_title(self):
        """更新标题和模式显示"""
        mode_names = {
            "learning": "🎯 学习模式 - 3-2-1方法+费曼学习法",
            "lifestyle": "🌟 生活态度 - 行动优先、长期主义",
            "mechanical": "🔧 机械设计 - 专注机械设计领域",
            "default": "📚 默认模式 - 综合助手",
        }
        mode_name = mode_names.get(self.mode, self.mode)
        self.title.setText(f"AI学习助手 - {mode_name}")
        self.mode_label.setText(f"当前模式: {self.mode}")

    def _on_connect(self):
        """连接Ollama服务"""
        # TODO: 实现完整的Ollama服务连接 - 检测服务状态和可用模型
        self.ollama_status.setText("连接中...")
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=3)
            if r.status_code == 200:
                models = r.json().get("models", [])
                if models:
                    self.ollama_status.setText("已连接")
                    self.model_status.setText(models[0].get("name", "未知"))
                else:
                    self.ollama_status.setText("无可用模型")
            else:
                self.ollama_status.setText("连接失败")
        except Exception:
            self.ollama_status.setText("连接失败")

    def _on_ask(self):
        """提问"""
        question = self.question_input.text().strip()

        if not question:
            return

        self.chat_history.append(f"<b>您:</b> {question}")
        self.question_input.clear()

        # TODO: 调用 sw_helper.chat 进行回答，使用 self.system_prompt 作为系统提示词
        # 临时显示功能开发中
        self.chat_history.append(f"<b>AI:</b> [功能开发中...]")

    def _on_view_prompt(self):
        """查看当前系统提示词"""
        from PySide6.QtWidgets import QMessageBox

        prompt_text = self.system_prompt if self.system_prompt else "未加载提示词"
        QMessageBox.information(
            self,
            f"系统提示词 - {self.mode} 模式",
            prompt_text[:2000] + ("..." if len(prompt_text) > 2000 else "")
        )

    def _on_clear(self):
        """清空对话历史"""
        self.chat_history.clear()


# 页面工厂函数
def create_chat_page(mode: str = "learning") -> ChatPage:
    """创建学习模式页面

    Args:
        mode: AI模式 (learning/lifestyle/mechanical/default)

    Returns:
        ChatPage: 学习模式页面对象
    """
    return ChatPage(mode)
