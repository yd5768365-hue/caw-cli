#!/usr/bin/env python3
"""
PR审查工具 - 基于RAG知识库的智能代码审查

此工具结合PR分析器和RAG知识库，为代码变更提供智能审查建议。
它能够：
1. 分析Git PR/Commit变更
2. 检查代码质量问题（安全、性能、可维护性）
3. 查询RAG知识库获取相关机械工程知识
4. 生成综合审查报告

Author: CAE-CLI DevOps Team
Version: 1.0.0
"""

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 导入项目模块
try:
    from .code_checker import CodeChecker, Severity
    from .pr_analyzer import PRAnalyzer
    from .rag_engine import get_rag_engine
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from sw_helper.utils.code_checker import CodeChecker, Severity
    from sw_helper.utils.pr_analyzer import PRAnalyzer
    from sw_helper.utils.rag_engine import get_rag_engine


class ReviewSeverity(Enum):
    """审查问题严重程度"""

    CRITICAL = "critical"  # 必须修复
    HIGH = "high"  # 应该修复
    MEDIUM = "medium"  # 建议修复
    LOW = "low"  # 优化建议
    INFO = "info"  # 信息提示


@dataclass
class ReviewSuggestion:
    """审查建议"""

    category: str  # 类别：security/performance/maintainability/knowledge
    severity: ReviewSeverity  # 严重程度
    file: str  # 文件路径
    line: int  # 行号（可选）
    message: str  # 问题描述
    suggestion: str  # 修复建议
    knowledge_ref: Optional[str] = None  # 相关知识库引用
    code_snippet: Optional[str] = None  # 代码片段


@dataclass
class ReviewSummary:
    """审查摘要"""

    total_files: int  # 总变更文件数
    reviewed_files: int  # 已审查文件数
    total_issues: int  # 总问题数
    critical_issues: int  # 严重问题数
    high_issues: int  # 高优先级问题数
    knowledge_queries: int  # 知识库查询次数
    knowledge_hits: int  # 知识库命中次数


class PRReviewer:
    """PR审查器主类"""

    def __init__(self, rag_engine=None):
        """
        初始化PR审查器

        Args:
            rag_engine: RAG引擎实例，如果为None则自动获取
        """
        self.pr_analyzer = PRAnalyzer()
        self.code_checker = CodeChecker()

        # RAG引擎（可选）
        if rag_engine is not None:
            self.rag_engine = rag_engine
            self.rag_available = True
        else:
            # rag_engine为None表示禁用RAG
            self.rag_engine = None
            self.rag_available = False

        # 审查结果
        self.suggestions: List[ReviewSuggestion] = []
        self.summary = ReviewSummary(0, 0, 0, 0, 0, 0, 0)

        # 知识库缓存（避免重复查询）
        self.knowledge_cache: Dict[str, List[Dict[str, Any]]] = {}

    async def review_pr(
        self, base_ref: str = "HEAD~1", head_ref: str = "HEAD", branch: Optional[str] = None
    ) -> Tuple[List[ReviewSuggestion], ReviewSummary]:
        """
        审查PR/提交

        Args:
            base_ref: 基准引用（默认：上一个提交）
            head_ref: 目标引用（默认：当前提交）
            branch: 分支名称（如果提供，则比较当前分支与该分支）

        Returns:
            (审查建议列表, 审查摘要)
        """
        print(f"[INFO] Reviewing changes: {base_ref} -> {head_ref}")

        # 1. 获取变更文件列表
        try:
            if branch:
                # 比较当前分支与指定分支
                file_changes = self.pr_analyzer.get_changed_files(branch, "HEAD")
            else:
                file_changes = self.pr_analyzer.get_changed_files(base_ref, head_ref)
        except Exception as e:
            print(f"[ERROR] Failed to analyze Git changes: {e}")
            return [], ReviewSummary(0, 0, 0, 0, 0, 0, 0)

        # 2. 统计信息
        self.summary.total_files = len(file_changes)

        # 3. 对每个变更文件进行审查
        for file_change in file_changes:
            if file_change.change_type in ["D", "R"]:  # 删除或重命名文件，跳过审查
                continue

            await self._review_file(file_change.path)
            self.summary.reviewed_files += 1

        # 4. 生成最终摘要
        self.summary.total_issues = len(self.suggestions)
        self.summary.critical_issues = sum(1 for s in self.suggestions if s.severity == ReviewSeverity.CRITICAL)
        self.summary.high_issues = sum(1 for s in self.suggestions if s.severity == ReviewSeverity.HIGH)

        print(f"[INFO] Review completed: {self.summary.reviewed_files} files, {self.summary.total_issues} issues")
        print(f"[INFO] Knowledge queries: {self.summary.knowledge_queries} (hits: {self.summary.knowledge_hits})")

        return self.suggestions, self.summary

    async def _review_file(self, file_path: str):
        """
        审查单个文件

        Args:
            file_path: 文件路径
        """
        # 1. 代码质量检查
        code_issues = self.code_checker.check_file(file_path)

        # 将代码问题转换为审查建议
        for issue in code_issues:
            # 映射严重程度
            if issue.severity == Severity.CRITICAL:
                severity = ReviewSeverity.CRITICAL
            elif issue.severity == Severity.HIGH:
                severity = ReviewSeverity.HIGH
            elif issue.severity == Severity.MEDIUM:
                severity = ReviewSeverity.MEDIUM
            else:
                severity = ReviewSeverity.LOW

            suggestion = ReviewSuggestion(
                category=issue.category,
                severity=severity,
                file=issue.file,
                line=issue.line,
                message=issue.message,
                suggestion=issue.suggestion,
                code_snippet=issue.code_snippet,
            )
            self.suggestions.append(suggestion)

        # 2. 知识库查询（仅对Python文件和重要变更）
        if file_path.endswith(".py") and self.rag_available:
            await self._query_knowledge_for_file(file_path)

    async def _query_knowledge_for_file(self, file_path: str):
        """
        为文件查询相关知识库

        Args:
            file_path: 文件路径
        """
        try:
            # 读取文件内容（仅读取前几行进行分析）
            with open(file_path, encoding="utf-8") as f:
                content = f.read(5000)  # 只读取前5000字符

            # 提取关键信息用于查询
            queries = self._extract_queries_from_code(content)

            for query in queries:
                self.summary.knowledge_queries += 1

                # 检查缓存
                if query in self.knowledge_cache:
                    results = self.knowledge_cache[query]
                    self.summary.knowledge_hits += 1
                    print(f"[RAG] Cache hit: {query[:50]}...")
                else:
                    # 查询RAG引擎
                    results = self.rag_engine.search(query, top_k=2, max_length=200)
                    self.knowledge_cache[query] = results

                # 处理查询结果
                if results:
                    # 为相关知识点生成建议
                    for result in results:
                        suggestion = ReviewSuggestion(
                            category="knowledge",
                            severity=ReviewSeverity.INFO,
                            file=file_path,
                            line=0,  # 无特定行号
                            message=f"相关知识库条目: {result['source']}",
                            suggestion=f"相关机械知识: {result['content'][:150]}...",
                            knowledge_ref=result["source"],
                        )
                        self.suggestions.append(suggestion)

        except Exception as e:
            print(f"[WARN] Failed to query knowledge base ({file_path}): {e}")

    def _extract_queries_from_code(self, code_content: str) -> List[str]:
        """
        从代码内容中提取查询关键词

        Args:
            code_content: 代码内容

        Returns:
            查询关键词列表
        """
        queries = []

        # 提取可能的机械相关关键词（简单实现）
        keywords = [
            # 材料相关
            "material",
            "steel",
            "aluminum",
            "alloy",
            "Q235",
            "Q345",
            "6061",
            "7075",
            # 力学相关
            "stress",
            "strain",
            "force",
            "load",
            "pressure",
            "tension",
            "compression",
            # 几何相关
            "geometry",
            "dimension",
            "tolerance",
            "clearance",
            "fit",
            # 紧固件
            "bolt",
            "screw",
            "nut",
            "fastener",
            "M6",
            "M8",
            "M10",
            "M12",
            # 分析类型
            "analysis",
            "simulation",
            "FEA",
            "mesh",
            "grid",
            "element",
        ]

        # 转换为小写以便匹配
        code_lower = code_content.lower()

        for keyword in keywords:
            if keyword.lower() in code_lower:
                queries.append(keyword)

        # 限制查询数量
        return queries[:5]  # 最多5个查询

    def generate_report(
        self, suggestions: List[ReviewSuggestion], summary: ReviewSummary, output_format: str = "text"
    ) -> str:
        """
        生成审查报告

        Args:
            suggestions: 审查建议列表
            summary: 审查摘要
            output_format: 输出格式 text|json

        Returns:
            报告字符串
        """
        if output_format == "json":
            return self._generate_json_report(suggestions, summary)
        else:
            return self._generate_text_report(suggestions, summary)

    def _generate_text_report(self, suggestions: List[ReviewSuggestion], summary: ReviewSummary) -> str:
        """生成文本报告"""
        report_lines = []

        # 标题
        report_lines.append("=" * 80)
        report_lines.append("PR智能审查报告")
        report_lines.append("=" * 80)

        # 摘要
        report_lines.append("\n[摘要]")
        report_lines.append("-" * 40)
        report_lines.append(f"审查文件: {summary.reviewed_files}/{summary.total_files}")
        report_lines.append(f"发现问题: {summary.total_issues}")
        report_lines.append(f"  - 严重问题: {summary.critical_issues}")
        report_lines.append(f"  - 高优先级: {summary.high_issues}")
        report_lines.append(f"知识库查询: {summary.knowledge_queries} (命中: {summary.knowledge_hits})")

        if not suggestions:
            report_lines.append("\n✅ 未发现问题！")
            return "\n".join(report_lines)

        # 按严重程度分组
        critical_suggestions = [s for s in suggestions if s.severity == ReviewSeverity.CRITICAL]
        high_suggestions = [s for s in suggestions if s.severity == ReviewSeverity.HIGH]
        medium_suggestions = [s for s in suggestions if s.severity == ReviewSeverity.MEDIUM]
        low_suggestions = [s for s in suggestions if s.severity == ReviewSeverity.LOW]
        info_suggestions = [s for s in suggestions if s.severity == ReviewSeverity.INFO]

        # 输出严重问题
        if critical_suggestions:
            report_lines.append("\n[CRITICAL ISSUES]")
            report_lines.append("-" * 40)
            for suggestion in critical_suggestions:
                report_lines.append(f"文件: {suggestion.file}:{suggestion.line}")
                report_lines.append(f"类别: {suggestion.category}")
                report_lines.append(f"问题: {suggestion.message}")
                if suggestion.code_snippet:
                    report_lines.append(f"代码: {suggestion.code_snippet}")
                report_lines.append(f"建议: {suggestion.suggestion}")
                if suggestion.knowledge_ref:
                    report_lines.append(f"参考: {suggestion.knowledge_ref}")
                report_lines.append("")

        # 输出高优先级问题
        if high_suggestions:
            report_lines.append("\n[HIGH PRIORITY ISSUES]")
            report_lines.append("-" * 40)
            for suggestion in high_suggestions:
                report_lines.append(f"文件: {suggestion.file}:{suggestion.line}")
                report_lines.append(f"类别: {suggestion.category}")
                report_lines.append(f"问题: {suggestion.message}")
                report_lines.append(f"建议: {suggestion.suggestion}")
                report_lines.append("")

        # 输出知识库建议（信息级别）
        if info_suggestions:
            report_lines.append("\n[KNOWLEDGE BASE SUGGESTIONS]")
            report_lines.append("-" * 40)
            for suggestion in info_suggestions:
                report_lines.append(f"文件: {suggestion.file}")
                report_lines.append(f"主题: {suggestion.message}")
                report_lines.append(f"内容: {suggestion.suggestion}")
                report_lines.append("")

        # Statistics
        report_lines.append("\n[STATISTICS]")
        report_lines.append("-" * 40)
        report_lines.append(f"严重问题: {len(critical_suggestions)}")
        report_lines.append(f"高优先级: {len(high_suggestions)}")
        report_lines.append(f"中优先级: {len(medium_suggestions)}")
        report_lines.append(f"低优先级: {len(low_suggestions)}")
        report_lines.append(f"知识建议: {len(info_suggestions)}")

        report_lines.append("\n" + "=" * 80)

        return "\n".join(report_lines)

    def _generate_json_report(self, suggestions: List[ReviewSuggestion], summary: ReviewSummary) -> str:
        """生成JSON报告"""
        report = {
            "summary": {
                "total_files": summary.total_files,
                "reviewed_files": summary.reviewed_files,
                "total_issues": summary.total_issues,
                "critical_issues": summary.critical_issues,
                "high_issues": summary.high_issues,
                "knowledge_queries": summary.knowledge_queries,
                "knowledge_hits": summary.knowledge_hits,
            },
            "suggestions": [
                {
                    "category": s.category,
                    "severity": s.severity.value,
                    "file": s.file,
                    "line": s.line,
                    "message": s.message,
                    "suggestion": s.suggestion,
                    "knowledge_ref": s.knowledge_ref,
                    "code_snippet": s.code_snippet,
                }
                for s in suggestions
            ],
        }

        return json.dumps(report, indent=2, ensure_ascii=False)


async def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="PR智能审查工具")
    parser.add_argument("--base", "-b", default="HEAD~1", help="基准引用（默认: HEAD~1）")
    parser.add_argument("--head", "-H", default="HEAD", help="目标引用（默认: HEAD）")
    parser.add_argument("--branch", "-B", help="比较当前分支与指定分支")
    parser.add_argument("--output", "-o", default="text", choices=["text", "json"], help="输出格式")
    parser.add_argument("--rag", action="store_true", help="启用RAG知识库查询")
    parser.add_argument("--no-rag", action="store_true", help="禁用RAG知识库查询")

    args = parser.parse_args()

    # 初始化审查器
    rag_engine = None
    if not args.no_rag:
        try:
            rag_engine = get_rag_engine()
            if not rag_engine.is_available():
                print("[WARN] RAG engine unavailable, disabling knowledge base queries")
                rag_engine = None
        except Exception as e:
            print(f"[WARN] Unable to get RAG engine: {e}")

    reviewer = PRReviewer(rag_engine=rag_engine if args.rag or not args.no_rag else None)

    # 执行审查
    suggestions, summary = await reviewer.review_pr(base_ref=args.base, head_ref=args.head, branch=args.branch)

    # 生成报告
    report = reviewer.generate_report(suggestions, summary, args.output)
    print(report)

    # 如果有严重问题，返回非零退出码
    if summary.critical_issues > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
