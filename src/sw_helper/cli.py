#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
Version: 0.1.0
"""

import sys
import json
import click
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# 确保导入路径正确
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

console = Console()

# 版本信息
__version__ = "0.1.0"
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
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config: Dict[str, Any]):
    """保存配置"""
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# 创建CLI组
@click.group()
@click.version_option(
    version=__version__, prog_name=__prog_name__, help="Show version info and exit"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output mode")
@click.option("--config", "-c", type=click.Path(), help="Specify config file path")
@click.pass_context
def cli(ctx, verbose, config):
    """
    CAE-CLI: SolidWorks CAE Integration Assistant

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
    # 确保ctx.obj存在
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config_path"] = config

    if verbose:
        console.print(f"[dim]版本: {__version__}[/dim]")


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
            result = parser.parse(
                file_path, file_format=None if format == "auto" else format
            )

            progress.update(task, completed=True)

        # 显示结果
        if format_output == "table":
            table = Table(
                title="几何信息", show_header=True, header_style="bold magenta"
            )
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

        # 显示结果表格
        table = Table(
            title="网格质量分析结果", show_header=True, header_style="bold blue"
        )
        table.add_column("指标", style="cyan")
        table.add_column("最小值", style="green")
        table.add_column("最大值", style="green")
        table.add_column("平均值", style="yellow")
        table.add_column("标准差", style="dim")

        for metric_name, values in results.items():
            if metric_name == "overall_quality":
                continue
            if isinstance(values, dict):
                table.add_row(
                    metric_name,
                    f"{values.get('min', 'N/A'):.4f}"
                    if isinstance(values.get("min"), (int, float))
                    else str(values.get("min", "N/A")),
                    f"{values.get('max', 'N/A'):.4f}"
                    if isinstance(values.get("max"), (int, float))
                    else str(values.get("max", "N/A")),
                    f"{values.get('mean', 'N/A'):.4f}"
                    if isinstance(values.get("mean"), (int, float))
                    else str(values.get("mean", "N/A")),
                    f"{values.get('std', 'N/A'):.4f}"
                    if isinstance(values.get("std"), (int, float))
                    else str(values.get("std", "N/A")),
                )

        console.print(table)

        # 整体质量评估
        overall = results.get("overall_quality", "unknown")
        quality_colors = {
            "excellent": "bright_green",
            "good": "green",
            "fair": "yellow",
            "poor": "red",
            "unknown": "dim",
        }
        color = quality_colors.get(overall, "white")
        console.print(f"\n整体质量: [{color}]{overall}[/{color}]")

        # 保存结果
        if output:
            import json

            with open(output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            console.print(f"[green]成功[/green] 报告已保存: [bold]{output}[/bold]")

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
@click.pass_context
def material(ctx, material_name, property, list_materials, search, unit):
    """
    Material database query

    MATERIAL_NAME: Material name (e.g.: Q235, 45Steel, Aluminum6061)

    Examples:
        cae-cli material Q235
        cae-cli material Q235 -p elastic_modulus
        cae-cli material --list
        cae-cli material --search "steel"
    """
    from sw_helper.material.database import MaterialDatabase

    try:
        db = MaterialDatabase()

        # 列出所有材料
        if list_materials:
            materials = db.list_materials()
            table = Table(title="材料数据库", show_header=True)
            table.add_column("名称", style="cyan")
            table.add_column("类型", style="green")
            table.add_column("标准", style="dim")

            for mat_name in materials:
                info = db.get_material(mat_name)
                table.add_row(
                    mat_name, info.get("type", "N/A"), info.get("standard", "N/A")
                )

            console.print(table)
            console.print(f"\n共 [bold]{len(materials)}[/bold] 种材料")
            return

        # 搜索材料
        if search:
            results = db.search_materials(search)
            if results:
                console.print(
                    f"\n搜索 '[bold]{search}[/bold]' 找到 {len(results)} 个结果:"
                )
                for mat in results:
                    console.print(
                        f"  - {mat['name']} - {mat.get('description', '无描述')}"
                    )
            else:
                console.print(
                    f"[yellow]未找到匹配 '[bold]{search}[/bold]' 的材料[/yellow]"
                )
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
                console.print(
                    f"[yellow]材料 '{material_name}' 没有属性 '{property}'[/yellow]"
                )
                console.print(f"可用属性: {', '.join(info.keys())}")
            return

        # 显示完整信息表格
        table = Table(title=f"材料信息: {material_name}", show_header=True)
        table.add_column("属性", style="cyan")
        table.add_column("值", style="green")
        table.add_column("单位", style="dim")

        # 单位转换
        unit_labels = {
            "si": {"density": "kg/m³", "elastic_modulus": "Pa", "strength": "Pa"},
            "mpa": {"density": "kg/m³", "elastic_modulus": "MPa", "strength": "MPa"},
        }

        for key, value in info.items():
            if key == "name":
                continue

            # 单位处理
            unit_label = ""
            if unit == "mpa" and isinstance(value, (int, float)):
                if "modulus" in key or "strength" in key:
                    value = value / 1e6
                    unit_label = "MPa"
                elif "density" in key:
                    unit_label = "kg/m³"

            table.add_row(str(key), str(value), unit_label)

        console.print(table)

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


@cli.command()
@click.option(
    "--set", "set_config", nargs=2, metavar="<KEY> <VALUE>", help="Set configuration item"
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


@cli.command()
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
@cli.command()
@click.pass_context
def info(ctx):
    """
    Show system information and configuration status

    Display current system environment, available integrations, and configuration info
    """
    from sw_helper.material.database import MaterialDatabase

    console.print(Panel.fit("[bold]CAE-CLI 系统信息[/bold]", border_style="blue"))

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


# ==================== CAD集成命令 ====================


@cli.command()
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

        # 打开文件
        if open:
            console.print(f"[dim]正在打开: {open}...[/dim]")
            if connector.open_document(open):
                console.print("[green]成功[/green] 文件已打开")
            else:
                console.print("[red]失败 无法打开文件[/red]")
                return

        # 列出参数
        if list_params:
            params = connector.get_parameters()
            if params:
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
            else:
                console.print("[yellow]未找到参数[/yellow]")

        # 设置参数
        if set_param:
            param_name, param_value = set_param
            param_value = float(param_value)

            console.print(f"[dim]设置参数: {param_name} = {param_value}...[/dim]")
            if connector.set_parameter(param_name, param_value):
                console.print("[green]成功[/green] 参数已更新")
            else:
                console.print("[red]失败 参数设置失败[/red]")

        # 重建
        if rebuild:
            console.print("[dim]重建模型...[/dim]")
            if connector.rebuild():
                console.print("[green]成功[/green] 重建完成")
            else:
                console.print("[yellow]⚠ 重建可能有问题[/yellow]")

        # 导出
        if export:
            console.print(f"[dim]导出到: {export}...[/dim]")
            if connector.export_file(export, format.upper()):
                console.print("[green]成功[/green] 导出成功")
                console.print(f"  路径: [bold]{export}[/bold]")
            else:
                console.print("[red]失败 导出失败[/red]")

        # 关闭连接
        manager.disconnect_all()

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


# ==================== 参数优化命令 ====================


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--parameter", "-p", required=True, help="Parameter name to optimize")
@click.option(
    "--param-range", "-r", nargs=2, type=float, required=True, help="Parameter range (min max)"
)
@click.option("--steps", "-s", type=int, default=5, help="Number of iterations")
@click.option(
    "--step-mode", "-m", type=click.Choice(["linear", "geometric"], case_sensitive=False),
    default="linear", help="Step mode: linear or geometric (default: linear)"
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
    ctx, file_path, parameter, param_range, steps, step_mode, cad, output, plot, report, output_dir, material
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
    from sw_helper.optimization.optimizer import FreeCADOptimizer
    from pathlib import Path

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
                    filename
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
            console.print(
                f"\n[dim]所有输出文件保存在: {Path(output_dir).absolute()}[/dim]"
            )

        else:
            console.print("[yellow]⚠️  没有获得优化结果[/yellow]")

    except FileNotFoundError as e:
        console.print(f"[red]失败 文件未找到: {e}[/red]")
        console.print("[dim]请检查文件路径是否正确[/dim]")
        sys.exit(1)
    except RuntimeError as e:
        console.print(f"[red]失败 运行时错误: {e}[/red]")
        if "FreeCAD" in str(e):
            console.print(
                "\n[yellow]提示: 如果您没有安装FreeCAD，可以使用模拟模式:[/yellow]"
            )
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


@cli.group()
def ai():
    """
    AI-assisted design functions

    Use AI to generate geometry and provide design suggestions
    """
    pass


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
@click.option("--analyze", "-a", is_flag=True, default=True, help="Run analysis and generate report")
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
    from pathlib import Path

    try:
        # 显示输入信息
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

        # 初始化生成器
        generator = AIModelGenerator(use_mock=mock)

        # 执行生成流程
        with console.status("[bold green]AI正在生成3D模型..."):
            result = generator.generate_with_analysis(
                description=description,
                output_dir=output_dir,
                name=name,
                generate_report=analyze,
            )

        if not result.get("success"):
            console.print(f"[red]失败 生成失败: {result.get('error', '未知错误')}[/red]")
            sys.exit(1)

        # 显示解析结果
        console.print("\n[cyan]解析结果 解析结果:[/cyan]")
        parsed = result["parsed_geometry"]
        console.print(f"  形状: [green]{parsed['shape_type']}[/green]")
        console.print("  参数:")
        for param, value in parsed["parameters"].items():
            console.print(f"    - {param}: [yellow]{value}[/yellow] mm")

        if parsed.get("features"):
            console.print(
                f"  特征: [magenta]{', '.join(f['type'] for f in parsed['features'])}[/magenta]"
            )

        # 显示输出文件
        console.print("\n[cyan]输出文件 输出文件:[/cyan]")
        files = result["output_files"]
        for file_type, file_path in files.items():
            file_size = (
                Path(file_path).stat().st_size / 1024 if Path(file_path).exists() else 0
            )
            console.print(
                f"  - {file_type.upper()}: [green]{file_path}[/green] ([dim]{file_size:.1f} KB[/dim])"
            )

        # 显示分析结果
        if "detailed_analysis" in result:
            console.print("\n[cyan]质量分析 质量分析:[/cyan]")
            analysis = result["detailed_analysis"]
            quality_score = analysis.get("quality_score", 0)

            # 根据分数设置颜色
            if quality_score >= 80:
                score_color = "green"
            elif quality_score >= 60:
                score_color = "yellow"
            else:
                score_color = "red"

            console.print(
                f"  质量评分: [{score_color}]{quality_score:.1f}/100[/{score_color}]"
            )

            if "geometry" in analysis:
                geo = analysis["geometry"]
                console.print(f"  体积: [dim]{geo.get('volume', 0):.2e} m^3[/dim]")
                console.print(f"  顶点数: [dim]{geo.get('vertices', 0)}[/dim]")

        # 显示报告路径
        if "report_path" in result:
            console.print(
                f"\n[cyan]报告 报告:[/cyan] [green]{result['report_path']}[/green]"
            )

        # 成功提示
        console.print(
            Panel.fit(
                "[bold green]成功 模型生成成功![/bold green]\n"
                f"FreeCAD模型: [blue]{files.get('fcstd', 'N/A')}[/blue]\n"
                f"STEP文件: [blue]{files.get('step', 'N/A')}[/blue]",
                border_style="green",
            )
        )

        # 提示下一步操作
        console.print("\n[cyan]建议操作:[/cyan]")
        console.print(
            f"  1. 查看模型: [dim]cae-cli parse {files.get('step', '')}[/dim]"
        )
        console.print(
            f"  2. 运行优化: [dim]cae-cli optimize {files.get('fcstd', '')} -p Radius -r 1 10[/dim]"
        )
        console.print(f"  3. 分析报告: [dim]cat {result.get('report_path', '')}[/dim]")

        # 如果指定了--open，尝试打开FreeCAD
        if open and not mock:
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
                except:
                    console.print(
                        "[yellow]⚠️  无法自动打开FreeCAD，请手动打开文件[/yellow]"
                    )

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        if mock:
            console.print("\n[yellow]提示: 模拟模式下可以正常使用所有功能[/yellow]")
        else:
            console.print(
                "\n[yellow]提示: 如果未安装FreeCAD，请使用 --mock 参数[/yellow]"
            )
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
        current_params = {"wall_thickness": 5, "fillet_radius": 3, "material": material or "Q235"}

        mock_metrics = {"max_stress": 180e6, "safety_factor": 1.8, "weight": 2.5}

        # 从知识库获取材料知识
        knowledge_text = ""
        if material:
            kb = get_knowledge_base()
            knowledge_text = kb.get_knowledge_text(material)

        suggestions = ai_gen.generate_optimization_suggestions(
            current_params, mock_metrics, target, knowledge_text
        )

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


@cli.command()
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
def macro(output_dir, type, format, cli_path):
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
    from sw_helper.integrations.sw_macro import SolidWorksMacroGenerator
    from pathlib import Path

    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        console.print("[bold cyan]🔧 生成SolidWorks宏[/bold cyan]")
        console.print(f"输出目录: {output_path}")
        console.print(f"宏类型: {type}")
        console.print("-" * 60)

        generator = SolidWorksMacroGenerator()

        if type in ["export", "full"]:
            # 生成导出宏
            macro_code = generator.generate_export_macro(
                output_path=str(output_path / "exported.step"),
                export_format=format.upper(),
                call_cli=(type == "full"),
                cli_path=cli_path,
            )

            macro_file = output_path / "CAE_Export.bas"
            generator.save_macro(macro_code, str(macro_file))
            console.print(f"[green]成功[/green] 导出宏: {macro_file}")

        if type in ["parametric", "full"]:
            # 生成参数宏
            macro_code = generator.generate_parameter_macro()
            macro_file = output_path / "CAE_Parametric.bas"
            generator.save_macro(macro_code, str(macro_file))
            console.print(f"[green]成功[/green] 参数宏: {macro_file}")

        if type == "full":
            # 生成完整集成宏
            macro_code = generator.generate_full_integration_macro(cli_path)
            macro_file = output_path / "CAE_FullIntegration.bas"
            generator.save_macro(macro_code, str(macro_file))
            console.print(f"[green]成功[/green] 完整集成宏: {macro_file}")

        console.print("\n[cyan]使用方法:[/cyan]")
        console.print("1. 在SolidWorks中按 Alt+F11 打开VBA编辑器")
        console.print("2. 文件 -> 导入文件，选择生成的.bas文件")
        console.print("3. 运行宏即可实现自动化导出和分析")

        if type == "full":
            console.print("\n[dim]完整集成宏功能:[/dim]")
            console.print("  - 修改圆角参数")
            console.print("  - 重建模型")
            console.print("  - 导出STEP文件")
            console.print("  - 调用CLI分析")
            console.print("  - 显示报告路径")
            console.print("  - 支持优化循环")

    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        console.print_exception()


# ==================== Chat交互命令 ====================


@cli.command()
@click.option(
    "--model",
    "-m",
    type=click.Choice(["openai", "anthropic", "deepseek", "ollama", "auto"]),
    default="auto",
    help="AI model provider",
)
@click.option("--api-key", "-k", help="API key")
@click.option("--mock", is_flag=True, help="Use mock mode (no AI required)")
def chat(model, api_key, mock):
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
        cae-cli chat --model openai --api-key sk-xxx

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
    from sw_helper.chat.interactive import OpencodeStyleChat
    from sw_helper.ai.llm_client import (
        LLMClient,
        LLMConfig,
        LLMProvider,
        create_openai_client,
        create_anthropic_client,
        create_ollama_client,
    )

    try:
        console.print(
            Panel.fit(
                "[bold cyan]🚀 启动CAE-CLI智能助手[/bold cyan]\n"
                "集成MCP + LLM + FreeCAD的交互式设计环境",
                border_style="cyan",
            )
        )

        chat_instance = OpencodeStyleChat()

        # 配置LLM
        if not mock and model != "auto":
            if model == "openai":
                api_key = api_key or click.prompt(
                    "OpenAI API Key", hide_input=True, confirmation_prompt=False
                )
                chat_instance.llm_client = create_openai_client(api_key=api_key)
            elif model == "anthropic":
                api_key = api_key or click.prompt(
                    "Anthropic API Key", hide_input=True, confirmation_prompt=False
                )
                from sw_helper.ai.llm_client import create_anthropic_client

                chat_instance.llm_client = create_anthropic_client(api_key=api_key)
            elif model == "deepseek":
                api_key = api_key or click.prompt(
                    "DeepSeek API Key", hide_input=True, confirmation_prompt=False
                )
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

        # 启动聊天
        asyncio.run(chat_instance.start())

    except KeyboardInterrupt:
        console.print("\n[yellow]再见！[/yellow]")
    except Exception as e:
        console.print(f"[red]失败 错误: {e}[/red]")
        raise


# ==================== MCP工具命令 ====================


@cli.group()
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
    from rich.console import Console

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
        highlighted_content = kb.highlight_keyword(result['content'], keyword)

        # 显示结果
        from rich.panel import Panel
        panel = Panel(
            highlighted_content,
            title=f"[green]{result['title']}[/green]",
            subtitle=f"[dim]{result['filename']}[/dim]",
            border_style="cyan",
            expand=False
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
    from sw_helper.knowledge import get_knowledge_base
    from rich.console import Console

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
        highlighted_content = kb.highlight_keyword(result['content'], material_name)

        from rich.panel import Panel
        panel = Panel(
            highlighted_content,
            title=f"[green]{result['title']}[/green]",
            subtitle=f"[dim]{result['filename']}[/dim]",
            border_style="cyan",
            expand=False
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
    from sw_helper.knowledge import get_knowledge_base
    from rich.console import Console

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
        highlighted_content = kb.highlight_keyword(result['content'], bolt_spec)

        from rich.panel import Panel
        panel = Panel(
            highlighted_content,
            title=f"[green]{result['title']}[/green]",
            subtitle=f"[dim]{result['filename']}[/dim]",
            border_style="cyan",
            expand=False
        )
        console.print(panel)
        console.print()


@cli.command()
def interactive():
    """
    Interactive mode - use CAE-CLI through a menu interface

    Features:
        1. Analyze model
        2. Parameter optimization
        3. AI generate model
        4. Exit

    Support direct command input like: "analyze test.step --material 40Cr"
    """
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    while True:
        try:
            # 显示菜单
            console.clear()

            # 创建菜单表格
            menu_table = Table(title="CAE-CLI Interactive Mode", show_header=True, header_style="bold cyan")
            menu_table.add_column("Option", style="cyan", width=5)
            menu_table.add_column("Operation", style="green")
            menu_table.add_column("Description", style="dim")

            menu_table.add_row("1", "Analyze Model", "Analyze geometry or mesh quality")
            menu_table.add_row("2", "Optimize Parameter", "Parameter optimization")
            menu_table.add_row("3", "AI Generate Model", "AI model generation")
            menu_table.add_row("4", "Exit", "Exit interactive mode")

            console.print(menu_table)
            console.print("\n[dim]Type a command directly (e.g., 'analyze test.step') to execute[/dim]")

            # 获取用户输入
            choice = Prompt.ask("\nEnter your choice (1-4) or command")

            if choice == "1":
                # 分析模型
                file_path = Prompt.ask("Enter model file path")
                if file_path:
                    # 支持多种分析选项
                    console.print("\n[cyan]Analysis options:[/cyan]")
                    console.print("  - [bold]parse[/bold]: Parse geometry file")
                    console.print("  - [bold]analyze[/bold]: Analyze mesh quality")
                    console.print("  - [bold]material[/bold]: Query material properties")

                    analysis_type = Prompt.ask("Enter analysis type", default="parse")

                    if analysis_type == "parse":
                        from sw_helper.geometry.parser import GeometryParser
                        try:
                            parser = GeometryParser()
                            result = parser.parse(file_path)
                            console.print_json(data=result)
                        except Exception as e:
                            console.print(f"[red]Error: {e}[/red]")

                    elif analysis_type == "analyze":
                        from sw_helper.mesh.quality import MeshQualityAnalyzer
                        try:
                            analyzer = MeshQualityAnalyzer()
                            results = analyzer.analyze(file_path)
                            console.print_json(data=results)
                        except Exception as e:
                            console.print(f"[red]Error: {e}[/red]")

                    elif analysis_type == "material":
                        material_name = Prompt.ask("Enter material name")
                        if material_name:
                            from sw_helper.material.database import MaterialDatabase
                            try:
                                db = MaterialDatabase()
                                material_info = db.get_material(material_name)
                                if material_info:
                                    console.print_json(data=material_info)
                                else:
                                    console.print(f"[yellow]Material '{material_name}' not found[/yellow]")
                            except Exception as e:
                                console.print(f"[red]Error: {e}[/red]")

            elif choice == "2":
                # 参数优化
                file_path = Prompt.ask("Enter CAD file path (.FCStd)")
                if file_path:
                    parameter = Prompt.ask("Enter parameter to optimize")
                    if parameter:
                        param_range = Prompt.ask("Enter parameter range (min max)", default="2 15")
                        steps = Prompt.ask("Enter number of steps", default="5")

                        try:
                            min_val, max_val = map(float, param_range.split())
                            steps_int = int(steps)

                            from sw_helper.optimization.optimizer import FreeCADOptimizer
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
                                analyze_geometry=True
                            )

                            if results:
                                best = max(results, key=lambda x: x.quality_score)
                                console.print(f"\n[green]Best result:[/green]")
                                console.print(f"Parameter: {best.parameter_name} = {best.parameter_value:.2f} mm")
                                console.print(f"Quality Score: {best.quality_score:.1f}/100")
                                console.print(f"Allowable Stress: {best.allowable_stress:.1f} MPa")
                                console.print(f"Safety Factor: {best.safety_factor:.2f}")
                            else:
                                console.print("[yellow]No results obtained[/yellow]")

                        except Exception as e:
                            console.print(f"[red]Error: {e}[/red]")

            elif choice == "3":
                # AI生成模型
                description = Prompt.ask("Enter model description")
                if description:
                    from sw_helper.ai.model_generator import AIModelGenerator

                    generator = AIModelGenerator()

                    try:
                        result = generator.generate(description)
                        console.print_json(data=result)
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")

            elif choice == "4":
                # 退出
                console.print("\n[green]Thank you for using CAE-CLI![/green]")
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
                        cwd=Path(__file__).parent.parent.parent
                    )

                    if result.stdout:
                        console.print(result.stdout)
                    if result.stderr:
                        console.print(f"[red]Error: {result.stderr}[/red]")

                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")

            else:
                console.print("[yellow]Please enter a valid choice or command[/yellow]")

            # 按任意键继续
            if choice not in ["4"]:
                try:
                    Prompt.ask("\nPress Enter to continue...", default="")
                except EOFError:
                    break

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            try:
                Prompt.ask("\nPress Enter to continue...", default="")
            except EOFError:
                break


@cli.group()
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
    from sw_helper.mcp.core import MCPMessage, InMemoryMCPTransport
    from sw_helper.mcp.freecad_server import get_freecad_mcp_server
    import asyncio

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
            message = MCPMessage(
                method="tools/call", params={"name": tool_name, "arguments": args}
            )

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
                    except:
                        console.print(result_text)
            elif response.error:
                console.print(f"\n[red]失败 错误: {response.error.get('message')}[/red]")

        except Exception as e:
            console.print(f"[red]失败 执行失败: {e}[/red]")

    asyncio.run(run_tool())


# 入口点
if __name__ == "__main__":
    cli()
