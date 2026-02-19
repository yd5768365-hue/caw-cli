#!/usr/bin/env python3
"""
测试 encoding_helper.format_text 函数是否能正确地替换所有的 Unicode 字符
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from src.sw_helper.utils.encoding_helper import get_encoding_helper

def test_format_text():
    """测试 format_text 函数"""
    encoding_helper = get_encoding_helper()

    encoding_helper.print("测试 encoding_helper.format_text 函数...")
    encoding_helper.print(f"使用回退方案: {encoding_helper.use_ascii_fallback}")
    encoding_helper.print("")

    # 测试字符列表
    test_chars = [
        "✅",  # 成功
        "❌",  # 失败
        "⚠️",  # 警告
        "🔧",  # 工具
        "📊",  # 图表
        "✓",  # 对勾
        "✗",  # 叉号
        "⏳",  # 等待
        "📈",  # 上升
        "📉",  # 下降
        "ℹ️",  # 信息
        "🔥",  # 热门
        "🎉",  # 庆祝
        "🚀",  # 火箭
        "📦",  # 包裹
        "📝",  # 笔记
        "🔍",  # 搜索
        "⭐",  # 星号
        "💡",  # 灯泡
        "❓",  # 问号
        "❗",  # 感叹号
        "💚",  # 绿色
        "❤️",  # 红色
        "💛",  # 黄色
        "💙",  # 蓝色
        "💜",  # 紫色
    ]

    # 测试每个字符
    all_passed = True
    for char in test_chars:
        try:
            formatted = encoding_helper.format_text(char)
            encoding_helper.print(f"  原字符: {repr(char)}")
            encoding_helper.print(f"  格式化后: {repr(formatted)}")

            # 验证格式化后的字符是否符合预期
            if encoding_helper.use_ascii_fallback:
                assert len(char) > 0 and char != formatted, f"{char} 没有被替换"
                assert formatted.startswith("[") and formatted.endswith("]"), \
                    f"{formatted} 不是 ASCII 回退格式"
            else:
                assert formatted == char, f"{char} 不应该被替换"

            # 使用编码助手打印测试结果
            success_msg = encoding_helper.format_text("  ✔️ 测试通过")
            encoding_helper.print(success_msg)
            encoding_helper.print("")
        except Exception as e:
            # 使用编码助手打印错误信息
            error_msg = encoding_helper.format_text(f"  ❌ 测试失败: {e}")
            encoding_helper.print(error_msg)
            encoding_helper.print("")
            all_passed = False

    if all_passed:
        encoding_helper.print("✅ 所有字符格式化测试通过")
    else:
        encoding_helper.print("❌ 有字符格式化测试失败")
        sys.exit(1)

if __name__ == "__main__":
    test_format_text()