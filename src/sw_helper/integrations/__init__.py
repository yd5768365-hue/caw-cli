"""
软件集成模块
"""

from .cad_connector import SolidWorksConnector, FreeCADConnector, CADManager, Parameter
from .sw_macro import SolidWorksMacroGenerator

__all__ = [
    "SolidWorksConnector",
    "FreeCADConnector",
    "CADManager",
    "Parameter",
    "SolidWorksMacroGenerator",
]
