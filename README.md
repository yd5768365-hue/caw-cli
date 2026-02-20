# CAE-CLI 机械设计学习助手

一个为机械专业学生设计的命令行工具，支持几何解析、材料计算、网格分析、AI问答等功能。

## 快速开始

```bash
# 安装
pip install -e .

# 运行
cae-cli --help

# 交互模式
cae-cli interactive
```

## 功能

| 功能 | 命令 |
|------|------|
| 材料查询 | `cae-cli material Q235` |
| 几何解析 | `cae-cli parse model.step` |
| 网格分析 | `cae-cli analyze mesh.msh` |
| AI学习助手 | `cae-cli interactive` |
| 手册查询 | `cae-cli handbook search <关键词>` |

## AI模式

启动交互模式后可选：
1. **Ollama服务** - 需要安装Ollama并下载模型
2. **本地GGUF模型** - 离线可用，加载本地.gguf模型文件
3. **本地知识库** - 仅使用RAG知识检索

## 要求

- Python 3.8+
- Windows/Linux/macOS
- 可选: Ollama (用于在线AI模型)
- 可选: llama-cpp-python (用于本地GGUF模型)

## 文档

- [快速开始](docs/QUICKSTART.md)
- [安装指南](docs/INSTALLATION_GUIDE.md)
- [常见问题](docs/FAQ.md)

---
⭐ Star us on [GitHub](https://github.com/yd5768365-hue/caw-cli)
