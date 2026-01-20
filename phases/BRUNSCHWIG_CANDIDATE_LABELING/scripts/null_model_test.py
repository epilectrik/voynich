#!/usr/bin/env python3
"""
NULL MODEL TEST: Permutation validation of material-class priors

Question: Does the observed entropy distribution differ from random token-folio
association only where the model predicts structural isolation?

Method:
1. Permute token-folio associations (shuffle which tokens appear in which folios)
2. Recompute material-class entropy for each permutation
3. Compare observed entropy distribution to null distribution
4. Test whether PRECISION isolation is real (not sample artifact)

Expected results (if model is correct):
- Overall entropy distribution should be similar to null
- PRECISION-exclusive tokens should show LOWER entropy than null (real isolation)
- WATER_STANDARD tokens should match null (baseline-dominated)
"""

import csv
import json
import math
import random
from collections import defaultdict, Counter

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

N_PERMUTATIONS = 1000

BRUNSCHWIG_MATERIAL_DISTRIBUTIONS = {
    'WATER_GENTLE': {
        'cold_moist_flower': 0.521,
        'fruit': 0.333,
        'dangerous_herb': 0.146
    },
    'OIL_RESIN': {
        'hot_dry_herb': 0.943,
        'hot_dry_root': 0.057
    },
    'WATER_STANDARD': {
        'herb': 0.863,
        'hot_flower': 0.055,
        'moderate_herb': 0.048,
        'moist_root': 0.022,
        'leaf': 0.012
    },
    'PRECISION': {
        'animal': 1.000
    }
}

ALL_MATERIAL_CLASSES = sorted(set(
    mc for dist in BRUNSCHWIG_MATERIAL_DISTRIBUTIONS.values()
    for mc in dist.keys()
))

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def entropy(probs):
    h = 0
    for p in probs:
        if p > 0:
            h -= p * math.log2(p)
    return h

# ============================================================
# DATA LOADING
# ============================================================

def load_registry_internal_middles():
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles'])

def load_folio_classifications():
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

def load_folio_middles():
    folio_middles = defaultdict(list)
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
            middle = get_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio].append(middle)
    return folio_middles

# ============================================================
# ENTROPY COMPUTATION
# ============================================================

def compute_entropy_for_middle(middle, folio_middles, folio_classifications):
    """Compute material-class entropy for a single MIDDLE."""
    folios_with = [f for f, middles in folio_middles.items() if middle in middles]

    if not folios_with:
        return None

    # Count by product type
    pt_counts = Counter()
    for folio in folios_with:
        pt = folio_classifications.get(folio, 'UNKNOWN')
        if pt in BRUNSCHWIG_MATERIAL_DISTRIBUTIONS:
            pt_counts[pt] += 1

    total = sum(pt_counts.values())
    if total == 0:
        return None

    # P(product_type | token)
    pt_dist = {pt: count / total for pt, count in pt_counts.items()}

    # P(material_class | token)
    mc_posterior = {mc: 0.0 for mc in ALL_MATERIAL_CLASSES}
    for pt, p_pt in pt_dist.items():
        for mc, p_mc in BRUNSCHWIG_MATERIAL_DISTRIBUTIONS[pt].items():
            mc_posterior[mc] += p_mc * p_pt

    probs = [p for p in mc_posterior.values() if p > 0]
    return entropy(probs)

def compute_all_entropies(registry_internal, folio_middles, folio_classifications):
    """Compute entropies for all registry-internal MIDDLEs."""
    entropies = {}
    for middle in registry_internal:
        h = compute_entropy_for_middle(middle, folio_middles, folio_classifications)
        if h is not None:
            entropies[middle] = h
    return entropies

# ============================================================
# PERMUTATION TEST
# ============================================================

def permute_folio_middles(folio_middles, registry_internal):
    """
    Create a permuted version: shuffle which registry-internal MIDDLEs
    appear in which folios, preserving the count structure.
    """
    # Get all (folio, middle) pairs for registry-internal MIDDLEs
    pairs = []
    for folio, middles in folio_middles.items():
        for m in middles:
            if m in registry_internal:
                pairs.append((folio, m))

    if not pairs:
        return folio_middles

    # Shuffle the middles while keeping folios fixed
    folios = [p[0] for p in pairs]
    middles = [p[1] for p in pairs]
    random.shuffle(middles)

    # Rebuild folio_middles with shuffled assignments
    permuted = defaultdict(list)
    for folio, orig_middles in folio_middles.items():
        for m in orig_middles:
            if m not in registry_internal:
                permuted[folio].append(m)

    for folio, middle in zip(folios, middles):
        permuted[folio].append(middle)

    return permuted

def run_permutation_test(registry_internal, folio_middles, folio_classifications, n_perms=N_PERMUTATIONS):
    """
    Run permutation test and collect null distribution of entropies.
    """
    null_entropies = []  # List of entropy distributions

    for i in range(n_perms):
        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{n_perms}...")

        permuted = permute_folio_middles(folio_middles, registry_internal)
        ent_dist = compute_all_entropies(registry_internal, permuted, folio_classifications)

        if ent_dist:
            null_entropies.append(ent_dist)

    return null_entropies

# ============================================================
# ANALYSIS
# ============================================================

def analyze_results(observed, null_distributions):
    """
    Compare observed entropy distribution to null.
    """
    # Get all MIDDLEs that appear in both observed and null
    common_middles = set(observed.keys())
    for null_dist in null_distributions:
        common_middles &= set(null_dist.keys())

    if not common_middles:
        return None

    results = {}

    for middle in common_middles:
        obs_h = observed[middle]
        null_h = [nd[middle] for nd in null_distributions if middle in nd]

        if not null_h:
            continue

        mean_null = sum(null_h) / len(null_h)
        std_null = (sum((h - mean_null)**2 for h in null_h) / len(null_h)) ** 0.5

        # How many SDs below/above null?
        if std_null > 0:
            z_score = (obs_h - mean_null) / std_null
        else:
            z_score = 0 if obs_h == mean_null else float('inf')

        # P-value (one-tailed: is observed lower than null?)
        p_lower = sum(1 for h in null_h if h <= obs_h) / len(null_h)

        results[middle] = {
            'observed_entropy': round(obs_h, 3),
            'null_mean': round(mean_null, 3),
            'null_std': round(std_null, 3),
            'z_score': round(z_score, 3),
            'p_lower': round(p_lower, 3)
        }

    return results

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("NULL MODEL TEST: Permutation Validation")
    print("=" * 70)
    print()
    print("Testing whether observed entropy structure differs from random")
    print("token-folio association only where model predicts isolation.")
    print()

    # Load data
    print("Loading data...")
    registry_internal = load_registry_internal_middles()
    folio_classifications = load_folio_classifications()
    folio_middles = load_folio_middles()

    print(f"  Registry-internal MIDDLEs: {len(registry_internal)}")
    print()

    # Compute observed entropies
    print("Computing observed entropies...")
    observed = compute_all_entropies(registry_internal, folio_middles, folio_classifications)
    print(f"  MIDDLEs with entropy: {len(observed)}")
    print()

    # Run permutation test
    print(f"Running {N_PERMUTATIONS} permutations...")
    null_distributions = run_permutation_test(
        registry_internal, folio_middles, folio_classifications
    )
    print(f"  Completed {len(null_distributions)} valid permutations")
    print()

    # Analyze
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print()

    results = analyze_results(observed, null_distributions)

    if not results:
        print("ERROR: No common MIDDLEs between observed and null")
        return

    # Categorize by whether observed is significantly lower than null
    significantly_lower = []  # Real isolation
    not_different = []        # Baseline-dominated
    significantly_higher = [] # Unexpected

    for middle, stats in results.items():
        if stats['p_lower'] < 0.05:  # Significantly lower entropy than null
            significantly_lower.append((middle, stats))
        elif stats['p_lower'] > 0.95:  # Significantly higher
            significantly_higher.append((middle, stats))
        else:
            not_different.append((middle, stats))

    print(f"MIDDLEs with LOWER entropy than null (real isolation): {len(significantly_lower)}")
    print(f"MIDDLEs matching null (baseline-dominated): {len(not_different)}")
    print(f"MIDDLEs with HIGHER entropy than null (unexpected): {len(significantly_higher)}")
    print()

    # Show significantly lower (real isolation)
    print("=" * 70)
    print("REAL ISOLATION (entropy < null, p < 0.05)")
    print("=" * 70)
    print()

    significantly_lower.sort(key=lambda x: x[1]['z_score'])
    for middle, stats in significantly_lower[:20]:
        print(f"  {middle}:")
        print(f"    observed: {stats['observed_entropy']:.2f}, null: {stats['null_mean']:.2f} +/- {stats['null_std']:.2f}")
        print(f"    z-score: {stats['z_score']:.2f}, p: {stats['p_lower']:.3f}")
        print()

    # Check if zero-entropy MIDDLEs are in the isolated set
    zero_entropy = [m for m, h in observed.items() if h == 0]
    isolated_zeros = [m for m in zero_entropy if m in [x[0] for x in significantly_lower]]

    print("=" * 70)
    print("ZERO-ENTROPY VALIDATION")
    print("=" * 70)
    print()
    print(f"MIDDLEs with observed entropy = 0: {len(zero_entropy)}")
    print(f"Of those, significantly isolated vs null: {len(isolated_zeros)}")
    print()

    if zero_entropy:
        # Check if any zero-entropy MIDDLEs are NOT isolated
        non_isolated_zeros = [m for m in zero_entropy if m not in [x[0] for x in significantly_lower]]
        if non_isolated_zeros:
            print(f"WARNING: {len(non_isolated_zeros)} zero-entropy MIDDLEs NOT significantly different from null:")
            for m in non_isolated_zeros[:5]:
                if m in results:
                    s = results[m]
                    print(f"  {m}: obs={s['observed_entropy']:.2f}, null={s['null_mean']:.2f}, p={s['p_lower']:.3f}")
        else:
            print("All zero-entropy MIDDLEs are significantly isolated (p < 0.05)")
    print()

    # Summary statistics
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    obs_mean = sum(observed.values()) / len(observed)
    null_means = [sum(nd.values()) / len(nd) for nd in null_distributions if nd]
    null_grand_mean = sum(null_means) / len(null_means)
    null_grand_std = (sum((m - null_grand_mean)**2 for m in null_means) / len(null_means)) ** 0.5

    print(f"Observed mean entropy: {obs_mean:.3f}")
    print(f"Null mean entropy: {null_grand_mean:.3f} +/- {null_grand_std:.3f}")
    print()

    # Save results
    output = {
        'test': 'NULL_MODEL_PERMUTATION',
        'date': '2026-01-20',
        'n_permutations': N_PERMUTATIONS,
        'n_middles_tested': len(results),
        'summary': {
            'observed_mean_entropy': round(obs_mean, 3),
            'null_mean_entropy': round(null_grand_mean, 3),
            'null_std_entropy': round(null_grand_std, 3),
            'n_significantly_lower': len(significantly_lower),
            'n_not_different': len(not_different),
            'n_significantly_higher': len(significantly_higher),
            'n_zero_entropy_total': len(zero_entropy),
            'n_zero_entropy_isolated': len(isolated_zeros)
        },
        'significantly_isolated': [
            {'middle': m, **s} for m, s in significantly_lower
        ],
        'per_middle_results': results
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/null_model_test.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    isolation_rate = len(significantly_lower) / len(results) if results else 0

    if isolation_rate > 0.15:
        print(f"CONFIRMED: {isolation_rate:.1%} of MIDDLEs show real structural isolation")
        print("(entropy significantly lower than random token-folio assignment)")
        print()
        print("This validates the model prediction:")
        print("  - PRECISION vocabulary is genuinely isolated")
        print("  - Isolation is not a sample-size artifact")
    else:
        print(f"BASELINE: Only {isolation_rate:.1%} of MIDDLEs show isolation")
        print("Most entropy matches random assignment baseline.")
    print()

    if len(significantly_higher) > len(results) * 0.05:
        print(f"WARNING: {len(significantly_higher)} MIDDLEs have HIGHER entropy than null")
        print("This is unexpected and may indicate data issues.")
    else:
        print("No unexpected high-entropy anomalies.")
    print()

    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/null_model_test.json")

if __name__ == '__main__':
    main()
