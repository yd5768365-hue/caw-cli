"""
CAE-CLI 首页/仪表盘
快速访问常用功能和查看状态
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QGroupBox,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QPen

from ..theme import CAETheme


class DashboardPage(QWidget):
    """首页/仪表盘 - 快速访问入口"""

    # 信号：导航到指定页面
    navigate = Signal(str)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # ===== 欢迎标题 =====
        welcome = QLabel("欢迎使用 CAE-CLI")
        welcome.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        layout.addWidget(welcome)

        subtitle = QLabel("专业的机械CAE命令行工具 - 几何解析 | 网格分析 | 材料查询 | AI辅助")
        subtitle.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # ===== 功能卡片区域 =====
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)

        # 功能卡片定义
        features = [
            {
                "title": "📐 几何解析",
                "desc": "解析 STEP/STL/IGES 文件",
                "cmd": "parse",
                "color": "#2196F3",
            },
            {
                "title": "🔲 网格分析",
                "desc": "分析网格质量和单元指标",
                "cmd": "mesh",
                "color": "#4CAF50",
            },
            {
                "title": "🔧 材料数据库",
                "desc": "查询GB/T标准材料性能",
                "cmd": "material",
                "color": "#FF9800",
            },
            {
                "title": "🤖 AI 助手",
                "desc": "自然语言生成CAD模型",
                "cmd": "ai",
                "color": "#9C27B0",
            },
            {
                "title": "📚 学习中心",
                "desc": "系统化学习CAE知识",
                "cmd": "learn",
                "color": "#E91E63",
            },
            {
                "title": "⚙️ 参数优化",
                "desc": "自动化参数优化循环",
                "cmd": "optimize",
                "color": "#00BCD4",
            },
        ]

        # 创建卡片
        for i, feat in enumerate(features):
            card = self._create_feature_card(
                feat["title"],
                feat["desc"],
                feat["cmd"],
                feat["color"]
            )
            cards_layout.addWidget(card, i // 3, i % 3)

        layout.addLayout(cards_layout)

        # ===== 快速命令区 =====
        cmd_group = QGroupBox("⚡ 快速命令")
        cmd_layout = QVBoxLayout()

        cmd_intro = QLabel("在下方输入命令快速执行（对应 cae-cli 命令）：")
        cmd_intro.setStyleSheet("color: #666;")
        cmd_layout.addWidget(cmd_intro)

        self.cmd_input = QLabel("💡 输入: cae-cli <命令> [参数]")
        self.cmd_input.setStyleSheet("""
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 14px;
        """)
        cmd_layout.addWidget(self.cmd_input)

        # 示例命令
        examples = QLabel("""
Examples:
  • cae-cli parse model.step           解析几何文件
  • cae-cli analyze mesh.msh          分析网格质量
  • cae-cli material Q235             查询材料属性
  • cae-cli learn list                查看课程列表
  • cae-cli ai generate "立方体"      AI生成模型
        """)
        examples.setStyleSheet("""
            font-family: monospace;
            font-size: 12px;
            color: #888;
            background: #fafafa;
            padding: 10px;
            border-radius: 3px;
        """)
        cmd_layout.addWidget(examples)

        cmd_group.setLayout(cmd_layout)
        layout.addWidget(cmd_group)

        # ===== 状态信息 =====
        status_group = QGroupBox("📊 系统状态")
        status_layout = QHBoxLayout()

        # 检查依赖
        self._add_status_item(status_layout, "Python", self._check_python(), "🟢")
        self._add_status_item(status_layout, "FreeCAD", self._check_freecad(), "🟡")
        self._add_status_item(status_layout, "Ollama", self._check_ollama(), "⚪")

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        layout.addStretch()

    def _create_feature_card(self, title: str, desc: str, cmd: str, color: str) -> QWidget:
        """创建功能卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
            QFrame:hover {{
                background: #fafafa;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # 描述
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("color: #666;")
        layout.addWidget(desc_label)

        # 点击按钮
        btn = QPushButton("进入 →")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """)
        btn.clicked.connect(lambda: self.navigate.emit(cmd))
        layout.addWidget(btn)

        return card

    def _add_status_item(self, layout, name: str, status: str, icon: str):
        """添加状态项"""
        item = QLabel(f"{icon} {name}: {status}")
        item.setStyleSheet("padding: 5px 10px;")
        layout.addWidget(item)

    def _check_python(self) -> str:
        """检查Python版本"""
        import sys
        return f"Python {sys.version_info.major}.{sys.version_info.minor}"

    def _check_freecad(self) -> str:
        """检查FreeCAD"""
        try:
            import FreeCAD
            return f"可用 (FreeCAD {FreeCAD.BuildVersion()})"
        except ImportError:
            return "未安装"

    def _check_ollama(self) -> str:
        """检查Ollama"""
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                models = r.json().get("models", [])
                count = len(models)
                return f"运行中 ({count}个模型)"
        except:
            pass
        return "未运行"
