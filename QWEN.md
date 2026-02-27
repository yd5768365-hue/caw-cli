# CAE-CLI 项目文档

## 项目概述

CAE-CLI 是一个专业的机械设计学习辅助命令行工具，专为机械专业学生设计，集成了几何解析、网格分析、材料查询、参数优化、AI学习助手等多种功能。该项目支持 SolidWorks、FreeCAD 等 CAD 软件的集成，并提供完整的 CAE 分析工作流。

### 核心特性

- **几何文件解析**：支持 STL/STEP/IGES 等格式，提取体积、表面积、顶点数等几何信息
- **网格质量评估**：分析纵横比、偏斜度、正交质量等指标，提供质量评分
- **参数自动优化**：自动迭代修改参数，寻找最佳质量/强度方案
- **材料数据库**：内置 GB/T 标准材料库（Q235、Q345、铝合金等）
- **AI 辅助设计**：自然语言描述转 FreeCAD 建模
- **多语言界面**：支持中英文界面切换
- **插件化架构**：标准化 CAD/CAE 接口，支持自由扩展软件集成
- **AI 学习助手**：本地 Ollama + RAG 知识检索，提供智能问答
- **GUI 桌面版**：PySide6 Web 美化界面

## 项目结构

```
cae-cli/
├── src/
│   ├── sw_helper/           # 主包
│   │   ├── cli.py          # CLI入口
│   │   ├── geometry/       # 几何解析模块
│   │   ├── mesh/           # 网格分析模块
│   │   ├── material/       # 材料力学模块
│   │   ├── mechanics/      # 力学计算模块
│   │   ├── report/         # 报告生成模块
│   │   ├── optimization/   # 参数优化模块
│   │   ├── ai/            # AI辅助设计模块
│   │   ├── chat/          # 交互式聊天模块
│   │   ├── integrations/   # CAD软件集成模块
│   │   ├── mcp/           # MCP协议接口模块
│   │   └── utils/         # 工具模块
│   ├── integrations/       # 插件化架构
│   │   ├── _base/         # 抽象基类
│   │   ├── cad/           # CAD连接器
│   │   ├── cae/           # CAE连接器
│   │   └── mesher/        # 网格生成器
│   ├── gui/               # GUI界面模块
│   ├── core/              # 核心数据类型
│   ├── knowledge/         # 机械知识库
│   └── main_gui.py        # GUI主入口
├── knowledge/              # 机械知识库
├── data/                  # 数据文件
├── tests/                 # 测试
├── docs/                  # 文档
├── examples/              # 示例配置
├── pyproject.toml         # 项目配置
├── cae-gui.spec          # GUI打包配置
└── README.md             # 说明文档
```

## 安装与配置

### 系统要求

- **Python**：>= 3.8
- **操作系统**：Windows / Linux / macOS
- **可选**：SolidWorks、FreeCAD、ANSYS、Abaqus
- **AI功能**（可选）：
  - Ollama (https://ollama.com/) - 本地LLM运行环境
  - RAM: 最少4GB (推荐8GB+，用于运行AI模型)

### 安装方式

#### 方式一：从 PyPI 安装（推荐）

```bash
pip install cae-cli
```

#### 方式二：从源码安装

```bash
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli
pip install -e .
```

#### 方式三：安装完整功能版

```bash
# 包含几何处理和网格分析的所有功能
pip install "cae-cli[full]"
```

#### 方式四：安装AI学习助手完整版

```bash
# 包含所有功能 + AI学习助手依赖
pip install "cae-cli[ai]"

# 或同时安装所有扩展
pip install "cae-cli[full,ai]"
```

#### 方式五：GUI 桌面版本

```bash
# 安装 GUI 依赖
pip install PySide6 PySide6-WebEngine

# 打包 GUI 版本
pyinstaller cae-gui.spec
```

## 主要功能

### 1. 几何文件解析

```bash
# 解析STEP文件
cae-cli parse model.step

# 指定格式并保存结果
cae-cli parse part.stl --format stl --output result.json

# 表格形式显示
cae-cli parse assembly.step --format-output table
```

### 2. 材料数据库查询

```bash
# 列出所有材料
cae-cli material --list

# 查询特定材料
cae-cli material Q235

# 查询特定属性
cae-cli material Q235 --property elastic_modulus

# 搜索材料
cae-cli material --search "钢"
```

### 3. 网格质量分析

```bash
# 分析网格文件
cae-cli analyze mesh.msh

# 指定质量指标
cae-cli analyze mesh.inp --metric aspect_ratio --metric skewness

# 设置阈值并保存报告
cae-cli analyze mesh.msh --threshold 0.05 --output quality_report.json
```

### 4. 生成分析报告

```bash
# 生成静力分析报告（HTML格式）
cae-cli report static --input result.inp --output report.html

# 生成模态分析报告（JSON格式）
cae-cli report modal --input eigenvalues.txt --format json

# 指定报告标题
cae-cli report thermal --input thermal.rth --title "热分析报告"
```

### 5. 参数优化

```bash
# 优化圆角半径（2mm ~ 15mm, 5 steps）
cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 5

# 优化长度并生成绘图和报告
cae-cli optimize bracket.FCStd -p Length -r 100 200 -s 10 --plot --report

# 使用模拟模式（无需FreeCAD安装）
cae-cli optimize model.FCStd -p Thickness -r 5 20 --cad mock
```

### 6. AI 模型生成

```bash
# 生成带圆角的立方体
cae-cli ai generate "cube with fillet, length 100 width 50 height 30 fillet 10"

# 生成圆柱体并指定名称
cae-cli ai generate "cylinder, radius 30 height 60" -n my_cylinder -d ./output

# 使用模拟模式（无需FreeCAD）
cae-cli ai generate "cube, side length 50" --mock
```

### 7. 交互模式

```bash
# 启动中文界面交互模式（默认）
cae-cli interactive --lang zh

# 启动英文界面交互模式
cae-cli interactive --lang en
```

### 8. AI 学习助手

```bash
# 启动AI学习助手
cae-cli learn chat

# 列出所有课程
cae-cli learn list

# 进入特定课程
cae-cli learn mechanics
```

## 开发约定

### 代码风格

- 使用 Black 格式化代码（行长度100字符）
- 使用 Ruff 进行代码检查
- 使用 MyPy 进行类型检查

### 测试

- 使用 pytest 进行单元测试
- 所有功能必须有对应的测试用例
- 代码覆盖率应保持在80%以上

### 架构原则

- **插件化设计**：通过标准化接口支持多种CAD/CAE软件
- **模块化结构**：各功能模块独立，便于维护和扩展
- **向后兼容**：新版本应保持与旧版本的向后兼容性

## 构建与部署

### 构建 CLI 版本

```bash
# 使用 PyInstaller 打包
pyinstaller --name=cae-cli --console --add-data "src;src" --add-data "data;data" --add-data "knowledge;knowledge" --hidden-import=click --hidden-import=rich --hidden-import=yaml --hidden-import=numpy --hidden-import=jinja2 --hidden-import=pint --collect-all=rich --exclude-module=PyQt5 --exclude-module=PySide6 src/sw_helper/cli.py
```

### 构建 GUI 版本

```bash
# 打包 GUI 版本
pyinstaller cae-gui.spec
```

### 发布流程

1. 更新版本号（在 `pyproject.toml` 和 `cli.py` 中）
2. 运行完整测试套件
3. 生成文档
4. 创建发布标签
5. 构建发行版本
6. 上传到 PyPI

## 依赖管理

项目依赖定义在 `pyproject.toml` 中：

- **核心依赖**：click, rich, numpy, pyyaml, jinja2, pint
- **AI 功能**：chromadb, sentence-transformers
- **完整功能**：pythonocc-core, meshio, vtk, matplotlib, pandas
- **GUI 依赖**：PySide6, PySide6-Addons, PySide6-WebEngine
- **开发依赖**：pytest, black, ruff, mypy, pre-commit, pyinstaller

## 故障排除

### 常见问题

1. **依赖安装失败**：
   ```bash
   pip install --upgrade pip
   pip install cae-cli
   ```

2. **FreeCAD 集成问题**：
   - 确保 FreeCAD 已正确安装
   - 检查 FreeCAD Python API 是否可用

3. **Ollama 连接问题**：
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. **GUI 启动失败**：
   - 确保 PySide6 和 QtWebEngine 已安装
   - 检查 Visual C++ 运行时是否安装

### 性能优化

- 使用缓存减少重复计算
- 优化数据库查询
- 实现异步处理提高响应速度
- 使用内存映射处理大文件

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发环境设置

```bash
git clone https://github.com/yd5768365-hue/caw-cli.git
cd cae-cli
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_geometry.py
```

## 许可证

本项目采用 MIT 许可证。

## 联系方式

- **项目主页**：https://github.com/yd5768365-hue/caw-cli
- **问题报告**：https://github.com/yd5768365-hue/caw-cli/issues