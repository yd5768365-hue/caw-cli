# AI 开发助手提示词 - CAE-CLI 项目

你是一个专业的Python开发助手，负责帮助开发这个CAE-CLI项目。请仔细阅读以下指南，以便高效地完成开发任务。

---

## 项目概述

**CAE-CLI** 是一个专为机械专业学生设计的专业 CAE（计算机辅助工程）命令行工具。它集成了 FreeCAD、CalculiX 及各类建模/仿真软件，提供几何解析、网格分析、材料数据库、力学计算和报告生成等功能。

### 核心功能模块
- 几何解析 (geometry) - STEP/STL/IGES 格式解析
- 网格分析 (mesh) - 质量评估、纵横比、偏斜度分析
- 材料数据库 (material) - GB/T 标准材料库查询
- 力学计算 (mechanics) - 应力、安全系数、屈曲计算
- 报告生成 (report) - HTML/PDF/JSON/Markdown 格式
- 参数优化 (optimization) - FreeCAD/SolidWorks 参数优化
- AI 辅助设计 (ai) - 自然语言建模、RAG 知识检索
- 交互式聊天 (chat) - 类似 OpenCode 的 AI 助手
- MCP 服务器 - FreeCAD/GitHub/SQLite/SSH 集成

---

## 技术栈

- **Python**: 3.8+
- **CLI框架**: Click
- **终端美化**: Rich
- **单位转换**: Pint
- **数据格式**: PyYAML, JSON, Markdown
- **可选依赖**: meshio, trimesh, gmsh, pythonocc-core, matplotlib, pandas, chromadb, sentence-transformers
- **GUI**: PySide6 + QtWebEngine

---

## 项目结构

```
cae-cli/
├── src/
│   ├── sw_helper/           # 主包
│   │   ├── cli.py          # CLI入口 (核心文件，3300+行)
│   │   ├── geometry/       # 几何解析
│   │   ├── mesh/           # 网格分析
│   │   ├── material/       # 材料力学
│   │   ├── mechanics/      # 力学计算
│   │   ├── report/         # 报告生成
│   │   ├── optimization/   # 参数优化
│   │   ├── ai/             # AI辅助设计
│   │   ├── chat/           # 交互式聊天
│   │   ├── mcp/            # MCP协议接口
│   │   ├── integrations/   # CAD软件集成
│   │   ├── knowledge.py    # 知识库管理
│   │   └── utils/          # 工具模块
│   ├── integrations/        # 插件化架构（新架构）
│   │   ├── _base/          # 抽象基类
│   │   ├── cad/            # CAD连接器
│   │   ├── cae/            # CAE连接器
│   │   └── mesher/         # 网格生成器
│   ├── core/               # 核心数据类型
│   └── gui/                # GUI界面
├── tests/                  # 测试
├── data/                   # 数据文件
├── knowledge/              # Markdown知识库
├── pyproject.toml          # 项目配置
└── CLAUDE.md               # AI开发指南
```

---

## 开发命令

### 安装依赖
```bash
# 基础安装
pip install -e .

# 安装完整功能版
pip install -e ".[full]"

# 安装开发依赖
pip install -e ".[dev]"

# 安装AI功能
pip install -e ".[ai]"

# 安装GUI功能
pip install -e ".[gui]"
```

### 运行测试
```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/unit/test_material.py -v

# 运行代码审查
cae-cli review --local
```

### 代码质量
```bash
# 格式化代码
black src/

# 类型检查
mypy src/sw_helper
```

### 运行CLI
```bash
# 查看帮助
cae-cli --help

# 或使用Python模块
python -m sw_helper --help
```

---

## 代码规范

### 1. 代码风格
- 使用 **Black** 格式化代码 (line-length: 100)
- 使用 **Ruff** 进行lint检查
- 遵循类型注解规范 (Python 3.8+)

### 2. 函数长度限制
- **最大50行**一个函数
- 如果函数确实需要超过50行，添加 `# noqa: PLR0912` 注释
- 优先提取helper函数到模块级别

### 3. 导入顺序
```python
# 1. 标准库
import os
import sys
from pathlib import Path

# 2. 第三方库
import click
from rich.console import Console

# 3. 本地模块
from sw_helper.utils import helper_func
from sw_helper.mesh import MeshAnalyzer
```

### 4. 错误处理
- 使用统一的错误处理模块 `sw_helper/utils/error_handler.py`
- 提供用户友好的错误消息和解决方案建议

### 5. 文档字符串
- 使用 Google 风格的文档字符串
- 包含 Args、Returns、Raises 说明

---

## 关键文件说明

### cli.py (核心入口)
- 定义所有CLI命令 (parse, analyze, material, report, optimize, ai, chat, interactive等)
- 包含rich表格输出、进度显示、错误处理
- **重要**: 长函数已添加 `# noqa: PLR0912` 注释

### pr_review.py (代码审查)
- 静态代码分析工具
- 检测: 函数长度、TODO标记、安全问题、性能问题
- 支持JSON/Markdown报告输出

### dependency_checker.py (依赖检查)
- 检查核心依赖安装状态
- 提供功能降级支持
- Rich表格化状态报告

### knowledge.py (知识库)
- 基于关键词搜索的Markdown知识库
- 存储位置: `knowledge/` 目录

### utils/rag_engine.py (RAG引擎)
- ChromaDB + sentence-transformers 向量检索
- 模型: `all-MiniLM-L6-v2`

---

## 常用开发模式

### 1. 添加新CLI命令
```python
@cli.command()
@click.option("--option", "-o", help="选项说明")
def new_command(ctx, option):
    """命令描述"""
    console = Console()
    console.print(f"[green]执行: {option}[/green]")
    # 业务逻辑
```

### 2. 添加新模块
```python
# src/sw_helper/new_module/__init__.py
from .new_class import NewClass

__all__ = ["NewClass"]
```

### 3. 添加单元测试
```python
# tests/unit/test_new_module.py
import pytest
from sw_helper.new_module import NewClass

class TestNewClass:
    def test_basic(self):
        obj = NewClass()
        assert obj is not None
```

---

## 注意事项

1. **不要修改 CLAUDE.md** - 这是AI开发指南
2. **不要硬编码敏感信息** - 使用配置文件或环境变量
3. **保持向后兼容** - 考虑现有API的兼容性
4. **优先使用现有模块** - 避免重复造轮子
5. **添加测试** - 新功能必须有对应的测试用例

---

## 快速开始

1. 克隆项目
2. 安装依赖: `pip install -e ".[dev]"`
3. 运行测试: `pytest`
4. 查看帮助: `cae-cli --help`
5. 代码审查: `cae-cli review --local`

---

## 获取帮助

- 查看CLI帮助: `cae-cli --help`
- 查看子命令帮助: `cae-cli <command> --help`
- 运行代码审查: `cae-cli review --local`
- 运行单元测试: `pytest tests/`

---

**提示**: 在进行任何修改前，先运行 `cae-cli review --local` 了解当前代码状态。完成后确保所有测试通过。
