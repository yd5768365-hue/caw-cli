# 脚本目录

此目录包含CAE-CLI项目的各种运行脚本和工具脚本。

## 目录结构

```
scripts/
├── mcp/              # MCP服务器相关脚本
├── setup/            # 安装和初始化脚本
├── tools/            # 工具脚本
└── test/             # 测试运行脚本
```

## 文件说明

### MCP脚本
- `mcp/run_github_mcp_protocol_fixed.py` - GitHub仓库管理MCP服务器（协议修复版）
- `mcp/run_sqlite_mcp_protocol_fixed.py` - SQLite数据库MCP服务器（协议修复版）
- `mcp/run_simple_mcp.py` - 简单MCP服务器演示

### 安装脚本
- `setup/init_sqlite_db.py` - 初始化SQLite数据库
- `setup/install.py` - 安装脚本

### 工具脚本
- `tools/generate_api_docs.py` - 生成API文档
- `tools/demo_github_mcp.py` - GitHub MCP演示
- `tools/demo_workflow.py` - 工作流演示

### 测试脚本
- `test/run_tests.py` - 运行测试套件
- `test/run_tests.bat` - Windows测试运行脚本
- `test/run_tests.sh` - Linux测试运行脚本