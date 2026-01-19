"""
Control Loop Visualization Panel

Visualizes B grammar as role-level reachability graph.
Shows legal transitions under AZC legality fields.

Per C121: 49 classes, universal grammar.
Per C171: Closed-loop control only (not stepwise procedure).
Per C411: ~40% reducible, justifying role collapse.
Per C444/C468: Vanishing semantics - illegal paths absent.

This shows reachable transition topology, not execution sequence.
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QButtonGroup, QWidget, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSlot

from core.data_loader import get_data_store
from core.role_classifier import RoleClassifier
from core.reachability_computer import ReachabilityComputer
from core.reachability_engine import ReachabilityResult

from .reachability_view import ReachabilityView
from .hazard_summary_panel import HazardSummaryPanel
from .legality_metrics_panel import LegalityMetricsPanel


class ControlLoopPanel(QFrame):
    """
    Main panel for Control Loop Visualization.

    Shows role-level reachability graph with:
    - Circular layout (emphasizes recurrence, not flow)
    - Directed edges (C111: 65% asymmetric)
    - Vanishing semantics (illegal = absent)
    - Hazard sidebar
    - Metrics footer
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_store = get_data_store()
        self.classifier = RoleClassifier(self.data_store)
        self.computer = ReachabilityComputer(self.data_store, self.classifier)

        self._current_reachable_classes = None
        # Stage 2 compilation state
        self._selected_folio = None
        self._selected_folio_classes = None
        self._setup_ui()

    def _setup_ui(self):
        """Build the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header with title and mode toggle
        header_layout = QHBoxLayout()

        self._title_label = QLabel("COMPILED REACHABILITY VIEW")
        self._title_label.setStyleSheet("color: #e0d8c8; font-weight: bold;")
        self._title_label.setToolTip(
            "Shows legal transition topology under AZC legality.\n"
            "Per C171: This is recurrent viability, not procedure.\n"
            "Per C391: Direction indicates asymmetry, not sequence.\n"
            "Per C444: Illegal paths are absent (vanishing semantics)."
        )
        header_layout.addWidget(self._title_label)

        # Folio info label (shown when a B folio is selected for Stage 2)
        self._folio_info_label = QLabel("")
        self._folio_info_label.setStyleSheet(
            "color: #f0a060; font-weight: bold; padding-left: 12px;"
        )
        header_layout.addWidget(self._folio_info_label)

        header_layout.addStretch()

        # Mode toggle
        self._mode_group = QButtonGroup(self)

        self._compiled_radio = QRadioButton("Compiled View")
        self._compiled_radio.setStyleSheet("color: #a0b0c0; font-size: 10px;")
        self._compiled_radio.setToolTip("Show only legal transitions under AZC")
        self._compiled_radio.setChecked(True)
        self._mode_group.addButton(self._compiled_radio, 0)
        header_layout.addWidget(self._compiled_radio)

        self._baseline_radio = QRadioButton("Baseline Grammar")
        self._baseline_radio.setStyleSheet("color: #a0b0c0; font-size: 10px;")
        self._baseline_radio.setToolTip("Show all legal transitions (AZC ignored)")
        self._mode_group.addButton(self._baseline_radio, 1)
        header_layout.addWidget(self._baseline_radio)

        self._mode_group.buttonClicked.connect(self._on_mode_changed)

        layout.addLayout(header_layout)

        # B Folio selector row (separate row for clarity)
        folio_row = QHBoxLayout()
        folio_label = QLabel("B Folio:")
        folio_label.setStyleSheet("color: #a0b0c0; font-size: 11px;")
        folio_row.addWidget(folio_label)

        self._folio_combo = QComboBox()
        self._folio_combo.setMinimumWidth(100)
        self._folio_combo.setMaximumWidth(150)
        self._folio_combo.setToolTip("Select a B folio to see Stage 2 compilation")
        self._folio_combo.addItem("(none)")
        # Populate with B folios
        for folio_id in sorted(self.data_store.b_folio_class_footprints.keys()):
            self._folio_combo.addItem(folio_id)
        self._folio_combo.currentTextChanged.connect(self._on_folio_combo_changed)
        folio_row.addWidget(self._folio_combo)
        folio_row.addStretch()

        layout.addLayout(folio_row)

        # Main content: view + sidebar
        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)

        # Reachability view (main area)
        self.reachability_view = ReachabilityView(self.data_store)
        content_layout.addWidget(self.reachability_view, stretch=3)

        # Hazard sidebar
        self.hazard_panel = HazardSummaryPanel()
        self.hazard_panel.setMaximumWidth(160)
        content_layout.addWidget(self.hazard_panel, stretch=1)

        layout.addLayout(content_layout, stretch=1)

        # Metrics footer
        self.metrics_panel = LegalityMetricsPanel()
        layout.addWidget(self.metrics_panel)

        # Initial update
        self._update_display()

    def _on_mode_changed(self):
        """Handle mode toggle."""
        if self._baseline_radio.isChecked():
            # Show baseline (all legal)
            self.reachability_view.reset()
            self._update_display(baseline=True)
        else:
            # Show compiled (AZC-constrained)
            if self._current_reachable_classes is not None:
                self.reachability_view.update_reachability(self._current_reachable_classes)
            self._update_display()

        # Reapply folio coloring if a B folio is selected
        if self._selected_folio:
            self._reapply_folio_compilation()

    def _update_display(self, baseline=False):
        """Update all display components."""
        if baseline:
            reachable = None
        else:
            reachable = self._current_reachable_classes

        # Update metrics
        reachability = self.computer.compute_reachability(reachable)
        self.metrics_panel.update_metrics(reachability)

        # Update hazard status
        hazard_status = self.computer.compute_hazard_status(reachable)
        self.hazard_panel.update_status(hazard_status)

    @pyqtSlot(object)
    def update_legality(self, reachability_result: ReachabilityResult):
        """
        Update view based on AZC legality field.

        Called when A folio selection changes.

        Args:
            reachability_result: Result from reachability engine
        """
        if reachability_result is None:
            self._current_reachable_classes = None
            self.reachability_view.reset()
        else:
            grammar = reachability_result.grammar_state
            self._current_reachable_classes = grammar.reachable_classes
            self.reachability_view.update_reachability(grammar.reachable_classes)

        # Only update compiled view if in compiled mode
        if self._compiled_radio.isChecked():
            self._update_display()

        # Reapply folio coloring if a B folio is selected
        if self._selected_folio:
            self._reapply_folio_compilation()

    def _reapply_folio_compilation(self):
        """Reapply folio-specific coloring after ambient view updates."""
        if not self._selected_folio or not self._selected_folio_classes:
            return

        # Recompute surviving/pruned with current legality
        if self._current_reachable_classes is not None:
            surviving = self._selected_folio_classes & self._current_reachable_classes
            pruned = self._selected_folio_classes - surviving
        else:
            surviving = self._selected_folio_classes
            pruned = set()

        # Reapply visualization
        self.reachability_view.show_folio_compilation(
            self._selected_folio,
            self._selected_folio_classes,
            surviving,
            pruned
        )

        # Update info labels
        n_total = len(self._selected_folio_classes)
        n_surviving = len(surviving)
        regime = self.data_store.regime_assignments.get(self._selected_folio, "")
        regime_str = f" ({regime})" if regime else ""
        kernel_status = self._check_kernel_integrity(surviving, pruned)
        folio_atomic = self._selected_folio_classes & self.data_store.atomic_hazard_classes
        folio_decomp = self._selected_folio_classes & self.data_store.decomposable_hazard_classes
        decomp_surviving = folio_decomp & surviving
        brittleness = self._compute_brittleness(surviving, pruned, len(decomp_surviving), len(folio_atomic))

        self._title_label.setText(f"COMPILED: {self._selected_folio}{regime_str}")
        pct = 100 * n_surviving / n_total if n_total > 0 else 0
        kernel_str = "INTACT" if kernel_status else "BROKEN"
        self._folio_info_label.setText(
            f"Classes: {n_surviving}/{n_total} ({pct:.0f}%) | "
            f"Kernel: {kernel_str} | "
            f"Hazards: {len(folio_atomic)} atomic, {len(decomp_surviving)}/{len(folio_decomp)} decomp | "
            f"{brittleness}"
        )

    def reset(self):
        """Reset to baseline state."""
        self._current_reachable_classes = None
        self._selected_folio = None
        self._selected_folio_classes = None
        self._folio_info_label.setText("")
        self._title_label.setText("COMPILED REACHABILITY VIEW")
        # Reset dropdown without triggering handler
        self._folio_combo.blockSignals(True)
        self._folio_combo.setCurrentText("(none)")
        self._folio_combo.blockSignals(False)
        self.reachability_view.reset()
        self._baseline_radio.setChecked(True)
        self._update_display(baseline=True)

    def _on_folio_combo_changed(self, folio_id: str):
        """Handle B folio selection from dropdown."""
        if folio_id == "(none)" or not folio_id:
            # Reset to ambient view
            self._selected_folio = None
            self._selected_folio_classes = None
            self._folio_info_label.setText("")
            self._title_label.setText("COMPILED REACHABILITY VIEW")
            self.reachability_view.reset()
            if self._compiled_radio.isChecked() and self._current_reachable_classes:
                self.reachability_view.update_reachability(self._current_reachable_classes)
            self._update_display()
            return

        # Get folio classes and apply Stage 2 compilation
        folio_classes = self.data_store.b_folio_class_footprints.get(folio_id, set())
        if folio_classes:
            # Create a minimal folio_result-like object (set_selected_folio needs it)
            self.set_selected_folio(folio_id, None)

    def set_selected_folio(self, folio_id: str, folio_result):
        """
        Show Stage 2 compilation for a specific B folio.

        Stage 2 answers: "How does THIS program execute within the ambient legality field?"

        Per C171: B folios ARE programs (closed-loop control).
        This shows the compiled program state, not just binary reachability.

        Args:
            folio_id: The B folio identifier (e.g., "f33v")
            folio_result: FolioReachability from reachability engine
        """
        self._selected_folio = folio_id
        self._selected_folio_classes = self.data_store.b_folio_class_footprints.get(folio_id, set())

        # Compute Stage 2 compilation metrics
        if self._current_reachable_classes is not None:
            surviving = self._selected_folio_classes & self._current_reachable_classes
            pruned = self._selected_folio_classes - surviving
        else:
            surviving = self._selected_folio_classes
            pruned = set()

        n_total = len(self._selected_folio_classes)
        n_surviving = len(surviving)
        n_pruned = len(pruned)

        # Get REGIME
        regime = self.data_store.regime_assignments.get(folio_id, "")
        regime_str = f" ({regime})" if regime else ""

        # Compute kernel integrity
        kernel_status = self._check_kernel_integrity(surviving, pruned)

        # Compute hazard status for this folio
        folio_atomic = self._selected_folio_classes & self.data_store.atomic_hazard_classes
        folio_decomp = self._selected_folio_classes & self.data_store.decomposable_hazard_classes
        decomp_surviving = folio_decomp & surviving
        decomp_pruned = folio_decomp - surviving

        # Compute brittleness
        brittleness = self._compute_brittleness(surviving, pruned, len(decomp_surviving), len(folio_atomic))

        # Update title with folio info
        self._title_label.setText(f"COMPILED: {folio_id}{regime_str}")

        # Update info label with metrics
        pct = 100 * n_surviving / n_total if n_total > 0 else 0
        kernel_str = "INTACT" if kernel_status else "BROKEN"
        self._folio_info_label.setText(
            f"Classes: {n_surviving}/{n_total} ({pct:.0f}%) | "
            f"Kernel: {kernel_str} | "
            f"Hazards: {len(folio_atomic)} atomic, {len(decomp_surviving)}/{len(folio_decomp)} decomp | "
            f"{brittleness}"
        )

        # Update visualization with folio-specific coloring
        self.reachability_view.show_folio_compilation(
            folio_id,
            self._selected_folio_classes,
            surviving,
            pruned
        )

        # Update hazard panel with folio-specific status
        hazard_status = self.computer.compute_hazard_status(
            self._current_reachable_classes,
            folio_classes=self._selected_folio_classes
        )
        self.hazard_panel.update_status(hazard_status)

    def _check_kernel_integrity(self, surviving: set, pruned: set) -> bool:
        """
        Check if the kernel backbone (k-h-e) survives compilation.

        Per C089: Kernel = {k, h, e} operators.
        Per C105: e = STABILITY_ANCHOR with 54.7% recovery paths.
        Per C107: Kernel nodes are boundary-adjacent to hazards.

        If any kernel-related class is pruned, the program may become brittle.
        """
        # For now, return True if no kernel-related classes are pruned
        # A more sophisticated check would look at specific k/h/e class IDs
        # The kernel classes are atomic, so they should always survive
        kernel_protection = self.data_store.kernel_classes
        kernel_in_folio = self._selected_folio_classes & kernel_protection
        kernel_surviving = kernel_in_folio & surviving
        return kernel_surviving == kernel_in_folio

    def _compute_brittleness(self, surviving: set, pruned: set,
                              n_decomp_active: int, n_atomic: int) -> str:
        """
        Compute brittleness indicator.

        Per C458: Recovery should be FREE (high variance), hazard should be CLAMPED.
        If too many recovery options are pruned while hazards remain,
        the program becomes brittle.
        """
        n_surviving = len(surviving)
        n_pruned = len(pruned)
        n_total = n_surviving + n_pruned

        if n_total == 0:
            return "N/A"

        # Simple heuristic: >20% pruned with active hazards = brittle
        pct_pruned = n_pruned / n_total
        has_hazards = n_decomp_active > 0 or n_atomic > 0

        if pct_pruned > 0.3 and has_hazards:
            return "BRITTLE"
        elif pct_pruned > 0.15 and has_hazards:
            return "CONSTRAINED"
        else:
            return "VIABLE"
