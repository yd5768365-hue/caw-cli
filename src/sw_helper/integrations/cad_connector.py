"""
CAD连接器模块 - 使用pywin32连接SolidWorks和FreeCAD
实现参数修改、重建模型、导出文件
"""

from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Parameter:
    """参数数据类"""

    name: str
    value: float
    unit: str = "mm"
    description: str = ""
    modifiable: bool = True


class SolidWorksConnector:
    """SolidWorks连接器 - 使用COM API"""

    def __init__(self):
        self.sw_app = None
        self.active_doc = None
        self.is_connected = False

    def connect(self) -> bool:
        """连接到SolidWorks"""
        try:
            import win32com.client

            # 尝试连接已运行的SolidWorks实例
            self.sw_app = win32com.client.Dispatch("SldWorks.Application")
            self.sw_app.Visible = True
            self.is_connected = True

            return True

        except Exception as e:
            print(f"连接SolidWorks失败: {e}")
            return False

    def open_document(self, file_path: str) -> bool:
        """打开文档"""
        if not self.is_connected:
            if not self.connect():
                return False

        try:
            file_path = str(Path(file_path).resolve())

            # 定义文件类型常量
            doc_types = {
                ".sldprt": 1,  # 零件
                ".sldasm": 2,  # 装配体
                ".slddrw": 3,  # 工程图
            }

            ext = Path(file_path).suffix.lower()
            doc_type = doc_types.get(ext, 1)

            # 打开文档
            errors = 0
            warnings = 0
            self.active_doc = self.sw_app.OpenDoc6(
                file_path, doc_type, 0, "", errors, warnings
            )

            return self.active_doc is not None

        except Exception as e:
            print(f"打开文档失败: {e}")
            return False

    def get_parameters(self) -> List[Parameter]:
        """获取所有参数"""
        if not self.active_doc:
            return []

        params = []

        try:
            # 获取自定义属性
            cust_prop = self.active_doc.Extension.CustomPropertyManager("")

            # 获取尺寸参数
            model = self.active_doc

            # 遍历特征获取尺寸
            feat = model.FirstFeature
            while feat:
                if feat.GetTypeName() in ["Dimension", "BaseFlange", "Extrude"]:
                    try:
                        # 获取特征的尺寸
                        dim = feat.GetSpecificFeature2
                        if hasattr(dim, "GetDimension"):
                            d = dim.GetDimension(0)
                            if d:
                                params.append(
                                    Parameter(
                                        name=d.FullName,
                                        value=d.Value * 1000,  # 转换为mm
                                        unit="mm",
                                        description=f"特征: {feat.Name}",
                                    )
                                )
                    except:
                        pass

                feat = feat.GetNextFeature()

            # 获取全局变量（方程式）
            eq_mgr = model.GetEquationMgr
            if eq_mgr:
                for i in range(eq_mgr.GetCount):
                    eq = eq_mgr.Equation(i)
                    if eq:
                        # 解析方程式
                        parts = eq.split("=", 1)
                        if len(parts) == 2:
                            name = parts[0].strip().strip('"')
                            try:
                                value = float(parts[1])
                                params.append(
                                    Parameter(
                                        name=name,
                                        value=value,
                                        unit="mm",
                                        description="全局变量",
                                    )
                                )
                            except:
                                pass

        except Exception as e:
            print(f"获取参数失败: {e}")

        return params

    def set_parameter(self, param_name: str, value: float) -> bool:
        """设置参数值"""
        if not self.active_doc:
            return False

        try:
            # 尝试作为尺寸参数设置
            dim = self.active_doc.Parameter(param_name)
            if dim:
                # SolidWorks使用米为单位
                dim.SystemValue = value / 1000
                return True

            # 尝试作为全局变量设置
            eq_mgr = self.active_doc.GetEquationMgr
            if eq_mgr:
                for i in range(eq_mgr.GetCount):
                    eq = eq_mgr.Equation(i)
                    if eq and param_name in eq:
                        # 更新方程式
                        new_eq = f'"{param_name}" = {value}'
                        eq_mgr.Equation(i, new_eq)
                        return True

            return False

        except Exception as e:
            print(f"设置参数失败: {e}")
            return False

    def rebuild(self) -> bool:
        """重建模型"""
        if not self.active_doc:
            return False

        try:
            # 强制重建
            self.active_doc.EditRebuild3
            return True
        except Exception as e:
            print(f"重建失败: {e}")
            return False

    def export_file(self, output_path: str, format_type: str = "STEP") -> bool:
        """导出文件"""
        if not self.active_doc:
            return False

        try:
            output_path = str(Path(output_path))

            # 根据格式选择导出方式
            format_map = {
                "STEP": (".step", True),
                "STL": (".stl", False),
                "IGES": (".iges", True),
                "PDF": (".pdf", False),
                "PARASOLID": (".x_t", True),
            }

            ext, use_save = format_map.get(format_type.upper(), (".step", True))

            # 确保扩展名正确
            if not output_path.endswith(ext):
                output_path += ext

            if use_save:
                # 使用SaveAs
                errors = 0
                warnings = 0
                result = self.active_doc.SaveAs3(output_path, 0, 2)
                return result == 0
            else:
                # 特殊导出（如STL）
                if format_type.upper() == "STL":
                    stl_exporter = self.active_doc.Extension.GetSTLExporter
                    if stl_exporter:
                        stl_exporter.ExportBinary = False
                        stl_exporter.ExportPath = output_path
                        return stl_exporter.Save

            return False

        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def close_document(self, save: bool = False):
        """关闭文档"""
        if self.active_doc:
            try:
                self.sw_app.CloseDoc(self.active_doc.GetTitle)
                self.active_doc = None
            except:
                pass

    def disconnect(self):
        """断开连接"""
        self.close_document()
        self.sw_app = None
        self.is_connected = False


class FreeCADConnector:
    """FreeCAD连接器"""

    def __init__(self):
        self.fc_app = None
        self.active_doc = None
        self.is_connected = False

    def connect(self) -> bool:
        """连接到FreeCAD"""
        try:
            # 尝试导入FreeCAD
            import FreeCAD as App
            import Part

            self.fc_app = App
            self.is_connected = True

            return True

        except ImportError:
            print("未找到FreeCAD模块，请确保已安装FreeCAD并配置Python路径")
            return False
        except Exception as e:
            print(f"连接FreeCAD失败: {e}")
            return False

    def open_document(self, file_path: str) -> bool:
        """打开文档"""
        if not self.is_connected:
            if not self.connect():
                return False

        try:
            file_path = str(Path(file_path).resolve())
            self.active_doc = self.fc_app.open(file_path)

            return self.active_doc is not None

        except Exception as e:
            print(f"打开文档失败: {e}")
            return False

    def get_parameters(self) -> List[Parameter]:
        """获取参数"""
        if not self.active_doc:
            return []

        params = []

        try:
            # FreeCAD使用电子表格或约束
            for obj in self.active_doc.Objects:
                # 检查是否有约束
                if hasattr(obj, "Constraints"):
                    for constraint in obj.Constraints:
                        if hasattr(constraint, "Value"):
                            params.append(
                                Parameter(
                                    name=constraint.Name,
                                    value=constraint.Value,
                                    unit="mm",
                                    description=f"对象: {obj.Name}",
                                )
                            )

                # 检查属性
                if hasattr(obj, "Length"):
                    params.append(
                        Parameter(
                            name=f"{obj.Name}.Length", value=obj.Length, unit="mm"
                        )
                    )

        except Exception as e:
            print(f"获取参数失败: {e}")

        return params

    def set_parameter(self, param_name: str, value: float) -> bool:
        """设置参数"""
        if not self.active_doc:
            return False

        try:
            # 解析参数名（格式：ObjectName.Property）
            parts = param_name.split(".", 1)

            if len(parts) == 2:
                obj_name, prop_name = parts
                obj = self.active_doc.getObject(obj_name)

                if obj and hasattr(obj, prop_name):
                    setattr(obj, prop_name, value)
                    return True
            else:
                # 尝试查找约束
                for obj in self.active_doc.Objects:
                    if hasattr(obj, "Constraints"):
                        for i, constraint in enumerate(obj.Constraints):
                            if constraint.Name == param_name:
                                # 更新约束值
                                obj.setDatum(i, value)
                                return True

            return False

        except Exception as e:
            print(f"设置参数失败: {e}")
            return False

    def rebuild(self) -> bool:
        """重新计算文档"""
        if not self.active_doc:
            return False

        try:
            self.active_doc.recompute()
            return True
        except Exception as e:
            print(f"重建失败: {e}")
            return False

    def export_file(self, output_path: str, format_type: str = "STEP") -> bool:
        """导出文件"""
        if not self.active_doc:
            return False

        try:

            output_path = str(Path(output_path))

            # 选择导出格式
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

            # 导出
            if format_type.upper() == "STEP":
                import Import

                Import.export(
                    [
                        obj
                        for obj in self.active_doc.Objects
                        if obj.isDerivedFrom("Part::Feature")
                    ],
                    output_path,
                )
                return True
            elif format_type.upper() == "STL":
                # 导出STL
                for obj in self.active_doc.Objects:
                    if obj.isDerivedFrom("Part::Feature"):
                        obj.Shape.exportStl(output_path)
                        return True

            return False

        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def close_document(self, save: bool = False):
        """关闭文档"""
        if self.active_doc:
            try:
                if save:
                    self.active_doc.save()
                self.fc_app.closeDocument(self.active_doc.Name)
                self.active_doc = None
            except:
                pass

    def disconnect(self):
        """断开连接"""
        self.close_document()
        self.fc_app = None
        self.is_connected = False


class CADManager:
    """CAD管理器 - 统一管理多个CAD软件"""

    def __init__(self):
        self.connectors = {
            "solidworks": SolidWorksConnector(),
            "freecad": FreeCADConnector(),
        }
        self.active_cad = None

    def auto_connect(self) -> str:
        """自动连接可用的CAD软件"""
        for name, connector in self.connectors.items():
            if connector.connect():
                self.active_cad = name
                print(f"成功连接到: {name}")
                return name

        print("未能连接到任何CAD软件")
        return None

    def get_connector(self, cad_name: Optional[str] = None):
        """获取连接器"""
        if cad_name:
            return self.connectors.get(cad_name.lower())
        elif self.active_cad:
            return self.connectors.get(self.active_cad)
        return None

    def disconnect_all(self):
        """断开所有连接"""
        for connector in self.connectors.values():
            connector.disconnect()
        self.active_cad = None
