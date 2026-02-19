"""
CAE-CLI Web界面 - PySide6 + QWebEngineView
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QMessageBox
)
from PySide6.QtCore import QUrl, QObject, Slot, Signal, QProcess, QTimer, QProcessEnvironment
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel


def get_cli_path():
    """获取CLI可执行文件路径 - 兼容打包和开发模式"""
    if getattr(sys, 'frozen', False):
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
        self._current_output += bytes(data).decode('utf-8', errors='replace')
    
    def _on_stderr(self):
        """标准错误"""
        data = self._process.readAllStandardError()
        self._current_output += bytes(data).decode('utf-8', errors='replace')
    
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
        self.setWindowTitle("CAE-CLI 现代化界面")
        self.setMinimumSize(1400, 900)
        self.resize(1800, 1100)
        
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
        
        # 左侧：Web视图
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
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
        
        # 右侧：命令面板
        right_widget = QWidget()
        right_widget.setMinimumWidth(600)
        right_widget.setMaximumWidth(800)
        right_widget.setStyleSheet("background-color: #0d1117;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(12)
        
        # 标题
        title_label = QLabel("📋 命令控制台")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px; color: #58a6ff;")
        right_layout.addWidget(title_label)
        
        # CLI路径显示
        cli_exists = "✅" if os.path.exists(CLI_EXE_PATH) else "❌"
        cli_path_label = QLabel(f"{cli_exists} CLI路径: {os.path.basename(CLI_EXE_PATH)}")
        cli_path_label.setStyleSheet("color: #8b949e; font-size: 12px; padding: 5px;")
        cli_path_label.setWordWrap(True)
        right_layout.addWidget(cli_path_label)
        
        # 命令输入框
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("输入命令，如: cae-cli --help")
        self.command_input.setStyleSheet("padding: 12px; font-size: 14px; background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px;")
        self.command_input.returnPressed.connect(self._execute_command)
        right_layout.addWidget(self.command_input)
        
        # 执行按钮
        button_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("▶ 执行命令")
        self.execute_btn.setStyleSheet("QPushButton { background-color: #238636; color: white; border: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; font-size: 14px; } QPushButton:hover { background-color: #2ea043; } QPushButton:disabled { background-color: #21262d; color: #484f58; }")
        self.execute_btn.clicked.connect(self._execute_command)
        button_layout.addWidget(self.execute_btn)
        
        self.clear_btn = QPushButton("🗑 清空")
        self.clear_btn.setStyleSheet("QPushButton { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 12px 20px; border-radius: 6px; font-size: 14px; } QPushButton:hover { background-color: #30363d; }")
        self.clear_btn.clicked.connect(lambda: self.output_text.clear())
        button_layout.addWidget(self.clear_btn)
        
        right_layout.addLayout(button_layout)
        
        # 输出文本框
        output_label = QLabel("📄 执行输出:")
        output_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #c9d1d9;")
        right_layout.addWidget(output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("QTextEdit { background-color: #0d1117; color: #c9d1d9; font-family: 'Consolas', monospace; font-size: 13px; border: 1px solid #30363d; padding: 10px; }")
        right_layout.addWidget(self.output_text, 1)
        
        # 状态栏
        self.status_label = QLabel("✅ 就绪 - 点击界面卡片或按回车执行命令")
        self.status_label.setStyleSheet("padding: 8px; font-size: 13px; color: #8b949e;")
        right_layout.addWidget(self.status_label)
        
        main_layout.addWidget(left_widget, 3)
        main_layout.addWidget(right_widget, 2)
        
        self._create_menu_bar()
        
        # 连接bridge信号
        self._bridge.commandStarted.connect(self._on_command_started)
        self._bridge.commandFinished.connect(self._on_command_finished)
    
    def _on_command_started(self):
        """命令开始执行"""
        self.status_label.setText("⏳ 正在执行命令...")
        self.execute_btn.setEnabled(False)
    
    def _on_command_finished(self, output: str):
        """命令执行完成"""
        self.output_text.append(output)
        self.output_text.append("-" * 60)
        self.output_text.append("")
        
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
        
        self.execute_btn.setEnabled(True)
        self.status_label.setText("✅ 命令执行完成")
    
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
            self.output_text.append(f"[错误] 找不到CLI: {CLI_EXE_PATH}")
            return
        
        self._bridge.runCommand(command_str)
    
    def _show_about(self):
        QMessageBox.about(
            self, "关于 CAE-CLI",
            "CAE-CLI 现代化界面 v0.2.0\n\n基于 PySide6 + QWebEngineView"
        )
    
    def _get_default_html(self) -> str:
        """获取默认HTML内容 - 暗色科技风"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAE-CLI</title>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #0d1117, #161b22); color: #c9d1d9; min-height: 100vh; }
        .header { background: rgba(22,27,34,0.95); padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; }
        .logo { font-size: 32px; font-weight: bold; background: linear-gradient(90deg, #58a6ff, #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .nav { display: flex; gap: 15px; }
        .nav-item { padding: 10px 20px; border-radius: 8px; cursor: pointer; color: #8b949e; }
        .nav-item:hover { background: rgba(88,166,255,0.1); }
        .nav-item.active { background: rgba(88,166,255,0.2); color: #58a6ff; }
        .container { padding: 40px; max-width: 1400px; margin: 0 auto; }
        .hero { text-align: center; padding: 40px 0; }
        .hero h1 { font-size: 56px; background: linear-gradient(90deg, #58a6ff, #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .modules { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 40px; }
        .module-card { background: linear-gradient(145deg, rgba(33,38,45,0.8), rgba(22,27,34,0.9)); border-radius: 16px; padding: 28px; border: 1px solid #30363d; cursor: pointer; transition: all 0.3s; }
        .module-card:hover { transform: translateY(-8px); border-color: #58a6ff; box-shadow: 0 15px 40px rgba(0,0,0,0.4); }
        .module-icon { font-size: 48px; margin-bottom: 16px; }
        .module-title { font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #c9d1d9; }
        .module-desc { font-size: 14px; color: #8b949e; }
        .module-cmd { margin-top: 15px; padding: 8px 12px; background: rgba(0,0,0,0.3); border-radius: 6px; font-family: Consolas, monospace; font-size: 12px; color: #58a6ff; }
        .action-btns { display: flex; gap: 15px; justify-content: center; }
        .action-btn { padding: 12px 28px; background: linear-gradient(90deg, #238636, #2ea043); border: none; border-radius: 8px; color: white; font-size: 14px; cursor: pointer; }
        .action-btn:hover { transform: scale(1.05); }
        .click-hint { background: rgba(88,166,255,0.1); border: 1px solid rgba(88,166,255,0.3); border-radius: 8px; padding: 12px; margin-bottom: 20px; text-align: center; color: #58a6ff; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">⚡ CAE-CLI</div>
        <div class="nav">
            <div class="nav-item active" onclick="showPage('home')">🏠 首页</div>
            <div class="nav-item" onclick="showPage('tools')">🛠️ 工具</div>
            <div class="nav-item" onclick="showPage('ai')">🤖 AI</div>
        </div>
    </div>
    <div class="container" id="home-page">
        <div class="click-hint">💡 点击任意模块卡片直接执行命令</div>
        <div class="hero">
            <h1>CAE-CLI</h1>
            <p>专业的机械设计辅助工具</p>
            <div class="action-btns">
                <button class="action-btn" onclick="bridge.runCommand('cae-cli --help')">查看帮助</button>
                <button class="action-btn" onclick="bridge.runCommand('cae-cli info')">系统信息</button>
                <button class="action-btn" onclick="bridge.runCommand('cae-cli material --list')">材料列表</button>
            </div>
        </div>
        <div class="modules">
            <div class="module-card" onclick="bridge.runCommand('cae-cli parse --help')">
                <div class="module-icon">📐</div>
                <div class="module-title">几何解析</div>
                <div class="module-desc">解析STEP、STL、IGES</div>
                <div class="module-cmd">cae-cli parse model.step</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli analyze --help')">
                <div class="module-icon">🔲</div>
                <div class="module-title">网格分析</div>
                <div class="module-desc">分析有限元网格质量</div>
                <div class="module-cmd">cae-cli analyze mesh.msh</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli material --help')">
                <div class="module-icon">🔧</div>
                <div class="module-title">材料查询</div>
                <div class="module-desc">查询材料数据库</div>
                <div class="module-cmd">cae-cli material Q235</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli optimize --help')">
                <div class="module-icon">⚡</div>
                <div class="module-title">参数优化</div>
                <div class="module-desc">自动调整设计参数</div>
                <div class="module-cmd">cae-cli optimize</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli workflow --help')">
                <div class="module-icon">🔄</div>
                <div class="module-title">CAE工作流</div>
                <div class="module-desc">完整CAD→CAE流程</div>
                <div class="module-cmd">cae-cli workflow</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli ai --help')">
                <div class="module-icon">🤖</div>
                <div class="module-title">AI助手</div>
                <div class="module-desc">自然语言生成模型</div>
                <div class="module-cmd">cae-cli ai</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli handbook --help')">
                <div class="module-icon">📚</div>
                <div class="module-title">知识库</div>
                <div class="module-desc">机械设计知识</div>
                <div class="module-cmd">cae-cli handbook</div>
            </div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli interactive --help')">
                <div class="module-icon">💬</div>
                <div class="module-title">交互模式</div>
                <div class="module-desc">菜单式交互</div>
                <div class="module-cmd">cae-cli interactive</div>
            </div>
        </div>
    </div>
    <div class="container" id="tools-page" style="display:none;">
        <h2 style="font-size:28px;margin-bottom:30px;">🛠️ 工具模块</h2>
        <div class="modules">
            <div class="module-card" onclick="bridge.runCommand('cae-cli parse --help')"><div class="module-icon">📐</div><div class="module-title">几何解析</div></div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli analyze --help')"><div class="module-icon">🔲</div><div class="module-title">网格分析</div></div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli material --help')"><div class="module-icon">🔧</div><div class="module-title">材料查询</div></div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli report --help')"><div class="module-icon">📊</div><div class="module-title">报告生成</div></div>
        </div>
    </div>
    <div class="container" id="ai-page" style="display:none;">
        <h2 style="font-size:28px;margin-bottom:30px;">🤖 AI模块</h2>
        <div class="modules">
            <div class="module-card" onclick="bridge.runCommand('cae-cli ai generate --help')"><div class="module-icon">🎲</div><div class="module-title">AI生成</div></div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli ai suggest --help')"><div class="module-icon">💡</div><div class="module-title">AI建议</div></div>
            <div class="module-card" onclick="bridge.runCommand('cae-cli chat --help')"><div class="module-icon">💬</div><div class="module-title">智能对话</div></div>
        </div>
    </div>
    <script>
        var bridge = null;
        
        // 初始化QWebChannel
        new QWebChannel(qtwebchannelCallbacks, function(channel) {
            bridge = channel.objects.bridge;
            console.log('Bridge initialized:', bridge);
        });
        
        function qtwebchannelCallbacks(registry) {
            // WebChannel初始化回调
        }
        
        function showPage(pageId) {
            document.getElementById('home-page').style.display = 'none';
            document.getElementById('tools-page').style.display = 'none';
            document.getElementById('ai-page').style.display = 'none';
            document.getElementById(pageId + '-page').style.display = 'block';
            document.querySelectorAll('.nav-item').forEach(function(item) { item.classList.remove('active'); });
            event.target.classList.add('active');
        }
    </script>
</body>
</html>"""


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CAE-CLI")
    app.setApplicationVersion("0.2.0")
    app.setStyle("Fusion")
    
    window = WebGUIWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
