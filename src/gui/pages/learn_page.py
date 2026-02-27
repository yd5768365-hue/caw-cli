"""
CAE-CLI 学习中心页面
对应 CLI 命令: cae-cli learn
支持课程浏览、测验、学习进度跟踪
"""

import re  # 性能优化：模块级别导入

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

# 颜色方案
COLORS = {
    "background": "#0d0e1a",
    "surface": "#12131f",
    "surface2": "#1a1b2e",
    "surface3": "#1e2035",
    "border": "rgba(80,120,255,0.13)",
    "primary": "#4a7fff",
    "amber": "#f0a500",
    "green": "#3ddc84",
    "text": "#cdd6f4",
    "text_secondary": "#6c7a9c",
}


class LearnPage(QWidget):
    """学习中心页面 - 对应 cae-cli learn 命令"""

    # 信号
    course_selected = Signal(str)  # 课程被选中
    chat_requested = Signal(str)  # AI问答请求，参数为模式

    def __init__(self):
        super().__init__()
        self.current_course = None
        self.current_quiz = None
        self.quiz_score = 0
        self.quiz_total = 0
        self.selected_filter = "全部"
        self._content_frame = None  # 主内容区域的frame
        self._init_ui()
        self._load_courses()
        self._load_progress()

    def _init_ui(self):
        """初始化UI"""
        # 设置整体背景
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== 左侧：侧边栏 =====
        left_panel = QWidget()
        left_panel.setFixedWidth(280)
        left_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 20, 16, 20)
        left_layout.setSpacing(16)

        # 1. 顶部标题区
        title = QLabel("学习中心")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")
        left_layout.addWidget(title)

        # 2. 学习进度区
        progress_header = QHBoxLayout()
        progress_label = QLabel("学习进度")
        progress_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        progress_header.addWidget(progress_label)

        self.progress_text = QLabel("0/5")
        self.progress_text.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        progress_header.addWidget(self.progress_text, alignment=Qt.AlignmentFlag.AlignRight)
        left_layout.addLayout(progress_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 2px;
                background-color: {COLORS['surface3']};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: 2px;
            }}
        """)
        left_layout.addWidget(self.progress_bar)

        # 3. 搜索框
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("border: none; font-size: 14px;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索课程...")
        self.search_input.textChanged.connect(self._on_search)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['surface2']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_secondary']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)

        # 4. 筛选标签
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.filter_buttons = {}
        filters = ["全部", "机械", "CAE", "笔记"]
        filter_group = QButtonGroup(self)

        for f in filters:
            btn = QPushButton(f)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            is_selected = f == "全部"
            btn.setChecked(is_selected)

            if is_selected:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['primary']};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 12px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['surface2']};
                        color: {COLORS['text_secondary']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['surface3']};
                    }}
                """)

            btn.clicked.connect(lambda checked, ft=f: self._on_filter_clicked(ft))
            filter_group.addButton(btn)
            self.filter_buttons[f] = btn
            filter_layout.addWidget(btn)

        left_layout.addLayout(filter_layout)

        # 5. 课程列表
        self.course_list = QListWidget()
        self.course_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                padding: 0;
            }}
            QListWidget::item {{
                background-color: {COLORS['surface2']};
                border-radius: 8px;
                padding: 0;
                margin-bottom: 8px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['surface3']};
            }}
        """)
        self.course_list.setSpacing(8)
        self.course_list.itemClicked.connect(self._on_course_clicked)
        left_layout.addWidget(self.course_list, 1)

        # 6. 底部操作区
        # 文本输入框（用于笔记输入）
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("记录笔记...")
        self.note_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['surface2']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_secondary']};
            }}
        """)
        left_layout.addWidget(self.note_input)

        # AI问答和笔记按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.chat_btn = QPushButton("AI问答")
        self.chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chat_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['green']};
                color: #000;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #2fc471;
            }}
        """)
        self.chat_btn.clicked.connect(self._on_chat_clicked)
        btn_layout.addWidget(self.chat_btn)

        self.note_btn = QPushButton("笔记")
        self.note_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.note_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #3a6fd9;
            }}
        """)
        self.note_btn.clicked.connect(self._on_note_clicked)
        btn_layout.addWidget(self.note_btn)

        left_layout.addLayout(btn_layout)

        # 刷新课程按钮
        self.refresh_btn = QPushButton("刷新课程")
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface2']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface3']};
                color: {COLORS['text']};
            }}
        """)
        self.refresh_btn.clicked.connect(self._load_courses)
        left_layout.addWidget(self.refresh_btn)

        layout.addWidget(left_panel)

        # ===== 右侧：主内容区 =====
        right_panel = QWidget()
        right_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 20, 24, 20)
        right_layout.setSpacing(16)

        # 1. 内容栏顶部
        header_layout = QHBoxLayout()

        # 左侧：当前课程名称 + 副标题
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        self.content_title = QLabel("欢迎使用学习中心")
        self.content_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.content_title.setStyleSheet(f"color: {COLORS['text']};")
        title_layout.addWidget(self.content_title)

        self.content_desc = QLabel("")
        self.content_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        title_layout.addWidget(self.content_desc)

        header_layout.addLayout(title_layout, 1)

        # 右上角：琥珀色小标签显示完成课程数
        self.completed_label = QLabel("已完成 0/5")
        self.completed_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['amber']};
                color: #000;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(self.completed_label)

        right_layout.addLayout(header_layout)

        # 2. 主内容区域
        self._content_frame = QFrame()
        self._content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        content_layout = QVBoxLayout(self._content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)

        # 初始化内容（未选课时的显示）
        self._show_empty_state()

        right_layout.addWidget(self._content_frame, 1)

        # 3. 底部标签（课程/笔记切换）
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(0)

        self.course_tab_btn = QPushButton("课程")
        self.course_tab_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.course_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px 0 0 6px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }}
        """)
        self.course_tab_btn.clicked.connect(self._show_course_tab)
        tab_layout.addWidget(self.course_tab_btn)

        self.notes_tab_btn = QPushButton("笔记")
        self.notes_tab_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.notes_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface2']};
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 0 6px 6px 0;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface3']};
                color: {COLORS['text']};
            }}
        """)
        self.notes_tab_btn.clicked.connect(self._show_notes_tab)
        tab_layout.addWidget(self.notes_tab_btn)

        tab_layout.addStretch()
        right_layout.addLayout(tab_layout)

        layout.addWidget(right_panel, 1)

    def _show_empty_state(self):
        """显示未选课时的空状态"""
        if self._content_frame is None:
            return

        content_layout = self._content_frame.layout()

        # 清除现有内容
        while content_layout.count():
            item = content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 黄色居中引导状态
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setContentsMargins(40, 40, 40, 40)
        empty_layout.setSpacing(16)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 大图标
        icon_label = QLabel("📚")
        icon_label.setStyleSheet("font-size: 48px; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(icon_label)

        # 说明文字
        desc_label = QLabel("从左侧选择课程开始学习")
        desc_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 14px;
            border: none;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(desc_label)

        # 三个常用课程快捷入口
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(12)
        quick_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        quick_courses = [
            ("📚", "材料力学"),
            ("🔧", "机械设计"),
            ("🧮", "有限元"),
        ]

        for emoji, name in quick_courses:
            btn = QPushButton(f"{emoji} {name}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['surface2']};
                    color: {COLORS['text']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['surface3']};
                    border-color: {COLORS['primary']};
                }}
            """)
            quick_layout.addWidget(btn)

        empty_layout.addLayout(quick_layout)

        # 提示条
        hint_label = QLabel("💡 学完课程可以做笔记")
        hint_label.setStyleSheet(f"""
            color: {COLORS['amber']};
            font-size: 12px;
            border: none;
            padding-top: 8px;
        """)
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(hint_label)

        content_layout.addWidget(empty_widget, 1)

    def _show_course_content(self, content: str):
        """显示课程内容"""
        if self._content_frame is None:
            return

        content_layout = self._content_frame.layout()

        # 清除现有内容
        while content_layout.count():
            item = content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 课程内容浏览器
        self.content_browser = QTextBrowser()
        self.content_browser.setStyleSheet(f"""
            QTextBrowser {{
                border: none;
                background-color: transparent;
                color: {COLORS['text']};
                selection-background-color: rgba(74, 127, 255, 0.3);
                padding: 0;
            }}
            QTextBrowser a {{
                color: {COLORS['primary']};
            }}
            QTextBrowser a:hover {{
                color: #6b9fff;
            }}
        """)
        self.content_browser.setHtml(self._markdown_to_html(content))
        content_layout.addWidget(self.content_browser, 1)

    def _show_notes_content(self):
        """显示笔记内容"""
        if self._content_frame is None:
            return

        content_layout = self._content_frame.layout()

        # 清除现有内容
        while content_layout.count():
            item = content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 笔记内容
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        notes_layout.setContentsMargins(0, 0, 0, 0)

        note_title = QLabel("我的笔记")
        note_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        note_title.setStyleSheet(f"color: {COLORS['text']}; border: none;")
        notes_layout.addWidget(note_title)

        # 示例笔记列表
        sample_notes = [
            ("材料力学", "应力计算公式：σ = F/A"),
            ("有限元", "单元类型： tetrahedron, hexahedron"),
        ]

        for title, content in sample_notes:
            note_item = QFrame()
            note_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['surface2']};
                    border-radius: 8px;
                    padding: 12px;
                }}
            """)
            note_layout = QVBoxLayout(note_item)
            note_layout.setContentsMargins(12, 12, 12, 12)

            note_title_label = QLabel(title)
            note_title_label.setStyleSheet(f"""
                color: {COLORS['primary']};
                font-weight: bold;
                border: none;
            """)
            note_layout.addWidget(note_title_label)

            note_content_label = QLabel(content)
            note_content_label.setStyleSheet(f"""
                color: {COLORS['text']};
                border: none;
            """)
            note_layout.addWidget(note_content_label)

            notes_layout.addWidget(note_item)

        notes_layout.addStretch()
        content_layout.addWidget(notes_widget, 1)

    def _show_course_tab(self):
        """切换到课程标签"""
        self.course_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px 0 0 6px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }}
        """)
        self.notes_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface2']};
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 0 6px 6px 0;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface3']};
                color: {COLORS['text']};
            }}
        """)

        if self.current_course:
            self._show_course_by_id(self.current_course)
        else:
            self._show_empty_state()

    def _show_notes_tab(self):
        """切换到笔记标签"""
        self.course_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface2']};
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 6px 0 0 6px;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface3']};
                color: {COLORS['text']};
            }}
        """)
        self.notes_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 0 6px 6px 0;
                padding: 10px 24px;
                font-weight: bold;
                font-size: 13px;
            }}
        """)

        self._show_notes_content()

    def _on_filter_clicked(self, filter_name: str):
        """筛选标签点击"""
        self.selected_filter = filter_name

        # 更新按钮样式
        for name, btn in self.filter_buttons.items():
            if name == filter_name:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['primary']};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 12px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['surface2']};
                        color: {COLORS['text_secondary']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['surface3']};
                    }}
                """)

        # 过滤课程列表
        self._filter_courses()

    def _filter_courses(self):
        """根据筛选条件过滤课程"""
        search_text = self.search_input.text().lower()

        for i in range(self.course_list.count()):
            item = self.course_list.item(i)
            course_name = item.text().lower()

            # 搜索过滤
            matches_search = search_text in course_name if search_text else True

            # 筛选过滤
            matches_filter = True
            if self.selected_filter != "全部":
                # 检查课程是否匹配筛选条件
                category_map = {
                    "机械": ["机械", "设计", "力学"],
                    "CAE": ["有限元", "CAE", "分析"],
                    "笔记": ["笔记"],
                }
                categories = category_map.get(self.selected_filter, [])
                matches_filter = any(cat in course_name for cat in categories)

            item.setHidden(not (matches_search and matches_filter))

    def _load_courses(self):
        """加载课程列表"""
        try:
            from sw_helper.learn import CourseManager

            self.course_list.clear()
            courses = CourseManager.get_all_courses()

            for course in courses:
                self._add_course_to_list(course.name, course.id, course.description)

        except Exception:
            # 如果学习模块不可用，显示默认课程
            self._load_default_courses()

    def _load_default_courses(self):
        """加载默认课程（当learn模块不可用时）"""
        self.course_list.clear()
        default_courses = [
            ("materials", "材料力学", "📚"),
            ("mechanics", "理论力学", "📚"),
            ("fem", "有限元基础", "🧮"),
            ("fasteners", "机械设计", "🔧"),
            ("tolerances", "CAE分析", "🧮"),
        ]

        for course_id, name, emoji in default_courses:
            self._add_course_to_list(name, course_id, emoji)

    def _add_course_to_list(self, name: str, course_id: str, emoji: str = "📚"):
        """添加课程到列表"""
        # 创建自定义widget
        widget = QWidget()
        widget.setStyleSheet("border: none; background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # 左边小图标块
        icon_label = QLabel(emoji)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                border: none;
                background-color: {COLORS['surface3']};
                border-radius: 6px;
                padding: 6px;
            }}
        """)
        icon_label.setFixedSize(40, 40)
        layout.addWidget(icon_label)

        # 中间文字（课程名）
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-weight: bold;
                font-size: 13px;
                border: none;
            }}
        """)
        layout.addWidget(name_label, 1)

        # 创建item
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, course_id)
        item.setSizeHint(widget.sizeHint())

        self.course_list.addItem(item)
        self.course_list.setItemWidget(item, widget)

    def _load_progress(self):
        """加载学习进度"""
        try:
            from sw_helper.learning.progress_tracker import get_progress_tracker

            tracker = get_progress_tracker()
            # 获取总体进度
            stats = tracker.get_statistics()
            progress = stats.get("completion_rate", 0) * 100
            self.progress_bar.setValue(int(progress))

            # 更新进度文字
            completed = int(progress / 20)  # 假设总共5个课程
            self.progress_text.setText(f"{completed}/5")

        except Exception:
            # 如果进度跟踪不可用，使用默认进度
            self.progress_bar.setValue(0)
            self.progress_text.setText("0/5")

    def _on_search(self, text):
        """搜索课程"""
        self._filter_courses()

    def _on_course_clicked(self, item):
        """课程被点击"""
        course_id = item.data(Qt.ItemDataRole.UserRole)
        self._show_course(course_id)

        # 更新选中高亮
        for i in range(self.course_list.count()):
            list_item = self.course_list.item(i)
            if list_item == item:
                self.course_list.setCurrentItem(list_item)
                widget = self.course_list.itemWidget(list_item)
                if widget:
                    widget.setStyleSheet(f"""
                        QWidget {{
                            border: none;
                            background-color: {COLORS['primary']};
                            border-radius: 8px;
                        }}
                    """)

    def _show_course(self, course_id):
        """显示课程内容"""
        self.current_course = course_id
        self._show_course_by_id(course_id)

    def _show_course_by_id(self, course_id):
        """根据ID显示课程"""
        try:
            from sw_helper.learn import CourseManager, load_course_content

            course = CourseManager.get_course(course_id)
            if not course:
                self._show_default_content(course_id)
                return

            self.content_title.setText(course.name)
            self.content_desc.setText(course.description)

            # 加载内容
            content = load_course_content(course_id)
            html_content = self._markdown_to_html(content)
            self._show_course_content(html_content)

        except Exception:
            self._show_default_content(course_id)

    def _show_default_content(self, course_id):
        """显示默认内容（当learn模块不可用时）"""
        content_map = {
            "materials": """# 材料力学

## 概述
材料力学是研究材料在外部载荷作用下行为的学科。

## 基本概念
- **应力**: 单位面积上的内力
- **应变**: 变形程度
- **弹性模量**: 材料刚度的度量

## 常用材料
| 材料 | 弹性模量(GPa) | 屈服强度(MPa) |
|------|---------------|--------------|
| 钢   | 200           | 250          |
| 铝   | 70            | 40           |
| 铜   | 100           | 33           |
""",
            "mechanics": """# 理论力学

## 概述
理论力学研究物体的机械运动规律。

## 主要内容
- **静力学**: 力的平衡条件
- **动力学**: 运动与力的关系
- **运动学**: 运动的几何描述

## 基本定律
1. 牛顿第一定律（惯性定律）
2. 牛顿第二定律（F=ma）
3. 牛顿第三定律（作用反作用）
""",
            "fem": """# 有限元基础

## 概述
有限元法是一种数值分析方法，用于求解复杂工程问题。

## 基本步骤
1. **离散化**: 将结构划分为有限个单元
2. **单元分析**: 建立单元刚度矩阵
3. **整体装配**: 组装整体刚度矩阵
4. **求解**: 施加边界条件并求解
5. **后处理**: 计算应力和应变
""",
            "fasteners": """# 机械设计

## 螺栓连接
- **等级**: 4.6, 8.8, 10.9, 12.9
- **预紧力**: 保证连接紧密性

## 螺纹参数
- **大径**: 螺纹外径
- **小径**: 螺纹内径
- **中径**: 螺纹平均直径
- **螺距**: 相邻牙型对应点距离
""",
            "tolerances": """# CAE分析

## 基本概念
- **公差**: 允许尺寸变动量
- **配合**: 孔与轴的松紧关系

## 配合类型
- **间隙配合**: 孔 > 轴
- **过盈配合**: 孔 < 轴
- **过渡配合**: 可能间隙或过盈
""",
        }

        # 根据课程ID获取课程名称
        name_map = {
            "materials": "材料力学",
            "mechanics": "理论力学",
            "fem": "有限元基础",
            "fasteners": "机械设计",
            "tolerances": "CAE分析",
        }

        content = content_map.get(course_id, "# 课程内容\n\n正在开发中...")
        self.content_title.setText(name_map.get(course_id, course_id))
        self.content_desc.setText("")
        self._show_course_content(self._markdown_to_html(content))

    def _on_chat_clicked(self):
        """点击AI问答按钮"""
        mode = "learning"  # 默认模式
        self.chat_requested.emit(mode)

    def _on_note_clicked(self):
        """点击笔记按钮"""
        note_text = self.note_input.text().strip()
        if not note_text:
            QMessageBox.information(self, "提示", "请先输入笔记内容")
            return

        # 保存笔记（简化版本）
        QMessageBox.information(self, "提示", "笔记已保存")
        self.note_input.clear()

    def _markdown_to_html(self, md_content: str) -> str:
        """简单的Markdown转HTML"""
        html = md_content

        # 代码块
        html = re.sub(r"```(\w+)?\n(.*?)```", r"<pre><code>\2</code></pre>", html, flags=re.DOTALL)

        # 标题
        for i in range(6, 0, -1):
            html = re.sub(rf'^({"#"*i}) (.+)$', rf"<h{i}>\2</h{i}>", html, flags=re.MULTILINE)

        # 粗体
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

        # 斜体
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

        # 链接
        html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)

        # 列表
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        html = re.sub(r"(<li>.*</li>)", r"<ul>\1</ul>", html)

        # 表格
        lines = html.split("\n")
        new_lines = []
        in_table = False
        for line in lines:
            if line.strip().startswith("|") and "---" not in line:
                if not in_table:
                    in_table = True
                    new_lines.append('<table border="1">')
                cells = [c.strip() for c in line.strip().split("|") if c.strip()]
                row = "".join(f"<td>{c}</td>" for c in cells)
                new_lines.append(f"<tr>{row}</tr>")
            else:
                if in_table:
                    new_lines.append("</table>")
                    in_table = False
                new_lines.append(line)
        if in_table:
            new_lines.append("</table>")
        html = "\n".join(new_lines)

        # 换行
        html = html.replace("\n\n", "</p><p>")
        html = f"<p>{html}</p>"

        # 基础样式 - 暗黑主题
        style = f"""
        <style>
            body {{
                font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
                line-height: 1.7;
                color: {COLORS['text']};
                background-color: transparent;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {COLORS['primary']};
                margin-top: 24px;
                margin-bottom: 12px;
                font-weight: 600;
            }}
            h1 {{ font-size: 1.8em; border-bottom: 1px solid {COLORS['border']}; padding-bottom: 8px; }}
            h2 {{ font-size: 1.5em; }}
            h3 {{ font-size: 1.25em; }}
            code {{
                background: {COLORS['surface3']};
                color: #ff7b72;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 0.9em;
            }}
            pre {{
                background: {COLORS['surface2']};
                border: 1px solid {COLORS['border']};
                padding: 14px;
                border-radius: 6px;
                overflow-x: auto;
            }}
            pre code {{
                background: transparent;
                color: {COLORS['text']};
                padding: 0;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 12px 0;
            }}
            td, th {{
                border: 1px solid {COLORS['border']};
                padding: 10px 12px;
                text-align: left;
            }}
            th {{
                background: {COLORS['surface3']};
                color: {COLORS['primary']};
                font-weight: 600;
            }}
            tr:nth-child(even) {{
                background: {COLORS['surface']};
            }}
            tr:nth-child(odd) {{
                background: {COLORS['surface2']};
            }}
            a {{
                color: {COLORS['primary']};
                text-decoration: none;
            }}
            a:hover {{
                color: #6b9fff;
                text-decoration: underline;
            }}
            ul, ol {{
                padding-left: 24px;
            }}
            li {{
                margin: 6px 0;
            }}
            blockquote {{
                border-left: 4px solid {COLORS['border']};
                margin: 12px 0;
                padding: 8px 16px;
                background: {COLORS['surface2']};
                color: {COLORS['text_secondary']};
            }}
            hr {{
                border: none;
                border-top: 1px solid {COLORS['border']};
                margin: 20px 0;
            }}
            p {{
                margin: 10px 0;
            }}
            strong {{
                color: {COLORS['amber']};
            }}
            em {{
                color: #a5d6ff;
            }}
        </style>
        """

        return f"<!DOCTYPE html><html><head>{style}</head><body>{html}</body></html>"

    def refresh(self):
        """刷新课程列表"""
        self._load_courses()
        self._load_progress()
