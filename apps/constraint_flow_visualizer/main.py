#!/usr/bin/env python3
"""
Constraint Flow Visualizer - Main Entry Point.

A control-system visualizer that demonstrates the A→AZC→B pipeline
as option space contraction under AZC legality fields.

Per the model:
> Currier A specifies constraint bundles (what must not be confused).
> AZC projects those bundles into position-indexed legality fields.
> Currier B executes blind grammar within the shrinking reachable space.
>
> No semantics. No branching. No lookup.
> Grammar unchanged. Option space contracts.

Usage:
    cd apps/constraint_flow_visualizer
    python main.py
"""

import sys
from pathlib import Path

# Add the app directory to the path for imports
APP_DIR = Path(__file__).parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from PyQt5.QtWidgets import QApplication

# Now use absolute imports from the app root
from core.constraint_bundle import compute_bundle, ConstraintBundle
from core.azc_projection import project_bundle
from core.reachability_engine import compute_reachability
from core.data_loader import get_data_store


def main():
    """Launch the Constraint Flow Visualizer."""
    # Pre-load data
    print("Loading data...")
    data_store = get_data_store()
    print(f"  {len(data_store.classes)} instruction classes")
    print(f"  {len(data_store.azc_folios)} AZC folios")
    print("Data loaded.")

    app = QApplication(sys.argv)
    app.setApplicationName("Constraint Flow Visualizer")
    app.setOrganizationName("Voynich Analysis")

    # Import main window after QApplication is created
    from ui.main_window import MainWindow

    window = MainWindow()
    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
