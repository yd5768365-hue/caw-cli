"""
CAD/CAE集成模块 - 插件化架构

此包提供CAD和CAE软件的标准化接口，支持插件化扩展。
"""

from ._base.connectors import CADConnector, CAEConnector, FileFormat
from ._base.workflow import WorkflowEngine

__all__ = ["CADConnector", "CAEConnector", "FileFormat", "WorkflowEngine"]

# 导出CAD连接器
try:
    from .cad.freecad import FreeCADConnector

    __all__.append("FreeCADConnector")
except ImportError:
    pass  # 如果FreeCAD不可用，不导出

# 导出CAE连接器
try:
    from .cae.calculix import CalculiXConnector, CalculiXConnectorMock

    __all__.extend(["CalculiXConnector", "CalculiXConnectorMock"])
except ImportError:
    pass  # 如果CalculiX不可用，不导出
