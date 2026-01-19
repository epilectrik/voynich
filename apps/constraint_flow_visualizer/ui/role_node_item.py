"""
Role Node Item - QGraphicsItem for role nodes in reachability view.

Visual representation of a control role in the circular layout.
"""

from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QBrush, QPen, QColor, QFont

from core.role_classifier import ControlRole, ROLE_COLORS, ROLE_LABELS


class RoleNodeItem(QGraphicsEllipseItem):
    """
    Visual representation of a control role.

    Displays as a colored circle with label.
    """

    NODE_RADIUS = 35
    BORDER_WIDTH = 2

    def __init__(self, role: ControlRole, parent=None):
        """
        Initialize role node.

        Args:
            role: The ControlRole this node represents
            parent: Parent graphics item
        """
        diameter = self.NODE_RADIUS * 2
        super().__init__(-self.NODE_RADIUS, -self.NODE_RADIUS,
                         diameter, diameter, parent)

        self.role = role
        self._is_active = True
        self._class_count = 0

        self._setup_appearance()
        self._create_label()

    def _setup_appearance(self):
        """Configure visual appearance."""
        color = QColor(ROLE_COLORS.get(self.role, "#808080"))
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("#1a2a3a"), self.BORDER_WIDTH))

        # Enable hover effects
        self.setAcceptHoverEvents(True)

    def _create_label(self):
        """Create text label for the node."""
        self._label = QGraphicsTextItem(self)
        label_text = ROLE_LABELS.get(self.role, self.role.value)
        self._label.setPlainText(label_text)

        # Style the label
        font = QFont("Arial", 9, QFont.Bold)
        self._label.setFont(font)
        self._label.setDefaultTextColor(QColor("#f0f0f0"))

        # Center the label
        rect = self._label.boundingRect()
        self._label.setPos(-rect.width() / 2, -rect.height() / 2)

    def set_active(self, active: bool):
        """
        Set whether this role has any reachable classes.

        Args:
            active: True if role has reachable classes
        """
        self._is_active = active
        if active:
            color = QColor(ROLE_COLORS.get(self.role, "#808080"))
            self.setBrush(QBrush(color))
            self.setOpacity(1.0)
        else:
            # Dimmed appearance for inactive roles
            self.setBrush(QBrush(QColor("#3a3a4a")))
            self.setOpacity(0.5)

    def set_class_count(self, count: int):
        """
        Set the number of classes in this role.

        Args:
            count: Number of reachable classes
        """
        self._class_count = count

    def hoverEnterEvent(self, event):
        """Highlight on hover."""
        if self._is_active:
            pen = self.pen()
            pen.setWidth(self.BORDER_WIDTH + 2)
            pen.setColor(QColor("#f0f0f0"))
            self.setPen(pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Remove highlight on leave."""
        pen = self.pen()
        pen.setWidth(self.BORDER_WIDTH)
        pen.setColor(QColor("#1a2a3a"))
        self.setPen(pen)
        super().hoverLeaveEvent(event)

    def get_edge_point(self, angle: float) -> QPointF:
        """
        Get point on node edge at given angle.

        Args:
            angle: Angle in radians from center

        Returns:
            QPointF on the node boundary
        """
        import math
        x = self.pos().x() + self.NODE_RADIUS * math.cos(angle)
        y = self.pos().y() + self.NODE_RADIUS * math.sin(angle)
        return QPointF(x, y)

    def set_folio_mode(self, mode: str, n_surviving: int = 0, n_pruned: int = 0, n_total: int = 0):
        """
        Set folio-specific coloring mode for Stage 2 compilation view.

        Args:
            mode: 'surviving' (green), 'pruned' (red), 'partial' (orange), 'unused' (gray)
            n_surviving: Number of surviving classes in this role
            n_pruned: Number of pruned classes in this role
            n_total: Total classes in this role used by the folio
        """
        self._is_active = True

        if mode == 'surviving':
            # All folio classes in this role are surviving
            self.setBrush(QBrush(QColor("#4a9a6a")))  # green
            self.setOpacity(1.0)
            border_color = QColor("#2a7a4a")
        elif mode == 'pruned':
            # All folio classes in this role are pruned
            self.setBrush(QBrush(QColor("#9a4a4a")))  # red
            self.setOpacity(1.0)
            border_color = QColor("#7a2a2a")
        elif mode == 'partial':
            # Mix of surviving and pruned
            self.setBrush(QBrush(QColor("#9a7a4a")))  # orange
            self.setOpacity(1.0)
            border_color = QColor("#7a5a2a")
        else:  # unused
            # Folio doesn't use classes from this role
            self.setBrush(QBrush(QColor("#3a3a4a")))  # gray
            self.setOpacity(0.4)
            border_color = QColor("#2a2a3a")

        pen = self.pen()
        pen.setColor(border_color)
        self.setPen(pen)

        # Update tooltip with folio-specific info
        if n_total > 0:
            self.setToolTip(
                f"{self.role.value}\n"
                f"Folio classes: {n_total}\n"
                f"Surviving: {n_surviving}\n"
                f"Pruned: {n_pruned}"
            )
        else:
            self.setToolTip(f"{self.role.value}\n(not used by this folio)")

    def clear_folio_mode(self):
        """Clear folio-specific coloring, return to normal role coloring."""
        color = QColor(ROLE_COLORS.get(self.role, "#808080"))
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("#1a2a3a"), self.BORDER_WIDTH))
        self.setOpacity(1.0)
        self.setToolTip(ROLE_LABELS.get(self.role, self.role.value))
