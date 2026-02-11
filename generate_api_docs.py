#!/usr/bin/env python3
"""
CAE-CLI API 文档生成脚本

使用 pdoc3 自动生成 API 文档，支持 HTML 和 Markdown 格式。

用法:
    python generate_api_docs.py                     # 生成 HTML 文档到 docs/api/
    python generate_api_docs.py --format markdown   # 生成 Markdown 文档
    python generate_api_docs.py --format html       # 生成 HTML 文档
    python generate_api_docs.py --help              # 显示帮助信息
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
DOCS_DIR = PROJECT_ROOT / "docs"

def check_pdoc_installed():
    """检查 pdoc 是否已安装"""
    try:
        import pdoc
        return True
    except ImportError:
        return False

def install_pdoc():
    """安装 pdoc3"""
    print("正在安装 pdoc3...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdoc3"])
        print("✅ pdoc3 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装 pdoc3 失败: {e}")
        return False

def generate_html_docs():
    """生成 HTML 格式 API 文档"""
    output_dir = DOCS_DIR / "api"

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成文档的模块列表
    modules = [
        "sw_helper",
        "integrations",
        "core"
    ]

    # 构建 pdoc 命令
    cmd = [
        sys.executable, "-m", "pdoc",
        "--html",
        "--output-dir", str(output_dir),
        "--force"
    ]

    # 添加模块路径
    for module in modules:
        module_path = SRC_DIR / module
        if module_path.exists():
            cmd.append(str(module_path))
        else:
            print(f"⚠️  模块路径不存在: {module_path}")

    print(f"正在生成 HTML API 文档到 {output_dir}...")
    print(f"执行命令: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
        print(f"✅ HTML API 文档已生成到 {output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 生成 HTML 文档失败: {e}")
        return False

def generate_markdown_docs(output_path=None):
    """生成 Markdown 格式 API 文档"""
    if output_path is None:
        output_path = DOCS_DIR / "API_REFERENCE.md"

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 生成文档的模块列表
    modules = [
        "sw_helper",
        "integrations",
        "core"
    ]

    # 导入 pdoc 并生成文档
    try:
        import pdoc

        # 收集所有模块的文档
        all_docs = []

        for module_name in modules:
            module_path = SRC_DIR / module_name
            if module_path.exists():
                print(f"正在处理模块: {module_name}")

                # 使用 pdoc 提取文档
                module_docs = pdoc.Module(module_name)

                # 这里简化处理，实际应用中需要更复杂的转换
                # 由于 pdoc 的 Markdown 输出需要额外处理，这里先简单生成
                all_docs.append(f"# {module_name} 模块\n\n")
                all_docs.append(f"模块路径: `{module_path}`\n\n")

                # 添加子模块信息
                for submodule_name in module_docs.submodules():
                    all_docs.append(f"## {submodule_name}\n\n")

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# CAE-CLI API 参考文档\n\n")
            f.write("> 注意：此 Markdown 文件为简化版本，完整 API 文档请查看 HTML 版本。\n\n")
            f.write("## 模块概览\n\n")
            f.write("".join(all_docs))
            f.write("\n\n## 完整文档\n\n")
            f.write("完整 API 文档已生成到 `docs/api/` 目录，请使用浏览器打开 `index.html` 查看。\n")

        print(f"✅ Markdown API 文档已生成到 {output_path}")
        print(f"⚠️  注意：Markdown 版本为简化版，建议查看 HTML 完整文档")
        return True

    except ImportError:
        print("❌ 未找到 pdoc 模块，请先安装: pip install pdoc3")
        return False
    except Exception as e:
        print(f"❌ 生成 Markdown 文档失败: {e}")
        return False

def generate_both_formats():
    """生成两种格式的文档"""
    success_html = generate_html_docs()
    success_md = generate_markdown_docs()

    return success_html and success_md

def main():
    parser = argparse.ArgumentParser(
        description="CAE-CLI API 文档生成脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 生成 HTML 文档到 docs/api/
  %(prog)s --format html      # 生成 HTML 文档
  %(prog)s --format markdown  # 生成 Markdown 文档
  %(prog)s --format both      # 生成两种格式
  %(prog)s --output custom.md # 指定输出路径
        """
    )

    parser.add_argument(
        "--format",
        choices=["html", "markdown", "both"],
        default="html",
        help="文档格式 (默认: html)"
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Markdown 输出文件路径 (仅对 markdown 格式有效)"
    )

    parser.add_argument(
        "--force-install",
        action="store_true",
        help="强制安装 pdoc3（如果未安装）"
    )

    args = parser.parse_args()

    # 检查 pdoc 是否已安装
    if not check_pdoc_installed():
        print("❌ pdoc3 未安装")
        if args.force_install:
            if not install_pdoc():
                sys.exit(1)
        else:
            print("请安装 pdoc3: pip install pdoc3")
            print("或使用 --force-install 参数自动安装")
            sys.exit(1)

    # 根据格式生成文档
    success = False

    if args.format == "html":
        success = generate_html_docs()
    elif args.format == "markdown":
        success = generate_markdown_docs(args.output)
    elif args.format == "both":
        success = generate_both_formats()

    if success:
        print("\n🎉 文档生成完成！")
        print("📖 HTML 文档位置: docs/api/index.html")
        print("📝 Markdown 文档位置: docs/API_REFERENCE.md")
        print("\n提示: 使用浏览器打开 docs/api/index.html 查看完整 API 文档")
    else:
        print("\n❌ 文档生成失败")
        sys.exit(1)

if __name__ == "__main__":
    main()