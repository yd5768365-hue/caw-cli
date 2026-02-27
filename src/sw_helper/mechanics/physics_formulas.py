"""
力学计算公式模块
包含材料力学、结构力学常用公式的Python实现
"""

import math
from typing import Tuple

import numpy as np


def calculate_von_mises_stress(stress_tensor: np.ndarray) -> float:
    """
    计算Von Mises等效应力

    Args:
        stress_tensor: 3x3应力张量 [σ_x, τ_xy, τ_xz; τ_yx, σ_y, τ_yz; τ_zx, τ_zy, σ_z]

    Returns:
        float: Von Mises等效应力
    """
    # 检查numpy可用性
    if stress_tensor.shape != (3, 3):
        raise ValueError("应力张量必须是3x3矩阵")

    # 提取应力分量
    σ_x = stress_tensor[0, 0]
    σ_y = stress_tensor[1, 1]
    σ_z = stress_tensor[2, 2]
    τ_xy = stress_tensor[0, 1]
    τ_xz = stress_tensor[0, 2]
    τ_yz = stress_tensor[1, 2]

    # Von Mises公式
    σ_vm = math.sqrt(0.5 * ((σ_x - σ_y) ** 2 + (σ_y - σ_z) ** 2 + (σ_z - σ_x) ** 2) + 3 * (τ_xy**2 + τ_xz**2 + τ_yz**2))

    return σ_vm


def calculate_principal_stresses(
    stress_tensor: np.ndarray,
) -> Tuple[float, float, float]:
    """
    计算主应力

    Args:
        stress_tensor: 3x3应力张量

    Returns:
        Tuple[float, float, float]: (σ1, σ2, σ3) 主应力，从大到小排序
    """
    # 使用numpy计算特征值
    eigenvalues = np.linalg.eigvalsh(stress_tensor)
    # 从大到小排序
    sorted_eigenvalues = sorted(eigenvalues, reverse=True)
    return tuple(sorted_eigenvalues)


def calculate_safety_factor(
    applied_stress: float,
    material_yield_strength: float,
    material_tensile_strength: float,
    material_type: str = "ductile",
) -> float:
    """
    计算安全系数

    Args:
        applied_stress: 施加的应力 (Pa)
        material_yield_strength: 材料屈服强度 (Pa)
        material_tensile_strength: 材料抗拉强度 (Pa)
        material_type: 材料类型 ("ductile" 塑性 / "brittle" 脆性)

    Returns:
        float: 安全系数
    """
    if applied_stress <= 0:
        raise ValueError("施加应力必须大于0")

    if material_type == "ductile":
        # 塑性材料基于屈服强度
        safety_factor = material_yield_strength / applied_stress
    else:
        # 脆性材料基于抗拉强度
        safety_factor = material_tensile_strength / applied_stress

    return safety_factor


def calculate_buckling_load(
    youngs_modulus: float,
    moment_of_inertia: float,
    length: float,
    end_condition: str = "pinned-pinned",
) -> float:
    """
    计算欧拉屈曲载荷

    Args:
        youngs_modulus: 弹性模量 (Pa)
        moment_of_inertia: 截面惯性矩 (m^4)
        length: 杆件长度 (m)
        end_condition: 边界条件 ("pinned-pinned", "fixed-fixed", "fixed-pinned", "fixed-free")

    Returns:
        float: 临界屈曲载荷 (N)
    """
    # 有效长度系数
    k_factors = {
        "pinned-pinned": 1.0,
        "fixed-fixed": 0.5,
        "fixed-pinned": 0.7,
        "fixed-free": 2.0,
    }

    if end_condition not in k_factors:
        raise ValueError(f"不支持的边界条件: {end_condition}")

    k = k_factors[end_condition]
    effective_length = k * length

    # 欧拉屈曲公式
    critical_load = (math.pi**2 * youngs_modulus * moment_of_inertia) / (effective_length**2)

    return critical_load


def calculate_deflection(
    load: float,
    length: float,
    youngs_modulus: float,
    moment_of_inertia: float,
    load_type: str = "point_center",
) -> float:
    """
    计算梁的挠度

    Args:
        load: 载荷 (N)
        length: 梁长度 (m)
        youngs_modulus: 弹性模量 (Pa)
        moment_of_inertia: 截面惯性矩 (m^4)
        load_type: 载荷类型 ("point_center", "uniform", "point_end")

    Returns:
        float: 最大挠度 (m)
    """
    deflection_formulas = {
        "point_center": lambda P, L, E, I: (P * L**3) / (48 * E * I),
        "uniform": lambda w, L, E, I: (5 * w * L**4) / (384 * E * I),
        "point_end": lambda P, L, E, I: (P * L**3) / (3 * E * I),
    }

    if load_type not in deflection_formulas:
        raise ValueError(f"不支持的载荷类型: {load_type}")

    formula = deflection_formulas[load_type]
    return formula(load, length, youngs_modulus, moment_of_inertia)


def calc_principal_stresses(
    sigma_x: float,
    sigma_y: float,
    tau_xy: float,
) -> Tuple[float, float]:
    """
    计算平面应力状态下的第一、第二主应力（σ1, σ2）

    物理意义：
        基于材料力学中主应力变换公式，用于确定材料在
        平面应力状态下的极值正应力。

    公式来源：
        《机械设计手册》— 应力分析章节（Mohr 圆）

    参数说明：
        sigma_x (float): x 方向正应力，单位 Pa
        sigma_y (float): y 方向正应力，单位 Pa
        tau_xy  (float): 剪应力，单位 Pa

    返回值：
        Tuple[float, float]:
            - sigma_1: 第一主应力（最大），单位 Pa
            - sigma_2: 第二主应力（最小），单位 Pa
    """
    avg = 0.5 * (sigma_x + sigma_y)
    radius = math.sqrt(((sigma_x - sigma_y) / 2.0) ** 2 + tau_xy**2)

    sigma_1 = avg + radius
    sigma_2 = avg - radius

    return sigma_1, sigma_2


def calc_von_mises(
    s1: float,
    s2: float,
    s3: float,
) -> float:
    """
    计算等效应力（von Mises 应力）
    ——第四强度理论（畸变能理论）

    物理意义：
        用于延性材料的屈服判据，认为材料在
        畸变能达到临界值时发生屈服。

    公式来源：
        《机械设计手册》— 第四强度理论

    参数说明：
        s1 (float): 第一主应力，单位 Pa
        s2 (float): 第二主应力，单位 Pa
        s3 (float): 第三主应力，单位 Pa

    返回值：
        float: von Mises 等效应力，单位 Pa
    """
    return math.sqrt(0.5 * ((s1 - s2) ** 2 + (s2 - s3) ** 2 + (s3 - s1) ** 2))


def calc_max_shear(
    s1: float,
    s3: float,
) -> float:
    """
    计算最大剪应力
    ——第三强度理论（最大剪应力理论 / Tresca）

    物理意义：
        常用于脆性材料或保守设计，
        认为材料在最大剪应力达到极限时破坏。

    公式来源：
        《机械设计手册》— 第三强度理论

    参数说明：
        s1 (float): 最大主应力，单位 Pa
        s3 (float): 最小主应力，单位 Pa

    返回值：
        float: 最大剪应力，单位 Pa
    """
    return 0.5 * abs(s1 - s3)
