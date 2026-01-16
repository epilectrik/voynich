"""
Binding Pass Control - Play/pause/scrub control for token binding animation.

NOT called "timeline" because time implies execution.
This is a "binding pass" - specification-time positioning.
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSlider, QLabel, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal


class BindingPassControl(QWidget):
    """
    Control widget for binding pass animation.

    Signals:
        progress_changed(float): Emitted when progress changes (0.0 - 1.0)
        play_toggled(bool): Emitted when play state changes
    """

    progress_changed = pyqtSignal(float)
    play_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._playing = False
        self._progress = 0.0
        self._speed = 1.0

        self._build_ui()

        # Animation timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(50)  # 20 FPS base

    def _build_ui(self):
        """Build the control UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 5)

        # Play/Pause button
        self.play_btn = QPushButton("Play")
        self.play_btn.setFixedWidth(80)
        self.play_btn.clicked.connect(self._toggle_play)
        layout.addWidget(self.play_btn)

        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setFixedWidth(60)
        self.reset_btn.clicked.connect(self.reset)
        layout.addWidget(self.reset_btn)

        # Progress slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.setValue(0)
        self.slider.sliderMoved.connect(self._on_slider_moved)
        self.slider.sliderPressed.connect(self._on_slider_pressed)
        self.slider.sliderReleased.connect(self._on_slider_released)
        layout.addWidget(self.slider, stretch=1)

        # Progress label
        self.progress_label = QLabel("Binding Pass")
        self.progress_label.setStyleSheet("color: #7a8a9a; min-width: 100px;")
        layout.addWidget(self.progress_label)

        # Speed control
        layout.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1.0x", "2.0x", "4.0x"])
        self.speed_combo.setCurrentIndex(2)  # Default 1.0x
        self.speed_combo.currentTextChanged.connect(self._on_speed_changed)
        self.speed_combo.setStyleSheet("min-width: 60px;")
        layout.addWidget(self.speed_combo)

        self._update_label()

    def _toggle_play(self):
        """Toggle play/pause state."""
        if self._playing:
            self._pause()
        else:
            self._play()

    def _play(self):
        """Start playback."""
        self._playing = True
        self.play_btn.setText("Pause")
        self._timer.start()
        self.play_toggled.emit(True)

    def _pause(self):
        """Pause playback."""
        self._playing = False
        self.play_btn.setText("Play")
        self._timer.stop()
        self.play_toggled.emit(False)

    def reset(self):
        """Reset to beginning."""
        self._pause()
        self._progress = 0.0
        self.slider.setValue(0)
        self._update_label()
        self.progress_changed.emit(0.0)

    def _tick(self):
        """Animation tick."""
        # Advance progress
        increment = 0.005 * self._speed
        self._progress += increment

        if self._progress >= 1.0:
            self._progress = 1.0
            self._pause()

        # Update UI
        self.slider.blockSignals(True)
        self.slider.setValue(int(self._progress * 1000))
        self.slider.blockSignals(False)

        self._update_label()
        self.progress_changed.emit(self._progress)

    def _on_slider_moved(self, value: int):
        """Handle slider drag."""
        self._progress = value / 1000.0
        self._update_label()
        self.progress_changed.emit(self._progress)

    def _on_slider_pressed(self):
        """Handle slider press - pause while dragging."""
        if self._playing:
            self._timer.stop()

    def _on_slider_released(self):
        """Handle slider release - resume if was playing."""
        if self._playing:
            self._timer.start()

    def _on_speed_changed(self, text: str):
        """Handle speed change."""
        try:
            self._speed = float(text.rstrip('x'))
        except ValueError:
            self._speed = 1.0

    def _update_label(self):
        """Update progress label."""
        percent = int(self._progress * 100)
        self.progress_label.setText(f"Binding Pass: {percent}%")

    def set_progress(self, progress: float):
        """Set progress externally."""
        self._progress = max(0.0, min(1.0, progress))
        self.slider.setValue(int(self._progress * 1000))
        self._update_label()

    @property
    def progress(self) -> float:
        """Get current progress."""
        return self._progress

    @property
    def is_playing(self) -> bool:
        """Get playing state."""
        return self._playing
