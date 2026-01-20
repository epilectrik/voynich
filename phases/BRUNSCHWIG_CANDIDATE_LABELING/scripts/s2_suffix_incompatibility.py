#!/usr/bin/env python3
"""
TEST S-2: Suffix Posture × Incompatibility Isolation

Hypothesis: Naked suffix-less MIDDLEs are MORE isolated (higher incompatibility),
while closure-suffixed MIDDLEs are MORE connected within local incompatibility
neighborhoods.

Method:
1. Load MIDDLE incompatibility graph
2. For each registry-internal MIDDLE, compute compatibility degree
3. Group by suffix posture (NAKED, CLOSURE, MINIMAL)
4. Compare means/distributions
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

# Suffix classification
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
    """Classify suffix into posture category."""
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

def load_incompatibility_data():
    """Load MIDDLE incompatibility graph data."""
    with open('results/middle_incompatibility.json', 'r') as f:
        data = json.load(f)
    return data

def load_a_tokens():
    """Load Currier A tokens to get MIDDLE → suffix mapping."""
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

def compute_middle_compatibility_degree(incomp_data):
    """
    Compute compatibility degree for each MIDDLE.
    Compatibility degree = number of MIDDLEs it CAN co-exist with.

    We use the components structure: MIDDLEs in the same component are compatible.
    """
    components = incomp_data['graph_analysis']['components']

    # Map each MIDDLE to its component index and component size
    middle_to_component = {}
    middle_to_compat_degree = {}

    for comp_idx, component in enumerate(components):
        comp_size = len(component)
        for middle in component:
            middle_to_component[middle] = comp_idx
            # Compatibility degree = component size - 1 (exclude self)
            middle_to_compat_degree[middle] = comp_size - 1

    return middle_to_compat_degree, middle_to_component

def get_middle_dominant_suffix(tokens, registry_internal):
    """For each registry-internal MIDDLE, find its dominant suffix."""
    middle_suffixes = defaultdict(Counter)

    for t in tokens:
        if t['middle'] in registry_internal:
            suffix = t['suffix'] if t['suffix'] else '[none]'
            middle_suffixes[t['middle']][suffix] += 1

    middle_dominant = {}
    for middle, suffix_counts in middle_suffixes.items():
        dominant = suffix_counts.most_common(1)[0][0]
        if dominant == '[none]':
            middle_dominant[middle] = None
        else:
            middle_dominant[middle] = dominant

    return middle_dominant

def main():
    print("=" * 70)
    print("TEST S-2: Suffix Posture × Incompatibility Isolation")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    registry_internal = load_registry_internal_middles()
    incomp_data = load_incompatibility_data()
    tokens = load_a_tokens()

    print(f"  Registry-internal MIDDLEs: {len(registry_internal)}")
    print()

    # Compute compatibility degrees
    print("Computing compatibility degrees...")
    compat_degree, middle_to_component = compute_middle_compatibility_degree(incomp_data)

    print(f"  Total MIDDLEs with compatibility data: {len(compat_degree)}")
    print()

    # Get dominant suffix for each registry-internal MIDDLE
    print("Classifying MIDDLEs by suffix posture...")
    middle_suffix = get_middle_dominant_suffix(tokens, registry_internal)

    # Find overlap: registry-internal MIDDLEs with compatibility data
    overlap = registry_internal & set(compat_degree.keys())
    print(f"  Registry-internal MIDDLEs with compatibility data: {len(overlap)}")
    print()

    # Group by suffix posture
    posture_degrees = defaultdict(list)
    posture_middles = defaultdict(list)

    for middle in overlap:
        if middle in middle_suffix:
            suffix = middle_suffix[middle]
            posture = get_suffix_posture(suffix)
            degree = compat_degree[middle]
            posture_degrees[posture].append(degree)
            posture_middles[posture].append(middle)

    # Also check MIDDLEs not in middle_suffix (might not appear in A tokens)
    missing = overlap - set(middle_suffix.keys())
    if missing:
        print(f"  Note: {len(missing)} MIDDLEs in incompatibility graph but not in A tokens")

    print()
    print("=" * 70)
    print("RESULTS: Compatibility Degree by Suffix Posture")
    print("=" * 70)
    print()

    print(f"{'Posture':<12} {'n':>6} {'Mean Compat':>12} {'Median':>8} {'Min':>6} {'Max':>6}")
    print("-" * 55)

    results = {}
    for posture in ['NAKED', 'CLOSURE', 'MINIMAL', 'EXECUTION', 'STRUCTURAL']:
        degrees = posture_degrees.get(posture, [])
        if degrees:
            mean_d = sum(degrees) / len(degrees)
            sorted_d = sorted(degrees)
            median_d = sorted_d[len(sorted_d)//2]
            min_d = min(degrees)
            max_d = max(degrees)
            print(f"{posture:<12} {len(degrees):>6} {mean_d:>12.1f} {median_d:>8} {min_d:>6} {max_d:>6}")
            results[posture] = {
                'n': len(degrees),
                'mean': round(mean_d, 2),
                'median': median_d,
                'min': min_d,
                'max': max_d,
                'degrees': degrees
            }
    print()

    # Statistical test: Compare NAKED vs CLOSURE
    naked = posture_degrees.get('NAKED', [])
    closure = posture_degrees.get('CLOSURE', [])

    if naked and closure:
        print("=" * 70)
        print("STATISTICAL COMPARISON: NAKED vs CLOSURE")
        print("=" * 70)
        print()

        # Mann-Whitney U test (rank-based)
        combined = [(d, 'N') for d in naked] + [(d, 'C') for d in closure]
        combined.sort(key=lambda x: x[0])

        # Assign ranks
        ranks = {}
        i = 0
        while i < len(combined):
            j = i
            while j < len(combined) and combined[j][0] == combined[i][0]:
                j += 1
            avg_rank = (i + j + 1) / 2  # 1-indexed
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

        # Effect size: r = Z / sqrt(N)
        # Approximate Z from U
        mu_U = n1 * n2 / 2
        sigma_U = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
        Z = (U - mu_U) / sigma_U if sigma_U > 0 else 0
        effect_r = abs(Z) / math.sqrt(n1 + n2)

        print(f"NAKED: n={n1}, mean={sum(naked)/len(naked):.1f}")
        print(f"CLOSURE: n={n2}, mean={sum(closure)/len(closure):.1f}")
        print()
        print(f"Mann-Whitney U: {U:.1f}")
        print(f"Z-score: {Z:.3f}")
        print(f"Effect size r: {effect_r:.3f}")
        print()

        # Interpret
        if effect_r < 0.1:
            effect_interp = "negligible"
        elif effect_r < 0.3:
            effect_interp = "small"
        elif effect_r < 0.5:
            effect_interp = "medium"
        else:
            effect_interp = "large"

        naked_mean = sum(naked) / len(naked)
        closure_mean = sum(closure) / len(closure)

        print(f"Effect interpretation: {effect_interp}")
        if naked_mean < closure_mean:
            print("Direction: NAKED MIDDLEs are MORE isolated (lower compatibility)")
            direction = "NAKED_MORE_ISOLATED"
        else:
            print("Direction: CLOSURE MIDDLEs are MORE isolated (lower compatibility)")
            direction = "CLOSURE_MORE_ISOLATED"
        print()
    else:
        direction = "INSUFFICIENT_DATA"
        effect_r = 0
        Z = 0

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if naked and closure:
        if effect_r > 0.2 and direction == "NAKED_MORE_ISOLATED":
            print("HYPOTHESIS SUPPORTED:")
            print("Naked suffix-less MIDDLEs are MORE isolated (lower compatibility).")
            print("This supports: NAKED = atomic, standalone discriminator.")
            verdict = "SUPPORTED"
        elif effect_r > 0.2 and direction == "CLOSURE_MORE_ISOLATED":
            print("HYPOTHESIS CONTRADICTED:")
            print("Closure-suffixed MIDDLEs are MORE isolated, opposite of prediction.")
            verdict = "CONTRADICTED"
        else:
            print("HYPOTHESIS NOT CLEARLY SUPPORTED:")
            print("No significant difference in isolation between suffix postures.")
            print("Suffix distinction may be stylistic/phonotactic, not structural.")
            verdict = "NULL"
    else:
        print("Insufficient data to test hypothesis.")
        verdict = "INSUFFICIENT_DATA"

    print()

    # Save results
    output = {
        'test': 'S2_SUFFIX_INCOMPATIBILITY',
        'date': '2026-01-20',
        'hypothesis': 'Naked suffix-less MIDDLEs are MORE isolated',
        'n_registry_internal': len(registry_internal),
        'n_with_compat_data': len(overlap),
        'posture_results': {k: {key: val for key, val in v.items() if key != 'degrees'}
                           for k, v in results.items()},
        'comparison': {
            'naked_vs_closure': {
                'z_score': round(Z, 3) if naked and closure else None,
                'effect_r': round(effect_r, 3) if naked and closure else None,
                'direction': direction
            }
        },
        'verdict': verdict
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/s2_suffix_incompatibility.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/s2_suffix_incompatibility.json")

if __name__ == '__main__':
    main()
