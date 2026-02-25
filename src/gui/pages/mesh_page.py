"""
网格分析页面

此模块提供网格质量分析功能的GUI界面。
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
    QDoubleSpinBox,
)
from PySide6.QtCore import Signal

from ..theme import CAETheme


class MeshPage(QWidget):
    """网格分析页面类"""

    # 信号：分析完成
    analysis_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("网格质量分析")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QFormLayout()

        # 文件路径
        self.file_path_label = QLabel("未选择文件")
        select_btn = QPushButton("选择网格文件")
        select_btn.clicked.connect(self._on_select_file)
        file_layout.addRow("文件路径:", self.file_path_label)
        file_layout.addWidget(select_btn)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 分析参数区域
        param_group = QGroupBox("分析参数")
        param_layout = QFormLayout()

        # 分析指标
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(["全部", "纵横比", "偏斜度", "正交质量", "雅可比矩阵"])
        param_layout.addRow("分析指标:", self.metric_combo)

        # 质量阈值
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setValue(0.1)
        self.threshold_spin.setSingleStep(0.05)
        param_layout.addRow("质量阈值:", self.threshold_spin)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # 分析按钮
        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.setProperty("primary", True)
        self.analyze_btn.clicked.connect(self._on_analyze)
        layout.addWidget(self.analyze_btn)

        # 结果显示区域
        result_group = QGroupBox("分析结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("分析结果将显示在此处...")
        result_layout.addWidget(self.result_text)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()

    def _on_select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择网格文件",
            "",
            "网格文件 (*.msh *.inp *.bdf *.cas);;所有文件 (*.*)",
        )

        if file_path:
            self.file_path_label.setText(file_path)

    def _on_analyze(self):
        """开始分析"""
        file_path = self.file_path_label.text()

        if file_path == "未选择文件" or not file_path:
            self.result_text.setText("请先选择文件")
            return

        self.analyze_btn.setEnabled(False)
        self.result_text.setText(f"正在分析: {file_path}\n请稍候...")

        try:
            from sw_helper.mesh.quality import MeshQualityAnalyzer

            # 获取分析指标
            metric_idx = self.metric_combo.currentIndex()
            metric_map = {
                0: None,  # 全部
                1: ["aspect_ratio"],
                2: ["skewness"],
                3: ["orthogonal_quality"],
                4: ["jacobian"],
            }
            metrics = metric_map.get(metric_idx)

            # 分析网格
            analyzer = MeshQualityAnalyzer()
            result = analyzer.analyze(file_path, metrics)

            # 显示结果
            lines = [
                "【分析完成】",
                "",
                f"文件: {file_path}",
                "",
                "--- 质量指标 ---",
            ]

            # 添加指标结果
            metric_names = {
                "aspect_ratio": "纵横比",
                "skewness": "偏斜度",
                "orthogonal_quality": "正交质量",
                "jacobian": "雅可比矩阵",
            }

            for metric, values in result.items():
                if metric == "overall_quality":
                    continue
                name = metric_names.get(metric, metric)
                if isinstance(values, dict):
                    lines.append(f"{name}:")
                    for k, v in values.items():
                        lines.append(f"  {k}: {v}")
                else:
                    lines.append(f"{name}: {values}")

            # 总体评价
            if "overall_quality" in result:
                quality = result["overall_quality"]
                quality_desc = {
                    "excellent": "优秀",
                    "good": "良好",
                    "fair": "一般",
                    "poor": "较差",
                }
                lines.append("")
                lines.append("--- 总体评价 ---")
                lines.append(f"质量等级: {quality_desc.get(quality, quality)}")

            self.result_text.setText("\n".join(lines))

        except ImportError as e:
            self.result_text.setText(f"缺少依赖: {e}\n\n请安装: pip install -e \".[full]\"")
        except FileNotFoundError as e:
            self.result_text.setText(f"文件不存在: {e}")
        except Exception as e:
            self.result_text.setText(f"分析失败: {e}")
        finally:
            self.analyze_btn.setEnabled(True)


# 页面工厂函数
def create_mesh_page() -> MeshPage:
    """创建网格分析页面

    Returns:
        MeshPage: 网格分析页面对象
    """
    return MeshPage()
