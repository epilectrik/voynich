#!/usr/bin/env python3
"""
SM-6: Does s make compounds more STAGING-enriched than their non-s equivalents?

s itself is 64.6% FQ at macro-state level, with its category profile being
STAGING-dominant (C1391). Since s-compounds are mostly HT/UN (unclassifiable
by the 49-class grammar), we use CategoryClassifier which works on ALL MIDDLEs
via atom-level voting.

Pairs tested:
  1. es MIDDLEs vs e-initial MIDDLEs (not es-initial)
  2. os MIDDLEs vs o-initial MIDDLEs (not os-initial)
  3. cs MIDDLEs vs c-initial MIDDLEs (not cs-initial)
  4. ksh MIDDLEs vs kh MIDDLEs (not ksh-initial)
  5. lsh MIDDLEs vs lh MIDDLEs (not lsh-initial)

s = STAGING/OPERATION per C1391.
Prediction: s-compounds have higher STAGING% than non-s equivalents.
Pass: >= 3/5 s-compounds have higher STAGING% than non-s equivalent.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    print("=" * 75)
    print("SM-6: STAGING amplification by s-modification")
    print("=" * 75)
    print()
    print("Note: s-compounds are mostly HT/UN (unclassifiable by 49-class grammar).")
    print("Using CategoryClassifier (atom-level voting) which classifies ALL MIDDLEs.")

    # --- Collect category distributions keyed by MIDDLE-initial pattern ---
    group_cat = defaultdict(Counter)
    group_total = defaultdict(int)
    global_cat = Counter()
    global_total = 0

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

        global_cat[cat] += 1
        global_total += 1

        # Pair 1: es vs e (not es)
        if mid.startswith('es'):
            group_cat['es'][cat] += 1
            group_total['es'] += 1
        elif mid.startswith('e') and not mid.startswith('es'):
            group_cat['e_not_es'][cat] += 1
            group_total['e_not_es'] += 1

        # Pair 2: os vs o (not os)
        if mid.startswith('os'):
            group_cat['os'][cat] += 1
            group_total['os'] += 1
        elif mid.startswith('o') and not mid.startswith('os'):
            group_cat['o_not_os'][cat] += 1
            group_total['o_not_os'] += 1

        # Pair 3: cs vs c (not cs)
        if mid.startswith('cs'):
            group_cat['cs'][cat] += 1
            group_total['cs'] += 1
        elif mid.startswith('c') and not mid.startswith('cs'):
            group_cat['c_not_cs'][cat] += 1
            group_total['c_not_cs'] += 1

        # Pair 4: ksh vs kh (not ksh)
        if len(mid) >= 3 and mid[:3] == 'ksh':
            group_cat['ksh'][cat] += 1
            group_total['ksh'] += 1
        elif len(mid) >= 2 and mid[:2] == 'kh' and not (len(mid) >= 3 and mid[:3] == 'ksh'):
            group_cat['kh_not_ksh'][cat] += 1
            group_total['kh_not_ksh'] += 1

        # Pair 5: lsh vs lh (not lsh)
        if len(mid) >= 3 and mid[:3] == 'lsh':
            group_cat['lsh'][cat] += 1
            group_total['lsh'] += 1
        elif len(mid) >= 2 and mid[:2] == 'lh' and not (len(mid) >= 3 and mid[:3] == 'lsh'):
            group_cat['lh_not_lsh'][cat] += 1
            group_total['lh_not_lsh'] += 1

    global_staging_pct = 100 * global_cat.get('STAGING', 0) / global_total if global_total > 0 else 0
    print()
    print("Global baseline: STAGING = %.1f%% of %d classified tokens" % (global_staging_pct, global_total))

    # --- Helper to print group profile ---
    def print_profile(label, grp_key):
        total = group_total.get(grp_key, 0)
        if total == 0:
            print("  %-25s  N=0 (no tokens)" % label)
            return 0.0, total
        staging_n = group_cat[grp_key].get('STAGING', 0)
        staging_pct = 100 * staging_n / total

        parts = []
        for cat in CATEGORIES:
            n = group_cat[grp_key].get(cat, 0)
            pct = 100 * n / total
            parts.append("%s=%.1f%%" % (cat[:4], pct))
        profile_str = "  ".join(parts)

        print("  %-25s  N=%-5d  STAGING=%.1f%%  [%s]" % (label, total, staging_pct, profile_str))
        return staging_pct, total

    # --- Evaluate each pair ---
    pairs = [
        ("Pair 1: es vs e(not es)", "es", "e_not_es"),
        ("Pair 2: os vs o(not os)", "os", "o_not_os"),
        ("Pair 3: cs vs c(not cs)", "cs", "c_not_cs"),
        ("Pair 4: ksh vs kh(not ksh)", "ksh", "kh_not_ksh"),
        ("Pair 5: lsh vs lh(not lsh)", "lsh", "lh_not_lsh"),
    ]

    print()
    results = []

    for label, s_key, base_key in pairs:
        print("-" * 75)
        print(label)
        print("-" * 75)

        s_staging, s_n = print_profile("s-compound (%s)" % s_key, s_key)
        base_staging, base_n = print_profile("base (%s)" % base_key, base_key)

        min_n = 3  # Relaxed threshold for rare compounds
        if s_n < min_n:
            print("  ** INCONCLUSIVE (s-compound N < %d)" % min_n)
            results.append((label, None, s_staging, base_staging, s_n, base_n))
        elif base_n < min_n:
            print("  ** INCONCLUSIVE (base N < %d)" % min_n)
            results.append((label, None, s_staging, base_staging, s_n, base_n))
        else:
            delta = s_staging - base_staging
            direction = "HIGHER" if delta > 0 else "LOWER" if delta < 0 else "EQUAL"
            passed = delta > 0
            print("  Delta (s - base): %+.1f pp  -->  s-compound STAGING is %s" % (delta, direction))
            print("  %s" % ("PASS (s-compound has higher STAGING%%)" if passed else "FAIL"))
            results.append((label, passed, s_staging, base_staging, s_n, base_n))
        print()

    # --- VERDICT ---
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    print()

    testable = [r for r in results if r[1] is not None]
    pass_count = sum(1 for r in testable if r[1])
    inconclusive = len(results) - len(testable)

    print("%-35s %10s %10s %8s %6s %8s" % ("Pair", "s-STAG%", "base-STAG%", "Delta", "s-N", "Verdict"))
    print("-" * 85)
    for label, passed, s_stag, base_stag, s_n, base_n in results:
        delta = s_stag - base_stag
        if passed is None:
            verdict = "INCON"
        elif passed:
            verdict = "PASS"
        else:
            verdict = "FAIL"
        print("%-35s %9.1f%% %9.1f%% %+7.1fpp %6d   %s" % (
            label, s_stag, base_stag, delta, s_n, verdict))

    print()
    print("Testable pairs:         %d / %d" % (len(testable), len(results)))
    print("Inconclusive:           %d" % inconclusive)
    print("s-compound > base:      %d / %d" % (pass_count, len(testable)))
    print("Threshold:              >= 3 / 5")
    print()

    overall = pass_count >= 3
    print("SM-6 OVERALL: %s" % ("PASS" if overall else "FAIL"))
    if overall:
        print("  s-modification amplifies STAGING rate in >= 3/5 compound families.")
    else:
        if len(testable) < 3:
            print("  Insufficient testable pairs (%d/5). s-compounds are rare." % len(testable))
            print("  Consider this test UNDERPOWERED rather than definitively failed.")
        else:
            print("  s-modification does NOT consistently amplify STAGING rate.")


if __name__ == '__main__':
    main()
