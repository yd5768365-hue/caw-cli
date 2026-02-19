"""
CAE-CLI 主窗口

此模块提供应用程序的主窗口类，
包含菜单栏、工具栏和页面切换功能。
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QMenuBar,
    QMenu,
    QToolBar,
    QStatusBar,
    QLabel,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QKeySequence

from .theme import CAETheme, MAIN_RED, HIGHLIGHT_RED


class MainWindow(QMainWindow):
    """CAE-CLI 主窗口类"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAE-CLI - 机械设计辅助工具")
        self.setMinimumSize(1200, 800)

        # 初始化UI
        self._init_ui()

        # 应用主题
        self._apply_theme()

        # 状态栏更新定时器
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(1000)

    def _init_ui(self):
        """初始化用户界面"""
        # 创建中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 创建标签页
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # 创建菜单栏
        self._create_menu_bar()

        # 创建工具栏
        self._create_toolbar()

        # 创建状态栏
        self._create_statusbar()

        # 创建页面（占位符）
        self._create_pages()

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        # 新建项目
        new_action = QAction("新建项目(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)

        # 打开文件
        open_action = QAction("打开文件(&O)...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # 保存
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)

        # 另存为
        save_as_action = QAction("另存为(&A)...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        copy_action = QAction("复制(&C)", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("粘贴(&V)", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        edit_menu.addAction(paste_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        # 几何解析
        geometry_action = QAction("几何解析", self)
        geometry_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        tools_menu.addAction(geometry_action)

        # 网格分析
        mesh_action = QAction("网格分析", self)
        mesh_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        tools_menu.addAction(mesh_action)

        # 材料查询
        material_action = QAction("材料查询", self)
        material_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        tools_menu.addAction(material_action)

        # 参数优化
        optimize_action = QAction("参数优化", self)
        optimize_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        tools_menu.addAction(optimize_action)

        tools_menu.addSeparator()

        # AI助手
        ai_action = QAction("AI助手", self)
        ai_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        tools_menu.addAction(ai_action)

        # 学习模式
        chat_action = QAction("学习模式", self)
        chat_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(5))
        tools_menu.addAction(chat_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        # 文档
        doc_action = QAction("使用文档(&D)", self)
        doc_action.triggered.connect(self._on_show_docs)
        help_menu.addAction(doc_action)

        # 关于
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 添加工具按钮
        # 新建
        new_action = QAction("新建", self)
        new_action.triggered.connect(self._on_new_project)
        toolbar.addAction(new_action)

        # 打开
        open_action = QAction("打开", self)
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)

        # 保存
        save_action = QAction("保存", self)
        save_action.triggered.connect(self._on_save)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # 快速切换
        toolbar.addWidget(QLabel("快速导航: "))

    def _create_statusbar(self):
        """创建状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.statusbar.addWidget(self.status_label)

        # 进度标签（用于显示任务进度）
        self.progress_label = QLabel("")
        self.statusbar.addPermanentWidget(self.progress_label)

    def _create_pages(self):
        """创建页面（占位符）"""
        # TODO: 后续创建具体页面
        from .pages import (
            GeometryPage,
            MeshPage,
            MaterialPage,
            OptimizationPage,
            AIPage,
            ChatPage,
        )

        # 几何解析页面
        self.geometry_page = GeometryPage()
        self.tab_widget.addTab(self.geometry_page, "几何解析")

        # 网格分析页面
        self.mesh_page = MeshPage()
        self.tab_widget.addTab(self.mesh_page, "网格分析")

        # 材料查询页面
        self.material_page = MaterialPage()
        self.tab_widget.addTab(self.material_page, "材料查询")

        # 参数优化页面
        self.optimization_page = OptimizationPage()
        self.tab_widget.addTab(self.optimization_page, "参数优化")

        # AI助手页面
        self.ai_page = AIPage()
        self.tab_widget.addTab(self.ai_page, "AI助手")

        # 学习模式页面
        self.chat_page = ChatPage()
        self.tab_widget.addTab(self.chat_page, "学习模式")

    def _apply_theme(self):
        """应用主题样式"""
        self.setStyleSheet(CAETheme.get_stylesheet())

    def _update_status(self):
        """更新状态信息"""
        # TODO: 实现状态更新逻辑
        pass

    # ==================== 菜单槽函数 ====================

    def _on_new_project(self):
        """新建项目"""
        self.status_label.setText("新建项目...")
        # TODO: 实现新建项目逻辑

    def _on_open_file(self):
        """打开文件"""
        self.status_label.setText("打开文件...")
        # TODO: 实现打开文件逻辑

    def _on_save(self):
        """保存"""
        self.status_label.setText("保存...")
        # TODO: 实现保存逻辑

    def _on_save_as(self):
        """另存为"""
        self.status_label.setText("另存为...")
        # TODO: 实现另存为逻辑

    def _on_show_docs(self):
        """显示文档"""
        # TODO: 实现文档显示
        QMessageBox.information(self, "使用文档", "文档功能开发中...")

    def _on_about(self):
        """显示关于"""
        QMessageBox.about(
            self,
            "关于 CAE-CLI",
            "CAE-CLI v0.1.0\n\n"
            "机械设计辅助工具\n\n"
            "基于 PySide6 构建\n"
            "支持几何解析、网格分析、材料查询、参数优化等功能",
        )

    # ==================== 公共接口 ====================

    def set_status(self, message: str):
        """设置状态栏消息

        Args:
            message: 状态消息
        """
        self.status_label.setText(message)

    def set_progress(self, message: str):
        """设置进度消息

        Args:
            message: 进度消息
        """
        self.progress_label.setText(message)

    def clear_progress(self):
        """清除进度消息"""
        self.progress_label.setText("")


def create_main_window() -> MainWindow:
    """创建主窗口实例

    Returns:
        MainWindow: 主窗口对象
    """
    return MainWindow()
