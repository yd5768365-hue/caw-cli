# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CAE-CLI 项目概览

CAE-CLI 是专为机械专业学生（特别是从互联网专业转向机械领域的学习者）设计的专业 CAE（计算机辅助工程）命令行工具。它集成了 FreeCAD、CalculiX 及各类建模/仿真软件，提供几何解析、网格分析、材料数据库、力学计算和报告生成等功能，并采用**插件化架构**支持灵活扩展。

**核心目标**：帮助学生快速分析模型网格质量、材料力学性能、参数优化，并集成 AI 建议和个人机械手册知识库。

## 项目架构

### 整体结构

```
cae-cli/
├── src/
│   ├── sw_helper/           # 主包（原有功能）
│   │   ├── cli.py          # CLI入口（核心文件）
│   │   ├── geometry/       # 几何解析模块
│   │   ├── mesh/           # 网格分析模块
│   │   ├── material/       # 材料力学模块
│   │   ├── mechanics/      # 力学计算模块
│   │   ├── report/         # 报告生成模块
│   │   ├── optimization/   # 参数优化模块
│   │   ├── ai/             # AI辅助设计模块
│   │   ├── chat/           # 交互式聊天模块
│   │   ├── integrations/   # CAD软件集成模块（旧接口，保留兼容性）
│   │   ├── mcp/            # MCP协议接口模块
│   │   ├── knowledge.py     # 知识库管理（Markdown搜索）
│   │   └── utils/          # 工具模块
│   ├── integrations/        # 🚀 插件化架构（全新，推荐使用）
│   │   ├── _base/          # 抽象基类
│   │   │   ├── connectors.py   # CAD/CAE连接器抽象基类
│   │   │   └── workflow.py     # 工作流引擎
│   │   ├── cad/            # CAD连接器实现
│   │   │   └── freecad.py  # FreeCAD连接器（新架构）
│   │   ├── cae/            # CAE连接器实现
│   │   │   └── calculix.py # CalculiX连接器（新架构）
│   │   └── mesher/         # 网格生成器
│   │       └── gmsh.py     # Gmsh连接器
│   └── core/               # 🎯 核心数据类型
│       └── types.py        # 统一数据流和配置模型
├── freecad-parametric-mcp/  # FreeCAD MCP 服务器插件
│   ├── src/freecad_parametric_mcp/  # MCP服务器实现
│   ├── addon/ParametricMCP/        # FreeCAD插件
│   └── examples/                    # 示例脚本
├── data/                    # 数据文件
│   ├── materials.json      # 材料库
│   ├── languages.json      # 多语言包
│   └── config.yaml         # 默认配置
├── knowledge/              # Markdown格式知识库（RAG向量源）
├── scripts/                # 工具脚本
│   ├── setup/              # 安装和初始化脚本
│   ├── tools/              # 开发工具（API文档生成等）
│   └── mcp/                # MCP相关脚本
├── tests/                  # 测试
│   ├── test_cli.py         # CLI测试
│   ├── integration/        # 集成测试
│   ├── mcp/               # MCP服务器测试
│   └── unit/              # 单元测试
├── examples/               # 示例
│   └── project.yaml        # 标准化配置文件示例
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

# 安装SSH增强功能
pip install -e ".[ssh]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_cli.py -v
pytest tests/test_workflow_integration.py -v

# 运行新架构测试
python tests/integration/connectors/test_freecad_connector.py
python tests/integration/connectors/test_calculix_connector.py
python tests/integration/connectors/test_gmsh.py

# 运行MCP服务器测试
python tests/mcp/test_mcp_simple.py
python tests/mcp/test_mcp_basic.py

# 运行工作流演示
python scripts/tools/demo_workflow.py
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
mypy src/sw_helper src/integrations src/core
```

### 运行CLI

```bash
# 查看帮助
cae-cli --help

# 或使用Python模块方式
python -m sw_helper --help
```

### 脚本工具

```bash
# 初始化SQLite数据库
python scripts/setup/init_sqlite_db.py

# 生成API文档
python scripts/tools/generate_api_docs.py

# 测试依赖
python -m sw_helper.utils.dependency_checker
```

## 核心架构

### 插件化架构 (全新)

#### 1. 标准化接口
- `CADConnector`：CAD软件连接器抽象基类（位于 `src/integrations/_base/connectors.py`）
- `CAEConnector`：CAE软件连接器抽象基类
- `WorkflowEngine`：工作流引擎，管理CAD→CAE完整分析流程
- 支持通过继承抽象类轻松集成新软件

#### 2. 已实现的连接器
- **CAD: FreeCAD**：标准化连接器，支持参数修改、重建、导出
- **CAE: CalculiX**：开源有限元分析软件集成
- **网格生成: Gmsh**：标准化网格生成器集成

#### 3. 配置驱动
使用 YAML 配置文件定义完整仿真流程：
```yaml
# examples/project.yaml
project:
  name: "支架静力分析"
  description: "分析支架在载荷下的应力和变形"

cad:
  software: "freecad"
  model: "bracket.FCStd"
  parameters:
    thickness: 5.0    # mm
    fillet_radius: 3.0 # mm

mesh:
  element_size: 2.0
  element_type: "tetrahedron"

material:
  name: "Q235"

analysis:
  type: "static"
  solver: "calculix"
```

#### 4. 双集成架构说明
项目包含两套集成接口：
- **旧接口**（`src/sw_helper/integrations/`）：保留兼容性，包含 SolidWorks 和 FreeCAD 的原始实现
- **新接口**（`src/integrations/`）：插件化架构，推荐使用，提供更好的扩展性和标准化

### MCP (Model Context Protocol) 服务器

项目包含多个 MCP 服务器，用于与 AI 系统集成：

#### 1. FreeCAD MCP 服务器
- 位置：`src/sw_helper/mcp/freecad_server.py`
- 功能：将 FreeCAD 建模功能暴露为 MCP 工具
- 使用场景：AI 智能调用 FreeCAD 进行建模

#### 2. GitHub 仓库 MCP 服务器
- 位置：`src/sw_helper/mcp/github_server.py`
- 功能：管理 `https://github.com/yd5768365-hue/caw-cli.git` 仓库
- 工具：文件操作（读取/写入/创建/删除）、Git 操作（提交/推送/拉取/分支管理）

#### 3. SSH 增强 MCP 服务器
- 位置：`src/sw_helper/mcp/ssh_server.py`
- 功能：
  - SSH 密钥管理（生成/获取/测试）
  - SSH 主机密钥修复
  - 网络诊断
  - 基于 SSH 的 Git 操作（更稳定）
- 依赖：可选安装 `paramiko` 用于高级 SSH 测试

#### 4. SQLite MCP 服务器
- 位置：`src/sw_helper/mcp/sqlite_server.py`
- 功能：
  - 材料数据库查询
  - 知识库全文搜索（FTS）
  - 计算历史管理
  - 数据库备份
- 默认数据库路径：`data/cae.db`

#### 5. MCP 核心框架
- 位置：`src/sw_helper/mcp/core.py`
- 功能：
  - `MCPServer`：基础 MCP 服务器类
  - `MCPClient`：MCP 客户端类
  - `InMemoryMCPTransport` / `InMemoryMCPClient`：内存传输（用于测试）
  - `Tool` / `Resource`：工具和资源定义

### 知识库系统

项目使用双层知识库架构：

#### 1. Markdown 知识库（`knowledge.py`）
- 位置：`src/sw_helper/knowledge.py`
- 功能：基于关键词搜索的 Markdown 知识库
- 存储位置：`knowledge/` 目录
- 支持的功能：
  - 关键词搜索
  - 材料信息查询
  - 螺栓规格查询
  - 公差配合查询

#### 2. RAG 向量知识库（`rag_engine.py`）
- 位置：`src/sw_helper/utils/rag_engine.py`
- 功能：基于 ChromaDB + sentence-transformers 的向量检索
- 向量存储：`knowledge/chroma_db/`
- 模型：`all-MiniLM-L6-v2`（支持自定义模型路径）
- 使用场景：AI 学习模式的智能检索

### 工具模块

#### 1. 依赖检查器（`dependency_checker.py`）
- 位置：`src/sw_helper/utils/dependency_checker.py`
- 功能：
  - 检查核心依赖安装状态
  - 友好的错误提示和安装命令
  - 功能降级支持（如 meshio → trimesh）
  - Rich 表格化状态报告

#### 2. 编码辅助器（`encoding_helper.py`）
- 功能：解决 Windows 终端编码问题
- 支持：Unicode 回退数据、编码自动检测

#### 3. 错误处理器（`error_handler.py`）
- 功能：统一的错误处理和用户友好的错误消息
- 特点：结构化错误信息、建议解决方案

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

### 4. 力学计算 (mechanics)
- 支持 Von Mises 应力、主应力、最大剪应力计算
- 基于材料伸长率的脆性/塑性智能判定
- 单位自动转换（Pint 库支持）
- 安全系数计算与颜色预警（红/黄/绿）
- 支持屈曲分析和挠度计算

### 5. 报告生成 (report)
- 支持 HTML、PDF、JSON、Markdown 格式
- 分析类型：静力、模态、热、屈曲分析
- 支持自定义模板

### 6. 参数优化 (optimization)
- 自动调整设计参数并评估质量
- 支持 FreeCAD 和 SolidWorks
- 优化流程：参数修改 → 重建 → 导出 → 分析 → 报告

### 7. AI辅助设计 (ai)
- 文本到 3D 模型生成（自然语言描述 → FreeCAD 建模）
- AI 优化建议
- 集成多个 LLM 提供商（OpenAI、Anthropic、Ollama 等）

### 8. 交互式聊天 (chat)
- 类似 OpenCode 的交互式 AI 助手
- 自然语言控制 FreeCAD 建模
- 实时质量分析反馈

### 9. AI 学习助手 (🔥 最新功能)
- **本地 AI 模型集成**：支持 Ollama 本地模型 (qwen2.5:1.5b / phi3:mini)
- **RAG 知识检索**：使用 ChromaDB + sentence-transformers 向量化知识库，智能检索相关知识
- **教学式回答**：专业机械学习助手，用中文教学式、一步步回答，适合大一学生
- **多轮对话**：自动保存对话历史，支持上下文连贯的深度问答
- **自动服务启动**：进入学习模式自动检测并启动 Ollama 服务
- **知识库增强**：每次提问前先检索 knowledge/ 目录的 Markdown 知识库，结合知识库内容回答
- **智能模型检测**：自动检测可用模型，优先使用 qwen2.5:1.5b，回退到 phi3:mini

### 10. 工作流管理 (workflow)
- 标准化 CAD→CAE 分析流程管理
- 支持预定义和自定义工作流
- 完整的步骤级错误处理和进度跟踪

## 常用命令示例

### 基础命令

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

# 启动交互式聊天（包含工作模式和学习模式）
cae-cli interactive --lang zh

# 在交互模式中选择"学习模式"使用AI学习助手：
# 1. 基于本地Ollama模型的智能问答（qwen2.5:1.5b/phi3:mini）
# 2. RAG知识检索：自动检索knowledge/目录的机械知识库
# 3. 教学式回答：适合大一学生的教学式、一步步解释
# 4. 多轮对话：自动保存对话历史，支持深度问答
# 5. 自动服务启动：自动检测并启动Ollama服务
```

### 插件化架构使用

```python
# Python API 使用新架构
from integrations import WorkflowEngine
from integrations.cad.freecad import FreeCADConnector
from integrations.cae.calculix import CalculiXConnector
from core.types import SimulationConfig

# 创建连接器
cad = FreeCADConnector()
cae = CalculiXConnector()

# 创建工作流引擎
workflow = WorkflowEngine(cad_connector=cad, cae_connector=cae)

# 加载配置
config = SimulationConfig.from_yaml("project.yaml")

# 运行工作流
result = workflow.run_workflow(
    "stress_analysis",
    cad_software="freecad",
    cae_software="calculix",
    config=config
)

# 查看结果
print(f"最大应力: {result.max_stress} Pa")
print(f"最大位移: {result.max_displacement} m")
print(f"安全系数: {result.safety_factor}")
```

### MCP 服务器使用

#### GitHub MCP 服务器

```python
from sw_helper.mcp import get_github_mcp_server
from sw_helper.mcp.core import InMemoryMCPTransport, InMemoryMCPClient
import asyncio

async def manage_repository():
    github_server = get_github_mcp_server()
    transport = InMemoryMCPTransport(github_server.server)
    client = transport.create_client()
    await client.connect()

    # 获取仓库信息
    repo_info = await client.call_tool("github_repo_info", {})

    # 读取文件
    readme = await client.call_tool("github_read_file", {
        "file_path": "README.md"
    })

    # Git 操作
    await client.call_tool("github_git_add", {"files": ["README.md"]})
    await client.call_tool("github_git_commit", {"message": "更新文档"})
```

#### SQLite MCP 服务器

```python
from sw_helper.mcp import get_sqlite_mcp_server

# 获取 SQLite MCP 服务器
sqlite_server = get_sqlite_mcp_server()

# 查询材料
materials = await client.call_tool("sqlite_query_materials", {
    "name": "Q235",
    "limit": 10
})

# 知识库搜索
results = await client.call_tool("sqlite_search_knowledge", {
    "query": "螺栓规格",
    "limit": 5
})
```

#### SSH MCP 服务器

```python
from sw_helper.mcp import get_ssh_mcp_server

# 获取 SSH MCP 服务器
ssh_server = get_ssh_mcp_server()

# 检查 SSH 配置
config = await client.call_tool("ssh_check_config", {})

# 生成 SSH 密钥
key = await client.call_tool("ssh_generate_key", {
    "key_type": "ed25519",
    "email": "user@example.com"
})

# 测试 SSH 连接
connection = await client.call_tool("ssh_test_connection", {
    "host": "github.com"
})
```

### FreeCAD Parametric MCP 插件

项目包含一个独立的 FreeCAD MCP 服务器插件：
- 位置：`freecad-parametric-mcp/`
- 功能：
  - 参数管理（获取/设置参数）
  - 草图操作（创建/编辑草图）
  - 特征操作（拉伸、旋转、扫掠）
  - 特征族管理
  - 历史记录查看
  - 模板应用

## 配置文件

配置文件位于 `~/.cae-cli/config.json`，支持自定义：
```json
{
  "default_material": "Q235",
  "safety_factor": 1.5,
  "default_output_format": "html",
  "verbose": false
}
```

## 开发注意事项

1. 项目使用 Python 3.8+，遵循 Black 代码风格
2. 所有 CLI 命令通过 Click 库实现
3. 使用 Rich 库提供美观的终端输出
4. 重要功能都有对应的测试用例
5. 支持可选依赖安装（[full] 包含所有功能，[ssh] 包含 SSH 功能）
6. 新架构采用插件化设计，通过实现抽象基类扩展功能
7. 配置驱动的工作流管理，支持复杂仿真流程的标准化
8. 双集成架构：新代码应使用 `src/integrations/`，旧接口 `src/sw_helper/integrations/` 保持兼容性
9. MCP 服务器使用统一的 `InMemoryMCPTransport` 进行测试
10. 知识库支持两种方式：Markdown 关键词搜索和 RAG 向量检索
