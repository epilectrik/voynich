"""
Phase 600: BRUNSCHWIG_CLOSURE_RESPONSE_ALIGNMENT
Tests whether historical closure demands predict Voynich closure-response phenotype.

3 historical predictor axes (CONTAINMENT_BURDEN, OPEN_INTERVENTION, RECYCLE_COMPLEXITY)
mapped to 7D Voynich closure-response vector via rank-order concordance.

Pre-registration hash: eb6824e86b0cc4c08c68f7a3c2a2ed93be637bd200cc162dc78a8e23afa1898a
"""

import json
import os
import sys
import re
import hashlib
import time
from collections import defaultdict, Counter

import numpy as np
from scipy.stats import spearmanr, mannwhitneyu, kendalltau
from scipy.spatial.distance import pdist, squareform, cosine as cosine_dist

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
PRED_HASH = 'eb6824e86b0cc4c08c68f7a3c2a2ed93be637bd200cc162dc78a8e23afa1898a'

pred_hash = hashlib.sha256(open(PRED_PATH, 'rb').read()).hexdigest()
assert pred_hash == PRED_HASH, f"PREDICTIONS.md hash mismatch: {pred_hash}"
print(f"Pre-registration verified: {PRED_HASH[:16]}...")

t0 = time.time()

# ============================================================
# 2. BRUNSCHWIG CLOSURE-BURDEN ANNOTATION
# ============================================================

print("\n=== BRUNSCHWIG CLOSURE-BURDEN ANNOTATION ===")

# Load recipes
recipe_path = os.path.join(os.path.dirname(__file__), '..', '..',
                           'BRUNSCHWIG_1512_BLIND_PREDICTION', 'results',
                           'brunschwig_1512_recipes.json')
with open(recipe_path) as f:
    recipe_data = json.load(f)

recipes = [r for r in recipe_data['recipes']
           if r['classification'] == 'recipe'
           and r['book'] not in ('front_matter', 'back_matter')]
print(f"Confirmed recipes (excl. front/back): {len(recipes)}")

# Load full English translation
eng_path = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                        'sources', 'brunschwig_1512', 'brunschwig_1512_english.txt')
with open(eng_path, encoding='utf-8') as f:
    eng_lines = f.readlines()
print(f"English translation: {len(eng_lines)} lines")

# Sort recipes by start_line to get boundaries
all_recipes_sorted = sorted(recipe_data['recipes'], key=lambda r: r['start_line'])
start_lines = [r['start_line'] for r in all_recipes_sorted]
recipe_id_to_idx = {r['id']: i for i, r in enumerate(all_recipes_sorted)}

def get_full_text(recipe):
    """Extract full recipe text from English translation."""
    idx = recipe_id_to_idx[recipe['id']]
    sl = all_recipes_sorted[idx]['start_line']
    if idx + 1 < len(all_recipes_sorted):
        el = all_recipes_sorted[idx + 1]['start_line']
    else:
        el = len(eng_lines)
    text = ' '.join(line.strip() for line in eng_lines[sl:el] if line.strip())
    return text

# Dual lexicon definitions
H1_STRICT_PATTERNS = [
    r'\bsealed\b', r'\bluted\b', r'\blutum\b', r'luto sapientiae',
    r'\bhermetically\b', r'stopped and sealed',
    r'\bpelican\b', r'\bcirculat(?:orium|ory)\b',
]
H1_BROAD_PATTERNS = H1_STRICT_PATTERNS + [
    r'\bseal\b', r'\blut(?:e|ing)\b', r'\bstopp(?:ed|er|ing)\b',
    r'\bwax(?:ed)?\b', r'\bclay\b', r'\bdough\b', r'\bpaste\b',
    r'\bhermet\b', r'close well', r'close tight', r'\bcork(?:ed)?\b',
    r'let it stand', r'let stand', r'let it rest', r'let rest',
    r'let it sit', r'leave it', r'\bputref', r'\bdigest(?:ion|ed|ing)?\b',
    r'\binfuse\b',
]

H2_STRICT_PATTERNS = [
    r'pour off', r'pour out', r'pour back', r'pour into',
    r'\btransfer\b', r'remove the', r'take off the',
    r'open the', r'opened the',
]
H2_BROAD_PATTERNS = H2_STRICT_PATTERNS + [
    r'\bstir(?:red|ring)?\b', r'add more', r'\breplenish\b',
    r'\bshake\b', r'\bcheck\b', r'\bturn\b', r'look at', r'\bobserve\b',
]

def count_patterns(text, patterns):
    """Count total matches of regex patterns in text (case-insensitive)."""
    text_lower = text.lower()
    total = 0
    for pat in patterns:
        total += len(re.findall(pat, text_lower))
    return total

# Method-class assignment (same as Phase 599)
METHOD_CLASSES = {
    'GENTLE_SUSTAINED': {'balneum_mariae', 'horse_dung', 'sun'},
    'OPEN_CYCLE_ELEVATED': {'open_fire', 'ashes', 'gentle_fire'},
    'SEALED_RECIRCULATION': {'circulation'},
    'PRECISION_CONTROLLED': {'sand_bath'},
}
# Rarity for multi-class assignment
METHOD_COUNTS = recipe_data['method_distribution']

def assign_method_class(methods):
    """Assign recipe to method class by dominant method (rarest if spanning)."""
    if not methods:
        return None
    best_class = None
    best_rarity = float('inf')
    for m in methods:
        for cls, members in METHOD_CLASSES.items():
            if m in members:
                rarity = METHOD_COUNTS.get(m, 999)
                if rarity < best_rarity:
                    best_rarity = rarity
                    best_class = cls
    return best_class

# Annotate each recipe
for r in recipes:
    text = get_full_text(r)
    wc = max(r['word_count'], 1)

    # H1: CONTAINMENT_BURDEN
    h1_strict_count = count_patterns(text, H1_STRICT_PATTERNS)
    h1_broad_count = count_patterns(text, H1_BROAD_PATTERNS)

    # Vessel boost
    vessel_boost = 0
    for v in r.get('vessels', []):
        if v in ('pelican', 'circulatorium'):
            vessel_boost += 2

    # Method boost for containment
    method_boost_h1 = 0
    for m in r.get('methods', []):
        if m in ('circulation', 'horse_dung'):
            method_boost_h1 += 1

    r['H1_strict'] = (h1_strict_count + vessel_boost + method_boost_h1) / wc * 100
    r['H1_broad'] = (h1_broad_count + vessel_boost + method_boost_h1) / wc * 100

    # H2: OPEN_INTERVENTION
    h2_strict_count = count_patterns(text, H2_STRICT_PATTERNS)
    h2_broad_count = count_patterns(text, H2_BROAD_PATTERNS)

    method_boost_h2 = 0
    for m in r.get('methods', []):
        if m in ('open_fire', 'ashes'):
            method_boost_h2 += 1

    r['H2_strict'] = (h2_strict_count + method_boost_h2) / wc * 100
    r['H2_broad'] = (h2_broad_count + method_boost_h2) / wc * 100

    # H3: RECYCLE_COMPLEXITY
    ds = r.get('distillation_steps', {})
    dr = ds.get('distill_references', 0)
    nd = ds.get('named_distillations', 0)
    r['H3'] = max(dr, nd * 2)

    # Method class
    r['method_class'] = assign_method_class(r.get('methods', []))

# Summary statistics
h1s = [r['H1_strict'] for r in recipes]
h1b = [r['H1_broad'] for r in recipes]
h2s = [r['H2_strict'] for r in recipes]
h2b = [r['H2_broad'] for r in recipes]
h3v = [r['H3'] for r in recipes]

print(f"\nH1_strict: mean={np.mean(h1s):.3f}, median={np.median(h1s):.3f}, "
      f"nonzero={sum(1 for x in h1s if x > 0)}/{len(h1s)}")
print(f"H1_broad:  mean={np.mean(h1b):.3f}, median={np.median(h1b):.3f}, "
      f"nonzero={sum(1 for x in h1b if x > 0)}/{len(h1b)}")
print(f"H2_strict: mean={np.mean(h2s):.3f}, median={np.median(h2s):.3f}, "
      f"nonzero={sum(1 for x in h2s if x > 0)}/{len(h2s)}")
print(f"H2_broad:  mean={np.mean(h2b):.3f}, median={np.median(h2b):.3f}, "
      f"nonzero={sum(1 for x in h2b if x > 0)}/{len(h2b)}")
print(f"H3:        mean={np.mean(h3v):.2f}, median={np.median(h3v):.0f}, "
      f"nonzero={sum(1 for x in h3v if x > 0)}/{len(h3v)}")

# Dual-lexicon correlation
h1_corr, h1_corr_p = spearmanr(h1s, h1b)
h2_corr, h2_corr_p = spearmanr(h2s, h2b)
print(f"\nDual-lexicon agreement:")
print(f"  H1 strict-broad Spearman: {h1_corr:.3f} (p={h1_corr_p:.4f})")
print(f"  H2 strict-broad Spearman: {h2_corr:.3f} (p={h2_corr_p:.4f})")

annotation_stable = h1_corr > 0.5 and h2_corr > 0.5
if not annotation_stable:
    print("  WARNING: ANNOTATION_UNSTABLE (correlation < 0.5)")

# Method-class prototypes
class_recipes = defaultdict(list)
for r in recipes:
    if r['method_class']:
        class_recipes[r['method_class']].append(r)

print(f"\nMethod-class recipe counts:")
class_prototypes = {}
for cls in ['GENTLE_SUSTAINED', 'OPEN_CYCLE_ELEVATED', 'SEALED_RECIRCULATION', 'PRECISION_CONTROLLED']:
    recs = class_recipes[cls]
    if recs:
        proto = np.array([
            np.mean([r['H1_strict'] for r in recs]),
            np.mean([r['H2_strict'] for r in recs]),
            np.mean([r['H3'] for r in recs]),
        ])
        class_prototypes[cls] = proto
        print(f"  {cls}: n={len(recs)}, H1={proto[0]:.3f}, H2={proto[1]:.3f}, H3={proto[2]:.2f}")

# ============================================================
# 3. S1: ANNOTATION AUDIT
# ============================================================

print("\n=== S1: ANNOTATION AUDIT ===")

# Sample 25 recipes across quartiles
h1_sorted = sorted(recipes, key=lambda r: r['H1_strict'])
h2_sorted = sorted(recipes, key=lambda r: r['H2_strict'])
n = len(recipes)
q1_h1 = h1_sorted[-5:]  # top 5 by H1
q4_h1 = h1_sorted[:5]   # bottom 5 by H1
q1_h2 = h2_sorted[-5:]  # top 5 by H2
q4_h2 = h2_sorted[:5]   # bottom 5 by H2

rng_audit = np.random.default_rng(600)
remaining_ids = set(r['id'] for r in recipes) - set(r['id'] for r in q1_h1 + q4_h1 + q1_h2 + q4_h2)
random_sample = [r for r in recipes if r['id'] in remaining_ids]
rng_audit.shuffle(random_sample)
random_5 = random_sample[:5]

audit_samples = []
for label, group in [('TOP_H1', q1_h1), ('BOT_H1', q4_h1),
                     ('TOP_H2', q1_h2), ('BOT_H2', q4_h2),
                     ('RANDOM', random_5)]:
    for r in group:
        text = get_full_text(r)
        excerpt = text[:120].replace('\n', ' ')
        audit_samples.append({
            'group': label,
            'id': r['id'],
            'heading': r['heading'][:60],
            'method_class': r['method_class'],
            'H1_strict': round(r['H1_strict'], 3),
            'H2_strict': round(r['H2_strict'], 3),
            'H3': r['H3'],
            'excerpt': excerpt,
        })
        print(f"  [{label}] {r['id']} H1s={r['H1_strict']:.2f} H2s={r['H2_strict']:.2f} "
              f"H3={r['H3']} cls={r['method_class']} -- {r['heading'][:50]}")

# ============================================================
# 4. VOYNICH DATA LOADING
# ============================================================

print("\n=== VOYNICH DATA LOADING ===")

# Manifold feature matrix
manifold_path = os.path.join(os.path.dirname(__file__), '..', '..',
                             'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS', 'results',
                             't0_feature_matrix_assembly.json')
with open(manifold_path) as f:
    manifold_data = json.load(f)

manifold_folios = manifold_data['folios']
space_a_raw = manifold_data['space_A']['raw']
space_b_raw = manifold_data['space_B']['raw']
folio_metadata = manifold_data['folio_metadata']
print(f"Manifold feature matrix: {len(manifold_folios)} folios")

# Extract CTS, DYE, PEF per folio
folio_cts = {manifold_folios[i]: space_a_raw[i][10] for i in range(len(manifold_folios))}
folio_dye = {manifold_folios[i]: space_b_raw[i][0] for i in range(len(manifold_folios))}
folio_pef = {manifold_folios[i]: space_b_raw[i][3] for i in range(len(manifold_folios))}

# Opportunity normalization covariates
opp_path = os.path.join(os.path.dirname(__file__), '..', '..',
                        'A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES', 'results',
                        't0_opportunity_normalization.json')
with open(opp_path) as f:
    opp_data = json.load(f)
opp_covariates = opp_data['covariates']
print(f"Opportunity normalization: {len(opp_covariates)} folios")

folio_dva = {f: c['mean_dv_magnitude'] for f, c in opp_covariates.items()}
folio_yga = {f: c['mean_y_gain'] for f, c in opp_covariates.items()}
folio_scf = {f: c['strong_close_fraction'] for f, c in opp_covariates.items()}

# ACS per event -> aggregate to per-folio mean
acs_path = os.path.join(os.path.dirname(__file__), '..', '..',
                        'SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE', 'results',
                        't0_acs_assembly.json')
with open(acs_path) as f:
    acs_data = json.load(f)

acs_by_folio = defaultdict(list)
for evt in acs_data['per_event_acs']:
    acs_by_folio[evt['folio']].append(evt['ACS'])
folio_acs = {f: np.mean(vals) for f, vals in acs_by_folio.items()}
print(f"ACS events: {len(acs_data['per_event_acs'])} events, {len(folio_acs)} folios")

# REGIME mapping
regime_path = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                           'data', 'regime_folio_mapping.json')
with open(regime_path) as f:
    regime_data = json.load(f)
regime_map = {f: info['regime'] for f, info in regime_data['regime_assignments'].items()}

# Section lookup
tx = Transcript()
folio_section = {}
for t in tx.currier_b():
    folio_section[t.folio] = t.section

# ============================================================
# 5. COMPUTE ey_rate AND ii_rate FROM TRANSCRIPT
# ============================================================

print("\n=== COMPUTING ey_rate AND ii_rate ===")

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

mean_ey = np.mean(list(folio_ey_rate.values()))
mean_ii = np.mean(list(folio_ii_rate.values()))
print(f"Mean ey_rate: {mean_ey:.4f} (expected ~0.1377)")
print(f"Mean ii_rate: {mean_ii:.4f} (expected ~0.0717)")
print(f"Folios with ey/ii data: {len(folio_ey_rate)}")

# ============================================================
# 6. BUILD 7D RESPONSE VECTORS AND CELLS
# ============================================================

print("\n=== BUILDING RESPONSE VECTORS ===")

# Common folio set: intersection of all data sources
common_folios = (set(manifold_folios) & set(opp_covariates.keys()) &
                 set(folio_ey_rate.keys()) & set(regime_map.keys()) &
                 set(folio_section.keys()))
# Also need ACS — some folios may have 0 events
folios_with_acs = set(folio_acs.keys())

print(f"Common folios (all sources): {len(common_folios)}")
print(f"Folios with ACS: {len(folios_with_acs & common_folios)}")

# Build per-folio 7D vectors
# [CTS, strong_close_frac, DYE, DVA, mean_ACS, ey_rate, ii_rate]
RESPONSE_NAMES = ['mean_CTS', 'strong_close_fraction', 'DYE_advantage',
                  'mean_dv_magnitude', 'mean_ACS', 'ey_rate', 'ii_rate']

folio_vectors = {}
for f in common_folios:
    acs_val = folio_acs.get(f, np.nan)  # NaN if no closure events
    vec = np.array([
        folio_cts[f],
        folio_scf[f],
        folio_dye[f],
        folio_dva[f],
        acs_val,
        folio_ey_rate[f],
        folio_ii_rate[f],
    ])
    folio_vectors[f] = vec

# Cell-to-method-class mapping (frozen)
CELL_METHOD_CLASS = {
    ('S', 'REGIME_1'): 'GENTLE_SUSTAINED',
    ('S', 'REGIME_3'): 'OPEN_CYCLE_ELEVATED',
    ('H', 'REGIME_2'): 'SEALED_RECIRCULATION',
    ('H', 'REGIME_4'): 'PRECISION_CONTROLLED',
    ('H', 'REGIME_3'): 'OPEN_CYCLE_ELEVATED',
}

# Build cells
cells = {}
for f in common_folios:
    sec = folio_section[f]
    reg = regime_map[f]
    key = (sec, reg)
    if key in CELL_METHOD_CLASS:
        if key not in cells:
            cells[key] = []
        cells[key].append(f)

print(f"\nViable cells:")
cell_names = sorted(cells.keys())
for key in cell_names:
    print(f"  {key[0]}:{key[1]} (n={len(cells[key])}) -> {CELL_METHOD_CLASS[key]}")

# Compute cell centroids (raw, then z-score for distance)
cell_centroids_raw = {}
for key in cell_names:
    vecs = [folio_vectors[f] for f in cells[key] if not np.any(np.isnan(folio_vectors[f]))]
    if vecs:
        cell_centroids_raw[key] = np.mean(vecs, axis=0)
    else:
        cell_centroids_raw[key] = np.full(7, np.nan)

# Z-score centroids across cells (for each dimension)
centroid_matrix = np.array([cell_centroids_raw[key] for key in cell_names])
centroid_means = np.nanmean(centroid_matrix, axis=0)
centroid_stds = np.nanstd(centroid_matrix, axis=0)
centroid_stds[centroid_stds == 0] = 1  # avoid div by zero

cell_centroids_z = {}
for i, key in enumerate(cell_names):
    cell_centroids_z[key] = (centroid_matrix[i] - centroid_means) / centroid_stds

print(f"\nCell centroids (raw):")
for key in cell_names:
    v = cell_centroids_raw[key]
    print(f"  {key[0]}:{key[1]}: " + " ".join(f"{RESPONSE_NAMES[j]}={v[j]:.4f}" for j in range(7)))

# ============================================================
# 7. S2: SAFETY BALANCE ORDERING
# ============================================================

print("\n=== S2: SAFETY BALANCE ORDERING ===")

cell_safety_balance = {}
for key in cell_names:
    ey_vals = [folio_ey_rate[f] for f in cells[key]]
    ii_vals = [folio_ii_rate[f] for f in cells[key]]
    balance = np.mean(ey_vals) - np.mean(ii_vals)
    cell_safety_balance[key] = balance
    print(f"  {key[0]}:{key[1]}: ey={np.mean(ey_vals):.4f}, ii={np.mean(ii_vals):.4f}, "
          f"balance={balance:.4f}")

# Hypothesized ordering (not enforced): H:R2 > S:R1 > H:R4 > H:R3 >= S:R3
hypothesized_order = [('H', 'REGIME_2'), ('S', 'REGIME_1'), ('H', 'REGIME_4'),
                      ('H', 'REGIME_3'), ('S', 'REGIME_3')]
observed_order = sorted(cell_names, key=lambda k: cell_safety_balance[k], reverse=True)
print(f"  Hypothesized: {[f'{k[0]}:{k[1]}' for k in hypothesized_order]}")
print(f"  Observed:     {[f'{k[0]}:{k[1]}' for k in observed_order]}")

hyp_ranks = {k: i for i, k in enumerate(hypothesized_order)}
obs_ranks = {k: i for i, k in enumerate(observed_order)}
common_cells = set(hyp_ranks.keys()) & set(obs_ranks.keys())
hyp_r = [hyp_ranks[k] for k in sorted(common_cells)]
obs_r = [obs_ranks[k] for k in sorted(common_cells)]
s2_tau, s2_tau_p = kendalltau(hyp_r, obs_r)
print(f"  Kendall tau: {s2_tau:.3f} (p={s2_tau_p:.4f})")

# ============================================================
# 8. P1: MANTEL GEOMETRY CONCORDANCE
# ============================================================

print("\n=== P1: MANTEL GEOMETRY CONCORDANCE ===")

# Predicted 3D distance matrix from method-class prototypes
pred_vecs = []
for key in cell_names:
    cls = CELL_METHOD_CLASS[key]
    pred_vecs.append(class_prototypes[cls])
pred_matrix = np.array(pred_vecs)

# Observed 7D distance matrix from z-scored centroids
obs_vecs = np.array([cell_centroids_z[key] for key in cell_names])

# Handle NaN in observed (replace with 0 for distance computation)
obs_vecs_clean = np.nan_to_num(obs_vecs, nan=0.0)

def upper_tri(mat):
    """Extract upper triangle of distance matrix."""
    n = mat.shape[0]
    idx = np.triu_indices(n, k=1)
    return mat[idx]

def mantel_test(pred_vecs, obs_vecs, n_perms=9999, metric='euclidean', seed=42):
    """Mantel test between predicted and observed distance matrices."""
    pred_dist = squareform(pdist(pred_vecs, metric=metric))
    obs_dist = squareform(pdist(obs_vecs, metric=metric))

    pred_flat = upper_tri(pred_dist)
    obs_flat = upper_tri(obs_dist)

    r_obs, _ = spearmanr(pred_flat, obs_flat)

    n = pred_vecs.shape[0]
    rng = np.random.default_rng(seed)
    count_ge = 0
    for _ in range(n_perms):
        perm = rng.permutation(n)
        obs_perm = obs_dist[np.ix_(perm, perm)]
        obs_perm_flat = upper_tri(obs_perm)
        r_perm, _ = spearmanr(pred_flat, obs_perm_flat)
        if r_perm >= r_obs:
            count_ge += 1
    p = (count_ge + 1) / (n_perms + 1)
    return r_obs, p, pred_dist, obs_dist

# Primary: Euclidean
p1_r_euc, p1_p_euc, p1_pred_dist, p1_obs_dist = mantel_test(
    pred_matrix, obs_vecs_clean, n_perms=9999, metric='euclidean', seed=42)
print(f"  Primary (Euclidean):  r={p1_r_euc:.4f}, p={p1_p_euc:.4f}")

# Sensitivity: Cosine
p1_r_cos, p1_p_cos, _, _ = mantel_test(
    pred_matrix, obs_vecs_clean, n_perms=9999, metric='cosine', seed=43)
print(f"  Sensitivity (Cosine): r={p1_r_cos:.4f}, p={p1_p_cos:.4f}")

p1_pass = p1_r_euc > 0.30 and p1_p_euc < 0.05
print(f"  P1 VERDICT: {'PASS' if p1_pass else 'FAIL'} (threshold: r>0.30 AND p<0.05)")

# ============================================================
# 9. P2: STARS R1 vs R3 DIRECTIONAL CONCORDANCE
# ============================================================

print("\n=== P2: STARS R1 vs R3 DIRECTIONAL CONCORDANCE ===")

stars_r1 = cells.get(('S', 'REGIME_1'), [])
stars_r3 = cells.get(('S', 'REGIME_3'), [])
print(f"  S:R1 n={len(stars_r1)}, S:R3 n={len(stars_r3)}")

# 4 pre-registered axes: ey_rate R1>R3, ii_rate R1<R3, DYE R1>R3, strong_close_frac R1>R3
p2_axes = [
    ('ey_rate', folio_ey_rate, 'greater'),      # R1 > R3
    ('ii_rate', folio_ii_rate, 'less'),          # R1 < R3
    ('DYE_advantage', folio_dye, 'greater'),     # R1 > R3
    ('strong_close_fraction', folio_scf, 'greater'),  # R1 > R3
]

p2_concordant = 0
p2_results = []
for name, data_dict, direction in p2_axes:
    r1_vals = [data_dict[f] for f in stars_r1 if f in data_dict]
    r3_vals = [data_dict[f] for f in stars_r3 if f in data_dict]
    r1_mean = np.mean(r1_vals)
    r3_mean = np.mean(r3_vals)

    if direction == 'greater':
        observed_concordant = r1_mean > r3_mean
        alt = 'greater'
    else:
        observed_concordant = r1_mean < r3_mean
        alt = 'less'

    stat, p_val = mannwhitneyu(r1_vals, r3_vals, alternative=alt)
    if observed_concordant:
        p2_concordant += 1

    p2_results.append({
        'axis': name,
        'R1_mean': float(r1_mean),
        'R3_mean': float(r3_mean),
        'predicted_direction': direction,
        'observed_concordant': bool(observed_concordant),
        'U': float(stat),
        'p': float(p_val),
    })
    print(f"  {name}: R1={r1_mean:.4f}, R3={r3_mean:.4f}, "
          f"pred={direction}, match={'YES' if observed_concordant else 'NO'}, p={p_val:.4f}")

# Combined permutation test
rng2 = np.random.default_rng(123)
stars_all = stars_r1 + stars_r3
n_r1 = len(stars_r1)
n_perm_ge = 0
n_perms_p2 = 5000

for _ in range(n_perms_p2):
    perm = rng2.permutation(len(stars_all))
    perm_r1 = [stars_all[i] for i in perm[:n_r1]]
    perm_r3 = [stars_all[i] for i in perm[n_r1:]]

    perm_concordant = 0
    for name, data_dict, direction in p2_axes:
        r1v = np.mean([data_dict[f] for f in perm_r1 if f in data_dict])
        r3v = np.mean([data_dict[f] for f in perm_r3 if f in data_dict])
        if direction == 'greater' and r1v > r3v:
            perm_concordant += 1
        elif direction == 'less' and r1v < r3v:
            perm_concordant += 1

    if perm_concordant >= p2_concordant:
        n_perm_ge += 1

p2_combined_p = (n_perm_ge + 1) / (n_perms_p2 + 1)
p2_pass = p2_concordant >= 3 and p2_combined_p < 0.05
print(f"\n  Concordant: {p2_concordant}/4, combined p={p2_combined_p:.4f}")
print(f"  P2 VERDICT: {'PASS' if p2_pass else 'FAIL'} (threshold: >=3/4 AND combined p<0.05)")

# Check safety reversal
ey_result = next(r for r in p2_results if r['axis'] == 'ey_rate')
safety_reversal = not ey_result['observed_concordant']
if safety_reversal:
    print("  WARNING: SAFETY_REVERSAL -- ey_rate direction wrong, undermines C1735")

# ============================================================
# 10. P3: RANK CONCORDANCE
# ============================================================

print("\n=== P3: HISTORICAL RANK CONCORDANCE ===")

# Method classes ranked by H1_strict (containment)
class_h1 = {cls: class_prototypes[cls][0] for cls in class_prototypes}
class_h2 = {cls: class_prototypes[cls][1] for cls in class_prototypes}

containment_ranked = sorted(class_h1.keys(), key=lambda c: class_h1[c], reverse=True)
intervention_ranked = sorted(class_h2.keys(), key=lambda c: class_h2[c], reverse=True)

print(f"  CONTAINMENT rank: {containment_ranked}")
print(f"  INTERVENTION rank: {intervention_ranked}")

# Map cells to ranks
# Note: H:R3 and S:R3 share OPEN_CYCLE_ELEVATED → same rank
cell_containment_rank = {}
cell_intervention_rank = {}
for key in cell_names:
    cls = CELL_METHOD_CLASS[key]
    cell_containment_rank[key] = containment_ranked.index(cls)
    cell_intervention_rank[key] = intervention_ranked.index(cls)

# Voynich response ranks
cell_ey = {key: cell_centroids_raw[key][5] for key in cell_names}  # ey_rate
cell_ii = {key: cell_centroids_raw[key][6] for key in cell_names}  # ii_rate
cell_cts = {key: cell_centroids_raw[key][0] for key in cell_names}  # mean_CTS

ey_ranked = sorted(cell_names, key=lambda k: cell_ey[k], reverse=True)
ii_ranked = sorted(cell_names, key=lambda k: cell_ii[k], reverse=True)  # will invert
cts_ranked = sorted(cell_names, key=lambda k: cell_cts[k], reverse=True)

# Compute Kendall taus
# 1. CONTAINMENT_RANK vs ey_rate rank
cont_ranks_arr = [cell_containment_rank[k] for k in cell_names]
ey_ranks_arr = [ey_ranked.index(k) for k in cell_names]
tau1, tau1_p = kendalltau(cont_ranks_arr, ey_ranks_arr)
# Note: both ranked highest=0, so positive tau = concordant

# 2. INTERVENTION_RANK vs ii_rate rank (inverted: high intervention → high ii)
int_ranks_arr = [cell_intervention_rank[k] for k in cell_names]
ii_ranks_arr = [ii_ranked.index(k) for k in cell_names]
tau2, tau2_p = kendalltau(int_ranks_arr, ii_ranks_arr)

# 3. CONTAINMENT_RANK vs mean_CTS rank
cts_ranks_arr = [cts_ranked.index(k) for k in cell_names]
tau3, tau3_p = kendalltau(cont_ranks_arr, cts_ranks_arr)

p3_results = [
    {'pair': 'CONTAINMENT vs ey_rate', 'tau': float(tau1), 'p': float(tau1_p),
     'concordant': tau1 > 0},
    {'pair': 'INTERVENTION vs ii_rate', 'tau': float(tau2), 'p': float(tau2_p),
     'concordant': tau2 > 0},
    {'pair': 'CONTAINMENT vs mean_CTS', 'tau': float(tau3), 'p': float(tau3_p),
     'concordant': tau3 > 0},
]

p3_concordant = sum(1 for r in p3_results if r['concordant'])
p3_any_sig = any(r['p'] < 0.10 for r in p3_results)
p3_pass = p3_concordant >= 2 and p3_any_sig

for r in p3_results:
    print(f"  {r['pair']}: tau={r['tau']:.3f}, p={r['p']:.4f}, "
          f"concordant={'YES' if r['concordant'] else 'NO'}")
print(f"\n  Concordant: {p3_concordant}/3, any sig at 0.10: {p3_any_sig}")
print(f"  P3 VERDICT: {'PASS' if p3_pass else 'FAIL'} (threshold: >=2/3 AND >=1 p<0.10)")

# ============================================================
# 11. P4: HERBAL R2 vs R4 REPLICATION
# ============================================================

print("\n=== P4: HERBAL R2 vs R4 REPLICATION ===")

herbal_r2 = cells.get(('H', 'REGIME_2'), [])
herbal_r4 = cells.get(('H', 'REGIME_4'), [])
print(f"  H:R2 n={len(herbal_r2)}, H:R4 n={len(herbal_r4)}")

p4_axes = [
    ('ey_rate', folio_ey_rate, 'greater'),      # R2 > R4
    ('ii_rate', folio_ii_rate, 'less'),          # R2 < R4
    ('DYE_advantage', folio_dye, 'greater'),     # R2 > R4
]

p4_concordant = 0
p4_results = []
for name, data_dict, direction in p4_axes:
    r2_vals = [data_dict[f] for f in herbal_r2 if f in data_dict]
    r4_vals = [data_dict[f] for f in herbal_r4 if f in data_dict]
    r2_mean = np.mean(r2_vals)
    r4_mean = np.mean(r4_vals)

    if direction == 'greater':
        observed_concordant = r2_mean > r4_mean
        alt = 'greater'
    else:
        observed_concordant = r2_mean < r4_mean
        alt = 'less'

    stat, p_val = mannwhitneyu(r2_vals, r4_vals, alternative=alt)
    if observed_concordant:
        p4_concordant += 1

    p4_results.append({
        'axis': name,
        'R2_mean': float(r2_mean),
        'R4_mean': float(r4_mean),
        'predicted_direction': direction,
        'observed_concordant': bool(observed_concordant),
        'U': float(stat),
        'p': float(p_val),
    })
    print(f"  {name}: R2={r2_mean:.4f}, R4={r4_mean:.4f}, "
          f"pred={direction}, match={'YES' if observed_concordant else 'NO'}, p={p_val:.4f}")

p4_any_sig = any(r['p'] < 0.10 for r in p4_results)
p4_pass = p4_concordant >= 2 and p4_any_sig
print(f"\n  Concordant: {p4_concordant}/3, any sig at 0.10: {p4_any_sig}")
print(f"  P4 VERDICT: {'PASS' if p4_pass else 'FAIL'} (threshold: >=2/3 AND >=1 p<0.10)")

# ============================================================
# 12. S3: SENSITIVITY TO H:R3
# ============================================================

print("\n=== S3: SENSITIVITY TO H:R3 ===")

# Re-run P1 without H:R3
cell_names_no_hr3 = [k for k in cell_names if k != ('H', 'REGIME_3')]
if len(cell_names_no_hr3) >= 4:
    pred_vecs_no = np.array([class_prototypes[CELL_METHOD_CLASS[k]] for k in cell_names_no_hr3])
    obs_vecs_no = np.array([cell_centroids_z[k] for k in cell_names_no_hr3])
    obs_vecs_no_clean = np.nan_to_num(obs_vecs_no, nan=0.0)
    p1_r_no, p1_p_no, _, _ = mantel_test(pred_vecs_no, obs_vecs_no_clean,
                                          n_perms=9999, metric='euclidean', seed=44)
    print(f"  P1 without H:R3: r={p1_r_no:.4f}, p={p1_p_no:.4f}")

# Re-run P3 without H:R3
cont_ranks_no = [cell_containment_rank[k] for k in cell_names_no_hr3]
ey_ranks_no = sorted(range(len(cell_names_no_hr3)),
                     key=lambda i: cell_ey[cell_names_no_hr3[i]], reverse=True)
ey_rank_map_no = {cell_names_no_hr3[ey_ranks_no[i]]: i for i in range(len(ey_ranks_no))}
ey_r_no = [ey_rank_map_no[k] for k in cell_names_no_hr3]
tau_no, tau_no_p = kendalltau(cont_ranks_no, ey_r_no)
print(f"  P3 CONTAINMENT vs ey_rate without H:R3: tau={tau_no:.3f}, p={tau_no_p:.4f}")

# ============================================================
# 13. VERDICT AND OUTPUT
# ============================================================

print("\n=== FINAL VERDICT ===")

passes = sum([p1_pass, p2_pass, p3_pass, p4_pass])
verdicts = {
    4: 'CLOSURE_RESPONSE_ALIGNED',
    3: 'CLOSURE_RESPONSE_PARTIAL',
    2: 'WEAK_CLOSURE_SIGNAL',
    1: 'CLOSURE_RESPONSE_NOT_CONFIRMED',
    0: 'CLOSURE_RESPONSE_NOT_CONFIRMED',
}
verdict = verdicts[passes]

qualifiers = []
if p2_pass and not p1_pass:
    qualifiers.append('STARS_ONLY')
if p1_pass and not p2_pass:
    qualifiers.append('GEOMETRY_ONLY')
if safety_reversal:
    qualifiers.append('SAFETY_REVERSAL')
if not annotation_stable:
    qualifiers.append('ANNOTATION_FRAGILE')

if qualifiers:
    verdict += ' (' + ', '.join(qualifiers) + ')'

print(f"  P1: {'PASS' if p1_pass else 'FAIL'} (Mantel r={p1_r_euc:.4f}, p={p1_p_euc:.4f})")
print(f"  P2: {'PASS' if p2_pass else 'FAIL'} (concordant={p2_concordant}/4, p={p2_combined_p:.4f})")
print(f"  P3: {'PASS' if p3_pass else 'FAIL'} (concordant={p3_concordant}/3)")
print(f"  P4: {'PASS' if p4_pass else 'FAIL'} (concordant={p4_concordant}/3)")
print(f"\n  VERDICT: {verdict} ({passes}/4)")

elapsed = time.time() - t0
print(f"\n  Runtime: {elapsed:.1f}s")

# Save results
results = {
    'metadata': {
        'phase': 600,
        'name': 'BRUNSCHWIG_CLOSURE_RESPONSE_ALIGNMENT',
        'prediction_hash': PRED_HASH,
        'n_recipes': len(recipes),
        'n_folios': len(common_folios),
        'n_cells': len(cell_names),
        'elapsed_seconds': elapsed,
    },
    'annotation': {
        'H1_strict_broad_corr': float(h1_corr),
        'H1_strict_broad_p': float(h1_corr_p),
        'H2_strict_broad_corr': float(h2_corr),
        'H2_strict_broad_p': float(h2_corr_p),
        'annotation_stable': annotation_stable,
        'class_prototypes': {cls: proto.tolist() for cls, proto in class_prototypes.items()},
        'class_recipe_counts': {cls: len(recs) for cls, recs in class_recipes.items()},
    },
    'S1_audit': audit_samples[:10],  # save first 10 for reference
    'S2_safety_balance': {
        'per_cell': {f'{k[0]}:{k[1]}': float(v) for k, v in cell_safety_balance.items()},
        'tau': float(s2_tau),
        'tau_p': float(s2_tau_p),
    },
    'cell_centroids': {
        f'{k[0]}:{k[1]}': {
            'n': len(cells[k]),
            'method_class': CELL_METHOD_CLASS[k],
            'raw': cell_centroids_raw[k].tolist(),
            'response_names': RESPONSE_NAMES,
        } for k in cell_names
    },
    'P1_mantel': {
        'test': 'Mantel geometry concordance (3D pred vs 7D obs)',
        'primary_euclidean': {'r': float(p1_r_euc), 'p': float(p1_p_euc)},
        'sensitivity_cosine': {'r': float(p1_r_cos), 'p': float(p1_p_cos)},
        'passed': p1_pass,
    },
    'P2_stars_direction': {
        'test': 'Stars R1 vs R3 directional concordance (4 axes)',
        'n_r1': len(stars_r1),
        'n_r3': len(stars_r3),
        'axes': p2_results,
        'concordant': p2_concordant,
        'combined_p': float(p2_combined_p),
        'safety_reversal': safety_reversal,
        'passed': p2_pass,
    },
    'P3_rank_concordance': {
        'test': 'Historical rank concordance (3 Kendall taus)',
        'containment_rank': containment_ranked,
        'intervention_rank': intervention_ranked,
        'pairs': p3_results,
        'concordant': p3_concordant,
        'any_sig_010': p3_any_sig,
        'passed': p3_pass,
    },
    'P4_herbal_direction': {
        'test': 'Herbal R2 vs R4 directional concordance (3 axes)',
        'n_r2': len(herbal_r2),
        'n_r4': len(herbal_r4),
        'axes': p4_results,
        'concordant': p4_concordant,
        'any_sig_010': p4_any_sig,
        'passed': p4_pass,
    },
    'S3_sensitivity': {
        'P1_without_HR3': {'r': float(p1_r_no), 'p': float(p1_p_no)} if len(cell_names_no_hr3) >= 4 else None,
        'P3_containment_ey_without_HR3': {'tau': float(tau_no), 'p': float(tau_no_p)},
    },
    'verdict': verdict,
    'passes': passes,
    'verification': {
        'mean_ey_rate': float(mean_ey),
        'mean_ii_rate': float(mean_ii),
        'n_common_folios': len(common_folios),
        'n_folios_with_acs': len(folios_with_acs & common_folios),
    },
}

out_path = os.path.join(os.path.dirname(__file__), '..', 'results',
                        'closure_response_alignment_results.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {out_path}")
