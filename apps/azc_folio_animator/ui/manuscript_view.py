"""
Manuscript View - Line selector for Currier A bundles.

Shows list of lines from folio. User selects ONE line at a time
to process through the AZC constraint field.

Each line is a constraint bundle (C473, C233).

Includes its own folio selector to choose which Currier A folio to view.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame,
    QListWidget, QListWidgetItem, QHBoxLayout, QComboBox,
    QMenu, QApplication
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import re

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.azc_folio_animator.core.folio_loader import FolioLoader, FolioData, TokenData
from typing import List, Optional


class LineItem(QFrame):
    """A single line entry in the list."""

    clicked = pyqtSignal(int)  # line index

    def __init__(self, line_num: int, line_idx: int, tokens: List[TokenData],
                 font: QFont, parent=None):
        super().__init__(parent)
        self.line_idx = line_idx
        self.line_num = line_num
        self.tokens = tokens
        self._selected = False

        self.setFrameStyle(QFrame.NoFrame)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        # Line number
        num_label = QLabel(f"{line_num:02d}")
        num_label.setStyleSheet("color: #5a6a7a; font-size: 11px; min-width: 20px;")
        layout.addWidget(num_label)

        # Token count indicator
        count_label = QLabel(f"[{len(tokens)}]")
        count_label.setStyleSheet("color: #4a5a6a; font-size: 10px; min-width: 25px;")
        layout.addWidget(count_label)

        # Line text (preview)
        text = " ".join(t.text for t in tokens[:5])
        if len(tokens) > 5:
            text += "..."

        text_label = QLabel(text)
        text_label.setFont(font)
        text_label.setStyleSheet("color: #a0b0c0;")
        layout.addWidget(text_label, stretch=1)

        self._update_style()

    def _update_style(self):
        """Update visual style based on selection."""
        if self._selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1a3040;
                    border-left: 3px solid #00aacc;
                    border-radius: 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border-left: 3px solid transparent;
                }
                QFrame:hover {
                    background-color: #12202a;
                }
            """)

    def set_selected(self, selected: bool):
        """Set selection state."""
        self._selected = selected
        self._update_style()

    def mousePressEvent(self, event):
        """Handle click."""
        self.clicked.emit(self.line_idx)
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

        # Get full line text as ASCII
        full_text = " ".join(t.text for t in self.tokens)

        copy_line = menu.addAction(f"Copy line ({len(self.tokens)} tokens)")
        copy_line.triggered.connect(lambda: self._copy_to_clipboard(full_text))

        # If line is short enough, show preview
        if len(full_text) <= 50:
            menu.addSeparator()
            preview = menu.addAction(full_text)
            preview.setEnabled(False)

        menu.exec_(event.globalPos())

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)


class ManuscriptView(QWidget):
    """
    Line selector showing Currier A bundles from a folio.

    Includes its own folio selector and displays lines as selectable items.
    Selected line becomes the active bundle for AZC processing.

    Signals:
        line_selected(int, list): Line index and list of TokenData
    """

    line_selected = pyqtSignal(int, list)

    def __init__(self, voynich_font: QFont, parent=None):
        super().__init__(parent)
        self.voynich_font = voynich_font
        self.folio_loader = FolioLoader()
        self.folio_loader.load()
        self.current_folio: FolioData = None
        self.line_items: List[LineItem] = []
        self._selected_idx: int = -1

        self._setup_ui()
        self._load_folio_list()

    def _setup_ui(self):
        """Build the UI with folio selector and line list."""
        self.setStyleSheet("background-color: #0a1218;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Folio selector row
        selector_row = QWidget()
        selector_row.setStyleSheet("background: #121a25; border-bottom: 1px solid #2a3a4a;")
        selector_layout = QHBoxLayout(selector_row)
        selector_layout.setContentsMargins(8, 6, 8, 6)

        label = QLabel("Source:")
        label.setStyleSheet("color: #666; font-size: 11px;")
        selector_layout.addWidget(label)

        self.folio_combo = QComboBox()
        self.folio_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a2635;
                color: #b0c4de;
                border: 1px solid #2a4050;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 80px;
            }
            QComboBox:hover { border-color: #00aacc; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #b0c4de;
            }
        """)
        self.folio_combo.currentTextChanged.connect(self._on_folio_changed)
        selector_layout.addWidget(self.folio_combo)

        selector_layout.addStretch()
        main_layout.addWidget(selector_row)

        # Scroll area for lines
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background-color: #0a1218;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #0a1218;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #2a3a4a;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background-color: #3a4a5a; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background-color: #0a1218;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(5, 5, 5, 5)
        self.container_layout.setSpacing(2)

        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

    def _load_folio_list(self):
        """Load list of all Currier A folios."""
        # All Currier A folios - tokens should map to AZC profiles
        folio_ids = self.folio_loader.get_all_folio_ids()

        # Sort by folio number
        def sort_key(fid):
            match = re.match(r'(\d+)([rv]\d*)', fid)
            if match:
                return (int(match.group(1)), match.group(2))
            return (999, fid)

        folio_ids = sorted(folio_ids, key=sort_key)

        self.folio_combo.blockSignals(True)
        self.folio_combo.clear()
        for fid in folio_ids:
            self.folio_combo.addItem(f"f{fid}")
        self.folio_combo.blockSignals(False)

        # Select first folio
        if folio_ids:
            self.folio_combo.setCurrentIndex(0)
            self._load_folio(folio_ids[0])

    def _on_folio_changed(self, text: str):
        """Handle folio selection change."""
        if text:
            folio_id = text.lstrip('f')
            self._load_folio(folio_id)

    def _load_folio(self, folio_id: str):
        """Load a folio and display its lines."""
        folio = self.folio_loader.get_folio(folio_id)
        if folio:
            self.set_folio(folio)

    def set_folio(self, folio: FolioData):
        """Load folio and display lines."""
        self.current_folio = folio
        self._selected_idx = -1

        # Clear existing
        for item in self.line_items:
            item.deleteLater()
        self.line_items.clear()

        # Clear layout
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Header
        header = QLabel(f"Currier A Lines - f{folio.folio_id}")
        header.setStyleSheet("""
            color: #7a8a9a;
            font-size: 11px;
            font-weight: bold;
            padding: 8px 5px;
            border-bottom: 1px solid #1a2a3a;
        """)
        self.container_layout.addWidget(header)

        # Info
        info = QLabel(f"{len(folio.lines)} lines | Select one to process")
        info.setStyleSheet("color: #5a6a7a; font-size: 10px; padding: 4px 5px;")
        self.container_layout.addWidget(info)

        # Add line items
        for idx, line_tokens in enumerate(folio.lines):
            if not line_tokens:
                continue

            line_num = line_tokens[0].line_num
            item = LineItem(line_num, idx, line_tokens, self.voynich_font)
            item.clicked.connect(self._on_line_clicked)
            self.container_layout.addWidget(item)
            self.line_items.append(item)

        self.container_layout.addStretch()

    def _on_line_clicked(self, idx: int):
        """Handle line selection."""
        self.select_line(idx)

    def select_line(self, idx: int):
        """Select a line by index."""
        if idx == self._selected_idx:
            return

        # Deselect previous
        if 0 <= self._selected_idx < len(self.line_items):
            self.line_items[self._selected_idx].set_selected(False)

        # Select new
        self._selected_idx = idx
        if 0 <= idx < len(self.line_items):
            self.line_items[idx].set_selected(True)

            # Emit with tokens
            if self.current_folio and idx < len(self.current_folio.lines):
                tokens = self.current_folio.lines[idx]
                self.line_selected.emit(idx, tokens)

    def select_next(self) -> bool:
        """Select next line. Returns False if at end."""
        if not self.line_items:
            return False

        next_idx = self._selected_idx + 1
        if next_idx >= len(self.line_items):
            return False

        self.select_line(next_idx)
        return True

    def select_first(self):
        """Select first line."""
        if self.line_items:
            self.select_line(0)

    def get_selected_tokens(self) -> Optional[List[TokenData]]:
        """Get tokens for selected line."""
        if self.current_folio and 0 <= self._selected_idx < len(self.current_folio.lines):
            return self.current_folio.lines[self._selected_idx]
        return None

    @property
    def selected_index(self) -> int:
        """Get selected line index."""
        return self._selected_idx

    @property
    def line_count(self) -> int:
        """Get number of lines."""
        return len(self.line_items)
