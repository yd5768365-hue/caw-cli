"""
CAE-CLI 源代码包

此包包含应用程序的所有源代码模块。
"""

# 版本信息
__version__ = "0.1.0"

# 导入核心模块
from .core import (
    CAEError,
    SimulationConfig,
    FileFormat,
)

# 导入GUI模块
from .gui import (
    MainWindow,
    CAETheme,
)

__all__ = [
    "__version__",
    # 核心模块
    "CAEError",
    "SimulationConfig",
    "FileFormat",
    # GUI模块
    "MainWindow",
    "CAETheme",
]
