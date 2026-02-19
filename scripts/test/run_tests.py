#!/usr/bin/env python3
"""
CAE-CLI 测试运行器 - 自动生成 HTML 测试报告

运行项目的所有测试，并生成美观的 HTML 测试报告。
报告将包含测试结果、代码覆盖率和详细的测试日志。
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入编码助手
try:
    from src.sw_helper.utils.encoding_helper import get_encoding_helper, configure_console
    encoding_helper = get_encoding_helper()
    console = configure_console()
    has_encoding_helper = True
except ImportError:
    has_encoding_helper = False


# 项目根目录
PROJECT_ROOT = Path(__file__).parent


def run_tests():
    """运行所有测试并生成 HTML 报告"""
    if has_encoding_helper:
        encoding_helper.print("=" * 60)
        encoding_helper.print("CAE-CLI 测试运行器")
        encoding_helper.print("=" * 60)
    else:
        print("=" * 60)
        print("CAE-CLI 测试运行器")
        print("=" * 60)

    # 检查是否已安装依赖
    if has_encoding_helper:
        encoding_helper.print("\n检查测试依赖...")
    else:
        print("\n检查测试依赖...")

    try:
        import pytest
        import pytest_html
        import pytest_cov
        if has_encoding_helper:
            encoding_helper.print("✅ 测试依赖已安装")
        else:
            print("测试依赖已安装")
    except ImportError as e:
        if has_encoding_helper:
            encoding_helper.print(f"❌ 测试依赖未安装: {e}")
            encoding_helper.print("请运行以下命令安装依赖:")
            encoding_helper.print("  pip install -e \"[dev]\"")
        else:
            print(f"测试依赖未安装: {e}")
            print("请运行以下命令安装依赖:")
            print("  pip install -e \"[dev]\"")
        sys.exit(1)

    # 创建报告目录（如果不存在）
    report_dir = PROJECT_ROOT / "tests/reports"
    report_dir.mkdir(exist_ok=True)

    if has_encoding_helper:
        encoding_helper.print(f"\n测试报告将保存到: {report_dir}")
    else:
        print(f"\n测试报告将保存到: {report_dir}")

    # 运行 pytest 命令
    if has_encoding_helper:
        encoding_helper.print("\n开始运行测试...")
    else:
        print("\n开始运行测试...")
    pytest_command = [
        sys.executable,
        "-m", "pytest",
        "-v",
        "--tb=short",
        "--html=tests/reports/test_report.html",
        "--css=tests/assets/report.css",
        "--cov=src/sw_helper",
        "--cov-report=html:tests/reports/coverage",
        "--cov-report=term-missing"
    ]

    try:
        result = subprocess.run(
            pytest_command,
            check=False,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 打印测试输出
        if has_encoding_helper:
            encoding_helper.print("\n" + "=" * 60)
            encoding_helper.print("测试输出")
            encoding_helper.print("=" * 60)
            encoding_helper.print(result.stdout)

            if result.stderr:
                encoding_helper.print("\n" + "=" * 60)
                encoding_helper.print("错误信息")
                encoding_helper.print("=" * 60)
                encoding_helper.print(result.stderr)

            # 检查测试是否通过
            if result.returncode == 0:
                encoding_helper.print("\n✅ 所有测试通过！")
            else:
                encoding_helper.print(f"\n❌ 测试失败，退出码: {result.returncode}")

            # 显示测试统计信息
            encoding_helper.print("\n" + "=" * 60)
            encoding_helper.print("测试报告生成完成")
            encoding_helper.print("=" * 60)
            encoding_helper.print(f"  测试报告: {report_dir / 'test_report.html'}")
            encoding_helper.print(f"  覆盖报告: {report_dir / 'coverage/index.html'}")

            # 自动打开浏览器查看报告
            encoding_helper.print("\n正在打开测试报告...")
        else:
            print("\n" + "=" * 60)
            print("测试输出")
            print("=" * 60)
            print(result.stdout)

            if result.stderr:
                print("\n" + "=" * 60)
                print("错误信息")
                print("=" * 60)
                print(result.stderr)

            # 检查测试是否通过
            if result.returncode == 0:
                print("\n所有测试通过！")
            else:
                print(f"\n测试失败，退出码: {result.returncode}")

            # 显示测试统计信息
            print("\n" + "=" * 60)
            print("测试报告生成完成")
            print("=" * 60)
            print(f"  测试报告: {report_dir / 'test_report.html'}")
            print(f"  覆盖报告: {report_dir / 'coverage/index.html'}")

            # 自动打开浏览器查看报告
            print("\n正在打开测试报告...")

        webbrowser.open(f"file://{report_dir / 'test_report.html'}")

        return result.returncode

    except Exception as e:
        if has_encoding_helper:
            encoding_helper.print(f"\n❌ 测试运行失败: {e}")
            import traceback
            encoding_helper.print(f"\n错误详细信息:\n{traceback.format_exc()}")
        else:
            print(f"\n测试运行失败: {e}")
            import traceback
            print(f"\n错误详细信息:\n{traceback.format_exc()}")
        return 1


def clean_reports():
    """清理旧的测试报告"""
    if has_encoding_helper:
        encoding_helper.print("正在清理旧的测试报告...")
    else:
        print("正在清理旧的测试报告...")

    report_dir = PROJECT_ROOT / "tests/reports"

    if report_dir.exists():
        for item in report_dir.iterdir():
            if item.is_dir():
                import shutil
                shutil.rmtree(item)
            else:
                item.unlink()

        if has_encoding_helper:
            encoding_helper.print("✅ 旧报告已清理")
        else:
            print("旧报告已清理")
    else:
        if has_encoding_helper:
            encoding_helper.print("ℹ️ 报告目录不存在，无需清理")
        else:
            print("报告目录不存在，无需清理")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="CAE-CLI 测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_tests.py          运行所有测试并生成报告
  python run_tests.py --clean  清理旧报告后运行测试
  python run_tests.py --help   显示此帮助信息
        """
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="在运行测试前清理旧的测试报告"
    )

    parser.add_argument(
        "--no-open",
        action="store_true",
        help="运行测试后不自动打开浏览器"
    )

    args = parser.parse_args()

    if args.clean:
        clean_reports()

    # 运行测试
    result_code = run_tests()

    # 检查是否需要自动打开浏览器
    if not args.no_open and result_code == 0:
        # 浏览器已经在 run_tests() 函数中打开了
        pass

    return result_code


if __name__ == "__main__":
    sys.exit(main())