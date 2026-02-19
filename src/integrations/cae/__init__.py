"""
CAE连接器模块 - 各种CAE软件的标准化接口
"""

try:
    from .calculix import CalculiXConnector, CalculiXConnectorMock

    __all__ = ["CalculiXConnector", "CalculiXConnectorMock"]
except ImportError:
    __all__ = []
