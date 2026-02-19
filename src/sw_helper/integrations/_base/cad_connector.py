"""
CAD连接器抽象基类 - 定义CAD软件集成的统一接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class Parameter:
    """参数数据类"""

    name: str
    value: float
    unit: str = "mm"
    description: str = ""
    modifiable: bool = True


class CADConnector(ABC):
    """CAD软件连接器抽象基类"""

    def __init__(self):
        self.is_connected = False
        self.active_document = None

    @abstractmethod
    def connect(self) -> bool:
        """连接到CAD软件

        Returns:
            bool: 连接是否成功
        """
        pass

    @abstractmethod
    def open_document(self, file_path: str) -> bool:
        """打开文档

        Args:
            file_path: 文件路径

        Returns:
            bool: 打开是否成功
        """
        pass

    @abstractmethod
    def get_parameters(self) -> List[Parameter]:
        """获取文档中的所有参数

        Returns:
            List[Parameter]: 参数列表
        """
        pass

    @abstractmethod
    def set_parameter(self, name: str, value: float) -> bool:
        """设置参数值

        Args:
            name: 参数名
            value: 参数值

        Returns:
            bool: 设置是否成功
        """
        pass

    @abstractmethod
    def rebuild(self) -> bool:
        """重建模型

        Returns:
            bool: 重建是否成功
        """
        pass

    @abstractmethod
    def export(self, output_path: str, format_type: str = "STEP") -> bool:
        """导出模型文件

        Args:
            output_path: 输出路径
            format_type: 格式类型 (STEP, STL, IGES等)

        Returns:
            bool: 导出是否成功
        """
        pass

    def close_document(self, save: bool = False):
        """关闭文档

        Args:
            save: 是否保存
        """
        pass

    def disconnect(self):
        """断开连接"""
        self.is_connected = False
        self.active_document = None

    def get_supported_formats(self) -> List[str]:
        """获取支持的导出格式

        Returns:
            List[str]: 格式列表
        """
        return ["STEP", "STL", "IGES", "BREP"]

    def get_software_info(self) -> Dict[str, Any]:
        """获取软件信息

        Returns:
            Dict[str, Any]: 软件信息字典
        """
        return {
            "name": self.__class__.__name__.replace("Connector", ""),
            "type": "CAD",
            "version": "unknown",
        }
