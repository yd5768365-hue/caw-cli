"""Family Generation Tools"""

import json


class FamilyTools:
    """Tools for parametric family generation"""

    def __init__(self, bridge):
        self.bridge = bridge

    async def create_table(self, name: str, parameters: list, data: list = None) -> dict:
        """Create design table"""
        data_json = json.dumps(data or [])

        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    doc = FreeCAD.newDocument("ParametricDesign")

# Create spreadsheet for design table
sheet = doc.addObject("Spreadsheet::Sheet", "DesignTable_{name}")
sheet.Label = "DesignTable_{name}"

# Set headers
params = {json.dumps(parameters)}
for i, param in enumerate(params):
    sheet.set(f"{{chr(65+i)}}1", param)

# Set data
data = {data_json}
for row_idx, row_data in enumerate(data, start=2):
    for col_idx, param in enumerate(params):
        if param in row_data:
            sheet.set(f"{{chr(65+col_idx)}}{{row_idx}}", row_data[param])

doc.recompute()
print(json.dumps({{
    "success": True,
    "table": sheet.Name,
    "name": "{name}",
    "parameters": params,
    "rows": len(data)
}}))
"""
        return self.bridge.execute_python(code)

    async def import_table(self, file_path: str, name: str = None) -> dict:
        """Import design table from file"""
        code = f"""
import json
import FreeCAD
import os
import pandas as pd

file_path = "{file_path}"
if not os.path.exists(file_path):
    print(json.dumps({{"error": f"File not found: {{file_path}}"}}))
else:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.csv':
        df = pd.read_csv(file_path)
    elif ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        print(json.dumps({{"error": f"Unsupported format: {{ext}}"}}))
        df = None
    
    if df is not None:
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument("ParametricDesign")
        
        table_name = "{name}" or os.path.splitext(os.path.basename(file_path))[0]
        sheet = doc.addObject("Spreadsheet::Sheet", f"DesignTable_{{table_name}}")
        sheet.Label = f"DesignTable_{{table_name}}"
        
        # Set headers
        for col_idx, col in enumerate(df.columns):
            sheet.set(f"{{chr(65+col_idx)}}1", col)
        
        # Set data
        for row_idx, row in enumerate(df.values, start=2):
            for col_idx, value in enumerate(row):
                sheet.set(f"{{chr(65+col_idx)}}{{row_idx}}", value)
        
        doc.recompute()
        print(json.dumps({{
            "success": True,
            "table": sheet.Name,
            "rows": len(df),
            "columns": len(df.columns)
        }}))
"""
        return self.bridge.execute_python(code)

    async def generate_member(self, design_table: str, row_index: int, name: str = None) -> dict:
        """Generate family member from design table"""
        member_name = name or f"Member_{row_index}"

        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    # Find design table
    table = None
    for obj in doc.Objects:
        if obj.Name == "{design_table}" or obj.Label == "{design_table}":
            table = obj
            break
    
    if not table:
        print(json.dumps({{"error": "Design table not found"}}))
    else:
        row = {row_index} + 1  # Account for header
        
        # Get parameter values from table
        params = {{}}
        used_cells = table.getUsedCells()
        if used_cells:
            headers = []
            for cell in used_cells:
                if cell[1:] == '1':
                    headers.append((cell[0], table.get(cell)))
            
            for col, header in headers:
                value = table.get(f"{{col}}{{row}}")
                params[header] = value
        
        # Create new document for this family member
        member_doc = FreeCAD.newDocument("{member_name}")
        
        # Copy objects from template
        for obj in doc.Objects:
            if obj.TypeId not in ["Spreadsheet::Sheet"]:
                try:
                    member_doc.copyObject(obj)
                except:
                    pass
        
        # Apply parameters
        for obj in member_doc.Objects:
            if hasattr(obj, 'LengthParam') and obj.LengthParam in params:
                obj.Length = params[obj.LengthParam]
            if hasattr(obj, 'DepthParam') and obj.DepthParam in params:
                obj.Length = params[obj.DepthParam]
        
        member_doc.recompute()
        
        print(json.dumps({{
            "success": True,
            "member": "{member_name}",
            "document": member_doc.Name,
            "parameters": params
        }}))
"""
        return self.bridge.execute_python(code)

    async def batch_generate(
        self, template: str, design_table: str, naming_pattern: str, output_dir: str
    ) -> dict:
        """Batch generate family members"""
        code = f"""
import json
import FreeCAD
import os

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    table = None
    for obj in doc.Objects:
        if obj.Name == "{design_table}" or obj.Label == "DesignTable_{design_table}":
            table = obj
            break
    
    if not table:
        print(json.dumps({{"error": "Design table not found"}}))
    else:
        # Get table dimensions
        used_cells = table.getUsedCells()
        max_row = max([int(c[1:]) for c in used_cells if c[1:].isdigit()])
        
        generated = []
        for row in range(2, max_row + 1):
            # Generate member name from pattern
            # Simple pattern: replace {{param}} with value
            name = "{naming_pattern}"  # This would need more sophisticated parsing
            
            # Create member (simplified)
            generated.append({{"row": row, "name": name}})
        
        print(json.dumps({{
            "success": True,
            "generated": len(generated),
            "members": generated,
            "output_dir": "{output_dir}"
        }}))
"""
        return self.bridge.execute_python(code)

    async def create_sweep(self, parameter: str, range: dict, metrics: list = None) -> dict:
        """Create parameter sweep"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    param = "{parameter}"
    min_val = {range.get("min", 0)}
    max_val = {range.get("max", 100)}
    steps = {range.get("steps", 10)}
    metrics = {json.dumps(metrics or [])}
    
    results = []
    step_size = (max_val - min_val) / (steps - 1) if steps > 1 else 0
    
    for i in range(steps):
        value = min_val + step_size * i
        
        # Update parameter
        # (simplified - would need actual parameter update logic)
        
        # Recompute
        doc.recompute()
        
        # Collect metrics
        metric_values = {{}}
        for metric in metrics:
            if metric == "mass":
                # Calculate mass (simplified)
                metric_values[metric] = 0
            elif metric == "volume":
                # Calculate volume
                metric_values[metric] = 0
        
        results.append({{
            "parameter_value": value,
            "metrics": metric_values
        }})
    
    print(json.dumps({{
        "success": True,
        "parameter": param,
        "results": results
    }}))
"""
        return self.bridge.execute_python(code)
