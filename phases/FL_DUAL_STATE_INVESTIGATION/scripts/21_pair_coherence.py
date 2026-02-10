"""
21_pair_coherence.py

Do lines sharing the same FL pair have more similar gap content than
lines with different pairs? If FL pairs are lookup coordinates, then
same-pair lines across different folios should be doing similar things.

Tests:
1. Within-pair vs between-pair gap word similarity
2. Within-pair vs between-pair gap role similarity
3. Most distinctive words per pair (TF-IDF style)
4. Can we characterize what each pair "does"?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
import random

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import mannwhitneyu

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

tx = Transcript()
morph = Morphology()
MIN_N = 50

# Load role map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']

# Collect by line
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
# Build line profiles with pairs and gap content
# ============================================================
line_profiles = []

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
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

        role = token_to_role.get(t.word, 'UNKNOWN')
        entry = {'word': t.word, 'pos': pos, 'is_fl': is_fl,
                 'mode': mode, 'stage': stage, 'role': role}
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

    # Gap tokens
    max_low = max(f['pos'] for f in low_fls)
    min_high = min(f['pos'] for f in high_fls)
    gap = [t for t in all_info if not t['is_fl'] and t['pos'] > max_low and t['pos'] < min_high]

    gap_words = Counter(t['word'] for t in gap)
    gap_roles = Counter(t['role'] for t in gap)

    line_profiles.append({
        'key': line_key,
        'folio': line_key[0],
        'pair': pair,
        'gap_words': gap_words,
        'gap_roles': gap_roles,
        'n_gap': len(gap),
    })

print(f"Lines with pairs: {len(line_profiles)}")

# Group by pair
pair_groups = defaultdict(list)
for lp in line_profiles:
    pair_groups[lp['pair']].append(lp)

# ============================================================
# TEST 1: Within-pair vs between-pair word similarity
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: WITHIN-PAIR vs BETWEEN-PAIR GAP WORD SIMILARITY")
print(f"{'='*60}")

def jaccard_words(a, b):
    """Jaccard similarity between two word Counters."""
    set_a = set(a.keys())
    set_b = set(b.keys())
    if not set_a and not set_b:
        return 0.0
    inter = set_a & set_b
    union = set_a | set_b
    return len(inter) / len(union)

def cosine_words(a, b):
    """Cosine similarity between two word Counters."""
    all_words = set(a.keys()) | set(b.keys())
    if not all_words:
        return 0.0
    vec_a = np.array([a.get(w, 0) for w in all_words])
    vec_b = np.array([b.get(w, 0) for w in all_words])
    dot = np.dot(vec_a, vec_b)
    norm = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    return dot / norm if norm > 0 else 0.0

# Sample within-pair similarities (same pair, different folios)
random.seed(42)
within_pair_jaccard = []
within_pair_cosine = []

for pair, lines in pair_groups.items():
    if len(lines) < 10:
        continue
    # Sample pairs from DIFFERENT folios
    folio_groups = defaultdict(list)
    for lp in lines:
        folio_groups[lp['folio']].append(lp)
    folios_with_lines = [f for f, ls in folio_groups.items() if ls]
    if len(folios_with_lines) < 2:
        continue

    # Sample up to 50 cross-folio pairs
    cross_folio_pairs = []
    for i, f1 in enumerate(folios_with_lines):
        for f2 in folios_with_lines[i+1:]:
            for l1 in folio_groups[f1][:3]:
                for l2 in folio_groups[f2][:3]:
                    cross_folio_pairs.append((l1, l2))
    random.shuffle(cross_folio_pairs)
    for l1, l2 in cross_folio_pairs[:50]:
        if l1['n_gap'] >= 2 and l2['n_gap'] >= 2:
            within_pair_jaccard.append(jaccard_words(l1['gap_words'], l2['gap_words']))
            within_pair_cosine.append(cosine_words(l1['gap_words'], l2['gap_words']))

# Sample between-pair similarities (different pair, different folios)
between_pair_jaccard = []
between_pair_cosine = []

all_pairs_with_data = [p for p, ls in pair_groups.items() if len(ls) >= 10]
for _ in range(len(within_pair_jaccard)):
    p1, p2 = random.sample(all_pairs_with_data, 2)
    l1 = random.choice(pair_groups[p1])
    l2 = random.choice(pair_groups[p2])
    if l1['n_gap'] >= 2 and l2['n_gap'] >= 2:
        between_pair_jaccard.append(jaccard_words(l1['gap_words'], l2['gap_words']))
        between_pair_cosine.append(cosine_words(l1['gap_words'], l2['gap_words']))

print(f"\nWithin-pair (same pair, different folios):")
print(f"  n={len(within_pair_jaccard)}")
print(f"  Jaccard: mean={np.mean(within_pair_jaccard):.3f}, median={np.median(within_pair_jaccard):.3f}")
print(f"  Cosine:  mean={np.mean(within_pair_cosine):.3f}, median={np.median(within_pair_cosine):.3f}")

print(f"\nBetween-pair (different pairs):")
print(f"  n={len(between_pair_jaccard)}")
print(f"  Jaccard: mean={np.mean(between_pair_jaccard):.3f}, median={np.median(between_pair_jaccard):.3f}")
print(f"  Cosine:  mean={np.mean(between_pair_cosine):.3f}, median={np.median(between_pair_cosine):.3f}")

if within_pair_jaccard and between_pair_jaccard:
    stat_j, p_j = mannwhitneyu(within_pair_jaccard, between_pair_jaccard, alternative='greater')
    stat_c, p_c = mannwhitneyu(within_pair_cosine, between_pair_cosine, alternative='greater')
    print(f"\n  Within > Between (Jaccard): U={stat_j:.0f}, p={p_j:.4f}")
    print(f"  Within > Between (Cosine):  U={stat_c:.0f}, p={p_c:.4f}")

    jaccard_lift = np.mean(within_pair_jaccard) / np.mean(between_pair_jaccard) if np.mean(between_pair_jaccard) > 0 else float('inf')
    cosine_lift = np.mean(within_pair_cosine) / np.mean(between_pair_cosine) if np.mean(between_pair_cosine) > 0 else float('inf')
    print(f"  Jaccard lift: {jaccard_lift:.2f}x")
    print(f"  Cosine lift: {cosine_lift:.2f}x")

# ============================================================
# TEST 2: Within-pair vs between-pair ROLE similarity
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: WITHIN-PAIR vs BETWEEN-PAIR ROLE DISTRIBUTION")
print(f"{'='*60}")

def role_vector(gap_roles):
    roles = ['ENERGY_OPERATOR', 'UNKNOWN', 'AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL']
    total = sum(gap_roles.values())
    if total == 0:
        return np.zeros(len(roles))
    return np.array([gap_roles.get(r, 0) / total for r in roles])

within_role_cos = []
between_role_cos = []

for pair, lines in pair_groups.items():
    if len(lines) < 10:
        continue
    folio_groups = defaultdict(list)
    for lp in lines:
        folio_groups[lp['folio']].append(lp)
    folios = [f for f, ls in folio_groups.items() if ls]
    if len(folios) < 2:
        continue
    cross = []
    for i, f1 in enumerate(folios):
        for f2 in folios[i+1:]:
            for l1 in folio_groups[f1][:3]:
                for l2 in folio_groups[f2][:3]:
                    cross.append((l1, l2))
    random.shuffle(cross)
    for l1, l2 in cross[:50]:
        if l1['n_gap'] >= 2 and l2['n_gap'] >= 2:
            v1 = role_vector(l1['gap_roles'])
            v2 = role_vector(l2['gap_roles'])
            dot = np.dot(v1, v2)
            norm = np.linalg.norm(v1) * np.linalg.norm(v2)
            if norm > 0:
                within_role_cos.append(dot / norm)

for _ in range(len(within_role_cos)):
    p1, p2 = random.sample(all_pairs_with_data, 2)
    l1 = random.choice(pair_groups[p1])
    l2 = random.choice(pair_groups[p2])
    if l1['n_gap'] >= 2 and l2['n_gap'] >= 2:
        v1 = role_vector(l1['gap_roles'])
        v2 = role_vector(l2['gap_roles'])
        dot = np.dot(v1, v2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        if norm > 0:
            between_role_cos.append(dot / norm)

print(f"  Within-pair role cosine:  mean={np.mean(within_role_cos):.3f} (n={len(within_role_cos)})")
print(f"  Between-pair role cosine: mean={np.mean(between_role_cos):.3f} (n={len(between_role_cos)})")

if within_role_cos and between_role_cos:
    stat, p = mannwhitneyu(within_role_cos, between_role_cos, alternative='greater')
    print(f"  Within > Between: U={stat:.0f}, p={p:.4f}")

# ============================================================
# TEST 3: Distinctive words per pair (TF-IDF style)
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: DISTINCTIVE GAP WORDS PER PAIR")
print(f"{'='*60}")

# Global word frequencies
global_words = Counter()
for lp in line_profiles:
    global_words += lp['gap_words']
global_total = sum(global_words.values())

# Per-pair TF-IDF: words that are overrepresented in this pair vs global
for pair in sorted(pair_groups.keys(), key=lambda p: (STAGE_ORDER[p[0]], STAGE_ORDER[p[1]])):
    lines = pair_groups[pair]
    if len(lines) < 15:
        continue

    pair_words = Counter()
    for lp in lines:
        pair_words += lp['gap_words']
    pair_total = sum(pair_words.values())
    if pair_total < 30:
        continue

    # Compute enrichment: (pair_freq / global_freq)
    enriched = []
    for word, count in pair_words.items():
        if count < 3:
            continue
        pair_freq = count / pair_total
        global_freq = global_words.get(word, 1) / global_total
        enrichment = pair_freq / global_freq
        if enrichment > 1.5:
            enriched.append((word, count, round(enrichment, 2)))

    enriched.sort(key=lambda x: -x[2])
    top = enriched[:6]
    if top:
        pair_label = f"{pair[0][:4]}>{pair[1][:4]}"
        words_str = ', '.join(f"{w}({e:.1f}x)" for w, c, e in top)
        print(f"  {pair_label:>12} (n={len(lines):>3}): {words_str}")

# ============================================================
# TEST 4: Same-folio vs cross-folio within-pair similarity
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: SAME-FOLIO vs CROSS-FOLIO WITHIN-PAIR SIMILARITY")
print(f"{'='*60}")

# Are same-pair lines from the SAME folio more similar than same-pair from DIFFERENT folios?
same_folio_within = []
cross_folio_within = []

for pair, lines in pair_groups.items():
    if len(lines) < 10:
        continue
    folio_groups = defaultdict(list)
    for lp in lines:
        folio_groups[lp['folio']].append(lp)

    # Same-folio pairs
    for folio, flines in folio_groups.items():
        if len(flines) >= 2:
            for i in range(min(len(flines), 5)):
                for j in range(i+1, min(len(flines), 5)):
                    if flines[i]['n_gap'] >= 2 and flines[j]['n_gap'] >= 2:
                        same_folio_within.append(
                            jaccard_words(flines[i]['gap_words'], flines[j]['gap_words']))

    # Cross-folio pairs (already computed above, reuse logic)
    folios = list(folio_groups.keys())
    for i in range(min(len(folios), 5)):
        for j in range(i+1, min(len(folios), 5)):
            f1_lines = folio_groups[folios[i]]
            f2_lines = folio_groups[folios[j]]
            l1 = f1_lines[0]
            l2 = f2_lines[0]
            if l1['n_gap'] >= 2 and l2['n_gap'] >= 2:
                cross_folio_within.append(
                    jaccard_words(l1['gap_words'], l2['gap_words']))

if same_folio_within and cross_folio_within:
    print(f"  Same-folio, same-pair Jaccard:  mean={np.mean(same_folio_within):.3f} (n={len(same_folio_within)})")
    print(f"  Cross-folio, same-pair Jaccard: mean={np.mean(cross_folio_within):.3f} (n={len(cross_folio_within)})")
    stat, p = mannwhitneyu(same_folio_within, cross_folio_within, alternative='greater')
    print(f"  Same-folio > Cross-folio: U={stat:.0f}, p={p:.4f}")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")

within_greater = False
meaningful_lift = False
role_similar = False

if within_pair_jaccard and between_pair_jaccard and p_j < 0.01:
    within_greater = True
if jaccard_lift > 1.1:
    meaningful_lift = True
if within_role_cos and between_role_cos and np.mean(within_role_cos) > np.mean(between_role_cos) + 0.02:
    role_similar = True

if within_greater and meaningful_lift:
    verdict = "PAIR_DEFINES_CONTENT"
    explanation = (f"Same-pair lines have significantly more similar gap content "
                   f"(Jaccard lift {jaccard_lift:.2f}x, Cosine lift {cosine_lift:.2f}x)")
elif within_greater:
    verdict = "WEAK_PAIR_COHERENCE"
    explanation = "Statistically significant but small effect"
else:
    verdict = "NO_PAIR_COHERENCE"
    explanation = "Same-pair lines are no more similar than random pairs"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# ============================================================
# Save
# ============================================================
result = {
    'n_lines': len(line_profiles),
    'within_pair_jaccard': round(float(np.mean(within_pair_jaccard)), 4),
    'between_pair_jaccard': round(float(np.mean(between_pair_jaccard)), 4),
    'within_pair_cosine': round(float(np.mean(within_pair_cosine)), 4),
    'between_pair_cosine': round(float(np.mean(between_pair_cosine)), 4),
    'jaccard_lift': round(float(jaccard_lift), 3),
    'cosine_lift': round(float(cosine_lift), 3),
    'jaccard_p': float(p_j),
    'cosine_p': float(p_c),
    'within_role_cosine': round(float(np.mean(within_role_cos)), 4),
    'between_role_cosine': round(float(np.mean(between_role_cos)), 4),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "21_pair_coherence.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
