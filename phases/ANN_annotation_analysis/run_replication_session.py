#!/usr/bin/env python3
"""
Run Mode B annotation session using pre-generated replication groups.

This script:
1. Loads pre-generated groups from annotation_data/replication_groups.json
2. Presents them in randomized order
3. Saves annotations to the normal annotation data files
"""

import json
import random
import sys
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QButtonGroup, QRadioButton,
    QProgressBar, QMessageBox, QScrollArea, QFrame
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

from annotation_config import load_folio_metadata, QUESTIONS_MODE_B
from annotation_data_manager import AnnotationDataManager


@dataclass
class ReplicationGroup:
    """A pre-generated replication group."""
    group_type: str
    group_basis: str
    folio_ids: List[str]
    is_null_group: bool
    is_foil_group: bool
    note: Optional[str] = None


def load_replication_groups() -> List[ReplicationGroup]:
    """Load pre-generated groups from JSON."""
    with open("annotation_data/replication_groups.json") as f:
        data = json.load(f)

    groups = []
    for g in data["groups"]:
        groups.append(ReplicationGroup(
            group_type=g["group_type"],
            group_basis=g["group_basis"],
            folio_ids=g["folio_ids"],
            is_null_group=g.get("is_null_group", False),
            is_foil_group=g.get("is_foil_group", False),
            note=g.get("note")
        ))

    return groups


class ReplicationAnnotationWindow(QMainWindow):
    """Main window for replication annotation session."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mode B Replication Session")
        self.setMinimumSize(1400, 900)

        # Load data
        self.metadata = load_folio_metadata()
        self.groups = load_replication_groups()
        self.data_manager = AnnotationDataManager()

        # Shuffle groups for randomized presentation
        random.shuffle(self.groups)

        # Session state
        self.current_group_idx = 0
        self.current_question_idx = 0
        self.questions_per_group = ["outlier_detection", "compare_leaf_similarity", "compare_root_similarity"]
        self.position_mapping = {}
        self.start_time = None

        # Build UI
        self._build_ui()

        # Start
        if self.groups:
            self._load_next_group()
        else:
            QMessageBox.warning(self, "No Groups", "No replication groups found.")

    def _build_ui(self):
        """Build the main UI."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Progress bar
        self.progress = QProgressBar()
        total_questions = len(self.groups) * len(self.questions_per_group)
        self.progress.setMaximum(total_questions)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Status label
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.status_label)

        # Question label
        self.question_label = QLabel()
        self.question_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)

        # Images container
        self.images_layout = QHBoxLayout()
        layout.addLayout(self.images_layout, stretch=1)

        # Options
        self.options_group = QGroupBox("Select one:")
        self.options_layout = QVBoxLayout(self.options_group)
        self.button_group = QButtonGroup(self)
        layout.addWidget(self.options_group)

        # Submit button
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self._on_submit)
        self.submit_btn.setEnabled(False)
        layout.addWidget(self.submit_btn)

    def _clear_images(self):
        """Clear image display."""
        while self.images_layout.count():
            item = self.images_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _clear_options(self):
        """Clear option buttons."""
        for button in self.button_group.buttons():
            self.button_group.removeButton(button)
            self.options_layout.removeWidget(button)
            button.deleteLater()

    def _load_next_group(self):
        """Load the next group."""
        if self.current_group_idx >= len(self.groups):
            self._session_complete()
            return

        group = self.groups[self.current_group_idx]
        self.current_group = group
        self.current_question_idx = 0

        # Create position mapping
        folios = group.folio_ids.copy()
        random.shuffle(folios)
        labels = ['A', 'B', 'C', 'D', 'E', 'F'][:len(folios)]
        self.position_mapping = {folio: label for folio, label in zip(folios, labels)}

        # Display images
        self._display_images()

        # Load first question for this group
        self._load_question()

    def _display_images(self):
        """Display images for current group."""
        self._clear_images()

        group = self.current_group
        image_dir = r"C:\git\voynich\data\scans\extracted"

        for folio_id, label in sorted(self.position_mapping.items(), key=lambda x: x[1]):
            # Container for image + label
            container = QFrame()
            container.setFrameStyle(QFrame.Box | QFrame.Plain)
            container_layout = QVBoxLayout(container)

            # Position label
            pos_label = QLabel(label)
            pos_label.setFont(QFont("Arial", 16, QFont.Bold))
            pos_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(pos_label)

            # Image
            image_path = f"{image_dir}\\{folio_id}.png"
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(300, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label = QLabel()
                img_label.setPixmap(scaled)
                img_label.setAlignment(Qt.AlignCenter)
                container_layout.addWidget(img_label)
            else:
                container_layout.addWidget(QLabel(f"[Image not found: {folio_id}]"))

            self.images_layout.addWidget(container)

    def _load_question(self):
        """Load the current question."""
        if self.current_question_idx >= len(self.questions_per_group):
            # Move to next group
            self.current_group_idx += 1
            self._load_next_group()
            return

        question_id = self.questions_per_group[self.current_question_idx]
        question_config = QUESTIONS_MODE_B.get(question_id, {})

        # Update status
        group = self.current_group
        total_q = len(self.groups) * len(self.questions_per_group)
        current_q = (self.current_group_idx * len(self.questions_per_group)) + self.current_question_idx + 1
        self.status_label.setText(
            f"Group {self.current_group_idx + 1}/{len(self.groups)} | "
            f"Question {current_q}/{total_q} | "
            f"Type: {group.group_type} ({group.group_basis})"
        )
        self.progress.setValue(current_q)

        # Set question text
        self.question_label.setText(question_config.get("template", ""))

        # Set options
        self._clear_options()
        for option, desc in question_config.get("options", []):
            text = f"{option}: {desc}" if desc else option
            radio = QRadioButton(text)
            radio.setProperty("option_value", option)
            self.button_group.addButton(radio)
            self.options_layout.addWidget(radio)
            radio.toggled.connect(self._on_option_selected)

        self.submit_btn.setEnabled(False)
        self.start_time = time.time()

    def _on_option_selected(self, checked):
        """Enable submit when option selected."""
        if checked:
            self.submit_btn.setEnabled(True)

    def _on_submit(self):
        """Handle submission."""
        # Get selected option
        selected = self.button_group.checkedButton()
        if not selected:
            return

        response = selected.property("option_value")
        question_id = self.questions_per_group[self.current_question_idx]
        group = self.current_group

        # Calculate response time
        response_time = int((time.time() - self.start_time) * 1000)

        # Save annotation
        self.data_manager.record_mode_b(
            folio_ids=group.folio_ids,
            folio_positions=self.position_mapping,
            question_id=question_id,
            response=response,
            response_time_ms=response_time,
            group_type=group.group_type,
            group_basis=group.group_basis,
            is_null_group=group.is_null_group,
            is_foil_group=group.is_foil_group
        )

        # Move to next question
        self.current_question_idx += 1
        self._load_question()

    def _session_complete(self):
        """Handle session completion."""
        # Data auto-saves after each annotation, but get stats
        stats = self.data_manager.get_statistics()
        msg = f"""Session Complete!

Mode B annotations: {stats.get('mode_b_total', 0)}

Data saved to annotation_data/

Next steps:
1. Run compute_replication_stats.py to compute replication statistics
2. Check replication_same_hub_type.json for results
"""
        QMessageBox.information(self, "Complete", msg)
        self.close()


def main():
    """Run replication annotation session."""
    app = QApplication(sys.argv)

    print("=" * 60)
    print("REPLICATION ANNOTATION SESSION")
    print("=" * 60)

    # Load groups
    try:
        groups = load_replication_groups()
        print(f"\nLoaded {len(groups)} replication groups:")
        for g in groups:
            print(f"  {g.group_type} ({g.group_basis}): {g.folio_ids}")
    except FileNotFoundError:
        print("ERROR: annotation_data/replication_groups.json not found")
        print("Run generate_replication_groups.py first")
        return

    # Start GUI
    window = ReplicationAnnotationWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
