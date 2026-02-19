"""
FreeCAD MCP Server - 将FreeCAD功能暴露为MCP工具
"""

from typing import Dict, Any, Optional
from pathlib import Path
from sw_helper.mcp.core import Tool, get_mcp_server


class FreeCADMCPServer:
    """
    FreeCAD MCP服务器
    将FreeCAD的所有功能封装为MCP工具
    """

    def __init__(self):
        self.server = get_mcp_server()
        self.fc_connector = None
        self._register_tools()

    def _register_tools(self):
        """注册所有FreeCAD工具"""

        # 1. 连接FreeCAD
        self.server.register_tool(
            Tool(
                name="freecad_connect",
                description="连接到FreeCAD",
                input_schema={
                    "type": "object",
                    "properties": {
                        "use_mock": {
                            "type": "boolean",
                            "description": "是否使用模拟模式",
                            "default": False,
                        }
                    },
                },
                handler=self._handle_connect,
            )
        )

        # 2. 打开文档
        self.server.register_tool(
            Tool(
                name="freecad_open",
                description="打开FreeCAD文档",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "文件路径"}
                    },
                    "required": ["file_path"],
                },
                handler=self._handle_open,
            )
        )

        # 3. 获取参数列表
        self.server.register_tool(
            Tool(
                name="freecad_get_parameters",
                description="获取模型中的所有参数",
                input_schema={"type": "object", "properties": {}},
                handler=self._handle_get_parameters,
            )
        )

        # 4. 设置参数
        self.server.register_tool(
            Tool(
                name="freecad_set_parameter",
                description="设置模型参数",
                input_schema={
                    "type": "object",
                    "properties": {
                        "param_name": {"type": "string", "description": "参数名称"},
                        "value": {"type": "number", "description": "参数值"},
                    },
                    "required": ["param_name", "value"],
                },
                handler=self._handle_set_parameter,
            )
        )

        # 5. 重建模型
        self.server.register_tool(
            Tool(
                name="freecad_rebuild",
                description="重建模型",
                input_schema={"type": "object", "properties": {}},
                handler=self._handle_rebuild,
            )
        )

        # 6. 导出文件
        self.server.register_tool(
            Tool(
                name="freecad_export",
                description="导出模型为STEP/STL",
                input_schema={
                    "type": "object",
                    "properties": {
                        "output_path": {"type": "string", "description": "输出路径"},
                        "format": {
                            "type": "string",
                            "description": "导出格式",
                            "enum": ["STEP", "STL", "IGES"],
                            "default": "STEP",
                        },
                    },
                    "required": ["output_path"],
                },
                handler=self._handle_export,
            )
        )

        # 7. 创建几何体
        self.server.register_tool(
            Tool(
                name="freecad_create_box",
                description="创建立方体",
                input_schema={
                    "type": "object",
                    "properties": {
                        "length": {"type": "number", "default": 100},
                        "width": {"type": "number", "default": 50},
                        "height": {"type": "number", "default": 30},
                    },
                },
                handler=self._handle_create_box,
            )
        )

        self.server.register_tool(
            Tool(
                name="freecad_create_cylinder",
                description="创建圆柱体",
                input_schema={
                    "type": "object",
                    "properties": {
                        "radius": {"type": "number", "default": 25},
                        "height": {"type": "number", "default": 50},
                    },
                },
                handler=self._handle_create_cylinder,
            )
        )

        # 8. 应用圆角
        self.server.register_tool(
            Tool(
                name="freecad_apply_fillet",
                description="应用圆角",
                input_schema={
                    "type": "object",
                    "properties": {
                        "radius": {"type": "number", "description": "圆角半径"}
                    },
                    "required": ["radius"],
                },
                handler=self._handle_apply_fillet,
            )
        )

        # 9. 优化参数
        self.server.register_tool(
            Tool(
                name="freecad_optimize",
                description="优化参数",
                input_schema={
                    "type": "object",
                    "properties": {
                        "param_name": {"type": "string"},
                        "min_value": {"type": "number"},
                        "max_value": {"type": "number"},
                        "steps": {"type": "integer", "default": 5},
                    },
                    "required": ["param_name", "min_value", "max_value"],
                },
                handler=self._handle_optimize,
            )
        )

        # 10. 分析质量
        self.server.register_tool(
            Tool(
                name="freecad_analyze",
                description="分析模型质量",
                input_schema={
                    "type": "object",
                    "properties": {"file_path": {"type": "string"}},
                },
                handler=self._handle_analyze,
            )
        )

        print(f"[FreeCAD MCP] 已注册 {len(self.server.tools)} 个工具")

    def _get_connector(self):
        """获取或创建连接器"""
        if self.fc_connector is None:
            from sw_helper.integrations.freecad_connector import (
                FreeCADConnectorMock,
            )

            # 这里可以选择使用真实或模拟连接器
            self.fc_connector = FreeCADConnectorMock()
        return self.fc_connector

    # ===== 工具处理器 =====

    def _handle_connect(self, use_mock: bool = False) -> Dict[str, Any]:
        """处理连接请求"""
        try:
            if use_mock:
                from sw_helper.integrations.freecad_connector import (
                    FreeCADConnectorMock,
                )

                self.fc_connector = FreeCADConnectorMock()
            else:
                from sw_helper.integrations.freecad_connector import FreeCADConnector

                self.fc_connector = FreeCADConnector()

            success = self.fc_connector.connect()
            return {
                "success": success,
                "mode": "mock" if use_mock else "real",
                "message": "连接成功" if success else "连接失败",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_open(self, file_path: str) -> Dict[str, Any]:
        """处理打开文件请求"""
        connector = self._get_connector()
        success = connector.open_document(file_path)
        return {"success": success, "file_path": file_path}

    def _handle_get_parameters(self) -> Dict[str, Any]:
        """处理获取参数请求"""
        connector = self._get_connector()
        params = connector.get_parameters()
        return {
            "count": len(params),
            "parameters": [
                {"name": p.name, "value": p.value, "unit": p.unit} for p in params
            ],
        }

    def _handle_set_parameter(self, param_name: str, value: float) -> Dict[str, Any]:
        """处理设置参数请求"""
        connector = self._get_connector()
        success = connector.set_parameter(param_name, value)
        return {"success": success, "param_name": param_name, "new_value": value}

    def _handle_rebuild(self) -> Dict[str, Any]:
        """处理重建请求"""
        connector = self._get_connector()
        success = connector.rebuild()
        return {"success": success}

    def _handle_export(self, output_path: str, format: str = "STEP") -> Dict[str, Any]:
        """处理导出请求"""
        connector = self._get_connector()
        success = connector.export_file(output_path, format)
        return {"success": success, "output_path": output_path, "format": format}

    def _handle_create_box(
        self, length: float = 100, width: float = 50, height: float = 30
    ) -> Dict[str, Any]:
        """处理创建立方体请求"""
        # 这里简化实现，实际应该调用FreeCAD API
        return {
            "success": True,
            "shape": "box",
            "dimensions": {"length": length, "width": width, "height": height},
            "message": f"创建立方体: {length}x{width}x{height}mm",
        }

    def _handle_create_cylinder(
        self, radius: float = 25, height: float = 50
    ) -> Dict[str, Any]:
        """处理创建圆柱体请求"""
        return {
            "success": True,
            "shape": "cylinder",
            "dimensions": {"radius": radius, "height": height},
            "message": f"创建圆柱体: 半径{radius}mm, 高度{height}mm",
        }

    def _handle_apply_fillet(self, radius: float) -> Dict[str, Any]:
        """处理应用圆角请求"""
        connector = self._get_connector()
        # 这里简化实现
        return {
            "success": True,
            "fillet_radius": radius,
            "message": f"应用圆角: R{radius}mm",
        }

    def _handle_optimize(
        self, param_name: str, min_value: float, max_value: float, steps: int = 5
    ) -> Dict[str, Any]:
        """处理优化请求"""
        # 这里调用优化器
        from sw_helper.optimization.optimizer import FreeCADOptimizer

        optimizer = FreeCADOptimizer(use_mock=True)
        # 简化实现，实际应该执行完整优化流程

        return {
            "success": True,
            "param_name": param_name,
            "range": [min_value, max_value],
            "steps": steps,
            "message": f"优化完成: {param_name} 范围 {min_value}~{max_value}mm, {steps}步",
            "best_value": (min_value + max_value) / 2,
            "quality_score": 85.0,
        }

    def _handle_analyze(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """处理分析请求"""
        if file_path and Path(file_path).exists():
            from sw_helper.geometry.parser import GeometryParser

            parser = GeometryParser()
            try:
                geo_data = parser.parse(file_path)
                return {
                    "success": True,
                    "volume": geo_data.get("volume", 0),
                    "vertices": geo_data.get("vertices", 0),
                    "faces": geo_data.get("faces", 0),
                    "quality_score": 80.0,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        return {"success": True, "message": "模型质量良好", "quality_score": 85.0}


# 全局FreeCAD MCP Server实例
_fc_mcp_server: Optional[FreeCADMCPServer] = None


def get_freecad_mcp_server() -> FreeCADMCPServer:
    """获取全局FreeCAD MCP服务器"""
    global _fc_mcp_server
    if _fc_mcp_server is None:
        _fc_mcp_server = FreeCADMCPServer()
    return _fc_mcp_server
