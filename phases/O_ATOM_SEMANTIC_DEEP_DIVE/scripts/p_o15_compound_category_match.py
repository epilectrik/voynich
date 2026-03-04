#!/usr/bin/env python3
"""
P-O15: o-compound category determinism (ordnen readings)

If o = "ordnen" (arrange/prepare), specific o-compounds should match
ordnen-derived category predictions:

  ok -> CONTAINMENT (prepare heating = apparatus setup)
  ol -> STAGING (prepare state)
  ot -> OPERATION (prepare transfer)
  od -> MARKING (prepare marking)
  eol -> THERMAL (cool + prepare + state)

At least 4/5 should match in top-2 categories.

Non-o controls: ke, hy, dy, ed should match their known categories.
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

    # Define predictions
    # (middle, predicted_category, reading)
    predictions = [
        ('ok', 'CONTAINMENT', 'prepare-heating = apparatus setup'),
        ('ol', 'STAGING', 'prepare-state'),
        ('ot', 'OPERATION', 'prepare-transfer'),
        ('od', 'MARKING', 'prepare-marking'),
        ('eol', 'THERMAL', 'cool + prepare + state'),
    ]

    # Controls (non-o compounds)
    controls = [
        ('ke', 'THERMAL', 'heat + cool = thermal balance'),
        ('hy', 'MONITORING', 'monitor + end'),
        ('dy', 'CONTAINMENT', 'seal + end'),
        ('ed', 'FLOW', 'cool + seal'),
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
    print("P-O15: o-compound category determinism (ordnen readings)")
    print("=" * 70)
    print()

    # ---- Evaluate predictions ----
    print("-" * 70)
    print("PREDICTIONS (o-compounds)")
    print("-" * 70)
    print()

    pred_matches = 0
    pred_total = len(predictions)

    for mid, predicted_cat, reading in predictions:
        total = middle_totals.get(mid, 0)
        if total == 0:
            print(f"  {mid}: NOT FOUND in corpus")
            print(f"    Predicted: {predicted_cat} ({reading})")
            print(f"    Actual: N/A")
            print(f"    Verdict: SKIP (no data)")
            print()
            pred_total -= 1  # Don't count missing compounds
            continue

        # Direct classification
        direct_cat = cc.classify(mid)

        # Distribution from tokens
        cats_sorted = sorted(middle_cats[mid].items(), key=lambda x: -x[1])
        top1 = cats_sorted[0] if cats_sorted else (None, 0)
        top2 = cats_sorted[1] if len(cats_sorted) > 1 else (None, 0)
        top2_cats = {top1[0], top2[0]} - {None}

        match = predicted_cat in top2_cats or (direct_cat is not None and direct_cat == predicted_cat)
        if match:
            pred_matches += 1

        print(f"  {mid} (N={total}): Predicted = {predicted_cat} ({reading})")
        print(f"    Direct classify: {direct_cat}")
        print(f"    Top-1: {top1[0]} ({top1[1]}/{total} = {top1[1]/total*100:.1f}%)" if top1[0] else "    Top-1: N/A")
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
    print("CONTROLS (non-o compounds)")
    print("-" * 70)
    print()

    ctrl_matches = 0
    ctrl_total = len(controls)

    for mid, predicted_cat, reading in controls:
        total = middle_totals.get(mid, 0)
        if total == 0:
            print(f"  {mid}: NOT FOUND in corpus")
            ctrl_total -= 1
            continue

        direct_cat = cc.classify(mid)
        cats_sorted = sorted(middle_cats[mid].items(), key=lambda x: -x[1])
        top1 = cats_sorted[0] if cats_sorted else (None, 0)
        top2 = cats_sorted[1] if len(cats_sorted) > 1 else (None, 0)
        top2_cats = {top1[0], top2[0]} - {None}

        match = predicted_cat in top2_cats or (direct_cat is not None and direct_cat == predicted_cat)
        if match:
            ctrl_matches += 1

        print(f"  {mid} (N={total}): Predicted = {predicted_cat} ({reading})")
        print(f"    Direct classify: {direct_cat}")
        if top1[0]:
            print(f"    Top-1: {top1[0]} ({top1[1]}/{total} = {top1[1]/total*100:.1f}%)")
        if top2[0]:
            print(f"    Top-2: {top2[0]} ({top2[1]}/{total} = {top2[1]/total*100:.1f}%)")
        print(f"    Verdict: {'PASS' if match else 'FAIL'}")
        print()

    # ---- Additional: broader o-compound survey ----
    print("-" * 70)
    print("ADDITIONAL: All o-containing MIDDLEs by frequency (top 25)")
    print("-" * 70)
    print()

    o_middles = []
    for mid, total in middle_totals.items():
        if 'o' in mid and total >= 5:
            top_cat = max(middle_cats[mid], key=middle_cats[mid].get) if middle_cats[mid] else 'N/A'
            o_middles.append((mid, total, top_cat))

    o_middles.sort(key=lambda x: -x[1])

    print(f"{'MIDDLE':<12} {'Count':>6} {'TopCategory':>15}")
    print("-" * 38)
    for mid, total, top_cat in o_middles[:25]:
        o_pos = 'initial' if mid[0] == 'o' else ('terminal' if mid[-1] == 'o' else 'medial')
        print(f"  {mid:<10} {total:>6} {top_cat:>15}  ({o_pos})")

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-O15 o-compound category determinism (ordnen)")
    print("=" * 70)

    pass_pred = pred_total > 0 and pred_matches >= min(4, pred_total)
    pass_ctrl = ctrl_total > 0 and ctrl_matches >= max(1, ctrl_total // 2)

    results = [
        (f"Predictions: >= 4/{pred_total} match", pass_pred,
         f"{pred_matches}/{pred_total} matched"),
        (f"Controls: >= {max(1, ctrl_total//2)}/{ctrl_total} match", pass_ctrl,
         f"{ctrl_matches}/{ctrl_total} matched"),
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
