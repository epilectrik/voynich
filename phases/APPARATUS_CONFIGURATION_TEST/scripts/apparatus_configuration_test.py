#!/usr/bin/env python3
"""
Phase 589: APPARATUS_CONFIGURATION_TEST
Do A folios parameterize apparatus? Tests A→B apparatus connection through
PP MIDDLE overlap, with bridge/dark decomposition.

Tests:
  T1: PP similarity predicts apparatus manifold distance (Mantel test)
  T2: PP content predicts apparatus axes (F-params + profiles, 10 axes)
  T3: Section mediation test (within/between section)
"""

import sys, json, functools, warnings, re, time
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore')

from scripts.voynich import Transcript, Morphology, RecordAnalyzer, load_middle_classes
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from numpy.linalg import lstsq

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
t0 = time.time()

# ============================================================
# STAGE 0: Data Loading
# ============================================================

print("=" * 70)
print("Phase 589: APPARATUS_CONFIGURATION_TEST")
print("Do A Folios Parameterize Apparatus?")
print("=" * 70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()
ri_middles, pp_middles = load_middle_classes()

# --- Load bridge and dark MIDDLEs ---
print("\n  Loading bridge/dark MIDDLE sets...")
with open(PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' /
          'results' / 'bridge_selection.json') as f:
    bridge_data = json.load(f)
bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

with open(PROJECT_ROOT / 'data' / 'dark_pipeline_middles.json') as f:
    dark_data = json.load(f)
dark_set = set(dark_data['middles'])

print(f"  Bridge MIDDLEs: {len(bridge_set)}")
print(f"  Dark MIDDLEs: {len(dark_set)}")
print(f"  Overlap: {len(bridge_set & dark_set)}")  # Should be 0

# --- Load apparatus data ---
print("\n  Loading apparatus data...")

# Manifold PC scores (76 folios, PC1-PC5 = 80% variance)
with open(PROJECT_ROOT / 'phases' / 'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS' /
          'results' / 't1_manifold_embedding.json') as f:
    manifold_data = json.load(f)
manifold_scores = manifold_data['space_A']['folio_scores']
MANIFOLD_PCS = ['PC1', 'PC2', 'PC3', 'PC4', 'PC5']
manifold_folios = set(manifold_scores.keys())
print(f"  Manifold folios: {len(manifold_folios)}")

# F-parameters (76 folios, F1-F5)
with open(PROJECT_ROOT / 'phases' / 'PRODUCTIVE_DISRUPTION_EXPANSION' /
          'results' / 't1_full_scale_setup.json') as f:
    fparam_data = json.load(f)
fparam_configs = fparam_data['folio_configs']
F_PARAMS = ['F1', 'F2', 'F3', 'F4_raw', 'F5']
fparam_folios = set(fparam_configs.keys())
print(f"  F-parameter folios: {len(fparam_folios)}")

# Apparatus profiles (82 folios, 5 profiles)
with open(PROJECT_ROOT / 'phases' / 'APPARATUS_VOCABULARY_CLASSIFICATION' /
          'results' / 'apparatus_profiles.json') as f:
    profile_data = json.load(f)
profile_scores = profile_data['folio_scores']
PROFILES = ['DISTILLATION', 'SEALED_VESSEL', 'SUSTAINED_HEAT', 'PRECISION', 'DIRECT_FIRE']
profile_folios = set(profile_scores.keys())
print(f"  Profile folios: {len(profile_folios)}")

# B folios with ALL apparatus data
b_apparatus_folios = manifold_folios & fparam_folios & profile_folios
print(f"  B folios with all data: {len(b_apparatus_folios)}")

# --- Build B folio MIDDLE vocabularies ---
print("\n  Building B folio MIDDLE vocabularies...")
b_folio_middles = defaultdict(set)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_folio_middles[token.folio].add(m.middle)

# Restrict to B folios that have apparatus data
b_folios_list = sorted(b_apparatus_folios & set(b_folio_middles.keys()))
print(f"  B folios with MIDDLE vocab + apparatus: {len(b_folios_list)}")

# --- Build A folio PP sets ---
print("  Building A folio PP sets...")

def get_section(folio):
    match = re.search(r'\d+', folio)
    if not match:
        return 'OTHER'
    num = int(match.group())
    if num <= 11: return 'HERBAL_1'
    elif num <= 25: return 'HERBAL_2'
    elif num <= 38: return 'HERBAL_3'
    elif num <= 66: return 'HERBAL_4'
    else: return 'PHARMA'

folio_pp_sets = defaultdict(set)
folio_section_map = {}

for record in analyzer.iter_records():
    section = get_section(record.folio)
    folio_section_map[record.folio] = section
    for t in record.tokens:
        m = morph.extract(t.word)
        if m.middle and m.middle in pp_middles:
            folio_pp_sets[record.folio].add(m.middle)

a_folios = sorted(folio_pp_sets.keys())
n_a = len(a_folios)
pp_sizes = [len(folio_pp_sets[f]) for f in a_folios]
print(f"  A folios: {n_a}")
print(f"  PP pool sizes: mean={np.mean(pp_sizes):.1f}, range=[{min(pp_sizes)}, {max(pp_sizes)}]")

# --- Partition PP sets into bridge/dark/other ---
print("\n  Partitioning PP sets (bridge / dark / other)...")
folio_bridge_pps = {}
folio_dark_pps = {}
folio_other_pps = {}

bridge_counts = []
dark_counts = []
other_counts = []

for folio in a_folios:
    pp_set = folio_pp_sets[folio]
    b_pp = pp_set & bridge_set
    d_pp = pp_set & dark_set
    o_pp = pp_set - bridge_set - dark_set
    folio_bridge_pps[folio] = b_pp
    folio_dark_pps[folio] = d_pp
    folio_other_pps[folio] = o_pp
    bridge_counts.append(len(b_pp))
    dark_counts.append(len(d_pp))
    other_counts.append(len(o_pp))

print(f"  Bridge PPs per folio: mean={np.mean(bridge_counts):.1f}, range=[{min(bridge_counts)}, {max(bridge_counts)}]")
print(f"  Dark PPs per folio: mean={np.mean(dark_counts):.1f}, range=[{min(dark_counts)}, {max(dark_counts)}]")
print(f"  Other PPs per folio: mean={np.mean(other_counts):.1f}, range=[{min(other_counts)}, {max(other_counts)}]")
print(f"  Bridge+dark coverage: {(np.mean(bridge_counts)+np.mean(dark_counts))/np.mean(pp_sizes)*100:.1f}%")

# --- Compute A→B coverage matrices (3 variants) ---
print("\n  Computing A→B coverage matrices (3 variants)...")

def compute_coverage_matrix(a_folios_list, b_folios_list, pp_getter):
    """Compute coverage(A,B) = |PP_A ∩ MID_B| / |MID_B| for all pairs."""
    n_a = len(a_folios_list)
    n_b = len(b_folios_list)
    cov = np.zeros((n_a, n_b))
    for i, a_f in enumerate(a_folios_list):
        pp_set = pp_getter(a_f)
        for j, b_f in enumerate(b_folios_list):
            b_mids = b_folio_middles[b_f]
            if len(b_mids) > 0:
                cov[i, j] = len(pp_set & b_mids) / len(b_mids)
    return cov

cov_full = compute_coverage_matrix(a_folios, b_folios_list, lambda f: folio_pp_sets[f])
cov_bridge = compute_coverage_matrix(a_folios, b_folios_list, lambda f: folio_bridge_pps[f])
cov_dark = compute_coverage_matrix(a_folios, b_folios_list, lambda f: folio_dark_pps[f])

print(f"  Full coverage: mean={cov_full.mean():.4f}, range=[{cov_full.min():.4f}, {cov_full.max():.4f}]")
print(f"  Bridge coverage: mean={cov_bridge.mean():.4f}")
print(f"  Dark coverage: mean={cov_dark.mean():.4f}")

# --- Build B folio apparatus vectors ---
print("  Building B folio apparatus vectors...")

# Manifold positions (5D)
b_manifold = np.zeros((len(b_folios_list), 5))
for j, bf in enumerate(b_folios_list):
    scores = manifold_scores[bf]
    b_manifold[j] = [scores[pc] for pc in MANIFOLD_PCS]

# F-parameters (5D)
b_fparams = np.zeros((len(b_folios_list), 5))
for j, bf in enumerate(b_folios_list):
    cfg = fparam_configs[bf]
    b_fparams[j] = [cfg[fp] for fp in F_PARAMS]

# Apparatus profiles (5D)
b_profiles = np.zeros((len(b_folios_list), 5))
for j, bf in enumerate(b_folios_list):
    scores = profile_scores[bf]
    b_profiles[j] = [scores[p] for p in PROFILES]

# --- Compute A folio apparatus centroids (coverage-weighted) ---
print("  Computing apparatus centroids (3 variants)...")

def compute_centroids(cov_matrix, b_vectors):
    """Coverage-weighted centroid: Σ cov(a,b) * vec(b) / Σ cov(a,b)."""
    n_a = cov_matrix.shape[0]
    n_dims = b_vectors.shape[1]
    centroids = np.zeros((n_a, n_dims))
    for i in range(n_a):
        weights = cov_matrix[i]
        w_sum = weights.sum()
        if w_sum > 0:
            centroids[i] = (weights[:, None] * b_vectors).sum(axis=0) / w_sum
    return centroids

centroid_full = compute_centroids(cov_full, b_manifold)
centroid_bridge = compute_centroids(cov_bridge, b_manifold)
centroid_dark = compute_centroids(cov_dark, b_manifold)

# Also compute centroids for F-params and profiles (full coverage only for T2)
centroid_fparam = compute_centroids(cov_full, b_fparams)
centroid_profile = compute_centroids(cov_full, b_profiles)

# Bridge/dark centroids for F-params + profiles
centroid_fparam_bridge = compute_centroids(cov_bridge, b_fparams)
centroid_fparam_dark = compute_centroids(cov_dark, b_fparams)
centroid_profile_bridge = compute_centroids(cov_bridge, b_profiles)
centroid_profile_dark = compute_centroids(cov_dark, b_profiles)

print(f"\n  Stage 0 complete ({time.time()-t0:.1f}s)")

# ============================================================
# HELPER: Mantel Test
# ============================================================

def mantel_test(dist_a, dist_b, n_perms=10000, seed=42):
    """Mantel test: correlation between two distance matrices.
    Returns (r_obs, p_value, r_null_mean, r_null_std)."""
    rng = np.random.default_rng(seed)
    n = dist_a.shape[0]
    # Extract upper triangle
    idx = np.triu_indices(n, k=1)
    a_flat = dist_a[idx]
    b_flat = dist_b[idx]

    # Observed correlation
    r_obs = np.corrcoef(a_flat, b_flat)[0, 1]

    # Permutation test
    r_nulls = np.empty(n_perms)
    for p in range(n_perms):
        perm = rng.permutation(n)
        b_perm = dist_b[np.ix_(perm, perm)]
        r_nulls[p] = np.corrcoef(a_flat, b_perm[idx])[0, 1]

    p_val = (np.sum(r_nulls >= r_obs) + 1) / (n_perms + 1)
    return float(r_obs), float(p_val), float(r_nulls.mean()), float(r_nulls.std())


def partial_mantel(dist_a, dist_b, control_dists, n_perms=10000, seed=42):
    """Partial Mantel: residualize both matrices against controls, then Mantel."""
    n = dist_a.shape[0]
    idx = np.triu_indices(n, k=1)
    a_flat = dist_a[idx]
    b_flat = dist_b[idx]

    # Build control matrix
    controls = np.column_stack([cd[idx] for cd in control_dists])
    A_mat = np.column_stack([controls, np.ones(len(a_flat))])

    # Residualize
    res_a = a_flat - A_mat @ lstsq(A_mat, a_flat, rcond=None)[0]
    res_b = b_flat - A_mat @ lstsq(A_mat, b_flat, rcond=None)[0]

    r_obs = np.corrcoef(res_a, res_b)[0, 1]

    # Permutation on residuals
    rng = np.random.default_rng(seed)
    r_nulls = np.empty(n_perms)
    for p in range(n_perms):
        perm = rng.permutation(len(res_a))
        r_nulls[p] = np.corrcoef(res_a, res_b[perm])[0, 1]

    p_val = (np.sum(r_nulls >= r_obs) + 1) / (n_perms + 1)
    return float(r_obs), float(p_val)


# ============================================================
# TEST 1: PP Similarity Predicts Apparatus Manifold Distance
# ============================================================

print(f"\n{'='*70}")
print("  TEST 1: PP Similarity vs Apparatus Manifold Distance (Mantel)")
print(f"{'='*70}")

# Build PP distance matrices (1 - Jaccard)
def build_jaccard_dist(folios, pp_getter):
    n = len(folios)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            s_i = pp_getter(folios[i])
            s_j = pp_getter(folios[j])
            union = s_i | s_j
            jaccard = len(s_i & s_j) / len(union) if union else 0
            dist[i, j] = dist[j, i] = 1.0 - jaccard
    return dist

pp_dist_full = build_jaccard_dist(a_folios, lambda f: folio_pp_sets[f])
pp_dist_bridge = build_jaccard_dist(a_folios, lambda f: folio_bridge_pps[f])
pp_dist_dark = build_jaccard_dist(a_folios, lambda f: folio_dark_pps[f])

# Build apparatus centroid distance matrices (Euclidean)
def build_centroid_dist(centroids):
    return squareform(pdist(centroids, 'euclidean'))

app_dist_full = build_centroid_dist(centroid_full)
app_dist_bridge = build_centroid_dist(centroid_bridge)
app_dist_dark = build_centroid_dist(centroid_dark)

# Build control distance matrices
pool_sizes = np.array([len(folio_pp_sets[f]) for f in a_folios], dtype=float)
pool_dist = np.abs(pool_sizes[:, None] - pool_sizes[None, :])

sections = [folio_section_map[f] for f in a_folios]
section_dist = np.zeros((n_a, n_a))
for i in range(n_a):
    for j in range(i + 1, n_a):
        section_dist[i, j] = section_dist[j, i] = 0.0 if sections[i] == sections[j] else 1.0

# Run Mantel tests
print("\n  --- Full PP ---")
r_full, p_full, r_null_mean, r_null_std = mantel_test(pp_dist_full, app_dist_full)
print(f"  Raw Mantel: r={r_full:.4f}, p={p_full:.4f}")
print(f"  Null distribution: mean={r_null_mean:.4f}, std={r_null_std:.4f}")

r_full_partial, p_full_partial = partial_mantel(
    pp_dist_full, app_dist_full, [pool_dist, section_dist])
print(f"  Partial Mantel (size + section): r={r_full_partial:.4f}, p={p_full_partial:.4f}")

print("\n  --- Bridge PP only ---")
r_bridge, p_bridge, _, _ = mantel_test(pp_dist_bridge, app_dist_bridge)
print(f"  Raw Mantel: r={r_bridge:.4f}, p={p_bridge:.4f}")
r_bridge_partial, p_bridge_partial = partial_mantel(
    pp_dist_bridge, app_dist_bridge, [pool_dist, section_dist])
print(f"  Partial Mantel: r={r_bridge_partial:.4f}, p={p_bridge_partial:.4f}")

print("\n  --- Dark PP only ---")
r_dark, p_dark, _, _ = mantel_test(pp_dist_dark, app_dist_dark)
print(f"  Raw Mantel: r={r_dark:.4f}, p={p_dark:.4f}")
r_dark_partial, p_dark_partial = partial_mantel(
    pp_dist_dark, app_dist_dark, [pool_dist, section_dist])
print(f"  Partial Mantel: r={r_dark_partial:.4f}, p={p_dark_partial:.4f}")

# T1 pass criteria
t1_pass = bool(
    (p_full < 0.001 and r_full > 0.15) or
    (p_bridge < 0.001 and r_bridge > 0.15) or
    (p_dark < 0.001 and r_dark > 0.15)
)
print(f"\n  T1 verdict: {'PASS' if t1_pass else 'FAIL'}")

# ============================================================
# TEST 2: PP Content Predicts Apparatus Axes (10-axis)
# ============================================================

print(f"\n{'='*70}")
print("  TEST 2: PP Content Predicts Apparatus Axes (10 axes)")
print(f"{'='*70}")

# Combine F-params and profiles into 10 axes
AXIS_NAMES = [f'F_{fp}' for fp in F_PARAMS] + [f'P_{p}' for p in PROFILES]
AXIS_LABELS = F_PARAMS + PROFILES

# Per-A-folio axis values (coverage-weighted means)
a_axis_full = np.hstack([centroid_fparam, centroid_profile])      # (n_a, 10)
a_axis_bridge = np.hstack([centroid_fparam_bridge, centroid_profile_bridge])
a_axis_dark = np.hstack([centroid_fparam_dark, centroid_profile_dark])

# Build PP Jaccard arrays for all pairs (flattened upper triangle)
n_pairs = n_a * (n_a - 1) // 2
idx = np.triu_indices(n_a, k=1)

jaccard_full_flat = 1.0 - pp_dist_full[idx]  # Jaccard = 1 - distance
jaccard_bridge_flat = 1.0 - pp_dist_bridge[idx]
jaccard_dark_flat = 1.0 - pp_dist_dark[idx]

same_section_flat = 1.0 - section_dist[idx]
pool_size_flat = pool_dist[idx]

# For each axis, compute axis-value distance and correlate with PP Jaccard
BONFERRONI = 10
t2_results_per_axis = []

for ax_idx in range(10):
    ax_name = AXIS_LABELS[ax_idx]
    vals_full = a_axis_full[:, ax_idx]
    vals_bridge = a_axis_bridge[:, ax_idx]
    vals_dark = a_axis_dark[:, ax_idx]

    # Axis distance (absolute difference)
    ax_dist_full = np.abs(vals_full[idx[0]] - vals_full[idx[1]])
    ax_dist_bridge = np.abs(vals_bridge[idx[0]] - vals_bridge[idx[1]])
    ax_dist_dark = np.abs(vals_dark[idx[0]] - vals_dark[idx[1]])

    # Spearman: PP Jaccard vs axis distance (negative = similar PP → similar axis)
    rho_full, p_rho_full = stats.spearmanr(jaccard_full_flat, ax_dist_full)
    rho_bridge, p_rho_bridge = stats.spearmanr(jaccard_bridge_flat, ax_dist_bridge)
    rho_dark, p_rho_dark = stats.spearmanr(jaccard_dark_flat, ax_dist_dark)

    # Partial Spearman controlling for pool size + section
    controls = np.column_stack([pool_size_flat, same_section_flat])
    A_mat = np.column_stack([controls, np.ones(n_pairs)])

    rank_j = stats.rankdata(jaccard_full_flat)
    rank_d = stats.rankdata(ax_dist_full)
    res_j = rank_j - A_mat @ lstsq(A_mat, rank_j, rcond=None)[0]
    res_d = rank_d - A_mat @ lstsq(A_mat, rank_d, rcond=None)[0]
    partial_rho, partial_p = stats.pearsonr(res_j, res_d)

    sig_full = bool(abs(rho_full) > 0.2 and p_rho_full * BONFERRONI < 0.005)
    sig_bridge = bool(abs(rho_bridge) > 0.2 and p_rho_bridge * BONFERRONI < 0.005)
    sig_dark = bool(abs(rho_dark) > 0.2 and p_rho_dark * BONFERRONI < 0.005)

    ax_result = {
        'axis': ax_name,
        'full_rho': float(rho_full), 'full_p': float(p_rho_full), 'full_sig': sig_full,
        'bridge_rho': float(rho_bridge), 'bridge_p': float(p_rho_bridge), 'bridge_sig': sig_bridge,
        'dark_rho': float(rho_dark), 'dark_p': float(p_rho_dark), 'dark_sig': sig_dark,
        'partial_rho': float(partial_rho), 'partial_p': float(partial_p),
    }

    # Per-MIDDLE correlations: for top-5 discriminative MIDDLEs
    # Spearman of MIDDLE presence (binary) vs coverage-weighted axis value
    all_pp_in_any = set()
    for f in a_folios:
        all_pp_in_any.update(folio_pp_sets[f])

    mid_cors = []
    for mid in sorted(all_pp_in_any):
        presence = np.array([1.0 if mid in folio_pp_sets[f] else 0.0 for f in a_folios])
        if presence.sum() < 5 or presence.sum() > n_a - 5:
            continue
        r, p = stats.spearmanr(presence, vals_full)
        mid_cors.append((mid, float(r), float(p)))

    mid_cors.sort(key=lambda x: abs(x[1]), reverse=True)
    ax_result['top5_middles'] = [
        {'middle': m, 'rho': r, 'p': p, 'is_bridge': m in bridge_set, 'is_dark': m in dark_set}
        for m, r, p in mid_cors[:5]
    ]

    t2_results_per_axis.append(ax_result)

    marker = '***' if sig_full else '   '
    print(f"  {marker} {ax_name:18s}: full rho={rho_full:+.4f} (p={p_rho_full:.2e})"
          f"  bridge={rho_bridge:+.4f}  dark={rho_dark:+.4f}"
          f"  partial={partial_rho:+.4f}")

n_sig_full = sum(1 for r in t2_results_per_axis if r['full_sig'])
n_sig_bridge = sum(1 for r in t2_results_per_axis if r['bridge_sig'])
n_sig_dark = sum(1 for r in t2_results_per_axis if r['dark_sig'])

print(f"\n  Significant axes (full): {n_sig_full}/10")
print(f"  Significant axes (bridge): {n_sig_bridge}/10")
print(f"  Significant axes (dark): {n_sig_dark}/10")

t2_pass = bool(n_sig_full >= 3 or n_sig_bridge >= 3 or n_sig_dark >= 3)
print(f"\n  T2 verdict: {'PASS' if t2_pass else 'FAIL'}")

# ============================================================
# TEST 3: Section Mediation Test
# ============================================================

print(f"\n{'='*70}")
print("  TEST 3: Section Mediation")
print(f"{'='*70}")

# Within-section Mantel: restrict to same-section pairs
within_mask = section_dist == 0
between_mask = section_dist > 0

# Get unique section groups
section_groups = defaultdict(list)
for i, f in enumerate(a_folios):
    section_groups[folio_section_map[f]].append(i)

# Within-section: build sub-matrices for each section, run Mantel
print("\n  --- Within-section analysis ---")
within_pairs_pp = []
within_pairs_app = []
within_pairs_pp_bridge = []
within_pairs_app_bridge = []
within_pairs_pp_dark = []
within_pairs_app_dark = []

for sec, indices in section_groups.items():
    if len(indices) < 4:
        continue
    for ii in range(len(indices)):
        for jj in range(ii + 1, len(indices)):
            i, j = indices[ii], indices[jj]
            within_pairs_pp.append(pp_dist_full[i, j])
            within_pairs_app.append(app_dist_full[i, j])
            within_pairs_pp_bridge.append(pp_dist_bridge[i, j])
            within_pairs_app_bridge.append(app_dist_bridge[i, j])
            within_pairs_pp_dark.append(pp_dist_dark[i, j])
            within_pairs_app_dark.append(app_dist_dark[i, j])

within_pairs_pp = np.array(within_pairs_pp)
within_pairs_app = np.array(within_pairs_app)
within_pairs_pp_bridge = np.array(within_pairs_pp_bridge)
within_pairs_app_bridge = np.array(within_pairs_app_bridge)
within_pairs_pp_dark = np.array(within_pairs_pp_dark)
within_pairs_app_dark = np.array(within_pairs_app_dark)

print(f"  Within-section pairs: {len(within_pairs_pp)}")

# Within-section Spearman (Mantel on flat vectors)
if len(within_pairs_pp) > 10:
    within_rho, within_p = stats.spearmanr(within_pairs_pp, within_pairs_app)
    print(f"  Full: rho={within_rho:.4f}, p={within_p:.2e}")

    within_rho_b, within_p_b = stats.spearmanr(within_pairs_pp_bridge, within_pairs_app_bridge)
    print(f"  Bridge: rho={within_rho_b:.4f}, p={within_p_b:.2e}")

    within_rho_d, within_p_d = stats.spearmanr(within_pairs_pp_dark, within_pairs_app_dark)
    print(f"  Dark: rho={within_rho_d:.4f}, p={within_p_d:.2e}")

    # Permutation test on within-section (10,000 perms)
    rng = np.random.default_rng(42)
    r_obs_within = np.corrcoef(within_pairs_pp, within_pairs_app)[0, 1]
    r_nulls_within = np.empty(10000)
    for p_i in range(10000):
        perm = rng.permutation(len(within_pairs_pp))
        r_nulls_within[p_i] = np.corrcoef(within_pairs_pp, within_pairs_app[perm])[0, 1]
    p_perm_within = (np.sum(r_nulls_within >= r_obs_within) + 1) / 10001
    print(f"  Within-section Pearson (permuted): r={r_obs_within:.4f}, p={p_perm_within:.4f}")
else:
    within_rho, within_p = float('nan'), float('nan')
    within_rho_b, within_p_b = float('nan'), float('nan')
    within_rho_d, within_p_d = float('nan'), float('nan')
    r_obs_within, p_perm_within = float('nan'), float('nan')

# Between-section Spearman
print("\n  --- Between-section analysis ---")
between_pairs_pp = []
between_pairs_app = []

for i in range(n_a):
    for j in range(i + 1, n_a):
        if sections[i] != sections[j]:
            between_pairs_pp.append(pp_dist_full[i, j])
            between_pairs_app.append(app_dist_full[i, j])

between_pairs_pp = np.array(between_pairs_pp)
between_pairs_app = np.array(between_pairs_app)
print(f"  Between-section pairs: {len(between_pairs_pp)}")

if len(between_pairs_pp) > 10:
    between_rho, between_p = stats.spearmanr(between_pairs_pp, between_pairs_app)
    print(f"  Full: rho={between_rho:.4f}, p={between_p:.2e}")
else:
    between_rho, between_p = float('nan'), float('nan')

# Per-axis partial correlation controlling for section
print("\n  --- Per-axis partial correlations (controlling section) ---")
t3_axis_results = []
for ax_idx in range(10):
    ax_name = AXIS_LABELS[ax_idx]
    vals = a_axis_full[:, ax_idx]
    ax_dist_flat = np.abs(vals[idx[0]] - vals[idx[1]])

    # Raw
    raw_rho, raw_p = stats.spearmanr(jaccard_full_flat, ax_dist_flat)

    # Partial (control section)
    controls = np.column_stack([same_section_flat, np.ones(n_pairs)])
    rank_j = stats.rankdata(jaccard_full_flat)
    rank_d = stats.rankdata(ax_dist_flat)
    res_j = rank_j - controls @ lstsq(controls, rank_j, rcond=None)[0]
    res_d = rank_d - controls @ lstsq(controls, rank_d, rcond=None)[0]
    part_rho, part_p = stats.pearsonr(res_j, res_d)

    t3_axis_results.append({
        'axis': ax_name,
        'raw_rho': float(raw_rho), 'raw_p': float(raw_p),
        'partial_rho': float(part_rho), 'partial_p': float(part_p),
        'change': float(part_rho - raw_rho),
    })
    print(f"  {ax_name:18s}: raw={raw_rho:+.4f}  partial={part_rho:+.4f}  change={part_rho-raw_rho:+.4f}")

# T3 pass: within-section signal persists
t3_pass = bool(not np.isnan(within_rho) and abs(within_rho) > 0.10 and within_p < 0.01)
t3_label = "INDEPENDENT" if t3_pass else "SECTION_MEDIATED"
print(f"\n  T3 verdict: {t3_label}")
if not np.isnan(within_rho):
    print(f"  Within-section rho={within_rho:.4f}, p={within_p:.2e}")

# ============================================================
# SUMMARY & VERDICT
# ============================================================

print(f"\n{'='*70}")
print("  SUMMARY")
print(f"{'='*70}")

# Determine which pipeline carries the signal
bridge_stronger = r_bridge > r_dark and r_bridge > r_full * 0.5
dark_stronger = r_dark > r_bridge and r_dark > r_full * 0.5
if bridge_stronger and not dark_stronger:
    pipeline_verdict = "BRIDGE_DOMINANT"
elif dark_stronger and not bridge_stronger:
    pipeline_verdict = "DARK_DOMINANT"
elif bridge_stronger and dark_stronger:
    pipeline_verdict = "COMPLEMENTARY"
else:
    pipeline_verdict = "NEITHER_DOMINANT"

# Overall verdict
if t1_pass and t2_pass and t3_pass:
    verdict = "APPARATUS_CONFIGURATION_SUPPORTED"
elif t1_pass and t2_pass and not t3_pass:
    verdict = "SECTION_MEDIATED_APPARATUS"
elif t1_pass and not t2_pass:
    verdict = "MANIFOLD_CORRELATED_NOT_PARAMETERIZED"
elif not t1_pass and t2_pass:
    verdict = "AXIS_SPECIFIC_NOT_GLOBAL"
else:
    verdict = "NO_APPARATUS_CONNECTION"

print(f"  T1 (Mantel): full r={r_full:.4f} (p={p_full:.4f}), "
      f"bridge r={r_bridge:.4f}, dark r={r_dark:.4f} → {'PASS' if t1_pass else 'FAIL'}")
print(f"  T2 (axes): {n_sig_full}/10 full, {n_sig_bridge}/10 bridge, "
      f"{n_sig_dark}/10 dark → {'PASS' if t2_pass else 'FAIL'}")
print(f"  T3 (mediation): {t3_label}")
print(f"  Pipeline: {pipeline_verdict}")
print(f"\n  VERDICT: {verdict}")
print(f"\n  Total runtime: {time.time()-t0:.1f}s")

# ============================================================
# Save results
# ============================================================

results = {
    'phase': 589,
    'test': 'APPARATUS_CONFIGURATION_TEST',
    'metadata': {
        'n_a_folios': n_a,
        'n_b_folios': len(b_folios_list),
        'n_bridge_middles': len(bridge_set),
        'n_dark_middles': len(dark_set),
        'bridge_dark_overlap': len(bridge_set & dark_set),
        'mean_pp_pool_size': float(np.mean(pp_sizes)),
        'mean_bridge_per_folio': float(np.mean(bridge_counts)),
        'mean_dark_per_folio': float(np.mean(dark_counts)),
        'mean_other_per_folio': float(np.mean(other_counts)),
        'bridge_dark_coverage_pct': float((np.mean(bridge_counts)+np.mean(dark_counts))/np.mean(pp_sizes)*100),
        'full_coverage_mean': float(cov_full.mean()),
        'bridge_coverage_mean': float(cov_bridge.mean()),
        'dark_coverage_mean': float(cov_dark.mean()),
    },
    'T1_mantel': {
        'full': {'r': r_full, 'p': p_full, 'null_mean': r_null_mean, 'null_std': r_null_std},
        'full_partial': {'r': r_full_partial, 'p': p_full_partial},
        'bridge': {'r': r_bridge, 'p': p_bridge},
        'bridge_partial': {'r': r_bridge_partial, 'p': p_bridge_partial},
        'dark': {'r': r_dark, 'p': p_dark},
        'dark_partial': {'r': r_dark_partial, 'p': p_dark_partial},
        'passed': t1_pass,
    },
    'T2_axes': {
        'n_sig_full': n_sig_full,
        'n_sig_bridge': n_sig_bridge,
        'n_sig_dark': n_sig_dark,
        'per_axis': t2_results_per_axis,
        'passed': t2_pass,
    },
    'T3_mediation': {
        'within_section': {
            'n_pairs': len(within_pairs_pp),
            'full_rho': float(within_rho) if not np.isnan(within_rho) else None,
            'full_p': float(within_p) if not np.isnan(within_p) else None,
            'bridge_rho': float(within_rho_b) if not np.isnan(within_rho_b) else None,
            'bridge_p': float(within_p_b) if not np.isnan(within_p_b) else None,
            'dark_rho': float(within_rho_d) if not np.isnan(within_rho_d) else None,
            'dark_p': float(within_p_d) if not np.isnan(within_p_d) else None,
            'pearson_perm_r': float(r_obs_within) if not np.isnan(r_obs_within) else None,
            'pearson_perm_p': float(p_perm_within) if not np.isnan(p_perm_within) else None,
        },
        'between_section': {
            'n_pairs': len(between_pairs_pp),
            'full_rho': float(between_rho) if not np.isnan(between_rho) else None,
            'full_p': float(between_p) if not np.isnan(between_p) else None,
        },
        'per_axis_partial': t3_axis_results,
        'passed': t3_pass,
        'label': t3_label,
    },
    'pipeline_verdict': pipeline_verdict,
    'verdict': verdict,
    'runtime_seconds': float(time.time() - t0),
}

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
with open(RESULTS_DIR / 'apparatus_configuration_test.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n  Results saved to {RESULTS_DIR / 'apparatus_configuration_test.json'}")
