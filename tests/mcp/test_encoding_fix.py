#!/usr/bin/env python3
"""
测试编码修复方案
"""
import sys
import io

# 测试不同编码设置方法
print("测试1: 当前编码设置")
print(f"stdout编码: {sys.stdout.encoding}")
print(f"stderr编码: {sys.stderr.encoding}")

print("\n测试2: 设置PYTHONIOENCODING环境变量")
# 这个方法需要在启动Python前设置

print("\n测试3: 使用io.TextIOWrapper重新包装stdio")
try:
    # 重新包装stdout为UTF-8
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='replace',
        line_buffering=True
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer,
        encoding='utf-8',
        errors='replace',
        line_buffering=True
    )
    print(f"重新包装后 - stdout编码: {sys.stdout.encoding}")
    print(f"重新包装后 - stderr编码: {sys.stderr.encoding}")
    print("测试输出: Hello 世界! 测试UTF-8编码")
except Exception as e:
    print(f"重新包装失败: {e}")

print("\n测试4: 使用二进制模式")
print("二进制模式需要不同的处理方法")

print("\n测试5: 使用环境变量方法")
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
# 注意：这个需要在脚本开始时设置