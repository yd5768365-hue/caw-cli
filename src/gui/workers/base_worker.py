"""
基础工作线程

此模块提供工作线程基类，
用于在后台线程中执行耗时操作。
"""

from PySide6.QtCore import QThread, Signal


class BaseWorker(QThread):
    """基础工作线程类

    使用方法:
        1. 继承此类并重写 run() 方法
        2. 在 run() 中执行耗时操作
        3. 通过信号通知主线程进度和结果
    """

    # 信号：任务完成（传递结果）
    finished = Signal(object)

    # 信号：任务失败（传递错误信息）
    error = Signal(str)

    # 信号：进度更新（传递进度百分比）
    progress = Signal(int)

    # 信号：状态更新（传递状态消息）
    status = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_cancelled = False

    def run(self):
        """执行后台任务

        此方法应在子类中被重写，
        实现具体的耗时操作。
        """
        try:
            self._run_internal()
            self.finished.emit(None)
        except Exception as e:
            self.error.emit(str(e))

    def _run_internal(self):
        """内部运行方法

        子类应重写此方法实现具体逻辑。
        """
        pass

    def cancel(self):
        """取消任务

        设置取消标志，
        子类应在执行过程中检查此标志。
        """
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """检查是否已取消

        Returns:
            bool: 是否已取消
        """
        return self._is_cancelled


class GeometryWorker(BaseWorker):
    """几何解析工作线程"""

    def __init__(self, file_path: str, file_format: str = "auto"):
        super().__init__()
        self.file_path = file_path
        self.file_format = file_format

    def _run_internal(self):
        """执行几何解析"""
        self.status.emit(f"正在解析: {self.file_path}")

        # TODO: 调用 sw_helper.geometry 进行解析
        # 模拟耗时操作
        for i in range(10):
            if self.is_cancelled():
                self.error.emit("任务已取消")
                return
            self.progress.emit((i + 1) * 10)
            self.sleep(1)

        result = {
            "file": self.file_path,
            "format": self.file_format,
            "faces": 0,
            "edges": 0,
            "vertices": 0,
        }
        self.finished.emit(result)


class MeshWorker(BaseWorker):
    """网格分析工作线程"""

    def __init__(self, file_path: str, metric: str = "all"):
        super().__init__()
        self.file_path = file_path
        self.metric = metric

    def _run_internal(self):
        """执行网格分析"""
        self.status.emit(f"正在分析: {self.file_path}")

        # TODO: 调用 sw_helper.mesh 进行分析
        for i in range(10):
            if self.is_cancelled():
                self.error.emit("任务已取消")
                return
            self.progress.emit((i + 1) * 10)
            self.sleep(1)

        result = {
            "file": self.file_path,
            "metric": self.metric,
            "total_elements": 0,
            "bad_elements": 0,
        }
        self.finished.emit(result)


class AIWorker(BaseWorker):
    """AI生成工作线程"""

    def __init__(self, description: str, model: str = "auto", mode: str = "full"):
        super().__init__()
        self.description = description
        self.model = model
        self.mode = mode

    def _run_internal(self):
        """执行AI生成"""
        self.status.emit("正在生成3D模型...")

        # TODO: 调用 sw_helper.ai 进行生成
        for i in range(10):
            if self.is_cancelled():
                self.error.emit("任务已取消")
                return
            self.progress.emit((i + 1) * 10)
            self.sleep(1)

        result = {
            "description": self.description,
            "model": self.model,
            "output_file": "generated_model.step",
        }
        self.finished.emit(result)


class ChatWorker(BaseWorker):
    """AI对话工作线程"""

    def __init__(self, question: str, model: str = "phi3:mini"):
        super().__init__()
        self.question = question
        self.model = model

    def _run_internal(self):
        """执行AI对话"""
        self.status.emit("正在思考...")

        # TODO: 调用 sw_helper.chat 进行对话
        # 模拟思考时间
        for i in range(5):
            if self.is_cancelled():
                self.error.emit("任务已取消")
                return
            self.progress.emit((i + 1) * 20)
            self.sleep(1)

        result = {
            "question": self.question,
            "answer": "[AI回答开发中...]",
        }
        self.finished.emit(result)
