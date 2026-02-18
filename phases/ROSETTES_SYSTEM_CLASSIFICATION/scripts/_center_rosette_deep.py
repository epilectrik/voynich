#!/usr/bin/env python3
"""Deep analysis of the CENTER rosette (C2) — the receiver."""
import sys
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import (Transcript, Morphology, RosettesAnalyzer,
                              BFolioDecoder)

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# ============================================================
# 1. FULL TOKEN SEQUENCE OF C2
# ============================================================
print("=" * 70)
print("CENTER ROSETTE (C2): FULL TOKEN ANALYSIS")
print("=" * 70)

c2_toks = ra.get_tokens('f85v2', 'C2')
print(f"Total tokens: {len(c2_toks)}")
print(f"Track: {c2_toks[0].transcriber if c2_toks else '?'}")
print()

for i, t in enumerate(c2_toks):
    m = morph.extract(t.word)
    a = decoder.analyze_token(t.word)
    hub = a.hub_sub_role or ''
    ms = a.macro_state or ''
    mk = a.middle_kernel or ''
    pr = a.prefix_role or ''
    sr = a.suffix_role or ''
    gloss = a.structural()
    print(f"  {i+1:>2}. {t.word:<18s} PRE={str(m.prefix):>5s} MID={str(m.middle):>8s} "
          f"SUF={str(m.suffix):>5s}  {hub:<18s} {ms:<8s} {mk}")

# ============================================================
# 2. HUB ROLE SEQUENCE — is there a narrative?
# ============================================================
print("\n" + "=" * 70)
print("HUB ROLE SEQUENCE (reading order)")
print("=" * 70)

role_seq = []
for t in c2_toks:
    a = decoder.analyze_token(t.word)
    role = a.hub_sub_role or 'UNKNOWN'
    role_seq.append(role)

for i, (t, role) in enumerate(zip(c2_toks, role_seq)):
    marker = ''
    if role == 'HAZARD_TARGET':
        marker = '  <<< TARGET'
    elif role == 'HAZARD_SOURCE':
        marker = '  >>> SOURCE'
    elif role == 'SAFETY_BUFFER':
        marker = '  ||| BUFFER'
    elif role == 'PURE_CONNECTOR':
        marker = '  --- CONNECT'
    print(f"  {i+1:>2}. {t.word:<18s} {role:<18s}{marker}")

# Count transitions
print(f"\nRole transitions in sequence:")
trans = Counter()
for i in range(len(role_seq)-1):
    pair = f"{role_seq[i]} -> {role_seq[i+1]}"
    trans[pair] += 1
for pair, count in trans.most_common():
    print(f"  {pair}: {count}")

# ============================================================
# 3. COMPARE C2 TO DESCRIPTION REGIONS (NORTH, VERT)
# ============================================================
print("\n" + "=" * 70)
print("CENTER vs PERIPHERAL DESCRIPTIONS")
print("=" * 70)

for region_name, region_ids in [('CENTER', ['C2']),
                                  ('NORTH', ['N1', 'N2']),
                                  ('VERT', ['V1', 'V2'])]:
    toks = []
    for r in region_ids:
        toks.extend(ra.get_tokens('f85v2', r))

    if not toks:
        continue

    hub_dist = Counter()
    macro_dist = Counter()
    kernel_chars = Counter()
    prefix_dist = Counter()
    suffix_dist = Counter()

    for t in toks:
        a = decoder.analyze_token(t.word)
        m = morph.extract(t.word)
        if a.hub_sub_role:
            hub_dist[a.hub_sub_role] += 1
        if a.macro_state:
            macro_dist[a.macro_state] += 1
        if a.middle_kernel:
            kernel_chars[a.middle_kernel] += 1
        if m.prefix:
            prefix_dist[m.prefix] += 1
        if m.suffix:
            suffix_dist[m.suffix] += 1

    total_hub = sum(hub_dist.values())
    src_pct = 100 * hub_dist.get('HAZARD_SOURCE', 0) / total_hub if total_hub else 0
    tgt_pct = 100 * hub_dist.get('HAZARD_TARGET', 0) / total_hub if total_hub else 0
    buf_pct = 100 * hub_dist.get('SAFETY_BUFFER', 0) / total_hub if total_hub else 0
    con_pct = 100 * hub_dist.get('PURE_CONNECTOR', 0) / total_hub if total_hub else 0

    # Source-to-target ratio (key metric)
    src_count = hub_dist.get('HAZARD_SOURCE', 0)
    tgt_count = hub_dist.get('HAZARD_TARGET', 0)
    st_ratio = src_count / tgt_count if tgt_count else float('inf')

    print(f"\n  {region_name} ({len(toks)} tokens):")
    print(f"    HUB: SRC={src_pct:.0f}% TGT={tgt_pct:.0f}% BUF={buf_pct:.0f}% CON={con_pct:.0f}%")
    print(f"    SOURCE:TARGET ratio = {st_ratio:.2f}  ({'SOURCE-dominant' if st_ratio > 1.2 else 'TARGET-dominant' if st_ratio < 0.8 else 'BALANCED'})")
    print(f"    Macro: {dict(macro_dist.most_common())}")
    print(f"    Kernels: {dict(kernel_chars.most_common())}")
    print(f"    Top prefixes: {dict(prefix_dist.most_common(5))}")
    print(f"    Top suffixes: {dict(suffix_dist.most_common(5))}")

# ============================================================
# 4. WHERE DO C2's MIDDLEs APPEAR IN THE MANUSCRIPT?
# ============================================================
print("\n" + "=" * 70)
print("C2 MIDDLE CROSS-REFERENCES")
print("=" * 70)

c2_middles = set()
for t in c2_toks:
    m = morph.extract(t.word)
    if m.middle:
        c2_middles.add(m.middle)

print(f"C2 contains {len(c2_middles)} unique MIDDLEs: {sorted(c2_middles)}")

# Find B sections where these MIDDLEs concentrate
mid_section = defaultdict(lambda: Counter())
for tok in tx.currier_b():
    if tok.folio in ra.ROSETTES_FOLIOS:
        continue
    m = morph.extract(tok.word)
    if m.middle in c2_middles:
        mid_section[m.middle][tok.section] += 1

print(f"\nC2 MIDDLE usage in B body text sections:")
for mid in sorted(c2_middles):
    usage = mid_section.get(mid, Counter())
    if usage:
        total = sum(usage.values())
        print(f"  {mid:<10s}: {total:>5} -> {dict(usage.most_common(3))}")
    else:
        print(f"  {mid:<10s}: NOT IN B BODY TEXT")

# ============================================================
# 5. C2 vs TYPICAL B PARAGRAPH — structural comparison
# ============================================================
print("\n" + "=" * 70)
print("C2 vs TYPICAL B PARAGRAPH (structural fingerprint)")
print("=" * 70)

# Pick a representative B paragraph for comparison
# Use f76r which is the top cross-referenced folio
f76r_toks = [t for t in tx.currier_b() if t.folio == 'f76r']
# Take first ~33 tokens to match C2 length
f76r_sample = f76r_toks[:33]

for name, toks_list in [('C2 (Center Rosette)', c2_toks),
                          ('f76r (top cross-ref, first 33)', f76r_sample)]:
    hub_d = Counter()
    macro_d = Counter()
    kern_d = Counter()
    for t in toks_list:
        a = decoder.analyze_token(t.word)
        if a.hub_sub_role:
            hub_d[a.hub_sub_role] += 1
        if a.macro_state:
            macro_d[a.macro_state] += 1
        if a.middle_kernel:
            kern_d[a.middle_kernel] += 1

    total = sum(hub_d.values())
    print(f"\n  {name}:")
    print(f"    Hub: {dict(hub_d.most_common())}")
    print(f"    Macro: {dict(macro_d.most_common())}")
    print(f"    Kernel: {dict(kern_d.most_common())}")
    if total:
        tgt = hub_d.get('HAZARD_TARGET', 0)
        src = hub_d.get('HAZARD_SOURCE', 0)
        print(f"    TARGET:SOURCE = {tgt}:{src}")

# ============================================================
# 6. TUBES/SPIKES: Do the label regions CONNECT to center?
# ============================================================
print("\n" + "=" * 70)
print("CONNECTIVITY: Do surrounding label MIDDLEs appear in C2?")
print("=" * 70)

# Get MIDDLEs from each surrounding label group
label_groups = {
    'BOTTOM': ['B1', 'B2', 'B3'],
    'MIDDLE': ['M1', 'M2'],
    'UPPER': ['U1', 'U2'],
    'D_W': ['W1'],
}

for gname, regions in label_groups.items():
    group_mids = set()
    for r in regions:
        for t in ra.get_tokens('f85v2', r):
            m = morph.extract(t.word)
            if m.middle:
                group_mids.add(m.middle)

    overlap = group_mids & c2_middles
    total_g = len(group_mids)

    print(f"\n  {gname} ({total_g} MIDDLEs) -> CENTER overlap: {len(overlap)}")
    if overlap:
        print(f"    Shared MIDDLEs: {sorted(overlap)}")
        for mid in sorted(overlap):
            # What role does this MIDDLE play in C2 vs in the label?
            c2_roles = []
            for t in c2_toks:
                m2 = morph.extract(t.word)
                if m2.middle == mid:
                    a = decoder.analyze_token(t.word)
                    c2_roles.append(a.hub_sub_role or 'UNKNOWN')

            label_roles = []
            for r in regions:
                for t in ra.get_tokens('f85v2', r):
                    m2 = morph.extract(t.word)
                    if m2.middle == mid:
                        a = decoder.analyze_token(t.word)
                        label_roles.append(a.hub_sub_role or 'UNKNOWN')

            print(f"      {mid}: in C2={c2_roles}, in {gname} labels={label_roles}")

# ============================================================
# 7. NORTH/VERT SOURCE -> CENTER TARGET flow?
# ============================================================
print("\n" + "=" * 70)
print("FLOW HYPOTHESIS: Do NORTH/VERT sources feed CENTER targets?")
print("=" * 70)

for desc_name, desc_regions in [('NORTH', ['N1', 'N2']), ('VERT', ['V1', 'V2'])]:
    desc_src_mids = set()
    desc_all_mids = set()
    for r in desc_regions:
        for t in ra.get_tokens('f85v2', r):
            m = morph.extract(t.word)
            a = decoder.analyze_token(t.word)
            if m.middle:
                desc_all_mids.add(m.middle)
                if a.hub_sub_role == 'HAZARD_SOURCE':
                    desc_src_mids.add(m.middle)

    c2_tgt_mids = set()
    for t in c2_toks:
        m = morph.extract(t.word)
        a = decoder.analyze_token(t.word)
        if m.middle and a.hub_sub_role == 'HAZARD_TARGET':
            c2_tgt_mids.add(m.middle)

    # Do the SOURCES in descriptions match TARGETS in center?
    src_to_tgt = desc_src_mids & c2_tgt_mids
    all_overlap = desc_all_mids & c2_middles

    print(f"\n  {desc_name}:")
    print(f"    Description SOURCE MIDDLEs: {sorted(desc_src_mids)}")
    print(f"    Center TARGET MIDDLEs: {sorted(c2_tgt_mids)}")
    print(f"    SOURCE->TARGET matches: {sorted(src_to_tgt)}")
    print(f"    Total MIDDLE overlap: {len(all_overlap)} ({sorted(all_overlap)})")
    if src_to_tgt:
        print(f"    ** FLOW CONFIRMED: {len(src_to_tgt)} MIDDLEs appear as SOURCE")
        print(f"       in {desc_name} and as TARGET in CENTER")
