"""
AI助手页面

此模块提供AI辅助设计功能的GUI界面。
"""

import os  # 性能优化：模块级别导入

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


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

        self.generate_btn.setEnabled(False)
        self.result_text.setText("正在生成模型...\n请稍候...")

        try:
            from sw_helper.ai.model_generator import AIModelGenerator

            # 判断是否使用模拟模式
            use_mock = self.model_combo.currentIndex() == 0

            # 创建生成器
            generator = AIModelGenerator(use_mock=use_mock)

            # 获取输出目录
            output_dir = os.path.expanduser("~/CAE-CLI/models")

            # 生成模型
            result = generator.generate(description, output_dir=output_dir)

            # 显示结果
            if result.get("success"):
                lines = [
                    "【生成成功】",
                    "",
                    f"描述: {description}",
                    "",
                    "--- 解析结果 ---",
                ]

                parsed = result.get("parsed", {})
                lines.append(f"形状: {parsed.get('shape_type', 'N/A')}")

                params = parsed.get("parameters", {})
                if params:
                    lines.append("参数:")
                    for k, v in params.items():
                        lines.append(f"  {k}: {v}")

                features = parsed.get("features", [])
                if features:
                    lines.append("特征:")
                    for f in features:
                        lines.append(f"  - {f.get('type')}: {f}")

                lines.append("")
                lines.append("--- 输出文件 ---")
                outputs = result.get("outputs", {})
                for key, path in outputs.items():
                    lines.append(f"{key}: {path}")

                self.result_text.setText("\n".join(lines))
            else:
                self.result_text.setText(f"生成失败: {result.get('error', '未知错误')}")

        except ImportError as e:
            self.result_text.setText(f'缺少依赖: {e}\n\n请安装: pip install -e ".[full]"')
        except Exception as e:
            self.result_text.setText(f"生成失败: {e}")
        finally:
            self.generate_btn.setEnabled(True)

    def _on_mock(self):
        """模拟模式生成"""
        description = self.description_text.toPlainText().strip()

        if not description:
            self.result_text.setText("请输入模型描述")
            return

        try:
            from sw_helper.ai.model_generator import AIModelGenerator

            # 强制使用模拟模式
            generator = AIModelGenerator(use_mock=True)

            output_dir = os.path.expanduser("~/CAE-CLI/models")

            result = generator.generate(description, output_dir=output_dir)

            if result.get("success"):
                lines = [
                    "【模拟模式 - 生成成功】",
                    "",
                    f"描述: {description}",
                    "",
                    "--- 解析结果 ---",
                ]

                parsed = result.get("parsed", {})
                lines.append(f"形状: {parsed.get('shape_type', 'N/A')}")

                params = parsed.get("parameters", {})
                if params:
                    lines.append("参数:")
                    for k, v in params.items():
                        lines.append(f"  {k}: {v}")

                lines.append("")
                lines.append("--- 输出文件 ---")
                lines.append("(模拟模式，不实际生成文件)")

                self.result_text.setText("\n".join(lines))
            else:
                self.result_text.setText(f"解析失败: {result.get('error', '未知错误')}")

        except Exception as e:
            self.result_text.setText(f"错误: {e}")


# 页面工厂函数
def create_ai_page() -> AIPage:
    """创建AI助手页面

    Returns:
        AIPage: AI助手页面对象
    """
    return AIPage()
