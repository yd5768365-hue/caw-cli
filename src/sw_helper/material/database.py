"""
材料数据库模块 - GB/T标准材料库
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List


def get_resource_path(relative_path: str) -> Path:
    """获取资源文件路径，支持打包后的exe和开发模式"""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent.parent.parent
    return base_path / relative_path


class MaterialDatabase:
    """材料数据库管理器"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = get_resource_path("data/materials.json")

        self.db_path = Path(db_path)
        self.materials = {}
        self._load_database()

    def _load_database(self):
        """加载材料数据库"""
        if self.db_path.exists():
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.materials = json.load(f)
        else:
            # 创建默认数据库
            self._create_default_database()

    def _create_default_database(self):
        """创建默认材料数据库"""
        self.materials = {
            "Q235": {
                "name": "Q235",
                "standard": "GB/T 700",
                "type": "碳素结构钢",
                "density": 7850,  # kg/m³
                "elastic_modulus": 210e9,  # Pa
                "poisson_ratio": 0.3,
                "yield_strength": 235e6,  # Pa
                "tensile_strength": 375e6,  # Pa
                "thermal_expansion": 1.2e-5,  # 1/K
                "description": "通用结构钢",
            },
            "Q345": {
                "name": "Q345",
                "standard": "GB/T 1591",
                "type": "低合金高强度钢",
                "density": 7850,
                "elastic_modulus": 210e9,
                "poisson_ratio": 0.3,
                "yield_strength": 345e6,
                "tensile_strength": 470e6,
                "thermal_expansion": 1.2e-5,
                "description": "低合金高强度结构钢",
            },
            "45钢": {
                "name": "45钢",
                "standard": "GB/T 699",
                "type": "优质碳素结构钢",
                "density": 7850,
                "elastic_modulus": 210e9,
                "poisson_ratio": 0.3,
                "yield_strength": 355e6,
                "tensile_strength": 600e6,
                "thermal_expansion": 1.1e-5,
                "description": "常用机械零件材料",
            },
            "铝合金6061": {
                "name": "铝合金6061",
                "standard": "GB/T 3190",
                "type": "铝合金",
                "density": 2700,
                "elastic_modulus": 69e9,
                "poisson_ratio": 0.33,
                "yield_strength": 276e6,
                "tensile_strength": 310e6,
                "thermal_expansion": 2.3e-5,
                "description": "航空铝合金",
            },
            "不锈钢304": {
                "name": "不锈钢304",
                "standard": "GB/T 20878",
                "type": "奥氏体不锈钢",
                "density": 8000,
                "elastic_modulus": 193e9,
                "poisson_ratio": 0.29,
                "yield_strength": 215e6,
                "tensile_strength": 520e6,
                "thermal_expansion": 1.7e-5,
                "description": "耐腐蚀不锈钢",
            },
        }
        self.save_database()

    def save_database(self):
        """保存数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.materials, f, indent=2, ensure_ascii=False)

    def get_material(self, name: str) -> Optional[Dict[str, Any]]:
        """获取材料信息"""
        return self.materials.get(name)

    def search_materials(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索材料"""
        results = []
        for name, data in self.materials.items():
            if (
                keyword.lower() in name.lower()
                or keyword.lower() in data.get("description", "").lower()
            ):
                results.append(data)
        return results

    def add_material(self, name: str, properties: Dict[str, Any]):
        """添加新材料"""
        self.materials[name] = properties
        self.save_database()

    def list_materials(self) -> List[str]:
        """列出所有材料名称"""
        return list(self.materials.keys())
