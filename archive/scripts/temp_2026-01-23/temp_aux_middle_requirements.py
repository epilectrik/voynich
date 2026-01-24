#!/usr/bin/env python3
"""
Map vulnerable AUXILIARY classes to required A-record MIDDLE signatures.

Question: What MIDDLEs make infrastructure instantiable?

For each AUXILIARY class, identify:
1. Which MIDDLEs it requires (from class_to_middles)
2. How common those MIDDLEs are across A records
3. Why some classes are vulnerable (28%) vs robust (100%)
"""

import json
from collections import defaultdict

# Load class mapping
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_map = json.load(f)

class_to_role = class_map['class_to_role']
class_to_middles = class_map['class_to_middles']

# Load A record survivors
with open('phases/CLASS_COSURVIVAL_TEST/results/a_record_survivors.json') as f:
    survivors_data = json.load(f)

class_survival_rates = survivors_data['class_survival_rates']
records = survivors_data['records']

# Identify AUXILIARY classes
aux_classes = [int(c) for c, role in class_to_role.items() if role == 'AUXILIARY']
aux_classes.sort()

print("="*70)
print("AUXILIARY CLASS MIDDLE REQUIREMENTS")
print("="*70)

# For each AUXILIARY class, show its MIDDLEs and survival rate
print("\nClass | Survival | MIDDLEs Required")
print("-"*70)

aux_data = []
for cls in aux_classes:
    middles = class_to_middles.get(str(cls), [])
    survival = class_survival_rates.get(str(cls), 0)
    aux_data.append({
        'class': cls,
        'survival': survival,
        'middles': middles,
        'n_middles': len(middles)
    })

# Sort by survival rate
aux_data.sort(key=lambda x: x['survival'])

for d in aux_data:
    middles_str = ', '.join(d['middles'][:8])
    if len(d['middles']) > 8:
        middles_str += f" (+{len(d['middles'])-8} more)"
    print(f"  {d['class']:2d}  |  {d['survival']*100:5.1f}%  | {middles_str}")

# ============================================================
# ANALYSIS: Count MIDDLE frequency across A records
# ============================================================
print("\n" + "="*70)
print("MIDDLE FREQUENCY ACROSS A RECORDS")
print("="*70)

# Count how many A records contain each MIDDLE
middle_frequency = defaultdict(int)
for rec in records:
    for m in rec['a_middles']:
        middle_frequency[m] += 1

n_records = len(records)

# Collect all MIDDLEs used by AUXILIARY classes
all_aux_middles = set()
for cls in aux_classes:
    middles = class_to_middles.get(str(cls), [])
    all_aux_middles.update(middles)

print(f"\nTotal unique MIDDLEs in AUXILIARY classes: {len(all_aux_middles)}")

# Categorize MIDDLEs by frequency
universal = []  # >95% of A records
common = []     # 50-95%
uncommon = []   # 10-50%
rare = []       # <10%

for m in all_aux_middles:
    freq = middle_frequency[m] / n_records
    if freq > 0.95:
        universal.append((m, freq))
    elif freq > 0.50:
        common.append((m, freq))
    elif freq > 0.10:
        uncommon.append((m, freq))
    else:
        rare.append((m, freq))

print(f"\nUniversal MIDDLEs (>95%): {len(universal)}")
for m, f in sorted(universal, key=lambda x: -x[1])[:10]:
    print(f"  '{m}': {f*100:.1f}%")

print(f"\nCommon MIDDLEs (50-95%): {len(common)}")
for m, f in sorted(common, key=lambda x: -x[1])[:10]:
    print(f"  '{m}': {f*100:.1f}%")

print(f"\nUncommon MIDDLEs (10-50%): {len(uncommon)}")
for m, f in sorted(uncommon, key=lambda x: -x[1])[:10]:
    print(f"  '{m}': {f*100:.1f}%")

print(f"\nRare MIDDLEs (<10%): {len(rare)}")
for m, f in sorted(rare, key=lambda x: -x[1])[:10]:
    print(f"  '{m}': {f*100:.1f}%")

# ============================================================
# ANALYSIS: Why are some AUXILIARY classes vulnerable?
# ============================================================
print("\n" + "="*70)
print("WHY VULNERABLE? MIDDLE RARITY ANALYSIS")
print("="*70)

print("\nFor each AUXILIARY class: max MIDDLE frequency determines survival ceiling")

for d in aux_data:
    cls = d['class']
    middles = d['middles']
    survival = d['survival']

    if not middles:
        # Atomic class (no MIDDLE)
        print(f"\nClass {cls:2d} (survival={survival*100:.1f}%): ATOMIC (no MIDDLE)")
        continue

    # Find the most common MIDDLE for this class
    middle_freqs = [(m, middle_frequency[m]/n_records) for m in middles]
    middle_freqs.sort(key=lambda x: -x[1])

    max_middle, max_freq = middle_freqs[0]
    min_middle, min_freq = middle_freqs[-1]

    # The class survives if ANY of its MIDDLEs is present
    # So survival ≈ max(middle_frequencies) for well-distributed MIDDLEs

    print(f"\nClass {cls:2d} (survival={survival*100:.1f}%):")
    print(f"  MIDDLEs ({len(middles)}): {', '.join(middles)}")
    print(f"  Most common: '{max_middle}' ({max_freq*100:.1f}%)")
    print(f"  Least common: '{min_middle}' ({min_freq*100:.1f}%)")

    # Check if survival matches expectation
    # Class survives if at least one MIDDLE is in A record
    expected_survival = 0
    for rec in records:
        if any(m in rec['a_middles'] for m in middles):
            expected_survival += 1
    expected_survival /= n_records

    print(f"  Expected survival (any MIDDLE match): {expected_survival*100:.1f}%")
    print(f"  Actual survival: {survival*100:.1f}%")
    diff = abs(expected_survival - survival)
    if diff > 0.01:
        print(f"  ** GAP: {diff*100:.1f}% **")

# ============================================================
# SUMMARY: What makes AUXILIARY classes vulnerable?
# ============================================================
print("\n" + "="*70)
print("SUMMARY: INSTANTIABILITY REQUIREMENTS")
print("="*70)

vulnerable = [d for d in aux_data if d['survival'] < 0.5]
robust = [d for d in aux_data if d['survival'] >= 0.9]

print(f"\nVULNERABLE AUXILIARY (survival < 50%): {len(vulnerable)} classes")
for d in vulnerable:
    middles = d['middles']
    if middles:
        freqs = [middle_frequency[m]/n_records for m in middles]
        max_freq = max(freqs)
        print(f"  Class {d['class']:2d}: {d['survival']*100:.1f}% survival, best MIDDLE at {max_freq*100:.1f}%")
    else:
        print(f"  Class {d['class']:2d}: {d['survival']*100:.1f}% survival, ATOMIC")

print(f"\nROBUST AUXILIARY (survival >= 90%): {len(robust)} classes")
for d in robust:
    middles = d['middles']
    if middles:
        freqs = [middle_frequency[m]/n_records for m in middles]
        max_freq = max(freqs)
        print(f"  Class {d['class']:2d}: {d['survival']*100:.1f}% survival, best MIDDLE at {max_freq*100:.1f}%")
    else:
        print(f"  Class {d['class']:2d}: {d['survival']*100:.1f}% survival, ATOMIC")

# ============================================================
# KEY INSIGHT: Survival tracks max(MIDDLE frequency)
# ============================================================
print("\n" + "="*70)
print("KEY INSIGHT: SURVIVAL vs MAX MIDDLE FREQUENCY")
print("="*70)

print("\nClass | Survival | Max MIDDLE Freq | MIDDLE")
print("-"*50)

correlations = []
for d in aux_data:
    middles = d['middles']
    if middles:
        middle_freqs = [(m, middle_frequency[m]/n_records) for m in middles]
        middle_freqs.sort(key=lambda x: -x[1])
        max_middle, max_freq = middle_freqs[0]
        correlations.append((d['survival'], max_freq))
        print(f"  {d['class']:2d}  |  {d['survival']*100:5.1f}%  |     {max_freq*100:5.1f}%     | '{max_middle}'")
    else:
        print(f"  {d['class']:2d}  |  {d['survival']*100:5.1f}%  |     N/A       | (atomic)")

# Compute correlation
if correlations:
    import numpy as np
    surv = [c[0] for c in correlations]
    maxf = [c[1] for c in correlations]
    corr = np.corrcoef(surv, maxf)[0,1]
    print(f"\nCorrelation(survival, max_middle_freq) = {corr:.3f}")
