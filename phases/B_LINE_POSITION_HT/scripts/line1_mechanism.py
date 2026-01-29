"""
Line-1 HT Mechanism Investigation

We know:
- Line-1 has 50.2% HT vs 29.8% body (C747)
- Line-1 HT is morphologically distinct (C749)
- Line-1 HT has 21.7% folio-unique MIDDLEs vs 11.7% body
- B-exclusive vocabulary = HT (C792)

Questions:
1. Does line-1 HT vocabulary correlate with A-folio best-match?
2. Does line-1 HT predict PP vocabulary usage in that folio?
3. Is line-1 HT related to folio sequence position?
4. What characterizes line-1 HT MIDDLEs?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

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

print("=" * 70)
print("LINE-1 HT MECHANISM INVESTIGATION")
print("=" * 70)

# ============================================================
# COLLECT DATA
# ============================================================

# A folio pools
a_folio_pools = defaultdict(set)
for token in tx.currier_a():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            a_folio_pools[token.folio].add(m.middle)

# B data by folio and line
b_data = defaultdict(lambda: {'line1_ht': [], 'line1_pp': [], 'body_pp': [], 'all_pp': []})

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = str(token.line)
    is_ht = w not in classified_tokens
    m = morph.extract(w)
    mid = m.middle

    if not mid:
        continue

    # Check if MIDDLE is PP (in any A folio)
    is_pp = any(mid in pool for pool in a_folio_pools.values())

    if line == '1':
        if is_ht:
            b_data[folio]['line1_ht'].append(mid)
        if is_pp:
            b_data[folio]['line1_pp'].append(mid)
    else:
        if is_pp:
            b_data[folio]['body_pp'].append(mid)

    if is_pp:
        b_data[folio]['all_pp'].append(mid)

b_folios = sorted(b_data.keys())
print(f"\nB folios: {len(b_folios)}")
print(f"A folios: {len(a_folio_pools)}")

# ============================================================
# T1: Does line-1 HT predict A-folio best-match?
# ============================================================
print("\n" + "=" * 70)
print("T1: LINE-1 HT vs A-FOLIO BEST-MATCH")
print("=" * 70)

# For each B folio, find which A folio provides best PP coverage
# Then check if line-1 HT vocabulary overlaps with that A folio's pool

a_folios = sorted(a_folio_pools.keys())

# Compute coverage matrix
coverage = {}
for b_fol in b_folios:
    b_pp = set(b_data[b_fol]['all_pp'])
    if not b_pp:
        continue
    coverage[b_fol] = {}
    for a_fol in a_folios:
        a_pool = a_folio_pools[a_fol]
        cov = len(a_pool & b_pp) / len(b_pp)
        coverage[b_fol][a_fol] = cov

# Find best-match A folio for each B
best_match = {}
for b_fol in coverage:
    best_a = max(coverage[b_fol], key=coverage[b_fol].get)
    best_match[b_fol] = best_a

# Now check: do line-1 HT MIDDLEs appear MORE in the best-match A folio?
line1_ht_in_best = []
line1_ht_in_random = []

rng = np.random.RandomState(42)

for b_fol in b_folios:
    line1_ht_mids = set(b_data[b_fol]['line1_ht'])
    if not line1_ht_mids:
        continue

    best_a = best_match.get(b_fol)
    if not best_a:
        continue

    best_pool = a_folio_pools[best_a]

    # How many line-1 HT MIDDLEs are in best-match A pool?
    in_best = len(line1_ht_mids & best_pool) / len(line1_ht_mids)
    line1_ht_in_best.append(in_best)

    # Compare to random A folio
    random_a = rng.choice(a_folios)
    random_pool = a_folio_pools[random_a]
    in_random = len(line1_ht_mids & random_pool) / len(line1_ht_mids)
    line1_ht_in_random.append(in_random)

print(f"\nLine-1 HT MIDDLEs in best-match A pool:")
print(f"  Mean: {np.mean(line1_ht_in_best):.3f} ({100*np.mean(line1_ht_in_best):.1f}%)")
print(f"  Median: {np.median(line1_ht_in_best):.3f}")

print(f"\nLine-1 HT MIDDLEs in random A pool (baseline):")
print(f"  Mean: {np.mean(line1_ht_in_random):.3f} ({100*np.mean(line1_ht_in_random):.1f}%)")

if line1_ht_in_best and line1_ht_in_random:
    lift = np.mean(line1_ht_in_best) / np.mean(line1_ht_in_random) if np.mean(line1_ht_in_random) > 0 else float('inf')
    print(f"\nLift (best vs random): {lift:.2f}x")

    from scipy import stats
    stat, pval = stats.wilcoxon(line1_ht_in_best, line1_ht_in_random)
    print(f"Wilcoxon test: p = {pval:.4f}")

# ============================================================
# T2: Does line-1 HT predict folio's PP vocabulary?
# ============================================================
print("\n" + "=" * 70)
print("T2: LINE-1 HT vs FOLIO PP VOCABULARY")
print("=" * 70)

# For each B folio: what fraction of body PP MIDDLEs have some substring
# match to line-1 HT MIDDLEs?

# Actually, simpler: do line-1 HT MIDDLEs appear in the body?
line1_ht_in_body = []
for b_fol in b_folios:
    line1_ht_mids = set(b_data[b_fol]['line1_ht'])
    body_pp_mids = set(b_data[b_fol]['body_pp'])

    if not line1_ht_mids or not body_pp_mids:
        continue

    # Do any line-1 HT MIDDLEs appear in body?
    overlap = line1_ht_mids & body_pp_mids
    frac = len(overlap) / len(line1_ht_mids)
    line1_ht_in_body.append(frac)

print(f"\nLine-1 HT MIDDLEs that appear in body PP:")
print(f"  Mean: {np.mean(line1_ht_in_body):.3f} ({100*np.mean(line1_ht_in_body):.1f}%)")
print(f"  Median: {np.median(line1_ht_in_body):.3f}")

# Note: Line-1 HT MIDDLEs are mostly B-exclusive, so low overlap expected

# ============================================================
# T3: Is line-1 HT related to folio sequence?
# ============================================================
print("\n" + "=" * 70)
print("T3: LINE-1 HT vs FOLIO SEQUENCE")
print("=" * 70)

# Get folio sequence numbers
def folio_to_number(f):
    """Extract numeric part of folio name for ordering"""
    import re
    match = re.search(r'f(\d+)', f)
    if match:
        return int(match.group(1))
    return 0

folio_order = {f: i for i, f in enumerate(sorted(b_folios, key=folio_to_number))}

# Does line-1 HT vocabulary size correlate with folio position?
positions = []
line1_ht_sizes = []
line1_ht_unique_rates = []

for b_fol in b_folios:
    line1_ht = b_data[b_fol]['line1_ht']
    if not line1_ht:
        continue

    positions.append(folio_order[b_fol])
    line1_ht_sizes.append(len(line1_ht))
    line1_ht_unique_rates.append(len(set(line1_ht)) / len(line1_ht))

from scipy.stats import spearmanr

if positions:
    rho_size, p_size = spearmanr(positions, line1_ht_sizes)
    rho_unique, p_unique = spearmanr(positions, line1_ht_unique_rates)

    print(f"\nFolio position vs line-1 HT size:")
    print(f"  Spearman rho = {rho_size:.3f}, p = {p_size:.4f}")

    print(f"\nFolio position vs line-1 HT unique rate:")
    print(f"  Spearman rho = {rho_unique:.3f}, p = {p_unique:.4f}")

# ============================================================
# T4: Characterize line-1 HT vocabulary
# ============================================================
print("\n" + "=" * 70)
print("T4: LINE-1 HT VOCABULARY CHARACTERIZATION")
print("=" * 70)

# Collect all line-1 HT MIDDLEs
all_line1_ht_mids = []
for b_fol in b_folios:
    all_line1_ht_mids.extend(b_data[b_fol]['line1_ht'])

line1_ht_counter = Counter(all_line1_ht_mids)
unique_line1_ht = set(all_line1_ht_mids)

print(f"\nLine-1 HT MIDDLEs:")
print(f"  Total occurrences: {len(all_line1_ht_mids)}")
print(f"  Unique types: {len(unique_line1_ht)}")
print(f"  Type/token ratio: {len(unique_line1_ht)/len(all_line1_ht_mids):.3f}")

# Most common
print(f"\nMost common line-1 HT MIDDLEs:")
for mid, count in line1_ht_counter.most_common(15):
    print(f"  '{mid}': {count} occurrences")

# Length distribution
lengths = [len(m) for m in all_line1_ht_mids]
print(f"\nLength distribution:")
print(f"  Mean: {np.mean(lengths):.2f}")
print(f"  Median: {np.median(lengths):.1f}")
print(f"  Max: {max(lengths)}")

# Compare to body HT
all_body_ht_mids = []
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    if w in classified_tokens:
        continue
    if str(token.line) == '1':
        continue
    m = morph.extract(w)
    if m.middle:
        all_body_ht_mids.append(m.middle)

body_lengths = [len(m) for m in all_body_ht_mids]
print(f"\nComparison - Body HT MIDDLE lengths:")
print(f"  Mean: {np.mean(body_lengths):.2f}")
print(f"  Median: {np.median(body_lengths):.1f}")

# Are line-1 HT MIDDLEs longer (compound)?
from scipy.stats import mannwhitneyu
stat, pval = mannwhitneyu(lengths, body_lengths, alternative='greater')
print(f"\nLine-1 HT longer than body HT? Mann-Whitney p = {pval:.4f}")

# ============================================================
# T5: Folio-uniqueness of line-1 HT
# ============================================================
print("\n" + "=" * 70)
print("T5: FOLIO-UNIQUENESS OF LINE-1 HT")
print("=" * 70)

# Which MIDDLEs appear in only one folio's line-1?
mid_to_folios = defaultdict(set)
for b_fol in b_folios:
    for mid in b_data[b_fol]['line1_ht']:
        mid_to_folios[mid].add(b_fol)

folio_unique = [m for m, fols in mid_to_folios.items() if len(fols) == 1]
multi_folio = [m for m, fols in mid_to_folios.items() if len(fols) > 1]

print(f"\nLine-1 HT MIDDLEs by folio spread:")
print(f"  Folio-unique (1 folio): {len(folio_unique)} ({100*len(folio_unique)/len(mid_to_folios):.1f}%)")
print(f"  Multi-folio (2+ folios): {len(multi_folio)} ({100*len(multi_folio)/len(mid_to_folios):.1f}%)")

# What are the multi-folio ones?
print(f"\nMulti-folio line-1 HT MIDDLEs:")
for mid in sorted(multi_folio, key=lambda m: -len(mid_to_folios[m]))[:10]:
    print(f"  '{mid}': {len(mid_to_folios[mid])} folios")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

print(f"""
T1: Line-1 HT MIDDLEs appear in best-match A folio at {100*np.mean(line1_ht_in_best):.1f}%
    vs {100*np.mean(line1_ht_in_random):.1f}% random. Lift = {lift:.2f}x.
    {'SIGNIFICANT' if pval < 0.05 else 'NOT SIGNIFICANT'} (p={pval:.4f})

T2: Only {100*np.mean(line1_ht_in_body):.1f}% of line-1 HT MIDDLEs appear in body PP.
    Line-1 HT vocabulary is largely separate from body vocabulary.

T3: Folio position {'CORRELATES' if p_size < 0.05 else 'does NOT correlate'} with
    line-1 HT size (rho={rho_size:.3f}, p={p_size:.4f}).

T4: Line-1 HT MIDDLEs are {'LONGER' if pval < 0.05 else 'similar length to'} body HT.
    Mean {np.mean(lengths):.2f} vs {np.mean(body_lengths):.2f} chars.

T5: {100*len(folio_unique)/len(mid_to_folios):.1f}% of line-1 HT MIDDLEs are folio-unique.
    These serve as folio identifiers.
""")
