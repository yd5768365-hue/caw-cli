#!/usr/bin/env python3
"""
学习模块单元测试

测试 sw_helper/learning 下的模块：
- progress_tracker: 学习进度跟踪
- quiz_manager: 测验管理
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
import tempfile


class TestLearningModule:
    """学习模块导入测试"""

    def test_progress_tracker_import(self):
        """测试进度跟踪器导入"""
        from sw_helper.learning.progress_tracker import LearningProgressTracker

        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = LearningProgressTracker("test_user", data_dir=tmpdir)
            assert tracker is not None

    def test_progress_tracker_user_id(self):
        """测试用户ID"""
        from sw_helper.learning.progress_tracker import LearningProgressTracker

        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = LearningProgressTracker("my_user", data_dir=tmpdir)
            assert tracker.user_id == "my_user"

    def test_quiz_manager_import(self):
        """测试测验管理器导入"""
        from sw_helper.learning.quiz_manager import QuizManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = QuizManager(quiz_dir=tmpdir)
            assert manager is not None
            assert manager.quiz_dir == Path(tmpdir)

    def test_get_quiz_manager_function(self):
        """测试获取测验管理器函数"""
        from sw_helper.learning.quiz_manager import get_quiz_manager

        func = get_quiz_manager
        assert callable(func)

    def test_get_progress_tracker_function(self):
        """测试获取进度跟踪器函数"""
        from sw_helper.learning.progress_tracker import get_progress_tracker

        func = get_progress_tracker
        assert callable(func)


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
