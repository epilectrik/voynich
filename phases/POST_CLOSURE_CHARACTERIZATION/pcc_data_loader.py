"""
Post-Closure Characterization Phase: Data Infrastructure

Provides:
- H-only filtered data loading
- MIDDLE extraction utilities
- Incompatibility density calculation
- Order-robust statistics helpers
- AZC compatibility data

CRITICAL: All analyses must be order-robust or explicitly tagged as order-sensitive.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
import warnings
import re
warnings.filterwarnings('ignore')

# Paths
DATA_PATH = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
RESULTS_DIR = Path("C:/git/voynich/results")
PHASE_DIR = Path("C:/git/voynich/phases/POST_CLOSURE_CHARACTERIZATION")

# Morphological components (from CAR phase)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
DA_FAMILY_PREFIXES = ['da', 'd']
CLOSURE_ENDINGS = ['y', 'n', 'm']

# Section boundaries for Currier A
HERBAL_A_MAX = 57  # f1-f57
HERBAL_C_MIN = 87  # f87-f102


class PCCDataLoader:
    """
    Data loader for Post-Closure Characterization phase.

    All methods return order-independent structures unless explicitly noted.
    """

    def __init__(self):
        self.df = None
        self.currier_a = None
        self.currier_b = None
        self._load_data()

    def _load_data(self):
        """Load and filter transcript data."""
        self.df = pd.read_csv(DATA_PATH, sep='\t', encoding='utf-8')

        # MANDATORY: H-only filter
        self.df = self.df[self.df['transcriber'] == 'H']

        # Split by Currier language
        self.currier_a = self.df[self.df['language'] == 'A'].copy()
        self.currier_b = self.df[self.df['language'] == 'B'].copy()

    def get_currier_a(self) -> pd.DataFrame:
        """Return Currier A data (H-only)."""
        return self.currier_a.copy()

    def get_currier_b(self) -> pd.DataFrame:
        """Return Currier B data (H-only)."""
        return self.currier_b.copy()

    def get_entries(self, df: pd.DataFrame = None) -> List[Dict]:
        """
        Extract entry-level data (line = entry for Currier A).

        ORDER-INDEPENDENT: Returns list of entry dicts without positional info.
        """
        if df is None:
            df = self.currier_a

        entries = []
        for (folio, line_num), group in df.groupby(['folio', 'line_number']):
            tokens = group['word'].tolist()
            if not tokens:
                continue

            entry = {
                'folio': folio,
                'line_number': line_num,
                'tokens': tokens,
                'token_count': len(tokens),
                'unique_tokens': len(set(tokens)),
                'first_token': tokens[0],
                'last_token': tokens[-1],
                'middles': self.extract_middles(tokens),
                'section': self.get_section(folio)
            }

            # Closure analysis
            entry['has_da_closure'] = self.is_da_family(tokens[-1])
            entry['has_ending_closure'] = self.has_closure_ending(tokens[-1])
            entry['has_any_closure'] = entry['has_da_closure'] or entry['has_ending_closure']

            # Opener analysis
            entry['has_non_prefix_opener'] = not any(
                tokens[0].startswith(p) for p in PREFIXES
            )

            entries.append(entry)

        return entries

    def extract_middles(self, tokens: List[str]) -> Set[str]:
        """
        Extract MIDDLE components from tokens.

        ORDER-INDEPENDENT: Returns set of unique MIDDLEs.
        """
        middles = set()
        for token in tokens:
            middle = self.get_middle(token)
            if middle:
                middles.add(middle)
        return middles

    def get_middle(self, token: str) -> str:
        """Extract MIDDLE from a single token."""
        middle = token

        # Strip known prefixes (longest match first)
        for prefix in sorted(PREFIXES, key=len, reverse=True):
            if middle.startswith(prefix):
                middle = middle[len(prefix):]
                break

        # Strip known suffixes
        suffixes = ['dy', 'y', 'n', 'm', 'l', 'r', 's', 'ain', 'aiin', 'in']
        for suffix in sorted(suffixes, key=len, reverse=True):
            if middle.endswith(suffix) and len(middle) > len(suffix):
                middle = middle[:-len(suffix)]
                break

        return middle if middle else token

    def is_da_family(self, token: str) -> bool:
        """Check if token belongs to DA-family."""
        return any(token.startswith(p) for p in DA_FAMILY_PREFIXES)

    def has_closure_ending(self, token: str) -> bool:
        """Check if token has closure morphology."""
        return any(token.endswith(e) for e in CLOSURE_ENDINGS)

    def get_section(self, folio: str) -> str:
        """
        Determine section for a folio.

        Returns: 'herbal_a', 'herbal_c', or 'other'
        """
        match = re.search(r'f(\d+)', folio)
        if match:
            num = int(match.group(1))
            if num <= HERBAL_A_MAX:
                return 'herbal_a'
            elif num >= HERBAL_C_MIN:
                return 'herbal_c'
        return 'other'

    def get_all_middles(self, entries: List[Dict] = None) -> Counter:
        """
        Get frequency distribution of all MIDDLEs.

        ORDER-INDEPENDENT: Bag-of-MIDDLEs statistics.
        """
        if entries is None:
            entries = self.get_entries()

        middle_counts = Counter()
        for entry in entries:
            middle_counts.update(entry['middles'])

        return middle_counts

    def calculate_incompatibility_density(self, middles: Set[str],
                                          all_middles: Counter) -> float:
        """
        Calculate incompatibility density for a set of MIDDLEs.

        Higher density = more constrained/incompatible space.
        Uses frequency-inverse weighting: rare MIDDLEs contribute more.

        ORDER-INDEPENDENT.
        """
        if not middles:
            return 0.0

        total_count = sum(all_middles.values())
        if total_count == 0:
            return 0.0

        # Inverse frequency weighting
        density = 0.0
        for middle in middles:
            freq = all_middles.get(middle, 1) / total_count
            # Rare MIDDLEs have higher incompatibility contribution
            density += (1 - freq)

        return density / len(middles)

    def get_novelty_score(self, entry: Dict, seen_middles: Set[str]) -> float:
        """
        Calculate novelty score: proportion of MIDDLEs not seen before.

        NOTE: This is ORDER-SENSITIVE if 'seen_middles' depends on order.
        For order-independent use, pass global rare MIDDLE set.
        """
        if not entry['middles']:
            return 0.0

        novel = entry['middles'] - seen_middles
        return len(novel) / len(entry['middles'])

    def get_rare_middles(self, threshold: int = 3) -> Set[str]:
        """
        Get MIDDLEs that appear <= threshold times globally.

        ORDER-INDEPENDENT.
        """
        all_middles = self.get_all_middles()
        return {m for m, c in all_middles.items() if c <= threshold}

    def jaccard_similarity(self, set1: Set, set2: Set) -> float:
        """Calculate Jaccard similarity between two sets."""
        if not set1 and not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0


def get_order_robust_adjacency_pairs(entries: List[Dict]) -> List[Tuple[Dict, Dict]]:
    """
    Get adjacent entry pairs within same folio.

    ORDER-SENSITIVE (depends on line_number within folio).
    Tag: FOLIO_LOCAL_ORDER
    """
    # Sort entries by folio and line
    sorted_entries = sorted(entries, key=lambda e: (e['folio'], e['line_number']))

    pairs = []
    for i in range(len(sorted_entries) - 1):
        curr = sorted_entries[i]
        next_entry = sorted_entries[i + 1]

        # Only pair within same folio
        if curr['folio'] == next_entry['folio']:
            pairs.append((curr, next_entry))

    return pairs


def permutation_test(observed: float, null_samples: List[float],
                     alternative: str = 'greater') -> float:
    """
    Calculate p-value from permutation test.

    ORDER-INDEPENDENT by design.
    """
    null_samples = np.array(null_samples)

    if alternative == 'greater':
        p_value = np.mean(null_samples >= observed)
    elif alternative == 'less':
        p_value = np.mean(null_samples <= observed)
    else:  # two-sided
        p_value = np.mean(np.abs(null_samples) >= np.abs(observed))

    return max(p_value, 1 / (len(null_samples) + 1))  # Prevent p=0


def bootstrap_ci(data: List[float], statistic_func, n_bootstrap: int = 1000,
                 ci: float = 0.95) -> Tuple[float, float, float]:
    """
    Calculate bootstrap confidence interval.

    ORDER-INDEPENDENT (resampling with replacement).
    """
    data = np.array(data)
    boot_stats = []

    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        boot_stats.append(statistic_func(sample))

    lower = np.percentile(boot_stats, (1 - ci) / 2 * 100)
    upper = np.percentile(boot_stats, (1 + ci) / 2 * 100)
    point = statistic_func(data)

    return point, lower, upper
