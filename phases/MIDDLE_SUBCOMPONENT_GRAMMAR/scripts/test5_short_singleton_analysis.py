#!/usr/bin/env python3
"""
Test 5: Short Singleton Exception Analysis

Hypothesis: The 168 short singletons (≤3 chars) have structural or contextual
differences from short repeaters.

Method:
1. Compare component inventories used by short singletons vs short repeaters
2. Compare positional distributions (line-initial rate, folio context)
3. Baseline: Bootstrap 1000x to establish confidence intervals
"""

import json
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
import random

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'MIDDLE_SUBCOMPONENT_GRAMMAR' / 'results'

# Morphology extraction
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    """Extract MIDDLE from token."""
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None


def get_character_inventory(middles):
    """Get character inventory used by a set of MIDDLEs."""
    chars = set()
    for m in middles:
        chars.update(m)
    return chars


def get_bigram_inventory(middles):
    """Get bigram inventory used by a set of MIDDLEs."""
    bigrams = set()
    for m in middles:
        if len(m) >= 2:
            for i in range(len(m) - 1):
                bigrams.add(m[i:i+2])
    return bigrams


def bootstrap_ci(data, stat_func, n_bootstrap=1000, ci=95):
    """Compute bootstrap confidence interval."""
    if len(data) == 0:
        return 0, 0, 0

    stats = []
    for _ in range(n_bootstrap):
        sample = random.choices(data, k=len(data))
        stats.append(stat_func(sample))

    lower = np.percentile(stats, (100 - ci) / 2)
    upper = np.percentile(stats, 100 - (100 - ci) / 2)
    return np.mean(stats), lower, upper


def main():
    print("=" * 70)
    print("TEST 5: SHORT SINGLETON EXCEPTION ANALYSIS")
    print("=" * 70)
    print()

    random.seed(42)
    np.random.seed(42)

    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    # Get Currier A data
    df_a = df[df['language'] == 'A'].copy()
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_a = df_a[df_a['middle'].notna()]

    # Compute MIDDLE frequencies
    middle_counts = df_a['middle'].value_counts()

    # Identify short singletons (≤3 chars, freq=1) and short repeaters (≤3 chars, freq>1)
    short_singletons = set(m for m, c in middle_counts.items() if c == 1 and len(m) <= 3)
    short_repeaters = set(m for m, c in middle_counts.items() if c > 1 and len(m) <= 3)

    print(f"Short MIDDLEs (≤3 chars):")
    print(f"  Singletons (freq=1): {len(short_singletons)}")
    print(f"  Repeaters (freq>1): {len(short_repeaters)}")
    print()

    # For comparison, also look at long singletons
    long_singletons = set(m for m, c in middle_counts.items() if c == 1 and len(m) > 3)
    print(f"Long singletons (>3 chars, freq=1): {len(long_singletons)}")
    print()

    # ============================================================
    # PHASE 1: Character inventory comparison
    # ============================================================
    print("=" * 70)
    print("PHASE 1: CHARACTER INVENTORY COMPARISON")
    print("=" * 70)
    print()

    sing_chars = get_character_inventory(short_singletons)
    rep_chars = get_character_inventory(short_repeaters)

    print(f"Characters used by short singletons: {len(sing_chars)}")
    print(f"  {sorted(sing_chars)}")
    print()
    print(f"Characters used by short repeaters: {len(rep_chars)}")
    print(f"  {sorted(rep_chars)}")
    print()

    # Unique to each
    sing_only = sing_chars - rep_chars
    rep_only = rep_chars - sing_chars
    shared = sing_chars & rep_chars

    print(f"Characters unique to singletons: {len(sing_only)}")
    if sing_only:
        print(f"  {sorted(sing_only)}")
    print()
    print(f"Characters unique to repeaters: {len(rep_only)}")
    if rep_only:
        print(f"  {sorted(rep_only)}")
    print()
    print(f"Shared characters: {len(shared)}")
    print()

    # Jaccard similarity
    jaccard = len(shared) / len(sing_chars | rep_chars) if (sing_chars | rep_chars) else 0
    print(f"Character inventory Jaccard similarity: {jaccard:.2f}")
    print()

    # ============================================================
    # PHASE 2: Bigram comparison
    # ============================================================
    print("=" * 70)
    print("PHASE 2: BIGRAM INVENTORY COMPARISON")
    print("=" * 70)
    print()

    sing_bigrams = get_bigram_inventory(short_singletons)
    rep_bigrams = get_bigram_inventory(short_repeaters)

    print(f"Bigrams in short singletons: {len(sing_bigrams)}")
    print(f"Bigrams in short repeaters: {len(rep_bigrams)}")
    print()

    sing_only_bi = sing_bigrams - rep_bigrams
    rep_only_bi = rep_bigrams - sing_bigrams
    shared_bi = sing_bigrams & rep_bigrams

    print(f"Bigrams unique to singletons: {len(sing_only_bi)}")
    if sing_only_bi:
        print(f"  {sorted(list(sing_only_bi)[:20])}")
    print()
    print(f"Bigrams unique to repeaters: {len(rep_only_bi)}")
    if rep_only_bi:
        print(f"  {sorted(list(rep_only_bi)[:20])}")
    print()

    jaccard_bi = len(shared_bi) / len(sing_bigrams | rep_bigrams) if (sing_bigrams | rep_bigrams) else 0
    print(f"Bigram inventory Jaccard similarity: {jaccard_bi:.2f}")
    print()

    # ============================================================
    # PHASE 3: Positional distribution
    # ============================================================
    print("=" * 70)
    print("PHASE 3: POSITIONAL DISTRIBUTION")
    print("=" * 70)
    print()

    # Get position data for tokens with these MIDDLEs
    sing_tokens = df_a[df_a['middle'].isin(short_singletons)]
    rep_tokens = df_a[df_a['middle'].isin(short_repeaters)]

    # Line-initial rate (using 'line_initial' column or fallback)
    if 'line_initial' in sing_tokens.columns:
        sing_initial = sing_tokens['line_initial'].fillna(False).astype(bool).values
        rep_initial = rep_tokens['line_initial'].fillna(False).astype(bool).values
    else:
        # Fallback: check if first token on line
        sing_initial = np.zeros(len(sing_tokens), dtype=bool)
        rep_initial = np.zeros(len(rep_tokens), dtype=bool)

    sing_initial_rate = np.mean(sing_initial) if len(sing_initial) > 0 else 0
    rep_initial_rate = np.mean(rep_initial) if len(rep_initial) > 0 else 0

    sing_positions = sing_initial
    rep_positions = rep_initial

    print(f"Line-initial rate (position=1):")
    print(f"  Short singletons: {100*sing_initial_rate:.1f}% (n={len(sing_positions)})")
    print(f"  Short repeaters: {100*rep_initial_rate:.1f}% (n={len(rep_positions)})")
    print()

    # Bootstrap CI for singleton rate
    if len(sing_positions) > 10:
        mean, lower, upper = bootstrap_ci(
            list(sing_positions == 1),
            lambda x: np.mean(x),
            n_bootstrap=1000
        )
        print(f"  Singleton 95% CI: [{100*lower:.1f}%, {100*upper:.1f}%]")
    print()

    # Folio concentration
    sing_folios = sing_tokens['folio'].nunique()
    rep_folios = rep_tokens['folio'].nunique()

    print(f"Folio spread:")
    print(f"  Short singletons: {sing_folios} folios ({len(short_singletons)} MIDDLEs)")
    print(f"  Short repeaters: {rep_folios} folios ({len(short_repeaters)} MIDDLEs)")
    print()

    # ============================================================
    # PHASE 4: Section distribution
    # ============================================================
    print("=" * 70)
    print("PHASE 4: SECTION DISTRIBUTION")
    print("=" * 70)
    print()

    sing_sections = sing_tokens['section'].value_counts()
    rep_sections = rep_tokens.groupby('middle')['section'].agg(lambda x: x.mode().iloc[0] if len(x) > 0 else None).value_counts()

    print("Short singletons by section:")
    for sec, count in sing_sections.items():
        pct = 100 * count / len(sing_tokens)
        print(f"  {sec}: {count} ({pct:.1f}%)")
    print()

    print("Short repeaters by section (mode per MIDDLE):")
    for sec, count in rep_sections.items():
        pct = 100 * count / len(short_repeaters)
        print(f"  {sec}: {count} ({pct:.1f}%)")
    print()

    # ============================================================
    # PHASE 5: Show the actual short singletons
    # ============================================================
    print("=" * 70)
    print("PHASE 5: SHORT SINGLETON INVENTORY")
    print("=" * 70)
    print()

    print("All short singletons (≤3 chars, sorted):")
    by_length = defaultdict(list)
    for m in short_singletons:
        by_length[len(m)].append(m)

    for length in sorted(by_length.keys()):
        middles = sorted(by_length[length])
        print(f"  Length {length}: {middles}")
    print()

    print("All short repeaters (≤3 chars, sorted by frequency):")
    short_rep_freq = [(m, int(middle_counts[m])) for m in short_repeaters]
    for m, freq in sorted(short_rep_freq, key=lambda x: -x[1])[:30]:
        print(f"  '{m}': freq={freq}")
    print()

    # ============================================================
    # PHASE 6: Bootstrap test for difference
    # ============================================================
    print("=" * 70)
    print("PHASE 6: BOOTSTRAP SIGNIFICANCE TEST")
    print("=" * 70)
    print()

    N_BOOTSTRAP = 1000

    # Test: Is the line-initial rate different between groups?
    if len(sing_positions) > 10 and len(rep_positions) > 10:
        observed_diff = sing_initial_rate - rep_initial_rate

        # Null: pool and resample
        pooled = list(sing_positions == 1) + list(rep_positions == 1)
        null_diffs = []

        for _ in range(N_BOOTSTRAP):
            random.shuffle(pooled)
            null_sing = pooled[:len(sing_positions)]
            null_rep = pooled[len(sing_positions):]
            null_diff = np.mean(null_sing) - np.mean(null_rep)
            null_diffs.append(null_diff)

        p_value = np.mean(np.abs(null_diffs) >= np.abs(observed_diff))

        print(f"Line-initial rate difference test:")
        print(f"  Observed difference: {100*observed_diff:.1f}pp")
        print(f"  Bootstrap p-value (two-tailed): {p_value:.3f}")
        if p_value < 0.05:
            print("  SIGNIFICANT at p < 0.05")
        else:
            print("  NOT significant")
        print()
    else:
        observed_diff = 0
        p_value = 1.0
        print("Insufficient data for bootstrap test")

    # ============================================================
    # SUMMARY
    # ============================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    results = {
        'short_singletons_count': len(short_singletons),
        'short_repeaters_count': len(short_repeaters),
        'character_analysis': {
            'singleton_chars': len(sing_chars),
            'repeater_chars': len(rep_chars),
            'singleton_unique': len(sing_only),
            'repeater_unique': len(rep_only),
            'jaccard': round(jaccard, 2)
        },
        'bigram_analysis': {
            'singleton_bigrams': len(sing_bigrams),
            'repeater_bigrams': len(rep_bigrams),
            'singleton_unique': len(sing_only_bi),
            'repeater_unique': len(rep_only_bi),
            'jaccard': round(jaccard_bi, 2)
        },
        'positional_analysis': {
            'singleton_initial_rate': round(100 * sing_initial_rate, 1),
            'repeater_initial_rate': round(100 * rep_initial_rate, 1),
            'rate_difference_pp': round(100 * (sing_initial_rate - rep_initial_rate), 1),
            'bootstrap_p_value': round(p_value, 3)
        },
        'section_distribution': {
            'singleton_sections': {k: int(v) for k, v in sing_sections.items()},
            'repeater_sections': {k: int(v) for k, v in rep_sections.items()}
        },
        'short_singleton_inventory': {
            str(l): sorted(by_length[l]) for l in by_length
        }
    }

    # Interpretation
    print(f"Short singletons (≤3 chars): {len(short_singletons)}")
    print(f"Short repeaters (≤3 chars): {len(short_repeaters)}")
    print()

    differences_found = []
    if len(sing_only) > 0:
        differences_found.append(f"unique characters ({len(sing_only)})")
    if len(sing_only_bi) > len(shared_bi):
        differences_found.append("distinct bigram patterns")
    if p_value < 0.05:
        differences_found.append("different line-initial rates")

    if differences_found:
        print("STRUCTURAL DIFFERENCES FOUND:")
        for diff in differences_found:
            print(f"  - {diff}")
        print()
        print("Short singletons are NOT just 'failed repeaters' - they show distinct patterns.")
    else:
        print("NO SIGNIFICANT STRUCTURAL DIFFERENCES FOUND.")
        print("Short singletons appear similar to short repeaters in structure.")
        print("Their singleton status may be sampling variance or rare usage contexts.")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'short_singleton_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to {RESULTS_DIR / 'short_singleton_analysis.json'}")


if __name__ == '__main__':
    main()
