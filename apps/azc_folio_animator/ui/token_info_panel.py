"""
Token Info Panel - Displays detailed token analysis below the A-Text Strip.

Shows:
- Morphological breakdown (PREFIX + MIDDLE + SUFFIX)
- Operational domain and material class
- Sister pair / operational mode
- AZC mapping status
- Token system classification (C240/C347/C350/C407)
- Frequency tier (CORE/COMMON/MODERATE/RARE/HAPAX)
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame,
    QMenu, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.azc_folio_animator.core.token_analyzer import (
    TokenAnalyzer, TokenAnalysis, OperationalDomain, MaterialClass, AStatus,
    TokenSystem, FrequencyTier
)
from apps.azc_folio_animator.core.token_classifier import TokenClassifier, TokenType
from apps.azc_folio_animator.core.corpus_stats import CorpusStatsLoader


class TokenInfoPanel(QWidget):
    """
    Panel showing detailed token analysis.

    Displays morphology, domain, material class, AZC status,
    token system classification, and frequency tier.
    """

    def __init__(self, voynich_font: QFont, classifier: TokenClassifier,
                 corpus_stats: Optional[CorpusStatsLoader] = None):
        super().__init__()
        self.voynich_font = voynich_font
        self.classifier = classifier
        self.corpus_stats = corpus_stats
        self.analyzer = TokenAnalyzer(corpus_stats)
        self.current_token: str = None  # Store for copy

        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(100)  # Increased for SYSTEM section
        self.setStyleSheet("""
            TokenInfoPanel {
                background: #0d1520;
                border-bottom: 1px solid #2a3a4a;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 8, 15, 8)
        main_layout.setSpacing(20)

        # Token display (large, in Voynich font)
        self.token_frame = QFrame()
        self.token_frame.setStyleSheet("""
            QFrame {
                background: #1a2535;
                border: 2px solid #2a4050;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        token_layout = QVBoxLayout(self.token_frame)
        token_layout.setContentsMargins(15, 5, 15, 5)

        self.token_label = QLabel("—")
        self.token_label.setFont(self.voynich_font)
        self.token_label.setStyleSheet("color: #00aacc; font-size: 18px;")
        self.token_label.setAlignment(Qt.AlignCenter)
        token_layout.addWidget(self.token_label)

        self.token_frame.setFixedWidth(120)
        main_layout.addWidget(self.token_frame)

        # Morphology section
        morph_layout = QVBoxLayout()
        morph_layout.setSpacing(2)

        morph_header = QLabel("MORPHOLOGY")
        morph_header.setStyleSheet("color: #666; font-size: 9px; font-weight: bold;")
        morph_layout.addWidget(morph_header)

        self.morph_label = QLabel("Select a token")
        self.morph_label.setStyleSheet("color: #b0c4de; font-size: 11px;")
        morph_layout.addWidget(self.morph_label)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7a8a9a; font-size: 10px;")
        morph_layout.addWidget(self.status_label)

        main_layout.addLayout(morph_layout)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet("color: #2a3a4a;")
        main_layout.addWidget(sep1)

        # Domain section
        domain_layout = QVBoxLayout()
        domain_layout.setSpacing(2)

        domain_header = QLabel("OPERATIONAL DOMAIN")
        domain_header.setStyleSheet("color: #666; font-size: 9px; font-weight: bold;")
        domain_layout.addWidget(domain_header)

        self.domain_label = QLabel("—")
        self.domain_label.setStyleSheet("color: #b0c4de; font-size: 11px;")
        domain_layout.addWidget(self.domain_label)

        self.mode_label = QLabel("")
        self.mode_label.setStyleSheet("color: #7a8a9a; font-size: 10px;")
        domain_layout.addWidget(self.mode_label)

        main_layout.addLayout(domain_layout)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("color: #2a3a4a;")
        main_layout.addWidget(sep2)

        # AZC section
        azc_layout = QVBoxLayout()
        azc_layout.setSpacing(2)

        azc_header = QLabel("AZC STATUS")
        azc_header.setStyleSheet("color: #666; font-size: 9px; font-weight: bold;")
        azc_layout.addWidget(azc_header)

        self.azc_label = QLabel("—")
        self.azc_label.setStyleSheet("color: #b0c4de; font-size: 11px;")
        azc_layout.addWidget(self.azc_label)

        self.azc_detail = QLabel("")
        self.azc_detail.setStyleSheet("color: #7a8a9a; font-size: 10px;")
        azc_layout.addWidget(self.azc_detail)

        main_layout.addLayout(azc_layout)

        # Separator
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.VLine)
        sep3.setStyleSheet("color: #2a3a4a;")
        main_layout.addWidget(sep3)

        # SYSTEM section (token system + frequency)
        system_layout = QVBoxLayout()
        system_layout.setSpacing(2)

        system_header = QLabel("SYSTEM")
        system_header.setStyleSheet("color: #666; font-size: 9px; font-weight: bold;")
        system_layout.addWidget(system_header)

        self.system_label = QLabel("—")
        self.system_label.setStyleSheet("color: #b0c4de; font-size: 11px;")
        system_layout.addWidget(self.system_label)

        self.freq_label = QLabel("")
        self.freq_label.setStyleSheet("color: #7a8a9a; font-size: 10px;")
        system_layout.addWidget(self.freq_label)

        main_layout.addLayout(system_layout)

        main_layout.addStretch()

    def set_token(self, token_text: str):
        """Update panel with analysis of the given token."""
        self.current_token = token_text  # Store for copy

        # Analyze token
        analysis = self.analyzer.analyze(token_text)

        # Get AZC info from classifier
        folio_count = self.classifier.get_folio_count(token_text)
        token_type = self.classifier.classify(token_text)
        analysis.azc_folio_count = folio_count

        # Update token display
        self.token_label.setText(token_text)

        # Update frame color based on domain
        frame_color = self._get_domain_color(analysis.domain)
        self.token_frame.setStyleSheet(f"""
            QFrame {{
                background: #1a2535;
                border: 2px solid {frame_color};
                border-radius: 6px;
                padding: 5px;
            }}
        """)
        self.token_label.setStyleSheet(f"color: {frame_color}; font-size: 18px;")

        # Update morphology
        self.morph_label.setText(analysis.get_morphology_display())
        self.status_label.setText(analysis.get_status_display())

        # Color status by validity
        if analysis.parse_status == AStatus.ILLEGAL_PREFIX:
            self.status_label.setStyleSheet("color: #aa5555; font-size: 10px;")
        elif analysis.parse_status in (AStatus.VALID_REGISTRY_ENTRY, AStatus.VALID_MINIMAL):
            self.status_label.setStyleSheet("color: #55aa55; font-size: 10px;")
        else:
            self.status_label.setStyleSheet("color: #aaaa55; font-size: 10px;")

        # Update domain
        self.domain_label.setText(analysis.get_domain_display())
        self.domain_label.setStyleSheet(f"color: {frame_color}; font-size: 11px;")
        self.mode_label.setText(analysis.get_sister_display())

        # Update AZC status
        self._update_azc_display(token_type, folio_count)

        # Update system classification
        self._update_system_display(analysis)

    def _get_domain_color(self, domain: OperationalDomain) -> str:
        """Get color for operational domain."""
        colors = {
            OperationalDomain.ENERGY_OPERATOR: "#ff8844",    # Orange - energy/heat
            OperationalDomain.CORE_CONTROL: "#44aaff",       # Blue - control/structure
            OperationalDomain.FREQUENT_OPERATOR: "#44dd88",  # Green - routine
            OperationalDomain.REGISTRY_REFERENCE: "#aa88ff", # Purple - reference
            OperationalDomain.UNCLASSIFIED: "#888888",       # Gray - unknown
        }
        return colors.get(domain, "#888888")

    def _update_azc_display(self, token_type: TokenType, folio_count: int):
        """Update AZC status display."""
        type_info = {
            TokenType.NO_AZC_MAPPING: ("No AZC mapping", "#aa5555", "MIDDLE not in AZC vocabulary"),
            TokenType.STRUCTURAL: ("Structural", "#888888", f"Grammar token ({folio_count} folios)"),
            TokenType.DISTRIBUTED: ("Distributed", "#aaaa55", f"Spans {folio_count} AZC folios"),
            TokenType.LOCALIZED: ("Localized", "#55aa55", f"Specific to {folio_count} folio(s)"),
        }

        label, color, detail = type_info.get(
            token_type,
            ("Unknown", "#888888", "")
        )

        self.azc_label.setText(label)
        self.azc_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")
        self.azc_detail.setText(detail)

    def _update_system_display(self, analysis: TokenAnalysis):
        """Update system classification and frequency display."""
        # System classification with color
        system_color = analysis.get_system_color()
        self.system_label.setText(analysis.get_system_display())
        self.system_label.setStyleSheet(f"color: {system_color}; font-size: 11px; font-weight: bold;")

        # Frequency info
        self.freq_label.setText(analysis.get_frequency_display())

    def clear(self):
        """Clear the panel."""
        self.current_token = None
        self.token_label.setText("—")
        self.token_frame.setStyleSheet("""
            QFrame {
                background: #1a2535;
                border: 2px solid #2a4050;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        self.token_label.setStyleSheet("color: #00aacc; font-size: 18px;")
        self.morph_label.setText("Select a token")
        self.status_label.setText("")
        self.domain_label.setText("—")
        self.mode_label.setText("")
        self.azc_label.setText("—")
        self.azc_detail.setText("")
        self.system_label.setText("—")
        self.system_label.setStyleSheet("color: #b0c4de; font-size: 11px;")
        self.freq_label.setText("")

    def contextMenuEvent(self, event):
        """Show context menu with copy option."""
        if not self.current_token:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a2635;
                color: #b0c4de;
                border: 1px solid #2a4050;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item { padding: 6px 20px; }
            QMenu::item:selected { background-color: #2a3a4a; }
        """)

        copy_action = menu.addAction(f"Copy: {self.current_token}")
        copy_action.triggered.connect(lambda: self._copy_to_clipboard(self.current_token))

        menu.exec_(event.globalPos())

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
