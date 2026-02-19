#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAE-CLI 打包脚本 - 使用 PyInstaller 创建可执行文件

注意：此脚本不包含AI模型文件（sentence-transformers、Ollama模型等）
首次运行时会提示用户下载或安装必要组件。

使用方法：
    python build_exe.py              # 构建可执行文件到 dist/ 目录
    python build_exe.py --onefile    # 构建单个可执行文件
    python build_exe.py --clean      # 清理构建文件
    python build_exe.py --gui        # 构建GUI版本（包含PySide6）
    python build_exe.py --web        # 构建Web美化版本（包含QWebEngineView）
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


def check_dependencies():
    """检查打包依赖"""
    try:
        import PyInstaller
        print(f"[INFO] PyInstaller 版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("[ERROR] 请先安装 PyInstaller: pip install pyinstaller")
        return False


def collect_data_files():
    """收集数据文件"""
    data_files = []

    # data/ 目录
    if DATA_DIR.exists():
        for item in DATA_DIR.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(PROJECT_ROOT)
                data_files.append((str(item), str(rel_path.parent)))

    # knowledge/ 目录
    if KNOWLEDGE_DIR.exists():
        for item in KNOWLEDGE_DIR.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(PROJECT_ROOT)
                data_files.append((str(item), str(rel_path.parent)))

    # 添加首次运行检查脚本
    first_run_script = PROJECT_ROOT / "scripts" / "first_run_check.py"
    if not first_run_script.exists():
        create_first_run_check_script()

    if first_run_script.exists():
        data_files.append((str(first_run_script), "scripts"))

    return data_files


def create_first_run_check_script():
    """创建首次运行检查脚本"""
    script_content = r'''#!/usr/bin/env python3
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
'''

    scripts_dir = PROJECT_ROOT / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    script_path = scripts_dir / "first_run_check.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"[INFO] 首次运行检查脚本已创建: {script_path}")


def build_exe(onefile=False, clean=False, gui=False, web=False):
    """构建可执行文件

    Args:
        onefile: 是否打包成单个文件
        clean: 是否清理构建文件
        gui: 是否包含GUI依赖
        web: 是否包含Web美化界面（QWebEngineView）
    """
    if clean:
        print("[INFO] 清理构建文件...")
        for dir_name in ["build", "dist", "__pycache__"]:
            dir_path = PROJECT_ROOT / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  已删除: {dir_path}")

        for spec_file in PROJECT_ROOT.glob("*.spec"):
            spec_file.unlink()
            print(f"  已删除: {spec_file}")

        print("[INFO] 清理完成")
        return True

    # 检查依赖
    if not check_dependencies():
        return False

    # 收集数据文件
    data_files = collect_data_files()
    print(f"[INFO] 收集到 {len(data_files)} 个数据文件")

    # 确定入口点
    if web:
        entry_point = str(SRC_DIR / "main_gui.py")
    else:
        entry_point = str(SRC_DIR / "sw_helper" / "cli.py")

    # 基础PyInstaller命令
    cmd = [
        "pyinstaller",
        "--name=cae-cli",
        f"--icon={PROJECT_ROOT / 'assets' / 'icon.ico'}" if (PROJECT_ROOT / "assets" / "icon.ico").exists() else "",
        "--console" if not gui and not web else "--windowed",
        "--add-data", f"{SRC_DIR}{os.pathsep}src",
        # 排除冲突的Qt库
        "--exclude-module", "PyQt5",
        "--exclude-module", "PyQt5.QtCore",
        "--exclude-module", "PyQt5.QtGui",
        "--exclude-module", "PyQt5.QtWidgets",
        "--exclude-module", "PyQt5.QtWebEngineWidgets",
    ]

    # 基础隐藏导入
    hidden_imports = [
        "click", "rich", "yaml", "numpy", "jinja2", "pint",
        "chromadb", "sentence_transformers",
        "sw_helper.utils.rag_engine",
        "sw_helper.learning.progress_tracker",
        "sw_helper.learning.quiz_manager",
        "sw_helper.main_menu",
    ]

    # 添加GUI/Web相关隐藏导入
    if gui or web:
        hidden_imports.extend([
            "PySide6",
            "PySide6.QtCore",
            "PySide6.QtGui",
            "PySide6.QtWidgets",
            "gui",
            "gui.main_window",
            "gui.theme",
        ])

    if web:
        hidden_imports.extend([
            "PySide6.QtWebEngineWidgets",
            "PySide6.QtWebEngineCore",
            "PySide6.QtWebChannel",
            "gui.web_view",
        ])

    # 添加所有隐藏导入
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # 收集所有依赖包
    collect_all = ["chromadb", "sentence_transformers", "rich"]
    if gui or web:
        collect_all.extend(["PySide6"])

    for pkg in collect_all:
        cmd.extend(["--collect-all", pkg])

    # 添加数据文件
    for src, dst in data_files:
        cmd.extend(["--add-data", f"{src}{os.pathsep}{dst}"])

    # onefile模式
    if onefile:
        cmd.append("--onefile")

    # 入口点
    cmd.append(entry_point)

    # 过滤空字符串
    cmd = [arg for arg in cmd if arg]

    print(f"[INFO] 执行命令: {' '.join(cmd[:15])}...")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[INFO] 构建成功!")

        if result.stdout:
            print("[PYINSTALLER STDOUT]:", result.stdout[-1000:])

        dist_dir = PROJECT_ROOT / "dist"
        if dist_dir.exists():
            print(f"\n[INFO] 可执行文件位于: {dist_dir}")
            for item in dist_dir.iterdir():
                print(f"  - {item.name}")

        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 构建失败: {e}")
        if e.stderr:
            print("[PYINSTALLER STDERR]:", e.stderr[-2000:])
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CAE-CLI 打包脚本")
    parser.add_argument("--onefile", action="store_true", help="创建单个可执行文件")
    parser.add_argument("--clean", action="store_true", help="清理构建文件")
    parser.add_argument("--gui", action="store_true", help="构建GUI版本")
    parser.add_argument("--web", action="store_true", help="构建Web美化版本（包含QWebEngineView）")

    args = parser.parse_args()

    print("CAE-CLI 打包工具")
    print("=" * 40)

    mode = "CLI"
    if args.web:
        mode = "Web美化界面"
    elif args.gui:
        mode = "GUI"

    print(f"打包模式: {mode}")

    success = build_exe(
        onefile=args.onefile,
        clean=args.clean,
        gui=args.gui,
        web=args.web
    )

    if success and not args.clean:
        print("\n" + "="*40)
        print(f"🎉 {mode}版本打包完成!")
        print("\n重要提示:")
        print("1. 可执行文件不包含AI模型文件")
        print("2. 首次运行时会检查并提示安装必要组件")
        if args.web:
            print("3. Web版本需要安装 PySide6-WebEngine")
            print("   pip install PySide6-WebEngine")
        print("="*40)
    elif not success:
        print("\n打包失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
