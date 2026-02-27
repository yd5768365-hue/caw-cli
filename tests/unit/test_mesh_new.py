#!/usr/bin/env python3
"""
网格模块单元测试

测试 sw_helper/mesh 下的模块：
- metrics: 网格指标
- quality: 网格质量
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
import tempfile


class TestMeshMetrics:
    """网格指标测试"""

    def test_mesh_metrics_import(self):
        """测试网格指标导入"""
        from sw_helper.mesh import metrics

        assert metrics is not None


class TestMeshQuality:
    """网格质量测试"""

    def test_mesh_quality_import(self):
        """测试网格质量导入"""
        from sw_helper.mesh import quality

        assert quality is not None

    def test_quality_class_import(self):
        """测试质量类导入"""
        from sw_helper.mesh.quality import MeshQualityAnalyzer

        analyzer = MeshQualityAnalyzer()
        assert analyzer is not None


class TestMeshModule:
    """网格模块综合测试"""

    def test_mesh_module_import(self):
        """测试网格模块导入"""
        from sw_helper import mesh

        assert mesh is not None


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
