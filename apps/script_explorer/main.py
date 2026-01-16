#!/usr/bin/env python3
"""
Voynich Script Explorer

A constraint-compliant script exploration tool for the Voynich Manuscript.
Visualizes ONLY frozen/validated findings (Tier 0-2) from the 411+ constraints.

This tool shows:
- Manuscript transcription with token highlighting
- Morphological segmentation (prefix/core/suffix)
- Instruction class and role annotations
- Searchable constraint browser

This tool does NOT show:
- Speculative apparatus interpretations
- Kernel effect meanings
- Operational semantics

Usage:
    python main.py

Requirements:
    - Python 3.11+
    - PyQt5
"""

import sys
from pathlib import Path

# Add app directory to path
APP_DIR = Path(__file__).parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase

from ui.main_window import MainWindow


def main():
    """Application entry point."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # Load Voynich font for glyph display
    font_path = (APP_DIR / "fonts" / "VoynichEVA.ttf").resolve()
    if font_path.exists():
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            print(f"Loaded Voynich font: {families}")
        else:
            print(f"Warning: Failed to load Voynich font from {font_path}")
    else:
        print(f"Warning: Voynich font not found at {font_path}")

    # Set application metadata
    app.setApplicationName("Voynich Script Explorer")
    app.setOrganizationName("Voynich Project")

    # Set default font
    font = QFont("Consolas", 10)
    app.setFont(font)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
