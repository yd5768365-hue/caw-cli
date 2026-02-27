# CAE-CLI 打包指南

## 📦 打包完成状态

✅ **打包日期**: 2026-02-27
✅ **打包工具**: PyInstaller
✅ **目标平台**: Windows 10/11 x64

## 🎯 打包输出

### 1. GUI 桌面版 (cae-gui)

**文件位置**: `dist/cae-gui/cae-gui.exe`

**大小**:
- 可执行文件: 82 MB
- 依赖库 (_internal): 1.2 GB
- 总大小: ~1.3 GB

**特点**:
- 完整图形界面 (PySide6)
- 支持 AI 学习助手 (需外部模型文件)
- 包含所有功能模块
- 适合普通用户使用

**运行方式**:
```bash
# 双击运行
dist/cae-gui/cae-gui.exe

# 或命令行运行
cd dist/cae-gui && cae-gui.exe
```

### 2. CLI 命令行版 (cae-cli)

**文件位置**: `dist/cae-cli/cae-cli.exe`

**大小**:
- 可执行文件: 82 MB
- 依赖库 (_internal): 651 MB
- 总大小: ~750 MB

**特点**:
- 无图形界面
- 更小更快
- 适合命令行爱好者和自动化脚本
- 包含所有核心功能

**运行方式**:
```bash
# 查看帮助
dist/cae-cli/cae-cli.exe --help

# 解析几何文件
dist/cae-cli/cae-cli.exe parse model.step

# 分析网格质量
dist/cae-cli/cae-cli.exe analyze mesh.msh

# 查询材料
dist/cae-cli/cae-cli.exe material Q235

# 启动交互式聊天
dist/cae-cli/cae-cli.exe interactive --lang zh
```

## 📂 打包目录结构

```
dist/
├── cae-gui/                    # GUI 桌面版
│   ├── cae-gui.exe            # 可执行文件 (82 MB)
│   └── _internal/             # 依赖库 (1.2 GB)
│       ├── data/              # 数据文件
│       │   ├── materials.json
│       │   ├── languages.json
│       │   └── config.yaml
│       ├── knowledge/         # 知识库
│       │   ├── materials/
│       │   ├── bolts/
│       │   └── tolerances/
│       ├── examples/          # 示例文件
│       ├── gui/               # GUI 资源
│       │   ├── cae_ui.html
│       │   └── terminal_ui.html
│       ├── torch/             # PyTorch 库
│       ├── PySide6/           # PySide6 库
│       ├── numpy/
│       ├── pandas/
│       ├── sklearn/
│       ├── llama_cpp/         # GGUF 模型加载器
│       └── ...
│
└── cae-cli/                   # CLI 命令行版
    ├── cae-cli.exe            # 可执行文件 (82 MB)
    └── _internal/             # 依赖库 (651 MB)
        ├── data/              # 数据文件
        ├── knowledge/         # 知识库
        ├── examples/          # 示例文件
        ├── numpy/
        ├── pandas/
        ├── sklearn/
        └── ...
```

## 🚀 使用说明

### 基础使用

**CLI 版常用命令**:
```bash
# 版本信息
cae-cli.exe --version

# 几何解析
cae-cli.exe parse model.step --output info.json

# 网格分析
cae-cli.exe analyze mesh.msh --metric aspect_ratio --metric skewness

# 材料查询
cae-cli.exe material Q235
cae-cli.exe material --search aluminum

# 力学计算
cae-cli.exe stress --force 1000 --area 50 --material Q235

# 报告生成
cae-cli.exe report static --input result.inp --output report.html

# 参数优化
cae-cli.exe optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 5

# AI 模型生成
cae-cli.exe ai generate "带圆角的立方体，长100宽50高30圆角10"

# 交互式聊天
cae-cli.exe interactive --lang zh
```

**GUI 版使用**:
1. 双击 `cae-gui.exe` 启动
2. 选择功能模块:
   - 几何解析
   - 网格分析
   - 材料查询
   - 力学计算
   - 报告生成
   - 参数优化
   - 交互式聊天 (工作模式/学习模式)

## 📦 分发说明

### 外部模型文件支持

本项目支持离线 AI 模型，但为了减小打包体积，模型文件需要单独下载。

**模型文件列表**:
1. `qwen2.5-1.5b-instruct-q4_k_m.gguf` (~1 GB)
   - LLM 对话模型
   - 下载地址: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF

2. `bge-m3-Q8_0.gguf` (~500 MB)
   - 嵌入向量模型
   - 下载地址: https://huggingface.co/BAAI/bge-m3-gguf

**放置位置**:
- 将模型文件放在 `cae-gui.exe` 或 `cae-cli.exe` 同一目录
- 程序会自动检测并加载模型

**推荐分发方案**:

1. **基础包** (必需)
   - `dist/cae-gui/` 或 `dist/cae-cli/` 整个目录
   - 包含所有依赖库和资源文件
   - 用户可直接运行

2. **完整包** (可选)
   - 基础包 + 预下载的模型文件
   - 适合离线环境使用
   - 总大小: ~2.8 GB (GUI 版) / ~2.3 GB (CLI 版)

### 安装说明

**用户无需安装**:
- ✅ 无需 Python 环境
- ✅ 无需安装依赖包
- ✅ 开箱即用

**系统要求**:
- ✅ Windows 10/11 x64
- ✅ 4 GB 内存 (推荐 8 GB+)
- ✅ 硬盘空间: 2 GB (基础包) / 3 GB (完整包)
- ✅ 显卡: 无需独立显卡 (集成显卡即可)

## 🔧 打包命令

### 打包 GUI 版

```bash
# 清理旧文件
rm -rf build/cae-gui dist/cae-gui

# 使用 spec 文件打包
pyinstaller cae-gui.spec -y
```

### 打包 CLI 版

```bash
# 清理旧文件
rm -rf build/cae-cli dist/cae-cli

# 命令行方式打包
pyinstaller --name=cae-cli \
    --console \
    --add-data "src;src" \
    --add-data "data;data" \
    --add-data "knowledge;knowledge" \
    --add-data "examples;examples" \
    --hidden-import=click \
    --hidden-import=rich \
    --hidden-import=yaml \
    --hidden-import=numpy \
    --hidden-import=jinja2 \
    --hidden-import=pint \
    --hidden-import=sw_helper \
    --hidden-import=sw_helper.cli \
    --hidden-import=sw_helper.geometry \
    --hidden-import=sw_helper.material \
    --hidden-import=sw_helper.mechanics \
    --hidden-import=sw_helper.ai \
    --hidden-import=sw_helper.learning \
    --hidden-import=sw_helper.mcp \
    --hidden-import=sw_helper.utils \
    --hidden-import=sw_helper.knowledge \
    --hidden-import=integrations \
    --hidden-import=core \
    --hidden-import=sklearn \
    --collect-all=rich \
    --exclude-module=PyQt5 \
    --exclude-module=PySide6 \
    src/sw_helper/cli.py \
    -y
```

### 自定义打包

**修改 spec 文件**:
```python
# cae-gui.spec
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="cae-gui",
    debug=False,
    console=False,  # 不显示控制台
    icon="icon.ico",  # 可添加图标
    ...
)
```

**添加图标**:
```bash
# GUI 版
pyinstaller --icon=icon.ico cae-gui.spec

# CLI 版
pyinstaller --icon=icon.ico --name=cae-cli ...
```

## ⚠️ 注意事项

1. **首次运行**:
   - 首次运行可能需要 3-5 秒加载依赖
   - 后续运行速度会快很多

2. **模型文件**:
   - 模型文件较大，建议单独下载
   - 程序会自动检测模型文件是否存在
   - 无模型文件时，AI 功能将降级使用在线 API

3. **更新打包**:
   - 修改代码后需要重新打包
   - 建议先清理 `build/` 和 `dist/` 目录
   - 使用 `-y` 参数自动覆盖旧文件

4. **常见问题**:
   - 如果遇到 DLL 缺失，检查 `_internal` 目录是否完整
   - 如果程序闪退，查看同目录下的日志文件
   - 确保有足够的磁盘空间 (至少 3 GB)

## 📊 性能优化建议

1. **减小打包体积**:
   - 移除不必要的依赖 (如测试框架)
   - 使用 `--exclude-module` 排除不需要的模块
   - 考虑使用 UPX 压缩 (已启用)

2. **加快启动速度**:
   - 减少隐藏导入数量
   - 延迟加载大型模块
   - 使用多线程预加载

3. **优化资源**:
   - 压缩图片和图标
   - 使用更小的字体文件
   - 移除调试符号

## 📝 打包日志

- **GUI 版警告**: `build/cae-gui/warn-cae-gui.txt`
- **CLI 版警告**: `build/cae-cli/warn-cae-cli.txt`
- **交叉引用**: `build/cae-gui/xref-cae-gui.html`
- **依赖图谱**: `build/cae-cli/xref-cae-cli.html`

## 🔗 相关资源

- [PyInstaller 文档](https://pyinstaller.org/)
- [项目 README](../README.md)
- [开发指南](../docs/PROJECT_INTRO.md)
