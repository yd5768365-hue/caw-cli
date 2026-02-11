# 安装和初始化脚本

此目录包含CAE-CLI项目的安装、配置和初始化脚本。

## 脚本列表

### 1. 数据库初始化
- **脚本**: `init_sqlite_db.py`
- **功能**: 初始化SQLite数据库，创建材料表、计算历史表和知识库表
- **用法**: `python scripts/setup/init_sqlite_db.py`
- **数据库位置**: `data/cae.db`

### 2. 项目安装
- **脚本**: `install.py`
- **功能**: 安装项目依赖和配置环境
- **用法**: `python scripts/setup/install.py`
- **依赖**: 自动安装`requirements.txt`中的依赖包

## 使用说明

### 完整安装流程
```bash
# 1. 安装项目依赖
pip install -e .

# 2. 初始化数据库
python scripts/setup/init_sqlite_db.py

# 3. 配置MCP服务器（可选）
claude mcp add sqlite python -u scripts/mcp/run_sqlite_mcp_protocol_fixed.py
claude mcp add github python -u scripts/mcp/run_github_mcp_protocol_fixed.py
```

### 数据库结构
初始化脚本会创建以下表：
1. **materials** - 材料数据库（GB/T标准材料）
2. **calculation_history** - 计算历史记录
3. **knowledge_base** - 机械工程知识库

### 环境要求
- Python 3.8+
- SQLite3（Python内置）
- 网络连接（用于安装依赖）

## 注意事项

1. **数据库备份**: 数据库文件位于`data/cae.db`，建议定期备份
2. **配置更新**: 安装后可能需要更新Claude Code的MCP配置
3. **权限要求**: 部分操作可能需要管理员权限（如全局包安装）