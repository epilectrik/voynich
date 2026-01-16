"""
AZC Folio Animator - Main Entry Point

Visualizes constraint field acting on single Currier A line bundles.
Core principle: "A constraint field that acts on a single attempted specification."

Key constraints respected:
- C233: A = LINE_ATOMIC
- C442: Disallowed combinations never occur (vanishing)
- C473: Currier A Entry Defines a Constraint Bundle
- C475: MIDDLE ATOMIC INCOMPATIBILITY
"""
import sys
from pathlib import Path

# Add project root to path
_project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont


def load_voynich_font() -> QFont:
    """Load the VoynichEVA font."""
    font_path = Path(__file__).parent / "fonts" / "VoynichEVA.ttf"

    if font_path.exists():
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                font = QFont(families[0], 14)
                return font

    # Fallback
    return QFont("Courier New", 12)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("AZC Folio Animator")

    # Load font
    voynich_font = load_voynich_font()

    # Import here to avoid circular imports
    from apps.azc_folio_animator.ui.main_window import MainWindow

    window = MainWindow(voynich_font)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
