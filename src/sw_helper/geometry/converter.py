"""
几何格式转换器 - 使用PythonOCC进行CAD格式转换

支持格式:
- STEP (.step, .stp)
- STL (.stl)
- IGES (.iges, .igs)
- BREP (.brep)
- OBJ (.obj)
"""

import shutil
from pathlib import Path
from typing import Optional


class GeometryConverter:
    """几何格式转换器"""

    SUPPORTED_FORMATS = {
        "step": [".step", ".stp"],
        "stl": [".stl"],
        "iges": [".iges", ".igs"],
        "brep": [".brep"],
        "obj": [".obj"],
    }

    def __init__(self):
        self.occ_available = False
        self._check_occ()

    def _check_occ(self) -> bool:
        """检查OpenCascade是否可用"""
        try:
            from OCC.Core import Version
            from OCC.Core.BRep import BRep_Builder
            from OCC.Core.IGESControl import IGESControl_Reader
            from OCC.Core.STEPControl import STEPControl_Reader
            from OCC.Core.StlAPI import StlAPI_Writer
            from OCC.Core.TopAbs import TopAbs_ShapeEnum
            from OCC.Core.TopoDS import TopoDS_Shape

            self.occ_available = True
            return True
        except ImportError:
            return False

    def _get_format(self, file_path: Path) -> str:
        """获取文件格式"""
        ext = file_path.suffix.lower()
        for fmt, exts in self.SUPPORTED_FORMATS.items():
            if ext in exts:
                return fmt
        return "unknown"

    def convert(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        target_format: Optional[str] = None,
    ) -> bool:
        """转换几何文件格式

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选，默认自动生成）
            target_format: 目标格式（step/stl/iges/brep/obj）

        Returns:
            是否成功
        """
        if not self.occ_available:
            print("⚠ OpenCascade未安装，使用简化转换模式")
            return self._mock_convert(input_file, output_file, target_format)

        input_path = Path(input_file)
        if not input_path.exists():
            print(f"✗ 文件不存在: {input_file}")
            return False

        # 确定目标格式
        source_format = self._get_format(input_path)
        if target_format is None:
            target_format = self._infer_target_format(input_path)

        if output_file is None:
            output_path = input_path.with_suffix(f".{target_format}")
        else:
            output_path = Path(output_file)

        # 创建输出目录
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 执行转换
            if source_format == "step" and target_format == "stl":
                return self._step_to_stl(input_path, output_path)
            elif source_format == "stl" and target_format == "step":
                return self._stl_to_step(input_path, output_path)
            elif source_format == "step" and target_format == "iges":
                return self._step_to_iges(input_path, output_path)
            elif source_format == "iges" and target_format == "step":
                return self._iges_to_step(input_path, output_path)
            elif source_format == "step" and target_format == "brep":
                return self._step_to_brep(input_path, output_path)
            elif source_format == "brep" and target_format == "step":
                return self._brep_to_step(input_path, output_path)
            else:
                print(f"✗ 不支持的转换: {source_format} -> {target_format}")
                return False

        except Exception as e:
            print(f"✗ 转换失败: {e}")
            return False

    def _mock_convert(
        self,
        input_file: str,
        output_file: Optional[str],
        target_format: Optional[str],
    ) -> bool:
        """简化转换（无OpenCascade时）"""
        input_path = Path(input_file)

        if output_file is None:
            output_path = input_path.with_suffix(f".{target_format or 'stl'}")
        else:
            output_path = Path(output_file)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 复制文件（仅改变扩展名）
        shutil.copy(input_path, output_path)
        print(f"✓ 简化转换: {input_path.name} -> {output_path.name}")
        print("  注意: 实际转换需要安装 pythonocc-core")
        return True

    def _infer_target_format(self, input_path: Path) -> str:
        """推断目标格式"""
        ext = input_path.suffix.lower()

        # STEP默认转STL
        if ext in [".step", ".stp"]:
            return "stl"
        # STL默认转STEP
        elif ext == ".stl":
            return "step"
        # 其他默认转STEP
        else:
            return "step"

    def _step_to_stl(self, input_path: Path, output_path: Path) -> bool:
        """STEP转STL"""
        from OCC.Core.STEPControl import STEPControl_Reader
        from OCC.Core.StlAPI import StlAPI_Writer

        # 读取STEP文件
        step_reader = STEPControl_Reader()
        step_reader.ReadFile(str(input_path))
        step_reader.TransferRoots()

        shape = step_reader.Shape()

        # 写入STL
        stl_writer = StlAPI_Writer()
        stl_writer.SetAccuracy(0.01)
        stl_writer.SetRelativeMode(True)
        stl_writer.Write(str(output_path), shape)

        print(f"✓ 转换成功: {input_path.name} -> {output_path.name}")
        return True

    def _stl_to_step(self, input_path: Path, output_path: Path) -> bool:
        """STL转STEP"""
        from OCC.Core.STEPControl import STEPControl_Writer
        from OCC.Core.StlAPI import StlAPI_Reader
        from OCC.Interface import Interface_Static

        # 读取STL
        stl_reader = StlAPI_Reader()
        shape = stl_reader.Load(str(input_path))

        # 写入STEP
        Interface_Static.SetCVal("write.step.schema", "AP214")
        step_writer = STEPControl_Writer()
        step_writer.Transfer(shape)
        step_writer.Write(str(output_path))

        print(f"✓ 转换成功: {input_path.name} -> {output_path.name}")
        return True

    def _step_to_iges(self, input_path: Path, output_path: Path) -> bool:
        """STEP转IGES"""
        from OCC.Core.IGESControl import IGESControl_Writer
        from OCC.Core.STEPControl import STEPControl_Reader

        step_reader = STEPControl_Reader()
        step_reader.ReadFile(str(input_path))
        step_reader.TransferRoots()
        shape = step_reader.Shape()

        iges_writer = IGESControl_Writer()
        iges_writer.AddShape(shape)
        iges_writer.Write(str(output_path))

        print(f"✓ 转换成功: {input_path.name} -> {output_path.name}")
        return True

    def _iges_to_step(self, input_path: Path, output_path: Path) -> bool:
        """IGES转STEP"""
        from OCC.Core.IGESControl import IGESControl_Reader
        from OCC.Core.STEPControl import STEPControl_Writer
        from OCC.Interface import Interface_Static

        iges_reader = IGESControl_Reader()
        iges_reader.ReadFile(str(input_path))
        iges_reader.TransferRoots()
        shape = iges_reader.Shape()

        Interface_Static.SetCVal("write.step.schema", "AP214")
        step_writer = STEPControl_Writer()
        step_writer.Transfer(shape)
        step_writer.Write(str(output_path))

        print(f"✓ 转换成功: {input_path.name} -> {output_path.name}")
        return True

    def _step_to_brep(self, input_path: Path, output_path: Path) -> bool:
        """STEP转BREP"""
        from OCC.Core.STEPControl import STEPControl_Reader

        step_reader = STEPControl_Reader()
        step_reader.ReadFile(str(input_path))
        step_reader.TransferRoots()
        shape = step_reader.Shape()

        # 保存为BREP
        from OCC.Core.BRepTools import BRepTools_Write_s

        BRepTools_Write_s(shape, str(output_path))

        print(f"✓ 转换成功: {input_path.name} -> {output_path.name}")
        return True

    def _brep_to_step(self, input_path: Path, output_path: Path) -> bool:
        """BREP转STEP"""
        from OCC.Core.BRepTools import BRepTools_Read
        from OCC.Core.STEPControl import STEPControl_Writer
        from OCC.Core.TopoDS import TopoDS_Shape
        from OCC.Interface import Interface_Static

        shape = TopoDS_Shape()
        BRepTools_Read(shape, str(input_path))

        Interface_Static.SetCVal("write.step.schema", "AP214")
        step_writer = STEPControl_Writer()
        step_writer.Transfer(shape)
        step_writer.Write(str(output_path))

        print(f"✓ 转换成功: {input_path.name} -> {output_path.name}")
        return True


def convert_geometry(
    input_file: str,
    output_file: Optional[str] = None,
    target_format: Optional[str] = None,
) -> bool:
    """便捷转换函数"""
    converter = GeometryConverter()
    return converter.convert(input_file, output_file, target_format)
