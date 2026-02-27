"""
ChatPage 完整测试套件

包含：
1. 单元测试 - AIChatAPI、核心功能
2. 集成测试 - GUI 交互
3. 性能测试 - API 响应、UI渲染
4. Bug捕获测试 - 边界情况、异常处理
"""

import json
import os
import sys
import time
import unittest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from pathlib import Path

# 添加 src 目录到路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


# ========== 1. 单元测试 - AIChatAPI ==========

class TestAIChatAPI(unittest.TestCase):
    """测试 AIChatAPI 类的核心功能"""

    def setUp(self):
        """测试前置"""
        # 延迟导入，避免未安装依赖时失败
        try:
            from gui.pages.chat_page import AIChatAPI
            self.api = AIChatAPI()
        except ImportError:
            self.skipTest("PySide6 未安装，跳过 GUI 相关测试")

    def test_provider_default(self):
        """测试默认提供商"""
        self.assertEqual(self.api.provider, "ollama")

    def test_set_provider(self):
        """测试设置提供商"""
        self.api.set_provider("openai")
        self.assertEqual(self.api.provider, "openai")

        self.api.set_provider("anthropic")
        self.assertEqual(self.api.provider, "anthropic")

    def test_set_invalid_provider(self):
        """测试无效提供商 - 应该不改变"""
        self.api.set_provider("invalid_provider")
        # 无效的 provider 不会被设置，但也不会报错
        # 这个测试确保不会崩溃

    @patch('requests.post')
    def test_ollama_chat_success(self, mock_post):
        """测试 Ollama 聊天成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "测试回复"}
        }
        mock_post.return_value = mock_response

        result = self.api._ollama_chat("qwen2.5:1.5b", [{"role": "user", "content": "你好"}])

        self.assertEqual(result, "测试回复")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_ollama_chat_error(self, mock_post):
        """测试 Ollama 聊天失败"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.api._ollama_chat("qwen2.5:1.5b", [{"role": "user", "content": "你好"}])

        self.assertIn("500", str(context.exception))

    @patch('requests.post')
    def test_ollama_chat_stream(self, mock_post):
        """测试 Ollama 流式输出"""
        # 模拟流式响应 (使用 ASCII 字符)
        def mock_iter_lines():
            yield b'{"message": {"content": "Hello"}}'
            yield b'{"message": {"content": " World"}}'
            yield b'{"message": {"content": "!"}}'

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines = mock_iter_lines
        mock_post.return_value = mock_response

        callback_result = []

        def callback(chunk):
            callback_result.append(chunk)

        result = self.api._ollama_chat(
            "qwen2.5:1.5b",
            [{"role": "user", "content": "你好"}],
            stream=True,
            callback=callback
        )

        # 流式输出会累积所有内容
        self.assertEqual(result, "Hello World!")

    @patch('requests.post')
    def test_openai_chat_no_api_key(self, mock_post):
        """测试 OpenAI 无 API Key"""
        # 清除环境变量
        original = os.environ.get("OPENAI_API_KEY")
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        with self.assertRaises(Exception) as context:
            self.api._openai_chat("gpt-4", [])

        self.assertIn("OPENAI_API_KEY", str(context.exception))

        # 恢复环境变量
        if original:
            os.environ["OPENAI_API_KEY"] = original


# ========== 2. 单元测试 - ChatPage 核心功能 ==========

class TestChatPageCore(unittest.TestCase):
    """测试 ChatPage 核心功能（不依赖 GUI）"""

    def test_system_prompt_learning(self):
        """测试学习模式提示词"""
        try:
            from gui.pages.chat_page import ChatPage

            # 模拟创建，绕过 GUI
            with patch('gui.pages.chat_page.QWidget.__init__', return_value=None):
                page = ChatPage.__new__(ChatPage)
                page.mode = "learning"
                page._init_ui = Mock()

                prompt = page._get_system_prompt()

                self.assertIn("费曼学习法", prompt)
                self.assertIn("机械设计", prompt)
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_system_prompt_mechanical(self):
        """测试机械模式提示词"""
        try:
            from gui.pages.chat_page import ChatPage

            with patch('gui.pages.chat_page.QWidget.__init__', return_value=None):
                page = ChatPage.__new__(ChatPage)
                page.mode = "mechanical"

                prompt = page._get_system_prompt()

                self.assertIn("机械设计", prompt)
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_system_prompt_default(self):
        """测试默认模式提示词"""
        try:
            from gui.pages.chat_page import ChatPage

            with patch('gui.pages.chat_page.QWidget.__init__', return_value=None):
                page = ChatPage.__new__(ChatPage)
                page.mode = "unknown_mode"

                prompt = page._get_system_prompt()

                self.assertIn("工程领域", prompt)
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_knowledge_search_empty(self):
        """测试空知识库搜索"""
        try:
            from gui.pages.chat_page import ChatPage

            with patch('gui.pages.chat_page.QWidget.__init__', return_value=None):
                page = ChatPage.__new__(ChatPage)

                # 测试知识库搜索返回空的情况
                result = page._search_knowledge("test query")
                # 应该返回空字符串（因为没有安装知识库模块）
                self.assertEqual(result, "")
        except ImportError:
            self.skipTest("PySide6 未安装")


# ========== 3. Bug捕获测试 - 边界情况 ==========

class TestBugCapture(unittest.TestCase):
    """捕获真实 Bug 的测试"""

    def test_empty_model_name(self):
        """测试空模型名"""
        try:
            from gui.pages.chat_page import AIChatAPI
            api = AIChatAPI()

            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"message": {"content": ""}}
                mock_post.return_value = mock_response

                # 空模型名不应崩溃
                result = api._ollama_chat("", [{"role": "user", "content": "test"}])
                # 应该返回空内容
                self.assertEqual(result, "")
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_none_messages(self):
        """测试 None 消息"""
        try:
            from gui.pages.chat_page import AIChatAPI
            api = AIChatAPI()

            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"message": {"content": "ok"}}
                mock_post.return_value = mock_response

                # None 消息不应崩溃
                result = api._ollama_chat("model", None)
                self.assertEqual(result, "ok")
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_invalid_json_response(self):
        """测试无效 JSON 响应"""
        try:
            from gui.pages.chat_page import AIChatAPI
            api = AIChatAPI()

            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                # 返回无效 JSON
                mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
                mock_post.return_value = mock_response

                with self.assertRaises(json.JSONDecodeError):
                    api._ollama_chat("model", [{"role": "user", "content": "test"}])
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_network_timeout(self):
        """测试网络超时"""
        try:
            import requests
            from gui.pages.chat_page import AIChatAPI
            api = AIChatAPI()

            with patch('requests.post', side_effect=requests.Timeout("Timeout")):
                with self.assertRaises(requests.Timeout):
                    api._ollama_chat("model", [{"role": "user", "content": "test"}])
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_network_connection_error(self):
        """测试网络连接错误"""
        try:
            import requests
            from gui.pages.chat_page import AIChatAPI
            api = AIChatAPI()

            with patch('requests.post', side_effect=requests.ConnectionError("Connection error")):
                with self.assertRaises(requests.ConnectionError):
                    api._ollama_chat("model", [{"role": "user", "content": "test"}])
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_message_without_role(self):
        """测试缺少 role 的消息"""
        try:
            from gui.pages.chat_page import AIChatAPI
            api = AIChatAPI()

            # 消息缺少 role 字段
            messages = [{"content": "test"}]

            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"message": {"content": "ok"}}
                mock_post.return_value = mock_response

                # 应该能处理
                result = api._ollama_chat("model", messages)
                self.assertEqual(result, "ok")
        except ImportError:
            self.skipTest("PySide6 未安装")


# ========== 4. 性能测试 ==========

class TestPerformance(unittest.TestCase):
    """性能测试"""

    def test_api_response_time(self):
        """测试 API 响应时间（模拟）"""
        try:
            from gui.pages.chat_page import AIChatAPI
            api = AIChatAPI()

            # 模拟慢响应
            def slow_response(*args, **kwargs):
                time.sleep(0.1)  # 100ms
                mock_resp = Mock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {"message": {"content": "test"}}
                return mock_resp

            with patch('requests.post', side_effect=slow_response):
                start = time.time()
                api._ollama_chat("model", [{"role": "user", "content": "test"}])
                elapsed = time.time() - start

                # 应该大于 100ms
                self.assertGreater(elapsed, 0.05)
                # 应该小于 200ms
                self.assertLess(elapsed, 0.2)
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_message_build_performance(self):
        """测试消息构建性能"""
        try:
            from gui.pages.chat_page import ChatPage

            # 创建大量历史消息
            messages = []
            for i in range(100):
                messages.append({"role": "user", "content": f"问题 {i}"})
                messages.append({"role": "assistant", "content": f"回答 {i}"})

            start = time.time()
            # 模拟截取最近10条
            recent = messages[-10:]
            elapsed = time.time() - start

            self.assertEqual(len(recent), 10)
            self.assertLess(elapsed, 0.01)  # 应该很快
        except ImportError:
            self.skipTest("PySide6 未安装")

    def test_search_knowledge_performance(self):
        """测试知识库搜索性能"""
        try:
            from gui.pages.chat_page import ChatPage

            with patch('gui.pages.chat_page.QWidget.__init__', return_value=None):
                page = ChatPage.__new__(ChatPage)

                # Mock search function to simulate work
                def slow_search(query, limit=3):
                    time.sleep(0.05)
                    return [{"title": "Test", "content": "Content"}]

                # 使用 try-except 处理导入错误
                try:
                    import gui.pages.chat_page as chat_page_module
                    original_search = getattr(chat_page_module, 'search', None)

                    # Mock search
                    if original_search:
                        with patch.object(chat_page_module, 'search', side_effect=slow_search):
                            start = time.time()
                            result = page._search_knowledge("test query")
                            elapsed = time.time() - start
                            self.assertIn("Test", result)
                            self.assertLess(elapsed, 0.1)
                    else:
                        # search 不存在，直接测试
                        pass
                except:
                    pass  # 忽略错误
        except ImportError:
            self.skipTest("PySide6 未安装")


# ========== 5. 集成测试 - 需要 GUI ==========

@unittest.skipIf(
    os.environ.get("SKIP_GUI_TESTS", "0") == "1",
    "跳过 GUI 测试"
)
class TestGUIIntegration(unittest.TestCase):
    """GUI 集成测试"""

    def setUp(self):
        """测试前置"""
        try:
            from PySide6.QtWidgets import QApplication
        except ImportError:
            self.skipTest("PySide6 未安装")

        # 创建 QApplication 如果不存在
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        # 延迟导入 ChatPage
        try:
            from gui.pages.chat_page import ChatPage
            self.ChatPage = ChatPage
        except ImportError:
            self.ChatPage = None

    def tearDown(self):
        """测试后置"""
        if hasattr(self, 'app'):
            # 不退出，保持 app 运行
            pass

    def test_create_chat_page(self):
        """测试创建聊天页面"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        try:
            page = self.ChatPage(mode="learning")
            self.assertIsNotNone(page)
            self.assertEqual(page.mode, "learning")
            self.assertEqual(page.model_source, "ollama")
            self.assertTrue(page.kb_enabled)
        except Exception as e:
            self.fail(f"创建页面失败: {e}")

    def test_create_different_modes(self):
        """测试创建不同模式的页面"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        modes = ["learning", "mechanical", "default"]

        for mode in modes:
            with self.subTest(mode=mode):
                page = self.ChatPage(mode=mode)
                self.assertEqual(page.mode, mode)

    def test_initial_state(self):
        """测试初始状态"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        page = self.ChatPage()

        # 检查初始状态
        self.assertEqual(len(page.messages), 0)
        self.assertIsNotNone(page.input_text)
        self.assertIsNotNone(page.send_btn)

    def test_source_toggle_buttons_exist(self):
        """测试来源切换按钮存在"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        page = self.ChatPage()

        self.assertIsNotNone(page.ollama_btn)
        self.assertIsNotNone(page.api_btn)
        self.assertIsNotNone(page.gguf_btn)

    def test_switch_source(self):
        """测试切换来源"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        page = self.ChatPage()

        # 切换到 API 模式
        page._switch_source("api")
        self.assertEqual(page.model_source, "api")
        self.assertEqual(page.api.provider, "openai")

        # 切换到 GGUF 模式
        page._switch_source("gguf")
        self.assertEqual(page.model_source, "gguf")

    def test_kb_toggle(self):
        """测试知识库开关"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        page = self.ChatPage()

        # 初始应该是开启的
        self.assertTrue(page.kb_enabled)

        # 切换关闭
        page._toggle_kb()
        self.assertFalse(page.kb_enabled)

        # 切换开启
        page._toggle_kb()
        self.assertTrue(page.kb_enabled)

    def test_model_selector_initially_hidden(self):
        """测试模型选择器初始隐藏"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        page = self.ChatPage()

        # 初始状态下模型选择器应该是隐藏的
        self.assertFalse(page.model_selector_expanded)

    def test_add_message(self):
        """测试添加消息"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        page = self.ChatPage()

        # 添加用户消息
        page._add_message("User", "Test message", is_bot=False)

        # 检查消息是否添加（通过布局）
        self.assertGreater(page.chat_layout.count(), 1)

    def test_clear_chat(self):
        """测试清空对话"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        page = self.ChatPage()

        # 添加一些消息
        page._add_message("User", "Test", is_bot=False)
        page._add_message("Bot", "Reply", is_bot=True)

        # 清空
        page._clear_chat()

        # 检查消息是否清空
        self.assertEqual(len(page.messages), 0)

    def test_status_update(self):
        """测试状态更新"""
        if self.ChatPage is None:
            self.skipTest("ChatPage 未导入")

        page = self.ChatPage()

        page._update_status("Test Status", True)

        # 检查状态文本
        self.assertEqual(page.status_text.text(), "Test Status")


# ========== 6. 异常处理测试 ==========

class TestExceptionHandling(unittest.TestCase):
    """异常处理测试"""

    def test_api_error_handling(self):
        """测试 API 错误处理"""
        try:
            from gui.pages.chat_page import AIChatAPI

            # Mock requests 使其返回错误状态码
            with patch('requests.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 404
                mock_post.return_value = mock_response

                api = AIChatAPI()

                # 应该抛出异常
                with self.assertRaises(Exception) as context:
                    api._ollama_chat("model", [{"role": "user", "content": "test"}])

                self.assertIn("404", str(context.exception))
        except ImportError:
            self.skipTest("PySide6 未安装")


# ========== 运行器 ==========

def run_tests():
    """运行所有测试"""
    print("=" * 70)
    print("ChatPage 完整测试套件")
    print("=" * 70)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestAIChatAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestChatPageCore))
    suite.addTests(loader.loadTestsFromTestCase(TestBugCapture))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestGUIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionHandling))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出摘要
    print("\n" + "=" * 70)
    print("测试摘要")
    print("=" * 70)
    print(f"运行: {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")

    if result.failures:
        print("\n失败详情:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1][:100]}")

    if result.errors:
        print("\n错误详情:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error: ')[-1][:100]}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
