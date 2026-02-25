"""
材料查询页面

此模块提供材料数据库查询功能的GUI界面。
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QGroupBox,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Signal

from ..theme import CAETheme


class MaterialPage(QWidget):
    """材料查询页面类"""

    # 信号：查询完成
    query_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("材料数据库查询")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 查询区域
        search_group = QGroupBox("材料查询")
        search_layout = QHBoxLayout()

        # 材料名称输入
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("输入材料名称（如 Q235、45钢）")
        self.material_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.material_input)

        # 查询按钮
        search_btn = QPushButton("查询")
        search_btn.setProperty("primary", True)
        search_btn.clicked.connect(self._on_search)
        search_layout.addWidget(search_btn)

        # 列出全部按钮
        list_btn = QPushButton("列出全部")
        list_btn.clicked.connect(self._on_list_all)
        search_layout.addWidget(list_btn)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # 材料列表
        list_group = QGroupBox("材料列表")
        list_layout = QVBoxLayout()

        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(3)
        self.materials_table.setHorizontalHeaderLabels(["名称", "类型", "标准"])
        self.materials_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.materials_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.materials_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.materials_table.itemDoubleClicked.connect(self._on_select_material)
        list_layout.addWidget(self.materials_table)

        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # 材料详情
        detail_group = QGroupBox("材料详情")
        detail_layout = QVBoxLayout()

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setPlaceholderText("双击材料列表中的项目查看详情...")
        detail_layout.addWidget(self.detail_text)

        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)

    def _on_search(self):
        """搜索材料"""
        material_name = self.material_input.text().strip()

        if not material_name:
            self.detail_text.setText("请输入材料名称")
            return

        try:
            from sw_helper.material.database import MaterialDatabase

            db = MaterialDatabase()
            # 尝试直接获取
            material = db.get_material(material_name)

            if material:
                self._display_material_detail(material)
            else:
                # 尝试搜索
                results = db.search_materials(material_name)
                if results:
                    self._display_search_results(results)
                else:
                    self.detail_text.setText(f"未找到材料: {material_name}")
        except Exception as e:
            self.detail_text.setText(f"查询失败: {e}")

    def _on_list_all(self):
        """列出全部材料"""
        try:
            from sw_helper.material.database import MaterialDatabase

            db = MaterialDatabase()
            materials = db.list_materials()

            self.materials_table.setRowCount(len(materials))
            for i, name in enumerate(materials):
                mat = db.get_material(name)
                if mat:
                    self.materials_table.setItem(
                        i, 0, QTableWidgetItem(mat.get("name", name))
                    )
                    self.materials_table.setItem(
                        i, 1, QTableWidgetItem(mat.get("type", ""))
                    )
                    self.materials_table.setItem(
                        i, 2, QTableWidgetItem(mat.get("standard", ""))
                    )

            self.detail_text.setText(f"已加载全部材料（共 {len(materials)} 种）")
        except Exception as e:
            self.detail_text.setText(f"加载失败: {e}")

    def _on_select_material(self, item):
        """选择材料"""
        row = item.row()
        material_name = self.materials_table.item(row, 0).text()

        try:
            from sw_helper.material.database import MaterialDatabase

            db = MaterialDatabase()
            material = db.get_material(material_name)

            if material:
                self._display_material_detail(material)
            else:
                self.detail_text.setText(f"未找到材料详情: {material_name}")
        except Exception as e:
            self.detail_text.setText(f"加载失败: {e}")

    def _display_material_detail(self, material: dict):
        """显示材料详情"""
        lines = [
            f"【{material.get('name', 'N/A')}】",
            f"类型: {material.get('type', 'N/A')}",
            f"标准: {material.get('standard', 'N/A')}",
            "",
            "--- 力学性能 ---",
        ]

        # 力学性能
        props = [
            ("密度", "density", "kg/m³"),
            ("弹性模量", "elastic_modulus", "GPa"),
            ("泊松比", "poisson_ratio", ""),
            ("屈服强度", "yield_strength", "MPa"),
            ("抗拉强度", "tensile_strength", "MPa"),
            ("伸长率", "elongation", "%"),
        ]

        for label, key, unit in props:
            if key in material:
                value = material[key]
                if key in ("elastic_modulus", "yield_strength", "tensile_strength"):
                    value = value / 1e6  # 转换为MPa
                if unit:
                    lines.append(f"{label}: {value} {unit}")
                else:
                    lines.append(f"{label}: {value}")

        self.detail_text.setText("\n".join(lines))

    def _display_search_results(self, results: list):
        """显示搜索结果"""
        self.materials_table.setRowCount(len(results))
        for i, mat in enumerate(results):
            self.materials_table.setItem(
                i, 0, QTableWidgetItem(mat.get("name", ""))
            )
            self.materials_table.setItem(
                i, 1, QTableWidgetItem(mat.get("type", ""))
            )
            self.materials_table.setItem(
                i, 2, QTableWidgetItem(mat.get("standard", ""))
            )

        self.detail_text.setText(f"找到 {len(results)} 个结果")


# 页面工厂函数
def create_material_page() -> MaterialPage:
    """创建材料查询页面

    Returns:
        MaterialPage: 材料查询页面对象
    """
    return MaterialPage()
