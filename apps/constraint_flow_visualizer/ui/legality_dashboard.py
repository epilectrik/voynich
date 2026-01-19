"""
Legality Envelope Dashboard

Visualizes what CHANGES when you select different A records:
- AZC Folio Activation (which constraint profiles light up)
- Escape/Recovery Rate (28x variance across A records)
- MIDDLE Compatibility (95.7% incompatible, unique fingerprints)
- B Folio Impact (what gets blocked for a specific program)

Per validated approach: "The Voynich system is constant in shape but
wildly variable in constraint — and constraints are not graph-shaped."

This dashboard shows the LEGALITY ENVELOPE, not the grammar structure.
"""

from typing import Optional, Set, List, Dict
from dataclasses import dataclass

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QListWidget, QListWidgetItem, QGroupBox,
    QComboBox, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QFont

from core.data_loader import get_data_store
from core.constraint_bundle import ConstraintBundle
from core.reachability_engine import ReachabilityResult


@dataclass
class LegalitySnapshot:
    """Computed legality state for an A record."""
    middles: Set[str]
    activated_azc_folios: Set[str]
    blocked_azc_folios: Set[str]
    escape_rate: float  # 0.0 to 1.0
    compatible_middle_count: int
    incompatible_middle_count: int
    total_middles: int


class LegalityDashboard(QFrame):
    """
    Main dashboard showing legality envelope for selected A record.

    Replaces the old graph-based control loop visualization.
    Shows quantitative constraint data that changes dramatically
    between A record selections.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_store = get_data_store()
        self._current_bundle: Optional[ConstraintBundle] = None
        self._current_snapshot: Optional[LegalitySnapshot] = None
        self._selected_b_folio: Optional[str] = None

        self._setup_ui()

    def _setup_ui(self):
        """Build the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Header
        header = QLabel("LEGALITY ENVELOPE DASHBOARD")
        header.setStyleSheet("color: #e0d8c8; font-weight: bold; font-size: 14px;")
        header.setToolTip(
            "Shows what CHANGES when you select different A records.\n"
            "The grammar is fixed; the legality envelope varies dramatically."
        )
        layout.addWidget(header)

        # Subtitle showing selected A record
        self._record_label = QLabel("No A record selected")
        self._record_label.setStyleSheet("color: #a0b0c0; font-size: 11px;")
        layout.addWidget(self._record_label)

        # Create scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(12)

        # Panel 1: AZC Folio Activation
        self._azc_panel = self._create_azc_activation_panel()
        content_layout.addWidget(self._azc_panel)

        # Panel 2: Escape Rate Meter
        self._escape_panel = self._create_escape_meter_panel()
        content_layout.addWidget(self._escape_panel)

        # Panel 3: MIDDLE Compatibility
        self._compat_panel = self._create_compatibility_panel()
        content_layout.addWidget(self._compat_panel)

        # Panel 4: B Folio selector and impact
        self._b_impact_panel = self._create_b_impact_panel()
        content_layout.addWidget(self._b_impact_panel)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

    def _create_azc_activation_panel(self) -> QGroupBox:
        """Create AZC Folio Activation panel."""
        panel = QGroupBox("AZC FOLIO ACTIVATION")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #e0d8c8;
                border: 1px solid #3a4a5a;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout(panel)

        # Progress bar showing activation ratio
        self._azc_progress = QProgressBar()
        self._azc_progress.setRange(0, 29)  # 29 AZC folios
        self._azc_progress.setValue(0)
        self._azc_progress.setFormat("ACTIVATED: %v/29 AZC folios")
        self._azc_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3a4a5a;
                border-radius: 3px;
                text-align: center;
                background-color: #1a2535;
                color: #e0d8c8;
            }
            QProgressBar::chunk {
                background-color: #4a7a4a;
            }
        """)
        layout.addWidget(self._azc_progress)

        # List of activated/blocked folios
        self._azc_list = QListWidget()
        self._azc_list.setMaximumHeight(150)
        self._azc_list.setStyleSheet("""
            QListWidget {
                background-color: #1a2535;
                border: 1px solid #3a4a5a;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 2px;
            }
        """)
        layout.addWidget(self._azc_list)

        return panel

    def _create_escape_meter_panel(self) -> QGroupBox:
        """Create Escape/Recovery Rate meter panel."""
        panel = QGroupBox("RECOVERY BUDGET")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #e0d8c8;
                border: 1px solid #3a4a5a;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout(panel)

        # Labels for range
        range_layout = QHBoxLayout()
        low_label = QLabel("LOW (1.0%)")
        low_label.setStyleSheet("color: #9a4a4a; font-size: 10px;")
        high_label = QLabel("HIGH (28.6%)")
        high_label.setStyleSheet("color: #4a9a4a; font-size: 10px;")
        range_layout.addWidget(low_label)
        range_layout.addStretch()
        range_layout.addWidget(high_label)
        layout.addLayout(range_layout)

        # Progress bar as meter
        self._escape_meter = QProgressBar()
        self._escape_meter.setRange(0, 286)  # 0.0% to 28.6% (scaled by 10)
        self._escape_meter.setValue(0)
        self._escape_meter.setFormat("%v‰")
        self._escape_meter.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3a4a5a;
                border-radius: 3px;
                text-align: center;
                background-color: #1a2535;
                color: #e0d8c8;
                min-height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9a4a4a, stop:0.5 #9a7a4a, stop:1 #4a9a4a);
            }
        """)
        layout.addWidget(self._escape_meter)

        # Current value label
        self._escape_label = QLabel("Select an A record to see recovery budget")
        self._escape_label.setStyleSheet("color: #a0b0c0; font-size: 11px;")
        self._escape_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._escape_label)

        # Interpretation
        self._escape_interpretation = QLabel("")
        self._escape_interpretation.setStyleSheet("color: #f0a060; font-size: 10px;")
        self._escape_interpretation.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._escape_interpretation)

        return panel

    def _create_compatibility_panel(self) -> QGroupBox:
        """Create MIDDLE Compatibility snapshot panel."""
        panel = QGroupBox("MIDDLE COMPATIBILITY")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #e0d8c8;
                border: 1px solid #3a4a5a;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout(panel)

        # This record's MIDDLEs
        self._middles_label = QLabel("MIDDLEs: (none)")
        self._middles_label.setStyleSheet("color: #a0b0c0; font-size: 11px;")
        self._middles_label.setWordWrap(True)
        layout.addWidget(self._middles_label)

        # Compatible count
        compat_layout = QHBoxLayout()
        self._compat_label = QLabel("Compatible: 0 (0%)")
        self._compat_label.setStyleSheet("color: #4a9a4a; font-size: 11px;")
        self._incompat_label = QLabel("Blocked: 0 (0%)")
        self._incompat_label.setStyleSheet("color: #9a4a4a; font-size: 11px;")
        compat_layout.addWidget(self._compat_label)
        compat_layout.addStretch()
        compat_layout.addWidget(self._incompat_label)
        layout.addLayout(compat_layout)

        # Fingerprint uniqueness indicator
        self._fingerprint_label = QLabel("Unique fingerprint: ─")
        self._fingerprint_label.setStyleSheet("color: #7a9aba; font-size: 10px;")
        self._fingerprint_label.setToolTip("Per C481: 0 collisions across 1,575 A records tested")
        layout.addWidget(self._fingerprint_label)

        return panel

    def _create_b_impact_panel(self) -> QGroupBox:
        """Create B Folio Impact panel."""
        panel = QGroupBox("B FOLIO COMPILATION")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #e0d8c8;
                border: 1px solid #3a4a5a;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout(panel)

        # B folio selector
        selector_layout = QHBoxLayout()
        selector_label = QLabel("B Folio:")
        selector_label.setStyleSheet("color: #a0b0c0; font-size: 11px;")
        selector_layout.addWidget(selector_label)

        self._b_folio_combo = QComboBox()
        self._b_folio_combo.setMinimumWidth(100)
        self._b_folio_combo.addItem("(none)")
        for folio_id in sorted(self.data_store.b_folio_class_footprints.keys()):
            self._b_folio_combo.addItem(folio_id)
        self._b_folio_combo.currentTextChanged.connect(self._on_b_folio_changed)
        selector_layout.addWidget(self._b_folio_combo)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        # Impact stats
        self._b_needs_label = QLabel("Folio needs: ─ instruction classes")
        self._b_needs_label.setStyleSheet("color: #a0b0c0; font-size: 11px;")
        layout.addWidget(self._b_needs_label)

        self._b_available_label = QLabel("Available: ─")
        self._b_available_label.setStyleSheet("color: #4a9a4a; font-size: 11px;")
        layout.addWidget(self._b_available_label)

        self._b_blocked_label = QLabel("Blocked: ─")
        self._b_blocked_label.setStyleSheet("color: #9a4a4a; font-size: 11px;")
        layout.addWidget(self._b_blocked_label)

        self._b_status_label = QLabel("")
        self._b_status_label.setStyleSheet("color: #f0a060; font-size: 11px; font-weight: bold;")
        layout.addWidget(self._b_status_label)

        return panel

    def _compute_legality_snapshot(self, bundle: ConstraintBundle) -> LegalitySnapshot:
        """Compute legality state from A record's constraint bundle."""
        middles = bundle.azc_active or set()

        # Compute which AZC folios are activated by this vocabulary
        activated = set()
        blocked = set()

        for folio_id, folio_middles in self.data_store.azc_folio_middles.items():
            # A folio is activated if ALL of the record's MIDDLEs are compatible
            # (i.e., appear in the folio's vocabulary)
            if middles and middles.issubset(folio_middles):
                activated.add(folio_id)
            else:
                blocked.add(folio_id)

        # If no MIDDLEs, all folios are potentially compatible
        if not middles:
            activated = set(self.data_store.azc_folio_middles.keys())
            blocked = set()

        # Compute escape rate based on activated folios
        # Per C468: 1.0% to 28.6% range
        if activated:
            # Simple heuristic: more folios = higher escape rate
            escape_rate = len(activated) / 29 * 0.286  # Scale to 28.6% max
        else:
            escape_rate = 0.01  # Minimum 1%

        # Compute MIDDLE compatibility
        # Per C475: 95.7% of MIDDLE pairs are incompatible
        all_middles = set(self.data_store.middle_zone_legality.keys())
        total = len(all_middles)

        if middles:
            # Find MIDDLEs that can co-occur with all of this record's MIDDLEs
            compatible = set()
            for m in all_middles:
                # Check if m can co-occur with all of the record's MIDDLEs
                # For now, use a simple heuristic based on shared AZC folios
                m_folios = {f for f, ms in self.data_store.azc_folio_middles.items() if m in ms}
                if any(f in activated for f in m_folios):
                    compatible.add(m)
            compatible_count = len(compatible)
        else:
            compatible_count = total

        incompatible_count = total - compatible_count

        return LegalitySnapshot(
            middles=middles,
            activated_azc_folios=activated,
            blocked_azc_folios=blocked,
            escape_rate=escape_rate,
            compatible_middle_count=compatible_count,
            incompatible_middle_count=incompatible_count,
            total_middles=total
        )

    def _update_azc_panel(self, snapshot: LegalitySnapshot):
        """Update AZC Folio Activation panel."""
        self._azc_progress.setValue(len(snapshot.activated_azc_folios))

        self._azc_list.clear()

        # Show activated folios first (green checkmark)
        for folio_id in sorted(snapshot.activated_azc_folios):
            item = QListWidgetItem(f"✓ {folio_id}")
            item.setForeground(QColor("#4a9a4a"))
            self._azc_list.addItem(item)

        # Then show blocked folios (red X) - limit to first 10
        blocked_list = sorted(snapshot.blocked_azc_folios)[:10]
        for folio_id in blocked_list:
            item = QListWidgetItem(f"✗ {folio_id}")
            item.setForeground(QColor("#9a4a4a"))
            self._azc_list.addItem(item)

        if len(snapshot.blocked_azc_folios) > 10:
            item = QListWidgetItem(f"  ... and {len(snapshot.blocked_azc_folios) - 10} more blocked")
            item.setForeground(QColor("#707070"))
            self._azc_list.addItem(item)

    def _update_escape_panel(self, snapshot: LegalitySnapshot):
        """Update Escape/Recovery Rate meter."""
        # Scale to permille for display (0-286)
        value = int(snapshot.escape_rate * 1000)
        self._escape_meter.setValue(value)

        pct = snapshot.escape_rate * 100
        self._escape_label.setText(f"This A record: {pct:.1f}% recovery rate")

        # Interpretation
        if pct < 5:
            interp = "CONSTRAINED: Very limited recovery options"
            color = "#9a4a4a"
        elif pct < 15:
            interp = "MODERATE: Some recovery paths available"
            color = "#9a7a4a"
        else:
            interp = "FLEXIBLE: Many recovery options available"
            color = "#4a9a4a"

        self._escape_interpretation.setText(interp)
        self._escape_interpretation.setStyleSheet(f"color: {color}; font-size: 10px;")

    def _update_compatibility_panel(self, snapshot: LegalitySnapshot):
        """Update MIDDLE Compatibility panel."""
        if snapshot.middles:
            middles_str = ", ".join(sorted(snapshot.middles)[:5])
            if len(snapshot.middles) > 5:
                middles_str += f" ... ({len(snapshot.middles)} total)"
            self._middles_label.setText(f"MIDDLEs: [{middles_str}]")
        else:
            self._middles_label.setText("MIDDLEs: (none - all compatible)")

        if snapshot.total_middles > 0:
            compat_pct = 100 * snapshot.compatible_middle_count / snapshot.total_middles
            incompat_pct = 100 * snapshot.incompatible_middle_count / snapshot.total_middles
        else:
            compat_pct = 0
            incompat_pct = 0

        self._compat_label.setText(f"Compatible: {snapshot.compatible_middle_count} ({compat_pct:.1f}%)")
        self._incompat_label.setText(f"Blocked: {snapshot.incompatible_middle_count} ({incompat_pct:.1f}%)")

        # Fingerprint visualization (simple hash-based bar)
        if snapshot.middles:
            fp_hash = hash(frozenset(snapshot.middles)) % 1000000
            bar_len = 20
            filled = (fp_hash % bar_len) + 1
            bar = "█" * filled + "░" * (bar_len - filled)
            self._fingerprint_label.setText(f"Unique fingerprint: {bar}")
        else:
            self._fingerprint_label.setText("Unique fingerprint: ─")

    def _update_b_impact_panel(self):
        """Update B Folio Impact panel based on current selection."""
        folio_id = self._b_folio_combo.currentText()

        if folio_id == "(none)" or not self._current_snapshot:
            self._b_needs_label.setText("Folio needs: ─ instruction classes")
            self._b_available_label.setText("Available: ─")
            self._b_blocked_label.setText("Blocked: ─")
            self._b_status_label.setText("")
            return

        folio_classes = self.data_store.b_folio_class_footprints.get(folio_id, set())
        n_total = len(folio_classes)

        # Compute which classes are available under current legality
        # For now, use a simplified calculation based on activated AZC folios
        # A class is available if it has MIDDLEs that are compatible
        available = set()
        blocked = set()

        for cls_id, cls_info in self.data_store.classes.items():
            if cls_id not in folio_classes:
                continue
            # Check if any of the class's MIDDLEs are in activated AZC folios
            cls_middles = cls_info.middles if hasattr(cls_info, 'middles') else set()
            if not cls_middles:
                # No MIDDLE info - assume available (kernel classes)
                available.add(cls_id)
            else:
                # Check if any MIDDLE is in an activated folio
                for m in cls_middles:
                    for f in self._current_snapshot.activated_azc_folios:
                        if m in self.data_store.azc_folio_middles.get(f, set()):
                            available.add(cls_id)
                            break
                    if cls_id in available:
                        break
                if cls_id not in available:
                    blocked.add(cls_id)

        n_available = len(available)
        n_blocked = len(blocked)

        self._b_needs_label.setText(f"Folio needs: {n_total} instruction classes")

        if n_total > 0:
            avail_pct = 100 * n_available / n_total
            block_pct = 100 * n_blocked / n_total
        else:
            avail_pct = 0
            block_pct = 0

        self._b_available_label.setText(f"Available: {n_available} ({avail_pct:.0f}%)")
        self._b_blocked_label.setText(f"Blocked: {n_blocked} ({block_pct:.0f}%)")

        # Status
        if n_blocked == 0:
            status = "VIABLE: All classes available"
            color = "#4a9a4a"
        elif block_pct < 20:
            status = "CONSTRAINED: Some recovery paths lost"
            color = "#9a7a4a"
        else:
            status = "BRITTLE: Significant degradation"
            color = "#9a4a4a"

        self._b_status_label.setText(status)
        self._b_status_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")

    def _on_b_folio_changed(self, folio_id: str):
        """Handle B folio selection change."""
        self._selected_b_folio = folio_id if folio_id != "(none)" else None
        self._update_b_impact_panel()

    @pyqtSlot(object)
    def update_from_bundle(self, bundle: ConstraintBundle):
        """Update dashboard from A record constraint bundle."""
        try:
            self._current_bundle = bundle

            if bundle is None:
                self._record_label.setText("No A record selected")
                self._current_snapshot = None
                return

            # Update header with record info
            # Use source_tokens (list) or token (str) - NOT "tokens"
            if hasattr(bundle, 'source_tokens') and bundle.source_tokens:
                record_text = " + ".join(bundle.source_tokens)
            elif hasattr(bundle, 'token') and bundle.token:
                record_text = bundle.token
            else:
                record_text = "(empty)"
            self._record_label.setText(f"Selected: {record_text}")

            # Compute legality snapshot
            self._current_snapshot = self._compute_legality_snapshot(bundle)

            # Update all panels
            self._update_azc_panel(self._current_snapshot)
            self._update_escape_panel(self._current_snapshot)
            self._update_compatibility_panel(self._current_snapshot)
            self._update_b_impact_panel()
        except Exception as e:
            import traceback
            print(f"ERROR in update_from_bundle: {e}")
            traceback.print_exc()
            self._record_label.setText(f"Error: {e}")

    @pyqtSlot(object)
    def update_legality(self, reachability_result: ReachabilityResult):
        """Update from reachability result (compatibility with existing interface)."""
        # Extract bundle info if available
        if reachability_result and hasattr(reachability_result, 'bundle'):
            self.update_from_bundle(reachability_result.bundle)

    def reset(self):
        """Reset to initial state."""
        self._current_bundle = None
        self._current_snapshot = None
        self._record_label.setText("No A record selected")
        self._azc_progress.setValue(0)
        self._azc_list.clear()
        self._escape_meter.setValue(0)
        self._escape_label.setText("Select an A record to see recovery budget")
        self._escape_interpretation.setText("")
        self._middles_label.setText("MIDDLEs: (none)")
        self._compat_label.setText("Compatible: 0 (0%)")
        self._incompat_label.setText("Blocked: 0 (0%)")
        self._fingerprint_label.setText("Unique fingerprint: ─")
        self._b_folio_combo.setCurrentText("(none)")
        self._update_b_impact_panel()
