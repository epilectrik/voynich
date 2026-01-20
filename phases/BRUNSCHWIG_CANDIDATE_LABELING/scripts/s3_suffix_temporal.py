#!/usr/bin/env python3
"""
TEST S-3: Suffix Posture × Temporal Scheduling

Hypothesis: Naked discriminators are introduced earlier in folio sequences;
closure-suffixed discriminators are used more in late-phase coverage completion.

Method:
1. For each registry-internal MIDDLE, find first folio appearance (by physical order)
2. Normalize to position within manuscript (0-1 scale)
3. Group by suffix posture
4. Compare temporal introduction distributions
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# CONFIGURATION
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

# ============================================================
# DATA LOADING
# ============================================================

def load_registry_internal_middles():
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles'])

def parse_folio_order(folio):
    """
    Convert folio string to numeric order.
    Examples: f1r -> 1.0, f1v -> 1.5, f2r -> 2.0, etc.
    Handles special cases like f68r1, f68r2, etc.
    """
    import re

    # Extract base number and suffix
    match = re.match(r'f(\d+)([rv])(\d*)', folio.lower())
    if not match:
        return None

    num = int(match.group(1))
    side = match.group(2)
    sub = match.group(3)

    # Base order: folio number * 2, +1 for verso
    order = num * 2
    if side == 'v':
        order += 1

    # Sub-folios (like f68r1, f68r2)
    if sub:
        order += int(sub) * 0.1

    return order

def load_a_tokens():
    """Load Currier A tokens with folio ordering."""
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

# ============================================================
# ANALYSIS
# ============================================================

def main():
    print("=" * 70)
    print("TEST S-3: Suffix Posture × Temporal Scheduling")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    registry_internal = load_registry_internal_middles()
    tokens = load_a_tokens()

    print(f"  Registry-internal MIDDLEs: {len(registry_internal)}")
    print(f"  Total A tokens: {len(tokens)}")
    print()

    # Filter to registry-internal tokens
    ri_tokens = [t for t in tokens if t['middle'] in registry_internal]
    print(f"  Registry-internal tokens: {len(ri_tokens)}")
    print()

    # For each MIDDLE, find FIRST appearance (by folio order)
    middle_first_appearance = {}
    middle_suffix_counts = defaultdict(Counter)

    for t in ri_tokens:
        middle = t['middle']
        suffix = t['suffix'] if t['suffix'] else '[none]'
        middle_suffix_counts[middle][suffix] += 1

        if middle not in middle_first_appearance:
            middle_first_appearance[middle] = t['folio_order']
        else:
            middle_first_appearance[middle] = min(middle_first_appearance[middle], t['folio_order'])

    # Get manuscript range
    all_orders = [t['folio_order'] for t in tokens]
    min_order = min(all_orders)
    max_order = max(all_orders)
    order_range = max_order - min_order

    print(f"  Manuscript range: {min_order} to {max_order} (span: {order_range})")
    print()

    # Normalize first appearances to 0-1 scale
    middle_normalized = {}
    for middle, first_order in middle_first_appearance.items():
        middle_normalized[middle] = (first_order - min_order) / order_range

    # Get dominant suffix for each MIDDLE
    middle_posture = {}
    for middle, suffix_counts in middle_suffix_counts.items():
        dominant = suffix_counts.most_common(1)[0][0]
        if dominant == '[none]':
            middle_posture[middle] = 'NAKED'
        else:
            middle_posture[middle] = get_suffix_posture(dominant)

    # Group by suffix posture
    posture_intro = defaultdict(list)
    for middle in middle_normalized:
        if middle in middle_posture:
            posture = middle_posture[middle]
            posture_intro[posture].append(middle_normalized[middle])

    print("=" * 70)
    print("RESULTS: First Appearance by Suffix Posture")
    print("=" * 70)
    print()

    print(f"{'Posture':<12} {'n':>6} {'Mean Intro':>12} {'Median':>10} {'Std':>10}")
    print("-" * 55)

    results = {}
    for posture in ['NAKED', 'CLOSURE', 'MINIMAL', 'EXECUTION', 'STRUCTURAL']:
        intros = posture_intro.get(posture, [])
        if intros:
            mean_intro = sum(intros) / len(intros)
            sorted_intros = sorted(intros)
            median_intro = sorted_intros[len(sorted_intros)//2]
            std_intro = (sum((x - mean_intro)**2 for x in intros) / len(intros))**0.5
            print(f"{posture:<12} {len(intros):>6} {mean_intro:>12.4f} {median_intro:>10.4f} {std_intro:>10.4f}")
            results[posture] = {
                'n': len(intros),
                'mean_intro': round(mean_intro, 4),
                'median_intro': round(median_intro, 4),
                'std': round(std_intro, 4),
                'intros': intros
            }
    print()

    # Statistical test: NAKED vs CLOSURE
    naked = posture_intro.get('NAKED', [])
    closure = posture_intro.get('CLOSURE', [])

    if naked and closure:
        print("=" * 70)
        print("STATISTICAL COMPARISON: NAKED vs CLOSURE")
        print("=" * 70)
        print()

        # Mann-Whitney U test
        combined = [(d, 'N') for d in naked] + [(d, 'C') for d in closure]
        combined.sort(key=lambda x: x[0])

        ranks = {}
        i = 0
        while i < len(combined):
            j = i
            while j < len(combined) and combined[j][0] == combined[i][0]:
                j += 1
            avg_rank = (i + j + 1) / 2
            for k in range(i, j):
                if combined[k][1] not in ranks:
                    ranks[combined[k][1]] = []
                ranks[combined[k][1]].append(avg_rank)
            i = j

        R_naked = sum(ranks.get('N', []))
        R_closure = sum(ranks.get('C', []))
        n1, n2 = len(naked), len(closure)

        U_naked = R_naked - n1 * (n1 + 1) / 2
        U_closure = R_closure - n2 * (n2 + 1) / 2
        U = min(U_naked, U_closure)

        mu_U = n1 * n2 / 2
        sigma_U = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
        Z = (U - mu_U) / sigma_U if sigma_U > 0 else 0
        effect_r = abs(Z) / math.sqrt(n1 + n2)

        naked_mean = sum(naked) / len(naked)
        closure_mean = sum(closure) / len(closure)

        print(f"NAKED: n={n1}, mean intro={naked_mean:.4f}")
        print(f"CLOSURE: n={n2}, mean intro={closure_mean:.4f}")
        print()
        print(f"Mann-Whitney U: {U:.1f}")
        print(f"Z-score: {Z:.3f}")
        print(f"Effect size r: {effect_r:.3f}")
        print()

        if effect_r < 0.1:
            effect_interp = "negligible"
        elif effect_r < 0.3:
            effect_interp = "small"
        elif effect_r < 0.5:
            effect_interp = "medium"
        else:
            effect_interp = "large"

        print(f"Effect interpretation: {effect_interp}")
        if naked_mean < closure_mean:
            direction = "NAKED_EARLIER"
            print("Direction: NAKED MIDDLEs introduced EARLIER")
        else:
            direction = "CLOSURE_EARLIER"
            print("Direction: CLOSURE MIDDLEs introduced EARLIER")
        print()
    else:
        direction = "INSUFFICIENT_DATA"
        effect_r = 0
        Z = 0
        naked_mean = None
        closure_mean = None

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if naked and closure:
        if effect_r > 0.2 and direction == "NAKED_EARLIER":
            print("HYPOTHESIS SUPPORTED:")
            print("Naked discriminators are introduced EARLIER in the manuscript.")
            print("This supports: NAKED = foundational discriminators, CLOSURE = later refinement.")
            verdict = "SUPPORTED"
        elif effect_r > 0.2 and direction == "CLOSURE_EARLIER":
            print("HYPOTHESIS CONTRADICTED:")
            print("Closure-suffixed MIDDLEs are introduced EARLIER, opposite of prediction.")
            verdict = "CONTRADICTED"
        else:
            print("HYPOTHESIS NOT CLEARLY SUPPORTED:")
            print(f"Effect size ({effect_r:.3f}) is too small to confirm hypothesis.")
            print("Temporal introduction does not clearly discriminate suffix postures.")
            verdict = "NULL"
    else:
        print("Insufficient data to test hypothesis.")
        verdict = "INSUFFICIENT_DATA"

    print()

    # Additional analysis: quartile distribution
    print("=" * 70)
    print("QUARTILE ANALYSIS: Where do postures appear?")
    print("=" * 70)
    print()

    for posture in ['NAKED', 'CLOSURE', 'MINIMAL']:
        intros = posture_intro.get(posture, [])
        if intros:
            q1 = len([x for x in intros if x < 0.25])
            q2 = len([x for x in intros if 0.25 <= x < 0.5])
            q3 = len([x for x in intros if 0.5 <= x < 0.75])
            q4 = len([x for x in intros if x >= 0.75])
            total = len(intros)
            print(f"{posture}:")
            print(f"  Q1 (0-25%):   {q1:>3} ({100*q1/total:>5.1f}%)")
            print(f"  Q2 (25-50%):  {q2:>3} ({100*q2/total:>5.1f}%)")
            print(f"  Q3 (50-75%):  {q3:>3} ({100*q3/total:>5.1f}%)")
            print(f"  Q4 (75-100%): {q4:>3} ({100*q4/total:>5.1f}%)")
            print()

    # Save results
    output = {
        'test': 'S3_SUFFIX_TEMPORAL',
        'date': '2026-01-20',
        'hypothesis': 'Naked discriminators introduced earlier than closure-suffixed',
        'manuscript_range': {
            'min_order': min_order,
            'max_order': max_order,
            'span': order_range
        },
        'posture_results': {k: {key: val for key, val in v.items() if key != 'intros'}
                          for k, v in results.items()},
        'comparison': {
            'naked_vs_closure': {
                'naked_mean': round(naked_mean, 4) if naked_mean else None,
                'closure_mean': round(closure_mean, 4) if closure_mean else None,
                'z_score': round(Z, 3) if naked and closure else None,
                'effect_r': round(effect_r, 3) if naked and closure else None,
                'direction': direction
            }
        },
        'verdict': verdict
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/s3_suffix_temporal.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/s3_suffix_temporal.json")

if __name__ == '__main__':
    main()
