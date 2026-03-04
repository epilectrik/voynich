#!/usr/bin/env python3
"""
P-P8: cp vs pc order sensitivity

Test whether reversing atom order in c-p compounds changes the category.

Method:
1. Collect all tokens with MIDDLE = "cp" (exactly) -> classify
2. Collect all tokens with MIDDLE = "pc" (exactly) -> classify
3. Compare majority categories
4. Compute Jensen-Shannon divergence between category distributions
5. Also check: op vs po, ep vs pe
6. Controls: ck vs kc (known flip), ct vs tc (known flip)

Predictions:
- cp and pc have different primary categories
- cp leans toward MONITORING (c=adjust injects monitoring, from Phase 499)
- pc leans toward MARKING (p=pause is MARKING-associated)

Pass: cp and pc have different majority categories AND JSD >= 0.05

Note: cp and pc each have only ~10 tokens. With N=10, acknowledge
statistical weakness but report the data.
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
            print(f"    {cat:<15} {fa*100:>8.1f}%  {fb*100:>8.1f}%  {delta:>+7.1f}%{flag}")

    print()
    print(f"    Primary: {name_a} = {primary_a}, {name_b} = {primary_b}")
    print(f"    Order-sensitive: {'YES' if shifted else 'NO'}")
    print(f"    JSD = {jsd:.4f}")

    if total_a < 15 or total_b < 15:
        print(f"    WARNING: Low N ({total_a}, {total_b}) -- interpret with caution")

    return primary_a, primary_b, jsd, shifted


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    print("=" * 75)
    print("P-P8: cp vs pc order sensitivity")
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

    # ---- TEST 1: Target pair: cp vs pc ----
    print()
    print("-" * 75)
    print("TEST 1: Target pair -- cp vs pc")
    print("-" * 75)

    cp_primary, pc_primary, cp_pc_jsd, cp_pc_shifted = analyze_pair(
        'cp', 'pc', middle_cats['cp'], middle_cats['pc'],
        CATEGORIES, global_cats, global_total
    )

    # ---- TEST 2: Additional p-pairs: op vs po, ep vs pe ----
    print()
    print("-" * 75)
    print("TEST 2: Additional p-containing order pairs")
    print("-" * 75)

    op_primary, po_primary, op_po_jsd, op_po_shifted = analyze_pair(
        'op', 'po', middle_cats['op'], middle_cats['po'],
        CATEGORIES, global_cats, global_total
    )

    ep_primary, pe_primary, ep_pe_jsd, ep_pe_shifted = analyze_pair(
        'ep', 'pe', middle_cats['ep'], middle_cats['pe'],
        CATEGORIES, global_cats, global_total
    )

    # pk vs kp
    pk_primary, kp_primary, pk_kp_jsd, pk_kp_shifted = analyze_pair(
        'pk', 'kp', middle_cats['pk'], middle_cats['kp'],
        CATEGORIES, global_cats, global_total
    )

    # ---- TEST 3: Known controls ----
    print()
    print("-" * 75)
    print("TEST 3: Known order-sensitive controls")
    print("-" * 75)

    ck_primary, kc_primary, ck_kc_jsd, ck_kc_shifted = analyze_pair(
        'ck', 'kc', middle_cats['ck'], middle_cats['kc'],
        CATEGORIES, global_cats, global_total
    )

    ct_primary, tc_primary, ct_tc_jsd, ct_tc_shifted = analyze_pair(
        'ct', 'tc', middle_cats['ct'], middle_cats['tc'],
        CATEGORIES, global_cats, global_total
    )

    # ek vs ke for reference
    ek_primary, ke_primary, ek_ke_jsd, ek_ke_shifted = analyze_pair(
        'ek', 'ke', middle_cats['ek'], middle_cats['ke'],
        CATEGORIES, global_cats, global_total
    )

    # ---- TEST 4: All 2-char MIDDLEs containing p ----
    print()
    print("-" * 75)
    print("TEST 4: All 2-char MIDDLEs containing 'p'")
    print("-" * 75)
    print()

    print(f"{'MIDDLE':<8} {'N':>6} {'Primary':<15} {'p-pos':<8} {'Profile'}")
    print("-" * 60)

    for mid in sorted(middle_cats.keys()):
        if len(mid) == 2 and 'p' in mid:
            counts = middle_cats[mid]
            total = sum(counts.values())
            if total < 2:
                continue
            primary = counts.most_common(1)[0][0]
            p_pos = "FIRST" if mid[0] == 'p' else "SECOND"
            top3 = ', '.join(f"{c}:{n}" for c, n in counts.most_common(3))
            print(f"  {mid:<6} {total:>6} {primary:<15} {p_pos:<8} {top3}")

    # ---- TEST 5: Summary of all order pairs ----
    print()
    print("-" * 75)
    print("TEST 5: Order sensitivity summary across all pairs")
    print("-" * 75)
    print()

    all_pairs = [
        ('cp/pc', cp_primary, pc_primary, cp_pc_jsd, cp_pc_shifted, 'TARGET'),
        ('op/po', op_primary, po_primary, op_po_jsd, op_po_shifted, 'TARGET'),
        ('ep/pe', ep_primary, pe_primary, ep_pe_jsd, ep_pe_shifted, 'TARGET'),
        ('pk/kp', pk_primary, kp_primary, pk_kp_jsd, pk_kp_shifted, 'TARGET'),
        ('ck/kc', ck_primary, kc_primary, ck_kc_jsd, ck_kc_shifted, 'CONTROL'),
        ('ct/tc', ct_primary, tc_primary, ct_tc_jsd, ct_tc_shifted, 'CONTROL'),
        ('ek/ke', ek_primary, ke_primary, ek_ke_jsd, ek_ke_shifted, 'CONTROL'),
    ]

    print(f"{'Pair':<10} {'Fwd Cat':<15} {'Rev Cat':<15} {'Shifted':<10} {'JSD':>8} {'Type':<10}")
    print("-" * 75)
    for name, fwd, rev, jsd, shifted, ptype in all_pairs:
        fwd_str = fwd if fwd else 'N/A'
        rev_str = rev if rev else 'N/A'
        shifted_str = 'YES' if shifted else 'NO'
        if fwd is None or rev is None:
            shifted_str = 'N/A'
        print(f"  {name:<8} {fwd_str:<15} {rev_str:<15} {shifted_str:<10} {jsd:>7.4f} {ptype:<10}")

    # ---- VERDICTS ----
    print()
    print("=" * 75)
    print("VERDICTS")
    print("=" * 75)
    print()

    # Primary test: cp vs pc
    cp_total = sum(middle_cats['cp'].values())
    pc_total = sum(middle_cats['pc'].values())

    if cp_total > 0 and pc_total > 0:
        p1 = cp_pc_shifted
        p2 = cp_pc_jsd >= 0.05
        print(f"  [{'PASS' if p1 else 'FAIL'}] P1: cp and pc have different majority categories: "
              f"cp={cp_primary}, pc={pc_primary}")
        print(f"  [{'PASS' if p2 else 'FAIL'}] P2: cp/pc JSD >= 0.05: {cp_pc_jsd:.4f}")

        # Check specific predictions
        p3 = cp_primary == 'MONITORING' if cp_primary else False
        p4 = pc_primary == 'MARKING' if pc_primary else False
        print(f"  [{'PASS' if p3 else 'FAIL'}] P3: cp leans MONITORING (c first): {cp_primary}")
        print(f"  [{'PASS' if p4 else 'FAIL'}] P4: pc leans MARKING (p first): {pc_primary}")

        primary_pass = p1 and p2
    else:
        print(f"  [SKIP] Insufficient data: cp N={cp_total}, pc N={pc_total}")
        primary_pass = False

    # Control validation
    print()
    print("  Controls:")
    ck_total = sum(middle_cats['ck'].values())
    kc_total = sum(middle_cats['kc'].values())
    if ck_total > 0 and kc_total > 0:
        ctrl1 = ck_kc_shifted
        print(f"  [{'PASS' if ctrl1 else 'FAIL'}] ck/kc known flip: ck={ck_primary}, kc={kc_primary}")
    else:
        print(f"  [SKIP] ck/kc insufficient data")

    ct_total = sum(middle_cats['ct'].values())
    tc_total = sum(middle_cats['tc'].values())
    if ct_total > 0 and tc_total > 0:
        ctrl2 = ct_tc_shifted
        print(f"  [{'PASS' if ctrl2 else 'FAIL'}] ct/tc known flip: ct={ct_primary}, tc={tc_primary}")
    else:
        print(f"  [SKIP] ct/tc insufficient data")

    # Count how many p-pairs are order-sensitive
    p_shifted = sum(1 for name, f, r, j, s, t in all_pairs
                    if t == 'TARGET' and s)
    p_available = sum(1 for name, f, r, j, s, t in all_pairs
                      if t == 'TARGET' and f is not None and r is not None)
    print()
    print(f"  p-containing order-sensitive pairs: {p_shifted}/{p_available}")

    print()
    print(f"  PRIMARY CRITERION (cp != pc AND JSD >= 0.05): {'PASS' if primary_pass else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if primary_pass else 'FAIL'}")

    if cp_total < 15 or pc_total < 15:
        print()
        print("  CAVEAT: Small sample sizes (cp={}, pc={}). Results are directional,".format(
            cp_total, pc_total))
        print("  not statistically robust. Treat as evidence, not proof.")


if __name__ == '__main__':
    main()
