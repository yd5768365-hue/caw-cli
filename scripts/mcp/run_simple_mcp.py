#!/usr/bin/env python3
"""
极简MCP服务器 - 同步版本
用于诊断MCP连接问题
"""
import sys
import json
import os
import io

# 修复Windows编码问题
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True, write_through=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True, write_through=True)
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    except:
        pass

print("极简MCP服务器启动", file=sys.stderr)
print("协议版本: 2024-11-05", file=sys.stderr)

# 简单的工具列表
tools = [
    {
        "name": "test_tool",
        "description": "测试工具",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "测试消息"}
            }
        }
    }
]

try:
    while True:
        # 读取一行
        line = sys.stdin.readline()
        if not line:
            print("EOF", file=sys.stderr)
            break

        line = line.strip()
        if not line:
            continue

        print(f"收到消息: {line[:100]}...", file=sys.stderr)

        try:
            data = json.loads(line)
            message_id = data.get("id")
            method = data.get("method")
            params = data.get("params", {})

            print(f"方法: {method}, ID: {message_id}", file=sys.stderr)

            response = {"jsonrpc": "2.0", "id": message_id}

            if method == "initialize":
                # 处理初始化请求
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": "simple-mcp-server",
                        "version": "1.0.0"
                    }
                }
                # 发送initialized通知
                notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                }
                print(json.dumps(notification))
                sys.stdout.flush()
                print("已发送initialized通知", file=sys.stderr)

            elif method == "tools/list":
                # 返回工具列表
                response["result"] = {"tools": tools}

            elif method == "tools/call":
                # 处理工具调用
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "test_tool":
                    message = arguments.get("message", "默认消息")
                    response["result"] = {
                        "content": [{
                            "type": "text",
                            "text": f"测试工具被调用: {message}"
                        }]
                    }
                else:
                    response["error"] = {
                        "code": -32601,
                        "message": f"工具未找到: {tool_name}"
                    }

            elif method == "ping":
                response["result"] = {}

            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"未知方法: {method}"
                }

            # 发送响应
            response_json = json.dumps(response)
            print(response_json)
            sys.stdout.flush()
            print(f"发送响应: {response_json[:100]}...", file=sys.stderr)

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}", file=sys.stderr)
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"JSON解析错误: {e}"}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            print(f"处理错误: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)

except KeyboardInterrupt:
    print("服务器被中断", file=sys.stderr)
except Exception as e:
    print(f"服务器错误: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)