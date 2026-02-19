#!/usr/bin/env python3
"""
MCP服务器连接测试
"""
import subprocess
import time
import json
import sys
import os
from pathlib import Path

def test_server_stdio(script_name):
    """通过stdio测试MCP服务器"""
    print(f"\n测试 {script_name}...")

    script_path = Path(__file__).parent / script_name

    # 启动进程
    proc = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0
    )

    # 等待启动
    time.sleep(1.5)

    # 读取所有可用的stderr输出
    stderr_data = b""
    while True:
        chunk = proc.stderr.read(4096)
        if not chunk:
            break
        stderr_data += chunk

    # 尝试解码
    try:
        stderr_text = stderr_data.decode('utf-8')
    except:
        try:
            stderr_text = stderr_data.decode('gbk')
        except:
            stderr_text = str(stderr_data)

    print("服务器启动输出:")
    for line in stderr_text.split('\n'):
        if line.strip():
            print(f"  {line}")

    # 发送初始化消息
    init_msg = {
        "jsonrpc": "2.0",
        "id": "test-init",
        "method": "initialize",
        "params": {}
    }

    init_json = json.dumps(init_msg) + '\n'
    print(f"\n发送: {init_json.strip()}")

    proc.stdin.write(init_json.encode('utf-8'))
    proc.stdin.flush()

    # 等待响应
    time.sleep(1)

    # 读取响应
    stdout_data = b""
    while True:
        chunk = proc.stdout.read(4096)
        if not chunk:
            break
        stdout_data += chunk

    try:
        stdout_text = stdout_data.decode('utf-8')
    except:
        try:
            stdout_text = stdout_data.decode('gbk')
        except:
            stdout_text = str(stdout_data)

    print(f"收到响应: {stdout_text}")

    # 尝试解析JSON
    for line in stdout_text.split('\n'):
        line = line.strip()
        if line:
            try:
                data = json.loads(line)
                print(f"\n解析成功!")
                print(f"JSON-RPC版本: {data.get('jsonrpc')}")
                print(f"ID: {data.get('id')}")
                if 'result' in data:
                    print(f"结果: {json.dumps(data['result'], indent=2, ensure_ascii=False)}")
                if 'error' in data:
                    print(f"错误: {json.dumps(data['error'], indent=2, ensure_ascii=False)}")
                break
            except json.JSONDecodeError:
                continue

    # 发送工具列表请求
    tools_msg = {
        "jsonrpc": "2.0",
        "id": "test-tools",
        "method": "tools/list",
        "params": {}
    }

    tools_json = json.dumps(tools_msg) + '\n'
    print(f"\n发送: {tools_json.strip()}")

    proc.stdin.write(tools_json.encode('utf-8'))
    proc.stdin.flush()

    time.sleep(1)

    # 读取工具列表响应
    tools_data = b""
    while True:
        chunk = proc.stdout.read(4096)
        if not chunk:
            break
        tools_data += chunk

    try:
        tools_text = tools_data.decode('utf-8')
    except:
        try:
            tools_text = tools_data.decode('gbk')
        except:
            tools_text = str(tools_data)

    print(f"工具列表响应: {tools_text}")

    # 清理
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except:
        proc.kill()

    return True

def main():
    print("=" * 60)
    print("MCP服务器连接测试")
    print("=" * 60)

    os.chdir(Path(__file__).parent)

    # 测试SQLite MCP服务器
    test_server_stdio("run_sqlite_mcp.py")

    # 测试GitHub MCP服务器
    test_server_stdio("run_github_mcp_fixed.py")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()