# CAE-CLI API 参考文档 🔧

本文档提供 CAE-CLI 的完整 Python API 参考。所有 API 均遵循类型注解，支持 IDE 自动补全和类型检查。

**📖 文档生成方式**：
- 使用 `pdoc3` 自动生成 HTML 文档（位于 `docs/api/`）
- 本文档为简化版 Markdown 参考，完整文档请查看 HTML 版本
- 最后更新：2026年2月

## 🚀 快速导航

### 核心模块
- **[sw_helper.cli](#sw_helpercli)** - CLI 入口点
- **[sw_helper.geometry](#sw_helpergeometry)** - 几何解析
- **[sw_helper.mesh](#sw_helpermesh)** - 网格分析
- **[sw_helper.material](#sw_helpermaterial)** - 材料力学
- **[sw_helper.mechanics](#sw_helpermechanics)** - 力学计算
- **[sw_helper.report](#sw_helperreport)** - 报告生成
- **[sw_helper.optimization](#sw_helperoptimization)** - 参数优化
- **[sw_helper.ai](#sw_helperai)** - AI 辅助设计

### 插件化架构（新）
- **[integrations._base.connectors](#integrations_baseconnectors)** - 连接器抽象基类
- **[integrations._base.workflow](#integrations_baseworkflow)** - 工作流引擎
- **[integrations.cad.freecad](#integrationscadfreecad)** - FreeCAD 连接器
- **[integrations.cae.calculix](#integrationscaecalculix)** - CalculiX 连接器

### 核心类型
- **[core.types](#coretypes)** - 统一数据模型和配置

---

## sw_helper.cli

CLI 应用程序的入口点，基于 Click 框架实现。

### `main()`
```python
def main(args: Optional[List[str]] = None) -> int:
    """
    CLI 入口函数。

    Args:
        args: 命令行参数列表，默认为 sys.argv[1:]

    Returns:
        退出码：0 表示成功，非零表示错误

    Example:
        >>> import sys
        >>> sys.argv = ['cae-cli', '--help']
        >>> main()
        0
    """
```

### `cli` 对象
```python
@click.group()
@click.version_option(version=__version__)
@click.option('-v', '--verbose', is_flag=True, help='启用详细输出模式')
@click.option('-c', '--config', type=click.Path(), help='指定配置文件路径')
def cli(verbose: bool, config: Optional[str]):
    """CAE-CLI: SolidWorks CAE Integration Assistant"""
```

**可用命令**：
- `parse` - 解析几何文件
- `analyze` - 分析网格质量
- `material` - 查询材料数据库
- `report` - 生成分析报告
- `optimize` - 参数优化
- `ai` - AI 辅助设计
- `chat` - 交互式聊天
- `workflow` - 运行 CAD/CAE 工作流

---

## sw_helper.geometry

几何文件解析模块，支持 STEP、STL、IGES 格式。

### `GeometryParser`
```python
class GeometryParser:
    """几何文件解析器"""

    def parse(self, file_path: PathLike, format: Optional[str] = None) -> Dict[str, Any]:
        """
        解析几何文件并提取信息。

        Args:
            file_path: 文件路径
            format: 文件格式（'step', 'stl', 'iges'），可选，自动检测

        Returns:
            包含几何信息的字典

        Raises:
            FileNotFoundError: 文件不存在
            UnsupportedFormatError: 不支持的格式

        Example:
            >>> parser = GeometryParser()
            >>> data = parser.parse("model.step")
            >>> print(data['volume'])
            0.00025  # m³
        """

    def get_supported_formats(self) -> List[str]:
        """返回支持的格式列表"""

    def export_to_json(self, data: Dict[str, Any], output_path: PathLike) -> bool:
        """将解析结果导出为 JSON 文件"""
```

### `GeometryAnalyzer`
```python
class GeometryAnalyzer:
    """几何分析器"""

    def calculate_volume(self, vertices: np.ndarray, faces: np.ndarray) -> float:
        """计算多面体体积"""

    def calculate_surface_area(self, vertices: np.ndarray, faces: np.ndarray) -> float:
        """计算表面积"""

    def check_manifold(self, vertices: np.ndarray, faces: np.ndarray) -> bool:
        """检查是否为流形几何"""
```

---

## sw_helper.mesh

网格质量分析模块，支持 .msh、.inp、.bdf 格式。

### `MeshQualityAnalyzer`
```python
class MeshQualityAnalyzer:
    """网格质量分析器"""

    def analyze(self, file_path: PathLike,
                metrics: Optional[List[str]] = None) -> MeshQualityReport:
        """
        分析网格质量。

        Args:
            file_path: 网格文件路径
            metrics: 要计算的质量指标列表，默认为所有指标

        Returns:
            MeshQualityReport 对象

        Example:
            >>> analyzer = MeshQualityAnalyzer()
            >>> report = analyzer.analyze("mesh.msh", metrics=["aspect_ratio", "skewness"])
            >>> print(report.overall_quality)
            "优秀"
        """

    def get_available_metrics(self) -> List[str]:
        """返回可用的质量指标"""
```

### `MeshQualityReport`
```python
@dataclass
class MeshQualityReport:
    """网格质量分析报告"""

    file_path: Path
    element_count: int
    node_count: int
    metrics: Dict[str, Dict[str, float]]  # 指标名称 -> {最小值, 最大值, 平均值, 标准差}
    quality_distribution: Dict[str, float]  # 质量分布
    overall_quality: str  # "优秀", "良好", "一般", "较差"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""

    def to_json(self, file_path: PathLike) -> bool:
        """导出为 JSON 文件"""
```

### 质量指标
- `aspect_ratio` - 纵横比（理想值：1.0）
- `skewness` - 偏斜度（理想值：0.0）
- `orthogonal_quality` - 正交质量（理想值：1.0）
- `jacobian_ratio` - 雅可比比率
- `warpage` - 翘曲度

---

## sw_helper.material

材料数据库和属性查询模块。

### `MaterialDatabase`
```python
class MaterialDatabase:
    """材料数据库"""

    def __init__(self, db_path: Optional[PathLike] = None):
        """
        初始化材料数据库。

        Args:
            db_path: 材料数据库 JSON 文件路径，默认为内置数据库
        """

    def get_material(self, name: str) -> Dict[str, Any]:
        """
        获取材料属性。

        Args:
            name: 材料名称（如 "Q235", "Q345", "Aluminum6061"）

        Returns:
            材料属性字典

        Raises:
            MaterialNotFoundError: 材料不存在
        """

    def search_materials(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索材料"""

    def list_materials(self) -> List[str]:
        """列出所有材料名称"""

    def add_custom_material(self, name: str, properties: Dict[str, Any]) -> bool:
        """添加自定义材料"""
```

### `MechanicsCalculator`
```python
class MechanicsCalculator:
    """力学计算器"""

    def calculate_stress(self, force: float, area: float,
                        material_name: Optional[str] = None,
                        material_properties: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        计算应力、安全系数等。

        Args:
            force: 力（N）
            area: 截面积（m²）
            material_name: 材料名称
            material_properties: 材料属性字典（如果未提供 material_name）

        Returns:
            计算结果字典

        Example:
            >>> calc = MechanicsCalculator()
            >>> result = calc.calculate_stress(10000, 0.001, "Q235")
            >>> print(result['safety_factor'])
            23.5
        """

    def calculate_buckling_load(self, length: float, moment_of_inertia: float,
                               youngs_modulus: float, end_condition: str = "fixed-free") -> float:
        """计算屈曲载荷"""

    def calculate_deflection(self, load: float, length: float,
                            moment_of_inertia: float, youngs_modulus: float,
                            load_type: str = "point") -> float:
        """计算挠度"""
```

---

## sw_helper.mechanics

力学计算引擎，支持多种分析类型。

### `MechanicsEngine`
```python
class MechanicsEngine:
    """力学计算引擎"""

    def static_analysis(self, forces: List[Force], constraints: List[Constraint],
                       material: Material, geometry: Geometry) -> StaticResult:
        """静力分析"""

    def modal_analysis(self, geometry: Geometry, material: Material,
                      num_modes: int = 5) -> ModalResult:
        """模态分析"""

    def thermal_analysis(self, heat_sources: List[HeatSource],
                        boundary_conditions: List[TemperatureBC],
                        material: Material) -> ThermalResult:
        """热分析"""
```

### 数据类型
```python
@dataclass
class Force:
    """力载荷"""
    value: float  # 大小（N）
    direction: Tuple[float, float, float]  # 方向向量
    location: Optional[Tuple[float, float, float]] = None  # 作用点

@dataclass
class Material:
    """材料"""
    name: str
    elastic_modulus: float  # 弹性模量（Pa）
    poisson_ratio: float  # 泊松比
    yield_strength: float  # 屈服强度（Pa）
    density: float  # 密度（kg/m³）

@dataclass
class StaticResult:
    """静力分析结果"""
    max_stress: float  # 最大应力（Pa）
    max_displacement: float  # 最大位移（m）
    safety_factor: float  # 安全系数
    stress_distribution: np.ndarray  # 应力分布
    warning_level: str  # "green", "yellow", "red"
```

---

## sw_helper.report

报告生成模块，支持 HTML、PDF、JSON、Markdown 格式。

### `ReportGenerator`
```python
class ReportGenerator:
    """报告生成器"""

    def generate_static_report(self, result: StaticResult,
                             template: Optional[str] = None) -> str:
        """生成静力分析报告"""

    def generate_mesh_report(self, report: MeshQualityReport,
                           format: str = "html") -> str:
        """生成网格质量报告"""

    def generate_optimization_report(self, history: List[Dict[str, Any]],
                                   best_params: Dict[str, float]) -> str:
        """生成优化报告"""

    def save_report(self, content: str, output_path: PathLike,
                   format: Optional[str] = None) -> bool:
        """保存报告到文件"""
```

### 模板系统
报告生成使用 Jinja2 模板引擎，模板位于 `data/templates/`：
- `static_report.html.j2` - 静力分析 HTML 模板
- `mesh_report.md.j2` - 网格质量 Markdown 模板
- `optimization_report.json.j2` - 优化结果 JSON 模板

---

## sw_helper.optimization

参数优化模块，支持自动迭代和结果评估。

### `ParametricOptimizer`
```python
class ParametricOptimizer:
    """参数优化器"""

    def optimize(self, model_path: PathLike,
                parameter_name: str,
                value_range: Tuple[float, float],
                steps: int = 10,
                objective: str = "maximize_quality") -> OptimizationResult:
        """
        优化单个参数。

        Args:
            model_path: CAD 模型文件路径
            parameter_name: 参数名称
            value_range: 参数值范围（最小值, 最大值）
            steps: 迭代步数
            objective: 优化目标

        Returns:
            OptimizationResult 对象

        Example:
            >>> optimizer = ParametricOptimizer()
            >>> result = optimizer.optimize(
            ...     "bracket.FCStd",
            ...     "Fillet_Radius",
            ...     (2.0, 15.0),
            ...     steps=5
            ... )
            >>> print(result.best_value)
            8.5
        """

    def multi_parameter_optimize(self, model_path: PathLike,
                               parameters: Dict[str, Tuple[float, float]],
                               max_iterations: int = 20) -> Dict[str, Any]:
        """多参数优化"""
```

### `OptimizationResult`
```python
@dataclass
class OptimizationResult:
    """优化结果"""

    parameter_name: str
    best_value: float
    best_score: float
    history: List[Dict[str, Any]]  # 迭代历史
    convergence_curve: np.ndarray  # 收敛曲线

    def plot_convergence(self, save_path: Optional[PathLike] = None) -> bool:
        """绘制收敛曲线"""

    def to_dataframe(self) -> pd.DataFrame:
        """转换为 Pandas DataFrame"""
```

---

## sw_helper.ai

AI 辅助设计模块，支持自然语言建模和智能建议。

### `ModelGenerator`
```python
class ModelGenerator:
    """AI 模型生成器"""

    def generate_from_text(self, description: str,
                          output_path: PathLike) -> bool:
        """
        从自然语言描述生成 3D 模型。

        Args:
            description: 自然语言描述
            output_path: 输出文件路径（.FCStd 或 .STEP）

        Returns:
            是否成功

        Example:
            >>> generator = ModelGenerator()
            >>> generator.generate_from_text(
            ...     "带圆角的立方体，长100宽50高30圆角10",
            ...     "cube.FCStd"
            ... )
            True
        """

    def optimize_with_ai(self, model_path: PathLike,
                        constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """AI 辅助优化"""
```

### `LLMClient`
```python
class LLMClient:
    """LLM 客户端（支持多个提供商）"""

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        初始化 LLM 客户端。

        Args:
            provider: 提供商（"openai", "anthropic", "ollama"）
            api_key: API 密钥
        """

    def get_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """获取改进建议"""

    def answer_technical_question(self, question: str) -> str:
        """回答技术问题"""
```

---

## integrations._base.connectors

CAD/CAE 连接器抽象基类，定义标准化接口。

### `CADConnector`（抽象基类）
```python
class CADConnector(ABC):
    """CAD 连接器抽象基类"""

    @abstractmethod
    def connect(self) -> bool:
        """连接 CAD 软件"""

    @abstractmethod
    def load_model(self, file_path: Path) -> bool:
        """加载模型文件"""

    @abstractmethod
    def get_parameter(self, name: str) -> Optional[float]:
        """获取参数值"""

    @abstractmethod
    def set_parameter(self, name: str, value: float) -> bool:
        """设置参数值"""

    @abstractmethod
    def rebuild(self) -> bool:
        """重建模型"""

    @abstractmethod
    def export_step(self, output_path: Path) -> bool:
        """导出为 STEP 格式"""

    @abstractmethod
    def get_supported_formats(self) -> List[FileFormat]:
        """返回支持的格式列表"""
```

### `CAEConnector`（抽象基类）
```python
class CAEConnector(ABC):
    """CAE 连接器抽象基类"""

    @abstractmethod
    def connect(self) -> bool:
        """连接 CAE 软件"""

    @abstractmethod
    def create_input_file(self, config: SimulationConfig) -> bool:
        """创建输入文件"""

    @abstractmethod
    def run_analysis(self) -> bool:
        """运行分析"""

    @abstractmethod
    def extract_results(self) -> Optional[SimulationResult]:
        """提取结果"""

    @abstractmethod
    def get_supported_analysis_types(self) -> List[str]:
        """返回支持的分析类型"""
```

---

## integrations._base.workflow

工作流引擎，管理 CAD→CAE 完整分析流程。

### `WorkflowEngine`
```python
class WorkflowEngine:
    """工作流引擎"""

    def __init__(self, cad_connector: CADConnector, cae_connector: CAEConnector):
        """
        初始化工作流引擎。

        Args:
            cad_connector: CAD 连接器实例
            cae_connector: CAE 连接器实例
        """

    def run_workflow(self, workflow_type: str,
                    cad_software: str,
                    cae_software: str,
                    config: SimulationConfig) -> SimulationResult:
        """
        运行完整工作流。

        Args:
            workflow_type: 工作流类型（"stress_analysis", "modal_analysis", ...）
            cad_software: CAD 软件名称
            cae_software: CAE 软件名称
            config: 仿真配置

        Returns:
            SimulationResult 对象

        Example:
            >>> workflow = WorkflowEngine(cad, cae)
            >>> config = SimulationConfig.from_yaml("project.yaml")
            >>> result = workflow.run_workflow(
            ...     "stress_analysis",
            ...     "freecad",
            ...     "calculix",
            ...     config
            ... )
        """

    def get_available_workflows(self) -> List[str]:
        """返回可用的工作流类型"""
```

---

## integrations.cad.freecad

FreeCAD 连接器实现。

### `FreeCADConnector`
```python
class FreeCADConnector(CADConnector):
    """FreeCAD 连接器"""

    def connect(self) -> bool:
        """连接 FreeCAD"""
        # 尝试导入 FreeCAD 模块
        # 设置 Python 路径等

    def load_model(self, file_path: Path) -> bool:
        """加载 FreeCAD 模型（.FCStd）"""

    def get_parameter(self, name: str) -> Optional[float]:
        """获取 FreeCAD 参数"""

    def set_parameter(self, name: str, value: float) -> bool:
        """设置 FreeCAD 参数"""

    def rebuild(self) -> bool:
        """重建 FreeCAD 模型"""

    def export_step(self, output_path: Path) -> bool:
        """导出为 STEP 格式"""

    def get_supported_formats(self) -> List[FileFormat]:
        """返回 FreeCAD 支持的格式"""
        return [
            FileFormat("FCStd", "FreeCAD 原生格式", ".FCStd"),
            FileFormat("STEP", "STEP AP242", ".step", ".stp"),
            FileFormat("STL", "STL 网格", ".stl"),
            FileFormat("IGES", "IGES", ".iges", ".igs")
        ]
```

---

## integrations.cae.calculix

CalculiX 连接器实现。

### `CalculiXConnector`
```python
class CalculiXConnector(CAEConnector):
    """CalculiX 连接器"""

    def connect(self) -> bool:
        """连接 CalculiX"""
        # 检查 CCX_PATH 环境变量
        # 验证可执行文件

    def create_input_file(self, config: SimulationConfig) -> bool:
        """创建 CalculiX 输入文件（.inp）"""

    def run_analysis(self) -> bool:
        """运行 CalculiX 分析"""
        # 调用 ccx_2.21.exe 求解器

    def extract_results(self) -> Optional[SimulationResult]:
        """从 .frd 文件中提取结果"""

    def get_supported_analysis_types(self) -> List[str]:
        """返回 CalculiX 支持的分析类型"""
        return ["static", "modal", "thermal", "buckling"]
```

---

## core.types

统一数据模型和配置类型。

### `SimulationConfig`
```python
@dataclass
class SimulationConfig:
    """仿真配置"""

    project: ProjectConfig
    cad: CADConfig
    mesh: MeshConfig
    material: MaterialConfig
    analysis: AnalysisConfig

    @classmethod
    def from_yaml(cls, yaml_path: PathLike) -> "SimulationConfig":
        """从 YAML 文件加载配置"""

    def to_yaml(self, yaml_path: PathLike) -> bool:
        """保存为 YAML 文件"""

    def validate(self) -> List[str]:
        """验证配置，返回错误信息列表"""
```

### `SimulationResult`
```python
@dataclass
class SimulationResult:
    """仿真结果"""

    max_stress: float  # 最大应力（Pa）
    max_displacement: float  # 最大位移（m）
    safety_factor: float  # 安全系数
    stress_distribution: Optional[np.ndarray] = None  # 应力分布
    displacement_field: Optional[np.ndarray] = None  # 位移场
    convergence_data: Optional[Dict[str, Any]] = None  # 收敛数据
    warnings: List[str] = field(default_factory=list)  # 警告信息

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""

    def to_dataframe(self) -> pd.DataFrame:
        """转换为 DataFrame"""
```

### 其他重要类型
```python
@dataclass
class ProjectConfig:
    """项目配置"""
    name: str
    description: str
    author: Optional[str] = None

@dataclass
class CADConfig:
    """CAD 配置"""
    software: str  # "freecad", "solidworks"
    model: Path
    parameters: Dict[str, float]

@dataclass
class MeshConfig:
    """网格配置"""
    element_size: float
    element_type: str  # "tetrahedron", "hexahedron"
    quality_threshold: float = 0.3

@dataclass
class MaterialConfig:
    """材料配置"""
    name: str
    properties: Dict[str, float]

@dataclass
class AnalysisConfig:
    """分析配置"""
    type: str  # "static", "modal", "thermal"
    solver: str  # "calculix"
    loads: List[LoadConfig]
    constraints: List[ConstraintConfig]
```

---

## 🔧 使用示例

### 示例 1：使用几何解析 API
```python
from sw_helper.geometry import GeometryParser

parser = GeometryParser()
data = parser.parse("model.step")
print(f"体积: {data['volume']} m³")
print(f"表面积: {data['surface_area']} m²")
print(f"顶点数: {data['vertex_count']}")
```

### 示例 2：使用材料数据库
```python
from sw_helper.material import MaterialDatabase

db = MaterialDatabase()
q235 = db.get_material("Q235")
print(f"弹性模量: {q235['elastic_modulus']} Pa")
print(f"屈服强度: {q235['yield_strength']} Pa")

# 搜索材料
steels = db.search_materials("钢")
for steel in steels:
    print(f"{steel['name']}: {steel['yield_strength']/1e6:.0f} MPa")
```

### 示例 3：使用插件化架构
```python
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

print(f"最大应力: {result.max_stress/1e6:.2f} MPa")
print(f"安全系数: {result.safety_factor:.2f}")
```

### 示例 4：自定义连接器
```python
from integrations._base.connectors import CADConnector
from typing import List, Optional
from pathlib import Path

class MyCADConnector(CADConnector):
    """自定义 CAD 连接器示例"""

    def connect(self) -> bool:
        # 实现连接逻辑
        return True

    def load_model(self, file_path: Path) -> bool:
        # 实现模型加载
        return True

    # ... 实现其他抽象方法
```

---

## 📚 完整 API 文档

本文档为简化参考，完整 API 文档包括：
- 所有类、方法、属性的详细说明
- 类型签名和默认值
- 继承关系和实现细节
- 使用示例和注意事项

### 查看完整文档
```bash
# 生成最新 API 文档
python generate_api_docs.py

# 在浏览器中查看
open docs/api/index.html
```

### 文档生成脚本
项目包含 `generate_api_docs.py` 脚本，用于自动生成 API 文档：
```bash
python generate_api_docs.py --format html --output docs/api
python generate_api_docs.py --format markdown --output docs/API_REFERENCE.md
```

---

## 🐛 问题与反馈

如果发现 API 文档错误或缺失，请：
1. 检查 `docs/api/` 目录下的 HTML 文档
2. 运行 `python generate_api_docs.py` 重新生成
3. 在 [GitHub Issues](https://github.com/yd5768365-hue/caw-cli/issues) 报告问题

**📅 文档版本**：v0.2.0
**生成工具**：pdoc3
**最后更新**：2026年2月