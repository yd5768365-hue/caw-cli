from integrations.mesher.gmsh import GmshConnector
from pathlib import Path

gmsh = GmshConnector()
gmsh.connect()
try:
      success = gmsh.generate_mesh(
          geometry_file=Path("model.step"),
          mesh_file=Path("model.msh"),
          element_size=2.0
      )
      if success:
          print("网格生成成功")
      else:
          print("网格生成失败")
except Exception as e:
      print(f"发生异常: {e}")