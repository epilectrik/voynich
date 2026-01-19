#!/usr/bin/env python
"""
CAR Phase: Frequency-Controlled Validation

Following expert review, this script runs controlled tests to determine whether
the observed A-B correlation (rho=0.491) is:
  - Infrastructure effect (collapses under control)
  - Genuine domain signal (survives controls)

Tests:
1. CAR-FC1: Partial correlation controlling for overall frequency
2. CAR-FC2: Rank-shuffled null (preserve frequency distribution, break identity)
3. CAR-FC3: Section-stratified analysis (within-section correlations)

Reference:
- CAR-5.1 raw finding: rho=0.491, p<0.0001
- Expert guidance: Population correlation is allowed, entry-level coupling is not
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from scipy import stats
from scipy.stats import spearmanr, pearsonr
import warnings
warnings.filterwarnings('ignore')

from car_data_loader import CARDataLoader, PHASE_DIR


def partial_correlation_pearson(x, y, z):
    """
    Calculate partial correlation between x and y, controlling for z.

    Uses the standard formula for partial correlation.
    Returns Pearson partial correlation.
    """
    if len(x) < 10:
        return 0, 1.0

    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    z = np.array(z, dtype=float)

    rxy, _ = pearsonr(x, y)
    rxz, _ = pearsonr(x, z)
    ryz, _ = pearsonr(y, z)

    # Partial correlation formula
    numerator = rxy - rxz * ryz
    denominator = np.sqrt((1 - rxz**2) * (1 - ryz**2))

    if denominator == 0:
        return 0, 1.0

    r_partial = numerator / denominator

    # Approximate p-value using Fisher transform
    n = len(x)
    t_stat = r_partial * np.sqrt((n - 3) / (1 - r_partial**2)) if abs(r_partial) < 1 else 0
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 3))

    return r_partial, p_value


def test_car_fc1_partial_correlation():
    """
    CAR-FC1: Partial Correlation Analysis

    Question: Does A-B correlation exist beyond what frequency alone predicts?

    Method: Control for token length as proxy for "commonness"
    (Shorter tokens tend to be more common in natural language)
    """
    print("\n" + "=" * 70)
    print("CAR-FC1: Partial Correlation Analysis")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()
    b_data = loader.get_currier_b()

    # Count tokens
    a_counts = Counter(a_data['word'])
    b_counts = Counter(b_data['word'])

    # Shared vocabulary
    shared = sorted(set(a_counts.keys()) & set(b_counts.keys()))
    print(f"\nShared tokens: {len(shared)}")

    # Build arrays
    a_freqs = np.array([a_counts[t] for t in shared])
    b_freqs = np.array([b_counts[t] for t in shared])

    # Use token length as independent control variable
    # (Not derived from A or B frequencies)
    token_lengths = np.array([len(t) for t in shared])

    # Log-transform frequencies
    a_log = np.log1p(a_freqs)
    b_log = np.log1p(b_freqs)

    # Raw correlation (replicate CAR-5.1)
    rho_raw, p_raw = spearmanr(a_freqs, b_freqs)
    r_raw_pearson, _ = pearsonr(a_log, b_log)
    print(f"\nRaw A-B correlation (replication):")
    print(f"  Spearman rho = {rho_raw:.3f}, p = {p_raw:.2e}")
    print(f"  Pearson r (log) = {r_raw_pearson:.3f}")

    # Partial correlation controlling for token length
    r_partial, p_partial = partial_correlation_pearson(a_log, b_log, token_lengths.astype(float))
    print(f"\nPartial correlation (controlling for token length):")
    print(f"  Pearson r_partial = {r_partial:.3f}, p = {p_partial:.2e}")

    # More meaningful test: correlation WITHIN frequency bands
    # This asks: "Among tokens of similar A frequency, is B frequency predictable?"
    print("\n" + "-" * 40)
    print("Within-band correlation analysis:")
    print("-" * 40)

    n_bands = 5
    a_bands = pd.qcut(a_freqs, n_bands, labels=False, duplicates='drop')

    within_band_results = []
    for band_id in sorted(set(a_bands)):
        mask = a_bands == band_id
        if np.sum(mask) >= 20:
            a_band = a_freqs[mask]
            b_band = b_freqs[mask]
            rho_band, p_band = spearmanr(a_band, b_band)
            n_band = np.sum(mask)
            a_range = f"{int(min(a_band))}-{int(max(a_band))}"

            within_band_results.append({
                'band': int(band_id),
                'n': int(n_band),
                'a_range': a_range,
                'rho': float(rho_band),
                'p': float(p_band)
            })

            sig = "*" if p_band < 0.05 else ""
            print(f"  Band {band_id} (A={a_range}, n={n_band}): rho={rho_band:.3f} {sig}")

    # The key diagnostic: if correlation holds within bands, it's genuine
    # If correlation disappears within bands, it's entirely frequency-driven
    significant_bands = sum(1 for r in within_band_results if r['p'] < 0.05 and r['rho'] > 0.1)
    total_bands = len(within_band_results)

    print(f"\nSignificant within-band correlations: {significant_bands}/{total_bands}")

    # Verdict based on within-band analysis
    if significant_bands == 0:
        verdict = "FREQUENCY_DRIVEN"
        interpretation = "No correlation within frequency bands - entirely frequency artifact"
    elif significant_bands < total_bands / 2:
        verdict = "PARTIALLY_FREQUENCY"
        interpretation = "Correlation partially explained by frequency structure"
    else:
        verdict = "BEYOND_FREQUENCY"
        interpretation = "Correlation persists within frequency bands"

    result = {
        'test_id': 'CAR-FC1',
        'test_name': 'Partial Correlation Analysis',
        'n_shared': len(shared),
        'raw_rho': float(rho_raw),
        'raw_p': float(p_raw),
        'raw_pearson': float(r_raw_pearson),
        'partial_r': float(r_partial),
        'partial_p': float(p_partial),
        'within_band_results': within_band_results,
        'significant_bands': significant_bands,
        'total_bands': total_bands,
        'verdict': verdict,
        'interpretation': interpretation
    }

    print(f"\n-> VERDICT: {verdict}")
    print(f"   {interpretation}")

    return result


def test_car_fc2_rank_shuffled_null():
    """
    CAR-FC2: Rank-Shuffled Null

    Question: Does A-B correlation exceed what's expected from frequency alone?

    Method: Shuffle B frequencies within frequency bins (preserve marginal
    distribution but break token identity).
    """
    print("\n" + "=" * 70)
    print("CAR-FC2: Rank-Shuffled Null Test")
    print("=" * 70)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()
    b_data = loader.get_currier_b()

    a_counts = Counter(a_data['word'])
    b_counts = Counter(b_data['word'])

    shared = sorted(set(a_counts.keys()) & set(b_counts.keys()))
    a_freqs = np.array([a_counts[t] for t in shared])
    b_freqs = np.array([b_counts[t] for t in shared])

    # Observed correlation
    rho_observed, _ = spearmanr(a_freqs, b_freqs)
    print(f"\nObserved rho = {rho_observed:.3f}")

    # Create frequency bins
    n_bins = 20
    a_bins = pd.qcut(a_freqs, n_bins, labels=False, duplicates='drop')

    # Rank-shuffled null: shuffle B within A's frequency bins
    print("\nComputing rank-shuffled null (1000 permutations)...")
    null_rhos = []

    for _ in range(1000):
        b_shuffled = b_freqs.copy()

        # Shuffle within each bin
        for bin_id in np.unique(a_bins):
            mask = a_bins == bin_id
            indices = np.where(mask)[0]
            np.random.shuffle(b_shuffled[indices])

        rho_null, _ = spearmanr(a_freqs, b_shuffled)
        null_rhos.append(rho_null)

    null_mean = np.mean(null_rhos)
    null_std = np.std(null_rhos)
    z_score = (rho_observed - null_mean) / null_std if null_std > 0 else 0
    p_value = np.mean([abs(r) >= abs(rho_observed) for r in null_rhos])

    print(f"\nRank-shuffled null distribution:")
    print(f"  Mean rho = {null_mean:.3f}")
    print(f"  Std = {null_std:.3f}")
    print(f"  Observed z-score = {z_score:.2f}")
    print(f"  Permutation p = {p_value:.4f}")

    # Also compute a global shuffle baseline for comparison
    print("\nComputing global shuffle baseline...")
    global_null_rhos = []
    for _ in range(1000):
        b_global_shuffled = np.random.permutation(b_freqs)
        rho_global, _ = spearmanr(a_freqs, b_global_shuffled)
        global_null_rhos.append(rho_global)

    global_mean = np.mean(global_null_rhos)
    global_std = np.std(global_null_rhos)
    global_z = (rho_observed - global_mean) / global_std if global_std > 0 else 0

    print(f"\nGlobal shuffle baseline:")
    print(f"  Mean rho = {global_mean:.3f}")
    print(f"  Std = {global_std:.3f}")
    print(f"  Observed z-score = {global_z:.2f}")

    # If rank-shuffled z-score << global z-score, frequency explains most of it
    if z_score < 2.0:
        verdict = "FREQUENCY_EXPLAINED"
        interpretation = "Rank-shuffled null accounts for observed correlation"
    elif z_score >= 2.0 and z_score < 5.0:
        verdict = "PARTIAL_SIGNAL"
        interpretation = "Some signal beyond frequency structure"
    else:
        verdict = "STRONG_SIGNAL"
        interpretation = "Strong correlation beyond frequency structure"

    result = {
        'test_id': 'CAR-FC2',
        'test_name': 'Rank-Shuffled Null',
        'n_shared': len(shared),
        'observed_rho': float(rho_observed),
        'rank_shuffled_null_mean': float(null_mean),
        'rank_shuffled_null_std': float(null_std),
        'rank_shuffled_z_score': float(z_score),
        'rank_shuffled_p': float(p_value),
        'global_null_mean': float(global_mean),
        'global_null_std': float(global_std),
        'global_z_score': float(global_z),
        'verdict': verdict,
        'interpretation': interpretation
    }

    print(f"\n-> VERDICT: {verdict}")
    print(f"   {interpretation}")
    print(f"   (Rank-shuffled z={z_score:.1f} vs Global z={global_z:.1f})")

    return result


def test_car_fc3_section_stratified():
    """
    CAR-FC3: Section-Stratified Analysis

    Question: Is A-B correlation consistent across manuscript sections?

    If correlation is uniform: Genuine cross-system signal
    If correlation varies wildly: Section composition artifact
    """
    print("\n" + "=" * 70)
    print("CAR-FC3: Section-Stratified Analysis")
    print("=" * 70)

    loader = CARDataLoader().load()

    # Get full data with section info
    full_data = loader.df.copy()

    # Identify A and B tokens by section
    a_sections = ['A', 'C']  # Currier A is in A and C sections
    b_sections = full_data[full_data['language'] == 'B']['section'].unique()

    print(f"\nA sections: {a_sections}")
    print(f"B sections: {list(b_sections)}")

    # Count tokens by section
    section_correlations = {}

    # For each A section, compare to B
    for a_section in a_sections:
        a_section_data = full_data[
            (full_data['section'] == a_section) &
            (full_data['language'].isna() | (full_data['language'] == 'A'))
        ]
        b_all = full_data[full_data['language'] == 'B']

        if len(a_section_data) < 100 or len(b_all) < 100:
            continue

        a_counts = Counter(a_section_data['word'])
        b_counts = Counter(b_all['word'])

        shared = set(a_counts.keys()) & set(b_counts.keys())
        if len(shared) < 50:
            continue

        a_freqs = np.array([a_counts[t] for t in shared])
        b_freqs = np.array([b_counts[t] for t in shared])

        rho, p = spearmanr(a_freqs, b_freqs)
        section_correlations[f"A-sect-{a_section} vs B"] = {
            'rho': float(rho),
            'p': float(p),
            'n_shared': len(shared),
            'n_a_tokens': len(a_section_data),
            'n_b_tokens': len(b_all)
        }

        print(f"\n{a_section} section vs B: rho={rho:.3f}, p={p:.2e}, n_shared={len(shared)}")

    # Also test within B sections
    b_herbal = full_data[(full_data['language'] == 'B') & (full_data['section'] == 'H')]
    b_pharma = full_data[(full_data['language'] == 'B') & (full_data['section'] == 'P')]

    if len(b_herbal) > 100 and len(b_pharma) > 100:
        a_all = full_data[full_data['language'].isna() & full_data['section'].isin(['A', 'C', 'Z'])]
        a_counts = Counter(a_all['word'])

        for b_subset, label in [(b_herbal, 'B-Herbal'), (b_pharma, 'B-Pharma')]:
            b_counts = Counter(b_subset['word'])
            shared = set(a_counts.keys()) & set(b_counts.keys())

            if len(shared) >= 50:
                a_freqs = np.array([a_counts[t] for t in shared])
                b_freqs = np.array([b_counts[t] for t in shared])
                rho, p = spearmanr(a_freqs, b_freqs)

                section_correlations[f"A-all vs {label}"] = {
                    'rho': float(rho),
                    'p': float(p),
                    'n_shared': len(shared)
                }
                print(f"\nA-all vs {label}: rho={rho:.3f}, p={p:.2e}, n_shared={len(shared)}")

    # Analyze consistency
    rhos = [v['rho'] for v in section_correlations.values() if not np.isnan(v['rho'])]

    if len(rhos) >= 2:
        rho_mean = np.mean(rhos)
        rho_std = np.std(rhos)
        rho_range = max(rhos) - min(rhos)
        cv = rho_std / abs(rho_mean) if rho_mean != 0 else float('inf')

        print(f"\nCorrelation consistency:")
        print(f"  Mean rho = {rho_mean:.3f}")
        print(f"  Std = {rho_std:.3f}")
        print(f"  Range = {rho_range:.3f}")
        print(f"  CV = {cv:.2f}")

        # If CV < 0.3 and all correlations have same sign, consistent
        if cv < 0.3 and all(r > 0 for r in rhos):
            verdict = "CONSISTENT"
            interpretation = "Correlation stable across sections"
        elif cv < 0.5:
            verdict = "MODERATELY_CONSISTENT"
            interpretation = "Some variation but pattern holds"
        else:
            verdict = "INCONSISTENT"
            interpretation = "Correlation varies substantially by section"
    else:
        rho_mean = rhos[0] if rhos else 0
        rho_std = 0
        rho_range = 0
        cv = 0
        verdict = "INSUFFICIENT_SECTIONS"
        interpretation = "Not enough sections to assess consistency"

    result = {
        'test_id': 'CAR-FC3',
        'test_name': 'Section-Stratified Analysis',
        'section_correlations': section_correlations,
        'rho_mean': float(rho_mean),
        'rho_std': float(rho_std),
        'rho_range': float(rho_range),
        'coefficient_of_variation': float(cv),
        'verdict': verdict,
        'interpretation': interpretation
    }

    print(f"\n-> VERDICT: {verdict}")
    print(f"   {interpretation}")

    return result


def run_frequency_controlled():
    """Run all frequency-controlled validation tests."""
    print("\n" + "=" * 80)
    print("CAR FREQUENCY-CONTROLLED VALIDATION")
    print("=" * 80)
    print("\nPurpose: Determine if CAR-O1 (A-B correlation) is:")
    print("  - Infrastructure effect (common tokens dominate)")
    print("  - Genuine domain signal (shared apparatus vocabulary)")
    print("\nBoth outcomes are architecturally consistent with the model.")

    results = {
        'phase': 'CAR-FC',
        'name': 'Frequency-Controlled Validation',
        'purpose': 'Distinguish infrastructure effect from domain signal',
        'tests': {}
    }

    # Run tests
    results['tests']['CAR-FC1'] = test_car_fc1_partial_correlation()
    results['tests']['CAR-FC2'] = test_car_fc2_rank_shuffled_null()
    results['tests']['CAR-FC3'] = test_car_fc3_section_stratified()

    # Summary
    print("\n" + "=" * 80)
    print("FREQUENCY-CONTROLLED VALIDATION SUMMARY")
    print("=" * 80)

    verdicts = [t['verdict'] for t in results['tests'].values()]

    print("\nTest Results:")
    for test_id, test in results['tests'].items():
        print(f"  {test_id}: {test['verdict']} - {test['interpretation']}")

    # Overall interpretation
    # FC2 (rank-shuffled) is the most definitive test
    fc2_verdict = results['tests']['CAR-FC2']['verdict']
    fc1_verdict = results['tests']['CAR-FC1']['verdict']
    fc3_verdict = results['tests']['CAR-FC3']['verdict']

    # If rank-shuffled null perfectly explains correlation, it's frequency-driven
    if fc2_verdict == "FREQUENCY_EXPLAINED":
        if fc1_verdict == "FREQUENCY_DRIVEN":
            overall = "FREQUENCY_ARTIFACT"
            summary = "A-B correlation is entirely explained by frequency structure (infrastructure effect)"
        else:
            overall = "FREQUENCY_DOMINATED"
            summary = "A-B correlation primarily reflects frequency structure"
    elif fc2_verdict == "STRONG_SIGNAL":
        overall = "GENUINE_DOMAIN_SIGNAL"
        summary = "A-B correlation reflects genuine token-level co-usage beyond frequency"
    else:
        overall = "MIXED_SIGNAL"
        summary = "Both frequency structure and domain effects contribute"

    results['overall_verdict'] = overall
    results['summary'] = summary

    print(f"\n-> OVERALL VERDICT: {overall}")
    print(f"   {summary}")

    # Architectural note
    print("\n" + "-" * 40)
    print("ARCHITECTURAL NOTE:")
    print("-" * 40)
    print("Regardless of verdict, the A-B correlation does NOT:")
    print("  - Violate C384 (no entry-level coupling)")
    print("  - Contradict C451 (HT stratification)")
    print("  - Imply per-token procedural meaning")
    print("\nBoth systems describe the same apparatus space.")
    print("Population-level vocabulary correlation is expected.")

    # Save results
    output_file = PHASE_DIR / 'car_frequency_controlled_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_frequency_controlled()
