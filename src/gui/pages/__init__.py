"""
CAE-CLI 页面模块

此模块包含各个功能页面的基类和具体实现。
"""

# 导入所有页面
from .ai_page import AIPage
from .chat_page import ChatPage
from .geometry_page import GeometryPage
from .home_page import HomePage, create_home_page
from .material_page import MaterialPage
from .mesh_page import MeshPage
from .optimization_page import OptimizationPage
from .welcome_page import WelcomePage, create_welcome_page

__all__ = [
    "GeometryPage",
    "MeshPage",
    "MaterialPage",
    "OptimizationPage",
    "AIPage",
    "ChatPage",
    "HomePage",
    "create_home_page",
    "WelcomePage",
    "create_welcome_page",
]
