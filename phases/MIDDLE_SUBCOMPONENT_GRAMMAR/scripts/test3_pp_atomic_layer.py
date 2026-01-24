#!/usr/bin/env python3
"""
Test 3: PP as Atomic Layer

Hypothesis: PP MIDDLEs (shared with B) are the primitives of the component vocabulary.

Method: Compute three metrics:
1. PP→Component: % of PP MIDDLEs that ARE sub-components
2. Component→PP: % of sub-components that ARE PP MIDDLEs
3. RI contains PP: % of RI MIDDLEs containing PP MIDDLE as substring

Pass criteria: High overlap (>50%) in at least two metrics
"""

import json
import sys
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path('.')
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'MIDDLE_SUBCOMPONENT_GRAMMAR' / 'results'

# Morphology extraction (from existing codebase patterns)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_middle(token):
    """Extract MIDDLE from token using standard morphology."""
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
    # Character frequencies
    all_chars = ''.join(all_middles)
    char_freq = Counter(all_chars)

    # Coverage counts for 2-grams and 3-grams
    coverage_2 = coverage_count(all_middles, 2)
    coverage_3 = coverage_count(all_middles, 3)

    # Components meeting coverage threshold
    components_2 = {g for g, c in coverage_2.items() if c >= min_coverage}
    components_3 = {g for g, c in coverage_3.items() if c >= min_coverage}
    single_chars = {ch for ch, c in char_freq.items() if c >= 50}

    return components_3 | components_2 | single_chars


def main():
    print("=" * 70)
    print("TEST 3: PP AS ATOMIC LAYER")
    print("=" * 70)
    print()

    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    # Load PP MIDDLEs from class_token_map
    with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
        class_map = json.load(f)

    pp_middles = set()
    for token, middle in class_map['token_to_middle'].items():
        if middle:
            pp_middles.add(middle)

    # Get ALL MIDDLEs from corpus
    df['middle'] = df['word'].apply(extract_middle)
    all_middles = set(df['middle'].dropna().unique())

    # Classify MIDDLEs
    df_a = df[df['language'] == 'A']
    df_b = df[df['language'] == 'B']

    a_middles = set(df_a['middle'].dropna().unique())
    b_middles = set(df_b['middle'].dropna().unique())

    ri_middles = a_middles - pp_middles  # A-exclusive

    print(f"MIDDLE populations:")
    print(f"  All unique MIDDLEs: {len(all_middles)}")
    print(f"  PP MIDDLEs (shared): {len(pp_middles)}")
    print(f"  RI MIDDLEs (A-exclusive): {len(ri_middles)}")
    print()

    # Build component vocabulary (C267.a methodology)
    component_vocab = build_component_vocab(all_middles, min_coverage=20)
    print(f"Component vocabulary: {len(component_vocab)} components")
    print()

    # Stratify by section
    section_map = df_a.groupby(df_a['middle'])['section'].agg(lambda x: x.mode().iloc[0] if len(x) > 0 else None).to_dict()

    # ============================================================
    # METRIC 1: PP→Component (% of PP MIDDLEs that ARE sub-components)
    # ============================================================
    print("=" * 70)
    print("METRIC 1: PP→Component (PP MIDDLEs that ARE sub-components)")
    print("=" * 70)
    print()

    pp_in_vocab = pp_middles & component_vocab
    pp_are_components_pct = 100 * len(pp_in_vocab) / len(pp_middles) if pp_middles else 0

    print(f"PP MIDDLEs that are sub-components: {len(pp_in_vocab)} / {len(pp_middles)}")
    print(f"Percentage: {pp_are_components_pct:.1f}%")
    print()

    # Show examples
    print("Examples of PP MIDDLEs that ARE components:")
    for m in sorted(pp_in_vocab, key=len)[:15]:
        print(f"  '{m}'")
    print()

    print("Examples of PP MIDDLEs that are NOT components:")
    pp_not_in_vocab = pp_middles - component_vocab
    for m in sorted(pp_not_in_vocab, key=len)[:15]:
        print(f"  '{m}'")
    print()

    # ============================================================
    # METRIC 2: Component→PP (% of sub-components that ARE PP MIDDLEs)
    # ============================================================
    print("=" * 70)
    print("METRIC 2: Component→PP (sub-components that ARE PP MIDDLEs)")
    print("=" * 70)
    print()

    components_are_pp = component_vocab & pp_middles
    components_are_pp_pct = 100 * len(components_are_pp) / len(component_vocab) if component_vocab else 0

    print(f"Sub-components that are PP MIDDLEs: {len(components_are_pp)} / {len(component_vocab)}")
    print(f"Percentage: {components_are_pp_pct:.1f}%")
    print()

    # Show examples
    print("Examples of components that ARE PP MIDDLEs:")
    for m in sorted(components_are_pp, key=len)[:15]:
        print(f"  '{m}'")
    print()

    print("Examples of components that are NOT PP MIDDLEs:")
    components_not_pp = component_vocab - pp_middles
    for m in sorted(components_not_pp, key=len)[:15]:
        print(f"  '{m}'")
    print()

    # ============================================================
    # METRIC 3: RI contains PP (% of RI MIDDLEs containing PP MIDDLE as substring)
    # ============================================================
    print("=" * 70)
    print("METRIC 3: RI contains PP (RI MIDDLEs containing PP as substring)")
    print("=" * 70)
    print()

    # Check each RI MIDDLE for PP substrings
    ri_contains_pp_count = 0
    ri_pp_containment = {}  # ri_middle -> list of PP substrings found

    pp_by_length = sorted(pp_middles, key=len, reverse=True)

    for ri_m in ri_middles:
        found_pp = []
        for pp_m in pp_by_length:
            if len(pp_m) > 0 and pp_m in ri_m and pp_m != ri_m:
                found_pp.append(pp_m)
        if found_pp:
            ri_contains_pp_count += 1
            ri_pp_containment[ri_m] = found_pp

    ri_contains_pp_pct = 100 * ri_contains_pp_count / len(ri_middles) if ri_middles else 0

    print(f"RI MIDDLEs containing PP substring: {ri_contains_pp_count} / {len(ri_middles)}")
    print(f"Percentage: {ri_contains_pp_pct:.1f}%")
    print()

    # Show examples
    print("Examples of RI MIDDLEs containing PP substrings:")
    examples = list(ri_pp_containment.items())[:20]
    for ri_m, pp_list in examples:
        print(f"  '{ri_m}' contains: {pp_list[:3]}")
    print()

    # ============================================================
    # STRATIFICATION BY SECTION
    # ============================================================
    print("=" * 70)
    print("STRATIFICATION BY SECTION")
    print("=" * 70)
    print()

    section_results = {}
    for section in ['H', 'P', 'T']:
        section_df = df_a[df_a['section'] == section]
        section_middles = set(section_df['middle'].dropna().unique())
        section_ri = section_middles - pp_middles

        if not section_ri:
            continue

        # Metric 3 by section
        ri_with_pp = sum(1 for m in section_ri if m in ri_pp_containment)
        pct = 100 * ri_with_pp / len(section_ri) if section_ri else 0

        section_results[section] = {
            'ri_middles': len(section_ri),
            'ri_contains_pp': ri_with_pp,
            'ri_contains_pp_pct': round(pct, 1)
        }
        print(f"Section {section}:")
        print(f"  RI MIDDLEs: {len(section_ri)}")
        print(f"  RI with PP substring: {ri_with_pp} ({pct:.1f}%)")
        print()

    # ============================================================
    # SUMMARY AND ASSESSMENT
    # ============================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    results = {
        'metric1_pp_are_components': {
            'count': len(pp_in_vocab),
            'total': len(pp_middles),
            'percentage': round(pp_are_components_pct, 1)
        },
        'metric2_components_are_pp': {
            'count': len(components_are_pp),
            'total': len(component_vocab),
            'percentage': round(components_are_pp_pct, 1)
        },
        'metric3_ri_contains_pp': {
            'count': ri_contains_pp_count,
            'total': len(ri_middles),
            'percentage': round(ri_contains_pp_pct, 1)
        },
        'stratification': section_results,
        'component_vocab_size': len(component_vocab),
        'pp_middles_count': len(pp_middles),
        'ri_middles_count': len(ri_middles)
    }

    # Pass criteria: >50% in at least two metrics
    metrics_above_50 = sum([
        pp_are_components_pct > 50,
        components_are_pp_pct > 50,
        ri_contains_pp_pct > 50
    ])

    results['pass_criteria'] = {
        'threshold': 50,
        'metrics_above_threshold': metrics_above_50,
        'passed': metrics_above_50 >= 2
    }

    print(f"Metric 1 (PP→Component):    {pp_are_components_pct:.1f}%")
    print(f"Metric 2 (Component→PP):    {components_are_pp_pct:.1f}%")
    print(f"Metric 3 (RI contains PP):  {ri_contains_pp_pct:.1f}%")
    print()
    print(f"Metrics above 50%: {metrics_above_50}/3")
    print(f"PASS CRITERIA (≥2 metrics above 50%): {'PASS' if metrics_above_50 >= 2 else 'FAIL'}")
    print()

    # Interpretation
    if metrics_above_50 >= 2:
        print("INTERPRETATION:")
        print("PP MIDDLEs DO form an atomic morphological layer.")
        print("They serve as building blocks for more complex RI MIDDLEs.")
        print()
        print("Potential constraint C512:")
        print("  'PP MIDDLEs form atomic morphological layer; RI MIDDLEs are built")
        print("   from PP primitives via combination and extension.'")
    else:
        print("INTERPRETATION:")
        print("PP MIDDLEs do NOT convincingly form an atomic layer.")
        print("The component vocabulary may be independent of PP/RI distinction.")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'pp_component_overlap.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Save Venn visualization
    with open(RESULTS_DIR / 'pp_component_venn.txt', 'w') as f:
        f.write("PP / Component Overlap Visualization\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"PP MIDDLEs: {len(pp_middles)}\n")
        f.write(f"Sub-components: {len(component_vocab)}\n")
        f.write(f"Intersection: {len(pp_in_vocab)}\n\n")
        f.write("PP-only (not components):\n")
        for m in sorted(pp_not_in_vocab, key=len)[:30]:
            f.write(f"  {m}\n")
        f.write("\nComponent-only (not PP MIDDLEs):\n")
        for m in sorted(components_not_pp, key=len)[:30]:
            f.write(f"  {m}\n")

    print()
    print(f"Results saved to {RESULTS_DIR / 'pp_component_overlap.json'}")
    print(f"Venn saved to {RESULTS_DIR / 'pp_component_venn.txt'}")


if __name__ == '__main__':
    main()
