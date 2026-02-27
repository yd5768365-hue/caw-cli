"""
CAE分析运行页面

此模块提供CAE分析运行功能的GUI界面。
支持使用不同的求解器进行静力、模态、热分析等。
"""

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class AnalysisWorker(QThread):
    """分析工作线程"""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            from integrations.cae.solvers import SolverConfig, get_solver

            # 获取求解器
            solver_name = self.config.get("solver", "simple")
            solver = get_solver(solver_name)

            # 如果求解器不可用，使用 simple
            if not solver.is_available():
                from integrations.cae.solvers import SimpleFEMSolver

                solver = SimpleFEMSolver()

            # 构建配置
            material = self.config.get("material", {})
            solver_config = SolverConfig(
                analysis_type=self.config.get("analysis_type", "static"),
                material=material,
                load=self.config.get("load", 1000),
                mesh_size=self.config.get("mesh_size", 10.0),
                geometry=self.config.get("geometry", {}),
            )

            # 执行分析
            result = solver.solve(solver_config)

            self.finished.emit(
                {
                    "max_displacement": result.max_displacement,
                    "max_stress": result.max_stress,
                    "safety_factor": result.safety_factor,
                    "solver": solver.name,
                    "messages": result.messages,
                }
            )
        except Exception as e:
            self.error.emit(str(e))


class RunPage(QWidget):
    """CAE分析运行页面类"""

    # 信号：分析完成
    analysis_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.worker = None
        self._init_ui()
        self._check_solver_status()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("CAE 分析运行")
        title.setProperty("heading", True)
        layout.addWidget(title)

        # 求解器选择
        solver_group = QGroupBox("求解器设置")
        solver_layout = QFormLayout()

        # 求解器类型
        self.solver_combo = QComboBox()
        self.solver_combo.addItems(
            [
                ("simple", "简易求解器 (内置，无需安装)"),
                ("scipy", "SciPy 求解器 (需要scipy)"),
                ("calculix", "CalculiX 求解器 (需要安装ccx)"),
            ]
        )
        self.solver_combo.setCurrentIndex(0)
        self.solver_combo.currentIndexChanged.connect(self._on_solver_changed)
        solver_layout.addRow("求解器:", self.solver_combo)

        # 求解器状态显示
        self.solver_status_label = QLabel()
        self.solver_status_label.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        solver_layout.addRow("状态:", self.solver_status_label)

        # 分析类型
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems(["static", "modal", "thermal", "buckling"])
        solver_layout.addRow("分析类型:", self.analysis_combo)

        solver_group.setLayout(solver_layout)
        layout.addWidget(solver_group)

        # CalculiX 特定配置
        self.calculix_group = QGroupBox("CalculiX 配置")
        calculix_layout = QFormLayout()

        # 输入文件选择
        input_file_layout = QHBoxLayout()
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("选择或生成 .inp 文件...")
        input_file_layout.addWidget(self.input_file_edit)

        self.input_file_btn = QPushButton("浏览...")
        self.input_file_btn.setFixedWidth(80)
        self.input_file_btn.clicked.connect(self._browse_input_file)
        input_file_layout.addWidget(self.input_file_btn)

        calculix_layout.addRow("输入文件:", input_file_layout)

        # 生成输入文件按钮
        self.generate_inp_btn = QPushButton("生成输入文件")
        self.generate_inp_btn.clicked.connect(self._generate_input_file)
        calculix_layout.addRow("", self.generate_inp_btn)

        # 结果文件查看
        result_file_layout = QHBoxLayout()
        self.result_file_edit = QLineEdit()
        self.result_file_edit.setPlaceholderText("选择 .frd 或 .dat 结果文件...")
        result_file_layout.addWidget(self.result_file_edit)

        self.result_file_btn = QPushButton("浏览...")
        self.result_file_btn.setFixedWidth(80)
        self.result_file_btn.clicked.connect(self._browse_result_file)
        result_file_layout.addWidget(self.result_file_btn)

        calculix_layout.addRow("结果文件:", result_file_layout)

        # 读取结果按钮
        self.read_result_btn = QPushButton("读取结果")
        self.read_result_btn.clicked.connect(self._read_result_file)
        calculix_layout.addRow("", self.read_result_btn)

        self.calculix_group.setLayout(calculix_layout)
        self.calculix_group.setVisible(False)  # 默认隐藏
        layout.addWidget(self.calculix_group)

        # 材料设置
        material_group = QGroupBox("材料设置")
        material_layout = QFormLayout()

        # 材料选择
        self.material_combo = QComboBox()
        self.material_combo.addItems(
            [
                "Q235",
                "Q345",
                "45钢",
                "40Cr",
                "304不锈钢",
                "6061",
                "7075",
                "TC4",
                "紫铜",
                "黄铜",
            ]
        )
        self.material_combo.setCurrentIndex(0)
        material_layout.addRow("材料:", self.material_combo)

        # 弹性模量（可选）
        self.emergency_layout = QLineEdit()
        self.emergency_layout.setPlaceholderText("默认从材料库获取")
        material_layout.addRow("自定义E(MPa):", self.emergency_layout)

        material_group.setLayout(material_layout)
        layout.addWidget(material_group)

        # 载荷设置
        load_group = QGroupBox("载荷与几何")
        load_layout = QFormLayout()

        # 载荷值
        self.load_spin = QDoubleSpinBox()
        self.load_spin.setRange(0, 1e9)
        self.load_spin.setValue(5000)
        self.load_spin.setSuffix(" N")
        load_layout.addRow("集中载荷:", self.load_spin)

        # 梁长度
        self.length_spin = QDoubleSpinBox()
        self.length_spin.setRange(10, 10000)
        self.length_spin.setValue(1000)
        self.length_spin.setSuffix(" mm")
        load_layout.addRow("梁长度:", self.length_spin)

        # 截面宽度
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(1, 1000)
        self.width_spin.setValue(50)
        self.width_spin.setSuffix(" mm")
        load_layout.addRow("截面宽度:", self.width_spin)

        # 截面高度
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1, 1000)
        self.height_spin.setValue(100)
        self.height_spin.setSuffix(" mm")
        load_layout.addRow("截面高度:", self.height_spin)

        load_group.setLayout(load_layout)
        layout.addWidget(load_group)

        # 运行按钮
        self.run_btn = QPushButton("开始分析")
        self.run_btn.setProperty("primary", True)
        self.run_btn.clicked.connect(self._on_run)
        layout.addWidget(self.run_btn)

        # 结果显示区域
        result_group = QGroupBox("分析结果")
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("分析结果将显示在此处...")
        result_layout.addWidget(self.result_text)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()

    def _check_solver_status(self):
        """检查各求解器安装状态"""
        try:
            from integrations.cae.solvers import get_solver

            # 检查 CalculiX 状态
            calculix_solver = get_solver("calculix")
            if calculix_solver.is_available():
                self.solver_status_label.setText("✓ CalculiX 已安装 (ccx 可用)")
                self.solver_status_label.setStyleSheet("color: #22c55e;")
            else:
                self.solver_status_label.setText("✗ CalculiX 未安装 (将使用备用求解器)")
                self.solver_status_label.setStyleSheet("color: #f59e0b;")
        except Exception as e:
            self.solver_status_label.setText(f"状态检查失败: {e}")
            self.solver_status_label.setStyleSheet("color: #f85149;")

    def _on_solver_changed(self, index):
        """求解器选择改变"""
        solver_name = self.solver_combo.currentData()

        # 显示/隐藏 CalculiX 配置
        self.calculix_group.setVisible(solver_name == "calculix")

        # 更新状态显示
        if solver_name == "calculix":
            try:
                from integrations.cae.solvers import get_solver

                calculix_solver = get_solver("calculix")
                if calculix_solver.is_available():
                    self.solver_status_label.setText("✓ CalculiX 已安装")
                    self.solver_status_label.setStyleSheet("color: #22c55e;")
                else:
                    self.solver_status_label.setText("✗ CalculiX 未安装")
                    self.solver_status_label.setStyleSheet("color: #f85149;")
            except Exception:
                pass

    def _browse_input_file(self):
        """浏览输入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 CalculiX 输入文件", "", "INP 文件 (*.inp);;所有文件 (*.*)"
        )
        if file_path:
            self.input_file_edit.setText(file_path)

    def _browse_result_file(self):
        """浏览结果文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 CalculiX 结果文件", "", "FRD 文件 (*.frd);;DAT 文件 (*.dat);;所有文件 (*.*)"
        )
        if file_path:
            self.result_file_edit.setText(file_path)

    def _generate_input_file(self):
        """生成 CalculiX 输入文件"""
        file_path, _ = QFileDialog.getSaveFileName(self, "保存 CalculiX 输入文件", "model.inp", "INP 文件 (*.inp)")
        if not file_path:
            return

        try:
            from integrations.cae.solvers import SolverConfig, get_solver

            # 获取材料信息
            material_name = self.material_combo.currentText()
            from sw_helper.material.database import MaterialDatabase

            db = MaterialDatabase()
            mat_info = db.get_material(material_name)

            if not mat_info:
                self.result_text.setText(f"未找到材料: {material_name}")
                return

            # 构建配置
            config = SolverConfig(
                analysis_type=self.analysis_combo.currentText(),
                material={
                    "elastic_modulus": mat_info.get("elastic_modulus", 210e9),
                    "yield_strength": mat_info.get("yield_strength", 235e6),
                    "poisson_ratio": mat_info.get("poisson_ratio", 0.3),
                },
                load=self.load_spin.value(),
                geometry={
                    "length": self.length_spin.value(),
                    "width": self.width_spin.value(),
                    "height": self.height_spin.value(),
                },
            )

            # 生成输入文件
            solver = get_solver("calculix")
            if solver.generate_input(config, file_path):
                self.input_file_edit.setText(file_path)
                self.result_text.setText(f"输入文件已生成: {file_path}\n\n可以使用 ccx 求解后读取结果。")
            else:
                self.result_text.setText("生成输入文件失败")

        except Exception as e:
            self.result_text.setText(f"生成失败: {e}")

    def _read_result_file(self):
        """读取结果文件"""
        file_path = self.result_file_edit.text()
        if not file_path:
            self.result_text.setText("请先选择结果文件")
            return

        try:
            from integrations.cae.solvers import SolverConfig, get_solver

            # 构建配置
            material_name = self.material_combo.currentText()
            from sw_helper.material.database import MaterialDatabase

            db = MaterialDatabase()
            mat_info = db.get_material(material_name)

            config = SolverConfig(
                analysis_type=self.analysis_combo.currentText(),
                material={
                    "elastic_modulus": mat_info.get("elastic_modulus", 210e9),
                    "yield_strength": mat_info.get("yield_strength", 235e6),
                    "poisson_ratio": mat_info.get("poisson_ratio", 0.3),
                },
            )

            solver = get_solver("calculix")
            result = solver.read_results(file_path, config)

            lines = [
                "【结果读取完成】",
                "",
                f"最大位移: {result.max_displacement*1000:.6f} mm",
                f"最大应力: {result.max_stress/1e6:.2f} MPa",
                f"安全系数: {result.safety_factor:.2f}",
                "",
            ]

            if result.messages:
                lines.append("--- 详细信息 ---")
                lines.append(result.messages)

            self.result_text.setText("\n".join(lines))

        except Exception as e:
            self.result_text.setText(f"读取失败: {e}")

    def _on_run(self):
        """开始分析"""
        # 获取材料信息
        material_name = self.material_combo.currentText()

        try:
            from sw_helper.material.database import MaterialDatabase

            db = MaterialDatabase()
            mat_info = db.get_material(material_name)

            if not mat_info:
                self.result_text.setText(f"未找到材料: {material_name}")
                return
        except Exception as e:
            self.result_text.setText(f"加载材料失败: {e}")
            return

        # 更新UI状态
        self.run_btn.setEnabled(False)
        self.result_text.setText("正在分析...\n")

        # 构建配置
        config = {
            "solver": self.solver_combo.currentData(),
            "analysis_type": self.analysis_combo.currentText(),
            "material": {
                "elastic_modulus": mat_info.get("elastic_modulus", 210e9),
                "yield_strength": mat_info.get("yield_strength", 235e6),
                "poisson_ratio": mat_info.get("poisson_ratio", 0.3),
            },
            "load": self.load_spin.value(),
            "mesh_size": 10.0,
            "geometry": {
                "length": self.length_spin.value(),
                "width": self.width_spin.value(),
                "height": self.height_spin.value(),
            },
        }

        # 启动工作线程
        self.worker = AnalysisWorker(config)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_finished(self, result):
        """分析完成"""
        self.run_btn.setEnabled(True)

        # 显示结果
        lines = [
            "【分析完成】",
            "",
            f"求解器: {result.get('solver', 'N/A')}",
            "",
            "--- 结果 ---",
            f"最大位移: {result.get('max_displacement', 0)*1000:.6f} mm",
            f"最大应力: {result.get('max_stress', 0)/1e6:.2f} MPa",
            f"安全系数: {result.get('safety_factor', 0):.2f}",
            "",
        ]

        if result.get("messages"):
            lines.append("--- 详细信息 ---")
            lines.append(result["messages"])

        self.result_text.setText("\n".join(lines))

    def _on_error(self, error_msg):
        """分析错误"""
        self.run_btn.setEnabled(True)
        self.result_text.setText(f"分析失败: {error_msg}")
