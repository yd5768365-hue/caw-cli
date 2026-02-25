#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装可选依赖脚本
用于安装 AI 功能所需的额外依赖（chromadb, sentence-transformers）
"""
import subprocess
import sys
import os


def install_ai_deps():
    """安装 AI 功能依赖"""
    print("=" * 50)
    print("安装 CAE-CLI AI 功能依赖")
    print("=" * 50)
    print("\n正在安装: chromadb, sentence-transformers...")
    print("这可能需要几分钟，请耐心等待...\n")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
        ])
        print("\n✅ AI 依赖安装成功!")
        print("\n现在你可以使用以下 AI 功能:")
        print("  - cae-cli ai generate")
        print("  - cae-cli ai suggest")
        print("  - cae-cli chat")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 安装失败: {e}")
        return False


def install_full_deps():
    """安装完整功能依赖"""
    print("=" * 50)
    print("安装 CAE-CLI 完整功能依赖")
    print("=" * 50)
    print("\n正在安装所有可选依赖...\n")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "-e", ".[full,ai,tools,optimize,ssh]",
        ])
        print("\n✅ 完整依赖安装成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 安装失败: {e}")
        return False


def check_current_deps():
    """检查当前已安装的依赖"""
    print("\n当前已安装的相关包:")
    packages = ["chromadb", "sentence-transformers", "torch", "transformers"]
    for pkg in packages:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", pkg],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"  ✅ {pkg}")
            else:
                print(f"  ❌ {pkg} (未安装)")
        except Exception:
            print(f"  ❌ {pkg} (未安装)")


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║           CAE-CLI 可选依赖安装程序                          ║
╠════════════════════════════════════════════════════════════╣
║  选项:                                                      ║
║    1. 安装 AI 功能依赖 (chromadb, sentence-transformers)   ║
║    2. 安装完整功能 (AI + 几何处理 + 优化 + SSH)             ║
║    3. 检查当前依赖状态                                       ║
║    0. 退出                                                  ║
╚════════════════════════════════════════════════════════════╝
    """)

    choice = input("请选择 [0-3]: ").strip()

    if choice == "1":
        install_ai_deps()
    elif choice == "2":
        install_full_deps()
    elif choice == "3":
        check_current_deps()
    elif choice == "0":
        print("再见!")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()
