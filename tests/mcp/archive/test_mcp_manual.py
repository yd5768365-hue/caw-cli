#!/usr/bin/env python3
"""
手动测试MCP服务器连接
"""
import subprocess
import time
import json
import sys
import os
from pathlib import Path

def test_sqlite_mcp():
    """测试SQLite MCP服务器"""
    print("测试SQLite MCP服务器启动...")

    script_path = Path(__file__).parent / "run_sqlite_mcp.py"

    try:
        # 启动MCP服务器进程
        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding='utf-8'
        )

        # 给服务器一点时间启动
        time.sleep(2)

        # 读取stderr输出（服务器的启动消息）
        stderr_output = ""
        while True:
            line = proc.stderr.readline()
            if not line:
                break
            stderr_output += line
            print(f"STDERR: {line.rstrip()}")

        print(f"服务器启动输出: {stderr_output[:500]}")

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

        # 读取响应（带超时）
        start_time = time.time()
        response = None
        while time.time() - start_time < 5:  # 5秒超时
            line = proc.stdout.readline()
            if line:
                response = line
                break
            time.sleep(0.1)

        if response:
            print(f"收到响应: {response}")
            try:
                data = json.loads(response)
                print(f"解析成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
        else:
            print("未收到响应（超时）")

        # 停止进程
        proc.terminate()
        proc.wait(timeout=5)
        print("SQLite MCP服务器测试完成")
        return True

    except Exception as e:
        print(f"SQLite MCP服务器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_github_mcp():
    """测试GitHub MCP服务器"""
    print("\n测试GitHub MCP服务器启动...")

    script_path = Path(__file__).parent / "run_github_mcp_fixed.py"

    try:
        # 启动MCP服务器进程
        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding='utf-8'
        )

        # 给服务器一点时间启动
        time.sleep(2)

        # 读取stderr输出
        stderr_output = ""
        while True:
            line = proc.stderr.readline()
            if not line:
                break
            stderr_output += line
            print(f"STDERR: {line.rstrip()}")

        print(f"服务器启动输出: {stderr_output[:500]}")

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

        # 读取响应（带超时）
        start_time = time.time()
        response = None
        while time.time() - start_time < 5:
            line = proc.stdout.readline()
            if line:
                response = line
                break
            time.sleep(0.1)

        if response:
            print(f"收到响应: {response}")
            try:
                data = json.loads(response)
                print(f"解析成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
        else:
            print("未收到响应（超时）")

        # 停止进程
        proc.terminate()
        proc.wait(timeout=5)
        print("GitHub MCP服务器测试完成")
        return True

    except Exception as e:
        print(f"GitHub MCP服务器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("MCP服务器手动测试")
    print("=" * 60)

    # 切换到项目根目录
    os.chdir(Path(__file__).parent)

    # 测试SQLite MCP服务器
    print("\n[测试1] SQLite MCP服务器")
    if test_sqlite_mcp():
        print("[OK] SQLite MCP服务器测试通过")
    else:
        print("[ERROR] SQLite MCP服务器测试失败")

    # 测试GitHub MCP服务器
    print("\n[测试2] GitHub MCP服务器")
    if test_github_mcp():
        print("[OK] GitHub MCP服务器测试通过")
    else:
        print("[ERROR] GitHub MCP服务器测试失败")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()