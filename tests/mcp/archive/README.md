# 存档测试文件

此目录包含旧的MCP测试文件，供参考和回滚使用。

## 文件说明

### 1. 旧版本测试
- **test_fixed_server.py** - 旧修复服务器测试
- **test_stdio_async.py** - 异步stdio测试
- **test_mcp_basic.py** - MCP基础功能测试旧版
- **test_mcp_server.py** - MCP服务器测试旧版
- **test_mcp_simple.py** - 简单MCP测试旧版
- **test_mcp_manual.py** - 手动MCP测试
- **test_mcp_connection.py** - MCP连接测试旧版

### 2. 通用测试
- **test_mcp_basic.py** - 通用MCP测试
- **test_mcp_server.py** - 服务器功能测试

## 测试历史

这些测试文件针对旧版本的MCP服务器开发，可能不适用于最新版本。

## 当前状态

**推荐使用最新测试**：
- `tests/mcp/test_simple_mcp.py`
- `tests/mcp/test_mcp_full_protocol.py`
- `tests/mcp/test_encoding_fix.py`

## 注意事项

1. **不再维护** - 这些测试不再更新
2. **兼容性问题** - 可能与最新MCP服务器不兼容
3. **仅供参考** - 供学习和问题分析使用