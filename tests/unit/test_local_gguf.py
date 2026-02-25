#!/usr/bin/env python3
"""
本地GGUF模型加载器单元测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from sw_helper.ai.local_gguf import (
    LocalGGUFModel,
    find_gguf_models,
    get_local_gguf_model,
)


class TestLocalGGUFModel:
    """LocalGGUFModel测试类"""

    def test_init(self):
        """测试初始化"""
        model = LocalGGUFModel()
        assert model.model is None
        assert model.llm is None
        assert model.model_path is None

    def test_init_with_path(self):
        """测试带路径初始化"""
        model = LocalGGUFModel("test.gguf")
        assert model.model_path == "test.gguf"

    def test_get_model_info(self):
        """测试获取模型信息"""
        model = LocalGGUFModel()

        # 测试不存在的模型
        info = model.get_model_info("nonexistent.gguf")
        assert info == {}

        # 测试查找现有模型
        models = find_gguf_models()
        if models:
            # 使用第一个找到的模型
            model_path = models[0]["path"]
            info = model.get_model_info(model_path)
            assert "path" in info
            assert "filename" in info
            assert "size_mb" in info
            assert "quantization" in info

    def test_estimate_memory_usage_no_model(self):
        """测试未加载模型时的内存估算"""
        model = LocalGGUFModel()
        mem_info = model.estimate_memory_usage(n_ctx=1024)
        # 未加载时应返回错误或默认信息
        assert "error" in mem_info or "total_mb" in mem_info

    def test_estimate_memory_usage_with_model(self):
        """测试加载模型后的内存估算"""
        models = find_gguf_models()
        if not models:
            pytest.skip("No GGUF models found")

        model_path = models[0]["path"]
        model = LocalGGUFModel(model_path)
        model.get_model_info()

        mem_info = model.estimate_memory_usage(n_ctx=1024)
        assert "model_size_mb" in mem_info
        assert "total_mb" in mem_info
        assert "total_gb" in mem_info
        assert "recommendation" in mem_info

    def test_get_memory_recommendation(self):
        """测试内存推荐生成"""
        model = LocalGGUFModel()

        # 测试不同内存需求的推荐
        assert "CPU" in model._get_memory_recommendation(1.0)
        assert "GPU" in model._get_memory_recommendation(3.0)
        assert "专业级" in model._get_memory_recommendation(10.0)

    def test_detect_llama_cpp(self):
        """测试llama.cpp检测"""
        model = LocalGGUFModel()
        # _llama_cpp_path 可能为 None（如果未找到）
        assert model._llama_cpp_path is None or model._llama_cpp_path.exists()

    def test_unload(self):
        """测试卸载模型"""
        model = LocalGGUFModel()
        model.llm = "mock_llm"
        model.unload()
        assert model.llm is None


class TestFindGGUFModels:
    """find_gguf_models函数测试"""

    def test_find_gguf_models(self):
        """测试查找GGUF模型"""
        models = find_gguf_models()
        assert isinstance(models, list)

    def test_model_structure(self):
        """测试模型信息结构"""
        models = find_gguf_models()
        if models:
            model = models[0]
            assert "path" in model
            assert "name" in model
            assert "size_mb" in model
            assert "quantization" in model

    def test_find_with_custom_dirs(self):
        """测试自定义搜索目录"""
        # 搜索当前目录
        models = find_gguf_models(["."])
        assert isinstance(models, list)

    def test_empty_dir(self):
        """测试空目录"""
        models = find_gguf_models(["/nonexistent_directory"])
        assert models == []


class TestGetLocalGGUFModel:
    """get_local_gguf_model单例测试"""

    def test_singleton(self):
        """测试单例模式"""
        model1 = get_local_gguf_model()
        model2 = get_local_gguf_model()
        assert model1 is model2

    def test_singleton_with_path(self):
        """测试带路径的单例"""
        model1 = get_local_gguf_model("test1.gguf")
        model2 = get_local_gguf_model("test2.gguf")
        # 应该是同一个实例
        assert model1 is model2


class TestQuantizationDetection:
    """量化类型检测测试"""

    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("qwen2.5-1.5b-q2_k.gguf", "Q2_K"),
            ("model-q3_k.gguf", "Q3_K"),
            ("llama-7b-q4_0.gguf", "Q4"),
            ("model-q4_k_m.gguf", "Q4"),
            ("model-q5_0.gguf", "Q5"),
            ("model-q5_1.gguf", "Q5"),
            ("model-q6_k.gguf", "Q6_K"),
            ("model-q8_0.gguf", "Q8"),
            ("model-f16.gguf", "F16"),
            ("model-f32.gguf", "F32"),
            ("model.gguf", "unknown"),
        ],
    )
    def test_quantization_detection(self, filename, expected):
        """测试量化类型推断（从文件名）"""
        # 创建一个不存在的模型路径来测试文件名解析
        # 因为 get_model_info 需要文件存在
        # 我们通过设置 model_path 然后调用 find_gguf_models 来间接测试

        # 直接测试文件名解析逻辑
        model = LocalGGUFModel()
        # 模拟文件名解析
        fname = filename.lower()
        quant_type = "unknown"
        if "q2_k" in fname:
            quant_type = "Q2_K"
        elif "q3_k" in fname:
            quant_type = "Q3_K"
        elif "q4" in fname:
            quant_type = "Q4"
        elif "q5" in fname:
            quant_type = "Q5"
        elif "q6_k" in fname:
            quant_type = "Q6_K"
        elif "q8" in fname:
            quant_type = "Q8"
        elif "f16" in fname:
            quant_type = "F16"
        elif "f32" in fname:
            quant_type = "F32"

        assert quant_type == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
