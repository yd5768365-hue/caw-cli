# 使用说明

## 基础命令

```bash
# 查看帮助
cae-cli --help

# 查看版本
cae-cli version

# 系统信息
cae-cli info
```

## 材料查询

```bash
# 查询材料
cae-cli material Q235

# 列出所有材料
cae-cli material list
```

## 几何解析

```bash
# 解析STEP文件
cae-cli parse model.step

# 解析IGES文件
cae-cli parse model.iges
```

## 网格分析

```bash
# 分析网格
cae-cli analyze mesh.msh

# 查看帮助
cae-cli analyze --help
```

## AI学习助手

```bash
# 启动交互模式
cae-cli interactive

# AI模式选择：
# 1. Ollama服务（需要安装Ollama）
# 2. 本地GGUF模型（离线可用）
# 3. 仅知识库
```

### 交互模式命令

- 输入问题开始对话
- 输入 `back` 或 `退出` 返回主菜单

## 手册查询

```bash
# 搜索手册
cae-cli handbook search "螺栓"
cae-cli handbook search "应力"

# 查看手册列表
cae-cli handbook list
```

## 报告生成

```bash
# 生成报告
cae-cli report input.msh output.html
```

## 配置

配置文件位置: `~/.cae-cli/config.yaml`

```yaml
language: zh  # 语言: zh/en
model: qwen2.5:3b  # 默认AI模型
```

## 注意事项

1. 首次使用AI功能需要选择AI模式
2. 本地GGUF模型需要下载模型文件放入项目目录
3. 部分功能需要安装额外依赖
