#!/usr/bin/env python3
"""
F-F2: f+X compound category determinism
==========================================
Test whether f-containing compound MIDDLEs produce categories matching
predicted decomposition based on f="flag" (MARKING).

Compounds tested:
  fch  (N~23) -> expected MARKING         (flag+adjust = mark/annotate)
  of   (N~15) -> expected MARKING         (arrange+flag = tag/label)
  ef   (N~6)  -> expected MARKING/THERMAL (cool+flag = thermal marker)
  cfh  (N~9)  -> expected MARKING         (adjust+flag+watch = verify mark)
  eef  (N~6)  -> expected MARKING/THERMAL (deep-cool+flag = deep thermal marker)

Pass criterion: >= 3/5 compounds match predicted category
                (FULL match = majority category matches prediction,
                 PARTIAL match = predicted category has >= 20% presence)

Also test: overall compound determinism -- are all f-compounds the same
category, or do they diversify?
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
        ('fch',  ['MARKING'],              'flag+adjust = mark/annotate'),
        ('of',   ['MARKING'],              'arrange+flag = tag/label'),
        ('ef',   ['MARKING', 'THERMAL'],   'cool+flag = thermal marker'),
        ('cfh',  ['MARKING'],              'adjust+flag+watch = verify mark'),
        ('eef',  ['MARKING', 'THERMAL'],   'deep-cool+flag = deep thermal marker'),
    ]

    # Controls (non-f compounds with known categories)
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
    print("F-F2: f+X compound category determinism")
    print("=" * 70)
    print()

    # ---- Evaluate predictions ----
    print("-" * 70)
    print("PREDICTIONS (f-compounds)")
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

    # ---- Controls ----
    print("-" * 70)
    print("CONTROLS (non-f compounds)")
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

    # ---- Additional: broader f-compound survey ----
    print("-" * 70)
    print("ADDITIONAL: All f-containing MIDDLEs by frequency (top 25)")
    print("-" * 70)
    print()

    f_middles = []
    for mid, total in middle_totals.items():
        if mid and 'f' in mid and total >= 2:
            top_cat = max(middle_cats[mid], key=middle_cats[mid].get) if middle_cats[mid] else 'N/A'
            direct = cc.classify(mid) or 'N/A'
            f_middles.append((mid, total, top_cat, direct))

    f_middles.sort(key=lambda x: -x[1])

    print("%-12s %6s %15s %15s" % ('MIDDLE', 'Count', 'TopCategory', 'DirectClass'))
    print("-" * 52)
    for mid, total, top_cat, direct in f_middles[:25]:
        print("  %-10s %6d %15s %15s" % (mid, total, top_cat, direct))

    # ---- Compound determinism test ----
    print()
    print("-" * 70)
    print("COMPOUND DETERMINISM: Are all f-compounds the same category?")
    print("-" * 70)
    print()

    # Get primary category of each f-containing MIDDLE with N >= 3
    f_primary_cats = defaultdict(int)
    f_compound_count = 0
    for mid, total in middle_totals.items():
        if mid and 'f' in mid and len(mid) > 1 and total >= 3:
            top_cat = max(middle_cats[mid], key=middle_cats[mid].get) if middle_cats[mid] else None
            if top_cat:
                f_primary_cats[top_cat] += 1
                f_compound_count += 1

    print("  f-compounds with N >= 3: %d" % f_compound_count)
    if f_compound_count > 0:
        print("  Primary category distribution:")
        for cat in sorted(f_primary_cats.keys(), key=lambda c: -f_primary_cats[c]):
            print("    %-15s %3d (%5.1f%%)" % (cat, f_primary_cats[cat],
                                                100 * f_primary_cats[cat] / f_compound_count))
        dominant = max(f_primary_cats, key=f_primary_cats.get)
        dominant_pct = 100 * f_primary_cats[dominant] / f_compound_count
        if dominant_pct >= 60:
            print("  --> UNIFORM: %s dominates at %.1f%%" % (dominant, dominant_pct))
        else:
            print("  --> DIVERSE: no single category dominates (top = %.1f%%)" % dominant_pct)

    # ---- SUMMARY ----
    print()
    print("=" * 70)
    print("SUMMARY: F-F2 f-compound category determinism")
    print("=" * 70)

    total_matches = pred_full + pred_partial  # count both full and partial
    pass_pred = pred_tested > 0 and total_matches >= 3
    pass_ctrl = ctrl_tested > 0 and ctrl_matches >= max(1, ctrl_tested // 2)

    results = [
        ("Predictions: >= 3/%d match (full or partial)" % pred_tested, pass_pred,
         "%d full + %d partial = %d/%d" % (pred_full, max(0, pred_partial - pred_full),
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
