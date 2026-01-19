"""
Reachability View - Displays role-level reachability as circular graph.

Per C171: Closed-loop control, not stepwise procedure.
Per C391: Time-reversal symmetric - direction ≠ sequence.
Per C111: 65% asymmetric transitions shown with directed edges.

Layout is circular to emphasize recurrence over flow.
"""

import math
from typing import Dict, Tuple, Optional

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPainter

from core.role_classifier import ControlRole, RoleClassifier
from core.reachability_computer import ReachabilityComputer, RoleReachability
from .role_node_item import RoleNodeItem
from .connectivity_edge_item import ConnectivityEdgeItem


class ReachabilityView(QGraphicsView):
    """
    Displays role-level reachability as circular graph.

    Circular layout emphasizes recurrent viability cycles.
    No left-to-right flow, no start/end markers.
    """

    LAYOUT_RADIUS = 120  # Radius of circular layout

    def __init__(self, data_store, parent=None):
        """
        Initialize view.

        Args:
            data_store: DataStore with grammar information
            parent: Parent widget
        """
        super().__init__(parent)

        self.data_store = data_store
        self.classifier = RoleClassifier(data_store)
        self.computer = ReachabilityComputer(data_store, self.classifier)

        self._nodes: Dict[ControlRole, RoleNodeItem] = {}
        self._edges: Dict[Tuple[ControlRole, ControlRole], ConnectivityEdgeItem] = {}

        self._setup_view()
        self._setup_scene()
        self._build_layout()
        self._create_edges()

        # Show baseline (all legal)
        self._show_baseline()

    def _setup_view(self):
        """Configure view settings."""
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor("#1a2a3a"))

    def _setup_scene(self):
        """Create and configure the scene."""
        self._scene = QGraphicsScene(self)
        self._scene.setSceneRect(-200, -200, 400, 400)
        self.setScene(self._scene)

    def _build_layout(self):
        """Build circular layout of role nodes."""
        roles = list(ControlRole)
        n_roles = len(roles)

        for i, role in enumerate(roles):
            # Position in circle
            angle = 2 * math.pi * i / n_roles - math.pi / 2  # Start from top
            x = self.LAYOUT_RADIUS * math.cos(angle)
            y = self.LAYOUT_RADIUS * math.sin(angle)

            # Create node
            node = RoleNodeItem(role)
            node.setPos(x, y)
            self._scene.addItem(node)
            self._nodes[role] = node

    def _create_edges(self):
        """Create all possible edges (visibility controlled by legality)."""
        for role_a in ControlRole:
            for role_b in ControlRole:
                edge = ConnectivityEdgeItem(role_a, role_b)
                self._scene.addItem(edge)
                self._edges[(role_a, role_b)] = edge

                # Position edge between nodes
                node_a = self._nodes[role_a]
                node_b = self._nodes[role_b]
                edge.set_endpoints(
                    node_a.pos(),
                    node_b.pos(),
                    RoleNodeItem.NODE_RADIUS,
                    RoleNodeItem.NODE_RADIUS
                )

    def _show_baseline(self):
        """Show baseline (unconstrained) reachability."""
        reachability = self.computer.compute_reachability(None)
        self._apply_reachability(reachability)

    def _apply_reachability(self, reachability: RoleReachability):
        """
        Apply reachability state to visualization.

        Per vanishing semantics: illegal edges are hidden, not greyed.

        Args:
            reachability: RoleReachability from computer
        """
        # Update edge visibility
        for (role_a, role_b), edge in self._edges.items():
            is_legal = reachability.legal_transitions.get((role_a, role_b), False)
            edge.set_visible_state(is_legal)
            edge.set_edge_count(reachability.edge_counts.get((role_a, role_b), 0))

        # Update node activity
        for role, node in self._nodes.items():
            # Node is active if it has any incoming or outgoing edges
            has_edges = False
            for other_role in ControlRole:
                if reachability.legal_transitions.get((role, other_role), False):
                    has_edges = True
                    break
                if reachability.legal_transitions.get((other_role, role), False):
                    has_edges = True
                    break
            node.set_active(has_edges)

    def update_reachability(self, reachable_classes: Optional[set] = None):
        """
        Update view with new reachability state.

        Args:
            reachable_classes: Set of legal class IDs, or None for baseline
        """
        reachability = self.computer.compute_reachability(reachable_classes)
        self._apply_reachability(reachability)

    def get_current_reachability(self) -> RoleReachability:
        """Get current reachability state."""
        return self.computer.compute_reachability(None)

    def reset(self):
        """Reset to baseline state."""
        # Clear any folio-specific coloring
        for node in self._nodes.values():
            node.clear_folio_mode()
        self._show_baseline()

    def show_folio_compilation(self, folio_id: str, folio_classes: set,
                                surviving: set, pruned: set):
        """
        Show Stage 2 compilation for a specific B folio.

        Colors nodes based on whether they contain:
        - Green: Surviving classes (used by folio AND reachable)
        - Red: Pruned classes (used by folio BUT unreachable)
        - Orange: Partial (mix of surviving and pruned)
        - Gray: Unused (folio doesn't use classes from this role)

        Args:
            folio_id: The B folio identifier
            folio_classes: Set of all class IDs the folio uses
            surviving: Set of class IDs that survive compilation
            pruned: Set of class IDs that are pruned
        """
        from core.role_classifier import ControlRole

        # Compute per-role statistics
        role_stats = {}
        for role in ControlRole:
            # Get classes that belong to this role
            role_classes = self.classifier.get_classes_for_role(role)
            # Intersect with folio's classes
            folio_role_classes = folio_classes & role_classes
            n_total = len(folio_role_classes)

            if n_total == 0:
                role_stats[role] = ('unused', 0, 0, 0)
            else:
                n_surviving = len(folio_role_classes & surviving)
                n_pruned = len(folio_role_classes & pruned)

                if n_pruned == 0:
                    mode = 'surviving'
                elif n_surviving == 0:
                    mode = 'pruned'
                else:
                    mode = 'partial'

                role_stats[role] = (mode, n_surviving, n_pruned, n_total)

        # Apply folio-specific coloring to nodes
        for role, node in self._nodes.items():
            mode, n_surviving, n_pruned, n_total = role_stats.get(
                role, ('unused', 0, 0, 0)
            )
            node.set_folio_mode(mode, n_surviving, n_pruned, n_total)

        # Update edges based on folio's actual transitions
        # For now, keep existing edge visibility but this could be enhanced
        # to show only transitions the folio actually uses

    def resizeEvent(self, event):
        """Handle resize."""
        super().resizeEvent(event)
        self.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
