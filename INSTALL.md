# 安装指南

## 环境要求

- Python 3.8+
- Windows 10/11 / Linux / macOS

## 基础安装

```bash
# 克隆项目
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli

# 安装
pip install -e .
```

## 可选功能

### 完整功能（含几何处理）
```bash
pip install -e ".[full]"
```

### 开发依赖
```bash
pip install -e ".[dev]"
```

## AI功能安装

### 方式1: Ollama（在线AI模型）

1. 安装 [Ollama](https://ollama.com)
2. 下载模型：
```bash
ollama pull qwen2.5:3b
```

### 方式2: 本地GGUF模型（离线可用）

1. 安装 llama-cpp-python：
```bash
pip install llama-cpp-python
```

2. 下载 GGUF 模型文件（如 qwen2.5-1.5b），放入项目目录

### GPU加速（可选）

如果使用 NVIDIA 显卡，安装 GPU 版：
```bash
pip install llama-cpp-python --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

## 验证安装

```bash
cae-cli --help
cae-cli info
```

## 常见问题

### 导入错误
```bash
pip install -e .
```

### AI模型太慢
- 使用更小的模型（如 qwen2.5-0.5b）
- 使用 GPU 加速
- 使用本地 GGUF 模型

### 中文显示乱码
这是终端编码问题，不影响功能。可尝试：
```bash
chcp 65001
```
