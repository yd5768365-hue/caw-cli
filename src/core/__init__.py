"""
CAE-CLI 核心模块

此模块包含项目的核心数据类型定义和自定义异常。
"""

# 导入数据类型
# 导入异常
from .exceptions import (
    AIError,
    CADConnectionError,
    CADOperationError,
    CAEAnalysisError,
    CAEError,
    ConfigError,
    ConfigValidationError,
    FileFormatError,
    FileNotFoundError,
    FileParseError,
    GUIError,
    MaterialNotFoundError,
    MaterialPropertyError,
    MeshGenerationError,
    ModelNotFoundError,
    OllamaConnectionError,
    RAGError,
    SimulationConvergenceError,
    SimulationError,
    SimulationTimeoutError,
    WorkerError,
    format_error,
    get_error_details,
)
from .types import (
    BoundaryCondition,
    FileFormat,
    LoadCondition,
    MaterialProperty,
    SimulationConfig,
    SimulationResult,
    create_default_config,
)

__all__ = [
    # 类型
    "FileFormat",
    "MaterialProperty",
    "LoadCondition",
    "BoundaryCondition",
    "SimulationConfig",
    "SimulationResult",
    "create_default_config",
    # 异常
    "CAEError",
    "FileNotFoundError",
    "FileFormatError",
    "FileParseError",
    "CADConnectionError",
    "CADOperationError",
    "CAEAnalysisError",
    "MeshGenerationError",
    "MaterialNotFoundError",
    "MaterialPropertyError",
    "ConfigError",
    "ConfigValidationError",
    "SimulationError",
    "SimulationTimeoutError",
    "SimulationConvergenceError",
    "AIError",
    "OllamaConnectionError",
    "ModelNotFoundError",
    "RAGError",
    "GUIError",
    "WorkerError",
    # 工具函数
    "format_error",
    "get_error_details",
]
