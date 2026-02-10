```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
```

## CAE-CLI 项目概览

CAE-CLI 是一个专业的 CAE（计算机辅助工程）命令行工具，集成了 SolidWorks、FreeCAD 及各类建模/仿真软件，提供几何解析、网格分析、材料数据库、力学计算和报告生成等功能。

## 项目结构

```
cae-cli/
├── src/sw_helper/           # 主包
│   ├── cli.py              # CLI入口（核心文件）
│   ├── geometry/           # 几何解析模块
│   ├── mesh/               # 网格分析模块
│   ├── material/           # 材料力学模块
│   ├── report/             # 报告生成模块
│   ├── optimization/       # 参数优化模块
│   ├── ai/                 # AI辅助设计模块
│   ├── chat/               # 交互式聊天模块
│   ├── integrations/       # CAD软件集成模块
│   ├── mcp/                # MCP协议接口模块
│   └── utils/              # 工具模块
├── data/                    # 数据文件
│   ├── materials.json      # 材料库
│   └── config.yaml         # 默认配置
├── tests/                   # 测试
├── examples/                # 示例
├── docs/                    # 文档
├── pyproject.toml          # 项目配置
├── setup.py                # 安装脚本
└── README.md               # 说明文档
```

## 开发命令

### 安装依赖

```bash
# 基础安装
pip install -e .

# 安装完整功能版（包含几何处理）
pip install -e ".[full]"

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_cli.py -v

# 运行特定测试函数
pytest tests/test_cli.py::test_parse_command -v
```

### 代码格式化

```bash
# 使用black格式化
black src/

# 检查格式问题
black --check src/
```

### 类型检查

```bash
mypy src/sw_helper
```

### 运行CLI

```bash
# 查看帮助
cae-cli --help

# 或使用Python模块方式
python -m sw_helper --help
```

## 核心功能模块

### 1. 几何解析 (geometry)
- 支持 STEP、STL、IGES 格式解析
- 提取几何信息（体积、表面积、顶点数等）
- 输出格式：JSON、YAML、表格

### 2. 网格分析 (mesh)
- 分析网格质量指标（纵横比、偏斜度、正交质量等）
- 支持 .msh、.inp、.bdf 格式
- 质量评估：优秀/良好/一般/较差

### 3. 材料数据库 (material)
- 内置 GB/T 标准材料库（Q235、Q345、铝合金等）
- 支持单位转换（SI、MPa）
- 支持搜索和查询特定属性

### 4. 报告生成 (report)
- 支持 HTML、PDF、JSON、Markdown 格式
- 分析类型：静力、模态、热、屈曲分析
- 支持自定义模板

### 5. 参数优化 (optimization)
- 自动调整设计参数并评估质量
- 支持 FreeCAD 和 SolidWorks
- 优化流程：参数修改 → 重建 → 导出 → 分析 → 报告

### 6. AI辅助设计 (ai)
- 文本到3D模型生成（自然语言描述 → FreeCAD建模）
- AI优化建议
- 集成多个LLM提供商（OpenAI、Anthropic、Ollama等）

### 7. CAD集成 (integrations)
- SolidWorks：参数修改、文件导出、宏生成
- FreeCAD：完整API集成、MCP协议
- 自动连接和操作CAD软件

### 8. 交互式聊天 (chat)
- 类似OpenCode的交互式AI助手
- 自然语言控制FreeCAD建模
- 实时质量分析反馈

### 9. MCP协议 (mcp)
- Model Context Protocol 接口
- 管理FreeCAD和其他工具的MCP服务器
- 直接调用MCP工具

## 常用命令示例

```bash
# 解析几何文件
cae-cli parse model.step

# 分析网格质量
cae-cli analyze mesh.msh --metric aspect_ratio --metric skewness

# 查询材料
cae-cli material Q235 --property elastic_modulus

# 生成报告
cae-cli report static --input result.inp --output report.html

# 参数优化
cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 5

# AI模型生成
cae-cli ai generate "带圆角的立方体，长100宽50高30圆角10"

# 启动交互式聊天
cae-cli chat

# 调用MCP工具
cae-cli mcp call freecad_create_box '{"length": 100, "width": 50, "height": 30}'
```

## 配置文件

配置文件位于 `~/.cae-cli/config.json`，支持自定义：
- 默认材料
- 安全系数
- 输出格式
- 详细模式

## 开发注意事项

1. 项目使用 Python 3.8+，遵循 Black 代码风格
2. 所有 CLI 命令通过 Click 库实现
3. 使用 Rich 库提供美观的终端输出
4. 重要功能都有对应的测试用例
5. 支持可选依赖安装（[full] 包含所有功能）
