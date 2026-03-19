"""
Phase 609: H_RATIO_REPERTOIRE_MECHANISM

Identifies which aspect of paragraph repertoire drives the independent h_ratio
effect found in C1763 (31.9% additional variance beyond PREFIX + section + parcount).

Tests:
  T1: Nested model tournament (5 candidates in 3 families vs baseline)
  T2: Continuous vs discrete representation comparison (3 tiers)
  T3: Section-dependent analysis (Stars vs others)
  T4: MP zone continuous deep-dive
  T5: Leave-one-out cross-validation (discrete vs continuous prediction)

Key question: Is this a genuine paragraph-combination effect, or an artifact of
discretizing continuous paragraph gradients into hard zone labels?
"""

import json
import os
import sys
import hashlib
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from numpy.linalg import lstsq
from scipy import stats

# ---------- paths ----------
BASE = Path(__file__).resolve().parents[3]
RESULTS_DIR = BASE / 'phases' / 'H_RATIO_REPERTOIRE_MECHANISM' / 'results'
PRED_PATH = BASE / 'phases' / 'H_RATIO_REPERTOIRE_MECHANISM' / 'PREDICTIONS.md'

sys.path.insert(0, str(BASE))
from scripts.voynich import Transcript, Morphology

# ---------- constants ----------
ZONE_NAMES = {0: "THERMAL-QO", 1: "CONTAINMENT-Sealing",
              2: "OPERATION-Iteration", 3: "MONITORING-Phase"}
ZONE_SHORT = {0: "TQ", 1: "CS", 2: "OI", 3: "MP"}
N_ZONES = 4
N_PERM = 1000

rng = np.random.default_rng(609)

# Atom-category mapping (from Phase 510 / C1250, C1195, C1388-C1392)
ATOM_CATEGORY = {
    'k': 'THERMAL', 'e': 'THERMAL', 'q': 'THERMAL',
    'h': 'MONITORING', 'c': 'MONITORING',
    'd': 'CONTAINMENT', 'y': 'CONTAINMENT',
    't': 'TRANSITION',
    'n': 'OPERATION', 'i': 'OPERATION', 'g': 'OPERATION', 'x': 'OPERATION',
    'a': 'STAGING', 'o': 'STAGING', 's': 'STAGING',
    'l': 'FLOW', 'r': 'FLOW',
    'm': 'MARKING', 'p': 'MARKING', 'f': 'MARKING',
}
CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']


def convert_numpy(obj):
    """Convert numpy types for JSON serialization."""
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, np.ndarray):
        return [convert_numpy(v) for v in obj]
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [convert_numpy(v) for v in obj]
    return obj


def assign_category(middle):
    """Assign operational category to a MIDDLE via atom plurality vote."""
    if not middle:
        return None
    votes = Counter()
    for ch in middle:
        cat = ATOM_CATEGORY.get(ch)
        if cat:
            votes[cat] += 1
    return votes.most_common(1)[0][0] if votes else None


def ols_r2(X, y):
    """Compute R-squared from OLS."""
    coef, _, _, _ = lstsq(X, y, rcond=None)
    y_pred = X @ coef
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    if ss_tot == 0:
        return 0.0
    return 1.0 - ss_res / ss_tot


def ols_predict(X_train, y_train, X_test):
    """OLS predict for LOO."""
    coef, _, _, _ = lstsq(X_train, y_train, rcond=None)
    return X_test @ coef


def f_test_nested(r2_full, r2_base, n, p_full, p_base):
    """F-test for nested model comparison."""
    df1 = p_full - p_base
    df2 = n - p_full
    if df1 <= 0 or df2 <= 0 or r2_full <= r2_base:
        return 0.0, 1.0
    f_stat = ((r2_full - r2_base) / df1) / ((1.0 - r2_full) / df2)
    p_val = 1.0 - stats.f.cdf(f_stat, df1, df2)
    return float(f_stat), float(p_val)


# ==================== DATA LOADING ====================

print("=== Phase 609: H_RATIO_REPERTOIRE_MECHANISM ===\n")

# Verify predictions hash
pred_hash = hashlib.sha256(PRED_PATH.read_bytes()).hexdigest()
print(f"PREDICTIONS.md SHA-256: {pred_hash}")

# 1. Paragraph zone assignments (C1398)
with open(BASE / 'phases' / 'PARAGRAPH_PROGRAM_TYPING' / 'results' / 'paragraph_program_typing.json') as f:
    p510 = json.load(f)
labels = p510['paragraph_labels']  # 264 entries
print(f"Loaded {len(labels)} paragraph labels")

# Build per-folio zone data
folio_zones = defaultdict(list)
folio_section = {}
for entry in labels:
    folio_zones[entry['folio']].append(entry['cluster'])
    folio_section[entry['folio']] = entry['section']

# 2. Folio operational profiles
with open(BASE / 'results' / 'folio_operational_profiles.json') as f:
    op_raw = json.load(f)
op_profiles = {p['folio']: p for p in op_raw['profiles']}

# 3. Compute PREFIX fractions per folio from transcript
print("Computing PREFIX fractions from transcript...")
tx = Transcript()
morph = Morphology()

folio_prefix_data = defaultdict(lambda: {'total': 0, 'qo': 0, 'chsh': 0, 'bare': 0})
for token in tx.currier_b():
    if '*' in token.word or not token.word.strip():
        continue
    if token.placement.startswith('L'):
        continue
    m = morph.extract(token.word)
    fpd = folio_prefix_data[token.folio]
    fpd['total'] += 1
    pfx = m.prefix
    if pfx is None:
        fpd['bare'] += 1
    elif pfx in ('qo', 'o'):
        fpd['qo'] += 1
    elif pfx in ('ch', 'sh', 'cth', 'ckh', 'cfh', 'cph'):
        fpd['chsh'] += 1

folio_prefix_fracs = {}
for folio, pd in folio_prefix_data.items():
    t = pd['total']
    if t > 0:
        folio_prefix_fracs[folio] = {
            'qo_frac': pd['qo'] / t,
            'chsh_frac': pd['chsh'] / t,
            'bare_frac': pd['bare'] / t,
        }
print(f"PREFIX fractions for {len(folio_prefix_fracs)} folios")


# ==================== PARAGRAPH-LEVEL CONTINUOUS FEATURES ====================

print("\nComputing per-paragraph continuous features...")

# Rebuild paragraphs from transcript (same as Phase 510)
all_b_tokens = list(tx.currier_b())
folio_tokens = defaultdict(list)
for t in all_b_tokens:
    folio_tokens[t.folio].append(t)
for folio in folio_tokens:
    folio_tokens[folio].sort(key=lambda t: (t.line, 0))

paragraphs = []
for folio, toks in sorted(folio_tokens.items()):
    par_idx = 0
    current_par = []
    for t in toks:
        if t.par_initial and current_par:
            paragraphs.append({
                'folio': folio,
                'par_idx': par_idx,
                'tokens': current_par,
                'section': current_par[0].section,
            })
            par_idx += 1
            current_par = [t]
        else:
            current_par.append(t)
    if current_par:
        paragraphs.append({
            'folio': folio,
            'par_idx': par_idx,
            'tokens': current_par,
            'section': current_par[0].section,
        })

# Count body lines and filter to 3+ body lines (matching Phase 510)
for par in paragraphs:
    lines = set(t.line for t in par['tokens'])
    par['body_lines'] = len(lines) - 1 if len(lines) > 1 else 0

filtered_pars = [p for p in paragraphs if p['body_lines'] >= 3]
print(f"Paragraphs with 3+ body lines: {len(filtered_pars)}")

# Compute continuous features per paragraph
par_continuous = []  # list of dicts with folio, par_idx, THERMAL_score, MONITORING_score, h_kernel_frac
for par in filtered_pars:
    toks = par['tokens']
    morphs = []
    for t in toks:
        w = t.word.strip()
        if not w or '*' in w:
            continue
        try:
            m = morph.extract(w)
            morphs.append(m)
        except Exception:
            continue
    if len(morphs) < 5:
        continue

    # Category fractions via atom plurality vote
    cat_counts = Counter()
    for m in morphs:
        cat = assign_category(m.middle)
        if cat:
            cat_counts[cat] += 1
    cat_total = sum(cat_counts.values()) or 1
    thermal_score = cat_counts.get('THERMAL', 0) / cat_total
    monitoring_score = cat_counts.get('MONITORING', 0) / cat_total

    # h_kernel fraction (tokens with 'h' in MIDDLE)
    h_count = sum(1 for m in morphs if m.middle and 'h' in m.middle)
    h_kernel_frac = h_count / len(morphs)

    par_continuous.append({
        'folio': par['folio'],
        'par_idx': par['par_idx'],
        'thermal_score': thermal_score,
        'monitoring_score': monitoring_score,
        'h_kernel_frac': h_kernel_frac,
    })

print(f"Paragraphs with continuous features: {len(par_continuous)}")

# Aggregate to folio level
folio_continuous = {}
for folio, zones in folio_zones.items():
    pars = [p for p in par_continuous if p['folio'] == folio]
    if not pars:
        continue

    thermal_scores = [p['thermal_score'] for p in pars]
    monitoring_scores = [p['monitoring_score'] for p in pars]
    h_kernel_fracs = [p['h_kernel_frac'] for p in pars]
    tm_diffs = [t - m for t, m in zip(thermal_scores, monitoring_scores)]

    fc = {}
    # Tier 1: Location
    fc['thermal_mean'] = np.mean(thermal_scores)
    fc['monitoring_mean'] = np.mean(monitoring_scores)
    fc['h_kernel_mean'] = np.mean(h_kernel_fracs)

    # Tier 2: Spread
    fc['thermal_monitoring_var'] = np.var(tm_diffs) if len(tm_diffs) > 1 else 0.0
    fc['monitoring_range'] = max(monitoring_scores) - min(monitoring_scores) if len(monitoring_scores) > 1 else 0.0
    fc['thermal_range'] = max(thermal_scores) - min(thermal_scores) if len(thermal_scores) > 1 else 0.0

    # Tier 3: Shape (quartiles)
    fc['monitoring_q25'] = np.percentile(monitoring_scores, 25)
    fc['monitoring_q75'] = np.percentile(monitoring_scores, 75)
    fc['thermal_q25'] = np.percentile(thermal_scores, 25)
    fc['thermal_q75'] = np.percentile(thermal_scores, 75)
    fc['h_kernel_q25'] = np.percentile(h_kernel_fracs, 25)
    fc['h_kernel_q75'] = np.percentile(h_kernel_fracs, 75)

    folio_continuous[folio] = fc

print(f"Folios with continuous aggregates: {len(folio_continuous)}")


# ==================== BUILD FOLIO OBJECTS ====================

# Binary zone signatures, repertoire properties
folio_data = {}
for folio, zones in folio_zones.items():
    zone_set = set(zones)
    zone_counts = Counter(zones)
    sig = ''.join('1' if i in zone_set else '0' for i in range(N_ZONES))
    breadth = len(zone_set)
    n_par = len(zones)

    # Shannon entropy of zone count vector
    total = sum(zone_counts.values())
    probs = [c / total for c in zone_counts.values()]
    rep_entropy = -sum(p * np.log2(p) for p in probs if p > 0)

    folio_data[folio] = {
        'zones': zones,
        'zone_set': zone_set,
        'zone_counts': dict(zone_counts),
        'signature': sig,
        'breadth': breadth,
        'n_paragraphs': n_par,
        'section': folio_section.get(folio, '?'),
        'mp_present': 3 in zone_set,
        'tq_present': 0 in zone_set,
        'tq_mp_exclusion': (0 in zone_set) != (3 in zone_set),  # XOR: has one but not both
        'mono_type': breadth == 1,
        'rep_entropy': rep_entropy,
    }

all_folios = sorted(folio_data.keys())
print(f"Total folios with zone data: {len(all_folios)}")

# Find folios with complete data for modeling
complete_folios = []
for f in all_folios:
    op = op_profiles.get(f)
    pfx = folio_prefix_fracs.get(f)
    fc = folio_continuous.get(f)
    if op and pfx and fc and op.get('h_ratio') is not None:
        complete_folios.append(f)
print(f"Folios with complete data: {len(complete_folios)}")

# Merge rare repertoire types (n < 5)
sig_counts = Counter(folio_data[f]['signature'] for f in complete_folios)
rare_sigs = {s for s, c in sig_counts.items() if c < 5}
print(f"Repertoire types: {len(sig_counts)}, rare (n<5, merged): {len(rare_sigs)}")


def get_rep_type(folio):
    sig = folio_data[folio]['signature']
    return 'RARE' if sig in rare_sigs else sig


def parcount_bin(f):
    n = folio_data[f]['n_paragraphs']
    if n == 1:
        return 0
    elif n <= 3:
        return 1
    return 2


# ==================== MODEL BUILDING HELPERS ====================

def build_baseline_A(folio_list, fixed_sections=None, fixed_sec_to_idx=None):
    """Baseline A: intercept + qo_frac + chsh_frac + bare_frac + paragraph_count + section dummies.

    If fixed_sections/fixed_sec_to_idx provided, use those for consistent column encoding
    (critical for LOO where train/test must have same columns).
    """
    if fixed_sec_to_idx is not None:
        sec_to_idx = fixed_sec_to_idx
        n_sec = len(sec_to_idx)
    else:
        sections = sorted(set(folio_data[f]['section'] for f in folio_list))
        sec_to_idx = {s: i for i, s in enumerate(sections[1:])}
        n_sec = len(sections) - 1
    n = len(folio_list)
    X = np.zeros((n, 5 + n_sec))
    for i, f in enumerate(folio_list):
        pfx = folio_prefix_fracs[f]
        X[i, 0] = 1  # intercept
        X[i, 1] = pfx['qo_frac']
        X[i, 2] = pfx['chsh_frac']
        X[i, 3] = pfx['bare_frac']
        X[i, 4] = folio_data[f]['n_paragraphs']
        sec = folio_data[f]['section']
        if sec in sec_to_idx:
            X[i, 5 + sec_to_idx[sec]] = 1
    return X


def build_baseline_B(folio_list):
    """Baseline B: Baseline A + k_ratio + e_ratio (kernel ecology sensitivity)."""
    X_A = build_baseline_A(folio_list)
    n = len(folio_list)
    X = np.zeros((n, X_A.shape[1] + 2))
    X[:, :X_A.shape[1]] = X_A
    for i, f in enumerate(folio_list):
        op = op_profiles[f]
        X[i, X_A.shape[1]] = op.get('k_ratio', 0)
        X[i, X_A.shape[1] + 1] = op.get('e_ratio', 0)
    return X


def add_repertoire_dummies(X_base, folio_list, rep_types, fixed_rep_to_idx=None):
    """Add repertoire type dummies to a baseline matrix.

    If fixed_rep_to_idx provided, use it for consistent column encoding (LOO).
    """
    if fixed_rep_to_idx is not None:
        rep_to_idx = fixed_rep_to_idx
        n_dummies = len(rep_to_idx)
    else:
        unique_reps = sorted(set(rep_types))
        if len(unique_reps) <= 1:
            return X_base, 0
        rep_to_idx = {r: i for i, r in enumerate(unique_reps[1:])}
        n_dummies = len(unique_reps) - 1
    X = np.zeros((len(folio_list), X_base.shape[1] + n_dummies))
    X[:, :X_base.shape[1]] = X_base
    for i, rt in enumerate(rep_types):
        if rt in rep_to_idx:
            X[i, X_base.shape[1] + rep_to_idx[rt]] = 1
    return X, n_dummies


def add_single_feature(X_base, values):
    """Add a single feature column."""
    X = np.zeros((X_base.shape[0], X_base.shape[1] + 1))
    X[:, :X_base.shape[1]] = X_base
    X[:, -1] = values
    return X


def add_continuous_features(X_base, folio_list, tier):
    """Add continuous paragraph features at specified tier level."""
    tier1_keys = ['thermal_mean', 'monitoring_mean', 'h_kernel_mean']
    tier2_keys = ['thermal_monitoring_var', 'monitoring_range', 'thermal_range']
    tier3_keys = ['monitoring_q25', 'monitoring_q75', 'thermal_q25', 'thermal_q75',
                  'h_kernel_q25', 'h_kernel_q75']

    if tier == 1:
        keys = tier1_keys
    elif tier == 2:
        keys = tier1_keys + tier2_keys
    elif tier == 3:
        keys = tier1_keys + tier2_keys + tier3_keys
    else:
        keys = []

    n_feat = len(keys)
    X = np.zeros((len(folio_list), X_base.shape[1] + n_feat))
    X[:, :X_base.shape[1]] = X_base
    for i, f in enumerate(folio_list):
        fc = folio_continuous[f]
        for j, k in enumerate(keys):
            X[i, X_base.shape[1] + j] = fc[k]
    return X, n_feat


# ==================== T1: NESTED MODEL TOURNAMENT ====================

print("\n" + "=" * 70)
print("T1: Which repertoire property drives h_ratio?")
print("=" * 70)

# Outcome: rank-transformed h_ratio
y_raw = np.array([op_profiles[f]['h_ratio'] for f in complete_folios])
y = stats.rankdata(y_raw)  # rank transform

X_A = build_baseline_A(complete_folios)
X_B = build_baseline_B(complete_folios)
r2_A = ols_r2(X_A, y)
r2_B = ols_r2(X_B, y)
n = len(complete_folios)

print(f"\nBaseline A R^2: {r2_A:.4f} (n={n}, p={X_A.shape[1]})")
print(f"Baseline B R^2: {r2_B:.4f} (p={X_B.shape[1]})")

# M1: MP_present
mp_vals = np.array([1.0 if folio_data[f]['mp_present'] else 0.0 for f in complete_folios])
X_M1 = add_single_feature(X_A, mp_vals)
r2_M1 = ols_r2(X_M1, y)
dr2_M1 = r2_M1 - r2_A
f_M1, fp_M1 = f_test_nested(r2_M1, r2_A, n, X_M1.shape[1], X_A.shape[1])

# M2: TQ_MP_exclusion
tqmp_vals = np.array([1.0 if folio_data[f]['tq_mp_exclusion'] else 0.0 for f in complete_folios])
X_M2 = add_single_feature(X_A, tqmp_vals)
r2_M2 = ols_r2(X_M2, y)
dr2_M2 = r2_M2 - r2_A
f_M2, fp_M2 = f_test_nested(r2_M2, r2_A, n, X_M2.shape[1], X_A.shape[1])

# M3: mono_vs_multi
mono_vals = np.array([1.0 if folio_data[f]['mono_type'] else 0.0 for f in complete_folios])
X_M3 = add_single_feature(X_A, mono_vals)
r2_M3 = ols_r2(X_M3, y)
dr2_M3 = r2_M3 - r2_A
f_M3, fp_M3 = f_test_nested(r2_M3, r2_A, n, X_M3.shape[1], X_A.shape[1])

# M4: repertoire_entropy
ent_vals = np.array([folio_data[f]['rep_entropy'] for f in complete_folios])
X_M4 = add_single_feature(X_A, ent_vals)
r2_M4 = ols_r2(X_M4, y)
dr2_M4 = r2_M4 - r2_A
f_M4, fp_M4 = f_test_nested(r2_M4, r2_A, n, X_M4.shape[1], X_A.shape[1])

# M5: full repertoire_type (categorical)
rep_types = [get_rep_type(f) for f in complete_folios]
X_M5, n_rep_dummies = add_repertoire_dummies(X_A, complete_folios, rep_types)
r2_M5 = ols_r2(X_M5, y)
dr2_M5 = r2_M5 - r2_A
f_M5, fp_M5 = f_test_nested(r2_M5, r2_A, n, X_M5.shape[1], X_A.shape[1])

# Print results
models = {
    'M1_MP_present': {'dR2': dr2_M1, 'F': f_M1, 'F_p': fp_M1, 'family': 'Presence', 'params': 1},
    'M2_TQ_MP_exclusion': {'dR2': dr2_M2, 'F': f_M2, 'F_p': fp_M2, 'family': 'Presence', 'params': 1},
    'M3_mono_vs_multi': {'dR2': dr2_M3, 'F': f_M3, 'F_p': fp_M3, 'family': 'Breadth', 'params': 1},
    'M4_rep_entropy': {'dR2': dr2_M4, 'F': f_M4, 'F_p': fp_M4, 'family': 'Breadth', 'params': 1},
    'M5_full_repertoire': {'dR2': dr2_M5, 'F': f_M5, 'F_p': fp_M5, 'family': 'Full', 'params': n_rep_dummies},
}

print("\n  Model              | Family   | dR^2   | F      | F_p    | params")
print("  " + "-" * 72)
for name, m in models.items():
    print(f"  {name:20s} | {m['family']:8s} | {m['dR2']:.4f} | {m['F']:.3f} | {m['F_p']:.4f} | {m['params']}")

# Permutation test (within section x parcount-bin)
print("\nRunning permutation tests (1000 shuffles within section x parcount-bin)...")

# Build strata
strata = defaultdict(list)
for i, f in enumerate(complete_folios):
    key = (folio_data[f]['section'], parcount_bin(f))
    strata[key].append(i)

# For each model, permute the added variable(s) within strata
def permutation_test_single(X_base, feature_col, y_obs, r2_base, n_perm=N_PERM):
    """Permutation test for a single added feature."""
    obs_dr2 = ols_r2(add_single_feature(X_base, feature_col), y_obs) - r2_base
    null_dr2s = []
    for _ in range(n_perm):
        perm_col = feature_col.copy()
        for indices in strata.values():
            if len(indices) > 1:
                subset = perm_col[indices].copy()
                rng.shuffle(subset)
                perm_col[indices] = subset
        null_dr2s.append(ols_r2(add_single_feature(X_base, perm_col), y_obs) - r2_base)
    null_arr = np.array(null_dr2s)
    perm_p = np.mean(null_arr >= obs_dr2)
    return float(perm_p)


def permutation_test_categorical(X_base, cat_labels, y_obs, r2_base, n_perm=N_PERM):
    """Permutation test for categorical variable (shuffle labels within strata)."""
    obs_dr2 = dr2_M5  # already computed
    null_dr2s = []
    labels_arr = np.array(cat_labels)
    for _ in range(n_perm):
        perm_labels = labels_arr.copy()
        for indices in strata.values():
            if len(indices) > 1:
                subset = perm_labels[indices].copy()
                rng.shuffle(subset)
                perm_labels[indices] = subset
        X_perm, _ = add_repertoire_dummies(X_base, complete_folios, list(perm_labels))
        r2_perm = ols_r2(X_perm, y_obs)
        null_dr2s.append(r2_perm - r2_base)
    null_arr = np.array(null_dr2s)
    perm_p = np.mean(null_arr >= obs_dr2)
    return float(perm_p)


perm_M1 = permutation_test_single(X_A, mp_vals, y, r2_A)
perm_M2 = permutation_test_single(X_A, tqmp_vals, y, r2_A)
perm_M3 = permutation_test_single(X_A, mono_vals, y, r2_A)
perm_M4 = permutation_test_single(X_A, ent_vals, y, r2_A)
perm_M5 = permutation_test_categorical(X_A, rep_types, y, r2_A)

for name, pp in [('M1', perm_M1), ('M2', perm_M2), ('M3', perm_M3), ('M4', perm_M4), ('M5', perm_M5)]:
    models[f'{name}_MP_present' if name == 'M1' else
           f'{name}_TQ_MP_exclusion' if name == 'M2' else
           f'{name}_mono_vs_multi' if name == 'M3' else
           f'{name}_rep_entropy' if name == 'M4' else
           f'{name}_full_repertoire']['perm_p'] = pp
    print(f"  {name} permutation p = {pp:.4f}")

# Identify best simple predictor (M1-M4) and best overall
simple_models = {k: v for k, v in models.items() if k != 'M5_full_repertoire'}
best_simple_name = max(simple_models, key=lambda k: simple_models[k]['dR2'])
best_simple = simple_models[best_simple_name]
best_overall_name = max(models, key=lambda k: models[k]['dR2'])

print(f"\nBest simple predictor: {best_simple_name} (dR^2={best_simple['dR2']:.4f})")
print(f"Best overall: {best_overall_name} (dR^2={models[best_overall_name]['dR2']:.4f})")
print(f"M5 improvement over best simple: {dr2_M5 - best_simple['dR2']:.4f}")

# Baseline B sensitivity check (run best simple + M5 against Baseline B)
print("\nBaseline B sensitivity check (adding k_ratio + e_ratio):")

best_simple_feat_map = {
    'M1_MP_present': mp_vals,
    'M2_TQ_MP_exclusion': tqmp_vals,
    'M3_mono_vs_multi': mono_vals,
    'M4_rep_entropy': ent_vals,
}

X_best_B = add_single_feature(X_B, best_simple_feat_map[best_simple_name])
r2_best_B = ols_r2(X_best_B, y)
dr2_best_B = r2_best_B - r2_B
f_best_B, fp_best_B = f_test_nested(r2_best_B, r2_B, n, X_best_B.shape[1], X_B.shape[1])

X_M5_B, n_rep_B = add_repertoire_dummies(X_B, complete_folios, rep_types)
r2_M5_B = ols_r2(X_M5_B, y)
dr2_M5_B = r2_M5_B - r2_B
f_M5_B, fp_M5_B = f_test_nested(r2_M5_B, r2_B, n, X_M5_B.shape[1], X_B.shape[1])

print(f"  Best simple ({best_simple_name}) vs B: dR^2={dr2_best_B:.4f}, F={f_best_B:.3f}, p={fp_best_B:.4f}")
print(f"  M5 vs B: dR^2={dr2_M5_B:.4f}, F={f_M5_B:.3f}, p={fp_M5_B:.4f}")

# Kruskal-Wallis raw tests (for comparison)
print("\nRaw Kruskal-Wallis (h_ratio by each repertoire property, no controls):")
mp_groups = [y_raw[mp_vals == 0], y_raw[mp_vals == 1]]
kw_M1 = stats.kruskal(*[g for g in mp_groups if len(g) > 0])
tqmp_groups = [y_raw[tqmp_vals == 0], y_raw[tqmp_vals == 1]]
kw_M2 = stats.kruskal(*[g for g in tqmp_groups if len(g) > 0])
mono_groups = [y_raw[mono_vals == 0], y_raw[mono_vals == 1]]
kw_M3 = stats.kruskal(*[g for g in mono_groups if len(g) > 0])
rep_type_arr = np.array(rep_types)
kw_groups_M5 = [y_raw[rep_type_arr == rt] for rt in sorted(set(rep_types)) if np.sum(rep_type_arr == rt) > 0]
kw_M5 = stats.kruskal(*kw_groups_M5) if len(kw_groups_M5) > 1 else (0, 1)
print(f"  M1 (MP_present): H={kw_M1.statistic:.2f}, p={kw_M1.pvalue:.4f}")
print(f"  M2 (TQ_MP_excl): H={kw_M2.statistic:.2f}, p={kw_M2.pvalue:.4f}")
print(f"  M3 (mono/multi): H={kw_M3.statistic:.2f}, p={kw_M3.pvalue:.4f}")
print(f"  M5 (full rep): H={kw_M5.statistic if hasattr(kw_M5, 'statistic') else kw_M5[0]:.2f}, p={kw_M5.pvalue if hasattr(kw_M5, 'pvalue') else kw_M5[1]:.4f}")

t1_results = {
    'baseline_A_r2': r2_A,
    'baseline_B_r2': r2_B,
    'n': n,
    'models': convert_numpy(models),
    'best_simple': best_simple_name,
    'best_overall': best_overall_name,
    'M5_improvement_over_best_simple': dr2_M5 - best_simple['dR2'],
    'baseline_B_sensitivity': {
        'best_simple_vs_B': {'dR2': dr2_best_B, 'F': f_best_B, 'F_p': fp_best_B},
        'M5_vs_B': {'dR2': dr2_M5_B, 'F': f_M5_B, 'F_p': fp_M5_B},
    },
}


# ==================== T2: CONTINUOUS vs DISCRETE ====================

print("\n" + "=" * 70)
print("T2: Continuous vs Discrete representation comparison")
print("=" * 70)

# Continuous tiers
X_cont1, n_c1 = add_continuous_features(X_A, complete_folios, tier=1)
X_cont2, n_c2 = add_continuous_features(X_A, complete_folios, tier=2)
X_cont3, n_c3 = add_continuous_features(X_A, complete_folios, tier=3)

r2_cont1 = ols_r2(X_cont1, y)
r2_cont2 = ols_r2(X_cont2, y)
r2_cont3 = ols_r2(X_cont3, y)

dr2_cont1 = r2_cont1 - r2_A
dr2_cont2 = r2_cont2 - r2_A
dr2_cont3 = r2_cont3 - r2_A

f_cont1, fp_cont1 = f_test_nested(r2_cont1, r2_A, n, X_cont1.shape[1], X_A.shape[1])
f_cont2, fp_cont2 = f_test_nested(r2_cont2, r2_A, n, X_cont2.shape[1], X_A.shape[1])
f_cont3, fp_cont3 = f_test_nested(r2_cont3, r2_A, n, X_cont3.shape[1], X_A.shape[1])

print(f"\n  Tier 1 (means only):     dR^2={dr2_cont1:.4f}, F={f_cont1:.3f}, p={fp_cont1:.4f} ({n_c1} features)")
print(f"  Tier 2 (+spread):        dR^2={dr2_cont2:.4f}, F={f_cont2:.3f}, p={fp_cont2:.4f} ({n_c2} features)")
print(f"  Tier 3 (+shape/quants):  dR^2={dr2_cont3:.4f}, F={f_cont3:.3f}, p={fp_cont3:.4f} ({n_c3} features)")
print(f"  Discrete M5 (reference): dR^2={dr2_M5:.4f}, F={f_M5:.3f}, p={fp_M5:.4f} ({n_rep_dummies} dummies)")

# Relative comparison
if dr2_M5 > 0:
    cont_full_frac = dr2_cont3 / dr2_M5
    cont_tier1_frac = dr2_cont1 / dr2_M5
    tier23_add = dr2_cont3 - dr2_cont1
else:
    cont_full_frac = 0
    cont_tier1_frac = 0
    tier23_add = 0

print(f"\n  Continuous-Full captures {cont_full_frac:.1%} of M5's dR^2")
print(f"  Continuous-Tier1 captures {cont_tier1_frac:.1%} of M5's dR^2")
print(f"  Tier 2+3 add {tier23_add:.4f} over Tier 1")

# Relative margin for verdict
if dr2_M5 > 0:
    relative_margin = (dr2_M5 - dr2_cont3) / dr2_M5
else:
    relative_margin = 0
discrete_wins = relative_margin > 0.30
print(f"  Relative margin (M5 - ContFull) / M5 = {relative_margin:.3f} --> discrete {'>' if discrete_wins else '<='} continuous (30% threshold)")

t2_results = {
    'continuous_tier1': {'dR2': dr2_cont1, 'F': f_cont1, 'F_p': fp_cont1, 'n_features': n_c1},
    'continuous_tier2': {'dR2': dr2_cont2, 'F': f_cont2, 'F_p': fp_cont2, 'n_features': n_c2},
    'continuous_full': {'dR2': dr2_cont3, 'F': f_cont3, 'F_p': fp_cont3, 'n_features': n_c3},
    'discrete_M5': {'dR2': dr2_M5, 'F': f_M5, 'F_p': fp_M5, 'n_dummies': n_rep_dummies},
    'continuous_full_fraction_of_M5': cont_full_frac,
    'continuous_tier1_fraction_of_M5': cont_tier1_frac,
    'tier23_addition': tier23_add,
    'relative_margin': relative_margin,
    'discrete_wins_30pct': discrete_wins,
}


# ==================== T3: SECTION-DEPENDENT ANALYSIS ====================

print("\n" + "=" * 70)
print("T3: Section-dependent analysis")
print("=" * 70)

t3_results = {}
for sec in ['B', 'H', 'S']:
    sec_folios = [f for f in complete_folios if folio_data[f]['section'] == sec]
    n_sec = len(sec_folios)
    if n_sec < 10:
        print(f"\n  Section {sec}: n={n_sec} (too small, skipping)")
        t3_results[sec] = {'n': n_sec, 'skipped': True}
        continue

    y_sec_raw = np.array([op_profiles[f]['h_ratio'] for f in sec_folios])
    y_sec = stats.rankdata(y_sec_raw)

    # Section-specific baseline (no section dummies needed)
    X_sec = np.zeros((n_sec, 4))
    for i, f in enumerate(sec_folios):
        pfx = folio_prefix_fracs[f]
        X_sec[i, 0] = 1
        X_sec[i, 1] = pfx['qo_frac']
        X_sec[i, 2] = pfx['chsh_frac']
        X_sec[i, 3] = pfx['bare_frac']
    # Add parcount
    X_sec_base = np.zeros((n_sec, 5))
    X_sec_base[:, :4] = X_sec
    for i, f in enumerate(sec_folios):
        X_sec_base[i, 4] = folio_data[f]['n_paragraphs']

    r2_sec_base = ols_r2(X_sec_base, y_sec)

    # Use best simple predictor from T1 within this section
    feat_map = {
        'M1_MP_present': lambda f: 1.0 if folio_data[f]['mp_present'] else 0.0,
        'M2_TQ_MP_exclusion': lambda f: 1.0 if folio_data[f]['tq_mp_exclusion'] else 0.0,
        'M3_mono_vs_multi': lambda f: 1.0 if folio_data[f]['mono_type'] else 0.0,
        'M4_rep_entropy': lambda f: folio_data[f]['rep_entropy'],
    }

    sec_model_results = {}
    for mname, feat_fn in feat_map.items():
        feat_vals = np.array([feat_fn(f) for f in sec_folios])
        # Check if there's any variance
        if np.std(feat_vals) < 1e-10:
            sec_model_results[mname] = {'dR2': 0, 'F': 0, 'F_p': 1.0, 'perm_p': 1.0, 'no_variance': True}
            continue
        X_sec_full = add_single_feature(X_sec_base, feat_vals)
        r2_sec_full = ols_r2(X_sec_full, y_sec)
        dr2_sec = r2_sec_full - r2_sec_base
        f_sec, fp_sec = f_test_nested(r2_sec_full, r2_sec_base, n_sec, X_sec_full.shape[1], X_sec_base.shape[1])

        # Permutation within section (no section stratification needed, already within-section)
        pc_strata = defaultdict(list)
        for i, f in enumerate(sec_folios):
            pc_strata[parcount_bin(f)].append(i)

        null_dr2s = []
        for _ in range(N_PERM):
            perm_feat = feat_vals.copy()
            for indices in pc_strata.values():
                if len(indices) > 1:
                    subset = perm_feat[indices].copy()
                    rng.shuffle(subset)
                    perm_feat[indices] = subset
            X_perm = add_single_feature(X_sec_base, perm_feat)
            null_dr2s.append(ols_r2(X_perm, y_sec) - r2_sec_base)
        perm_p_sec = float(np.mean(np.array(null_dr2s) >= dr2_sec))

        sec_model_results[mname] = {'dR2': dr2_sec, 'F': f_sec, 'F_p': fp_sec, 'perm_p': perm_p_sec}

    # Also test M5 (full repertoire) within section
    sec_rep_types = [get_rep_type(f) for f in sec_folios]
    sec_unique_reps = set(sec_rep_types)
    if len(sec_unique_reps) > 1:
        X_sec_M5, n_sec_dummies = add_repertoire_dummies(X_sec_base, sec_folios, sec_rep_types)
        r2_sec_M5 = ols_r2(X_sec_M5, y_sec)
        dr2_sec_M5 = r2_sec_M5 - r2_sec_base
        f_sec_M5, fp_sec_M5 = f_test_nested(r2_sec_M5, r2_sec_base, n_sec, X_sec_M5.shape[1], X_sec_base.shape[1])
    else:
        dr2_sec_M5, f_sec_M5, fp_sec_M5 = 0, 0, 1.0

    sec_model_results['M5_full_repertoire'] = {'dR2': dr2_sec_M5, 'F': f_sec_M5, 'F_p': fp_sec_M5}

    t3_results[sec] = {
        'n': n_sec,
        'skipped': False,
        'baseline_r2': r2_sec_base,
        'models': convert_numpy(sec_model_results),
    }

    print(f"\n  Section {sec} (n={n_sec}):")
    print(f"    Baseline R^2: {r2_sec_base:.4f}")
    for mname, mr in sec_model_results.items():
        perm_str = f", perm_p={mr.get('perm_p', '?')}" if 'perm_p' in mr else ''
        nv_str = ' [NO VARIANCE]' if mr.get('no_variance') else ''
        print(f"    {mname}: dR^2={mr['dR2']:.4f}, F={mr['F']:.3f}, F_p={mr['F_p']:.4f}{perm_str}{nv_str}")


# ==================== T4: MP ZONE DEEP-DIVE ====================

print("\n" + "=" * 70)
print("T4: MP zone continuous deep-dive")
print("=" * 70)

mp_folios = [f for f in complete_folios if folio_data[f]['mp_present']]
no_mp_folios = [f for f in complete_folios if not folio_data[f]['mp_present']]
print(f"\n  MP-present: {len(mp_folios)}, MP-absent: {len(no_mp_folios)}")

t4_results = {'mp_present_n': len(mp_folios), 'mp_absent_n': len(no_mp_folios)}

# Compare continuous features
compare_features = {
    'h_ratio': lambda f: op_profiles[f]['h_ratio'],
    'monitoring_mean': lambda f: folio_continuous[f]['monitoring_mean'],
    'h_kernel_mean': lambda f: folio_continuous[f]['h_kernel_mean'],
    'thermal_monitoring_var': lambda f: folio_continuous[f]['thermal_monitoring_var'],
}

print("\n  Feature                | MP-pres  | MP-abs   | MW-U    | p      | direction")
print("  " + "-" * 75)
t4_comparisons = {}
for feat_name, feat_fn in compare_features.items():
    mp_vals_f = np.array([feat_fn(f) for f in mp_folios])
    nomp_vals_f = np.array([feat_fn(f) for f in no_mp_folios])
    u_stat, p_mw = stats.mannwhitneyu(mp_vals_f, nomp_vals_f, alternative='two-sided')
    direction = 'MP higher' if np.median(mp_vals_f) > np.median(nomp_vals_f) else 'MP lower'
    print(f"  {feat_name:24s} | {np.median(mp_vals_f):.4f}  | {np.median(nomp_vals_f):.4f}  | {u_stat:.0f}   | {p_mw:.4f} | {direction}")
    t4_comparisons[feat_name] = {
        'mp_median': float(np.median(mp_vals_f)),
        'mp_mean': float(np.mean(mp_vals_f)),
        'nomp_median': float(np.median(nomp_vals_f)),
        'nomp_mean': float(np.mean(nomp_vals_f)),
        'MW_U': float(u_stat),
        'MW_p': float(p_mw),
        'direction': direction,
    }

# Section-controlled comparison (residualize by section, then compare)
print("\n  Section-controlled MW (residualize by section):")
for feat_name, feat_fn in compare_features.items():
    all_vals = np.array([feat_fn(f) for f in complete_folios])
    all_sections = [folio_data[f]['section'] for f in complete_folios]
    # Compute section means and subtract
    sec_means = {}
    for sec in set(all_sections):
        sec_idx = [i for i, s in enumerate(all_sections) if s == sec]
        sec_means[sec] = np.mean(all_vals[sec_idx])
    resid = np.array([all_vals[i] - sec_means[all_sections[i]] for i in range(len(complete_folios))])
    mp_resid = resid[[i for i, f in enumerate(complete_folios) if folio_data[f]['mp_present']]]
    nomp_resid = resid[[i for i, f in enumerate(complete_folios) if not folio_data[f]['mp_present']]]
    if len(mp_resid) > 0 and len(nomp_resid) > 0:
        u_ctrl, p_ctrl = stats.mannwhitneyu(mp_resid, nomp_resid, alternative='two-sided')
        print(f"  {feat_name:24s}: p={p_ctrl:.4f} (section-controlled)")
        t4_comparisons[feat_name]['MW_p_section_controlled'] = float(p_ctrl)

# Within MP-present: does number of MP paragraphs predict h_ratio?
print("\n  Within MP-present folios: MP paragraph count vs h_ratio")
if len(mp_folios) >= 5:
    mp_counts = np.array([folio_data[f]['zone_counts'].get(3, 0) for f in mp_folios])
    mp_h_ratios = np.array([op_profiles[f]['h_ratio'] for f in mp_folios])
    if np.std(mp_counts) > 0:
        rho, rho_p = stats.spearmanr(mp_counts, mp_h_ratios)
        print(f"  Spearman rho={rho:.3f}, p={rho_p:.4f} (n={len(mp_folios)})")
        t4_results['mp_count_vs_h_ratio'] = {'rho': float(rho), 'p': float(rho_p), 'n': len(mp_folios)}
    else:
        print(f"  All MP-present folios have same MP count -- no test")
        t4_results['mp_count_vs_h_ratio'] = {'note': 'no variance in MP count'}
else:
    print(f"  Too few MP-present folios for within-group analysis")
    t4_results['mp_count_vs_h_ratio'] = {'note': f'n={len(mp_folios)} too small'}

t4_results['comparisons'] = convert_numpy(t4_comparisons)


# ==================== T5: LEAVE-ONE-OUT CROSS-VALIDATION ====================

print("\n" + "=" * 70)
print("T5: Leave-one-out cross-validation")
print("=" * 70)

def loo_rmse(build_X_fn, folio_list, y_vals):
    """LOO cross-validation, return RMSE and R^2_cv."""
    n_loo = len(folio_list)
    predictions = np.zeros(n_loo)
    for i in range(n_loo):
        train_idx = [j for j in range(n_loo) if j != i]
        train_folios = [folio_list[j] for j in train_idx]
        test_folio = [folio_list[i]]

        X_train = build_X_fn(train_folios)
        y_train = y_vals[train_idx]
        X_test = build_X_fn(test_folio)

        # Protect against singular matrices
        try:
            pred = ols_predict(X_train, y_train, X_test)
            predictions[i] = pred[0]
        except Exception:
            predictions[i] = np.mean(y_train)

    residuals = y_vals - predictions
    rmse = np.sqrt(np.mean(residuals ** 2))
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y_vals - y_vals.mean()) ** 2)
    r2_cv = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return rmse, r2_cv


# Use raw h_ratio for LOO (not rank-transformed -- we want prediction accuracy)
y_loo = y_raw.copy()

# Pre-compute fixed encodings so train/test X matrices have consistent columns
all_sections = sorted(set(folio_data[f]['section'] for f in complete_folios))
fixed_sec_to_idx = {s: i for i, s in enumerate(all_sections[1:])}
all_rep_types_sorted = sorted(set(get_rep_type(f) for f in complete_folios))
fixed_rep_to_idx = {r: i for i, r in enumerate(all_rep_types_sorted[1:])}

# LOO builder functions with fixed encodings
def loo_build_D(fl):
    return build_baseline_A(fl, fixed_sec_to_idx=fixed_sec_to_idx)

def loo_build_A(fl):
    base = build_baseline_A(fl, fixed_sec_to_idx=fixed_sec_to_idx)
    rts = [get_rep_type(f) for f in fl]
    X, _ = add_repertoire_dummies(base, fl, rts, fixed_rep_to_idx=fixed_rep_to_idx)
    return X

def loo_build_Bt1(fl):
    base = build_baseline_A(fl, fixed_sec_to_idx=fixed_sec_to_idx)
    X, _ = add_continuous_features(base, fl, tier=1)
    return X

def loo_build_Bf(fl):
    base = build_baseline_A(fl, fixed_sec_to_idx=fixed_sec_to_idx)
    X, _ = add_continuous_features(base, fl, tier=3)
    return X

def loo_build_C(fl):
    base = build_baseline_A(fl, fixed_sec_to_idx=fixed_sec_to_idx)
    rts = [get_rep_type(f) for f in fl]
    X_rep, _ = add_repertoire_dummies(base, fl, rts, fixed_rep_to_idx=fixed_rep_to_idx)
    tier1_keys = ['thermal_mean', 'monitoring_mean', 'h_kernel_mean']
    tier2_keys = ['thermal_monitoring_var', 'monitoring_range', 'thermal_range']
    tier3_keys = ['monitoring_q25', 'monitoring_q75', 'thermal_q25', 'thermal_q75',
                  'h_kernel_q25', 'h_kernel_q75']
    all_keys = tier1_keys + tier2_keys + tier3_keys
    n_feat = len(all_keys)
    X = np.zeros((len(fl), X_rep.shape[1] + n_feat))
    X[:, :X_rep.shape[1]] = X_rep
    for i, f in enumerate(fl):
        fc = folio_continuous[f]
        for j, k in enumerate(all_keys):
            X[i, X_rep.shape[1] + j] = fc[k]
    return X

# Model D (baseline only)
print("\n  Running LOO for Model D (baseline)...")
rmse_D, r2cv_D = loo_rmse(loo_build_D, complete_folios, y_loo)
print(f"  Model D (baseline): RMSE={rmse_D:.5f}, R^2_cv={r2cv_D:.4f}")

# Model A (discrete repertoire)
print("  Running LOO for Model A (discrete)...")
rmse_A, r2cv_A = loo_rmse(loo_build_A, complete_folios, y_loo)
print(f"  Model A (discrete rep): RMSE={rmse_A:.5f}, R^2_cv={r2cv_A:.4f}")

# Model B-Tier1 (continuous means only)
print("  Running LOO for Model B-Tier1 (cont means)...")
rmse_Bt1, r2cv_Bt1 = loo_rmse(loo_build_Bt1, complete_folios, y_loo)
print(f"  Model B-Tier1 (cont means): RMSE={rmse_Bt1:.5f}, R^2_cv={r2cv_Bt1:.4f}")

# Model B-Full (continuous all tiers)
print("  Running LOO for Model B-Full (cont all)...")
rmse_Bf, r2cv_Bf = loo_rmse(loo_build_Bf, complete_folios, y_loo)
print(f"  Model B-Full (cont all): RMSE={rmse_Bf:.5f}, R^2_cv={r2cv_Bf:.4f}")

# Model C (both)
print("  Running LOO for Model C (discrete + continuous)...")
rmse_C, r2cv_C = loo_rmse(loo_build_C, complete_folios, y_loo)
print(f"  Model C (both): RMSE={rmse_C:.5f}, R^2_cv={r2cv_C:.4f}")

print("\n  Summary:")
print(f"    D (baseline):     RMSE={rmse_D:.5f}  R^2_cv={r2cv_D:.4f}")
print(f"    A (discrete):     RMSE={rmse_A:.5f}  R^2_cv={r2cv_A:.4f}")
print(f"    B-T1 (cont mean): RMSE={rmse_Bt1:.5f}  R^2_cv={r2cv_Bt1:.4f}")
print(f"    B-Full (cont all):RMSE={rmse_Bf:.5f}  R^2_cv={r2cv_Bf:.4f}")
print(f"    C (both):         RMSE={rmse_C:.5f}  R^2_cv={r2cv_C:.4f}")

# In-sample R^2 for overfitting check
insample_A = ols_r2(loo_build_A(complete_folios), y_loo)
insample_Bf = ols_r2(loo_build_Bf(complete_folios), y_loo)
print(f"\n  Overfitting check:")
print(f"    Model A: in-sample R^2={insample_A:.4f}, LOO R^2={r2cv_A:.4f}, gap={insample_A - r2cv_A:.4f}")
print(f"    Model B-Full: in-sample R^2={insample_Bf:.4f}, LOO R^2={r2cv_Bf:.4f}, gap={insample_Bf - r2cv_Bf:.4f}")

t5_results = {
    'model_D': {'RMSE': rmse_D, 'R2_cv': r2cv_D},
    'model_A': {'RMSE': rmse_A, 'R2_cv': r2cv_A, 'insample_R2': insample_A},
    'model_B_tier1': {'RMSE': rmse_Bt1, 'R2_cv': r2cv_Bt1},
    'model_B_full': {'RMSE': rmse_Bf, 'R2_cv': r2cv_Bf, 'insample_R2': insample_Bf},
    'model_C': {'RMSE': rmse_C, 'R2_cv': r2cv_C},
}


# ==================== VERDICT ====================

print("\n" + "=" * 70)
print("VERDICT DETERMINATION")
print("=" * 70)

# T1 outcome
best_simple_family = models[best_simple_name]['family']
best_simple_dr2 = models[best_simple_name]['dR2']
best_simple_perm = models[best_simple_name].get('perm_p', 1.0)
m5_dr2 = dr2_M5
m5_perm = models['M5_full_repertoire'].get('perm_p', 1.0)

print(f"\n  T1: Best simple = {best_simple_name} ({best_simple_family})")
print(f"      dR^2={best_simple_dr2:.4f}, perm_p={best_simple_perm:.4f}")
print(f"      M5 dR^2={m5_dr2:.4f}, M5 improvement over best simple: {m5_dr2 - best_simple_dr2:.4f}")

# T2 outcome
print(f"  T2: Discrete M5 dR^2={dr2_M5:.4f}, Continuous-Full dR^2={dr2_cont3:.4f}")
print(f"      Relative margin: {relative_margin:.3f} (threshold: 0.30)")
print(f"      Continuous-Full captures {cont_full_frac:.1%} of M5")
print(f"      Tier 2+3 addition over Tier 1: {tier23_add:.4f}")

# T3 outcome
t3_stars_effect = False
t3_stars_only = False
for sec in ['S', 'B', 'H']:
    if sec in t3_results and not t3_results[sec].get('skipped', True):
        sec_best = max(t3_results[sec]['models'].items(),
                       key=lambda x: x[1].get('dR2', 0) if not x[1].get('no_variance') else 0)
        sec_dr2 = sec_best[1].get('dR2', 0)
        sec_perm = sec_best[1].get('perm_p', 1.0)
        print(f"  T3 {sec}: best={sec_best[0]}, dR^2={sec_dr2:.4f}, perm_p={sec_perm}")
        if sec == 'S' and sec_dr2 > 0.15 and sec_perm < 0.05:
            t3_stars_effect = True

# Check if Stars is the only section with a real effect
other_sec_effects = []
for sec in ['B', 'H']:
    if sec in t3_results and not t3_results[sec].get('skipped', True):
        sec_models = t3_results[sec]['models']
        any_sig = any(m.get('perm_p', 1.0) < 0.05 and m.get('dR2', 0) > 0.05
                      for m in sec_models.values() if not m.get('no_variance'))
        other_sec_effects.append(any_sig)
t3_stars_only = t3_stars_effect and not any(other_sec_effects)

# Determine verdict
all_weak = all(m['dR2'] < 0.05 or m.get('perm_p', 1.0) > 0.05
               for k, m in models.items() if k != 'M5_full_repertoire')

if all_weak:
    verdict = 'H_RATIO_MECHANISM_UNCLEAR'
elif cont_tier1_frac >= 0.70:  # Tier1 alone matches M5 within 30%
    verdict = 'H_RATIO_GRADIENT_EFFECT'
elif not discrete_wins:  # Continuous-Full within 30% of M5
    if tier23_add > 0.03:  # Tier 2+3 add substantially
        verdict = 'H_RATIO_HETEROGENEITY_EFFECT'
    else:
        verdict = 'H_RATIO_GRADIENT_EFFECT'
elif best_simple_family == 'Presence':
    verdict = 'H_RATIO_BUNDLE_EFFECT'
elif best_simple_family == 'Breadth':
    verdict = 'H_RATIO_NARROWNESS_EFFECT'
else:
    verdict = 'H_RATIO_MECHANISM_UNCLEAR'

if t3_stars_only:
    verdict += '_STARS_SPECIFIC'

print(f"\n  --> VERDICT: {verdict}")

# Collect descriptive stats
mp_present_count = sum(1 for f in complete_folios if folio_data[f]['mp_present'])
print(f"\n  Descriptive: {mp_present_count}/{len(complete_folios)} folios have MP paragraphs")


# ==================== SAVE RESULTS ====================

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

results = {
    'phase': 'H_RATIO_REPERTOIRE_MECHANISM (Phase 609)',
    'predictions_sha256': pred_hash,
    'n_folios': len(complete_folios),
    'n_paragraphs_analyzed': len(par_continuous),
    'verdict': verdict,
    'T1_mechanism_tournament': convert_numpy(t1_results),
    'T2_continuous_vs_discrete': convert_numpy(t2_results),
    'T3_section_dependence': convert_numpy(t3_results),
    'T4_mp_deep_dive': convert_numpy(t4_results),
    'T5_loo_crossvalidation': convert_numpy(t5_results),
}

out_path = RESULTS_DIR / 'h_ratio_mechanism_results.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=convert_numpy)

print(f"\nResults written to {out_path}")
print(f"\n=== Phase 609 COMPLETE: {verdict} ===")
