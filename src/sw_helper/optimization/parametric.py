"""
参数化优化模块 - 实现设计参数优化循环
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class OptimizationResult:
    """优化结果数据类"""

    iteration: int
    parameters: Dict[str, float]
    quality_score: float
    analysis_time: float
    timestamp: str
    notes: str = ""


@dataclass
class OptimizationConfig:
    """优化配置"""

    target_parameter: str
    parameter_range: tuple  # (min, max)
    step_size: float
    iterations: int
    target_metric: str  # 如 'max_stress', 'safety_factor'
    target_value: Optional[float] = None
    minimize: bool = True


class ParametricOptimizer:
    """参数优化器"""

    def __init__(self, cad_connector=None):
        self.cad = cad_connector
        self.results: List[OptimizationResult] = []
        self.callback: Optional[Callable] = None

    def set_callback(self, callback: Callable):
        """设置进度回调函数"""
        self.callback = callback

    def optimize_fillet_radius(
        self,
        file_path: str,
        radius_range: tuple = (2, 15),
        steps: int = 5,
        cad_type: str = "solidworks",
    ) -> List[OptimizationResult]:
        """
        优化圆角半径

        工作流程:
        1. 修改圆角半径参数
        2. 重建模型
        3. 导出STEP文件
        4. 分析质量
        5. 记录结果

        Args:
            file_path: CAD文件路径
            radius_range: 圆角半径范围 (min, max) mm
            steps: 迭代次数
            cad_type: CAD软件类型

        Returns:
            优化结果列表
        """
        from sw_helper.geometry.parser import GeometryParser
        from sw_helper.integrations.cad_connector import CADManager

        self.results = []

        # 连接CAD
        if not self.cad:
            manager = CADManager()
            cad_name = manager.auto_connect()
            if not cad_name:
                raise RuntimeError("无法连接到CAD软件")
            self.cad = manager.get_connector()

        # 打开文件
        if not self.cad.open_document(file_path):
            raise RuntimeError(f"无法打开文件: {file_path}")

        # 生成半径序列
        min_r, max_r = radius_range
        radii = [min_r + (max_r - min_r) * i / (steps - 1) for i in range(steps)]

        def console_print(msg):
            if not self.callback:
                print(msg)
            else:
                self.callback(msg)

        console_print(f"开始优化圆角半径: {radius_range[0]} ~ {radius_range[1]} mm")
        console_print(f"迭代次数: {steps}")
        console_print("-" * 60)

        for i, radius in enumerate(radii):
            iteration_start = time.time()

            console_print(f"\n[迭代 {i + 1}/{steps}] 圆角 R = {radius:.2f} mm")

            try:
                # 1. 修改参数
                if cad_type.lower() == "solidworks":
                    # SolidWorks参数名可能是 "Fillet_R" 或类似的
                    param_names = ["Fillet_R", "Fillet_Radius", "R", "圆角半径"]
                    param_set = False

                    for param_name in param_names:
                        if self.cad.set_parameter(param_name, radius):
                            console_print(f"  ✓ 设置参数: {param_name} = {radius} mm")
                            param_set = True
                            break

                    if not param_set:
                        console_print("  ⚠ 警告: 未能找到圆角参数，尝试使用特征名称")
                        # 可以尝试通过特征名称修改
                else:
                    # FreeCAD
                    self.cad.set_parameter("Fillet_Radius", radius)

                # 2. 重建模型
                console_print("  ⏳ 重建模型...")
                if self.cad.rebuild():
                    console_print("  ✓ 重建完成")
                else:
                    console_print("  ⚠ 重建可能有问题")

                # 3. 导出文件
                export_path = Path("temp") / f"opt_iter_{i + 1}_r{radius:.1f}.step"
                export_path.parent.mkdir(exist_ok=True)

                console_print(f"  ⏳ 导出到: {export_path}")
                if self.cad.export_file(str(export_path), "STEP"):
                    console_print("  ✓ 导出成功")
                else:
                    console_print("  ✗ 导出失败")
                    continue

                # 4. 分析几何质量
                console_print("  ⏳ 分析几何质量...")
                parser = GeometryParser()
                geo_data = parser.parse(str(export_path))

                # 计算质量分数（模拟）
                quality_score = self._calculate_quality_score(geo_data, radius)

                analysis_time = time.time() - iteration_start

                # 5. 记录结果
                result = OptimizationResult(
                    iteration=i + 1,
                    parameters={"fillet_radius": radius},
                    quality_score=quality_score,
                    analysis_time=analysis_time,
                    timestamp=datetime.now().isoformat(),
                    notes=f"体积: {geo_data.get('volume', 0):.2e} m³",
                )

                self.results.append(result)

                console_print(f"  ✓ 质量分数: {quality_score:.2f}")
                console_print(f"  ⏱  耗时: {analysis_time:.2f}s")

            except Exception as e:
                console_print(f"  ✗ 错误: {e}")
                continue

        # 关闭CAD文档
        self.cad.close_document(save=False)

        # 生成优化报告
        self._generate_optimization_report()

        return self.results

    def _calculate_quality_score(self, geo_data: Dict, radius: float) -> float:
        """计算质量分数"""
        # 这是一个简化的质量评分函数
        # 实际应根据应力分析、制造工艺等因素计算

        score = 50.0  # 基础分

        # 圆角半径适中加分（避免应力集中）
        if 3 <= radius <= 10:
            score += 20
        elif radius > 10:
            score += 10
        else:
            score += 5

        # 体积合理加分（不过大）
        volume = geo_data.get("volume", 0)
        if volume < 0.001:  # 小于1升
            score += 15

        # 几何复杂度（顶点数）
        vertices = geo_data.get("vertices", 0)
        if 100 < vertices < 10000:
            score += 15

        return min(100, score)

    def optimize_parameter(
        self, file_path: str, config: OptimizationConfig, cad_type: str = "solidworks"
    ) -> List[OptimizationResult]:
        """
        通用参数优化

        Args:
            file_path: CAD文件路径
            config: 优化配置
            cad_type: CAD软件类型

        Returns:
            优化结果列表
        """
        self.results = []

        # 连接CAD
        from sw_helper.integrations.cad_connector import CADManager

        if not self.cad:
            manager = CADManager()
            cad_name = manager.auto_connect()
            if not cad_name:
                raise RuntimeError("无法连接到CAD软件")
            self.cad = manager.get_connector()

        # 打开文件
        if not self.cad.open_document(file_path):
            raise RuntimeError(f"无法打开文件: {file_path}")

        # 生成参数序列
        min_val, max_val = config.parameter_range
        if config.iterations == 1:
            values = [min_val]
        else:
            step = (max_val - min_val) / (config.iterations - 1)
            values = [min_val + i * step for i in range(config.iterations)]

        print(f"开始优化参数 '{config.target_parameter}'")
        print(f"范围: {min_val} ~ {max_val}, 步长: {config.step_size}")
        print("-" * 60)

        for i, value in enumerate(values):
            iteration_start = time.time()

            print(f"\n[迭代 {i + 1}/{config.iterations}] {config.target_parameter} = {value:.4f}")

            try:
                # 修改参数
                if self.cad.set_parameter(config.target_parameter, value):
                    print("  ✓ 参数设置成功")
                else:
                    print("  ✗ 参数设置失败")
                    continue

                # 重建
                print("  ⏳ 重建模型...")
                self.cad.rebuild()

                # 导出
                export_path = Path("temp") / f"opt_{i + 1}.step"
                self.cad.export_file(str(export_path), "STEP")

                # 分析（这里简化处理）
                quality_score = 50 + (value - min_val) / (max_val - min_val) * 50

                analysis_time = time.time() - iteration_start

                result = OptimizationResult(
                    iteration=i + 1,
                    parameters={config.target_parameter: value},
                    quality_score=quality_score,
                    analysis_time=analysis_time,
                    timestamp=datetime.now().isoformat(),
                )

                self.results.append(result)
                print(f"  ✓ 质量分数: {quality_score:.2f}")

            except Exception as e:
                print(f"  ✗ 错误: {e}")
                continue

        self.cad.close_document(save=False)
        return self.results

    def _generate_optimization_report(self) -> str:
        """生成优化报告"""
        if not self.results:
            return ""

        report_lines = [
            "=" * 60,
            "参数优化报告",
            "=" * 60,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"总迭代次数: {len(self.results)}",
            "",
            "优化结果:",
            "-" * 60,
        ]

        best_result = max(self.results, key=lambda x: x.quality_score)

        for result in self.results:
            params_str = ", ".join([f"{k}={v:.2f}" for k, v in result.parameters.items()])
            marker = " ★ 最佳" if result == best_result else ""
            report_lines.append(
                f"迭代 {result.iteration}: {params_str} | "
                f"质量分数: {result.quality_score:.2f} | "
                f"耗时: {result.analysis_time:.2f}s{marker}"
            )

        report_lines.extend(
            [
                "",
                "=" * 60,
                "最佳结果:",
                "-" * 60,
                f"迭代: {best_result.iteration}",
            ]
        )

        for param_name, value in best_result.parameters.items():
            report_lines.append(f"{param_name}: {value:.4f}")

        report_lines.extend(
            [
                f"质量分数: {best_result.quality_score:.2f}",
                f"总耗时: {sum(r.analysis_time for r in self.results):.2f}s",
                "=" * 60,
            ]
        )

        report = "\n".join(report_lines)

        # 保存报告
        report_path = Path("temp") / f"optimization_report_{int(time.time())}.txt"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n报告已保存: {report_path}")

        return report

    def export_results_json(self, output_path: str):
        """导出结果为JSON"""
        data = {
            "optimization_type": "parametric",
            "timestamp": datetime.now().isoformat(),
            "results": [asdict(r) for r in self.results],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"结果已导出: {output_path}")

    def plot_results(self):
        """绘制优化结果图表"""
        try:
            import matplotlib.pyplot as plt

            iterations = [r.iteration for r in self.results]
            scores = [r.quality_score for r in self.results]

            plt.figure(figsize=(10, 6))
            plt.plot(iterations, scores, "b-o", linewidth=2, markersize=8)
            plt.xlabel("迭代次数", fontsize=12)
            plt.ylabel("质量分数", fontsize=12)
            plt.title("参数优化迭代过程", fontsize=14)
            plt.grid(True, alpha=0.3)

            # 标记最佳点
            best_idx = scores.index(max(scores))
            plt.plot(
                iterations[best_idx],
                scores[best_idx],
                "r*",
                markersize=15,
                label="最佳",
            )
            plt.legend()

            plt.tight_layout()
            plt.savefig("temp/optimization_plot.png", dpi=150)
            plt.close()

            print("图表已保存: temp/optimization_plot.png")

        except ImportError:
            print("警告: 未安装matplotlib，无法绘制图表")


class AIAssistedOptimizer(ParametricOptimizer):
    """AI辅助优化器"""

    def __init__(self, cad_connector=None):
        super().__init__(cad_connector)
        from sw_helper.ai.generator import AIGenerator

        self.ai = AIGenerator()

    def ai_guided_optimization(
        self, file_path: str, description: str, target: str = "strength"
    ) -> List[OptimizationResult]:
        """
        AI引导的优化

        1. AI分析当前设计
        2. 生成优化建议
        3. 执行参数调整
        4. 验证结果

        Args:
            file_path: CAD文件路径
            description: 设计描述
            target: 优化目标
        """
        print("=" * 60)
        print("AI辅助参数优化")
        print("=" * 60)

        # 1. AI分析设计
        print(f"\n🤖 AI分析设计: {description}")
        design_data = self.ai.parse_geometry_description(description)

        print("\n设计参数:")
        for param_name, param_info in design_data.get("parameters", {}).items():
            print(f"  • {param_name}: {param_info['value']} {param_info['unit']}")

        # 2. 获取AI优化建议
        current_params = {k: v["value"] for k, v in design_data.get("parameters", {}).items()}

        # 模拟质量指标
        mock_metrics = {"max_stress": 180e6, "safety_factor": 1.8, "weight": 2.5}

        suggestions = self.ai.generate_optimization_suggestions(current_params, mock_metrics, target)

        print("\nAI优化建议:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion['reason']}")
            print(f"     建议: {suggestion['type']} = {suggestion.get('suggested', 'N/A')}")
            print(f"     预期改进: {suggestion.get('expected_improvement', 'N/A')}")

        # 3. 执行第一个建议的优化
        if suggestions:
            first_suggestion = suggestions[0]
            param_name = first_suggestion.get("parameter")

            if param_name and param_name in current_params:
                current_val = current_params[param_name]
                suggested_val = first_suggestion.get("suggested", current_val * 1.2)

                print(f"\n🔄 执行优化: 修改 {param_name}")
                print(f"   当前值: {current_val}")
                print(f"   建议值: {suggested_val}")

                # 创建优化配置
                min_val = min(current_val * 0.8, suggested_val * 0.8)
                max_val = max(current_val * 1.2, suggested_val * 1.2)

                config = OptimizationConfig(
                    target_parameter=param_name,
                    parameter_range=(min_val, max_val),
                    step_size=abs(suggested_val - current_val) / 3,
                    iterations=5,
                    target_metric=target,
                    minimize=(target == "weight"),
                )

                # 执行优化
                results = self.optimize_parameter(file_path, config)

                return results

        return []
