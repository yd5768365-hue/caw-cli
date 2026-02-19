#!/usr/bin/env python3
"""
使用SSH增强的MCP同步项目进度到GitHub
提供更稳定的SSH连接和网络诊断
"""

import asyncio
import json
from pathlib import Path
from sw_helper.mcp import (
    get_ssh_mcp_server,
    InMemoryMCPTransport,
    InMemoryMCPClient,
)


async def sync_project_with_ssh_mcp():
    """使用SSH增强的MCP服务器同步项目到GitHub"""
    print("=" * 70)
    print("使用SSH增强的MCP同步项目进度到GitHub")
    print("=" * 70)
    print(f"仓库: https://github.com/yd5768365-hue/caw-cli.git")
    print(f"SSH仓库: git@github.com:yd5768365-hue/caw-cli.git")
    print()

    # 1. 获取SSH增强的MCP服务器实例
    print("1. 初始化SSH增强MCP服务器...")
    ssh_server = get_ssh_mcp_server()
    transport = InMemoryMCPTransport(ssh_server.server)
    client = transport.create_client()

    # 2. 连接客户端
    print("2. 连接MCP客户端...")
    if await client.connect():
        print("   [OK] 客户端连接成功")
    else:
        print("   [FAIL] 客户端连接失败")
        return

    try:
        # 3. 网络诊断
        print("\n3. 执行网络诊断...")
        network_result = await client.call_tool("network_diagnostic", {
            "targets": ["github.com", "8.8.8.8"]
        })

        if network_result.get("success"):
            print("   [OK] 网络诊断完成")
            for target_result in network_result.get("targets", []):
                target = target_result.get("target")
                ping_success = target_result.get("ping", {}).get("success", False)
                status = "可达" if ping_success else "不可达"
                print(f"     - {target}: {status}")
        else:
            print(f"   [WARN] 网络诊断失败: {network_result.get('error')}")

        # 4. 检查SSH配置
        print("\n4. 检查SSH配置...")
        ssh_check = await client.call_tool("ssh_check_config", {})

        if ssh_check.get("success"):
            print("   [OK] SSH配置检查完成")
            key_files = ssh_check.get("key_files", [])
            if key_files:
                print(f"     找到 {len(key_files)} 个SSH密钥:")
                for key in key_files:
                    print(f"     - {key['name']}: {'可用' if key['private_exists'] else '缺失'}")
            else:
                print("     [WARN] 未找到SSH密钥")
        else:
            print(f"   [WARN] SSH配置检查失败: {ssh_check.get('error')}")

        # 5. 检查Git远程配置
        print("\n5. 检查Git远程配置...")
        remote_check = await client.call_tool("git_check_remote", {"remote_name": "origin"})

        if remote_check.get("success"):
            current_protocol = remote_check.get("protocol", "unknown")
            is_ssh = remote_check.get("is_ssh", False)

            print(f"     当前远程: {remote_check.get('url', '未知')}")
            print(f"     协议: {current_protocol}")
            print(f"     状态: {'已配置SSH（推荐）' if is_ssh else '使用HTTPS'}")

            # 如果不是SSH，建议切换
            if not is_ssh:
                print("     [INFO] 建议切换到SSH协议以获得更稳定的连接")
                switch_choice = input("     是否切换到SSH协议？(y/N): ").strip().lower()
                if switch_choice == 'y':
                    print("     正在切换到SSH协议...")
                    switch_result = await client.call_tool("ssh_configure_remote", {"remote_name": "origin"})
                    if switch_result.get("success"):
                        print("     [OK] 已切换到SSH协议")
                    else:
                        print(f"     [FAIL] 切换失败: {switch_result.get('error')}")
        else:
            print(f"   [WARN] 远程配置检查失败: {remote_check.get('error')}")

        # 6. 测试SSH连接
        print("\n6. 测试SSH连接到GitHub...")
        ssh_test = await client.call_tool("ssh_test_connection", {"host": "github.com"})

        if ssh_test.get("success"):
            print("   [OK] SSH连接测试成功")
            interpretation = ssh_test.get("interpretation", "")
            if interpretation:
                print(f"     解释: {interpretation}")
        else:
            print(f"   [WARN] SSH连接测试失败")

            # 检查是否是主机密钥验证问题
            ssh_output = ssh_test.get("ssh_command_result", {}).get("stderr", "").lower()
            if "host key verification failed" in ssh_output or "verification failed" in ssh_output:
                print(f"     检测到主机密钥验证问题，尝试自动修复...")

                # 尝试修复主机密钥
                fix_result = await client.call_tool("ssh_fix_host_key", {
                    "host": "github.com",
                    "key_types": ["rsa", "ecdsa", "ed25519"]
                })

                if fix_result.get("success"):
                    print(f"     [OK] 主机密钥修复成功")
                    keys_added = fix_result.get("keys_added", 0)
                    print(f"     已添加 {keys_added} 个主机密钥")

                    # 重新测试连接
                    print(f"     重新测试SSH连接...")
                    ssh_test2 = await client.call_tool("ssh_test_connection", {"host": "github.com"})

                    if ssh_test2.get("success"):
                        print(f"     [OK] SSH连接测试现在成功")
                    else:
                        print(f"     [WARN] SSH连接仍然失败，可能需要其他配置")
                else:
                    print(f"     [FAIL] 主机密钥修复失败: {fix_result.get('error')}")
            else:
                print(f"     可能需要生成SSH密钥或检查网络连接")

        # 7. 获取仓库信息（使用GitHub MCP服务器）
        print("\n7. 获取仓库基本信息...")
        # 由于SSH服务器没有直接提供仓库信息工具，我们需要切换到GitHub MCP服务器
        from sw_helper.mcp import get_github_mcp_server
        github_server = get_github_mcp_server()
        github_transport = InMemoryMCPTransport(github_server.server)
        github_client = github_transport.create_client()
        await github_client.connect()

        repo_info = await github_client.call_tool("github_repo_info", {})
        if repo_info.get("success"):
            print(f"     仓库路径: {repo_info.get('repo_path')}")
            print(f"     当前分支: {repo_info.get('current_branch')}")
            print(f"     未提交更改: {repo_info.get('uncommitted_changes')} 个文件")
        else:
            print(f"   [FAIL] 获取仓库信息失败")

        # 8. 查看Git状态
        print("\n8. 查看Git状态...")
        git_status = await github_client.call_tool("github_git_status", {})
        if not git_status.get("success"):
            print(f"   [FAIL] 获取Git状态失败")
            await github_client.disconnect()
            return

        changed_files = git_status.get("changed_files", 0)
        print(f"     有 {changed_files} 个更改的文件需要提交")

        files = git_status.get("files", [])
        if files:
            print("     更改的文件列表:")
            for file_info in files:
                status = file_info.get('status', 'unknown')
                path = file_info.get('path', 'unknown')
                print(f"       - {status:10} {path}")

        # 9. 添加所有更改的文件到Git暂存区
        print("\n9. 添加所有更改的文件到Git暂存区...")
        files_to_add = []
        for file_info in files:
            status = file_info.get('status', '')
            path = file_info.get('path', '')
            # 只添加修改过的文件，不包括删除的文件，排除同步脚本自身
            if status not in ['D', 'deleted'] and path not in ['sync_with_mcp.py', 'sync_with_ssh_mcp.py']:
                files_to_add.append(path)

        if files_to_add:
            print(f"     添加 {len(files_to_add)} 个文件到暂存区:")
            for file_path in files_to_add:
                print(f"       - {file_path}")

            add_result = await github_client.call_tool("github_git_add", {
                "files": files_to_add
            })

            if add_result.get("success"):
                print("     [OK] 文件添加成功")
            else:
                error_msg = add_result.get('error', '未知错误')
                print(f"     [FAIL] 文件添加失败: {error_msg}")
                # 尝试使用通配符添加
                print("     尝试使用通配符添加...")
                add_result2 = await github_client.call_tool("github_git_add", {
                    "files": ["."]  # 添加所有更改
                })
                if add_result2.get("success"):
                    print("     [OK] 通配符添加成功")
                else:
                    print(f"     [FAIL] 通配符添加失败: {add_result2.get('error', '未知错误')}")
                    await github_client.disconnect()
                    return
        else:
            print("     没有需要添加的文件")

        # 10. 创建提交
        print("\n10. 创建Git提交...")
        commit_message = """更新项目进度

- 新增SSH增强的MCP服务器：提供更稳定的SSH连接和网络诊断
- 添加SSH密钥管理、网络诊断、SSH连接测试工具
- 支持SSH协议切换，提供更稳定的Git操作
- 更新同步脚本，支持SSH增强的同步流程

🤖 通过SSH增强的MCP服务器自动同步
"""

        commit_result = await github_client.call_tool("github_git_commit", {
            "message": commit_message,
            "author": "Claude Code <noreply@anthropic.com>"
        })

        if commit_result.get("success"):
            commit_hash = commit_result.get("commit_hash", "")
            print(f"     [OK] 提交创建成功")
            print(f"     提交哈希: {commit_hash[:8]}")
            print(f"     提交消息: {commit_message.splitlines()[0]}")
        else:
            print(f"     [FAIL] 提交创建失败: {commit_result.get('error')}")
            await github_client.disconnect()
            return

        # 11. 使用SSH推送（更稳定）
        print("\n11. 使用SSH推送Git提交（更稳定）...")
        ssh_push_result = await client.call_tool("ssh_git_push", {
            "remote": "origin",
            "branch": "main",
            "timeout": 60  # 增加超时时间
        })

        if ssh_push_result.get("success"):
            print("     [OK] SSH推送成功")
        else:
            print(f"     [FAIL] SSH推送失败")

            # 提供诊断信息
            if "diagnostics" in ssh_push_result:
                diag = ssh_push_result["diagnostics"]
                print(f"     诊断信息:")

                # 检查网络状态
                network_status = diag.get("network_status", {})
                if network_status.get("success"):
                    print(f"       网络: 正常")
                else:
                    print(f"       网络: 异常")

                # 显示建议
                suggestions = diag.get("suggestions", [])
                if suggestions:
                    print(f"       建议:")
                    for suggestion in suggestions:
                        print(f"         - {suggestion}")

            # 尝试使用传统的GitHub MCP推送作为备选
            print("     尝试使用传统推送作为备选...")
            push_result = await github_client.call_tool("github_git_push", {
                "remote": "origin",
                "branch": "main"
            })

            if push_result.get("success"):
                print("     [OK] 传统推送成功")
            else:
                print(f"     [FAIL] 传统推送失败: {push_result.get('error')}")
                await github_client.disconnect()
                return

        # 12. 查看提交历史
        print("\n12. 查看最新的提交历史...")
        log_result = await github_client.call_tool("github_git_log", {
            "limit": 3,
            "format": "full"
        })

        if log_result.get("success"):
            commits = log_result.get("commits", [])
            print(f"     最近 {len(commits)} 次提交:")
            for i, commit in enumerate(commits, 1):
                hash_short = commit.get("hash", "")[:8]
                author = commit.get("author", "")
                message = commit.get("message", "")
                date = commit.get("date", "")
                print(f"     {i}. [{hash_short}] {author}")
                print(f"         消息: {message[:60]}{'...' if len(message) > 60 else ''}")
                print(f"         时间: {date}")
                print()

        await github_client.disconnect()

        print("\n" + "=" * 70)
        print("项目同步完成!")
        print("=" * 70)
        print("\n总结:")
        print(f"- 网络诊断: {'通过' if network_result.get('success') else '警告'}")
        print(f"- SSH配置: {'就绪' if ssh_check.get('success') and ssh_check.get('key_files') else '需要配置'}")
        print(f"- Git协议: {remote_check.get('protocol', '未知')}")
        print(f"- 更新文件: {len(files_to_add)} 个")
        print(f"- 提交消息: {commit_message.splitlines()[0]}")
        print(f"- 推送方式: SSH增强" if ssh_push_result.get('success') else "- 推送方式: 传统HTTPS")
        print(f"- 查看仓库: https://github.com/yd5768365-hue/caw-cli.git")

    except Exception as e:
        print(f"\n[FAIL] 同步过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理
        print("\n清理资源...")
        await client.disconnect()
        print("SSH增强同步任务结束。")


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
    asyncio.run(sync_project_with_ssh_mcp())