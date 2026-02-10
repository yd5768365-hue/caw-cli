# CAE-CLI Optimize 依赖说明

## 核心依赖

以下依赖必须安装：

```bash
pip install click rich
```

- **click**: CLI框架
- **rich**: 终端美化（彩色表格、进度条）

## 可选依赖

### 1. 可视化图表 (--plot)

如果需要生成优化图表：

```bash
pip install matplotlib
```

### 2. FreeCAD 集成

真实FreeCAD模式需要安装 FreeCAD：

**Windows:**
- 下载: https://www.freecad.org/downloads.php
- 安装后设置环境变量: `FREECAD_LIB=C:\Program Files\FreeCAD 0.21\bin`

**Linux:**
```bash
sudo apt-get install freecad-python3
```

**macOS:**
```bash
brew install --cask freecad
```

### 3. 完整功能

安装所有依赖：

```bash
pip install click rich matplotlib numpy
```

## 快速开始

### 方式1: 使用模拟模式（推荐初学者）

无需安装FreeCAD，使用模拟模式测试功能：

```bash
# 安装基础依赖
pip install click rich

# 运行优化（模拟模式）
cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 5 --cad mock
```

### 方式2: 真实FreeCAD模式

```bash
# 安装依赖
pip install click rich matplotlib

# 确保FreeCAD已安装并设置环境变量
export FREECAD_LIB=/usr/lib/freecad-python3/lib  # Linux
# set FREECAD_LIB=C:\Program Files\FreeCAD 0.21\bin  # Windows

# 运行优化
cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 5
```

## 故障排除

### 错误: "未找到FreeCAD"

**解决方案1 - 使用模拟模式:**
```bash
cae-cli optimize model.FCStd -p Radius -r 1 10 --cad mock
```

**解决方案2 - 设置FreeCAD路径:**
```python
import sys
sys.path.append('C:/Program Files/FreeCAD 0.21/bin')
```

### 错误: "ModuleNotFoundError: No module named 'matplotlib'"

安装matplotlib:
```bash
pip install matplotlib
```

或禁用图表功能（不使用--plot参数）

### 错误: "ModuleNotFoundError: No module named 'rich'"

安装rich:
```bash
pip install rich
```

## 依赖版本要求

- Python >= 3.8
- click >= 8.0.0
- rich >= 13.0.0
- matplotlib >= 3.5.0 (可选)
- numpy >= 1.21.0 (可选)
- FreeCAD >= 0.20 (可选)

## 检查安装

运行以下命令检查环境：

```bash
# 检查CAE-CLI安装
cae-cli --version

# 检查FreeCAD连接
cae-cli info

# 测试优化功能（模拟模式）
cae-cli optimize --help
```
