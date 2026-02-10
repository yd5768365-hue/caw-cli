"""ParametricMCP Workbench for FreeCAD"""

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui
import os

# Import bridge server
from . import bridge_server


class ParametricMCPWorkbench(FreeCADGui.Workbench):
    """ParametricMCP Workbench"""

    MenuText = "Parametric MCP"
    ToolTip = "Parametric MCP Integration"
    Icon = ""  # Would add icon path here

    def Initialize(self):
        """Initialize workbench"""
        # Define commands
        self.commands = [
            "ParametricMCP_StartBridge",
            "ParametricMCP_StopBridge",
            "ParametricMCP_Status",
        ]

        # Append to toolbar and menu
        self.appendToolbar("Parametric MCP", self.commands)
        self.appendMenu("Parametric MCP", self.commands)

    def Activated(self):
        """Called when workbench is activated"""
        pass

    def Deactivated(self):
        """Called when workbench is deactivated"""
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


class StartBridgeCommand:
    """Command to start MCP bridge"""

    def GetResources(self):
        return {
            "Pixmap": "",  # Icon path
            "MenuText": "Start MCP Bridge",
            "ToolTip": "Start MCP Bridge Server",
            "CmdType": "ForEdit",
        }

    def Activated(self):
        bridge_server.start_bridge()
        QtGui.QMessageBox.information(
            None, "Parametric MCP", "MCP Bridge started!\\nCheck FreeCAD console for details."
        )

    def IsActive(self):
        return True


class StopBridgeCommand:
    """Command to stop MCP bridge"""

    def GetResources(self):
        return {
            "Pixmap": "",  # Icon path
            "MenuText": "Stop MCP Bridge",
            "ToolTip": "Stop MCP Bridge Server",
            "CmdType": "ForEdit",
        }

    def Activated(self):
        bridge_server.stop_bridge()
        QtGui.QMessageBox.information(None, "Parametric MCP", "MCP Bridge stopped!")

    def IsActive(self):
        return True


class StatusCommand:
    """Command to check bridge status"""

    def GetResources(self):
        return {
            "Pixmap": "",  # Icon path
            "MenuText": "Bridge Status",
            "ToolTip": "Check MCP Bridge Status",
            "CmdType": "ForEdit",
        }

    def Activated(self):
        if bridge_server._bridge_instance and bridge_server._bridge_instance.running:
            QtGui.QMessageBox.information(
                None,
                "Parametric MCP",
                f"Bridge is running on port {bridge_server._bridge_instance.port}",
            )
        else:
            QtGui.QMessageBox.information(None, "Parametric MCP", "Bridge is not running")

    def IsActive(self):
        return True


# Register commands
FreeCADGui.addCommand("ParametricMCP_StartBridge", StartBridgeCommand())
FreeCADGui.addCommand("ParametricMCP_StopBridge", StopBridgeCommand())
FreeCADGui.addCommand("ParametricMCP_Status", StatusCommand())
