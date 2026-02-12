#!/usr/bin/env python3
"""Quick audit: what's in the 634 hapax blob? Are they A-rich but B-poor?"""

import sys, json, functools
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

tx = Transcript()
morph = Morphology()

# Count MIDDLEs in A vs B
a_freq = Counter()
a_ri_freq = Counter()  # RI = first token in line (proxy for record-initial)
a_pp_freq = Counter()  # PP = non-first position

for token in tx.currier_a():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    if m.middle:
        a_freq[m.middle] += 1
        if token.line_initial:
            a_ri_freq[m.middle] += 1
        else:
            a_pp_freq[m.middle] += 1

b_freq = Counter()
for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    if m.middle:
        b_freq[m.middle] += 1

# Load affordance table to get bin assignments
with open('data/middle_affordance_table.json') as f:
    table = json.load(f)

middles_data = table['middles']
all_middles = sorted(middles_data.keys())

print("=" * 70)
print("HAPAX AUDIT: What's in the 634-MIDDLE Bin 4?")
print("=" * 70)

# Categorize the 972 MIDDLEs
bin4 = [m for m in all_middles if middles_data[m].get('affordance_bin') == 4]
non_bin4 = [m for m in all_middles if middles_data[m].get('affordance_bin') != 4]

print(f"\nTotal MIDDLEs: {len(all_middles)}")
print(f"Bin 4 (BULK_OPERATIONAL): {len(bin4)}")
print(f"Other bins: {len(non_bin4)}")

# For bin 4: what's their A frequency?
print(f"\n{'=' * 70}")
print("Bin 4 MIDDLEs: A vs B frequency")
print("=" * 70)

b4_a_freq = [a_freq[m] for m in bin4]
b4_b_freq = [b_freq[m] for m in bin4]

print(f"\n  A frequency stats (Bin 4):")
print(f"    Mean: {sum(b4_a_freq)/len(b4_a_freq):.1f}")
print(f"    Median: {sorted(b4_a_freq)[len(b4_a_freq)//2]}")
print(f"    A freq >= 5: {sum(1 for f in b4_a_freq if f >= 5)} ({100*sum(1 for f in b4_a_freq if f >= 5)/len(bin4):.1f}%)")
print(f"    A freq >= 10: {sum(1 for f in b4_a_freq if f >= 10)} ({100*sum(1 for f in b4_a_freq if f >= 10)/len(bin4):.1f}%)")
print(f"    A freq >= 50: {sum(1 for f in b4_a_freq if f >= 50)} ({100*sum(1 for f in b4_a_freq if f >= 50)/len(bin4):.1f}%)")

print(f"\n  B frequency stats (Bin 4):")
print(f"    Mean: {sum(b4_b_freq)/len(b4_b_freq):.1f}")
print(f"    B freq == 0: {sum(1 for f in b4_b_freq if f == 0)} ({100*sum(1 for f in b4_b_freq if f == 0)/len(bin4):.1f}%)")
print(f"    B freq == 1: {sum(1 for f in b4_b_freq if f == 1)} ({100*sum(1 for f in b4_b_freq if f == 1)/len(bin4):.1f}%)")
print(f"    B freq >= 2: {sum(1 for f in b4_b_freq if f >= 2)} ({100*sum(1 for f in b4_b_freq if f >= 2)/len(bin4):.1f}%)")

# Cross-tab: A-rich but B-poor
print(f"\n{'=' * 70}")
print("Cross-tab: A frequency vs B frequency (Bin 4)")
print("=" * 70)

categories = {
    'A-rich, B-absent': [m for m in bin4 if a_freq[m] >= 5 and b_freq[m] == 0],
    'A-rich, B-hapax': [m for m in bin4 if a_freq[m] >= 5 and b_freq[m] == 1],
    'A-rich, B-present': [m for m in bin4 if a_freq[m] >= 5 and b_freq[m] >= 2],
    'A-moderate, B-poor': [m for m in bin4 if 2 <= a_freq[m] < 5 and b_freq[m] <= 1],
    'A-hapax, B-poor': [m for m in bin4 if a_freq[m] <= 1 and b_freq[m] <= 1],
}

for cat, middles in categories.items():
    print(f"\n  {cat}: {len(middles)}")
    if middles and len(middles) <= 15:
        for m in sorted(middles, key=lambda x: -a_freq[x])[:15]:
            print(f"    {m:>15} A={a_freq[m]:>4} B={b_freq[m]:>4}")
    elif middles:
        for m in sorted(middles, key=lambda x: -a_freq[x])[:10]:
            print(f"    {m:>15} A={a_freq[m]:>4} B={b_freq[m]:>4}")
        print(f"    ... and {len(middles) - 10} more")

# RI analysis
print(f"\n{'=' * 70}")
print("RI (Record-Initial) vs PP (Non-Initial) in A")
print("=" * 70)

ri_exclusive = [m for m in all_middles if a_ri_freq[m] > 0 and a_pp_freq[m] == 0]
pp_exclusive = [m for m in all_middles if a_pp_freq[m] > 0 and a_ri_freq[m] == 0]
both_pos = [m for m in all_middles if a_ri_freq[m] > 0 and a_pp_freq[m] > 0]
neither = [m for m in all_middles if a_ri_freq[m] == 0 and a_pp_freq[m] == 0]

print(f"\n  RI-exclusive: {len(ri_exclusive)} MIDDLEs (only appear line-initial in A)")
print(f"  PP-exclusive: {len(pp_exclusive)} MIDDLEs (never appear line-initial in A)")
print(f"  Both positions: {len(both_pos)} MIDDLEs")
print(f"  Neither (no A tokens): {len(neither)} MIDDLEs")

# RI-exclusive MIDDLEs: what bin are they in?
print(f"\n  RI-exclusive by affordance bin:")
ri_bins = Counter()
for m in ri_exclusive:
    b = middles_data[m].get('affordance_bin', -1)
    ri_bins[b] += 1
for b in sorted(ri_bins.keys()):
    label = middles_data[ri_exclusive[0]].get('affordance_label', '?') if b >= 0 else 'NONE'
    # Get label from metadata
    bin_meta = table['_metadata'].get('affordance_bins', {}).get(str(b), {})
    label = bin_meta.get('label', '?')
    print(f"    Bin {b} ({label}): {ri_bins[b]}")

# RI-exclusive MIDDLEs: B frequency?
print(f"\n  RI-exclusive MIDDLEs: B frequency distribution:")
ri_b_freqs = [b_freq[m] for m in ri_exclusive]
print(f"    B freq == 0: {sum(1 for f in ri_b_freqs if f == 0)}")
print(f"    B freq == 1: {sum(1 for f in ri_b_freqs if f == 1)}")
print(f"    B freq >= 2: {sum(1 for f in ri_b_freqs if f >= 2)}")
print(f"    B freq >= 10: {sum(1 for f in ri_b_freqs if f >= 10)}")

# Top RI-exclusive MIDDLEs
print(f"\n  Top 20 RI-exclusive MIDDLEs (by A frequency):")
for m in sorted(ri_exclusive, key=lambda x: -a_freq[x])[:20]:
    b = middles_data[m].get('affordance_bin', -1)
    bin_meta = table['_metadata'].get('affordance_bins', {}).get(str(b), {})
    label = bin_meta.get('label', '?')
    print(f"    {m:>15} A={a_freq[m]:>4} (RI={a_ri_freq[m]:>3}) B={b_freq[m]:>4} Bin={b} ({label})")

# PP-exclusive MIDDLEs that are B-shared
print(f"\n  Top 20 PP-exclusive MIDDLEs (by A frequency):")
for m in sorted(pp_exclusive, key=lambda x: -a_freq[x])[:20]:
    b_bin = middles_data[m].get('affordance_bin', -1)
    bin_meta = table['_metadata'].get('affordance_bins', {}).get(str(b_bin), {})
    label = bin_meta.get('label', '?')
    print(f"    {m:>15} A={a_freq[m]:>4} (PP={a_pp_freq[m]:>3}) B={b_freq[m]:>4} Bin={b_bin} ({label})")

# Summary: how much of Bin 4 could be rescued with A-context?
print(f"\n{'=' * 70}")
print("RESCUE POTENTIAL: How many Bin 4 MIDDLEs have A-context?")
print("=" * 70)

b4_with_a = [m for m in bin4 if a_freq[m] >= 3]
b4_with_ri = [m for m in bin4 if a_ri_freq[m] > 0]
b4_ri_exclusive = [m for m in bin4 if a_ri_freq[m] > 0 and a_pp_freq[m] == 0]
b4_no_a = [m for m in bin4 if a_freq[m] == 0]

print(f"\n  Bin 4 total: {len(bin4)}")
print(f"  With A freq >= 3: {len(b4_with_a)} ({100*len(b4_with_a)/len(bin4):.1f}%) — enough A-context to compute features")
print(f"  With any RI presence: {len(b4_with_ri)} ({100*len(b4_with_ri)/len(bin4):.1f}%)")
print(f"  RI-exclusive in A: {len(b4_ri_exclusive)} ({100*len(b4_ri_exclusive)/len(bin4):.1f}%)")
print(f"  No A tokens at all: {len(b4_no_a)} ({100*len(b4_no_a)/len(bin4):.1f}%)")

# RI ratio as a feature
print(f"\n{'=' * 70}")
print("RI RATIO: Fraction of A-occurrences at line-initial position")
print("=" * 70)

print(f"\n  {'MIDDLE':>15} {'A_freq':>8} {'RI_rate':>8} {'B_freq':>8} {'Bin':>5}")
print(f"  {'-'*50}")
for m in sorted([m for m in all_middles if a_freq[m] >= 10], key=lambda x: -a_ri_freq[x]/max(a_freq[x],1))[:30]:
    ri_rate = a_ri_freq[m] / a_freq[m] if a_freq[m] > 0 else 0
    b_bin = middles_data[m].get('affordance_bin', -1)
    print(f"  {m:>15} {a_freq[m]:>8} {ri_rate:>8.2f} {b_freq[m]:>8} {b_bin:>5}")
