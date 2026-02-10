"""ParametricMCP FreeCAD Workbench - Initialization"""

import FreeCAD
import FreeCADGui

# This file is executed when FreeCAD starts
FreeCAD.Console.PrintMessage("Loading ParametricMCP workbench...\\n")

# Import the workbench
from . import ParametricMCPWorkbench
