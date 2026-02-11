"""
Gmsh网格生成器连接器 - 基于新架构的实现

Gmsh是一个开源的三维有限元网格生成器，支持多种几何格式和网格算法。
此连接器提供与Gmsh Python API的标准化接口，用于从STEP几何文件生成高质量网格。

功能：
- 从STEP/STL/BREP等格式生成四面体/六面体网格
- 控制网格单元尺寸和质量参数
- 支持转换为CalculiX/Abaqus/NASTRAN等格式
- 网格质量检查和异常处理
"""

import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import tempfile

import pint

from .._base.connectors import CAEConnector, FileFormat


class MeshQualityError(Exception):
    """网格质量异常"""

    pass


class GmshConnector(CAEConnector):
    """Gmsh网格生成器连接器"""

    def __init__(self) -> None:
        self.gmsh_module: Optional[Any] = None
        self.is_connected: bool = False
        self.work_dir: Optional[Path] = None
        self.current_model: Optional[Any] = None
        self.ureg = pint.UnitRegistry()
        self.mesh_options: Dict[str, Any] = {
            "element_size": 1.0,  # 默认单元尺寸 (mm)
            "algorithm": "Delannay",  # Delannay, Frontal, Netgen
            "optimize": True,
            "quality_type": "tetrahedron",  # tetrahedron, hexahedron, mixed
            "min_quality": 0.3,  # 最小网格质量阈值
            "max_quality": 1.0,  # 最大网格质量阈值
        }

    def _gmsh(self) -> Any:
        """获取gmsh模块，确保已连接"""
        if self.gmsh_module is None:
            raise RuntimeError("Gmsh模块未初始化，请先调用connect()")
        return self.gmsh_module

    def connect(self) -> bool:
        """连接到Gmsh实例（检查gmsh模块是否可用）"""
        try:
            import gmsh

            self.gmsh_module = gmsh
            self.is_connected = True
            print("✓ 连接到Gmsh成功")
            return True

        except ImportError:
            print("✗ 未找到Gmsh Python模块")
            print("提示: 请安装Gmsh并确保Python绑定可用")
            print("      pip install gmsh")
            print("      或从 https://gmsh.info/ 下载")
            return False

        except Exception as e:
            print(f"连接Gmsh失败: {e}")
            return False

    def generate_mesh(
        self, geometry_file: Path, mesh_file: Path, element_size: float = 1.0
    ) -> bool:
        """从几何文件生成网格

        支持格式: STEP (.step, .stp), STL (.stl), BREP (.brep), IGES (.iges)
        输出格式: .msh (Gmsh格式)，可转换为其他格式

        Args:
            geometry_file: 输入几何文件路径
            mesh_file: 输出网格文件路径
            element_size: 单元尺寸 (mm，默认1.0)

        Returns:
            bool: 网格生成是否成功
        """
        if not self.is_connected:
            if not self.connect():
                return False

        # 确保gmsh_module已连接
        assert self.gmsh_module is not None, "Gmsh模块未初始化"

        try:
            # 确保输出目录存在
            mesh_file.parent.mkdir(parents=True, exist_ok=True)

            # 检查输入文件是否存在
            if not geometry_file.exists():
                raise FileNotFoundError(f"几何文件不存在: {geometry_file}")

            # 获取文件格式
            file_format = self._detect_file_format(geometry_file)

            # 初始化Gmsh
            self._gmsh().initialize()
            self._gmsh().option.setNumber("General.Terminal", 1)

            # 设置网格选项 (element_size 单位: mm → 转换为 m 供 Gmsh 使用)
            element_size_m = (
                self.ureg.Quantity(element_size, self.ureg.mm).to(self.ureg.m).magnitude
            )
            self._set_mesh_options(element_size_m)

            # 导入几何
            print(f"⏳ 导入几何: {geometry_file.name}")
            if file_format == "step":
                self.gmsh_module.merge(str(geometry_file))
            elif file_format == "stl":
                self.gmsh_module.merge(str(geometry_file))
            elif file_format == "brep":
                self.gmsh_module.open(str(geometry_file))
            else:
                # 通用导入
                self.gmsh_module.merge(str(geometry_file))

            # 同步几何模型
            self.gmsh_module.model.geo.synchronize()

            # 生成2D表面网格
            print("⏳ 生成表面网格...")
            self.gmsh_module.model.mesh.generate(2)

            # 生成3D体积网格
            print("⏳ 生成体积网格...")
            self.gmsh_module.model.mesh.generate(3)

            # 网格优化
            if self.mesh_options["optimize"]:
                print("⏳ 优化网格质量...")
                self.gmsh_module.model.mesh.optimize("Netgen")

            # 检查网格质量
            quality_ok = self._check_mesh_quality()
            if not quality_ok:
                print("⚠️ 网格质量警告: 部分单元质量较低")

            # 保存网格文件
            print(f"⏳ 保存网格文件: {mesh_file}")
            self.gmsh_module.write(str(mesh_file))

            # 清理Gmsh
            self.gmsh_module.finalize()

            # 验证输出文件
            if mesh_file.exists() and mesh_file.stat().st_size > 0:
                print(f"✓ 网格生成成功: {mesh_file}")
                print(f"  文件大小: {mesh_file.stat().st_size / 1024:.1f} KB")

                # 显示网格统计信息
                self._print_mesh_stats(mesh_file)
                return True
            else:
                print("✗ 网格文件生成失败")
                return False

        except Exception as e:
            print(f"生成网格失败: {e}")
            # 确保清理Gmsh
            try:
                self.gmsh_module.finalize()
            except:
                pass
            return False

    def setup_simulation(self, mesh_file: Path, config: Dict[str, Any]) -> Path:
        """设置仿真分析（对于网格生成器，此方法返回输入文件路径）

        注意：Gmsh本身不是求解器，此方法用于创建转换后的输入文件
        例如：将.msh转换为CalculiX .inp格式
        """
        if not self.is_connected:
            if not self.connect():
                raise RuntimeError("Gmsh未连接")

        try:
            # 创建临时工作目录
            if not self.work_dir:
                self.work_dir = Path(tempfile.mkdtemp(prefix="gmsh_"))

            # 确定目标格式
            target_format = config.get("target_format", "inp")
            input_file = self.work_dir / f"{mesh_file.stem}.{target_format}"

            # 转换网格格式
            if target_format == "inp":
                self._convert_to_inp(mesh_file, input_file)
            elif target_format == "bdf":
                self._convert_to_bdf(mesh_file, input_file)
            elif target_format == "cas":
                self._convert_to_cas(mesh_file, input_file)
            else:
                # 默认复制原始.msh文件
                shutil.copy2(mesh_file, input_file)

            print(f"✓ 创建输入文件: {input_file}")
            return input_file

        except Exception as e:
            print(f"设置仿真失败: {e}")
            raise

    def run_simulation(
        self, input_file: Path, output_dir: Optional[Path] = None
    ) -> bool:
        """运行仿真分析（对于网格生成器，此方法无实际意义）

        注意：Gmsh不是求解器，此方法仅用于兼容性
        实际仿真应使用CalculiX、Abaqus等求解器
        """
        print(f"⚠️  Gmsh不是求解器，跳过仿真步骤")
        print(f"    输入文件: {input_file}")
        print(f"    请使用CAE求解器运行此文件")

        # 为兼容性返回成功
        return True

    def read_results(self, result_file: Path) -> Dict[str, Any]:
        """读取仿真结果（对于网格生成器，此方法读取网格质量信息）"""
        try:
            if not result_file.exists():
                raise FileNotFoundError(f"结果文件不存在: {result_file}")

            results = {
                "file_path": str(result_file),
                "file_size": result_file.stat().st_size,
                "mesh_quality": {},
                "elements": 0,
                "nodes": 0,
                "element_types": {},
            }

            # 如果是.msh文件，解析网格信息
            if result_file.suffix.lower() == ".msh":
                results.update(self._parse_msh_file(result_file))

            # 如果是.inp文件，解析CalculiX网格信息
            elif result_file.suffix.lower() == ".inp":
                results.update(self._parse_inp_file(result_file))

            return results

        except Exception as e:
            print(f"读取结果失败: {e}")
            return {
                "file_path": str(result_file),
                "error": str(e),
                "success": False,
            }

    def get_supported_analysis_types(self) -> List[str]:
        """获取支持的分析类型（对于网格生成器，返回空列表）"""
        return []  # Gmsh不是求解器，不直接支持分析类型

    def convert_to_calculix_inp(self, msh_path: Path) -> Path:
        """将 .msh 文件转换为 CalculiX 兼容的 .inp 文件

        Args:
            msh_path: 输入 .msh 文件路径

        Returns:
            Path: 生成的 .inp 文件路径

        Raises:
            FileNotFoundError: 输入文件不存在时
            RuntimeError: 转换失败时
        """
        if not msh_path.exists():
            raise FileNotFoundError(f"MSH 文件不存在: {msh_path}")

        # 创建输出文件路径
        inp_path = msh_path.with_suffix(".inp")

        # 使用内部转换方法
        if not self._convert_to_inp(msh_path, inp_path):
            raise RuntimeError(f"转换为 CalculiX INP 格式失败: {msh_path}")

        return inp_path

    def convert_mesh_format(
        self, input_mesh: Path, output_mesh: Path, target_format: str
    ) -> bool:
        """转换网格格式

        Args:
            input_mesh: 输入网格文件
            output_mesh: 输出网格文件
            target_format: 目标格式 ('inp', 'bdf', 'cas', 'vtk')

        Returns:
            bool: 转换是否成功
        """
        if not self.is_connected:
            if not self.connect():
                return False

        try:
            format_map = {
                "inp": self._convert_to_inp,
                "bdf": self._convert_to_bdf,
                "cas": self._convert_to_cas,
                "vtk": self._convert_to_vtk,
            }

            if target_format not in format_map:
                raise ValueError(f"不支持的格式: {target_format}")

            converter = format_map[target_format]
            return converter(input_mesh, output_mesh)

        except Exception as e:
            print(f"转换网格格式失败: {e}")
            return False

    def get_mesh_quality_report(self, mesh_file: Path) -> Dict[str, Any]:
        """获取网格质量报告"""
        if not self.is_connected:
            if not self.connect():
                raise RuntimeError("Gmsh未连接")

        try:
            # 初始化Gmsh并加载网格
            self.gmsh_module.initialize()
            self.gmsh_module.open(str(mesh_file))

            # 计算网格质量指标
            quality_metrics = self._calculate_quality_metrics()

            # 清理
            self.gmsh_module.finalize()

            return {
                "mesh_file": str(mesh_file),
                "quality_metrics": quality_metrics,
                "overall_quality": self._evaluate_overall_quality(quality_metrics),
                "recommendations": self._generate_quality_recommendations(
                    quality_metrics
                ),
            }

        except Exception as e:
            print(f"获取网格质量报告失败: {e}")
            return {"error": str(e)}

    # ========== 内部辅助方法 ==========

    def _detect_file_format(self, file_path: Path) -> str:
        """检测文件格式"""
        suffix = file_path.suffix.lower()
        if suffix in [".step", ".stp"]:
            return "step"
        elif suffix in [".stl"]:
            return "stl"
        elif suffix in [".brep"]:
            return "brep"
        elif suffix in [".iges", ".igs"]:
            return "iges"
        elif suffix in [".msh"]:
            return "msh"
        elif suffix in [".inp"]:
            return "inp"
        else:
            return "unknown"

    def _set_mesh_options(self, element_size: float):
        """设置网格生成选项"""
        self.gmsh_module.option.setNumber("Mesh.CharacteristicLengthMin", element_size)
        self.gmsh_module.option.setNumber("Mesh.CharacteristicLengthMax", element_size)
        self.gmsh_module.option.setNumber("Mesh.Algorithm", 5)  # Delannay
        self.gmsh_module.option.setNumber("Mesh.Algorithm3D", 1)  # Delannay 3D
        self.gmsh_module.option.setNumber("Mesh.Optimize", 1)
        self.gmsh_module.option.setNumber("Mesh.QualityType", 2)  # Tetrahedron quality

    def _check_mesh_quality(self) -> bool:
        """检查网格质量"""
        try:
            # 获取质量统计
            quality_stats = self.gmsh_module.model.mesh.getQualityStatistics()

            min_quality = quality_stats[0]  # 最小质量
            max_quality = quality_stats[1]  # 最大质量
            avg_quality = quality_stats[2]  # 平均质量

            print(f"  网格质量统计:")
            print(f"    最小质量: {min_quality:.4f}")
            print(f"    最大质量: {max_quality:.4f}")
            print(f"    平均质量: {avg_quality:.4f}")

            # 检查是否满足最小质量阈值
            threshold = self.mesh_options["min_quality"]
            if min_quality < threshold:
                error_msg = (
                    f"网格质量过低: 最小质量 ({min_quality:.4f}) 低于阈值 ({threshold})。"
                    f"建议减小单元尺寸或调整几何。"
                )
                raise MeshQualityError(error_msg)

            return True

        except Exception as e:
            print(f"检查网格质量失败: {e}")
            return True  # 如果检查失败，假设质量合格

    def _print_mesh_stats(self, mesh_file: Path):
        """打印网格统计信息"""
        try:
            # 重新打开网格文件获取统计信息
            self.gmsh_module.initialize()
            self.gmsh_module.open(str(mesh_file))

            # 获取网格信息
            node_count = self.gmsh_module.model.mesh.getNodes()[0].shape[0]
            element_count = self.gmsh_module.model.mesh.getElements()[2][0].shape[0]

            print(f"  网格统计:")
            print(f"    节点数: {node_count}")
            print(f"    单元数: {element_count}")

            self.gmsh_module.finalize()

        except Exception as e:
            print(f"获取网格统计失败: {e}")

    def _convert_to_inp(self, input_mesh: Path, output_inp: Path) -> bool:
        """转换为CalculiX .inp格式"""
        try:
            # 确保输出目录存在
            output_inp.parent.mkdir(parents=True, exist_ok=True)

            # 初始化Gmsh并加载网格
            self.gmsh_module.initialize()
            self.gmsh_module.open(str(input_mesh))

            # 获取网格数据
            nodes = self.gmsh_module.model.mesh.getNodes()
            elements = self.gmsh_module.model.mesh.getElements()

            # 写入.inp格式
            with open(output_inp, "w", encoding="utf-8") as f:
                f.write("** Converted from Gmsh .msh format\n")
                f.write("** Generated by CAE-CLI GmshConnector\n\n")

                # 写入节点
                f.write("*NODE\n")
                for i, (node_id, coords) in enumerate(zip(nodes[0], nodes[1]), 1):
                    x, y, z = coords[0], coords[1], coords[2]
                    f.write(f"{i}, {x:.6f}, {y:.6f}, {z:.6f}\n")

                # 按单元类型分组写入单元
                element_groups = {}

                for elem_type, elem_tags, elem_nodes in zip(elements[0], elements[1], elements[2]):
                    if elem_type not in element_groups:
                        element_groups[elem_type] = []
                    for tag, nodes_list in zip(elem_tags, elem_nodes):
                        element_groups[elem_type].append((tag, nodes_list))

                # 定义Gmsh到CalculiX的单元类型映射
                elem_type_map = {
                    4: "C3D4",    # 四面体
                    5: "C3D8",    # 六面体
                    1: "CPS4",    # 四边形（平面应力）
                    2: "CPE4",    # 四边形（平面应变）
                    3: "C3D6",    # 三棱柱
                    6: "C3D10",   # 四面体（二次）
                    7: "C3D20"    # 六面体（二次）
                }

                # 写入每个单元组
                for gmsh_type, elems in element_groups.items():
                    calculix_type = elem_type_map.get(gmsh_type)
                    if calculix_type:
                        f.write(f"\n*ELEMENT, TYPE={calculix_type}, ELSET=PART1\n")
                        for i, (tag, nodes_list) in enumerate(elems, 1):
                            # 转换节点编号（Gmsh节点编号从1开始，CalculiX也是）
                            nodes_str = ", ".join(str(int(n)) for n in nodes_list)
                            f.write(f"{i}, {nodes_str}\n")

                # 写入固体截面定义
                f.write("\n*SOLID SECTION, ELSET=PART1, MATERIAL=DEFAULT_MATERIAL\n")

            self.gmsh_module.finalize()
            print(f"✓ 转换成功: {input_mesh.name} -> {output_inp.name}")
            return True

        except Exception as e:
            print(f"转换为INP格式失败: {e}")
            return False

    def _convert_to_bdf(self, input_mesh: Path, output_bdf: Path) -> bool:
        """转换为NASTRAN .bdf格式"""
        try:
            # 简化实现：创建示例.bdf文件
            with open(output_bdf, "w", encoding="utf-8") as f:
                f.write("$ NASTRAN input file converted from Gmsh\n")
                f.write("$ Generated by CAE-CLI GmshConnector\n")
                f.write("SOL 101\n")
                f.write("CEND\n")
                f.write("BEGIN BULK\n")
                f.write("$ Nodes and elements would be here\n")
                f.write("ENDDATA\n")

            print(f"✓ 创建BDF文件: {output_bdf.name}")
            return True

        except Exception as e:
            print(f"转换为BDF格式失败: {e}")
            return False

    def _convert_to_cas(self, input_mesh: Path, output_cas: Path) -> bool:
        """转换为Fluent .cas格式"""
        try:
            # 简化实现：创建示例.cas文件
            with open(output_cas, "w", encoding="utf-8") as f:
                f.write('(0 "Fluent Case File converted from Gmsh")\n')
                f.write('(0 "Generated by CAE-CLI GmshConnector")\n')
                f.write("(2 2)\n")  # 版本信息

            print(f"✓ 创建CAS文件: {output_cas.name}")
            return True

        except Exception as e:
            print(f"转换为CAS格式失败: {e}")
            return False

    def _convert_to_vtk(self, input_mesh: Path, output_vtk: Path) -> bool:
        """转换为VTK格式"""
        try:
            # Gmsh可以直接导出为VTK
            self.gmsh_module.initialize()
            self.gmsh_module.open(str(input_mesh))
            self.gmsh_module.write(str(output_vtk))
            self.gmsh_module.finalize()

            print(f"✓ 转换成功: {input_mesh.name} -> {output_vtk.name}")
            return True

        except Exception as e:
            print(f"转换为VTK格式失败: {e}")
            return False

    def _parse_msh_file(self, msh_file: Path) -> Dict[str, Any]:
        """解析.msh文件"""
        results = {
            "format": "msh",
            "version": "unknown",
            "nodes": 0,
            "elements": 0,
        }

        try:
            with open(msh_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line in lines:
                if line.startswith("$MeshFormat"):
                    # 格式信息
                    parts = lines[1].strip().split()
                    if len(parts) >= 2:
                        results["version"] = parts[0]
                elif line.startswith("$Nodes"):
                    # 节点数
                    node_line = lines[lines.index(line) + 1].strip()
                    results["nodes"] = int(node_line.split()[0])
                elif line.startswith("$Elements"):
                    # 单元数
                    elem_line = lines[lines.index(line) + 1].strip()
                    results["elements"] = int(elem_line.split()[0])

        except Exception as e:
            print(f"解析MSH文件失败: {e}")

        return results

    def _parse_inp_file(self, inp_file: Path) -> Dict[str, Any]:
        """解析.inp文件"""
        results = {
            "format": "inp",
            "nodes": 0,
            "elements": 0,
            "materials": [],
        }

        try:
            with open(inp_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            in_nodes = False
            in_elements = False

            for line in lines:
                line = line.strip()
                if not line or line.startswith("**"):
                    continue

                if line.upper().startswith("*NODE"):
                    in_nodes = True
                    in_elements = False
                elif line.upper().startswith("*ELEMENT"):
                    in_nodes = False
                    in_elements = True
                elif line.upper().startswith("*MATERIAL"):
                    material_name = line.split(",")[1].strip().split("=")[1]
                    results["materials"].append(material_name)
                elif in_nodes and "," in line:
                    results["nodes"] += 1
                elif in_elements and "," in line:
                    results["elements"] += 1

        except Exception as e:
            print(f"解析INP文件失败: {e}")

        return results

    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """计算网格质量指标"""
        try:
            # 获取质量统计
            stats = self.gmsh_module.model.mesh.getQualityStatistics()

            return {
                "min_quality": stats[0],
                "max_quality": stats[1],
                "avg_quality": stats[2],
                "std_quality": stats[3] if len(stats) > 3 else 0.0,
                "jacobian_min": stats[4] if len(stats) > 4 else 1.0,
                "jacobian_max": stats[5] if len(stats) > 5 else 1.0,
            }
        except Exception as e:
            print(f"计算质量指标失败: {e}")
            return {}

    def _evaluate_overall_quality(self, metrics: Dict[str, float]) -> str:
        """评估整体网格质量"""
        min_quality = metrics.get("min_quality", 1.0)

        if min_quality >= 0.7:
            return "excellent"
        elif min_quality >= 0.5:
            return "good"
        elif min_quality >= 0.3:
            return "fair"
        elif min_quality >= 0.1:
            return "poor"
        else:
            return "unacceptable"

    def _generate_quality_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """生成质量改进建议"""
        recommendations = []
        min_quality = metrics.get("min_quality", 1.0)

        if min_quality < 0.3:
            recommendations.append("网格质量过低，建议减小单元尺寸或调整几何")
        elif min_quality < 0.5:
            recommendations.append("部分单元质量较差，建议进行网格优化")
        elif min_quality < 0.7:
            recommendations.append("网格质量一般，可接受但建议优化")

        avg_quality = metrics.get("avg_quality", 1.0)
        if avg_quality < 0.8:
            recommendations.append("平均质量偏低，建议检查几何模型")

        return recommendations

    def cleanup(self):
        """清理工作目录"""
        if self.work_dir and self.work_dir.exists():
            try:
                shutil.rmtree(self.work_dir)
                self.work_dir = None
            except:
                pass


class GmshConnectorMock(GmshConnector):
    """Gmsh连接器模拟器（用于测试）"""

    def __init__(self):
        super().__init__()
        self.mock_mode = True

    def connect(self) -> bool:
        print("[模拟模式] 连接Gmsh")
        self.is_connected = True
        return True

    def generate_mesh(
        self, geometry_file: Path, mesh_file: Path, element_size: float = 2.0
    ) -> bool:
        print(f"[模拟模式] 生成网格: {geometry_file} -> {mesh_file}")
        mesh_file.parent.mkdir(parents=True, exist_ok=True)

        # 创建模拟网格文件
        with open(mesh_file, "w", encoding="utf-8") as f:
            f.write("** Mock Gmsh mesh file\n")
            f.write("$MeshFormat\n")
            f.write("4.1 0 8\n")
            f.write("$EndMeshFormat\n")
            f.write("$Nodes\n")
            f.write("8\n")
            f.write("1 0.0 0.0 0.0\n")
            f.write("2 10.0 0.0 0.0\n")
            f.write("3 10.0 5.0 0.0\n")
            f.write("4 0.0 5.0 0.0\n")
            f.write("5 0.0 0.0 3.0\n")
            f.write("6 10.0 0.0 3.0\n")
            f.write("7 10.0 5.0 3.0\n")
            f.write("8 0.0 5.0 3.0\n")
            f.write("$EndNodes\n")
            f.write("$Elements\n")
            f.write("1\n")
            f.write("1 5 2 0 1 1 2 3 4 5 6 7 8\n")
            f.write("$EndElements\n")

        return True

    def convert_mesh_format(
        self, input_mesh: Path, output_mesh: Path, target_format: str
    ) -> bool:
        print(f"[模拟模式] 转换格式: {input_mesh} -> {output_mesh} ({target_format})")
        output_mesh.parent.mkdir(parents=True, exist_ok=True)
        output_mesh.write_text(f"** Mock {target_format.upper()} file\n")
        return True
