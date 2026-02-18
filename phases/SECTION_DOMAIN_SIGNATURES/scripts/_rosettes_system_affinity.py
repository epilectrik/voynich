#!/usr/bin/env python3
"""Quick probe: Does Rosettes vocabulary show affinity with A, B, AZC, or HT?"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, RosettesAnalyzer
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()

# ============================================================
# 1. Build vocabulary sets for each system
# ============================================================
print("=" * 65)
print("SYSTEM VOCABULARY SETS")
print("=" * 65)

a_middles = set()
b_middles = set()  # non-Rosettes B only
azc_middles = set()
ros_middles = set()

# Currier A
for tok in tx.currier_a():
    m = morph.extract(tok.word)
    if m.middle:
        a_middles.add(m.middle)

# Currier B (excluding Rosettes)
for tok in tx.currier_b():
    if tok.folio not in ra.ROSETTES_FOLIOS:
        m = morph.extract(tok.word)
        if m.middle:
            b_middles.add(m.middle)

# AZC
for tok in tx.azc():
    m = morph.extract(tok.word)
    if m.middle:
        azc_middles.add(m.middle)

# Rosettes (all folios, best track)
for folio in ra.get_folios():
    for tok in ra.get_tokens(folio):
        m = morph.extract(tok.word)
        if m.middle:
            ros_middles.add(m.middle)

print(f"Currier A MIDDLEs:     {len(a_middles)}")
print(f"Currier B MIDDLEs:     {len(b_middles)} (excl Rosettes)")
print(f"AZC MIDDLEs:           {len(azc_middles)}")
print(f"Rosettes MIDDLEs:      {len(ros_middles)}")

# ============================================================
# 2. Overlap analysis
# ============================================================
print()
print("=" * 65)
print("ROSETTES VOCABULARY OVERLAP WITH EACH SYSTEM")
print("=" * 65)

for name, system_set in [("Currier A", a_middles), ("Currier B", b_middles), ("AZC", azc_middles)]:
    shared = ros_middles & system_set
    ros_only = ros_middles - system_set
    sys_only = system_set - ros_middles
    jaccard = len(shared) / len(ros_middles | system_set) if (ros_middles | system_set) else 0
    overlap_pct = 100 * len(shared) / len(ros_middles) if ros_middles else 0
    print(f"\n  Rosettes vs {name}:")
    print(f"    Shared:       {len(shared):>5} ({overlap_pct:.1f}% of Rosettes)")
    print(f"    Ros-only:     {len(ros_only):>5}")
    print(f"    {name[:5]}-only: {len(sys_only):>5}")
    print(f"    Jaccard:      {jaccard:.3f}")

# Rosettes MIDDLEs that appear in A but NOT in B
a_not_b = ros_middles & a_middles - b_middles
print(f"\n  Rosettes in A but NOT in B: {len(a_not_b)}")
if a_not_b:
    print(f"    {sorted(a_not_b)[:20]}")

# Rosettes MIDDLEs that appear in AZC but NOT in B
azc_not_b = ros_middles & azc_middles - b_middles
print(f"\n  Rosettes in AZC but NOT in B: {len(azc_not_b)}")
if azc_not_b:
    print(f"    {sorted(azc_not_b)[:20]}")

# Rosettes MIDDLEs in NONE of the other systems
nowhere_else = ros_middles - a_middles - b_middles - azc_middles
print(f"\n  Rosettes EXCLUSIVE (not in A, B, or AZC): {len(nowhere_else)}")
if nowhere_else:
    print(f"    {sorted(nowhere_else)[:30]}")

# ============================================================
# 3. Morphological profile comparison
# ============================================================
print()
print("=" * 65)
print("MORPHOLOGICAL PROFILE COMPARISON")
print("=" * 65)

def morph_profile(tokens):
    """Compute morphological stats for a token list."""
    n = 0
    prefixed = 0
    suffixed = 0
    articulated = 0
    middle_lens = []
    for tok in tokens:
        m = morph.extract(tok.word)
        if not m.middle:
            continue
        n += 1
        if m.prefix: prefixed += 1
        if m.suffix: suffixed += 1
        if m.articulator: articulated += 1
        middle_lens.append(len(m.middle))
    if n == 0:
        return None
    return {
        'n': n,
        'prefix_rate': 100 * prefixed / n,
        'suffix_rate': 100 * suffixed / n,
        'artic_rate': 100 * articulated / n,
        'mean_mid_len': sum(middle_lens) / len(middle_lens) if middle_lens else 0,
    }

# Build token lists
a_tokens = list(tx.currier_a())
b_tokens = [t for t in tx.currier_b() if t.folio not in ra.ROSETTES_FOLIOS]
azc_tokens = list(tx.azc())
ros_tokens = []
for folio in ra.get_folios():
    ros_tokens.extend(ra.get_tokens(folio))

print(f"\n{'System':<12} {'N':>6} {'Prefix%':>8} {'Suffix%':>8} {'Artic%':>8} {'MidLen':>7}")
print("-" * 55)
for name, toks in [("Currier A", a_tokens), ("Currier B", b_tokens),
                    ("AZC", azc_tokens), ("Rosettes", ros_tokens)]:
    p = morph_profile(toks)
    if p:
        print(f"{name:<12} {p['n']:>6} {p['prefix_rate']:>7.1f}% {p['suffix_rate']:>7.1f}% {p['artic_rate']:>7.1f}% {p['mean_mid_len']:>6.2f}")

# ============================================================
# 4. HT content in Rosettes
# ============================================================
print()
print("=" * 65)
print("HT TOKEN ANALYSIS IN ROSETTES")
print("=" * 65)

# C740/C747: HT tokens are compound-specified, cross-system
# Check for known HT indicators in Rosettes vocabulary
# HT tokens have compound MIDDLEs (C935) and specific prefixes
ht_indicators = {
    'compound_prefixes': ['qo', 'da', 'ol', 'ok', 'ot', 'ct'],
    'compound_suffixes': ['aiin', 'ain', 'oin', 'am'],
}

for folio in ra.get_folios():
    tokens = ra.get_tokens(folio)
    total = len(tokens)
    compound_count = 0
    prefix_dist = Counter()
    suffix_dist = Counter()

    for tok in tokens:
        m = morph.extract(tok.word)
        if m.prefix:
            prefix_dist[m.prefix] += 1
        if m.suffix:
            suffix_dist[m.suffix] += 1
        # Simple compound indicator: has both prefix and suffix
        if m.prefix and m.suffix:
            compound_count += 1

    compound_rate = 100 * compound_count / total if total else 0
    top_pre = prefix_dist.most_common(5)
    top_suf = suffix_dist.most_common(5)
    print(f"\n  {folio} ({total} tokens, compound_rate={compound_rate:.1f}%):")
    print(f"    Top prefixes: {top_pre}")
    print(f"    Top suffixes: {top_suf}")

# ============================================================
# 5. Per-region system affinity for f85v2
# ============================================================
print()
print("=" * 65)
print("f85v2 PER-REGION SYSTEM AFFINITY")
print("=" * 65)

fp = ra.profile_folio('f85v2')
for region in fp.regions:
    if region.token_count < 5:
        continue
    region_middles = set(region.middles)
    a_overlap = len(region_middles & a_middles)
    b_overlap = len(region_middles & b_middles)
    azc_overlap = len(region_middles & azc_middles)
    exclusive = len(region_middles - a_middles - b_middles - azc_middles)
    total = len(region_middles)

    # Which system does this region most resemble?
    max_overlap = max(a_overlap, b_overlap, azc_overlap)
    affinity = "A" if a_overlap == max_overlap else ("B" if b_overlap == max_overlap else "AZC")

    print(f"  {region.region:>3} ({total:>2} unique): "
          f"A={a_overlap:>2} B={b_overlap:>2} AZC={azc_overlap:>2} "
          f"excl={exclusive:>2}  affinity={affinity}")

# ============================================================
# 6. Prefix family comparison (A-like vs B-like)
# ============================================================
print()
print("=" * 65)
print("PREFIX FAMILY DISTRIBUTION")
print("=" * 65)

def prefix_dist(tokens):
    dist = Counter()
    for tok in tokens:
        m = morph.extract(tok.word)
        if m.prefix:
            dist[m.prefix] += 1
    total = sum(dist.values())
    return {k: 100*v/total for k, v in dist.most_common(10)} if total else {}

print("\nTop prefixes by system (% of prefixed tokens):")
for name, toks in [("Currier A", a_tokens), ("Currier B", b_tokens),
                    ("AZC", azc_tokens), ("Rosettes", ros_tokens)]:
    d = prefix_dist(toks)
    top5 = [(k, f"{v:.1f}%") for k, v in list(d.items())[:7]]
    print(f"  {name:<12}: {top5}")
