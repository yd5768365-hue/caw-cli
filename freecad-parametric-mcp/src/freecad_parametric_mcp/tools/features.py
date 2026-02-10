"""Feature Tools"""

import json


class FeatureTools:
    """Tools for parametric feature creation"""

    def __init__(self, bridge):
        self.bridge = bridge

    async def create_pad(
        self, sketch: str, length_param: str, direction: str = "forward", name: str = None
    ) -> dict:
        """Create parametric pad (extrusion)"""
        feature_name = name or f"Pad_{sketch}"

        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
sketch = doc.getObject("{sketch}")
if not sketch:
    print(json.dumps({{"error": "Sketch not found"}}))
else:
    if "PartDesign" not in FreeCAD.activeWorkbenches():
        FreeCAD.activateWorkbench("PartDesignWorkbench")
    
    # Create body if needed
    body = None
    for obj in doc.Objects:
        if obj.TypeId == "PartDesign::Body":
            body = obj
            break
    
    if not body:
        body = doc.addObject("PartDesign::Body", "Body")
    
    # Ensure sketch is in body
    if sketch not in body.Group:
        body.addObject(sketch)
    
    # Create pad
    pad = doc.addObject("PartDesign::Pad", "{feature_name}")
    body.addObject(pad)
    pad.Profile = sketch
    
    # Set length - try to parse as number or use expression
    try:
        length = float("{length_param}")
        pad.Length = length
    except:
        # It's a parameter reference, store for later binding
        pad.addProperty("App::PropertyString", "LengthParam")
        pad.LengthParam = "{length_param}"
    
    # Set direction
    direction_map = {{"forward": 0, "reverse": 1, "both": 2}}
    pad.Direction = direction_map.get("{direction}", 0)
    
    doc.recompute()
    print(json.dumps({{
        "success": True,
        "feature": pad.Name,
        "type": "Pad",
        "length": "{length_param}",
        "direction": "{direction}"
    }}))
"""
        return self.bridge.execute_python(code)

    async def create_pocket(self, sketch: str, depth_param: str, name: str = None) -> dict:
        """Create parametric pocket"""
        feature_name = name or f"Pocket_{sketch}"

        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
sketch = doc.getObject("{sketch}")
if not sketch:
    print(json.dumps({{"error": "Sketch not found"}}))
else:
    body = None
    for obj in doc.Objects:
        if obj.TypeId == "PartDesign::Body":
            body = obj
            break
    
    if not body:
        print(json.dumps({{"error": "No PartDesign Body found"}}))
    else:
        pocket = doc.addObject("PartDesign::Pocket", "{feature_name}")
        body.addObject(pocket)
        pocket.Profile = sketch
        
        try:
            depth = float("{depth_param}")
            pocket.Length = depth
        except:
            pocket.addProperty("App::PropertyString", "DepthParam")
            pocket.DepthParam = "{depth_param}"
        
        doc.recompute()
        print(json.dumps({{
            "success": True,
            "feature": pocket.Name,
            "type": "Pocket"
        }}))
"""
        return self.bridge.execute_python(code)

    async def create_hole(
        self,
        position: dict,
        diameter_param: str,
        depth_param: str = None,
        hole_type: str = "simple",
        name: str = None,
    ) -> dict:
        """Create parametric hole"""
        feature_name = name or "Hole"

        code = f"""
import json
import FreeCAD
import Part

doc = FreeCAD.ActiveDocument
body = None
for obj in doc.Objects:
    if obj.TypeId == "PartDesign::Body":
        body = obj
        break

if not body:
    print(json.dumps({{"error": "No PartDesign Body found"}}))
else:
    # Create hole feature
    hole = doc.addObject("PartDesign::Hole", "{feature_name}")
    body.addObject(hole)
    
    # Set hole properties
    try:
        diameter = float("{diameter_param}")
        hole.Diameter = diameter
    except:
        hole.addProperty("App::PropertyString", "DiameterParam")
        hole.DiameterParam = "{diameter_param}"
    
    hole.HoleType = "{hole_type}"
    
    if "{depth_param}":
        try:
            depth = float("{depth_param}")
            hole.Depth = depth
        except:
            hole.addProperty("App::PropertyString", "DepthParam")
            hole.DepthParam = "{depth_param}"
    
    doc.recompute()
    print(json.dumps({{
        "success": True,
        "feature": hole.Name,
        "type": "Hole",
        "hole_type": "{hole_type}"
    }}))
"""
        return self.bridge.execute_python(code)

    async def edit_parameter(
        self, feature: str, parameter: str, value: str, regenerate: bool = True
    ) -> dict:
        """Edit feature parameter"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
feat = doc.getObject("{feature}")
if not feat:
    print(json.dumps({{"error": "Feature not found"}}))
else:
    param = "{parameter}"
    value = "{value}"
    
    # Try to set as number first
    try:
        num_value = float(value)
        setattr(feat, param, num_value)
    except:
        # Store as parameter reference
        if hasattr(feat, param + "Param"):
            setattr(feat, param + "Param", value)
        else:
            feat.addProperty("App::PropertyString", param + "Param")
            setattr(feat, param + "Param", value)
    
    if {regenerate}:
        doc.recompute()
    
    print(json.dumps({{
        "success": True,
        "feature": "{feature}",
        "parameter": param,
        "value": value
    }}))
"""
        return self.bridge.execute_python(code)

    async def get_tree(self, document: str = None, include_suppressed: bool = False) -> dict:
        """Get feature tree"""
        doc_filter = (
            f'doc = FreeCAD.getDocument("{document}")'
            if document
            else "doc = FreeCAD.ActiveDocument"
        )

        code = f"""
import json
import FreeCAD

{doc_filter}
if not doc:
    print(json.dumps({{"error": "Document not found"}}))
else:
    tree = []
    
    for obj in doc.Objects:
        node = {{
            "name": obj.Name,
            "label": obj.Label,
            "type": obj.TypeId if hasattr(obj, 'TypeId') else type(obj).__name__,
        }}
        
        if hasattr(obj, 'Visibility'):
            node["visible"] = obj.Visibility
        
        if hasattr(obj, 'State'):
            node["state"] = obj.State
            node["invalid"] = 'Invalid' in obj.State
        
        tree.append(node)
    
    print(json.dumps({{
        "document": doc.Name,
        "features": tree,
        "count": len(tree)
    }}))
"""
        return self.bridge.execute_python(code)

    async def analyze_dependencies(self, feature: str, direction: str = "both") -> dict:
        """Analyze feature dependencies"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
feat = doc.getObject("{feature}")
if not feat:
    print(json.dumps({{"error": "Feature not found"}}))
else:
    upstream = []
    downstream = []
    
    # Find upstream (what this feature depends on)
    if hasattr(feat, 'Profile'):
        upstream.append({{"type": "Profile", "name": feat.Profile.Name if feat.Profile else None}})
    
    # Find downstream (what depends on this feature)
    for obj in doc.Objects:
        if hasattr(obj, 'Profile') and obj.Profile == feat:
            downstream.append({{"name": obj.Name, "type": obj.TypeId}})
    
    result = {{"feature": "{feature}"}}
    
    direction = "{direction}"
    if direction in ["upstream", "both"]:
        result["upstream"] = upstream
    if direction in ["downstream", "both"]:
        result["downstream"] = downstream
    
    print(json.dumps(result))
"""
        return self.bridge.execute_python(code)
