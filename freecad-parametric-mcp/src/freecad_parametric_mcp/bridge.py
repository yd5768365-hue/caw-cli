"""FreeCAD Bridge - 连接 MCP 和 FreeCAD"""

import json
import socket
import threading
import time
import xmlrpc.client
from typing import Any, Optional


class FreeCADBridge:
    """Bridge between MCP server and FreeCAD"""

    def __init__(self, host: str = "localhost", port: int = 9875):
        self.host = host
        self.port = port
        self._proxy: Optional[xmlrpc.client.ServerProxy] = None
        self._connected = False
        self._lock = threading.Lock()

    def connect(self) -> bool:
        """Connect to FreeCAD XML-RPC server"""
        try:
            self._proxy = xmlrpc.client.ServerProxy(
                f"http://{self.host}:{self.port}", allow_none=True
            )
            # Test connection
            self._proxy.ping()
            self._connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to FreeCAD: {e}")
            self._connected = False
            return False

    def ensure_connected(self) -> bool:
        """Ensure connection is active"""
        if not self._connected or self._proxy is None:
            return self.connect()
        try:
            self._proxy.ping()
            return True
        except:
            return self.connect()

    def execute_python(self, code: str) -> dict:
        """Execute Python code in FreeCAD"""
        if not self.ensure_connected():
            raise ConnectionError("Not connected to FreeCAD")

        with self._lock:
            try:
                result = self._proxy.execute_python(code)
                return json.loads(result) if isinstance(result, str) else result
            except Exception as e:
                return {"error": str(e)}

    def get_document(self, name: Optional[str] = None) -> dict:
        """Get document info"""
        if name:
            code = f"""
import json
import FreeCAD
if "{name}" in FreeCAD.listDocuments():
    doc = FreeCAD.getDocument("{name}")
    print(json.dumps({{
        "name": doc.Name,
        "label": doc.Label,
        "filename": doc.FileName if hasattr(doc, 'FileName') else None,
        "objects": [obj.Name for obj in doc.Objects]
    }}))
else:
    print(json.dumps({{"error": "Document not found"}}))
"""
        else:
            code = """
import json
import FreeCAD
doc = FreeCAD.ActiveDocument
if doc:
    print(json.dumps({
        "name": doc.Name,
        "label": doc.Label,
        "filename": doc.FileName if hasattr(doc, 'FileName') else None,
        "objects": [obj.Name for obj in doc.Objects]
    }))
else:
    print(json.dumps({"error": "No active document"}))
"""
        return self.execute_python(code)

    def create_document(self, name: str) -> dict:
        """Create a new document"""
        code = f"""
import json
import FreeCAD
doc = FreeCAD.newDocument("{name}")
print(json.dumps({{"success": True, "name": doc.Name}}))
"""
        return self.execute_python(code)

    def recompute(self, document: Optional[str] = None) -> dict:
        """Recompute document"""
        if document:
            code = f"""
import json
import FreeCAD
doc = FreeCAD.getDocument("{document}")
doc.recompute()
print(json.dumps({{"success": True}}))
"""
        else:
            code = """
import json
import FreeCAD
doc = FreeCAD.ActiveDocument
if doc:
    doc.recompute()
    print(json.dumps({"success": True}))
else:
    print(json.dumps({"error": "No active document"}))
"""
        return self.execute_python(code)

    def get_parameter_groups(self) -> dict:
        """Get all parameter groups from FreeCAD"""
        code = """
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({"error": "No active document"}))
else:
    groups = {}
    # FreeCAD uses PropertyBags or custom properties for parameters
    # This is a simplified version
    for obj in doc.Objects:
        if hasattr(obj, 'Group'):
            for prop in obj.PropertiesList:
                if not prop.startswith('__'):
                    groups.setdefault(obj.Label, {})[prop] = getattr(obj, prop)
    print(json.dumps(groups))
"""
        return self.execute_python(code)

    def set_property(self, obj_name: str, prop_name: str, value: Any) -> dict:
        """Set object property"""
        code = f"""
import json
import FreeCAD

doc = FreeCAD.ActiveDocument
if not doc:
    print(json.dumps({{"error": "No active document"}}))
else:
    obj = doc.getObject("{obj_name}")
    if obj:
        setattr(obj, "{prop_name}", {repr(value)})
        print(json.dumps({{"success": True}}))
    else:
        print(json.dumps({{"error": "Object not found"}}))
"""
        return self.execute_python(code)

    def ping(self) -> bool:
        """Check if FreeCAD is responsive"""
        try:
            if self._proxy:
                self._proxy.ping()
                return True
        except:
            pass
        return False
