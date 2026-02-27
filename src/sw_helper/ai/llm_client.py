"""
AI LLM集成 - 支持OpenAI/Claude/本地模型
实现类似opencode的交互式AI助手
"""

import asyncio
import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiohttp


class LLMProvider(Enum):
    """支持的LLM提供商"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"  # 本地模型
    CUSTOM = "custom"


class ConnectionPool:
    """HTTP连接池 - 重用ClientSession减少TCP握手开销"""

    _instance = None
    _sessions: Dict[str, aiohttp.ClientSession] = {}
    _session_refcount: Dict[str, int] = {}
    _cleanup_task = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_session(self, base_url: str) -> aiohttp.ClientSession:
        """
        获取或创建ClientSession

        Args:
            base_url: API基础URL

        Returns:
            ClientSession实例
        """
        # 规范化URL（去除末尾斜杠）
        normalized_url = base_url.rstrip("/")

        if normalized_url not in self._sessions:
            # 创建新的session
            timeout = aiohttp.ClientTimeout(total=60)
            connector = aiohttp.TCPConnector(limit=10, keepalive_timeout=30)
            session = aiohttp.ClientSession(timeout=timeout, connector=connector, headers={"User-Agent": "CAE-CLI/1.0"})
            self._sessions[normalized_url] = session
            self._session_refcount[normalized_url] = 1
            print(f"[HTTP连接池] 创建新session: {normalized_url}")
        else:
            # 增加引用计数
            self._session_refcount[normalized_url] += 1

        return self._sessions[normalized_url]

    def release_session(self, base_url: str):
        """
        释放session引用

        Args:
            base_url: API基础URL
        """
        normalized_url = base_url.rstrip("/")

        if normalized_url in self._session_refcount:
            self._session_refcount[normalized_url] -= 1

            # 如果引用计数为0，关闭session（实际上我们保持session开启以重用）
            # 这里我们只是减少引用计数，session会一直保持开启直到程序结束
            if self._session_refcount[normalized_url] <= 0:
                print(f"[HTTP连接池] 引用计数归零，但保持session开启: {normalized_url}")

    async def cleanup(self):
        """清理所有session（程序退出时调用）"""
        for url, session in self._sessions.items():
            if not session.closed:
                await session.close()
                print(f"[HTTP连接池] 关闭session: {url}")

        self._sessions.clear()
        self._session_refcount.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        return {
            "total_sessions": len(self._sessions),
            "session_refcounts": self._session_refcount.copy(),
            "open_sessions": sum(1 for s in self._sessions.values() if not s.closed),
        }


@dataclass
class LLMConfig:
    """LLM配置"""

    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60


@dataclass
class Message:
    """聊天消息"""

    role: str  # system, user, assistant, tool
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None


class LLMClient:
    """
    LLM客户端
    支持多种模型提供商
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.conversation_history: List[Message] = []
        self.connection_pool = ConnectionPool()

    def _get_base_url(self) -> str:
        """获取API基础URL"""
        if self.config.api_base:
            return self.config.api_base.rstrip("/")

        # 默认URL
        if self.config.provider == LLMProvider.OPENAI:
            return "https://api.openai.com/v1"
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return "https://api.anthropic.com/v1"
        elif self.config.provider == LLMProvider.DEEPSEEK:
            return "https://api.deepseek.com"
        elif self.config.provider == LLMProvider.OLLAMA:
            return "http://localhost:11434"
        else:
            return "http://localhost:8080"  # 自定义API默认地址

    async def __aenter__(self):
        base_url = self._get_base_url()
        self.session = self.connection_pool.get_session(base_url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            # 不关闭session，只是释放引用
            base_url = self._get_base_url()
            self.connection_pool.release_session(base_url)
            self.session = None

    async def chat(self, message: str, tools: Optional[List[Dict]] = None) -> str:
        """
        发送聊天消息

        Args:
            message: 用户消息
            tools: 可用工具列表（用于function calling）

        Returns:
            AI回复
        """
        # 添加用户消息到历史
        self.conversation_history.append(Message(role="user", content=message))

        # 根据提供商调用不同的API
        if self.config.provider == LLMProvider.OPENAI:
            response = await self._call_openai(tools)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            response = await self._call_anthropic(tools)
        elif self.config.provider == LLMProvider.DEEPSEEK:
            response = await self._call_deepseek(tools)
        elif self.config.provider == LLMProvider.OLLAMA:
            response = await self._call_ollama(tools)
        else:
            response = await self._call_custom(tools)

        # 添加AI回复到历史
        self.conversation_history.append(Message(role="assistant", content=response))

        return response

    async def chat_stream(self, message: str, tools: Optional[List[Dict]] = None) -> AsyncGenerator[str, None]:
        """
        流式聊天

        Yields:
            流式响应片段
        """
        # 添加用户消息到历史
        self.conversation_history.append(Message(role="user", content=message))

        full_response = ""

        if self.config.provider == LLMProvider.OPENAI:
            async for chunk in self._call_openai_stream(tools):
                full_response += chunk
                yield chunk
        elif self.config.provider == LLMProvider.ANTHROPIC:
            async for chunk in self._call_anthropic_stream(tools):
                full_response += chunk
                yield chunk
        else:
            # 非流式API模拟流式
            response = await self.chat(message, tools)
            # 按句子分割输出
            import re

            sentences = re.split("([。！？.!?]\\s*)", response)
            for sentence in sentences:
                if sentence:
                    yield sentence
                    await asyncio.sleep(0.05)  # 模拟打字效果

        # 添加完整回复到历史
        self.conversation_history.append(Message(role="assistant", content=full_response))

    async def _call_openai(self, tools: Optional[List[Dict]] = None) -> str:
        """调用OpenAI API"""
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        messages = [{"role": m.role, "content": m.content} for m in self.conversation_history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with self.session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"OpenAI API error: {error}")

            data = await resp.json()
            choice = data["choices"][0]

            # 检查是否有工具调用
            if "tool_calls" in choice["message"]:
                # 处理工具调用
                return await self._handle_tool_calls(choice["message"]["tool_calls"])

            return choice["message"]["content"]

    async def _call_openai_stream(self, tools: Optional[List[Dict]] = None) -> AsyncGenerator[str, None]:
        """流式调用OpenAI API"""
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        messages = [{"role": m.role, "content": m.content} for m in self.conversation_history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with self.session.post(url, headers=headers, json=payload) as resp:
            async for line in resp.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue

    async def _call_anthropic(self, tools: Optional[List[Dict]] = None) -> str:
        """调用Anthropic Claude API"""
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not found")

        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": api_key, "Content-Type": "application/json"}

        # 构建消息
        system_msg = ""
        messages = []
        for m in self.conversation_history:
            if m.role == "system":
                system_msg = m.content
            else:
                messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        if system_msg:
            payload["system"] = system_msg

        async with self.session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"Anthropic API error: {error}")

            data = await resp.json()
            return data["content"][0]["text"]

    async def _call_anthropic_stream(self, tools: Optional[List[Dict]] = None) -> AsyncGenerator[str, None]:
        """流式调用Anthropic API"""
        # 简化实现，实际应该使用SSE
        response = await self._call_anthropic(tools)
        for char in response:
            yield char
            await asyncio.sleep(0.01)

    async def _call_deepseek(self, tools: Optional[List[Dict]] = None) -> str:
        """调用DeepSeek API"""
        api_key = self.config.api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek API key not found")

        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        messages = [{"role": m.role, "content": m.content} for m in self.conversation_history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        async with self.session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"DeepSeek API error: {error}")

            data = await resp.json()
            return data["choices"][0]["message"]["content"]

    async def _call_ollama(self, tools: Optional[List[Dict]] = None) -> str:
        """调用Ollama本地模型（使用HTTP连接池）"""
        # 获取基础URL
        base_url = self.config.api_base or "http://localhost:11434"
        url = f"{base_url.rstrip('/')}/api/chat"

        messages = [{"role": m.role, "content": m.content} for m in self.conversation_history]

        payload = {"model": self.config.model, "messages": messages, "stream": False}

        # 使用连接池的session
        use_temp_session = self.session is None
        session_to_use = self.session

        try:
            if use_temp_session:
                # 从连接池获取临时session
                session_to_use = self.connection_pool.get_session(base_url)
                print(f"[HTTP连接池] 获取临时session: {base_url}")

            # 执行HTTP请求
            import time

            start_time = time.time()

            async with session_to_use.post(url, json=payload) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"Ollama error: {error}")

                data = await resp.json()

                # 统计信息
                elapsed_ms = int((time.time() - start_time) * 1000)
                print(f"[Ollama] 请求完成 | 耗时 {elapsed_ms}ms | 连接池: {'是' if use_temp_session else '否'}")

                return data["message"]["content"]

        finally:
            if use_temp_session and session_to_use:
                # 释放临时session
                self.connection_pool.release_session(base_url)
                print(f"[HTTP连接池] 释放临时session: {base_url}")

    async def _call_custom(self, tools: Optional[List[Dict]] = None) -> str:
        """调用自定义API"""
        if not self.config.api_base:
            raise ValueError("Custom API base URL not set")

        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        headers["Content-Type"] = "application/json"

        messages = [{"role": m.role, "content": m.content} for m in self.conversation_history]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        async with self.session.post(self.config.api_base, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error = await resp.text()
                raise Exception(f"Custom API error: {error}")

            data = await resp.json()
            # 假设标准格式
            return data["choices"][0]["message"]["content"]

    async def _handle_tool_calls(self, tool_calls: List[Dict]) -> str:
        """处理工具调用（简化实现）"""
        # 实际应该调用MCP工具
        return "[工具调用结果]"

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()

    def get_history(self) -> List[Message]:
        """获取对话历史"""
        return self.conversation_history.copy()


# 便捷函数：创建常用配置的客户端
def create_openai_client(model: str = "gpt-4", api_key: Optional[str] = None) -> LLMClient:
    """创建OpenAI客户端"""
    config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model=model,
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
    )
    return LLMClient(config)


def create_anthropic_client(model: str = "claude-3-sonnet-20240229", api_key: Optional[str] = None) -> LLMClient:
    """创建Anthropic客户端"""
    config = LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model=model,
        api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
    )
    return LLMClient(config)


def create_ollama_client(model: str = "llama2", api_base: str = "http://localhost:11434") -> LLMClient:
    """创建Ollama本地模型客户端"""
    config = LLMConfig(provider=LLMProvider.OLLAMA, model=model, api_base=api_base)
    return LLMClient(config)
