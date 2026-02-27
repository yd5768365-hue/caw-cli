"""
几何格式转换页面

此模块提供几何文件格式转换功能的GUI界面。
支持 STEP、STL、IGES、BREP、OBJ 等格式的相互转换。
"""

import os  # 性能优化：模块级别导入

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ConvertPage(QWidget):
    """几何格式转换页面类"""

    # 信号：转换完成
    convert_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("几何格式转换")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 输入文件选择
        input_group = QGroupBox("输入文件")
        input_layout = QFormLayout()

        # 文件路径
        self.input_path_label = QLabel("未选择文件")
        select_btn = QPushButton("选择文件")
        select_btn.clicked.connect(self._on_select_input)
        input_layout.addRow("文件路径:", self.input_path_label)
        input_layout.addWidget(select_btn)

        # 格式检测
        self.format_label = QLabel("-")
        input_layout.addRow("检测格式:", self.format_label)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QFormLayout()

        # 目标格式
        self.format_combo = QComboBox()
        self.format_combo.addItems(
            [
                ("stl", "STL (.stl) - 网格格式"),
                ("step", "STEP (.step) - CAD格式"),
                ("iges", "IGES (.iges) - CAD格式"),
                ("brep", "BREP (.brep) - OpenCAD格式"),
                ("obj", "OBJ (.obj) - 3D格式"),
            ]
        )
        output_layout.addRow("目标格式:", self.format_combo)

        # 输出路径
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("默认自动生成")
        output_layout.addRow("输出路径:", self.output_path_input)

        # 检查几何质量
        self.check_quality = QCheckBox()
        self.check_quality.setText("转换后检查几何质量")
        self.check_quality.setChecked(True)
        output_layout.addRow("质量检查:", self.check_quality)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 转换按钮
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setProperty("primary", True)
        self.convert_btn.clicked.connect(self._on_convert)
        layout.addWidget(self.convert_btn)

        # 结果显示区域
        result_group = QGroupBox("转换结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("转换结果将显示在此处...")
        result_layout.addWidget(self.result_text)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()

    def _on_select_input(self):
        """选择输入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择几何文件",
            "",
            "CAD文件 (*.step *.stp *.stl *.iges *.igs *.brep *.obj);;所有文件 (*.*)",
        )

        if file_path:
            self.input_path_label.setText(file_path)

            # 自动检测格式
            ext = os.path.splitext(file_path)[1].lower()
            format_map = {
                ".step": "STEP",
                ".stp": "STEP",
                ".stl": "STL",
                ".iges": "IGES",
                ".igs": "IGES",
                ".brep": "BREP",
                ".obj": "OBJ",
            }
            self.format_label.setText(format_map.get(ext, "未知"))

    def _on_convert(self):
        """开始转换"""
        input_path = self.input_path_label.text()

        if input_path == "未选择文件" or not input_path:
            self.result_text.setText("请先选择输入文件")
            return

        self.convert_btn.setEnabled(False)
        self.result_text.setText("正在转换...\n")

        try:
            from sw_helper.geometry.converter import GeometryConverter

            # 获取目标格式
            target_format = self.format_combo.currentData()

            # 获取输出路径
            output_path = self.output_path_input.text().strip()
            if not output_path:
                output_path = None

            # 执行转换
            converter = GeometryConverter()
            success = converter.convert(input_path, output_path, target_format)

            if success:
                # 生成输出路径
                input_dir = os.path.dirname(input_path)
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                output_file = os.path.join(input_dir or ".", f"{input_name}.{target_format}")

                lines = [
                    "【转换成功】",
                    "",
                    f"输入文件: {input_path}",
                    f"输出文件: {output_file}",
                    f"目标格式: {target_format.upper()}",
                ]

                # 质量检查
                if self.check_quality.isChecked():
                    lines.append("")
                    lines.append("--- 质量检查 ---")
                    lines.append("(需要 pythonocc-core 进行详细检查)")

                self.result_text.setText("\n".join(lines))
            else:
                self.result_text.setText("转换失败，请检查输入文件格式")

        except Exception as e:
            self.result_text.setText(f"转换失败: {e}")

        finally:
            self.convert_btn.setEnabled(True)
