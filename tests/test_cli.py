#!/usr/bin/env python3
"""
CAE-CLI 测试脚本
验证CLI安装和功能
"""

import subprocess
import sys


def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        return False, f"命令未找到: {cmd[0]}"


def test_cli():
    """测试CLI命令"""
    print("=" * 60)
    print("CAE-CLI 安装测试")
    print("=" * 60)

    tests = [
        ("查看版本", ["cae-cli", "--version"]),
        ("查看帮助", ["cae-cli", "--help"]),
        ("查看版本信息", ["cae-cli", "version"]),
        ("查看系统信息", ["cae-cli", "info"]),
        ("列出材料", ["cae-cli", "material", "--list"]),
        ("查询Q235", ["cae-cli", "material", "Q235"]),
        ("查看配置", ["cae-cli", "config", "--list"]),
    ]

    passed = 0
    failed = 0

    for test_name, cmd in tests:
        print(f"\n🧪 测试: {test_name}")
        print(f"   命令: {' '.join(cmd)}")

        success, output = run_command(cmd)

        if success:
            print(f"   ✅ 通过")
            passed += 1
        else:
            print(f"   ❌ 失败")
            print(f"   错误: {output[:200]}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 所有测试通过！CAE-CLI 安装成功。")
        print("\n快速开始:")
        print("  cae-cli material --list")
        print("  cae-cli info")
        print("  cae-cli --help")
    else:
        print(f"\n⚠️  {failed} 个测试失败，请检查安装。")
        sys.exit(1)


if __name__ == "__main__":
    test_cli()
