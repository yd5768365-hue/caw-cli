"""
CAE-CLI Web视图接口模块

此模块提供 QWebEngineView 集成接口，用于美化软件桌面。
支持本地HTML页面渲染和JavaScript交互。

使用方法:
    from gui.web_view import WebViewWindow, create_web_view
    
    # 创建独立的Web视图窗口
    window = WebViewWindow()
    window.load_url("https://example.com")
    window.show()
    
    # 或在现有窗口中嵌入Web视图
    web_view = create_web_view(parent=main_window)
    main_layout.addWidget(web_view)
"""

from typing import Optional, Callable, Dict, Any
from pathlib import Path

from PySide6.QtCore import QUrl, Signal, Slot, QObject, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings


class WebBridge(QObject):
    """Web与Python通信桥接器
    
    允许JavaScript调用Python函数，实现Web页面与应用的交互。
    
    使用示例:
        # Python端定义回调
        bridge = WebBridge()
        bridge.python_callback.connect(lambda msg: print(f"JS消息: {msg}"))
        
        # 注入到Web视图
        web_view.page().webChannel().registerObject("pybridge", bridge)
        
        # JavaScript端调用
        # pybridge.python_callback.emit("Hello from JS!")
    """
    
    # 信号：接收来自JavaScript的消息
    message_received = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._callbacks: Dict[str, Callable] = {}
    
    @Slot(str)
    def receive_message(self, message: str):
        """接收来自JavaScript的消息"""
        self.message_received.emit(message)
    
    def register_callback(self, name: str, callback: Callable):
        """注册回调函数
        
        Args:
            name: 回调函数名称
            callback: 要执行的Python函数
        """
        self._callbacks[name] = callback
    
    def call_js(self, func_name: str, *args):
        """调用JavaScript函数
        
        Args:
            func_name: JavaScript函数名
            args: 传递给JS函数的参数
        """
        args_str = ", ".join([f'"{arg}"' if isinstance(arg, str) else str(arg) for arg in args])
        js_code = f"{func_name}({args_str})"
        return js_code


class WebViewWidget(QWidget):
    """Web视图控件
    
    可嵌入到其他窗口中的Web视图组件。
    
    Attributes:
        web_view: QWebEngineView实例
        bridge: WebBridge通信桥
    """
    
    def __init__(self, parent: Optional[QWidget] = None, debug: bool = False):
        super().__init__(parent)
        self._debug = debug
        self._init_ui()
        self._setup_bridge()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建Web视图
        self.web_view = QWebEngineView(self)
        
        # 配置Web设置
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowFeaturesFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        
        # 开发者工具（调试模式）
        if self._debug:
            from PySide6.QtWebEngineWidgets import QWebEngineDevToolsWidget
            self.dev_tools = QWebEngineDevToolsWidget(self.web_view.page())
        else:
            self.dev_tools = None
        
        layout.addWidget(self.web_view)
        
        # 页面加载完成信号
        self.web_view.loadFinished.connect(self._on_load_finished)
    
    def _setup_bridge(self):
        """设置Web通信桥"""
        self.bridge = WebBridge(self)
        
        # 将bridge注入到Web视图
        self.web_view.page().webChannel().registerObject("pybridge", self.bridge)
        
        # 注入JavaScript桥接代码
        js_bridge = """
        // Python桥接器
        window.pybridge = {
            sendMessage: function(msg) {
                if (window.pybridge && window.pybridge.receive_message) {
                    window.pybridge.receive_message(msg);
                }
            },
            // 供Python调用的回调
            callbacks: {},
            registerCallback: function(name, func) {
                this.callbacks[name] = func;
            },
            // 触发Python回调
            triggerCallback: function(name, data) {
                if (this.callbacks[name]) {
                    this.callbacks[name](data);
                }
            }
        };
        
        // 兼容旧版本
        if (typeof window.pybridge !== 'undefined') {
            window.pybridge.receive_message = function(msg) {
                // 可以在这里添加自定义处理
                console.log('Received from Python:', msg);
            };
        }
        """
        self.web_view.page().runJavaScript(js_bridge)
    
    def _on_load_finished(self, ok: bool):
        """页面加载完成回调"""
        if ok:
            if self._debug:
                print("[WebView] 页面加载成功")
        else:
            if self._debug:
                print("[WebView] 页面加载失败")
    
    def load_url(self, url: str):
        """加载URL
        
        Args:
            url: 要加载的网址或本地文件路径
        """
        if url.startswith("http://") or url.startswith("https://"):
            self.web_view.setUrl(QUrl(url))
        else:
            # 本地文件
            file_path = Path(url)
            if file_path.exists():
                self.web_view.setUrl(QUrl.fromLocalFile(str(file_path.absolute())))
            else:
                print(f"[WebView] 文件不存在: {url}")
    
    def load_html(self, html: str):
        """加载HTML内容
        
        Args:
            html: HTML字符串
        """
        self.web_view.setHtml(html)
    
    def load_file(self, file_path: str):
        """加载本地HTML文件
        
        Args:
            file_path: 本地HTML文件路径
        """
        path = Path(file_path)
        if path.exists():
            self.web_view.setUrl(QUrl.fromLocalFile(str(path.absolute())))
        else:
            print(f"[WebView] 文件不存在: {file_path}")
    
    def execute_js(self, code: str):
        """执行JavaScript代码
        
        Args:
            code: JavaScript代码
        """
        self.web_view.page().runJavaScript(code)
    
    def get_web_view(self) -> QWebEngineView:
        """获取WebEngineView实例"""
        return self.web_view
    
    def get_bridge(self) -> WebBridge:
        """获取WebBridge实例"""
        return self.bridge


class WebViewWindow(QMainWindow):
    """独立的Web视图窗口
    
    创建一个独立的窗口来显示Web内容。
    适用于全屏Web应用或嵌入式浏览器。
    
    使用示例:
        window = WebViewWindow(title="My App", size=(800, 600))
        window.load_url("https://example.com")
        window.show()
    """
    
    def __init__(
        self, 
        title: str = "CAE-CLI Web View",
        size: tuple = (1024, 768),
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self._title = title
        self._size = size
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle(self._title)
        self.resize(*self._size)
        
        # 创建Web视图组件
        self.web_widget = WebViewWidget(self, debug=True)
        self.setCentralWidget(self.web_widget)
    
    def load_url(self, url: str):
        """加载URL"""
        self.web_widget.load_url(url)
    
    def load_html(self, html: str):
        """加载HTML"""
        self.web_widget.load_html(html)
    
    def load_file(self, file_path: str):
        """加载本地文件"""
        self.web_widget.load_file(file_path)
    
    def execute_js(self, code: str):
        """执行JavaScript"""
        self.web_widget.execute_js(code)
    
    @property
    def web_view(self) -> QWebEngineView:
        """获取WebEngineView实例"""
        return self.web_widget.get_web_view()
    
    @property
    def bridge(self) -> WebBridge:
        """获取WebBridge实例"""
        return self.web_widget.get_bridge()


def create_web_view(
    parent: Optional[QWidget] = None,
    url: Optional[str] = None,
    size: Optional[tuple] = None,
    debug: bool = False
) -> WebViewWidget:
    """创建Web视图的便捷函数
    
    Args:
        parent: 父窗口
        url: 初始加载的URL
        size: 视图大小 (width, height)
        debug: 是否启用调试模式
    
    Returns:
        WebViewWidget: Web视图控件
    
    Usage:
        # 在现有窗口中添加Web视图
        web_view = create_web_view(
            parent=main_window,
            url="https://example.com",
            size=(800, 600)
        )
        layout.addWidget(web_view)
    """
    widget = WebViewWidget(parent=parent, debug=debug)
    
    if size:
        widget.setMinimumSize(*size)
    
    if url:
        widget.load_url(url)
    
    return widget


def create_modern_desktop_html() -> str:
    """创建现代化桌面界面的HTML模板
    
    Returns:
        str: HTML字符串，可直接加载到WebView中
    """
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAE-CLI 现代化界面</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(255,255,255,0.05);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(10px);
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .nav {
            display: flex;
            gap: 20px;
        }
        
        .nav-item {
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .nav-item:hover {
            background: rgba(255,255,255,0.1);
        }
        
        .nav-item.active {
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
        }
        
        .main {
            flex: 1;
            padding: 40px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .card-icon {
            font-size: 40px;
            margin-bottom: 16px;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .card-desc {
            font-size: 14px;
            color: #aaa;
        }
        
        .footer {
            background: rgba(255,255,255,0.05);
            padding: 16px 40px;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">CAE-CLI</div>
        <div class="nav">
            <div class="nav-item active">首页</div>
            <div class="nav-item">功能</div>
            <div class="nav-item">学习</div>
            <div class="nav-item">设置</div>
        </div>
    </div>
    
    <div class="main">
        <div class="card" onclick="openModule('geometry')">
            <div class="card-icon">📐</div>
            <div class="card-title">几何分析</div>
            <div class="card-desc">几何模型解析与参数提取</div>
        </div>
        
        <div class="card" onclick="openModule('mesh')">
            <div class="card-icon">🔲</div>
            <div class="card-title">网格分析</div>
            <div class="card-desc">有限元网格质量评估</div>
        </div>
        
        <div class="card" onclick="openModule('material')">
            <div class="card-icon">🔧</div>
            <div class="card-title">材料数据库</div>
            <div class="card-desc">工程材料属性查询</div>
        </div>
        
        <div class="card" onclick="openModule('optimize')">
            <div class="card-icon">⚡</div>
            <div class="card-title">优化设计</div>
            <div class="card-desc">参数化优化与敏感性分析</div>
        </div>
        
        <div class="card" onclick="openModule('ai')">
            <div class="card-icon">🤖</div>
            <div class="card-title">AI 助手</div>
            <div class="card-desc">智能问答与知识检索</div>
        </div>
        
        <div class="card" onclick="openModule('learning')">
            <div class="card-icon">📚</div>
            <div class="card-title">学习中心</div>
            <div class="card-desc">机械设计知识与案例</div>
        </div>
    </div>
    
    <div class="footer">
        CAE-CLI v0.2.0 | 现代化CAE集成工具
    </div>
    
    <script>
        function openModule(moduleName) {
            console.log('打开模块:', moduleName);
            // 通过桥接器通知Python
            if (window.pybridge) {
                window.pybridge.sendMessage(JSON.stringify({
                    action: 'open_module',
                    module: moduleName
                }));
            }
        }
        
        // 接收Python消息
        if (window.pybridge) {
            window.pybridge.receive_message = function(msg) {
                console.log('收到Python消息:', msg);
                try {
                    const data = JSON.parse(msg);
                    handlePythonMessage(data);
                } catch(e) {
                    console.log('消息解析失败:', e);
                }
            };
        }
        
        function handlePythonMessage(data) {
            switch(data.action) {
                case 'navigate':
                    // 处理导航
                    break;
                case 'update':
                    // 更新界面
                    break;
            }
        }
    </script>
</body>
</html>
"""


# 导出公共接口
__all__ = [
    "WebViewWidget",
    "WebViewWindow", 
    "WebBridge",
    "create_web_view",
    "create_modern_desktop_html",
]
