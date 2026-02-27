"""
CAE-CLI 可视化界面模块

此模块提供 PySide6 桌面应用程序界面，
包括主窗口、页面组件和工作线程。
"""

# 版本信息
__version__ = "1.0.0"

# 导入主题配置
# 导入主窗口
from .main_window import MainWindow
from .theme import (
    BACKGROUND_BLACK,
    COOL_GRAY,
    HIGHLIGHT_RED,
    MAIN_RED,
    TEXT_WHITE,
    CAETheme,
)

__all__ = [
    "__version__",
    # 主题
    "CAETheme",
    "MAIN_RED",
    "HIGHLIGHT_RED",
    "BACKGROUND_BLACK",
    "COOL_GRAY",
    "TEXT_WHITE",
    # 主窗口
    "MainWindow",
]
