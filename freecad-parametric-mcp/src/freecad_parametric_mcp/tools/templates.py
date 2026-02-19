"""Template Tools"""

import json


class TemplateTools:
    """Tools for template-based design"""

    def __init__(self, bridge):
        self.bridge = bridge
        self._templates = self._load_templates()

    def _load_templates(self) -> dict:
        """Load built-in templates"""
        return {
            "spur_gear": {
                "category": "mechanical",
                "parameters": ["module", "teeth", "width", "pressure_angle"],
                "description": "Standard spur gear",
            },
            "flange": {
                "category": "mechanical",
                "parameters": ["outer_dia", "inner_dia", "thickness", "bolt_circle", "bolt_count"],
                "description": "Standard flange",
            },
            "bracket": {
                "category": "structural",
                "parameters": ["length", "width", "height", "thickness", "hole_dia"],
                "description": "L-shaped bracket",
            },
            "bearing_housing": {
                "category": "mechanical",
                "parameters": ["bearing_od", "housing_od", "width", "flange_thickness"],
                "description": "Bearing housing with flange",
            },
            "pulley": {
                "category": "mechanical",
                "parameters": ["diameter", "width", "bore", "groove_count"],
                "description": "V-belt pulley",
            },
            "box": {
                "category": "enclosure",
                "parameters": ["length", "width", "height", "wall_thickness"],
                "description": "Hollow box enclosure",
            },
        }

    async def list_templates(self, category: str = None) -> dict:
        """List available templates"""
        templates = self._templates

        if category:
            templates = {k: v for k, v in templates.items() if v.get("category") == category}

        return {
            "templates": [{"name": name, **info} for name, info in templates.items()],
            "count": len(templates),
        }

    async def create_from_template(self, template: str, parameters: dict, name: str = None) -> dict:
        """Create model from template"""
        if template not in self._templates:
            return {"error": f"Template '{template}' not found"}

        template_info = self._templates[template]
        model_name = name or f"{template.capitalize()}_1"

        # Generate code based on template type
        if template == "spur_gear":
            return await self._create_spur_gear(model_name, parameters)
        elif template == "flange":
            return await self._create_flange(model_name, parameters)
        elif template == "bracket":
            return await self._create_bracket(model_name, parameters)
        else:
            # Generic template
            code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    doc = FreeCAD.newDocument("{model_name}")

# Create body
body = doc.addObject("PartDesign::Body", "Body")

# Create parameters spreadsheet
params = doc.addObject("Spreadsheet::Sheet", "Parameters")
params.Label = "_Parameters_"

# Set template parameters
param_data = {json.dumps(parameters)}
row = 1
for key, value in param_data.items():
    row += 1
    params.set(f"A{{row}}", "dimensions")
    params.set(f"B{{row}}", key)
    params.set(f"C{{row}}", value)

doc.recompute()
print(json.dumps({{
    "success": True,
    "template": "{template}",
    "model": "{model_name}",
    "parameters_set": len(param_data)
}}))
"""
            return self.bridge.execute_python(code)

    async def _create_spur_gear(self, name: str, params: dict) -> dict:
        """Create spur gear from template"""
        module_val = params.get("module", 2.0)
        teeth = params.get("teeth", 20)
        width = params.get("width", 10)
        pressure_angle = params.get("pressure_angle", 20)

        code = f"""
import json
import FreeCAD
import Part
import PartDesign
import Sketcher
import math

if "PartDesign" not in FreeCAD.activeWorkbenches():
    FreeCAD.activateWorkbench("PartDesignWorkbench")

doc = FreeCAD.newDocument("{name}")

# Create body
body = doc.addObject("PartDesign::Body", "Body")

# Create parameters
params_sheet = doc.addObject("Spreadsheet::Sheet", "GearParams")
params_sheet.Label = "_Parameters_"
params_sheet.set("A1", "Group")
params_sheet.set("B1", "Name")
params_sheet.set("C1", "Value")
params_sheet.set("D1", "Unit")

# Set gear parameters
row = 2
params_sheet.set(f"A{{row}}", "gear")
params_sheet.set(f"B{{row}}", "module")
params_sheet.set(f"C{{row}}", {module_val})
params_sheet.set(f"D{{row}}", "mm")

row += 1
params_sheet.set(f"A{{row}}", "gear")
params_sheet.set(f"B{{row}}", "teeth")
params_sheet.set(f"C{{row}}", {teeth})
params_sheet.set(f"D{{row}}", "count")

row += 1
params_sheet.set(f"A{{row}}", "gear")
params_sheet.set(f"B{{row}}", "width")
params_sheet.set(f"C{{row}}", {width})
params_sheet.set(f"D{{row}}", "mm")

row += 1
params_sheet.set(f"A{{row}}", "gear")
params_sheet.set(f"B{{row}}", "pressure_angle")
params_sheet.set(f"C{{row}}", {pressure_angle})
params_sheet.set(f"D{{row}}", "deg")

# Calculated parameters
row += 1
params_sheet.set(f"A{{row}}", "gear")
params_sheet.set(f"B{{row}}", "pitch_diameter")
params_sheet.set(f"C{{row}}", f"={module_val}*{teeth}")
params_sheet.set(f"D{{row}}", "mm")

row += 1
params_sheet.set(f"A{{row}}", "gear")
params_sheet.set(f"B{{row}}", "outer_diameter")
params_sheet.set(f"C{{row}}", f"={module_val}*({teeth}+2)")
params_sheet.set(f"D{{row}}", "mm")

doc.recompute()

print(json.dumps({{
    "success": True,
    "template": "spur_gear",
    "model": "{name}",
    "parameters": {{
        "module": {module_val},
        "teeth": {teeth},
        "width": {width},
        "pressure_angle": {pressure_angle}
    }},
    "note": "Gear profile generation requires additional profile sketching"
}}))
"""
        return self.bridge.execute_python(code)

    async def _create_flange(self, name: str, params: dict) -> dict:
        """Create flange from template"""
        outer_dia = params.get("outer_dia", 100)
        inner_dia = params.get("inner_dia", 50)
        thickness = params.get("thickness", 10)
        bolt_circle = params.get("bolt_circle", 80)
        bolt_count = params.get("bolt_count", 4)

        code = f"""
import json
import FreeCAD
import Part
import PartDesign
import Sketcher

doc = FreeCAD.newDocument("{name}")
body = doc.addObject("PartDesign::Body", "Body")

# Create base sketch on XY plane
sketch = doc.addObject("Sketcher::SketchObject", "Flange_Sketch")
body.addObject(sketch)

# Add outer circle
outer_geo = sketch.addGeometry(Part.Circle(
    FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), {outer_dia}/2
), False)

# Add inner circle (hole)
inner_geo = sketch.addGeometry(Part.Circle(
    FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1), {inner_dia}/2
), False)

# Add constraints
sketch.addConstraint(Sketcher.Constraint("Coincident", outer_geo, 3, -1, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", inner_geo, 3, -1, 1))
sketch.addConstraint(Sketcher.Constraint("Diameter", outer_geo, {outer_dia}))
sketch.addConstraint(Sketcher.Constraint("Diameter", inner_geo, {inner_dia}))

# Pad to create flange
pad = doc.addObject("PartDesign::Pad", "Flange_Body")
body.addObject(pad)
pad.Profile = sketch
pad.Length = {thickness}

# Add bolt holes
import math
for i in range({bolt_count}):
    angle = 2 * math.pi * i / {bolt_count}
    x = {bolt_circle}/2 * math.cos(angle)
    y = {bolt_circle}/2 * math.sin(angle)
    
    # Create hole sketch
    hole_sketch = doc.addObject("Sketcher::SketchObject", f"Hole_{{i}}")
    body.addObject(hole_sketch)
    hole_sketch.Support = (pad, ["Face3"])
    hole_sketch.MapMode = "FlatFace"
    
    hole_geo = hole_sketch.addGeometry(Part.Circle(
        FreeCAD.Vector(x, y, 0), FreeCAD.Vector(0,0,1), 5
    ), False)
    
    hole = doc.addObject("PartDesign::Hole", f"BoltHole_{{i}}")
    body.addObject(hole)
    hole.Profile = hole_sketch
    hole.Diameter = 8
doc.recompute()

print(json.dumps({{
    "success": True,
    "template": "flange",
    "model": "{name}",
    "parameters": {{
        "outer_dia": {outer_dia},
        "inner_dia": {inner_dia},
        "thickness": {thickness},
        "bolt_circle": {bolt_circle},
        "bolt_count": {bolt_count}
    }}
}}))
"""
        return self.bridge.execute_python(code)

    async def _create_bracket(self, name: str, params: dict) -> dict:
        """Create L-bracket from template"""
        length = params.get("length", 100)
        width = params.get("width", 50)
        height = params.get("height", 50)
        thickness = params.get("thickness", 5)
        hole_dia = params.get("hole_dia", 8)

        code = f"""
import json
import FreeCAD
import PartDesign

doc = FreeCAD.newDocument("{name}")
body = doc.addObject("PartDesign::Body", "Body")

# This is a simplified bracket - would need more detailed modeling
# For now, create a basic shape
box1 = doc.addObject("Part::Box", "Vertical_Plate")
box1.Length = {thickness}
box1.Width = {width}
box1.Height = {height}

box2 = doc.addObject("Part::Box", "Horizontal_Plate")
box2.Length = {length}
box2.Width = {width}
box2.Height = {thickness}
box2.Placement.Base = FreeCAD.Vector(0, 0, 0)

# Fuse them
fuse = doc.addObject("Part::Fuse", "Bracket")
fuse.Base = box1
fuse.Tool = box2

doc.recompute()

print(json.dumps({{
    "success": True,
    "template": "bracket",
    "model": "{name}",
    "parameters": {{
        "length": {length},
        "width": {width},
        "height": {height},
        "thickness": {thickness},
        "hole_dia": {hole_dia}
    }},
    "note": "Simplified bracket - full parametric version requires PartDesign approach"
}}))
"""
        return self.bridge.execute_python(code)
