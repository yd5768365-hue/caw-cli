"""Sketch Tools"""

import json


class SketchTools:
    """Tools for parametric sketching"""

    def __init__(self, bridge):
        self.bridge = bridge

    async def create_sketch(
        self, name: str, plane: str, body: str = None, parameters: dict = None
    ) -> dict:
        """Create a parametric sketch"""
        body_code = f'body = doc.getObject("{body}")' if body else "body = None"

        code = f"""
import json
import FreeCAD
import Part
import Sketcher

if "PartDesign" not in FreeCAD.activeWorkbenches():
    FreeCAD.activateWorkbench("PartDesignWorkbench")

doc = FreeCAD.ActiveDocument
if not doc:
    doc = FreeCAD.newDocument("ParametricDesign")

{body_code}

if body:
    sketch = doc.addObject("Sketcher::SketchObject", "{name}")
    body.addObject(sketch)
else:
    sketch = doc.addObject("Sketcher::SketchObject", "{name}")

# Set plane
plane_map = {{"XY": "XY_Plane", "XZ": "XZ_Plane", "YZ": "YZ_Plane"}}
plane_name = plane_map.get("{plane}", "{plane}")
sketch.Support = (doc.getObject(plane_name), [""])
sketch.MapMode = "FlatFace"

# Store parameter references
if {json.dumps(parameters)}:
    sketch.addProperty("App::PropertyString", "ParameterRefs")
    sketch.ParameterRefs = json.dumps({json.dumps(parameters)})

doc.recompute()
print(json.dumps({{"success": True, "sketch": sketch.Name, "plane": "{plane}"}}))
"""
        return self.bridge.execute_python(code)

    async def add_line(
        self,
        sketch: str,
        start: dict,
        end: dict,
        constraints: list = None,
        parameter_refs: dict = None,
    ) -> dict:
        """Add a constrained line"""
        code = f"""
import json
import FreeCAD
import Part

doc = FreeCAD.ActiveDocument
sketch = doc.getObject("{sketch}")
if not sketch:
    print(json.dumps({{"error": "Sketch not found"}}))
else:
    # Add line
    start_point = FreeCAD.Vector({start["x"]}, {start["y"]}, 0)
    end_point = FreeCAD.Vector({end["x"]}, {end["y"]}, 0)
    
    geo_index = sketch.addGeometry(Part.LineSegment(start_point, end_point), False)
    
    # Add constraints
    constraint_list = {json.dumps(constraints or [])}
    for constraint in constraint_list:
        if constraint == "horizontal":
            sketch.addConstraint(Sketcher.Constraint("Horizontal", geo_index))
        elif constraint == "vertical":
            sketch.addConstraint(Sketcher.Constraint("Vertical", geo_index))
    
    doc.recompute()
    print(json.dumps({{"success": True, "geometry_index": geo_index}}))
"""
        return self.bridge.execute_python(code)

    async def add_circle(
        self, sketch: str, center: dict, radius: str, construction: bool = False
    ) -> dict:
        """Add a constrained circle"""
        code = f"""
import json
import FreeCAD
import Part

doc = FreeCAD.ActiveDocument
sketch = doc.getObject("{sketch}")
if not sketch:
    print(json.dumps({{"error": "Sketch not found"}}))
else:
    center_point = FreeCAD.Vector({center["x"]}, {center["y"]}, 0)
    
    # Try to parse radius as number or use as expression
    try:
        r = float("{radius}")
    except:
        r = 10  # Default, will be constrained
    
    geo_index = sketch.addGeometry(Part.Circle(center_point, FreeCAD.Vector(0,0,1), r), {construction})
    
    # Add radius constraint if radius is a parameter reference
    if not "{radius}".replace('.','').replace('-','').isdigit():
        # It's a parameter reference
        constraint_index = sketch.addConstraint(Sketcher.Constraint(
            "Radius", geo_index, r
        ))
        # Store parameter reference for later binding
    
    doc.recompute()
    print(json.dumps({{"success": True, "geometry_index": geo_index}}))
"""
        return self.bridge.execute_python(code)

    async def add_constraint(
        self, sketch: str, type: str, entities: list, value: str = None, expression: str = None
    ) -> dict:
        """Add dimensional constraint"""
        entities_str = json.dumps(entities)

        code = f"""
import json
import FreeCAD
import Sketcher

doc = FreeCAD.ActiveDocument
sketch = doc.getObject("{sketch}")
if not sketch:
    print(json.dumps({{"error": "Sketch not found"}}))
else:
    entities = {entities_str}
    constraint_type = "{type}"
    
    try:
        if constraint_type == "distance":
            if len(entities) == 2:
                c = sketch.addConstraint(Sketcher.Constraint(
                    "Distance", entities[0], entities[1], float("{value}")
                ))
            else:
                c = sketch.addConstraint(Sketcher.Constraint(
                    "Distance", entities[0], 1, entities[0], 2, float("{value}")
                ))
        elif constraint_type == "radius":
            c = sketch.addConstraint(Sketcher.Constraint(
                "Radius", entities[0], float("{value}")
            ))
        elif constraint_type == "diameter":
            c = sketch.addConstraint(Sketcher.Constraint(
                "Diameter", entities[0], float("{value}")
            ))
        elif constraint_type == "angle":
            c = sketch.addConstraint(Sketcher.Constraint(
                "Angle", entities[0], entities[1], float("{value}")
            ))
        
        doc.recompute()
        print(json.dumps({{"success": True, "constraint_index": c}}))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
"""
        return self.bridge.execute_python(code)

    async def auto_constrain(
        self, sketch: str, strategy: str = "standard", detect_symmetry: bool = True
    ) -> dict:
        """Auto-constrain sketch"""
        code = f"""
import json
import FreeCAD
import Sketcher

doc = FreeCAD.ActiveDocument
sketch = doc.getObject("{sketch}")
if not sketch:
    print(json.dumps({{"error": "Sketch not found"}}))
else:
    # Auto-constrain logic based on strategy
    strategy = "{strategy}"
    added_constraints = 0
    
    # Detect horizontal/vertical lines
    for i, geo in enumerate(sketch.Geometry):
        if hasattr(geo, 'StartPoint') and hasattr(geo, 'EndPoint'):
            start = geo.StartPoint
            end = geo.EndPoint
            
            # Check if horizontal
            if abs(start.y - end.y) < 0.001 and strategy in ["standard", "full"]:
                try:
                    sketch.addConstraint(Sketcher.Constraint("Horizontal", i))
                    added_constraints += 1
                except:
                    pass
            
            # Check if vertical
            if abs(start.x - end.x) < 0.001 and strategy in ["standard", "full"]:
                try:
                    sketch.addConstraint(Sketcher.Constraint("Vertical", i))
                    added_constraints += 1
                except:
                    pass
    
    # Detect coincidences
    if strategy == "full":
        points = []
        for i, geo in enumerate(sketch.Geometry):
            if hasattr(geo, 'StartPoint'):
                points.append((i, geo.StartPoint))
            if hasattr(geo, 'EndPoint'):
                points.append((i, geo.EndPoint))
        
        for i, (gi, p1) in enumerate(points):
            for j, (gj, p2) in enumerate(points[i+1:], i+1):
                if p1.distanceToPoint(p2) < 0.001 and gi != gj:
                    try:
                        sketch.addConstraint(Sketcher.Constraint(
                            "Coincident", gi, 1 if p1 == sketch.Geometry[gi].StartPoint else 2,
                            gj, 1 if p2 == sketch.Geometry[gj].StartPoint else 2
                        ))
                        added_constraints += 1
                    except:
                        pass
    
    doc.recompute()
    print(json.dumps({{
        "success": True,
        "constraints_added": added_constraints,
        "strategy": strategy
    }}))
"""
        return self.bridge.execute_python(code)

    async def analyze_dof(self, sketch: str, detailed: bool = False) -> dict:
        """Analyze sketch degrees of freedom"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
sketch = doc.getObject("{sketch}")
if not sketch:
    print(json.dumps({{"error": "Sketch not found"}}))
else:
    dof = sketch.DegreeOfFreedom
    geometry_count = len(sketch.Geometry)
    constraint_count = len(sketch.Constraints)
    
    result = {{
        "dof": dof,
        "geometry_count": geometry_count,
        "constraint_count": constraint_count,
        "fully_constrained": dof == 0,
        "over_constrained": dof < 0
    }}
    
    if {detailed}:
        result["constraints"] = [str(c.Type) for c in sketch.Constraints]
    
    print(json.dumps(result))
"""
        return self.bridge.execute_python(code)

    async def get_constraint_graph(
        self, sketch: str, format: str = "json", include_dof: bool = True
    ) -> dict:
        """Get constraint relationship graph"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
sketch = doc.getObject("{sketch}")
if not sketch:
    print(json.dumps({{"error": "Sketch not found"}}))
else:
    nodes = []
    edges = []
    
    # Add geometry nodes
    for i, geo in enumerate(sketch.Geometry):
        node = {{
            "id": f"geo_{{i}}",
            "type": geo.TypeId if hasattr(geo, 'TypeId') else type(geo).__name__,
            "index": i
        }}
        nodes.append(node)
    
    # Add constraint nodes and edges
    for i, con in enumerate(sketch.Constraints):
        node = {{
            "id": f"con_{{i}}",
            "type": con.Type,
            "value": con.Value if hasattr(con, 'Value') else None,
            "index": i
        }}
        nodes.append(node)
        
        # Connect constraint to geometry
        if hasattr(con, 'First'):
            edges.append({{"source": f"con_{{i}}", "target": f"geo_{{con.First}}"}})
        if hasattr(con, 'Second') and con.Second >= 0:
            edges.append({{"source": f"con_{{i}}", "target": f"geo_{{con.Second}}"}})
    
    result = {{
        "nodes": nodes,
        "edges": edges,
        "format": "{format}"
    }}
    
    if {include_dof}:
        result["dof"] = sketch.DegreeOfFreedom
    
    print(json.dumps(result))
"""
        return self.bridge.execute_python(code)
