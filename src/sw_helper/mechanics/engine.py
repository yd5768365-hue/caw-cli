"""
力学计算引擎
整合材料数据库、单位转换和力学公式
"""

import json
import math
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import numpy as np

try:
    from rich.console import Console
    from rich.table import Table

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    import pint

    HAS_PINT = True
except ImportError:
    HAS_PINT = False

from .physics_formulas import (
    calculate_von_mises_stress,
    calculate_principal_stresses,
    calculate_safety_factor,
    calculate_buckling_load,
    calculate_deflection,
    calc_principal_stresses,
    calc_von_mises,
    calc_max_shear,
)


class MechanicsEngine:
    """力学计算引擎"""

    def __init__(self, materials_db_path: Optional[str] = None):
        """
        初始化力学计算引擎

        Args:
            materials_db_path: 材料数据库路径，默认为项目data/materials.json
        """
        # 加载材料数据库
        if materials_db_path is None:
            # 默认路径：项目根目录下的data/materials.json
            project_root = Path(__file__).parent.parent.parent.parent
            self.db_path = project_root / "data" / "materials.json"
        else:
            self.db_path = Path(materials_db_path)

        self.materials = self._load_materials()

        # 初始化单位转换系统
        self.ureg = None
        if HAS_PINT:
            self.ureg = pint.UnitRegistry()
            self._setup_units()

    def _load_materials(self) -> Dict[str, Any]:
        """加载材料数据库"""
        try:
            if self.db_path.exists():
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                raise FileNotFoundError(f"材料数据库不存在: {self.db_path}")
        except Exception as e:
            print(f"警告: 无法加载材料数据库: {e}")
            # 返回空数据库，允许程序继续运行
            return {}

    def _setup_units(self):
        """设置单位系统"""
        if not self.ureg:
            return

        # 定义常用单位别名
        self.ureg.define("newton_per_mm2 = newton / millimeter ** 2")
        self.ureg.define("MPa = megapascal")
        self.ureg.define("GPa = gigapascal")
        self.ureg.define("kN = kilonewton")

    def convert_units(self, value: float, from_unit: str, to_unit: str) -> float:
        """
        单位转换

        Args:
            value: 数值
            from_unit: 原单位
            to_unit: 目标单位

        Returns:
            转换后的数值
        """
        if not self.ureg:
            # 如果没有pint，进行简单转换
            return self._simple_unit_conversion(value, from_unit, to_unit)

        try:
            quantity = value * self.ureg(from_unit)
            converted = quantity.to(to_unit)
            return converted.magnitude
        except Exception as e:
            print(f"单位转换失败 {from_unit} -> {to_unit}: {e}")
            return value

    def _simple_unit_conversion(
        self, value: float, from_unit: str, to_unit: str
    ) -> float:
        """简单单位转换（用于没有pint的情况）"""
        # 常用单位转换映射
        pressure_conversions = {
            ("MPa", "Pa"): lambda x: x * 1e6,
            ("Pa", "MPa"): lambda x: x / 1e6,
            ("N/mm^2", "Pa"): lambda x: x * 1e6,
            ("Pa", "N/mm^2"): lambda x: x / 1e6,
            ("GPa", "Pa"): lambda x: x * 1e9,
            ("Pa", "GPa"): lambda x: x / 1e9,
        }

        force_conversions = {
            ("kN", "N"): lambda x: x * 1000,
            ("N", "kN"): lambda x: x / 1000,
        }

        length_conversions = {
            ("mm", "m"): lambda x: x / 1000,
            ("m", "mm"): lambda x: x * 1000,
            ("cm", "m"): lambda x: x / 100,
            ("m", "cm"): lambda x: x * 100,
        }

        # 合并所有转换
        all_conversions = {
            **pressure_conversions,
            **force_conversions,
            **length_conversions,
        }

        key = (from_unit, to_unit)
        if key in all_conversions:
            return all_conversions[key](value)

        # 如果单位相同
        if from_unit == to_unit:
            return value

        raise ValueError(f"不支持的单位转换: {from_unit} -> {to_unit}")

    def get_material(self, material_name: str) -> Dict[str, Any]:
        """
        获取材料属性

        Args:
            material_name: 材料名称

        Returns:
            材料属性字典

        Raises:
            KeyError: 材料不存在时抛出
        """
        material = self.materials.get(material_name)
        if not material:
            raise KeyError(f"材料 '{material_name}' 不在数据库中")
        return material

    def determine_material_type(self, material_name: str) -> str:
        """
        判断材料类型（塑性/脆性）

        Args:
            material_name: 材料名称

        Returns:
            "ductile" (塑性) 或 "brittle" (脆性)
        """
        material = self.get_material(material_name)
        material_type = material.get("type", "")

        # 基于材料类型判断
        brittle_keywords = ["铸铁", "陶瓷", "玻璃", "脆性"]
        ductile_keywords = ["钢", "铝", "铜", "塑性", "韧"]

        material_type_lower = material_type.lower()

        for keyword in brittle_keywords:
            if keyword in material_type_lower:
                return "brittle"

        # 默认为塑性材料
        return "ductile"

    def calculate_stress_analysis(
        self,
        stress_tensor: np.ndarray,
        material_name: str,
        applied_force: Optional[float] = None,
        force_unit: str = "N",
    ) -> Dict[str, Any]:
        """
        综合应力分析

        Args:
            stress_tensor: 3x3应力张量 (Pa)
            material_name: 材料名称
            applied_force: 施加的力（可选）
            force_unit: 力的单位

        Returns:
            应力分析结果字典
        """
        # 获取材料属性
        material = self.get_material(material_name)
        yield_strength = material.get("yield_strength", 0)
        tensile_strength = material.get("tensile_strength", 0)

        # 计算Von Mises应力
        von_mises = calculate_von_mises_stress(stress_tensor)

        # 计算主应力
        principal_stresses = calculate_principal_stresses(stress_tensor)

        # 判断材料类型
        material_type = self.determine_material_type(material_name)

        # 计算安全系数
        if material_type == "ductile":
            reference_strength = yield_strength
        else:
            reference_strength = tensile_strength

        safety_factor = calculate_safety_factor(
            applied_stress=von_mises,
            material_yield_strength=yield_strength,
            material_tensile_strength=tensile_strength,
            material_type=material_type,
        )

        # 单位转换（如果需要）
        if applied_force and force_unit != "N":
            applied_force = self.convert_units(applied_force, force_unit, "N")

        return {
            "material": material_name,
            "material_type": material_type,
            "von_mises_stress": von_mises,
            "principal_stresses": principal_stresses,
            "safety_factor": safety_factor,
            "yield_strength": yield_strength,
            "tensile_strength": tensile_strength,
            "applied_force": applied_force,
            "is_safe": safety_factor >= 1.0,
        }

    def calculate_buckling_safety(
        self,
        material_name: str,
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
        屈曲安全分析

        Args:
            material_name: 材料名称
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
        # 单位转换到SI
        area = self.convert_units(cross_section_area, area_unit, "m^2")
        length_m = self.convert_units(length, length_unit, "m")
        force_n = self.convert_units(applied_force, force_unit, "N")
        # 惯性矩单位是m^4，假设输入单位一致

        # 获取材料属性
        material = self.get_material(material_name)
        elastic_modulus = material.get("elastic_modulus", 0)

        # 计算屈曲临界载荷
        critical_load = calculate_buckling_load(
            youngs_modulus=elastic_modulus,
            moment_of_inertia=moment_of_inertia,
            length=length_m,
            end_condition=end_condition,
        )

        # 计算屈曲安全系数
        buckling_safety = critical_load / force_n if force_n > 0 else float("inf")

        # 计算压缩应力
        compressive_stress = force_n / area if area > 0 else 0

        return {
            "material": material_name,
            "elastic_modulus": elastic_modulus,
            "critical_buckling_load": critical_load,
            "applied_force": force_n,
            "buckling_safety_factor": buckling_safety,
            "compressive_stress": compressive_stress,
            "is_stable": buckling_safety >= 1.0,
        }

    def calculate_deflection_analysis(
        self,
        load: float,
        length: float,
        material_name: str,
        moment_of_inertia: float,
        load_type: str = "point_center",
        load_unit: str = "N",
        length_unit: str = "m",
    ) -> Dict[str, Any]:
        """
        挠度分析

        Args:
            load: 载荷
            length: 长度
            material_name: 材料名称
            moment_of_inertia: 截面惯性矩
            load_type: 载荷类型
            load_unit: 载荷单位
            length_unit: 长度单位

        Returns:
            挠度分析结果
        """
        # 单位转换
        load_n = self.convert_units(load, load_unit, "N")
        length_m = self.convert_units(length, length_unit, "m")

        # 获取材料属性
        material = self.get_material(material_name)
        elastic_modulus = material.get("elastic_modulus", 0)

        # 计算挠度
        deflection = calculate_deflection(
            load=load_n,
            length=length_m,
            youngs_modulus=elastic_modulus,
            moment_of_inertia=moment_of_inertia,
            load_type=load_type,
        )

        # 计算允许挠度（通常为长度的1/250）
        allowable_deflection = length_m / 250

        # 挠度安全系数
        deflection_safety = (
            allowable_deflection / deflection if deflection > 0 else float("inf")
        )

        return {
            "material": material_name,
            "elastic_modulus": elastic_modulus,
            "deflection": deflection,
            "allowable_deflection": allowable_deflection,
            "deflection_safety_factor": deflection_safety,
            "is_within_limit": deflection <= allowable_deflection,
        }

    @staticmethod
    def evaluate_material_theory(elongation: float) -> str:
        """
        根据材料伸长率判断材料类型

        判定规则（机械设计常规经验）：
            - 伸长率 > 5%  → 延性材料（Ductile）
            - 伸长率 ≤ 5% → 脆性材料（Brittle）

        参数：
            elongation (float): 断后伸长率，单位 %

        返回：
            str: "Ductile" 或 "Brittle"
        """
        return "Ductile" if elongation > 5.0 else "Brittle"

    def solve_safety_factor(
        self,
        force: float,
        area: float,
        material_name: str,
        force_unit: str = "N",
        area_unit: str = "m^2",
    ) -> Dict[str, Any]:
        """
        强度校核主函数（安全系数计算）

        计算流程：
            1. 单位统一（自动转为 SI）
            2. 计算名义正应力
            3. 计算主应力
            4. 根据材料延展性选择强度理论
            5. 计算等效应力
            6. 计算安全系数

        参数说明：
            force (float): 外载荷
            area  (float): 承载面积
            material_name (str): 材料名称
            force_unit (str): 力的单位
            area_unit (str): 面积的单位

        返回：
            Dict[str, Any]: 包含安全系数和详细计算结果
        """
        # 单位转换到SI
        force_si = self.convert_units(force, force_unit, "N")
        area_si = self.convert_units(area, area_unit, "m^2")

        # 计算名义应力
        sigma = force_si / area_si if area_si > 0 else 0

        # 假设单向受拉，平面应力状态
        sigma_x = sigma
        sigma_y = 0.0
        tau_xy = 0.0

        # 计算主应力
        s1, s2 = calc_principal_stresses(sigma_x, sigma_y, tau_xy)
        s3 = 0.0

        # 获取材料属性
        material = self.get_material(material_name)

        # 获取伸长率（如果不存在，根据材料类型推断）
        elongation = material.get("elongation")
        if elongation is None:
            # 根据材料类型推断：钢类通常为延性，铸铁类为脆性
            material_type = material.get("type", "").lower()
            if any(
                keyword in material_type for keyword in ["铸铁", "陶瓷", "玻璃", "脆性"]
            ):
                elongation = 3.0  # 脆性材料典型值
            else:
                elongation = 20.0  # 延性材料典型值

        # 判断材料类型
        material_type = self.evaluate_material_theory(elongation)

        # 获取材料强度
        yield_strength = material.get("yield_strength", 0)
        ultimate_strength = material.get("tensile_strength", 0)

        # 强度理论选择
        if material_type == "Ductile":
            theory = "von Mises (第四强度理论)"
            equivalent_stress = calc_von_mises(s1, s2, s3)
            allowable = yield_strength
        else:
            theory = "Max Shear (第三强度理论)"
            equivalent_stress = calc_max_shear(s1, s3)
            allowable = ultimate_strength

        # 计算安全系数
        safety_factor = (
            allowable / equivalent_stress if equivalent_stress > 0 else float("inf")
        )

        # 构建结果
        result = {
            "material": material_name,
            "force": force,
            "force_unit": force_unit,
            "area": area,
            "area_unit": area_unit,
            "nominal_stress": sigma,
            "principal_stresses": (s1, s2, s3),
            "material_type": material_type,
            "strength_theory": theory,
            "equivalent_stress": equivalent_stress,
            "allowable_strength": allowable,
            "safety_factor": safety_factor,
            "is_safe": safety_factor >= 1.0,
        }

        # 如果Rich可用，生成表格报告
        if HAS_RICH:
            console = Console()
            table = Table(title="CAE Safety Factor Evaluation")

            table.add_column("Item", style="cyan", no_wrap=True)
            table.add_column("Value", style="magenta")

            table.add_row("Force", f"{force} {force_unit}")
            table.add_row("Area", f"{area} {area_unit}")
            table.add_row("Nominal Stress", f"{sigma:.3e} Pa")
            table.add_row("Material Type", material_type)
            table.add_row("Strength Theory", theory)
            table.add_row("Equivalent Stress", f"{equivalent_stress:.3e} Pa")
            table.add_row("Allowable Strength", f"{allowable:.3e} Pa")
            table.add_row("Safety Factor", f"{safety_factor:.2f}")

            console.print(table)

        return result
