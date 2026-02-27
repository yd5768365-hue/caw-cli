"""
CAE-CLI 卡片式主界面

侧边栏 + 卡片布局的GUI主界面，
核心永远是 CLI，GUI 只是可视化界面。
"""

import os
import shutil
import sys
from typing import Any, Dict, Optional

from PySide6.QtCore import QProcess, Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..theme import BORDER_COLOR, DARK_BACKGROUND, HIGHLIGHT_RED, MAIN_RED, PANEL_BACKGROUND


# CLI 可执行文件路径
def get_cli_path() -> str:
    """获取CLI可执行文件路径"""
    # 首先尝试使用 Python 模块方式运行（更可靠）
    if shutil.which("python") or shutil.which("python3"):
        return "python"

    # 如果是打包后的 exe
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发模式：项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    search_paths = [
        os.path.join(base_dir, "cae-cli.exe"),
        os.path.join(base_dir, "dist", "cae-cli.exe"),
        os.path.join(base_dir, "cae-cli"),
    ]

    for cli_path in search_paths:
        if os.path.exists(cli_path):
            return cli_path

    # 最后尝试系统PATH中的cae-cli
    return "cae-cli"


CLI_EXE_PATH = get_cli_path()


# 功能卡片数据
FEATURE_CARDS = [
    {
        "id": "parse",
        "title": "几何解析",
        "icon": "📐",
        "description": "解析 STEP/STL/IGES 文件",
        "cli_cmd": "parse",
        "file_filter": "几何文件 (*.step *.stp *.stl *.iges *.igs);;所有文件 (*.*)",
        "color": "#2196F3",
    },
    {
        "id": "mesh",
        "title": "网格分析",
        "icon": "🔲",
        "description": "分析网格质量和单元指标",
        "cli_cmd": "analyze",
        "file_filter": "网格文件 (*.msh *.inp *.bdf *.vtk);;所有文件 (*.*)",
        "color": "#4CAF50",
    },
    {
        "id": "material",
        "title": "材料查询",
        "icon": "🔧",
        "description": "查询GB/T标准材料性能",
        "cli_cmd": "material",
        "file_filter": "",
        "color": "#FF9800",
    },
    {
        "id": "report",
        "title": "报告生成",
        "icon": "📊",
        "description": "生成分析报告 HTML/PDF",
        "cli_cmd": "report",
        "file_filter": "所有文件 (*.*)",
        "color": "#9C27B0",
    },
    {
        "id": "optimize",
        "title": "参数优化",
        "icon": "⚙️",
        "description": "自动化参数优化循环",
        "cli_cmd": "optimize",
        "file_filter": "CAD文件 (*.FCStd *.FCStd1);;所有文件 (*.*)",
        "color": "#00BCD4",
    },
    {
        "id": "ai",
        "title": "AI 助手",
        "icon": "🤖",
        "description": "自然语言生成CAD模型",
        "cli_cmd": "ai",
        "file_filter": "",
        "color": "#E91E63",
    },
]


# 侧边栏分类
SIDEBAR_ITEMS = [
    {"id": "geometry", "title": "几何", "icon": "📐", "cards": ["parse"]},
    {"id": "mesh", "title": "网格", "icon": "🔲", "cards": ["mesh"]},
    {"id": "material", "title": "材料", "icon": "🔧", "cards": ["material"]},
    {"id": "report", "title": "报告", "icon": "📊", "cards": ["report"]},
    {"id": "optimize", "title": "优化", "icon": "⚙️", "cards": ["optimize"]},
    {"id": "ai", "title": "AI", "icon": "🤖", "cards": ["ai"]},
    {"id": "learn", "title": "学习", "icon": "📚", "cards": []},
    {"id": "command", "title": "命令", "icon": "⚡", "cards": []},
]


class FeatureCard(QFrame):
    """功能卡片组件"""

    # 信号：点击卡片
    clicked = Signal(dict)

    def __init__(self, card_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.card_data = card_data
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        color = self.card_data.get("color", MAIN_RED)

        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BACKGROUND};
                border: 1px solid {BORDER_COLOR};
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
            QFrame:hover {{
                border: 2px solid {color};
                background-color: {DARK_BACKGROUND};
            }}
        """)
        self.setMinimumSize(180, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # 图标和标题
        icon = self.card_data.get("icon", "")
        title = self.card_data.get("title", "")
        title_label = QLabel(f"{icon} {title}")
        title_label.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)

        # 描述
        desc = self.card_data.get("description", "")
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("color: #B0B0B0; font-size: 11px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addStretch()

    def mousePressEvent(self, event):
        """点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.card_data)
        super().mousePressEvent(event)


class HomePage(QWidget):
    """卡片式主页面 - 侧边栏 + 卡片区 + 结果区"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process: Optional[QProcess] = None
        self._current_category = "geometry"
        self._selected_file = ""
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== 左侧侧边栏 =====
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        # ===== 右侧内容区域 =====
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # 顶部标题栏
        header = self._create_header()
        content_layout.addWidget(header)

        # 卡片网格
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        content_layout.addWidget(self.cards_container, 1)

        # 文件选择和参数区域
        self.input_area = self._create_input_area()
        content_layout.addWidget(self.input_area)

        # 执行按钮
        self.exec_button = QPushButton("执行命令")
        self.exec_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MAIN_RED};
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HIGHLIGHT_RED};
            }}
            QPushButton:disabled {{
                background-color: #666666;
                color: #999999;
            }}
        """)
        self.exec_button.clicked.connect(self._on_execute)
        self.exec_button.setEnabled(False)
        content_layout.addWidget(self.exec_button)

        # ===== 结果显示区域 =====
        result_group = self._create_result_area()
        content_layout.addWidget(result_group, 2)

        main_layout.addWidget(content_widget, 1)

        # 初始化显示几何分类的卡片（延迟到所有UI创建完成后）
        self.sidebar_list.setCurrentRow(0)
        self._show_cards("geometry")

    def _create_sidebar(self) -> QWidget:
        """创建侧边栏"""
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {DARK_BACKGROUND};
                border-right: 1px solid {BORDER_COLOR};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # Logo/标题
        logo = QLabel("MechDesign")
        logo.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {MAIN_RED}; padding: 10px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        version = QLabel("v1.0.0")
        version.setStyleSheet("color: #666666; font-size: 10px;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        layout.addSpacing(20)

        # 分类列表
        self.sidebar_list = QListWidget()
        self.sidebar_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                color: #B0B0B0;
            }}
            QListWidget::item {{
                padding: 12px 15px;
                border-radius: 6px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {MAIN_RED};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: #333333;
            }}
        """)

        for item in SIDEBAR_ITEMS:
            list_item = QListWidgetItem(f"{item['icon']}  {item['title']}")
            list_item.setData(Qt.ItemDataRole.UserRole, item["id"])
            self.sidebar_list.addItem(list_item)

        self.sidebar_list.currentRowChanged.connect(self._on_sidebar_changed)
        # 注意：不要在这里调用 setCurrentRow，会在 _init_ui 完成前触发 _show_cards
        layout.addWidget(self.sidebar_list)

        layout.addStretch()

        # 底部状态
        status_label = QLabel("CLI 就绪" if os.path.exists(CLI_EXE_PATH) else "CLI 未找到")
        status_label.setStyleSheet("color: #666666; font-size: 10px; padding: 10px;")
        layout.addWidget(status_label)

        return sidebar

    def _create_header(self) -> QWidget:
        """创建顶部标题栏"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        self.category_title = QLabel("几何解析")
        self.category_title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        self.category_title.setStyleSheet("color: white;")
        layout.addWidget(self.category_title)

        layout.addStretch()

        # 版本和帮助按钮
        version_btn = QPushButton("v1.0.0")
        version_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #888888;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(version_btn)

        help_btn = QPushButton("帮助")
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #888888;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        layout.addWidget(help_btn)

        return header

    def _create_input_area(self) -> QWidget:
        """创建输入区域（文件选择和参数）"""
        from PySide6.QtWidgets import QLineEdit

        area = QWidget()
        area.setStyleSheet(f"""
            QWidget {{
                background-color: {PANEL_BACKGROUND};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        layout = QHBoxLayout(area)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 文件选择
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: #888888;")
        self.file_label.setMinimumWidth(200)
        layout.addWidget(self.file_label)

        select_btn = QPushButton("选择文件")
        select_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #333333;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {MAIN_RED};
            }}
        """)
        select_btn.clicked.connect(self._on_select_file)
        layout.addWidget(select_btn)

        # 参数输入（用于材料名称等）
        self.param_label = QLabel("参数:")
        self.param_label.setStyleSheet("color: #888888;")
        self.param_label.setVisible(False)
        layout.addWidget(self.param_label)

        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText("如: 材料名称")
        self.param_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #2D2D2D;
                color: white;
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 6px;
                min-width: 150px;
            }}
        """)
        self.param_input.setVisible(False)
        layout.addWidget(self.param_input)

        layout.addStretch()

        return area

    def _create_result_area(self) -> QWidget:
        """创建结果区域"""
        group = QWidget()
        group.setStyleSheet(f"""
            QWidget {{
                background-color: {PANEL_BACKGROUND};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = QWidget()
        title_bar.setStyleSheet(f"""
            background-color: {DARK_BACKGROUND};
            border-bottom: 1px solid {BORDER_COLOR};
            padding: 8px 15px;
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)

        result_title = QLabel("输出结果")
        result_title.setStyleSheet("color: #B0B0B0; font-weight: bold;")
        title_layout.addWidget(result_title)

        title_layout.addStretch()

        # 清除按钮
        clear_btn = QPushButton("清除")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: none;
                padding: 5px 10px;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        clear_btn.clicked.connect(lambda: self.result_text.clear())
        title_layout.addWidget(clear_btn)

        layout.addWidget(title_bar)

        # 结果文本区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #0F0F0F;
                color: #D4D4D4;
                border: none;
                font-family: Consolas, monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.result_text, 1)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {DARK_BACKGROUND};
                color: white;
                border: none;
                height: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {MAIN_RED};
            }}
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        return group

    def _show_cards(self, category: str):
        """显示指定分类的卡片"""
        self._current_category = category

        # 确保 cards_layout 已初始化
        if not hasattr(self, "cards_layout") or self.cards_layout is None:
            return

        # 清除现有卡片
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 查找对应的卡片
        cards_to_show = []
        for cat in SIDEBAR_ITEMS:
            if cat["id"] == category:
                cards_to_show = cat.get("cards", [])
                break

        # 如果没有卡片（比如学习、命令分类），显示提示
        if not cards_to_show:
            no_cards = QLabel("此功能即将推出...")
            no_cards.setStyleSheet("color: #666666; font-size: 14px;")
            no_cards.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.addWidget(no_cards, 0, 0)
            self.exec_button.setEnabled(False)
            return

        # 创建卡片
        card_data_map = {card["id"]: card for card in FEATURE_CARDS}
        row, col = 0, 0
        for card_id in cards_to_show:
            if card_id in card_data_map:
                card = FeatureCard(card_data_map[card_id])
                card.clicked.connect(self._on_card_clicked)
                self.cards_layout.addWidget(card, row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

        # 更新标题
        for cat in SIDEBAR_ITEMS:
            if cat["id"] == category:
                self.category_title.setText(f"{cat['icon']} {cat['title']}")
                break

    def _on_sidebar_changed(self, row: int):
        """侧边栏选择变化"""
        if row >= 0 and row < len(SIDEBAR_ITEMS):
            category = SIDEBAR_ITEMS[row]["id"]
            self._show_cards(category)
            self._selected_file = ""
            self.file_label.setText("未选择文件")
            self.exec_button.setEnabled(False)
            # 隐藏参数输入框
            if hasattr(self, "param_label"):
                self.param_label.setVisible(False)
            if hasattr(self, "param_input"):
                self.param_input.setVisible(False)
                self.param_input.clear()

    def _on_card_clicked(self, card_data: Dict[str, Any]):
        """卡片点击事件"""
        self._selected_card = card_data
        card_id = card_data.get("id", "")
        title = card_data.get("title", "")
        desc = card_data.get("description", "")
        cli_cmd = card_data.get("cli_cmd", "")

        # 显示功能说明（不执行命令）
        self.result_text.clear()
        self._append_output(f"【{title}】\n", "command")
        self._append_output(f"{desc}\n\n", "normal")
        self._append_output(f"CLI 命令: cae-cli {cli_cmd}\n\n", "dim")
        self._append_output("请选择文件或输入参数，然后点击「执行命令」按钮\n", "success")

        # 更新文件选择器
        file_filter = card_data.get("file_filter", "")
        if file_filter:
            self.file_label.setText("未选择文件")
            self.file_label.setToolTip(file_filter)
        else:
            self.file_label.setText("无需文件")
            self.file_label.setToolTip("")

        # 根据不同卡片显示/隐藏参数输入框
        if card_id == "material":
            self.param_label.setVisible(True)
            self.param_label.setText("材料名称:")
            self.param_input.setVisible(True)
            self.param_input.setPlaceholderText("如: Q235, Q345, 铝合金")
            self.param_input.setText("Q235")  # 默认值
        elif card_id == "ai":
            self.param_label.setVisible(True)
            self.param_label.setText("AI提示:")
            self.param_input.setVisible(True)
            self.param_input.setPlaceholderText("如: 生成一个立方体")
            self.param_input.setText("")
        else:
            self.param_label.setVisible(False)
            self.param_input.setVisible(False)

        # 禁用执行按钮，等待用户选择文件
        self.exec_button.setEnabled(False)

        # 如果不需要文件，直接启用按钮
        if not file_filter:
            self.exec_button.setEnabled(True)

    def _on_select_file(self):
        """选择文件"""
        if not hasattr(self, "_selected_card"):
            self.result_text.setText("请先选择功能卡片")
            return

        file_filter = self._selected_card.get("file_filter", "")
        if not file_filter:
            self.result_text.setText("此功能无需选择文件")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            file_filter,
        )

        if file_path:
            self._selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.file_label.setToolTip(file_path)
            # 选择文件后启用执行按钮
            self.exec_button.setEnabled(True)
            self._append_output(f"已选择文件: {os.path.basename(file_path)}\n", "success")
            self._append_output("点击「执行命令」开始解析\n", "normal")

    def _show_command_help(self, cmd: str):
        """显示命令帮助"""
        if not cmd:
            return

        self._run_command(f"cae-cli {cmd} --help")

    def _on_execute(self):
        """执行命令"""
        if not hasattr(self, "_selected_card"):
            self._append_output("请先选择功能卡片\n", "error")
            return

        card = self._selected_card
        cli_cmd = card.get("cli_cmd", "")
        file_path = self._selected_file
        card_id = card.get("id", "")
        param = self.param_input.text().strip() if hasattr(self, "param_input") else ""

        if not cli_cmd:
            return

        # 验证：需要文件的命令必须选择文件
        if card.get("file_filter") and not file_path:
            self._append_output("请先选择文件\n", "error")
            return

        # 验证：材料查询必须输入材料名称
        if card_id == "material" and not param:
            self._append_output("请输入材料名称（如 Q235）\n", "error")
            return

        # 验证：AI 助手必须输入提示
        if card_id == "ai" and not param:
            self._append_output("请输入 AI 提示\n", "error")
            return

        # 根据不同类型的命令构建命令
        if card_id == "material" and param:
            # 材料查询：使用参数输入的材料名称
            full_cmd = f"cae-cli {cli_cmd} {param}"
        elif card_id == "ai" and param:
            # AI 助手：使用参数作为提示
            full_cmd = f'cae-cli {cli_cmd} generate "{param}"'
        elif card.get("file_filter") and file_path:
            # 需要文件的命令
            full_cmd = f"cae-cli {cli_cmd} {file_path}"
        else:
            # 其他命令
            full_cmd = f"cae-cli {cli_cmd}"

        self._run_command(full_cmd)

    def _run_command(self, cmd: str):
        """运行 CLI 命令"""

        # 显示命令
        self._append_output(f"$ {cmd}\n", "command")
        self._append_output("-" * 50 + "\n", "dim")

        # 禁用执行按钮
        self.exec_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度

        # 分割命令
        cmd_list = cmd.split()

        # 移除 "cae-cli" 前缀
        if cmd_list and cmd_list[0] in ("cae-cli", "cae"):
            cmd_list = cmd_list[1:]

        # 确定使用什么命令运行
        # 优先使用 Python 模块方式
        if CLI_EXE_PATH == "python" or CLI_EXE_PATH == "python3":
            # 使用 python -m sw_helper
            final_cmd = [CLI_EXE_PATH, "-m", "sw_helper"] + cmd_list
        elif os.path.exists(CLI_EXE_PATH):
            # 使用找到的 exe
            final_cmd = [CLI_EXE_PATH] + cmd_list
        else:
            # 尝试系统 PATH 中的 cae-cli
            final_cmd = ["cae-cli"] + cmd_list

        # 创建进程
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)

        # 显示实际执行的命令
        self._append_output(f"[执行: {' '.join(final_cmd)}]\n", "dim")

        self._process.start(final_cmd[0], final_cmd[1:])

    def _on_stdout(self):
        """标准输出"""
        if self._process:
            data = self._process.readAllStandardOutput()
            text = bytes(data).decode("utf-8", errors="replace")
            self._append_output(text, "normal")

    def _on_stderr(self):
        """标准错误"""
        if self._process:
            data = self._process.readAllStandardError()
            text = bytes(data).decode("utf-8", errors="replace")
            self._append_output(text, "error")

    def _on_finished(self, exitCode: int, exitStatus):
        """命令完成"""
        self._append_output("\n", "normal")
        if exitCode != 0:
            self._append_output(f"[退出码: {exitCode}]\n", "error")
        else:
            self._append_output("[完成]\n", "success")

        self.progress_bar.setVisible(False)
        self.exec_button.setEnabled(True)

        # 滚动到底部
        self.result_text.verticalScrollBar().setValue(self.result_text.verticalScrollBar().maximum())

    def _append_output(self, text: str, style: str = "normal"):
        """追加输出文本"""
        # 创建格式
        fmt = QTextCharFormat()

        if style == "command":
            fmt.setForeground(QColor("#569CD6"))  # 蓝色
            fmt.setFontWeight(QFont.Weight.Bold)
        elif style == "error":
            fmt.setForeground(QColor("#F44747"))  # 红色
        elif style == "success":
            fmt.setForeground(QColor("#6A9955"))  # 绿色
        elif style == "dim":
            fmt.setForeground(QColor("#666666"))  # 灰色
        else:
            fmt.setForeground(QColor("#D4D4D4"))  # 白色

        cursor = self.result_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.result_text.setTextCursor(cursor)


def create_home_page() -> HomePage:
    """创建主页

    Returns:
        HomePage: 主页对象
    """
    return HomePage()
