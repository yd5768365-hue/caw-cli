"""
验证工具模块
"""

from pathlib import Path
from typing import Union


class FileValidator:
    """文件验证器"""

    SUPPORTED_GEOMETRY = [".step", ".stp", ".stl", ".iges", ".igs"]
    SUPPORTED_MESH = [".msh", ".inp", ".bdf", ".cdb", ".unv"]

    @classmethod
    def validate_geometry_file(cls, file_path: Union[str, Path]) -> bool:
        """验证几何文件"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if path.suffix.lower() not in cls.SUPPORTED_GEOMETRY:
            raise ValueError(
                f"不支持的几何文件格式: {path.suffix}. " f"支持的格式: {', '.join(cls.SUPPORTED_GEOMETRY)}"
            )

        return True

    @classmethod
    def validate_mesh_file(cls, file_path: Union[str, Path]) -> bool:
        """验证网格文件"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if path.suffix.lower() not in cls.SUPPORTED_MESH:
            raise ValueError(f"不支持的网格文件格式: {path.suffix}. " f"支持的格式: {', '.join(cls.SUPPORTED_MESH)}")

        return True

    @classmethod
    def validate_file_size(cls, file_path: Union[str, Path], max_size_mb: float = 100) -> bool:
        """验证文件大小"""
        path = Path(file_path)
        size_mb = path.stat().st_size / (1024 * 1024)

        if size_mb > max_size_mb:
            raise ValueError(f"文件过大: {size_mb:.2f}MB. 最大允许: {max_size_mb}MB")

        return True


class InputValidator:
    """输入验证器"""

    @staticmethod
    def validate_material_name(name: str) -> bool:
        """验证材料名称"""
        if not name or not isinstance(name, str):
            raise ValueError("材料名称不能为空")

        if len(name) > 100:
            raise ValueError("材料名称过长")

        return True

    @staticmethod
    def validate_positive_number(value: float, name: str = "值") -> bool:
        """验证正数"""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name}必须是数字")

        if value <= 0:
            raise ValueError(f"{name}必须大于0")

        return True

    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float, name: str = "值") -> bool:
        """验证数值范围"""
        if not min_val <= value <= max_val:
            raise ValueError(f"{name}必须在 {min_val} 和 {max_val} 之间")

        return True
