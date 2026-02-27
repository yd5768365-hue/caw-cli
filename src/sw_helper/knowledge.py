#!/usr/bin/env python3
"""
机械手册知识库管理模块
用于读取 Markdown 格式的知识库文件并提供搜索功能
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class KnowledgeBase:
    """机械手册知识库管理类"""

    def __init__(self, knowledge_dir: str = "knowledge"):
        """
        初始化知识库

        Args:
            knowledge_dir: 知识库目录，默认在项目根目录的 knowledge 文件夹
        """
        self.console = Console()
        self.knowledge_dir = Path(knowledge_dir)

        # 检查知识库目录是否存在
        if not self.knowledge_dir.exists():
            self.console.print(f"[yellow]警告: 知识库目录 '{self.knowledge_dir}' 不存在，正在创建...[/yellow]")
            self.knowledge_dir.mkdir(exist_ok=True)

        self._documents: List[Dict[str, str]] = []
        self._load_documents()

    def _load_documents(self) -> None:
        """加载知识库中的所有 Markdown 文件"""
        md_files = list(self.knowledge_dir.glob("*.md"))

        if not md_files:
            self.console.print(f"[yellow]警告: 知识库目录 '{self.knowledge_dir}' 中没有找到 Markdown 文件[/yellow]")
            self._create_default_knowledge()
            md_files = list(self.knowledge_dir.glob("*.md"))

        self._documents = []
        for md_file in md_files:
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                self._documents.append(
                    {
                        "filename": md_file.name,
                        "title": self._extract_title(content) or md_file.name.replace(".md", ""),
                        "content": content,
                    }
                )

            except Exception as e:
                self.console.print(f"[red]错误: 无法读取文件 '{md_file}': {e}[/red]")

    def _extract_title(self, content: str) -> Optional[str]:
        """从 Markdown 内容中提取标题"""
        # 查找 # 标题
        match = re.search(r"^#\s+([^\n]+)", content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        return None

    def _create_default_knowledge(self) -> None:
        """创建默认的知识库文件（如果目录为空）"""
        default_files = [
            {
                "filename": "materials.md",
                "content": """# 常用材料

## 钢

| 牌号 | 屈服强度 (MPa) | 抗拉强度 (MPa) | 伸长率 (%) | 用途 |
|------|----------------|----------------|------------|------|
| Q235 | 235 | 370-500 | 26 | 普通结构钢，用于建筑、桥梁等 |
| 45钢 | 355 | 600 | 16 | 中碳结构钢，用于轴、齿轮等 |
| Q345 | 345 | 470-630 | 22 | 低合金高强度钢，用于压力容器、船舶等 |
| 304 | 205 | 520 | 40 | 不锈钢，用于化工设备、食品工业等 |
| 20CrMnTi | 835 | 1080 | 10 | 合金渗碳钢，用于齿轮、轴类等 |

## 铝合金

| 牌号 | 屈服强度 (MPa) | 抗拉强度 (MPa) | 伸长率 (%) | 用途 |
|------|----------------|----------------|------------|------|
| 6061 | 55 | 180 | 10 | 通用铝合金，用于航空、汽车、建筑等 |
| 7075 | 505 | 570 | 11 | 高强度铝合金，用于航空航天领域 |

## 铜合金

| 牌号 | 屈服强度 (MPa) | 抗拉强度 (MPa) | 伸长率 (%) | 用途 |
|------|----------------|----------------|------------|------|
| H62 | 110 | 330 | 40 | 普通黄铜，用于制造小五金、仪表等 |
| QSn4-3 | 200 | 400 | 40 | 锡青铜，用于制造轴承、轴套等 |
""",
            },
            {
                "filename": "fasteners.md",
                "content": """# 紧固件

## 螺栓规格

| 公称直径 (mm) | 螺距 (mm) | 头高 (mm) | 头宽 (mm) |
|---------------|-----------|-----------|-----------|
| M6 | 1.0 | 3.5 | 10.0 |
| M8 | 1.25 | 4.0 | 13.0 |
| M10 | 1.5 | 4.8 | 16.0 |
| M12 | 1.75 | 5.5 | 18.0 |
| M16 | 2.0 | 6.8 | 24.0 |
| M20 | 2.5 | 8.0 | 30.0 |

## 螺栓强度等级

| 等级 | 最小抗拉强度 (MPa) | 最小屈服强度 (MPa) | 用途 |
|------|---------------------|---------------------|------|
| 4.8 | 400 | 320 | 普通螺栓，用于不重要的连接 |
| 8.8 | 800 | 640 | 高强度螺栓，用于重要的连接 |
| 10.9 | 1000 | 900 | 高强度螺栓，用于重载连接 |
| 12.9 | 1200 | 1080 | 超高强度螺栓，用于极重要的连接 |
""",
            },
            {
                "filename": "tolerances.md",
                "content": """# 公差配合

## 常用公差等级

| 等级 | 应用范围 | 示例 |
|------|----------|------|
| IT1-IT4 | 高精度量仪、精密机械等 | 量块、千分尺等 |
| IT5-IT6 | 高精度配合 | 机床主轴与轴承等 |
| IT7-IT8 | 中等精度配合 | 齿轮、联轴器等 |
| IT9-IT10 | 低精度配合 | 支架、外壳等 |
| IT11-IT13 | 粗糙配合 | 农业机械、建筑机械等 |

## 配合类型

| 配合类型 | 特点 | 应用 |
|----------|------|------|
| 间隙配合 | 孔的尺寸大于轴的尺寸，有间隙 | 滑动轴承、齿轮啮合等 |
| 过盈配合 | 孔的尺寸小于轴的尺寸，有过盈 | 轴与轮毂的连接等 |
| 过渡配合 | 可能有间隙或过盈，配合较紧 | 定位配合、定心配合等 |
""",
            },
        ]

        for file_info in default_files:
            file_path = self.knowledge_dir / file_info["filename"]
            if not file_path.exists():
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(file_info["content"])
                    self.console.print(f"[green]已创建默认知识库文件: {file_path}[/green]")
                except Exception as e:
                    self.console.print(f"[red]错误: 无法创建文件 '{file_path}': {e}[/red]")

    def search(self, keyword: str) -> List[Dict[str, str]]:
        """
        搜索知识库

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的文档列表，包含 filename、title 和 content 字段
        """
        if not keyword:
            return []

        keyword = keyword.strip().lower()
        matches = []

        for doc in self._documents:
            # 在标题和内容中搜索关键词
            if keyword in doc["title"].lower() or keyword in doc["content"].lower():
                matches.append(doc.copy())

        return matches

    def search_material(self, material_name: str) -> List[Dict[str, str]]:
        """
        搜索材料信息

        Args:
            material_name: 材料名称或牌号

        Returns:
            匹配的文档列表
        """
        return self.search(f"材料 {material_name}") + self.search(material_name)

    def search_bolt(self, bolt_spec: str) -> List[Dict[str, str]]:
        """
        搜索螺栓规格

        Args:
            bolt_spec: 螺栓规格（如 M6、M8 等）

        Returns:
            匹配的文档列表
        """
        return self.search(f"螺栓 {bolt_spec}") + self.search(bolt_spec)

    def get_all_titles(self) -> List[str]:
        """获取所有知识库文档的标题"""
        return [doc["title"] for doc in self._documents]

    def highlight_keyword(self, text: str, keyword: str) -> Text:
        """
        高亮文本中的关键词

        Args:
            text: 原始文本
            keyword: 关键词

        Returns:
            高亮后的文本对象
        """
        result = Text()
        keyword = keyword.lower()
        idx = 0

        while idx < len(text):
            found_idx = text.lower().find(keyword, idx)
            if found_idx == -1:
                result.append(text[idx:])
                break

            result.append(text[idx:found_idx])
            result.append(text[found_idx : found_idx + len(keyword)], style="yellow")
            idx = found_idx + len(keyword)

        return result

    def format_search_results(self, results: List[Dict[str, str]], keyword: str) -> List[Panel]:
        """
        格式化搜索结果

        Args:
            results: 搜索结果列表
            keyword: 搜索关键词

        Returns:
            格式化后的 Rich 面板列表
        """
        panels = []

        for i, result in enumerate(results):
            # 提取匹配的内容片段
            content = result["content"]

            # 高亮关键词
            highlighted_content = self.highlight_keyword(content, keyword)

            panel = Panel(
                highlighted_content,
                title=f"[green]{result['title']}[/green]",
                subtitle=f"[dim]{result['filename']}[/dim]",
                border_style="cyan",
                expand=False,
            )

            panels.append(panel)

        return panels

    def search_and_display(self, keyword: str) -> None:
        """
        搜索并显示结果

        Args:
            keyword: 搜索关键词
        """
        if not keyword.strip():
            self.console.print("[yellow]请输入搜索关键词[/yellow]")
            return

        results = self.search(keyword)

        if not results:
            self.console.print(f"[red]未找到包含 '{keyword}' 的内容[/red]")
            self._suggest_keywords()
            return

        self.console.print(f"[green]找到 {len(results)} 个匹配结果:[/green]")

        # 显示格式化的搜索结果
        for panel in self.format_search_results(results, keyword):
            self.console.print(panel)
            self.console.print()

    def _suggest_keywords(self) -> None:
        """提供搜索建议"""
        suggestions = [
            "Q235",
            "45钢",
            "Q345",
            "304不锈钢",
            "6061铝合金",
            "M6",
            "M8",
            "M10",
            "螺栓规格",
            "螺栓强度",
            "公差等级",
            "间隙配合",
            "过盈配合",
        ]

        self.console.print("[dim]建议搜索:[/dim]")
        for i, suggestion in enumerate(suggestions, 1):
            self.console.print(f"  {i}. [cyan]{suggestion}[/cyan]")

    def get_knowledge_text(self, topic: str) -> str:
        """
        获取指定主题的知识文本，用于 AI prompt 注入

        Args:
            topic: 主题名称

        Returns:
            知识文本（Markdown 格式）
        """
        results = self.search(topic)
        if not results:
            return f"未找到关于 '{topic}' 的详细知识"

        # 合并所有匹配的内容
        knowledge_text = ""
        for result in results:
            knowledge_text += f"# {result['title']}\n\n"
            knowledge_text += result["content"] + "\n\n"

        return knowledge_text


# 单例模式
_kb_instance = None


def get_knowledge_base() -> KnowledgeBase:
    """获取知识库实例（单例模式）"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance


if __name__ == "__main__":
    # 测试知识库功能
    kb = get_knowledge_base()

    print("知识库文档标题:")
    for title in kb.get_all_titles():
        print(f"  - {title}")

    print("\n搜索 'Q235' 的结果:")
    q235_results = kb.search("Q235")
    for result in q235_results:
        print(f"\n{result['title']}:")
        print(result["content"][:200] + "...")
