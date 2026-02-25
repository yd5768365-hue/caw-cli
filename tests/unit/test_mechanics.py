#!/usr/bin/env python3
"""
力学计算单元测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
import numpy as np
from sw_helper.mechanics.physics_formulas import (
    calculate_von_mises_stress,
    calculate_principal_stresses,
    calculate_safety_factor,
    calculate_deflection,
    calculate_buckling_load,
    calc_von_mises,
    calc_principal_stresses,
    calc_max_shear,
)


class TestVonMisesStress:
    """Von Mises应力计算测试"""

    def test_simple_tension(self):
        """测试简单拉伸情况"""
        # 简单拉伸应力状态: σ_x = 100 MPa, 其他为0
        stress = np.array([
            [100e6, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ], dtype=float)
        vm_stress = calculate_von_mises_stress(stress)
        assert np.isclose(vm_stress, 100e6)

    def test_pure_shear(self):
        """测试纯剪切情况"""
        # 纯剪切: τ_xy = 50 MPa
        stress = np.array([
            [0, 50e6, 0],
            [50e6, 0, 0],
            [0, 0, 0]
        ], dtype=float)
        vm_stress = calculate_von_mises_stress(stress)
        # 纯剪切时 Von Mises = sqrt(3) * τ
        expected = np.sqrt(3) * 50e6
        assert np.isclose(vm_stress, expected, rtol=0.01)

    def test_biaxial_stress(self):
        """测试双轴应力状态"""
        # 等双轴拉伸: σ_x = σ_y = 100 MPa
        stress = np.array([
            [100e6, 0, 0],
            [0, 100e6, 0],
            [0, 0, 0]
        ], dtype=float)
        vm_stress = calculate_von_mises_stress(stress)
        # Von Mises = |σ1 - σ2|
        assert np.isclose(vm_stress, 100e6)

    def test_invalid_tensor(self):
        """测试无效应力张量"""
        with pytest.raises(ValueError):
            calculate_von_mises_stress(np.array([1, 2, 3]))


class TestPrincipalStresses:
    """主应力计算测试"""

    def test_uniaxial_tension(self):
        """测试单轴拉伸"""
        stress = np.array([
            [100e6, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ], dtype=float)
        σ1, σ2, σ3 = calculate_principal_stresses(stress)
        assert np.isclose(σ1, 100e6)
        assert np.isclose(σ3, 0, atol=1e-3)

    def test_triaxial_stress(self):
        """测试三轴应力状态"""
        stress = np.array([
            [100e6, 0, 0],
            [0, 50e6, 0],
            [0, 0, 20e6]
        ], dtype=float)
        σ1, σ2, σ3 = calculate_principal_stresses(stress)
        assert σ1 >= σ2 >= σ3
        assert np.isclose(σ1, 100e6)
        assert np.isclose(σ3, 20e6)


class TestMaxShearStress:
    """最大剪应力测试"""

    def test_max_shear_calculation(self):
        """测试最大剪应力计算"""
        # 使用主应力计算最大剪应力
        s1 = 100e6  # 最大主应力
        s3 = 20e6  # 最小主应力
        max_shear = calc_max_shear(s1, s3)
        # 最大剪应力 = (σ1 - σ3) / 2
        expected = (s1 - s3) / 2
        assert np.isclose(max_shear, expected, rtol=0.01)


class TestSafetyFactor:
    """安全系数计算测试"""

    def test_ductile_safety_factor(self):
        """测试塑性材料安全系数"""
        # 屈服强度 235 MPa, 施加应力 100 MPa
        sf = calculate_safety_factor(
            applied_stress=100e6,
            material_yield_strength=235e6,
            material_tensile_strength=375e6,
            material_type="ductile"
        )
        assert np.isclose(sf, 2.35)

    def test_brittle_safety_factor(self):
        """测试脆性材料安全系数"""
        # 抗拉强度 375 MPa, 施加应力 100 MPa
        sf = calculate_safety_factor(
            applied_stress=100e6,
            material_yield_strength=235e6,
            material_tensile_strength=375e6,
            material_type="brittle"
        )
        assert np.isclose(sf, 3.75)

    def test_zero_stress_error(self):
        """测试零应力错误"""
        with pytest.raises(ValueError):
            calculate_safety_factor(
                applied_stress=0,
                material_yield_strength=235e6,
                material_tensile_strength=375e6
            )


class TestDeflection:
    """挠度计算测试"""

    def test_simple_beam_deflection(self):
        """测试简支梁挠度"""
        # 简支梁, 集中载荷
        deflection = calculate_deflection(
            load=1000,  # 1000N
            length=1.0,  # 1m
            youngs_modulus=210e9,  # 210 GPa
            moment_of_inertia=8.33e-6,  # 矩形截面 I = bh³/12
            load_type="point_center"
        )
        assert deflection > 0


class TestBucklingLoad:
    """屈曲载荷测试"""

    def test_euler_buckling(self):
        """测试欧拉屈曲载荷"""
        # 欧拉公式: Pcr = π²EI/(KL)²
        load = calculate_buckling_load(
            youngs_modulus=210e9,
            moment_of_inertia=8.33e-6,
            length=1.0,
            end_condition="pinned-pinned"  # 两端铰支
        )
        assert load > 0

    def test_fixed_free_buckling(self):
        """测试一端固定一端自由屈曲"""
        load = calculate_buckling_load(
            youngs_modulus=210e9,
            moment_of_inertia=8.33e-6,
            length=1.0,
            end_condition="fixed-free"  # 悬臂
        )
        # 一端固定的临界载荷更小
        pinned_load = calculate_buckling_load(
            youngs_modulus=210e9,
            moment_of_inertia=8.33e-6,
            length=1.0,
            end_condition="pinned-pinned"
        )
        assert load < pinned_load


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
