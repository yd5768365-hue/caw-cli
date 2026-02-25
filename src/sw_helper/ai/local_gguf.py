#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地GGUF模型加载器
支持 llama-cpp-python 和 llama.cpp 直接调用两种方式
"""

import os
import sys
import subprocess
import multiprocessing
import json
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Generator

# 设置UTF-8输出以避免Windows编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

DEFAULT_MODEL_DIR = Path(__file__).parent.parent.parent
DEFAULT_GGUF_MODEL = "qwen2.5-1.5b-instruct-q4_k_m.gguf"


class LocalGGUFModel:
    """本地GGUF模型管理器

    支持两种后端:
    - llama-cpp-python: Python绑定，更易用
    - llama.cpp: C++可执行文件，性能更好，支持更多量化类型
    """

    def __init__(self, model_path: Optional[str] = None, use_llama_cpp: bool = True):
        self.model = None
        self.model_path = model_path
        self.llm = None
        self.use_llama_cpp = use_llama_cpp
        self._llama_cpp_path: Optional[Path] = None  # llama.cpp 可执行文件路径
        self._model_info: Dict[str, Any] = {}
        self._detect_llama_cpp()

    def _detect_llama_cpp(self):
        """检测系统中的 llama.cpp 可执行文件"""
        possible_paths = []

        # Windows
        if sys.platform == "win32":
            possible_paths = [
                Path("llama-cli.exe"),
                Path("llama-chat.exe"),
                Path("build/bin/Release/llama-cli.exe"),
                Path.home() / "llama.cpp" / "build" / "bin" / "Release" / "llama-cli.exe",
            ]
        # Linux/Mac
        else:
            possible_paths = [
                Path("llama-cli"),
                Path("llama"),
                Path.home() / "llama.cpp" / "build" / "bin" / "llama-cli",
            ]

        for path in possible_paths:
            if path.exists():
                self._llama_cpp_path = path
                console.print(f"[dim]检测到 llama.cpp: {path}[/dim]")
                return

    def get_model_info(self, model_path: Optional[str] = None) -> Dict[str, Any]:
        """获取模型信息（量化类型、大小等）"""
        if model_path:
            self.model_path = model_path

        if not self.model_path:
            return {}

        model_file = Path(self.model_path)
        if not model_file.exists():
            return {}

        # 获取文件大小
        file_size = model_file.stat().st_size
        size_mb = file_size / (1024 * 1024)
        size_gb = size_mb / 1024

        # 从文件名推断量化类型
        filename = model_file.name.lower()
        quant_type = "unknown"
        if "q2_k" in filename:
            quant_type = "Q2_K"
        elif "q3_k" in filename:
            quant_type = "Q3_K"
        elif "q4_0" in filename:
            quant_type = "Q4_0"
        elif "q4_1" in filename:
            quant_type = "Q4_1"
        elif "q4_k" in filename:
            quant_type = "Q4_K_M"
        elif "q5_0" in filename:
            quant_type = "Q5_0"
        elif "q5_1" in filename:
            quant_type = "Q5_1"
        elif "q5_k" in filename:
            quant_type = "Q5_K_M"
        elif "q6_k" in filename:
            quant_type = "Q6_K"
        elif "q8_0" in filename:
            quant_type = "Q8_0"
        elif "f16" in filename:
            quant_type = "F16"
        elif "f32" in filename:
            quant_type = "F32"

        self._model_info = {
            "path": str(model_file),
            "filename": model_file.name,
            "size_bytes": file_size,
            "size_mb": round(size_mb, 2),
            "size_gb": round(size_gb, 2),
            "quantization": quant_type,
        }

        return self._model_info

    def load_model(
        self,
        model_path: Optional[str] = None,
        n_ctx: int = 1024,
        n_gpu_layers: int = 32,
        backend: Optional[str] = None,
    ) -> bool:
        """加载GGUF模型

        Args:
            model_path: 模型文件路径
            n_ctx: 上下文长度，越短越快（建议512-2048）
            n_gpu_layers: GPU加速层数，0=纯CPU，建议32或更大
            backend: 后端选择 "llama-cpp" 或 "llama-cpp-direct"

        Returns:
            bool: 加载是否成功
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

        # 获取模型信息
        self.get_model_info()

        # 优先使用 llama-cpp-python
        if backend is None:
            backend = "llama-cpp"

        # 尝试 llama-cpp-python
        if backend == "llama-cpp":
            if self._load_with_llama_cpp_python(n_ctx, n_gpu_layers):
                return True
            console.print("[yellow]llama-cpp-python 加载失败，尝试 llama.cpp 直接调用[/yellow]")

        # 回退到 llama.cpp 直接调用
        if self._llama_cpp_path:
            return True

        console.print("[red]无法加载模型，请安装 llama-cpp-python 或下载 llama.cpp[/red]")
        return False

    def _load_with_llama_cpp_python(self, n_ctx: int, n_gpu_layers: int) -> bool:
        """使用 llama-cpp-python 加载模型"""
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
                verbose=False,
            )
            console.print(f"[green]✓ 模型加载成功 (llama-cpp-python)[/green]")
            return True
        except ImportError:
            console.print("[yellow]llama-cpp-python 未安装[/yellow]")
            return False
        except Exception as e:
            console.print(f"[red]模型加载失败: {str(e)}[/red]")
            return False

    def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
        stream: bool = False,
    ) -> str:
        """使用模型进行对话

        Args:
            message: 用户消息
            history: 对话历史
            temperature: 温度参数（0-2），越低越确定性
            max_tokens: 最大生成token数
            stream: 是否流式输出

        Returns:
            str: 模型回复
        """
        # 使用 llama.cpp 直接调用
        if self._llama_cpp_path and not self.llm:
            return self._chat_with_llama_cpp(message, history, temperature, max_tokens)

        # 使用 llama-cpp-python
        if not self.llm:
            return "模型未加载，请先加载模型"

        try:
            messages = []
            if history:
                for h in history:
                    messages.append(
                        {"role": h.get("role", "user"), "content": h.get("content", "")}
                    )
            messages.append({"role": "user", "content": message})

            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )

            if stream:
                # 流式输出
                result = []
                for chunk in response:
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            result.append(delta["content"])
                return "".join(result)

            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"生成失败: {str(e)}"

    def _chat_with_llama_cpp(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> str:
        """使用 llama.cpp 直接调用进行对话"""
        if not self._llama_cpp_path:
            return "llama.cpp 未找到"

        # 构建 prompt
        prompt = self._build_prompt(message, history)

        try:
            cmd = [
                str(self._llama_cpp_path),
                "-m", str(self.model_path),
                "-p", prompt,
                "--temp", str(temperature),
                "-n", str(max_tokens),
                "--no-mmap",
            ]

            # Windows 下可能需要设置编码
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode != 0:
                return f"llama.cpp 执行失败: {result.stderr}"

            return result.stdout.strip()

        except Exception as e:
            return f"生成失败: {str(e)}"

    def _build_prompt(
        self, message: str, history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """构建 llama.cpp 格式的 prompt"""
        from llama_cpp import Llama

        # 使用 llama.cpp 内置的 prompt template
        if self.llm:
            return message

        # 手动构建 prompt（用于 llama.cpp 直接调用）
        prompt_parts = []
        if history:
            for h in history:
                role = h.get("role", "user")
                content = h.get("content", "")
                if role == "user":
                    prompt_parts.append(f"User: {content}")
                else:
                    prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append(f"User: {message}")
        prompt_parts.append("Assistant:")

        return "\n".join(prompt_parts)

    def chat_stream(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ) -> Generator[str, None, None]:
        """流式对话生成

        Yields:
            str: 生成的文本片段
        """
        # 使用 llama-cpp-python 流式输出
        if self.llm:
            try:
                messages = []
                if history:
                    for h in history:
                        messages.append(
                            {
                                "role": h.get("role", "user"),
                                "content": h.get("content", ""),
                            }
                        )
                messages.append({"role": "user", "content": message})

                response = self.llm.create_chat_completion(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )

                for chunk in response:
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]

            except Exception as e:
                yield f"生成失败: {str(e)}"

        # 使用 llama.cpp 直接调用（无流式支持，返回空生成器）
        elif self._llama_cpp_path:
            result = self._chat_with_llama_cpp(message, history, temperature, max_tokens)
            yield result

        else:
            yield "模型未加载，请先加载模型"

    def estimate_memory_usage(self, n_ctx: int = 1024) -> Dict[str, float]:
        """估算模型内存占用

        Args:
            n_ctx: 上下文长度

        Returns:
            Dict: 内存估算信息（MB）
        """
        if not self._model_info:
            self.get_model_info()

        if not self._model_info:
            return {"error": "模型未加载"}

        # 估算公式（近似值）
        # 实际内存 ≈ 模型大小 + KV缓存 + 中间层缓存
        model_size_mb = self._model_info.get("size_mb", 0)
        kv_cache = n_ctx * 4 / 1024  # 约 4KB per token
        overhead = model_size_mb * 0.2  # 20% 开销

        total_mb = model_size_mb + kv_cache + overhead
        total_gb = total_mb / 1024

        return {
            "model_size_mb": model_size_mb,
            "kv_cache_mb": round(kv_cache, 2),
            "overhead_mb": round(overhead, 2),
            "total_mb": round(total_mb, 2),
            "total_gb": round(total_gb, 2),
            "recommendation": self._get_memory_recommendation(total_gb),
        }

    def _get_memory_recommendation(self, required_gb: float) -> str:
        """根据内存需求给出推荐"""
        if required_gb < 2:
            return "适合CPU运行，推荐 n_gpu_layers=0"
        elif required_gb < 4:
            return "建议使用GPU加速，推荐 n_gpu_layers=32"
        elif required_gb < 8:
            return "需要较大GPU显存，推荐 n_gpu_layers=99"
        else:
            return "需要专业级GPU，建议使用量化模型"

    def unload(self):
        """卸载模型"""
        self.llm = None
        import gc

        gc.collect()


_local_gguf_model: Optional[LocalGGUFModel] = None


def get_local_gguf_model(model_path: Optional[str] = None) -> LocalGGUFModel:
    """获取本地GGUF模型实例（单例模式）"""
    global _local_gguf_model
    if _local_gguf_model is None:
        _local_gguf_model = LocalGGUFModel(model_path)
    return _local_gguf_model


def find_gguf_models(search_dirs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """查找目录中的GGUF模型文件

    Returns:
        List[Dict]: 模型文件信息列表，包含路径、大小、量化类型等
    """
    model_files = []

    if search_dirs is None:
        search_dirs = [
            ".",
            str(DEFAULT_MODEL_DIR),
            str(Path.home() / "models"),
            str(Path.home() / "Downloads"),
        ]

    for search_dir in search_dirs:
        dir_path = Path(search_dir)
        if dir_path.exists() and dir_path.is_dir():
            for file in dir_path.glob("*.gguf"):
                # 获取文件信息
                size = file.stat().st_size
                size_mb = size / (1024 * 1024)

                # 解析量化类型
                filename = file.name.lower()
                quant = "unknown"
                if "q2_k" in filename:
                    quant = "Q2_K"
                elif "q3_k" in filename:
                    quant = "Q3_K"
                elif "q4" in filename:
                    quant = "Q4"
                elif "q5" in filename:
                    quant = "Q5"
                elif "q6_k" in filename:
                    quant = "Q6_K"
                elif "q8" in filename:
                    quant = "Q8"
                elif "f16" in filename:
                    quant = "F16"
                elif "f32" in filename:
                    quant = "F32"

                model_files.append(
                    {
                        "path": str(file),
                        "name": file.name,
                        "size_mb": round(size_mb, 2),
                        "quantization": quant,
                    }
                )

    return sorted(model_files, key=lambda x: x["size_mb"])


def print_model_list(search_dirs: Optional[List[str]] = None):
    """打印可用的GGUF模型列表"""
    models = find_gguf_models(search_dirs)

    if not models:
        console.print("[yellow]未找到GGUF模型文件[/yellow]")
        console.print("[dim]请将模型文件放置在以下目录:[/dim]")
        console.print(f"  - {DEFAULT_MODEL_DIR}")
        console.print(f"  - {Path.home() / 'models'}")
        return

    console.print(f"\n[cyan]找到 {len(models)} 个GGUF模型:[/cyan]\n")

    from rich.table import Table

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("名称", style="cyan")
    table.add_column("大小", justify="right")
    table.add_column("量化", justify="center")
    table.add_column("路径")

    for model in models:
        table.add_row(
            model["name"],
            f"{model['size_mb']:.1f} MB",
            f"[green]{model['quantization']}[/green]",
            str(Path(model["path"]).parent),
        )

    console.print(table)


def download_model(model_name: str, output_dir: Optional[Path] = None) -> Optional[str]:
    """从HuggingFace下载GGUF模型

    Args:
        model_name: HuggingFace上的模型名称（如 TheBloke/Qwen2.5-1.5B-Instruct-GGUF）
        output_dir: 下载目录

    Returns:
        str: 下载的模型路径，失败返回None
    """
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        console.print("[red]请安装 huggingface_hub: pip install huggingface_hub[/red]")
        return None

    if output_dir is None:
        output_dir = Path.home() / "models"

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[cyan]正在下载模型: {model_name}[/cyan]")

    try:
        # 列出可用文件
        from huggingface_hub import list_repo_files

        files = list(list_repo_files(model_name, repo_type="model"))
        gguf_files = [f for f in files if f.endswith(".gguf")]

        if not gguf_files:
            console.print("[red]该仓库中没有GGUF文件[/red]")
            return None

        # 选择最小的量化版本
        selected_file = gguf_files[0]
        for f in gguf_files:
            if "q4" in f.lower() or "q5" in f.lower():
                selected_file = f
                break

        console.print(f"[dim]选择文件: {selected_file}[/dim]")

        # 下载
        output_path = hf_hub_download(
            repo_id=model_name,
            filename=selected_file,
            local_dir=output_dir,
        )

        console.print(f"[green]✓ 下载完成: {output_path}[/green]")
        return output_path

    except Exception as e:
        console.print(f"[red]下载失败: {str(e)}[/red]")
        return None
