"""
Main Window for Constraint Flow Visualizer.

Sets up the overall layout with dark theme and contains all panels.
Wires up the A→AZC→B pipeline flow.
"""

from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSplitter, QStatusBar, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase

from .a_entry_panel import AEntryPanel
from .baseline_grammar_panel import BaselineGrammarPanel
from .azc_field_panel import AZCFieldPanel
from .b_reachability_panel import BReachabilityPanel
from .legality_dashboard import LegalityDashboard

from core.constraint_bundle import ConstraintBundle, BundleType, compute_compatible_folios
from core.azc_projection import project_bundle
from core.reachability_engine import compute_reachability
from core.data_loader import get_data_store


# =============================================================================
# STYLING
# =============================================================================

DARK_THEME = """
QMainWindow {
    background-color: #0f1623;
}
QWidget {
    background-color: #0f1623;
    color: #b0c4de;
    font-family: 'Segoe UI', sans-serif;
    font-size: 11px;
}
QFrame {
    background-color: #151d2e;
    border: 1px solid #2a3a4a;
    border-radius: 4px;
}
QLabel {
    background-color: transparent;
    border: none;
}
QLabel#header {
    font-size: 12px;
    font-weight: bold;
    color: #e0d8c8;
    padding: 4px;
}
QLabel#status {
    font-size: 10px;
    color: #8090a0;
}
QLineEdit {
    background-color: #1a2535;
    border: 1px solid #3a4a5a;
    border-radius: 3px;
    padding: 4px 8px;
    color: #e0d8c8;
}
QLineEdit:focus {
    border-color: #5080a0;
}
QListWidget {
    background-color: #1a2535;
    border: 1px solid #2a3a4a;
    border-radius: 3px;
}
QListWidget::item {
    padding: 4px;
}
QListWidget::item:selected {
    background-color: #2a4a6a;
}
QListWidget::item:hover {
    background-color: #1f3045;
}
QSplitter::handle {
    background-color: #2a3a4a;
}
QStatusBar {
    background-color: #0a1018;
    color: #8090a0;
    border-top: 1px solid #2a3a4a;
}
QComboBox {
    background-color: #1a2535;
    border: 1px solid #3a4a5a;
    border-radius: 3px;
    padding: 4px 8px;
    color: #e0d8c8;
}
QComboBox:hover {
    border-color: #5080a0;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #1a2535;
    border: 1px solid #3a4a5a;
    selection-background-color: #2a4a6a;
}
QGroupBox {
    border: 1px solid #2a3a4a;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 4px;
    color: #b0c4de;
}
QTabWidget::pane {
    border: 1px solid #2a3a4a;
    background-color: #151d2e;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #1a2535;
    color: #8090a0;
    padding: 8px 16px;
    border: 1px solid #2a3a4a;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #151d2e;
    color: #e0d8c8;
}
QTabBar::tab:hover {
    background-color: #1f3045;
}
"""


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Constraint Flow Visualizer")
        self.setMinimumSize(1200, 800)

        # Load Voynich font
        self._load_voynich_font()

        # Apply dark theme
        self.setStyleSheet(DARK_THEME)

        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Title bar
        title_label = QLabel("Constraint Flow Visualizer")
        title_label.setObjectName("header")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # Subtitle
        subtitle = QLabel(
            "A → AZC → B Pipeline Visualization | "
            "Grammar unchanged. Option space contracts."
        )
        subtitle.setObjectName("status")
        layout.addWidget(subtitle)

        # Main content area: horizontal splitter with sidebar + tabs
        main_splitter = QSplitter(Qt.Horizontal)

        # Left sidebar: A Entry panel (always visible for input)
        self.a_entry_panel = AEntryPanel(self.voynich_font)
        main_splitter.addWidget(self.a_entry_panel)

        # Right side: Tabs for output panels
        self.tabs = QTabWidget()

        # Grammar panel: Baseline vs Conditioned
        self.grammar_panel = BaselineGrammarPanel()
        self.tabs.addTab(self.grammar_panel, "Grammar")

        # AZC field section
        self.azc_panel = AZCFieldPanel()
        self.tabs.addTab(self.azc_panel, "AZC Field")

        # B Reachability
        self.b_panel = BReachabilityPanel()
        self.tabs.addTab(self.b_panel, "B Reachability")

        # Legality Dashboard - Shows what CHANGES between A records
        self.legality_dashboard = LegalityDashboard()
        self.tabs.addTab(self.legality_dashboard, "Legality")

        main_splitter.addWidget(self.tabs)

        # Set initial sizes (sidebar ~280px, tabs get rest)
        main_splitter.setSizes([280, 920])

        layout.addWidget(main_splitter, 1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(
            "Ready. Select a Currier A record to visualize constraint flow."
        )

        # Wire up connections
        self._connect_signals()

    def _load_voynich_font(self):
        """Load the Voynich EVA font."""
        font_path = Path(__file__).parent.parent / "fonts" / "VoynichEVA.ttf"
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id >= 0:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    self.voynich_font = QFont(families[0], 14)
                    return
        # Fallback
        self.voynich_font = QFont("Courier New", 14)

    def _connect_signals(self):
        """Wire up signal/slot connections for the pipeline."""
        # When a token is selected, process the full pipeline (Stage 1: ambient legality)
        self.a_entry_panel.token_selected.connect(self._on_token_selected)

        # When a B folio is clicked, show Stage 2 compilation (program-specific view)
        self.b_panel.folio_selected.connect(self._on_b_folio_selected)

    def _on_token_selected(self, bundle: ConstraintBundle):
        """
        Handle record selection - run the full A→AZC→B pipeline.

        Per C233, C473, C481 - the RECORD is the unit that interacts
        with AZC. The bundle contains ALL MIDDLEs from all tokens.

        This is the main flow:
        1. Display constraint bundle (record-level)
        2. Project through AZC (uses full MIDDLE set)
        3. Compute reachability
        4. Update all panels
        """
        # Project through AZC
        projection = project_bundle(bundle)

        # Compute reachability
        reachability = compute_reachability(projection)

        # Update panels
        self.grammar_panel.update_grammar(reachability)
        self.azc_panel.update_projection(projection)
        self.b_panel.update_reachability(reachability)
        self.legality_dashboard.update_from_bundle(bundle)

        # Determine bundle type for status message
        data_store = get_data_store()
        if bundle.azc_active:
            compatible = compute_compatible_folios(frozenset(bundle.azc_active), data_store)
            if compatible:
                bundle_type_str = "ACTIVATING"
            else:
                bundle_type_str = "BLOCKED"
        else:
            bundle_type_str = "NEUTRAL"

        # Update status bar
        gs = reachability.grammar_state
        self.status_bar.showMessage(
            f"[{bundle_type_str}] {gs.n_reachable}/49 classes reachable, "
            f"{gs.n_pruned} pruned. Grammar unchanged."
        )

    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_bar.showMessage(message)

    def _on_b_folio_selected(self, folio_id: str, folio_result):
        """
        Handle B folio selection from B Reachability panel.

        Note: The Legality Dashboard has its own B folio selector.
        This handler updates the status bar when folio is selected from B panel.
        """
        # Update status bar
        data_store = get_data_store()
        regime = data_store.regime_assignments.get(folio_id, "")
        regime_str = f" ({regime})" if regime else ""

        n_missing = len(folio_result.missing_classes) if folio_result.missing_classes else 0
        status_str = folio_result.status.name if hasattr(folio_result.status, 'name') else str(folio_result.status)

        self.status_bar.showMessage(
            f"Selected: {folio_id}{regime_str} | Status: {status_str} | "
            f"Missing: {n_missing} classes"
        )


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
