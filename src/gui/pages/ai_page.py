"""
AI助手页面

此模块提供AI辅助设计功能的GUI界面。
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
from PySide6.QtCore import Signal

from ..theme import CAETheme


class AIPage(QWidget):
    """AI助手页面类"""

    # 信号：生成完成
    generation_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("AI辅助设计")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 模型选择区域
        model_group = QGroupBox("AI模型设置")
        model_layout = QFormLayout()

        # 模型选择
        self.model_combo = QComboBox()
        self.model_combo.addItems(["自动选择", "qwen2.5:1.5b", "phi3:mini", "llama2:7b"])
        model_layout.addRow("AI模型:", self.model_combo)

        # 生成模式
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["完整模式（含分析）", "仅生成模型"])
        model_layout.addRow("生成模式:", self.mode_combo)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # 生成描述区域
        desc_group = QGroupBox("模型描述")
        desc_layout = QVBoxLayout()

        self.description_text = QTextEdit()
        self.description_text.setPlaceholderText(
            "输入模型描述，例如：\n"
            "立方体，圆角，长100宽50高30圆角10\n"
            "圆柱体，半径30高度60\n"
            "支架，L型，长150宽80厚5"
        )
        desc_layout.addWidget(self.description_text)

        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)

        # 生成按钮
        btn_layout = QHBoxLayout()

        self.generate_btn = QPushButton("生成3D模型")
        self.generate_btn.setProperty("primary", True)
        self.generate_btn.clicked.connect(self._on_generate)
        btn_layout.addWidget(self.generate_btn)

        self.mock_btn = QPushButton("模拟模式")
        self.mock_btn.clicked.connect(self._on_mock)
        btn_layout.addWidget(self.mock_btn)

        layout.addLayout(btn_layout)

        # 结果显示区域
        result_group = QGroupBox("生成结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("生成结果将显示在此处...")
        result_layout.addWidget(self.result_text)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()

    def _on_generate(self):
        """生成模型"""
        description = self.description_text.toPlainText().strip()

        if not description:
            self.result_text.setText("请输入模型描述")
            return

        # TODO: 调用 sw_helper.ai 进行生成
        self.result_text.setText(
            f"正在生成模型...\n\n"
            f"描述: {description}\n"
            f"模型: {self.model_combo.currentText()}\n"
            f"模式: {self.mode_combo.currentText()}\n\n"
            f"[功能开发中...]"
        )

    def _on_mock(self):
        """模拟模式生成"""
        description = self.description_text.toPlainText().strip()

        if not description:
            self.result_text.setText("请输入模型描述")
            return

        # 模拟模式
        self.result_text.setText(
            f"[模拟模式]\n\n"
            f"描述: {description}\n\n"
            f"生成成功！\n"
            f"FCStd文件: mock_model.FCStd\n"
            f"STEP文件: mock_model.step\n\n"
            f"[这是模拟模式的输出，不实际生成文件]"
        )


# 页面工厂函数
def create_ai_page() -> AIPage:
    """创建AI助手页面

    Returns:
        AIPage: AI助手页面对象
    """
    return AIPage()
