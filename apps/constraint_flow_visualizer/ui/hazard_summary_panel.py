"""
Hazard Summary Panel - Shows forbidden transition status.

Per C109: 17 forbidden transitions in 5 failure classes.
Distinguishes atomic (always active) vs decomposable (AZC-tunable).
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
)
from PyQt5.QtCore import Qt

from core.reachability_computer import HazardStatus


class HazardSummaryPanel(QFrame):
    """
    Sidebar showing hazard class status.

    Per C109: 5 failure classes with different percentages:
    - PHASE_ORDERING: 41%
    - COMPOSITION_JUMP: 24%
    - CONTAINMENT_TIMING: 24%
    - RATE_MISMATCH: 6%
    - ENERGY_OVERSHOOT: 6%
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Build the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header
        header = QLabel("HAZARD STATUS")
        header.setStyleSheet("color: #a0b0c0; font-weight: bold; font-size: 11px;")
        header.setToolTip(
            "Per C109: 17 forbidden transitions in 5 failure classes.\n"
            "Atomic hazards (7,9,23) are always active.\n"
            "Decomposable hazards are AZC-tunable."
        )
        layout.addWidget(header)

        # Failure class rows
        self._class_rows = {}
        failure_classes = [
            ("PHASE_ORDERING", 7, "41% - Material in wrong phase location"),
            ("COMPOSITION_JUMP", 4, "24% - Impure fractions passing"),
            ("CONTAINMENT", 4, "24% - Overflow/pressure events"),
            ("RATE_MISMATCH", 1, "6% - Flow imbalance"),
            ("ENERGY_OVERSHOOT", 1, "6% - Thermal damage"),
        ]

        for cls_name, total, tooltip in failure_classes:
            row = self._create_class_row(cls_name, total, tooltip)
            layout.addLayout(row)
            self._class_rows[cls_name] = row

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #3a4a5a;")
        layout.addWidget(sep)

        # Atomic vs Decomposable summary
        self._atomic_label = QLabel("Atomic: 3 (always)")
        self._atomic_label.setStyleSheet("color: #c07070; font-size: 10px;")
        self._atomic_label.setToolTip("Classes 7, 9, 23 - cannot be suppressed by AZC")
        layout.addWidget(self._atomic_label)

        self._decomp_label = QLabel("Decomposable: 6/6")
        self._decomp_label.setStyleSheet("color: #70a070; font-size: 10px;")
        self._decomp_label.setToolTip("AZC-tunable via MIDDLE availability")
        layout.addWidget(self._decomp_label)

        layout.addStretch()

    def _create_class_row(self, name: str, total: int, tooltip: str):
        """Create a row for a failure class."""
        row = QHBoxLayout()
        row.setSpacing(4)

        # Short name
        short_name = name.replace("_", " ").title()
        if len(short_name) > 12:
            short_name = name[:10] + ".."

        label = QLabel(short_name)
        label.setStyleSheet("color: #8090a0; font-size: 9px;")
        label.setToolTip(tooltip)
        label.setFixedWidth(80)
        row.addWidget(label)

        # Progress-style indicator
        value_label = QLabel(f"{total}/{total}")
        value_label.setStyleSheet("color: #60a060; font-size: 9px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignRight)
        value_label.setProperty("name", name)
        value_label.setProperty("total", total)
        row.addWidget(value_label)

        return row

    def update_status(self, status: HazardStatus):
        """
        Update display with current hazard status.

        Args:
            status: HazardStatus from reachability computer
        """
        # Update failure class rows
        for cls_name, row in self._class_rows.items():
            # Find the value label in the row
            for i in range(row.count()):
                item = row.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, QLabel) and widget.property("name") == cls_name:
                        total = widget.property("total") or status.total_by_class.get(cls_name, 0)
                        # Map to status keys
                        status_key = cls_name
                        if cls_name == "CONTAINMENT":
                            status_key = "CONTAINMENT_TIMING"
                        active = status.active_by_class.get(status_key, total)

                        widget.setText(f"{active}/{total}")

                        # Color based on suppression
                        if active == total:
                            widget.setStyleSheet("color: #60a060; font-size: 9px; font-weight: bold;")
                        elif active == 0:
                            widget.setStyleSheet("color: #a06060; font-size: 9px; font-weight: bold;")
                        else:
                            widget.setStyleSheet("color: #a0a060; font-size: 9px; font-weight: bold;")

        # Update summary labels
        self._atomic_label.setText(f"Atomic: {status.atomic_active} (always)")
        self._decomp_label.setText(
            f"Decomposable: {status.decomposable_active}/{status.decomposable_total}"
        )

        if status.decomposable_active < status.decomposable_total:
            suppressed = status.decomposable_total - status.decomposable_active
            self._decomp_label.setText(
                f"Decomposable: {status.decomposable_active}/{status.decomposable_total} "
                f"({suppressed} suppressed)"
            )
