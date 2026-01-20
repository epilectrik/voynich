#!/usr/bin/env python3
"""
TEST S-4: Naked MIDDLEs × Tail Pressure

Confirmatory test from S-3: Are naked registry-internal MIDDLEs more strongly
associated with late, high tail-pressure folios than closure-marked ones?

Tail pressure = coverage completion pressure, operationalized as:
- Folios in Q4 (final 25% of manuscript)
- High "new MIDDLE introduction rate" in that folio

This decorates the S-3 finding, doesn't change the story.
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# CONFIGURATION (same as S-3)
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

EXECUTION_SUFFIXES = ['-ey', '-dy', '-edy', '-aiin', '-ain']
CLOSURE_SUFFIXES = ['-y', '-ol', '-or', '-al', '-ar']
STRUCTURAL_SUFFIXES = ['-am', '-om', '-an', '-in', '-m', '-n']
MINIMAL_SUFFIXES = ['-r', '-l', '-s', '-d']

ALL_SUFFIXES = EXECUTION_SUFFIXES + CLOSURE_SUFFIXES + STRUCTURAL_SUFFIXES + MINIMAL_SUFFIXES

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def get_suffix(token):
    for s in sorted(ALL_SUFFIXES, key=len, reverse=True):
        suffix_str = s.replace('-', '')
        if token.endswith(suffix_str) and len(token) > len(suffix_str):
            return s
    return None

def get_suffix_posture(suffix):
    if suffix is None:
        return 'NAKED'
    elif suffix in CLOSURE_SUFFIXES:
        return 'CLOSURE'
    elif suffix in MINIMAL_SUFFIXES:
        return 'MINIMAL'
    elif suffix in EXECUTION_SUFFIXES:
        return 'EXECUTION'
    elif suffix in STRUCTURAL_SUFFIXES:
        return 'STRUCTURAL'
    else:
        return 'UNKNOWN'

def parse_folio_order(folio):
    import re
    match = re.match(r'f(\d+)([rv])(\d*)', folio.lower())
    if not match:
        return None
    num = int(match.group(1))
    side = match.group(2)
    sub = match.group(3)
    order = num * 2
    if side == 'v':
        order += 1
    if sub:
        order += int(sub) * 0.1
    return order

def load_registry_internal_middles():
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles'])

def load_a_tokens():
    tokens = []
    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue
            folio_order = parse_folio_order(folio)
            if folio_order is None:
                continue
            tokens.append({
                'word': word,
                'folio': folio,
                'folio_order': folio_order,
                'middle': get_middle(word),
                'suffix': get_suffix(word)
            })
    return tokens

def main():
    print("=" * 70)
    print("TEST S-4: Naked MIDDLEs × Tail Pressure")
    print("=" * 70)
    print()

    # Load data
    registry_internal = load_registry_internal_middles()
    tokens = load_a_tokens()
    ri_tokens = [t for t in tokens if t['middle'] in registry_internal]

    # Get manuscript range
    all_orders = [t['folio_order'] for t in tokens]
    min_order, max_order = min(all_orders), max(all_orders)
    order_range = max_order - min_order
    q4_threshold = min_order + 0.75 * order_range

    print(f"Registry-internal tokens: {len(ri_tokens)}")
    print(f"Q4 threshold (75%): folio order > {q4_threshold:.1f}")
    print()

    # For each MIDDLE, find first appearance and classify
    middle_first = {}
    middle_suffix_counts = defaultdict(Counter)

    for t in ri_tokens:
        middle = t['middle']
        suffix = t['suffix'] if t['suffix'] else '[none]'
        middle_suffix_counts[middle][suffix] += 1
        if middle not in middle_first:
            middle_first[middle] = t['folio_order']
        else:
            middle_first[middle] = min(middle_first[middle], t['folio_order'])

    # Classify by dominant suffix
    middle_posture = {}
    for middle, suffix_counts in middle_suffix_counts.items():
        dominant = suffix_counts.most_common(1)[0][0]
        middle_posture[middle] = 'NAKED' if dominant == '[none]' else get_suffix_posture(dominant)

    # Split by Q4 introduction
    q4_middles = {m for m, order in middle_first.items() if order >= q4_threshold}
    early_middles = {m for m, order in middle_first.items() if order < q4_threshold}

    print("=" * 70)
    print("Q4 (FINAL 25%) INTRODUCTION BY POSTURE")
    print("=" * 70)
    print()

    print(f"{'Posture':<12} {'Total':>8} {'Q4 Intro':>10} {'Q4 Rate':>10}")
    print("-" * 45)

    results = {}
    for posture in ['NAKED', 'CLOSURE', 'MINIMAL', 'EXECUTION', 'STRUCTURAL']:
        total = len([m for m, p in middle_posture.items() if p == posture])
        q4_count = len([m for m in q4_middles if middle_posture.get(m) == posture])
        rate = q4_count / total if total > 0 else 0
        print(f"{posture:<12} {total:>8} {q4_count:>10} {rate:>10.1%}")
        results[posture] = {'total': total, 'q4_intro': q4_count, 'q4_rate': round(rate, 3)}

    print()

    # Direct comparison: NAKED vs CLOSURE Q4 rates
    naked_total = results['NAKED']['total']
    naked_q4 = results['NAKED']['q4_intro']
    closure_total = results['CLOSURE']['total']
    closure_q4 = results['CLOSURE']['q4_intro']

    print("=" * 70)
    print("DIRECT COMPARISON: NAKED vs CLOSURE")
    print("=" * 70)
    print()

    naked_rate = naked_q4 / naked_total if naked_total > 0 else 0
    closure_rate = closure_q4 / closure_total if closure_total > 0 else 0
    ratio = naked_rate / closure_rate if closure_rate > 0 else float('inf')

    print(f"NAKED Q4 rate:   {naked_rate:.1%} ({naked_q4}/{naked_total})")
    print(f"CLOSURE Q4 rate: {closure_rate:.1%} ({closure_q4}/{closure_total})")
    print(f"Ratio (NAKED/CLOSURE): {ratio:.2f}×")
    print()

    # Fisher's exact test approximation (chi-square for 2x2)
    # Table: [naked_q4, naked_early] vs [closure_q4, closure_early]
    naked_early = naked_total - naked_q4
    closure_early = closure_total - closure_q4

    n = naked_total + closure_total
    if n > 0:
        # Chi-square for 2x2
        observed = [[naked_q4, naked_early], [closure_q4, closure_early]]
        row_totals = [sum(row) for row in observed]
        col_totals = [naked_q4 + closure_q4, naked_early + closure_early]

        chi2 = 0
        for i in range(2):
            for j in range(2):
                expected = row_totals[i] * col_totals[j] / n
                if expected > 0:
                    chi2 += (observed[i][j] - expected)**2 / expected

        # Phi coefficient (effect size for 2x2)
        phi = math.sqrt(chi2 / n) if n > 0 else 0

        print(f"Chi-square: {chi2:.2f}")
        print(f"Phi coefficient: {phi:.3f}")

        if phi < 0.1:
            effect = "negligible"
        elif phi < 0.3:
            effect = "small"
        elif phi < 0.5:
            effect = "medium"
        else:
            effect = "large"
        print(f"Effect interpretation: {effect}")
    else:
        chi2 = 0
        phi = 0

    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if naked_rate > closure_rate * 1.5 and phi > 0.15:
        print("CONFIRMED: Naked MIDDLEs concentrate in final coverage push.")
        print(f"  - NAKED Q4 rate ({naked_rate:.1%}) >> CLOSURE Q4 rate ({closure_rate:.1%})")
        print(f"  - Ratio: {ratio:.2f}×")
        print()
        print("This decorates S-3: naked = late refinement, not foundation.")
        verdict = "CONFIRMED"
    elif naked_rate > closure_rate:
        print("DIRECTIONALLY SUPPORTED but weak effect.")
        print("Naked MIDDLEs slightly more concentrated in Q4.")
        verdict = "WEAK_SUPPORT"
    else:
        print("NOT SUPPORTED: No tail-pressure concentration for naked MIDDLEs.")
        verdict = "NULL"

    print()

    # Save results
    output = {
        'test': 'S4_TAIL_PRESSURE',
        'date': '2026-01-20',
        'hypothesis': 'Naked MIDDLEs concentrate in final coverage push (Q4)',
        'q4_threshold': round(q4_threshold, 1),
        'posture_results': results,
        'comparison': {
            'naked_q4_rate': round(naked_rate, 3),
            'closure_q4_rate': round(closure_rate, 3),
            'ratio': round(ratio, 2),
            'chi_square': round(chi2, 2),
            'phi': round(phi, 3)
        },
        'verdict': verdict
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/s4_tail_pressure.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/s4_tail_pressure.json")

if __name__ == '__main__':
    main()
