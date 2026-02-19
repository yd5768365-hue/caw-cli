#!/usr/bin/env python3
"""
完整MCP协议测试
模拟Claude Code连接MCP服务器的完整过程
"""
import sys
import json
import subprocess
import time
import threading
import queue

class MCPClientTester:
    """MCP客户端测试器"""

    def __init__(self, server_cmd):
        self.server_cmd = server_cmd
        self.process = None
        self.message_id = 0

    def start_server(self):
        """启动MCP服务器进程"""
        print(f"启动MCP服务器: {self.server_cmd}")

        self.process = subprocess.Popen(
            self.server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            bufsize=1
        )

        # 启动读取线程
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()

        def read_output(pipe, queue):
            while True:
                line = pipe.readline()
                if not line:
                    break
                queue.put(line)

        self.stdout_thread = threading.Thread(
            target=read_output, args=(self.process.stdout, self.output_queue), daemon=True
        )
        self.stderr_thread = threading.Thread(
            target=read_output, args=(self.process.stderr, self.error_queue), daemon=True
        )

        self.stdout_thread.start()
        self.stderr_thread.start()

        # 等待服务器启动
        time.sleep(1)

        # 收集启动日志
        stderr_output = []
        while not self.error_queue.empty():
            try:
                stderr_output.append(self.error_queue.get_nowait())
            except queue.Empty:
                break

        print(f"服务器启动日志:")
        for line in stderr_output:
            print(f"  STDERR: {line.rstrip()}")

        return True

    def send_message(self, method, params=None):
        """发送消息到服务器"""
        self.message_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": str(self.message_id),
            "method": method,
            "params": params or {}
        }

        message_json = json.dumps(message)
        print(f"发送消息: {message_json}")

        self.process.stdin.write(message_json + "\n")
        self.process.stdin.flush()

        return str(self.message_id)

    def receive_response(self, timeout=5):
        """接收响应"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                line = self.output_queue.get(timeout=0.1)
                print(f"收到响应: {line.rstrip()}")

                try:
                    response = json.loads(line)
                    return response
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"原始响应: {line}")
                    continue

            except queue.Empty:
                continue

        print(f"超时：{timeout}秒内未收到响应")
        return None

    def test_initialize(self):
        """测试初始化协议"""
        print("\n=== 测试初始化协议 ===")

        # 发送initialize消息
        msg_id = self.send_message("initialize", {
            "protocolVersion": "2024-11-05",
            "clientInfo": {
                "name": "Claude Code",
                "version": "2.1.39"
            }
        })

        # 接收响应
        response = self.receive_response()
        if not response:
            print("初始化失败：没有响应")
            return False

        if response.get("id") != msg_id:
            print(f"ID不匹配：期望 {msg_id}，实际 {response.get('id')}")

        if "error" in response:
            print(f"初始化错误：{response['error']}")
            return False

        if "result" not in response:
            print("初始化失败：没有result字段")
            return False

        result = response["result"]
        print(f"初始化成功！")
        print(f"  协议版本: {result.get('protocolVersion')}")
        print(f"  服务器信息: {result.get('serverInfo', {})}")
        print(f"  能力: {result.get('capabilities', {})}")

        return True

    def test_tools_list(self):
        """测试工具列表"""
        print("\n=== 测试工具列表 ===")

        msg_id = self.send_message("tools/list")

        response = self.receive_response()
        if not response:
            print("工具列表失败：没有响应")
            return False

        if "error" in response:
            print(f"工具列表错误：{response['error']}")
            return False

        if "result" not in response:
            print("工具列表失败：没有result字段")
            return False

        result = response["result"]
        tools = result.get("tools", [])
        print(f"工具列表成功！共 {len(tools)} 个工具")

        for tool in tools:
            print(f"  - {tool.get('name')}: {tool.get('description', '无描述')}")

        return len(tools) > 0

    def test_ping(self):
        """测试ping"""
        print("\n=== 测试ping ===")

        msg_id = self.send_message("ping")

        response = self.receive_response()
        if not response:
            print("ping失败：没有响应")
            return False

        if "error" in response:
            print(f"ping错误：{response['error']}")
            return False

        print("ping成功！")
        return True

    def cleanup(self):
        """清理"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except:
                self.process.kill()

def test_server(server_name, server_cmd):
    """测试特定服务器"""
    print(f"\n{'='*60}")
    print(f"测试 {server_name} MCP服务器")
    print(f"命令: {server_cmd}")
    print(f"{'='*60}")

    tester = MCPClientTester(server_cmd)

    try:
        # 启动服务器
        if not tester.start_server():
            print("服务器启动失败")
            return False

        # 测试初始化
        if not tester.test_initialize():
            print("初始化测试失败")
            return False

        # 测试工具列表
        if not tester.test_tools_list():
            print("工具列表测试失败")
            return False

        # 测试ping
        if not tester.test_ping():
            print("ping测试失败")
            return False

        print(f"\n✓ {server_name} MCP服务器所有测试通过！")
        return True

    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        tester.cleanup()

def main():
    """主函数"""
    print("MCP服务器完整协议测试")

    # 测试SQLite MCP服务器
    sqlite_cmd = [
        sys.executable, "-u", "run_mcp_with_encoding_fix.py", "run_sqlite_mcp_fixed2.py"
    ]
    sqlite_ok = test_server("SQLite", sqlite_cmd)

    # 测试GitHub MCP服务器
    github_cmd = [
        sys.executable, "-u", "run_mcp_with_encoding_fix.py", "run_github_mcp_fixed.py"
    ]
    github_ok = test_server("GitHub", github_cmd)

    print(f"\n{'='*60}")
    print("测试总结:")
    print(f"SQLite MCP服务器: {'✓ 通过' if sqlite_ok else '✗ 失败'}")
    print(f"GitHub MCP服务器: {'✓ 通过' if github_ok else '✗ 失败'}")

    if not sqlite_ok and not github_ok:
        print("\n常见问题排查:")
        print("1. 检查MCP服务器脚本是否包含正确的消息处理")
        print("2. 确保服务器响应正确的JSON-RPC格式")
        print("3. 检查编码问题（应该使用UTF-8）")
        print("4. 验证服务器启动后不会立即退出")
        print("5. 检查是否需要特定的工作目录")

if __name__ == "__main__":
    main()