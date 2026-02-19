# CAE-CLI MCP 连接问题解决方案

## 问题描述

在运行 `/mcp` 命令时出现连接错误：
```
Failed to reconnect to cae-sqlite.
```

## 根本原因

经过分析，发现以下问题：

1. **MCP协议实现不完整** - 原始MCP服务器缺少`initialized`通知响应
2. **Windows编码问题** - 在Windows上，Python默认使用GBK编码，而MCP协议要求UTF-8
3. **复杂的异步架构** - 原始服务器使用多线程和异步混合架构，在Windows上不稳定
4. **stdio处理问题** - 原始服务器的stdio处理方式与Claude Code不兼容

## 解决方案

已创建修复版本，解决所有上述问题：

### 1. 编码修复
- 强制设置UTF-8编码环境变量
- 重新包装stdio流为UTF-8编码
- 确保JSON消息正确编码/解码

### 2. MCP协议完整实现
- 正确处理`initialize`请求
- 发送`notifications/initialized`通知
- 遵循MCP协议规范（2024-11-05）

### 3. 简化架构
- 使用同步循环处理stdio
- 避免复杂的多线程/异步混合
- 提高Windows兼容性

## 修复版本

已创建以下修复版本：

| 服务器 | 原始脚本 | 修复版本脚本 | 状态 |
|--------|----------|--------------|------|
| SQLite MCP | `run_sqlite_mcp_fixed2.py` | `run_sqlite_mcp_protocol_fixed.py` | ✅ 连接成功 |
| GitHub MCP | `run_github_mcp_fixed.py` | `run_github_mcp_protocol_fixed.py` | ✅ 连接成功 |

## 配置更新

MCP服务器配置已更新为使用修复版本：

```bash
# 当前配置
claude mcp list

# 输出：
# sqlite: python -u E:\cae-cli\run_sqlite_mcp_protocol_fixed.py - ✓ Connected
# github: python -u E:\cae-cli\run_github_mcp_protocol_fixed.py - ✓ Connected
```

## 验证方法

### 1. 测试连接
```bash
claude mcp list
```

### 2. 测试功能
```bash
# 测试SQLite MCP服务器
python test_sqlite_fixed_tools.py

# 测试简单MCP协议
python test_simple_mcp.py
```

## 后续维护

### 如果需要创建新的MCP服务器
请参考以下模板创建：
1. 使用`run_sqlite_mcp_protocol_fixed.py`作为基础模板
2. 确保正确处理MCP协议
3. 解决Windows编码问题
4. 保持架构简单稳定

### 如果问题复发
检查以下方面：
1. 确保使用UTF-8编码
2. 验证MCP协议实现完整性
3. 测试简单服务器连接（`run_simple_mcp.py`）
4. 检查Claude Code版本兼容性

## 技术细节

### 关键修复点

1. **编码修复代码**：
```python
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True, write_through=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True, write_through=True)
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
```

2. **MCP协议关键部分**：
```python
# 响应initialize请求
response["result"] = {
    "protocolVersion": "2024-11-05",
    "capabilities": {"tools": {"listChanged": True}, "resources": {"listChanged": True}},
    "serverInfo": {"name": "server-name", "version": "1.0.0"}
}

# 发送initialized通知
notification = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
    "params": {}
}
print(json.dumps(notification))
sys.stdout.flush()
```

## 总结

通过创建符合MCP协议的修复版本，解决了原始服务器的连接问题。修复版本：
- ✅ 正确处理MCP协议
- ✅ 解决Windows编码问题
- ✅ 提供稳定连接
- ✅ 保持原有功能完整性

两个MCP服务器现在都可以正常连接到Claude Code。