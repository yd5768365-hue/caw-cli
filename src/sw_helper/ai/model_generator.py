"""
AI模型生成器 - 自然语言到3D模型
支持解析文本描述并自动生成FreeCAD模型
包含改进的Prompt模板和增强的特征识别
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============ Prompt 模板 ============

PROMPT_TEMPLATES = {
    # 中文提示模板
    "zh": {
        "system": """你是一个专业的CAD建模助手，专门帮助用户使用FreeCAD创建3D模型。
请根据用户的描述，生成精确的建模指令。

支持的几何形状：
- box/立方体/长方体：需要 length, width, height
- cylinder/圆柱：需要 radius, height
- sphere/球：需要 radius
- cone/圆锥：需要 radius (底部), radius2 (顶部，可选), height
- torus/圆环：需要 radius, radius2 (管半径)
- wedge/楔形：需要 length, width, height, x1, x2
- prism/棱柱：需要 polygon (边数), radius, height

支持的特征：
- fillet/圆角：需要 radius
- chamfer/倒角：需要 radius
- hole/孔：需要 diameter, depth (可选), position (可选)
- pocket/凹槽：需要 length, width, depth
- pad/凸台：需要 length, width, height
- shell/抽壳：需要 thickness
- revolve/旋转：需要 angle, axis

材料选项：steel(钢), aluminum(铝), copper(铜), plastic(塑料), titanium(钛)

请按以下JSON格式返回：
```json
{
  "shape_type": "形状类型",
  "parameters": {"参数名": 数值, ...},
  "features": [{"type": "特征类型", ...}, ...],
  "material": "材料或null"
}
```""",
        "user": "请生成一个{shape_description}，参数为{parameters}。",
    },
    # 英文提示模板
    "en": {
        "system": """You are a professional CAD modeling assistant specializing in FreeCAD 3D model creation.
Generate precise modeling instructions based on user descriptions.

Supported shapes:
- box: requires length, width, height
- cylinder: requires radius, height
- sphere: requires radius
- cone: requires radius, radius2 (optional), height
- torus: requires radius, radius2 (tube radius)
- wedge: requires length, width, height, x1, x2
- prism: requires polygon (edges), radius, height

Supported features:
- fillet: requires radius
- chamfer: requires radius
- hole: requires diameter, depth (optional)
- pocket: requires length, width, depth
- pad: requires length, width, height
- shell: requires thickness

Return JSON format:
```json
{
  "shape_type": "shape_type",
  "parameters": {"param": value},
  "features": [{"type": "feature_type", ...}],
  "material": "material or null"
}
```""",
        "user": "Generate a {shape_description} with parameters: {parameters}.",
    },
}


@dataclass
class ParsedGeometry:
    """解析后的几何描述"""

    shape_type: str  # box, cylinder, sphere, etc.
    parameters: Dict[str, float]  # 尺寸参数
    features: List[Dict[str, Any]] = field(default_factory=list)  # 特征
    material: Optional[str] = None
    description: str = ""
    position: Optional[Dict[str, float]] = None  # 位置
    rotation: Optional[Dict[str, float]] = None  # 旋转角度


class NaturalLanguageParser:
    """自然语言解析器"""

    # 预编译正则表达式（性能优化）
    _PARAM_PATTERNS_COMPILED = None  # 延迟初始化
    # 特征检测预编译模式
    _FILET_PATTERN = re.compile(r"圆角[半径]?[\s为是:]+(\d+\.?\d*)", re.IGNORECASE)
    _HOLE_PATTERN = re.compile(r"(\d+\.?\d*)\s*mm?[\s]*孔", re.IGNORECASE)
    _POS_X_PATTERN = re.compile(r"x\s*[:=]\s*(\d+\.?\d*)")
    _POS_Y_PATTERN = re.compile(r"y\s*[:=]\s*(\d+\.?\d*)")
    _POS_Z_PATTERN = re.compile(r"z\s*[:=]\s*(\d+\.?\d*)")
    _ROT_X_PATTERN = re.compile(r"rx\s*[:=]\s*(\d+\.?\d*)")
    _ROT_Y_PATTERN = re.compile(r"ry\s*[:=]\s*(\d+\.?\d*)")
    _ROT_Z_PATTERN = re.compile(r"rz\s*[:=]\s*(\d+\.?\d*)")
    _CHAMFER_PATTERN = re.compile(r"倒角[大小]?[\s为是:]+(\d+\.?\d*)", re.IGNORECASE)

    # 形状关键词映射（扩展版）
    SHAPE_KEYWORDS = {
        # 中文
        "立方体": "box",
        "长方体": "box",
        "方块": "box",
        "矩形": "box",
        "板": "plate",
        "圆柱": "cylinder",
        "圆柱体": "cylinder",
        "圆筒": "cylinder",
        "球": "sphere",
        "球体": "sphere",
        "圆锥": "cone",
        "圆锥体": "cone",
        "圆台": "frustum",
        "圆环": "torus",
        "圆环体": "torus",
        "楔形": "wedge",
        "棱柱": "prism",
        "六棱柱": "hexagon_prism",
        "支架": "bracket",
        "L型": "l_shape",
        "U型": "u_shape",
        "T型": "t_shape",
        # 英文
        "box": "box",
        "rectangle": "box",
        "plate": "plate",
        "cylinder": "cylinder",
        "sphere": "sphere",
        "cone": "cone",
        "frustum": "frustum",
        "torus": "torus",
        "wedge": "wedge",
        "prism": "prism",
        "bracket": "bracket",
        "l-shape": "l_shape",
        "u-shape": "u_shape",
        "t-shape": "t_shape",
        "pipe": "pipe",
        "管": "pipe",
        "管子": "pipe",
    }

    # 布尔运算关键词
    BOOLEAN_KEYWORDS = {
        "union": ["合并", "并集", "相加", "加", "unite", "union", "add", "fuse"],
        "subtract": ["减去", "差集", "切除", "减", "cut", "subtract", "remove"],
        "intersect": ["相交", "交集", "common", "intersect"],
    }

    # 参数关键词映射（扩展版）
    PARAM_PATTERNS = {
        "length": [
            r"长[度]?[\s为是:]+(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*mm?[\s]*长",
            r"length[\s:]+(\d+\.?\d*)",
            r"L[\s:=]+(\d+\.?\d*)",
        ],
        "width": [
            r"宽[度]?[\s为是:]+(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*mm?[\s]*宽",
            r"width[\s:]+(\d+\.?\d*)",
            r"W[\s:=]+(\d+\.?\d*)",
        ],
        "height": [
            r"高[度]?[\s为是:]+(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*mm?[\s]*高",
            r"height[\s:]+(\d+\.?\d*)",
            r"H[\s:=]+(\d+\.?\d*)",
        ],
        "radius": [
            r"半径[\s为是:]+(\d+\.?\d*)",
            r"R[\s为是:]+(\d+\.?\d*)",
            r"radius[\s:]+(\d+\.?\d*)",
            r"r[\s:=]+(\d+\.?\d*)",
        ],
        "radius2": [
            r"顶部半径[\s为是:]+(\d+\.?\d*)",
            r"上半径[\s为是:]+(\d+\.?\d*)",
            r"radius2[\s:]+(\d+\.?\d*)",
        ],
        "tube_radius": [
            r"管半径[\s为是:]+(\d+\.?\d*)",
            r"管径[\s为是:]+(\d+\.?\d*)",
            r"tube[\s:]+(\d+\.?\d*)",
        ],
        "diameter": [
            r"直径[\s为是:]+(\d+\.?\d*)",
            r"D[\s为是:]+(\d+\.?\d*)",
            r"diameter[\s:]+(\d+\.?\d*)",
            r"Φ(\d+\.?\d*)",
        ],
        "fillet_radius": [
            r"圆角[半径]?[\s为是:]+(\d+\.?\d*)",
            r"倒角[\s为是:]+(\d+\.?\d*)",
            r"fillet[\s:]+(\d+\.?\d*)",
        ],
        "chamfer_radius": [
            r"倒角半径[\s为是:]+(\d+\.?\d*)",
            r"chamfer[\s:]+(\d+\.?\d*)",
        ],
        "thickness": [
            r"厚度[\s为是:]+(\d+\.?\d*)",
            r"厚[\s为是:]+(\d+\.?\d*)",
            r"thickness[\s:]+(\d+\.?\d*)",
            r"t[\s:=]+(\d+\.?\d*)",
        ],
        "depth": [
            r"深度[\s为是:]+(\d+\.?\d*)",
            r"深[\s为是:]+(\d+\.?\d*)",
            r"depth[\s:]+(\d+\.?\d*)",
        ],
        "angle": [
            r"角度[\s为是:]+(\d+\.?\d*)",
            r"度[\s:]+(\d+\.?\d*)",
            r"angle[\s:]+(\d+\.?\d*)",
        ],
        "polygon": [
            r"(\d+)\s*边",
            r"(\d+)\s*棱",
            r"(\d+)-边",
            r"polygon[\s:]+(\d+)",
        ],
    }

    # 特征关键词映射
    FEATURE_KEYWORDS = {
        "fillet": [
            r"圆角",
            r"倒圆角",
            r"fillet",
            r"round",
        ],
        "chamfer": [
            r"倒角",
            r"倒斜角",
            r"chamfer",
            r"bevel",
        ],
        "hole": [
            r"孔",
            r"钻孔",
            r"hole",
            r"bore",
        ],
        "pocket": [
            r"凹槽",
            r"腔",
            r"pocket",
            r"cavity",
        ],
        "pad": [
            r"凸台",
            r"突起",
            r"pad",
            r"boss",
        ],
        "shell": [
            r"抽壳",
            r"薄壁",
            r"shell",
            r"hollow",
        ],
        "thread": [
            r"螺纹",
            r"thread",
        ],
        "revolve": [
            r"旋转",
            r"revolve",
        ],
        "sweep": [
            r"扫掠",
            r"sweep",
        ],
    }

    # 材料关键词映射
    MATERIAL_KEYWORDS = {
        "steel": ["钢", "钢材", "steel", "iron", "铁"],
        "aluminum": ["铝", "铝合金", "aluminum", "aluminium"],
        "copper": ["铜", "铜材", "copper"],
        "brass": ["黄铜", "brass"],
        "plastic": ["塑料", "plastic", "abs", "pp", "尼龙"],
        "titanium": ["钛", "钛合金", "titanium", "ti"],
        "stainless": ["不锈钢", "stainless", "304", "316"],
    }

    def parse(self, description: str) -> ParsedGeometry:
        """解析自然语言描述

        Args:
            description: 如"带圆角的立方体，长100宽50高30圆角10"

        Returns:
            ParsedGeometry对象
        """
        original_desc = description
        description = description.lower().strip()

        # 1. 识别形状类型
        shape_type = self._detect_shape(description)

        # 2. 提取参数
        parameters = self._extract_parameters(description)

        # 3. 识别特征
        features = self._detect_features(description)

        # 4. 识别材料
        material = self._detect_material(description)

        # 5. 识别位置和旋转
        position = self._detect_position(description)
        rotation = self._detect_rotation(description)

        # 6. 设置默认值
        parameters = self._set_defaults(shape_type, parameters)

        return ParsedGeometry(
            shape_type=shape_type,
            parameters=parameters,
            features=features,
            material=material,
            description=original_desc,
            position=position,
            rotation=rotation,
        )

    def parse_with_llm(self, description: str, llm_model, language: str = "zh") -> Optional[ParsedGeometry]:
        """使用LLM模型解析复杂描述

        Args:
            description: 自然语言描述
            llm_model: 已加载的LLM模型
            language: 语言 "zh" 或 "en"

        Returns:
            ParsedGeometry对象，失败返回None
        """
        template = PROMPT_TEMPLATES.get(language, PROMPT_TEMPLATES["zh"])

        # 构建完整prompt
        full_prompt = f"{template['system']}\n\nUser: {description}\nAssistant:"

        try:
            # 调用LLM
            response = llm_model.chat(
                message=full_prompt,
                temperature=0.1,
                max_tokens=512,
            )

            # 解析JSON响应
            return self._parse_llm_response(response)

        except Exception as e:
            print(f"LLM解析失败: {e}")
            # 回退到正则解析
            return self.parse(description)

    def _parse_llm_response(self, response: str) -> Optional[ParsedGeometry]:
        """解析LLM返回的JSON响应"""
        try:
            # 提取JSON部分
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if not json_match:
                return None

            data = json.loads(json_match.group())

            return ParsedGeometry(
                shape_type=data.get("shape_type", "box"),
                parameters=data.get("parameters", {}),
                features=data.get("features", []),
                material=data.get("material"),
                description="",
            )

        except (json.JSONDecodeError, KeyError) as e:
            print(f"JSON解析错误: {e}")
            return None

    def _detect_shape(self, desc: str) -> str:
        """检测形状类型"""
        for keyword, shape in self.SHAPE_KEYWORDS.items():
            if keyword in desc:
                return shape
        return "box"  # 默认为立方体

    @classmethod
    def _get_compiled_patterns(cls):
        """获取预编译的正则表达式模式（延迟初始化）"""
        if cls._PARAM_PATTERNS_COMPILED is None:
            cls._PARAM_PATTERNS_COMPILED = {}
            for param_name, patterns in cls.PARAM_PATTERNS.items():
                cls._PARAM_PATTERNS_COMPILED[param_name] = [re.compile(p, re.IGNORECASE) for p in patterns]
        return cls._PARAM_PATTERNS_COMPILED

    def _extract_parameters(self, desc: str) -> Dict[str, float]:
        """提取尺寸参数"""
        params = {}
        compiled = self._get_compiled_patterns()

        for param_name, compiled_patterns in compiled.items():
            for pattern in compiled_patterns:
                match = pattern.search(desc)
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
        fillet_match = self._FILET_PATTERN.search(desc)
        if fillet_match:
            features.append(
                {
                    "type": "fillet",
                    "radius": float(fillet_match.group(1)),
                    "edges": "all",
                }
            )

        # 检测孔
        hole_match = self._HOLE_PATTERN.search(desc)
        if hole_match:
            features.append({"type": "hole", "diameter": float(hole_match.group(1))})

        return features

    def _detect_material(self, desc: str) -> Optional[str]:
        """检测材料"""
        for material, keywords in self.MATERIAL_KEYWORDS.items():
            for kw in keywords:
                if kw in desc:
                    return material
        return None

    def _detect_position(self, desc: str) -> Optional[Dict[str, float]]:
        """检测位置参数"""
        pos = {}

        x_match = self._POS_X_PATTERN.search(desc)
        if x_match:
            pos["x"] = float(x_match.group(1))

        y_match = self._POS_Y_PATTERN.search(desc)
        if y_match:
            pos["y"] = float(y_match.group(1))

        z_match = self._POS_Z_PATTERN.search(desc)
        if z_match:
            pos["z"] = float(z_match.group(1))

        return pos if pos else None

    def _detect_rotation(self, desc: str) -> Optional[Dict[str, float]]:
        """检测旋转参数"""
        rot = {}

        rx_match = self._ROT_X_PATTERN.search(desc)
        if rx_match:
            rot["x"] = float(rx_match.group(1))

        ry_match = self._ROT_Y_PATTERN.search(desc)
        if ry_match:
            rot["y"] = float(ry_match.group(1))

        rz_match = self._ROT_Z_PATTERN.search(desc)
        if rz_match:
            rot["z"] = float(rz_match.group(1))

        return rot if rot else None

    def _detect_boolean(self, desc: str) -> Optional[Dict[str, Any]]:
        """检测布尔运算"""
        for op_type, keywords in self.BOOLEAN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in desc:
                    # 尝试提取第二个形状的参数
                    return {"type": op_type, "keyword": keyword}
        return None

    def _set_defaults(self, shape: str, params: Dict[str, float]) -> Dict[str, float]:
        """设置默认值"""
        defaults = {
            "box": {"length": 100, "width": 50, "height": 30},
            "plate": {"length": 100, "width": 100, "thickness": 10},
            "cylinder": {"radius": 25, "height": 50},
            "pipe": {"radius": 25, "thickness": 5, "height": 100},
            "sphere": {"radius": 30},
            "cone": {"radius": 25, "height": 50},
            "frustum": {"radius": 25, "radius2": 15, "height": 50},
            "torus": {"radius": 30, "tube_radius": 10},
            "wedge": {"length": 100, "width": 50, "height": 30},
            "prism": {"polygon": 6, "radius": 25, "height": 50},
            "hexagon_prism": {"radius": 25, "height": 50},
            "bracket": {"length": 100, "width": 50, "height": 30, "thickness": 10},
            "l_shape": {"length": 100, "width": 50, "height": 30, "thickness": 10},
            "u_shape": {"length": 100, "width": 50, "height": 30, "thickness": 10},
            "t_shape": {"length": 100, "width": 50, "height": 30, "thickness": 10},
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
                    Part.LineSegment(self.fc_app.Vector(0, 0, 0), self.fc_app.Vector(length, 0, 0)),
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
                    Part.LineSegment(self.fc_app.Vector(0, width, 0), self.fc_app.Vector(0, 0, 0)),
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

            elif shape_type == "cone":
                radius = params.get("radius", 25)
                height = params.get("height", 50)
                # 圆锥（顶点朝上）
                cone = Part.makeCone(radius, 0, height)
                obj = self.doc.addObject("Part::Feature", "Cone")
                obj.Shape = cone

            elif shape_type == "frustum":
                # 圆台
                radius = params.get("radius", 25)
                radius2 = params.get("radius2", 15)
                height = params.get("height", 50)
                frustum = Part.makeCone(radius, radius2, height)
                obj = self.doc.addObject("Part::Feature", "Frustum")
                obj.Shape = frustum

            elif shape_type == "torus":
                radius = params.get("radius", 30)
                tube_radius = params.get("tube_radius", 10)
                torus = Part.makeTorus(radius, tube_radius)
                obj = self.doc.addObject("Part::Feature", "Torus")
                obj.Shape = torus

            elif shape_type == "cylinder":
                radius = params.get("radius", 25)
                height = params.get("height", 50)
                cylinder = Part.makeCylinder(radius, height)
                obj = self.doc.addObject("Part::Feature", "Cylinder")
                obj.Shape = cylinder

            elif shape_type == "pipe":
                # 空心圆管
                radius = params.get("radius", 25)
                thickness = params.get("thickness", 5)
                height = params.get("height", 100)
                outer = Part.makeCylinder(radius, height)
                inner = Part.makeCylinder(radius - thickness, height)
                pipe = outer.cut(inner)
                obj = self.doc.addObject("Part::Feature", "Pipe")
                obj.Shape = pipe

            elif shape_type == "plate":
                # 薄板
                length = params.get("length", 100)
                width = params.get("width", 100)
                thickness = params.get("thickness", 10)
                plate = Part.makeBox(length, width, thickness)
                obj = self.doc.addObject("Part::Feature", "Plate")
                obj.Shape = plate

            elif shape_type == "wedge":
                # 楔形
                length = params.get("length", 100)
                width = params.get("width", 50)
                height = params.get("height", 30)
                # 创建楔形的顶点
                [
                    self.fc_app.Vector(0, 0, 0),
                    self.fc_app.Vector(length, 0, 0),
                    self.fc_app.Vector(length, width, 0),
                    self.fc_app.Vector(0, width, 0),
                    self.fc_app.Vector(0, 0, height),
                    self.fc_app.Vector(0, width, height),
                ]
                # 简化：创建拉伸体
                wedge = Part.makeBox(length, width, height)
                obj = self.doc.addObject("Part::Feature", "Wedge")
                obj.Shape = wedge

            elif shape_type == "prism":
                # 棱柱
                polygon = int(params.get("polygon", 6))
                radius = params.get("radius", 25)
                height = params.get("height", 50)
                prism = Part.makePrism(radius, height, polygon)
                obj = self.doc.addObject("Part::Feature", "Prism")
                obj.Shape = prism

            elif shape_type == "hexagon_prism":
                # 六棱柱
                radius = params.get("radius", 25)
                height = params.get("height", 50)
                prism = Part.makePrism(radius, height, 6)
                obj = self.doc.addObject("Part::Feature", "HexagonPrism")
                obj.Shape = prism

            elif shape_type in ("bracket", "l_shape", "u_shape", "t_shape"):
                # 复杂形状：简化为组合Box
                length = params.get("length", 100)
                width = params.get("width", 50)
                height = params.get("height", 30)
                thickness = params.get("thickness", 10)

                if shape_type == "l_shape":
                    # L型支架
                    box1 = Part.makeBox(length, thickness, height)
                    box2 = Part.makeBox(thickness, width, height)
                    shape = box1.fuse(box2)
                elif shape_type == "u_shape":
                    # U型支架
                    box1 = Part.makeBox(length, thickness, height)
                    box2 = Part.makeBox(thickness, width, height)
                    box3 = Part.makeBox(length, thickness, height).translate(
                        self.fc_app.Vector(0, width - thickness, 0)
                    )
                    shape = box1.fuse(box2).fuse(box3)
                elif shape_type == "t_shape":
                    # T型支架
                    box1 = Part.makeBox(length, thickness, height)
                    box2 = Part.makeBox(thickness, width, height)
                    shape = box1.fuse(box2)
                else:
                    # 通用支架
                    shape = Part.makeBox(length, width, height)

                obj = self.doc.addObject("Part::Feature", shape_type.capitalize())
                obj.Shape = shape

            else:
                # 默认：立方体
                length = params.get("length", 100)
                width = params.get("width", 50)
                height = params.get("height", 30)
                box = Part.makeBox(length, width, height)
                obj = self.doc.addObject("Part::Feature", "Box")
                obj.Shape = box

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

            objects = [obj for obj in self.doc.Objects if obj.isDerivedFrom("Part::Feature")]
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
            except Exception:
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

                print(f" 质量评分: {result['detailed_analysis']['quality_score']:.1f}/100")

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
