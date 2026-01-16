"""
Weather Overlay - HT ambient field as background texture.

Per C477 (Two-Axis Model): HT appears as ambient weather, not tokens.
- Background grain density varies per folio
- Micro-motion frequency changes with folio HT load
- High tail-middle pressure → denser, calmer background grain
- Low load → lighter but more complex texture

Implementation uses Perlin-like noise with density parameter.
"""
import math
import random
from typing import List, Tuple
from dataclasses import dataclass
from PyQt5.QtCore import QPointF, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QColor


@dataclass
class WeatherParticle:
    """A single particle in the weather overlay."""
    x: float
    y: float
    size: float
    alpha: float
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    phase: float = 0.0


class WeatherOverlay(QObject):
    """
    Generates and animates HT ambient weather effect.

    Weather properties:
    - density: How many particles (related to HT pressure)
    - complexity: How much motion/variation (related to TTR)
    - family: Color theme (zodiac = cool, ac = warm)

    Signals:
        particles_updated(): Emitted when particles change
    """

    particles_updated = pyqtSignal()

    def __init__(self, center: QPointF, radius: float, parent=None):
        super().__init__(parent)
        self.center = center
        self.radius = radius

        # Weather parameters
        self._density = 0.5
        self._complexity = 0.5
        self._family = 'zodiac'

        # Particles
        self._particles: List[WeatherParticle] = []

        # Animation
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._elapsed = 0.0

    def set_parameters(self, density: float, complexity: float, family: str):
        """Set weather parameters and regenerate particles."""
        self._density = max(0, min(1, density))
        self._complexity = max(0, min(1, complexity))
        self._family = family
        self._generate_particles()

    def start(self):
        """Start weather animation."""
        self._timer.start(50)  # 20 FPS

    def stop(self):
        """Stop weather animation."""
        self._timer.stop()

    def _generate_particles(self):
        """Generate particle field based on density."""
        self._particles.clear()

        # Number of particles based on density
        base_count = 30
        count = int(base_count * (0.3 + self._density * 0.7))

        for _ in range(count):
            # Random position within radius
            angle = random.random() * 2 * math.pi
            dist = random.random() * self.radius * 1.1

            x = self.center.x() + dist * math.cos(angle)
            y = self.center.y() + dist * math.sin(angle)

            # Size varies with density (denser = smaller, more uniform)
            if self._density > 0.7:
                size = 1 + random.random() * 1.5
            else:
                size = 1 + random.random() * 3

            # Alpha based on distance from center
            dist_factor = dist / self.radius
            alpha = 0.1 + 0.2 * (1 - dist_factor)

            # Velocity based on complexity
            if self._complexity > 0.5:
                # More complex = more motion
                vel_scale = 0.5 * self._complexity
                velocity_x = (random.random() - 0.5) * vel_scale
                velocity_y = (random.random() - 0.5) * vel_scale
            else:
                # Low complexity = calm, drift only
                velocity_x = (random.random() - 0.5) * 0.1
                velocity_y = (random.random() - 0.5) * 0.1

            particle = WeatherParticle(
                x=x, y=y, size=size, alpha=alpha,
                velocity_x=velocity_x, velocity_y=velocity_y,
                phase=random.random() * 2 * math.pi
            )
            self._particles.append(particle)

    def _animate(self):
        """Animation tick for weather motion."""
        self._elapsed += 0.05

        for particle in self._particles:
            # Update phase for pulsing
            particle.phase += 0.05 + self._complexity * 0.1

            # Apply velocity
            particle.x += particle.velocity_x
            particle.y += particle.velocity_y

            # Drift toward center (very slight)
            dx = self.center.x() - particle.x
            dy = self.center.y() - particle.y
            particle.x += dx * 0.001
            particle.y += dy * 0.001

            # Wrap around edges
            dist = math.sqrt(
                (particle.x - self.center.x())**2 +
                (particle.y - self.center.y())**2
            )
            if dist > self.radius * 1.2:
                # Respawn at random edge position
                angle = random.random() * 2 * math.pi
                particle.x = self.center.x() + self.radius * math.cos(angle)
                particle.y = self.center.y() + self.radius * math.sin(angle)

        self.particles_updated.emit()

    def get_particles(self) -> List[WeatherParticle]:
        """Get current particles for rendering."""
        return self._particles

    def get_base_color(self) -> QColor:
        """Get base color for family."""
        if self._family == 'zodiac':
            return QColor(0, 150, 180)  # Cool cyan
        else:
            return QColor(180, 120, 40)  # Warm amber

    def get_particle_color(self, particle: WeatherParticle) -> QColor:
        """Get color for a specific particle."""
        base = self.get_base_color()

        # Pulse alpha
        pulse = 0.7 + 0.3 * math.sin(particle.phase)
        alpha = int(particle.alpha * pulse * 255)

        return QColor(base.red(), base.green(), base.blue(), alpha)
