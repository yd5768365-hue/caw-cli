#!/usr/bin/env python3
"""
核心模块单元测试

测试核心数据类型和异常
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
import tempfile


class TestCoreExceptions:
    """核心异常测试"""

    def test_exceptions_import(self):
        """测试异常导入"""
        from core import exceptions

        assert exceptions is not None


class TestCoreTypes:
    """核心类型测试"""

    def test_types_import(self):
        """测试类型导入"""
        from core import types

        assert types is not None


class TestIntegrationsBase:
    """集成模块基础测试"""

    def test_connectors_import(self):
        """测试连接器导入"""
        from integrations._base import connectors

        assert connectors is not None


class TestMCPModule:
    """MCP模块测试"""

    def test_mcp_core_import(self):
        """测试MCP核心导入"""
        from sw_helper.mcp import core

        assert core is not None

    def test_mcp_server_import(self):
        """测试MCP服务器导入"""
        from sw_helper.mcp import MCPServer

        assert MCPServer is not None


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
