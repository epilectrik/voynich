"""
SUBSTRING CONSISTENCY TEST

If unique MIDDLEs are compositional, shared substrings should show consistent behavior.
If it's just string math, substring sharing should be random.

Test: Do unique MIDDLEs that share a substring behave similarly?
- Same PREFIX associations?
- Same SUFFIX associations?
- Same positional patterns?
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
print("SUBSTRING CONSISTENCY TEST")
print("Do shared substrings in unique MIDDLEs behave consistently?")
print("=" * 70)

# Build token data with full morphology
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
                'line': token.line,
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
            })
            folio_middles[token.folio][m.middle] += 1

# Identify unique MIDDLEs (appear in exactly 1 folio)
middle_folios = defaultdict(set)
for folio, middles in folio_middles.items():
    for m in middles:
        middle_folios[m].add(folio)

unique_middles = {m for m, folios in middle_folios.items() if len(folios) == 1}
print(f"\nUnique MIDDLEs: {len(unique_middles)}")

# Extract substrings of length 2-3 from unique MIDDLEs
def get_substrings(middle, min_len=2, max_len=3):
    subs = set()
    for length in range(min_len, min(max_len + 1, len(middle))):
        for i in range(len(middle) - length + 1):
            subs.add(middle[i:i+length])
    return subs

# Find substrings that appear in multiple unique MIDDLEs across different folios
substring_to_middles = defaultdict(list)
for m in unique_middles:
    folio = list(middle_folios[m])[0]
    for sub in get_substrings(m):
        substring_to_middles[sub].append((m, folio))

# Filter to substrings appearing in 5+ unique MIDDLEs from different folios
cross_folio_substrings = {}
for sub, occurrences in substring_to_middles.items():
    folios = set(f for m, f in occurrences)
    if len(folios) >= 5:  # At least 5 different folios
        cross_folio_substrings[sub] = occurrences

print(f"Substrings in 5+ folios' unique MIDDLEs: {len(cross_folio_substrings)}")

# For each cross-folio substring, check if it has consistent PREFIX/SUFFIX associations
print("\n" + "=" * 70)
print("PREFIX CONSISTENCY TEST")
print("Do MIDDLEs sharing a substring use similar PREFIXes?")
print("=" * 70)

# Build MIDDLE -> PREFIX/SUFFIX associations from actual tokens
middle_prefixes = defaultdict(Counter)
middle_suffixes = defaultdict(Counter)

for t in token_data:
    if t['prefix']:
        middle_prefixes[t['middle']][t['prefix']] += 1
    if t['suffix']:
        middle_suffixes[t['middle']][t['suffix']] += 1

def get_prefix_distribution(middle):
    """Get normalized PREFIX distribution for a MIDDLE."""
    counts = middle_prefixes[middle]
    total = sum(counts.values())
    if total == 0:
        return {}
    return {p: c/total for p, c in counts.items()}

def jensen_shannon(p, q):
    """Jensen-Shannon divergence between two distributions."""
    all_keys = set(p.keys()) | set(q.keys())
    if not all_keys:
        return 0

    p_vec = np.array([p.get(k, 0) for k in all_keys])
    q_vec = np.array([q.get(k, 0) for k in all_keys])

    # Normalize
    p_vec = p_vec / (p_vec.sum() + 1e-10)
    q_vec = q_vec / (q_vec.sum() + 1e-10)

    m = (p_vec + q_vec) / 2

    # KL divergence with smoothing
    def kl(a, b):
        mask = a > 0
        return np.sum(a[mask] * np.log(a[mask] / (b[mask] + 1e-10)))

    return (kl(p_vec, m) + kl(q_vec, m)) / 2

# For each cross-folio substring, compute PREFIX consistency
substring_consistency = []

for sub, occurrences in list(cross_folio_substrings.items())[:50]:  # Top 50
    middles = [m for m, f in occurrences]

    # Get PREFIX distributions for each unique MIDDLE containing this substring
    prefix_dists = [get_prefix_distribution(m) for m in middles]
    prefix_dists = [d for d in prefix_dists if d]  # Filter empty

    if len(prefix_dists) < 2:
        continue

    # Compute pairwise JS divergence
    js_values = []
    for i, j in combinations(range(len(prefix_dists)), 2):
        js = jensen_shannon(prefix_dists[i], prefix_dists[j])
        js_values.append(js)

    if js_values:
        mean_js = np.mean(js_values)
        substring_consistency.append((sub, mean_js, len(occurrences)))

# Sort by consistency (lower JS = more consistent)
substring_consistency.sort(key=lambda x: x[1])

print(f"\nMost PREFIX-consistent substrings (low JS = consistent):")
for sub, js, count in substring_consistency[:15]:
    print(f"  '{sub}': JS={js:.3f} (in {count} unique MIDDLEs)")

print(f"\nLeast PREFIX-consistent substrings (high JS = inconsistent):")
for sub, js, count in substring_consistency[-10:]:
    print(f"  '{sub}': JS={js:.3f} (in {count} unique MIDDLEs)")

# Baseline: random pairs of unique MIDDLEs (no shared substring)
print("\n" + "=" * 70)
print("BASELINE: Random pairs (no shared substring)")
print("=" * 70)

import random
random.seed(42)

unique_middle_list = list(unique_middles)
random_js = []

for _ in range(500):
    m1, m2 = random.sample(unique_middle_list, 2)
    d1 = get_prefix_distribution(m1)
    d2 = get_prefix_distribution(m2)
    if d1 and d2:
        random_js.append(jensen_shannon(d1, d2))

print(f"Random pair JS divergence: mean={np.mean(random_js):.3f}, std={np.std(random_js):.3f}")

# Compare
shared_js = [js for sub, js, count in substring_consistency]
print(f"Shared substring JS divergence: mean={np.mean(shared_js):.3f}, std={np.std(shared_js):.3f}")

if np.mean(shared_js) < np.mean(random_js):
    reduction = (np.mean(random_js) - np.mean(shared_js)) / np.mean(random_js) * 100
    print(f"\n=> Shared substrings are {reduction:.1f}% MORE PREFIX-consistent than random")
else:
    print(f"\n=> Shared substrings are NOT more consistent than random")

# Statistical test
from scipy import stats
t_stat, p_value = stats.ttest_ind(shared_js, random_js)
print(f"T-test: t={t_stat:.3f}, p={p_value:.4f}")

# Now check POSITION consistency
print("\n" + "=" * 70)
print("POSITION CONSISTENCY TEST")
print("Does the substring appear at the same position within MIDDLEs?")
print("=" * 70)

def get_substring_position(middle, substring):
    """Return normalized position (0=start, 1=end) of substring in middle."""
    idx = middle.find(substring)
    if idx == -1:
        return None
    # Normalize: 0 = start, 1 = end
    return idx / max(len(middle) - len(substring), 1)

position_consistency = []

for sub, occurrences in list(cross_folio_substrings.items())[:50]:
    positions = []
    for m, f in occurrences:
        pos = get_substring_position(m, sub)
        if pos is not None:
            positions.append(pos)

    if len(positions) >= 5:
        # Lower std = more consistent position
        std = np.std(positions)
        mean_pos = np.mean(positions)
        position_consistency.append((sub, std, mean_pos, len(positions)))

position_consistency.sort(key=lambda x: x[1])

print(f"\nMost position-consistent substrings:")
for sub, std, mean_pos, count in position_consistency[:15]:
    pos_label = "START" if mean_pos < 0.3 else "END" if mean_pos > 0.7 else "MIDDLE"
    print(f"  '{sub}': std={std:.3f}, mean_pos={mean_pos:.2f} ({pos_label}), n={count}")

# Are certain substrings always at START vs END?
print("\n" + "=" * 70)
print("POSITIONAL SPECIALIZATION")
print("=" * 70)

start_subs = [(s, std, mp, n) for s, std, mp, n in position_consistency if mp < 0.25 and std < 0.2]
end_subs = [(s, std, mp, n) for s, std, mp, n in position_consistency if mp > 0.75 and std < 0.2]

print(f"\nSTART-specialized substrings (pos<0.25, std<0.2): {len(start_subs)}")
for sub, std, mp, n in start_subs[:10]:
    print(f"  '{sub}': mean_pos={mp:.2f}, std={std:.3f}, n={n}")

print(f"\nEND-specialized substrings (pos>0.75, std<0.2): {len(end_subs)}")
for sub, std, mp, n in end_subs[:10]:
    print(f"  '{sub}': mean_pos={mp:.2f}, std={std:.3f}, n={n}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
PREFIX CONSISTENCY:
  - Shared substring pairs: JS = {np.mean(shared_js):.3f}
  - Random pairs: JS = {np.mean(random_js):.3f}
  - T-test p = {p_value:.4f}

POSITION CONSISTENCY:
  - START-specialized substrings: {len(start_subs)}
  - END-specialized substrings: {len(end_subs)}

INTERPRETATION:
""")

if p_value < 0.05 and np.mean(shared_js) < np.mean(random_js):
    print("""
  => COMPOSITIONAL SIGNAL DETECTED
  MIDDLEs sharing a substring DO show more consistent PREFIX usage
  than random pairs. This suggests substrings carry behavioral meaning.
""")
elif len(start_subs) > 5 or len(end_subs) > 5:
    print("""
  => POSITIONAL STRUCTURE DETECTED
  Some substrings are reliably START or END positioned.
  This is consistent with C510's positional sub-component grammar.
""")
else:
    print("""
  => NO COMPOSITIONAL SIGNAL
  Shared substrings do not show consistent PREFIX/SUFFIX/position behavior.
  The containment is likely string mathematics, not composition.
""")
