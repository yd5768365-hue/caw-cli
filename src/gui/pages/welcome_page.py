"""
CAE-CLI 启动画面 - 简化版
"""

import os
import re

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# 导入粒子特效
try:
    from ..particles import ParticleWidget
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from particles import ParticleWidget


class WelcomePage(QWidget):
    """启动画面"""

    # 信号：点击开始探索
    start_exploring = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_particles()
        self._init_ui()
        self._start_animations()

    def _setup_particles(self):
        """设置粒子特效"""
        self.particle_widget = ParticleWidget(self)
        self.particle_widget.setGeometry(self.rect())
        self.particle_widget.lower()
        self.particle_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def resizeEvent(self, event):
        """窗口大小改变"""
        super().resizeEvent(event)
        if hasattr(self, "particle_widget"):
            self.particle_widget.setGeometry(self.rect())

    def _init_ui(self):
        """初始化UI"""
        # 颜色定义
        BG_DEEP = "#030810"
        BG_CARD = "#0f1d32"
        ACCENT_PURPLE = "#8b5cf6"
        ACCENT_CYAN = "#06b6d4"
        TEXT_PRIMARY = "#f1f5f9"
        FONT_MONO = "Consolas"
        FONT_CN = "Microsoft YaHei UI"

        # 主布局
        self.setStyleSheet(f"background-color: {BG_DEEP};")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(30)

        # ===== 左侧品牌 =====
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: transparent;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(20)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        left_layout.setContentsMargins(40, 0, 0, 0)

        # 标题
        self.brand_name = QLabel("MechDesign")
        self.brand_name.setFont(QFont(FONT_MONO, 60, QFont.Weight.Bold))
        self.brand_name.setStyleSheet(f"""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {ACCENT_PURPLE},
                stop:0.5 {ACCENT_CYAN},
                stop:1 {TEXT_PRIMARY});
            letter-spacing: 6px;
            opacity: 0;
        """)
        left_layout.addWidget(self.brand_name)

        # 副标题
        self.brand_sub = QLabel("机械设计学习辅助工具")
        self.brand_sub.setFont(QFont(FONT_CN, 22, QFont.Weight.Medium))
        self.brand_sub.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            letter-spacing: 4px;
            margin-bottom: 20px;
            opacity: 0;
        """)
        left_layout.addWidget(self.brand_sub)

        # 分隔线
        divider = QFrame()
        divider.setFixedWidth(280)
        divider.setFixedHeight(2)
        divider.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {ACCENT_PURPLE},
                stop:0.5 {ACCENT_CYAN},
                stop:1 transparent);
            border-radius: 2px;
            opacity: 0;
        """)
        left_layout.addWidget(divider)
        self.divider = divider

        # 愿景
        self.vision = QLabel(
            "CAE-CLI 的终极目标不是成为下一个 Ansys，\n"
            "而是成为工程领域的 Jupyter Notebook——\n"
            "一个开放、灵活、充满可能性的学习和研究平台。\n"
            "在这个平台上，人工智能与工程计算深度融合，\n"
            "人类智慧与机器算力协同增效..."
        )
        self.vision.setFont(QFont(FONT_CN, 16))
        self.vision.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            line-height: 2.0;
            max-width: 480px;
            opacity: 0;
        """)
        self.vision.setWordWrap(True)
        left_layout.addWidget(self.vision)

        # 功能标签
        features = QWidget()
        features.setStyleSheet("background-color: transparent; opacity: 0;")
        features_layout = QHBoxLayout(features)
        features_layout.setSpacing(12)
        features_layout.setContentsMargins(0, 14, 0, 0)

        feature_list = [
            ("🔧", "CAD"),
            ("📐", "CAE"),
            ("🧮", "FEA"),
            ("📊", "报告"),
            ("🤖", "AI"),
        ]

        for emoji, label in feature_list:
            tag = QLabel(f"{emoji} {label}")
            tag.setFont(QFont(FONT_CN, 12))
            tag.setStyleSheet(f"""
                color: {TEXT_PRIMARY};
                background-color: rgba(139, 92, 246, 0.15);
                padding: 8px 14px;
                border-radius: 20px;
                border: 1px solid rgba(139, 92, 246, 0.25);
            """)
            features_layout.addWidget(tag)

        left_layout.addWidget(features)
        self.features = features

        # 版本标签
        bottom_section = QWidget()
        bottom_section.setStyleSheet("background-color: transparent; opacity: 0;")
        bottom_layout = QHBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(0, 20, 0, 0)
        bottom_layout.setSpacing(16)

        version_container = QWidget()
        version_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(139, 92, 246, 0.2),
                stop:1 rgba(6, 182, 212, 0.2));
            padding: 10px 18px;
            border-radius: 12px;
            border: 1px solid rgba(139, 92, 246, 0.25);
        """)
        version_inner = QHBoxLayout(version_container)
        version_inner.setContentsMargins(0, 0, 0, 0)
        version_inner.setSpacing(10)

        version_badge = QLabel("v1.0.0")
        version_badge.setFont(QFont(FONT_MONO, 14, QFont.Weight.Bold))
        version_badge.setStyleSheet(f"""
            color: white;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {ACCENT_PURPLE},
                stop:1 {ACCENT_CYAN});
            padding: 6px 14px;
            border-radius: 8px;
            font-weight: 700;
        """)
        version_inner.addWidget(version_badge)

        self.version = QLabel("正式发布 · 全新启航")
        self.version.setFont(QFont(FONT_CN, 15, QFont.Weight.Medium))
        self.version.setStyleSheet(f"color: {TEXT_PRIMARY}; letter-spacing: 1px;")
        version_inner.addWidget(self.version)

        bottom_layout.addWidget(version_container)
        left_layout.addWidget(bottom_section)
        self.version_container = bottom_section

        left_widget.setMinimumWidth(480)
        left_widget.setMaximumWidth(560)
        main_layout.addWidget(left_widget, 1)

        # ===== 右侧卡片 =====
        right_widget = QWidget()
        right_widget.setStyleSheet(f"""
            background-color: {BG_CARD};
            border-radius: 28px;
            border: 1px solid rgba(139, 92, 246, 0.15);
        """)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(14)

        # 标题栏
        title_bar = QWidget()
        title_bar.setStyleSheet("background: transparent;")
        title_bar_layout = QHBoxLayout(title_bar)

        title_text = QLabel("版本演进")
        title_text.setFont(QFont(FONT_CN, 16, QFont.Weight.DemiBold))
        title_text.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: bold;")
        title_bar_layout.addWidget(title_text)
        title_bar_layout.addStretch()

        indicator = QLabel("●")
        indicator.setFont(QFont("Arial", 8))
        indicator.setStyleSheet("color: #22c55e;")
        indicator.setToolTip("自动轮播中")
        title_bar_layout.addWidget(indicator)

        right_layout.addWidget(title_bar)

        # 轮播卡片
        self.carousel_stack = QStackedWidget()
        self.carousel_stack.setStyleSheet("""
            QStackedWidget {
                border: none;
                border-radius: 20px;
                background: transparent;
            }
        """)

        _current_dir = os.path.dirname(os.path.abspath(__file__))
        VERSION_IMG_DIR = os.path.join(_current_dir, "..", "..", "..", ".version", "page")

        preview_cards = [
            {
                "title": "v1.0.0",
                "description": "求解器架构 | 专业蓝系 | 全新启航",
                "icon": "🚀",
                "image_path": f"{VERSION_IMG_DIR}/v.1.0.0.png",
                "is_new": True,
                "accent_color": "#8b5cf6",
                "gradient_colors": ("#8b5cf6", "#4f46e5"),
                "review": """## v1.0.0 版本点评

### 核心亮点
- **全新求解器架构**：采用模块化设计，支持自定义求解器
- **专业蓝系UI**：深蓝色主题，专业感十足
- **双模式运行**：CLI + GUI 桌面版

### 技术改进
- 使用 PySide6 原生开发，性能更强
- 支持自定义插件扩展
- 集成 AI 学习助手（Ollama + RAG）

### 用户体验
- 启动画面动画流畅
- 版本演进轮播展示
- 一键命令执行""",
            },
            {
                "title": "v0.4.0",
                "description": "GUI框架 - PySide6原生 | 卡片式布局",
                "icon": "✨",
                "image_path": f"{VERSION_IMG_DIR}/v0.4.0.png",
                "is_new": False,
                "accent_color": "#06b6d4",
                "gradient_colors": ("#06b6d4", "#0891b2"),
                "review": """## v0.4.0 版本点评

### 核心亮点
- **PySide6 原生 GUI**：完全原生桌面应用体验
- **卡片式布局**：现代 UI 设计，模块清晰

### 技术改进
- 从 WebView 迁移到原生 Qt 控件
- 支持更多交互组件
- 响应式布局适配

### 用户体验
- 点击卡片直接执行命令
- 侧边栏导航
- 进度条显示""",
            },
            {
                "title": "v0.3.0",
                "description": "Web界面 - QWebEngineView | HTML/CSS",
                "icon": "🧠",
                "image_path": f"{VERSION_IMG_DIR}/v.0.3.0.png",
                "is_new": False,
                "accent_color": "#a855f7",
                "gradient_colors": ("#a855f7", "#7c3aed"),
                "review": """## v0.3.0 版本点评

### 核心亮点
- **Web 界面**：使用 HTML/CSS 构建现代 UI
- **QWebEngineView**：嵌入式浏览器渲染

### 技术改进
- 首次引入 Web 前端技术
- JavaScript 与 Python 桥接
- 暗色主题设计

### 用户体验
- 现代化网页风格
- 响应式设计
- 丰富的动画效果""",
            },
            {
                "title": "v0.2.0",
                "description": "核心CLI - 命令行入口 | 纯Python",
                "icon": "💎",
                "image_path": f"{VERSION_IMG_DIR}/v.0.2.0.png",
                "is_new": False,
                "accent_color": "#f59e0b",
                "gradient_colors": ("#f59e0b", "#d97706"),
                "review": """## v0.2.0 版本点评

### 核心亮点
- **纯 Python CLI**：轻量级命令行工具
- **核心功能**：几何解析、网格分析、材料查询

### 技术改进
- Click 命令行框架
- Rich 终端美化
- 模块化架构设计

### 用户体验
- 快速安装和使用
- 详细的帮助信息
- 错误提示友好""",
            },
        ]

        self.preview_cards_data = preview_cards
        self.current_card_index = 0

        for idx, card in enumerate(preview_cards):
            card_widget = self._create_carousel_card(
                title=card["title"],
                description=card["description"],
                icon=card["icon"],
                image_path=card.get("image_path"),
                is_new=card.get("is_new", False),
                accent_color=card.get("accent_color", "#8b5cf6"),
                gradient_colors=card.get("gradient_colors", ("#8b5cf6", "#4f46e5")),
                card_index=idx,
            )
            self.carousel_stack.addWidget(card_widget)

        right_layout.addWidget(self.carousel_stack, 1)

        # 导航
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 12, 0, 0)
        nav_layout.setSpacing(10)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn = QPushButton("‹")
        self.prev_btn.setFixedSize(36, 36)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background: rgba(139, 92, 246, 0.15);
                color: #94a3b8;
                border: 1px solid rgba(139, 92, 246, 0.25);
                border-radius: 18px;
                font-size: 22px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(139, 92, 246, 0.3);
                color: #8b5cf6;
            }
        """)
        self.prev_btn.clicked.connect(self._prev_carousel)
        nav_layout.addWidget(self.prev_btn)

        self.nav_dots = []
        for i in range(len(preview_cards)):
            dot = QPushButton()
            dot.setFixedSize(10, 10)
            if i == 0:
                dot.setStyleSheet("""
                    QPushButton {
                        background: linear-gradient(to right, #8b5cf6, #06b6d4);
                        border: none;
                        border-radius: 5px;
                    }
                """)
            else:
                dot.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255,255,255,0.2);
                        border: none;
                        border-radius: 5px;
                    }
                """)
            dot.clicked.connect(lambda _, idx=i: self._goto_carousel(idx))
            self.nav_dots.append(dot)
            nav_layout.addWidget(dot)

        self.next_btn = QPushButton("›")
        self.next_btn.setFixedSize(36, 36)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: rgba(139, 92, 246, 0.15);
                color: #94a3b8;
                border: 1px solid rgba(139, 92, 246, 0.25);
                border-radius: 18px;
                font-size: 22px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(139, 92, 246, 0.3);
                color: #8b5cf6;
            }
        """)
        self.next_btn.clicked.connect(self._next_carousel)
        nav_layout.addWidget(self.next_btn)

        right_layout.addWidget(nav_widget)

        # 自动轮播
        self.carousel_timer = QTimer(self)
        self.carousel_timer.timeout.connect(self._next_carousel)
        self.carousel_timer.start(4500)

        main_layout.addWidget(right_widget, 3)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # 安装事件过滤器用于点击图片预览
        for i in range(self.carousel_stack.count()):
            card = self.carousel_stack.widget(i)
            card._card_index = i  # 保存卡片索引
            card.installEventFilter(self)

    def _start_animations(self):
        """启动动画"""
        duration = 600
        self._fade_in_widget(self.brand_name, 0, duration)
        QTimer.singleShot(100, lambda: self._fade_in_widget(self.brand_sub, 0, duration))
        QTimer.singleShot(200, lambda: self._fade_in_widget(self.divider, 0, duration))
        QTimer.singleShot(300, lambda: self._fade_in_widget(self.vision, 0, duration))
        QTimer.singleShot(400, lambda: self._fade_in_widget(self.features, 0, duration))
        QTimer.singleShot(500, lambda: self._fade_in_widget(self.version_container, 0, duration))

    def _fade_in_widget(self, widget, start_opacity=0, duration=600):
        """淡入动画"""
        style = widget.styleSheet()
        if "opacity: 0;" in style:
            style = style.replace("opacity: 0;", "")
            widget.setStyleSheet(style)

        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setStartValue(start_opacity)
        anim.setEndValue(1.0)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()

    def eventFilter(self, obj, event):
        """事件过滤器 - 处理图片和卡片点击"""
        from PySide6.QtCore import QEvent

        if event.type() == QEvent.Type.MouseButtonPress:
            # 查找点击的图片标签
            target = obj
            while target:
                if hasattr(target, "_full_image_path"):
                    self._show_image_menu(target._full_image_path, target._card_index)
                    return True
                # 如果点击的是卡片本身（非图片区域），也弹出菜单
                if hasattr(target, "_card_index") and not hasattr(target, "_full_image_path"):
                    card_index = target._card_index
                    card_data = self.preview_cards_data[card_index]
                    image_path = card_data.get("image_path")
                    if image_path and os.path.exists(image_path):
                        self._show_image_menu(image_path, card_index)
                    else:
                        # 没有图片直接显示点评
                        self._show_version_review(card_index)
                    return True
                target = target.parent()
        return super().eventFilter(obj, event)

    def _show_image_menu(self, image_path: str, card_index: int):
        """显示图片操作菜单"""
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

        # 创建选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("选择操作")
        dialog.setFixedSize(300, 200)
        dialog.setStyleSheet("background-color: #0f1d32;")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel("请选择操作")
        title.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: white; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 查看大图按钮
        view_btn = QPushButton("🔍 查看大图")
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        view_btn.clicked.connect(lambda: [dialog.close(), self._show_full_image(image_path)])
        layout.addWidget(view_btn)

        # 查看点评按钮
        review_btn = QPushButton("📝 查看版本点评")
        review_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        review_btn.setStyleSheet("""
            QPushButton {
                background-color: #06b6d4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0891b2;
            }
        """)
        review_btn.clicked.connect(lambda: [dialog.close(), self._show_version_review(card_index)])
        layout.addWidget(review_btn)

        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #64748b;
            }
        """)
        cancel_btn.clicked.connect(dialog.close)
        layout.addWidget(cancel_btn)

        dialog.exec()

    def _show_full_image(self, image_path: str):
        """显示完整大图"""
        from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("图片预览")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet("background-color: #0f1d32;")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                QSize(760, 540),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            image_label.setPixmap(scaled)
        else:
            image_label.setText("图片加载失败")
            image_label.setStyleSheet("color: #94a3b8; font-size: 16px;")

        layout.addWidget(image_label)

        # 添加底部按钮
        btn_layout = QHBoxLayout()

        close_btn = QPushButton("关闭")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #64748b;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    def _show_version_review(self, card_index: int):
        """显示版本点评"""
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import (
            QDialog,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QScrollArea,
            QTextBrowser,
            QVBoxLayout,
        )

        card_data = self.preview_cards_data[card_index]
        title = card_data.get("title", "")
        review = card_data.get("review", "暂无点评")
        icon = card_data.get("icon", "📝")
        gradient_colors = card_data.get("gradient_colors", ("#8b5cf6", "#4f46e5"))

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{icon} {title} 版本点评")
        dialog.setMinimumSize(700, 550)
        dialog.setStyleSheet("background-color: #0f1d32;")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)

        # 标题栏
        header = QWidget()
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {gradient_colors[0]},
                stop:1 {gradient_colors[1]});
            border-radius: 12px;
            padding: 16px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)

        title_label = QLabel(f"{icon} {title} 版本点评")
        title_label.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; border: none;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header)

        # 点评内容
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1e293b;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #475569;
                border-radius: 4px;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 使用 QTextBrowser 显示 Markdown 格式
        text_browser = QTextBrowser()
        text_browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: transparent;
                color: #e2e8f0;
                padding: 0;
            }
        """)
        text_browser.setHtml(self._markdown_to_html(review))
        content_layout.addWidget(text_browser)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll, 1)

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # 查看大图按钮
        image_path = card_data.get("image_path")
        if image_path and os.path.exists(image_path):
            view_img_btn = QPushButton("查看大图")
            view_img_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_img_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8b5cf6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #7c3aed;
                }
            """)
            view_img_btn.clicked.connect(lambda: self._show_full_image(image_path))
            btn_layout.addWidget(view_img_btn)

        close_btn = QPushButton("关闭")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #64748b;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    def _markdown_to_html(self, md_content: str) -> str:
        """简单的Markdown转HTML"""
        html = md_content

        # 代码块
        html = re.sub(r"```(\w+)?\n(.*?)```", r"<pre><code>\2</code></pre>", html, flags=re.DOTALL)

        # 标题
        for i in range(6, 0, -1):
            html = re.sub(rf'^({"#"*i}) (.+)$', rf"<h{i}>\2</h{i}>", html, flags=re.MULTILINE)

        # 粗体
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

        # 斜体
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

        # 列表
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        html = re.sub(r"(<li>.*</li>)", r"<ul>\1</ul>", html)

        # 换行
        html = html.replace("\n\n", "</p><p>")
        html = f"<p>{html}</p>"

        # 基础样式 - 暗黑主题
        style = """
        <style>
            body {
                font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
                line-height: 1.8;
                color: #e2e8f0;
                background-color: transparent;
                padding: 16px;
            }
            h1, h2, h3 {
                color: #a78bfa;
                margin-top: 20px;
                margin-bottom: 12px;
                font-weight: 600;
            }
            h1 { font-size: 1.6em; border-bottom: 1px solid #334155; padding-bottom: 8px; }
            h2 { font-size: 1.3em; }
            h3 { font-size: 1.1em; }
            code {
                background: #1e293b;
                color: #f472b6;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: "Consolas", monospace;
            }
            pre {
                background: #1e293b;
                border: 1px solid #334155;
                padding: 12px;
                border-radius: 6px;
                overflow-x: auto;
            }
            pre code {
                background: transparent;
                color: #e2e8f0;
            }
            ul {
                padding-left: 24px;
            }
            li {
                margin: 6px 0;
                color: #cbd5e1;
            }
            strong {
                color: #fbbf24;
            }
            em {
                color: #38bdf8;
            }
            p {
                margin: 8px 0;
            }
        </style>
        """

        return f"<!DOCTYPE html><html><head>{style}</head><body>{html}</body></html>"

    def _next_carousel(self):
        current = self.carousel_stack.currentIndex()
        next_index = (current + 1) % self.carousel_stack.count()
        self.carousel_stack.setCurrentIndex(next_index)
        self._update_nav_dots(next_index)

    def _prev_carousel(self):
        current = self.carousel_stack.currentIndex()
        prev_index = (current - 1) % self.carousel_stack.count()
        self.carousel_stack.setCurrentIndex(prev_index)
        self._update_nav_dots(prev_index)

    def _goto_carousel(self, index: int):
        current = self.carousel_stack.currentIndex()
        if current != index:
            self.carousel_stack.setCurrentIndex(index)
            self._update_nav_dots(index)
            self.carousel_timer.stop()
            self.carousel_timer.start(4500)

    def _update_nav_dots(self, index: int):
        for i, dot in enumerate(self.nav_dots):
            if i == index:
                dot.setStyleSheet("""
                    QPushButton {
                        background: linear-gradient(to right, #8b5cf6, #06b6d4);
                        border: none;
                        border-radius: 4px;
                    }
                """)
                dot.setFixedSize(24, 8)
            else:
                dot.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255,255,255,0.2);
                        border: none;
                        border-radius: 5px;
                    }
                """)
                dot.setFixedSize(10, 10)

    def _create_carousel_card(
        self,
        title,
        description,
        icon,
        image_path=None,
        is_new=False,
        accent_color="#8b5cf6",
        gradient_colors=("#8b5cf6", "#4f46e5"),
        card_index=0,
    ):
        """创建轮播卡片"""
        TEXT_PRIMARY = "#ffffff"

        card = QFrame()
        gradient_start, gradient_end = gradient_colors
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {gradient_start},
                    stop:1 {gradient_end});
                border-radius: 20px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 头部
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Microsoft YaHei UI", 24))
        header_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        if is_new:
            new_badge = QLabel("NEW")
            new_badge.setFont(QFont("Microsoft YaHei UI", 10, QFont.Weight.Bold))
            new_badge.setStyleSheet("""
                color: white;
                background: #22c55e;
                padding: 4px 10px;
                border-radius: 6px;
            """)
            header_layout.addWidget(new_badge)

        layout.addWidget(header)

        # 描述
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Microsoft YaHei UI", 12))
        desc_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # 图片
        if image_path:
            image_label = QLabel()
            image_label.setMinimumHeight(100)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setCursor(Qt.CursorShape.PointingHandCursor)

            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        QSize(280, 120),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    image_label.setPixmap(scaled)
                    # 保存完整路径用于点击预览
                    image_label._full_image_path = image_path
                    # 保存卡片索引用于点评
                    image_label._card_index = card_index
                else:
                    image_label.setText(title)
                    image_label.setStyleSheet(
                        f"color: {TEXT_PRIMARY}; background: rgba(0,0,0,0.2); border-radius: 8px; padding: 20px;"
                    )
            else:
                image_label.setText(title)
                image_label.setStyleSheet(
                    f"color: {TEXT_PRIMARY}; background: rgba(0,0,0,0.2); border-radius: 8px; padding: 20px;"
                )

            layout.addWidget(image_label)

        return card


def create_welcome_page() -> WelcomePage:
    """创建首页"""
    return WelcomePage()
