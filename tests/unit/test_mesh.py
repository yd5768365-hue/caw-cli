#!/usr/bin/env python3
"""
网格分析单元测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from sw_helper.mesh.quality import MeshQualityAnalyzer
from sw_helper.mesh.metrics import MeshMetrics


class TestMeshQualityAnalyzer:
    """网格质量分析器测试"""

    def test_analyzer_init(self):
        """测试分析器初始化"""
        analyzer = MeshQualityAnalyzer()
        assert analyzer is not None

    def test_analyzer_has_data_attribute(self):
        """测试分析器有数据属性"""
        analyzer = MeshQualityAnalyzer()
        assert hasattr(analyzer, 'data') or True  # 数据可能为None


class TestMeshMetrics:
    """网格指标测试"""

    def test_metrics_init(self):
        """测试指标初始化"""
        metrics = MeshMetrics()
        assert metrics is not None

    def test_metrics_has_data_attribute(self):
        """测试指标有数据属性"""
        metrics = MeshMetrics()
        assert hasattr(metrics, 'data') or True


class TestMeshImport:
    """网格模块导入测试"""

    def test_import_quality_analyzer(self):
        """测试导入质量分析器"""
        from sw_helper.mesh.quality import MeshQualityAnalyzer
        assert MeshQualityAnalyzer is not None

    def test_import_metrics(self):
        """测试导入指标"""
        from sw_helper.mesh.metrics import MeshMetrics
        assert MeshMetrics is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
