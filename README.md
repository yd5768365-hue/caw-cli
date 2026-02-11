cae-cli - 机械设计学习辅助 CLI 工具 🛠️
🎯 项目目的与背景
🤔 为什么创建这个工具？
CAE-CLI 是为机械专业学生（特别是从互联网专业转向机械领域的学习者）设计的专业命令行工具。作为一个大一学生，我在学习机械设计时遇到了几个痛点：

🔒 缺少商业软件许可证：无法使用 SolidWorks，需要替代方案
📈 学习曲线陡峭：机械设计、有限元分析、材料力学概念复杂
🧩 缺乏系统学习工具：需要一个整合的工具来辅助学习全过程
🔌 软件集成困难：不同CAD/CAE软件接口不统一，难以建立标准化工作流
🎓 用户背景
身份：大一学生，从互联网专业转向机械专业
软件：正在学习 FreeCAD（开源替代 SolidWorks）
目标：系统学习机械设计、有限元分析、材料力学等专业知识
📚 核心学习目标
目标	具体内容	实现状态
✅ 网格质量分析	快速评估模型网格质量，理解网格参数对分析结果的影响	✅ 已实现
✅ 材料力学计算	查询材料性能参数，计算应力、应变、安全系数等	✅ 已实现
✅ 参数优化	自动优化设计参数，寻找最佳设计方案	✅ 已实现
✅ 知识库管理	建立个人机械设计知识库，随时查询	✅ 已实现
✅ 报告生成	自动生成分析报告，整理学习笔记	✅ 已实现
🌟 多语言支持	交互界面支持中文/英文切换，适应不同语言习惯	✅ 新功能
🚀 插件化架构	标准化CAD/CAE软件接口，支持自由扩展软件集成	✅ 新增功能
🤖 AI学习助手	集成本地Ollama模型 + RAG知识检索，提供智能问答	✅ 最新功能
一个专为机械专业学生设计的终端工具，帮助快速分析 SolidWorks/FreeCAD 模型的网格质量、材料力学性能、参数优化，并集成 AI 建议和个人机械手册知识库。新增插件化架构，支持标准化CAD/CAE软件集成。



🆚 版本演进与功能对比
📊 当前版本 (v0.2.0+) 新增功能
功能模块	新增内容	说明
📚 完整文档体系	5个专业文档	新增QUICKSTART.md快速开始、INSTALLATION_GUIDE.md安装指南、FAQ.md常见问题、API_REFERENCE.md API参考、CONTRIBUTING.md贡献指南
🔧 API文档生成	自动生成脚本	支持一键生成HTML/Markdown格式的完整API参考文档
🧩 网格生成器集成	Gmsh连接器	新增src/integrations/mesher/gmsh.py，支持Gmsh网格生成器标准化集成
⚙️ 工具模块增强	4个新工具模块	新增依赖检查器(dependency_checker.py)、编码辅助(encoding_helper.py)、错误处理(error_handler.py)、Unicode回退数据
🧪 测试与示例	完整测试套件	新增工作流集成测试、工具测试、示例配置文件(optimization_demo.yaml)
📝 开发脚本	多平台测试脚本	新增run_tests.py/.sh/.bat，支持Windows/Linux/macOS测试运行
🔄 核心架构演进
版本阶段	核心特性	状态
v0.1.x	基础CAE功能	✅ 已稳定
v0.2.0	插件化架构重构	✅ 已发布
v0.2.0+	完整文档与工具链	✅ 本次更新
🎯 关键里程碑达成
✅ 插件化架构完成 - 标准化CAD/CAE接口，支持FreeCAD+CalculiX集成
✅ 力学计算模块完善 - 完整的应力、应变、安全系数计算体系
✅ 多语言支持 - 中英文界面切换，国际化设计
✅ 完整文档体系 - 从安装到开发的全方位文档支持
🔄 工作流CLI集成 - 进行中，即将发布
💡 项目状态：CAE-CLI已从基础工具发展为完整的机械学习辅助平台，具备插件化扩展能力、完整文档体系和专业测试套件。

🚀 核心功能
🎯 模型分析与优化
📐 几何文件解析：支持 STL/STEP/IGES 格式，提取体积、表面积、顶点数等几何信息
🔍 网格质量评估：分析纵横比、偏斜度、正交质量等指标，提供质量评分（优秀/良好/一般/较差）
⚙️ 参数自动优化：自动迭代修改参数（圆角半径、壁厚等），寻找最佳质量/强度方案
📊 力学性能计算：计算许用应力、安全系数、屈曲载荷等
🤖 AI 辅助设计
🎨 AI模型生成：自然语言描述 → FreeCAD 建模（"带圆角的立方体，长100宽50高30圆角10"）
💡 智能建议：基于分析结果提供专业中文建议
🤖 自动建模：规划中的自动建模功能
🎮 交互式学习体验
🖥️ 交互模式：菜单式操作，新手友好
🌐 多语言界面：🔴 新功能 支持中英文界面切换（--lang zh/en）
⚡ 实时反馈：操作过程中提供即时质量分析建议
📝 命令学习：支持直接命令行输入和菜单操作两种模式
🤖 AI学习助手 (🔥 最新功能)
🤖 本地AI模型：集成Ollama本地模型（支持qwen2.5:1.5b/phi3:mini）
🔍 RAG知识检索：使用sentence-transformers + ChromaDB向量化知识库，智能检索相关知识
👨‍🏫 教学式回答：专业机械学习助手，用中文教学式、一步步回答，适合大一学生
💬 多轮对话：自动保存对话历史，支持上下文连贯的深度问答
⚡ 自动服务启动：进入学习模式自动检测并启动Ollama服务
📚 知识库增强：每次提问前先检索knowledge/目录的Markdown知识库，结合知识库内容回答
🔧 智能模型检测：自动检测可用模型，优先使用qwen2.5:1.5b，回退到phi3:mini
📚 机械知识库管理
🧱 材料数据库：内置 GB/T 标准材料库（Q235、Q345、铝合金等）
📖 手册查询：本地 Markdown 知识库，查询材料参数、螺栓规格、公差、疲劳强度
📏 单位转换：支持 SI/MPa 单位系统自动转换
📊 报告与输出
📄 多格式报告：支持 HTML/PDF/JSON/Markdown 格式
📈 可视化图表：质量分曲线、应力分布图等
🔬 分析类型：静力、模态、热、屈曲分析报告
🧩 插件化架构 (🔥 全新功能)
🔌 标准化接口：统一的CAD/CAE抽象基类，支持自由扩展软件集成
⚙️ 工作流引擎：标准化的CAD→CAE分析流程管理，支持预定义和自定义工作流
⚡ 配置驱动：YAML配置文件定义完整仿真流程，支持复杂参数设置
🛠️ 多软件支持：已实现FreeCAD、CalculiX集成，可扩展支持更多软件
📦 安装
方式一：从 PyPI 安装（推荐）
bash
复制
pip install cae-cli
方式二：从源码安装
bash
复制
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli
pip install -e .

# 或运行安装脚本
python install.py
方式三：安装完整功能版
bash
复制
# 包含几何处理和网格分析的所有功能
pip install "cae-cli[full]"
系统要求
Python >= 3.8
Windows / Linux / macOS
可选：SolidWorks、FreeCAD、ANSYS、Abaqus
🚀 快速开始
查看帮助
bash
复制
cae-cli --help
1. 📐 几何文件解析
bash
复制
# 解析STEP文件
cae-cli parse model.step

# 指定格式并保存结果
cae-cli parse part.stl --format stl --output result.json

# 表格形式显示
cae-cli parse assembly.step --format-output table
2. 🧱 材料数据库查询
bash
复制
# 列出所有材料
cae-cli material --list

# 查询特定材料
cae-cli material Q235

# 查询特定属性
cae-cli material Q235 --property elastic_modulus

# 搜索材料
cae-cli material --search "钢"
3. 🔍 网格质量分析
bash
复制
# 分析网格文件
cae-cli analyze mesh.msh

# 指定质量指标
cae-cli analyze mesh.inp --metric aspect_ratio --metric skewness

# 设置阈值并保存报告
cae-cli analyze mesh.msh --threshold 0.05 --output quality_report.json
4. 📊 生成分析报告
bash
复制
# 生成静力分析报告（HTML格式）
cae-cli report static --input result.inp --output report.html

# 生成模态分析报告（JSON格式）
cae-cli report modal --input eigenvalues.txt --format json

# 指定报告标题
cae-cli report thermal --input thermal.rth --title "热分析报告"
5. ⚙️ 配置管理
bash
复制
# 查看配置
cae-cli config --list

# 设置配置项
cae-cli config --set default_material Q345
cae-cli config --set safety_factor 2.0

# 获取配置项
cae-cli config --get default_material

# 重置配置
cae-cli config --reset
6. 💻 系统信息
bash
复制
# 查看系统信息和状态
cae-cli info

# 查看版本
cae-cli version
cae-cli version --check
7. 🎮 交互模式（多语言支持）
bash
复制
# 启动中文界面交互模式（默认）
cae-cli interactive --lang zh

# 启动英文界面交互模式
cae-cli interactive --lang en

# 使用交互模式进行模型分析
# 在交互界面中可以直接选择菜单选项：
# 1. 分析模型
# 2. 参数优化
# 3. AI生成模型
# 4. 知识库查询
# 5. 退出

# 也可以在交互模式中直接输入命令
# 例如直接输入：analyze model.step --material Q235
8. 🤖 AI学习助手模式（最新功能）
进入交互模式后，选择"学习模式"即可使用AI学习助手：

bash
复制
# 启动交互模式（中文界面）
cae-cli interactive --lang zh

# 在交互菜单中选择"学习模式"（支持箭头键导航）
# 学习模式提供：
# 1. 基于本地Ollama模型的智能问答（qwen2.5:1.5b/phi3:mini）
# 2. RAG知识检索：自动检索knowledge/目录的机械知识库
# 3. 教学式回答：适合大一学生的教学式、一步步解释
# 4. 多轮对话：自动保存对话历史，支持深度问答
# 5. 自动服务启动：自动检测并启动Ollama服务

# 使用示例：
# 1. 问："Q235材料的屈服强度是多少？"
# 2. 问："M10螺栓的螺距是多少？"
# 3. 问："什么是间隙配合？"
# 4. 问："解释一下Von Mises应力的概念"
依赖安装：

bash
复制
# 安装AI学习助手所需依赖
pip install chromadb sentence-transformers requests

# 安装Ollama（请访问 https://ollama.com/ 下载安装）
# 运行Ollama服务并下载模型
ollama run phi3:mini
# 或
ollama run qwen2.5:1.5b
📖 命令参考
全局选项
选项	说明
--version, -v	显示版本信息
--verbose	启用详细输出模式
--config	指定配置文件路径
--help	显示帮助信息
可用命令
命令	说明	示例
parse	解析几何文件	cae-cli parse model.step
analyze	分析网格质量	cae-cli analyze mesh.msh
material	查询材料数据库	cae-cli material Q235
report	生成分析报告	cae-cli report static -i result.inp
config	管理配置	cae-cli config --list
version	显示版本	cae-cli version
info	系统信息	cae-cli info
interactive	交互模式（支持多语言 + AI学习助手）	cae-cli interactive --lang zh
🔧 Python API
除了CLI，你也可以在Python代码中使用：

python
复制
from sw_helper.geometry import GeometryParser
from sw_helper.material import MaterialDatabase, MechanicsCalculator

# 解析几何
parser = GeometryParser()
geo_data = parser.parse("model.step")
print(f"体积: {geo_data['volume']} m³")

# 查询材料
db = MaterialDatabase()
q235 = db.get_material("Q235")
print(f"弹性模量: {q235['elastic_modulus']} Pa")

# 力学计算
calc = MechanicsCalculator()
result = calc.calculate_stress(
    force=10000,  # 10kN
    area=0.001,   # 0.001 m²
    material_name="Q235"
)
print(f"安全系数: {result['safety_factor']}")
📖 项目文档
CAE-CLI 提供了完整的文档体系，帮助不同角色的用户快速上手：

👤 用户文档
文档	用途	路径
QUICKSTART.md	3步快速开始，包含5个核心命令示例	docs/QUICKSTART.md
INSTALLATION_GUIDE.md	详细安装指南，支持Windows/Linux/macOS	docs/INSTALLATION_GUIDE.md
FAQ.md	10个常见问题解答，解决使用中的疑难问题	docs/FAQ.md
👨‍💻 开发者文档
文档	用途	路径
API_REFERENCE.md	完整的Python API参考，所有模块详细说明	docs/API_REFERENCE.md
CONTRIBUTING.md	贡献指南，包含PR模板和开发规范	docs/CONTRIBUTING.md
CLAUDE.md	Claude Code助手配置，项目架构说明	CLAUDE.md
🛠️ 工具与脚本
工具	用途	说明
generate_api_docs.py	API文档自动生成	一键生成HTML/Markdown格式API文档
run_tests.py/.sh/.bat	跨平台测试脚本	支持Windows/Linux/macOS测试运行
🌐 在线文档
API文档在线查看：docs/api/ 目录包含完整的HTML API文档
自动更新：使用 python generate_api_docs.py 重新生成API文档
📁 项目结构
cae-cli/
├── src/sw_helper/           # 主包（原有功能）
│   ├── cli.py              # CLI入口（核心文件）
│   ├── geometry/           # 几何解析模块
│   ├── mesh/               # 网格分析模块
│   ├── material/           # 材料力学模块
│   ├── report/             # 报告生成模块
│   ├── optimization/       # 参数优化模块
│   ├── ai/                 # AI辅助设计模块
│   ├── chat/               # 交互式聊天模块
│   ├── integrations/       # CAD软件集成模块（旧接口）
│   ├── mcp/                # MCP协议接口模块
│   └── utils/              # 工具模块
├── src/integrations/       # 🚀 插件化架构（全新）
│   ├── _base/              # 抽象基类
│   │   ├── connectors.py   # CAD/CAE连接器抽象基类
│   │   └── workflow.py     # 工作流引擎
│   ├── cad/                # CAD连接器实现
│   │   ├── freecad.py      # FreeCAD连接器（新架构）
│   │   └── __init__.py
│   ├── cae/                # CAE连接器实现
│   │   ├── calculix.py     # CalculiX连接器（新架构）
│   │   └── __init__.py
│   ├── mesher/             # 网格生成器集成
│   │   ├── gmsh.py         # Gmsh网格生成器（新架构）
│   │   └── __init__.py
│   └── __init__.py         # 统一导出
├── src/core/               # 🎯 核心数据类型
│   └── types.py           # 统一数据流和配置模型
├── examples/               # 示例文件
│   ├── project.yaml       # 标准化配置文件示例
│   └── demo_config_usage.py # 配置系统使用演示
├── data/                   # 数据文件
│   ├── materials.json     # 材料库
│   ├── languages.json     # 多语言包
│   └── config.yaml        # 默认配置
├── tests/                  # 测试
├── docs/                   # 文档
├── pyproject.toml         # 项目配置
├── setup.py               # 安装脚本
└── README.md              # 说明文档
🔗 软件集成与协议
🎯 插件化架构
标准化接口：统一的CADConnector和CAEConnector抽象基类
灵活扩展：通过实现抽象方法轻松集成新软件
工作流管理：WorkflowEngine管理CAD→CAE完整分析流程
配置驱动：YAML配置文件定义完整仿真参数和工作流
🔧 已实现的连接器
✅ CAD: FreeCAD：基于新架构的标准化连接器，支持参数修改、重建、导出
✅ CAE: CalculiX：开源有限元分析软件集成，支持静力、模态、热分析
✅ 网格生成: Gmsh：开源网格生成器集成，支持2D/3D网格生成和质量控制
✅ MCP服务器: GitHub仓库管理：专门针对 https://github.com/yd5768365-hue/caw-cli.git 仓库的MCP服务器，支持完整的文件操作和Git操作
🔄 旧接口兼容：原有FreeCAD/SolidWorks连接器保持可用
🔄 标准数据流
格式标准化：遵循 CAD → STEP → MSH → INP → VTK 数据流路径
统一配置：SimulationConfig模型管理所有仿真参数
结果标准化：SimulationResult统一结果数据格式
🤝 工作流支持
预定义工作流：stress_analysis, modal_analysis, topology_optimization
自定义工作流：支持用户定义任意分析流程
异常处理：完整的步骤级错误处理和进度跟踪
📊 仿真工具链
Gmsh：开源网格生成器（✅ 已实现集成）
CalculiX：开源有限元分析（✅ 已实现）
通用格式支持：.inp (Abaqus/CalculiX), .bdf (NASTRAN), .msh (Gmsh)
🤖 MCP (Model Context Protocol) 服务器
FreeCAD MCP服务器：将FreeCAD建模功能暴露为MCP工具，支持AI智能调用
GitHub仓库MCP服务器：专门针对 https://github.com/yd5768365-hue/caw-cli.git 仓库的MCP服务器，提供：
完整的文件操作：读取、写入、创建、删除、重命名文件
完整的Git操作：状态查看、添加、提交、推送、拉取、分支管理
仓库信息查询：获取仓库基本信息、文件统计、提交历史
演示脚本：demo_github_mcp.py 展示所有功能
🚀 插件化架构使用
1. 配置文件示例
创建 project.yaml 定义完整仿真流程：

yaml
复制
# examples/project.yaml
project:
  name: "支架静力分析"
  description: "分析支架在载荷下的应力和变形"

cad:
  software: "freecad"
  model: "bracket.FCStd"
  parameters:
    thickness: 5.0    # mm
    fillet_radius: 3.0 # mm

mesh:
  element_size: 2.0
  element_type: "tetrahedron"

material:
  name: "Q235"
  properties:
    - name: "elastic_modulus"
      value: 210e9
      unit: "Pa"

analysis:
  type: "static"
  solver: "calculix"
  
  loads:
    - type: "force"
      value: -1000.0
      direction: [0, 0, -1]
  
  constraints:
    - type: "fixed"
      location: "bottom_surface"
2. Python API 使用
python
复制
from integrations import WorkflowEngine
from integrations.cad.freecad import FreeCADConnector
from integrations.cae.calculix import CalculiXConnector
from core.types import SimulationConfig

# 创建连接器
cad = FreeCADConnector()
cae = CalculiXConnector()

# 创建工作流引擎
workflow = WorkflowEngine(cad_connector=cad, cae_connector=cae)

# 加载配置
config = SimulationConfig.from_yaml("project.yaml")

# 运行工作流
result = workflow.run_workflow(
    "stress_analysis",
    cad_software="freecad",
    cae_software="calculix",
    config=config
)

# 查看结果
print(f"最大应力: {result.max_stress} Pa")
print(f"最大位移: {result.max_displacement} m")
print(f"安全系数: {result.safety_factor}")
3. 完整工作流示例 (CAD → Mesh → CAE)
python
复制
from integrations import WorkflowEngine
from integrations.cad.freecad import FreeCADConnector
from integrations.mesher.gmsh import GmshConnector
from integrations.cae.calculix import CalculiXConnector
from core.types import SimulationConfig

# 创建完整的工具链连接器
cad = FreeCADConnector()
mesher = GmshConnector()
cae = CalculiXConnector()

# 创建工作流引擎（支持网格生成）
workflow = WorkflowEngine(
    cad_connector=cad,
    mesher_connector=mesher,  # 可选的网格生成器
    cae_connector=cae
)

# 加载配置
config = SimulationConfig.from_yaml("project.yaml")

# 运行完整工作流：CAD建模 → 网格生成 → CAE分析
result = workflow.run_workflow(
    "complete_analysis",
    cad_software="freecad",
    mesher_software="gmsh",    # 指定网格生成器
    cae_software="calculix",
    config=config
)

# 查看完整分析结果
print(f"模型信息: {result.cad_info}")
print(f"网格质量: {result.mesh_quality}")
print(f"最大应力: {result.max_stress} Pa")
print(f"安全系数: {result.safety_factor}")
4. 网格生成器使用示例
python
复制
from integrations.mesher.gmsh import GmshConnector

# 创建Gmsh连接器
gmsh = GmshConnector()

# 连接Gmsh
if gmsh.connect():
    # 从STEP文件生成网格
    success = gmsh.generate_mesh(
        input_file="model.step",
        output_file="model.msh",
        element_size=2.0,
        element_type="tetrahedron"
    )

    if success:
        # 分析网格质量
        quality = gmsh.analyze_mesh_quality("model.msh")
        print(f"网格质量指标: {quality}")

        # 可视化网格
        gmsh.visualize_mesh("model.msh")
6. 扩展新软件
要集成新的CAD软件，继承 CADConnector 并实现抽象方法：

python
复制
from integrations._base.connectors import CADConnector

class MyCADConnector(CADConnector):
    def connect(self) -> bool:
        # 连接软件
        pass
    
    def load_model(self, file_path: Path) -> bool:
        # 加载模型
        pass
    
    def get_parameter(self, name: str) -> Optional[float]:
        # 获取参数
        pass
    
    def set_parameter(self, name: str, value: float) -> bool:
        # 设置参数
        pass
    
    def rebuild(self) -> bool:
        # 重建模型
        pass
    
    def export_step(self, output_path: Path) -> bool:
        # 导出STEP
        pass
    
    def get_supported_formats(self) -> List[FileFormat]:
        # 返回支持的格式
        pass
7. 快速测试
运行演示脚本查看新架构功能：

bash
复制
python demo_workflow.py
🛠️ 开发
安装开发依赖
bash
复制
git clone https://github.com/yd5768365-hue/caw-cli.git
cd caw-cli
pip install -e ".[dev]"
运行测试
bash
复制
# 运行所有测试
pytest

# 运行新架构连接器测试
python test_freecad_connector.py
python test_calculix_connector.py
python test_gmsh.py

# 运行工作流集成测试
python test_workflow_integration.py

# 运行工具模块测试
python test_utils.py
python test_unicode_display.py
python test_format_text.py

# 运行工作流演示
python demo_workflow.py
代码格式化
bash
复制
black src/
类型检查
bash
复制
mypy src/sw_helper src/integrations src/core
📝 配置文件
配置文件位于 ~/.cae-cli/config.json，可以自定义：

json
复制
{
  "default_material": "Q235",
  "safety_factor": 1.5,
  "default_output_format": "html",
  "verbose": false
}
🐛 故障排除
安装失败
bash
复制
# 升级pip
pip install --upgrade pip

# 安装基础版本（不含可选依赖）
pip install cae-cli

# 安装完整版本
pip install "cae-cli[full]"
命令找不到
bash
复制
# 确保Python Scripts目录在PATH中
# Windows: %APPDATA%\Python\Python3x\Scripts
# Linux/macOS: ~/.local/bin

# 或直接使用Python模块方式
python -m sw_helper --help
🤝 贡献
欢迎提交Issue和Pull Request！

Fork 本仓库
创建特性分支 (git checkout -b feature/amazing-feature)
提交更改 (git commit -m 'Add amazing feature')
推送到分支 (git push origin feature/amazing-feature)
创建 Pull Request
📄 许可证
本项目采用 MIT 许可证。

📮 联系方式与支持
📍 项目信息
项目主页：https://github.com/yd5768365-hue/caw-cli
文档站点：https://caw-cli.readthedocs.io (规划中)
PyPI包：https://pypi.org/project/cae-cli/ (规划中)
🐛 问题报告
GitHub Issues：https://github.com/yd5768365-hue/caw-cli/issues
功能建议：欢迎提交Issue描述您的需求
🎯 项目状态
当前版本：v0.2.0+ (插件化架构 + 完整文档体系)
主要用户：机械专业学生、FreeCAD用户、CAE学习者、插件开发者、开源贡献者
开发进度：
✅ 基础功能：几何解析、材料计算、网格分析
✅ AI与交互：AI辅助设计、多语言支持、交互模式、AI学习助手（Ollama+RAG）
✅ 插件化架构：标准化CAD/CAE接口，FreeCAD+CalculiX集成
✅ 网格生成器：Gmsh标准化集成（src/integrations/mesher/gmsh.py）
✅ 完整文档体系：5个核心文档 + API自动生成脚本
🔄 工作流CLI命令集成：进行中，即将发布
🔄 PyPI包发布：规划中，需要完善测试和打包
🙏 致谢
Click - Python CLI框架
Rich - 终端美化库
PythonOCC - OpenCASCADE Python绑定

