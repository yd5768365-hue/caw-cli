#!/usr/bin/env python3
"""
修复SSH主机密钥验证问题
专门解决 "Host key verification failed" 错误
"""

import asyncio
import sys
from pathlib import Path
from sw_helper.mcp import (
    get_ssh_mcp_server,
    InMemoryMCPTransport,
    InMemoryMCPClient,
)


async def fix_ssh_host_keys():
    """修复SSH主机密钥验证问题"""
    print("=" * 60)
    print("修复SSH主机密钥验证问题")
    print("=" * 60)
    print("此工具专门解决以下错误:")
    print("  - Host key verification failed")
    print("  - The authenticity of host 'github.com' can't be established")
    print("  - SSH连接时出现主机密钥验证错误")
    print()

    # 获取SSH增强的MCP服务器实例
    print("1. 初始化SSH MCP服务器...")
    try:
        ssh_server = get_ssh_mcp_server()
        transport = InMemoryMCPTransport(ssh_server.server)
        client = transport.create_client()

        # 连接客户端
        if await client.connect():
            print("   [OK] 客户端连接成功")
        else:
            print("   [FAIL] 客户端连接失败")
            return False
    except Exception as e:
        print(f"   [FAIL] 初始化失败: {e}")
        print("\n备用方案: 手动修复")
        print("运行以下命令修复主机密钥:")
        print("  ssh-keyscan github.com >> ~/.ssh/known_hosts")
        print("  ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts")
        print("  ssh-keyscan -t ecdsa github.com >> ~/.ssh/known_hosts")
        print("  ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts")
        return False

    try:
        # 2. 首先测试当前连接状态
        print("\n2. 测试当前SSH连接状态...")
        ssh_test = await client.call_tool("ssh_test_connection", {"host": "github.com"})

        ssh_output = ssh_test.get("ssh_command_result", {}).get("stderr", "").lower()
        ssh_success = ssh_test.get("success", False)

        if ssh_success:
            print("   [OK] SSH连接正常，无需修复")
            print(f"   状态: {ssh_test.get('interpretation', '连接成功')}")
            return True
        elif "host key verification failed" in ssh_output or "verification failed" in ssh_output:
            print("   [检测] 发现主机密钥验证问题")
        else:
            print(f"   [INFO] 其他SSH连接问题: {ssh_output[:100]}")

        # 3. 修复主机密钥
        print("\n3. 修复主机密钥验证...")
        fix_result = await client.call_tool("ssh_fix_host_key", {
            "host": "github.com",
            "key_types": ["rsa", "ecdsa", "ed25519"]
        })

        if fix_result.get("success"):
            print("   [OK] 主机密钥修复成功")

            keys_added = fix_result.get("keys_added", 0)
            total_scanned = fix_result.get("keys_scanned", 0)
            known_hosts_file = fix_result.get("known_hosts_file", "")

            print(f"   扫描密钥类型: {total_scanned} 个")
            print(f"   成功添加密钥: {keys_added} 个")
            print(f"   known_hosts文件: {known_hosts_file}")

            # 显示添加的密钥信息
            results = fix_result.get("results", [])
            for result in results:
                if result.get("success"):
                    key_type = result.get("key_type", "unknown")
                    print(f"     - {key_type}: 已添加")
                else:
                    key_type = result.get("key_type", "unknown")
                    error = result.get("error", "未知错误")
                    print(f"     - {key_type}: 失败 - {error[:50]}")

        else:
            print(f"   [FAIL] 主机密钥修复失败: {fix_result.get('error')}")
            print("\n手动修复方法:")
            print("1. 确保SSH目录存在:")
            print("   mkdir -p ~/.ssh")
            print("   chmod 700 ~/.ssh")
            print("\n2. 手动添加GitHub主机密钥:")
            print("   ssh-keyscan github.com >> ~/.ssh/known_hosts")
            print("   ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts")
            print("   ssh-keyscan -t ecdsa github.com >> ~/.ssh/known_hosts")
            print("   ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts")
            print("\n3. 验证修复:")
            print("   ssh -T git@github.com")
            return False

        # 4. 测试修复后的连接
        print("\n4. 测试修复后的SSH连接...")
        ssh_test2 = await client.call_tool("ssh_test_connection", {"host": "github.com"})

        test_after_fix = fix_result.get("test_after_fix", {})
        if test_after_fix.get("success") or ssh_test2.get("success"):
            print("   [OK] SSH连接测试成功!")
            output = test_after_fix.get("output", "") or ssh_test2.get("ssh_command_result", {}).get("stdout", "")
            error = test_after_fix.get("error", "") or ssh_test2.get("ssh_command_result", {}).get("stderr", "")

            if output:
                print(f"   输出: {output[:100]}")
            if error:
                print(f"   错误: {error[:100]}")

            print(f"   解释: {ssh_test2.get('interpretation', '连接成功')}")

            # 检查是否是预期的"认证失败"消息
            if "permission denied" in error.lower() or "successfully authenticated" in error.lower():
                print("\n   [INFO] 这是预期的结果!")
                print("   SSH连接已建立，但认证失败（因为我们没有提供密钥）")
                print("   这说明主机密钥验证问题已解决")
                print("   要完成GitHub SSH设置，您需要:")
                print("   1. 生成SSH密钥: ssh-keygen -t ed25519 -C \"your_email@example.com\"")
                print("   2. 添加公钥到GitHub: cat ~/.ssh/id_ed25519.pub")
                print("   3. 在GitHub设置中添加公钥")
                success = True
            else:
                success = ssh_test2.get("success", False)
        else:
            print("   [FAIL] SSH连接测试仍然失败")
            success = False

        # 5. 提供后续步骤
        print("\n" + "=" * 60)
        if success:
            print("修复成功!")
            print("=" * 60)
            print("\n后续步骤:")
            print("1. 生成SSH密钥（如果还没有）:")
            print("   ssh-keygen -t ed25519 -C \"your_email@example.com\"")
            print("\n2. 查看公钥内容:")
            print("   cat ~/.ssh/id_ed25519.pub")
            print("\n3. 将公钥添加到GitHub:")
            print("   - 访问 https://github.com/settings/keys")
            print("   - 点击 \"New SSH key\"")
            print("   - 粘贴公钥内容")
            print("\n4. 测试完整SSH连接:")
            print("   ssh -T git@github.com")
            print("\n5. 配置Git使用SSH:")
            print("   git remote set-url origin git@github.com:用户名/仓库名.git")
        else:
            print("修复部分成功或失败")
            print("=" * 60)
            print("\n建议:")
            print("1. 检查网络连接")
            print("2. 确保防火墙未阻挡SSH端口(22)")
            print("3. 尝试手动修复（见上面的命令）")
            print("4. 考虑使用HTTPS协议代替SSH")

        return success

    except Exception as e:
        print(f"\n[FAIL] 修复过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理
        print("\n清理资源...")
        await client.disconnect()
        print("修复任务结束。")


if __name__ == "__main__":
    try:
        success = asyncio.run(fix_ssh_host_keys())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n修复被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n修复过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)