"""
Phase 618: PREFIX Composition Determinants
Tests what determines folio-level PREFIX composition: section, REGIME,
kernel fractions, or irreducible folio-level design freedom.

Blocks:
  A: Section effect on PREFIX composition (KW tests, eta-squared)
  B: REGIME effect (overall, within-section, continuous kernel correlations)
  C: Hierarchical variance decomposition (LOO R2)
  D: Residual PREFIX -> manifold (6 partial Mantel tests)
  E: Within-folio paragraph PREFIX diversity (ICC, JSD ratio)
  F: Verdict

Produces: prefix_composition_determinants.json
"""
import sys; sys.path.insert(0, '.')
import json
import time
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.spatial.distance import pdist, squareform, jensenshannon
from scipy.stats import spearmanr, kruskal
from numpy.linalg import lstsq
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut
from collections import Counter, defaultdict
from scripts.voynich import Transcript, Morphology

t0 = time.time()
PROJECT_ROOT = Path('.')
tx = Transcript()
morph = Morphology()

SECTION_MAP = {'S': 'Stars', 'B': 'Bio', 'H': 'Herbal', 'T': 'Cosmo', 'C': 'Cosmo'}
MAJOR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'da', 'ol', 'or',
                  'pch', 'tch', 'lch', 'ar', 'al', 'BARE']
MANIFOLD_PCS = ['PC1', 'PC2', 'PC3', 'PC4', 'PC5']

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def mantel_test(dist_a, dist_b, n_perms=10000, seed=42):
    """Mantel test with z-score."""
    rng = np.random.default_rng(seed)
    n = dist_a.shape[0]
    idx = np.triu_indices(n, k=1)
    a_flat = dist_a[idx]
    b_flat = dist_b[idx]
    r_obs = float(np.corrcoef(a_flat, b_flat)[0, 1])
    r_nulls = np.empty(n_perms)
    for p in range(n_perms):
        perm = rng.permutation(n)
        b_perm = dist_b[np.ix_(perm, perm)]
        r_nulls[p] = np.corrcoef(a_flat, b_perm[idx])[0, 1]
    p_val = float((np.sum(r_nulls >= r_obs) + 1) / (n_perms + 1))
    z = float((r_obs - r_nulls.mean()) / (r_nulls.std() + 1e-10))
    return r_obs, p_val, z, float(r_nulls.mean()), float(r_nulls.std())


def partial_mantel(dist_a, dist_b, control_dists, n_perms=10000, seed=42):
    """Partial Mantel via OLS residualization."""
    n = dist_a.shape[0]
    idx = np.triu_indices(n, k=1)
    a_flat = dist_a[idx]
    b_flat = dist_b[idx]
    controls = np.column_stack([cd[idx] for cd in control_dists])
    A_mat = np.column_stack([controls, np.ones(len(a_flat))])
    res_a = a_flat - A_mat @ lstsq(A_mat, a_flat, rcond=None)[0]
    res_b = b_flat - A_mat @ lstsq(A_mat, b_flat, rcond=None)[0]
    r_obs = float(np.corrcoef(res_a, res_b)[0, 1])
    rng = np.random.default_rng(seed)
    r_nulls = np.empty(n_perms)
    for p in range(n_perms):
        perm = rng.permutation(len(res_a))
        r_nulls[p] = np.corrcoef(res_a, res_b[perm])[0, 1]
    p_val = float((np.sum(r_nulls >= r_obs) + 1) / (n_perms + 1))
    z = float((r_obs - r_nulls.mean()) / (r_nulls.std() + 1e-10))
    return r_obs, p_val, z


def loo_r2(X, y):
    """Leave-one-out cross-validated R2."""
    n = len(y)
    if X.shape[1] == 0:
        return 0.0
    preds = np.zeros(n)
    loo = LeaveOneOut()
    for train_idx, test_idx in loo.split(X):
        lr = LinearRegression()
        lr.fit(X[train_idx], y[train_idx])
        preds[test_idx] = lr.predict(X[test_idx])
    ss_res = np.sum((y - preds) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0


def train_r2(X, y):
    """Training R2 (for gap comparison with LOO)."""
    if X.shape[1] == 0:
        return 0.0
    lr = LinearRegression().fit(X, y)
    preds = lr.predict(X)
    ss_res = np.sum((y - preds) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0


def icc_one_way(groups):
    """ICC(1,1) one-way random effects."""
    valid = [g for g in groups if len(g) > 0]
    k = len(valid)
    if k < 2:
        return 0.0
    ns = [len(g) for g in valid]
    N = sum(ns)
    if N < k + 1:
        return 0.0
    grand_mean = sum(x for g in valid for x in g) / N
    ms_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in valid) / (k - 1)
    ss_within = sum((x - np.mean(g)) ** 2 for g in valid for x in g)
    df_within = N - k
    if df_within <= 0:
        return 0.0
    ms_within = ss_within / df_within
    n0 = (N - sum(n ** 2 for n in ns) / N) / (k - 1)
    if n0 < 1:
        n0 = 1
    denom = ms_between + (n0 - 1) * ms_within
    return float((ms_between - ms_within) / denom) if denom > 0 else 0.0


# ============================================================
# DATA LOADING
# ============================================================
print('Loading data...')

# REGIME assignments
regime_path = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path) as f:
    regime_data = json.load(f)
folio_to_regime = {f: v['regime'] for f, v in regime_data['regime_assignments'].items()}

# Manifold PC scores
mani_path = (PROJECT_ROOT / 'phases' / 'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS'
             / 'results' / 't1_manifold_embedding.json')
with open(mani_path) as f:
    mani_data = json.load(f)
manifold_scores = mani_data['space_A']['folio_scores']

# Operational profiles (for k/h/e ratios)
ops_path = PROJECT_ROOT / 'results' / 'folio_operational_profiles.json'
with open(ops_path) as f:
    ops_data = json.load(f)
ops_profiles = {p['folio']: p for p in ops_data['profiles']}

# ============================================================
# BUILD PER-FOLIO PREFIX FRACTIONS
# ============================================================
print('\nBuilding per-folio PREFIX fractions...')

folio_tokens = defaultdict(list)
folio_sections = {}
folio_headless_counts = defaultdict(lambda: [0, 0])  # [headless, total]

for tok in tx.currier_b():
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    if tok.placement.startswith('L'):
        continue
    folio_tokens[tok.folio].append(w)
    if tok.folio not in folio_sections:
        folio_sections[tok.folio] = SECTION_MAP.get(tok.section, tok.section)
    # Track headless
    m = morph.extract(w)
    folio_headless_counts[tok.folio][1] += 1
    if m.middle and not m.prefix and m.has_articulator is False:
        folio_headless_counts[tok.folio][0] += 1

# Compute per-folio PREFIX fractions
folio_prefix_fracs = {}
folio_prefix_counts = {}
total_covered = 0
total_tokens_all = 0

for fid, words in folio_tokens.items():
    pfx_counts = Counter()
    for w in words:
        m = morph.extract(w)
        pfx = m.prefix if m.prefix else 'BARE'
        pfx_counts[pfx] += 1
    total = sum(pfx_counts.values())
    major_total = sum(pfx_counts.get(p, 0) for p in MAJOR_PREFIXES)
    total_covered += major_total
    total_tokens_all += total
    folio_prefix_fracs[fid] = {p: pfx_counts.get(p, 0) / total for p in MAJOR_PREFIXES}
    folio_prefix_counts[fid] = dict(pfx_counts)

# Headless fractions
folio_headless_frac = {}
for fid in folio_prefix_fracs:
    hl, tot = folio_headless_counts[fid]
    folio_headless_frac[fid] = hl / tot if tot > 0 else 0

# Kernel fractions
folio_kernel = {}
for fid in folio_prefix_fracs:
    if fid in ops_profiles:
        p = ops_profiles[fid]
        folio_kernel[fid] = {
            'k_ratio': p['k_ratio'], 'h_ratio': p['h_ratio'], 'e_ratio': p['e_ratio']
        }

coverage = total_covered / total_tokens_all if total_tokens_all > 0 else 0
n_folios = len(folio_prefix_fracs)
print(f'  {n_folios} B-folios, {total_tokens_all} tokens')
print(f'  Major PREFIX coverage: {coverage:.1%}')

results = {
    'metadata': {
        'phase': 618,
        'phase_name': 'PREFIX_COMPOSITION_DETERMINANTS',
        'n_folios': n_folios,
        'n_tokens': total_tokens_all,
        'prefix_coverage': round(coverage, 4),
        'major_prefixes': MAJOR_PREFIXES,
    }
}

# ============================================================
# BLOCK A: Section Effect on PREFIX Composition
# ============================================================
print('\n' + '=' * 60)
print('BLOCK A: Section Effect on PREFIX Composition')

# Section counts
sec_counts = Counter(folio_sections[f] for f in folio_prefix_fracs)
viable_sections = sorted(s for s, c in sec_counts.items() if c >= 5)
print(f'  Sections: {dict(sec_counts)}')
print(f'  Viable (n>=5): {viable_sections}')

# Section mean profiles
sec_profiles = {}
for sec in viable_sections:
    fids = [f for f in folio_prefix_fracs if folio_sections.get(f) == sec]
    profile = {}
    for pfx in MAJOR_PREFIXES:
        vals = [folio_prefix_fracs[f][pfx] for f in fids]
        profile[pfx] = round(float(np.mean(vals)), 4)
    sec_profiles[sec] = profile

# KW tests
kw_results = {}
for pfx in MAJOR_PREFIXES:
    groups = []
    for sec in viable_sections:
        vals = [folio_prefix_fracs[f][pfx] for f in folio_prefix_fracs
                if folio_sections.get(f) == sec]
        groups.append(vals)
    if all(len(g) >= 2 for g in groups):
        H_stat, p_val = kruskal(*groups)
        N = sum(len(g) for g in groups)
        eta2 = (H_stat - len(groups) + 1) / (N - 1)
    else:
        H_stat, p_val, eta2 = 0, 1, 0
    kw_results[pfx] = {'H': round(H_stat, 2), 'p': round(p_val, 6), 'eta2': round(eta2, 4)}

mean_eta2 = float(np.mean([v['eta2'] for v in kw_results.values()]))
sig_count = sum(1 for v in kw_results.values() if v['p'] < 0.05)

print(f'\n  KW tests (section -> PREFIX):')
print(f'  {"PREFIX":<8} {"H":>8} {"p":>10} {"eta2":>8}')
for pfx in MAJOR_PREFIXES:
    r = kw_results[pfx]
    marker = '*' if r['p'] < 0.05 else ' '
    print(f'  {pfx:<8} {r["H"]:8.2f} {r["p"]:10.6f} {r["eta2"]:8.4f} {marker}')
print(f'  Mean eta2: {mean_eta2:.4f}, {sig_count}/{len(MAJOR_PREFIXES)} significant')

print(f'\n  Section mean profiles:')
print(f'  {"Section":<10}', end='')
for pfx in ['qo', 'ch', 'sh', 'ok', 'ot', 'da', 'ol', 'BARE']:
    print(f' {pfx:>6}', end='')
print()
for sec in viable_sections:
    print(f'  {sec:<10}', end='')
    for pfx in ['qo', 'ch', 'sh', 'ok', 'ot', 'da', 'ol', 'BARE']:
        print(f' {sec_profiles[sec][pfx]:6.3f}', end='')
    print()

results['block_A'] = {
    'section_counts': dict(sec_counts),
    'viable_sections': viable_sections,
    'kw_tests': kw_results,
    'mean_eta2': round(mean_eta2, 4),
    'n_significant': sig_count,
    'section_profiles': sec_profiles,
}
print(f'\n  Block A complete ({time.time()-t0:.1f}s)')

# ============================================================
# BLOCK B: REGIME Effect
# ============================================================
print('\n' + '=' * 60)
print('BLOCK B: REGIME Effect')

# Overall REGIME -> PREFIX
regime_kw = {}
for pfx in MAJOR_PREFIXES:
    rgroups = defaultdict(list)
    for f in folio_prefix_fracs:
        r = folio_to_regime.get(f)
        if r:
            rgroups[r].append(folio_prefix_fracs[f][pfx])
    valid_groups = [v for v in rgroups.values() if len(v) >= 2]
    if len(valid_groups) >= 2:
        H_stat, p_val = kruskal(*valid_groups)
        N = sum(len(g) for g in valid_groups)
        eta2 = (H_stat - len(valid_groups) + 1) / (N - 1)
    else:
        H_stat, p_val, eta2 = 0, 1, 0
    regime_kw[pfx] = {'H': round(H_stat, 2), 'p': round(p_val, 6), 'eta2': round(eta2, 4)}

regime_sig = sum(1 for v in regime_kw.values() if v['p'] < 0.05)
regime_mean_eta2 = float(np.mean([v['eta2'] for v in regime_kw.values()]))
print(f'  Overall REGIME -> PREFIX: {regime_sig}/{len(MAJOR_PREFIXES)} sig, mean eta2={regime_mean_eta2:.4f}')

# Within-Herbal
herbal_fids = [f for f in folio_prefix_fracs if folio_sections.get(f) == 'Herbal']
herbal_regimes = Counter(folio_to_regime.get(f) for f in herbal_fids)
print(f'  Within-Herbal: n={len(herbal_fids)}, REGIMEs={dict(herbal_regimes)}')

herbal_kw = {}
for pfx in MAJOR_PREFIXES:
    rgroups = defaultdict(list)
    for f in herbal_fids:
        r = folio_to_regime.get(f)
        if r:
            rgroups[r].append(folio_prefix_fracs[f][pfx])
    valid_groups = [v for v in rgroups.values() if len(v) >= 3]
    if len(valid_groups) >= 2:
        H_stat, p_val = kruskal(*valid_groups)
        N = sum(len(g) for g in valid_groups)
        eta2 = (H_stat - len(valid_groups) + 1) / (N - 1)
    else:
        H_stat, p_val, eta2 = 0, 1, 0
    herbal_kw[pfx] = {'H': round(H_stat, 2), 'p': round(p_val, 6), 'eta2': round(eta2, 4)}

herbal_sig = sum(1 for v in herbal_kw.values() if v['p'] < 0.05)
print(f'  Within-Herbal: {herbal_sig}/{len(MAJOR_PREFIXES)} sig')

# Within-Stars
stars_fids = [f for f in folio_prefix_fracs if folio_sections.get(f) == 'Stars']
stars_regimes = Counter(folio_to_regime.get(f) for f in stars_fids)
print(f'  Within-Stars: n={len(stars_fids)}, REGIMEs={dict(stars_regimes)}')

stars_kw = {}
for pfx in MAJOR_PREFIXES:
    rgroups = defaultdict(list)
    for f in stars_fids:
        r = folio_to_regime.get(f)
        if r:
            rgroups[r].append(folio_prefix_fracs[f][pfx])
    valid_groups = [v for v in rgroups.values() if len(v) >= 3]
    if len(valid_groups) >= 2:
        H_stat, p_val = kruskal(*valid_groups)
        N = sum(len(g) for g in valid_groups)
        eta2 = (H_stat - len(valid_groups) + 1) / (N - 1)
    else:
        H_stat, p_val, eta2 = 0, 1, 0
    stars_kw[pfx] = {'H': round(H_stat, 2), 'p': round(p_val, 6), 'eta2': round(eta2, 4)}

stars_sig = sum(1 for v in stars_kw.values() if v['p'] < 0.05)
print(f'  Within-Stars: {stars_sig}/{len(MAJOR_PREFIXES)} sig')

# Continuous: kernel + headless correlations with PREFIX fractions
common_kernel = sorted(set(folio_prefix_fracs.keys()) & set(folio_kernel.keys()))
continuous_vars = ['k_ratio', 'h_ratio', 'e_ratio', 'headless_frac']
kernel_corr = {}
for pfx in MAJOR_PREFIXES:
    pfx_vals = np.array([folio_prefix_fracs[f][pfx] for f in common_kernel])
    for cv in continuous_vars:
        if cv == 'headless_frac':
            cv_vals = np.array([folio_headless_frac[f] for f in common_kernel])
        else:
            cv_vals = np.array([folio_kernel[f][cv] for f in common_kernel])
        rho, p = spearmanr(pfx_vals, cv_vals)
        kernel_corr[f'{pfx}_vs_{cv}'] = {'rho': round(float(rho), 4), 'p': round(float(p), 6)}

# Print top correlations
print(f'\n  Top kernel/headless correlations (|rho| > 0.3):')
for key, val in sorted(kernel_corr.items(), key=lambda x: -abs(x[1]['rho'])):
    if abs(val['rho']) > 0.3:
        print(f'    {key:<25} rho={val["rho"]:+.4f}  p={val["p"]:.6f}')

results['block_B'] = {
    'overall_regime_kw': regime_kw,
    'overall_mean_eta2': round(regime_mean_eta2, 4),
    'overall_n_sig': regime_sig,
    'within_herbal': {'n': len(herbal_fids), 'regimes': dict(herbal_regimes),
                      'kw': herbal_kw, 'n_sig': herbal_sig},
    'within_stars': {'n': len(stars_fids), 'regimes': dict(stars_regimes),
                     'kw': stars_kw, 'n_sig': stars_sig},
    'kernel_correlations': kernel_corr,
}
print(f'\n  Block B complete ({time.time()-t0:.1f}s)')

# ============================================================
# BLOCK C: Hierarchical Variance Decomposition
# ============================================================
print('\n' + '=' * 60)
print('BLOCK C: Hierarchical Variance Decomposition')

folio_list_c = sorted(f for f in folio_prefix_fracs
                      if f in folio_to_regime and f in folio_kernel)
n_c = len(folio_list_c)
print(f'  Folios for decomposition: {n_c}')

# Section dummies
sections_c = [folio_sections[f] for f in folio_list_c]
unique_secs = sorted(set(sections_c))
sec_dummies = np.zeros((n_c, len(unique_secs) - 1))
for i, sec in enumerate(sections_c):
    idx = unique_secs.index(sec)
    if idx > 0:
        sec_dummies[i, idx - 1] = 1

# REGIME dummies
regimes_c = [folio_to_regime[f] for f in folio_list_c]
unique_regs = sorted(set(regimes_c))
reg_dummies = np.zeros((n_c, len(unique_regs) - 1))
for i, reg in enumerate(regimes_c):
    idx = unique_regs.index(reg)
    if idx > 0:
        reg_dummies[i, idx - 1] = 1

# Kernel + headless continuous
kernel_headless = np.array([
    [folio_kernel[f]['k_ratio'], folio_kernel[f]['h_ratio'],
     folio_kernel[f]['e_ratio'], folio_headless_frac[f]]
    for f in folio_list_c
])

# Design matrices
X_sec = sec_dummies
X_sec_reg = np.hstack([sec_dummies, reg_dummies])
X_sec_reg_kh = np.hstack([sec_dummies, reg_dummies, kernel_headless])

print(f'  Predictors: section={X_sec.shape[1]}, +REGIME={X_sec_reg.shape[1]}, +kernel+headless={X_sec_reg_kh.shape[1]}')

# Per-PREFIX LOO R2
block_c = {}
for pfx in MAJOR_PREFIXES:
    y = np.array([folio_prefix_fracs[f][pfx] for f in folio_list_c])
    r2_s_loo = loo_r2(X_sec, y)
    r2_sr_loo = loo_r2(X_sec_reg, y)
    r2_srk_loo = loo_r2(X_sec_reg_kh, y)
    r2_s_train = train_r2(X_sec, y)
    r2_sr_train = train_r2(X_sec_reg, y)
    r2_srk_train = train_r2(X_sec_reg_kh, y)
    block_c[pfx] = {
        'loo_section': round(r2_s_loo, 4),
        'loo_sec_regime': round(r2_sr_loo, 4),
        'loo_sec_reg_kernel_headless': round(r2_srk_loo, 4),
        'train_section': round(r2_s_train, 4),
        'train_sec_regime': round(r2_sr_train, 4),
        'train_sec_reg_kernel_headless': round(r2_srk_train, 4),
    }

# Mean across PREFIXes
mean_loo_sec = float(np.mean([v['loo_section'] for v in block_c.values()]))
mean_loo_sr = float(np.mean([v['loo_sec_regime'] for v in block_c.values()]))
mean_loo_srk = float(np.mean([v['loo_sec_reg_kernel_headless'] for v in block_c.values()]))

print(f'\n  {"PREFIX":<8} {"LOO sec":>10} {"LOO s+r":>10} {"LOO s+r+k":>10} {"Train s+r+k":>12}')
for pfx in MAJOR_PREFIXES:
    c = block_c[pfx]
    print(f'  {pfx:<8} {c["loo_section"]:10.4f} {c["loo_sec_regime"]:10.4f} '
          f'{c["loo_sec_reg_kernel_headless"]:10.4f} {c["train_sec_reg_kernel_headless"]:12.4f}')
print(f'  {"MEAN":<8} {mean_loo_sec:10.4f} {mean_loo_sr:10.4f} {mean_loo_srk:10.4f}')

results['block_C'] = {
    'per_prefix': block_c,
    'mean_loo_section': round(mean_loo_sec, 4),
    'mean_loo_sec_regime': round(mean_loo_sr, 4),
    'mean_loo_sec_reg_kernel_headless': round(mean_loo_srk, 4),
    'n_folios': n_c,
    'n_predictors': {'section': X_sec.shape[1], 'sec_regime': X_sec_reg.shape[1],
                     'sec_reg_kernel_headless': X_sec_reg_kh.shape[1]},
}
print(f'\n  Block C complete ({time.time()-t0:.1f}s)')

# ============================================================
# BLOCK D: Residual PREFIX -> Manifold (Partial Mantel)
# ============================================================
print('\n' + '=' * 60)
print('BLOCK D: Residual PREFIX -> Manifold (Partial Mantel)')

common_d = sorted(set(folio_prefix_fracs.keys()) & set(manifold_scores.keys())
                  & set(folio_to_regime.keys()) & set(folio_kernel.keys()))
n_d = len(common_d)
print(f'  Common folios (manifold-eligible): {n_d}')

# 1. PREFIX JSD distance
pfx_vectors = []
for f in common_d:
    vec = np.array([folio_prefix_fracs[f].get(p, 0) for p in MAJOR_PREFIXES])
    vec = vec + 1e-10
    vec = vec / vec.sum()
    pfx_vectors.append(vec)
D_prefix = squareform(pdist(np.array(pfx_vectors), jensenshannon))

# 2. Manifold Euclidean distance
manifold_matrix = np.array([[manifold_scores[f][pc] for pc in MANIFOLD_PCS]
                             for f in common_d])
D_manifold = squareform(pdist(manifold_matrix, 'euclidean'))

# 3. Section binary distance
sections_d = [folio_sections[f] for f in common_d]
D_section = np.zeros((n_d, n_d))
for i in range(n_d):
    for j in range(n_d):
        D_section[i, j] = 0 if sections_d[i] == sections_d[j] else 1

# 4. REGIME binary distance
regimes_d = [folio_to_regime[f] for f in common_d]
D_regime = np.zeros((n_d, n_d))
for i in range(n_d):
    for j in range(n_d):
        D_regime[i, j] = 0 if regimes_d[i] == regimes_d[j] else 1

# 5. Kernel+headless Euclidean distance
kh_vecs = np.array([
    [folio_kernel[f]['k_ratio'], folio_kernel[f]['h_ratio'],
     folio_kernel[f]['e_ratio'], folio_headless_frac[f]]
    for f in common_d
])
D_kernel_headless = squareform(pdist(kh_vecs, 'euclidean'))

# Run 6 Mantel tests
print('  Running Mantel tests (10000 perms each)...')

r_d1, p_d1, z_d1, _, _ = mantel_test(D_prefix, D_manifold)
print(f'  D1 PREFIX->manifold (raw):         r={r_d1:.4f}, p={p_d1:.6f}, z={z_d1:.2f}')

r_d2, p_d2, z_d2 = partial_mantel(D_prefix, D_manifold, [D_section])
print(f'  D2 PREFIX|section:                  r={r_d2:.4f}, p={p_d2:.6f}, z={z_d2:.2f}  ret={r_d2/r_d1:.1%}')

r_d3, p_d3, z_d3 = partial_mantel(D_prefix, D_manifold, [D_regime])
print(f'  D3 PREFIX|REGIME:                   r={r_d3:.4f}, p={p_d3:.6f}, z={z_d3:.2f}  ret={r_d3/r_d1:.1%}')

r_d4, p_d4, z_d4 = partial_mantel(D_prefix, D_manifold, [D_section, D_regime])
print(f'  D4 PREFIX|section+REGIME:           r={r_d4:.4f}, p={p_d4:.6f}, z={z_d4:.2f}  ret={r_d4/r_d1:.1%}')

r_d5, p_d5, z_d5 = partial_mantel(D_prefix, D_manifold, [D_kernel_headless])
print(f'  D5 PREFIX|kernel+headless:          r={r_d5:.4f}, p={p_d5:.6f}, z={z_d5:.2f}  ret={r_d5/r_d1:.1%}')

r_d6, p_d6, z_d6 = partial_mantel(D_prefix, D_manifold, [D_section, D_regime, D_kernel_headless])
print(f'  D6 PREFIX|sec+reg+kernel+headless:  r={r_d6:.4f}, p={p_d6:.6f}, z={z_d6:.2f}  ret={r_d6/r_d1:.1%}')

results['block_D'] = {
    'n_folios': n_d,
    'n_perms': 10000,
    'D1': {'r': round(r_d1, 4), 'p': round(p_d1, 6), 'z': round(z_d1, 2)},
    'D2': {'r': round(r_d2, 4), 'p': round(p_d2, 6), 'z': round(z_d2, 2),
           'retention': round(r_d2 / r_d1, 4) if r_d1 > 0 else 0},
    'D3': {'r': round(r_d3, 4), 'p': round(p_d3, 6), 'z': round(z_d3, 2),
           'retention': round(r_d3 / r_d1, 4) if r_d1 > 0 else 0},
    'D4': {'r': round(r_d4, 4), 'p': round(p_d4, 6), 'z': round(z_d4, 2),
           'retention': round(r_d4 / r_d1, 4) if r_d1 > 0 else 0},
    'D5': {'r': round(r_d5, 4), 'p': round(p_d5, 6), 'z': round(z_d5, 2),
           'retention': round(r_d5 / r_d1, 4) if r_d1 > 0 else 0},
    'D6': {'r': round(r_d6, 4), 'p': round(p_d6, 6), 'z': round(z_d6, 2),
           'retention': round(r_d6 / r_d1, 4) if r_d1 > 0 else 0},
}
print(f'\n  Block D complete ({time.time()-t0:.1f}s)')

# ============================================================
# BLOCK E: Within-Folio Paragraph PREFIX Diversity
# ============================================================
print('\n' + '=' * 60)
print('BLOCK E: Within-Folio Paragraph PREFIX Diversity')

# Build paragraphs
by_folio = defaultdict(list)
for tok in tx.currier_b():
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    if tok.placement.startswith('L'):
        continue
    by_folio[tok.folio].append(tok)

para_prefix_data = []
for fid in sorted(by_folio.keys()):
    toks = by_folio[fid]
    paras = []
    current = []
    for t in toks:
        if t.par_initial and current:
            paras.append(current)
            current = [t]
        else:
            current.append(t)
    if current:
        paras.append(current)

    for pi, ptoks in enumerate(paras):
        n_lines = len(set(t.line for t in ptoks))
        if n_lines < 3:
            continue
        pfx_counts = Counter()
        for t in ptoks:
            w = t.word.strip()
            m = morph.extract(w)
            pfx = m.prefix if m.prefix else 'BARE'
            pfx_counts[pfx] += 1
        n = sum(pfx_counts.values())
        if n < 5:
            continue
        fracs = {p: pfx_counts.get(p, 0) / n for p in MAJOR_PREFIXES}
        para_prefix_data.append({'folio': fid, 'para_idx': pi, 'fracs': fracs, 'n': n})

# Group by folio
folio_para_groups = defaultdict(list)
for rec in para_prefix_data:
    folio_para_groups[rec['folio']].append(rec)

multi_folios = {f: recs for f, recs in folio_para_groups.items() if len(recs) >= 2}
print(f'  Qualifying paragraphs: {len(para_prefix_data)}')
print(f'  Folios with >=2 paragraphs: {len(multi_folios)}')

# ICC per PREFIX
icc_results = {}
for pfx in MAJOR_PREFIXES:
    groups = [
        [r['fracs'][pfx] for r in recs]
        for f, recs in multi_folios.items()
    ]
    icc_val = icc_one_way(groups)
    icc_results[pfx] = round(icc_val, 4)

mean_icc = float(np.mean(list(icc_results.values())))
print(f'\n  ICC per PREFIX (C1182 sister ICC=0.317):')
for pfx in MAJOR_PREFIXES:
    marker = '*' if icc_results[pfx] > 0.317 else ' '
    print(f'    {pfx:<8} ICC={icc_results[pfx]:.4f} {marker}')
print(f'  Mean ICC: {mean_icc:.4f}')

# Within-folio vs between-folio JSD
within_jsds = []
for fid, recs in multi_folios.items():
    vecs = []
    for r in recs:
        v = np.array([r['fracs'][p] for p in MAJOR_PREFIXES]) + 1e-10
        vecs.append(v / v.sum())
    for i in range(len(vecs)):
        for j in range(i + 1, len(vecs)):
            within_jsds.append(float(jensenshannon(vecs[i], vecs[j])))

# Between-folio JSD from Block D distance matrix (upper triangle)
between_jsds = []
if n_d > 1:
    idx_bt = np.triu_indices(n_d, k=1)
    between_jsds = D_prefix[idx_bt].tolist()

within_mean = float(np.mean(within_jsds)) if within_jsds else 0
between_mean = float(np.mean(between_jsds)) if between_jsds else 0
jsd_ratio = within_mean / between_mean if between_mean > 0 else 0

print(f'\n  Within-folio JSD mean: {within_mean:.4f} (n={len(within_jsds)})')
print(f'  Between-folio JSD mean: {between_mean:.4f} (n={len(between_jsds)})')
print(f'  Ratio (within/between): {jsd_ratio:.4f}')
if jsd_ratio < 0.5:
    jsd_interp = 'FOLIO_TEMPLATE'
elif jsd_ratio < 0.8:
    jsd_interp = 'MODERATE_CONSTRAINT'
else:
    jsd_interp = 'PARAGRAPH_CHOICE'
print(f'  Interpretation: {jsd_interp}')

results['block_E'] = {
    'n_paragraphs': len(para_prefix_data),
    'n_folios_multi_para': len(multi_folios),
    'icc_per_prefix': icc_results,
    'mean_icc': round(mean_icc, 4),
    'c1182_sister_icc': 0.317,
    'within_jsd_mean': round(within_mean, 4),
    'between_jsd_mean': round(between_mean, 4),
    'jsd_ratio': round(jsd_ratio, 4),
    'interpretation': jsd_interp,
}
print(f'\n  Block E complete ({time.time()-t0:.1f}s)')

# ============================================================
# BLOCK F: Verdict
# ============================================================
print('\n' + '=' * 60)
print('VERDICT')

# Criterion 1: How much variance explained?
mean_r2 = mean_loo_srk  # section + REGIME + kernel + headless

# Criterion 2: Does residual PREFIX predict manifold?
residual_r = r_d6
residual_p = p_d6
residual_sig = residual_r > 0.10 and residual_p < 0.05

# Criterion 3: Kernel+headless mediation
kernel_retention = r_d5 / r_d1 if r_d1 > 0 else 0
kernel_mediated = kernel_retention < 0.50

# Primary verdict
if mean_r2 > 0.70:
    if residual_sig:
        verdict = 'MOSTLY_DETERMINED_WITH_RESIDUAL'
    else:
        verdict = 'SECTION_REGIME_PROXY'
elif mean_r2 > 0.30:
    if residual_sig:
        verdict = 'PARTIAL_WITH_INDEPENDENT_SIGNAL'
    else:
        verdict = 'PARTIAL_NO_INDEPENDENT_SIGNAL'
else:
    if residual_sig:
        verdict = 'FOLIO_DESIGN_FREEDOM'
    else:
        verdict = 'UNSTRUCTURED'

# Modifier
if kernel_mediated:
    verdict_full = f'{verdict} (kernel-mediated)'
else:
    verdict_full = verdict

print(f'\n  VERDICT: {verdict_full}')
print(f'  Mean LOO R2 (sec+reg+kernel+headless): {mean_r2:.4f}')
print(f'  Residual Mantel (D6): r={residual_r:.4f}, p={residual_p:.6f}, sig={residual_sig}')
print(f'  Kernel+headless retention (D5): {kernel_retention:.4f}, mediated={kernel_mediated}')
print(f'  Mean ICC: {mean_icc:.4f}')
print(f'  JSD ratio: {jsd_ratio:.4f} ({jsd_interp})')

results['verdict'] = {
    'verdict': verdict_full,
    'mean_loo_r2': round(mean_r2, 4),
    'residual_mantel_r': round(residual_r, 4),
    'residual_mantel_p': round(residual_p, 6),
    'residual_significant': residual_sig,
    'kernel_retention': round(kernel_retention, 4),
    'kernel_mediated': kernel_mediated,
    'mean_icc': round(mean_icc, 4),
    'jsd_ratio': round(jsd_ratio, 4),
}

# Save
runtime = round(time.time() - t0, 1)
results['metadata']['runtime_s'] = runtime
out_path = (PROJECT_ROOT / 'phases' / 'PREFIX_COMPOSITION_DETERMINANTS'
            / 'results' / 'prefix_composition_determinants.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f'\nResults saved to {out_path}')
print(f'Total runtime: {runtime}s')
