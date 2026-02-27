#!/usr/bin/env python3
"""
首次运行检查模块 - 验证依赖并提示用户安装必要组件
"""

from pathlib import Path
from typing import Dict, List, Tuple

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

# 项目颜色定义
MAIN_RED = "#8B0000"
HIGHLIGHT_RED = "#FF4500"


def check_dependency(module_name: str, display_name: str = None) -> Tuple[bool, str]:
    """
    检查Python模块是否可用

    Args:
        module_name: 模块名
        display_name: 显示名称（可选）

    Returns:
        (是否可用, 错误信息)
    """
    if display_name is None:
        display_name = module_name

    try:
        __import__(module_name)
        return True, ""
    except ImportError as e:
        return False, f"{display_name}: {e}"
    except Exception as e:
        return False, f"{display_name}: 未知错误 - {e}"


def check_sentence_transformers() -> Tuple[bool, str]:
    """检查sentence-transformers"""
    try:
        from sentence_transformers import SentenceTransformer

        # 只检查导入，不实际加载模型
        return True, "sentence-transformers可用"
    except ImportError as e:
        return False, f"sentence-transformers未安装: {e}"
    except Exception as e:
        return False, f"sentence-transformers错误: {e}"


def check_ollama_service() -> Tuple[bool, str]:
    """检查Ollama服务是否运行"""
    try:
        import asyncio

        import aiohttp

        async def check():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:11434/api/tags", timeout=5) as resp:
                        return resp.status == 200
            except (aiohttp.ClientError, asyncio.TimeoutError):
                return False
            except Exception:
                return False

        # 同步环境中运行异步检查
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(check())
            loop.close()

            if result:
                return True, "Ollama服务正在运行"
            else:
                return False, "Ollama服务未运行（请启动Ollama或安装）"
        except Exception:
            return False, "无法检查Ollama服务"

    except ImportError:
        return False, "aiohttp未安装，无法检查Ollama"


def check_chromadb() -> Tuple[bool, str]:
    """检查ChromaDB"""
    return check_dependency("chromadb", "ChromaDB")


def is_first_run() -> bool:
    """检查是否是首次运行"""
    marker_file = Path.home() / ".cae-cli" / "first_run_checked"
    return not marker_file.exists()


def mark_first_run_done():
    """标记首次运行检查已完成"""
    marker_dir = Path.home() / ".cae-cli"
    marker_dir.mkdir(exist_ok=True)

    marker_file = marker_dir / "first_run_checked"
    marker_file.touch()


def show_installation_guide(missing_deps: List[str]):
    """显示安装指南"""
    guide_text = f"""
# CAE-CLI AI功能依赖安装指南

## 缺少的依赖
检测到以下依赖未安装或不可用：
{chr(10).join(f'- {dep}' for dep in missing_deps)}

## 安装步骤

### 1. 基础AI依赖
```bash
# 安装知识库检索所需组件
pip install sentence-transformers==2.2.0
pip install chromadb==0.4.0
```

### 2. Ollama（可选，推荐用于辅助学习）
1. 下载并安装 Ollama: https://ollama.com/
2. 启动Ollama服务
3. 下载模型（二选一）：
   ```bash
   ollama pull qwen2.5:1.5b    # 推荐，性能较好
   ollama pull phi3:mini       # 轻量级替代
   ```

### 3. 首次使用
- 知识库检索：首次使用时会自动下载sentence-transformers模型（约80MB）
- 辅助学习：需要Ollama服务运行

### 4. 基础功能（无需AI）
以下功能无需AI依赖：
- [OK] 几何文件解析
- [OK] 网格质量分析
- [OK] 材料数据库查询
- [OK] 报告生成
- [OK] 参数优化

## 验证安装
安装完成后，重启CAE-CLI，系统会自动检测依赖状态。

**注意**：AI功能是可选的，您可以在没有AI组件的情况下使用基础功能。
"""

    console.print("\n")
    console.print(
        Panel(
            Markdown(guide_text),
            title="[bright_red]安装指南[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
    )


def perform_first_run_check(show_guide: bool = True) -> Dict[str, bool]:
    """
    执行首次运行检查

    Args:
        show_guide: 是否显示安装指南

    Returns:
        依赖检查结果字典
    """
    console.print(f"\n[{HIGHLIGHT_RED}]首次运行检查...[/{HIGHLIGHT_RED}]")

    results = {}
    missing_deps = []

    # 基础依赖（必须）
    console.print("[dim]检查基础依赖...[/dim]")
    base_deps = [
        ("click", "Click"),
        ("rich", "Rich"),
        ("yaml", "PyYAML"),
        ("numpy", "NumPy"),
        ("jinja2", "Jinja2"),
    ]

    for module_name, display_name in base_deps:
        ok, msg = check_dependency(module_name, display_name)
        results[f"base_{module_name}"] = ok
        if ok:
            console.print(f"  [green][OK] {display_name}[/green]")
        else:
            console.print(f"  [red][FAIL] {display_name}[/red]")
            missing_deps.append(f"{display_name} ({msg})")

    # AI依赖（可选但重要）
    console.print("\n[dim]检查AI依赖...[/dim]")

    # sentence-transformers
    st_ok, st_msg = check_sentence_transformers()
    results["ai_sentence_transformers"] = st_ok
    if st_ok:
        console.print("  [green][OK] sentence-transformers[/green]")
    else:
        console.print(f"  [yellow][WARN] sentence-transformers[/yellow]: [dim]{st_msg}[/dim]")
        missing_deps.append("sentence-transformers")

    # ChromaDB
    chroma_ok, chroma_msg = check_chromadb()
    results["ai_chromadb"] = chroma_ok
    if chroma_ok:
        console.print("  [green][OK] ChromaDB[/green]")
    else:
        console.print(f"  [yellow][WARN] ChromaDB[/yellow]: [dim]{chroma_msg}[/dim]")
        missing_deps.append("ChromaDB")

    # Ollama
    ollama_ok, ollama_msg = check_ollama_service()
    results["ai_ollama"] = ollama_ok
    if ollama_ok:
        console.print("  [green][OK] Ollama服务[/green]")
    else:
        console.print(f"  [yellow][WARN] Ollama服务[/yellow]: [dim]{ollama_msg}[/dim]")
        if "未安装" in ollama_msg or "未运行" in ollama_msg:
            missing_deps.append("Ollama（可选）")

    # 总结
    console.print(f"\n[{HIGHLIGHT_RED}]检查完成！[/{HIGHLIGHT_RED}]")

    base_ok = all(results.get(f"base_{dep[0]}", False) for dep in base_deps)
    ai_ok = results.get("ai_sentence_transformers", False) and results.get("ai_chromadb", False)

    if base_ok:
        if ai_ok and results.get("ai_ollama", False):
            console.print("[green][OK] 所有依赖就绪，完整功能可用！[/green]")
        elif ai_ok:
            console.print("[green][OK] 基础AI功能可用，辅助学习功能受限[/green]")
            console.print("[dim]（Ollama服务未运行，辅助学习模式将使用知识库检索）[/dim]")
        else:
            console.print("[yellow][WARN] 基础功能可用，AI功能需要额外安装[/yellow]")
            if show_guide and missing_deps:
                show_installation_guide(missing_deps)
    else:
        console.print("[red][FAIL] 缺少必要基础依赖，部分功能不可用[/red]")
        if show_guide and missing_deps:
            show_installation_guide(missing_deps)

    # 标记检查完成
    mark_first_run_done()

    return results


def quick_check() -> bool:
    """
    快速检查 - 只检查基础依赖

    Returns:
        基础依赖是否就绪
    """
    base_deps = ["click", "rich", "yaml", "numpy", "jinja2"]

    for module_name in base_deps:
        ok, _ = check_dependency(module_name)
        if not ok:
            return False

    return True


if __name__ == "__main__":
    # 命令行测试
    print("运行首次检查...")
    results = perform_first_run_check()

    print("\n检查结果:")
    for key, value in results.items():
        print(f"  {key}: {'✅' if value else '❌'}")
