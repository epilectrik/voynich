"""P-R9: Lines with ar should have higher k-kernel content than lines with or.

If r = "reifen" (ripen/mature):
- ar = material ripeness in hazardous flow -> thermal processing context -> high k-kernel
- or = vessel cycle complete -> administrative checkpoint -> h-dominant or neutral

Also test: what is the full kernel profile on ar-lines vs or-lines?
"""

import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology


tx = Transcript()
morph = Morphology()

# ============================================================
# Build per-line token data
# ============================================================
print("Building per-line token data...")

line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    line_tokens[(token.folio, token.line)].append(w)

print(f"  Total lines: {len(line_tokens)}")

# ============================================================
# P-R9a: k-kernel fraction on ar-lines vs or-lines
# ============================================================
print(f"\n{'='*70}")
print("P-R9a: KERNEL PROFILE ON ar-LINES vs or-LINES")
print(f"{'='*70}")
print("Prediction: k-kernel higher on ar-lines, h-kernel higher on or-lines\n")

# Classify lines by whether they contain ar, or, both, or neither
ar_lines = set()
or_lines = set()

for line_key, words in line_tokens.items():
    for w in words:
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue
        if mid == 'ar':
            ar_lines.add(line_key)
        elif mid == 'or':
            or_lines.add(line_key)

ar_only = ar_lines - or_lines
or_only = or_lines - ar_lines
both = ar_lines & or_lines
neither = set(line_tokens.keys()) - ar_lines - or_lines

print(f"  ar-only lines: {len(ar_only)}")
print(f"  or-only lines: {len(or_only)}")
print(f"  both: {len(both)}")
print(f"  neither: {len(neither)}")

# Compute kernel atom fractions for each line set
kernel_atoms = {'k', 'e', 'h'}

def kernel_profile(line_set):
    counts = defaultdict(int)
    total_mid = 0
    for lk in line_set:
        for w in line_tokens[lk]:
            mid = morph.extract(w).middle
            if not mid or len(mid) < 2:
                continue
            # Skip the ar/or token itself
            if mid in ('ar', 'or'):
                continue
            total_mid += 1
            for atom in mid:
                if atom in kernel_atoms:
                    counts[atom] += 1
    return counts, total_mid

ar_kcounts, ar_total = kernel_profile(ar_only)
or_kcounts, or_total = kernel_profile(or_only)
neither_kcounts, neither_total = kernel_profile(neither)

print(f"\n  {'Kernel':<8s} {'ar-lines':>10s} {'or-lines':>10s} {'neither':>10s}")
print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10}")

for atom in ['k', 'e', 'h']:
    ar_pct = ar_kcounts[atom] / ar_total * 100 if ar_total > 0 else 0
    or_pct = or_kcounts[atom] / or_total * 100 if or_total > 0 else 0
    ne_pct = neither_kcounts[atom] / neither_total * 100 if neither_total > 0 else 0
    print(f"  {atom:<8s} {ar_pct:>9.2f}% {or_pct:>9.2f}% {ne_pct:>9.2f}%")

# Total kernel
ar_ktotal = sum(ar_kcounts[a] for a in kernel_atoms) / ar_total * 100 if ar_total > 0 else 0
or_ktotal = sum(or_kcounts[a] for a in kernel_atoms) / or_total * 100 if or_total > 0 else 0
ne_ktotal = sum(neither_kcounts[a] for a in kernel_atoms) / neither_total * 100 if neither_total > 0 else 0
print(f"  {'TOTAL':<8s} {ar_ktotal:>9.2f}% {or_ktotal:>9.2f}% {ne_ktotal:>9.2f}%")

# ============================================================
# P-R9b: FULL atom profile on ar-lines vs or-lines
# ============================================================
print(f"\n{'='*70}")
print("P-R9b: FULL ATOM PROFILE ON ar-LINES vs or-LINES")
print(f"{'='*70}")

def full_atom_profile(line_set):
    counts = defaultdict(int)
    total = 0
    for lk in line_set:
        for w in line_tokens[lk]:
            mid = morph.extract(w).middle
            if not mid or len(mid) < 2:
                continue
            if mid in ('ar', 'or'):
                continue
            for atom in mid:
                counts[atom] += 1
                total += 1
    return counts, total

ar_atoms, ar_atotal = full_atom_profile(ar_only)
or_atoms, or_atotal = full_atom_profile(or_only)

print(f"\n  {'Atom':<5s} {'ar-line%':>10s} {'or-line%':>10s} {'ratio':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*10} {'-'*8}")

atom_ratios = []
all_atoms = sorted(set(list(ar_atoms.keys()) + list(or_atoms.keys())))
for atom in all_atoms:
    ar_pct = ar_atoms[atom] / ar_atotal * 100 if ar_atotal > 0 else 0
    or_pct = or_atoms[atom] / or_atotal * 100 if or_atotal > 0 else 0
    ratio = ar_pct / or_pct if or_pct > 0 else 999
    atom_ratios.append((atom, ar_pct, or_pct, ratio))

atom_ratios.sort(key=lambda x: -x[3])
for atom, ar_pct, or_pct, ratio in atom_ratios:
    marker = ''
    if atom == 'k': marker = ' <-- HEAT'
    elif atom == 'e': marker = ' <-- COOL'
    elif atom == 'h': marker = ' <-- WATCH'
    elif atom == 'l': marker = ' <-- STATE'
    elif atom == 'n': marker = ' <-- SEAL'
    print(f"  {atom:<5s} {ar_pct:>9.2f}% {or_pct:>9.2f}% {ratio:>7.3f}x{marker}")

# ============================================================
# P-R9c: ar vs or -- INITIAL ATOM of neighboring tokens
# ============================================================
print(f"\n{'='*70}")
print("P-R9c: WHAT TOKENS NEIGHBOR ar vs or?")
print(f"{'='*70}")
print("Token immediately BEFORE and AFTER ar vs or\n")

before_ar = Counter()
after_ar = Counter()
before_or = Counter()
after_or = Counter()
ar_count = 0
or_count = 0

for line_key, words in line_tokens.items():
    for i, w in enumerate(words):
        mid = morph.extract(w).middle
        if not mid or len(mid) < 2:
            continue

        if mid == 'ar':
            ar_count += 1
            if i > 0:
                prev_mid = morph.extract(words[i-1]).middle
                if prev_mid and len(prev_mid) >= 2:
                    before_ar[prev_mid[-1]] += 1  # terminal of prev
            if i < len(words) - 1:
                next_mid = morph.extract(words[i+1]).middle
                if next_mid and len(next_mid) >= 2:
                    after_ar[next_mid[0]] += 1  # initial of next

        elif mid == 'or':
            or_count += 1
            if i > 0:
                prev_mid = morph.extract(words[i-1]).middle
                if prev_mid and len(prev_mid) >= 2:
                    before_or[prev_mid[-1]] += 1
            if i < len(words) - 1:
                next_mid = morph.extract(words[i+1]).middle
                if next_mid and len(next_mid) >= 2:
                    after_or[next_mid[0]] += 1

print(f"  ar tokens: {ar_count}, or tokens: {or_count}\n")

# Before
print(f"  Terminal BEFORE:")
print(f"  {'Atom':<5s} {'before ar':>10s} {'before or':>10s} {'ar%':>8s} {'or%':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*10} {'-'*8} {'-'*8}")

ar_before_total = sum(before_ar.values())
or_before_total = sum(before_or.values())

all_before = sorted(set(list(before_ar.keys()) + list(before_or.keys())))
for atom in all_before:
    arc = before_ar.get(atom, 0)
    orc = before_or.get(atom, 0)
    ar_pct = arc / ar_before_total * 100 if ar_before_total > 0 else 0
    or_pct = orc / or_before_total * 100 if or_before_total > 0 else 0
    print(f"  {atom:<5s} {arc:>10d} {orc:>10d} {ar_pct:>7.1f}% {or_pct:>7.1f}%")

# After
print(f"\n  Initial AFTER:")
print(f"  {'Atom':<5s} {'after ar':>10s} {'after or':>10s} {'ar%':>8s} {'or%':>8s}")
print(f"  {'-'*5} {'-'*10} {'-'*10} {'-'*8} {'-'*8}")

ar_after_total = sum(after_ar.values())
or_after_total = sum(after_or.values())

all_after = sorted(set(list(after_ar.keys()) + list(after_or.keys())))
for atom in all_after:
    arc = after_ar.get(atom, 0)
    orc = after_or.get(atom, 0)
    ar_pct = arc / ar_after_total * 100 if ar_after_total > 0 else 0
    or_pct = orc / or_after_total * 100 if or_after_total > 0 else 0
    print(f"  {atom:<5s} {arc:>10d} {orc:>10d} {ar_pct:>7.1f}% {or_pct:>7.1f}%")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("P-R9 SUMMARY")
print(f"{'='*70}")

k_ar = ar_kcounts['k'] / ar_total * 100 if ar_total > 0 else 0
k_or = or_kcounts['k'] / or_total * 100 if or_total > 0 else 0
h_ar = ar_kcounts['h'] / ar_total * 100 if ar_total > 0 else 0
h_or = or_kcounts['h'] / or_total * 100 if or_total > 0 else 0

print(f"\n  k-kernel on ar-lines: {k_ar:.2f}%")
print(f"  k-kernel on or-lines: {k_or:.2f}%")
print(f"  Delta: {k_ar - k_or:+.2f}pp")

print(f"\n  h-kernel on ar-lines: {h_ar:.2f}%")
print(f"  h-kernel on or-lines: {h_or:.2f}%")
print(f"  Delta: {h_ar - h_or:+.2f}pp")

if k_ar > k_or + 5:
    print(f"\n  SUPPORTS: k-kernel higher on ar-lines")
elif k_ar > k_or:
    print(f"\n  PARTIAL: k-kernel slightly higher on ar-lines ({k_ar - k_or:+.2f}pp)")
else:
    print(f"\n  DOES NOT SUPPORT: k-kernel not higher on ar-lines")
