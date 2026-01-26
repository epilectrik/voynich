"""
GALLOWS_B_COMPATIBILITY Phase - Test 4
Question: Do PREFIX and SUFFIX affect token-level B filtering?

We know:
- MIDDLE is the primary filter (~95% of B vocabulary filtered)
- PREFIX has AZC family affinity (C471)
- SUFFIX has regime breadth association (C495)

This tests whether PREFIX/SUFFIX add filtering power beyond MIDDLE.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict
import numpy as np
from scipy import stats

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("PREFIX/SUFFIX FILTERING ANALYSIS")
print("=" * 70)

# Step 1: Build B token inventory with full morphology
print("\nStep 1: Building B token morphology...")

b_tokens = {}  # token -> (prefix, middle, suffix)
for token in tx.currier_b():
    word = token.word
    m = morph.extract(word)
    if m.middle:
        b_tokens[word] = (m.prefix, m.middle, m.suffix)

print(f"  B tokens with morphology: {len(b_tokens)}")

# Group B tokens by MIDDLE, PREFIX, SUFFIX
b_by_middle = defaultdict(set)
b_by_prefix = defaultdict(set)
b_by_suffix = defaultdict(set)

for token, (prefix, middle, suffix) in b_tokens.items():
    b_by_middle[middle].add(token)
    if prefix:
        b_by_prefix[prefix].add(token)
    if suffix:
        b_by_suffix[suffix].add(token)

print(f"  Unique B MIDDLEs: {len(b_by_middle)}")
print(f"  Unique B PREFIXes: {len(b_by_prefix)}")
print(f"  Unique B SUFFIXes: {len(b_by_suffix)}")

# Step 2: Build A record morphology profiles
print("\nStep 2: Building A record morphology...")

a_records = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    a_records[key].append(token)

record_morphology = {}  # (folio, line) -> (prefixes, middles, suffixes)
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

# Step 3: Compute legal B tokens under different filtering schemes
print("\nStep 3: Computing legal tokens under different filters...")

b_middles = set(b_by_middle.keys())
b_prefixes = set(b_by_prefix.keys())
b_suffixes = set(b_by_suffix.keys())

results = {
    'middle_only': [],
    'middle_and_prefix': [],
    'middle_and_suffix': [],
    'full_morphology': []
}

for (folio, line), (prefixes, middles, suffixes) in record_morphology.items():
    # PP = shared with B
    pp_middles = middles & b_middles
    pp_prefixes = prefixes & b_prefixes
    pp_suffixes = suffixes & b_suffixes

    # MIDDLE-only filtering
    middle_legal = set()
    for mid in pp_middles:
        middle_legal.update(b_by_middle[mid])
    results['middle_only'].append(len(middle_legal))

    # MIDDLE + PREFIX filtering
    mp_legal = set()
    for token, (pref, mid, suf) in b_tokens.items():
        if mid in pp_middles:
            if pref is None or pref in pp_prefixes:
                mp_legal.add(token)
    results['middle_and_prefix'].append(len(mp_legal))

    # MIDDLE + SUFFIX filtering
    ms_legal = set()
    for token, (pref, mid, suf) in b_tokens.items():
        if mid in pp_middles:
            if suf is None or suf in pp_suffixes:
                ms_legal.add(token)
    results['middle_and_suffix'].append(len(ms_legal))

    # Full morphology filtering
    full_legal = set()
    for token, (pref, mid, suf) in b_tokens.items():
        if mid in pp_middles:
            pref_ok = (pref is None or pref in pp_prefixes)
            suf_ok = (suf is None or suf in pp_suffixes)
            if pref_ok and suf_ok:
                full_legal.add(token)
    results['full_morphology'].append(len(full_legal))

# Step 4: Compare filtering schemes
print("\n" + "=" * 70)
print("FILTERING SCHEME COMPARISON")
print("=" * 70)

total_b = len(b_tokens)
print(f"\nTotal B tokens: {total_b}")
print("\nMean legal tokens by filtering scheme:")
print("-" * 50)

for scheme, counts in results.items():
    arr = np.array(counts)
    mean_legal = np.mean(arr)
    pct = 100 * mean_legal / total_b
    filtered_pct = 100 - pct
    print(f"  {scheme:20s}: {mean_legal:6.1f} legal ({pct:4.1f}%), {filtered_pct:4.1f}% filtered")

# Step 5: Incremental filtering effect
print("\n" + "=" * 70)
print("INCREMENTAL FILTERING EFFECT")
print("=" * 70)

m_only = np.array(results['middle_only'])
mp = np.array(results['middle_and_prefix'])
ms = np.array(results['middle_and_suffix'])
full = np.array(results['full_morphology'])

prefix_reduction = 100 * (1 - np.mean(mp) / np.mean(m_only))
suffix_reduction = 100 * (1 - np.mean(ms) / np.mean(m_only))
full_reduction = 100 * (1 - np.mean(full) / np.mean(m_only))

print(f"""
Starting from MIDDLE-only filtering ({np.mean(m_only):.1f} tokens):

  Adding PREFIX filter: {prefix_reduction:+.1f}% additional reduction
  Adding SUFFIX filter: {suffix_reduction:+.1f}% additional reduction
  Adding BOTH:          {full_reduction:+.1f}% additional reduction
""")

# Step 6: Statistical significance of PREFIX/SUFFIX effects
print("=" * 70)
print("STATISTICAL TESTS")
print("=" * 70)

# Is PREFIX reduction significant?
t_prefix, p_prefix = stats.ttest_rel(m_only, mp)
t_suffix, p_suffix = stats.ttest_rel(m_only, ms)
t_full, p_full = stats.ttest_rel(m_only, full)

print(f"""
Paired t-tests (MIDDLE-only vs with additional filter):

  + PREFIX: t={t_prefix:.2f}, p={p_prefix:.4g} {'*' if p_prefix < 0.05 else ''}
  + SUFFIX: t={t_suffix:.2f}, p={p_suffix:.4g} {'*' if p_suffix < 0.05 else ''}
  + BOTH:   t={t_full:.2f}, p={p_full:.4g} {'*' if p_full < 0.05 else ''}
""")

# Step 7: Per-record breakdown
print("=" * 70)
print("PER-RECORD ANALYSIS")
print("=" * 70)

# How many records have zero reduction from PREFIX/SUFFIX?
no_prefix_reduction = sum(1 for i in range(len(m_only)) if mp[i] == m_only[i])
no_suffix_reduction = sum(1 for i in range(len(m_only)) if ms[i] == m_only[i])
no_full_reduction = sum(1 for i in range(len(m_only)) if full[i] == m_only[i])

print(f"""
Records with NO additional filtering:
  + PREFIX: {no_prefix_reduction} ({100*no_prefix_reduction/len(m_only):.1f}%)
  + SUFFIX: {no_suffix_reduction} ({100*no_suffix_reduction/len(m_only):.1f}%)
  + BOTH:   {no_full_reduction} ({100*no_full_reduction/len(m_only):.1f}%)
""")

# Step 8: Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
MIDDLE is the PRIMARY filter: {100*(1 - np.mean(m_only)/total_b):.1f}% of B vocabulary filtered

PREFIX adds: {prefix_reduction:.1f}% additional filtering (p={p_prefix:.4g})
SUFFIX adds: {suffix_reduction:.1f}% additional filtering (p={p_suffix:.4g})
BOTH add:    {full_reduction:.1f}% additional filtering

INTERPRETATION:
""")

if prefix_reduction > 5 or suffix_reduction > 5:
    print("""  PREFIX and/or SUFFIX provide meaningful additional filtering
  beyond MIDDLE alone. The morphological envelope matters.
""")
elif prefix_reduction > 0 or suffix_reduction > 0:
    print(f"""  PREFIX/SUFFIX provide statistically significant but SMALL
  additional filtering ({prefix_reduction:.1f}%/{suffix_reduction:.1f}%).
  MIDDLE does ~95% of the work; PREFIX/SUFFIX refine the edges.
""")
else:
    print("""  PREFIX and SUFFIX add NO filtering beyond MIDDLE.
  Once MIDDLE is matched, PREFIX/SUFFIX are always compatible.
""")
