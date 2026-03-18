"""
Phase 599: APPARATUS_BUNDLE_ALIGNMENT
Tests whether Brunschwig method-bundle taxonomy predicts Voynich secondary apparatus profile shape.

Pre-registration hash: 5dded97c42e8af61bdaab5fb20f8a1a7e8f04d3ffd29d9524d8e550358230314
"""

import json
import hashlib
import sys
import os
import numpy as np
from collections import Counter, defaultdict
from itertools import product as iterproduct
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr, mannwhitneyu, kruskal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# ── Verify pre-registration hash ──────────────────────────────────────────
pred_path = os.path.join(os.path.dirname(__file__), '..', 'PREDICTIONS.md')
pred_hash = hashlib.sha256(open(pred_path, 'rb').read()).hexdigest()
assert pred_hash == '5dded97c42e8af61bdaab5fb20f8a1a7e8f04d3ffd29d9524d8e550358230314', \
    f"PREDICTIONS.md hash mismatch: {pred_hash}"
print(f"Pre-registration hash verified: {pred_hash[:16]}...")


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


# ── Constants ─────────────────────────────────────────────────────────────
PROFILES = ['DISTILLATION', 'SEALED_VESSEL', 'SUSTAINED_HEAT', 'PRECISION', 'DIRECT_FIRE']
SECONDARY = ['SEALED_VESSEL', 'SUSTAINED_HEAT', 'PRECISION', 'DIRECT_FIRE']  # no DISTILLATION

# Method bundle classes
BUNDLE_CLASSES = {
    'GENTLE_SUSTAINED': ['balneum_mariae', 'horse_dung', 'sun'],
    'OPEN_CYCLE_ELEVATED': ['open_fire', 'ashes', 'gentle_fire'],
    'SEALED_RECIRCULATION': ['circulation'],
    'PRECISION_CONTROLLED': ['sand_bath'],
}

# Method -> bundle class lookup
METHOD_TO_BUNDLE = {}
for bc, methods in BUNDLE_CLASSES.items():
    for m in methods:
        METHOD_TO_BUNDLE[m] = bc

# Certain profile mappings (always included in secondary space)
CERTAIN_MAP = {
    'GENTLE_SUSTAINED': 'SUSTAINED_HEAT',
    'OPEN_CYCLE_ELEVATED': 'DIRECT_FIRE',
    'SEALED_RECIRCULATION': 'SEALED_VESSEL',
    'PRECISION_CONTROLLED': 'PRECISION',
}

# Admissible alternate mappings (may be included or not)
# Key: bundle class, Value: secondary profile name
# Note: OPEN_CYCLE_ELEVATED's alternate is DISTILLATION (removed in secondary space),
# so it has no effect on secondary tests. We skip it.
ALTERNATE_MAP = {
    'GENTLE_SUSTAINED': 'SEALED_VESSEL',
    'SEALED_RECIRCULATION': 'PRECISION',
    'PRECISION_CONTROLLED': 'SUSTAINED_HEAT',
}

# Cell -> prototype mapping (from frozen constraints)
CELL_PROTOTYPE = {
    ('S', 'REGIME_1'): 'GENTLE_SUSTAINED',
    ('S', 'REGIME_3'): 'OPEN_CYCLE_ELEVATED',
    ('H', 'REGIME_2'): 'SEALED_RECIRCULATION',
    ('H', 'REGIME_4'): 'PRECISION_CONTROLLED',
    ('H', 'REGIME_3'): 'OPEN_CYCLE_ELEVATED',
}

# Weight family
WEIGHT_LEVELS = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80]

# Viable cells (n >= 5)
VIABLE_CELLS = [('H', 'REGIME_2'), ('H', 'REGIME_3'), ('H', 'REGIME_4'),
                ('S', 'REGIME_1'), ('S', 'REGIME_3')]

N_PERMS = 9999


def make_secondary(profile_vec):
    """Remove DISTILLATION from 5D profile, re-normalize to 4D secondary."""
    # profile_vec is dict {profile_name: score}
    sec = {p: profile_vec.get(p, 0.0) for p in SECONDARY}
    total = sum(sec.values())
    if total > 0:
        sec = {p: v / total for p, v in sec.items()}
    return sec


def sec_to_array(sec_dict):
    """Convert secondary profile dict to numpy array in canonical order."""
    return np.array([sec_dict.get(p, 0.0) for p in SECONDARY])


def build_bridge_variant(primary_weight, include_alternates):
    """
    Build a bridge variant: maps each bundle class to a 4D secondary profile vector.

    include_alternates: dict {bundle_class: bool} for each bundle that has an alternate
    """
    bridge = {}
    for bc in BUNDLE_CLASSES:
        vec = {p: 0.0 for p in SECONDARY}
        certain_profile = CERTAIN_MAP[bc]

        if bc in ALTERNATE_MAP and include_alternates.get(bc, False):
            alt_profile = ALTERNATE_MAP[bc]
            vec[certain_profile] = primary_weight
            vec[alt_profile] = 1.0 - primary_weight
        else:
            # Sole profile
            vec[certain_profile] = 1.0

        bridge[bc] = vec
    return bridge


def generate_all_bridge_variants():
    """Generate all 48 bridge variants."""
    variants = []
    alternate_bundles = list(ALTERNATE_MAP.keys())  # GS, SR, PC

    for weight in WEIGHT_LEVELS:
        # 2^3 = 8 alternate configurations
        for bits in range(8):
            include = {}
            for i, bc in enumerate(alternate_bundles):
                include[bc] = bool(bits & (1 << i))
            variants.append({
                'weight': weight,
                'include_alternates': include,
                'bridge': build_bridge_variant(weight, include),
            })

    return variants


def assign_recipe_to_bundle(recipe):
    """Assign recipe to bundle class by rarest method (information-weighted)."""
    methods = recipe.get('methods', [])
    if not methods:
        return None

    # Method rarity (inverse of global frequency)
    METHOD_FREQ = {
        'balneum_mariae': 192, 'sun': 129, 'horse_dung': 127,
        'gentle_fire': 50, 'circulation': 39, 'ashes': 22,
        'open_fire': 16, 'sand_bath': 14,
    }

    best_bundle = None
    best_rarity = float('inf')

    for m in methods:
        if m in METHOD_TO_BUNDLE:
            freq = METHOD_FREQ.get(m, 999)
            if freq < best_rarity:
                best_rarity = freq
                best_bundle = METHOD_TO_BUNDLE[m]

    return best_bundle


# ── Load Data ─────────────────────────────────────────────────────────────
print("\n=== Loading data ===")

# Load Brunschwig recipes
recipe_path = os.path.join(os.path.dirname(__file__), '..', '..',
                           'BRUNSCHWIG_1512_BLIND_PREDICTION', 'results',
                           'brunschwig_1512_recipes.json')
with open(recipe_path) as f:
    recipe_data = json.load(f)

recipes = [r for r in recipe_data['recipes']
           if r['classification'] == 'recipe'
           and r['book'] not in ('front_matter', 'back_matter')]
print(f"Confirmed recipes: {len(recipes)}")

# Classify recipes into bundle classes
recipe_bundles = defaultdict(list)
unclassified = 0
for r in recipes:
    bc = assign_recipe_to_bundle(r)
    if bc:
        recipe_bundles[bc].append(r)
    else:
        unclassified += 1

print(f"Bundle assignment: " + ", ".join(f"{bc}={len(rs)}" for bc, rs in sorted(recipe_bundles.items())))
print(f"Unclassified (no methods): {unclassified}")

# Load apparatus profiles
profile_path = os.path.join(os.path.dirname(__file__), '..', '..',
                            'APPARATUS_VOCABULARY_CLASSIFICATION', 'results',
                            'apparatus_profiles.json')
with open(profile_path) as f:
    profile_data = json.load(f)

# Load REGIME assignments
regime_path = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                           'data', 'regime_folio_mapping.json')
with open(regime_path) as f:
    regime_data = json.load(f)

# Get section per folio from Transcript
from scripts.voynich import Transcript
tx = Transcript()
folio_section = {}
for t in tx.currier_b():
    folio_section[t.folio] = t.section

# Build per-folio data: {folio: {profile scores, regime, section}}
folio_data = {}
for folio, info in regime_data['regime_assignments'].items():
    regime = info['regime']
    section = folio_section.get(folio)
    if section is None:
        continue

    # Get apparatus profile scores for this folio
    # Profile data has folio_profiles with per-folio scores
    folio_data[folio] = {
        'regime': regime,
        'section': section,
    }

# Load per-folio profile scores from folio_scores
for folio, scores in profile_data.get('folio_scores', {}).items():
    if folio in folio_data:
        folio_data[folio]['profiles'] = scores

has_profiles = sum(1 for f in folio_data.values() if 'profiles' in f)
print(f"Folios with profile data: {has_profiles}")

# ── Build Cells ───────────────────────────────────────────────────────────
print("\n=== Building cells ===")

# Group folios by (section, regime)
cells = defaultdict(list)
for folio, fd in folio_data.items():
    if 'profiles' not in fd:
        continue
    key = (fd['section'], fd['regime'])
    cells[key].append(folio)

# Report cell sizes
print("Cell sizes:")
for key in sorted(cells.keys()):
    marker = " *VIABLE*" if key in VIABLE_CELLS else ""
    print(f"  {key[0]}:{key[1]} = {len(cells[key])}{marker}")

# Compute observed secondary profiles per cell
cell_observed = {}
for cell_key in VIABLE_CELLS:
    folios = cells.get(cell_key, [])
    if not folios:
        print(f"  WARNING: no folios for {cell_key}")
        continue

    # Average profile across folios in cell
    profile_sum = {p: 0.0 for p in PROFILES}
    for f in folios:
        for p in PROFILES:
            profile_sum[p] += folio_data[f]['profiles'].get(p, 0.0)
    profile_mean = {p: v / len(folios) for p, v in profile_sum.items()}

    # Convert to secondary
    cell_observed[cell_key] = make_secondary(profile_mean)

print(f"\nObserved secondary profiles for viable cells:")
for ck in VIABLE_CELLS:
    if ck in cell_observed:
        obs = cell_observed[ck]
        print(f"  {ck[0]}:{ck[1]}: " + ", ".join(f"{p}={obs[p]:.3f}" for p in SECONDARY))


# ── P1: Mantel Geometry Concordance ───────────────────────────────────────
print("\n=== P1: Mantel Geometry Concordance ===")

def compute_distance_matrix(cell_vecs, cell_order):
    """Compute Euclidean distance matrix from cell vectors."""
    n = len(cell_order)
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            ci, cj = cell_order[i], cell_order[j]
            vi = sec_to_array(cell_vecs[ci])
            vj = sec_to_array(cell_vecs[cj])
            d = np.linalg.norm(vi - vj)
            mat[i, j] = d
            mat[j, i] = d
    return mat


def upper_tri(mat):
    """Extract upper triangle as flat array."""
    n = mat.shape[0]
    return np.array([mat[i, j] for i in range(n) for j in range(i + 1, n)])


def mantel_test(obs_mat, pred_mat, n_perms=N_PERMS):
    """Mantel test: Spearman correlation between upper-tri distance vectors."""
    obs_flat = upper_tri(obs_mat)
    pred_flat = upper_tri(pred_mat)

    if np.std(obs_flat) == 0 or np.std(pred_flat) == 0:
        return 0.0, 1.0

    r_obs, _ = spearmanr(obs_flat, pred_flat)

    # Permutation
    n = obs_mat.shape[0]
    count_ge = 0
    rng = np.random.default_rng(42)
    for _ in range(n_perms):
        perm = rng.permutation(n)
        perm_mat = obs_mat[np.ix_(perm, perm)]
        perm_flat = upper_tri(perm_mat)
        r_perm, _ = spearmanr(perm_flat, pred_flat)
        if r_perm >= r_obs:
            count_ge += 1

    p = (count_ge + 1) / (n_perms + 1)
    return r_obs, p


# Run P1 across all bridge variants
cell_order = list(VIABLE_CELLS)
obs_mat = compute_distance_matrix(cell_observed, cell_order)

bridge_variants = generate_all_bridge_variants()
print(f"Bridge variants: {len(bridge_variants)}")

p1_results = []
for bv in bridge_variants:
    bridge = bv['bridge']

    # Build predicted secondary profiles for each cell
    pred_vecs = {}
    for ck in cell_order:
        prototype = CELL_PROTOTYPE[ck]
        pred_vecs[ck] = bridge[prototype]

    pred_mat = compute_distance_matrix(pred_vecs, cell_order)

    r, p = mantel_test(obs_mat, pred_mat)
    p1_results.append({
        'weight': bv['weight'],
        'alternates': {k: v for k, v in bv['include_alternates'].items()},
        'mantel_r': r,
        'mantel_p': p,
    })

mantel_rs = [x['mantel_r'] for x in p1_results]
mantel_ps = [x['mantel_p'] for x in p1_results]
median_r = np.median(mantel_rs)
median_p = np.median(mantel_ps)
pct_positive = sum(1 for r in mantel_rs if r > 0) / len(mantel_rs) * 100
pct_sig = sum(1 for r, p in zip(mantel_rs, mantel_ps) if r > 0 and p < 0.05) / len(mantel_rs) * 100

p1_pass = median_r > 0.30 and median_p < 0.05 and pct_sig >= 75
print(f"P1 results: median r={median_r:.3f}, median p={median_p:.3f}")
print(f"  Positive variants: {pct_positive:.0f}%, Significant (r>0 & p<0.05): {pct_sig:.0f}%")
print(f"  Range: r=[{min(mantel_rs):.3f}, {max(mantel_rs):.3f}]")
print(f"  P1 PASS: {p1_pass}")


# ── P2: Dominant-Profile Match ────────────────────────────────────────────
print("\n=== P2: Dominant-Profile Match ===")

MARGIN = 0.02

# Observed dominants
obs_dominants = {}
obs_top2 = {}
for ck in cell_order:
    obs = cell_observed[ck]
    ranked = sorted(SECONDARY, key=lambda p: obs[p], reverse=True)
    obs_dominants[ck] = ranked[0]
    obs_top2[ck] = set(ranked[:2])
    margin = obs[ranked[0]] - obs[ranked[1]]
    is_ambig = margin < MARGIN
    print(f"  {ck[0]}:{ck[1]}: dominant={ranked[0]} (margin={margin:.3f})"
          f"{' AMBIGUOUS' if is_ambig else ''}")

# Predicted dominants (per bridge variant)
p2_results = []
for bv in bridge_variants:
    bridge = bv['bridge']
    hits = 0
    misses = 0
    ambiguous = 0
    top2_hits = 0

    for ck in cell_order:
        prototype = CELL_PROTOTYPE[ck]
        pred_vec = bridge[prototype]
        pred_ranked = sorted(SECONDARY, key=lambda p: pred_vec.get(p, 0), reverse=True)
        pred_dominant = pred_ranked[0]
        pred_top2 = set(pred_ranked[:2])

        obs = cell_observed[ck]
        obs_ranked = sorted(SECONDARY, key=lambda p: obs[p], reverse=True)
        obs_dominant = obs_ranked[0]
        margin = obs[obs_ranked[0]] - obs[obs_ranked[1]]

        if margin < MARGIN:
            ambiguous += 1
        elif pred_dominant == obs_dominant:
            hits += 1
        else:
            misses += 1

        if pred_top2 & set(obs_ranked[:2]):
            top2_hits += 1

    non_ambig = hits + misses
    match_frac = hits / non_ambig if non_ambig > 0 else 0
    top2_frac = top2_hits / len(cell_order)

    p2_results.append({
        'weight': bv['weight'],
        'hits': hits,
        'misses': misses,
        'ambiguous': ambiguous,
        'match_fraction': match_frac,
        'top2_overlap': top2_frac,
    })

# Median results across bridge variants
median_match = np.median([x['match_fraction'] for x in p2_results])
median_top2 = np.median([x['top2_overlap'] for x in p2_results])
best_hits = max(x['hits'] for x in p2_results)
print(f"P2 results: median match={median_match:.2f}, median top2={median_top2:.2f}")
print(f"  Best variant: {best_hits} hits")

# Permutation test for P2 (using median bridge variant)
# Shuffle REGIME labels within section
mid_bv = bridge_variants[len(bridge_variants) // 2]  # median weight variant
mid_bridge = mid_bv['bridge']

# Get all folio-level data for permutation
folio_list_by_section = defaultdict(list)
for folio, fd in folio_data.items():
    if 'profiles' in fd and fd['section'] in ('H', 'S'):
        folio_list_by_section[fd['section']].append(folio)

def compute_p2_score(folio_data_local, bridge):
    """Compute P2 score for a given assignment of folios to cells."""
    # Rebuild cell observations
    cell_obs_local = defaultdict(lambda: defaultdict(float))
    cell_counts = defaultdict(int)
    for folio, fd in folio_data_local.items():
        if 'profiles' not in fd:
            continue
        key = (fd['section'], fd['regime'])
        if key not in VIABLE_CELLS:
            continue
        for p in PROFILES:
            cell_obs_local[key][p] += fd['profiles'].get(p, 0.0)
        cell_counts[key] += 1

    hits = 0
    misses = 0
    for ck in VIABLE_CELLS:
        if cell_counts[ck] == 0:
            continue
        raw = {p: cell_obs_local[ck][p] / cell_counts[ck] for p in PROFILES}
        sec = make_secondary(raw)
        ranked = sorted(SECONDARY, key=lambda p: sec[p], reverse=True)
        margin = sec[ranked[0]] - sec[ranked[1]]
        if margin < MARGIN:
            continue

        prototype = CELL_PROTOTYPE[ck]
        pred_vec = bridge[prototype]
        pred_ranked = sorted(SECONDARY, key=lambda p: pred_vec.get(p, 0), reverse=True)

        if pred_ranked[0] == ranked[0]:
            hits += 1
        else:
            misses += 1

    return hits / (hits + misses) if (hits + misses) > 0 else 0

obs_p2_score = compute_p2_score(folio_data, mid_bridge)

rng = np.random.default_rng(123)
p2_perm_count = 0
for _ in range(5000):
    # Shuffle REGIME labels within each section
    fd_shuffled = {}
    for folio, fd in folio_data.items():
        fd_shuffled[folio] = dict(fd)

    for section in ('H', 'S'):
        section_folios = [f for f in folio_list_by_section[section]]
        regimes = [folio_data[f]['regime'] for f in section_folios]
        rng.shuffle(regimes)
        for i, f in enumerate(section_folios):
            fd_shuffled[f]['regime'] = regimes[i]

    perm_score = compute_p2_score(fd_shuffled, mid_bridge)
    if perm_score >= obs_p2_score:
        p2_perm_count += 1

p2_perm_p = (p2_perm_count + 1) / 5001
p2_pass = median_match >= 0.6 and p2_perm_p < 0.05  # >=3/5 non-ambiguous
print(f"P2 permutation: observed score={obs_p2_score:.2f}, p={p2_perm_p:.3f}")
print(f"  P2 PASS: {p2_pass}")


# ── P3: Stars R1 vs R3 Direction Concordance ──────────────────────────────
print("\n=== P3: Stars R1 vs R3 Direction Concordance ===")

stars_r1 = [f for f, fd in folio_data.items()
            if 'profiles' in fd and fd['section'] == 'S' and fd['regime'] == 'REGIME_1']
stars_r3 = [f for f, fd in folio_data.items()
            if 'profiles' in fd and fd['section'] == 'S' and fd['regime'] == 'REGIME_3']

print(f"Stars R1: {len(stars_r1)} folios, R3: {len(stars_r3)} folios")

# Compute mean secondary profiles
def mean_secondary(folio_list):
    profile_sum = {p: 0.0 for p in PROFILES}
    for f in folio_list:
        for p in PROFILES:
            profile_sum[p] += folio_data[f]['profiles'].get(p, 0.0)
    raw = {p: v / len(folio_list) for p, v in profile_sum.items()}
    return make_secondary(raw)

r1_sec = mean_secondary(stars_r1)
r3_sec = mean_secondary(stars_r3)

# Pre-registered predictions: R1 - R3 direction
PREDICTED_SIGNS = {
    'SEALED_VESSEL': +1,    # R1 > R3
    'SUSTAINED_HEAT': +1,   # R1 > R3
    'DIRECT_FIRE': -1,      # R1 < R3
}

concordant = 0
p3_details = {}
for axis, pred_sign in PREDICTED_SIGNS.items():
    diff = r1_sec[axis] - r3_sec[axis]
    obs_sign = +1 if diff > 0 else -1
    match = obs_sign == pred_sign
    concordant += match
    p3_details[axis] = {
        'r1_mean': r1_sec[axis],
        'r3_mean': r3_sec[axis],
        'diff': diff,
        'predicted_sign': pred_sign,
        'observed_sign': obs_sign,
        'concordant': match,
    }
    print(f"  {axis}: R1={r1_sec[axis]:.3f}, R3={r3_sec[axis]:.3f}, "
          f"diff={diff:+.3f}, pred={'+' if pred_sign > 0 else '-'}, "
          f"{'MATCH' if match else 'MISS'}")

# Exploratory: PRECISION
prec_diff = r1_sec['PRECISION'] - r3_sec['PRECISION']
p3_details['PRECISION'] = {
    'r1_mean': r1_sec['PRECISION'],
    'r3_mean': r3_sec['PRECISION'],
    'diff': prec_diff,
    'status': 'EXPLORATORY',
}
print(f"  PRECISION (exploratory): R1={r1_sec['PRECISION']:.3f}, R3={r3_sec['PRECISION']:.3f}, "
      f"diff={prec_diff:+.3f}")

# Permutation test
stars_all = stars_r1 + stars_r3
n_r1 = len(stars_r1)
rng3 = np.random.default_rng(456)
p3_perm_count = 0
for _ in range(5000):
    perm = rng3.permutation(len(stars_all))
    perm_r1 = [stars_all[i] for i in perm[:n_r1]]
    perm_r3 = [stars_all[i] for i in perm[n_r1:]]

    pr1 = mean_secondary(perm_r1)
    pr3 = mean_secondary(perm_r3)

    perm_conc = 0
    for axis, pred_sign in PREDICTED_SIGNS.items():
        diff = pr1[axis] - pr3[axis]
        if (diff > 0 and pred_sign > 0) or (diff < 0 and pred_sign < 0):
            perm_conc += 1

    if perm_conc >= concordant:
        p3_perm_count += 1

p3_perm_p = (p3_perm_count + 1) / 5001
p3_pass = concordant == 3 and p3_perm_p < 0.05
print(f"P3 result: {concordant}/3 concordant, permutation p={p3_perm_p:.3f}")
print(f"  P3 PASS: {p3_pass}")


# ── P4: Open-Cycle Signature Test ─────────────────────────────────────────
print("\n=== P4: Open-Cycle Signature Test ===")

# Classify recipes as open-cycle vs single-pass
open_cycle = [r for r in recipes
              if r.get('distillation_steps', {}).get('distill_references', 0) >= 2]
single_pass = [r for r in recipes
               if r.get('distillation_steps', {}).get('distill_references', 0) <= 1]

print(f"Open-cycle recipes (refs>=2): {len(open_cycle)}")
print(f"Single-pass recipes (refs<=1): {len(single_pass)}")

# Compute method mix for each subset
def method_mix(recipe_list):
    """Compute fraction of recipes using each method."""
    n = len(recipe_list)
    if n == 0:
        return {}
    counts = Counter()
    for r in recipe_list:
        for m in r['methods']:
            counts[m] += 1
    return {m: c / n for m, c in counts.items()}

oc_mix = method_mix(open_cycle)
sp_mix = method_mix(single_pass)

print(f"Open-cycle method mix: " + ", ".join(f"{m}={v:.2f}" for m, v in sorted(oc_mix.items())))
print(f"Single-pass method mix: " + ", ".join(f"{m}={v:.2f}" for m, v in sorted(sp_mix.items())))

# For each subset, compute predicted secondary profile using median bridge
mid_bridge = bridge_variants[len(bridge_variants) // 2]['bridge']

def subset_predicted_profile(recipe_list, bridge):
    """Compute predicted secondary profile for a recipe subset."""
    vec_sum = {p: 0.0 for p in SECONDARY}
    n_assigned = 0
    for r in recipe_list:
        bc = assign_recipe_to_bundle(r)
        if bc is None:
            continue
        proto = bridge[bc]
        for p in SECONDARY:
            vec_sum[p] += proto.get(p, 0.0)
        n_assigned += 1

    if n_assigned == 0:
        return {p: 0.25 for p in SECONDARY}
    return {p: v / n_assigned for p, v in vec_sum.items()}

oc_pred = subset_predicted_profile(open_cycle, mid_bridge)
sp_pred = subset_predicted_profile(single_pass, mid_bridge)

# Direction vector: open-cycle minus single-pass (predicted)
pred_direction = np.array([oc_pred[p] - sp_pred[p] for p in SECONDARY])

# Observed direction: R3 minus R1 in Stars
obs_r3_minus_r1 = np.array([r3_sec[p] - r1_sec[p] for p in SECONDARY])

# Cosine similarity
def cosine_sim(a, b):
    dot = np.dot(a, b)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

p4_cosine = cosine_sim(pred_direction, obs_r3_minus_r1)
print(f"Predicted direction (OC - SP): {dict(zip(SECONDARY, pred_direction))}")
print(f"Observed direction (R3 - R1): {dict(zip(SECONDARY, obs_r3_minus_r1))}")
print(f"Cosine similarity: {p4_cosine:.3f}")

# Permutation test: shuffle open-cycle/single-pass labels among recipes
all_classified = open_cycle + single_pass
n_oc = len(open_cycle)
rng4 = np.random.default_rng(789)
p4_perm_count = 0
for _ in range(5000):
    perm = rng4.permutation(len(all_classified))
    perm_oc = [all_classified[i] for i in perm[:n_oc]]
    perm_sp = [all_classified[i] for i in perm[n_oc:]]

    perm_oc_pred = subset_predicted_profile(perm_oc, mid_bridge)
    perm_sp_pred = subset_predicted_profile(perm_sp, mid_bridge)
    perm_direction = np.array([perm_oc_pred[p] - perm_sp_pred[p] for p in SECONDARY])

    perm_cos = cosine_sim(perm_direction, obs_r3_minus_r1)
    if perm_cos >= p4_cosine:
        p4_perm_count += 1

p4_perm_p = (p4_perm_count + 1) / 5001
p4_pass = p4_cosine > 0 and p4_perm_p < 0.05
print(f"P4 permutation: p={p4_perm_p:.3f}")
print(f"  P4 PASS: {p4_pass}")

# Also report P4 feasibility
if len(open_cycle) < 20:
    print(f"  WARNING: Only {len(open_cycle)} open-cycle recipes. UNDERPOWERED.")


# ── S1: DISTILLATION Contamination Diagnostic ─────────────────────────────
print("\n=== S1: DISTILLATION Contamination Diagnostic ===")

herbal_r2 = [f for f, fd in folio_data.items()
             if 'profiles' in fd and fd['section'] == 'H' and fd['regime'] == 'REGIME_2']
herbal_r4 = [f for f, fd in folio_data.items()
             if 'profiles' in fd and fd['section'] == 'H' and fd['regime'] == 'REGIME_4']

r2_dist = [folio_data[f]['profiles']['DISTILLATION'] for f in herbal_r2]
r4_dist = [folio_data[f]['profiles']['DISTILLATION'] for f in herbal_r4]

if len(r2_dist) > 0 and len(r4_dist) > 0:
    stat, s1_p = mannwhitneyu(r2_dist, r4_dist, alternative='two-sided')
    r2_mean = np.mean(r2_dist)
    r4_mean = np.mean(r4_dist)
    s1_clean = s1_p > 0.10
    s1_contaminated = s1_p < 0.05
    print(f"Herbal R2 DISTILLATION: mean={r2_mean:.3f} (n={len(r2_dist)})")
    print(f"Herbal R4 DISTILLATION: mean={r4_mean:.3f} (n={len(r4_dist)})")
    print(f"Mann-Whitney p={s1_p:.3f}")
    print(f"  {'CLEAN' if s1_clean else 'CONTAMINATED' if s1_contaminated else 'AMBIGUOUS'}")
else:
    s1_p = 1.0
    s1_clean = True
    s1_contaminated = False
    print("Insufficient data for S1")


# ── S2: Section Diversity Description ─────────────────────────────────────
print("\n=== S2: Section Diversity Description ===")

def shannon_entropy(vec):
    """Shannon entropy of a probability vector."""
    vec = np.array(vec)
    vec = vec[vec > 0]
    if len(vec) == 0:
        return 0.0
    return -np.sum(vec * np.log2(vec))

section_entropies = defaultdict(list)
for folio, fd in folio_data.items():
    if 'profiles' not in fd:
        continue
    sec = make_secondary(fd['profiles'])
    sec_vec = [sec[p] for p in SECONDARY]
    ent = shannon_entropy(sec_vec)
    section_entropies[fd['section']].append(ent)

print("Section secondary profile entropy (mean +/- std):")
for s in sorted(section_entropies.keys()):
    vals = section_entropies[s]
    print(f"  {s}: {np.mean(vals):.3f} +/- {np.std(vals):.3f} (n={len(vals)})")

# Kruskal-Wallis across H, S, B
if all(s in section_entropies for s in ('H', 'S', 'B')):
    kw_stat, kw_p = kruskal(section_entropies['H'], section_entropies['S'], section_entropies['B'])
    print(f"Kruskal-Wallis: H={kw_stat:.2f}, p={kw_p:.3f}")

    # H vs S
    hs_stat, hs_p = mannwhitneyu(section_entropies['H'], section_entropies['S'], alternative='greater')
    print(f"H > S: Mann-Whitney p={hs_p:.3f}")

    s2_ordering = (np.mean(section_entropies['H']) > np.mean(section_entropies['S']) >
                   np.mean(section_entropies['B']))
    print(f"H > S > B ordering: {s2_ordering}")


# ── S3: Sensitivity to H:R3 Cell ─────────────────────────────────────────
print("\n=== S3: Sensitivity to H:R3 ===")

# Re-run P1 without H:R3
cells_no_hr3 = [ck for ck in VIABLE_CELLS if ck != ('H', 'REGIME_3')]
obs_mat_no_hr3 = compute_distance_matrix(cell_observed, cells_no_hr3)

# Use median bridge variant
mid_bv = bridge_variants[len(bridge_variants) // 2]
pred_vecs_no_hr3 = {}
for ck in cells_no_hr3:
    prototype = CELL_PROTOTYPE[ck]
    pred_vecs_no_hr3[ck] = mid_bv['bridge'][prototype]
pred_mat_no_hr3 = compute_distance_matrix(pred_vecs_no_hr3, cells_no_hr3)

r_no_hr3, p_no_hr3 = mantel_test(obs_mat_no_hr3, pred_mat_no_hr3)
print(f"P1 without H:R3: Mantel r={r_no_hr3:.3f}, p={p_no_hr3:.3f}")
print(f"P1 with H:R3 (median): Mantel r={median_r:.3f}, p={median_p:.3f}")
s3_fragile = (median_r > 0.30 and r_no_hr3 <= 0.30) or (median_p < 0.05 and p_no_hr3 >= 0.05)
print(f"  H:R3 fragility: {'FRAGILE' if s3_fragile else 'ROBUST'}")


# ── Verdict ───────────────────────────────────────────────────────────────
print("\n=== VERDICT ===")

passes = sum([p1_pass, p2_pass, p3_pass, p4_pass])
print(f"Primary tests passed: {passes}/4")
print(f"  P1 (Mantel geometry): {'PASS' if p1_pass else 'FAIL'}")
print(f"  P2 (Dominant match): {'PASS' if p2_pass else 'FAIL'}")
print(f"  P3 (Stars R1-R3): {'PASS' if p3_pass else 'FAIL'}")
print(f"  P4 (Open-cycle): {'PASS' if p4_pass else 'FAIL'}")

# Bridge robustness (for P1)
bridge_robust = pct_sig >= 75
bridge_sensitive = pct_sig < 50

verdicts = {
    4: 'APPARATUS_BUNDLE_ALIGNED',
    3: 'APPARATUS_SHAPE_ALIGNED',
    2: 'PARTIAL_APPARATUS_ALIGNMENT',
    1: 'WEAK_APPARATUS_SIGNAL',
    0: 'APPARATUS_ALIGNMENT_NOT_CONFIRMED',
}
verdict = verdicts[passes]

qualifiers = []
if s1_contaminated:
    qualifiers.append('INTENSITY_CONTAMINATION')
if bridge_sensitive:
    qualifiers.append('BRIDGE_SENSITIVE')
if bridge_robust:
    qualifiers.append('BRIDGE_ROBUST')
if s3_fragile:
    qualifiers.append('HR3_FRAGILE')

if qualifiers:
    verdict += ' (' + ', '.join(qualifiers) + ')'

print(f"\nFinal verdict: {verdict}")


# ── Save Results ──────────────────────────────────────────────────────────
results = {
    'phase': 'APPARATUS_BUNDLE_ALIGNMENT',
    'phase_number': 599,
    'preregistration_hash': pred_hash,
    'n_recipes': len(recipes),
    'n_bridge_variants': len(bridge_variants),
    'bundle_sizes': {bc: len(rs) for bc, rs in recipe_bundles.items()},
    'cell_sizes': {f"{ck[0]}:{ck[1]}": len(cells.get(ck, []))
                   for ck in VIABLE_CELLS},
    'observed_secondary_profiles': {
        f"{ck[0]}:{ck[1]}": cell_observed[ck]
        for ck in VIABLE_CELLS if ck in cell_observed
    },
    'P1_mantel_geometry': {
        'median_r': median_r,
        'median_p': median_p,
        'pct_positive': pct_positive,
        'pct_significant': pct_sig,
        'r_range': [min(mantel_rs), max(mantel_rs)],
        'pass': p1_pass,
        'threshold': 'median_r > 0.30, median_p < 0.05, pct_sig >= 75%',
    },
    'P2_dominant_match': {
        'median_match_fraction': median_match,
        'median_top2_overlap': median_top2,
        'permutation_p': p2_perm_p,
        'pass': p2_pass,
        'observed_dominants': {f"{ck[0]}:{ck[1]}": obs_dominants[ck] for ck in cell_order},
        'threshold': 'match >= 0.6, permutation p < 0.05',
    },
    'P3_stars_direction': {
        'concordant': concordant,
        'total_preregistered': 3,
        'permutation_p': p3_perm_p,
        'pass': p3_pass,
        'details': p3_details,
        'threshold': '3/3 concordant, permutation p < 0.05',
    },
    'P4_open_cycle': {
        'n_open_cycle': len(open_cycle),
        'n_single_pass': len(single_pass),
        'cosine_similarity': p4_cosine,
        'permutation_p': p4_perm_p,
        'pass': p4_pass,
        'predicted_direction': dict(zip(SECONDARY, pred_direction.tolist())),
        'observed_direction': dict(zip(SECONDARY, obs_r3_minus_r1.tolist())),
        'threshold': 'cosine > 0, permutation p < 0.05',
    },
    'S1_distillation_diagnostic': {
        'herbal_r2_mean': float(np.mean(r2_dist)) if r2_dist else None,
        'herbal_r4_mean': float(np.mean(r4_dist)) if r4_dist else None,
        'mann_whitney_p': s1_p,
        'clean': s1_clean,
        'contaminated': s1_contaminated,
    },
    'S2_section_diversity': {
        section: {
            'mean_entropy': float(np.mean(vals)),
            'std_entropy': float(np.std(vals)),
            'n': len(vals),
        }
        for section, vals in section_entropies.items()
    },
    'S3_hr3_sensitivity': {
        'mantel_r_with_hr3': median_r,
        'mantel_r_without_hr3': r_no_hr3,
        'fragile': s3_fragile,
    },
    'verdict': verdict,
    'passes': passes,
}

out_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'bundle_alignment_results.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f"\nResults saved to {out_path}")
