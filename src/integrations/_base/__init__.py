"""
integrations._base - 基础连接器模块

提供CAD/CAE软件集成的抽象基类和通用接口
"""

from .connectors import CADConnector, CAEConnector, FileFormat
from .workflow import WorkflowEngine, WorkflowStep, WorkflowStatus

__all__ = [
    "CADConnector",
    "CAEConnector", 
    "FileFormat",
    "WorkflowEngine",
    "WorkflowStep",
    "WorkflowStatus",
]
