"""
sw_helper.integrations - CAD/CAE集成模块

此模块提供CAD软件的统一管理和连接功能
"""

from .cad_connector import CADManager, SolidWorksConnector
from .sw_macro import SolidWorksMacroGenerator

__all__ = ["CADManager", "SolidWorksConnector", "SolidWorksMacroGenerator"]
