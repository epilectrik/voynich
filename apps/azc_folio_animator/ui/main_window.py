"""
Main window for AZC Folio Animator v2 - Token-Centric Multi-Folio Activation.

PARADIGM SHIFT:
- OLD: User selects ONE AZC folio, views lines through that folio's lens.
- NEW: User clicks a token, system shows ALL AZC folios where that token lives.

Core principle: "Click a token, see everywhere it lives."
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QStatusBar
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.azc_folio_animator.core.folio_loader import FolioLoader, TokenData
from apps.azc_folio_animator.core.azc_folio_model import AZCFolioRegistry
from apps.azc_folio_animator.core.token_classifier import TokenClassifier
from apps.azc_folio_animator.core.corpus_stats import CorpusStatsLoader
from apps.azc_folio_animator.ui.manuscript_view import ManuscriptView
from apps.azc_folio_animator.ui.a_text_strip import ATextStrip
from apps.azc_folio_animator.ui.azc_panel import AZCPanel
from apps.azc_folio_animator.ui.token_info_panel import TokenInfoPanel
from typing import List


class MainWindow(QMainWindow):
    """
    Main window for AZC Folio Animator v2.

    Token-centric exploration: click a token to see all AZC folios
    where it appears, with positions illuminated.
    """

    def __init__(self, voynich_font: QFont):
        super().__init__()
        self.voynich_font = voynich_font
        self.setWindowTitle("Currier A Explorer - Token Classification System")
        self.setMinimumSize(1200, 800)

        # Apply dark theme
        self._apply_theme()

        # Initialize data loaders
        self.folio_loader = FolioLoader()
        self.folio_loader.load()

        # Initialize corpus statistics (for frequency tiers)
        self.corpus_stats = CorpusStatsLoader(self.folio_loader)
        self.corpus_stats.load()

        # Initialize registry and classifier
        self.azc_registry = AZCFolioRegistry(self.folio_loader)
        self.token_classifier = TokenClassifier(self.azc_registry)

        # Current state
        self.current_line_tokens: List[TokenData] = []
        self.current_line_idx: int = -1
        self.selected_token: str = None

        # Build UI
        self._build_ui()

        # Connect signals
        self._connect_signals()

        # Update status
        self._update_status()

    def _apply_theme(self):
        """Apply dark theme appropriate for constraint visualization."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(15, 22, 35))
        palette.setColor(QPalette.WindowText, QColor(176, 196, 222))
        palette.setColor(QPalette.Base, QColor(10, 18, 30))
        palette.setColor(QPalette.AlternateBase, QColor(20, 28, 40))
        palette.setColor(QPalette.Text, QColor(176, 196, 222))
        palette.setColor(QPalette.Button, QColor(25, 38, 55))
        palette.setColor(QPalette.ButtonText, QColor(176, 196, 222))
        palette.setColor(QPalette.Highlight, QColor(0, 170, 204))
        palette.setColor(QPalette.HighlightedText, QColor(10, 18, 30))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f1623;
            }
            QSplitter::handle {
                background-color: #1a2a3a;
                width: 3px;
            }
            QLabel {
                color: #b0c4de;
            }
            QStatusBar {
                background-color: #121a25;
                color: #7a8a9a;
                border-top: 1px solid #2a3a4a;
            }
        """)

    def _build_ui(self):
        """Build the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Top bar: title and stats (no folio selector)
        top_bar = self._build_top_bar()
        main_layout.addWidget(top_bar)

        # A-text strip: horizontal token display
        self.a_text_strip = ATextStrip(
            self.voynich_font, self.token_classifier, self.corpus_stats
        )
        main_layout.addWidget(self.a_text_strip)

        # Token info panel: detailed breakdown of selected token
        self.token_info_panel = TokenInfoPanel(
            self.voynich_font, self.token_classifier, self.corpus_stats
        )
        main_layout.addWidget(self.token_info_panel)

        # Main content: splitter with manuscript view and AZC panel
        self.splitter = QSplitter(Qt.Horizontal)

        # Left: Line selector (ManuscriptView) - shows all Currier A folios
        self.manuscript_view = ManuscriptView(self.voynich_font)
        self.splitter.addWidget(self.manuscript_view)

        # Right: AZC Panel (dynamic multi-folio display)
        self.azc_panel = AZCPanel(self.voynich_font)
        self.splitter.addWidget(self.azc_panel)

        self.splitter.setSizes([300, 700])
        main_layout.addWidget(self.splitter, stretch=1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _build_top_bar(self) -> QWidget:
        """Build the top bar with title and stats."""
        bar = QWidget()
        bar.setStyleSheet("background: #121a25; border-radius: 4px;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(15, 8, 15, 8)

        # Title
        title = QLabel("AZC Animator v2")
        title.setStyleSheet("color: #00aacc; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Token-Centric Exploration")
        subtitle.setStyleSheet("color: #666; font-size: 12px; font-style: italic;")
        layout.addWidget(subtitle)

        layout.addStretch()

        # Stats
        zodiac_count = self.azc_registry.zodiac_count
        ac_count = self.azc_registry.ac_count
        total = self.azc_registry.folio_count

        stats = QLabel(f"AZC Folios: {total} ({zodiac_count} Zodiac, {ac_count} A/C)")
        stats.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(stats)

        return bar

    def _connect_signals(self):
        """Connect all signals."""
        # Line selection populates the A-text strip
        self.manuscript_view.line_selected.connect(self._on_line_selected)

        # Token click triggers AZC panel update
        self.a_text_strip.token_clicked.connect(self._on_token_clicked)

    def _on_line_selected(self, line_idx: int, tokens: list):
        """Handle line selection from manuscript view."""
        self.current_line_idx = line_idx
        self.current_line_tokens = tokens
        self.selected_token = None

        # Populate A-text strip with tokens
        self.a_text_strip.set_tokens(tokens)
        self.a_text_strip.clear_selection()

        # Clear panels (waiting for token click)
        self.azc_panel.clear()
        self.token_info_panel.clear()

        self._update_status()

    def _on_token_clicked(self, token_text: str):
        """Handle token click from A-text strip."""
        self.selected_token = token_text

        # Update token info panel with detailed analysis
        self.token_info_panel.set_token(token_text)

        # Get all folios containing this token
        activated_folios = self.azc_registry.get_activated_folios(token_text)

        # Display in AZC panel
        self.azc_panel.show_activated_folios(activated_folios, token_text)

        self._update_status()

    def _update_status(self):
        """Update status bar."""
        parts = []

        # Line info
        if self.current_line_idx >= 0:
            parts.append(f"Line {self.current_line_idx + 1}")
            parts.append(f"{len(self.current_line_tokens)} tokens")

        # Token info
        if self.selected_token:
            folio_count = self.token_classifier.get_folio_count(self.selected_token)
            token_type = self.token_classifier.classify(self.selected_token)
            parts.append(f"Token: '{self.selected_token}'")
            parts.append(f"in {folio_count} folio(s)")
            parts.append(f"[{token_type.name}]")

        if parts:
            self.status.showMessage(" | ".join(parts))
        else:
            self.status.showMessage("Select a line to begin")
