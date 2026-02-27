"""
软件集成模块
"""

from .cad_connector import CADManager, FreeCADConnector, Parameter, SolidWorksConnector
from .sw_macro import SolidWorksMacroGenerator

__all__ = [
    "SolidWorksConnector",
    "FreeCADConnector",
    "CADManager",
    "Parameter",
    "SolidWorksMacroGenerator",
]
