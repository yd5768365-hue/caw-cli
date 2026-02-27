"""
CAE-CLI Web界面 - PySide6 + QWebEngineView
"""

import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QUrl, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def get_cli_path():
    """获取CLI可执行文件路径 - 兼容打包和开发模式"""
    if getattr(sys, "frozen", False):
        # 打包后：exe 同目录
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发时：项目根目录 (caw-cli/)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 搜索路径列表（按优先级）
    search_paths = [
        os.path.join(base_dir, "cae-cli.exe"),
        os.path.join(base_dir, "build", "cae-cli", "cae-cli.exe"),
        os.path.join(base_dir, "dist", "cae-cli", "cae-cli.exe"),
        # 往上一级目录搜索
        os.path.join(base_dir, "..", "dist", "cae-cli", "cae-cli.exe"),
        os.path.join(base_dir, "..", "build", "cae-cli", "cae-cli.exe"),
        os.path.join(base_dir, "..", "cae-cli.exe"),
    ]

    for cli_path in search_paths:
        if os.path.exists(cli_path):
            return cli_path

    return search_paths[0]


CLI_EXE_PATH = get_cli_path()


class CLIBridge(QObject):
    """CLI桥接器 - 允许JavaScript调用Python执行命令"""

    # 信号：命令执行完成
    commandFinished = Signal(str)

    # 信号：命令执行中状态
    commandStarted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = None
        self._current_output = ""

    @Slot(str)
    def runCommand(self, cmd: str):
        """从JavaScript接收命令并执行"""
        print(f"[Bridge] runCommand called: {cmd}")
        self.commandStarted.emit()
        self._current_output = ""

        # 创建QProcess执行命令
        self._process = QProcess(self)
        # 直接使用系统环境，不设置特殊环境变量

        # 连接信号
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)

        # 分割命令
        cmd_list = cmd.split()

        # 替换cae-cli为实际路径
        if cmd_list and (cmd_list[0] == "cae-cli" or cmd_list[0] == "cae"):
            if os.path.exists(CLI_EXE_PATH):
                cmd_list[0] = CLI_EXE_PATH
            else:
                self.commandFinished.emit(f"[错误] 找不到CLI: {CLI_EXE_PATH}")
                return

        # 启动进程
        self._process.start(cmd_list[0], cmd_list[1:])

    def _on_stdout(self):
        """标准输出"""
        data = self._process.readAllStandardOutput()
        self._current_output += bytes(data).decode("utf-8", errors="replace")

    def _on_stderr(self):
        """标准错误"""
        data = self._process.readAllStandardError()
        self._current_output += bytes(data).decode("utf-8", errors="replace")

    def _on_finished(self, exitCode, exitStatus):
        """进程结束"""
        if exitCode == 0:
            output = self._current_output if self._current_output else "命令执行成功"
            self.commandFinished.emit(output)
        else:
            error = self._current_output if self._current_output else "命令执行失败"
            self.commandFinished.emit(f"[错误] {error}")


class WebGUIWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._bridge = CLIBridge(self)
        self._init_ui()
        self._load_homepage()

    def _init_ui(self):
        self.setWindowTitle("MechDesign 简洁界面")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self.setStyleSheet("""
            QMainWindow { background-color: #0d1117; }
            QMenuBar { background-color: #161b22; color: #c9d1d9; border-bottom: 1px solid #30363d; }
            QMenuBar::item:selected { background-color: #21262d; }
            QMenu { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; }
            QMenu::item:selected { background-color: #21262d; }
        """)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧：Web视图（主页和聊天）
        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()

        # 配置Web设置
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)

        # 设置WebChannel
        self._channel = QWebChannel(self)
        self._channel.registerObject("bridge", self._bridge)
        self.web_view.page().setWebChannel(self._channel)

        left_layout.addWidget(self.web_view)

        # 右侧：命令面板（简化版，窄一些）
        right_widget = QWidget()
        right_widget.setMinimumWidth(400)
        right_widget.setMaximumWidth(500)
        right_widget.setStyleSheet("background-color: #0d1117;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(10)

        # 标题
        title_label = QLabel("终端输出")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px; color: #165DFF;")
        right_layout.addWidget(title_label)

        # CLI状态
        cli_exists = "✅" if os.path.exists(CLI_EXE_PATH) else "❌"
        cli_path_label = QLabel(f"{cli_exists} CLI: {os.path.basename(CLI_EXE_PATH)}")
        cli_path_label.setStyleSheet("color: #8b949e; font-size: 11px; padding: 5px;")
        cli_path_label.setWordWrap(True)
        right_layout.addWidget(cli_path_label)

        # 输出文本框 - 占据更大空间
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(
            "QTextEdit { background-color: #0d1117; color: #c9d1d9; font-family: 'Consolas', monospace; font-size: 12px; border: 1px solid #30363d; padding: 10px; }"
        )
        right_layout.addWidget(self.output_text, 3)  # 占据更多空间

        # 状态栏
        self.status_label = QLabel("✅ 就绪")
        self.status_label.setStyleSheet("padding: 6px; font-size: 12px; color: #8b949e;")
        right_layout.addWidget(self.status_label)

        main_layout.addWidget(self.left_widget, 3)  # 左侧占 3 份
        main_layout.addWidget(right_widget, 1)  # 右侧占 1 份

        self._create_menu_bar()

        # 连接bridge信号
        self._bridge.commandStarted.connect(self._on_command_started)
        self._bridge.commandFinished.connect(self._on_command_finished)

    def _on_command_started(self):
        """命令开始执行"""
        self.status_label.setText('<span style="color: #f0a500;">◐</span> 正在执行命令...')
        self.execute_btn.setEnabled(False)

    def _on_command_finished(self, output: str):
        """命令执行完成"""
        # 使用 HTML 格式化输出 - 灰色文字
        self.output_text.append(f'<span style="color: #8899aa;">{output}</span>')
        self.output_text.append(f"<span style=\"color: #30363d;\">{'─' * 60}</span>")
        self.output_text.append("")

        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())

        self.execute_btn.setEnabled(True)
        self.status_label.setText('<span style="color: #22c55e;">✓</span> 命令执行完成')

    def _create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("QMenuBar { background-color: #161b22; color: #c9d1d9; }")

        file_menu = menubar.addMenu("文件(&F)")
        refresh_action = QAction("刷新(&R)", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.web_view.reload)
        file_menu.addAction(refresh_action)
        file_menu.addSeparator()
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        nav_menu = menubar.addMenu("导航(&N)")
        home_action = QAction("🏠 主页", self)
        home_action.triggered.connect(self._load_homepage)
        nav_menu.addAction(home_action)
        nav_menu.addSeparator()
        back_action = QAction("⬅ 后退", self)
        back_action.triggered.connect(self.web_view.back)
        nav_menu.addAction(back_action)
        forward_action = QAction("➡ 前进", self)
        forward_action.triggered.connect(self.web_view.forward)
        nav_menu.addAction(forward_action)

        tools_menu = menubar.addMenu("工具(&T)")
        geometry_action = QAction("📐 几何解析", self)
        geometry_action.triggered.connect(lambda: self._fill_command("cae-cli parse --help"))
        tools_menu.addAction(geometry_action)
        mesh_action = QAction("🔲 网格分析", self)
        mesh_action.triggered.connect(lambda: self._fill_command("cae-cli analyze --help"))
        tools_menu.addAction(mesh_action)
        material_action = QAction("🔧 材料查询", self)
        material_action.triggered.connect(lambda: self._fill_command("cae-cli material --help"))
        tools_menu.addAction(material_action)
        optimize_action = QAction("⚡ 参数优化", self)
        optimize_action.triggered.connect(lambda: self._fill_command("cae-cli optimize --help"))
        tools_menu.addAction(optimize_action)
        tools_menu.addSeparator()
        ai_action = QAction("🤖 AI助手", self)
        ai_action.triggered.connect(lambda: self._fill_command("cae-cli ai --help"))
        tools_menu.addAction(ai_action)
        workflow_action = QAction("🔄 CAE工作流", self)
        workflow_action.triggered.connect(lambda: self._fill_command("cae-cli workflow --help"))
        tools_menu.addAction(workflow_action)
        kb_action = QAction("📚 知识库", self)
        kb_action.triggered.connect(lambda: self._fill_command("cae-cli handbook --help"))
        tools_menu.addAction(kb_action)

        help_menu = menubar.addMenu("帮助(&H)")
        about_action = QAction("ℹ️  关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _fill_command(self, cmd: str):
        """填入命令到输入框"""
        self.command_input.setText(cmd)
        self.status_label.setText(f"📝 已填入命令: {cmd}，按回车执行")

    def _load_homepage(self):
        # 加载HTML文件
        html_file = Path(__file__).parent / "cae_ui.html"
        if html_file.exists():
            self.web_view.setUrl(QUrl.fromLocalFile(str(html_file.absolute())))
            print(f"[GUI] Loaded HTML file: {html_file}")
        else:
            # 回退到内联HTML
            html = self._get_default_html()
            self.web_view.setHtml(html)
            print("[GUI] Fallback to inline HTML")

    def _execute_command(self):
        """执行命令（从输入框）"""
        command_str = self.command_input.text().strip()
        if not command_str:
            return

        if not os.path.exists(CLI_EXE_PATH):
            self.output_text.append(
                f'<span style="color: #f44747;">[错误]</span> <span style="color: #8899aa;">找不到CLI: {CLI_EXE_PATH}</span>'
            )
            return

        self._bridge.runCommand(command_str)

    def _show_about(self):
        QMessageBox.about(self, "关于 MechDesign", "MechDesign 现代化界面 v0.2.0\n\n基于 PySide6 + QWebEngineView")

    def _get_default_html(self) -> str:
        """简化版HTML - 简洁界面"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MechDesign</title>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --border-color: #30363d;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --accent-blue: #165DFF;
            --accent-purple: #FF7D00;
            --accent-green: #238636;
            --gradient-primary: linear-gradient(135deg, #165DFF 0%, #FF7D00 100%);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
        }
        .header {
            background: var(--bg-secondary);
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
        }
        .logo { font-size: 18px; font-weight: bold; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .nav { display: flex; gap: 8px; }
        .nav-item {
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            color: var(--text-secondary);
            font-size: 14px;
        }
        .nav-item:hover { background: rgba(88, 166, 255, 0.1); color: var(--accent-blue); }
        .nav-item.active { background: var(--gradient-primary); color: white; }
        .main { padding: 20px; height: calc(100vh - 50px); overflow-y: auto; }
        .modules { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; max-width: 1200px; margin: 0 auto; }
        .module-card {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
            cursor: pointer;
            transition: 0.2s;
            text-align: center;
        }
        .module-card:hover { border-color: var(--accent-blue); transform: translateY(-3px); }
        .module-icon { font-size: 32px; margin-bottom: 10px; }
        .module-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
        .module-desc { font-size: 12px; color: var(--text-secondary); }
        /* 聊天页面 */
        #chat-page { display: none; height: calc(100vh - 50px); }
        .chat-full {
            display: flex;
            flex-direction: column;
            height: 100%;
            background: var(--bg-secondary);
            border-radius: 12px;
            margin: 20px;
            border: 1px solid var(--border-color);
        }
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .chat-message {
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 70%;
            font-size: 14px;
            line-height: 1.5;
        }
        .chat-message.user {
            background: var(--gradient-primary);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        .chat-message.ai {
            background: var(--bg-primary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            border-bottom-left-radius: 4px;
        }
        .chat-input-area {
            padding: 16px;
            background: var(--bg-primary);
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 12px;
        }
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 14px;
        }
        .chat-input:focus { outline: none; border-color: var(--accent-blue); }
        .chat-send-btn {
            padding: 12px 24px;
            background: var(--gradient-primary);
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-size: 14px;
        }
        .chat-send-btn:hover { opacity: 0.9; }
        .loading { color: var(--text-secondary); font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">MechDesign v1.0.0</div>
        <div class="nav">
            <div class="nav-item active" onclick="showPage('home')">首页</div>
            <div class="nav-item" onclick="showPage('chat')">AI 聊天</div>
        </div>
    </div>
    <div class="main">
        <div id="home-page">
            <div class="modules">
                <div class="module-card" onclick="bridge.runCommand('cae-cli parse --help')">
                    <div class="module-icon">📐</div>
                    <div class="module-title">几何解析</div>
                    <div class="module-desc">解析 STEP/STL/IGES</div>
                </div>
                <div class="module-card" onclick="bridge.runCommand('cae-cli analyze --help')">
                    <div class="module-icon">🔲</div>
                    <div class="module-title">网格分析</div>
                    <div class="module-desc">分析网格质量</div>
                </div>
                <div class="module-card" onclick="bridge.runCommand('cae-cli material --help')">
                    <div class="module-icon">🔧</div>
                    <div class="module-title">材料查询</div>
                    <div class="module-desc">GB/T 材料库</div>
                </div>
                <div class="module-card" onclick="showPage('chat')">
                    <div class="module-icon">🤖</div>
                    <div class="module-title">AI 助手</div>
                    <div class="module-desc">智能问答</div>
                </div>
            </div>
        </div>
        <div id="chat-page">
            <div class="chat-full">
                <div class="chat-messages" id="chat-messages">
                    <div class="chat-message ai">
                        你好！我是 CAE-CLI AI 助手。<br><br>
                        可以帮助你解答：<br>
                        • CAD/CAE 问题<br>
                        • 材料选型建议<br>
                        • 网格划分知识<br>
                        • 机械设计问题<br><br>
                        请在下方输入你的问题...
                    </div>
                </div>
                <div class="chat-input-area">
                    <input type="text" class="chat-input" id="chat-input"
                           placeholder="输入问题，按回车发送..."
                           onkeypress="if(event.key==='Enter')sendChat()">
                    <button class="chat-send-btn" onclick="sendChat()">发送</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        var bridge = null;
        new QWebChannel(qtwebchannelCallbacks, function(channel) { bridge = channel.objects.bridge; });
        function qtwebchannelCallbacks(registry) {}
        function showPage(pageId) {
            document.getElementById('home-page').style.display = pageId === 'home' ? 'block' : 'none';
            document.getElementById('chat-page').style.display = pageId === 'chat' ? 'block' : 'none';
            document.querySelectorAll('.nav-item').forEach(function(item) {
                item.classList.remove('active');
                if(item.textContent.includes(pageId === 'home' ? '首页' : '聊天')) item.classList.add('active');
            });
        }
        function sendChat() {
            var input = document.getElementById('chat-input');
            var msg = input.value.trim();
            if (!msg) return;
            var messages = document.getElementById('chat-messages');
            messages.innerHTML += '<div class="chat-message user">' + msg + '</div>';
            messages.innerHTML += '<div class="chat-message ai loading">正在思考...</div>';
            input.value = '';
            messages.scrollTop = messages.scrollHeight;
            if (bridge) bridge.runCommand('cae-cli chat "' + msg + '"');
        }
    </script>
</body>
</html>"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MechDesign</title>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* ===== CSS Variables ===== */
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-card: rgba(22, 27, 34, 0.8);
            --bg-glass: rgba(22, 27, 34, 0.7);
            --border-color: #30363d;
            --border-hover: #165DFF;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --accent-blue: #165DFF;
            --accent-purple: #FF7D00;
            --accent-green: #238636;
            --accent-green-hover: #2ea043;
            --gradient-primary: linear-gradient(135deg, #165DFF 0%, #FF7D00 100%);
            --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.3);
            --shadow-hover: 0 8px 40px rgba(88, 166, 255, 0.15);
            --radius-sm: 6px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --transition-fast: 0.2s ease;
            --transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* ===== Base Styles ===== */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ===== Background Effects ===== */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(ellipse at 20% 20%, rgba(88, 166, 255, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(163, 113, 247, 0.08) 0%, transparent 50%),
                linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            z-index: -1;
            pointer-events: none;
        }

        /* ===== Glassmorphism Header ===== */
        .header {
            background: var(--bg-glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }

        .logo {
            font-size: 24px;
            font-weight: 700;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .logo-icon {
            width: 36px;
            height: 36px;
            background: var(--gradient-primary);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            -webkit-text-fill-color: white;
        }

        /* ===== Navigation ===== */
        .nav {
            display: flex;
            gap: 8px;
            background: rgba(0, 0, 0, 0.2);
            padding: 4px;
            border-radius: var(--radius-md);
        }

        .nav-item {
            padding: 10px 18px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 500;
            transition: var(--transition-smooth);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .nav-item:hover {
            background: rgba(88, 166, 255, 0.1);
            color: var(--accent-blue);
        }

        .nav-item.active {
            background: var(--gradient-primary);
            color: white;
            box-shadow: 0 4px 15px rgba(88, 166, 255, 0.3);
        }

        /* ===== Main Container ===== */
        .main-content {
            padding: 24px;
            max-width: 1400px;
            margin: 0 auto;
        }

        /* ===== Quick Actions Bar ===== */
        .quick-actions {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }

        .quick-action-btn {
            padding: 10px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: var(--transition-smooth);
        }

        .quick-action-btn:hover {
            background: rgba(88, 166, 255, 0.1);
            border-color: var(--accent-blue);
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
        }

        .quick-action-btn i { color: var(--accent-blue); }

        /* ===== Page Title ===== */
        .page-title {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .page-title i {
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* ===== Cards Grid ===== */
        .modules {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }

        .module-card {
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            padding: 24px;
            border: 1px solid var(--border-color);
            cursor: pointer;
            transition: var(--transition-smooth);
            position: relative;
            overflow: hidden;
        }

        .module-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-primary);
            transform: scaleX(0);
            transition: var(--transition-smooth);
        }

        .module-card:hover {
            transform: translateY(-6px);
            border-color: var(--accent-blue);
            box-shadow: var(--shadow-hover);
        }

        .module-card:hover::before {
            transform: scaleX(1);
        }

        .module-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }

        .module-icon {
            width: 52px;
            height: 52px;
            background: rgba(88, 166, 255, 0.1);
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            transition: var(--transition-smooth);
        }

        .module-card:hover .module-icon {
            background: var(--gradient-primary);
            transform: scale(1.1);
        }

        .module-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .module-desc {
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 16px;
            line-height: 1.5;
        }

        .module-cmd {
            padding: 8px 14px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: var(--radius-sm);
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            color: var(--accent-blue);
            display: inline-block;
        }

        /* ===== Buttons ===== */
        .action-btn {
            padding: 12px 28px;
            background: var(--gradient-primary);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition-smooth);
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(88, 166, 255, 0.3);
        }

        /* ===== Status Badge ===== */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            background: rgba(35, 134, 54, 0.2);
            border-radius: 20px;
            font-size: 12px;
            color: #3fb950;
        }

        /* ===== Chat Page ===== */
        #chat-page { display: none; }
        .chat-container {
            display: flex;
            height: calc(100vh - 70px);
            background: var(--bg-secondary);
            border-radius: var(--radius-lg);
            overflow: hidden;
            margin: 20px;
            border: 1px solid var(--border-color);
        }

        .chat-sidebar {
            width: 280px;
            background: var(--bg-card);
            border-right: 1px solid var(--border-color);
            padding: 20px;
            display: flex;
            flex-direction: column;
        }

        .chat-sidebar h3 {
            color: var(--accent-blue);
            font-size: 16px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chat-sidebar-item {
            padding: 12px 16px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            color: var(--text-secondary);
            margin-bottom: 8px;
            transition: var(--transition-fast);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chat-sidebar-item:hover {
            background: rgba(88, 166, 255, 0.1);
            color: var(--text-primary);
        }

        .chat-sidebar-item.active {
            background: rgba(88, 166, 255, 0.2);
            color: var(--accent-blue);
        }

        .chat-main {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .chat-message {
            padding: 14px 18px;
            border-radius: var(--radius-lg);
            max-width: 75%;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .chat-message.user {
            background: var(--gradient-primary);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }

        .chat-message.ai {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            border-bottom-left-radius: 4px;
        }

        .chat-input-area {
            padding: 16px 20px;
            background: var(--bg-card);
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 12px;
        }

        .chat-input {
            flex: 1;
            padding: 14px 18px;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
            background: var(--bg-primary);
            color: var(--text-primary);
            font-size: 14px;
            transition: var(--transition-fast);
        }

        .chat-input:focus {
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
        }

        .chat-send-btn {
            padding: 14px 28px;
            background: var(--gradient-primary);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: var(--transition-smooth);
        }

        .chat-send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(88, 166, 255, 0.3);
        }

        /* ===== Loading Animation ===== */
        .loading-dots::after {
            content: '...';
            animation: dots 1.5s infinite;
        }

        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }

        /* ===== Responsive ===== */
        @media (max-width: 768px) {
            .header { flex-direction: column; gap: 12px; }
            .nav { flex-wrap: wrap; justify-content: center; }
            .modules { grid-template-columns: 1fr; }
            .chat-sidebar { display: none; }
        }

        /* ===== Animations ===== */
        .fade-in {
            animation: fadeIn 0.5s ease forwards;
        }

        .stagger-1 { animation-delay: 0.1s; }
        .stagger-2 { animation-delay: 0.2s; }
        .stagger-3 { animation-delay: 0.3s; }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="logo">
            <div class="logo-icon">⚡</div>
            <span>CAE-CLI</span>
            <span class="status-badge"><i class="fas fa-circle" style="font-size: 8px;"></i> v0.2.0</span>
        </div>
        <div class="nav">
            <div class="nav-item active" data-page="home" onclick="showPage('home')">
                <i class="fas fa-home"></i> 首页
            </div>
            <div class="nav-item" data-page="tools" onclick="showPage('tools')">
                <i class="fas fa-tools"></i> 工具
            </div>
            <div class="nav-item" data-page="workflow" onclick="showPage('workflow')">
                <i class="fas fa-project-diagram"></i> 工作流
            </div>
            <div class="nav-item" data-page="chat" onclick="showPage('chat')">
                <i class="fas fa-comments"></i> 聊天
            </div>
            <div class="nav-item" data-page="ai" onclick="showPage('ai')">
                <i class="fas fa-robot"></i> AI
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <!-- Quick Actions -->
        <div class="quick-actions">
            <button class="quick-action-btn" onclick="bridge.runCommand('cae-cli --help')">
                <i class="fas fa-question-circle"></i> 帮助
            </button>
            <button class="quick-action-btn" onclick="bridge.runCommand('cae-cli info')">
                <i class="fas fa-info-circle"></i> 系统信息
            </button>
            <button class="quick-action-btn" onclick="bridge.runCommand('cae-cli material --list')">
                <i class="fas fa-list"></i> 材料列表
            </button>
            <button class="quick-action-btn" onclick="bridge.runCommand('cae-cli handbook search 螺栓')">
                <i class="fas fa-book"></i> 知识库
            </button>
        </div>

        <!-- Home Page Content -->
        <div id="home-page">
            <div class="page-title">
                <i class="fas fa-rocket"></i> 欢迎使用 CAE-CLI
            </div>
            <div class="modules">
                <div class="module-card fade-in stagger-1" onclick="bridge.runCommand('cae-cli parse --help')">
                    <div class="module-header">
                        <div class="module-icon">📐</div>
                        <div class="module-title">几何解析</div>
                    </div>
                    <div class="module-desc">解析 STEP、STL、IGES 等 CAD 格式，提取几何特征</div>
                    <div class="module-cmd">cae-cli parse model.step</div>
                </div>

                <div class="module-card fade-in stagger-2" onclick="bridge.runCommand('cae-cli analyze --help')">
                    <div class="module-header">
                        <div class="module-icon">🔲</div>
                        <div class="module-title">网格分析</div>
                    </div>
                    <div class="module-desc">分析有限元网格质量指标：纵横比、偏斜度、正交性</div>
                    <div class="module-cmd">cae-cli analyze mesh.msh</div>
                </div>

                <div class="module-card fade-in stagger-3" onclick="bridge.runCommand('cae-cli material --help')">
                    <div class="module-header">
                        <div class="module-icon">🔧</div>
                        <div class="module-title">材料查询</div>
                    </div>
                    <div class="module-desc">查询 GB/T 标准材料库，获取材料力学性能参数</div>
                    <div class="module-cmd">cae-cli material Q235</div>
                </div>

                <div class="module-card fade-in stagger-1" onclick="bridge.runCommand('cae-cli optimize --help')">
                    <div class="module-header">
                        <div class="module-icon">⚡</div>
                        <div class="module-title">参数优化</div>
                    </div>
                    <div class="module-desc">自动调整 CAD 参数，优化设计性能</div>
                    <div class="module-cmd">cae-cli optimize model.fcstd</div>
                </div>

                <div class="module-card fade-in stagger-2" onclick="bridge.runCommand('cae-cli report --help')">
                    <div class="module-header">
                        <div class="module-icon">📊</div>
                        <div class="module-title">报告生成</div>
                    </div>
                    <div class="module-desc">生成 HTML、PDF、Markdown 格式分析报告</div>
                    <div class="module-cmd">cae-cli report static</div>
                </div>

                <div class="module-card fade-in stagger-3" onclick="showPage('chat')">
                    <div class="module-header">
                        <div class="module-icon">🤖</div>
                        <div class="module-title">AI 助手</div>
                    </div>
                    <div class="module-desc">智能对话助手，基于本地知识库和 AI 模型</div>
                    <div class="module-cmd">点击进入聊天</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Tools Page -->
    <div id="tools-page" style="display:none;">
        <div class="page-title">
            <i class="fas fa-tools"></i> 工具模块
        </div>
        <div class="modules">
            <div class="module-card" onclick="bridge.runCommand('cae-cli parse --help')">
                <div class="module-header">
                    <div class="module-icon">📐</div>
                    <div class="module-title">几何解析</div>
                </div>
                <div class="module-desc">解析 STEP/STL/IGES，提取体积、表面积、顶点数</div>
                <div class="module-cmd">cae-cli parse model.step</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli analyze --help')">
                <div class="module-header">
                    <div class="module-icon">🔲</div>
                    <div class="module-title">网格分析</div>
                </div>
                <div class="module-desc">分析网格质量：纵横比、偏斜度、Jacobian 行列式</div>
                <div class="module-cmd">cae-cli analyze mesh.msh</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli material --help')">
                <div class="module-header">
                    <div class="module-icon">🔧</div>
                    <div class="module-title">材料查询</div>
                </div>
                <div class="module-desc">GB/T 标准材料：Q235、Q345、45钢、铝合金等</div>
                <div class="module-cmd">cae-cli material Q235</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli handbook --help')">
                <div class="module-header">
                    <div class="module-icon">📚</div>
                    <div class="module-title">知识库</div>
                </div>
                <div class="module-desc">机械设计知识：螺栓规格，公差配合，材料选择</div>
                <div class="module-cmd">cae-cli handbook search 螺栓</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli optimize --help')">
                <div class="module-header">
                    <div class="module-icon">⚡</div>
                    <div class="module-title">参数优化</div>
                </div>
                <div class="module-desc">FreeCAD/SolidWorks 参数化优化</div>
                <div class="module-cmd">cae-cli optimize model.fcstd</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli report --help')">
                <div class="module-header">
                    <div class="module-icon">📊</div>
                    <div class="module-title">报告生成</div>
                </div>
                <div class="module-desc">生成 HTML、PDF、Markdown 格式分析报告</div>
                <div class="module-cmd">cae-cli report static</div>
            </div>
        </div>
    </div>

    <!-- Workflow Page -->
    <div id="workflow-page" style="display:none;">
        <div class="page-title">
            <i class="fas fa-project-diagram"></i> 工作流
        </div>
        <div class="modules">
            <div class="module-card" onclick="bridge.runCommand('cae-cli workflow --help')">
                <div class="module-header">
                    <div class="module-icon">▶️</div>
                    <div class="module-title">运行工作流</div>
                </div>
                <div class="module-desc">执行完整的 CAD → CAE 分析流程</div>
                <div class="module-cmd">cae-cli workflow run</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli cad --help')">
                <div class="module-header">
                    <div class="module-icon">🖥️</div>
                    <div class="module-title">CAD 连接</div>
                </div>
                <div class="module-desc">连接 FreeCAD/SolidWorks 进行参数化建模</div>
                <div class="module-cmd">cae-cli cad --connect freecad</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli mcp tools')">
                <div class="module-header">
                    <div class="module-icon">🔌</div>
                    <div class="module-title">MCP 工具</div>
                </div>
                <div class="module-desc">MCP 协议工具：FreeCAD、GitHub、SQLite</div>
                <div class="module-cmd">cae-cli mcp tools</div>
            </div>
        </div>
    </div>
    <!-- Chat Page -->
    <div id="chat-page">
        <div class="chat-container">
            <div class="chat-sidebar">
                <h3><i class="fas fa-robot"></i> AI 助手</h3>
                <div class="chat-sidebar-item active">
                    <i class="fas fa-robot"></i> 智能助手
                </div>
                <div class="chat-sidebar-item">
                    <i class="fas fa-cube"></i> CAD 问题
                </div>
                <div class="chat-sidebar-item">
                    <i class="fas fa-cogs"></i> 材料咨询
                </div>
                <div class="chat-sidebar-item">
                    <i class="fas fa-chart-line"></i> 优化建议
                </div>

                <div style="margin-top: auto; padding-top: 20px; border-top: 1px solid var(--border-color);">
                    <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 12px;">
                        <i class="fas fa-bolt"></i> 快捷命令
                    </div>
                    <div class="chat-sidebar-item" onclick="bridge.runCommand('cae-cli ai generate')">
                        <i class="fas fa-magic"></i> AI 生成
                    </div>
                    <div class="chat-sidebar-item" onclick="bridge.runCommand('cae-cli ai suggest')">
                        <i class="fas fa-lightbulb"></i> AI 建议
                    </div>
                </div>
            </div>
            <div class="chat-main">
                <div class="chat-messages" id="chat-messages">
                    <div class="chat-message ai">
                        <i class="fas fa-robot" style="margin-right: 8px;"></i>
                        你好！我是 CAE-CLI AI 助手，可以帮助你：
                        <ul style="margin: 10px 0 10px 20px;">
                            <li>解答 CAD/CAE 问题</li>
                            <li>提供材料选型建议</li>
                            <li>辅助网格划分</li>
                            <li>优化设计参数</li>
                        </ul>
                        请在下方输入你的问题...
                    </div>
                </div>
                <div class="chat-input-area">
                    <input type="text" class="chat-input" id="chat-input"
                           placeholder="输入你的问题..."
                           onkeypress="if(event.key==='Enter')sendChat()">
                    <button class="chat-send-btn" onclick="sendChat()">
                        <i class="fas fa-paper-plane"></i> 发送
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- AI Page -->
    <div id="ai-page" style="display:none;">
        <div class="page-title">
            <i class="fas fa-robot"></i> AI 模块
        </div>
        <div class="modules">
            <div class="module-card" onclick="showPage('chat')">
                <div class="module-header">
                    <div class="module-icon">💬</div>
                    <div class="module-title">智能对话</div>
                </div>
                <div class="module-desc">基于 Ollama/本地模型的 AI 对话助手</div>
                <div class="module-cmd">点击进入聊天</div>
            </div>

            <div class="module-card" onclick="bridge.runCommand('cae-cli ai generate --help')">
                <div class="module-header">
                    <div class="module-icon">🎲</div>
                    <div class="module-title">AI 生成</div>
                </div>
                <div class="module-desc">自然语言描述生成 3D 模型 (FreeCAD)</div>
                <div class="module-cmd">cae-cli ai generate "立方体"</div>
            </div>

            <div class="module-card" onclick="bridge.runCommand('cae-cli ai suggest --help')">
                <div class="module-header">
                    <div class="module-icon">💡</div>
                    <div class="module-title">AI 建议</div>
                </div>
                <div class="module-desc">基于 AI 的设计优化建议</div>
                <div class="module-cmd">cae-cli ai suggest</div>
            </div>

            <div class="module-card" onclick="bridge.runCommand('cae-cli chat --help')">
                <div class="module-header">
                    <div class="module-icon">🗣️</div>
                    <div class="module-title">交互模式</div>
                </div>
                <div class="module-desc">终端交互式 AI 助手</div>
                <div class="module-cmd">cae-cli chat --lang zh</div>
            </div>
        </div>
    </div>
    <script>
        var bridge = null;
        
        // 初始化QWebChannel
        new QWebChannel(qtwebchannelCallbacks, function(channel) {
            bridge = channel.objects.bridge;
            console.log('Bridge initialized:', bridge);
        });
        
        function qtwebchannelCallbacks(registry) {}
        
        function showPage(pageId) {
            // Hide all pages
            var pages = ['home', 'tools', 'workflow', 'chat', 'ai'];
            pages.forEach(function(page) {
                var el = document.getElementById(page + '-page');
                if (el) el.style.display = 'none';
            });

            // Show selected page
            var selectedPage = document.getElementById(pageId + '-page');
            if (selectedPage) {
                selectedPage.style.display = 'block';
            }

            // Update nav active state
            document.querySelectorAll('.nav-item').forEach(function(item) {
                item.classList.remove('active');
                if (item.getAttribute('data-page') === pageId) {
                    item.classList.add('active');
                }
            });
            
            // 聊天页面时隐藏右侧面板
            if (pageId === 'chat') {
                document.body.classList.add('hide-console');
            } else {
                document.body.classList.remove('hide-console');
            }
        }
        
        function sendChat() {
            var input = document.getElementById('chat-input');
            var msg = input.value.trim();
            if (!msg) return;

            // 添加用户消息
            var messages = document.getElementById('chat-messages');
            messages.innerHTML += '<div class="chat-message user">' + msg + '</div>';

            // 添加加载状态
            var loadingDiv = document.createElement('div');
            loadingDiv.className = 'chat-message ai';
            loadingDiv.id = 'loading-msg';
            loadingDiv.innerHTML = '<span class="loading-dots">正在思考</span>';
            messages.appendChild(loadingDiv);

            // 清空输入
            input.value = '';
            messages.scrollTop = messages.scrollHeight;

            // 调用CLI执行AI聊天
            if (bridge) {
                bridge.runCommand('cae-cli chat "' + msg + '"');
            }
        }

        // 清除加载状态
        function clearLoading() {
            var loading = document.getElementById('loading-msg');
            if (loading) {
                loading.remove();
            }
        }
        
        // 命令执行结果回调
        function onCommandResult(result) {
            var messages = document.getElementById('chat-messages');
            if (messages) {
                messages.innerHTML += '<div class="chat-message ai">' + result.replace(/\\n/g, '<br>') + '</div>';
                messages.scrollTop = messages.scrollHeight;
            }
        }
    </script>
</body>
</html>"""


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MechDesign")
    app.setApplicationVersion("1.0.0")
    app.setStyle("Fusion")

    # 设置应用图标和主题
    app.setStyleSheet("""
        QToolTip {
            background-color: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            padding: 5px;
        }
    """)

    window = WebGUIWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
