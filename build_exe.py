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
                # 计算相对路径
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
    script_content = '''#!/usr/bin/env python3
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
        # 尝试加载一个小模型来测试
        print("[INFO] 检查 sentence-transformers...")
        # 不实际加载模型，只检查是否可导入
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
    print("\\n" + "="*60)
    print("  CAE-CLI AI功能依赖安装指南")
    print("="*60)

    print("\\n[重要] CAE-CLI 需要以下AI组件才能使用完整功能:")
    print("\\n1. sentence-transformers (用于知识库检索):")
    print("   运行: pip install sentence-transformers")
    print("   或: pip install sentence-transformers==2.2.0")

    print("\\n2. ChromaDB (向量数据库):")
    print("   运行: pip install chromadb==0.4.0")

    print("\\n3. Ollama (本地AI模型，可选但推荐):")
    print("   下载: https://ollama.com/")
    print("   安装后运行: ollama pull qwen2.5:1.5b")
    print("   或: ollama pull phi3:mini")

    print("\\n4. 首次使用知识库检索时，会自动下载模型")
    print("   (~80MB，只需下载一次)")

    print("\\n5. 基础功能（无需AI）:")
    print("   - 几何文件解析")
    print("   - 网格质量分析")
    print("   - 材料数据库查询")
    print("   - 报告生成")

    print("\\n" + "="*60)
    print("提示: 您可以在没有AI组件的情况下使用基础功能。")
    print("当需要AI功能时，程序会提示您安装。")
    print("="*60 + "\\n")

def create_model_download_script():
    """创建模型下载脚本（可选）"""
    script = '''
import os
import sys
from sentence_transformers import SentenceTransformer

def download_model():
    """下载sentence-transformers模型"""
    print("正在下载 sentence-transformers 模型 (all-MiniLM-L6-v2)...")
    print("这可能需要几分钟，取决于您的网络速度。")
    print("模型大小约80MB。")

    try:
        # 下载模型
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ 模型下载完成!")

        # 测试模型
        embeddings = model.encode(["测试文本"])
        print(f"✓ 模型测试通过，嵌入维度: {embeddings.shape[1]}")
        return True
    except Exception as e:
        print(f"✗ 模型下载失败: {e}")
        return False

if __name__ == "__main__":
    download_model()
'''

    script_path = Path("scripts") / "download_model.py"
    script_path.parent.mkdir(exist_ok=True)

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)

    print(f"[INFO] 模型下载脚本已创建: {script_path}")
    print("[INFO] 运行: python scripts/download_model.py")

def main():
    """主检查函数"""
    print("\\n[CAE-CLI] 首次运行检查")
    print("-" * 40)

    # 检查基础依赖
    print("\\n[1/4] 检查基础依赖...")
    deps_ok = True

    try:
        import click
        import rich
        import yaml
        import numpy
        print("✓ 基础依赖正常")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -e . 或 pip install -r requirements.txt")
        deps_ok = False

    # 检查AI依赖
    print("\\n[2/4] 检查AI依赖...")
    ai_deps_ok = True

    st_ok = check_sentence_transformers()
    chroma_ok = check_chromadb()
    ollama_ok = check_ollama()

    if st_ok:
        print("✓ sentence-transformers: 已安装")
    else:
        print("✗ sentence-transformers: 未安装")
        ai_deps_ok = False

    if chroma_ok:
        print("✓ ChromaDB: 已安装")
    else:
        print("✗ ChromaDB: 未安装")
        ai_deps_ok = False

    if ollama_ok:
        print("✓ Ollama: 已安装并运行")
    else:
        print("⚠ Ollama: 未安装或未运行 (辅助学习功能受限)")

    # 显示指南
    if not ai_deps_ok:
        show_installation_guide()

        # 询问是否创建下载脚本
        response = input("\\n是否创建模型下载脚本? (y/n): ").lower()
        if response == 'y':
            create_model_download_script()

    print("\\n" + "="*60)
    if deps_ok:
        print("✅ CAE-CLI 准备就绪!")
        if ai_deps_ok:
            print("所有AI功能可用")
        else:
            print("基础功能可用，AI功能需安装额外依赖")
    else:
        print("❌ 缺少必要依赖，请先安装")
    print("="*60 + "\\n")

    # 创建标记文件，避免每次检查
    marker_file = Path.home() / ".cae-cli" / "first_run_done"
    marker_file.parent.mkdir(exist_ok=True)
    marker_file.touch()

    return deps_ok

if __name__ == "__main__":
    main()
'''

    scripts_dir = PROJECT_ROOT / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    script_path = scripts_dir / "first_run_check.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"[INFO] 首次运行检查脚本已创建: {script_path}")

def build_exe(onefile=False, clean=False):
    """构建可执行文件"""
    if clean:
        print("[INFO] 清理构建文件...")
        for dir_name in ["build", "dist", "__pycache__"]:
            dir_path = PROJECT_ROOT / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  已删除: {dir_path}")

        # 删除.spec文件
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

    # PyInstaller命令
    entry_point = str(SRC_DIR / "sw_helper" / "cli.py")

    cmd = [
        "pyinstaller",
        "--name=cae-cli",
        f"--icon={PROJECT_ROOT / 'assets' / 'icon.ico'}" if (PROJECT_ROOT / "assets" / "icon.ico").exists() else "",
        "--console",
        "--add-data", f"{SRC_DIR}{os.pathsep}src",
        "--hidden-import", "click",
        "--hidden-import", "rich",
        "--hidden-import", "yaml",
        "--hidden-import", "numpy",
        "--hidden-import", "jinja2",
        "--hidden-import", "pint",
        "--hidden-import", "chromadb",
        "--hidden-import", "sentence_transformers",
        "--hidden-import", "sw_helper.utils.rag_engine",
        "--hidden-import", "sw_helper.learning.progress_tracker",
        "--hidden-import", "sw_helper.learning.quiz_manager",
        "--hidden-import", "sw_helper.main_menu",
        "--collect-all", "chromadb",
        "--collect-all", "sentence_transformers",
    ]

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

    print(f"[INFO] 执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[INFO] 构建成功!")

        # 显示输出信息
        if result.stdout:
            print("[PYINSTALLER STDOUT]:", result.stdout[-1000:])  # 显示最后1000字符

        # 显示构建结果
        dist_dir = PROJECT_ROOT / "dist"
        if dist_dir.exists():
            print(f"\n[INFO] 可执行文件位于: {dist_dir}")
            for item in dist_dir.iterdir():
                print(f"  - {item.name}")

        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 构建失败: {e}")
        if e.stderr:
            print("[PYINSTALLER STDERR]:", e.stderr[-2000:])  # 显示最后2000字符
        return False

def create_installer_script():
    """创建安装脚本（可选）"""
    script_content = '''#!/usr/bin/env bash
# CAE-CLI 安装脚本

set -e

echo "CAE-CLI 安装程序"
echo "================"

# 检测操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    OS="unknown"
fi

echo "检测到操作系统: $OS"

# 安装位置
INSTALL_DIR="$HOME/.local/cae-cli"
BIN_DIR="$HOME/.local/bin"

# 创建目录
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

echo "安装目录: $INSTALL_DIR"

# 复制文件
echo "复制文件..."
cp -r dist/cae-cli/* "$INSTALL_DIR/"

# 创建启动脚本
if [[ "$OS" == "windows" ]]; then
    # Windows批处理文件
    cat > "$BIN_DIR/cae-cli.bat" << 'EOF'
@echo off
setlocal
set CAE_CLI_DIR=%~dp0..\.local\cae-cli
"%CAE_CLI_DIR%\cae-cli.exe" %*
EOF
    echo "创建: $BIN_DIR/cae-cli.bat"
else
    # Unix shell脚本
    cat > "$BIN_DIR/cae-cli" << 'EOF'
#!/bin/bash
CAE_CLI_DIR="$HOME/.local/cae-cli"
"$CAE_CLI_DIR/cae-cli" "$@"
EOF
    chmod +x "$BIN_DIR/cae-cli"
    echo "创建: $BIN_DIR/cae-cli"
fi

echo ""
echo "安装完成!"
echo ""
echo "使用方法:"
if [[ "$OS" == "windows" ]]; then
    echo "  1. 将 $BIN_DIR 添加到 PATH 环境变量"
    echo "  2. 在命令行中运行: cae-cli --help"
else
    echo "  1. 确保 $BIN_DIR 在 PATH 环境变量中"
    echo "  2. 在终端中运行: cae-cli --help"
fi
echo ""
echo "首次运行时会检查AI依赖并提示安装。"
'''

    script_path = PROJECT_ROOT / "install.sh"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    os.chmod(script_path, 0o755)
    print(f"[INFO] 安装脚本已创建: {script_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CAE-CLI 打包脚本")
    parser.add_argument("--onefile", action="store_true", help="创建单个可执行文件")
    parser.add_argument("--clean", action="store_true", help="清理构建文件")
    parser.add_argument("--installer", action="store_true", help="创建安装脚本")

    args = parser.parse_args()

    print("CAE-CLI 打包工具")
    print("=" * 40)

    if args.installer:
        create_installer_script()
        return

    success = build_exe(onefile=args.onefile, clean=args.clean)

    if success and not args.clean:
        print("\n" + "="*40)
        print("打包完成!")
        print("\n重要提示:")
        print("1. 可执行文件不包含AI模型文件")
        print("2. 首次运行时会检查并提示安装必要组件")
        print("3. 模型文件需要额外下载 (约80MB)")
        print("4. 确保用户有网络连接以下载依赖")
        print("="*40)

        # 询问是否创建安装脚本
        response = input("\n是否创建安装脚本? (y/n): ").lower()
        if response == 'y':
            create_installer_script()
    elif not success:
        print("\n打包失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()