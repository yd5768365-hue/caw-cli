#!/usr/bin/env python3
"""
GitHub仓库管理MCP服务器 - stdio模式
用于Claude Code的MCP服务器集成
"""

import sys
import json
import asyncio
from pathlib import Path

# 修复Windows上的asyncio事件循环策略
if sys.platform == 'win32':
    # 尝试不同的策略组合
    try:
        # 首先尝试使用SelectorEventLoop（可能更稳定）
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        # 如果失败，回退到ProactorEventLoop
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 添加src目录到Python路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from sw_helper.mcp import get_github_mcp_server, get_mcp_server
from sw_helper.mcp.core import MCPMessage


class StdioMCPServer:
    """基于stdio的MCP服务器"""

    def __init__(self):
        self.server = get_mcp_server()
        # 确保GitHub MCP服务器被初始化（这会注册所有工具）
        self.github_server = get_github_mcp_server()
        print(f"[MCP Server] MCP服务器已启动", file=sys.stderr)
        print(f"[MCP Server] 工具数量: {len(self.server.tools)}", file=sys.stderr)
        print(f"[MCP Server] 仓库URL: https://github.com/yd5768365-hue/caw-cli.git", file=sys.stderr)

    async def run(self):
        """运行MCP服务器（stdio模式）"""
        print(f"[MCP Server] 等待MCP消息...", file=sys.stderr)

        # 使用asyncio处理stdio
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        writer_transport, writer_protocol = await loop.connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout
        )
        writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, loop)

        try:
            while True:
                # 读取一行JSON-RPC消息
                line = await reader.readline()
                if not line:
                    break

                line = line.decode('utf-8').strip()
                if not line:
                    continue

                print(f"[MCP Server] 收到消息: {line[:100]}...", file=sys.stderr)

                try:
                    # 解析消息
                    message_data = json.loads(line)
                    message = MCPMessage.from_dict(message_data)

                    # 处理消息
                    response = await self.server.handle_message(message)

                    # 发送响应
                    response_json = response.to_json()
                    writer.write(response_json.encode('utf-8'))
                    writer.write(b'\n')
                    await writer.drain()

                    print(f"[MCP Server] 发送响应: {response_json[:100]}...", file=sys.stderr)

                except json.JSONDecodeError as e:
                    print(f"[MCP Server] JSON解析错误: {e}", file=sys.stderr)
                    error_response = MCPMessage(
                        error={"code": -32700, "message": f"JSON解析错误: {e}"}
                    )
                    writer.write(error_response.to_json().encode('utf-8'))
                    writer.write(b'\n')
                    await writer.drain()

                except Exception as e:
                    print(f"[MCP Server] 处理错误: {e}", file=sys.stderr)
                    error_response = MCPMessage(
                        error={"code": -32603, "message": f"内部错误: {e}"}
                    )
                    writer.write(error_response.to_json().encode('utf-8'))
                    writer.write(b'\n')
                    await writer.drain()

        except asyncio.CancelledError:
            print(f"[MCP Server] 服务器被取消", file=sys.stderr)
        except Exception as e:
            print(f"[MCP Server] 服务器错误: {e}", file=sys.stderr)
        finally:
            print(f"[MCP Server] 服务器关闭", file=sys.stderr)
            writer.close()


def main():
    """主函数"""
    print(f"GitHub仓库管理MCP服务器", file=sys.stderr)
    print(f"版本: 1.0.0", file=sys.stderr)
    print(f"仓库: https://github.com/yd5768365-hue/caw-cli.git", file=sys.stderr)
    print(f"=" * 60, file=sys.stderr)

    # 创建并运行服务器
    server = StdioMCPServer()

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print(f"\n[MCP Server] 收到中断信号，关闭服务器", file=sys.stderr)
    except Exception as e:
        print(f"[MCP Server] 致命错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()