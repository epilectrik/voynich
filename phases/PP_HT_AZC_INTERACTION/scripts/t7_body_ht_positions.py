"""
T7: Body HT Positional Patterns

Questions:
1. Where in the line does body HT appear? (initial, medial, final)
2. Does body HT cluster near FL tokens?
3. Does body HT cluster near LINK (ol) tokens?
4. Is body HT at line boundaries?
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

FL_CLASSES = {7, 30, 38, 40}

print("=" * 70)
print("T7: BODY HT POSITIONAL PATTERNS")
print("=" * 70)

# Collect tokens by line with positions
lines_data = defaultdict(list)  # (folio, line) -> [(word, is_ht, is_fl, is_link), ...]

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = str(token.line)

    if line == '1':
        continue  # Skip line-1, focus on body

    is_ht = w not in classified_tokens
    is_fl = False
    is_link = 'ol' in w  # LINK tokens contain 'ol'

    if not is_ht:
        cls = int(ctm['token_to_class'][w])
        is_fl = cls in FL_CLASSES

    lines_data[(folio, line)].append({
        'word': w,
        'is_ht': is_ht,
        'is_fl': is_fl,
        'is_link': is_link,
    })

print(f"\nBody lines analyzed: {len(lines_data)}")

# ============================================================
# TEST 1: HT position within line
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: HT POSITION WITHIN LINE")
print("=" * 70)

ht_positions = []  # normalized position (0-1)
non_ht_positions = []

for (folio, line), tokens in lines_data.items():
    n = len(tokens)
    if n < 3:
        continue

    for i, tok in enumerate(tokens):
        pos = i / (n - 1) if n > 1 else 0.5
        if tok['is_ht']:
            ht_positions.append(pos)
        else:
            non_ht_positions.append(pos)

print(f"\nHT tokens: {len(ht_positions)}")
print(f"Non-HT tokens: {len(non_ht_positions)}")

print(f"\nMean position (0=start, 1=end):")
print(f"  HT: {np.mean(ht_positions):.3f}")
print(f"  Non-HT: {np.mean(non_ht_positions):.3f}")

mw_stat, mw_p = stats.mannwhitneyu(ht_positions, non_ht_positions, alternative='two-sided')
print(f"\nMann-Whitney: U={mw_stat:.0f}, p={mw_p:.4f}")

# Position bins
bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
ht_hist, _ = np.histogram(ht_positions, bins=bins)
non_ht_hist, _ = np.histogram(non_ht_positions, bins=bins)

print(f"\nPosition distribution:")
print(f"  Bin        HT%    Non-HT%")
for i in range(len(bins)-1):
    ht_pct = 100 * ht_hist[i] / len(ht_positions)
    non_ht_pct = 100 * non_ht_hist[i] / len(non_ht_positions)
    print(f"  {bins[i]:.1f}-{bins[i+1]:.1f}:   {ht_pct:5.1f}%  {non_ht_pct:5.1f}%")

# ============================================================
# TEST 2: HT proximity to FL tokens
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: HT PROXIMITY TO FL TOKENS")
print("=" * 70)

# For each HT token, measure distance to nearest FL
ht_to_fl_distances = []
non_ht_to_fl_distances = []

for (folio, line), tokens in lines_data.items():
    fl_positions = [i for i, tok in enumerate(tokens) if tok['is_fl']]

    if not fl_positions:
        continue

    for i, tok in enumerate(tokens):
        min_dist = min(abs(i - fp) for fp in fl_positions)
        if tok['is_ht']:
            ht_to_fl_distances.append(min_dist)
        elif not tok['is_fl']:  # non-HT, non-FL
            non_ht_to_fl_distances.append(min_dist)

print(f"\nLines with FL tokens: measuring HT distance to nearest FL")
print(f"HT tokens near FL: {len(ht_to_fl_distances)}")
print(f"Non-HT tokens near FL: {len(non_ht_to_fl_distances)}")

if ht_to_fl_distances and non_ht_to_fl_distances:
    print(f"\nMean distance to nearest FL:")
    print(f"  HT: {np.mean(ht_to_fl_distances):.2f} tokens")
    print(f"  Non-HT: {np.mean(non_ht_to_fl_distances):.2f} tokens")

    mw_fl, p_fl = stats.mannwhitneyu(ht_to_fl_distances, non_ht_to_fl_distances, alternative='two-sided')
    print(f"\nMann-Whitney: U={mw_fl:.0f}, p={p_fl:.4f}")

    # Adjacent to FL?
    ht_adjacent = sum(1 for d in ht_to_fl_distances if d <= 1)
    non_ht_adjacent = sum(1 for d in non_ht_to_fl_distances if d <= 1)

    print(f"\nAdjacent to FL (distance <= 1):")
    print(f"  HT: {100*ht_adjacent/len(ht_to_fl_distances):.1f}%")
    print(f"  Non-HT: {100*non_ht_adjacent/len(non_ht_to_fl_distances):.1f}%")

# ============================================================
# TEST 3: HT proximity to LINK tokens
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: HT PROXIMITY TO LINK TOKENS")
print("=" * 70)

ht_to_link_distances = []
non_ht_to_link_distances = []

for (folio, line), tokens in lines_data.items():
    link_positions = [i for i, tok in enumerate(tokens) if tok['is_link']]

    if not link_positions:
        continue

    for i, tok in enumerate(tokens):
        min_dist = min(abs(i - lp) for lp in link_positions)
        if tok['is_ht']:
            ht_to_link_distances.append(min_dist)
        elif not tok['is_link']:
            non_ht_to_link_distances.append(min_dist)

print(f"\nLines with LINK tokens:")
print(f"HT tokens: {len(ht_to_link_distances)}")
print(f"Non-HT tokens: {len(non_ht_to_link_distances)}")

if ht_to_link_distances and non_ht_to_link_distances:
    print(f"\nMean distance to nearest LINK:")
    print(f"  HT: {np.mean(ht_to_link_distances):.2f} tokens")
    print(f"  Non-HT: {np.mean(non_ht_to_link_distances):.2f} tokens")

    mw_link, p_link = stats.mannwhitneyu(ht_to_link_distances, non_ht_to_link_distances, alternative='two-sided')
    print(f"\nMann-Whitney: U={mw_link:.0f}, p={p_link:.4f}")

# ============================================================
# TEST 4: HT at line boundaries
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: HT AT LINE BOUNDARIES")
print("=" * 70)

first_token_ht = 0
first_token_total = 0
last_token_ht = 0
last_token_total = 0
middle_token_ht = 0
middle_token_total = 0

for (folio, line), tokens in lines_data.items():
    if len(tokens) < 3:
        continue

    # First token
    first_token_total += 1
    if tokens[0]['is_ht']:
        first_token_ht += 1

    # Last token
    last_token_total += 1
    if tokens[-1]['is_ht']:
        last_token_ht += 1

    # Middle tokens
    for tok in tokens[1:-1]:
        middle_token_total += 1
        if tok['is_ht']:
            middle_token_ht += 1

print(f"\nHT rate by position:")
print(f"  First token: {100*first_token_ht/first_token_total:.1f}% ({first_token_ht}/{first_token_total})")
print(f"  Last token: {100*last_token_ht/last_token_total:.1f}% ({last_token_ht}/{last_token_total})")
print(f"  Middle tokens: {100*middle_token_ht/middle_token_total:.1f}% ({middle_token_ht}/{middle_token_total})")

# Chi-squared for boundary effect
contingency = [[first_token_ht, first_token_total - first_token_ht],
               [middle_token_ht, middle_token_total - middle_token_ht]]
chi2_first, p_first, _, _ = stats.chi2_contingency(contingency)

contingency = [[last_token_ht, last_token_total - last_token_ht],
               [middle_token_ht, middle_token_total - middle_token_ht]]
chi2_last, p_last, _, _ = stats.chi2_contingency(contingency)

print(f"\nFirst vs Middle: chi2={chi2_first:.1f}, p={p_first:.4f}")
print(f"Last vs Middle: chi2={chi2_last:.1f}, p={p_last:.4f}")

# ============================================================
# TEST 5: HT before vs after FL
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: HT BEFORE vs AFTER FL")
print("=" * 70)

ht_before_fl = 0
ht_after_fl = 0
non_ht_before_fl = 0
non_ht_after_fl = 0

for (folio, line), tokens in lines_data.items():
    fl_positions = [i for i, tok in enumerate(tokens) if tok['is_fl']]

    if not fl_positions:
        continue

    first_fl = min(fl_positions)
    last_fl = max(fl_positions)

    for i, tok in enumerate(tokens):
        if tok['is_fl']:
            continue

        if i < first_fl:
            if tok['is_ht']:
                ht_before_fl += 1
            else:
                non_ht_before_fl += 1
        elif i > last_fl:
            if tok['is_ht']:
                ht_after_fl += 1
            else:
                non_ht_after_fl += 1

total_before = ht_before_fl + non_ht_before_fl
total_after = ht_after_fl + non_ht_after_fl

if total_before > 0 and total_after > 0:
    print(f"\nHT rate before first FL: {100*ht_before_fl/total_before:.1f}%")
    print(f"HT rate after last FL: {100*ht_after_fl/total_after:.1f}%")

    contingency = [[ht_before_fl, non_ht_before_fl],
                   [ht_after_fl, non_ht_after_fl]]
    chi2_ba, p_ba, _, _ = stats.chi2_contingency(contingency)
    print(f"\nChi-squared (before vs after): chi2={chi2_ba:.1f}, p={p_ba:.4f}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
POSITION WITHIN LINE:
  HT mean position: {np.mean(ht_positions):.3f}
  Non-HT mean position: {np.mean(non_ht_positions):.3f}
  {'HT skews EARLIER' if np.mean(ht_positions) < np.mean(non_ht_positions) else 'HT skews LATER'} (p={mw_p:.4f})

LINE BOUNDARIES:
  First token HT rate: {100*first_token_ht/first_token_total:.1f}%
  Middle token HT rate: {100*middle_token_ht/middle_token_total:.1f}%
  Last token HT rate: {100*last_token_ht/last_token_total:.1f}%

FL PROXIMITY:
  HT mean distance to FL: {np.mean(ht_to_fl_distances):.2f} tokens
  Non-HT mean distance to FL: {np.mean(non_ht_to_fl_distances):.2f} tokens
  {'HT is CLOSER to FL' if np.mean(ht_to_fl_distances) < np.mean(non_ht_to_fl_distances) else 'HT is FARTHER from FL'} (p={p_fl:.4f})
""")
