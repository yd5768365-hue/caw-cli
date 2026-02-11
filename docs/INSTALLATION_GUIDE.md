# CAE-CLI 详细安装指南 📖

本指南提供 **Windows 平台** 下 CAE-CLI 的完整安装说明，包含 Python、CAE-CLI、FreeCAD、CalculiX 的逐步安装教程，以及环境变量配置和验证清单。

**📋 安装概览**：
1. **Python 安装**（必需）
2. **CAE-CLI 安装**（必需）
3. **FreeCAD 安装**（可选，用于 CAD 建模）
4. **CalculiX 安装**（可选，用于有限元分析）
5. **环境变量配置**（推荐）
6. **安装验证**（必需）

预计完成时间：**15-30分钟**

## 系统要求

### 基本要求

- Windows 10/11 64位
- Python 3.8 或更高版本
- 至少 2GB 可用磁盘空间
- 稳定的网络连接（用于下载依赖）

## 1. Python 安装 🐍（必需）

### Windows 逐步安装指南（含截图）

#### 步骤 1：下载 Python 安装程序
1. 访问 **[Python 官方网站](https://www.python.org/downloads/)**
2. 下载 **Windows installer (64-bit)** 版本
3. **推荐版本**：Python 3.10 或 3.11（与 FreeCAD 兼容性最佳）

**📸 截图示意**：
```
[Python官网下载页面截图]
- 显示 "Download Python 3.10.11"
- 点击 "Windows installer (64-bit)" 按钮
```

#### 步骤 2：运行安装程序
1. 双击下载的 `.exe` 文件（如 `python-3.10.11-amd64.exe`）
2. 在安装界面中，**务必勾选**以下选项：
   - ✅ **Add Python 3.10 to PATH**（最重要！）
   - ✅ **Install launcher for all users**（可选）
3. 选择 **Customize installation** 或 **Install Now**

**📸 截图示意**：
```
[Python安装界面截图]
- 显示 "Add Python 3.10 to PATH" 复选框（已勾选）
- 显示 "Install Now" 按钮
```

#### 步骤 3：完成安装
1. 点击 "Install Now" 开始安装
2. 等待进度条完成（约 1-3 分钟）
3. 看到 "Setup was successful" 表示安装成功

#### 步骤 4：验证 Python 安装
打开命令提示符（Win+R → 输入 `cmd` → 回车），输入：

```bash
python --version
pip --version
```

**✅ 预期输出：**
```
Python 3.10.11
pip 23.1.2 from c:\python310\lib\site-packages\pip (python 3.10)
```

**⚠️ 如果出现错误**：
- `python` 命令未找到 → 重新安装并确保勾选 "Add to PATH"
- 版本不匹配 → 检查 PATH 中是否有多个 Python 版本

#### 步骤 3：验证 Python 安装

打开命令提示符（cmd）或 PowerShell，输入：

```bash
python --version
pip --version
```

**预期输出：**
```
Python 3.10.11
pip 23.1.2 from c:\python310\lib\site-packages\pip (python 3.10)
```

## 2. CAE-CLI 安装 🚀

### 方法一：使用 pip 安装（推荐）

```bash
# 基础安装（不含几何处理功能）
pip install cae-cli

# 完整安装（包含所有功能）
pip install "cae-cli[full]"

# 开发安装（从源代码）
pip install -e ".[dev]"
```

### 方法二：从源代码安装

```bash
git clone https://github.com/yourusername/cae-cli.git
cd cae-cli
pip install -e .
```

### 验证安装

```bash
cae-cli --help
```

**预期输出：**
```
Usage: cae-cli [OPTIONS] COMMAND [ARGS]...

  CAE-CLI: SolidWorks CAE Integration Assistant

  Professional CAE tools supporting: - Geometry file parsing (STEP, STL, IGES)
  - Mesh quality analysis - Material database query - Simulation report
  generation - Integration with SolidWorks/FreeCAD

Options:
  --version          Show version info and exit
  -v, --verbose      Enable verbose output mode
  -c, --config PATH  Specify config file path
  --help             Show this message and exit.

Commands:
  ai           AI-assisted design functions
  analyze      Analyze mesh quality
  cad          CAD software integration control
  chat         Start interactive AI assistant (similar to OpenCode)
  config       Manage CLI configuration
  info         Show system information and configuration status
  interactive  Interactive mode - use CAE-CLI through a menu interface
  material     Material database query
  mcp          MCP (Model Context Protocol) tool management
  optimize     Parameter optimization loop - automatically adjust design...
  parse        Parse geometric files and extract information
  report       Generate analysis report
  version      Show version information
  workflow     Run CAD/CAE automation workflow
```

## 3. FreeCAD 安装 🎨（可选，但推荐）

### 为什么安装 FreeCAD？
FreeCAD 是开源的参数化 3D CAD 建模软件，CAE-CLI 使用它进行：
- **CAD模型修改**：调整参数（圆角半径、壁厚等）
- **模型重建**：参数变更后自动重建几何
- **格式转换**：将 `.FCStd` 文件导出为 `.STEP` 格式供CAE分析

### 🖼️ 安装步骤（含截图）

#### 步骤 1：下载 FreeCAD
1. 访问 **[FreeCAD 官方网站](https://www.freecadweb.org/downloads.php)**
2. 选择 **Windows 64-bit** 版本
3. 下载 **FreeCAD 0.20.1** 或更高版本的安装程序
   - 文件大小：约 300-500 MB
   - 文件名：`FreeCAD-0.20.1-WIN-x64-installer-1.exe`

**📸 截图示意**：
```
[FreeCAD下载页面截图]
- 显示版本选择（推荐 0.20.1）
- 显示 "Windows 64-bit" 下载链接
```

#### 步骤 2：运行安装程序
1. 双击安装程序，点击 "Next"
2. **接受许可协议**，点击 "Next"
3. **选择安装类型**：建议选择 "Complete"（完全安装）
4. **选择安装位置**：默认 `C:\Program Files\FreeCAD 0.20`
5. **重要**：勾选以下选项：
   - ✅ **Add FreeCAD to PATH**（方便命令行调用）
   - ✅ **Create desktop shortcut**（创建桌面快捷方式）
6. 点击 "Install" 开始安装

**📸 截图示意**：
```
[FreeCAD安装界面截图]
- 显示 "Add FreeCAD to PATH" 复选框（已勾选）
- 显示安装进度条
```

#### 步骤 3：完成安装
1. 等待安装完成（约 2-5 分钟）
2. 取消勾选 "Launch FreeCAD"（可选）
3. 点击 "Finish"

#### 步骤 4：验证 FreeCAD 安装
```bash
# 验证 FreeCAD 是否可访问
cae-cli cad freecad --info
```

**✅ 预期输出：**
```
FreeCAD 信息
===========
- 版本: 0.20.1
- 安装路径: C:\Program Files\FreeCAD 0.20
- Python绑定: 可用
- 可用性: ✅ 可用
```

**⚠️ 如果显示 "不可用"**：
1. 检查 `FREECAD_PATH` 环境变量
2. 手动设置路径：
   ```bash
   set FREECAD_PATH=C:\Program Files\FreeCAD 0.20
   ```
3. 重启命令行窗口后重试

## 4. CalculiX 安装 🔬（可选，用于有限元分析）

### 为什么安装 CalculiX？
CalculiX 是开源的有限元分析（FEA）软件，CAE-CLI 使用它进行：
- **静力分析**：计算应力、应变、位移
- **模态分析**：计算固有频率和振型
- **热分析**：温度场计算
- **结果提取**：从 `.inp` 文件中提取分析结果

### 🖼️ 安装步骤（含截图）

#### 步骤 1：下载 CalculiX
1. 访问 **[CalculiX 官方网站](http://www.calculix.de/)**
2. 转到 **Downloads** 页面
3. 下载 **Precompiled binaries for Windows**
4. 选择最新版本（如 `ccx_2.21.zip`）
   - 文件大小：约 5-10 MB
   - 文件名：`ccx_2.21.zip`

**📸 截图示意**：
```
[CalculiX下载页面截图]
- 显示 "Precompiled binaries for Windows" 链接
- 显示 ccx_2.21.zip 下载链接
```

#### 步骤 2：解压文件
1. 创建目录 `C:\CalculiX`
2. 将下载的 `ccx_2.21.zip` 解压到此目录
3. 目录结构应为：
   ```
   C:\CalculiX\
   ├── ccx_2.21.exe      # 主程序
   ├── ccx_2.21.tgz      # 源代码（可选）
   └── README.txt        # 说明文档
   ```

#### 步骤 3：配置环境变量（重要！）
1. **打开环境变量设置**：
   - 右键点击 "此电脑" → "属性" → "高级系统设置" → "环境变量"
2. **添加用户变量**：
   - 点击 "新建..."
   - 变量名：`CCX_PATH`
   - 变量值：`C:\CalculiX\ccx_2.21.exe`
   - 点击 "确定"
3. **添加到系统 PATH**：
   - 在 "系统变量" 中找到 `Path` 变量
   - 点击 "编辑..." → "新建"
   - 添加：`C:\CalculiX`
   - 点击 "确定" 保存所有更改

**📸 截图示意**：
```
[环境变量设置界面截图]
- 显示 "CCX_PATH" 变量设置
- 显示 Path 变量中添加的 C:\CalculiX 条目
```

#### 步骤 4：验证 CalculiX 安装
```bash
# 方法1：直接调用 CalculiX
ccx_2.21

# 方法2：通过 CAE-CLI 验证
cae-cli cae calculix --info
```

**✅ 预期输出（方法2）：**
```
CalculiX 信息
============
- 版本: 2.21
- 路径: C:\CalculiX\ccx_2.21.exe
- 可用性: ✅ 可用
- 功能: 静力分析、模态分析、热分析
```

**⚠️ 如果显示 "不可用"**：
1. 检查 `CCX_PATH` 环境变量是否正确
2. 重启命令行窗口使环境变量生效
3. 手动测试：
   ```bash
   C:\CalculiX\ccx_2.21.exe -v
   ```

### 🔄 替代安装方法：使用 Chocolatey
如果你已安装 [Chocolatey](https://chocolatey.org/)（Windows 包管理器），可以一键安装：
```bash
choco install calculix
```

## 5. 环境变量配置 🔧

### 必需环境变量

| 变量名 | 用途 | 默认值 |
|--------|------|--------|
| `CCX_PATH` | 指定 CalculiX 求解器路径 | 自动检测 |
| `FREECAD_PATH` | 指定 FreeCAD 安装路径 | 自动检测 |
| `PYTHONIOENCODING` | 设置 Python 输出编码 | `utf-8` |

### 建议环境变量

```bash
# 设置输出编码（避免 Windows 控制台乱码）
set PYTHONIOENCODING=utf-8

# 或者永久添加到系统变量中
```

## 6. 验证安装 📝

### 完整验证清单

```bash
# 检查所有依赖是否可用
cae-cli info
```

**预期输出示例：**
```
CAE-CLI 系统信息
================

- Python 版本: 3.10.11
- 安装路径: C:\Users\username\AppData\Roaming\Python\Python310\site-packages
- CAE-CLI 版本: 0.2.0

已安装依赖:
============
- rich: 13.3.5 ✅
- click: 8.1.3 ✅
- numpy: 1.23.5 ✅
- pyyaml: 6.0 ✅
- jinja2: 3.1.2 ✅
- pint: 0.22 ✅

CAD/CAE 集成状态:
================
- FreeCAD: 0.20.1 ✅
- CalculiX: 2.21 ✅
```

## 7. 常见问题解决 🛠️

### 问题1：`cae-cli` 命令未找到

**解决方案：**

1. 确保 Python Scripts 目录在 PATH 中
2. 检查路径：`C:\Users\username\AppData\Roaming\Python\Python310\Scripts`
3. 尝试重新安装

### 问题2：FreeCAD 未找到

**解决方案：**

1. 确认 FreeCAD 已正确安装
2. 检查 `FREECAD_PATH` 环境变量
3. 尝试手动设置路径：

```bash
set FREECAD_PATH=C:\Program Files\FreeCAD 0.20
```

### 问题3：CalculiX 未找到

**解决方案：**

1. 确认 CalculiX 已正确解压
2. 检查 `CCX_PATH` 环境变量
3. 尝试手动设置路径：

```bash
set CCX_PATH=C:\CalculiX\ccx_2.21.exe
```

## 8. 快速测试 🚦

### 运行简单测试

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_cli.py -v
```

**预期输出：**
```
collected 3 items

tests/test_cli.py::test_cli PASSED                               [ 33%]
tests/test_workflow_integration.py::test_workflow_with_standalone_mesher PASSED [ 66%]
tests/test_workflow_integration.py::test_workflow_without_mesher PASSED  [100%]
```

## 9. 后续步骤 🎯

### 推荐资源

- [快速开始指南](QUICKSTART.md)
- [API 参考文档](API_REFERENCE.md)
- [常见问题解答](FAQ.md)
- [开发贡献指南](CONTRIBUTING.md)

### 示例项目

```bash
# 运行示例工作流程
python demo_workflow.py
```

## 10. 联系方式 📧

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/yourusername/cae-cli/issues)
- 发送邮件至：your@email.com

## 11. 许可证信息 📄

CAE-CLI 采用 [MIT 许可证](https://opensource.org/licenses/MIT)。

## 12. 更新和升级 📈

### 检查更新

```bash
cae-cli version --check
```

### 升级到最新版本

```bash
pip install --upgrade cae-cli
```

### 卸载 CAE-CLI

```bash
pip uninstall cae-cli
```

## 13. 高级配置 ⚙️

### 配置文件位置

```bash
# 配置文件路径
%APPDATA%\.cae-cli\config.json
```

### 自定义配置

```json
{
  "default_material": "Q235",
  "safety_factor": 1.5,
  "default_output_format": "html",
  "verbose": false
}
```

## 14. 扩展功能 🚀

### 安装可选功能

```bash
# 安装网格分析工具
pip install "cae-cli[tools]"

# 安装优化功能
pip install "cae-cli[optimize]"

# 安装完整功能
pip install "cae-cli[full]"
```