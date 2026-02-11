#!/usr/bin/env python3
"""
使用MCP同步项目进度到GitHub
更新README.md并提交所有更改
"""

import asyncio
import json
from pathlib import Path
from sw_helper.mcp import (
    get_github_mcp_server,
    InMemoryMCPTransport,
    InMemoryMCPClient,
)

async def sync_project_with_mcp():
    """使用MCP服务器同步项目到GitHub"""
    print("=" * 60)
    print("使用MCP同步项目进度到GitHub")
    print("=" * 60)
    print(f"仓库: https://github.com/yd5768365-hue/caw-cli.git")
    print()

    # 1. 获取GitHub MCP服务器实例
    print("1. 初始化GitHub MCP服务器...")
    github_server = get_github_mcp_server()
    transport = InMemoryMCPTransport(github_server.server)
    client = transport.create_client()

    # 2. 连接客户端
    print("2. 连接MCP客户端...")
    if await client.connect():
        print("   [OK] 客户端连接成功")
    else:
        print("   [FAIL] 客户端连接失败")
        return

    try:
        # 3. 获取仓库信息
        print("\n3. 获取仓库基本信息...")
        repo_info = await client.call_tool("github_repo_info", {})
        if not repo_info.get("success"):
            print(f"   [FAIL] 获取仓库信息失败: {repo_info.get('error')}")
            return

        print(f"   仓库路径: {repo_info.get('repo_path')}")
        print(f"   当前分支: {repo_info.get('current_branch')}")
        print(f"   未提交更改: {repo_info.get('uncommitted_changes')} 个文件")

        # 4. 查看Git状态
        print("\n4. 查看Git状态...")
        git_status = await client.call_tool("github_git_status", {})
        if not git_status.get("success"):
            print(f"   [FAIL] 获取Git状态失败: {git_status.get('error')}")
            return

        changed_files = git_status.get("changed_files", 0)
        print(f"   有 {changed_files} 个更改的文件需要提交")

        files = git_status.get("files", [])
        if files:
            print("   更改的文件列表:")
            for file_info in files:
                status = file_info.get('status', 'unknown')
                path = file_info.get('path', 'unknown')
                print(f"     - {status:10} {path}")

        # 5. 更新README.md文件
        print("\n5. 读取并更新README.md文件...")
        # 先读取当前README内容
        readme_result = await client.call_tool("github_read_file", {
            "file_path": "README.md",
            "encoding": "utf-8"
        })

        if readme_result.get("success"):
            current_content = readme_result.get("content", "")
            print(f"   当前README.md大小: {len(current_content)} 字符")

            # 这里可以检查README是否已经更新
            # 由于我们已经在本地更新了README，直接使用本地文件内容
            local_readme_path = Path("README.md")
            if local_readme_path.exists():
                with open(local_readme_path, "r", encoding="utf-8") as f:
                    new_content = f.read()

                if current_content != new_content:
                    print("   README.md内容已更新，正在写入...")
                    write_result = await client.call_tool("github_write_file", {
                        "file_path": "README.md",
                        "content": new_content,
                        "encoding": "utf-8"
                    })

                    if write_result.get("success"):
                        print("   [OK] README.md更新成功")
                    else:
                        print(f"   [FAIL] README.md更新失败: {write_result.get('error')}")
                else:
                    print("   README.md内容未更改")
            else:
                print("   [FAIL] 本地README.md文件不存在")
        else:
            print(f"   [FAIL] 读取README.md失败: {readme_result.get('error')}")

        # 6. 添加所有更改的文件到Git暂存区
        print("\n6. 添加所有更改的文件到Git暂存区...")

        # 获取需要添加的文件列表（排除脚本自身）
        files_to_add = []
        for file_info in files:
            status = file_info.get('status', '')
            path = file_info.get('path', '')
            # 调试输出
            print(f"   调试: status='{status}', path='{path}'")

            # 只添加修改过的文件，不包括删除的文件，排除sync_with_mcp.py
            if status not in ['D', 'deleted'] and path != 'sync_with_mcp.py':
                files_to_add.append(path)

        if files_to_add:
            print(f"   添加 {len(files_to_add)} 个文件到暂存区:")
            for file_path in files_to_add:
                print(f"     - {file_path}")

            add_result = await client.call_tool("github_git_add", {
                "files": files_to_add
            })

            if add_result.get("success"):
                print("   [OK] 文件添加成功")
            else:
                error_msg = add_result.get('error', '未知错误')
                print(f"   [FAIL] 文件添加失败: {error_msg}")
                # 尝试使用通配符添加
                print("   尝试使用通配符添加...")
                add_result2 = await client.call_tool("github_git_add", {
                    "files": ["."]  # 添加所有更改
                })
                if add_result2.get("success"):
                    print("   [OK] 通配符添加成功")
                else:
                    print(f"   [FAIL] 通配符添加失败: {add_result2.get('error', '未知错误')}")
                    return
        else:
            print("   没有需要添加的文件")

        # 7. 创建提交
        print("\n7. 创建Git提交...")
        commit_message = """更新项目进度

- 新增AI学习助手功能：集成本地Ollama模型(qwen2.5:1.5b/phi3:mini) + RAG知识检索
- 实现RAG引擎：使用ChromaDB + sentence-transformers向量化knowledge/目录知识库
- 增强学习模式：支持多轮对话、自动服务启动、教学式回答
- 更新README.md：添加AI学习助手功能说明和使用示例
- 更新依赖：添加chromadb、sentence-transformers、requests到pyproject.toml
- 优化交互体验：箭头键导航、无闪烁界面、智能模型检测

🤖 通过MCP服务器自动同步
"""

        commit_result = await client.call_tool("github_git_commit", {
            "message": commit_message,
            "author": "Claude Code <noreply@anthropic.com>"
        })

        if commit_result.get("success"):
            commit_hash = commit_result.get("commit_hash", "")
            print(f"   [OK] 提交创建成功")
            print(f"   提交哈希: {commit_hash[:8]}")
            print(f"   提交消息: {commit_message.splitlines()[0]}")
        else:
            print(f"   [FAIL] 提交创建失败: {commit_result.get('error')}")
            return

        # 8. 推送到远程仓库
        print("\n8. 推送到远程GitHub仓库...")
        push_result = await client.call_tool("github_git_push", {
            "remote": "origin",
            "branch": "main"
        })

        if push_result.get("success"):
            print("   [OK] 推送成功")
        else:
            print(f"   [FAIL] 推送失败: {push_result.get('error')}")
            return

        # 9. 查看提交历史
        print("\n9. 查看最新的提交历史...")
        log_result = await client.call_tool("github_git_log", {
            "limit": 3,
            "format": "full"
        })

        if log_result.get("success"):
            commits = log_result.get("commits", [])
            print(f"   最近 {len(commits)} 次提交:")
            for i, commit in enumerate(commits, 1):
                hash_short = commit.get("hash", "")[:8]
                author = commit.get("author", "")
                message = commit.get("message", "")
                date = commit.get("date", "")
                print(f"   {i}. [{hash_short}] {author}")
                print(f"      消息: {message[:60]}{'...' if len(message) > 60 else ''}")
                print(f"      时间: {date}")
                print()

        print("\n" + "=" * 60)
        print("项目同步完成!")
        print("=" * 60)
        print("\n总结:")
        print(f"- 更新了 {len(files_to_add)} 个文件")
        print(f"- 创建了新的提交: {commit_message.splitlines()[0]}")
        print(f"- 已推送到GitHub仓库")
        print(f"- 查看仓库: https://github.com/yd5768365-hue/caw-cli.git")

    except Exception as e:
        print(f"\n[FAIL] 同步过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理
        print("\n清理资源...")
        await client.disconnect()
        print("同步任务结束。")

if __name__ == "__main__":
    # 检查是否在Git仓库中
    repo_path = Path.cwd()
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        print("错误: 当前目录不是Git仓库!")
        print(f"当前目录: {repo_path}")
        print("请在项目根目录运行此脚本")
        exit(1)

    # 运行同步任务
    asyncio.run(sync_project_with_mcp())