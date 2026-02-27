# 安装指南

## 系统要求

- Python >= 3.8
- Windows / Linux / macOS

## 安装方式

### 从 PyPI 安装

```bash
pip install cae-cli
```

### 从源码安装

```bash
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli
pip install -e .
```

### 安装完整功能

```bash
# 包含几何处理
pip install "cae-cli[full]"

# 包含 AI 功能
pip install "cae-cli[ai]"

# 开发依赖
pip install -e ".[dev]"
```

## GUI 桌面版本

```bash
# 安装 GUI 依赖
pip install PySide6 PySide6-WebEngine

# 运行 GUI
python -m main_gui
```

## Ollama 配置 (AI 学习助手)

```bash
# 1. 下载安装 Ollama
# https://ollama.com/

# 2. 下载模型
ollama pull qwen2.5:1.5b

# 3. 验证
curl http://localhost:11434/api/tags
```

## 验证安装

```bash
cae-cli --version
cae-cli info
```
