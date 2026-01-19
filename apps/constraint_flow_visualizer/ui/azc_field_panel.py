"""
AZC Field Panel - Zone-Indexed Legality Field Visualization.

Displays AZC as a legality field with zone progression,
showing how option space contracts with position.

Per expert guidance:
> AZC must feel like a legality field, not a checklist.
> Layered zones (C → P → R → S) as spatial depth.
> Transparency/opacity decay with zone progression.
> "Option space contracts with position. Nothing is selected."
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QWidget, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient

from core.azc_projection import (
    ProjectionSummary, AZCProjectionResult, ZoneStatus, ZONES
)


# Zone colors (gradient from bright to dim)
ZONE_COLORS = {
    'C': '#4a8a6a',    # Bright green - full availability
    'P': '#4a7a6a',    # Slightly dimmer
    'R1': '#5a7a6a',   # Fading
    'R2': '#6a6a5a',   # More fading
    'R3': '#6a5a4a',   # Sparse
    'S': '#5a4a4a',    # Heavy restriction (dim red)
}

# Status colors
STATUS_COLORS = {
    ZoneStatus.AVAILABLE: '#4a8a6a',
    ZoneStatus.FADING: '#7a7a5a',
    ZoneStatus.UNAVAILABLE: '#5a3a3a',
}


class ZoneBar(QFrame):
    """A single zone indicator in the field progression."""

    def __init__(self, zone: str, parent=None):
        super().__init__(parent)
        self.zone = zone
        self._status = ZoneStatus.AVAILABLE

        self.setFixedSize(60, 40)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self.zone_label = QLabel(self.zone)
        self.zone_label.setAlignment(Qt.AlignCenter)
        self.zone_label.setStyleSheet(
            "font-weight: bold; color: #e0d8c8; font-size: 11px;"
        )
        layout.addWidget(self.zone_label)

        self.status_label = QLabel("full")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 8px; color: #a0b0c0;"
        )
        layout.addWidget(self.status_label)

        self._update_style()

    def _update_style(self):
        color = STATUS_COLORS.get(self._status, STATUS_COLORS[ZoneStatus.AVAILABLE])
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 1px solid #3a4a5a;
                border-radius: 4px;
            }}
        """)

        # Update status text
        status_text = {
            ZoneStatus.AVAILABLE: "full",
            ZoneStatus.FADING: "fading",
            ZoneStatus.UNAVAILABLE: "locked",
        }
        self.status_label.setText(status_text.get(self._status, ""))

    def set_status(self, status: ZoneStatus):
        if self._status != status:
            self._status = status
            self._update_style()


class ZoneProgression(QFrame):
    """Shows the C → P → R1 → R2 → R3 → S zone progression."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.zone_bars = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        for i, zone in enumerate(ZONES):
            bar = ZoneBar(zone)
            self.zone_bars[zone] = bar
            layout.addWidget(bar)

            # Add arrow between zones (except after last)
            if i < len(ZONES) - 1:
                arrow = QLabel("→")
                arrow.setStyleSheet("color: #5a6a7a; font-size: 14px;")
                layout.addWidget(arrow)

    def update_from_projection(self, projection: AZCProjectionResult):
        """Update zone bars from a projection result."""
        for zone in ZONES:
            status = projection.get_zone_status(zone)
            self.zone_bars[zone].set_status(status)

    def reset(self):
        """Reset all zones to available."""
        for bar in self.zone_bars.values():
            bar.set_status(ZoneStatus.AVAILABLE)


class FolioReachabilityBar(QFrame):
    """Shows reachability for a single AZC folio across zones."""

    def __init__(self, folio: str, parent=None):
        super().__init__(parent)
        self.folio = folio
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        # Folio name
        self.folio_label = QLabel(self.folio)
        self.folio_label.setFixedWidth(50)
        self.folio_label.setStyleSheet("color: #b0c0d0; font-size: 10px;")
        layout.addWidget(self.folio_label)

        # Zone bar (visual progress)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(12)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1a2535;
                border: 1px solid #2a3a4a;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #4a8a6a;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress, 1)

        # Reachability summary
        self.summary_label = QLabel("(fully reachable)")
        self.summary_label.setStyleSheet("color: #8090a0; font-size: 9px;")
        self.summary_label.setFixedWidth(120)
        layout.addWidget(self.summary_label)

    def update_from_projection(self, projection: AZCProjectionResult):
        """Update bar from projection result."""
        # Count reachable zones
        reachable_count = sum(
            1 for zone in ZONES
            if projection.get_zone_status(zone) == ZoneStatus.AVAILABLE
        )
        fading_count = sum(
            1 for zone in ZONES
            if projection.get_zone_status(zone) == ZoneStatus.FADING
        )

        # Calculate percentage (available = 100%, fading = 50%, unavailable = 0%)
        pct = (reachable_count * 100 + fading_count * 50) // len(ZONES)
        self.progress.setValue(pct)

        # Update color based on reachability
        if reachable_count == len(ZONES):
            color = "#4a8a6a"
            summary = "fully reachable"
        elif reachable_count > 0:
            color = "#7a7a5a"
            through = projection.reachable_through_zone or "partial"
            summary = f"reachable through {through}"
        else:
            color = "#5a3a3a"
            summary = "unreachable"

        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1a2535;
                border: 1px solid #2a3a4a;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)
        self.summary_label.setText(f"({summary})")


class AZCFieldPanel(QFrame):
    """
    Panel showing AZC legality field visualization.

    Displays zone progression and per-folio reachability,
    emphasizing the field-like nature of AZC constraints.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.folio_bars = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header
        header = QLabel("AZC LEGALITY FIELD")
        header.setObjectName("header")
        layout.addWidget(header)

        # Zone progression display
        self.zone_progression = ZoneProgression()
        layout.addWidget(self.zone_progression)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #2a3a4a;")
        layout.addWidget(divider)

        # Per-folio reachability (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        folio_widget = QWidget()
        self.folio_layout = QVBoxLayout(folio_widget)
        self.folio_layout.setContentsMargins(0, 0, 0, 0)
        self.folio_layout.setSpacing(2)

        # Will be populated when projection is set
        self.folio_layout.addStretch()

        scroll.setWidget(folio_widget)
        layout.addWidget(scroll, 1)

        # Footer message
        self.footer = QLabel(
            "Option space contracts with position. Nothing is selected."
        )
        self.footer.setStyleSheet(
            "color: #8090a0; font-style: italic; margin-top: 4px;"
        )
        self.footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer)

    @pyqtSlot(object)
    def update_projection(self, projection_summary: ProjectionSummary):
        """Update the panel from a projection summary."""
        # Clear existing folio bars
        for bar in self.folio_bars.values():
            bar.deleteLater()
        self.folio_bars.clear()

        # Remove stretch
        while self.folio_layout.count() > 0:
            item = self.folio_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Update zone progression from first folio (representative)
        if projection_summary.results:
            first_folio = list(projection_summary.results.keys())[0]
            first_projection = projection_summary.results[first_folio]
            self.zone_progression.update_from_projection(first_projection)

        # Add folio bars (limit to first 10 for MVP)
        shown_folios = list(projection_summary.results.items())[:10]

        for folio, projection in shown_folios:
            bar = FolioReachabilityBar(folio)
            bar.update_from_projection(projection)
            self.folio_layout.addWidget(bar)
            self.folio_bars[folio] = bar

        self.folio_layout.addStretch()

        # Update footer with summary
        fully = len(projection_summary.fully_reachable_folios)
        partial = len(projection_summary.partially_reachable_folios)
        unreachable = len(projection_summary.unreachable_folios)
        total = len(projection_summary.results)

        self.footer.setText(
            f"{fully} fully reachable | {partial} conditional | "
            f"{unreachable} unreachable (of {total} AZC folios)"
        )

    def reset(self):
        """Reset to initial state."""
        self.zone_progression.reset()

        for bar in self.folio_bars.values():
            bar.deleteLater()
        self.folio_bars.clear()

        while self.folio_layout.count() > 0:
            item = self.folio_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.folio_layout.addStretch()

        self.footer.setText(
            "Option space contracts with position. Nothing is selected."
        )
