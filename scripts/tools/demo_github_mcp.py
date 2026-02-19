#!/usr/bin/env python3
"""
GitHub仓库管理MCP演示脚本
演示如何使用GitHub MCP服务器来管理 https://github.com/yd5768365-hue/caw-cli.git 仓库
"""

import asyncio
import json
from pathlib import Path
from sw_helper.mcp import (
    get_github_mcp_server,
    InMemoryMCPTransport,
    InMemoryMCPClient,
    get_mcp_server
)


async def demo_github_mcp():
    """演示GitHub MCP服务器的使用"""
    print("=" * 60)
    print("GitHub仓库管理MCP服务器演示")
    print("=" * 60)
    print(f"仓库URL: https://github.com/yd5768365-hue/caw-cli.git")
    print()

    # 1. 获取GitHub MCP服务器实例
    print("1. 初始化GitHub MCP服务器...")
    github_server = get_github_mcp_server()
    transport = InMemoryMCPTransport(github_server.server)
    client = transport.create_client()

    # 2. 连接客户端
    print("2. 连接MCP客户端...")
    if await client.connect():
        print("   ✓ 客户端连接成功")
    else:
        print("   ✗ 客户端连接失败")
        return

    # 3. 获取可用工具列表
    print("3. 获取可用工具列表...")
    tools = await client.list_tools()
    print(f"   可用工具数量: {len(tools)}")
    for i, tool in enumerate(tools[:5], 1):  # 只显示前5个
        print(f"   {i}. {tool.name}: {tool.description}")
    if len(tools) > 5:
        print(f"   ... 还有 {len(tools) - 5} 个工具")

    print("\n" + "=" * 60)
    print("开始演示工具调用")
    print("=" * 60)

    try:
        # 4. 获取仓库信息
        print("\n4. 获取仓库基本信息...")
        repo_info = await client.call_tool("github_repo_info", {})
        if repo_info.get("success"):
            print(f"   仓库路径: {repo_info.get('repo_path')}")
            print(f"   当前分支: {repo_info.get('current_branch')}")
            print(f"   未提交更改: {repo_info.get('uncommitted_changes')} 个文件")
            stats = repo_info.get("file_stats", {})
            print(f"   文件统计: {stats.get('total_files')} 个文件")
            print(f"             {stats.get('python_files')} 个Python文件")
            print(f"             {stats.get('markdown_files')} 个Markdown文件")
        else:
            print(f"   ✗ 获取仓库信息失败: {repo_info.get('error')}")

        # 5. 查看Git状态
        print("\n5. 查看Git状态...")
        git_status = await client.call_tool("github_git_status", {})
        if git_status.get("success"):
            print(f"   Git状态: {git_status.get('changed_files')} 个更改的文件")
            files = git_status.get("files", [])
            if files:
                print("   更改的文件列表:")
                for file_info in files[:5]:  # 只显示前5个
                    print(f"     - {file_info.get('status')} {file_info.get('path')}")
                if len(files) > 5:
                    print(f"     ... 还有 {len(files) - 5} 个文件")
        else:
            print(f"   ✗ 获取Git状态失败: {git_status.get('error')}")

        # 6. 列出README.md文件信息
        print("\n6. 读取README.md文件...")
        readme_content = await client.call_tool("github_read_file", {
            "file_path": "README.md",
            "encoding": "utf-8"
        })
        if readme_content.get("success"):
            content = readme_content.get("content", "")
            print(f"   README.md大小: {readme_content.get('size')} 字节")
            print(f"   文件行数: {len(content.splitlines())}")

            # 显示前几行
            lines = content.splitlines()[:5]
            print("   文件前5行:")
            for i, line in enumerate(lines, 1):
                print(f"     {i}. {line[:80]}{'...' if len(line) > 80 else ''}")
        else:
            print(f"   ✗ 读取README.md失败: {readme_content.get('error')}")

        # 7. 列出项目文件结构
        print("\n7. 列出项目文件结构...")
        file_list = await client.call_tool("github_list_files", {
            "directory": ".",
            "recursive": False,
            "pattern": "*"
        })
        if file_list.get("success"):
            files = file_list.get("files", [])
            print(f"   根目录下文件和目录: {len(files)} 个")

            # 分类显示
            dirs = [f for f in files if f.get("is_dir")]
            py_files = [f for f in files if f.get("name", "").endswith(".py")]
            md_files = [f for f in files if f.get("name", "").endswith(".md")]

            if dirs:
                print("   目录:")
                for d in dirs[:5]:
                    print(f"     - {d.get('name')}/")

            if py_files:
                print("   Python文件:")
                for f in py_files[:3]:
                    print(f"     - {f.get('name')}")

            if md_files:
                print("   Markdown文件:")
                for f in md_files[:3]:
                    print(f"     - {f.get('name')}")
        else:
            print(f"   ✗ 列出文件失败: {file_list.get('error')}")

        # 8. 查看Git提交历史
        print("\n8. 查看Git提交历史...")
        git_log = await client.call_tool("github_git_log", {
            "limit": 5,
            "format": "oneline"
        })
        if git_log.get("success"):
            commits = git_log.get("commits", [])
            print(f"   最近 {len(commits)} 次提交:")
            for i, commit in enumerate(commits, 1):
                hash_short = commit.get("hash", "")[:8]
                message = commit.get("message", "")
                print(f"     {i}. [{hash_short}] {message[:60]}{'...' if len(message) > 60 else ''}")
        else:
            print(f"   ✗ 获取Git日志失败: {git_log.get('error')}")

        # 9. 演示文件操作（创建一个临时测试文件）
        print("\n9. 演示文件操作...")
        test_file = "TEST_MCP_DEMO.md"

        # 创建测试文件
        print(f"   创建测试文件: {test_file}")
        create_result = await client.call_tool("github_create_file", {
            "file_path": test_file,
            "content": "# GitHub MCP服务器测试文件\n\n这是一个通过GitHub MCP服务器创建的测试文件。\n\n创建时间: 2026-02-12\n用途: 演示MCP文件操作功能\n",
            "encoding": "utf-8"
        })

        if create_result.get("success"):
            print(f"   ✓ 测试文件创建成功")

            # 读取刚刚创建的文件
            print(f"   读取测试文件...")
            read_result = await client.call_tool("github_read_file", {
                "file_path": test_file,
                "encoding": "utf-8"
            })

            if read_result.get("success"):
                content = read_result.get("content", "")
                print(f"   ✓ 文件读取成功，大小: {len(content)} 字符")

            # 删除测试文件
            print(f"   删除测试文件...")
            delete_result = await client.call_tool("github_delete_file", {
                "file_path": test_file,
                "force": False
            })

            if delete_result.get("success"):
                print(f"   ✓ 测试文件删除成功")
            else:
                print(f"   ✗ 测试文件删除失败: {delete_result.get('error')}")
        else:
            print(f"   ✗ 测试文件创建失败: {create_result.get('error')}")

        print("\n" + "=" * 60)
        print("演示完成!")
        print("=" * 60)

        # 10. 显示所有可用工具
        print("\n可用工具总结:")
        print("-" * 40)
        tools_by_category = {
            "文件操作": [
                "github_list_files", "github_read_file", "github_write_file",
                "github_create_file", "github_delete_file", "github_rename_file"
            ],
            "Git操作": [
                "github_git_status", "github_git_add", "github_git_commit",
                "github_git_push", "github_git_pull", "github_git_log",
                "github_git_create_branch", "github_git_checkout"
            ],
            "仓库信息": [
                "github_repo_info"
            ]
        }

        for category, tool_names in tools_by_category.items():
            print(f"{category}:")
            for tool_name in tool_names:
                # 查找工具描述
                tool_desc = ""
                for tool in tools:
                    if tool.name == tool_name:
                        tool_desc = tool.description
                        break
                print(f"  - {tool_name}: {tool_desc}")
            print()

    except Exception as e:
        print(f"\n✗ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理
        print("\n清理资源...")
        await client.disconnect()
        print("演示结束。")


if __name__ == "__main__":
    print("GitHub仓库管理MCP演示")
    print("仓库: https://github.com/yd5768365-hue/caw-cli.git")
    print()

    # 检查是否在Git仓库中
    repo_path = Path.cwd()
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        print("警告: 当前目录不是Git仓库!")
        print(f"当前目录: {repo_path}")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            print("退出演示")
            exit(1)

    # 运行演示
    asyncio.run(demo_github_mcp())