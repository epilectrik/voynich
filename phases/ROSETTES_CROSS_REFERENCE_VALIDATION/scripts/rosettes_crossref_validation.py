#!/usr/bin/env python3
"""
Phase 393: Rosettes Cross-Reference Validation -- 6-test battery

Tests whether the Rosettes foldout demonstrates the operational character
of its cross-referenced target folios, not just vocabulary overlap.

P1: Description region heterogeneity (GATE)
P2: B-like Rosettes folios match Stars/Pharma character
P3: Non-bridge section signal
P4: AZC-to-B gradient predicts Stars similarity
P5: Target folio specificity
P6: CENTER convergence distinctiveness

Grounding constraints:
  C1088 (hybrid classification), C1091 (cross-reference map),
  C1092 (CENTER convergence), C1093 (label-description bifurcation),
  C1098 (structural index), C1100 (bridge-mediated Jaccard),
  C1106 (Stars e-stability), C1107 (Stars LINK concentration)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, BFolioDecoder, BTokenAnalysis

RESULTS = ROOT / "phases" / "ROSETTES_CROSS_REFERENCE_VALIDATION" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

ROSETTES_FOLIOS = ['f85r1', 'f85r2', 'f85v2', 'f86v3', 'f86v4', 'f86v5', 'f86v6']
TARGET_FOLIOS = ['f111r', 'f108r', 'f76r', 'f108v', 'f116r']

# Description groups on f85v2 (U-track)
DESC_GROUPS = {
    'NORTH': ['N1', 'N2'],
    'VERT': ['V1', 'V2'],
    'CENTER': ['C2'],
}

# C109 hazard sources
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]
HAZARD_SOURCES = set(a for a, b in FORBIDDEN_TRANSITIONS)

CC_TRIGGERS = {
    'daiin': 'CHSH_PRECISION', 'dain': 'CHSH_PRECISION',
    'aiin': 'FQ_FREQUENT', 'ain': 'FQ_FREQUENT',
    'ol': 'QO_ENERGY',
    'or': 'CLOSE_FLOW', 'al': 'CLOSE_FLOW', 'ar': 'CLOSE_FLOW',
}


def round_floats(obj, decimals=4):
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return round(float(obj), decimals)
    if isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, decimals) for x in obj]
    return obj


def cosine_sim(v1, v2):
    v1, v2 = np.array(v1, dtype=float), np.array(v2, dtype=float)
    dot = np.dot(v1, v2)
    m1, m2 = np.linalg.norm(v1), np.linalg.norm(v2)
    return float(dot / (m1 * m2)) if m1 > 0 and m2 > 0 else 0.0


def jaccard(s1, s2):
    if not s1 and not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def profile_vector(prof):
    """Extract 9-dimensional vector from profile dict."""
    return [
        prof.get('k_pct', 0), prof.get('h_pct', 0), prof.get('e_pct', 0),
        prof.get('qo_pct', 0), prof.get('chsh_pct', 0),
        prof.get('link_pct', 0), prof.get('haz_density', 0),
        prof.get('ttr', 0), prof.get('e_kernel_fraction', 0),
    ]


# ===================================================================
# Initialize
# ===================================================================
print("=" * 70)
print("PHASE 393: ROSETTES CROSS-REFERENCE VALIDATION")
print("=" * 70)
print()

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Load bridge MIDDLEs
bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
with open(bridge_path, 'r', encoding='utf-8') as f:
    bridge_data = json.load(f)
bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])
print(f"Bridge MIDDLEs loaded: {len(bridge_middles)}")

# Load regime assignments
regime_path = ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}


# ===================================================================
# Compute profiles
# ===================================================================

def compute_profile(tokens):
    """Compute operational profile from a list of token words."""
    words = [w for w in tokens if w.strip()]
    n = len(words)
    if n == 0:
        return None

    # Kernel counts (character-level)
    k_chars = Counter()
    middles = set()
    e_middle_count = 0
    total_middle_count = 0
    for w in words:
        m = morph.extract(w)
        if m.middle:
            middles.add(m.middle)
            total_middle_count += 1
            if 'e' in m.middle:
                e_middle_count += 1
            for c in m.middle:
                if c in ('k', 'h', 'e'):
                    k_chars[c] += 1
    k_total = sum(k_chars.values())

    # Lane distribution
    lanes = Counter()
    for w in words:
        m = morph.extract(w)
        if m.prefix:
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            lanes[lane] += 1

    # Hazard source density
    haz_sources = sum(1 for w in words if w in HAZARD_SOURCES)

    # CC trigger distribution
    cc_counts = Counter()
    for w in words:
        if w in CC_TRIGGERS:
            cc_counts[CC_TRIGGERS[w]] += 1

    # Hub role distribution (using BFolioDecoder)
    hub_roles = Counter()
    for w in words:
        tc = decoder._token_to_class.get(w)
        if tc is not None:
            ms = decoder.MACRO_STATE.get(str(tc))
            if ms:
                hub_roles[ms] += 1

    ttr = len(middles) / n if n > 0 else 0
    e_kernel_frac = e_middle_count / total_middle_count if total_middle_count > 0 else 0

    return {
        'k_pct': k_chars['k'] / k_total if k_total > 0 else 0,
        'h_pct': k_chars['h'] / k_total if k_total > 0 else 0,
        'e_pct': k_chars['e'] / k_total if k_total > 0 else 0,
        'qo_pct': lanes.get('QO', 0) / n,
        'chsh_pct': lanes.get('CHSH', 0) / n,
        'link_pct': lanes.get('LINK', 0) / n,
        'haz_density': haz_sources / n,
        'ttr': ttr,
        'e_kernel_fraction': e_kernel_frac,
        'n_tokens': n,
        'n_unique_middles': len(middles),
        'middles': middles,  # for Jaccard
        'hub_roles': dict(hub_roles),
        'cc_triggers': dict(cc_counts),
    }


# --- Rosettes folio profiles ---
print("Computing Rosettes folio profiles...")
rosettes_tokens = defaultdict(list)
rosettes_f85v2_regions = defaultdict(list)

for tok in tx.all(h_only=False):
    if tok.folio in ROSETTES_FOLIOS:
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        # f85v2 uses U-track; others use H-track
        if tok.folio == 'f85v2':
            if tok.transcriber == 'U':
                rosettes_tokens[tok.folio].append(w)
                rosettes_f85v2_regions[tok.placement].append(w)
        else:
            if tok.transcriber == 'H':
                rosettes_tokens[tok.folio].append(w)

rosettes_profiles = {}
for folio in ROSETTES_FOLIOS:
    words = rosettes_tokens.get(folio, [])
    if words:
        rosettes_profiles[folio] = compute_profile(words)
        print(f"  {folio}: {len(words)} tokens")
    else:
        print(f"  {folio}: NO tokens (skipped)")

# --- f85v2 description region profiles ---
print("\nComputing f85v2 description region profiles...")
desc_profiles = {}
for group_name, regions in DESC_GROUPS.items():
    group_words = []
    for r in regions:
        group_words.extend(rosettes_f85v2_regions.get(r, []))
    if group_words:
        desc_profiles[group_name] = compute_profile(group_words)
        print(f"  {group_name}: {len(group_words)} tokens ({', '.join(regions)})")

# --- Body-text section profiles ---
print("\nComputing body-text section profiles...")
section_tokens = defaultdict(list)
section_folios = defaultdict(set)
folio_section_map = {}

for tok in tx.currier_b():
    if not tok.word.strip() or '*' in tok.word:
        continue
    section_tokens[tok.section].append(tok.word)
    section_folios[tok.section].add(tok.folio)
    folio_section_map[tok.folio] = tok.section

section_profiles = {}
for s in ['B', 'H', 'S']:
    section_profiles[s] = compute_profile(section_tokens[s])
    print(f"  Section {s}: {len(section_tokens[s])} tokens, {len(section_folios[s])} folios")

# --- Per-folio profiles for target folios and all B-corpus ---
print("\nComputing per-folio profiles for body-text folios...")
folio_tokens_b = defaultdict(list)
for tok in tx.currier_b():
    if not tok.word.strip() or '*' in tok.word:
        continue
    folio_tokens_b[tok.folio].append(tok.word)

folio_profiles = {}
for folio, words in folio_tokens_b.items():
    folio_profiles[folio] = compute_profile(words)

# --- Per-folio non-bridge MIDDLE sets for body text ---
section_nonbridge_middles = defaultdict(set)
for folio, prof in folio_profiles.items():
    s = folio_section_map.get(folio)
    if s and prof and 'middles' in prof:
        nonbridge = prof['middles'] - bridge_middles
        section_nonbridge_middles[s] |= nonbridge

print(f"\nNon-bridge MIDDLE counts by section:")
for s in ['B', 'H', 'S']:
    print(f"  Section {s}: {len(section_nonbridge_middles[s])} non-bridge MIDDLEs")
print()


# ===================================================================
# P1: DESCRIPTION REGION HETEROGENEITY (GATE)
# ===================================================================
print("-" * 70)
print("P1: Description Region Heterogeneity (GATE TEST)")
print("-" * 70)
print()

# Compute kernel + hub role vectors for each description group
def desc_vector(prof):
    """7-dim vector: k_pct, h_pct, e_pct, src_frac, tgt_frac, buf_frac, con_frac."""
    hub = prof.get('hub_roles', {})
    hub_total = sum(hub.values()) or 1
    return [
        prof.get('k_pct', 0), prof.get('h_pct', 0), prof.get('e_pct', 0),
        hub.get('AXM', 0) / hub_total,  # Use macro-states as available
        prof.get('haz_density', 0),
        prof.get('link_pct', 0),
        prof.get('e_kernel_fraction', 0),
    ]

desc_vectors = {}
for name in ['NORTH', 'VERT', 'CENTER']:
    if name in desc_profiles:
        desc_vectors[name] = desc_vector(desc_profiles[name])

# Pairwise cosine distances
pairs = [('NORTH', 'VERT'), ('NORTH', 'CENTER'), ('VERT', 'CENTER')]
real_distances = {}
for a, b in pairs:
    if a in desc_vectors and b in desc_vectors:
        sim = cosine_sim(desc_vectors[a], desc_vectors[b])
        dist = 1 - sim
        real_distances[f"{a}-{b}"] = dist
        print(f"  {a} vs {b}: cosine={sim:.4f}, distance={dist:.4f}")

mean_real_dist = np.mean(list(real_distances.values()))
print(f"\n  Mean pairwise distance: {mean_real_dist:.4f}")

# Permutation test: random blocks from full Rosettes corpus
all_rosettes_words = []
for folio in ROSETTES_FOLIOS:
    all_rosettes_words.extend(rosettes_tokens.get(folio, []))

rng = np.random.RandomState(42)
n_perms = 10000
group_sizes = [60, 62, 33]  # NORTH, VERT, CENTER
perm_means = []

for _ in range(n_perms):
    # Draw 3 random blocks
    block_vecs = []
    for sz in group_sizes:
        idx = rng.choice(len(all_rosettes_words), size=min(sz, len(all_rosettes_words)), replace=False)
        block_words = [all_rosettes_words[i] for i in idx]
        bp = compute_profile(block_words)
        if bp:
            block_vecs.append(desc_vector(bp))

    if len(block_vecs) == 3:
        dists = []
        for i in range(3):
            for j in range(i + 1, 3):
                dists.append(1 - cosine_sim(block_vecs[i], block_vecs[j]))
        perm_means.append(np.mean(dists))

perm_means = np.array(perm_means)
p1_p = float(np.mean(perm_means >= mean_real_dist))
p1_percentile = float(np.mean(perm_means < mean_real_dist) * 100)

print(f"  Permutation test ({n_perms} iterations):")
print(f"    Real mean distance: {mean_real_dist:.4f}")
print(f"    Permuted mean: {np.mean(perm_means):.4f} (sd={np.std(perm_means):.4f})")
print(f"    Percentile: {p1_percentile:.1f}th")
print(f"    p = {p1_p:.4f}")

if p1_p < 0.05:
    p1_verdict = "PASS_HETEROGENEOUS"
else:
    p1_verdict = "FAIL_HOMOGENEOUS"

p1_data = {
    'pairwise_distances': real_distances,
    'mean_distance': mean_real_dist,
    'permuted_mean': float(np.mean(perm_means)),
    'percentile': p1_percentile,
    'p': p1_p,
}

print(f"\nP1 VERDICT: {p1_verdict}")
print()


# ===================================================================
# P2: B-LIKE ROSETTES FOLIOS MATCH STARS CHARACTER
# ===================================================================
print("-" * 70)
print("P2: B-Like Rosettes Folios Match Stars/Pharma Character")
print("-" * 70)
print()

stars_vec = profile_vector(section_profiles['S'])
herbal_vec = profile_vector(section_profiles['H'])
bio_vec = profile_vector(section_profiles['B'])

b_like_folios = ['f86v3', 'f86v6']
p2_results = {}

for folio in ROSETTES_FOLIOS:
    if folio in rosettes_profiles:
        r_vec = profile_vector(rosettes_profiles[folio])
        cos_s = cosine_sim(r_vec, stars_vec)
        cos_h = cosine_sim(r_vec, herbal_vec)
        cos_b = cosine_sim(r_vec, bio_vec)
        is_blike = folio in b_like_folios
        print(f"  {folio} ({'B-like' if is_blike else 'other':>7}): "
              f"Stars={cos_s:.4f}, Herbal={cos_h:.4f}, Bio={cos_b:.4f}")
        p2_results[folio] = {
            'cos_stars': cos_s, 'cos_herbal': cos_h, 'cos_bio': cos_b,
            'best_match': 'S' if cos_s >= cos_h and cos_s >= cos_b else
                          'H' if cos_h >= cos_b else 'B',
            'b_like': is_blike,
        }

blike_stars_wins = sum(1 for f in b_like_folios
                       if f in p2_results and p2_results[f]['cos_stars'] > p2_results[f]['cos_herbal'])

if blike_stars_wins == 2:
    p2_verdict = "PASS_STARS_MATCH"
elif blike_stars_wins == 1:
    p2_verdict = "PARTIAL_STARS_MATCH"
else:
    p2_verdict = "FAIL_NO_MATCH"

p2_data = {'folio_results': p2_results, 'blike_stars_wins': blike_stars_wins}

print(f"\n  B-like folios with Stars > Herbal: {blike_stars_wins}/2")
print(f"\nP2 VERDICT: {p2_verdict}")
print()


# ===================================================================
# P3: NON-BRIDGE SECTION SIGNAL
# ===================================================================
print("-" * 70)
print("P3: Non-Bridge Section Signal")
print("-" * 70)
print()

p3_results = {}
for folio in ROSETTES_FOLIOS:
    if folio in rosettes_profiles and rosettes_profiles[folio].get('middles'):
        r_nonbridge = rosettes_profiles[folio]['middles'] - bridge_middles
        if r_nonbridge:
            jaccards = {}
            for s in ['B', 'H', 'S']:
                j = jaccard(r_nonbridge, section_nonbridge_middles[s])
                jaccards[s] = j
            best = max(jaccards, key=jaccards.get)
            is_blike = folio in b_like_folios
            print(f"  {folio} ({'B-like' if is_blike else 'other':>7}): "
                  f"B={jaccards['B']:.4f}, H={jaccards['H']:.4f}, S={jaccards['S']:.4f} -> {best}")
            p3_results[folio] = {
                'jaccard_B': jaccards['B'], 'jaccard_H': jaccards['H'],
                'jaccard_S': jaccards['S'], 'best': best,
                'n_nonbridge': len(r_nonbridge), 'b_like': is_blike,
            }

blike_s_top = sum(1 for f in b_like_folios
                  if f in p3_results and p3_results[f]['best'] == 'S')

if blike_s_top == 2:
    p3_verdict = "PASS_STARS_NONBRIDGE"
elif blike_s_top == 1:
    p3_verdict = "PARTIAL_STARS_NONBRIDGE"
else:
    p3_verdict = "FAIL_NOT_STARS"

p3_data = {'folio_results': p3_results, 'blike_s_top': blike_s_top}

print(f"\n  B-like folios with S as top non-bridge match: {blike_s_top}/2")
print(f"\nP3 VERDICT: {p3_verdict}")
print()


# ===================================================================
# P4: GRADIENT PREDICTS STARS SIMILARITY
# ===================================================================
print("-" * 70)
print("P4: AZC-to-B Gradient Predicts Stars Similarity")
print("-" * 70)
print()

# Prefix ratios from metalayer results (B-likeness = lower prefix ratio)
prefix_ratios = {
    'f85r1': 0.593, 'f85r2': 0.595, 'f85v2': 6.538,
    'f86v3': 0.354, 'f86v4': 0.639, 'f86v5': 0.710, 'f86v6': 0.296,
}

# Exclude f85v2 (AZC-like index page)
gradient_folios = [f for f in ROSETTES_FOLIOS if f != 'f85v2']

b_likeness = []
stars_sims = []
for folio in gradient_folios:
    if folio in rosettes_profiles and folio in prefix_ratios:
        r_vec = profile_vector(rosettes_profiles[folio])
        cos_s = cosine_sim(r_vec, stars_vec)
        bl = 1.0 / (1.0 + prefix_ratios[folio])  # Transform: lower ratio -> higher B-likeness
        b_likeness.append(bl)
        stars_sims.append(cos_s)
        print(f"  {folio}: prefix_ratio={prefix_ratios[folio]:.3f}, "
              f"B-likeness={bl:.3f}, Stars_cosine={cos_s:.4f}")

from scipy import stats as sp_stats

p4_rho, p4_p = 0, 1.0
if len(b_likeness) >= 4:
    p4_rho, p4_p = sp_stats.spearmanr(b_likeness, stars_sims)
    print(f"\n  Spearman rho = {p4_rho:.3f}, p = {p4_p:.4f}")

if p4_rho > 0.50 and p4_p < 0.05:
    p4_verdict = "PASS_GRADIENT"
elif p4_rho > 0.30:
    p4_verdict = "PARTIAL_GRADIENT"
else:
    p4_verdict = "FAIL_NO_GRADIENT"

p4_data = {'rho': float(p4_rho), 'p': float(p4_p),
           'b_likeness': b_likeness, 'stars_sims': stars_sims}

print(f"\nP4 VERDICT: {p4_verdict}")
print()


# ===================================================================
# P5: TARGET FOLIO SPECIFICITY
# ===================================================================
print("-" * 70)
print("P5: Target Folio Specificity")
print("-" * 70)
print()

# Compute cosine between B-like Rosettes folios and target folios
target_cosines = []
for rf in b_like_folios:
    if rf in rosettes_profiles:
        r_vec = profile_vector(rosettes_profiles[rf])
        for tf in TARGET_FOLIOS:
            if tf in folio_profiles:
                t_vec = profile_vector(folio_profiles[tf])
                cos = cosine_sim(r_vec, t_vec)
                target_cosines.append(cos)

mean_target_cos = np.mean(target_cosines) if target_cosines else 0

# All B-corpus folios (excluding targets and Rosettes)
all_b_folios = [f for f in folio_profiles.keys()
                if f not in TARGET_FOLIOS and f not in ROSETTES_FOLIOS]

print(f"  Mean cosine (B-like Rosettes vs {len(TARGET_FOLIOS)} targets): {mean_target_cos:.4f}")

# Permutation: random selections of 5 B-corpus folios
n_perms = 10000
perm_cosines = []
rng = np.random.RandomState(42)

for _ in range(n_perms):
    random_folios = rng.choice(all_b_folios, size=min(5, len(all_b_folios)), replace=False)
    rand_cos = []
    for rf in b_like_folios:
        if rf in rosettes_profiles:
            r_vec = profile_vector(rosettes_profiles[rf])
            for tf in random_folios:
                if tf in folio_profiles:
                    t_vec = profile_vector(folio_profiles[tf])
                    rand_cos.append(cosine_sim(r_vec, t_vec))
    if rand_cos:
        perm_cosines.append(np.mean(rand_cos))

perm_cosines = np.array(perm_cosines)
mean_random_cos = float(np.mean(perm_cosines))
lift = mean_target_cos / mean_random_cos if mean_random_cos > 0 else 0
p5_p = float(np.mean(perm_cosines >= mean_target_cos))

print(f"  Mean cosine (B-like Rosettes vs random 5): {mean_random_cos:.4f}")
print(f"  Lift: {lift:.3f}x")
print(f"  Permutation p = {p5_p:.4f}")

if p5_p < 0.05 and lift > 1.2:
    p5_verdict = "PASS_SPECIFIC"
elif lift > 1.1:
    p5_verdict = "PARTIAL_SPECIFIC"
else:
    p5_verdict = "FAIL_NOT_SPECIFIC"

p5_data = {
    'mean_target_cosine': float(mean_target_cos),
    'mean_random_cosine': mean_random_cos,
    'lift': float(lift),
    'p': p5_p,
}

print(f"\nP5 VERDICT: {p5_verdict}")
print()


# ===================================================================
# P6: CENTER CONVERGENCE DISTINCTIVENESS
# ===================================================================
print("-" * 70)
print("P6: CENTER Convergence Distinctiveness")
print("-" * 70)
print()

# Use pre-computed data from rosette_decoder_map.json for hub balance
# NORTH: src=17, tgt=15, buf=6, con=7 (total=45)
# VERT: src=17, tgt=18, buf=4, con=9 (total=48)
# CENTER: src=4, tgt=11, buf=4, con=5 (total=24)
# Also use kernel data: NORTH k_pct=69.2%, VERT k_pct=71.9%, CENTER k_pct=54.5%

hub_data = {
    'NORTH': {'src': 17, 'tgt': 15, 'buf': 6, 'con': 7, 'total': 45, 'k_pct': 69.2, 'hazard_pct': 71.1},
    'VERT': {'src': 17, 'tgt': 18, 'buf': 4, 'con': 9, 'total': 48, 'k_pct': 71.9, 'hazard_pct': 72.9},
    'CENTER': {'src': 4, 'tgt': 11, 'buf': 4, 'con': 5, 'total': 24, 'k_pct': 54.5, 'hazard_pct': 62.5},
}

for name, d in hub_data.items():
    tgt_frac = d['tgt'] / d['total'] if d['total'] > 0 else 0
    d['tgt_fraction'] = tgt_frac
    print(f"  {name}: tgt_fraction={tgt_frac:.3f}, k_pct={d['k_pct']:.1f}%, hazard={d['hazard_pct']:.1f}%")

center_tgt = hub_data['CENTER']['tgt_fraction']
north_tgt = hub_data['NORTH']['tgt_fraction']
vert_tgt = hub_data['VERT']['tgt_fraction']

center_k = hub_data['CENTER']['k_pct']
north_k = hub_data['NORTH']['k_pct']
vert_k = hub_data['VERT']['k_pct']

tgt_condition = center_tgt > north_tgt and center_tgt > vert_tgt
k_condition = center_k < north_k and center_k < vert_k

print(f"\n  CENTER tgt_fraction ({center_tgt:.3f}) > NORTH ({north_tgt:.3f}): {tgt_condition}")
print(f"  CENTER tgt_fraction ({center_tgt:.3f}) > VERT ({vert_tgt:.3f}): {tgt_condition}")
print(f"  CENTER k_pct ({center_k:.1f}) < NORTH ({north_k:.1f}): {k_condition}")
print(f"  CENTER k_pct ({center_k:.1f}) < VERT ({vert_k:.1f}): {k_condition}")

if tgt_condition and k_condition:
    p6_verdict = "PASS_CONVERGENCE_CONFIRMED"
elif tgt_condition or k_condition:
    p6_verdict = "PARTIAL_CONVERGENCE"
else:
    p6_verdict = "FAIL_NOT_DISTINCT"

p6_data = {
    'hub_balance': hub_data,
    'tgt_condition': tgt_condition,
    'k_condition': k_condition,
}

print(f"\nP6 VERDICT: {p6_verdict}")
print()


# ===================================================================
# SYNTHESIS
# ===================================================================
print("=" * 70)
print("PHASE 393 SYNTHESIS")
print("=" * 70)
print()

verdicts = {
    'P1': p1_verdict, 'P2': p2_verdict, 'P3': p3_verdict,
    'P4': p4_verdict, 'P5': p5_verdict, 'P6': p6_verdict,
}

for k, v in verdicts.items():
    print(f"  {k}: {v}")
print()

p1_pass = 'PASS' in p1_verdict
p2_to_p6_pass = sum(1 for k in ['P2', 'P3', 'P4', 'P5', 'P6'] if 'PASS' in verdicts[k])
p2_to_p6_partial = sum(1 for k in ['P2', 'P3', 'P4', 'P5', 'P6'] if 'PARTIAL' in verdicts[k])

print(f"Gate (P1): {'PASS' if p1_pass else 'FAIL'}")
print(f"Content tests (P2-P6): {p2_to_p6_pass} PASS, {p2_to_p6_partial} PARTIAL")
print()

if p1_pass and p2_to_p6_pass >= 4:
    overall = "ROSETTES_PROCESS_GUIDE"
    summary = ("The Rosettes demonstrates target section character in its B-like folios and "
               "differentiates process types in its description regions. It is a process-type reference guide.")
elif p1_pass and p2_to_p6_pass + p2_to_p6_partial >= 3:
    overall = "ROSETTES_SECTION_INDEX"
    summary = ("The Rosettes matches section character but evidence for folio-level specificity is mixed. "
               "It indexes section membership but may not differentiate individual procedures.")
elif not p1_pass or p2_to_p6_pass <= 1:
    overall = "ROSETTES_VOCABULARY_ONLY"
    summary = ("The Rosettes index function operates purely through vocabulary overlap, "
               "not operational demonstration.")
else:
    overall = "INCONCLUSIVE"
    summary = "Mixed results."

print(f"OVERALL VERDICT: {overall}")
print(f"  {summary}")
print()

# Remove non-serializable sets from profiles
def clean_profile(prof):
    if prof is None:
        return None
    p = {k: v for k, v in prof.items() if k != 'middles'}
    return p

# Assemble results
results = round_floats({
    'phase': 393,
    'name': 'ROSETTES_CROSS_REFERENCE_VALIDATION',
    'test_count': 6,
    'rosettes_folios': ROSETTES_FOLIOS,
    'target_folios': TARGET_FOLIOS,
    'verdicts': verdicts,
    'P1_data': p1_data,
    'P2_data': p2_data,
    'P3_data': {k: v for k, v in p3_data.items() if k != 'folio_results'},
    'P3_folio_results': {k: v for k, v in p3_data.get('folio_results', {}).items()},
    'P4_data': p4_data,
    'P5_data': p5_data,
    'P6_data': p6_data,
    'rosettes_profiles': {f: clean_profile(p) for f, p in rosettes_profiles.items()},
    'desc_profiles': {n: clean_profile(p) for n, p in desc_profiles.items()},
    'synthesis': {
        'gate_pass': p1_pass,
        'content_pass': p2_to_p6_pass,
        'content_partial': p2_to_p6_partial,
        'overall': overall,
        'summary': summary,
    },
})

output_path = RESULTS / 'rosettes_crossref_validation.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to: {output_path}")
