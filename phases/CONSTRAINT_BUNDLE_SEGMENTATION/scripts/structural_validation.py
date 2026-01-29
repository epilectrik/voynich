"""
CONSTRAINT_BUNDLE_SEGMENTATION - Script 1: Structural Validation
Tests T1.1-T1.5 (C694-C698)

Gate: 4/5 pass to proceed to Phase 2.

Tests:
  T1.1: RI Placement Non-Random (C694)
  T1.2: PP-Only Runs Longer Than Chance (C695)
  T1.3: RI Line-Final Preference (C696)
  T1.4: PREFIX Clustering Within Lines (C697)
  T1.5: Bundle Sizes Match C424 Clusters (C698)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import Counter
from scipy import stats as scipy_stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from bundle_segmentation import segment_all_folios, PROJECT_ROOT as PROJ

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'

print("=" * 70)
print("CONSTRAINT_BUNDLE_SEGMENTATION - Script 1: Structural Validation")
print("=" * 70)

# ── Segment ──
bundles, ri_lines, metadata, shared = segment_all_folios(verbose=True)

tx = shared['tx']
morph = shared['morph']
analyzer = shared['analyzer']

folio_stats = metadata['folio_stats']
folios = sorted(folio_stats.keys())

results = {
    'metadata': {
        'phase': 'CONSTRAINT_BUNDLE_SEGMENTATION',
        'script': 'structural_validation.py',
        'tests': 'T1.1-T1.5 (C694-C698)',
        'segmentation': {
            'total_folios': metadata['total_folios'],
            'total_bundles': metadata['total_bundles'],
            'total_ri_lines': metadata['total_ri_lines'],
            'total_pp_pure_lines': metadata['total_pp_pure_lines'],
            'total_lines': metadata['total_lines'],
        },
    },
}

pass_count = 0

# ════════════════════════════════════════════════════════════════
# T1.1: RI Placement Non-Random (C694)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T1.1: RI PLACEMENT NON-RANDOM (C694)")
print("=" * 70)

# For each folio: build binary sequence (0=PP-pure, 1=RI-bearing)
# Test with Wald-Wolfowitz runs test + KS on inter-RI gap lengths

folio_ks_pvals = []
folio_runs_pvals = []
gap_lengths_all = []

for fol in folios:
    records = analyzer.analyze_folio(fol)
    if len(records) < 5:
        continue

    binary = [1 if rec.ri_count > 0 else 0 for rec in records]
    n_ri = sum(binary)
    n_pp = len(binary) - n_ri

    if n_ri < 2 or n_pp < 2:
        continue

    # Inter-RI gap lengths (PP-pure lines between consecutive RI lines)
    ri_positions = [i for i, b in enumerate(binary) if b == 1]
    gaps = []
    for i in range(1, len(ri_positions)):
        gap = ri_positions[i] - ri_positions[i - 1] - 1
        gaps.append(gap)
    if gaps:
        gap_lengths_all.extend(gaps)

    # KS test: gaps vs geometric(p) where p = n_ri / len(binary)
    if len(gaps) >= 5:
        p_ri = n_ri / len(binary)
        # Geometric distribution: P(gap=k) = (1-p_ri)^k * p_ri for k=0,1,2,...
        ks_stat, ks_p = scipy_stats.kstest(gaps, 'geom', args=(p_ri,))
        folio_ks_pvals.append(ks_p)

    # Wald-Wolfowitz runs test
    runs = 1
    for i in range(1, len(binary)):
        if binary[i] != binary[i - 1]:
            runs += 1

    n = len(binary)
    n1 = n_ri
    n2 = n_pp
    # Expected runs and variance under null
    expected_runs = 1 + (2 * n1 * n2) / n
    if n > 1:
        var_runs = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n * n * (n - 1))
        if var_runs > 0:
            z = (runs - expected_runs) / np.sqrt(var_runs)
            p_runs = 2 * scipy_stats.norm.sf(abs(z))
            folio_runs_pvals.append(p_runs)

# Fisher's combined p-value for KS tests
if folio_ks_pvals:
    # Fisher's method: -2 * sum(ln(p)) ~ chi2(2k)
    ks_stat_fisher = -2 * sum(np.log(max(p, 1e-300)) for p in folio_ks_pvals)
    ks_df = 2 * len(folio_ks_pvals)
    ks_combined_p = scipy_stats.chi2.sf(ks_stat_fisher, ks_df)
else:
    ks_combined_p = 1.0

if folio_runs_pvals:
    runs_stat_fisher = -2 * sum(np.log(max(p, 1e-300)) for p in folio_runs_pvals)
    runs_df = 2 * len(folio_runs_pvals)
    runs_combined_p = scipy_stats.chi2.sf(runs_stat_fisher, runs_df)
else:
    runs_combined_p = 1.0

# Also: aggregate KS on all gap lengths
agg_gap_arr = np.array(gap_lengths_all)
overall_p_ri = metadata['total_ri_lines'] / metadata['total_lines'] if metadata['total_lines'] > 0 else 0.5
if len(agg_gap_arr) >= 10:
    agg_ks_stat, agg_ks_p = scipy_stats.kstest(agg_gap_arr, 'geom', args=(overall_p_ri,))
else:
    agg_ks_stat, agg_ks_p = 0, 1.0

t11_pass = ks_combined_p < 0.01

print(f"\n  Folios with KS tests: {len(folio_ks_pvals)}")
print(f"  Folios with runs tests: {len(folio_runs_pvals)}")
print(f"  Total inter-RI gaps: {len(gap_lengths_all)}")
print(f"  Mean gap length: {np.mean(agg_gap_arr):.2f}" if len(agg_gap_arr) > 0 else "  No gaps")
print(f"  Overall RI fraction: {overall_p_ri:.3f}")
print(f"  Fisher combined KS p: {ks_combined_p:.2e}")
print(f"  Fisher combined runs p: {runs_combined_p:.2e}")
print(f"  Aggregate KS (all gaps): stat={agg_ks_stat:.4f}, p={agg_ks_p:.2e}")
print(f"\n  PASS (KS p < 0.01): {t11_pass}")

if t11_pass:
    pass_count += 1

results['T1_1_ri_placement'] = {
    'constraint': 'C694',
    'n_folios_ks': len(folio_ks_pvals),
    'n_folios_runs': len(folio_runs_pvals),
    'total_gaps': len(gap_lengths_all),
    'mean_gap': round(float(np.mean(agg_gap_arr)), 3) if len(agg_gap_arr) > 0 else None,
    'overall_ri_fraction': round(overall_p_ri, 4),
    'fisher_ks_combined_p': float(ks_combined_p),
    'fisher_runs_combined_p': float(runs_combined_p),
    'aggregate_ks_stat': round(float(agg_ks_stat), 5),
    'aggregate_ks_p': float(agg_ks_p),
    'pass': t11_pass,
}


# ════════════════════════════════════════════════════════════════
# T1.2: PP-Only Runs Longer Than Chance (C695)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T1.2: PP-ONLY RUNS LONGER THAN CHANCE (C695)")
print("=" * 70)

bundle_sizes = [b.size for b in bundles]
size_arr = np.array(bundle_sizes)

# Null: geometric(1-q) where q = fraction of PP-pure lines
q = metadata['total_pp_pure_lines'] / metadata['total_lines'] if metadata['total_lines'] > 0 else 0.5
# Under null, run length ~ geometric(1-q): P(run=k) = q^(k-1) * (1-q) for k=1,2,...
# scipy.stats.geom uses P(X=k) = (1-p)^(k-1) * p, so p = 1-q

null_p = 1 - q  # probability of "stop" (hitting RI line)

if len(size_arr) >= 10:
    ks_stat, ks_p = scipy_stats.kstest(size_arr, 'geom', args=(null_p,))
else:
    ks_stat, ks_p = 0, 1.0

# Direction check: are observed runs LONGER than expected?
expected_mean = 1 / null_p if null_p > 0 else float('inf')
observed_mean = float(np.mean(size_arr))

# Also check excess of long runs (size >= 4)
n_long_obs = int(np.sum(size_arr >= 4))
# Under geometric(null_p), P(X>=4) = q^3
p_long_null = q ** 3 if q < 1 else 1.0
n_long_expected = len(size_arr) * p_long_null

# One-sided: more long runs than expected
if n_long_expected > 0 and len(size_arr) > 0:
    # Binomial test: observed long runs vs expected
    binom_p = scipy_stats.binom_test(n_long_obs, len(size_arr), p_long_null, alternative='greater') if hasattr(scipy_stats, 'binom_test') else scipy_stats.binomtest(n_long_obs, len(size_arr), p_long_null, alternative='greater').pvalue
else:
    binom_p = 1.0

t12_pass = ks_p < 0.01

print(f"\n  Bundle count: {len(size_arr)}")
print(f"  PP-pure fraction (q): {q:.3f}")
print(f"  Null stop probability (1-q): {null_p:.3f}")
print(f"  Expected mean run length: {expected_mean:.2f}")
print(f"  Observed mean run length: {observed_mean:.2f}")
print(f"  Size distribution:")

size_dist = Counter(int(s) for s in size_arr)
for k in sorted(size_dist.keys())[:15]:
    print(f"    size {k}: {size_dist[k]}")

print(f"  Long runs (>=4): {n_long_obs} observed, {n_long_expected:.1f} expected")
print(f"  KS stat: {ks_stat:.4f}, p: {ks_p:.2e}")
print(f"  Binomial p (excess long runs): {binom_p:.2e}")
print(f"\n  PASS (KS p < 0.01): {t12_pass}")

if t12_pass:
    pass_count += 1

results['T1_2_pp_run_length'] = {
    'constraint': 'C695',
    'n_bundles': len(size_arr),
    'pp_pure_fraction': round(q, 4),
    'null_stop_prob': round(null_p, 4),
    'expected_mean_run': round(expected_mean, 3),
    'observed_mean_run': round(observed_mean, 3),
    'size_distribution': {str(k): size_dist[k] for k in sorted(size_dist.keys())},
    'long_runs_observed': n_long_obs,
    'long_runs_expected': round(n_long_expected, 2),
    'ks_stat': round(float(ks_stat), 5),
    'ks_p': float(ks_p),
    'binom_excess_long_p': float(binom_p),
    'pass': t12_pass,
}


# ════════════════════════════════════════════════════════════════
# T1.3: RI Line-Final Preference (C696)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T1.3: RI LINE-FINAL PREFERENCE (C696)")
print("=" * 70)

ri_line_final = 0
ri_total = 0
all_line_final = 0
all_total = 0

for fol in folios:
    records = analyzer.analyze_folio(fol)
    for rec in records:
        if not rec.tokens:
            continue
        n_tok = len(rec.tokens)
        all_total += n_tok
        all_line_final += 1  # last position per line

        for i, t in enumerate(rec.tokens):
            if t.is_ri:
                ri_total += 1
                if i == n_tok - 1:
                    ri_line_final += 1

# Baseline: fraction of all tokens that are line-final
baseline_final_rate = all_line_final / all_total if all_total > 0 else 0
ri_final_rate = ri_line_final / ri_total if ri_total > 0 else 0
ratio = ri_final_rate / baseline_final_rate if baseline_final_rate > 0 else 0

# Chi-squared test
# Observed: ri_line_final RI tokens are line-final, (ri_total - ri_line_final) are not
# Expected under baseline rate
expected_ri_final = ri_total * baseline_final_rate
expected_ri_nonfinal = ri_total * (1 - baseline_final_rate)
observed = np.array([ri_line_final, ri_total - ri_line_final])
expected = np.array([expected_ri_final, expected_ri_nonfinal])
if expected_ri_final > 0 and expected_ri_nonfinal > 0:
    chi2 = float(np.sum((observed - expected) ** 2 / expected))
    chi2_p = scipy_stats.chi2.sf(chi2, 1)
else:
    chi2, chi2_p = 0, 1.0

t13_pass = ratio > 1.5 and chi2_p < 0.001

print(f"\n  Total RI tokens: {ri_total}")
print(f"  RI tokens at line-final: {ri_line_final}")
print(f"  RI line-final rate: {ri_final_rate:.4f}")
print(f"  Baseline line-final rate: {baseline_final_rate:.4f}")
print(f"  Ratio: {ratio:.2f}x")
print(f"  Chi2: {chi2:.2f}, p: {chi2_p:.2e}")
print(f"  [C498 reference: 1.76x]")
print(f"\n  PASS (ratio > 1.5x AND p < 0.001): {t13_pass}")

if t13_pass:
    pass_count += 1

results['T1_3_ri_line_final'] = {
    'constraint': 'C696',
    'ri_total': ri_total,
    'ri_line_final': ri_line_final,
    'ri_final_rate': round(ri_final_rate, 5),
    'baseline_final_rate': round(baseline_final_rate, 5),
    'ratio': round(ratio, 3),
    'chi2': round(chi2, 3),
    'chi2_p': float(chi2_p),
    'c498_reference': 1.76,
    'pass': t13_pass,
}


# ════════════════════════════════════════════════════════════════
# T1.4: PREFIX Clustering Within Lines (C697)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T1.4: PREFIX CLUSTERING WITHIN LINES (C697)")
print("=" * 70)

# For each A line: Shannon entropy of PREFIX distribution
# Compare to 1000 shuffled permutations (tokens shuffled across lines within folio)

def shannon_entropy(counter):
    """Shannon entropy in bits from a Counter."""
    total = sum(counter.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counter.values() if c > 0]
    return -sum(p * np.log2(p) for p in probs)


# Pre-compute per-folio prefix data
folio_prefix_data = {}  # folio -> list of (line_prefixes, n_tokens)
folio_all_prefixes = {}  # folio -> list of all prefixes (for shuffling)

for fol in folios:
    records = analyzer.analyze_folio(fol)
    line_data = []
    all_pref = []
    for rec in records:
        prefixes = []
        for t in rec.tokens:
            p = t.prefix
            if p:
                prefixes.append(p)
        line_data.append(prefixes)
        all_pref.extend(prefixes)
    if all_pref:
        folio_prefix_data[fol] = line_data
        folio_all_prefixes[fol] = all_pref

# Observed mean entropy across all lines
observed_entropies = []
for fol, line_data in folio_prefix_data.items():
    for prefixes in line_data:
        if prefixes:
            cnt = Counter(prefixes)
            observed_entropies.append(shannon_entropy(cnt))

obs_mean_entropy = np.mean(observed_entropies) if observed_entropies else 0

# Permutation test: shuffle tokens across lines within folio
N_PERMS = 1000
rng = np.random.RandomState(42)
shuffled_means = []

for perm_i in range(N_PERMS):
    perm_entropies = []
    for fol, line_data in folio_prefix_data.items():
        all_pref = list(folio_all_prefixes[fol])
        rng.shuffle(all_pref)

        # Redistribute to lines (same lengths)
        idx = 0
        for prefixes in line_data:
            n = len(prefixes)
            if n > 0:
                shuffled_line = all_pref[idx:idx + n]
                cnt = Counter(shuffled_line)
                perm_entropies.append(shannon_entropy(cnt))
                idx += n

    if perm_entropies:
        shuffled_means.append(np.mean(perm_entropies))

shuffled_arr = np.array(shuffled_means)
# p-value: fraction of shuffled means <= observed (one-sided: observed should be lower)
p_prefix = np.mean(shuffled_arr <= obs_mean_entropy) if len(shuffled_arr) > 0 else 1.0

t14_pass = obs_mean_entropy < np.mean(shuffled_arr) and p_prefix < 0.001

print(f"\n  Lines with prefixes: {len(observed_entropies)}")
print(f"  Observed mean PREFIX entropy: {obs_mean_entropy:.4f}")
print(f"  Shuffled mean PREFIX entropy: {np.mean(shuffled_arr):.4f} (+/- {np.std(shuffled_arr):.4f})")
print(f"  p-value (observed < shuffled): {p_prefix:.4e}")
print(f"  Effect: {'lower' if obs_mean_entropy < np.mean(shuffled_arr) else 'higher'} entropy = {'more' if obs_mean_entropy < np.mean(shuffled_arr) else 'less'} clustering")
print(f"\n  PASS (observed < shuffled, p < 0.001): {t14_pass}")

if t14_pass:
    pass_count += 1

results['T1_4_prefix_clustering'] = {
    'constraint': 'C697',
    'n_lines_with_prefixes': len(observed_entropies),
    'observed_mean_entropy': round(float(obs_mean_entropy), 5),
    'shuffled_mean_entropy': round(float(np.mean(shuffled_arr)), 5),
    'shuffled_std': round(float(np.std(shuffled_arr)), 5),
    'p_value': float(p_prefix),
    'direction': 'lower' if obs_mean_entropy < np.mean(shuffled_arr) else 'higher',
    'n_permutations': N_PERMS,
    'pass': t14_pass,
}


# ════════════════════════════════════════════════════════════════
# T1.5: Bundle Sizes Match C424 Clusters (C698)
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("T1.5: BUNDLE SIZES MATCH C424 CLUSTERS (C698)")
print("=" * 70)

# C424 published distribution: {2:141, 3:87, 4:34, 5+:26}
# Total clusters: 288, mean size: 2.95, range: 2-20
# These are ADJACENCY clusters (runs of repeated MIDDLEs), not identical to bundles
# but should have similar distributional shape if bundles are the same structure

# Reconstruct C424 raw data from published distribution
# 2:141, 3:87, 4:34, 5+:26
# For 5+, we need to estimate. Mean overall = 2.95
# Total entries = 141*2 + 87*3 + 34*4 + 26*x = 288 * 2.95 = 849.6
# 282 + 261 + 136 + 26x = 849.6 -> 26x = 170.6 -> x = 6.56
# So 5+ mean ~ 6.6. Approximate as uniform spread: some 5s, 6s, 7s, etc.
# For KS, expand with best estimate
c424_sizes = []
c424_sizes.extend([2] * 141)
c424_sizes.extend([3] * 87)
c424_sizes.extend([4] * 34)
# Distribute 26 clusters across 5-20 range, weighted toward lower values
# Use exponential-like: more 5s, fewer 20s, maintaining mean ~6.6
c424_5plus = []
remaining = 26
for s in range(5, 21):
    if remaining <= 0:
        break
    weight = max(1, int(remaining * 0.35))
    count = min(weight, remaining)
    c424_5plus.extend([s] * count)
    remaining -= count
if remaining > 0:
    c424_5plus.extend([5] * remaining)
c424_sizes.extend(c424_5plus)
c424_arr = np.array(c424_sizes)

# Bundle sizes (only bundles of size >= 2 to match C424 which counts clusters of 2+)
bundle_sizes_2plus = size_arr[size_arr >= 2]

if len(bundle_sizes_2plus) >= 5 and len(c424_arr) >= 5:
    ks_stat_c424, ks_p_c424 = scipy_stats.ks_2samp(bundle_sizes_2plus, c424_arr)
else:
    ks_stat_c424, ks_p_c424 = 0, 1.0

t15_pass = ks_p_c424 > 0.05  # Same distribution

# Also compare summary stats
bundle_2plus_mean = float(np.mean(bundle_sizes_2plus)) if len(bundle_sizes_2plus) > 0 else 0
c424_mean = float(np.mean(c424_arr))

print(f"\n  C424 clusters (reconstructed): n={len(c424_arr)}, mean={c424_mean:.2f}")
print(f"  Bundle sizes (>=2): n={len(bundle_sizes_2plus)}, mean={bundle_2plus_mean:.2f}")
print(f"  All bundles: n={len(size_arr)}, mean={float(np.mean(size_arr)):.2f}")

print(f"\n  Bundle size distribution (all):")
for k in sorted(size_dist.keys())[:12]:
    print(f"    size {k}: {size_dist[k]}")

print(f"\n  C424 reference: mean=2.95, range=2-20")
print(f"  KS stat (2+ bundles vs C424): {ks_stat_c424:.4f}, p: {ks_p_c424:.4f}")
print(f"\n  PASS (KS p > 0.05, same distribution): {t15_pass}")

if t15_pass:
    pass_count += 1

results['T1_5_bundle_c424_match'] = {
    'constraint': 'C698',
    'c424_n': len(c424_arr),
    'c424_mean': round(c424_mean, 3),
    'c424_published_mean': 2.95,
    'bundle_2plus_n': int(len(bundle_sizes_2plus)),
    'bundle_2plus_mean': round(bundle_2plus_mean, 3),
    'bundle_all_mean': round(float(np.mean(size_arr)), 3),
    'ks_stat': round(float(ks_stat_c424), 5),
    'ks_p': float(ks_p_c424),
    'pass': t15_pass,
}


# ════════════════════════════════════════════════════════════════
# GATE CHECK
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("GATE CHECK: Phase 1")
print("=" * 70)

tests = ['T1.1 (C694)', 'T1.2 (C695)', 'T1.3 (C696)', 'T1.4 (C697)', 'T1.5 (C698)']
passes = [
    results['T1_1_ri_placement']['pass'],
    results['T1_2_pp_run_length']['pass'],
    results['T1_3_ri_line_final']['pass'],
    results['T1_4_prefix_clustering']['pass'],
    results['T1_5_bundle_c424_match']['pass'],
]

for test, passed in zip(tests, passes):
    status = "PASS" if passed else "FAIL"
    print(f"  {test}: {status}")

print(f"\n  Total passed: {pass_count}/5")
gate_passed = pass_count >= 4
print(f"  Gate (4/5): {'PASSED' if gate_passed else 'FAILED'}")

results['gate'] = {
    'threshold': '4/5',
    'passed': int(pass_count),
    'total': 5,
    'result': 'PASSED' if gate_passed else 'FAILED',
}

# ── Save ──
out_path = RESULTS_DIR / 'structural_validation.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n  Saved: {out_path}")
print("\nDone.")
