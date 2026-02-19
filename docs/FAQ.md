# CAE-CLI 常见问题解答 🤔

本 FAQ 列出了 CAE-CLI 使用过程中的常见问题、原因及解决方案。问题按出现频率排序。

## 1. `ModuleNotFoundError: No module named 'cae-cli'` 🚫

**问题**：安装后无法使用 `cae-cli` 命令，提示找不到模块。

**原因**：
1. Python Scripts 目录未添加到系统 PATH 中
2. pip 安装失败
3. 安装过程中出现权限问题

**解决方案**：

### 方案 1：检查 PATH（最常见）

```bash
# 查找 Python Scripts 目录
python -m site --user-site
```

**预期输出**（类似）：
```
C:\Users\屁屁不会电脑\AppData\Roaming\Python\Python313\site-packages
```

**解决方案**：
将 Scripts 目录（如 `C:\Users\屁屁不会电脑\AppData\Roaming\Python\Python313\Scripts`）添加到系统 PATH 中。

### 方案 2：重新安装

```bash
# 强制重新安装
pip install --upgrade --force-reinstall cae-cli
```

## 2. `UnicodeEncodeError: 'gbk' codec can't encode` 👓

**问题**：在 Windows 控制台中显示中文时出现编码错误。

**原因**：Windows 控制台默认使用 GBK 编码，而 CAE-CLI 使用 UTF-8 编码。

**解决方案**：

### 方案 1：设置输出编码

```bash
# 临时解决方案（当前会话）
set PYTHONIOENCODING=utf-8
cae-cli --help

# 永久解决方案（添加到系统变量）
# 在系统环境变量中添加 PYTHONIOENCODING=utf-8
```

### 方案 2：修改控制台编码

```bash
chcp 65001  # 设置为 UTF-8 编码
cae-cli material Q235
```

## 3. FreeCAD 无法连接 ❌

**问题**：运行 CAD 命令时提示 `No module named 'FreeCAD'`。

**原因**：
1. FreeCAD 未安装
2. FreeCAD 路径未正确配置
3. Python 版本与 FreeCAD 不兼容

**解决方案**：

### 方案 1：安装 FreeCAD

```bash
# 检查 FreeCAD 可用性
cae-cli cad freecad --info
```

**如果未安装**：
1. 访问 [FreeCAD 官方网站](https://www.freecadweb.org/downloads/) 下载
2. 安装时选择 "Add FreeCAD to PATH"

### 方案 2：手动指定 FreeCAD 路径

```bash
# 设置 FreeCAD 路径（Windows 示例）
set FREECAD_PATH=C:\Program Files\FreeCAD 0.20
cae-cli cad freecad --info
```

## 4. CalculiX 未找到 🔍

**问题**：运行 CAE 命令时提示 `CalculiX not found`。

**原因**：
1. CalculiX 未安装
2. `CCX_PATH` 环境变量未设置
3. 文件路径包含空格

**解决方案**：

### 方案 1：下载预编译版本

1. 访问 [CalculiX 官方网站](http://www.calculix.de/) 下载
2. 解压到 `C:\CalculiX` 目录
3. 设置环境变量：

```bash
set CCX_PATH=C:\CalculiX\ccx_2.21.exe
cae-cli cae calculix --info
```

### 方案 2：使用 Chocolatey（Windows）

```bash
choco install calculix
```

## 5. 几何文件解析失败 📄

**问题**：使用 `parse` 命令解析 STEP/STL 文件时失败。

**原因**：
1. 文件格式不支持
2. 文件损坏
3. 缺少 PythonOCC 依赖

**解决方案**：

### 方案 1：检查文件格式

```bash
# 检查文件扩展名和内容
cae-cli parse model.step --verbose

# 如果是 STL 文件
cae-cli parse model.stl --format stl
```

### 方案 2：安装几何处理依赖

```bash
# 安装完整功能版本
pip install "cae-cli[full]"
```

## 6. 质量评估无输出 📊

**问题**：运行 `analyze` 命令后无输出或报错。

**原因**：
1. 文件路径包含中文或空格
2. 网格文件格式不支持
3. 缺少 meshio 依赖

**解决方案**：

### 方案 1：检查文件路径

```bash
# 使用英文路径和文件名
cae-cli analyze "d:\temp\mesh_1.msh"
```

### 方案 2：验证网格格式

```bash
# 查看文件头信息
head -50 mesh.msh
```

**预期输出**（GMsh 格式）：
```
$MeshFormat
2.2 0 8
$EndMeshFormat
$Nodes
...
```

## 7. 材料属性查询失败 📚

**问题**：使用 `material` 命令查询属性时提示未找到。

**原因**：
1. 材料名称拼写错误
2. 材料数据库未初始化
3. 自定义材料未正确添加

**解决方案**：

### 方案 1：检查材料名称

```bash
# 列出所有可用材料
cae-cli material --list

# 搜索材料
cae-cli material --search "钢"
```

### 方案 2：添加自定义材料

```bash
# 创建材料配置文件（materials.json）
{
  "Q235": {
    "name": "Q235 钢",
    "elastic_modulus": 210000000000,
    "poisson_ratio": 0.3,
    "yield_strength": 235000000,
    "density": 7850
  }
}
```

## 8. 优化命令无响应 ⏳

**问题**：`optimize` 命令长时间运行且无响应。

**原因**：
1. CAD 文件过于复杂
2. 优化参数设置不当
3. 内存不足

**解决方案**：

### 方案 1：简化优化参数

```bash
# 使用较小的迭代次数
cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 3

# 增加迭代间隔
cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --step-size 5
```

### 方案 2：监控资源使用

```bash
# 使用任务管理器监控 CPU 和内存使用
# 确保有足够的资源可用
```

## 9. `TypeError: 'NoneType' object has no attribute` 🐛

**问题**：运行命令时出现 `NoneType` 错误。

**原因**：
1. 输入参数无效
2. 文件路径错误
3. 内部状态未初始化

**解决方案**：

### 方案 1：启用详细模式

```bash
cae-cli parse model.step --verbose
```

### 方案 2：检查参数类型

```bash
# 确保参数值有效
cae-cli mechanics stress --force 1000 --area 0.001 --material Q235
```

## 10. `ImportError: DLL load failed while importing FreeCAD` ⚠️

**问题**：连接 FreeCAD 时出现 DLL 加载失败。

**原因**：
1. Python 版本与 FreeCAD 不兼容
2. FreeCAD 安装不完整
3. 缺少依赖库

**解决方案**：

### 方案 1：检查兼容性

**推荐版本组合**：
- Python 3.8-3.10
- FreeCAD 0.19-0.20

**验证 Python 版本**：
```bash
python --version
```

### 方案 2：重新安装 FreeCAD

```bash
# 卸载并重新安装
# 确保选择与 Python 版本匹配的 FreeCAD 版本
```

## 更多帮助 📞

### 获取支持

**官方渠道**：
- GitHub Issues：https://github.com/yourusername/cae-cli/issues
- Wiki 文档：https://github.com/yourusername/cae-cli/wiki
- QQ 群：[CAE-CLI 技术交流]

**命令行帮助**：
```bash
# 查看完整帮助
cae-cli --help

# 查看特定命令帮助
cae-cli material --help
```

### 报告问题

**问题报告格式**：
```
### 问题描述
使用 cae-cli material 命令时出现错误

### 复现步骤
1. 执行命令 cae-cli material Q235 --property density
2. 出现错误：...

### 系统信息
- Windows 11
- Python 3.10
- CAE-CLI 0.2.0
- FreeCAD 0.20

### 错误信息
完整的错误堆栈信息
```