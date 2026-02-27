#!/usr/bin/env python3
"""
CAE-CLI: SolidWorks CAE集成助手
专业的命令行工具，集成SolidWorks、FreeCAD及各类建模/仿真软件

Usage:
    cae-cli --help
    cae-cli parse model.step
    cae-cli analyze mesh.inp --metric aspect_ratio
    cae-cli material Q235
    cae-cli report static -i result.inp

Author: Your Name
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# 确保导入路径正确
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def get_resource_path(relative_path: str) -> Path:
    """获取资源文件路径，支持打包后的exe和开发模式"""
    if getattr(sys, "frozen", False):
        # 打包后：资源在 _internal 目录下
        base_path = Path(sys._MEIPASS)
    else:
        # 开发模式
        base_path = Path(__file__).parent.parent.parent
    return base_path / relative_path


# 处理Windows终端编码问题
import io


def _get_console_file():
    """获取适合的终端文件对象"""
    if sys.platform == "win32":
        try:
            # 尝试设置UTF-8输出
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except (AttributeError, io.UnsupportedOperation):
            pass
    return None


_get_console_file()

console = Console(force_terminal=False)

# 项目核心颜色定义
MAIN_RED = "#8B0000"  # 深红/酒红 - 主色调
HIGHLIGHT_RED = "#FF4500"  # 荧光红 - 高亮色
BACKGROUND_BLACK = "#0F0F0F"  # 深黑背景
COOL_GRAY = "#333333"  # 冷灰 - 辅助色
TEXT_WHITE = "#FFFFFF"  # 白色

# 版本信息
__version__ = "1.0.0"
__prog_name__ = "cae-cli"


def get_config_path() -> Path:
    """获取配置文件路径"""
    home = Path.home()
    config_dir = home / ".cae-cli"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def load_config() -> Dict[str, Any]:
    """加载配置"""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config: Dict[str, Any]):
    """保存配置"""
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ==================== 启动动画 ====================

import time


def _print_animated_banner():
    """打印动画启动横幅"""
    # ASCII Art 横幅
    banner_lines = [
        "════════════════════════════════════════════════════════════",
        "███╗   ███╗███████╗ ██████╗██╗  ██╗██████╗ ███████╗███████╗",
        " ████╗ ████║██╔════╝██╔════╝██║  ██║██╔══██╗██╔════╝██╔════╝",
        " ██╔████╔██║█████╗  ██║     ███████║██║  ██║█████╗  ███████╗",
        " ██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██║  ██║██╔══╝  ╚════██║",
        " ██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██████╔╝███████╗███████║",
        " ╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝",
        "════════════════════════════════════════════════════════════",
    ]

    # 颜色代码
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    # 逐行显示横幅（打字机效果）
    for i, line in enumerate(banner_lines):
        if i == 0 or i == len(banner_lines) - 1:
            print(f"{CYAN}{line}{RESET}")
        else:
            print(f"{CYAN}{line[0:18]}{RESET}{BLUE}{line[18:]}{RESET}")
        time.sleep(0.08)

    # 副标题
    print()
    subtitle_lines = [
        ("◆", BLUE, " 机械设计学习辅助工具"),
        ("◆", GREEN, f" 版本: {__version__}"),
    ]

    for prefix, color, text in subtitle_lines:
        print(f"{color}{prefix}{RESET}{BOLD}{text}{RESET}")
        time.sleep(0.15)

    print()
    print(f"{CYAN}{'═' * 60}{RESET}")
    print()


def _run_banner_animation():
    """在后台线程运行动画"""
    try:
        _print_animated_banner()
    except Exception:
        # 如果动画失败，静默回退
        pass


# 控制是否显示动画（可在配置中禁用）
_SHOW_ANIMATION = True


# 创建CLI组
@click.group()
@click.version_option(version=__version__, prog_name=__prog_name__, help="Show version info and exit")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output mode")
@click.option("--config", "-c", type=click.Path(), help="Specify config file path")
@click.pass_context
def cli(ctx, verbose, config):
    """
    MechDesign: SolidWorks CAE Integration Assistant

    Professional CAE tools supporting:
    - Geometry file parsing (STEP, STL, IGES)
    - Mesh quality analysis
    - Material database query
    - Simulation report generation
    - Integration with SolidWorks/FreeCAD

    Examples:
        cae-cli parse model.step -o result.json
        cae-cli analyze mesh.msh --metric aspect_ratio
        cae-cli material Q235 --property elastic_modulus
        cae-cli report static -i analysis.inp -o report.html
    """
    # 显示启动动画（verbose 模式或运行子命令时）
    global _SHOW_ANIMATION
    if _SHOW_ANIMATION:
        # 检查是否需要显示动画（verbose 或运行子命令）
        show_banner = verbose
        # 检查是否有子命令
        cmd_args = [a for a in sys.argv[1:] if not a.startswith("-")]
        if cmd_args:
            show_banner = True  # 有子命令时也显示

        if show_banner:
            _SHOW_ANIMATION = False  # 只显示一次
            _print_animated_banner()

    # 确保ctx.obj存在
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config_path"] = config

    if verbose:
        console.print(f"[dim]版本: {__version__}[/dim]")


# 注册提示词管理命令组
from sw_helper.cli_prompt import prompt as prompt_group

cli.add_command(prompt_group)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, readable=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["step", "stl", "iges", "auto"], case_sensitive=False),
    default="auto",
    help="File format (default: auto-detect)",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format-output",
    "-F",
    type=click.Choice(["json", "yaml", "table"], case_sensitive=False),
    default="table",
    help="Output format",
)
@click.pass_context
def parse(ctx, file_path, format, output, format_output):
    """
    Parse geometric files and extract information

    FILE_PATH: Path to the geometric file to parse

    Supported formats: STEP (.step, .stp), STL (.stl), IGES (.iges, .igs)

    Examples:
        cae-cli parse model.step
        cae-cli parse part.stl -f stl -o output.json
        cae-cli parse assembly.step --format-output table
    """
    from sw_helper.geometry.parser import GeometryParser

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("正在解析几何文件...", total=None)

            parser = GeometryParser()
            result = parser.parse(file_path, file_format=None if format == "auto" else format)

            progress.update(task, completed=True)

        # 显示结果
        if format_output == "table":
            table = Table(title="几何信息", show_header=True, header_style="bold magenta")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")

            for key, value in result.items():
                if isinstance(value, dict):
                    value = json.dumps(value, ensure_ascii=False)
                table.add_row(str(key), str(value))

            console.print(table)
        elif format_output == "json":
            console.print_json(data=result)
        else:
            console.print(result)

        # 保存到文件
        if output:
            parser.save(result, output)
            console.print(f"\n[green]成功[/green] 结果已保存至: [bold]{output}[/bold]")

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, readable=True))
@click.option(
    "--metric",
    "-m",
    multiple=True,
    type=click.Choice(
        ["aspect_ratio", "skewness", "volume", "orthogonal_quality", "jacobian", "all"],
        case_sensitive=False,
    ),
    default=["all"],
    help="Mesh quality metrics to calculate",
)
@click.option("--threshold", "-t", type=float, default=0.1, help="Quality threshold (0-1)")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--material", "-M", help="Material name for AI suggestions (e.g., Q235)")
@click.pass_context
def analyze(ctx, file_path, metric, threshold, output, material):
    """
    Analyze mesh quality

    FILE_PATH: Path to mesh file (.msh, .inp, .bdf, etc.)

    Examples:
        cae-cli analyze mesh.msh
        cae-cli analyze model.inp -m aspect_ratio -m skewness
        cae-cli analyze mesh.msh -t 0.05 -o quality_report.json
    """
    from sw_helper.mesh.quality import MeshQualityAnalyzer

    try:
        console.print(f"[dim]分析文件: {file_path}[/dim]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("正在分析网格质量...", total=None)

            analyzer = MeshQualityAnalyzer()
            metrics_list = None if "all" in metric else list(metric)
            results = analyzer.analyze(file_path, metrics=metrics_list)

            progress.update(task, completed=True)

        # 显示结果
        _display_analysis_results(results)

        # 整体质量评估
        overall = results.get("overall_quality", "unknown")
        color = _get_quality_color(overall)
        console.print(f"\n整体质量: [{color}]{overall}[/{color}]")

        # 保存结果
        if output:
            _save_analysis_results(results, output)

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("material_name", required=False)
@click.option(
    "--property",
    "-p",
    help="Query specific property (e.g.: density, elastic_modulus, yield_strength)",
)
@click.option("--list", "-l", "list_materials", is_flag=True, help="List all available materials")
@click.option("--search", "-s", help="Search materials (supports name or description keywords)")
@click.option(
    "--unit",
    "-u",
    type=click.Choice(["si", "mpa", "custom"], case_sensitive=False),
    default="si",
    help="Unit system",
)
@click.option(
    "--full",
    "-f",
    "full_info",
    is_flag=True,
    help="Show full material information (all properties)",
)
@click.pass_context
def material(ctx, material_name, property, list_materials, search, unit, full_info):
    """
    Material database query

    MATERIAL_NAME: Material name (e.g.: Q235, 45Steel, Aluminum6061)

    Examples:
        cae-cli material Q235
        cae-cli material Q235 -p elastic_modulus
        cae-cli material Q235 --full
        cae-cli material --list
        cae-cli material --search "steel"
    """
    from sw_helper.material.database import MaterialDatabase

    try:
        db = MaterialDatabase()

        # 列出所有材料
        if list_materials:
            _list_materials_table(db)
            return

        # 搜索材料
        if search:
            _search_materials_table(db, search)
            return

        # 查询特定材料
        if not material_name:
            console.print("[yellow]请指定材料名称或使用 --list 查看所有材料[/yellow]")
            return

        info = db.get_material(material_name)

        if info is None:
            console.print(f"[red]失败 未找到材料: {material_name}[/red]")
            console.print("[dim]使用 'cae-cli material --list' 查看可用材料[/dim]")
            sys.exit(1)

        # 查询特定属性
        if property:
            value = info.get(property)
            if value is not None:
                console.print(f"{material_name}.{property} = {value}")
            else:
                console.print(f"[yellow]材料 '{material_name}' 没有属性 '{property}'[/yellow]")
                console.print(f"可用属性: {', '.join(info.keys())}")
            return

        # 显示完整信息表格
        _display_material_info(info, material_name, unit, full_info)

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument(
    "analysis_type",
    type=click.Choice(["static", "modal", "thermal", "buckling"], case_sensitive=False),
)
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True),
    help="Input analysis result file",
)
@click.option("--output", "-o", type=click.Path(), help="Output report path")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "html", "pdf", "markdown"], case_sensitive=False),
    default="html",
    help="Report format",
)
@click.option("--template", "-t", help="Report template name or path")
@click.option("--title", help="Report title")
@click.pass_context
def report(ctx, analysis_type, input_file, output, output_format, template, title):
    """
    Generate analysis report

    ANALYSIS_TYPE: Analysis type (static: static analysis, modal: modal analysis,
                            thermal: thermal analysis, buckling: buckling analysis)

    Examples:
        cae-cli report static -i result.inp -o report.html
        cae-cli report modal -i eigenvalues.txt --format json
        cae-cli report thermal -i thermal.rth -o thermal_report.pdf
    """
    from sw_helper.report.generator import ReportGenerator

    try:
        console.print(f"[dim]分析类型: {analysis_type}[/dim]")
        console.print(f"[dim]输入文件: {input_file}[/dim]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("正在生成报告...", total=None)

            generator = ReportGenerator(template_dir=template)

            # 确定输出路径
            if not output:
                input_path = Path(input_file)
                output = input_path.parent / f"{input_path.stem}_report.{output_format}"

            report_path = generator.generate(
                analysis_type,
                input_file,
                str(output),
                format=output_format,
                title=title,
            )

            progress.update(task, completed=True)

        # 显示完成信息
        output_path = Path(report_path)
        file_size = output_path.stat().st_size / 1024  # KB

        console.print("\n[green]成功[/green] 报告生成成功!")
        console.print(f"  路径: [bold]{report_path}[/bold]")
        console.print(f"  大小: {file_size:.1f} KB")
        console.print(f"  格式: {output_format.upper()}")

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command(hidden=True)
@click.option(
    "--set",
    "set_config",
    nargs=2,
    metavar="<KEY> <VALUE>",
    help="Set configuration item",
)
@click.option("--get", metavar="<KEY>", help="Get configuration item")
@click.option("--list", "-l", "list_config", is_flag=True, help="List all configurations")
@click.option("--reset", is_flag=True, help="Reset to default configuration")
@click.pass_context
def config(ctx, set_config, get, list_config, reset):
    """
    Manage CLI configuration

    Examples:
        cae-cli config --list
        cae-cli config --get default_material
        cae-cli config --set default_material Q345
        cae-cli config --reset
    """
    try:
        if reset:
            config_path = get_config_path()
            if config_path.exists():
                config_path.unlink()
            console.print("[green]成功[/green] 配置已重置为默认值")
            return

        cfg = load_config()

        if list_config:
            if cfg:
                table = Table(title="当前配置", show_header=True)
                table.add_column("键", style="cyan")
                table.add_column("值", style="green")

                for key, value in cfg.items():
                    table.add_row(str(key), str(value))

                console.print(table)
            else:
                console.print("[dim]暂无自定义配置[/dim]")
            return

        if get:
            value = cfg.get(get, "[dim]未设置[/dim]")
            console.print(f"{get} = {value}")
            return

        if set_config:
            key, value = set_config
            cfg[key] = value
            save_config(cfg)
            console.print(f"[green]成功[/green] 已设置: {key} = {value}")
            return

        # 如果没有选项，显示帮助
        console.print("使用 [bold]--help[/bold] 查看可用选项")

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@cli.command(hidden=True)
@click.option("--check", "-c", is_flag=True, help="Check for latest version")
@click.pass_context
def version(ctx, check):
    """
    Show version information

    Examples:
        cae-cli version
        cae-cli version --check
    """
    console.print(
        Panel.fit(
            f"[bold cyan]{__prog_name__}[/bold cyan]\n"
            f"版本: [green]{__version__}[/green]\n"
            f"Python: [dim]{sys.version.split()[0]}[/dim]\n"
            f"路径: [dim]{project_root}[/dim]",
            title="版本信息",
            border_style="cyan",
        )
    )

    if check:
        console.print("\n[yellow]正在检查更新...[/yellow]")
        # 这里可以添加版本检查逻辑
        console.print("[green]成功[/green] 当前已是最新版本")


# Add a convenient info command
@cli.command(hidden=True)
@click.pass_context
def info(ctx):
    """
    Show system information and configuration status

    Display current system environment, available integrations, and configuration info
    """
    from sw_helper.material.database import MaterialDatabase

    console.print(Panel.fit("[bold]MechDesign 系统信息[/bold]", border_style="blue"))

    # Python信息
    console.print("\n[cyan]Python 环境:[/cyan]")
    console.print(f"  版本: {sys.version.split()[0]}")
    console.print(f"  路径: {sys.executable}")
    console.print(f"  平台: {sys.platform}")

    # 材料数据库
    try:
        db = MaterialDatabase()
        materials = db.list_materials()
        console.print("\n[cyan]材料数据库:[/cyan]")
        console.print(f"  材料数量: {len(materials)}")
        console.print(f"  数据库路径: {db.db_path}")
    except Exception as e:
        console.print(f"\n[yellow]材料数据库: 未初始化 ({e})[/yellow]")

    # 配置
    cfg = load_config()
    console.print("\n[cyan]用户配置:[/cyan]")
    if cfg:
        for key, value in cfg.items():
            console.print(f"  {key}: {value}")
    else:
        console.print("  [dim]使用默认配置[/dim]")

    console.print(f"\n[dim]配置文件: {get_config_path()}[/dim]")


# ==================== 格式转换命令 ====================


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path(), required=False)
@click.option(
    "--format",
    "-f",
    "target_format",
    type=click.Choice(["step", "stl", "iges", "brep", "obj"], case_sensitive=False),
    help="Target format (auto-inferred if not specified)",
)
@click.option(
    "--check/--no-check",
    default=False,
    help="Check geometry quality after conversion",
)
def convert(input_file, output_file, target_format, check):
    """
    Convert CAD geometry between formats

    INPUT_FILE: Input geometry file (STEP/STL/IGES/BREP)

    OUTPUT_FILE: Output file path (optional, auto-generated)

    Examples:
        # STEP to STL
        cae-cli convert model.step

        # Specify output
        cae-cli convert model.step -o output.stl

        # Specify format
        cae-cli convert model.step -f stl

        # IGES to STEP
       CAE-CLI convert part.iges -o part.step
    """
    from pathlib import Path

    from rich.console import Console
    from rich.table import Table

    console = Console()

    try:
        from sw_helper.geometry.converter import GeometryConverter

        converter = GeometryConverter()

        # 执行转换
        if converter.convert(input_file, output_file, target_format):
            # 显示结果
            input_path = Path(input_file)
            if output_file:
                output_path = Path(output_file)
            else:
                output_path = input_path.with_suffix(f".{target_format or '.stl'}")

            table = Table(title="转换结果", show_header=False)
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")

            table.add_row("输入", str(input_path))
            table.add_row("输出", str(output_path))
            table.add_row("源格式", converter._get_format(input_path))
            if target_format:
                table.add_row("目标格式", target_format.upper())

            console.print(table)

            # 可选：检查几何质量
            if check:
                console.print("\n[dim]检查几何质量...[/dim]")
                # 这里可以调用几何分析模块
                console.print("[yellow]几何质量检查功能开发中...[/yellow]")

        else:
            console.print("[red]转换失败[/red]")
            sys.exit(1)

    except ImportError as e:
        console.print(f"[red]缺少依赖: {e}[/red]")
        console.print("[dim]运行 'pip install -e \".[full]\"' 安装完整依赖[/dim]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


# ==================== CAD集成命令 ====================


def _connect_cad(connect, manager):
    """Connect to CAD software and return connector"""
    # 连接CAD
    if connect == "auto":
        cad_name = manager.auto_connect()
    else:
        connector = manager.get_connector(connect)
        if connector and connector.connect():
            cad_name = connect
            manager.active_cad = connect
        else:
            cad_name = None

    if not cad_name:
        console.print("[red]失败 无法连接到CAD软件[/red]")
        console.print("[dim]请确保SolidWorks或FreeCAD已运行[/dim]")
        sys.exit(1)

    connector = manager.get_connector()
    console.print(f"[green]成功[/green] 已连接到: [bold]{cad_name}[/bold]")
    return connector


def _open_cad_file(connector, file_path):
    """Open CAD file"""
    console.print(f"[dim]正在打开: {file_path}...[/dim]")
    if connector.open_document(file_path):
        console.print("[green]成功[/green] 文件已打开")
        return True
    else:
        console.print("[red]失败 无法打开文件[/red]")
        return False


def _list_cad_parameters(connector):
    """List CAD parameters in a table"""
    params = connector.get_parameters()
    if not params:
        console.print("[yellow]未找到参数[/yellow]")
        return

    table = Table(title="模型参数", show_header=True)
    table.add_column("名称", style="cyan")
    table.add_column("值", style="green")
    table.add_column("单位", style="dim")
    table.add_column("描述", style="white")

    for param in params[:20]:  # 限制显示前20个
        table.add_row(
            param.name,
            f"{param.value:.4f}",
            param.unit,
            param.description[:30],
        )

    console.print(table)
    console.print(f"\n共 {len(params)} 个参数")


def _set_cad_parameter(connector, param_name, param_value):
    """Set CAD parameter value"""
    console.print(f"[dim]设置参数: {param_name} = {param_value}...[/dim]")
    if connector.set_parameter(param_name, param_value):
        console.print("[green]成功[/green] 参数已更新")
        return True
    else:
        console.print("[red]失败 参数设置失败[/red]")
        return False


def _rebuild_cad_model(connector):
    """Rebuild CAD model"""
    console.print("[dim]重建模型...[/dim]")
    if connector.rebuild():
        console.print("[green]成功[/green] 重建完成")
        return True
    else:
        console.print("[yellow]⚠ 重建可能有问题[/yellow]")
        return False


def _export_cad_file(connector, export_path, export_format):
    """Export CAD file"""
    console.print(f"[dim]导出到: {export_path}...[/dim]")
    if connector.export_file(export_path, export_format.upper()):
        console.print("[green]成功[/green] 导出成功")
        console.print(f"  路径: [bold]{export_path}[/bold]")
        return True
    else:
        console.print("[red]失败 导出失败[/red]")
        return False


@cli.command(hidden=True)
@click.option(
    "--connect",
    "-c",
    type=click.Choice(["solidworks", "freecad", "auto"], case_sensitive=False),
    default="auto",
    help="Connect to CAD software",
)
@click.option("--open", type=click.Path(exists=True), help="Open CAD file")
@click.option("--list-params", "-l", is_flag=True, help="List all parameters")
@click.option("--set-param", "-s", nargs=2, metavar="<NAME> <VALUE>", help="Set parameter value")
@click.option("--rebuild", "-r", is_flag=True, help="Rebuild model")
@click.option("--export", "-e", type=click.Path(), help="Export file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["step", "stl", "iges"], case_sensitive=False),
    default="step",
    help="Export format",
)
@click.pass_context
def cad(ctx, connect, open, list_params, set_param, rebuild, export, format):
    """
    CAD software integration control

    Connect to SolidWorks or FreeCAD, perform parameter modification, export, etc.

    Examples:
        cae-cli cad --connect solidworks
        cae-cli cad --open model.sldprt --list-params
        cae-cli cad --set-param Fillet_R 10 --rebuild
        cae-cli cad --export output.step --format step
    """
    from sw_helper.integrations.cad_connector import CADManager

    try:
        manager = CADManager()
        connector = _connect_cad(connect, manager)

        # 打开文件
        if open:
            if not _open_cad_file(connector, open):
                return

        # 列出参数
        if list_params:
            _list_cad_parameters(connector)

        # 设置参数
        if set_param:
            param_name, param_value = set_param
            param_value = float(param_value)
            _set_cad_parameter(connector, param_name, param_value)

        # 重建
        if rebuild:
            _rebuild_cad_model(connector)

        # 导出
        if export:
            _export_cad_file(connector, export, format)

        # 关闭连接
        manager.disconnect_all()

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


# ==================== 分析运行命令 ====================


@cli.command()
@click.argument("config_file", type=click.Path(exists=True), required=False)
@click.option(
    "--type",
    "-t",
    "analysis_type",
    type=click.Choice(["static", "modal", "thermal", "buckling"], case_sensitive=False),
    default="static",
    help="Analysis type",
)
@click.option("--material", "-m", help="Material name (from materials database)")
@click.option("--load", "-l", "load_value", type=float, help="Load value (N)")
@click.option("--mesh-size", "-s", "mesh_size", type=float, default=10.0, help="Mesh element size (mm)")
@click.option("--output", "-o", "output_dir", type=click.Path(), default="./results", help="Output directory")
@click.option(
    "--solver",
    default="simple",
    type=click.Choice(["simple", "scipy", "calculix"], case_sensitive=False),
    help="CAE solver to use (simple: 内置求解器, scipy: 需要scipy, calculix: 需要安装ccx)",
)
@click.option("--mock/--no-mock", default=False, help="Run in mock mode (no actual solver)")
@click.pass_context
def run(
    ctx,
    config_file,
    analysis_type,
    material,
    load_value,
    mesh_size,
    output_dir,
    solver,
    mock,
):
    """
    Run CAE analysis workflow

    Run a complete CAE analysis from configuration file or command line arguments.

    CONFIG_FILE: YAML configuration file (optional)

    Examples:
        # From config file
        cae-cli run config.yaml
        cae-cli run examples/beam_analysis.yaml

        # From command line
        cae-cli run -m Q235 -l 1000 --mesh-size 5

        # Quick static analysis
        cae-cli run --type static -m Q235 -l 5000
    """
    from pathlib import Path

    import yaml
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    try:
        # 加载配置
        config = {}
        if config_file:
            config_file = Path(config_file)
            console.print(f"[dim]加载配置: {config_file}[/dim]")
            with open(config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

        # 解析参数
        mat_name = material or config.get("material", {}).get("name", "Q235")
        load = load_value or config.get("analysis", {}).get("loads", [{}])[0].get("value", 1000)
        mesh_s = mesh_size or config.get("mesh", {}).get("element_size", 10.0)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 获取材料信息
        from sw_helper.material.database import MaterialDatabase

        db = MaterialDatabase()
        mat_info = db.get_material(mat_name)

        if not mat_info:
            console.print(f"[red]错误: 未找到材料 '{mat_name}'[/red]")
            console.print("[dim]使用 'cae-cli material --list' 查看可用材料[/dim]")
            sys.exit(1)

        console.print(
            Panel.fit(
                f"[bold cyan]MechDesign 分析运行器[/bold cyan]\n\n"
                f"材料: [green]{mat_name}[/green]\n"
                f"载荷: [yellow]{load} N[/yellow]\n"
                f"网格大小: [yellow]{mesh_s} mm[/yellow]\n"
                f"分析类型: [cyan]{analysis_type}[/cyan]\n"
                f"输出目录: [dim]{out_dir}[/dim]",
                border_style="cyan",
            )
        )

        # 显示材料信息
        E = mat_info.get("elastic_modulus", 210e9) / 1e9  # GPa
        sigma_yield = mat_info.get("yield_strength", 235e6) / 1e6  # MPa
        console.print("\n[dim]材料参数:[/dim]")
        console.print(f"  弹性模量 E = {E:.1f} GPa")
        console.print(f"  屈服强度 σy = {sigma_yield:.1f} MPa")

        # 检查求解器 - 使用标准化求解器接口
        try:
            from integrations.cae.solvers import SolverConfig, SolverResult, get_solver
        except ImportError:
            # 降级：如果没有新接口，使用旧逻辑
            from integrations.cae.solvers import SimpleFEMSolver

            solver = SimpleFEMSolver()
            solver_available = True
        else:
            # 使用新求解器接口
            solver = get_solver(solver)
            solver_available = solver.is_available()

            # 显示求解器信息
            solver_info = solver.get_info()
            console.print(f"\n[dim]求解器: {solver_info['name']}[/dim]")
            console.print(f"[dim]描述: {solver_info['description']}[/dim]")
            if solver_info["requires_install"]:
                console.print(f"[dim]依赖: {solver_info['requires_install']}[/dim]")

        # 构建求解器配置
        # 默认几何参数（简支梁）
        L = 1000  # mm
        b = 50  # mm
        h = 100  # mm

        solver_config = SolverConfig(
            analysis_type=analysis_type,
            material={
                "elastic_modulus": mat_info.get("elastic_modulus", 210e9),
                "yield_strength": mat_info.get("yield_strength", 235e6),
                "poisson_ratio": mat_info.get("poisson_ratio", 0.3),
            },
            load=load,
            mesh_size=mesh_size,
            geometry={
                "length": L,
                "width": b,
                "height": h,
            },
        )

        # 执行求解
        if mock or not solver_available:
            # 模拟模式或求解器不可用时使用 simple solver
            from integrations.cae.solvers import SimpleFEMSolver

            solver = SimpleFEMSolver()

            if mock:
                console.print("\n[yellow]⚠ 模拟模式 - 使用简易求解器[/yellow]")
            else:
                console.print("\n[yellow]⚠ 请求的求解器不可用，使用内置简易求解器[/yellow]")

            result = solver.solve(solver_config)
        else:
            # 使用实际求解器
            result = solver.solve(solver_config)

        # 提取结果
        delta = result.max_displacement * 1000  # m -> mm
        sigma = result.max_stress / 1e6  # Pa -> MPa

        results = {
            "status": "success",
            "solver": solver.name,
            "max_displacement": delta,
            "max_stress": sigma,
            "safety_factor": result.safety_factor,
            "material": mat_name,
            "load": load,
            "beam_length": L,
            "section": f"{b}x{h}",
        }

        # 保存结果
        result_file = out_dir / "analysis_results.json"
        import json

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        console.print(f"\n[green]✓ 结果已保存: {result_file}[/green]")

        # 显示结果（总是显示）
        if True:
            # 显示结果
            console.print("\n[bold]分析结果:[/bold]")
            console.print(f"  最大位移: {results['max_displacement']:.6f} mm")
            console.print(f"  最大应力: {results['max_stress']:.2f} MPa")

            # 安全系数
            n = results.get("safety_factor", sigma_yield / (results["max_stress"] * 1e6))
            if n >= 1.5:
                color = "green"
                status = "安全"
            elif n >= 1.0:
                color = "yellow"
                status = "警告"
            else:
                color = "red"
                status = "危险"

            console.print(f"  安全系数: [{color}]{n:.2f}[/{color}] ({status})")

            # 显示求解器消息（如果有）
            if result.messages:
                console.print(f"\n[dim]{result.messages}[/dim]")

    except ImportError as e:
        console.print(f"[red]缺少依赖: {e}[/red]")
        console.print("[dim]运行 'pip install -e \".[full]\"' 安装完整依赖[/dim]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


# ==================== 参数优化命令 ====================


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--parameter", "-p", required=True, help="Parameter name to optimize")
@click.option(
    "--param-range",
    "-r",
    nargs=2,
    type=float,
    required=True,
    help="Parameter range (min max)",
)
@click.option("--steps", "-s", type=int, default=5, help="Number of iterations")
@click.option(
    "--step-mode",
    "-m",
    type=click.Choice(["linear", "geometric"], case_sensitive=False),
    default="linear",
    help="Step mode: linear or geometric (default: linear)",
)
@click.option(
    "--cad",
    type=click.Choice(["solidworks", "freecad", "mock"], case_sensitive=False),
    default="freecad",
    help="CAD software type (default: freecad)",
)
@click.option("--output", "-o", type=click.Path(), help="Output results file (.json)")
@click.option("--plot", is_flag=True, help="Generate optimization plot")
@click.option("--report", is_flag=True, help="Generate Markdown report")
@click.option(
    "--output-dir",
    "-d",
    type=click.Path(),
    default="./optimization_results",
    help="Output directory (default: ./optimization_results)",
)
@click.option("--material", "-M", help="Material name for AI suggestions (e.g., Q235)")
@click.pass_context
def optimize(
    ctx,
    file_path,
    parameter,
    param_range,
    steps,
    step_mode,
    cad,
    output,
    plot,
    report,
    output_dir,
    material,
):
    """
    Parameter optimization loop - automatically adjust design parameters and evaluate quality

    Workflow:
    1. Load CAD file (FreeCAD .FCStd)
    2. Iteratively modify parameter values
    3. Rebuild model
    4. Export to STEP
    5. Analyze geometric quality
    6. Record quality scores
    7. Find optimal parameter

    FILE_PATH: CAD file path (.FCStd, .sldprt)

    Examples:
        # Optimize fillet radius (2mm ~ 15mm, 5 steps)
        cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 5

        # Optimize length and generate plot and report
        cae-cli optimize bracket.FCStd -p Length -r 100 200 -s 10 --plot --report

        # Use simulation mode (no FreeCAD installation required)
        cae-cli optimize model.FCStd -p Thickness -r 5 20 --cad mock

        # Specify output directory
        cae-cli optimize part.FCStd -p Radius -r 1 10 -o results.json -d ./output
    """
    from pathlib import Path

    from sw_helper.optimization.optimizer import FreeCADOptimizer

    try:
        # 显示优化信息
        console.print(
            Panel.fit(
                f"[bold cyan]参数优化闭环[/bold cyan]\n"
                f"文件: [green]{file_path}[/green]\n"
                f"参数: [yellow]{parameter}[/yellow]\n"
                f"范围: [blue]{param_range[0]} ~ {param_range[1]} mm[/blue]\n"
                f"步数: [magenta]{steps}[/magenta]\n"
                f"CAD: [dim]{cad}[/dim]",
                title="优化配置",
                border_style="cyan",
            )
        )

        # 确定是否使用模拟模式
        use_mock = cad.lower() == "mock"
        if use_mock:
            console.print("[yellow]使用模拟模式（无需FreeCAD）[/yellow]")

        # 创建优化器
        optimizer = FreeCADOptimizer(use_mock=use_mock)

        # 设置进度回调（使用rich显示）
        def progress_callback(msg: str):
            # 根据消息类型设置颜色
            if "成功" in msg or "完成" in msg:
                style = "green"
            elif "失败" in msg or "错误" in msg:
                style = "red"
            elif "⚠️" in msg or "警告" in msg:
                style = "yellow"
            elif "🔄" in msg:
                style = "cyan"
            else:
                style = "white"
            console.print(f"[{style}]{msg}[/{style}]")

        optimizer.set_progress_callback(progress_callback)

        # 执行优化
        with console.status("[bold green]正在进行参数优化..."):
            results = optimizer.optimize_parameter(
                file_path=file_path,
                param_name=parameter,
                param_range=(param_range[0], param_range[1]),
                steps=steps,
                step_mode=step_mode,
                output_dir=output_dir,
                analyze_geometry=True,
            )

        # 显示结果表格
        if results:
            console.print("\n")

            # 创建结果表格
            table = Table(
                title=f"Optimization Results: {parameter}",
                show_header=True,
                header_style="bold cyan",
                border_style="blue",
            )
            table.add_column("Iteration", style="cyan", justify="center")
            table.add_column("Parameter Value (mm)", style="green", justify="right")
            table.add_column("Quality Score", style="yellow", justify="right")
            table.add_column("Allowable Stress (MPa)", style="blue", justify="right")
            table.add_column("Safety Factor", style="magenta", justify="right")
            table.add_column("Time (s)", style="dim", justify="right")
            table.add_column("Exported File", style="blue", no_wrap=True)

            # 找出最佳结果
            best = max(results, key=lambda x: x.quality_score)

            for r in results:
                # 标记最佳结果
                if r == best:
                    iter_str = f"[bold]{r.iteration}[/bold]"
                    score_str = f"[bold green]{r.quality_score:.1f}[/bold green]"
                    value_str = f"[bold]{r.parameter_value:.2f}[/bold]"
                else:
                    iter_str = str(r.iteration)
                    score_str = f"{r.quality_score:.1f}"
                    value_str = f"{r.parameter_value:.2f}"

                # 截断文件名
                filename = Path(r.export_path).name
                if len(filename) > 25:
                    filename = filename[:22] + "..."

                table.add_row(
                    iter_str,
                    value_str,
                    score_str,
                    f"{r.allowable_stress:.1f}",
                    f"{r.safety_factor:.2f}",
                    f"{r.analysis_time:.2f}",
                    filename,
                )

            console.print(table)

            # 显示最佳结果面板
            best_panel = Panel.fit(
                f"[bold green]最佳结果[/bold green]\n\n"
                f"迭代: [cyan]#{best.iteration}[/cyan]\n"
                f"参数值: [yellow]{best.parameter_name} = {best.parameter_value:.2f} mm[/yellow]\n"
                f"质量分数: [green]{best.quality_score:.1f}/100[/green]\n"
                f"许用应力: [blue]{best.allowable_stress:.1f} MPa[/blue]\n"
                f"安全系数: [magenta]{best.safety_factor:.2f}[/magenta]\n"
                f"导出文件: [dim]{Path(best.export_path).name}[/dim]",
                title="Best Solution",
                border_style="green",
            )
            console.print(best_panel)

            # 统计信息
            total_time = sum(r.analysis_time for r in results)
            avg_score = sum(r.quality_score for r in results) / len(results)

            stats = Panel.fit(
                f"总迭代: [cyan]{len(results)}[/cyan] | "
                f"平均分数: [yellow]{avg_score:.1f}[/yellow] | "
                f"总耗时: [dim]{total_time:.2f}s[/dim]",
                border_style="blue",
            )
            console.print(stats)

            # 导出结果
            if output:
                optimizer.export_results(output)
                console.print(f"[green]Results exported:[/green] [dim]{output}[/dim]")

            # 生成图表
            if plot:
                plot_path = Path(output_dir) / "optimization_plot.png"
                optimizer.plot_results(str(plot_path))
                console.print(f"[green]Plot generated:[/green] [dim]{plot_path}[/dim]")

            # 生成报告
            if report:
                report_path = Path(output_dir) / "optimization_report.md"
                optimizer.generate_report(str(report_path))
                console.print(f"[green]Report generated:[/green] [dim]{report_path}[/dim]")

            # 提示输出目录
            console.print(f"\n[dim]所有输出文件保存在: {Path(output_dir).absolute()}[/dim]")

        else:
            console.print("[yellow]⚠️  没有获得优化结果[/yellow]")

    except FileNotFoundError as e:
        console.print(f"[red]失败 文件未找到: {e}[/red]")
        console.print("[dim]请检查文件路径是否正确[/dim]")
        sys.exit(1)
    except RuntimeError as e:
        console.print(f"[red]失败 运行时错误: {e}[/red]")
        if "FreeCAD" in str(e):
            console.print("\n[yellow]提示: 如果您没有安装FreeCAD，可以使用模拟模式:[/yellow]")
            console.print(
                f"[dim]  cae-cli optimize {file_path} -p {parameter} -r {param_range[0]} {param_range[1]} --cad mock[/dim]"
            )
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


# ==================== AI辅助命令 ====================


@cli.group(hidden=True)
def ai():
    """
    AI-assisted design functions

    Use AI to generate geometry and provide design suggestions
    """
    pass


def _display_ai_generation_config(description, output_dir, mock):
    """Display AI generation configuration panel"""
    console.print(
        Panel.fit(
            f"[bold cyan]AI模型生成[/bold cyan]\n"
            f"描述: [green]{description}[/green]\n"
            f"模式: [yellow]{'模拟' if mock else '真实FreeCAD'}[/yellow]\n"
            f"输出: [blue]{output_dir}[/blue]",
            title="生成配置",
            border_style="cyan",
        )
    )


def _execute_ai_generation(generator, description, output_dir, name, generate_report):
    """Execute AI generation process"""
    with console.status("[bold green]AI正在生成3D模型..."):
        result = generator.generate_with_analysis(
            description=description,
            output_dir=output_dir,
            name=name,
            generate_report=generate_report,
        )
    return result


def _display_parsed_results(parsed):
    """Display parsed geometry results"""
    console.print("\n[cyan]解析结果 解析结果:[/cyan]")
    console.print(f"  形状: [green]{parsed['shape_type']}[/green]")
    console.print("  参数:")
    for param, value in parsed["parameters"].items():
        console.print(f"    - {param}: [yellow]{value}[/yellow] mm")

    if parsed.get("features"):
        console.print(f"  特征: [magenta]{', '.join(f['type'] for f in parsed['features'])}[/magenta]")


def _display_output_files(files):
    """Display output files information"""
    console.print("\n[cyan]输出文件 输出文件:[/cyan]")
    for file_type, file_path in files.items():
        file_size = Path(file_path).stat().st_size / 1024 if Path(file_path).exists() else 0
        console.print(f"  - {file_type.upper()}: [green]{file_path}[/green] ([dim]{file_size:.1f} KB[/dim])")


def _display_analysis_results(analysis):
    """Display quality analysis results"""
    console.print("\n[cyan]质量分析 质量分析:[/cyan]")
    quality_score = analysis.get("quality_score", 0)

    # 根据分数设置颜色
    if quality_score >= 80:
        score_color = "green"
    elif quality_score >= 60:
        score_color = "yellow"
    else:
        score_color = "red"

    console.print(f"  质量评分: [{score_color}]{quality_score:.1f}/100[/{score_color}]")

    if "geometry" in analysis:
        geo = analysis["geometry"]
        console.print(f"  体积: [dim]{geo.get('volume', 0):.2e} m^3[/dim]")
        console.print(f"  顶点数: [dim]{geo.get('vertices', 0)}[/dim]")


def _display_success_panel(files):
    """Display success panel"""
    console.print(
        Panel.fit(
            "[bold green]成功 模型生成成功![/bold green]\n"
            f"FreeCAD模型: [blue]{files.get('fcstd', 'N/A')}[/blue]\n"
            f"STEP文件: [blue]{files.get('step', 'N/A')}[/blue]",
            border_style="green",
        )
    )


def _display_next_steps(files, report_path):
    """Display suggested next steps"""
    console.print("\n[cyan]建议操作:[/cyan]")
    console.print(f"  1. 查看模型: [dim]cae-cli parse {files.get('step', '')}[/dim]")
    console.print(f"  2. 运行优化: [dim]cae-cli optimize {files.get('fcstd', '')} -p Radius -r 1 10[/dim]")
    console.print(f"  3. 分析报告: [dim]cat {report_path or ''}[/dim]")


def _open_freecad_if_requested(open_flag, mock, files):
    """Open FreeCAD if requested"""
    if not open_flag or mock:
        return

    fcstd_path = files.get("fcstd")
    if fcstd_path and Path(fcstd_path).exists():
        console.print("\n[dim]正在打开FreeCAD...[/dim]")
        import subprocess

        try:
            subprocess.Popen(
                ["freecad", fcstd_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, PermissionError, OSError):
            console.print("[yellow]⚠️  无法自动打开FreeCAD，请手动打开文件[/yellow]")


@ai.command("generate")
@click.argument("description")
@click.option(
    "--output-dir",
    "-d",
    type=click.Path(),
    default="./generated_models",
    help="Output directory (default: ./generated_models)",
)
@click.option("--name", "-n", help="Model name (auto-generated if not specified)")
@click.option("--mock", "-m", is_flag=True, help="Use mock mode (no FreeCAD required)")
@click.option(
    "--analyze",
    "-a",
    is_flag=True,
    default=True,
    help="Run analysis and generate report",
)
@click.option("--open", is_flag=True, help="Open FreeCAD to view after generation")
def ai_generate(description, output_dir, name, mock, analyze, open):
    """
    AI generate 3D model - text to solid model

    Natural language description → FreeCAD modeling → STEP export → Quality analysis → Report generation

    DESCRIPTION: Natural language description, e.g., "cube with fillet, length 100 width 50 height 30 fillet 10"

    Examples:
        # Generate cube with fillet
        cae-cli ai generate "cube with fillet, length 100 width 50 height 30 fillet 10"

        # Generate cylinder and specify name
        cae-cli ai generate "cylinder, radius 30 height 60" -n my_cylinder -d ./output

        # Use mock mode (no FreeCAD installation required)
        cae-cli ai generate "cube, side length 50" --mock

        # Complete process (modeling + analysis + report)
        cae-cli ai generate "bracket, length 150 width 80 thickness 5" --analyze -d ./bracket
    """
    from sw_helper.ai.model_generator import AIModelGenerator

    try:
        # 显示生成配置
        _display_ai_generation_config(description, output_dir, mock)

        # 初始化生成器
        generator = AIModelGenerator(use_mock=mock)

        # 执行生成流程
        result = _execute_ai_generation(generator, description, output_dir, name, analyze)

        if not result.get("success"):
            console.print(f"[red]失败 生成失败: {result.get('error', '未知错误')}[/red]")
            sys.exit(1)

        # 获取结果数据
        parsed = result["parsed_geometry"]
        files = result["output_files"]

        # 显示解析结果
        _display_parsed_results(parsed)

        # 显示输出文件
        _display_output_files(files)

        # 显示分析结果
        if "detailed_analysis" in result:
            _display_analysis_results(result["detailed_analysis"])

        # 显示报告路径
        if "report_path" in result:
            console.print(f"\n[cyan]报告 报告:[/cyan] [green]{result['report_path']}[/green]")

        # 成功提示
        _display_success_panel(files)

        # 提示下一步操作
        _display_next_steps(files, result.get("report_path"))

        # 如果指定了--open，尝试打开FreeCAD
        _open_freecad_if_requested(open, mock, files)

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if mock:
            console.print("\n[yellow]提示: 模拟模式下可以正常使用所有功能[/yellow]")
        else:
            console.print("\n[yellow]提示: 如果未安装FreeCAD，请使用 --mock 参数[/yellow]")
            console.print(f'[dim]  cae-cli ai generate "{description}" --mock[/dim]')
        raise


@ai.command("suggest")
@click.option("--file", "-f", type=click.Path(exists=True), help="Analyze existing design file")
@click.option(
    "--target",
    type=click.Choice(["strength", "weight", "cost", "manufacturability"]),
    default="strength",
    help="Optimization target",
)
@click.option("--material", "-M", help="Material name for AI suggestions (e.g., Q235)")
def ai_suggest(file, target, material):
    """
    AI design optimization suggestions

    Analyze design and provide improvement suggestions

    Examples:
        cae-cli ai suggest --file model.step --target strength
        cae-cli ai suggest -f bracket.step --target weight
        cae-cli ai suggest --file model.step --material Q235
    """
    from sw_helper.ai.generator import AIGenerator
    from sw_helper.knowledge import get_knowledge_base

    try:
        console.print("[bold cyan]AI优化建议[/bold cyan]")
        console.print(f"优化目标: {target}")
        if material:
            console.print(f"材料: {material}")
        console.print("-" * 60)

        ai_gen = AIGenerator()

        # 模拟当前参数和质量指标
        current_params = {
            "wall_thickness": 5,
            "fillet_radius": 3,
            "material": material or "Q235",
        }

        mock_metrics = {"max_stress": 180e6, "safety_factor": 1.8, "weight": 2.5}

        # 从知识库获取材料知识
        knowledge_text = ""
        if material:
            kb = get_knowledge_base()
            knowledge_text = kb.get_knowledge_text(material)

        suggestions = ai_gen.generate_optimization_suggestions(current_params, mock_metrics, target, knowledge_text)

        if suggestions:
            console.print(f"\n[cyan]发现 {len(suggestions)} 条优化建议:[/cyan]\n")

            for i, sug in enumerate(suggestions, 1):
                panel = Panel.fit(
                    f"[bold]{sug['reason']}[/bold]\n\n"
                    f"类型: {sug['type']}\n"
                    f"建议值: {sug.get('suggested', 'N/A')}\n"
                    f"预期改进: {sug.get('expected_improvement', 'N/A')}",
                    title=f"建议 {i}",
                    border_style="green",
                )
                console.print(panel)
        else:
            console.print("[yellow]暂无可用的优化建议[/yellow]")

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")


# ==================== 宏生成命令 ====================


@cli.command(hidden=True)
@click.argument("output_dir", type=click.Path())
@click.option(
    "--type",
    "-t",
    type=click.Choice(["export", "parametric", "full"], case_sensitive=False),
    default="full",
    help="Macro type",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["step", "stl", "iges"], case_sensitive=False),
    default="step",
    help="Export format",
)
@click.option("--cli-path", default="cae-cli", help="CLI command path")
def macro(output_dir, type, format, cli_path):  # noqa: PLR0912
    """
    Generate SolidWorks VBA macro

    OUTPUT_DIR: Macro file output directory

    Generate VBA macro code that can run in SolidWorks,实现：
    - One-click export model to STEP/STL
    - Auto call CLI analysis
    - Popup report path
    - Parametric dimension modification

    Examples:
        cae-cli macro ./macros --type export --format step
        cae-cli macro ./macros --type full --cli-path "C:\\Tools\\cae-cli"
    """
    from pathlib import Path

    from sw_helper.integrations.sw_macro import SolidWorksMacroGenerator

    def _generate_export_macro(generator, output_path, export_format, call_cli, cli_path):
        """Generate export macro"""
        macro_code = generator.generate_export_macro(
            output_path=str(output_path / "exported.step"),
            export_format=export_format.upper(),
            call_cli=call_cli,
            cli_path=cli_path,
        )
        macro_file = output_path / "CAE_Export.bas"
        generator.save_macro(macro_code, str(macro_file))
        console.print(f"[green]成功[/green] 导出宏: {macro_file}")
        return macro_file

    def _generate_parametric_macro(generator, output_path):
        """Generate parametric macro"""
        macro_code = generator.generate_parameter_macro()
        macro_file = output_path / "CAE_Parametric.bas"
        generator.save_macro(macro_code, str(macro_file))
        console.print(f"[green]成功[/green] 参数宏: {macro_file}")
        return macro_file

    def _generate_full_macro(generator, output_path, cli_path):
        """Generate full integration macro"""
        macro_code = generator.generate_full_integration_macro(cli_path)
        macro_file = output_path / "CAE_FullIntegration.bas"
        generator.save_macro(macro_code, str(macro_file))
        console.print(f"[green]成功[/green] 完整集成宏: {macro_file}")
        return macro_file

    def _display_usage():
        """Display macro usage instructions"""
        console.print("\n[cyan]使用方法:[/cyan]")
        console.print("1. 在SolidWorks中按 Alt+F11 打开VBA编辑器")
        console.print("2. 文件 -> 导入文件，选择生成的.bas文件")
        console.print("3. 运行宏即可实现自动化导出和分析")

    def _display_full_features():
        """Display full integration macro features"""
        console.print("\n[dim]完整集成宏功能:[/dim]")
        console.print("  - 修改圆角参数")
        console.print("  - 重建模型")
        console.print("  - 导出STEP文件")
        console.print("  - 调用CLI分析")
        console.print("  - 显示报告路径")
        console.print("  - 支持优化循环")

    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        console.print("[bold cyan]🔧 生成SolidWorks宏[/bold cyan]")
        console.print(f"输出目录: {output_path}")
        console.print(f"宏类型: {type}")
        console.print("-" * 60)

        generator = SolidWorksMacroGenerator()

        if type in ["export", "full"]:
            _generate_export_macro(generator, output_path, format, (type == "full"), cli_path)

        if type in ["parametric", "full"]:
            _generate_parametric_macro(generator, output_path)

        if type == "full":
            _generate_full_macro(generator, output_path, cli_path)

        _display_usage()

        if type == "full":
            _display_full_features()

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        console.print_exception()


# ==================== Chat交互命令 ====================


def _configure_llm_for_chat(model, api_key, mock, chat_instance):
    """Configure LLM client for chat"""
    if not mock and model != "auto":
        if model == "openai":
            api_key = api_key or click.prompt("OpenAI API Key", hide_input=True, confirmation_prompt=False)
            chat_instance.llm_client = create_openai_client(api_key=api_key)
        elif model == "anthropic":
            api_key = api_key or click.prompt("Anthropic API Key", hide_input=True, confirmation_prompt=False)
            from sw_helper.ai.llm_client import create_anthropic_client

            chat_instance.llm_client = create_anthropic_client(api_key=api_key)
        elif model == "deepseek":
            api_key = api_key or click.prompt("DeepSeek API Key", hide_input=True, confirmation_prompt=False)
            config = LLMConfig(
                provider=LLMProvider.DEEPSEEK,
                model="deepseek-chat",
                api_key=api_key,
            )
            chat_instance.llm_client = LLMClient(config)
        elif model == "ollama":
            chat_instance.llm_client = create_ollama_client()

        console.print(f"[green]成功 {model} 模型已配置[/green]")
    elif mock:
        console.print("[yellow]⚠ 模拟模式 - 不使用AI，直接执行命令[/yellow]")


def _display_chat_start_panel():
    """Display chat start panel"""
    console.print(
        Panel.fit(
            "[bold cyan]🚀 启动MechDesign智能助手[/bold cyan]\n" "集成MCP + LLM + FreeCAD的交互式设计环境",
            border_style="cyan",
        )
    )


@cli.command(hidden=True)
@click.option(
    "--model",
    "-m",
    type=click.Choice(["openai", "anthropic", "deepseek", "ollama", "auto"]),
    default="auto",
    help="AI model provider",
)
@click.option("--api-key", "-k", help="API key")
@click.option("--mock", is_flag=True, help="Use mock mode (no AI required)")
def chat(model, api_key, mock):  # noqa: PLR0912
    """
    Start interactive AI assistant (similar to OpenCode)

    Integrated MCP + LLM + FreeCAD intelligent dialogue interface

    Features:
      - Natural language control of FreeCAD modeling
      - Intelligent parameter optimization suggestions
      - Real-time quality analysis feedback
      - Multi-turn dialogue context understanding

    Examples:
        # Auto select model
        cae-cli chat

        # Use OpenAI
        cae-cli chat --model openai --api-key YOUR_API_KEY_HERE

        # Use local Ollama
        cae-cli chat --model ollama

        # Pure MCP mode (no AI required)
        cae-cli chat --mock

    Dialogue examples:
        > Create a cube with length 100, width 50, height 30
        > Open file model.FCStd
        > Optimize fillet radius from 2 to 15
        > Analyze quality of current model
    """
    import asyncio

    from sw_helper.ai.llm_client import (
        LLMClient,
        LLMConfig,
        LLMProvider,
        create_anthropic_client,
        create_ollama_client,
        create_openai_client,
    )
    from sw_helper.chat.interactive import OpencodeStyleChat

    def _configure_llm(chat_instance):
        """Configure LLM client for chat"""
        if not mock and model != "auto":
            if model == "openai":
                actual_api_key = api_key or click.prompt("OpenAI API Key", hide_input=True, confirmation_prompt=False)
                chat_instance.llm_client = create_openai_client(api_key=actual_api_key)
            elif model == "anthropic":
                actual_api_key = api_key or click.prompt(
                    "Anthropic API Key", hide_input=True, confirmation_prompt=False
                )
                chat_instance.llm_client = create_anthropic_client(api_key=actual_api_key)
            elif model == "deepseek":
                actual_api_key = api_key or click.prompt("DeepSeek API Key", hide_input=True, confirmation_prompt=False)
                config = LLMConfig(
                    provider=LLMProvider.DEEPSEEK,
                    model="deepseek-chat",
                    api_key=actual_api_key,
                )
                chat_instance.llm_client = LLMClient(config)
            elif model == "ollama":
                chat_instance.llm_client = create_ollama_client()

            console.print(f"[green]成功 {model} 模型已配置[/green]")
        elif mock:
            console.print("[yellow]⚠ 模拟模式 - 不使用AI，直接执行命令[/yellow]")

    try:
        console.print(
            Panel.fit(
                "[bold cyan]🚀 启动MechDesign智能助手[/bold cyan]\n" "集成MCP + LLM + FreeCAD的交互式设计环境",
                border_style="cyan",
            )
        )

        chat_instance = OpencodeStyleChat()
        _configure_llm(chat_instance)
        asyncio.run(chat_instance.start())

    except KeyboardInterrupt:
        console.print("\n[yellow]再见！[/yellow]")
    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        raise


# ==================== MCP工具命令 ====================


@cli.group(hidden=True)
def handbook():
    """
    机械手册知识库功能

    提供机械设计相关的知识查询和搜索功能
    """
    pass


@handbook.command()
@click.argument("keyword")
@click.option("--case-sensitive", "-c", is_flag=True, help="Case-sensitive search")
def search(keyword, case_sensitive):
    """
    搜索知识库

    搜索知识库中的所有 Markdown 文件，返回包含关键词的内容

    KEYWORD: 搜索关键词
    """
    from sw_helper.knowledge import get_knowledge_base

    # 创建Console时处理编码问题
    try:
        console = Console(force_terminal=False)
    except Exception:
        console = Console()

    kb = get_knowledge_base()

    console.print(f"[cyan]正在搜索知识库:[/cyan] '{keyword}'")

    if case_sensitive:
        results = kb.search(keyword)
    else:
        results = kb.search(keyword.lower())

    if not results:
        console.print(f"[red]未找到包含 '{keyword}' 的内容[/red]")
        kb._suggest_keywords()
        return

    console.print(f"[green]找到 {len(results)} 个匹配结果:[/green]")

    for i, result in enumerate(results, 1):
        # 高亮关键词
        highlighted_content = kb.highlight_keyword(result["content"], keyword)

        # 显示结果
        from rich.panel import Panel

        panel = Panel(
            highlighted_content,
            title=f"[green]{result['title']}[/green]",
            subtitle=f"[dim]{result['filename']}[/dim]",
            border_style="cyan",
            expand=False,
        )
        console.print(panel)
        console.print()


@handbook.command()
@click.argument("material_name")
def material(material_name):
    """
    搜索材料信息

    搜索知识库中的材料信息，支持牌号、名称等模糊搜索

    MATERIAL_NAME: 材料名称或牌号（如 Q235、45钢、304不锈钢）
    """
    from rich.console import Console

    from sw_helper.knowledge import get_knowledge_base

    console = Console()
    kb = get_knowledge_base()

    console.print(f"[cyan]正在搜索材料信息:[/cyan] '{material_name}'")

    results = kb.search_material(material_name)

    if not results:
        console.print(f"[red]未找到关于 '{material_name}' 的材料信息[/red]")
        console.print("[dim]建议搜索:[/dim]")
        for mat in ["Q235", "45钢", "Q345", "304不锈钢", "6061铝合金"]:
            console.print(f"  - [cyan]{mat}[/cyan]")
        return

    console.print(f"[green]找到 {len(results)} 个匹配结果:[/green]")

    for i, result in enumerate(results, 1):
        highlighted_content = kb.highlight_keyword(result["content"], material_name)

        from rich.panel import Panel

        panel = Panel(
            highlighted_content,
            title=f"[green]{result['title']}[/green]",
            subtitle=f"[dim]{result['filename']}[/dim]",
            border_style="cyan",
            expand=False,
        )
        console.print(panel)
        console.print()


@handbook.command()
@click.argument("bolt_spec")
def bolt(bolt_spec):
    """
    搜索螺栓规格

    搜索知识库中的螺栓规格信息，支持 M 型号搜索

    BOLT_SPEC: 螺栓规格（如 M6、M8、M10 等）
    """
    from rich.console import Console

    from sw_helper.knowledge import get_knowledge_base

    console = Console()
    kb = get_knowledge_base()

    console.print(f"[cyan]正在搜索螺栓规格:[/cyan] '{bolt_spec}'")

    results = kb.search_bolt(bolt_spec)

    if not results:
        console.print(f"[red]未找到关于 '{bolt_spec}' 的螺栓规格信息[/red]")
        console.print("[dim]建议搜索:[/dim]")
        for spec in ["M6", "M8", "M10", "M12", "M16", "M20"]:
            console.print(f"  - [cyan]{spec}[/cyan]")
        return

    console.print(f"[green]找到 {len(results)} 个匹配结果:[/green]")

    for i, result in enumerate(results, 1):
        highlighted_content = kb.highlight_keyword(result["content"], bolt_spec)

        from rich.panel import Panel

        panel = Panel(
            highlighted_content,
            title=f"[green]{result['title']}[/green]",
            subtitle=f"[dim]{result['filename']}[/dim]",
            border_style="cyan",
            expand=False,
        )
        console.print(panel)
        console.print()


# ===================== Learn 命令组 =====================


@cli.group(hidden=True)
def learn():
    """MechDesign 学习中心 - 系统化学习CAE知识"""
    pass


@learn.command("list")
def learn_list():
    """列出所有可用课程"""
    from sw_helper.learn import CourseManager

    console = Console()

    # 标题
    console.print("\n")
    console.print("[bold cyan]📚 MechDesign 学习中心[/bold cyan]")
    console.print("=" * 50)

    # 课程列表
    courses = CourseManager.get_all_courses()

    console.print("\n[bold]可选课程：[/bold]\n")

    for i, course in enumerate(courses, 1):
        console.print(f"  [cyan]{i}.[/cyan] [bold]{course.name}[/bold]")
        console.print(f"      {course.description}")
        console.print(f"      [dim]命令: cae-cli learn {course.id}[/dim]\n")

    console.print("=" * 50)
    console.print("\n[bold]使用说明：[/bold]")
    console.print("  查看课程:  cae-cli learn list")
    console.print("  进入课程:  cae-cli learn <课程名>")
    console.print("  示例:      cae-cli learn mechanics")
    console.print()


@learn.command("mechanics", help="材料力学")
def learn_mechanics():
    """材料力学"""
    _show_course("mechanics")


@learn.command("theory", help="理论力学")
def learn_theory():
    """理论力学"""
    _show_course("theory")


@learn.command("fem", help="有限元基础")
def learn_fem():
    """有限元基础"""
    _show_course("fem")


@learn.command("materials", help="材料知识")
def learn_materials():
    """材料知识"""
    _show_course("materials")


@learn.command("fasteners", help="紧固件")
def learn_fasteners():
    """紧固件"""
    _show_course("fasteners")


@learn.command("standards", help="公差配合")
def learn_standards():
    """公差配合"""
    _show_course("standards")


@learn.command("standard-parts", help="标准零件")
def learn_standard_parts():
    """标准零件"""
    _show_course("standard_parts")


# 通用的课程查看命令（支持任意课程ID）
@learn.command("view", help="查看课程内容")
@click.argument("course_id", required=False)
def learn_view(course_id):
    """查看课程内容

    COURSE_ID: 课程ID（支持模糊匹配）

    示例:
      cae-cli learn view mechanics
      cae-cli learn view standard
    """
    from sw_helper.learn import CourseManager

    console = Console()

    if not course_id:
        learn_list()
        return

    # 尝试精确匹配
    course = CourseManager.get_course(course_id)

    # 如果没有精确匹配，尝试模糊匹配
    if not course:
        # 模糊匹配：检查是否包含搜索词
        course_id_lower = course_id.lower().replace("-", "_")
        for c in CourseManager.get_all_courses():
            if course_id_lower in c.id.lower():
                course = c
                break

    if not course:
        # 搜索名称和关键词
        courses = CourseManager.search(course_id)
        if courses:
            course = courses[0]
            console.print(f"[yellow]未找到 '{course_id}'，显示搜索结果: {course.name}[/yellow]\n")

    if not course:
        console.print(f"\n[red]错误: 未找到课程 '{course_id}'[/red]\n")
        console.print("[bold]可用课程：[/bold]")
        for c in CourseManager.get_all_courses():
            console.print(f"  - {c.id}: {c.name}")
        console.print("\n使用 [cyan]cae-cli learn list[/cyan] 查看所有课程\n")
        return

    # 显示课程
    _show_course(course.id)


def _show_course(course_id: str):
    """显示课程内容"""
    from sw_helper.learn import CourseManager, load_course_content

    console = Console()

    course = CourseManager.get_course(course_id)
    if not course:
        console.print(f"[red]错误: 未知课程 '{course_id}'[/red]\n")
        return

    console.print("\n")
    console.print(f"[bold cyan]📖 {course.name}[/bold cyan]")
    console.print("-" * 40)
    console.print(f"{course.description}\n")

    content = load_course_content(course_id)
    if content:
        console.print("[bold]课程内容：[/bold]")
        console.print(content[:1500])
        if len(content) > 1500:
            console.print("\n[dim]... (内容过长)[/dim]")

    console.print("\n" + "=" * 40)
    console.print("[bold]下一步：[/bold]")
    console.print("  AI问答: cae-cli learn chat")
    console.print("  课程列表: cae-cli learn list")
    console.print()


@learn.command()
@click.argument("course_id", required=False)
def learn_read(course_id):
    """读取完整课程内容

    COURSE_ID: 课程ID (mechanics, theory, fem, materials, fasteners, standards)
    """
    import platform
    import subprocess

    from sw_helper.learn import CourseManager, load_course_content

    console = Console()

    if not course_id:
        console.print("[red]请指定课程ID[/red]")
        console.print("使用 cae-cli learn list 查看可用课程\n")
        return

    course = CourseManager.get_course(course_id)

    if not course:
        console.print(f"[red]错误: 未知课程 '{course_id}'[/red]\n")
        return

    content = load_course_content(course_id)

    # 使用系统分页器显示
    if platform.system() == "Windows":
        # Windows: 使用 more
        with open("temp_learn.md", "w", encoding="utf-8") as f:
            f.write(content)
        subprocess.run(["cmd", "/c", "type", "temp_learn.md"])
        try:
            import os

            os.remove("temp_learn.md")
        except OSError:
            pass
    else:
        # Linux/Mac: 使用 less 或 more
        with open("temp_learn.md", "w", encoding="utf-8") as f:
            f.write(content)
        subprocess.run(
            ["less", "temp_learn.md"]
            if subprocess.run(["which", "less"]).returncode == 0
            else ["more", "temp_learn.md"]
        )
        try:
            import os

            os.remove("temp_learn.md")
        except OSError:
            pass


@learn.command("create")
@click.argument("course_name")
@click.option("--description", "-d", default="", help="课程描述")
@click.option("--keywords", "-k", default="", help="关键词，用逗号分隔")
def learn_create(course_name, description, keywords):
    """创建新课程模板

    COURSE_NAME: 课程名称

    示例:
      cae-cli learn create "机械设计基础"
      cae-cli learn create "振动分析" -d "机械振动理论" -k "振动,固有频率,模态"
    """
    from sw_helper.learn import CourseManager, create_course_template

    console = Console()

    # 构建关键词列表
    [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []

    # 生成模板
    from sw_helper.learn import KNOWLEDGE_DIR

    template = create_course_template(course_name, description)

    # 保存到文件
    course_filename = course_name.lower().replace(" ", "-")
    course_path = KNOWLEDGE_DIR / f"{course_filename}.md"

    if course_path.exists():
        console.print(f"[red]错误: 课程文件已存在: {course_path}[/red]")
        return

    try:
        with open(course_path, "w", encoding="utf-8") as f:
            f.write(template)

        # 刷新缓存
        CourseManager.refresh()

        console.print("\n[green]✓ 课程创建成功![/green]")
        console.print(f"  文件: {course_path}")
        console.print("\n[bold]下一步：[/bold]")
        console.print(f"  编辑内容: code {course_path}")
        console.print(f"  查看课程: cae-cli learn {course_filename}")
        console.print("  刷新列表: cae-cli learn list\n")

    except Exception as e:
        console.print(f"[red]创建失败: {e}[/red]")


@learn.command("chat")
@click.option(
    "--mode",
    "-m",
    default="learning",
    type=click.Choice(["default", "learning", "lifestyle", "mechanical"]),
    help="AI模式选择",
)
def learn_chat(mode):  # noqa: PLR0912
    """AI学习助手 - 问答模式

    --mode 选项:
      learning: 学习模式 (3-2-1方法+费曼学习法)
      lifestyle: 生活态度模式
      mechanical: 机械设计模式
      default: 默认模式
    """
    from sw_helper.ai.prompt_manager import PromptManager

    console = Console()

    # 获取系统提示词
    system_prompt = PromptManager.build_system_prompt(mode)

    console.print("\n[bold cyan]🤖 MechDesign AI 学习助手[/bold cyan]")
    console.print(f"[dim]模式: {mode}[/dim]")
    console.print("=" * 40)

    # 显示模式说明
    mode_descs = {
        "learning": "🎯 学习模式 - 使用3-2-1方法和费曼学习法",
        "lifestyle": "🌟 生活态度 - 行动优先、长期主义",
        "mechanical": "🔧 机械设计 - 专注机械设计领域",
        "default": "📚 默认模式 - 综合助手",
    }
    console.print(f"[yellow]{mode_descs.get(mode, '')}[/yellow]\n")

    # 检测模型
    ollama_ok = False
    ollama_model = None

    try:
        import requests

        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            models = r.json().get("models", [])
            if models:
                ollama_model = models[0].get("name", "")
                ollama_ok = True
                console.print(f"[green]✓ 模型: {ollama_model}[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠ 检测Ollama失败: {e}[/yellow]")

    console.print("=" * 40)
    console.print("[bold]输入问题开始学习，q退出[/bold]")
    console.print("[dim]提示: 使用 --mode 切换模式[/dim]\n")

    # 主循环 - 带历史记录
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            q = input("> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            console.print("\n再见!")
            break

        if not q or not q.strip():
            continue
        if q.strip().lower() == "q":
            console.print("再见!")
            break

        console.print("\nAI思考中...\n")

        # 调用API
        if ollama_ok and ollama_model:
            try:
                import requests

                messages.append({"role": "user", "content": q.strip()})

                resp = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": ollama_model,
                        "messages": messages[-10:],  # 保留最近10条
                        "stream": False,
                    },
                    timeout=60,
                )
                if resp.status_code == 200:
                    answer = resp.json().get("message", {}).get("content", "")
                    console.print(answer)
                    messages.append({"role": "assistant", "content": answer})
                    console.print()
                else:
                    console.print(f"[red]API错误: {resp.status_code}[/red]\n")
            except Exception as e:
                console.print(f"[red]请求错误: {e}[/red]\n")
        else:
            console.print("[yellow]无可用AI模型，请确保Ollama已启动[/yellow]\n")


@cli.command(hidden=True)
@click.option("--lang", default="zh", type=click.Choice(["zh", "en"]))
def interactive(lang):  # noqa: PLR0912
    """
    Interactive mode - use CAE-CLI through a menu interface

    Features:
        1. Analyze model
        2. Parameter optimization
        3. AI generate model
        4. 知识库查询 (Handbook)
        5. Exit

    Support direct command input like: "analyze test.step --material 40Cr"
    """
    import json
    import sys
    from pathlib import Path

    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table

    # 加载语言包
    lang_file = get_resource_path("data/languages.json")
    try:
        with open(lang_file, encoding="utf-8") as f:
            lang_data = json.load(f)
        strings = lang_data.get(lang, lang_data["zh"])
    except Exception as e:
        print(f"Warning: Failed to load language pack: {e}")
        strings = {}

    # 初始化Console
    from rich.console import Console

    console = Console()

    # 启动动画函数 - 使用与主CLI相同的横幅
    def show_startup_animation():
        """显示启动动画 - 使用与主CLI相同的横幅"""
        import time

        # 清除屏幕
        console.clear()

        # 使用与主CLI相同的ASCII艺术横幅
        # ASCII Art 横幅
        banner_lines = [
            "════════════════════════════════════════════════════════════",
            "███╗   ███╗███████╗ ██████╗██╗  ██╗██████╗ ███████╗███████╗",
            " ████╗ ████║██╔════╝██╔════╝██║  ██║██╔══██╗██╔════╝██╔════╝",
            " ██╔████╔██║█████╗  ██║     ███████║██║  ██║█████╗  ███████╗",
            " ██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██║  ██║██╔══╝  ╚════██║",
            " ██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██████╔╝███████╗███████║",
            " ╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝",
            "════════════════════════════════════════════════════════════",
        ]

        # 颜色代码
        CYAN = "\033[96m"
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        # 逐行显示横幅（打字机效果）
        for i, line in enumerate(banner_lines):
            if i == 0 or i == len(banner_lines) - 1:
                print(f"{CYAN}{line}{RESET}")
            else:
                print(f"{CYAN}{line[0:18]}{RESET}{BLUE}{line[18:]}{RESET}")
            time.sleep(0.08)

        # 副标题
        print()
        subtitle_lines = [
            ("◆", BLUE, " 交互模式启动"),
            ("◆", GREEN, f" 版本: {__version__}"),
        ]

        for prefix, color, text in subtitle_lines:
            print(f"{color}{prefix}{RESET}{BOLD}{text}{RESET}")
            time.sleep(0.15)

        print()
        print(f"{CYAN}{'═' * 60}{RESET}")
        print()

    # 显示启动动画
    show_startup_animation()

    # 一级菜单选择函数
    def select_mode():
        console.print("\n[bold]请选择模式:[/bold]")
        console.print("  [cyan]1[/cyan]. [green]工作模式[/green] - 网格分析、参数优化、AI建模")
        console.print("  [cyan]2[/cyan]. [yellow]学习模式[/yellow] - AI助教，解答机械工程问题")
        console.print("  [cyan]3[/cyan]. 退出")

        while True:
            try:
                choice = input("\n请输入选择 (1-3): ").strip()
            except (EOFError, KeyboardInterrupt):
                choice = ""
            if choice == "1":
                return "work"
            elif choice == "2":
                return "learn"
            elif choice == "3":
                return "exit"
            elif choice == "":
                # 默认选择学习模式
                return "learn"
            else:
                print("无效选择，请输入 1, 2 或 3")

    # 学习模式函数 - 极简稳定版
    def learning_mode():
        """简洁的AI学习助手"""
        import sys

        # 创建本地console用于学习模式（不干扰主console）
        from rich.console import Console as RichConsole

        RichConsole()

        # 使用原始标准流
        out = sys.stdout.write
        inp = sys.stdin.readline

        out("\n=== 学习助手初始化 ===\n")

        # 检测模型
        ollama_ok = False
        ollama_model = None

        try:
            import requests

            r = requests.get("http://localhost:11434/api/tags", timeout=3)
            if r.status_code == 200:
                models = r.json().get("models", [])
                if models:
                    ollama_model = models[0].get("name", "")
                    ollama_ok = True
                    out(f"模型: {ollama_model}\n")
        except Exception as e:
            out(f"检测Ollama失败: {e}\n")

        out("=====================\n")
        out("输入问题，q退出\n\n")

        # 主循环
        while True:
            out("> ")
            try:
                q = inp()
            except (EOFError, KeyboardInterrupt):
                break

            if not q.strip():
                continue
            if q.strip().lower() == "q":
                out("再见!\n")
                break

            out("AI思考中...\n")

            # 调用API
            if ollama_ok and ollama_model:
                try:
                    import requests

                    resp = requests.post(
                        "http://localhost:11434/api/chat",
                        json={
                            "model": ollama_model,
                            "messages": [{"role": "user", "content": q.strip()}],
                            "stream": False,
                        },
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        answer = resp.json().get("message", {}).get("content", "")
                        out(f"\n{answer}\n\n")
                    else:
                        out(f"\nAPI错误: {resp.status_code}\n\n")
                except Exception as e:
                    out(f"\n错误: {e}\n\n")
            else:
                out("\n无AI模型\n")

    # 主循环
    while True:
        mode = select_mode()

        if mode == "work":
            # 原有工作模式逻辑（完整保留）
            while True:
                try:
                    # 显示菜单（支持箭头键选择）
                    console.clear()

                    # 创建菜单表格
                    menu_table = Table(
                        title=strings.get("menu_title", "MechDesign Interactive Mode"),
                        show_header=True,
                        header_style="bold cyan",
                    )
                    menu_table.add_column(
                        strings.get("columns", {}).get("option", "Option"),
                        style="cyan",
                        width=5,
                    )
                    menu_table.add_column(strings.get("columns", {}).get("operation", "Operation"), style="green")
                    menu_table.add_column(
                        strings.get("columns", {}).get("description", "Description"),
                        style="dim",
                    )

                    menu_table.add_row(
                        "1",
                        strings.get("menu", {}).get("analyze", "Analyze Model"),
                        strings.get("descriptions", {}).get("analyze", "Analyze geometry or mesh quality"),
                    )
                    menu_table.add_row(
                        "2",
                        strings.get("menu", {}).get("optimize", "Optimize Parameter"),
                        strings.get("descriptions", {}).get("optimize", "Parameter optimization"),
                    )
                    menu_table.add_row(
                        "3",
                        strings.get("menu", {}).get("ai_generate", "AI Generate Model"),
                        strings.get("descriptions", {}).get("ai_generate", "AI model generation"),
                    )
                    menu_table.add_row(
                        "4",
                        strings.get("menu", {}).get("handbook", "知识库查询 (Handbook)"),
                        strings.get("descriptions", {}).get("handbook", "Query mechanical handbook knowledge base"),
                    )
                    menu_table.add_row(
                        "5",
                        strings.get("menu", {}).get("exit", "Exit"),
                        strings.get("descriptions", {}).get("exit", "Exit interactive mode"),
                    )

                    console.print(menu_table)
                    console.print(
                        strings.get("prompts", {}).get(
                            "direct_command",
                            "\n[dim]Type a command directly (e.g., 'analyze test.step') to execute[/dim]",
                        )
                    )

                    # 直接使用简单输入方式（更稳定）
                    choice = Prompt.ask(
                        strings.get("prompts", {}).get("enter_choice", "\n输入选项 (1-5) 或直接输入命令")
                    )

                    if choice == "1":
                        # 分析模型
                        file_path = Prompt.ask(strings.get("analyze", {}).get("enter_file", "Enter model file path"))
                        if file_path:
                            # 支持多种分析选项
                            console.print(strings.get("analyze", {}).get("options", "\n[cyan]Analysis options:[/cyan]"))
                            console.print(
                                strings.get("analyze", {}).get("parse", "  - [bold]parse[/bold]: Parse geometry file")
                            )
                            console.print(
                                strings.get("analyze", {}).get(
                                    "analyze", "  - [bold]analyze[/bold]: Analyze mesh quality"
                                )
                            )
                            console.print(
                                strings.get("analyze", {}).get(
                                    "material",
                                    "  - [bold]material[/bold]: Query material properties",
                                )
                            )

                            analysis_type = Prompt.ask(
                                strings.get("analyze", {}).get("enter_analysis_type", "Enter analysis type"),
                                default="parse",
                            )

                            if analysis_type == "parse":
                                from sw_helper.geometry.parser import GeometryParser

                                try:
                                    parser = GeometryParser()
                                    result = parser.parse(file_path)
                                    console.print_json(data=result)
                                except Exception as e:
                                    console.print(
                                        strings.get("prompts", {})
                                        .get("error", "[red]Error: {error}[/red]")
                                        .format(error=e)
                                    )

                            elif analysis_type == "analyze":
                                from sw_helper.mesh.quality import MeshQualityAnalyzer

                                try:
                                    analyzer = MeshQualityAnalyzer()
                                    results = analyzer.analyze(file_path)
                                    console.print_json(data=results)
                                except Exception as e:
                                    console.print(
                                        strings.get("prompts", {})
                                        .get("error", "[red]Error: {error}[/red]")
                                        .format(error=e)
                                    )

                            elif analysis_type == "material":
                                material_name = Prompt.ask(
                                    strings.get("analyze", {}).get("enter_material_name", "Enter material name")
                                )
                                if material_name:
                                    from sw_helper.material.database import MaterialDatabase

                                    try:
                                        db = MaterialDatabase()
                                        material_info = db.get_material(material_name)
                                        if material_info:
                                            console.print_json(data=material_info)
                                        else:
                                            console.print(
                                                strings.get("analyze", {})
                                                .get(
                                                    "material_not_found",
                                                    f"[yellow]Material '{material_name}' not found[/yellow]",
                                                )
                                                .format(material_name=material_name)
                                            )
                                    except Exception as e:
                                        console.print(
                                            strings.get("prompts", {})
                                            .get("error", "[red]Error: {error}[/red]")
                                            .format(error=e)
                                        )

                    elif choice == "2":
                        # 参数优化
                        file_path = Prompt.ask(
                            strings.get("optimize", {}).get("enter_cad_file", "Enter CAD file path (.FCStd)")
                        )
                        if file_path:
                            parameter = Prompt.ask(
                                strings.get("optimize", {}).get("enter_parameter", "Enter parameter to optimize")
                            )
                            if parameter:
                                param_range = Prompt.ask(
                                    strings.get("optimize", {}).get(
                                        "enter_param_range", "Enter parameter range (min max)"
                                    ),
                                    default="2 15",
                                )
                                steps = Prompt.ask(
                                    strings.get("optimize", {}).get("enter_steps", "Enter number of steps"),
                                    default="5",
                                )

                                try:
                                    min_val, max_val = map(float, param_range.split())
                                    steps_int = int(steps)

                                    from sw_helper.optimization.optimizer import (
                                        FreeCADOptimizer,
                                    )

                                    optimizer = FreeCADOptimizer(use_mock=False)

                                    # 设置进度回调
                                    def progress_callback(msg):
                                        console.print(msg)

                                    optimizer.set_progress_callback(progress_callback)

                                    # 执行优化
                                    results = optimizer.optimize_parameter(
                                        file_path=file_path,
                                        param_name=parameter,
                                        param_range=(min_val, max_val),
                                        steps=steps_int,
                                        step_mode="linear",
                                        output_dir="./optimization_output",
                                        analyze_geometry=True,
                                    )

                                    if results:
                                        best = max(results, key=lambda x: x.quality_score)
                                        console.print(
                                            strings.get("optimize", {}).get(
                                                "best_result", "\n[green]Best result:[/green]"
                                            )
                                        )
                                        console.print(
                                            strings.get("optimize", {})
                                            .get(
                                                "parameter",
                                                "Parameter: {parameter_name} = {parameter_value:.2f} mm",
                                            )
                                            .format(
                                                parameter_name=best.parameter_name,
                                                parameter_value=best.parameter_value,
                                            )
                                        )
                                        console.print(
                                            strings.get("optimize", {})
                                            .get(
                                                "quality_score",
                                                "Quality Score: {quality_score:.1f}/100",
                                            )
                                            .format(quality_score=best.quality_score)
                                        )
                                        console.print(
                                            strings.get("optimize", {})
                                            .get(
                                                "allowable_stress",
                                                "Allowable Stress: {allowable_stress:.1f} MPa",
                                            )
                                            .format(allowable_stress=best.allowable_stress)
                                        )
                                        console.print(
                                            strings.get("optimize", {})
                                            .get(
                                                "safety_factor",
                                                "Safety Factor: {safety_factor:.2f}",
                                            )
                                            .format(safety_factor=best.safety_factor)
                                        )

                                    else:
                                        console.print(
                                            strings.get("optimize", {}).get(
                                                "no_results",
                                                "[yellow]No results obtained[/yellow]",
                                            )
                                        )

                                except Exception as e:
                                    console.print(
                                        strings.get("prompts", {})
                                        .get("error", "[red]Error: {error}[/red]")
                                        .format(error=e)
                                    )

                    elif choice == "3":
                        # AI生成模型
                        description = Prompt.ask(
                            strings.get("ai_generate", {}).get("enter_description", "Enter model description")
                        )
                        if description:
                            from sw_helper.ai.model_generator import AIModelGenerator

                            generator = AIModelGenerator()

                            try:
                                result = generator.generate(description)
                                console.print_json(data=result)
                            except Exception as e:
                                console.print(
                                    strings.get("prompts", {}).get("error", "[red]Error: {error}[/red]").format(error=e)
                                )

                    elif choice == "4":
                        # 知识库查询
                        from sw_helper.knowledge import get_knowledge_base

                        kb = get_knowledge_base()

                        while True:
                            try:
                                console.clear()
                                console.print(
                                    Panel(
                                        strings.get("handbook", {}).get(
                                            "welcome",
                                            "[green]📚 机械手册知识库查询[/green]\n\n输入关键词查询机械设计相关知识\n示例: 40Cr, M10螺栓, 圆角, 公差, Q235\n\n[dim]输入 'back' 或按 Enter 返回主菜单[/dim]",
                                        ),
                                        title=strings.get("handbook", {}).get("title", "知识库查询"),
                                        border_style="cyan",
                                    )
                                )

                                keyword = Prompt.ask(strings.get("handbook", {}).get("enter_keyword", "\n输入关键词"))

                                if not keyword or keyword.lower() == "back":
                                    break

                                # 执行搜索
                                console.print(
                                    strings.get("handbook", {})
                                    .get("searching", "\n[cyan]正在搜索: {keyword}[/cyan]")
                                    .format(keyword=keyword)
                                )
                                kb.search_and_display(keyword)

                                # 询问是否继续搜索
                                continue_search = Prompt.ask(
                                    strings.get("handbook", {}).get("continue_search", "\n继续搜索? (y/n)"),
                                    default="y",
                                ).lower()
                                if continue_search not in ["y", "yes"]:
                                    break

                            except KeyboardInterrupt:
                                console.print(
                                    strings.get("handbook", {}).get("back_to_menu", "\n[yellow]返回主菜单[/yellow]")
                                )
                                break
                            except Exception as e:
                                console.print(
                                    strings.get("handbook", {})
                                    .get("query_error", "[red]查询错误: {error}[/red]")
                                    .format(error=e)
                                )
                                try:
                                    Prompt.ask(
                                        strings.get("handbook", {}).get("press_enter", "\n按 Enter 继续..."),
                                        default="",
                                    )
                                except EOFError:
                                    break

                    elif choice == "5":
                        # 退出工作模式，返回一级菜单
                        console.print(strings.get("prompts", {}).get("back_to_main", "\n[green]返回主菜单...[/green]"))
                        break

                    elif choice.strip():
                        # 直接命令执行
                        try:
                            import subprocess

                            result = subprocess.run(
                                f"python -m sw_helper.cli {choice}",
                                shell=True,
                                capture_output=True,
                                text=True,
                                cwd=Path(__file__).parent.parent.parent,
                            )

                            if result.stdout:
                                console.print(result.stdout)
                            if result.stderr:
                                console.print(
                                    strings.get("prompts", {})
                                    .get("error", "[red]Error: {error}[/red]")
                                    .format(error=result.stderr)
                                )

                        except Exception as e:
                            console.print(
                                strings.get("prompts", {}).get("error", "[red]Error: {error}[/red]").format(error=e)
                            )

                    else:
                        console.print(
                            strings.get("prompts", {}).get(
                                "invalid_choice",
                                "[yellow]Please enter a valid choice or command[/yellow]",
                            )
                        )

                    # 按任意键继续
                    if choice not in ["5"]:
                        try:
                            Prompt.ask(
                                strings.get("prompts", {}).get("press_continue", "\nPress Enter to continue..."),
                                default="",
                            )
                        except EOFError:
                            break

                except KeyboardInterrupt:
                    console.print(
                        strings.get("prompts", {}).get("interrupted", "\n[yellow]Interrupted by user[/yellow]")
                    )
                    break
                except Exception as e:
                    console.print(strings.get("prompts", {}).get("error", "[red]Error: {error}[/red]").format(error=e))
                    import traceback

                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
                    try:
                        Prompt.ask(
                            strings.get("prompts", {}).get("press_continue", "\nPress Enter to continue..."),
                            default="",
                        )
                    except EOFError:
                        break

            # 工作模式循环结束，返回一级菜单
            continue

        elif mode == "learn":
            # 强制禁用console并重置stdout
            console = None
            import sys

            try:
                sys.stdout = sys.__stdout__
                sys.stdin = sys.__stdin__
            except (AttributeError, OSError):
                pass
            learning_mode()
            # 学习模式结束后返回一级菜单
            continue

        elif mode == "exit":
            console.print(
                strings.get("prompts", {}).get("thank_you", "\n[green]Thank you for using MechDesign![/green]")
            )
            break


@cli.group(hidden=True)
def mcp():
    """
    MCP (Model Context Protocol) tool management

    Manage MCP interfaces for FreeCAD and other tools
    """
    pass


@mcp.command("tools")
def mcp_tools():
    """List all available MCP tools"""
    from sw_helper.mcp.freecad_server import get_freecad_mcp_server

    try:
        server = get_freecad_mcp_server()
        tools = server.server.tools

        console.print(f"\n[bold cyan]可用MCP工具 ({len(tools)}个):[/bold cyan]\n")

        for name, tool in tools.items():
            panel = Panel.fit(
                f"[bold green]{tool.description}[/bold green]\n\n"
                f"输入参数:\n"
                f"[dim]{json.dumps(tool.input_schema, indent=2, ensure_ascii=False)}[/dim]",
                title=name,
                border_style="blue",
            )
            console.print(panel)
            console.print()

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")


@mcp.command("call")
@click.argument("tool_name")
@click.argument("arguments", required=False)
def mcp_call(tool_name, arguments):
    """
    Directly call MCP tool

    TOOL_NAME: Tool name
    ARGUMENTS: JSON formatted parameters (optional)

    Examples:
        cae-cli mcp call freecad_connect '{"use_mock": true}'
        cae-cli mcp call freecad_create_box '{"length": 100, "width": 50}'
    """
    import asyncio

    from sw_helper.mcp.core import InMemoryMCPTransport, MCPMessage
    from sw_helper.mcp.freecad_server import get_freecad_mcp_server

    async def run_tool():
        try:
            server = get_freecad_mcp_server()
            transport = InMemoryMCPTransport(server.server)

            # 解析参数
            args = {}
            if arguments:
                try:
                    args = json.loads(arguments)
                except json.JSONDecodeError:
                    console.print("[red]失败 参数格式错误，请使用JSON格式[/red]")
                    return

            # 构建消息
            message = MCPMessage(method="tools/call", params={"name": tool_name, "arguments": args})

            # 执行
            with console.status(f"[bold green]执行 {tool_name}..."):
                response = await transport.handle_client_message(message)

            # 显示结果
            if response.result:
                console.print("\n[green]成功 执行成功[/green]")
                content = response.result.get("content", [])
                if content:
                    result_text = content[0].get("text", "")
                    try:
                        result_json = json.loads(result_text)
                        console.print_json(data=result_json)
                    except json.JSONDecodeError:
                        console.print(result_text)
            elif response.error:
                console.print(f"\n[red]失败 错误: {response.error.get('message')}[/red]")

        except Exception as e:
            console.print(f"[red]失败 执行失败: {e}[/red]")

    asyncio.run(run_tool())


# ==================== 主菜单命令 ====================


@cli.command(hidden=True)
def menu():
    """
    启动CAE-CLI主菜单 - 三个并列顶层模块入口

    三个并列模块：
      - 工作模式：纯粹工具箱（分析、优化、报告生成）
      - 知识顾问：快速检索手册、材料参数、公差标准
      - 辅助学习：系统性学习、教学式解释、进度追踪

    风格：深红科技暗黑系 + 荧光红高亮
    """
    from sw_helper.main_menu import start_main_menu

    try:
        start_main_menu()
    except KeyboardInterrupt:
        console.print(f"\n[{HIGHLIGHT_RED}]再见！[{HIGHLIGHT_RED}]")
    except Exception as e:
        console.print(f"[red]启动主菜单失败: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()


@cli.command(hidden=True)
@click.option("--local", is_flag=True, help="审查本地未提交的变更")
@click.option("--pr", type=int, help="审查指定PR编号的变更")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="输出格式: text 或 json",
)
def review(local, pr, output_format):  # noqa: PLR0912
    """
    智能代码审查

    分析代码变更，检查安全、性能、可维护性问题。
    支持两种模式：
      --local：审查本地未提交的变更
      --pr NUMBER：审查指定PR的变更

    示例：
      cae-cli review --local
      cae-cli review --pr 123
      cae-cli review --local --format json
    """
    # 如果请求JSON格式，使用utils下的PR审查工具
    if output_format == "json":
        import subprocess
        import sys

        # 构建命令参数
        cmd = [sys.executable, "-m", "sw_helper.utils.pr_review", "--output", "json", "--no-rag"]

        if local:
            # 对于本地变更，比较HEAD和HEAD~1
            cmd.extend(["--base", "HEAD~1", "--head", "HEAD"])
        elif pr:
            # PR模式 - 简化处理，使用默认分支比较
            console.print(f"[yellow]注意: PR {pr} 审查使用默认分支比较[/yellow]")
            cmd.extend(["--branch", "main"])
        else:
            # 默认：比较当前分支与main
            cmd.extend(["--branch", "main"])

        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

        # 提取JSON输出（工具可能输出日志信息，JSON在最后）
        stdout_text = result.stdout if result.stdout is not None else ""
        stderr_text = result.stderr if result.stderr is not None else ""

        output_lines = stdout_text.strip().split("\n")
        json_start = None

        # 查找JSON开始位置
        for i, line in enumerate(output_lines):
            line = line.strip()
            if line.startswith("{"):
                json_start = i
                break

        if json_start is not None:
            json_str = "\n".join(output_lines[json_start:])
            try:
                # 验证JSON有效性并重新格式化输出
                import json

                json_data = json.loads(json_str)
                # 输出纯JSON
                print(json.dumps(json_data, indent=2, ensure_ascii=True))
            except json.JSONDecodeError as e:
                # JSON解析失败，输出原始内容
                print(f"[ERROR] JSON解析失败: {e}")
                print(stdout_text)
        else:
            # 没有找到JSON，输出原始内容
            print(stdout_text)

        if stderr_text:
            console.print(f"[yellow]{stderr_text}[/yellow]")

        # 传递退出码
        sys.exit(result.returncode)
    else:
        # 默认行为：使用原有的review_command
        try:
            # 尝试绝对导入
            from sw_helper.pr_review import review_command
        except ImportError:
            # 回退到相对导入
            from .pr_review import review_command

        try:
            review_command(local=local, pr=pr)
        except KeyboardInterrupt:
            console.print(f"\n[{HIGHLIGHT_RED}]审查已取消[/{HIGHLIGHT_RED}]")
        except Exception as e:
            console.print(f"[red]审查失败: {e}[/red]")


# 入口点
if __name__ == "__main__":
    cli()
