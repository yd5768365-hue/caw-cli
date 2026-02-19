# MCP测试文件

此目录包含Model Context Protocol (MCP) 服务器的测试文件。

## 测试文件列表

### 1. MCP连接测试
- **test_mcp_connection_diagnostic.py** - MCP连接诊断测试
- **test_mcp_full_protocol.py** - 完整MCP协议测试
- **test_simple_mcp.py** - 简单MCP服务器测试

### 2. 编码修复测试
- **test_encoding_fix.py** - Windows编码修复测试

### 3. 服务器功能测试
- **test_sqlite_fixed_tools.py** - SQLite MCP服务器工具测试
- **test_mcp_basic.py** - MCP基础功能测试
- **test_mcp_server.py** - MCP服务器测试
- **test_mcp_manual.py** - 手动MCP测试
- **test_mcp_simple.py** - 简单MCP测试

## 测试说明

### 运行所有MCP测试
```bash
pytest tests/mcp/ -v
```

### 运行特定测试
```bash
pytest tests/mcp/test_simple_mcp.py -v
```

### 测试依赖
MCP测试需要：
1. MCP服务器脚本（位于`scripts/mcp/`）
2. 正确的Python环境
3. 必要的依赖包（asyncio, json等）

## 测试类型

### 1. 协议测试
- 验证MCP协议正确实现
- 测试initialize/initialized流程
- 测试工具列表和调用

### 2. 功能测试
- 测试具体工具功能
- 验证服务器响应
- 测试错误处理

### 3. 集成测试
- 测试与Claude Code的集成
- 验证端到端功能
- 测试实际使用场景

## 注意事项

1. **环境要求**: 某些测试可能需要特定环境配置
2. **服务器状态**: 测试前确保MCP服务器可运行
3. **平台差异**: 注意Windows和Unix平台的差异
4. **编码问题**: Windows下特别注意UTF-8编码测试