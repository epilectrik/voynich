"""
Record Cycle Control - Simplified controls for line-by-line viewing.

Just navigate between lines - no animation or filtering.
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal


class RecordCycleControl(QWidget):
    """
    Simplified control widget for navigating lines.

    Signals:
        next_line(): User wants to move to next line
        reset_requested(): User wants to clear current view
        reset_view_requested(): User wants to reset zoom/pan
    """

    next_line = pyqtSignal()
    reset_requested = pyqtSignal()
    reset_view_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_line = 0
        self._line_count = 0

        self._build_ui()

    def _build_ui(self):
        """Build the simplified control UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 5)
        layout.setSpacing(15)

        # Line indicator
        line_group = QWidget()
        line_layout = QHBoxLayout(line_group)
        line_layout.setContentsMargins(0, 0, 0, 0)
        line_layout.setSpacing(5)

        line_label = QLabel("Line:")
        line_label.setStyleSheet("color: #7a8a9a;")
        line_layout.addWidget(line_label)

        self.line_display = QLabel("—/—")
        self.line_display.setStyleSheet("""
            color: #b0c4de;
            min-width: 60px;
        """)
        line_layout.addWidget(self.line_display)

        layout.addWidget(line_group)

        # Next line button
        self.next_line_btn = QPushButton("Next Line")
        self.next_line_btn.setFixedWidth(90)
        self.next_line_btn.clicked.connect(self._on_next_line_clicked)
        self.next_line_btn.setEnabled(False)
        layout.addWidget(self.next_line_btn)

        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setFixedWidth(70)
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        layout.addWidget(self.reset_btn)

        # Reset View button
        self.reset_view_btn = QPushButton("Fit View")
        self.reset_view_btn.setFixedWidth(70)
        self.reset_view_btn.setToolTip("Reset zoom and pan (scroll to zoom, drag to pan)")
        self.reset_view_btn.clicked.connect(self._on_reset_view_clicked)
        layout.addWidget(self.reset_view_btn)

        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Status
        self.status_label = QLabel("Select a line to view")
        self.status_label.setStyleSheet("color: #5a6a7a; font-style: italic;")
        layout.addWidget(self.status_label)

    def set_line_count(self, count: int):
        """Set total number of lines."""
        self._line_count = count
        self._update_displays()

    def set_current_line(self, idx: int):
        """Set current line index."""
        self._current_line = idx
        self._update_displays()
        self.status_label.setText(f"Viewing line {idx + 1}")

    def bundle_injected(self):
        """Called when a bundle is injected into diagram."""
        self.status_label.setText(f"Line {self._current_line + 1} - {self._line_count} tokens")
        self._update_displays()

    def _on_next_line_clicked(self):
        """Handle next line button."""
        self.next_line.emit()

    def _on_reset_clicked(self):
        """Handle reset button."""
        self.reset_requested.emit()

    def _on_reset_view_clicked(self):
        """Handle reset view button."""
        self.reset_view_requested.emit()

    def _update_displays(self):
        """Update line counter display."""
        if self._line_count > 0:
            self.line_display.setText(f"{self._current_line + 1}/{self._line_count}")
            self.next_line_btn.setEnabled(self._current_line < self._line_count - 1)
        else:
            self.line_display.setText("—/—")
            self.next_line_btn.setEnabled(False)

    def reset(self):
        """Reset to initial state."""
        self._current_line = 0
        self.next_line_btn.setEnabled(False)
        self.status_label.setText("Select a line to view")
        self._update_displays()
