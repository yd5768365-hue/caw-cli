#!/usr/bin/env python3
"""
AI模块单元测试

测试 sw_helper/ai 下的模块：
- model_generator: 模型生成器
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestAIModelGenerator:
    """模型生成器测试"""

    def test_generator_import(self):
        """测试生成器导入"""
        from sw_helper.ai.model_generator import AIModelGenerator

        gen = AIModelGenerator(use_mock=True)
        assert gen is not None
        assert gen.use_mock is True

    def test_generator_with_real_mode(self):
        """测试真实模式"""
        from sw_helper.ai.model_generator import AIModelGenerator

        gen = AIModelGenerator(use_mock=False)
        assert gen is not None

    def test_generate_with_mock(self):
        """测试模拟生成"""
        from sw_helper.ai.model_generator import AIModelGenerator

        gen = AIModelGenerator(use_mock=True)
        result = gen.generate("创建立方体", output_dir="/tmp")
        assert isinstance(result, dict)
        assert "success" in result


class TestPromptManager:
    """提示词管理器测试"""

    def test_prompt_manager_import(self):
        """测试提示词管理器导入"""
        from sw_helper.ai.prompt_manager import PromptManager

        pm = PromptManager()
        assert pm is not None


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
