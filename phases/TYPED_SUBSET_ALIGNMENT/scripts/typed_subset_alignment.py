"""
Phase 607: TYPED_SUBSET_ALIGNMENT
Tests whether PL-internal co-variate structure transfers to V Stars
under a specific a priori feature mapping.

Two-layer design:
  Layer A: Conservative heat-monitoring anchor (replicates C1752 within Stars)
  Layer B: Bold threshold-authenticity probe (novel predictions)
  Controls: N1 feature mapping shuffle, N2 random PL subset

Graceful degradation: If S_T (3-condition) is too small, tries S_T_relaxed
(2-condition, dropping chain requirement). Layer A runs regardless.
"""

import json
import os
import hashlib
import numpy as np
from scipy import stats

# ── 0. Pre-registration ─────────────────────────────────────────────
PRED_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'PREDICTIONS.md')
EXPECTED_HASH = 'b3d96e77acd589be48ffd8b9943b62ec8a31cf45072d20bfc4c5e92ad2646d2f'
actual_hash = hashlib.sha256(open(PRED_PATH, 'rb').read()).hexdigest()
assert actual_hash == EXPECTED_HASH, f'PREDICTIONS.md hash mismatch: {actual_hash}'
print(f'[OK] Pre-registration hash verified: {actual_hash[:16]}...')

# ── 1. Load data sources ────────────────────────────────────────────
pl_data = json.load(open('phases/PSEUDO_LULL_CHARACTERIZATION/results/pseudo_lull_structural_profile.json'))
pl_chapters = pl_data['E1_chapters']

op_raw = json.load(open('results/folio_operational_profiles.json'))
op_profiles = {p['folio']: p for p in op_raw['profiles']}

t0_data = json.load(open('phases/A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/results/t0_opportunity_normalization.json'))
t0_cov = t0_data['covariates']

scaffold = json.load(open('results/b_macro_scaffold_audit.json'))
scaf_feat = scaffold['features']

# ── Join V features for Stars ────────────────────────────────────────
stars_folios = sorted(k for k, v in t0_cov.items() if v.get('section') == 'S')
print(f'Stars folios identified: {len(stars_folios)}')

v_data = {}
for f in stars_folios:
    if f not in op_profiles:
        continue
    op = op_profiles[f]
    cov = t0_cov[f]
    sc = scaf_feat.get(f, {})
    v_data[f] = {
        'thermo_ke': op['thermo_ke'],
        'h_ratio': op['h_ratio'],
        'checkpoint_rate': op['checkpoint_rate'],
        'iteration_rate': op['iteration_rate'],
        'k_ratio': op['k_ratio'],
        'strong_close_fraction': cov.get('strong_close_fraction', np.nan),
        'qo_density': sc.get('qo_density', np.nan),
    }

v_folios = sorted(v_data.keys())
n_stars = len(v_folios)
print(f'Stars folios with complete V data: {n_stars}')

V_FEATURES = ['thermo_ke', 'h_ratio', 'strong_close_fraction', 'checkpoint_rate', 'iteration_rate']
v_arrays = {}
for feat in V_FEATURES + ['qo_density', 'k_ratio']:
    v_arrays[feat] = np.array([v_data[f][feat] for f in v_folios])

# ── Compute PL per-chapter rates ────────────────────────────────────
PL_FEATURES = ['heat_rate', 'monitoring_rate', 'termination_rate',
               'judgment_rate', 'chain_rate', 'correction_rate', 'operational_density']

pl_records = []
for ch in pl_chapters:
    lines = ch['en_line_end'] - ch['en_line_start']
    if lines <= 0:
        continue
    pl_records.append({
        'heat_rate': ch['heat_count'] / lines,
        'monitoring_rate': ch['monitoring_count'] / lines,
        'termination_rate': ch['termination_count'] / lines,
        'judgment_rate': ch['judgment_count'] / lines,
        'chain_rate': ch['chain_count'] / lines,
        'correction_rate': ch['correction_count'] / lines,
        'operational_density': ch['operational_density'],
        'chapter': ch['number'],
        'family': ch['primary_family'],
    })

n_pl = len(pl_records)
print(f'PL chapters with valid line counts: {n_pl}')

# ── 2. Compute PL medians and P75 ───────────────────────────────────
pl_arrays = {}
for feat in PL_FEATURES:
    pl_arrays[feat] = np.array([r[feat] for r in pl_records])

medians = {feat: float(np.median(pl_arrays[feat])) for feat in PL_FEATURES}
p75 = {feat: float(np.percentile(pl_arrays[feat], 75)) for feat in PL_FEATURES}

print('\nPL feature medians:')
for f in PL_FEATURES:
    nz = int(np.sum(pl_arrays[f] > 0))
    print(f'  {f}: median={medians[f]:.6f}  P75={p75[f]:.6f}  nonzero={nz}/{n_pl}')

# ── 3. Define subsets ────────────────────────────────────────────────
def subset_mask(records, condition):
    return [i for i, r in enumerate(records) if condition(r)]

# Conservative pair (Layer A)
s_hm_hot = subset_mask(pl_records, lambda r: r['heat_rate'] > medians['heat_rate']
                        and r['monitoring_rate'] < medians['monitoring_rate'])
s_hm_mon = subset_mask(pl_records, lambda r: r['monitoring_rate'] > medians['monitoring_rate']
                        and r['heat_rate'] < medians['heat_rate'])

# Bold subset: 3-condition (pre-registered)
s_t_strict = subset_mask(pl_records, lambda r: r['termination_rate'] > medians['termination_rate']
                         and r['judgment_rate'] > medians['judgment_rate']
                         and r['chain_rate'] < medians['chain_rate'])

# Relaxed S_T: 2-condition (drop chain, since expert noted threshold procedures
# can be iterative — C1579, C1642-C1648 — and P2 was already demoted)
s_t_relaxed = subset_mask(pl_records, lambda r: r['termination_rate'] > medians['termination_rate']
                          and r['judgment_rate'] > medians['judgment_rate'])

# Additional (discrimination)
s_r = subset_mask(pl_records, lambda r: r['correction_rate'] > p75['correction_rate'])
s_m = subset_mask(pl_records, lambda r: r['monitoring_rate'] > medians['monitoring_rate']
                  and r['termination_rate'] > medians['termination_rate'])

print('\nSubset sizes:')
print(f'  S_HM_hot: n={len(s_hm_hot)}')
print(f'  S_HM_mon: n={len(s_hm_mon)}')
print(f'  S_T_strict (3-cond): n={len(s_t_strict)}')
print(f'  S_T_relaxed (2-cond): n={len(s_t_relaxed)}')
print(f'  S_R: n={len(s_r)}')
print(f'  S_M: n={len(s_m)}')

# ── 4. C0 gates (split) ─────────────────────────────────────────────
MIN_N = 12

c0a_pass = len(s_hm_hot) >= MIN_N and len(s_hm_mon) >= MIN_N
c0b_strict = len(s_t_strict) >= MIN_N
c0b_relaxed = len(s_t_relaxed) >= MIN_N

# Choose which S_T to use
if c0b_strict:
    s_t = s_t_strict
    s_t_variant = 'strict'
    c0b_pass = True
elif c0b_relaxed:
    s_t = s_t_relaxed
    s_t_variant = 'relaxed'
    c0b_pass = True
    print(f'\n[NOTE] S_T strict (n={len(s_t_strict)}) < {MIN_N}. Using S_T relaxed (n={len(s_t_relaxed)}).')
    print(f'  Relaxation: dropped chain < median condition (expert noted threshold')
    print(f'  procedures can be iterative — C1579, C1642-C1648; P2 already demoted)')
else:
    s_t = []
    s_t_variant = 'none'
    c0b_pass = False

all_subsets = {
    'S_HM_hot': s_hm_hot, 'S_HM_mon': s_hm_mon,
    'S_T': s_t, 'S_R': s_r, 'S_M': s_m
}

results = {
    'phase': 607,
    'predictions_hash': actual_hash,
    'n_stars': n_stars,
    'n_pl_chapters': n_pl,
    'pl_medians': medians,
    'subset_sizes': {
        'S_HM_hot': len(s_hm_hot), 'S_HM_mon': len(s_hm_mon),
        'S_T_strict': len(s_t_strict), 'S_T_relaxed': len(s_t_relaxed),
        'S_R': len(s_r), 'S_M': len(s_m),
    },
    'S_T_variant': s_t_variant,
    'C0a': {'pass': c0a_pass, 'S_HM_hot': len(s_hm_hot), 'S_HM_mon': len(s_hm_mon)},
    'C0b': {'pass': c0b_pass, 'strict_n': len(s_t_strict), 'relaxed_n': len(s_t_relaxed), 'variant': s_t_variant},
}

print(f'\nC0a (Layer A subsets >= {MIN_N}): {"PASS" if c0a_pass else "FAIL"}')
print(f'C0b (S_T >= {MIN_N}): {"PASS" if c0b_pass else "FAIL"} (variant={s_t_variant})')

if not c0a_pass:
    results['verdict'] = 'INSUFFICIENT_DATA'
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results',
                            'typed_subset_alignment_results.json')
    json.dump(results, open(out_path, 'w'), indent=2, default=float)
    print(f'\nVerdict: INSUFFICIENT_DATA')
    exit()

# ── 5. Layer A anchor: A1 (runs regardless of S_T) ──────────────────
rho_a1, p_a1_two = stats.spearmanr(v_arrays['thermo_ke'], v_arrays['h_ratio'])
p_a1 = p_a1_two / 2 if rho_a1 < 0 else 1 - p_a1_two / 2
a1_pass = rho_a1 < 0 and p_a1 < 0.05

print(f'\nA1 anchor: thermo_ke vs h_ratio in Stars')
print(f'  rho={rho_a1:.4f} p_one_sided={p_a1:.6f} {"PASS" if a1_pass else "FAIL"}')

results['A1'] = {'rho': float(rho_a1), 'p_one_sided': float(p_a1), 'pass': a1_pass, 'n': n_stars}

# C1b gate (marginal does NOT halt — we continue and report all results)
c1b_pass = a1_pass
results['C1b'] = {'pass': c1b_pass}
if not c1b_pass:
    print(f'  [C1b FAIL: A1 marginal. Continuing to report all results with FRAMEWORK_MARGINAL context.]')

# ── 6. C1a gate: S_T separability (only if S_T available) ───────────
layer_b_active = c0b_pass

if layer_b_active:
    held_out_features = ['monitoring_rate', 'correction_rate', 'heat_rate', 'operational_density']
    # If using relaxed S_T, chain_rate is also held-out (not used in definition)
    if s_t_variant == 'relaxed':
        held_out_features.append('chain_rate')

    s_t_set = set(s_t)
    rest_idx = [i for i in range(n_pl) if i not in s_t_set]

    c1a_tests = {}
    c1a_pass_count = 0
    for feat in held_out_features:
        s_t_vals = [pl_records[i][feat] for i in s_t]
        rest_vals = [pl_records[i][feat] for i in rest_idx]
        u_stat, p_val = stats.mannwhitneyu(s_t_vals, rest_vals, alternative='two-sided')
        passed = p_val < 0.05
        if passed:
            c1a_pass_count += 1
        c1a_tests[feat] = {
            'U': float(u_stat), 'p': float(p_val), 'pass': passed,
            'S_T_mean': float(np.mean(s_t_vals)), 'rest_mean': float(np.mean(rest_vals))
        }

    c1a_pass = c1a_pass_count >= 2
    print(f'\nC1a gate (S_T separable on >= 2/{len(held_out_features)} held-out): {"PASS" if c1a_pass else "FAIL"} ({c1a_pass_count}/{len(held_out_features)})')
    for feat, t in c1a_tests.items():
        print(f'  {feat}: U={t["U"]:.1f} p={t["p"]:.4f} S_T={t["S_T_mean"]:.4f} rest={t["rest_mean"]:.4f} {"PASS" if t["pass"] else "FAIL"}')

    results['C1a'] = {'pass': c1a_pass, 'n_passing': c1a_pass_count,
                       'n_held_out': len(held_out_features), 'tests': c1a_tests}

    if not c1a_pass:
        layer_b_active = False
        print('  [Layer B deactivated: S_T not separable]')

# ── 7. Layer B predictions: P1, P2 ──────────────────────────────────
# These V-internal tests run regardless (the correlations exist or not),
# but are only counted toward verdict if Layer B is active.

# P1: strong_close_fraction vs checkpoint_rate (positive)
rho_p1, p_p1_two = stats.spearmanr(v_arrays['strong_close_fraction'], v_arrays['checkpoint_rate'])
p_p1 = p_p1_two / 2 if rho_p1 > 0 else 1 - p_p1_two / 2
p1_pass = rho_p1 > 0 and p_p1 < 0.05

# P2: h_ratio vs checkpoint_rate (positive)
rho_p2, p_p2_two = stats.spearmanr(v_arrays['h_ratio'], v_arrays['checkpoint_rate'])
p_p2 = p_p2_two / 2 if rho_p2 > 0 else 1 - p_p2_two / 2
p2_pass = rho_p2 > 0 and p_p2 < 0.05

K = int(p1_pass) + int(p2_pass)

print(f'\nLayer B predictions (Stars n={n_stars}):')
print(f'  P1: strong_close_fraction vs checkpoint_rate: rho={rho_p1:.4f} p={p_p1:.6f} {"PASS" if p1_pass else "FAIL"}')
print(f'  P2: h_ratio vs checkpoint_rate:              rho={rho_p2:.4f} p={p_p2:.6f} {"PASS" if p2_pass else "FAIL"}')
if not layer_b_active:
    print(f'  [Layer B deactivated — V correlations reported but not counted toward verdict]')

results['primary_battery'] = [
    {'id': 'P1_SCF_CHECKPOINT', 'rho': float(rho_p1), 'p_one_sided': float(p_p1), 'pass': p1_pass, 'n': n_stars},
    {'id': 'P2_HRATIO_CHECKPOINT', 'rho': float(rho_p2), 'p_one_sided': float(p_p2), 'pass': p2_pass, 'n': n_stars},
]
results['K'] = K
results['layer_b_active'] = layer_b_active

# ── 8. Secondary battery ────────────────────────────────────────────
# S1: strong_close_fraction vs iteration_rate (negative)
rho_s1, p_s1_two = stats.spearmanr(v_arrays['strong_close_fraction'], v_arrays['iteration_rate'])
p_s1 = p_s1_two / 2 if rho_s1 < 0 else 1 - p_s1_two / 2
s1_pass = rho_s1 < 0 and p_s1 < 0.05

# S2: S_HM_hot vs S_HM_mon discrimination (>= 3/7 features differ)
s2_diffs = 0
s2_detail = {}
for feat in PL_FEATURES:
    hot_vals = [pl_records[i][feat] for i in s_hm_hot]
    mon_vals = [pl_records[i][feat] for i in s_hm_mon]
    u, p = stats.mannwhitneyu(hot_vals, mon_vals, alternative='two-sided')
    sig = p < 0.05
    if sig:
        s2_diffs += 1
    s2_detail[feat] = {'U': float(u), 'p': float(p), 'pass': sig}
s2_pass = s2_diffs >= 3

# S3: All-PL co-variate transfer
all_term = pl_arrays['termination_rate']
all_judg = pl_arrays['judgment_rate']
all_mon = pl_arrays['monitoring_rate']

rho_all_tj, _ = stats.spearmanr(all_term, all_judg)
rho_all_tc, _ = stats.spearmanr(all_term, pl_arrays['chain_rate'])
rho_all_mj, _ = stats.spearmanr(all_mon, all_judg)

s3_pred_p1_sign = 1 if rho_all_tj > 0 else -1
s3_pred_p2_sign = 1 if rho_all_mj > 0 else -1

if s3_pred_p1_sign > 0:
    s3_p1_pass = rho_p1 > 0 and p_p1 < 0.05
else:
    p_neg = p_p1_two / 2 if rho_p1 < 0 else 1 - p_p1_two / 2
    s3_p1_pass = rho_p1 < 0 and p_neg < 0.05

if s3_pred_p2_sign > 0:
    s3_p2_pass = rho_p2 > 0 and p_p2 < 0.05
else:
    p_neg = p_p2_two / 2 if rho_p2 < 0 else 1 - p_p2_two / 2
    s3_p2_pass = rho_p2 < 0 and p_neg < 0.05

s3_k = int(s3_p1_pass) + int(s3_p2_pass)

# S4: PL-internal S_T co-variates (descriptive, if S_T available)
s4_results = {}
if len(s_t) >= 6:
    s_t_term = np.array([pl_records[i]['termination_rate'] for i in s_t])
    s_t_judg = np.array([pl_records[i]['judgment_rate'] for i in s_t])
    s_t_chain = np.array([pl_records[i]['chain_rate'] for i in s_t])
    s_t_mon = np.array([pl_records[i]['monitoring_rate'] for i in s_t])

    rho_tj, p_tj = stats.spearmanr(s_t_term, s_t_judg)
    rho_tc, p_tc = stats.spearmanr(s_t_term, s_t_chain)
    rho_mj, p_mj = stats.spearmanr(s_t_mon, s_t_judg)
    s4_results = {
        'term_judg': {'rho': float(rho_tj), 'p': float(p_tj)},
        'term_chain': {'rho': float(rho_tc), 'p': float(p_tc)},
        'mon_judg': {'rho': float(rho_mj), 'p': float(p_mj)},
    }

print(f'\nSecondary battery:')
print(f'  S1: SCF vs iteration_rate: rho={rho_s1:.4f} p={p_s1:.6f} {"PASS" if s1_pass else "FAIL"}')
print(f'  S2: S_HM_hot vs S_HM_mon differ on {s2_diffs}/7 features: {"PASS" if s2_pass else "FAIL"}')
print(f'  S3: All-PL co-variate transfer K={s3_k} (signs: P1={s3_pred_p1_sign:+d} P2={s3_pred_p2_sign:+d})')
print(f'       All-PL: term<>judg={rho_all_tj:.3f} term<>chain={rho_all_tc:.3f} mon<>judg={rho_all_mj:.3f}')
if s4_results:
    print(f'  S4: S_T (n={len(s_t)}) internal co-variates:')
    for pair, vals in s4_results.items():
        print(f'       {pair}: rho={vals["rho"]:.4f} p={vals["p"]:.6f}')

results['secondary_battery'] = [
    {'id': 'S1_SCF_ITERATION', 'rho': float(rho_s1), 'p_one_sided': float(p_s1), 'pass': s1_pass, 'n': n_stars},
    {'id': 'S2_HM_DISCRIMINATION', 'n_differing': s2_diffs, 'pass': s2_pass, 'detail': s2_detail},
    {'id': 'S3_ALL_PL_TRANSFER', 'K': s3_k,
     'all_pl_covariates': {'term_judg': float(rho_all_tj), 'term_chain': float(rho_all_tc), 'mon_judg': float(rho_all_mj)},
     'predicted_signs': {'P1': s3_pred_p1_sign, 'P2': s3_pred_p2_sign}},
    {'id': 'S4_ST_INTERNAL', 'n': len(s_t), 'covariates': s4_results},
]

# ── 9. N1: Feature mapping shuffle ──────────────────────────────────
# Use S_T co-variate signs if available, else all-PL signs
rng = np.random.RandomState(42)
N_SHUFFLES = 500

if s4_results:
    sign_tj = 1 if s4_results['term_judg']['rho'] > 0 else -1
    sign_mj = 1 if s4_results['mon_judg']['rho'] > 0 else -1
    sign_source = 'S_T'
else:
    sign_tj = s3_pred_p1_sign
    sign_mj = s3_pred_p2_sign
    sign_source = 'all_PL'

K_obs = K
v_feature_names = ['thermo_ke', 'h_ratio', 'strong_close_fraction', 'checkpoint_rate', 'iteration_rate']
# PL index: 0=heat, 1=monitoring, 2=termination, 3=judgment, 4=chain
# P1 uses (term=2, judg=3), P2 uses (mon=1, judg=3)

n1_k_dist = []
for _ in range(N_SHUFFLES):
    perm = rng.permutation(5)
    v1a = v_arrays[v_feature_names[perm[2]]]
    v1b = v_arrays[v_feature_names[perm[3]]]
    v2a = v_arrays[v_feature_names[perm[1]]]
    v2b = v_arrays[v_feature_names[perm[3]]]

    rho1, p1_two = stats.spearmanr(v1a, v1b)
    rho2, p2_two = stats.spearmanr(v2a, v2b)

    if sign_tj > 0:
        p1o = p1_two / 2 if rho1 > 0 else 1 - p1_two / 2
        pass1 = rho1 > 0 and p1o < 0.05
    else:
        p1o = p1_two / 2 if rho1 < 0 else 1 - p1_two / 2
        pass1 = rho1 < 0 and p1o < 0.05

    if sign_mj > 0:
        p2o = p2_two / 2 if rho2 > 0 else 1 - p2_two / 2
        pass2 = rho2 > 0 and p2o < 0.05
    else:
        p2o = p2_two / 2 if rho2 < 0 else 1 - p2_two / 2
        pass2 = rho2 < 0 and p2o < 0.05

    n1_k_dist.append(int(pass1) + int(pass2))

n1_frac = float(np.mean(np.array(n1_k_dist) >= K_obs)) if K_obs > 0 else 1.0
n1_pass = n1_frac < 0.05

print(f'\nN1: Feature mapping shuffle ({N_SHUFFLES} perms, signs from {sign_source})')
print(f'  sign_tj={sign_tj:+d} sign_mj={sign_mj:+d}')
print(f'  K_obs={K_obs} frac(K_shuffle >= K_obs)={n1_frac:.4f} {"PASS" if n1_pass else "FAIL"}')

results['N1_mapping_shuffle'] = {
    'n_shuffles': N_SHUFFLES, 'K_obs': K_obs,
    'frac_exceeding': n1_frac, 'pass': n1_pass,
    'sign_tj': sign_tj, 'sign_mj': sign_mj, 'sign_source': sign_source,
}

# ── 10. N2: Random PL subset ────────────────────────────────────────
n_st = len(s_t) if len(s_t) >= MIN_N else len(s_t_relaxed)
n2_k_dist = []

for _ in range(N_SHUFFLES):
    rand_idx = rng.choice(n_pl, size=max(n_st, 6), replace=False)
    r_term = np.array([pl_records[i]['termination_rate'] for i in rand_idx])
    r_judg = np.array([pl_records[i]['judgment_rate'] for i in rand_idx])
    r_mon = np.array([pl_records[i]['monitoring_rate'] for i in rand_idx])

    r_tj, _ = stats.spearmanr(r_term, r_judg)
    r_mj, _ = stats.spearmanr(r_mon, r_judg)

    r_sign_tj = 1 if r_tj > 0 else -1
    r_sign_mj = 1 if r_mj > 0 else -1

    if r_sign_tj > 0:
        pass1 = rho_p1 > 0 and p_p1 < 0.05
    else:
        p_neg = p_p1_two / 2 if rho_p1 < 0 else 1 - p_p1_two / 2
        pass1 = rho_p1 < 0 and p_neg < 0.05

    if r_sign_mj > 0:
        pass2 = rho_p2 > 0 and p_p2 < 0.05
    else:
        p_neg = p_p2_two / 2 if rho_p2 < 0 else 1 - p_p2_two / 2
        pass2 = rho_p2 < 0 and p_neg < 0.05

    n2_k_dist.append(int(pass1) + int(pass2))

n2_frac = float(np.mean(np.array(n2_k_dist) >= K_obs)) if K_obs > 0 else 1.0
n2_pass = n2_frac < 0.05

print(f'\nN2: Random PL subset ({N_SHUFFLES} draws, n={max(n_st, 6)})')
print(f'  K_obs={K_obs} frac(K_random >= K_obs)={n2_frac:.4f} {"PASS" if n2_pass else "FAIL"}')

results['N2_random_subset'] = {
    'n_shuffles': N_SHUFFLES, 'n_subset': max(n_st, 6),
    'K_obs': K_obs, 'frac_exceeding': n2_frac, 'pass': n2_pass,
}

# ── 11. Exploratory ─────────────────────────────────────────────────
# D1: Kruskal-Wallis across subsets
chapter_labels = ['remainder'] * n_pl
for name, idx_list in all_subsets.items():
    for i in idx_list:
        if chapter_labels[i] == 'remainder':
            chapter_labels[i] = name

unique_labels = sorted(set(chapter_labels))
d1_results = {}
for feat in PL_FEATURES:
    groups = []
    for label in unique_labels:
        vals = [pl_records[i][feat] for i in range(n_pl) if chapter_labels[i] == label]
        if len(vals) >= 2:
            groups.append(vals)
    if len(groups) >= 2:
        h_stat, p_val = stats.kruskal(*groups)
        d1_results[feat] = {'H': float(h_stat), 'p': float(p_val), 'n_groups': len(groups)}

# D2: Per-prediction N1 pass fractions
rng2 = np.random.RandomState(42)
n1_p1_count = 0
n1_p2_count = 0
for _ in range(N_SHUFFLES):
    perm = rng2.permutation(5)
    v1a = v_arrays[v_feature_names[perm[2]]]
    v1b = v_arrays[v_feature_names[perm[3]]]
    v2a = v_arrays[v_feature_names[perm[1]]]
    v2b = v_arrays[v_feature_names[perm[3]]]

    rho1, p1t = stats.spearmanr(v1a, v1b)
    rho2, p2t = stats.spearmanr(v2a, v2b)

    if sign_tj > 0:
        if rho1 > 0 and (p1t / 2 if rho1 > 0 else 1 - p1t / 2) < 0.05:
            n1_p1_count += 1
    else:
        if rho1 < 0 and (p1t / 2 if rho1 < 0 else 1 - p1t / 2) < 0.05:
            n1_p1_count += 1

    if sign_mj > 0:
        if rho2 > 0 and (p2t / 2 if rho2 > 0 else 1 - p2t / 2) < 0.05:
            n1_p2_count += 1
    else:
        if rho2 < 0 and (p2t / 2 if rho2 < 0 else 1 - p2t / 2) < 0.05:
            n1_p2_count += 1

d2_n1 = {'P1_frac': n1_p1_count / N_SHUFFLES, 'P2_frac': n1_p2_count / N_SHUFFLES}

print(f'\nExploratory:')
print(f'  D1: Kruskal-Wallis across subsets:')
for feat, r in d1_results.items():
    print(f'    {feat}: H={r["H"]:.2f} p={r["p"]:.4f}')
print(f'  D2: Per-prediction N1 pass fractions:')
print(f'    P1: {d2_n1["P1_frac"]:.4f}  P2: {d2_n1["P2_frac"]:.4f}')

results['exploratory'] = {
    'D1_kruskal_wallis': d1_results,
    'D2_per_prediction_n1': d2_n1,
}

# ── 12. Verdict determination ────────────────────────────────────────
if layer_b_active:
    if n1_pass and n2_pass:
        K_ctrl = K
    else:
        K_ctrl = 0

    if not c1b_pass:
        # A1 anchor failed — all Layer B results are exploratory
        if K_ctrl >= 2:
            verdict = 'FRAMEWORK_MARGINAL_TRANSFER_OBSERVED'
        elif K_ctrl >= 1:
            verdict = 'FRAMEWORK_MARGINAL'
        else:
            verdict = 'FRAMEWORK_MARGINAL'
    elif K_ctrl >= 2:
        verdict = 'COVARIATE_TRANSFER_CONFIRMED'
    elif K_ctrl == 1:
        verdict = 'PARTIAL_TRANSFER'
    else:
        verdict = 'ANCHOR_ONLY'
else:
    K_ctrl = 0
    if not c1b_pass:
        verdict = 'FRAMEWORK_MARGINAL'
    else:
        verdict = 'ANCHOR_ONLY'

print(f'\n{"="*60}')
print(f'A1: {"PASS" if a1_pass else "FAIL"} (rho={rho_a1:.4f})')
print(f'Layer B active: {layer_b_active} (S_T variant={s_t_variant}, n={len(s_t)})')
print(f'K={K} (P1={"PASS" if p1_pass else "FAIL"}, P2={"PASS" if p2_pass else "FAIL"})')
print(f'N1={"PASS" if n1_pass else "FAIL"} (frac={n1_frac:.4f})')
print(f'N2={"PASS" if n2_pass else "FAIL"} (frac={n2_frac:.4f})')
print(f'K_ctrl={K_ctrl}')
print(f'\nVerdict: {verdict}')
print(f'{"="*60}')

results['K_ctrl'] = K_ctrl
results['verdict'] = verdict

# ── 13. Write results ────────────────────────────────────────────────
def convert_numpy(obj):
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, bool):
        return bool(obj)
    return obj

results = convert_numpy(results)
out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results',
                        'typed_subset_alignment_results.json')
json.dump(results, open(out_path, 'w'), indent=2)
print(f'\nResults written to {out_path}')
