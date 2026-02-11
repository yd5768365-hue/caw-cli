#!/usr/bin/env python3
"""
基本MCP服务器功能测试
"""

import sys
from pathlib import Path

def test_import():
    """测试导入功能"""
    print("1. 测试模块导入...")
    try:
        src_dir = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_dir))

        from sw_helper.mcp import get_github_mcp_server, get_mcp_server
        print("   SUCCESS: 模块导入成功")
        return True
    except Exception as e:
        print(f"   FAILED: 导入失败 - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_creation():
    """测试服务器创建"""
    print("2. 测试服务器创建...")
    try:
        from sw_helper.mcp import get_github_mcp_server, get_mcp_server

        # 获取MCP服务器
        server = get_mcp_server()
        print(f"   SUCCESS: MCP服务器创建成功")
        print(f"   服务器名称: {server.name}")
        print(f"   服务器版本: {server.version}")

        # 获取GitHub MCP服务器（这会注册所有工具）
        github_server = get_github_mcp_server()
        print(f"   SUCCESS: GitHub MCP服务器创建成功")
        print(f"   工具数量: {len(server.tools)}")

        # 列出所有工具
        print(f"   可用工具列表:")
        tool_names = list(server.tools.keys())
        for i, name in enumerate(tool_names, 1):
            tool = server.tools[name]
            print(f"     {i:2d}. {name}")
            print(f"         {tool.description}")

        return True
    except Exception as e:
        print(f"   FAILED: 服务器创建失败 - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_functionality():
    """测试工具功能"""
    print("3. 测试工具功能...")
    try:
        from sw_helper.mcp import get_github_mcp_server, get_mcp_server
        from sw_helper.mcp.core import InMemoryMCPTransport, InMemoryMCPClient
        import asyncio

        # 获取服务器
        github_server = get_github_mcp_server()
        transport = InMemoryMCPTransport(github_server.server)
        client = transport.create_client()

        async def test():
            await client.connect()

            # 测试工具列表
            tools = await client.list_tools()
            print(f"   通过客户端获取工具数量: {len(tools)}")

            # 测试仓库信息工具
            print(f"   测试 github_repo_info 工具...")
            result = await client.call_tool("github_repo_info", {})

            if result and result.get("success"):
                print(f"   仓库信息获取成功:")
                print(f"     仓库路径: {result.get('repo_path')}")
                print(f"     当前分支: {result.get('current_branch')}")
                return True
            else:
                print(f"   仓库信息获取失败: {result}")
                return False

        success = asyncio.run(test())
        return success

    except Exception as e:
        print(f"   FAILED: 工具功能测试失败 - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_run_script():
    """测试运行脚本"""
    print("4. 测试MCP服务器启动脚本...")
    try:
        import subprocess
        import time

        script_path = Path(__file__).parent / "run_github_mcp.py"

        # 尝试启动脚本（不测试stdio通信）
        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 等待一段时间
        time.sleep(2)

        # 检查进程是否仍在运行
        if proc.poll() is None:
            print("   SUCCESS: MCP服务器脚本启动成功（进程仍在运行）")
            proc.terminate()
            proc.wait(timeout=5)
            return True
        else:
            stdout, stderr = proc.communicate()
            print(f"   FAILED: 脚本启动失败")
            print(f"   退出码: {proc.returncode}")
            print(f"   stderr: {stderr[:500]}")
            return False

    except Exception as e:
        print(f"   FAILED: 脚本测试失败 - {e}")
        return False

def generate_config():
    """生成配置示例"""
    print("5. 生成Claude Code配置...")

    project_path = Path(__file__).parent
    config = {
        "mcpServers": {
            "github-cae-cli": {
                "command": "python",
                "args": [
                    str(project_path / "run_github_mcp.py")
                ],
                "env": {
                    "PYTHONPATH": str(project_path / "src")
                }
            }
        }
    }

    print("   配置示例 (JSON格式):")
    import json
    print(json.dumps(config, indent=2, ensure_ascii=False))

    print("\n   配置文件位置:")
    print("   Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("   Linux: ~/.config/Claude/claude_desktop_config.json")

    return True

def main():
    """主函数"""
    print("=" * 60)
    print("GitHub仓库管理MCP服务器 - 基本功能测试")
    print("=" * 60)

    tests = [
        ("模块导入", test_import),
        ("服务器创建", test_server_creation),
        ("工具功能", test_tool_functionality),
        ("启动脚本", test_run_script),
        ("配置生成", generate_config),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"   ERROR: 测试异常 - {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)

    all_passed = True
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {name:15} : {status}")
        if not success:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败，请查看上面的错误信息")

    print("\n下一步操作:")
    print("1. 将生成的配置添加到Claude Code配置文件中")
    print("2. 重启Claude Code")
    print("3. 运行 `/mcp` 命令检查MCP服务器是否加载")
    print("4. 运行 `/doctor` 命令诊断配置问题")
    print("5. 参考 MCP_CONFIGURATION.md 获取详细配置指南")

if __name__ == "__main__":
    main()