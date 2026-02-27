"""
简易 FEM 求解器 - 内置，无需额外安装

基于简化梁理论的分析求解器，适合教学演示和简单结构分析。
"""

from .base import BaseSolver, SolverConfig, SolverResult


class SimpleFEMSolver(BaseSolver):
    """简易 FEM 求解器

    基于材料力学公式的简化求解器：
    - 简支梁弯曲
    - 悬臂梁弯曲
    - 简单应力分析

    适用于教学演示和初步设计估算。
    """

    name = "simple"
    description = "简易求解器 (内置，基于材料力学公式)"
    requires_install = None

    def is_available(self) -> bool:
        """始终可用（内置）"""
        return True

    def solve(self, config: SolverConfig) -> SolverResult:
        """执行简支梁弯曲分析

        基于材料力学公式：
        - 最大位移: δ = P*L³/(48*E*I)  (集中载荷中点)
        - 最大应力: σ = P*L/(4*W)      (中点上下表面)
        """
        # 提取参数
        material = config.material or {}
        E = material.get("elastic_modulus", 210e9)  # 弹性模量 (Pa)
        sigma_yield = material.get("yield_strength", 235e6)  # 屈服强度 (Pa)
        load = config.load  # 载荷 (N)

        # 几何参数（默认简支梁）
        geometry = config.geometry or {}
        length = geometry.get("length", 1000)  # 梁长 (mm)
        width = geometry.get("width", 50)  # 截面宽 (mm)
        height = geometry.get("height", 100)  # 截面高 (mm)

        # 单位转换：mm -> m
        L = length / 1000  # m
        b = width / 1000  # m
        h = height / 1000  # m

        # 截面惯性矩 I = bh³/12
        I = (b * h**3) / 12

        # 截面模量 W = bh²/6
        W = (b * h**2) / 6

        # 计算位移和应力
        # 简支梁中点集中载荷
        max_displacement = (load * L**3) / (48 * E * I)  # m
        max_stress = (load * L) / (4 * W)  # Pa

        # 安全系数
        safety_factor = sigma_yield / max_stress if max_stress > 0 else float("inf")

        # 评估状态
        if safety_factor > 1.5:
            pass
        elif safety_factor > 1.0:
            pass
        else:
            pass

        return SolverResult(
            max_displacement=max_displacement,
            max_stress=max_stress,
            safety_factor=safety_factor,
            displacement={
                "mid_span": max_displacement,
                "L/4": max_displacement * 0.5,
                "3L/4": max_displacement * 0.5,
            },
            stress={
                "top_fiber": max_stress,
                "bottom_fiber": -max_stress,
                "neutral_axis": 0,
            },
            messages=(
                f"简支梁分析 - 长度 {length}mm, 截面 {width}x{height}mm\n"
                f"材料: E={E/1e9:.0f}GPa, σyield={sigma_yield/1e6:.0f}MPa"
            ),
        )


class SimpleFEMSolver2D(BaseSolver):
    """2D 平面应力简易求解器

    基于有限元思想的简化2D平面应力分析。
    """

    name = "simple_2d"
    description = "2D 平面应力求解器 (内置)"
    requires_install = None

    def is_available(self) -> bool:
        return True

    def solve(self, config: SolverConfig) -> SolverResult:
        """2D 平面应力分析

        使用简化有限元方法分析平面应力问题。
        """
        material = config.material or {}
        E = material.get("elastic_modulus", 210e9)
        material.get("poisson_ratio", 0.3)
        sigma_yield = material.get("yield_strength", 235e6)

        load = config.load

        # 简化计算：假设矩形板承受均匀拉应力
        # σ = P/A
        geometry = config.geometry or {}
        thickness = geometry.get("thickness", 10) / 1000  # m
        width = geometry.get("width", 100) / 1000  # m

        area = thickness * width
        max_stress = load / area if area > 0 else 0

        # 简化位移计算
        max_displacement = (load * geometry.get("length", 1000) / 1000) / (E * area)

        safety_factor = sigma_yield / max_stress if max_stress > 0 else float("inf")


        return SolverResult(
            max_displacement=max_displacement,
            max_stress=max_stress,
            safety_factor=safety_factor,
            messages=f"2D平面应力分析 - 厚度 {thickness*1000:.1f}mm",
        )
