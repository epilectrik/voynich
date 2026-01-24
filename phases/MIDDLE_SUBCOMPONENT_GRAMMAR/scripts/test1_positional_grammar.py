#!/usr/bin/env python3
"""
Test 1: Sub-Component Positional Grammar

Hypothesis: Sub-components have positional constraints forming a grammar.

Method:
1. For each of the 218 sub-components, compute positional distribution (start/middle/end of MIDDLE)
2. Calculate position exclusivity score: max(start%, middle%, end%)
3. Classify components into position classes (threshold: 70%)
4. Baseline: Permutation test - shuffle components across MIDDLEs 1000x to establish null distribution

Pass criteria: >70% of components show strong position preference (exclusivity > 0.7)
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


def get_ngrams(s, n):
    """Get all n-grams from string."""
    return [s[i:i+n] for i in range(len(s)-n+1)]


def coverage_count(middles, n):
    """Count how many different MIDDLEs contain each n-gram."""
    gram_to_middles = defaultdict(set)
    for m in middles:
        if len(m) >= n:
            for ng in set(get_ngrams(m, n)):
                gram_to_middles[ng].add(m)
    return {g: len(ms) for g, ms in gram_to_middles.items()}


def build_component_vocab(all_middles, min_coverage=20):
    """Build component vocabulary (replicating C267.a methodology)."""
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
    positions = []  # (segment, start_idx, end_idx)
    i = 0
    while i < len(middle):
        matched = False
        for comp in vocab_sorted:
            if middle[i:].startswith(comp):
                segments.append(comp)
                positions.append((comp, i, i + len(comp)))
                i += len(comp)
                matched = True
                break
        if not matched:
            segments.append(middle[i])
            positions.append((middle[i], i, i + 1))
            i += 1
    return segments, positions


def compute_position_stats(component, middles, vocab_sorted):
    """Compute start/middle/end counts for a component in MIDDLEs."""
    start_count = 0
    middle_count = 0
    end_count = 0

    for m in middles:
        if component not in m:
            continue

        segments, positions = segment_middle(m, vocab_sorted)

        for i, seg in enumerate(segments):
            if seg == component:
                if i == 0:
                    start_count += 1
                elif i == len(segments) - 1:
                    end_count += 1
                else:
                    middle_count += 1

    return start_count, middle_count, end_count


def main():
    print("=" * 70)
    print("TEST 1: SUB-COMPONENT POSITIONAL GRAMMAR")
    print("=" * 70)
    print()

    random.seed(42)
    np.random.seed(42)

    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    # Get ALL MIDDLEs
    df['middle'] = df['word'].apply(extract_middle)
    all_middles = list(df['middle'].dropna().unique())

    print(f"Total unique MIDDLEs: {len(all_middles)}")
    print()

    # Build component vocabulary
    component_vocab = build_component_vocab(set(all_middles), min_coverage=20)
    vocab_sorted = sorted(component_vocab, key=len, reverse=True)

    print(f"Component vocabulary: {len(component_vocab)} components")
    print()

    # Verify C267.a reproduction
    full_coverage = 0
    for m in all_middles:
        segments, _ = segment_middle(m, vocab_sorted)
        if all(s in component_vocab for s in segments):
            full_coverage += 1

    coverage_pct = 100 * full_coverage / len(all_middles)
    print(f"C267.a verification: {coverage_pct:.1f}% fully covered (expected ~97.8%)")
    print()

    # ============================================================
    # PHASE 1: Compute position distribution for each component
    # ============================================================
    print("=" * 70)
    print("PHASE 1: POSITION DISTRIBUTION FOR EACH COMPONENT")
    print("=" * 70)
    print()

    position_distribution = {}
    component_list = list(component_vocab)

    print("Computing position statistics...")
    # Pre-compute segmentations to avoid repeated work
    middle_segmentations = {}
    for m in all_middles:
        segments, positions = segment_middle(m, vocab_sorted)
        middle_segmentations[m] = (segments, positions)

    # Count positions for each component
    for comp in component_list:
        start_count = 0
        middle_count = 0
        end_count = 0

        for m in all_middles:
            segments, _ = middle_segmentations[m]
            for i, seg in enumerate(segments):
                if seg == comp:
                    if i == 0:
                        start_count += 1
                    elif i == len(segments) - 1:
                        end_count += 1
                    else:
                        middle_count += 1

        total = start_count + middle_count + end_count
        if total > 0:
            position_distribution[comp] = {
                'start': start_count,
                'middle': middle_count,
                'end': end_count,
                'total': total,
                'start_pct': round(100 * start_count / total, 1),
                'middle_pct': round(100 * middle_count / total, 1),
                'end_pct': round(100 * end_count / total, 1)
            }

    print(f"Components with position data: {len(position_distribution)}")
    print()

    # ============================================================
    # PHASE 2: Calculate exclusivity scores and classify
    # ============================================================
    print("=" * 70)
    print("PHASE 2: POSITION EXCLUSIVITY CLASSIFICATION")
    print("=" * 70)
    print()

    EXCLUSIVITY_THRESHOLD = 0.7
    MIN_OCCURRENCES = 10

    start_class = []
    middle_class = []
    end_class = []
    free_class = []

    for comp, stats in position_distribution.items():
        if stats['total'] < MIN_OCCURRENCES:
            continue

        exclusivity = max(stats['start_pct'], stats['middle_pct'], stats['end_pct']) / 100

        if stats['start_pct'] >= EXCLUSIVITY_THRESHOLD * 100:
            start_class.append((comp, stats['start_pct'], stats['total']))
        elif stats['end_pct'] >= EXCLUSIVITY_THRESHOLD * 100:
            end_class.append((comp, stats['end_pct'], stats['total']))
        elif stats['middle_pct'] >= EXCLUSIVITY_THRESHOLD * 100:
            middle_class.append((comp, stats['middle_pct'], stats['total']))
        else:
            free_class.append((comp, exclusivity, stats['total']))

    total_classified = len(start_class) + len(middle_class) + len(end_class) + len(free_class)

    print(f"Components with ≥{MIN_OCCURRENCES} occurrences: {total_classified}")
    print()
    print(f"START-class (>{EXCLUSIVITY_THRESHOLD*100:.0f}% at start): {len(start_class)}")
    for comp, pct, n in sorted(start_class, key=lambda x: -x[1])[:10]:
        print(f"  '{comp}': {pct:.0f}% start (n={n})")
    print()

    print(f"MIDDLE-class (>{EXCLUSIVITY_THRESHOLD*100:.0f}% in middle): {len(middle_class)}")
    for comp, pct, n in sorted(middle_class, key=lambda x: -x[1])[:10]:
        print(f"  '{comp}': {pct:.0f}% middle (n={n})")
    print()

    print(f"END-class (>{EXCLUSIVITY_THRESHOLD*100:.0f}% at end): {len(end_class)}")
    for comp, pct, n in sorted(end_class, key=lambda x: -x[1])[:10]:
        print(f"  '{comp}': {pct:.0f}% end (n={n})")
    print()

    print(f"FREE-class (no strong preference): {len(free_class)}")
    for comp, excl, n in sorted(free_class, key=lambda x: -x[1])[:10]:
        print(f"  '{comp}': {excl:.0%} max exclusivity (n={n})")
    print()

    constrained_pct = 100 * (len(start_class) + len(middle_class) + len(end_class)) / total_classified if total_classified > 0 else 0
    print(f"Components with position preference: {len(start_class) + len(middle_class) + len(end_class)} / {total_classified}")
    print(f"Percentage: {constrained_pct:.1f}%")
    print()

    # ============================================================
    # PHASE 3: PERMUTATION TEST (Null model)
    # ============================================================
    print("=" * 70)
    print("PHASE 3: PERMUTATION TEST (NULL MODEL)")
    print("=" * 70)
    print()

    N_PERMUTATIONS = 1000

    # Under null: shuffle segment positions within each MIDDLE
    # Count how many components show >70% preference by chance

    print(f"Running {N_PERMUTATIONS} permutations...")

    null_constrained_counts = []

    for perm in range(N_PERMUTATIONS):
        if perm % 100 == 0:
            print(f"  Permutation {perm}...")

        # Shuffle: for each MIDDLE, randomly shuffle its segment order
        null_position_counts = defaultdict(lambda: {'start': 0, 'middle': 0, 'end': 0})

        for m in all_middles:
            segments, _ = middle_segmentations[m]
            shuffled = segments.copy()
            random.shuffle(shuffled)

            for i, seg in enumerate(shuffled):
                if seg in component_vocab:
                    if i == 0:
                        null_position_counts[seg]['start'] += 1
                    elif i == len(shuffled) - 1:
                        null_position_counts[seg]['end'] += 1
                    else:
                        null_position_counts[seg]['middle'] += 1

        # Count constrained components in this permutation
        constrained = 0
        for comp, counts in null_position_counts.items():
            total = counts['start'] + counts['middle'] + counts['end']
            if total >= MIN_OCCURRENCES:
                max_pct = max(counts['start'], counts['middle'], counts['end']) / total
                if max_pct >= EXCLUSIVITY_THRESHOLD:
                    constrained += 1

        null_constrained_counts.append(constrained)

    null_mean = np.mean(null_constrained_counts)
    null_std = np.std(null_constrained_counts)
    null_95 = np.percentile(null_constrained_counts, 95)

    observed_constrained = len(start_class) + len(middle_class) + len(end_class)
    z_score = (observed_constrained - null_mean) / null_std if null_std > 0 else 0
    p_value = sum(1 for x in null_constrained_counts if x >= observed_constrained) / N_PERMUTATIONS

    print()
    print(f"Null model (random shuffling):")
    print(f"  Mean constrained components: {null_mean:.1f}")
    print(f"  Std: {null_std:.1f}")
    print(f"  95th percentile: {null_95:.1f}")
    print()
    print(f"Observed constrained components: {observed_constrained}")
    print(f"Z-score: {z_score:.2f}")
    print(f"P-value (one-tailed): {p_value:.4f}")
    print()

    # ============================================================
    # PHASE 4: STRATIFICATION BY SECTION
    # ============================================================
    print("=" * 70)
    print("PHASE 4: STRATIFICATION BY SECTION")
    print("=" * 70)
    print()

    df_a = df[df['language'] == 'A']
    section_results = {}

    for section in ['H', 'P', 'T']:
        section_df = df_a[df_a['section'] == section]
        section_middles = list(section_df['middle'].dropna().unique())

        if len(section_middles) < 50:
            continue

        # Compute position stats for this section
        section_segmentations = {m: middle_segmentations[m] for m in section_middles if m in middle_segmentations}

        section_position_counts = defaultdict(lambda: {'start': 0, 'middle': 0, 'end': 0})
        for m in section_middles:
            if m not in middle_segmentations:
                continue
            segments, _ = middle_segmentations[m]
            for i, seg in enumerate(segments):
                if seg in component_vocab:
                    if i == 0:
                        section_position_counts[seg]['start'] += 1
                    elif i == len(segments) - 1:
                        section_position_counts[seg]['end'] += 1
                    else:
                        section_position_counts[seg]['middle'] += 1

        # Count constrained
        section_constrained = 0
        section_total = 0
        for comp, counts in section_position_counts.items():
            total = counts['start'] + counts['middle'] + counts['end']
            if total >= 5:  # Lower threshold for smaller samples
                section_total += 1
                max_pct = max(counts['start'], counts['middle'], counts['end']) / total
                if max_pct >= EXCLUSIVITY_THRESHOLD:
                    section_constrained += 1

        section_pct = 100 * section_constrained / section_total if section_total > 0 else 0
        section_results[section] = {
            'middles': len(section_middles),
            'constrained_components': section_constrained,
            'total_components': section_total,
            'constrained_pct': round(section_pct, 1)
        }

        print(f"Section {section}:")
        print(f"  MIDDLEs: {len(section_middles)}")
        print(f"  Components with ≥5 occurrences: {section_total}")
        print(f"  Constrained (>70%): {section_constrained} ({section_pct:.1f}%)")
        print()

    # ============================================================
    # SUMMARY
    # ============================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    # Pass criterion: >70% of components show strong position preference
    passed = constrained_pct > 70

    results = {
        'component_vocab_size': len(component_vocab),
        'coverage_verification': round(coverage_pct, 1),
        'classification': {
            'total_classified': total_classified,
            'start_class': len(start_class),
            'middle_class': len(middle_class),
            'end_class': len(end_class),
            'free_class': len(free_class),
            'constrained_pct': round(constrained_pct, 1)
        },
        'permutation_test': {
            'n_permutations': N_PERMUTATIONS,
            'null_mean': round(null_mean, 1),
            'null_std': round(null_std, 1),
            'null_95th': round(null_95, 1),
            'observed': observed_constrained,
            'z_score': round(z_score, 2),
            'p_value': round(p_value, 4)
        },
        'stratification': section_results,
        'pass_criteria': {
            'threshold': 70,
            'observed': round(constrained_pct, 1),
            'passed': passed
        }
    }

    print(f"Components with position preference: {constrained_pct:.1f}%")
    print(f"PASS CRITERIA (>70%): {'PASS' if passed else 'FAIL'}")
    print()

    if z_score > 2 and p_value < 0.05:
        print("PERMUTATION TEST: SIGNIFICANT (p < 0.05)")
        print("Positional preferences are NOT explained by random chance.")
    else:
        print("PERMUTATION TEST: NOT SIGNIFICANT")
        print("Positional preferences may be random artifacts.")
    print()

    if passed and z_score > 2:
        print("INTERPRETATION:")
        print("Sub-components DO have positional constraints forming a grammar.")
        print()
        print("Potential constraint C510:")
        print("  'Sub-components have positional constraints: START-class (qc, qe, op),")
        print("   END-class (eg, hh, as), and MIDDLE-class form a positional grammar")
        print("   within MIDDLEs.'")

    # Save detailed results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_DIR / 'position_distribution.json', 'w') as f:
        json.dump(position_distribution, f, indent=2)

    position_classes = {
        'start_class': [(c, p, n) for c, p, n in start_class],
        'middle_class': [(c, p, n) for c, p, n in middle_class],
        'end_class': [(c, p, n) for c, p, n in end_class],
        'free_class': [(c, e, n) for c, e, n in free_class]
    }
    with open(RESULTS_DIR / 'position_classes.json', 'w') as f:
        json.dump(position_classes, f, indent=2)

    with open(RESULTS_DIR / 'test1_summary.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to {RESULTS_DIR}")


if __name__ == '__main__':
    main()
