"""
MCP (Model Context Protocol) 模块
"""

from .core import (
    MCPServer,
    MCPClient,
    MCPMessage,
    Tool,
    Resource,
    InMemoryMCPTransport,
    InMemoryMCPClient,
    get_mcp_server,
)
from .freecad_server import FreeCADMCPServer, get_freecad_mcp_server

__all__ = [
    "MCPServer",
    "MCPClient",
    "MCPMessage",
    "Tool",
    "Resource",
    "InMemoryMCPTransport",
    "InMemoryMCPClient",
    "get_mcp_server",
    "FreeCADMCPServer",
    "get_freecad_mcp_server",
]
