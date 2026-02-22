#!/usr/bin/env python3
"""
Exploratory analysis: What MIDDLEs pair with ch vs sh prefixes in Currier B?

Examines:
  1. MIDDLE frequency under ch-prefix vs sh-prefix
  2. Atom-level composition of each MIDDLE (k, e, h, other)
  3. Overlap: ch-only, sh-only, shared MIDDLEs
  4. Top-20 MIDDLEs per prefix with atom breakdown
  5. Section stratification
  6. Folio kernel bias (k-biased vs e-biased) and MIDDLE selection
"""

import sys
from collections import Counter, defaultdict
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology


# ============================================================
# HELPERS
# ============================================================

def atom_counts(middle):
    """Count k, e, h, and other atoms in a MIDDLE string."""
    if not middle or middle == '_EMPTY_':
        return {'k': 0, 'e': 0, 'h': 0, 'other': 0}
    counts = {'k': 0, 'e': 0, 'h': 0, 'other': 0}
    for ch in middle:
        if ch == 'k':
            counts['k'] += 1
        elif ch == 'e':
            counts['e'] += 1
        elif ch == 'h':
            counts['h'] += 1
        else:
            counts['other'] += 1
    return counts


def atom_fraction(middle):
    """Return (k_frac, e_frac, h_frac) for a MIDDLE string."""
    c = atom_counts(middle)
    total = c['k'] + c['e'] + c['h'] + c['other']
    if total == 0:
        return (0.0, 0.0, 0.0)
    return (c['k'] / total, c['e'] / total, c['h'] / total)


def fmt_pct(n, total):
    """Format count as 'n (pct%)'."""
    if total == 0:
        return '%d (---)' % n
    return '%d (%.1f%%)' % (n, 100.0 * n / total)


# ============================================================
# LOAD DATA
# ============================================================
print('=' * 70)
print('CH vs SH PREFIX -- MIDDLE EXPLORATION (Currier B)')
print('=' * 70)

tx = Transcript()
morph = Morphology()

# Collect all B tokens with morphology
all_b = []
for token in tx.currier_b():
    m = morph.extract(token.word)
    all_b.append((token, m))

print('Total Currier B tokens (H, no labels, no uncertain): %d' % len(all_b))
print()

# ============================================================
# 1. FILTER TO ch/sh PREFIX TOKENS
# ============================================================
# A token qualifies if prefix == 'ch'/'sh' OR prefix2 == 'ch'/'sh'
ch_middles = []  # list of (middle, token) for ch-prefixed
sh_middles = []  # list of (middle, token) for sh-prefixed

for token, m in all_b:
    mid = m.middle
    if not mid or mid == '_EMPTY_':
        continue

    # Check primary prefix
    if m.prefix == 'ch':
        ch_middles.append((mid, token))
    elif m.prefix == 'sh':
        sh_middles.append((mid, token))

    # Check secondary prefix (prefix2) -- only if primary was not ch/sh
    if m.prefix2 == 'ch' and m.prefix != 'ch':
        ch_middles.append((mid, token))
    elif m.prefix2 == 'sh' and m.prefix != 'sh':
        sh_middles.append((mid, token))

print('Tokens with ch-prefix (primary or secondary): %d' % len(ch_middles))
print('Tokens with sh-prefix (primary or secondary): %d' % len(sh_middles))
print()

# ============================================================
# 2. MIDDLE FREQUENCY LISTS
# ============================================================
ch_counter = Counter(mid for mid, _ in ch_middles)
sh_counter = Counter(mid for mid, _ in sh_middles)

print('-' * 70)
print('TOP MIDDLEs UNDER ch-PREFIX (all, sorted by freq)')
print('-' * 70)
print('%-20s %8s  %s' % ('MIDDLE', 'Count', 'Atoms (chars)'))
for mid, cnt in ch_counter.most_common():
    ac = atom_counts(mid)
    print('%-20s %8d  k=%d e=%d h=%d other=%d  [%s]' % (
        mid, cnt, ac['k'], ac['e'], ac['h'], ac['other'],
        ' '.join(mid)
    ))
print('Distinct MIDDLEs under ch: %d' % len(ch_counter))
print()

print('-' * 70)
print('TOP MIDDLEs UNDER sh-PREFIX (all, sorted by freq)')
print('-' * 70)
print('%-20s %8s  %s' % ('MIDDLE', 'Count', 'Atoms (chars)'))
for mid, cnt in sh_counter.most_common():
    ac = atom_counts(mid)
    print('%-20s %8d  k=%d e=%d h=%d other=%d  [%s]' % (
        mid, cnt, ac['k'], ac['e'], ac['h'], ac['other'],
        ' '.join(mid)
    ))
print('Distinct MIDDLEs under sh: %d' % len(sh_counter))
print()

# ============================================================
# 3. POOL COMPARISON: ch-only, sh-only, shared
# ============================================================
ch_set = set(ch_counter.keys())
sh_set = set(sh_counter.keys())
shared = ch_set & sh_set
ch_only = ch_set - sh_set
sh_only = sh_set - ch_set

print('-' * 70)
print('MIDDLE POOL COMPARISON')
print('-' * 70)
print('ch-only MIDDLEs:  %d' % len(ch_only))
print('sh-only MIDDLEs:  %d' % len(sh_only))
print('Shared MIDDLEs:   %d' % len(shared))
print()

print('  ch-only (top 30 by freq):')
for mid in sorted(ch_only, key=lambda x: -ch_counter[x])[:30]:
    print('    %-20s  count=%d' % (mid, ch_counter[mid]))
print()

print('  sh-only (top 30 by freq):')
for mid in sorted(sh_only, key=lambda x: -sh_counter[x])[:30]:
    print('    %-20s  count=%d' % (mid, sh_counter[mid]))
print()

print('  Shared (top 30 by combined freq):')
for mid in sorted(shared, key=lambda x: -(ch_counter[x] + sh_counter[x]))[:30]:
    print('    %-20s  ch=%d  sh=%d  total=%d' % (
        mid, ch_counter[mid], sh_counter[mid],
        ch_counter[mid] + sh_counter[mid]
    ))
print()

# ============================================================
# 4. TOP-20 MIDDLEs WITH ATOM BREAKDOWN
# ============================================================
print('-' * 70)
print('TOP-20 MIDDLEs UNDER ch -- ATOM BREAKDOWN')
print('-' * 70)
print('%-20s %6s  %5s %5s %5s %5s' % ('MIDDLE', 'Count', 'k%', 'e%', 'h%', 'oth%'))
for mid, cnt in ch_counter.most_common(20):
    kf, ef, hf = atom_fraction(mid)
    of = 1.0 - kf - ef - hf
    print('%-20s %6d  %5.1f %5.1f %5.1f %5.1f' % (
        mid, cnt, 100*kf, 100*ef, 100*hf, 100*of
    ))
print()

print('-' * 70)
print('TOP-20 MIDDLEs UNDER sh -- ATOM BREAKDOWN')
print('-' * 70)
print('%-20s %6s  %5s %5s %5s %5s' % ('MIDDLE', 'Count', 'k%', 'e%', 'h%', 'oth%'))
for mid, cnt in sh_counter.most_common(20):
    kf, ef, hf = atom_fraction(mid)
    of = 1.0 - kf - ef - hf
    print('%-20s %6d  %5.1f %5.1f %5.1f %5.1f' % (
        mid, cnt, 100*kf, 100*ef, 100*hf, 100*of
    ))
print()

# ============================================================
# 5. AGGREGATE ATOM COMPOSITION PER PREFIX
# ============================================================
print('-' * 70)
print('AGGREGATE ATOM COMPOSITION')
print('-' * 70)

for label, middles_list in [('ch-prefix', ch_middles), ('sh-prefix', sh_middles)]:
    total_k, total_e, total_h, total_other = 0, 0, 0, 0
    for mid, _ in middles_list:
        ac = atom_counts(mid)
        total_k += ac['k']
        total_e += ac['e']
        total_h += ac['h']
        total_other += ac['other']
    grand = total_k + total_e + total_h + total_other
    if grand > 0:
        print('%s: k=%s  e=%s  h=%s  other=%s  (total atoms=%d)' % (
            label,
            fmt_pct(total_k, grand),
            fmt_pct(total_e, grand),
            fmt_pct(total_h, grand),
            fmt_pct(total_other, grand),
            grand
        ))
    else:
        print('%s: no atoms' % label)
print()

# ============================================================
# 6. SECTION STRATIFICATION
# ============================================================
print('-' * 70)
print('SECTION STRATIFICATION')
print('-' * 70)

# Gather by section
ch_by_section = defaultdict(Counter)
sh_by_section = defaultdict(Counter)

for mid, token in ch_middles:
    ch_by_section[token.section][mid] += 1

for mid, token in sh_middles:
    sh_by_section[token.section][mid] += 1

all_sections = sorted(set(list(ch_by_section.keys()) + list(sh_by_section.keys())))

for section in all_sections:
    ch_sec = ch_by_section[section]
    sh_sec = sh_by_section[section]
    ch_total = sum(ch_sec.values())
    sh_total = sum(sh_sec.values())
    print()
    print('  Section: %s  (ch=%d tokens, sh=%d tokens)' % (section, ch_total, sh_total))

    # Top-10 MIDDLEs per prefix in this section
    if ch_total > 0:
        print('    ch top-10: %s' % ', '.join(
            '%s(%d)' % (m, c) for m, c in ch_sec.most_common(10)
        ))
    if sh_total > 0:
        print('    sh top-10: %s' % ', '.join(
            '%s(%d)' % (m, c) for m, c in sh_sec.most_common(10)
        ))

    # Overlap in this section
    ch_s = set(ch_sec.keys())
    sh_s = set(sh_sec.keys())
    shared_s = ch_s & sh_s
    print('    ch-only=%d  sh-only=%d  shared=%d' % (
        len(ch_s - sh_s), len(sh_s - ch_s), len(shared_s)
    ))

print()

# ============================================================
# 7. FOLIO KERNEL BIAS STRATIFICATION
# ============================================================
print('-' * 70)
print('FOLIO KERNEL BIAS (k-biased vs e-biased)')
print('-' * 70)

# Step 1: Compute k-atom fraction and e-atom fraction per folio
# across ALL Currier B tokens (not just ch/sh)
folio_k_atoms = Counter()
folio_e_atoms = Counter()
folio_total_atoms = Counter()

for token, m in all_b:
    mid = m.middle
    if not mid or mid == '_EMPTY_':
        continue
    ac = atom_counts(mid)
    f = token.folio
    folio_k_atoms[f] += ac['k']
    folio_e_atoms[f] += ac['e']
    folio_total_atoms[f] += ac['k'] + ac['e'] + ac['h'] + ac['other']

# Classify folios
k_biased_folios = set()
e_biased_folios = set()
neutral_folios = set()

folio_bias = {}  # folio -> (k_frac, e_frac, bias_label)
for f in sorted(folio_total_atoms.keys()):
    total = folio_total_atoms[f]
    if total == 0:
        continue
    kf = folio_k_atoms[f] / total
    ef = folio_e_atoms[f] / total
    if kf > ef:
        k_biased_folios.add(f)
        folio_bias[f] = (kf, ef, 'k-biased')
    elif ef > kf:
        e_biased_folios.add(f)
        folio_bias[f] = (kf, ef, 'e-biased')
    else:
        neutral_folios.add(f)
        folio_bias[f] = (kf, ef, 'neutral')

print('k-biased folios: %d' % len(k_biased_folios))
print('e-biased folios: %d' % len(e_biased_folios))
print('neutral folios:  %d' % len(neutral_folios))
print()

# Show top/bottom folios by k-fraction
print('Most k-biased folios (top 10):')
for f in sorted(folio_bias.keys(), key=lambda x: -folio_bias[x][0])[:10]:
    kf, ef, label = folio_bias[f]
    print('  %8s  k=%.3f  e=%.3f  (%s)' % (f, kf, ef, label))
print()

print('Most e-biased folios (top 10):')
for f in sorted(folio_bias.keys(), key=lambda x: -folio_bias[x][1])[:10]:
    kf, ef, label = folio_bias[f]
    print('  %8s  k=%.3f  e=%.3f  (%s)' % (f, kf, ef, label))
print()

# Step 2: MIDDLE selection under ch/sh on k-biased vs e-biased folios
print('-' * 70)
print('CH/SH MIDDLE SELECTION BY FOLIO BIAS')
print('-' * 70)

for prefix_label, middles_list in [('ch', ch_middles), ('sh', sh_middles)]:
    k_mid_counter = Counter()
    e_mid_counter = Counter()
    k_total = 0
    e_total = 0

    k_atoms_agg = {'k': 0, 'e': 0, 'h': 0, 'other': 0}
    e_atoms_agg = {'k': 0, 'e': 0, 'h': 0, 'other': 0}

    for mid, token in middles_list:
        f = token.folio
        ac = atom_counts(mid)
        if f in k_biased_folios:
            k_mid_counter[mid] += 1
            k_total += 1
            for key in ac:
                k_atoms_agg[key] += ac[key]
        elif f in e_biased_folios:
            e_mid_counter[mid] += 1
            e_total += 1
            for key in ac:
                e_atoms_agg[key] += ac[key]

    print()
    print('  %s-prefix on k-biased folios: %d tokens, %d distinct MIDDLEs' % (
        prefix_label, k_total, len(k_mid_counter)
    ))
    k_grand = sum(k_atoms_agg.values())
    if k_grand > 0:
        print('    Atom composition: k=%s  e=%s  h=%s  other=%s' % (
            fmt_pct(k_atoms_agg['k'], k_grand),
            fmt_pct(k_atoms_agg['e'], k_grand),
            fmt_pct(k_atoms_agg['h'], k_grand),
            fmt_pct(k_atoms_agg['other'], k_grand),
        ))
    print('    Top-15 MIDDLEs: %s' % ', '.join(
        '%s(%d)' % (m, c) for m, c in k_mid_counter.most_common(15)
    ))

    print()
    print('  %s-prefix on e-biased folios: %d tokens, %d distinct MIDDLEs' % (
        prefix_label, e_total, len(e_mid_counter)
    ))
    e_grand = sum(e_atoms_agg.values())
    if e_grand > 0:
        print('    Atom composition: k=%s  e=%s  h=%s  other=%s' % (
            fmt_pct(e_atoms_agg['k'], e_grand),
            fmt_pct(e_atoms_agg['e'], e_grand),
            fmt_pct(e_atoms_agg['h'], e_grand),
            fmt_pct(e_atoms_agg['other'], e_grand),
        ))
    print('    Top-15 MIDDLEs: %s' % ', '.join(
        '%s(%d)' % (m, c) for m, c in e_mid_counter.most_common(15)
    ))

    # Pool comparison between k-biased and e-biased folios
    k_set = set(k_mid_counter.keys())
    e_set = set(e_mid_counter.keys())
    print()
    print('  %s-prefix pool overlap: k-only=%d  e-only=%d  shared=%d' % (
        prefix_label, len(k_set - e_set), len(e_set - k_set), len(k_set & e_set)
    ))

print()
print('=' * 70)
print('EXPLORATION COMPLETE')
print('=' * 70)
