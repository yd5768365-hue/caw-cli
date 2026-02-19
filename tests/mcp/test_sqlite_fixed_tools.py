#!/usr/bin/env python3
"""
测试SQLite MCP修复版本的工具功能
"""
import sys
import json
import subprocess
import time
import threading
import queue

def test_mcp_server():
    """测试MCP服务器工具功能"""

    print("测试SQLite MCP修复版本...")

    # 启动服务器
    proc = subprocess.Popen(
        [sys.executable, "-u", "run_sqlite_mcp_protocol_fixed.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        bufsize=1
    )

    # 等待服务器启动
    time.sleep(1)

    def send_message(method, params=None, msg_id="test-1"):
        """发送消息到服务器"""
        message = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method,
            "params": params or {}
        }
        proc.stdin.write(json.dumps(message) + "\n")
        proc.stdin.flush()
        return msg_id

    def read_response(timeout=3):
        """读取响应"""
        start = time.time()
        while time.time() - start < timeout:
            line = proc.stdout.readline()
            if line:
                return line.strip()
        return None

    # 1. 测试初始化
    print("1. 测试初始化...")
    send_message("initialize", {
        "protocolVersion": "2024-11-05",
        "clientInfo": {"name": "test", "version": "1.0"}
    }, "init-1")

    # 读取初始化响应和通知
    init_response = read_response()
    if init_response:
        print(f"初始化响应: {init_response[:100]}...")

    notification = read_response()
    if notification:
        print(f"初始化通知: {notification[:100]}...")

    # 2. 测试工具列表
    print("\n2. 测试工具列表...")
    send_message("tools/list", {}, "tools-1")

    tools_response = read_response()
    if tools_response:
        print(f"工具列表响应: {tools_response[:200]}...")
        try:
            data = json.loads(tools_response)
            tools = data.get("result", {}).get("tools", [])
            print(f"找到 {len(tools)} 个工具")
            for tool in tools[:3]:  # 只显示前3个
                print(f"  - {tool.get('name')}: {tool.get('description', '无描述')}")
        except:
            print("无法解析工具列表")

    # 3. 测试数据库信息工具
    print("\n3. 测试数据库信息工具...")
    send_message("tools/call", {
        "name": "sqlite_db_info",
        "arguments": {}
    }, "call-1")

    db_info_response = read_response()
    if db_info_response:
        print(f"数据库信息响应: {db_info_response[:200]}...")

    # 清理
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except:
        proc.kill()

    print("\n测试完成")

if __name__ == "__main__":
    test_mcp_server()