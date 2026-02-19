"""ParametricMCP FreeCAD Workbench - Bridge Server"""

import FreeCAD
import FreeCADGui
import xmlrpc.server
import threading
import json
import socket


class FreeCADBridgeServer:
    """XML-RPC server running inside FreeCAD"""

    def __init__(self, host="localhost", port=9875):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False

    def start(self):
        """Start the bridge server in a separate thread"""
        if self.running:
            FreeCAD.Console.PrintMessage("Bridge server already running\\n")
            return

        try:
            self.server = xmlrpc.server.SimpleXMLRPCServer(
                (self.host, self.port), allow_none=True, logRequests=False
            )
            self.server.register_instance(self)
            self.server.register_introspection_functions()

            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()

            self.running = True
            FreeCAD.Console.PrintMessage(f"\\n" + "=" * 60 + "\\n")
            FreeCAD.Console.PrintMessage("MCP Bridge started!\\n")
            FreeCAD.Console.PrintMessage(f"  - XML-RPC: {self.host}:{self.port}\\n")
            FreeCAD.Console.PrintMessage("=" * 60 + "\\n\\n")

        except Exception as e:
            FreeCAD.Console.PrintError(f"Failed to start bridge: {e}\\n")

    def stop(self):
        """Stop the bridge server"""
        if self.server:
            self.server.shutdown()
            self.running = False
            FreeCAD.Console.PrintMessage("Bridge server stopped\\n")

    def ping(self):
        """Health check"""
        return {"status": "ok", "freecad_version": FreeCAD.Version()}

    def execute_python(self, code):
        """Execute Python code in FreeCAD context"""
        import sys
        from io import StringIO

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        try:
            # Execute in FreeCAD context
            exec(code, {"FreeCAD": FreeCAD, "FreeCADGui": FreeCADGui, "json": json})
            output = mystdout.getvalue()
            return output if output else "{}"
        except Exception as e:
            return json.dumps({"error": str(e)})
        finally:
            sys.stdout = old_stdout

    def get_active_document(self):
        """Get active document info"""
        doc = FreeCAD.ActiveDocument
        if not doc:
            return None
        return {
            "name": doc.Name,
            "label": doc.Label,
            "filename": doc.FileName if hasattr(doc, "FileName") else None,
            "object_count": len(doc.Objects),
        }

    def list_documents(self):
        """List all open documents"""
        return [
            {"name": name, "label": FreeCAD.getDocument(name).Label}
            for name in FreeCAD.listDocuments()
        ]

    def recompute_document(self, doc_name=None):
        """Recompute document"""
        if doc_name:
            doc = FreeCAD.getDocument(doc_name)
        else:
            doc = FreeCAD.ActiveDocument

        if doc:
            doc.recompute()
            return {"success": True}
        return {"error": "No document"}


# Global instance
_bridge_instance = None


def start_bridge():
    """Start the bridge server"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = FreeCADBridgeServer()
    _bridge_instance.start()
    return _bridge_instance


def stop_bridge():
    """Stop the bridge server"""
    global _bridge_instance
    if _bridge_instance:
        _bridge_instance.stop()
        _bridge_instance = None


# Auto-start when FreeCAD loads
# Uncomment the next line to auto-start:
# start_bridge()
