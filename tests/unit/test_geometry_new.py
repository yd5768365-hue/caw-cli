#!/usr/bin/env python3
"""
几何模块单元测试

测试 sw_helper/geometry 下的模块：
- parser: 几何解析
- analyzer: 几何分析
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
import tempfile


class TestGeometryParser:
    """几何解析器测试"""

    def test_geometry_parser_import(self):
        """测试几何解析器导入"""
        from sw_helper.geometry import parser

        assert parser is not None


class TestGeometryAnalyzer:
    """几何分析器测试"""

    def test_geometry_analyzer_import(self):
        """测试几何分析器导入"""
        from sw_helper.geometry import analyzer

        assert analyzer is not None


class TestGeometryModule:
    """几何模块综合测试"""

    def test_geometry_module_import(self):
        """测试几何模块导入"""
        from sw_helper import geometry

        assert geometry is not None


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
