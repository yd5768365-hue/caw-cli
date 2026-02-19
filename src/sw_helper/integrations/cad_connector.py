"""
CAD连接器管理器 - 统一管理多个CAD软件的连接

提供CAD软件的自动检测、连接和切换功能，
支持SolidWorks、FreeCAD等主流CAD软件。
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import sys

# 尝试导入基础连接器
try:
    from integrations._base.connectors import CADConnector
except ImportError:
    CADConnector = None


class CADManager:
    """CAD连接器管理器
    
    负责管理多个CAD软件的连接，提供统一的接口
    支持自动检测和手动选择CAD软件
    """

    def __init__(self):
        self.connectors: Dict[str, Any] = {}
        self.active_cad: Optional[str] = None
        self._available_cads: List[str] = []

    def auto_connect(self) -> Optional[str]:
        """自动检测并连接可用的CAD软件
        
        按优先级尝试连接:
        1. FreeCAD
        2. SolidWorks
        
        Returns:
            Optional[str]: 成功连接的CAD名称，未找到则返回None
        """
        # 尝试FreeCAD
        cad_name = self._try_connect_freecad()
        if cad_name:
            self.active_cad = cad_name
            return cad_name

        # 尝试SolidWorks
        cad_name = self._try_connect_solidworks()
        if cad_name:
            self.active_cad = cad_name
            return cad_name

        return None

    def _try_connect_freecad(self) -> Optional[str]:
        """尝试连接FreeCAD"""
        try:
            from integrations.cad.freecad import FreeCADConnector
            
            connector = FreeCADConnector()
            if connector.connect():
                self.connectors["freecad"] = connector
                self._available_cads.append("freecad")
                return "freecad"
        except ImportError:
            pass
        except Exception:
            pass
        return None

    def _try_connect_solidworks(self) -> Optional[str]:
        """尝试连接SolidWorks（需要Windows环境）"""
        try:
            # 使用本地定义的SolidWorksConnector类
            connector = SolidWorksConnector()
            if connector.connect():
                self.connectors["solidworks"] = connector
                self._available_cads.append("solidworks")
                return "solidworks"
        except ImportError:
            pass
        except Exception:
            pass
        return None

    def get_connector(self, cad_name: Optional[str] = None) -> Optional[Any]:
        """获取指定CAD的连接器
        
        Args:
            cad_name: CAD名称，如果为None则返回当前激活的连接器
            
        Returns:
            Optional[Any]: CAD连接器实例
        """
        if cad_name is None:
            cad_name = self.active_cad
        
        if cad_name is None:
            return None
            
        return self.connectors.get(cad_name)

    def connect(self, cad_name: str) -> bool:
        """连接到指定的CAD软件
        
        Args:
            cad_name: CAD名称 ("solidworks", "freecad")
            
        Returns:
            bool: 连接是否成功
        """
        if cad_name == "solidworks":
            result = self._try_connect_solidworks()
        elif cad_name == "freecad":
            result = self._try_connect_freecad()
        else:
            return False
            
        if result:
            self.active_cad = result
            return True
        return False

    def disconnect_all(self) -> None:
        """断开所有CAD连接"""
        for name, connector in self.connectors.items():
            try:
                if hasattr(connector, 'disconnect'):
                    connector.disconnect()
                elif hasattr(connector, 'close_document'):
                    connector.close_document()
            except Exception:
                pass
        
        self.connectors.clear()
        self.active_cad = None

    def list_available(self) -> List[str]:
        """列出所有可用的CAD软件
        
        Returns:
            List[str]: 可用的CAD名称列表
        """
        return self._available_cads.copy()

    def get_active_cad(self) -> Optional[str]:
        """获取当前激活的CAD软件名称
        
        Returns:
            Optional[str]: 当前激活的CAD名称
        """
        return self.active_cad


class SolidWorksConnector:
    """SolidWorks连接器
    
    注意: 此连接器需要SolidWorks安装且仅在Windows环境下可用
    """
    
    def __init__(self):
        self.sws_app = None
        self.active_doc = None
        self.is_connected = False

    def connect(self) -> bool:
        """连接到SolidWorks实例"""
        try:
            # 尝试使用Python的win32com连接SolidWorks
            try:
                import win32com.client
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                print("警告: win32com/pywin32不可用，无法连接SolidWorks")
                print("提示: pip install pywin32")
                return False
            
            self.sws_app = win32com.client.Dispatch("SldWorks.Application")
            self.sws_app.Visible = True
            self.is_connected = True
            return True
        except Exception as e:
            print(f"连接SolidWorks失败: {e}")
            return False

    def load_model(self, file_path: Path) -> bool:
        """加载CAD模型文件"""
        if not self.is_connected:
            if not self.connect():
                return False

        try:
            file_path = str(file_path.resolve())
            # 打开文档
            self.active_doc = self.sws_app.OpenDoc(file_path, 1)  # 1 = swDocPART
            if self.active_doc:
                return True
            return False
        except Exception as e:
            print(f"打开文档失败: {e}")
            return False

    def get_parameter(self, name: str) -> Optional[float]:
        """获取指定参数的值"""
        if not self.active_doc:
            return None
        
        try:
            # 获取文档的定制属性
            custom_props = self.active_doc.CustomPropertyManager
            if custom_props:
                value = custom_props.Get(name)
                if value:
                    return float(value)
        except Exception:
            pass
        return None

    def set_parameter(self, name: str, value: float) -> bool:
        """设置参数值"""
        if not self.active_doc:
            return False

        try:
            custom_props = self.active_doc.CustomPropertyManager
            if custom_props:
                custom_props.Set(name, str(value))
                return True
        except Exception as e:
            print(f"设置参数失败: {e}")
        return False

    def rebuild(self) -> bool:
        """重建模型"""
        if not self.active_doc:
            return False

        try:
            self.active_doc.EditRebuild3()
            return True
        except Exception:
            return False

    def export_step(self, output_path: Path) -> bool:
        """导出为STEP格式"""
        if not self.active_doc:
            return False

        try:
            export_data = self.sws_app.GetExportFileData(1)  # 1 = step
            result = self.active_doc.SaveAs3(str(output_path), 0, 0)
            return result == 0
        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def get_supported_formats(self):
        """获取支持的导出格式"""
        from integrations._base.connectors import FileFormat
        return [
            FileFormat.STEP,
            FileFormat.STL,
            FileFormat.IGES,
            FileFormat.SLDPRT,
            FileFormat.SLDASM,
        ]
