#!/usr/bin/env python3
"""
CAE-CLI GUI 入口文件

提供图形用户界面启动入口，支持依赖检查和优雅的错误提示。

Author: CAE-CLI Team
Version: 1.0.0
"""

import sys
from pathlib import Path

# ==================== 配置常量 ====================
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

APP_NAME = "MechDesign"
APP_VERSION = "1.0.0"

# UI 样式配置
UI = {
    "banner_width": 60,
    "colors": {
        "error": "\033[91m",  # 红色
        "warning": "\033[93m",  # 黄色
        "info": "\033[94m",  # 蓝色
        "success": "\033[92m",  # 绿色
        "accent": "\033[96m",  # 青色
        "bold": "\033[1m",  # 加粗
        "reset": "\033[0m",  # 重置
    },
}


# ==================== 启动横幅 ====================


def _print_banner() -> None:
    """打印启动横幅"""
    c = UI["colors"]
    banner = f"""
{c['accent']}{'═' * 60}
{c['bold']}███╗   ███╗███████╗ ██████╗██╗  ██╗██████╗ ███████╗███████╗
 ████╗ ████║██╔════╝██╔════╝██║  ██║██╔══██╗██╔════╝██╔════╝
 ██╔████╔██║█████╗  ██║     ███████║██║  ██║█████╗  ███████╗
 ██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██║  ██║██╔══╝  ╚════██║
 ██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██████╔╝███████╗███████║
 ╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝{c['reset']}

   {c['info']}◆{c['reset']} 机械设计学习辅助工具
   {c['info']}◆{c['reset']} 版本: {c['success']}{APP_VERSION}{c['reset']}

   {c['accent']}{'═' * 60}{c['reset']}
"""
    print(banner)


# ==================== 依赖检查 ====================


def check_dependencies() -> list[str]:
    """检查GUI所需依赖是否已安装

    Returns:
        缺失的依赖列表，如果全部满足则返回空列表
    """
    import importlib.util

    missing = []

    # 检查 PySide6
    if importlib.util.find_spec("PySide6") is None:
        missing.append("PySide6")

    # 检查 PySide6.QtWebEngineWidgets
    if importlib.util.find_spec("PySide6.QtWebEngineWidgets") is None:
        missing.append("PySide6-QtWebEngineWidgets")

    return missing


# ==================== 错误提示 ====================


def _print_section(title: str) -> None:
    """打印分隔章节"""
    c = UI["colors"]
    width = UI["banner_width"]
    print(f"\n{c['bold']}{title}{c['reset']}")
    print(f"{c['accent']}{'─' * width}{c['reset']}")


def show_install_guide(missing: list[str]) -> None:
    """显示详细的安装指南

    Args:
        missing: 缺失的依赖列表
    """
    c = UI["colors"]
    width = UI["banner_width"]

    # 打印横幅
    print(f"\n{c['error']}╔{'═' * (width-2)}╗{c['reset']}")
    print(
        f"{c['error']}║{c['reset']}{c['bold']}{'CAE-CLI GUI 启动失败':^{width-4}}{c['reset']}{c['error']}║{c['reset']}"
    )
    print(f"{c['error']}╚{'═' * (width-2)}╝{c['reset']}")

    # 原因
    _print_section(f"{c['error']}◆ 缺少依赖{c['reset']}")
    for dep in missing:
        print(f"  {c['error']}•{c['reset']} {dep}")

    # 安装方案
    _print_section(f"{c['info']}◆ 安装方案{c['reset']}")

    print(f"""
  {c['success']}┌─── 方案一: 基础安装{c['reset']}
  │  pip install PySide6 PySide6-Addons PySide6-WebEngine
  │
  {c['success']}├─── 方案二: GUI版本{c['reset']}
  │  pip install -e ".[gui]"
  │
  {c['success']}└─── 方案三: 完整功能{c['reset']}
     pip install -e ".[full]"
""")

    # 提示
    print(f"{c['warning']}💡 提示{c['reset']}: PySide6-WebEngine 需要 Visual C++ 运行时")
    print("   Windows: 确认已安装 Visual C++ Redistributable 2015-2022")

    print(f"\n{c['accent']}{'─' * width}{c['reset']}\n")

    # 等待用户确认
    try:
        input(f"{c['info']}按回车键退出...{c['reset']}")
    except (KeyboardInterrupt, EOFError):
        print(f"\n{c['warning']}已退出{c['reset']}")


# ==================== GUI 启动 ====================


def setup_application() -> None:
    """配置应用程序样式和属性"""
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import QApplication

    # 设置应用程序调色板
    app = QApplication.instance()
    if app:
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(13, 17, 23))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(201, 209, 217))
        app.setPalette(palette)


def launch_gui() -> int:
    """启动GUI应用程序

    Returns:
        应用程序退出码
    """
    from PySide6.QtWidgets import QApplication

    from gui.main_window import create_main_window

    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setDesktopFileName(APP_NAME)

    # 应用样式配置
    setup_application()

    # 创建并显示主窗口
    window = create_main_window()
    window.show()

    # 进入事件循环
    return app.exec()


# ==================== 主入口 ====================


def main() -> int:
    """应用程序入口点

    Returns:
        退出码，0表示正常退出
    """
    # 打印启动横幅
    _print_banner()

    # 检查依赖
    print(f"{UI['colors']['info']}正在检查依赖...{UI['colors']['reset']}")
    missing_deps = check_dependencies()

    if missing_deps:
        show_install_guide(missing_deps)
        return 1

    print(f"{UI['colors']['success']}[SUCCESS] 依赖检查完成{UI['colors']['reset']}\n")

    # 启动GUI
    print(f"{UI['colors']['info']}正在启动GUI...{UI['colors']['reset']}")
    try:
        return launch_gui()
    except Exception as e:
        c = UI["colors"]
        print(f"\n{c['error']}╔{'─' * 56}╗{c['reset']}")
        print(
            f"{c['error']}║{c['reset']}  {c['bold']}启动失败{c['reset']}{c['error']}                                      ║{c['reset']}"
        )
        print(f"{c['error']}╠{'═' * 56}╣{c['reset']}")
        print(f"{c['error']}║{c['reset']}  错误: {e:<46} {c['error']}║{c['reset']}")
        print(f"{c['error']}╚{'─' * 56}╝{c['reset']}")
        print(f"\n{c['warning']}请检查日志了解详细信息{c['reset']}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
