"""
CAE-CLI 主窗口

此模块提供应用程序的主窗口类，
包含菜单栏、工具栏和页面切换功能。
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .theme import CAETheme


class MainWindow(QMainWindow):
    """CAE-CLI 主窗口类"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MechDesign - 机械设计辅助工具")
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
        self.central_widget.setStyleSheet("background-color: transparent;")
        self.setCentralWidget(self.central_widget)

        # 主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 添加横幅 - 在原来菜单栏和工具栏的位置
        self._create_banner()

        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("background-color: transparent;")
        self.main_layout.addWidget(self.tab_widget)

        # 创建页面（占位符）
        self._create_pages()

        # 创建状态栏
        self._create_statusbar()

    def _create_banner(self):
        """创建横幅 - 在导航栏下方显示CAE-CLI ASCII艺术横幅"""
        # 创建横幅部件
        self.banner_widget = QWidget()
        self.banner_widget.setFixedHeight(250)  # 设置高度以适应大字体

        # 设置横幅样式 - 使用蓝色主题
        banner_style = """
        QWidget {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #1a237e, stop:0.5 #283593, stop:1 #303f9f);
            border-bottom: 2px solid #5c6bc0;
            padding: 10px;
        }
        """
        self.banner_widget.setStyleSheet(banner_style)

        # 创建横幅布局
        banner_layout = QVBoxLayout(self.banner_widget)
        banner_layout.setContentsMargins(20, 15, 20, 15)
        banner_layout.setSpacing(8)

        # 添加标题行
        title_label = QLabel("CAE-CLI - 机械设计学习辅助工具")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #4fc3f7;
            font-family: 'Microsoft YaHei UI', 'Segoe UI';
            font-size: 16pt;
            font-weight: bold;
        """)
        banner_layout.addWidget(title_label)

        # ASCII艺术横幅 - 使用QLabel显示
        ascii_container = QWidget()
        ascii_layout = QVBoxLayout(ascii_container)
        ascii_layout.setSpacing(4)  # 行间距
        ascii_layout.setContentsMargins(0, 0, 0, 0)

        # 完整的ASCII艺术横幅
        ascii_lines = [
            "███╗   ███╗███████╗ ██████╗██╗  ██╗██████╗ ███████╗███████╗",
            " ████╗ ████║██╔════╝██╔════╝██║  ██║██╔══██╗██╔════╝██╔════╝",
            " ██╔████╔██║█████╗  ██║     ███████║██║  ██║█████╗  ███████╗",
            " ██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██║  ██║██╔══╝  ╚════██║",
            " ██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██████╔╝███████╗███████║",
            " ╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝",
        ]

        for line in ascii_lines:
            line_label = QLabel(line)
            line_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            line_label.setStyleSheet("""
                font-family: 'Consolas', 'Monaco', 'Courier New', 'Lucida Console', monospace;
                font-size: 16pt;  /* 增大的字体 */
                font-weight: bold;
                color: #64b5f6;
                background-color: transparent;
                padding: 2px 0px;
            """)
            ascii_layout.addWidget(line_label)

        banner_layout.addWidget(ascii_container)

        # 将横幅添加到主布局中
        self.main_layout.addWidget(self.banner_widget)

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        self._create_file_menu(menubar)
        self._create_edit_menu(menubar)
        menubar.addMenu("视图(&V)")
        self._create_tools_menu(menubar)
        self._create_help_menu(menubar)

    def _create_file_menu(self, menubar):
        """创建文件菜单"""
        file_menu = menubar.addMenu("文件(&F)")

        new_action = QAction("新建项目(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)

        open_action = QAction("打开文件(&O)...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)

        save_as_action = QAction("另存为(&A)...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_edit_menu(self, menubar):
        """创建编辑菜单"""
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

    def _create_tools_menu(self, menubar):
        """创建工具菜单"""
        tools_menu = menubar.addMenu("工具(&T)")

        home_action = QAction("首页", self)
        home_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        tools_menu.addAction(home_action)

        tools_menu.addSeparator()

        # 功能页面
        page_actions = [
            ("几何解析", 1),
            ("网格分析", 2),
            ("材料查询", 3),
            ("学习中心", 4),
            ("AI助手", 5),
            ("参数优化", 6),
            ("交互聊天", 7),
        ]

        for label, idx in page_actions:
            action = QAction(label, self)
            action.triggered.connect(lambda checked, i=idx: self.tab_widget.setCurrentIndex(i))
            tools_menu.addAction(action)

    def _create_help_menu(self, menubar):
        """创建帮助菜单"""
        help_menu = menubar.addMenu("帮助(&H)")

        doc_action = QAction("使用文档(&D)", self)
        doc_action.triggered.connect(self._on_show_docs)
        help_menu.addAction(doc_action)

        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 添加工具按钮（带动画效果）
        # 新建
        new_btn = self._create_animated_button("新建", self._on_new_project)
        toolbar.addWidget(new_btn)

        # 打开
        open_btn = self._create_animated_button("打开", self._on_open_file)
        toolbar.addWidget(open_btn)

        # 保存
        save_btn = self._create_animated_button("保存", self._on_save)
        toolbar.addWidget(save_btn)

        toolbar.addSeparator()

        # 快速导航标签
        nav_label = QLabel("快速导航:")
        toolbar.addWidget(nav_label)

        # 快速导航按钮组（带动画）
        nav_buttons = [
            ("首页", 0),
            ("学习", 1),
            ("AI", 2),
            ("聊天", 3),
        ]

        for text, idx in nav_buttons:
            btn = self._create_nav_button(text, idx)
            toolbar.addWidget(btn)

    def _create_animated_button(self, text: str, callback) -> QPushButton:
        """创建带动画效果的按钮"""
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # 存储原始样式
        btn._original_style = btn.styleSheet()

        # 悬停效果：进入
        btn.enterEvent = lambda e: self._animate_button_hover(btn, True)
        # 悬停效果：离开
        btn.leaveEvent = lambda e: self._animate_button_hover(btn, False)

        # 点击效果
        btn.clicked.connect(callback)

        return btn

    def _create_nav_button(self, text: str, page_index: int) -> QPushButton:
        """创建带动画的导航按钮"""
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedWidth(60)

        # 导航动画
        btn.clicked.connect(lambda: self._animate_tab_switch(page_index))

        # 悬停效果
        btn.enterEvent = lambda e: self._animate_button_hover(btn, True)
        btn.leaveEvent = lambda e: self._animate_button_hover(btn, False)

        return btn

    def _animate_button_hover(self, btn: QPushButton, entering: bool):
        """按钮悬停动画 - 蓝紫渐变"""
        if entering:
            # 悬停时使用渐变蓝
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(88, 166, 255, 0.2);
                    color: #58a6ff;
                    border: 1px solid #58a6ff;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
            """)
        else:
            # 恢复原样式
            btn.setStyleSheet("")

    def _animate_tab_switch(self, index: int):
        """标签页切换动画"""
        # 先淡出当前页面
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            # 淡出动画
            self._fade_widget(current_widget, out=True, callback=lambda: self._switch_and_fade(index))
        else:
            self.tab_widget.setCurrentIndex(index)

    def _switch_and_fade(self, index: int):
        """切换并淡入"""
        self.tab_widget.setCurrentIndex(index)
        # 淡入新页面
        new_widget = self.tab_widget.currentWidget()
        if new_widget:
            self._fade_widget(new_widget, out=False)

    def _fade_widget(self, widget: QWidget, out: bool = True, callback=None):
        """淡入淡出动画"""
        if out:
            target = 0
            start = 1
        else:
            target = 1
            start = widget.windowOpacity() if widget.windowOpacity() > 0 else 0

        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setStartValue(start)
        anim.setEndValue(target)
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        if callback:
            anim.finished.connect(callback)

        anim.start()

    def _create_banner(self):
        """创建横幅区域 - 显示CAE-CLI ASCII艺术横幅，嵌入到标题上方"""
        # 创建横幅部件
        self.banner_widget = QWidget()
        self.banner_widget.setObjectName("BannerWidget")
        self.banner_widget.setFixedHeight(130)  # 增加高度以容纳更多信息

        # 设置横幅样式 - 使用蓝色主题，更融入整体界面
        banner_style = """
        QWidget#BannerWidget {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                              stop:0 #1a237e, stop:0.5 #283593, stop:1 #303f9f);
            border-bottom: 2px solid #5c6bc0;
            padding: 5px;
        }
        QLabel#BannerLabel {
            color: #e3f2fd;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 9pt;
            font-weight: bold;
        }
        QLabel#TitleLabel {
            color: #bbdefb;
            font-family: 'Microsoft YaHei UI', 'Segoe UI';
            font-size: 12pt;
            font-weight: bold;
            margin-top: 5px;
        }
        """
        self.banner_widget.setStyleSheet(banner_style)

        # 创建横幅布局
        banner_layout = QVBoxLayout(self.banner_widget)
        banner_layout.setContentsMargins(15, 10, 15, 8)
        banner_layout.setSpacing(3)

        # 添加标题行
        title_label = QLabel("MechDesign - CAE-CLI 机械设计学习辅助工具")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #4fc3f7;
            font-family: 'Microsoft YaHei UI', 'Segoe UI';
            font-size: 14pt;
            font-weight: bold;
            margin-bottom: 5px;
        """)
        banner_layout.addWidget(title_label)

        # ASCII艺术横幅文本（稍作调整以更好融入）
        ascii_art = [
            "███╗   ███╗███████╗ ██████╗██╗  ██╗██████╗ ███████╗███████╗",
            " ████╗ ████║██╔════╝██╔════╝██║  ██║██╔══██╗██╔════╝██╔════╝",
            " ██╔████╔██║█████╗  ██║     ███████║██║  ██║█████╗  ███████╗",
            " ██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██║  ██║██╔══╝  ╚════██║",
            " ██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██████╔╝███████╗███████║",
            " ╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝",
        ]

        # 添加每一行到布局
        for line in ascii_art:
            label = QLabel(line)
            label.setObjectName("BannerLabel")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                color: #64b5f6;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                font-weight: bold;
                margin: 1px 0px;
            """)
            banner_layout.addWidget(label)

        # 将横幅添加到主布局中，在工具栏下方
        self.main_layout.addWidget(self.banner_widget)

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
        """创建页面"""
        # 导入欢迎页面
        from .pages.welcome_page import create_welcome_page

        # 首页 - 使用新的欢迎页面（启动画面）
        self.welcome_page = create_welcome_page()
        self.welcome_page.start_exploring.connect(self._on_navigate_to_main)
        self.tab_widget.addTab(self.welcome_page, "🏠 首页")

        # 启用学习页面和 AI 页面
        from .pages.ai_page import AIPage
        from .pages.chat_page import ChatPage
        from .pages.learn_page import LearnPage

        # 学习中心页面 - 知识库导航中心
        self.learn_page = LearnPage()
        self.learn_page.course_selected.connect(self._on_navigate_to_chat)
        self.learn_page.chat_requested.connect(self._on_chat_requested)
        self.tab_widget.addTab(self.learn_page, "📚 学习")

        # AI助手页面
        self.ai_page = AIPage()
        self.tab_widget.addTab(self.ai_page, "🤖 AI")

        # 交互聊天页面
        self.chat_page = ChatPage("learning")
        self.tab_widget.addTab(self.chat_page, "💬 聊天")

        # 其他页面（暂时禁用）
        # from .pages.home_page import create_home_page
        # from .pages.command_panel import CommandPanel
        # from .pages.geometry_page import GeometryPage
        # from .pages.mesh_page import MeshPage
        # from .pages.material_page import MaterialPage
        # from .pages.optimization_page import OptimizationPage

        # 工作流页面
        from .pages.convert_page import ConvertPage
        from .pages.report_page import ReportPage
        from .pages.run_page import RunPage

        # CAE分析运行页面
        self.run_page = RunPage()
        self.tab_widget.addTab(self.run_page, "🔬 分析")

        # 格式转换页面
        self.convert_page = ConvertPage()
        self.tab_widget.addTab(self.convert_page, "🔄 转换")

        # 报告生成页面
        self.report_page = ReportPage()
        self.tab_widget.addTab(self.report_page, "📄 报告")

        # self.home_page = create_home_page()
        # self.tab_widget.addTab(self.home_page, "🔧 功能")

        # 网格分析页面
        # self.mesh_page = MeshPage()
        # self.tab_widget.addTab(self.mesh_page, "🔲 网格")

        # 材料查询页面
        # self.material_page = MaterialPage()
        # self.tab_widget.addTab(self.material_page, "🔧 材料")

        # 学习中心页面（暂时禁用）
        # self.learn_page = LearnPage()
        # self.learn_page.course_selected.connect(self._on_navigate_to_chat)
        # self.learn_page.chat_requested.connect(self._on_chat_requested)
        # self.tab_widget.addTab(self.learn_page, "📚 学习")

        # AI助手页面（暂时禁用）
        # self.ai_page = AIPage()
        # self.tab_widget.addTab(self.ai_page, "🤖 AI")

        # 参数优化页面（暂时禁用）
        # self.optimization_page = OptimizationPage()
        # self.tab_widget.addTab(self.optimization_page, "⚙️ 优化")

        # 交互聊天页面（暂时禁用）
        # self.chat_page = ChatPage("learning")
        # self.tab_widget.addTab(self.chat_page, "💬 聊天")

    def _on_navigate(self, page_name: str):
        """导航到指定页面"""
        page_map = {
            "parse": 1,  # 几何
            "mesh": 2,  # 网格
            "material": 3,  # 材料
            "learn": 4,  # 学习
            "ai": 5,  # AI
            "optimize": 6,  # 优化
        }
        if page_name in page_map:
            self.tab_widget.setCurrentIndex(page_map[page_name])

    def _on_navigate_to_main(self):
        """从启动画面进入主界面 - 切换到学习页面"""
        self.tab_widget.setCurrentIndex(1)  # 切换到学习页面

    def _on_navigate_to_chat(self, target: str):
        """导航到聊天页面"""
        if target == "chat":
            self.tab_widget.setCurrentIndex(7)  # 聊天页

    def _on_chat_requested(self, mode: str):
        """处理AI问答请求

        Args:
            mode: AI模式 (learning/lifestyle/mechanical/default)
        """
        # 更新聊天页面的模式
        self.chat_page = ChatPage(mode)
        # 替换tab_widget中的聊天页面
        self.tab_widget.removeTab(7)
        self.tab_widget.insertTab(7, self.chat_page, "💬 聊天")
        # 切换到聊天页面
        self.tab_widget.setCurrentIndex(7)

    def _apply_theme(self):
        """应用主题样式"""
        self.setStyleSheet(CAETheme.get_stylesheet())

    def _update_status(self):
        """更新状态信息"""
        # 状态更新逻辑 - 可扩展为显示系统资源使用情况
        pass

    # ==================== 菜单槽函数 ====================

    def _on_new_project(self):
        """新建项目"""
        self.status_label.setText("新建项目...")
        # TODO: 实现新建项目逻辑 - 创建新项目目录结构

    def _on_open_file(self):
        """打开文件"""
        from PySide6.QtWidgets import QFileDialog

        self.status_label.setText("打开文件...")
        # TODO: 实现打开文件逻辑 - 支持CAD/CAE文件打开
        file_path, _ = QFileDialog.getOpenFileName(self, "打开文件", "", "所有文件 (*.*)")
        if file_path:
            self.status_label.setText(f"已打开: {file_path}")

    def _on_save(self):
        """保存"""
        self.status_label.setText("保存...")
        # TODO: 实现保存逻辑 - 保存当前项目状态
        self.status_label.setText("已保存")

    def _on_save_as(self):
        """另存为"""
        from PySide6.QtWidgets import QFileDialog

        self.status_label.setText("另存为...")
        # TODO: 实现另存为逻辑 - 另存为新文件
        file_path, _ = QFileDialog.getSaveFileName(self, "另存为", "", "所有文件 (*.*)")
        if file_path:
            self.status_label.setText(f"已另存为: {file_path}")

    def _on_show_docs(self):
        """显示文档"""
        # TODO: 实现文档显示 - 链接到在线文档或本地文档
        QMessageBox.information(self, "使用文档", "文档功能开发中...")

    def _on_about(self):
        """显示关于"""
        QMessageBox.about(
            self,
            "关于 MechDesign",
            "MechDesign v1.0.0\n\n"
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
