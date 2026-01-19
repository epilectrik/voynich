"""
B Reachability Panel - Currier B Folio Reachability Display.

Shows which Currier B folios remain reachable under the current
legality field, with binary classification FIRST.

Per expert guidance:
> Binary reachability before scoring.
> Primary: REACHABLE / CONDITIONAL / UNREACHABLE
> Secondary: Coverage percentage (labeled as "coverage" not "match")
> "B executes blind grammar within shrinking reachable space."
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QColor, QBrush

from core.reachability_engine import (
    ReachabilityResult, FolioReachability, ReachabilityStatus
)
from core.sufficiency_engine import SufficiencyStatus
from core.data_loader import get_data_store


# Status display configuration
STATUS_CONFIG = {
    ReachabilityStatus.REACHABLE: {
        'symbol': '✓',
        'text': 'REACHABLE',
        'color': '#4a8a6a',
        'bg': '#1a3530',
    },
    ReachabilityStatus.CONDITIONAL: {
        'symbol': '◐',
        'text': 'CONDITIONAL',
        'color': '#8a8a5a',
        'bg': '#2a3025',
    },
    ReachabilityStatus.UNREACHABLE: {
        'symbol': '✗',
        'text': 'UNREACHABLE',
        'color': '#8a4a4a',
        'bg': '#301a1a',
    },
}

# REGIME display configuration
# Per C179-C185: 4 stable regimes from OPS-2 K-Means clustering
# CEI ordering: REGIME_2 < REGIME_1 < REGIME_4 < REGIME_3
REGIME_CONFIG = {
    "REGIME_2": {
        'short': 'R2',
        'color': '#5a8a5a',  # green - gentle
        'tooltip': "REGIME_2: Gentle, high-waiting\n[Tier 3] Introductory procedures - per X.11-X.16 curriculum alignment",
    },
    "REGIME_1": {
        'short': 'R1',
        'color': '#6a7a8a',  # blue-gray - moderate
        'tooltip': "REGIME_1: Moderate\n[Tier 3] Standard execution - per X.11-X.16 curriculum alignment",
    },
    "REGIME_4": {
        'short': 'R4',
        'color': '#8a7a5a',  # amber - precision
        'tooltip': "REGIME_4: Precision-constrained\n[Tier 3] Tight control required - per X.11-X.16 curriculum alignment",
    },
    "REGIME_3": {
        'short': 'R3',
        'color': '#8a5a5a',  # red - aggressive
        'tooltip': "REGIME_3: Aggressive, transient\n[Tier 3] Advanced/high-risk - per X.11-X.16 curriculum alignment",
    },
}

# Sufficiency display configuration
# Per X.14 (Curriculum Completeness Model) - Tier 3 interpretation
# Per OJLM-1: Annotate, never prune
SUFFICIENCY_CONFIG = {
    SufficiencyStatus.SUFFICIENT: {
        'symbol': '●',
        'text': 'SUFFICIENT',
        'color': '#5a8a5a',  # green
        'tooltip': "Meets REGIME completeness requirements\n[Tier 3: X.14 Curriculum Completeness]",
    },
    SufficiencyStatus.INSUFFICIENT: {
        'symbol': '○',
        'text': 'INSUFFICIENT',
        'color': '#8a7a4a',  # amber
        'tooltip': "Below threshold for assigned REGIME\n[Tier 3: X.14 Curriculum Completeness]\nLegal but incomplete for full execution",
    },
    SufficiencyStatus.NOT_APPLICABLE: {
        'symbol': '-',
        'text': 'N/A',
        'color': '#606060',  # gray
        'tooltip': "REGIME_2/1 have no completeness thresholds\n[Tier 3: X.14 Curriculum Completeness]",
    },
}


class BReachabilityPanel(QFrame):
    """
    Panel showing Currier B folio reachability under the current
    AZC legality field.

    Shows binary classification (REACHABLE/CONDITIONAL/UNREACHABLE)
    as the PRIMARY indicator, with coverage as secondary.

    Emits folio_selected when a B folio is clicked, enabling
    Stage 2 compilation (program-specific view).
    """

    # Signal emitted when user clicks on a B folio row
    # Args: folio_id (str), folio_result (FolioReachability)
    folio_selected = pyqtSignal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_folio_results = {}  # folio_id -> FolioReachability
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header
        header = QLabel("CURRIER B REACHABILITY")
        header.setObjectName("header")
        layout.addWidget(header)

        # Summary bar
        summary_layout = QHBoxLayout()

        self.reachable_count = QLabel("✓ 0")
        self.reachable_count.setStyleSheet(
            f"color: {STATUS_CONFIG[ReachabilityStatus.REACHABLE]['color']}; "
            "font-weight: bold; padding: 4px;"
        )
        summary_layout.addWidget(self.reachable_count)

        self.conditional_count = QLabel("◐ 0")
        self.conditional_count.setStyleSheet(
            f"color: {STATUS_CONFIG[ReachabilityStatus.CONDITIONAL]['color']}; "
            "font-weight: bold; padding: 4px;"
        )
        summary_layout.addWidget(self.conditional_count)

        self.unreachable_count = QLabel("✗ 0")
        self.unreachable_count.setStyleSheet(
            f"color: {STATUS_CONFIG[ReachabilityStatus.UNREACHABLE]['color']}; "
            "font-weight: bold; padding: 4px;"
        )
        summary_layout.addWidget(self.unreachable_count)

        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        # REGIME distribution section
        # Per C179-C185: Tier 2 structural fact (OPS-2 K-Means clustering)
        # Curriculum interpretation is Tier 3 (X.11-X.16)
        regime_frame = QFrame()
        regime_layout = QHBoxLayout(regime_frame)
        regime_layout.setContentsMargins(0, 4, 0, 4)
        regime_layout.setSpacing(8)

        regime_header = QLabel("REGIME:")
        regime_header.setStyleSheet("color: #8090a0; font-weight: bold;")
        regime_header.setToolTip(
            "REGIME distribution of reachable folios (Tier 2: C179-C185)\n"
            "Procedural completeness classification from OPS-2 clustering.\n"
            "All reachable folios are equally SAFE (C458) - REGIME is observational."
        )
        regime_layout.addWidget(regime_header)

        # REGIME count labels (in CEI order: R2 < R1 < R4 < R3)
        self.regime_labels = {}
        for regime_id in ["REGIME_2", "REGIME_1", "REGIME_4", "REGIME_3"]:
            config = REGIME_CONFIG[regime_id]
            label = QLabel(f"{config['short']}: 0")
            label.setStyleSheet(
                f"color: {config['color']}; font-weight: bold; padding: 2px 6px;"
            )
            label.setToolTip(config['tooltip'])
            self.regime_labels[regime_id] = label
            regime_layout.addWidget(label)

        regime_layout.addStretch()
        layout.addWidget(regime_frame)

        # Sufficiency summary section - TWO DISPLAYS per external expert guidance:
        # 1. Global (B-intrinsic): Static, doesn't change with A selection
        # 2. Reachable: Filtered to currently reachable folios
        # Per X.14 (Curriculum Completeness) - Tier 3 interpretation
        # Per OJLM-1: Surfaced, not enforced
        suff_frame = QFrame()
        suff_layout = QVBoxLayout(suff_frame)
        suff_layout.setContentsMargins(0, 4, 0, 4)
        suff_layout.setSpacing(2)

        # Row 1: Global sufficiency (B-intrinsic, static)
        global_row = QHBoxLayout()
        global_row.setSpacing(8)

        global_header = QLabel("Sufficiency (Global):")
        global_header.setStyleSheet("color: #606a70; font-weight: bold;")
        global_header.setToolTip(
            "REGIME Sufficiency - GLOBAL (intrinsic to B folios)\n"
            "This does NOT change when you select different A folios.\n"
            "Sufficiency is an intrinsic property of each B folio's structure.\n\n"
            "[Tier 3: X.14 Curriculum Completeness]\n"
            "REGIME_4 requires 25% LINK density (monitoring completeness)\n"
            "REGIME_3 requires 2+ recovery operations (recovery completeness)\n\n"
            "Per OJLM-1: Surfaced for expert judgment, not enforced.\n"
            "Per C458: Risk is clamped globally; sufficiency varies locally."
        )
        global_row.addWidget(global_header)

        # Global sufficiency count labels
        self.global_sufficient_label = QLabel("● 0")
        self.global_sufficient_label.setStyleSheet(
            f"color: {SUFFICIENCY_CONFIG[SufficiencyStatus.SUFFICIENT]['color']}; "
            "padding: 2px 4px; opacity: 0.7;"
        )
        self.global_sufficient_label.setToolTip("Global: Folios meeting REGIME requirements")
        global_row.addWidget(self.global_sufficient_label)

        self.global_insufficient_label = QLabel("○ 0")
        self.global_insufficient_label.setStyleSheet(
            f"color: {SUFFICIENCY_CONFIG[SufficiencyStatus.INSUFFICIENT]['color']}; "
            "padding: 2px 4px; opacity: 0.7;"
        )
        self.global_insufficient_label.setToolTip("Global: Folios below REGIME threshold")
        global_row.addWidget(self.global_insufficient_label)

        self.global_na_label = QLabel("- 0")
        self.global_na_label.setStyleSheet(
            f"color: {SUFFICIENCY_CONFIG[SufficiencyStatus.NOT_APPLICABLE]['color']}; "
            "padding: 2px 4px; opacity: 0.7;"
        )
        self.global_na_label.setToolTip("Global: REGIME_2/1 have no thresholds")
        global_row.addWidget(self.global_na_label)

        global_row.addStretch()
        suff_layout.addLayout(global_row)

        # Row 2: Reachable sufficiency (filtered by current AZC context)
        reachable_row = QHBoxLayout()
        reachable_row.setSpacing(8)

        reachable_header = QLabel("Reachable:")
        reachable_header.setStyleSheet("color: #8090a0; font-weight: bold;")
        reachable_header.setToolTip(
            "REGIME Sufficiency - REACHABLE ONLY\n"
            "Filtered to folios reachable under current AZC legality.\n"
            "This DOES change when you select different A folios.\n\n"
            "[Tier 3: X.14 Curriculum Completeness]"
        )
        reachable_row.addWidget(reachable_header)

        # Reachable sufficiency count labels
        self.sufficient_label = QLabel("● 0")
        self.sufficient_label.setStyleSheet(
            f"color: {SUFFICIENCY_CONFIG[SufficiencyStatus.SUFFICIENT]['color']}; "
            "font-weight: bold; padding: 2px 6px;"
        )
        self.sufficient_label.setToolTip(SUFFICIENCY_CONFIG[SufficiencyStatus.SUFFICIENT]['tooltip'])
        reachable_row.addWidget(self.sufficient_label)

        self.insufficient_label = QLabel("○ 0")
        self.insufficient_label.setStyleSheet(
            f"color: {SUFFICIENCY_CONFIG[SufficiencyStatus.INSUFFICIENT]['color']}; "
            "font-weight: bold; padding: 2px 6px;"
        )
        self.insufficient_label.setToolTip(SUFFICIENCY_CONFIG[SufficiencyStatus.INSUFFICIENT]['tooltip'])
        reachable_row.addWidget(self.insufficient_label)

        self.na_label = QLabel("- 0")
        self.na_label.setStyleSheet(
            f"color: {SUFFICIENCY_CONFIG[SufficiencyStatus.NOT_APPLICABLE]['color']}; "
            "font-weight: bold; padding: 2px 6px;"
        )
        self.na_label.setToolTip(SUFFICIENCY_CONFIG[SufficiencyStatus.NOT_APPLICABLE]['tooltip'])
        reachable_row.addWidget(self.na_label)

        reachable_row.addStretch()
        suff_layout.addLayout(reachable_row)

        layout.addWidget(suff_frame)

        # Grammar Effects section - DYNAMIC metrics
        # Per external expert: Show "structure in motion", not invariants
        # These metrics CHANGE when you select different A folios
        grammar_frame = QFrame()
        grammar_layout = QHBoxLayout(grammar_frame)
        grammar_layout.setContentsMargins(0, 4, 0, 4)
        grammar_layout.setSpacing(8)

        grammar_header = QLabel("Grammar Effects:")
        grammar_header.setStyleSheet("color: #8090a0; font-weight: bold;")
        grammar_header.setToolTip(
            "Grammar contraction under current legality field.\n"
            "These metrics CHANGE when you select different A folios.\n\n"
            "Per model: 'B executes blind grammar within shrinking reachable space.'\n"
            "The 49-class grammar is universal (C121). AZC restricts which\n"
            "classes are reachable by constraining MIDDLE availability (C470)."
        )
        grammar_layout.addWidget(grammar_header)

        # Instruction classes active
        self.classes_label = QLabel("Classes: 49/49")
        self.classes_label.setStyleSheet("color: #6a8aaa; padding: 2px 6px;")
        self.classes_label.setToolTip(
            "Instruction classes active under current legality field.\n"
            "49 classes exist (C121). Some may become unreachable\n"
            "when AZC restricts MIDDLE availability."
        )
        grammar_layout.addWidget(self.classes_label)

        # Decomposable hazards suppressed
        self.decomp_hazards_label = QLabel("Hazards suppressed: 0/6")
        self.decomp_hazards_label.setStyleSheet("color: #8a7a5a; padding: 2px 6px;")
        self.decomp_hazards_label.setToolTip(
            "Decomposable hazard classes suppressed by MIDDLE restrictions.\n"
            "6 hazard classes have MIDDLE involvement (context-tunable).\n"
            "3 hazard classes are atomic (always active, cannot be suppressed).\n\n"
            "Per C470: MIDDLE restrictions transfer intact to B."
        )
        grammar_layout.addWidget(self.decomp_hazards_label)

        # Atomic hazards unchanged
        self.atomic_label = QLabel("Atomic: 3/3")
        self.atomic_label.setStyleSheet("color: #606060; padding: 2px 6px;")
        self.atomic_label.setToolTip(
            "Atomic hazard classes (always active regardless of AZC context).\n"
            "Classes 7, 9, 23 have no MIDDLE involvement.\n"
            "These hazards are universally enforced."
        )
        grammar_layout.addWidget(self.atomic_label)

        grammar_layout.addStretch()
        layout.addWidget(grammar_frame)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Status", "Folio", "REGIME", "Suff", "Zones Reachable", "Missing Classes"
        ])

        # Configure table
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        # Set column widths
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Fixed)   # Status
        header_view.setSectionResizeMode(1, QHeaderView.Fixed)   # Folio
        header_view.setSectionResizeMode(2, QHeaderView.Fixed)   # REGIME
        header_view.setSectionResizeMode(3, QHeaderView.Fixed)   # Suff
        header_view.setSectionResizeMode(4, QHeaderView.Stretch) # Zones Reachable
        header_view.setSectionResizeMode(5, QHeaderView.Stretch) # Missing Classes
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 55)
        self.table.setColumnWidth(3, 55)

        # Style
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a2535;
                border: 1px solid #2a3a4a;
                border-radius: 3px;
                gridline-color: #2a3a4a;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #2a4a6a;
            }
            QHeaderView::section {
                background-color: #151d2e;
                color: #b0c4de;
                padding: 4px;
                border: none;
                border-bottom: 1px solid #2a3a4a;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.table, 1)

        # Connect table click for Stage 2 compilation view
        self.table.cellClicked.connect(self._on_folio_clicked)

        # Footer message
        self.footer = QLabel(
            "B executes blind grammar within shrinking reachable space."
        )
        self.footer.setStyleSheet(
            "color: #8090a0; font-style: italic; margin-top: 4px;"
        )
        self.footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer)

    def _create_status_item(self, status: ReachabilityStatus) -> QTableWidgetItem:
        """Create a table item for the status column."""
        config = STATUS_CONFIG[status]
        item = QTableWidgetItem(f"{config['symbol']} {config['text']}")
        item.setForeground(QBrush(QColor(config['color'])))
        return item

    def _create_zones_item(self, folio_result: FolioReachability) -> QTableWidgetItem:
        """Create a table item showing reachable zones."""
        if folio_result.status == ReachabilityStatus.REACHABLE:
            text = "C P R1 R2 R3 S (all)"
        elif folio_result.reachable_zones:
            text = " ".join(folio_result.reachable_zones)
        else:
            text = "(none)"

        item = QTableWidgetItem(text)
        return item

    def _create_missing_item(self, folio_result: FolioReachability) -> QTableWidgetItem:
        """Create a table item showing missing classes."""
        if not folio_result.missing_classes:
            text = "(none)"
        else:
            classes = sorted(folio_result.missing_classes)
            if len(classes) <= 5:
                text = ", ".join(f"Class {c}" for c in classes)
            else:
                shown = classes[:4]
                text = ", ".join(f"Class {c}" for c in shown) + f" (+{len(classes)-4})"

        item = QTableWidgetItem(text)
        if folio_result.missing_classes:
            item.setForeground(QBrush(QColor("#8a6a5a")))
        return item

    def _create_regime_item(self, folio: str) -> QTableWidgetItem:
        """Create a table item showing REGIME classification."""
        data_store = get_data_store()
        regime = data_store.regime_assignments.get(folio, "")

        if regime and regime in REGIME_CONFIG:
            config = REGIME_CONFIG[regime]
            item = QTableWidgetItem(config['short'])
            item.setForeground(QBrush(QColor(config['color'])))
            item.setToolTip(config['tooltip'])
        else:
            item = QTableWidgetItem("-")
            item.setForeground(QBrush(QColor("#505050")))

        return item

    def _create_sufficiency_item(self, folio_result: FolioReachability) -> QTableWidgetItem:
        """Create a table item showing sufficiency status."""
        sufficiency = folio_result.sufficiency

        if not sufficiency:
            item = QTableWidgetItem("-")
            item.setForeground(QBrush(QColor("#505050")))
            return item

        config = SUFFICIENCY_CONFIG[sufficiency.status]

        if sufficiency.status == SufficiencyStatus.SUFFICIENT:
            text = config['symbol']
        elif sufficiency.status == SufficiencyStatus.INSUFFICIENT:
            # Show what's missing
            if sufficiency.missing_link_pct is not None:
                actual_pct = sufficiency.link_density * 100
                text = f"{config['symbol']}{actual_pct:.0f}%"
            elif sufficiency.missing_recovery is not None:
                text = f"{config['symbol']}{sufficiency.recovery_ops}"
            else:
                text = config['symbol']
        else:
            text = config['symbol']

        item = QTableWidgetItem(text)
        item.setForeground(QBrush(QColor(config['color'])))

        # Build detailed tooltip
        tooltip_lines = [config['tooltip'], ""]
        if sufficiency.status == SufficiencyStatus.INSUFFICIENT:
            if sufficiency.required_link is not None:
                tooltip_lines.append(
                    f"LINK density: {sufficiency.link_density:.1%} "
                    f"(requires {sufficiency.required_link:.0%})"
                )
            if sufficiency.required_recovery is not None:
                tooltip_lines.append(
                    f"Recovery ops: {sufficiency.recovery_ops} "
                    f"(requires {sufficiency.required_recovery})"
                )
        elif sufficiency.status == SufficiencyStatus.SUFFICIENT:
            if sufficiency.required_link is not None:
                tooltip_lines.append(f"LINK density: {sufficiency.link_density:.1%} ✓")
            if sufficiency.required_recovery is not None:
                tooltip_lines.append(f"Recovery ops: {sufficiency.recovery_ops} ✓")

        item.setToolTip("\n".join(tooltip_lines))
        return item

    @pyqtSlot(object)
    def update_reachability(self, result: ReachabilityResult):
        """Update the panel from a reachability result."""
        # Store folio results for click handler lookup (Stage 2 compilation)
        self._current_folio_results = {
            fr.folio: fr for fr in result.folio_results.values()
        }

        # Update counts
        reachable = result.reachable_folios
        conditional = result.conditional_folios
        unreachable = result.unreachable_folios

        self.reachable_count.setText(f"✓ {len(reachable)} REACHABLE")
        self.conditional_count.setText(f"◐ {len(conditional)} CONDITIONAL")
        self.unreachable_count.setText(f"✗ {len(unreachable)} UNREACHABLE")

        # Compute REGIME distribution of reachable folios
        # Per C179-C185: Tier 2 structural fact
        # Per C458: All reachable folios are equally SAFE
        data_store = get_data_store()
        regime_counts = {"REGIME_2": 0, "REGIME_1": 0, "REGIME_4": 0, "REGIME_3": 0}

        for fr in reachable:
            regime = data_store.regime_assignments.get(fr.folio, "")
            if regime in regime_counts:
                regime_counts[regime] += 1

        # Update REGIME labels
        for regime_id, count in regime_counts.items():
            config = REGIME_CONFIG[regime_id]
            self.regime_labels[regime_id].setText(f"{config['short']}: {count}")

        # Compute sufficiency distribution (Tier 3: X.14)
        # Per OJLM-1: Surfaced for expert judgment, not enforced
        # Per external expert: Show BOTH global (static) and reachable (filtered)

        # Global sufficiency (ALL B folios - doesn't change with A selection)
        global_suff_counts = {
            SufficiencyStatus.SUFFICIENT: 0,
            SufficiencyStatus.INSUFFICIENT: 0,
            SufficiencyStatus.NOT_APPLICABLE: 0,
        }
        for fr in result.folio_results.values():
            if fr.sufficiency:
                global_suff_counts[fr.sufficiency.status] += 1

        # Reachable sufficiency (REACHABLE folios only - changes with A selection)
        reachable_suff_counts = {
            SufficiencyStatus.SUFFICIENT: 0,
            SufficiencyStatus.INSUFFICIENT: 0,
            SufficiencyStatus.NOT_APPLICABLE: 0,
        }
        for fr in reachable:
            if fr.sufficiency:
                reachable_suff_counts[fr.sufficiency.status] += 1

        # Update global sufficiency labels (static, B-intrinsic)
        self.global_sufficient_label.setText(f"● {global_suff_counts[SufficiencyStatus.SUFFICIENT]}")
        self.global_insufficient_label.setText(f"○ {global_suff_counts[SufficiencyStatus.INSUFFICIENT]}")
        self.global_na_label.setText(f"- {global_suff_counts[SufficiencyStatus.NOT_APPLICABLE]}")

        # Update reachable sufficiency labels (filtered by current AZC context)
        self.sufficient_label.setText(f"● {reachable_suff_counts[SufficiencyStatus.SUFFICIENT]}")
        self.insufficient_label.setText(f"○ {reachable_suff_counts[SufficiencyStatus.INSUFFICIENT]}")
        self.na_label.setText(f"- {reachable_suff_counts[SufficiencyStatus.NOT_APPLICABLE]}")

        # Update Grammar Effects (dynamic metrics)
        # Per external expert: Show "structure in motion"
        # These metrics CHANGE when you select different A folios
        grammar = result.grammar_state

        n_reachable = len(grammar.reachable_classes)
        n_decomp_suppressed = len(grammar.decomposable_hazards_pruned)
        n_decomp_total = len(grammar.decomposable_hazards_reachable) + len(grammar.decomposable_hazards_pruned)
        n_atomic = len(grammar.atomic_hazards_reachable)

        # Update labels with color coding based on contraction
        if n_reachable == 49:
            classes_color = "#5a8a5a"  # green - full
        elif n_reachable >= 40:
            classes_color = "#8a8a5a"  # yellow - mild contraction
        else:
            classes_color = "#8a5a5a"  # red - significant contraction

        self.classes_label.setText(f"Classes: {n_reachable}/49")
        self.classes_label.setStyleSheet(f"color: {classes_color}; font-weight: bold; padding: 2px 6px;")

        # Color code hazards by suppression level
        if n_decomp_suppressed == 0:
            hazard_color = "#5a8a5a"  # green - none suppressed
        elif n_decomp_suppressed <= 2:
            hazard_color = "#8a8a5a"  # yellow
        else:
            hazard_color = "#8a5a5a"  # red - many suppressed

        self.decomp_hazards_label.setText(f"Hazards suppressed: {n_decomp_suppressed}/{n_decomp_total}")
        self.decomp_hazards_label.setStyleSheet(f"color: {hazard_color}; font-weight: bold; padding: 2px 6px;")

        self.atomic_label.setText(f"Atomic: {n_atomic}/3")

        # Populate table - sorted by status (REACHABLE first, then CONDITIONAL, then UNREACHABLE)
        all_results = (
            sorted(reachable, key=lambda r: r.folio) +
            sorted(conditional, key=lambda r: r.folio) +
            sorted(unreachable, key=lambda r: r.folio)
        )

        self.table.setRowCount(len(all_results))

        for row, folio_result in enumerate(all_results):
            # Status (PRIMARY column)
            status_item = self._create_status_item(folio_result.status)
            self.table.setItem(row, 0, status_item)

            # Folio name
            folio_item = QTableWidgetItem(folio_result.folio)
            self.table.setItem(row, 1, folio_item)

            # REGIME classification
            regime_item = self._create_regime_item(folio_result.folio)
            self.table.setItem(row, 2, regime_item)

            # Sufficiency (Tier 3: X.14)
            suff_item = self._create_sufficiency_item(folio_result)
            self.table.setItem(row, 3, suff_item)

            # Zones reachable
            zones_item = self._create_zones_item(folio_result)
            self.table.setItem(row, 4, zones_item)

            # Missing classes
            missing_item = self._create_missing_item(folio_result)
            self.table.setItem(row, 5, missing_item)

        # Update footer
        total = len(result.folio_results)
        pct_reachable = len(reachable) / total * 100 if total > 0 else 0
        self.footer.setText(
            f"B executes blind grammar within shrinking reachable space. "
            f"({pct_reachable:.0f}% fully reachable)"
        )

    def reset(self):
        """Reset to initial state."""
        self.reachable_count.setText("✓ 0")
        self.conditional_count.setText("◐ 0")
        self.unreachable_count.setText("✗ 0")

        # Reset REGIME labels
        for regime_id in self.regime_labels:
            config = REGIME_CONFIG[regime_id]
            self.regime_labels[regime_id].setText(f"{config['short']}: 0")

        # Reset sufficiency labels (both global and reachable)
        self.global_sufficient_label.setText("● 0")
        self.global_insufficient_label.setText("○ 0")
        self.global_na_label.setText("- 0")
        self.sufficient_label.setText("● 0")
        self.insufficient_label.setText("○ 0")
        self.na_label.setText("- 0")

        # Reset Grammar Effects labels
        self.classes_label.setText("Classes: 49/49")
        self.classes_label.setStyleSheet("color: #6a8aaa; padding: 2px 6px;")
        self.decomp_hazards_label.setText("Hazards suppressed: 0/6")
        self.decomp_hazards_label.setStyleSheet("color: #8a7a5a; padding: 2px 6px;")
        self.atomic_label.setText("Atomic: 3/3")

        self.table.setRowCount(0)
        self.footer.setText(
            "B executes blind grammar within shrinking reachable space."
        )
        self._current_folio_results = {}

    def _on_folio_clicked(self, row: int, column: int):
        """Handle click on a folio row - emit signal for Stage 2 compilation."""
        # Get folio name from column 1 (Folio column)
        folio_item = self.table.item(row, 1)
        if not folio_item:
            return

        folio_id = folio_item.text()
        folio_result = self._current_folio_results.get(folio_id)

        if folio_result:
            self.folio_selected.emit(folio_id, folio_result)
