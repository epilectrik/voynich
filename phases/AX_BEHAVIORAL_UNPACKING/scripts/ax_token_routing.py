#!/usr/bin/env python3
"""
AX BEHAVIORAL UNPACKING - Script 1: Token-Level Routing

Tests whether AX MIDDLE adds routing signal beyond positional subgroup.
C572 showed class-level collapse; this tests MIDDLE-level differentiation.

Sections:
1. MIDDLE-Level Routing Within AX Subgroups
2. AX MIDDLE -> Successor MIDDLE Matching (Priming Test)
3. AX MIDDLE Diversity and Folio Complexity
4. Class 22 Deep Dive
"""

import os
import sys
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency, spearmanr

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("=" * 70)
print("AX BEHAVIORAL UNPACKING - Script 1: Token-Level Routing")
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
print(f"Total Currier B tokens: {len(b_tokens)}")

line_seqs = defaultdict(list)
for t in b_tokens:
    line_seqs[(t.folio, t.line)].append(t)

# Classify all AX tokens with subgroup + morphology
ax_tokens_data = []  # (token, subgroup, morph, line_key, position_in_line)
all_b_classified = []

for key, seq in line_seqs.items():
    for i, t in enumerate(seq):
        role = get_role(t.word)
        m = morph.extract(t.word)
        all_b_classified.append((t, role, m, key, i))

        if role == 'AX':
            cls_num = token_to_class.get(t.word)
            if cls_num is not None:
                sg = get_subgroup(cls_num)
                if sg:
                    ax_tokens_data.append((t, sg, m, key, i))

print(f"AX tokens with subgroup: {len(ax_tokens_data)}")
print(f"  AX_INIT: {sum(1 for _, sg, _, _, _ in ax_tokens_data if sg == 'AX_INIT')}")
print(f"  AX_MED:  {sum(1 for _, sg, _, _, _ in ax_tokens_data if sg == 'AX_MED')}")
print(f"  AX_FINAL:{sum(1 for _, sg, _, _, _ in ax_tokens_data if sg == 'AX_FINAL')}")

# ==============================================================================
# SECTION 1: MIDDLE-LEVEL ROUTING WITHIN AX SUBGROUPS
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 1: MIDDLE-LEVEL ROUTING WITHIN AX SUBGROUPS")
print("=" * 70)

# For each AX token, find the next token and its role
def get_next_role(line_key, pos_in_line):
    """Get role of the next token in the same line."""
    seq = line_seqs[line_key]
    if pos_in_line + 1 < len(seq):
        next_word = seq[pos_in_line + 1].word
        return get_role(next_word)
    return None

# Group by (subgroup, MIDDLE) -> next_role distribution
for subgroup in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    sg_tokens = [(t, m, key, pos) for t, sg, m, key, pos in ax_tokens_data if sg == subgroup]

    middle_next = defaultdict(Counter)  # middle -> next_role counts
    for t, m, key, pos in sg_tokens:
        mid = m.middle if m.middle else '_NONE_'
        next_role = get_next_role(key, pos)
        if next_role:
            middle_next[mid][next_role] += 1

    # Filter MIDDLEs with >= 20 tokens
    valid_middles = {mid: dist for mid, dist in middle_next.items() if sum(dist.values()) >= 20}

    print(f"\n--- {subgroup} (n={len(sg_tokens)}) ---")
    print(f"  MIDDLEs with >=20 successor tokens: {len(valid_middles)}")

    if len(valid_middles) < 2:
        print(f"  Too few MIDDLEs for chi-squared test")
        continue

    # Build contingency table: rows=MIDDLEs, cols=roles
    roles_order = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']
    middles_order = sorted(valid_middles.keys(), key=lambda m: sum(valid_middles[m].values()), reverse=True)

    table = []
    for mid in middles_order:
        row = [valid_middles[mid].get(r, 0) for r in roles_order]
        table.append(row)

    table_arr = np.array(table)
    # Remove zero columns
    nonzero_cols = table_arr.sum(axis=0) > 0
    table_filtered = table_arr[:, nonzero_cols]
    roles_filtered = [r for r, nz in zip(roles_order, nonzero_cols) if nz]

    if table_filtered.shape[0] >= 2 and table_filtered.shape[1] >= 2:
        chi2, p, dof, expected = chi2_contingency(table_filtered)
        n_total = table_filtered.sum()
        k = min(table_filtered.shape)
        cramers_v = np.sqrt(chi2 / (n_total * (k - 1))) if n_total > 0 and k > 1 else 0

        print(f"  Chi-squared: chi2={chi2:.2f}, p={p:.6f}, dof={dof}, V={cramers_v:.3f}")
        print(f"  {'SIGNIFICANT' if p < 0.05 else 'NOT SIGNIFICANT'}: MIDDLE {'DOES' if p < 0.05 else 'does NOT'} predict successor role")

    # Show top MIDDLEs
    print(f"\n  {'MIDDLE':<12} {'N':>5} {'CC':>6} {'EN':>6} {'FL':>6} {'FQ':>6} {'AX':>6} {'UN':>6}")
    print(f"  {'-'*55}")
    for mid in middles_order[:10]:
        dist = valid_middles[mid]
        n = sum(dist.values())
        vals = [f"{dist.get(r, 0)/n*100:5.1f}%" for r in roles_order]
        print(f"  {mid:<12} {n:>5} {' '.join(vals)}")

# ==============================================================================
# SECTION 2: AX MIDDLE -> SUCCESSOR MIDDLE MATCHING (PRIMING TEST)
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 2: AX MIDDLE -> SUCCESSOR MIDDLE MATCHING")
print("=" * 70)

# For each AX token, find next non-AX non-UN token in same line
match_data = []  # (ax_middle, successor_middle, subgroup)

for t, sg, m, key, pos in ax_tokens_data:
    ax_mid = m.middle
    if not ax_mid:
        continue

    seq = line_seqs[key]
    for j in range(pos + 1, len(seq)):
        next_word = seq[j].word
        next_role = get_role(next_word)
        if next_role not in ('AX', 'UN'):
            next_m = morph.extract(next_word)
            if next_m.middle:
                match_data.append((ax_mid, next_m.middle, sg))
            break

total_pairs = len(match_data)
exact_matches = sum(1 for am, sm, _ in match_data if am == sm)
exact_rate = exact_matches / total_pairs if total_pairs > 0 else 0

print(f"\nTotal AX -> operational successor pairs: {total_pairs}")
print(f"Exact MIDDLE match: {exact_matches} ({exact_rate*100:.2f}%)")

# Null model: shuffle AX MIDDLEs within subgroup
np.random.seed(42)
n_perms = 1000
null_rates = []

for subgroup in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    sg_pairs = [(am, sm) for am, sm, sg in match_data if sg == subgroup]
    if len(sg_pairs) < 10:
        continue

    observed_match = sum(1 for am, sm in sg_pairs if am == sm) / len(sg_pairs)
    ax_mids = [am for am, sm in sg_pairs]
    succ_mids = [sm for am, sm in sg_pairs]

    perm_rates = []
    for _ in range(n_perms):
        shuffled = list(ax_mids)
        np.random.shuffle(shuffled)
        perm_match = sum(1 for a, s in zip(shuffled, succ_mids) if a == s) / len(sg_pairs)
        perm_rates.append(perm_match)

    null_mean = np.mean(perm_rates)
    null_std = np.std(perm_rates)
    z_score = (observed_match - null_mean) / null_std if null_std > 0 else 0
    p_val = np.mean([r >= observed_match for r in perm_rates])

    print(f"\n  {subgroup} (n={len(sg_pairs)}):")
    print(f"    Observed match rate: {observed_match*100:.2f}%")
    print(f"    Null mean: {null_mean*100:.2f}% (std={null_std*100:.2f}%)")
    print(f"    Z-score: {z_score:.2f}, permutation p={p_val:.4f}")
    print(f"    {'PRIMING DETECTED' if p_val < 0.05 else 'No priming effect'}")

# Partial match: shared PP atom
print(f"\nPartial matching (shared substring >= 2 chars):")
partial_matches = 0
for am, sm, _ in match_data:
    # Check if any substring of length >= 2 is shared
    shared = False
    for length in range(min(len(am), len(sm)), 1, -1):
        for start in range(len(am) - length + 1):
            if am[start:start+length] in sm:
                shared = True
                break
        if shared:
            break
    if shared:
        partial_matches += 1

partial_rate = partial_matches / total_pairs if total_pairs > 0 else 0
print(f"  Partial match rate: {partial_matches}/{total_pairs} ({partial_rate*100:.1f}%)")

# ==============================================================================
# SECTION 3: AX MIDDLE DIVERSITY AND FOLIO COMPLEXITY
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 3: AX MIDDLE DIVERSITY AND FOLIO COMPLEXITY")
print("=" * 70)

# Per folio: unique MIDDLEs by role
folio_ax_middles = defaultdict(set)
folio_en_middles = defaultdict(set)
folio_fq_middles = defaultdict(set)
folio_token_counts = Counter()

for t, role, m, key, pos in all_b_classified:
    folio = t.folio
    folio_token_counts[folio] += 1
    if m.middle:
        if role == 'AX':
            folio_ax_middles[folio].add(m.middle)
        elif role == 'EN':
            folio_en_middles[folio].add(m.middle)
        elif role == 'FQ':
            folio_fq_middles[folio].add(m.middle)

folios = sorted(set(t.folio for t in b_tokens))
ax_div = np.array([len(folio_ax_middles.get(f, set())) for f in folios])
en_div = np.array([len(folio_en_middles.get(f, set())) for f in folios])
fq_div = np.array([len(folio_fq_middles.get(f, set())) for f in folios])

print(f"\nFolio-level MIDDLE diversity:")
print(f"  AX: mean={ax_div.mean():.1f}, median={np.median(ax_div):.1f}")
print(f"  EN: mean={en_div.mean():.1f}, median={np.median(en_div):.1f}")
print(f"  FQ: mean={fq_div.mean():.1f}, median={np.median(fq_div):.1f}")

print(f"\nSpearman: AX MIDDLE diversity vs operational diversity:")
for name, arr in [('EN', en_div), ('FQ', fq_div)]:
    rho, p = spearmanr(ax_div, arr)
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
    print(f"  AX vs {name}: rho={rho:+.3f}, p={p:.4f} {sig}")

# AX subgroup balance vs folio characteristics
folio_sg_counts = defaultdict(lambda: Counter())
for t, sg, m, key, pos in ax_tokens_data:
    folio_sg_counts[t.folio][sg] += 1

folio_init_frac = np.array([
    folio_sg_counts[f].get('AX_INIT', 0) / max(sum(folio_sg_counts[f].values()), 1)
    for f in folios
])
folio_final_frac = np.array([
    folio_sg_counts[f].get('AX_FINAL', 0) / max(sum(folio_sg_counts[f].values()), 1)
    for f in folios
])

print(f"\nAX subgroup balance vs operational diversity:")
rho, p = spearmanr(folio_init_frac, en_div)
print(f"  AX_INIT fraction vs EN diversity: rho={rho:+.3f}, p={p:.4f}")
rho, p = spearmanr(folio_final_frac, en_div)
print(f"  AX_FINAL fraction vs EN diversity: rho={rho:+.3f}, p={p:.4f}")

# ==============================================================================
# SECTION 4: CLASS 22 DEEP DIVE
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 4: CLASS 22 DEEP DIVE")
print("=" * 70)

# Class 22 tokens
class_22_words = set()
for word, cls in token_to_class.items():
    if cls == 22:
        class_22_words.add(word)

print(f"\nClass 22 member tokens: {sorted(class_22_words)}")
print(f"  Count: {len(class_22_words)}")

# Find all Class 22 occurrences in B
class_22_occurrences = []
for key, seq in line_seqs.items():
    for i, t in enumerate(seq):
        if t.word in class_22_words:
            class_22_occurrences.append((t, key, i, len(seq)))

print(f"  Total occurrences: {len(class_22_occurrences)}")

# Position distribution
positions = [i / (n - 1) if n > 1 else 0.5 for _, _, i, n in class_22_occurrences]
final_rate = sum(1 for _, _, i, n in class_22_occurrences if i == n - 1) / len(class_22_occurrences)
print(f"\n  Position: mean={np.mean(positions):.3f}, median={np.median(positions):.3f}")
print(f"  Line-final rate: {final_rate*100:.1f}%")

# Compare to other AX_FINAL classes
other_final_classes = {15, 19, 20, 21, 25}
other_final_words = set()
for word, cls in token_to_class.items():
    if cls in other_final_classes:
        other_final_words.add(word)

other_final_occs = []
for key, seq in line_seqs.items():
    for i, t in enumerate(seq):
        if t.word in other_final_words:
            other_final_occs.append((t, key, i, len(seq)))

other_positions = [i / (n - 1) if n > 1 else 0.5 for _, _, i, n in other_final_occs]
other_final_rate = sum(1 for _, _, i, n in other_final_occs if i == n - 1) / len(other_final_occs) if other_final_occs else 0

print(f"\n  Class 22 vs Other AX_FINAL:")
print(f"    Class 22: mean_pos={np.mean(positions):.3f}, final_rate={final_rate*100:.1f}% (n={len(class_22_occurrences)})")
print(f"    Other AX_FINAL: mean_pos={np.mean(other_positions):.3f}, final_rate={other_final_rate*100:.1f}% (n={len(other_final_occs)})")

# Predecessor distribution
c22_prev = Counter()
for t, key, pos, n in class_22_occurrences:
    if pos > 0:
        prev_word = line_seqs[key][pos - 1].word
        c22_prev[get_role(prev_word)] += 1

other_prev = Counter()
for t, key, pos, n in other_final_occs:
    if pos > 0:
        prev_word = line_seqs[key][pos - 1].word
        other_prev[get_role(prev_word)] += 1

print(f"\n  Predecessor role distribution:")
print(f"  {'Role':<6} {'C22':>8} {'C22 %':>8} {'Other':>8} {'Other %':>8}")
print(f"  {'-'*40}")
for role in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
    c22_c = c22_prev.get(role, 0)
    oth_c = other_prev.get(role, 0)
    c22_p = c22_c / sum(c22_prev.values()) * 100 if c22_prev else 0
    oth_p = oth_c / sum(other_prev.values()) * 100 if other_prev else 0
    print(f"  {role:<6} {c22_c:>8} {c22_p:>7.1f}% {oth_c:>8} {oth_p:>7.1f}%")

# Token-level analysis
print(f"\n  Class 22 token frequencies:")
for word in sorted(class_22_words):
    count = sum(1 for t, _, _, _ in class_22_occurrences if t.word == word)
    m = morph.extract(word) if word else None
    mid = m.middle if m else '-'
    print(f"    '{word}': {count}x (MIDDLE={mid})")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

results = {
    'ax_token_count': len(ax_tokens_data),
    'priming': {
        'total_pairs': total_pairs,
        'exact_match_rate': round(exact_rate, 4),
        'partial_match_rate': round(partial_rate, 4),
    },
    'diversity': {
        'ax_en_rho': round(float(spearmanr(ax_div, en_div)[0]), 3),
        'ax_fq_rho': round(float(spearmanr(ax_div, fq_div)[0]), 3),
    },
    'class_22': {
        'member_tokens': sorted(class_22_words),
        'occurrences': len(class_22_occurrences),
        'mean_position': round(float(np.mean(positions)), 3),
        'final_rate': round(final_rate, 3),
    },
}

output_path = 'phases/AX_BEHAVIORAL_UNPACKING/results/ax_token_routing.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\n{'=' * 70}")
print("AX TOKEN ROUTING COMPLETE")
print(f"{'=' * 70}")
