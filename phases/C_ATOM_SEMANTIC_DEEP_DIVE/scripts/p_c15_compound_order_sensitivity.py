"""
P-C15: c+X vs X+c Order Sensitivity
=====================================
Test whether c is order-sensitive: c must be FIRST to function as modifier.

Method:
1. Find all compounds where c and another atom appear in both orders: c+X and X+c
2. For each pair, compare category profiles
3. If c+X != X+c in category, c carries positional semantic content
4. Compare to other atom pairs that show order sensitivity (e.g., ke vs ek)

Pass: >= 2 order-sensitive pairs with different primary categories
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


def jensen_shannon(p, q, categories):
    """Compute Jensen-Shannon divergence between two category distributions."""
    import math
    eps = 1e-10
    jsd = 0
    for cat in categories:
        pi = p.get(cat, 0) + eps
        qi = q.get(cat, 0) + eps
        mi = (pi + qi) / 2
        jsd += 0.5 * pi * math.log2(pi / mi) + 0.5 * qi * math.log2(qi / mi)
    return jsd


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Collect category profiles for all MIDDLEs
    middle_cats = defaultdict(Counter)

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
        middle_cats[mid][cat] += 1

    print("=" * 80)
    print("P-C15: c+X vs X+c Order Sensitivity")
    print("=" * 80)

    # --- Part 1: Find c-containing order pairs ---
    print("\n--- c-Containing Order Pairs ---")

    # Find all 2-char MIDDLEs containing 'c'
    c_pairs = {}  # {(atom1, atom2): {'forward': mid1, 'reverse': mid2}}
    for mid, counts in middle_cats.items():
        if len(mid) == 2 and 'c' in mid and sum(counts.values()) >= 3:
            a, b = mid[0], mid[1]
            if a == 'c':
                key = (a, b)
                if key not in c_pairs:
                    c_pairs[key] = {}
                c_pairs[key]['forward'] = mid
            elif b == 'c':
                key = (a, b)
                # Also check reverse
                rev_key = (b, a)
                if rev_key not in c_pairs:
                    c_pairs[rev_key] = {}
                c_pairs[rev_key]['reverse'] = mid

    # Also directly search: for each c+X, check if X+c exists
    order_pairs = []
    checked = set()
    for mid in middle_cats:
        if len(mid) == 2 and mid[0] == 'c':
            other = mid[1]
            reverse = other + 'c'
            pair_key = tuple(sorted([mid, reverse]))
            if pair_key in checked:
                continue
            checked.add(pair_key)

            fwd_counts = middle_cats.get(mid, Counter())
            rev_counts = middle_cats.get(reverse, Counter())
            fwd_total = sum(fwd_counts.values())
            rev_total = sum(rev_counts.values())

            if fwd_total >= 3 and rev_total >= 3:
                order_pairs.append((mid, reverse, fwd_counts, rev_counts, fwd_total, rev_total))

    if not order_pairs:
        # Also check 3-char compounds
        for mid in middle_cats:
            if len(mid) >= 2 and mid[0] == 'c':
                other_atoms = mid[1:]
                reverse = other_atoms + 'c'
                if reverse in middle_cats:
                    fwd_counts = middle_cats[mid]
                    rev_counts = middle_cats[reverse]
                    fwd_total = sum(fwd_counts.values())
                    rev_total = sum(rev_counts.values())
                    if fwd_total >= 3 and rev_total >= 3:
                        pair_key = tuple(sorted([mid, reverse]))
                        if pair_key not in checked:
                            checked.add(pair_key)
                            order_pairs.append((mid, reverse, fwd_counts, rev_counts, fwd_total, rev_total))

    print(f"\nFound {len(order_pairs)} c-containing order pairs (both orders N>=3)")

    order_sensitive_count = 0

    for fwd, rev, fwd_counts, rev_counts, fwd_total, rev_total in order_pairs:
        fwd_primary = fwd_counts.most_common(1)[0][0]
        rev_primary = rev_counts.most_common(1)[0][0]
        shifted = fwd_primary != rev_primary

        # Compute distributions
        fwd_dist = {cat: fwd_counts.get(cat, 0) / fwd_total for cat in CATEGORIES}
        rev_dist = {cat: rev_counts.get(cat, 0) / rev_total for cat in CATEGORIES}
        jsd = jensen_shannon(fwd_dist, rev_dist, CATEGORIES)

        # Chi-square test on the contingency table
        observed = []
        for cat in CATEGORIES:
            observed.append([fwd_counts.get(cat, 0), rev_counts.get(cat, 0)])
        # Filter zero rows
        observed_nz = [row for row in observed if sum(row) > 0]
        if len(observed_nz) >= 2:
            chi2, p_val, dof, _ = stats.chi2_contingency(observed_nz)
        else:
            chi2, p_val, dof = 0, 1.0, 0

        if shifted:
            order_sensitive_count += 1

        print(f"\n  {fwd} (N={fwd_total}) vs {rev} (N={rev_total})")
        print(f"  Primary: {fwd} -> {fwd_primary}, {rev} -> {rev_primary}")
        print(f"  Order-sensitive: {'YES' if shifted else 'no'}")
        print(f"  JSD = {jsd:.4f}, chi2 = {chi2:.1f}, p = {p_val:.4f}")
        print(f"  {'Category':<15} {fwd:<12} {rev:<12} {'Delta'}")
        for cat in CATEGORIES:
            f_frac = fwd_dist.get(cat, 0)
            r_frac = rev_dist.get(cat, 0)
            delta = f_frac - r_frac
            flag = " ***" if abs(delta) > 0.15 else ""
            if f_frac > 0 or r_frac > 0:
                print(f"  {cat:<15} {f_frac:<12.1%} {r_frac:<12.1%} {delta:+.1%}{flag}")

    # --- Part 2: Non-c order pairs for comparison ---
    print("\n\n--- Non-c Order Pairs for Comparison ---")

    non_c_pairs = []
    checked2 = set()
    for mid in middle_cats:
        if len(mid) == 2 and 'c' not in mid:
            reverse = mid[1] + mid[0]
            pair_key = tuple(sorted([mid, reverse]))
            if pair_key in checked2:
                continue
            checked2.add(pair_key)

            fwd_counts = middle_cats.get(mid, Counter())
            rev_counts = middle_cats.get(reverse, Counter())
            fwd_total = sum(fwd_counts.values())
            rev_total = sum(rev_counts.values())

            if fwd_total >= 10 and rev_total >= 10:
                fwd_primary = fwd_counts.most_common(1)[0][0]
                rev_primary = rev_counts.most_common(1)[0][0]

                fwd_dist = {cat: fwd_counts.get(cat, 0) / fwd_total for cat in CATEGORIES}
                rev_dist = {cat: rev_counts.get(cat, 0) / rev_total for cat in CATEGORIES}
                jsd = jensen_shannon(fwd_dist, rev_dist, CATEGORIES)

                non_c_pairs.append({
                    'fwd': mid, 'rev': reverse,
                    'fwd_n': fwd_total, 'rev_n': rev_total,
                    'fwd_primary': fwd_primary, 'rev_primary': rev_primary,
                    'shifted': fwd_primary != rev_primary,
                    'jsd': jsd
                })

    # Sort by JSD descending
    non_c_pairs.sort(key=lambda x: x['jsd'], reverse=True)

    print(f"\nFound {len(non_c_pairs)} non-c order pairs (both N>=10)")
    print(f"\nTop 10 by JSD:")
    print(f"{'Pair':<20} {'N_fwd':<8} {'N_rev':<8} {'Fwd Cat':<15} {'Rev Cat':<15} {'Shifted':<10} {'JSD'}")
    print("-" * 90)

    non_c_shifted = sum(1 for p in non_c_pairs if p['shifted'])
    for p in non_c_pairs[:10]:
        marker = "YES" if p['shifted'] else "no"
        print(f"{p['fwd']} vs {p['rev']:<12} {p['fwd_n']:<8} {p['rev_n']:<8} "
              f"{p['fwd_primary']:<15} {p['rev_primary']:<15} {marker:<10} {p['jsd']:.4f}")

    non_c_shift_rate = non_c_shifted / len(non_c_pairs) if non_c_pairs else 0
    print(f"\nNon-c order sensitivity rate: {non_c_shifted}/{len(non_c_pairs)} = {non_c_shift_rate:.1%}")

    # --- Part 3: All 2-char MIDDLEs with c for broader context ---
    print("\n\n--- All 2-Char MIDDLEs Containing 'c' ---")
    print(f"{'MIDDLE':<8} {'Tokens':<8} {'Primary':<15} {'c-pos':<8} {'Profile'}")
    print("-" * 70)

    for mid in sorted(middle_cats.keys()):
        if len(mid) == 2 and 'c' in mid:
            counts = middle_cats[mid]
            total = sum(counts.values())
            if total < 3:
                continue
            primary = counts.most_common(1)[0][0]
            c_pos = "FIRST" if mid[0] == 'c' else "SECOND"
            top3 = ', '.join(f"{c}:{n}" for c, n in counts.most_common(3))
            print(f"{mid:<8} {total:<8} {primary:<15} {c_pos:<8} {top3}")

    # --- Verdicts ---
    print("\n" + "=" * 80)
    print("VERDICTS")
    print("=" * 80)

    v1 = order_sensitive_count >= 2
    print(f"\n[{'PASS' if v1 else 'FAIL'}] >= 2 c order-sensitive pairs: {order_sensitive_count} found")

    # Check if c's order sensitivity is comparable to other atoms
    c_shift_rate_val = order_sensitive_count / len(order_pairs) if order_pairs else 0
    v2 = c_shift_rate_val >= non_c_shift_rate if non_c_pairs else True
    print(f"[{'PASS' if v2 else 'FAIL'}] c order sensitivity >= non-c baseline: "
          f"c={c_shift_rate_val:.1%} vs non-c={non_c_shift_rate:.1%}")

    overall = v1
    print(f"\n{'='*80}")
    print(f"OVERALL: {'PASS' if overall else 'FAIL'} (>= 2 order-sensitive pairs)")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
