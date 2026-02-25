"""
CAE-CLI 学习中心页面
对应 CLI 命令: cae-cli learn
支持课程浏览、测验、学习进度跟踪
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
    QProgressBar,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
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
        self.current_quiz = None
        self.quiz_score = 0
        self.quiz_total = 0
        self._init_ui()
        self._load_courses()
        self._load_progress()

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

        # 学习进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        left_layout.addWidget(self.progress_bar)

        # 进度标签
        self.progress_label = QLabel("学习进度: 0%")
        self.progress_label.setStyleSheet("color: #666; font-size: 12px;")
        left_layout.addWidget(self.progress_label)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索课程...")
        self.search_input.textChanged.connect(self._on_search)
        left_layout.addWidget(self.search_input)

        # 课程分类
        self.category_combo = QComboBox()
        self.category_combo.addItems(["全部", "材料力学", "理论力学", "有限元", "机械设计"])
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        left_layout.addWidget(self.category_combo)

        # 课程列表
        self.course_list = QListWidget()
        self.course_list.itemClicked.connect(self._on_course_clicked)
        left_layout.addWidget(self.course_list)

        # AI问答和测验按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)

        # 模式选择
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["learning", "lifestyle", "mechanical", "default"])
        self.mode_combo.setToolTip("选择AI模式")
        btn_layout.addWidget(self.mode_combo)

        # AI问答按钮
        self.chat_btn = QPushButton("🤖 AI问答")
        self.chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.chat_btn.clicked.connect(self._on_chat_clicked)
        btn_layout.addWidget(self.chat_btn)

        # 测验按钮
        self.quiz_btn = QPushButton("📝 测验")
        self.quiz_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.quiz_btn.clicked.connect(self._on_start_quiz)
        btn_layout.addWidget(self.quiz_btn)

        left_layout.addLayout(btn_layout)

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新课程")
        refresh_btn.clicked.connect(self._load_courses)
        left_layout.addWidget(refresh_btn)

        left_panel.setMinimumWidth(280)
        left_panel.setMaximumWidth(380)
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

        # 标签页切换
        self.tab_widget = QWidget()
        tab_layout = QVBoxLayout(self.tab_widget)

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
        tab_layout.addWidget(self.content_browser)

        # 测验区域（初始隐藏）
        self.quiz_widget = QWidget()
        quiz_layout = QVBoxLayout(self.quiz_widget)

        self.quiz_question = QLabel("点击「开始测验」按钮")
        self.quiz_question.setWordWrap(True)
        self.quiz_question.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        quiz_layout.addWidget(self.quiz_question)

        # 选项按钮组
        self.option_group = QButtonGroup(self)
        self.option_buttons = []
        for i in range(4):
            rb = QRadioButton()
            rb.setVisible(False)
            self.option_group.addButton(rb, i)
            self.option_buttons.append(rb)
            quiz_layout.addWidget(rb)

        # 提交按钮
        self.submit_quiz_btn = QPushButton("提交答案")
        self.submit_quiz_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.submit_quiz_btn.clicked.connect(self._on_submit_quiz)
        self.submit_quiz_btn.setVisible(False)
        quiz_layout.addWidget(self.submit_quiz_btn)

        # 测验结果
        self.quiz_result = QLabel("")
        self.quiz_result.setStyleSheet("font-size: 14px; padding: 10px;")
        quiz_layout.addWidget(self.quiz_result)

        self.quiz_widget.setVisible(False)
        tab_layout.addWidget(self.quiz_widget)

        # 底部提示
        hint_label = QLabel("💡 提示: 学习完课程后可以做测验检验学习效果")
        hint_label.setStyleSheet("color: #888; padding: 5px;")
        tab_layout.addWidget(hint_label)

        # 切换按钮
        switch_layout = QHBoxLayout()
        self.view_content_btn = QPushButton("📖 课程内容")
        self.view_content_btn.setStyleSheet("""
            QPushButton { background-color: #ddd; padding: 8px; border-radius: 3px; }
            QPushButton:pressed { background-color: #ccc; }
        """)
        self.view_content_btn.clicked.connect(self._show_content_view)
        switch_layout.addWidget(self.view_content_btn)

        self.view_quiz_btn = QPushButton("📝 测验")
        self.view_quiz_btn.setStyleSheet("""
            QPushButton { background-color: #ddd; padding: 8px; border-radius: 3px; }
            QPushButton:pressed { background-color: #ccc; }
        """)
        self.view_quiz_btn.clicked.connect(self._show_quiz_view)
        switch_layout.addWidget(self.view_quiz_btn)
        tab_layout.addLayout(switch_layout)

        right_layout.addWidget(self.tab_widget, 1)

        layout.addWidget(right_panel, 1)

    def _load_courses(self):
        """加载课程列表"""
        try:
            from sw_helper.learn import CourseManager

            self.course_list.clear()
            courses = CourseManager.get_all_courses()

            for course in courses:
                item = QListWidgetItem(f"📖 {course.name}")
                item.setData(Qt.ItemDataRole.UserRole, course.id)
                item.setToolTip(course.description)
                self.course_list.addItem(item)

        except Exception as e:
            # 如果学习模块不可用，显示默认课程
            self._load_default_courses()

    def _load_default_courses(self):
        """加载默认课程（当learn模块不可用时）"""
        self.course_list.clear()
        default_courses = [
            ("materials", "材料力学", "材料力学基础知识"),
            ("mechanics", "理论力学", "理论力学基础概念"),
            ("fem", "有限元基础", "有限元分析方法"),
            ("fasteners", "紧固件", "机械紧固件知识"),
            ("tolerances", "公差配合", "公差与配合知识"),
        ]

        for course_id, name, desc in default_courses:
            item = QListWidgetItem(f"📖 {name}")
            item.setData(Qt.ItemDataRole.UserRole, course_id)
            item.setToolTip(desc)
            self.course_list.addItem(item)

    def _load_progress(self):
        """加载学习进度"""
        try:
            from sw_helper.learning.progress_tracker import get_progress_tracker

            tracker = get_progress_tracker()
            # 获取总体进度
            stats = tracker.get_statistics()
            progress = stats.get("completion_rate", 0) * 100
            self.progress_bar.setValue(int(progress))
            self.progress_label.setText(f"学习进度: {int(progress)}%")

        except Exception:
            # 如果进度跟踪不可用，使用默认进度
            self.progress_bar.setValue(0)
            self.progress_label.setText("学习进度: 0%")

    def _on_search(self, text):
        """搜索课程"""
        for i in range(self.course_list.count()):
            item = self.course_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _on_category_changed(self, category):
        """按分类筛选课程"""
        # 简化实现：实际应该按分类过滤
        self._on_search(self.search_input.text())

    def _on_course_clicked(self, item):
        """课程被点击"""
        course_id = item.data(Qt.ItemDataRole.UserRole)
        self._show_course(course_id)

    def _show_course(self, course_id):
        """显示课程内容"""
        self.current_course = course_id

        try:
            from sw_helper.learn import CourseManager, load_course_content

            course = CourseManager.get_course(course_id)
            if not course:
                self._show_default_content(course_id)
                return

            self.content_title.setText(f"📖 {course.name}")
            self.content_desc.setText(course.description)

            # 加载内容
            content = load_course_content(course_id)
            html_content = self._markdown_to_html(content)
            self.content_browser.setHtml(html_content)

        except Exception:
            self._show_default_content(course_id)

        # 显示内容视图
        self._show_content_view()

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
            "fasteners": """# 紧固件

## 螺栓连接
- **等级**: 4.6, 8.8, 10.9, 12.9
- **预紧力**: 保证连接紧密性

## 螺纹参数
- **大径**: 螺纹外径
- **小径**: 螺纹内径
- **中径**: 螺纹平均直径
- **螺距**: 相邻牙型对应点距离
""",
            "tolerances": """# 公差配合

## 基本概念
- **公差**: 允许尺寸变动量
- **配合**: 孔与轴的松紧关系

## 配合类型
- **间隙配合**: 孔 > 轴
- **过盈配合**: 孔 < 轴
- **过渡配合**: 可能间隙或过盈

## 公差等级
IT01, IT0, IT1...IT18
数字越大，公差越大
""",
        }

        content = content_map.get(course_id, "# 课程内容\n\n正在开发中...")
        self.content_title.setText(f"📖 {course_id}")
        self.content_desc.setText("")
        self.content_browser.setHtml(self._markdown_to_html(content))

    def _show_content_view(self):
        """显示课程内容视图"""
        self.content_browser.setVisible(True)
        self.quiz_widget.setVisible(False)
        self.view_content_btn.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; padding: 8px; border-radius: 3px; }
        """)
        self.view_quiz_btn.setStyleSheet("""
            QPushButton { background-color: #ddd; padding: 8px; border-radius: 3px; }
        """)

    def _show_quiz_view(self):
        """显示测验视图"""
        self.content_browser.setVisible(False)
        self.quiz_widget.setVisible(True)
        self.view_content_btn.setStyleSheet("""
            QPushButton { background-color: #ddd; padding: 8px; border-radius: 3px; }
        """)
        self.view_quiz_btn.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; padding: 8px; border-radius: 3px; }
        """)

        # 重置测验状态
        self.current_quiz = None
        self.quiz_question.setText("点击「测验」按钮开始测验")
        for btn in self.option_buttons:
            btn.setVisible(False)
        self.submit_quiz_btn.setVisible(False)
        self.quiz_result.setText("")

    def _on_start_quiz(self):
        """开始测验"""
        if not self.current_course:
            QMessageBox.information(self, "提示", "请先选择一个课程")
            return

        try:
            from sw_helper.learning.quiz_manager import get_quiz_manager

            quiz_mgr = get_quiz_manager()
            # 生成测验（简化版本）
            quiz = quiz_mgr.generate_quiz(self.current_course, 3)

            if quiz:
                self._display_quiz(quiz)
                self._show_quiz_view()
            else:
                QMessageBox.information(self, "提示", "暂无测验题目")

        except Exception:
            # 如果测验模块不可用，显示示例测验
            self._show_sample_quiz()
            self._show_quiz_view()

    def _show_sample_quiz(self):
        """显示示例测验"""
        sample_quiz = {
            "question": "材料力学中，应力的单位是什么？",
            "options": ["N", "Pa", "kg", "m"],
            "correct": 1,  # 正确答案是 Pa
        }
        self.current_quiz = sample_quiz
        self.quiz_question.setText(sample_quiz["question"])
        for i, option in enumerate(sample_quiz["options"]):
            self.option_buttons[i].setText(option)
            self.option_buttons[i].setVisible(True)
            self.option_buttons[i].setChecked(False)
        self.submit_quiz_btn.setVisible(True)

    def _display_quiz(self, quiz):
        """显示测验题目"""
        self.current_quiz = quiz
        self.quiz_question.setText(quiz.get("question", ""))

        options = quiz.get("options", [])
        for i in range(4):
            if i < len(options):
                self.option_buttons[i].setText(options[i])
                self.option_buttons[i].setVisible(True)
                self.option_buttons[i].setChecked(False)
            else:
                self.option_buttons[i].setVisible(False)

        self.submit_quiz_btn.setVisible(True)

    def _on_submit_quiz(self):
        """提交测验答案"""
        if not self.current_quiz:
            return

        # 获取选中的答案
        selected_id = self.option_group.checkedId()
        if selected_id == -1:
            QMessageBox.warning(self, "提示", "请选择一个答案")
            return

        correct = self.current_quiz.get("correct", 0)
        self.quiz_total += 1

        if selected_id == correct:
            self.quiz_score += 1
            self.quiz_result.setText("✅ 回答正确！")
            self.quiz_result.setStyleSheet("color: green; font-size: 14px; font-weight: bold;")
        else:
            self.quiz_result.setText(f"❌ 回答错误，正确答案是: {self.current_quiz['options'][correct]}")
            self.quiz_result.setStyleSheet("color: red; font-size: 14px;")

        # 更新进度
        self._update_progress()

    def _update_progress(self):
        """更新学习进度"""
        try:
            from sw_helper.learning.progress_tracker import get_progress_tracker

            tracker = get_progress_tracker()
            # 记录测验完成
            if self.current_course:
                tracker.complete_lesson(self.current_course)

            # 获取新进度
            stats = tracker.get_statistics()
            progress = stats.get("completion_rate", 0) * 100
            self.progress_bar.setValue(int(progress))
            self.progress_label.setText(f"学习进度: {int(progress)}%")

        except Exception:
            # 简单本地进度
            progress = int((self.quiz_score / max(self.quiz_total, 1)) * 100)
            self.progress_bar.setValue(progress)
            self.progress_label.setText(f"测验正确率: {progress}%")

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

        # 表格
        lines = html.split('\n')
        new_lines = []
        in_table = False
        for line in lines:
            if line.strip().startswith('|') and '---' not in line:
                if not in_table:
                    in_table = True
                    new_lines.append('<table border="1">')
                cells = [c.strip() for c in line.strip().split('|') if c.strip()]
                row = ''.join(f'<td>{c}</td>' for c in cells)
                new_lines.append(f'<tr>{row}</tr>')
            else:
                if in_table:
                    new_lines.append('</table>')
                    in_table = False
                new_lines.append(line)
        if in_table:
            new_lines.append('</table>')
        html = '\n'.join(new_lines)

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
            table { border-collapse: collapse; width: 100%; margin: 10px 0; }
            td, th { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f4f4f4; }
            a { color: #2196F3; }
            ul { padding-left: 20px; }
        </style>
        """

        return f"<!DOCTYPE html><html><head>{style}</head><body>{html}</body></html>"

    def _on_chat_clicked(self):
        """点击AI问答按钮"""
        mode = self.mode_combo.currentText()
        self.chat_requested.emit(mode)

    def refresh(self):
        """刷新课程列表"""
        self._load_courses()
        self._load_progress()
