"""
P-P12: Compositional reading convergence -- DECISIVE
=====================================================
THE decisive test. Check whether independently glossed p-compounds match
CategoryClassifier output.

Glossed compounds and expected categories:
1. op  = "start"         -> o(arrange)+p(pause) -> STAGING or TRANSITION
2. ep  = "precision cool"-> e(cool)+p(pause)    -> THERMAL or CONTAINMENT
3. cph = "measure"       -> c(adjust)+p(pause)+h(watch) -> MONITORING
4. cp  = (unglossed)     -> c(adjust)+p(pause)  -> MARKING or OPERATION

Pass: >= 3/4 gloss-to-category matches (FULL or PARTIAL)
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']

# Glossed compounds: (compound_middle, gloss, acceptable_categories, compositional_reading)
GLOSSED_COMPOUNDS = [
    ('op',  'start',
     ['STAGING', 'TRANSITION'],
     'o(arrange) + p(pause) = arrange a pause -> initiate/start -> STAGING/TRANSITION'),
    ('ep',  'precision cool',
     ['THERMAL', 'CONTAINMENT'],
     'e(cool) + p(pause) = cool pause -> controlled cooling -> THERMAL/CONTAINMENT'),
    ('cph', 'measure',
     ['MONITORING'],
     'c(adjust) + p(pause) + h(watch) = adjust-pause-monitor -> measure -> MONITORING'),
    ('cp',  '(unglossed: predicted MARKING)',
     ['MARKING', 'OPERATION'],
     'c(adjust) + p(pause) = adjust-pause -> calibrated pause -> MARKING/OPERATION'),
]


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Collect category distributions for each target compound
    compound_cats = defaultdict(list)
    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle
        if not mid:
            continue
        cat = cc.classify(mid)
        if cat == 'UNK':
            continue
        compound_cats[mid].append(cat)

    print("=" * 72)
    print("P-P12: Compositional reading convergence -- DECISIVE")
    print("        p-compound readings vs CategoryClassifier")
    print("=" * 72)
    print()

    matches = 0
    total = 0
    detailed_results = []

    for mid, gloss, expected_cats, reading in GLOSSED_COMPOUNDS:
        total += 1
        cats = compound_cats.get(mid, [])

        print(f"Compound: {mid}")
        print(f"  Gloss: \"{gloss}\"")
        print(f"  Compositional: {reading}")
        print(f"  Expected categories: {expected_cats}")

        if not cats:
            print(f"  Observed: NO TOKENS FOUND")
            print(f"  Match: INCONCLUSIVE (no data)")
            print()
            detailed_results.append((mid, gloss, 'INCONCLUSIVE', None, expected_cats))
            continue

        cat_counts = Counter(cats)
        majority_cat = cat_counts.most_common(1)[0][0]
        majority_frac = cat_counts[majority_cat] / len(cats)

        # Check if majority category is in expected list
        match = majority_cat in expected_cats

        # Also check if ANY expected category has substantial presence (>= 20%)
        expected_presence = sum(cat_counts.get(ec, 0) for ec in expected_cats) / len(cats)

        print(f"  Observed: N={len(cats)}, majority={majority_cat} ({majority_frac:.1%})")
        print(f"  Distribution: ", end='')
        for cat, cnt in cat_counts.most_common():
            print(f"{cat}={cnt}({cnt / len(cats):.1%}) ", end='')
        print()
        print(f"  Expected category presence: {expected_presence:.1%}")

        if match:
            verdict = 'FULL'
            matches += 1
            print(f"  Match: FULL (majority {majority_cat} in expected {expected_cats})")
        elif expected_presence >= 0.20:
            verdict = 'PARTIAL'
            matches += 1
            print(f"  Match: PARTIAL (expected cats at {expected_presence:.1%}, "
                  f"majority is {majority_cat})")
        else:
            verdict = 'NONE'
            print(f"  Match: NONE (majority {majority_cat} not in {expected_cats}, "
                  f"expected presence only {expected_presence:.1%})")

        detailed_results.append((mid, gloss, verdict, majority_cat, expected_cats))
        print()

    # Summary table
    print("=" * 72)
    print("SUMMARY TABLE")
    print("=" * 72)
    print()
    print(f"{'Compound':<10} {'Gloss':<25} {'Majority':<14} {'Expected':<25} {'Match'}")
    print("-" * 80)
    for mid, gloss, verdict, maj, exp in detailed_results:
        exp_str = ', '.join(exp) if exp else 'N/A'
        maj_str = maj if maj else 'N/A'
        # Truncate long glosses
        gloss_short = gloss[:23] if len(gloss) > 23 else gloss
        print(f"{mid:<10} {gloss_short:<25} {maj_str:<14} {exp_str:<25} {verdict}")

    print()

    # Count verdicts
    n_full = sum(1 for _, _, v, _, _ in detailed_results if v == 'FULL')
    n_partial = sum(1 for _, _, v, _, _ in detailed_results if v == 'PARTIAL')
    n_none = sum(1 for _, _, v, _, _ in detailed_results if v == 'NONE')
    n_incon = sum(1 for _, _, v, _, _ in detailed_results if v == 'INCONCLUSIVE')

    print(f"FULL matches:    {n_full}/{total}")
    print(f"PARTIAL matches: {n_partial}/{total}")
    print(f"NO match:        {n_none}/{total}")
    print(f"Inconclusive:    {n_incon}/{total}")
    print(f"Total matching (FULL+PARTIAL): {matches}/{total}")
    print()

    # Order sensitivity check: cp vs pc
    print("=" * 72)
    print("ORDER SENSITIVITY CHECK")
    print("=" * 72)
    print()

    cp_cats = compound_cats.get('cp', [])
    pc_cats = compound_cats.get('pc', [])
    if cp_cats and pc_cats:
        cp_majority = Counter(cp_cats).most_common(1)[0][0]
        pc_majority = Counter(pc_cats).most_common(1)[0][0]
        order_diff = cp_majority != pc_majority
        print(f"  cp majority: {cp_majority} (N={len(cp_cats)})")
        print(f"  pc majority: {pc_majority} (N={len(pc_cats)})")
        print(f"  Different categories: {'YES' if order_diff else 'NO'}")
        print(f"  Consistent with order sensitivity: {'YES' if order_diff else 'NO'}")
    elif cp_cats:
        cp_majority = Counter(cp_cats).most_common(1)[0][0]
        print(f"  cp majority: {cp_majority} (N={len(cp_cats)})")
        print(f"  pc: not found ({len(pc_cats)} tokens)")
        print(f"  Cannot compare order sensitivity")
    else:
        print(f"  cp: {len(cp_cats)} tokens, pc: {len(pc_cats)} tokens")
        print(f"  Cannot compare order sensitivity")

    # Also compare op vs po
    print()
    op_cats = compound_cats.get('op', [])
    po_cats = compound_cats.get('po', [])
    if op_cats and po_cats:
        op_majority = Counter(op_cats).most_common(1)[0][0]
        po_majority = Counter(po_cats).most_common(1)[0][0]
        order_diff = op_majority != po_majority
        print(f"  op majority: {op_majority} (N={len(op_cats)})")
        print(f"  po majority: {po_majority} (N={len(po_cats)})")
        print(f"  Different categories: {'YES' if order_diff else 'NO'}")
    elif op_cats:
        op_majority = Counter(op_cats).most_common(1)[0][0]
        print(f"  op majority: {op_majority} (N={len(op_cats)})")
        print(f"  po: not found ({len(po_cats)} tokens)")
    else:
        print(f"  op: {len(op_cats)} tokens, po: {len(po_cats)} tokens")

    # Compare ep vs pe
    print()
    ep_cats = compound_cats.get('ep', [])
    pe_cats = compound_cats.get('pe', [])
    if ep_cats and pe_cats:
        ep_majority = Counter(ep_cats).most_common(1)[0][0]
        pe_majority = Counter(pe_cats).most_common(1)[0][0]
        order_diff = ep_majority != pe_majority
        print(f"  ep majority: {ep_majority} (N={len(ep_cats)})")
        print(f"  pe majority: {pe_majority} (N={len(pe_cats)})")
        print(f"  Different categories: {'YES' if order_diff else 'NO'}")
    elif ep_cats:
        ep_majority = Counter(ep_cats).most_common(1)[0][0]
        print(f"  ep majority: {ep_majority} (N={len(ep_cats)})")
        print(f"  pe: not found ({len(pe_cats)} tokens)")
    else:
        print(f"  ep: {len(ep_cats)} tokens, pe: {len(pe_cats)} tokens")

    print()

    # Overall verdict
    passed = matches >= 3
    print("=" * 72)
    print(f"OVERALL VERDICT: {'PASS' if passed else 'FAIL'} "
          f"({matches}/{total} gloss-to-category matches, threshold >= 3/4)")
    print("=" * 72)

    if passed:
        print("  Compositional readings of p-compounds converge with CategoryClassifier.")
        print("  p = 'pause' gloss is structurally validated at compound level.")
    else:
        print("  Compositional readings do NOT converge with CategoryClassifier.")
        print("  p = 'pause' may need revision or refinement.")


if __name__ == '__main__':
    main()
