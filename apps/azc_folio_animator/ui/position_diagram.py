"""
Position Diagram - AZC Constraint Field Visualization.

Shows constraints ACTING on a single Currier A line (bundle).
NOT a placement map or population view.

Key principle:
> "A constraint field that acts on a single attempted specification."

POSITIONAL GRAMMAR (F-AZC-005):
- Rings represent LINE POSITION ZONES, not filtering stages
- C: Early (mean 0.35) - first ~35% of line
- P: Early-Mid (mean 0.44) - ~35-50% of line
- R: Late-Mid (mean 0.67) - ~50-75% of line
- S: Late (mean 0.79) - last ~25% of line

Tokens appear at their designated position based on where they
occurred in the source line. MIDDLE compatibility determines
whether a token survives (4.3% of MIDDLE pairs are legal).
"""
import math
import re
from enum import Enum
from typing import List, Optional, Dict, Set
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QTransform
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.azc_folio_animator.core.folio_loader import TokenData, FolioData
from apps.azc_folio_animator.core.azc_engine import AZCEngine, ZoneCategory, EscapeClass


# Position zone thresholds (from F-AZC-005)
POSITION_ZONES = {
    'C': {'min': 0.00, 'max': 0.39, 'mean': 0.349, 'label': 'Early'},
    'P': {'min': 0.39, 'max': 0.55, 'mean': 0.436, 'label': 'Early-Mid'},
    'R': {'min': 0.55, 'max': 0.73, 'mean': 0.666, 'label': 'Late-Mid'},
    'S': {'min': 0.73, 'max': 1.00, 'mean': 0.785, 'label': 'Late'},
}


def extract_middle(token_text: str) -> str:
    """
    Extract MIDDLE component from a Voynich token.

    MIDDLE is the core component between PREFIX and SUFFIX.
    Common MIDDLEs: ol, or, al, ar, ain, aiin, etc.
    """
    # Simple extraction: strip common prefixes and suffixes
    text = token_text.lower()

    # Common prefixes to strip
    prefixes = ['qok', 'qot', 'qo', 'ch', 'sh', 'ok', 'ot', 'ct', 's', 'k', 'd']
    for p in prefixes:
        if text.startswith(p) and len(text) > len(p):
            text = text[len(p):]
            break

    # Common suffixes to strip
    suffixes = ['y', 'dy', 'ey', 'ly', 'ry', 'chy', 'shy']
    for s in suffixes:
        if text.endswith(s) and len(text) > len(s):
            text = text[:-len(s)]
            break

    return text if text else token_text


def get_position_zone(norm_pos: float) -> str:
    """Get the phase/ring for a normalized position (0-1)."""
    for phase, zone in POSITION_ZONES.items():
        if zone['min'] <= norm_pos < zone['max']:
            return phase
    return 'S'  # Default to late if at end


class TokenState(Enum):
    """Token placement states (simplified - no animation)."""
    PLACED = 1        # Token is placed in zone (instant)


class RingItem(QGraphicsEllipseItem):
    """A phase ring in the constraint field."""

    def __init__(self, radius: float, center: QPointF, phase: str, color: str, parent=None):
        diameter = radius * 2
        super().__init__(
            center.x() - radius,
            center.y() - radius,
            diameter,
            diameter,
            parent
        )
        self.phase = phase
        self.base_color = QColor(color)
        self._active = False
        self._pulse = 0.0

        self._update_style()

    def _update_style(self):
        """Update ring appearance."""
        color = QColor(self.base_color)
        if self._active:
            color.setAlpha(180)
            width = 3
        else:
            color.setAlpha(80)
            width = 1.5

        # Pulse effect
        if self._pulse > 0:
            boost = int(60 * math.sin(self._pulse * math.pi))
            color.setAlpha(min(255, color.alpha() + boost))

        self.setPen(QPen(color, width))
        self.setBrush(QBrush(Qt.NoBrush))

    def set_active(self, active: bool):
        """Set whether this ring is currently active."""
        self._active = active
        self._update_style()

    def pulse(self, value: float):
        """Set pulse animation value (0-1)."""
        self._pulse = value
        self._update_style()


class TangentTokenItem(QGraphicsTextItem):
    """
    A token rendered tangentially along a ring.

    Text follows the ring curvature with proper rotation.
    """

    def __init__(self, text: str, font: QFont, color: QColor,
                 center: QPointF, radius: float, angle: float, parent=None):
        super().__init__(text, parent)
        self.token_text = text
        self._center = center
        self._radius = radius
        self._angle = angle  # radians
        self._opacity = 1.0
        self._state = TokenState.PLACED

        # Set font and color
        self.setFont(font)
        self.setDefaultTextColor(color)

        # Position and rotate
        self._update_transform()

    def _update_transform(self):
        """Position token tangentially on ring."""
        # Calculate position on ring
        x = self._center.x() + self._radius * math.cos(self._angle)
        y = self._center.y() + self._radius * math.sin(self._angle)

        # Rotation: tangent to ring (perpendicular to radius)
        # Add 90 degrees so text baseline follows ring
        rotation_deg = math.degrees(self._angle) + 90

        # Keep text readable (not upside down)
        if 90 < rotation_deg < 270:
            rotation_deg += 180

        # Center the text on position
        rect = self.boundingRect()
        self.setTransformOriginPoint(rect.width() / 2, rect.height() / 2)
        self.setRotation(rotation_deg)
        self.setPos(x - rect.width() / 2, y - rect.height() / 2)
        self.setOpacity(self._opacity)

    def set_radius(self, radius: float):
        """Move token to new radius (phase change)."""
        self._radius = radius
        self._update_transform()

    def set_angle(self, angle: float):
        """Set angular position."""
        self._angle = angle
        self._update_transform()

    def set_opacity(self, opacity: float):
        """Set opacity for fading."""
        self._opacity = max(0, min(1, opacity))
        self.setOpacity(self._opacity)

    def set_state(self, state: TokenState):
        """Set token state."""
        self._state = state


class PositionDiagram(QGraphicsView):
    """
    AZC Constraint Field Diagram.

    Shows constraint action on a single Currier A line (bundle).
    Tokens enter together, compatibility acts, survivors proceed or vanish.

    Rules:
    - Diagram starts EMPTY
    - Max 3 tokens visible at Entry (C)
    - Reduces through phases
    - Clears after commit
    """

    # Signals
    phase_complete = pyqtSignal(str)  # Emitted when phase completes
    bundle_complete = pyqtSignal(bool)  # True if committed, False if collapsed

    def __init__(self, engine: AZCEngine, voynich_font: QFont, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.voynich_font = voynich_font

        # Visual settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setBackgroundBrush(QBrush(QColor(8, 15, 25)))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setStyleSheet("""
            QGraphicsView {
                border: 1px solid #1a2a3a;
                border-radius: 4px;
            }
        """)

        # Enable interactive zoom and pan
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self._zoom_level = 1.0
        self._min_zoom = 0.3
        self._max_zoom = 15.0

        # PERFORMANCE: Optimize rendering (but keep text crisp)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheBackground)
        # NOTE: Removed DontAdjustForAntialiasing - it causes blurry text when zooming
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)

        # Create scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Diagram dimensions (large for big constraint bundles)
        self.diagram_radius = 450
        self.center = QPointF(0, 0)

        # Storage
        self.rings: dict = {}
        self.labels: dict = {}
        self.active_tokens: List[TangentTokenItem] = []
        self.scaffold_items: List[QGraphicsTextItem] = []  # Static folio text (Layer A)

        # Animation state
        self._animation_phase = 0.0
        self._current_phase = None
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)

        # Build diagram (empty rings)
        self._build_diagram()

    def _build_diagram(self):
        """Build empty ring structure."""
        self.scene.clear()
        self.rings.clear()
        self.labels.clear()
        self.active_tokens.clear()

        # Draw ambient background
        self._draw_background()

        # Draw phase rings: C → P → R → S
        phases = self.engine.phase_order

        for phase in phases:
            positions = self.engine.phases.get(phase, [phase])
            if positions:
                radius_factor = self.engine.get_radius(positions[0])
                radius = self.diagram_radius * radius_factor
                color = self.engine.get_color(positions[0])

                ring = RingItem(radius, self.center, phase, color)
                self.scene.addItem(ring)
                self.rings[phase] = ring

                # Phase label with position zone info
                zone_info = POSITION_ZONES.get(phase, {})
                zone_label = zone_info.get('label', '')
                zone_mean = zone_info.get('mean', 0)

                if zone_label:
                    # Full label: "C - Early (0.35)"
                    display = f"{phase} - {zone_label} ({zone_mean:.2f})"
                else:
                    display = self.engine.get_phase_display(phase)

                label = QGraphicsTextItem(display)
                label.setDefaultTextColor(QColor(130, 150, 170, 180))
                label.setFont(QFont("Arial", 9, QFont.Bold))

                label_rect = label.boundingRect()
                label.setPos(
                    self.center.x() - label_rect.width() / 2,
                    self.center.y() - radius - 20
                )
                self.scene.addItem(label)
                self.labels[phase] = label

                # Add position range label below
                if zone_info:
                    range_text = f"[{zone_info.get('min', 0):.0%}-{zone_info.get('max', 1):.0%}]"
                    range_label = QGraphicsTextItem(range_text)
                    range_label.setDefaultTextColor(QColor(100, 120, 140, 120))
                    range_label.setFont(QFont("Arial", 7))
                    range_rect = range_label.boundingRect()
                    range_label.setPos(
                        self.center.x() - range_rect.width() / 2,
                        self.center.y() - radius - 8
                    )
                    self.scene.addItem(range_label)

        # Center point
        center_dot = QGraphicsEllipseItem(-3, -3, 6, 6)
        center_dot.setPen(QPen(Qt.NoPen))
        center_dot.setBrush(QBrush(QColor(100, 120, 140, 80)))
        self.scene.addItem(center_dot)

        # Set scene rect
        margin = 60
        size = (self.diagram_radius + margin) * 2
        self.scene.setSceneRect(-size/2, -size/2, size, size)

    def _draw_background(self):
        """Draw subtle ambient background."""
        gradient = QRadialGradient(self.center, self.diagram_radius * 1.2)

        if self.engine.family == 'zodiac':
            base = QColor(0, 80, 100)
        else:
            base = QColor(100, 60, 20)

        gradient.setColorAt(0, QColor(base.red(), base.green(), base.blue(), 20))
        gradient.setColorAt(0.7, QColor(base.red(), base.green(), base.blue(), 8))
        gradient.setColorAt(1, QColor(8, 15, 25, 0))

        bg = QGraphicsEllipseItem(
            -self.diagram_radius * 1.2,
            -self.diagram_radius * 1.2,
            self.diagram_radius * 2.4,
            self.diagram_radius * 2.4
        )
        bg.setBrush(QBrush(gradient))
        bg.setPen(QPen(Qt.NoPen))
        bg.setZValue(-10)
        self.scene.addItem(bg)

    def clear_tokens(self):
        """Clear all tokens from diagram."""
        for token in self.active_tokens:
            self.scene.removeItem(token)
        self.active_tokens.clear()

        # Reset ring states
        for ring in self.rings.values():
            ring.set_active(False)

        # Reset scaffold highlights
        self._reset_scaffold_highlights()

    def inject_bundle(self, tokens: List[TokenData]):
        """
        Inject a Currier A line bundle into the diagram.

        INSTANT APPEARANCE per AZC-ACT:
        - "No movement of tokens"
        - Tokens appear immediately at their zone position

        Control operators (1-token entries) are filtered per C484.
        """
        self.clear_tokens()
        self._reset_scaffold_highlights()

        if not tokens:
            return

        # Filter out control operators (C484: meta-structural, not registry content)
        registry_tokens = [t for t in tokens if not t.is_control_operator]

        if not registry_tokens:
            # Show message if only control operators
            label = QGraphicsTextItem("Control operators only")
            label.setDefaultTextColor(QColor(150, 150, 150, 180))
            label.setFont(QFont("Arial", 10))
            rect = label.boundingRect()
            label.setPos(-rect.width() / 2, 0)
            label.setZValue(15)
            self.scene.addItem(label)
            self.active_tokens.append(label)
            return

        # Calculate normalized position for each token
        line_length = len(registry_tokens)
        if line_length == 0:
            return

        # Use registry_tokens for the rest
        tokens = registry_tokens

        # Group tokens by their position zone
        tokens_by_zone: Dict[str, List[tuple]] = {phase: [] for phase in self.engine.phase_order}

        # Extract scaffold MIDDLEs for compatibility checking
        scaffold_middles = self._get_scaffold_middles()

        for i, token in enumerate(tokens):
            # Normalize position: 0 = start, 1 = end
            norm_pos = i / max(1, line_length - 1) if line_length > 1 else 0.5

            # Determine which ring this token belongs to
            zone = get_position_zone(norm_pos)

            # Extract MIDDLE for compatibility check
            middle = extract_middle(token.text)
            is_compatible, matching_items = self._check_middle_compatibility_with_items(middle, zone)

            tokens_by_zone[zone].append((token, norm_pos, middle, is_compatible, matching_items))

        # Get ring radii for calculating "between" positions
        ring_radii = {}
        for phase in self.engine.phase_order:
            positions = self.engine.phases.get(phase, [phase])
            if positions:
                ring_radii[phase] = self.diagram_radius * self.engine.get_radius(positions[0])

        # Place tokens BETWEEN their respective rings
        phases = self.engine.phase_order
        for idx, phase in enumerate(phases):
            phase_tokens = tokens_by_zone.get(phase, [])
            if not phase_tokens:
                continue

            # Calculate position between rings
            outer_radius = ring_radii.get(phase, self.diagram_radius * 0.3)
            if idx > 0:
                inner_radius = ring_radii.get(phases[idx - 1], 0)
            else:
                inner_radius = 0  # Center

            # Place tokens at midpoint between rings
            token_radius = (inner_radius + outer_radius) / 2
            ring_color = QColor(self.engine.get_color(phase))

            # Activate ring if it has tokens
            if phase in self.rings:
                self.rings[phase].set_active(True)

            # C233: LINE_ATOMIC - large bundles are by design, show all tokens
            # Distribute tokens around the full ring arc for large bundles
            display_tokens = phase_tokens
            num_tokens = len(display_tokens)

            # Distribute around arc - expand spread for large bundles
            base_angle = -math.pi / 2  # Top
            # Scale spread based on token count: small bundles get narrow arc, large get wider
            if num_tokens <= 5:
                spread = math.pi / 3  # 60 degrees
            elif num_tokens <= 10:
                spread = math.pi / 2  # 90 degrees
            elif num_tokens <= 20:
                spread = math.pi * 0.8  # 144 degrees
            else:
                spread = math.pi * 1.2  # 216 degrees for very large bundles

            for j, (token, norm_pos, middle, is_compatible, matching_items) in enumerate(display_tokens):
                if num_tokens == 1:
                    angle = base_angle
                else:
                    angle = base_angle + spread * (j - (num_tokens - 1) / 2) / max(1, num_tokens - 1)

                # All tokens get ring color (no red incompatible marking)
                color = QColor(ring_color)
                color.setAlpha(255)

                # ILLUMINATE matching scaffold tokens
                if matching_items:
                    self._illuminate_matches(matching_items)

                font = QFont(self.voynich_font)
                # Scale font size for large bundles to prevent overlap
                if num_tokens <= 10:
                    font.setPointSize(12)
                elif num_tokens <= 20:
                    font.setPointSize(10)
                else:
                    font.setPointSize(8)  # Small for very large bundles

                token_item = TangentTokenItem(
                    token.text, font, color,
                    self.center, token_radius, angle
                )
                token_item.set_state(TokenState.PLACED)
                token_item.setZValue(10)
                self.scene.addItem(token_item)
                self.active_tokens.append(token_item)

        # Set current phase to first active one
        for phase in self.engine.phase_order:
            if phase in self.rings and self.rings[phase]._active:
                self._current_phase = phase
                break

        # Show pipeline exit view (what B receives)
        self._show_pipeline_exit(tokens)

    def _show_pipeline_exit(self, tokens: List[TokenData]):
        """
        Show pipeline exit view in center.

        Per AZC-B-ACT: B receives legality class only.
        B is blind to A content - only sees categorical output.
        """
        if not tokens:
            return

        # Determine dominant zone from token placements
        zone_counts = {'C': 0, 'P': 0, 'R': 0, 'S': 0}
        for token in tokens:
            zone = self.engine.get_zone_for_position(token.placement)
            if zone in zone_counts:
                zone_counts[zone] += 1

        dominant_zone = max(zone_counts, key=zone_counts.get) if any(zone_counts.values()) else 'C'

        # Get categorical output
        category = self.engine.get_zone_category(dominant_zone)
        escape_class = self.engine.get_escape_class(dominant_zone)
        intervention = self.engine.is_intervention_permitted(dominant_zone)

        # Colors
        if category == ZoneCategory.INTERIOR:
            cat_color = QColor(100, 200, 255)  # Blue for interior
        else:
            cat_color = QColor(255, 180, 100)  # Amber for boundary

        escape_colors = {
            EscapeClass.HIGH: QColor(100, 255, 150),
            EscapeClass.MODERATE: QColor(180, 220, 140),
            EscapeClass.RESTRICTING: QColor(255, 200, 100),
            EscapeClass.ZERO: QColor(255, 120, 120)
        }

        # Build compact center display
        y_offset = -30

        # Legality class (the main output)
        cat_label = QGraphicsTextItem(category.value)
        cat_label.setDefaultTextColor(cat_color)
        cat_label.setFont(QFont("Arial", 14, QFont.Bold))
        cat_rect = cat_label.boundingRect()
        cat_label.setPos(-cat_rect.width() / 2, y_offset)
        cat_label.setZValue(20)
        self.scene.addItem(cat_label)
        self.active_tokens.append(cat_label)

        # Escape class
        y_offset += 22
        escape_label = QGraphicsTextItem(escape_class.value)
        escape_label.setDefaultTextColor(escape_colors.get(escape_class, QColor(200, 200, 200)))
        escape_label.setFont(QFont("Arial", 10))
        esc_rect = escape_label.boundingRect()
        escape_label.setPos(-esc_rect.width() / 2, y_offset)
        escape_label.setZValue(20)
        self.scene.addItem(escape_label)
        self.active_tokens.append(escape_label)

        # Intervention indicator (small, subtle)
        y_offset += 18
        int_text = "intervention permitted" if intervention else "no intervention"
        int_color = QColor(120, 180, 140, 180) if intervention else QColor(180, 120, 120, 180)
        int_label = QGraphicsTextItem(int_text)
        int_label.setDefaultTextColor(int_color)
        int_label.setFont(QFont("Arial", 8))
        int_rect = int_label.boundingRect()
        int_label.setPos(-int_rect.width() / 2, y_offset)
        int_label.setZValue(20)
        self.scene.addItem(int_label)
        self.active_tokens.append(int_label)

    def _reset_scaffold_highlights(self):
        """Reset all scaffold items to default ghosted appearance."""
        if not hasattr(self, 'scaffold_items'):
            return
        for item in self.scaffold_items:
            # Reset to ghosted color
            base_opacity = 0.22
            # Get original color from item's data or use default
            color = QColor(100, 150, 180, int(255 * base_opacity))
            item.setDefaultTextColor(color)

    def _illuminate_matches(self, matching_items: List[QGraphicsTextItem]):
        """Illuminate scaffold items that match an injected token."""
        for item in matching_items:
            # Bright highlight color
            highlight_color = QColor(100, 255, 180, 220)  # Bright green
            item.setDefaultTextColor(highlight_color)

    def illuminate_by_token_text(self, token_text: str, positions: list = None):
        """
        Illuminate scaffold items matching the given token text.

        Used by the token-centric multi-folio view to highlight where
        a clicked token appears in this folio's constraint field.

        Args:
            token_text: The exact token text to match
            positions: Optional list of TokenData positions for adding if not in scaffold
        """
        self._reset_scaffold_highlights()

        illuminated_count = 0
        for item in self.scaffold_items:
            if hasattr(item, 'toPlainText') and item.toPlainText() == token_text:
                # Bright illumination - cyan/green glow
                highlight_color = QColor(100, 255, 180, 255)
                item.setDefaultTextColor(highlight_color)
                illuminated_count += 1

        # If token wasn't in sampled scaffold but we have positions, add it
        if illuminated_count == 0 and positions:
            highlight_color = QColor(100, 255, 180, 255)
            highlight_font = QFont(self.voynich_font)
            highlight_font.setPointSize(11)
            highlight_font.setBold(True)

            for token_data in positions:
                # Get phase and calculate position
                phase = token_data.phase if hasattr(token_data, 'phase') else 'C'
                phase_positions = self.engine.phases.get(phase, [phase])
                if not phase_positions:
                    continue

                radius = self.diagram_radius * self.engine.get_radius(phase_positions[0])

                # Place at a visible angle (top of ring)
                angle = -math.pi / 2

                # Create highlighted text item
                item = QGraphicsTextItem(token_text)
                item.setFont(highlight_font)
                item.setDefaultTextColor(highlight_color)

                # Position on ring
                x = self.center.x() + radius * math.cos(angle)
                y = self.center.y() + radius * math.sin(angle)

                rotation_deg = math.degrees(angle) + 90
                if 90 < rotation_deg < 270:
                    rotation_deg += 180

                rect = item.boundingRect()
                item.setTransformOriginPoint(rect.width() / 2, rect.height() / 2)
                item.setRotation(rotation_deg)
                item.setPos(x - rect.width() / 2, y - rect.height() / 2)
                item.setZValue(15)  # Above scaffold

                self.scene.addItem(item)
                self.scaffold_items.append(item)  # Track for cleanup
                illuminated_count += 1
                break  # Only add once per diagram

        return illuminated_count

    def illuminate_by_middle(self, clicked_token: str, related_tokens: List[str], positions: list = None):
        """
        Illuminate all tokens sharing the same MIDDLE as the clicked token.

        Per C472: MIDDLE is primary carrier of folio specificity.
        This highlights the full MIDDLE family, not just exact token matches.

        Args:
            clicked_token: The token that was clicked (for primary highlight)
            related_tokens: All tokens in this folio sharing the same MIDDLE
            positions: TokenData positions for all related tokens
        """
        self._reset_scaffold_highlights()

        illuminated_count = 0
        related_set = set(related_tokens)

        # First pass: illuminate matching scaffold items
        for item in self.scaffold_items:
            if hasattr(item, 'toPlainText'):
                item_text = item.toPlainText()
                if item_text in related_set:
                    # Primary token gets brighter color
                    if item_text == clicked_token:
                        highlight_color = QColor(100, 255, 180, 255)  # Bright green
                    else:
                        highlight_color = QColor(80, 200, 160, 220)  # Slightly dimmer for related
                    item.setDefaultTextColor(highlight_color)
                    illuminated_count += 1

        # If none found in scaffold, add the primary token
        if illuminated_count == 0 and positions:
            highlight_color = QColor(100, 255, 180, 255)
            highlight_font = QFont(self.voynich_font)
            highlight_font.setPointSize(11)
            highlight_font.setBold(True)

            # Use first position
            token_data = positions[0]
            phase = token_data.phase if hasattr(token_data, 'phase') else 'C'
            phase_positions = self.engine.phases.get(phase, [phase])
            if phase_positions:
                radius = self.diagram_radius * self.engine.get_radius(phase_positions[0])
                angle = -math.pi / 2  # Top of ring

                item = QGraphicsTextItem(clicked_token)
                item.setFont(highlight_font)
                item.setDefaultTextColor(highlight_color)

                x = self.center.x() + radius * math.cos(angle)
                y = self.center.y() + radius * math.sin(angle)

                rotation_deg = math.degrees(angle) + 90
                if 90 < rotation_deg < 270:
                    rotation_deg += 180

                rect = item.boundingRect()
                item.setTransformOriginPoint(rect.width() / 2, rect.height() / 2)
                item.setRotation(rotation_deg)
                item.setPos(x - rect.width() / 2, y - rect.height() / 2)
                item.setZValue(15)

                self.scene.addItem(item)
                self.scaffold_items.append(item)
                illuminated_count += 1

        return illuminated_count

    def _check_middle_compatibility_with_items(self, middle: str, phase: str) -> tuple:
        """
        Check MIDDLE compatibility and return matching scaffold items.

        Returns (is_compatible, list_of_matching_items)

        PERFORMANCE: Uses stored phase data instead of distance calculations.
        """
        matching_items = []
        phase_scaffold_count = 0

        for item in self.scaffold_items:
            if not hasattr(item, 'toPlainText'):
                continue

            # PERFORMANCE: Use stored phase instead of calculating distance
            item_phase = item.data(0)
            if item_phase != phase:
                continue

            phase_scaffold_count += 1
            text = item.toPlainText()
            scaffold_middle = extract_middle(text)

            # Check for match
            if middle == scaffold_middle:
                matching_items.append(item)
            elif middle in scaffold_middle or scaffold_middle in middle:
                matching_items.append(item)
            elif len(middle) >= 2 and len(scaffold_middle) >= 2 and middle[:2] == scaffold_middle[:2]:
                matching_items.append(item)

        # Compatible if: has matches, OR this phase has no scaffold tokens
        is_compatible = len(matching_items) > 0 or phase_scaffold_count == 0
        return is_compatible, matching_items

    def _get_scaffold_middles(self) -> Dict[str, Set[str]]:
        """Extract MIDDLEs from scaffold tokens, grouped by phase.

        PERFORMANCE: Uses stored phase data instead of distance calculations.
        """
        middles_by_phase: Dict[str, Set[str]] = {phase: set() for phase in self.engine.phase_order}

        for item in self.scaffold_items:
            if hasattr(item, 'toPlainText'):
                text = item.toPlainText()
                middle = extract_middle(text)

                # PERFORMANCE: Use stored phase instead of calculating distance
                phase = item.data(0)
                if phase in middles_by_phase:
                    middles_by_phase[phase].add(middle)

        return middles_by_phase

    def _check_middle_compatibility(self, middle: str, phase: str, scaffold_middles: Dict[str, Set[str]]) -> bool:
        """
        Check if a MIDDLE is compatible with the scaffold at this phase.

        Returns True if the MIDDLE appears in the scaffold for this phase,
        or if scaffold is empty (no constraints).
        """
        phase_middles = scaffold_middles.get(phase, set())

        if not phase_middles:
            return True  # No scaffold = no constraints

        # Check if this MIDDLE or a similar one exists in scaffold
        if middle in phase_middles:
            return True

        # Partial match: check if MIDDLE is substring or shares common core
        for scaffold_middle in phase_middles:
            if middle in scaffold_middle or scaffold_middle in middle:
                return True
            # Common core check (first 2 chars match)
            if len(middle) >= 2 and len(scaffold_middle) >= 2:
                if middle[:2] == scaffold_middle[:2]:
                    return True

        return False

    def _complete_bundle(self):
        """Complete bundle processing and clear."""
        had_survivors = len(self.active_tokens) > 0
        self.clear_tokens()
        self._current_phase = None
        self.bundle_complete.emit(had_survivors)

    def _animate(self):
        """Animation tick - minimal, no physics."""
        # Per AZC-ACT: no movement of tokens
        # Animation reduced to simple ring highlight
        pass

    def set_family(self, family: str):
        """Switch family topology."""
        if family != self.engine.family:
            self.engine.set_family(family)
            self._build_diagram()

    def set_scaffold_folio(self, folio: FolioData):
        """
        Build the static scaffold layer from AZC folio text.

        This is Layer A - the constraint field itself.
        Always visible, ghosted, never animates.
        """
        # Clear existing scaffold
        self._clear_scaffold()

        if not folio or not folio.tokens:
            return

        # Group tokens by phase
        phase_tokens = {phase: [] for phase in self.engine.phase_order}

        for token in folio.tokens:
            phase = token.phase
            if phase in phase_tokens:
                phase_tokens[phase].append(token)

        # Scaffold visual settings
        scaffold_opacity = 0.22
        scaffold_font = QFont(self.voynich_font)
        scaffold_font.setPointSize(9)

        # PERFORMANCE: Reduced from 40 to 12 - fewer items = faster rendering
        max_tokens_per_ring = 12

        # Build scaffold for each ring
        for phase in self.engine.phase_order:
            tokens = phase_tokens.get(phase, [])
            if not tokens:
                continue

            # Get ring properties
            positions = self.engine.phases.get(phase, [phase])
            if not positions:
                continue

            radius = self.diagram_radius * self.engine.get_radius(positions[0])
            base_color = QColor(self.engine.get_color(positions[0]))

            # Ghosted color
            scaffold_color = QColor(base_color)
            scaffold_color.setAlpha(int(255 * scaffold_opacity))

            # Sample tokens if too many (evenly distributed)
            if len(tokens) > max_tokens_per_ring:
                step = len(tokens) / max_tokens_per_ring
                tokens = [tokens[int(i * step)] for i in range(max_tokens_per_ring)]

            # Distribute tokens around full ring with spacing
            num_tokens = len(tokens)
            for i, token in enumerate(tokens):
                # Full circle distribution
                angle = (i / num_tokens) * 2 * math.pi - math.pi / 2  # Start at top

                # Create scaffold text item
                item = QGraphicsTextItem(token.text)
                item.setFont(scaffold_font)
                item.setDefaultTextColor(scaffold_color)

                # Position tangentially (same math as TangentTokenItem)
                x = self.center.x() + radius * math.cos(angle)
                y = self.center.y() + radius * math.sin(angle)

                rotation_deg = math.degrees(angle) + 90
                if 90 < rotation_deg < 270:
                    rotation_deg += 180

                rect = item.boundingRect()
                item.setTransformOriginPoint(rect.width() / 2, rect.height() / 2)
                item.setRotation(rotation_deg)
                item.setPos(x - rect.width() / 2, y - rect.height() / 2)

                # Z-index: below active tokens, above rings
                item.setZValue(1)

                # NOTE: Do NOT use ItemCoordinateCache for text - it causes pixelation when zooming
                # Text items should render fresh at each zoom level for crispness

                # PERFORMANCE: Store phase directly to avoid distance calculations later
                item.setData(0, phase)  # Qt data role 0 = custom phase storage

                self.scene.addItem(item)
                self.scaffold_items.append(item)

    def _clear_scaffold(self):
        """Clear scaffold items only."""
        for item in self.scaffold_items:
            self.scene.removeItem(item)
        self.scaffold_items.clear()

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        # IMPORTANT: Accept event to prevent propagation to parent scrollbar
        event.accept()

        # Zoom factor
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        # Get zoom direction
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        # Check zoom limits
        new_zoom = self._zoom_level * zoom_factor
        if new_zoom < self._min_zoom or new_zoom > self._max_zoom:
            return

        # PERFORMANCE: Disable updates during zoom, then re-enable
        self.setUpdatesEnabled(False)
        self._zoom_level = new_zoom
        self.scale(zoom_factor, zoom_factor)
        self.setUpdatesEnabled(True)

    def reset_view(self):
        """Reset zoom and position to default."""
        self.resetTransform()
        self._zoom_level = 1.0
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        """Handle resize."""
        super().resizeEvent(event)
        # Only fit on initial resize, not after user has zoomed
        if self._zoom_level == 1.0:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
