#!/usr/bin/env python3
"""
演示如何使用CAE-CLI的核心配置系统

此脚本展示：
1. 如何从YAML文件加载仿真配置
2. 如何创建和验证配置对象
3. 如何将配置保存回YAML文件
4. 如何使用配置创建工作流
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from core.types import SimulationConfig, FileFormat, create_default_config
    from integrations._base.connectors import CADConnector, CAEConnector
    from integrations._base.workflow import WorkflowEngine
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装CAE-CLI开发版本: pip install -e .")
    sys.exit(1)


def demo_config_loading():
    """演示配置加载和验证"""
    print("=" * 60)
    print("演示1: 配置加载和验证")
    print("=" * 60)

    # 方法1: 从YAML文件加载
    yaml_path = Path(__file__).parent / "project.yaml"

    if yaml_path.exists():
        print(f"从YAML文件加载配置: {yaml_path}")
        try:
            config = SimulationConfig.from_yaml(yaml_path)
            print(f"✓ 配置加载成功: {config.project_name}")
            print(f"  描述: {config.description}")
            print(f"  CAD软件: {config.cad_software}")
            print(f"  分析类型: {config.analysis_type}")
            print(f"  求解器: {config.solver}")

            # 验证配置
            errors = config.validate()
            if errors:
                print("✗ 配置验证失败:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("✓ 配置验证通过")

        except Exception as e:
            print(f"✗ 配置加载失败: {e}")
    else:
        print(f"⚠ YAML文件不存在: {yaml_path}")
        print("使用默认配置进行演示...")
        config = create_default_config("演示项目")
        print(f"✓ 创建默认配置: {config.project_name}")

    # 方法2: 从字典创建
    print("\n从字典创建配置:")
    config_dict = {
        "project_name": "手动创建项目",
        "cad_software": "freecad",
        "cad_file": "test.FCStd",
        "analysis_type": "static",
        "mesh_element_size": 1.5,
        "output_formats": ["vtk", "json"],
    }

    config2 = SimulationConfig.from_dict(config_dict)
    print(f"✓ 从字典创建配置: {config2.project_name}")
    print(f"  单元尺寸: {config2.element_size} mm")
    print(f"  输出格式: {[fmt.value for fmt in config2.output_formats]}")

    # 转换为字典
    print("\n配置序列化:")
    serialized = config2.to_dict()
    print(f"  序列化键: {list(serialized.keys())}")

    return config


def demo_workflow_creation():
    """演示工作流创建"""
    print("\n" + "=" * 60)
    print("演示2: 工作流创建")
    print("=" * 60)

    # 创建模拟连接器（实际实现需要具体软件支持）
    class MockCADConnector(CADConnector):
        """模拟CAD连接器用于演示"""

        def connect(self) -> bool:
            print("  [模拟] 连接到CAD软件")
            return True

        def load_model(self, file_path: Path) -> bool:
            print(f"  [模拟] 加载模型: {file_path}")
            return True

        def get_parameter(self, name: str):
            print(f"  [模拟] 获取参数: {name}")
            return 10.0

        def set_parameter(self, name: str, value: float) -> bool:
            print(f"  [模拟] 设置参数: {name} = {value}")
            return True

        def rebuild(self) -> bool:
            print("  [模拟] 重建模型")
            return True

        def export_step(self, output_path: Path) -> bool:
            print(f"  [模拟] 导出STEP: {output_path}")
            return True

        def get_supported_formats(self):
            return [FileFormat.STEP, FileFormat.STL]

    class MockCAEConnector(CAEConnector):
        """模拟CAE连接器用于演示"""

        def connect(self) -> bool:
            print("  [模拟] 连接到CAE软件")
            return True

        def generate_mesh(
            self, geometry_file: Path, mesh_file: Path, element_size: float
        ) -> bool:
            print(f"  [模拟] 生成网格: {element_size}mm")
            return True

        def setup_simulation(self, mesh_file: Path, config: dict) -> Path:
            print(f"  [模拟] 设置仿真: {config.get('analysis_type', 'unknown')}")
            return mesh_file.parent / "simulation.inp"

        def run_simulation(self, input_file: Path, output_dir: Path = None) -> bool:
            print(f"  [模拟] 运行仿真: {input_file.name}")
            return True

        def read_results(self, result_file: Path) -> dict:
            print(f"  [模拟] 读取结果: {result_file.name}")
            return {"max_stress": 150e6, "max_displacement": 0.5, "safety_factor": 1.8}

        def get_supported_analysis_types(self):
            return ["static", "modal", "thermal"]

    # 创建连接器实例
    cad_connector = MockCADConnector()
    cae_connector = MockCAEConnector()

    # 创建工作流引擎
    workflow = WorkflowEngine(cad_connector, cae_connector)

    print("可用预定义工作流:")
    for name, steps in workflow.PREDEFINED_WORKFLOWS.items():
        print(f"  - {name}: {len(steps)} 个步骤")

    # 运行预定义工作流
    print("\n运行预定义工作流 'stress_analysis':")
    try:
        config = {
            "cad_file": "test.FCStd",
            "parameters": {"thickness": 5.0, "fillet_radius": 3.0},
            "mesh_element_size": 2.0,
            "output_dir": "./demo_output",
        }

        result = workflow.run_workflow("stress_analysis", config)
        print(f"✓ 工作流完成: {result['status']}")
        print(f"  输出目录: {result['output_dir']}")
        print(f"  执行步骤: {len(result['steps'])}")

    except Exception as e:
        print(f"✗ 工作流执行失败: {e}")

    # 运行自定义工作流
    print("\n运行自定义工作流:")
    custom_steps = [
        ("cad", "load_model"),
        ("cad", "set_parameters"),
        ("cad", "export_step"),
        ("mesher", "generate_mesh"),
        ("cae", "setup_static_analysis"),
    ]

    try:
        config = {
            "cad_file": "custom.FCStd",
            "parameters": {"length": 100.0},
            "output_dir": "./custom_output",
        }

        result = workflow.run_workflow("custom_analysis", config, custom_steps)
        print(f"✓ 自定义工作流完成")

    except Exception as e:
        print(f"✗ 自定义工作流失败: {e}")


def demo_file_format_usage():
    """演示文件格式枚举使用"""
    print("\n" + "=" * 60)
    print("演示3: 文件格式和数据流")
    print("=" * 60)

    print("标准数据流路径:")
    data_flow = [
        ("CAD模型", FileFormat.FCSTD),
        ("几何交换", FileFormat.STEP),
        ("网格文件", FileFormat.MSH),
        ("求解器输入", FileFormat.INP),
        ("结果文件", FileFormat.VTK),
        ("报告", FileFormat.HTML),
    ]

    for stage, fmt in data_flow:
        print(f"  {stage}: {fmt.value} (.{fmt.value})")

    print("\n文件格式验证:")
    test_formats = ["step", "msh", "inp", "vtk", "html", "unknown"]

    for fmt_str in test_formats:
        try:
            fmt = FileFormat(fmt_str)
            print(f"  ✓ {fmt_str} -> {fmt.value}")
        except ValueError:
            print(f"  ✗ {fmt_str}: 不支持的文件格式")

    print("\n格式转换示例:")
    # 模拟CAD到CAE的数据流
    cad_file = Path("model.FCStd")
    step_file = cad_file.with_suffix(".step")
    mesh_file = step_file.with_suffix(".msh")
    input_file = mesh_file.with_suffix(".inp")
    result_file = input_file.with_suffix(".vtk")

    files = [cad_file, step_file, mesh_file, input_file, result_file]
    for i, file in enumerate(files):
        suffix = file.suffix[1:] if file.suffix else ""
        try:
            fmt = FileFormat(suffix) if suffix else None
            stage = ["CAD", "几何", "网格", "求解", "结果"][i]
            print(f"  {stage}: {file.name} ({fmt.value if fmt else 'N/A'})")
        except:
            print(f"  {stage}: {file.name} (格式未知)")


def main():
    """主演示函数"""
    print("CAE-CLI 核心架构演示")
    print("展示插件化架构和配置系统\n")

    # 演示1: 配置加载
    config = demo_config_loading()

    # 演示2: 工作流创建
    demo_workflow_creation()

    # 演示3: 文件格式
    demo_file_format_usage()

    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)
    print("\n下一步:")
    print("1. 实现具体的CADConnector (如FreeCADConnector)")
    print("2. 实现具体的CAEConnector (如CalculiXConnector)")
    print("3. 使用配置系统管理仿真项目")
    print("4. 扩展工作流支持更多分析类型")


if __name__ == "__main__":
    main()
