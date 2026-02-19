#!/usr/bin/env python3
"""
测试修复版MCP服务器
"""
import subprocess
import time
import json
import sys
import os
from pathlib import Path

def test_fixed_server():
    script_path = Path(__file__).parent / "run_sqlite_mcp_fixed2.py"

    # 启动进程
    proc = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        text=True,
        encoding='utf-8'
    )

    # 等待启动
    time.sleep(2)

    # 读取stderr
    stderr_lines = []
    while True:
        line = proc.stderr.readline()
        if not line:
            break
        stderr_lines.append(line)
        print(f"STDERR: {line.rstrip()}")

    # 发送初始化消息
    init_msg = {
        "jsonrpc": "2.0",
        "id": "test-1",
        "method": "initialize",
        "params": {}
    }

    print(f"\n发送: {json.dumps(init_msg)}")
    proc.stdin.write(json.dumps(init_msg) + '\n')
    proc.stdin.flush()

    # 等待响应
    time.sleep(1)

    # 读取响应
    response = proc.stdout.readline()
    print(f"收到: {response}")

    # 发送工具列表请求
    tools_msg = {
        "jsonrpc": "2.0",
        "id": "test-2",
        "method": "tools/list",
        "params": {}
    }

    print(f"\n发送: {json.dumps(tools_msg)}")
    proc.stdin.write(json.dumps(tools_msg) + '\n')
    proc.stdin.flush()

    time.sleep(1)

    # 读取工具列表响应
    response = proc.stdout.readline()
    print(f"收到: {response}")

    # 停止进程
    proc.terminate()
    proc.wait(timeout=2)

if __name__ == "__main__":
    test_fixed_server()