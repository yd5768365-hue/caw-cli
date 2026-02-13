#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习进度追踪器 - 用JSON文件记录用户完成知识点进度

数据结构：
{
    "user_id": "default_user",
    "progress": [
        {
            "knowledge_id": "materials#Q235",
            "topic": "Q235材料属性",
            "source_file": "materials.md",
            "completed": true,
            "completion_time": "2026-02-13T10:30:00",
            "study_time_seconds": 300,
            "quiz_score": 85,
            "tags": ["材料", "钢", "力学性能"]
        }
    ],
    "achievements": [
        {
            "achievement_id": "material_master",
            "name": "材料大师",
            "description": "掌握10种材料属性",
            "unlocked": true,
            "unlock_time": "2026-02-13T10:30:00",
            "prerequisites": ["materials#Q235", "materials#45钢"]
        }
    ],
    "statistics": {
        "total_study_time_seconds": 3600,
        "completed_topics": 15,
        "average_quiz_score": 78.5,
        "last_study_date": "2026-02-13"
    }
}
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

class LearningProgressTracker:
    """学习进度追踪器 - 管理用户学习进度"""

    def __init__(self, user_id: str = "default_user", data_dir: str = "data"):
        """
        初始化进度追踪器

        Args:
            user_id: 用户ID，默认为"default_user"
            data_dir: 数据目录，默认为"data"
        """
        self.user_id = user_id
        self.data_dir = Path(data_dir)
        self.progress_file = self.data_dir / "learning_progress.json"

        # 确保数据目录存在
        self.data_dir.mkdir(exist_ok=True)

        # 加载或初始化进度数据
        self.data = self._load_or_initialize()

    def _load_or_initialize(self) -> Dict[str, Any]:
        """加载或初始化进度数据"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 如果数据格式正确，返回
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"警告: 无法加载进度文件，将创建新文件: {e}")

        # 初始化新数据结构
        return {
            "user_id": self.user_id,
            "progress": [],
            "achievements": [],
            "statistics": {
                "total_study_time_seconds": 0,
                "completed_topics": 0,
                "average_quiz_score": 0,
                "last_study_date": None
            }
        }

    def save(self):
        """保存进度数据到文件"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"错误: 无法保存进度文件: {e}")
            return False

    def mark_topic_completed(self, knowledge_id: str, topic: str,
                           source_file: str, study_time_seconds: int = 0,
                           quiz_score: Optional[int] = None, tags: Optional[List[str]] = None):
        """
        标记知识点完成

        Args:
            knowledge_id: 知识点ID，格式如 "materials#Q235"
            topic: 主题名称，如 "Q235材料属性"
            source_file: 来源文件，如 "materials.md"
            study_time_seconds: 学习时间（秒）
            quiz_score: 测验分数（0-100）
            tags: 标签列表
        """
        # 检查是否已存在该知识点的记录
        existing_idx = -1
        for idx, record in enumerate(self.data["progress"]):
            if record.get("knowledge_id") == knowledge_id:
                existing_idx = idx
                break

        current_time = datetime.now().isoformat()

        # 创建或更新记录
        if existing_idx >= 0:
            # 更新现有记录
            record = self.data["progress"][existing_idx]
            record["completed"] = True
            record["completion_time"] = current_time
            record["study_time_seconds"] = study_time_seconds
            if quiz_score is not None:
                record["quiz_score"] = quiz_score
            if tags:
                if "tags" not in record:
                    record["tags"] = []
                record["tags"].extend([tag for tag in tags if tag not in record["tags"]])
        else:
            # 创建新记录
            record = {
                "knowledge_id": knowledge_id,
                "topic": topic,
                "source_file": source_file,
                "completed": True,
                "completion_time": current_time,
                "study_time_seconds": study_time_seconds,
                "quiz_score": quiz_score,
                "tags": tags or []
            }
            self.data["progress"].append(record)

        # 更新统计信息
        self._update_statistics()

        # 检查成就解锁
        self._check_achievements()

        return record

    def get_topic_progress(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """获取特定知识点的进度"""
        for record in self.data["progress"]:
            if record.get("knowledge_id") == knowledge_id:
                return record.copy()
        return None

    def is_topic_completed(self, knowledge_id: str) -> bool:
        """检查知识点是否已完成"""
        record = self.get_topic_progress(knowledge_id)
        return record is not None and record.get("completed", False)

    def get_all_progress(self) -> List[Dict[str, Any]]:
        """获取所有进度记录"""
        return self.data["progress"].copy()

    def get_completed_topics(self) -> List[Dict[str, Any]]:
        """获取已完成的主题列表"""
        return [record for record in self.data["progress"] if record.get("completed", False)]

    def get_progress_summary(self) -> Dict[str, Any]:
        """获取进度摘要"""
        completed = self.get_completed_topics()
        total = len(self.data["progress"])

        # 按来源文件分组
        by_source = {}
        for record in completed:
            source = record.get("source_file", "unknown")
            if source not in by_source:
                by_source[source] = 0
            by_source[source] += 1

        # 按标签分组
        by_tag = {}
        for record in completed:
            for tag in record.get("tags", []):
                if tag not in by_tag:
                    by_tag[tag] = 0
                by_tag[tag] += 1

        return {
            "total_topics": total,
            "completed_topics": len(completed),
            "completion_rate": (len(completed) / total * 100) if total > 0 else 0,
            "by_source": by_source,
            "by_tag": by_tag,
            "statistics": self.data["statistics"]
        }

    def _update_statistics(self):
        """更新统计信息"""
        completed = self.get_completed_topics()

        # 计算总学习时间
        total_study_time = sum(record.get("study_time_seconds", 0) for record in completed)

        # 计算平均测验分数
        quiz_scores = [record.get("quiz_score") for record in completed if record.get("quiz_score") is not None]
        avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0

        # 获取最近学习日期
        completion_times = [record.get("completion_time") for record in completed if record.get("completion_time")]
        last_study_date = max(completion_times) if completion_times else None

        self.data["statistics"] = {
            "total_study_time_seconds": total_study_time,
            "completed_topics": len(completed),
            "average_quiz_score": avg_quiz_score,
            "last_study_date": last_study_date
        }

    def _check_achievements(self):
        """检查成就解锁 - 扩展成就系统"""
        completed = self.get_completed_topics()
        completed_count = len(completed)

        # 统计信息
        stats = self.data["statistics"]
        total_study_time = stats.get("total_study_time_seconds", 0)
        avg_quiz_score = stats.get("average_quiz_score", 0)

        # 统计各类别完成情况
        categories_completed = {}
        for record in completed:
            source = record.get("source_file", "").lower()
            if "material" in source:
                categories_completed["材料"] = True
            if "fastener" in source:
                categories_completed["紧固件"] = True
            if "tolerance" in source:
                categories_completed["公差"] = True
            if "standard" in source:
                categories_completed["标准件"] = True

        # 预定义成就（包含成就点数）
        achievements_to_check = [
            {
                "achievement_id": "beginner",
                "name": "学习新兵",
                "description": "完成第一个知识点",
                "points": 10,
                "prerequisite_count": 1
            },
            {
                "achievement_id": "material_expert",
                "name": "材料专家",
                "description": "完成5个材料相关知识点",
                "points": 20,
                "prerequisite_tags": ["材料"],
                "prerequisite_tag_count": 5  # 需要5个含"材料"标签的知识点
            },
            {
                "achievement_id": "fastener_master",
                "name": "紧固件大师",
                "description": "完成3个紧固件相关知识点",
                "points": 20,
                "prerequisite_tags": ["紧固件", "螺栓"],
                "prerequisite_tag_count": 3  # 需要3个含相关标签的知识点
            },
            {
                "achievement_id": "tolerance_guru",
                "name": "公差专家",
                "description": "完成公差配合相关知识点",
                "points": 20,
                "prerequisite_tags": ["公差", "配合"]
            },
            {
                "achievement_id": "learning_champion",
                "name": "学习达人",
                "description": "完成10个知识点",
                "points": 30,
                "prerequisite_count": 10
            },
            {
                "achievement_id": "time_manager",
                "name": "时间管理者",
                "description": "总学习时间超过30分钟",
                "points": 25,
                "prerequisite_study_time": 1800  # 30分钟 = 1800秒
            },
            {
                "achievement_id": "quiz_master",
                "name": "测验高手",
                "description": "平均测验分数超过80分",
                "points": 30,
                "prerequisite_quiz_score": 80
            },
            {
                "achievement_id": "comprehensive_learner",
                "name": "全面学习者",
                "description": "完成至少1个材料、1个紧固件、1个公差、1个标准件知识点",
                "points": 40,
                "prerequisite_categories": ["材料", "紧固件", "公差", "标准件"]
            }
        ]

        for achievement_def in achievements_to_check:
            achievement_id = achievement_def["achievement_id"]

            # 检查是否已解锁
            already_unlocked = any(
                ach.get("achievement_id") == achievement_id and ach.get("unlocked", False)
                for ach in self.data["achievements"]
            )

            if already_unlocked:
                continue

            # 检查解锁条件
            unlocked = False

            # 1. 知识点数量条件
            if "prerequisite_count" in achievement_def:
                if completed_count >= achievement_def["prerequisite_count"]:
                    unlocked = True

            # 2. 标签条件（需要特定数量的标签）
            elif "prerequisite_tags" in achievement_def:
                required_tags = achievement_def["prerequisite_tags"]
                required_count = achievement_def.get("prerequisite_tag_count", 1)

                # 计算包含任意指定标签的知识点数量
                tag_matched_count = 0
                for record in completed:
                    record_tags = record.get("tags", [])
                    if any(tag in record_tags for tag in required_tags):
                        tag_matched_count += 1

                if tag_matched_count >= required_count:
                    unlocked = True

            # 3. 学习时间条件
            elif "prerequisite_study_time" in achievement_def:
                if total_study_time >= achievement_def["prerequisite_study_time"]:
                    unlocked = True

            # 4. 测验分数条件
            elif "prerequisite_quiz_score" in achievement_def:
                if avg_quiz_score >= achievement_def["prerequisite_quiz_score"]:
                    unlocked = True

            # 5. 多类别条件
            elif "prerequisite_categories" in achievement_def:
                required_categories = achievement_def["prerequisite_categories"]
                categories_met = all(cat in categories_completed for cat in required_categories)
                if categories_met:
                    unlocked = True

            # 如果解锁，添加到成就列表
            if unlocked:
                achievement = {
                    "achievement_id": achievement_id,
                    "name": achievement_def["name"],
                    "description": achievement_def["description"],
                    "points": achievement_def.get("points", 10),
                    "unlocked": True,
                    "unlock_time": datetime.now().isoformat(),
                    "prerequisites": achievement_def.get("prerequisites", [])
                }

                # 添加或更新成就
                existing_idx = -1
                for idx, ach in enumerate(self.data["achievements"]):
                    if ach.get("achievement_id") == achievement_id:
                        existing_idx = idx
                        break

                if existing_idx >= 0:
                    self.data["achievements"][existing_idx] = achievement
                else:
                    self.data["achievements"].append(achievement)

    def get_achievements(self) -> List[Dict[str, Any]]:
        """获取成就列表"""
        return self.data["achievements"].copy()

    def get_unlocked_achievements(self) -> List[Dict[str, Any]]:
        """获取已解锁的成就列表"""
        return [ach for ach in self.data["achievements"] if ach.get("unlocked", False)]

    def get_total_achievement_points(self) -> int:
        """获取总成就点数"""
        unlocked = self.get_unlocked_achievements()
        return sum(ach.get("points", 0) for ach in unlocked)

    def get_achievement_summary(self) -> Dict[str, Any]:
        """获取成就摘要"""
        all_achievements = self.data["achievements"]
        unlocked = self.get_unlocked_achievements()
        locked = [ach for ach in all_achievements if not ach.get("unlocked", False)]

        # 按点数分级
        points_distribution = {}
        for ach in unlocked:
            points = ach.get("points", 0)
            if points not in points_distribution:
                points_distribution[points] = 0
            points_distribution[points] += 1

        return {
            "total_achievements": len(all_achievements),
            "unlocked_count": len(unlocked),
            "locked_count": len(locked),
            "unlock_rate": (len(unlocked) / len(all_achievements) * 100) if all_achievements else 0,
            "total_points": self.get_total_achievement_points(),
            "points_distribution": points_distribution
        }

    def reset_progress(self, keep_achievements: bool = False):
        """
        重置进度

        Args:
            keep_achievements: 是否保留成就记录
        """
        self.data["progress"] = []
        if not keep_achievements:
            self.data["achievements"] = []
        self._update_statistics()
        self.save()


# 单例模式
_tracker_instance = None

def get_progress_tracker(user_id: str = "default_user") -> LearningProgressTracker:
    """获取进度追踪器实例（单例模式）"""
    global _tracker_instance
    if _tracker_instance is None or _tracker_instance.user_id != user_id:
        _tracker_instance = LearningProgressTracker(user_id=user_id)
    return _tracker_instance


if __name__ == "__main__":
    # 测试进度追踪器
    tracker = get_progress_tracker()

    # 模拟完成几个知识点
    tracker.mark_topic_completed(
        knowledge_id="materials#Q235",
        topic="Q235材料属性",
        source_file="materials.md",
        study_time_seconds=300,
        quiz_score=85,
        tags=["材料", "钢", "力学性能"]
    )

    tracker.mark_topic_completed(
        knowledge_id="materials#45钢",
        topic="45钢材料属性",
        source_file="materials.md",
        study_time_seconds=420,
        quiz_score=90,
        tags=["材料", "钢", "中碳钢"]
    )

    tracker.mark_topic_completed(
        knowledge_id="fasteners#M10",
        topic="M10螺栓规格",
        source_file="fasteners.md",
        study_time_seconds=180,
        quiz_score=78,
        tags=["紧固件", "螺栓", "规格"]
    )

    # 保存
    tracker.save()

    # 显示进度摘要
    summary = tracker.get_progress_summary()
    print("进度摘要:")
    print(f"  完成知识点: {summary['completed_topics']}/{summary['total_topics']}")
    print(f"  完成率: {summary['completion_rate']:.1f}%")
    print(f"  总学习时间: {summary['statistics']['total_study_time_seconds']}秒")

    # 显示成就
    achievements = tracker.get_unlocked_achievements()
    if achievements:
        print("\n已解锁成就:")
        for ach in achievements:
            print(f"  - {ach['name']}: {ach['description']}")
    else:
        print("\n暂无成就")