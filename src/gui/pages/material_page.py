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

        # TODO: 调用 sw_helper.material 进行查询
        self.detail_text.setText(f"正在查询材料: {material_name}\n\n[功能开发中...]")

    def _on_list_all(self):
        """列出全部材料"""
        # TODO: 调用 sw_helper.material 获取材料列表
        # 暂时显示示例数据
        sample_materials = [
            ("Q235", "碳素结构钢", "GB/T 700"),
            ("Q345", "低合金高强度钢", "GB/T 1591"),
            ("45钢", "优质碳素结构钢", "GB/T 699"),
            ("铝合金6061", "铝合金", "GB/T 3190"),
            ("不锈钢304", "奥氏体不锈钢", "GB/T 20878"),
        ]

        self.materials_table.setRowCount(len(sample_materials))
        for i, (name, mtype, standard) in enumerate(sample_materials):
            self.materials_table.setItem(i, 0, QTableWidgetItem(name))
            self.materials_table.setItem(i, 1, QTableWidgetItem(mtype))
            self.materials_table.setItem(i, 2, QTableWidgetItem(standard))

        self.detail_text.setText("已加载全部材料（共 5 种）")

    def _on_select_material(self, item):
        """选择材料"""
        row = item.row()
        material_name = self.materials_table.item(row, 0).text()

        # TODO: 调用 sw_helper.material 获取材料详情
        self.detail_text.setText(f"材料: {material_name}\n\n[材料详情开发中...]")


# 页面工厂函数
def create_material_page() -> MaterialPage:
    """创建材料查询页面

    Returns:
        MaterialPage: 材料查询页面对象
    """
    return MaterialPage()
