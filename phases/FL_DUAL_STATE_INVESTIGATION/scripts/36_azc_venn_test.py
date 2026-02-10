"""
36_azc_venn_test.py

Two-wheel Venn hypothesis: two AZC diagrams describe the two halves
of a B line, overlapping at the center.

    Wheel 1 (LEFT):  S -> R1 -> R2 -> R3 -> C  (= FL-LOW -> OL -> left-CENTER)
    Wheel 2 (RIGHT): C -> R3 -> R2 -> R1 -> S  (= right-CENTER -> OR -> FL-HIGH)
    Venn overlap at C = shared CENTER content

Predictions:
  1. S-subscripts should show LEFT/RIGHT asymmetry (S1 maps to one side, S2 to other)
  2. R1 (outermost) vocabulary should be more edge-biased than R3 (innermost)
  3. C vocabulary should be position-symmetric (shared center)
  4. AZC subscript vocabulary should systematically shift from LEFT to RIGHT
     as you move from one subscript to another
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr, mannwhitneyu

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
token_to_role = class_data['token_to_role']

# ============================================================
# Build B line left/right vocabularies
# ============================================================
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

# For each B line, split into left half and right half
# LEFT = everything at or before midpoint
# RIGHT = everything after midpoint
# Also track: FL-LOW side (FL tokens + tokens closer to FL-LOW)
#             FL-HIGH side (FL tokens + tokens closer to FL-HIGH)

b_left_words = Counter()    # left half of line
b_right_words = Counter()   # right half of line
b_fl_low_side = Counter()   # FL-LOW bookend + OL + left gap
b_fl_high_side = Counter()  # right gap + OR + FL-HIGH bookend

# More granular: position bins (quintiles)
b_position_words = defaultdict(Counter)  # quintile (0-4) -> word counter

# For each word, track its mean B-line position
word_positions = defaultdict(list)

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    for idx, t in enumerate(tokens):
        pos = idx / (n - 1) if n > 1 else 0.5
        word_positions[t.word].append(pos)

        # Left/right split
        if pos <= 0.5:
            b_left_words[t.word] += 1
        else:
            b_right_words[t.word] += 1

        # Quintile
        quintile = min(int(pos * 5), 4)
        b_position_words[quintile][t.word] += 1

# Compute mean position for each word
word_mean_pos = {}
for w, positions in word_positions.items():
    if len(positions) >= 5:  # minimum occurrences
        word_mean_pos[w] = np.mean(positions)

print(f"Words with mean position: {len(word_mean_pos)}")
print(f"B left tokens: {sum(b_left_words.values())}, B right tokens: {sum(b_right_words.values())}")

# ============================================================
# Build AZC subscript vocabularies
# ============================================================
azc_sub_words = defaultdict(Counter)
azc_sub_prefixes = defaultdict(Counter)

for t in tx.azc():
    p = t.placement.strip()
    if p.startswith('L') or p.startswith('P'):
        continue  # skip labels and paragraphs

    m = morph.extract(t.word)
    prefix = m.prefix if m and m.prefix else 'NONE'

    azc_sub_words[p][t.word] += 1
    azc_sub_prefixes[p][prefix] += 1

print(f"\nAZC placement codes:")
for p in sorted(azc_sub_words.keys()):
    print(f"  {p:>4}: {sum(azc_sub_words[p].values()):>5} tokens, {len(azc_sub_words[p]):>4} types")

# ============================================================
# TEST 1: Mean B-line position of AZC subscript vocabulary
# ============================================================
print(f"\n{'='*70}")
print("TEST 1: MEAN B-LINE POSITION OF AZC SUBSCRIPT VOCABULARY")
print("=" * 70)

# For each AZC placement code, find its vocabulary in B,
# and compute the mean position of those words in B lines.
# If S1 maps to LEFT and S2 maps to RIGHT (or vice versa),
# their mean positions should differ.

print(f"\n  {'Placement':<10} {'nAZC':>5} {'Shared':>7} "
      f"{'MeanBPos':>9} {'MedianBP':>9} {'StdBPos':>8} {'LR_bias':>8}")
print(f"  {'-'*65}")

placement_mean_positions = {}
placements_ordered = ['S0', 'S1', 'S2', 'S3', 'R1', 'R2', 'R3', 'R4', 'C', 'C1', 'C2',
                      'R', 'S', 'X', 'Y', 'O']

for p in placements_ordered:
    if p not in azc_sub_words:
        continue
    azc_vocab = set(azc_sub_words[p].keys())
    # Find these words' positions in B
    shared_positions = []
    for w in azc_vocab:
        if w in word_mean_pos:
            # Weight by how often this word appears in this AZC position
            count = azc_sub_words[p][w]
            shared_positions.extend([word_mean_pos[w]] * count)

    n_azc = sum(azc_sub_words[p].values())
    n_shared = len(set(azc_sub_words[p].keys()) & set(word_mean_pos.keys()))

    if len(shared_positions) >= 10:
        mean_pos = np.mean(shared_positions)
        median_pos = np.median(shared_positions)
        std_pos = np.std(shared_positions)
        lr_bias = "LEFT" if mean_pos < 0.47 else "RIGHT" if mean_pos > 0.53 else "CENTER"
        placement_mean_positions[p] = mean_pos
        print(f"  {p:<10} {n_azc:>5} {n_shared:>7} "
              f"{mean_pos:>9.3f} {median_pos:>9.3f} {std_pos:>8.3f} {lr_bias:>8}")
    else:
        print(f"  {p:<10} {n_azc:>5} {n_shared:>7}       (too few shared words)")

# ============================================================
# TEST 2: S-SUBSCRIPT LEFT/RIGHT ASYMMETRY
# ============================================================
print(f"\n{'='*70}")
print("TEST 2: S-SUBSCRIPT LEFT/RIGHT ASYMMETRY")
print("=" * 70)

# For S1 and S2 vocabulary, compare left-half vs right-half presence in B
for s_code in ['S0', 'S1', 'S2', 'S3', 'S']:
    if s_code not in azc_sub_words:
        continue
    azc_vocab = set(w for w, c in azc_sub_words[s_code].items() if c >= 1)

    left_hits = sum(b_left_words.get(w, 0) for w in azc_vocab)
    right_hits = sum(b_right_words.get(w, 0) for w in azc_vocab)
    total = left_hits + right_hits

    if total > 0:
        left_pct = left_hits / total * 100
        right_pct = right_hits / total * 100
        bias = left_pct - right_pct
        print(f"  {s_code}: left={left_pct:.1f}%, right={right_pct:.1f}%, "
              f"bias={bias:+.1f}pp (n={total})")

# ============================================================
# TEST 3: R-SUBSCRIPT GRADIENT (outer -> inner = edge -> center)
# ============================================================
print(f"\n{'='*70}")
print("TEST 3: R-SUBSCRIPT GRADIENT")
print("=" * 70)

# If outer rings (R1) map to edges and inner rings (R3) map to center,
# R1 vocabulary should have more extreme mean positions (near 0 or 1)
# and R3 vocabulary should have positions clustered near 0.5.

for r_code in ['R1', 'R2', 'R3', 'R4', 'R']:
    if r_code not in azc_sub_words:
        continue
    azc_vocab = set(azc_sub_words[r_code].keys())
    positions = [word_mean_pos[w] for w in azc_vocab if w in word_mean_pos]

    if len(positions) >= 10:
        # Compute "centrality" = how close to 0.5
        centrality = [1 - 2 * abs(p - 0.5) for p in positions]
        mean_centrality = np.mean(centrality)
        # Also compute spread (std of positions)
        mean_pos = np.mean(positions)
        std_pos = np.std(positions)
        print(f"  {r_code}: mean_pos={mean_pos:.3f}, std={std_pos:.3f}, "
              f"centrality={mean_centrality:.3f} (n={len(positions)})")

# ============================================================
# TEST 4: QUINTILE DISTRIBUTION PER AZC PLACEMENT
# ============================================================
print(f"\n{'='*70}")
print("TEST 4: B-LINE QUINTILE DISTRIBUTION OF AZC VOCABULARY")
print("=" * 70)

# For each AZC placement, how does its vocabulary distribute
# across B line positions (quintiles 0-4)?

quintile_labels = ['Q0(0-.2)', 'Q1(.2-.4)', 'Q2(.4-.6)', 'Q3(.6-.8)', 'Q4(.8-1)']

print(f"\n  {'Place':<6}", end='')
for ql in quintile_labels:
    print(f" {ql:>10}", end='')
print(f" {'Asymmetry':>10}")
print(f"  {'-'*72}")

placement_asymmetries = {}
for p in ['S0', 'S1', 'S2', 'R1', 'R2', 'R3', 'C', 'R', 'S']:
    if p not in azc_sub_words:
        continue
    azc_vocab = set(azc_sub_words[p].keys())

    q_hits = []
    for q in range(5):
        hits = sum(b_position_words[q].get(w, 0) for w in azc_vocab)
        q_hits.append(hits)

    total = sum(q_hits)
    if total < 50:
        continue

    # Asymmetry: (Q0+Q1) / (Q3+Q4) — >1 means left-biased, <1 means right-biased
    left_q = q_hits[0] + q_hits[1]
    right_q = q_hits[3] + q_hits[4]
    asymmetry = left_q / right_q if right_q > 0 else float('inf')
    placement_asymmetries[p] = asymmetry

    print(f"  {p:<6}", end='')
    for q in range(5):
        pct = q_hits[q] / total * 100
        print(f" {pct:>9.1f}%", end='')
    print(f" {asymmetry:>9.2f}x")

# ============================================================
# TEST 5: PAIRED S-SUBSCRIPTS — DO THEY MAP TO OPPOSITE SIDES?
# ============================================================
print(f"\n{'='*70}")
print("TEST 5: DO S1 AND S2 MAP TO OPPOSITE LINE HALVES?")
print("=" * 70)

# Direct comparison: words unique to S1 vs S2
if 'S1' in azc_sub_words and 'S2' in azc_sub_words:
    s1_vocab = set(azc_sub_words['S1'].keys())
    s2_vocab = set(azc_sub_words['S2'].keys())

    s1_only = s1_vocab - s2_vocab
    s2_only = s2_vocab - s1_vocab
    shared = s1_vocab & s2_vocab

    print(f"\n  S1-only words: {len(s1_only)}")
    print(f"  S2-only words: {len(s2_only)}")
    print(f"  Shared words:  {len(shared)}")

    # Mean B position of S1-only vs S2-only words
    s1_only_positions = [word_mean_pos[w] for w in s1_only if w in word_mean_pos]
    s2_only_positions = [word_mean_pos[w] for w in s2_only if w in word_mean_pos]

    if len(s1_only_positions) >= 5 and len(s2_only_positions) >= 5:
        s1_mean = np.mean(s1_only_positions)
        s2_mean = np.mean(s2_only_positions)
        print(f"\n  S1-only mean B position: {s1_mean:.3f} (n={len(s1_only_positions)})")
        print(f"  S2-only mean B position: {s2_mean:.3f} (n={len(s2_only_positions)})")
        print(f"  Separation: {abs(s1_mean - s2_mean):.3f}")

        # Mann-Whitney test
        stat, p_val = mannwhitneyu(s1_only_positions, s2_only_positions, alternative='two-sided')
        print(f"  Mann-Whitney U: stat={stat:.1f}, p={p_val:.4f}")

        if s1_mean < s2_mean:
            print(f"  -> S1 maps LEFT, S2 maps RIGHT")
        else:
            print(f"  -> S2 maps LEFT, S1 maps RIGHT")
    else:
        print(f"  Too few shared words with B for position comparison")

    # Also: S1/S2 PREFIX comparison
    print(f"\n  Prefix profiles:")
    top_pfx = ['ch', 'sh', 'qo', 'NONE', 'ok', 'ot', 'ol']
    print(f"  {'Code':<4}", end='')
    for pfx in top_pfx:
        print(f" {pfx:>6}", end='')
    print()
    for s_code in ['S1', 'S2']:
        total = sum(azc_sub_prefixes[s_code].values())
        if total == 0:
            continue
        print(f"  {s_code:<4}", end='')
        for pfx in top_pfx:
            pct = azc_sub_prefixes[s_code].get(pfx, 0) / total * 100
            print(f" {pct:>5.1f}%", end='')
        print()

# ============================================================
# TEST 6: DO AZC FAMILY TYPES MAP TO DIFFERENT HALVES?
# ============================================================
print(f"\n{'='*70}")
print("TEST 6: ZODIAC vs A/C FAMILY POSITION BIAS")
print("=" * 70)

# Zodiac family = Z sections + f57v
# A/C family = A + C sections (minus f57v)
zodiac_words = Counter()
ac_words = Counter()

for t in tx.azc():
    p = t.placement.strip()
    if p.startswith('L') or p.startswith('P'):
        continue
    sec = t.section
    folio = t.folio

    # Zodiac family: Z sections + f57v
    if sec == 'Z' or folio == 'f57v':
        zodiac_words[t.word] += 1
    elif sec in ('A', 'C') and folio != 'f57v':
        ac_words[t.word] += 1

# Mean B position of Zodiac vocabulary vs A/C vocabulary
zodiac_positions = []
for w in zodiac_words:
    if w in word_mean_pos:
        zodiac_positions.extend([word_mean_pos[w]] * zodiac_words[w])

ac_positions = []
for w in ac_words:
    if w in word_mean_pos:
        ac_positions.extend([word_mean_pos[w]] * ac_words[w])

if zodiac_positions and ac_positions:
    z_mean = np.mean(zodiac_positions)
    ac_mean = np.mean(ac_positions)
    print(f"\n  Zodiac family: mean B position = {z_mean:.3f} (n={len(zodiac_positions)})")
    print(f"  A/C family:    mean B position = {ac_mean:.3f} (n={len(ac_positions)})")
    print(f"  Separation: {abs(z_mean - ac_mean):.3f}")

    stat, p_val = mannwhitneyu(zodiac_positions, ac_positions, alternative='two-sided')
    print(f"  Mann-Whitney U: p={p_val:.4f}")

    if z_mean < ac_mean:
        print(f"  -> Zodiac vocabulary biased LEFT in B lines")
    else:
        print(f"  -> A/C vocabulary biased LEFT in B lines")

# ============================================================
# VERDICT
# ============================================================
print(f"\n{'='*70}")
print("VERDICT")
print("=" * 70)

checks = {
    's_subscripts_asymmetric': False,
    'r_gradient_exists': False,
    'c_is_centered': False,
    'families_map_to_sides': False,
    'quintile_shift_visible': False,
}

# S-subscript asymmetry
if 'S1' in placement_asymmetries and 'S2' in placement_asymmetries:
    s1_asym = placement_asymmetries['S1']
    s2_asym = placement_asymmetries['S2']
    if abs(s1_asym - s2_asym) > 0.15:
        checks['s_subscripts_asymmetric'] = True
        print(f"\n  S1 asymmetry: {s1_asym:.2f}x, S2 asymmetry: {s2_asym:.2f}x")

# R gradient
if 'R1' in placement_mean_positions and 'R3' in placement_mean_positions:
    r1_pos = placement_mean_positions['R1']
    r3_pos = placement_mean_positions['R3']
    if abs(r1_pos - 0.5) > abs(r3_pos - 0.5):
        checks['r_gradient_exists'] = True
        print(f"  R1 distance from center: {abs(r1_pos - 0.5):.3f}")
        print(f"  R3 distance from center: {abs(r3_pos - 0.5):.3f}")

# C centrality
if 'C' in placement_mean_positions:
    c_pos = placement_mean_positions['C']
    if abs(c_pos - 0.5) < 0.03:
        checks['c_is_centered'] = True
    print(f"  C position: {c_pos:.3f} (distance from 0.5: {abs(c_pos - 0.5):.3f})")

# Family side mapping
if zodiac_positions and ac_positions:
    if abs(z_mean - ac_mean) > 0.02 and p_val < 0.05:
        checks['families_map_to_sides'] = True

# Quintile shift
if 'R1' in placement_asymmetries and 'R3' in placement_asymmetries:
    if abs(placement_asymmetries['R1'] - placement_asymmetries['R3']) > 0.1:
        checks['quintile_shift_visible'] = True

n_pass = sum(checks.values())

print(f"\n  Venn correspondence checks ({n_pass}/5):")
for name, val in checks.items():
    print(f"    {name:>30}: {'YES' if val else 'NO'}")

if n_pass >= 4:
    verdict = "TWO_WHEEL_VENN"
    explanation = "AZC subscripts map to opposite halves of B lines - Venn model confirmed"
elif n_pass >= 3:
    verdict = "PARTIAL_VENN"
    explanation = "Some left/right asymmetry in AZC->B mapping but not complete"
elif n_pass >= 2:
    verdict = "WEAK_ASYMMETRY"
    explanation = "Marginal left/right signal, not enough for Venn model"
else:
    verdict = "NO_VENN"
    explanation = "AZC subscripts do not map to opposite halves of B lines"

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

# ============================================================
# SAVE
# ============================================================
result = {
    'placement_mean_b_positions': {k: round(float(v), 4) for k, v in placement_mean_positions.items()},
    'placement_asymmetries': {k: round(float(v), 3) for k, v in placement_asymmetries.items()},
    'family_positions': {
        'zodiac_mean': round(float(z_mean), 4) if zodiac_positions else None,
        'ac_mean': round(float(ac_mean), 4) if ac_positions else None,
        'separation': round(float(abs(z_mean - ac_mean)), 4) if zodiac_positions and ac_positions else None,
        'p_value': round(float(p_val), 4) if zodiac_positions and ac_positions else None,
    },
    'checks': {k: bool(v) for k, v in checks.items()},
    'n_pass': int(n_pass),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "36_azc_venn_test.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
