"""
CAE-CLI 页面模块

此模块包含各个功能页面的基类和具体实现。
"""

# 导入所有页面
from .geometry_page import GeometryPage
from .mesh_page import MeshPage
from .material_page import MaterialPage
from .optimization_page import OptimizationPage
from .ai_page import AIPage
from .chat_page import ChatPage

__all__ = [
    "GeometryPage",
    "MeshPage",
    "MaterialPage",
    "OptimizationPage",
    "AIPage",
    "ChatPage",
]
