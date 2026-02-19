"""
MCP (Model Context Protocol) 核心架构
用于CAE-CLI与FreeCAD、AI模型之间的通信
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import uuid


class MessageType(Enum):
    """MCP消息类型"""

    INITIALIZE = "initialize"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PROMPT_LIST = "prompts/list"
    PROMPT_GET = "prompts/get"
    NOTIFICATION = "notification"
    ERROR = "error"
    PING = "ping"


@dataclass
class MCPMessage:
    """MCP标准消息格式"""

    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.id is None and self.method:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = {"jsonrpc": self.jsonrpc}
        if self.id:
            data["id"] = self.id
        if self.method:
            data["method"] = self.method
        if self.params:
            data["params"] = self.params
        if self.result:
            data["result"] = self.result
        if self.error:
            data["error"] = self.error
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPMessage":
        """从字典创建"""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method"),
            params=data.get("params"),
            result=data.get("result"),
            error=data.get("error"),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "MCPMessage":
        return cls.from_dict(json.loads(json_str))


@dataclass
class Tool:
    """MCP工具定义"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


@dataclass
class Resource:
    """MCP资源定义"""

    uri: str
    name: str
    mime_type: str
    description: str
    handler: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "mimeType": self.mime_type,
            "description": self.description,
        }


class MCPServer:
    """
    MCP服务器基类
    提供工具注册、资源管理、消息处理
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, Tool] = {}
        self.resources: Dict[str, Resource] = {}
        self.handlers: Dict[str, Callable] = {}
        self.initialized = False

    def register_tool(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool
        if tool.handler:
            self.handlers[tool.name] = tool.handler
        print(f"[MCP Server] 注册工具: {tool.name}")

    def register_resource(self, resource: Resource):
        """注册资源"""
        self.resources[resource.uri] = resource
        print(f"[MCP Server] 注册资源: {resource.uri}")

    def tool(self, name: str, description: str, schema: Dict[str, Any]):
        """装饰器：注册工具"""

        def decorator(func: Callable):
            tool = Tool(
                name=name, description=description, input_schema=schema, handler=func
            )
            self.register_tool(tool)
            return func

        return decorator

    async def handle_message(self, message: MCPMessage) -> MCPMessage:
        """处理MCP消息"""
        try:
            if message.method == "initialize":
                return await self._handle_initialize(message)
            elif message.method == "tools/list":
                return await self._handle_tools_list(message)
            elif message.method == "tools/call":
                return await self._handle_tools_call(message)
            elif message.method == "resources/list":
                return await self._handle_resources_list(message)
            elif message.method == "ping":
                return MCPMessage(id=message.id, result={})
            else:
                return MCPMessage(
                    id=message.id,
                    error={"code": -32601, "message": f"未知方法: {message.method}"},
                )
        except Exception as e:
            return MCPMessage(id=message.id, error={"code": -32603, "message": str(e)})

    async def _handle_initialize(self, message: MCPMessage) -> MCPMessage:
        """处理初始化请求"""
        self.initialized = True
        return MCPMessage(
            id=message.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": self.name, "version": self.version},
            },
        )

    async def _handle_tools_list(self, message: MCPMessage) -> MCPMessage:
        """处理工具列表请求"""
        tools_list = [tool.to_dict() for tool in self.tools.values()]
        return MCPMessage(id=message.id, result={"tools": tools_list})

    async def _handle_tools_call(self, message: MCPMessage) -> MCPMessage:
        """处理工具调用"""
        params = message.params or {}
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            return MCPMessage(
                id=message.id,
                error={"code": -32602, "message": f"工具不存在: {tool_name}"},
            )

        tool = self.tools[tool_name]
        if not tool.handler:
            return MCPMessage(
                id=message.id,
                error={"code": -32602, "message": f"工具未实现: {tool_name}"},
            )

        try:
            # 调用工具处理器
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**arguments)
            else:
                result = tool.handler(**arguments)

            return MCPMessage(
                id=message.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False)
                            if isinstance(result, dict)
                            else str(result),
                        }
                    ]
                },
            )
        except Exception as e:
            return MCPMessage(
                id=message.id,
                error={"code": -32603, "message": f"工具执行错误: {str(e)}"},
            )

    async def _handle_resources_list(self, message: MCPMessage) -> MCPMessage:
        """处理资源列表请求"""
        resources_list = [res.to_dict() for res in self.resources.values()]
        return MCPMessage(id=message.id, result={"resources": resources_list})


class MCPClient:
    """
    MCP客户端基类
    用于连接MCP服务器并调用工具
    """

    def __init__(self):
        self.server_capabilities: Optional[Dict[str, Any]] = None
        self.available_tools: List[Tool] = []
        self.message_handlers: List[Callable] = []

    async def connect(self) -> bool:
        """连接到服务器"""
        raise NotImplementedError

    async def initialize(self) -> bool:
        """初始化连接"""
        message = MCPMessage(method="initialize", params={})
        response = await self.send_message(message)
        if response.result:
            self.server_capabilities = response.result
            return True
        return False

    async def list_tools(self) -> List[Tool]:
        """获取可用工具列表"""
        message = MCPMessage(method="tools/list")
        response = await self.send_message(message)
        if response.result and "tools" in response.result:
            tools_data = response.result["tools"]
            self.available_tools = [
                Tool(
                    name=t["name"],
                    description=t["description"],
                    input_schema=t.get("inputSchema", {}),
                )
                for t in tools_data
            ]
        return self.available_tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """调用工具"""
        message = MCPMessage(
            method="tools/call", params={"name": name, "arguments": arguments}
        )
        response = await self.send_message(message)
        if response.result:
            content = response.result.get("content", [])
            if content:
                text = content[0].get("text", "")
                try:
                    return json.loads(text)
                except:
                    return text
        elif response.error:
            raise Exception(response.error.get("message", "未知错误"))
        return None

    async def send_message(self, message: MCPMessage) -> MCPMessage:
        """发送消息（子类实现）"""
        raise NotImplementedError

    async def disconnect(self):
        """断开连接"""
        pass


class InMemoryMCPTransport:
    """
    内存中MCP传输层
    用于同一进程内的Server-Client通信
    """

    def __init__(self, server: MCPServer):
        self.server = server
        self.client_handler: Optional[Callable] = None

    async def handle_client_message(self, message: MCPMessage) -> MCPMessage:
        """处理客户端消息"""
        return await self.server.handle_message(message)

    def create_client(self) -> "InMemoryMCPClient":
        """创建关联的客户端"""
        return InMemoryMCPClient(self)


class InMemoryMCPClient(MCPClient):
    """内存中MCP客户端"""

    def __init__(self, transport: InMemoryMCPTransport):
        super().__init__()
        self.transport = transport

    async def connect(self) -> bool:
        """连接到服务器（内存中直接返回True）"""
        return await self.initialize()

    async def send_message(self, message: MCPMessage) -> MCPMessage:
        """通过传输层发送消息"""
        return await self.transport.handle_client_message(message)


# 全局MCP Server实例
_mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """获取或创建全局MCP服务器"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer(name="cae-cli-mcp", version="1.0.0")
    return _mcp_server
