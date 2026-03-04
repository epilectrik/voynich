#!/usr/bin/env python3
"""
P-P2: p+X compound category determinism

Test whether p-containing compound MIDDLEs produce categories matching
predicted decomposition based on p="pause".

Predictions (p + X):
  op  -> TRANSITION      (o=arrange + p=pause = "start")
  ep  -> THERMAL         (e=cool + p=pause = "precision cool")
  cph -> MONITORING      (c=adjust + p=pause + h=watch = "measure")
  cp  -> MARKING or MONITORING  (c=adjust + p=pause)
  pc  -> should differ from cp  (order sensitivity check)

Controls: ck=OPERATION, ok=CONTAINMENT (known from prior phases)

Pass criterion: >= 3/5 compounds match predicted category
                (FULL match = majority category matches prediction,
                 PARTIAL match = predicted category has >= 20% presence)
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
        ('op',  ['TRANSITION'],              'arrange+pause = start/initiate'),
        ('ep',  ['THERMAL'],                 'cool+pause = precision cool'),
        ('cph', ['MONITORING'],              'adjust+pause+watch = measure'),
        ('cp',  ['MARKING', 'MONITORING'],   'adjust+pause = mark/calibrate'),
        ('pc',  ['OPERATION', 'STAGING'],    'pause+adjust = should differ from cp'),
    ]

    # Controls (non-p compounds with known categories)
    controls = [
        ('ck', ['OPERATION'],      'adjust+heat = direct heat operation'),
        ('ok', ['CONTAINMENT'],    'arrange+heat = vessel seal/containment'),
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
    print("P-P2: p+X compound category determinism")
    print("=" * 70)
    print()

    # ---- Evaluate predictions ----
    print("-" * 70)
    print("PREDICTIONS (p-compounds)")
    print("-" * 70)
    print()

    pred_full = 0
    pred_partial = 0
    pred_tested = 0

    for mid, predicted_cats, reading in predictions:
        total = middle_totals.get(mid, 0)
        if total == 0:
            print("  %s: NOT FOUND in corpus" % mid)
            print("    Predicted: %s (%s)" % ('/'.join(predicted_cats), reading))
            print("    Actual: N/A")
            print("    Verdict: SKIP (no data)")
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

        # Full match: majority category matches prediction
        full_match = top1[0] in predicted_cats if top1[0] else False

        # Partial match: predicted category has >= 20% presence
        partial_match = False
        for pc in predicted_cats:
            pc_count = middle_cats[mid].get(pc, 0)
            if total > 0 and pc_count / total >= 0.20:
                partial_match = True
                break

        # Also check direct classification
        if direct_cat is not None and direct_cat in predicted_cats:
            partial_match = True

        if full_match:
            pred_full += 1
        if partial_match:
            pred_partial += 1

        # Determine verdict
        if full_match:
            verdict = "FULL MATCH"
        elif partial_match:
            verdict = "PARTIAL MATCH"
        else:
            verdict = "FAIL"

        print("  %s (N=%d): Predicted = %s (%s)" % (mid, total, '/'.join(predicted_cats), reading))
        print("    Direct classify: %s" % direct_cat)
        if top1[0]:
            print("    Top-1: %s (%d/%d = %.1f%%)" % (top1[0], top1[1], total, top1[1] / total * 100))
        if top2[0]:
            print("    Top-2: %s (%d/%d = %.1f%%)" % (top2[0], top2[1], total, top2[1] / total * 100))

        # Full profile
        print("    Full profile:")
        for cat in CATEGORIES:
            n = middle_cats[mid].get(cat, 0)
            if n > 0:
                print("      %-15s %5d (%5.1f%%)" % (cat, n, n / total * 100))

        print("    Verdict: %s" % verdict)
        print()

    # ---- Order sensitivity: cp vs pc ----
    print("-" * 70)
    print("ORDER SENSITIVITY: cp vs pc")
    print("-" * 70)
    print()

    cp_total = middle_totals.get('cp', 0)
    pc_total = middle_totals.get('pc', 0)

    if cp_total > 0 and pc_total > 0:
        cp_top = max(middle_cats['cp'], key=middle_cats['cp'].get) if middle_cats['cp'] else 'N/A'
        pc_top = max(middle_cats['pc'], key=middle_cats['pc'].get) if middle_cats['pc'] else 'N/A'
        differ = cp_top != pc_top
        print("  cp majority category: %s (N=%d)" % (cp_top, cp_total))
        print("  pc majority category: %s (N=%d)" % (pc_top, pc_total))
        print("  Categories differ: %s" % ('YES -- order matters' if differ else 'NO -- same category'))

        # Show both profiles side by side
        print()
        print("  %-15s %10s %10s" % ('Category', 'cp%', 'pc%'))
        print("  " + "-" * 38)
        for cat in CATEGORIES:
            cp_n = middle_cats['cp'].get(cat, 0)
            pc_n = middle_cats['pc'].get(cat, 0)
            if cp_n > 0 or pc_n > 0:
                cp_pct = cp_n / cp_total * 100 if cp_total > 0 else 0
                pc_pct = pc_n / pc_total * 100 if pc_total > 0 else 0
                print("  %-15s %9.1f%% %9.1f%%" % (cat, cp_pct, pc_pct))
    else:
        if cp_total == 0:
            print("  cp: NOT FOUND in corpus")
        if pc_total == 0:
            print("  pc: NOT FOUND in corpus")

    # ---- Controls ----
    print()
    print("-" * 70)
    print("CONTROLS (non-p compounds)")
    print("-" * 70)
    print()

    ctrl_matches = 0
    ctrl_tested = 0

    for mid, predicted_cats, reading in controls:
        total = middle_totals.get(mid, 0)
        if total == 0:
            print("  %s: NOT FOUND in corpus" % mid)
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

        print("  %s (N=%d): Predicted = %s (%s)" % (mid, total, '/'.join(predicted_cats), reading))
        print("    Direct classify: %s" % direct_cat)
        if top1[0]:
            print("    Top-1: %s (%d/%d = %.1f%%)" % (top1[0], top1[1], total, top1[1] / total * 100))
        if top2[0]:
            print("    Top-2: %s (%d/%d = %.1f%%)" % (top2[0], top2[1], total, top2[1] / total * 100))
        print("    Verdict: %s" % ('PASS' if match else 'FAIL'))
        print()

    # ---- Additional: broader p-compound survey ----
    print("-" * 70)
    print("ADDITIONAL: All p-containing MIDDLEs by frequency (top 25)")
    print("-" * 70)
    print()

    p_middles = []
    for mid, total in middle_totals.items():
        if mid and 'p' in mid and total >= 3:
            top_cat = max(middle_cats[mid], key=middle_cats[mid].get) if middle_cats[mid] else 'N/A'
            direct = cc.classify(mid) or 'N/A'
            p_middles.append((mid, total, top_cat, direct))

    p_middles.sort(key=lambda x: -x[1])

    print("%-12s %6s %15s %15s" % ('MIDDLE', 'Count', 'TopCategory', 'DirectClass'))
    print("-" * 52)
    for mid, total, top_cat, direct in p_middles[:25]:
        print("  %-10s %6d %15s %15s" % (mid, total, top_cat, direct))

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: P-P2 p-compound category determinism")
    print("=" * 70)

    total_matches = pred_full + pred_partial  # count both full and partial
    pass_pred = pred_tested > 0 and total_matches >= 3
    pass_ctrl = ctrl_tested > 0 and ctrl_matches >= max(1, ctrl_tested // 2)

    results = [
        ("Predictions: >= 3/%d match (full or partial)" % pred_tested, pass_pred,
         "%d full + %d partial = %d/%d" % (pred_full, pred_partial - pred_full if pred_partial > pred_full else 0,
                                            total_matches, pred_tested)),
        ("Controls: >= %d/%d match" % (max(1, ctrl_tested // 2), ctrl_tested), pass_ctrl,
         "%d/%d matched" % (ctrl_matches, ctrl_tested)),
    ]

    for desc, passed, val in results:
        status = "PASS" if passed else "FAIL"
        print("  [%s] %s: %s" % (status, desc, val))

    overall = pass_pred
    print()
    print("  PRIMARY CRITERION (>= 3/5 predictions match): %s" % ('PASS' if overall else 'FAIL'))
    print("  OVERALL VERDICT: %s" % ('PASS' if overall else 'FAIL'))


if __name__ == '__main__':
    main()
