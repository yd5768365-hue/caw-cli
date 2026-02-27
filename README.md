# CAE-CLI 🛠️

**专为机械专业学生设计的智能 CAE 命令行工具**
开箱即用的网格分析、材料计算、参数优化 + 本地 AI 学习助手 🤖

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

---

## ✨ 核心特性

### 🤖 **本地 AI 学习助手**（离线可用！）
- **GGUF 离线模式**：无需 Ollama，下载模型文件即可使用
- **RAG 知识检索**：基于知识库的智能问答
- **教学式回答**：用中文一步步讲解，适合大一学生
- **多轮对话**：自动保存对话历史，支持深度问答

### 🧩 **插件化架构**
- **标准化接口**：统一的 CAD/CAE 抽象基类
- **工作流引擎**：配置驱动的完整仿真流程
- **多软件支持**：FreeCAD + CalculiX + Gmsh

### 🔍 **快速模型分析**
- 几何解析：STL/STEP/IGES 格式支持
- 网格质量评估：纵横比、偏斜度、正交质量
- 材料力学计算：应力、应变、安全系数
- 报告生成：HTML/PDF/JSON 多格式

### 🎮 **交互式学习**
- 中文/英文界面切换
- 菜单式操作，新手友好
- 实时质量分析反馈

---

## 🚀 快速开始

### 方式一：PyPI 安装（推荐）

```bash
pip install cae-cli

# 查看帮助
cae-cli --help

# 解析几何文件
cae-cli parse model.step

# 查询材料
cae-cli material Q235

# 网格分析
cae-cli analyze mesh.msh
```

### 方式二：GUI 桌面版（含离线 AI）

**下载预编译版本**：[Releases](https://github.com/yd5768365-hue/caw-cli/releases)

```
cae-gui/
├── cae-gui.exe              # GUI 可执行文件
├── qwen2.5-1.5b-instruct... # AI 模型 (需自行下载)
└── bge-m3-Q8_0.gguf        # 向量模型 (需自行下载)
```

**双击运行**：无需 Python 环境，开箱即用！

### AI 离线使用指南

1. 下载两个模型文件（约 1.5GB）：
   - `qwen2.5-1.5b-instruct-q4_k_m.gguf` (LLM)
   - `bge-m3-Q8_0.gguf` (嵌入)

2. 放入 exe 同目录

3. 启动程序，选择"学习模式"即可使用！

---

## 💡 典型应用场景

### 📐 工程师日常

```bash
# 快速检查网格质量
cae-cli analyze bracket.msh --metric aspect_ratio

# 材料参数查询
cae-cli material Q235 --property yield_strength

# 生成分析报告
cae-cli report static --input result.inp --output report.html
```

### 👨‍🎓 学习辅助

```bash
# 进入交互模式
cae-cli interactive --lang zh

# 学习模式中提问
"什么是 Von Mises 应力？"
"如何理解安全系数？"
```

### ⚙️ 参数优化

```bash
# 自动优化圆角半径
cae-cli optimize bracket.FCStd -p Fillet_Radius -r 2 15 --steps 5
```

### 🎨 AI 辅助设计

```bash
# AI 生成 3D 模型
cae-cli ai generate "带圆角的立方体，长100宽50高30圆角10"
```

---

## 📦 完整命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `parse` | 几何解析 | `cae-cli parse model.step` |
| `analyze` | 网格分析 | `cae-cli analyze mesh.msh` |
| `material` | 材料查询 | `cae-cli material Q235` |
| `report` | 报告生成 | `cae-cli report static -i result.inp` |
| `interactive` | 交互模式 | `cae-cli interactive --lang zh` |
| `learn` | AI学习助手 | `cae-cli learn --lang zh` |
| `optimize` | 参数优化 | `cae-cli optimize model.FCStd` |

**更多命令**：`cae-cli --help`

---

## 🛠️ 开发与贡献

```bash
# 克隆项目
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
```

---

## 📚 文档

- 📘 **快速开始**：[QUICKSTART.md](docs/QUICKSTART.md)
- 📖 **安装指南**：[INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md)
- ❓ **常见问题**：[FAQ.md](docs/FAQ.md)
- 📜 **API 参考**：[API_REFERENCE.md](docs/API_REFERENCE.md)
- 🤝 **贡献指南**：[CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## 🎯 项目特点总结

| 特性 | 说明 |
|------|------|
| 🤖 **本地 AI** | 无需联网，离线使用，打包即用 |
| 🧩 **插件化** | 标准化接口，自由扩展软件集成 |
| 🎮 **易用性** | 中文界面，菜单操作，新手友好 |
| 📚 **知识库** | 内置机械知识，支持 RAG 检索 |
| 📊 **多格式** | HTML/PDF/JSON，灵活输出 |
| 🌐 **多语言** | 中英文切换，国际化设计 |
| 📦 **可分发** | 打包版本无需 Python 环境 |

---

## 📮 联系与支持

- **项目主页**：https://github.com/yd5768365-hue/caw-cli
- **问题反馈**：https://github.com/yd5768365-hue/caw-cli/issues
- **版本发布**：https://github.com/yd5768365-hue/caw-cli/releases

---

## 📄 许可证

MIT License - 自由使用、修改、分发

---

**CAE-CLI - 让机械学习更简单 🚀**
