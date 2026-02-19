#!/usr/bin/env python3
"""
简单的MCP服务器测试
"""
import sys
import json
import io
import os

# 修复编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True, write_through=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True, write_through=True)
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    except:
        pass

print("简单的MCP服务器测试", file=sys.stderr)
print("等待输入...", file=sys.stderr)

try:
    while True:
        line = sys.stdin.readline()
        if not line:
            print("EOF", file=sys.stderr)
            break

        line = line.strip()
        if not line:
            continue

        print(f"收到: {line}", file=sys.stderr)

        # 尝试解析为JSON
        try:
            data = json.loads(line)
            print(f"解析为JSON: {data}", file=sys.stderr)

            # 简单回应
            response = {
                "jsonrpc": "2.0",
                "id": data.get("id", "unknown"),
                "result": {"message": "Hello from test server"}
            }
            print(json.dumps(response))
            sys.stdout.flush()

        except json.JSONDecodeError as e:
            print(f"不是JSON: {e}", file=sys.stderr)
            response = {
                "jsonrpc": "2.0",
                "id": "error",
                "error": {"code": -32700, "message": "Parse error"}
            }
            print(json.dumps(response))
            sys.stdout.flush()

except KeyboardInterrupt:
    print("中断", file=sys.stderr)
except Exception as e:
    print(f"错误: {e}", file=sys.stderr)