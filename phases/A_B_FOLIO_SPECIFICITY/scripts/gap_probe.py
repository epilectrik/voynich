#!/usr/bin/env python3
"""
Probe the B-exclusive gap: 950 MIDDLEs in B that no A folio contains.
What are they? How frequent? Where do they appear? What do they do?
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, RecordAnalyzer

print("=" * 70)
print("Gap Probe: B-Exclusive MIDDLEs")
print("=" * 70)

tx = Transcript()
morph = Morphology()
analyzer = RecordAnalyzer()

morph_cache = {}
def get_morph(word):
    if word not in morph_cache:
        morph_cache[word] = morph.extract(word)
    return morph_cache[word]

# ============================================================
# Build inventories
# ============================================================
print("\n--- Building inventories ---")

# All PP MIDDLEs from A
a_folios = sorted(analyzer.get_folios())
all_pp_mids = set()
for fol in a_folios:
    records = analyzer.analyze_folio(fol)
    for rec in records:
        for t in rec.tokens:
            if t.is_pp and t.middle:
                all_pp_mids.add(t.middle)

# Also get ALL A MIDDLEs (including RI)
all_a_mids = set()
for fol in a_folios:
    records = analyzer.analyze_folio(fol)
    for rec in records:
        for t in rec.tokens:
            if t.middle:
                all_a_mids.add(t.middle)

print(f"PP MIDDLEs (A, shared with B): {len(all_pp_mids)}")
print(f"All A MIDDLEs (PP + RI): {len(all_a_mids)}")
print(f"RI-only MIDDLEs: {len(all_a_mids - all_pp_mids)}")

# All B MIDDLEs with full data
b_mid_data = defaultdict(lambda: {
    'tokens': set(),
    'folios': set(),
    'occurrences': 0,
    'lines': set(),
    'prefixes': set(),
    'suffixes': set(),
    'positions': [],  # within-line fractional position
})

b_folio_line_tokens = defaultdict(lambda: defaultdict(list))

for token in tx.currier_b():
    w = token.word
    m = get_morph(w)
    if not m.middle:
        continue
    mid = m.middle
    d = b_mid_data[mid]
    d['tokens'].add(w)
    d['folios'].add(token.folio)
    d['occurrences'] += 1
    d['lines'].add((token.folio, token.line))
    if m.prefix:
        d['prefixes'].add(m.prefix)
    if m.suffix:
        d['suffixes'].add(m.suffix)
    b_folio_line_tokens[token.folio][token.line].append((w, mid))

all_b_mids = set(b_mid_data.keys())
b_exclusive_mids = all_b_mids - all_pp_mids
b_shared_mids = all_b_mids & all_pp_mids

# Check: are any B-exclusive MIDDLEs actually RI MIDDLEs?
ri_mids = all_a_mids - all_pp_mids
b_excl_in_ri = b_exclusive_mids & ri_mids
b_excl_truly_exclusive = b_exclusive_mids - all_a_mids

print(f"\nAll B MIDDLEs: {len(all_b_mids)}")
print(f"Shared (PP): {len(b_shared_mids)}")
print(f"B-exclusive: {len(b_exclusive_mids)}")
print(f"  Of which also RI in A: {len(b_excl_in_ri)}")
print(f"  Of which truly B-only (not in A at all): {len(b_excl_truly_exclusive)}")

# ============================================================
# Q1: Frequency profile of B-exclusive vs shared MIDDLEs
# ============================================================
print("\n--- Q1: Frequency Profile ---")

excl_occ = sorted([b_mid_data[m]['occurrences'] for m in b_exclusive_mids], reverse=True)
shared_occ = sorted([b_mid_data[m]['occurrences'] for m in b_shared_mids], reverse=True)

print(f"\nB-exclusive MIDDLEs ({len(b_exclusive_mids)}):")
print(f"  Total occurrences: {sum(excl_occ)}")
print(f"  Mean: {np.mean(excl_occ):.1f}")
print(f"  Median: {np.median(excl_occ):.0f}")
print(f"  Max: {max(excl_occ)}")
print(f"  Singletons (1 occ): {sum(1 for x in excl_occ if x == 1)} ({sum(1 for x in excl_occ if x == 1)/len(excl_occ)*100:.1f}%)")
print(f"  <=5 occ: {sum(1 for x in excl_occ if x <= 5)} ({sum(1 for x in excl_occ if x <= 5)/len(excl_occ)*100:.1f}%)")
print(f"  >50 occ: {sum(1 for x in excl_occ if x > 50)} ({sum(1 for x in excl_occ if x > 50)/len(excl_occ)*100:.1f}%)")

print(f"\nShared MIDDLEs ({len(b_shared_mids)}):")
print(f"  Total occurrences: {sum(shared_occ)}")
print(f"  Mean: {np.mean(shared_occ):.1f}")
print(f"  Median: {np.median(shared_occ):.0f}")
print(f"  Max: {max(shared_occ)}")
print(f"  Singletons: {sum(1 for x in shared_occ if x == 1)} ({sum(1 for x in shared_occ if x == 1)/len(shared_occ)*100:.1f}%)")

# Top 20 most frequent B-exclusive MIDDLEs
print(f"\nTop 20 B-exclusive MIDDLEs:")
top_excl = sorted(b_exclusive_mids, key=lambda m: -b_mid_data[m]['occurrences'])[:20]
for mid in top_excl:
    d = b_mid_data[mid]
    example_toks = sorted(d['tokens'])[:5]
    in_ri = "RI" if mid in ri_mids else "B-only"
    print(f"  {mid:>12}: {d['occurrences']:>5} occ, {len(d['folios']):>3} folios, "
          f"{len(d['tokens']):>3} forms, [{in_ri}] e.g. {', '.join(example_toks)}")

# ============================================================
# Q2: Folio spread of B-exclusive MIDDLEs
# ============================================================
print("\n--- Q2: Folio Spread ---")

excl_folio_counts = [len(b_mid_data[m]['folios']) for m in b_exclusive_mids]
shared_folio_counts = [len(b_mid_data[m]['folios']) for m in b_shared_mids]

print(f"B-exclusive folio counts:")
print(f"  Mean: {np.mean(excl_folio_counts):.1f}")
print(f"  Median: {np.median(excl_folio_counts):.0f}")
print(f"  1 folio: {sum(1 for x in excl_folio_counts if x == 1)} ({sum(1 for x in excl_folio_counts if x == 1)/len(excl_folio_counts)*100:.1f}%)")
print(f"  2-5: {sum(1 for x in excl_folio_counts if 2 <= x <= 5)} ({sum(1 for x in excl_folio_counts if 2 <= x <= 5)/len(excl_folio_counts)*100:.1f}%)")
print(f"  6-20: {sum(1 for x in excl_folio_counts if 6 <= x <= 20)} ({sum(1 for x in excl_folio_counts if 6 <= x <= 20)/len(excl_folio_counts)*100:.1f}%)")
print(f"  21+: {sum(1 for x in excl_folio_counts if x >= 21)} ({sum(1 for x in excl_folio_counts if x >= 21)/len(excl_folio_counts)*100:.1f}%)")

print(f"\nShared folio counts (comparison):")
print(f"  Mean: {np.mean(shared_folio_counts):.1f}")
print(f"  Median: {np.median(shared_folio_counts):.0f}")

# ============================================================
# Q3: Morphological profile
# ============================================================
print("\n--- Q3: Morphological Profile ---")

# PREFIX usage
excl_prefix_counts = Counter()
shared_prefix_counts = Counter()
excl_no_prefix = 0
shared_no_prefix = 0

for token in tx.currier_b():
    m = get_morph(token.word)
    if not m.middle:
        continue
    if m.middle in b_exclusive_mids:
        if m.prefix:
            excl_prefix_counts[m.prefix] += 1
        else:
            excl_no_prefix += 1
    elif m.middle in b_shared_mids:
        if m.prefix:
            shared_prefix_counts[m.prefix] += 1
        else:
            shared_no_prefix += 1

total_excl_tokens = sum(excl_prefix_counts.values()) + excl_no_prefix
total_shared_tokens = sum(shared_prefix_counts.values()) + shared_no_prefix

print(f"PREFIX usage:")
print(f"  B-exclusive: {excl_no_prefix/total_excl_tokens*100:.1f}% no prefix")
print(f"  Shared: {shared_no_prefix/total_shared_tokens*100:.1f}% no prefix")

print(f"\n  Top PREFIXes in B-exclusive MIDDLEs:")
for pref, cnt in excl_prefix_counts.most_common(10):
    pct = cnt / total_excl_tokens * 100
    print(f"    {pref}: {cnt} ({pct:.1f}%)")

print(f"\n  Top PREFIXes in shared MIDDLEs:")
for pref, cnt in shared_prefix_counts.most_common(10):
    pct = cnt / total_shared_tokens * 100
    print(f"    {pref}: {cnt} ({pct:.1f}%)")

# SUFFIX usage
excl_suffix_counts = Counter()
shared_suffix_counts = Counter()
excl_no_suffix = 0
shared_no_suffix = 0

for token in tx.currier_b():
    m = get_morph(token.word)
    if not m.middle:
        continue
    if m.middle in b_exclusive_mids:
        if m.suffix:
            excl_suffix_counts[m.suffix] += 1
        else:
            excl_no_suffix += 1
    elif m.middle in b_shared_mids:
        if m.suffix:
            shared_suffix_counts[m.suffix] += 1
        else:
            shared_no_suffix += 1

print(f"\nSUFFIX usage:")
print(f"  B-exclusive: {excl_no_suffix/(sum(excl_suffix_counts.values()) + excl_no_suffix)*100:.1f}% no suffix")
print(f"  Shared: {shared_no_suffix/(sum(shared_suffix_counts.values()) + shared_no_suffix)*100:.1f}% no suffix")

# ============================================================
# Q4: MIDDLE length distribution
# ============================================================
print("\n--- Q4: MIDDLE Length ---")

excl_lengths = [len(m) for m in b_exclusive_mids]
shared_lengths = [len(m) for m in b_shared_mids]

print(f"B-exclusive MIDDLE lengths:")
print(f"  Mean: {np.mean(excl_lengths):.2f}")
print(f"  Median: {np.median(excl_lengths):.0f}")
for l in range(1, 8):
    n = sum(1 for x in excl_lengths if x == l)
    if n > 0:
        print(f"  Length {l}: {n} ({n/len(excl_lengths)*100:.1f}%)")

print(f"\nShared MIDDLE lengths:")
print(f"  Mean: {np.mean(shared_lengths):.2f}")
print(f"  Median: {np.median(shared_lengths):.0f}")
for l in range(1, 8):
    n = sum(1 for x in shared_lengths if x == l)
    if n > 0:
        print(f"  Length {l}: {n} ({n/len(shared_lengths)*100:.1f}%)")

# ============================================================
# Q5: Co-occurrence with shared MIDDLEs on same line
# ============================================================
print("\n--- Q5: Line Co-occurrence ---")

# When a B-exclusive MIDDLE appears on a line, what else is on that line?
lines_with_excl = 0
lines_with_only_excl = 0
lines_with_mixed = 0
total_b_lines = 0

for b_fol in b_folio_line_tokens:
    for line_key, tokens in b_folio_line_tokens[b_fol].items():
        total_b_lines += 1
        mids_on_line = [mid for _, mid in tokens]
        has_excl = any(m in b_exclusive_mids for m in mids_on_line)
        has_shared = any(m in b_shared_mids for m in mids_on_line)
        if has_excl:
            lines_with_excl += 1
            if has_shared:
                lines_with_mixed += 1
            else:
                lines_with_only_excl += 1

print(f"Total B lines: {total_b_lines}")
print(f"Lines with B-exclusive MIDDLE: {lines_with_excl} ({lines_with_excl/total_b_lines*100:.1f}%)")
print(f"  Mixed (both exclusive + shared): {lines_with_mixed} ({lines_with_mixed/total_b_lines*100:.1f}%)")
print(f"  Only exclusive: {lines_with_only_excl} ({lines_with_only_excl/total_b_lines*100:.1f}%)")

# Per-line: fraction of tokens with B-exclusive MIDDLEs
line_excl_fracs = []
for b_fol in b_folio_line_tokens:
    for line_key, tokens in b_folio_line_tokens[b_fol].items():
        mids = [mid for _, mid in tokens]
        if not mids:
            continue
        n_excl = sum(1 for m in mids if m in b_exclusive_mids)
        line_excl_fracs.append(n_excl / len(mids))

line_excl_fracs = np.array(line_excl_fracs)
print(f"\nPer-line B-exclusive fraction:")
print(f"  Mean: {np.mean(line_excl_fracs):.4f}")
print(f"  Median: {np.median(line_excl_fracs):.4f}")
print(f"  Lines with 0%: {np.sum(line_excl_fracs == 0)} ({np.sum(line_excl_fracs == 0)/len(line_excl_fracs)*100:.1f}%)")
print(f"  Lines with >50%: {np.sum(line_excl_fracs > 0.5)} ({np.sum(line_excl_fracs > 0.5)/len(line_excl_fracs)*100:.1f}%)")
print(f"  Lines with 100%: {np.sum(line_excl_fracs == 1.0)} ({np.sum(line_excl_fracs == 1.0)/len(line_excl_fracs)*100:.1f}%)")

# ============================================================
# Q6: Section distribution
# ============================================================
print("\n--- Q6: Section Distribution ---")

# Load section info from transcript
b_folio_sections = {}
for token in tx.currier_b():
    if token.folio not in b_folio_sections:
        b_folio_sections[token.folio] = token.section if hasattr(token, 'section') else 'unknown'

# Count B-exclusive MIDDLE occurrences by section
section_excl_occ = Counter()
section_shared_occ = Counter()
section_total_occ = Counter()

for token in tx.currier_b():
    m = get_morph(token.word)
    if not m.middle:
        continue
    sec = token.section if hasattr(token, 'section') else 'unknown'
    section_total_occ[sec] += 1
    if m.middle in b_exclusive_mids:
        section_excl_occ[sec] += 1
    elif m.middle in b_shared_mids:
        section_shared_occ[sec] += 1

print(f"\nB-exclusive fraction by section:")
for sec in sorted(section_total_occ.keys()):
    total = section_total_occ[sec]
    excl = section_excl_occ[sec]
    if total > 100:  # only substantial sections
        print(f"  {sec}: {excl}/{total} ({excl/total*100:.1f}%) B-exclusive")

# ============================================================
# Q7: Are B-exclusive MIDDLEs structured or noise?
# ============================================================
print("\n--- Q7: Structure Check ---")

# Character composition: do B-exclusive MIDDLEs use different characters?
excl_chars = Counter()
shared_chars = Counter()
for mid in b_exclusive_mids:
    for ch in mid:
        excl_chars[ch] += 1
for mid in b_shared_mids:
    for ch in mid:
        shared_chars[ch] += 1

# Normalize
total_excl_ch = sum(excl_chars.values())
total_shared_ch = sum(shared_chars.values())

all_chars = sorted(set(list(excl_chars.keys()) + list(shared_chars.keys())))
print(f"\nCharacter frequency (B-exclusive vs shared MIDDLEs):")
print(f"{'Char':<6} {'Excl%':>8} {'Shared%':>8} {'Ratio':>8}")
for ch in all_chars:
    e_pct = excl_chars[ch] / total_excl_ch * 100 if total_excl_ch > 0 else 0
    s_pct = shared_chars[ch] / total_shared_ch * 100 if total_shared_ch > 0 else 0
    ratio = e_pct / s_pct if s_pct > 0 else float('inf')
    if e_pct > 1 or s_pct > 1:
        print(f"  {ch:<6} {e_pct:>7.1f}% {s_pct:>7.1f}% {ratio:>7.2f}x")

# Token form diversity per MIDDLE
excl_forms = [len(b_mid_data[m]['tokens']) for m in b_exclusive_mids]
shared_forms = [len(b_mid_data[m]['tokens']) for m in b_shared_mids]

print(f"\nToken forms per MIDDLE:")
print(f"  B-exclusive: mean={np.mean(excl_forms):.2f}, median={np.median(excl_forms):.0f}")
print(f"  Shared: mean={np.mean(shared_forms):.2f}, median={np.median(shared_forms):.0f}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\nB has {len(all_b_mids)} MIDDLEs: {len(b_shared_mids)} shared with A (PP), {len(b_exclusive_mids)} B-exclusive")
print(f"  Of B-exclusive: {len(b_excl_in_ri)} also RI in A, {len(b_excl_truly_exclusive)} truly B-only")
print(f"\nB-exclusive MIDDLEs are:")
print(f"  Rare: median {np.median(excl_occ):.0f} occ (vs shared median {np.median(shared_occ):.0f})")
print(f"  Narrow: median {np.median(excl_folio_counts):.0f} folios (vs shared median {np.median(shared_folio_counts):.0f})")
print(f"  Short: mean length {np.mean(excl_lengths):.2f} (vs shared {np.mean(shared_lengths):.2f})")
print(f"  Low-diversity: median {np.median(excl_forms):.0f} forms (vs shared {np.median(shared_forms):.0f})")
print(f"\nOn lines:")
print(f"  {lines_with_excl/total_b_lines*100:.1f}% of lines have a B-exclusive token")
print(f"  {lines_with_only_excl/total_b_lines*100:.1f}% of lines are ALL B-exclusive")
print(f"  Mean per-line fraction: {np.mean(line_excl_fracs):.1%}")

print("\nDONE")
