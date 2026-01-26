"""
GALLOWS_B_COMPATIBILITY Phase - Test 5
Question: How many instruction classes survive under full morphological filtering?

Previous finding (C503): Based on MIDDLE-only filtering
New question: What happens with PREFIX+MIDDLE+SUFFIX filtering?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("CLASS SURVIVAL UNDER FULL MORPHOLOGICAL FILTERING")
print("=" * 70)

# Step 1: Build B token -> class mapping
# We need to determine instruction class for each B token
# Class is determined by PREFIX (per C121 structure)
print("\nStep 1: Building B token class assignments...")

# From the grammar, instruction classes are determined by prefix patterns
# Let's use a simplified class assignment based on prefix
def get_instruction_class(prefix, middle, suffix):
    """Assign instruction class based on morphology."""
    # This is a simplified version - the real class system is in BCSC
    # For this test, we'll use prefix as primary class indicator
    if prefix:
        return f"P_{prefix}"
    elif suffix:
        return f"S_{suffix}"
    else:
        return "BARE"

b_tokens = {}  # token -> (prefix, middle, suffix, class)
b_classes = set()

for token in tx.currier_b():
    word = token.word
    m = morph.extract(word)
    if m.middle:
        cls = get_instruction_class(m.prefix, m.middle, m.suffix)
        b_tokens[word] = (m.prefix, m.middle, m.suffix, cls)
        b_classes.add(cls)

print(f"  B tokens: {len(b_tokens)}")
print(f"  Unique classes (by prefix/suffix): {len(b_classes)}")

# Step 2: Build A record morphology
print("\nStep 2: Building A record morphology...")

a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

record_morphology = {}
for (folio, line), tokens in a_records.items():
    prefixes = set()
    middles = set()
    suffixes = set()
    for t in tokens:
        m = morph.extract(t.word)
        if m.prefix:
            prefixes.add(m.prefix)
        if m.middle:
            middles.add(m.middle)
        if m.suffix:
            suffixes.add(m.suffix)
    record_morphology[(folio, line)] = (prefixes, middles, suffixes)

print(f"  A records: {len(record_morphology)}")

# Step 3: Compute class survival under different filtering schemes
print("\nStep 3: Computing class survival...")

b_middles = set(m for p, m, s, c in b_tokens.values())
b_prefixes = set(p for p, m, s, c in b_tokens.values() if p)
b_suffixes = set(s for p, m, s, c in b_tokens.values() if s)

results = {
    'middle_only': [],
    'full_morphology': []
}

for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    # MIDDLE-only: classes of tokens where MIDDLE matches
    middle_classes = set()
    for token, (pref, mid, suf, cls) in b_tokens.items():
        if mid in pp_middles:
            middle_classes.add(cls)
    results['middle_only'].append(len(middle_classes))

    # Full morphology: classes of tokens where all components match
    full_classes = set()
    for token, (pref, mid, suf, cls) in b_tokens.items():
        if mid in pp_middles:
            pref_ok = (pref is None or pref in pp_prefixes)
            suf_ok = (suf is None or suf in pp_suffixes)
            if pref_ok and suf_ok:
                full_classes.add(cls)
    results['full_morphology'].append(len(full_classes))

# Step 4: Results
print("\n" + "=" * 70)
print("CLASS SURVIVAL COMPARISON")
print("=" * 70)

total_classes = len(b_classes)
print(f"\nTotal B classes: {total_classes}")

for scheme, counts in results.items():
    arr = np.array(counts)
    mean_classes = np.mean(arr)
    pct = 100 * mean_classes / total_classes
    print(f"\n{scheme}:")
    print(f"  Mean surviving classes: {mean_classes:.1f} ({pct:.1f}%)")
    print(f"  Median: {np.median(arr):.1f}")
    print(f"  Min: {np.min(arr)}")
    print(f"  Max: {np.max(arr)}")

# Step 5: Distribution
print("\n" + "=" * 70)
print("CLASS SURVIVAL DISTRIBUTION (Full Morphology)")
print("=" * 70)

full_arr = np.array(results['full_morphology'])
bins = [(0, 5), (5, 10), (10, 20), (20, 30), (30, 50)]
print("\nRecords by surviving class count:")
for lo, hi in bins:
    count = sum(1 for c in full_arr if lo <= c < hi)
    pct = 100 * count / len(full_arr)
    print(f"  {lo:2d}-{hi:2d} classes: {count:4d} records ({pct:5.1f}%)")

# Zero classes
zero_count = sum(1 for c in full_arr if c == 0)
print(f"\n  ZERO classes surviving: {zero_count} records ({100*zero_count/len(full_arr):.1f}%)")

# Step 6: Compare to C503 claim
print("\n" + "=" * 70)
print("COMPARISON TO C503")
print("=" * 70)

middle_arr = np.array(results['middle_only'])
middle_mean = np.mean(middle_arr)
full_mean = np.mean(full_arr)
reduction = 100 * (1 - full_mean / middle_mean)

print(f"""
C503 (MIDDLE-only): ~32.3 mean classes (66% of 49)
Our MIDDLE-only:    {middle_mean:.1f} classes ({100*middle_mean/total_classes:.1f}% of {total_classes})

Full morphology:    {full_mean:.1f} classes ({100*full_mean/total_classes:.1f}% of {total_classes})

Additional reduction from PREFIX+SUFFIX: {reduction:.1f}%
""")

# Step 7: What classes always survive vs never survive?
print("=" * 70)
print("CLASS SURVIVAL PATTERNS")
print("=" * 70)

# Count how often each class survives
class_survival_count = defaultdict(int)
for counts_list in [results['full_morphology']]:
    for i, ((folio, line), (prefixes, middles, suffixes)) in enumerate(record_morphology.items()):
        pp_middles = middles & b_middles
        pp_prefixes = prefixes & b_prefixes
        pp_suffixes = suffixes & b_suffixes

        for token, (pref, mid, suf, cls) in b_tokens.items():
            if mid in pp_middles:
                pref_ok = (pref is None or pref in pp_prefixes)
                suf_ok = (suf is None or suf in pp_suffixes)
                if pref_ok and suf_ok:
                    class_survival_count[cls] += 1

n_records = len(record_morphology)
always_survive = [c for c, cnt in class_survival_count.items() if cnt == n_records]
never_survive = [c for c in b_classes if class_survival_count[c] == 0]
rare_survive = [c for c, cnt in class_survival_count.items() if 0 < cnt < n_records * 0.1]

print(f"\nClasses that ALWAYS survive (100%): {len(always_survive)}")
if always_survive:
    print(f"  {always_survive[:10]}...")

print(f"\nClasses that NEVER survive (0%): {len(never_survive)}")
if never_survive:
    print(f"  {never_survive[:10]}...")

print(f"\nClasses that rarely survive (<10%): {len(rare_survive)}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
Under full morphological filtering (PREFIX+MIDDLE+SUFFIX):

  Mean surviving classes: {full_mean:.1f} / {total_classes} ({100*full_mean/total_classes:.1f}%)

  This is a {reduction:.1f}% reduction from MIDDLE-only filtering.

  Implication: A records constrain B to not just a vocabulary slice,
  but also to a SUBSET OF INSTRUCTION CLASSES.
""")
