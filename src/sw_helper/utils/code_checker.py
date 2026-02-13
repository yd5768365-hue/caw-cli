#!/usr/bin/env python3
"""
代码质量检查器 - 多维度代码分析工具

此模块提供三个维度的代码检查：
1. SecurityChecker: 安全检查
   - 检测硬编码密码/API Key
   - 检测危险函数
   - 检测 SQL 注入风险

2. PerformanceChecker: 性能检查
   - 检测低效循环
   - 检测大文件操作
   - 检测内存泄漏风险

3. MaintainabilityChecker: 可维护性检查
   - 检测代码复杂度
   - 检测过长函数
   - 检测缺少文档字符串
   - 检测 TODO/FIXME 注释

Author: CAE-CLI DevOps Team
Version: 0.1.0
"""

import re
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import warnings


class Severity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CodeIssue:
    """代码问题"""
    category: str  # security/performance/maintainability
    severity: Severity
    file: str
    line: int
    message: str
    suggestion: str
    code_snippet: Optional[str] = None


class BaseChecker:
    """基础检查器"""

    def __init__(self):
        self.issues: List[CodeIssue] = []

    def check_file(self, file_path: str, content: str) -> List[CodeIssue]:
        """
        检查单个文件

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            代码问题列表
        """
        self.issues = []
        self._check_file(file_path, content)
        return self.issues

    def _check_file(self, file_path: str, content: str) -> None:
        """具体检查逻辑由子类实现"""
        raise NotImplementedError

    def _add_issue(self, category: str, severity: Severity, file: str,
                  line: int, message: str, suggestion: str,
                  code_snippet: Optional[str] = None) -> None:
        """添加代码问题"""
        issue = CodeIssue(
            category=category,
            severity=severity,
            file=file,
            line=line,
            message=message,
            suggestion=suggestion,
            code_snippet=code_snippet
        )
        self.issues.append(issue)

    def _get_line_content(self, content: str, line_num: int) -> Optional[str]:
        """获取指定行内容"""
        lines = content.split('\n')
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1].strip()
        return None


class SecurityChecker(BaseChecker):
    """安全检查器"""

    # 硬编码密码/密钥模式
    PASSWORD_PATTERNS = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
        r'passwd\s*=\s*["\'][^"\']+["\']',
        r'credentials\s*=\s*["\'][^"\']+["\']',
    ]

    # 危险函数
    DANGEROUS_FUNCTIONS = [
        'eval',
        'exec',
        'execfile',
        'compile',
        '__import__',
        'input',  # Python 2 的 input 是危险的
    ]

    # 危险模块/方法
    DANGEROUS_IMPORTS = [
        'os.system',
        'os.popen',
        'subprocess.call',
        'subprocess.Popen',
        'pickle.loads',
        'pickle.load',
        'marshal.loads',
        'marshal.load',
        'yaml.load',  # 如果不指定 Loader
        'json.loads',  # 如果处理不受信任的数据
    ]

    # SQL 注入模式
    SQL_INJECTION_PATTERNS = [
        r'f"[^"]*{\w+}[^"]*sql',
        r'"[^"]*%s[^"]*sql',
        r'"[^"]*%\([^)]+\)s[^"]*sql',
        r'\.format\([^)]*\)[^)]*sql',
        r'\+.*SELECT',
        r'\+.*INSERT',
        r'\+.*UPDATE',
        r'\+.*DELETE',
    ]

    def _check_file(self, file_path: str, content: str) -> None:
        """执行安全检查"""
        # 仅检查 Python 文件
        if not file_path.endswith('.py'):
            return

        lines = content.split('\n')

        # 检查硬编码密码/密钥
        for i, line in enumerate(lines, 1):
            for pattern in self.PASSWORD_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_issue(
                        category="security",
                        severity=Severity.CRITICAL,
                        file=file_path,
                        line=i,
                        message=f"发现硬编码的敏感信息: {line.strip()}",
                        suggestion="使用环境变量或安全的配置管理系统存储敏感信息",
                        code_snippet=line.strip()
                    )
                    break

        # 检查危险函数调用
        for i, line in enumerate(lines, 1):
            for func in self.DANGEROUS_FUNCTIONS:
                pattern = rf'\b{func}\('
                if re.search(pattern, line):
                    self._add_issue(
                        category="security",
                        severity=Severity.HIGH,
                        file=file_path,
                        line=i,
                        message=f"发现危险函数调用: {func}",
                        suggestion=f"避免使用 {func}，或确保输入完全受信任并经过适当清理",
                        code_snippet=line.strip()
                    )

        # 检查 SQL 注入风险
        for i, line in enumerate(lines, 1):
            for pattern in self.SQL_INJECTION_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_issue(
                        category="security",
                        severity=Severity.HIGH,
                        file=file_path,
                        line=i,
                        message="发现可能的 SQL 注入风险",
                        suggestion="使用参数化查询或 ORM 来防止 SQL 注入",
                        code_snippet=line.strip()
                    )
                    break

        # 检查危险导入（需要解析 AST）
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for dangerous_import in self.DANGEROUS_IMPORTS:
                            module = dangerous_import.split('.')[0]
                            if alias.name == module:
                                self._add_issue(
                                    category="security",
                                    severity=Severity.MEDIUM,
                                    file=file_path,
                                    line=node.lineno if hasattr(node, 'lineno') else 0,
                                    message=f"导入潜在危险模块: {module}",
                                    suggestion=f"谨慎使用 {dangerous_import}，确保输入验证和清理",
                                    code_snippet=self._get_line_content(content, node.lineno) if hasattr(node, 'lineno') else None
                                )

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for dangerous_import in self.DANGEROUS_IMPORTS:
                            dangerous_module = dangerous_import.split('.')[0]
                            dangerous_func = dangerous_import.split('.')[1] if '.' in dangerous_import else None

                            if node.module == dangerous_module or node.module.startswith(dangerous_module + '.'):
                                if dangerous_func:
                                    for alias in node.names:
                                        if alias.name == dangerous_func:
                                            self._add_issue(
                                                category="security",
                                                severity=Severity.MEDIUM,
                                                file=file_path,
                                                line=node.lineno if hasattr(node, 'lineno') else 0,
                                                message=f"导入潜在危险函数: {dangerous_import}",
                                                suggestion=f"谨慎使用 {dangerous_import}，确保输入验证和清理",
                                                code_snippet=self._get_line_content(content, node.lineno) if hasattr(node, 'lineno') else None
                                            )
                                else:
                                    self._add_issue(
                                        category="security",
                                        severity=Severity.MEDIUM,
                                        file=file_path,
                                        line=node.lineno if hasattr(node, 'lineno') else 0,
                                        message=f"导入潜在危险模块: {node.module}",
                                        suggestion=f"谨慎使用 {node.module} 模块，确保输入验证和清理",
                                        code_snippet=self._get_line_content(content, node.lineno) if hasattr(node, 'lineno') else None
                                    )
        except SyntaxError:
            # 如果文件有语法错误，跳过 AST 分析
            pass


class PerformanceChecker(BaseChecker):
    """性能检查器"""

    def _check_file(self, file_path: str, content: str) -> None:
        """执行性能检查"""
        # 仅检查 Python 文件
        if not file_path.endswith('.py'):
            return

        lines = content.split('\n')

        # 检查大文件操作（无缓冲读取）
        for i, line in enumerate(lines, 1):
            if 'open(' in line and 'read()' in line:
                if 'with' not in line and 'close()' not in line:
                    self._add_issue(
                        category="performance",
                        severity=Severity.MEDIUM,
                        file=file_path,
                        line=i,
                        message="发现可能的大文件操作，可能造成内存问题",
                        suggestion="使用流式读取（逐行读取）或分块读取大文件，使用 with 语句确保文件关闭",
                        code_snippet=line.strip()
                    )

        # 检查全局变量累积（简化检查）
        # 这里主要检查在函数内修改全局变量的情况
        try:
            tree = ast.parse(content)

            # 查找全局变量修改
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 在函数内部检查全局变量使用
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Global):
                            self._add_issue(
                                category="performance",
                                severity=Severity.LOW,
                                file=file_path,
                                line=subnode.lineno if hasattr(subnode, 'lineno') else node.lineno,
                                message="函数内使用全局变量，可能影响性能和维护性",
                                suggestion="考虑将全局变量作为参数传递，或使用类封装状态",
                                code_snippet=self._get_line_content(content, subnode.lineno) if hasattr(subnode, 'lineno') and subnode.lineno else None
                            )
        except SyntaxError:
            pass

        # 检查嵌套循环（简化版本，检查缩进层次）
        indent_level = 0
        loop_stack = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # 计算缩进
            leading_spaces = len(line) - len(line.lstrip())
            current_indent = leading_spaces // 4  # 假设 4 空格缩进

            # 检查循环开始
            if stripped.startswith(('for ', 'while ', 'async for ')):
                loop_stack.append((stripped, current_indent, i))

            # 检查循环嵌套深度
            if loop_stack:
                last_loop = loop_stack[-1]
                if current_indent > last_loop[1] + 1 and len(loop_stack) >= 2:
                    # 发现嵌套循环
                    self._add_issue(
                        category="performance",
                        severity=Severity.MEDIUM,
                        file=file_path,
                        line=i,
                        message=f"发现嵌套循环，深度 {len(loop_stack)}",
                        suggestion="考虑使用向量化操作、算法优化或提前中断循环",
                        code_snippet=line.strip()
                    )

            # 检查循环结束（通过缩进减少）
            while loop_stack and current_indent <= loop_stack[-1][1]:
                loop_stack.pop()


class MaintainabilityChecker(BaseChecker):
    """可维护性检查器"""

    def _check_file(self, file_path: str, content: str) -> None:
        """执行可维护性检查"""
        # 仅检查 Python 文件
        if not file_path.endswith('.py'):
            return

        lines = content.split('\n')

        # 检查 TODO/FIXME 注释
        for i, line in enumerate(lines, 1):
            if re.search(r'\b(TODO|FIXME|XXX|HACK|BUG)\b', line, re.IGNORECASE):
                self._add_issue(
                    category="maintainability",
                    severity=Severity.LOW,
                    file=file_path,
                    line=i,
                    message="发现技术债务标记",
                    suggestion="尽快解决标记的问题或创建对应的任务跟踪",
                    code_snippet=line.strip()
                )

        # 检查过长函数（行数 > 50）
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # 计算函数行数
                    func_lines = self._count_function_lines(node, lines)

                    if func_lines > 50:
                        self._add_issue(
                            category="maintainability",
                            severity=Severity.MEDIUM,
                            file=file_path,
                            line=node.lineno,
                            message=f"函数 '{node.name}' 过长 ({func_lines} 行)",
                            suggestion="考虑将函数拆分为更小的单一职责函数",
                            code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else None
                        )

                    # 检查缺少文档字符串
                    if not self._has_docstring(node):
                        # 跳过私有方法（以 _ 开头）和魔术方法（以 __ 开头和结尾）
                        if not node.name.startswith('_') or (node.name.startswith('__') and node.name.endswith('__')):
                            self._add_issue(
                                category="maintainability",
                                severity=Severity.LOW,
                                file=file_path,
                                line=node.lineno,
                                message=f"公共函数 '{node.name}' 缺少文档字符串",
                                suggestion="添加 Google 风格或 Numpy 风格的文档字符串",
                                code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else None
                            )

                    # 检查圈复杂度（简化版）
                    complexity = self._calculate_complexity(node)
                    if complexity > 10:
                        self._add_issue(
                            category="maintainability",
                            severity=Severity.MEDIUM,
                            file=file_path,
                            line=node.lineno,
                            message=f"函数 '{node.name}' 圈复杂度较高 ({complexity})",
                            suggestion="简化条件逻辑，考虑提取子函数或使用设计模式",
                            code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else None
                        )

        except SyntaxError:
            pass

    def _count_function_lines(self, func_node: ast.AST, lines: List[str]) -> int:
        """计算函数行数"""
        if not hasattr(func_node, 'lineno') or not hasattr(func_node, 'end_lineno'):
            return 0

        start_line = func_node.lineno
        end_line = func_node.end_lineno if hasattr(func_node, 'end_lineno') else start_line

        # 计算非空行
        code_lines = 0
        for i in range(start_line - 1, min(end_line, len(lines))):
            line = lines[i].strip()
            if line and not line.startswith('#'):
                code_lines += 1

        return code_lines

    def _has_docstring(self, func_node: ast.AST) -> bool:
        """检查函数是否有文档字符串"""
        if not func_node.body:
            return False

        first_stmt = func_node.body[0]
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
            if isinstance(first_stmt.value.value, str):
                return True

        return False

    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        计算圈复杂度（简化版）
        复杂度 = 1 + 决策点数
        决策点包括：if, for, while, except, 布尔运算符
        """
        complexity = 1  # 基础复杂度

        for subnode in ast.walk(node):
            # 决策点
            if isinstance(subnode, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1

            # 布尔运算符
            elif isinstance(subnode, ast.BoolOp):
                complexity += len(subnode.values) - 1

            # 异常处理
            elif isinstance(subnode, ast.ExceptHandler):
                complexity += 1

        return complexity


class CodeChecker:
    """代码检查器主类"""

    def __init__(self):
        self.checkers = [
            SecurityChecker(),
            PerformanceChecker(),
            MaintainabilityChecker()
        ]

    def check_file(self, file_path: str) -> List[CodeIssue]:
        """
        检查单个文件

        Args:
            file_path: 文件路径

        Returns:
            代码问题列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError):
            # 如果无法读取文件，返回空列表
            return []

        all_issues = []
        for checker in self.checkers:
            issues = checker.check_file(file_path, content)
            all_issues.extend(issues)

        return all_issues

    def check_files(self, file_paths: List[str]) -> Dict[str, List[CodeIssue]]:
        """
        检查多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            字典：文件路径 -> 问题列表
        """
        results = {}
        for file_path in file_paths:
            issues = self.check_file(file_path)
            if issues:
                results[file_path] = issues

        return results


def main():
    """命令行测试"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python code_checker.py <file1> [file2 ...]")
        sys.exit(1)

    checker = CodeChecker()
    results = checker.check_files(sys.argv[1:])

    for file_path, issues in results.items():
        print(f"\n{'='*80}")
        print(f"File: {file_path}")
        print(f"Issues: {len(issues)}")
        print(f"{'='*80}")

        for issue in issues:
            print(f"  [{issue.severity.value.upper()}] Line {issue.line}: {issue.message}")
            if issue.code_snippet:
                print(f"      Code: {issue.code_snippet}")
            print(f"      Suggestion: {issue.suggestion}")
            print()


if __name__ == "__main__":
    main()