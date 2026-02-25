"""
CAE-CLI 学习中心页面
对应 CLI 命令: cae-cli learn
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QLineEdit,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon

from ..theme import CAETheme


class LearnPage(QWidget):
    """学习中心页面 - 对应 cae-cli learn 命令"""

    # 信号
    course_selected = Signal(str)  # 课程被选中
    chat_requested = Signal(str)  # AI问答请求，参数为模式

    def __init__(self):
        super().__init__()
        self.current_course = None
        self._init_ui()
        self._load_courses()

    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ===== 左侧：课程列表 =====
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title = QLabel("📚 学习中心")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        left_layout.addWidget(title)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索课程...")
        self.search_input.textChanged.connect(self._on_search)
        left_layout.addWidget(self.search_input)

        # 课程列表
        self.course_list = QListWidget()
        self.course_list.itemClicked.connect(self._on_course_clicked)
        left_layout.addWidget(self.course_list)

        # AI问答按钮
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(5)

        # 模式选择
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["learning", "lifestyle", "mechanical", "default"])
        self.mode_combo.setToolTip("选择AI模式")
        mode_layout.addWidget(self.mode_combo)

        # AI问答按钮
        self.chat_btn = QPushButton("🤖 AI问答")
        self.chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.chat_btn.clicked.connect(self._on_chat_clicked)
        mode_layout.addWidget(self.chat_btn, 1)

        left_layout.addLayout(mode_layout)

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新课程")
        refresh_btn.clicked.connect(self._load_courses)
        left_layout.addWidget(refresh_btn)

        left_panel.setMinimumWidth(250)
        left_panel.setMaximumWidth(350)
        layout.addWidget(left_panel)

        # ===== 右侧：课程内容 =====
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 课程标题
        self.content_title = QLabel("欢迎使用学习中心")
        self.content_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        right_layout.addWidget(self.content_title)

        # 课程描述
        self.content_desc = QLabel("从左侧选择课程开始学习")
        self.content_desc.setStyleSheet("color: #666;")
        right_layout.addWidget(self.content_desc)

        # 内容显示
        self.content_browser = QTextBrowser()
        self.content_browser.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #fafafa;
            }
        """)
        right_layout.addWidget(self.content_browser)

        # 底部提示
        hint_label = QLabel("💡 提示: 使用 AI问答 可以向AI助手提问任何问题")
        hint_label.setStyleSheet("color: #888; padding: 5px;")
        right_layout.addWidget(hint_label)

        layout.addWidget(right_panel, 1)

    def _load_courses(self):
        """加载课程列表"""
        from sw_helper.learn import CourseManager

        self.course_list.clear()
        courses = CourseManager.get_all_courses()

        for course in courses:
            item = QListWidgetItem(f"📖 {course.name}")
            item.setData(Qt.ItemDataRole.UserRole, course.id)
            item.setToolTip(course.description)
            self.course_list.addItem(item)

    def _on_search(self, text):
        """搜索课程"""
        for i in range(self.course_list.count()):
            item = self.course_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _on_course_clicked(self, item):
        """课程被点击"""
        course_id = item.data(Qt.ItemDataRole.UserRole)
        self._show_course(course_id)

    def _show_course(self, course_id):
        """显示课程内容"""
        from sw_helper.learn import CourseManager, load_course_content

        course = CourseManager.get_course(course_id)
        if not course:
            return

        self.current_course = course_id
        self.content_title.setText(f"📖 {course.name}")
        self.content_desc.setText(course.description)

        # 加载内容
        content = load_course_content(course_id)

        # 转换为HTML显示
        html_content = self._markdown_to_html(content)
        self.content_browser.setHtml(html_content)

    def _markdown_to_html(self, md_content: str) -> str:
        """简单的Markdown转HTML"""
        import re

        html = md_content

        # 代码块
        html = re.sub(
            r'```(\w+)?\n(.*?)```',
            r'<pre><code>\2</code></pre>',
            html,
            flags=re.DOTALL
        )

        # 标题
        for i in range(6, 0, -1):
            html = re.sub(
                rf'^({"#"*i}) (.+)$',
                rf'<h{i}>\2</h{i}>',
                html,
                flags=re.MULTILINE
            )

        # 粗体
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # 斜体
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # 链接
        html = re.sub(
            r'\[(.+?)\]\((.+?)\)',
            r'<a href="\2">\1</a>',
            html
        )

        # 列表
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html)

        # 表格（简化）
        html = re.sub(
            r'\|(.+)\|',
            lambda m: '<tr>' + ''.join(f'<td>{c.strip()}</td>' for c in m.group(1).split('|') if c.strip()) + '</tr>',
            html
        )
        html = re.sub(r'<tr>.*</tr>', lambda m: f'<table border="1">{m.group()}</table>', html)

        # 换行
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'

        # 基础样式
        style = """
        <style>
            body { font-family: Microsoft YaHei, sans-serif; line-height: 1.6; }
            h1, h2, h3, h4, h5, h6 { color: #333; margin-top: 20px; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            table { border-collapse: collapse; width: 100%; }
            td, th { border: 1px solid #ddd; padding: 8px; }
            th { background: #f4f4f4; }
            a { color: #2196F3; }
        </style>
        """

        return f"<!DOCTYPE html><html><head>{style}</head><body>{html}</body></html>"

    def _on_chat_clicked(self):
        """点击AI问答按钮"""
        # 获取选中的模式
        mode = self.mode_combo.currentText()
        # 发出信号，让主窗口切换到AI聊天，并传递模式
        self.chat_requested.emit(mode)

    def refresh(self):
        """刷新课程列表"""
        self._load_courses()
