#!/usr/bin/env python3
"""
AX BEHAVIORAL UNPACKING - Script 2: AX-UN Integration

Tests whether AX-predicted UN tokens (C613) fit the AX subgroup structure.
Classifies UN-AX into INIT/MED/FINAL, compares routing, analyzes MIDDLE overlap,
and reports the combined AX profile if UN tokens were absorbed.

Sections:
1. AX-Predicted UN Subgroup Classification
2. AX-UN Routing Comparison
3. AX-UN MIDDLE Overlap
4. Combined AX Profile
"""

import os
import sys
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("=" * 70)
print("AX BEHAVIORAL UNPACKING - Script 2: AX-UN Integration")
print("=" * 70)

tx = Transcript()
morph = Morphology()

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

# AX subgroup definitions (C563)
AX_INIT_CLASSES = {4, 5, 6, 24, 26}
AX_MED_CLASSES = {1, 2, 3, 16, 18, 27, 28, 29}
AX_FINAL_CLASSES = {15, 19, 20, 21, 22, 25}

def get_subgroup(cls_num):
    if cls_num in AX_INIT_CLASSES:
        return 'AX_INIT'
    elif cls_num in AX_MED_CLASSES:
        return 'AX_MED'
    elif cls_num in AX_FINAL_CLASSES:
        return 'AX_FINAL'
    return None

def get_role(word):
    if word in token_to_class:
        cls = str(token_to_class[word])
        role = class_to_role.get(cls, 'UNKNOWN')
        return ROLE_ABBREV.get(role, role)
    return 'UN'

# Build line sequences
b_tokens = list(tx.currier_b())
total_b = len(b_tokens)
print(f"Total Currier B tokens: {total_b}")

line_seqs = defaultdict(list)
for t in b_tokens:
    line_seqs[(t.folio, t.line)].append(t)

# -----------------------------------------------------------------------
# BUILD PREFIX -> ROLE AND PREFIX -> SUBGROUP MAPS FROM CLASSIFIED TOKENS
# -----------------------------------------------------------------------

prefix_role_dist = defaultdict(Counter)
prefix_subgroup_dist = defaultdict(Counter)

for t in b_tokens:
    word = t.word
    if word not in token_to_class:
        continue
    cls = token_to_class[word]
    cls_str = str(cls)
    role_full = class_to_role.get(cls_str, 'UNKNOWN')
    abbrev = ROLE_ABBREV.get(role_full, role_full)
    m = morph.extract(word)
    prefix = m.prefix if m.prefix else '_NONE_'
    prefix_role_dist[prefix][abbrev] += 1
    if abbrev == 'AX':
        sg = get_subgroup(cls)
        if sg:
            prefix_subgroup_dist[prefix][sg] += 1

# PREFIX -> majority role
prefix_to_majority_role = {}
for prefix, dist in prefix_role_dist.items():
    total = sum(dist.values())
    best_role, best_count = dist.most_common(1)[0]
    prefix_to_majority_role[prefix] = (best_role, best_count / total)

# PREFIX -> majority subgroup (for AX prefixes only)
prefix_to_subgroup = {}
for prefix, dist in prefix_subgroup_dist.items():
    total = sum(dist.values())
    best_sg, best_count = dist.most_common(1)[0]
    prefix_to_subgroup[prefix] = (best_sg, best_count / total)

# Collect classified AX tokens with subgroup and position info
classified_ax = []  # (token, subgroup, morph, line_key, pos, line_len)
for key, seq in line_seqs.items():
    for i, t in enumerate(seq):
        if t.word in token_to_class:
            cls = token_to_class[t.word]
            cls_str = str(cls)
            role_full = class_to_role.get(cls_str, 'UNKNOWN')
            if ROLE_ABBREV.get(role_full) == 'AX':
                sg = get_subgroup(cls)
                if sg:
                    m_ax = morph.extract(t.word)
                    classified_ax.append((t, sg, m_ax, key, i, len(seq)))

print(f"Classified AX tokens: {len(classified_ax)}")

# Collect all UN tokens
un_tokens_data = []  # (token, morph, line_key, pos, line_len)
for key, seq in line_seqs.items():
    for i, t in enumerate(seq):
        if get_role(t.word) == 'UN':
            m_un = morph.extract(t.word)
            un_tokens_data.append((t, m_un, key, i, len(seq)))

print(f"Total UN tokens: {len(un_tokens_data)}")

# Filter to AX-predicted UN: PREFIX majority role is AX
ax_un_tokens = []
for t, m, key, pos, line_len in un_tokens_data:
    prefix = m.prefix if m.prefix else '_NONE_'
    role_info = prefix_to_majority_role.get(prefix)
    if role_info and role_info[0] == 'AX':
        ax_un_tokens.append((t, m, key, pos, line_len))

print(f"AX-predicted UN tokens (PREFIX majority=AX): {len(ax_un_tokens)}")

# ==============================================================================
# SECTION 1: AX-PREDICTED UN SUBGROUP CLASSIFICATION
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 1: AX-PREDICTED UN SUBGROUP CLASSIFICATION")
print("=" * 70)

# Classified AX position distributions per subgroup (reference)
cls_ax_positions = defaultdict(list)
for t, sg, m, key, pos, line_len in classified_ax:
    rel_pos = pos / (line_len - 1) if line_len > 1 else 0.5
    cls_ax_positions[sg].append(rel_pos)

print("\nClassified AX position distributions (reference):")
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    positions = cls_ax_positions[sg]
    print(f"  {sg}: mean={np.mean(positions):.3f}, median={np.median(positions):.3f}, "
          f"std={np.std(positions):.3f}, n={len(positions)}")

# Method A: Position-based classification (thirds)
def position_classify(rel_pos):
    if rel_pos < 0.33:
        return 'AX_INIT'
    elif rel_pos < 0.66:
        return 'AX_MED'
    else:
        return 'AX_FINAL'

# Method B: PREFIX-based classification
def prefix_classify(prefix):
    sg_info = prefix_to_subgroup.get(prefix)
    if sg_info:
        return sg_info[0]
    return None

# Classify all AX-UN tokens with both methods
ax_un_classified = []
for t, m, key, pos, line_len in ax_un_tokens:
    rel_pos = pos / (line_len - 1) if line_len > 1 else 0.5
    prefix = m.prefix if m.prefix else '_NONE_'
    pos_sg = position_classify(rel_pos)
    pre_sg = prefix_classify(prefix)
    ax_un_classified.append((t, m, key, pos, line_len, pos_sg, pre_sg))

# Report position-based classification
pos_counts = Counter(x[5] for x in ax_un_classified)
print(f"\nPosition-based classification (thirds):")
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    n = pos_counts.get(sg, 0)
    pct = n / len(ax_un_classified) * 100 if ax_un_classified else 0
    print(f"  {sg}: {n} ({pct:.1f}%)")

# Report PREFIX-based classification
prefix_sg_counts = Counter()
unassigned = 0
for x in ax_un_classified:
    if x[6] is not None:
        prefix_sg_counts[x[6]] += 1
    else:
        unassigned += 1

print(f"\nPREFIX-based classification:")
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    n = prefix_sg_counts.get(sg, 0)
    pct = n / len(ax_un_classified) * 100 if ax_un_classified else 0
    print(f"  {sg}: {n} ({pct:.1f}%)")
print(f"  Unassigned (novel PREFIX): {unassigned} ({unassigned / len(ax_un_classified) * 100:.1f}%)")

# Agreement rate (where both methods assign)
assignable = sum(1 for x in ax_un_classified if x[6] is not None)
agreement = sum(1 for x in ax_un_classified if x[6] is not None and x[5] == x[6])
agree_pct = agreement / assignable * 100 if assignable > 0 else 0
print(f"\nAgreement (position vs PREFIX): {agreement}/{assignable} ({agree_pct:.1f}%)")

# Classified AX subgroup proportions (reference)
cls_sg_counts = Counter(sg for _, sg, _, _, _, _ in classified_ax)
cls_total = sum(cls_sg_counts.values())
print(f"\nClassified AX subgroup proportions (reference):")
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    n = cls_sg_counts[sg]
    print(f"  {sg}: {n} ({n / cls_total * 100:.1f}%)")

# AX-UN position distribution compared to classified AX
print(f"\nAX-UN position distribution:")
un_positions = [pos / (line_len - 1) if line_len > 1 else 0.5
                for _, _, _, pos, line_len in ax_un_tokens]
print(f"  Mean: {np.mean(un_positions):.3f}, Median: {np.median(un_positions):.3f}")
all_cls_positions = [pos / (ll - 1) if ll > 1 else 0.5
                     for _, _, _, _, pos, ll in classified_ax]
print(f"  Classified AX mean: {np.mean(all_cls_positions):.3f}")

# ==============================================================================
# SECTION 2: AX-UN ROUTING COMPARISON
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 2: AX-UN ROUTING COMPARISON")
print("=" * 70)

def get_next_role_in_line(line_key, pos_idx):
    """Get role of the next token in the same line."""
    seq = line_seqs[line_key]
    if pos_idx + 1 < len(seq):
        return get_role(seq[pos_idx + 1].word)
    return None

roles_order = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']

# Classified AX routing by subgroup
cls_routing = defaultdict(Counter)
for t, sg, m, key, pos, line_len in classified_ax:
    nr = get_next_role_in_line(key, pos)
    if nr:
        cls_routing[sg][nr] += 1

# AX-UN routing by subgroup (use PREFIX-based where available, position otherwise)
un_routing = defaultdict(Counter)
for t, m, key, pos, line_len, pos_sg, pre_sg in ax_un_classified:
    sg = pre_sg if pre_sg else pos_sg
    nr = get_next_role_in_line(key, pos)
    if nr:
        un_routing[sg][nr] += 1

routing_chi2_results = {}

for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    cls_dist = cls_routing[sg]
    un_dist = un_routing[sg]
    cls_n = sum(cls_dist.values())
    un_n = sum(un_dist.values())

    print(f"\n--- {sg} ---")
    if cls_n == 0 or un_n == 0:
        print(f"  Insufficient data (classified={cls_n}, UN={un_n})")
        continue

    print(f"  {'Role':<6} {'Classified':>12} {'Cls %':>8} {'AX-UN':>12} {'UN %':>8}")
    print(f"  {'-' * 50}")

    table_rows = []
    for role in roles_order:
        c = cls_dist.get(role, 0)
        u = un_dist.get(role, 0)
        cp = c / cls_n * 100
        up = u / un_n * 100
        print(f"  {role:<6} {c:>12} {cp:>7.1f}% {u:>12} {up:>7.1f}%")
        table_rows.append([c, u])

    table = np.array(table_rows)
    nonzero = table.sum(axis=1) > 0
    table_filtered = table[nonzero]

    if table_filtered.shape[0] >= 2:
        chi2, p, dof, exp = chi2_contingency(table_filtered)
        n_total = table_filtered.sum()
        k = min(table_filtered.shape)
        V = np.sqrt(chi2 / (n_total * (k - 1))) if n_total > 0 and k > 1 else 0

        print(f"\n  Chi-squared: chi2={chi2:.2f}, p={p:.6f}, dof={dof}, V={V:.3f}")
        sig = p < 0.05
        print(f"  {'DIFFERENT routing' if sig else 'SIMILAR routing (not significantly different)'}")

        routing_chi2_results[sg] = {
            'chi2': round(float(chi2), 2),
            'p': round(float(p), 6),
            'dof': int(dof),
            'V': round(float(V), 3),
            'significant': bool(sig),
            'classified_n': cls_n,
            'un_n': un_n,
        }

# ==============================================================================
# SECTION 3: AX-UN MIDDLE OVERLAP
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 3: AX-UN MIDDLE OVERLAP")
print("=" * 70)

# Classified AX MIDDLEs
cls_ax_middles = set()
cls_ax_middle_counts = Counter()
for t, sg, m, key, pos, line_len in classified_ax:
    if m.middle:
        cls_ax_middles.add(m.middle)
        cls_ax_middle_counts[m.middle] += 1

# AX-UN MIDDLEs
un_ax_middles = set()
un_ax_middle_counts = Counter()
for t, m, key, pos, line_len, pos_sg, pre_sg in ax_un_classified:
    if m.middle:
        un_ax_middles.add(m.middle)
        un_ax_middle_counts[m.middle] += 1

print(f"\nClassified AX unique MIDDLEs: {len(cls_ax_middles)}")
print(f"AX-UN unique MIDDLEs: {len(un_ax_middles)}")

shared = cls_ax_middles & un_ax_middles
only_cls = cls_ax_middles - un_ax_middles
only_un = un_ax_middles - cls_ax_middles

print(f"\nOverlap:")
print(f"  Shared: {len(shared)}")
if un_ax_middles:
    print(f"    = {len(shared) / len(un_ax_middles) * 100:.1f}% of AX-UN MIDDLEs")
    print(f"    = {len(shared) / len(cls_ax_middles) * 100:.1f}% of classified AX MIDDLEs")
print(f"  Classified-only: {len(only_cls)}")
print(f"  AX-UN-only (novel): {len(only_un)}")

union = cls_ax_middles | un_ax_middles
jaccard = len(shared) / len(union) if union else 0
print(f"  Jaccard similarity: {jaccard:.3f}")

# Token coverage of shared MIDDLEs
total_un_mid_tokens = sum(un_ax_middle_counts.values())
shared_token_cov = sum(un_ax_middle_counts[m] for m in shared)
shared_cov_pct = shared_token_cov / total_un_mid_tokens * 100 if total_un_mid_tokens > 0 else 0
print(f"\nShared MIDDLE token coverage: {shared_token_cov}/{total_un_mid_tokens} ({shared_cov_pct:.1f}%)")

# Cross-role analysis of novel AX-UN MIDDLEs
# Build MIDDLE -> role map from all classified tokens
middle_role_map = defaultdict(Counter)
for t in b_tokens:
    word = t.word
    if word in token_to_class:
        cls_str = str(token_to_class[word])
        role_full = class_to_role.get(cls_str, 'UNKNOWN')
        abbrev = ROLE_ABBREV.get(role_full, role_full)
        m = morph.extract(word)
        if m.middle:
            middle_role_map[m.middle][abbrev] += 1

novel_in_other_roles = 0
novel_truly_novel = 0
novel_role_dist = Counter()
for mid in only_un:
    if mid in middle_role_map:
        novel_in_other_roles += 1
        for role in middle_role_map[mid]:
            novel_role_dist[role] += 1
    else:
        novel_truly_novel += 1

print(f"\nNovel AX-UN MIDDLEs ({len(only_un)} types):")
print(f"  Appear in other classified roles: {novel_in_other_roles}")
if novel_in_other_roles > 0:
    print(f"    Role distribution: ", end="")
    for role in ['CC', 'EN', 'FL', 'FQ']:
        if novel_role_dist.get(role, 0) > 0:
            print(f"{role}={novel_role_dist[role]} ", end="")
    print()
print(f"  Truly novel (no classified occurrence): {novel_truly_novel}")

# Specific cross-role MIDDLEs: shared with EN or FQ classified tokens?
en_middles = set()
fq_middles = set()
for word, cls in token_to_class.items():
    cls_str = str(cls)
    role_full = class_to_role.get(cls_str, 'UNKNOWN')
    abbrev = ROLE_ABBREV.get(role_full, role_full)
    m = morph.extract(word)
    if m.middle:
        if abbrev == 'EN':
            en_middles.add(m.middle)
        elif abbrev == 'FQ':
            fq_middles.add(m.middle)

un_shared_en = un_ax_middles & en_middles
un_shared_fq = un_ax_middles & fq_middles
print(f"\nAX-UN MIDDLEs shared with classified EN: {len(un_shared_en)}")
print(f"AX-UN MIDDLEs shared with classified FQ: {len(un_shared_fq)}")
print(f"AX-UN MIDDLEs shared with classified AX: {len(shared)}")

# Top 15 shared MIDDLEs
print(f"\nTop 15 shared MIDDLEs (classified AX & AX-UN):")
print(f"  {'MIDDLE':<12} {'Cls n':>8} {'UN n':>8} {'Total':>8}")
print(f"  {'-' * 40}")
for mid in sorted(shared, key=lambda m: un_ax_middle_counts[m], reverse=True)[:15]:
    c = cls_ax_middle_counts[mid]
    u = un_ax_middle_counts[mid]
    print(f"  {mid:<12} {c:>8} {u:>8} {c + u:>8}")

# ==============================================================================
# SECTION 4: COMBINED AX PROFILE
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 4: COMBINED AX PROFILE")
print("=" * 70)

# Classified AX subgroup counts
cls_sg = Counter(sg for _, sg, _, _, _, _ in classified_ax)
cls_total_ax = sum(cls_sg.values())

# AX-UN subgroup counts (PREFIX-based where available, position otherwise)
un_sg = Counter()
for t, m, key, pos, line_len, pos_sg, pre_sg in ax_un_classified:
    sg = pre_sg if pre_sg else pos_sg
    un_sg[sg] += 1
un_total_ax = sum(un_sg.values())

# Combined
combined_sg = Counter()
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    combined_sg[sg] = cls_sg.get(sg, 0) + un_sg.get(sg, 0)
combined_total = sum(combined_sg.values())

print(f"\n{'Subgroup':<12} {'Classified':>12} {'%':>7} {'AX-UN':>10} {'%':>7} {'Combined':>10} {'%':>7}")
print(f"{'-' * 68}")
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    c = cls_sg.get(sg, 0)
    u = un_sg.get(sg, 0)
    t = combined_sg[sg]
    cp = c / cls_total_ax * 100 if cls_total_ax > 0 else 0
    up = u / un_total_ax * 100 if un_total_ax > 0 else 0
    tp = t / combined_total * 100 if combined_total > 0 else 0
    print(f"{sg:<12} {c:>12} {cp:>6.1f}% {u:>10} {up:>6.1f}% {t:>10} {tp:>6.1f}%")
print(f"{'TOTAL':<12} {cls_total_ax:>12} {'':>7} {un_total_ax:>10} {'':>7} {combined_total:>10}")

# B population shift
print(f"\nB population shift:")
print(f"  Classified AX: {cls_total_ax} ({cls_total_ax / total_b * 100:.1f}% of B)")
print(f"  Combined AX (+ UN): {combined_total} ({combined_total / total_b * 100:.1f}% of B)")
print(f"  Growth: +{un_total_ax} tokens (+{(combined_total / cls_total_ax - 1) * 100:.1f}%)")

# Routing comparison: classified-only vs combined
print(f"\nRouting shift (classified vs combined):")
combined_routing = defaultdict(Counter)
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    for role in roles_order:
        combined_routing[sg][role] = cls_routing[sg].get(role, 0) + un_routing[sg].get(role, 0)

for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    cls_dist = cls_routing[sg]
    comb_dist = combined_routing[sg]
    cls_n = sum(cls_dist.values())
    comb_n = sum(comb_dist.values())

    if cls_n == 0 or comb_n == 0:
        continue

    print(f"\n  {sg}:")
    print(f"  {'Role':<6} {'Cls %':>10} {'Combined %':>12} {'Delta':>8}")
    print(f"  {'-' * 40}")
    for role in roles_order:
        cp = cls_dist.get(role, 0) / cls_n * 100
        bp = comb_dist.get(role, 0) / comb_n * 100
        delta = bp - cp
        print(f"  {role:<6} {cp:>9.1f}% {bp:>11.1f}% {delta:>+7.1f}%")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

results = {
    'ax_un_count': len(ax_un_tokens),
    'subgroup_classification': {
        'position_based': dict(pos_counts),
        'prefix_based': dict(prefix_sg_counts),
        'unassigned_prefix': unassigned,
        'agreement_rate': round(agree_pct / 100, 3),
    },
    'routing_comparison': routing_chi2_results,
    'middle_overlap': {
        'classified_unique': len(cls_ax_middles),
        'un_unique': len(un_ax_middles),
        'shared': len(shared),
        'novel': len(only_un),
        'jaccard': round(jaccard, 3),
        'shared_token_coverage_pct': round(shared_cov_pct, 1),
        'truly_novel': novel_truly_novel,
        'cross_role_en': len(un_shared_en),
        'cross_role_fq': len(un_shared_fq),
    },
    'combined_profile': {
        'classified_ax': cls_total_ax,
        'ax_un': un_total_ax,
        'combined': combined_total,
        'classified_pct_of_b': round(cls_total_ax / total_b * 100, 1),
        'combined_pct_of_b': round(combined_total / total_b * 100, 1),
        'subgroups': {sg: combined_sg[sg] for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']},
    },
}

output_path = 'phases/AX_BEHAVIORAL_UNPACKING/results/ax_un_integration.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\n{'=' * 70}")
print("AX-UN INTEGRATION COMPLETE")
print(f"{'=' * 70}")
