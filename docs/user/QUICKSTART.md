# 快速开始

3 分钟内开始使用 CAE-CLI。

## 安装

```bash
pip install cae-cli
```

## 基础命令

```bash
# 查看帮助
cae-cli --help

# 查询材料
cae-cli material Q235

# 分析网格
cae-cli analyze mesh.msh

# 解析几何
cae-cli parse model.step

# 交互模式
cae-cli interactive --lang zh
```

## AI 学习助手

```bash
# 启动 AI 问答
cae-cli learn chat --mode learning

# 查看课程
cae-cli learn list
```

## 常见问题

### 安装失败
```bash
pip install --upgrade pip
pip install cae-cli
```

### 命令找不到
```bash
python -m sw_helper --help
```
