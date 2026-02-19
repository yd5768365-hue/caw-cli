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

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("AI学习助手")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 服务状态区域
        status_group = QGroupBox("服务状态")
        status_layout = QFormLayout()

        # Ollama状态
        self.ollama_status = QLabel("未连接")
        status_layout.addRow("Ollama服务:", self.ollama_status)

        # 模型状态
        self.model_status = QLabel("未加载")
        status_layout.addRow("当前模型:", self.model_status)

        # 连接按钮
        connect_btn = QPushButton("连接服务")
        connect_btn.clicked.connect(self._on_connect)
        status_layout.addWidget(connect_btn)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # 对话历史区域
        history_group = QGroupBox("对话历史")
        history_layout = QVBoxLayout()

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("对话历史将显示在此处...")
        history_layout.addWidget(self.chat_history)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # 输入区域
        input_group = QGroupBox("提问")
        input_layout = QVBoxLayout()

        # 问题输入
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("输入您的问题...")
        self.question_input.returnPressed.connect(self._on_ask)
        input_layout.addWidget(self.question_input)

        # 按钮
        btn_layout = QHBoxLayout()

        ask_btn = QPushButton("提问")
        ask_btn.setProperty("primary", True)
        ask_btn.clicked.connect(self._on_ask)
        btn_layout.addWidget(ask_btn)

        clear_btn = QPushButton("清空历史")
        clear_btn.clicked.connect(self._on_clear)
        btn_layout.addWidget(clear_btn)

        input_layout.addLayout(btn_layout)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        layout.addStretch()

    def _on_connect(self):
        """连接Ollama服务"""
        # TODO: 实现Ollama服务连接
        self.ollama_status.setText("连接中...")
        self.ollama_status.setText("已连接")
        self.model_status.setText("phi3:mini")

    def _on_ask(self):
        """提问"""
        question = self.question_input.text().strip()

        if not question:
            return

        # 显示用户问题
        self.chat_history.append(f"<b>您:</b> {question}")
        self.question_input.clear()

        # 显示AI回答（占位）
        self.chat_history.append(f"<b>AI:</b> [功能开发中...]")

        # TODO: 调用 sw_helper.chat 进行回答

    def _on_clear(self):
        """清空对话历史"""
        self.chat_history.clear()


# 页面工厂函数
def create_chat_page() -> ChatPage:
    """创建学习模式页面

    Returns:
        ChatPage: 学习模式页面对象
    """
    return ChatPage()
