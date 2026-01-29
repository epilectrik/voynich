"""
10_cross_system_summary.py - A-B Cross-System Summary

Parallel comparisons:
- Size: lines/paragraph
- Density: tokens/line
- Header enrichment: RI line-1 concentration (A) vs HT line-1 concentration (B)
- Initiation: Gallows-initial rate
- Section effects

Depends on: 04, 09 scripts (merged profiles)
"""

import json
import sys
from pathlib import Path
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

try:
    from scipy import stats as scipy_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

def cohens_d(group1, group2):
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return None
    var1, var2 = statistics.variance(group1), statistics.variance(group2)
    pooled_std = ((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2)
    pooled_std = pooled_std ** 0.5
    if pooled_std == 0:
        return None
    return (statistics.mean(group1) - statistics.mean(group2)) / pooled_std

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load merged profiles
    with open(results_dir / 'a_paragraph_profiles.json') as f:
        a_data = json.load(f)

    with open(results_dir / 'b_paragraph_profiles.json') as f:
        b_data = json.load(f)

    a_profiles = a_data['profiles']
    b_profiles = b_data['profiles']

    results = {
        'system_counts': {
            'A': len(a_profiles),
            'B': len(b_profiles)
        },
        'comparisons': {},
        'tests': {}
    }

    print("=== A-B CROSS-SYSTEM SUMMARY ===\n")
    print(f"A paragraphs: {len(a_profiles)}")
    print(f"B paragraphs: {len(b_profiles)}")

    # === SIZE COMPARISON ===
    a_lines = [p['size']['line_count'] for p in a_profiles]
    b_lines = [p['size']['line_count'] for p in b_profiles]

    a_tokens = [p['size']['token_count'] for p in a_profiles]
    b_tokens = [p['size']['token_count'] for p in b_profiles]

    results['comparisons']['line_count'] = {
        'A': {'mean': round(statistics.mean(a_lines), 2), 'median': statistics.median(a_lines), 'stdev': round(statistics.stdev(a_lines), 2)},
        'B': {'mean': round(statistics.mean(b_lines), 2), 'median': statistics.median(b_lines), 'stdev': round(statistics.stdev(b_lines), 2)}
    }

    results['comparisons']['token_count'] = {
        'A': {'mean': round(statistics.mean(a_tokens), 2), 'median': statistics.median(a_tokens)},
        'B': {'mean': round(statistics.mean(b_tokens), 2), 'median': statistics.median(b_tokens)}
    }

    print("\n--- SIZE COMPARISON ---")
    print(f"Line count:")
    print(f"  A: mean={results['comparisons']['line_count']['A']['mean']}, median={results['comparisons']['line_count']['A']['median']}")
    print(f"  B: mean={results['comparisons']['line_count']['B']['mean']}, median={results['comparisons']['line_count']['B']['median']}")

    print(f"\nToken count:")
    print(f"  A: mean={results['comparisons']['token_count']['A']['mean']}")
    print(f"  B: mean={results['comparisons']['token_count']['B']['mean']}")

    # Effect sizes
    d_lines = cohens_d(a_lines, b_lines)
    d_tokens = cohens_d(a_tokens, b_tokens)

    if d_lines:
        results['tests']['line_count_cohens_d'] = round(d_lines, 3)
        print(f"\n  Cohen's d (lines): {d_lines:.3f}")
    if d_tokens:
        results['tests']['token_count_cohens_d'] = round(d_tokens, 3)
        print(f"  Cohen's d (tokens): {d_tokens:.3f}")

    # === DENSITY COMPARISON ===
    a_density = [p['size']['tokens_per_line'] for p in a_profiles]
    b_density = [p['size']['tokens_per_line'] for p in b_profiles]

    results['comparisons']['tokens_per_line'] = {
        'A': {'mean': round(statistics.mean(a_density), 2), 'median': round(statistics.median(a_density), 2)},
        'B': {'mean': round(statistics.mean(b_density), 2), 'median': round(statistics.median(b_density), 2)}
    }

    print("\n--- DENSITY COMPARISON ---")
    print(f"Tokens/line:")
    print(f"  A: mean={results['comparisons']['tokens_per_line']['A']['mean']}")
    print(f"  B: mean={results['comparisons']['tokens_per_line']['B']['mean']}")

    # === HEADER ENRICHMENT COMPARISON ===
    # A: RI concentration in line 1
    a_ri_conc = [p['ri_profile']['ri_concentration_line1'] for p in a_profiles
                 if 'ri_profile' in p and p['ri_profile']['ri_concentration_line1'] is not None]

    # B: HT delta (line1 - body)
    b_ht_delta = [p['ht_profile']['ht_delta'] for p in b_profiles if 'ht_profile' in p]
    b_line1_ht = [p['ht_profile']['line1_ht_rate'] for p in b_profiles if 'ht_profile' in p]
    b_body_ht = [p['ht_profile']['body_ht_rate'] for p in b_profiles if 'ht_profile' in p]

    results['comparisons']['header_enrichment'] = {
        'A': {
            'metric': 'RI_concentration_line1',
            'mean': round(statistics.mean(a_ri_conc), 2) if a_ri_conc else None,
            'interpretation': 'line1_RI_rate / body_RI_rate'
        },
        'B': {
            'metric': 'HT_delta',
            'mean': round(statistics.mean(b_ht_delta), 3) if b_ht_delta else None,
            'line1_ht_mean': round(statistics.mean(b_line1_ht), 3) if b_line1_ht else None,
            'body_ht_mean': round(statistics.mean(b_body_ht), 3) if b_body_ht else None,
            'interpretation': 'line1_HT_rate - body_HT_rate'
        }
    }

    print("\n--- HEADER ENRICHMENT COMPARISON ---")
    print(f"A (RI concentration line 1): {results['comparisons']['header_enrichment']['A']['mean']}")
    print(f"B (HT delta): {results['comparisons']['header_enrichment']['B']['mean']}")
    print(f"  B line 1 HT: {results['comparisons']['header_enrichment']['B']['line1_ht_mean']}")
    print(f"  B body HT: {results['comparisons']['header_enrichment']['B']['body_ht_mean']}")

    # === GALLOWS-INITIAL COMPARISON ===
    # For A, we need to calculate gallows-initial from RI profile or directly
    # A paragraphs typically start with gallows (from C841 parallel)
    # B gallows rate from initiation profile

    b_gallows = [1 if p.get('initiation', {}).get('is_gallows_initial', False) else 0 for p in b_profiles]
    b_gallows_rate = sum(b_gallows) / len(b_gallows)

    results['comparisons']['gallows_initial'] = {
        'A': {'note': 'See C841 - historically similar gallows-initial pattern'},
        'B': {'rate': round(b_gallows_rate, 3), 'expected': 0.715}
    }

    print("\n--- GALLOWS-INITIAL COMPARISON ---")
    print(f"B gallows-initial rate: {b_gallows_rate:.3f} (expected 0.715)")
    print("  A: Similar gallows-initial pattern documented (C841)")

    # === STRUCTURAL PARALLEL ===
    print("\n--- STRUCTURAL PARALLEL ---")
    print("A paragraphs: RI header (line 1 concentrated) + PP body")
    print("B paragraphs: HT header (line 1 concentrated) + classified body")
    print(f"\nHeader concentration (line 1 vs body):")
    if a_ri_conc:
        print(f"  A RI: {statistics.mean(a_ri_conc):.2f}x (line 1 RI rate / body RI rate)")
    print(f"  B HT: +{statistics.mean(b_ht_delta):.3f} delta (line 1 - body)")

    # Statistical comparison if scipy available
    if HAS_SCIPY:
        # Mann-Whitney for line counts
        u_stat, p_val = scipy_stats.mannwhitneyu(a_lines, b_lines, alternative='two-sided')
        results['tests']['line_count_mannwhitney'] = {
            'U': round(u_stat, 1),
            'p': round(p_val, 6),
            'significant': bool(p_val < 0.05)
        }
        print(f"\nMann-Whitney (line count A vs B): U={u_stat:.1f}, p={p_val:.6f}")

    # Save
    with open(results_dir / 'cross_system_summary.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved to {results_dir}/cross_system_summary.json")

if __name__ == '__main__':
    main()
