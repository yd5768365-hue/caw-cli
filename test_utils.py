#!/usr/bin/env python3
"""
测试 utils 模块中的工具类
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))


def test_encoding_helper():
    """测试编码助手"""
    print("=== 测试编码助手 ===")
    try:
        from src.sw_helper.utils.encoding_helper import get_encoding_helper

        helper = get_encoding_helper()
        helper.print("编码测试成功")
        info = helper.get_encoding_info()
        print(info)
        print("[OK] 编码助手测试成功")
    except Exception as e:
        print(f"[ERROR] 编码助手测试失败: {e}")
        import traceback

        print(traceback.format_exc())
    print()


def test_dependency_checker():
    """测试依赖检查器"""
    print("=== 测试依赖检查器 ===")
    try:
        from src.sw_helper.utils.dependency_checker import create_dependency_checker

        checker = create_dependency_checker()
        checker.check_all_dependencies()
        checker.print_report()
        print("[OK] 依赖检查器测试成功")
    except Exception as e:
        print(f"[ERROR] 依赖检查器测试失败: {e}")
        import traceback

        print(traceback.format_exc())
    print()


def test_error_handler():
    """测试错误处理器"""
    print("=== 测试错误处理器 ===")
    try:
        from src.sw_helper.utils.error_handler import create_error_handler

        handler = create_error_handler(debug=True)
        raise ValueError("测试错误")
    except Exception as e:
        handler.handle_exception(e)
        print("[OK] 错误处理器测试成功")
    print()


def main():
    """测试入口"""
    try:
        test_encoding_helper()
        test_dependency_checker()
        test_error_handler()
    except KeyboardInterrupt:
        print("\n[ERROR] 测试被中断")
        sys.exit(1)


if __name__ == "__main__":
    main()