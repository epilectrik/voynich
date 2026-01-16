"""
Corpus Statistics - Precomputes corpus-wide token frequency statistics.

Based on C265: 1,123 unique tokens, 85 core (freq>=10).

Provides frequency tier classification:
- CORE: freq >= 10 (85 tokens per C265)
- COMMON: top 30% by frequency
- MODERATE: 30-70% quantile
- RARE: bottom 30%
- HAPAX: freq == 1 (unique in corpus)
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, TYPE_CHECKING
from collections import Counter

if TYPE_CHECKING:
    from apps.azc_folio_animator.core.folio_loader import FolioLoader


class FrequencyTier(Enum):
    """Frequency quantile bucket (C265)."""
    CORE = "CORE"           # freq >= 10 (85 tokens per C265)
    COMMON = "COMMON"       # top 30% by frequency
    MODERATE = "MODERATE"   # 30-70% quantile
    RARE = "RARE"           # bottom 30%
    HAPAX = "HAPAX"         # freq == 1


@dataclass
class FrequencyStats:
    """Corpus-wide frequency statistics for a token."""
    raw_frequency: int
    frequency_rank: int         # 1 = most common
    total_unique: int           # Total unique tokens in corpus
    tier: FrequencyTier
    is_hapax: bool

    def get_percentile(self) -> float:
        """Return percentile (0.0 = most common, 1.0 = least common)."""
        if self.total_unique == 0:
            return 0.5
        return self.frequency_rank / self.total_unique

    def get_display(self) -> str:
        """Format for UI display."""
        if self.tier == FrequencyTier.HAPAX:
            return "Hapax (unique)"
        pct = 100 * (1 - self.get_percentile())
        return f"{self.tier.value} (#{self.frequency_rank}, top {pct:.0f}%)"


class CorpusStatsLoader:
    """
    Precomputes corpus-wide token frequency statistics.

    Loads all Currier A folios and counts token occurrences to determine
    frequency ranks and tiers.
    """

    # Thresholds per C265
    CORE_THRESHOLD = 10  # 85 tokens have freq >= 10

    def __init__(self, folio_loader: 'FolioLoader'):
        self.folio_loader = folio_loader
        self.token_frequencies: Dict[str, int] = {}
        self.frequency_ranks: Dict[str, int] = {}
        self.total_unique: int = 0
        self.total_tokens: int = 0
        self._loaded: bool = False

    def load(self):
        """Count all token occurrences across Currier A folios."""
        if self._loaded:
            return

        # Count all token occurrences
        counter = Counter()
        all_folio_ids = self.folio_loader.get_all_folio_ids()

        for folio_id in all_folio_ids:
            folio = self.folio_loader.get_folio(folio_id)
            if folio:
                for token in folio.tokens:
                    counter[token.text] += 1
                    self.total_tokens += 1

        self.token_frequencies = dict(counter)
        self.total_unique = len(self.token_frequencies)

        # Compute ranks (1 = most common)
        sorted_tokens = sorted(
            self.token_frequencies.keys(),
            key=lambda t: (-self.token_frequencies[t], t)
        )
        for rank, token in enumerate(sorted_tokens, 1):
            self.frequency_ranks[token] = rank

        self._loaded = True

    def get_frequency_stats(self, token: str) -> FrequencyStats:
        """Return frequency stats for a token."""
        if not self._loaded:
            self.load()

        freq = self.token_frequencies.get(token, 0)
        rank = self.frequency_ranks.get(token, self.total_unique + 1)

        return FrequencyStats(
            raw_frequency=freq,
            frequency_rank=rank,
            total_unique=self.total_unique,
            tier=self._get_tier(freq, rank),
            is_hapax=(freq == 1)
        )

    def _get_tier(self, freq: int, rank: int) -> FrequencyTier:
        """Determine frequency tier based on count and rank."""
        if freq >= self.CORE_THRESHOLD:
            return FrequencyTier.CORE
        if freq == 1:
            return FrequencyTier.HAPAX
        if freq == 0:
            return FrequencyTier.HAPAX  # Not in corpus = treat as hapax

        # Rank-based classification
        if self.total_unique == 0:
            return FrequencyTier.MODERATE

        percentile = rank / self.total_unique
        if percentile <= 0.30:
            return FrequencyTier.COMMON
        elif percentile <= 0.70:
            return FrequencyTier.MODERATE
        else:
            return FrequencyTier.RARE

    def get_raw_frequency(self, token: str) -> int:
        """Get raw frequency count for a token."""
        if not self._loaded:
            self.load()
        return self.token_frequencies.get(token, 0)

    def get_rank(self, token: str) -> int:
        """Get frequency rank for a token (1 = most common)."""
        if not self._loaded:
            self.load()
        return self.frequency_ranks.get(token, self.total_unique + 1)

    def get_tier(self, token: str) -> FrequencyTier:
        """Get frequency tier for a token."""
        return self.get_frequency_stats(token).tier

    @property
    def stats_summary(self) -> str:
        """Return summary statistics."""
        if not self._loaded:
            self.load()

        core_count = sum(1 for f in self.token_frequencies.values() if f >= self.CORE_THRESHOLD)
        hapax_count = sum(1 for f in self.token_frequencies.values() if f == 1)

        return (
            f"Corpus: {self.total_unique} unique tokens, {self.total_tokens} total\n"
            f"Core (freq>=10): {core_count}\n"
            f"Hapax (freq=1): {hapax_count}"
        )
