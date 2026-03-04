#!/usr/bin/env python3
"""
SM-2: Base-dependent category shift test

Question: Does s systematically shift its partner's default category?

For each atom X, compute the category profile of all X-initial MIDDLEs
(standalone X or X-prefixed compounds). Then compute the category profile
of the Xs compound (s appended to X). Compare: does the primary category
change?

Testable pairs (Xs N >= 5):
  es(14) vs e-initial, os(16) vs o-initial, cs(12) vs c-initial,
  ks(7) vs k-initial, ls(7) vs l-initial

For context, also show Xsh compounds to demonstrate the h-junction separately.

Pass: >= 3/5 Xs compounds show different primary category than X alone.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']

# Atoms to test
TEST_ATOMS = ['e', 'o', 'c', 'k', 'l']
MIN_N = 5


def get_primary(cat_counts, total):
    """Return (primary_category, percentage) or (None, 0)."""
    if total == 0:
        return None, 0.0
    best = max(cat_counts.items(), key=lambda x: x[1]) if cat_counts else (None, 0)
    return best[0], best[1] / total * 100


def print_profile(cat_counts, total, indent="    "):
    """Print a full 8-category profile."""
    for cat in CATEGORIES:
        n = cat_counts.get(cat, 0)
        pct = n / total * 100 if total > 0 else 0.0
        if n > 0:
            print(f"{indent}{cat:<15} {n:>5} ({pct:>5.1f}%)")


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Collect category counts per MIDDLE
    middle_cats = defaultdict(lambda: defaultdict(int))
    middle_totals = defaultdict(int)

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle:
            continue

        cat = cc.classify(m.middle)
        if cat is None:
            continue

        middle_cats[m.middle][cat] += 1
        middle_totals[m.middle] += 1

    # Build X-initial profiles (all MIDDLEs starting with atom X)
    # X-initial means: MIDDLE starts with the character X
    x_initial_cats = defaultdict(lambda: defaultdict(int))
    x_initial_totals = defaultdict(int)

    for mid, total in middle_totals.items():
        if not mid:
            continue
        first_char = mid[0]
        for cat, n in middle_cats[mid].items():
            x_initial_cats[first_char][cat] += n
            x_initial_totals[first_char] += n

    print("=" * 75)
    print("SM-2: Base-dependent category shift -- Does s shift X's default?")
    print("=" * 75)
    print()

    # ---- Main test: Xs vs X-initial ----
    print("-" * 75)
    print("TEST: Category shift from X-initial to Xs compound")
    print("-" * 75)
    print()

    tested = 0
    shifted = 0
    results = []

    for atom in TEST_ATOMS:
        xs_compound = atom + 's'
        xs_total = middle_totals.get(xs_compound, 0)
        xi_total = x_initial_totals.get(atom, 0)

        if xs_total < MIN_N:
            print(f"  {xs_compound}: N={xs_total} < {MIN_N} -- SKIPPED")
            print()
            continue

        tested += 1

        # X-initial profile
        xi_primary, xi_pct = get_primary(x_initial_cats[atom], xi_total)

        # Xs compound profile
        xs_primary, xs_pct = get_primary(middle_cats[xs_compound], xs_total)

        is_shift = xi_primary != xs_primary
        if is_shift:
            shifted += 1

        results.append((atom, xs_compound, xi_total, xs_total, xi_primary, xi_pct,
                         xs_primary, xs_pct, is_shift))

        verdict = "SHIFT" if is_shift else "NO SHIFT"
        print(f"  {atom}-initial (N={xi_total}) vs {xs_compound} (N={xs_total}):  --> {verdict}")
        print(f"    {atom}-initial primary: {xi_primary} ({xi_pct:.1f}%)")
        print(f"    {xs_compound} primary:     {xs_primary} ({xs_pct:.1f}%)")
        print()
        print(f"    {atom}-initial full profile:")
        print_profile(x_initial_cats[atom], xi_total, indent="      ")
        print()
        print(f"    {xs_compound} full profile:")
        print_profile(middle_cats[xs_compound], xs_total, indent="      ")

        # Compute delta for dominant category
        if xi_primary and xi_primary in middle_cats[xs_compound]:
            orig_in_xs = middle_cats[xs_compound][xi_primary] / xs_total * 100
        else:
            orig_in_xs = 0.0
        delta = orig_in_xs - xi_pct
        print()
        print(f"    Delta (original dominant '{xi_primary}' in Xs): {delta:+.1f}pp")
        print()

    # ---- Context: Xsh compounds for comparison ----
    print("-" * 75)
    print("CONTEXT: Xsh compounds (h-junction comparison)")
    print("-" * 75)
    print()

    for atom in TEST_ATOMS:
        xsh_compound = atom + 'sh'
        xsh_total = middle_totals.get(xsh_compound, 0)
        xi_total = x_initial_totals.get(atom, 0)

        if xsh_total < MIN_N:
            print(f"  {xsh_compound}: N={xsh_total} -- skipped (< {MIN_N})")
            continue

        xi_primary, xi_pct = get_primary(x_initial_cats[atom], xi_total)
        xsh_primary, xsh_pct = get_primary(middle_cats[xsh_compound], xsh_total)
        is_shift = xi_primary != xsh_primary

        print(f"  {xsh_compound} (N={xsh_total}): primary={xsh_primary} ({xsh_pct:.1f}%)"
              f"  [X-initial: {xi_primary} ({xi_pct:.1f}%)]"
              f"  {'SHIFT' if is_shift else 'SAME'}")

    # ---- Summary table ----
    print()
    print("-" * 75)
    print("SUMMARY TABLE")
    print("-" * 75)
    print()

    header = f"{'Atom':<6} {'X-init N':>8} {'X-init 1st':<15} {'Xs N':>6} {'Xs 1st':<15} {'Shift?':>7}"
    print(header)
    print("-" * len(header))

    for atom, xs_comp, xi_n, xs_n, xi_p, xi_pct, xs_p, xs_pct, is_shift in results:
        print(f"  {atom:<4} {xi_n:>8} {str(xi_p)+' ('+'{:.0f}'.format(xi_pct)+'%)':<15}"
              f" {xs_n:>6} {str(xs_p)+' ('+'{:.0f}'.format(xs_pct)+'%)':<15}"
              f" {'YES' if is_shift else 'NO':>7}")

    # ---- VERDICT ----
    print()
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    print()

    if tested == 0:
        print("  No Xs compounds had N >= %d -- CANNOT EVALUATE" % MIN_N)
        overall = False
    else:
        threshold = 3
        overall = shifted >= threshold
        print(f"  Tested: {tested} Xs compounds with N >= {MIN_N}")
        print(f"  Category shifts: {shifted}/{tested}")
        print(f"  Threshold: >= {threshold}/{tested}")
        print()
        print(f"  OVERALL: {'PASS' if overall else 'FAIL'}")
        if overall:
            print("  s systematically shifts its partner's default category")
        else:
            print("  s does NOT systematically shift its partner's default category")
            print(f"  Only {shifted}/{tested} compounds showed a shift (needed >= {threshold})")


if __name__ == '__main__':
    main()
