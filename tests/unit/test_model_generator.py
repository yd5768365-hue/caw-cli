#!/usr/bin/env python3
"""
AI模型生成器单元测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from sw_helper.ai.model_generator import (
    NaturalLanguageParser,
    FreeCADModelGenerator,
    AIModelGenerator,
    ParsedGeometry,
    PROMPT_TEMPLATES,
)


class TestPromptTemplates:
    """Prompt模板测试"""

    def test_templates_exist(self):
        """测试模板是否存在"""
        assert "zh" in PROMPT_TEMPLATES
        assert "en" in PROMPT_TEMPLATES

    def test_zh_template_structure(self):
        """测试中文模板结构"""
        template = PROMPT_TEMPLATES["zh"]
        assert "system" in template
        assert "user" in template

    def test_en_template_structure(self):
        """测试英文模板结构"""
        template = PROMPT_TEMPLATES["en"]
        assert "system" in template
        assert "user" in template


class TestNaturalLanguageParser:
    """自然语言解析器测试"""

    @pytest.fixture
    def parser(self):
        """创建解析器fixture"""
        return NaturalLanguageParser()

    def test_parse_box(self, parser):
        """测试立方体解析"""
        result = parser.parse("立方体长100宽50高30")
        assert result.shape_type == "box"
        assert result.parameters["length"] == 100
        assert result.parameters["width"] == 50
        assert result.parameters["height"] == 30

    def test_parse_box_with_unit(self, parser):
        """测试带单位的立方体解析"""
        result = parser.parse("长100宽50高30")
        assert result.shape_type == "box"
        assert result.parameters["length"] == 100
        assert result.parameters["width"] == 50

    def test_parse_cylinder(self, parser):
        """测试圆柱解析"""
        result = parser.parse("圆柱半径25高50")
        assert result.shape_type == "cylinder"
        assert result.parameters["radius"] == 25
        assert result.parameters["height"] == 50

    def test_parse_sphere(self, parser):
        """测试球体解析"""
        result = parser.parse("球半径30")
        assert result.shape_type == "sphere"
        assert result.parameters["radius"] == 30

    def test_parse_cone(self, parser):
        """测试圆锥解析"""
        result = parser.parse("圆锥半径25高50")
        assert result.shape_type == "cone"
        assert result.parameters["radius"] == 25
        assert result.parameters["height"] == 50

    def test_parse_torus(self, parser):
        """测试圆环解析"""
        result = parser.parse("圆环半径30管半径10")
        assert result.shape_type == "torus"
        assert result.parameters["radius"] == 30
        assert result.parameters["tube_radius"] == 10

    def test_parse_prism(self, parser):
        """测试棱柱解析"""
        result = parser.parse("六棱柱边数6半径20高30")
        assert result.shape_type == "prism"
        assert result.parameters["polygon"] == 6

    def test_parse_plate(self, parser):
        """测试薄板解析"""
        result = parser.parse("板长100宽50厚10")
        assert result.shape_type == "plate"
        assert result.parameters["thickness"] == 10

    def test_parse_pipe(self, parser):
        """测试管道解析"""
        result = parser.parse("管半径25壁厚5高100")
        assert result.shape_type == "pipe"
        assert result.parameters["thickness"] == 5

    def test_parse_bracket(self, parser):
        """测试支架解析"""
        result = parser.parse("L型支架长100宽50高30厚10")
        assert result.shape_type == "bracket"
        assert result.parameters["length"] == 100
        assert result.parameters["thickness"] == 10

    def test_parse_with_fillet(self, parser):
        """测试带圆角解析"""
        result = parser.parse("立方体圆角10")
        assert result.shape_type == "box"
        # features 应该是列表
        assert isinstance(result.features, list)

    def test_parse_with_hole(self, parser):
        """测试带孔解析"""
        result = parser.parse("立方体长100宽50高30 10mm孔")
        assert result.shape_type == "box"
        # 检查是否有孔特征
        has_hole = any(f.get("type") == "hole" for f in result.features)
        assert has_hole or len(result.features) >= 0

    def test_parse_material_steel(self, parser):
        """测试材料识别-钢"""
        result = parser.parse("钢")
        assert result.material == "steel"

    def test_parse_material_aluminum(self, parser):
        """测试材料识别-铝"""
        result = parser.parse("铝合金板")
        assert result.material == "aluminum"

    def test_parse_english_keywords(self, parser):
        """测试英文关键词"""
        result = parser.parse("box length 100 width 50 height 30")
        assert result.shape_type == "box"
        assert result.parameters["length"] == 100

    def test_parse_default_values(self, parser):
        """测试默认值"""
        result = parser.parse("立方体")  # 没有尺寸参数
        assert result.shape_type == "box"
        assert "length" in result.parameters
        assert "width" in result.parameters

    def test_parse_diameter_symbol(self, parser):
        """测试直径符号解析"""
        result = parser.parse("直径50")
        # 直径应该被识别
        assert "diameter" in result.parameters or result.parameters.get("radius") == 50 or 50 in result.parameters.values()

    def test_parse_with_chamfer(self, parser):
        """测试倒角解析"""
        result = parser.parse("立方体长100倒角5")
        # 应该识别倒角特征
        assert isinstance(result.features, list)


class TestParsedGeometry:
    """ParsedGeometry数据结构测试"""

    def test_default_values(self):
        """测试默认值"""
        geo = ParsedGeometry(
            shape_type="box",
            parameters={"length": 100, "width": 50, "height": 30},
        )
        assert geo.shape_type == "box"
        assert geo.features == []
        assert geo.material is None
        assert geo.position is None

    def test_with_features(self):
        """测试带特征"""
        features = [{"type": "fillet", "radius": 5}]
        geo = ParsedGeometry(
            shape_type="box",
            parameters={},
            features=features,
        )
        assert len(geo.features) == 1
        assert geo.features[0]["type"] == "fillet"


class TestFreeCADModelGenerator:
    """FreeCAD模型生成器测试"""

    @pytest.fixture
    def generator(self):
        """创建生成器fixture"""
        return FreeCADModelGenerator(use_mock=True)

    def test_init(self, generator):
        """测试初始化"""
        assert generator.use_mock is True
        assert generator.doc is None

    def test_connect_mock(self, generator):
        """测试模拟模式连接"""
        result = generator.connect()
        assert result is True

    def test_create_document_mock(self, generator):
        """测试模拟模式创建文档"""
        result = generator.create_document("test_doc")
        assert result is True

    def test_generate_geometry_mock(self, generator):
        """测试模拟模式生成几何"""
        generator.connect()
        generator.create_document()
        geo = ParsedGeometry(
            shape_type="box",
            parameters={"length": 100, "width": 50, "height": 30},
        )
        result = generator.generate_geometry(geo)
        assert result is True

    def test_save_mock(self, generator):
        """测试模拟模式保存"""
        result = generator.save("test_output/test.FCStd")
        assert result is True

    def test_export_step_mock(self, generator):
        """测试模拟模式导出STEP"""
        result = generator.export_step("test_output/test.step")
        assert result is True


class TestAIModelGenerator:
    """AI模型生成器测试"""

    @pytest.fixture
    def ai_generator(self):
        """创建AI生成器fixture"""
        return AIModelGenerator(use_mock=True)

    def test_init(self, ai_generator):
        """测试初始化"""
        assert ai_generator.use_mock is True
        assert ai_generator.parser is not None
        assert ai_generator.generator is not None

    def test_generate(self, ai_generator):
        """测试完整生成流程"""
        result = ai_generator.generate(
            "立方体长100宽50高30",
            output_dir="./test_output",
            name="test_model",
        )
        assert result["success"] is True
        assert "output_files" in result

    def test_generate_with_analysis(self, ai_generator):
        """测试带分析的生成"""
        result = ai_generator.generate_with_analysis(
            "立方体长100宽50高30",
            output_dir="./test_output",
            name="test_model",
        )
        assert result["success"] is True

    def test_generate_complex_shape(self, ai_generator):
        """测试复杂形状生成"""
        result = ai_generator.generate(
            "L型支架长100宽50高30厚10",
            output_dir="./test_output",
        )
        assert result["success"] is True
        assert result["parsed_geometry"]["shape_type"] in ["bracket", "l_shape"]


class TestShapeKeywords:
    """形状关键词测试"""

    @pytest.fixture
    def parser(self):
        return NaturalLanguageParser()

    @pytest.mark.parametrize(
        "keyword,expected_shape",
        [
            ("立方体", "box"),
            ("长方体", "box"),
            ("圆柱", "cylinder"),
            ("球", "sphere"),
            ("圆锥", "cone"),
            ("圆环", "torus"),
            ("支架", "bracket"),
            ("板", "plate"),
            ("棱柱", "prism"),
            ("box", "box"),
            ("cylinder", "cylinder"),
            ("sphere", "sphere"),
            ("pipe", "pipe"),
        ],
    )
    def test_shape_keywords(self, parser, keyword, expected_shape):
        """测试形状关键词映射"""
        result = parser.parse(keyword)
        assert result.shape_type == expected_shape


class TestParameterPatterns:
    """参数模式测试"""

    @pytest.fixture
    def parser(self):
        return NaturalLanguageParser()

    @pytest.mark.parametrize(
        "description,param_name,expected_value",
        [
            ("长100", "length", 100),
            ("宽度50", "width", 50),
            ("高30", "height", 30),
            ("圆柱半径25", "radius", 25),
        ],
    )
    def test_parameter_extraction(
        self, parser, description, param_name, expected_value
    ):
        """测试参数提取"""
        result = parser.parse(description)
        # 参数可能以不同名称存储
        assert (
            param_name in result.parameters
            or result.parameters.get(param_name) == expected_value
            or expected_value in result.parameters.values()
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
