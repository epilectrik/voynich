#!/usr/bin/env python3
"""
Phase 388H: ROSETTES_METALAYER_MAPPING

The Rosettes foldout is a hybrid structure that draws vocabulary from
A, B, and AZC while maintaining 79 exclusive MIDDLEs. Phase 387 showed
it respects B grammar (forbidden transitions) but doesn't fully operate
under it (depleted LINK, low kernel density, lowest bigram reuse).

Hypothesis: Rosettes is a META-LAYER — an organizational structure
that sits above A/B/AZC, indexing and cross-referencing the body text.

This phase tests:
  T1: Region-to-section vocabulary correlation (table of contents test)
  T2: AZC-to-B gradient mapping across the foldout
  T3: Exclusive vocabulary characterization (organizational labels?)
  T4: Cross-reference density (do rare MIDDLEs link rosettes to specific folios?)
  T5: Structural role classification per region
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, RosettesAnalyzer

# ============================================================
# SETUP
# ============================================================
print("=" * 65)
print("Phase 388H: ROSETTES_METALAYER_MAPPING")
print("=" * 65)

tx = Transcript()
morph = Morphology()
ra = RosettesAnalyzer()

# Pre-compute section vocabularies (H-track B folios, non-Rosettes)
print("\nPre-computing section vocabularies...")

SECTION_MAP = {}  # folio -> section
SECTION_FOLIOS = defaultdict(list)
SECTION_MIDDLES = defaultdict(set)
SECTION_MIDDLE_COUNTS = defaultdict(lambda: Counter())
FOLIO_MIDDLES = defaultdict(set)

for tok in tx.currier_b():
    if tok.folio in ra.ROSETTES_FOLIOS:
        continue
    SECTION_MAP[tok.folio] = tok.section
    m = morph.extract(tok.word)
    if m.middle:
        SECTION_MIDDLES[tok.section].add(m.middle)
        SECTION_MIDDLE_COUNTS[tok.section][m.middle] += 1
        FOLIO_MIDDLES[tok.folio].add(m.middle)
    if tok.folio not in SECTION_FOLIOS[tok.section]:
        SECTION_FOLIOS[tok.section].append(tok.folio)

for sec, folios in sorted(SECTION_FOLIOS.items()):
    print(f"  Section {sec}: {len(folios)} folios, {len(SECTION_MIDDLES[sec])} MIDDLEs")

# A vocabulary
A_MIDDLES = set()
A_MIDDLE_COUNTS = Counter()
for tok in tx.currier_a():
    m = morph.extract(tok.word)
    if m.middle:
        A_MIDDLES.add(m.middle)
        A_MIDDLE_COUNTS[m.middle] += 1
print(f"  Currier A: {len(A_MIDDLES)} MIDDLEs")

# AZC vocabulary
AZC_MIDDLES = set()
AZC_MIDDLE_COUNTS = Counter()
for tok in tx.azc():
    m = morph.extract(tok.word)
    if m.middle:
        AZC_MIDDLES.add(m.middle)
        AZC_MIDDLE_COUNTS[m.middle] += 1
print(f"  AZC: {len(AZC_MIDDLES)} MIDDLEs")

# Rosettes per-folio and per-region vocabularies
ROS_FOLIO_MIDDLES = {}
ROS_REGION_MIDDLES = {}
ROS_REGION_TOKENS = {}
ALL_B_MIDDLES = set()
for sec_middles in SECTION_MIDDLES.values():
    ALL_B_MIDDLES.update(sec_middles)

for folio in ra.get_folios():
    folio_middles = set()
    for tok in ra.get_tokens(folio):
        m = morph.extract(tok.word)
        if m.middle:
            folio_middles.add(m.middle)
    ROS_FOLIO_MIDDLES[folio] = folio_middles

    for region in ra.get_regions(folio):
        key = (folio, region)
        region_middles = set()
        region_toks = ra.get_tokens(folio, region)
        for tok in region_toks:
            m = morph.extract(tok.word)
            if m.middle:
                region_middles.add(m.middle)
        ROS_REGION_MIDDLES[key] = region_middles
        ROS_REGION_TOKENS[key] = region_toks

# All Rosettes MIDDLEs
ALL_ROS_MIDDLES = set()
for v in ROS_FOLIO_MIDDLES.values():
    ALL_ROS_MIDDLES.update(v)

results = {
    'phase': '388H',
    'name': 'ROSETTES_METALAYER_MAPPING',
    'test_count': 5,
    'verdicts': {},
}


# ============================================================
# T1: REGION-TO-SECTION VOCABULARY CORRELATION
# ============================================================
print("\n" + "=" * 65)
print("T1: REGION-TO-SECTION VOCABULARY CORRELATION")
print("=" * 65)
print("Testing: Do rosette regions share vocabulary preferentially")
print("with specific manuscript sections?")

# For each Rosettes folio, compute Jaccard with each section
print(f"\n{'Folio':<8}", end="")
sections = sorted(SECTION_MIDDLES.keys())
for s in sections:
    print(f"  {s:>6}", end="")
print(f"  {'A':>6}  {'AZC':>6}  best_sec  best_J")
print("-" * 85)

t1_data = {}
for folio in ra.get_folios():
    fmid = ROS_FOLIO_MIDDLES[folio]
    if not fmid:
        continue
    row = {}
    print(f"{folio:<8}", end="")
    best_sec = None
    best_j = -1
    for sec in sections:
        smid = SECTION_MIDDLES[sec]
        j = len(fmid & smid) / len(fmid | smid) if (fmid | smid) else 0
        row[sec] = round(j, 3)
        print(f"  {j:>6.3f}", end="")
        if j > best_j:
            best_j = j
            best_sec = sec

    # Also compare to A and AZC
    j_a = len(fmid & A_MIDDLES) / len(fmid | A_MIDDLES) if (fmid | A_MIDDLES) else 0
    j_azc = len(fmid & AZC_MIDDLES) / len(fmid | AZC_MIDDLES) if (fmid | AZC_MIDDLES) else 0
    row['A'] = round(j_a, 3)
    row['AZC'] = round(j_azc, 3)
    row['best_section'] = best_sec
    row['best_jaccard'] = round(best_j, 3)
    print(f"  {j_a:>6.3f}  {j_azc:>6.3f}  {best_sec:>8}  {best_j:.3f}")
    t1_data[folio] = row

# Per-REGION analysis for f85v2 (the 9-diagram page)
print(f"\nf85v2 per-region section correlation (regions with 5+ MIDDLEs):")
print(f"{'Region':<8}", end="")
for s in sections:
    print(f"  {s:>6}", end="")
print(f"  {'A':>6}  {'AZC':>6}  best")
print("-" * 80)

t1_regions = {}
for region in ra.get_regions('f85v2'):
    key = ('f85v2', region)
    rmid = ROS_REGION_MIDDLES.get(key, set())
    if len(rmid) < 5:
        continue
    print(f"{region:<8}", end="")
    best_sec = None
    best_j = -1
    rdata = {}
    for sec in sections:
        smid = SECTION_MIDDLES[sec]
        j = len(rmid & smid) / len(rmid | smid) if (rmid | smid) else 0
        rdata[sec] = round(j, 3)
        print(f"  {j:>6.3f}", end="")
        if j > best_j:
            best_j = j
            best_sec = sec
    j_a = len(rmid & A_MIDDLES) / len(rmid | A_MIDDLES) if (rmid | A_MIDDLES) else 0
    j_azc = len(rmid & AZC_MIDDLES) / len(rmid | AZC_MIDDLES) if (rmid | AZC_MIDDLES) else 0
    rdata['A'] = round(j_a, 3)
    rdata['AZC'] = round(j_azc, 3)
    rdata['best'] = best_sec
    print(f"  {j_a:>6.3f}  {j_azc:>6.3f}  {best_sec}")
    t1_regions[region] = rdata

# Do different regions point to different sections?
best_sections = [d['best'] for d in t1_regions.values() if 'best' in d]
unique_targets = set(best_sections)
print(f"\nf85v2 regions point to {len(unique_targets)} unique sections: {sorted(unique_targets)}")

if len(unique_targets) > 1:
    t1_verdict = 'MULTI_SECTION_MAPPING'
elif len(unique_targets) == 1:
    t1_verdict = f'SINGLE_SECTION_{list(unique_targets)[0]}'
else:
    t1_verdict = 'NO_CLEAR_MAPPING'

print(f"VERDICT: {t1_verdict}")
results['verdicts']['T1_section_correlation'] = t1_verdict
results['T1_data'] = {'per_folio': t1_data, 'f85v2_regions': t1_regions}


# ============================================================
# T2: AZC-TO-B GRADIENT MAPPING
# ============================================================
print("\n" + "=" * 65)
print("T2: AZC-TO-B GRADIENT MAPPING")
print("=" * 65)
print("Mapping the transition from AZC-like to B-like across the foldout.")

LINK_PREFIXES = {'lk', 'lo'}

def system_profile(tokens):
    """Compute multi-dimensional system affinity profile."""
    if not tokens:
        return None
    prefix_counts = Counter()
    link_count = 0
    kernel_chars = 0
    total_middle_chars = 0
    middles_with_kernel = 0
    total_middles = 0

    for tok in tokens:
        m = morph.extract(tok.word)
        if m.prefix:
            prefix_counts[m.prefix] += 1
            if m.prefix in LINK_PREFIXES:
                link_count += 1
        if m.middle:
            total_middles += 1
            kc = sum(1 for c in m.middle if c in 'khe')
            if kc > 0:
                middles_with_kernel += 1
            kernel_chars += kc
            total_middle_chars += len(m.middle)

    ok_ot = prefix_counts.get('ok', 0) + prefix_counts.get('ot', 0)
    qo_ch = prefix_counts.get('qo', 0) + prefix_counts.get('ch', 0)

    return {
        'n_tokens': len(tokens),
        'link_density': link_count / len(tokens) if tokens else 0,
        'kernel_middle_rate': middles_with_kernel / total_middles if total_middles else 0,
        'kernel_char_density': kernel_chars / total_middle_chars if total_middle_chars else 0,
        'ok_ot': ok_ot,
        'qo_ch': qo_ch,
        'prefix_ratio': ok_ot / qo_ch if qo_ch else float('inf'),
        'top_prefixes': prefix_counts.most_common(5),
    }

# Per-folio gradient
print(f"\n{'Folio':<8} {'Tok':>4} {'LINK%':>7} {'Kern%':>7} {'ok+ot':>6} {'qo+ch':>6} {'Ratio':>7} Character")
print("-" * 70)

t2_gradient = {}
for folio in ra.get_folios():
    toks = ra.get_tokens(folio)
    p = system_profile(toks)
    if not p:
        continue

    # Classify
    if p['prefix_ratio'] > 2.0 and p['link_density'] < 0.005:
        char = 'AZC-like'
    elif p['prefix_ratio'] < 0.5 and p['link_density'] > 0.015:
        char = 'B-like'
    elif p['prefix_ratio'] < 0.5:
        char = 'B-leaning'
    elif p['prefix_ratio'] > 1.0:
        char = 'AZC-leaning'
    else:
        char = 'Transitional'

    print(f"{folio:<8} {p['n_tokens']:>4} {p['link_density']:>6.2%} "
          f"{p['kernel_middle_rate']:>6.1%} {p['ok_ot']:>6} {p['qo_ch']:>6} "
          f"{p['prefix_ratio']:>7.3f} {char}")

    t2_gradient[folio] = {
        'n_tokens': p['n_tokens'],
        'link_density': round(p['link_density'], 4),
        'kernel_middle_rate': round(p['kernel_middle_rate'], 3),
        'prefix_ratio': round(p['prefix_ratio'], 3),
        'character': char,
    }

# Count gradient zones
chars = [d['character'] for d in t2_gradient.values()]
azc_count = sum(1 for c in chars if 'AZC' in c)
b_count = sum(1 for c in chars if 'B-l' in c)
trans_count = sum(1 for c in chars if 'Trans' in c)

print(f"\nGradient: {azc_count} AZC-like, {trans_count} transitional, {b_count} B-like")

# Per-region gradient for f85v2
print(f"\nf85v2 per-region (5+ tokens):")
print(f"{'Region':<6} {'Tok':>4} {'LINK%':>7} {'Kern%':>7} {'Ratio':>7} Character")
print("-" * 50)

t2_v2_regions = {}
for region in ra.get_regions('f85v2'):
    toks = ra.get_tokens('f85v2', region)
    if len(toks) < 5:
        continue
    p = system_profile(toks)
    if not p:
        continue
    if p['prefix_ratio'] > 2.0:
        char = 'AZC-like'
    elif p['prefix_ratio'] < 0.5:
        char = 'B-leaning'
    else:
        char = 'Mixed'

    print(f"{region:<6} {p['n_tokens']:>4} {p['link_density']:>6.2%} "
          f"{p['kernel_middle_rate']:>6.1%} {p['prefix_ratio']:>7.3f} {char}")
    t2_v2_regions[region] = {
        'prefix_ratio': round(p['prefix_ratio'], 3),
        'character': char,
    }

t2_verdict = 'GRADIENT_CONFIRMED' if azc_count >= 1 and b_count >= 1 else 'NO_GRADIENT'
print(f"\nVERDICT: {t2_verdict}")
results['verdicts']['T2_gradient'] = t2_verdict
results['T2_data'] = {'per_folio': t2_gradient, 'f85v2_regions': t2_v2_regions}


# ============================================================
# T3: EXCLUSIVE VOCABULARY CHARACTERIZATION
# ============================================================
print("\n" + "=" * 65)
print("T3: EXCLUSIVE VOCABULARY CHARACTERIZATION")
print("=" * 65)
print("Are the 79 Rosettes-exclusive MIDDLEs organizational labels?")

exclusive = ALL_ROS_MIDDLES - ALL_B_MIDDLES - A_MIDDLES - AZC_MIDDLES
print(f"\nExclusive MIDDLEs: {len(exclusive)}")

# Length distribution
lengths = [len(m) for m in exclusive]
mean_len = sum(lengths) / len(lengths) if lengths else 0
print(f"  Mean length: {mean_len:.2f}")
print(f"  Length distribution: {Counter(lengths).most_common()}")

# Compare to shared vocabulary length
shared = ALL_ROS_MIDDLES & ALL_B_MIDDLES
shared_lens = [len(m) for m in shared]
shared_mean = sum(shared_lens) / len(shared_lens) if shared_lens else 0
print(f"  Shared MIDDLEs mean length: {shared_mean:.2f}")

# Kernel character density in exclusive vs shared
def kernel_rate(middles):
    if not middles:
        return 0
    with_k = sum(1 for m in middles if any(c in 'khe' for c in m))
    return with_k / len(middles)

excl_kr = kernel_rate(exclusive)
shared_kr = kernel_rate(shared)
print(f"\n  Kernel char rate (exclusive): {excl_kr:.1%}")
print(f"  Kernel char rate (shared):    {shared_kr:.1%}")

# Compound analysis: do exclusive MIDDLEs contain known core atoms?
core_atoms = {'od', 'al', 'ar', 'aiin', 'or', 'dy', 'ol', 'ey', 'y', 'r',
              'l', 'e', 'd', 'k', 'h', 'in', 'an', 'am', 'ee', 'eey',
              'edy', 'ain', 'oin'}

compound_count = 0
atom_containing = 0
for mid in exclusive:
    contained = [a for a in core_atoms if a in mid and a != mid and len(a) < len(mid)]
    if len(contained) >= 2:
        compound_count += 1
    if contained:
        atom_containing += 1

print(f"\n  Contains core atoms: {atom_containing}/{len(exclusive)} ({100*atom_containing/len(exclusive):.1f}%)")
print(f"  Contains 2+ atoms (compound): {compound_count}/{len(exclusive)} ({100*compound_count/len(exclusive):.1f}%)")

# Where do exclusive MIDDLEs appear? (which folios/regions)
excl_locations = defaultdict(list)
for folio in ra.get_folios():
    for region in ra.get_regions(folio):
        key = (folio, region)
        rmid = ROS_REGION_MIDDLES.get(key, set())
        excl_here = rmid & exclusive
        if excl_here:
            excl_locations[folio].extend(excl_here)

print(f"\n  Distribution across folios:")
for folio in ra.get_folios():
    count = len(excl_locations.get(folio, []))
    total = len(ROS_FOLIO_MIDDLES.get(folio, set()))
    pct = 100 * count / total if total else 0
    print(f"    {folio}: {count} exclusive / {total} total ({pct:.1f}%)")

# Hapax check
excl_freq = Counter()
for folio in ra.get_folios():
    for tok in ra.get_tokens(folio):
        m = morph.extract(tok.word)
        if m.middle in exclusive:
            excl_freq[m.middle] += 1

hapax = sum(1 for c in excl_freq.values() if c == 1)
hapax_rate = hapax / len(excl_freq) if excl_freq else 0
print(f"\n  Hapax rate: {hapax}/{len(excl_freq)} = {hapax_rate:.1%}")
print(f"  (C618 prediction for unique B MIDDLEs: 99.7%)")

# Show some examples with their locations
print(f"\n  Sample exclusive MIDDLEs with occurrence counts:")
for mid, count in excl_freq.most_common(20):
    locs = []
    for folio in ra.get_folios():
        for region in ra.get_regions(folio):
            key = (folio, region)
            if mid in ROS_REGION_MIDDLES.get(key, set()):
                locs.append(f"{folio}:{region}")
    print(f"    {mid:15s} x{count}  at {', '.join(locs)}")

if hapax_rate > 0.80 and mean_len > 3.5:
    t3_verdict = 'MORPHOLOGICAL_TAIL'
elif hapax_rate < 0.50:
    t3_verdict = 'ORGANIZATIONAL_VOCABULARY'
else:
    t3_verdict = 'MIXED_CHARACTER'

print(f"\nVERDICT: {t3_verdict}")
results['verdicts']['T3_exclusive_vocab'] = t3_verdict
results['T3_data'] = {
    'count': len(exclusive),
    'mean_length': round(mean_len, 2),
    'shared_mean_length': round(shared_mean, 2),
    'kernel_rate_exclusive': round(excl_kr, 3),
    'kernel_rate_shared': round(shared_kr, 3),
    'compound_rate': round(compound_count / len(exclusive), 3) if exclusive else 0,
    'hapax_rate': round(hapax_rate, 3),
}


# ============================================================
# T4: CROSS-REFERENCE DENSITY
# ============================================================
print("\n" + "=" * 65)
print("T4: CROSS-REFERENCE DENSITY")
print("=" * 65)
print("Do rare MIDDLEs link specific rosettes to specific body text folios?")

# For each Rosettes folio, find body text folios that share rare MIDDLEs
# "Rare" = appears in fewer than 5 B folios (highly diagnostic)

# Build MIDDLE-to-folio map for body text
middle_to_b_folios = defaultdict(set)
for folio, middles in FOLIO_MIDDLES.items():
    for m in middles:
        middle_to_b_folios[m].add(folio)

# Rare MIDDLEs: appear in 1-4 B folios
rare_middles = {m for m, folios in middle_to_b_folios.items() if 1 <= len(folios) <= 4}
print(f"Rare B MIDDLEs (1-4 folios): {len(rare_middles)}")

# For each Rosettes folio, find its rare MIDDLE links
print(f"\nCross-references via rare MIDDLEs:")
t4_data = {}

for folio in ra.get_folios():
    fmid = ROS_FOLIO_MIDDLES[folio]
    shared_rare = fmid & rare_middles

    if not shared_rare:
        print(f"  {folio}: 0 rare links")
        t4_data[folio] = {'rare_links': 0, 'target_folios': {}}
        continue

    # Which body folios are pointed to?
    target_counts = Counter()
    link_details = []
    for m in shared_rare:
        targets = middle_to_b_folios[m]
        for t in targets:
            target_counts[t] += 1
            section = SECTION_MAP.get(t, '?')
            link_details.append((m, t, section))

    top_targets = target_counts.most_common(5)
    print(f"  {folio}: {len(shared_rare)} rare links, top targets: "
          f"{[(f, c, SECTION_MAP.get(f,'?')) for f, c in top_targets[:3]]}")

    t4_data[folio] = {
        'rare_links': len(shared_rare),
        'target_folios': {f: {'count': c, 'section': SECTION_MAP.get(f, '?')}
                          for f, c in top_targets},
    }

# Aggregate: which sections get the most cross-references?
all_targets = Counter()
for folio in ra.get_folios():
    fmid = ROS_FOLIO_MIDDLES[folio]
    for m in fmid & rare_middles:
        for target_f in middle_to_b_folios[m]:
            all_targets[SECTION_MAP.get(target_f, '?')] += 1

print(f"\nSection cross-reference totals:")
for sec, count in all_targets.most_common():
    print(f"  {sec}: {count} rare-MIDDLE links")

# Per-region cross-references for f85v2
print(f"\nf85v2 per-region cross-references (5+ tokens):")
t4_v2 = {}
for region in ra.get_regions('f85v2'):
    key = ('f85v2', region)
    rmid = ROS_REGION_MIDDLES.get(key, set())
    if len(rmid) < 5:
        continue
    shared_rare = rmid & rare_middles
    if not shared_rare:
        print(f"  {region}: 0 rare links")
        t4_v2[region] = {'links': 0}
        continue

    target_secs = Counter()
    for m in shared_rare:
        for target_f in middle_to_b_folios[m]:
            target_secs[SECTION_MAP.get(target_f, '?')] += 1

    print(f"  {region}: {len(shared_rare)} rare links -> {target_secs.most_common(3)}")
    t4_v2[region] = {
        'links': len(shared_rare),
        'section_targets': dict(target_secs.most_common()),
    }

# Do different regions point to different sections?
region_targets = {}
for region, data in t4_v2.items():
    if data.get('section_targets'):
        top_sec = max(data['section_targets'], key=data['section_targets'].get)
        region_targets[region] = top_sec

unique_targets = set(region_targets.values())
print(f"\nf85v2 regions point to {len(unique_targets)} sections via rare MIDDLEs: {sorted(unique_targets)}")
print(f"Region -> section mapping: {region_targets}")

if len(unique_targets) > 2:
    t4_verdict = 'MULTI_TARGET_CROSSREF'
elif len(unique_targets) == 1:
    t4_verdict = 'SINGLE_TARGET'
else:
    t4_verdict = 'WEAK_CROSSREF'

print(f"\nVERDICT: {t4_verdict}")
results['verdicts']['T4_crossref_density'] = t4_verdict
results['T4_data'] = {
    'per_folio': t4_data,
    'f85v2_regions': t4_v2,
    'section_totals': dict(all_targets.most_common()),
}


# ============================================================
# T5: STRUCTURAL ROLE CLASSIFICATION PER REGION
# ============================================================
print("\n" + "=" * 65)
print("T5: STRUCTURAL ROLE CLASSIFICATION")
print("=" * 65)
print("Classifying each folio/region as: INDEX, DESCRIPTION, or BRIDGE")

# Classification heuristics:
# INDEX (AZC-like): low LINK, high ok/ot ratio, low bigram reuse, orthogonal vocab
# DESCRIPTION (B-like): normal LINK, qo/ch dominant, sequential coherence
# BRIDGE: intermediate properties

def classify_role(tokens):
    """Classify a token set by structural role."""
    if len(tokens) < 5:
        return 'TOO_SMALL', {}

    prefix_counts = Counter()
    link_count = 0
    middle_list = []

    for tok in tokens:
        m = morph.extract(tok.word)
        if m.prefix:
            prefix_counts[m.prefix] += 1
            if m.prefix in LINK_PREFIXES:
                link_count += 1
        if m.middle:
            middle_list.append(m.middle)

    n = len(tokens)
    link_density = link_count / n
    ok_ot = prefix_counts.get('ok', 0) + prefix_counts.get('ot', 0)
    qo_ch = prefix_counts.get('qo', 0) + prefix_counts.get('ch', 0)
    prefix_ratio = ok_ot / qo_ch if qo_ch else float('inf')

    # Bigram reuse
    bigrams = Counter()
    for i in range(len(middle_list) - 1):
        bigrams[(middle_list[i], middle_list[i+1])] += 1
    reuse_rate = sum(1 for c in bigrams.values() if c >= 2) / len(bigrams) if bigrams else 0

    # Vocabulary uniqueness
    unique_middles = len(set(middle_list))
    vocab_ratio = unique_middles / len(middle_list) if middle_list else 0

    # Score: higher = more INDEX-like, lower = more DESCRIPTION-like
    index_score = 0
    if prefix_ratio > 1.0:
        index_score += 2
    elif prefix_ratio > 0.6:
        index_score += 1
    if link_density < 0.005:
        index_score += 2
    elif link_density < 0.015:
        index_score += 1
    if reuse_rate < 0.03:
        index_score += 1
    if vocab_ratio > 0.6:
        index_score += 1

    if index_score >= 4:
        role = 'INDEX'
    elif index_score <= 1:
        role = 'DESCRIPTION'
    else:
        role = 'BRIDGE'

    return role, {
        'index_score': index_score,
        'link_density': round(link_density, 4),
        'prefix_ratio': round(prefix_ratio, 3),
        'reuse_rate': round(reuse_rate, 3),
        'vocab_ratio': round(vocab_ratio, 3),
    }

# Classify each folio
print(f"\n{'Folio':<8} {'Role':<12} {'Score':>5} {'LINK%':>7} {'Ratio':>7} {'Reuse%':>7} {'VocR':>6}")
print("-" * 60)

t5_folios = {}
for folio in ra.get_folios():
    toks = ra.get_tokens(folio)
    role, metrics = classify_role(toks)
    print(f"{folio:<8} {role:<12} {metrics.get('index_score',''):>5} "
          f"{metrics.get('link_density',0):>6.2%} "
          f"{metrics.get('prefix_ratio',0):>7.3f} "
          f"{metrics.get('reuse_rate',0):>6.1%} "
          f"{metrics.get('vocab_ratio',0):>6.3f}")
    t5_folios[folio] = {'role': role, **metrics}

# Classify f85v2 regions
print(f"\nf85v2 per-region roles:")
t5_v2 = {}
for region in ra.get_regions('f85v2'):
    toks = ra.get_tokens('f85v2', region)
    role, metrics = classify_role(toks)
    if role == 'TOO_SMALL':
        continue
    print(f"  {region:<6} {role:<12} score={metrics.get('index_score','')}")
    t5_v2[region] = {'role': role, **metrics}

# Summary
roles = Counter(d['role'] for d in t5_folios.values())
print(f"\nFolio role distribution: {dict(roles)}")

v2_roles = Counter(d['role'] for d in t5_v2.values())
print(f"f85v2 region roles: {dict(v2_roles)}")

if roles.get('INDEX', 0) >= 1 and roles.get('DESCRIPTION', 0) >= 1:
    t5_verdict = 'MIXED_ROLES_CONFIRMED'
elif roles.get('INDEX', 0) == len(t5_folios):
    t5_verdict = 'ALL_INDEX'
elif roles.get('DESCRIPTION', 0) == len(t5_folios):
    t5_verdict = 'ALL_DESCRIPTION'
else:
    t5_verdict = 'BRIDGE_DOMINANT'

print(f"\nVERDICT: {t5_verdict}")
results['verdicts']['T5_structural_roles'] = t5_verdict
results['T5_data'] = {'per_folio': t5_folios, 'f85v2_regions': t5_v2}


# ============================================================
# OVERALL ASSESSMENT
# ============================================================
print("\n" + "=" * 65)
print("OVERALL ASSESSMENT")
print("=" * 65)

verdicts = results['verdicts']
print("\nAll verdicts:")
for test, verdict in sorted(verdicts.items()):
    print(f"  {test}: {verdict}")

# Metalayer assessment
gradient_confirmed = 'GRADIENT' in verdicts.get('T2_gradient', '')
mixed_roles = 'MIXED' in verdicts.get('T5_structural_roles', '')
multi_target = 'MULTI' in verdicts.get('T4_crossref_density', '')

if gradient_confirmed and mixed_roles:
    overall = 'METALAYER_CONFIRMED'
    summary = ("The Rosettes foldout is a META-LAYER structure with an "
               "AZC-to-B gradient. Some pages/regions function as INDEX "
               "(positional encoding), others as DESCRIPTION (B-like text). "
               "It draws vocabulary from all three systems (A, B, AZC) "
               "and maintains exclusive organizational vocabulary.")
elif gradient_confirmed:
    overall = 'GRADIENT_STRUCTURE'
    summary = ("The Rosettes shows a clear AZC-to-B gradient but "
               "role differentiation is less distinct than expected.")
else:
    overall = 'INCONCLUSIVE'
    summary = "The metalayer hypothesis is not clearly supported."

print(f"\nOVERALL: {overall}")
print(f"\n{summary}")

results['overall'] = overall
results['summary'] = summary

# ============================================================
# SAVE
# ============================================================
output_path = ROOT / 'phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosettes_metalayer_results.json'

def round_floats(obj, digits=4):
    if isinstance(obj, float):
        return round(obj, digits)
    elif isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    elif isinstance(obj, set):
        return sorted(obj)
    return obj

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(round_floats(results), f, indent=2)

print(f"\nResults saved to {output_path}")
