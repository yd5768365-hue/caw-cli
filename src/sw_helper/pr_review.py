#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能代码审查工具 - CAE-CLI PR审查

功能：
1. 分析git diff获取变更
2. 检查安全、性能、可维护性三个维度
3. 输出Markdown格式报告
4. 支持--local（本地变更）和--pr NUMBER（PR编号）两种模式

Author: CAE-CLI DevOps Team
Version: 0.1.0
"""

import subprocess
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import click
from rich.console import Console
from rich.markdown import Markdown

console = Console()

# 颜色定义
MAIN_RED = "#8B0000"
HIGHLIGHT_RED = "#FF4500"


class CodeReviewer:
    """代码审查器"""

    def __init__(self):
        self.issues = []

    def run_git_diff(self, local: bool = True, pr_number: Optional[int] = None) -> List[str]:
        """
        运行git diff获取变更文件列表

        Args:
            local: 是否分析本地变更
            pr_number: PR编号（如果提供）

        Returns:
            变更文件路径列表
        """
        changed_files = []

        try:
            if local:
                # 本地未提交的变更
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
            elif pr_number:
                # PR变更（简化实现：假设有GitHub CLI）
                # 实际应该使用GitHub API获取PR变更
                result = subprocess.run(
                    ["git", "diff", "--name-only", f"origin/main...HEAD"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
            else:
                # 默认：与上游分支比较
                result = subprocess.run(
                    ["git", "diff", "--name-only", "origin/main...HEAD"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )

            if result.returncode == 0 and result.stdout.strip():
                changed_files = [
                    f.strip() for f in result.stdout.strip().split('\n')
                    if f.strip() and os.path.exists(f.strip())
                ]

        except Exception as e:
            console.print(f"[red]Failed to run git diff: {e}[/red]")

        return changed_files

    def check_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        检查单个文件的代码问题

        Args:
            file_path: 文件路径

        Returns:
            问题列表
        """
        issues = []

        # 只检查Python文件
        if not file_path.endswith('.py'):
            return issues

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # 安全检查
            issues.extend(self._check_security(file_path, lines))

            # 性能检查
            issues.extend(self._check_performance(file_path, lines))

            # 可维护性检查
            issues.extend(self._check_maintainability(file_path, lines))

        except Exception as e:
            console.print(f"[yellow]Failed to check file {file_path}: {e}[/yellow]")

        return issues

    def _check_security(self, file_path: str, lines: List[str]) -> List[Dict[str, Any]]:
        """安全检查"""
        issues = []
        security_patterns = [
            (r'password\s*=\s*[\"\'].*[\"\']', 'Hardcoded password'),
            (r'api_key\s*=\s*[\"\'].*[\"\']', 'Hardcoded API key'),
            (r'secret\s*=\s*[\"\'].*[\"\']', 'Hardcoded secret'),
            (r'eval\(', 'Dangerous eval function'),
            (r'exec\(', 'Dangerous exec function'),
            (r'os\.system\(', 'Direct system call'),
            (r'subprocess\.call\(.*shell=True', 'Dangerous shell call'),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, description in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'category': 'security',
                        'severity': 'high',
                        'description': description,
                        'code': line.strip()[:100]
                    })
                    break  # 每行只报告一个问题

        return issues

    def _check_performance(self, file_path: str, lines: List[str]) -> List[Dict[str, Any]]:
        """性能检查"""
        issues = []

        # 检查大文件读取
        for i, line in enumerate(lines, 1):
            if 'open(' in line and 'read()' in line:
                if 'with' not in line and 'close()' not in line:
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'category': 'performance',
                        'severity': 'medium',
                        'description': 'Possible unbuffered large file read',
                        'code': line.strip()[:100]
                    })

        # 检查嵌套循环（简化版）
        indent_level = 0
        loop_stack = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # 计算缩进
            leading_spaces = len(line) - len(line.lstrip())
            current_indent = leading_spaces // 4  # 假设4空格缩进

            # 检查循环开始
            if stripped.startswith(('for ', 'while ', 'async for ')):
                loop_stack.append((stripped, current_indent, i))

            # 检查循环嵌套深度
            if loop_stack:
                last_loop = loop_stack[-1]
                if current_indent > last_loop[1] + 1 and len(loop_stack) >= 2:
                    issues.append({
                        'file': file_path,
                        'line': i,
                        'category': 'performance',
                        'severity': 'medium',
                        'description': f'Nested loops, depth {len(loop_stack)}',
                        'code': line.strip()[:100]
                    })

            # 检查循环结束（通过缩进减少）
            while loop_stack and current_indent <= loop_stack[-1][1]:
                loop_stack.pop()

        return issues

    def _check_maintainability(self, file_path: str, lines: List[str]) -> List[Dict[str, Any]]:
        """可维护性检查"""
        issues = []

        # 检查TODO/FIXME注释
        for i, line in enumerate(lines, 1):
            if re.search(r'\b(TODO|FIXME|XXX|HACK|BUG)\b', line, re.IGNORECASE):
                issues.append({
                    'file': file_path,
                    'line': i,
                    'category': 'maintainability',
                    'severity': 'low',
                    'description': 'Technical debt marker',
                    'code': line.strip()[:100]
                })

        # 检查函数长度（简化版）
        in_function = False
        function_start = 0
        function_lines = 0
        current_indent = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if not stripped or stripped.startswith('#'):
                continue

            leading_spaces = len(line) - len(line.lstrip())
            line_indent = leading_spaces // 4

            # 函数开始
            if not in_function and stripped.startswith(('def ', 'async def ')):
                in_function = True
                function_start = i
                function_lines = 0
                current_indent = line_indent
            elif in_function:
                if line_indent <= current_indent and stripped and not stripped.startswith('#'):
                    # 函数结束
                    if function_lines > 50:
                        issues.append({
                            'file': file_path,
                            'line': function_start,
                            'category': 'maintainability',
                            'severity': 'medium',
                            'description': f'Function too long ({function_lines} lines)',
                            'code': lines[function_start-1].strip()[:100]
                        })
                    in_function = False
                else:
                    function_lines += 1

        return issues

    def generate_markdown_report(self, issues: List[Dict[str, Any]],
                               changed_files: List[str]) -> str:
        """
        Generate code review report in Markdown format

        Args:
            issues: List of issues
            changed_files: List of changed files

        Returns:
            Markdown report string
        """
        if not issues:
            return "# [OK] Code Review Report\n\nNo issues found!"

        # Statistics by severity
        critical_count = sum(1 for i in issues if i['severity'] == 'critical')
        high_count = sum(1 for i in issues if i['severity'] == 'high')
        medium_count = sum(1 for i in issues if i['severity'] == 'medium')
        low_count = sum(1 for i in issues if i['severity'] == 'low')

        # Statistics by category
        security_count = sum(1 for i in issues if i['category'] == 'security')
        performance_count = sum(1 for i in issues if i['category'] == 'performance')
        maintainability_count = sum(1 for i in issues if i['category'] == 'maintainability')

        report = []
        report.append("# [REVIEW] Code Review Report")
        report.append("")
        report.append("## [SUMMARY] Review Overview")
        report.append("")
        report.append(f"- **Files reviewed**: {len(changed_files)}")
        report.append(f"- **Issues found**: {len(issues)}")
        report.append(f"- **Critical issues**: {critical_count}")
        report.append(f"- **High severity**: {high_count}")
        report.append(f"- **Medium severity**: {medium_count}")
        report.append(f"- **Low severity**: {low_count}")
        report.append("")
        report.append("## [CATEGORIES] Issue Categories")
        report.append("")
        report.append(f"- **Security issues**: {security_count}")
        report.append(f"- **Performance issues**: {performance_count}")
        report.append(f"- **Maintainability issues**: {maintainability_count}")
        report.append("")

        # Security issues
        security_issues = [i for i in issues if i['category'] == 'security']
        if security_issues:
            report.append("## [SECURITY] Security Issues")
            report.append("")
            report.append("| File | Line | Severity | Description | Code Snippet |")
            report.append("|------|------|----------|-------------|--------------|")
            for issue in security_issues:
                file_name = os.path.basename(issue['file'])
                line = issue['line']
                severity = issue['severity'].upper()
                desc = issue['description']
                code = issue['code'].replace('|', '\\|')  # Escape Markdown table separator
                report.append(f"| `{file_name}` | {line} | **{severity}** | {desc} | `{code}` |")
            report.append("")

        # Performance issues
        performance_issues = [i for i in issues if i['category'] == 'performance']
        if performance_issues:
            report.append("## [PERFORMANCE] Performance Issues")
            report.append("")
            report.append("| File | Line | Severity | Description | Code Snippet |")
            report.append("|------|------|----------|-------------|--------------|")
            for issue in performance_issues:
                file_name = os.path.basename(issue['file'])
                line = issue['line']
                severity = issue['severity'].upper()
                desc = issue['description']
                code = issue['code'].replace('|', '\\|')
                report.append(f"| `{file_name}` | {line} | **{severity}** | {desc} | `{code}` |")
            report.append("")

        # Maintainability issues
        maintainability_issues = [i for i in issues if i['category'] == 'maintainability']
        if maintainability_issues:
            report.append("## [MAINTAINABILITY] Maintainability Issues")
            report.append("")
            report.append("| File | Line | Severity | Description | Code Snippet |")
            report.append("|------|------|----------|-------------|--------------|")
            for issue in maintainability_issues:
                file_name = os.path.basename(issue['file'])
                line = issue['line']
                severity = issue['severity'].upper()
                desc = issue['description']
                code = issue['code'].replace('|', '\\|')
                report.append(f"| `{file_name}` | {line} | **{severity}** | {desc} | `{code}` |")
            report.append("")

        # Recommendations
        report.append("## [RECOMMENDATIONS] Suggestions")
        report.append("")
        if security_issues:
            report.append("1. **Security recommendations**:")
            report.append("   - Remove hardcoded passwords and API keys")
            report.append("   - Use environment variables or config management")
            report.append("   - Avoid dangerous functions like eval/exec")
            report.append("")

        if performance_issues:
            report.append("2. **Performance recommendations**:")
            report.append("   - Use streaming for large files")
            report.append("   - Reduce nested loop depth")
            report.append("   - Use with statements for resource management")
            report.append("")

        if maintainability_issues:
            report.append("3. **Maintainability recommendations**:")
            report.append("   - Address TODO/FIXME markers promptly")
            report.append("   - Keep functions short (<50 lines)")
            report.append("   - Add appropriate comments and documentation")
            report.append("")

        report.append("---")
        report.append("*Generated by CAE-CLI Code Review Tool*")

        return '\n'.join(report)


def review_command(local: bool = True, pr: Optional[int] = None):
    """
    Execute code review command

    Args:
        local: Whether to review local changes
        pr: PR number
    """
    console.print(f"[{HIGHLIGHT_RED}][INFO] Starting code review...[/{HIGHLIGHT_RED}]")

    # Check if in Git repository
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.returncode != 0:
            console.print("[red]Error: Not in a Git repository[/red]")
            return
    except Exception as e:
        console.print(f"[red]Error: Unable to check Git status: {e}[/red]")
        return

    # Initialize reviewer
    reviewer = CodeReviewer()

    # Get changed files
    changed_files = reviewer.run_git_diff(local=local, pr_number=pr)

    if not changed_files:
        console.print("[yellow]No changed files found[/yellow]")
        return

    console.print(f"[green]Found {len(changed_files)} changed files[/green]")

    # 检查每个文件
    all_issues = []
    for file_path in changed_files:
        issues = reviewer.check_file(file_path)
        all_issues.extend(issues)

    # 生成报告
    report = reviewer.generate_markdown_report(all_issues, changed_files)

    # 输出报告
    console.print("\n")
    # 直接打印报告文本，避免Markdown编码问题
    console.print(report)

    # Summary
    if all_issues:
        console.print(f"\n[{MAIN_RED}][WARN] Found {len(all_issues)} issues, please fix them[/{MAIN_RED}]")
    else:
        console.print(f"\n[{HIGHLIGHT_RED}][OK] Code quality is good! No issues found[/{HIGHLIGHT_RED}]")


if __name__ == "__main__":
    # 命令行测试
    import argparse
    parser = argparse.ArgumentParser(description="代码审查工具")
    parser.add_argument("--local", action="store_true", help="审查本地变更")
    parser.add_argument("--pr", type=int, help="PR编号")

    args = parser.parse_args()
    review_command(local=args.local, pr=args.pr)