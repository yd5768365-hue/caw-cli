# 存档目录

此目录包含旧版本的MCP服务器脚本，供参考和回滚使用。

## 文件说明

### 1. 旧版本修复脚本
- **run_github_mcp_fixed.py** - GitHub MCP服务器旧修复版
- **run_sqlite_mcp_fixed2.py** - SQLite MCP服务器旧修复版
- **run_github_mcp_wrapper.py** - GitHub MCP包装器旧版
- **run_sqlite_mcp.py** - SQLite MCP服务器原始版
- **run_github_mcp.py** - GitHub MCP服务器原始版

### 2. 旧版本测试
- **test_fixed_server.py** - 旧修复服务器测试
- **test_stdio_async.py** - 异步stdio测试

## 版本历史

### 原始版本问题
1. **编码问题** - Windows下GBK编码与UTF-8冲突
2. **协议不完整** - 缺少initialized通知
3. **异步架构复杂** - 多线程/异步混合不稳定

### 修复版本演进
1. **第一次修复** (`*_fixed.py`) - 尝试修复编码和异步问题
2. **第二次修复** (`*_fixed2.py`) - 改进架构，使用同步读取
3. **协议修复版** (`*_protocol_fixed.py`) - 完整MCP协议实现，稳定运行

## 当前状态

**推荐使用最新版本**：
- `scripts/mcp/run_github_mcp_protocol_fixed.py`
- `scripts/mcp/run_sqlite_mcp_protocol_fixed.py`

## 注意事项

1. **不再维护** - 这些旧版本不再接收更新
2. **仅供参考** - 供学习和问题分析使用
3. **可能存在bug** - 不建议在生产环境使用