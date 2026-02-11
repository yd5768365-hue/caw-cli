# 工具脚本

此目录包含CAE-CLI项目的各种工具和演示脚本。

## 脚本列表

### 1. API文档生成
- **脚本**: `generate_api_docs.py`
- **功能**: 自动生成项目API文档
- **用法**: `python scripts/tools/generate_api_docs.py`
- **输出**: 生成`docs/api/`目录中的文档文件

### 2. GitHub MCP演示
- **脚本**: `demo_github_mcp.py`
- **功能**: 演示GitHub MCP服务器的完整功能
- **用法**: `python scripts/tools/demo_github_mcp.py`
- **演示内容**: 文件操作、Git操作、仓库管理等

### 3. 工作流演示
- **脚本**: `demo_workflow.py`
- **功能**: 演示CAE-CLI的工作流引擎
- **用法**: `python scripts/tools/demo_workflow.py`
- **演示内容**: CAD→CAE完整分析流程

### 4. MCP配置脚本
- **脚本**: `setup_sqlite_mcp.bat`
- **功能**: Windows下配置SQLite MCP服务器
- **用法**: 双击运行或命令行执行
- **注意**: Windows专用脚本

### 5. 测试运行脚本
- **脚本**: `run_tests.py`, `run_tests.bat`, `run_tests.sh`
- **功能**: 运行项目测试套件
- **平台**:
  - `run_tests.py`: 跨平台Python脚本
  - `run_tests.bat`: Windows批处理脚本
  - `run_tests.sh`: Linux/macOS shell脚本

## 使用示例

### 生成API文档
```bash
python scripts/tools/generate_api_docs.py
# 文档将生成到 docs/api/ 目录
```

### 运行GitHub MCP演示
```bash
python scripts/tools/demo_github_mcp.py
# 演示完整的GitHub仓库管理功能
```

### 运行工作流演示
```bash
python scripts/tools/demo_workflow.py
# 演示CAD到CAE的完整分析流程
```

### 运行测试套件
```bash
# 使用Python脚本（跨平台）
python scripts/tools/run_tests.py

# Windows
scripts/tools/run_tests.bat

# Linux/macOS
./scripts/tools/run_tests.sh
```

## 开发说明

这些工具脚本主要用于：
1. **项目维护** - 文档生成、测试运行
2. **功能演示** - 展示项目核心功能
3. **开发辅助** - 简化常见开发任务

## 注意事项

1. **依赖要求**: 部分脚本需要项目已安装依赖
2. **环境配置**: 确保Python路径和依赖正确配置
3. **平台差异**: 注意脚本的平台兼容性（.bat为Windows，.sh为Unix）