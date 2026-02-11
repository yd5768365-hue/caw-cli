#!/usr/bin/env python3
"""
MCP服务器编码修复包装器
解决Windows上Python stdio编码问题
"""
import sys
import io
import os
import subprocess

def fix_stdio_encoding():
    """修复stdio编码为UTF-8"""
    # 方法1: 重新包装stdio（对于当前进程）
    try:
        # 重新包装stdout为UTF-8
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding='utf-8',
            errors='replace',
            line_buffering=True,
            write_through=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding='utf-8',
            errors='replace',
            line_buffering=True,
            write_through=True
        )
        # 重新打开stdin
        sys.stdin = io.TextIOWrapper(
            sys.stdin.buffer,
            encoding='utf-8',
            errors='replace'
        )
        return True
    except Exception as e:
        print(f"重新包装stdio失败: {e}", file=sys.stderr)
        return False

def run_mcp_server(server_script, *args):
    """运行MCP服务器脚本"""
    print(f"[MCP包装器] 启动MCP服务器: {server_script}", file=sys.stderr)

    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'

    # 构建命令行
    cmd = [sys.executable, "-u", server_script] + list(args)

    # 启动进程
    proc = subprocess.Popen(
        cmd,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=env,
        bufsize=0  # 无缓冲
    )

    # 等待进程结束
    try:
        proc.wait()
    except KeyboardInterrupt:
        print(f"\n[MCP包装器] 收到中断信号，终止服务器", file=sys.stderr)
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except:
            proc.kill()
    except Exception as e:
        print(f"[MCP包装器] 错误: {e}", file=sys.stderr)
        return 1

    return proc.returncode

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python run_mcp_with_encoding_fix.py <mcp_server_script> [args...]", file=sys.stderr)
        print("例如: python run_mcp_with_encoding_fix.py run_sqlite_mcp_fixed2.py", file=sys.stderr)
        sys.exit(1)

    server_script = sys.argv[1]
    args = sys.argv[2:]

    print(f"[MCP包装器] MCP服务器编码修复包装器", file=sys.stderr)
    print(f"[MCP包装器] Python版本: {sys.version}", file=sys.stderr)
    print(f"[MCP包装器] 默认编码: {sys.getdefaultencoding()}", file=sys.stderr)
    print(f"[MCP包装器] 原始stdout编码: {sys.stdout.encoding}", file=sys.stderr)

    # 修复编码
    if fix_stdio_encoding():
        print(f"[MCP包装器] 已修复stdio编码为UTF-8", file=sys.stderr)
        print(f"[MCP包装器] 修复后stdout编码: {sys.stdout.encoding}", file=sys.stderr)
    else:
        print(f"[MCP包装器] 警告：无法修复stdio编码", file=sys.stderr)

    # 运行MCP服务器
    return run_mcp_server(server_script, *args)

if __name__ == "__main__":
    sys.exit(main())