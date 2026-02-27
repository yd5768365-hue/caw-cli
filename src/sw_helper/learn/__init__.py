"""
CAE-CLI 学习模块
提供交互式学习体验，集成知识库和AI问答
自动从 knowledge/ 目录扫描课程
"""

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# 知识库基础路径
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent.parent / "knowledge"


@dataclass
class Course:
    """课程信息"""

    id: str  # 课程ID，对应文件名
    name: str  # 课程名称
    description: str  # 课程描述
    path: Path  # 课程内容路径
    keywords: List[str] = field(default_factory=list)  # 搜索关键词
    order: int = 0  # 显示顺序


class CourseManager:
    """课程管理器 - 自动扫描knowledge目录"""

    _courses_cache: Optional[List[Course]] = None

    @classmethod
    def _parse_markdown_metadata(cls, content: str) -> Dict[str, Any]:
        """解析Markdown文件的frontmatter元数据"""
        metadata = {}

        # 检查是否有 frontmatter (--- 包裹)
        if content.startswith("---"):
            # 找到第二个 ---
            end_idx = content.find("---", 3)
            if end_idx != -1:
                frontmatter = content[3:end_idx].strip()
                # 解析 key: value 格式
                for line in frontmatter.split("\n"):
                    line = line.strip()
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip().lower()] = value.strip()

        return metadata

    @classmethod
    def _extract_title_and_description(cls, content: str) -> tuple:
        """从markdown内容中提取标题和描述"""
        lines = content.split("\n")

        # 找标题 (# 开头)
        title = ""
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # 找描述（第一个非空非标题行）
        description = ""
        in_frontmatter = False
        found_title = False

        for line in lines:
            line = line.strip()

            # 跳过 frontmatter
            if line == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue

            # 跳过标题
            if line.startswith("#"):
                found_title = True
                continue

            # 第一个有效段落作为描述
            if found_title and line:
                # 去掉markdown格式符号
                description = re.sub(r"[*_`#]", "", line)
                # 截断到合适长度
                if len(description) > 100:
                    description = description[:100] + "..."
                break

        return title, description

    @classmethod
    def _scan_courses(cls) -> List[Course]:
        """扫描knowledge目录，自动发现课程"""
        courses = []

        if not KNOWLEDGE_DIR.exists():
            return courses

        # 扫描所有 .md 文件
        for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                # 解析元数据
                metadata = cls._parse_markdown_metadata(content)

                # 提取标题和描述
                title, description = cls._extract_title_and_description(content)

                # 构建课程对象
                course = Course(
                    id=md_file.stem,  # 文件名作为ID
                    name=metadata.get("title", title or md_file.stem.capitalize()),
                    description=metadata.get("description", description or "点击查看内容"),
                    path=md_file,
                    keywords=cls._extract_keywords(content),
                    order=int(metadata.get("order", 999)),
                )

                courses.append(course)

            except Exception as e:
                print(f"警告: 无法读取课程文件 {md_file}: {e}")

        # 按 order 排序
        courses.sort(key=lambda c: c.order)

        return courses

    @classmethod
    def _extract_keywords(cls, content: str) -> List[str]:
        """从内容中提取关键词"""
        keywords = []

        # 查找 frontmatter 中的 keywords
        kw_match = re.search(r"keywords?:?\s*(.+?)(?:\n---|$)", content, re.IGNORECASE)
        if kw_match:
            kw_str = kw_match.group(1)
            # 分割关键词
            keywords = [k.strip() for k in re.split(r"[,，]", kw_str) if k.strip()]

        return keywords

    @classmethod
    def refresh(cls):
        """刷新课程列表"""
        cls._courses_cache = None

    @classmethod
    def get_all_courses(cls) -> List[Course]:
        """获取所有课程"""
        if cls._courses_cache is None:
            cls._courses_cache = cls._scan_courses()
        return cls._courses_cache

    @classmethod
    def get_course(cls, course_id: str) -> Optional[Course]:
        """获取指定课程"""
        for course in cls.get_all_courses():
            if course.id.lower() == course_id.lower():
                return course
        return None

    @classmethod
    def list_courses(cls) -> List[str]:
        """列出课程ID列表"""
        return [c.id for c in cls.get_all_courses()]

    @classmethod
    def search(cls, keyword: str) -> List[Course]:
        """搜索课程"""
        results = []
        keyword_lower = keyword.lower()

        for course in cls.get_all_courses():
            # 匹配课程名称
            if keyword_lower in course.name.lower():
                results.append(course)
                continue

            # 匹配关键词
            for kw in course.keywords:
                if keyword_lower in kw.lower():
                    results.append(course)
                    break

        return results


def load_course_content(course_id: str) -> str:
    """加载课程内容"""
    course = CourseManager.get_course(course_id)

    if not course:
        return f"# 课程不存在\n\n未找到课程: {course_id}"

    if not course.path.exists():
        return f"# {course.name}\n\n课程内容文件不存在: {course.path}"

    try:
        # 去掉 frontmatter 后返回正文
        with open(course.path, encoding="utf-8") as f:
            content = f.read()

        # 如果有 frontmatter，去掉它
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx != -1:
                content = content[end_idx + 3 :].strip()

        return content

    except Exception as e:
        return f"# 错误\n\n读取课程内容失败: {e}"


def create_course_template(course_name: str, description: str = "") -> str:
    """创建新课程模板"""
    return f"""---
title: {course_name}
description: {description}
order: 99
keywords: 关键词1, 关键词2, 关键词3
---

# {course_name}

{description}

## 目录

- [章节1: 基础概念](#1-基础概念)
- [章节2: 理论推导](#2-理论推导)
- [章节3: 实例分析](#3-实例分析)

---

## 1. 基础概念

在这里添加基础概念内容...

## 2. 理论推导

在这里添加理论推导内容...

## 3. 实例分析

在这里添加实例分析...

---

*使用 `cae-cli learn {course_name.lower().replace(' ', '-')}` 开始学习*
"""


__all__ = [
    "Course",
    "CourseManager",
    "load_course_content",
    "KNOWLEDGE_DIR",
    "create_course_template",
]
