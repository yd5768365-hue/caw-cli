"""
CAE-CLI 终端可视化 - CLI 的图形外壳
核心永远是 CLI，GUI 只是可视化界面
"""

import os
import sys

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def get_cli_path():
    """获取CLI可执行文件路径"""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    search_paths = [
        os.path.join(base_dir, "cae-cli.exe"),
        os.path.join(base_dir, "dist", "cae-cli.exe"),
    ]

    for cli_path in search_paths:
        if os.path.exists(cli_path):
            return cli_path
    return search_paths[0]


CLI_EXE_PATH = get_cli_path()


class TerminalGUI(QMainWindow):
    """终端可视化 - CLI 的图形外壳"""

    def __init__(self):
        super().__init__()
        self._process = None
        self._init_ui()
        self._show_welcome()

    def _init_ui(self):
        self.setWindowTitle("MechDesign 终端")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)

        self.setStyleSheet("""
            QMainWindow { background-color: #0d1117; }
            QWidget { background-color: #0d1117; color: #8899aa; }
            QMenuBar { background-color: #161b22; color: #8899aa; border-bottom: 1px solid #30363d; }
            QMenuBar::item:selected { background-color: rgba(88, 166, 255, 0.15); }
            QMenu { background-color: #161b22; color: #8899aa; border: 1px solid #30363d; }
            QMenu::item:selected { background-color: rgba(88, 166, 255, 0.15); }
            QTextEdit { background-color: #0d1117; color: #8899aa; border: 1px solid #30363d; font-family: Consolas, monospace; font-size: 12px; }
            QLineEdit { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; padding: 8px; border-radius: 6px; }
            QLineEdit:focus { border: 1px solid #165DFF; }
            QPushButton { background-color: #238636; color: white; border: none; padding: 8px 20px; border-radius: 6px; }
            QPushButton:hover { background-color: #2ea043; }
            QLabel { color: #c9d1d9; }
        """)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 标题
        title = QLabel("MechDesign 终端")
        title.setStyleSheet("color: #f0a500; font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # CLI 状态 - 绿色表示就绪
        cli_status = (
            '<span style="color: #22c55e;">✓</span> CLI 就绪'
            if os.path.exists(CLI_EXE_PATH)
            else '<span style="color: #f44747;">✗</span> CLI 未找到'
        )
        self.status_label = QLabel(f'{cli_status} | <span style="color: #165DFF;">{CLI_EXE_PATH}</span>')
        self.status_label.setStyleSheet("font-size: 11px; padding: 5px;")
        layout.addWidget(self.status_label)

        # 终端输出
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text, 1)

        # 命令输入
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("输入命令，如: cae-cli --help")
        self.command_input.returnPressed.connect(self._execute_command)
        layout.addWidget(self.command_input)

        # 按钮
        btn_layout = QHBoxLayout()
        self.exec_btn = QPushButton("执行")
        self.exec_btn.clicked.connect(self._execute_command)
        btn_layout.addWidget(self.exec_btn)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(lambda: self.output_text.clear())
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self._create_menu_bar()

    def _create_menu_bar(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("刷新", self._show_welcome)
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)

        # 核心功能菜单
        core_menu = menubar.addMenu("核心功能")
        core_menu.addAction("帮助", lambda: self._run("cae-cli --help"))
        core_menu.addAction("系统信息", lambda: self._run("cae-cli info"))
        core_menu.addAction("版本", lambda: self._run("cae-cli version"))
        core_menu.addSeparator()
        core_menu.addAction("几何解析", lambda: self._run("cae-cli parse --help"))
        core_menu.addAction("网格分析", lambda: self._run("cae-cli analyze --help"))
        core_menu.addAction("材料查询", lambda: self._run("cae-cli material --help"))
        core_menu.addAction("报告生成", lambda: self._run("cae-cli report --help"))
        core_menu.addAction("参数优化", lambda: self._run("cae-cli optimize --help"))

        # AI 功能菜单
        ai_menu = menubar.addMenu("AI 功能")
        ai_menu.addAction("AI 助手", lambda: self._run("cae-cli ai --help"))
        ai_menu.addAction("学习模式", lambda: self._run("cae-cli learn --help"))
        ai_menu.addAction("交互聊天", lambda: self._run("cae-cli chat --help"))

        # 系统菜单
        sys_menu = menubar.addMenu("系统")
        sys_menu.addAction("配置管理", lambda: self._run("cae-cli config --list"))
        sys_menu.addAction("交互模式", lambda: self._run("cae-cli interactive --help"))
        sys_menu.addAction("知识库", lambda: self._run("cae-cli handbook --help"))

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        help_menu.addAction("关于", self._show_about)

    def _show_welcome(self):
        """显示欢迎信息"""
        self.output_text.setHtml("""
<h2 style="color: #f0a500;">欢迎使用 CAE-CLI 终端</h2>
<p style="color: #8899aa;">GUI 是 CLI 的图形外壳，核心永远是 CLI 命令。</p>

<h3 style="color: #f0a500;">使用方式：</h3>
<ul style="color: #8899aa;">
<li>在下方输入框直接输入 CLI 命令</li>
<li>或通过菜单选择功能</li>
</ul>

<h3 style="color: #f0a500;">常用命令：</h3>
<pre style="color: #8899aa;">
<span style="color: #165DFF;">cae-cli --help</span>          <span style="color: #6a9955;"># 查看帮助</span>
<span style="color: #165DFF;">cae-cli info</span>            <span style="color: #6a9955;"># 系统信息</span>
<span style="color: #165DFF;">cae-cli parse --help</span>    <span style="color: #6a9955;"># 几何解析</span>
<span style="color: #165DFF;">cae-cli analyze --help</span>  <span style="color: #6a9955;"># 网格分析</span>
<span style="color: #165DFF;">cae-cli material --help</span> <span style="color: #6a9955;"># 材料查询</span>
<span style="color: #165DFF;">cae-cli report --help</span>   <span style="color: #6a9955;"># 报告生成</span>
<span style="color: #165DFF;">cae-cli ai --help</span>       <span style="color: #6a9955;"># AI 助手</span>
<span style="color: #165DFF;">cae-cli learn --help</span>    <span style="color: #6a9955;"># 学习模式</span>
</pre>
        """)

    def _show_about(self):
        QMessageBox.about(self, "关于", "CAE-CLI 终端 v1.0.0\n\n" "CLI 的图形外壳\n\n" "核心永远是 CLI 命令")

    def _execute_command(self):
        """执行命令（从输入框）"""
        cmd = self.command_input.text().strip()
        if cmd:
            self._run(cmd)
            self.command_input.clear()

    def _run(self, cmd: str):
        """运行 CLI 命令"""
        if not os.path.exists(CLI_EXE_PATH):
            self.output_text.append(
                f'<span style="color: #f44747;">[错误]</span> <span style="color: #8899aa;">CLI 未找到: {CLI_EXE_PATH}</span>\n'
            )
            return

        # 命令提示符 - 蓝色
        self.output_text.append(f'<span style="color: #165DFF;">$</span> <span style="color: #8899aa;">{cmd}</span>')
        self.output_text.append("-" * 40)
        self.exec_btn.setEnabled(False)
        self.status_label.setText("⏳ 执行中...")

        # 创建进程
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)

        # 分割命令
        cmd_list = cmd.split()

        # 替换 cae-cli 为实际路径
        if cmd_list and cmd_list[0] in ("cae-cli", "cae"):
            cmd_list[0] = CLI_EXE_PATH

        self._process.start(cmd_list[0], cmd_list[1:])

    def _on_stdout(self):
        data = self._process.readAllStandardOutput()
        self.output_text.append(bytes(data).decode("utf-8", errors="replace"))

    def _on_stderr(self):
        data = self._process.readAllStandardError()
        self.output_text.append(bytes(data).decode("utf-8", errors="replace"))

    def _on_finished(self, exitCode, exitStatus):
        self.output_text.append("")
        if exitCode != 0:
            self.output_text.append(f'<span style="color: #f44747;">[退出码: {exitCode}]</span>')
        else:
            self.output_text.append('<span style="color: #22c55e;">[完成]</span>')
        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())
        self.exec_btn.setEnabled(True)
        self.status_label.setText('<span style="color: #22c55e;">✓</span> 就绪')


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MechDesign")
    app.setApplicationVersion("1.0.0")
    window = TerminalGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
