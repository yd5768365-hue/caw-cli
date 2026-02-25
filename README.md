# CAE-CLI 机械设计辅助工具

专业 CAE 命令行工具，帮助机械专业学生进行几何解析、网格分析、材料查询、力学计算和 AI 辅助学习。

## 核心功能

| 功能 | 命令 | 说明 |
|------|------|------|
| 📐 几何解析 | `cae-cli parse model.step` | 支持 STEP/STL/IGES 格式 |
| 🔍 网格分析 | `cae-cli analyze mesh.msh` | 质量评估、纵横比、偏斜度 |
| 🔧 材料查询 | `cae-cli material Q235` | GB/T 标准材料库 |
| 📊 力学计算 | 内置模块 | 应力、安全系数、屈曲 |
| 🤖 AI 学习助手 | `cae-cli learn chat` | 本地 Ollama + RAG 知识检索 |
| 🖥️ GUI 界面 | `python -m main_gui` | PySide6 图形界面 |

## 快速开始

```bash
# 安装
pip install cae-cli

# 查看帮助
cae-cli --help

# 查询材料
cae-cli material Q235

# 分析网格
cae-cli analyze mesh.msh

# 启动 AI 学习助手
cae-cli learn chat --mode learning
```

## 安装选项

```bash
# 基础版
pip install cae-cli

# 完整功能 (几何处理)
pip install "cae-cli[full]"

# AI 学习功能
pip install "cae-cli[ai]"

# 开发版
pip install -e ".[dev]"
```

## AI 学习助手

支持本地 Ollama 模型 + RAG 向量知识库：

```bash
# 启动学习模式
cae-cli learn chat

# 选择模式: learning / lifestyle / mechanical / default
cae-cli learn chat --mode mechanical
```

推荐模型: `qwen2.5:1.5b` (低资源) 或 `phi3:mini`

## 项目结构

```
cae-cli/
├── src/
│   ├── sw_helper/        # CLI 核心
│   ├── integrations/     # 插件化架构
│   ├── core/           # 数据类型
│   └── gui/            # GUI 界面
├── knowledge/           # Markdown 知识库
├── tests/               # 单元测试 (92 tests)
└── .github/workflows/ # CI/CD
```

## 测试

```bash
# 运行所有测试
pytest

# 代码审查
cae-cli review --local
```

## 技术栈

- Python 3.8+
- Click / Rich (CLI)
- PySide6 (GUI)
- ChromaDB + sentence-transformers (RAG)
- Ollama (本地 AI)

## 许可证

MIT

---
更多文档: [CLAUDE.md](./CLAUDE.md)
