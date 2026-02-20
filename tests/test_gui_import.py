"""
测试 GUI 模块导入

此脚本验证 GUI 模块是否正确创建。
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试模块导入"""
    print("=" * 60)
    print("测试 GUI 模块导入")
    print("=" * 60)
    
    # 测试主题模块
    print("\n1. 测试 theme 模块...")
    from gui.theme import CAETheme, MAIN_RED, HIGHLIGHT_RED
    print(f"   ✓ CAETheme: {CAETheme}")
    print(f"   ✓ MAIN_RED: {MAIN_RED}")
    print(f"   ✓ HIGHLIGHT_RED: {HIGHLIGHT_RED}")
    
    # 测试样式表
    stylesheet = CAETheme.get_stylesheet()
    print(f"   ✓ QSS 样式表长度: {len(stylesheet)} 字符")
    
    # 测试页面模块
    print("\n2. 测试页面模块...")
    from gui.pages import (
        GeometryPage,
        MeshPage,
        MaterialPage,
        OptimizationPage,
        AIPage,
        ChatPage,
    )
    print(f"   ✓ GeometryPage: {GeometryPage}")
    print(f"   ✓ MeshPage: {MeshPage}")
    print(f"   ✓ MaterialPage: {MaterialPage}")
    print(f"   ✓ OptimizationPage: {OptimizationPage}")
    print(f"   ✓ AIPage: {AIPage}")
    print(f"   ✓ ChatPage: {ChatPage}")
    
    # 测试工作线程模块
    print("\n3. 测试工作线程模块...")
    from gui.workers import BaseWorker
    from gui.workers.base_worker import (
        GeometryWorker,
        MeshWorker,
        AIWorker,
        ChatWorker,
    )
    print(f"   ✓ BaseWorker: {BaseWorker}")
    print(f"   ✓ GeometryWorker: {GeometryWorker}")
    print(f"   ✓ MeshWorker: {MeshWorker}")
    print(f"   ✓ AIWorker: {AIWorker}")
    print(f"   ✓ ChatWorker: {ChatWorker}")
    
    # 测试主窗口（不显示，只测试导入）
    print("\n4. 测试主窗口模块...")
    from gui.main_window import MainWindow, create_main_window
    print(f"   ✓ MainWindow: {MainWindow}")
    print(f"   ✓ create_main_window: {create_main_window}")
    
    # 测试GUI包
    print("\n5. 测试 GUI 包...")
    from gui import __version__, MainWindow, CAETheme
    print(f"   ✓ __version__: {__version__}")
    print(f"   ✓ MainWindow: {MainWindow}")
    print(f"   ✓ CAETheme: {CAETheme}")
    
    # 测试主入口
    print("\n6. 测试主入口模块...")
    import main_gui
    print(f"   ✓ main_gui: {main_gui}")
    
    print("\n" + "=" * 60)
    print("所有导入测试通过！✓")
    print("=" * 60)
    
    print("\n注意：GUI 需要 PySide6 支持")
    print("如需运行完整 GUI，请确保已安装 PySide6")
    print("安装命令: pip install PySide6")


if __name__ == "__main__":
    test_imports()
