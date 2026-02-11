#!/usr/bin/env python3
"""
测试新的CalculiX连接器
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations.cae.calculix import CalculiXConnector, CalculiXConnectorMock


def test_connector_interface():
    """测试CalculiX连接器接口"""
    print("测试CalculiX连接器接口...")

    # 测试模拟模式
    print("1. 测试模拟连接器...")
    mock_connector = CalculiXConnectorMock()

    # 测试连接
    assert mock_connector.connect() == True
    print("   ✓ 连接成功")

    # 测试支持的分析类型
    analysis_types = mock_connector.get_supported_analysis_types()
    print(f"   ✓ 支持的分析类型: {analysis_types}")

    # 测试软件信息
    info = mock_connector.get_software_info()
    print(f"   ✓ 软件信息: {info}")

    # 测试实际连接器（如果可用）
    print("\n2. 测试实际连接器（如果可用）...")
    real_connector = CalculiXConnector()

    # 测试连接（可能失败，如果没有安装CalculiX）
    connected = real_connector.connect()
    if connected:
        print("   ✓ CalculiX已安装并可用")

        # 测试分析类型
        real_types = real_connector.get_supported_analysis_types()
        print(f"   ✓ 实际支持的分析类型: {real_types}")
    else:
        print("   ⚠ CalculiX未安装，跳过实际测试")
        print("   提示: 安装CalculiX以进行完整测试")

    print("\n✅ 接口测试完成")


def test_mock_simulation():
    """测试模拟仿真流程"""
    print("\n测试模拟仿真流程...")

    mock_connector = CalculiXConnectorMock()
    mock_connector.connect()

    # 创建测试文件
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)

    geometry_file = test_dir / "test_geometry.step"
    mesh_file = test_dir / "test_mesh.inp"

    # 创建虚拟几何文件
    geometry_file.write_text("** Test geometry\n")

    # 测试网格生成
    print("1. 测试网格生成...")
    success = mock_connector.generate_mesh(geometry_file, mesh_file, element_size=2.0)
    assert success == True
    print(f"   ✓ 网格生成成功: {mesh_file}")

    # 测试仿真设置
    print("2. 测试仿真设置...")
    config = {
        "analysis_type": "static",
        "material": {"name": "STEEL", "E": 210000.0, "nu": 0.3},
        "loads": [{"node_set": "LOAD_NODES", "dof": 3, "value": -100.0}],
        "constraints": [{"node_set": "FIXED", "dofs": "1,3,0.0"}],
    }

    input_file = mock_connector.setup_simulation(mesh_file, config)
    assert input_file.exists()
    print(f"   ✓ 输入文件创建: {input_file}")

    # 测试仿真运行
    print("3. 测试仿真运行...")
    output_dir = test_dir / "results"
    success = mock_connector.run_simulation(input_file, output_dir)
    assert success == True
    print(f"   ✓ 仿真运行成功")

    # 测试结果读取
    print("4. 测试结果读取...")
    result_file = output_dir / "test_mesh.frd"
    if result_file.exists():
        results = mock_connector.read_results(result_file)
        print(f"   ✓ 结果读取成功: {results.get('file_path')}")
    else:
        print("   ⚠ 结果文件不存在（模拟模式可能未创建）")

    # 清理
    print("\n5. 清理测试文件...")
    import shutil

    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"   ✓ 清理完成")

    print("\n✅ 模拟仿真测试完成")


if __name__ == "__main__":
    test_connector_interface()
    test_mock_simulation()
