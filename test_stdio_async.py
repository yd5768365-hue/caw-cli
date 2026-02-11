#!/usr/bin/env python3
"""
测试Windows上的asyncio stdio
"""
import sys
import asyncio
import json

async def async_main():
    print("测试asyncio stdio...", file=sys.stderr)

    # 创建StreamReader
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    # 创建StreamWriter
    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, asyncio.get_event_loop())

    print("等待输入...", file=sys.stderr)

    try:
        while True:
            # 读取一行
            line_bytes = await reader.readline()
            if not line_bytes:
                break

            line = line_bytes.decode('utf-8').strip()
            print(f"收到: {line}", file=sys.stderr)

            # 回显
            response = {"echo": line, "status": "ok"}
            writer.write(json.dumps(response).encode('utf-8'))
            writer.write(b'\n')
            await writer.drain()

    except asyncio.CancelledError:
        print("取消", file=sys.stderr)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
    finally:
        writer.close()
        print("关闭", file=sys.stderr)

def main():
    # Windows事件循环策略
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n中断", file=sys.stderr)

if __name__ == "__main__":
    main()