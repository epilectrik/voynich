"""
Phase 601: SAFETY_STYLE_MODERATION
Tests whether A2-like apparatus forgivingness/authenticity regime shifts safety
style toward transformative intervention (ii) over preventive stabilization (e->y).

Core mechanistic test: does mean_null_dye (apparatus forgivingness) explain
within-REGIME safety_balance variance in Herbal?

Pre-registration hash: f485ef57f69b453511a3ab45cb1f9e6992098bf18ccb8b4f219b2c7567689a58
"""

import json
import os
import sys
import hashlib
import time
from collections import Counter, defaultdict

import numpy as np
from numpy.linalg import lstsq
from scipy.stats import spearmanr, mannwhitneyu
import scipy.stats as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology, decompose_middle_hmt


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        return super().default(obj)


# ============================================================
# 1. PRE-REGISTRATION VERIFICATION
# ============================================================

PRED_PATH = os.path.join(os.path.dirname(__file__), '..', 'PREDICTIONS.md')
PRED_HASH = 'f485ef57f69b453511a3ab45cb1f9e6992098bf18ccb8b4f219b2c7567689a58'

pred_hash = hashlib.sha256(open(PRED_PATH, 'rb').read()).hexdigest()
assert pred_hash == PRED_HASH, f"PREDICTIONS.md hash mismatch: {pred_hash}"
print(f"Pre-registration verified: {PRED_HASH[:16]}...")

t0 = time.time()


# ============================================================
# 2. DATA LOADING
# ============================================================

print("\n=== DATA LOADING ===")

BASE = os.path.join(os.path.dirname(__file__), '..', '..', '..')

# Opportunity normalization → mean_null_dye, profile, strong_close_fraction
opp_path = os.path.join(BASE, 'phases', 'A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES',
                        'results', 't0_opportunity_normalization.json')
with open(opp_path) as f:
    opp_data = json.load(f)
opp_cov = opp_data['covariates']
print(f"Opportunity normalization: {len(opp_cov)} folios")

folio_null_dye = {f: c['mean_null_dye'] for f, c in opp_cov.items()}
folio_profile = {f: c['profile'] for f, c in opp_cov.items()}
folio_scf = {f: c['strong_close_fraction'] for f, c in opp_cov.items()}

# Manifold → DYE_advantage, section, family
manifold_path = os.path.join(BASE, 'phases', 'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS',
                             'results', 't0_feature_matrix_assembly.json')
with open(manifold_path) as f:
    manifold_data = json.load(f)
manifold_folios = manifold_data['folios']
space_b_raw = manifold_data['space_B']['raw']
folio_metadata = manifold_data['folio_metadata']
folio_dye = {manifold_folios[i]: space_b_raw[i][0] for i in range(len(manifold_folios))}
print(f"Manifold: {len(manifold_folios)} folios")

# REGIME mapping
regime_path = os.path.join(BASE, 'data', 'regime_folio_mapping.json')
with open(regime_path) as f:
    regime_data = json.load(f)
regime_map = {f: info['regime'] for f, info in regime_data['regime_assignments'].items()}

# Section lookup
tx = Transcript()
folio_section = {}
for t in tx.currier_b():
    folio_section[t.folio] = t.section


# ============================================================
# 3. COMPUTE ey_rate, ii_rate, safety_balance
# ============================================================

print("\n=== COMPUTING SAFETY BALANCE ===")

morph = Morphology()

def max_consecutive_i(middle):
    max_run = current = 0
    for ch in middle:
        if ch == 'i':
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run

folio_token_counts = Counter()
folio_ey_counts = Counter()
folio_ii_counts = Counter()

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if token.placement.startswith('L'):
        continue
    folio = token.folio
    m = morph.extract(w)
    head, mods, term, frame = decompose_middle_hmt(m.middle)
    folio_token_counts[folio] += 1
    if head == 'e' and term == 'y':
        folio_ey_counts[folio] += 1
    if max_consecutive_i(m.middle) >= 2:
        folio_ii_counts[folio] += 1

folio_ey_rate = {f: folio_ey_counts[f] / folio_token_counts[f]
                 for f in folio_token_counts if folio_token_counts[f] > 0}
folio_ii_rate = {f: folio_ii_counts[f] / folio_token_counts[f]
                 for f in folio_token_counts if folio_token_counts[f] > 0}
folio_safety_bal = {f: folio_ey_rate[f] - folio_ii_rate[f] for f in folio_ey_rate}

mean_ey = np.mean(list(folio_ey_rate.values()))
mean_ii = np.mean(list(folio_ii_rate.values()))
print(f"Mean ey_rate: {mean_ey:.4f} (expected ~0.1377)")
print(f"Mean ii_rate: {mean_ii:.4f} (expected ~0.0717)")


# ============================================================
# 4. BUILD COMMON FOLIO SET
# ============================================================

common_folios = sorted(
    set(manifold_folios) & set(opp_cov.keys()) &
    set(folio_ey_rate.keys()) & set(regime_map.keys()) &
    set(folio_section.keys())
)
print(f"\nCommon folios: {len(common_folios)}")

# Verify section x REGIME x family composition
print("\n=== CELL COMPOSITION ===")
cell_folios = defaultdict(list)
for f in common_folios:
    sec = folio_section[f]
    reg = regime_map[f]
    prof = folio_profile.get(f, 'UNKNOWN')
    cell_folios[(sec, reg)].append((f, prof))

for key in sorted(cell_folios.keys()):
    members = cell_folios[key]
    profiles = [p for _, p in members]
    profile_counts = Counter(profiles)
    prof_str = ', '.join(f"{k.split('_')[0]}:{v}" for k, v in sorted(profile_counts.items()))
    print(f"  {key[0]}:{key[1]} n={len(members)} [{prof_str}]")


# ============================================================
# HELPER: Partial Spearman via residualization
# ============================================================

def partial_spearman(x, y, controls):
    """Partial Spearman correlation between x and y, controlling for controls matrix."""
    n = len(x)
    if n < 5:
        return 0.0, 1.0
    X_ctrl = np.column_stack([controls, np.ones(n)])
    beta_x, _, _, _ = lstsq(X_ctrl, x, rcond=None)
    x_resid = x - X_ctrl @ beta_x
    beta_y, _, _, _ = lstsq(X_ctrl, y, rcond=None)
    y_resid = y - X_ctrl @ beta_y
    if np.std(x_resid) < 1e-10 or np.std(y_resid) < 1e-10:
        return 0.0, 1.0
    rho, p = spearmanr(x_resid, y_resid)
    return float(rho), float(p)


def bootstrap_partial_spearman(x, y, controls, n_boot=5000, seed=42):
    """BCa bootstrap 95% CI for partial Spearman."""
    rng = np.random.RandomState(seed)
    n = len(x)
    observed = partial_spearman(x, y, controls)[0]
    boot_rhos = []
    for _ in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        rho_b, _ = partial_spearman(x[idx], y[idx], controls[idx])
        boot_rhos.append(rho_b)
    boot_rhos = np.array(boot_rhos)
    lo = float(np.percentile(boot_rhos, 2.5))
    hi = float(np.percentile(boot_rhos, 97.5))
    return lo, hi


def section_dummies(sections, ref='B'):
    """Build section dummy matrix (n x k-1), dropping reference category."""
    unique = sorted(set(sections))
    unique = [s for s in unique if s != ref]
    dummies = np.zeros((len(sections), len(unique)))
    for i, s in enumerate(sections):
        if s in unique:
            dummies[i, unique.index(s)] = 1.0
    return dummies


def regime_dummies(regimes, ref='REGIME_2'):
    """Build REGIME dummy matrix, dropping reference category."""
    unique = sorted(set(regimes))
    unique = [r for r in unique if r != ref]
    dummies = np.zeros((len(regimes), len(unique)))
    for i, r in enumerate(regimes):
        if r in unique:
            dummies[i, unique.index(r)] = 1.0
    return dummies


# ============================================================
# P0: WITHIN-SECTION VARIANCE IN mean_null_dye
# ============================================================

print("\n=== P0: WITHIN-SECTION VARIANCE DIAGNOSTIC ===")

sections_arr = np.array([folio_section[f] for f in common_folios])
null_dye_arr = np.array([folio_null_dye[f] for f in common_folios])
sb_arr = np.array([folio_safety_bal[f] for f in common_folios])

unique_sections = sorted(set(sections_arr))
grand_mean = np.mean(null_dye_arr)
ss_between = sum(np.sum(sections_arr == s) * (np.mean(null_dye_arr[sections_arr == s]) - grand_mean) ** 2
                 for s in unique_sections)
ss_total = np.sum((null_dye_arr - grand_mean) ** 2)
icc = ss_between / ss_total if ss_total > 0 else 0.0

p0_results = {'ICC': float(icc), 'sections': {}}
for s in unique_sections:
    vals = null_dye_arr[sections_arr == s]
    p0_results['sections'][s] = {
        'n': int(len(vals)),
        'mean': float(np.mean(vals)),
        'std': float(np.std(vals)),
        'range': [float(np.min(vals)), float(np.max(vals))]
    }
    print(f"  {s}: n={len(vals)}, mean={np.mean(vals):.4f}, std={np.std(vals):.4f}, "
          f"range=[{np.min(vals):.4f}, {np.max(vals):.4f}]")
print(f"  ICC (between-section / total): {icc:.4f}")
if icc > 0.90:
    print("  WARNING: ICC > 0.90 — section dummies absorb nearly all variance")


# ============================================================
# S2: STARS SAFETY-BALANCE CONFIRMATORY ANCHOR
# ============================================================

print("\n=== S2: STARS SAFETY-BALANCE REPLICATION ===")

stars_r1 = [folio_safety_bal[f] for f in common_folios
            if folio_section[f] == 'S' and regime_map[f] == 'REGIME_1']
stars_r3 = [folio_safety_bal[f] for f in common_folios
            if folio_section[f] == 'S' and regime_map[f] == 'REGIME_3']

s2_u, s2_p_raw = mannwhitneyu(stars_r1, stars_r3, alternative='greater')
s2_pass = float(np.mean(stars_r1)) > float(np.mean(stars_r3)) and s2_p_raw < 0.05

s2_results = {
    'R1_n': len(stars_r1), 'R1_mean': float(np.mean(stars_r1)),
    'R3_n': len(stars_r3), 'R3_mean': float(np.mean(stars_r3)),
    'U': float(s2_u), 'p': float(s2_p_raw),
    'direction_correct': float(np.mean(stars_r1)) > float(np.mean(stars_r3)),
    'pass': bool(s2_pass)
}
print(f"  S:R1 safety_balance: {np.mean(stars_r1):.4f} (n={len(stars_r1)})")
print(f"  S:R3 safety_balance: {np.mean(stars_r3):.4f} (n={len(stars_r3)})")
print(f"  Mann-Whitney U={s2_u:.1f}, p={s2_p_raw:.6f}")
print(f"  S2 PASS: {s2_pass}")

if not s2_pass:
    print("\n  *** CALIBRATION_FAILURE: S2 anchor fails. Combined metric does not capture individual axis signals. ***")


# ============================================================
# P1: FORGIVINGNESS PREDICTS SAFETY STRATEGY
# ============================================================

print("\n=== P1: FORGIVINGNESS -> SAFETY STRATEGY ===")

sec_dum = section_dummies(sections_arr)

# Section-controlled partial Spearman
p1_rho, p1_p = partial_spearman(null_dye_arr, sb_arr, sec_dum)
p1_ci = bootstrap_partial_spearman(null_dye_arr, sb_arr, sec_dum)
p1_pass = p1_rho < 0 and p1_p < 0.05

print(f"  Partial Spearman (section-controlled): rho={p1_rho:.4f}, p={p1_p:.6f}")
print(f"  Bootstrap 95% CI: [{p1_ci[0]:.4f}, {p1_ci[1]:.4f}]")
print(f"  Direction: {'NEGATIVE (as predicted)' if p1_rho < 0 else 'POSITIVE (reversed)'}")
print(f"  P1 PASS: {p1_pass}")

# Sensitivity: raw (no section control)
p1_raw_rho, p1_raw_p = spearmanr(null_dye_arr, sb_arr)
print(f"  Raw Spearman (no control): rho={p1_raw_rho:.4f}, p={p1_raw_p:.6f}")

# Sensitivity: Herbal-only
herbal_mask = sections_arr == 'H'
if np.sum(herbal_mask) >= 5:
    p1_herbal_rho, p1_herbal_p = spearmanr(null_dye_arr[herbal_mask], sb_arr[herbal_mask])
    print(f"  Herbal-only Spearman: rho={p1_herbal_rho:.4f}, p={p1_herbal_p:.6f} (n={np.sum(herbal_mask)})")
else:
    p1_herbal_rho, p1_herbal_p = float('nan'), float('nan')

p1_results = {
    'partial_rho': p1_rho, 'partial_p': p1_p,
    'ci_95': list(p1_ci),
    'raw_rho': float(p1_raw_rho), 'raw_p': float(p1_raw_p),
    'herbal_rho': float(p1_herbal_rho), 'herbal_p': float(p1_herbal_p),
    'herbal_n': int(np.sum(herbal_mask)),
    'direction_correct': p1_rho < 0,
    'pass': bool(p1_pass)
}


# ============================================================
# P2: HERBAL WITHIN-REGIME FORGIVINGNESS (CORE TEST)
# ============================================================

print("\n=== P2: HERBAL FORGIVINGNESS × REGIME (CORE TEST) ===")

# Build Herbal viable set (R2, R3, R4 only, exclude R1 n=2)
herbal_folios = [f for f in common_folios
                 if folio_section[f] == 'H'
                 and regime_map[f] in ('REGIME_2', 'REGIME_3', 'REGIME_4')]
print(f"  Herbal viable folios: {len(herbal_folios)}")

h_sb = np.array([folio_safety_bal[f] for f in herbal_folios])
h_nd = np.array([folio_null_dye[f] for f in herbal_folios])
h_reg = [regime_map[f] for f in herbal_folios]
h_prof = [folio_profile[f] for f in herbal_folios]

# Report per-cell composition
for reg in sorted(set(h_reg)):
    mask = np.array([r == reg for r in h_reg])
    profs = [h_prof[i] for i in range(len(h_reg)) if h_reg[i] == reg]
    prof_counts = Counter(profs)
    prof_str = ', '.join(f"{k.split('_')[0]}:{v}" for k, v in sorted(prof_counts.items()))
    print(f"  H:{reg} n={np.sum(mask)} [{prof_str}] sb_mean={np.mean(h_sb[mask]):.4f} nd_mean={np.mean(h_nd[mask]):.4f}")

# PRIMARY: Nested OLS
# Model A: safety_balance ~ REGIME (R2 = reference)
h_reg_dum = regime_dummies(h_reg, ref='REGIME_2')
X_a = np.column_stack([h_reg_dum, np.ones(len(herbal_folios))])
beta_a, _, _, _ = lstsq(X_a, h_sb, rcond=None)
resid_a = h_sb - X_a @ beta_a
rss_a = np.sum(resid_a ** 2)
df_a = len(herbal_folios) - X_a.shape[1]
r2_a = 1.0 - rss_a / np.sum((h_sb - np.mean(h_sb)) ** 2)

# Model B: safety_balance ~ REGIME + mean_null_dye
X_b = np.column_stack([h_reg_dum, h_nd, np.ones(len(herbal_folios))])
beta_b, _, _, _ = lstsq(X_b, h_sb, rcond=None)
resid_b = h_sb - X_b @ beta_b
rss_b = np.sum(resid_b ** 2)
df_b = len(herbal_folios) - X_b.shape[1]
r2_b = 1.0 - rss_b / np.sum((h_sb - np.mean(h_sb)) ** 2)

delta_r2 = r2_b - r2_a

# F-test for mean_null_dye contribution
f_stat = ((rss_a - rss_b) / 1) / (rss_b / df_b) if rss_b > 0 and df_b > 0 else 0.0
f_p = 1.0 - st.f.cdf(f_stat, 1, df_b) if f_stat > 0 else 1.0

print(f"\n  Model A (REGIME only): R²={r2_a:.4f}")
print(f"  Model B (REGIME + mean_null_dye): R²={r2_b:.4f}")
print(f"  Delta-R²: {delta_r2:.4f}")
print(f"  F-test for mean_null_dye: F={f_stat:.3f}, p={f_p:.6f}")
print(f"  mean_null_dye coefficient: {beta_b[-2]:.4f}")

# ROBUSTNESS: Rank-based partial Spearman
p2_rank_rho, p2_rank_p = partial_spearman(h_nd, h_sb, h_reg_dum)
print(f"  Rank-partial Spearman (REGIME-controlled): rho={p2_rank_rho:.4f}, p={p2_rank_p:.6f}")

p2_ols_pass = f_p < 0.05 or delta_r2 > 0.03
p2_rank_pass = p2_rank_rho < 0 and p2_rank_p < 0.05  # negative = forgiving → transformative
p2_pass = p2_ols_pass or p2_rank_pass

print(f"  P2 OLS pass: {p2_ols_pass} (F p<0.05 or dR²>0.03)")
print(f"  P2 rank pass: {p2_rank_pass}")
print(f"  P2 PASS (either): {p2_pass}")

# SENSITIVITY: full interaction model (descriptive only)
h_reg_x_nd = h_reg_dum * h_nd[:, np.newaxis]
X_int = np.column_stack([h_reg_dum, h_nd, h_reg_x_nd, np.ones(len(herbal_folios))])
beta_int, _, _, _ = lstsq(X_int, h_sb, rcond=None)
resid_int = h_sb - X_int @ beta_int
rss_int = np.sum(resid_int ** 2)
r2_int = 1.0 - rss_int / np.sum((h_sb - np.mean(h_sb)) ** 2)
print(f"  Interaction model R²: {r2_int:.4f} (descriptive, n too small for formal test)")

p2_results = {
    'n': len(herbal_folios),
    'r2_regime_only': float(r2_a),
    'r2_regime_plus_dye': float(r2_b),
    'delta_r2': float(delta_r2),
    'f_stat': float(f_stat),
    'f_p': float(f_p),
    'dye_coefficient': float(beta_b[-2]),
    'rank_partial_rho': float(p2_rank_rho),
    'rank_partial_p': float(p2_rank_p),
    'interaction_r2': float(r2_int),
    'ols_pass': bool(p2_ols_pass),
    'rank_pass': bool(p2_rank_pass),
    'pass': bool(p2_pass)
}


# ============================================================
# P3: HERBAL A3 SURGERY TEST
# ============================================================

print("\n=== P3: HERBAL A3 SURGERY TEST ===")

h_a3_r3 = [folio_safety_bal[f] for f in common_folios
           if folio_section[f] == 'H' and regime_map[f] == 'REGIME_3'
           and folio_profile.get(f, '').startswith('A3')]
h_a3_r4 = [folio_safety_bal[f] for f in common_folios
           if folio_section[f] == 'H' and regime_map[f] == 'REGIME_4'
           and folio_profile.get(f, '').startswith('A3')]

print(f"  H(A3):R3 n={len(h_a3_r3)}, mean sb={np.mean(h_a3_r3):.4f}" if h_a3_r3 else "  H(A3):R3 n=0")
print(f"  H(A3):R4 n={len(h_a3_r4)}, mean sb={np.mean(h_a3_r4):.4f}" if h_a3_r4 else "  H(A3):R4 n=0")

if len(h_a3_r3) >= 3 and len(h_a3_r4) >= 3:
    p3_u, p3_p = mannwhitneyu(h_a3_r4, h_a3_r3, alternative='greater')
    p3_direction = np.mean(h_a3_r4) > np.mean(h_a3_r3)
    p3_pass = p3_direction and p3_p < 0.10
    print(f"  Mann-Whitney (R4 > R3): U={p3_u:.1f}, p={p3_p:.6f}")
    print(f"  Direction R4 > R3: {p3_direction}")
    print(f"  P3 PASS: {p3_pass}")
else:
    p3_u, p3_p, p3_direction, p3_pass = float('nan'), float('nan'), False, False
    print("  INSUFFICIENT N for formal test")

# Also report all Herbal A3 folios descriptively
h_a3_folios = [(f, regime_map[f], folio_safety_bal[f], folio_null_dye[f])
               for f in common_folios if folio_section[f] == 'H'
               and folio_profile.get(f, '').startswith('A3')]
print(f"\n  All Herbal A3 folios ({len(h_a3_folios)}):")
for f, reg, sb, nd in sorted(h_a3_folios, key=lambda x: x[1]):
    print(f"    {f} {reg} sb={sb:.4f} nd={nd:.4f}")

p3_results = {
    'h_a3_r3_n': len(h_a3_r3), 'h_a3_r3_mean': float(np.mean(h_a3_r3)) if h_a3_r3 else None,
    'h_a3_r4_n': len(h_a3_r4), 'h_a3_r4_mean': float(np.mean(h_a3_r4)) if h_a3_r4 else None,
    'U': float(p3_u), 'p': float(p3_p),
    'direction_r4_gt_r3': bool(p3_direction),
    'pass': bool(p3_pass)
}


# ============================================================
# P4: CLOSURE AUTHENTICITY INTERACTION
# ============================================================

print("\n=== P4: CLOSURE AUTHENTICITY (strong_close_fraction) ===")

scf_arr = np.array([folio_scf[f] for f in common_folios])

p4_rho, p4_p = partial_spearman(scf_arr, sb_arr, sec_dum)
p4_pass = p4_rho > 0 and p4_p < 0.10

print(f"  Partial Spearman (section-controlled): rho={p4_rho:.4f}, p={p4_p:.6f}")
print(f"  Direction: {'POSITIVE (as predicted)' if p4_rho > 0 else 'NEGATIVE (reversed)'}")
print(f"  P4 PASS: {p4_pass}")

# Raw sensitivity
p4_raw_rho, p4_raw_p = spearmanr(scf_arr, sb_arr)
print(f"  Raw Spearman: rho={p4_raw_rho:.4f}, p={p4_raw_p:.6f}")

p4_results = {
    'partial_rho': float(p4_rho), 'partial_p': float(p4_p),
    'raw_rho': float(p4_raw_rho), 'raw_p': float(p4_raw_p),
    'direction_correct': p4_rho > 0,
    'pass': bool(p4_pass)
}


# ============================================================
# S1a: DYE ORTHOGONALITY WITHIN STARS
# ============================================================

print("\n=== S1a: DYE ORTHOGONALITY (STARS) ===")

stars_folios = [f for f in common_folios
                if folio_section[f] == 'S'
                and regime_map[f] in ('REGIME_1', 'REGIME_3')]
s_dye = np.array([folio_dye[f] for f in stars_folios])
s_sb = np.array([folio_safety_bal[f] for f in stars_folios])
s_reg = [regime_map[f] for f in stars_folios]
s_reg_dum = regime_dummies(s_reg, ref='REGIME_1')

s1a_rho, s1a_p = partial_spearman(s_dye, s_sb, s_reg_dum)
print(f"  Stars DYE vs safety_balance (REGIME-controlled): rho={s1a_rho:.4f}, p={s1a_p:.6f} (n={len(stars_folios)})")
print(f"  Prediction: NOT significant -> {'CONFIRMED' if s1a_p >= 0.05 else 'VIOLATED'}")

s1a_results = {
    'n': len(stars_folios),
    'partial_rho': float(s1a_rho), 'partial_p': float(s1a_p),
    'orthogonal': s1a_p >= 0.05
}


# ============================================================
# S1b: DYE ORTHOGONALITY ALL FOLIOS
# ============================================================

print("\n=== S1b: DYE ORTHOGONALITY (ALL FOLIOS) ===")

dye_arr = np.array([folio_dye[f] for f in common_folios])
s1b_rho, s1b_p = partial_spearman(dye_arr, sb_arr, sec_dum)
print(f"  All-folio DYE vs safety_balance (section-controlled): rho={s1b_rho:.4f}, p={s1b_p:.6f}")
print(f"  Prediction: weak/null -> {'CONFIRMED' if s1b_p >= 0.05 else 'VIOLATED'}")

s1b_results = {
    'partial_rho': float(s1b_rho), 'partial_p': float(s1b_p),
    'orthogonal': s1b_p >= 0.05
}


# ============================================================
# S3: A2 DUMMY SENSITIVITY
# ============================================================

print("\n=== S3: A2 DUMMY SENSITIVITY ===")

is_a2 = np.array([1.0 if folio_profile.get(f, '').startswith('A2') else 0.0
                   for f in common_folios])

# OLS: safety_balance ~ is_A2 + section
X_a2 = np.column_stack([is_a2, sec_dum, np.ones(len(common_folios))])
beta_a2, _, _, _ = lstsq(X_a2, sb_arr, rcond=None)
resid_a2 = sb_arr - X_a2 @ beta_a2
rss_a2 = np.sum(resid_a2 ** 2)
r2_a2 = 1.0 - rss_a2 / np.sum((sb_arr - np.mean(sb_arr)) ** 2)

# t-test for A2 dummy
se_a2 = np.sqrt(rss_a2 / (len(common_folios) - X_a2.shape[1]) *
                np.diag(np.linalg.pinv(X_a2.T @ X_a2))[0])
t_a2 = beta_a2[0] / se_a2 if se_a2 > 1e-10 else 0.0
p_a2 = 2 * (1 - st.t.cdf(abs(t_a2), len(common_folios) - X_a2.shape[1]))

# Compare with P1: is the A2 dummy effect similar?
a2_folios = [f for f in common_folios if folio_profile.get(f, '').startswith('A2')]
non_a2_folios = [f for f in common_folios if not folio_profile.get(f, '').startswith('A2')]
a2_sb_mean = np.mean([folio_safety_bal[f] for f in a2_folios])
non_a2_sb_mean = np.mean([folio_safety_bal[f] for f in non_a2_folios])

print(f"  A2 dummy coefficient: {beta_a2[0]:.4f}")
print(f"  t-stat: {t_a2:.3f}, p={p_a2:.6f}")
print(f"  Model R²: {r2_a2:.4f}")
print(f"  A2 mean safety_balance: {a2_sb_mean:.4f} (n={len(a2_folios)})")
print(f"  Non-A2 mean safety_balance: {non_a2_sb_mean:.4f} (n={len(non_a2_folios)})")
print(f"  Profile-concentrated: {'YES' if p_a2 < 0.05 else 'NO'}")

s3_results = {
    'a2_coeff': float(beta_a2[0]),
    't_stat': float(t_a2), 'p': float(p_a2),
    'r2': float(r2_a2),
    'a2_n': len(a2_folios), 'a2_sb_mean': float(a2_sb_mean),
    'non_a2_n': len(non_a2_folios), 'non_a2_sb_mean': float(non_a2_sb_mean),
    'profile_concentrated': p_a2 < 0.05
}


# ============================================================
# VERDICT
# ============================================================

print("\n" + "=" * 60)
print("VERDICT")
print("=" * 60)

if not s2_pass:
    verdict = 'CALIBRATION_FAILURE'
elif p2_pass and s2_pass:
    if p1_pass:
        verdict = 'FORGIVINGNESS_ASSOCIATED_WITH_SAFETY_STYLE'
    else:
        verdict = 'SAFETY_STYLE_MODERATION_SUPPORTED'
    # Check P3 trend for A2_REVERSAL_MECHANISM_SUPPORTED qualifier
    if p3_direction and p3_pass:
        verdict = 'A2_REVERSAL_MECHANISM_SUPPORTED'
elif p1_pass and not p2_pass:
    verdict = 'GLOBAL_ASSOCIATION_WITHOUT_HERBAL_MECHANISM'
elif s2_pass and not p1_pass and not p2_pass:
    verdict = 'STARS_ONLY_REPLICATION'
else:
    verdict = 'SAFETY_STYLE_MODERATION_NOT_CONFIRMED'

# Construct pass summary
pass_summary = {
    'S2': bool(s2_pass), 'P1': bool(p1_pass), 'P2': bool(p2_pass),
    'P3': bool(p3_pass), 'P4': bool(p4_pass)
}
n_primary_pass = sum(1 for k in ['P1', 'P2', 'P3', 'P4'] if pass_summary[k])

print(f"\n  S2 (Stars anchor):         {'PASS' if s2_pass else 'FAIL'}")
print(f"  P1 (Forgivingness global): {'PASS' if p1_pass else 'FAIL'}")
print(f"  P2 (Herbal core):          {'PASS' if p2_pass else 'FAIL'}")
print(f"  P3 (Surgery test):         {'PASS' if p3_pass else 'FAIL'}")
print(f"  P4 (Authenticity):         {'PASS' if p4_pass else 'FAIL'}")
print(f"\n  Primary passes: {n_primary_pass}/4")
print(f"\n  VERDICT: {verdict}")

runtime = time.time() - t0
print(f"\nRuntime: {runtime:.1f}s")


# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'phase': 601,
    'phase_name': 'SAFETY_STYLE_MODERATION',
    'prediction_hash': PRED_HASH,
    'n_folios': len(common_folios),
    'verification': {
        'mean_ey_rate': float(mean_ey),
        'mean_ii_rate': float(mean_ii),
    },
    'P0_icc': p0_results,
    'S2_stars_anchor': s2_results,
    'P1_forgivingness': p1_results,
    'P2_herbal_core': p2_results,
    'P3_surgery': p3_results,
    'P4_authenticity': p4_results,
    'S1a_dye_stars': s1a_results,
    'S1b_dye_all': s1b_results,
    'S3_a2_dummy': s3_results,
    'pass_summary': pass_summary,
    'n_primary_pass': n_primary_pass,
    'verdict': verdict,
    'runtime_s': round(runtime, 1),
}

results_path = os.path.join(os.path.dirname(__file__), '..', 'results',
                            'safety_style_moderation_results.json')
with open(results_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)
print(f"\nResults saved to {results_path}")
