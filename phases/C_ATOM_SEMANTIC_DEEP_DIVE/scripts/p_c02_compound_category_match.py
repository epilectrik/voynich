#!/usr/bin/env python3
"""
P-C2: c+X compound category determinism

Test whether specific c-compounds match predicted categories based on
compositional reading c="adjust" + second atom gloss.

Predictions (c="adjust" + X):
  ck  -> THERMAL or CONTAINMENT  (adjust+heat = direct heat control)
  ct  -> MONITORING              (adjust+transfer = quality control)
  cth -> MARKING                 (adjust+transfer+watch = hazard marking)
  cph -> MONITORING              (adjust+pause+watch = measurement)
  cfh -> MARKING                 (adjust+flag+watch = flagged monitoring)

Controls (non-c compounds): ke, hy, dy, ed

Pass criterion: >= 4/5 compounds match predicted category in top-2
                categories by token count.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
                  'TRANSITION', 'MARKING', 'MONITORING']

    # Define predictions: (middle, list_of_acceptable_categories, reading)
    predictions = [
        ('ck',  ['THERMAL', 'CONTAINMENT'], 'adjust+heat = direct heat control'),
        ('ct',  ['MONITORING'],              'adjust+transfer = quality control'),
        ('cth', ['MARKING'],                 'adjust+transfer+watch = hazard marking'),
        ('cph', ['MONITORING'],              'adjust+pause+watch = measurement'),
        ('cfh', ['MARKING'],                 'adjust+flag+watch = flagged monitoring'),
    ]

    # Controls (non-c compounds with known categories)
    controls = [
        ('ke', ['THERMAL'],      'heat+cool = thermal balance'),
        ('hy', ['MONITORING'],   'watch+end = confirm'),
        ('dy', ['CONTAINMENT'],  'seal+end = sealing'),
        ('ed', ['FLOW'],         'cool+seal = flow control'),
    ]

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

    print("=" * 70)
    print("P-C2: c+X compound category determinism")
    print("=" * 70)
    print()

    # ---- Evaluate predictions ----
    print("-" * 70)
    print("PREDICTIONS (c-compounds)")
    print("-" * 70)
    print()

    pred_matches = 0
    pred_tested = 0

    for mid, predicted_cats, reading in predictions:
        total = middle_totals.get(mid, 0)
        if total == 0:
            print(f"  {mid}: NOT FOUND in corpus")
            print(f"    Predicted: {'/'.join(predicted_cats)} ({reading})")
            print(f"    Actual: N/A")
            print(f"    Verdict: SKIP (no data)")
            print()
            continue

        pred_tested += 1

        # Direct classification
        direct_cat = cc.classify(mid)

        # Distribution from tokens
        cats_sorted = sorted(middle_cats[mid].items(), key=lambda x: -x[1])
        top1 = cats_sorted[0] if cats_sorted else (None, 0)
        top2 = cats_sorted[1] if len(cats_sorted) > 1 else (None, 0)
        top2_cats = {top1[0], top2[0]} - {None}

        # Match if any predicted category is in top-2 OR matches direct classification
        match = bool(set(predicted_cats) & top2_cats) or (
            direct_cat is not None and direct_cat in predicted_cats
        )
        if match:
            pred_matches += 1

        print(f"  {mid} (N={total}): Predicted = {'/'.join(predicted_cats)} ({reading})")
        print(f"    Direct classify: {direct_cat}")
        if top1[0]:
            print(f"    Top-1: {top1[0]} ({top1[1]}/{total} = {top1[1]/total*100:.1f}%)")
        if top2[0]:
            print(f"    Top-2: {top2[0]} ({top2[1]}/{total} = {top2[1]/total*100:.1f}%)")

        # Full profile
        print(f"    Full profile:")
        for cat in CATEGORIES:
            n = middle_cats[mid].get(cat, 0)
            if n > 0:
                print(f"      {cat:<15} {n:>5} ({n/total*100:>5.1f}%)")

        print(f"    In top-2? {'YES' if match else 'NO'}")
        print(f"    Verdict: {'PASS' if match else 'FAIL'}")
        print()

    # ---- Controls ----
    print("-" * 70)
    print("CONTROLS (non-c compounds)")
    print("-" * 70)
    print()

    ctrl_matches = 0
    ctrl_tested = 0

    for mid, predicted_cats, reading in controls:
        total = middle_totals.get(mid, 0)
        if total == 0:
            print(f"  {mid}: NOT FOUND in corpus")
            ctrl_tested += 0  # Don't count missing
            continue

        ctrl_tested += 1

        direct_cat = cc.classify(mid)
        cats_sorted = sorted(middle_cats[mid].items(), key=lambda x: -x[1])
        top1 = cats_sorted[0] if cats_sorted else (None, 0)
        top2 = cats_sorted[1] if len(cats_sorted) > 1 else (None, 0)
        top2_cats = {top1[0], top2[0]} - {None}

        match = bool(set(predicted_cats) & top2_cats) or (
            direct_cat is not None and direct_cat in predicted_cats
        )
        if match:
            ctrl_matches += 1

        print(f"  {mid} (N={total}): Predicted = {'/'.join(predicted_cats)} ({reading})")
        print(f"    Direct classify: {direct_cat}")
        if top1[0]:
            print(f"    Top-1: {top1[0]} ({top1[1]}/{total} = {top1[1]/total*100:.1f}%)")
        if top2[0]:
            print(f"    Top-2: {top2[0]} ({top2[1]}/{total} = {top2[1]/total*100:.1f}%)")
        print(f"    Verdict: {'PASS' if match else 'FAIL'}")
        print()

    # ---- Additional: broader c-compound survey ----
    print("-" * 70)
    print("ADDITIONAL: All c-initial MIDDLEs by frequency (top 25)")
    print("-" * 70)
    print()

    c_middles = []
    for mid, total in middle_totals.items():
        if mid and mid[0] == 'c' and total >= 3:
            top_cat = max(middle_cats[mid], key=middle_cats[mid].get) if middle_cats[mid] else 'N/A'
            direct = cc.classify(mid) or 'N/A'
            c_middles.append((mid, total, top_cat, direct))

    c_middles.sort(key=lambda x: -x[1])

    print(f"{'MIDDLE':<12} {'Count':>6} {'TopCategory':>15} {'DirectClass':>15}")
    print("-" * 52)
    for mid, total, top_cat, direct in c_middles[:25]:
        print(f"  {mid:<10} {total:>6} {top_cat:>15} {direct:>15}")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-C2 c-compound category determinism")
    print("=" * 70)

    pass_pred = pred_tested > 0 and pred_matches >= min(4, pred_tested)
    pass_ctrl = ctrl_tested > 0 and ctrl_matches >= max(1, ctrl_tested // 2)

    results = [
        (f"Predictions: >= 4/{pred_tested} match top-2", pass_pred,
         f"{pred_matches}/{pred_tested} matched"),
        (f"Controls: >= {max(1, ctrl_tested//2)}/{ctrl_tested} match", pass_ctrl,
         f"{ctrl_matches}/{ctrl_tested} matched"),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {desc}: {val}")

    overall = pass_pred
    print()
    print(f"  PRIMARY CRITERION (>= 4/5 predictions match top-2): {'PASS' if overall else 'FAIL'}")
    print(f"  OVERALL VERDICT: {'PASS' if overall else 'FAIL'}")


if __name__ == '__main__':
    main()
