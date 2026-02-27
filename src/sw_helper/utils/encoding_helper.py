#!/usr/bin/env python3
"""
编码问题解决方案 - 自动检测和配置系统编码

此模块提供编码问题的根治方案，包括：
- 自动检测系统编码
- 智能 Unicode 字符降级
- 配置 Rich Console 输出
- 设置环境变量
- 提供回退方案

支持平台：
- Windows GBK 环境：使用 ASCII 替代字符
- Windows UTF-8 环境：正常显示 Unicode
- Linux/Mac：正常显示 Unicode
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 字符映射配置文件路径
UNICODE_FALLBACK_CONFIG = PROJECT_ROOT / "utils/unicode_fallback.json"

# 编码映射
ENCODING_MAP = {
    "win32": ["utf-8", "gbk"],
    "linux": ["utf-8"],
    "darwin": ["utf-8"],
}

# 默认编码
DEFAULT_ENCODING = "utf-8"


def load_unicode_fallback() -> Dict[str, str]:
    """加载 Unicode 到 ASCII 字符映射配置

    Returns:
        Dict[str, str]: 字符映射字典
    """
    default_mapping = {
        "✅": "[OK]",
        "❌": "[ERROR]",
        "⚠️": "[WARN]",
        "🔧": "[FIX]",
        "📊": "[DATA]",
        "✓": "[OK]",
        "✗": "[ERROR]",
        "⏳": "[WAIT]",
        "📈": "[UP]",
        "📉": "[DOWN]",
        "ℹ️": "[INFO]",
        "🔥": "[HOT]",
        "🎉": "[OK]",
        "🚀": "[GO]",
        "📦": "[PKG]",
        "📝": "[NOTE]",
        "🔍": "[SEARCH]",
        "⭐": "[STAR]",
        "💡": "[IDEA]",
        "❓": "[QUESTION]",
        "❗": "[WARNING]",
        "💚": "[OK]",
        "❤️": "[ERROR]",
        "💛": "[WARN]",
        "💙": "[INFO]",
        "💜": "[DEBUG]",
    }

    try:
        if UNICODE_FALLBACK_CONFIG.exists():
            with open(UNICODE_FALLBACK_CONFIG, encoding="utf-8") as f:
                custom_mapping = json.load(f)
            default_mapping.update(custom_mapping)
    except Exception as e:
        print(f"加载 Unicode 字符映射失败: {e}")

    return default_mapping


# 字符映射
ASCII_FALLBACK = load_unicode_fallback()


def detect_system_encoding() -> str:
    """自动检测系统编码

    Returns:
        str: 检测到的最佳编码
    """
    platform = sys.platform.lower()
    possible_encodings = ENCODING_MAP.get(platform, [DEFAULT_ENCODING])

    for encoding in possible_encodings:
        try:
            # 测试编码是否有效
            "测试编码".encode(encoding).decode(encoding)
            return encoding
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue

    return DEFAULT_ENCODING


def should_use_ascii_fallback() -> bool:
    """判断是否需要使用 ASCII 回退方案

    Returns:
        bool: 是否需要使用 ASCII 回退
    """
    if sys.platform != "win32":
        return False

    try:
        # 测试控制台是否支持 Unicode
        test_chars = "✅❌⚠️🔧📊"
        for char in test_chars:
            char.encode(sys.stdout.encoding)
        return False
    except UnicodeEncodeError:
        return True


def ascii_fallback(text: str) -> str:
    """将 Unicode 字符替换为 ASCII 等效字符

    Args:
        text: 包含 Unicode 字符的文本

    Returns:
        str: 替换后的 ASCII 文本
    """
    if not should_use_ascii_fallback():
        return text

    result = text
    for unicode_char, ascii_replacement in ASCII_FALLBACK.items():
        result = result.replace(unicode_char, ascii_replacement)
    return result


def configure_console() -> Console:
    """配置 Rich Console 以处理编码问题

    Returns:
        Console: 配置好的控制台实例
    """
    try:
        # 根据平台和编码配置 Rich Console
        if sys.platform == "win32":
            # Windows 特殊配置
            console = Console(
                force_terminal=True,
                legacy_windows=False,
                color_system="auto",
            )
        else:
            # Linux/Mac 配置
            console = Console(
                force_terminal=True,
                color_system="auto",
            )
        return console
    except Exception as e:
        # 回退方案：使用简化的控制台
        print(f"控制台配置失败: {e}")
        return Console(
            force_terminal=False,
            legacy_windows=True,
            color_system=None,
        )


def set_encoding_env() -> None:
    """设置编码相关的环境变量"""
    os.environ["PYTHONIOENCODING"] = DEFAULT_ENCODING

    # Windows 特定设置
    if sys.platform == "win32":
        try:
            # 尝试设置控制台代码页
            import subprocess

            subprocess.run(["chcp", "65001"], shell=True, check=False, capture_output=True)
        except Exception as e:
            print(f"设置控制台代码页失败: {e}")


def safe_print(text: str, console: Optional[Console] = None) -> None:
    """安全打印函数，处理编码问题

    Args:
        text: 要打印的文本
        console: 可选的 Rich Console 实例
    """
    fallback_text = ascii_fallback(text)

    try:
        if console:
            console.print(fallback_text)
        else:
            print(fallback_text)
    except Exception:
        # 终极回退方案：仅打印 ASCII 字符
        try:
            stripped_text = "".join(c for c in fallback_text if ord(c) < 128)
            print(stripped_text)
        except Exception:
            print("输出失败")


class EncodingHelper:
    """编码问题解决方案的高级接口"""

    def __init__(self):
        self.encoding = detect_system_encoding()
        self.use_ascii_fallback = should_use_ascii_fallback()
        self.console = configure_console()
        set_encoding_env()

    def print(self, text: str) -> None:
        """安全打印方法"""
        safe_print(text, self.console)

    def format_text(self, text: str) -> str:
        """格式化文本，根据环境选择是否使用 ASCII 回退

        Args:
            text: 要格式化的文本

        Returns:
            str: 格式化后的文本
        """
        return ascii_fallback(text)

    def get_encoding_info(self) -> Dict[str, Any]:
        """获取编码信息

        Returns:
            Dict[str, Any]: 编码信息字典
        """
        return {
            "platform": sys.platform,
            "detected_encoding": self.encoding,
            "color_system": self.console.color_system,
            "using_ascii_fallback": self.use_ascii_fallback,
            "console_supports_unicode": not self.use_ascii_fallback,
        }

    def test_unicode_support(self, chars: Optional[str] = None) -> Dict[str, bool]:
        """测试控制台的 Unicode 支持情况

        Args:
            chars: 要测试的字符，默认为常用字符

        Returns:
            Dict[str, bool]: 字符支持情况字典
        """
        if chars is None:
            chars = "✅❌⚠️🔧📊"

        results = {}
        for char in chars:
            try:
                char.encode(sys.stdout.encoding)
                results[char] = True
            except UnicodeEncodeError:
                results[char] = False

        return results


# 单例实例
_helper_instance: Optional[EncodingHelper] = None


def get_encoding_helper() -> EncodingHelper:
    """获取编码助手的单例实例

    Returns:
        EncodingHelper: 单例实例
    """
    global _helper_instance
    if _helper_instance is None:
        _helper_instance = EncodingHelper()
    return _helper_instance


def update_unicode_fallback(new_mapping: Dict[str, str]) -> None:
    """更新 Unicode 字符映射配置

    Args:
        new_mapping: 新的字符映射
    """
    global ASCII_FALLBACK
    ASCII_FALLBACK.update(new_mapping)

    try:
        with open(UNICODE_FALLBACK_CONFIG, "w", encoding="utf-8") as f:
            json.dump(ASCII_FALLBACK, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存 Unicode 字符映射失败: {e}")


if __name__ == "__main__":
    # 测试编码助手
    helper = get_encoding_helper()
    helper.print("编码助手测试 ✅")
    helper.print(f"检测到的编码: {helper.encoding}")
    helper.print(f"使用 ASCII 回退: {helper.use_ascii_fallback}")
    helper.print("这是一个包含特殊字符的测试: ⚠️ 🔧 📊")

    # 打印编码信息
    info = helper.get_encoding_info()
    for key, value in info.items():
        helper.print(f"{key}: {value}")

    # 测试 Unicode 支持
    helper.print("\nUnicode 支持测试:")
    support = helper.test_unicode_support()
    for char, supported in support.items():
        status = "✅ 支持" if supported else "❌ 不支持"
        helper.print(f"  {char}: {status}")
