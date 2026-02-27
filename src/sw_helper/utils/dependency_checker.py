#!/usr/bin/env python3
"""
依赖检查和降级方案 - 确保核心功能可用

此模块提供依赖检查功能：
- 启动时检查核心依赖
- 友好错误提示和安装命令
- 功能降级支持
- 依赖状态报告
"""

from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table


class Dependency:
    """依赖项信息"""

    def __init__(
        self,
        name: str,
        module_name: str,
        min_version: str = "",
        install_command: str = "",
        fallback: Optional[str] = None,
    ):
        self.name = name
        self.module_name = module_name
        self.min_version = min_version
        self.install_command = install_command
        self.fallback = fallback

    def __repr__(self):
        return f"Dependency(name={self.name}, module={self.module_name})"


# 核心依赖定义
CORE_DEPENDENCIES = [
    Dependency(
        name="Click",
        module_name="click",
        min_version="8.0.0",
        install_command="pip install click",
    ),
    Dependency(
        name="Rich",
        module_name="rich",
        min_version="13.0.0",
        install_command="pip install rich",
    ),
    Dependency(
        name="Pint",
        module_name="pint",
        min_version="0.22",
        install_command="pip install pint",
    ),
    Dependency(
        name="PyYAML",
        module_name="yaml",
        min_version="6.0",
        install_command="pip install pyyaml",
    ),
    Dependency(
        name="NumPy",
        module_name="numpy",
        min_version="1.21.0",
        install_command="pip install numpy",
    ),
    Dependency(
        name="MeshIO",
        module_name="meshio",
        min_version="5.0.0",
        install_command="pip install meshio",
        fallback="trimesh",
    ),
    Dependency(
        name="Trimesh",
        module_name="trimesh",
        min_version="3.9.0",
        install_command="pip install trimesh",
    ),
    Dependency(
        name="Gmsh",
        module_name="gmsh",
        min_version="4.10.0",
        install_command="pip install gmsh",
    ),
]


class DependencyChecker:
    """依赖检查器"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.dependency_status: Dict[Dependency, Dict] = {}

    def _check_single_dependency(self, dependency: Dependency) -> Dict:
        """检查单个依赖项

        Returns:
            Dict: 包含状态、版本、错误信息的字典
        """
        status = {
            "is_installed": False,
            "version": None,
            "error": None,
        }

        try:
            module = __import__(dependency.module_name)
            status["is_installed"] = True

            # 尝试获取版本 - 使用 importlib.metadata 避免弃用警告
            try:
                from importlib.metadata import version

                status["version"] = version(dependency.module_name)
            except (ImportError, Exception):
                # 回退到属性检查
                if hasattr(module, "__version__"):
                    status["version"] = module.__version__
                elif hasattr(module, "__VERSION__"):
                    status["version"] = module.__VERSION__
                else:
                    status["version"] = "Unknown"

        except ImportError as e:
            status["error"] = str(e)
        except Exception as e:
            status["error"] = f"导入模块时出错: {e}"

        return status

    def check_all_dependencies(self) -> Dict[Dependency, Dict]:
        """检查所有核心依赖项

        Returns:
            Dict: 依赖项状态字典
        """
        self.console.print("正在检查核心依赖项...", style="blue")

        for dep in CORE_DEPENDENCIES:
            self.console.print(f"检查 {dep.name}...", style="dim")
            status = self._check_single_dependency(dep)
            self.dependency_status[dep] = status

        return self.dependency_status

    def get_status_report(self) -> str:
        """获取依赖状态报告"""
        table = Table(title="依赖状态报告", show_header=True, header_style="bold")
        table.add_column("依赖名称", style="cyan")
        table.add_column("模块名称", style="magenta")
        table.add_column("状态", style="green")
        table.add_column("版本", style="blue")
        table.add_column("错误信息", style="red")

        for dep, status in self.dependency_status.items():
            if status["is_installed"]:
                status_text = "[OK]"
                version_text = status["version"] or "Unknown"
                error_text = ""
            else:
                status_text = "[ERROR]"
                version_text = ""
                error_text = status["error"] or ""

            table.add_row(dep.name, dep.module_name, status_text, version_text, error_text)

        return table

    def get_missing_dependencies(self) -> List[Dependency]:
        """获取缺失的依赖项

        Returns:
            List[Dependency]: 缺失的依赖项列表
        """
        missing = []
        for dep, status in self.dependency_status.items():
            if not status["is_installed"]:
                missing.append(dep)
        return missing

    def get_install_commands(self) -> List[str]:
        """获取安装命令

        Returns:
            List[str]: pip 安装命令列表
        """
        commands = []
        for dep, status in self.dependency_status.items():
            if not status["is_installed"]:
                commands.append(dep.install_command)
        return commands

    def get_fallback_options(self) -> Dict[str, str]:
        """获取功能降级选项

        Returns:
            Dict: 功能降级选项字典
        """
        fallback_options = {}
        for dep, status in self.dependency_status.items():
            if not status["is_installed"] and dep.fallback:
                fallback_status = self._check_single_dependency(
                    Dependency(name=f"{dep.fallback}", module_name=dep.fallback)
                )
                if fallback_status["is_installed"]:
                    fallback_options[dep.module_name] = dep.fallback

        return fallback_options

    def print_report(self) -> None:
        """打印依赖状态报告"""
        report = self.get_status_report()
        self.console.print(report)

        # 打印安装命令
        missing_deps = self.get_missing_dependencies()
        if missing_deps:
            self.console.print("\n缺失的依赖项安装命令:", style="bold")
            for dep in missing_deps:
                self.console.print(f"  {dep.install_command}", style="yellow")

        # 打印完整安装命令
        full_command = "pip install click rich pint pyyaml numpy meshio trimesh gmsh"
        self.console.print(f"\n完整安装命令:\n  {full_command}", style="cyan")

        # 打印功能降级信息
        fallback_options = self.get_fallback_options()
        if fallback_options:
            self.console.print("\n功能降级选项:", style="bold")
            for module, fallback in fallback_options.items():
                self.console.print(f"  {module} → {fallback}", style="green")


def create_dependency_checker(console: Optional[Console] = None) -> DependencyChecker:
    """创建依赖检查器实例

    Args:
        console: Rich Console 实例

    Returns:
        DependencyChecker: 依赖检查器实例
    """
    return DependencyChecker(console)


def main() -> None:
    """测试依赖检查器"""
    console = Console()
    checker = create_dependency_checker(console)
    checker.check_all_dependencies()
    checker.print_report()


if __name__ == "__main__":
    main()
