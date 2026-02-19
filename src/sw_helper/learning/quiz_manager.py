#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库管理器 - 加载YAML题库、随机出题、检查答案、记录分数
"""

import yaml
import random
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class QuestionDifficulty(Enum):
    """题目难度等级"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class QuestionOption:
    """选择题选项"""
    text: str
    correct: bool

@dataclass
class Question:
    """题目"""
    id: str
    knowledge_id: str
    question: str
    explanation: str
    category: str
    difficulty: QuestionDifficulty
    tags: List[str]
    options: List[QuestionOption]

@dataclass
class QuizResult:
    """测验结果"""
    question_id: str
    knowledge_id: str
    selected_option_index: int
    correct_option_index: int
    is_correct: bool
    time_spent_seconds: float
    score: int  # 0或100


class QuizManager:
    """题库管理器"""

    def __init__(self, quiz_dir: str = "data/quiz"):
        """
        初始化题库管理器

        Args:
            quiz_dir: 题库目录，默认为"data/quiz"
        """
        self.quiz_dir = Path(quiz_dir)
        self.questions: List[Question] = []
        self.loaded = False

    def load_all_quizzes(self) -> bool:
        """加载所有题库文件"""
        if not self.quiz_dir.exists():
            print(f"警告: 题库目录不存在: {self.quiz_dir}")
            return False

        # 查找所有YAML题库文件
        quiz_files = list(self.quiz_dir.glob("*.yaml")) + list(self.quiz_dir.glob("*.yml"))
        if not quiz_files:
            print(f"警告: 题库目录中没有找到YAML文件: {self.quiz_dir}")
            return False

        all_questions = []
        for quiz_file in quiz_files:
            try:
                with open(quiz_file, 'r', encoding='utf-8') as f:
                    quiz_data = yaml.safe_load(f)

                # 验证数据格式
                if not isinstance(quiz_data, dict) or "questions" not in quiz_data:
                    print(f"警告: 题库文件格式错误: {quiz_file}")
                    continue

                # 解析题目
                for q_data in quiz_data["questions"]:
                    try:
                        question = self._parse_question(q_data)
                        all_questions.append(question)
                    except (KeyError, ValueError) as e:
                        print(f"警告: 解析题目失败 ({quiz_file}): {e}")
                        continue

                print(f"[OK] 加载题库: {quiz_file.name} ({len(quiz_data['questions'])} 题)")

            except yaml.YAMLError as e:
                print(f"警告: 解析YAML文件失败 {quiz_file}: {e}")
                continue
            except IOError as e:
                print(f"警告: 读取文件失败 {quiz_file}: {e}")
                continue

        self.questions = all_questions
        self.loaded = True
        print(f"总计加载 {len(self.questions)} 道题目")
        return True

    def _parse_question(self, q_data: Dict[str, Any]) -> Question:
        """解析题目数据"""
        # 解析难度
        difficulty_str = q_data.get("difficulty", "medium").lower()
        try:
            difficulty = QuestionDifficulty(difficulty_str)
        except ValueError:
            difficulty = QuestionDifficulty.MEDIUM

        # 解析选项
        options = []
        for opt_data in q_data.get("options", []):
            option = QuestionOption(
                text=opt_data.get("text", ""),
                correct=opt_data.get("correct", False)
            )
            options.append(option)

        # 确保至少有一个正确选项
        if not any(opt.correct for opt in options):
            raise ValueError(f"题目 {q_data.get('id', 'unknown')} 没有正确选项")

        return Question(
            id=q_data.get("id", ""),
            knowledge_id=q_data.get("knowledge_id", ""),
            question=q_data.get("question", ""),
            explanation=q_data.get("explanation", ""),
            category=q_data.get("category", ""),
            difficulty=difficulty,
            tags=q_data.get("tags", []),
            options=options
        )

    def get_random_questions(self, count: int = 5,
                           categories: Optional[List[str]] = None,
                           difficulty: Optional[QuestionDifficulty] = None) -> List[Question]:
        """
        获取随机题目

        Args:
            count: 题目数量
            categories: 限制类别（如["materials", "fasteners"]）
            difficulty: 限制难度

        Returns:
            随机题目列表
        """
        if not self.loaded:
            self.load_all_quizzes()

        if not self.questions:
            return []

        # 过滤题目
        filtered_questions = self.questions
        if categories:
            filtered_questions = [q for q in filtered_questions if q.category in categories]
        if difficulty:
            filtered_questions = [q for q in filtered_questions if q.difficulty == difficulty]

        # 确保不超过可用题目数
        actual_count = min(count, len(filtered_questions))
        if actual_count == 0:
            return []

        # 随机选择
        return random.sample(filtered_questions, actual_count)

    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """根据ID获取题目"""
        if not self.loaded:
            self.load_all_quizzes()

        for question in self.questions:
            if question.id == question_id:
                return question
        return None

    def get_questions_by_knowledge_id(self, knowledge_id: str) -> List[Question]:
        """根据知识点ID获取相关题目"""
        if not self.loaded:
            self.load_all_quizzes()

        return [q for q in self.questions if q.knowledge_id == knowledge_id]

    def check_answer(self, question: Question, selected_option_index: int) -> Tuple[bool, int, str]:
        """
        检查答案

        Args:
            question: 题目对象
            selected_option_index: 用户选择的选项索引（0-based）

        Returns:
            (是否正确, 正确选项索引, 解释)
        """
        # 验证索引范围
        if selected_option_index < 0 or selected_option_index >= len(question.options):
            raise ValueError(f"选项索引超出范围: {selected_option_index}")

        # 查找正确选项索引
        correct_option_indices = [i for i, opt in enumerate(question.options) if opt.correct]
        if not correct_option_indices:
            # 理论上不会发生，因为加载时已验证
            return False, -1, "题目配置错误：无正确选项"

        # 单选题：假设只有一个正确选项
        if len(correct_option_indices) == 1:
            correct_index = correct_option_indices[0]
            is_correct = (selected_option_index == correct_index)
            return is_correct, correct_index, question.explanation
        else:
            # 多选题：暂时不支持
            return False, correct_option_indices[0], "暂不支持多选题"

    def calculate_score(self, results: List[QuizResult]) -> Dict[str, Any]:
        """
        计算测验分数统计

        Args:
            results: 测验结果列表

        Returns:
            分数统计字典
        """
        if not results:
            return {
                "total_questions": 0,
                "correct_answers": 0,
                "score_percentage": 0,
                "average_time": 0,
                "by_category": {},
                "by_difficulty": {}
            }

        total = len(results)
        correct = sum(1 for r in results if r.is_correct)
        score_percentage = (correct / total * 100) if total > 0 else 0

        # 按类别统计
        by_category = {}
        # 按难度统计
        by_difficulty = {}

        # 平均用时
        total_time = sum(r.time_spent_seconds for r in results)
        average_time = total_time / total if total > 0 else 0

        return {
            "total_questions": total,
            "correct_answers": correct,
            "score_percentage": score_percentage,
            "average_time": average_time,
            "by_category": by_category,
            "by_difficulty": by_difficulty
        }

    def get_quiz_summary(self) -> Dict[str, Any]:
        """获取题库摘要"""
        if not self.loaded:
            self.load_all_quizzes()

        # 按类别统计
        by_category = {}
        by_difficulty = {}
        by_tag = {}

        for question in self.questions:
            # 类别统计
            category = question.category
            if category not in by_category:
                by_category[category] = 0
            by_category[category] += 1

            # 难度统计
            difficulty = question.difficulty.value
            if difficulty not in by_difficulty:
                by_difficulty[difficulty] = 0
            by_difficulty[difficulty] += 1

            # 标签统计
            for tag in question.tags:
                if tag not in by_tag:
                    by_tag[tag] = 0
                by_tag[tag] += 1

        return {
            "total_questions": len(self.questions),
            "by_category": by_category,
            "by_difficulty": by_difficulty,
            "by_tag": by_tag
        }


# 单例模式
_quiz_manager_instance = None

def get_quiz_manager() -> QuizManager:
    """获取题库管理器实例（单例模式）"""
    global _quiz_manager_instance
    if _quiz_manager_instance is None:
        _quiz_manager_instance = QuizManager()
        _quiz_manager_instance.load_all_quizzes()
    return _quiz_manager_instance


if __name__ == "__main__":
    # 测试题库管理器
    print("测试题库管理器...")

    manager = get_quiz_manager()
    summary = manager.get_quiz_summary()

    print(f"\n题库摘要:")
    print(f"  总题数: {summary['total_questions']}")

    print(f"\n按类别分布:")
    for category, count in summary['by_category'].items():
        print(f"  {category}: {count}题")

    print(f"\n按难度分布:")
    for difficulty, count in summary['by_difficulty'].items():
        print(f"  {difficulty}: {count}题")

    # 测试随机出题
    print(f"\n随机抽取3题测试:")
    random_questions = manager.get_random_questions(count=3)

    for i, question in enumerate(random_questions, 1):
        print(f"\n{i}. [{question.category}] {question.question}")
        print(f"   难度: {question.difficulty.value}")

        # 显示选项
        for j, option in enumerate(question.options, 1):
            correct_mark = "✓" if option.correct else " "
            print(f"    {j}. [{correct_mark}] {option.text}")

        # 模拟选择第一个选项并检查
        try:
            is_correct, correct_idx, explanation = manager.check_answer(question, 0)
            print(f"   选择选项1: {'正确' if is_correct else '错误'}")
            print(f"   解释: {explanation[:100]}...")
        except ValueError as e:
            print(f"   错误: {e}")

    print("\n测试完成！")