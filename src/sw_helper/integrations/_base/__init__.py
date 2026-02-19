"""
集成基础模块 - 定义CAD/CAE软件集成的基础接口和抽象类
"""

from .cad_connector import CADConnector, Parameter
from .cae_connector import CAEConnector, AnalysisResult
from .workflow_engine import Workflow, WorkflowStep, WorkflowEngine

__all__ = [
    "CADConnector",
    "Parameter",
    "CAEConnector",
    "AnalysisResult",
    "Workflow",
    "WorkflowStep",
    "WorkflowEngine",
]
