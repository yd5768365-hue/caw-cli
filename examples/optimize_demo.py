#!/usr/bin/env python3
"""
CAE-CLI Optimize 命令使用示例
演示参数优化闭环功能
"""

import subprocess
import sys


def run_command(cmd, description=""):
    """运行命令并显示结果"""
    if description:
        print(f"\n{'=' * 60}")
        print(f"📝 {description}")
        print(f"{'=' * 60}")
    print(f"$ {cmd}")
    print("-" * 60)

    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    return result.returncode == 0


def main():
    """运行示例"""

    print("""
╔══════════════════════════════════════════════════════════════╗
║              CAE-CLI Optimize 命令使用示例                    ║
╚══════════════════════════════════════════════════════════════╝

本示例演示 cae-cli optimize 命令的各种用法
    """)

    # 示例1: 基本优化（使用模拟模式）
    print("\n1️⃣  基本参数优化（模拟模式 - 无需FreeCAD）")
    run_command(
        "cae-cli optimize examples/test_model.FCStd -p Fillet_Radius -r 2 15 --steps 5 --cad mock",
        "优化圆角半径: 2mm ~ 15mm, 5次迭代",
    )

    # 示例2: 生成图表
    print("\n2️⃣  优化并生成可视化图表")
    run_command(
        "cae-cli optimize examples/bracket.FCStd -p Thickness -r 5 20 --steps 8 --plot --cad mock",
        "优化厚度并生成优化曲线图",
    )

    # 示例3: 生成完整报告
    print("\n3️⃣  优化并生成完整报告")
    run_command(
        "cae-cli optimize examples/part.FCStd -p Length -r 100 200 -s 10 --plot --report --cad mock",
        "优化长度并生成图表和Markdown报告",
    )

    # 示例4: 指定输出
    print("\n4️⃣  自定义输出路径")
    run_command(
        "cae-cli optimize model.FCStd -p Radius -r 1 10 -o results/opt_result.json -d ./my_output --plot --cad mock",
        "指定JSON输出和输出目录",
    )

    # 示例5: 真实FreeCAD模式（如果安装了FreeCAD）
    print("\n5️⃣  使用真实FreeCAD（如果已安装）")
    print("如果已安装FreeCAD，可以使用真实模式:")
    print("$ cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 5")

    print("\n" + "=" * 60)
    print("✅ 示例完成!")
    print("=" * 60)
    print("""
📚 常用命令总结:

1. 基本优化:
   cae-cli optimize model.FCStd -p Fillet_Radius -r 2 15 --steps 5

2. 生成图表:
   cae-cli optimize model.FCStd -p Length -r 100 200 --plot

3. 生成报告:
   cae-cli optimize model.FCStd -p Thickness -r 5 20 --report

4. 使用模拟模式(无需FreeCAD):
   cae-cli optimize model.FCStd -p Radius -r 1 10 --cad mock

5. 完整参数:
   cae-cli optimize model.FCStd -p Param -r min max -s steps -o output.json -d dir --plot --report

📖 参数说明:
   -p, --parameter    要优化的参数名
   -r, --range        参数范围 (最小值 最大值)
   -s, --steps        迭代步数
   --cad              CAD类型: freecad(默认) | solidworks | mock
   -o, --output       JSON结果输出路径
   -d, --output-dir   输出目录
   --plot             生成优化图表(PNG)
   --report           生成Markdown报告
    """)


if __name__ == "__main__":
    main()
