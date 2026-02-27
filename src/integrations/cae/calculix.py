"""
CalculiX连接器 - 开源有限元分析软件集成

CalculiX是一个基于GNU GPL许可证的开源有限元分析软件，
支持线性和非线性结构分析、热分析、流体分析等。

此连接器提供与CalculiX命令行工具(ccx)的标准化接口。
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .._base.connectors import CAEConnector


class CalculiXConnector(CAEConnector):
    """CalculiX有限元分析软件连接器"""

    def __init__(self):
        self.ccx_path = None
        self.is_connected = False
        self.work_dir = None

    def connect(self) -> bool:
        """连接到CalculiX实例（检查ccx命令是否可用）"""
        try:
            # 查找ccx命令
            ccx_path = shutil.which("ccx")
            if ccx_path:
                self.ccx_path = Path(ccx_path)
                self.is_connected = True
                print(f"✓ 找到CalculiX: {self.ccx_path}")
                return True
            else:
                print("✗ 未找到CalculiX (ccx)命令")
                print("提示: 请安装CalculiX并确保ccx在PATH中")
                print("      Ubuntu/Debian: sudo apt-get install calculix-ccx")
                print("      Windows: 从https://www.calculix.de/下载")
                return False

        except Exception as e:
            print(f"连接CalculiX失败: {e}")
            return False

    def generate_mesh(self, geometry_file: Path, mesh_file: Path, element_size: float = 2.0) -> bool:
        """从几何文件生成网格

        注意：CalculiX本身不包含网格生成器，通常使用Gmsh生成网格。
        此方法创建一个简单的.inp文件占位符，实际项目中应集成Gmsh。
        """
        if not self.is_connected:
            if not self.connect():
                return False

        try:
            # 确保输出目录存在
            mesh_file.parent.mkdir(parents=True, exist_ok=True)

            # 创建简单的.inp文件（示例）
            # 实际实现应该调用Gmsh或使用其他网格生成器
            with open(mesh_file, "w", encoding="utf-8") as f:
                f.write(self._create_sample_inp(geometry_file, element_size))

            print(f"✓ 生成网格文件: {mesh_file}")
            print("  注意：这是一个示例网格，实际应使用Gmsh生成")
            return True

        except Exception as e:
            print(f"生成网格失败: {e}")
            return False

    def setup_simulation(self, mesh_file: Path, config: Dict[str, Any]) -> Path:
        """设置仿真分析

        根据配置创建CalculiX输入文件(.inp)
        """
        if not self.is_connected:
            if not self.connect():
                raise RuntimeError("CalculiX未连接")

        try:
            # 创建临时工作目录
            if not self.work_dir:
                self.work_dir = Path(tempfile.mkdtemp(prefix="calculix_"))

            # 生成输入文件名
            input_file = self.work_dir / f"{mesh_file.stem}.inp"

            # 根据配置类型生成不同的输入文件
            analysis_type = config.get("analysis_type", "static")

            if analysis_type == "static":
                inp_content = self._create_static_analysis(mesh_file, config)
            elif analysis_type == "modal":
                inp_content = self._create_modal_analysis(mesh_file, config)
            elif analysis_type == "thermal":
                inp_content = self._create_thermal_analysis(mesh_file, config)
            else:
                raise ValueError(f"不支持的分析类型: {analysis_type}")

            # 写入输入文件
            with open(input_file, "w", encoding="utf-8") as f:
                f.write(inp_content)

            print(f"✓ 创建输入文件: {input_file}")
            return input_file

        except Exception as e:
            print(f"设置仿真失败: {e}")
            raise

    def run_simulation(self, input_file: Path, output_dir: Optional[Path] = None) -> bool:
        """运行仿真分析"""
        if not self.is_connected:
            if not self.connect():
                return False

        try:
            # 设置输出目录
            if not output_dir:
                output_dir = input_file.parent

            output_dir.mkdir(parents=True, exist_ok=True)

            # 准备命令参数
            input_stem = input_file.stem
            cmd = [str(self.ccx_path), "-i", input_stem]

            print(f"⏳ 运行CalculiX仿真: {' '.join(cmd)}")

            # 切换到输入文件目录运行
            cwd = input_file.parent
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
            )

            # 检查结果
            if result.returncode == 0:
                print("✓ 仿真完成")

                # 检查输出文件
                expected_files = [f"{input_stem}.frd", f"{input_stem}.dat"]
                for f in expected_files:
                    if (cwd / f).exists():
                        shutil.move(cwd / f, output_dir / f)

                return True
            else:
                print(f"✗ 仿真失败 (退出码: {result.returncode})")
                if result.stderr:
                    print("错误输出:")
                    print(result.stderr[:500])  # 只显示前500字符
                return False

        except subprocess.TimeoutExpired:
            print("✗ 仿真超时 (5分钟)")
            return False
        except Exception as e:
            print(f"运行仿真失败: {e}")
            return False

    def read_results(self, result_file: Path) -> Dict[str, Any]:
        """读取仿真结果

        解析.frd结果文件，提取关键结果数据。
        注意：完整解析.frd文件较复杂，这里只提取基本信息。
        """
        try:
            if not result_file.exists():
                raise FileNotFoundError(f"结果文件不存在: {result_file}")

            results = {
                "file_path": str(result_file),
                "file_size": result_file.stat().st_size,
                "analysis_type": "unknown",
                "nodes": 0,
                "elements": 0,
                "max_stress": None,
                "max_displacement": None,
                "success": True,
            }

            # 尝试解析.frd文件
            if result_file.suffix.lower() == ".frd":
                results.update(self._parse_frd_file(result_file))

            # 尝试解析.dat文件（如果有）
            dat_file = result_file.with_suffix(".dat")
            if dat_file.exists():
                results.update(self._parse_dat_file(dat_file))

            return results

        except Exception as e:
            print(f"读取结果失败: {e}")
            return {
                "file_path": str(result_file),
                "error": str(e),
                "success": False,
            }

    def get_supported_analysis_types(self) -> List[str]:
        """获取支持的分析类型"""
        return ["static", "modal", "thermal"]

    # ========== 内部辅助方法 ==========

    def _create_sample_inp(self, geometry_file: Path, element_size: float) -> str:
        """创建示例.inp文件"""
        return f"""** Sample CalculiX input file
** Generated from: {geometry_file.name}
** Element size: {element_size} mm

*NODE
1, 0.0, 0.0, 0.0
2, 10.0, 0.0, 0.0
3, 10.0, 5.0, 0.0
4, 0.0, 5.0, 0.0
5, 0.0, 0.0, 3.0
6, 10.0, 0.0, 3.0
7, 10.0, 5.0, 3.0
8, 0.0, 5.0, 3.0

*ELEMENT, TYPE=C3D8, ELSET=PART1
1, 1, 2, 3, 4, 5, 6, 7, 8

*MATERIAL, NAME=STEEL
*ELASTIC
210000.0, 0.3
*DENSITY
7.85E-9

*SOLID SECTION, ELSET=PART1, MATERIAL=STEEL

*STEP
*STATIC
*BOUNDARY
1, 1, 3, 0.0  # 固定节点1的XYZ方向
4, 1, 3, 0.0  # 固定节点4的XYZ方向

*CLOAD
8, 3, -100.0  # 在节点8的Z方向施加-100N载荷

*NODE PRINT
U
*EL PRINT
S
*END STEP
"""

    def _create_static_analysis(self, mesh_file: Path, config: Dict[str, Any]) -> str:
        """创建静态分析输入文件"""
        material = config.get("material", {"E": 210000.0, "nu": 0.3, "density": 7.85e-9})
        loads = config.get("loads", [])
        constraints = config.get("constraints", [])

        inp = f"""** Static analysis input file
** Mesh: {mesh_file.name}
** Material: {material.get("name", "STEEL")}

*INCLUDE, INPUT={mesh_file.name}

*MATERIAL, NAME={material.get("name", "STEEL")}
*ELASTIC
{material.get("E", 210000.0)}, {material.get("nu", 0.3)}
*DENSITY
{material.get("density", 7.85e-9)}

*STEP
*STATIC
"""

        # 添加边界条件
        for constraint in constraints:
            inp += "*BOUNDARY\n"
            inp += f"{constraint.get('node_set', 'FIXED')}, {constraint.get('dofs', '1,3,0.0')}\n"

        # 添加载荷
        for load in loads:
            inp += "*CLOAD\n"
            inp += f"{load.get('node_set', 'LOAD_NODES')}, {load.get('dof', 3)}, {load.get('value', -100.0)}\n"

        inp += """*NODE PRINT
U
*EL PRINT
S,E
*END STEP
"""

        return inp

    def _create_modal_analysis(self, mesh_file: Path, config: Dict[str, Any]) -> str:
        """创建模态分析输入文件"""
        num_modes = config.get("num_modes", 10)

        inp = f"""** Modal analysis input file
** Mesh: {mesh_file.name}
** Number of modes: {num_modes}

*INCLUDE, INPUT={mesh_file.name}

*MATERIAL, NAME=STEEL
*ELASTIC
210000.0, 0.3
*DENSITY
7.85E-9

*STEP
*FREQUENCY
{num_modes}
*BOUNDARY
FIXED, 1, 3, 0.0
*NODE PRINT
U
*EL PRINT
S,E
*END STEP
"""

        return inp

    def _create_thermal_analysis(self, mesh_file: Path, config: Dict[str, Any]) -> str:
        """创建热分析输入文件"""
        inp = f"""** Thermal analysis input file
** Mesh: {mesh_file.name}

*INCLUDE, INPUT={mesh_file.name}

*MATERIAL, NAME=STEEL
*CONDUCTIVITY
50.0
*SPECIFIC HEAT
500.0
*DENSITY
7.85E-9

*STEP
*HEAT TRANSFER
*BOUNDARY
FIXED, 11, 11, 293.0  # 固定温度293K
*DFLUX
HEAT_FLUX, 12, 1000.0  # 热通量1000W/m²
*NODE PRINT
NT
*EL PRINT
HFL
*END STEP
"""

        return inp

    def _parse_frd_file(self, frd_file: Path) -> Dict[str, Any]:
        """解析.frd文件（简化版本）"""
        results = {
            "analysis_type": "unknown",
            "nodes": 0,
            "elements": 0,
            "steps": [],
        }

        try:
            with open(frd_file, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            node_count = 0
            element_count = 0
            current_step = None

            for line in lines:
                if "C CalculiX" in line:
                    results["analysis_type"] = line.strip()
                elif "1PSTEP" in line:
                    # 新的分析步
                    parts = line.split()
                    if len(parts) >= 4:
                        step_num = int(parts[2])
                        step_type = parts[3]
                        current_step = {
                            "number": step_num,
                            "type": step_type,
                            "time": 0.0,
                        }
                        results["steps"].append(current_step)
                elif "2C" in line and "DISPLACEMENT" in line:
                    results["has_displacements"] = True
                elif "2C" in line and "STRESS" in line:
                    results["has_stresses"] = True
                elif " -1" in line and " 1 " in line:
                    # 节点定义
                    node_count += 1
                elif " -1" in line and " 2 " in line:
                    # 单元定义
                    element_count += 1

            results["nodes"] = node_count
            results["elements"] = element_count

        except Exception as e:
            print(f"解析.frd文件失败: {e}")

        return results

    def _parse_dat_file(self, dat_file: Path) -> Dict[str, Any]:
        """解析.dat文件（简化版本）"""
        results = {
            "max_displacement": 0.0,
            "max_stress": 0.0,
            "reactions": [],
        }

        try:
            with open(dat_file, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 简单搜索关键信息
            import re

            # 查找最大位移
            disp_pattern = r"displacement.*?magnitude.*?(\d+\.\d+E?[+-]?\d*)"
            disp_matches = re.findall(disp_pattern, content, re.IGNORECASE)
            if disp_matches:
                try:
                    results["max_displacement"] = float(disp_matches[-1])
                except (ValueError, IndexError):
                    pass

            # 查找最大应力
            stress_pattern = r"stress.*?(\d+\.\d+E?[+-]?\d*)"
            stress_matches = re.findall(stress_pattern, content, re.IGNORECASE)
            if stress_matches:
                try:
                    results["max_stress"] = float(stress_matches[-1])
                except (ValueError, IndexError):
                    pass

        except Exception as e:
            print(f"解析.dat文件失败: {e}")

        return results

    def cleanup(self):
        """清理工作目录"""
        if self.work_dir and self.work_dir.exists():
            try:
                shutil.rmtree(self.work_dir)
                self.work_dir = None
            except OSError:
                pass


class CalculiXConnectorMock(CalculiXConnector):
    """CalculiX连接器模拟器（用于测试）"""

    def __init__(self):
        super().__init__()
        self.mock_mode = True

    def connect(self) -> bool:
        print("[模拟模式] 连接CalculiX")
        self.is_connected = True
        return True

    def generate_mesh(self, geometry_file: Path, mesh_file: Path, element_size: float = 2.0) -> bool:
        print(f"[模拟模式] 生成网格: {geometry_file} -> {mesh_file}")
        mesh_file.parent.mkdir(parents=True, exist_ok=True)
        mesh_file.write_text("** Mock mesh file\n")
        return True

    def run_simulation(self, input_file: Path, output_dir: Optional[Path] = None) -> bool:
        print(f"[模拟模式] 运行仿真: {input_file}")
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            # 创建模拟结果文件
            stem = input_file.stem
            (output_dir / f"{stem}.frd").write_text("** Mock FRD file\n")
            (output_dir / f"{stem}.dat").write_text("** Mock DAT file\n")
        return True
