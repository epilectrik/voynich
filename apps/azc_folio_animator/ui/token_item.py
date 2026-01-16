"""
Token Item - Animated token for binding visualization.

Tokens migrate from manuscript view to position diagram with
physics-based animation reflecting elasticity.

Visual states:
- UNBOUND: Initial, in manuscript
- BINDING: In flight to diagram
- OSCILLATING: At P/R boundary (pre-commitment)
- BOUND: Snapped to position
- VANISHING: Fading out (incompatible)
"""
import math
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QColor, QPen, QBrush, QPainter, QFont
from PyQt5.QtCore import Qt, QPointF, QRectF, QPropertyAnimation, QEasingCurve

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.azc_folio_animator.core.folio_loader import TokenData


class TokenItem(QGraphicsItem):
    """
    Animated token item for binding visualization.

    Physics properties derived from AZCEngine elasticity:
    - High elasticity → bouncy (overshoot, oscillate)
    - Low elasticity → snappy (direct binding)
    """

    # States
    UNBOUND = 0
    BINDING = 1
    OSCILLATING = 2
    BOUND = 3
    VANISHING = 4
    SUPPRESSED = 5

    def __init__(self, token: TokenData, font: QFont, parent=None):
        super().__init__(parent)
        self.token_data = token
        self.font = font
        self.state = self.UNBOUND

        # Visual properties
        self._size = 20.0
        self._color = QColor(255, 255, 255, 128)
        self._glow_intensity = 0.0
        self._scale = 1.0
        self._rotation = 0.0
        self._opacity = 1.0

        # Physics state
        self._velocity = QPointF(0, 0)
        self._target_pos = QPointF(0, 0)
        self._spring_constant = 0.5
        self._damping = 0.3

        # Animation state
        self._oscillation_phase = 0.0
        self._oscillation_speed = 0.05

        # Position
        self._current_pos = QPointF(0, 0)

    def boundingRect(self) -> QRectF:
        """Return bounding rectangle."""
        size = self._size * self._scale
        margin = 5
        return QRectF(-size/2 - margin, -size/2 - margin,
                      size + margin*2, size + margin*2)

    def paint(self, painter: QPainter, option, widget):
        """Paint the token."""
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate size with scale
        size = self._size * self._scale

        if self.state == self.UNBOUND:
            # White circle, semi-transparent, pulsing
            pulse = 0.7 + 0.3 * math.sin(self._oscillation_phase)
            color = QColor(255, 255, 255, int(128 * pulse))
            painter.setPen(QPen(color, 1))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QRectF(-size/2, -size/2, size, size))

        elif self.state == self.BINDING:
            # Yellow glow, scaling
            glow_color = QColor(255, 200, 0, int(200 * self._glow_intensity))
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(glow_color))

            # Outer glow
            glow_size = size * 1.5
            painter.drawEllipse(QRectF(-glow_size/2, -glow_size/2, glow_size, glow_size))

            # Core
            core_color = QColor(255, 220, 50, 220)
            painter.setBrush(QBrush(core_color))
            painter.drawEllipse(QRectF(-size/2, -size/2, size, size))

        elif self.state == self.OSCILLATING:
            # Slow rotation indicator
            painter.save()
            painter.rotate(self._rotation)

            # Ring indicator
            ring_color = QColor(0, 170, 204, 180)
            painter.setPen(QPen(ring_color, 2))
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawEllipse(QRectF(-size/2, -size/2, size, size))

            # Orientation mark
            painter.setPen(QPen(ring_color, 3))
            painter.drawLine(QPointF(0, -size/2), QPointF(0, -size/2 - 5))

            painter.restore()

            # Core
            core_color = QColor(255, 220, 100, 200)
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(core_color))
            painter.drawEllipse(QRectF(-size*0.3, -size*0.3, size*0.6, size*0.6))

        elif self.state == self.BOUND:
            # Solid position color
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(self._color))
            painter.drawEllipse(QRectF(-size/2, -size/2, size, size))

        elif self.state == self.VANISHING:
            # Fading ghost
            fade_color = QColor(100, 100, 100, int(80 * self._opacity))
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(QBrush(fade_color))
            painter.drawEllipse(QRectF(-size/2, -size/2, size, size))

        elif self.state == self.SUPPRESSED:
            # Ghost for "show suppressed" mode
            ghost_color = QColor(80, 80, 80, 60)
            painter.setPen(QPen(QColor(100, 100, 100, 80), 1, Qt.DashLine))
            painter.setBrush(QBrush(ghost_color))
            painter.drawEllipse(QRectF(-size/2, -size/2, size, size))

    def set_state(self, state: int):
        """Set token state."""
        self.state = state
        self.update()

    def set_target(self, pos: QPointF):
        """Set target position for binding animation."""
        self._target_pos = pos

    def set_color(self, color: QColor):
        """Set bound state color."""
        self._color = color

    def set_physics(self, spring: float, damping: float):
        """Set physics parameters."""
        self._spring_constant = spring
        self._damping = damping

    def tick(self, dt: float):
        """Physics tick for animation."""
        if self.state == self.BINDING:
            # Spring physics toward target
            dx = self._target_pos.x() - self._current_pos.x()
            dy = self._target_pos.y() - self._current_pos.y()

            # Acceleration
            ax = dx * self._spring_constant
            ay = dy * self._spring_constant

            # Apply with damping
            self._velocity.setX(self._velocity.x() * (1 - self._damping) + ax * dt)
            self._velocity.setY(self._velocity.y() * (1 - self._damping) + ay * dt)

            # Update position
            self._current_pos += self._velocity

            # Update glow based on speed
            speed = math.sqrt(self._velocity.x()**2 + self._velocity.y()**2)
            self._glow_intensity = min(1.0, speed * 0.1)

            # Check if arrived
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 2.0 and speed < 0.5:
                self.state = self.BOUND
                self._glow_intensity = 0

            self.setPos(self._current_pos)

        elif self.state == self.OSCILLATING:
            # Slow rotation
            self._oscillation_phase += self._oscillation_speed
            self._rotation = 30 * math.sin(self._oscillation_phase)

        elif self.state == self.VANISHING:
            # Fade out
            self._opacity -= dt * 2
            if self._opacity <= 0:
                self._opacity = 0
                self.state = self.SUPPRESSED

        elif self.state == self.UNBOUND:
            # Gentle pulse
            self._oscillation_phase += 0.1

        self.update()

    def start_binding(self, target: QPointF, spring: float, damping: float):
        """Start binding animation to target position."""
        self._target_pos = target
        self._spring_constant = spring
        self._damping = damping
        self._current_pos = self.pos()
        self.state = self.BINDING
        self._glow_intensity = 1.0

    def start_vanish(self):
        """Start vanish animation (incompatible token)."""
        self.state = self.VANISHING
        self._opacity = 1.0
