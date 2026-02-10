# CAE-CLI

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

🚀 **SolidWorks CAE集成助手** - 专业的CAE命令行工具，集成SolidWorks、FreeCAD及各类建模/仿真软件。

## ✨ 特性

- 🎯 **几何解析** - 支持STEP、STL、IGES等格式的几何文件解析
- 📊 **网格分析** - 网格质量评估与指标计算
- 📚 **材料数据库** - 内置GB/T标准材料库（Q235、Q345、铝合金等）
- 🔧 **力学计算** - 应力、应变、屈曲等计算工具
- 📄 **报告生成** - 自动生成JSON/HTML/PDF格式的分析报告
- 🎨 **美观界面** - 使用Rich库提供彩色表格和进度条
- ⚙️ **配置管理** - 支持用户自定义配置

## 📦 安装

### 方式一：从 PyPI 安装（推荐）

```bash
pip install cae-cli
```

### 方式二：从源码安装

```bash
git clone https://github.com/yourusername/cae-cli.git
cd cae-cli
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
├── src/sw_helper/           # 主包
│   ├── cli.py              # CLI入口
│   ├── geometry/           # 几何解析
│   ├── mesh/               # 网格分析
│   ├── material/           # 材料力学
│   ├── report/             # 报告生成
│   └── utils/              # 工具模块
├── data/                    # 数据文件
│   ├── materials.json      # 材料库
│   └── config.yaml         # 默认配置
├── tests/                   # 测试
├── examples/                # 示例
├── docs/                    # 文档
├── pyproject.toml          # 项目配置
├── setup.py                # 安装脚本
└── README.md               # 本文件
```

## 🔗 支持的软件集成

### CAD软件
- ✅ SolidWorks (计划支持API)
- ✅ FreeCAD (计划支持API)
- ✅ AutoCAD

### CAE软件
- ✅ ANSYS Workbench
- ✅ Abaqus
- ✅ NASTRAN
- ✅ OpenFOAM

### 网格工具
- ✅ Gmsh
- ✅ Netgen
- ✅ TetGen

## 🛠️ 开发

### 安装开发依赖

```bash
git clone https://github.com/yourusername/cae-cli.git
cd cae-cli
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black src/
```

### 类型检查

```bash
mypy src/sw_helper
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

## 📮 联系方式

- 作者: Your Name
- 邮箱: your.email@example.com
- 项目主页: https://github.com/yourusername/cae-cli
- 文档: https://cae-cli.readthedocs.io

## 🙏 致谢

- [Click](https://click.palletsprojects.com/) - Python CLI框架
- [Rich](https://rich.readthedocs.io/) - 终端美化库
- [PythonOCC](https://github.com/tpaviot/pythonocc-core) - OpenCASCADE Python绑定

---

<p align="center">
  Made with ❤️ for CAE Engineers
</p>
