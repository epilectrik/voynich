"""
35_azc_nesting_correspondence.py

Do AZC spatial positions (S/R/C) correspond to B nesting layers (FL/OL-OR/CENTER)?

Hypothesis: AZC diagrams spatially render the same center-out structure
that B lines encode linearly:

    AZC spatial         B linear
    -----------         --------
    S-series (edge)  <-> FL bookends (boundary)
    R-series (rings) <-> OL/OR (inner frame)
    C (center)       <-> CENTER (free content)

Tests:
  1. VOCABULARY OVERLAP: Do S-position words appear near FL in B?
     Do C-position words appear at CENTER in B?
  2. PREFIX PROFILE MATCH: Does prefix distribution at each AZC zone
     match the corresponding B layer?
  3. MIDDLE OVERLAP: Do the FL MIDDLEs appear in S-positions?
  4. ROLE PROFILE: Do role distributions align across corresponding zones?
  5. ENRICHMENT: For shared vocabulary, is it enriched at the
     corresponding layer vs the wrong layer?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency, fisher_exact

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}

tx = Transcript()
morph = Morphology()
MIN_N = 50

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']
token_to_role = class_data['token_to_role']

# ============================================================
# PART 1: Build AZC zone vocabularies
# ============================================================
print("=" * 70)
print("PART 1: AZC ZONE VOCABULARIES")
print("=" * 70)

azc_zone_words = defaultdict(Counter)     # zone -> word counter
azc_zone_prefixes = defaultdict(Counter)  # zone -> prefix counter
azc_zone_middles = defaultdict(Counter)   # zone -> middle counter
azc_zone_roles = defaultdict(Counter)     # zone -> role counter

def classify_placement(placement):
    """Map placement code to zone: S_SERIES, R_SERIES, CENTER, PARA, OTHER."""
    p = placement.strip()
    if p.startswith('S'):
        return 'S_SERIES'
    elif p.startswith('R'):
        return 'R_SERIES'
    elif p.startswith('C'):
        return 'CENTER_AZC'
    elif p.startswith('P'):
        return 'PARA'  # Not diagram - exclude
    elif p.startswith('L'):
        return 'LABEL'  # Exclude
    else:
        return 'OTHER'

for t in tx.azc():
    zone = classify_placement(t.placement)
    if zone in ('PARA', 'LABEL', 'OTHER'):
        continue

    m = morph.extract(t.word)
    prefix = m.prefix if m and m.prefix else 'NONE'
    middle = m.middle if m and m.middle else 'UNKNOWN'
    role = token_to_role.get(t.word, 'UNKNOWN')

    azc_zone_words[zone][t.word] += 1
    azc_zone_prefixes[zone][prefix] += 1
    azc_zone_middles[zone][middle] += 1
    azc_zone_roles[zone][role] += 1

for zone in ['S_SERIES', 'R_SERIES', 'CENTER_AZC']:
    total = sum(azc_zone_words[zone].values())
    n_types = len(azc_zone_words[zone])
    print(f"\n  {zone}: {total} tokens, {n_types} types")
    top5 = azc_zone_words[zone].most_common(5)
    print(f"    Top words: {', '.join(f'{w}({c})' for w, c in top5)}")

# ============================================================
# PART 2: Build B nesting layer vocabularies
# ============================================================
print(f"\n{'=' * 70}")
print("PART 2: B NESTING LAYER VOCABULARIES")
print("=" * 70)

line_tokens = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)

# Fit GMMs
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

# Classify B tokens into nesting layers
b_layer_words = defaultdict(Counter)
b_layer_prefixes = defaultdict(Counter)
b_layer_middles = defaultdict(Counter)
b_layer_roles = defaultdict(Counter)

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'

        prefix = m.prefix if m and m.prefix else 'NONE'
        middle = m.middle if m and m.middle else 'UNKNOWN'
        role = token_to_role.get(t.word, 'UNKNOWN')

        all_info.append({
            'word': t.word, 'idx': idx, 'is_fl': is_fl,
            'mode': mode, 'prefix': prefix, 'middle': middle, 'role': role,
        })

    low_fls = [a for a in all_info if a['is_fl'] and a['mode'] == 'LOW']
    high_fls = [a for a in all_info if a['is_fl'] and a['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)

    gap = [a for a in all_info if not a['is_fl']
           and a['idx'] > max_low_idx and a['idx'] < min_high_idx]
    if len(gap) < 2:
        continue

    # Assign layers
    for a in all_info:
        if a['is_fl']:
            layer = 'FL_BOOKEND'
        elif a['idx'] <= max_low_idx or a['idx'] >= min_high_idx:
            layer = 'PREAMBLE_CODA'  # outside the nesting
        elif a == gap[0]:
            layer = 'OL'
        elif a == gap[-1]:
            layer = 'OR'
        elif a['idx'] > gap[0]['idx'] and a['idx'] < gap[-1]['idx']:
            layer = 'CENTER_B'
        else:
            layer = 'FRAME'  # OL or OR (if gap has exactly 2)
            continue

        b_layer_words[layer][a['word']] += 1
        b_layer_prefixes[layer][a['prefix']] += 1
        b_layer_middles[layer][a['middle']] += 1
        b_layer_roles[layer][a['role']] += 1

for layer in ['FL_BOOKEND', 'OL', 'OR', 'CENTER_B', 'PREAMBLE_CODA']:
    total = sum(b_layer_words[layer].values())
    n_types = len(b_layer_words[layer])
    print(f"\n  {layer}: {total} tokens, {n_types} types")
    top5 = b_layer_words[layer].most_common(5)
    print(f"    Top words: {', '.join(f'{w}({c})' for w, c in top5)}")

# ============================================================
# TEST 1: WORD-LEVEL OVERLAP MATRIX
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 1: WORD-LEVEL OVERLAP (Jaccard)")
print("=" * 70)

azc_zones = ['S_SERIES', 'R_SERIES', 'CENTER_AZC']
b_layers = ['FL_BOOKEND', 'OL', 'OR', 'CENTER_B']

# Word sets (types appearing 2+ times)
azc_word_sets = {z: set(w for w, c in azc_zone_words[z].items() if c >= 2) for z in azc_zones}
b_word_sets = {l: set(w for w, c in b_layer_words[l].items() if c >= 2) for l in b_layers}

print(f"\n  Jaccard overlap (word types, n>=2):")
print(f"  {'AZC zone':<15}", end='')
for bl in b_layers:
    print(f" {bl:>12}", end='')
print()
print(f"  {'-'*65}")

overlap_matrix = {}
for az in azc_zones:
    print(f"  {az:<15}", end='')
    overlap_matrix[az] = {}
    for bl in b_layers:
        inter = len(azc_word_sets[az] & b_word_sets[bl])
        union = len(azc_word_sets[az] | b_word_sets[bl])
        jacc = inter / union if union > 0 else 0
        overlap_matrix[az][bl] = jacc
        print(f" {jacc:>11.3f}", end='')
    print()

# Which B layer has HIGHEST overlap for each AZC zone?
print(f"\n  Best B-layer match for each AZC zone:")
for az in azc_zones:
    best = max(b_layers, key=lambda bl: overlap_matrix[az][bl])
    print(f"    {az:<15} -> {best} (Jaccard={overlap_matrix[az][best]:.3f})")

# ============================================================
# TEST 2: PREFIX PROFILE COMPARISON
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 2: PREFIX PROFILE COMPARISON")
print("=" * 70)

top_pfx = ['ch', 'sh', 'qo', 'NONE', 'ok', 'ot', 'ol', 'd', 's']

print(f"\n  AZC zones:")
print(f"  {'Zone':<15}", end='')
for p in top_pfx:
    print(f" {p:>5}", end='')
print()
print(f"  {'-'*60}")
for az in azc_zones:
    total = sum(azc_zone_prefixes[az].values())
    print(f"  {az:<15}", end='')
    for p in top_pfx:
        pct = azc_zone_prefixes[az].get(p, 0) / total * 100 if total > 0 else 0
        print(f" {pct:>4.1f}%", end='')
    print()

print(f"\n  B layers:")
print(f"  {'Layer':<15}", end='')
for p in top_pfx:
    print(f" {p:>5}", end='')
print()
print(f"  {'-'*60}")
for bl in ['FL_BOOKEND', 'OL', 'OR', 'CENTER_B']:
    total = sum(b_layer_prefixes[bl].values())
    print(f"  {bl:<15}", end='')
    for p in top_pfx:
        pct = b_layer_prefixes[bl].get(p, 0) / total * 100 if total > 0 else 0
        print(f" {pct:>4.1f}%", end='')
    print()

# Cosine similarity between prefix profiles
def prefix_cosine(counter1, counter2, pfx_list):
    """Cosine similarity between two prefix distributions."""
    total1 = sum(counter1.values())
    total2 = sum(counter2.values())
    if total1 == 0 or total2 == 0:
        return 0
    v1 = np.array([counter1.get(p, 0) / total1 for p in pfx_list])
    v2 = np.array([counter2.get(p, 0) / total2 for p in pfx_list])
    dot = np.dot(v1, v2)
    norm = np.linalg.norm(v1) * np.linalg.norm(v2)
    return dot / norm if norm > 0 else 0

print(f"\n  Prefix profile cosine similarity (AZC zone x B layer):")
print(f"  {'AZC zone':<15}", end='')
for bl in b_layers:
    print(f" {bl:>12}", end='')
print()
print(f"  {'-'*65}")

pfx_cosine_matrix = {}
for az in azc_zones:
    pfx_cosine_matrix[az] = {}
    print(f"  {az:<15}", end='')
    for bl in b_layers:
        cos = prefix_cosine(azc_zone_prefixes[az], b_layer_prefixes[bl], top_pfx)
        pfx_cosine_matrix[az][bl] = cos
        print(f" {cos:>11.3f}", end='')
    print()

print(f"\n  Best prefix match:")
for az in azc_zones:
    best = max(b_layers, key=lambda bl: pfx_cosine_matrix[az][bl])
    print(f"    {az:<15} -> {best} (cosine={pfx_cosine_matrix[az][best]:.3f})")

# ============================================================
# TEST 3: FL MIDDLE PRESENCE IN AZC ZONES
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 3: FL MIDDLE PRESENCE IN AZC ZONES")
print("=" * 70)

fl_middles = set(FL_STAGE_MAP.keys())

print(f"\n  FL MIDDLEs found in each AZC zone:")
for az in azc_zones:
    fl_in_zone = {m: c for m, c in azc_zone_middles[az].items() if m in fl_middles}
    total_fl = sum(fl_in_zone.values())
    total_all = sum(azc_zone_middles[az].values())
    pct = total_fl / total_all * 100 if total_all > 0 else 0
    print(f"\n  {az}: {total_fl}/{total_all} tokens have FL MIDDLEs ({pct:.1f}%)")
    if fl_in_zone:
        for m, c in sorted(fl_in_zone.items(), key=lambda x: -x[1])[:8]:
            print(f"    {m:<6}: {c:>4}")

# Same for B layers
print(f"\n  FL MIDDLEs in B layers (for comparison):")
for bl in b_layers:
    fl_in_layer = {m: c for m, c in b_layer_middles[bl].items() if m in fl_middles}
    total_fl = sum(fl_in_layer.values())
    total_all = sum(b_layer_middles[bl].values())
    pct = total_fl / total_all * 100 if total_all > 0 else 0
    print(f"  {bl}: {pct:.1f}% FL MIDDLEs")

# ============================================================
# TEST 4: ROLE PROFILE COMPARISON
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 4: ROLE PROFILE COMPARISON")
print("=" * 70)

roles_list = ['ENERGY_OPERATOR', 'FREQUENT_OPERATOR', 'CORE_CONTROL', 'AUXILIARY', 'UNKNOWN']

print(f"\n  AZC zones:")
print(f"  {'Zone':<15}", end='')
for r in roles_list:
    print(f" {r[:8]:>9}", end='')
print()
print(f"  {'-'*60}")
for az in azc_zones:
    total = sum(azc_zone_roles[az].values())
    print(f"  {az:<15}", end='')
    for r in roles_list:
        pct = azc_zone_roles[az].get(r, 0) / total * 100 if total > 0 else 0
        print(f" {pct:>8.1f}%", end='')
    print()

print(f"\n  B layers:")
print(f"  {'Layer':<15}", end='')
for r in roles_list:
    print(f" {r[:8]:>9}", end='')
print()
print(f"  {'-'*60}")
for bl in b_layers:
    total = sum(b_layer_roles[bl].values())
    print(f"  {bl:<15}", end='')
    for r in roles_list:
        pct = b_layer_roles[bl].get(r, 0) / total * 100 if total > 0 else 0
        print(f" {pct:>8.1f}%", end='')
    print()

# Role cosine
print(f"\n  Role profile cosine similarity:")
print(f"  {'AZC zone':<15}", end='')
for bl in b_layers:
    print(f" {bl:>12}", end='')
print()
print(f"  {'-'*65}")

role_cosine_matrix = {}
for az in azc_zones:
    role_cosine_matrix[az] = {}
    print(f"  {az:<15}", end='')
    for bl in b_layers:
        cos = prefix_cosine(azc_zone_roles[az], b_layer_roles[bl], roles_list)
        role_cosine_matrix[az][bl] = cos
        print(f" {cos:>11.3f}", end='')
    print()

# ============================================================
# TEST 5: ENRICHMENT TEST
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 5: DIRECTIONAL ENRICHMENT")
print("=" * 70)

# For words shared between AZC and B:
# Are S-series words enriched at FL_BOOKEND relative to CENTER_B?
# Are C words enriched at CENTER_B relative to FL_BOOKEND?

def enrichment_test(azc_zone, b_target, b_other, azc_words, b_words_target, b_words_other):
    """Test if azc_zone vocabulary is enriched at b_target vs b_other."""
    azc_vocab = set(w for w, c in azc_words[azc_zone].items() if c >= 2)
    target_total = sum(b_words_target.values())
    other_total = sum(b_words_other.values())

    if target_total == 0 or other_total == 0:
        return None

    target_hits = sum(b_words_target.get(w, 0) for w in azc_vocab)
    other_hits = sum(b_words_other.get(w, 0) for w in azc_vocab)

    target_rate = target_hits / target_total
    other_rate = other_hits / other_total
    lift = target_rate / other_rate if other_rate > 0 else float('inf')

    return {
        'target_rate': target_rate,
        'other_rate': other_rate,
        'lift': lift,
        'target_hits': target_hits,
        'other_hits': other_hits,
        'azc_vocab_size': len(azc_vocab),
    }

# S_SERIES -> FL_BOOKEND vs CENTER_B
test_s_fl = enrichment_test('S_SERIES', 'FL_BOOKEND', 'CENTER_B',
                             azc_zone_words, b_layer_words['FL_BOOKEND'],
                             b_layer_words['CENTER_B'])

# S_SERIES -> OL vs CENTER_B (alternative: maybe S maps to OL?)
test_s_ol = enrichment_test('S_SERIES', 'OL', 'CENTER_B',
                             azc_zone_words, b_layer_words['OL'],
                             b_layer_words['CENTER_B'])

# R_SERIES -> OL vs CENTER_B
test_r_ol = enrichment_test('R_SERIES', 'OL', 'CENTER_B',
                             azc_zone_words, b_layer_words['OL'],
                             b_layer_words['CENTER_B'])

# R_SERIES -> OR vs CENTER_B
test_r_or = enrichment_test('R_SERIES', 'OR', 'CENTER_B',
                             azc_zone_words, b_layer_words['OR'],
                             b_layer_words['CENTER_B'])

# CENTER_AZC -> CENTER_B vs FL_BOOKEND
test_c_center = enrichment_test('CENTER_AZC', 'CENTER_B', 'FL_BOOKEND',
                                 azc_zone_words, b_layer_words['CENTER_B'],
                                 b_layer_words['FL_BOOKEND'])

# CENTER_AZC -> CENTER_B vs OL
test_c_center_ol = enrichment_test('CENTER_AZC', 'CENTER_B', 'OL',
                                    azc_zone_words, b_layer_words['CENTER_B'],
                                    b_layer_words['OL'])

print(f"\n  Enrichment: AZC zone vocabulary at target vs other B layer")
print(f"  {'AZC zone':<12} {'Target':<12} {'Other':<12} {'Tgt rate':>9} {'Oth rate':>9} {'Lift':>6}")
print(f"  {'-'*65}")

tests = [
    ('S_SERIES', 'FL_BOOKEND', 'CENTER_B', test_s_fl),
    ('S_SERIES', 'OL', 'CENTER_B', test_s_ol),
    ('R_SERIES', 'OL', 'CENTER_B', test_r_ol),
    ('R_SERIES', 'OR', 'CENTER_B', test_r_or),
    ('CENTER_AZC', 'CENTER_B', 'FL_BOOKEND', test_c_center),
    ('CENTER_AZC', 'CENTER_B', 'OL', test_c_center_ol),
]

for az, target, other, result in tests:
    if result:
        print(f"  {az:<12} {target:<12} {other:<12} "
              f"{result['target_rate']:>8.1%} {result['other_rate']:>8.1%} "
              f"{result['lift']:>5.2f}x")

# ============================================================
# TEST 6: R-SERIES SUBSCRIPT ORDERING vs B NESTING DEPTH
# ============================================================
print(f"\n{'=' * 70}")
print("TEST 6: R-SERIES SUBSCRIPTS vs B LAYER DEPTH")
print("=" * 70)

# For Zodiac folios: R1 (outer) -> R2 (middle) -> R3 (inner)
# Does this correspond to OL (inner-left) -> CENTER -> OR (inner-right)?

r_sub_words = defaultdict(Counter)
r_sub_prefixes = defaultdict(Counter)
for t in tx.azc():
    p = t.placement.strip()
    if p in ('R1', 'R2', 'R3'):
        m = morph.extract(t.word)
        prefix = m.prefix if m and m.prefix else 'NONE'
        r_sub_words[p][t.word] += 1
        r_sub_prefixes[p][prefix] += 1

print(f"\n  R-subscript prefix profiles:")
print(f"  {'Ring':<6} {'n':>5}", end='')
for p in top_pfx:
    print(f" {p:>5}", end='')
print()
print(f"  {'-'*55}")
for ring in ['R1', 'R2', 'R3']:
    total = sum(r_sub_prefixes[ring].values())
    if total == 0:
        continue
    print(f"  {ring:<6} {total:>5}", end='')
    for p in top_pfx:
        pct = r_sub_prefixes[ring].get(p, 0) / total * 100
        print(f" {pct:>4.1f}%", end='')
    print()

# Compare R1/R2/R3 to OL/CENTER/OR
print(f"\n  R-subscript -> B layer cosine similarity:")
print(f"  {'Ring':<6}", end='')
for bl in ['OL', 'CENTER_B', 'OR']:
    print(f" {bl:>10}", end='')
print()
for ring in ['R1', 'R2', 'R3']:
    print(f"  {ring:<6}", end='')
    for bl in ['OL', 'CENTER_B', 'OR']:
        cos = prefix_cosine(r_sub_prefixes[ring], b_layer_prefixes[bl], top_pfx)
        print(f" {cos:>9.3f}", end='')
    print()

# ============================================================
# VERDICT
# ============================================================
print(f"\n{'=' * 70}")
print("VERDICT")
print("=" * 70)

# Check the hypothesis
# 1. Does S_SERIES map best to FL_BOOKEND or OL?
s_best_word = max(b_layers, key=lambda bl: overlap_matrix['S_SERIES'][bl])
s_best_pfx = max(b_layers, key=lambda bl: pfx_cosine_matrix['S_SERIES'][bl])

# 2. Does R_SERIES map best to OL or OR?
r_best_word = max(b_layers, key=lambda bl: overlap_matrix['R_SERIES'][bl])
r_best_pfx = max(b_layers, key=lambda bl: pfx_cosine_matrix['R_SERIES'][bl])

# 3. Does CENTER_AZC map best to CENTER_B?
c_best_word = max(b_layers, key=lambda bl: overlap_matrix['CENTER_AZC'][bl])
c_best_pfx = max(b_layers, key=lambda bl: pfx_cosine_matrix['CENTER_AZC'][bl])

print(f"\n  Best-match mapping (word overlap):")
print(f"    S_SERIES   -> {s_best_word}")
print(f"    R_SERIES   -> {r_best_word}")
print(f"    CENTER_AZC -> {c_best_word}")

print(f"\n  Best-match mapping (prefix profile):")
print(f"    S_SERIES   -> {s_best_pfx}")
print(f"    R_SERIES   -> {r_best_pfx}")
print(f"    CENTER_AZC -> {c_best_pfx}")

# Score correspondence
checks = {
    's_maps_to_boundary': s_best_word in ('FL_BOOKEND', 'OL') or s_best_pfx in ('FL_BOOKEND', 'OL'),
    'r_maps_to_frame': r_best_word in ('OL', 'OR') or r_best_pfx in ('OL', 'OR'),
    'c_maps_to_center': c_best_word == 'CENTER_B' or c_best_pfx == 'CENTER_B',
    's_enriched_at_boundary': (test_s_fl and test_s_fl['lift'] > 1.1) or (test_s_ol and test_s_ol['lift'] > 1.1),
    'c_enriched_at_center': test_c_center is not None and test_c_center['lift'] > 1.1,
}

n_pass = sum(checks.values())

print(f"\n  Correspondence checks ({n_pass}/5):")
for name, val in checks.items():
    print(f"    {name:>30}: {'YES' if val else 'NO'}")

if n_pass >= 4:
    verdict = "SPATIAL_NESTING_CORRESPONDENCE"
    explanation = "AZC spatial positions correspond to B nesting layers - same architecture, different medium"
elif n_pass >= 3:
    verdict = "PARTIAL_CORRESPONDENCE"
    explanation = "Some AZC-B nesting alignment but not a clean mapping"
elif n_pass >= 2:
    verdict = "WEAK_SIGNAL"
    explanation = "Marginal correspondence, may be driven by shared vocabulary"
else:
    verdict = "NO_CORRESPONDENCE"
    explanation = "AZC spatial structure does not map onto B nesting layers"

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

# ============================================================
# SAVE
# ============================================================
result = {
    'word_overlap': {
        az: {bl: round(float(overlap_matrix[az][bl]), 4) for bl in b_layers}
        for az in azc_zones
    },
    'prefix_cosine': {
        az: {bl: round(float(pfx_cosine_matrix[az][bl]), 4) for bl in b_layers}
        for az in azc_zones
    },
    'role_cosine': {
        az: {bl: round(float(role_cosine_matrix[az][bl]), 4) for bl in b_layers}
        for az in azc_zones
    },
    'enrichment': {
        's_at_fl': {'lift': round(float(test_s_fl['lift']), 3)} if test_s_fl else None,
        's_at_ol': {'lift': round(float(test_s_ol['lift']), 3)} if test_s_ol else None,
        'r_at_ol': {'lift': round(float(test_r_ol['lift']), 3)} if test_r_ol else None,
        'r_at_or': {'lift': round(float(test_r_or['lift']), 3)} if test_r_or else None,
        'c_at_center': {'lift': round(float(test_c_center['lift']), 3)} if test_c_center else None,
    },
    'checks': {k: bool(v) for k, v in checks.items()},
    'n_pass': int(n_pass),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "35_azc_nesting_correspondence.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
