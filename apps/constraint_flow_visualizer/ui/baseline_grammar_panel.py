"""
Baseline Grammar Panel - Always-Visible Grammar Reference.

Shows the baseline 49-class grammar alongside the conditioned view
to demonstrate: "Grammar unchanged. Reachable subset contracts."

Per expert guidance:
> BASELINE (left): Full 49 classes, universal hazard skeleton
> CONDITIONED (right): Same structure with subtraction overlay
> User must experience: "Nothing changed. Only what is reachable."
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPalette

from core.reachability_engine import GrammarState, ReachabilityResult
from core.data_loader import get_data_store, is_atomic_hazard, is_decomposable_hazard


# Role colors (muted for dark theme)
ROLE_COLORS = {
    'kernel': '#4a6a8a',      # Blue-gray
    'hazard': '#8a4a5a',      # Muted red
    'recovery': '#5a7a5a',    # Muted green
    'transport': '#7a6a5a',   # Brown
    'default': '#5a5a6a',     # Gray
}


class ClassTile(QFrame):
    """A single instruction class tile."""

    def __init__(self, class_id: int, role: str = 'default', parent=None):
        super().__init__(parent)
        self.class_id = class_id
        self.role = role
        self._is_reachable = True

        self.setFixedSize(36, 36)
        self._setup_ui()
        self._update_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.label = QLabel(str(self.class_id))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.label)

    def _update_style(self):
        """Update tile appearance based on reachability."""
        base_color = ROLE_COLORS.get(self.role, ROLE_COLORS['default'])

        if self._is_reachable:
            # Solid, visible
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {base_color};
                    border: 1px solid #3a4a5a;
                    border-radius: 3px;
                }}
            """)
            self.label.setStyleSheet(
                "background: transparent; border: none; "
                "color: #e0d8c8; font-weight: bold;"
            )
        else:
            # Hollow, faded - represents pruned class
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: transparent;
                    border: 2px dashed #3a3a4a;
                    border-radius: 3px;
                }}
            """)
            self.label.setStyleSheet(
                "background: transparent; border: none; "
                "color: #4a4a5a; font-weight: normal;"
            )

    def set_reachable(self, reachable: bool):
        """Set whether this class is reachable."""
        if self._is_reachable != reachable:
            self._is_reachable = reachable
            self._update_style()


class GrammarView(QFrame):
    """A view showing all 49 instruction classes in a grid."""

    def __init__(self, title: str, is_baseline: bool = True, parent=None):
        super().__init__(parent)
        self.is_baseline = is_baseline
        self.tiles = {}

        self._setup_ui(title)

    def _setup_ui(self, title: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Header
        header = QLabel(title)
        header.setObjectName("header")
        header.setStyleSheet("font-weight: bold; color: #e0d8c8;")
        layout.addWidget(header)

        # Subtitle
        if self.is_baseline:
            subtitle = QLabel("49 classes | 17 forbidden transitions")
        else:
            subtitle = QLabel("Reachable subset under legality field")
        subtitle.setObjectName("status")
        subtitle.setStyleSheet("color: #8090a0; font-size: 10px;")
        layout.addWidget(subtitle)
        self.subtitle = subtitle

        # Grid of class tiles
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(4, 4, 4, 4)
        grid_layout.setSpacing(3)

        # Load class data
        data_store = get_data_store()

        # Arrange in 7x7 grid (49 classes)
        for class_id in range(1, 50):
            row = (class_id - 1) // 7
            col = (class_id - 1) % 7

            # Determine role for coloring
            cls = data_store.classes.get(class_id)
            role = cls.role if cls else 'default'

            tile = ClassTile(class_id, role)
            grid_layout.addWidget(tile, row, col)
            self.tiles[class_id] = tile

        layout.addWidget(grid_widget)

        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(12)

        for role, color in [
            ('kernel', ROLE_COLORS['kernel']),
            ('hazard', ROLE_COLORS['hazard']),
            ('recovery', ROLE_COLORS['recovery']),
        ]:
            legend_item = QLabel(f"■ {role}")
            legend_item.setStyleSheet(f"color: {color}; font-size: 9px;")
            legend_layout.addWidget(legend_item)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        # Stats label (for conditioned view)
        if not self.is_baseline:
            self.stats_label = QLabel("")
            self.stats_label.setStyleSheet(
                "color: #a0b0c0; font-size: 10px; margin-top: 4px;"
            )
            layout.addWidget(self.stats_label)

    def update_reachability(self, grammar_state: GrammarState):
        """Update tile reachability based on grammar state."""
        if self.is_baseline:
            # Baseline always shows all classes as reachable
            for tile in self.tiles.values():
                tile.set_reachable(True)
        else:
            # Conditioned view shows pruned classes as hollow
            for class_id, tile in self.tiles.items():
                tile.set_reachable(class_id in grammar_state.reachable_classes)

            # Update stats
            self.stats_label.setText(
                f"{grammar_state.n_reachable}/49 reachable | "
                f"{grammar_state.n_pruned} unavailable"
            )
            self.subtitle.setText(
                f"Reachable subset ({grammar_state.reachability_ratio:.0%})"
            )


class BaselineGrammarPanel(QFrame):
    """
    Panel showing baseline vs conditioned grammar side-by-side.

    Demonstrates the core principle:
    "Grammar unchanged. Reachable subset contracts."
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Panel header
        header = QLabel("GRAMMAR: BASELINE vs CONDITIONED")
        header.setObjectName("header")
        layout.addWidget(header)

        # Side-by-side views
        views_layout = QHBoxLayout()
        views_layout.setSpacing(12)

        # Baseline view (left)
        self.baseline_view = GrammarView("BASELINE (universal)", is_baseline=True)
        views_layout.addWidget(self.baseline_view)

        # Arrow indicator
        arrow_label = QLabel("→")
        arrow_label.setStyleSheet(
            "font-size: 24px; color: #5a6a7a; font-weight: bold;"
        )
        arrow_label.setAlignment(Qt.AlignCenter)
        views_layout.addWidget(arrow_label)

        # Conditioned view (right)
        self.conditioned_view = GrammarView(
            "CONDITIONED (under legality)", is_baseline=False
        )
        views_layout.addWidget(self.conditioned_view)

        layout.addLayout(views_layout)

        # Footer message
        self.footer = QLabel(
            "Grammar unchanged. Reachable subset contracts."
        )
        self.footer.setStyleSheet(
            "color: #8090a0; font-style: italic; margin-top: 4px;"
        )
        self.footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer)

    @pyqtSlot(object)
    def update_grammar(self, reachability_result: ReachabilityResult):
        """Update the conditioned view based on reachability result."""
        self.conditioned_view.update_reachability(
            reachability_result.grammar_state
        )

        # Update footer with summary
        gs = reachability_result.grammar_state
        if gs.n_pruned == 0:
            self.footer.setText(
                "No restrictions. Full grammar reachable."
            )
        else:
            self.footer.setText(
                f"Grammar unchanged. {gs.n_pruned} classes unavailable "
                f"under legality field."
            )

    def reset(self):
        """Reset to baseline state (no conditioning)."""
        # Create an "all reachable" grammar state
        full_state = GrammarState(
            reachable_classes=set(range(1, 50)),
            pruned_classes=set()
        )
        self.conditioned_view.update_reachability(full_state)
        self.footer.setText("Grammar unchanged. Reachable subset contracts.")
