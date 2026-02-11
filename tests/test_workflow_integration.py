"""
端到端工作流集成测试
测试完整的CAD->网格生成->CAE求解流程
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, Optional, List

from integrations._base.workflow import WorkflowEngine
from integrations._base.connectors import CADConnector, CAEConnector, FileFormat


class MockCADConnector(CADConnector):
    """模拟CAD连接器"""

    def __init__(self):
        super().__init__()
        self.connected = False
        self.loaded_model = None
        self.parameters = {}
        self.exported_files = []

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self) -> bool:
        self.connected = False
        return True

    def load_model(self, file_path: Path) -> bool:
        self.loaded_model = file_path
        return True

    def get_parameter(self, name: str) -> Optional[float]:
        return self.parameters.get(name, 10.0)  # 默认值

    def get_parameters(self) -> Dict[str, Any]:
        return {"thickness": 10.0, "width": 50.0}

    def set_parameter(self, name: str, value: float) -> bool:
        self.parameters[name] = value
        return True

    def rebuild(self) -> bool:
        return True

    def export_step(self, output_path: Path) -> bool:
        # 创建空文件以模拟导出
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("Mock STEP file")
        self.exported_files.append(output_path)
        return True

    def get_supported_formats(self) -> List[FileFormat]:
        from integrations._base.connectors import FileFormat

        return [FileFormat.STEP, FileFormat.STL]


class MockMesherConnector(CAEConnector):
    """模拟网格生成器连接器"""

    def __init__(self):
        super().__init__()
        self.connected = False
        self.generated_meshes = []

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self) -> bool:
        self.connected = False
        return True

    def generate_mesh(
        self, geometry_file: Path, mesh_file: Path, element_size: float = 2.0
    ) -> bool:
        # 创建空网格文件
        mesh_file.parent.mkdir(parents=True, exist_ok=True)
        mesh_file.write_text("Mock mesh file")
        self.generated_meshes.append(
            {"geometry": geometry_file, "mesh": mesh_file, "element_size": element_size}
        )
        return True

    def setup_simulation(self, mesh_file: Path, config: Dict[str, Any]) -> Path:
        # 不实现，仅用于网格生成
        raise NotImplementedError("MockMesherConnector仅用于网格生成")

    def run_simulation(
        self, input_file: Path, output_dir: Optional[Path] = None
    ) -> bool:
        # 不实现
        raise NotImplementedError("MockMesherConnector仅用于网格生成")

    def read_results(self, result_file: Path) -> Dict[str, Any]:
        # 不实现
        raise NotImplementedError("MockMesherConnector仅用于网格生成")

    def get_supported_analysis_types(self) -> List[str]:
        return ["static", "modal"]  # 网格生成器通常支持多种分析类型


class MockCAEConnector(CAEConnector):
    """模拟CAE求解器连接器"""

    def __init__(self):
        super().__init__()
        self.connected = False
        self.setup_simulations = []
        self.run_simulations = []

    def connect(self) -> bool:
        self.connected = True
        return True

    def disconnect(self) -> bool:
        self.connected = False
        return True

    def generate_mesh(
        self, geometry_file: Path, mesh_file: Path, element_size: float = 2.0
    ) -> bool:
        # 不实现，使用独立的网格生成器
        raise NotImplementedError("MockCAEConnector不生成网格")

    def setup_simulation(self, mesh_file: Path, config: Dict[str, Any]) -> Path:
        # 创建输入文件
        output_dir = mesh_file.parent
        input_file = output_dir / "simulation.inp"
        input_file.write_text("Mock simulation input")
        self.setup_simulations.append(
            {"mesh": mesh_file, "config": config, "input": input_file}
        )
        return input_file

    def run_simulation(
        self, input_file: Path, output_dir: Optional[Path] = None
    ) -> bool:
        # 创建结果文件
        if output_dir is None:
            output_dir = input_file.parent
        result_file = output_dir / "results.vtk"
        result_file.write_text("Mock results")
        self.run_simulations.append(
            {"input": input_file, "output_dir": output_dir, "result": result_file}
        )
        return True

    def read_results(self, result_file: Path) -> Dict[str, Any]:
        return {
            "max_stress": 250.5,
            "min_stress": 10.2,
            "safety_factor": 2.1,
            "status": "converged",
        }

    def get_supported_analysis_types(self) -> List[str]:
        return ["static", "modal", "thermal"]


def test_workflow_with_standalone_mesher():
    """测试使用独立网格生成器的工作流"""
    # 创建模拟连接器
    cad_connector = MockCADConnector()
    mesher_connector = MockMesherConnector()
    cae_connector = MockCAEConnector()

    # 创建工作流引擎（传递独立的网格生成器）
    engine = WorkflowEngine(cad_connector, cae_connector, mesher_connector)

    # 准备测试配置
    config = {
        "cad_file": "test_model.FCStd",
        "parameters": {"thickness": 12.0},
        "mesh_element_size": 1.5,
        "output_dir": "test_output",
        "material": "steel",
        "loads": [{"type": "force", "value": 1000}],
        "constraints": [{"type": "fixed", "location": "bottom"}],
    }

    # 运行工作流
    result = engine.run_workflow("stress_analysis", config)

    # 验证结果
    assert result["status"] == "completed"
    assert result["workflow"] == "stress_analysis"

    # 验证步骤执行
    steps = result["steps"]
    assert len(steps) == 8  # stress_analysis有8个步骤

    # 验证CAD连接器被调用
    assert cad_connector.connected
    assert cad_connector.loaded_model == Path("test_model.FCStd")
    assert "thickness" in cad_connector.parameters
    assert cad_connector.parameters["thickness"] == 12.0
    assert len(cad_connector.exported_files) == 1

    # 验证网格生成器被调用（而不是CAE连接器）
    assert mesher_connector.connected
    assert len(mesher_connector.generated_meshes) == 1
    mesh_info = mesher_connector.generated_meshes[0]
    assert mesh_info["element_size"] == 1.5

    # 验证CAE连接器被调用进行仿真设置和求解
    assert cae_connector.connected
    assert len(cae_connector.setup_simulations) == 1
    assert len(cae_connector.run_simulations) == 1

    # 验证结果提取
    assert "max_stress" in engine.results
    assert engine.results["max_stress"] == 250.5

    # 清理测试文件
    import shutil

    if Path("test_output").exists():
        shutil.rmtree("test_output")


def test_workflow_without_mesher():
    """测试没有独立网格生成器的工作流（向后兼容）"""
    # 创建模拟连接器（CAE连接器也处理网格生成）
    cad_connector = MockCADConnector()

    class MockCAEWithMeshConnector(MockCAEConnector):
        """既能生成网格又能求解的CAE连接器"""

        def generate_mesh(
            self, geometry_file: Path, mesh_file: Path, element_size: float = 2.0
        ) -> bool:
            mesh_file.parent.mkdir(parents=True, exist_ok=True)
            mesh_file.write_text("Mock mesh from CAE connector")
            return True

    cae_connector = MockCAEWithMeshConnector()

    # 创建工作流引擎（不传递网格生成器）
    engine = WorkflowEngine(cad_connector, cae_connector)

    # 准备测试配置
    config = {
        "cad_file": "test_model.FCStd",
        "parameters": {"thickness": 10.0},
        "mesh_element_size": 2.0,
        "output_dir": "test_output_legacy",
    }

    # 运行工作流
    result = engine.run_workflow("stress_analysis", config)

    # 验证结果
    assert result["status"] == "completed"

    # 清理测试文件
    import shutil

    if Path("test_output_legacy").exists():
        shutil.rmtree("test_output_legacy")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
