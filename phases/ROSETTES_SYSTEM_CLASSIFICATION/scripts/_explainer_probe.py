#!/usr/bin/env python3
"""Probe: Is Rosettes explaining the manuscript's structure?"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, RosettesAnalyzer, BFolioDecoder

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()
decoder = BFolioDecoder()

# Load class map
CTM_PATH = ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
with open(CTM_PATH, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

# ============================================================
# 1. DOES ROSETTES SAMPLE ALL MACRO-STATES?
# ============================================================
print("=" * 65)
print("1. MACRO-STATE COVERAGE (is it sampling B's full grammar?)")
print("=" * 65)

# B corpus macro-state distribution
b_macro = Counter()
b_total = 0
for tok in tx.currier_b():
    if tok.folio in ra.ROSETTES_FOLIOS:
        continue
    cls = token_to_class.get(tok.word)
    if cls is not None:
        state = decoder.MACRO_STATE.get(str(cls))
        if state:
            b_macro[state] += 1
            b_total += 1

print("B corpus macro-state distribution:")
for state, count in b_macro.most_common():
    print(f"  {state:10s}: {count:>5} ({100*count/b_total:.1f}%)")

# Rosettes macro-state distribution
ros_macro = Counter()
ros_total = 0
for folio in ra.get_folios():
    for tok in ra.get_tokens(folio):
        cls = token_to_class.get(tok.word)
        if cls is not None:
            state = decoder.MACRO_STATE.get(str(cls))
            if state:
                ros_macro[state] += 1
                ros_total += 1

print(f"\nRosettes macro-state distribution ({ros_total} classified):")
for state in ['AXM', 'AXm', 'CC', 'FQ', 'FL_HAZ', 'FL_SAFE']:
    b_pct = 100 * b_macro.get(state, 0) / b_total if b_total else 0
    r_pct = 100 * ros_macro.get(state, 0) / ros_total if ros_total else 0
    print(f"  {state:10s}: B={b_pct:>5.1f}%  Ros={r_pct:>5.1f}%  {'PRESENT' if ros_macro.get(state,0) else 'ABSENT'}")

# How many of the 49 classes are represented?
ros_classes = set()
for folio in ra.get_folios():
    for tok in ra.get_tokens(folio):
        cls = token_to_class.get(tok.word)
        if cls is not None:
            ros_classes.add(cls)

print(f"\n49-class coverage: {len(ros_classes)}/49 classes represented in Rosettes")

# ============================================================
# 2. CURRIER A LINE STRUCTURE TRACES
# ============================================================
print("\n" + "=" * 65)
print("2. CURRIER A LINE STRUCTURE TRACES")
print("=" * 65)

# Line length distribution
print("\nLine length distribution by system:")
for system_name, tokens in [("B corpus", list(tx.currier_b())),
                              ("A corpus", list(tx.currier_a()))]:
    lines = defaultdict(int)
    for tok in tokens:
        if tok.folio not in ra.ROSETTES_FOLIOS:
            lines[(tok.folio, tok.line)] += 1
    lens = list(lines.values())
    len_dist = Counter(lens)
    single_token = len_dist.get(1, 0)
    total_lines = len(lens)
    mean_len = sum(lens) / len(lens) if lens else 0
    print(f"  {system_name}: mean={mean_len:.1f} tok/line, "
          f"1-token lines={single_token}/{total_lines} ({100*single_token/total_lines:.1f}%)")

# Rosettes line lengths
ros_lines = defaultdict(int)
for folio in ra.get_folios():
    for tok in ra.get_tokens(folio):
        ros_lines[(folio, tok.line)] += 1

ros_lens = list(ros_lines.values())
ros_len_dist = Counter(ros_lens)
ros_single = ros_len_dist.get(1, 0)
ros_mean = sum(ros_lens) / len(ros_lens) if ros_lens else 0
print(f"  Rosettes: mean={ros_mean:.1f} tok/line, "
      f"1-token lines={ros_single}/{len(ros_lens)} ({100*ros_single/len(ros_lens):.1f}%)")

# Per-folio breakdown
print(f"\nPer-folio line lengths:")
for folio in ra.get_folios():
    f_lines = {k: v for k, v in ros_lines.items() if k[0] == folio}
    f_lens = list(f_lines.values())
    if not f_lens:
        continue
    f_mean = sum(f_lens) / len(f_lens)
    f_single = sum(1 for l in f_lens if l == 1)
    f_max = max(f_lens)
    print(f"  {folio}: {len(f_lens)} lines, mean={f_mean:.1f}, "
          f"1-tok={f_single} ({100*f_single/len(f_lens):.0f}%), max={f_max}")

# f85v2 specifically
print(f"\nf85v2 line lengths per region:")
for region in ra.get_regions('f85v2'):
    toks = ra.get_tokens('f85v2', region)
    if not toks:
        continue
    r_lines = defaultdict(int)
    for tok in toks:
        r_lines[tok.line] += 1
    r_lens = list(r_lines.values())
    r_single = sum(1 for l in r_lens if l == 1)
    print(f"  {region:>3}: {len(r_lens)} lines, lengths={sorted(r_lens)}, "
          f"1-tok={r_single}")

# ============================================================
# 3. A-LIKE MORPHOLOGICAL SIGNATURES
# ============================================================
print("\n" + "=" * 65)
print("3. A-LIKE MORPHOLOGICAL SIGNATURES")
print("=" * 65)

# ct-prefix enrichment (C498: 5.1x in RI)
# da-prefix patterns
# Line-initial gallows (A trait)
a_prefixes = Counter()
for tok in tx.currier_a():
    m = morph.extract(tok.word)
    if m.prefix:
        a_prefixes[m.prefix] += 1
a_pre_total = sum(a_prefixes.values())

b_prefixes = Counter()
for tok in tx.currier_b():
    if tok.folio not in ra.ROSETTES_FOLIOS:
        m = morph.extract(tok.word)
        if m.prefix:
            b_prefixes[m.prefix] += 1
b_pre_total = sum(b_prefixes.values())

ros_prefixes = Counter()
for folio in ra.get_folios():
    for tok in ra.get_tokens(folio):
        m = morph.extract(tok.word)
        if m.prefix:
            ros_prefixes[m.prefix] += 1
ros_pre_total = sum(ros_prefixes.values())

print("Prefix distribution comparison (top 10):")
all_prefixes = sorted(set(list(a_prefixes.keys()) + list(b_prefixes.keys()) + list(ros_prefixes.keys())),
                       key=lambda p: ros_prefixes.get(p, 0), reverse=True)

print(f"{'Prefix':<8} {'A%':>6} {'B%':>6} {'Ros%':>6} {'Ros_closest':>12}")
print("-" * 45)
for p in all_prefixes[:15]:
    a_pct = 100 * a_prefixes.get(p, 0) / a_pre_total if a_pre_total else 0
    b_pct = 100 * b_prefixes.get(p, 0) / b_pre_total if b_pre_total else 0
    r_pct = 100 * ros_prefixes.get(p, 0) / ros_pre_total if ros_pre_total else 0
    closest = 'A' if abs(r_pct - a_pct) < abs(r_pct - b_pct) else 'B'
    print(f"{p:<8} {a_pct:>5.1f}% {b_pct:>5.1f}% {r_pct:>5.1f}% {closest:>12}")

# Count how many prefixes are closer to A vs B
a_closer = 0
b_closer = 0
for p in all_prefixes[:15]:
    a_pct = 100 * a_prefixes.get(p, 0) / a_pre_total if a_pre_total else 0
    b_pct = 100 * b_prefixes.get(p, 0) / b_pre_total if b_pre_total else 0
    r_pct = 100 * ros_prefixes.get(p, 0) / ros_pre_total if ros_pre_total else 0
    if abs(r_pct - a_pct) < abs(r_pct - b_pct):
        a_closer += 1
    else:
        b_closer += 1
print(f"\nRosettes prefix rates closer to: A={a_closer}, B={b_closer}")

# ============================================================
# 4. VOCABULARY COVERAGE — IS IT A MASTER INDEX?
# ============================================================
print("\n" + "=" * 65)
print("4. VOCABULARY COVERAGE — MASTER INDEX TEST")
print("=" * 65)

# How much of the manuscript's MIDDLE vocabulary does Rosettes cover?
all_b_middles = set()
for tok in tx.currier_b():
    if tok.folio not in ra.ROSETTES_FOLIOS:
        m = morph.extract(tok.word)
        if m.middle:
            all_b_middles.add(m.middle)

all_a_middles = set()
for tok in tx.currier_a():
    m = morph.extract(tok.word)
    if m.middle:
        all_a_middles.add(m.middle)

all_azc_middles = set()
for tok in tx.azc():
    m = morph.extract(tok.word)
    if m.middle:
        all_azc_middles.add(m.middle)

ros_middles = set()
for folio in ra.get_folios():
    for tok in ra.get_tokens(folio):
        m = morph.extract(tok.word)
        if m.middle:
            ros_middles.add(m.middle)

print(f"Total B MIDDLEs: {len(all_b_middles)}")
print(f"Total A MIDDLEs: {len(all_a_middles)}")
print(f"Total AZC MIDDLEs: {len(all_azc_middles)}")
print(f"Rosettes MIDDLEs: {len(ros_middles)}")
print()

b_covered = len(ros_middles & all_b_middles)
a_covered = len(ros_middles & all_a_middles)
azc_covered = len(ros_middles & all_azc_middles)

print(f"B vocabulary covered by Rosettes: {b_covered}/{len(all_b_middles)} ({100*b_covered/len(all_b_middles):.1f}%)")
print(f"A vocabulary covered by Rosettes: {a_covered}/{len(all_a_middles)} ({100*a_covered/len(all_a_middles):.1f}%)")
print(f"AZC vocabulary covered by Rosettes: {azc_covered}/{len(all_azc_middles)} ({100*azc_covered/len(all_azc_middles):.1f}%)")

# Coverage of CORE (high-frequency) vocabulary
# Core = appears in 20+ folios
mid_folio_counts = defaultdict(set)
for tok in tx.currier_b():
    m = morph.extract(tok.word)
    if m.middle:
        mid_folio_counts[m.middle].add(tok.folio)

core_middles = {m for m, folios in mid_folio_counts.items() if len(folios) >= 20}
core_covered = len(ros_middles & core_middles)
print(f"\nCore B MIDDLEs (20+ folios): {len(core_middles)}")
print(f"Core covered by Rosettes: {core_covered}/{len(core_middles)} ({100*core_covered/len(core_middles):.1f}%)")

# Hub MIDDLEs coverage (the 23 most structurally important)
hub_middles = set(decoder.HUB_SUB_ROLE.keys())
hub_covered = len(ros_middles & hub_middles)
print(f"\nHub MIDDLEs (C1000, 23 total): {hub_covered}/{len(hub_middles)} covered")
missing_hubs = hub_middles - ros_middles
if missing_hubs:
    print(f"  Missing: {sorted(missing_hubs)}")

# ============================================================
# 5. IS f85v2 EXPLAINING SYNTAX? (token role sampling)
# ============================================================
print("\n" + "=" * 65)
print("5. ROLE SAMPLING IN ROSETTES (explaining the grammar?)")
print("=" * 65)

# Check if Rosettes samples prefix roles, suffix roles, etc. more evenly
# than B corpus (which would be skewed by actual execution patterns)
ros_prefix_roles = Counter()
ros_suffix_roles = Counter()
ros_hub_roles = Counter()
for folio in ra.get_folios():
    for tok in ra.get_tokens(folio):
        analysis = decoder.analyze_token(tok.word)
        if analysis.prefix_role:
            ros_prefix_roles[analysis.prefix_role] += 1
        if analysis.suffix_role:
            ros_suffix_roles[analysis.suffix_role] += 1
        if analysis.hub_sub_role:
            ros_hub_roles[analysis.hub_sub_role] += 1

b_prefix_roles = Counter()
b_suffix_roles = Counter()
b_hub_roles = Counter()
# Sample ~2000 B tokens for comparison
import random
random.seed(42)
b_sample = random.sample(list(tx.currier_b()), min(2000, 21283))
for tok in b_sample:
    if tok.folio in ra.ROSETTES_FOLIOS:
        continue
    analysis = decoder.analyze_token(tok.word)
    if analysis.prefix_role:
        b_prefix_roles[analysis.prefix_role] += 1
    if analysis.suffix_role:
        b_suffix_roles[analysis.suffix_role] += 1
    if analysis.hub_sub_role:
        b_hub_roles[analysis.hub_sub_role] += 1

print("Prefix role distribution:")
all_roles = sorted(set(list(ros_prefix_roles.keys()) + list(b_prefix_roles.keys())))
ros_pr_total = sum(ros_prefix_roles.values())
b_pr_total = sum(b_prefix_roles.values())
for role in all_roles:
    r_pct = 100 * ros_prefix_roles.get(role, 0) / ros_pr_total if ros_pr_total else 0
    b_pct = 100 * b_prefix_roles.get(role, 0) / b_pr_total if b_pr_total else 0
    print(f"  {role:<20s}: B={b_pct:>5.1f}%  Ros={r_pct:>5.1f}%")

print(f"\nHub sub-role distribution:")
ros_hr_total = sum(ros_hub_roles.values())
b_hr_total = sum(b_hub_roles.values())
for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']:
    r_pct = 100 * ros_hub_roles.get(role, 0) / ros_hr_total if ros_hr_total else 0
    b_pct = 100 * b_hub_roles.get(role, 0) / b_hr_total if b_hr_total else 0
    print(f"  {role:<20s}: B={b_pct:>5.1f}%  Ros={r_pct:>5.1f}%")

# Evenness: compute entropy of role distributions
import math
def entropy(dist):
    total = sum(dist.values())
    if total == 0:
        return 0
    probs = [c/total for c in dist.values() if c > 0]
    return -sum(p * math.log2(p) for p in probs)

ros_macro_ent = entropy(ros_macro)
b_macro_ent = entropy(b_macro)
print(f"\nMacro-state entropy (higher = more even sampling):")
print(f"  B corpus: {b_macro_ent:.3f}")
print(f"  Rosettes: {ros_macro_ent:.3f}")
print(f"  {'Rosettes samples more evenly' if ros_macro_ent > b_macro_ent else 'B is more even'}")

ros_pr_ent = entropy(ros_prefix_roles)
b_pr_ent = entropy(b_prefix_roles)
print(f"\nPrefix role entropy:")
print(f"  B corpus: {b_pr_ent:.3f}")
print(f"  Rosettes: {ros_pr_ent:.3f}")
print(f"  {'Rosettes samples more evenly' if ros_pr_ent > b_pr_ent else 'B is more even'}")
