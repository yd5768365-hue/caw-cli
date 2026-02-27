"""
CAE-CLI 粒子特效系统

AI 风格粒子动画效果 - 类似 Trae.ai
"""

import math
import random

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class Particle:
    """单个粒子"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.5, 0.5)  # X方向速度
        self.vy = random.uniform(-0.5, 0.5)  # Y方向速度
        self.radius = random.uniform(1, 3)  # 粒子大小
        self.base_alpha = random.uniform(0.3, 0.8)  # 基础透明度
        self.connected = False  # 是否与其他粒子连接

        # 边界
        self.width = width
        self.height = height

    def update(self):
        """更新粒子位置"""
        self.x += self.vx
        self.y += self.vy

        # 边界反弹
        if self.x < 0 or self.x > self.width:
            self.vx *= -1
            self.x = max(0, min(self.x, self.width))

        if self.y < 0 or self.y > self.height:
            self.vy *= -1
            self.y = max(0, min(self.y, self.height))

    def distance_to(self, other):
        """计算到另一个粒子的距离"""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


class ParticleSystem:
    """粒子系统"""

    def __init__(self, width, height, particle_count=60):
        self.width = width
        self.height = height
        self.particles = []
        self.particle_count = particle_count
        self.mouse_pos = None
        self.mouse_connected = False

        # 颜色配置 - 工程蓝橙风格
        self.particle_color = QColor(22, 93, 255)  # 工程蓝 #165DFF
        self.particle_glow = QColor(255, 125, 0, 80)  # 工程橙 #FF7D00
        self.line_color = QColor(22, 93, 255, 60)  # 连线颜色
        self.mouse_line_color = QColor(255, 125, 0, 120)  # 鼠标连线 - 橙色

        # 连接距离
        self.connect_distance = 150
        self.mouse_distance = 200

        # 初始化粒子
        self._init_particles()

    def _init_particles(self):
        """初始化粒子"""
        self.particles = []
        for _ in range(self.particle_count):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            self.particles.append(Particle(x, y, self.width, self.height))

    def set_mouse(self, x, y):
        """设置鼠标位置"""
        self.mouse_pos = QPointF(x, y) if x is not None else None

    def resize(self, width, height):
        """调整大小"""
        self.width = width
        self.height = height
        for p in self.particles:
            p.width = width
            p.height = height

    def update(self):
        """更新粒子系统"""
        for particle in self.particles:
            particle.update()

            # 鼠标吸引力
            if self.mouse_pos:
                dx = self.mouse_pos.x() - particle.x
                dy = self.mouse_pos.y() - particle.y
                dist = math.sqrt(dx * dx + dy * dy)

                if dist < self.mouse_distance and dist > 0:
                    # 轻微向鼠标移动
                    force = (self.mouse_distance - dist) / self.mouse_distance
                    particle.vx += (dx / dist) * force * 0.02
                    particle.vy += (dy / dist) * force * 0.02

    def draw(self, painter):
        """绘制粒子系统"""
        # 绘制粒子之间的连线
        self._draw_connections(painter)

        # 绘制粒子
        self._draw_particles(painter)

        # 绘制鼠标连线
        if self.mouse_pos:
            self._draw_mouse_connections(painter)

    def _draw_particles(self, painter):
        """绘制粒子"""
        for particle in self.particles:
            # 绘制发光效果（外圈）
            glow_brush = QBrush(self.particle_glow)
            painter.setBrush(glow_brush)
            painter.setPen(Qt.PenStyle.NoPen)

            # 外圈（发光）
            glow_radius = particle.radius * 3
            painter.setOpacity(particle.base_alpha * 0.3)
            painter.drawEllipse(QPointF(particle.x, particle.y), glow_radius, glow_radius)

            # 内圈（核心）
            painter.setOpacity(particle.base_alpha)
            painter.setBrush(QBrush(self.particle_color))
            painter.drawEllipse(QPointF(particle.x, particle.y), particle.radius, particle.radius)

        painter.setOpacity(1.0)

    def _draw_connections(self, painter):
        """绘制粒子之间的连线"""
        painter.setPen(QPen(self.line_color, 1))

        for i, p1 in enumerate(self.particles):
            for j in range(i + 1, len(self.particles)):
                p2 = self.particles[j]
                dist = p1.distance_to(p2)

                if dist < self.connect_distance:
                    # 计算透明度（距离越近越不透明）
                    alpha = (1 - dist / self.connect_distance) * 0.6

                    # 使用渐变效果的线条
                    color = QColor(self.particle_color)
                    color.setAlphaF(alpha)
                    painter.setPen(QPen(color, 1))

                    painter.drawLine(QPointF(p1.x, p1.y), QPointF(p2.x, p2.y))

    def _draw_mouse_connections(self, painter):
        """绘制鼠标与粒子的连线"""
        for particle in self.particles:
            dx = self.mouse_pos.x() - particle.x
            dy = self.mouse_pos.y() - particle.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < self.mouse_distance:
                # 距离越近连线越亮
                alpha = (1 - dist / self.mouse_distance) * 0.8
                color = QColor(self.mouse_line_color)
                color.setAlphaF(alpha)

                # 线条粗细随距离变化
                width = max(0.5, 2 * (1 - dist / self.mouse_distance))

                painter.setPen(QPen(color, width))
                painter.drawLine(QPointF(particle.x, particle.y), self.mouse_pos)


class ParticleWidget(QWidget):
    """粒子动画部件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # 初始化粒子系统
        self.particle_system = None
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(16)  # ~60fps

    def resizeEvent(self, event):
        """窗口大小改变"""
        super().resizeEvent(event)
        if self.particle_system is None:
            self.particle_system = ParticleSystem(self.width(), self.height())
        else:
            self.particle_system.resize(self.width(), self.height())

    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if self.particle_system:
            self.particle_system.set_mouse(event.pos().x(), event.pos().y())

    def leaveEvent(self, event):
        """鼠标离开"""
        if self.particle_system:
            self.particle_system.set_mouse(None, None)

    def paintEvent(self, event):
        """绘制"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.particle_system:
            # 更新粒子
            self.particle_system.update()

            # 绘制
            self.particle_system.draw(painter)

    def _animate(self):
        """动画更新"""
        self.update()


class ParticleOverlay:
    """粒子覆盖层 - 可以添加到其他窗口上"""

    def __init__(self, target_widget):
        self.target = target_widget
        self.particle_widget = None

    def install(self):
        """安装粒子效果"""
        if self.particle_widget is None:
            self.particle_widget = ParticleWidget()
            self.particle_widget.setGeometry(self.target.geometry())
            self.particle_widget.show()

    def uninstall(self):
        """卸载粒子效果"""
        if self.particle_widget:
            self.particle_widget.close()
            self.particle_widget = None

    def update_geometry(self):
        """更新位置"""
        if self.particle_widget:
            self.particle_widget.setGeometry(self.target.geometry())
