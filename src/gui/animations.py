"""
CAE-CLI 动画工具

提供各种Qt动画效果，增强GUI的趣味性
"""

from PySide6.QtCore import Property, QEasingCurve, QObject, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QLabel, QWidget


class AnimationHelper:
    """动画辅助工具类"""

    @staticmethod
    def fade_in(widget: QWidget, duration: int = 300, delay: int = 0):
        """淡入动画

        Args:
            widget: 目标控件
            duration: 动画持续时间(毫秒)
            delay: 延迟时间(毫秒)
        """

        def start():
            widget.setWindowOpacity(0)
            anim = QPropertyAnimation(widget, b"windowOpacity")
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setDuration(duration)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.start()

        if delay > 0:
            QTimer.singleShot(delay, start)
        else:
            start()

    @staticmethod
    def fade_out(widget: QWidget, duration: int = 300, delay: int = 0, on_complete=None):
        """淡出动画

        Args:
            widget: 目标控件
            duration: 动画持续时间(毫秒)
            delay: 延迟时间(毫秒)
            on_complete: 动画完成后的回调
        """

        def start():
            anim = QPropertyAnimation(widget, b"windowOpacity")
            anim.setStartValue(widget.windowOpacity())
            anim.setEndValue(0)
            anim.setDuration(duration)
            anim.setEasingCurve(QEasingCurve.Type.InCubic)
            if on_complete:
                anim.finished.connect(on_complete)
            anim.start()

        if delay > 0:
            QTimer.singleShot(delay, start)
        else:
            start()

    @staticmethod
    def slide_in(widget: QWidget, direction: str = "left", duration: int = 400):
        """滑入动画

        Args:
            widget: 目标控件
            direction: 方向 ("left", "right", "top", "bottom")
            duration: 动画持续时间
        """
        # 保存原始位置
        orig_pos = widget.pos()

        # 设置起始位置
        if direction == "left":
            start_x = orig_pos.x() - 50
            start_y = orig_pos.y()
        elif direction == "right":
            start_x = orig_pos.x() + 50
            start_y = orig_pos.y()
        elif direction == "top":
            start_x = orig_pos.x()
            start_y = orig_pos.y() - 50
        else:  # bottom
            start_x = orig_pos.x()
            start_y = orig_pos.y() + 50

        widget.move(start_x, start_y)
        widget.setWindowOpacity(0)

        # 透明度动画
        opacity = QPropertyAnimation(widget, b"windowOpacity")
        opacity.setStartValue(0)
        opacity.setEndValue(1)
        opacity.setDuration(duration)

        # 位置动画
        pos = QPropertyAnimation(widget, b"pos")
        pos.setStartValue(widget.pos())
        pos.setEndValue(orig_pos)
        pos.setDuration(duration)
        pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        opacity.start()
        pos.start()

    @staticmethod
    def pulse(widget: QWidget, scale: float = 1.05, duration: int = 500):
        """脉冲缩放动画

        Args:
            widget: 目标控件
            scale: 缩放比例
            duration: 动画持续时间
        """
        # 使用setScale实现（需要自定义控件）
        # 这里用透明度模拟
        orig_opacity = widget.windowOpacity()

        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setStartValue(orig_opacity)
        anim.setKeyValueAt(0.5, orig_opacity * 0.8)
        anim.setEndValue(orig_opacity)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.start()

    @staticmethod
    def shake(widget: QWidget, intensity: int = 10, duration: int = 300):
        """摇晃动画（用于错误提示）

        Args:
            widget: 目标控件
            intensity: 摇晃强度
            duration: 动画持续时间
        """
        orig_pos = widget.pos()

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)

        # 创建摇晃关键帧
        key_values = [
            (0.0, orig_pos),
            (0.1, (orig_pos.x() - intensity, orig_pos.y())),
            (0.2, (orig_pos.x() + intensity, orig_pos.y())),
            (0.3, (orig_pos.x() - intensity, orig_pos.y())),
            (0.4, (orig_pos.x() + intensity, orig_pos.y())),
            (0.5, (orig_pos.x() - intensity, orig_pos.y())),
            (0.6, (orig_pos.x() + intensity, orig_pos.y())),
            (0.7, (orig_pos.x() - intensity, orig_pos.y())),
            (0.8, (orig_pos.x() + intensity, orig_pos.y())),
            (0.9, (orig_pos.x() - intensity, orig_pos.y())),
            (1.0, orig_pos),
        ]

        for time, pos in key_values:
            if isinstance(pos, tuple):
                from PySide6.QtCore import QPoint

                pos = QPoint(*pos)
            anim.setKeyValueAt(time, pos)

        anim.setEasingCurve(QEasingCurve.Type.Linear)
        anim.start()


class AnimatedButton(QObject):
    """带动画效果的按钮"""

    def __init__(self, button):
        super().__init__()
        self.button = button
        self._scale = 1.0
        self._glow = 0

    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value
        # 通过样式表应用缩放效果
        if value > 1.0:
            self.button.setStyleSheet(self.button.styleSheet() + "border: 2px solid #FF4500; padding: -2px;")
        else:
            # 恢复原样式
            self.button.setStyleSheet("")

    scale = Property(float, get_scale, set_scale)

    def animate_hover(self):
        """悬停时放大"""
        self.anim = QPropertyAnimation(self, b"scale")
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(1.05)
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

    def animate_leave(self):
        """离开时恢复"""
        self.anim = QPropertyAnimation(self, b"scale")
        self.anim.setStartValue(self._scale)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim.start()


class BreathingLabel:
    """呼吸灯效果的标签"""

    def __init__(self, label: QLabel):
        self.label = label
        self._opacity = 1.0
        self._direction = 1  # 1 = 变亮, -1 = 变暗
        self._timer = None

    def start(self, min_opacity: float = 0.7, speed: int = 30):
        """启动呼吸灯效果

        Args:
            min_opacity: 最小透明度
            speed: 变化速度
        """
        self._min_opacity = min_opacity
        self._speed = speed

        if self._timer:
            self._timer.stop()

        self._timer = QTimer()
        self._timer.timeout.connect(self._update)
        self._timer.start(speed)

    def stop(self):
        """停止呼吸灯效果"""
        if self._timer:
            self._timer.stop()
            self._timer = None
        self.label.setWindowOpacity(1.0)

    def _update(self):
        """更新透明度"""
        self._opacity += 0.01 * self._direction

        if self._opacity >= 1.0:
            self._direction = -1
        elif self._opacity <= self._min_opacity:
            self._direction = 1

        self.label.setWindowOpacity(self._opacity)


class TypingEffect:
    """打字机效果"""

    def __init__(self, label, text: str, speed: int = 30):
        self.label = label
        self.text = text
        self.speed = speed
        self._index = 0
        self._timer = None

    def start(self):
        """开始打字效果"""
        self._index = 0
        self.label.setText("")

        self._timer = QTimer()
        self._timer.timeout.connect(self._type)
        self._timer.start(self.speed)

    def stop(self):
        """停止打字效果"""
        if self._timer:
            self._timer.stop()
        # 显示完整文本
        self.label.setText(self.text)

    def _type(self):
        """逐字显示"""
        if self._index < len(self.text):
            self.label.setText(self.text[: self._index + 1])
            self._index += 1
        else:
            self._timer.stop()


class MarqueeLabel:
    """滚动文字（跑马灯效果）"""

    def __init__(self, label: QLabel, speed: int = 50):
        self.label = label
        self.speed = speed
        self._timer = None
        self._offset = 0
        self._text = ""

    def set_text(self, text: str):
        """设置文字"""
        self._text = text
        self.label.setText(text)

    def start(self):
        """开始滚动"""
        if self._timer:
            return

        self._timer = QTimer()
        self._timer.timeout.connect(self._scroll)
        self._timer.start(self.speed)

    def stop(self):
        """停止滚动"""
        if self._timer:
            self._timer.stop()
            self._timer = None

    def _scroll(self):
        """滚动更新"""
        self._offset = (self._offset + 1) % 20
        # 使用空格实现滚动效果
        self.label.setText(" " * self._offset + self._text)


class LoadingDots:
    """加载中的点动画"""

    def __init__(self, label: QLabel):
        self.label = label
        self._timer = None
        self._frame = 0
        self._frames = ["   ", ".  ", ".. ", "..."]

    def start(self):
        """开始动画"""
        self._timer = QTimer()
        self._timer.timeout.connect(self._update)
        self._timer.start(300)

    def stop(self):
        """停止动画"""
        if self._timer:
            self._timer.stop()
        self.label.setText("")

    def _update(self):
        """更新帧"""
        self.label.setText("正在加载" + self._frames[self._frame])
        self._frame = (self._frame + 1) % len(self._frames)
