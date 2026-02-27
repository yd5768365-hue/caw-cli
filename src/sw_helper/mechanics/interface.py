"""
力学模块接口
为CLI提供统一的力学计算接口，并处理报告渲染
"""

import json
from typing import Any, Dict, Optional

import numpy as np

try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from .engine import MechanicsEngine


class MechanicsInterface:
    """力学模块接口类"""

    def __init__(self, materials_db_path: Optional[str] = None):
        """
        初始化力学接口

        Args:
            materials_db_path: 材料数据库路径
        """
        self.engine = MechanicsEngine(materials_db_path)
        self.console = Console() if HAS_RICH else None

    def check_strength(
        self,
        model_file: Optional[str] = None,
        force: Optional[float] = None,
        material: Optional[str] = None,
        force_unit: str = "N",
        stress_tensor: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        强度检查（主入口函数）

        Args:
            model_file: 模型文件路径（可选，未来扩展）
            force: 施加的力
            material: 材料名称
            force_unit: 力的单位
            stress_tensor: 应力张量（如果直接提供）

        Returns:
            强度分析结果
        """
        # 如果没有提供应力张量，尝试从模型文件计算
        # 目前先使用示例应力张量
        if stress_tensor is None:
            # 创建一个示例应力张量（未来从模型文件解析）
            stress_tensor = np.array([[100e6, 20e6, 0], [20e6, 50e6, 0], [0, 0, 0]])

        if material is None:
            material = "Q235"  # 默认材料

        # 执行应力分析
        result = self.engine.calculate_stress_analysis(
            stress_tensor=stress_tensor,
            material_name=material,
            applied_force=force,
            force_unit=force_unit,
        )

        # 添加额外信息
        result["model_file"] = model_file
        result["analysis_type"] = "strength_check"

        return result

    def check_buckling(
        self,
        material: str,
        cross_section_area: float,
        moment_of_inertia: float,
        length: float,
        applied_force: float,
        end_condition: str = "pinned-pinned",
        area_unit: str = "m^2",
        length_unit: str = "m",
        force_unit: str = "N",
    ) -> Dict[str, Any]:
        """
        屈曲检查

        Args:
            material: 材料名称
            cross_section_area: 截面积
            moment_of_inertia: 截面惯性矩
            length: 长度
            applied_force: 施加的力
            end_condition: 边界条件
            area_unit: 面积单位
            length_unit: 长度单位
            force_unit: 力单位

        Returns:
            屈曲分析结果
        """
        return self.engine.calculate_buckling_safety(
            material_name=material,
            cross_section_area=cross_section_area,
            moment_of_inertia=moment_of_inertia,
            length=length,
            applied_force=applied_force,
            end_condition=end_condition,
            area_unit=area_unit,
            length_unit=length_unit,
            force_unit=force_unit,
        )

    def check_deflection(
        self,
        load: float,
        length: float,
        material: str,
        moment_of_inertia: float,
        load_type: str = "point_center",
        load_unit: str = "N",
        length_unit: str = "m",
    ) -> Dict[str, Any]:
        """
        挠度检查

        Args:
            load: 载荷
            length: 长度
            material: 材料名称
            moment_of_inertia: 截面惯性矩
            load_type: 载荷类型
            load_unit: 载荷单位
            length_unit: 长度单位

        Returns:
            挠度分析结果
        """
        return self.engine.calculate_deflection_analysis(
            load=load,
            length=length,
            material_name=material,
            moment_of_inertia=moment_of_inertia,
            load_type=load_type,
            load_unit=load_unit,
            length_unit=length_unit,
        )

    def generate_report(self, analysis_results: Dict[str, Any], output_format: str = "rich") -> str:
        """
        生成分析报告

        Args:
            analysis_results: 分析结果
            output_format: 输出格式 ("rich", "json", "text")

        Returns:
            报告字符串
        """
        if output_format == "json":
            return json.dumps(analysis_results, indent=2, ensure_ascii=False)

        if output_format == "rich" and HAS_RICH and self.console:
            return self._generate_rich_report(analysis_results)

        # 默认文本格式
        return self._generate_text_report(analysis_results)

    def _generate_rich_report(self, results: Dict[str, Any]) -> str:
        """生成Rich格式报告"""
        from rich.console import Console

        console = Console()

        # 创建输出字符串
        with console.capture() as capture:
            self._render_rich_report(console, results)

        return capture.get()

    def _render_rich_report(self, console, results: Dict[str, Any]):
        """渲染Rich报告到控制台"""
        analysis_type = results.get("analysis_type", "unknown")

        # 标题
        console.print(
            Panel.fit(
                f"[bold cyan]CAE-CLI 力学分析报告[/bold cyan]\n" f"[dim]分析类型: {analysis_type}[/dim]",
                border_style="cyan",
            )
        )

        # 材料特征部分
        material = results.get("material", "未知材料")
        material_type = results.get("material_type", "未知类型")

        material_table = Table(title="材料特征", box=box.ROUNDED, show_header=False)
        material_table.add_column("属性", style="cyan")
        material_table.add_column("值", style="white")

        material_table.add_row("材料名称", material)
        material_table.add_row("材料类型", material_type)

        if "yield_strength" in results:
            material_table.add_row("屈服强度", f"{results['yield_strength'] / 1e6:.2f} MPa")
        if "tensile_strength" in results:
            material_table.add_row("抗拉强度", f"{results['tensile_strength'] / 1e6:.2f} MPa")

        console.print(material_table)
        console.print()

        # 公式计算路径
        if analysis_type == "strength_check":
            self._render_strength_formulas(console, results)
        elif "buckling_safety_factor" in results:
            self._render_buckling_formulas(console, results)
        elif "deflection_safety_factor" in results:
            self._render_deflection_formulas(console, results)

        # 安全系数显示
        self._render_safety_factor(console, results)

    def _render_strength_formulas(self, console, results: Dict[str, Any]):
        """渲染强度计算公式"""
        formulas_panel = Panel(
            "[bold]应力分析公式:[/bold]\n"
            "1. Von Mises等效应力: σ_vm = √[0.5((σ₁-σ₂)²+(σ₂-σ₃)²+(σ₃-σ₁)²)+3(τ₁₂²+τ₂₃²+τ₃₁²)]\n"
            "2. 安全系数: SF = σ_yield / σ_vm (塑性材料)\n"
            "3. 主应力: σ₁ ≥ σ₂ ≥ σ₃ (特征值分解)",
            title="计算路径",
            border_style="blue",
        )
        console.print(formulas_panel)

        # 显示具体数值
        if "von_mises_stress" in results:
            vm_stress = results["von_mises_stress"] / 1e6  # 转换为MPa
            principal = results.get("principal_stresses", (0, 0, 0))

            stress_table = Table(title="应力结果", box=box.SIMPLE)
            stress_table.add_column("应力类型", style="cyan")
            stress_table.add_column("数值 (MPa)", style="white")
            stress_table.add_column("状态", style="green")

            stress_table.add_row(
                "Von Mises等效应力",
                f"{vm_stress:.2f}",
                "[green]✓" if vm_stress < 235 else "[red]✗",
            )

            for i, stress in enumerate(principal, 1):
                stress_mpa = stress / 1e6
                stress_table.add_row(f"主应力 σ{i}", f"{stress_mpa:.2f}", "")

            console.print(stress_table)
            console.print()

    def _render_buckling_formulas(self, console, results: Dict[str, Any]):
        """渲染屈曲计算公式"""
        formulas_panel = Panel(
            "[bold]屈曲分析公式:[/bold]\n"
            "1. 欧拉临界载荷: P_cr = π²EI/(KL)²\n"
            "2. 屈曲安全系数: SF_buckling = P_cr / P_applied\n"
            "3. 压缩应力: σ_comp = P_applied / A",
            title="计算路径",
            border_style="blue",
        )
        console.print(formulas_panel)

        # 显示具体数值
        buckling_table = Table(title="屈曲分析结果", box=box.SIMPLE)
        buckling_table.add_column("参数", style="cyan")
        buckling_table.add_column("数值", style="white")
        buckling_table.add_column("单位", style="dim")

        buckling_table.add_row(
            "临界屈曲载荷",
            f"{results.get('critical_buckling_load', 0) / 1000:.2f}",
            "kN",
        )
        buckling_table.add_row("施加载荷", f"{results.get('applied_force', 0) / 1000:.2f}", "kN")
        buckling_table.add_row("屈曲安全系数", f"{results.get('buckling_safety_factor', 0):.2f}", "")
        buckling_table.add_row("压缩应力", f"{results.get('compressive_stress', 0) / 1e6:.2f}", "MPa")

        console.print(buckling_table)
        console.print()

    def _render_deflection_formulas(self, console, results: Dict[str, Any]):
        """渲染挠度计算公式"""
        formulas_panel = Panel(
            "[bold]挠度分析公式:[/bold]\n"
            "1. 简支梁中点集中载荷: δ = PL³/(48EI)\n"
            "2. 允许挠度: δ_allow = L/250\n"
            "3. 挠度安全系数: SF_deflection = δ_allow / δ",
            title="计算路径",
            border_style="blue",
        )
        console.print(formulas_panel)

        # 显示具体数值
        deflection_table = Table(title="挠度分析结果", box=box.SIMPLE)
        deflection_table.add_column("参数", style="cyan")
        deflection_table.add_column("数值", style="white")
        deflection_table.add_column("单位", style="dim")

        deflection = results.get("deflection", 0) * 1000  # 转换为mm
        allowable = results.get("allowable_deflection", 0) * 1000

        deflection_table.add_row("计算挠度", f"{deflection:.3f}", "mm")
        deflection_table.add_row("允许挠度", f"{allowable:.3f}", "mm")
        deflection_table.add_row("挠度安全系数", f"{results.get('deflection_safety_factor', 0):.2f}", "")

        console.print(deflection_table)
        console.print()

    def _render_safety_factor(self, console, results: Dict[str, Any]):
        """渲染安全系数（带颜色预警）"""
        safety_factor = None
        factor_name = ""

        # 确定使用哪个安全系数
        if "safety_factor" in results:
            safety_factor = results["safety_factor"]
            factor_name = "强度安全系数"
        elif "buckling_safety_factor" in results:
            safety_factor = results["buckling_safety_factor"]
            factor_name = "屈曲安全系数"
        elif "deflection_safety_factor" in results:
            safety_factor = results["deflection_safety_factor"]
            factor_name = "挠度安全系数"

        if safety_factor is not None:
            # 确定颜色
            if safety_factor < 1.0:
                color = "red"
                status = "危险"
            elif safety_factor < 1.5:
                color = "yellow"
                status = "警告"
            else:
                color = "green"
                status = "安全"

            # 创建安全系数面板
            safety_text = Text()
            safety_text.append(f"{factor_name}: ", style="bold")
            safety_text.append(f"{safety_factor:.3f}", style=f"bold {color}")
            safety_text.append(f" ({status})", style=color)

            safety_panel = Panel(safety_text, title="安全评估", border_style=color)
            console.print(safety_panel)

            # 添加结论
            conclusion = "结论: 设计"
            if safety_factor < 1.0:
                conclusion += " [red bold]不满足[/red bold] 安全要求，需要重新设计。"
            elif safety_factor < 1.5:
                conclusion += " [yellow bold]基本满足[/yellow bold] 安全要求，建议优化。"
            else:
                conclusion += " [green bold]完全满足[/green bold] 安全要求，设计合理。"

            console.print(conclusion)

    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """生成文本格式报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("CAE-CLI 力学分析报告")
        lines.append(f"分析类型: {results.get('analysis_type', 'unknown')}")
        lines.append("=" * 60)

        # 材料特征
        lines.append("\n[材料特征]")
        lines.append(f"  材料名称: {results.get('material', '未知材料')}")
        lines.append(f"  材料类型: {results.get('material_type', '未知类型')}")

        if "yield_strength" in results:
            lines.append(f"  屈服强度: {results['yield_strength'] / 1e6:.2f} MPa")
        if "tensile_strength" in results:
            lines.append(f"  抗拉强度: {results['tensile_strength'] / 1e6:.2f} MPa")

        # 计算结果
        if "von_mises_stress" in results:
            lines.append("\n[应力分析结果]")
            lines.append(f"  Von Mises等效应力: {results['von_mises_stress'] / 1e6:.2f} MPa")
            principal = results.get("principal_stresses", (0, 0, 0))
            for i, stress in enumerate(principal, 1):
                lines.append(f"  主应力 σ{i}: {stress / 1e6:.2f} MPa")

        if "buckling_safety_factor" in results:
            lines.append("\n[屈曲分析结果]")
            lines.append(f"  临界屈曲载荷: {results.get('critical_buckling_load', 0) / 1000:.2f} kN")
            lines.append(f"  施加载荷: {results.get('applied_force', 0) / 1000:.2f} kN")
            lines.append(f"  屈曲安全系数: {results.get('buckling_safety_factor', 0):.2f}")

        if "deflection_safety_factor" in results:
            lines.append("\n[挠度分析结果]")
            deflection = results.get("deflection", 0) * 1000
            allowable = results.get("allowable_deflection", 0) * 1000
            lines.append(f"  计算挠度: {deflection:.3f} mm")
            lines.append(f"  允许挠度: {allowable:.3f} mm")
            lines.append(f"  挠度安全系数: {results.get('deflection_safety_factor', 0):.2f}")

        # 安全系数
        safety_factor = None
        if "safety_factor" in results:
            safety_factor = results["safety_factor"]
        elif "buckling_safety_factor" in results:
            safety_factor = results["buckling_safety_factor"]
        elif "deflection_safety_factor" in results:
            safety_factor = results["deflection_safety_factor"]

        if safety_factor is not None:
            lines.append("\n[安全评估]")
            lines.append(f"  安全系数: {safety_factor:.3f}")
            if safety_factor < 1.0:
                lines.append("  状态: 危险 (安全系数 < 1.0)")
                lines.append("  结论: 设计不满足安全要求，需要重新设计。")
            elif safety_factor < 1.5:
                lines.append("  状态: 警告 (1.0 ≤ 安全系数 < 1.5)")
                lines.append("  结论: 设计基本满足安全要求，建议优化。")
            else:
                lines.append("  状态: 安全 (安全系数 ≥ 1.5)")
                lines.append("  结论: 设计完全满足安全要求，设计合理。")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
