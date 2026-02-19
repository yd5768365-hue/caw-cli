"""FreeCAD Parametric MCP Server - Main Entry Point"""

import asyncio
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from .bridge import FreeCADBridge
from .tools.parameters import ParameterTools
from .tools.sketches import SketchTools
from .tools.features import FeatureTools
from .tools.family import FamilyTools
from .tools.history import HistoryTools
from .tools.analysis import AnalysisTools
from .tools.templates import TemplateTools


class ParametricMCPServer:
    """Perfect Parametric Modeling MCP Server"""

    def __init__(self):
        self.server = Server("freecad-parametric-mcp")
        self.bridge = FreeCADBridge()

        # Initialize tool handlers
        self.param_tools = ParameterTools(self.bridge)
        self.sketch_tools = SketchTools(self.bridge)
        self.feature_tools = FeatureTools(self.bridge)
        self.family_tools = FamilyTools(self.bridge)
        self.history_tools = HistoryTools(self.bridge)
        self.analysis_tools = AnalysisTools(self.bridge)
        self.template_tools = TemplateTools(self.bridge)

        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools"""
            tools = []

            # Parameter management tools
            tools.extend(
                [
                    Tool(
                        name="create_parameter_group",
                        description="创建参数组用于组织相关参数",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "参数组名称"},
                                "description": {"type": "string", "description": "参数组描述"},
                                "parent_group": {
                                    "type": "string",
                                    "description": "父参数组名称（可选）",
                                },
                            },
                            "required": ["name"],
                        },
                    ),
                    Tool(
                        name="add_parameter",
                        description="添加参数到指定参数组",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "group": {"type": "string", "description": "参数组名称"},
                                "name": {"type": "string", "description": "参数名称"},
                                "value": {"type": "number", "description": "参数值"},
                                "unit": {
                                    "type": "string",
                                    "description": "单位（如 mm, deg, count）",
                                },
                                "formula": {"type": "string", "description": "计算公式（可选）"},
                                "min_value": {"type": "number", "description": "最小值（可选）"},
                                "max_value": {"type": "number", "description": "最大值（可选）"},
                                "description": {"type": "string", "description": "参数描述"},
                            },
                            "required": ["group", "name"],
                        },
                    ),
                    Tool(
                        name="set_parameter_formula",
                        description="为参数设置计算公式",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "group": {"type": "string", "description": "参数组名称"},
                                "name": {"type": "string", "description": "参数名称"},
                                "formula": {"type": "string", "description": "计算公式"},
                            },
                            "required": ["group", "name", "formula"],
                        },
                    ),
                    Tool(
                        name="update_parameter",
                        description="更新参数值并触发模型重生成",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "group": {"type": "string", "description": "参数组名称"},
                                "name": {"type": "string", "description": "参数名称"},
                                "value": {"type": "number", "description": "新参数值"},
                                "regenerate": {
                                    "type": "boolean",
                                    "description": "是否立即重生成模型",
                                    "default": True,
                                },
                            },
                            "required": ["group", "name", "value"],
                        },
                    ),
                    Tool(
                        name="list_parameters",
                        description="列出所有参数或指定组的参数",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "group": {
                                    "type": "string",
                                    "description": "参数组名称（可选，不指定则列出所有）",
                                },
                                "include_formulas": {
                                    "type": "boolean",
                                    "description": "是否包含公式信息",
                                    "default": True,
                                },
                            },
                        },
                    ),
                    Tool(
                        name="create_parameter_link",
                        description="创建两个参数之间的关联",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source_group": {"type": "string", "description": "源参数组"},
                                "source_param": {"type": "string", "description": "源参数名"},
                                "target_group": {"type": "string", "description": "目标参数组"},
                                "target_param": {"type": "string", "description": "目标参数名"},
                                "expression": {
                                    "type": "string",
                                    "description": "关联表达式，如 '*2' 或 '+10'",
                                },
                            },
                            "required": [
                                "source_group",
                                "source_param",
                                "target_group",
                                "target_param",
                            ],
                        },
                    ),
                    Tool(
                        name="validate_parameters",
                        description="验证所有参数的合法性",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "check_constraints": {
                                    "type": "boolean",
                                    "description": "是否检查约束冲突",
                                    "default": True,
                                },
                                "check_circularity": {
                                    "type": "boolean",
                                    "description": "是否检查循环依赖",
                                    "default": True,
                                },
                            },
                        },
                    ),
                    Tool(
                        name="import_parameters",
                        description="从文件导入参数",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "参数文件路径（JSON/CSV/Excel）",
                                },
                                "group_prefix": {
                                    "type": "string",
                                    "description": "导入参数组前缀（可选）",
                                },
                            },
                            "required": ["file_path"],
                        },
                    ),
                    Tool(
                        name="export_parameters",
                        description="导出参数到文件",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "file_path": {"type": "string", "description": "输出文件路径"},
                                "format": {
                                    "type": "string",
                                    "enum": ["json", "csv", "xlsx"],
                                    "default": "json",
                                },
                                "groups": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "要导出的参数组（可选）",
                                },
                            },
                            "required": ["file_path"],
                        },
                    ),
                ]
            )

            # Sketch tools
            tools.extend(
                [
                    Tool(
                        name="create_parametric_sketch",
                        description="创建参数化草图",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "草图名称"},
                                "plane": {
                                    "type": "string",
                                    "description": "草图平面（XY, XZ, YZ 或面名称）",
                                },
                                "body": {"type": "string", "description": "所属Body（可选）"},
                                "parameters": {
                                    "type": "object",
                                    "description": "草图关联的参数映射",
                                },
                            },
                            "required": ["name", "plane"],
                        },
                    ),
                    Tool(
                        name="add_constrained_line",
                        description="添加带约束的直线",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sketch": {"type": "string", "description": "草图名称"},
                                "start": {
                                    "type": "object",
                                    "properties": {
                                        "x": {"type": "number"},
                                        "y": {"type": "number"},
                                    },
                                },
                                "end": {
                                    "type": "object",
                                    "properties": {
                                        "x": {"type": "number"},
                                        "y": {"type": "number"},
                                    },
                                },
                                "constraints": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "约束类型列表",
                                },
                                "parameter_refs": {
                                    "type": "object",
                                    "description": "参数引用（如长度、角度）",
                                },
                            },
                            "required": ["sketch", "start", "end"],
                        },
                    ),
                    Tool(
                        name="add_constrained_circle",
                        description="添加带约束的圆",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sketch": {"type": "string", "description": "草图名称"},
                                "center": {
                                    "type": "object",
                                    "properties": {
                                        "x": {"type": "number"},
                                        "y": {"type": "number"},
                                    },
                                },
                                "radius": {"type": "string", "description": "半径参数引用或数值"},
                                "construction": {"type": "boolean", "default": False},
                            },
                            "required": ["sketch", "center", "radius"],
                        },
                    ),
                    Tool(
                        name="add_dimensional_constraint",
                        description="添加尺寸约束",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sketch": {"type": "string", "description": "草图名称"},
                                "type": {
                                    "type": "string",
                                    "enum": ["distance", "radius", "diameter", "angle"],
                                },
                                "entities": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "约束对象名称列表",
                                },
                                "value": {"type": "string", "description": "约束值或参数引用"},
                                "expression": {
                                    "type": "string",
                                    "description": "约束表达式（可选）",
                                },
                            },
                            "required": ["sketch", "type", "entities", "value"],
                        },
                    ),
                    Tool(
                        name="auto_constrain_sketch",
                        description="自动为草图添加约束",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sketch": {"type": "string", "description": "草图名称"},
                                "strategy": {
                                    "type": "string",
                                    "enum": ["minimal", "standard", "full"],
                                    "default": "standard",
                                },
                                "detect_symmetry": {"type": "boolean", "default": True},
                            },
                            "required": ["sketch"],
                        },
                    ),
                    Tool(
                        name="analyze_sketch_dof",
                        description="分析草图自由度",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sketch": {"type": "string", "description": "草图名称"},
                                "detailed": {"type": "boolean", "default": False},
                            },
                            "required": ["sketch"],
                        },
                    ),
                    Tool(
                        name="get_constraint_graph",
                        description="获取约束关系图",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sketch": {"type": "string", "description": "草图名称"},
                                "format": {
                                    "type": "string",
                                    "enum": ["json", "svg", "dot"],
                                    "default": "json",
                                },
                                "include_dof": {"type": "boolean", "default": True},
                            },
                            "required": ["sketch"],
                        },
                    ),
                ]
            )

            # Feature tools
            tools.extend(
                [
                    Tool(
                        name="create_parametric_pad",
                        description="创建参数化拉伸特征",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sketch": {"type": "string", "description": "草图名称"},
                                "length_param": {"type": "string", "description": "长度参数引用"},
                                "direction": {
                                    "type": "string",
                                    "enum": ["forward", "reverse", "both"],
                                    "default": "forward",
                                },
                                "name": {"type": "string", "description": "特征名称"},
                            },
                            "required": ["sketch", "length_param"],
                        },
                    ),
                    Tool(
                        name="create_parametric_pocket",
                        description="创建参数化挖槽特征",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sketch": {"type": "string", "description": "草图名称"},
                                "depth_param": {"type": "string", "description": "深度参数引用"},
                                "name": {"type": "string", "description": "特征名称"},
                            },
                            "required": ["sketch", "depth_param"],
                        },
                    ),
                    Tool(
                        name="create_parametric_hole",
                        description="创建参数化孔",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "position": {"type": "object", "description": "孔位置"},
                                "diameter_param": {"type": "string", "description": "直径参数引用"},
                                "depth_param": {"type": "string", "description": "深度参数引用"},
                                "hole_type": {
                                    "type": "string",
                                    "enum": ["simple", "countersink", "counterbore", "tapped"],
                                },
                                "name": {"type": "string", "description": "特征名称"},
                            },
                            "required": ["position", "diameter_param"],
                        },
                    ),
                    Tool(
                        name="edit_feature_parameter",
                        description="编辑特征参数",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "feature": {"type": "string", "description": "特征名称"},
                                "parameter": {"type": "string", "description": "参数名"},
                                "value": {"type": "string", "description": "新值或参数引用"},
                                "regenerate": {"type": "boolean", "default": True},
                            },
                            "required": ["feature", "parameter", "value"],
                        },
                    ),
                    Tool(
                        name="get_feature_tree",
                        description="获取特征树",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "document": {"type": "string", "description": "文档名称（可选）"},
                                "include_suppressed": {"type": "boolean", "default": False},
                            },
                        },
                    ),
                    Tool(
                        name="analyze_feature_dependencies",
                        description="分析特征依赖关系",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "feature": {"type": "string", "description": "特征名称"},
                                "direction": {
                                    "type": "string",
                                    "enum": ["upstream", "downstream", "both"],
                                    "default": "both",
                                },
                            },
                            "required": ["feature"],
                        },
                    ),
                ]
            )

            # Family tools
            tools.extend(
                [
                    Tool(
                        name="create_design_table",
                        description="创建设计表",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "设计表名称"},
                                "parameters": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "参数列表",
                                },
                                "data": {
                                    "type": "array",
                                    "items": {"type": "object"},
                                    "description": "设计表数据行",
                                },
                            },
                            "required": ["name", "parameters"],
                        },
                    ),
                    Tool(
                        name="import_design_table",
                        description="从文件导入设计表",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "CSV/Excel 文件路径",
                                },
                                "name": {"type": "string", "description": "设计表名称"},
                            },
                            "required": ["file_path"],
                        },
                    ),
                    Tool(
                        name="generate_family_member",
                        description="生成参数族成员",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "design_table": {"type": "string", "description": "设计表名称"},
                                "row_index": {"type": "integer", "description": "行索引"},
                                "name": {"type": "string", "description": "成员名称"},
                            },
                            "required": ["design_table", "row_index"],
                        },
                    ),
                    Tool(
                        name="batch_generate_family",
                        description="批量生成参数族",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "template": {"type": "string", "description": "模板名称"},
                                "design_table": {"type": "string", "description": "设计表名称"},
                                "naming_pattern": {"type": "string", "description": "命名模式"},
                                "output_dir": {"type": "string", "description": "输出目录"},
                            },
                            "required": ["template", "design_table"],
                        },
                    ),
                    Tool(
                        name="create_parameter_sweep",
                        description="创建参数扫描",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "parameter": {"type": "string", "description": "参数名"},
                                "range": {
                                    "type": "object",
                                    "properties": {
                                        "min": {"type": "number"},
                                        "max": {"type": "number"},
                                        "steps": {"type": "integer"},
                                    },
                                },
                                "metrics": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "要记录的指标",
                                },
                            },
                            "required": ["parameter", "range"],
                        },
                    ),
                ]
            )

            # History tools
            tools.extend(
                [
                    Tool(
                        name="get_design_timeline",
                        description="获取设计时间线",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "document": {"type": "string", "description": "文档名称（可选）"},
                                "limit": {
                                    "type": "integer",
                                    "description": "最大返回数量",
                                    "default": 50,
                                },
                            },
                        },
                    ),
                    Tool(
                        name="create_design_branch",
                        description="创建设计分支",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "分支名称"},
                                "from_version": {
                                    "type": "string",
                                    "description": "基于版本（可选）",
                                },
                                "description": {"type": "string", "description": "分支描述"},
                            },
                            "required": ["name"],
                        },
                    ),
                    Tool(
                        name="compare_design_versions",
                        description="对比设计版本",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "version_a": {"type": "string", "description": "版本A"},
                                "version_b": {"type": "string", "description": "版本B"},
                                "include_parameters": {"type": "boolean", "default": True},
                                "include_geometry": {"type": "boolean", "default": False},
                            },
                            "required": ["version_a", "version_b"],
                        },
                    ),
                ]
            )

            # Analysis tools
            tools.extend(
                [
                    Tool(
                        name="analyze_parameter_sensitivity",
                        description="分析参数敏感性",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "target_parameter": {"type": "string", "description": "目标参数"},
                                "target_metric": {
                                    "type": "string",
                                    "description": "目标指标（如 mass, volume）",
                                },
                                "range": {
                                    "type": "object",
                                    "properties": {
                                        "min": {"type": "number"},
                                        "max": {"type": "number"},
                                        "steps": {"type": "integer"},
                                    },
                                },
                                "output": {"type": "string", "description": "输出文件路径"},
                            },
                            "required": ["target_parameter", "target_metric", "range"],
                        },
                    ),
                    Tool(
                        name="check_design_rules",
                        description="检查设计规则",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "ruleset": {"type": "string", "description": "规则集名称"},
                                "auto_fix": {"type": "boolean", "default": False},
                            },
                        },
                    ),
                    Tool(
                        name="generate_parameter_report",
                        description="生成参数报告",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "report_type": {
                                    "type": "string",
                                    "enum": ["full", "sensitivity", "family"],
                                },
                                "parameters": {"type": "array", "items": {"type": "string"}},
                                "include_charts": {"type": "boolean", "default": True},
                                "output": {"type": "string", "description": "输出文件路径"},
                            },
                            "required": ["report_type", "output"],
                        },
                    ),
                ]
            )

            # Template tools
            tools.extend(
                [
                    Tool(
                        name="create_from_template",
                        description="从模板创建模型",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "template": {"type": "string", "description": "模板名称"},
                                "parameters": {"type": "object", "description": "模板参数"},
                                "name": {"type": "string", "description": "模型名称"},
                            },
                            "required": ["template"],
                        },
                    ),
                    Tool(
                        name="list_available_templates",
                        description="列出可用模板",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "category": {"type": "string", "description": "类别过滤"}
                            },
                        },
                    ),
                ]
            )

            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Call a tool"""
            try:
                result = await self._handle_tool(name, arguments)
                return [TextContent(type="text", text=str(result))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_tool(self, name: str, arguments: dict) -> Any:
        """Route tool call to appropriate handler"""

        # Parameter tools
        if name == "create_parameter_group":
            return await self.param_tools.create_group(**arguments)
        elif name == "add_parameter":
            return await self.param_tools.add_parameter(**arguments)
        elif name == "set_parameter_formula":
            return await self.param_tools.set_formula(**arguments)
        elif name == "update_parameter":
            return await self.param_tools.update_parameter(**arguments)
        elif name == "list_parameters":
            return await self.param_tools.list_parameters(**arguments)
        elif name == "create_parameter_link":
            return await self.param_tools.create_link(**arguments)
        elif name == "validate_parameters":
            return await self.param_tools.validate(**arguments)
        elif name == "import_parameters":
            return await self.param_tools.import_from_file(**arguments)
        elif name == "export_parameters":
            return await self.param_tools.export_to_file(**arguments)

        # Sketch tools
        elif name == "create_parametric_sketch":
            return await self.sketch_tools.create_sketch(**arguments)
        elif name == "add_constrained_line":
            return await self.sketch_tools.add_line(**arguments)
        elif name == "add_constrained_circle":
            return await self.sketch_tools.add_circle(**arguments)
        elif name == "add_dimensional_constraint":
            return await self.sketch_tools.add_constraint(**arguments)
        elif name == "auto_constrain_sketch":
            return await self.sketch_tools.auto_constrain(**arguments)
        elif name == "analyze_sketch_dof":
            return await self.sketch_tools.analyze_dof(**arguments)
        elif name == "get_constraint_graph":
            return await self.sketch_tools.get_constraint_graph(**arguments)

        # Feature tools
        elif name == "create_parametric_pad":
            return await self.feature_tools.create_pad(**arguments)
        elif name == "create_parametric_pocket":
            return await self.feature_tools.create_pocket(**arguments)
        elif name == "create_parametric_hole":
            return await self.feature_tools.create_hole(**arguments)
        elif name == "edit_feature_parameter":
            return await self.feature_tools.edit_parameter(**arguments)
        elif name == "get_feature_tree":
            return await self.feature_tools.get_tree(**arguments)
        elif name == "analyze_feature_dependencies":
            return await self.feature_tools.analyze_dependencies(**arguments)

        # Family tools
        elif name == "create_design_table":
            return await self.family_tools.create_table(**arguments)
        elif name == "import_design_table":
            return await self.family_tools.import_table(**arguments)
        elif name == "generate_family_member":
            return await self.family_tools.generate_member(**arguments)
        elif name == "batch_generate_family":
            return await self.family_tools.batch_generate(**arguments)
        elif name == "create_parameter_sweep":
            return await self.family_tools.create_sweep(**arguments)

        # History tools
        elif name == "get_design_timeline":
            return await self.history_tools.get_timeline(**arguments)
        elif name == "create_design_branch":
            return await self.history_tools.create_branch(**arguments)
        elif name == "compare_design_versions":
            return await self.history_tools.compare_versions(**arguments)

        # Analysis tools
        elif name == "analyze_parameter_sensitivity":
            return await self.analysis_tools.analyze_sensitivity(**arguments)
        elif name == "check_design_rules":
            return await self.analysis_tools.check_rules(**arguments)
        elif name == "generate_parameter_report":
            return await self.analysis_tools.generate_report(**arguments)

        # Template tools
        elif name == "create_from_template":
            return await self.template_tools.create_from_template(**arguments)
        elif name == "list_available_templates":
            return await self.template_tools.list_templates(**arguments)

        else:
            raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        """Run the server"""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    server = ParametricMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
