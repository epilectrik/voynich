"""
AZC CONSTRAINT SENSITIVITY TEST

Question: Do our key AZC findings change if we filter to R/C/S only
(excluding labels and OTHER placements)?

Tests key metrics that established C430-C436, C454-C456.
"""

import os
from collections import Counter, defaultdict
import numpy as np

os.chdir('C:/git/voynich')

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Get H-only AZC
all_azc = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if (row.get('transcriber', '').strip() == 'H' and
            row.get('language', '') == 'NA'):
            all_azc.append(row)

# Define filtered vs unfiltered
def is_rcs(row):
    """Ring, Circle, or Star placement."""
    p = row.get('placement', '')
    return p.startswith('R') or p.startswith('C') or p.startswith('S')

def is_not_label(row):
    """Not a label."""
    return not row.get('placement', '').startswith('L')

unfiltered = all_azc
no_labels = [r for r in all_azc if is_not_label(r)]
rcs_only = [r for r in all_azc if is_rcs(r)]

print("=" * 70)
print("AZC CONSTRAINT SENSITIVITY TEST")
print("=" * 70)

print(f"\n[Dataset Sizes]")
print(f"  Unfiltered: {len(unfiltered)} tokens")
print(f"  No labels:  {len(no_labels)} tokens ({100*(1-len(no_labels)/len(unfiltered)):.1f}% removed)")
print(f"  R/C/S only: {len(rcs_only)} tokens ({100*(1-len(rcs_only)/len(unfiltered)):.1f}% removed)")

# Test 1: Vocabulary size
print(f"\n[Test 1: Vocabulary Size]")
vocab_unfiltered = set(r['word'] for r in unfiltered)
vocab_no_labels = set(r['word'] for r in no_labels)
vocab_rcs = set(r['word'] for r in rcs_only)

print(f"  Unfiltered: {len(vocab_unfiltered)} types")
print(f"  No labels:  {len(vocab_no_labels)} types (lost {len(vocab_unfiltered - vocab_no_labels)})")
print(f"  R/C/S only: {len(vocab_rcs)} types (lost {len(vocab_unfiltered - vocab_rcs)})")

# Test 2: Placement distribution (key for C430-C436)
print(f"\n[Test 2: Placement Distribution (C430-C436 relevant)]")

def get_placement_dist(rows):
    """Get R/S series distribution."""
    placements = Counter(r.get('placement', '') for r in rows)
    r_series = sum(c for p, c in placements.items() if p.startswith('R'))
    s_series = sum(c for p, c in placements.items() if p.startswith('S'))
    c_series = sum(c for p, c in placements.items() if p.startswith('C'))
    return r_series, s_series, c_series

r_un, s_un, c_un = get_placement_dist(unfiltered)
r_nl, s_nl, c_nl = get_placement_dist(no_labels)
r_rcs, s_rcs, c_rcs = get_placement_dist(rcs_only)

print(f"  Unfiltered: R={r_un}, S={s_un}, C={c_un}")
print(f"  No labels:  R={r_nl}, S={s_nl}, C={c_nl}")
print(f"  R/C/S only: R={r_rcs}, S={s_rcs}, C={c_rcs}")
print(f"  -> R/C/S filtering removes only non-R/C/S content, structure unchanged")

# Test 3: Folio distribution (key for bifurcation C430)
print(f"\n[Test 3: Folio Distribution (C430 bifurcation)]")

def get_folio_dist(rows):
    """Get zodiac vs non-zodiac folio counts."""
    folios = Counter(r.get('folio', '') for r in rows)
    # Zodiac folios are f70v1, f70v2, f71r, f71v, f72r1, f72r2, f72r3, f72v1, f72v2, f72v3, f73r, f73v
    zodiac_prefixes = ['f70v', 'f71', 'f72', 'f73']
    zodiac = sum(c for f, c in folios.items() if any(f.startswith(p) for p in zodiac_prefixes))
    non_zodiac = sum(c for f, c in folios.items() if not any(f.startswith(p) for p in zodiac_prefixes))
    return zodiac, non_zodiac, len(folios)

z_un, nz_un, n_un = get_folio_dist(unfiltered)
z_nl, nz_nl, n_nl = get_folio_dist(no_labels)
z_rcs, nz_rcs, n_rcs = get_folio_dist(rcs_only)

print(f"  Unfiltered: Zodiac={z_un}, Non-zodiac={nz_un}, Folios={n_un}")
print(f"  No labels:  Zodiac={z_nl}, Non-zodiac={nz_nl}, Folios={n_nl}")
print(f"  R/C/S only: Zodiac={z_rcs}, Non-zodiac={nz_rcs}, Folios={n_rcs}")

# Test 4: Shared vocabulary with A and B
print(f"\n[Test 4: Cross-system Vocabulary Sharing (C301)]")

# Load A and B vocab
a_vocab = set()
b_vocab = set()
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if row.get('transcriber', '').strip() != 'H':
            continue
        if row.get('language', '') == 'A':
            a_vocab.add(row['word'])
        elif row.get('language', '') == 'B':
            b_vocab.add(row['word'])

def get_sharing(vocab):
    with_a = len(vocab & a_vocab) / len(vocab) * 100 if vocab else 0
    with_b = len(vocab & b_vocab) / len(vocab) * 100 if vocab else 0
    return with_a, with_b

a_un, b_un = get_sharing(vocab_unfiltered)
a_nl, b_nl = get_sharing(vocab_no_labels)
a_rcs, b_rcs = get_sharing(vocab_rcs)

print(f"  Unfiltered: A-sharing={a_un:.1f}%, B-sharing={b_un:.1f}%")
print(f"  No labels:  A-sharing={a_nl:.1f}%, B-sharing={b_nl:.1f}%")
print(f"  R/C/S only: A-sharing={a_rcs:.1f}%, B-sharing={b_rcs:.1f}%")

# Test 5: Self-transition rate (C433 zodiac block grammar)
print(f"\n[Test 5: Self-Transition Rate (C433)]")

def get_self_transition_rate(rows):
    """Calculate placement self-transition rate."""
    by_line = defaultdict(list)
    for r in rows:
        key = (r.get('folio', ''), r.get('line_number', ''))
        by_line[key].append(r)

    total = 0
    self_trans = 0
    for key, tokens in by_line.items():
        for i in range(len(tokens) - 1):
            p1 = tokens[i].get('placement', '')
            p2 = tokens[i+1].get('placement', '')
            if p1 and p2:
                total += 1
                if p1 == p2:
                    self_trans += 1
    return 100 * self_trans / total if total > 0 else 0

st_un = get_self_transition_rate(unfiltered)
st_nl = get_self_transition_rate(no_labels)
st_rcs = get_self_transition_rate(rcs_only)

print(f"  Unfiltered: {st_un:.1f}% self-transition")
print(f"  No labels:  {st_nl:.1f}% self-transition")
print(f"  R/C/S only: {st_rcs:.1f}% self-transition")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("\nKey metrics comparison:")
print(f"  {'Metric':<30} {'Unfiltered':<15} {'No Labels':<15} {'R/C/S Only':<15}")
print(f"  {'-'*75}")
print(f"  {'Token count':<30} {len(unfiltered):<15} {len(no_labels):<15} {len(rcs_only):<15}")
print(f"  {'Vocabulary':<30} {len(vocab_unfiltered):<15} {len(vocab_no_labels):<15} {len(vocab_rcs):<15}")
print(f"  {'A-sharing %':<30} {a_un:<15.1f} {a_nl:<15.1f} {a_rcs:<15.1f}")
print(f"  {'B-sharing %':<30} {b_un:<15.1f} {b_nl:<15.1f} {b_rcs:<15.1f}")
print(f"  {'Self-transition %':<30} {st_un:<15.1f} {st_nl:<15.1f} {st_rcs:<15.1f}")

# Verdict
print("\n[VERDICT]")
delta_vocab = abs(len(vocab_rcs) - len(vocab_unfiltered)) / len(vocab_unfiltered) * 100
delta_sharing = abs(a_rcs - a_un) + abs(b_rcs - b_un)
delta_st = abs(st_rcs - st_un)

if delta_vocab < 5 and delta_sharing < 5 and delta_st < 5:
    print("  Filtering impact: MINIMAL")
    print("  -> Key constraint metrics stable across filtering approaches")
    print("  -> Current analyses likely VALID")
else:
    print("  Filtering impact: SIGNIFICANT")
    print(f"  -> Vocabulary delta: {delta_vocab:.1f}%")
    print(f"  -> Sharing delta: {delta_sharing:.1f}%")
    print(f"  -> Self-transition delta: {delta_st:.1f}%")
    print("  -> Consider re-running key AZC analyses with R/C/S filter")
