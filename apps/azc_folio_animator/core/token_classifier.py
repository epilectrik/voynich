"""
Token Classifier - Classifies tokens by their AZC distribution.

ARCHITECTURE (per C441, C472):
- Activation is MIDDLE-based, not full token text
- C472: MIDDLE is primary carrier of folio specificity (77% exclusive)
- Classification counts how many AZC folios contain the token's MIDDLE

Token types:
- LOCALIZED (1-3 folios): Content tokens, fully interactive
- DISTRIBUTED (4-9 folios): Mixed tokens, interactive but muted
- STRUCTURAL (10+ folios): Grammar tokens (daiin, aiin, etc.), de-emphasized

This classification drives UI styling in the A-text strip.
"""
from enum import Enum
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.azc_folio_animator.core.azc_folio_model import AZCFolioRegistry


class TokenType(Enum):
    """Token classification by AZC distribution."""
    LOCALIZED = 1      # 1-3 folios - content tokens
    DISTRIBUTED = 2    # 4-9 folios - mixed
    STRUCTURAL = 3     # 10+ folios - grammar (daiin, aiin, etc.)
    NO_AZC_MAPPING = 4 # 0 folios - MIDDLE not in AZC vocabulary


class TokenClassifier:
    """
    Classifies tokens by AZC distribution for UI styling.

    Based on empirical analysis:
    - 82.8% of tokens are in exactly 1 folio (localized)
    - 17.2% are in 2+ folios
    - Only 0.9% (18 tokens) are in 10+ folios (structural)

    Structural tokens include: daiin, aiin, dar, al, okeey, oteey, ar,
    shey, dal, chol, oteos, dy, okey, otey - these are articulators
    that serve grammatical roles, not content.
    """

    STRUCTURAL_THRESHOLD = 10  # 10+ folios = structural
    DISTRIBUTED_THRESHOLD = 4   # 4-9 folios = distributed

    def __init__(self, registry: 'AZCFolioRegistry'):
        self.registry = registry
        self._cache: Dict[str, TokenType] = {}
        self._count_cache: Dict[str, int] = {}

    def classify(self, token_text: str) -> TokenType:
        """Classify a token by its AZC distribution."""
        if token_text in self._cache:
            return self._cache[token_text]

        count = self.get_folio_count(token_text)

        if count == 0:
            token_type = TokenType.NO_AZC_MAPPING
        elif count >= self.STRUCTURAL_THRESHOLD:
            token_type = TokenType.STRUCTURAL
        elif count >= self.DISTRIBUTED_THRESHOLD:
            token_type = TokenType.DISTRIBUTED
        else:
            token_type = TokenType.LOCALIZED

        self._cache[token_text] = token_type
        return token_type

    def is_clickable(self, token_text: str) -> bool:
        """
        Check if token should be clickable.

        All tokens are clickable, but structural tokens are de-emphasized.
        Users rarely click structural tokens since they're grammar, not content.
        """
        return True  # All tokens clickable

    def get_folio_count(self, token_text: str) -> int:
        """Get the number of AZC folios containing this token (cached)."""
        if token_text not in self._count_cache:
            self._count_cache[token_text] = self.registry.count_folios_for_token(token_text)
        return self._count_cache[token_text]

    def is_structural(self, token_text: str) -> bool:
        """Check if token is structural (10+ folios)."""
        return self.classify(token_text) == TokenType.STRUCTURAL

    def is_localized(self, token_text: str) -> bool:
        """Check if token is localized (1-3 folios)."""
        return self.classify(token_text) == TokenType.LOCALIZED

    def is_distributed(self, token_text: str) -> bool:
        """Check if token is distributed (4-9 folios)."""
        return self.classify(token_text) == TokenType.DISTRIBUTED
