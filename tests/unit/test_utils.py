#!/usr/bin/env python3
"""
工具模块单元测试

测试 sw_helper/utils 下的工具模块：
- validator: 输入验证
- error_handler: 错误处理
- encoding_helper: 编码辅助
- dependency_checker: 依赖检查
"""

import sys
from pathlib import Path
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from unittest.mock import Mock, patch


class TestFileValidator:
    """文件验证器测试"""

    def test_validate_geometry_file_valid(self):
        """测试有效几何文件验证"""
        from sw_helper.utils.validator import FileValidator

        # 创建临时几何文件
        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f:
            f.write(b"test")
            temp_path = f.name

        result = FileValidator.validate_geometry_file(temp_path)
        assert result is True
        Path(temp_path).unlink()

    def test_validate_geometry_file_invalid_format(self):
        """测试无效几何文件格式"""
        from sw_helper.utils.validator import FileValidator

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test")
            temp_path = f.name

        with pytest.raises(ValueError, match="不支持的几何文件格式"):
            FileValidator.validate_geometry_file(temp_path)
        Path(temp_path).unlink()

    def test_validate_mesh_file_valid(self):
        """测试有效网格文件验证"""
        from sw_helper.utils.validator import FileValidator

        with tempfile.NamedTemporaryFile(suffix=".msh", delete=False) as f:
            f.write(b"test")
            temp_path = f.name

        result = FileValidator.validate_mesh_file(temp_path)
        assert result is True
        Path(temp_path).unlink()

    def test_validate_file_size_valid(self):
        """测试有效文件大小"""
        from sw_helper.utils.validator import FileValidator

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"x" * 1024)  # 1KB
            temp_path = f.name

        result = FileValidator.validate_file_size(temp_path, max_size_mb=1)
        assert result is True
        Path(temp_path).unlink()

    def test_validate_file_size_too_large(self):
        """测试文件过大"""
        from sw_helper.utils.validator import FileValidator

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"x" * (2 * 1024 * 1024))  # 2MB
            temp_path = f.name

        with pytest.raises(ValueError, match="文件过大"):
            FileValidator.validate_file_size(temp_path, max_size_mb=0.001)
        Path(temp_path).unlink()


class TestInputValidator:
    """输入验证器测试"""

    def test_validate_positive_number(self):
        """测试正数验证"""
        from sw_helper.utils.validator import InputValidator

        assert InputValidator.validate_positive_number(10) is True
        assert InputValidator.validate_positive_number(0.001) is True
        with pytest.raises(ValueError):
            InputValidator.validate_positive_number(-1)
        with pytest.raises(ValueError):
            InputValidator.validate_positive_number(0)

    def test_validate_range(self):
        """测试范围验证"""
        from sw_helper.utils.validator import InputValidator

        assert InputValidator.validate_range(5, 1, 10) is True
        assert InputValidator.validate_range(1, 1, 10) is True
        assert InputValidator.validate_range(10, 1, 10) is True
        with pytest.raises(ValueError):
            InputValidator.validate_range(0, 1, 10)
        with pytest.raises(ValueError):
            InputValidator.validate_range(11, 1, 10)


class TestErrorHandler:
    """错误处理器测试"""

    def test_error_handler_import(self):
        """测试错误处理器导入"""
        from sw_helper.utils import error_handler

        assert error_handler is not None


class TestEncodingHelper:
    """编码辅助器测试"""

    def test_encoding_helper_import(self):
        """测试编码辅助器导入"""
        from sw_helper.utils import encoding_helper

        assert encoding_helper is not None


class TestDependencyChecker:
    """依赖检查器测试"""

    def test_dependency_checker_import(self):
        """测试依赖检查器导入"""
        from sw_helper.utils.dependency_checker import DependencyChecker

        checker = DependencyChecker()
        assert checker is not None


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
