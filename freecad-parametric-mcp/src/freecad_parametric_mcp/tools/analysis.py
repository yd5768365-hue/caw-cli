"""Analysis Tools"""

import json


class AnalysisTools:
    """Tools for design analysis"""

    def __init__(self, bridge):
        self.bridge = bridge

    async def analyze_sensitivity(
        self, target_parameter: str, target_metric: str, range: dict, output: str = None
    ) -> dict:
        """Analyze parameter sensitivity"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    param = "{target_parameter}"
    metric = "{target_metric}"
    min_val = {range.get("min", 0)}
    max_val = {range.get("max", 100)}
    steps = {range.get("steps", 10)}
    
    # Perform parameter sweep
    results = []
    baseline_value = None
    
    step_size = (max_val - min_val) / (steps - 1) if steps > 1 else 0
    
    for i in range(steps):
        value = min_val + step_size * i
        
        # Update parameter value
        # (In real implementation, would update the actual parameter)
        
        # Recompute
        doc.recompute()
        
        # Calculate metric
        metric_value = 0
        if metric == "mass":
            # Calculate mass of all solids
            for obj in doc.Objects:
                if hasattr(obj, 'Shape') and hasattr(obj.Shape, 'Volume'):
                    # Assuming density of 1 for simplicity
                    metric_value += obj.Shape.Volume * 0.001  # Convert to mass
        elif metric == "volume":
            for obj in doc.Objects:
                if hasattr(obj, 'Shape') and hasattr(obj.Shape, 'Volume'):
                    metric_value += obj.Shape.Volume
        
        if i == 0:
            baseline_value = metric_value
        
        results.append({{
            "parameter_value": value,
            "metric_value": metric_value,
            "change_percent": ((metric_value - baseline_value) / baseline_value * 100) if baseline_value else 0
        }})
    
    result = {{
        "parameter": param,
        "metric": metric,
        "range": {{"min": min_val, "max": max_val}},
        "steps": steps,
        "results": results,
        "sensitivity": abs(results[-1]["metric_value"] - results[0]["metric_value"]) if len(results) > 1 else 0
    }}
    
    # Save to file if specified
    output_file = "{output or ""}"
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    print(json.dumps(result))
"""
        return self.bridge.execute_python(code)

    async def check_rules(self, ruleset: str = "default", auto_fix: bool = False) -> dict:
        """Check design rules"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    ruleset = "{ruleset}"
    auto_fix = {auto_fix}
    
    violations = []
    warnings = []
    
    # Define rules based on ruleset
    if ruleset == "mechanical_design":
        rules = [
            {{"name": "minimum_wall_thickness", "min": 1.0, "message": "Wall thickness should be at least 1mm"}},
            {{"name": "hole_spacing", "min": 3.0, "message": "Hole edge distance should be at least 3mm"}},
        ]
    else:
        rules = []
    
    # Check each object
    for obj in doc.Objects:
        if hasattr(obj, 'Shape'):
            # Check for small features
            if hasattr(obj.Shape, 'Area') and obj.Shape.Area < 0.01:
                warnings.append({{
                    "object": obj.Name,
                    "rule": "small_feature",
                    "message": f"Object {{obj.Label}} has very small area"
                }})
            
            # Check for invalid shapes
            if hasattr(obj, 'State') and 'Invalid' in obj.State:
                violations.append({{
                    "object": obj.Name,
                    "rule": "invalid_geometry",
                    "message": f"Object {{obj.Label}} has invalid geometry",
                    "severity": "error"
                }})
    
    print(json.dumps({{
        "valid": len(violations) == 0,
        "violations": violations,
        "warnings": warnings,
        "ruleset": ruleset
    }}))
"""
        return self.bridge.execute_python(code)

    async def generate_report(
        self, report_type: str, output: str, parameters: list = None, include_charts: bool = True
    ) -> dict:
        """Generate parameter report"""
        params_filter = json.dumps(parameters or [])

        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    report = {{
        "type": "{report_type}",
        "document": doc.Name,
        "generated": str(datetime.now()),
        "include_charts": {include_charts}
    }}
    
    # Collect parameter info
    param_filter = {params_filter}
    parameters_info = []
    
    # Get parameters from spreadsheet
    for obj in doc.Objects:
        if obj.Label == "_Parameters_":
            # Parse parameter sheet
            for row in range(2, 1000):
                try:
                    group = obj.get(f"A{{row}}")
                    if not group:
                        break
                    
                    name = obj.get(f"B{{row}}")
                    if param_filter and name not in param_filter:
                        continue
                    
                    param_info = {{
                        "group": group,
                        "name": name,
                        "value": obj.get(f"C{{row}}"),
                        "unit": obj.get(f"D{{row}}"),
                        "formula": obj.get(f"E{{row}}"),
                        "description": obj.get(f"H{{row}}")
                    }}
                    parameters_info.append(param_info)
                except:
                    break
    
    report["parameters"] = parameters_info
    
    # Calculate statistics
    if parameters_info:
        values = [p["value"] for p in parameters_info if isinstance(p["value"], (int, float))]
        if values:
            report["statistics"] = {{
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values)
            }}
    
    # Save report
    output_file = "{output}"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps({{
        "success": True,
        "file": output_file,
        "parameters_count": len(parameters_info)
    }}))
"""
        return self.bridge.execute_python(code)
