#!/usr/bin/env python3
"""
测试新的FreeCAD连接器
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations.cad.freecad import FreeCADConnector


def test_connector():
    """测试FreeCAD连接器基本功能"""
    print("测试新的FreeCAD连接器...")

    # 创建连接器实例
    connector = FreeCADConnector()

    # 测试连接（模拟模式）
    print("1. 测试连接...")
    # 注意：实际测试需要FreeCAD安装，这里只测试接口

    # 测试支持的格式
    print("2. 测试支持的格式...")
    formats = connector.get_supported_formats()
    print(f"   支持的格式: {[fmt.value for fmt in formats]}")

    # 测试软件信息
    print("3. 测试软件信息...")
    info = connector.get_software_info()
    print(f"   软件信息: {info}")

    print("\n✅ 接口测试完成")
    print("   注意：完整测试需要FreeCAD安装和环境配置")


if __name__ == "__main__":
    test_connector()
