#!/usr/bin/env python3
"""
代码质量检查脚本

运行各种代码质量检查工具：
- ruff: 代码检查
- black: 代码格式化

使用方法:
    python scripts/tools/code_check.py        # 运行所有检查
    python scripts/tools/code_check.py --fix   # 自动修复
    python scripts/tools/code_check.py --ruff  # 仅 ruff
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], name: str) -> bool:
    """运行命令并报告结果"""
    print(f"\n[{name}]")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.stdout:
        print(result.stdout[:2000])  # 限制输出长度
    if result.returncode != 0:
        print(f"[FAIL] {name}")
        return False
    else:
        print(f"[PASS] {name}")
        return True


def main():
    parser = argparse.ArgumentParser(description="Code quality check")
    parser.add_argument("--fix", action="store_true", help="Auto fix")
    parser.add_argument("--ruff", action="store_true", help="Only ruff")
    parser.add_argument("--black", action="store_true", help="Only black")
    parser.add_argument("--path", default="src", help="Check path")
    args = parser.parse_args()

    print("=== CAE-CLI Code Quality Check ===")

    # Run specific tool
    if args.ruff:
        cmd = ["python", "-m", "ruff", "check", args.path]
        if args.fix:
            cmd.append("--fix")
        run_command(cmd, "Ruff Check")
        return

    if args.black:
        cmd = ["python", "-m", "black", args.path, "--line-length", "120"]
        run_command(cmd, "Black Format")
        return

    # Run all checks
    results = []

    # 1. Ruff
    cmd = ["python", "-m", "ruff", "check", args.path]
    if args.fix:
        cmd.append("--fix")
    results.append(run_command(cmd, "Ruff Check"))

    # 2. Black
    cmd = ["python", "-m", "black", args.path, "--line-length", "120"]
    results.append(run_command(cmd, "Black Format"))

    # Summary
    print("\n=== Summary ===")
    if all(results):
        print("[OK] All checks passed!")
        return 0
    else:
        print("[FAIL] Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
