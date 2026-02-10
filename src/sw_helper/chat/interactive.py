"""
交互式AI Chat模式 - 类似opencode的智能助手
集成MCP工具和LLM，实现自然语言控制CAE-CLI
"""

import asyncio
import json
from typing import Optional, List, Dict
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from sw_helper.mcp.core import MCPMessage, InMemoryMCPTransport
from sw_helper.mcp.freecad_server import get_freecad_mcp_server
from sw_helper.ai.llm_client import (
    LLMClient,
    LLMConfig,
    LLMProvider,
    create_openai_client,
)


console = Console()


# 系统提示词
SYSTEM_PROMPT = """你是一个专业的CAE（计算机辅助工程）助手，集成了FreeCAD建模、参数优化和分析功能。

你可以使用以下工具来帮助用户：

1. **FreeCAD建模工具**:
   - freecad_connect: 连接FreeCAD
   - freecad_open: 打开CAD文件
   - freecad_get_parameters: 获取模型参数
   - freecad_set_parameter: 设置参数值
   - freecad_rebuild: 重建模型
   - freecad_export: 导出STEP/STL
   - freecad_create_box: 创建立方体
   - freecad_create_cylinder: 创建圆柱体
   - freecad_apply_fillet: 应用圆角
   - freecad_optimize: 优化参数
   - freecad_analyze: 分析模型质量

2. **CAE-CLI命令**:
   - 解析几何文件
   - 网格质量分析
   - 材料数据库查询
   - 生成分析报告

工作流程建议：
1. 先连接FreeCAD (freecad_connect)
2. 创建或打开模型
3. 修改参数并重建
4. 导出并分析
5. 如果需要，进行优化

请用中文回复用户。当需要调用工具时，请明确说明你在调用什么工具。"""


class OpencodeStyleChat:
    """
    opencode风格的交互式Chat
    集成MCP + LLM + CAE-CLI
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
        self.mcp_server = get_freecad_mcp_server()
        self.mcp_transport = InMemoryMCPTransport(self.mcp_server.server)
        self.running = False
        self.command_history: List[str] = []

    async def start(self):
        """启动交互式聊天"""
        self.running = True

        # 显示欢迎信息
        self._print_welcome()

        # 初始化LLM
        if not self.llm_client:
            await self._setup_llm()

        # 添加系统提示
        if self.llm_client:
            self.llm_client.conversation_history.append(
                {"role": "system", "content": SYSTEM_PROMPT}
            )

        # 主循环
        while self.running:
            try:
                # 获取用户输入
                user_input = await self._get_input()

                if not user_input.strip():
                    continue

                # 处理特殊命令
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                    continue

                # 处理自然语言
                await self._process_natural_language(user_input)

            except KeyboardInterrupt:
                console.print("\n[yellow]再见！[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")

    def _print_welcome(self):
        """打印欢迎信息"""
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              🤖 CAE-CLI Smart Assistant                      ║
║                                                              ║
║     集成 FreeCAD MCP + AI LLM 的智能工程助手                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

支持的命令:
  /help          - 显示帮助
  /tools         - 列出可用工具
  /connect       - 连接FreeCAD
  /mode <type>   - 切换模式 (auto/mcp/cli)
  /clear         - 清空对话
  /exit          - 退出

示例对话:
  "创建一个长100宽50高30的立方体"
  "打开文件 model.FCStd"
  "优化圆角半径从2到15"
  "分析当前模型的质量"

开始您的CAE智能设计之旅！
        """
        console.print(Panel(welcome_text, border_style="cyan"))

    async def _setup_llm(self):
        """设置LLM客户端"""
        console.print("\n[yellow]选择AI模型提供商:[/yellow]")
        console.print("1. OpenAI (GPT-4)")
        console.print("2. Anthropic (Claude)")
        console.print("3. DeepSeek")
        console.print("4. Ollama (本地模型)")
        console.print("5. 跳过 (仅使用MCP工具)")

        choice = Prompt.ask("请选择", choices=["1", "2", "3", "4", "5"], default="1")

        if choice == "1":
            api_key = Prompt.ask("OpenAI API Key", password=True)
            self.llm_client = create_openai_client(api_key=api_key)
            console.print("[green]✓ OpenAI客户端已配置[/green]")
        elif choice == "2":
            api_key = Prompt.ask("Anthropic API Key", password=True)
            from sw_helper.ai.llm_client import create_anthropic_client

            self.llm_client = create_anthropic_client(api_key=api_key)
            console.print("[green]✓ Anthropic客户端已配置[/green]")
        elif choice == "3":
            api_key = Prompt.ask("DeepSeek API Key", password=True)
            config = LLMConfig(
                provider=LLMProvider.DEEPSEEK, model="deepseek-chat", api_key=api_key
            )
            self.llm_client = LLMClient(config)
            console.print("[green]✓ DeepSeek客户端已配置[/green]")
        elif choice == "4":
            model = Prompt.ask("模型名称", default="llama2")
            self.llm_client = create_ollama_client(model=model)
            console.print("[green]✓ Ollama客户端已配置[/green]")
        else:
            console.print("[yellow]⚠ 未配置LLM，将仅使用MCP工具[/yellow]")

    async def _get_input(self) -> str:
        """获取用户输入"""
        return Prompt.ask("\n[bold cyan]You[/bold cyan]")

    async def _handle_command(self, command: str):
        """处理特殊命令"""
        cmd_parts = command.split()
        cmd = cmd_parts[0].lower()
        args = cmd_parts[1:]

        if cmd == "/exit" or cmd == "/quit":
            self.running = False
            console.print("[yellow]再见！[/yellow]")

        elif cmd == "/help":
            self._print_help()

        elif cmd == "/tools":
            await self._list_tools()

        elif cmd == "/connect":
            await self._connect_freecad()

        elif cmd == "/clear":
            if self.llm_client:
                self.llm_client.clear_history()
            console.print("[green]✓ 对话历史已清空[/green]")

        elif cmd == "/mode":
            if args:
                mode = args[0]
                console.print(f"[green]✓ 切换到 {mode} 模式[/green]")
            else:
                console.print("[yellow]用法: /mode <auto/mcp/cli>[/yellow]")
        else:
            console.print(f"[red]未知命令: {cmd}[/red]")

    def _print_help(self):
        """打印帮助信息"""
        help_text = """
## 可用命令

### 系统命令
- `/help` - 显示帮助
- `/exit` - 退出程序
- `/clear` - 清空对话历史
- `/tools` - 列出所有MCP工具
- `/connect` - 连接FreeCAD

### FreeCAD工具
你可以用自然语言描述操作，例如:
- "创建一个立方体，长100宽50高30"
- "打开文件 model.FCStd"
- "设置圆角半径为10mm"
- "导出为STEP格式"
- "优化厚度参数从5到20"

### CAE分析
- "分析当前模型的网格质量"
- "查询材料Q235的属性"
- "生成分析报告"

### 提示
如果不配置LLM，系统将直接解析命令并执行。
配置LLM后，AI会理解复杂指令并规划执行步骤。
        """
        console.print(Markdown(help_text))

    async def _list_tools(self):
        """列出可用工具"""
        tools = self.mcp_server.server.tools

        console.print("\n[bold cyan]可用工具列表:[/bold cyan]")
        for name, tool in tools.items():
            console.print(f"\n[green]{name}[/green]")
            console.print(f"  {tool.description}")

    async def _connect_freecad(self):
        """连接FreeCAD"""
        with console.status("[bold green]连接FreeCAD..."):
            # 调用MCP工具
            message = MCPMessage(
                method="tools/call",
                params={"name": "freecad_connect", "arguments": {"use_mock": True}},
            )
            response = await self.mcp_transport.handle_client_message(message)

            if response.result:
                content = response.result.get("content", [{}])[0].get("text", "")
                result = json.loads(content)
                if result.get("success"):
                    console.print(f"[green]✓ {result.get('message')}[/green]")
                else:
                    console.print("[red]✗ 连接失败[/red]")
            else:
                console.print("[red]✗ 连接错误[/red]")

    async def _process_natural_language(self, text: str):
        """处理自然语言输入"""

        # 如果没有LLM，直接解析执行
        if not self.llm_client:
            await self._direct_execute(text)
            return

        # 使用LLM理解意图
        try:
            async with self.llm_client:
                # 获取可用工具列表
                tools_list = await self._get_tools_for_llm()

                # 调用LLM
                with console.status("[bold green]AI思考中...") as status:
                    response = await self.llm_client.chat(text, tools=tools_list)

                # 显示AI回复
                console.print("\n[bold green]AI[/bold green]")
                console.print(Panel(response, border_style="green"))

                # 检查是否需要执行工具
                await self._check_and_execute_tools(response)

        except Exception as e:
            console.print(f"[red]AI处理错误: {e}[/red]")
            # 回退到直接执行
            await self._direct_execute(text)

    async def _direct_execute(self, text: str):
        """直接解析并执行命令"""
        # 简单的关键字匹配
        text_lower = text.lower()

        if "创建" in text_lower or "create" in text_lower:
            await self._handle_create(text)
        elif "打开" in text_lower or "open" in text_lower:
            await self._handle_open(text)
        elif "优化" in text_lower or "optimize" in text_lower:
            await self._handle_optimize(text)
        elif "分析" in text_lower or "analyze" in text_lower:
            await self._handle_analyze(text)
        else:
            console.print("[yellow]无法理解的命令，尝试使用 /help 查看帮助[/yellow]")

    async def _handle_create(self, text: str):
        """处理创建命令"""
        # 解析参数
        import re

        # 提取数字
        numbers = re.findall(r"(\d+\.?\d*)", text)

        if "立方" in text or "box" in text:
            # 创建立方体
            params = {
                "length": float(numbers[0]) if len(numbers) > 0 else 100,
                "width": float(numbers[1]) if len(numbers) > 1 else 50,
                "height": float(numbers[2]) if len(numbers) > 2 else 30,
            }

            message = MCPMessage(
                method="tools/call",
                params={"name": "freecad_create_box", "arguments": params},
            )

        elif "圆柱" in text or "cylinder" in text:
            # 创建圆柱
            params = {
                "radius": float(numbers[0]) if len(numbers) > 0 else 25,
                "height": float(numbers[1]) if len(numbers) > 1 else 50,
            }

            message = MCPMessage(
                method="tools/call",
                params={"name": "freecad_create_cylinder", "arguments": params},
            )
        else:
            console.print("[yellow]支持的形状: 立方体、圆柱体[/yellow]")
            return

        # 执行
        with console.status("[bold green]创建模型..."):
            response = await self.mcp_transport.handle_client_message(message)
            if response.result:
                content = response.result.get("content", [{}])[0].get("text", "")
                result = json.loads(content)
                console.print(f"[green]✓ {result.get('message', '创建完成')}[/green]")

    async def _handle_open(self, text: str):
        """处理打开文件命令"""
        import re

        # 提取文件路径
        match = re.search(r"[\w\\/]+\.\w+", text)
        if match:
            file_path = match.group()
            message = MCPMessage(
                method="tools/call",
                params={"name": "freecad_open", "arguments": {"file_path": file_path}},
            )

            with console.status(f"[bold green]打开 {file_path}..."):
                response = await self.mcp_transport.handle_client_message(message)
                if response.result:
                    console.print("[green]✓ 文件已打开[/green]")
        else:
            console.print("[yellow]请提供文件路径[/yellow]")

    async def _handle_optimize(self, text: str):
        """处理优化命令"""
        console.print("[yellow]优化功能需要在打开的模型上执行[/yellow]")
        console.print("使用: cae-cli optimize <file> -p <param> -r <min> <max>")

    async def _handle_analyze(self, text: str):
        """处理分析命令"""
        message = MCPMessage(
            method="tools/call", params={"name": "freecad_analyze", "arguments": {}}
        )

        with console.status("[bold green]分析模型..."):
            response = await self.mcp_transport.handle_client_message(message)
            if response.result:
                content = response.result.get("content", [{}])[0].get("text", "")
                result = json.loads(content)
                console.print(
                    f"[green]✓ 质量评分: {result.get('quality_score', 0)}/100[/green]"
                )

    async def _get_tools_for_llm(self) -> List[Dict]:
        """获取工具列表（用于LLM function calling）"""
        tools = []
        for name, tool in self.mcp_server.server.tools.items():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    },
                }
            )
        return tools

    async def _check_and_execute_tools(self, response: str):
        """检查AI回复中是否包含工具调用并执行"""
        # 这里简化实现，实际应该解析LLM的工具调用格式
        # 检查常见的执行关键词
        if "执行" in response or "调用" in response:
            console.print("[dim]AI建议执行相关操作[/dim]")


async def start_chat_mode():
    """启动Chat模式的入口函数"""
    chat = OpencodeStyleChat()
    await chat.start()


# 命令行入口
if __name__ == "__main__":
    asyncio.run(start_chat_mode())
