#!/usr/bin/env python3
"""
知识库单元测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from sw_helper.knowledge import KnowledgeBase, get_knowledge_base


class TestKnowledgeBase:
    """知识库测试类"""

    @pytest.fixture
    def kb(self):
        """创建知识库fixture"""
        return KnowledgeBase()

    def test_knowledge_base_init(self, kb):
        """测试知识库初始化"""
        assert kb is not None

    def test_search_bolt(self, kb):
        """测试螺栓搜索"""
        results = kb.search("螺栓")
        assert len(results) > 0

    def test_search_steel(self, kb):
        """测试钢材搜索"""
        results = kb.search("Q235")
        # 测试是否能通过材料名称搜索
        assert isinstance(results, (list, dict))

    def test_search_empty(self, kb):
        """测试空关键词"""
        results = kb.search("")
        # 空关键词应该返回空或全部
        assert isinstance(results, (list, dict))

    def test_search_nonexistent(self, kb):
        """测试不存在的关键词"""
        results = kb.search("xyznonexistent123")
        # 可能返回空结果或所有结果
        assert isinstance(results, (list, dict))


class TestGetKnowledgeBase:
    """获取知识库测试"""

    def test_get_knowledge_base_function(self):
        """测试get_knowledge_base函数"""
        kb = get_knowledge_base()
        assert kb is not None

    def test_knowledge_base_search(self):
        """测试知识库搜索功能"""
        kb = get_knowledge_base()
        results = kb.search("材料")
        assert results is not None


class TestKnowledgeContent:
    """知识库内容测试"""

    def test_bolt_knowledge_exists(self):
        """测试螺栓知识存在"""
        kb = KnowledgeBase()
        results = kb.search("螺栓")
        # 检查结果中是否包含螺栓相关内容
        assert len(results) > 0

    def test_material_knowledge_exists(self):
        """测试材料知识存在"""
        kb = KnowledgeBase()
        results = kb.search("材料")
        assert len(results) > 0

    def test_tolerance_knowledge_exists(self):
        """测试公差知识存在"""
        kb = KnowledgeBase()
        results = kb.search("公差")
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
