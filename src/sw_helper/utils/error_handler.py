#!/usr/bin/env python3
"""
全局错误处理方案 - 提供友好的错误信息

此模块提供：
- 统一的异常捕获和处理
- 友好的中文错误信息
- 调试模式支持
- 简单的控制台日志记录
"""

import sys
import traceback
from typing import Any, Callable, Optional

from rich.console import Console
from rich.prompt import Confirm
from rich.style import Style

# 导入编码助手
from .encoding_helper import get_encoding_helper


class ErrorHandler:
    """全局错误处理器"""

    def __init__(self, console: Optional[Console] = None, debug: bool = False):
        self.console = console or Console()
        self.debug = debug
        self.encoding_helper = get_encoding_helper()

    def _get_error_color(self, error_type: str) -> Style:
        """根据错误类型返回颜色样式"""
        colors = {
            "CRITICAL": "bold red",
            "ERROR": "red",
            "WARNING": "yellow",
            "INFO": "blue",
            "DEBUG": "cyan",
        }
        return colors.get(error_type.upper(), "white")

    def log(self, message: str, level: str = "INFO") -> None:
        """记录日志信息

        Args:
            message: 日志消息
            level: 日志级别
        """
        color = self._get_error_color(level)
        formatted_message = self.encoding_helper.format_text(f"[{level}] {message}")
        self.console.print(formatted_message, style=color)

    def handle_exception(self, e: Exception) -> None:
        """处理异常

        Args:
            e: 异常对象
        """
        error_name = type(e).__name__
        error_msg = str(e)

        self.console.print("\n" + "=" * 80, style="bold red")
        formatted_line = self.encoding_helper.format_text(f"❌ 程序错误: {error_name}")
        self.console.print(formatted_line, style="bold red")
        self.console.print(f"  错误信息: {error_msg}", style="red")

        if self.debug:
            self.console.print("\n" + "-" * 80, style="bold yellow")
            formatted_line = self.encoding_helper.format_text("📋 详细错误信息:")
            self.console.print(formatted_line)
            self.console.print(f"  异常类型: {type(e).__name__}")
            self.console.print(f"  错误信息: {e}")

            self.console.print("\n" + "-" * 80, style="bold yellow")
            formatted_line = self.encoding_helper.format_text("📚 错误堆栈:")
            self.console.print(formatted_line)
            tb = traceback.format_exc()
            self.console.print(f"```\n{tb}```", style="red")

        else:
            self.console.print("\n" + "-" * 80, style="bold yellow")
            formatted_line = self.encoding_helper.format_text("💡 提示: 运行程序时添加 --debug 选项查看详细错误信息")
            self.console.print(formatted_line, style="yellow")
            formatted_line = self.encoding_helper.format_text("💡 示例: cae-cli --debug [命令]")
            self.console.print(formatted_line, style="yellow")

        self.console.print("\n" + "=" * 80, style="bold red")

    def handle_keyboard_interrupt(self) -> None:
        """处理用户中断"""
        formatted_line = self.encoding_helper.format_text("\n\n[yellow]⚠️ 用户中断操作[/yellow]")
        self.console.print(formatted_line, style="bold")

    def handle_unknown_error(self, e: Any) -> None:
        """处理未知错误类型

        Args:
            e: 错误对象
        """
        self.console.print("\n" + "=" * 80, style="bold red")
        formatted_line = self.encoding_helper.format_text("❌ 未知错误")
        self.console.print(formatted_line, style="bold red")
        self.console.print(f"  错误对象: {e}", style="red")
        self.console.print(f"  类型: {type(e)}", style="red")

        if self.debug:
            self.console.print("\n" + "-" * 80, style="bold yellow")
            formatted_line = self.encoding_helper.format_text("📚 错误堆栈:")
            self.console.print(formatted_line)
            tb = traceback.format_exc()
            self.console.print(f"```\n{tb}```", style="red")

        self.console.print("\n" + "=" * 80, style="bold red")

    def prompt_continue(self, message: str = "是否继续执行其他操作?") -> bool:
        """提示用户是否继续

        Args:
            message: 提示信息

        Returns:
            bool: 用户选择结果
        """
        return Confirm.ask(f"[yellow]{message}[/yellow]")


def create_error_handler(console: Optional[Console] = None, debug: bool = False) -> ErrorHandler:
    """创建错误处理器实例

    Args:
        console: Rich Console 实例
        debug: 是否启用调试模式

    Returns:
        ErrorHandler: 错误处理器实例
    """
    return ErrorHandler(console, debug)


def handle_error(func: Callable) -> Callable:
    """装饰器：统一处理函数异常"""

    def wrapper(*args, **kwargs):
        error_handler = create_error_handler()
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            error_handler.handle_keyboard_interrupt()
            return False
        except Exception as e:
            error_handler.handle_exception(e)
            return False
        except:
            error_handler.handle_unknown_error(sys.exc_info()[1])
            return False

    return wrapper


def main() -> None:
    """测试错误处理功能"""
    console = Console()
    error_handler = create_error_handler(console, debug=True)

    # 测试不同类型的错误
    console.print("测试错误处理功能...", style="bold blue")

    try:
        # 测试异常处理
        console.print("\n1. 测试除法错误...")
        1 / 0
    except Exception as e:
        error_handler.handle_exception(e)

    try:
        # 测试未知错误
        console.print("\n2. 测试未知错误...")
        raise "这不是一个异常对象"
    except Exception as e:
        error_handler.handle_unknown_error(e)

    try:
        # 测试调试信息
        console.print("\n3. 测试调试信息...")
        raise ValueError("调试信息测试")
    except Exception as e:
        error_handler.handle_exception(e)


if __name__ == "__main__":
    main()