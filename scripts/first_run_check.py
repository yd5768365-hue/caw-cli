#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首次运行检查 - 验证AI模型依赖并提示用户安装
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def check_sentence_transformers():
    """检查sentence-transformers模型"""
    try:
        from sentence_transformers import SentenceTransformer
        print("[INFO] 检查 sentence-transformers...")
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"[WARNING] sentence-transformers 检查异常: {e}")
        return False

def check_ollama():
    """检查Ollama服务"""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_chromadb():
    """检查ChromaDB"""
    try:
        import chromadb
        return True
    except ImportError:
        return False

def show_installation_guide():
    """显示安装指南"""
    print("\n" + "="*60)
    print("  CAE-CLI AI功能依赖安装指南")
    print("="*60)
    print("\n[重要] CAE-CLI 需要以下AI组件才能使用完整功能:")
    print("\n1. sentence-transformers: pip install sentence-transformers")
    print("\n2. ChromaDB: pip install chromadb==0.4.0")
    print("\n3. Ollama: https://ollama.com/")
    print("\n" + "="*60)

def main():
    print("\n[CAE-CLI] 首次运行检查")
    deps_ok = True
    try:
        import click
        import rich
        import yaml
        import numpy
        print("✓ 基础依赖正常")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        deps_ok = False

    if not deps_ok:
        print("请运行: pip install -e .")

    print("\n" + "="*60)
    if deps_ok:
        print("✅ CAE-CLI 准备就绪!")
    else:
        print("❌ 缺少必要依赖")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
