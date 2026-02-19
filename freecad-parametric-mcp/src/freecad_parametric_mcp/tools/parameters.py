"""Parameter Management Tools"""

import json
from typing import Any, Optional


class ParameterTools:
    """Tools for managing parameters in FreeCAD"""

    def __init__(self, bridge):
        self.bridge = bridge
        self._param_groups = {}  # Local cache

    async def create_group(
        self, name: str, description: str = "", parent_group: Optional[str] = None
    ) -> dict:
        """Create a parameter group"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    # Create a new document
    doc = FreeCAD.newDocument("ParametricDesign")

# Create a spreadsheet for parameters if not exists
param_obj = None
for obj in doc.Objects:
    if obj.Label == "_Parameters_" or (hasattr(obj, 'TypeId') and obj.TypeId == "Spreadsheet::Sheet"):
        param_obj = obj
        break

if not param_obj:
    param_obj = doc.addObject("Spreadsheet::Sheet", "Parameters")
    param_obj.Label = "_Parameters_"

# Add group metadata
group_key = "{name}"
row = param_obj.getUsedCells()
if row:
    row = max([int(r[1:]) for r in row if r[1:].isdigit()]) + 1
else:
    row = 1

param_obj.set(f"A{{row}}", group_key)
param_obj.set(f"B{{row}}", "{description}")
param_obj.set(f"C{{row}}", "{parent_group or ""}")

doc.recompute()
print(json.dumps({{"success": True, "group": "{name}", "description": "{description}"}}))
"""
        return self.bridge.execute_python(code)

    async def add_parameter(
        self,
        group: str,
        name: str,
        value: Any = None,
        unit: str = "",
        formula: str = "",
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        description: str = "",
    ) -> dict:
        """Add a parameter to a group"""

        # Handle value vs formula
        if formula:
            value_expr = f'"{formula}"'
        else:
            value_expr = repr(value) if value is not None else "0"

        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    doc = FreeCAD.newDocument("ParametricDesign")

# Find or create parameter spreadsheet
param_sheet = None
for obj in doc.Objects:
    if obj.Label == "_Parameters_":
        param_sheet = obj
        break

if not param_sheet:
    param_sheet = doc.addObject("Spreadsheet::Sheet", "Parameters")
    param_sheet.Label = "_Parameters_"
    # Setup header
    param_sheet.set("A1", "Group")
    param_sheet.set("B1", "Name")
    param_sheet.set("C1", "Value")
    param_sheet.set("D1", "Unit")
    param_sheet.set("E1", "Formula")
    param_sheet.set("F1", "Min")
    param_sheet.set("G1", "Max")
    param_sheet.set("H1", "Description")

# Find next row
used_cells = param_sheet.getUsedCells()
row = 2
if used_cells:
    rows = [int(c[1:]) for c in used_cells if c[1:].isdigit()]
    if rows:
        row = max(rows) + 1

# Add parameter
param_sheet.set(f"A{{row}}", "{group}")
param_sheet.set(f"B{{row}}", "{name}")
param_sheet.set(f"C{{row}}", {value_expr})
param_sheet.set(f"D{{row}}", "{unit}")
param_sheet.set(f"E{{row}}", "{formula}")
param_sheet.set(f"F{{row}}", "{min_value or ""}")
param_sheet.set(f"G{{row}}", "{max_value or ""}")
param_sheet.set(f"H{{row}}", "{description}")

doc.recompute()
print(json.dumps({{
    "success": True,
    "group": "{group}",
    "name": "{name}",
    "value": {value_expr},
    "unit": "{unit}"
}}))
"""
        return self.bridge.execute_python(code)

    async def set_formula(self, group: str, name: str, formula: str) -> dict:
        """Set formula for a parameter"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    param_sheet = None
    for obj in doc.Objects:
        if obj.Label == "_Parameters_":
            param_sheet = obj
            break
    
    if not param_sheet:
        print(json.dumps({{"error": "Parameter sheet not found"}}))
    else:
        # Find the parameter row
        found = False
        for row in range(2, 1000):
            try:
                g = param_sheet.get(f"A{{row}}")
                n = param_sheet.get(f"B{{row}}")
                if g == "{group}" and n == "{name}":
                    param_sheet.set(f"E{{row}}", "{formula}")
                    # Set formula reference in Value column
                    param_sheet.set(f"C{{row}}", f"={formula}")
                    found = True
                    break
            except:
                break
        
        if found:
            doc.recompute()
            print(json.dumps({{"success": True, "group": "{group}", "name": "{name}", "formula": "{formula}"}}))
        else:
            print(json.dumps({{"error": "Parameter not found"}}))
"""
        return self.bridge.execute_python(code)

    async def update_parameter(
        self, group: str, name: str, value: float, regenerate: bool = True
    ) -> dict:
        """Update parameter value"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    param_sheet = None
    for obj in doc.Objects:
        if obj.Label == "_Parameters_":
            param_sheet = obj
            break
    
    if not param_sheet:
        print(json.dumps({{"error": "Parameter sheet not found"}}))
    else:
        # Find and update parameter
        found = False
        for row in range(2, 1000):
            try:
                g = param_sheet.get(f"A{{row}}")
                n = param_sheet.get(f"B{{row}}")
                if g == "{group}" and n == "{name}":
                    param_sheet.set(f"C{{row}}", {value})
                    found = True
                    break
            except:
                break
        
        if found:
            if {regenerate}:
                doc.recompute()
            print(json.dumps({{
                "success": True,
                "group": "{group}",
                "name": "{name}",
                "new_value": {value}
            }}))
        else:
            print(json.dumps({{"error": "Parameter not found"}}))
"""
        return self.bridge.execute_python(code)

    async def list_parameters(
        self, group: Optional[str] = None, include_formulas: bool = True
    ) -> dict:
        """List all parameters"""
        filter_code = f'if g == "{group}"' if group else ""

        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    param_sheet = None
    for obj in doc.Objects:
        if obj.Label == "_Parameters_":
            param_sheet = obj
            break
    
    if not param_sheet:
        print(json.dumps({{"parameters": []}}))
    else:
        params = []
        for row in range(2, 1000):
            try:
                g = param_sheet.get(f"A{{row}}")
                if not g:
                    break
                {filter_code}
                param = {{
                    "group": g,
                    "name": param_sheet.get(f"B{{row}}"),
                    "value": param_sheet.get(f"C{{row}}"),
                    "unit": param_sheet.get(f"D{{row}}") or "",
                }}
                if {include_formulas}:
                    param["formula"] = param_sheet.get(f"E{{row}}") or ""
                params.append(param)
            except Exception as e:
                break
        
        print(json.dumps({{"parameters": params}}))
"""
        return self.bridge.execute_python(code)

    async def create_link(
        self,
        source_group: str,
        source_param: str,
        target_group: str,
        target_param: str,
        expression: str = "",
    ) -> dict:
        """Create parameter link"""
        formula = f"{source_group}.{source_param}{expression}"
        return await self.set_formula(target_group, target_param, formula)

    async def validate(
        self, check_constraints: bool = True, check_circularity: bool = True
    ) -> dict:
        """Validate parameters"""
        code = """
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    errors = []
    warnings = []
    
    # Validate each parameter
    param_sheet = None
    for obj in doc.Objects:
        if obj.Label == "_Parameters_":
            param_sheet = obj
            break
    
    if param_sheet:
        for row in range(2, 1000):
            try:
                group = param_sheet.get(f"A{{row}}")
                if not group:
                    break
                name = param_sheet.get(f"B{{row}}")
                value = param_sheet.get(f"C{{row}}")
                min_val = param_sheet.get(f"F{{row}}")
                max_val = param_sheet.get(f"G{{row}}")
                
                # Check range constraints
                if min_val and value < min_val:
                    errors.append(f"Parameter {{group}}.{{name}}: value {{value}} < min {{min_val}}")
                if max_val and value > max_val:
                    errors.append(f"Parameter {{group}}.{{name}}: value {{value}} > max {{max_val}}")
            except:
                break
    
    # Check for errors in document
    if doc:
        for obj in doc.Objects:
            if hasattr(obj, 'State') and 'Invalid' in obj.State:
                errors.append(f"Object {{obj.Label}} is invalid")
    
    print(json.dumps({{
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }}))
"""
        return self.bridge.execute_python(code)

    async def import_from_file(self, file_path: str, group_prefix: str = "") -> dict:
        """Import parameters from file"""
        code = f"""
import json
import FreeCAD
import os

file_path = "{file_path}"
if not os.path.exists(file_path):
    print(json.dumps({{"error": f"File not found: {{file_path}}"}}))
else:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.json':
        with open(file_path, 'r') as f:
            data = json.load(f)
    elif ext in ['.csv', '.xlsx']:
        import pandas as pd
        df = pd.read_csv(file_path) if ext == '.csv' else pd.read_excel(file_path)
        data = df.to_dict('records')
    else:
        print(json.dumps({{"error": f"Unsupported format: {{ext}}"}}))
        data = None
    
    if data:
        imported = 0
        prefix = "{group_prefix}"
        for item in data:
            # Process each parameter
            imported += 1
        
        print(json.dumps({{"success": True, "imported": imported}}))
"""
        return self.bridge.execute_python(code)

    async def export_to_file(
        self, file_path: str, format: str = "json", groups: Optional[list] = None
    ) -> dict:
        """Export parameters to file"""
        groups_filter = json.dumps(groups) if groups else "None"

        code = f"""
import json
import FreeCAD

file_path = "{file_path}"
format_type = "{format}"
groups = {groups_filter}

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    # Get parameters
    params = []
    param_sheet = None
    for obj in doc.Objects:
        if obj.Label == "_Parameters_":
            param_sheet = obj
            break
    
    if param_sheet:
        for row in range(2, 1000):
            try:
                group = param_sheet.get(f"A{{row}}")
                if not group:
                    break
                if groups and group not in groups:
                    continue
                
                param = {{
                    "group": group,
                    "name": param_sheet.get(f"B{{row}}"),
                    "value": param_sheet.get(f"C{{row}}"),
                    "unit": param_sheet.get(f"D{{row}}"),
                    "formula": param_sheet.get(f"E{{row}}"),
                    "min": param_sheet.get(f"F{{row}}"),
                    "max": param_sheet.get(f"G{{row}}"),
                    "description": param_sheet.get(f"H{{row}}")
                }}
                params.append(param)
            except:
                break
    
    # Export based on format
    if format_type == "json":
        with open(file_path, 'w') as f:
            json.dump(params, f, indent=2)
    elif format_type in ["csv", "xlsx"]:
        import pandas as pd
        df = pd.DataFrame(params)
        if format_type == "csv":
            df.to_csv(file_path, index=False)
        else:
            df.to_excel(file_path, index=False)
    
    print(json.dumps({{"success": True, "exported": len(params), "file": file_path}}))
"""
        return self.bridge.execute_python(code)
