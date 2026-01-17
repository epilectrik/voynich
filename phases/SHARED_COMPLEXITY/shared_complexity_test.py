#!/usr/bin/env python3
"""
SHARED-COMPLEXITY: Shared Vocabulary Evolution vs B Folio Complexity

Phase: SHARED-COMPLEXITY
Research Question: Does SHARED MIDDLE participation change with B complexity?

Hypothesis (Expert-Predicted):
As B complexity increases, SHARED MIDDLEs should decrease in dominance,
but shift from HUB-shared to TAIL-shared roles.

Expected trends:
- % SHARED (raw): Mild decrease or flat
- SHARED-hub usage: Strong decrease
- SHARED-tail usage: Strong increase
- B-EXCL usage: Increase (grammar load)
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr, kruskal, pearsonr
import numpy as np

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
B_METRICS_PATH = PROJECT_ROOT / 'results' / 'b_macro_scaffold_audit.json'
OUTPUT_PATH = PROJECT_ROOT / 'results' / 'shared_complexity.json'

# Standard PREFIX list (8 marker classes from C235)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']

# Extended prefixes (compound forms that should be recognized)
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',  # C+ch compounds
    'lch', 'lk', 'lsh', 'yk',  # L-compounds (B-specific per C298)
    'ke', 'te', 'se', 'de', 'pe',  # e-compounds
    'so', 'ko', 'to', 'do', 'po',  # o-compounds
    'sa', 'ka', 'ta',  # a-compounds
    'al', 'ar', 'or',  # vowel-initial
]

# All prefixes (try longest first for matching)
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

# Standard suffix list (comprehensive, try longest first)
SUFFIXES = [
    # Complex suffixes (longest first)
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]

# REGIME ordering (by CEI): R2 < R1 < R4 < R3
REGIME_ORDER = {'REGIME_2': 0, 'REGIME_1': 1, 'REGIME_4': 2, 'REGIME_3': 3}


def extract_middle(token):
    """
    Extract MIDDLE from token using PREFIX + MIDDLE + SUFFIX decomposition.
    Returns (prefix, middle, suffix) or (None, None, None) if unparseable.
    """
    # Find prefix (try longest first)
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]

    # Find suffix (try longest first)
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
        suffix = ''

    # Empty middle is valid (token is just PREFIX+SUFFIX)
    if middle == '':
        middle = '_EMPTY_'

    return prefix, middle, suffix


def load_data():
    """Load H-only transcript data, separate by Currier system and folio."""
    a_tokens = []
    b_tokens_by_folio = defaultdict(list)
    a_middles = Counter()
    b_middles = Counter()

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # H-only filter (CRITICAL)
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                word = parts[0].strip('"').strip().lower()
                lang = parts[6].strip('"').strip()
                folio = parts[2].strip('"').strip()  # Column 2 is folio, not 1

                if not word or '*' in word:
                    continue

                prefix, middle, suffix = extract_middle(word)
                if middle is None:
                    continue

                if lang == 'A':
                    a_tokens.append(word)
                    a_middles[middle] += 1
                elif lang == 'B':
                    b_tokens_by_folio[folio].append((word, middle))
                    b_middles[middle] += 1

    return a_tokens, b_tokens_by_folio, a_middles, b_middles


def build_middle_classifications(a_middles, b_middles):
    """Build SHARED, A-EXCL, B-EXCL sets."""
    a_set = set(a_middles.keys())
    b_set = set(b_middles.keys())

    shared = a_set & b_set
    a_excl = a_set - b_set
    b_excl = b_set - a_set

    # Compute combined frequency for shared MIDDLEs
    shared_freq = {m: a_middles[m] + b_middles[m] for m in shared}

    return shared, a_excl, b_excl, shared_freq


def partition_shared_by_frequency(shared_set, shared_freq):
    """
    Split SHARED into HUB and TAIL tiers.
    - SHARED-HUB: Top 10% frequency within SHARED
    - SHARED-TAIL: Bottom 50% frequency within SHARED
    """
    if not shared_set:
        return set(), set()

    sorted_shared = sorted(shared_set, key=lambda m: shared_freq.get(m, 0), reverse=True)
    n = len(sorted_shared)

    hub_cutoff = max(1, int(n * 0.10))
    tail_start = int(n * 0.50)

    shared_hub = set(sorted_shared[:hub_cutoff])
    shared_tail = set(sorted_shared[tail_start:])

    return shared_hub, shared_tail


def load_b_complexity_metrics():
    """Load CEI, REGIME, and other complexity metrics per B folio."""
    with open(B_METRICS_PATH, 'r') as f:
        data = json.load(f)

    metrics = {}
    for folio, features in data.get('features', {}).items():
        metrics[folio] = {
            'cei': features.get('cei_total', 0),
            'regime': features.get('regime', 'UNKNOWN'),
            'regime_ordinal': REGIME_ORDER.get(features.get('regime'), -1),
            'hazard_density': features.get('hazard_density', 0),
            'escape_density': features.get('qo_density', 0),
            'near_miss_count': features.get('near_miss_count', 0),
            'recovery_ops_count': features.get('recovery_ops_count', 0),
        }

    return metrics


def compute_folio_composition(folio_middles, shared, a_excl, b_excl, shared_hub, shared_tail):
    """Compute MIDDLE class composition for a folio."""
    middles = [m for _, m in folio_middles]
    total = len(middles)

    if total == 0:
        return None

    # Count by class
    shared_count = sum(1 for m in middles if m in shared)
    a_excl_count = sum(1 for m in middles if m in a_excl)
    b_excl_count = sum(1 for m in middles if m in b_excl)

    # Within SHARED breakdown
    shared_hub_count = sum(1 for m in middles if m in shared_hub)
    shared_tail_count = sum(1 for m in middles if m in shared_tail)

    # Percentages
    pct_shared = shared_count / total
    pct_a_excl = a_excl_count / total
    pct_b_excl = b_excl_count / total

    # Within-shared percentages (avoid division by zero)
    pct_shared_hub = shared_hub_count / shared_count if shared_count > 0 else 0
    pct_shared_tail = shared_tail_count / shared_count if shared_count > 0 else 0

    # Entropy of MIDDLE classes
    probs = [p for p in [pct_shared, pct_a_excl, pct_b_excl] if p > 0]
    class_entropy = -sum(p * np.log(p) for p in probs) if probs else 0

    return {
        'total_middles': total,
        'shared_count': shared_count,
        'a_excl_count': a_excl_count,
        'b_excl_count': b_excl_count,
        'shared_hub_count': shared_hub_count,
        'shared_tail_count': shared_tail_count,
        'pct_shared': pct_shared,
        'pct_a_excl': pct_a_excl,
        'pct_b_excl': pct_b_excl,
        'pct_shared_hub': pct_shared_hub,
        'pct_shared_tail': pct_shared_tail,
        'class_entropy': class_entropy,
    }


def run_correlation_tests(compositions, metrics):
    """Run Spearman correlations between composition metrics and complexity."""
    results = {}

    # Get aligned arrays
    folios = sorted(set(compositions.keys()) & set(metrics.keys()))

    if len(folios) < 10:
        return {'error': f'Only {len(folios)} folios with both composition and metrics'}

    # Extract arrays
    cei = np.array([metrics[f]['cei'] for f in folios])
    regime_ord = np.array([metrics[f]['regime_ordinal'] for f in folios])
    hazard = np.array([metrics[f]['hazard_density'] for f in folios])
    escape = np.array([metrics[f]['escape_density'] for f in folios])

    pct_shared = np.array([compositions[f]['pct_shared'] for f in folios])
    pct_a_excl = np.array([compositions[f]['pct_a_excl'] for f in folios])
    pct_b_excl = np.array([compositions[f]['pct_b_excl'] for f in folios])
    pct_shared_hub = np.array([compositions[f]['pct_shared_hub'] for f in folios])
    pct_shared_tail = np.array([compositions[f]['pct_shared_tail'] for f in folios])

    # Spearman correlations with CEI
    results['cei_correlations'] = {
        'pct_shared': {'rho': spearmanr(pct_shared, cei)[0], 'p': spearmanr(pct_shared, cei)[1]},
        'pct_a_excl': {'rho': spearmanr(pct_a_excl, cei)[0], 'p': spearmanr(pct_a_excl, cei)[1]},
        'pct_b_excl': {'rho': spearmanr(pct_b_excl, cei)[0], 'p': spearmanr(pct_b_excl, cei)[1]},
        'pct_shared_hub': {'rho': spearmanr(pct_shared_hub, cei)[0], 'p': spearmanr(pct_shared_hub, cei)[1]},
        'pct_shared_tail': {'rho': spearmanr(pct_shared_tail, cei)[0], 'p': spearmanr(pct_shared_tail, cei)[1]},
    }

    # Spearman correlations with hazard density
    results['hazard_correlations'] = {
        'pct_shared': {'rho': spearmanr(pct_shared, hazard)[0], 'p': spearmanr(pct_shared, hazard)[1]},
        'pct_shared_hub': {'rho': spearmanr(pct_shared_hub, hazard)[0], 'p': spearmanr(pct_shared_hub, hazard)[1]},
        'pct_shared_tail': {'rho': spearmanr(pct_shared_tail, hazard)[0], 'p': spearmanr(pct_shared_tail, hazard)[1]},
    }

    # Spearman correlations with escape density (inverse complexity)
    results['escape_correlations'] = {
        'pct_shared': {'rho': spearmanr(pct_shared, escape)[0], 'p': spearmanr(pct_shared, escape)[1]},
        'pct_shared_hub': {'rho': spearmanr(pct_shared_hub, escape)[0], 'p': spearmanr(pct_shared_hub, escape)[1]},
        'pct_shared_tail': {'rho': spearmanr(pct_shared_tail, escape)[0], 'p': spearmanr(pct_shared_tail, escape)[1]},
    }

    # Kruskal-Wallis test across regimes
    regime_groups = defaultdict(list)
    for f in folios:
        regime_groups[metrics[f]['regime']].append(compositions[f]['pct_shared'])

    if len(regime_groups) >= 2:
        groups = [regime_groups[r] for r in sorted(regime_groups.keys(), key=lambda x: REGIME_ORDER.get(x, 99))]
        if all(len(g) >= 2 for g in groups):
            kw_stat, kw_p = kruskal(*groups)
            results['regime_kruskal_wallis'] = {
                'statistic': kw_stat,
                'p': kw_p,
                'n_groups': len(groups),
                'group_sizes': [len(g) for g in groups],
            }

            # Regime means
            results['regime_means'] = {
                r: {'mean_pct_shared': np.mean(regime_groups[r]), 'n': len(regime_groups[r])}
                for r in regime_groups
            }

    return results


def run_permutation_test(compositions, metrics, n_perms=1000):
    """Run permutation test to control for Zipf frequency artifacts."""
    folios = sorted(set(compositions.keys()) & set(metrics.keys()))

    if len(folios) < 10:
        return {'error': 'Insufficient folios'}

    cei = np.array([metrics[f]['cei'] for f in folios])
    pct_shared = np.array([compositions[f]['pct_shared'] for f in folios])
    pct_shared_hub = np.array([compositions[f]['pct_shared_hub'] for f in folios])

    # Observed correlations
    obs_rho_shared, _ = spearmanr(pct_shared, cei)
    obs_rho_hub, _ = spearmanr(pct_shared_hub, cei)

    # Permutation null distribution
    perm_rhos_shared = []
    perm_rhos_hub = []

    np.random.seed(42)
    for _ in range(n_perms):
        perm_idx = np.random.permutation(len(cei))
        perm_cei = cei[perm_idx]
        perm_rhos_shared.append(spearmanr(pct_shared, perm_cei)[0])
        perm_rhos_hub.append(spearmanr(pct_shared_hub, perm_cei)[0])

    # Two-tailed p-values
    perm_p_shared = np.mean(np.abs(perm_rhos_shared) >= np.abs(obs_rho_shared))
    perm_p_hub = np.mean(np.abs(perm_rhos_hub) >= np.abs(obs_rho_hub))

    return {
        'n_permutations': n_perms,
        'pct_shared_vs_cei': {
            'observed_rho': obs_rho_shared,
            'permutation_p': perm_p_shared,
        },
        'pct_shared_hub_vs_cei': {
            'observed_rho': obs_rho_hub,
            'permutation_p': perm_p_hub,
        },
    }


def main():
    print("=" * 70)
    print("SHARED-COMPLEXITY: Shared Vocabulary Evolution vs B Folio Complexity")
    print("=" * 70)
    print()

    # Step 1: Load data
    print("Loading H-only data...")
    a_tokens, b_tokens_by_folio, a_middles, b_middles = load_data()
    print(f"  Currier A tokens: {len(a_tokens):,}")
    print(f"  Currier B folios: {len(b_tokens_by_folio):,}")
    print(f"  A unique MIDDLEs: {len(a_middles):,}")
    print(f"  B unique MIDDLEs: {len(b_middles):,}")
    print()

    # Step 2: Build MIDDLE classifications
    print("Building MIDDLE classifications...")
    shared, a_excl, b_excl, shared_freq = build_middle_classifications(a_middles, b_middles)
    print(f"  SHARED: {len(shared):,}")
    print(f"  A-EXCL: {len(a_excl):,}")
    print(f"  B-EXCL: {len(b_excl):,}")

    # Partition SHARED by frequency
    shared_hub, shared_tail = partition_shared_by_frequency(shared, shared_freq)
    print(f"  SHARED-HUB (top 10%): {len(shared_hub):,}")
    print(f"  SHARED-TAIL (bottom 50%): {len(shared_tail):,}")
    print()

    # Step 3: Load B complexity metrics
    print("Loading B complexity metrics...")
    b_metrics = load_b_complexity_metrics()
    print(f"  Folios with metrics: {len(b_metrics):,}")
    print()

    # Step 4: Compute per-folio composition
    print("Computing per-folio composition...")
    compositions = {}
    for folio, tokens in b_tokens_by_folio.items():
        comp = compute_folio_composition(tokens, shared, a_excl, b_excl, shared_hub, shared_tail)
        if comp:
            compositions[folio] = comp

    print(f"  Folios with composition: {len(compositions):,}")

    # Check coverage
    common_folios = set(compositions.keys()) & set(b_metrics.keys())
    print(f"  Folios with both: {len(common_folios):,}")
    print()

    # Step 5: Run statistical tests
    print("Running correlation tests...")
    correlation_results = run_correlation_tests(compositions, b_metrics)
    print()

    # Step 6: Run permutation control
    print("Running permutation control (1000 permutations)...")
    permutation_results = run_permutation_test(compositions, b_metrics, n_perms=1000)
    print()

    # Print results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    print("\n--- CEI Correlations ---")
    for metric, vals in correlation_results.get('cei_correlations', {}).items():
        sig = "***" if vals['p'] < 0.001 else "**" if vals['p'] < 0.01 else "*" if vals['p'] < 0.05 else ""
        print(f"  {metric}: rho={vals['rho']:.3f}, p={vals['p']:.4f} {sig}")

    print("\n--- Hazard Density Correlations ---")
    for metric, vals in correlation_results.get('hazard_correlations', {}).items():
        sig = "***" if vals['p'] < 0.001 else "**" if vals['p'] < 0.01 else "*" if vals['p'] < 0.05 else ""
        print(f"  {metric}: rho={vals['rho']:.3f}, p={vals['p']:.4f} {sig}")

    print("\n--- Escape Density Correlations (inverse complexity) ---")
    for metric, vals in correlation_results.get('escape_correlations', {}).items():
        sig = "***" if vals['p'] < 0.001 else "**" if vals['p'] < 0.01 else "*" if vals['p'] < 0.05 else ""
        print(f"  {metric}: rho={vals['rho']:.3f}, p={vals['p']:.4f} {sig}")

    if 'regime_kruskal_wallis' in correlation_results:
        kw = correlation_results['regime_kruskal_wallis']
        print(f"\n--- Regime Kruskal-Wallis ---")
        print(f"  H={kw['statistic']:.3f}, p={kw['p']:.4f}")

    if 'regime_means' in correlation_results:
        print(f"\n--- Regime Means (% SHARED) ---")
        for regime in ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']:
            if regime in correlation_results['regime_means']:
                rm = correlation_results['regime_means'][regime]
                print(f"  {regime}: {rm['mean_pct_shared']:.3f} (n={rm['n']})")

    print("\n--- Permutation Control ---")
    if 'pct_shared_vs_cei' in permutation_results:
        ps = permutation_results['pct_shared_vs_cei']
        print(f"  pct_shared vs CEI: rho={ps['observed_rho']:.3f}, perm_p={ps['permutation_p']:.4f}")
    if 'pct_shared_hub_vs_cei' in permutation_results:
        ph = permutation_results['pct_shared_hub_vs_cei']
        print(f"  pct_shared_hub vs CEI: rho={ph['observed_rho']:.3f}, perm_p={ph['permutation_p']:.4f}")

    # Interpretation
    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    # Check hypothesis
    cei_corrs = correlation_results.get('cei_correlations', {})
    shared_hub_cei = cei_corrs.get('pct_shared_hub', {})
    shared_tail_cei = cei_corrs.get('pct_shared_tail', {})
    b_excl_cei = cei_corrs.get('pct_b_excl', {})

    hypothesis_supported = 0
    hypothesis_details = []

    # Check SHARED-hub decreases with CEI
    if shared_hub_cei.get('rho', 0) < 0 and shared_hub_cei.get('p', 1) < 0.05:
        hypothesis_supported += 1
        hypothesis_details.append("SHARED-hub decreases with CEI (SUPPORTED)")
    else:
        hypothesis_details.append(f"SHARED-hub vs CEI: rho={shared_hub_cei.get('rho', 0):.3f}, p={shared_hub_cei.get('p', 1):.4f} (NOT SUPPORTED)")

    # Check SHARED-tail increases with CEI
    if shared_tail_cei.get('rho', 0) > 0 and shared_tail_cei.get('p', 1) < 0.05:
        hypothesis_supported += 1
        hypothesis_details.append("SHARED-tail increases with CEI (SUPPORTED)")
    else:
        hypothesis_details.append(f"SHARED-tail vs CEI: rho={shared_tail_cei.get('rho', 0):.3f}, p={shared_tail_cei.get('p', 1):.4f} (NOT SUPPORTED)")

    # Check B-EXCL increases with CEI
    if b_excl_cei.get('rho', 0) > 0 and b_excl_cei.get('p', 1) < 0.05:
        hypothesis_supported += 1
        hypothesis_details.append("B-EXCL increases with CEI (SUPPORTED)")
    else:
        hypothesis_details.append(f"B-EXCL vs CEI: rho={b_excl_cei.get('rho', 0):.3f}, p={b_excl_cei.get('p', 1):.4f} (NOT SUPPORTED)")

    print(f"\nHypothesis checks: {hypothesis_supported}/3 supported")
    for detail in hypothesis_details:
        print(f"  - {detail}")

    if hypothesis_supported >= 2:
        print("\n** HYPOTHESIS SUPPORTED: Shared vocabulary shows complexity-dependent role evolution **")
    else:
        print("\n** HYPOTHESIS NOT SUPPORTED: Shared vocabulary appears complexity-invariant **")

    # Save results
    results = {
        'metadata': {
            'phase': 'SHARED-COMPLEXITY',
            'question': 'Does SHARED MIDDLE participation change with B complexity?',
            'n_b_folios': len(b_tokens_by_folio),
            'n_folios_with_metrics': len(common_folios),
        },
        'middle_classifications': {
            'shared_count': len(shared),
            'a_excl_count': len(a_excl),
            'b_excl_count': len(b_excl),
            'shared_hub_count': len(shared_hub),
            'shared_tail_count': len(shared_tail),
        },
        'correlation_results': correlation_results,
        'permutation_results': permutation_results,
        'hypothesis_evaluation': {
            'supported_count': hypothesis_supported,
            'total_checks': 3,
            'details': hypothesis_details,
            'verdict': 'SUPPORTED' if hypothesis_supported >= 2 else 'NOT_SUPPORTED',
        },
        'folio_compositions': {f: compositions[f] for f in sorted(common_folios)},
    }

    print()
    print(f"Saving results to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print("\nDone.")
    return results


if __name__ == '__main__':
    main()
