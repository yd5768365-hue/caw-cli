#!/usr/bin/env python3
"""
GitHub MCP服务器 - MCP协议修复版
基于简单MCP服务器的工作模式
"""
import sys
import json
import os
import io
from pathlib import Path

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

print("GitHub MCP服务器启动", file=sys.stderr)
print("协议版本: 2024-11-05", file=sys.stderr)

# 添加src目录到Python路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from sw_helper.mcp.github_server import GitHubRepoMCPServer
    print("已导入GitHubRepoMCPServer", file=sys.stderr)
except ImportError as e:
    print(f"导入错误: {e}", file=sys.stderr)
    print("尝试直接从模块导入", file=sys.stderr)
    sys.exit(1)

# 创建GitHub MCP服务器实例
github_server = GitHubRepoMCPServer()

print("GitHub MCP服务器准备就绪", file=sys.stderr)

# 简单的工具列表作为回退
tools = [
    {
        "name": "github_repo_info",
        "description": "获取GitHub仓库基本信息",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "github_list_files",
        "description": "列出仓库中的文件",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "目录路径"}
            }
        }
    }
]

def handle_tool_call(tool_name, arguments):
    """处理工具调用（简单回退实现）"""
    if tool_name == "github_repo_info":
        return {
            "content": [{
                "type": "text",
                "text": f"GitHub仓库信息:\n- 仓库路径: {github_server.repo_path}\n- 仓库URL: {github_server.repo_url}"
            }]
        }
    elif tool_name == "github_list_files":
        path = arguments.get("path", ".")
        try:
            target_path = github_server.repo_path / path
            if target_path.exists() and target_path.is_dir():
                files = list(target_path.iterdir())
                result_text = f"目录 {path} 中的文件 ({len(files)} 个):\n"
                for f in files[:20]:  # 限制数量
                    result_text += f"- {f.name}\n"
                if len(files) > 20:
                    result_text += f"... 和 {len(files) - 20} 个更多文件"
            else:
                result_text = f"路径不存在或不是目录: {path}"

            return {
                "content": [{
                    "type": "text",
                    "text": result_text
                }]
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"文件列表错误: {e}"
                }]
            }
    else:
        return {
            "content": [{
                "type": "text",
                "text": f"未知工具: {tool_name}"
            }]
        }

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
                        "name": "github-mcp-server",
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
                # 返回工具列表 - 使用实际的工具列表
                try:
                    # 从服务器获取工具列表
                    if hasattr(github_server, 'server') and hasattr(github_server.server, 'tools'):
                        tools_list = []
                        for tool_name, tool_obj in github_server.server.tools.items():
                            tools_list.append({
                                "name": tool_name,
                                "description": getattr(tool_obj, 'description', 'No description'),
                                "inputSchema": getattr(tool_obj, 'input_schema', {"type": "object", "properties": {}})
                            })
                        response["result"] = {"tools": tools_list}
                    else:
                        # 回退到简单工具列表
                        response["result"] = {"tools": tools}
                except:
                    # 回退到简单工具列表
                    response["result"] = {"tools": tools}

            elif method == "tools/call":
                # 处理工具调用
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                print(f"调用工具: {tool_name}, 参数: {arguments}", file=sys.stderr)

                try:
                    # 尝试使用服务器的handle_message方法
                    from sw_helper.mcp.core import MCPMessage
                    tool_call_message = MCPMessage(
                        id=message_id,
                        method="tools/call",
                        params={"name": tool_name, "arguments": arguments}
                    )

                    # 使用异步处理
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    tool_response = loop.run_until_complete(
                        github_server.server.handle_message(tool_call_message)
                    )

                    response["result"] = tool_response.result
                    loop.close()

                except Exception as e:
                    print(f"服务器工具调用失败: {e}", file=sys.stderr)
                    # 回退到简单处理
                    result = handle_tool_call(tool_name, arguments)
                    response["result"] = result

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