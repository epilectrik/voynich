"""
P-C18: Compositional reading convergence -- c-compound readings match glossed dictionary
==========================================================================================
Test whether the compositional decomposition c(adjust)+X matches the independently
glossed compound meanings from the GLOSSING dictionary.

For each glossed compound, check if the CategoryClassifier output is consistent with
the expected semantic field of the gloss. This is DIFFERENT from P-C2 because P-C2
tested PREDICTED categories based on the "adjust" hypothesis, while this tests against
INDEPENDENTLY GLOSSED meanings.

Gloss-to-category mappings:
  ck  = "direct heat"      -> THERMAL or OPERATION
  ckh = "firm"             -> CONTAINMENT
  ct  = "control"          -> MONITORING
  cth = "hazard"           -> MARKING
  cph = "measure"          -> MONITORING
  kc  = "intense heat-seal"-> THERMAL or CONTAINMENT

Pass: >= 5/6 gloss-to-category matches
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']

# Independently glossed compounds and their expected categories
# Each entry: (compound_middle, gloss, acceptable_categories, compositional_reading)
GLOSSED_COMPOUNDS = [
    ('ck',  'direct heat',       ['THERMAL', 'OPERATION'],
     'c(adjust) + k(heat) = adjust the heat -> direct heat control'),
    ('ckh', 'firm',              ['CONTAINMENT'],
     'c(adjust) + k(heat) + h(watch) = adjust-heat-monitor -> firm/stable'),
    ('ct',  'control',           ['MONITORING'],
     'c(adjust) + t(transfer) = adjust the transfer -> control'),
    ('cth', 'hazard',            ['MARKING'],
     'c(adjust) + t(transfer) + h(watch) = adjust-transfer-monitor -> hazard'),
    ('cph', 'measure',           ['MONITORING'],
     'c(adjust) + p(pause) + h(watch) = adjust-pause-monitor -> measure'),
    ('kc',  'intense heat-seal', ['THERMAL', 'CONTAINMENT'],
     'k(heat) + c(adjust) = heat adjustment -> intense heat-seal'),
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
    print("P-C18: Compositional reading convergence")
    print("        c-compound readings vs glossed dictionary")
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
            detailed_results.append((mid, gloss, 'INCONCLUSIVE', None, None))
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
            print(f"{cat}={cnt}({cnt/len(cats):.1%}) ", end='')
        print()
        print(f"  Expected category presence: {expected_presence:.1%}")

        if match:
            verdict = 'FULL'
            matches += 1
            print(f"  Match: FULL (majority {majority_cat} in expected {expected_cats})")
        elif expected_presence >= 0.20:
            verdict = 'PARTIAL'
            matches += 1  # Partial counts toward the >= 5/6 threshold
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
    print(f"{'Compound':<10} {'Gloss':<20} {'Majority':<14} {'Expected':<25} {'Match'}")
    print("-" * 75)
    for mid, gloss, verdict, maj, exp in detailed_results:
        exp_str = ', '.join(exp) if exp else 'N/A'
        maj_str = maj if maj else 'N/A'
        print(f"{mid:<10} {gloss:<20} {maj_str:<14} {exp_str:<25} {verdict}")

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

    # Order sensitivity check
    print("=" * 72)
    print("ORDER SENSITIVITY CHECK")
    print("=" * 72)
    print()
    # Compare ck vs kc
    ck_cats = compound_cats.get('ck', [])
    kc_cats = compound_cats.get('kc', [])
    if ck_cats and kc_cats:
        ck_majority = Counter(ck_cats).most_common(1)[0][0]
        kc_majority = Counter(kc_cats).most_common(1)[0][0]
        order_diff = ck_majority != kc_majority
        print(f"  ck majority: {ck_majority} (N={len(ck_cats)})")
        print(f"  kc majority: {kc_majority} (N={len(kc_cats)})")
        print(f"  Different categories: {'YES' if order_diff else 'NO'}")
        print(f"  Consistent with order sensitivity: {'YES' if order_diff else 'NO'}")
    else:
        print(f"  Cannot compare: ck has {len(ck_cats)} tokens, kc has {len(kc_cats)} tokens")

    # Compare ct vs tc if available
    ct_cats = compound_cats.get('ct', [])
    tc_cats = compound_cats.get('tc', [])
    print()
    if ct_cats:
        ct_majority = Counter(ct_cats).most_common(1)[0][0]
        print(f"  ct majority: {ct_majority} (N={len(ct_cats)})")
    if tc_cats:
        tc_majority = Counter(tc_cats).most_common(1)[0][0]
        print(f"  tc majority: {tc_majority} (N={len(tc_cats)})")
        if ct_cats:
            order_diff_2 = ct_majority != tc_majority
            print(f"  Different categories: {'YES' if order_diff_2 else 'NO'}")
    else:
        print(f"  tc: not found or no classified tokens")

    print()

    # Overall verdict
    passed = matches >= 5
    print("=" * 72)
    print(f"OVERALL VERDICT: {'PASS' if passed else 'FAIL'} "
          f"({matches}/6 gloss-to-category matches, threshold >= 5/6)")
    print("=" * 72)


if __name__ == '__main__':
    main()
