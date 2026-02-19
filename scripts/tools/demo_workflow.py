#!/usr/bin/env python3
"""
演示完整的FreeCAD + CalculiX工作流

此脚本展示如何使用新的插件化架构进行完整的CAD/CAE分析流程。
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from integrations import WorkflowEngine
from integrations.cad.freecad import FreeCADConnector
from integrations.cae.calculix import (
    CalculiXConnectorMock as CalculiXConnector,
)  # 使用模拟器
from core.types import SimulationConfig, create_default_config


def demo_workflow():
    """演示完整工作流"""
    print("=" * 60)
    print("FreeCAD + CalculiX 工作流演示")
    print("=" * 60)

    # 创建输出目录
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)

    # 1. 创建仿真配置
    print("\n1. 创建仿真配置...")
    config = create_default_config("演示项目")
    config.cad_file = Path("examples/sample_model.FCStd")  # 假设的示例文件
    config.output_dir = output_dir
    config.analysis_type = "static"
    config.solver = "calculix"
    config.element_size = 5.0

    print(f"   项目名称: {config.project_name}")
    print(f"   分析类型: {config.analysis_type}")
    print(f"   求解器: {config.solver}")
    print(f"   输出目录: {config.output_dir}")

    # 保存配置到文件
    config_file = output_dir / "config.yaml"
    config.to_yaml(config_file)
    print(f"   配置已保存: {config_file}")

    # 2. 创建工作流引擎
    print("\n2. 创建工作流引擎...")
    workflow = WorkflowEngine()

    # 3. 设置CAD连接器
    print("\n3. 设置CAD连接器...")
    cad_connector = FreeCADConnector()

    # 注意：由于可能没有安装FreeCAD，我们只测试接口
    print(f"   CAD连接器类型: {type(cad_connector).__name__}")
    print(
        f"   支持的格式: {[fmt.value for fmt in cad_connector.get_supported_formats()]}"
    )

    # 4. 设置CAE连接器
    print("\n4. 设置CAE连接器...")
    cae_connector = CalculiXConnector()
    cae_connector.connect()  # 连接模拟器

    print(f"   CAE连接器类型: {type(cae_connector).__name__}")
    print(f"   支持的分析类型: {cae_connector.get_supported_analysis_types()}")

    # 5. 运行工作流
    print("\n5. 运行工作流...")
    print("   注意：这是演示模式，使用模拟连接器")

    try:
        # 注册连接器
        workflow.register_cad_connector("freecad", cad_connector)
        workflow.register_cae_connector("calculix", cae_connector)

        # 运行预定义的工作流
        print("\n   a) 运行应力分析工作流...")
        result = workflow.run_workflow(
            "stress_analysis",
            cad_software="freecad",
            cae_software="calculix",
            config=config,
        )

        if result:
            print(f"   ✓ 工作流执行成功")

            # 显示结果摘要
            print(f"\n   结果摘要:")
            print(f"     状态: {result.status}")
            if result.max_stress:
                print(f"     最大应力: {result.max_stress:.2f} Pa")
            if result.max_displacement:
                print(f"     最大位移: {result.max_displacement:.6f} m")
            if result.safety_factor:
                print(f"     安全系数: {result.safety_factor:.2f}")

            # 检查生成的文件
            if result.result_files:
                print(f"\n   生成的文件:")
                for fmt, path in result.result_files.items():
                    if path.exists():
                        print(f"     - {fmt.value}: {path}")

        else:
            print("   ⚠ 工作流执行失败（模拟模式）")

    except Exception as e:
        print(f"   ✗ 工作流执行出错: {e}")
        import traceback

        traceback.print_exc()

    # 6. 演示自定义工作流
    print("\n6. 演示自定义工作流...")

    custom_steps = [
        {
            "name": "参数优化",
            "description": "调整CAD参数并重新分析",
            "action": "optimize_parameters",
            "parameters": {
                "target": "min_stress",
                "constraints": {"displacement_max": 0.01},
                "variables": ["Fillet_Radius", "Thickness"],
                "ranges": {"Fillet_Radius": (1.0, 10.0), "Thickness": (2.0, 20.0)},
            },
        },
        {
            "name": "网格收敛性研究",
            "description": "测试不同网格尺寸对结果的影响",
            "action": "mesh_convergence",
            "parameters": {
                "element_sizes": [10.0, 5.0, 2.0, 1.0],
                "metric": "max_stress",
            },
        },
    ]

    print("   自定义工作流步骤:")
    for i, step in enumerate(custom_steps, 1):
        print(f"     {i}. {step['name']}: {step['description']}")

    # 7. 清理
    print("\n7. 清理...")
    # 保留输出文件用于检查
    print(f"   输出文件保存在: {output_dir}")
    print("   可以手动检查生成的文件")

    print("\n" + "=" * 60)
    print("工作流演示完成!")
    print("=" * 60)

    return True


def demo_connector_factory():
    """演示连接器工厂模式"""
    print("\n" + "=" * 60)
    print("连接器工厂演示")
    print("=" * 60)

    # 演示如何动态创建连接器
    connectors_info = [
        ("CAD", "freecad", "FreeCAD连接器"),
        ("CAE", "calculix", "CalculiX连接器"),
        ("CAE", "abaqus", "Abaqus连接器（待实现）"),
        ("CAD", "solidworks", "SolidWorks连接器（待实现）"),
    ]

    print("\n支持的连接器类型:")
    for connector_type, name, description in connectors_info:
        print(f"  {connector_type}: {name} - {description}")

    # 演示配置文件使用
    print("\n配置文件示例:")
    config_example = {
        "project_name": "支架优化",
        "cad_software": "freecad",
        "cae_software": "calculix",
        "analysis_type": "static",
        "parameters": {"Fillet_Radius": 5.0, "Thickness": 10.0},
        "mesh_settings": {"element_size": 3.0, "element_type": "tetrahedron"},
        "material": {"name": "Q235", "E": 210e9, "nu": 0.3, "density": 7850},
    }

    # 打印简化的配置文件
    for key, value in config_example.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        demo_workflow()
        demo_connector_factory()

        print("\n✅ 演示完成!")
        print("\n下一步:")
        print("  1. 安装FreeCAD和CalculiX进行实际测试")
        print("  2. 运行 'python -m pytest tests/' 进行单元测试")
        print("  3. 查看 examples/ 目录中的示例配置文件")
        print("  4. 运行 'cae-cli workflow --help' 查看CLI命令")

    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
