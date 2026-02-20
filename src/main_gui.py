#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAE-CLI GUI 入口文件
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查GUI依赖是否安装"""
    missing = []
    
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        missing.append("PySide6")
    
    try:
        from PySide6 import QtWebEngineWidgets
    except ImportError:
        missing.append("PySide6-WebEngine")
    
    return missing

def show_install_guide(missing):
    """显示安装指南"""
    print("=" * 50)
    print("CAE-CLI GUI 启动失败")
    print("=" * 50)
    print("\n缺少以下依赖:")
    for dep in missing:
        print(f"  - {dep}")
    print("\n请运行以下命令安装:")
    print("  pip install PySide6 PySide6-Addons PySide6-WebEngine")
    print("\n或安装完整版:")
    print("  pip install -e '.[full]'")
    print("=" * 50)
    input("\n按回车键退出...")

def main():
    """主函数"""
    # 检查依赖
    missing = check_dependencies()
    
    if missing:
        show_install_guide(missing)
        sys.exit(1)
    
    # 导入并启动 GUI
    from gui.web_gui import main as gui_main
    gui_main()

if __name__ == "__main__":
    main()
