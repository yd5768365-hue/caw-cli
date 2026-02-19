"""
网格生成器模块 - 集成Gmsh等网格生成工具

此模块提供网格生成器的标准化接口，支持从几何文件生成
有限元分析所需的网格，并确保网格质量满足仿真要求。
"""

from .gmsh import GmshConnector, GmshConnectorMock

__all__ = ["GmshConnector", "GmshConnectorMock"]
