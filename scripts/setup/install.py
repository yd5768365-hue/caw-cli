#!/usr/bin/env python
"""安装脚本 - 支持开发模式安装"""

import subprocess
import sys


def main():
    """运行pip install -e ."""
    print("正在安装 cae-cli...")

    # 使用pip安装当前包（开发模式）
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        capture_output=False,
        text=True,
    )

    if result.returncode == 0:
        print("\n✓ 安装成功!")
        print("\n可用命令:")
        print("  cae-cli --help")
        print("  sw-helper --help")
        print("\n快速开始:")
        print("  cae-cli material --list")
        print("  cae-cli info")
    else:
        print("\n✗ 安装失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
