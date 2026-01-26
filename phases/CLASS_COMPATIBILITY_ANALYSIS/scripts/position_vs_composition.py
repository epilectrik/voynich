"""
POSITION VS COMPOSITION TEST

Is the PREFIX consistency due to:
1. POSITIONAL GRAMMAR (C510) - substrings at same position use same PREFIXes
2. TRUE COMPOSITION - substrings carry meaning regardless of position

If positional: consistency should correlate with position consistency
If compositional: consistency should be independent of position
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np
from itertools import combinations

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("POSITION VS COMPOSITION TEST")
print("Is PREFIX consistency driven by position or by substring meaning?")
print("=" * 70)

# Build data
token_data = []
folio_middles = defaultdict(Counter)

for token in tx.currier_b():
    word = token.word
    if word:
        m = morph.extract(word)
        if m.middle:
            token_data.append({
                'word': word,
                'folio': token.folio,
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
            })
            folio_middles[token.folio][m.middle] += 1

# Unique MIDDLEs
middle_folios = defaultdict(set)
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folios[m].add(folio)

unique_middles = {m for m, folios in middle_folios.items() if len(folios) == 1}

# Extract substrings
def get_substrings(middle, min_len=2, max_len=3):
    subs = set()
    for length in range(min_len, min(max_len + 1, len(middle))):
        for i in range(len(middle) - length + 1):
            subs.add(middle[i:i+length])
    return subs

substring_to_middles = defaultdict(list)
for m in unique_middles:
    folio = list(middle_folios[m])[0]
    for sub in get_substrings(m):
        substring_to_middles[sub].append((m, folio))

cross_folio_substrings = {
    sub: occs for sub, occs in substring_to_middles.items()
    if len(set(f for m, f in occs)) >= 5
}

# MIDDLE -> PREFIX associations
middle_prefixes = defaultdict(Counter)
for t in token_data:
    if t['prefix']:
        middle_prefixes[t['middle']][t['prefix']] += 1

def get_prefix_distribution(middle):
    counts = middle_prefixes[middle]
    total = sum(counts.values())
    if total == 0:
        return {}
    return {p: c/total for p, c in counts.items()}

def jensen_shannon(p, q):
    all_keys = set(p.keys()) | set(q.keys())
    if not all_keys:
        return 0
    p_vec = np.array([p.get(k, 0) for k in all_keys])
    q_vec = np.array([q.get(k, 0) for k in all_keys])
    p_vec = p_vec / (p_vec.sum() + 1e-10)
    q_vec = q_vec / (q_vec.sum() + 1e-10)
    m = (p_vec + q_vec) / 2
    def kl(a, b):
        mask = a > 0
        return np.sum(a[mask] * np.log(a[mask] / (b[mask] + 1e-10)))
    return (kl(p_vec, m) + kl(q_vec, m)) / 2

def get_substring_position(middle, substring):
    idx = middle.find(substring)
    if idx == -1:
        return None
    return idx / max(len(middle) - len(substring), 1)

# For each substring, compute:
# 1. PREFIX consistency (mean JS between MIDDLEs containing it)
# 2. Position consistency (std of position)
# Then correlate them

results = []

for sub, occurrences in cross_folio_substrings.items():
    middles = [m for m, f in occurrences]

    # PREFIX consistency
    prefix_dists = [get_prefix_distribution(m) for m in middles]
    prefix_dists = [d for d in prefix_dists if d]

    if len(prefix_dists) < 3:
        continue

    js_values = []
    for i, j in combinations(range(len(prefix_dists)), 2):
        js = jensen_shannon(prefix_dists[i], prefix_dists[j])
        js_values.append(js)

    if not js_values:
        continue

    mean_js = np.mean(js_values)

    # Position consistency
    positions = []
    for m, f in occurrences:
        pos = get_substring_position(m, sub)
        if pos is not None:
            positions.append(pos)

    if len(positions) < 3:
        continue

    pos_std = np.std(positions)
    mean_pos = np.mean(positions)

    results.append({
        'sub': sub,
        'prefix_js': mean_js,  # Lower = more consistent
        'pos_std': pos_std,    # Lower = more consistent position
        'mean_pos': mean_pos,
        'n': len(occurrences)
    })

# Correlation: does position consistency predict PREFIX consistency?
prefix_js = [r['prefix_js'] for r in results]
pos_std = [r['pos_std'] for r in results]

from scipy import stats
corr, p_value = stats.pearsonr(prefix_js, pos_std)

print(f"\nCorrelation: position_std vs prefix_JS")
print(f"  r = {corr:.3f}, p = {p_value:.4f}")

if corr > 0 and p_value < 0.05:
    print(f"\n  => POSITIVE CORRELATION: Position-consistent substrings have MORE PREFIX consistency")
    print(f"     This suggests PREFIX consistency is driven by POSITIONAL GRAMMAR (C510)")
elif corr < 0 and p_value < 0.05:
    print(f"\n  => NEGATIVE CORRELATION: Position-variable substrings have MORE PREFIX consistency")
    print(f"     This would suggest TRUE COMPOSITIONAL meaning")
else:
    print(f"\n  => NO SIGNIFICANT CORRELATION")
    print(f"     PREFIX consistency is INDEPENDENT of positional consistency")

# Split by position consistency and compare
print("\n" + "=" * 70)
print("STRATIFIED ANALYSIS")
print("=" * 70)

pos_consistent = [r for r in results if r['pos_std'] < 0.25]
pos_variable = [r for r in results if r['pos_std'] >= 0.25]

print(f"\nPosition-CONSISTENT substrings (std < 0.25): {len(pos_consistent)}")
if pos_consistent:
    pc_js = [r['prefix_js'] for r in pos_consistent]
    print(f"  PREFIX JS: mean={np.mean(pc_js):.3f}")

print(f"\nPosition-VARIABLE substrings (std >= 0.25): {len(pos_variable)}")
if pos_variable:
    pv_js = [r['prefix_js'] for r in pos_variable]
    print(f"  PREFIX JS: mean={np.mean(pv_js):.3f}")

if pos_consistent and pos_variable:
    pc_js = [r['prefix_js'] for r in pos_consistent]
    pv_js = [r['prefix_js'] for r in pos_variable]
    t, p = stats.ttest_ind(pc_js, pv_js)
    print(f"\nT-test (position-consistent vs position-variable):")
    print(f"  t = {t:.3f}, p = {p:.4f}")

# Check: do position-variable substrings still show PREFIX consistency vs random?
print("\n" + "=" * 70)
print("POSITION-VARIABLE SUBSTRINGS VS RANDOM BASELINE")
print("=" * 70)

import random
random.seed(42)

unique_list = list(unique_middles)
random_js = []
for _ in range(500):
    m1, m2 = random.sample(unique_list, 2)
    d1 = get_prefix_distribution(m1)
    d2 = get_prefix_distribution(m2)
    if d1 and d2:
        random_js.append(jensen_shannon(d1, d2))

print(f"\nRandom pairs: JS = {np.mean(random_js):.3f}")
if pos_variable:
    pv_js = [r['prefix_js'] for r in pos_variable]
    print(f"Position-VARIABLE shared substrings: JS = {np.mean(pv_js):.3f}")

    t, p = stats.ttest_ind(pv_js, random_js)
    print(f"\nT-test (position-variable vs random):")
    print(f"  t = {t:.3f}, p = {p:.4f}")

    if p < 0.05 and np.mean(pv_js) < np.mean(random_js):
        print(f"\n  => COMPOSITIONAL SIGNAL SURVIVES position control")
        print(f"     Even position-variable substrings show PREFIX consistency")
        print(f"     This suggests substrings carry meaning BEYOND position")
    else:
        print(f"\n  => NO COMPOSITIONAL SIGNAL after position control")
        print(f"     PREFIX consistency was driven by positional grammar")

# Summary
print("\n" + "=" * 70)
print("FINAL INTERPRETATION")
print("=" * 70)

if pos_variable and p < 0.05 and np.mean(pv_js) < np.mean(random_js):
    print("""
COMPOSITIONAL MEANING DETECTED:

Even when controlling for position, shared substrings show PREFIX consistency.
This suggests substrings DO carry behavioral/semantic meaning across folios.

The C512 retest may have been too conservative, or the signal emerges
only when testing cross-folio unique MIDDLEs specifically.

This SUPPORTS the interpretation that unique MIDDLEs are compositional
elaborations, not just string mathematics.
""")
else:
    print("""
POSITIONAL GRAMMAR ONLY:

PREFIX consistency is explained by positional grammar (C510).
Substrings that appear at consistent positions show consistent PREFIX usage.
This is already documented in C510-C513.

When controlling for position, no compositional signal remains.
The C512 retest verdict stands: containment is string mathematics.
""")
