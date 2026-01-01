#!/usr/bin/env python3
"""
Voynich Manuscript Visual Coding GUI

PyQt5 application for coding visual features of 30 pilot folios.
Displays manuscript pages from PDF and provides form for 25 visual features.
Saves data in JSON format compatible with post_coding_pipeline.py.

Requirements:
    pip install PyQt5 PyMuPDF
"""

import sys
import json
import webbrowser
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QGroupBox, QScrollArea,
    QFrame, QProgressBar, QMessageBox, QFileDialog, QSplitter,
    QSpinBox, QSlider, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QImage

# =============================================================================
# FEATURE DEFINITIONS / HELP TEXT
# =============================================================================

FEATURE_HELP = {
    # ROOT
    'root_present': {
        'description': 'Is there a visible root system below the stem/ground line?',
        'PRESENT': 'Root structure is clearly visible',
        'ABSENT': 'No root shown (plant cut off at stem base)',
        'UNDETERMINED': 'Cannot tell due to damage or unclear drawing',
    },
    'root_type': {
        'description': 'What shape/form is the root system?',
        'NONE': 'No root visible',
        'SINGLE_TAPROOT': 'One main root going straight down (like a carrot)',
        'BRANCHING': 'Root splits into 2+ thick branches (like a tree root)',
        'BULBOUS': 'Round, swollen root base (like an onion or garlic bulb)',
        'FIBROUS': 'Many thin roots of similar size spreading out (like grass roots)',
        'UNDETERMINED': 'Root visible but type unclear',
    },
    'root_prominence': {
        'description': 'How much of the illustration is the root?',
        'SMALL': 'Root is less than 20% of total plant height',
        'MEDIUM': 'Root is 20-40% of total plant height',
        'LARGE': 'Root is more than 40% of total plant height',
        'NA': 'Not applicable (no root)',
        'UNDETERMINED': 'Cannot determine size ratio',
    },
    'root_color_distinct': {
        'description': 'Is the root drawn in a different color than the stem?',
        'YES': 'Root has different coloring/shading than stem',
        'NO': 'Root same color as stem',
        'UNDETERMINED': 'Cannot tell',
    },

    # STEM
    'stem_count': {
        'description': 'How many main stems emerge from the root/base?',
        '1': 'Single main stem',
        '2': 'Two main stems',
        '3_PLUS': 'Three or more main stems',
        'UNDETERMINED': 'Cannot count stems clearly',
    },
    'stem_type': {
        'description': 'What is the overall shape/behavior of the stem?',
        'STRAIGHT': 'Stem goes mostly straight up',
        'CURVED': 'Stem has significant curve or bend',
        'BRANCHING': 'Stem divides into multiple branches',
        'TWINING': 'Stem wraps or spirals (like a vine)',
        'UNDETERMINED': 'Stem type unclear',
    },
    'stem_thickness': {
        'description': 'How thick is the main stem relative to plant size?',
        'THIN': 'Delicate, grass-like stem',
        'MEDIUM': 'Average thickness',
        'THICK': 'Sturdy, tree-like stem',
        'UNDETERMINED': 'Cannot judge thickness',
    },
    'stem_color_distinct': {
        'description': 'Is stem drawn in different color than leaves?',
        'YES': 'Stem has different coloring than leaves',
        'NO': 'Stem same color as leaves',
        'UNDETERMINED': 'Cannot tell',
    },

    # LEAF
    'leaf_present': {
        'description': 'Are there leaves visible on the plant?',
        'PRESENT': 'Leaves are visible',
        'ABSENT': 'No leaves shown',
        'UNDETERMINED': 'Cannot tell if structures are leaves',
    },
    'leaf_count_category': {
        'description': 'Approximately how many leaves?',
        'NONE': 'No leaves',
        'FEW_1_5': '1-5 leaves',
        'MEDIUM_6_15': '6-15 leaves',
        'MANY_16_PLUS': '16 or more leaves',
        'UNDETERMINED': 'Too many/unclear to count',
    },
    'leaf_shape': {
        'description': 'What is the primary leaf shape?',
        'ROUND': 'Circular or nearly circular leaves',
        'OVAL': 'Egg-shaped, longer than wide with smooth edges',
        'LANCEOLATE': 'Long and narrow, pointed at tip (like a spear)',
        'LOBED': 'Leaf has deep indentations (>25% into leaf) like oak or maple',
        'COMPOUND': 'Multiple separate leaflets on one stem (like a fern or clover)',
        'SERRATED': 'Leaf edge has small teeth/saw-like edge (<25% into leaf)',
        'NEEDLE': 'Very thin, needle-like leaves (like pine)',
        'MIXED': 'Multiple leaf shapes present',
        'UNDETERMINED': 'Shape unclear',
    },
    'leaf_arrangement': {
        'description': 'How are leaves positioned on the stem?',
        'ALTERNATE': 'Leaves alternate sides going up stem (left, right, left...)',
        'OPPOSITE': 'Leaves in pairs, directly across from each other',
        'BASAL': 'All leaves cluster at the base/bottom of plant',
        'WHORLED': '3+ leaves attach at same point around stem',
        'SCATTERED': 'No clear pattern',
        'NA': 'Not applicable',
        'UNDETERMINED': 'Arrangement unclear',
    },
    'leaf_size_relative': {
        'description': 'How big are leaves compared to the whole plant?',
        'SMALL': 'Leaves are small relative to plant',
        'MEDIUM': 'Leaves are medium sized',
        'LARGE': 'Leaves are prominent/dominant feature',
        'MIXED': 'Mix of different sized leaves',
        'UNDETERMINED': 'Cannot judge size',
    },
    'leaf_color_uniform': {
        'description': 'Are all leaves the same color?',
        'YES': 'All leaves same color/shade',
        'NO': 'Leaves have different colors',
        'UNDETERMINED': 'Cannot tell',
    },

    # FLOWER
    'flower_present': {
        'description': 'Are there flowers visible?',
        'PRESENT': 'Flowers are visible',
        'ABSENT': 'No flowers shown',
        'UNDETERMINED': 'Cannot tell if structures are flowers',
    },
    'flower_count': {
        'description': 'How many flowers?',
        'NONE': 'No flowers',
        '1': 'Single flower',
        '2_5': '2-5 flowers',
        '6_PLUS': '6 or more flowers',
        'UNDETERMINED': 'Cannot count',
    },
    'flower_position': {
        'description': 'Where are flowers located on the plant?',
        'NONE': 'No flowers',
        'TERMINAL': 'Flowers at the tips/ends of stems',
        'AXILLARY': 'Flowers where leaves meet stem (leaf junctions)',
        'THROUGHOUT': 'Flowers distributed all along the plant',
        'UNDETERMINED': 'Position unclear',
    },
    'flower_color_distinct': {
        'description': 'Are flowers a different color than leaves/stem?',
        'YES': 'Flowers have distinct coloring',
        'NO': 'Flowers same color as rest of plant',
        'UNDETERMINED': 'Cannot tell',
    },
    'flower_shape': {
        'description': 'What is the flower structure?',
        'NONE': 'No flowers',
        'SIMPLE': 'Basic flower with single ring of petals',
        'COMPOUND': 'Complex flower head (like a daisy - many tiny flowers)',
        'RADIAL': 'Symmetric, star-like pattern',
        'IRREGULAR': 'Asymmetric or unusual shape',
        'UNDETERMINED': 'Shape unclear',
    },

    # OVERALL
    'plant_count': {
        'description': 'How many separate plants in this illustration?',
        '1': 'Single plant',
        '2': 'Two plants',
        '3_PLUS': 'Three or more plants',
        'UNDETERMINED': 'Cannot tell if one plant or multiple',
    },
    'container_present': {
        'description': 'Is the plant shown in a pot/vase/container?',
        'PRESENT': 'Plant is in a container',
        'ABSENT': 'No container (plant shown with roots or cut)',
        'UNDETERMINED': 'Cannot tell',
    },
    'plant_symmetry': {
        'description': 'Is the plant drawing symmetric left-to-right?',
        'SYMMETRIC': 'Left and right sides are mirror images',
        'ASYMMETRIC': 'Sides are noticeably different',
        'UNDETERMINED': 'Cannot judge symmetry',
    },
    'overall_complexity': {
        'description': 'How detailed/complex is the overall illustration?',
        'SIMPLE': 'Less than 5 distinct visual elements (few leaves, simple shape)',
        'MODERATE': '5-15 distinct elements',
        'COMPLEX': 'More than 15 elements or very intricate detail',
        'UNDETERMINED': 'Cannot judge complexity',
    },
    'identifiable_impression': {
        'description': 'Does this look like it could be a real, identifiable plant?',
        'YES': 'Looks like a realistic plant that might be identifiable',
        'NO': 'Looks fantastical, abstract, or clearly not a real plant',
        'UNCERTAIN': 'Could go either way',
    },
    'drawing_completeness': {
        'description': 'Is the illustration complete or partial?',
        'COMPLETE': 'Full plant shown (root to top)',
        'PARTIAL': 'Some parts cut off or not shown',
        'FRAGMENTARY': 'Only a small portion visible',
        'UNDETERMINED': 'Cannot tell if complete',
    },
}

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("WARNING: PyMuPDF not installed. Run: pip install PyMuPDF")

# =============================================================================
# CONFIGURATION
# =============================================================================

TEXT_FEATURES_FILE = 'pilot_folio_text_features.json'
CODING_ORDER_FILE = 'coding_order.json'
SAVE_FILE = 'visual_coding_data.json'
PDF_FILE = 'data/scans/Voynich_Manuscript.pdf'
YALE_URL = 'https://collections.library.yale.edu/catalog/2002046'

# Feature definitions with their possible values
FEATURES = {
    'ROOT': {
        'root_present': ['', 'PRESENT', 'ABSENT', 'UNDETERMINED'],
        'root_type': ['', 'NONE', 'SINGLE_TAPROOT', 'BRANCHING', 'BULBOUS', 'FIBROUS', 'UNDETERMINED'],
        'root_prominence': ['', 'SMALL', 'MEDIUM', 'LARGE', 'NA', 'UNDETERMINED'],
        'root_color_distinct': ['', 'YES', 'NO', 'UNDETERMINED'],
    },
    'STEM': {
        'stem_count': ['', '1', '2', '3_PLUS', 'UNDETERMINED'],
        'stem_type': ['', 'STRAIGHT', 'CURVED', 'BRANCHING', 'TWINING', 'UNDETERMINED'],
        'stem_thickness': ['', 'THIN', 'MEDIUM', 'THICK', 'UNDETERMINED'],
        'stem_color_distinct': ['', 'YES', 'NO', 'UNDETERMINED'],
    },
    'LEAF': {
        'leaf_present': ['', 'PRESENT', 'ABSENT', 'UNDETERMINED'],
        'leaf_count_category': ['', 'NONE', 'FEW_1_5', 'MEDIUM_6_15', 'MANY_16_PLUS', 'UNDETERMINED'],
        'leaf_shape': ['', 'ROUND', 'OVAL', 'LANCEOLATE', 'LOBED', 'COMPOUND', 'SERRATED', 'NEEDLE', 'MIXED', 'UNDETERMINED'],
        'leaf_arrangement': ['', 'ALTERNATE', 'OPPOSITE', 'BASAL', 'WHORLED', 'SCATTERED', 'NA', 'UNDETERMINED'],
        'leaf_size_relative': ['', 'SMALL', 'MEDIUM', 'LARGE', 'MIXED', 'UNDETERMINED'],
        'leaf_color_uniform': ['', 'YES', 'NO', 'UNDETERMINED'],
    },
    'FLOWER': {
        'flower_present': ['', 'PRESENT', 'ABSENT', 'UNDETERMINED'],
        'flower_count': ['', 'NONE', '1', '2_5', '6_PLUS', 'UNDETERMINED'],
        'flower_position': ['', 'NONE', 'TERMINAL', 'AXILLARY', 'THROUGHOUT', 'UNDETERMINED'],
        'flower_color_distinct': ['', 'YES', 'NO', 'UNDETERMINED'],
        'flower_shape': ['', 'NONE', 'SIMPLE', 'COMPOUND', 'RADIAL', 'IRREGULAR', 'UNDETERMINED'],
    },
    'OVERALL': {
        'plant_count': ['', '1', '2', '3_PLUS', 'UNDETERMINED'],
        'container_present': ['', 'PRESENT', 'ABSENT', 'UNDETERMINED'],
        'plant_symmetry': ['', 'SYMMETRIC', 'ASYMMETRIC', 'UNDETERMINED'],
        'overall_complexity': ['', 'SIMPLE', 'MODERATE', 'COMPLEX', 'UNDETERMINED'],
        'identifiable_impression': ['', 'YES', 'NO', 'UNCERTAIN'],
        'drawing_completeness': ['', 'COMPLETE', 'PARTIAL', 'FRAGMENTARY', 'UNDETERMINED'],
    },
}

# Dependencies: if parent is ABSENT, disable children
DEPENDENCIES = {
    'root_present': ['root_type', 'root_prominence', 'root_color_distinct'],
    'leaf_present': ['leaf_count_category', 'leaf_shape', 'leaf_arrangement', 'leaf_size_relative', 'leaf_color_uniform'],
    'flower_present': ['flower_count', 'flower_position', 'flower_color_distinct', 'flower_shape'],
}


# =============================================================================
# FOLIO TO PAGE MAPPING
# =============================================================================

def folio_to_page(folio_id: str) -> int:
    """
    Convert folio ID (e.g., 'f42r') to PDF page number.

    The Voynich manuscript PDF typically has pages in order:
    - f1r = page 1, f1v = page 2, f2r = page 3, f2v = page 4, etc.

    Special cases:
    - f90v2 might need manual adjustment
    - Foldout pages may have different numbering
    """
    # Parse folio ID: fXXr or fXXv or fXXvN
    match = re.match(r'f(\d+)([rv])(\d*)', folio_id)
    if not match:
        return 1  # Default to first page

    folio_num = int(match.group(1))
    side = match.group(2)  # 'r' or 'v'
    section = match.group(3)  # Optional section number like '2' in f90v2

    # Basic calculation: each folio has 2 pages (recto and verso)
    # Page = (folio_num - 1) * 2 + (1 if recto, 2 if verso)
    page = (folio_num - 1) * 2 + (1 if side == 'r' else 2)

    # For sections like f90v2, this might need manual adjustment
    # The section number suggests a multi-part page

    return page


# Manual overrides for known problematic mappings
PAGE_OVERRIDES = {
    # Add manual overrides here if needed, e.g.:
    # 'f90v2': 180,
}


def get_page_for_folio(folio_id: str) -> int:
    """Get PDF page number for a folio, with override support."""
    if folio_id in PAGE_OVERRIDES:
        return PAGE_OVERRIDES[folio_id]
    return folio_to_page(folio_id)


# =============================================================================
# PDF VIEWER
# =============================================================================

class PDFViewer(QWidget):
    """Widget for displaying PDF pages."""

    def __init__(self, pdf_path: str):
        super().__init__()
        self.pdf_path = pdf_path
        self.doc = None
        self.current_page = 0
        self.zoom = 1.0
        self.page_count = 0

        self.init_ui()
        self.load_pdf()

    def init_ui(self):
        """Initialize the PDF viewer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Controls bar
        controls = QHBoxLayout()

        # Page navigation
        self.page_label = QLabel("Page: 1")
        controls.addWidget(self.page_label)

        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(300)
        self.page_spin.valueChanged.connect(self.go_to_page)
        controls.addWidget(self.page_spin)

        # Page nav buttons
        prev_page_btn = QPushButton("<")
        prev_page_btn.setMaximumWidth(30)
        prev_page_btn.clicked.connect(self.prev_page)
        controls.addWidget(prev_page_btn)

        next_page_btn = QPushButton(">")
        next_page_btn.setMaximumWidth(30)
        next_page_btn.clicked.connect(self.next_page)
        controls.addWidget(next_page_btn)

        controls.addSpacing(20)

        # Zoom controls
        controls.addWidget(QLabel("Zoom:"))

        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setMaximumWidth(30)
        zoom_out_btn.clicked.connect(self.zoom_out)
        controls.addWidget(zoom_out_btn)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        controls.addWidget(self.zoom_label)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setMaximumWidth(30)
        zoom_in_btn.clicked.connect(self.zoom_in)
        controls.addWidget(zoom_in_btn)

        controls.addStretch()

        layout.addLayout(controls)

        # Scrollable image area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel("Loading PDF...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)

        layout.addWidget(self.scroll_area, 1)

    def load_pdf(self):
        """Load the PDF file."""
        if not HAS_PYMUPDF:
            self.image_label.setText("PyMuPDF not installed.\nRun: pip install PyMuPDF")
            return

        if not Path(self.pdf_path).exists():
            self.image_label.setText(f"PDF not found:\n{self.pdf_path}")
            return

        try:
            self.doc = fitz.open(self.pdf_path)
            self.page_count = self.doc.page_count
            self.page_spin.setMaximum(self.page_count)
            self.render_page()
        except Exception as e:
            self.image_label.setText(f"Error loading PDF:\n{e}")

    def render_page(self):
        """Render current page to display."""
        if not self.doc:
            return

        if self.current_page < 0 or self.current_page >= self.page_count:
            return

        try:
            page = self.doc[self.current_page]

            # Render at zoom level
            mat = fitz.Matrix(self.zoom * 1.5, self.zoom * 1.5)  # Base scale for readability
            pix = page.get_pixmap(matrix=mat)

            # Convert to QImage
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)

            self.image_label.setPixmap(pixmap)
            self.page_label.setText(f"Page: {self.current_page + 1}/{self.page_count}")
            self.page_spin.blockSignals(True)
            self.page_spin.setValue(self.current_page + 1)
            self.page_spin.blockSignals(False)
            self.zoom_label.setText(f"{int(self.zoom * 100)}%")

        except Exception as e:
            self.image_label.setText(f"Error rendering page:\n{e}")

    def set_page(self, page_num: int):
        """Set current page (1-indexed for user, 0-indexed internally)."""
        self.current_page = max(0, min(page_num - 1, self.page_count - 1))
        self.render_page()

    def go_to_page(self, page_num: int):
        """Go to specific page from spinbox."""
        self.set_page(page_num)

    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()

    def next_page(self):
        """Go to next page."""
        if self.current_page < self.page_count - 1:
            self.current_page += 1
            self.render_page()

    def zoom_in(self):
        """Zoom in."""
        self.zoom = min(3.0, self.zoom + 0.25)
        self.render_page()

    def zoom_out(self):
        """Zoom out."""
        self.zoom = max(0.25, self.zoom - 0.25)
        self.render_page()

    def close_pdf(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()
            self.doc = None


# =============================================================================
# DATA MANAGEMENT
# =============================================================================

class DataManager:
    """Handles loading and saving of coding data."""

    def __init__(self):
        self.text_features = {}
        self.coding_order = []
        self.coded_data = {}
        self.current_index = 0

    def load_text_features(self) -> bool:
        """Load folio text features."""
        try:
            with open(TEXT_FEATURES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.text_features = data.get('pilot_folios', {})
            return True
        except FileNotFoundError:
            return False

    def load_coding_order(self) -> bool:
        """Load recommended coding order."""
        try:
            with open(CODING_ORDER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.coding_order = data.get('coding_order', [])
            return True
        except FileNotFoundError:
            self.coding_order = [
                {'folio_id': fid, 'order': i, 'priority': 'MEDIUM', 'reason': ''}
                for i, fid in enumerate(self.text_features.keys())
            ]
            return True

    def load_saved_data(self) -> bool:
        """Load previously saved coding data."""
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.coded_data = data.get('folios', {})
            return True
        except FileNotFoundError:
            self.coded_data = {}
            return False

    def save_data(self):
        """Save all coding data to file."""
        coded_count = sum(1 for f in self.coded_data.values() if f.get('coded', False))
        data = {
            'metadata': {
                'last_modified': datetime.now().isoformat(),
                'folios_coded': coded_count,
                'total_folios': len(self.coding_order)
            },
            'folios': self.coded_data
        }
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_folio_data(self, folio_id: str) -> Dict:
        return self.coded_data.get(folio_id, {})

    def set_folio_data(self, folio_id: str, data: Dict):
        self.coded_data[folio_id] = data

    def get_current_folio(self) -> Optional[Dict]:
        if 0 <= self.current_index < len(self.coding_order):
            return self.coding_order[self.current_index]
        return None

    def get_folio_text_features(self, folio_id: str) -> Dict:
        return self.text_features.get(folio_id, {})

    def export_csv(self, filepath: str):
        """Export coded data to CSV format."""
        if not self.coded_data:
            return

        all_features = []
        for category, features in FEATURES.items():
            all_features.extend(features.keys())

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            header = ['folio_id'] + all_features + ['notes']
            writer.writerow(header)

            for folio in self.coding_order:
                folio_id = folio['folio_id']
                data = self.coded_data.get(folio_id, {})
                row = [folio_id]
                for feature in all_features:
                    row.append(data.get(feature, ''))
                row.append(data.get('notes', ''))
                writer.writerow(row)


# =============================================================================
# MAIN WINDOW
# =============================================================================

class VisualCodingGUI(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.feature_widgets = {}
        self.pdf_viewer = None
        self.init_data()
        self.init_ui()
        self.load_current_folio()

    def init_data(self):
        """Initialize data loading."""
        if not self.data_manager.load_text_features():
            QMessageBox.critical(self, "Error",
                f"Could not load {TEXT_FEATURES_FILE}\nMake sure the file exists.")
            sys.exit(1)

        self.data_manager.load_coding_order()
        self.data_manager.load_saved_data()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Voynich Visual Coding Tool")
        self.setMinimumSize(1400, 900)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Top navigation bar
        nav_bar = self.create_nav_bar()
        main_layout.addWidget(nav_bar)

        # Main content area (splitter: PDF | Info + Form)
        main_splitter = QSplitter(Qt.Horizontal)

        # Left: PDF viewer
        self.pdf_viewer = PDFViewer(PDF_FILE)
        main_splitter.addWidget(self.pdf_viewer)

        # Right: Info + Form
        right_splitter = QSplitter(Qt.Vertical)

        # Info panel
        info_panel = self.create_info_panel()
        right_splitter.addWidget(info_panel)

        # Feature form
        form_panel = self.create_feature_form()
        right_splitter.addWidget(form_panel)

        right_splitter.setSizes([150, 600])
        main_splitter.addWidget(right_splitter)

        # Set splitter proportions (PDF takes more space)
        main_splitter.setSizes([700, 500])
        main_layout.addWidget(main_splitter, 1)

        # Bottom status bar
        status_bar = self.create_status_bar()
        main_layout.addWidget(status_bar)

    def create_nav_bar(self) -> QWidget:
        """Create the top navigation bar."""
        nav = QFrame()
        nav.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout(nav)

        self.prev_btn = QPushButton("< Previous Folio")
        self.prev_btn.clicked.connect(self.go_previous)
        layout.addWidget(self.prev_btn)

        self.folio_label = QLabel("Folio: ---")
        self.folio_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.folio_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.folio_label, 1)

        self.next_btn = QPushButton("Next Folio >")
        self.next_btn.clicked.connect(self.go_next)
        layout.addWidget(self.next_btn)

        layout.addSpacing(20)

        yale_btn = QPushButton("Open Yale Library")
        yale_btn.clicked.connect(self.open_yale)
        layout.addWidget(yale_btn)

        help_btn = QPushButton("? Help")
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)

        save_btn = QPushButton("Save All")
        save_btn.clicked.connect(self.save_all)
        layout.addWidget(save_btn)

        return nav

    def create_info_panel(self) -> QWidget:
        """Create the info panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)

        title = QLabel("Folio Information")
        title.setFont(QFont('Arial', 11, QFont.Bold))
        layout.addWidget(title)

        # Info in horizontal layout to save vertical space
        info_row = QHBoxLayout()

        self.heading_label = QLabel("Heading: ---")
        self.prefix_label = QLabel("Prefix: ---")
        self.words_label = QLabel("Words: ---")
        self.status_label = QLabel("Status: ---")
        self.priority_label = QLabel("Priority: ---")

        for label in [self.heading_label, self.prefix_label, self.words_label,
                      self.status_label, self.priority_label]:
            label.setFont(QFont('Arial', 9))
            info_row.addWidget(label)

        layout.addLayout(info_row)

        self.reason_label = QLabel("Reason: ---")
        self.reason_label.setWordWrap(True)
        self.reason_label.setFont(QFont('Arial', 9))
        layout.addWidget(self.reason_label)

        return panel

    def create_feature_form(self) -> QWidget:
        """Create the feature coding form."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)

        for category, features in FEATURES.items():
            group = QGroupBox(category)
            group_layout = QVBoxLayout(group)

            for feature_name, values in features.items():
                row = QHBoxLayout()

                label = QLabel(feature_name + ":")
                label.setMinimumWidth(140)
                label.setFont(QFont('Arial', 9))
                # Add tooltip with description
                if feature_name in FEATURE_HELP:
                    label.setToolTip(FEATURE_HELP[feature_name].get('description', ''))
                row.addWidget(label)

                combo = QComboBox()
                combo.addItems(values)
                combo.setMinimumWidth(150)
                # Build tooltip showing all option definitions
                if feature_name in FEATURE_HELP:
                    help_info = FEATURE_HELP[feature_name]
                    tooltip_lines = [help_info.get('description', ''), '']
                    for val in values:
                        if val and val in help_info:
                            tooltip_lines.append(f"{val}: {help_info[val]}")
                    combo.setToolTip('\n'.join(tooltip_lines))
                combo.currentTextChanged.connect(
                    lambda text, fn=feature_name: self.on_feature_changed(fn, text)
                )
                row.addWidget(combo)
                row.addStretch()

                group_layout.addLayout(row)
                self.feature_widgets[feature_name] = combo

            layout.addWidget(group)

        # Notes field
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        notes_layout.addWidget(self.notes_edit)
        layout.addWidget(notes_group)

        # Coding guide hints (compact)
        guide_group = QGroupBox("Quick Reference")
        guide_layout = QHBoxLayout(guide_group)
        hints = ["LOBED: >25%", "SERRATED: <25%", "SIMPLE: <5", "MODERATE: 5-15", "COMPLEX: >15"]
        for hint in hints:
            lbl = QLabel(hint)
            lbl.setFont(QFont('Arial', 8))
            guide_layout.addWidget(lbl)
        layout.addWidget(guide_group)

        scroll.setWidget(container)
        return scroll

    def create_status_bar(self) -> QWidget:
        """Create the bottom status bar."""
        bar = QFrame()
        bar.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout(bar)

        self.progress_label = QLabel("Progress: 0/30 coded")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(30)
        self.progress_bar.setMinimumWidth(200)
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        layout.addWidget(export_btn)

        self.save_status = QLabel("Status: Ready")
        layout.addWidget(self.save_status)

        return bar

    def load_current_folio(self):
        """Load and display current folio data."""
        folio = self.data_manager.get_current_folio()
        if not folio:
            return

        folio_id = folio['folio_id']
        idx = self.data_manager.current_index
        total = len(self.data_manager.coding_order)

        # Update navigation
        self.folio_label.setText(f"Folio: {folio_id} ({idx + 1}/{total})")
        self.prev_btn.setEnabled(idx > 0)
        self.next_btn.setEnabled(idx < total - 1)

        # Update info panel
        text_features = self.data_manager.get_folio_text_features(folio_id)
        self.heading_label.setText(f"Heading: {text_features.get('heading_word', 'N/A')}")
        self.prefix_label.setText(f"Prefix: {text_features.get('heading_prefix', 'N/A')}")
        self.words_label.setText(f"Words: {text_features.get('word_count', 'N/A')}")
        self.status_label.setText(f"Status: {folio.get('reference_status', 'ISOLATED')}")
        self.priority_label.setText(f"Priority: {folio.get('priority', 'MEDIUM')}")
        self.reason_label.setText(f"Reason: {folio.get('reason', '')}")

        # Navigate PDF to correct page
        page = get_page_for_folio(folio_id)
        if self.pdf_viewer:
            self.pdf_viewer.set_page(page)

        # Load coded data
        coded = self.data_manager.get_folio_data(folio_id)

        for feature_name, combo in self.feature_widgets.items():
            combo.blockSignals(True)
            value = coded.get(feature_name, '')
            idx = combo.findText(value)
            combo.setCurrentIndex(idx if idx >= 0 else 0)
            combo.blockSignals(False)

        self.notes_edit.setPlainText(coded.get('notes', ''))
        self.update_dependencies()
        self.update_progress()

    def save_current_folio(self):
        """Save current folio data."""
        folio = self.data_manager.get_current_folio()
        if not folio:
            return

        folio_id = folio['folio_id']
        data = {'coding_date': datetime.now().strftime('%Y-%m-%d')}

        all_filled = True
        for feature_name, combo in self.feature_widgets.items():
            value = combo.currentText()
            data[feature_name] = value
            if not value:
                all_filled = False

        data['notes'] = self.notes_edit.toPlainText()
        data['coded'] = all_filled

        self.data_manager.set_folio_data(folio_id, data)
        self.data_manager.save_data()

        self.save_status.setText("Status: Saved")
        self.update_progress()

    def on_feature_changed(self, feature_name: str, value: str):
        if feature_name in DEPENDENCIES:
            self.update_dependencies()
        self.save_current_folio()

    def update_dependencies(self):
        for parent, children in DEPENDENCIES.items():
            parent_combo = self.feature_widgets.get(parent)
            if not parent_combo:
                continue

            parent_value = parent_combo.currentText()
            is_absent = parent_value == 'ABSENT'

            for child in children:
                child_combo = self.feature_widgets.get(child)
                if child_combo:
                    child_combo.setEnabled(not is_absent)
                    if is_absent:
                        child_combo.blockSignals(True)
                        child_combo.setCurrentIndex(0)
                        child_combo.blockSignals(False)

    def update_progress(self):
        coded = sum(1 for f in self.data_manager.coded_data.values()
                    if f.get('coded', False))
        total = len(self.data_manager.coding_order)
        self.progress_label.setText(f"Progress: {coded}/{total} coded")
        self.progress_bar.setValue(coded)

    def go_previous(self):
        self.save_current_folio()
        if self.data_manager.current_index > 0:
            self.data_manager.current_index -= 1
            self.load_current_folio()

    def go_next(self):
        self.save_current_folio()
        if self.data_manager.current_index < len(self.data_manager.coding_order) - 1:
            self.data_manager.current_index += 1
            self.load_current_folio()

    def open_yale(self):
        webbrowser.open(YALE_URL)

    def show_help(self):
        """Show help dialog with all feature definitions."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Visual Feature Definitions")
        dialog.setMinimumSize(700, 600)

        layout = QVBoxLayout(dialog)

        # Instructions at top
        intro = QLabel(
            "This guide explains what each visual feature means and how to code it.\n"
            "Hover over any field in the form to see a quick tooltip."
        )
        intro.setWordWrap(True)
        intro.setFont(QFont('Arial', 10))
        layout.addWidget(intro)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Organize by category
        categories = {
            'ROOT': ['root_present', 'root_type', 'root_prominence', 'root_color_distinct'],
            'STEM': ['stem_count', 'stem_type', 'stem_thickness', 'stem_color_distinct'],
            'LEAF': ['leaf_present', 'leaf_count_category', 'leaf_shape', 'leaf_arrangement',
                     'leaf_size_relative', 'leaf_color_uniform'],
            'FLOWER': ['flower_present', 'flower_count', 'flower_position', 'flower_color_distinct',
                       'flower_shape'],
            'OVERALL': ['plant_count', 'container_present', 'plant_symmetry', 'overall_complexity',
                        'identifiable_impression', 'drawing_completeness'],
        }

        for category, features in categories.items():
            # Category header
            cat_label = QLabel(f"\n{category}")
            cat_label.setFont(QFont('Arial', 12, QFont.Bold))
            cat_label.setStyleSheet("color: #2E86AB;")
            content_layout.addWidget(cat_label)

            for feature in features:
                if feature not in FEATURE_HELP:
                    continue

                help_info = FEATURE_HELP[feature]

                # Feature name and description
                feature_label = QLabel(f"  {feature}")
                feature_label.setFont(QFont('Arial', 10, QFont.Bold))
                content_layout.addWidget(feature_label)

                desc = help_info.get('description', '')
                desc_label = QLabel(f"    {desc}")
                desc_label.setFont(QFont('Arial', 9))
                desc_label.setStyleSheet("color: #555;")
                content_layout.addWidget(desc_label)

                # Option values
                for key, value in help_info.items():
                    if key == 'description':
                        continue
                    opt_label = QLabel(f"      {key}: {value}")
                    opt_label.setFont(QFont('Arial', 9))
                    opt_label.setWordWrap(True)
                    content_layout.addWidget(opt_label)

        # Visual examples section
        examples_label = QLabel("\n\nQUICK TIPS")
        examples_label.setFont(QFont('Arial', 12, QFont.Bold))
        examples_label.setStyleSheet("color: #2E86AB;")
        content_layout.addWidget(examples_label)

        tips = [
            "LOBED vs SERRATED: Lobed leaves have deep cuts (>25% into leaf), serrated have small teeth (<25%)",
            "COMPOUND leaves: Multiple separate leaflets on one stem (like clover or fern fronds)",
            "ALTERNATE vs OPPOSITE: Alternate = zigzag pattern, Opposite = paired at same height",
            "TERMINAL flowers: At tips of branches. AXILLARY: Where leaf meets stem",
            "SIMPLE drawing: <5 elements. MODERATE: 5-15 elements. COMPLEX: >15 elements",
            "When in doubt, use UNDETERMINED - it's better than guessing wrong!",
        ]

        for tip in tips:
            tip_label = QLabel(f"  - {tip}")
            tip_label.setFont(QFont('Arial', 9))
            tip_label.setWordWrap(True)
            content_layout.addWidget(tip_label)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.close)
        layout.addWidget(button_box)

        dialog.exec_()

    def save_all(self):
        self.save_current_folio()
        QMessageBox.information(self, "Saved", "All data saved successfully.")

    def export_csv(self):
        self.save_current_folio()
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "visual_coding_export.csv", "CSV Files (*.csv)"
        )
        if filepath:
            self.data_manager.export_csv(filepath)
            QMessageBox.information(self, "Exported", f"Data exported to {filepath}")

    def closeEvent(self, event):
        self.save_current_folio()
        if self.pdf_viewer:
            self.pdf_viewer.close_pdf()
        event.accept()


# =============================================================================
# MAIN
# =============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = VisualCodingGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
