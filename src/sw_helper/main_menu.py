#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAE-CLI 主菜单模块
三个并列顶层模块：工作模式 / 知识顾问 / 辅助学习
"""

import asyncio
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.markdown import Markdown
from sw_helper.utils.rag_engine import get_rag_engine
from sw_helper.ai.llm_client import LLMClient, LLMConfig, LLMProvider, Message, create_ollama_client
from sw_helper.learning.progress_tracker import get_progress_tracker
from sw_helper.learning.quiz_manager import get_quiz_manager
from sw_helper.utils.first_run import is_first_run, perform_first_run_check

# 项目核心颜色定义
MAIN_RED = "#8B0000"       # 深红/酒红 - 主色调
HIGHLIGHT_RED = "#FF4500"     # 荧光红 - 高亮色
BACKGROUND_BLACK = "#0F0F0F"   # 深黑背景
COOL_GRAY = "#333333"         # 冷灰 - 辅助色
TEXT_WHITE = "#FFFFFF"          # 白色

console = Console()


class MainMenu:
    """主菜单 - 三个并列顶层模块入口"""

    def __init__(self):
        self.running = False

    def start(self):
        """启动主菜单"""
        self.running = True
        self._show_welcome()

        # 首次运行检查
        if is_first_run():
            console.print(f"\n[{HIGHLIGHT_RED}]首次运行检测，正在检查依赖...[/{HIGHLIGHT_RED}]")
            perform_first_run_check(show_guide=True)
            console.print(f"\n[{HIGHLIGHT_RED}]按 Enter 继续...[/{HIGHLIGHT_RED}]")
            from rich.prompt import Prompt
            Prompt.ask("", default="", show_default=False)

        while self.running:
            try:
                self._show_main_menu()
                choice = self._get_user_choice()
                self._handle_choice(choice)
            except KeyboardInterrupt:
                console.print(f"\n[{HIGHLIGHT_RED}]再见！[{HIGHLIGHT_RED}]")
                self.running = False
            except Exception as e:
                console.print(f"[red]错误: {e}[/red]")

    def _show_welcome(self):
        """显示欢迎界面"""
        welcome_text = Text()
        welcome_text.append("CAE-CLI", style=f"bold {HIGHLIGHT_RED}")
        welcome_text.append(" - 机械工程专业学习工具\n", style="white")

        panel = Panel(
            welcome_text,
            title="[bright_red]欢迎[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print("\n")
        console.print(panel)

    def _show_main_menu(self):
        """显示主菜单 - 三个并列选项"""
        console.print("\n")

        # 创建菜单表格
        table = Table(
            title=None,
            show_header=False,
            border_style=MAIN_RED,
            padding=(0, 2),
        )

        table.add_column(style=HIGHLIGHT_RED, width=5)
        table.add_column(style="white", width=40)
        table.add_column(style=f"dim {HIGHLIGHT_RED}", width=35)

        # 工作模式
        table.add_row(
            "[bright_red]1[/bright_red]",
            "[bold white]工作模式[/bold white]",
            "纯粹工具箱 - 分析、优化、报告生成"
        )

        # 知识顾问
        table.add_row(
            "[bright_red]2[/bright_red]",
            "[bold white]知识顾问[/bold white]",
            "快速检索手册、材料参数、公差标准"
        )

        # 辅助学习
        table.add_row(
            "[bright_red]3[/bright_red]",
            "[bold white]辅助学习[/bold white]",
            "系统性学习、教学式解释、进度追踪"
        )

        # 退出
        table.add_row(
            "[bright_red]0[/bright_red]",
            "[bold white]退出[/bold white]",
            "退出程序"
        )

        console.print(table)
        console.print("\n")

    def _get_user_choice(self) -> str:
        """获取用户选择"""
        return Prompt.ask(
            f"[{HIGHLIGHT_RED}]请选择模式[{HIGHLIGHT_RED}]",
            choices=["0", "1", "2", "3"],
            default="1",
            show_choices=False,
        )

    def _handle_choice(self, choice: str):
        """处理用户选择"""
        if choice == "0":
            self.running = False
            console.print(f"\n[{HIGHLIGHT_RED}]再见！[{HIGHLIGHT_RED}]")
        elif choice == "1":
            self._enter_work_mode()
        elif choice == "2":
            self._enter_knowledge_advisor_mode()
        elif choice == "3":
            self._enter_learning_assistant_mode()

    def _enter_work_mode(self):
        """进入工作模式 - 纯粹工具箱"""
        console.print("\n")
        panel = Panel(
            f"[bold white]工作模式[/bold white]\n\n"
            f"机械分析工具箱\n"
            f"- 几何文件解析\n"
            f"- 网格质量分析\n"
            f"- 材料数据库查询\n"
            f"- 参数优化\n"
            f"- 报告生成",
            title="[bright_red]工具模式[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(panel)

        # 显示工作模式菜单
        self._show_work_menu()

        choice = self._get_work_menu_choice()
        self._handle_work_menu_choice(choice)

    def _show_work_menu(self):
        """显示工作模式子菜单"""
        console.print("\n")

        table = Table(
            show_header=False,
            border_style=MAIN_RED,
            padding=(0, 2),
        )

        table.add_column(style=HIGHLIGHT_RED, width=5)
        table.add_column(style="white", width=40)

        table.add_row("[bright_red]1[/bright_red]", "[white]解析几何文件 (parse)[/white]")
        table.add_row("[bright_red]2[/bright_red]", "[white]分析网格质量 (analyze)[/white]")
        table.add_row("[bright_red]3[/bright_red]", "[white]查询材料数据库 (material)[/white]")
        table.add_row("[bright_red]4[/bright_red]", "[white]生成分析报告 (report)[/white]")
        table.add_row("[bright_red]5[/bright_red]", "[white]参数优化 (optimize)[/white]")
        table.add_row("[bright_red]0[/bright_red]", "[white]返回主菜单[/white]")

        console.print(table)
        console.print("\n")

    def _get_work_menu_choice(self) -> str:
        """获取工作模式选择"""
        return Prompt.ask(
            f"[{HIGHLIGHT_RED}]请选择功能[{HIGHLIGHT_RED}]",
            choices=["0", "1", "2", "3", "4", "5"],
            default="0",
            show_choices=False,
        )

    def _handle_work_menu_choice(self, choice: str):
        """处理工作模式选择"""
        if choice == "0":
            # 返回主菜单
            return
        elif choice == "1":
            console.print(f"\n[{HIGHLIGHT_RED}]请使用命令: cae-cli parse <文件>[{HIGHLIGHT_RED}]")
        elif choice == "2":
            console.print(f"\n[{HIGHLIGHT_RED}]请使用命令: cae-cli analyze <文件>[{HIGHLIGHT_RED}]")
        elif choice == "3":
            console.print(f"\n[{HIGHLIGHT_RED}]请使用命令: cae-cli material <材料名>[{HIGHLIGHT_RED}]")
        elif choice == "4":
            console.print(f"\n[{HIGHLIGHT_RED}]请使用命令: cae-cli report <类型> -i <文件>[{HIGHLIGHT_RED}]")
        elif choice == "5":
            console.print(f"\n[{HIGHLIGHT_RED}]请使用命令: cae-cli optimize <文件> -p <参数>[{HIGHLIGHT_RED}]")

        # 按任意键返回
        Prompt.ask(f"\n[{HIGHLIGHT_RED}]按 Enter 返回主菜单...[{HIGHLIGHT_RED}]")

    def _enter_knowledge_advisor_mode(self):
        """进入知识顾问模式 - 极简检索"""
        console.print("\n")
        panel = Panel(
            f"[bold white]知识顾问模式[/bold white]\n\n"
            f"快速精准检索 knowledge/ 目录\n\n"
            f"[dim]- 手册内容查询[/dim]\n"
            f"[dim]- 材料参数查询[/dim]\n"
            f"[dim]- 公差标准查询[/dim]\n"
            f"[dim]- 公式查询[/dim]",
            title="[bright_red]知识顾问[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(panel)

        # 进入知识顾问循环
        self._knowledge_advisor_loop()

    def _knowledge_advisor_loop(self):
        """知识顾问检索循环 - 极简检索，表格化输出"""
        # 初始化RAG引擎（单例）
        try:
            rag_engine = get_rag_engine()
            if not rag_engine.is_available():
                console.print(f"\n[red]RAG引擎不可用[/red]")
                console.print(f"[dim]请检查sentence-transformers依赖，或使用离线模式。[/dim]")
                console.print(f"[dim]知识顾问功能受限，将使用简单关键词匹配。[/dim]")
                rag_available = False
            else:
                rag_available = True
        except Exception as e:
            console.print(f"\n[yellow]RAG引擎初始化异常: {e}[/yellow]")
            rag_available = False

        while True:
            console.print("\n")
            keyword = Prompt.ask(f"[{HIGHLIGHT_RED}]输入搜索关键词 (或 '0' 返回)[{HIGHLIGHT_RED}]")

            if keyword == "0":
                return

            if not keyword.strip():
                console.print(f"[red]请输入有效关键词[/red]")
                continue

            console.print(f"\n[green]正在检索...[/green]")
            console.print(f"[dim]当前模式: phi3:mini (优先速度和结构化输出)[/dim]")

            results = []
            if rag_available:
                # 使用RAG向量检索
                try:
                    results = rag_engine.search(keyword, top_k=3, max_length=150)
                except Exception as e:
                    console.print(f"[red]检索失败: {e}[/red]")
                    results = []
            else:
                # 降级：简单关键词匹配（极简实现）
                results = self._simple_keyword_search(keyword)

            # 显示结果
            if not results:
                console.print(f"\n[{HIGHLIGHT_RED}]未找到相关结果。尝试其他关键词。[/{HIGHLIGHT_RED}]")
                continue

            # 用表格展示检索结果
            self._display_results_table(results, keyword)

    def _simple_keyword_search(self, keyword: str) -> List[Dict[str, Any]]:
        """简单关键词搜索（降级方案）- 读取knowledge目录的markdown文件"""
        results = []
        knowledge_dir = Path("knowledge")

        if not knowledge_dir.exists():
            return results

        # 遍历knowledge目录的.md文件
        for md_file in knowledge_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 简单关键词匹配（不区分大小写）
                if keyword.lower() in content.lower():
                    # 提取包含关键词的段落（简单实现）
                    lines = content.split('\n')
                    for line in lines:
                        if keyword.lower() in line.lower() and line.strip():
                            # 截断过长的行
                            preview = line.strip()[:150] + ("..." if len(line.strip()) > 150 else "")
                            results.append({
                                "content": preview,
                                "source": md_file.name,
                                "distance": 1.0  # 简单搜索没有距离，设为1.0
                            })
                            break  # 每个文件只取第一个匹配行
            except Exception as e:
                continue  # 忽略读取错误

        return results[:3]  # 最多返回3个结果

    def _display_results_table(self, results: List[Dict[str, Any]], query: str):
        """用表格展示检索结果 - 极简风格"""
        if not results:
            return

        console.print(f"\n[{HIGHLIGHT_RED}]检索结果 (关键词: '{query}'):[/{HIGHLIGHT_RED}]")

        # 创建结果表格
        table = Table(
            title=None,
            show_header=True,
            header_style=f"bold {HIGHLIGHT_RED}",
            border_style=MAIN_RED,
            padding=(0, 1),
        )

        table.add_column("序号", style=HIGHLIGHT_RED, width=5, justify="center")
        table.add_column("内容", style="white", width=70)
        table.add_column("来源", style=f"dim {COOL_GRAY}", width=20)

        for i, result in enumerate(results, 1):
            content = result.get("content", "").strip()
            source = result.get("source", "未知来源")

            # 相似度显示（如果有）
            distance = result.get("distance", 1.0)
            similarity = 1.0 - distance if distance <= 1.0 else 0.0

            # 格式化内容，添加相似度标签（RAG结果才显示）
            if distance < 1.0:  # RAG结果
                content_display = f"[white]{content}[/white]\n[dim]相似度: {similarity:.2%}[/dim]"
            else:  # 简单搜索结果
                content_display = f"[white]{content}[/white]"

            table.add_row(
                f"[bright_red]{i}[/bright_red]",
                content_display,
                f"[dim]{source}[/dim]"
            )

        console.print(table)
        console.print("\n")

    def _enter_learning_assistant_mode(self):
        """进入辅助学习模式 - 教学式对话"""
        console.print("\n")
        panel = Panel(
            f"[bold white]辅助学习模式[/bold white]\n\n"
            f"系统性学习 + 教学式解释\n\n"
            f"[dim]- 概念深度讲解[/dim]\n"
            f"[dim]- 一步步引导[/dim]\n"
            f"[dim]- 学习进度追踪[/dim]\n"
            f"[dim]- 练习题生成[/dim]",
            title="[bright_red]辅助学习[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(panel)

        # 进入学习模式循环（异步）
        try:
            asyncio.run(self._learning_assistant_loop())
        except KeyboardInterrupt:
            console.print(f"\n[{HIGHLIGHT_RED}]返回主菜单[/{HIGHLIGHT_RED}]")
        except Exception as e:
            console.print(f"[red]学习模式异常: {e}[/red]")

    async def _learning_assistant_loop(self):
        """辅助学习对话循环 - 教学式多轮对话"""
        console.print(f"\n[green]初始化辅助学习系统...[/green]")

        # 初始化RAG引擎
        rag_engine = None
        try:
            rag_engine = get_rag_engine()
            if not rag_engine.is_available():
                console.print(f"[yellow]RAG引擎不可用，知识库检索功能受限[/yellow]")
                rag_engine = None
            else:
                console.print(f"[green][OK] 知识库检索引擎就绪[/green]")
        except Exception as e:
            console.print(f"[yellow]RAG引擎异常: {e}[/yellow]")
            rag_engine = None

        # 初始化Ollama客户端
        llm_client = None
        try:
            # 尝试连接Ollama服务
            ollama_available = self._check_ollama_available()
            if not ollama_available:
                console.print(f"[red]Ollama服务不可用[/red]")
                console.print(f"[dim]请确保已安装并启动Ollama，模型 qwen2.5:1.5b 或 phi3:mini 可用[/dim]")
                console.print(f"[dim]辅助学习模式将降级到本地知识库检索[/dim]")
            else:
                # 创建Ollama客户端，默认使用qwen2.5:1.5b
                try:
                    llm_client = create_ollama_client(model="qwen2.5:1.5b")
                    console.print(f"[green][OK] Ollama客户端就绪 (模型: qwen2.5:1.5b)[/green]")
                except Exception as e:
                    console.print(f"[yellow]无法加载qwen2.5:1.5b: {e}[/yellow]")
                    console.print(f"[dim]尝试回退到phi3:mini...[/dim]")
                    try:
                        llm_client = create_ollama_client(model="phi3:mini")
                        console.print(f"[green][OK] Ollama客户端就绪 (模型: phi3:mini)[/green]")
                    except Exception as e2:
                        console.print(f"[red]无法加载任何Ollama模型: {e2}[/red]")
                        llm_client = None
        except Exception as e:
            console.print(f"[red]Ollama初始化异常: {e}[/red]")
            llm_client = None

        # 定义教学式系统提示词
        system_prompt = """# 角色：机械工程教学助手

你是一位专业、耐心的机械工程教学助手，专门帮助大一学生理解机械工程基础知识。你的教学风格应该：

## 教学原则
1. **循序渐进**：从基础概念开始，逐步深入
2. **举例说明**：每个概念都要配现实世界的例子
3. **比喻解释**：用生活中的比喻帮助理解抽象概念
4. **鼓励提问**：鼓励学生多问为什么
5. **检查理解**：适当时候提问确认学生是否理解

## 回答结构
1. **概念定义**：先给出清晰的定义
2. **重要性说明**：解释为什么这个概念重要
3. **详细解释**：逐步深入解释细节
4. **应用示例**：给出实际的工程应用例子
5. **常见误区**：指出学生常见的理解误区
6. **学习建议**：提供进一步学习建议

## 语言风格
- 用中文教学，语气亲切但不随意
- 使用"我们"而不是"你"，体现共同学习
- 适当使用表情符号增强亲和力😊
- 复杂概念分步骤解释

## 知识库集成
当你回答时，会先获得相关知识库的检索结果。请基于这些知识进行教学，但不要简单重复。将知识库内容融入你的教学解释中。

现在开始帮助学生学习机械工程吧！"""

        # 初始化对话历史
        conversation_history = []
        if llm_client:
            # 添加系统提示到LLM客户端
            llm_client.conversation_history.append(Message(role="system", content=system_prompt))
            conversation_history.append({"role": "system", "content": system_prompt})

        # 初始化进度追踪器
        progress_tracker = get_progress_tracker()

        # 显示当前学习进度
        progress_summary = progress_tracker.get_progress_summary()
        completed_count = progress_summary["completed_topics"]
        total_study_time = progress_summary["statistics"]["total_study_time_seconds"]

        progress_text = f"[bold white]当前学习进度[/bold white]\n\n"
        progress_text += f"[dim]已掌握知识点:[/dim] [bright_red]{completed_count}[/bright_red] 个\n"
        progress_text += f"[dim]总学习时间:[/dim] [bright_red]{total_study_time}[/bright_red] 秒\n"

        if progress_summary["by_source"]:
            progress_text += f"\n[dim]按知识库分类:[/dim]\n"
            for source, count in progress_summary["by_source"].items():
                progress_text += f"  [white]{source}:[/white] [bright_red]{count}[/bright_red] 个知识点\n"

        # 显示已解锁成就（徽章形式）
        unlocked_achievements = progress_tracker.get_unlocked_achievements()
        if unlocked_achievements:
            progress_text += f"\n[dim]已解锁成就:[/dim] [bright_red]{len(unlocked_achievements)}[/bright_red] 个 ([bright_red]{progress_tracker.get_total_achievement_points()}[/bright_red] 点)"

            # 按点数分组显示
            achievements_by_points = {}
            for ach in unlocked_achievements:
                points = ach.get("points", 10)
                if points not in achievements_by_points:
                    achievements_by_points[points] = []
                achievements_by_points[points].append(ach)

            # 显示徽章（按点数排序，点数高的先显示）
            sorted_points = sorted(achievements_by_points.keys(), reverse=True)
            for points in sorted_points[:2]:  # 最多显示2个点数级别
                ach_list = achievements_by_points[points]
                progress_text += f"\n  [bright_red]★ {points}点:[/bright_red] "
                progress_text += f"[white]{ach_list[0]['name']}[/white]"
                if len(ach_list) > 1:
                    progress_text += f" 等{len(ach_list)}个"

            if len(unlocked_achievements) > 0:
                progress_text += f"\n  [dim]输入'成就'查看所有成就徽章[/dim]"
        else:
            progress_text += f"\n[dim]已解锁成就:[/dim] [bright_red]0[/bright_red] 个 ([dim]暂无徽章[/dim])"
            progress_text += f"\n  [dim]输入'成就'查看可解锁成就[/dim]"

        progress_panel = Panel(
            progress_text,
            title="[bright_red]学习进度[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(progress_panel)

        console.print(f"\n[{HIGHLIGHT_RED}]教学助手已就绪！输入你的问题，我会一步步教你。[/{HIGHLIGHT_RED}]")
        console.print(f"[{HIGHLIGHT_RED}]特殊命令: '成就'查看成就徽章 | '测验'开始自测 | '进度'查看详细进度 | '0'返回主菜单[/{HIGHLIGHT_RED}]")

        # 多轮对话循环
        while True:
            console.print("\n")
            question = Prompt.ask(f"[{HIGHLIGHT_RED}]你的问题[{HIGHLIGHT_RED}]")

            if question == "0":
                return

            # 特殊命令处理
            if question.lower() in ["成就", "achievements", "徽章"]:
                self._show_achievements_badges(progress_tracker)
                continue
            elif question.lower() in ["进度", "progress", "统计"]:
                self._show_detailed_progress(progress_tracker)
                continue
            elif question.lower() in ["测验", "quiz", "测试"]:
                self._start_quiz_session(progress_tracker)
                continue

            if not question.strip():
                console.print(f"[red]请输入有效问题[/red]")
                continue

            # 检索相关知识
            knowledge_context = ""
            results = []  # 初始化结果列表
            if rag_engine:
                try:
                    results = rag_engine.search(question, top_k=2, max_length=500)
                    if results:
                        knowledge_context = "\n## 相关知识点（来自知识库）\n"
                        for i, result in enumerate(results, 1):
                            content = result.get("content", "").strip()
                            source = result.get("source", "未知来源")
                            similarity = 1.0 - result.get("distance", 1.0)
                            knowledge_context += f"\n**知识点 {i}** (来源: {source}, 相关性: {similarity:.1%}):\n{content}\n"
                except Exception as e:
                    console.print(f"[yellow]知识库检索失败: {e}[/yellow]")

            # 构建完整的用户消息（包含知识库上下文）
            user_message = question
            if knowledge_context:
                user_message = f"{knowledge_context}\n\n## 学生的问题\n{question}"

            # 保存用户消息到历史
            conversation_history.append({"role": "user", "content": user_message})

            # 生成回答
            console.print(f"\n[green]正在生成教学式回答...[/green]")

            if llm_client:
                # 使用Ollama生成回答
                try:
                    # 异步调用
                    response = await self._async_chat(llm_client, user_message)

                    # 显示回答
                    console.print("\n")
                    console.print(Panel(
                        Markdown(response),
                        title="[bright_red]教学助手[/bright_red]",
                        border_style=MAIN_RED,
                        padding=(1, 2),
                    ))

                    # 保存助手回复到历史
                    conversation_history.append({"role": "assistant", "content": response})

                    # 更新学习进度 - 标记相关知识点为已学习
                    if results:  # 使用之前检索到的results
                        # 记录更新前的成就ID
                        before_achievements = progress_tracker.get_unlocked_achievements()
                        before_ids = {ach["achievement_id"] for ach in before_achievements}

                        for result in results:
                            source = result.get("source", "")
                            content_preview = result.get("content", "")[:100]  # 取前100字符作为主题

                            # 生成知识点ID：文件#行号或内容哈希
                            import hashlib
                            content_hash = hashlib.md5(content_preview.encode()).hexdigest()[:8]
                            knowledge_id = f"{source.replace('.md', '')}#{content_hash}"

                            # 提取标签（基于源文件）
                            tags = []
                            if "material" in source.lower():
                                tags.append("材料")
                            if "fastener" in source.lower():
                                tags.append("紧固件")
                            if "tolerance" in source.lower():
                                tags.append("公差")
                            if "standard" in source.lower():
                                tags.append("标准件")

                            # 标记为已学习（学习时间估算：30秒 + 根据内容长度计算）
                            content_length = len(result.get("content", ""))
                            study_time = min(30 + content_length // 10, 300)  # 最多5分钟

                            progress_tracker.mark_topic_completed(
                                knowledge_id=knowledge_id,
                                topic=f"知识点: {content_preview}...",
                                source_file=source,
                                study_time_seconds=study_time,
                                tags=tags
                            )

                        # 保存进度
                        progress_tracker.save()

                        # 显示进度更新
                        completed_now = len(results)
                        console.print(f"\n[green][OK] 已记录 {completed_now} 个知识点学习进度[/green]")

                        # 检查并显示新解锁的成就
                        self._check_and_display_new_achievements(progress_tracker, before_ids)

                except Exception as e:
                    console.print(f"[red]生成回答失败: {e}[/red]")
                    console.print(f"[dim]将使用知识库内容回复...[/dim]")

                    # 降级：显示知识库内容
                    if knowledge_context:
                        console.print("\n")
                        console.print(Panel(
                            Markdown(knowledge_context + "\n\n**由于AI模型不可用，以上是知识库检索结果。**"),
                            title="[bright_red]知识库检索结果[/bright_red]",
                            border_style=MAIN_RED,
                            padding=(1, 2),
                        ))

                        # 更新学习进度 - 标记相关知识点为已学习
                        if results:
                            # 记录更新前的成就ID
                            before_achievements = progress_tracker.get_unlocked_achievements()
                            before_ids = {ach["achievement_id"] for ach in before_achievements}

                            for result in results:
                                source = result.get("source", "")
                                content_preview = result.get("content", "")[:100]

                                import hashlib
                                content_hash = hashlib.md5(content_preview.encode()).hexdigest()[:8]
                                knowledge_id = f"{source.replace('.md', '')}#{content_hash}"

                                tags = []
                                if "material" in source.lower():
                                    tags.append("材料")
                                if "fastener" in source.lower():
                                    tags.append("紧固件")
                                if "tolerance" in source.lower():
                                    tags.append("公差")
                                if "standard" in source.lower():
                                    tags.append("标准件")

                                content_length = len(result.get("content", ""))
                                study_time = min(30 + content_length // 10, 300)

                                progress_tracker.mark_topic_completed(
                                    knowledge_id=knowledge_id,
                                    topic=f"知识点: {content_preview}...",
                                    source_file=source,
                                    study_time_seconds=study_time,
                                    tags=tags
                                )

                            progress_tracker.save()
                            console.print(f"\n[green][OK] 已记录 {len(results)} 个知识点学习进度[/green]")

                            # 检查并显示新解锁的成就
                            self._check_and_display_new_achievements(progress_tracker, before_ids)
                    else:
                        console.print(f"\n[{HIGHLIGHT_RED}]抱歉，无法生成回答。请检查Ollama服务或尝试其他问题。[/{HIGHLIGHT_RED}]")
            else:
                # 无AI模型，仅显示知识库内容
                if knowledge_context:
                    console.print("\n")
                    console.print(Panel(
                        Markdown(knowledge_context + "\n\n**提示：启动Ollama服务可获得更好的教学式解释**"),
                        title="[bright_red]知识库检索结果[/bright_red]",
                        border_style=MAIN_RED,
                        padding=(1, 2),
                    ))

                    # 更新学习进度 - 标记相关知识点为已学习
                    if results:
                        # 记录更新前的成就ID
                        before_achievements = progress_tracker.get_unlocked_achievements()
                        before_ids = {ach["achievement_id"] for ach in before_achievements}

                        for result in results:
                            source = result.get("source", "")
                            content_preview = result.get("content", "")[:100]

                            import hashlib
                            content_hash = hashlib.md5(content_preview.encode()).hexdigest()[:8]
                            knowledge_id = f"{source.replace('.md', '')}#{content_hash}"

                            tags = []
                            if "material" in source.lower():
                                tags.append("材料")
                            if "fastener" in source.lower():
                                tags.append("紧固件")
                            if "tolerance" in source.lower():
                                tags.append("公差")
                            if "standard" in source.lower():
                                tags.append("标准件")

                            content_length = len(result.get("content", ""))
                            study_time = min(30 + content_length // 10, 300)

                            progress_tracker.mark_topic_completed(
                                knowledge_id=knowledge_id,
                                topic=f"知识点: {content_preview}...",
                                source_file=source,
                                study_time_seconds=study_time,
                                tags=tags
                            )

                        progress_tracker.save()
                        console.print(f"\n[green][OK] 已记录 {len(results)} 个知识点学习进度[/green]")

                        # 检查并显示新解锁的成就
                        self._check_and_display_new_achievements(progress_tracker, before_ids)
                else:
                    console.print(f"\n[{HIGHLIGHT_RED}]未找到相关知识。请尝试其他问题或启动Ollama服务。[/{HIGHLIGHT_RED}]")

            console.print(f"\n[{HIGHLIGHT_RED}]继续问吧～ 输入'0'返回主菜单[/{HIGHLIGHT_RED}]")

    def _check_ollama_available(self) -> bool:
        """检查Ollama服务是否可用"""
        import aiohttp
        import asyncio

        async def check():
            try:
                async with aiohttp.ClientSession() as session:
                    # 尝试连接Ollama API
                    async with session.get("http://localhost:11434/api/tags", timeout=5) as resp:
                        return resp.status == 200
            except:
                return False

        try:
            # 同步环境中运行异步检查
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(check())
            loop.close()
            return result
        except:
            return False

    async def _async_chat(self, llm_client: LLMClient, question: str) -> str:
        """异步调用LLM聊天（封装异步操作）"""
        import asyncio

        try:
            # 设置30秒超时
            async with asyncio.timeout(30):
                try:
                    # 使用异步上下文管理器
                    async with llm_client:
                        response = await llm_client.chat(question)
                        return response
                except Exception as e:
                    # 如果异步上下文失败，尝试直接调用
                    try:
                        return await llm_client.chat(question)
                    except:
                        raise e
        except asyncio.TimeoutError:
            raise TimeoutError("LLM响应超时（30秒），请检查Ollama服务状态或尝试简化问题")

    def _show_achievements_badges(self, progress_tracker):
        """显示成就徽章页面"""
        console.print("\n")
        panel = Panel(
            f"[bold white]成就徽章系统[/bold white]\n\n"
            f"完成学习任务，解锁专属徽章！\n\n"
            f"[dim]每个成就都有对应的点数，点数越高代表成就越难获得。[/dim]",
            title="[bright_red]🏆 成就大厅 🏆[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(panel)

        # 获取成就数据
        all_achievements = progress_tracker.get_achievements()
        unlocked_achievements = progress_tracker.get_unlocked_achievements()
        locked_achievements = [ach for ach in all_achievements if not ach.get("unlocked", False)]
        total_points = progress_tracker.get_total_achievement_points()

        # 显示总览
        overview_text = f"[bold white]成就总览[/bold white]\n\n"
        overview_text += f"[dim]总成就数:[/dim] [bright_red]{len(all_achievements)}[/bright_red] 个\n"
        overview_text += f"[dim]已解锁:[/dim] [bright_red]{len(unlocked_achievements)}[/bright_red] 个\n"
        overview_text += f"[dim]未解锁:[/dim] [bright_red]{len(locked_achievements)}[/bright_red] 个\n"
        overview_text += f"[dim]总成就点数:[/dim] [bright_red]{total_points}[/bright_red] 点\n"

        # 解锁进度条
        if all_achievements:
            unlock_rate = (len(unlocked_achievements) / len(all_achievements)) * 100
            overview_text += f"\n[dim]解锁进度:[/dim] [white]{unlock_rate:.1f}%[/white]"
            # 简单进度条
            progress_bar_length = 20
            filled = int(unlock_rate / 100 * progress_bar_length)
            progress_bar = "█" * filled + "░" * (progress_bar_length - filled)
            overview_text += f"\n[green]{progress_bar}[/green]\n"

        overview_panel = Panel(
            overview_text,
            title="[bright_red]📊 统计[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(overview_panel)

        # 显示已解锁成就（徽章形式）
        if unlocked_achievements:
            console.print(f"\n[{HIGHLIGHT_RED}]🎖️ 已解锁成就徽章 [{HIGHLIGHT_RED}]")

            # 按点数排序，高的在前
            unlocked_sorted = sorted(unlocked_achievements, key=lambda x: x.get("points", 0), reverse=True)

            # 用表格显示成就徽章
            table = Table(
                show_header=True,
                header_style=f"bold {HIGHLIGHT_RED}",
                border_style=MAIN_RED,
                padding=(0, 1),
            )
            table.add_column("徽章", style=HIGHLIGHT_RED, width=5, justify="center")
            table.add_column("名称", style="white", width=20)
            table.add_column("描述", style="white", width=40)
            table.add_column("点数", style=f"bright_red", width=8, justify="center")
            table.add_column("解锁时间", style=f"dim {COOL_GRAY}", width=15)

            for ach in unlocked_sorted:
                # 徽章符号根据点数不同
                points = ach.get("points", 10)
                if points >= 30:
                    badge = "🏆"
                elif points >= 20:
                    badge = "⭐"
                else:
                    badge = "[OK]"

                table.add_row(
                    f"[bright_red]{badge}[/bright_red]",
                    f"[bold white]{ach['name']}[/bold white]",
                    f"[white]{ach['description']}[/white]",
                    f"[bright_red]{points}[/bright_red]",
                    f"[dim]{ach.get('unlock_time', '未知')[:10]}[/dim]" if ach.get('unlock_time') else "[dim]未知[/dim]"
                )

            console.print(table)
        else:
            console.print(f"\n[{HIGHLIGHT_RED}]尚无已解锁成就，开始学习吧！[/{HIGHLIGHT_RED}]")

        # 显示未解锁成就（可预览）
        if locked_achievements:
            console.print(f"\n[{HIGHLIGHT_RED}]🔒 可解锁成就（预览）[{HIGHLIGHT_RED}]")
            console.print(f"[dim]完成以下任务来解锁成就：[/dim]\n")

            # 只显示前5个未解锁成就
            for i, ach in enumerate(locked_achievements[:5], 1):
                points = ach.get("points", 10)
                console.print(f"  [bright_red]{i}.[/bright_red] [white]{ach['name']}[/white] ([bright_red]{points}[/bright_red]点)")
                console.print(f"     [dim]{ach['description']}[/dim]")

            if len(locked_achievements) > 5:
                console.print(f"  [dim]...还有 {len(locked_achievements)-5} 个成就等待解锁[/dim]")

        console.print(f"\n[{HIGHLIGHT_RED}]输入任何内容返回学习...[{HIGHLIGHT_RED}]")
        Prompt.ask(f"[{HIGHLIGHT_RED}]按 Enter 继续...[{HIGHLIGHT_RED}]")

    def _show_detailed_progress(self, progress_tracker):
        """显示详细学习进度"""
        console.print("\n")
        progress_summary = progress_tracker.get_progress_summary()
        achievement_summary = progress_tracker.get_achievement_summary()

        # 创建进度详情面板
        progress_text = f"[bold white]📈 详细学习进度[/bold white]\n\n"

        # 基础统计
        completed_count = progress_summary["completed_topics"]
        total_topics = progress_summary["total_topics"]
        completion_rate = progress_summary["completion_rate"]
        total_study_time = progress_summary["statistics"]["total_study_time_seconds"]

        progress_text += f"[dim]已掌握知识点:[/dim] [bright_red]{completed_count}[/bright_red] / [white]{total_topics}[/white] 个\n"
        progress_text += f"[dim]掌握率:[/dim] [bright_red]{completion_rate:.1f}%[/bright_red]\n"
        progress_text += f"[dim]总学习时间:[/dim] [bright_red]{total_study_time}[/bright_red] 秒 ([bright_red]{total_study_time/60:.1f}[/bright_red] 分钟)\n"
        if progress_summary["statistics"]["last_study_date"]:
            progress_text += f"[dim]最近学习:[/dim] [white]{progress_summary['statistics']['last_study_date']}[/white]\n"

        # 按来源分类
        if progress_summary["by_source"]:
            progress_text += f"\n[dim]📚 按知识库分类:[/dim]\n"
            for source, count in progress_summary["by_source"].items():
                progress_text += f"  [white]{source}:[/white] [bright_red]{count}[/bright_red] 个知识点\n"

        # 按标签分类
        if progress_summary["by_tag"]:
            progress_text += f"\n[dim]🏷️ 按标签分类:[/dim]\n"
            sorted_tags = sorted(progress_summary["by_tag"].items(), key=lambda x: x[1], reverse=True)[:5]  # 前5个
            for tag, count in sorted_tags:
                progress_text += f"  [white]{tag}:[/white] [bright_red]{count}[/bright_red] 次\n"

        progress_panel = Panel(
            progress_text,
            title="[bright_red]学习进度详情[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(progress_panel)

        # 成就统计面板
        achievement_text = f"[bold white]🎯 成就统计[/bold white]\n\n"
        achievement_text += f"[dim]总成就数:[/dim] [bright_red]{achievement_summary['total_achievements']}[/bright_red] 个\n"
        achievement_text += f"[dim]已解锁:[/dim] [bright_red]{achievement_summary['unlocked_count']}[/bright_red] 个\n"
        achievement_text += f"[dim]未解锁:[/dim] [bright_red]{achievement_summary['locked_count']}[/bright_red] 个\n"
        achievement_text += f"[dim]解锁率:[/dim] [bright_red]{achievement_summary['unlock_rate']:.1f}%[/bright_red]\n"
        achievement_text += f"[dim]总成就点数:[/dim] [bright_red]{achievement_summary['total_points']}[/bright_red] 点\n"

        if achievement_summary["points_distribution"]:
            achievement_text += f"\n[dim]点数分布:[/dim]\n"
            for points, count in sorted(achievement_summary["points_distribution"].items(), reverse=True):
                achievement_text += f"  [white]{points}[/white]点成就: [bright_red]{count}[/bright_red] 个\n"

        achievement_panel = Panel(
            achievement_text,
            title="[bright_red]成就统计[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(achievement_panel)

        console.print(f"\n[{HIGHLIGHT_RED}]输入任何内容返回学习...[{HIGHLIGHT_RED}]")
        Prompt.ask(f"[{HIGHLIGHT_RED}]按 Enter 继续...[{HIGHLIGHT_RED}]")

    def _start_quiz_session(self, progress_tracker):
        """开始自测测验"""
        console.print("\n")
        panel = Panel(
            f"[bold white]自测题库[/bold white]\n\n"
            f"测试你的机械工程知识掌握程度！\n\n"
            f"[dim]• 每次测验随机抽取题目[/dim]\n"
            f"[dim]• 答对题目可获得成就点数[/dim]\n"
            f"[dim]• 测验结果计入学习进度[/dim]",
            title="[bright_red]📝 知识测验[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(panel)

        # 获取题库管理器
        try:
            quiz_manager = get_quiz_manager()
            if not quiz_manager.loaded:
                if not quiz_manager.load_all_quizzes():
                    console.print(f"\n[red]题库加载失败，请检查data/quiz目录是否有题库文件[/red]")
                    Prompt.ask(f"[{HIGHLIGHT_RED}]按 Enter 返回...[{HIGHLIGHT_RED}]")
                    return
        except Exception as e:
            console.print(f"\n[red]题库初始化失败: {e}[/red]")
            Prompt.ask(f"[{HIGHLIGHT_RED}]按 Enter 返回...[{HIGHLIGHT_RED}]")
            return

        # 选择测验设置
        console.print(f"\n[{HIGHLIGHT_RED}]测验设置:[/{HIGHLIGHT_RED}]")
        console.print(f"[dim]1. 快速测验 (3题)[/dim]")
        console.print(f"[dim]2. 标准测验 (5题)[/dim]")
        console.print(f"[dim]3. 综合测验 (8题)[/dim]")
        console.print(f"[dim]0. 返回[/dim]")

        choice = Prompt.ask(
            f"[{HIGHLIGHT_RED}]选择测验类型[{HIGHLIGHT_RED}]",
            choices=["0", "1", "2", "3"],
            default="2",
            show_choices=False,
        )

        if choice == "0":
            return

        # 确定题目数量
        if choice == "1":
            question_count = 3
        elif choice == "2":
            question_count = 5
        else:
            question_count = 8

        # 开始测验
        console.print(f"\n[green]正在准备 {question_count} 道题目...[/green]")
        questions = quiz_manager.get_random_questions(count=question_count)

        if not questions:
            console.print(f"\n[red]题库中没有足够的题目，请检查题库文件[/red]")
            Prompt.ask(f"[{HIGHLIGHT_RED}]按 Enter 返回...[{HIGHLIGHT_RED}]")
            return

        console.print(f"\n[{HIGHLIGHT_RED}]测验开始！请认真回答每题。[/{HIGHLIGHT_RED}]")

        results = []
        correct_count = 0
        total_time = 0

        import time
        for i, question in enumerate(questions, 1):
            console.print(f"\n[{HIGHLIGHT_RED}]题目 {i}/{len(questions)}:[/{HIGHLIGHT_RED}]")
            console.print(f"[bold white]{question.question}[/bold white]")
            console.print(f"[dim]类别: {question.category} | 难度: {question.difficulty.value}[/dim]")
            console.print("")

            # 显示选项
            for j, option in enumerate(question.options, 1):
                console.print(f"  [bright_red]{j}.[/bright_red] [white]{option.text}[/white]")

            # 获取用户选择
            start_time = time.time()
            while True:
                try:
                    user_choice = Prompt.ask(
                        f"[{HIGHLIGHT_RED}]你的答案 (1-{len(question.options)})[{HIGHLIGHT_RED}]",
                        show_choices=False,
                    )
                    selected_index = int(user_choice) - 1
                    if 0 <= selected_index < len(question.options):
                        break
                    console.print(f"[red]请输入 1-{len(question.options)} 之间的数字[/red]")
                except ValueError:
                    console.print(f"[red]请输入有效数字[/red]")

            end_time = time.time()
            time_spent = end_time - start_time
            total_time += time_spent

            # 检查答案
            is_correct, correct_idx, explanation = quiz_manager.check_answer(question, selected_index)

            # 显示结果
            console.print("")
            if is_correct:
                console.print(f"[green][OK] 回答正确！用时 {time_spent:.1f} 秒[/green]")
                correct_count += 1
            else:
                console.print(f"[red]✗ 回答错误！用时 {time_spent:.1f} 秒[/red]")
                console.print(f"[dim]正确答案是选项 {correct_idx + 1}[/dim]")

            console.print(f"\n[dim]💡 解释: {explanation}[/dim]")

            # 记录结果
            results.append({
                "question_id": question.id,
                "knowledge_id": question.knowledge_id,
                "selected_option_index": selected_index,
                "correct_option_index": correct_idx,
                "is_correct": is_correct,
                "time_spent_seconds": time_spent,
                "score": 100 if is_correct else 0
            })

            if i < len(questions):
                console.print(f"\n[{HIGHLIGHT_RED}]按 Enter 继续下一题...[{HIGHLIGHT_RED}]")
                Prompt.ask("", default="", show_default=False)

        # 显示测验结果
        console.print(f"\n[{HIGHLIGHT_RED}]🎉 测验完成！[/{HIGHLIGHT_RED}]")

        score_percentage = (correct_count / len(questions)) * 100
        avg_time = total_time / len(questions) if questions else 0

        result_text = f"[bold white]测验结果[/bold white]\n\n"
        result_text += f"[dim]答题数:[/dim] [bright_red]{len(questions)}[/bright_red] 题\n"
        result_text += f"[dim]答对题数:[/dim] [bright_red]{correct_count}[/bright_red] 题\n"
        result_text += f"[dim]正确率:[/dim] [bright_red]{score_percentage:.1f}%[/bright_red]\n"
        result_text += f"[dim]平均用时:[/dim] [bright_red]{avg_time:.1f}[/bright_red] 秒/题\n"
        result_text += f"[dim]总用时:[/dim] [bright_red]{total_time:.1f}[/bright_red] 秒\n"

        # 等级评价
        if score_percentage >= 90:
            rating = "[bright_red]🎖️ 优秀[/bright_red]"
        elif score_percentage >= 70:
            rating = "[green]👍 良好[/green]"
        elif score_percentage >= 50:
            rating = "[yellow]📚 一般[/yellow]"
        else:
            rating = "[red]📖 需要加强[/red]"

        result_text += f"[dim]评价:[/dim] {rating}\n"

        result_panel = Panel(
            result_text,
            title="[bright_red]测验成绩单[/bright_red]",
            border_style=MAIN_RED,
            padding=(1, 2),
        )
        console.print(result_panel)

        # 记录学习进度（基于答对的题目）
        for result in results:
            if result["is_correct"]:
                # 查找对应题目
                question = quiz_manager.get_question_by_id(result["question_id"])
                if question:
                    # 标记该知识点为已掌握
                    tags = question.tags.copy()
                    tags.append("测验")

                    progress_tracker.mark_topic_completed(
                        knowledge_id=question.knowledge_id,
                        topic=f"测验知识点: {question.question[:50]}...",
                        source_file=f"quiz_{question.category}",
                        study_time_seconds=int(result["time_spent_seconds"]),
                        quiz_score=100,
                        tags=tags
                    )

        # 保存进度
        progress_tracker.save()

        # 显示新解锁的成就
        unlocked_achievements = progress_tracker.get_unlocked_achievements()
        if unlocked_achievements:
            # 检查哪些是新增的（简单实现：显示最新成就）
            console.print(f"\n[{HIGHLIGHT_RED}]🎊 新成就解锁！[/{HIGHLIGHT_RED}]")
            for ach in unlocked_achievements[-2:]:  # 显示最近2个
                points = ach.get("points", 10)
                console.print(f"  [bright_red]🏆 {ach['name']}[/bright_red] ([bright_red]{points}[/bright_red]点)")
                console.print(f"    [dim]{ach['description']}[/dim]")

        console.print(f"\n[{HIGHLIGHT_RED}]按 Enter 返回学习模式...[{HIGHLIGHT_RED}]")
        Prompt.ask(f"[{HIGHLIGHT_RED}]", default="", show_default=False)

    def _check_and_display_new_achievements(self, progress_tracker, before_achievement_ids=None):
        """检查并显示新解锁的成就"""
        if before_achievement_ids is None:
            before_achievement_ids = set()

        # 获取当前已解锁成就
        current_unlocked = progress_tracker.get_unlocked_achievements()
        current_ids = {ach["achievement_id"] for ach in current_unlocked}

        # 找出新解锁的成就
        new_ids = current_ids - before_achievement_ids
        if new_ids:
            new_achievements = [ach for ach in current_unlocked if ach["achievement_id"] in new_ids]

            console.print(f"\n[{HIGHLIGHT_RED}]🎉 新成就解锁！[/{HIGHLIGHT_RED}]")
            for ach in new_achievements:
                points = ach.get("points", 10)
                badge = "🏆" if points >= 30 else "⭐" if points >= 20 else "[OK]"
                console.print(f"  [bright_red]{badge} {ach['name']}[/bright_red] ([bright_red]{points}[/bright_red]点)")
                console.print(f"    [dim]{ach['description']}[/dim]")


def start_main_menu():
    """启动主菜单入口函数"""
    menu = MainMenu()
    menu.start()


if __name__ == "__main__":
    start_main_menu()
