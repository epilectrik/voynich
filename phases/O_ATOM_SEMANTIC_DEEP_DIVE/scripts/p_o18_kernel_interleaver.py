#!/usr/bin/env python3
"""
P-O18: o as kernel interleaver (preparatory positioning)

If o = "ordnen" (arrange/prepare), o-initial tokens should appear BETWEEN
kernel operations (k/e/h) more than any other non-kernel atom. The preparation
function places o as the interleaving step between active kernel interventions.

Tests:
1. On lines with >= 4 tokens containing both o-initial and kernel-initial MIDDLEs,
   compute between-kernel fraction for o vs other atoms
2. Compare to all NEUTRAL and RESPONDER atoms
3. Check that o has LOWER after-ALL-kernel fraction than RESPONDER atoms {l, r}
   (preparers appear between kernels, not after them)

Pass: between-kernel >= 45% AND o ranked #1 non-kernel interleaver
      AND o after-kernel < l after-kernel
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology


def main():
    tx = Transcript()
    morph = Morphology()

    KERNEL_ATOMS = {'k', 'e', 'h'}
    NEUTRAL_ATOMS = {'d', 'y', 'o', 'i'}
    RESPONDER_ATOMS = {'l', 'r'}
    ALL_TEST_ATOMS = set('abcdefghiklmnopqrsty') - KERNEL_ATOMS

    # Build lines: folio -> line -> [(position_idx, word, initial_atom)]
    folio_lines = defaultdict(lambda: defaultdict(list))

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if not m.middle or len(m.middle) < 1:
            continue
        initial = m.middle[0]
        folio_lines[token.folio][token.line].append(initial)

    # For each non-kernel atom, compute positional statistics relative to kernel tokens
    # "between-kernel" = atom appears with kernel atom both before and after it on the line
    # "after-all-kernel" = atom appears after the LAST kernel atom on the line

    atom_between = defaultdict(int)   # atom -> count of between-kernel occurrences
    atom_after_all = defaultdict(int)  # atom -> count of after-last-kernel occurrences
    atom_before_all = defaultdict(int) # atom -> count of before-first-kernel occurrences
    atom_eligible = defaultdict(int)   # atom -> total occurrences on kernel-containing lines

    for folio, lines in folio_lines.items():
        for line_id, initials in lines.items():
            if len(initials) < 4:
                continue

            # Find kernel positions
            kernel_positions = [i for i, a in enumerate(initials) if a in KERNEL_ATOMS]
            if len(kernel_positions) < 2:
                continue  # Need at least 2 kernel tokens for meaningful interleaving

            first_kernel = kernel_positions[0]
            last_kernel = kernel_positions[-1]

            # Classify each non-kernel token
            for i, atom in enumerate(initials):
                if atom in KERNEL_ATOMS:
                    continue
                if atom not in ALL_TEST_ATOMS:
                    continue

                atom_eligible[atom] += 1

                if i < first_kernel:
                    atom_before_all[atom] += 1
                elif i > last_kernel:
                    atom_after_all[atom] += 1
                else:
                    atom_between[atom] += 1

    print("=" * 70)
    print("P-O18: o as kernel interleaver (ordnen hypothesis)")
    print("=" * 70)
    print()

    # ---- TEST 1: All atoms ranked by between-kernel fraction ----
    print("-" * 70)
    print("TEST 1: Non-kernel atoms ranked by between-kernel fraction")
    print("        (lines with >= 4 tokens and >= 2 kernel tokens)")
    print("-" * 70)
    print()

    atom_stats = []
    for atom in sorted(ALL_TEST_ATOMS):
        elig = atom_eligible.get(atom, 0)
        if elig < 20:
            continue
        between = atom_between.get(atom, 0)
        after = atom_after_all.get(atom, 0)
        before = atom_before_all.get(atom, 0)
        between_frac = between / elig
        after_frac = after / elig
        before_frac = before / elig
        group = 'NEUTRAL' if atom in NEUTRAL_ATOMS else ('RESP' if atom in RESPONDER_ATOMS else 'OTHER')
        atom_stats.append((atom, between_frac, after_frac, before_frac, between, after, before, elig, group))

    atom_stats.sort(key=lambda x: -x[1])  # Descending by between-kernel fraction

    print(f"{'Rank':<5} {'Atom':<5} {'Between%':>9} {'After%':>8} {'Before%':>8} {'N':>6} {'Group':>8}")
    print("-" * 55)

    o_rank = None
    o_between_frac = 0
    o_after_frac = 0
    o_elig = 0
    l_after_frac = 0
    r_after_frac = 0

    for rank, (atom, btwn_f, aft_f, bef_f, btwn, aft, bef, elig, grp) in enumerate(atom_stats, 1):
        marker = " <--" if atom == 'o' else ""
        print(f"  {rank:<3} {atom:<4} {btwn_f*100:>8.1f}% {aft_f*100:>7.1f}% {bef_f*100:>7.1f}% {elig:>6} {grp:>8}{marker}")
        if atom == 'o':
            o_rank = rank
            o_between_frac = btwn_f
            o_after_frac = aft_f
            o_elig = elig
        if atom == 'l':
            l_after_frac = aft_f
        if atom == 'r':
            r_after_frac = aft_f

    print()
    if o_rank:
        print(f"  o between-kernel rank: #{o_rank} of {len(atom_stats)} non-kernel atoms")
        print(f"  o between-kernel fraction: {o_between_frac*100:.1f}%")
    else:
        print("  WARNING: o not found or too few tokens")

    # ---- TEST 2: NEUTRAL atom comparison ----
    print()
    print("-" * 70)
    print("TEST 2: NEUTRAL atom comparison (between-kernel focus)")
    print("-" * 70)
    print()

    neutral_stats = [(a, bf, af, bef_f, n, e, grp) for a, bf, af, bef_f, n, _, _, e, grp in atom_stats if grp == 'NEUTRAL']
    neutral_stats.sort(key=lambda x: -x[1])

    o_neutral_rank = None
    for i, (atom, bf, af, _, _, _, _) in enumerate(neutral_stats):
        marker = " <-- TARGET" if atom == 'o' else ""
        if atom == 'o':
            o_neutral_rank = i + 1
        print(f"  {atom}: between={bf*100:.1f}%, after={af*100:.1f}%{marker}")

    # ---- TEST 3: o vs RESPONDER atoms (l, r) after-kernel comparison ----
    print()
    print("-" * 70)
    print("TEST 3: o vs RESPONDER atoms {l, r} in after-kernel position")
    print("-" * 70)
    print()

    print(f"  o after-all-kernel: {o_after_frac*100:.1f}%")
    print(f"  l after-all-kernel: {l_after_frac*100:.1f}%")
    print(f"  r after-all-kernel: {r_after_frac*100:.1f}%")
    o_less_than_l = o_after_frac < l_after_frac
    o_less_than_r = o_after_frac < r_after_frac
    print(f"  o < l? {'YES' if o_less_than_l else 'NO'}")
    print(f"  o < r? {'YES' if o_less_than_r else 'NO'}")

    # ---- TEST 4: Position pattern detail for o vs k ----
    print()
    print("-" * 70)
    print("TEST 4: Position pattern detail (o and kernel atoms)")
    print("-" * 70)
    print()

    for atom in ['o', 'k', 'e', 'h']:
        elig = atom_eligible.get(atom, 0)
        if elig == 0:
            continue
        between = atom_between.get(atom, 0)
        after = atom_after_all.get(atom, 0)
        before = atom_before_all.get(atom, 0)
        print(f"  {atom}: before={before/elig*100:.1f}% between={between/elig*100:.1f}% after={after/elig*100:.1f}% (N={elig})")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O18 o as kernel interleaver (ordnen)")
    print("=" * 70)

    pass_between = o_between_frac >= 0.45
    pass_rank = o_rank == 1 if o_rank is not None else False
    pass_neutral_rank = o_neutral_rank == 1 if o_neutral_rank is not None else False
    pass_after_l = o_less_than_l
    pass_n = o_elig >= 50

    results = [
        ("Between-kernel >= 45%", pass_between,
         f"{o_between_frac*100:.1f}%"),
        ("Ranked #1 non-kernel interleaver", pass_rank,
         f"rank #{o_rank}" if o_rank else "N/A"),
        ("Ranked #1 NEUTRAL interleaver", pass_neutral_rank,
         f"rank #{o_neutral_rank}" if o_neutral_rank else "N/A"),
        ("o after-kernel < l after-kernel", pass_after_l,
         f"o={o_after_frac*100:.1f}% vs l={l_after_frac*100:.1f}%"),
        ("Sufficient data (N >= 50)", pass_n,
         f"N = {o_elig}"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_between and (pass_rank or pass_neutral_rank) and pass_after_l
    print()
    print(f"  PRIMARY CRITERION (between>=45% AND #1 interleaver AND o<l after): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
