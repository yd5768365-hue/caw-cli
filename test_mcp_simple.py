#!/usr/bin/env python3
"""
Simple test for GitHub MCP server
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_basic():
    """Basic import test"""
    print("Testing GitHub MCP server import...")

    try:
        from sw_helper.mcp.github_server import GitHubRepoMCPServer, get_github_mcp_server
        print("SUCCESS: GitHubRepoMCPServer imported")

        # Try to create server instance
        print("Creating server instance...")
        server = get_github_mcp_server()
        print(f"SUCCESS: Server created with {len(server.server.tools)} tools")

        # List all tools
        print("\nAvailable tools:")
        for name, tool in server.server.tools.items():
            print(f"  - {name}: {tool.description}")

        return True

    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_call():
    """Test calling a tool"""
    print("\nTesting tool call...")

    try:
        from sw_helper.mcp import get_github_mcp_server
        from sw_helper.mcp.core import InMemoryMCPTransport, InMemoryMCPClient

        server = get_github_mcp_server()
        transport = InMemoryMCPTransport(server.server)
        client = transport.create_client()

        import asyncio

        async def test():
            await client.connect()
            print("Client connected")

            # Test repo info tool
            result = await client.call_tool("github_repo_info", {})
            print(f"Repo info result: {result.get('success', False)}")

            if result.get("success"):
                print(f"Repo path: {result.get('repo_path')}")
                print(f"Current branch: {result.get('current_branch')}")

            return result

        result = asyncio.run(test())
        return result.get("success", False)

    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GitHub MCP Server Test")
    print("=" * 60)

    # Check if we're in a git repo
    repo_path = Path.cwd()
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        print("WARNING: Not in a git repository!")
        print(f"Current dir: {repo_path}")

    # Run tests
    if test_basic():
        test_tool_call()

    print("\n" + "=" * 60)
    print("Test complete")
    print("=" * 60)