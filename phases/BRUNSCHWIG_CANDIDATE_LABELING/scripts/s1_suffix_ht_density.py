#!/usr/bin/env python3
"""
TEST S-1: Suffix Posture × HT Density

Hypothesis: Closure-suffixed registry entries appear in HIGHER HT contexts
than naked ones, because they coincide with conscious cognitive "wrap-up" moments.

Method:
1. Load registry-internal tokens with suffix classification
2. For each folio, get HT density from existing analysis
3. Compare mean HT density across suffix postures
4. Statistical test: Kruskal-Wallis across posture groups
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

def load_ht_density():
    """Load per-folio HT density."""
    with open('results/ht_folio_features.json', 'r') as f:
        data = json.load(f)
    return {folio: info['ht_density'] for folio, info in data['folios'].items()}

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
            tokens.append({
                'word': word,
                'folio': folio,
                'middle': get_middle(word),
                'suffix': get_suffix(word)
            })
    return tokens

# ============================================================
# ANALYSIS
# ============================================================

def main():
    print("=" * 70)
    print("TEST S-1: Suffix Posture × HT Density")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    registry_internal = load_registry_internal_middles()
    ht_density = load_ht_density()
    tokens = load_a_tokens()

    print(f"  Registry-internal MIDDLEs: {len(registry_internal)}")
    print(f"  Folios with HT density: {len(ht_density)}")
    print()

    # Filter to registry-internal tokens
    ri_tokens = [t for t in tokens if t['middle'] in registry_internal]
    print(f"  Registry-internal tokens: {len(ri_tokens)}")
    print()

    # For each suffix posture, collect HT densities of folios where they appear
    posture_ht = defaultdict(list)
    posture_folios = defaultdict(set)

    for t in ri_tokens:
        folio = t['folio']
        if folio in ht_density:
            posture = get_suffix_posture(t['suffix'])
            posture_ht[posture].append(ht_density[folio])
            posture_folios[posture].add(folio)

    print("=" * 70)
    print("RESULTS: HT Density by Suffix Posture (Token-Level)")
    print("=" * 70)
    print()
    print("For each suffix posture, mean HT density of folios where tokens appear:")
    print()

    print(f"{'Posture':<12} {'n_tokens':>10} {'n_folios':>10} {'Mean HT':>10} {'Std':>10}")
    print("-" * 55)

    results = {}
    for posture in ['NAKED', 'CLOSURE', 'MINIMAL', 'EXECUTION', 'STRUCTURAL']:
        ht_values = posture_ht.get(posture, [])
        if ht_values:
            mean_ht = sum(ht_values) / len(ht_values)
            std_ht = (sum((x - mean_ht)**2 for x in ht_values) / len(ht_values))**0.5
            n_folios = len(posture_folios.get(posture, set()))
            print(f"{posture:<12} {len(ht_values):>10} {n_folios:>10} {mean_ht:>10.4f} {std_ht:>10.4f}")
            results[posture] = {
                'n_tokens': len(ht_values),
                'n_folios': n_folios,
                'mean_ht': round(mean_ht, 4),
                'std_ht': round(std_ht, 4),
                'ht_values': ht_values
            }
    print()

    # Type-level analysis: for each MIDDLE, get its dominant suffix and mean HT
    print("=" * 70)
    print("TYPE-LEVEL ANALYSIS: Mean HT by MIDDLE's Dominant Suffix")
    print("=" * 70)
    print()

    middle_suffix = defaultdict(Counter)
    middle_ht = defaultdict(list)

    for t in ri_tokens:
        folio = t['folio']
        if folio in ht_density:
            suffix = t['suffix'] if t['suffix'] else '[none]'
            middle_suffix[t['middle']][suffix] += 1
            middle_ht[t['middle']].append(ht_density[folio])

    # Classify each MIDDLE by dominant suffix
    middle_posture = {}
    for middle, suffix_counts in middle_suffix.items():
        dominant = suffix_counts.most_common(1)[0][0]
        if dominant == '[none]':
            middle_posture[middle] = 'NAKED'
        else:
            middle_posture[middle] = get_suffix_posture(dominant)

    # Compute mean HT for each MIDDLE, then aggregate by posture
    type_posture_ht = defaultdict(list)
    for middle, ht_values in middle_ht.items():
        if middle in middle_posture:
            mean_ht = sum(ht_values) / len(ht_values)
            type_posture_ht[middle_posture[middle]].append(mean_ht)

    print(f"{'Posture':<12} {'n_MIDDLEs':>10} {'Mean of Means':>14} {'Std':>10}")
    print("-" * 50)

    type_results = {}
    for posture in ['NAKED', 'CLOSURE', 'MINIMAL', 'EXECUTION', 'STRUCTURAL']:
        ht_means = type_posture_ht.get(posture, [])
        if ht_means:
            grand_mean = sum(ht_means) / len(ht_means)
            std = (sum((x - grand_mean)**2 for x in ht_means) / len(ht_means))**0.5
            print(f"{posture:<12} {len(ht_means):>10} {grand_mean:>14.4f} {std:>10.4f}")
            type_results[posture] = {
                'n_middles': len(ht_means),
                'mean_ht': round(grand_mean, 4),
                'std': round(std, 4)
            }
    print()

    # Statistical test: NAKED vs CLOSURE
    naked = type_posture_ht.get('NAKED', [])
    closure = type_posture_ht.get('CLOSURE', [])

    if naked and closure:
        print("=" * 70)
        print("STATISTICAL COMPARISON: NAKED vs CLOSURE (Type-Level)")
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

        print(f"NAKED: n={n1}, mean HT={naked_mean:.4f}")
        print(f"CLOSURE: n={n2}, mean HT={closure_mean:.4f}")
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

        if closure_mean > naked_mean:
            direction = "CLOSURE_HIGHER_HT"
            print("Direction: CLOSURE entries appear in HIGHER HT contexts")
        else:
            direction = "NAKED_HIGHER_HT"
            print("Direction: NAKED entries appear in HIGHER HT contexts")
        print()
    else:
        effect_r = 0
        Z = 0
        direction = "INSUFFICIENT_DATA"

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if naked and closure:
        if effect_r > 0.2 and direction == "CLOSURE_HIGHER_HT":
            print("HYPOTHESIS SUPPORTED:")
            print("Closure-suffixed entries appear in HIGHER HT contexts.")
            print("This supports: CLOSURE = cognitive wrap-up, HT-associated.")
            verdict = "SUPPORTED"
        elif effect_r > 0.2 and direction == "NAKED_HIGHER_HT":
            print("HYPOTHESIS CONTRADICTED:")
            print("Naked entries appear in HIGHER HT contexts, opposite of prediction.")
            verdict = "CONTRADICTED"
        else:
            print("HYPOTHESIS NOT CLEARLY SUPPORTED:")
            print(f"Effect size ({effect_r:.3f}) is too small to confirm hypothesis.")
            print("HT density does not clearly discriminate suffix postures.")
            verdict = "NULL"
    else:
        print("Insufficient data to test hypothesis.")
        verdict = "INSUFFICIENT_DATA"

    print()

    # Save results
    output = {
        'test': 'S1_SUFFIX_HT_DENSITY',
        'date': '2026-01-20',
        'hypothesis': 'Closure-suffixed entries appear in HIGHER HT contexts',
        'token_level': {k: {key: val for key, val in v.items() if key != 'ht_values'}
                       for k, v in results.items()},
        'type_level': type_results,
        'comparison': {
            'naked_vs_closure': {
                'naked_mean': round(naked_mean, 4) if naked else None,
                'closure_mean': round(closure_mean, 4) if closure else None,
                'z_score': round(Z, 3) if naked and closure else None,
                'effect_r': round(effect_r, 3) if naked and closure else None,
                'direction': direction
            }
        },
        'verdict': verdict
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/s1_suffix_ht_density.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/s1_suffix_ht_density.json")

if __name__ == '__main__':
    main()
