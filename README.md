# cae-cli - 机械设计学习辅助 CLI 工具 🛠️

## 🎯 项目目的与背景

### 为什么创建这个工具？

**CAE-CLI** 是为机械专业学生（特别是从互联网专业转向机械领域的学习者）设计的专业命令行工具。作为一个大一学生，我在学习机械设计时遇到了几个痛点：

1. **缺少商业软件许可证**：无法使用 SolidWorks，需要替代方案
2. **学习曲线陡峭**：机械设计、有限元分析、材料力学概念复杂
3. **缺乏系统学习工具**：需要一个整合的工具来辅助学习全过程
4. **软件集成困难**：不同CAD/CAE软件接口不统一，难以建立标准化工作流

### 🎓 用户背景
- **身份**：大一学生，从互联网专业转向机械专业
- **软件**：正在学习 FreeCAD（开源替代 SolidWorks）
- **目标**：系统学习机械设计、有限元分析、材料力学等专业知识

### 📚 核心学习目标
| 目标 | 具体内容 | 实现状态 |
|------|----------|----------|
| ✅ **网格质量分析** | 快速评估模型网格质量，理解网格参数对分析结果的影响 | ✅ 已实现 |
| ✅ **材料力学计算** | 查询材料性能参数，计算应力、应变、安全系数等 | ✅ 已实现 |
| ✅ **参数优化** | 自动优化设计参数，寻找最佳设计方案 | ✅ 已实现 |
| ✅ **知识库管理** | 建立个人机械设计知识库，随时查询 | ✅ 已实现 |
| ✅ **报告生成** | 自动生成分析报告，整理学习笔记 | ✅ 已实现 |
| 🌟 **多语言支持** | 交互界面支持中文/英文切换，适应不同语言习惯 | ✅ 新功能 |
| 🚀 **插件化架构** | 标准化CAD/CAE软件接口，支持自由扩展软件集成 | ✅ **新增功能** |

---

一个专为机械专业学生设计的终端工具，帮助快速分析 SolidWorks/FreeCAD 模型的网格质量、材料力学性能、参数优化，并集成 AI 建议和个人机械手册知识库。**新增插件化架构**，支持标准化CAD/CAE软件集成。

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 核心功能

### 🎯 **模型分析与优化**
- **几何文件解析**：支持 STL/STEP/IGES 格式，提取体积、表面积、顶点数等几何信息
- **网格质量评估**：分析纵横比、偏斜度、正交质量等指标，提供质量评分（优秀/良好/一般/较差）
- **参数自动优化**：自动迭代修改参数（圆角半径、壁厚等），寻找最佳质量/强度方案
- **力学性能计算**：计算许用应力、安全系数、屈曲载荷等

### 🤖 **AI 辅助设计**
- **AI模型生成**：自然语言描述 → FreeCAD 建模（"带圆角的立方体，长100宽50高30圆角10"）
- **智能建议**：基于分析结果提供专业中文建议
- **自动建模**：规划中的自动建模功能

### 🎮 **交互式学习体验**
- **交互模式**：菜单式操作，新手友好
- **多语言界面**：🔴 **新功能** 支持中英文界面切换（`--lang zh/en`）
- **实时反馈**：操作过程中提供即时质量分析建议
- **命令学习**：支持直接命令行输入和菜单操作两种模式

### 📚 **机械知识库管理**
- **材料数据库**：内置 GB/T 标准材料库（Q235、Q345、铝合金等）
- **手册查询**：本地 Markdown 知识库，查询材料参数、螺栓规格、公差、疲劳强度
- **单位转换**：支持 SI/MPa 单位系统自动转换

### 📊 **报告与输出**
- **多格式报告**：支持 HTML/PDF/JSON/Markdown 格式
- **可视化图表**：质量分曲线、应力分布图等
- **分析类型**：静力、模态、热、屈曲分析报告

### 🧩 **插件化架构** (🔥 **全新功能**)
- **标准化接口**：统一的CAD/CAE抽象基类，支持自由扩展软件集成
- **工作流引擎**：标准化的CAD→CAE分析流程管理，支持预定义和自定义工作流
- **配置驱动**：YAML配置文件定义完整仿真流程，支持复杂参数设置
- **多软件支持**：已实现FreeCAD、CalculiX集成，可扩展支持更多软件



## 📦 安装

### 方式一：从 PyPI 安装（推荐）

```bash
pip install cae-cli
```

### 方式二：从源码安装

```bash
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli
pip install -e .

# 或运行安装脚本
python install.py
```

### 方式三：安装完整功能版

```bash
# 包含几何处理和网格分析的所有功能
pip install "cae-cli[full]"
```

### 系统要求

- Python >= 3.8
- Windows / Linux / macOS
- 可选：SolidWorks、FreeCAD、ANSYS、Abaqus

## 🚀 快速开始

### 查看帮助

```bash
cae-cli --help
```

### 1. 几何文件解析

```bash
# 解析STEP文件
cae-cli parse model.step

# 指定格式并保存结果
cae-cli parse part.stl --format stl --output result.json

# 表格形式显示
cae-cli parse assembly.step --format-output table
```

### 2. 材料数据库查询

```bash
# 列出所有材料
cae-cli material --list

# 查询特定材料
cae-cli material Q235

# 查询特定属性
cae-cli material Q235 --property elastic_modulus

# 搜索材料
cae-cli material --search "钢"
```

### 3. 网格质量分析

```bash
# 分析网格文件
cae-cli analyze mesh.msh

# 指定质量指标
cae-cli analyze mesh.inp --metric aspect_ratio --metric skewness

# 设置阈值并保存报告
cae-cli analyze mesh.msh --threshold 0.05 --output quality_report.json
```

### 4. 生成分析报告

```bash
# 生成静力分析报告（HTML格式）
cae-cli report static --input result.inp --output report.html

# 生成模态分析报告（JSON格式）
cae-cli report modal --input eigenvalues.txt --format json

# 指定报告标题
cae-cli report thermal --input thermal.rth --title "热分析报告"
```

### 5. 配置管理

```bash
# 查看配置
cae-cli config --list

# 设置配置项
cae-cli config --set default_material Q345
cae-cli config --set safety_factor 2.0

# 获取配置项
cae-cli config --get default_material

# 重置配置
cae-cli config --reset
```

### 6. 系统信息

```bash
# 查看系统信息和状态
cae-cli info

# 查看版本
cae-cli version
cae-cli version --check
```

### 7. 交互模式（多语言支持）

```bash
# 启动中文界面交互模式（默认）
cae-cli interactive --lang zh

# 启动英文界面交互模式
cae-cli interactive --lang en

# 使用交互模式进行模型分析
# 在交互界面中可以直接选择菜单选项：
# 1. 分析模型
# 2. 参数优化
# 3. AI生成模型
# 4. 知识库查询
# 5. 退出

# 也可以在交互模式中直接输入命令
# 例如直接输入：analyze model.step --material Q235
```

## 📖 命令参考

### 全局选项

| 选项 | 说明 |
|------|------|
| `--version`, `-v` | 显示版本信息 |
| `--verbose` | 启用详细输出模式 |
| `--config` | 指定配置文件路径 |
| `--help` | 显示帮助信息 |

### 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `parse` | 解析几何文件 | `cae-cli parse model.step` |
| `analyze` | 分析网格质量 | `cae-cli analyze mesh.msh` |
| `material` | 查询材料数据库 | `cae-cli material Q235` |
| `report` | 生成分析报告 | `cae-cli report static -i result.inp` |
| `config` | 管理配置 | `cae-cli config --list` |
| `version` | 显示版本 | `cae-cli version` |
| `info` | 系统信息 | `cae-cli info` |
| `interactive` | 交互模式（支持多语言） | `cae-cli interactive --lang zh` |

## 🔧 Python API

除了CLI，你也可以在Python代码中使用：

```python
from sw_helper.geometry import GeometryParser
from sw_helper.material import MaterialDatabase, MechanicsCalculator

# 解析几何
parser = GeometryParser()
geo_data = parser.parse("model.step")
print(f"体积: {geo_data['volume']} m³")

# 查询材料
db = MaterialDatabase()
q235 = db.get_material("Q235")
print(f"弹性模量: {q235['elastic_modulus']} Pa")

# 力学计算
calc = MechanicsCalculator()
result = calc.calculate_stress(
    force=10000,  # 10kN
    area=0.001,   # 0.001 m²
    material_name="Q235"
)
print(f"安全系数: {result['safety_factor']}")
```

## 📁 项目结构

```
cae-cli/
├── src/sw_helper/           # 主包（原有功能）
│   ├── cli.py              # CLI入口（核心文件）
│   ├── geometry/           # 几何解析模块
│   ├── mesh/               # 网格分析模块
│   ├── material/           # 材料力学模块
│   ├── report/             # 报告生成模块
│   ├── optimization/       # 参数优化模块
│   ├── ai/                 # AI辅助设计模块
│   ├── chat/               # 交互式聊天模块
│   ├── integrations/       # CAD软件集成模块（旧接口）
│   ├── mcp/                # MCP协议接口模块
│   └── utils/              # 工具模块
├── src/integrations/       # 🚀 插件化架构（全新）
│   ├── _base/              # 抽象基类
│   │   ├── connectors.py   # CAD/CAE连接器抽象基类
│   │   └── workflow.py     # 工作流引擎
│   ├── cad/                # CAD连接器实现
│   │   ├── freecad.py      # FreeCAD连接器（新架构）
│   │   └── __init__.py
│   ├── cae/                # CAE连接器实现
│   │   ├── calculix.py     # CalculiX连接器（新架构）
│   │   └── __init__.py
│   └── __init__.py         # 统一导出
├── src/core/               # 🎯 核心数据类型
│   └── types.py           # 统一数据流和配置模型
├── examples/               # 示例文件
│   ├── project.yaml       # 标准化配置文件示例
│   └── demo_config_usage.py # 配置系统使用演示
├── data/                   # 数据文件
│   ├── materials.json     # 材料库
│   ├── languages.json     # 多语言包
│   └── config.yaml        # 默认配置
├── tests/                  # 测试
├── docs/                   # 文档
├── pyproject.toml         # 项目配置
├── setup.py               # 安装脚本
└── README.md              # 说明文档
```

## 🔗 软件集成与协议

### 🎯 **插件化架构**
- **标准化接口**：统一的`CADConnector`和`CAEConnector`抽象基类
- **灵活扩展**：通过实现抽象方法轻松集成新软件
- **工作流管理**：`WorkflowEngine`管理CAD→CAE完整分析流程
- **配置驱动**：YAML配置文件定义完整仿真参数和工作流

### 🔧 **已实现的连接器**
- **✅ CAD: FreeCAD**：基于新架构的标准化连接器，支持参数修改、重建、导出
- **✅ CAE: CalculiX**：开源有限元分析软件集成，支持静力、模态、热分析
- **🔄 旧接口兼容**：原有FreeCAD/SolidWorks连接器保持可用

### 🔄 **标准数据流**
- **格式标准化**：遵循 `CAD → STEP → MSH → INP → VTK` 数据流路径
- **统一配置**：`SimulationConfig`模型管理所有仿真参数
- **结果标准化**：`SimulationResult`统一结果数据格式

### 🤝 **工作流支持**
- **预定义工作流**：`stress_analysis`, `modal_analysis`, `topology_optimization`
- **自定义工作流**：支持用户定义任意分析流程
- **异常处理**：完整的步骤级错误处理和进度跟踪

### 📊 **仿真工具链**
- **Gmsh**：开源网格生成器（规划中集成）
- **CalculiX**：开源有限元分析（已实现）
- **通用格式支持**：.inp (Abaqus/CalculiX), .bdf (NASTRAN), .msh (Gmsh)

## 🚀 插件化架构使用

### 1. 配置文件示例
创建 `project.yaml` 定义完整仿真流程：

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
  properties:
    - name: "elastic_modulus"
      value: 210e9
      unit: "Pa"

analysis:
  type: "static"
  solver: "calculix"
  
  loads:
    - type: "force"
      value: -1000.0
      direction: [0, 0, -1]
  
  constraints:
    - type: "fixed"
      location: "bottom_surface"
```

### 2. Python API 使用
```python
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

### 3. 扩展新软件
要集成新的CAD软件，继承 `CADConnector` 并实现抽象方法：

```python
from integrations._base.connectors import CADConnector

class MyCADConnector(CADConnector):
    def connect(self) -> bool:
        # 连接软件
        pass
    
    def load_model(self, file_path: Path) -> bool:
        # 加载模型
        pass
    
    def get_parameter(self, name: str) -> Optional[float]:
        # 获取参数
        pass
    
    def set_parameter(self, name: str, value: float) -> bool:
        # 设置参数
        pass
    
    def rebuild(self) -> bool:
        # 重建模型
        pass
    
    def export_step(self, output_path: Path) -> bool:
        # 导出STEP
        pass
    
    def get_supported_formats(self) -> List[FileFormat]:
        # 返回支持的格式
        pass
```

### 4. 快速测试
运行演示脚本查看新架构功能：
```bash
python demo_workflow.py
```

## 🛠️ 开发

### 安装开发依赖

```bash
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行新架构测试
python test_freecad_connector.py
python test_calculix_connector.py

# 运行工作流演示
python demo_workflow.py
```

### 代码格式化

```bash
black src/
```

### 类型检查

```bash
mypy src/sw_helper src/integrations src/core
```

## 📝 配置文件

配置文件位于 `~/.cae-cli/config.json`，可以自定义：

```json
{
  "default_material": "Q235",
  "safety_factor": 1.5,
  "default_output_format": "html",
  "verbose": false
}
```

## 🐛 故障排除

### 安装失败

```bash
# 升级pip
pip install --upgrade pip

# 安装基础版本（不含可选依赖）
pip install cae-cli

# 安装完整版本
pip install "cae-cli[full]"
```

### 命令找不到

```bash
# 确保Python Scripts目录在PATH中
# Windows: %APPDATA%\Python\Python3x\Scripts
# Linux/macOS: ~/.local/bin

# 或直接使用Python模块方式
python -m sw_helper --help
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 📮 联系方式与支持

### 📍 项目信息
- **项目主页**：https://github.com/yd5768365-hue/caw-cli
- **文档站点**：https://caw-cli.readthedocs.io (规划中)
- **PyPI包**：https://pypi.org/project/cae-cli/ (规划中)

### 🐛 问题报告
- **GitHub Issues**：https://github.com/yd5768365-hue/caw-cli/issues
- **功能建议**：欢迎提交Issue描述您的需求

### 🎯 项目状态
- **当前版本**：v0.2.0 (插件化架构发布)
- **主要用户**：机械专业学生、FreeCAD用户、CAE学习者、插件开发者
- **开发进度**：
  - ✅ 基础功能已完成（几何解析、材料计算、网格分析）
  - ✅ AI辅助设计和多语言支持
  - ✅ **插件化架构**：标准化CAD/CAE接口，FreeCAD+CalculiX集成
  - 🔄 工作流CLI命令集成（进行中）
  - 🔄 Gmsh网格生成器集成（规划中）

## 🙏 致谢

- [Click](https://click.palletsprojects.com/) - Python CLI框架
- [Rich](https://rich.readthedocs.io/) - 终端美化库
- [PythonOCC](https://github.com/tpaviot/pythonocc-core) - OpenCASCADE Python绑定

---

<p align="center">
  Made with ❤️ for CAE Engineers
</p>
