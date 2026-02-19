# MCP服务器脚本

此目录包含Model Context Protocol (MCP) 服务器相关脚本。

## 当前可用的MCP服务器

### 1. GitHub仓库管理MCP服务器
- **脚本**: `run_github_mcp_protocol_fixed.py`
- **功能**: 管理GitHub仓库（https://github.com/yd5768365-hue/caw-cli.git）
- **工具**: 提供完整的Git操作和文件管理工具集
- **状态**: ✅ 协议修复版，稳定运行

### 2. SQLite数据库MCP服务器
- **脚本**: `run_sqlite_mcp_protocol_fixed.py`
- **功能**: 管理CAE-CLI的SQLite数据库
- **工具**: 材料查询、计算历史、知识库搜索等
- **状态**: ✅ 协议修复版，稳定运行

### 3. 简单MCP服务器
- **脚本**: `run_simple_mcp.py`
- **功能**: MCP协议演示和测试
- **状态**: ✅ 基础功能

## 配置说明

这些脚本已配置为Claude Code的MCP服务器。配置位于用户配置目录：
- `~/.config/claude-desktop/claude_desktop_config.json` (Linux/macOS)
- `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

## 使用示例

### 在Claude Code中查看MCP服务器状态
```bash
claude mcp list
```

### 手动运行MCP服务器
```bash
python scripts/mcp/run_github_mcp_protocol_fixed.py
```

### 测试连接
```bash
python scripts/mcp/test_simple_mcp.py
```

## 修复历史

原始MCP服务器存在以下问题：
1. **Windows编码问题** - 修复UTF-8编码
2. **MCP协议不完整** - 添加`initialized`通知响应
3. **异步架构问题** - 简化架构提高稳定性

修复版本已解决所有问题，确保在Windows和Linux/macOS上稳定运行。