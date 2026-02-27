"""
CAE连接器抽象基类 - 定义CAE仿真软件集成的统一接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class AnalysisType(Enum):
    """分析类型枚举"""

    STATIC = "static"  # 静力分析
    MODAL = "modal"  # 模态分析
    THERMAL = "thermal"  # 热分析
    BUCKLING = "buckling"  # 屈曲分析
    CFD = "cfd"  # 流体分析
    MULTIPHYSICS = "multiphysics"  # 多物理场


@dataclass
class AnalysisResult:
    """分析结果数据类"""

    name: str
    value: float
    unit: str = ""
    location: Optional[List[float]] = None  # 结果位置坐标 [x, y, z]
    component: Optional[str] = None  # 结果分量 (e.g., "XX", "XY", "von Mises")
    step: int = 0  # 分析步
    iteration: int = 0  # 迭代步


class CAEConnector(ABC):
    """CAE仿真软件连接器抽象基类"""

    def __init__(self):
        self.is_connected = False
        self.active_job = None

    @abstractmethod
    def connect(self) -> bool:
        """连接到CAE软件

        Returns:
            bool: 连接是否成功
        """
        pass

    @abstractmethod
    def setup_analysis(self, config: Dict[str, Any]) -> bool:
        """设置分析配置

        Args:
            config: 分析配置字典

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def submit_job(self, input_file: Optional[str] = None) -> bool:
        """提交分析作业

        Args:
            input_file: 输入文件路径（可选）

        Returns:
            bool: 提交是否成功
        """
        pass

    @abstractmethod
    def get_results(self, result_file: Optional[str] = None) -> List[AnalysisResult]:
        """获取分析结果

        Args:
            result_file: 结果文件路径（可选）

        Returns:
            List[AnalysisResult]: 结果列表
        """
        pass

    @abstractmethod
    def generate_input(self, mesh_file: str, config: Dict[str, Any]) -> str:
        """生成输入文件

        Args:
            mesh_file: 网格文件路径
            config: 分析配置

        Returns:
            str: 生成的输入文件路径
        """
        pass

    def wait_for_completion(self, timeout: float = 3600.0) -> bool:
        """等待作业完成

        Args:
            timeout: 超时时间（秒）

        Returns:
            bool: 是否成功完成
        """
        # 默认实现：立即返回成功（用于命令行求解器）
        return True

    def cancel_job(self) -> bool:
        """取消当前作业

        Returns:
            bool: 取消是否成功
        """
        return False

    def disconnect(self):
        """断开连接"""
        self.is_connected = False
        self.active_job = None

    def get_supported_analysis_types(self) -> List[AnalysisType]:
        """获取支持的分析类型

        Returns:
            List[AnalysisType]: 分析类型列表
        """
        return [AnalysisType.STATIC]

    def get_software_info(self) -> Dict[str, Any]:
        """获取软件信息

        Returns:
            Dict[str, Any]: 软件信息字典
        """
        return {
            "name": self.__class__.__name__.replace("Connector", ""),
            "type": "CAE",
            "version": "unknown",
            "supported_analysis": [at.value for at in self.get_supported_analysis_types()],
        }
