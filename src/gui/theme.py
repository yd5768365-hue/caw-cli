"""
CAE-CLI 主题配置 - 深红科技暗黑系

此模块定义应用程序的视觉样式，
包括颜色、字体、图标样式等。
"""

# 主色调
MAIN_RED = "#8B0000"       # 深红/酒红 - 主色调
HIGHLIGHT_RED = "#FF4500"  # 荧光红 - 高亮色
BACKGROUND_BLACK = "#0F0F0F"  # 深黑背景
COOL_GRAY = "#333333"       # 冷灰 - 辅助色
TEXT_WHITE = "#FFFFFF"      # 白色文字

# 扩展色板
DARK_BACKGROUND = "#1A1A1A"    # 较浅的背景
PANEL_BACKGROUND = "#252525"   # 面板背景
BORDER_COLOR = "#404040"      # 边框颜色
INPUT_BACKGROUND = "#2D2D2D"  # 输入框背景

# 状态色
SUCCESS_GREEN = "#28A745"     # 成功
WARNING_YELLOW = "#FFC107"    # 警告
ERROR_RED = "#DC3545"        # 错误
INFO_BLUE = "#17A2B8"        # 信息

# 文本色
PRIMARY_TEXT = "#FFFFFF"      # 主要文字
SECONDARY_TEXT = "#B0B0B0"   # 次要文字
DISABLED_TEXT = "#666666"     # 禁用文字

# 渐变色（用于特殊效果）
GRADIENT_START = "#8B0000"    # 渐变起始
GRADIENT_END = "#4A0000"      # 渐变结束


class CAETheme:
    """主题配置类"""

    # 颜色配置
    colors = {
        "main_red": MAIN_RED,
        "highlight_red": HIGHLIGHT_RED,
        "background": BACKGROUND_BLACK,
        "cool_gray": COOL_GRAY,
        "text_white": TEXT_WHITE,
        "dark_background": DARK_BACKGROUND,
        "panel_background": PANEL_BACKGROUND,
        "border": BORDER_COLOR,
        "input_background": INPUT_BACKGROUND,
        "success": SUCCESS_GREEN,
        "warning": WARNING_YELLOW,
        "error": ERROR_RED,
        "info": INFO_BLUE,
        "primary_text": PRIMARY_TEXT,
        "secondary_text": SECONDARY_TEXT,
        "disabled_text": DISABLED_TEXT,
        "gradient_start": GRADIENT_START,
        "gradient_end": GRADIENT_END,
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
        """获取完整的 QSS 样式表

        Returns:
            str: QSS 样式表字符串
        """
        return f"""
        /* 全局样式 */
        QWidget {{
            background-color: {BACKGROUND_BLACK};
            color: {TEXT_WHITE};
            font-family: "Microsoft YaHei UI", "Segoe UI", Arial;
            font-size: 10pt;
        }}

        /* 主窗口 */
        QMainWindow {{
            background-color: {BACKGROUND_BLACK};
        }}

        /* 菜单栏 */
        QMenuBar {{
            background-color: {DARK_BACKGROUND};
            color: {TEXT_WHITE};
            border-bottom: 1px solid {BORDER_COLOR};
        }}
        QMenuBar::item:selected {{
            background-color: {MAIN_RED};
        }}
        QMenuBar::item:pressed {{
            background-color: {HIGHLIGHT_RED};
        }}

        /* 菜单 */
        QMenu {{
            background-color: {PANEL_BACKGROUND};
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
        }}
        QMenu::item:selected {{
            background-color: {MAIN_RED};
        }}

        /* 按钮 */
        QPushButton {{
            background-color: {COOL_GRAY};
            color: {TEXT_WHITE};
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: {MAIN_RED};
        }}
        QPushButton:pressed {{
            background-color: {HIGHLIGHT_RED};
        }}
        QPushButton:disabled {{
            background-color: {COOL_GRAY};
            color: {DISABLED_TEXT};
        }}
        QPushButton:focus {{
            border: 2px solid {HIGHLIGHT_RED};
        }}

        /* 主要按钮 */
        QPushButton[primary="true"] {{
            background-color: {MAIN_RED};
        }}
        QPushButton[primary="true"]:hover {{
            background-color: {HIGHLIGHT_RED};
        }}

        /* 输入框 */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {INPUT_BACKGROUND};
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
            border-radius: 4px;
            padding: 6px;
            selection-background-color: {MAIN_RED};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {MAIN_RED};
        }}

        /* 组合框 */
        QComboBox {{
            background-color: {INPUT_BACKGROUND};
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
            border-radius: 4px;
            padding: 6px;
        }}
        QComboBox:hover {{
            border: 1px solid {MAIN_RED};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {PANEL_BACKGROUND};
            color: {TEXT_WHITE};
            selection-background-color: {MAIN_RED};
        }}

        /* 标签 */
        QLabel {{
            color: {TEXT_WHITE};
            background-color: transparent;
        }}
        QLabel[heading="true"] {{
            font-size: 14pt;
            font-weight: bold;
            color: {HIGHLIGHT_RED};
        }}

        /* 分组框 */
        QGroupBox {{
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {HIGHLIGHT_RED};
        }}

        /* 表格 */
        QTableWidget, QTableView {{
            background-color: {PANEL_BACKGROUND};
            color: {TEXT_WHITE};
            alternate-background-color: {DARK_BACKGROUND};
            gridline-color: {BORDER_COLOR};
            border: none;
        }}
        QTableWidget::item, QTableView::item {{
            padding: 4px;
        }}
        QTableWidget::item:selected, QTableView::item:selected {{
            background-color: {MAIN_RED};
        }}
        QHeaderView::section {{
            background-color: {COOL_GRAY};
            color: {TEXT_WHITE};
            padding: 8px;
            border: none;
            border-right: 1px solid {BORDER_COLOR};
            border-bottom: 1px solid {BORDER_COLOR};
        }}

        /* 列表 */
        QListWidget, QListView {{
            background-color: {PANEL_BACKGROUND};
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
        }}
        QListWidget::item:selected, QListView::item:selected {{
            background-color: {MAIN_RED};
        }}

        /* 滚动条 */
        QScrollBar:vertical {{
            background-color: {DARK_BACKGROUND};
            width: 12px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background-color: {COOL_GRAY};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {MAIN_RED};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background-color: {DARK_BACKGROUND};
            height: 12px;
            border: none;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {COOL_GRAY};
            border-radius: 6px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {MAIN_RED};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* 进度条 */
        QProgressBar {{
            background-color: {DARK_BACKGROUND};
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
            border-radius: 4px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {MAIN_RED};
            border-radius: 3px;
        }}

        /* 滑块 */
        QSlider::groove:horizontal {{
            background-color: {COOL_GRAY};
            height: 8px;
            border-radius: 4px;
        }}
        QSlider::handle:horizontal {{
            background-color: {HIGHLIGHT_RED};
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }}
        QSlider::groove:vertical {{
            background-color: {COOL_GRAY};
            width: 8px;
            border-radius: 4px;
        }}
        QSlider::handle:vertical {{
            background-color: {HIGHLIGHT_RED};
            height: 16px;
            margin: 0 -4px;
            border-radius: 8px;
        }}

        /* 复选框 */
        QCheckBox {{
            color: {TEXT_WHITE};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {BORDER_COLOR};
            border-radius: 3px;
            background-color: {INPUT_BACKGROUND};
        }}
        QCheckBox::indicator:checked {{
            background-color: {MAIN_RED};
            border-color: {MAIN_RED};
        }}
        QCheckBox::indicator:checked::after {{
            content: "✓";
            color: {TEXT_WHITE};
            font-size: 14px;
        }}

        /* 单选按钮 */
        QRadioButton {{
            color: {TEXT_WHITE};
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {BORDER_COLOR};
            border-radius: 9px;
            background-color: {INPUT_BACKGROUND};
        }}
        QRadioButton::indicator:checked {{
            background-color: {MAIN_RED};
            border-color: {MAIN_RED};
        }}

        /* 选项卡 */
        QTabWidget::pane {{
            border: 1px solid {BORDER_COLOR};
            background-color: {PANEL_BACKGROUND};
        }}
        QTabBar::tab {{
            background-color: {COOL_GRAY};
            color: {TEXT_WHITE};
            padding: 10px 20px;
            border: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: {MAIN_RED};
        }}
        QTabBar::tab:hover {{
            background-color: {HIGHLIGHT_RED};
        }}

        /* 工具栏 */
        QToolBar {{
            background-color: {DARK_BACKGROUND};
            border: none;
            spacing: 8px;
            padding: 4px;
        }}
        QToolButton {{
            background-color: transparent;
            color: {TEXT_WHITE};
            border: none;
            border-radius: 4px;
            padding: 8px;
        }}
        QToolButton:hover {{
            background-color: {MAIN_RED};
        }}
        QToolButton:pressed {{
            background-color: {HIGHLIGHT_RED};
        }}

        /* 状态栏 */
        QStatusBar {{
            background-color: {DARK_BACKGROUND};
            color: {SECONDARY_TEXT};
            border-top: 1px solid {BORDER_COLOR};
        }}

        /* 提示框 */
        QToolTip {{
            background-color: {PANEL_BACKGROUND};
            color: {TEXT_WHITE};
            border: 1px solid {MAIN_RED};
            padding: 4px;
            border-radius: 4px;
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

        /* スピンボックス */
        QSpinBox, QDoubleSpinBox {{
            background-color: {INPUT_BACKGROUND};
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
            border-radius: 4px;
            padding: 4px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {MAIN_RED};
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
            background-color: {INPUT_BACKGROUND};
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
            border-radius: 4px;
            padding: 4px;
        }}

        /* 对话框 */
        QDialog {{
            background-color: {BACKGROUND_BLACK};
        }}
        """

    @classmethod
    def get_color(cls, name: str) -> str:
        """获取指定名称的颜色

        Args:
            name: 颜色名称

        Returns:
            str: 颜色值（十六进制）
        """
        return cls.colors.get(name, TEXT_WHITE)

    @classmethod
    def get_font(cls, name: str) -> tuple:
        """获取指定名称的字体配置

        Args:
            name: 字体名称

        Returns:
            tuple: (family, size, weight) 元组
        """
        return cls.fonts.get(name, cls.fonts["body"])
