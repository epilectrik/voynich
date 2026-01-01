#!/usr/bin/env python3
"""
Comparative Query-Driven Visual Annotation System - Main GUI

A PyQt5 application for hypothesis-driven visual annotation of Voynich folios.
Two modes:
- Mode A: Single-image forced-choice questions
- Mode B: 4-6 image comparative questions

Features:
- Strict blinding (no folio IDs visible)
- Response timing and weighting
- Interleaved Mode A/B questions
- Session management with fatigue detection
- Auto-save on every response
"""

import sys
import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QRadioButton, QButtonGroup, QPushButton, QProgressBar,
    QFrame, QScrollArea, QMessageBox, QGroupBox, QSplitter
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QElapsedTimer

from annotation_config import (
    QUESTIONS_MODE_A, QUESTIONS_MODE_B,
    SESSION_CONFIG, load_folio_metadata, get_all_available_folios,
    GroupType
)
from annotation_grouper import GroupGenerator, GroupResult
from annotation_data_manager import AnnotationDataManager


# =============================================================================
# SESSION CONTROLLER
# =============================================================================

@dataclass
class QuestionItem:
    """A single question in the session queue."""
    mode: str  # "A" or "B"
    question_id: str
    folio_id: Optional[str] = None  # For Mode A
    group_result: Optional[GroupResult] = None  # For Mode B
    is_duplicate_check: bool = False


class SessionController:
    """
    Controls the annotation session.

    Handles:
    - Question queue generation
    - Mode interleaving
    - Duplicate check insertion
    - Fatigue detection
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.metadata = load_folio_metadata()
        self.all_folios = list(self.metadata.keys())
        self.group_generator = GroupGenerator(target_group_size=4, seed=seed)

        # Queue
        self.question_queue: List[QuestionItem] = []
        self.current_index = 0

        # Tracking
        self.mode_a_folio_questions: Dict[str, set] = {}  # folio -> set of asked questions
        self.consecutive_flags = 0

    def generate_session(self, target_total: int = 50) -> List[QuestionItem]:
        """
        Generate a session's worth of questions.

        Args:
            target_total: Target number of questions

        Returns:
            List of QuestionItem
        """
        queue = []
        mode_a_count = 0
        mode_b_count = 0

        mode_a_questions = list(QUESTIONS_MODE_A.keys())
        mode_b_questions = list(QUESTIONS_MODE_B.keys())

        # Interleave Mode A and Mode B (roughly 55% A, 45% B based on sample size targets)
        while len(queue) < target_total:
            if self.rng.random() < 0.55:
                # Mode A
                item = self._generate_mode_a_question(mode_a_questions)
                if item:
                    queue.append(item)
                    mode_a_count += 1
            else:
                # Mode B
                item = self._generate_mode_b_question(mode_b_questions)
                if item:
                    queue.append(item)
                    mode_b_count += 1

        # Insert duplicate checks
        queue = self._insert_duplicate_checks(queue)

        self.question_queue = queue
        self.current_index = 0

        return queue

    def _generate_mode_a_question(self, questions: List[str]) -> Optional[QuestionItem]:
        """Generate a Mode A question."""
        # Pick a folio that hasn't been exhausted
        available_folios = [
            f for f in self.all_folios
            if f not in self.mode_a_folio_questions or
               len(self.mode_a_folio_questions[f]) < len(questions)
        ]

        if not available_folios:
            return None

        folio = self.rng.choice(available_folios)

        # Pick a question not yet asked for this folio
        asked = self.mode_a_folio_questions.get(folio, set())
        available_questions = [q for q in questions if q not in asked]

        if not available_questions:
            return None

        question = self.rng.choice(available_questions)

        # Track
        if folio not in self.mode_a_folio_questions:
            self.mode_a_folio_questions[folio] = set()
        self.mode_a_folio_questions[folio].add(question)

        return QuestionItem(
            mode="A",
            question_id=question,
            folio_id=folio
        )

    def _generate_mode_b_question(self, questions: List[str]) -> Optional[QuestionItem]:
        """Generate a Mode B question."""
        group_result = self.group_generator.generate_group()
        if not group_result:
            return None

        question = self.rng.choice(questions)

        return QuestionItem(
            mode="B",
            question_id=question,
            group_result=group_result
        )

    def _insert_duplicate_checks(self, queue: List[QuestionItem]) -> List[QuestionItem]:
        """Insert duplicate checks at configured rates."""
        result = list(queue)
        insertions = []

        for i, item in enumerate(queue):
            if item.mode == "A":
                if self.rng.random() < SESSION_CONFIG["mode_a_duplicate_rate"]:
                    dup = QuestionItem(
                        mode="A",
                        question_id=item.question_id,
                        folio_id=item.folio_id,
                        is_duplicate_check=True
                    )
                    # Insert later in queue
                    insert_pos = min(i + self.rng.randint(5, 15), len(queue) - 1)
                    insertions.append((insert_pos, dup))

            elif item.mode == "B":
                if self.rng.random() < SESSION_CONFIG["mode_b_duplicate_rate"]:
                    # Re-use same group with shuffled positions
                    new_positions = dict(zip(
                        item.group_result.folio_ids,
                        self.rng.sample(['A', 'B', 'C', 'D', 'E', 'F'][:len(item.group_result.folio_ids)],
                                       len(item.group_result.folio_ids))
                    ))
                    dup_group = GroupResult(
                        group_type=item.group_result.group_type,
                        group_basis=item.group_result.group_basis,
                        folio_ids=item.group_result.folio_ids,
                        position_mapping=new_positions,
                        is_hypothesis_driven=item.group_result.is_hypothesis_driven,
                        is_null=item.group_result.is_null,
                        is_foil=item.group_result.is_foil
                    )
                    dup = QuestionItem(
                        mode="B",
                        question_id=item.question_id,
                        group_result=dup_group,
                        is_duplicate_check=True
                    )
                    insert_pos = min(i + self.rng.randint(5, 15), len(queue) - 1)
                    insertions.append((insert_pos, dup))

        # Sort insertions by position and insert in reverse order
        for pos, item in sorted(insertions, key=lambda x: -x[0]):
            result.insert(pos, item)

        return result

    def get_current_question(self) -> Optional[QuestionItem]:
        """Get current question."""
        if self.current_index < len(self.question_queue):
            return self.question_queue[self.current_index]
        return None

    def advance(self) -> bool:
        """Advance to next question. Returns True if more questions remain."""
        self.current_index += 1
        return self.current_index < len(self.question_queue)

    def should_suggest_break(self) -> bool:
        """Check if should suggest a break."""
        return self.current_index > 0 and \
               self.current_index % SESSION_CONFIG["break_suggestion_at"] == 0

    def should_end_session(self) -> bool:
        """Check if session should end due to consecutive flags."""
        return self.consecutive_flags >= SESSION_CONFIG["consecutive_flags_to_end"]

    def record_flags(self, n_flags: int):
        """Record number of flags from last response."""
        if n_flags > 0:
            self.consecutive_flags += 1
        else:
            self.consecutive_flags = 0


# =============================================================================
# GUI WIDGETS
# =============================================================================

class ImageLabel(QLabel):
    """A label for displaying folio images with consistent sizing."""

    def __init__(self, min_height: int = 400):
        super().__init__()
        self.min_height = min_height
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(min_height)
        self.setStyleSheet("border: 2px solid #ccc; background-color: #f5f5f5;")

    def load_image(self, path: str) -> bool:
        """Load image from path. Returns True on success."""
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.setText("Image not found")
            return False

        # Scale to fit while maintaining aspect ratio
        scaled = pixmap.scaledToHeight(self.min_height, Qt.SmoothTransformation)
        self.setPixmap(scaled)
        return True


class ModeAWidget(QWidget):
    """Widget for Mode A single-image questions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_folio = None
        self.current_question_id = None
        self.timer = QElapsedTimer()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Image display
        self.image_label = ImageLabel(min_height=500)
        layout.addWidget(self.image_label, stretch=3)

        # Question text
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setFont(QFont("Arial", 12))
        self.question_label.setStyleSheet("padding: 10px; background-color: #e8e8e8;")
        layout.addWidget(self.question_label)

        # Options
        self.options_group = QGroupBox("Select one:")
        self.options_layout = QVBoxLayout(self.options_group)
        self.button_group = QButtonGroup(self)
        layout.addWidget(self.options_group, stretch=1)

        # Submit button
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setEnabled(False)
        self.submit_btn.setMinimumHeight(40)
        self.submit_btn.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(self.submit_btn)

        self.button_group.buttonClicked.connect(self._on_selection)

    def _on_selection(self, button):
        """Enable submit when option selected."""
        self.submit_btn.setEnabled(True)

    def load_question(self, folio_id: str, question_id: str, image_path: str):
        """Load a question for the given folio."""
        self.current_folio = folio_id
        self.current_question_id = question_id

        # Load image
        self.image_label.load_image(image_path)

        # Load question
        question_config = QUESTIONS_MODE_A.get(question_id, {})
        self.question_label.setText(question_config.get("template", "Question not found"))

        # Clear old options
        for btn in self.button_group.buttons():
            self.button_group.removeButton(btn)
            btn.deleteLater()

        # Clear layout
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new options
        options = question_config.get("options", [])
        for i, (value, description) in enumerate(options):
            if description:
                label = f"{value} - {description}"
            else:
                label = value
            btn = QRadioButton(label)
            btn.setProperty("value", value)
            self.button_group.addButton(btn, i)
            self.options_layout.addWidget(btn)

        # Reset state
        self.submit_btn.setEnabled(False)

        # Start timer
        self.timer.start()

    def get_response(self) -> Tuple[str, int]:
        """Get selected response and elapsed time."""
        checked = self.button_group.checkedButton()
        if checked:
            response = checked.property("value")
            elapsed = self.timer.elapsed()
            return response, elapsed
        return None, 0


class ModeBWidget(QWidget):
    """Widget for Mode B comparative questions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_folios = []
        self.current_positions = {}
        self.current_question_id = None
        self.timer = QElapsedTimer()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Images row
        images_widget = QWidget()
        self.images_layout = QHBoxLayout(images_widget)
        self.images_layout.setSpacing(10)
        layout.addWidget(images_widget, stretch=3)

        self.image_labels = []
        self.position_labels = []

        # Create 6 image slots (some may be hidden)
        for i in range(6):
            container = QVBoxLayout()

            pos_label = QLabel(chr(65 + i))  # A, B, C, ...
            pos_label.setAlignment(Qt.AlignCenter)
            pos_label.setFont(QFont("Arial", 14, QFont.Bold))
            container.addWidget(pos_label)
            self.position_labels.append(pos_label)

            img_label = ImageLabel(min_height=350)
            container.addWidget(img_label)
            self.image_labels.append(img_label)

            frame = QFrame()
            frame.setLayout(container)
            frame.setFrameStyle(QFrame.Box)
            self.images_layout.addWidget(frame)

        # Question text
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setFont(QFont("Arial", 12))
        self.question_label.setStyleSheet("padding: 10px; background-color: #e8e8e8;")
        layout.addWidget(self.question_label)

        # Options
        self.options_group = QGroupBox("Select one:")
        self.options_layout = QHBoxLayout(self.options_group)  # Horizontal for Mode B
        self.button_group = QButtonGroup(self)
        layout.addWidget(self.options_group)

        # Submit button
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setEnabled(False)
        self.submit_btn.setMinimumHeight(40)
        self.submit_btn.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(self.submit_btn)

        self.button_group.buttonClicked.connect(self._on_selection)

    def _on_selection(self, button):
        """Enable submit when option selected."""
        self.submit_btn.setEnabled(True)

    def load_question(self, group_result: GroupResult, question_id: str, metadata: Dict):
        """Load a comparative question."""
        self.current_folios = group_result.folio_ids
        self.current_positions = group_result.position_mapping
        self.current_question_id = question_id

        # Sort folios by position
        sorted_by_pos = sorted(
            group_result.position_mapping.items(),
            key=lambda x: x[1]  # Sort by A, B, C, D...
        )

        # Load images
        for i, (img_label, pos_label) in enumerate(zip(self.image_labels, self.position_labels)):
            if i < len(sorted_by_pos):
                folio_id, position = sorted_by_pos[i]
                pos_label.setText(position)
                pos_label.show()
                img_label.show()

                # Get image path
                meta = metadata.get(folio_id)
                if meta:
                    img_label.load_image(meta.image_path)
                else:
                    img_label.setText("No image")
            else:
                pos_label.hide()
                img_label.hide()

        # Load question
        question_config = QUESTIONS_MODE_B.get(question_id, {})
        self.question_label.setText(question_config.get("template", "Question not found"))

        # Clear old options
        for btn in self.button_group.buttons():
            self.button_group.removeButton(btn)
            btn.deleteLater()

        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new options
        options = question_config.get("options", [])

        # Filter to only relevant position options
        n_images = len(group_result.folio_ids)
        valid_positions = [chr(65 + i) for i in range(n_images)]

        for i, (value, description) in enumerate(options):
            # Skip position options not relevant
            if len(value) == 1 and value in 'ABCDEF' and value not in valid_positions:
                continue
            # Skip pairwise options not relevant
            if '-' in value and len(value) == 3:
                p1, p2 = value.split('-')
                if p1 not in valid_positions or p2 not in valid_positions:
                    continue

            if description:
                label = f"{value} - {description}"
            else:
                label = value

            btn = QRadioButton(label)
            btn.setProperty("value", value)
            self.button_group.addButton(btn, i)
            self.options_layout.addWidget(btn)

        self.submit_btn.setEnabled(False)
        self.timer.start()

    def get_response(self) -> Tuple[str, int]:
        """Get selected response and elapsed time."""
        checked = self.button_group.checkedButton()
        if checked:
            response = checked.property("value")
            elapsed = self.timer.elapsed()
            return response, elapsed
        return None, 0


# =============================================================================
# MAIN WINDOW
# =============================================================================

class AnnotationMainWindow(QMainWindow):
    """Main window for the annotation application."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Voynich Comparative Annotation System")
        self.setMinimumSize(1400, 900)

        # Initialize components
        self.metadata = load_folio_metadata()
        self.session_controller = SessionController()
        self.data_manager = AnnotationDataManager()

        # Delay timer (minimum time between submissions)
        self.delay_timer = QTimer()
        self.delay_timer.setSingleShot(True)
        self.delay_timer.timeout.connect(self._enable_submit)
        self.delay_active = False

        self.setup_ui()
        self.start_session()

    def setup_ui(self):
        """Set up the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header
        header = QHBoxLayout()
        self.mode_label = QLabel("Mode: -")
        self.mode_label.setFont(QFont("Arial", 11, QFont.Bold))
        header.addWidget(self.mode_label)
        header.addStretch()

        self.progress_label = QLabel("Question 0/0")
        self.progress_label.setFont(QFont("Arial", 11))
        header.addWidget(self.progress_label)

        layout.addLayout(header)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Stacked widget for modes
        self.mode_a_widget = ModeAWidget()
        self.mode_b_widget = ModeBWidget()

        # Connect submit buttons
        self.mode_a_widget.submit_btn.clicked.connect(self.submit_response)
        self.mode_b_widget.submit_btn.clicked.connect(self.submit_response)

        # Put in splitter for layout
        self.mode_a_widget.hide()
        self.mode_b_widget.hide()

        layout.addWidget(self.mode_a_widget, stretch=1)
        layout.addWidget(self.mode_b_widget, stretch=1)

        # Status bar
        self.statusBar().showMessage("Ready")

    def start_session(self):
        """Start a new annotation session."""
        target = SESSION_CONFIG["max_questions_per_session"]
        self.session_controller.generate_session(target_total=target)

        self.progress_bar.setMaximum(target)
        self.progress_bar.setValue(0)

        self.load_current_question()

    def load_current_question(self):
        """Load the current question."""
        question = self.session_controller.get_current_question()

        if question is None:
            self.end_session()
            return

        idx = self.session_controller.current_index + 1
        total = len(self.session_controller.question_queue)
        self.progress_label.setText(f"Question {idx}/{total}")
        self.progress_bar.setValue(idx)

        if question.mode == "A":
            self.mode_label.setText("Mode: Single Image")
            self.mode_a_widget.show()
            self.mode_b_widget.hide()

            meta = self.metadata.get(question.folio_id)
            if meta:
                self.mode_a_widget.load_question(
                    folio_id=question.folio_id,
                    question_id=question.question_id,
                    image_path=meta.image_path
                )
            else:
                self.statusBar().showMessage(f"Error: No metadata for {question.folio_id}")

        elif question.mode == "B":
            self.mode_label.setText("Mode: Comparative")
            self.mode_a_widget.hide()
            self.mode_b_widget.show()

            self.mode_b_widget.load_question(
                group_result=question.group_result,
                question_id=question.question_id,
                metadata=self.metadata
            )

        # Check for break suggestion
        if self.session_controller.should_suggest_break():
            reply = QMessageBox.question(
                self, "Break Time",
                f"You've completed {idx} questions.\nWould you like to take a short break?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                QMessageBox.information(
                    self, "Break",
                    "Take a moment to rest your eyes.\nClick OK when ready to continue."
                )

    def _enable_submit(self):
        """Re-enable submit buttons after delay."""
        self.delay_active = False

    def submit_response(self):
        """Handle response submission."""
        if self.delay_active:
            return

        question = self.session_controller.get_current_question()
        if question is None:
            return

        # Get response based on mode
        if question.mode == "A":
            response, elapsed = self.mode_a_widget.get_response()
            if response is None:
                return

            record = self.data_manager.record_mode_a(
                folio_id=question.folio_id,
                question_id=question.question_id,
                response=response,
                response_time_ms=elapsed,
                is_duplicate_check=question.is_duplicate_check
            )

            self.session_controller.record_flags(len(record.flags))

        elif question.mode == "B":
            response, elapsed = self.mode_b_widget.get_response()
            if response is None:
                return

            record = self.data_manager.record_mode_b(
                folio_ids=question.group_result.folio_ids,
                folio_positions=question.group_result.position_mapping,
                question_id=question.question_id,
                response=response,
                response_time_ms=elapsed,
                group_type=question.group_result.group_type.value,
                group_basis=question.group_result.group_basis,
                is_null_group=question.group_result.is_null,
                is_foil_group=question.group_result.is_foil,
                is_duplicate_check=question.is_duplicate_check
            )

            self.session_controller.record_flags(len(record.flags))

        # Check for session end due to flags
        if self.session_controller.should_end_session():
            QMessageBox.warning(
                self, "Session Ending",
                "Multiple flagged responses detected.\n"
                "Consider taking a break before continuing."
            )
            self.end_session()
            return

        # Start delay timer
        self.delay_active = True
        self.mode_a_widget.submit_btn.setEnabled(False)
        self.mode_b_widget.submit_btn.setEnabled(False)
        self.delay_timer.start(SESSION_CONFIG["min_delay_between_questions_ms"])

        # Advance to next question
        if self.session_controller.advance():
            self.load_current_question()
        else:
            self.end_session()

    def end_session(self):
        """End the current session."""
        self.data_manager.end_session()

        stats = self.data_manager.get_statistics()

        QMessageBox.information(
            self, "Session Complete",
            f"Session complete!\n\n"
            f"Mode A responses: {stats['mode_a_total']}\n"
            f"Mode B responses: {stats['mode_b_total']}\n\n"
            f"Data saved automatically."
        )

        # Offer to export
        reply = QMessageBox.question(
            self, "Export Data",
            "Would you like to export aggregated results now?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.data_manager.export_aggregated_features()
            self.data_manager.export_cohesion_analysis()
            self.data_manager.export_reliability_report()
            QMessageBox.information(
                self, "Export Complete",
                "Results exported to annotation_data/ folder."
            )

        # Option to continue or quit
        reply = QMessageBox.question(
            self, "Continue?",
            "Start another session?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.session_controller = SessionController()
            self.data_manager = AnnotationDataManager()
            self.start_session()
        else:
            self.close()

    def closeEvent(self, event):
        """Handle window close."""
        reply = QMessageBox.question(
            self, "Confirm Exit",
            "Are you sure you want to exit?\n"
            "Your progress has been auto-saved.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.data_manager.end_session()
            event.accept()
        else:
            event.ignore()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    window = AnnotationMainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
