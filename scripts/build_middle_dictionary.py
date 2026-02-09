#!/usr/bin/env python3
"""
Build middle_dictionary.json with all unique MIDDLEs from Currier B.

Populates:
- kernel: K/H/E kernel correlation
- regime: PRECISION/HIGH_ENERGY/SETTLING
- gloss: null (to be filled in as we learn)
- token_count: how many tokens use this MIDDLE
- folio_count: how many folios this MIDDLE appears in
"""

import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# Kernel profiles from BFolioDecoder
MIDDLE_KERNEL_PROFILE = {
    # K-ENRICHED: Energy/heat operations
    'ck': 'K', 'eck': 'K', 'lk': 'K', 'k': 'K', 'ek': 'K', 'eek': 'K',
    'lch': 'K', 'ke': 'K', 'ckh': 'K', 'l': 'K', 'kch': 'K',
    'dy': 'K', 'ol': 'K', 'in': 'K', 'r': 'K', 'al': 'K',
    # H-ENRICHED: Hazard/monitoring
    'opch': 'H', 'sh': 'H', 'ch': 'H', 'pch': 'H', 'd': 'H',
    # E-ENRICHED: Escape/settling
    'eed': 'E', 'eeo': 'E', 'ed': 'E', 'eod': 'E', 'eey': 'E', 'eo': 'E', 'e': 'E',
    # NEUTRAL
    'aiin': None, 'edy': None, 'ar': None, 'tch': None, 'o': None, 't': None,
}

MIDDLE_REGIME = {
    # PRECISION mode
    'm': 'PRECISION', 'ek': 'PRECISION', 'et': 'PRECISION', 'y': 'PRECISION',
    'd': 'PRECISION', 'dy': 'PRECISION', 'od': 'PRECISION', 'am': 'PRECISION',
    'a': 'PRECISION', 's': 'PRECISION', 'i': 'PRECISION',
    # HIGH_ENERGY mode
    'lk': 'HIGH_ENERGY', 'eck': 'HIGH_ENERGY', 'eek': 'HIGH_ENERGY',
    'k': 'HIGH_ENERGY', 'ck': 'HIGH_ENERGY', 'ol': 'HIGH_ENERGY',
    # SETTLING mode
    'eed': 'SETTLING', 'eod': 'SETTLING', 'ed': 'SETTLING', 'eeo': 'SETTLING',
    'ai': 'SETTLING', 'ee': 'SETTLING', 'eo': 'SETTLING', 'eey': 'SETTLING',
    'iin': 'SETTLING',
}

def infer_kernel(middle: str) -> str:
    """Infer kernel type from MIDDLE content or mappings."""
    # Direct lookup
    if middle in MIDDLE_KERNEL_PROFILE:
        return MIDDLE_KERNEL_PROFILE[middle]

    # Check for contained patterns (longest first)
    for pattern in sorted(MIDDLE_KERNEL_PROFILE.keys(), key=len, reverse=True):
        if pattern in middle and len(pattern) >= 2:
            k = MIDDLE_KERNEL_PROFILE[pattern]
            if k:
                return k

    # Infer from kernel character content
    has_k = 'k' in middle
    has_h = 'h' in middle
    has_e = 'e' in middle

    if has_e and not has_k and not has_h:
        return 'E'
    elif has_k and not has_e:
        return 'K'
    elif has_h and not has_k and not has_e:
        return 'H'
    elif has_k and has_e:
        return 'KE'  # Mixed
    elif has_h and has_e:
        return 'HE'  # Mixed

    return None

def infer_regime(middle: str) -> str:
    """Infer regime from MIDDLE."""
    if middle in MIDDLE_REGIME:
        return MIDDLE_REGIME[middle]

    # Check for contained patterns
    for pattern in sorted(MIDDLE_REGIME.keys(), key=len, reverse=True):
        if pattern in middle and len(pattern) >= 2:
            return MIDDLE_REGIME[pattern]

    return None

def main():
    tx = Transcript()
    morph = Morphology()

    # Collect MIDDLE statistics
    middle_counts = Counter()
    middle_folios = defaultdict(set)
    middle_tokens = defaultdict(set)

    for tok in tx.currier_b():
        if not tok.word or '*' in tok.word:
            continue
        m = morph.extract(tok.word)
        if m.middle:
            middle_counts[m.middle] += 1
            middle_folios[m.middle].add(tok.folio)
            middle_tokens[m.middle].add(tok.word)

    # Build dictionary
    middles = {}
    for middle, count in middle_counts.items():
        middles[middle] = {
            'kernel': infer_kernel(middle),
            'regime': infer_regime(middle),
            'gloss': None,
            'token_count': count,
            'folio_count': len(middle_folios[middle]),
            'example_tokens': sorted(list(middle_tokens[middle]))[:5],
            'notes': []
        }

    data = {
        'meta': {
            'version': '1.0',
            'description': 'MIDDLE dictionary for Currier B semantic tracking',
            'total_middles': len(middles),
            'glossed': 0,
            'schema_notes': 'kernel=K/H/E/KE/HE, regime=PRECISION/HIGH_ENERGY/SETTLING'
        },
        'middles': middles
    }

    with open('data/middle_dictionary.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Report
    print("Middle Dictionary Built")
    print("=" * 50)
    print(f"Total unique MIDDLEs: {len(middles)}")

    kernel_counts = Counter(m['kernel'] for m in middles.values())
    print(f"\nKernel distribution:")
    for k, c in kernel_counts.most_common():
        print(f"  {k or 'None':6}: {c:4} MIDDLEs")

    regime_counts = Counter(m['regime'] for m in middles.values())
    print(f"\nRegime distribution:")
    for r, c in regime_counts.most_common():
        print(f"  {r or 'None':12}: {c:4} MIDDLEs")

    # Top 10 by frequency
    print(f"\nTop 10 MIDDLEs by token count:")
    for middle, count in middle_counts.most_common(10):
        k = middles[middle]['kernel'] or '-'
        print(f"  {middle:10}: {count:5} tokens, kernel={k}")

if __name__ == '__main__':
    main()
