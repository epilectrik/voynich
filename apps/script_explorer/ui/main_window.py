"""
Main Window - Voynich Script Explorer

A constraint-compliant script exploration tool that visualizes
ONLY frozen/validated findings (Tier 0-2).

Layout:
- Left: Folio browser
- Center: Transcription with token highlighting
- Right: Constraint browser
- Bottom: Folio stats
"""

from typing import Optional, List
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QListWidget, QListWidgetItem, QFrame, QStatusBar,
    QCheckBox, QGroupBox, QRadioButton, QButtonGroup, QTextEdit,
    QPushButton, QApplication
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
    from ui.folio_viewer import (
        FolioViewer, ViewMode, segment_word, segment_word_4component, get_token_classification,
        get_kernel_contact, get_token_legality, get_token_instruction_role,
        get_token_prefix_family, get_kernel_affinity, get_link_affinity,
        get_a_marker_family, get_a_sister_pair, get_a_token_role, get_token_primary_system,
        LINK_TOKENS, SYSTEM_MODES, SYSTEM_DEFAULT_MODE, VIEW_MODE_LABELS, SYSTEM_BANNERS,
        MORPHOLOGY_COLORS, KERNEL_AFFINITY_COLORS, LINK_AFFINITY_COLORS,
        B_INSTRUCTION_COLORS, B_POSITION_COLORS, B_KERNEL_CONTACT_COLORS, B_EXECUTION_COLORS,
        A_MARKER_COLORS, A_SISTER_COLORS, A_ROLE_COLORS, AZC_PLACEMENT_COLORS,
        EXTENDED_PREFIX_MAP
    )
    from ui.constraint_panel import ConstraintPanel
    from core.transcription import TranscriptionLoader
    from core.grammar import Grammar
    from parsing.currier_a import (
        parse_currier_a_token, CurrierAParseResult, AStatus, MARKER_FAMILIES,
        A_INFRASTRUCTURE_MINIMAL, EXTENDED_PREFIX_MAP as CURRIER_A_EXTENDED_MAP
    )
except ImportError:
    from .folio_viewer import (
        FolioViewer, ViewMode, segment_word, segment_word_4component, get_token_classification,
        get_kernel_contact, get_token_legality, get_token_instruction_role,
        get_token_prefix_family, get_kernel_affinity, get_link_affinity,
        get_a_marker_family, get_a_sister_pair, get_a_token_role, get_token_primary_system,
        LINK_TOKENS, SYSTEM_MODES, SYSTEM_DEFAULT_MODE, VIEW_MODE_LABELS, SYSTEM_BANNERS,
        MORPHOLOGY_COLORS, KERNEL_AFFINITY_COLORS, LINK_AFFINITY_COLORS,
        B_INSTRUCTION_COLORS, B_POSITION_COLORS, B_KERNEL_CONTACT_COLORS, B_EXECUTION_COLORS,
        A_MARKER_COLORS, A_SISTER_COLORS, A_ROLE_COLORS, AZC_PLACEMENT_COLORS,
        EXTENDED_PREFIX_MAP
    )
    from .constraint_panel import ConstraintPanel
    from ..core.transcription import TranscriptionLoader
    from ..core.grammar import Grammar
    from ..parsing.currier_a import (
        parse_currier_a_token, CurrierAParseResult, AStatus, MARKER_FAMILIES,
        A_INFRASTRUCTURE_MINIMAL, EXTENDED_PREFIX_MAP as CURRIER_A_EXTENDED_MAP
    )


# Color palette
PALETTE = {
    'background': '#12100E',
    'panel': '#1A1612',
    'border': '#3D3428',
    'copper': '#C9A227',
    'copper_dim': '#8B7355',
    'amber': '#FFBF00',
    'parchment': '#D4B896',
}


# Currier classification by folio (from transcription data)
CURRIER_A_FOLIOS = {
    '100r', '100v', '101r1', '101v2', '102r1', '102r2', '102v1', '102v2',
    '10r', '10v', '11r', '11v', '13r', '13v', '14r', '14v', '15r', '15v',
    '16r', '16v', '17r', '17v', '18r', '18v', '19r', '19v', '1r', '1v',
    '20r', '20v', '21r', '21v', '22r', '22v', '23r', '23v', '24r', '24v',
    '25r', '25v', '27r', '27v', '28r', '28v', '29r', '29v', '2r', '2v',
    '30r', '30v', '32r', '32v', '35r', '35v', '36r', '36v', '37r', '37v',
    '38r', '38v', '3r', '3v', '42r', '42v', '44r', '44v', '45r', '45v',
    '47r', '47v', '49r', '49v', '4r', '4v', '51r', '51v', '52r', '52v',
    '53r', '53v', '54r', '54v', '56r', '56v', '58r', '58v', '5r', '5v',
    '6r', '6v', '7r', '7v', '87r', '87v', '88r', '88v', '89r1', '89r2',
    '89v1', '89v2', '8r', '8v', '90r1', '90r2', '90v1', '90v2', '93r', '93v',
    '96r', '96v', '99r', '99v', '9r', '9v'
}

CURRIER_B_FOLIOS = {
    '103r', '103v', '104r', '104v', '105r', '105v', '106r', '106v',
    '107r', '107v', '108r', '108v', '111r', '111v', '112r', '112v',
    '113r', '113v', '114r', '114v', '115r', '115v', '116r', '26r', '26v',
    '31r', '31v', '33r', '33v', '34r', '34v', '39r', '39v', '40r', '40v',
    '41r', '41v', '43r', '43v', '46r', '46v', '48r', '48v', '50r', '50v',
    '55r', '55v', '57r', '66r', '66v', '75r', '75v', '76r', '76v', '77r',
    '77v', '78r', '78v', '79r', '79v', '80r', '80v', '81r', '81v', '82r',
    '82v', '83r', '83v', '84r', '84v', '85r1', '85r2', '85v2', '86v3',
    '86v4', '86v5', '86v6', '94r', '94v', '95r1', '95r2', '95v1', '95v2'
}

AZC_FOLIOS = {
    '116v', '57v', '65r', '65v', '67r1', '67r2', '67v1', '67v2',
    '68r1', '68r2', '68r3', '68v1', '68v2', '68v3', '69r', '69v',
    '70r1', '70r2', '70v1', '70v2', '71r', '71v', '72r1', '72r2',
    '72r3', '72v1', '72v2', '72v3', '73r', '73v'
}

# Colors for Currier types in folio list
CURRIER_COLORS = {
    'A': '#6B8E9B',   # Muted blue-gray
    'B': '#7B9B6B',   # Muted green
    'AZC': '#C9A227', # Copper/gold
}

# =============================================================================
# UI CONFIGURATION FOR GUIDED INSPECTION MODE
# =============================================================================

# View mode groupings for toolbar UI (5 groups)
VIEW_MODE_GROUPS = {
    'Global': [ViewMode.MORPHOLOGY, ViewMode.KERNEL_AFFINITY, ViewMode.LINK_AFFINITY],
    'A': [ViewMode.A_MARKER, ViewMode.A_SISTER, ViewMode.A_ROLE],
    'B': [ViewMode.B_INSTRUCTION, ViewMode.B_POSITION, ViewMode.B_KERNEL_CONTACT, ViewMode.B_EXECUTION],
    'AZC': [ViewMode.AZC_PLACEMENT],
    'Plain': [ViewMode.PLAIN],
}

# Which groups are applicable per Currier system
APPLICABLE_GROUPS = {
    'A': ['Global', 'A', 'Plain'],
    'B': ['Global', 'B', 'Plain'],
    'AZC': ['Global', 'AZC', 'Plain'],
}

# Recommended views per system (shown on folio load)
RECOMMENDED_VIEWS = {
    'A': ['Marker', 'Sister', 'Morph'],
    'B': ['Instr', 'Contact', 'Morph'],
    'AZC': ['Place', 'Morph', 'Affinity'],
}

# Mode to target system mapping (for mismatch detection)
# Global modes have no target system (applicable everywhere)
MODE_TARGET_SYSTEM = {
    ViewMode.A_MARKER: 'A',
    ViewMode.A_SISTER: 'A',
    ViewMode.A_ROLE: 'A',
    ViewMode.A_MULTIPLICITY: 'A',
    ViewMode.B_INSTRUCTION: 'B',
    ViewMode.B_POSITION: 'B',
    ViewMode.B_KERNEL_CONTACT: 'B',
    ViewMode.B_EXECUTION: 'B',
    ViewMode.AZC_PLACEMENT: 'AZC',
    ViewMode.AZC_LEGALITY: 'AZC',
}


class FolioBrowser(QFrame):
    """Simple folio browser list with Currier classification colors."""

    folio_selected = pyqtSignal(str)  # Emits folio ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self._folio_ids: List[str] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        header = QLabel("FOLIOS")
        header.setFont(QFont("Consolas", 10, QFont.Bold))
        header.setStyleSheet(f"color: {PALETTE['copper']};")
        layout.addWidget(header)

        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_selection)
        self._list.setStyleSheet(f"""
            QListWidget {{
                background-color: {PALETTE['panel']};
                color: {PALETTE['parchment']};
                border: 1px solid {PALETTE['border']};
                border-radius: 3px;
            }}
            QListWidget::item:selected {{
                background-color: {PALETTE['border']};
            }}
        """)
        layout.addWidget(self._list)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {PALETTE['background']};
                border: 2px solid {PALETTE['border']};
                border-radius: 5px;
            }}
        """)

    def set_folios(self, folio_ids: List[str]):
        """Set the list of available folios with Currier classification colors."""
        self._folio_ids = folio_ids
        self._list.clear()
        for fid in folio_ids:
            # Determine Currier type
            if fid in CURRIER_A_FOLIOS:
                currier_type = 'A'
                label = f"A  f{fid}"
            elif fid in CURRIER_B_FOLIOS:
                currier_type = 'B'
                label = f"B  f{fid}"
            elif fid in AZC_FOLIOS:
                currier_type = 'AZC'
                label = f"Z  f{fid}"
            else:
                currier_type = 'B'  # Default
                label = f"?  f{fid}"

            item = QListWidgetItem(label)
            item.setForeground(QColor(CURRIER_COLORS[currier_type]))
            self._list.addItem(item)

    def _on_selection(self, current: QListWidgetItem, previous: QListWidgetItem):
        if current:
            # Label format is "A  f1r" or "B  f103r" etc - extract folio ID after 'f'
            text = current.text()
            if 'f' in text:
                folio_id = text.split('f', 1)[1]  # Everything after first 'f'
                self.folio_selected.emit(folio_id)


class MainWindow(QMainWindow):
    """
    Voynich Script Explorer - Main Window

    Constraint-compliant visualization of manuscript text with
    structural annotations traceable to frozen facts.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voynich Script Explorer")
        self.setMinimumSize(1200, 800)

        # Core modules
        self._grammar = Grammar()
        self._transcription_loader = TranscriptionLoader()
        self._current_folio: Optional[str] = None

        self._setup_ui()
        self._apply_styles()
        self._load_data()

    def _setup_ui(self):
        """Set up the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Title bar
        title_bar = self._create_title_bar()
        main_layout.addWidget(title_bar)

        # Main content - three columns
        content_splitter = QSplitter(Qt.Horizontal)

        # LEFT: Folio browser
        self._folio_browser = FolioBrowser()
        self._folio_browser.folio_selected.connect(self._on_folio_selected)
        self._folio_browser.setMaximumWidth(120)
        content_splitter.addWidget(self._folio_browser)

        # CENTER: Transcription viewer (now without detail panel)
        center_panel = self._create_center_panel()
        content_splitter.addWidget(center_panel)

        # RIGHT: Selected token detail panel (moved from center)
        self._detail_panel = self._create_detail_panel()
        content_splitter.addWidget(self._detail_panel)

        # Hidden constraint panel (still needed for constraint lookup)
        self._constraint_panel = ConstraintPanel()
        self._constraint_panel.hide()

        content_splitter.setSizes([100, 700, 350])
        main_layout.addWidget(content_splitter, stretch=1)

        # Status bar
        self._setup_status_bar()

    def _create_title_bar(self) -> QWidget:
        """Create the application title bar."""
        title_bar = QFrame()
        title_bar.setMaximumHeight(50)
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 5, 15, 5)

        title = QLabel("VOYNICH SCRIPT EXPLORER")
        title.setFont(QFont("Consolas", 14, QFont.Bold))
        title.setStyleSheet(f"color: {PALETTE['copper']};")
        layout.addWidget(title)

        layout.addStretch()

        subtitle = QLabel("Constraint-Compliant Visualization (Tier 0-2)")
        subtitle.setFont(QFont("Consolas", 9))
        subtitle.setStyleSheet(f"color: {PALETTE['copper_dim']};")
        layout.addWidget(subtitle)

        title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {PALETTE['panel']};
                border: 2px solid {PALETTE['border']};
                border-radius: 5px;
            }}
        """)
        return title_bar

    def _create_center_panel(self) -> QWidget:
        """Create the center panel with transcription viewer."""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # System banner (dynamic - changes with folio selection)
        self._system_banner = self._create_system_banner('B')
        layout.addWidget(self._system_banner)

        # Toolbar with view mode and glyph toggle
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Folio viewer (takes full height now)
        self._folio_viewer = FolioViewer()
        self._folio_viewer.token_selected.connect(self._on_token_selected)
        layout.addWidget(self._folio_viewer, stretch=1)

        # Stats bar at bottom
        self._stats_label = QLabel("Select a folio to begin")
        self._stats_label.setFont(QFont("Consolas", 9))
        self._stats_label.setStyleSheet(f"color: {PALETTE['amber']}; padding: 5px;")
        layout.addWidget(self._stats_label)

        panel.setStyleSheet(f"background-color: {PALETTE['background']};")
        return panel

    def _create_system_banner(self, system: str) -> QFrame:
        """Create system mode banner with title and description."""
        banner = QFrame()
        banner.setMaximumHeight(50)
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(15, 8, 15, 8)

        title, subtitle = SYSTEM_BANNERS.get(system, ("UNKNOWN SYSTEM", ""))

        # System indicator icon
        system_colors = {
            'A': CURRIER_COLORS['A'],
            'B': CURRIER_COLORS['B'],
            'AZC': CURRIER_COLORS['AZC'],
        }
        color = system_colors.get(system, PALETTE['copper'])

        # Title with colored indicator
        title_label = QLabel(f"[{system}]  {title}")
        title_label.setFont(QFont("Consolas", 11, QFont.Bold))
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)

        layout.addStretch()

        # Subtitle (interpretation guidance)
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Consolas", 9))
        subtitle_label.setStyleSheet(f"color: {PALETTE['copper_dim']};")
        layout.addWidget(subtitle_label)

        banner.setStyleSheet(f"""
            QFrame {{
                background-color: {PALETTE['panel']};
                border: 2px solid {color};
                border-radius: 5px;
            }}
        """)
        return banner

    def _update_system_banner(self, system: str):
        """Update the system banner for the new system."""
        title, subtitle = SYSTEM_BANNERS.get(system, ("UNKNOWN SYSTEM", ""))
        system_colors = {
            'A': CURRIER_COLORS['A'],
            'B': CURRIER_COLORS['B'],
            'AZC': CURRIER_COLORS['AZC'],
        }
        color = system_colors.get(system, PALETTE['copper'])

        # Find and update labels in banner
        layout = self._system_banner.layout()
        if layout:
            # Title is first label
            title_item = layout.itemAt(0)
            if title_item and title_item.widget():
                title_label = title_item.widget()
                title_label.setText(f"[{system}]  {title}")
                title_label.setStyleSheet(f"color: {color};")

            # Subtitle is last label (after stretch)
            subtitle_item = layout.itemAt(layout.count() - 1)
            if subtitle_item and subtitle_item.widget():
                subtitle_label = subtitle_item.widget()
                subtitle_label.setText(subtitle)

        # Update border color
        self._system_banner.setStyleSheet(f"""
            QFrame {{
                background-color: {PALETTE['panel']};
                border: 2px solid {color};
                border-radius: 5px;
            }}
        """)

    def _create_toolbar(self) -> QWidget:
        """Create toolbar with system-aware view mode selector and glyph toggle."""
        self._toolbar = QFrame()
        self._toolbar.setMaximumHeight(40)
        self._toolbar_layout = QHBoxLayout(self._toolbar)
        self._toolbar_layout.setContentsMargins(10, 5, 10, 5)
        self._toolbar_layout.setSpacing(10)

        # View mode label
        view_label = QLabel("View:")
        view_label.setFont(QFont("Consolas", 9, QFont.Bold))
        view_label.setStyleSheet(f"color: {PALETTE['copper']};")
        self._toolbar_layout.addWidget(view_label)

        # Container for dynamic mode buttons - will be rebuilt per system
        self._mode_button_container = QWidget()
        self._mode_button_layout = QHBoxLayout(self._mode_button_container)
        self._mode_button_layout.setContentsMargins(0, 0, 0, 0)
        self._mode_button_layout.setSpacing(8)
        self._toolbar_layout.addWidget(self._mode_button_container)

        # Button group for radio buttons
        self._view_button_group = QButtonGroup(self)
        self._view_button_group.buttonClicked.connect(self._on_view_mode_changed)

        self._toolbar_layout.addStretch()

        # Execution Inspector toggle (B system only)
        self._exec_toggle = QCheckBox("Execution Inspector")
        self._exec_toggle.setStyleSheet(f"""
            QCheckBox {{
                color: {PALETTE['copper']};
                font-family: Consolas;
            }}
            QCheckBox:checked {{
                color: #FF6040;
            }}
        """)
        self._exec_toggle.setToolTip("Enable execution semantics analysis (C357, C371-373). B-system only.")
        self._exec_toggle.toggled.connect(self._on_exec_toggle)
        self._toolbar_layout.addWidget(self._exec_toggle)

        # Separator
        sep_exec = QLabel("|")
        sep_exec.setStyleSheet(f"color: {PALETTE['border']}; padding: 0 5px;")
        self._toolbar_layout.addWidget(sep_exec)

        # Glyph toggle
        self._glyph_toggle = QCheckBox("Voynich Glyphs")
        self._glyph_toggle.setStyleSheet(f"""
            QCheckBox {{
                color: {PALETTE['copper']};
                font-family: Consolas;
            }}
        """)
        self._glyph_toggle.toggled.connect(self._on_glyph_toggle)
        self._toolbar_layout.addWidget(self._glyph_toggle)

        self._toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {PALETTE['panel']};
                border: 1px solid {PALETTE['border']};
                border-radius: 3px;
            }}
        """)

        # Initialize for B system (default)
        self._current_system = 'B'
        self._rebuild_mode_buttons('B')

        return self._toolbar

    def _get_folio_system(self, folio_id: str) -> str:
        """Return 'A', 'B', or 'AZC' for the given folio."""
        if folio_id in CURRIER_A_FOLIOS:
            return 'A'
        elif folio_id in AZC_FOLIOS:
            return 'AZC'
        else:
            return 'B'  # Default

    def _rebuild_mode_buttons(self, system: str):
        """Rebuild mode buttons for the specified Currier system.

        Shows ALL 14 modes in 5 visual groups. Non-applicable groups are
        de-emphasized (dimmed) but still clickable for cross-system inspection.

        Groups: Global | A | B | AZC | Plain
        """
        # Clear existing buttons from group and layout
        for button in self._view_button_group.buttons():
            self._view_button_group.removeButton(button)

        # Clear layout
        while self._mode_button_layout.count() > 0:
            item = self._mode_button_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get default mode and applicable groups for this system
        default_mode = SYSTEM_DEFAULT_MODE.get(system, ViewMode.PLAIN)
        applicable = APPLICABLE_GROUPS.get(system, ['Global', 'Plain'])

        # Define display order for groups
        group_order = ['Global', 'A', 'B', 'AZC', 'Plain']

        first_group = True
        for group_name in group_order:
            modes = VIEW_MODE_GROUPS.get(group_name, [])
            if not modes:
                continue

            # Check if this group is applicable to current system
            is_applicable = group_name in applicable

            # Add separator between groups (except before first)
            if not first_group:
                sep = QLabel("|")
                sep.setStyleSheet(f"color: {PALETTE['border']}; padding: 0 3px;")
                self._mode_button_layout.addWidget(sep)
            first_group = False

            # Add group label for system-specific groups
            if group_name not in ['Global', 'Plain']:
                group_label = QLabel(f"{group_name}:")
                group_color = PALETTE['parchment'] if is_applicable else PALETTE['copper_dim']
                group_label.setStyleSheet(f"color: {group_color}; font-family: Consolas; font-size: 11px; padding-right: 2px;")
                self._mode_button_layout.addWidget(group_label)

            # Add mode buttons for this group
            for mode in modes:
                label, tooltip = VIEW_MODE_LABELS.get(mode, (mode.name, None))
                radio = QRadioButton(label)

                # Visual treatment: applicable = bright, non-applicable = dimmed
                if is_applicable:
                    if group_name == 'Plain':
                        text_color = PALETTE['copper_dim']
                    elif group_name == 'Global':
                        text_color = PALETTE['parchment']
                    else:
                        text_color = PALETTE['amber']  # System-specific = amber
                else:
                    text_color = '#5A5550'  # Dimmed but visible

                radio.setStyleSheet(f"""
                    QRadioButton {{
                        color: {text_color};
                        font-family: Consolas;
                        font-size: 12px;
                    }}
                    QRadioButton::indicator {{ width: 14px; height: 14px; }}
                """)

                if tooltip:
                    # Add applicability hint to tooltip for non-applicable modes
                    if not is_applicable:
                        tooltip = f"{tooltip}\n(Not applicable to {system} folios - tokens will be transparent)"
                    radio.setToolTip(tooltip)

                if mode == default_mode:
                    radio.setChecked(True)

                self._view_button_group.addButton(radio, mode.value)
                self._mode_button_layout.addWidget(radio)

        # Store current mode - use default for this system
        self._current_view_mode = default_mode
        # Only set view mode if folio_viewer exists (not during initial construction)
        if hasattr(self, '_folio_viewer'):
            self._folio_viewer.set_view_mode(default_mode)

    def _create_detail_panel(self) -> QWidget:
        """Create the selected token detail panel (right side, full height)."""
        panel = QFrame()
        panel.setMinimumWidth(300)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        header = QLabel("SELECTED TOKEN")
        header.setFont(QFont("Consolas", 11, QFont.Bold))
        header.setStyleSheet(f"color: {PALETTE['copper']};")
        layout.addWidget(header)

        subheader = QLabel("Click any token to analyze | Select text to copy")
        subheader.setFont(QFont("Consolas", 8))
        subheader.setStyleSheet(f"color: {PALETTE['copper_dim']};")
        layout.addWidget(subheader)

        # === Buttons row ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self._copy_all_btn = QPushButton("Copy All Tokens")
        self._copy_all_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['copper_dim']};
                color: {PALETTE['background']};
                padding: 4px 8px;
                border: 1px solid {PALETTE['border']};
                border-radius: 3px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: {PALETTE['copper']};
            }}
        """)
        self._copy_all_btn.clicked.connect(self._on_copy_all_tokens)
        buttons_layout.addWidget(self._copy_all_btn)

        self._copy_selected_btn = QPushButton("Copy Selected")
        self._copy_selected_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['copper_dim']};
                color: {PALETTE['background']};
                padding: 4px 8px;
                border: 1px solid {PALETTE['border']};
                border-radius: 3px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: {PALETTE['copper']};
            }}
        """)
        self._copy_selected_btn.clicked.connect(self._on_copy_selected)
        buttons_layout.addWidget(self._copy_selected_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Use QTextEdit for selectable/copyable text (full height)
        self._detail_text = QTextEdit()
        self._detail_text.setReadOnly(True)
        self._detail_text.setFont(QFont("Consolas", 10))
        self._detail_text.setPlainText("Click a token to view details...")
        self._detail_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {PALETTE['background']};
                color: {PALETTE['parchment']};
                border: 1px solid {PALETTE['border']};
                border-radius: 3px;
                padding: 10px;
            }}
        """)
        layout.addWidget(self._detail_text, stretch=1)

        # === Legend Panel (UI-only, never copied) ===
        self._legend_panel = self._create_legend_panel()
        layout.addWidget(self._legend_panel)

        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {PALETTE['panel']};
                border: 2px solid {PALETTE['border']};
                border-radius: 5px;
            }}
        """)
        return panel

    def _create_legend_panel(self) -> QFrame:
        """Create fixed colored legend panel below detail text.

        IMPORTANT: This panel is UI-only and is NEVER included in clipboard output.
        This prevents color and UI semantics from contaminating text diagnostics.
        """
        panel = QFrame()
        panel.setStyleSheet(f"background: {PALETTE['background']}; border: 1px solid {PALETTE['border']}; border-radius: 3px;")
        panel.setFixedHeight(140)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # Header with view mode indicator
        self._legend_header = QLabel("VIEW: (none)")
        self._legend_header.setFont(QFont("Consolas", 12, QFont.Bold))
        self._legend_header.setStyleSheet(f"color: {PALETTE['copper']}; border: none;")
        layout.addWidget(self._legend_header)

        # Colored legend content (HTML with actual colored spans)
        self._legend_content = QLabel()
        self._legend_content.setWordWrap(True)
        self._legend_content.setFont(QFont("Consolas", 11))
        self._legend_content.setStyleSheet(f"color: {PALETTE['parchment']}; border: none;")
        layout.addWidget(self._legend_content)
        layout.addStretch()

        return panel

    def _update_legend_panel(self):
        """Update legend panel with current view mode colors."""
        mode = self._folio_viewer.transcription_panel._view_mode
        label, tooltip = VIEW_MODE_LABELS.get(mode, (mode.name, ""))

        # Update header with mode and system
        self._legend_header.setText(f"VIEW: {label} ({self._current_system})")

        # Get color map for current mode
        color_map = self._get_color_map_for_mode(mode)

        # Build HTML with colored background spans
        html_parts = []
        for key, color in color_map.items():
            html_parts.append(
                f'<span style="background:{color}; color:#000; padding:5px 12px; margin:4px;">'
                f'{key}</span>'
            )

        self._legend_content.setText(" ".join(html_parts))

    def _get_color_map_for_mode(self, mode: ViewMode) -> dict:
        """Get the color mapping for a view mode."""
        mode_color_maps = {
            ViewMode.A_MARKER: A_MARKER_COLORS,
            ViewMode.A_SISTER: A_SISTER_COLORS,
            ViewMode.A_ROLE: A_ROLE_COLORS,
            ViewMode.B_INSTRUCTION: B_INSTRUCTION_COLORS,
            ViewMode.B_POSITION: B_POSITION_COLORS,
            ViewMode.B_KERNEL_CONTACT: B_KERNEL_CONTACT_COLORS,
            ViewMode.B_EXECUTION: B_EXECUTION_COLORS,
            ViewMode.KERNEL_AFFINITY: KERNEL_AFFINITY_COLORS,
            ViewMode.MORPHOLOGY: MORPHOLOGY_COLORS,
            ViewMode.LINK_AFFINITY: LINK_AFFINITY_COLORS,
            ViewMode.AZC_PLACEMENT: AZC_PLACEMENT_COLORS,
        }
        return mode_color_maps.get(mode, {})

    def _on_copy_all_tokens(self):
        """Copy all unique tokens with property records to clipboard.

        Output is TOKEN-CENTRIC (not folio-centric):
        - Each token gets its own primary_system classification
        - Property records with labeled fields, not prose summaries
        - No order, frequency, or execution semantics
        """
        tokens = self._folio_viewer.transcription_panel.get_unique_tokens()
        if not tokens:
            self.statusBar().showMessage("No tokens to copy")
            return

        # Get token placements for AZC binding (C306)
        token_placements = self._folio_viewer.transcription_panel.get_token_placements()

        lines = [f"=== {self._current_folio} (folio system: {self._current_system}) - {len(tokens)} unique tokens ===\n"]

        # Sort for display only (not semantic)
        for token in sorted(tokens):
            # Token-centric: determine primary_system per token
            primary = get_token_primary_system(token, self._current_system)

            lines.append(f"TOKEN: {token}")
            lines.append(f"  primary_system: {primary}")

            if primary == 'A':
                result = parse_currier_a_token(token)
                lines.append(f"  a_status: {result.a_status.name}")

                # Check if this is an infrastructure minimal form
                is_infrastructure = token.lower() in A_INFRASTRUCTURE_MINIMAL

                if is_infrastructure:
                    # Infrastructure minimals are atomic - don't call them "prefix"
                    lines.append(f"  a_role: INFRASTRUCTURE_MINIMAL")
                    lines.append(f"  form: {token.lower()}")
                else:
                    # Regular A tokens: show prefix/middle/suffix structure
                    lines.append(f"  prefix: {result.prefix or '-'}")
                    lines.append(f"  middle: {result.middle or '-'}")
                    lines.append(f"  suffix: {result.suffix or '-'}")

                    # Determine marker family for all prefixes
                    if result.prefix:
                        prefix_lower = result.prefix.lower()
                        # Extended prefixes map to base family
                        if prefix_lower in CURRIER_A_EXTENDED_MAP:
                            family = CURRIER_A_EXTENDED_MAP[prefix_lower].upper()
                        # Standard 2-char prefixes ARE the family
                        elif prefix_lower in MARKER_FAMILIES:
                            family = prefix_lower.upper()
                        else:
                            family = '-'
                        lines.append(f"  marker_family: {family}")

                # Add kernel affinity for all A tokens
                affinity = get_kernel_affinity(token)
                if affinity:
                    lines.append(f"  kernel_affinity: {affinity}")
            elif primary == 'B':
                # B tokens: add instruction role from 49-class grammar (C121)
                instruction_role = get_token_instruction_role(token)
                lines.append(f"  instruction_role: {instruction_role}")
                # Grammar binding status - clarifies UNKNOWN vs bound
                grammar_bound = instruction_role != 'UNKNOWN'
                lines.append(f"  grammar_bound: {str(grammar_bound).lower()}")
                # Surface segmentation only, explicitly labeled
                prefix, middle, suffix = segment_word(token)
                lines.append(f"  surface_prefix: {prefix or '-'}")
                lines.append(f"  surface_middle: {middle or '-'}")
                lines.append(f"  surface_suffix: {suffix or '-'}")
            elif primary == 'AZC':
                # AZC tokens: show placement class (C306)
                placements = token_placements.get(token, ['UNKNOWN'])
                # Deduplicate while preserving first occurrence
                unique_placements = list(dict.fromkeys(placements))
                if len(unique_placements) == 1:
                    lines.append(f"  azc_placement: {unique_placements[0]}")
                else:
                    # Multiple placements - keep scalar + list candidates
                    lines.append(f"  azc_placement: MULTI")
                    lines.append(f"  azc_placement_set: [{', '.join(unique_placements)}]")
                # Surface segmentation
                prefix, middle, suffix = segment_word(token)
                lines.append(f"  surface_prefix: {prefix or '-'}")
                lines.append(f"  surface_middle: {middle or '-'}")
                lines.append(f"  surface_suffix: {suffix or '-'}")
                # Add kernel affinity (shared type system)
                affinity = get_kernel_affinity(token)
                if affinity:
                    lines.append(f"  kernel_affinity: {affinity}")
            elif primary == 'HT':
                lines.append(f"  note: Currier HT (high-frequency terminal)")
            else:
                # INVALID or unknown
                lines.append(f"  note: Not legal in any known system")

            lines.append("")

        text = "\n".join(lines)
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage(f"Copied {len(tokens)} unique tokens to clipboard")

    def _on_copy_selected(self):
        """Copy current detail text to clipboard (excludes legend)."""
        text = self._detail_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.statusBar().showMessage("Copied token detail to clipboard")

    def _setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Consolas", 9))
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Ready | Grammar: {self._grammar.class_count} classes, {self._grammar.token_count} tokens")

    def _apply_styles(self):
        """Apply application-wide styles."""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {PALETTE['background']};
            }}
            QLabel {{
                color: {PALETTE['parchment']};
            }}
            QStatusBar {{
                background-color: {PALETTE['panel']};
                color: {PALETTE['copper_dim']};
                border-top: 1px solid {PALETTE['border']};
            }}
        """)

    def _load_data(self):
        """Load transcription data and populate folio list."""
        # Load transcriptions
        paths = [
            "C:/git/voynich/data/transcriptions/interlinear_full_words.txt",
            "./data/transcriptions/interlinear_full_words.txt",
        ]

        for path in paths:
            try:
                count = self._transcription_loader.load_interlinear(path)
                if count > 0:
                    self.status_bar.showMessage(f"Loaded {count} folios | Grammar: {self._grammar.class_count} classes")
                    break
            except FileNotFoundError:
                continue

        # Populate folio list
        folio_ids = self._transcription_loader.get_folio_ids()
        self._folio_browser.set_folios(folio_ids)

    def _on_folio_selected(self, folio_id: str):
        """Handle folio selection with system-aware updates."""
        self._current_folio = folio_id

        # Detect Currier system and update UI if changed
        new_system = self._get_folio_system(folio_id)
        if new_system != self._current_system:
            self._current_system = new_system
            self._update_system_banner(new_system)
            self._rebuild_mode_buttons(new_system)
            # Reset execution toggle when leaving B system
            if new_system != 'B' and self._exec_toggle.isChecked():
                self._exec_toggle.blockSignals(True)
                self._exec_toggle.setChecked(False)
                self._exec_toggle.blockSignals(False)
            # Enable/disable execution toggle based on system
            self._exec_toggle.setEnabled(new_system == 'B')

        # Set folio system BEFORE loading (for system-aware token coloring)
        self._folio_viewer.set_folio_system(new_system)

        # Load folio content
        self._folio_viewer.load_folio(folio_id)
        self._update_legend_panel()

        # Update stats with system indicator
        folio = self._transcription_loader.get_folio(folio_id)
        if folio:
            token_count = folio.token_count
            line_count = folio.line_count

            # Calculate LINK density (tokens containing 'ol' or 'al')
            link_tokens = sum(1 for t in folio.tokens if 'ol' in t.lower() or 'al' in t.lower())
            link_density = (link_tokens / token_count * 100) if token_count > 0 else 0

            self._stats_label.setText(
                f"[{new_system}] f{folio_id} | {token_count} tokens | {line_count} lines | LINK: {link_density:.1f}%"
            )

            # Show recommended views hint in status bar
            recommended = RECOMMENDED_VIEWS.get(new_system, [])
            rec_str = ', '.join(recommended) if recommended else 'Morph'
            self.status_bar.showMessage(
                f"Loaded f{folio_id} ({new_system}) — Recommended: {rec_str}"
            )

    def _on_glyph_toggle(self, checked: bool):
        """Toggle Voynich glyph display."""
        self._folio_viewer.set_use_glyphs(checked)

    def _on_exec_toggle(self, checked: bool):
        """Toggle Execution Inspector mode (B-system only)."""
        if self._current_system != 'B':
            # Not in B system - disable and show message
            self._exec_toggle.blockSignals(True)
            self._exec_toggle.setChecked(False)
            self._exec_toggle.blockSignals(False)
            self.status_bar.showMessage("Execution Inspector is only available in Currier B folios", 3000)
            return

        if checked:
            # Switch to execution mode
            self._pre_exec_mode = self._current_view_mode  # Store previous mode
            self._folio_viewer.set_view_mode(ViewMode.B_EXECUTION)
            self._current_view_mode = ViewMode.B_EXECUTION
            self._update_legend_panel()
            # Update banner to show execution is active
            self._update_system_banner_exec(True)
            self.status_bar.showMessage("Execution Inspector ACTIVE - kernel contact + position + LINK (C357, C371-373)")
        else:
            # Return to previous mode
            prev_mode = getattr(self, '_pre_exec_mode', ViewMode.B_INSTRUCTION)
            self._folio_viewer.set_view_mode(prev_mode)
            self._current_view_mode = prev_mode
            self._update_legend_panel()
            self._update_system_banner_exec(False)
            self.status_bar.showMessage(f"View mode: {prev_mode.name}")

    def _update_system_banner_exec(self, exec_active: bool):
        """Update system banner to reflect execution inspector state."""
        if not hasattr(self, '_system_banner'):
            return

        if exec_active:
            # Show execution warning
            color = '#FF6040'  # Bright orange-red
            title = "EXECUTION INSPECTOR ACTIVE"
            subtitle = "Showing kernel contact (C372), position (C371), LINK affinity (C373)"
        else:
            # Restore normal banner - use CURRIER_COLORS for system-specific colors
            color = CURRIER_COLORS.get(self._current_system, PALETTE['amber'])
            title, subtitle = SYSTEM_BANNERS.get(self._current_system, ("UNKNOWN", ""))

        # Update title
        layout = self._system_banner.layout()
        if layout and layout.count() > 0:
            title_item = layout.itemAt(0)
            if title_item and title_item.widget():
                title_label = title_item.widget()
                title_label.setText(title)
                title_label.setStyleSheet(f"color: {color}; background: transparent;")

            if layout.count() > 1:
                subtitle_item = layout.itemAt(layout.count() - 1)
                if subtitle_item and subtitle_item.widget():
                    subtitle_label = subtitle_item.widget()
                    subtitle_label.setText(subtitle)

        # Update border color
        self._system_banner.setStyleSheet(f"""
            QFrame {{
                background-color: {PALETTE['panel']};
                border: 2px solid {color};
                border-radius: 5px;
            }}
        """)

    def _on_view_mode_changed(self, button: QRadioButton):
        """Handle view mode change with soft mismatch warning."""
        mode_id = self._view_button_group.id(button)
        mode = ViewMode(mode_id)
        self._folio_viewer.set_view_mode(mode)
        self._current_view_mode = mode
        self._update_legend_panel()

        # Check for system mismatch and show soft warning
        target_system = MODE_TARGET_SYSTEM.get(mode)  # None for global modes
        label, _ = VIEW_MODE_LABELS.get(mode, (mode.name, None))

        if target_system and target_system != self._current_system:
            # Mismatched mode - show warning (non-blocking, auto-clears)
            self.status_bar.showMessage(
                f"{label} view — not applicable to Currier {self._current_system} folios. "
                f"Tokens will remain transparent.",
                5000  # Auto-clear after 5 seconds
            )
        else:
            self.status_bar.showMessage(f"View mode: {label}")

    def _on_token_selected(self, token_text: str, line_num: int, tok_idx: int):
        """Handle token selection - update detail panel with system-appropriate facts.

        Uses token's PRIMARY SYSTEM (not folio system) to determine which detail builder.
        This ensures HT tokens on B folios get HT treatment, not B treatment.
        """
        # Get token's actual primary system (may differ from folio system)
        primary = get_token_primary_system(token_text, self._current_system)

        if primary == 'HT':
            detail = self._build_ht_detail(token_text, line_num, tok_idx)
        elif primary == 'B':
            detail = self._build_b_detail(token_text, line_num, tok_idx)
        elif primary == 'A':
            detail = self._build_a_detail(token_text, line_num, tok_idx)
        elif primary == 'AZC':
            detail = self._build_azc_detail(token_text, line_num, tok_idx)
        else:  # INVALID
            detail = self._build_invalid_detail(token_text, line_num, tok_idx)

        self._detail_text.setPlainText(detail)
        self._update_legend_panel()

        # Filter constraint panel by token
        self._constraint_panel.filter_by_token(token_text)

        self.status_bar.showMessage(f"Selected: {token_text} at line {line_num} ({primary})")

    def _build_b_detail(self, token_text: str, line_num: int, tok_idx: int) -> str:
        """Build detail panel content for Currier B token (execution grammar)."""
        prefix, core, suffix = segment_word(token_text)
        instruction_role = get_token_instruction_role(token_text)
        kernel = get_kernel_contact(token_text)
        is_link = token_text.lower() in LINK_TOKENS

        # Format morphology
        morph_parts = []
        if prefix:
            morph_parts.append(f"{prefix}-")
        morph_parts.append(core if core else "(core)")
        if suffix:
            morph_parts.append(f"-{suffix}")
        morph_display = " + ".join(morph_parts)

        # Get related constraints
        related_constraints = self._constraint_panel._loader.find_for_token(token_text)
        constraint_refs = [f"  {c.id}: {c.description[:50]}..." for c in related_constraints[:5]] if related_constraints else ["  (none found)"]

        detail = f"""TOKEN: {token_text}
{'=' * 45}
CURRIER B — Execution Grammar

STRUCTURAL FACTS (C121: 100% coverage)
  Instruction:   {instruction_role:<16} (C098)
  Kernel Contact:{kernel.upper():<16} (C372)
  Is LINK:       {'YES' if is_link else 'NO':<16} (C105)
  Morphology:    {morph_display}

KERNEL SEMANTICS (C372)"""

        if kernel == 'heavy':
            detail += """
  KERNEL-HEAVY: 100% kernel contact
  High intervention intensity, direct state change"""
        elif kernel == 'light':
            detail += """
  KERNEL-LIGHT: <5% kernel contact
  Low intervention intensity, monitoring/passive"""
        elif kernel == 'escape':
            detail += """
  ESCAPE ROUTE: exits hazard state (C397)
  Allows recovery from forbidden zone"""
        else:
            detail += """
  NEUTRAL: No special kernel role"""

        detail += f"""

CONSTRAINTS
{chr(10).join(constraint_refs)}
{'=' * 45}
Position: Line {line_num}, Token {tok_idx}"""

        return detail

    def _build_a_detail(self, token_text: str, line_num: int, tok_idx: int) -> str:
        """Build detail panel content for Currier A token (categorical registry)."""
        # Two-gate validation: C240 prefix legality + C267 morphology completeness
        parse_result = parse_currier_a_token(token_text)
        if not (parse_result.is_prefix_legal and parse_result.is_morph_complete):
            return self._build_invalid_a_detail(token_text, parse_result, line_num, tok_idx)

        # 4-component morphology (C267 + C291)
        articulator, prefix, middle, suffix = segment_word_4component(token_text)
        token_role = get_a_token_role(token_text)
        marker_family = get_a_marker_family(token_text)
        sister_pair = get_a_sister_pair(token_text)
        kernel_affinity = get_kernel_affinity(token_text)

        # Format 4-component morphology
        morph_parts = []
        if articulator:
            morph_parts.append(f"[{articulator}]")  # Articulator in brackets
        if prefix:
            morph_parts.append(f"{prefix}-")
        if middle:
            morph_parts.append(f"({middle})")  # Middle (DATA) in parens
        else:
            morph_parts.append("()")  # Empty middle
        if suffix:
            morph_parts.append(f"-{suffix}")
        morph_display = " ".join(morph_parts) if morph_parts else token_text

        # Get related constraints - FILTER to A-safe constraints only
        # Exclude B execution constraints (C074-C199, C300-C382)
        all_constraints = self._constraint_panel._loader.find_for_token(token_text)
        A_SAFE_RANGES = [
            (229, 299),   # Currier A architecture (C229-C299)
            (383, 420),   # Global type system, cross-system (C383+)
            (267, 268),   # Morphology (C267-C268) - shared but safe
        ]
        def is_a_safe(c):
            return any(start <= c.number <= end for start, end in A_SAFE_RANGES)
        related_constraints = [c for c in all_constraints if is_a_safe(c)]
        constraint_refs = [f"  {c.id}: {c.description[:50]}..." for c in related_constraints[:5]] if related_constraints else ["  (none found)"]

        # Marker family description
        marker_desc = {
            'ch': 'Primary classifier',
            'sh': 'Sister to ch (J=0.23)',
            'ok': 'Primary classifier',
            'ot': 'Sister to ok (J=0.24)',
            'da': 'Infrastructure marker',
            'qo': 'Bridging marker',
            'ol': 'Bridging marker',
            'ct': 'Section H specialist',
        }.get(marker_family, 'Other')

        # Role description
        role_desc = {
            'ARTICULATED': 'Has refinement prefix (yk-, yt-, kch-)',
            'INFRASTRUCTURE': 'Registry infrastructure token',
            'REGISTRY_ENTRY': 'Categorical entry (has MIDDLE)',
            'MINIMAL': 'Frame only (PREFIX + SUFFIX)',
        }.get(token_role, 'Unknown')

        detail = f"""TOKEN: {token_text}
{'=' * 45}
CURRIER A — Categorical Registry

FUNCTIONAL ROLE (C267, C291)
  Role:            {token_role:<14} ({role_desc})

4-COMPONENT MORPHOLOGY (C267)
  [ARTICULATOR] + PREFIX + [MIDDLE] + SUFFIX
  Articulator:     {articulator if articulator else '(none)':<14} (~20% have this)
  Prefix:          {prefix if prefix else '(none)':<14} (category marker)
  Middle:          {middle if middle else '(none)':<14} (registry payload)
  Suffix:          {suffix if suffix else '(none)':<14} (universal form)
  Full Parse:      {morph_display}

MARKER ANALYSIS (C240: 8 families)
  Marker Family:   {marker_family.upper():<14} ({marker_desc})
  Sister Pair:     {sister_pair:<14} (C408)

TYPE SYSTEM (C383 - shared)
  Kernel Affinity: {kernel_affinity.upper():<14}"""

        if token_role == 'ARTICULATED':
            detail += f"""

NOTE: ARTICULATOR "{articulator}" (C291)
  Optional refinement, 100% removable
  Does not change token identity"""
        elif sister_pair.startswith('pair1'):
            detail += """

NOTE: ch-sh are EQUIVALENCE CLASSES (C408)
  Interchangeable in structural contexts
  J=0.23 Jaccard similarity"""
        elif sister_pair.startswith('pair2'):
            detail += """

NOTE: ok-ot are EQUIVALENCE CLASSES (C408)
  Interchangeable in structural contexts
  J=0.24 Jaccard similarity"""

        detail += f"""

A-SPECIFIC CONSTRAINTS
  POSITION-FREE: No positional grammar (C234)
  LINE_ATOMIC: Median 3 tokens/line (C233)
  NON-SEQUENTIAL: No execution semantics

CONSTRAINTS
{chr(10).join(constraint_refs)}
{'=' * 45}
Position: Line {line_num}, Token {tok_idx}"""

        return detail

    def _build_invalid_a_detail(self, token_text: str, parse_result: CurrierAParseResult, line_num: int, tok_idx: int) -> str:
        """Build detail panel for token that fails Currier A validation."""
        # Status-specific gate information
        if parse_result.a_status == AStatus.ILLEGAL_PREFIX:
            gate_info = f"""
GATE 1 FAILED: No valid C240 prefix
  Valid prefixes: {', '.join(sorted(MARKER_FAMILIES))}
  Token start: '{token_text[:3] if len(token_text) >= 3 else token_text}'

Gate 2: Not evaluated (Gate 1 failed)"""

        elif parse_result.a_status == AStatus.PREFIX_VALID_MORPH_INCOMPLETE:
            gate_info = f"""
GATE 1 PASSED: Valid prefix detected
  Prefix: {parse_result.prefix}

GATE 2 FAILED: Morphology incomplete (C267)
  Remainder has no recognizable A suffix pattern.
  Middle/Suffix: {parse_result.middle or '(none)'} / {parse_result.suffix or '(none)'}"""

        elif parse_result.a_status == AStatus.AMBIGUOUS_MORPHOLOGY:
            gate_info = f"""
GATE 1 PASSED: Valid prefix detected
  Prefix: {parse_result.prefix}

GATE 2 AMBIGUOUS: Decomposition uncertain
  '{parse_result.suffix}' is both a valid suffix AND prefix family.
  Cannot determine: PREFIX+SUFFIX or PREFIX+PREFIX"""

        else:
            gate_info = f"""
  Status: {parse_result.a_status.name}
  Reason: {parse_result.reason}"""

        detail = f"""TOKEN: {token_text}
{'=' * 45}
CURRIER A VALIDATION FAILED

Status: {parse_result.a_status.name}
{gate_info}

EXPLANATION
  This token is treated as INVALID for Currier A.
  It will appear transparent in A-specific view modes.

CLASSIFICATION
  NOT Currier A registry content
  Candidate Systems: HT / AZC / Residue

{'=' * 45}
Position: Line {line_num}, Token {tok_idx}"""
        return detail

    def _build_azc_detail(self, token_text: str, line_num: int, tok_idx: int) -> str:
        """Build detail panel content for AZC token (diagram annotation)."""
        prefix, core, suffix = segment_word(token_text)
        kernel_affinity = get_kernel_affinity(token_text)

        # Format morphology
        morph_parts = []
        if prefix:
            morph_parts.append(f"{prefix}-")
        morph_parts.append(core if core else "(core)")
        if suffix:
            morph_parts.append(f"-{suffix}")
        morph_display = " + ".join(morph_parts)

        # Get related constraints
        related_constraints = self._constraint_panel._loader.find_for_token(token_text)
        constraint_refs = [f"  {c.id}: {c.description[:50]}..." for c in related_constraints[:5]] if related_constraints else ["  (none found)"]

        detail = f"""TOKEN: {token_text}
{'=' * 45}
AZC — Diagram Annotation

PLACEMENT (C306: topological classes)
  [Placement data requires folio context]
  Classes: C (Core), P (Peripheral), R (Ring), S (Surface)

TYPE SYSTEM (C383 - shared)
  Kernel Affinity: {kernel_affinity.upper():<14}
  Morphology:      {morph_display}

AZC-SPECIFIC CONSTRAINTS
  HYBRID: Topological core + positional frame (C317)
  LEGALITY: 219 forbidden position pairs (C313-C316)
  LABELING: Diagram-anchored, not sequential

CONSTRAINTS
{chr(10).join(constraint_refs)}
{'=' * 45}
Position: Line {line_num}, Token {tok_idx}"""

        return detail

    def _build_ht_detail(self, token_text: str, line_num: int, tok_idx: int) -> str:
        """Build detail panel content for Human-Track (HT) token.

        HT tokens are non-operational, non-executing tokens (C404-406).
        They may reuse B suffixes but are NOT grammar-bound.
        """
        prefix, core, suffix = segment_word(token_text)

        # Format morphology
        morph_parts = []
        if prefix:
            morph_parts.append(f"{prefix}-")
        morph_parts.append(core if core else "(core)")
        if suffix:
            morph_parts.append(f"-{suffix}")
        morph_display = " + ".join(morph_parts)

        # Detect B-suffix reuse
        b_suffixes = {'edy', 'eedy', 'ey', 'dy', 'in', 'ain', 'aiin'}
        suffix_lower = suffix.lower() if suffix else ''
        has_b_suffix = suffix_lower in b_suffixes

        detail = f"""TOKEN: {token_text}
{'=' * 45}
HUMAN-TRACK (HT) — Non-Operational

CLASSIFICATION (C404-406)
  Primary System:  HT (Human-Track)
  Operational:     NO
  Grammar-Bound:   NO
  Kernel Semantics: NONE

MORPHOLOGY
  HT Prefix:       {prefix if prefix else '(bare)'}
  Middle:          {core if core else '(none)'}
  Suffix:          {suffix if suffix else '(none)'}
  Full Parse:      {morph_display}"""

        if has_b_suffix:
            detail += f"""

B-SUFFIX REUSE DETECTED
  Suffix '{suffix}' is shared with Currier B grammar.
  This is morphological reuse, NOT execution semantics.
  HT prefix overrides B suffix for system classification."""

        detail += f"""

HT PROPERTIES
  - Non-operational: does not affect program outcomes
  - Non-executing: no kernel contact, no hazard interaction
  - Removing HT tokens does not change grammar or execution
  - ~12.47% of corpus are HT-B hybrids (expected)

{'=' * 45}
Position: Line {line_num}, Token {tok_idx}
Folio System: {self._current_system} (HT appears in all systems)"""

        return detail

    def _build_invalid_detail(self, token_text: str, line_num: int, tok_idx: int) -> str:
        """Build detail panel content for INVALID token."""
        prefix, core, suffix = segment_word(token_text)

        detail = f"""TOKEN: {token_text}
{'=' * 45}
INVALID — Classification Failed

This token could not be classified into any known system:
  - Not valid Currier A (failed C240/C267 gates)
  - Not Human-Track (no HT prefix)
  - Context: Folio system is {self._current_system}

MORPHOLOGY (surface only)
  Prefix: {prefix if prefix else '(none)'}
  Middle: {core if core else '(none)'}
  Suffix: {suffix if suffix else '(none)'}

{'=' * 45}
Position: Line {line_num}, Token {tok_idx}"""

        return detail

    def _get_prefix_meaning(self, prefix: str) -> str:
        """Get frozen-fact meaning of prefix."""
        if not prefix:
            return ""
        prefix_lower = prefix.lower()
        if prefix_lower in ('ch', 'sh', 'ok', 'lk', 'yk', 'ke', 'ot', 'ct'):
            return "(KERNEL-HEAVY, 100% kernel contact)"
        elif prefix_lower in ('da', 'sa'):
            return "(KERNEL-LIGHT, <5% kernel contact)"
        elif prefix_lower == 'qo':
            return "(ESCAPE ROUTE, exits hazard)"
        elif prefix_lower in ('ol', 'al'):
            return "(LINK-ATTRACTED)"
        elif prefix_lower in ('so', 'po', 'to', 'ko'):
            return "(LINE-INITIAL enriched)"
        return ""

    def _get_suffix_meaning(self, suffix: str) -> str:
        """Get frozen-fact meaning of suffix."""
        if not suffix:
            return ""
        suffix_lower = suffix.lower()
        if suffix_lower in ('edy', 'eedy', 'ey', 'dy'):
            return "(KERNEL-HEAVY, 83-95%)"
        elif suffix_lower in ('in', 'l', 'r', 'al'):
            return "(LINK-ATTRACTED)"
        elif suffix_lower == 'aiin':
            return "(da+-aiin = 30%)"
        elif suffix_lower in ('am', 'om', 'oly'):
            return "(LINE-FINAL enriched)"
        return ""

    def _build_view_legend(self) -> str:
        """Build a legend explaining the current view mode and its colors."""
        mode = self._folio_viewer.transcription_panel._view_mode
        label, tooltip = VIEW_MODE_LABELS.get(mode, (mode.name, None))

        # Mode descriptions (corrected per expert review)
        mode_descriptions = {
            ViewMode.PLAIN: "No highlighting - all tokens transparent",
            ViewMode.MORPHOLOGY: "Highlights tokens by 2-char prefix family (ch-, sh-, da-, etc.)",
            ViewMode.KERNEL_AFFINITY: "Shared morphological type system (C383) - NOT execution semantics",
            ViewMode.LINK_AFFINITY: "LINK operator attraction/avoidance pattern",
            ViewMode.B_INSTRUCTION: "49-class execution grammar roles (C121)",
            ViewMode.B_POSITION: "Line-initial/final positional enrichment (C371)",
            ViewMode.B_KERNEL_CONTACT: "Kernel contact execution semantics (C372) - B-specific",
            ViewMode.B_EXECUTION: "EXECUTION INSPECTOR: composite view of kernel contact + position + LINK (C357, C371-373)",
            ViewMode.A_MARKER: "8 validated marker families: ch/sh/ok/ot/da/qo/ol/ct (C240)",
            ViewMode.A_SISTER: "ch-sh, ok-ot equivalence classes (C408)",
            ViewMode.A_ROLE: "Functional role in categorical registry (C267, C291)",
            ViewMode.A_MULTIPLICITY: "Multiplicity enumeration pattern (C250)",
            ViewMode.AZC_PLACEMENT: "Topological placement classes (C306)",
            ViewMode.AZC_LEGALITY: "Position legality constraints (C313)",
        }

        # Color key descriptions per mode
        color_keys = {
            ViewMode.PLAIN: [],
            ViewMode.MORPHOLOGY: [
                ("ch", "Red family"),
                ("sh", "Orange family"),
                ("da", "Blue family"),
                ("qo", "Green family (escape)"),
                ("ok", "Purple family"),
                ("ot", "Violet family"),
                ("ol", "Teal family"),
                ("ct", "Yellow family"),
                ("other", "Gray (unrecognized prefix)"),
            ],
            ViewMode.KERNEL_AFFINITY: [
                ("heavy", "Kernel-heavy morphology (ch-, sh-, ok-, ot-, ct-)"),
                ("light", "Kernel-light morphology (da-, sa-)"),
                ("escape", "Escape route morphology (qo-)"),
                ("transparent", "Neutral affinity"),
            ],
            ViewMode.LINK_AFFINITY: [
                ("attracted", "LINK-attracted tokens (ol, al, da-, sa-)"),
                ("avoided", "LINK-avoided tokens (qo-)"),
                ("transparent", "Neutral"),
            ],
            ViewMode.B_INSTRUCTION: [
                ("CORE_CONTROL", "Execution boundaries"),
                ("ENERGY_OPERATOR", "Energy modulation"),
                ("FLOW_OPERATOR", "Flow control"),
                ("HIGH_IMPACT", "Major interventions"),
                ("FREQUENT_OPERATOR", "Common operations"),
                ("AUXILIARY", "Support operations"),
                ("LINK", "LINK behavior"),
                ("MODIFIER", "Parameter modifiers"),
                ("TERMINAL", "Sequence terminators"),
                ("UNKNOWN", "Unmapped token"),
            ],
            ViewMode.B_POSITION: [
                ("initial", "Line-initial token (so-, po-, to-, ko-)"),
                ("final", "Line-final token (-am, -om, -oly)"),
                ("link", "LINK token (shown for context)"),
                ("transparent", "Mid-line position"),
            ],
            ViewMode.B_KERNEL_CONTACT: [
                ("heavy", "Intervention contact (ch-, sh-, ok-)"),
                ("light", "Monitoring contact (da-, sa-)"),
                ("escape", "Escape contact (qo-)"),
                ("transparent", "Neutral contact"),
            ],
            ViewMode.B_EXECUTION: [
                ("heavy", "INTERVENTION phase (ch-, sh-, ok-) - kernel-heavy"),
                ("light", "MONITORING phase (da-, sa-) - kernel-light"),
                ("escape", "ESCAPE route (qo-) - hazard exit"),
                ("neutral", "Unclassified token"),
            ],
            ViewMode.A_MARKER: [
                ("ch", "Primary classifier (mauve)"),
                ("sh", "Sister to ch (gray-mauve)"),
                ("ok", "Primary classifier (steel blue)"),
                ("ot", "Sister to ok (teal)"),
                ("da", "Infrastructure (olive)"),
                ("qo", "Bridging/escape (yellow-olive)"),
                ("ol", "Bridging (purple)"),
                ("ct", "Section H specialist (red)"),
                ("other", "Invalid marker (dark gray)"),
            ],
            ViewMode.A_SISTER: [
                ("pair1_ch", "ch-sh pair (ch shade)"),
                ("pair1_sh", "ch-sh pair (sh shade)"),
                ("pair2_ok", "ok-ot pair (ok shade)"),
                ("pair2_ot", "ok-ot pair (ot shade)"),
                ("other", "Not a sister pair member"),
            ],
            ViewMode.A_ROLE: [
                ("ARTICULATED", "Has articulator prefix (yk-, yt-, kch-)"),
                ("INFRASTRUCTURE", "Registry infrastructure token (daiin, ol, ar)"),
                ("REGISTRY_ENTRY", "Categorical entry with MIDDLE component"),
                ("MINIMAL", "Frame only (PREFIX + SUFFIX)"),
            ],
            ViewMode.A_MULTIPLICITY: [
                ("(uses morphology colors)", ""),
            ],
            ViewMode.AZC_PLACEMENT: [
                ("C", "Core position"),
                ("P", "Peripheral position"),
                ("R", "Ring position"),
                ("S", "Surface position"),
                ("B/T/L/M/N", "Other placement classes"),
                ("other", "Unknown placement"),
            ],
            ViewMode.AZC_LEGALITY: [
                ("(placeholder)", ""),
            ],
        }

        description = mode_descriptions.get(mode, tooltip or "")
        keys = color_keys.get(mode, [])

        # Build legend text
        legend = f"""
VIEW LEGEND
{'=' * 45}
Mode: {label}
{description}
"""
        if keys:
            legend += "\nColors:\n"
            for key, desc in keys:
                if key == "transparent":
                    legend += f"  [] {key}: {desc}\n"
                elif desc:  # Skip empty descriptions
                    legend += f"  [#] {key}: {desc}\n"

        # System-aware disclaimer
        legend += """
Note: Transparent tokens may indicate neutral
classification or system illegality (C240/C267)."""

        return legend
