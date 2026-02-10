"""
CAD/CAE连接器抽象基类 - 定义软件集成的统一接口

此模块提供插件化架构的核心抽象接口，允许不同的CAD和CAE软件
通过实现这些接口来集成到系统中。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum


class FileFormat(Enum):
    """支持的文件格式枚举"""

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


class CADConnector(ABC):
    """CAD软件连接器抽象基类

    定义CAD软件必须实现的通用接口，包括模型加载、参数操作、
    模型导出等核心功能。
    """

    @abstractmethod
    def connect(self) -> bool:
        """连接到CAD软件实例

        Returns:
            bool: 连接是否成功
        """
        pass

    @abstractmethod
    def load_model(self, file_path: Path) -> bool:
        """加载CAD模型文件

        Args:
            file_path: 模型文件路径

        Returns:
            bool: 加载是否成功

        Raises:
            FileNotFoundError: 文件不存在时
            ValueError: 文件格式不支持时
        """
        pass

    @abstractmethod
    def get_parameter(self, name: str) -> Optional[float]:
        """获取指定参数的值

        Args:
            name: 参数名称

        Returns:
            Optional[float]: 参数值，如果参数不存在则返回None
        """
        pass

    @abstractmethod
    def set_parameter(self, name: str, value: float) -> bool:
        """设置参数值

        Args:
            name: 参数名称
            value: 参数值

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def rebuild(self) -> bool:
        """重建模型（应用参数变更）

        Returns:
            bool: 重建是否成功
        """
        pass

    @abstractmethod
    def export_step(self, output_path: Path) -> bool:
        """导出为STEP格式文件

        Args:
            output_path: 输出文件路径

        Returns:
            bool: 导出是否成功
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[FileFormat]:
        """获取支持的导出格式

        Returns:
            List[FileFormat]: 支持的格式列表
        """
        pass

    def export(self, output_path: Path, format_type: FileFormat) -> bool:
        """导出模型到指定格式（通用实现）

        Args:
            output_path: 输出文件路径
            format_type: 导出格式

        Returns:
            bool: 导出是否成功
        """
        if format_type == FileFormat.STEP:
            return self.export_step(output_path)
        else:
            raise NotImplementedError(f"格式 {format_type} 尚未实现")

    def get_software_info(self) -> Dict[str, Any]:
        """获取软件信息

        Returns:
            Dict[str, Any]: 包含软件名称、版本等信息的字典
        """
        return {
            "connector_type": "CAD",
            "class_name": self.__class__.__name__,
            "supported_formats": [fmt.value for fmt in self.get_supported_formats()],
        }


class CAEConnector(ABC):
    """CAE仿真软件连接器抽象基类

    定义CAE软件必须实现的通用接口，包括网格生成、求解设置、
    仿真运行和结果提取等核心功能。
    """

    @abstractmethod
    def connect(self) -> bool:
        """连接到CAE软件实例

        Returns:
            bool: 连接是否成功
        """
        pass

    @abstractmethod
    def generate_mesh(
        self, geometry_file: Path, mesh_file: Path, element_size: float = 2.0
    ) -> bool:
        """从几何文件生成网格

        Args:
            geometry_file: 输入几何文件路径（STEP/STL等）
            mesh_file: 输出网格文件路径
            element_size: 单元尺寸（默认2.0）

        Returns:
            bool: 网格生成是否成功
        """
        pass

    @abstractmethod
    def setup_simulation(self, mesh_file: Path, config: Dict[str, Any]) -> Path:
        """设置仿真分析

        Args:
            mesh_file: 网格文件路径
            config: 仿真配置字典

        Returns:
            Path: 生成的输入文件路径
        """
        pass

    @abstractmethod
    def run_simulation(
        self, input_file: Path, output_dir: Optional[Path] = None
    ) -> bool:
        """运行仿真分析

        Args:
            input_file: 输入文件路径
            output_dir: 输出目录（可选）

        Returns:
            bool: 仿真是否成功完成
        """
        pass

    @abstractmethod
    def read_results(self, result_file: Path) -> Dict[str, Any]:
        """读取仿真结果

        Args:
            result_file: 结果文件路径

        Returns:
            Dict[str, Any]: 包含结果数据的字典
        """
        pass

    @abstractmethod
    def get_supported_analysis_types(self) -> List[str]:
        """获取支持的分析类型

        Returns:
            List[str]: 支持的分析类型列表（如["static", "modal", "thermal"]）
        """
        pass

    def get_software_info(self) -> Dict[str, Any]:
        """获取软件信息

        Returns:
            Dict[str, Any]: 包含软件名称、版本等信息的字典
        """
        return {
            "connector_type": "CAE",
            "class_name": self.__class__.__name__,
            "supported_analysis": self.get_supported_analysis_types(),
        }
