"""
CAE-CLI 主题配置 - 现代暗黑科技风 (工程专业风格)

此模块定义应用程序的视觉样式，
包括颜色、字体、图标样式等。
采用更柔和的深灰色背景和专业工程蓝橙配色。
"""

# ==================== 背景色 ====================
BG_PRIMARY = "#1E1E1E"  # 主背景 - 深灰色，更柔和
BG_SECONDARY = "#252525"  # 次级背景
BG_CARD = "rgba(35, 35, 35, 0.9)"  # 卡片背景
BG_GLASS = "rgba(30, 30, 30, 0.85)"  # 毛玻璃效果

# ==================== 边框色 ====================
BORDER_COLOR = "#3A3A3A"  # 边框
BORDER_HOVER = "#165DFF"  # 悬停边框 - 工程蓝

# ==================== 文字色 ====================
TEXT_PRIMARY = "#FFFFFF"  # 主要文字 - 高对比度白色
TEXT_SECONDARY = "#6C6C6C"  # 次要文字 - 中灰色
DISABLED_TEXT = "#3A3A3A"  # 禁用文字 - 低饱和度深灰

# ==================== 强调色 ====================
ACCENT_BLUE = "#165DFF"  # 主蓝色 - 更专业的工程蓝
ACCENT_ORANGE = "#FF7D00"  # 辅助色 - 温暖的工程橙
ACCENT_PURPLE = "#8b5cf6"  # 紫色强调
ACCENT_GREEN = "#22c55e"  # 绿色 (成功状态)
ACCENT_GREEN_HOVER = "#16a34a"  # 绿色悬停

# ==================== 渐变色 ====================
GRADIENT_PRIMARY = "linear-gradient(135deg, #165DFF 0%, #FF7D00 100%)"
GRADIENT_HERO = "linear-gradient(180deg, #252525 0%, #1E1E1E 100%)"

# ==================== 状态色 ====================
SUCCESS_GREEN = "#22c55e"  # 成功
WARNING_YELLOW = "#FF7D00"  # 警告 - 橙色
ERROR_RED = "#F85149"  # 错误
INFO_BLUE = "#165DFF"  # 信息 - 工程蓝

# ==================== 兼容别名 ====================
MAIN_RED = ACCENT_BLUE  # 兼容性别名
HIGHLIGHT_RED = ACCENT_ORANGE  # 兼容性别名 - 橙色
BACKGROUND_BLACK = BG_PRIMARY  # 兼容性别名
COOL_GRAY = BORDER_COLOR  # 兼容性别名
TEXT_WHITE = TEXT_PRIMARY  # 兼容性别名
DARK_BACKGROUND = BG_SECONDARY  # 较浅的背景
PANEL_BACKGROUND = BG_CARD  # 面板背景
INPUT_BACKGROUND = BG_SECONDARY  # 输入框背景

# ==================== 趣味增强色 ====================
ACCENT_GLOW = ACCENT_BLUE  # 柔和蓝光
ACCENT_PULSE = ACCENT_ORANGE  # 橙色脉动
GRADIENT_BLUE_START = "#165DFF"  # 渐变蓝-起始
GRADIENT_ORANGE_END = "#FF7D00"  # 渐变橙-结束
GRADIENT_START = ACCENT_BLUE  # 渐变起始
GRADIENT_END = ACCENT_ORANGE  # 渐变结束


# ==================== 主题类 ====================


class CAETheme:
    """主题配置类"""

    # 颜色配置
    colors = {
        # 背景
        "bg_primary": BG_PRIMARY,
        "bg_secondary": BG_SECONDARY,
        "bg_card": BG_CARD,
        "bg_glass": BG_GLASS,
        # 边框
        "border": BORDER_COLOR,
        "border_hover": BORDER_HOVER,
        # 文字
        "text_primary": TEXT_PRIMARY,
        "text_secondary": TEXT_SECONDARY,
        # 强调色
        "accent_blue": ACCENT_BLUE,
        "accent_purple": ACCENT_PURPLE,
        "accent_green": ACCENT_GREEN,
        # 渐变
        "gradient_primary": GRADIENT_PRIMARY,
        # 兼容别名
        "main_red": MAIN_RED,
        "highlight_red": HIGHLIGHT_RED,
        "background": BACKGROUND_BLACK,
        "cool_gray": COOL_GRAY,
        "text_white": TEXT_WHITE,
        "dark_background": DARK_BACKGROUND,
        "panel_background": PANEL_BACKGROUND,
        "input_background": INPUT_BACKGROUND,
        # 状态
        "success": SUCCESS_GREEN,
        "warning": WARNING_YELLOW,
        "error": ERROR_RED,
        "info": INFO_BLUE,
        # 文字状态
        "primary_text": TEXT_PRIMARY,
        "secondary_text": TEXT_SECONDARY,
        "disabled_text": DISABLED_TEXT,
        # 渐变
        "gradient_start": GRADIENT_START,
        "gradient_end": GRADIENT_END,
        # 趣味增强
        "accent_glow": ACCENT_GLOW,
        "accent_pulse": ACCENT_PULSE,
        "gradient_blue_start": GRADIENT_BLUE_START,
        "gradient_orange_end": GRADIENT_ORANGE_END,
        "dark_gradient_top": BG_SECONDARY,
        "dark_gradient_bottom": BG_PRIMARY,
    }

    # 字体配置
    fonts = {
        "title": ("Microsoft YaHei UI", 16, "bold"),
        "heading": ("Microsoft YaHei UI", 14, "bold"),
        "subheading": ("Microsoft YaHei UI", 12, "bold"),
        "body": ("Microsoft YaHei UI", 10),
        "caption": ("Microsoft YaHei UI", 9),
        "monospace": ("Consolas", 10),
    }

    # 间距配置
    spacing = {
        "xs": 4,
        "sm": 8,
        "md": 12,
        "lg": 16,
        "xl": 24,
        "xxl": 32,
    }

    # 边框配置
    border_radius = {
        "none": 0,
        "sm": 4,
        "md": 8,
        "lg": 12,
    }

    @classmethod
    def get_stylesheet(cls) -> str:
        """获取完整的 QSS 样式表 - 工程专业暗黑风格"""
        return f"""
        /* 全局样式 */
        QWidget {{
            background-color: {BG_PRIMARY};
            color: {TEXT_PRIMARY};
            font-family: "Segoe UI", "Microsoft YaHei UI", Arial;
            font-size: 10pt;
        }}

        /* 主窗口 */
        QMainWindow {{
            background-color: {BG_PRIMARY};
        }}

        /* 菜单栏 */
        QMenuBar {{
            background-color: {BG_GLASS};
            color: {TEXT_PRIMARY};
            border-bottom: 1px solid {BORDER_COLOR};
            padding: 6px 12px;
        }}
        QMenuBar::item:selected {{
            background-color: rgba(22, 93, 255, 0.15);
            border-radius: 4px;
        }}
        QMenuBar::item:pressed {{
            background-color: rgba(22, 93, 255, 0.25);
        }}

        /* 菜单 */
        QMenu {{
            background-color: {BG_SECONDARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            padding: 4px;
        }}
        QMenu::item:selected {{
            background-color: rgba(22, 93, 255, 0.15);
            border-radius: 4px;
        }}

        /* 按钮 - 8px圆角，更现代 */
        QPushButton {{
            background-color: {BG_SECONDARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            padding: 8px 16px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: rgba(22, 93, 255, 0.1);
            border-color: {ACCENT_BLUE};
        }}
        QPushButton:pressed {{
            background-color: rgba(88, 166, 255, 0.2);
        }}
        QPushButton:disabled {{
            background-color: {BG_SECONDARY};
            color: {DISABLED_TEXT};
            border-color: {BORDER_COLOR};
        }}
        QPushButton:focus {{
            border: 2px solid {ACCENT_BLUE};
        }}

        /* 主要按钮 */
        QPushButton[primary="true"] {{
            background: {GRADIENT_PRIMARY};
            color: white;
            border: none;
            font-weight: 500;
        }}
        QPushButton[primary="true"]:hover {{
            background: {GRADIENT_PRIMARY};
            border: none;
        }}
        QPushButton[primary="true"]:pressed {{
            background: {ACCENT_PURPLE};
        }}

        /* 输入框 */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {BG_PRIMARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 8px;
            selection-background-color: rgba(88, 166, 255, 0.3);
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {ACCENT_BLUE};
        }}

        /* 组合框 */
        QComboBox {{
            background-color: {BG_PRIMARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 8px;
        }}
        QComboBox:hover {{
            border: 1px solid {ACCENT_BLUE};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {BG_SECONDARY};
            color: {TEXT_PRIMARY};
            selection-background-color: rgba(88, 166, 255, 0.2);
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
        }}

        /* 标签 */
        QLabel {{
            color: {TEXT_PRIMARY};
            background-color: transparent;
        }}
        QLabel[heading="true"] {{
            font-size: 14pt;
            font-weight: bold;
            color: {ACCENT_BLUE};
        }}

        /* 分组框 */
        QGroupBox {{
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {ACCENT_BLUE};
        }}

        /* 表格 */
        QTableWidget, QTableView {{
            background-color: {BG_SECONDARY};
            color: {TEXT_PRIMARY};
            alternate-background-color: {BG_PRIMARY};
            gridline-color: {BORDER_COLOR};
            border: none;
            border-radius: 8px;
        }}
        QTableWidget::item, QTableView::item {{
            padding: 8px;
        }}
        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: rgba(88, 166, 255, 0.2);
        }}
        QHeaderView::section {{
            background-color: {BG_PRIMARY};
            color: {TEXT_PRIMARY};
            padding: 10px;
            border: none;
            border-right: 1px solid {BORDER_COLOR};
            border-bottom: 1px solid {BORDER_COLOR};
        }}

        /* 列表 */
        QListWidget, QListView {{
            background-color: {BG_SECONDARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
        }}
        QListWidget::item:selected, QListView::item:selected {{
            background-color: rgba(88, 166, 255, 0.2);
        }}

        /* 滚动条 */
        QScrollBar:vertical {{
            background-color: transparent;
            width: 8px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background-color: {BORDER_COLOR};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {ACCENT_BLUE};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background-color: transparent;
            height: 8px;
            border: none;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {BORDER_COLOR};
            border-radius: 4px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {ACCENT_BLUE};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* 进度条 */
        QProgressBar {{
            background-color: {BG_PRIMARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 4px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background: {GRADIENT_PRIMARY};
            border-radius: 3px;
        }}

        /* 滑块 */
        QSlider::groove:horizontal {{
            background-color: {BORDER_COLOR};
            height: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {GRADIENT_PRIMARY};
            width: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        QSlider::groove:vertical {{
            background-color: {BORDER_COLOR};
            width: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:vertical {{
            background: {GRADIENT_PRIMARY};
            height: 16px;
            margin: 0 -5px;
            border-radius: 8px;
        }}

        /* 复选框 */
        QCheckBox {{
            color: {TEXT_PRIMARY};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {BORDER_COLOR};
            border-radius: 4px;
            background-color: {BG_PRIMARY};
        }}
        QCheckBox::indicator:checked {{
            background-color: {ACCENT_BLUE};
            border-color: {ACCENT_BLUE};
        }}

        /* 单选按钮 */
        QRadioButton {{
            color: {TEXT_PRIMARY};
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {BORDER_COLOR};
            border-radius: 9px;
            background-color: {BG_PRIMARY};
        }}
        QRadioButton::indicator:checked {{
            background-color: {ACCENT_BLUE};
            border-color: {ACCENT_BLUE};
        }}

        /* 选项卡 */
        QTabWidget::pane {{
            border: none;
            background-color: transparent;
        }}
        QTabBar::tab {{
            background-color: {BG_PRIMARY};
            color: {TEXT_SECONDARY};
            padding: 10px 20px;
            border: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {BG_SECONDARY};
            color: {ACCENT_BLUE};
        }}
        QTabBar::tab:hover {{
            background-color: rgba(88, 166, 255, 0.1);
            color: {TEXT_PRIMARY};
        }}

        /* 工具栏 */
        QToolBar {{
            background-color: {BG_GLASS};
            border: none;
            spacing: 8px;
            padding: 4px;
        }}
        QToolButton {{
            background-color: transparent;
            color: {TEXT_PRIMARY};
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
        }}
        QToolButton:hover {{
            background-color: rgba(88, 166, 255, 0.1);
        }}
        QToolButton:pressed {{
            background-color: rgba(88, 166, 255, 0.2);
        }}

        /* 状态栏 */
        QStatusBar {{
            background-color: {BG_SECONDARY};
            color: {TEXT_SECONDARY};
            border-top: 1px solid {BORDER_COLOR};
            padding: 4px;
        }}

        /* 提示框 */
        QToolTip {{
            background-color: {BG_SECONDARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {ACCENT_BLUE};
            padding: 6px 10px;
            border-radius: 6px;
        }}

        /* 分割器 */
        QSplitter::handle {{
            background-color: {BORDER_COLOR};
        }}
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        QSplitter::handle:vertical {{
            height: 2px;
        }}

        /* _spinbox */
        QSpinBox, QDoubleSpinBox {{
            background-color: {BG_PRIMARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 6px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {ACCENT_BLUE};
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            border: none;
            background-color: transparent;
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            border: none;
            background-color: transparent;
        }}

        /* 日期时间选择器 */
        QDateTimeEdit {{
            background-color: {BG_PRIMARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 6px;
        }}

        /* 对话框 */
        QDialog {{
            background-color: {BG_PRIMARY};
        }}
        """

    @classmethod
    def get_animations_stylesheet(cls) -> str:
        """获取动画增强的 QSS 样式表

        注意: Qt的QSS不支持@keyframes动画和box-shadow，
        动画效果由Python代码中的QPropertyAnimation实现
        """
        return f"""
        /* 按钮悬停发光效果 */
        QPushButton[primary="true"] {{
            background: {GRADIENT_PRIMARY};
            border: none;
            color: white;
        }}
        QPushButton[primary="true"]:hover {{
            border: 2px solid {ACCENT_BLUE};
        }}

        /* 打字机光标样式 */
        .typing-cursor {{
            background-color: {ACCENT_BLUE};
        }}

        /* 加载动画占位符 */
        .loading-spinner {{
            background: {GRADIENT_PRIMARY};
            border-radius: 4px;
        }}
        """

    @classmethod
    def get_color(cls, name: str) -> str:
        """获取指定名称的颜色"""
        return cls.colors.get(name, TEXT_WHITE)

    @classmethod
    def get_font(cls, name: str) -> tuple:
        """获取指定名称的字体配置"""
        return cls.fonts.get(name, cls.fonts["body"])
