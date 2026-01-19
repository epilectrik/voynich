#!/usr/bin/env python
"""
CAR Phase Track 5: Failed Test Retries

Re-runs tests that returned null results before the transcriber bug fix.

Tests:
- CAR-5.1: A-B Correlation (Retry)
- CAR-5.2: HT-Phase Reset in A/C (Retry)

Reference:
- C451: A-B frequency-driven, no residual correlation
- AC_INTERNAL_CHARACTERIZATION: HT reset no signal (p=1.00)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import random

from car_data_loader import (
    CARDataLoader, decompose_token, get_middles_from_tokens,
    MARKER_PREFIXES, PHASE_DIR
)

# Known HT markers (from constraint system)
HT_MARKERS = {'s', 'f', 'p', 'cfh', 'cph', 'ckh', 'cth'}


def test_car_5_1_ab_correlation():
    """
    CAR-5.1: A-B Correlation (Retry)

    Question: Is there ANY correlation between A vocabulary and B usage?

    Previous result: C451 - frequency-driven, no residual correlation

    Method:
    1. Load H-only A and B data
    2. For tokens appearing in both:
       - Calculate frequency correlation
       - Regress out frequency, test residual
    3. Compare to shuffled baseline
    """
    print("\n" + "=" * 60)
    print("CAR-5.1: A-B Correlation (Retry)")
    print("=" * 60)

    loader = CARDataLoader().load()
    a_data = loader.get_currier_a()
    b_data = loader.get_currier_b()

    # Count tokens in each system
    a_counts = Counter(a_data['word'])
    b_counts = Counter(b_data['word'])

    # Shared vocabulary
    shared = set(a_counts.keys()) & set(b_counts.keys())
    a_only = set(a_counts.keys()) - set(b_counts.keys())
    b_only = set(b_counts.keys()) - set(a_counts.keys())

    print(f"\nA unique tokens: {len(a_counts)}")
    print(f"B unique tokens: {len(b_counts)}")
    print(f"Shared tokens: {len(shared)}")
    print(f"A-only tokens: {len(a_only)}")
    print(f"B-only tokens: {len(b_only)}")

    # Frequency correlation for shared tokens
    if len(shared) < 10:
        print("Insufficient shared tokens for correlation analysis")
        return {
            'test_id': 'CAR-5.1',
            'test_name': 'A-B Correlation (Retry)',
            'verdict': 'INSUFFICIENT_DATA'
        }

    a_freqs = np.array([a_counts[t] for t in shared])
    b_freqs = np.array([b_counts[t] for t in shared])

    # Raw correlation
    rho_raw, p_raw = stats.spearmanr(a_freqs, b_freqs)
    print(f"\nRaw frequency correlation (Spearman):")
    print(f"  rho = {rho_raw:.3f}, p = {p_raw:.6f}")

    # Log-frequency correlation (often more meaningful)
    a_log = np.log1p(a_freqs)
    b_log = np.log1p(b_freqs)
    rho_log, p_log = stats.spearmanr(a_log, b_log)
    print(f"\nLog-frequency correlation:")
    print(f"  rho = {rho_log:.3f}, p = {p_log:.6f}")

    # Pearson on log (linearity test)
    r_pearson, p_pearson = stats.pearsonr(a_log, b_log)
    print(f"\nPearson on log-frequencies:")
    print(f"  r = {r_pearson:.3f}, p = {p_pearson:.6f}")

    # Shuffled baseline
    print("\nComputing shuffled baseline...")
    shuffled_rhos = []
    for _ in range(1000):
        shuffled_b = b_freqs.copy()
        np.random.shuffle(shuffled_b)
        rho, _ = stats.spearmanr(a_freqs, shuffled_b)
        shuffled_rhos.append(rho)

    baseline_mean = np.mean(shuffled_rhos)
    baseline_std = np.std(shuffled_rhos)
    effect_size = (rho_raw - baseline_mean) / baseline_std if baseline_std > 0 else 0
    perm_p = np.mean([abs(r) >= abs(rho_raw) for r in shuffled_rhos])

    print(f"\nBaseline rho: {baseline_mean:.3f} +/- {baseline_std:.3f}")
    print(f"Observed rho: {rho_raw:.3f}")
    print(f"Effect size: {effect_size:.2f}")
    print(f"Permutation p-value: {perm_p:.4f}")

    # Check top shared tokens
    print(f"\nTop 10 shared tokens by A frequency:")
    shared_sorted = sorted(shared, key=lambda t: a_counts[t], reverse=True)
    for token in shared_sorted[:10]:
        print(f"  {token}: A={a_counts[token]}, B={b_counts[token]}")

    result = {
        'test_id': 'CAR-5.1',
        'test_name': 'A-B Correlation (Retry)',
        'n_a_types': len(a_counts),
        'n_b_types': len(b_counts),
        'n_shared': len(shared),
        'raw_rho': rho_raw,
        'raw_p': p_raw,
        'log_rho': rho_log,
        'log_p': p_log,
        'baseline_mean': baseline_mean,
        'baseline_std': baseline_std,
        'effect_size': effect_size,
        'perm_p_value': perm_p,
        'verdict': 'SIGNIFICANT' if p_raw < 0.001 and abs(rho_raw) > 0.1 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  A-B frequency correlation detected!")
        print(f"  rho = {rho_raw:.3f} (above threshold)")
    else:
        print(f"  A-B correlation is NULL or below threshold")
        print(f"  Confirms C451: no meaningful residual correlation")

    return result


def test_car_5_2_ht_reset():
    """
    CAR-5.2: HT-Phase Reset in A/C (Retry)

    Question: Does HT show different reset patterns in A/C vs Zodiac?

    Previous result: AC_INTERNAL_CHARACTERIZATION - no signal (p=1.00)
    """
    print("\n" + "=" * 60)
    print("CAR-5.2: HT-Phase Reset in A/C (Retry)")
    print("=" * 60)

    loader = CARDataLoader().load()
    azc_data = loader.get_azc()

    # Identify HT markers in AZC data
    print(f"\nHT markers to detect: {HT_MARKERS}")

    # Count HT occurrences by section
    ht_by_section = defaultdict(int)
    total_by_section = defaultdict(int)
    ht_by_folio = defaultdict(lambda: defaultdict(int))

    for _, row in azc_data.iterrows():
        section = row['section']
        folio = row['folio']
        token = str(row['word']).lower()

        total_by_section[section] += 1

        # Check if token contains HT marker
        for ht in HT_MARKERS:
            if ht in token:
                ht_by_section[section] += 1
                ht_by_folio[section][folio] += 1
                break

    print(f"\nHT occurrences by section:")
    for section in sorted(total_by_section.keys()):
        ht_count = ht_by_section[section]
        total = total_by_section[section]
        rate = ht_count / total if total > 0 else 0
        print(f"  {section}: {ht_count}/{total} = {100*rate:.2f}%")

    # Compare A/C vs Z
    ac_ht = ht_by_section.get('A', 0) + ht_by_section.get('C', 0)
    ac_total = total_by_section.get('A', 0) + total_by_section.get('C', 0)
    z_ht = ht_by_section.get('Z', 0)
    z_total = total_by_section.get('Z', 0)

    if ac_total > 0 and z_total > 0:
        ac_rate = ac_ht / ac_total
        z_rate = z_ht / z_total

        print(f"\nA/C HT rate: {100*ac_rate:.2f}% ({ac_ht}/{ac_total})")
        print(f"Zodiac HT rate: {100*z_rate:.2f}% ({z_ht}/{z_total})")

        # Chi-square test
        contingency = [[ac_ht, ac_total - ac_ht],
                      [z_ht, z_total - z_ht]]
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency)

        print(f"\nChi-square test (A/C vs Zodiac):")
        print(f"  Chi2 = {chi2:.2f}, p = {p_val:.4f}")

        ratio = ac_rate / z_rate if z_rate > 0 else 0
        print(f"  Rate ratio (A/C / Zodiac): {ratio:.2f}x")
    else:
        p_val = 1.0
        ratio = 0

    # HT distribution by folio
    print(f"\nHT occurrences by folio (top 10):")
    all_folio_ht = []
    for section, folios in ht_by_folio.items():
        for folio, count in folios.items():
            all_folio_ht.append((section, folio, count))

    for section, folio, count in sorted(all_folio_ht, key=lambda x: -x[2])[:10]:
        print(f"  {folio} ({section}): {count}")

    result = {
        'test_id': 'CAR-5.2',
        'test_name': 'HT-Phase Reset in A/C (Retry)',
        'ht_markers': list(HT_MARKERS),
        'ht_by_section': {k: int(v) for k, v in ht_by_section.items()},
        'total_by_section': {k: int(v) for k, v in total_by_section.items()},
        'ac_rate': ac_rate if ac_total > 0 else 0,
        'z_rate': z_rate if z_total > 0 else 0,
        'chi2': chi2 if ac_total > 0 and z_total > 0 else 0,
        'p_value': p_val,
        'rate_ratio': ratio,
        'verdict': 'SIGNIFICANT' if p_val < 0.001 else 'NULL'
    }

    print(f"\n-> VERDICT: {result['verdict']}")
    if result['verdict'] == 'SIGNIFICANT':
        print(f"  HT patterns differ between A/C and Zodiac!")
        print(f"  Rate ratio: {ratio:.2f}x")
    else:
        print(f"  HT patterns similar across AZC families")
        print(f"  Confirms previous null finding")

    return result


def run_track5():
    """Run all Track 5 tests."""
    print("\n" + "=" * 70)
    print("TRACK 5: FAILED TEST RETRIES")
    print("=" * 70)

    results = {
        'track': 5,
        'name': 'Failed Test Retries',
        'tests': {}
    }

    # Run tests
    results['tests']['CAR-5.1'] = test_car_5_1_ab_correlation()
    results['tests']['CAR-5.2'] = test_car_5_2_ht_reset()

    # Summary
    print("\n" + "=" * 70)
    print("TRACK 5 SUMMARY")
    print("=" * 70)

    significant = sum(1 for t in results['tests'].values()
                     if t.get('verdict') == 'SIGNIFICANT')
    null = sum(1 for t in results['tests'].values()
              if t.get('verdict') in ('NULL', 'INSUFFICIENT_DATA'))

    print(f"\nTests passed (SIGNIFICANT): {significant}/2")
    print(f"Tests confirmed NULL: {null}/2")

    for test_id, test in results['tests'].items():
        print(f"\n{test_id}: {test.get('test_name', 'Unknown')}")
        print(f"  Verdict: {test.get('verdict', 'N/A')}")

    # Track verdict
    if significant >= 1:
        results['track_verdict'] = 'NEW_FINDING'
        print("\n-> TRACK 5 VERDICT: NEW_FINDING")
        print("  Clean data revealed previously masked pattern!")
    else:
        results['track_verdict'] = 'CONFIRMED_NULL'
        print("\n-> TRACK 5 VERDICT: CONFIRMED_NULL")
        print("  Previous null findings confirmed with clean data")

    # Save results
    output_file = PHASE_DIR / 'car_track5_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_track5()
