#!/usr/bin/env python3
"""
PR 分析器 - 分析 Git 变更并提供统计报告

此模块提供 Pull Request 分析功能：
- 使用 Git 命令获取变更内容
- 解析变更文件列表并分类
- 提取代码变更统计信息
- 生成简单的文本报告

支持多种输入方式：
1. 比较两个提交或分支
2. 分析指定的 diff 文件
3. 分析当前工作区的变更

Author: CAE-CLI DevOps Team
Version: 1.0.0
"""

import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import git

    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False

from rich.box import SIMPLE
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .code_checker import CodeChecker, CodeIssue

# 导入项目错误处理器
from .error_handler import create_error_handler


class ChangeType(Enum):
    """变更类型枚举"""

    ADDED = "A"
    MODIFIED = "M"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNKNOWN = "?"


@dataclass
class FileChange:
    """文件变更信息"""

    path: str
    change_type: ChangeType
    old_path: Optional[str] = None  # 仅用于重命名/复制
    additions: int = 0
    deletions: int = 0


@dataclass
class ChangeStatistics:
    """变更统计信息"""

    total_files: int = 0
    added_files: int = 0
    modified_files: int = 0
    deleted_files: int = 0
    renamed_files: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    language_stats: Dict[str, int] = field(default_factory=dict)  # 语言类型 -> 文件数
    changed_dirs: Set[str] = field(default_factory=set)  # 变更涉及的目录


@dataclass
class CodeQualityResults:
    """代码质量检查结果"""

    total_issues: int = 0
    issues_by_category: Dict[str, int] = field(default_factory=dict)  # 分类 -> 问题数
    issues_by_severity: Dict[str, int] = field(default_factory=dict)  # 严重程度 -> 问题数
    issues_by_file: Dict[str, List[CodeIssue]] = field(default_factory=dict)  # 文件路径 -> 问题列表
    checker_stats: Dict[str, int] = field(default_factory=dict)  # 检查器 -> 发现问题数


class PRAnalyzer:
    """PR 分析器主类"""

    def __init__(self, repo_path: Optional[str] = None, debug: bool = False):
        """
        初始化 PR 分析器

        Args:
            repo_path: Git 仓库路径，默认为当前目录
            debug: 是否启用调试模式
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.debug = debug
        self.console = Console()
        self.error_handler = create_error_handler(self.console, debug=debug)
        self._repo = None

        # 验证是否为 Git 仓库
        self._validate_git_repo()

    def _validate_git_repo(self) -> None:
        """验证当前目录是否为 Git 仓库"""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise NotGitRepositoryError(f"目录 {self.repo_path} 不是 Git 仓库")

    def _run_git_command(self, args: List[str]) -> str:
        """
        运行 Git 命令并返回输出

        Args:
            args: Git 命令参数列表

        Returns:
            Git 命令输出

        Raises:
            GitCommandError: Git 命令执行失败
        """
        try:
            result = subprocess.run(
                ["git"] + args, cwd=self.repo_path, capture_output=True, text=True, encoding="utf-8", errors="replace"
            )

            if result.returncode != 0:
                error_msg = f"Git 命令失败: {' '.join(args)}\n错误: {result.stderr}"
                raise GitCommandError(error_msg)

            return result.stdout.strip()

        except subprocess.SubprocessError as e:
            raise GitCommandError(f"执行 Git 命令时出错: {e}")

    def get_changed_files(self, base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> List[FileChange]:
        """
        获取变更文件列表

        Args:
            base_ref: 基准引用 (如 main, HEAD~1)
            head_ref: 目标引用 (如 HEAD, 分支名)

        Returns:
            文件变更列表
        """
        # 使用 git diff --name-status 获取变更状态
        diff_cmd = ["diff", "--name-status", f"{base_ref}...{head_ref}"]
        output = self._run_git_command(diff_cmd)

        if not output:
            return []

        file_changes = []
        lines = output.split("\n")

        for line in lines:
            if not line.strip():
                continue

            # 解析 git diff --name-status 输出格式
            # 格式: <状态><制表符><文件路径>
            # 重命名: R<制表符><旧路径><制表符><新路径>
            parts = line.split("\t")

            if len(parts) < 2:
                continue

            status = parts[0].strip()
            path = parts[1].strip()

            # 确定变更类型
            change_type = self._parse_change_type(status)

            file_change = FileChange(path=path, change_type=change_type)

            # 处理重命名/复制
            if change_type in (ChangeType.RENAMED, ChangeType.COPIED) and len(parts) >= 3:
                file_change.old_path = parts[1].strip()
                file_change.path = parts[2].strip()

            file_changes.append(file_change)

        return file_changes

    def _parse_change_type(self, status: str) -> ChangeType:
        """解析 Git 状态字符为变更类型"""
        status_map = {
            "A": ChangeType.ADDED,
            "M": ChangeType.MODIFIED,
            "D": ChangeType.DELETED,
            "R": ChangeType.RENAMED,
            "C": ChangeType.COPIED,
        }

        # 取第一个字符（状态可能包含分数，如 'M100'）
        status_char = status[0] if status else "?"
        return status_map.get(status_char, ChangeType.UNKNOWN)

    def get_line_changes(
        self, file_change: FileChange, base_ref: str = "HEAD~1", head_ref: str = "HEAD"
    ) -> Tuple[int, int]:
        """
        获取文件行变更统计（新增/删除行数）

        Args:
            file_change: 文件变更对象
            base_ref: 基准引用
            head_ref: 目标引用

        Returns:
            (新增行数, 删除行数)
        """
        if file_change.change_type == ChangeType.DELETED:
            # 对于删除的文件，获取完整删除的行数
            diff_cmd = ["diff", "--numstat", f"{base_ref}...{head_ref}", "--", file_change.path]
        else:
            diff_cmd = ["diff", "--numstat", f"{base_ref}...{head_ref}", "--", file_change.path]

        try:
            output = self._run_git_command(diff_cmd)
            if output:
                # --numstat 输出格式: <新增行数><制表符><删除行数><制表符><文件路径>
                parts = output.split("\t")
                if len(parts) >= 2:
                    try:
                        additions = int(parts[0]) if parts[0] != "-" else 0
                        deletions = int(parts[1]) if parts[1] != "-" else 0
                        return additions, deletions
                    except ValueError:
                        pass
        except GitCommandError:
            # 如果获取行数失败，返回默认值
            pass

        return 0, 0

    def _detect_language(self, file_path: str) -> str:
        """检测文件的语言类型"""
        ext = Path(file_path).suffix.lower()

        # Python 文件
        if ext in [".py", ".pyw"]:
            return "Python"
        # 配置文件
        elif ext in [".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf"]:
            return "Config"
        # 文档文件
        elif ext in [".md", ".rst", ".txt", ".adoc", ".tex"]:
            return "Documentation"
        # 脚本文件
        elif ext in [".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd"]:
            return "Script"
        # 测试文件
        elif "/test_" in file_path or file_path.startswith("test_") or "/tests/" in file_path:
            return "Test"
        # 其他代码文件
        elif ext in [".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp", ".go", ".rs", ".rb"]:
            return "Code"
        # 数据文件
        elif ext in [".csv", ".tsv", ".xlsx", ".xls", ".jsonl", ".parquet"]:
            return "Data"
        else:
            return "Other"

    def analyze_changes(self, base_ref: str = "HEAD~1", head_ref: str = "HEAD") -> ChangeStatistics:
        """
        分析变更并生成统计信息

        Args:
            base_ref: 基准引用
            head_ref: 目标引用

        Returns:
            变更统计信息
        """
        # 获取变更文件
        file_changes = self.get_changed_files(base_ref, head_ref)

        if not file_changes:
            return ChangeStatistics(language_stats={}, changed_dirs=set())

        stats = ChangeStatistics(total_files=len(file_changes), language_stats={}, changed_dirs=set())

        # 统计变更类型和语言
        for file_change in file_changes:
            # 统计变更类型
            if file_change.change_type == ChangeType.ADDED:
                stats.added_files += 1
            elif file_change.change_type == ChangeType.MODIFIED:
                stats.modified_files += 1
            elif file_change.change_type == ChangeType.DELETED:
                stats.deleted_files += 1
            elif file_change.change_type in (ChangeType.RENAMED, ChangeType.COPIED):
                stats.renamed_files += 1

            # 获取行变更统计
            additions, deletions = self.get_line_changes(file_change, base_ref, head_ref)
            file_change.additions = additions
            file_change.deletions = deletions

            stats.total_additions += additions
            stats.total_deletions += deletions

            # 检测语言类型
            language = self._detect_language(file_change.path)
            stats.language_stats[language] = stats.language_stats.get(language, 0) + 1

            # 记录变更目录
            dir_path = str(Path(file_change.path).parent)
            if dir_path != ".":
                stats.changed_dirs.add(dir_path)

        return stats

    def check_code_quality(self, file_changes: List[FileChange]) -> CodeQualityResults:
        """
        检查变更文件的代码质量

        Args:
            file_changes: 文件变更列表

        Returns:
            代码质量检查结果
        """
        checker = CodeChecker()
        results = CodeQualityResults()

        # 只检查Python文件（新增和修改的文件）
        python_files = []
        for fc in file_changes:
            if fc.path.endswith(".py") and fc.change_type in (ChangeType.ADDED, ChangeType.MODIFIED):
                python_files.append(fc.path)

        if not python_files:
            return results

        # 运行代码检查
        issues_by_file = checker.check_files(python_files)

        # 统计结果
        results.issues_by_file = issues_by_file
        results.total_issues = sum(len(issues) for issues in issues_by_file.values())

        # 按分类统计
        for file_path, issues in issues_by_file.items():
            for issue in issues:
                # 分类统计
                results.issues_by_category[issue.category] = results.issues_by_category.get(issue.category, 0) + 1
                # 严重程度统计
                severity_str = issue.severity.value
                results.issues_by_severity[severity_str] = results.issues_by_severity.get(severity_str, 0) + 1

        # 检查器统计（简化：根据分类统计）
        checker_names = {
            "security": "SecurityChecker",
            "performance": "PerformanceChecker",
            "maintainability": "MaintainabilityChecker",
        }
        for category, count in results.issues_by_category.items():
            checker_name = checker_names.get(category, category)
            results.checker_stats[checker_name] = count

        return results

    def generate_report(
        self, stats: ChangeStatistics, file_changes: List[FileChange], code_quality: Optional[CodeQualityResults] = None
    ) -> str:
        """
        生成文本报告

        Args:
            stats: 变更统计信息
            file_changes: 文件变更列表
            code_quality: 可选，代码质量检查结果

        Returns:
            文本报告字符串
        """
        report_lines = []

        # 标题
        report_lines.append("=" * 80)
        report_lines.append("PR Change Analysis Report")
        report_lines.append("=" * 80)
        report_lines.append("")

        # 摘要统计
        report_lines.append("[Summary]")
        report_lines.append("-" * 40)
        report_lines.append(f"Changed files: {stats.total_files}")
        report_lines.append(f"  Added files: {stats.added_files}")
        report_lines.append(f"  Modified files: {stats.modified_files}")
        report_lines.append(f"  Deleted files: {stats.deleted_files}")
        report_lines.append(f"  Renamed/Copied: {stats.renamed_files}")
        report_lines.append("")
        report_lines.append(f"Line changes: +{stats.total_additions} / -{stats.total_deletions}")

        if stats.total_additions + stats.total_deletions > 0:
            net_change = stats.total_additions - stats.total_deletions
            change_symbol = "+" if net_change >= 0 else ""
            report_lines.append(f"Net change: {change_symbol}{net_change} lines")
        report_lines.append("")

        # 语言类型统计
        if stats.language_stats:
            report_lines.append("[Language Distribution]")
            report_lines.append("-" * 40)
            for lang, count in sorted(stats.language_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats.total_files) * 100
                report_lines.append(f"  {lang}: {count} files ({percentage:.1f}%)")
            report_lines.append("")

        # 变更目录
        if stats.changed_dirs:
            report_lines.append("[Changed Directories]")
            report_lines.append("-" * 40)
            for directory in sorted(stats.changed_dirs):
                report_lines.append(f"  {directory}")
            report_lines.append("")

        # 文件变更详情
        if file_changes:
            report_lines.append("[File Changes]")
            report_lines.append("-" * 40)

            for file_change in file_changes:
                change_symbol = {
                    ChangeType.ADDED: "[+]",
                    ChangeType.MODIFIED: "[~]",
                    ChangeType.DELETED: "[-]",
                    ChangeType.RENAMED: "[R]",
                    ChangeType.COPIED: "[C]",
                    ChangeType.UNKNOWN: "[?]",
                }.get(file_change.change_type, "[?]")

                line_info = ""
                if file_change.additions > 0 or file_change.deletions > 0:
                    line_info = f" (+{file_change.additions}/-{file_change.deletions})"

                report_lines.append(f"  {change_symbol} {file_change.path}{line_info}")

                # 如果是重命名/复制，显示旧路径
                if file_change.old_path:
                    report_lines.append(f"      <- {file_change.old_path}")

        report_lines.append("")

        # 代码质量检查结果
        if code_quality and code_quality.total_issues > 0:
            report_lines.append("[Code Quality Issues]")
            report_lines.append("-" * 40)
            report_lines.append(f"Total issues: {code_quality.total_issues}")

            # 按严重程度统计
            if code_quality.issues_by_severity:
                report_lines.append("By severity:")
                for severity, count in sorted(
                    code_quality.issues_by_severity.items(),
                    key=lambda x: (
                        ["critical", "high", "medium", "low"].index(x[0])
                        if x[0] in ["critical", "high", "medium", "low"]
                        else 999
                    ),
                ):
                    report_lines.append(f"  {severity}: {count}")

            # 按分类统计
            if code_quality.issues_by_category:
                report_lines.append("By category:")
                for category, count in sorted(
                    code_quality.issues_by_category.items(), key=lambda x: x[1], reverse=True
                ):
                    report_lines.append(f"  {category}: {count}")

            # 按文件详细问题
            report_lines.append("")
            report_lines.append("Detailed issues by file:")
            for file_path, issues in code_quality.issues_by_file.items():
                report_lines.append(f"  {file_path} ({len(issues)} issues):")
                for issue in issues[:5]:  # 每个文件最多显示5个问题
                    report_lines.append(f"    [{issue.severity.value.upper()}] Line {issue.line}: {issue.message}")
                if len(issues) > 5:
                    report_lines.append(f"    ... and {len(issues) - 5} more issues")

            report_lines.append("")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def analyze_from_diff_file(self, diff_file_path: str) -> Tuple[ChangeStatistics, List[FileChange]]:
        """
        从 diff 文件分析变更

        Args:
            diff_file_path: diff 文件路径

        Returns:
            (统计信息, 文件变更列表)

        Note:
            此方法为简化实现，实际分析 diff 文件需要解析 diff 格式
        """
        # TODO: 实现完整的 diff 文件解析
        raise NotImplementedError("从 diff 文件分析功能尚未实现")

    def print_rich_report(
        self, stats: ChangeStatistics, file_changes: List[FileChange], code_quality: Optional[CodeQualityResults] = None
    ) -> None:
        """使用 Rich 输出美观的报告"""
        # 创建摘要表格
        summary_table = Table(title="[Summary] PR Change Summary", box=SIMPLE, show_header=True)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", style="green")
        summary_table.add_column("Description", style="white")

        summary_table.add_row("Changed files", str(stats.total_files), "Total number of files changed")
        summary_table.add_row("Added files", str(stats.added_files), "Newly added files")
        summary_table.add_row("Modified files", str(stats.modified_files), "Modified files")
        summary_table.add_row("Deleted files", str(stats.deleted_files), "Deleted files")
        summary_table.add_row(
            "Line changes", f"+{stats.total_additions} / -{stats.total_deletions}", "Added/deleted lines"
        )

        if stats.total_additions + stats.total_deletions > 0:
            net_change = stats.total_additions - stats.total_deletions
            change_symbol = "+" if net_change >= 0 else ""
            summary_table.add_row("Net change", f"{change_symbol}{net_change}", "Net lines added")

        self.console.print(summary_table)
        self.console.print()

        # 语言分布表格
        if stats.language_stats:
            lang_table = Table(title="[语言] 语言类型分布", box=SIMPLE, show_header=True)
            lang_table.add_column("Language", style="cyan")
            lang_table.add_column("Files", style="green")
            lang_table.add_column("Percentage", style="yellow")

            for lang, count in sorted(stats.language_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats.total_files) * 100
                lang_table.add_row(lang, str(count), f"{percentage:.1f}%")

            self.console.print(lang_table)
            self.console.print()

        # 文件变更列表
        if file_changes:
            files_table = Table(title="[文件] 文件变更详情", box=SIMPLE, show_header=True)
            files_table.add_column("Status", style="cyan", width=4)
            files_table.add_column("File Path", style="white")
            files_table.add_column("Line Changes", style="green", width=12)

            for file_change in file_changes:
                # 状态符号和颜色
                status_map = {
                    ChangeType.ADDED: ("[+]", "green"),
                    ChangeType.MODIFIED: ("[~]", "yellow"),
                    ChangeType.DELETED: ("[-]", "red"),
                    ChangeType.RENAMED: ("[R]", "cyan"),
                    ChangeType.COPIED: ("[C]", "blue"),
                    ChangeType.UNKNOWN: ("[?]", "white"),
                }

                status_symbol, status_color = status_map.get(file_change.change_type, ("[?]", "white"))
                status_text = Text(status_symbol, style=status_color)

                # 文件路径
                path_text = file_change.path
                if file_change.old_path:
                    path_text = f"{file_change.path} ← {file_change.old_path}"

                # 行变更信息
                line_text = ""
                if file_change.additions > 0 or file_change.deletions > 0:
                    line_text = f"+{file_change.additions}/-{file_change.deletions}"

                files_table.add_row(status_text, path_text, line_text)

            self.console.print(files_table)

        # 代码质量检查结果
        if code_quality and code_quality.total_issues > 0:
            self.console.print()

            # 创建代码质量问题摘要表格
            issues_table = Table(title="[Code Quality] Issues Summary", box=SIMPLE, show_header=True)
            issues_table.add_column("Category", style="cyan")
            issues_table.add_column("Count", style="green")
            issues_table.add_column("Severity Distribution", style="yellow")

            # 按类别显示问题
            for category, count in sorted(code_quality.issues_by_category.items(), key=lambda x: x[1], reverse=True):
                # 获取该类别的严重程度分布
                severity_items = []
                for severity in ["critical", "high", "medium", "low"]:
                    if severity in code_quality.issues_by_severity:
                        # 估算各类别的问题数（简化）
                        severity_items.append(f"{severity[0]}:{code_quality.issues_by_severity.get(severity, 0)}")

                severity_str = ", ".join(severity_items)
                issues_table.add_row(category.capitalize(), str(count), severity_str)

            self.console.print(issues_table)

            # 显示每个文件的详细问题
            self.console.print()
            details_table = Table(title="[Code Quality] Detailed Issues", box=SIMPLE, show_header=True)
            details_table.add_column("File", style="white")
            details_table.add_column("Line", style="cyan", width=6)
            details_table.add_column("Severity", style="red", width=8)
            details_table.add_column("Issue", style="yellow")

            for file_path, issues in code_quality.issues_by_file.items():
                for issue in issues[:3]:  # 每个文件最多显示3个问题
                    severity_color = {"critical": "bold red", "high": "red", "medium": "yellow", "low": "blue"}.get(
                        issue.severity.value, "white"
                    )

                    severity_text = Text(issue.severity.value.upper(), style=severity_color)
                    details_table.add_row(
                        file_path,
                        str(issue.line),
                        severity_text,
                        issue.message[:100] + "..." if len(issue.message) > 100 else issue.message,
                    )

            self.console.print(details_table)


# 自定义异常类
class PRAnalyzerError(Exception):
    """PR 分析器基础异常"""

    pass


class NotGitRepositoryError(PRAnalyzerError):
    """非 Git 仓库异常"""

    pass


class GitCommandError(PRAnalyzerError):
    """Git 命令执行异常"""

    pass


class NoChangesError(PRAnalyzerError):
    """无变更异常"""

    pass


def main():
    """命令行入口函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="PR 分析器 - 分析 Git 变更并提供统计报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                      # 分析最近一次提交
  %(prog)s --base main --head feature-branch  # 分析分支差异
  %(prog)s --pr-number 123      # 分析 PR (需要 GitHub CLI)
  %(prog)s --diff-file changes.diff  # 分析 diff 文件

默认行为: 分析 HEAD~1 到 HEAD 的变更
        """,
    )

    parser.add_argument("--base", "-b", default="HEAD~1", help="基准引用 (分支名、提交哈希、标签等)")

    parser.add_argument("--head", "-H", default="HEAD", help="目标引用 (分支名、提交哈希、标签等)")

    parser.add_argument("--branch", "-B", help="比较当前分支与指定分支 (便捷参数，等价于 --base <branch> --head HEAD)")

    parser.add_argument("--pr-number", "-p", type=int, help="PR 编号 (需要 GitHub CLI 支持)")

    parser.add_argument("--diff-file", "-d", help="直接分析 diff 文件")

    parser.add_argument("--repo-path", "-r", help="Git 仓库路径 (默认为当前目录)")

    parser.add_argument(
        "--output",
        "-o",
        choices=["text", "rich", "json"],
        default="rich",
        help="输出格式: text(文本), rich(美化), json(JSON格式)",
    )

    parser.add_argument("--check-code", "-c", action="store_true", help="启用代码质量检查")

    parser.add_argument("--debug", "-D", action="store_true", help="启用调试模式")

    parser.add_argument("--version", "-V", action="version", version="PR 分析器 v1.0.0")

    args = parser.parse_args()

    try:
        # 创建分析器
        analyzer = PRAnalyzer(repo_path=args.repo_path, debug=args.debug)

        # 根据参数选择分析方式
        if args.diff_file:
            stats, file_changes = analyzer.analyze_from_diff_file(args.diff_file)
        elif args.pr_number:
            # 简单实现: 使用 GitHub CLI 获取 PR 差异
            # 这里简化处理，使用分支比较
            print(f"注意: PR #{args.pr_number} 分析需要 GitHub CLI，暂时使用分支比较替代")
            base_ref = args.base
            head_ref = args.head
            stats = analyzer.analyze_changes(base_ref, head_ref)
            file_changes = analyzer.get_changed_files(base_ref, head_ref)
        else:
            # 确定比较的基准和目标
            if args.branch:
                base_ref = args.branch
                head_ref = "HEAD"
            else:
                base_ref = args.base
                head_ref = args.head

            stats = analyzer.analyze_changes(base_ref, head_ref)
            file_changes = analyzer.get_changed_files(base_ref, head_ref)

        # 代码质量检查
        code_quality = None
        if args.check_code:
            code_quality = analyzer.check_code_quality(file_changes)

        # 输出结果
        if stats.total_files == 0:
            # 直接使用MBCS编码输出
            message = "[OK] No changes found\n"
            try:
                sys.stdout.buffer.write(message.encode("mbcs"))
            except UnicodeEncodeError:
                sys.stdout.buffer.write(message.encode("mbcs", errors="replace"))
            return 0

        if args.output == "text":
            report = analyzer.generate_report(stats, file_changes, code_quality)
            # 直接使用MBCS编码输出（Windows系统编码）
            try:
                sys.stdout.buffer.write(report.encode("mbcs"))
                sys.stdout.buffer.write(b"\n")
            except UnicodeEncodeError:
                # 如果MBCS编码失败，使用replace策略
                sys.stdout.buffer.write(report.encode("mbcs", errors="replace"))
                sys.stdout.buffer.write(b"\n")
        elif args.output == "rich":
            analyzer.print_rich_report(stats, file_changes, code_quality)
        elif args.output == "json":
            import json

            result = {
                "summary": {
                    "total_files": stats.total_files,
                    "added_files": stats.added_files,
                    "modified_files": stats.modified_files,
                    "deleted_files": stats.deleted_files,
                    "renamed_files": stats.renamed_files,
                    "total_additions": stats.total_additions,
                    "total_deletions": stats.total_deletions,
                },
                "languages": stats.language_stats,
                "changed_dirs": list(stats.changed_dirs) if stats.changed_dirs else [],
                "file_changes": [
                    {
                        "path": fc.path,
                        "change_type": fc.change_type.value,
                        "old_path": fc.old_path,
                        "additions": fc.additions,
                        "deletions": fc.deletions,
                    }
                    for fc in file_changes
                ],
            }

            # 添加代码质量检查结果（如果存在）
            if code_quality:
                # 转换问题为JSON可序列化格式
                issues_list = []
                for file_path, issues in code_quality.issues_by_file.items():
                    for issue in issues:
                        issues_list.append(
                            {
                                "file": issue.file,
                                "line": issue.line,
                                "category": issue.category,
                                "severity": issue.severity.value,
                                "message": issue.message,
                                "suggestion": issue.suggestion,
                                "code_snippet": issue.code_snippet,
                            }
                        )

                result["code_quality"] = {
                    "total_issues": code_quality.total_issues,
                    "issues_by_category": code_quality.issues_by_category,
                    "issues_by_severity": code_quality.issues_by_severity,
                    "checker_stats": code_quality.checker_stats,
                    "issues": issues_list,
                }
            print(json.dumps(result, indent=2, ensure_ascii=False))

        return 0

    except PRAnalyzerError as e:
        error_msg = f"[ERROR] 错误: {e}\n"
        try:
            sys.stderr.buffer.write(error_msg.encode("mbcs"))
        except UnicodeEncodeError:
            sys.stderr.buffer.write(error_msg.encode("mbcs", errors="replace"))
        return 1
    except Exception as e:
        error_msg = f"[ERROR] 未预期的错误: {e}\n"
        try:
            sys.stderr.buffer.write(error_msg.encode("mbcs"))
        except UnicodeEncodeError:
            sys.stderr.buffer.write(error_msg.encode("mbcs", errors="replace"))
        if args.debug:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
