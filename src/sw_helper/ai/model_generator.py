"""
AI模型生成器 - 自然语言到3D模型
支持解析文本描述并自动生成FreeCAD模型
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ParsedGeometry:
    """解析后的几何描述"""

    shape_type: str  # box, cylinder, sphere, etc.
    parameters: Dict[str, float]  # 尺寸参数
    features: List[Dict[str, Any]]  # 特征（如圆角、孔等）
    material: Optional[str] = None
    description: str = ""


class NaturalLanguageParser:
    """自然语言解析器"""

    # 形状关键词映射
    SHAPE_KEYWORDS = {
        "立方体": "box",
        "长方体": "box",
        "方块": "box",
        "box": "box",
        "圆柱": "cylinder",
        "圆柱体": "cylinder",
        "cylinder": "cylinder",
        "球": "sphere",
        "球体": "sphere",
        "sphere": "sphere",
        "圆锥": "cone",
        "圆锥体": "cone",
        "cone": "cone",
        "圆环": "torus",
        "torus": "torus",
        "支架": "bracket",
        "bracket": "bracket",
        "板": "plate",
        "plate": "plate",
    }

    # 参数关键词映射
    PARAM_PATTERNS = {
        "length": [
            r"长[度]?[\s为是:]+(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*mm?[\s]*长",
            r"length[\s:]+(\d+\.?\d*)",
        ],
        "width": [
            r"宽[度]?[\s为是:]+(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*mm?[\s]*宽",
            r"width[\s:]+(\d+\.?\d*)",
        ],
        "height": [
            r"高[度]?[\s为是:]+(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*mm?[\s]*高",
            r"height[\s:]+(\d+\.?\d*)",
        ],
        "radius": [
            r"半径[\s为是:]+(\d+\.?\d*)",
            r"R[\s为是:]+(\d+\.?\d*)",
            r"radius[\s:]+(\d+\.?\d*)",
        ],
        "diameter": [
            r"直径[\s为是:]+(\d+\.?\d*)",
            r"D[\s为是:]+(\d+\.?\d*)",
            r"diameter[\s:]+(\d+\.?\d*)",
        ],
        "fillet_radius": [
            r"圆角[半径]?[\s为是:]+(\d+\.?\d*)",
            r"倒角[\s为是:]+(\d+\.?\d*)",
            r"fillet[\s:]+(\d+\.?\d*)",
        ],
        "thickness": [
            r"厚度[\s为是:]+(\d+\.?\d*)",
            r"厚[\s为是:]+(\d+\.?\d*)",
            r"thickness[\s:]+(\d+\.?\d*)",
        ],
    }

    def parse(self, description: str) -> ParsedGeometry:
        """
        解析自然语言描述

        Args:
            description: 如"带圆角的立方体，长100宽50高30圆角10"

        Returns:
            ParsedGeometry对象
        """
        description = description.lower().strip()

        # 1. 识别形状类型
        shape_type = self._detect_shape(description)

        # 2. 提取参数
        parameters = self._extract_parameters(description)

        # 3. 识别特征
        features = self._detect_features(description)

        # 4. 识别材料
        material = self._detect_material(description)

        # 5. 设置默认值
        parameters = self._set_defaults(shape_type, parameters)

        return ParsedGeometry(
            shape_type=shape_type,
            parameters=parameters,
            features=features,
            material=material,
            description=description,
        )

    def _detect_shape(self, desc: str) -> str:
        """检测形状类型"""
        for keyword, shape in self.SHAPE_KEYWORDS.items():
            if keyword in desc:
                return shape
        return "box"  # 默认为立方体

    def _extract_parameters(self, desc: str) -> Dict[str, float]:
        """提取尺寸参数"""
        params = {}

        for param_name, patterns in self.PARAM_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, desc, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        params[param_name] = value
                        break
                    except (ValueError, IndexError):
                        continue

        return params

    def _detect_features(self, desc: str) -> List[Dict[str, Any]]:
        """检测特征（圆角、孔等）"""
        features = []

        # 检测圆角
        fillet_match = re.search(
            r"圆角[半径]?[\s为是:]+(\d+\.?\d*)", desc, re.IGNORECASE
        )
        if fillet_match:
            features.append(
                {
                    "type": "fillet",
                    "radius": float(fillet_match.group(1)),
                    "edges": "all",
                }
            )

        # 检测孔
        hole_match = re.search(r"(\d+\.?\d*)\s*mm?[\s]*孔", desc, re.IGNORECASE)
        if hole_match:
            features.append({"type": "hole", "diameter": float(hole_match.group(1))})

        return features

    def _detect_material(self, desc: str) -> Optional[str]:
        """检测材料"""
        materials = {
            "钢": "steel",
            "steel": "steel",
            "铝": "aluminum",
            "铝合金": "aluminum",
            "aluminum": "aluminum",
            "铜": "copper",
            "copper": "copper",
            "塑料": "plastic",
            "plastic": "plastic",
        }

        for keyword, material in materials.items():
            if keyword in desc:
                return material
        return None

    def _set_defaults(self, shape: str, params: Dict[str, float]) -> Dict[str, float]:
        """设置默认值"""
        defaults = {
            "box": {"length": 100, "width": 50, "height": 30},
            "cylinder": {"radius": 25, "height": 50},
            "sphere": {"radius": 30},
            "cone": {"radius": 25, "height": 50},
        }

        shape_defaults = defaults.get(shape, {})

        # 合并默认值和用户参数
        for key, value in shape_defaults.items():
            if key not in params:
                params[key] = value

        return params


class FreeCADModelGenerator:
    """FreeCAD模型生成器"""

    def __init__(self, use_mock: bool = False):
        self.doc = None
        self.fc_app = None
        self.use_mock = use_mock

    def connect(self) -> bool:
        """连接到FreeCAD"""
        if self.use_mock:
            print("[模拟模式] 连接FreeCAD")
            return True

        try:
            import FreeCAD as App
            import Part

            self.fc_app = App
            return True
        except ImportError:
            print("FreeCAD未安装，切换到模拟模式")
            self.use_mock = True
            return True

    def create_document(self, name: str = "GeneratedModel") -> bool:
        """创建新文档"""
        if self.use_mock:
            print(f"[模拟模式] 创建文档: {name}")
            return True

        try:
            self.doc = self.fc_app.newDocument(name)
            return True
        except Exception as e:
            print(f"创建文档失败: {e}")
            return False

    def generate_geometry(self, geometry: ParsedGeometry) -> bool:
        """
        根据解析结果生成几何体

        Args:
            geometry: 解析后的几何描述

        Returns:
            是否成功
        """
        if self.use_mock:
            print(f"[模拟模式] 生成{geometry.shape_type}")
            print(f"  参数: {geometry.parameters}")
            return True

        try:
            import Part

            shape_type = geometry.shape_type
            params = geometry.parameters

            if shape_type == "box":
                # 创建立方体
                length = params.get("length", 100)
                width = params.get("width", 50)
                height = params.get("height", 30)

                # 创建草图
                body = self.doc.addObject("PartDesign::Body", "Body")
                sketch = body.newObject("Sketcher::SketchObject", "Sketch")

                # 创建矩形
                sketch.addGeometry(
                    Part.LineSegment(
                        self.fc_app.Vector(0, 0, 0), self.fc_app.Vector(length, 0, 0)
                    ),
                    False,
                )
                sketch.addGeometry(
                    Part.LineSegment(
                        self.fc_app.Vector(length, 0, 0),
                        self.fc_app.Vector(length, width, 0),
                    ),
                    False,
                )
                sketch.addGeometry(
                    Part.LineSegment(
                        self.fc_app.Vector(length, width, 0),
                        self.fc_app.Vector(0, width, 0),
                    ),
                    False,
                )
                sketch.addGeometry(
                    Part.LineSegment(
                        self.fc_app.Vector(0, width, 0), self.fc_app.Vector(0, 0, 0)
                    ),
                    False,
                )

                # 拉伸
                pad = body.newObject("PartDesign::Pad", "Pad")
                pad.Profile = sketch
                pad.Length = height

            elif shape_type == "cylinder":
                radius = params.get("radius", 25)
                height = params.get("height", 50)

                # 直接创建圆柱
                cylinder = Part.makeCylinder(radius, height)
                obj = self.doc.addObject("Part::Feature", "Cylinder")
                obj.Shape = cylinder

            elif shape_type == "sphere":
                radius = params.get("radius", 30)

                sphere = Part.makeSphere(radius)
                obj = self.doc.addObject("Part::Feature", "Sphere")
                obj.Shape = sphere

            # 添加圆角特征
            for feature in geometry.features:
                if feature["type"] == "fillet":
                    self._apply_fillet(feature["radius"])

            # 重建文档
            self.doc.recompute()
            return True

        except Exception as e:
            print(f"生成几何体失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _apply_fillet(self, radius: float):
        """应用圆角"""
        if self.use_mock or not self.doc:
            return

        try:
            # 找到Body并添加圆角
            for obj in self.doc.Objects:
                if obj.isDerivedFrom("PartDesign::Body"):
                    fillet = obj.newObject("PartDesign::Fillet", "Fillet")
                    fillet.Radius = radius
                    # 这里简化处理，实际应该遍历所有边
                    break
        except Exception as e:
            print(f"应用圆角失败: {e}")

    def save(self, filepath: str) -> bool:
        """保存为.FCStd文件"""
        if self.use_mock:
            print(f"[模拟模式] 保存: {filepath}")
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            Path(filepath).touch()
            return True

        try:
            self.doc.saveAs(filepath)
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False

    def export_step(self, filepath: str) -> bool:
        """导出为STEP格式"""
        if self.use_mock:
            print(f"[模拟模式] 导出STEP: {filepath}")
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            Path(filepath).touch()
            return True

        try:
            import Import

            objects = [
                obj for obj in self.doc.Objects if obj.isDerivedFrom("Part::Feature")
            ]
            if objects:
                Import.export(objects, filepath)
                return True
            return False
        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def close(self):
        """关闭文档"""
        if self.doc and not self.use_mock:
            try:
                self.fc_app.closeDocument(self.doc.Name)
            except:
                pass


class AIModelGenerator:
    """AI模型生成器 - 主控制器"""

    def __init__(self, use_mock: bool = False):
        self.parser = NaturalLanguageParser()
        self.generator = FreeCADModelGenerator(use_mock=use_mock)
        self.use_mock = use_mock

    def generate(
        self,
        description: str,
        output_dir: str = "./generated_models",
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        完整的生成流程

        Args:
            description: 自然语言描述
            output_dir: 输出目录
            name: 模型名称（可选）

        Returns:
            结果字典
        """
        print(f"输入描述: {description}")
        print("-" * 60)

        # 1. 解析描述
        print("解析描述...")
        geometry = self.parser.parse(description)
        print(f" 识别形状: {geometry.shape_type}")
        print(f" 参数: {geometry.parameters}")
        if geometry.features:
            print(f" 特征: {[f['type'] for f in geometry.features]}")

        # 2. 连接FreeCAD
        print("\n 连接FreeCAD...")
        if not self.generator.connect():
            return {"success": False, "error": "无法连接FreeCAD"}

        # 3. 生成模型
        print("\n  生成模型...")
        if not self.generator.create_document():
            return {"success": False, "error": "无法创建文档"}

        if not self.generator.generate_geometry(geometry):
            return {"success": False, "error": "无法生成几何体"}

        # 4. 准备输出路径
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if name is None:
            # 根据描述自动生成名称
            name = f"{geometry.shape_type}_{int(geometry.parameters.get('length', 0))}"

        fcstd_path = output_path / f"{name}.FCStd"
        step_path = output_path / f"{name}.step"

        # 5. 保存和导出
        print("\n保存 保存模型...")
        if not self.generator.save(str(fcstd_path)):
            return {"success": False, "error": "保存失败"}
        print(f" FCStd: {fcstd_path}")

        print("\n 导出STEP...")
        if not self.generator.export_step(str(step_path)):
            return {"success": False, "error": "导出失败"}
        print(f" STEP: {step_path}")

        # 6. 分析（可选）
        analysis_result = None
        if step_path.exists() and not self.use_mock:
            print("\n 分析模型...")
            try:
                from sw_helper.geometry.parser import GeometryParser

                parser = GeometryParser()
                analysis_result = parser.parse(str(step_path))
                print(f" 体积: {analysis_result.get('volume', 0):.2e} m³")
            except Exception as e:
                print(f"  分析失败: {e}")

        # 7. 关闭
        self.generator.close()

        # 8. 返回结果
        result = {
            "success": True,
            "description": description,
            "parsed_geometry": {
                "shape_type": geometry.shape_type,
                "parameters": geometry.parameters,
                "features": geometry.features,
            },
            "output_files": {
                "fcstd": str(fcstd_path),
                "step": str(step_path),
            },
            "analysis": analysis_result,
        }

        print("\n" + "=" * 60)
        print("成功 生成完成!")
        print("=" * 60)

        return result

    def generate_with_analysis(
        self,
        description: str,
        output_dir: str = "./generated_models",
        name: Optional[str] = None,
        generate_report: bool = True,
    ) -> Dict[str, Any]:
        """
        生成模型并运行完整分析流程

        这是 cae-cli ai generate 命令的核心实现
        """
        # 1. 生成模型
        result = self.generate(description, output_dir, name)

        if not result["success"]:
            return result

        step_path = result["output_files"]["step"]

        # 2. 运行分析（如果文件存在）
        if Path(step_path).exists() and generate_report:
            print("\n图表 运行质量分析...")

            try:
                # 几何分析
                from sw_helper.geometry.parser import GeometryParser

                geo_parser = GeometryParser()
                geo_data = geo_parser.parse(step_path)

                result["detailed_analysis"] = {
                    "geometry": geo_data,
                    "quality_score": self._calculate_quality(geo_data),
                }

                print(
                    f" 质量评分: {result['detailed_analysis']['quality_score']:.1f}/100"
                )

                # 生成报告
                report_path = Path(output_dir) / "generation_report.md"
                self._generate_markdown_report(result, str(report_path))
                result["report_path"] = str(report_path)
                print(f" 报告: {report_path}")

            except Exception as e:
                print(f"  详细分析失败: {e}")

        return result

    def _calculate_quality(self, geo_data: Dict) -> float:
        """计算质量分数"""
        score = 70.0

        volume = geo_data.get("volume", 0)
        if 0.0001 < volume < 0.01:
            score += 15

        vertices = geo_data.get("vertices", 0)
        if 100 < vertices < 50000:
            score += 10

        return min(100, score)

    def _generate_markdown_report(self, result: Dict, output_path: str):
        """生成Markdown报告"""
        geo = result["parsed_geometry"]

        report = f"""# AI模型生成报告

## 输入描述

{result["description"]}

## 解析结果

### 形状类型
{geo["shape_type"]}

### 参数
"""

        for param, value in geo["parameters"].items():
            report += f"- **{param}**: {value} mm\n"

        if geo["features"]:
            report += "\n### 特征\n"
            for feature in geo["features"]:
                report += f"- {feature['type']}: {feature}\n"

        report += f"""
## 输出文件

- **FreeCAD模型**: `{result["output_files"]["fcstd"]}`
- **STEP文件**: `{result["output_files"]["step"]}`

## 分析结果

"""

        if "detailed_analysis" in result:
            analysis = result["detailed_analysis"]
            report += f"**质量评分**: {analysis['quality_score']:.1f}/100\n\n"

            if "geometry" in analysis:
                geo_data = analysis["geometry"]
                report += f"""### 几何信息

- 体积: {geo_data.get("volume", 0):.2e} m³
- 表面积: {geo_data.get("surface_area", 0):.2e} m²
- 顶点数: {geo_data.get("vertices", 0)}
- 面数: {geo_data.get("faces", 0)}
"""

        report += """
---
*Generated by CAE-CLI AI Generator*
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
