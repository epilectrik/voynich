#!/usr/bin/env python3
"""
UN COMPOSITIONAL MECHANICS - Script 1: Census & Morphological Profile

Characterizes the ~7,042 UN (unclassified) tokens that comprise ~30.5% of
Currier B. C566 established they are "morphologically normal" and unclassified
due to cosurvival threshold, not structural deviance.

Sections:
1. UN Token Inventory (totals, types, hapax)
2. Morphological Profile (PREFIX, MIDDLE, SUFFIX distributions)
3. Morphological Overlap with Classified Roles (PREFIX->role probability)
4. MIDDLE Overlap Analysis (Jaccard, PP/RI status)
5. Section/REGIME Distribution
"""

import os
import sys
import json
import numpy as np
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("=" * 70)
print("UN COMPOSITIONAL MECHANICS - Script 1: Census")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Load B tokens
b_tokens = list(tx.currier_b())
print(f"Total Currier B tokens: {len(b_tokens)}")

# Load ICC class map
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']

ROLE_ABBREV = {
    'CORE_CONTROL': 'CC',
    'ENERGY_OPERATOR': 'EN',
    'FLOW_OPERATOR': 'FL',
    'FREQUENT_OPERATOR': 'FQ',
    'AUXILIARY': 'AX',
}

# Load middle classes (RI/PP)
with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
    mid_data = json.load(f)
ri_middles = set(mid_data['a_exclusive_middles'])
pp_middles = set(mid_data['a_shared_middles'])

# Load regime mapping
with open('phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json', 'r') as f:
    regime_map_raw = json.load(f)
# Invert: folio -> regime
folio_to_regime = {}
for regime, folios in regime_map_raw.items():
    for f in folios:
        folio_to_regime[f] = regime

# Classify each B token
classified_tokens = []  # (token_obj, role_abbrev)
un_tokens = []

for t in b_tokens:
    if t.word in token_to_class:
        cls = str(token_to_class[t.word])
        role = class_to_role.get(cls, 'UNKNOWN')
        abbrev = ROLE_ABBREV.get(role, role)
        classified_tokens.append((t, abbrev))
    else:
        un_tokens.append(t)

print(f"Classified tokens: {len(classified_tokens)} ({len(classified_tokens)/len(b_tokens)*100:.1f}%)")
print(f"UN tokens: {len(un_tokens)} ({len(un_tokens)/len(b_tokens)*100:.1f}%)")

# ==============================================================================
# SECTION 1: UN TOKEN INVENTORY
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 1: UN TOKEN INVENTORY")
print("=" * 70)

un_words = [t.word for t in un_tokens]
un_type_counts = Counter(un_words)
un_types = len(un_type_counts)
un_hapax = sum(1 for w, c in un_type_counts.items() if c == 1)
un_hapax_pct = un_hapax / un_types * 100 if un_types > 0 else 0

print(f"\nUN Token Statistics:")
print(f"  Total tokens:  {len(un_tokens)}")
print(f"  Unique types:  {un_types}")
print(f"  Hapax (1x):    {un_hapax} ({un_hapax_pct:.1f}%)")

# Verify against C566 (expected: ~7,042 tokens, ~4,421 types, ~74.1% hapax)
print(f"\n  C566 comparison:")
print(f"    Tokens: {len(un_tokens)} (expected ~7,042)")
print(f"    Types:  {un_types} (expected ~4,421)")
print(f"    Hapax:  {un_hapax_pct:.1f}% (expected ~74.1%)")

# Frequency distribution
freq_dist = Counter(un_type_counts.values())
print(f"\nFrequency distribution:")
for freq in sorted(freq_dist.keys())[:10]:
    count = freq_dist[freq]
    print(f"  {freq}x: {count} types")
if max(freq_dist.keys()) > 10:
    high_freq = sum(v for k, v in freq_dist.items() if k > 10)
    print(f"  >10x: {high_freq} types")

# Top repeaters
print(f"\nTop 15 most frequent UN types:")
for word, count in un_type_counts.most_common(15):
    print(f"  {word:<20} {count:>5}x")

# Folio distribution
un_by_folio = Counter(t.folio for t in un_tokens)
total_by_folio = Counter(t.folio for t in b_tokens)
folio_un_pcts = {}
for folio in sorted(total_by_folio.keys()):
    un_count = un_by_folio.get(folio, 0)
    total = total_by_folio[folio]
    pct = un_count / total * 100
    folio_un_pcts[folio] = pct

pcts = list(folio_un_pcts.values())
print(f"\nUN proportion by folio:")
print(f"  Mean:   {np.mean(pcts):.1f}%")
print(f"  Median: {np.median(pcts):.1f}%")
print(f"  Min:    {np.min(pcts):.1f}%")
print(f"  Max:    {np.max(pcts):.1f}%")

# Top 5 folios by UN proportion
sorted_folios = sorted(folio_un_pcts.items(), key=lambda x: x[1], reverse=True)
print(f"\n  Highest UN proportion folios:")
for folio, pct in sorted_folios[:5]:
    print(f"    {folio}: {pct:.1f}% ({un_by_folio[folio]}/{total_by_folio[folio]})")

# ==============================================================================
# SECTION 2: MORPHOLOGICAL PROFILE
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 2: MORPHOLOGICAL PROFILE")
print("=" * 70)

# Extract morphology for all UN tokens
un_morphs = [(t, morph.extract(t.word)) for t in un_tokens]

# Also extract for all classified tokens for comparison
classified_morphs = [(t, morph.extract(t.word)) for t, _ in classified_tokens]
classified_roles = [role for _, role in classified_tokens]

# PREFIX distribution - UN
un_prefix_counts = Counter(m.prefix for _, m in un_morphs)
total_un_with_prefix = sum(1 for _, m in un_morphs if m.prefix is not None)
total_un_no_prefix = sum(1 for _, m in un_morphs if m.prefix is None)

print(f"\nUN PREFIX distribution:")
print(f"  With prefix:    {total_un_with_prefix} ({total_un_with_prefix/len(un_tokens)*100:.1f}%)")
print(f"  Without prefix: {total_un_no_prefix} ({total_un_no_prefix/len(un_tokens)*100:.1f}%)")
print(f"\n  {'PREFIX':<10} {'UN':>8} {'UN %':>8}")
print(f"  {'-'*30}")
for prefix, count in un_prefix_counts.most_common(15):
    pct = count / len(un_tokens) * 100
    label = prefix if prefix else '(none)'
    print(f"  {label:<10} {count:>8} {pct:>7.1f}%")

# PREFIX distribution - Classified (for comparison)
cls_prefix_counts = Counter(m.prefix for _, m in classified_morphs)
print(f"\n  Classified PREFIX comparison (top 10):")
print(f"  {'PREFIX':<10} {'CLS':>8} {'CLS %':>8} {'UN':>8} {'UN %':>8} {'Ratio':>8}")
print(f"  {'-'*55}")
all_prefixes = set(list(un_prefix_counts.keys())[:10] + list(cls_prefix_counts.keys())[:10])
for prefix in sorted(all_prefixes, key=lambda p: un_prefix_counts.get(p, 0), reverse=True)[:12]:
    un_c = un_prefix_counts.get(prefix, 0)
    cls_c = cls_prefix_counts.get(prefix, 0)
    un_p = un_c / len(un_tokens) * 100
    cls_p = cls_c / len(classified_tokens) * 100
    ratio = un_p / cls_p if cls_p > 0 else float('inf')
    label = prefix if prefix else '(none)'
    print(f"  {label:<10} {cls_c:>8} {cls_p:>7.1f}% {un_c:>8} {un_p:>7.1f}% {ratio:>7.2f}x")

# SUFFIX distribution
un_suffix_counts = Counter(m.suffix for _, m in un_morphs)
total_un_with_suffix = sum(1 for _, m in un_morphs if m.suffix is not None)
cls_with_suffix = sum(1 for _, m in classified_morphs if m.suffix is not None)

print(f"\nSUFFIX presence:")
print(f"  UN with suffix:  {total_un_with_suffix} ({total_un_with_suffix/len(un_tokens)*100:.1f}%)")
print(f"  CLS with suffix: {cls_with_suffix} ({cls_with_suffix/len(classified_tokens)*100:.1f}%)")

print(f"\n  Top UN suffixes:")
for suffix, count in un_suffix_counts.most_common(10):
    pct = count / len(un_tokens) * 100
    label = suffix if suffix else '(none)'
    print(f"    {label:<10} {count:>6} ({pct:.1f}%)")

# MIDDLE distribution
un_middle_counts = Counter(m.middle for _, m in un_morphs if m.middle)
print(f"\nUN MIDDLE statistics:")
print(f"  Unique MIDDLEs: {len(un_middle_counts)}")
print(f"  Top 10 UN MIDDLEs:")
for mid, count in un_middle_counts.most_common(10):
    pp_status = 'PP' if mid in pp_middles else ('RI' if mid in ri_middles else '--')
    print(f"    {mid:<15} {count:>5} ({pp_status})")

# MIDDLE PP/RI status
un_pp_middles = sum(1 for _, m in un_morphs if m.middle and m.middle in pp_middles)
un_ri_middles = sum(1 for _, m in un_morphs if m.middle and m.middle in ri_middles)
un_neither = sum(1 for _, m in un_morphs if m.middle and m.middle not in pp_middles and m.middle not in ri_middles)
un_no_middle = sum(1 for _, m in un_morphs if not m.middle)

print(f"\nUN MIDDLE classification (token-level):")
print(f"  PP (shared):     {un_pp_middles} ({un_pp_middles/len(un_tokens)*100:.1f}%)")
print(f"  RI (A-exclusive): {un_ri_middles} ({un_ri_middles/len(un_tokens)*100:.1f}%)")
print(f"  Neither:         {un_neither} ({un_neither/len(un_tokens)*100:.1f}%)")
print(f"  No MIDDLE:       {un_no_middle} ({un_no_middle/len(un_tokens)*100:.1f}%)")

# Type-level
un_mid_types = set(m.middle for _, m in un_morphs if m.middle)
un_pp_types = un_mid_types & pp_middles
un_ri_types = un_mid_types & ri_middles
un_novel_types = un_mid_types - pp_middles - ri_middles

print(f"\nUN MIDDLE classification (type-level):")
print(f"  Total unique MIDDLEs: {len(un_mid_types)}")
print(f"  PP types: {len(un_pp_types)} ({len(un_pp_types)/len(un_mid_types)*100:.1f}%)")
print(f"  RI types: {len(un_ri_types)} ({len(un_ri_types)/len(un_mid_types)*100:.1f}%)")
print(f"  Novel (neither): {len(un_novel_types)} ({len(un_novel_types)/len(un_mid_types)*100:.1f}%)")

# Articulator rate
un_art_count = sum(1 for _, m in un_morphs if m.has_articulator)
cls_art_count = sum(1 for _, m in classified_morphs if m.has_articulator)
print(f"\nArticulator rate:")
print(f"  UN:  {un_art_count} ({un_art_count/len(un_tokens)*100:.1f}%)")
print(f"  CLS: {cls_art_count} ({cls_art_count/len(classified_tokens)*100:.1f}%)")

# ==============================================================================
# SECTION 3: PREFIX->ROLE PROBABILITY TABLE
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 3: MORPHOLOGICAL OVERLAP WITH CLASSIFIED ROLES")
print("=" * 70)

# For each PREFIX found in UN, what role distribution do classified tokens with that PREFIX have?
cls_prefix_role = defaultdict(Counter)
for (t, role), (_, m) in zip(classified_tokens, classified_morphs):
    prefix = m.prefix if m.prefix else '(none)'
    cls_prefix_role[prefix][role] += 1

print(f"\nPREFIX -> Role probability (from classified tokens):")
print(f"  {'PREFIX':<10} {'N_cls':>6} {'CC':>6} {'EN':>6} {'FL':>6} {'FQ':>6} {'AX':>6} {'Mode':>6}")
print(f"  {'-'*58}")

# Focus on prefixes found in UN tokens
un_prefixes_for_table = [p for p, _ in un_prefix_counts.most_common(20) if p is not None]
prefix_role_probs = {}

for prefix in un_prefixes_for_table:
    role_dist = cls_prefix_role.get(prefix, Counter())
    total = sum(role_dist.values())
    if total == 0:
        continue
    probs = {r: role_dist.get(r, 0) / total * 100 for r in ['CC', 'EN', 'FL', 'FQ', 'AX']}
    mode_role = max(probs, key=probs.get)
    prefix_role_probs[prefix] = probs
    print(f"  {prefix:<10} {total:>6} {probs['CC']:>5.1f}% {probs['EN']:>5.1f}% {probs['FL']:>5.1f}% {probs['FQ']:>5.1f}% {probs['AX']:>5.1f}% {mode_role:>6}")

# Also compute for (none) prefix
none_dist = cls_prefix_role.get('(none)', Counter())
if sum(none_dist.values()) > 0:
    total = sum(none_dist.values())
    probs = {r: none_dist.get(r, 0) / total * 100 for r in ['CC', 'EN', 'FL', 'FQ', 'AX']}
    mode_role = max(probs, key=probs.get)
    print(f"  {'(none)':<10} {total:>6} {probs['CC']:>5.1f}% {probs['EN']:>5.1f}% {probs['FL']:>5.1f}% {probs['FQ']:>5.1f}% {probs['AX']:>5.1f}% {mode_role:>6}")

# ==============================================================================
# SECTION 4: MIDDLE OVERLAP ANALYSIS
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 4: MIDDLE OVERLAP ANALYSIS")
print("=" * 70)

# Get MIDDLEs by role from classified tokens
role_middles = defaultdict(set)
for (t, role), (_, m) in zip(classified_tokens, classified_morphs):
    if m.middle:
        role_middles[role].add(m.middle)

print(f"\nMIDDLE sets by role:")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    print(f"  {role}: {len(role_middles[role])} unique MIDDLEs")

# Jaccard overlap: UN MIDDLEs vs each role's MIDDLEs
print(f"\nJaccard overlap: UN MIDDLEs vs role MIDDLEs:")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    intersection = un_mid_types & role_middles[role]
    union = un_mid_types | role_middles[role]
    jaccard = len(intersection) / len(union) if len(union) > 0 else 0
    overlap_pct = len(intersection) / len(un_mid_types) * 100 if len(un_mid_types) > 0 else 0
    print(f"  UN vs {role}: Jaccard={jaccard:.3f}, {len(intersection)}/{len(un_mid_types)} UN MIDDLEs shared ({overlap_pct:.1f}%)")

# How many UN MIDDLEs are found in ANY classified role?
all_cls_middles = set()
for role in role_middles:
    all_cls_middles |= role_middles[role]

un_in_cls = un_mid_types & all_cls_middles
un_novel = un_mid_types - all_cls_middles
print(f"\nUN MIDDLEs found in classified vocabulary: {len(un_in_cls)} ({len(un_in_cls)/len(un_mid_types)*100:.1f}%)")
print(f"UN MIDDLEs NOT in classified vocabulary:  {len(un_novel)} ({len(un_novel)/len(un_mid_types)*100:.1f}%)")

# For novel MIDDLEs: are they compositionally derivable?
# Check if they contain known PP/RI substrings
print(f"\nNovel UN MIDDLEs: compositional check")
novel_with_pp_atom = 0
for mid in un_novel:
    for pp in pp_middles:
        if len(pp) >= 2 and pp in mid and mid != pp:
            novel_with_pp_atom += 1
            break
print(f"  Novel MIDDLEs containing a PP atom: {novel_with_pp_atom}/{len(un_novel)} ({novel_with_pp_atom/len(un_novel)*100:.1f}%)")

# ==============================================================================
# SECTION 5: SECTION / REGIME DISTRIBUTION
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 5: SECTION / REGIME DISTRIBUTION")
print("=" * 70)

# UN proportion by section
section_un = defaultdict(int)
section_total = defaultdict(int)
for t in b_tokens:
    sec = t.section if t.section else 'UNKNOWN'
    section_total[sec] += 1
    if t.word not in token_to_class:
        section_un[sec] += 1

print(f"\nUN proportion by section:")
print(f"  {'Section':<12} {'Total':>8} {'UN':>8} {'UN %':>8}")
print(f"  {'-'*40}")
for sec in sorted(section_total.keys()):
    un_c = section_un[sec]
    tot = section_total[sec]
    pct = un_c / tot * 100
    print(f"  {sec:<12} {tot:>8} {un_c:>8} {pct:>7.1f}%")

# UN proportion by REGIME
regime_un = defaultdict(int)
regime_total = defaultdict(int)
for t in b_tokens:
    regime = folio_to_regime.get(t.folio, 'UNASSIGNED')
    regime_total[regime] += 1
    if t.word not in token_to_class:
        regime_un[regime] += 1

print(f"\nUN proportion by REGIME:")
print(f"  {'REGIME':<15} {'Total':>8} {'UN':>8} {'UN %':>8}")
print(f"  {'-'*45}")
for regime in sorted(regime_total.keys()):
    un_c = regime_un[regime]
    tot = regime_total[regime]
    pct = un_c / tot * 100
    print(f"  {regime:<15} {tot:>8} {un_c:>8} {pct:>7.1f}%")

# Spearman: folio UN proportion vs classified role proportions
from scipy.stats import spearmanr

folio_list = sorted(total_by_folio.keys())
folio_un_arr = np.array([un_by_folio.get(f, 0) / total_by_folio[f] for f in folio_list])

# Folio-level role proportions
folio_role_counts = defaultdict(lambda: defaultdict(int))
for (t, role) in classified_tokens:
    folio_role_counts[t.folio][role] += 1

print(f"\nSpearman: folio UN proportion vs folio-level variables:")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    role_arr = np.array([folio_role_counts[f].get(role, 0) / total_by_folio[f] for f in folio_list])
    rho, p = spearmanr(folio_un_arr, role_arr)
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
    print(f"  UN vs {role:<3} proportion: rho={rho:+.3f}, p={p:.4f} {sig}")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

results = {
    'inventory': {
        'total_b': len(b_tokens),
        'classified': len(classified_tokens),
        'un_tokens': len(un_tokens),
        'un_pct': round(len(un_tokens) / len(b_tokens) * 100, 1),
        'un_types': un_types,
        'un_hapax': un_hapax,
        'un_hapax_pct': round(un_hapax_pct, 1),
    },
    'morphology': {
        'un_with_prefix_pct': round(total_un_with_prefix / len(un_tokens) * 100, 1),
        'un_with_suffix_pct': round(total_un_with_suffix / len(un_tokens) * 100, 1),
        'un_articulator_pct': round(un_art_count / len(un_tokens) * 100, 1),
        'cls_with_suffix_pct': round(cls_with_suffix / len(classified_tokens) * 100, 1),
        'un_pp_middle_pct': round(un_pp_middles / len(un_tokens) * 100, 1),
        'un_ri_middle_pct': round(un_ri_middles / len(un_tokens) * 100, 1),
    },
    'middle_overlap': {
        'un_middle_types': len(un_mid_types),
        'in_classified': len(un_in_cls),
        'novel': len(un_novel),
        'novel_with_pp_atom_pct': round(novel_with_pp_atom / len(un_novel) * 100, 1) if un_novel else 0,
        'jaccard_by_role': {
            role: round(len(un_mid_types & role_middles[role]) / len(un_mid_types | role_middles[role]), 3)
            if len(un_mid_types | role_middles[role]) > 0 else 0
            for role in ['CC', 'EN', 'FL', 'FQ', 'AX']
        },
    },
    'section_distribution': {
        sec: round(section_un[sec] / section_total[sec] * 100, 1)
        for sec in sorted(section_total.keys())
    },
    'regime_distribution': {
        regime: round(regime_un[regime] / regime_total[regime] * 100, 1)
        for regime in sorted(regime_total.keys())
    },
}

output_path = 'phases/UN_COMPOSITIONAL_MECHANICS/results/un_census.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\n{'=' * 70}")
print("UN CENSUS COMPLETE")
print(f"{'=' * 70}")
