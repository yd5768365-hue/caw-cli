"""
参数优化页面

此模块提供参数优化功能的GUI界面。
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class OptimizationPage(QWidget):
    """参数优化页面类"""

    # 信号：优化完成
    optimization_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("参数优化")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 文件选择区域
        file_group = QGroupBox("CAD文件")
        file_layout = QFormLayout()

        # 文件路径
        self.file_path_label = QLabel("未选择文件")
        select_btn = QPushButton("选择CAD文件")
        select_btn.clicked.connect(self._on_select_file)
        file_layout.addRow("文件路径:", self.file_path_label)
        file_layout.addWidget(select_btn)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 优化参数区域
        param_group = QGroupBox("优化参数")
        param_layout = QFormLayout()

        # 参数名称
        self.param_name_input = QLineEdit()
        self.param_name_input.setPlaceholderText("如: Fillet_Radius, Thickness")
        param_layout.addRow("优化参数:", self.param_name_input)

        # 参数范围
        range_layout = QHBoxLayout()
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(0.0, 10000.0)
        self.min_spin.setValue(2.0)
        self.min_spin.setSuffix(" mm")
        range_layout.addWidget(self.min_spin)

        range_layout.addWidget(QLabel(" ~ "))

        self.max_spin = QDoubleSpinBox()
        self.max_spin.setRange(0.0, 10000.0)
        self.max_spin.setValue(15.0)
        self.max_spin.setSuffix(" mm")
        range_layout.addWidget(self.max_spin)

        param_layout.addRow("参数范围:", range_layout)

        # 迭代步数
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(1, 100)
        self.steps_spin.setValue(5)
        param_layout.addRow("迭代步数:", self.steps_spin)

        # 优化模式
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["线性", "几何"])
        param_layout.addRow("步进模式:", self.mode_combo)

        # CAD软件
        self.cad_combo = QComboBox()
        self.cad_combo.addItems(["FreeCAD", "SolidWorks", "模拟模式"])
        param_layout.addRow("CAD软件:", self.cad_combo)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # 优化按钮
        self.optimize_btn = QPushButton("开始优化")
        self.optimize_btn.setProperty("primary", True)
        self.optimize_btn.clicked.connect(self._on_optimize)
        layout.addWidget(self.optimize_btn)

        # 结果显示区域
        result_group = QGroupBox("优化结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("优化结果将显示在此处...")
        result_layout.addWidget(self.result_text)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()

    def _on_select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择CAD文件",
            "",
            "CAD文件 (*.FCStd *.sldprt);;所有文件 (*.*)",
        )

        if file_path:
            self.file_path_label.setText(file_path)

    def _on_optimize(self):
        """开始优化"""
        file_path = self.file_path_label.text()
        param_name = self.param_name_input.text().strip()

        if file_path == "未选择文件" or not file_path:
            self.result_text.setText("请先选择CAD文件")
            return

        if not param_name:
            self.result_text.setText("请输入优化参数名称")
            return

        # TODO: 调用 sw_helper.optimization 进行优化
        self.result_text.setText(
            f"正在优化: {param_name}\n"
            f"范围: {self.min_spin.value()} ~ {self.max_spin.value()} mm\n"
            f"步数: {self.steps_spin.value()}\n\n"
            f"[功能开发中...]"
        )


# 页面工厂函数
def create_optimization_page() -> OptimizationPage:
    """创建参数优化页面

    Returns:
        OptimizationPage: 参数优化页面对象
    """
    return OptimizationPage()
