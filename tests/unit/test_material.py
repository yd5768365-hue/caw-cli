#!/usr/bin/env python3
"""
材料数据库单元测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from sw_helper.material.database import MaterialDatabase


class TestMaterialDatabase:
    """材料数据库测试类"""

    @pytest.fixture
    def db(self):
        """创建材料数据库fixture"""
        return MaterialDatabase()

    def test_load_database(self, db):
        """测试数据库加载"""
        assert db.materials is not None
        assert len(db.materials) > 0

    def test_get_material(self, db):
        """测试获取材料"""
        q235 = db.get_material("Q235")
        assert q235 is not None
        assert q235["name"] == "Q235"
        assert q235["standard"] == "GB/T 700"

    def test_get_material_properties(self, db):
        """测试获取材料属性"""
        q235 = db.get_material("Q235")
        assert "elastic_modulus" in q235
        assert "density" in q235
        assert "yield_strength" in q235

    def test_get_nonexistent_material(self, db):
        """测试获取不存在的材料"""
        result = db.get_material("不存在的材料")
        assert result is None

    def test_list_materials(self, db):
        """测试列出所有材料"""
        materials = db.list_materials()
        assert len(materials) > 0
        assert "Q235" in materials

    def test_search_materials(self, db):
        """测试搜索材料"""
        results = db.search_materials("钢")
        assert len(results) > 0

    def test_get_all_properties(self, db):
        """测试获取所有属性"""
        q235 = db.get_material("Q235")
        assert "elastic_modulus" in q235
        assert q235["elastic_modulus"] == 210000000000


class TestMaterialProperties:
    """材料属性测试类"""

    def test_q235_properties(self):
        """测试Q235材料属性"""
        db = MaterialDatabase()
        q235 = db.get_material("Q235")

        # 验证基本属性
        assert q235["density"] == 7850  # kg/m³
        assert q235["elastic_modulus"] == 210e9  # Pa
        assert q235["poisson_ratio"] == 0.3
        assert q235["yield_strength"] == 235e6  # Pa

    def test_q345_properties(self):
        """测试Q345材料属性"""
        db = MaterialDatabase()
        q345 = db.get_material("Q345")

        assert q345["yield_strength"] == 345e6  # Pa

    def test_45steel_properties(self):
        """测试45钢材料属性"""
        db = MaterialDatabase()
        steel45 = db.get_material("45钢")

        assert steel45["yield_strength"] == 355e6  # Pa
        assert steel45["tensile_strength"] == 600e6  # Pa


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
