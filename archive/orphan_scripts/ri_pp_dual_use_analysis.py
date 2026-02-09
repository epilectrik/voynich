#!/usr/bin/env python3
"""
RI-PP Dual-Use MIDDLE Analysis

Investigates why FINAL-RI + PP MIDDLEs have higher B survival
than INITIAL-RI + PP MIDDLEs.

Questions:
1. What are these dual-use MIDDLEs?
2. Do they have different morphological properties?
3. What PREFIX patterns are associated with each?
4. Is there a semantic pattern we can identify?
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
GALLOWS = {'k', 't', 'p', 'f'}

print("="*70)
print("RI-PP DUAL-USE MIDDLE ANALYSIS")
print("="*70)

# Build paragraph data
paragraphs = []
current_folio = None
current_para = []
current_line = None

for token in tx.currier_a():
    if '*' in token.word:
        continue
    if token.folio != current_folio:
        if current_para:
            paragraphs.append({'tokens': [t.word for t in current_para]})
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        continue
    if token.line != current_line:
        if token.word and token.word[0] in GALLOWS:
            paragraphs.append({'tokens': [t.word for t in current_para]})
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)
if current_para:
    paragraphs.append({'tokens': [t.word for t in current_para]})

# Collect MIDDLEs by zone with PREFIX info
initial_ri_data = defaultdict(lambda: {'count': 0, 'prefixes': Counter()})
final_ri_data = defaultdict(lambda: {'count': 0, 'prefixes': Counter()})
pp_data = defaultdict(lambda: {'count': 0, 'prefixes': Counter()})

for para in paragraphs:
    tokens = para['tokens']
    if len(tokens) < 4:
        continue

    # INITIAL RI = first 3
    for token in tokens[:3]:
        try:
            m = morph.extract(token)
            if m.middle:
                initial_ri_data[m.middle]['count'] += 1
                if m.prefix:
                    initial_ri_data[m.middle]['prefixes'][m.prefix] += 1
        except:
            pass

    # FINAL RI = last 3
    for token in tokens[-3:]:
        try:
            m = morph.extract(token)
            if m.middle:
                final_ri_data[m.middle]['count'] += 1
                if m.prefix:
                    final_ri_data[m.middle]['prefixes'][m.prefix] += 1
        except:
            pass

    # PP = middle zone
    if len(tokens) > 6:
        for token in tokens[3:-3]:
            try:
                m = morph.extract(token)
                if m.middle:
                    pp_data[m.middle]['count'] += 1
                    if m.prefix:
                        pp_data[m.middle]['prefixes'][m.prefix] += 1
            except:
                pass

initial_ri_middles = set(initial_ri_data.keys())
final_ri_middles = set(final_ri_data.keys())
pp_middles = set(pp_data.keys())

# Position-exclusive + PP intersection
initial_only = initial_ri_middles - final_ri_middles
final_only = final_ri_middles - initial_ri_middles

initial_only_in_pp = initial_only & pp_middles
final_only_in_pp = final_only & pp_middles

print(f"\nDual-use MIDDLEs (in both RI zone and PP):")
print(f"  INITIAL-only + PP: {len(initial_only_in_pp)}")
print(f"  FINAL-only + PP: {len(final_only_in_pp)}")

# B vocabulary
b_folio_middles = defaultdict(set)
b_middle_count = Counter()
for token in tx.currier_b():
    if '*' in token.word:
        continue
    try:
        m = morph.extract(token.word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)
            b_middle_count[m.middle] += 1
    except:
        pass

def b_survival_rate(middle):
    count = sum(1 for fv in b_folio_middles.values() if middle in fv)
    return count / len(b_folio_middles) if b_folio_middles else 0

# =========================================================================
# ANALYSIS 1: List the dual-use MIDDLEs with their B survival
# =========================================================================
print("\n" + "="*70)
print("ANALYSIS 1: DUAL-USE MIDDLES BY B SURVIVAL")
print("="*70)

print("\nFINAL-only + PP MIDDLEs (sorted by B survival):")
final_with_survival = [(m, b_survival_rate(m)) for m in final_only_in_pp]
final_with_survival.sort(key=lambda x: -x[1])

print(f"\n{'MIDDLE':<15} {'B Survival':<12} {'B Count':<10} {'PP Count':<10} {'FINAL Count':<12}")
print("-"*60)
for mid, surv in final_with_survival[:20]:
    b_count = b_middle_count.get(mid, 0)
    pp_count = pp_data[mid]['count']
    final_count = final_ri_data[mid]['count']
    print(f"{mid:<15} {surv*100:>6.1f}%      {b_count:<10} {pp_count:<10} {final_count:<12}")

print("\nINITIAL-only + PP MIDDLEs (sorted by B survival):")
initial_with_survival = [(m, b_survival_rate(m)) for m in initial_only_in_pp]
initial_with_survival.sort(key=lambda x: -x[1])

print(f"\n{'MIDDLE':<15} {'B Survival':<12} {'B Count':<10} {'PP Count':<10} {'INIT Count':<12}")
print("-"*60)
for mid, surv in initial_with_survival[:20]:
    b_count = b_middle_count.get(mid, 0)
    pp_count = pp_data[mid]['count']
    init_count = initial_ri_data[mid]['count']
    print(f"{mid:<15} {surv*100:>6.1f}%      {b_count:<10} {pp_count:<10} {init_count:<12}")

# =========================================================================
# ANALYSIS 2: PREFIX patterns in each group
# =========================================================================
print("\n" + "="*70)
print("ANALYSIS 2: PREFIX PATTERNS")
print("="*70)

def get_prefix_dist(middles, data_source):
    """Get aggregate PREFIX distribution for a set of MIDDLEs."""
    prefix_counts = Counter()
    for mid in middles:
        if mid in data_source:
            prefix_counts.update(data_source[mid]['prefixes'])
    return prefix_counts

# PREFIX distribution in PP zone for each group
final_pp_prefixes = get_prefix_dist(final_only_in_pp, pp_data)
initial_pp_prefixes = get_prefix_dist(initial_only_in_pp, pp_data)

print("\nPREFIX distribution in PP zone:")
print(f"\n{'PREFIX':<10} {'FINAL-only':<15} {'INITIAL-only':<15} {'Ratio':<10}")
print("-"*50)

all_prefixes = set(final_pp_prefixes.keys()) | set(initial_pp_prefixes.keys())
prefix_rows = []
for prefix in all_prefixes:
    f_count = final_pp_prefixes.get(prefix, 0)
    i_count = initial_pp_prefixes.get(prefix, 0)
    f_rate = f_count / sum(final_pp_prefixes.values()) if final_pp_prefixes else 0
    i_rate = i_count / sum(initial_pp_prefixes.values()) if initial_pp_prefixes else 0
    ratio = f_rate / i_rate if i_rate > 0 else float('inf')
    prefix_rows.append((prefix, f_count, i_count, f_rate, i_rate, ratio))

# Sort by ratio
prefix_rows.sort(key=lambda x: -x[5] if x[5] != float('inf') else 999)

for prefix, f_count, i_count, f_rate, i_rate, ratio in prefix_rows[:15]:
    ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
    print(f"{prefix:<10} {f_count:>5} ({f_rate*100:>5.1f}%)    {i_count:>5} ({i_rate*100:>5.1f}%)    {ratio_str}")

# =========================================================================
# ANALYSIS 3: MIDDLE length/complexity
# =========================================================================
print("\n" + "="*70)
print("ANALYSIS 3: MIDDLE COMPLEXITY")
print("="*70)

final_lengths = [len(m) for m in final_only_in_pp]
initial_lengths = [len(m) for m in initial_only_in_pp]

print(f"\nMIDDLE length (character count):")
print(f"  FINAL-only + PP: mean={np.mean(final_lengths):.2f}, median={np.median(final_lengths):.1f}")
print(f"  INITIAL-only + PP: mean={np.mean(initial_lengths):.2f}, median={np.median(initial_lengths):.1f}")

t_stat, p_val = stats.ttest_ind(final_lengths, initial_lengths)
print(f"  T-test: t={t_stat:.3f}, p={p_val:.4f}")

# =========================================================================
# ANALYSIS 4: High-B vs Low-B within each group
# =========================================================================
print("\n" + "="*70)
print("ANALYSIS 4: HIGH-B vs LOW-B CHARACTERISTICS")
print("="*70)

# Split FINAL-only+PP by median B survival
final_survivals = [b_survival_rate(m) for m in final_only_in_pp]
median_surv = np.median(final_survivals)

high_b_final = [m for m in final_only_in_pp if b_survival_rate(m) >= median_surv]
low_b_final = [m for m in final_only_in_pp if b_survival_rate(m) < median_surv]

print(f"\nWithin FINAL-only + PP:")
print(f"  High-B (>= median): {len(high_b_final)} MIDDLEs")
print(f"  Low-B (< median): {len(low_b_final)} MIDDLEs")

# What distinguishes high-B from low-B?
high_b_prefixes = get_prefix_dist(high_b_final, pp_data)
low_b_prefixes = get_prefix_dist(low_b_final, pp_data)

print(f"\nPREFIX enrichment in High-B vs Low-B (FINAL-only+PP):")
for prefix in ['ch', 'sh', 'qo', 'ok', 'ct', 'da', 'ol', 'or']:
    high_rate = high_b_prefixes.get(prefix, 0) / sum(high_b_prefixes.values()) if high_b_prefixes else 0
    low_rate = low_b_prefixes.get(prefix, 0) / sum(low_b_prefixes.values()) if low_b_prefixes else 0
    ratio = high_rate / low_rate if low_rate > 0 else float('inf')
    ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
    print(f"  {prefix}: High-B={high_rate*100:.1f}%, Low-B={low_rate*100:.1f}%, ratio={ratio_str}")

# =========================================================================
# ANALYSIS 5: Specific MIDDLEs driving the effect
# =========================================================================
print("\n" + "="*70)
print("ANALYSIS 5: TOP CONTRIBUTORS TO THE EFFECT")
print("="*70)

# Which specific MIDDLEs contribute most to the FINAL > INITIAL difference?
# Weight by both frequency and B-survival differential

print("\nTop FINAL-only+PP MIDDLEs by B impact (survival * PP_count):")
final_impact = [(m, b_survival_rate(m) * pp_data[m]['count']) for m in final_only_in_pp]
final_impact.sort(key=lambda x: -x[1])

for mid, impact in final_impact[:10]:
    surv = b_survival_rate(m)
    pp_count = pp_data[mid]['count']
    print(f"  {mid}: survival={b_survival_rate(mid)*100:.1f}%, PP_count={pp_count}, impact={impact:.1f}")

print("\nTop INITIAL-only+PP MIDDLEs by B impact:")
initial_impact = [(m, b_survival_rate(m) * pp_data[m]['count']) for m in initial_only_in_pp]
initial_impact.sort(key=lambda x: -x[1])

for mid, impact in initial_impact[:10]:
    surv = b_survival_rate(mid)
    pp_count = pp_data[mid]['count']
    print(f"  {mid}: survival={b_survival_rate(mid)*100:.1f}%, PP_count={pp_count}, impact={impact:.1f}")

# =========================================================================
# SUMMARY
# =========================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print("""
This analysis examines WHY FINAL-only+PP MIDDLEs have higher B survival
than INITIAL-only+PP MIDDLEs.

Possible explanations:
1. FINAL-position MIDDLEs have different PREFIX associations
2. FINAL-position MIDDLEs are structurally simpler/more common
3. The effect is driven by a few high-impact MIDDLEs
4. There's a genuine functional difference (outputs vs inputs)
""")
