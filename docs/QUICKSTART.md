# CAE-CLI 快速开始指南 🚀

CAE-CLI 是一款专为机械专业学生设计的 CAE 分析工具。本指南将帮助您在 **5 分钟** 内快速上手。

## 🎯 3步安装流程

### 第1步：安装 Python（如未安装）
确保您的系统已安装 Python 3.8 或更高版本。访问 [Python官网](https://www.python.org/downloads/) 下载安装程序，安装时**务必勾选 "Add Python to PATH"**。

### 第2步：安装 CAE-CLI
```bash
# 推荐：完整功能安装（包含几何处理、网格分析、AI辅助等所有功能）
pip install "cae-cli[full]"

# 或：基础安装（不含几何处理功能）
pip install cae-cli
```

### 第3步：验证安装
```bash
cae-cli --version
```
**预期输出：**
```
cae-cli 0.2.0
```

✅ **恭喜！安装完成！**

---

## 🚀 5个基础命令示例

### 示例1：解析几何文件（STEP/STL格式）
```bash
cae-cli parse model.step
```
**预期输出（截图示意）：**
```
📐 几何文件解析结果
─────────────────
文件名: model.step
体积: 250000 mm³
表面积: 15000 mm²
顶点数: 12
边数: 18
面数: 6
格式: STEP (AP242)
解析时间: 0.5s
```

### 示例2：查询材料属性
```bash
cae-cli material Q235 --property elastic_modulus
```
**预期输出：**
```
🔧 材料属性查询
──────────────
材料: Q235 (碳素结构钢)
属性: elastic_modulus (弹性模量)
值: 210000000000 Pa
单位: Pa
标准: GB/T 700-2006
建议安全系数: 1.5
```

### 示例3：分析网格质量
```bash
cae-cli analyze mesh.msh
```
**预期输出：**
```
📊 网格质量分析报告
─────────────────
网格文件: mesh.msh
元素数量: 10000
节点数量: 12000
平均质量: 0.85
质量分布:
  ✅ 优秀 (0.8-1.0): 80%
  ⚠️ 良好 (0.6-0.8): 15%
  ⚠️ 一般 (0.4-0.6): 5%
  ❌ 较差 (<0.4): 0%
总体评价: ✅ 优秀
```

### 示例4：计算力学性能
```bash
cae-cli mechanics stress --force 10000 --area 0.001 --material Q235
```
**预期输出：**
```
⚙️ 应力计算结果
─────────────
名义应力: 10000000 Pa (10 MPa)
许用应力: 235000000 Pa (235 MPa)
安全系数: 23.5
状态: ✅ 安全 (安全系数 > 1.5)
颜色预警: 🟢 绿色
建议: 设计保守，可优化减重
```

### 示例5：优化设计参数
```bash
cae-cli optimize bracket.FCStd -p Fillet_Radius -r 2 15 --steps 5
```
**预期输出：**
```
🔄 参数优化结果
─────────────
优化参数: Fillet_Radius (圆角半径)
搜索范围: 2.0 - 15.0 mm
最优值: 8.5 mm
质量分数: 95.3/100
最大应力: 180 MPa
迭代次数: 5
优化时间: 45.2s
节省材料: ≈12%
```

## 2. 5个基础命令示例 🎯

### 命令1：解析几何文件

```bash
# 解析STEP文件并显示信息
cae-cli parse model.step
```

**预期输出：**
```
文件名: model.step
体积: 250000 mm³
表面积: 15000 mm²
顶点数: 12
边数: 18
面数: 6
```

### 命令2：查询材料属性

```bash
# 查询Q235钢的属性
cae-cli material Q235 --property elastic_modulus
```

**预期输出：**
```
材料: Q235
属性: elastic_modulus
值: 210000000000 Pa
单位: Pa
```

### 命令3：分析网格质量

```bash
# 分析网格质量（支持 .msh, .inp, .bdf 格式）
cae-cli analyze mesh.msh
```

**预期输出：**
```
网格质量分析结果
==================
- 元素数量: 10000
- 平均质量: 0.85
- 质量分布: [0.8-1.0]: 80%, [0.6-0.8]: 15%, [0.4-0.6]: 5%, <0.4: 0%
- 总体质量: 优秀
```

### 命令4：计算力学性能

```bash
# 计算矩形截面的应力
cae-cli mechanics stress --force 10000 --area 0.001 --material Q235
```

**预期输出：**
```
应力计算结果
============
- 名义应力: 10000000 Pa (10 MPa)
- 许用应力: 235000000 Pa (235 MPa)
- 安全系数: 23.5
- 状态: 安全
```

### 命令5：优化参数

```bash
# 优化圆角半径（自动调整参数）
cae-cli optimize test_model.FCStd -p Fillet_Radius -r 2 15 --steps 5
```

**预期输出：**
```
参数优化结果
============
- 最优圆角半径: 8.5 mm
- 质量分数: 95.3/100
- 最大应力: 180 MPa
- 迭代次数: 5
```

## 🛠️ 故障排除快速链接

### 常见问题快速修复

| 问题 | 解决方案 | 详细说明 |
|------|----------|----------|
| **`ModuleNotFoundError: No module named 'sw_helper'`** | `pip install -e .` | 重新安装项目依赖 |
| **`UnicodeEncodeError: 'gbk' codec can't encode`** | `set PYTHONIOENCODING=utf-8` 或 `chcp 65001` | Windows 编码问题修复 |
| **`cae-cli: command not found`** | 检查 Python Scripts 目录是否在 PATH 中 | 添加 `%APPDATA%\Python\Python3*\Scripts` 到 PATH |
| **`FreeCAD not found`** | 设置 `FREECAD_PATH` 环境变量 | 指向 FreeCAD 安装目录 |
| **`CalculiX not found`** | 设置 `CCX_PATH` 环境变量 | 指向 CalculiX 可执行文件 |

### ⚡ 快速诊断命令
```bash
# 检查系统状态和依赖
cae-cli info

# 查看详细的安装问题诊断
cae-cli config --diagnose
```

### 📚 更多帮助资源

- 📖 [详细安装指南](INSTALLATION_GUIDE.md) - FreeCAD/CalculiX 详细安装步骤
- ❓ [常见问题解答](FAQ.md) - 10个最常见问题及解决方案
- 🔧 [API参考文档](API_REFERENCE.md) - 完整的Python API文档
- 🐛 [GitHub Issues](https://github.com/yd5768365-hue/caw-cli/issues) - 报告问题或建议
- 💬 [QQ技术交流群] - 实时技术交流（见项目主页）

---

## 🎯 下一步学习路径

### 阶段1：基础掌握（1-2小时）
1. **熟悉所有命令**：`cae-cli --help` 查看命令列表
2. **尝试交互模式**：`cae-cli interactive --lang zh` 中文菜单操作
3. **解析示例文件**：使用项目自带的示例文件练习

### 阶段2：中级应用（3-5小时）
1. **学习插件化架构**：阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解标准化接口
2. **运行完整工作流**：`python demo_workflow.py` 体验CAD→CAE完整流程
3. **创建配置文件**：参考 `examples/project.yaml` 创建自己的分析配置

### 阶段3：高级扩展（5+小时）
1. **集成新软件**：基于抽象基类添加新的CAD/CAE软件支持
2. **自定义材料库**：编辑 `data/materials.json` 添加自定义材料
3. **贡献代码**：阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 参与项目开发

---

## 📞 获取帮助

### 官方支持渠道
- **GitHub Issues**：https://github.com/yd5768365-hue/caw-cli/issues
- **文档网站**：https://caw-cli.readthedocs.io（规划中）
- **邮件支持**：your@email.com

### 紧急问题
1. 运行 `cae-cli info` 收集系统信息
2. 截图错误信息
3. 在 GitHub Issues 中提供复现步骤和系统信息

---

## 🎉 开始您的 CAE 学习之旅！

现在您已经掌握了 CAE-CLI 的基础用法，可以：

1. **分析您的第一个模型**：`cae-cli parse your_model.step`
2. **优化设计参数**：`cae-cli optimize your_model.FCStd -p Parameter_Name -r min max`
3. **生成专业报告**：`cae-cli report static --input result.inp --output report.html`

**💡 小贴士**：使用 `--verbose` 选项查看详细执行过程，便于学习和调试。

祝您学习愉快，早日成为 CAE 专家！ 🎓🚀