"""
Phase: SUFFIX_BOUNDARY_TEST
Script: fusion_vs_adjacency.py
Question: Are frequent 2-char pairs (ed, ke, ol, etc.) fused macro-atoms
          or just adjacent atoms in neighboring slots?

Tests:
  1. Separation Test - do paired atoms ever appear with atoms between them?
  2. HEAD Selectivity - do HEADs freely combine with all MODIFIERs?
  3. Substitution Paradigm - can each component substitute independently?
  4. Positional Consistency - does the pair have a fixed positional profile?
  5. Frequency Excess - does the pair occur more than expected from slot probabilities?

Uses C1210 slot assignments:
  HEAD = {a, e, o}  (INITIAL position)
  MODIFIER = {p, c, i, f, d, s}  (MEDIAL position)
  TERMINAL = {l, r, h, y, m, n}  (TERMINAL position)
  FREE = {k, t}  (no positional preference)
"""

import json
import sys
import os
from collections import Counter, defaultdict
from itertools import product as iterproduct
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology

# ── Slot assignments (C1209, C1210) ──
HEAD = {'a', 'e', 'o'}
MODIFIER = {'p', 'c', 'i', 'f', 'd', 's'}
TERMINAL = {'l', 'r', 'h', 'y', 'm', 'n'}
FREE = {'k', 't'}

ALL_ATOMS = HEAD | MODIFIER | TERMINAL | FREE

# Candidate macro-atoms to test
CANDIDATES = ['ed', 'ke', 'ol', 'od', 'ai', 'ey', 'dy', 'in', 'ck', 'ch', 'ee', 'op']

def get_slot(atom):
    """Return slot assignment for a single-char atom."""
    if atom in HEAD:
        return 'HEAD'
    elif atom in MODIFIER:
        return 'MOD'
    elif atom in TERMINAL:
        return 'TERM'
    elif atom in FREE:
        return 'FREE'
    return 'UNK'


def extract_compound_middles():
    """Extract all compound MIDDLEs (len >= 2) from Currier B."""
    tx = Transcript()
    morph = Morphology()

    middles = []
    middle_counts = Counter()

    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and len(m.middle) >= 1:
            middles.append(m.middle)
            middle_counts[m.middle] += 1

    # Separate single-atom and compound
    compounds = [mid for mid in middles if len(mid) >= 2]
    compound_counts = Counter(compounds)

    return middles, middle_counts, compounds, compound_counts


def test1_separation(compounds, compound_counts):
    """
    Test 1: Separation Test
    For each candidate pair X+Y, search all compound MIDDLEs for patterns
    where X and Y both appear but NOT adjacent.
    """
    print("\n" + "="*80)
    print("TEST 1: SEPARATION TEST")
    print("Can atoms in the candidate pair be separated by intervening atoms?")
    print("="*80)

    results = {}

    for pair in CANDIDATES:
        x, y = pair[0], pair[1]
        adjacent_count = 0
        separated_count = 0
        separated_examples = []
        adjacent_examples = []

        for mid, cnt in compound_counts.items():
            if len(mid) < 2:
                continue

            # Find all positions of x and y in this MIDDLE
            x_positions = [i for i, c in enumerate(mid) if c == x]
            y_positions = [i for i, c in enumerate(mid) if c == y]

            if not x_positions or not y_positions:
                continue

            # Check for adjacent x->y
            for xp in x_positions:
                if (xp + 1) in y_positions:
                    adjacent_count += cnt
                    if cnt >= 3 and len(adjacent_examples) < 5:
                        adjacent_examples.append((mid, cnt))
                    break  # Count each MIDDLE once per type

            # Check for separated x...y (x before y but not adjacent)
            for xp in x_positions:
                for yp in y_positions:
                    if yp > xp + 1:  # y is after x but not immediately
                        separated_count += cnt
                        if cnt >= 2 and len(separated_examples) < 10:
                            separated_examples.append((mid, cnt, xp, yp))
                        break
                else:
                    continue
                break

        sep_ratio = separated_count / max(adjacent_count, 1)

        results[pair] = {
            'adjacent_tokens': adjacent_count,
            'separated_tokens': separated_count,
            'separation_ratio': round(sep_ratio, 4),
            'adjacent_examples': [(m, c) for m, c in adjacent_examples[:5]],
            'separated_examples': [(m, c) for m, c, _, _ in separated_examples[:5]],
            'verdict': 'FUSED' if sep_ratio < 0.05 else ('WEAK_FUSION' if sep_ratio < 0.20 else 'SEPARATE_SLOTS')
        }

        print(f"\n  {pair} ({x}+{y}):")
        print(f"    Adjacent occurrences (tokens):  {adjacent_count}")
        print(f"    Separated occurrences (tokens): {separated_count}")
        print(f"    Separation ratio:               {sep_ratio:.4f}")
        if adjacent_examples:
            print(f"    Adjacent examples:  {', '.join(f'{m}({c})' for m,c in adjacent_examples[:5])}")
        if separated_examples:
            print(f"    Separated examples: {', '.join(f'{m}({c})' for m,c,_,_ in separated_examples[:5])}")
        print(f"    Verdict: {results[pair]['verdict']}")

    return results


def test2_head_selectivity(compounds, compound_counts):
    """
    Test 2: HEAD Selectivity
    For each HEAD atom, count what follows it in compound MIDDLEs.
    If ed is fused, e+d should massively dominate.
    """
    print("\n" + "="*80)
    print("TEST 2: HEAD SELECTIVITY")
    print("How freely do HEAD atoms combine with each following atom?")
    print("="*80)

    results = {}

    # For each HEAD atom and FREE atom, count what follows
    test_atoms = sorted(HEAD) + sorted(FREE)

    for atom in test_atoms:
        follower_counts = Counter()
        total = 0

        for mid, cnt in compound_counts.items():
            for i, c in enumerate(mid):
                if c == atom and i + 1 < len(mid):
                    follower = mid[i + 1]
                    if follower in ALL_ATOMS:
                        follower_counts[follower] += cnt
                        total += cnt

        if total == 0:
            continue

        # Compute chi-squared for uniformity
        n_followers = len(follower_counts)
        if n_followers > 1:
            expected = total / n_followers
            chi2 = sum((cnt - expected)**2 / expected for cnt in follower_counts.values())
        else:
            chi2 = 0

        # Top followers by frequency
        top = follower_counts.most_common(10)

        # Concentration: what fraction does the top follower take?
        top_frac = top[0][1] / total if top else 0

        slot = get_slot(atom)
        results[atom] = {
            'slot': slot,
            'total_following': total,
            'unique_followers': n_followers,
            'chi2_uniformity': round(chi2, 1),
            'top_follower': top[0][0] if top else None,
            'top_follower_frac': round(top_frac, 4),
            'distribution': {f: cnt for f, cnt in top}
        }

        print(f"\n  {atom} ({slot})  total={total}, unique followers={n_followers}, chi2={chi2:.1f}")
        print(f"    Top follower: '{top[0][0]}' at {top_frac:.1%}" if top else "    No followers")
        print(f"    Distribution: ", end="")
        for f, cnt in top[:8]:
            pct = cnt / total * 100
            print(f"{f}={cnt}({pct:.1f}%) ", end="")
        print()

    # Cross-HEAD comparison
    print("\n  CROSS-HEAD MODIFIER SELECTION:")
    print(f"  {'':4s}", end="")
    mod_atoms = sorted(MODIFIER) + sorted(TERMINAL) + sorted(FREE)
    for m in mod_atoms[:12]:
        print(f"{m:>6s}", end="")
    print()
    for atom in sorted(HEAD):
        if atom in results:
            dist = results[atom]['distribution']
            total = results[atom]['total_following']
            print(f"  {atom}:  ", end="")
            for m in mod_atoms[:12]:
                cnt = dist.get(m, 0)
                pct = cnt / total * 100 if total > 0 else 0
                print(f"{pct:5.1f}%", end="")
            print()

    return results


def test3_substitution(compound_counts):
    """
    Test 3: Substitution Paradigm
    For each candidate pair, check if components substitute independently.
    High substitution freedom = separate slots. Low = fused unit.
    """
    print("\n" + "="*80)
    print("TEST 3: SUBSTITUTION PARADIGM")
    print("Can each component of the pair be independently replaced?")
    print("="*80)

    # Build a set of all 2-char pairs that appear with freq >= 5
    freq_pairs = {mid: cnt for mid, cnt in compound_counts.items()
                  if len(mid) == 2 and cnt >= 5}
    all_pairs = {mid for mid, cnt in compound_counts.items() if len(mid) == 2}

    results = {}

    for pair in CANDIDATES:
        x, y = pair[0], pair[1]
        pair_freq = compound_counts.get(pair, 0)

        # Position 0 substitutions (replace x with other atoms)
        pos0_subs = []
        for atom in sorted(ALL_ATOMS - {x}):
            alt = atom + y
            alt_freq = compound_counts.get(alt, 0)
            if alt_freq > 0:
                pos0_subs.append((alt, alt_freq))

        # Position 1 substitutions (replace y with other atoms)
        pos1_subs = []
        for atom in sorted(ALL_ATOMS - {y}):
            alt = x + atom
            alt_freq = compound_counts.get(alt, 0)
            if alt_freq > 0:
                pos1_subs.append((alt, alt_freq))

        # Substitution freedom: fraction of possible substitutions that exist (freq >= 1)
        max_pos0 = len(ALL_ATOMS) - 1  # all atoms except x
        max_pos1 = len(ALL_ATOMS) - 1  # all atoms except y

        pos0_freedom = len(pos0_subs) / max_pos0
        pos1_freedom = len(pos1_subs) / max_pos1

        # Also check freq >= 5 threshold
        pos0_subs_f5 = [s for s in pos0_subs if s[1] >= 5]
        pos1_subs_f5 = [s for s in pos1_subs if s[1] >= 5]

        pos0_freedom_f5 = len(pos0_subs_f5) / max_pos0
        pos1_freedom_f5 = len(pos1_subs_f5) / max_pos1

        avg_freedom = (pos0_freedom + pos1_freedom) / 2
        avg_freedom_f5 = (pos0_freedom_f5 + pos1_freedom_f5) / 2

        results[pair] = {
            'pair_freq': pair_freq,
            'pos0_substitutions': [(s, f) for s, f in pos0_subs],
            'pos1_substitutions': [(s, f) for s, f in pos1_subs],
            'pos0_freedom': round(pos0_freedom, 3),
            'pos1_freedom': round(pos1_freedom, 3),
            'pos0_freedom_f5': round(pos0_freedom_f5, 3),
            'pos1_freedom_f5': round(pos1_freedom_f5, 3),
            'avg_freedom': round(avg_freedom, 3),
            'avg_freedom_f5': round(avg_freedom_f5, 3),
            'verdict': 'SEPARATE_SLOTS' if avg_freedom_f5 > 0.20 else ('WEAK_FUSION' if avg_freedom_f5 > 0.10 else 'FUSED')
        }

        print(f"\n  {pair} (freq={pair_freq}):")
        print(f"    Slot[0] ({x}) replacements (any freq): {len(pos0_subs)}/{max_pos0} = {pos0_freedom:.1%}")
        if pos0_subs:
            top5 = sorted(pos0_subs, key=lambda s: -s[1])[:8]
            print(f"      Top: {', '.join(f'{s}({f})' for s,f in top5)}")
        print(f"    Slot[1] ({y}) replacements (any freq): {len(pos1_subs)}/{max_pos1} = {pos1_freedom:.1%}")
        if pos1_subs:
            top5 = sorted(pos1_subs, key=lambda s: -s[1])[:8]
            print(f"      Top: {', '.join(f'{s}({f})' for s,f in top5)}")
        print(f"    Freedom (f>=5): pos0={pos0_freedom_f5:.1%}, pos1={pos1_freedom_f5:.1%}, avg={avg_freedom_f5:.1%}")
        print(f"    Verdict: {results[pair]['verdict']}")

    return results


def test4_positional_consistency(compounds, compound_counts, all_middles, all_middle_counts):
    """
    Test 4: Positional Consistency
    If a pair is fused, it should always appear at the same position in compounds.
    Compare pair's positional profile to independent component profiles.
    """
    print("\n" + "="*80)
    print("TEST 4: POSITIONAL CONSISTENCY")
    print("Does the pair occupy a consistent position in longer compounds?")
    print("="*80)

    # For each compound MIDDLE (len >= 3), classify each atom's relative position
    # as START (first atom), END (last atom), or INTERIOR

    # First compute individual atom positional profiles
    atom_pos_counts = defaultdict(lambda: Counter())  # atom -> {START, INTERIOR, END}

    for mid, cnt in compound_counts.items():
        if len(mid) < 2:
            continue
        for i, c in enumerate(mid):
            if i == 0:
                pos = 'START'
            elif i == len(mid) - 1:
                pos = 'END'
            else:
                pos = 'INTERIOR'
            atom_pos_counts[c][pos] += cnt

    # Now compute pair positional profiles (in compounds len >= 3)
    pair_pos_counts = defaultdict(lambda: Counter())

    for mid, cnt in compound_counts.items():
        if len(mid) < 3:
            continue
        for pair in CANDIDATES:
            x, y = pair[0], pair[1]
            # Find adjacent occurrences of x+y in this MIDDLE
            for i in range(len(mid) - 1):
                if mid[i] == x and mid[i+1] == y:
                    if i == 0:
                        pos = 'START'
                    elif i + 1 == len(mid) - 1:
                        pos = 'END'
                    else:
                        pos = 'INTERIOR'
                    pair_pos_counts[pair][pos] += cnt

    results = {}

    for pair in CANDIDATES:
        x, y = pair[0], pair[1]

        # Pair position profile
        pair_total = sum(pair_pos_counts[pair].values())

        if pair_total == 0:
            print(f"\n  {pair}: No occurrences in compounds of length >= 3")
            results[pair] = {'pair_total_in_compounds': 0, 'verdict': 'INSUFFICIENT_DATA'}
            continue

        pair_profile = {pos: pair_pos_counts[pair].get(pos, 0) / pair_total
                       for pos in ['START', 'INTERIOR', 'END']}

        # Independent component profiles
        x_total = sum(atom_pos_counts[x].values())
        y_total = sum(atom_pos_counts[y].values())

        x_profile = {pos: atom_pos_counts[x].get(pos, 0) / max(x_total, 1)
                     for pos in ['START', 'INTERIOR', 'END']}
        y_profile = {pos: atom_pos_counts[y].get(pos, 0) / max(y_total, 1)
                     for pos in ['START', 'INTERIOR', 'END']}

        # Dominant position for pair
        dominant_pos = max(pair_profile, key=pair_profile.get)
        dominant_frac = pair_profile[dominant_pos]

        # Compute positional entropy of pair
        pair_entropy = 0
        for pos, frac in pair_profile.items():
            if frac > 0:
                pair_entropy -= frac * math.log2(frac)

        # Positional specificity: low entropy = always same position = more fused
        results[pair] = {
            'pair_total_in_compounds': pair_total,
            'pair_profile': {k: round(v, 3) for k, v in pair_profile.items()},
            'x_profile': {k: round(v, 3) for k, v in x_profile.items()},
            'y_profile': {k: round(v, 3) for k, v in y_profile.items()},
            'dominant_position': dominant_pos,
            'dominant_fraction': round(dominant_frac, 3),
            'pair_entropy': round(pair_entropy, 3),
            'x_slot': get_slot(x),
            'y_slot': get_slot(y),
            'verdict': 'FUSED' if dominant_frac > 0.90 else ('POSITIONAL' if dominant_frac > 0.70 else 'FLEXIBLE')
        }

        print(f"\n  {pair} ({get_slot(x)}+{get_slot(y)}) in {pair_total} compound tokens (len>=3):")
        print(f"    Pair profile:  START={pair_profile['START']:.1%}  INT={pair_profile['INTERIOR']:.1%}  END={pair_profile['END']:.1%}")
        print(f"    {x} alone:     START={x_profile['START']:.1%}  INT={x_profile['INTERIOR']:.1%}  END={x_profile['END']:.1%}")
        print(f"    {y} alone:     START={y_profile['START']:.1%}  INT={y_profile['INTERIOR']:.1%}  END={y_profile['END']:.1%}")
        print(f"    Dominant: {dominant_pos} at {dominant_frac:.1%}, entropy={pair_entropy:.3f}")
        print(f"    Verdict: {results[pair]['verdict']}")

    return results


def test5_frequency_excess(compounds, compound_counts, all_middles, all_middle_counts):
    """
    Test 5: Frequency Excess
    If a pair is just adjacent slots, its frequency should be predictable from
    independent slot probabilities. High O/E ratio suggests fusion.
    """
    print("\n" + "="*80)
    print("TEST 5: FREQUENCY EXCESS")
    print("Does the pair occur more than expected from independent slot probabilities?")
    print("="*80)

    # Compute atom-level positional probabilities
    # For position 0 in 2-char MIDDLEs, what's the probability of each atom?
    # For position 1 in 2-char MIDDLEs, what's the probability of each atom?

    # Method: use all compound MIDDLEs to estimate P(atom at position i, i+1)
    bigram_total = 0
    first_atom_counts = Counter()
    second_atom_counts = Counter()
    bigram_counts = Counter()

    for mid, cnt in compound_counts.items():
        for i in range(len(mid) - 1):
            c1, c2 = mid[i], mid[i+1]
            if c1 in ALL_ATOMS and c2 in ALL_ATOMS:
                first_atom_counts[c1] += cnt
                second_atom_counts[c2] += cnt
                bigram_counts[c1 + c2] += cnt
                bigram_total += cnt

    results = {}

    print(f"\n  Bigram context: {bigram_total} total adjacent atom pairs in compounds")
    print(f"  {'Pair':6s} {'Obs':>7s} {'Exp':>9s} {'O/E':>7s} {'log2(O/E)':>10s}  Verdict")
    print(f"  {'----':6s} {'---':>7s} {'---':>9s} {'---':>7s} {'---------':>10s}  -------")

    for pair in CANDIDATES:
        x, y = pair[0], pair[1]

        observed = bigram_counts.get(pair, 0)

        # Expected under independence: P(x at pos i) * P(y at pos i+1) * total
        p_x = first_atom_counts.get(x, 0) / bigram_total
        p_y = second_atom_counts.get(y, 0) / bigram_total
        expected = p_x * p_y * bigram_total

        oe_ratio = observed / max(expected, 0.001)
        log2_oe = math.log2(oe_ratio) if oe_ratio > 0 else float('-inf')

        verdict = 'FUSED' if oe_ratio > 5.0 else ('ENRICHED' if oe_ratio > 2.0 else ('EXPECTED' if oe_ratio > 0.5 else 'DEPLETED'))

        results[pair] = {
            'observed': observed,
            'expected': round(expected, 1),
            'oe_ratio': round(oe_ratio, 3),
            'log2_oe': round(log2_oe, 3),
            'p_x_first': round(p_x, 5),
            'p_y_second': round(p_y, 5),
            'verdict': verdict
        }

        print(f"  {pair:6s} {observed:7d} {expected:9.1f} {oe_ratio:7.3f} {log2_oe:10.3f}  {verdict}")

    # Also compute for all frequent bigrams as context
    print(f"\n  ALL FREQUENT ATOM BIGRAMS (obs >= 50) for context:")
    print(f"  {'Pair':6s} {'Obs':>7s} {'Exp':>9s} {'O/E':>7s} {'Slots':>12s}")
    print(f"  {'----':6s} {'---':>7s} {'---':>9s} {'---':>7s} {'-----':>12s}")

    for bg, obs in sorted(bigram_counts.items(), key=lambda x: -x[1]):
        if obs < 50 or len(bg) != 2:
            continue
        x, y = bg[0], bg[1]
        p_x = first_atom_counts.get(x, 0) / bigram_total
        p_y = second_atom_counts.get(y, 0) / bigram_total
        exp = p_x * p_y * bigram_total
        oe = obs / max(exp, 0.001)
        slots = f"{get_slot(x):>4s}+{get_slot(y):<4s}"
        print(f"  {bg:6s} {obs:7d} {exp:9.1f} {oe:7.3f} {slots:>12s}")

    return results


def synthesize_results(t1, t2, t3, t4, t5):
    """Combine all test results into final verdicts."""
    print("\n" + "="*80)
    print("SYNTHESIS: FUSION vs ADJACENCY VERDICTS")
    print("="*80)

    synthesis = {}

    print(f"\n  {'Pair':6s} {'T1:Sep':>10s} {'T3:SubFree':>10s} {'T4:PosEnt':>10s} {'T5:O/E':>10s} {'VERDICT':>12s}")
    print(f"  {'----':6s} {'------':>10s} {'--------':>10s} {'-------':>10s} {'----':>10s} {'-------':>12s}")

    for pair in CANDIDATES:
        scores = {}

        # T1: Separation ratio (lower = more fused)
        sep_ratio = t1[pair]['separation_ratio']
        scores['t1_separation'] = sep_ratio

        # T3: Substitution freedom (lower = more fused)
        sub_free = t3[pair]['avg_freedom_f5']
        scores['t3_substitution'] = sub_free

        # T4: Positional entropy (lower = more fused)
        if 'pair_entropy' in t4[pair]:
            pos_ent = t4[pair]['pair_entropy']
        else:
            pos_ent = None
        scores['t4_positional'] = pos_ent

        # T5: O/E ratio (higher = more fused)
        oe_ratio = t5[pair]['oe_ratio']
        scores['t5_oe_ratio'] = oe_ratio

        # Composite verdict
        fusion_evidence = 0
        adjacency_evidence = 0

        if sep_ratio < 0.05:
            fusion_evidence += 2
        elif sep_ratio < 0.15:
            fusion_evidence += 1
        else:
            adjacency_evidence += 1

        if sub_free < 0.10:
            fusion_evidence += 2
        elif sub_free < 0.20:
            fusion_evidence += 1
        else:
            adjacency_evidence += 1

        if pos_ent is not None:
            if pos_ent < 0.8:
                fusion_evidence += 1
            else:
                adjacency_evidence += 1

        if oe_ratio > 5.0:
            fusion_evidence += 2
        elif oe_ratio > 2.0:
            fusion_evidence += 1
        elif oe_ratio < 1.5:
            adjacency_evidence += 2
        else:
            adjacency_evidence += 1

        if fusion_evidence >= 5:
            verdict = 'FUSED'
        elif fusion_evidence >= 3:
            verdict = 'LIKELY_FUSED'
        elif adjacency_evidence >= 4:
            verdict = 'ADJACENT_SLOTS'
        elif adjacency_evidence >= 3:
            verdict = 'LIKELY_ADJACENT'
        else:
            verdict = 'AMBIGUOUS'

        scores['fusion_evidence'] = fusion_evidence
        scores['adjacency_evidence'] = adjacency_evidence
        scores['verdict'] = verdict

        synthesis[pair] = scores

        pos_ent_str = f"{pos_ent:.3f}" if pos_ent is not None else "N/A"
        print(f"  {pair:6s} {sep_ratio:10.4f} {sub_free:10.3f} {pos_ent_str:>10s} {oe_ratio:10.3f} {verdict:>12s}")

    # Categorize
    fused = [p for p, s in synthesis.items() if 'FUSED' in s['verdict']]
    adjacent = [p for p, s in synthesis.items() if 'ADJACENT' in s['verdict']]
    ambiguous = [p for p, s in synthesis.items() if s['verdict'] == 'AMBIGUOUS']

    print(f"\n  FUSED/LIKELY_FUSED:     {', '.join(fused) if fused else 'none'}")
    print(f"  ADJACENT/LIKELY_ADJ:    {', '.join(adjacent) if adjacent else 'none'}")
    print(f"  AMBIGUOUS:              {', '.join(ambiguous) if ambiguous else 'none'}")

    return synthesis


def main():
    print("FUSION vs ADJACENCY TEST BATTERY")
    print("Candidate macro-atoms:", ', '.join(CANDIDATES))
    print()

    # Extract data
    print("Loading Currier B compound MIDDLEs...")
    all_middles, all_middle_counts, compounds, compound_counts = extract_compound_middles()
    print(f"  Total MIDDLE tokens: {len(all_middles)}")
    print(f"  Unique MIDDLEs: {len(all_middle_counts)}")
    print(f"  Compound MIDDLE tokens (len>=2): {len(compounds)}")
    print(f"  Unique compound MIDDLEs: {len(compound_counts)}")

    # Run tests
    t1 = test1_separation(compounds, compound_counts)
    t2 = test2_head_selectivity(compounds, compound_counts)
    t3 = test3_substitution(compound_counts)
    t4 = test4_positional_consistency(compounds, compound_counts, all_middles, all_middle_counts)
    t5 = test5_frequency_excess(compounds, compound_counts, all_middles, all_middle_counts)

    # Synthesize
    synthesis = synthesize_results(t1, t2, t3, t4, t5)

    # Save results
    output = {
        'metadata': {
            'candidates': CANDIDATES,
            'total_middle_tokens': len(all_middles),
            'unique_middles': len(all_middle_counts),
            'compound_tokens': len(compounds),
            'unique_compounds': len(compound_counts),
            'slot_assignments': {
                'HEAD': sorted(HEAD),
                'MODIFIER': sorted(MODIFIER),
                'TERMINAL': sorted(TERMINAL),
                'FREE': sorted(FREE)
            }
        },
        'test1_separation': t1,
        'test2_head_selectivity': {k: {kk: vv for kk, vv in v.items()} for k, v in t2.items()},
        'test3_substitution': t3,
        'test4_positional_consistency': t4,
        'test5_frequency_excess': t5,
        'synthesis': synthesis
    }

    out_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'fusion_vs_adjacency.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n  Results saved to: {os.path.abspath(out_path)}")


if __name__ == '__main__':
    main()
