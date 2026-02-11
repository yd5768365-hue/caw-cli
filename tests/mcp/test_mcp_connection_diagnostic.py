#!/usr/bin/env python3
"""
MCP连接诊断工具
测试MCP服务器是否能正确响应初始化消息
"""
import sys
import json
import subprocess
import time
import threading
import queue

def test_mcp_server(script_path, server_name):
    """测试MCP服务器连接"""
    print(f"测试 {server_name} MCP服务器...")
    print(f"脚本路径: {script_path}")

    # 启动MCP服务器进程
    proc = subprocess.Popen(
        [sys.executable, "-u", script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # 发送初始化消息
    init_message = {
        "jsonrpc": "2.0",
        "id": "test-init",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {
                "name": "Claude Code",
                "version": "2.1.39"
            }
        }
    }

    print(f"发送初始化消息...")
    proc.stdin.write(json.dumps(init_message) + "\n")
    proc.stdin.flush()

    # 读取响应（带超时）
    def read_output():
        try:
            line = proc.stdout.readline()
            return line
        except:
            return None

    # 等待响应
    response = None
    for i in range(10):  # 10秒超时
        line = read_output()
        if line:
            response = line.strip()
            break
        time.sleep(1)

    # 检查stderr输出
    stderr_output = ""
    try:
        stderr_output = proc.stderr.read(1024)
    except:
        pass

    # 清理进程
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except:
        proc.kill()

    # 分析结果
    print(f"\n诊断结果:")
    print(f"标准输出: {response}")
    print(f"标准错误: {stderr_output[:200]}")

    if response:
        try:
            response_data = json.loads(response)
            if "result" in response_data:
                print(f"✓ 服务器响应正常")
                return True
            elif "error" in response_data:
                print(f"✗ 服务器返回错误: {response_data['error']}")
                return False
        except json.JSONDecodeError as e:
            print(f"✗ 响应不是有效的JSON: {e}")
            return False
    else:
        print("✗ 服务器没有响应")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("MCP服务器连接诊断工具")
    print("=" * 60)

    # 测试SQLite MCP服务器
    sqlite_ok = test_mcp_server("run_sqlite_mcp_fixed2.py", "SQLite")

    print("\n" + "=" * 60)

    # 测试GitHub MCP服务器
    github_ok = test_mcp_server("run_github_mcp_fixed.py", "GitHub")

    print("\n" + "=" * 60)
    print("总结:")
    print(f"SQLite MCP服务器: {'✓ 通过' if sqlite_ok else '✗ 失败'}")
    print(f"GitHub MCP服务器: {'✓ 通过' if github_ok else '✗ 失败'}")

    if not (sqlite_ok or github_ok):
        print("\n建议:")
        print("1. 检查MCP服务器脚本是否包含正确的initialize处理")
        print("2. 确保服务器脚本使用正确的stdio处理")
        print("3. 在Windows上尝试使用简单的同步stdio处理")
        print("4. 检查编码问题（输出中有乱码）")

if __name__ == "__main__":
    main()