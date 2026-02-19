"""History Tools"""

import json
from datetime import datetime


class HistoryTools:
    """Tools for design history management"""

    def __init__(self, bridge):
        self.bridge = bridge

    async def get_timeline(self, document: str = None, limit: int = 50) -> dict:
        """Get design timeline"""
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
    # Get history from document properties or rebuild from objects
    timeline = []
    
    for i, obj in enumerate(doc.Objects):
        event = {{
            "index": i,
            "timestamp": str(datetime.now()),  # FreeCAD doesn't store timestamps natively
            "action": "create",
            "object": obj.Name,
            "label": obj.Label,
            "type": obj.TypeId if hasattr(obj, 'TypeId') else type(obj).__name__
        }}
        timeline.append(event)
    
    # Limit results
    timeline = timeline[-{limit}:]
    
    print(json.dumps({{
        "document": doc.Name,
        "timeline": timeline,
        "total_events": len(doc.Objects)
    }}))
"""
        return self.bridge.execute_python(code)

    async def create_branch(
        self, name: str, from_version: str = None, description: str = ""
    ) -> dict:
        """Create design branch"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    # Save current state as a branch
    branch_name = "{name}"
    
    # Store branch info in document metadata
    if not hasattr(doc, "Branches"):
        doc.addProperty("App::PropertyString", "Branches")
        doc.Branches = "{{}}"
    
    # Parse existing branches
    try:
        branches = json.loads(doc.Branches)
    except:
        branches = {{}}
    
    # Add new branch
    branches[branch_name] = {{
        "created": str(datetime.now()),
        "description": "{description}",
        "from_version": "{from_version or "current"}",
        "object_count": len(doc.Objects)
    }}
    
    doc.Branches = json.dumps(branches)
    
    # Save document copy for branch
    import os
    base_path = os.path.dirname(doc.FileName) if doc.FileName else "."
    branch_file = os.path.join(base_path, f"{{branch_name}}.FCStd")
    doc.saveAs(branch_file)
    
    print(json.dumps({{
        "success": True,
        "branch": branch_name,
        "file": branch_file,
        "description": "{description}"
    }}))
"""
        return self.bridge.execute_python(code)

    async def compare_versions(
        self,
        version_a: str,
        version_b: str,
        include_parameters: bool = True,
        include_geometry: bool = False,
    ) -> dict:
        """Compare two design versions"""
        code = f"""
import json
import FreeCAD

# Load documents
doc_a = None
doc_b = None

for doc_name in FreeCAD.listDocuments():
    if doc_name == "{version_a}" or doc_name.startswith("{version_a}"):
        doc_a = FreeCAD.getDocument(doc_name)
    if doc_name == "{version_b}" or doc_name.startswith("{version_b}"):
        doc_b = FreeCAD.getDocument(doc_name)

differences = []

if doc_a and doc_b:
    # Compare objects
    objects_a = {{obj.Name: obj for obj in doc_a.Objects}}
    objects_b = {{obj.Name: obj for obj in doc_b.Objects}}
    
    # Find added objects
    for name in objects_b:
        if name not in objects_a:
            differences.append({{
                "type": "added",
                "object": name,
                "in_version": "{version_b}"
            }})
    
    # Find removed objects
    for name in objects_a:
        if name not in objects_b:
            differences.append({{
                "type": "removed",
                "object": name,
                "in_version": "{version_a}"
            }})
    
    # Find modified objects
    for name in objects_a:
        if name in objects_b:
            obj_a = objects_a[name]
            obj_b = objects_b[name]
            
            # Compare properties
            if {include_parameters}:
                for prop in obj_a.PropertiesList:
                    if hasattr(obj_a, prop) and hasattr(obj_b, prop):
                        val_a = getattr(obj_a, prop)
                        val_b = getattr(obj_b, prop)
                        if val_a != val_b:
                            differences.append({{
                                "type": "modified",
                                "object": name,
                                "property": prop,
                                "from": str(val_a),
                                "to": str(val_b)
                            }})

print(json.dumps({{
    "version_a": "{version_a}",
    "version_b": "{version_b}",
    "differences": differences,
    "count": len(differences)
}}))
"""
        return self.bridge.execute_python(code)
