"""
测试示例
"""

from sw_helper.geometry import GeometryParser
from sw_helper.material import MaterialDatabase, MechanicsCalculator


def test_geometry_parser():
    """测试几何解析器"""
    parser = GeometryParser()
    print("几何解析器创建成功")
    print(f"支持的格式: {parser.SUPPORTED_FORMATS}")


def test_material_database():
    """测试材料数据库"""
    db = MaterialDatabase()
    materials = db.list_materials()
    print(f"\n可用材料 ({len(materials)} 种):")
    for mat in materials:
        info = db.get_material(mat)
        print(f"  - {mat}: {info['description']}")


def test_mechanics_calculator():
    """测试力学计算"""
    calc = MechanicsCalculator()

    # 计算应力
    result = calc.calculate_stress(
        force=10000,  # 10kN
        area=0.001,  # 0.001 m²
        material_name="Q235",
    )
    print(f"\n应力计算结果:")
    print(f"  应力: {result['stress'] / 1e6:.2f} MPa")
    print(f"  安全系数: {result['safety_factor']:.2f}")


if __name__ == "__main__":
    test_geometry_parser()
    test_material_database()
    test_mechanics_calculator()
