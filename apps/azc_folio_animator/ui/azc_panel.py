"""
AZC Panel - Dynamic display of activated AZC folio diagrams.

Shows 1-N mini-diagrams in a grid layout based on which folios
contain the clicked token. Each diagram is faithful to the folio's
actual layout with the token's position(s) illuminated.
"""
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.azc_folio_animator.core.azc_folio_model import AZCFolioModel
from apps.azc_folio_animator.core.azc_engine import AZCEngine
from apps.azc_folio_animator.ui.position_diagram import PositionDiagram


class MiniDiagram(QFrame):
    """
    Compact AZC folio diagram with header and illumination.

    Shows a single folio's constraint field layout with the
    selected token's position(s) illuminated.
    """

    # Signal emitted when fullscreen toggle is clicked
    fullscreen_toggled = pyqtSignal(object, bool)  # (self, is_fullscreen)

    def __init__(self, folio: AZCFolioModel, voynich_font: QFont, parent=None):
        super().__init__(parent)
        self.folio = folio
        self.voynich_font = voynich_font
        self._is_fullscreen = False

        # Create a dedicated engine for this diagram
        self.engine = AZCEngine(folio.family)

        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            MiniDiagram {
                background: #0a1018;
                border: 1px solid #2a3a4a;
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        # Header row: folio ID, family, and fullscreen toggle
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)

        family_color = "#00aacc" if self.folio.family == 'zodiac' else "#ffaa00"
        family_name = "Zodiac" if self.folio.family == 'zodiac' else "A/C"
        header = QLabel(f"<b>f{self.folio.folio_id}</b> "
                       f"<span style='color:{family_color}'>{family_name}</span>")
        header.setStyleSheet("color: #b0c4de; font-size: 11px; background: transparent;")

        # Fullscreen toggle button
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setFixedSize(22, 22)
        self.fullscreen_btn.setToolTip("Toggle fullscreen")
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background: #1a2a3a;
                border: 1px solid #3a4a5a;
                border-radius: 3px;
                color: #8a9aaa;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #2a3a4a;
                color: #00aacc;
                border-color: #00aacc;
            }
            QPushButton:checked {
                background: #00aacc;
                color: #ffffff;
            }
        """)
        self.fullscreen_btn.setCheckable(True)
        self.fullscreen_btn.clicked.connect(self._on_fullscreen_clicked)

        header_layout.addStretch()
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(self.fullscreen_btn)

        layout.addLayout(header_layout)

        # Diagram
        self.diagram = PositionDiagram(self.engine, self.voynich_font)
        self.diagram.setMinimumSize(250, 250)
        self.diagram.setMaximumSize(400, 400)

        # Set scaffold from folio data
        if self.folio.folio_data:
            self.diagram.set_scaffold_folio(self.folio.folio_data)

        layout.addWidget(self.diagram)

    def illuminate_token(self, token_text: str):
        """Highlight all positions where the exact token appears in this folio.

        Uses exact token matching for clarity - the clicked token is highlighted,
        not all tokens sharing the same MIDDLE.
        """
        # Get exact positions of this token
        positions = self.folio.get_positions(token_text)
        self.diagram.illuminate_by_token_text(token_text, positions)

    def _on_fullscreen_clicked(self):
        """Handle fullscreen button click."""
        self._is_fullscreen = self.fullscreen_btn.isChecked()
        self.fullscreen_toggled.emit(self, self._is_fullscreen)

    def set_fullscreen(self, fullscreen: bool):
        """Set fullscreen state (called by parent)."""
        self._is_fullscreen = fullscreen
        self.fullscreen_btn.setChecked(fullscreen)

        if fullscreen:
            # Remove ALL size constraints for fullscreen - both frame and diagram
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)  # QWIDGETSIZE_MAX
            self.diagram.setMinimumSize(0, 0)
            self.diagram.setMaximumSize(16777215, 16777215)
            # Set size policy to expanding
            from PyQt5.QtWidgets import QSizePolicy
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.diagram.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        else:
            # Restore size constraints
            self.diagram.setMinimumSize(250, 250)
            self.diagram.setMaximumSize(400, 400)
            from PyQt5.QtWidgets import QSizePolicy
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)


class AZCPanel(QWidget):
    """
    Dynamic panel showing 1-N AZC folio diagrams.

    When a token is clicked in the A-text strip, this panel displays
    all folios containing that token in a responsive grid layout.
    Each diagram shows the folio's layout with the token illuminated.
    """

    def __init__(self, voynich_font: QFont):
        super().__init__()
        self.voynich_font = voynich_font
        self.diagrams: List[MiniDiagram] = []
        self._fullscreen_diagram: MiniDiagram = None

        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background: #0f1623;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Scroll area for many diagrams
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #1a2635;
            }
            QScrollBar::handle:vertical {
                background: #3a4a5a;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(5, 5, 5, 5)

        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

        # Placeholder
        self.placeholder = QLabel("Select a line, then click a token\nto see its AZC positions")
        self.placeholder.setStyleSheet("color: #555; font-size: 14px; background: transparent;")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(self.placeholder, 0, 0, 1, 3)

    def show_activated_folios(self, folios: List[AZCFolioModel], token_text: str):
        """Display diagrams for all activated folios with illumination."""
        self._clear_diagrams()

        if not folios:
            self.placeholder.setText(f"'{token_text}' not found\nin any AZC folio")
            self.placeholder.show()
            return

        self.placeholder.hide()

        # Determine grid layout based on count
        count = len(folios)
        if count == 1:
            cols = 1
        elif count == 2:
            cols = 2
        elif count <= 4:
            cols = 2
        elif count <= 6:
            cols = 3
        else:
            cols = 3  # Max 3 columns, scroll for more

        for i, folio in enumerate(folios):
            row = i // cols
            col = i % cols

            diagram = MiniDiagram(folio, self.voynich_font)
            diagram.illuminate_token(token_text)
            diagram.fullscreen_toggled.connect(self._on_fullscreen_toggled)

            self.diagrams.append(diagram)
            self.grid.addWidget(diagram, row, col)

        # Add stretch at the bottom if not filling all rows
        if count > 0:
            final_row = (count - 1) // cols + 1
            self.grid.setRowStretch(final_row, 1)

    def _clear_diagrams(self):
        """Remove all diagram widgets."""
        # Handle fullscreen diagram - it's in main layout, not grid
        if self._fullscreen_diagram is not None:
            self.layout().removeWidget(self._fullscreen_diagram)
            self._fullscreen_diagram = None
            self.scroll.show()

        for diagram in self.diagrams:
            self.grid.removeWidget(diagram)
            diagram.deleteLater()
        self.diagrams.clear()

        # Reset row stretch
        for i in range(self.grid.rowCount()):
            self.grid.setRowStretch(i, 0)

    def clear(self):
        """Clear panel and show placeholder."""
        self._clear_diagrams()
        self._fullscreen_diagram = None
        self.placeholder.setText("Click a token to see its AZC positions")
        self.placeholder.show()

    def _on_fullscreen_toggled(self, diagram: MiniDiagram, is_fullscreen: bool):
        """Handle fullscreen toggle from a diagram."""
        if is_fullscreen:
            # Enter fullscreen: hide scroll area, add diagram directly to main layout
            self._fullscreen_diagram = diagram
            for d in self.diagrams:
                if d is not diagram:
                    d.hide()

            # Remove from grid and hide scroll area
            self.grid.removeWidget(diagram)
            self.scroll.hide()

            # Add directly to main layout (bypassing scroll area)
            diagram.set_fullscreen(True)
            self.layout().addWidget(diagram, 1)  # stretch=1 to fill

        else:
            # Exit fullscreen: restore to grid inside scroll area
            self._fullscreen_diagram = None
            diagram.set_fullscreen(False)

            # Remove from main layout
            self.layout().removeWidget(diagram)

            # Show scroll area again
            self.scroll.show()

            # Rebuild grid layout
            count = len(self.diagrams)
            if count == 1:
                cols = 1
            elif count <= 4:
                cols = 2
            else:
                cols = 3

            for i, d in enumerate(self.diagrams):
                row = i // cols
                col = i % cols
                self.grid.addWidget(d, row, col)
                d.show()
