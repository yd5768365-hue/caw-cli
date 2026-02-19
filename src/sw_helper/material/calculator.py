"""
材料力学计算模块
"""

import numpy as np
from typing import Dict, Optional
from .database import MaterialDatabase


class MechanicsCalculator:
    """力学计算器"""

    def __init__(self):
        self.db = MaterialDatabase()

    def calculate_stress(
        self, force: float, area: float, material_name: Optional[str] = None
    ) -> Dict[str, float]:
        """计算应力

        Args:
            force: 受力 (N)
            area: 截面积 (m²)
            material_name: 材料名称（可选，用于获取许用应力）

        Returns:
            应力计算结果
        """
        stress = force / area

        result = {"stress": stress, "safety_factor": None}

        if material_name:
            material = self.db.get_material(material_name)
            if material:
                yield_strength = material.get("yield_strength", 0)
                if yield_strength > 0:
                    result["safety_factor"] = yield_strength / stress
                    result["yield_strength"] = yield_strength

        return result

    def calculate_strain(self, stress: float, material_name: str) -> Dict[str, float]:
        """计算应变

        Args:
            stress: 应力 (Pa)
            material_name: 材料名称

        Returns:
            应变计算结果
        """
        material = self.db.get_material(material_name)
        if not material:
            raise ValueError(f"未知材料: {material_name}")

        E = material.get("elastic_modulus", 0)
        if E == 0:
            raise ValueError(f"材料 {material_name} 缺少弹性模量数据")

        strain = stress / E

        return {"strain": strain, "elastic_modulus": E}

    def calculate_deflection(
        self,
        load: float,
        length: float,
        elastic_modulus: float,
        moment_of_inertia: float,
    ) -> float:
        """计算简支梁挠度

        Args:
            load: 载荷 (N)
            length: 梁长度 (m)
            elastic_modulus: 弹性模量 (Pa)
            moment_of_inertia: 截面惯性矩 (m⁴)

        Returns:
            最大挠度 (m)
        """
        # 简支梁中点集中载荷: δ = PL³/(48EI)
        return (load * length**3) / (48 * elastic_modulus * moment_of_inertia)

    def calculate_buckling_load(
        self,
        elastic_modulus: float,
        moment_of_inertia: float,
        length: float,
        end_condition: str = "pinned",
    ) -> float:
        """计算屈曲临界载荷（欧拉公式）

        Args:
            elastic_modulus: 弹性模量 (Pa)
            moment_of_inertia: 截面惯性矩 (m⁴)
            length: 柱长度 (m)
            end_condition: 端部约束条件 ('fixed', 'pinned', 'free')

        Returns:
            临界屈曲载荷 (N)
        """
        # 端部系数
        K_map = {"fixed": 0.5, "pinned": 1.0, "fixed-pinned": 0.7, "fixed-free": 2.0}
        K = K_map.get(end_condition, 1.0)

        # 欧拉公式: Pcr = π²EI/(KL)²
        return (np.pi**2 * elastic_modulus * moment_of_inertia) / (K * length) ** 2

    def thermal_stress(
        self,
        temperature_change: float,
        elastic_modulus: float,
        thermal_expansion: float,
        constraint: str = "fully",
    ) -> float:
        """计算热应力

        Args:
            temperature_change: 温度变化 (K)
            elastic_modulus: 弹性模量 (Pa)
            thermal_expansion: 热膨胀系数 (1/K)
            constraint: 约束条件

        Returns:
            热应力 (Pa)
        """
        if constraint == "fully":
            return elastic_modulus * thermal_expansion * temperature_change
        elif constraint == "partial":
            return 0.5 * elastic_modulus * thermal_expansion * temperature_change
        else:
            return 0.0
