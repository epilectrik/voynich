"""
Connectivity Edge Item - QGraphicsItem for directed edges.

Per C111: 65% of transitions are asymmetric.
Edges show structural direction, not execution sequence.
"""

import math
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QPainterPath, QPolygonF

from core.role_classifier import ControlRole


class ConnectivityEdgeItem(QGraphicsPathItem):
    """
    Directed edge between role nodes.

    Shows structural asymmetry with arrowhead.
    Direction indicates legal transition direction, NOT execution sequence.
    """

    ARROW_SIZE = 10
    LINE_WIDTH = 2
    CURVE_FACTOR = 0.2  # For curved edges between same roles

    def __init__(self, from_role: ControlRole, to_role: ControlRole, parent=None):
        """
        Initialize edge.

        Args:
            from_role: Source role
            to_role: Destination role
            parent: Parent graphics item
        """
        super().__init__(parent)

        self.from_role = from_role
        self.to_role = to_role
        self._from_pos = QPointF(0, 0)
        self._to_pos = QPointF(0, 0)
        self._is_visible = True
        self._edge_count = 0

        self._setup_appearance()

    def _setup_appearance(self):
        """Configure visual appearance."""
        self.setPen(QPen(QColor("#5a7a9a"), self.LINE_WIDTH))
        self.setZValue(-1)  # Behind nodes

    def set_endpoints(self, from_pos: QPointF, to_pos: QPointF, from_radius: float, to_radius: float):
        """
        Set edge endpoints, accounting for node radii.

        Args:
            from_pos: Center of source node
            to_pos: Center of destination node
            from_radius: Radius of source node
            to_radius: Radius of destination node
        """
        # Calculate angle between centers
        dx = to_pos.x() - from_pos.x()
        dy = to_pos.y() - from_pos.y()
        angle = math.atan2(dy, dx)

        # Offset start and end points to node edges
        start_x = from_pos.x() + from_radius * math.cos(angle)
        start_y = from_pos.y() + from_radius * math.sin(angle)

        end_x = to_pos.x() - to_radius * math.cos(angle)
        end_y = to_pos.y() - to_radius * math.sin(angle)

        self._from_pos = QPointF(start_x, start_y)
        self._to_pos = QPointF(end_x, end_y)

        self._rebuild_path()

    def _rebuild_path(self):
        """Rebuild the path with line and arrowhead."""
        path = QPainterPath()

        # Check for self-loop
        if self.from_role == self.to_role:
            self._build_self_loop(path)
        else:
            self._build_straight_arrow(path)

        self.setPath(path)

    def _build_straight_arrow(self, path: QPainterPath):
        """Build straight arrow between different roles."""
        path.moveTo(self._from_pos)
        path.lineTo(self._to_pos)

        # Add arrowhead
        self._add_arrowhead(path, self._from_pos, self._to_pos)

    def _build_self_loop(self, path: QPainterPath):
        """Build curved self-loop for same role."""
        # Create a loop above/beside the node
        cx = self._from_pos.x()
        cy = self._from_pos.y() - 40  # Loop center above

        # Bezier curve for loop
        path.moveTo(self._from_pos)
        path.cubicTo(
            QPointF(cx - 30, cy - 20),
            QPointF(cx + 30, cy - 20),
            self._to_pos
        )

        # Simplified arrowhead for self-loop
        self._add_arrowhead(path, QPointF(cx + 20, cy), self._to_pos)

    def _add_arrowhead(self, path: QPainterPath, from_pt: QPointF, to_pt: QPointF):
        """Add arrowhead at destination."""
        dx = to_pt.x() - from_pt.x()
        dy = to_pt.y() - from_pt.y()
        angle = math.atan2(dy, dx)

        # Arrow points
        arrow_p1 = QPointF(
            to_pt.x() - self.ARROW_SIZE * math.cos(angle - math.pi / 6),
            to_pt.y() - self.ARROW_SIZE * math.sin(angle - math.pi / 6)
        )
        arrow_p2 = QPointF(
            to_pt.x() - self.ARROW_SIZE * math.cos(angle + math.pi / 6),
            to_pt.y() - self.ARROW_SIZE * math.sin(angle + math.pi / 6)
        )

        # Draw arrowhead
        path.moveTo(to_pt)
        path.lineTo(arrow_p1)
        path.moveTo(to_pt)
        path.lineTo(arrow_p2)

    def set_visible_state(self, visible: bool):
        """
        Set edge visibility (vanishing semantics).

        Per C444/C468: Illegal paths are absent, not greyed.

        Args:
            visible: True if edge is legal, False to hide
        """
        self._is_visible = visible
        self.setVisible(visible)

    def set_edge_count(self, count: int):
        """
        Set number of class-level edges this role edge represents.

        Args:
            count: Number of underlying class transitions
        """
        self._edge_count = count
        # Could adjust line width based on count
        if count > 50:
            self.setPen(QPen(QColor("#7090b0"), self.LINE_WIDTH + 1))
        elif count > 10:
            self.setPen(QPen(QColor("#5a7a9a"), self.LINE_WIDTH))
        else:
            self.setPen(QPen(QColor("#4a6a8a"), max(1, self.LINE_WIDTH - 1)))

    def set_highlighted(self, highlighted: bool):
        """Set highlight state."""
        if highlighted:
            self.setPen(QPen(QColor("#f0c060"), self.LINE_WIDTH + 1))
        else:
            self.setPen(QPen(QColor("#5a7a9a"), self.LINE_WIDTH))
