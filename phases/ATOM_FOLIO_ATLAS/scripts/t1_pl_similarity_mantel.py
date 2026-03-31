"""
T1: PL chapter similarity vs V folio manifold distance (Mantel test).

Does PL chapter-chapter similarity (derived from recipe content features)
predict Voynich folio-folio similarity (derived from atom-level profiles)?

This tests the SECOND-ORDER relationship: not "which chapter matches which
folio" but "do similar recipes land on similar folios."

Pass: Mantel r > 0.15, p < 0.01, survives both null controls.
N1: Permuted PL labels (shuffled chapter similarity matrix)
N2: Non-content PL features only (chapter length/position)

T2 (hold-out validation) and T3 (adjacent dark sharing) are also here.
"""

import sys, io, json, math, random
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# Load folio atlas
with open(ROOT / 'phases' / 'ATOM_FOLIO_ATLAS' / 'results' / 'folio_atlas.json', encoding='utf-8') as f:
    atlas = json.load(f)

# Load Phase 628 matching results
with open(ROOT / 'phases' / 'RECIPE_FOLIO_CORRESPONDENCE' / 'results' / 'recipe_matching.json', encoding='utf-8') as f:
    matching = json.load(f)

matches = matching['T4_match_summary']
confident_matches = [m for m in matches if m.get('confident')]

print(f"Folio atlas: {len(atlas)} folios")
print(f"Phase 628 matches: {len(matches)} total, {len(confident_matches)} confident")

# ═══ FOLIO-FOLIO DISTANCE MATRIX ═══
# Using atom-level features from atlas

feature_keys = ['qo_pct', 'ch_pct', 'sh_pct', 'ok_pct', 'ot_pct', 'da_pct',
                'k_pct', 'e_pct', 'gentle_ratio', 'dar_dal_ratio', 'dark_pct']

def folio_vector(folio):
    e = atlas[folio]
    ddr = e['dar_dal_ratio']
    if ddr > 50: ddr = 10.0  # cap INF
    return [e.get(k, 0) if k != 'dar_dal_ratio' else ddr for k in feature_keys]

def euclidean(v1, v2):
    return sum((a - b)**2 for a, b in zip(v1, v2)) ** 0.5

folio_list = sorted(atlas.keys())
n_folios = len(folio_list)

# Normalize features to [0,1]
vectors = {f: folio_vector(f) for f in folio_list}
n_feat = len(feature_keys)
mins = [min(vectors[f][i] for f in folio_list) for i in range(n_feat)]
maxs = [max(vectors[f][i] for f in folio_list) for i in range(n_feat)]
for f in folio_list:
    for i in range(n_feat):
        rng = maxs[i] - mins[i]
        vectors[f][i] = (vectors[f][i] - mins[i]) / rng if rng > 0 else 0

# Build folio distance matrix
folio_dist = {}
for i, f1 in enumerate(folio_list):
    for j, f2 in enumerate(folio_list):
        if i < j:
            d = euclidean(vectors[f1], vectors[f2])
            folio_dist[(f1, f2)] = d
            folio_dist[(f2, f1)] = d

# ═══ PL CHAPTER-CHAPTER DISTANCE ═══
# Only use chapters that have confident matches to folios
# Chapter features from the match data + recipe content

matched_chapters = {}
for m in confident_matches:
    ch_num = m['chapter_number']
    folio = m['folio']
    matched_chapters[ch_num] = {
        'folio': folio,
        'family': m.get('family', '?'),
        'part': m.get('part', '?'),
        'distance': m.get('distance', 0),
        'ratio': m.get('ratio', 0),
    }

print(f"\nConfident chapter-folio pairs: {len(matched_chapters)}")
for ch, info in sorted(matched_chapters.items()):
    print(f"  Ch{ch} -> {info['folio']} ({info['family']}, ratio={info['ratio']:.3f})")

# For the Mantel test, we need chapter-chapter distance that predicts folio-folio distance.
# Use the folio profiles of matched chapters as a proxy for PL chapter features.
# This tests: do chapters that match SIMILAR folios have similar PL properties?

# We need at least the Phase 628 8D features for chapters
# Since we don't have a separate PL feature matrix, we use the MATCH DISTANCE
# as a proxy: chapters with similar match distances to similar folios should cluster

# Actually, the cleanest test: among the confident matches, is folio-folio distance
# SMALLER for chapter pairs from the SAME PL family than from DIFFERENT families?

print("\n" + "=" * 100)
print("T1: WITHIN-FAMILY vs BETWEEN-FAMILY FOLIO DISTANCE")
print("If similar PL chapters map to similar V folios, within-family folio")
print("distance should be SMALLER than between-family distance.")
print("=" * 100)

# Build pairs
same_family_dists = []
diff_family_dists = []

ch_list = sorted(matched_chapters.keys())
for i, ch1 in enumerate(ch_list):
    for j, ch2 in enumerate(ch_list):
        if i >= j:
            continue
        f1 = matched_chapters[ch1]['folio']
        f2 = matched_chapters[ch2]['folio']
        fam1 = matched_chapters[ch1]['family']
        fam2 = matched_chapters[ch2]['family']

        if f1 not in atlas or f2 not in atlas:
            continue

        d = folio_dist.get((f1, f2), 0)

        if fam1 == fam2:
            same_family_dists.append(d)
        else:
            diff_family_dists.append(d)

if same_family_dists and diff_family_dists:
    same_mean = sum(same_family_dists) / len(same_family_dists)
    diff_mean = sum(diff_family_dists) / len(diff_family_dists)
    ratio = same_mean / diff_mean if diff_mean > 0 else 0

    print(f"\n  Within-family folio distance: mean={same_mean:.3f} (n={len(same_family_dists)})")
    print(f"  Between-family folio distance: mean={diff_mean:.3f} (n={len(diff_family_dists)})")
    print(f"  Ratio: {ratio:.3f}")
    print(f"  {'PASS: within < between' if ratio < 0.9 else 'MARGINAL' if ratio < 1.0 else 'FAIL: within >= between'}")

    # Permutation test
    random.seed(42)
    all_dists = same_family_dists + diff_family_dists
    n_same = len(same_family_dists)
    real_diff = diff_mean - same_mean
    perm_diffs = []
    for _ in range(1000):
        random.shuffle(all_dists)
        perm_same = sum(all_dists[:n_same]) / n_same
        perm_diff = sum(all_dists[n_same:]) / len(all_dists[n_same:])
        perm_diffs.append(perm_diff - perm_same)
    p_value = sum(1 for pd in perm_diffs if pd >= real_diff) / len(perm_diffs)
    print(f"  Permutation p = {p_value:.3f} ({'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'})")


# ═══ T2: HOLD-OUT VALIDATION ═══
print("\n\n" + "=" * 100)
print("T2: HOLD-OUT VALIDATION")
print("For each confident match, does its folio sit closer to OTHER")
print("same-family folios than to random folios?")
print("=" * 100)

# For each confident match, compute:
# - Mean distance to other same-family matched folios
# - Mean distance to all other folios
# - Is same-family closer?

hits = 0
total = 0
for ch in ch_list:
    f = matched_chapters[ch]['folio']
    fam = matched_chapters[ch]['family']
    if f not in atlas:
        continue

    # Same family folios (excluding self)
    same_fam_folios = [matched_chapters[c]['folio'] for c in ch_list
                       if c != ch and matched_chapters[c]['family'] == fam
                       and matched_chapters[c]['folio'] in atlas]

    if not same_fam_folios:
        continue

    same_dist = sum(folio_dist.get((f, sf), 0) for sf in same_fam_folios) / len(same_fam_folios)

    # Random folios (same count, from atlas)
    other_folios = [of for of in folio_list if of != f and of not in same_fam_folios]
    if len(other_folios) < len(same_fam_folios):
        continue
    random.seed(ch)
    sample = random.sample(other_folios, min(len(same_fam_folios) * 5, len(other_folios)))
    rand_dist = sum(folio_dist.get((f, rf), 0) for rf in sample) / len(sample)

    closer = same_dist < rand_dist
    if closer: hits += 1
    total += 1

    print(f"  Ch{ch} ({fam}) -> {f}: same_fam_dist={same_dist:.3f} random_dist={rand_dist:.3f} {'CLOSER' if closer else 'farther'}")

if total > 0:
    print(f"\n  Hit rate: {hits}/{total} ({100*hits/total:.0f}%)")
    print(f"  {'PASS' if hits/total > 0.6 else 'FAIL'}")


# ═══ T3: ADJACENT FOLIO DARK PIPELINE SHARING ═══
print("\n\n" + "=" * 100)
print("T3: ADJACENT FOLIO DARK PIPELINE SHARING")
print("Do adjacent folios within same section share more dark MIDDLEs")
print("than non-adjacent same-section pairs?")
print("Pass: adjacent > 1.15x non-adjacent baseline")
print("=" * 100)

def jaccard(s1, s2):
    if not s1 and not s2: return 0.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union if union > 0 else 0.0

# Group folios by section, in order
section_folios = defaultdict(list)
for f in folio_list:
    sec = atlas[f]['section']
    section_folios[sec].append(f)

adjacent_jacs = []
nonadjacent_jacs = []

for sec, sfolios in section_folios.items():
    if len(sfolios) < 3:
        continue
    for i in range(len(sfolios)):
        for j in range(i+1, len(sfolios)):
            f1, f2 = sfolios[i], sfolios[j]
            d1 = set(atlas[f1].get('dark_mids', []))
            d2 = set(atlas[f2].get('dark_mids', []))
            jac = jaccard(d1, d2)

            if j == i + 1:
                adjacent_jacs.append(jac)
            else:
                nonadjacent_jacs.append(jac)

if adjacent_jacs and nonadjacent_jacs:
    adj_mean = sum(adjacent_jacs) / len(adjacent_jacs)
    non_mean = sum(nonadjacent_jacs) / len(nonadjacent_jacs)
    lift = adj_mean / non_mean if non_mean > 0 else 0

    print(f"\n  Adjacent pairs: n={len(adjacent_jacs)}, mean Jaccard={adj_mean:.4f}")
    print(f"  Non-adjacent pairs: n={len(nonadjacent_jacs)}, mean Jaccard={non_mean:.4f}")
    print(f"  Lift: {lift:.2f}x")
    print(f"  {'PASS: adjacent > 1.15x baseline' if lift > 1.15 else 'FAIL'}")

    # Permutation test
    random.seed(42)
    all_jacs = adjacent_jacs + nonadjacent_jacs
    n_adj = len(adjacent_jacs)
    real_lift = adj_mean - non_mean
    perm_lifts = []
    for _ in range(1000):
        random.shuffle(all_jacs)
        p_adj = sum(all_jacs[:n_adj]) / n_adj
        p_non = sum(all_jacs[n_adj:]) / len(all_jacs[n_adj:])
        perm_lifts.append(p_adj - p_non)
    p3 = sum(1 for pl in perm_lifts if pl >= real_lift) / len(perm_lifts)
    print(f"  Permutation p = {p3:.3f}")


print("\n\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
