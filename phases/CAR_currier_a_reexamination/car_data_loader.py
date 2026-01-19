#!/usr/bin/env python
"""
CAR Phase: Common Data Loader

Provides standardized data loading with MANDATORY H-only filtering.
All CAR phase scripts should use this loader.

CRITICAL: This loader enforces the H-only filter that was previously missing,
causing the transcriber bug that invalidated C250-C266.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Paths
DATA_PATH = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
RESULTS_DIR = Path("C:/git/voynich/results")
PHASE_DIR = Path("C:/git/voynich/phases/CAR_currier_a_reexamination")

# Morphological components
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
SUFFIXES = ['y', 'dy', 'chy', 'shy', 'ain', 'aiin', 'in', 'n', 's', 'l', 'r', 'm',
            'or', 'ar', 'ol', 'al', 'ey', 'edy', 'eey']

# Marker classes (8 mutually exclusive prefix families) - C235
MARKER_PREFIXES = {'ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct'}

# Sister pairs - C408-C412
SISTER_PAIRS = [('ch', 'sh'), ('ok', 'ot')]

# DA articulator (internal punctuation) - C422
DA_TOKENS = {'daiin', 'dain', 'daiiin', 'dam', 'dan'}


class CARDataLoader:
    """
    Standard data loader for CAR phase with H-only filtering.

    CRITICAL: Always filters to transcriber == 'H' (PRIMARY track)
    """

    def __init__(self):
        self.df = None
        self.currier_a = None
        self.currier_b = None
        self.azc = None
        self._loaded = False

    def load(self) -> 'CARDataLoader':
        """Load and filter data. Returns self for chaining."""
        if self._loaded:
            return self

        # Load raw data
        self.df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)

        # MANDATORY: Filter to H transcriber only
        self.df = self.df[self.df['transcriber'] == 'H']

        # Filter valid tokens (no asterisks, not null)
        self.df = self.df[
            (self.df['word'].notna()) &
            (~self.df['word'].str.contains(r'\*', na=False))
        ]

        # Split by Currier classification
        self.currier_a = self.df[self.df['language'] == 'A'].copy()
        self.currier_b = self.df[self.df['language'] == 'B'].copy()

        # AZC = unclassified tokens in sections A, Z, C (language is NA)
        # These are the astronomical/zodiac/cosmological folios
        azc_sections = self.df[self.df['section'].isin(['A', 'Z', 'C'])]
        self.azc = azc_sections[azc_sections['language'].isna()].copy()

        self._loaded = True
        return self

    def get_currier_a(self) -> pd.DataFrame:
        """Get Currier A data."""
        if not self._loaded:
            self.load()
        return self.currier_a

    def get_currier_b(self) -> pd.DataFrame:
        """Get Currier B data."""
        if not self._loaded:
            self.load()
        return self.currier_b

    def get_azc(self) -> pd.DataFrame:
        """Get AZC (Astronomical/Zodiac/Cosmological) data."""
        if not self._loaded:
            self.load()
        return self.azc

    def get_a_entries(self) -> List[Dict]:
        """
        Get Currier A data organized by line (entry).

        Returns list of dicts with:
        - folio: folio identifier
        - line: line number
        - section: section code (H, P, T)
        - tokens: list of tokens in order
        """
        a_data = self.get_currier_a()

        entries = []
        for (folio, line), group in a_data.groupby(['folio', 'line_number']):
            # Sort by index to maintain original order
            group = group.sort_index()
            tokens = group['word'].tolist()
            section = group['section'].iloc[0] if 'section' in group.columns else 'H'

            entries.append({
                'folio': folio,
                'line': line,
                'section': section,
                'tokens': tokens
            })

        # Sort by folio, then line
        entries.sort(key=lambda x: (x['folio'], x['line']))
        return entries

    def verify_counts(self) -> Dict:
        """
        Verify token counts match corrected values.

        Expected (H-only):
        - AZC tokens: ~3,299
        - AZC unique types: ~903
        """
        a_data = self.get_currier_a()
        b_data = self.get_currier_b()
        azc_data = self.get_azc()

        counts = {
            'currier_a_tokens': len(a_data),
            'currier_a_types': a_data['word'].nunique(),
            'currier_b_tokens': len(b_data),
            'currier_b_types': b_data['word'].nunique(),
            'azc_tokens': len(azc_data),
            'azc_types': azc_data['word'].nunique(),
            'total_tokens': len(self.df),
            'total_types': self.df['word'].nunique(),
        }

        # Validation (allow for minor variations in filtering)
        counts['azc_tokens_expected'] = 3299
        counts['azc_tokens_valid'] = abs(counts['azc_tokens'] - 3299) < 200

        return counts


def decompose_token(word: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Decompose token into PREFIX, MIDDLE, SUFFIX.

    Returns (prefix, middle, suffix) or (None, None, None) if no prefix match.
    """
    word = str(word).lower().strip()

    # Extract prefix (longest match first)
    prefix = None
    for p in sorted(PREFIXES, key=len, reverse=True):
        if word.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = word[len(prefix):]

    # Extract suffix (longest match first)
    suffix = ''
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break

    return prefix, remainder, suffix


def get_dominant_marker(tokens: List[str]) -> Optional[str]:
    """
    Get the dominant marker prefix for a list of tokens.

    Returns the most frequent marker prefix, or None if no markers found.
    """
    marker_counts = Counter()

    for token in tokens:
        prefix, _, _ = decompose_token(token)
        if prefix in MARKER_PREFIXES:
            marker_counts[prefix] += 1

    if not marker_counts:
        return None

    return marker_counts.most_common(1)[0][0]


def is_da_token(token: str) -> bool:
    """Check if token is a DA articulator (C422)."""
    return token.lower().strip() in DA_TOKENS or token.lower().startswith('da')


def segment_by_da(tokens: List[str]) -> List[List[str]]:
    """
    Segment a token list by DA articulators.

    Returns list of blocks (sub-records).
    DA tokens are excluded from blocks.
    """
    blocks = []
    current_block = []

    for token in tokens:
        if is_da_token(token):
            if current_block:
                blocks.append(current_block)
                current_block = []
        else:
            current_block.append(token)

    if current_block:
        blocks.append(current_block)

    return blocks


def jaccard_similarity(set1: Set, set2: Set) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def get_middles_from_tokens(tokens: List[str]) -> Set[str]:
    """Extract all MIDDLE components from a list of tokens."""
    middles = set()
    for token in tokens:
        _, middle, _ = decompose_token(token)
        if middle is not None:
            middles.add(middle)
    return middles


def run_permutation_test(observed: float,
                         data_func,
                         n_permutations: int = 1000) -> Tuple[float, float]:
    """
    Run permutation test.

    Args:
        observed: Observed test statistic
        data_func: Function that takes shuffled data and returns test statistic
        n_permutations: Number of permutations

    Returns:
        (p_value, effect_size) where effect_size = (observed - mean) / std
    """
    permuted_values = [data_func() for _ in range(n_permutations)]

    mean_perm = np.mean(permuted_values)
    std_perm = np.std(permuted_values)

    # Two-tailed p-value
    if std_perm > 0:
        effect_size = (observed - mean_perm) / std_perm
        p_value = np.mean([abs(v - mean_perm) >= abs(observed - mean_perm)
                          for v in permuted_values])
    else:
        effect_size = 0.0
        p_value = 1.0

    return p_value, effect_size


if __name__ == "__main__":
    # Verify data loading
    loader = CARDataLoader()
    loader.load()

    counts = loader.verify_counts()

    print("=" * 60)
    print("CAR Phase Data Loader - Verification")
    print("=" * 60)
    print(f"\nCurrier A: {counts['currier_a_tokens']:,} tokens, {counts['currier_a_types']:,} types")
    print(f"Currier B: {counts['currier_b_tokens']:,} tokens, {counts['currier_b_types']:,} types")
    print(f"AZC:       {counts['azc_tokens']:,} tokens, {counts['azc_types']:,} types")
    print(f"Total:     {counts['total_tokens']:,} tokens, {counts['total_types']:,} types")
    print(f"\nAZC tokens valid (expected ~3,299): {counts['azc_tokens_valid']}")

    # Test entry loading
    entries = loader.get_a_entries()
    print(f"\nCurrier A entries: {len(entries)}")

    # Test DA segmentation
    multi_da = 0
    for entry in entries:
        blocks = segment_by_da(entry['tokens'])
        if len(blocks) > 1:
            multi_da += 1

    print(f"Multi-DA entries: {multi_da} ({100*multi_da/len(entries):.1f}%)")

    print("\n" + "=" * 60)
    print("Data loader ready for CAR phase tests")
    print("=" * 60)
