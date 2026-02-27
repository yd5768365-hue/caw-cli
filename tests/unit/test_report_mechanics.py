#!/usr/bin/env python3
"""
报告和力学模块单元测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
import tempfile


class TestReportGenerator:
    """报告生成器测试"""

    def test_report_generator_import(self):
        """测试报告生成器导入"""
        from sw_helper.report.generator import ReportGenerator

        gen = ReportGenerator()
        assert gen is not None


class TestMechanicsEngine:
    """力学引擎测试"""

    def test_mechanics_engine_import(self):
        """测试力学引擎导入"""
        from sw_helper.mechanics import engine

        assert engine is not None

    def test_mechanics_interface_import(self):
        """测试力学接口导入"""
        from sw_helper.mechanics import interface

        assert interface is not None


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
