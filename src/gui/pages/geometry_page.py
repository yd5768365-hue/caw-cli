"""
几何解析页面

此模块提供几何文件解析功能的GUI界面。
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTextEdit,
    QGroupBox,
    QFormLayout,
    QComboBox,
)
from PySide6.QtCore import Signal

from ..theme import CAETheme


class GeometryPage(QWidget):
    """几何解析页面类"""

    # 信号：解析完成
    parse_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("几何文件解析")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QFormLayout()

        # 文件格式选择
        self.format_combo = QComboBox()
        self.format_combo.addItems(["自动检测", "STEP", "STL", "IGES"])
        file_layout.addRow("文件格式:", self.format_combo)

        # 文件路径
        self.file_path_label = QLabel("未选择文件")
        select_btn = QPushButton("选择文件")
        select_btn.clicked.connect(self._on_select_file)
        file_layout.addRow("文件路径:", self.file_path_label)
        file_layout.addWidget(select_btn)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 解析按钮
        self.parse_btn = QPushButton("开始解析")
        self.parse_btn.setProperty("primary", True)
        self.parse_btn.clicked.connect(self._on_parse)
        layout.addWidget(self.parse_btn)

        # 结果显示区域
        result_group = QGroupBox("解析结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("解析结果将显示在此处...")
        result_layout.addWidget(self.result_text)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()

    def _on_select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择几何文件",
            "",
            "几何文件 (*.step *.stp *.stl *.iges *.igs);;所有文件 (*.*)",
        )

        if file_path:
            self.file_path_label.setText(file_path)

    def _on_parse(self):
        """开始解析"""
        file_path = self.file_path_label.text()

        if file_path == "未选择文件" or not file_path:
            self.result_text.setText("请先选择文件")
            return

        self.parse_btn.setEnabled(False)
        self.result_text.setText(f"正在解析: {file_path}\n请稍候...")

        try:
            from sw_helper.geometry.parser import GeometryParser

            # 获取格式
            format_idx = self.format_combo.currentIndex()
            format_map = {1: "step", 2: "stl", 3: "iges"}
            file_format = format_map.get(format_idx)

            # 解析文件
            parser = GeometryParser()
            result = parser.parse(file_path, file_format)

            # 显示结果
            lines = [
                "【解析成功】",
                "",
                f"文件: {result.get('file', 'N/A')}",
                f"格式: {result.get('format', 'N/A').upper()}",
                "",
                "--- 几何信息 ---",
            ]

            # 添加详细信息
            info_keys = ["vertices", "faces", "edges"]
            for key in info_keys:
                if key in result:
                    lines.append(f"{key}: {result[key]}")

            # 边界信息
            bounds = result.get("bounds", {})
            if bounds:
                lines.append("")
                lines.append("--- 边界框 ---")
                for axis, (min_val, max_val) in bounds.items():
                    lines.append(f"{axis}轴: {min_val} ~ {max_val}")

            # 体积
            if result.get("volume", 0) > 0:
                lines.append(f"体积: {result.get('volume'):.2e} m³")

            self.result_text.setText("\n".join(lines))

        except ImportError as e:
            self.result_text.setText(f"缺少依赖: {e}\n\n请安装: pip install -e \".[full]\"")
        except FileNotFoundError as e:
            self.result_text.setText(f"文件不存在: {e}")
        except Exception as e:
            self.result_text.setText(f"解析失败: {e}")
        finally:
            self.parse_btn.setEnabled(True)


# 页面工厂函数（用于动态创建页面）
def create_geometry_page() -> GeometryPage:
    """创建几何解析页面

    Returns:
        GeometryPage: 几何解析页面对象
    """
    return GeometryPage()
