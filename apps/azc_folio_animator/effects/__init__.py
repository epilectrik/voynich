"""Visual effects modules for AZC Folio Animator.

Effects are visual decoration only - no physics simulation.
Per AZC-ACT: tokens appear instantly, no movement.
"""
from .commitment_dimmer import CommitmentDimmer
from .weather_overlay import WeatherOverlay, WeatherParticle

__all__ = [
    'CommitmentDimmer',
    'WeatherOverlay', 'WeatherParticle'
]
