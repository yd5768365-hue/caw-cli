#!/usr/bin/env python3
"""
Windows 控制台 Unicode 显示测试脚本

此脚本用于测试和验证 encoding_helper.py 中的 Unicode 字符降级功能，
特别是在 Windows GBK 控制台环境下的兼容性。
"""

import sys
from pathlib import Path
import subprocess

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.sw_helper.utils.encoding_helper import (
    get_encoding_helper,
    should_use_ascii_fallback,
    ascii_fallback,
    load_unicode_fallback,
    update_unicode_fallback,
)


def test_basic_functionality():
    """测试基本功能"""
    helper = get_encoding_helper()
    helper.print("=== 基本功能测试 ===")

    # 打印系统信息
    info = helper.get_encoding_info()
    for key, value in info.items():
        helper.print(f"{key}: {value}")

    # 测试 Unicode 支持
    helper.print("\n=== Unicode 支持测试 ===")
    test_chars = "✅❌⚠️🔧📊✅❌⚠️🔧📊"
    support = helper.test_unicode_support(test_chars)
    for char, supported in support.items():
        status = "[OK] 支持" if supported else "[ERROR] 不支持"
        helper.print(f"  {char}: {status}")

    # 测试是否应该使用回退方案
    helper.print(f"\n是否需要使用 ASCII 回退: {should_use_ascii_fallback()}")


def test_fallback_replacement():
    """测试字符替换功能"""
    helper = get_encoding_helper()
    helper.print("\n=== 字符替换测试 ===")

    # 测试包含 Unicode 字符的文本
    test_texts = [
        "操作成功 ✅",
        "操作失败 ❌",
        "警告信息 ⚠️",
        "正在修复 🔧",
        "数据分析 📊",
        "等待中 ⏳",
        "价格上涨 📈",
        "价格下跌 📉",
        "信息说明 ℹ️",
        "热门项目 🔥",
        "项目完成 🎉",
        "快速前进 🚀",
        "软件包 📦",
        "笔记 📝",
        "搜索 🔍",
        "星标 ⭐",
        "想法 💡",
        "问题 ❓",
        "警告 ❗",
        "绿色 💚",
        "红色 ❤️",
        "黄色 💛",
        "蓝色 💙",
        "紫色 💜",
    ]

    for original in test_texts:
        fallback = helper.format_text(original)
        helper.print(f"  原文本: {original}")
        helper.print(f"  替换后: {fallback}")
        helper.print("")

    # 测试重复字符替换
    repeated_text = "✅✅✅ 三个成功操作"
    fallback_text = helper.format_text(repeated_text)
    helper.print("  重复字符测试:")
    helper.print(f"    原文本: {repeated_text}")
    helper.print(f"    替换后: {fallback_text}")


def test_load_and_update_config():
    """测试配置加载和更新功能"""
    helper = get_encoding_helper()
    helper.print("\n=== 配置管理测试 ===")

    # 测试加载配置
    fallback_config = load_unicode_fallback()
    helper.print(f"字符映射配置大小: {len(fallback_config)} 个")

    # 测试更新配置
    test_key = "🎯"
    test_value = "[TARGET]"
    update_unicode_fallback({test_key: test_value})

    # 测试是否能正确替换
    test_text = f"目标达成 {test_key}"
    fallback_text = helper.format_text(test_text)
    helper.print("新增字符替换测试:")
    helper.print(f"  原文本: {test_text}")
    helper.print(f"  替换后: {fallback_text}")

    # 验证替换是否正确
    if test_value in fallback_text:
        helper.print("[OK] 新增字符替换成功")
    else:
        helper.print("[ERROR] 新增字符替换失败")


def test_safe_printing():
    """测试安全打印功能"""
    helper = get_encoding_helper()
    helper.print("\n=== 安全打印测试 ===")

    try:
        helper.print("安全打印测试 ✅")
        helper.print("这是一个包含多个特殊字符的测试: 🔧📊⚠️✅❌")
        helper.print("[OK] 安全打印功能正常")
    except Exception as e:
        helper.print(f"[ERROR] 安全打印功能测试失败: {e}")


def test_console_encoding():
    """测试控制台编码"""
    helper = get_encoding_helper()
    helper.print("\n=== 控制台编码测试 ===")
    helper.print(f"系统编码: {sys.getdefaultencoding()}")
    helper.print(f"标准输出编码: {sys.stdout.encoding}")
    helper.print(f"标准错误编码: {sys.stderr.encoding}")


def test_integration():
    """综合测试"""
    helper = get_encoding_helper()
    helper.print("\n=== 综合功能测试 ===")

    # 测试 CLI 命令
    helper.print("\n=== CLI 命令测试 ===")
    test_commands = [
        "cae-cli --help",
        "cae-cli version",
        "cae-cli info",
    ]

    for cmd in test_commands:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True,
                timeout=10
            )

            if result.returncode == 0:
                helper.print(f"[OK] 命令成功: {cmd}")
                if result.stdout:
                    stdout_text = result.stdout.strip()
                    if stdout_text:
                        helper.print(f"  输出预览: {repr(stdout_text[:50])}")
            else:
                helper.print(f"[ERROR] 命令失败: {cmd}")
                if result.stderr:
                    stderr_text = result.stderr.strip()
                    if stderr_text:
                        helper.print(f"  错误信息: {stderr_text}")

        except Exception as e:
            helper.print(f"[ERROR] 命令执行失败: {cmd} - {e}")


def test_file_operations():
    """测试文件操作功能"""
    helper = get_encoding_helper()
    helper.print("\n=== 文件操作测试 ===")

    # 测试配置文件是否存在
    from src.sw_helper.utils.encoding_helper import UNICODE_FALLBACK_CONFIG

    if UNICODE_FALLBACK_CONFIG.exists():
        helper.print(f"[OK] 配置文件存在: {UNICODE_FALLBACK_CONFIG}")
        file_size = UNICODE_FALLBACK_CONFIG.stat().st_size
        helper.print(f"  文件大小: {file_size} 字节")
    else:
        helper.print(f"[ERROR] 配置文件不存在: {UNICODE_FALLBACK_CONFIG}")

    # 测试配置文件内容
    try:
        with open(UNICODE_FALLBACK_CONFIG, "r", encoding="utf-8") as f:
            content = f.read()
            helper.print("[OK] 配置文件内容读取成功")
            helper.print(f"  内容长度: {len(content)} 字符")
            helper.print(f"  包含的字符数: {len(load_unicode_fallback())}")
    except Exception as e:
        helper.print(f"[ERROR] 配置文件读取失败: {e}")


def main():
    """主测试函数"""
    helper = get_encoding_helper()
    helper.print("Windows 控制台 Unicode 显示测试")
    helper.print("=" * 60)

    try:
        test_basic_functionality()
        test_console_encoding()
        test_fallback_replacement()
        test_safe_printing()
        test_load_and_update_config()
        test_file_operations()
        test_integration()

        helper.print("\n" + "=" * 60)
        helper.print("[OK] 所有测试完成！")
        helper.print("")

        # 总结
        info = helper.get_encoding_info()
        if info["using_ascii_fallback"]:
            helper.print("ℹ️ 当前使用 ASCII 回退模式，Unicode 字符将被替换为 ASCII 等效字符")
        else:
            helper.print("ℹ️ 当前使用正常模式，Unicode 字符将正常显示")

    except Exception as e:
        helper.print(f"\n[ERROR] 测试过程中出现错误: {e}")
        import traceback
        helper.print(f"\n错误详情:\n{traceback.format_exc()}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)