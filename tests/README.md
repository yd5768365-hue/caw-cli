# CAE-CLI 测试套件

此目录包含CAE-CLI项目的所有测试文件。

## 测试目录结构

```
tests/
├── unit/              # 单元测试（单个函数/类测试）
│   ├── geometry/      # 几何解析模块测试
│   ├── mesh/          # 网格分析模块测试
│   ├── material/      # 材料力学模块测试
│   ├── mechanics/     # 力学计算模块测试
│   ├── report/        # 报告生成模块测试
│   ├── ai/            # AI辅助设计模块测试
│   └── utils/         # 工具模块测试
├── integration/       # 集成测试（模块间集成）
│   ├── connectors/    # 连接器集成测试
│   ├── workflow/      # 工作流引擎测试
│   └── cli/           # CLI命令集成测试
├── mcp/               # MCP服务器测试
│   ├── protocol/      # MCP协议测试
│   ├── tools/         # MCP工具测试
│   └── archive/       # 旧版本MCP测试
├── e2e/               # 端到端测试（完整流程）
└── fixtures/          # 测试夹具和数据
    └── test_data/     # 测试数据文件
```

## 测试类型说明

### 1. 单元测试 (unit)
- 测试单个函数或类的功能
- 快速执行，隔离依赖
- 使用mock对象模拟外部依赖

### 2. 集成测试 (integration)
- 测试多个模块的协作
- 验证接口兼容性
- 测试实际工作流

### 3. MCP测试 (mcp)
- 测试Model Context Protocol服务器
- 验证MCP协议实现
- 测试工具功能

### 4. 端到端测试 (e2e)
- 测试完整CAD→CAE流程
- 验证实际软件集成
- 需要安装相应软件（FreeCAD, CalculiX等）

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定类型的测试
```bash
# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行MCP测试
pytest tests/mcp/
```

### 运行单个测试文件
```bash
pytest tests/unit/test_material_calculator.py -v
```

### 生成覆盖率报告
```bash
pytest --cov=src --cov-report=html
```

## 测试配置

测试配置位于根目录的`pytest.ini`文件中：
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v
```

## 测试数据

测试数据位于`tests/fixtures/test_data/`目录中，包括：
- 示例几何文件（STEP, STL格式）
- 示例网格文件（MSH, INP格式）
- 示例结果文件（FRD, VTK格式）

## 注意事项

1. **环境要求**: 某些测试需要特定软件安装（如FreeCAD, CalculiX）
2. **模拟模式**: 无软件环境时使用模拟连接器
3. **测试隔离**: 每个测试应该独立运行，不依赖外部状态
4. **清理工作**: 测试后应清理生成的文件