# MCP文档

此目录包含Model Context Protocol (MCP) 相关的文档。

## 文档列表

### 1. 配置文档
- **MCP_CONFIGURATION.md** - MCP服务器配置说明
- **MCP_FIX_SUMMARY.md** - MCP连接问题解决方案总结

### 2. 技术文档
- **协议说明** - MCP协议实现细节
- **服务器架构** - MCP服务器设计文档
- **工具开发** - 如何开发新的MCP工具

### 3. 使用指南
- **快速开始** - 如何配置和使用MCP服务器
- **故障排除** - 常见问题和解决方案
- **最佳实践** - MCP服务器使用建议

## MCP服务器概览

CAE-CLI项目包含以下MCP服务器：

### 1. GitHub仓库管理MCP服务器
- **功能**: 管理GitHub仓库（https://github.com/yd5768365-hue/caw-cli.git）
- **工具**: 完整的Git操作和文件管理工具集
- **状态**: ✅ 协议修复版，稳定运行
- **脚本**: `scripts/mcp/run_github_mcp_protocol_fixed.py`

### 2. SQLite数据库MCP服务器
- **功能**: 管理CAE-CLI的SQLite数据库
- **工具**: 材料查询、计算历史、知识库搜索等
- **状态**: ✅ 协议修复版，稳定运行
- **脚本**: `scripts/mcp/run_sqlite_mcp_protocol_fixed.py`

### 3. FreeCAD参数化MCP服务器
- **功能**: FreeCAD参数化建模工具
- **状态**: ⚠️ 独立子项目，位于`freecad-parametric-mcp/`
- **文档**: 参考子项目文档

## 快速开始

### 1. 配置MCP服务器
```bash
# 添加SQLite MCP服务器
claude mcp add sqlite python -u scripts/mcp/run_sqlite_mcp_protocol_fixed.py

# 添加GitHub MCP服务器
claude mcp add github python -u scripts/mcp/run_github_mcp_protocol_fixed.py
```

### 2. 验证连接
```bash
claude mcp list
```

### 3. 测试功能
```bash
python tests/mcp/test_simple_mcp.py
```

## 开发指南

### 创建新的MCP服务器
参考`scripts/mcp/run_simple_mcp.py`作为模板。

### 添加新工具
在相应的MCP服务器模块中添加工具定义。

### 测试MCP服务器
使用`tests/mcp/`目录中的测试文件。

## 故障排除

常见问题及解决方案请参考`MCP_FIX_SUMMARY.md`文档。