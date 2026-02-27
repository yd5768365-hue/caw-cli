"""
集成基础模块 - 定义CAD/CAE软件集成的基础接口和抽象类

注意：此模块已弃用，请使用 src/integrations/ 中的新架构
"""

from .cad_connector import CADConnector, Parameter
from .cae_connector import AnalysisResult, CAEConnector

__all__ = [
    "CADConnector",
    "Parameter",
    "CAEConnector",
    "AnalysisResult",
]
