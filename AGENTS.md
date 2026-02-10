# AGENTS.md - CAE-CLI 项目开发指南

本文档为在 CAE-CLI 项目中工作的 AI 代理提供开发指南，包括构建命令、测试流程、代码风格约定和最佳实践。

## 项目概述

CAE-CLI 是一个专业的 CAE（计算机辅助工程）命令行工具，集成了 SolidWorks、FreeCAD 及各类建模/仿真软件，提供几何解析、网格分析、材料数据库、力学计算和报告生成等功能。

- **项目类型**: Python CLI 工具
- **Python 版本**: >= 3.8
- **包管理器**: pip + setuptools (pyproject.toml)
- **代码风格**: Black (行长度100), 类型提示 (mypy)
- **测试框架**: pytest

## 构建与开发命令

### 安装依赖

```bash
# 基础安装（最小依赖）
pip install -e .

# 安装完整功能版（包含几何处理）
pip install -e ".[full]"

# 安装开发依赖（推荐）
pip install -e ".[dev]"

# 仅安装网格分析工具
pip install -e ".[tools]"

# 仅安装优化功能
pip install -e ".[optimize]"
```

### 运行 CLI

```bash
# 查看帮助
cae-cli --help

# 使用 Python 模块方式（如果 PATH 有问题）
python -m sw_helper --help

# 查看版本
cae-cli version

# 查看系统信息
cae-cli info
```

## 测试命令

### 运行测试套件

```bash
# 运行所有测试（默认配置）
pytest

# 详细输出，显示短跟踪回溯
pytest -v --tb=short

# 运行特定测试文件
pytest tests/test_cli.py -v

# 运行特定测试函数
pytest tests/test_cli.py::test_parse_command -v

# 运行特定测试类
pytest tests/test_cli.py::TestCLI -v

# 运行测试并生成覆盖率报告
pytest --cov=src/sw_helper --cov-report=term-missing

# 仅运行上次失败的测试
pytest --lf

# 运行测试并快速失败
pytest -x
```

### 测试配置

- **测试路径**: `tests/`
- **测试文件模式**: `test_*.py`
- **测试类模式**: `Test*`
- **测试函数模式**: `test_*`
- **默认选项**: `-v --tb=short`（已在 pyproject.toml 中配置）

## 代码质量工具

### 代码格式化

```bash
# 使用 Black 格式化代码
black src/

# 检查格式问题（不修改文件）
black --check src/

# 格式化特定文件
black src/sw_helper/cli.py

# 检查特定文件
black --check src/sw_helper/material/database.py
```

**Black 配置**:
- 行长度: 100 字符
- Python 版本: 3.8+
- 排除目录: `.eggs`, `.git`, `.hg`, `.mypy_cache`, `.tox`, `.venv`, `build`, `dist`

### 类型检查

```bash
# 运行 mypy 类型检查
mypy src/sw_helper

# 检查特定模块
mypy src/sw_helper/material/

# 使用严格模式（项目已配置为严格模式）
mypy --strict src/sw_helper/
```

**mypy 配置**:
- `python_version = "3.8"`
- `disallow_untyped_defs = true`
- `disallow_incomplete_defs = true`
- `check_untyped_defs = true`
- `no_implicit_optional = true`

### Linting

```bash
# 运行 flake8（如果安装）
flake8 src/

# 运行 ruff（如果安装）
ruff check src/
ruff format --check src/
```

## 代码风格指南

### 导入顺序

1. 标准库导入
2. 第三方库导入
3. 本地应用/库导入

每组导入之间用空行分隔，按字母顺序排列：

```python
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import click
import numpy as np
from rich.console import Console
from rich.table import Table

from .database import MaterialDatabase
from .calculator import MechanicsCalculator
```

### 命名约定

- **类名**: `PascalCase` (`MaterialDatabase`, `GeometryParser`)
- **函数/方法名**: `snake_case` (`get_material`, `calculate_stress`)
- **变量名**: `snake_case` (`material_name`, `elastic_modulus`)
- **常量**: `UPPER_SNAKE_CASE` (`MAX_ITERATIONS`, `DEFAULT_SAFETY_FACTOR`)
- **私有成员**: 前缀下划线 (`_internal_data`, `_calculate_internal()`)
- **模块名**: `snake_case` (`material.py`, `geometry_parser.py`)

### 类型提示

所有函数和方法都应包含类型提示：

```python
def get_material(self, name: str) -> Optional[Dict[str, Any]]:
    """根据名称获取材料数据"""
    return self.materials.get(name)

def calculate_stress(
    self, 
    force: float, 
    area: float, 
    material_name: str
) -> Dict[str, float]:
    """计算应力和安全系数"""
    # ...
```

### 文档字符串

使用 Google 风格文档字符串：

```python
def parse_geometry(file_path: Path, format: Optional[str] = None) -> Dict[str, Any]:
    """解析几何文件并提取信息。

    Args:
        file_path: 几何文件路径
        format: 文件格式（可选，自动检测）

    Returns:
        包含几何信息的字典，如体积、表面积、顶点数

    Raises:
        FileNotFoundError: 文件不存在时
        ValueError: 文件格式不支持时
    """
    # ...
```

### 错误处理

使用具体的异常类型，并提供有用的错误信息：

```python
def load_database(self, db_path: Path) -> None:
    """加载材料数据库"""
    if not db_path.exists():
        raise FileNotFoundError(f"材料数据库文件不存在: {db_path}")
    
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            self.materials = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"材料数据库格式无效: {e}")
    except PermissionError:
        raise PermissionError(f"没有权限读取文件: {db_path}")
```

### 文件编码

始终使用 UTF-8 编码读写文件：

```python
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

### 路径处理

使用 `pathlib.Path` 而不是字符串操作：

```python
from pathlib import Path

config_dir = Path.home() / ".cae-cli"
config_dir.mkdir(exist_ok=True)
config_file = config_dir / "config.json"

if config_file.exists():
    with open(config_file, "r", encoding="utf-8") as f:
        # ...
```

## 项目结构约定

### 模块组织

```
src/sw_helper/
├── cli.py                 # CLI 入口点
├── geometry/              # 几何解析模块
├── mesh/                  # 网格分析模块
├── material/              # 材料力学模块
├── mechanics/             # 力学计算模块
├── report/                # 报告生成模块
├── optimization/          # 参数优化模块
├── ai/                    # AI 辅助设计模块
├── chat/                  # 交互式聊天模块
├── integrations/          # CAD 软件集成模块
├── mcp/                   # MCP 协议接口模块
└── utils/                 # 工具模块
```

### 包结构

每个模块应包含：
- `__init__.py` - 导出公共 API
- 主模块文件（如 `database.py`, `parser.py`）
- 可选：子模块目录

`__init__.py` 示例：
```python
from .database import MaterialDatabase
from .calculator import MechanicsCalculator

__all__ = ["MaterialDatabase", "MechanicsCalculator"]
```

## CLI 开发指南

### Click 约定

- 使用 `@click.group()` 作为主命令组
- 使用 `@cli.command()` 定义子命令
- 提供完整的帮助文本和示例
- 使用 `@click.pass_context` 共享上下文

```python
@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--output", "-o", help="输出文件路径")
@click.pass_context
def parse(ctx, file_path, output):
    """解析几何文件并提取信息。
    
    示例:
        cae-cli parse model.step
        cae-cli parse part.stl -o result.json
    """
    # ...
```

### Rich 输出

使用 Rich 库提供美观的终端输出：

```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()

# 进度条
with Progress() as progress:
    task = progress.add_task("处理中...", total=100)
    # ...

# 表格
table = Table(title="材料属性")
table.add_column("属性", style="cyan")
table.add_column("值", style="green")
table.add_row("弹性模量", "210 GPa")
console.print(table)
```

## 提交前检查

在提交更改前，运行以下命令确保代码质量：

```bash
# 1. 运行测试
pytest

# 2. 格式化代码
black src/

# 3. 类型检查
mypy src/sw_helper

# 4. 确保所有测试通过
```

## 故障排除

### 常见问题

1. **导入错误**: 确保使用 `pip install -e .` 进行开发安装
2. **测试失败**: 检查测试数据文件是否存在于 `test_data/` 目录
3. **类型检查错误**: 确保所有函数都有类型提示
4. **Black 格式化问题**: 运行 `black src/` 自动修复格式

### 环境设置

```bash
# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装开发依赖
pip install -e ".[dev]"
```

## 贡献流程

1. 运行测试确保现有功能正常
2. 为新功能添加测试
3. 遵循代码风格指南
4. 更新文档（CLAUDE.md, README.md）
5. 提交前运行完整检查链

---
*最后更新: 2026-02-11*  
*基于 pyproject.toml, CLAUDE.md 和现有代码分析*