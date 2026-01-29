#!/usr/bin/env python3
"""
HAZARD_CIRCUIT_TOKEN_RESOLUTION - Script 3: Forbidden Pair Selectivity

Within each class pair that contains forbidden transitions, what distinguishes
forbidden from allowed token pairs? Tests frequency, reciprocity, and
circuit direction as predictors.

Sections:
  1. Within-class-pair token discrimination
  2. Token frequency and forbidden status
  3. Reciprocal pair analysis
  4. Predictive summary (all features combined)

Constraint references:
  C109: 17 forbidden transitions
  C601: Hazard circuit
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
# SUB-GROUP CLASSIFICATION (same as scripts 1 and 2)
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
# SECTION 1: WITHIN-CLASS-PAIR TOKEN DISCRIMINATION
# ============================================================
def section1_within_pair_discrimination(sequences, token_to_class, forbidden_inv, class_to_tokens):
    print("=" * 70)
    print("SECTION 1: WITHIN-CLASS-PAIR TOKEN DISCRIMINATION")
    print("=" * 70)
    print()

    transitions = forbidden_inv['transitions']
    forbidden_pairs = set((t['source'], t['target']) for t in transitions)

    # Build map of forbidden pairs by class pair
    forbidden_by_classpair = defaultdict(list)
    for t in transitions:
        sc = token_to_class.get(t['source'])
        tc = token_to_class.get(t['target'])
        if sc is not None and tc is not None:
            forbidden_by_classpair[(sc, tc)].append((t['source'], t['target']))

    # Count all observed transitions between hazard classes
    observed_transitions = defaultdict(lambda: Counter())
    for key in sorted(sequences.keys()):
        words = sequences[key]
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            c1 = token_to_class.get(w1)
            c2 = token_to_class.get(w2)
            if c1 is not None and c2 is not None:
                if c1 in HAZARD_CLASSES and c2 in HAZARD_CLASSES:
                    observed_transitions[(c1, c2)][(w1, w2)] += 1

    # Token frequencies in B
    token_freq = Counter()
    for key in sorted(sequences.keys()):
        for word in sequences[key]:
            token_freq[word] += 1

    morph = Morphology()
    results = {}

    for (c1, c2) in sorted(forbidden_by_classpair.keys()):
        forb_list = forbidden_by_classpair[(c1, c2)]
        obs = observed_transitions.get((c1, c2), Counter())
        n_observed = len(obs)
        total_volume = sum(obs.values())

        sg1 = CLASS_TO_SUBGROUP.get(c1, '?')
        sg2 = CLASS_TO_SUBGROUP.get(c2, '?')
        direction = classify_direction(sg1, sg2)

        print(f"--- Class pair c{c1} -> c{c2} ({sg1} -> {sg2}, {direction}) ---")
        print(f"  Forbidden: {len(forb_list)}, Observed: {n_observed}, Volume: {total_volume}")

        # List all observed with frequencies
        obs_sorted = sorted(obs.items(), key=lambda x: -x[1])
        for (w1, w2), count in obs_sorted:
            is_forb = (w1, w2) in forbidden_pairs
            tag = " [FORBIDDEN]" if is_forb else ""
            src_freq = token_freq.get(w1, 0)
            tgt_freq = token_freq.get(w2, 0)
            m1 = morph.extract(w1)
            m2 = morph.extract(w2)
            print(f"    {w1:>10} -> {w2:<10}: {count:3d}  "
                  f"(freq:{src_freq}/{tgt_freq}, "
                  f"mid:{m1.middle or '-'}/{m2.middle or '-'}){tag}")

        # Also list forbidden pairs that are NOT observed (count=0)
        for (s, t) in forb_list:
            if (s, t) not in obs:
                src_freq = token_freq.get(s, 0)
                tgt_freq = token_freq.get(t, 0)
                m1 = morph.extract(s)
                m2 = morph.extract(t)
                print(f"    {s:>10} -> {t:<10}:   0  "
                      f"(freq:{src_freq}/{tgt_freq}, "
                      f"mid:{m1.middle or '-'}/{m2.middle or '-'}) [FORBIDDEN, never observed]")

        print()

        results[f"c{c1}->c{c2}"] = {
            'source_class': c1,
            'target_class': c2,
            'source_subgroup': sg1,
            'target_subgroup': sg2,
            'direction': direction,
            'n_forbidden': len(forb_list),
            'n_observed': n_observed,
            'total_volume': total_volume,
            'forbidden_pairs': [{'source': s, 'target': t} for s, t in forb_list],
            'observed_pairs': [
                {'source': w1, 'target': w2, 'count': c,
                 'is_forbidden': (w1, w2) in forbidden_pairs}
                for (w1, w2), c in obs_sorted
            ],
        }

    return results


# ============================================================
# SECTION 2: TOKEN FREQUENCY AND FORBIDDEN STATUS
# ============================================================
def section2_frequency_analysis(sequences, token_to_class, class_to_tokens, forbidden_inv):
    print("=" * 70)
    print("SECTION 2: TOKEN FREQUENCY AND FORBIDDEN STATUS")
    print("=" * 70)
    print()

    transitions = forbidden_inv['transitions']
    forbidden_tokens = set()
    for t in transitions:
        forbidden_tokens.add(t['source'])
        forbidden_tokens.add(t['target'])

    # Token frequencies in B
    token_freq = Counter()
    for key in sorted(sequences.keys()):
        for word in sequences[key]:
            token_freq[word] += 1

    results = {}
    for cls in sorted(HAZARD_CLASSES):
        members = class_to_tokens.get(str(cls), [])
        if not members:
            continue

        # Rank by frequency
        ranked = sorted(members, key=lambda t: -token_freq.get(t, 0))
        print(f"Class {cls} ({CLASS_TO_SUBGROUP.get(cls, '?')}):")
        for rank, tok in enumerate(ranked, 1):
            freq = token_freq.get(tok, 0)
            is_forb = tok in forbidden_tokens
            tag = " <-- FORBIDDEN" if is_forb else ""
            print(f"  #{rank:2d}: {tok:>12} freq={freq:5d}{tag}")
        print()

        # Count how many forbidden tokens are in top-N
        n_forb = sum(1 for t in members if t in forbidden_tokens)
        forb_ranks = [i + 1 for i, t in enumerate(ranked) if t in forbidden_tokens]

        results[str(cls)] = {
            'subgroup': CLASS_TO_SUBGROUP.get(cls, '?'),
            'n_members': len(members),
            'n_forbidden': n_forb,
            'forbidden_ranks': forb_ranks,
            'ranking': [
                {'token': t, 'freq': token_freq.get(t, 0),
                 'is_forbidden': t in forbidden_tokens}
                for t in ranked
            ],
        }

    # Summary: are forbidden tokens systematically high-frequency?
    print("-" * 60)
    print("SUMMARY: Frequency rank of forbidden tokens within their class")
    print("-" * 60)
    all_ranks = []
    all_total = []
    for cls in sorted(HAZARD_CLASSES):
        r = results.get(str(cls))
        if r and r['forbidden_ranks']:
            for rank in r['forbidden_ranks']:
                normalized = rank / r['n_members']
                all_ranks.append(normalized)
                all_total.append(r['n_members'])
                print(f"  Class {cls}: rank {rank}/{r['n_members']} = {normalized:.2f}")

    if all_ranks:
        mean_norm_rank = sum(all_ranks) / len(all_ranks)
        print()
        print(f"Mean normalized rank: {mean_norm_rank:.3f} (0=highest freq, 1=lowest)")
        print(f"  If random: expected 0.500")
        print(f"  {'FORBIDDEN = HIGH FREQ' if mean_norm_rank < 0.35 else 'FORBIDDEN = LOW FREQ' if mean_norm_rank > 0.65 else 'NO FREQUENCY BIAS'}")
    print()

    return results


# ============================================================
# SECTION 3: RECIPROCAL PAIR ANALYSIS
# ============================================================
def section3_reciprocal_analysis(sequences, token_to_class, forbidden_inv):
    print("=" * 70)
    print("SECTION 3: RECIPROCAL PAIR ANALYSIS")
    print("=" * 70)
    print()

    transitions = forbidden_inv['transitions']
    forbidden_pairs = set((t['source'], t['target']) for t in transitions)

    # Count all hazard bigrams
    bigram_counts = Counter()
    for key in sorted(sequences.keys()):
        words = sequences[key]
        for i in range(len(words) - 1):
            bigram_counts[(words[i], words[i + 1])] += 1

    print(f"{'ID':>3} {'Forbidden A->B':>20} {'B->A count':>12} {'B->A status':>15} {'CircuitDir':>12}")
    print("-" * 70)

    reciprocal_results = []
    for t in transitions:
        src, tgt = t['source'], t['target']
        reverse_count = bigram_counts.get((tgt, src), 0)
        reverse_forbidden = (tgt, src) in forbidden_pairs
        reverse_status = "FORBIDDEN" if reverse_forbidden else f"ALLOWED({reverse_count})" if reverse_count > 0 else "UNOBSERVED"

        sc = token_to_class.get(src)
        tc = token_to_class.get(tgt)
        if sc is not None and tc is not None:
            sg1 = CLASS_TO_SUBGROUP.get(sc, '?')
            sg2 = CLASS_TO_SUBGROUP.get(tc, '?')
            fwd_dir = classify_direction(sg1, sg2)
            rev_dir = classify_direction(sg2, sg1)
        else:
            fwd_dir = '?'
            rev_dir = '?'

        print(f"{t['id']:3d} {src:>10}->{tgt:<10} {reverse_count:10d}   {reverse_status:>15} {fwd_dir:>12}")

        reciprocal_results.append({
            'id': t['id'],
            'source': src,
            'target': tgt,
            'forward_direction': fwd_dir,
            'reverse_count': reverse_count,
            'reverse_forbidden': reverse_forbidden,
            'reverse_status': reverse_status,
            'reverse_direction': rev_dir,
        })

    print()

    # Summary: asymmetry analysis
    n_both_forbidden = sum(1 for r in reciprocal_results if r['reverse_forbidden'])
    n_reverse_allowed = sum(1 for r in reciprocal_results if r['reverse_count'] > 0 and not r['reverse_forbidden'])
    n_reverse_unobserved = sum(1 for r in reciprocal_results if r['reverse_count'] == 0 and not r['reverse_forbidden'])

    print(f"Reciprocal status summary:")
    print(f"  Both directions forbidden: {n_both_forbidden}")
    print(f"  A->B forbidden, B->A allowed: {n_reverse_allowed}")
    print(f"  A->B forbidden, B->A unobserved: {n_reverse_unobserved}")
    print()

    # For asymmetric pairs (A->B forbidden, B->A allowed), check direction
    print("Asymmetric pairs (A->B forbidden, B->A allowed):")
    for r in reciprocal_results:
        if r['reverse_count'] > 0 and not r['reverse_forbidden']:
            print(f"  {r['source']}->{r['target']}: fwd={r['forward_direction']}, "
                  f"rev={r['reverse_direction']}, rev_count={r['reverse_count']}")
    print()

    return reciprocal_results


# ============================================================
# SECTION 4: PREDICTIVE SUMMARY
# ============================================================
def section4_predictive_summary(classified_pairs, reciprocal_results, token_to_class,
                                 sequences, forbidden_inv):
    print("=" * 70)
    print("SECTION 4: PREDICTIVE SUMMARY")
    print("=" * 70)
    print()

    transitions = forbidden_inv['transitions']
    forbidden_pairs = set((t['source'], t['target']) for t in transitions)

    # Token frequencies
    token_freq = Counter()
    for key in sorted(sequences.keys()):
        for word in sequences[key]:
            token_freq[word] += 1

    morph = Morphology()

    # Load circuit mapping results if available
    mapping_path = PROJECT_ROOT / 'phases' / 'HAZARD_CIRCUIT_TOKEN_RESOLUTION' / 'results' / 'hazard_circuit_token_mapping.json'
    direction_map = {}
    if mapping_path.exists():
        with open(mapping_path, 'r') as f:
            mapping_data = json.load(f)
        for pair in mapping_data.get('section1_classification', {}).get('classified_pairs', []):
            direction_map[pair['id']] = pair.get('direction', '?')

    # Build reciprocal lookup
    recip_lookup = {r['id']: r for r in reciprocal_results}

    print(f"{'ID':>3} {'Pair':>22} {'Direction':>12} {'SrcFreq':>8} {'TgtFreq':>8} "
          f"{'Recip':>10} {'Explanation':>20}")
    print("-" * 90)

    explanations = []
    for t in transitions:
        src, tgt = t['source'], t['target']
        tid = t['id']

        sc = token_to_class.get(src)
        tc = token_to_class.get(tgt)

        direction = direction_map.get(tid, '?')

        src_freq = token_freq.get(src, 0)
        tgt_freq = token_freq.get(tgt, 0)

        recip = recip_lookup.get(tid, {})
        recip_status = recip.get('reverse_status', '?')[:10]

        # Determine explanation
        if direction == 'REVERSE':
            explanation = 'REVERSE_CIRCUIT'
        elif direction == 'SELF_LOOP':
            # Self-loops: check if it's class 31->8 (EN_CHSH internal)
            if sc is not None and tc is not None:
                sg1 = CLASS_TO_SUBGROUP.get(sc, '?')
                sg2 = CLASS_TO_SUBGROUP.get(tc, '?')
                if sg1 == sg2 == 'EN_CHSH':
                    explanation = 'EN_CHSH_INTERNAL'
                elif sg1 == sg2 == 'FL_HAZ':
                    explanation = 'FL_HAZ_INTERNAL'
                else:
                    explanation = 'SELF_LOOP_OTHER'
            else:
                explanation = 'SELF_LOOP_OTHER'
        elif direction == 'CROSS_GROUP':
            explanation = 'CROSS_GROUP'
        elif direction == 'FORWARD':
            explanation = 'FORWARD_SPECIFIC'
        elif direction == 'UNCLASSIFIABLE':
            explanation = 'UNCLASSIFIED_TOKEN'
        else:
            explanation = 'UNKNOWN'

        explanations.append({
            'id': tid,
            'source': src,
            'target': tgt,
            'direction': direction,
            'src_freq': src_freq,
            'tgt_freq': tgt_freq,
            'reciprocal': recip_status,
            'explanation': explanation,
        })

        print(f"{tid:3d} {src:>10}->{tgt:<10} {direction:>12} {src_freq:8d} {tgt_freq:8d} "
              f"{recip_status:>10} {explanation:>20}")

    print()

    # Summary counts
    explanation_counts = Counter(e['explanation'] for e in explanations)
    print("Explanation distribution:")
    for exp, count in explanation_counts.most_common():
        print(f"  {exp:>25}: {count}")
    print()

    # Verdict
    n_reverse = explanation_counts.get('REVERSE_CIRCUIT', 0)
    n_self = sum(v for k, v in explanation_counts.items() if 'INTERNAL' in k or 'SELF_LOOP' in k)
    n_cross = explanation_counts.get('CROSS_GROUP', 0)
    n_forward = explanation_counts.get('FORWARD_SPECIFIC', 0)
    n_unclass = explanation_counts.get('UNCLASSIFIED_TOKEN', 0)

    print("=" * 60)
    print("VERDICT: DOES TWO-LANE ARCHITECTURE PREDICT HAZARD?")
    print("=" * 60)
    print()
    print(f"  REVERSE-CIRCUIT (directionally explained): {n_reverse}/17")
    print(f"  EN_CHSH/FL_HAZ INTERNAL (self-loop):       {n_self}/17")
    print(f"  CROSS-GROUP (FQ_CLOSER involvement):       {n_cross}/17")
    print(f"  FORWARD (circuit-following, need extra):    {n_forward}/17")
    print(f"  UNCLASSIFIED (tokens outside class map):   {n_unclass}/17")
    print()

    circuit_explained = n_reverse + n_self
    print(f"Circuit topology explains: {circuit_explained}/17 ({circuit_explained/17*100:.0f}%)")
    print(f"  - {n_reverse} reverse-flow prohibitions")
    print(f"  - {n_self} within-subgroup restrictions")
    print()
    if n_unclass > 0:
        classifiable = 17 - n_unclass
        print(f"Among classifiable pairs: {circuit_explained}/{classifiable} "
              f"({circuit_explained/classifiable*100:.0f}%)")
    print()

    return {
        'explanations': explanations,
        'summary': dict(explanation_counts),
        'circuit_explained': circuit_explained,
        'total': 17,
        'classifiable': 17 - n_unclass,
    }


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("HAZARD CIRCUIT TOKEN RESOLUTION: FORBIDDEN PAIR SELECTIVITY")
    print("=" * 70)
    print()

    print("Loading data...")
    ctm = load_class_token_map()
    token_to_class = {k: int(v) for k, v in ctm['token_to_class'].items()}
    class_to_tokens = ctm.get('class_to_tokens', {})
    forbidden_inv = load_forbidden_inventory()

    print("Loading Currier B sequences...")
    sequences = build_b_token_sequences()
    total_tokens = sum(len(v) for v in sequences.values())
    print(f"  Lines: {len(sequences)}, Tokens: {total_tokens}")
    print()

    # Section 1
    within_pair_results = section1_within_pair_discrimination(
        sequences, token_to_class, forbidden_inv, class_to_tokens)

    # Section 2
    freq_results = section2_frequency_analysis(
        sequences, token_to_class, class_to_tokens, forbidden_inv)

    # Section 3
    reciprocal_results = section3_reciprocal_analysis(
        sequences, token_to_class, forbidden_inv)

    # Section 4 (needs results from script 1 if available)
    # We pass empty classified_pairs since we read from JSON
    predictive_results = section4_predictive_summary(
        [], reciprocal_results, token_to_class, sequences, forbidden_inv)

    # Save
    output = {
        'metadata': {
            'phase': 'HAZARD_CIRCUIT_TOKEN_RESOLUTION',
            'script': 'forbidden_pair_selectivity',
            'timestamp': datetime.now().isoformat(),
        },
        'section1_within_pair': within_pair_results,
        'section2_frequency': freq_results,
        'section3_reciprocal': reciprocal_results,
        'section4_predictive': predictive_results,
    }

    output_path = PROJECT_ROOT / 'phases' / 'HAZARD_CIRCUIT_TOKEN_RESOLUTION' / 'results' / 'forbidden_pair_selectivity.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
