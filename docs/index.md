# 使用文档

## 目录

1. [快速开始](quickstart.md)
2. [CLI命令参考](cli-reference.md)
3. [Python API](api-reference.md)
4. [软件集成指南](integration-guide.md)
5. [材料数据库](material-database.md)
6. [示例教程](tutorials/)

## 快速开始

### 安装

```bash
pip install sw-cae-helper
```

### 第一个命令

```bash
# 解析STEP文件
cae-cli parse example.step

# 查看解析结果
{
  "file": "example.step",
  "format": ".step",
  "vertices": 1205,
  "faces": 2401,
  "volume": 0.00125,
  "bounds": {
    "x": [0.0, 100.0],
    "y": [0.0, 50.0],
    "z": [0.0, 25.0]
  }
}
```

## 支持的文件格式

### 几何文件
- STEP (.step, .stp)
- IGES (.iges, .igs)
- STL (.stl)

### 网格文件
- ANSYS (.msh, .inp)
- Abaqus (.inp)
- NASTRAN (.bdf, .dat)

## 配置

配置文件位于 `~/.sw-helper/config.yaml`，可以自定义：

- 默认材料
- 质量阈值
- 软件路径
- 报告模板

## 获取帮助

```bash
# 查看所有命令
cae-cli --help

# 查看具体命令帮助
cae-cli parse --help
```
