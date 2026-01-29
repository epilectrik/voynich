#!/usr/bin/env python3
"""
HAZARD_CIRCUIT_TOKEN_RESOLUTION - Script 2: Lane-MIDDLE Discrimination

Tests whether CHSH-lane vocabulary predicts forbidden-token MIDDLEs and
whether CC trigger context explains forbidden pair activation.

Sections:
  1. Sub-group MIDDLE vocabulary extraction and cross-reference
  2. CC trigger context for forbidden source tokens
  3. Lane activation context for hazard-class bigrams
  4. Lane x direction interaction

Constraint references:
  C600: CC sub-group selectivity (CC_DAIIN/OL -> CHSH, CC_OL_D -> QO)
  C601: Hazard circuit
  C606: CC->EN line-level routing
  C623: Forbidden tokens are lexically specific
"""

import json
import math
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# SUB-GROUP CLASSIFICATION (same as script 1)
# ============================================================
CLASS_TO_SUBGROUP = {}
for c in [8, 31]:
    CLASS_TO_SUBGROUP[c] = 'EN_CHSH'
for c in [32, 33, 34, 35, 36, 41, 44, 45, 46, 49]:
    CLASS_TO_SUBGROUP[c] = 'EN_QO'
for c in [37, 39, 42, 43, 47, 48]:
    CLASS_TO_SUBGROUP[c] = 'EN_MINOR'
CLASS_TO_SUBGROUP[9] = 'FQ_CONN'
CLASS_TO_SUBGROUP[23] = 'FQ_CLOSER'
for c in [13, 14]:
    CLASS_TO_SUBGROUP[c] = 'FQ_PAIR'
for c in [7, 30]:
    CLASS_TO_SUBGROUP[c] = 'FL_HAZ'
for c in [38, 40]:
    CLASS_TO_SUBGROUP[c] = 'FL_SAFE'
CLASS_TO_SUBGROUP[10] = 'CC_DAIIN'
CLASS_TO_SUBGROUP[11] = 'CC_OL'
CLASS_TO_SUBGROUP[17] = 'CC_OL_D'
CLASS_TO_SUBGROUP[12] = 'CC_OTHER'
for c in list(range(1, 7)) + list(range(15, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_SUBGROUP:
        CLASS_TO_SUBGROUP[c] = 'AX'

HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}
CC_CLASSES = {10, 11, 12, 17}
CC_CHSH_TRIGGERS = {10, 11}   # CC_DAIIN, CC_OL -> CHSH lane
CC_QO_TRIGGERS = {17}          # CC_OL_D -> QO lane
EN_CHSH_CLASSES = {8, 31}
EN_QO_CLASSES = {32, 33, 34, 35, 36, 41, 44, 45, 46, 49}

FORWARD_PAIRS = {
    ('FL_HAZ', 'FQ_CONN'), ('FL_HAZ', 'FQ_CLOSER'),
    ('FQ_CONN', 'EN_CHSH'), ('FQ_CLOSER', 'EN_CHSH'),
    ('FL_HAZ', 'EN_CHSH'),
}
REVERSE_PAIRS = {
    ('EN_CHSH', 'FQ_CONN'), ('EN_CHSH', 'FQ_CLOSER'),
    ('EN_CHSH', 'FL_HAZ'),
    ('FQ_CONN', 'FL_HAZ'), ('FQ_CLOSER', 'FL_HAZ'),
}


def classify_direction(src_sg, tgt_sg):
    if src_sg == tgt_sg:
        return 'SELF_LOOP'
    if (src_sg, tgt_sg) in FORWARD_PAIRS:
        return 'FORWARD'
    if (src_sg, tgt_sg) in REVERSE_PAIRS:
        return 'REVERSE'
    return 'CROSS_GROUP'


# ============================================================
# LOAD DATA
# ============================================================
def load_class_token_map():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_forbidden_inventory():
    path = PROJECT_ROOT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_b_token_sequences():
    tx = Transcript()
    sequences = defaultdict(list)
    for token in tx.currier_b():
        key = (token.folio, token.line)
        sequences[key].append(token.word)
    return sequences


# ============================================================
# SECTION 1: SUB-GROUP MIDDLE VOCABULARY
# ============================================================
def section1_middle_vocabulary(ctm, forbidden_inv, token_to_class):
    print("=" * 70)
    print("SECTION 1: SUB-GROUP MIDDLE VOCABULARY")
    print("=" * 70)
    print()

    morph = Morphology()
    class_to_middles = ctm.get('class_to_middles', {})

    # Build per-sub-group MIDDLE sets
    subgroup_middles = defaultdict(set)
    for cls_str, middles in class_to_middles.items():
        cls = int(cls_str)
        sg = CLASS_TO_SUBGROUP.get(cls, 'OTHER')
        for m in middles:
            if m:
                subgroup_middles[sg].add(m)

    # Print sub-group MIDDLE sets
    hazard_subgroups = ['EN_CHSH', 'FQ_CONN', 'FQ_CLOSER', 'FL_HAZ']
    safe_subgroups = ['EN_QO', 'EN_MINOR', 'FQ_PAIR', 'FL_SAFE']

    for sg in hazard_subgroups + safe_subgroups:
        middles = sorted(subgroup_middles.get(sg, set()))
        print(f"{sg:>12}: {len(middles)} MIDDLEs: {middles[:15]}{'...' if len(middles) > 15 else ''}")
    print()

    # CHSH-lane vocabulary: EN_CHSH + FL_HAZ + FQ_CONN + FQ_CLOSER
    chsh_lane_middles = (subgroup_middles.get('EN_CHSH', set()) |
                         subgroup_middles.get('FL_HAZ', set()) |
                         subgroup_middles.get('FQ_CONN', set()) |
                         subgroup_middles.get('FQ_CLOSER', set()))

    # QO-lane vocabulary: EN_QO + FQ_PAIR + FL_SAFE
    qo_lane_middles = (subgroup_middles.get('EN_QO', set()) |
                       subgroup_middles.get('FQ_PAIR', set()) |
                       subgroup_middles.get('FL_SAFE', set()))

    print(f"CHSH-lane MIDDLEs: {len(chsh_lane_middles)}")
    print(f"QO-lane MIDDLEs: {len(qo_lane_middles)}")
    print(f"Shared: {len(chsh_lane_middles & qo_lane_middles)}")
    print(f"CHSH-exclusive: {len(chsh_lane_middles - qo_lane_middles)}")
    print(f"QO-exclusive: {len(qo_lane_middles - chsh_lane_middles)}")
    print()

    # Cross-reference with forbidden-token MIDDLEs
    transitions = forbidden_inv['transitions']
    forbidden_tokens = set()
    for t in transitions:
        forbidden_tokens.add(t['source'])
        forbidden_tokens.add(t['target'])

    forbidden_middles = set()
    for tok in forbidden_tokens:
        m = morph.extract(tok)
        if m.middle:
            forbidden_middles.add(m.middle)

    # From C623
    forbidden_exclusive = {'aiin', 'al', 'edy', 'ey', 'l'}
    safe_exclusive = {'am', 'd', 'eo', 'i', 'in', 'm', 's', 'y'}
    shared_middles = {'ar', 'dy', 'o', 'ol', 'or', 'r'}

    print("Forbidden-exclusive MIDDLEs vs lane vocabulary:")
    for mid in sorted(forbidden_exclusive):
        in_chsh = mid in chsh_lane_middles
        in_qo = mid in qo_lane_middles
        lane = "CHSH" if in_chsh and not in_qo else "QO" if in_qo and not in_chsh else "BOTH" if in_chsh and in_qo else "NEITHER"
        print(f"  '{mid}': CHSH={in_chsh}, QO={in_qo} -> {lane}")
    print()

    print("Safe-exclusive MIDDLEs vs lane vocabulary:")
    for mid in sorted(safe_exclusive):
        in_chsh = mid in chsh_lane_middles
        in_qo = mid in qo_lane_middles
        lane = "CHSH" if in_chsh and not in_qo else "QO" if in_qo and not in_chsh else "BOTH" if in_chsh and in_qo else "NEITHER"
        print(f"  '{mid}': CHSH={in_chsh}, QO={in_qo} -> {lane}")
    print()

    print("Shared (both forbidden and safe) MIDDLEs vs lane vocabulary:")
    for mid in sorted(shared_middles):
        in_chsh = mid in chsh_lane_middles
        in_qo = mid in qo_lane_middles
        lane = "CHSH" if in_chsh and not in_qo else "QO" if in_qo and not in_chsh else "BOTH" if in_chsh and in_qo else "NEITHER"
        print(f"  '{mid}': CHSH={in_chsh}, QO={in_qo} -> {lane}")
    print()

    # Quantitative summary
    forb_excl_in_chsh = sum(1 for m in forbidden_exclusive if m in chsh_lane_middles)
    forb_excl_in_qo = sum(1 for m in forbidden_exclusive if m in qo_lane_middles)
    safe_excl_in_chsh = sum(1 for m in safe_exclusive if m in chsh_lane_middles)
    safe_excl_in_qo = sum(1 for m in safe_exclusive if m in qo_lane_middles)

    print(f"Summary:")
    print(f"  Forbidden-exclusive in CHSH: {forb_excl_in_chsh}/{len(forbidden_exclusive)}")
    print(f"  Forbidden-exclusive in QO:   {forb_excl_in_qo}/{len(forbidden_exclusive)}")
    print(f"  Safe-exclusive in CHSH:      {safe_excl_in_chsh}/{len(safe_exclusive)}")
    print(f"  Safe-exclusive in QO:        {safe_excl_in_qo}/{len(safe_exclusive)}")
    print()

    return {
        'subgroup_middles': {sg: sorted(middles) for sg, middles in subgroup_middles.items()},
        'chsh_lane_middles': sorted(chsh_lane_middles),
        'qo_lane_middles': sorted(qo_lane_middles),
        'chsh_exclusive': sorted(chsh_lane_middles - qo_lane_middles),
        'qo_exclusive': sorted(qo_lane_middles - chsh_lane_middles),
        'forbidden_exclusive_lane': {
            mid: {
                'in_chsh': mid in chsh_lane_middles,
                'in_qo': mid in qo_lane_middles,
            }
            for mid in sorted(forbidden_exclusive)
        },
        'safe_exclusive_lane': {
            mid: {
                'in_chsh': mid in chsh_lane_middles,
                'in_qo': mid in qo_lane_middles,
            }
            for mid in sorted(safe_exclusive)
        },
    }


# ============================================================
# SECTION 2: CC TRIGGER CONTEXT
# ============================================================
def section2_cc_trigger_context(sequences, token_to_class, forbidden_inv):
    print("=" * 70)
    print("SECTION 2: CC TRIGGER CONTEXT FOR FORBIDDEN SOURCE TOKENS")
    print("=" * 70)
    print()

    transitions = forbidden_inv['transitions']
    forbidden_sources = set(t['source'] for t in transitions)
    forbidden_targets = set(t['target'] for t in transitions)
    all_forbidden_tokens = forbidden_sources | forbidden_targets

    # For each forbidden source token occurrence, find most recent CC token on same line
    cc_before_forbidden = Counter()   # CC sub-group -> count
    cc_before_nonforbidden = Counter()  # CC sub-group -> count (non-forbidden hazard-class tokens)
    total_forbidden_with_cc = 0
    total_nonforbidden_with_cc = 0

    for key in sorted(sequences.keys()):
        words = sequences[key]
        # Track most recent CC token
        last_cc_subgroup = None

        for i, word in enumerate(words):
            cls = token_to_class.get(word)
            if cls is not None and cls in CC_CLASSES:
                last_cc_subgroup = CLASS_TO_SUBGROUP.get(cls, 'CC_OTHER')
                continue

            if cls is not None and cls in HAZARD_CLASSES:
                if last_cc_subgroup is not None:
                    if word in forbidden_sources:
                        cc_before_forbidden[last_cc_subgroup] += 1
                        total_forbidden_with_cc += 1
                    else:
                        cc_before_nonforbidden[last_cc_subgroup] += 1
                        total_nonforbidden_with_cc += 1

    print("CC trigger preceding forbidden source tokens:")
    print(f"  Total forbidden source occurrences with CC context: {total_forbidden_with_cc}")
    for sg, count in cc_before_forbidden.most_common():
        pct = count / total_forbidden_with_cc * 100 if total_forbidden_with_cc > 0 else 0
        print(f"    {sg}: {count} ({pct:.1f}%)")
    print()

    print("CC trigger preceding non-forbidden hazard-class tokens:")
    print(f"  Total: {total_nonforbidden_with_cc}")
    for sg, count in cc_before_nonforbidden.most_common():
        pct = count / total_nonforbidden_with_cc * 100 if total_nonforbidden_with_cc > 0 else 0
        print(f"    {sg}: {count} ({pct:.1f}%)")
    print()

    # Fisher's exact: CHSH trigger (CC_DAIIN/CC_OL) vs QO trigger (CC_OL_D) x forbidden vs non-forbidden
    forb_chsh = cc_before_forbidden.get('CC_DAIIN', 0) + cc_before_forbidden.get('CC_OL', 0)
    forb_qo = cc_before_forbidden.get('CC_OL_D', 0)
    nonf_chsh = cc_before_nonforbidden.get('CC_DAIIN', 0) + cc_before_nonforbidden.get('CC_OL', 0)
    nonf_qo = cc_before_nonforbidden.get('CC_OL_D', 0)

    print(f"Fisher's exact (CHSH/QO trigger x forbidden/non-forbidden):")
    print(f"                   CHSH_trig  QO_trig")
    print(f"  Forbidden:        {forb_chsh:5d}     {forb_qo:5d}")
    print(f"  Non-forbidden:    {nonf_chsh:5d}     {nonf_qo:5d}")

    if forb_qo > 0 and nonf_qo > 0:
        odds = (forb_chsh * nonf_qo) / (forb_qo * nonf_chsh) if forb_qo > 0 and nonf_chsh > 0 else float('inf')
        p = fisher_exact_2x2(forb_chsh, forb_qo, nonf_chsh, nonf_qo)
        print(f"  Odds ratio: {odds:.3f}")
        print(f"  Fisher's p: {p:.6f}")
    else:
        odds = None
        p = None
        print("  Insufficient data for Fisher's test (one cell is zero)")
    print()

    return {
        'cc_before_forbidden': dict(cc_before_forbidden),
        'cc_before_nonforbidden': dict(cc_before_nonforbidden),
        'total_forbidden_with_cc': total_forbidden_with_cc,
        'total_nonforbidden_with_cc': total_nonforbidden_with_cc,
        'fisher_test': {
            'table': [[forb_chsh, forb_qo], [nonf_chsh, nonf_qo]],
            'odds_ratio': round(odds, 3) if odds is not None else None,
            'p_value': round(p, 6) if p is not None else None,
        },
    }


# ============================================================
# SECTION 3: LANE ACTIVATION CONTEXT
# ============================================================
def section3_lane_activation(sequences, token_to_class):
    print("=" * 70)
    print("SECTION 3: LANE ACTIVATION CONTEXT FOR HAZARD BIGRAMS")
    print("=" * 70)
    print()

    # For each hazard-class bigram, look at preceding 3 tokens
    # Classify context as CHSH-lane, QO-lane, or mixed/unclear

    context_by_direction = defaultdict(lambda: Counter())  # direction -> {lane_context: count}

    for key in sorted(sequences.keys()):
        words = sequences[key]
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            c1 = token_to_class.get(w1)
            c2 = token_to_class.get(w2)
            if c1 is None or c2 is None:
                continue
            if c1 not in HAZARD_CLASSES or c2 not in HAZARD_CLASSES:
                continue

            sg1 = CLASS_TO_SUBGROUP.get(c1, 'UNK')
            sg2 = CLASS_TO_SUBGROUP.get(c2, 'UNK')
            direction = classify_direction(sg1, sg2)

            # Look at preceding 3 tokens
            chsh_markers = 0
            qo_markers = 0
            for j in range(max(0, i - 3), i):
                prev_cls = token_to_class.get(words[j])
                if prev_cls is None:
                    continue
                if prev_cls in EN_CHSH_CLASSES or prev_cls in CC_CHSH_TRIGGERS:
                    chsh_markers += 1
                elif prev_cls in EN_QO_CLASSES or prev_cls in CC_QO_TRIGGERS:
                    qo_markers += 1

            if chsh_markers > 0 and qo_markers == 0:
                lane_ctx = 'CHSH'
            elif qo_markers > 0 and chsh_markers == 0:
                lane_ctx = 'QO'
            elif chsh_markers > 0 and qo_markers > 0:
                lane_ctx = 'MIXED'
            else:
                lane_ctx = 'UNCLEAR'

            context_by_direction[direction][lane_ctx] += 1

    # Print results
    print(f"{'Direction':>15} {'CHSH':>8} {'QO':>8} {'MIXED':>8} {'UNCLEAR':>8} {'Total':>8} {'CHSH%':>7}")
    print("-" * 70)
    for d in ['FORWARD', 'REVERSE', 'SELF_LOOP', 'CROSS_GROUP']:
        counts = context_by_direction.get(d, Counter())
        total = sum(counts.values())
        chsh = counts.get('CHSH', 0)
        qo = counts.get('QO', 0)
        mixed = counts.get('MIXED', 0)
        unclear = counts.get('UNCLEAR', 0)
        chsh_pct = chsh / total * 100 if total > 0 else 0
        print(f"{d:>15} {chsh:8d} {qo:8d} {mixed:8d} {unclear:8d} {total:8d} {chsh_pct:6.1f}%")
    print()

    # Chi-squared: direction x lane context
    # Simplify to CHSH vs non-CHSH for 2x2
    directions = ['FORWARD', 'REVERSE', 'SELF_LOOP']
    print("Chi-squared: CHSH context rate differs by direction?")
    for d1 in directions:
        for d2 in directions:
            if d1 >= d2:
                continue
            c1 = context_by_direction.get(d1, Counter())
            c2 = context_by_direction.get(d2, Counter())
            a = c1.get('CHSH', 0)
            b = sum(c1.values()) - a
            c = c2.get('CHSH', 0)
            d_val = sum(c2.values()) - c
            if a + b > 0 and c + d_val > 0:
                p = fisher_exact_2x2(a, b, c, d_val)
                rate1 = a / (a + b) * 100
                rate2 = c / (c + d_val) * 100
                print(f"  {d1} vs {d2}: CHSH rate {rate1:.1f}% vs {rate2:.1f}%, Fisher p={p:.4f}")
    print()

    return {
        'context_by_direction': {
            d: dict(context_by_direction.get(d, Counter()))
            for d in ['FORWARD', 'REVERSE', 'SELF_LOOP', 'CROSS_GROUP']
        },
    }


# ============================================================
# SECTION 4: LANE x DIRECTION INTERACTION
# ============================================================
def section4_lane_direction_interaction(sequences, token_to_class):
    print("=" * 70)
    print("SECTION 4: LANE x DIRECTION INTERACTION")
    print("=" * 70)
    print()

    # Same as section 3 but focus on the key question:
    # Do reverse-circuit transitions concentrate in CHSH-lane contexts?
    # Does this explain QO's hazard immunity?

    # Count how many hazard bigrams in QO-activated context involve QO-lane sub-groups
    qo_context_hazard = Counter()  # sub-group pair -> count
    chsh_context_hazard = Counter()

    for key in sorted(sequences.keys()):
        words = sequences[key]
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            c1 = token_to_class.get(w1)
            c2 = token_to_class.get(w2)
            if c1 is None or c2 is None:
                continue
            if c1 not in HAZARD_CLASSES or c2 not in HAZARD_CLASSES:
                continue

            sg1 = CLASS_TO_SUBGROUP.get(c1, 'UNK')
            sg2 = CLASS_TO_SUBGROUP.get(c2, 'UNK')

            # Context
            chsh_markers = 0
            qo_markers = 0
            for j in range(max(0, i - 3), i):
                prev_cls = token_to_class.get(words[j])
                if prev_cls is None:
                    continue
                if prev_cls in EN_CHSH_CLASSES or prev_cls in CC_CHSH_TRIGGERS:
                    chsh_markers += 1
                elif prev_cls in EN_QO_CLASSES or prev_cls in CC_QO_TRIGGERS:
                    qo_markers += 1

            if qo_markers > 0 and chsh_markers == 0:
                qo_context_hazard[(sg1, sg2)] += 1
            elif chsh_markers > 0 and qo_markers == 0:
                chsh_context_hazard[(sg1, sg2)] += 1

    print("Hazard bigrams in QO-activated context:")
    total_qo = sum(qo_context_hazard.values())
    if total_qo > 0:
        for (sg1, sg2), count in qo_context_hazard.most_common(10):
            d = classify_direction(sg1, sg2)
            print(f"  {sg1:>12} -> {sg2:<12} ({d}): {count}")
    else:
        print("  None found")
    print(f"  Total: {total_qo}")
    print()

    print("Hazard bigrams in CHSH-activated context:")
    total_chsh = sum(chsh_context_hazard.values())
    for (sg1, sg2), count in chsh_context_hazard.most_common(10):
        d = classify_direction(sg1, sg2)
        print(f"  {sg1:>12} -> {sg2:<12} ({d}): {count}")
    print(f"  Total: {total_chsh}")
    print()

    # Key finding: what fraction of hazard bigrams in QO context are reverse-circuit?
    qo_reverse = sum(v for (sg1, sg2), v in qo_context_hazard.items()
                     if classify_direction(sg1, sg2) == 'REVERSE')
    chsh_reverse = sum(v for (sg1, sg2), v in chsh_context_hazard.items()
                       if classify_direction(sg1, sg2) == 'REVERSE')

    print(f"Reverse-circuit transitions in QO context: {qo_reverse}/{total_qo} "
          f"({qo_reverse/total_qo*100:.1f}%)" if total_qo > 0 else "")
    print(f"Reverse-circuit transitions in CHSH context: {chsh_reverse}/{total_chsh} "
          f"({chsh_reverse/total_chsh*100:.1f}%)" if total_chsh > 0 else "")
    print()

    # QO immunity explanation
    print("=" * 50)
    print("QO IMMUNITY EXPLANATION")
    print("=" * 50)
    print()
    print(f"Total hazard bigrams in QO context: {total_qo}")
    print(f"Total hazard bigrams in CHSH context: {total_chsh}")
    if total_qo > 0 and total_chsh > 0:
        ratio = total_chsh / total_qo
        print(f"CHSH/QO ratio: {ratio:.1f}x")
        print(f"Hazard bigrams are {ratio:.1f}x more common in CHSH than QO context")
    print()

    return {
        'qo_context_hazard': {f"{s}->{t}": c for (s, t), c in qo_context_hazard.items()},
        'chsh_context_hazard': {f"{s}->{t}": c for (s, t), c in chsh_context_hazard.items()},
        'qo_reverse': qo_reverse,
        'chsh_reverse': chsh_reverse,
        'total_qo': total_qo,
        'total_chsh': total_chsh,
    }


# ============================================================
# STATISTICAL UTILITIES
# ============================================================
def fisher_exact_2x2(a, b, c, d):
    """Fisher's exact test for 2x2 table (two-sided)."""
    n = a + b + c + d
    row1 = a + b
    row2 = c + d
    col1 = a + c

    def log_hyper(x):
        return (log_comb(row1, x) + log_comb(row2, col1 - x) - log_comb(n, col1))

    p_obs = math.exp(log_hyper(a))
    min_a = max(0, col1 - row2)
    max_a = min(row1, col1)
    p_val = 0.0
    for x in range(min_a, max_a + 1):
        p_x = math.exp(log_hyper(x))
        if p_x <= p_obs * 1.00001:
            p_val += p_x
    return min(p_val, 1.0)


def log_comb(n, k):
    if k < 0 or k > n:
        return float('-inf')
    if k == 0 or k == n:
        return 0.0
    k = min(k, n - k)
    result = 0.0
    for i in range(k):
        result += math.log(n - i) - math.log(i + 1)
    return result


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("HAZARD CIRCUIT TOKEN RESOLUTION: LANE-MIDDLE DISCRIMINATION")
    print("=" * 70)
    print()

    print("Loading data...")
    ctm = load_class_token_map()
    token_to_class = {k: int(v) for k, v in ctm['token_to_class'].items()}
    forbidden_inv = load_forbidden_inventory()

    print("Loading Currier B sequences...")
    sequences = build_b_token_sequences()
    total_tokens = sum(len(v) for v in sequences.values())
    print(f"  Lines: {len(sequences)}, Tokens: {total_tokens}")
    print()

    # Section 1
    vocab_results = section1_middle_vocabulary(ctm, forbidden_inv, token_to_class)

    # Section 2
    cc_results = section2_cc_trigger_context(sequences, token_to_class, forbidden_inv)

    # Section 3
    lane_results = section3_lane_activation(sequences, token_to_class)

    # Section 4
    interaction_results = section4_lane_direction_interaction(sequences, token_to_class)

    # Save
    output = {
        'metadata': {
            'phase': 'HAZARD_CIRCUIT_TOKEN_RESOLUTION',
            'script': 'lane_middle_discrimination',
            'timestamp': datetime.now().isoformat(),
        },
        'section1_middle_vocabulary': vocab_results,
        'section2_cc_trigger_context': cc_results,
        'section3_lane_activation': lane_results,
        'section4_lane_direction': interaction_results,
    }

    output_path = PROJECT_ROOT / 'phases' / 'HAZARD_CIRCUIT_TOKEN_RESOLUTION' / 'results' / 'lane_middle_discrimination.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
