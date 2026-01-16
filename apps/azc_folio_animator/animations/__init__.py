"""Animation modules for AZC Folio Animator.

Per AZC-ACT: "No movement of tokens"
Tokens appear instantly at zone positions.
"""
from .binding_animator import BindingAnimator, PlacementState

__all__ = [
    'BindingAnimator', 'PlacementState'
]
