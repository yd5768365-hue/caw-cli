"""
CAD连接器模块 - 各种CAD软件的标准化接口
"""

try:
    from .freecad import FreeCADConnector

    __all__ = ["FreeCADConnector"]
except ImportError:
    __all__ = []
