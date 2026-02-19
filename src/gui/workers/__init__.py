"""
GUI 工作线程模块

此模块提供后台工作线程，
用于处理耗时操作（如文件解析、AI生成等），
避免阻塞主界面线程。
"""

# 基础工作线程
from .base_worker import BaseWorker

__all__ = [
    "BaseWorker",
]
