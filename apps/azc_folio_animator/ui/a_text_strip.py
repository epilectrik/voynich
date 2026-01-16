"""
A-Text Strip - Horizontal display of Currier A line tokens.

Shows tokens from the currently selected line with styling based on
their AZC distribution (localized/distributed/structural).

Clicking a token emits a signal that triggers the AZC panel to show
all folios containing that token.
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea, QFrame, QLabel,
    QMenu, QApplication
)
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.azc_folio_animator.core.folio_loader import TokenData
from apps.azc_folio_animator.core.token_classifier import TokenClassifier, TokenType
from apps.azc_folio_animator.core.token_analyzer import TokenAnalyzer, OperationalDomain, TokenSystem
from apps.azc_folio_animator.core.token_system_classifier import SYSTEM_COLORS
from apps.azc_folio_animator.core.corpus_stats import CorpusStatsLoader


class TokenWidget(QFrame):
    """Single clickable token in the A-text strip."""

    clicked = pyqtSignal(str)  # Emits token text

    # Domain colors for left border accent
    DOMAIN_COLORS = {
        OperationalDomain.ENERGY_OPERATOR: "#ff8844",    # Orange - energy/heat
        OperationalDomain.CORE_CONTROL: "#44aaff",       # Blue - control/structure
        OperationalDomain.FREQUENT_OPERATOR: "#44dd88",  # Green - routine
        OperationalDomain.REGISTRY_REFERENCE: "#aa88ff", # Purple - reference
        OperationalDomain.UNCLASSIFIED: "#555555",       # Gray - unknown
    }

    def __init__(self, token: TokenData, token_type: TokenType,
                 folio_count: int, domain: OperationalDomain,
                 token_system: TokenSystem, font: QFont):
        super().__init__()
        self.token = token
        self.token_type = token_type
        self.folio_count = folio_count
        self.domain = domain
        self.token_system = token_system
        self._selected = False
        self.badge = None
        self.system_dot = None

        self._setup_ui(font)
        self._apply_style()

    def _setup_ui(self, font: QFont):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        # System dot badge (small colored circle showing token system)
        system_color = SYSTEM_COLORS.get(self.token_system, "#666666")
        self.system_dot = QLabel("●")
        self.system_dot.setStyleSheet(f"color: {system_color}; font-size: 8px;")
        self.system_dot.setFixedWidth(12)
        layout.addWidget(self.system_dot)

        self.label = QLabel(self.token.text)
        self.label.setFont(font)
        layout.addWidget(self.label)

        # Small badge showing folio count for multi-folio tokens
        if self.folio_count > 1:
            self.badge = QLabel(f"({self.folio_count})")
            badge_font = QFont(font)
            badge_font.setPointSize(max(6, font.pointSize() - 4))
            self.badge.setFont(badge_font)
            layout.addWidget(self.badge)

        self.setCursor(QCursor(Qt.PointingHandCursor))

    def _apply_style(self):
        """Apply styling based on token type, domain, and selection state."""
        domain_color = self.DOMAIN_COLORS.get(self.domain, "#555555")

        if self._selected:
            self.setStyleSheet(f"""
                TokenWidget {{
                    background: #00aacc;
                    border-radius: 4px;
                    border: 2px solid #00ddff;
                    border-left: 4px solid {domain_color};
                }}
            """)
            self.label.setStyleSheet("color: #ffffff; font-weight: bold;")
            if self.badge:
                self.badge.setStyleSheet("color: #ffffff;")

        elif self.token_type == TokenType.NO_AZC_MAPPING:
            # Red-tinted - token's MIDDLE not in AZC vocabulary
            self.setStyleSheet(f"""
                TokenWidget {{
                    background: #2a1515;
                    border-radius: 4px;
                    border: 1px solid #4a2020;
                    border-left: 3px solid {domain_color};
                }}
                TokenWidget:hover {{ border-color: #662222; border-left: 3px solid {domain_color}; }}
            """)
            self.label.setStyleSheet("color: #885555;")
            if self.badge:
                self.badge.setStyleSheet("color: #664444;")

        elif self.token_type == TokenType.STRUCTURAL:
            # Gray - structural/grammar tokens
            self.setStyleSheet(f"""
                TokenWidget {{
                    background: #1a1a1a;
                    border-radius: 4px;
                    border: 1px solid #333;
                    border-left: 3px solid {domain_color};
                }}
                TokenWidget:hover {{ border-color: #555; border-left: 3px solid {domain_color}; }}
            """)
            self.label.setStyleSheet("color: #555;")
            if self.badge:
                self.badge.setStyleSheet("color: #444;")

        elif self.token_type == TokenType.DISTRIBUTED:
            # Muted - distributed tokens (4-9 folios)
            self.setStyleSheet(f"""
                TokenWidget {{
                    background: #252a35;
                    border-radius: 4px;
                    border: 1px solid #3a4050;
                    border-left: 3px solid {domain_color};
                }}
                TokenWidget:hover {{ border-color: #00aacc; border-left: 3px solid {domain_color}; }}
            """)
            self.label.setStyleSheet("color: #8a9aaa;")
            if self.badge:
                self.badge.setStyleSheet("color: #666;")

        else:  # LOCALIZED - bright, fully interactive
            self.setStyleSheet(f"""
                TokenWidget {{
                    background: #1a3a4a;
                    border-radius: 4px;
                    border: 1px solid #2a5060;
                    border-left: 3px solid {domain_color};
                }}
                TokenWidget:hover {{ border-color: #00aacc; border-left: 3px solid {domain_color}; }}
            """)
            self.label.setStyleSheet("color: #b0c4de;")
            if self.badge:
                self.badge.setStyleSheet("color: #666;")

    def set_selected(self, selected: bool):
        """Set selection state."""
        self._selected = selected
        self._apply_style()

    def mousePressEvent(self, event):
        """Handle click - emit token text."""
        self.clicked.emit(self.token.text)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        """Show context menu with copy option."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a2635;
                color: #b0c4de;
                border: 1px solid #2a4050;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item { padding: 6px 20px; }
            QMenu::item:selected { background-color: #2a3a4a; }
        """)

        copy_action = menu.addAction(f"Copy: {self.token.text}")
        copy_action.triggered.connect(lambda: self._copy_to_clipboard(self.token.text))

        # Show folio count info
        menu.addSeparator()
        info = menu.addAction(f"In {self.folio_count} AZC folio(s)")
        info.setEnabled(False)

        menu.exec_(event.globalPos())

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)


class ATextStrip(QWidget):
    """
    Horizontal strip showing Currier A line tokens.

    Tokens are styled by their AZC distribution:
    - Localized (1-3 folios): Bright, fully interactive
    - Distributed (4-9 folios): Muted
    - Structural (10+ folios): Grayed out

    Clicking a token emits token_clicked signal with the token text.
    """

    token_clicked = pyqtSignal(str)  # Emits token text

    def __init__(self, voynich_font: QFont, classifier: TokenClassifier,
                 corpus_stats: Optional[CorpusStatsLoader] = None):
        super().__init__()
        self.voynich_font = voynich_font
        self.classifier = classifier
        self.corpus_stats = corpus_stats
        self.analyzer = TokenAnalyzer(corpus_stats)
        self.token_widgets: List[TokenWidget] = []
        self.selected_token: Optional[str] = None

        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(55)
        self.setStyleSheet("background: #121a25; border-bottom: 1px solid #2a3a4a;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(0)

        # Label
        label = QLabel("Line:")
        label.setStyleSheet("color: #666; font-size: 11px;")
        label.setFixedWidth(35)
        main_layout.addWidget(label)

        # Scroll area for long lines
        self.scroll = QScrollArea()
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:horizontal {
                height: 8px;
                background: #1a2635;
            }
            QScrollBar::handle:horizontal {
                background: #3a4a5a;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(6)
        self.container_layout.addStretch()

        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

        # Placeholder (shown when no tokens)
        self.placeholder = QLabel("Select a line to view tokens")
        self.placeholder.setStyleSheet("color: #555; font-style: italic;")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setFixedWidth(200)
        main_layout.addWidget(self.placeholder)

    def set_tokens(self, tokens: List[TokenData]):
        """Populate strip with tokens from selected line."""
        self._clear()

        if not tokens:
            self.placeholder.setText("No tokens in line")
            self.placeholder.show()
            self.scroll.hide()
            return

        self.placeholder.hide()
        self.scroll.show()

        for token in tokens:
            token_type = self.classifier.classify(token.text)
            folio_count = self.classifier.get_folio_count(token.text)

            # Get operational domain and token system from analyzer
            analysis = self.analyzer.analyze(token.text)
            domain = analysis.domain
            token_system = analysis.token_system

            widget = TokenWidget(token, token_type, folio_count, domain, token_system, self.voynich_font)
            widget.clicked.connect(self._on_token_clicked)

            self.token_widgets.append(widget)
            # Insert before the stretch
            self.container_layout.insertWidget(
                self.container_layout.count() - 1, widget
            )

    def _on_token_clicked(self, token_text: str):
        """Handle token click."""
        self._update_selection(token_text)
        self.token_clicked.emit(token_text)

    def _update_selection(self, token_text: str):
        """Update which token is selected."""
        self.selected_token = token_text
        for widget in self.token_widgets:
            widget.set_selected(widget.token.text == token_text)

    def clear_selection(self):
        """Clear token selection."""
        self.selected_token = None
        for widget in self.token_widgets:
            widget.set_selected(False)

    def _clear(self):
        """Clear all token widgets."""
        for widget in self.token_widgets:
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
        self.token_widgets.clear()
        self.selected_token = None

    def contextMenuEvent(self, event):
        """Show context menu for copying all tokens in line."""
        if not self.token_widgets:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a2635;
                color: #b0c4de;
                border: 1px solid #2a4050;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item { padding: 6px 20px; }
            QMenu::item:selected { background-color: #2a3a4a; }
        """)

        # Get all tokens as space-separated string
        all_tokens = " ".join(w.token.text for w in self.token_widgets)

        copy_all = menu.addAction(f"Copy all ({len(self.token_widgets)} tokens)")
        copy_all.triggered.connect(lambda: self._copy_to_clipboard(all_tokens))

        # Preview (truncated if long)
        menu.addSeparator()
        preview_text = all_tokens[:60] + "..." if len(all_tokens) > 60 else all_tokens
        preview = menu.addAction(preview_text)
        preview.setEnabled(False)

        menu.exec_(event.globalPos())

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
