"""
FreeCAD连接器 - 新架构实现

基于CADConnector抽象基类的FreeCAD连接器实现，
提供与FreeCAD Python API的标准化交互接口。
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .._base.connectors import CADConnector, FileFormat


@dataclass
class FCParameter:
    """FreeCAD参数数据类（保持与旧代码兼容）"""

    name: str
    value: float
    unit: str = "mm"
    obj_name: str = ""  # FreeCAD中的对象名称
    constraint_index: int = -1  # 如果是约束，记录索引


class FreeCADConnector(CADConnector):
    """FreeCAD连接器 - 基于新架构的实现"""

    def __init__(self):
        self.fc_app = None
        self.part_module = None
        self.active_doc = None
        self.is_connected = False

    def connect(self) -> bool:
        """连接到FreeCAD实例"""
        try:
            # 尝试导入FreeCAD
            import FreeCAD as App
            import Part

            self.fc_app = App
            self.part_module = Part
            self.is_connected = True
            return True

        except ImportError:
            # 如果直接导入失败，尝试添加FreeCAD路径
            print("尝试添加FreeCAD路径...")

            # 常见的FreeCAD安装路径
            possible_paths = [
                "C:/Program Files/FreeCAD 0.21/bin",
                "C:/Program Files/FreeCAD 0.20/bin",
                "C:/Program Files/FreeCAD/bin",
                "/usr/lib/freecad-python3/lib",
                "/usr/lib/freecad/lib",
                "/Applications/FreeCAD.app/Contents/lib",
            ]

            fc_found = False
            for path in possible_paths:
                if Path(path).exists():
                    sys.path.append(path)
                    try:
                        import FreeCAD as App
                        import Part

                        self.fc_app = App
                        self.part_module = Part
                        self.is_connected = True
                        fc_found = True
                        print(f"✓ 从 {path} 加载FreeCAD成功")
                        break
                    except ImportError:
                        continue

            if not fc_found:
                print("✗ 未能找到FreeCAD，请确保已安装并配置Python路径")
                print("提示: 可以设置 FREECAD_LIB 环境变量指向FreeCAD的lib目录")
                return False

            return True

        except Exception as e:
            print(f"连接FreeCAD失败: {e}")
            return False

    def load_model(self, file_path: Path) -> bool:
        """加载CAD模型文件"""
        if not self.is_connected:
            if not self.connect():
                return False

        try:
            file_path = str(file_path.resolve())

            # 关闭当前文档（如果有）
            if self.active_doc:
                self.close_document()

            # 打开文档
            self.active_doc = self.fc_app.open(file_path)

            if self.active_doc:
                print(f"✓ 已打开: {self.active_doc.Name}")
                return True
            else:
                print("✗ 无法打开文档")
                return False

        except Exception as e:
            print(f"打开文档失败: {e}")
            return False

    def get_parameter(self, name: str) -> Optional[float]:
        """获取指定参数的值"""
        if not self.active_doc:
            return None

        # 使用现有方法查找参数
        param = self._find_parameter_internal(name)
        return param.value if param else None

    def set_parameter(self, name: str, value: float) -> bool:
        """设置参数值"""
        if not self.active_doc:
            print("✗ 没有打开的文档")
            return False

        try:
            # 使用现有的参数设置逻辑
            return self._set_parameter_internal(name, value)
        except Exception as e:
            print(f"设置参数失败: {e}")
            return False

    def rebuild(self) -> bool:
        """重建模型（应用参数变更）"""
        if not self.active_doc:
            print("✗ 没有打开的文档")
            return False

        try:
            print("⏳ 重新计算文档...")
            self.active_doc.recompute()
            self.fc_app.ActiveDocument = self.active_doc
            print("✓ 重建完成")
            return True
        except Exception as e:
            print(f"重建失败: {e}")
            return False

    def export_step(self, output_path: Path) -> bool:
        """导出为STEP格式文件"""
        return self._export_file_internal(output_path, "STEP")

    def get_supported_formats(self) -> List[FileFormat]:
        """获取支持的导出格式"""
        return [
            FileFormat.STEP,
            FileFormat.STL,
            FileFormat.IGES,
            FileFormat.BREP,
            FileFormat.FCSTD,
        ]

    # ========== 内部辅助方法（保持与旧代码兼容）==========

    def _get_parameters_internal(self) -> List[FCParameter]:
        """获取所有参数（内部实现，保持与旧代码兼容）"""
        if not self.active_doc:
            return []

        params = []

        try:
            # 遍历所有对象
            for obj in self.active_doc.Objects:
                # 检查Sketcher对象（草图约束）
                if obj.isDerivedFrom("Sketcher::SketchObject"):
                    if hasattr(obj, "Constraints"):
                        for i, constraint in enumerate(obj.Constraints):
                            if hasattr(constraint, "Value"):
                                params.append(
                                    FCParameter(
                                        name=constraint.Name
                                        if hasattr(constraint, "Name")
                                        and constraint.Name
                                        else f"Constraint_{i}",
                                        value=constraint.Value,
                                        unit="mm",
                                        obj_name=obj.Name,
                                        constraint_index=i,
                                    )
                                )

                # 检查PartDesign特征（如Pad、Pocket等）
                if obj.isDerivedFrom("PartDesign::Feature"):
                    # 检查常见参数
                    param_names = [
                        "Length",
                        "Width",
                        "Height",
                        "Radius",
                        "FilletRadius",
                        "Thickness",
                    ]
                    for param_name in param_names:
                        if hasattr(obj, param_name):
                            value = getattr(obj, param_name)
                            if isinstance(value, (int, float)):
                                params.append(
                                    FCParameter(
                                        name=f"{obj.Name}.{param_name}",
                                        value=float(value),
                                        unit="mm",
                                        obj_name=obj.Name,
                                    )
                                )

                # 检查Fillet（圆角）
                if obj.isDerivedFrom("PartDesign::Fillet"):
                    if hasattr(obj, "Radius"):
                        params.append(
                            FCParameter(
                                name=f"{obj.Name}.Radius",
                                value=float(obj.Radius),
                                unit="mm",
                                obj_name=obj.Name,
                            )
                        )

                # 检查Spreadsheet（电子表格中的参数）
                if obj.isDerivedFrom("Spreadsheet::Sheet"):
                    # 获取电子表格中的单元格
                    for cell in ["A1", "A2", "A3", "B1", "B2", "B3"]:
                        try:
                            value = obj.get(cell)
                            if isinstance(value, (int, float)):
                                params.append(
                                    FCParameter(
                                        name=f"Spreadsheet.{cell}",
                                        value=float(value),
                                        unit="mm",
                                        obj_name=obj.Name,
                                    )
                                )
                        except:
                            pass

        except Exception as e:
            print(f"获取参数失败: {e}")

        return params

    def _find_parameter_internal(self, param_name: str) -> Optional[FCParameter]:
        """查找特定参数（内部实现）"""
        params = self._get_parameters_internal()

        # 精确匹配
        for p in params:
            if p.name == param_name:
                return p

        # 模糊匹配（部分匹配）
        param_lower = param_name.lower()
        for p in params:
            if param_lower in p.name.lower():
                return p

        return None

    def _set_parameter_internal(self, param_name: str, value: float) -> bool:
        """设置参数值（内部实现，保持与旧代码兼容）"""
        try:
            # 支持的参数映射（标准化参数名称）
            param_mapping = {
                "fillet_radius": ["FilletRadius", "Radius"],
                "length": ["Length"],
                "width": ["Width"],
                "height": ["Height"],
                "hole_diameter": ["Diameter"],
                "thickness": ["Thickness"],
                "radius": ["Radius"],
                "diameter": ["Diameter"],
            }

            # 查找参数
            param = self._find_parameter_internal(param_name)

            if param:
                obj = self.active_doc.getObject(param.obj_name)

                if obj:
                    # 如果是草图约束
                    if param.constraint_index >= 0 and hasattr(obj, "Constraints"):
                        obj.setDatum(param.constraint_index, value)
                        print(f"✓ 设置约束 {param.name} = {value} mm")
                        return True

                    # 如果是对象属性（如 Fillet.Radius）
                    if "." in param.name:
                        prop_name = param.name.split(".")[-1]
                        if hasattr(obj, prop_name):
                            setattr(obj, prop_name, value)
                            print(f"✓ 设置 {param.name} = {value} mm")
                            return True

                    # 直接设置属性
                    for attr in ["Length", "Width", "Height", "Radius", "Thickness"]:
                        if hasattr(obj, attr):
                            setattr(obj, attr, value)
                            print(f"✓ 设置 {obj.Name}.{attr} = {value} mm")
                            return True

            # 尝试通过对象名称直接查找
            if "." in param_name:
                parts = param_name.split(".")
                if len(parts) == 2:
                    obj_name, prop_name = parts
                    obj = self.active_doc.getObject(obj_name)
                    if obj and hasattr(obj, prop_name):
                        setattr(obj, prop_name, value)
                        print(f"✓ 设置 {param_name} = {value} mm")
                        return True

            # 尝试全局搜索所有对象（支持常见参数类型）
            target_param_lower = param_name.lower()

            for obj in self.active_doc.Objects:
                # 支持的属性类型
                for attr in [
                    "Radius",
                    "Length",
                    "Width",
                    "Height",
                    "FilletRadius",
                    "Thickness",
                    "Diameter",
                ]:
                    if hasattr(obj, attr):
                        # 检查属性名称是否匹配
                        attr_lower = attr.lower()

                        # 精确匹配或包含匹配
                        if (
                            attr_lower == target_param_lower
                            or target_param_lower in attr_lower
                        ):
                            setattr(obj, attr, value)
                            print(f"✓ 设置 {obj.Name}.{attr} = {value} mm")
                            return True

                        # 检查参数名称是否在属性值中（如 Hole_Diameter 匹配 Diameter）
                        for key, values in param_mapping.items():
                            if key in target_param_lower:
                                for possible_attr in values:
                                    if hasattr(obj, possible_attr):
                                        setattr(obj, possible_attr, value)
                                        print(
                                            f"✓ 设置 {obj.Name}.{possible_attr} = {value} mm"
                                        )
                                        return True

            # 尝试在电子表格中查找
            for obj in self.active_doc.Objects:
                if obj.isDerivedFrom("Spreadsheet::Sheet"):
                    for cell in obj.getContents().keys():
                        cell_content = obj.getContents()[cell]
                        if (
                            param_name.lower() in cell.lower()
                            or param_name.lower() in str(cell_content).lower()
                        ):
                            try:
                                obj.set(cell, str(value))
                                print(f"✓ 设置电子表格单元格 {cell} = {value} mm")
                                return True
                            except:
                                continue

            print(f"✗ 未找到参数 '{param_name}'")
            print("可用参数:")
            params = self._get_parameters_internal()
            for i, p in enumerate(params[:10]):
                print(f"  {i + 1}. {p.name} = {p.value} mm")

            if len(params) > 10:
                print(f"  ... 以及另外 {len(params) - 10} 个参数")

            return False

        except Exception as e:
            print(f"设置参数失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _export_file_internal(self, output_path: Path, format_type: str) -> bool:
        """导出文件（内部实现，保持与旧代码兼容）"""
        if not self.active_doc:
            print("✗ 没有打开的文档")
            return False

        try:
            output_path = str(output_path)

            # 根据格式选择导出方式
            format_map = {
                "STEP": ".step",
                "STL": ".stl",
                "IGES": ".iges",
                "BREP": ".brep",
                "OBJ": ".obj",
            }

            ext = format_map.get(format_type.upper(), ".step")
            if not output_path.endswith(ext):
                output_path += ext

            # 确保输出目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            print(f"⏳ 导出到: {output_path}")

            # 导出STEP
            if format_type.upper() == "STEP":
                import Import

                # 收集所有Part对象
                objects = [
                    obj
                    for obj in self.active_doc.Objects
                    if obj.isDerivedFrom("Part::Feature")
                ]
                if objects:
                    Import.export(objects, output_path)
                    print(f"✓ 导出成功: {output_path}")
                    return True
                else:
                    print("✗ 没有找到可导出的Part对象")
                    return False

            # 导出STL
            elif format_type.upper() == "STL":
                for obj in self.active_doc.Objects:
                    if obj.isDerivedFrom("Part::Feature") and hasattr(obj, "Shape"):
                        obj.Shape.exportStl(output_path)
                        print(f"✓ 导出成功: {output_path}")
                        return True
                print("✗ 没有找到可导出的Shape")
                return False

            # 保存为FCStd（FreeCAD原生格式）
            elif format_type.upper() == "FCSTD":
                self.active_doc.saveAs(output_path)
                print(f"✓ 保存成功: {output_path}")
                return True

            # 导出IGES
            elif format_type.upper() == "IGES":
                import Import

                objects = [
                    obj
                    for obj in self.active_doc.Objects
                    if obj.isDerivedFrom("Part::Feature")
                ]
                if objects:
                    Import.export(objects, output_path)
                    print(f"✓ 导出成功: {output_path}")
                    return True
                else:
                    print("✗ 没有找到可导出的Part对象")
                    return False

            return False

        except Exception as e:
            print(f"导出失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    def close_document(self, save: bool = False):
        """关闭文档（兼容性方法）"""
        if self.active_doc:
            try:
                if save:
                    self.active_doc.save()
                doc_name = self.active_doc.Name
                self.fc_app.closeDocument(doc_name)
                self.active_doc = None
                print(f"✓ 已关闭文档: {doc_name}")
            except Exception as e:
                print(f"关闭文档时出错: {e}")

    def disconnect(self):
        """断开连接（兼容性方法）"""
        self.close_document(save=False)
        self.fc_app = None
        self.part_module = None
        self.is_connected = False

    # ========== 额外方法（向后兼容）==========

    def open_document(self, file_path: str) -> bool:
        """打开文档（向后兼容）"""
        return self.load_model(Path(file_path))

    def get_parameters(self) -> List[FCParameter]:
        """获取所有参数（向后兼容）"""
        return self._get_parameters_internal()

    def find_parameter(self, param_name: str) -> Optional[FCParameter]:
        """查找特定参数（向后兼容）"""
        return self._find_parameter_internal(param_name)

    def export_file(self, output_path: str, format_type: str = "STEP") -> bool:
        """导出文件（向后兼容）"""
        return self._export_file_internal(Path(output_path), format_type)

    def save_document(self, file_path: Optional[str] = None) -> bool:
        """保存文档（向后兼容）"""
        if not self.active_doc:
            return False

        try:
            if file_path:
                self.active_doc.saveAs(file_path)
            else:
                self.active_doc.save()
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False
