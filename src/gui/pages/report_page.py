"""
报告生成页面

此模块提供分析报告生成功能的GUI界面。
支持 HTML、PDF、JSON、Markdown 格式的报告输出。
"""

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


class ReportPage(QWidget):
    """报告生成页面类"""

    # 信号：生成完成
    report_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("分析报告生成")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 输入文件选择
        input_group = QGroupBox("输入文件")
        input_layout = QFormLayout()

        # 分析结果文件
        self.input_path_label = QLabel("未选择文件")
        select_btn = QPushButton("选择文件")
        select_btn.clicked.connect(self._on_select_input)
        input_layout.addRow("结果文件:", self.input_path_label)
        input_layout.addWidget(select_btn)

        # 分析类型
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["静力分析", "模态分析", "热分析", "屈曲分析"])
        input_layout.addRow("分析类型:", self.analysis_type_combo)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # 报告设置
        settings_group = QGroupBox("报告设置")
        settings_layout = QFormLayout()

        # 报告标题
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("默认: CAE分析报告")
        settings_layout.addRow("报告标题:", self.title_input)

        # 输出格式
        self.format_combo = QComboBox()
        self.format_combo.addItems(
            [
                ("html", "HTML (网页格式)"),
                ("json", "JSON (数据格式)"),
                ("markdown", "Markdown (文档格式)"),
                ("pdf", "PDF (需安装wkhtmltopdf)"),
            ]
        )
        self.format_combo.setCurrentIndex(0)
        settings_layout.addRow("输出格式:", self.format_combo)

        # 输出路径
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("默认: ./report.html")
        settings_layout.addRow("输出路径:", self.output_path_input)

        # 包含图表
        self.include_charts = QCheckBox()
        self.include_charts.setText("包含图表")
        self.include_charts.setChecked(True)
        settings_layout.addRow("图表:", self.include_charts)

        # 包含详细信息
        self.include_details = QCheckBox()
        self.include_details.setText("包含详细信息")
        self.include_details.setChecked(True)
        settings_layout.addRow("详情:", self.include_details)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # 生成按钮
        self.generate_btn = QPushButton("生成报告")
        self.generate_btn.setProperty("primary", True)
        self.generate_btn.clicked.connect(self._on_generate)
        layout.addWidget(self.generate_btn)

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

    def _on_select_input(self):
        """选择输入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择分析结果文件",
            "",
            "分析结果 (*.inp *.frd *.dat *.json *.rst);;所有文件 (*.*)",
        )

        if file_path:
            self.input_path_label.setText(file_path)

    def _on_generate(self):
        """生成报告"""
        input_path = self.input_path_label.text()

        if input_path == "未选择文件" or not input_path:
            self.result_text.setText("请先选择输入文件")
            return

        self.generate_btn.setEnabled(False)
        self.result_text.setText("正在生成报告...\n")

        try:
            from sw_helper.report.generator import ReportGenerator

            # 获取设置
            title = self.title_input.text().strip() or "CAE分析报告"
            output_format = self.format_combo.currentData()
            output_path = self.output_path_input.text().strip()

            # 默认输出路径
            if not output_path:
                if output_format == "html":
                    output_path = "./report.html"
                elif output_format == "json":
                    output_path = "./report.json"
                elif output_format == "markdown":
                    output_path = "./report.md"
                elif output_format == "pdf":
                    output_path = "./report.pdf"

            # 分析类型映射
            analysis_type_map = {
                "静力分析": "static",
                "模态分析": "modal",
                "热分析": "thermal",
                "屈曲分析": "buckling",
            }
            analysis_type = analysis_type_map.get(self.analysis_type_combo.currentText(), "static")

            # 创建报告生成器
            generator = ReportGenerator()

            # 生成报告
            result = generator.generate(
                input_file=input_path,
                output_file=output_path,
                report_type=analysis_type,
                title=title,
            )

            if result.get("success"):
                lines = [
                    "【报告生成成功】",
                    "",
                    f"输入文件: {input_path}",
                    f"输出文件: {output_path}",
                    f"报告类型: {self.analysis_type_combo.currentText()}",
                ]

                if result.get("warnings"):
                    lines.append("")
                    lines.append("--- 警告 ---")
                    for w in result["warnings"]:
                        lines.append(f"  - {w}")

                self.result_text.setText("\n".join(lines))
            else:
                self.result_text.setText(f"生成失败: {result.get('error', '未知错误')}")

        except Exception as e:
            self.result_text.setText(f"生成失败: {e}")

        finally:
            self.generate_btn.setEnabled(True)
