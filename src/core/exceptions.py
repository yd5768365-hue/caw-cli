"""
CAE-CLI 核心异常定义

此模块定义项目中使用的自定义异常类型，
便于错误处理和调试。
"""


class CAEError(Exception):
    """CAE-CLI 基础异常类"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# ==================== 文件相关异常 ====================


class FileNotFoundError(CAEError):
    """文件未找到异常"""

    pass


class FileFormatError(CAEError):
    """文件格式错误异常"""

    pass


class FileParseError(CAEError):
    """文件解析错误异常"""

    pass


# ==================== CAD/CAE 相关异常 ====================


class CADConnectionError(CAEError):
    """CAD软件连接异常"""

    pass


class CADOperationError(CAEError):
    """CAD操作异常"""

    pass


class CAEAnalysisError(CAEError):
    """CAE分析异常"""

    pass


class MeshGenerationError(CAEError):
    """网格生成异常"""

    pass


# ==================== 材料相关异常 ====================


class MaterialNotFoundError(CAEError):
    """材料未找到异常"""

    pass


class MaterialPropertyError(CAEError):
    """材料属性错误异常"""

    pass


# ==================== 配置相关异常 ====================


class ConfigError(CAEError):
    """配置错误异常"""

    pass


class ConfigValidationError(ConfigError):
    """配置验证失败异常"""

    pass


# ==================== 仿真相关异常 ====================


class SimulationError(CAEError):
    """仿真基础异常"""

    pass


class SimulationTimeoutError(SimulationError):
    """仿真超时异常"""

    pass


class SimulationConvergenceError(SimulationError):
    """仿真不收敛异常"""

    pass


# ==================== AI 相关异常 ====================


class AIError(CAEError):
    """AI模块基础异常"""

    pass


class OllamaConnectionError(AIError):
    """Ollama服务连接异常"""

    pass


class ModelNotFoundError(AIError):
    """AI模型未找到异常"""

    pass


class RAGError(AIError):
    """RAG知识检索异常"""

    pass


# ==================== GUI 相关异常 ====================


class GUIError(CAEError):
    """GUI基础异常"""

    pass


class WorkerError(GUIError):
    """工作线程异常"""

    pass


# ==================== 工具函数 ====================


def format_error(error: Exception) -> str:
    """格式化异常信息

    Args:
        error: 异常对象

    Returns:
        str: 格式化的错误信息
    """
    if isinstance(error, CAEError):
        return str(error)

    # 对于非CAEError异常，返回异常类型和消息
    return f"{type(error).__name__}: {str(error)}"


def get_error_details(error: Exception) -> dict:
    """获取异常的详细信息

    Args:
        error: 异常对象

    Returns:
        dict: 异常详细信息
    """
    if isinstance(error, CAEError):
        return {
            "message": error.message,
            "type": type(error).__name__,
            "details": error.details,
        }

    return {
        "message": str(error),
        "type": type(error).__name__,
        "details": {},
    }
