# CAE-CLI 完整功能说明

## 🚀 新功能概览

### 1. AI集成
- **AI几何生成** - 自然语言描述生成参数化几何
- **AI优化建议** - 智能设计改进建议
- **设计变体生成** - 自动生成多个设计方案

### 2. SolidWorks VBA宏集成
- **一键导出** - STEP/STL/IGES格式
- **自动分析** - 导出后自动调用CLI
- **弹窗提示** - 显示报告路径
- **参数化修改** - 支持尺寸驱动设计

### 3. CAD连接器 (pywin32)
- **SolidWorks集成** - COM API连接
- **FreeCAD集成** - Python API连接
- **参数读写** - 实时修改模型参数
- **自动重建** - 修改后自动重建

### 4. 参数优化
- **圆角优化** - R值自动扫描
- **通用参数优化** - 任意参数优化
- **AI辅助优化** - AI指导优化方向
- **结果可视化** - 生成优化图表

## 📦 安装

```bash
# 基础安装
pip install -e .

# 完整功能（包含所有可选依赖）
pip install -e ".[full]"

# 仅CAD连接功能
pip install pywin32
```

## 🎯 使用示例

### 1. 连接CAD软件

```bash
# 自动连接可用的CAD软件
cae-cli cad --connect auto

# 连接SolidWorks
cae-cli cad --connect solidworks

# 打开文件并列出参数
cae-cli cad --open model.sldprt --list-params

# 修改参数并导出
cae-cli cad --open model.sldprt \
  --set-param Fillet_R 10 \
  --rebuild \
  --export output.step
```

### 2. 参数优化

```bash
# 圆角半径优化（5次迭代，R=2~15mm）
cae-cli optimize model.sldprt \
  -p Fillet_R \
  -r 2 15 \
  --steps 5 \
  --cad solidworks

# 通用参数优化
cae-cli optimize bracket.FCStd \
  -p Thickness \
  -r 5 20 \
  --steps 10 \
  --plot \
  --output results.json

# AI辅助优化
cae-cli optimize part.sldprt \
  -p Fillet_R \
  -r 2 15 \
  --steps 5 \
  --ai
```

### 3. AI辅助设计

```bash
# AI生成几何描述
cae-cli ai generate "带圆角的立方体，边长100mm，圆角R5"

# 生成并保存
cae-cli ai generate "L型支架，厚度5mm" -o design.json

# AI优化建议
cae-cli ai suggest --file model.step --target strength
cae-cli ai suggest -f bracket.step --target weight
```

### 4. 生成SolidWorks宏

```bash
# 生成完整集成宏
cae-cli macro ./sw_macros --type full --format step

# 仅导出宏
cae-cli macro ./sw_macros --type export --format stl

# 指定CLI路径
cae-cli macro ./sw_macros --type full --cli-path "C:\Tools\cae-cli"
```

生成的宏功能：
- **CAE_Export.bas** - 一键导出模型
- **CAE_Parametric.bas** - 参数化修改
- **CAE_FullIntegration.bas** - 完整自动化流程

## 🔧 SolidWorks集成工作流程

### 方法一：使用生成的VBA宏

1. **生成宏文件**
```bash
cae-cli macro ./macros --type full
```

2. **在SolidWorks中导入宏**
   - 按 `Alt+F11` 打开VBA编辑器
   - 文件 -> 导入文件
   - 选择 `CAE_FullIntegration.bas`

3. **运行宏**
   - 宏会：
     1. 修改圆角参数
     2. 重建模型
     3. 导出STEP文件
     4. 调用CLI分析
     5. 弹窗显示报告路径

### 方法二：使用Python直接控制

```python
from sw_helper.integrations import CADManager

# 连接SolidWorks
manager = CADManager()
manager.auto_connect()
connector = manager.get_connector()

# 打开文件
connector.open_document("model.sldprt")

# 获取参数
params = connector.get_parameters()
for p in params:
    print(f"{p.name}: {p.value} {p.unit}")

# 修改参数
connector.set_parameter("Fillet_R", 10)
connector.rebuild()

# 导出
connector.export_file("output.step", "STEP")

# 关闭
manager.disconnect_all()
```

## 🔄 参数优化工作流程

### 圆角优化示例

```bash
cae-cli optimize model.sldprt \
  -p Fillet_R \
  -r 2 15 \
  --steps 5 \
  --plot \
  -o results.json
```

工作流程：
1. 连接SolidWorks
2. 设置圆角 R=2mm
3. 重建并导出
4. 分析质量分数
5. 重复R=5, 8, 11, 15mm
6. 生成优化报告和图表

### AI辅助优化示例

```bash
cae-cli optimize model.sldprt --ai
```

AI会：
1. 分析当前设计
2. 识别应力集中区域
3. 建议增大圆角半径
4. 自动执行优化
5. 推荐最佳方案

## 🎨 输出示例

### 参数优化结果

```
┏━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┓
┃ 迭代     ┃ 参数值   ┃ 质量分数 ┃ 耗时  ┃
┡━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━┩
│ 1        │ 2.00     │ 55.00    │ 2.34s │
│ 2        │ 5.25     │ 72.00    │ 2.18s │
│ 3        │ 8.50 ★   │ 85.00    │ 2.21s │
│ 4        │ 11.75    │ 80.00    │ 2.19s │
│ 5        │ 15.00    │ 75.00    │ 2.25s │
└──────────┴──────────┴──────────┴───────┘

✓ 最佳结果: 迭代 3, 质量分数 85.00
```

### AI生成的设计描述

```json
{
  "type": "cube_with_fillet",
  "parameters": {
    "length": {"value": 100, "unit": "mm", "modifiable": true},
    "fillet_radius": {"value": 5, "unit": "mm", "modifiable": true, "range": [1, 15]}
  },
  "material": "铝合金6061",
  "manufacturing_notes": [
    "建议CNC加工",
    "圆角处注意刀具半径补偿"
  ],
  "optimization_hints": [
    "圆角半径增大可降低应力集中"
  ]
}
```

## 📊 生成的宏代码示例

### CAE_FullIntegration.bas

```vba
Sub RunOptimization()
    ' 1. 修改圆角参数
    Call ModifyFilletRadius(10)
    
    ' 2. 重建模型
    Part.EditRebuild3
    
    ' 3. 导出STEP
    Part.SaveAs3 exportPath, 0, 2
    
    ' 4. 调用CLI分析
    shell.Run "cae-cli parse """ & exportPath & """ --verbose", 1, True
    
    ' 5. 显示报告
    MsgBox "分析完成!" & vbCrLf & "报告路径:" & vbCrLf & reportPath
End Sub
```

## 🛠️ 开发工具集成

### VS Code + SolidWorks

1. 安装 `SolidWorks API` 扩展
2. 配置Python解释器
3. 使用 `cae-cli cad` 命令测试连接

### Jupyter Notebook

```python
# 在Notebook中控制SolidWorks
from sw_helper.integrations import CADManager
import matplotlib.pyplot as plt

manager = CADManager()
manager.auto_connect()
connector = manager.get_connector()

# 参数扫描
radii = [2, 5, 8, 10, 15]
scores = []

for r in radii:
    connector.set_parameter("Fillet_R", r)
    connector.rebuild()
    # 分析并记录质量分数
    scores.append(analyze_quality())

plt.plot(radii, scores)
plt.xlabel('Fillet Radius (mm)')
plt.ylabel('Quality Score')
```

## 📚 完整命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| `cae-cli cad` | CAD集成控制 | `--connect solidworks --list-params` |
| `cae-cli optimize` | 参数优化 | `-p Fillet_R -r 2 15 --steps 5` |
| `cae-cli ai generate` | AI生成几何 | `"带圆角的立方体"` |
| `cae-cli ai suggest` | AI优化建议 | `--file model.step --target strength` |
| `cae-cli macro` | 生成VBA宏 | `./macros --type full` |
| `cae-cli parse` | 解析几何文件 | `model.step --output result.json` |
| `cae-cli analyze` | 网格质量分析 | `mesh.msh --metric aspect_ratio` |
| `cae-cli material` | 材料数据库 | `Q235 --property elastic_modulus` |
| `cae-cli report` | 生成报告 | `static -i result.inp -o report.html` |
| `cae-cli config` | 配置管理 | `--set default_material Q345` |
| `cae-cli info` | 系统信息 | - |
| `cae-cli version` | 版本信息 | `--check` |

## 🎉 总结

现在你拥有了一个完整的CAE工作流：

1. **SolidWorks** -> VBA宏一键导出
2. **CLI分析** -> 自动解析和评估
3. **参数优化** -> 自动调整设计参数
4. **AI辅助** -> 智能设计建议
5. **报告生成** -> 专业分析报告

完整实现了：✅ AI生成、✅ VBA宏集成、✅ pywin32连接、✅ 参数优化循环、✅ 彩色输出
