# 测试运行脚本

此目录包含运行CAE-CLI项目测试套件的各种脚本。

## 脚本列表

### 1. 主测试运行器
- **脚本**: `run_tests.py`
- **功能**: 运行完整的测试套件
- **用法**: `python scripts/test/run_tests.py [选项]`
- **选项**:
  - `-v`: 详细输出
  - `--coverage`: 生成覆盖率报告
  - `-k PATTERN`: 运行匹配模式名的测试

### 2. Windows测试脚本
- **脚本**: `run_tests.bat`
- **功能**: Windows下运行测试
- **用法**: 双击运行或命令行执行
- **特点**: 自动设置Python路径和环境变量

### 3. Linux/macOS测试脚本
- **脚本**: `run_tests.sh`
- **功能**: Unix系统下运行测试
- **用法**: `./scripts/test/run_tests.sh`
- **特点**: 支持bash环境，设置执行权限

## 测试目录结构

项目测试文件位于根目录的`tests/`目录中：

```
tests/
├── test_cli.py              # CLI命令测试
├── test_workflow_integration.py # 工作流集成测试
└── ...                      # 其他测试文件
```

## 使用示例

### 运行所有测试
```bash
python scripts/test/run_tests.py
```

### 运行详细测试并生成覆盖率报告
```bash
python scripts/test/run_tests.py -v --coverage
```

### 运行特定测试模块
```bash
python scripts/test/run_tests.py -k "test_cli"
```

### Windows环境
```bash
scripts/test/run_tests.bat
```

### Linux/macOS环境
```bash
chmod +x scripts/test/run_tests.sh
./scripts/test/run_tests.sh
```

## 测试类型

### 1. 单元测试
- 测试单个函数和类
- 位于`tests/`目录中

### 2. 集成测试
- 测试模块间集成
- 如`test_workflow_integration.py`

### 3. MCP测试
- 测试MCP服务器功能
- 位于`tests/mcp/`目录中

## 配置说明

测试配置位于`pytest.ini`文件中：
- 测试发现规则
- 覆盖率配置
- 测试标记定义

## 注意事项

1. **依赖要求**: 运行测试前确保安装所有依赖
2. **环境变量**: 某些测试可能需要特定环境变量
3. **测试数据**: 测试使用`test_data/`目录中的示例文件
4. **覆盖率**: 覆盖率报告生成在`.coverage`文件和`htmlcov/`目录中