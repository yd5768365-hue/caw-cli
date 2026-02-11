#!/usr/bin/env python3
"""
Phase 1 集成测试 - 验证CAD/CAE连接器和工作流引擎的基本功能

此脚本用于测试：
1. 所有连接器是否可以正常导入
2. FileFormat 枚举是否统一
3. 工作流引擎是否可以正常初始化
4. 简单的配置解析

注意：此测试不执行实际的CAD/CAE操作，只验证接口可用性
"""

import sys
from pathlib import Path

# 设置编码为 UTF-8
import os
os.environ["PYTHONIOENCODING"] = "utf-8"

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

def test_import_connectors():
    """测试所有连接器是否可以正常导入"""
    print("=" * 60)
    print("测试连接器导入...")
    print("=" * 60)

    try:
        from integrations import (
            CADConnector,
            CAEConnector,
            FileFormat,
            WorkflowEngine,
            FreeCADConnector,
            CalculiXConnector,
            GmshConnector
        )

        print("OK: 所有连接器导入成功")

        # 验证FileFormat枚举一致性
        print(f"OK: FileFormat枚举包含 {len(list(FileFormat.__members__.items()))} 种格式")

        # 验证关键格式是否存在
        assert FileFormat.STEP in FileFormat.__members__.values()
        assert FileFormat.MSH in FileFormat.__members__.values()
        assert FileFormat.INP in FileFormat.__members__.values()
        assert FileFormat.FRD in FileFormat.__members__.values()
        assert FileFormat.VTK in FileFormat.__members__.values()

        print("OK: 核心数据交换格式枚举一致")

        return True

    except ImportError as e:
        print(f"ERROR: 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"ERROR: 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_engine():
    """测试工作流引擎初始化"""
    print("\n" + "=" * 60)
    print("测试工作流引擎初始化...")
    print("=" * 60)

    try:
        from integrations import (
            WorkflowEngine,
            FreeCADConnector,
            CalculiXConnector,
            GmshConnector
        )

        # 创建模拟配置（不执行实际操作）
        cad_connector = FreeCADConnector()
        cae_connector = CalculiXConnector()
        mesher_connector = GmshConnector()

        print("OK: 连接器实例创建成功")

        # 初始化工作流引擎
        workflow = WorkflowEngine(
            cad_connector=cad_connector,
            cae_connector=cae_connector,
            mesher_connector=mesher_connector
        )

        print("OK: 工作流引擎初始化成功")

        # 检查预定义工作流是否可用
        assert hasattr(workflow, "PREDEFINED_WORKFLOWS")
        assert "stress_analysis" in workflow.PREDEFINED_WORKFLOWS
        assert "modal_analysis" in workflow.PREDEFINED_WORKFLOWS
        assert "topology_optimization" in workflow.PREDEFINED_WORKFLOWS

        print("OK: 预定义工作流检查成功")

        return True

    except Exception as e:
        print(f"ERROR: 工作流引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simulation_config():
    """测试SimulationConfig配置解析"""
    print("\n" + "=" * 60)
    print("测试仿真配置解析...")
    print("=" * 60)

    try:
        from core.types import SimulationConfig, FileFormat

        # 测试创建默认配置
        config = SimulationConfig(
            project_name="测试项目",
            description="用于验证Phase 1实现的测试配置",
            cad_file=Path("test_model.FCStd"),
            parameters={"thickness": 5.0, "fillet_radius": 3.0},
            element_size=2.0,
            material_name="Q235",
            analysis_type="static",
            solver="calculix"
        )

        print("OK: 配置对象创建成功")

        # 测试验证方法
        errors = config.validate()
        if errors:
            print(f"ERROR: 配置验证失败: {', '.join(errors)}")
        else:
            print("OK: 配置验证通过")

        # 测试YAML序列化/反序列化
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test_config.yaml"
            config.to_yaml(temp_path)
            print("OK: 配置YAML序列化成功")

            loaded_config = SimulationConfig.from_yaml(temp_path)
            print("OK: 配置YAML反序列化成功")

            assert loaded_config.project_name == config.project_name
            assert loaded_config.description == config.description
            assert loaded_config.cad_file == config.cad_file
            assert loaded_config.parameters == config.parameters
            assert loaded_config.element_size == config.element_size
            assert loaded_config.material_name == config.material_name
            assert loaded_config.analysis_type == config.analysis_type
            assert loaded_config.solver == config.solver

        print("OK: 配置序列化/反序列化一致性验证成功")

        return True

    except Exception as e:
        print(f"ERROR: 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """测试核心依赖是否可用"""
    print("\n" + "=" * 60)
    print("测试核心依赖...")
    print("=" * 60)

    required_deps = [
        "click", "rich", "yaml", "pint", "numpy"
    ]

    failed_deps = []

    # 依赖名称映射（模块名 → 包名）
    dep_map = {
        "yaml": "PyYAML",
        "click": "click",
        "rich": "rich",
        "pint": "pint",
        "numpy": "numpy"
    }

    for dep in required_deps:
        try:
            __import__(dep)
            print(f"OK: {dep_map.get(dep, dep)} 依赖可用")
        except ImportError:
            print(f"ERROR: {dep_map.get(dep, dep)} 依赖缺失")
            failed_deps.append(dep)

    return len(failed_deps) == 0

def main():
    """执行所有Phase 1测试"""
    print("CAE-CLI Phase 1 集成测试")
    print("=" * 60)

    tests = [
        ("连接器导入", test_import_connectors),
        ("工作流引擎", test_workflow_engine),
        ("配置解析", test_simulation_config),
        ("核心依赖", test_dependencies)
    ]

    all_passed = True
    passed_count = 0
    total_count = len(tests)

    for test_name, test_func in tests:
        try:
            success = test_func()
            if success:
                passed_count += 1
            else:
                all_passed = False
        except Exception as e:
            print(f"\nERROR: {test_name} 测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print("\n" + "=" * 60)
    print(f"测试结果: {passed_count}/{total_count} 个测试通过")
    print("=" * 60)

    if all_passed:
        print("\nSUCCESS: Phase 1 集成测试全部通过")
        print("\n项目架构验证成功!")
        print("\n关键成就:")
        print("- OK: 统一接口架构实现")
        print("- OK: CAD/CAE/Mesher 连接器集成")
        print("- OK: 工作流引擎配置完成")
        print("- OK: 核心数据格式标准化")
        print("- OK: 依赖管理策略实施")
        return 0
    else:
        print("\nFAILURE: Phase 1 集成测试部分失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())