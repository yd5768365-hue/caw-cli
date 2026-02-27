"""
CAE 求解器抽象基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class SolverResult:
    """求解结果数据结构"""

    max_displacement: float  # 最大位移 (m)
    max_stress: float  # 最大应力 (Pa)
    safety_factor: float  # 安全系数
    displacement: Optional[Dict[str, float]] = None  # 节点位移
    stress: Optional[Dict[str, float]] = None  # 应力分布
    messages: str = ""  # 附加信息


@dataclass
class SolverConfig:
    """求解器配置"""

    analysis_type: str = "static"  # static/modal/thermal/buckling
    material: Dict[str, Any] = None  # 材料参数
    load: float = 0  # 载荷 (N)
    mesh_size: float = 10.0  # 网格大小 (mm)
    boundary_conditions: Dict[str, Any] = None  # 边界条件
    geometry: Dict[str, Any] = None  # 几何参数


class BaseSolver(ABC):
    """CAE 求解器抽象基类"""

    name: str = "base"
    description: str = "基础求解器"
    requires_install: str = None  # 依赖安装命令

    @abstractmethod
    def solve(self, config: SolverConfig) -> SolverResult:
        """执行求解

        Args:
            config: 求解器配置

        Returns:
            求解结果
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查求解器是否可用

        Returns:
            是否可用
        """
        pass

    def get_info(self) -> Dict[str, str]:
        """获取求解器信息"""
        return {
            "name": self.name,
            "description": self.description,
            "requires_install": self.requires_install or "内置",
        }
