"""
P-O10: o-initial tokens interleave between kernel operations on lines

If o = "vessel" (physical object requiring intermittent management), o-initial
tokens should appear BETWEEN kernel operations: k...o...k or e...o...e.

Tests:
1. On lines with both o-initial and kernel MIDDLEs, check if o-initial tokens
   fall between kernel extremes.
2. Mean distance from o-initial to nearest kernel neighbor.
3. Compare to other NEUTRAL atoms (d, y, i).
4. Compare to RESPONDER atoms (l, n, r) - l should be AFTER kernel, not interleaved.

Pass criterion: o between kernel extremes >= 60% of mixed lines.
Mean o-to-kernel distance > 1.5 positions.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology


def normal_cdf(x):
    """Approximate CDF of standard normal distribution."""
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    d = 0.3989422804014327
    p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.8212560 + t * 1.3302744))))
    return 1.0 - p if x > 0 else p


def is_kernel_initial(middle):
    """Check if MIDDLE starts with a kernel atom (k, e, h)."""
    if not middle:
        return False
    return middle[0] in {'k', 'e', 'h'}


def is_atom_initial(middle, atom):
    """Check if MIDDLE starts with the given atom."""
    if not middle:
        return False
    return middle[0] == atom


def main():
    tx = Transcript()
    morph = Morphology()

    # Atoms to compare
    NEUTRAL_ATOMS = ['o', 'd', 'y', 'i']
    RESPONDER_ATOMS = ['l', 'n', 'r']
    ALL_TEST_ATOMS = NEUTRAL_ATOMS + RESPONDER_ATOMS

    # ---------------------------------------------------------------------------
    # Build line-level data: list of (position, middle, is_kernel, atom_initial)
    # ---------------------------------------------------------------------------
    # folio -> line -> [(pos, middle)]
    line_data = defaultdict(lambda: defaultdict(list))

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle if m.middle else ''
        line_data[token.folio][token.line].append(mid)

    # Flatten to list of lines
    all_lines = []
    for folio in sorted(line_data.keys()):
        for line_id in sorted(line_data[folio].keys()):
            mids = line_data[folio][line_id]
            if len(mids) >= 4:  # Need enough tokens
                all_lines.append(mids)

    print("=" * 70)
    print("P-O10: o-initial tokens interleave between kernel operations")
    print("=" * 70)
    print(f"\nTotal lines with >= 4 tokens: {len(all_lines)}")

    # ---------------------------------------------------------------------------
    # For each test atom, compute interleaving metrics
    # ---------------------------------------------------------------------------
    results = {}

    for atom in ALL_TEST_ATOMS:
        # Find lines that have BOTH atom-initial MIDDLEs AND kernel-initial MIDDLEs
        mixed_lines = 0
        between_count = 0
        not_between_count = 0
        distances_to_kernel = []  # min distance from each atom-initial to nearest kernel

        for mids in all_lines:
            # Find positions of atom-initial and kernel-initial tokens
            atom_positions = []
            kernel_positions = []

            for pos, mid in enumerate(mids):
                if is_atom_initial(mid, atom):
                    atom_positions.append(pos)
                if is_kernel_initial(mid):
                    kernel_positions.append(pos)

            # Need at least 1 atom-initial and 2 kernel tokens for "between" test
            if not atom_positions or len(kernel_positions) < 2:
                continue

            mixed_lines += 1
            k_min = min(kernel_positions)
            k_max = max(kernel_positions)

            # Check each atom-initial token
            for a_pos in atom_positions:
                if k_min < a_pos < k_max:
                    between_count += 1
                else:
                    not_between_count += 1

                # Distance to nearest kernel
                min_dist = min(abs(a_pos - kp) for kp in kernel_positions)
                distances_to_kernel.append(min_dist)

        total_atom_tokens = between_count + not_between_count
        between_frac = between_count / total_atom_tokens if total_atom_tokens > 0 else 0
        mean_dist = sum(distances_to_kernel) / len(distances_to_kernel) if distances_to_kernel else 0

        # Also compute: fraction of lines where MEAN atom pos is between kernel extremes
        line_between_count = 0
        for mids in all_lines:
            atom_positions = [pos for pos, mid in enumerate(mids) if is_atom_initial(mid, atom)]
            kernel_positions = [pos for pos, mid in enumerate(mids) if is_kernel_initial(mid)]

            if not atom_positions or len(kernel_positions) < 2:
                continue

            mean_atom_pos = sum(atom_positions) / len(atom_positions)
            k_min = min(kernel_positions)
            k_max = max(kernel_positions)

            if k_min < mean_atom_pos < k_max:
                line_between_count += 1

        line_between_frac = line_between_count / mixed_lines if mixed_lines > 0 else 0

        # Compute: fraction of atom tokens that come AFTER all kernel tokens
        after_all_kernel = 0
        for mids in all_lines:
            atom_positions = [pos for pos, mid in enumerate(mids) if is_atom_initial(mid, atom)]
            kernel_positions = [pos for pos, mid in enumerate(mids) if is_kernel_initial(mid)]
            if not atom_positions or not kernel_positions:
                continue
            k_max = max(kernel_positions)
            for a_pos in atom_positions:
                if a_pos > k_max:
                    after_all_kernel += 1

        after_frac = after_all_kernel / total_atom_tokens if total_atom_tokens > 0 else 0

        results[atom] = {
            'mixed_lines': mixed_lines,
            'total_tokens': total_atom_tokens,
            'between_frac': between_frac,
            'line_between_frac': line_between_frac,
            'mean_dist': mean_dist,
            'after_frac': after_frac,
            'n_distances': len(distances_to_kernel),
        }

    # ---------------------------------------------------------------------------
    # Print results
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 1-2: Per-atom interleaving metrics")
    print("=" * 70)

    print(f"\n{'Atom':<6} {'Mixed':>6} {'Tokens':>7} {'Between%':>9} {'LineBtwn%':>10} {'MeanDist':>9} {'After%':>8}")
    print("-" * 60)
    for atom in ALL_TEST_ATOMS:
        r = results[atom]
        group = 'NEUTRAL' if atom in NEUTRAL_ATOMS else 'RESPOND'
        print(f"  {atom} ({group[0]}) {r['mixed_lines']:>5}  {r['total_tokens']:>6}  "
              f"{r['between_frac']:>8.1%}  {r['line_between_frac']:>9.1%}  "
              f"{r['mean_dist']:>8.2f}  {r['after_frac']:>7.1%}")

    # ---------------------------------------------------------------------------
    # Test 3: Compare o to other NEUTRAL atoms
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 3: o vs other NEUTRAL atoms (interleaving comparison)")
    print("=" * 70)

    o_between = results['o']['between_frac']
    o_line_between = results['o']['line_between_frac']
    o_mean_dist = results['o']['mean_dist']

    for atom in NEUTRAL_ATOMS:
        if atom == 'o':
            continue
        r = results[atom]
        print(f"  o vs {atom}:")
        print(f"    Between fraction: o={o_between:.3f} vs {atom}={r['between_frac']:.3f} "
              f"(diff={o_between - r['between_frac']:+.3f})")
        print(f"    Line-between:     o={o_line_between:.3f} vs {atom}={r['line_between_frac']:.3f}")
        print(f"    Mean distance:    o={o_mean_dist:.2f} vs {atom}={r['mean_dist']:.2f}")

    # ---------------------------------------------------------------------------
    # Test 4: Compare to RESPONDER atoms (l should be after, not interleaved)
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Test 4: o vs RESPONDER atoms (l,n,r)")
    print("=" * 70)

    for atom in RESPONDER_ATOMS:
        r = results[atom]
        print(f"  o vs {atom}:")
        print(f"    Between fraction: o={o_between:.3f} vs {atom}={r['between_frac']:.3f}")
        print(f"    After-all-kernel: o={results['o']['after_frac']:.3f} vs {atom}={r['after_frac']:.3f}")
        print(f"    Pattern: o={'INTERLEAVED' if o_between > r['between_frac'] else 'LESS INTERLEAVED'}, "
              f"{atom}={'AFTER' if r['after_frac'] > results['o']['after_frac'] else 'NOT AFTER'}")

    # ---------------------------------------------------------------------------
    # Rank atoms by "interleaving score" (between fraction)
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("Atom ranking by interleaving score (between-kernel fraction)")
    print("=" * 70)

    ranked = sorted(ALL_TEST_ATOMS, key=lambda a: results[a]['between_frac'], reverse=True)
    for i, atom in enumerate(ranked):
        r = results[atom]
        group = 'NEUTRAL' if atom in NEUTRAL_ATOMS else 'RESPOND'
        marker = " <-- O" if atom == 'o' else ""
        print(f"  #{i+1} {atom} ({group}): between={r['between_frac']:.3f}, "
              f"line_between={r['line_between_frac']:.3f}, "
              f"after={r['after_frac']:.3f}{marker}")

    o_rank = ranked.index('o') + 1

    # ---------------------------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------------------------
    print(f"\n{'='*70}")
    print("SUMMARY: P-O10 o-initial kernel interleaving")
    print("=" * 70)

    o_r = results['o']

    t1_pass = o_r['line_between_frac'] >= 0.60
    t2_pass = o_r['mean_dist'] <= 2.5  # Close to kernel but not adjacent
    # o should be more interleaved than l (l is post-kernel per C1385)
    l_r = results.get('l', {'between_frac': 0, 'after_frac': 0})
    t3_pass = o_r['between_frac'] > l_r['between_frac']
    # o should have lower after-fraction than l
    t4_pass = o_r['after_frac'] < l_r['after_frac']

    print(f"\n  Test 1 (line-between >= 60%):     {o_r['line_between_frac']:.1%}")
    print(f"    Pass?                            {'PASS' if t1_pass else 'FAIL'}")
    print(f"\n  Test 2 (mean distance <= 2.5):     {o_r['mean_dist']:.2f}")
    print(f"    Pass?                            {'PASS' if t2_pass else 'FAIL'}")
    print(f"\n  Test 3 (o more interleaved than l): o={o_r['between_frac']:.3f} vs l={l_r['between_frac']:.3f}")
    print(f"    Pass?                            {'PASS' if t3_pass else 'FAIL'}")
    print(f"\n  Test 4 (o less after-kernel than l): o={o_r['after_frac']:.3f} vs l={l_r['after_frac']:.3f}")
    print(f"    Pass?                            {'PASS' if t4_pass else 'FAIL'}")

    tests_passed = sum([t1_pass, t2_pass, t3_pass, t4_pass])
    print(f"\n  o interleaving rank: #{o_rank} of {len(ALL_TEST_ATOMS)}")
    print(f"  OVERALL: {tests_passed}/4 tests passed")
    print(f"  VERDICT: {'PASS' if tests_passed >= 3 else 'FAIL'} (need 3/4)")


if __name__ == '__main__':
    main()
