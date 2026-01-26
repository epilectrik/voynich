#!/usr/bin/env python3
"""
Analyze structural differences between RI and PP MIDDLEs.

Questions:
1. Do RI tokens have different PREFIX attachment rates?
2. Do RI tokens have different SUFFIX patterns?
3. Is the length difference intrinsic to MIDDLE or due to affixation?
4. Are there specific glyph patterns that make MIDDLEs A-exclusive?
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Known PREFIX and SUFFIX inventories from CLAUDE.md
PREFIXES = {
    'q', 'y', 'd', 's', 'o', 'k', 't', 'p', 'f', 'c',  # Common
    'qo', 'ok', 'ot', 'op', 'of', 'ok', 'ol',  # 2-char
    # Add more as needed
}

SUFFIXES = {
    'y', 'd', 'l', 's', 'r', 'm', 'g', 'n',  # Single char
    'dy', 'ly', 'ry', 'my',  # -y endings
    'in', 'iin', 'iiin',  # -in series
    'al', 'ol', 'ar', 'or',  # Liquid endings
}


def load_data():
    """Load middle classes and transcript."""
    mc_path = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json'
    with open(mc_path) as f:
        mc = json.load(f)

    ri_set = set(mc['a_exclusive_middles'])
    pp_set = set(mc['a_shared_middles'])

    # Load transcript
    tx_path = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    df = pd.read_csv(tx_path, sep='\t')
    df = df[df['transcriber'] == 'H']

    return ri_set, pp_set, df


def extract_middle(word, prefixes, suffixes):
    """
    Extract MIDDLE from word by stripping PREFIX and SUFFIX.
    Returns (prefix, middle, suffix) tuple.
    """
    if not word or pd.isna(word):
        return None, None, None

    word = str(word).strip()
    if not word or '*' in word:
        return None, None, None

    prefix = ''
    suffix = ''

    # Try longest prefix first
    for p in sorted(prefixes, key=len, reverse=True):
        if word.startswith(p) and len(word) > len(p):
            prefix = p
            word = word[len(p):]
            break

    # Try longest suffix first
    for s in sorted(suffixes, key=len, reverse=True):
        if word.endswith(s) and len(word) > len(s):
            suffix = s
            word = word[:-len(s)]
            break

    return prefix, word, suffix


def analyze_affix_patterns(df, ri_set, pp_set):
    """Analyze PREFIX/SUFFIX attachment patterns for RI vs PP."""

    # Get Currier A tokens only
    df_a = df[df['language'] == 'A'].copy()

    results = {
        'ri': {'total': 0, 'has_prefix': 0, 'has_suffix': 0, 'prefix_counts': Counter(), 'suffix_counts': Counter()},
        'pp': {'total': 0, 'has_prefix': 0, 'has_suffix': 0, 'prefix_counts': Counter(), 'suffix_counts': Counter()}
    }

    for _, row in df_a.iterrows():
        word = row['word']
        prefix, middle, suffix = extract_middle(word, PREFIXES, SUFFIXES)

        if middle is None:
            continue

        if middle in ri_set:
            cat = 'ri'
        elif middle in pp_set:
            cat = 'pp'
        else:
            continue

        results[cat]['total'] += 1
        if prefix:
            results[cat]['has_prefix'] += 1
            results[cat]['prefix_counts'][prefix] += 1
        if suffix:
            results[cat]['has_suffix'] += 1
            results[cat]['suffix_counts'][suffix] += 1

    return results


def analyze_glyph_composition(ri_set, pp_set):
    """Analyze which glyphs appear in RI vs PP."""

    ri_glyphs = Counter()
    pp_glyphs = Counter()

    for m in ri_set:
        for c in m:
            ri_glyphs[c] += 1

    for m in pp_set:
        for c in m:
            pp_glyphs[c] += 1

    # Normalize by total
    ri_total = sum(ri_glyphs.values())
    pp_total = sum(pp_glyphs.values())

    all_glyphs = set(ri_glyphs.keys()) | set(pp_glyphs.keys())

    glyph_comparison = {}
    for g in all_glyphs:
        ri_pct = 100 * ri_glyphs.get(g, 0) / ri_total if ri_total > 0 else 0
        pp_pct = 100 * pp_glyphs.get(g, 0) / pp_total if pp_total > 0 else 0
        glyph_comparison[g] = {
            'ri_pct': ri_pct,
            'pp_pct': pp_pct,
            'diff': ri_pct - pp_pct
        }

    return glyph_comparison, ri_glyphs, pp_glyphs


def analyze_length_by_structure(df, ri_set, pp_set):
    """Check if length difference is in MIDDLE or due to affixes."""

    df_a = df[df['language'] == 'A'].copy()

    ri_data = {'word_lens': [], 'middle_lens': [], 'prefix_lens': [], 'suffix_lens': []}
    pp_data = {'word_lens': [], 'middle_lens': [], 'prefix_lens': [], 'suffix_lens': []}

    for _, row in df_a.iterrows():
        word = row['word']
        if not word or pd.isna(word) or '*' in str(word):
            continue
        word = str(word).strip()

        prefix, middle, suffix = extract_middle(word, PREFIXES, SUFFIXES)

        if middle is None:
            continue

        if middle in ri_set:
            data = ri_data
        elif middle in pp_set:
            data = pp_data
        else:
            continue

        data['word_lens'].append(len(word))
        data['middle_lens'].append(len(middle))
        data['prefix_lens'].append(len(prefix) if prefix else 0)
        data['suffix_lens'].append(len(suffix) if suffix else 0)

    return ri_data, pp_data


def analyze_initial_final_patterns(ri_set, pp_set):
    """Check which initial/final character patterns are RI-exclusive."""

    ri_initials = Counter(m[0] for m in ri_set if m)
    pp_initials = Counter(m[0] for m in pp_set if m)

    ri_finals = Counter(m[-1] for m in ri_set if m)
    pp_finals = Counter(m[-1] for m in pp_set if m)

    # Find RI-heavy initials
    all_initials = set(ri_initials.keys()) | set(pp_initials.keys())
    initial_analysis = {}
    for c in all_initials:
        ri_count = ri_initials.get(c, 0)
        pp_count = pp_initials.get(c, 0)
        total = ri_count + pp_count
        ri_ratio = ri_count / total if total > 0 else 0
        initial_analysis[c] = {'ri': ri_count, 'pp': pp_count, 'ri_ratio': ri_ratio}

    all_finals = set(ri_finals.keys()) | set(pp_finals.keys())
    final_analysis = {}
    for c in all_finals:
        ri_count = ri_finals.get(c, 0)
        pp_count = pp_finals.get(c, 0)
        total = ri_count + pp_count
        ri_ratio = ri_count / total if total > 0 else 0
        final_analysis[c] = {'ri': ri_count, 'pp': pp_count, 'ri_ratio': ri_ratio}

    return initial_analysis, final_analysis


def main():
    ri_set, pp_set, df = load_data()

    print("=" * 70)
    print("STRUCTURAL ANALYSIS: RI vs PP MIDDLEs")
    print("=" * 70)

    # Basic stats
    print(f"\nDataset: {len(ri_set)} RI, {len(pp_set)} PP")
    print(f"RI mean length: {np.mean([len(m) for m in ri_set]):.2f}")
    print(f"PP mean length: {np.mean([len(m) for m in pp_set]):.2f}")

    # 1. Affix patterns
    print("\n" + "-" * 70)
    print("1. PREFIX/SUFFIX ATTACHMENT PATTERNS (in Currier A tokens)")
    print("-" * 70)

    affix = analyze_affix_patterns(df, ri_set, pp_set)

    for cat in ['ri', 'pp']:
        total = affix[cat]['total']
        if total == 0:
            continue
        prefix_rate = 100 * affix[cat]['has_prefix'] / total
        suffix_rate = 100 * affix[cat]['has_suffix'] / total
        print(f"\n  {cat.upper()} tokens (n={total}):")
        print(f"    PREFIX attachment: {affix[cat]['has_prefix']} ({prefix_rate:.1f}%)")
        print(f"    SUFFIX attachment: {affix[cat]['has_suffix']} ({suffix_rate:.1f}%)")
        print(f"    Top prefixes: {affix[cat]['prefix_counts'].most_common(5)}")
        print(f"    Top suffixes: {affix[cat]['suffix_counts'].most_common(5)}")

    # 2. Length decomposition
    print("\n" + "-" * 70)
    print("2. LENGTH DECOMPOSITION (where does length come from?)")
    print("-" * 70)

    ri_data, pp_data = analyze_length_by_structure(df, ri_set, pp_set)

    print(f"\n  RI tokens (n={len(ri_data['word_lens'])}):")
    print(f"    Mean word length:   {np.mean(ri_data['word_lens']):.2f}")
    print(f"    Mean MIDDLE length: {np.mean(ri_data['middle_lens']):.2f}")
    print(f"    Mean PREFIX length: {np.mean(ri_data['prefix_lens']):.2f}")
    print(f"    Mean SUFFIX length: {np.mean(ri_data['suffix_lens']):.2f}")

    print(f"\n  PP tokens (n={len(pp_data['word_lens'])}):")
    print(f"    Mean word length:   {np.mean(pp_data['word_lens']):.2f}")
    print(f"    Mean MIDDLE length: {np.mean(pp_data['middle_lens']):.2f}")
    print(f"    Mean PREFIX length: {np.mean(pp_data['prefix_lens']):.2f}")
    print(f"    Mean SUFFIX length: {np.mean(pp_data['suffix_lens']):.2f}")

    print(f"\n  MIDDLE length difference: {np.mean(ri_data['middle_lens']) - np.mean(pp_data['middle_lens']):.2f} chars")
    print(f"  Total word length difference: {np.mean(ri_data['word_lens']) - np.mean(pp_data['word_lens']):.2f} chars")

    # 3. Initial/final character patterns
    print("\n" + "-" * 70)
    print("3. INITIAL/FINAL CHARACTER PATTERNS")
    print("-" * 70)

    init_analysis, final_analysis = analyze_initial_final_patterns(ri_set, pp_set)

    # Sort by RI ratio
    ri_heavy_initials = sorted(init_analysis.items(), key=lambda x: x[1]['ri_ratio'], reverse=True)
    pp_heavy_initials = sorted(init_analysis.items(), key=lambda x: x[1]['ri_ratio'])

    print("\n  RI-heavy initial characters (>80% RI):")
    for c, data in ri_heavy_initials[:10]:
        if data['ri_ratio'] > 0.8 and data['ri'] + data['pp'] >= 5:
            print(f"    '{c}': {data['ri']} RI, {data['pp']} PP ({100*data['ri_ratio']:.0f}% RI)")

    print("\n  PP-heavy initial characters (>80% PP):")
    for c, data in pp_heavy_initials[:10]:
        if data['ri_ratio'] < 0.2 and data['ri'] + data['pp'] >= 5:
            print(f"    '{c}': {data['ri']} RI, {data['pp']} PP ({100*(1-data['ri_ratio']):.0f}% PP)")

    ri_heavy_finals = sorted(final_analysis.items(), key=lambda x: x[1]['ri_ratio'], reverse=True)

    print("\n  RI-heavy final characters (>80% RI):")
    for c, data in ri_heavy_finals[:10]:
        if data['ri_ratio'] > 0.8 and data['ri'] + data['pp'] >= 5:
            print(f"    '{c}': {data['ri']} RI, {data['pp']} PP ({100*data['ri_ratio']:.0f}% RI)")

    # 4. Glyph composition
    print("\n" + "-" * 70)
    print("4. GLYPH FREQUENCY DIFFERENCES")
    print("-" * 70)

    glyph_comp, ri_glyphs, pp_glyphs = analyze_glyph_composition(ri_set, pp_set)

    # Sort by difference
    sorted_glyphs = sorted(glyph_comp.items(), key=lambda x: abs(x[1]['diff']), reverse=True)

    print("\n  Glyphs over-represented in RI (vs PP):")
    for g, data in sorted_glyphs[:10]:
        if data['diff'] > 1:
            print(f"    '{g}': RI {data['ri_pct']:.1f}%, PP {data['pp_pct']:.1f}% (diff: +{data['diff']:.1f}%)")

    print("\n  Glyphs over-represented in PP (vs RI):")
    for g, data in sorted_glyphs[:10]:
        if data['diff'] < -1:
            print(f"    '{g}': RI {data['ri_pct']:.1f}%, PP {data['pp_pct']:.1f}% (diff: {data['diff']:.1f}%)")

    # 5. Specific pattern analysis
    print("\n" + "-" * 70)
    print("5. SPECIFIC PATTERN ANALYSIS")
    print("-" * 70)

    # Check for compound patterns in RI
    ri_with_ch = [m for m in ri_set if 'ch' in m]
    pp_with_ch = [m for m in pp_set if 'ch' in m]
    print(f"\n  MIDDLEs containing 'ch': RI {len(ri_with_ch)}, PP {len(pp_with_ch)}")

    ri_with_sh = [m for m in ri_set if 'sh' in m]
    pp_with_sh = [m for m in pp_set if 'sh' in m]
    print(f"  MIDDLEs containing 'sh': RI {len(ri_with_sh)}, PP {len(pp_with_sh)}")

    ri_with_cph = [m for m in ri_set if 'cph' in m]
    pp_with_cph = [m for m in pp_set if 'cph' in m]
    print(f"  MIDDLEs containing 'cph': RI {len(ri_with_cph)}, PP {len(pp_with_cph)}")

    # Check for doubled elements
    ri_doubled = [m for m in ri_set if any(m.count(c*2) > 0 for c in 'aeio')]
    pp_doubled = [m for m in pp_set if any(m.count(c*2) > 0 for c in 'aeio')]
    print(f"  MIDDLEs with doubled vowels: RI {len(ri_doubled)}, PP {len(pp_doubled)}")

    # Save results
    results = {
        'affix_patterns': {
            'ri': {
                'total': affix['ri']['total'],
                'prefix_rate': 100 * affix['ri']['has_prefix'] / affix['ri']['total'] if affix['ri']['total'] > 0 else 0,
                'suffix_rate': 100 * affix['ri']['has_suffix'] / affix['ri']['total'] if affix['ri']['total'] > 0 else 0
            },
            'pp': {
                'total': affix['pp']['total'],
                'prefix_rate': 100 * affix['pp']['has_prefix'] / affix['pp']['total'] if affix['pp']['total'] > 0 else 0,
                'suffix_rate': 100 * affix['pp']['has_suffix'] / affix['pp']['total'] if affix['pp']['total'] > 0 else 0
            }
        },
        'length_decomposition': {
            'ri': {
                'mean_word': float(np.mean(ri_data['word_lens'])) if ri_data['word_lens'] else 0,
                'mean_middle': float(np.mean(ri_data['middle_lens'])) if ri_data['middle_lens'] else 0,
                'mean_prefix': float(np.mean(ri_data['prefix_lens'])) if ri_data['prefix_lens'] else 0,
                'mean_suffix': float(np.mean(ri_data['suffix_lens'])) if ri_data['suffix_lens'] else 0
            },
            'pp': {
                'mean_word': float(np.mean(pp_data['word_lens'])) if pp_data['word_lens'] else 0,
                'mean_middle': float(np.mean(pp_data['middle_lens'])) if pp_data['middle_lens'] else 0,
                'mean_prefix': float(np.mean(pp_data['prefix_lens'])) if pp_data['prefix_lens'] else 0,
                'mean_suffix': float(np.mean(pp_data['suffix_lens'])) if pp_data['suffix_lens'] else 0
            }
        },
        'conclusion': 'See console output for detailed analysis'
    }

    out_path = PROJECT_ROOT / 'phases' / 'PP_RI_RETEST' / 'results' / 'structural_analysis.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {out_path}")


if __name__ == '__main__':
    main()
