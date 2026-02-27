"""
参数优化引擎 - 使用FreeCAD实现参数优化闭环
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class OptimizationResult:
    """优化结果数据类 - 包含更详细的信息"""

    iteration: int
    parameter_name: str
    parameter_value: float
    quality_score: float
    analysis_time: float
    timestamp: str
    allowable_stress: float = 0.0
    safety_factor: float = 0.0
    notes: str = ""
    export_path: str = ""


class FreeCADOptimizer:
    """FreeCAD参数优化器"""

    def __init__(self, use_mock: bool = False):
        self.connector = None
        self.use_mock = use_mock
        self.results: List[OptimizationResult] = []
        self.progress_callback: Optional[Callable[[str], None]] = None

    def set_progress_callback(self, callback: Callable[[str], None]):
        """设置进度回调函数"""
        self.progress_callback = callback

    def log(self, message: str):
        """输出日志"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)

    def connect(self) -> bool:
        """连接到FreeCAD"""
        if self.use_mock:
            from sw_helper.integrations.freecad_connector import FreeCADConnectorMock

            self.connector = FreeCADConnectorMock()
            return self.connector.connect()

        try:
            from sw_helper.integrations.freecad_connector import FreeCADConnector

            self.connector = FreeCADConnector()
            return self.connector.connect()
        except Exception as e:
            self.log(f"Failed to connect to FreeCAD: {e}")
            self.log("Switching to mock mode...")
            self.use_mock = True
            return self.connect()

    def optimize_parameter(
        self,
        file_path: str,
        param_name: str,
        param_range: tuple,
        steps: int = 5,
        step_mode: str = "linear",
        output_dir: str = "./optimization_output",
        analyze_geometry: bool = True,
    ) -> List[OptimizationResult]:
        """
        优化指定参数

        Args:
            file_path: CAD文件路径(.FCStd)
            param_name: 参数名(如"Fillet_Radius")
            param_range: (最小值, 最大值)
            steps: 迭代步数
            step_mode: 步进模式 (linear/geometric)
            output_dir: 输出目录
            analyze_geometry: 是否分析几何质量

        Returns:
            优化结果列表
        """
        self.results = []

        # 连接FreeCAD
        self.log("Connecting to FreeCAD...")
        if not self.connect():
            raise RuntimeError("Failed to connect to FreeCAD")

        # 打开文件
        self.log(f"Opening file: {file_path}")
        if not self.connector.open_document(file_path):
            raise RuntimeError(f"Failed to open file: {file_path}")

        # 显示可用参数
        self.log("\nAvailable parameters:")
        params = self.connector.get_parameters()
        for p in params[:5]:  # 显示前5个
            self.log(f"  - {p.name} = {p.value} {p.unit}")

        # 检查目标参数是否存在
        target_param = self.connector.find_parameter(param_name)
        if not target_param:
            if params:
                self.log(f"[Warning] Parameter '{param_name}' not found, available parameters:")
                for p in params[:10]:  # 显示前10个参数
                    self.log(f"  - {p.name} = {p.value} {p.unit}")
                raise ValueError(
                    f"Parameter '{param_name}' not found. Please select from the available parameters above."
                )
            else:
                raise ValueError(f"Parameter '{param_name}' not found, and no parameters were found in the model.")

        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成参数序列
        min_val, max_val = param_range
        if steps == 1:
            values = [min_val]
        elif step_mode == "linear":
            # 线性步进
            step_size = (max_val - min_val) / (steps - 1)
            values = [min_val + i * step_size for i in range(steps)]
        else:  # geometric
            # 等比步进
            import math

            ratio = math.exp(math.log(max_val / min_val) / (steps - 1))
            values = [min_val * (ratio**i) for i in range(steps)]

        self.log(f"\nStarting optimization for parameter: {param_name}")
        self.log(f"   Range: {min_val} ~ {max_val} mm")
        self.log(f"   Steps: {steps}")
        self.log(f"   Step mode: {step_mode}")
        self.log(f"   Value sequence: {[round(v, 2) for v in values]}")
        self.log("-" * 60)

        # 优化循环
        for i, value in enumerate(values, 1):
            iteration_start = time.time()

            self.log(f"\n[Iteration {i}/{steps}] {param_name} = {value:.2f} mm")

            try:
                # 1. 设置参数
                self.log("   Modifying parameter...")
                if not self.connector.set_parameter(param_name, value):
                    self.log("   Parameter setting failed, skipping")
                    continue

                # 2. 重建模型
                self.log("   Rebuilding model...")
                if not self.connector.rebuild():
                    self.log("   Warning: Rebuild may have issues")

                # 3. 导出文件
                export_file = output_path / f"iter_{i:02d}_{param_name}_{value:.1f}.step"
                self.log(f"   Exporting: {export_file.name}")

                if not self.connector.export_file(str(export_file), "STEP"):
                    self.log("   Export failed")
                    continue

                # 4. 分析质量（如果启用）
                quality_score = 50.0  # 基础分
                allowable_stress = 0.0
                safety_factor = 0.0
                notes = "Not analyzed"

                if analyze_geometry and export_file.exists():
                    self.log("   Analyzing geometry quality...")
                    try:
                        from sw_helper.geometry.parser import GeometryParser

                        parser = GeometryParser()
                        geo_data = parser.parse(str(export_file))

                        # 计算质量分数
                        quality_score = self._calculate_quality_score(geo_data, value)

                        # 计算力学性能
                        allowable_stress, safety_factor = self._calculate_mechanical_properties(geo_data, value)

                        notes = f"Volume: {geo_data.get('volume', 0):.2e} m³"
                    except Exception as e:
                        self.log(f"   Analysis failed: {e}")
                        notes = f"Analysis failed: {e}"
                else:
                    notes = "Not analyzed"
                    # 模拟质量分数和力学性能（用于测试）
                    quality_score = 50 + (value - min_val) / (max_val - min_val) * 40
                    if param_name.lower() in ["fillet", "radius", "r"]:
                        # 圆角半径在适中范围得分高
                        optimal = (min_val + max_val) / 2
                        quality_score = 100 - abs(value - optimal) / (max_val - min_val) * 50

                    # 模拟力学性能
                    allowable_stress, safety_factor = self._calculate_mechanical_properties({}, value)

                analysis_time = time.time() - iteration_start

                # 记录结果
                result = OptimizationResult(
                    iteration=i,
                    parameter_name=param_name,
                    parameter_value=value,
                    quality_score=quality_score,
                    allowable_stress=allowable_stress,
                    safety_factor=safety_factor,
                    analysis_time=analysis_time,
                    timestamp=datetime.now().isoformat(),
                    notes=notes,
                    export_path=str(export_file),
                )

                self.results.append(result)

                self.log(f"   Quality score: {quality_score:.1f}/100")
                self.log(f"   Time elapsed: {analysis_time:.2f}s")

            except Exception as e:
                self.log(f"   ✗ 错误: {e}")
                import traceback

                traceback.print_exc()
                continue

        # 关闭文档
        self.log("\nClosing document...")
        self.connector.close_document(save=False)
        self.connector.disconnect()

        # 生成最终报告
        if self.results:
            self._generate_summary()

        return self.results

    def _calculate_quality_score(self, geo_data: Dict, param_value: float) -> float:
        """计算质量分数 - 包含许用应力和安全系数分析（改进版）"""
        score = 50.0  # 基础分

        # 体积合理性
        volume = geo_data.get("volume", 0)
        if 0.0001 < volume < 0.01:  # 合理的体积范围
            score += 15
        elif volume < 0.0001:
            score += 5  # 过小体积
        elif volume < 0.1:
            score += 10  # 稍大体积
        else:
            score += 5  # 过大体积

        # 几何复杂度
        vertices = geo_data.get("vertices", 0)
        if 100 < vertices < 50000:
            score += 10
        elif vertices < 100:
            score += 5  # 过于简单
        else:
            score += 7  # 过于复杂

        # 面数合理性
        faces = geo_data.get("faces", 0)
        if 100 < faces < 10000:
            score += 10
        elif faces < 100:
            score += 5  # 过于简单
        else:
            score += 7  # 过于复杂

        # 参数优化加分（假设适中的参数值更好）
        min_param = 5
        max_param = 15
        if min_param < param_value < max_param:
            score += 20
        elif param_value <= min_param:
            score += 10
        else:
            score += 15

        # 力学性能加分
        allowable_stress, safety_factor = self._calculate_mechanical_properties(geo_data, param_value)
        if allowable_stress > 140:
            score += 10
        elif allowable_stress > 120:
            score += 5
        else:
            score += 2

        if safety_factor > 2.0:
            score += 10
        elif safety_factor > 1.5:
            score += 5
        else:
            score += 2

        return min(100, max(0, score))

    def _calculate_mechanical_properties(self, geo_data: Dict, param_value: float) -> tuple:
        """计算力学性能 - 许用应力和安全系数（改进版）"""
        # 假设材料为Q235钢
        yield_strength = 235  # MPa

        # 根据几何信息调整计算
        volume = geo_data.get("volume", 0)
        vertices = geo_data.get("vertices", 0)
        faces = geo_data.get("faces", 0)

        # 基础安全系数
        base_safety_factor = 1.5

        # 根据参数值调整
        if param_value < 5:
            param_factor = 0.8  # 较小参数值，降低许用应力
            safety_factor = base_safety_factor * 1.2  # 增加安全系数
        elif param_value < 15:
            param_factor = 1.0  # 适中参数值，正常许用应力
            safety_factor = base_safety_factor
        else:
            param_factor = 0.9  # 较大参数值，略低许用应力
            safety_factor = base_safety_factor * 1.1

        # 根据体积调整
        if volume < 0.0001:
            volume_factor = 0.7  # 小体积，降低许用应力
        elif volume < 0.01:
            volume_factor = 1.0  # 合理体积范围
        else:
            volume_factor = 0.8  # 大体积，降低许用应力

        # 根据复杂度调整
        complexity = vertices + faces
        if complexity < 1000:
            complexity_factor = 1.1  # 简单几何，提高许用应力
        elif complexity < 10000:
            complexity_factor = 1.0  # 适中复杂度
        else:
            complexity_factor = 0.9  # 复杂几何，降低许用应力

        # 综合计算许用应力
        allowable_stress = yield_strength * param_factor * volume_factor * complexity_factor

        # 确保许用应力在合理范围内
        allowable_stress = max(50, min(allowable_stress, yield_strength * 0.7))

        # 确保安全系数在合理范围内
        safety_factor = max(1.2, min(safety_factor, 3.0))

        return allowable_stress, safety_factor

    def _generate_summary(self):
        """生成优化总结"""
        if not self.results:
            return

        best = max(self.results, key=lambda x: x.quality_score)

        self.log("\n" + "=" * 60)
        self.log("Optimization complete!")
        self.log("=" * 60)
        self.log(f"Total iterations: {len(self.results)}")
        self.log(f"Best iteration: #{best.iteration}")
        self.log(f"Best parameter: {best.parameter_name} = {best.parameter_value:.2f} mm")
        self.log(f"Top quality score: {best.quality_score:.1f}/100")
        self.log(f"Total time: {sum(r.analysis_time for r in self.results):.2f}s")
        self.log("=" * 60)

    def export_results(self, output_file: str):
        """导出结果为JSON"""
        if not self.results:
            return

        data = {
            "optimization_type": "parametric",
            "timestamp": datetime.now().isoformat(),
            "total_iterations": len(self.results),
            "results": [asdict(r) for r in self.results],
        }

        # 添加最佳结果
        best = max(self.results, key=lambda x: x.quality_score)
        data["best_result"] = asdict(best)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.log(f"\nResults saved: {output_file}")

    def plot_results(self, output_file: str = "optimization_plot.png"):
        """绘制优化结果图表"""
        try:
            import matplotlib
            import matplotlib.pyplot as plt

            matplotlib.use("Agg")  # 非交互式后端

            values = [r.parameter_value for r in self.results]
            scores = [r.quality_score for r in self.results]
            allowable_stresses = [r.allowable_stress for r in self.results]
            safety_factors = [r.safety_factor for r in self.results]

            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

            # 图1: 质量分数 vs 参数值
            ax1.plot(values, scores, "b-o", linewidth=2, markersize=8)
            ax1.set_xlabel("Parameter Value (mm)", fontsize=12)
            ax1.set_ylabel("Quality Score", fontsize=12)
            ax1.set_title("Quality Score vs Parameter Value", fontsize=14, pad=10)
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 100)

            # 标记最佳点
            best_idx = scores.index(max(scores))
            ax1.plot(
                values[best_idx],
                scores[best_idx],
                "r*",
                markersize=20,
                label="Best",
            )
            ax1.legend()

            # 图2: 许用应力 vs 参数值
            ax2.plot(values, allowable_stresses, "g-s", linewidth=2, markersize=8)
            ax2.set_xlabel("Parameter Value (mm)", fontsize=12)
            ax2.set_ylabel("Allowable Stress (MPa)", fontsize=12)
            ax2.set_title("Allowable Stress vs Parameter Value", fontsize=14, pad=10)
            ax2.grid(True, alpha=0.3)

            # 标记最佳点
            ax2.plot(
                values[best_idx],
                allowable_stresses[best_idx],
                "r*",
                markersize=20,
                label="Best",
            )
            ax2.legend()

            # 图3: 安全系数 vs 参数值
            ax3.plot(values, safety_factors, "m-^", linewidth=2, markersize=8)
            ax3.set_xlabel("Parameter Value (mm)", fontsize=12)
            ax3.set_ylabel("Safety Factor", fontsize=12)
            ax3.set_title("Safety Factor vs Parameter Value", fontsize=14, pad=10)
            ax3.grid(True, alpha=0.3)

            # 标记最佳点
            ax3.plot(
                values[best_idx],
                safety_factors[best_idx],
                "r*",
                markersize=20,
                label="Best",
            )
            ax3.legend()

            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            plt.close()

            self.log(f"Plot saved: {output_file}")

        except ImportError:
            self.log("matplotlib not installed, skipping plot")
        except Exception as e:
            self.log(f"Plot failed: {e}")

    def generate_report(self, output_file: str = "optimization_report.md"):
        """生成Markdown报告"""
        if not self.results:
            return

        best = max(self.results, key=lambda x: x.quality_score)

        report = f"""# 参数优化报告

## 优化概览

- **优化参数**: {best.parameter_name}
- **总迭代次数**: {len(self.results)}
- **优化时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 最佳结果

- **迭代编号**: {best.iteration}
- **最佳参数值**: {best.parameter_value:.2f} mm
- **最高质量分**: {best.quality_score:.1f}/100
- **许用应力**: {best.allowable_stress:.1f} MPa
- **安全系数**: {best.safety_factor:.2f}
- **分析耗时**: {best.analysis_time:.2f}s
- **输出文件**: `{best.export_path}`

## 详细结果

| 迭代 | 参数值 (mm) | 质量分数 | 许用应力 (MPa) | 安全系数 | 耗时 (s) | 备注 |
|------|-------------|----------|----------------|----------|----------|------|
"""

        for r in self.results:
            marker = "⭐" if r == best else ""
            report += f"| {r.iteration} | {r.parameter_value:.2f} | {r.quality_score:.1f} {marker} | {r.allowable_stress:.1f} | {r.safety_factor:.2f} | {r.analysis_time:.2f} | {r.notes} |\n"

        report += f"""

## 统计信息

- **平均质量分数**: {sum(r.quality_score for r in self.results) / len(self.results):.1f}
- **质量分数范围**: {min(r.quality_score for r in self.results):.1f} ~ {max(r.quality_score for r in self.results):.1f}
- **平均许用应力**: {sum(r.allowable_stress for r in self.results) / len(self.results):.1f} MPa
- **许用应力范围**: {min(r.allowable_stress for r in self.results):.1f} ~ {max(r.allowable_stress for r in self.results):.1f} MPa
- **平均安全系数**: {sum(r.safety_factor for r in self.results) / len(self.results):.2f}
- **安全系数范围**: {min(r.safety_factor for r in self.results):.2f} ~ {max(r.safety_factor for r in self.results):.2f}
- **总耗时**: {sum(r.analysis_time for r in self.results):.2f}s
- **平均迭代耗时**: {sum(r.analysis_time for r in self.results) / len(self.results):.2f}s

## 建议

基于优化结果，建议采用以下参数：

- **{best.parameter_name}**: {best.parameter_value:.2f} mm
- **预期质量分数**: {best.quality_score:.1f}/100
- **预期许用应力**: {best.allowable_stress:.1f} MPa
- **预期安全系数**: {best.safety_factor:.2f}

---
*Generated by CAE-CLI Optimize*
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

        self.log(f"Report generated: {output_file}")
