#!/usr/bin/env python3
"""
Test 4: Compositional Decomposition

Hypothesis: Longer MIDDLEs can be split into two valid shorter MIDDLEs.

Method:
1. For each 4+ char MIDDLE, test all split points
2. Check if both halves are valid MIDDLEs under THREE definitions:
   - Option A: Any MIDDLE in corpus
   - Option B: Any MIDDLE with frequency > 1
   - Option C: Any PP MIDDLE only
"""

import json
import sys
import pandas as pd
from pathlib import Path
from collections import Counter

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


def can_decompose(middle, valid_set, min_len=1):
    """Check if middle can be split into two valid halves."""
    for i in range(min_len, len(middle) - min_len + 1):
        left = middle[:i]
        right = middle[i:]
        if left in valid_set and right in valid_set:
            return True, left, right
    return False, None, None


def main():
    print("=" * 70)
    print("TEST 4: COMPOSITIONAL DECOMPOSITION")
    print("=" * 70)
    print()

    # Load transcript
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']

    # Load PP MIDDLEs
    with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
        class_map = json.load(f)

    pp_middles = set()
    for token, middle in class_map['token_to_middle'].items():
        if middle:
            pp_middles.add(middle)

    # Get ALL MIDDLEs from corpus
    df['middle'] = df['word'].apply(extract_middle)
    df_a = df[df['language'] == 'A']
    a_middle_counts = df_a['middle'].dropna().value_counts()

    all_middles = set(a_middle_counts.index)
    repeater_middles = set(m for m, c in a_middle_counts.items() if c > 1)

    print(f"MIDDLE populations:")
    print(f"  All unique A MIDDLEs: {len(all_middles)}")
    print(f"  Repeater MIDDLEs (freq > 1): {len(repeater_middles)}")
    print(f"  PP MIDDLEs: {len(pp_middles)}")
    print()

    # Target: MIDDLEs with 4+ characters
    long_middles = [m for m in all_middles if len(m) >= 4]
    print(f"MIDDLEs with 4+ chars (candidates for decomposition): {len(long_middles)}")
    print()

    # ============================================================
    # OPTION A: Split into any valid MIDDLE
    # ============================================================
    print("=" * 70)
    print("OPTION A: Split into any MIDDLE in corpus")
    print("=" * 70)
    print()

    option_a_success = 0
    option_a_examples = []

    for m in long_middles:
        success, left, right = can_decompose(m, all_middles)
        if success:
            option_a_success += 1
            if len(option_a_examples) < 30:
                option_a_examples.append((m, left, right))

    option_a_pct = 100 * option_a_success / len(long_middles) if long_middles else 0
    print(f"Decomposable: {option_a_success} / {len(long_middles)} ({option_a_pct:.1f}%)")
    print()

    print("Examples:")
    for m, left, right in option_a_examples[:15]:
        print(f"  '{m}' = '{left}' + '{right}'")
    print()

    # ============================================================
    # OPTION B: Split into repeater MIDDLEs only
    # ============================================================
    print("=" * 70)
    print("OPTION B: Split into repeater MIDDLEs (freq > 1)")
    print("=" * 70)
    print()

    option_b_success = 0
    option_b_examples = []

    for m in long_middles:
        success, left, right = can_decompose(m, repeater_middles)
        if success:
            option_b_success += 1
            if len(option_b_examples) < 30:
                option_b_examples.append((m, left, right))

    option_b_pct = 100 * option_b_success / len(long_middles) if long_middles else 0
    print(f"Decomposable: {option_b_success} / {len(long_middles)} ({option_b_pct:.1f}%)")
    print()

    print("Examples:")
    for m, left, right in option_b_examples[:15]:
        left_freq = int(a_middle_counts.get(left, 0))
        right_freq = int(a_middle_counts.get(right, 0))
        print(f"  '{m}' = '{left}' (f={left_freq}) + '{right}' (f={right_freq})")
    print()

    # ============================================================
    # OPTION C: Split into PP MIDDLEs only
    # ============================================================
    print("=" * 70)
    print("OPTION C: Split into PP MIDDLEs only")
    print("=" * 70)
    print()

    option_c_success = 0
    option_c_examples = []

    for m in long_middles:
        success, left, right = can_decompose(m, pp_middles)
        if success:
            option_c_success += 1
            if len(option_c_examples) < 30:
                option_c_examples.append((m, left, right))

    option_c_pct = 100 * option_c_success / len(long_middles) if long_middles else 0
    print(f"Decomposable: {option_c_success} / {len(long_middles)} ({option_c_pct:.1f}%)")
    print()

    print("Examples:")
    for m, left, right in option_c_examples[:15]:
        print(f"  '{m}' = '{left}' + '{right}'")
    print()

    # ============================================================
    # STRATIFICATION BY LENGTH
    # ============================================================
    print("=" * 70)
    print("STRATIFICATION BY MIDDLE LENGTH")
    print("=" * 70)
    print()

    length_analysis = {}
    for length in range(4, 10):
        len_middles = [m for m in all_middles if len(m) == length]
        if len(len_middles) < 10:
            continue

        a_count = sum(1 for m in len_middles if can_decompose(m, all_middles)[0])
        b_count = sum(1 for m in len_middles if can_decompose(m, repeater_middles)[0])
        c_count = sum(1 for m in len_middles if can_decompose(m, pp_middles)[0])

        length_analysis[length] = {
            'total': len(len_middles),
            'option_a': a_count,
            'option_b': b_count,
            'option_c': c_count,
            'option_a_pct': round(100 * a_count / len(len_middles), 1),
            'option_b_pct': round(100 * b_count / len(len_middles), 1),
            'option_c_pct': round(100 * c_count / len(len_middles), 1)
        }

        print(f"Length {length}: n={len(len_middles)}")
        print(f"  Option A (any): {a_count} ({100*a_count/len(len_middles):.1f}%)")
        print(f"  Option B (repeater): {b_count} ({100*b_count/len(len_middles):.1f}%)")
        print(f"  Option C (PP): {c_count} ({100*c_count/len(len_middles):.1f}%)")
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
        section_middles = set(m for m in section_df['middle'].dropna().unique() if len(m) >= 4)

        if len(section_middles) < 50:
            continue

        a_count = sum(1 for m in section_middles if can_decompose(m, all_middles)[0])
        b_count = sum(1 for m in section_middles if can_decompose(m, repeater_middles)[0])
        c_count = sum(1 for m in section_middles if can_decompose(m, pp_middles)[0])

        section_results[section] = {
            'total': len(section_middles),
            'option_a': a_count,
            'option_b': b_count,
            'option_c': c_count,
            'option_a_pct': round(100 * a_count / len(section_middles), 1),
            'option_b_pct': round(100 * b_count / len(section_middles), 1),
            'option_c_pct': round(100 * c_count / len(section_middles), 1)
        }

        print(f"Section {section}: n={len(section_middles)}")
        print(f"  Option A: {a_count} ({100*a_count/len(section_middles):.1f}%)")
        print(f"  Option B: {b_count} ({100*b_count/len(section_middles):.1f}%)")
        print(f"  Option C: {c_count} ({100*c_count/len(section_middles):.1f}%)")
        print()

    # ============================================================
    # SUMMARY
    # ============================================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    results = {
        'long_middles_count': len(long_middles),
        'option_a': {
            'description': 'Split into any MIDDLE in corpus',
            'success': option_a_success,
            'percentage': round(option_a_pct, 1),
            'examples': [(m, l, r) for m, l, r in option_a_examples[:10]]
        },
        'option_b': {
            'description': 'Split into repeater MIDDLEs',
            'success': option_b_success,
            'percentage': round(option_b_pct, 1),
            'examples': [(m, l, r) for m, l, r in option_b_examples[:10]]
        },
        'option_c': {
            'description': 'Split into PP MIDDLEs only',
            'success': option_c_success,
            'percentage': round(option_c_pct, 1),
            'examples': [(m, l, r) for m, l, r in option_c_examples[:10]]
        },
        'by_length': length_analysis,
        'by_section': section_results
    }

    print(f"Option A (any MIDDLE):     {option_a_pct:.1f}% decomposable")
    print(f"Option B (repeater only):  {option_b_pct:.1f}% decomposable")
    print(f"Option C (PP only):        {option_c_pct:.1f}% decomposable")
    print()

    print("INTERPRETATION:")
    if option_a_pct > 50:
        print("Majority of long MIDDLEs CAN be decomposed into valid shorter MIDDLEs.")
        print("This supports the compositional model.")
    else:
        print("Most long MIDDLEs cannot be cleanly decomposed.")
        print("The compositional model may operate at sub-MIDDLE level (n-grams) rather than MIDDLE level.")

    if option_c_pct > 20:
        print()
        print("Notable: PP MIDDLEs ARE used as building blocks in some long MIDDLEs.")
        print("This supports C512 (PP as atomic layer) even if not the majority.")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'decomposition_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to {RESULTS_DIR / 'decomposition_results.json'}")


if __name__ == '__main__':
    main()
