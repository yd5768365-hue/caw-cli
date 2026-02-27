# CAE-CLI 项目详细介绍

## 一、项目概述

### 1.1 项目定位

**CAE-CLI** 是一款专为机械专业学生设计的专业 CAE（计算机辅助工程）命令行工具。项目由一名大一学生发起（从互联网专业转向机械领域），旨在为机械学习者提供一个免费、开源、易用的学习工具平台。

### 1.2 核心理念

| 理念 | 说明 |
|------|------|
| **开源替代** | 使用 FreeCAD、CalculiX 等开源软件替代昂贵的商业软件 |
| **学习为本** | 注重教学式交互，帮助初学者理解复杂概念 |
| **离线可用** | AI 功能支持本地运行，无需网络连接 |
| **插件架构** | 模块化设计，便于扩展新功能 |

### 1.3 目标用户

- 机械专业在校学生
- 从其他专业转入机械领域的学习者
- 预算有限无法购买商业软件的工程师
- 机械设计爱好者

---

## 二、功能体系

### 2.1 核心功能矩阵

```
┌─────────────────────────────────────────────────────────────────┐
│                      CAE-CLI 功能架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  几何解析    │  │  网格分析    │  │  材料数据库  │          │
│  │  • STEP     │  │  • 纵横比    │  │  • GB/T标准 │          │
│  │  • STL      │  │  • 偏斜度    │  │  • Q235/Q345 │          │
│  │  • IGES     │  │  • 正交质量  │  │  • 铝合金    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  力学计算    │  │  参数优化    │  │  报告生成   │          │
│  │  • 应力     │  │  • 圆角优化  │  │  • HTML     │          │
│  │  • 应变     │  │  • 壁厚优化  │  │  • PDF      │          │
│  │  • 安全系数 │  │  • AI辅助    │  │  • JSON     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    AI 学习助手                          │    │
│  │  • 本地 LLM (Ollama/GGUF)  • RAG 知识检索            │    │
│  │  • 教学式问答  • 多轮对话  • 离线可用                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 详细功能说明

#### 📐 几何解析模块 (`sw_helper/geometry/`)

| 功能 | 支持格式 | 输出信息 |
|------|---------|---------|
| 文件解析 | STEP, STL, IGES | 体积、表面积、顶点数、边数、面数 |
| 格式转换 | STEP ↔ STL ↔ IGES | 标准化几何数据 |
| 质量评估 | 完整性检查 | 拓扑分析报告 |

#### 🔍 网格分析模块 (`sw_helper/mesh/`)

| 指标 | 说明 | 评分标准 |
|------|------|---------|
| 纵横比 (Aspect Ratio) | 单元形状质量 | <3 优秀, <5 良好, <10 一般 |
| 偏斜度 (Skewness) | 单元歪斜程度 | <30° 优秀, <45° 良好, <60° 一般 |
| 正交质量 (Orthogonal Quality) | 网格正交性 | >0.7 优秀, >0.5 良好, >0.3 一般 |

#### 🔧 材料数据库 (`sw_helper/material/`)

```
内置材料库 (data/materials.json):
├── 碳素结构钢
│   ├── Q235 (σs=235MPa)
│   ├── Q275 (σs=275MPa)
│   └── Q345 (σs=345MPa) ← 国标
├── 低合金高强度钢
│   ├── Q460 (σs=460MPa)
│   └── Q550 (σs=550MPa)
└── 铝合金
    ├── 6061-T6
    └── 7075-T6
```

#### ⚙️ 力学计算模块 (`sw_helper/mechanics/`)

- **应力分析**: Von Mises 应力、主应力、最大剪应力
- **安全系数**: 基于材料屈服强度的安全系数计算
- **单位转换**: SI / MPa 单位制自动转换
- **智能判定**: 基于材料伸长率自动判断脆性/塑性

#### 🤖 AI 学习助手 (`sw_helper/ai/`)

| 特性 | 说明 |
|------|------|
| **双模式** | Ollama 在线 / GGUF 离线 |
| **模型支持** | qwen2.5:1.5b, phi3:mini |
| **RAG 检索** | ChromaDB + sentence-transformers |
| **教学式回答** | 适合大一学生的逐步讲解 |

#### 📊 报告生成模块 (`sw_helper/report/`)

支持格式: HTML | PDF | JSON | Markdown

#### 🎯 参数优化模块 (`sw_helper/optimization/`)

```
优化流程:
参数设置 → CAD修改 → 网格生成 → 仿真计算 → 结果评估 → 迭代收敛
    ↑                                                          │
    └──────────────────── 循环 ──────────────────────────────┘
```

---

## 三、技术架构

### 3.1 项目结构

```
cae-cli/
├── src/                          # 源代码
│   ├── sw_helper/               # 原有功能模块 (保持兼容)
│   │   ├── cli.py              # CLI 入口
│   │   ├── geometry/           # 几何解析
│   │   ├── mesh/               # 网格分析
│   │   ├── material/           # 材料数据库
│   │   ├── mechanics/          # 力学计算
│   │   ├── optimization/        # 参数优化
│   │   ├── ai/                 # AI 模块
│   │   ├── learning/            # 学习模块
│   │   ├── mcp/                # MCP 服务器
│   │   └── utils/              # 工具函数
│   │
│   ├── integrations/             # 🚀 插件化架构 (推荐)
│   │   ├── _base/             # 抽象基类
│   │   │   ├── connectors.py   # CAD/CAE 连接器
│   │   │   └── workflow.py    # 工作流引擎
│   │   ├── cad/               # CAD 连接器
│   │   │   └── freecad.py     # FreeCAD 连接器
│   │   ├── cae/               # CAE 连接器
│   │   │   └── calculix.py    # CalculiX 连接器
│   │   └── mesher/            # 网格生成器
│   │       └── gmsh.py        # Gmsh 连接器
│   │
│   ├── core/                   # 核心数据类型
│   │   └── types.py           # 统一配置模型
│   │
│   └── gui/                    # GUI 桌面版
│       ├── main_window.py      # 主窗口
│       ├── theme.py            # 主题配置
│       └── pages/              # 页面组件
│
├── data/                        # 数据文件
│   ├── materials.json          # 材料库
│   └── languages.json          # 多语言包
│
├── knowledge/                   # Markdown 知识库
│   ├── 机械设计手册/
│   ├── materials.md           # 材料笔记
│   ├── mechanics.md           # 力学笔记
│   └── ...
│
├── tests/                      # 测试套件
│   ├── unit/                 # 单元测试
│   ├── integration/           # 集成测试
│   └── mcp/                 # MCP 测试
│
├── freecad-parametric-mcp/    # FreeCAD MCP 插件
│   ├── src/                  # MCP 服务器
│   └── addon/                # FreeCAD 插件
│
└── pyproject.toml             # 项目配置
```

### 3.2 插件化架构

```python
# 使用示例: 标准化 CAD→CAE 工作流
from integrations import WorkflowEngine
from integrations.cad.freecad import FreeCADConnector
from integrations.cae.calculix import CalculiXConnector

# 创建连接器
cad = FreeCADConnector()
cae = CalculiXConnector()

# 创建工作流引擎
workflow = WorkflowEngine(cad_connector=cad, cae_connector=cae)

# 运行完整分析流程
result = workflow.run_workflow(
    "stress_analysis",
    cad_software="freecad",
    cae_software="calculix",
    config=config
)
```

### 3.3 MCP 服务器生态

| 服务器 | 功能 | 端口/协议 |
|--------|------|----------|
| FreeCAD MCP | 参数化建模 | STDIO |
| GitHub MCP | 仓库管理 | STDIO |
| SQLite MCP | 知识库/材料库 | STDIO |
| SSH MCP | 远程连接 | STDIO |

### 3.4 技术栈

| 层级 | 技术选型 |
|------|---------|
| CLI 框架 | Click + Rich |
| GUI 框架 | PySide6 + QWebEngineView |
| 数学计算 | NumPy + SciPy |
| 几何处理 | FreeCAD, OCC |
| 网格分析 | Gmsh, meshio |
| 有限元 | CalculiX (开源) |
| AI 引擎 | Ollama, llama-cpp-python |
| 向量数据库 | ChromaDB |
| 嵌入模型 | sentence-transformers |
| 测试框架 | pytest |
| 代码质量 | ruff, mypy, black |

---

## 四、安装与使用

### 4.1 安装方式

```bash
# 方式一: 基础安装
pip install cae-cli

# 方式二: 完整功能 (推荐)
pip install -e ".[full]"

# 方式三: AI 学习助手
pip install -e ".[ai]"

# 方式四: 源码开发安装
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli
pip install -e .
```

### 4.2 快速命令参考

```bash
# 查看帮助
cae-cli --help

# 解析几何文件
cae-cli parse model.step

# 分析网格质量
cae-cli analyze mesh.msh --metric aspect_ratio --metric skewness

# 查询材料
cae-cli material Q235 --property elastic_modulus

# 参数优化
cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 5

# AI 模型生成
cae-cli ai generate "带圆角的立方体，长100宽50高30圆角10"

# 启动 AI 学习助手
cae-cli interactive --lang zh
```

---

## 五、版本演进

| 版本 | 阶段 | 里程碑 |
|------|------|---------|
| v0.1.x | 基础功能 | CLI 框架、基础分析功能 |
| v0.2.0 | 架构重构 | 插件化架构、标准化接口 |
| v0.5.0 | AI 集成 | Ollama 集成、RAG 知识库 |
| v0.8.0 | GUI 桌面版 | PySide6 Web 界面 |
| v0.10.0 | 完整生态 | 文档体系、DevOps 自动化 |

---

## 六、贡献与交流

### 6.1 如何贡献

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'feat: 添加新功能'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

### 6.2 文档体系

- 📖 [QUICKSTART.md](./docs/QUICKSTART.md) - 快速开始
- 📦 [INSTALLATION_GUIDE.md](./docs/INSTALLATION_GUIDE.md) - 安装指南
- ❓ [FAQ.md](./docs/FAQ.md) - 常见问题
- 📚 [API_REFERENCE.md](./docs/API_REFERENCE.md) - API 参考
- 🤝 [CONTRIBUTING.md](./docs/CONTRIBUTING.md) - 贡献指南

---

## 七、总结

**CAE-CLI** 不仅仅是一个命令行工具，更是一个为机械专业学生打造的学习平台。通过整合开源 CAD/CAE 软件、AI 能力和知识库系统，帮助学习者：

- ✅ 降低学习成本（使用免费开源软件）
- ✅ 提升学习效率（自动化分析流程）
- ✅ 增强理解深度（AI 辅助教学）
- ✅ 建立知识体系（个人知识库）

> 🚀 **让我们一起，用开源工具开启机械学习之旅！**
