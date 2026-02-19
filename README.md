# cae-cli - 机械设计学习辅助 CLI 工具

一个专为机械专业学生设计的终端工具，支持 CAD→CAE 完整仿真工作流。

## 安装

```bash
# 从 PyPI 安装
pip install cae-cli

# 或从源码安装
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli
pip install -e .
```

## 快速开始

### 1. 静力分析 (stress_analysis)

```bash
python src/sw_helper/cli.py workflow stress_analysis -f model.FCStd -M Q235
```

### 2. 模态分析 (modal_analysis)

```bash
python src/sw_helper/cli.py workflow modal_analysis -f model.FCStd -M Q235
```

### 3. 拓扑优化 (topology_optimization)

```bash
python src/sw_helper/cli.py workflow topology_optimization -f model.FCStd -M Q235
```

### 查看可用工作流

```bash
python src/sw_helper/cli.py workflows
```

## 支持的求解器

| 类别 | 软件 | 状态 |
|------|------|------|
| CAD | FreeCAD | ✅ 已支持 |
| CAD | SolidWorks | 🔄 开发中 |
| CAE | CalculiX | ✅ 已支持 |
| CAE | Abaqus | 🔄 开发中 |
| 网格生成 | Gmsh | ✅ 已支持 |

## 后续计划

- [ ] PyPI 包发布
- [ ] 完整 Windows/Linux/macOS 支持
- [ ] 更多 CAD/CAE 软件集成
- [ ] GUI 界面开发
- [ ] 云端求解支持

## 文档

详细文档见 `docs/` 目录。

## 许可证

MIT License
