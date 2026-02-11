#!/usr/bin/env python3
"""
SQLite MCP服务器 - MCP协议修复版
基于简单MCP服务器的工作模式
"""
import sys
import json
import os
import io
import sqlite3
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

print("SQLite MCP服务器启动", file=sys.stderr)
print("协议版本: 2024-11-05", file=sys.stderr)

# 添加src目录到Python路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from sw_helper.mcp.sqlite_server import SQLiteMCPServer
    print("已导入SQLiteMCPServer", file=sys.stderr)
except ImportError as e:
    print(f"导入错误: {e}", file=sys.stderr)
    print("尝试直接从模块导入", file=sys.stderr)
    sys.exit(1)

# 数据库路径
db_path = Path(__file__).parent / "data" / "cae.db"
print(f"数据库路径: {db_path}", file=sys.stderr)

# 创建SQLite MCP服务器实例
sqlite_server = SQLiteMCPServer(db_path=str(db_path))

# 获取MCP服务器
try:
    from sw_helper.mcp import get_mcp_server
    server = get_mcp_server()
    print(f"已获取MCP服务器，工具数量: {len(server.tools)}", file=sys.stderr)
except:
    print("无法获取MCP服务器，创建简单的工具集", file=sys.stderr)
    # 创建简单的工具列表
    tools = [
        {
            "name": "sqlite_db_info",
            "description": "获取SQLite数据库基本信息",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "sqlite_query_materials",
            "description": "查询材料数据库",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "搜索关键词"}
                }
            }
        }
    ]

def handle_tool_call(tool_name, arguments):
    """处理工具调用"""
    if tool_name == "sqlite_db_info":
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # 获取表信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            # 获取数据库统计信息
            cursor.execute("SELECT COUNT(*) FROM materials")
            material_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM calculation_history")
            calc_count = cursor.fetchone()[0] if cursor.fetchone() else 0

            conn.close()

            return {
                "content": [{
                    "type": "text",
                    "text": f"SQLite数据库信息:\n- 数据库路径: {db_path}\n- 表数量: {len(tables)}\n- 材料记录: {material_count}\n- 计算记录: {calc_count}"
                }]
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"数据库查询错误: {e}"
                }]
            }

    elif tool_name == "sqlite_query_materials":
        try:
            search = arguments.get("search", "")
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            if search:
                cursor.execute("SELECT name, standard, elastic_modulus, yield_strength FROM materials WHERE name LIKE ?", (f"%{search}%",))
            else:
                cursor.execute("SELECT name, standard, elastic_modulus, yield_strength FROM materials LIMIT 10")

            materials = cursor.fetchall()
            conn.close()

            result_text = f"找到 {len(materials)} 个材料:\n"
            for mat in materials:
                result_text += f"- {mat[0]} ({mat[1]}): E={mat[2]}, σ_s={mat[3]}\n"

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
                    "text": f"材料查询错误: {e}"
                }]
            }

    else:
        return {
            "content": [{
                "type": "text",
                "text": f"未知工具: {tool_name}"
            }]
        }

print("SQLite MCP服务器准备就绪", file=sys.stderr)

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
                        "name": "sqlite-mcp-server",
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
                    if hasattr(sqlite_server, 'server') and hasattr(sqlite_server.server, 'tools'):
                        tools_list = []
                        for tool_name, tool_obj in sqlite_server.server.tools.items():
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
                        sqlite_server.server.handle_message(tool_call_message)
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