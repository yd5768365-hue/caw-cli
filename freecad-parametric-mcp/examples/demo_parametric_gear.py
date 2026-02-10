"""
Example: Parametric Gear Design
Demonstrates perfect parametric modeling with MCP
"""

import asyncio


async def create_parametric_gear():
    """Create a fully parametric spur gear"""

    # This would be called through MCP
    commands = [
        # 1. Create parameter group
        {
            "tool": "create_parameter_group",
            "params": {"name": "gear_design", "description": "Spur gear design parameters"},
        },
        # 2. Add base parameters
        {
            "tool": "add_parameter",
            "params": {
                "group": "gear_design",
                "name": "module",
                "value": 2.0,
                "unit": "mm",
                "min_value": 0.5,
                "max_value": 10.0,
                "description": "Gear module - determines tooth size",
            },
        },
        {
            "tool": "add_parameter",
            "params": {
                "group": "gear_design",
                "name": "teeth_count",
                "value": 24,
                "unit": "count",
                "min_value": 12,
                "max_value": 100,
                "description": "Number of teeth",
            },
        },
        {
            "tool": "add_parameter",
            "params": {
                "group": "gear_design",
                "name": "face_width",
                "value": 15.0,
                "unit": "mm",
                "description": "Width of gear teeth",
            },
        },
        {
            "tool": "add_parameter",
            "params": {
                "group": "gear_design",
                "name": "pressure_angle",
                "value": 20.0,
                "unit": "deg",
                "description": "Pressure angle in degrees",
            },
        },
        {
            "tool": "add_parameter",
            "params": {
                "group": "gear_design",
                "name": "bore_diameter",
                "value": 20.0,
                "unit": "mm",
                "description": "Shaft bore diameter",
            },
        },
        # 3. Add formula-driven parameters
        {
            "tool": "add_parameter",
            "params": {
                "group": "gear_design",
                "name": "pitch_diameter",
                "formula": "module * teeth_count",
                "unit": "mm",
                "description": "Pitch circle diameter",
            },
        },
        {
            "tool": "add_parameter",
            "params": {
                "group": "gear_design",
                "name": "outer_diameter",
                "formula": "pitch_diameter + 2 * module",
                "unit": "mm",
                "description": "Outer diameter (tip)",
            },
        },
        {
            "tool": "add_parameter",
            "params": {
                "group": "gear_design",
                "name": "root_diameter",
                "formula": "pitch_diameter - 2.5 * module",
                "unit": "mm",
                "description": "Root diameter (dedendum)",
            },
        },
        # 4. Create parametric sketch
        {
            "tool": "create_parametric_sketch",
            "params": {
                "name": "Gear_Profile",
                "plane": "XY",
                "parameters": {
                    "pitch_dia": "gear_design.pitch_diameter",
                    "outer_dia": "gear_design.outer_diameter",
                    "root_dia": "gear_design.root_diameter",
                },
            },
        },
        # 5. Add construction geometry
        {
            "tool": "add_constrained_circle",
            "params": {
                "sketch": "Gear_Profile",
                "center": {"x": 0, "y": 0},
                "radius": "pitch_diameter / 2",
                "construction": True,
            },
        },
        {
            "tool": "add_constrained_circle",
            "params": {
                "sketch": "Gear_Profile",
                "center": {"x": 0, "y": 0},
                "radius": "outer_diameter / 2",
                "construction": True,
            },
        },
        # 6. Add center bore
        {
            "tool": "add_constrained_circle",
            "params": {
                "sketch": "Gear_Profile",
                "center": {"x": 0, "y": 0},
                "radius": "bore_diameter / 2",
                "construction": False,
            },
        },
        # 7. Auto-constrain sketch
        {
            "tool": "auto_constrain_sketch",
            "params": {"sketch": "Gear_Profile", "strategy": "full", "detect_symmetry": True},
        },
        # 8. Analyze sketch
        {"tool": "analyze_sketch_dof", "params": {"sketch": "Gear_Profile", "detailed": True}},
        # 9. Create extrusion
        {
            "tool": "create_parametric_pad",
            "params": {
                "sketch": "Gear_Profile",
                "length_param": "face_width",
                "direction": "forward",
                "name": "Gear_Body",
            },
        },
        # 10. Validate parameters
        {
            "tool": "validate_parameters",
            "params": {"check_constraints": True, "check_circularity": True},
        },
    ]

    print("Parametric gear design workflow prepared!")
    print(f"Total steps: {len(commands)}")
    print("\nKey features:")
    print("- Formula-driven parameters (pitch_dia, outer_dia, root_dia)")
    print("- Constraint validation")
    print("- Automatic sketch constraint")
    print("- Parameter ranges for validation")

    return commands


async def create_parameter_family():
    """Create a family of gears with different sizes"""

    design_table = {
        "tool": "create_design_table",
        "params": {
            "name": "Gear_Family",
            "parameters": ["module", "teeth_count", "face_width", "bore_diameter"],
            "data": [
                {"module": 1.0, "teeth_count": 20, "face_width": 10, "bore_diameter": 10},
                {"module": 1.5, "teeth_count": 24, "face_width": 15, "bore_diameter": 15},
                {"module": 2.0, "teeth_count": 30, "face_width": 20, "bore_diameter": 20},
                {"module": 2.5, "teeth_count": 36, "face_width": 25, "bore_diameter": 25},
                {"module": 3.0, "teeth_count": 40, "face_width": 30, "bore_diameter": 30},
            ],
        },
    }

    batch_generate = {
        "tool": "batch_generate_family",
        "params": {
            "template": "gear_template",
            "design_table": "Gear_Family",
            "naming_pattern": "Gear_M{module}_Z{teeth_count}",
            "output_dir": "./gear_family/",
        },
    }

    print("Gear family generation workflow:")
    print("- 5 variants with different modules and sizes")
    print("- Automatic naming: Gear_M{module}_Z{teeth_count}")
    print("- Output to ./gear_family/")

    return [design_table, batch_generate]


async def analyze_design():
    """Analyze gear design sensitivity"""

    analysis = {
        "tool": "analyze_parameter_sensitivity",
        "params": {
            "target_parameter": "module",
            "target_metric": "mass",
            "range": {"min": 1.0, "max": 5.0, "steps": 20},
            "output": "module_sensitivity.json",
        },
    }

    report = {
        "tool": "generate_parameter_report",
        "params": {
            "report_type": "full",
            "parameters": ["module", "teeth_count", "face_width", "pitch_diameter"],
            "include_charts": True,
            "output": "gear_design_report.pdf",
        },
    }

    print("Design analysis workflow:")
    print("- Sensitivity analysis on module parameter")
    print("- Mass calculation across 20 steps")
    print("- Full parameter report with charts")

    return [analysis, report]


if __name__ == "__main__":
    print("=" * 60)
    print("FreeCAD Parametric MCP - Example Workflows")
    print("=" * 60)

    print("\n1. PARAMETRIC GEAR DESIGN")
    print("-" * 40)
    asyncio.run(create_parametric_gear())

    print("\n2. PARAMETER FAMILY GENERATION")
    print("-" * 40)
    asyncio.run(create_parameter_family())

    print("\n3. DESIGN ANALYSIS")
    print("-" * 40)
    asyncio.run(analyze_design())

    print("\n" + "=" * 60)
    print("These workflows demonstrate:")
    print("  ✓ Formula-driven parameters")
    print("  ✓ Constraint management")
    print("  ✓ Design table / Parameter families")
    print("  ✓ Sensitivity analysis")
    print("  ✓ Automated reporting")
    print("=" * 60)
