"""
Currier A Record Panel.

Input panel for selecting a Currier A record (full line).
Per C233, C473, C481, C484 - the RECORD is the structural unit
that interacts with AZC, not individual tokens.

Selection flow: Folio → Line → Record
Shows aggregated constraint bundle for the entire record.
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QListWidget, QListWidgetItem, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from core.a_record_loader import get_a_record_store, ARecord, ARecordStore
from core.constraint_bundle import (
    compute_record_bundle, ConstraintBundle,
    compute_compatible_folios, BundleType
)
from core.data_loader import get_data_store


class AEntryPanel(QFrame):
    """
    Panel for Currier A record selection.

    Provides folio → line browsing to select full records,
    not individual tokens. Per structural contracts, the record
    is what gets projected through AZC.
    """

    # Signal emitted when a record is selected (full bundle)
    token_selected = pyqtSignal(ConstraintBundle)  # Keep name for compatibility

    def __init__(self, voynich_font: QFont = None):
        super().__init__()
        self.voynich_font = voynich_font or QFont("Courier New", 14)
        self._current_bundle = None
        self._store: ARecordStore = None
        self._current_records = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header
        header = QLabel("CURRIER A RECORD")
        header.setObjectName("header")
        layout.addWidget(header)

        # Folio selector
        folio_layout = QHBoxLayout()
        folio_label = QLabel("Folio:")
        folio_label.setFixedWidth(40)
        self.folio_combo = QComboBox()
        self.folio_combo.currentTextChanged.connect(self._on_folio_changed)
        folio_layout.addWidget(folio_label)
        folio_layout.addWidget(self.folio_combo, 1)
        layout.addLayout(folio_layout)

        # Filter for ACTIVATING entries only
        self.activating_filter = QCheckBox("Show only ACTIVATING entries")
        self.activating_filter.setToolTip(
            "ACTIVATING entries have restricted MIDDLEs that constrain B reachability.\n"
            "NEUTRAL entries (no restricted MIDDLEs) show no conditioning effect."
        )
        self.activating_filter.stateChanged.connect(self._on_filter_changed)
        layout.addWidget(self.activating_filter)

        # Record list (lines in selected folio)
        self.record_list = QListWidget()
        self.record_list.itemClicked.connect(self._on_record_clicked)
        self.record_list.setStyleSheet("""
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #2a3a4a;
            }
            QListWidget::item:selected {
                background-color: #2a4a6a;
            }
        """)
        layout.addWidget(self.record_list, 1)

        # Selected record display
        selected_group = QGroupBox("Selected Record")
        selected_layout = QVBoxLayout(selected_group)
        selected_layout.setContentsMargins(8, 8, 8, 8)
        selected_layout.setSpacing(4)

        # Record ID
        self.record_id_label = QLabel("(none selected)")
        self.record_id_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; color: #e0d8c8;"
        )
        selected_layout.addWidget(self.record_id_label)

        # Tokens display (in Voynich font)
        self.tokens_display = QLabel("")
        self.tokens_display.setFont(self.voynich_font)
        self.tokens_display.setWordWrap(True)
        self.tokens_display.setStyleSheet(
            "font-size: 14px; color: #e0d8c8; padding: 4px; "
            "background-color: #1a2535; border-radius: 4px;"
        )
        selected_layout.addWidget(self.tokens_display)

        # Token count
        self.token_count_label = QLabel("")
        self.token_count_label.setStyleSheet("color: #8090a0; font-size: 10px;")
        selected_layout.addWidget(self.token_count_label)

        layout.addWidget(selected_group)

        # Aggregate bundle display
        bundle_group = QGroupBox("Aggregate Bundle")
        bundle_layout = QVBoxLayout(bundle_group)
        bundle_layout.setContentsMargins(8, 8, 8, 8)
        bundle_layout.setSpacing(4)

        self.middles_label = QLabel("MIDDLEs: -")
        self.middles_label.setWordWrap(True)
        bundle_layout.addWidget(self.middles_label)

        # AZC-active MIDDLEs (the ones that actually constrain)
        self.azc_active_label = QLabel("AZC-active: -")
        self.azc_active_label.setWordWrap(True)
        self.azc_active_label.setStyleSheet("color: #f0a060;")
        bundle_layout.addWidget(self.azc_active_label)

        self.prefixes_label = QLabel("PREFIX families: -")
        bundle_layout.addWidget(self.prefixes_label)

        # Compatible folios count
        self.compatible_folios_label = QLabel("Compatible AZC folios: -")
        self.compatible_folios_label.setStyleSheet("color: #80a0c0;")
        bundle_layout.addWidget(self.compatible_folios_label)

        # Bundle type indicator (NEUTRAL/ACTIVATING/BLOCKED)
        self.type_label = QLabel("")
        self.type_label.setStyleSheet(
            "margin-top: 4px; padding: 4px; "
            "background-color: #1a3050; border-radius: 3px;"
        )
        bundle_layout.addWidget(self.type_label)

        layout.addWidget(bundle_group)

    def _load_data(self):
        """Load A record data."""
        self._store = get_a_record_store()

        # Populate folio dropdown
        self.folio_combo.clear()
        folios = self._store.folios
        if folios:
            self.folio_combo.addItems(folios)
            # Select first folio
            self._on_folio_changed(folios[0])

    def _on_folio_changed(self, folio: str):
        """Handle folio selection change."""
        if not folio or not self._store:
            return

        # Get records for this folio
        self._current_records = self._store.get_records_for_folio(folio)
        self._populate_record_list()

    def _on_filter_changed(self, state):
        """Handle filter checkbox change."""
        self._populate_record_list()

    def _populate_record_list(self):
        """Populate the record list with optional filtering."""
        self.record_list.clear()
        filter_activating = self.activating_filter.isChecked()
        data_store = get_data_store()

        for record in self._current_records:
            # Pre-compute bundle to get type
            bundle = compute_record_bundle(record)

            # Determine bundle type
            if bundle.azc_active:
                compatible = compute_compatible_folios(
                    frozenset(bundle.azc_active), data_store
                )
                if compatible:
                    bundle_type = BundleType.ACTIVATING
                else:
                    bundle_type = BundleType.BLOCKED
            else:
                bundle_type = BundleType.NEUTRAL

            # Apply filter
            if filter_activating and bundle_type != BundleType.ACTIVATING:
                continue

            # Show line number + first few tokens + bundle type
            tokens_preview = " ".join(record.tokens[:3])
            if len(record.tokens) > 3:
                tokens_preview += "..."

            # Type marker with bundle classification
            if bundle_type == BundleType.ACTIVATING:
                type_marker = " [ACT]"
            elif bundle_type == BundleType.BLOCKED:
                type_marker = " [BLK]"
            else:
                type_marker = " [NEU]"

            if record.is_short_entry:
                type_marker = " [1-tok]"

            display = f"L{record.line_number}: {tokens_preview}{type_marker}"

            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, record)
            item.setData(Qt.UserRole + 1, bundle_type)

            # Color by bundle type
            if bundle_type == BundleType.ACTIVATING:
                item.setForeground(QColor("#f0a060"))  # Orange for activating
            elif bundle_type == BundleType.BLOCKED:
                item.setForeground(QColor("#f06060"))  # Red for blocked
            elif record.is_short_entry:
                item.setForeground(QColor("#808080"))  # Gray for short
            else:
                item.setForeground(QColor("#90a0b0"))  # Dim for neutral

            self.record_list.addItem(item)

    def _on_record_clicked(self, item: QListWidgetItem):
        """Handle record selection."""
        record = item.data(Qt.UserRole)
        if record:
            self._select_record(record)

    def _select_record(self, record: ARecord):
        """Select a record and compute its bundle."""
        # Compute full record bundle
        bundle = compute_record_bundle(record)
        self._current_bundle = bundle
        data_store = get_data_store()

        # Compute compatible folios
        if bundle.azc_active:
            compatible_folios = compute_compatible_folios(
                frozenset(bundle.azc_active), data_store
            )
        else:
            compatible_folios = frozenset(data_store.azc_folio_middles.keys())

        # Determine bundle type
        if not bundle.azc_active:
            bundle_type = BundleType.NEUTRAL
        elif compatible_folios:
            bundle_type = BundleType.ACTIVATING
        else:
            bundle_type = BundleType.BLOCKED

        # Update record display
        self.record_id_label.setText(f"{record.display_name}")
        self.tokens_display.setText(record.tokens_display)
        self.token_count_label.setText(f"{record.token_count} tokens")

        # Update bundle display - all MIDDLEs
        if bundle.middles:
            middles_str = ", ".join(sorted(bundle.middles))
            self.middles_label.setText(f"MIDDLEs: {{{middles_str}}}")
        else:
            self.middles_label.setText("MIDDLEs: (none)")

        # Update AZC-active MIDDLEs (the constraining ones)
        if bundle.azc_active:
            azc_str = ", ".join(sorted(bundle.azc_active))
            self.azc_active_label.setText(f"AZC-active: {{{azc_str}}}")
            self.azc_active_label.setStyleSheet("color: #f0a060; font-weight: bold;")
        else:
            self.azc_active_label.setText("AZC-active: (none - no conditioning)")
            self.azc_active_label.setStyleSheet("color: #808080;")

        if bundle.prefix_families:
            prefixes_str = ", ".join(sorted(bundle.prefix_families))
            self.prefixes_label.setText(f"PREFIX families: {{{prefixes_str}}}")
        else:
            self.prefixes_label.setText("PREFIX families: (none)")

        # Update compatible folios
        n_compatible = len(compatible_folios)
        n_total = len(data_store.azc_folio_middles)
        self.compatible_folios_label.setText(
            f"Compatible AZC folios: {n_compatible}/{n_total}"
        )

        # Update type indicator with CLEAR bundle type
        if bundle.is_short_entry:
            self.type_label.setText("SHORT ENTRY (1 token) - rare")
            self.type_label.setStyleSheet(
                "margin-top: 4px; padding: 4px; "
                "background-color: #303050; border-radius: 3px; color: #9090d0;"
            )
        elif bundle_type == BundleType.NEUTRAL:
            self.type_label.setText(
                "NEUTRAL - No restricted MIDDLEs\n"
                "Baseline = Conditioned (correct behavior)"
            )
            self.type_label.setStyleSheet(
                "margin-top: 4px; padding: 4px; "
                "background-color: #1a3050; border-radius: 3px; color: #90b0d0;"
            )
        elif bundle_type == BundleType.ACTIVATING:
            self.type_label.setText(
                f"ACTIVATING - {len(bundle.azc_active)} restricted MIDDLE(s)\n"
                f"Should show conditioning effect"
            )
            self.type_label.setStyleSheet(
                "margin-top: 4px; padding: 4px; "
                "background-color: #503020; border-radius: 3px; color: #f0a060;"
            )
        else:  # BLOCKED
            self.type_label.setText(
                f"BLOCKED - MIDDLEs not jointly in any folio\n"
                "All classes pruned"
            )
            self.type_label.setStyleSheet(
                "margin-top: 4px; padding: 4px; "
                "background-color: #502020; border-radius: 3px; color: #f06060;"
            )

        # Emit signal
        self.token_selected.emit(bundle)

    def get_current_bundle(self) -> ConstraintBundle:
        """Get the currently selected bundle."""
        return self._current_bundle
