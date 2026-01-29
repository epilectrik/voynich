#!/usr/bin/env python3
"""
HAZARD_CIRCUIT_TOKEN_RESOLUTION - Script 1: Hazard Circuit Token Mapping

Maps each of the 17 forbidden transitions to their position in the hazard
circuit (C601: FL_HAZ -> FQ_CONN -> EN_CHSH). Tests whether forbidden
transitions are disproportionately reverse-circuit flows.

Sections:
  1. Forbidden pair sub-group classification
  2. Circuit direction analysis (forward/reverse/self-loop)
  3. Forward vs reverse traffic volume
  4. Unclassified token characterization (c, ee, he, t)

Constraint references:
  C109: 17 forbidden transitions
  C541: 6 hazard classes
  C601: Hazard circuit FL_HAZ -> FQ_CONN -> EN_CHSH
  C622-C624: Hazard exposure, morphology, boundary architecture
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
# SUB-GROUP CLASSIFICATION
# ============================================================
CLASS_TO_SUBGROUP = {}

# EN sub-groups
for c in [8, 31]:
    CLASS_TO_SUBGROUP[c] = 'EN_CHSH'
for c in [32, 33, 34, 35, 36, 41, 44, 45, 46, 49]:
    CLASS_TO_SUBGROUP[c] = 'EN_QO'
for c in [37, 39, 42, 43, 47, 48]:
    CLASS_TO_SUBGROUP[c] = 'EN_MINOR'

# FQ sub-groups
CLASS_TO_SUBGROUP[9] = 'FQ_CONN'
CLASS_TO_SUBGROUP[23] = 'FQ_CLOSER'
for c in [13, 14]:
    CLASS_TO_SUBGROUP[c] = 'FQ_PAIR'

# FL sub-groups
for c in [7, 30]:
    CLASS_TO_SUBGROUP[c] = 'FL_HAZ'
for c in [38, 40]:
    CLASS_TO_SUBGROUP[c] = 'FL_SAFE'

# CC sub-groups
CLASS_TO_SUBGROUP[10] = 'CC_DAIIN'
CLASS_TO_SUBGROUP[11] = 'CC_OL'
CLASS_TO_SUBGROUP[17] = 'CC_OL_D'
CLASS_TO_SUBGROUP[12] = 'CC_OTHER'

# AX
for c in list(range(1, 7)) + list(range(15, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_SUBGROUP:
        CLASS_TO_SUBGROUP[c] = 'AX'

HAZARD_CLASSES = {7, 8, 9, 23, 30, 31}

# Circuit direction: FL_HAZ -> FQ_CONN -> EN_CHSH
# Forward = FL->FQ, FQ->EN, FL->EN
# Reverse = EN->FQ, EN->FL, FQ->FL
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
    """Classify circuit direction of a sub-group transition."""
    if src_sg == tgt_sg:
        return 'SELF_LOOP'
    if (src_sg, tgt_sg) in FORWARD_PAIRS:
        return 'FORWARD'
    if (src_sg, tgt_sg) in REVERSE_PAIRS:
        return 'REVERSE'
    # Cross-group: involves FQ_CLOSER<->FQ_CONN or other non-main transitions
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
    """Build per-folio, per-line token sequences for Currier B."""
    tx = Transcript()
    sequences = defaultdict(list)
    for token in tx.currier_b():
        key = (token.folio, token.line)
        sequences[key].append(token.word)
    return sequences


# ============================================================
# SECTION 1: FORBIDDEN PAIR SUB-GROUP CLASSIFICATION
# ============================================================
def section1_subgroup_classification(forbidden_inv, token_to_class):
    print("=" * 70)
    print("SECTION 1: FORBIDDEN PAIR SUB-GROUP CLASSIFICATION")
    print("=" * 70)
    print()

    transitions = forbidden_inv['transitions']

    classified = []
    unclassified_tokens = set()

    print(f"{'ID':>3} {'Source':>10} {'Target':>10} {'SrcClass':>9} {'TgtClass':>9} "
          f"{'SrcSubGrp':>12} {'TgtSubGrp':>12}")
    print("-" * 70)

    for t in transitions:
        src = t['source']
        tgt = t['target']
        src_cls = token_to_class.get(src)
        tgt_cls = token_to_class.get(tgt)
        src_sg = CLASS_TO_SUBGROUP.get(src_cls, 'UNCLASSIFIED') if src_cls is not None else 'UNCLASSIFIED'
        tgt_sg = CLASS_TO_SUBGROUP.get(tgt_cls, 'UNCLASSIFIED') if tgt_cls is not None else 'UNCLASSIFIED'

        if src_sg == 'UNCLASSIFIED':
            unclassified_tokens.add(src)
        if tgt_sg == 'UNCLASSIFIED':
            unclassified_tokens.add(tgt)

        entry = {
            'id': t['id'],
            'source': src,
            'target': tgt,
            'source_class': src_cls,
            'target_class': tgt_cls,
            'source_subgroup': src_sg,
            'target_subgroup': tgt_sg,
        }
        classified.append(entry)

        sc_str = str(src_cls) if src_cls is not None else '???'
        tc_str = str(tgt_cls) if tgt_cls is not None else '???'
        print(f"{t['id']:3d} {src:>10} {tgt:>10} {sc_str:>9} {tc_str:>9} "
              f"{src_sg:>12} {tgt_sg:>12}")

    print()
    print(f"Unclassified tokens (not in 480-token class map): {sorted(unclassified_tokens)}")

    # Count sub-group pair types
    pair_counts = Counter()
    for entry in classified:
        pair = (entry['source_subgroup'], entry['target_subgroup'])
        pair_counts[pair] += 1

    print()
    print("Sub-group pair distribution of forbidden transitions:")
    for (src_sg, tgt_sg), count in pair_counts.most_common():
        print(f"  {src_sg:>12} -> {tgt_sg:<12}: {count}")

    # Count classifiable vs unclassifiable
    fully_classified = sum(1 for e in classified
                          if e['source_subgroup'] != 'UNCLASSIFIED'
                          and e['target_subgroup'] != 'UNCLASSIFIED')
    partially_classified = sum(1 for e in classified
                              if (e['source_subgroup'] == 'UNCLASSIFIED') !=
                              (e['target_subgroup'] == 'UNCLASSIFIED'))
    unclassifiable = sum(1 for e in classified
                        if e['source_subgroup'] == 'UNCLASSIFIED'
                        and e['target_subgroup'] == 'UNCLASSIFIED')

    print()
    print(f"Fully classified: {fully_classified}/17")
    print(f"Partially classified: {partially_classified}/17")
    print(f"Fully unclassified: {unclassifiable}/17")
    print()

    return classified, unclassified_tokens


# ============================================================
# SECTION 2: CIRCUIT DIRECTION ANALYSIS
# ============================================================
def section2_direction_analysis(classified, sequences, token_to_class):
    print("=" * 70)
    print("SECTION 2: CIRCUIT DIRECTION ANALYSIS")
    print("=" * 70)
    print()

    # Classify direction for each forbidden pair
    forbidden_directions = []
    for entry in classified:
        src_sg = entry['source_subgroup']
        tgt_sg = entry['target_subgroup']
        if src_sg == 'UNCLASSIFIED' or tgt_sg == 'UNCLASSIFIED':
            direction = 'UNCLASSIFIABLE'
        else:
            direction = classify_direction(src_sg, tgt_sg)
        entry['direction'] = direction
        forbidden_directions.append(direction)

    # Print forbidden pair directions
    print("Forbidden pair circuit directions:")
    for entry in classified:
        print(f"  #{entry['id']:2d}: {entry['source']:>10} -> {entry['target']:<10} "
              f"({entry['source_subgroup']:>12} -> {entry['target_subgroup']:<12}) = {entry['direction']}")
    print()

    # Count forbidden by direction
    forb_dir_counts = Counter(forbidden_directions)
    print("Forbidden transition direction distribution:")
    for d, c in forb_dir_counts.most_common():
        print(f"  {d:>15}: {c}")
    print()

    # Now classify ALL observed hazard-class transitions
    all_hazard_transitions = Counter()  # (src_sg, tgt_sg) -> count
    all_hazard_directions = Counter()   # direction -> count

    forbidden_pairs = set()
    for entry in classified:
        forbidden_pairs.add((entry['source'], entry['target']))

    for key in sorted(sequences.keys()):
        words = sequences[key]
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            c1 = token_to_class.get(w1)
            c2 = token_to_class.get(w2)
            if c1 is not None and c2 is not None:
                if c1 in HAZARD_CLASSES and c2 in HAZARD_CLASSES:
                    sg1 = CLASS_TO_SUBGROUP.get(c1, 'UNK')
                    sg2 = CLASS_TO_SUBGROUP.get(c2, 'UNK')
                    all_hazard_transitions[(sg1, sg2)] += 1
                    direction = classify_direction(sg1, sg2)
                    all_hazard_directions[direction] += 1

    total_hazard_bigrams = sum(all_hazard_directions.values())

    print("ALL hazard-class transition direction distribution:")
    for d in ['FORWARD', 'REVERSE', 'SELF_LOOP', 'CROSS_GROUP']:
        c = all_hazard_directions.get(d, 0)
        pct = c / total_hazard_bigrams * 100 if total_hazard_bigrams > 0 else 0
        print(f"  {d:>15}: {c:5d} ({pct:.1f}%)")
    print(f"  {'TOTAL':>15}: {total_hazard_bigrams}")
    print()

    # Fisher's exact test: forbidden x direction (REVERSE vs non-REVERSE)
    # Only use classifiable forbidden pairs
    classifiable = [e for e in classified if e['direction'] != 'UNCLASSIFIABLE']
    n_classifiable = len(classifiable)
    n_forb_reverse = sum(1 for e in classifiable if e['direction'] == 'REVERSE')
    n_forb_nonreverse = n_classifiable - n_forb_reverse

    # For all observed hazard transitions
    n_all_reverse = all_hazard_directions.get('REVERSE', 0)
    n_all_nonreverse = total_hazard_bigrams - n_all_reverse

    # 2x2 table: forbidden/not-forbidden x reverse/not-reverse
    # But we need to be careful: forbidden transitions have 0 corpus occurrences
    # So we compare the TYPE distribution (unique pairs), not token counts
    # Count unique observed pair types by direction
    observed_pair_directions = Counter()
    observed_pairs_by_dir = defaultdict(set)
    for key in sorted(sequences.keys()):
        words = sequences[key]
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            c1 = token_to_class.get(w1)
            c2 = token_to_class.get(w2)
            if c1 is not None and c2 is not None:
                if c1 in HAZARD_CLASSES and c2 in HAZARD_CLASSES:
                    sg1 = CLASS_TO_SUBGROUP.get(c1, 'UNK')
                    sg2 = CLASS_TO_SUBGROUP.get(c2, 'UNK')
                    direction = classify_direction(sg1, sg2)
                    if (w1, w2) not in forbidden_pairs:
                        observed_pairs_by_dir[direction].add((w1, w2))

    print("Unique observed (non-forbidden) pair types by direction:")
    for d in ['FORWARD', 'REVERSE', 'SELF_LOOP', 'CROSS_GROUP']:
        n = len(observed_pairs_by_dir.get(d, set()))
        print(f"  {d:>15}: {n} unique pairs")
    print()

    # Compare: forbidden concentration by direction
    print("Forbidden concentration by direction:")
    print(f"{'Direction':>15} {'Forbidden':>10} {'Observed':>10} {'Forb%':>8}")
    print("-" * 50)
    for d in ['FORWARD', 'REVERSE', 'SELF_LOOP', 'CROSS_GROUP']:
        n_forb = sum(1 for e in classifiable if e['direction'] == d)
        n_obs = len(observed_pairs_by_dir.get(d, set()))
        total = n_forb + n_obs
        pct = n_forb / total * 100 if total > 0 else 0
        print(f"{d:>15} {n_forb:10d} {n_obs:10d} {pct:7.1f}%")
    print()

    # Fisher's exact: reverse vs non-reverse x forbidden vs non-forbidden
    # Using unique pair counts
    a = n_forb_reverse  # forbidden + reverse
    b = sum(1 for e in classifiable if e['direction'] != 'REVERSE')  # forbidden + non-reverse
    c = len(observed_pairs_by_dir.get('REVERSE', set()))  # non-forbidden + reverse
    d_val = sum(len(s) for dir_key, s in observed_pairs_by_dir.items() if dir_key != 'REVERSE')

    print(f"Fisher's exact 2x2 (reverse vs non-reverse x forbidden vs observed):")
    print(f"                    Reverse  Non-Reverse")
    print(f"  Forbidden:         {a:5d}       {b:5d}")
    print(f"  Non-forbidden:     {c:5d}       {d_val:5d}")

    fisher_p = fisher_exact_2x2(a, b, c, d_val)
    odds = (a * d_val) / (b * c) if b > 0 and c > 0 else float('inf')
    print(f"  Odds ratio: {odds:.2f}")
    print(f"  Fisher's exact p: {fisher_p:.6f}")
    print()

    return {
        'forbidden_directions': {e['id']: e['direction'] for e in classified},
        'direction_counts': {
            'forbidden': dict(forb_dir_counts),
            'all_hazard_volume': dict(all_hazard_directions),
            'observed_unique_pairs': {d: len(s) for d, s in observed_pairs_by_dir.items()},
        },
        'fisher_test': {
            'table': [[a, b], [c, d_val]],
            'odds_ratio': round(odds, 3) if odds != float('inf') else 'inf',
            'p_value': round(fisher_p, 6),
        },
        'classified_pairs': [
            {k: v for k, v in e.items()}
            for e in classified
        ],
    }


# ============================================================
# SECTION 3: FORWARD VS REVERSE TRAFFIC VOLUME
# ============================================================
def section3_traffic_volume(sequences, token_to_class):
    print("=" * 70)
    print("SECTION 3: FORWARD VS REVERSE TRAFFIC VOLUME")
    print("=" * 70)
    print()

    # Count ALL transitions between hazard sub-groups with direction
    direction_volume = Counter()         # direction -> token count
    direction_unique = defaultdict(set)  # direction -> set of unique pairs

    for key in sorted(sequences.keys()):
        words = sequences[key]
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            c1 = token_to_class.get(w1)
            c2 = token_to_class.get(w2)
            if c1 is not None and c2 is not None:
                if c1 in HAZARD_CLASSES and c2 in HAZARD_CLASSES:
                    sg1 = CLASS_TO_SUBGROUP.get(c1, 'UNK')
                    sg2 = CLASS_TO_SUBGROUP.get(c2, 'UNK')
                    direction = classify_direction(sg1, sg2)
                    direction_volume[direction] += 1
                    direction_unique[direction].add((w1, w2))

    total = sum(direction_volume.values())

    print(f"{'Direction':>15} {'Volume':>8} {'Vol%':>7} {'UniqueP':>8} {'VolPerP':>9}")
    print("-" * 55)
    for d in ['FORWARD', 'REVERSE', 'SELF_LOOP', 'CROSS_GROUP']:
        vol = direction_volume.get(d, 0)
        pct = vol / total * 100 if total > 0 else 0
        uniq = len(direction_unique.get(d, set()))
        vol_per = vol / uniq if uniq > 0 else 0
        print(f"{d:>15} {vol:8d} {pct:6.1f}% {uniq:8d} {vol_per:9.1f}")
    print(f"{'TOTAL':>15} {total:8d}")
    print()

    # Sub-group pair detail
    sgpair_volume = Counter()
    sgpair_unique = defaultdict(set)
    for key in sorted(sequences.keys()):
        words = sequences[key]
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            c1 = token_to_class.get(w1)
            c2 = token_to_class.get(w2)
            if c1 is not None and c2 is not None:
                if c1 in HAZARD_CLASSES and c2 in HAZARD_CLASSES:
                    sg1 = CLASS_TO_SUBGROUP.get(c1, 'UNK')
                    sg2 = CLASS_TO_SUBGROUP.get(c2, 'UNK')
                    sgpair_volume[(sg1, sg2)] += 1
                    sgpair_unique[(sg1, sg2)].add((w1, w2))

    print("Sub-group pair detail:")
    print(f"{'Source':>12} {'Target':>12} {'Dir':>12} {'Volume':>8} {'Unique':>8}")
    print("-" * 60)
    for (sg1, sg2), vol in sorted(sgpair_volume.items(), key=lambda x: -x[1]):
        d = classify_direction(sg1, sg2)
        uniq = len(sgpair_unique[(sg1, sg2)])
        print(f"{sg1:>12} {sg2:>12} {d:>12} {vol:8d} {uniq:8d}")
    print()

    return {
        'direction_volume': {d: direction_volume.get(d, 0) for d in ['FORWARD', 'REVERSE', 'SELF_LOOP', 'CROSS_GROUP']},
        'direction_unique_pairs': {d: len(direction_unique.get(d, set())) for d in ['FORWARD', 'REVERSE', 'SELF_LOOP', 'CROSS_GROUP']},
        'sgpair_detail': {
            f"{sg1}->{sg2}": {'volume': vol, 'unique': len(sgpair_unique[(sg1, sg2)]),
                              'direction': classify_direction(sg1, sg2)}
            for (sg1, sg2), vol in sgpair_volume.items()
        },
    }


# ============================================================
# SECTION 4: UNCLASSIFIED TOKEN CHARACTERIZATION
# ============================================================
def section4_unclassified_tokens(unclassified_tokens, sequences, token_to_class):
    print("=" * 70)
    print("SECTION 4: UNCLASSIFIED TOKEN CHARACTERIZATION")
    print("=" * 70)
    print()

    morph = Morphology()
    kernel_operators = {'k', 'h', 'e'}

    results = {}
    for tok in sorted(unclassified_tokens):
        # Corpus count
        count = 0
        neighbors = Counter()
        for key in sorted(sequences.keys()):
            words = sequences[key]
            for i, w in enumerate(words):
                if w == tok:
                    count += 1
                    if i > 0:
                        prev_cls = token_to_class.get(words[i - 1])
                        if prev_cls is not None:
                            sg = CLASS_TO_SUBGROUP.get(prev_cls, f'c{prev_cls}')
                            neighbors[f'prev:{sg}'] += 1
                    if i < len(words) - 1:
                        next_cls = token_to_class.get(words[i + 1])
                        if next_cls is not None:
                            sg = CLASS_TO_SUBGROUP.get(next_cls, f'c{next_cls}')
                            neighbors[f'next:{sg}'] += 1

        # Morphology
        m = morph.extract(tok)

        # Kernel-adjacent check
        is_kernel_adjacent = tok in kernel_operators or any(
            tok.startswith(k) or tok.endswith(k) for k in kernel_operators
        )

        print(f"Token: '{tok}'")
        print(f"  Corpus count (B): {count}")
        print(f"  Morphology: art={m.articulator}, pre={m.prefix}, mid={m.middle}, suf={m.suffix}")
        print(f"  Length: {len(tok)}")
        print(f"  Kernel-adjacent: {is_kernel_adjacent} (kernel operators: k, h, e)")
        print(f"  Top neighbors: {neighbors.most_common(5)}")
        print()

        results[tok] = {
            'corpus_count': count,
            'morph': {
                'articulator': m.articulator,
                'prefix': m.prefix,
                'middle': m.middle,
                'suffix': m.suffix,
            },
            'length': len(tok),
            'is_kernel_adjacent': is_kernel_adjacent,
            'top_neighbors': dict(neighbors.most_common(10)),
        }

    return results


# ============================================================
# STATISTICAL UTILITIES
# ============================================================
def fisher_exact_2x2(a, b, c, d):
    """Fisher's exact test for 2x2 contingency table (two-sided p-value)."""
    n = a + b + c + d
    # Use hypergeometric distribution
    # P(X=a) = C(a+b,a) * C(c+d,c) / C(n, a+c)
    # Sum probabilities as extreme or more extreme than observed

    row1 = a + b
    row2 = c + d
    col1 = a + c
    col2 = b + d

    # Calculate probability of observed table
    def log_hypergeometric(x):
        """Log probability of observing x in cell (0,0)."""
        return (log_comb(row1, x) + log_comb(row2, col1 - x) - log_comb(n, col1))

    p_observed = math.exp(log_hypergeometric(a))

    # Sum all tables with probability <= p_observed
    min_a = max(0, col1 - row2)
    max_a = min(row1, col1)

    p_value = 0.0
    for x in range(min_a, max_a + 1):
        p_x = math.exp(log_hypergeometric(x))
        if p_x <= p_observed * 1.00001:  # small tolerance for floating point
            p_value += p_x

    return min(p_value, 1.0)


def log_comb(n, k):
    """Log of binomial coefficient C(n, k)."""
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
    print("HAZARD CIRCUIT TOKEN RESOLUTION: CIRCUIT MAPPING")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    ctm = load_class_token_map()
    token_to_class = {k: int(v) for k, v in ctm['token_to_class'].items()}
    forbidden_inv = load_forbidden_inventory()
    print(f"  Token-to-class: {len(token_to_class)} entries")
    print(f"  Forbidden transitions: {forbidden_inv['total_forbidden']}")

    print("Loading Currier B sequences...")
    sequences = build_b_token_sequences()
    total_tokens = sum(len(v) for v in sequences.values())
    print(f"  Lines: {len(sequences)}, Tokens: {total_tokens}")
    print()

    # Section 1
    classified, unclassified_tokens = section1_subgroup_classification(
        forbidden_inv, token_to_class)

    # Section 2
    direction_results = section2_direction_analysis(
        classified, sequences, token_to_class)

    # Section 3
    traffic_results = section3_traffic_volume(sequences, token_to_class)

    # Section 4
    unclass_results = section4_unclassified_tokens(
        unclassified_tokens, sequences, token_to_class)

    # Save results
    output = {
        'metadata': {
            'phase': 'HAZARD_CIRCUIT_TOKEN_RESOLUTION',
            'script': 'hazard_circuit_token_mapping',
            'timestamp': datetime.now().isoformat(),
            'total_forbidden': forbidden_inv['total_forbidden'],
            'total_b_tokens': total_tokens,
        },
        'section1_classification': {
            'classified_pairs': direction_results['classified_pairs'],
            'unclassified_tokens': sorted(unclassified_tokens),
        },
        'section2_direction_analysis': direction_results,
        'section3_traffic_volume': traffic_results,
        'section4_unclassified': unclass_results,
    }

    output_path = PROJECT_ROOT / 'phases' / 'HAZARD_CIRCUIT_TOKEN_RESOLUTION' / 'results' / 'hazard_circuit_token_mapping.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
