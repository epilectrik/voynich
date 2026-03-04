#!/usr/bin/env python3
"""
Pair-Locked Atom Analysis
=========================
Investigates which atoms never/rarely appear as standalone single-atom MIDDLEs,
existing only inside compound MIDDLEs. Tests whether their common pairs function
as single-slot macro-atoms in the three-slot grammar.

Context:
  C1209: MIDDLE slot syntax (HEAD/MODIFIER/TERMINAL/FREE)
  C1379: Macro-atom parallel composition
  C1387: r-terminal only appears as ar/or
  C1210: MIDDLE slot grammar rules
  C1065: Atom bigram ordering grammar

Output: phases/SUFFIX_BOUNDARY_TEST/results/pair_locked_atoms.json
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# CONFIGURATION
# ============================================================
# The 18 canonical atoms (C085 + extensions)
ATOMS = list('aeopcifdsklrthymng')

# Slot classifications from C1209
HEAD_ATOMS = set('aeqo')       # 86-57% initial
MODIFIER_ATOMS = set('cipdsf')  # medial
TERMINAL_ATOMS = set('nymrhl')  # 71-99% terminal
FREE_ATOMS = set('kt')          # no preference

# Known macro-atoms from C1379 and prior work
KNOWN_MACRO_ATOMS = [
    'ke', 'kee', 'keee',   # k+e extensible family
    'ek', 'eek',            # reverse k+e
    'ck',                    # c+k compound
    'ch',                    # c+h compound (also PREFIX but appears in MIDDLE)
    'dy',                    # d+y closure
    'in', 'iin', 'iiin',    # i+n extensible family
    'ain', 'aiin',          # a+i+n family
]

OUTPUT_DIR = PROJECT_ROOT / 'phases' / 'SUFFIX_BOUNDARY_TEST' / 'results'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_atom_decomposition(middle: str) -> list:
    """
    Decompose a MIDDLE into its constituent atoms.
    Returns list of single characters that are valid atoms.
    Handles extensible atoms (ee, ii) by treating each char separately.
    """
    return [c for c in middle if c in ATOMS]


def classify_slot(atom_char: str) -> str:
    """Classify which slot an atom occupies in the grammar."""
    if atom_char in HEAD_ATOMS:
        return 'HEAD'
    elif atom_char in MODIFIER_ATOMS:
        return 'MODIFIER'
    elif atom_char in TERMINAL_ATOMS:
        return 'TERMINAL'
    elif atom_char in FREE_ATOMS:
        return 'FREE'
    return 'UNKNOWN'


def find_pair_position_in_compound(pair: str, compound: str) -> str:
    """
    Determine where a pair sits in a larger compound.
    Returns FIRST, LAST, MIDDLE, or WHOLE.
    """
    if compound == pair:
        return 'WHOLE'
    idx = compound.find(pair)
    if idx == -1:
        return 'NOT_FOUND'
    if idx == 0:
        return 'FIRST'
    elif idx + len(pair) == len(compound):
        return 'LAST'
    else:
        return 'MIDDLE'


def main():
    tx = Transcript()
    morph = Morphology()

    # ============================================================
    # STEP 1: Inventory audit - collect all MIDDLEs from Currier B
    # ============================================================
    print("=" * 70)
    print("PAIR-LOCKED ATOM ANALYSIS")
    print("=" * 70)

    middle_counter = Counter()
    token_count = 0

    for token in tx.currier_b():
        m = morph.extract(token.word)
        if m.middle and m.middle != '_EMPTY_':
            middle_counter[m.middle] += 1
            token_count += 1

    print(f"\nTotal B tokens with valid MIDDLE: {token_count}")
    print(f"Unique MIDDLEs: {len(middle_counter)}")

    # ============================================================
    # STEP 2: For each atom, count standalone vs compound appearances
    # ============================================================
    print("\n" + "=" * 70)
    print("ATOM STANDALONE vs COMPOUND INVENTORY")
    print("=" * 70)

    atom_stats = {}

    for atom in sorted(ATOMS):
        standalone_count = middle_counter.get(atom, 0)
        compound_forms = {}  # middle -> count

        for mid, cnt in middle_counter.items():
            if len(mid) > 1 and atom in mid:
                compound_forms[mid] = cnt

        compound_total = sum(compound_forms.values())
        total = standalone_count + compound_total
        standalone_ratio = standalone_count / total if total > 0 else 0

        atom_stats[atom] = {
            'standalone_count': standalone_count,
            'compound_count': compound_total,
            'total_occurrences': total,
            'standalone_ratio': round(standalone_ratio, 4),
            'unique_compound_forms': len(compound_forms),
            'top_compound_forms': sorted(compound_forms.items(),
                                          key=lambda x: -x[1])[:20],
            'slot_class': classify_slot(atom),
            'pair_locked': standalone_ratio < 0.10,
        }

    # Print results sorted by standalone ratio
    print(f"\n{'Atom':<6} {'Slot':<10} {'Standalone':<12} {'Compound':<12} "
          f"{'Total':<10} {'Ratio':<10} {'Locked?':<8}")
    print("-" * 70)

    for atom in sorted(ATOMS, key=lambda a: atom_stats[a]['standalone_ratio']):
        s = atom_stats[atom]
        locked = "YES" if s['pair_locked'] else ""
        print(f"{atom:<6} {s['slot_class']:<10} {s['standalone_count']:<12} "
              f"{s['compound_count']:<12} {s['total_occurrences']:<10} "
              f"{s['standalone_ratio']:<10.4f} {locked:<8}")

    # ============================================================
    # STEP 3: Pair-locked atoms - analyze their common pairs
    # ============================================================
    print("\n" + "=" * 70)
    print("PAIR-LOCKED ATOM DETAIL")
    print("=" * 70)

    pair_locked_atoms = [a for a in ATOMS if atom_stats[a]['pair_locked']]
    print(f"\nPair-locked atoms (standalone ratio < 10%): {pair_locked_atoms}")

    pair_analysis = {}

    for atom in pair_locked_atoms:
        s = atom_stats[atom]
        print(f"\n--- Atom '{atom}' (standalone: {s['standalone_count']}, "
              f"compound: {s['compound_count']}, ratio: {s['standalone_ratio']}) ---")
        print(f"  Slot class: {s['slot_class']}")

        # Find most common pairs (2-char MIDDLEs containing this atom)
        pairs = {}
        for mid, cnt in middle_counter.items():
            if len(mid) == 2 and atom in mid:
                pairs[mid] = cnt

        print(f"  Two-char pairs: {sorted(pairs.items(), key=lambda x: -x[1])}")

        # For each common pair, check position in longer compounds
        pair_slot_data = {}
        for pair, pair_cnt in sorted(pairs.items(), key=lambda x: -x[1]):
            positions = Counter()
            compounds_with_pair = []

            for mid, cnt in middle_counter.items():
                if len(mid) > 2 and pair in mid:
                    pos = find_pair_position_in_compound(pair, mid)
                    positions[pos] += cnt
                    compounds_with_pair.append((mid, cnt, pos))

            # What slot would this pair occupy?
            # Get the two atoms in the pair
            atoms_in_pair = [c for c in pair]
            slots_in_pair = [classify_slot(c) for c in atoms_in_pair]

            pair_slot_data[pair] = {
                'count_as_standalone_middle': pair_cnt,
                'atoms': atoms_in_pair,
                'atom_slots': slots_in_pair,
                'position_in_longer_compounds': dict(positions),
                'examples': [(m, c, p) for m, c, p in
                             sorted(compounds_with_pair, key=lambda x: -x[1])[:10]],
            }

            print(f"\n  Pair '{pair}' (count={pair_cnt}):")
            print(f"    Atoms: {atoms_in_pair} -> Slots: {slots_in_pair}")
            print(f"    Position in longer compounds: {dict(positions)}")
            if compounds_with_pair:
                print(f"    Top examples in longer MIDDLEs:")
                for m, c, p in sorted(compounds_with_pair, key=lambda x: -x[1])[:8]:
                    atoms_decomp = get_atom_decomposition(m)
                    print(f"      {m} (n={c}) -> position={p}, "
                          f"atoms={atoms_decomp}")

        pair_analysis[atom] = pair_slot_data

    # ============================================================
    # STEP 4: Test macro-atom slot occupancy
    # ============================================================
    print("\n" + "=" * 70)
    print("MACRO-ATOM SLOT OCCUPANCY TEST")
    print("=" * 70)

    # For each candidate macro-atom, determine if it consistently occupies
    # a single slot position across all compounds it appears in
    all_candidate_pairs = set()

    # Add pair-locked atom pairs
    for atom in pair_locked_atoms:
        for pair, _ in sorted(
                [(m, c) for m, c in middle_counter.items()
                 if len(m) == 2 and atom in m],
                key=lambda x: -x[1]):
            all_candidate_pairs.add(pair)

    # Add known macro-atoms
    for ma in KNOWN_MACRO_ATOMS:
        if len(ma) <= 3:  # Only test short ones
            all_candidate_pairs.add(ma)

    # Also check ALL high-frequency 2-char MIDDLEs
    for mid, cnt in middle_counter.items():
        if len(mid) == 2 and cnt >= 10:
            all_candidate_pairs.add(mid)

    print(f"\nTesting {len(all_candidate_pairs)} candidate macro-atoms...")

    macro_atom_roster = {}

    for pair in sorted(all_candidate_pairs):
        pair_as_middle = middle_counter.get(pair, 0)

        # Find all longer MIDDLEs containing this pair
        positions = Counter()
        total_in_compounds = 0
        compound_examples = []

        for mid, cnt in middle_counter.items():
            if len(mid) > len(pair) and pair in mid:
                pos = find_pair_position_in_compound(pair, mid)
                positions[pos] += cnt
                total_in_compounds += cnt
                compound_examples.append((mid, cnt, pos))

        if total_in_compounds == 0 and pair_as_middle == 0:
            continue

        # Determine dominant position
        if positions:
            dominant_pos = positions.most_common(1)[0][0]
            dominant_frac = positions.most_common(1)[0][1] / total_in_compounds
        else:
            dominant_pos = 'STANDALONE_ONLY'
            dominant_frac = 1.0

        # Check if atoms span slots
        atoms_in = [c for c in pair if c in ATOMS]
        slots_in = [classify_slot(c) for c in atoms_in]
        spans_slots = len(set(slots_in)) > 1

        # Verdict: is this a macro-atom?
        # Criteria: consistently in one position, or spans adjacent slots
        is_macro = (
            pair_as_middle > 0 and  # exists as standalone
            (total_in_compounds == 0 or  # never in compounds (trivially macro)
             dominant_frac >= 0.70)  # or strongly consistent position
        )

        macro_atom_roster[pair] = {
            'as_standalone_middle': pair_as_middle,
            'in_compounds_total': total_in_compounds,
            'position_distribution': dict(positions),
            'dominant_position': dominant_pos,
            'dominant_fraction': round(dominant_frac, 3),
            'atoms': atoms_in,
            'slots': slots_in,
            'spans_slots': spans_slots,
            'is_macro_atom': is_macro,
        }

    # Print macro-atom roster
    print(f"\n{'Pair':<8} {'Solo':<8} {'InCmpd':<8} {'DomPos':<10} "
          f"{'DomFrac':<10} {'Slots':<20} {'Macro?':<8}")
    print("-" * 75)

    for pair in sorted(macro_atom_roster.keys(),
                       key=lambda p: -macro_atom_roster[p]['as_standalone_middle']):
        r = macro_atom_roster[pair]
        slots_str = '+'.join(r['slots'])
        macro_str = "YES" if r['is_macro_atom'] else ""
        print(f"{pair:<8} {r['as_standalone_middle']:<8} {r['in_compounds_total']:<8} "
              f"{r['dominant_position']:<10} {r['dominant_fraction']:<10.3f} "
              f"{slots_str:<20} {macro_str:<8}")

    # ============================================================
    # STEP 5: Comprehensive macro-atom roster
    # ============================================================
    print("\n" + "=" * 70)
    print("COMPREHENSIVE MACRO-ATOM ROSTER")
    print("=" * 70)

    confirmed_macros = {k: v for k, v in macro_atom_roster.items()
                        if v['is_macro_atom']}

    # Also add known macro-atoms that are in the data
    for ma in KNOWN_MACRO_ATOMS:
        if ma not in confirmed_macros and middle_counter.get(ma, 0) > 0:
            confirmed_macros[ma] = {
                'as_standalone_middle': middle_counter.get(ma, 0),
                'in_compounds_total': sum(cnt for mid, cnt in middle_counter.items()
                                          if len(mid) > len(ma) and ma in mid),
                'atoms': [c for c in ma],
                'slots': [classify_slot(c) for c in ma],
                'known_macro': True,
            }

    print(f"\nTotal confirmed/known macro-atoms: {len(confirmed_macros)}")
    for pair in sorted(confirmed_macros.keys()):
        r = confirmed_macros[pair]
        slots = '+'.join(r['slots'])
        src = " (KNOWN)" if r.get('known_macro') else ""
        print(f"  {pair:<10} solo={r['as_standalone_middle']:<6} "
              f"in_cmpd={r['in_compounds_total']:<6} slots={slots}{src}")

    # ============================================================
    # STEP 6: Special analysis for 'r' atom (the motivating case)
    # ============================================================
    print("\n" + "=" * 70)
    print("SPECIAL ANALYSIS: r-ATOM PAIR LOCKING")
    print("=" * 70)

    r_middles = [(mid, cnt) for mid, cnt in middle_counter.items()
                 if 'r' in mid]
    r_middles.sort(key=lambda x: -x[1])

    print(f"\nAll MIDDLEs containing 'r' ({len(r_middles)} forms, "
          f"{sum(c for _, c in r_middles)} tokens):")

    r_standalone = middle_counter.get('r', 0)
    print(f"\n  Standalone 'r': {r_standalone} tokens")

    # Group by r-pair
    r_pairs = defaultdict(list)
    for mid, cnt in r_middles:
        if len(mid) == 1:
            continue
        # Find the 2-char pair containing r
        for i, c in enumerate(mid):
            if c == 'r':
                if i > 0:
                    pair = mid[i-1] + 'r'
                    r_pairs[pair].append((mid, cnt))
                if i < len(mid) - 1:
                    pair = 'r' + mid[i+1]
                    r_pairs[pair].append((mid, cnt))

    print(f"\n  r-containing pairs and their compounds:")
    for pair in sorted(r_pairs.keys(), key=lambda p: -sum(c for _, c in r_pairs[p])):
        total = sum(c for _, c in r_pairs[p])
        print(f"\n    '{pair}' (total tokens in compounds: {total}):")
        for mid, cnt in sorted(r_pairs[pair], key=lambda x: -x[1])[:10]:
            atoms = get_atom_decomposition(mid)
            print(f"      {mid:<15} n={cnt:<6} atoms={atoms}")

    # ============================================================
    # STEP 7: Exhaustive standalone analysis - which atoms NEVER standalone?
    # ============================================================
    print("\n" + "=" * 70)
    print("ATOMS THAT NEVER APPEAR AS STANDALONE MIDDLE")
    print("=" * 70)

    never_standalone = []
    for atom in sorted(ATOMS):
        if middle_counter.get(atom, 0) == 0:
            never_standalone.append(atom)
            # What compound forms exist?
            forms = [(mid, cnt) for mid, cnt in middle_counter.items()
                     if atom in mid]
            forms.sort(key=lambda x: -x[1])
            total = sum(c for _, c in forms)
            print(f"\n  '{atom}': NEVER standalone, {len(forms)} compound forms, "
                  f"{total} total tokens")
            print(f"    Top forms: {[(m, c) for m, c in forms[:8]]}")

    if not never_standalone:
        print("\n  All atoms appear as standalone MIDDLEs at least once.")

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    results = {
        'metadata': {
            'total_b_tokens': token_count,
            'unique_middles': len(middle_counter),
            'atoms_tested': len(ATOMS),
        },
        'atom_inventory': {
            atom: {
                'standalone_count': atom_stats[atom]['standalone_count'],
                'compound_count': atom_stats[atom]['compound_count'],
                'total_occurrences': atom_stats[atom]['total_occurrences'],
                'standalone_ratio': atom_stats[atom]['standalone_ratio'],
                'unique_compound_forms': atom_stats[atom]['unique_compound_forms'],
                'slot_class': atom_stats[atom]['slot_class'],
                'pair_locked': atom_stats[atom]['pair_locked'],
                'top_compound_forms': [
                    {'middle': m, 'count': c}
                    for m, c in atom_stats[atom]['top_compound_forms']
                ],
            }
            for atom in sorted(ATOMS)
        },
        'pair_locked_atoms': pair_locked_atoms,
        'never_standalone_atoms': never_standalone,
        'pair_analysis': {
            atom: {
                pair: {
                    'count': data['count_as_standalone_middle'],
                    'atoms': data['atoms'],
                    'atom_slots': data['atom_slots'],
                    'position_in_compounds': data['position_in_longer_compounds'],
                    'examples': [
                        {'middle': m, 'count': c, 'position': p}
                        for m, c, p in data['examples']
                    ],
                }
                for pair, data in pairs.items()
            }
            for atom, pairs in pair_analysis.items()
        },
        'macro_atom_roster': {
            pair: {
                'as_standalone': data['as_standalone_middle'],
                'in_compounds': data['in_compounds_total'],
                'dominant_position': data.get('dominant_position', 'N/A'),
                'dominant_fraction': data.get('dominant_fraction', 0),
                'atoms': data['atoms'],
                'slots': data['slots'],
                'spans_slots': data.get('spans_slots', False),
                'is_confirmed': data.get('is_macro_atom', False) or data.get('known_macro', False),
            }
            for pair, data in sorted(confirmed_macros.items())
        },
    }

    output_path = OUTPUT_DIR / 'pair_locked_atoms.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_path}")

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\n  Pair-locked atoms (standalone < 10%): "
          f"{len(pair_locked_atoms)} -> {pair_locked_atoms}")
    print(f"  Never-standalone atoms: "
          f"{len(never_standalone)} -> {never_standalone}")
    print(f"  Confirmed macro-atoms: {len(confirmed_macros)}")
    print(f"    -> {sorted(confirmed_macros.keys())}")

    # Cross-reference with slot grammar
    print(f"\n  Slot coverage of pair-locked atoms:")
    for atom in pair_locked_atoms:
        s = atom_stats[atom]
        print(f"    '{atom}' ({s['slot_class']}): always paired, "
              f"top compound forms:")
        for mid, cnt in s['top_compound_forms'][:5]:
            print(f"      {mid} (n={cnt})")


if __name__ == '__main__':
    main()
