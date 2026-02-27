"""
CAE 求解器模块 - 标准化求解器接口

提供多种求解器实现：
- SimpleFEMSolver: 内置简易求解器（无需额外安装）
- SciPySolver: 基于 SciPy 的求解器
- CalculiXSolver: CalculiX 求解器（未来预留）
"""

from .base import BaseSolver, SolverConfig, SolverResult
from .calculix_solver import CalculiXSolver
from .scipy_solver import SciPySolver
from .simple_fem import SimpleFEMSolver

__all__ = [
    "BaseSolver",
    "SolverResult",
    "SolverConfig",
    "SimpleFEMSolver",
    "SciPySolver",
    "CalculiXSolver",
    "get_solver",
]


def get_solver(solver_name: str = "simple") -> BaseSolver:
    """获取求解器实例

    Args:
        solver_name: 求解器名称 (simple/scipy/calculix)

    Returns:
        求解器实例
    """
    solvers = {
        "simple": SimpleFEMSolver,
        "scipy": SciPySolver,
        "calculix": CalculiXSolver,
    }

    solver_class = solvers.get(solver_name.lower())

    if solver_class is None:
        raise ValueError(f"未知求解器: {solver_name}，可用: {list(solvers.keys())}")

    return solver_class()
