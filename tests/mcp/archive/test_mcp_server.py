#!/usr/bin/env python3
"""
测试MCP服务器功能
"""

import subprocess
import time
import json
import sys
from pathlib import Path

def test_mcp_server_start():
    """测试MCP服务器能否启动"""
    print("测试MCP服务器启动...")

    script_path = Path(__file__).parent / "run_github_mcp.py"

    try:
        # 启动MCP服务器进程
        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # 给服务器一点时间启动
        time.sleep(2)

        # 发送初始化消息
        init_msg = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "initialize",
            "params": {}
        }

        print(f"发送初始化消息: {json.dumps(init_msg)}")
        proc.stdin.write(json.dumps(init_msg) + '\n')
        proc.stdin.flush()

        # 读取响应
        response = proc.stdout.readline()
        print(f"收到响应: {response}")

        # 发送工具列表请求
        tools_msg = {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "tools/list",
            "params": {}
        }

        print(f"发送工具列表请求: {json.dumps(tools_msg)}")
        proc.stdin.write(json.dumps(tools_msg) + '\n')
        proc.stdin.flush()

        # 读取响应
        response = proc.stdout.readline()
        print(f"收到响应: {response}")

        # 解析响应
        if response:
            try:
                data = json.loads(response)
                tools = data.get("result", {}).get("tools", [])
                print(f"找到 {len(tools)} 个工具")
                for tool in tools[:5]:  # 只显示前5个
                    print(f"  - {tool.get('name')}: {tool.get('description')}")
                if len(tools) > 5:
                    print(f"  ... 还有 {len(tools) - 5} 个工具")
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")

        # 停止进程
        proc.terminate()
        proc.wait(timeout=5)

        print("MCP服务器测试完成")
        return True

    except Exception as e:
        print(f"MCP服务器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_claude_code_config():
    """测试Claude Code配置"""
    print("\n生成Claude Code配置示例...")

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

    print("Claude Code配置 (JSON格式):")
    print(json.dumps(config, indent=2, ensure_ascii=False))

    print(f"\n配置文件路径建议:")
    print(f"Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print(f"macOS/Linux: ~/.config/Claude/claude_desktop_config.json")

    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("GitHub仓库管理MCP服务器测试")
    print("=" * 60)

    # 测试1: MCP服务器启动
    print("\n[测试1] MCP服务器功能测试")
    if test_mcp_server_start():
        print("[OK] MCP服务器功能测试通过")
    else:
        print("[ERROR] MCP服务器功能测试失败")

    # 测试2: Claude Code配置
    print("\n[测试2] Claude Code配置生成")
    test_claude_code_config()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

    print("\n下一步:")
    print("1. 将生成的配置添加到Claude Code配置文件中")
    print("2. 重启Claude Code")
    print("3. 运行 `/mcp` 命令验证MCP服务器是否加载")
    print("4. 运行 `/doctor` 命令诊断配置问题")

if __name__ == "__main__":
    main()