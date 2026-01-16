"""
Constraint Panel - Searchable browser for the 411+ validated constraints.

Provides:
- Search by C-number, keyword, or description
- Filter by tier (0-4) and category
- Full constraint text display
- Click-to-copy constraint references
"""

from typing import Optional, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QTextEdit, QComboBox,
    QFrame, QSplitter, QPushButton, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import sys
from pathlib import Path

# Handle imports for both package and direct execution
_app_dir = Path(__file__).parent.parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))

try:
    from core.constraints import ConstraintLoader, Constraint, ConstraintTier
except ImportError:
    from ..core.constraints import ConstraintLoader, Constraint, ConstraintTier


# Color palette
PALETTE = {
    'background': '#12100E',
    'panel': '#1A1612',
    'border': '#3D3428',
    'copper': '#C9A227',
    'amber': '#FFBF00',
    'parchment': '#D4B896',
    'tier0': '#50A050',  # Green - frozen
    'tier1': '#A05050',  # Red - falsified
    'tier2': '#5080B4',  # Blue - validated
    'tier3': '#B490C8',  # Purple - speculative
    'tier4': '#808080',  # Gray - interpretive
}


class ConstraintListItem(QListWidgetItem):
    """Custom list item for constraints."""

    def __init__(self, constraint: Constraint):
        super().__init__()
        self.constraint = constraint

        # Format display
        tier_labels = {
            ConstraintTier.TIER_0: "[T0]",
            ConstraintTier.TIER_1: "[T1]",
            ConstraintTier.TIER_2: "[T2]",
            ConstraintTier.TIER_3: "[T3]",
            ConstraintTier.TIER_4: "[T4]",
        }
        tier_label = tier_labels.get(constraint.tier, "[??]")

        # Truncate description if too long
        desc = constraint.description[:60] + "..." if len(constraint.description) > 60 else constraint.description
        self.setText(f"{constraint.id} {tier_label} {desc}")

        # Color by tier
        tier_colors = {
            ConstraintTier.TIER_0: PALETTE['tier0'],
            ConstraintTier.TIER_1: PALETTE['tier1'],
            ConstraintTier.TIER_2: PALETTE['tier2'],
            ConstraintTier.TIER_3: PALETTE['tier3'],
            ConstraintTier.TIER_4: PALETTE['tier4'],
        }
        color = tier_colors.get(constraint.tier, PALETTE['parchment'])
        self.setForeground(QColor(color))


class ConstraintPanel(QFrame):
    """
    Searchable constraint browser panel.

    Shows the 411+ validated constraints with filtering and search.
    """

    constraint_selected = pyqtSignal(object)  # Emits Constraint when selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loader = ConstraintLoader()
        self._current_constraint: Optional[Constraint] = None
        self._setup_ui()
        self._populate_list()

    def _setup_ui(self):
        """Set up the constraint browser UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header
        header = QLabel(f"CONSTRAINTS ({self._loader.total_count})")
        header.setFont(QFont("Consolas", 10, QFont.Bold))
        header.setStyleSheet(f"color: {PALETTE['copper']}; padding: 5px;")
        layout.addWidget(header)

        # Search bar
        search_layout = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search C-number, keyword...")
        self._search_input.textChanged.connect(self._on_search)
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {PALETTE['panel']};
                color: {PALETTE['parchment']};
                border: 1px solid {PALETTE['border']};
                border-radius: 3px;
                padding: 5px;
            }}
        """)
        search_layout.addWidget(self._search_input)

        # Tier filter
        self._tier_filter = QComboBox()
        self._tier_filter.addItems(["All Tiers", "Tier 0 (Frozen)", "Tier 1 (Falsified)",
                                     "Tier 2 (Validated)", "Tier 3 (Speculative)", "Tier 4 (Interpretive)"])
        self._tier_filter.currentIndexChanged.connect(self._on_filter_changed)
        self._tier_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {PALETTE['panel']};
                color: {PALETTE['parchment']};
                border: 1px solid {PALETTE['border']};
                border-radius: 3px;
                padding: 5px;
                min-width: 120px;
            }}
        """)
        search_layout.addWidget(self._tier_filter)
        layout.addLayout(search_layout)

        # Splitter for list and detail
        splitter = QSplitter(Qt.Vertical)

        # Constraint list
        self._constraint_list = QListWidget()
        self._constraint_list.currentItemChanged.connect(self._on_selection_changed)
        self._constraint_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {PALETTE['panel']};
                border: 1px solid {PALETTE['border']};
                border-radius: 3px;
            }}
            QListWidget::item {{
                padding: 3px;
                border-bottom: 1px solid {PALETTE['border']};
            }}
            QListWidget::item:selected {{
                background-color: {PALETTE['border']};
            }}
        """)
        splitter.addWidget(self._constraint_list)

        # Detail view
        detail_frame = QFrame()
        detail_layout = QVBoxLayout(detail_frame)
        detail_layout.setContentsMargins(5, 5, 5, 5)

        # Constraint ID and copy button
        id_layout = QHBoxLayout()
        self._id_label = QLabel("")
        self._id_label.setFont(QFont("Consolas", 12, QFont.Bold))
        self._id_label.setStyleSheet(f"color: {PALETTE['amber']};")
        id_layout.addWidget(self._id_label)

        self._copy_btn = QPushButton("Copy ID")
        self._copy_btn.clicked.connect(self._copy_constraint_id)
        self._copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PALETTE['border']};
                color: {PALETTE['parchment']};
                border: 1px solid {PALETTE['copper']};
                border-radius: 3px;
                padding: 3px 10px;
            }}
            QPushButton:hover {{
                background-color: {PALETTE['copper']};
            }}
        """)
        id_layout.addWidget(self._copy_btn)
        id_layout.addStretch()
        detail_layout.addLayout(id_layout)

        # Full text display
        self._detail_text = QTextEdit()
        self._detail_text.setReadOnly(True)
        self._detail_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {PALETTE['background']};
                color: {PALETTE['parchment']};
                border: 1px solid {PALETTE['border']};
                border-radius: 3px;
                padding: 5px;
            }}
        """)
        detail_layout.addWidget(self._detail_text)

        detail_frame.setStyleSheet(f"background-color: {PALETTE['panel']};")
        splitter.addWidget(detail_frame)

        splitter.setSizes([200, 150])
        layout.addWidget(splitter)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PALETTE['background']};
                border: 2px solid {PALETTE['border']};
                border-radius: 5px;
            }}
        """)

    def _populate_list(self, constraints: Optional[List[Constraint]] = None):
        """Populate the constraint list."""
        self._constraint_list.clear()

        if constraints is None:
            # Show all constraints sorted by number
            constraints = sorted(self._loader.constraints.values(), key=lambda c: c.number)

        for constraint in constraints:
            item = ConstraintListItem(constraint)
            self._constraint_list.addItem(item)

    def _on_search(self, text: str):
        """Handle search input."""
        if not text.strip():
            self._populate_list()
            return

        results = self._loader.search(text)
        self._populate_list(results)

    def _on_filter_changed(self, index: int):
        """Handle tier filter change."""
        if index == 0:
            self._populate_list()
            return

        tier_map = {
            1: ConstraintTier.TIER_0,
            2: ConstraintTier.TIER_1,
            3: ConstraintTier.TIER_2,
            4: ConstraintTier.TIER_3,
            5: ConstraintTier.TIER_4,
        }
        tier = tier_map.get(index)
        if tier:
            results = self._loader.get_by_tier(tier)
            self._populate_list(results)

    def _on_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle constraint selection."""
        if not current or not isinstance(current, ConstraintListItem):
            return

        constraint = current.constraint
        self._current_constraint = constraint
        self._id_label.setText(constraint.id)

        # Build detail text
        tier_names = {
            ConstraintTier.TIER_0: "Tier 0 - Frozen Fact",
            ConstraintTier.TIER_1: "Tier 1 - Falsified",
            ConstraintTier.TIER_2: "Tier 2 - Validated",
            ConstraintTier.TIER_3: "Tier 3 - Speculative",
            ConstraintTier.TIER_4: "Tier 4 - Interpretive",
        }

        detail = f"""<b>{constraint.id}</b> - {tier_names.get(constraint.tier, 'Unknown')}
<br><br>
<b>Category:</b> {constraint.category}
<br><br>
<b>Description:</b><br>
{constraint.description}
"""

        # Load full text if available
        full_text = self._loader.load_full_text(constraint)
        if full_text:
            # Show first 500 chars of full text
            preview = full_text[:500]
            if len(full_text) > 500:
                preview += "..."
            detail += f"<br><br><b>Full Text:</b><br><pre>{preview}</pre>"

        if constraint.file_path:
            detail += f"<br><br><i>File: {constraint.file_path}</i>"
        elif constraint.registry:
            detail += f"<br><br><i>Registry: {constraint.registry}</i>"

        self._detail_text.setHtml(detail)
        self.constraint_selected.emit(constraint)

    def _copy_constraint_id(self):
        """Copy current constraint ID to clipboard."""
        if self._current_constraint:
            clipboard = QApplication.clipboard()
            clipboard.setText(self._current_constraint.id)

    def search(self, query: str):
        """Programmatically search constraints."""
        self._search_input.setText(query)

    def filter_by_token(self, token: str):
        """Filter constraints to show those relevant to a specific token."""
        # Search for constraints mentioning this token
        results = self._loader.find_for_token(token)

        if results:
            self._populate_list(results)
            self._search_input.setText(f"token: {token}")

            # Select first result
            if self._constraint_list.count() > 0:
                self._constraint_list.setCurrentRow(0)
        else:
            # Fall back to text search
            self._search_input.setText(token)
