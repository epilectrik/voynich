"""
P-C13: c as Category Shifter
=============================
Test whether c systematically shifts the category of the second atom away
from that atom's default category.

Method:
1. For each second atom X in c+X compounds, determine X's "default" category
   (when X is standalone or X-initial in non-c compounds)
2. For each c+X, determine the actual category
3. Measure how often c+X DIFFERS from X's default (shift rate)
4. Compare to other first atoms (e, a, o, k, etc.)

Pass: shift rate >= 80% AND c is top 3 among all first atoms
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Collect all compound MIDDLEs and their categories
    # compound_data[middle] = Counter of categories
    compound_data = defaultdict(Counter)
    # standalone_data[atom] = Counter of categories (for standalone single-char MIDDLEs)
    standalone_data = defaultdict(Counter)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        if not mid:
            continue
        cat = cc.classify(mid)
        if cat not in CATEGORIES:
            continue

        compound_data[mid][cat] += 1

        # Track standalone single-char MIDDLEs
        if len(mid) == 1:
            standalone_data[mid][cat] += 1

    # Build atom default categories
    # For each atom X, its "default" is the primary category when X appears as:
    #   (a) standalone MIDDLE, or
    #   (b) first atom in non-c compounds (X+something)
    # We use all X-initial compounds where X != c to establish defaults

    # First: gather X-initial compound data (where X is first char, compound len >= 2)
    x_initial_data = defaultdict(Counter)  # x_initial_data[first_char] = Counter
    for mid, cat_counts in compound_data.items():
        if len(mid) >= 2:
            first = mid[0]
            for cat, cnt in cat_counts.items():
                x_initial_data[first][cat] += cnt

    # Default category for atom X: combine standalone + X-initial
    atom_defaults = {}
    all_atoms = set()
    for mid in compound_data:
        for ch in mid:
            all_atoms.add(ch)

    for atom in sorted(all_atoms):
        combined = Counter()
        if atom in standalone_data:
            combined += standalone_data[atom]
        if atom in x_initial_data:
            combined += x_initial_data[atom]
        if combined:
            atom_defaults[atom] = combined.most_common(1)[0][0]

    print("=" * 70)
    print("P-C13: c as Category Shifter")
    print("=" * 70)

    # --- Part 1: Atom default categories ---
    print("\n--- Atom Default Categories ---")
    print(f"{'Atom':<6} {'Default Cat':<15} {'Total Tokens':<12} {'Top 3'}")
    print("-" * 65)
    for atom in sorted(atom_defaults.keys()):
        combined = Counter()
        if atom in standalone_data:
            combined += standalone_data[atom]
        if atom in x_initial_data:
            combined += x_initial_data[atom]
        total = sum(combined.values())
        top3 = ', '.join(f"{c}:{n}" for c, n in combined.most_common(3))
        print(f"{atom:<6} {atom_defaults[atom]:<15} {total:<12} {top3}")

    # --- Part 2: c+X compounds vs X defaults ---
    print("\n--- c+X Compounds vs X Default ---")
    print(f"{'Compound':<10} {'Tokens':<8} {'Primary Cat':<15} {'X':<4} {'X Default':<15} {'Shifted?'}")
    print("-" * 70)

    c_compounds = {}
    for mid, cat_counts in compound_data.items():
        if len(mid) >= 2 and mid[0] == 'c':
            total = sum(cat_counts.values())
            if total >= 5:  # minimum token threshold
                primary = cat_counts.most_common(1)[0][0]
                c_compounds[mid] = {
                    'total': total,
                    'primary': primary,
                    'counts': cat_counts
                }

    c_shift_count = 0
    c_total_count = 0
    c_shift_tokens = 0
    c_total_tokens = 0

    for mid in sorted(c_compounds.keys()):
        info = c_compounds[mid]
        second_atom = mid[1]
        x_default = atom_defaults.get(second_atom, 'UNKNOWN')
        shifted = info['primary'] != x_default
        marker = "YES" if shifted else "no"

        print(f"{mid:<10} {info['total']:<8} {info['primary']:<15} {second_atom:<4} {x_default:<15} {marker}")

        c_total_count += 1
        c_total_tokens += info['total']
        if shifted:
            c_shift_count += 1
            c_shift_tokens += info['total']

    c_shift_rate = c_shift_count / c_total_count if c_total_count > 0 else 0
    c_shift_rate_weighted = c_shift_tokens / c_total_tokens if c_total_tokens > 0 else 0

    print(f"\nc shift rate (unweighted): {c_shift_count}/{c_total_count} = {c_shift_rate:.1%}")
    print(f"c shift rate (token-weighted): {c_shift_tokens}/{c_total_tokens} = {c_shift_rate_weighted:.1%}")

    # --- Part 3: Compare all first atoms ---
    print("\n--- Shift Rate by First Atom (all first+X compounds, N>=5) ---")

    first_atom_shifts = {}
    for first_atom in sorted(all_atoms):
        shift_count = 0
        total_count = 0
        shift_tokens = 0
        total_tokens = 0

        for mid, cat_counts in compound_data.items():
            if len(mid) >= 2 and mid[0] == first_atom:
                total = sum(cat_counts.values())
                if total < 5:
                    continue
                primary = cat_counts.most_common(1)[0][0]
                second_atom = mid[1]
                x_default = atom_defaults.get(second_atom, None)
                if x_default is None:
                    continue

                total_count += 1
                total_tokens += total
                if primary != x_default:
                    shift_count += 1
                    shift_tokens += total

        if total_count >= 2:  # need at least 2 compounds to compare
            rate = shift_count / total_count
            rate_w = shift_tokens / total_tokens if total_tokens > 0 else 0
            first_atom_shifts[first_atom] = {
                'shift': shift_count,
                'total': total_count,
                'rate': rate,
                'rate_w': rate_w,
                'tokens': total_tokens
            }

    print(f"{'Atom':<6} {'Shifted':<10} {'Total':<8} {'Rate':<10} {'Wtd Rate':<10} {'Tokens'}")
    print("-" * 60)

    # Sort by rate descending
    ranked = sorted(first_atom_shifts.items(), key=lambda x: x[1]['rate'], reverse=True)
    c_rank = None
    for i, (atom, info) in enumerate(ranked):
        marker = " <<<" if atom == 'c' else ""
        if atom == 'c':
            c_rank = i + 1
        print(f"{atom:<6} {info['shift']:<10} {info['total']:<8} {info['rate']:<10.1%} {info['rate_w']:<10.1%} {info['tokens']}{marker}")

    # --- Part 4: Detailed comparison of c vs e, a, o ---
    print("\n--- Direct Comparison: c vs e, a, o ---")
    for comp_atom in ['e', 'a', 'o']:
        if comp_atom in first_atom_shifts:
            ci = first_atom_shifts.get('c', {'rate': 0})
            oi = first_atom_shifts[comp_atom]
            diff = ci['rate'] - oi['rate']
            print(f"  c ({ci['rate']:.1%}) vs {comp_atom} ({oi['rate']:.1%}): delta = {diff:+.1%}")

    # --- Verdicts ---
    print("\n" + "=" * 70)
    print("VERDICTS")
    print("=" * 70)

    v1 = c_shift_rate >= 0.80
    print(f"\n[{'PASS' if v1 else 'FAIL'}] c+X shift rate >= 80%: {c_shift_rate:.1%}")

    v2 = c_rank is not None and c_rank <= 3
    print(f"[{'PASS' if v2 else 'FAIL'}] c is top 3 among first atoms: rank {c_rank}")

    # Check c > e and c > a
    c_rate = first_atom_shifts.get('c', {}).get('rate', 0)
    e_rate = first_atom_shifts.get('e', {}).get('rate', 0)
    a_rate = first_atom_shifts.get('a', {}).get('rate', 0)
    v3 = c_rate > e_rate and c_rate > a_rate
    print(f"[{'PASS' if v3 else 'FAIL'}] c shift rate > e AND > a: c={c_rate:.1%}, e={e_rate:.1%}, a={a_rate:.1%}")

    overall = v1 and v2
    print(f"\n{'='*70}")
    print(f"OVERALL: {'PASS' if overall else 'FAIL'} (shift >= 80% AND top 3)")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
