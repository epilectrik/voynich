"""
P-C16: h-Suffix as Category Transformer on c-Compounds
========================================================
Test whether adding h to a c+X compound systematically transforms its category.

Method:
1. Compare paired compounds: ck vs ckh, ct vs cth, cp vs cph, cf vs cfh
2. For each pair, compute category before h (c+X) and after h (c+X+h)
3. Does adding h consistently shift the category? In which direction?
4. Is the transformation systematic (always same direction)?

Known data:
- ck=OPERATION -> ckh=CONTAINMENT (shift)
- ct=MONITORING -> cth=MARKING (shift)
- cp=MARKING -> cph=MONITORING (shift: MARKING->MONITORING)
- cf=MARKING -> cfh=MARKING (no shift)

Pass: >= 3/4 pairs show shift AND transformation is non-random (chi-square p < 0.05)
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


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
    print("P-C16: h-Suffix as Category Transformer on c-Compounds")
    print("=" * 80)

    # --- Part 1: Known c+X / c+Xh pairs ---
    known_pairs = [
        ('ck', 'ckh'),
        ('ct', 'cth'),
        ('cp', 'cph'),
        ('cf', 'cfh'),
    ]

    # Also discover any additional c+X / c+Xh pairs
    c_middles = [mid for mid in middle_cats if mid.startswith('c') and len(mid) >= 2]
    discovered_pairs = []
    for mid in c_middles:
        if not mid.endswith('h'):
            h_form = mid + 'h'
            if h_form in middle_cats:
                pair = (mid, h_form)
                if pair not in known_pairs:
                    discovered_pairs.append(pair)

    all_pairs = known_pairs + discovered_pairs

    print(f"\nKnown pairs: {len(known_pairs)}")
    print(f"Discovered additional pairs: {len(discovered_pairs)}")
    if discovered_pairs:
        for base, h_form in discovered_pairs:
            print(f"  {base} -> {h_form}")

    # --- Part 2: Paired comparison ---
    print("\n--- Paired Category Comparison: c+X vs c+Xh ---")
    print(f"{'Base':<8} {'N':<6} {'Primary':<15} {'h-form':<8} {'N':<6} {'Primary':<15} {'Shifted?':<10} {'Direction'}")
    print("-" * 85)

    shift_count = 0
    total_count = 0
    shift_directions = []

    pair_results = []

    for base, h_form in all_pairs:
        base_counts = middle_cats.get(base, Counter())
        h_counts = middle_cats.get(h_form, Counter())
        base_total = sum(base_counts.values())
        h_total = sum(h_counts.values())

        if base_total < 3 or h_total < 3:
            continue

        base_primary = base_counts.most_common(1)[0][0]
        h_primary = h_counts.most_common(1)[0][0]
        shifted = base_primary != h_primary
        direction = f"{base_primary} -> {h_primary}" if shifted else "SAME"

        total_count += 1
        if shifted:
            shift_count += 1
            shift_directions.append((base_primary, h_primary))

        marker = "YES" if shifted else "no"
        print(f"{base:<8} {base_total:<6} {base_primary:<15} {h_form:<8} {h_total:<6} {h_primary:<15} {marker:<10} {direction}")

        pair_results.append({
            'base': base, 'h_form': h_form,
            'base_counts': base_counts, 'h_counts': h_counts,
            'base_total': base_total, 'h_total': h_total,
            'base_primary': base_primary, 'h_primary': h_primary,
            'shifted': shifted
        })

    shift_rate = shift_count / total_count if total_count > 0 else 0
    print(f"\nShift rate: {shift_count}/{total_count} = {shift_rate:.1%}")

    # --- Part 3: Full category profiles ---
    print("\n--- Full Category Profiles for Each Pair ---")

    for pr in pair_results:
        base = pr['base']
        h_form = pr['h_form']
        base_counts = pr['base_counts']
        h_counts = pr['h_counts']
        base_total = pr['base_total']
        h_total = pr['h_total']

        print(f"\n  {base} (N={base_total}) vs {h_form} (N={h_total})")
        print(f"  {'Category':<15} {base:<12} {h_form:<12} {'Delta'}")
        for cat in CATEGORIES:
            b_frac = base_counts.get(cat, 0) / base_total
            h_frac = h_counts.get(cat, 0) / h_total
            delta = h_frac - b_frac
            flag = " ***" if abs(delta) > 0.15 else ""
            if b_frac > 0 or h_frac > 0:
                print(f"  {cat:<15} {b_frac:<12.1%} {h_frac:<12.1%} {delta:+.1%}{flag}")

    # --- Part 4: Transformation direction analysis ---
    print("\n--- Transformation Direction Analysis ---")

    if shift_directions:
        print(f"\nObserved shifts (N={len(shift_directions)}):")
        for src, dst in shift_directions:
            print(f"  {src} -> {dst}")

        # Check for systematic pattern
        dst_cats = Counter(dst for _, dst in shift_directions)
        src_cats = Counter(src for src, _ in shift_directions)
        print(f"\nSource categories: {dict(src_cats)}")
        print(f"Destination categories: {dict(dst_cats)}")

        # Is there a dominant destination?
        if dst_cats:
            top_dst = dst_cats.most_common(1)[0]
            print(f"Most common destination: {top_dst[0]} ({top_dst[1]}/{len(shift_directions)})")

        # Check monitoring/containment hypothesis
        mon_cont_count = sum(1 for _, dst in shift_directions
                            if dst in ('MONITORING', 'CONTAINMENT'))
        print(f"\nShifts toward MONITORING or CONTAINMENT: {mon_cont_count}/{len(shift_directions)}")
    else:
        print("  No shifts observed")

    # --- Part 5: Chi-square test for non-randomness ---
    print("\n--- Chi-Square Test for Systematic Transformation ---")

    # Build contingency table: rows = pairs, columns = categories
    # Test if h-addition systematically changes category composition
    if len(pair_results) >= 2:
        # Aggregate: all base tokens vs all h-form tokens
        base_agg = Counter()
        h_agg = Counter()
        for pr in pair_results:
            base_agg += pr['base_counts']
            h_agg += pr['h_counts']

        observed = []
        cat_labels = []
        for cat in CATEGORIES:
            b_val = base_agg.get(cat, 0)
            h_val = h_agg.get(cat, 0)
            if b_val > 0 or h_val > 0:
                observed.append([b_val, h_val])
                cat_labels.append(cat)

        if len(observed) >= 2:
            chi2, p_val, dof, expected = stats.chi2_contingency(observed)
            print(f"  Aggregated chi2 = {chi2:.1f}, dof = {dof}, p = {p_val:.6f}")
            print(f"  Categories in test: {cat_labels}")

            # Show observed vs expected
            print(f"\n  {'Category':<15} {'Base obs':<12} {'Base exp':<12} {'h obs':<12} {'h exp':<12}")
            for i, cat in enumerate(cat_labels):
                print(f"  {cat:<15} {observed[i][0]:<12} {expected[i][0]:<12.1f} "
                      f"{observed[i][1]:<12} {expected[i][1]:<12.1f}")
        else:
            chi2, p_val = 0, 1.0
            print("  Insufficient categories for chi-square test")
    else:
        chi2, p_val = 0, 1.0
        print("  Insufficient pairs for chi-square test")

    # --- Part 6: Non-c control: does h-suffix transform non-c compounds similarly? ---
    print("\n--- Control: h-Suffix Effect on Non-c Compounds ---")

    non_c_h_pairs = []
    for mid in middle_cats:
        if len(mid) >= 2 and not mid.startswith('c') and not mid.endswith('h'):
            h_form = mid + 'h'
            if h_form in middle_cats:
                base_total = sum(middle_cats[mid].values())
                h_total = sum(middle_cats[h_form].values())
                if base_total >= 10 and h_total >= 10:
                    base_primary = middle_cats[mid].most_common(1)[0][0]
                    h_primary = middle_cats[h_form].most_common(1)[0][0]
                    non_c_h_pairs.append({
                        'base': mid, 'h_form': h_form,
                        'base_n': base_total, 'h_n': h_total,
                        'base_primary': base_primary,
                        'h_primary': h_primary,
                        'shifted': base_primary != h_primary
                    })

    non_c_shift = sum(1 for p in non_c_h_pairs if p['shifted'])
    non_c_total_ctrl = len(non_c_h_pairs)
    non_c_rate = non_c_shift / non_c_total_ctrl if non_c_total_ctrl > 0 else 0

    print(f"\nNon-c h-suffix pairs found (both N>=10): {non_c_total_ctrl}")
    print(f"Non-c shift rate: {non_c_shift}/{non_c_total_ctrl} = {non_c_rate:.1%}")

    if non_c_h_pairs:
        print(f"\n{'Base':<10} {'N':<6} {'Primary':<15} {'h-form':<10} {'N':<6} {'Primary':<15} {'Shifted?'}")
        print("-" * 80)
        for p in non_c_h_pairs[:15]:
            marker = "YES" if p['shifted'] else "no"
            print(f"{p['base']:<10} {p['base_n']:<6} {p['base_primary']:<15} "
                  f"{p['h_form']:<10} {p['h_n']:<6} {p['h_primary']:<15} {marker}")

    # --- Verdicts ---
    print("\n" + "=" * 80)
    print("VERDICTS")
    print("=" * 80)

    v1 = total_count >= 4 and shift_rate >= 0.75
    print(f"\n[{'PASS' if v1 else 'FAIL'}] >= 3/4 pairs show category shift: "
          f"{shift_count}/{total_count} = {shift_rate:.1%}")

    v2 = p_val < 0.05
    print(f"[{'PASS' if v2 else 'FAIL'}] Transformation is non-random (chi2 p < 0.05): p = {p_val:.6f}")

    # Bonus: c-specific vs general
    v3 = shift_rate > non_c_rate if non_c_total_ctrl > 0 else True
    print(f"[{'PASS' if v3 else 'FAIL'}] c+Xh shift rate > non-c+Xh shift rate: "
          f"{shift_rate:.1%} vs {non_c_rate:.1%}")

    overall = v1 and v2
    print(f"\n{'='*80}")
    print(f"OVERALL: {'PASS' if overall else 'FAIL'} (>= 3/4 shift AND non-random)")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
