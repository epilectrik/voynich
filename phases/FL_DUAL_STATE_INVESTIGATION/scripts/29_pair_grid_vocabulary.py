"""
29_pair_grid_vocabulary.py

Does the FL pair grid carve up vocabulary in a way consistent
with different material conditions?

If FL pairs are real state tags:
  1. Nearby pairs should share more vocabulary than distant pairs
  2. The LOW and HIGH dimensions should independently contribute
  3. Distinctive words per pair should cluster into coherent groups
  4. The pair grid should show gradient structure, not random scatter
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr
from scipy.spatial.distance import pdist, squareform

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
STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}
STAGES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']

tx = Transcript()
morph = Morphology()
MIN_N = 50

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']
token_to_role = class_data['token_to_role']

line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

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

# ============================================================
# Build pair -> gap vocabulary
# ============================================================
pair_gap_words = defaultdict(Counter)
pair_gap_roles = defaultdict(Counter)
pair_gap_prefixes = defaultdict(Counter)
pair_gap_classes = defaultdict(Counter)
pair_line_count = Counter()

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    fl_info = []
    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        stage = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]

        cls = token_to_class.get(t.word, None)
        role = token_to_role.get(t.word, 'UNKNOWN')
        prefix = m.prefix if m and m.prefix else 'NONE'
        entry = {'word': t.word, 'idx': idx, 'is_fl': is_fl,
                 'mode': mode, 'stage': stage, 'class': cls,
                 'role': role, 'prefix': prefix}
        all_info.append(entry)
        if is_fl and mode:
            fl_info.append(entry)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    pair = (low_stage, high_stage)

    # Gap tokens (non-FL between LOW and HIGH)
    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)
    gap = [t for t in all_info if not t['is_fl']
           and t['idx'] > max_low_idx and t['idx'] < min_high_idx]

    if len(gap) < 2:
        continue

    pair_line_count[pair] += 1
    for t in gap:
        pair_gap_words[pair][t['word']] += 1
        pair_gap_roles[pair][t['role']] += 1
        pair_gap_prefixes[pair][t['prefix']] += 1
        if t['class']:
            pair_gap_classes[pair][t['class']] += 1

# Filter to pairs with enough data
MIN_LINES = 20
common_pairs = [p for p in pair_line_count if pair_line_count[p] >= MIN_LINES]
common_pairs.sort(key=lambda p: (STAGE_ORDER[p[0]], STAGE_ORDER[p[1]]))

print(f"Common FL pairs (n>={MIN_LINES}): {len(common_pairs)}")
for p in common_pairs:
    n_words = sum(pair_gap_words[p].values())
    print(f"  {p[0][:4]}>{p[1][:4]}: {pair_line_count[p]} lines, {n_words} gap tokens")

# ============================================================
# TEST 1: Distance in pair space predicts vocabulary distance
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: PAIR DISTANCE vs VOCABULARY DISTANCE")
print(f"{'='*60}")

# Pair distance = |LOW_stage_diff| + |HIGH_stage_diff| (Manhattan)
# Vocabulary distance = 1 - Jaccard(word sets)
# Also cosine distance on word frequency vectors

# Build word frequency vectors
all_words = set()
for p in common_pairs:
    all_words.update(pair_gap_words[p].keys())
all_words = sorted(all_words)
word_idx = {w: i for i, w in enumerate(all_words)}

pair_vectors = {}
pair_word_sets = {}
for p in common_pairs:
    vec = np.zeros(len(all_words))
    for w, c in pair_gap_words[p].items():
        vec[word_idx[w]] = c
    # Normalize to proportions
    total = vec.sum()
    if total > 0:
        vec = vec / total
    pair_vectors[p] = vec
    pair_word_sets[p] = set(pair_gap_words[p].keys())

# Compute pairwise distances
n_pairs = len(common_pairs)
stage_distances = []
jaccard_distances = []
cosine_distances = []

for i in range(n_pairs):
    for j in range(i + 1, n_pairs):
        p1, p2 = common_pairs[i], common_pairs[j]

        # Stage distance (Manhattan on the grid)
        sd = abs(STAGE_ORDER[p1[0]] - STAGE_ORDER[p2[0]]) + abs(STAGE_ORDER[p1[1]] - STAGE_ORDER[p2[1]])
        stage_distances.append(sd)

        # Jaccard distance
        inter = len(pair_word_sets[p1] & pair_word_sets[p2])
        union = len(pair_word_sets[p1] | pair_word_sets[p2])
        jd = 1 - (inter / union) if union > 0 else 1
        jaccard_distances.append(jd)

        # Cosine distance
        v1, v2 = pair_vectors[p1], pair_vectors[p2]
        dot = np.dot(v1, v2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        cd = 1 - (dot / norm) if norm > 0 else 1
        cosine_distances.append(cd)

# Correlation
rho_jaccard, p_jaccard = spearmanr(stage_distances, jaccard_distances)
rho_cosine, p_cosine = spearmanr(stage_distances, cosine_distances)

print(f"  Stage distance vs Jaccard distance: rho={rho_jaccard:.3f} (p={p_jaccard:.4f})")
print(f"  Stage distance vs Cosine distance:  rho={rho_cosine:.3f} (p={p_cosine:.4f})")

if rho_jaccard > 0 and p_jaccard < 0.05:
    print("  -> Nearby pairs share more vocabulary (gradient exists)")
elif rho_jaccard < 0 and p_jaccard < 0.05:
    print("  -> Distant pairs share MORE vocabulary (anti-gradient)")
else:
    print("  -> No significant relationship between pair distance and vocabulary")

# ============================================================
# TEST 2: LOW and HIGH dimensions independently contribute
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: INDEPENDENT CONTRIBUTION OF LOW AND HIGH")
print(f"{'='*60}")

# Hold LOW constant, vary HIGH -> how much does vocabulary change?
# Hold HIGH constant, vary LOW -> how much does vocabulary change?

low_groups = defaultdict(list)
high_groups = defaultdict(list)
for p in common_pairs:
    low_groups[p[0]].append(p)
    high_groups[p[1]].append(p)

# Within same LOW: how similar are vocabularies?
same_low_cosines = []
diff_low_cosines = []
same_high_cosines = []
diff_high_cosines = []

for i in range(n_pairs):
    for j in range(i + 1, n_pairs):
        p1, p2 = common_pairs[i], common_pairs[j]
        v1, v2 = pair_vectors[p1], pair_vectors[p2]
        dot = np.dot(v1, v2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        cos_sim = dot / norm if norm > 0 else 0

        if p1[0] == p2[0]:  # Same LOW
            same_low_cosines.append(cos_sim)
        else:
            diff_low_cosines.append(cos_sim)

        if p1[1] == p2[1]:  # Same HIGH
            same_high_cosines.append(cos_sim)
        else:
            diff_high_cosines.append(cos_sim)

print(f"  Same LOW stage:  mean cosine = {np.mean(same_low_cosines):.4f} (n={len(same_low_cosines)})")
print(f"  Diff LOW stage:  mean cosine = {np.mean(diff_low_cosines):.4f} (n={len(diff_low_cosines)})")
low_lift = np.mean(same_low_cosines) / np.mean(diff_low_cosines) if np.mean(diff_low_cosines) > 0 else 0
print(f"  LOW-matching lift: {low_lift:.3f}x")

print(f"\n  Same HIGH stage: mean cosine = {np.mean(same_high_cosines):.4f} (n={len(same_high_cosines)})")
print(f"  Diff HIGH stage: mean cosine = {np.mean(diff_high_cosines):.4f} (n={len(diff_high_cosines)})")
high_lift = np.mean(same_high_cosines) / np.mean(diff_high_cosines) if np.mean(diff_high_cosines) > 0 else 0
print(f"  HIGH-matching lift: {high_lift:.3f}x")

# ============================================================
# TEST 3: Role profiles across the pair grid
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: ROLE PROFILES ACROSS THE PAIR GRID")
print(f"{'='*60}")

roles = ['ENERGY_OPERATOR', 'UNKNOWN', 'AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL']
role_short = {'ENERGY_OPERATOR': 'EN', 'UNKNOWN': 'UK', 'AUXILIARY': 'AX',
              'FREQUENT_OPERATOR': 'FQ', 'CORE_CONTROL': 'CC'}

print(f"\n  {'Pair':>12} {'n':>5}  {'EN%':>5} {'UK%':>5} {'AX%':>5} {'FQ%':>5} {'CC%':>5}")
print(f"  {'-'*50}")

pair_role_profiles = {}
for p in common_pairs:
    total = sum(pair_gap_roles[p].values())
    profile = {}
    label = f"{p[0][:4]}>{p[1][:4]}"
    parts = []
    for r in roles:
        pct = pair_gap_roles[p].get(r, 0) / total * 100
        profile[r] = pct
        parts.append(f"{pct:>5.1f}")
    pair_role_profiles[p] = profile
    print(f"  {label:>12} {total:>5}  {'  '.join(parts)}")

# Do role profiles correlate with stage position?
# For each role: does its percentage change with LOW or HIGH stage?
print(f"\n  Role correlations with stage dimensions:")
for r in roles:
    low_stages = [STAGE_ORDER[p[0]] for p in common_pairs]
    high_stages = [STAGE_ORDER[p[1]] for p in common_pairs]
    role_pcts = [pair_role_profiles[p][r] for p in common_pairs]

    rho_low, p_low = spearmanr(low_stages, role_pcts)
    rho_high, p_high = spearmanr(high_stages, role_pcts)

    sig_low = '*' if p_low < 0.05 else ''
    sig_high = '*' if p_high < 0.05 else ''

    print(f"    {r:>20}: LOW rho={rho_low:>+.3f}{sig_low:1}  HIGH rho={rho_high:>+.3f}{sig_high:1}")

# ============================================================
# TEST 4: Prefix profiles across the pair grid
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: PREFIX PROFILES ACROSS THE PAIR GRID")
print(f"{'='*60}")

top_pfx = ['ch', 'sh', 'qo', 'NONE', 'ok', 'ot']

print(f"\n  {'Pair':>12} {'n':>5}", end='')
for p in top_pfx:
    print(f" {p:>6}", end='')
print()
print(f"  {'-'*55}")

pair_pfx_profiles = {}
for pair in common_pairs:
    total = sum(pair_gap_prefixes[pair].values())
    profile = {}
    label = f"{pair[0][:4]}>{pair[1][:4]}"
    print(f"  {label:>12} {total:>5}", end='')
    for p in top_pfx:
        pct = pair_gap_prefixes[pair].get(p, 0) / total * 100
        profile[p] = pct
        print(f" {pct:>5.1f}%", end='')
    print()
    pair_pfx_profiles[pair] = profile

# PREFIX correlations with stage dimensions
print(f"\n  Prefix correlations with stage dimensions:")
for pfx in top_pfx:
    low_stages = [STAGE_ORDER[p[0]] for p in common_pairs]
    high_stages = [STAGE_ORDER[p[1]] for p in common_pairs]
    pfx_pcts = [pair_pfx_profiles[p][pfx] for p in common_pairs]

    rho_low, p_low = spearmanr(low_stages, pfx_pcts)
    rho_high, p_high = spearmanr(high_stages, pfx_pcts)

    sig_low = '*' if p_low < 0.05 else ''
    sig_high = '*' if p_high < 0.05 else ''

    print(f"    {pfx:>8}: LOW rho={rho_low:>+.3f}{sig_low:1}  HIGH rho={rho_high:>+.3f}{sig_high:1}")

# ============================================================
# TEST 5: Distinctive words per pair (enrichment analysis)
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: DISTINCTIVE WORDS PER PAIR")
print(f"{'='*60}")

# For each pair, find words enriched vs corpus baseline
total_words = Counter()
for p in common_pairs:
    total_words += pair_gap_words[p]
total_count = sum(total_words.values())

for pair in common_pairs:
    pair_total = sum(pair_gap_words[pair].values())
    if pair_total < 30:
        continue

    enriched = []
    for w, count in pair_gap_words[pair].items():
        if count < 3:
            continue
        pair_pct = count / pair_total
        baseline_pct = total_words[w] / total_count
        if baseline_pct > 0:
            enrichment = pair_pct / baseline_pct
            if enrichment > 2.0:
                enriched.append((w, count, enrichment, pair_pct * 100))

    enriched.sort(key=lambda x: -x[2])
    label = f"{pair[0][:4]}>{pair[1][:4]}"
    if enriched:
        top4 = enriched[:4]
        words_str = ', '.join(f"{w}({e:.1f}x)" for w, c, e, p in top4)
        print(f"  {label:>12} (n={pair_total:>3}): {words_str}")
    else:
        print(f"  {label:>12} (n={pair_total:>3}): no enriched words")

# ============================================================
# TEST 6: Grid coherence - are adjacent cells more similar?
# ============================================================
print(f"\n{'='*60}")
print("TEST 6: GRID COHERENCE (adjacent vs non-adjacent)")
print(f"{'='*60}")

adjacent_cosines = []
nonadjacent_cosines = []

for i in range(n_pairs):
    for j in range(i + 1, n_pairs):
        p1, p2 = common_pairs[i], common_pairs[j]
        v1, v2 = pair_vectors[p1], pair_vectors[p2]
        dot = np.dot(v1, v2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        cos_sim = dot / norm if norm > 0 else 0

        sd = abs(STAGE_ORDER[p1[0]] - STAGE_ORDER[p2[0]]) + abs(STAGE_ORDER[p1[1]] - STAGE_ORDER[p2[1]])
        if sd <= 2:
            adjacent_cosines.append(cos_sim)
        else:
            nonadjacent_cosines.append(cos_sim)

if adjacent_cosines and nonadjacent_cosines:
    adj_mean = np.mean(adjacent_cosines)
    nonadj_mean = np.mean(nonadjacent_cosines)
    grid_lift = adj_mean / nonadj_mean if nonadj_mean > 0 else 0
    print(f"  Adjacent pairs (distance<=2): mean cosine = {adj_mean:.4f} (n={len(adjacent_cosines)})")
    print(f"  Non-adjacent pairs (distance>2): mean cosine = {nonadj_mean:.4f} (n={len(nonadjacent_cosines)})")
    print(f"  Grid coherence lift: {grid_lift:.3f}x")
else:
    grid_lift = 0

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")
print("VERDICT")
print(f"{'='*60}")

gradient_exists = rho_cosine > 0.15 and p_cosine < 0.1
low_contributes = low_lift > 1.05
high_contributes = high_lift > 1.05
grid_coherent = grid_lift > 1.05
has_distinctive_vocab = True  # We printed it above

checks = {
    'gradient_exists': gradient_exists,
    'low_dim_contributes': low_contributes,
    'high_dim_contributes': high_contributes,
    'grid_coherent': grid_coherent,
}
n_pass = sum(checks.values())

print(f"  Checks ({n_pass}/4):")
for name, val in checks.items():
    print(f"    {name:>25}: {'YES' if val else 'NO'}")

if n_pass >= 3:
    verdict = "MATERIAL_STATE_GRID"
    explanation = ("FL pair grid carves vocabulary along a gradient: "
                   "nearby states share more operations")
elif n_pass >= 2:
    verdict = "PARTIAL_GRID"
    explanation = "Some grid structure but not fully coherent"
elif n_pass >= 1:
    verdict = "WEAK_SIGNAL"
    explanation = "Minimal grid structure in vocabulary space"
else:
    verdict = "NO_GRID"
    explanation = "FL pairs do not carve vocabulary into a coherent state space"

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

print(f"\n  Stage distance vs cosine distance: rho={rho_cosine:.3f} (p={p_cosine:.4f})")
print(f"  LOW-matching lift: {low_lift:.3f}x")
print(f"  HIGH-matching lift: {high_lift:.3f}x")
print(f"  Grid coherence lift: {grid_lift:.3f}x")

# Save
result = {
    'n_common_pairs': len(common_pairs),
    'stage_vs_cosine_rho': round(float(rho_cosine), 3),
    'stage_vs_cosine_p': round(float(p_cosine), 4),
    'stage_vs_jaccard_rho': round(float(rho_jaccard), 3),
    'stage_vs_jaccard_p': round(float(p_jaccard), 4),
    'low_matching_lift': round(float(low_lift), 3),
    'high_matching_lift': round(float(high_lift), 3),
    'grid_coherence_lift': round(float(grid_lift), 3),
    'checks': {k: bool(v) for k, v in checks.items()},
    'n_pass': int(n_pass),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "29_pair_grid_vocabulary.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
