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
from .github_server import GitHubRepoMCPServer, get_github_mcp_server
from .ssh_server import SSHEnhancedMCPServer, get_ssh_mcp_server
from .sqlite_server import SQLiteMCPServer, get_sqlite_mcp_server

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
    "GitHubRepoMCPServer",
    "get_github_mcp_server",
    "SSHEnhancedMCPServer",
    "get_ssh_mcp_server",
    "SQLiteMCPServer",
    "get_sqlite_mcp_server",
]
