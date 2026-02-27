"""
核心数据类型定义 - 标准化CAD/CAE集成中的数据结构和配置

此模块定义统一的数据流格式、配置模型和枚举类型，
确保不同软件组件之间的数据交换一致性。
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

# 使用pydantic需要额外安装，这里用dataclass替代
# from pydantic import BaseModel, Field, validator


class FileFormat(Enum):
    """文件格式枚举 - 定义标准化的数据流格式

    遵循 CAD → STEP → MSH → INP → VTK 的数据流路径
    """

    # CAD格式
    FCSTD = "FCStd"  # FreeCAD原生格式
    SLDPRT = "sldprt"  # SolidWorks零件
    SLDASM = "sldasm"  # SolidWorks装配体

    # 几何交换格式
    STEP = "step"  # ISO 10303标准
    STL = "stl"  # 三角网格
    IGES = "iges"  # 旧版交换格式
    BREP = "brep"  # OpenCASCADE边界表示

    # 网格格式
    MSH = "msh"  # Gmsh网格格式
    INP = "inp"  # Abaqus/CalculiX输入格式
    BDF = "bdf"  # NASTRAN格式
    CAS = "cas"  # Fluent格式

    # 结果格式
    VTK = "vtk"  # VTK可视化格式
    FRD = "frd"  # CalculiX结果格式
    ODB = "odb"  # Abaqus结果格式
    RST = "rst"  # ANSYS结果格式

    # 报告格式
    JSON = "json"  # 结构化数据
    HTML = "html"  # 网页报告
    PDF = "pdf"  # 可打印报告
    MARKDOWN = "md"  # Markdown文档


@dataclass
class MaterialProperty:
    """材料属性定义"""

    name: str
    value: float
    unit: str
    description: Optional[str] = None


@dataclass
class LoadCondition:
    """载荷条件定义"""

    type: str  # "force", "pressure", "moment", "temperature"
    value: Union[float, List[float]]
    location: Optional[str] = None
    direction: Optional[List[float]] = None
    distribution: Optional[str] = None  # "uniform", "linear", "parabolic"


@dataclass
class BoundaryCondition:
    """边界条件定义"""

    type: str  # "fixed", "displacement", "symmetry", "contact"
    location: str
    value: Optional[Union[float, List[float]]] = None
    degrees_of_freedom: Optional[List[bool]] = None  # [x, y, z, rx, ry, rz]


@dataclass
class SimulationConfig:
    """仿真配置模型 - 标准化仿真参数

    用于存储从project.yaml解析的仿真配置信息。
    """

    # 基本信息
    project_name: str = "未命名项目"
    description: Optional[str] = None

    # CAD配置
    cad_software: str = "freecad"
    cad_file: Optional[Path] = None
    parameters: Dict[str, float] = field(default_factory=dict)

    # 网格配置
    mesh_generator: str = "gmsh"
    element_type: str = "tetrahedron"  # "tetrahedron", "hexahedron", "mixed"
    element_size: float = 2.0
    mesh_quality: Dict[str, float] = field(default_factory=dict)

    # 材料配置
    material_name: str = "Q235"
    material_properties: List[MaterialProperty] = field(default_factory=list)

    # 分析配置
    analysis_type: str = "static"  # "static", "modal", "thermal", "buckling"
    solver: str = "calculix"

    # 载荷和边界条件
    loads: List[LoadCondition] = field(default_factory=list)
    constraints: List[BoundaryCondition] = field(default_factory=list)

    # 求解器设置
    solver_settings: Dict[str, Any] = field(default_factory=dict)

    # 输出配置
    output_dir: Path = Path("./simulation_output")
    output_formats: List[FileFormat] = field(default_factory=lambda: [FileFormat.VTK, FileFormat.JSON])
    report_format: FileFormat = FileFormat.HTML

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "SimulationConfig":
        """从YAML文件加载配置

        Args:
            yaml_path: YAML配置文件路径

        Returns:
            SimulationConfig: 配置对象

        Raises:
            FileNotFoundError: YAML文件不存在时
            yaml.YAMLError: YAML解析错误时
        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {yaml_path}")

        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfig":
        """从字典创建配置对象

        Args:
            data: 配置字典

        Returns:
            SimulationConfig: 配置对象
        """
        # 转换文件路径
        if "cad_file" in data and data["cad_file"]:
            data["cad_file"] = Path(data["cad_file"])

        if "output_dir" in data and data["output_dir"]:
            data["output_dir"] = Path(data["output_dir"])

        # 转换文件格式枚举
        if "output_formats" in data:
            data["output_formats"] = [FileFormat(fmt) for fmt in data["output_formats"]]

        if "report_format" in data:
            data["report_format"] = FileFormat(data["report_format"])

        # 创建配置对象
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）

        Returns:
            Dict[str, Any]: 字典表示
        """
        data = self.__dict__.copy()

        # 转换Path对象为字符串
        if data["cad_file"]:
            data["cad_file"] = str(data["cad_file"])

        data["output_dir"] = str(data["output_dir"])

        # 转换枚举为字符串
        data["output_formats"] = [fmt.value for fmt in data["output_formats"]]
        data["report_format"] = data["report_format"].value

        return data

    def to_yaml(self, yaml_path: Path) -> bool:
        """保存配置到YAML文件

        Args:
            yaml_path: 输出YAML文件路径

        Returns:
            bool: 保存是否成功
        """
        try:
            data = self.to_dict()
            yaml_path.parent.mkdir(parents=True, exist_ok=True)

            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)

            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def validate(self) -> List[str]:
        """验证配置有效性

        Returns:
            List[str]: 错误消息列表，为空表示配置有效
        """
        errors = []

        # 检查必要字段
        if not self.project_name:
            errors.append("项目名称不能为空")

        if not self.cad_file:
            errors.append("CAD文件路径不能为空")
        elif not self.cad_file.exists():
            errors.append(f"CAD文件不存在: {self.cad_file}")

        # 检查网格配置
        if self.element_size <= 0:
            errors.append("单元尺寸必须大于0")

        # 检查分析类型
        valid_analysis_types = ["static", "modal", "thermal", "buckling", "cfd"]
        if self.analysis_type not in valid_analysis_types:
            errors.append(f"不支持的分析类型: {self.analysis_type}")

        return errors


@dataclass
class SimulationResult:
    """仿真结果数据结构"""

    config: SimulationConfig
    status: str  # "completed", "failed", "running"
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None

    # 数值结果
    max_stress: Optional[float] = None
    max_displacement: Optional[float] = None
    safety_factor: Optional[float] = None
    natural_frequencies: Optional[List[float]] = None

    # 文件结果
    result_files: Dict[FileFormat, Path] = field(default_factory=dict)
    report_file: Optional[Path] = None

    # 原始数据
    raw_data: Dict[str, Any] = field(default_factory=dict)


def create_default_config(project_name: str = "默认项目") -> SimulationConfig:
    """创建默认仿真配置

    Args:
        project_name: 项目名称

    Returns:
        SimulationConfig: 默认配置对象
    """
    config = SimulationConfig(
        project_name=project_name,
        description=f"{project_name}的仿真分析配置",
        # 默认材料属性
        material_properties=[
            MaterialProperty("弹性模量", 210e9, "Pa", "杨氏模量"),
            MaterialProperty("泊松比", 0.3, "", "横向变形系数"),
            MaterialProperty("密度", 7850, "kg/m³", "材料密度"),
            MaterialProperty("屈服强度", 235e6, "Pa", "屈服极限"),
        ],
        # 默认载荷
        loads=[
            LoadCondition(
                type="force",
                value=1000.0,
                location="top_face",
                direction=[0, 0, -1],
                distribution="uniform",
            )
        ],
        # 默认约束
        constraints=[
            BoundaryCondition(
                type="fixed",
                location="bottom_face",
                degrees_of_freedom=[True, True, True, False, False, False],
            )
        ],
        # 默认求解器设置
        solver_settings={
            "max_iterations": 100,
            "tolerance": 1e-6,
            "solver_type": "direct",
            "num_processors": 1,
        },
    )

    return config
