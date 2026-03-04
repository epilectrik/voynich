#!/usr/bin/env python3
"""
S-S8: s-compound order sensitivity

Test whether reversing atom order in s-compound pairs changes the category.

Pairs tested:
1. os (16 tokens) vs so (? tokens) -- o+s vs s+o
2. es (15 tokens) vs se (? tokens) -- e+s vs s+e
3. cs (12 tokens) vs sc (? tokens) -- c+s vs s+c

For each pair:
- Find all tokens with MIDDLE exactly matching each form
- Classify by CategoryClassifier
- Compare primary categories
- Compute Jensen-Shannon divergence between category distributions

Pass: >= 1/3 testable reversed pairs show different majority categories AND JSD >= 0.05
Risk: HIGH -- reversed forms (so, se, sc) may have N < 5. If N < 5, mark INCONCLUSIVE.

Controls: ck vs kc (100% flip from Phase 499), cp vs pc (both MARKING from Phase 500)
"""

import sys
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


def jensen_shannon(p_dist, q_dist, categories):
    """Compute Jensen-Shannon divergence between two category distributions."""
    eps = 1e-10
    jsd = 0
    for cat in categories:
        pi = p_dist.get(cat, 0) + eps
        qi = q_dist.get(cat, 0) + eps
        mi = (pi + qi) / 2
        jsd += 0.5 * pi * math.log2(pi / mi) + 0.5 * qi * math.log2(qi / mi)
    return jsd


def analyze_pair(name_a, name_b, cats_a, cats_b, categories, global_cats, global_total):
    """Analyze a pair of order-reversed MIDDLEs."""
    total_a = sum(cats_a.values())
    total_b = sum(cats_b.values())

    print(f"\n  {name_a} (N={total_a}) vs {name_b} (N={total_b})")

    if total_a == 0 and total_b == 0:
        print("    Both absent from corpus")
        return None, None, 0, False
    if total_a == 0:
        print(f"    {name_a} absent from corpus")
        return None, cats_b.most_common(1)[0][0] if total_b > 0 else None, 0, False
    if total_b == 0:
        print(f"    {name_b} absent from corpus")
        return cats_a.most_common(1)[0][0] if total_a > 0 else None, None, 0, False

    if total_a < 5 or total_b < 5:
        low = name_a if total_a < 5 else name_b
        print(f"    WARNING: {low} has N < 5 -- INCONCLUSIVE")

    # Category profiles
    dist_a = {cat: cats_a.get(cat, 0) / total_a for cat in categories}
    dist_b = {cat: cats_b.get(cat, 0) / total_b for cat in categories}

    primary_a = cats_a.most_common(1)[0][0]
    primary_b = cats_b.most_common(1)[0][0]
    shifted = primary_a != primary_b
    jsd = jensen_shannon(dist_a, dist_b, categories)

    header = f"    {'Category':<15} {name_a:>10} {name_b:>10} {'Delta':>8}"
    print(header)
    print("    " + "-" * 48)

    for cat in categories:
        fa = dist_a.get(cat, 0)
        fb = dist_b.get(cat, 0)
        delta = fa - fb
        na = cats_a.get(cat, 0)
        nb = cats_b.get(cat, 0)
        flag = " ***" if abs(delta) > 0.15 else ""
        if na > 0 or nb > 0:
            print(f"    {cat:<15} {fa*100:>8.1f}%  {fb*100:>8.1f}%  {delta*100:>+7.1f}%{flag}")

    print()
    print(f"    Primary: {name_a} = {primary_a}, {name_b} = {primary_b}")
    print(f"    Order-sensitive: {'YES' if shifted else 'NO'}")
    print(f"    JSD = {jsd:.4f}")

    if total_a < 5 or total_b < 5:
        print(f"    STATUS: INCONCLUSIVE (N < 5)")
    elif shifted and jsd >= 0.05:
        print(f"    STATUS: ORDER-SENSITIVE")
    else:
        print(f"    STATUS: ORDER-INSENSITIVE")

    return primary_a, primary_b, jsd, shifted


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    print("=" * 75)
    print("S-S8: s-compound order sensitivity")
    print("=" * 75)

    # ---- Collect category profiles for all 2-char MIDDLEs ----
    middle_cats = defaultdict(Counter)
    global_cats = Counter()
    global_total = 0

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue

        m = morph.extract(w)
        if not m.middle:
            continue

        mid = m.middle
        cat = cc.classify(mid)
        if cat not in CATEGORIES:
            continue

        global_cats[cat] += 1
        global_total += 1
        middle_cats[mid][cat] += 1

    # ---- TEST 1: Target pairs: os/so, es/se, cs/sc ----
    print()
    print("-" * 75)
    print("TEST 1: Target s-compound order pairs")
    print("-" * 75)

    target_pairs = [('os', 'so'), ('es', 'se'), ('cs', 'sc')]
    target_results = []

    for fwd, rev in target_pairs:
        fwd_primary, rev_primary, jsd, shifted = analyze_pair(
            fwd, rev, middle_cats[fwd], middle_cats[rev],
            CATEGORIES, global_cats, global_total
        )
        fwd_n = sum(middle_cats[fwd].values())
        rev_n = sum(middle_cats[rev].values())
        testable = fwd_n >= 5 and rev_n >= 5
        target_results.append((fwd, rev, fwd_primary, rev_primary, jsd, shifted, testable))

    # ---- TEST 2: Additional s-containing 2-char pairs ----
    print()
    print("-" * 75)
    print("TEST 2: Additional s-containing order pairs")
    print("-" * 75)

    extra_pairs = [('ks', 'sk'), ('ts', 'st'), ('ds', 'sd'), ('ls', 'sl')]
    extra_results = []

    for fwd, rev in extra_pairs:
        fwd_primary, rev_primary, jsd, shifted = analyze_pair(
            fwd, rev, middle_cats[fwd], middle_cats[rev],
            CATEGORIES, global_cats, global_total
        )
        fwd_n = sum(middle_cats[fwd].values())
        rev_n = sum(middle_cats[rev].values())
        testable = fwd_n >= 5 and rev_n >= 5
        extra_results.append((fwd, rev, fwd_primary, rev_primary, jsd, shifted, testable))

    # ---- TEST 3: Known controls ----
    print()
    print("-" * 75)
    print("TEST 3: Known order-sensitive controls")
    print("-" * 75)

    control_pairs = [('ck', 'kc'), ('cp', 'pc'), ('ek', 'ke')]
    control_results = []

    for fwd, rev in control_pairs:
        fwd_primary, rev_primary, jsd, shifted = analyze_pair(
            fwd, rev, middle_cats[fwd], middle_cats[rev],
            CATEGORIES, global_cats, global_total
        )
        fwd_n = sum(middle_cats[fwd].values())
        rev_n = sum(middle_cats[rev].values())
        testable = fwd_n >= 5 and rev_n >= 5
        control_results.append((fwd, rev, fwd_primary, rev_primary, jsd, shifted, testable))

    # ---- TEST 4: All 2-char MIDDLEs containing 's' ----
    print()
    print("-" * 75)
    print("TEST 4: All 2-char MIDDLEs containing 's'")
    print("-" * 75)
    print()

    print(f"{'MIDDLE':<8} {'N':>6} {'Primary':<15} {'s-pos':<8} {'Profile'}")
    print("-" * 60)

    for mid in sorted(middle_cats.keys()):
        if len(mid) == 2 and 's' in mid:
            counts = middle_cats[mid]
            total = sum(counts.values())
            if total < 2:
                continue
            primary = counts.most_common(1)[0][0]
            s_pos = "FIRST" if mid[0] == 's' else "SECOND"
            top3 = ', '.join(f"{c}:{n}" for c, n in counts.most_common(3))
            print(f"  {mid:<6} {total:>6} {primary:<15} {s_pos:<8} {top3}")

    # ---- TEST 5: Summary table ----
    print()
    print("-" * 75)
    print("TEST 5: Order sensitivity summary")
    print("-" * 75)
    print()

    all_results = []
    for fwd, rev, fp, rp, jsd, shifted, testable in target_results:
        all_results.append((f"{fwd}/{rev}", fp, rp, jsd, shifted, testable, 'TARGET'))
    for fwd, rev, fp, rp, jsd, shifted, testable in extra_results:
        all_results.append((f"{fwd}/{rev}", fp, rp, jsd, shifted, testable, 'EXTRA'))
    for fwd, rev, fp, rp, jsd, shifted, testable in control_results:
        all_results.append((f"{fwd}/{rev}", fp, rp, jsd, shifted, testable, 'CONTROL'))

    print(f"{'Pair':<10} {'Fwd Cat':<15} {'Rev Cat':<15} {'Shifted':<10} {'JSD':>8} {'Testable':<10} {'Type':<10}")
    print("-" * 85)
    for name, fwd_cat, rev_cat, jsd, shifted, testable, ptype in all_results:
        fwd_str = fwd_cat if fwd_cat else 'N/A'
        rev_str = rev_cat if rev_cat else 'N/A'
        if fwd_cat is None or rev_cat is None:
            shifted_str = 'N/A'
        else:
            shifted_str = 'YES' if shifted else 'NO'
        test_str = 'YES' if testable else 'NO'
        print(f"  {name:<8} {fwd_str:<15} {rev_str:<15} {shifted_str:<10} {jsd:>7.4f} {test_str:<10} {ptype:<10}")

    # ---- VERDICTS ----
    print()
    print("=" * 75)
    print("VERDICTS")
    print("=" * 75)
    print()

    # Count testable target pairs that show order sensitivity
    testable_targets = [(fwd, rev, fp, rp, jsd, shifted) for fwd, rev, fp, rp, jsd, shifted, t
                        in target_results if t]
    sensitive_targets = [(fwd, rev) for fwd, rev, fp, rp, jsd, shifted in testable_targets
                         if shifted and jsd >= 0.05]
    inconclusive_targets = [(fwd, rev) for fwd, rev, fp, rp, jsd, shifted, t
                            in target_results if not t and (fp is not None or rp is not None)]

    n_testable = len(testable_targets)
    n_sensitive = len(sensitive_targets)
    n_inconclusive = len(inconclusive_targets)

    print(f"  Testable target pairs: {n_testable}/3")
    print(f"  Inconclusive (N < 5): {n_inconclusive}/3")
    print(f"  Order-sensitive (shifted AND JSD >= 0.05): {n_sensitive}/{n_testable}")

    if n_testable > 0:
        p1 = n_sensitive >= 1
        print()
        print(f"  [{'PASS' if p1 else 'FAIL'}] P1: >= 1 testable pair is order-sensitive: "
              f"{n_sensitive}/{n_testable}")
    else:
        p1 = False
        print()
        print(f"  [FAIL] P1: No testable pairs (all N < 5)")

    # Report on inconclusive pairs
    if inconclusive_targets:
        print()
        print("  Inconclusive pairs (directional evidence only):")
        for fwd, rev in inconclusive_targets:
            fwd_n = sum(middle_cats[fwd].values())
            rev_n = sum(middle_cats[rev].values())
            fwd_cat = middle_cats[fwd].most_common(1)[0][0] if fwd_n > 0 else 'N/A'
            rev_cat = middle_cats[rev].most_common(1)[0][0] if rev_n > 0 else 'N/A'
            print(f"    {fwd}(N={fwd_n})={fwd_cat} vs {rev}(N={rev_n})={rev_cat}")

    # Control validation
    print()
    print("  Controls:")
    for fwd, rev, fp, rp, jsd, shifted, testable in control_results:
        if testable:
            status = "PASS" if shifted else "FAIL"
            print(f"    [{status}] {fwd}/{rev}: {fp} vs {rp} (JSD={jsd:.4f})")
        else:
            print(f"    [SKIP] {fwd}/{rev}: insufficient data")

    print()
    primary_pass = p1
    print(f"  PRIMARY CRITERION (>= 1/3 testable pairs order-sensitive): {'PASS' if primary_pass else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if primary_pass else 'FAIL'}")

    if n_inconclusive > 0:
        print()
        print(f"  CAVEAT: {n_inconclusive} pair(s) inconclusive due to low N.")
        print("  Results are directional, not statistically robust for those pairs.")


if __name__ == '__main__':
    main()
