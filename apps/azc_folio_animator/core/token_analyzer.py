"""
Token Analyzer - Full morphological and operational analysis of Currier A tokens.

Provides detailed breakdown for UI display:
- Morphological components (PREFIX/MIDDLE/SUFFIX)
- Operational domain (ENERGY/CONTROL/FREQUENT/REGISTRY)
- Material-behavior class (M-A/B/C/D)
- Token system classification (OPERATIONAL/HT/INFRASTRUCTURE/etc.)
- Frequency tier (CORE/COMMON/MODERATE/RARE/HAPAX)
- AZC mapping status
"""
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from enum import Enum

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.script_explorer.parsing.currier_a import parse_currier_a_token, AStatus
from apps.azc_folio_animator.core.token_system_classifier import (
    TokenSystem, TokenSystemClassifier, SYSTEM_COLORS
)
from apps.azc_folio_animator.core.corpus_stats import (
    FrequencyTier, FrequencyStats, CorpusStatsLoader
)


class OperationalDomain(Enum):
    """Operational domain based on PREFIX (Tier-3 classification)."""
    ENERGY_OPERATOR = "ENERGY"      # ch, sh, qo - 59.4%
    CORE_CONTROL = "CONTROL"        # da, ol - 19.1%
    FREQUENT_OPERATOR = "FREQUENT"  # ok, ot - 15.1%
    REGISTRY_REFERENCE = "REGISTRY" # ct - 6.4%
    UNCLASSIFIED = "UNCLASSIFIED"   # Infrastructure, edge cases


class MaterialClass(Enum):
    """Material-behavior class (CCM Phase)."""
    M_A = "M-A"  # Mobile, Distinct (ch, sh, qo) - Energy operations
    M_B = "M-B"  # Mobile, Homogeneous (ok, ot) - Routine operations
    M_C = "M-C"  # Stable, Distinct (ct) - Registry reference
    M_D = "M-D"  # Stable, Homogeneous (ol, da) - Structural anchor
    UNKNOWN = "?"


# PREFIX -> Domain mapping (from behavioral classification)
PREFIX_TO_DOMAIN = {
    'ch': OperationalDomain.ENERGY_OPERATOR,
    'sh': OperationalDomain.ENERGY_OPERATOR,
    'qo': OperationalDomain.ENERGY_OPERATOR,
    'da': OperationalDomain.CORE_CONTROL,
    'ol': OperationalDomain.CORE_CONTROL,
    'ok': OperationalDomain.FREQUENT_OPERATOR,
    'ot': OperationalDomain.FREQUENT_OPERATOR,
    'ct': OperationalDomain.REGISTRY_REFERENCE,
}

# PREFIX -> Material class mapping (from CCM)
PREFIX_TO_MATERIAL = {
    'ch': MaterialClass.M_A,
    'sh': MaterialClass.M_A,
    'qo': MaterialClass.M_A,
    'ok': MaterialClass.M_B,
    'ot': MaterialClass.M_B,
    'ct': MaterialClass.M_C,
    'ol': MaterialClass.M_D,
    'da': MaterialClass.M_D,
}

# Sister pair relationships
SISTER_PAIRS = {
    'ch': ('ch', 'sh', 'precision'),
    'sh': ('ch', 'sh', 'tolerance'),
    'ok': ('ok', 'ot', 'precision'),
    'ot': ('ok', 'ot', 'tolerance'),
}


@dataclass
class TokenAnalysis:
    """Complete analysis of a Currier A token."""
    text: str

    # Morphological breakdown
    prefix: Optional[str]
    middle: Optional[str]
    suffix: Optional[str]
    parse_status: AStatus

    # Operational classification
    domain: OperationalDomain
    material_class: MaterialClass

    # Sister pair info
    sister_primary: Optional[str] = None
    sister_alternate: Optional[str] = None
    operational_mode: Optional[str] = None  # 'precision' or 'tolerance'

    # AZC info (filled by classifier)
    azc_folio_count: int = 0

    # Token system classification (C240/C347/C350/C407)
    token_system: TokenSystem = TokenSystem.UNCLASSIFIED

    # Frequency info (C265)
    frequency_tier: FrequencyTier = FrequencyTier.RARE
    raw_frequency: int = 0
    frequency_rank: int = 0

    def get_morphology_display(self) -> str:
        """Format morphology for display."""
        parts = []
        if self.prefix:
            parts.append(f"PREFIX: {self.prefix}")
        if self.middle:
            parts.append(f"MIDDLE: {self.middle}")
        if self.suffix:
            parts.append(f"SUFFIX: {self.suffix}")

        if parts:
            return " + ".join(parts)
        elif self.parse_status == AStatus.ILLEGAL_PREFIX:
            # Show what prefix was attempted
            if len(self.text) >= 2:
                attempted = self.text[:2]
                return f"'{attempted}...' not in C240 prefixes (ch/sh/ok/ot/da/qo/ol/ct)"
            return "Token too short for prefix"
        else:
            return "No valid parse"

    def get_domain_display(self) -> str:
        """Format domain info for display."""
        if self.domain == OperationalDomain.UNCLASSIFIED:
            return "Unclassified (infrastructure/edge case)"
        return f"{self.domain.value} ({self.material_class.value})"

    def get_sister_display(self) -> str:
        """Format sister pair info for display."""
        if self.operational_mode:
            return f"Mode: {self.operational_mode} ({self.sister_primary}/{self.sister_alternate} pair)"
        return ""

    def get_status_display(self) -> str:
        """Format parse status for display."""
        status_map = {
            AStatus.VALID_REGISTRY_ENTRY: "Valid registry entry (PREFIX+MIDDLE+SUFFIX)",
            AStatus.VALID_MINIMAL: "Valid minimal form (PREFIX+SUFFIX only)",
            AStatus.UNDERSPECIFIED: "Underspecified (valid prefix, no recognized suffix)",
            AStatus.ILLEGAL_PREFIX: "Outside C240 system (~37% of tokens)",
            AStatus.PREFIX_VALID_MORPH_INCOMPLETE: "Prefix valid, morphology incomplete",
            AStatus.AMBIGUOUS_MORPHOLOGY: "Ambiguous morphology",
        }
        return status_map.get(self.parse_status, str(self.parse_status))

    def get_system_display(self) -> str:
        """Format token system classification for display."""
        system_names = {
            TokenSystem.OPERATIONAL: "Operational (C240)",
            TokenSystem.HUMAN_TRACK: "Human Track (C347)",
            TokenSystem.HT_B_HYBRID: "HT-B Hybrid (C350)",
            TokenSystem.INFRASTRUCTURE: "Infrastructure (C407)",
            TokenSystem.ARTICULATOR: "Articulator (C291)",
            TokenSystem.UNCLASSIFIED: "Unclassified",
        }
        return system_names.get(self.token_system, "Unknown")

    def get_frequency_display(self) -> str:
        """Format frequency info for display."""
        if self.frequency_tier == FrequencyTier.HAPAX:
            return "Hapax (unique in corpus)"
        if self.raw_frequency == 0:
            return "Not in corpus"
        return f"{self.frequency_tier.value} (#{self.frequency_rank}, freq={self.raw_frequency})"

    def get_system_color(self) -> str:
        """Get UI color for token system."""
        return SYSTEM_COLORS.get(self.token_system, "#666666")


class TokenAnalyzer:
    """Analyzes Currier A tokens for UI display."""

    def __init__(self, corpus_stats: Optional[CorpusStatsLoader] = None):
        """
        Initialize analyzer.

        Args:
            corpus_stats: Optional corpus statistics loader for frequency data.
                         If not provided, frequency fields will use defaults.
        """
        self.corpus_stats = corpus_stats
        self.system_classifier = TokenSystemClassifier()

    def analyze(self, token_text: str) -> TokenAnalysis:
        """Perform full analysis of a token."""
        # Parse morphology
        parse_result = parse_currier_a_token(token_text)

        # Get operational domain
        domain = PREFIX_TO_DOMAIN.get(
            parse_result.prefix,
            OperationalDomain.UNCLASSIFIED
        )

        # Get material class
        material_class = PREFIX_TO_MATERIAL.get(
            parse_result.prefix,
            MaterialClass.UNKNOWN
        )

        # Get sister pair info
        sister_info = SISTER_PAIRS.get(parse_result.prefix)
        sister_primary = sister_alternate = op_mode = None
        if sister_info:
            sister_primary, sister_alternate, op_mode = sister_info

        # Get token system classification
        token_system = self.system_classifier.classify(token_text, parse_result)

        # Get frequency stats
        freq_tier = FrequencyTier.RARE
        raw_freq = 0
        freq_rank = 0
        if self.corpus_stats:
            stats = self.corpus_stats.get_frequency_stats(token_text)
            freq_tier = stats.tier
            raw_freq = stats.raw_frequency
            freq_rank = stats.frequency_rank

        return TokenAnalysis(
            text=token_text,
            prefix=parse_result.prefix,
            middle=parse_result.middle,
            suffix=parse_result.suffix,
            parse_status=parse_result.a_status,
            domain=domain,
            material_class=material_class,
            sister_primary=sister_primary,
            sister_alternate=sister_alternate,
            operational_mode=op_mode,
            token_system=token_system,
            frequency_tier=freq_tier,
            raw_frequency=raw_freq,
            frequency_rank=freq_rank,
        )
