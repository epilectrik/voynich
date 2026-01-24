#!/usr/bin/env python3
"""
Test 6: Folio Complexity Progression (OPTIONAL)

Hypothesis: MIDDLE complexity changes across Currier A folios.

Method: Plot mean MIDDLE length and segment count by folio order.

Caveat: Confounded by binding history (C156, C367). Results should be
interpreted cautiously.
"""

import json
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

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


def coverage_count(middles, n):
    """Count how many different MIDDLEs contain each n-gram."""
    gram_to_middles = defaultdict(set)
    for m in middles:
        if len(m) >= n:
            for i in range(len(m) - n + 1):
                ng = m[i:i+n]
                gram_to_middles[ng].add(m)
    return {g: len(ms) for g, ms in gram_to_middles.items()}


def build_component_vocab(all_middles, min_coverage=20):
    """Build component vocabulary."""
    all_chars = ''.join(all_middles)
    char_freq = Counter(all_chars)

    coverage_2 = coverage_count(all_middles, 2)
    coverage_3 = coverage_count(all_middles, 3)

    components_2 = {g for g, c in coverage_2.items() if c >= min_coverage}
    components_3 = {g for g, c in coverage_3.items() if c >= min_coverage}
    single_chars = {ch for ch, c in char_freq.items() if c >= 50}

    return components_3 | components_2 | single_chars


def segment_middle(middle, vocab_sorted):
    """Greedy longest-match segmentation."""
    segments = []
    i = 0
    while i < len(middle):
        matched = False
        for comp in vocab_sorted:
            if middle[i:].startswith(comp):
                segments.append(comp)
                i += len(comp)
                matched = True
                break
        if not matched:
            segments.append(middle[i])
            i += 1
    return segments


def folio_sort_key(folio):
    """Sort key for folio names (f1r, f1v, f2r, etc.)."""
    import re
    match = re.match(r'f(\d+)([rv])?(\d*)', folio)
    if match:
        num = int(match.group(1))
        side = 0 if match.group(2) == 'r' else 1
        extra = int(match.group(3)) if match.group(3) else 0
        return (num, side, extra)
    return (9999, 0, 0)


def main():
    print("=" * 70)
    print("TEST 6: FOLIO COMPLEXITY PROGRESSION (OPTIONAL)")
    print("=" * 70)
    print()
    print("CAVEAT: Folio order is confounded by binding history (C156, C367).")
    print("Results should be interpreted cautiously.")
    print()

    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    # Get Currier A data
    df_a = df[df['language'] == 'A'].copy()
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_a = df_a[df_a['middle'].notna()]

    # Get all MIDDLEs for vocabulary
    all_middles = list(df_a['middle'].unique())
    component_vocab = build_component_vocab(set(all_middles), min_coverage=20)
    vocab_sorted = sorted(component_vocab, key=len, reverse=True)

    print(f"Total unique MIDDLEs: {len(all_middles)}")
    print(f"Component vocabulary: {len(component_vocab)}")
    print()

    # ============================================================
    # Compute per-folio metrics
    # ============================================================
    print("=" * 70)
    print("FOLIO-BY-FOLIO ANALYSIS")
    print("=" * 70)
    print()

    folio_metrics = []
    folio_groups = df_a.groupby('folio')

    for folio, group in folio_groups:
        middles = list(group['middle'].dropna())
        if len(middles) < 10:  # Skip folios with too few tokens
            continue

        # Mean length
        mean_length = np.mean([len(m) for m in middles])

        # Mean segment count
        segment_counts = []
        for m in middles:
            segs = segment_middle(m, vocab_sorted)
            segment_counts.append(len(segs))
        mean_segments = np.mean(segment_counts)

        # Unique rate (singleton rate in this folio)
        unique_middles = len(set(middles))
        unique_rate = unique_middles / len(middles)

        folio_metrics.append({
            'folio': folio,
            'section': group['section'].mode().iloc[0] if len(group) > 0 else 'U',
            'n_tokens': len(middles),
            'n_unique_middles': unique_middles,
            'mean_length': round(mean_length, 2),
            'mean_segments': round(mean_segments, 2),
            'unique_rate': round(unique_rate, 3)
        })

    # Sort by folio order
    folio_metrics.sort(key=lambda x: folio_sort_key(x['folio']))

    print(f"Folios analyzed: {len(folio_metrics)}")
    print()

    # ============================================================
    # Display progression
    # ============================================================
    print("Folio progression (sorted by binding order):")
    print("-" * 80)
    print(f"{'Folio':<10} {'Sect':<5} {'N':<6} {'Unique':<6} {'Mean Len':<10} {'Mean Seg':<10} {'Uniq Rate':<10}")
    print("-" * 80)

    for m in folio_metrics:
        print(f"{m['folio']:<10} {m['section']:<5} {m['n_tokens']:<6} {m['n_unique_middles']:<6} "
              f"{m['mean_length']:<10} {m['mean_segments']:<10} {m['unique_rate']:<10}")

    print()

    # ============================================================
    # Trend analysis
    # ============================================================
    print("=" * 70)
    print("TREND ANALYSIS")
    print("=" * 70)
    print()

    # Correlation with folio order
    folio_order = list(range(len(folio_metrics)))
    lengths = [m['mean_length'] for m in folio_metrics]
    segments = [m['mean_segments'] for m in folio_metrics]
    unique_rates = [m['unique_rate'] for m in folio_metrics]

    from scipy import stats

    rho_len, p_len = stats.spearmanr(folio_order, lengths)
    rho_seg, p_seg = stats.spearmanr(folio_order, segments)
    rho_uniq, p_uniq = stats.spearmanr(folio_order, unique_rates)

    print(f"Correlation with folio order:")
    print(f"  Mean length:    rho = {rho_len:.3f}, p = {p_len:.4f}")
    print(f"  Mean segments:  rho = {rho_seg:.3f}, p = {p_seg:.4f}")
    print(f"  Unique rate:    rho = {rho_uniq:.3f}, p = {p_uniq:.4f}")
    print()

    # ============================================================
    # By section
    # ============================================================
    print("=" * 70)
    print("SECTION COMPARISON")
    print("=" * 70)
    print()

    section_stats = defaultdict(list)
    for m in folio_metrics:
        section_stats[m['section']].append(m)

    for section in ['H', 'P', 'T']:
        if section not in section_stats:
            continue
        folios = section_stats[section]
        mean_len = np.mean([f['mean_length'] for f in folios])
        mean_seg = np.mean([f['mean_segments'] for f in folios])
        mean_uniq = np.mean([f['unique_rate'] for f in folios])

        print(f"Section {section}:")
        print(f"  Folios: {len(folios)}")
        print(f"  Mean length: {mean_len:.2f}")
        print(f"  Mean segments: {mean_seg:.2f}")
        print(f"  Mean unique rate: {mean_uniq:.3f}")
        print()

    # ============================================================
    # SUMMARY
    # ============================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    results = {
        'folio_count': len(folio_metrics),
        'folio_metrics': folio_metrics,
        'trend_analysis': {
            'length_vs_order': {'rho': round(rho_len, 3), 'p': round(p_len, 4)},
            'segments_vs_order': {'rho': round(rho_seg, 3), 'p': round(p_seg, 4)},
            'unique_rate_vs_order': {'rho': round(rho_uniq, 3), 'p': round(p_uniq, 4)}
        },
        'section_summary': {
            section: {
                'n_folios': len(folios),
                'mean_length': round(np.mean([f['mean_length'] for f in folios]), 2),
                'mean_segments': round(np.mean([f['mean_segments'] for f in folios]), 2),
                'mean_unique_rate': round(np.mean([f['unique_rate'] for f in folios]), 3)
            }
            for section, folios in section_stats.items()
        }
    }

    significant_trends = []
    if p_len < 0.05:
        direction = "increasing" if rho_len > 0 else "decreasing"
        significant_trends.append(f"MIDDLE length {direction} across folios")
    if p_seg < 0.05:
        direction = "increasing" if rho_seg > 0 else "decreasing"
        significant_trends.append(f"Segment count {direction} across folios")
    if p_uniq < 0.05:
        direction = "increasing" if rho_uniq > 0 else "decreasing"
        significant_trends.append(f"Unique rate {direction} across folios")

    if significant_trends:
        print("SIGNIFICANT TRENDS DETECTED:")
        for trend in significant_trends:
            print(f"  - {trend}")
        print()
        print("WARNING: These trends may be artifacts of binding history, not composition order.")
    else:
        print("NO SIGNIFICANT TRENDS detected in folio order.")
        print("MIDDLE complexity appears stable across folios.")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save as CSV
    pd.DataFrame(folio_metrics).to_csv(RESULTS_DIR / 'folio_complexity_progression.csv', index=False)

    with open(RESULTS_DIR / 'test6_summary.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to {RESULTS_DIR}")


if __name__ == '__main__':
    main()
