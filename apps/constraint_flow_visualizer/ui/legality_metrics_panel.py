"""
Legality Metrics Panel - Shows reachability metrics.

Displays class count, transition count, escape percentage.
"""

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

from core.reachability_computer import RoleReachability


class LegalityMetricsPanel(QFrame):
    """
    Bottom panel showing legality metrics.

    Shows:
    - Legal classes: X/49
    - Legal transitions: X/Y
    - Escape %: X%
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Build the UI."""
        self.setStyleSheet("background-color: #1a2a3a;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(24)

        # Legal classes
        self._classes_label = QLabel("Legal classes: 49/49")
        self._classes_label.setStyleSheet("color: #a0b0c0; font-size: 10px;")
        layout.addWidget(self._classes_label)

        # Separator
        sep1 = QLabel("|")
        sep1.setStyleSheet("color: #4a5a6a;")
        layout.addWidget(sep1)

        # Legal transitions
        self._transitions_label = QLabel("Legal transitions: --")
        self._transitions_label.setStyleSheet("color: #a0b0c0; font-size: 10px;")
        layout.addWidget(self._transitions_label)

        # Separator
        sep2 = QLabel("|")
        sep2.setStyleSheet("color: #4a5a6a;")
        layout.addWidget(sep2)

        # Escape percentage
        self._escape_label = QLabel("Connectivity: 100%")
        self._escape_label.setStyleSheet("color: #a0b0c0; font-size: 10px;")
        layout.addWidget(self._escape_label)

        layout.addStretch()

    def update_metrics(self, reachability: RoleReachability):
        """
        Update display with current metrics.

        Args:
            reachability: RoleReachability from computer
        """
        # Classes
        total_classes = 49
        legal_classes = reachability.reachable_classes
        self._classes_label.setText(f"Legal classes: {legal_classes}/{total_classes}")

        if legal_classes == total_classes:
            self._classes_label.setStyleSheet("color: #60a060; font-size: 10px;")
        elif legal_classes >= 45:
            self._classes_label.setStyleSheet("color: #a0a060; font-size: 10px;")
        else:
            self._classes_label.setStyleSheet("color: #a06060; font-size: 10px;")

        # Transitions
        self._transitions_label.setText(
            f"Legal transitions: {reachability.total_legal_edges}/{reachability.total_possible_edges}"
        )

        # Connectivity percentage
        if reachability.total_possible_edges > 0:
            connectivity = reachability.total_legal_edges / reachability.total_possible_edges * 100
            self._escape_label.setText(f"Connectivity: {connectivity:.1f}%")

            if connectivity >= 95:
                self._escape_label.setStyleSheet("color: #60a060; font-size: 10px;")
            elif connectivity >= 80:
                self._escape_label.setStyleSheet("color: #a0a060; font-size: 10px;")
            else:
                self._escape_label.setStyleSheet("color: #a06060; font-size: 10px;")
