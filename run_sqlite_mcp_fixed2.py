#!/usr/bin/env python3
"""
SQLite数据库MCP服务器 - 修复Windows stdio问题
使用同步读取，异步处理
"""
import sys
import json
import asyncio
import os
from pathlib import Path
import threading
import queue

# 修复Windows上的asyncio事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 添加src目录到Python路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from sw_helper.mcp import get_sqlite_mcp_server, get_mcp_server
from sw_helper.mcp.core import MCPMessage


class FixedStdioMCPServer:
    """修复Windows stdio问题的MCP服务器"""

    def __init__(self, db_path: str = None):
        self.server = get_mcp_server()
        self.sqlite_server = get_sqlite_mcp_server(db_path)
        print(f"[SQLite MCP Server] SQLite MCP服务器已启动", file=sys.stderr)
        print(f"[SQLite MCP Server] 工具数量: {len(self.server.tools)}", file=sys.stderr)
        print(f"[SQLite MCP Server] 数据库路径: {self.sqlite_server.db_path}", file=sys.stderr)

        # 消息队列
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.running = True

    async def handle_input(self):
        """异步处理输入消息"""
        while self.running:
            try:
                # 从队列获取消息（带超时）
                try:
                    message_data = self.input_queue.get(timeout=0.1)
                except queue.Empty:
                    await asyncio.sleep(0.01)
                    continue

                # 处理消息
                message = MCPMessage.from_dict(message_data)
                response = await self.server.handle_message(message)

                # 将响应放入输出队列
                self.output_queue.put(response)

            except Exception as e:
                print(f"[SQLite MCP Server] 处理错误: {e}", file=sys.stderr)
                error_response = MCPMessage(
                    error={"code": -32603, "message": f"内部错误: {e}"}
                )
                self.output_queue.put(error_response)

    def sync_read_stdin(self):
        """同步读取stdin（在单独线程中运行）"""
        print(f"[SQLite MCP Server] 开始读取stdin...", file=sys.stderr)
        while self.running:
            try:
                # 读取一行
                line = sys.stdin.readline()
                if not line:
                    # EOF
                    print(f"[SQLite MCP Server] stdin结束", file=sys.stderr)
                    break

                line = line.strip()
                if not line:
                    continue

                print(f"[SQLite MCP Server] 收到消息: {line[:100]}...", file=sys.stderr)

                # 解析JSON
                try:
                    message_data = json.loads(line)
                    self.input_queue.put(message_data)
                except json.JSONDecodeError as e:
                    print(f"[SQLite MCP Server] JSON解析错误: {e}", file=sys.stderr)
                    error_response = MCPMessage(
                        error={"code": -32700, "message": f"JSON解析错误: {e}"}
                    )
                    self.output_queue.put(error_response)

            except Exception as e:
                print(f"[SQLite MCP Server] 读取错误: {e}", file=sys.stderr)
                if not self.running:
                    break

    def sync_write_stdout(self):
        """同步写入stdout（在单独线程中运行）"""
        print(f"[SQLite MCP Server] 开始写入stdout...", file=sys.stderr)
        while self.running:
            try:
                # 从输出队列获取响应
                try:
                    response = self.output_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                # 发送响应
                response_json = response.to_json()
                sys.stdout.write(response_json + '\n')
                sys.stdout.flush()

                print(f"[SQLite MCP Server] 发送响应: {response_json[:100]}...", file=sys.stderr)

            except Exception as e:
                print(f"[SQLite MCP Server] 写入错误: {e}", file=sys.stderr)
                if not self.running:
                    break

    async def run_async(self):
        """运行异步部分"""
        # 启动处理任务
        handle_task = asyncio.create_task(self.handle_input())

        # 等待直到停止
        while self.running:
            await asyncio.sleep(0.1)

        # 取消任务
        handle_task.cancel()
        try:
            await handle_task
        except asyncio.CancelledError:
            pass

    def run(self):
        """主运行方法"""
        print(f"[SQLite MCP Server] 启动修复版服务器...", file=sys.stderr)

        # 启动读取线程
        read_thread = threading.Thread(target=self.sync_read_stdin, daemon=True)
        read_thread.start()

        # 启动写入线程
        write_thread = threading.Thread(target=self.sync_write_stdout, daemon=True)
        write_thread.start()

        try:
            # 运行异步事件循环
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            print(f"\n[SQLite MCP Server] 收到中断信号", file=sys.stderr)
        except Exception as e:
            print(f"[SQLite MCP Server] 错误: {e}", file=sys.stderr)
        finally:
            self.running = False
            print(f"[SQLite MCP Server] 服务器关闭", file=sys.stderr)


def main():
    """主函数"""
    print(f"SQLite数据库MCP服务器 (修复版)", file=sys.stderr)
    print(f"版本: 1.0.0", file=sys.stderr)
    print(f"工作目录: {os.getcwd()}", file=sys.stderr)
    print(f"=" * 60, file=sys.stderr)

    # 解析命令行参数
    db_path = None
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        print(f"[INFO] 使用指定数据库路径: {db_path}", file=sys.stderr)

    # 创建并运行服务器
    server = FixedStdioMCPServer(db_path)
    server.run()


if __name__ == "__main__":
    main()