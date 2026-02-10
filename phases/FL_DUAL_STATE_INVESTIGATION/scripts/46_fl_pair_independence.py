"""
46_fl_pair_independence.py

Tests whether the 2D FL grid (LOW_stage, HIGH_stage) is genuine pairwise
structure or merely two independent 1D gradients projected together.

Three tests:
  1. CONTINGENCY TABLE CHI-SQUARED: Does the joint distribution of (lo, ho)
     differ significantly from the product of marginals?
  2. MUTUAL INFORMATION: Is the MI between lo and ho greater than expected
     under 1000 independent shuffles?
  3. CONDITIONAL DISTRIBUTION: For each lo value, does the distribution of
     ho differ from the ho marginal? (Per-row chi-squared / KL divergence.)

Verdict:
  GENUINE_2D           -- 2+ checks pass
  WEAK_2D              -- exactly 1 check passes
  PROJECTION_ARTIFACT  -- 0 checks pass
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency, chi2

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# ============================================================
# Constants (identical to scripts 42-45)
# ============================================================
FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}
STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}
STAGES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']

tx = Transcript()
morph = Morphology()
MIN_N = 50

# ============================================================
# Build data pipeline (identical to scripts 42-45)
# ============================================================
line_tokens = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)

# Fit GMMs per FL middle
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))

gmm_models = {}
for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm.fit(X)
    if gmm.means_[0] > gmm.means_[1]:
        gmm_models[mid] = {'model': gmm, 'swap': True}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False}

# Assign line coordinates
line_coords = {}
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue
    fl_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]
            fl_info.append({'mode': mode, 'stage': stage})
    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue
    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    lo = STAGE_ORDER[low_stage]
    ho = STAGE_ORDER[high_stage]
    line_coords[line_key] = {'lo': lo, 'ho': ho}

all_lo = np.array([c['lo'] for c in line_coords.values()])
all_ho = np.array([c['ho'] for c in line_coords.values()])
N = len(all_lo)

print("=" * 70)
print("FL PAIR INDEPENDENCE TEST")
print("=" * 70)
print(f"\nLines with (lo, ho) coordinates: {N}")

# ============================================================
# Marginal distributions
# ============================================================
lo_counts = Counter(all_lo.tolist())
ho_counts = Counter(all_ho.tolist())
lo_vals_present = sorted(lo_counts.keys())
ho_vals_present = sorted(ho_counts.keys())

print(f"\nLO marginal: {dict(sorted(lo_counts.items()))}")
print(f"HO marginal: {dict(sorted(ho_counts.items()))}")

# ============================================================
# TEST 1: CONTINGENCY TABLE CHI-SQUARED
# ============================================================
print(f"\n{'='*70}")
print("TEST 1: CONTINGENCY TABLE CHI-SQUARED")
print("=" * 70)
print("\n  H0: lo_stage and ho_stage are independent.")
print("  H1: The joint distribution differs from the product of marginals.\n")

# Build contingency table using all 6 stages as rows/columns
n_stages = len(STAGES)
contingency = np.zeros((n_stages, n_stages), dtype=int)
for c in line_coords.values():
    contingency[c['lo'], c['ho']] += 1

print("  Contingency table (rows=lo, cols=ho):")
header = "       " + "  ".join(f"{s[:4]:>5}" for s in STAGES)
print(f"  {header}")
for i, stage in enumerate(STAGES):
    row_str = "  ".join(f"{contingency[i,j]:>5}" for j in range(n_stages))
    print(f"  {stage[:5]:>5}  {row_str}")

# Remove rows/cols that are all zero for chi-squared validity
row_mask = contingency.sum(axis=1) > 0
col_mask = contingency.sum(axis=0) > 0
contingency_trimmed = contingency[np.ix_(row_mask, col_mask)]

if contingency_trimmed.shape[0] >= 2 and contingency_trimmed.shape[1] >= 2:
    chi2_stat, chi2_p, chi2_dof, chi2_expected = chi2_contingency(contingency_trimmed)
    print(f"\n  Chi-squared statistic: {chi2_stat:.2f}")
    print(f"  Degrees of freedom:   {chi2_dof}")
    print(f"  p-value:              {chi2_p:.6e}")
    # Cramers V for effect size
    k = min(contingency_trimmed.shape)
    cramers_v = np.sqrt(chi2_stat / (N * (k - 1))) if N > 0 and k > 1 else 0.0
    print(f"  Cramer's V:           {cramers_v:.4f}")
else:
    chi2_stat = 0.0
    chi2_p = 1.0
    chi2_dof = 0
    cramers_v = 0.0
    print("\n  Insufficient categories for chi-squared test.")

check_1 = bool(chi2_p < 0.01)
print(f"\n  check_1 (chi2 p < 0.01): {check_1}")

# ============================================================
# TEST 2: MUTUAL INFORMATION vs NULL DISTRIBUTION
# ============================================================
print(f"\n{'='*70}")
print("TEST 2: MUTUAL INFORMATION (observed vs 1000 shuffles)")
print("=" * 70)
print("\n  MI measures how much knowing lo reduces uncertainty about ho.")
print("  Under independence MI = 0. Compare to null from shuffled data.\n")


def compute_mi(lo_arr, ho_arr):
    """Compute mutual information between two discrete arrays."""
    n = len(lo_arr)
    if n == 0:
        return 0.0
    joint = Counter(zip(lo_arr.tolist(), ho_arr.tolist()))
    lo_marginal = Counter(lo_arr.tolist())
    ho_marginal = Counter(ho_arr.tolist())
    mi = 0.0
    for (l, h), count in joint.items():
        p_joint = count / n
        p_lo = lo_marginal[l] / n
        p_ho = ho_marginal[h] / n
        if p_joint > 0 and p_lo > 0 and p_ho > 0:
            mi += p_joint * np.log2(p_joint / (p_lo * p_ho))
    return mi


obs_mi = compute_mi(all_lo, all_ho)
print(f"  Observed MI: {obs_mi:.6f} bits")

# Null distribution: independently permute lo and ho
rng = np.random.RandomState(42)
N_SHUFFLES = 1000
null_mi = np.zeros(N_SHUFFLES)
for i in range(N_SHUFFLES):
    shuf_lo = rng.permutation(all_lo)
    shuf_ho = rng.permutation(all_ho)
    null_mi[i] = compute_mi(shuf_lo, shuf_ho)

null_mi_mean = float(np.mean(null_mi))
null_mi_95 = float(np.percentile(null_mi, 95))
null_mi_99 = float(np.percentile(null_mi, 99))
mi_p = float(np.mean(null_mi >= obs_mi))

print(f"  Null MI mean:          {null_mi_mean:.6f}")
print(f"  Null MI 95th pctile:   {null_mi_95:.6f}")
print(f"  Null MI 99th pctile:   {null_mi_99:.6f}")
print(f"  Permutation p-value:   {mi_p:.4f}")
print(f"  MI ratio (obs/null95): {obs_mi / null_mi_95:.2f}x" if null_mi_95 > 0
      else "  MI ratio: null_95 is zero")

check_2 = bool(obs_mi > null_mi_95)
print(f"\n  check_2 (obs MI > null 95th pctile): {check_2}")

# ============================================================
# TEST 3: CONDITIONAL DISTRIBUTION TEST
# ============================================================
print(f"\n{'='*70}")
print("TEST 3: CONDITIONAL DISTRIBUTION (ho | lo)")
print("=" * 70)
print("\n  For each lo value, is the conditional distribution of ho different")
print("  from the overall ho marginal? If independent, ho|lo == ho marginal.\n")

# Build ho marginal distribution (as proportions)
ho_marginal_counts = np.zeros(n_stages)
for h in all_ho:
    ho_marginal_counts[h] += 1
ho_marginal_dist = ho_marginal_counts / ho_marginal_counts.sum()

print(f"  HO marginal distribution:")
for i, s in enumerate(STAGES):
    if ho_marginal_counts[i] > 0:
        print(f"    {s}: {ho_marginal_counts[i]:.0f} ({ho_marginal_dist[i]:.3f})")

print(f"\n  Conditional distributions ho|lo:")
conditional_results = []
n_lo_significant = 0
n_lo_tested = 0

for lo_val in range(n_stages):
    # Get ho values for this lo
    mask = all_lo == lo_val
    n_lo = int(mask.sum())
    if n_lo < 5:
        continue
    n_lo_tested += 1
    ho_given_lo = all_ho[mask]
    ho_cond_counts = np.zeros(n_stages)
    for h in ho_given_lo:
        ho_cond_counts[h] += 1
    ho_cond_dist = ho_cond_counts / ho_cond_counts.sum()

    # Chi-squared test: observed conditional vs expected (marginal * n_lo)
    expected = ho_marginal_dist * n_lo
    # Only include cells where expected > 0
    valid = expected > 0
    if valid.sum() < 2:
        continue

    obs_cells = ho_cond_counts[valid]
    exp_cells = expected[valid]
    chi2_cond = float(np.sum((obs_cells - exp_cells) ** 2 / exp_cells))
    dof_cond = int(valid.sum() - 1)
    if dof_cond > 0:
        p_cond = float(1.0 - chi2.cdf(chi2_cond, dof_cond))
    else:
        p_cond = 1.0

    # KL divergence (ho_cond || ho_marginal), only where both > 0
    both_pos = (ho_cond_dist > 0) & (ho_marginal_dist > 0)
    if both_pos.sum() > 0:
        kl = float(np.sum(ho_cond_dist[both_pos] *
                          np.log2(ho_cond_dist[both_pos] / ho_marginal_dist[both_pos])))
    else:
        kl = 0.0

    is_sig = bool(p_cond < 0.05)
    if is_sig:
        n_lo_significant += 1

    cond_detail = {
        'lo_stage': STAGES[lo_val],
        'lo_val': lo_val,
        'n': n_lo,
        'chi2': round(chi2_cond, 3),
        'dof': dof_cond,
        'p': round(p_cond, 6),
        'kl_divergence': round(kl, 6),
        'significant': is_sig,
    }
    conditional_results.append(cond_detail)

    dist_str = "  ".join(f"{STAGES[j][:4]}={ho_cond_dist[j]:.2f}" for j in range(n_stages)
                         if ho_cond_counts[j] > 0 or ho_marginal_counts[j] > 0)
    sig_marker = " ***" if is_sig else ""
    print(f"    lo={STAGES[lo_val]:<9} (n={n_lo:>3}): chi2={chi2_cond:>7.2f}  "
          f"p={p_cond:.4f}  KL={kl:.4f}{sig_marker}")

frac_significant = n_lo_significant / n_lo_tested if n_lo_tested > 0 else 0.0
print(f"\n  Lo values tested: {n_lo_tested}")
print(f"  Significant conditional deviations: {n_lo_significant}/{n_lo_tested} "
      f"({frac_significant:.0%})")

check_3 = bool(frac_significant >= 0.50)
print(f"\n  check_3 (>=50% lo values show significant deviation): {check_3}")

# ============================================================
# VERDICT
# ============================================================
print(f"\n{'='*70}")
print("VERDICT")
print("=" * 70)

n_pass = sum([check_1, check_2, check_3])
print(f"\n  check_1 (chi2 independence test, p<0.01):     {check_1}")
print(f"  check_2 (MI exceeds 95th pctile of null):      {check_2}")
print(f"  check_3 (>=50% conditional deviations sig.):   {check_3}")
print(f"\n  Checks passed: {n_pass}/3")

if n_pass >= 2:
    verdict = "GENUINE_2D"
    explanation = (
        f"The (lo, ho) joint distribution is NOT explained by two independent "
        f"marginals. {n_pass}/3 independence tests reject the null hypothesis. "
        f"The 2D FL grid contains genuine pairwise structure beyond what "
        f"independent 1D gradients would produce."
    )
elif n_pass == 1:
    verdict = "WEAK_2D"
    explanation = (
        f"Only 1/3 independence tests rejects the null. The evidence for "
        f"genuine 2D structure is weak -- the grid may be partially explained "
        f"by independent marginals with minor coupling."
    )
else:
    verdict = "PROJECTION_ARTIFACT"
    explanation = (
        f"0/3 independence tests reject the null. The 2D grid is consistent "
        f"with two independent 1D gradients projected together. No genuine "
        f"pairwise structure detected."
    )

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

# ============================================================
# Write results
# ============================================================
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.bool_): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

results = {
    'n_lines': N,
    'lo_marginal': dict(sorted(lo_counts.items())),
    'ho_marginal': dict(sorted(ho_counts.items())),
    'test_1_chi_squared': {
        'contingency_table': contingency.tolist(),
        'chi2_statistic': round(float(chi2_stat), 3),
        'dof': int(chi2_dof),
        'p_value': float(chi2_p),
        'cramers_v': round(float(cramers_v), 4),
        'check_1': check_1,
    },
    'test_2_mutual_information': {
        'observed_mi_bits': round(float(obs_mi), 6),
        'null_mi_mean': round(null_mi_mean, 6),
        'null_mi_95th': round(null_mi_95, 6),
        'null_mi_99th': round(null_mi_99, 6),
        'permutation_p': round(float(mi_p), 4),
        'n_shuffles': N_SHUFFLES,
        'check_2': check_2,
    },
    'test_3_conditional_distribution': {
        'n_lo_tested': n_lo_tested,
        'n_lo_significant': n_lo_significant,
        'fraction_significant': round(frac_significant, 3),
        'per_lo_results': conditional_results,
        'check_3': check_3,
    },
    'checks': {
        'check_1': check_1,
        'check_2': check_2,
        'check_3': check_3,
        'n_pass': n_pass,
    },
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '46_fl_pair_independence.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
