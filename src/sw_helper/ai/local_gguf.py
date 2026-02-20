#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地GGUF模型加载器
使用llama-cpp-python加载本地GGUF模型文件
"""

import os
import sys
import multiprocessing
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console

console = Console()

DEFAULT_MODEL_DIR = Path(__file__).parent.parent.parent
DEFAULT_GGUF_MODEL = "qwen2.5-1.5b-instruct-q4_k_m.gguf"


class LocalGGUFModel:
    """本地GGUF模型管理器"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path
        self.llm = None
        
    def load_model(self, model_path: Optional[str] = None, n_ctx: int = 1024, n_gpu_layers: int = 32) -> bool:
        """加载GGUF模型
        
        优化参数:
        - n_ctx: 上下文长度，越短越快（建议512-1024）
        - n_gpu_layers: GPU加速层数，0=纯CPU，建议32或更大
        - n_threads: CPU线程数
        - n_threads_batch: 批处理线程数
        """
        if model_path:
            self.model_path = model_path
            
        if not self.model_path:
            console.print("[red]未指定模型路径[/red]")
            return False
            
        model_file = Path(self.model_path)
        if not model_file.exists():
            default_path = DEFAULT_MODEL_DIR / self.model_path
            if default_path.exists():
                self.model_path = str(default_path)
            else:
                console.print(f"[red]模型文件不存在: {self.model_path}[/red]")
                return False
    
        try:
            from llama_cpp import Llama
            cpu_count = multiprocessing.cpu_count()
            n_threads = max(4, cpu_count - 2)
            
            console.print(f"[cyan]正在加载模型: {self.model_path}[/cyan]")
            console.print(f"[dim]CPU线程: {n_threads}, 上下文: {n_ctx}, GPU层数: {n_gpu_layers}[/dim]")
            
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                n_threads=n_threads,
                n_threads_batch=n_threads,
                use_mmap=True,
                use_mlock=True,
                verbose=False
            )
            console.print(f"[green]✓ 模型加载成功[/green]")
            return True
        except ImportError:
            console.print("[red]llama-cpp-python未安装，请运行: pip install llama-cpp-python[/red]")
            return False
        except Exception as e:
            console.print(f"[red]模型加载失败: {str(e)}[/red]")
            return False
    
    def chat(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """使用模型进行对话"""
        if not self.llm:
            return "模型未加载，请先加载模型"
        
        try:
            messages = []
            if history:
                for h in history:
                    messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            messages.append({"role": "user", "content": message})
            
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=256,
                stream=False
            )
            
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"生成失败: {str(e)}"
    
    def unload(self):
        """卸载模型"""
        self.llm = None
        import gc
        gc.collect()


_local_gguf_model: Optional[LocalGGUFModel] = None


def get_local_gguf_model(model_path: Optional[str] = None) -> LocalGGUFModel:
    """获取本地GGUF模型实例"""
    global _local_gguf_model
    if _local_gguf_model is None:
        _local_gguf_model = LocalGGUFModel(model_path)
    return _local_gguf_model


def find_gguf_models(search_dirs: Optional[List[str]] = None) -> List[str]:
    """查找目录中的GGUF模型文件"""
    gguf_files = []
    
    if search_dirs is None:
        search_dirs = [
            ".",
            str(DEFAULT_MODEL_DIR),
            str(Path.home() / "models"),
        ]
    
    for search_dir in search_dirs:
        dir_path = Path(search_dir)
        if dir_path.exists() and dir_path.is_dir():
            for file in dir_path.glob("*.gguf"):
                gguf_files.append(str(file))
    
    return gguf_files
