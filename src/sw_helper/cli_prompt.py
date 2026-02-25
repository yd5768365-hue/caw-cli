#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提示词管理CLI命令
"""

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from sw_helper.ai.prompt_manager import PromptManager, list_prompts


console = Console()


@click.group()
def prompt():
    """提示词管理命令"""
    pass


@prompt.command("list")
@click.option("--category", "-c", help="分类筛选")
def list_prompts_cmd(category):
    """列出所有提示词"""
    prompts = list_prompts()

    console.print("\n[bold cyan]📚 CAE-CLI 提示词列表[/bold cyan]\n")

    if category:
        if category in prompts:
            console.print(f"[bold]{category}[/bold]\n")
            for p in prompts[category]:
                console.print(f"  - {p}")
        else:
            console.print(f"[red]分类不存在: {category}[/red]")
        return

    for cat, items in prompts.items():
        console.print(f"[bold]{cat}:[/bold]")
        for item in items:
            console.print(f"  - {item}")
        console.print()


@prompt.command("show")
@click.argument("prompt_path")
def show_prompt(prompt_path):
    """显示提示词内容

    格式: category/name

    示例:
      prompt show system/main
      prompt show learning/3-2-1-method
    """
    if "/" not in prompt_path:
        console.print("[red]格式错误，请使用 category/name 格式[/red]")
        return

    category, name = prompt_path.split("/", 1)
    content = PromptManager.get_prompt(category, name)

    console.print(f"\n[bold cyan]📄 {prompt_path}[/bold cyan]\n")
    console.print(content)
    console.print()


@prompt.command("modes")
def show_modes():
    """显示可用的AI模式"""
    console.print("\n[bold cyan]🎯 可用的AI模式[/bold cyan]\n")

    modes = {
        "default": "默认模式 - 综合助手",
        "learning": "学习模式 - 3-2-1方法 + 费曼学习法",
        "lifestyle": "生活态度 - 行动优先、长期主义",
        "mechanical": "机械设计 - 专注机械设计领域",
    }

    for mode, desc in modes.items():
        console.print(f"  [cyan]{mode}[/cyan]  - {desc}")

    console.print()


@prompt.command("build")
@click.option("--mode", "-m", default="default", help="模式选择")
def build_prompt_cmd(mode):
    """构建指定模式的系统提示词"""
    content = PromptManager.build_system_prompt(mode)

    console.print(f"\n[bold cyan]📝 {mode} 模式提示词[/bold cyan]")
    console.print(f"长度: {len(content)} 字符\n")
    console.print(content[:500] + "..." if len(content) > 500 else content)


if __name__ == "__main__":
    prompt()
