#!/usr/bin/env python3
"""
测试SSH增强的MCP服务器
"""

import asyncio
from sw_helper.mcp import (
    get_ssh_mcp_server,
    InMemoryMCPTransport,
    InMemoryMCPClient,
)


async def test_ssh_mcp():
    """测试SSH MCP服务器"""
    print("测试SSH增强的MCP服务器...")
    print("=" * 50)

    # 获取SSH增强的MCP服务器实例
    ssh_server = get_ssh_mcp_server()
    transport = InMemoryMCPTransport(ssh_server.server)
    client = transport.create_client()

    # 连接客户端
    if await client.connect():
        print("[OK] 客户端连接成功")
    else:
        print("[FAIL] 客户端连接失败")
        return

    try:
        # 1. 测试SSH配置检查
        print("\n1. 测试SSH配置检查...")
        ssh_check = await client.call_tool("ssh_check_config", {})
        if ssh_check.get("success"):
            print("   [OK] SSH配置检查成功")
            key_files = ssh_check.get("key_files", [])
            print(f"   找到 {len(key_files)} 个SSH密钥文件")
        else:
            print(f"   [WARN] SSH配置检查失败: {ssh_check.get('error')}")

        # 2. 测试网络诊断
        print("\n2. 测试网络诊断...")
        network_result = await client.call_tool("network_diagnostic", {
            "targets": ["github.com"]
        })
        if network_result.get("success"):
            print("   [OK] 网络诊断成功")
            for target_result in network_result.get("targets", []):
                target = target_result.get("target")
                ping_success = target_result.get("ping", {}).get("success", False)
                print(f"     - {target}: {'可达' if ping_success else '不可达'}")
        else:
            print(f"   [WARN] 网络诊断失败: {network_result.get('error')}")

        # 3. 测试Git远程检查
        print("\n3. 测试Git远程检查...")
        remote_check = await client.call_tool("git_check_remote", {"remote_name": "origin"})
        if remote_check.get("success"):
            print("   [OK] Git远程检查成功")
            print(f"     当前协议: {remote_check.get('protocol', '未知')}")
            print(f"     远程URL: {remote_check.get('url', '未知')}")
        else:
            print(f"   [WARN] Git远程检查失败: {remote_check.get('error')}")

        # 4. 测试SSH连接测试
        print("\n4. 测试SSH连接测试...")
        ssh_test = await client.call_tool("ssh_test_connection", {"host": "github.com"})
        if ssh_test.get("success") is not None:
            print("   [OK] SSH连接测试完成")
            print(f"     结果: {'成功' if ssh_test.get('success') else '失败'}")
            interpretation = ssh_test.get("interpretation", "")
            if interpretation:
                print(f"     解释: {interpretation}")
        else:
            print(f"   [WARN] SSH连接测试失败")

        # 5. 测试获取SSH公钥（如果有）
        print("\n5. 测试获取SSH公钥...")
        ssh_check_result = await client.call_tool("ssh_check_config", {})
        key_files = ssh_check_result.get("key_files", [])
        if key_files:
            key_name = key_files[0]["name"]
            pubkey_result = await client.call_tool("ssh_get_public_key", {"key_file": key_name})
            if pubkey_result.get("success"):
                print(f"   [OK] 获取公钥成功: {key_name}")
                content_preview = pubkey_result.get("content", "")[:50]
                print(f"     预览: {content_preview}...")
            else:
                print(f"   [WARN] 获取公钥失败: {pubkey_result.get('error')}")
        else:
            print("   [INFO] 没有找到SSH密钥文件")

        print("\n" + "=" * 50)
        print("SSH MCP服务器测试完成")

    except Exception as e:
        print(f"\n[FAIL] 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理
        await client.disconnect()
        print("测试结束。")


if __name__ == "__main__":
    asyncio.run(test_ssh_mcp())