"""
F-A-009: Comparability Window Fit

Tests whether entries with shared partial universality (2-5 prefixes)
cluster near each other in manuscript space more than expected by chance.

Core question: Is relational comparison scaffolded by layout/topology?

This tests the relational hypothesis at its weakest boundary:
comparison BETWEEN entries, not WITHIN entries.

Pre-declared outcomes:
- Positive signal -> F2: "Relational comparison weakly scaffolded by layout"
- Null -> F1: "Relationality is purely cognitive, not scaffolded"
- Opposite -> F1: "Registry avoids collocating comparable cases"

This is potentially the last internal probe before closure by exhaustion.
"""

import os
import json
from collections import defaultdict, Counter
import math
import random

# Known prefixes from CAS-MORPH phase
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Extended suffixes for decomposition
SUFFIXES = ['aiin', 'ain', 'ar', 'al', 'or', 'ol', 'am', 'an', 'in',
            'y', 'dy', 'ey', 'edy', 'eedy', 'chy', 'shy',
            'r', 'l', 's', 'd', 'n', 'm']
SUFFIX_PATTERNS = sorted(SUFFIXES, key=len, reverse=True)


def load_currier_a_full():
    """Load Currier A tokens with full metadata, preserving order."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []
    line_order = 0  # Global order counter

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 11:
                currier = parts[6].strip('"').strip()
                if currier == 'A':
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    line_num = parts[11].strip('"').strip()

                    # Skip damaged tokens
                    if token and '*' not in token:
                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'section': section,
                            'line_num': line_num,
                            'order': line_order
                        })
                        line_order += 1

    return tokens


def decompose_token(token):
    """Decompose token into PREFIX + MIDDLE + SUFFIX."""
    prefix = None
    remainder = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            remainder = token[len(p):]
            break

    if not prefix:
        return None, None, None

    suffix = None
    middle = remainder

    for s in SUFFIX_PATTERNS:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            middle = remainder[:-len(s)]
            break
        elif remainder == s:
            suffix = s
            middle = ''
            break

    if not suffix:
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        elif len(remainder) == 1:
            suffix = remainder
            middle = ''
        else:
            suffix = ''
            middle = ''

    return prefix, middle, suffix


def build_middle_universality_map():
    """Build map of MIDDLE -> number of prefixes it works with."""
    data_path = r'C:\git\voynich\results\currier_a_modeling_data.json'

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    p_middle_given_prefix = data['target_1_token_census']['p_middle_given_prefix']

    # For each MIDDLE, count prefixes
    middle_prefix_count = defaultdict(int)

    for prefix in PREFIXES:
        if prefix in p_middle_given_prefix:
            for middle, prob in p_middle_given_prefix[prefix].items():
                if prob > 0:
                    middle_prefix_count[middle] += 1

    return middle_prefix_count


def classify_entry_universality_band(middles, middle_prefix_count):
    """
    Classify entry by MIDDLE universality into three bands.

    Returns:
    - 'exclusive': max universality = 1 (all single-domain)
    - 'shared': max universality in 2-5 (Goldilocks zone)
    - 'universal': max universality >= 6 (cross-domain)
    """
    if not middles:
        return 'unknown'

    max_universality = max(middle_prefix_count.get(m, 1) for m in middles)

    if max_universality >= 6:
        return 'universal'
    elif max_universality >= 2:
        return 'shared'
    else:
        return 'exclusive'


def compute_adjacency_match_rate(entries, window_sizes):
    """
    For each entry, check if entries within +/-k positions share the same band.

    Returns dict: {k: match_rate}
    """
    n = len(entries)
    results = {}

    for k in window_sizes:
        matches = 0
        total = 0

        for i, e in enumerate(entries):
            band = e['band']
            if band == 'unknown':
                continue

            # Check entries within window
            for j in range(max(0, i - k), min(n, i + k + 1)):
                if i == j:
                    continue

                neighbor_band = entries[j]['band']
                if neighbor_band == 'unknown':
                    continue

                total += 1
                if band == neighbor_band:
                    matches += 1

        results[k] = matches / total if total > 0 else 0

    return results


def compute_shuffled_baseline(entries, window_sizes, n_shuffles=100):
    """
    Compute expected match rate under shuffled band assignments.
    Shuffle bands while preserving section structure.
    """
    random.seed(42)

    # Group by section for section-matched shuffling
    by_section = defaultdict(list)
    for i, e in enumerate(entries):
        by_section[e['section']].append((i, e['band']))

    baseline_results = {k: [] for k in window_sizes}

    for _ in range(n_shuffles):
        # Shuffle bands within each section
        shuffled_entries = entries.copy()

        for section, items in by_section.items():
            indices = [i for i, _ in items]
            bands = [b for _, b in items]
            random.shuffle(bands)

            for idx, band in zip(indices, bands):
                shuffled_entries[idx] = {**entries[idx], 'band': band}

        # Compute match rates
        rates = compute_adjacency_match_rate(shuffled_entries, window_sizes)
        for k in window_sizes:
            baseline_results[k].append(rates[k])

    # Return mean and std for each k
    return {
        k: {
            'mean': sum(vals) / len(vals),
            'std': math.sqrt(sum((v - sum(vals)/len(vals))**2 for v in vals) / len(vals))
        }
        for k, vals in baseline_results.items()
    }


def z_score_test(observed, baseline_mean, baseline_std, n):
    """Compute z-score and p-value for observed vs baseline."""
    if baseline_std == 0:
        return 0, 1.0

    z = (observed - baseline_mean) / baseline_std
    # Two-tailed p-value
    from math import erf
    p = 2 * (1 - 0.5 * (1 + erf(abs(z) / math.sqrt(2))))
    return z, p


def run_analysis():
    """Main analysis function."""
    print("=" * 70)
    print("F-A-009: COMPARABILITY WINDOW FIT")
    print("=" * 70)
    print()

    # Set random seed for reproducibility
    random.seed(42)

    # Step 1: Build MIDDLE universality map
    print("Step 1: Building MIDDLE universality map...")
    middle_prefix_count = build_middle_universality_map()
    print(f"  Total MIDDLEs: {len(middle_prefix_count)}")

    # Step 2: Load and order entries
    print("\nStep 2: Loading Currier A entries in manuscript order...")
    tokens = load_currier_a_full()

    # Group by (folio, line_num) preserving order
    entry_dict = defaultdict(list)
    entry_order = {}

    for t in tokens:
        key = (t['folio'], t['line_num'])
        entry_dict[key].append(t)
        if key not in entry_order:
            entry_order[key] = t['order']

    # Sort entries by manuscript order
    sorted_keys = sorted(entry_dict.keys(), key=lambda k: entry_order[k])

    print(f"  Total entries (ordered): {len(sorted_keys)}")

    # Step 3: Classify entries by universality band
    print("\nStep 3: Classifying entries by universality band...")

    entries = []
    for key in sorted_keys:
        entry_tokens = entry_dict[key]
        section = entry_tokens[0]['section']

        # Decompose and get MIDDLEs
        middles = []
        for t in entry_tokens:
            prefix, middle, suffix = decompose_token(t['token'])
            if prefix and middle:
                middles.append(middle)

        band = classify_entry_universality_band(middles, middle_prefix_count)

        entries.append({
            'key': key,
            'section': section,
            'band': band,
            'token_count': len(entry_tokens),
            'middle_count': len(middles)
        })

    # Count bands
    band_counts = Counter(e['band'] for e in entries)
    print(f"\nBand distribution:")
    for band in ['exclusive', 'shared', 'universal', 'unknown']:
        if band in band_counts:
            pct = 100 * band_counts[band] / len(entries)
            print(f"  {band}: {band_counts[band]} ({pct:.1f}%)")

    # Step 4: Compute observed adjacency match rates
    print("\n" + "-" * 50)
    print("Step 4: Computing observed adjacency match rates...")

    window_sizes = [1, 2, 3, 5]
    observed_rates = compute_adjacency_match_rate(entries, window_sizes)

    print("\nObserved same-band adjacency rates:")
    for k in window_sizes:
        print(f"  +/-{k} window: {100*observed_rates[k]:.2f}%")

    # Step 5: Compute shuffled baselines
    print("\n" + "-" * 50)
    print("Step 5: Computing shuffled baselines (100 shuffles)...")

    baseline_stats = compute_shuffled_baseline(entries, window_sizes, n_shuffles=100)

    print("\nBaseline (section-matched shuffle):")
    for k in window_sizes:
        mean = baseline_stats[k]['mean']
        std = baseline_stats[k]['std']
        print(f"  +/-{k} window: {100*mean:.2f}% (+/- {100*std:.2f}%)")

    # Step 6: Statistical comparison
    print("\n" + "-" * 50)
    print("Step 6: Statistical comparison (observed vs baseline)...")

    test_results = {}
    significant_windows = 0

    for k in window_sizes:
        obs = observed_rates[k]
        base_mean = baseline_stats[k]['mean']
        base_std = baseline_stats[k]['std']

        z, p = z_score_test(obs, base_mean, base_std, len(entries))
        diff = obs - base_mean

        test_results[k] = {
            'observed': obs,
            'baseline_mean': base_mean,
            'baseline_std': base_std,
            'difference': diff,
            'z': z,
            'p': p
        }

        direction = "CLUSTERING" if diff > 0 else "AVOIDANCE"
        sig = "*" if p < 0.05 else ""

        if p < 0.05 and diff > 0:
            significant_windows += 1

        print(f"\n+/-{k} window:")
        print(f"  Observed: {100*obs:.2f}%, Baseline: {100*base_mean:.2f}%")
        print(f"  Difference: {100*diff:+.2f} percentage points")
        print(f"  z = {z:.2f}, p = {p:.4f} {sig}")
        print(f"  Direction: {direction}")

    # Step 7: Section-stratified analysis
    print("\n" + "-" * 50)
    print("Step 7: Section-stratified analysis...")

    section_results = {}

    for section in ['H', 'P', 'T']:
        sec_entries = [e for e in entries if e['section'] == section]
        if len(sec_entries) < 20:
            print(f"\n{section} section: insufficient data ({len(sec_entries)} entries)")
            continue

        sec_observed = compute_adjacency_match_rate(sec_entries, [1, 3])

        # Quick shuffle for this section
        sec_baseline = compute_shuffled_baseline(sec_entries, [1, 3], n_shuffles=50)

        section_results[section] = {}
        print(f"\n{section} section (n={len(sec_entries)}):")

        for k in [1, 3]:
            obs = sec_observed[k]
            base = sec_baseline[k]['mean']
            diff = obs - base
            z, p = z_score_test(obs, base, sec_baseline[k]['std'], len(sec_entries))

            section_results[section][k] = {
                'observed': obs,
                'baseline': base,
                'diff': diff,
                'z': z,
                'p': p
            }

            print(f"  +/-{k}: obs={100*obs:.2f}%, base={100*base:.2f}%, diff={100*diff:+.2f}pp, p={p:.3f}")

    # Step 8: Focus on "Goldilocks" band (shared)
    print("\n" + "-" * 50)
    print("Step 8: Focus on SHARED band (Goldilocks zone, 2-5 prefixes)...")

    shared_entries = [e for e in entries if e['band'] == 'shared']
    shared_indices = [i for i, e in enumerate(entries) if e['band'] == 'shared']

    # Check if shared entries are closer to each other than expected
    if len(shared_indices) >= 10:
        # Compute mean distance to nearest same-band neighbor
        distances = []
        for i, idx in enumerate(shared_indices):
            min_dist = float('inf')
            for j, other_idx in enumerate(shared_indices):
                if i != j:
                    dist = abs(idx - other_idx)
                    if dist < min_dist:
                        min_dist = dist
            if min_dist < float('inf'):
                distances.append(min_dist)

        mean_dist = sum(distances) / len(distances) if distances else 0

        # Expected distance under uniform random placement
        n_total = len(entries)
        n_shared = len(shared_indices)
        expected_dist = n_total / (n_shared + 1)  # Approximate

        print(f"\nSHARED band nearest-neighbor analysis:")
        print(f"  Total entries: {n_total}")
        print(f"  SHARED entries: {n_shared} ({100*n_shared/n_total:.1f}%)")
        print(f"  Mean distance to nearest SHARED neighbor: {mean_dist:.1f} entries")
        print(f"  Expected under uniform placement: ~{expected_dist:.1f} entries")
        print(f"  Ratio (obs/expected): {mean_dist/expected_dist:.2f}")

        shared_clustering = mean_dist < expected_dist
    else:
        shared_clustering = False
        mean_dist = 0
        expected_dist = 0

    # Step 9: Determine fit tier
    print("\n" + "=" * 70)
    print("RESULT SUMMARY")
    print("=" * 70)

    # Primary criterion: significant clustering at any window with p < 0.05
    has_clustering = significant_windows >= 1
    has_robust_clustering = significant_windows >= 2

    # Check direction
    overall_direction = "CLUSTERING" if sum(test_results[k]['difference'] for k in window_sizes) > 0 else "AVOIDANCE"

    print(f"\nPre-declared outcome conditions:")
    print(f"  1. Significant clustering (p < 0.05 at any window): {'YES' if has_clustering else 'NO'}")
    print(f"  2. Robust clustering (p < 0.05 at >=2 windows): {'YES' if has_robust_clustering else 'NO'}")
    print(f"  3. Overall direction: {overall_direction}")
    print(f"  4. Significant windows: {significant_windows}/{len(window_sizes)}")

    if has_robust_clustering and overall_direction == "CLUSTERING":
        fit_tier = "F2"
        result = "SUCCESS"
        interpretation = "Relational comparison is weakly scaffolded by layout: similar entries cluster."
    elif has_clustering and overall_direction == "CLUSTERING":
        fit_tier = "F1"
        result = "PARTIAL"
        interpretation = "Weak layout scaffolding exists but is not robust across window sizes."
    elif has_clustering and overall_direction == "AVOIDANCE":
        fit_tier = "F1"
        result = "OPPOSITE"
        interpretation = "Registry avoids collocating comparable cases - anti-clustering."
    else:
        fit_tier = "F1"
        result = "NULL"
        interpretation = "Relationality is purely cognitive, not scaffolded by manuscript layout."

    print(f"\n{'='*50}")
    print(f"FIT TIER: {fit_tier}")
    print(f"RESULT: {result}")
    print(f"{'='*50}")
    print(f"\nInterpretation: {interpretation}")

    # Compile results
    results = {
        'fit_id': 'F-A-009',
        'fit_name': 'Comparability Window',
        'fit_tier': fit_tier,
        'result': result,
        'date': '2026-01-10',
        'entry_summary': {
            'total_entries': len(entries),
            'exclusive': band_counts.get('exclusive', 0),
            'shared': band_counts.get('shared', 0),
            'universal': band_counts.get('universal', 0)
        },
        'adjacency_tests': {
            str(k): {
                'observed': float(test_results[k]['observed']),
                'baseline_mean': float(test_results[k]['baseline_mean']),
                'baseline_std': float(test_results[k]['baseline_std']),
                'difference': float(test_results[k]['difference']),
                'z': float(test_results[k]['z']),
                'p': float(test_results[k]['p'])
            }
            for k in window_sizes
        },
        'section_results': {
            s: {
                str(k): {kk: float(vv) if isinstance(vv, float) else vv for kk, vv in v.items()}
                for k, v in sr.items()
            }
            for s, sr in section_results.items()
        },
        'shared_analysis': {
            'mean_neighbor_distance': float(mean_dist),
            'expected_distance': float(expected_dist),
            'ratio': float(mean_dist / expected_dist) if expected_dist > 0 else 0
        },
        'criteria_check': {
            'has_clustering': has_clustering,
            'has_robust_clustering': has_robust_clustering,
            'significant_windows': significant_windows,
            'direction': overall_direction
        },
        'interpretation': interpretation,
        'supports_constraints': [] if fit_tier == "F1" else ['relational_registry_synthesis'],
        'introduces_new_constraints': False
    }

    # Save results
    output_path = r'C:\git\voynich\results\currier_a_comparability_window.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    run_analysis()
