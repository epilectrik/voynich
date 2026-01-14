#!/usr/bin/env python3
"""
HT Perceptual Load Test v2
==========================

Refined test using FOLIO-LEVEL metrics instead of local context windows.

Research Question:
Does HT PREFIX index perceptual regime (load level)?

Key insight from v1:
- Section-level analysis showed LATE enriched 1.51x in H (highest complexity)
- Section-level analysis showed LATE depleted 0.24x in T (lowest complexity)
- That's a 6x differential - the signal exists at macro level, not micro level
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from scipy import stats
import json
from pathlib import Path

DATA_PATH = "C:/git/voynich/data/transcriptions/interlinear_full_words.txt"

# HT PREFIX definitions from C347/C348
HT_EARLY_PREFIXES = ['op', 'pc', 'do']
HT_LATE_PREFIXES = ['ta']
ALL_HT_PREFIXES = HT_EARLY_PREFIXES + HT_LATE_PREFIXES


def get_ht_prefix_class(word):
    """Classify HT token by PREFIX (EARLY vs LATE)."""
    if pd.isna(word) or not isinstance(word, str):
        return None
    word = word.strip('"').lower()

    for prefix in HT_EARLY_PREFIXES:
        if word.startswith(prefix):
            return 'EARLY'
    for prefix in HT_LATE_PREFIXES:
        if word.startswith(prefix):
            return 'LATE'
    return None


def extract_middle(token):
    """Extract approximate MIDDLE from token."""
    if not isinstance(token, str) or '*' in token:
        return None
    token = token.strip('"').lower()

    # Skip HT tokens
    if token.startswith('y') or any(token.startswith(p) for p in ALL_HT_PREFIXES):
        return None

    # Skip atoms
    if len(token) <= 2:
        return None

    # Extract middle area (positions 2-4)
    if len(token) >= 5:
        return token[2:4]
    elif len(token) >= 4:
        return token[2:3]
    return None


def main():
    print("=" * 80)
    print("HT PERCEPTUAL LOAD TEST v2 (Folio-Level Analysis)")
    print("=" * 80)

    # Load data
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
    df_b = df[df['language'] == 'B'].copy()

    print(f"Loaded {len(df_b)} Currier B tokens")

    # =========================================================================
    # COMPUTE FOLIO-LEVEL METRICS
    # =========================================================================
    print("\n" + "=" * 80)
    print("FOLIO-LEVEL COMPLEXITY METRICS")
    print("=" * 80)

    folio_metrics = defaultdict(lambda: {
        'early_count': 0,
        'late_count': 0,
        'total_tokens': 0,
        'unique_middles': set(),
        'section': None
    })

    for _, row in df_b.iterrows():
        folio = row['folio']
        word = row['word']
        section = row.get('section', 'UNK')

        folio_metrics[folio]['total_tokens'] += 1
        folio_metrics[folio]['section'] = section

        # Count HT by class
        cls = get_ht_prefix_class(word)
        if cls == 'EARLY':
            folio_metrics[folio]['early_count'] += 1
        elif cls == 'LATE':
            folio_metrics[folio]['late_count'] += 1

        # Track MIDDLEs for complexity
        middle = extract_middle(word)
        if middle:
            folio_metrics[folio]['unique_middles'].add(middle)

    # Convert to analyzable format
    folio_data = []
    for folio, metrics in folio_metrics.items():
        if metrics['total_tokens'] < 50:  # Skip tiny folios
            continue

        early = metrics['early_count']
        late = metrics['late_count']
        total_ht = early + late

        if total_ht < 5:  # Skip folios with minimal HT
            continue

        late_ratio = late / total_ht if total_ht > 0 else 0
        complexity = len(metrics['unique_middles'])

        folio_data.append({
            'folio': folio,
            'section': metrics['section'],
            'total_tokens': metrics['total_tokens'],
            'early': early,
            'late': late,
            'total_ht': total_ht,
            'late_ratio': late_ratio,
            'complexity': complexity
        })

    folio_df = pd.DataFrame(folio_data)
    print(f"\nAnalyzing {len(folio_df)} folios with sufficient data")

    # =========================================================================
    # CORRELATION: LATE RATIO vs COMPLEXITY
    # =========================================================================
    print("\n" + "=" * 80)
    print("CORRELATION: LATE RATIO vs FOLIO COMPLEXITY")
    print("=" * 80)

    r, p = stats.pearsonr(folio_df['late_ratio'], folio_df['complexity'])
    rho, p_spearman = stats.spearmanr(folio_df['late_ratio'], folio_df['complexity'])

    print(f"\nPearson r = {r:.3f} (p = {p:.4f})")
    print(f"Spearman rho = {rho:.3f} (p = {p_spearman:.4f})")

    if p < 0.05 and r > 0:
        print("\n  -> POSITIVE correlation: Higher LATE ratio in more complex folios")
        print("  -> SUPPORTS perceptual load hypothesis")
        complexity_correlation = "POSITIVE"
    elif p < 0.05 and r < 0:
        print("\n  -> NEGATIVE correlation: Higher LATE ratio in LESS complex folios")
        print("  -> CONTRADICTS perceptual load hypothesis")
        complexity_correlation = "NEGATIVE"
    else:
        print("\n  -> No significant correlation")
        complexity_correlation = "NONE"

    # =========================================================================
    # SECTION-LEVEL ANALYSIS (More Statistical Rigor)
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION-LEVEL LATE RATIO BY COMPLEXITY RANK")
    print("=" * 80)

    # Get mean complexity by section
    section_complexity = folio_df.groupby('section')['complexity'].mean().sort_values(ascending=False)
    print("\nSection complexity ranking:")
    for section, complexity in section_complexity.items():
        print(f"  {section}: mean = {complexity:.1f} unique MIDDLEs")

    # Get mean LATE ratio by section
    section_late_ratio = folio_df.groupby('section')['late_ratio'].mean()

    print("\n{'Section':<10} {'Complexity':<15} {'LATE Ratio':<15} {'Expected':<15}")
    print("-" * 55)

    section_results = []
    for section in section_complexity.index:
        complexity = section_complexity[section]
        late_ratio = section_late_ratio.get(section, 0)
        n_folios = len(folio_df[folio_df['section'] == section])

        # Expected: higher complexity -> higher LATE ratio
        section_results.append({
            'section': section,
            'complexity': complexity,
            'late_ratio': late_ratio,
            'n_folios': n_folios
        })
        print(f"{section:<10} {complexity:<15.1f} {late_ratio:<15.3f} {'HIGH' if complexity > 60 else 'LOW':<15}")

    # Test if complexity rank correlates with LATE ratio rank
    complexity_rank = list(section_complexity.index)
    late_ratio_rank = list(section_late_ratio.sort_values(ascending=False).index)

    print(f"\nComplexity rank (high to low): {complexity_rank}")
    print(f"LATE ratio rank (high to low): {late_ratio_rank}")

    # Calculate rank correlation
    rank_match = sum(1 for i, s in enumerate(complexity_rank) if s in late_ratio_rank[:len(complexity_rank)//2 + 1] and i < len(complexity_rank)//2 + 1)
    print(f"\nRank agreement: {rank_match}/{len(complexity_rank)//2 + 1} high-complexity sections also have high LATE ratio")

    # =========================================================================
    # EXTREME FOLIOS ANALYSIS
    # =========================================================================
    print("\n" + "=" * 80)
    print("EXTREME FOLIOS: HIGH vs LOW COMPLEXITY")
    print("=" * 80)

    # Split into high and low complexity folios
    median_complexity = folio_df['complexity'].median()
    high_complexity = folio_df[folio_df['complexity'] > median_complexity]
    low_complexity = folio_df[folio_df['complexity'] <= median_complexity]

    high_late_ratio = high_complexity['late_ratio'].mean()
    low_late_ratio = low_complexity['late_ratio'].mean()

    print(f"\nHigh complexity folios (>{median_complexity:.0f} MIDDLEs): n={len(high_complexity)}")
    print(f"  Mean LATE ratio: {high_late_ratio:.3f}")

    print(f"\nLow complexity folios (<={median_complexity:.0f} MIDDLEs): n={len(low_complexity)}")
    print(f"  Mean LATE ratio: {low_late_ratio:.3f}")

    # Statistical test
    stat, p_extreme = stats.mannwhitneyu(
        high_complexity['late_ratio'],
        low_complexity['late_ratio'],
        alternative='greater'  # One-tailed: high complexity should have MORE LATE
    )

    print(f"\nMann-Whitney U (one-tailed: high > low): p = {p_extreme:.4f}")

    if p_extreme < 0.05:
        print("  -> SIGNIFICANT: High-complexity folios have higher LATE ratio")
        extreme_test = "PASSED"
    else:
        print("  -> NOT significant")
        extreme_test = "FAILED"

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY: HT PREFIX AS PERCEPTUAL LOAD INDEXER")
    print("=" * 80)

    evidence_for = []
    evidence_against = []

    if complexity_correlation == "POSITIVE":
        evidence_for.append(f"Positive folio-level correlation (r={r:.3f})")
    elif complexity_correlation == "NEGATIVE":
        evidence_against.append(f"Negative folio-level correlation (r={r:.3f})")

    if extreme_test == "PASSED":
        evidence_for.append("High-complexity folios have higher LATE ratio (p<0.05)")
    else:
        evidence_against.append("No difference between high/low complexity folios")

    if section_complexity.index[0] in late_ratio_rank[:2]:
        evidence_for.append("Highest complexity section has high LATE ratio")
    else:
        evidence_against.append("Highest complexity section does NOT have high LATE ratio")

    print("\nEvidence FOR perceptual load indexing:")
    for e in evidence_for:
        print(f"  + {e}")

    print("\nEvidence AGAINST perceptual load indexing:")
    for e in evidence_against:
        print(f"  - {e}")

    if len(evidence_for) >= 2:
        verdict = "SUPPORTED"
    elif len(evidence_against) >= 2:
        verdict = "NOT SUPPORTED"
    else:
        verdict = "INCONCLUSIVE"

    print(f"\n-> VERDICT: {verdict}")

    # Save results
    results = {
        'test': 'HT Perceptual Load Test v2',
        'folio_level_correlation': {
            'pearson_r': float(r),
            'pearson_p': float(p),
            'spearman_rho': float(rho),
            'spearman_p': float(p_spearman)
        },
        'extreme_folios': {
            'high_complexity_late_ratio': float(high_late_ratio),
            'low_complexity_late_ratio': float(low_late_ratio),
            'p_value': float(p_extreme),
            'passed': extreme_test == "PASSED"
        },
        'section_analysis': section_results,
        'evidence_for': evidence_for,
        'evidence_against': evidence_against,
        'verdict': verdict
    }

    output_path = Path("C:/git/voynich/results/ht_perceptual_load_test_v2.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
