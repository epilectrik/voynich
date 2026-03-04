"""
P-C19: c-compound folio coverage breadth
==========================================
Test whether c-compounds appear broadly across folios (not localized to a few).

If c is a genuine semantic modifier, its compounds should appear wherever those
operations are needed -- broadly distributed. If they're localized, c might be
an artifact of a few folios.

Predictions:
- Major c-compounds (ck, ckh, ct) each appear in >= 30 folios (>= 36% coverage)
- c-compound mean folio coverage >= mean of frequency-matched non-c compounds
- No c-compound is concentrated in < 5 folios (no localization)

Pass: major c-compounds >= 30 folios AND no localization (min >= 5 folios)
"""

import sys
from pathlib import Path
from collections import defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']

# Target c-compounds
C_COMPOUNDS = ['ck', 'ckh', 'ct', 'cth', 'cph', 'cfh']
MAJOR_C_COMPOUNDS = ['ck', 'ckh', 'ct']  # Expected high-frequency ones


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # Collect per-MIDDLE folio sets and token counts
    middle_folios = defaultdict(set)
    middle_counts = defaultdict(int)
    all_b_folios = set()

    for token in tx.currier_b():
        w = token.word
        if not w or '*' in w:
            continue
        folio = token.folio
        all_b_folios.add(folio)

        m = morph.extract(w)
        mid = m.middle
        if not mid or len(mid) < 2:
            continue

        middle_folios[mid].add(folio)
        middle_counts[mid] += 1

    total_folios = len(all_b_folios)

    print("=" * 72)
    print("P-C19: c-compound folio coverage breadth")
    print("=" * 72)
    print()
    print(f"Total Currier B folios: {total_folios}")
    print()

    # Report c-compound coverage
    print("C-COMPOUND FOLIO COVERAGE")
    print("-" * 60)
    print(f"{'Compound':<12} {'Tokens':<8} {'Folios':<8} {'Coverage':<10} {'Status'}")
    print("-" * 60)

    c_compound_stats = {}
    for mid in C_COMPOUNDS:
        n_tok = middle_counts.get(mid, 0)
        n_fol = len(middle_folios.get(mid, set()))
        coverage = n_fol / total_folios if total_folios > 0 else 0

        is_major = mid in MAJOR_C_COMPOUNDS
        status = ""
        if is_major:
            status = "PASS" if n_fol >= 30 else "FAIL"
            status += " (major)"
        else:
            status = "OK" if n_fol >= 5 else "LOCALIZED"

        c_compound_stats[mid] = {
            'tokens': n_tok,
            'folios': n_fol,
            'coverage': coverage,
        }

        print(f"{mid:<12} {n_tok:<8} {n_fol:<8} {coverage:<10.1%} {status}")

    print()

    # Build frequency-matched controls
    # For each c-compound, find non-c compounds with similar token counts
    # and compare their folio coverage
    print("=" * 72)
    print("FREQUENCY-MATCHED CONTROL COMPARISON")
    print("=" * 72)
    print()

    # Get all non-c compound MIDDLEs (multi-char, first char != 'c')
    non_c_compounds = {}
    for mid, count in middle_counts.items():
        if len(mid) >= 2 and mid[0] != 'c':
            non_c_compounds[mid] = {
                'tokens': count,
                'folios': len(middle_folios.get(mid, set())),
            }

    c_coverages = []
    ctrl_coverages_all = []

    for c_mid in C_COMPOUNDS:
        c_tok = middle_counts.get(c_mid, 0)
        c_fol = len(middle_folios.get(c_mid, set()))

        if c_tok == 0:
            print(f"{c_mid}: no tokens, skipping control comparison")
            continue

        # Find non-c compounds within +/- 50% token count (or at least +/- 5)
        margin = max(5, int(c_tok * 0.5))
        lo = c_tok - margin
        hi = c_tok + margin

        controls = []
        for mid, data in non_c_compounds.items():
            if lo <= data['tokens'] <= hi:
                controls.append((mid, data['tokens'], data['folios']))

        if not controls:
            # Widen to +/- 100%
            lo2 = max(1, c_tok - int(c_tok * 1.0))
            hi2 = c_tok + int(c_tok * 1.0)
            for mid, data in non_c_compounds.items():
                if lo2 <= data['tokens'] <= hi2:
                    controls.append((mid, data['tokens'], data['folios']))

        ctrl_folios = [c[2] for c in controls]

        c_coverages.append(c_fol)

        if ctrl_folios:
            ctrl_mean = statistics.mean(ctrl_folios)
            ctrl_median = statistics.median(ctrl_folios)
            ctrl_coverages_all.extend(ctrl_folios)
            ratio = c_fol / ctrl_mean if ctrl_mean > 0 else float('inf')

            print(f"{c_mid} (N={c_tok}, folios={c_fol}):")
            print(f"  Controls: {len(controls)} compounds with "
                  f"{lo}-{hi} tokens")
            print(f"  Control folio mean: {ctrl_mean:.1f}, median: {ctrl_median:.1f}")
            print(f"  c-compound / control ratio: {ratio:.2f}x")

            # Show top 5 controls
            controls_sorted = sorted(controls, key=lambda c: -c[2])[:5]
            print(f"  Top controls: ", end='')
            for cm, ct, cf in controls_sorted:
                print(f"{cm}(N={ct},f={cf}) ", end='')
            print()
        else:
            print(f"{c_mid} (N={c_tok}, folios={c_fol}): no frequency-matched controls found")

        print()

    # Aggregate comparison
    print("=" * 72)
    print("AGGREGATE COMPARISON")
    print("=" * 72)
    print()

    if c_coverages and ctrl_coverages_all:
        c_mean = statistics.mean(c_coverages)
        ctrl_mean = statistics.mean(ctrl_coverages_all)
        print(f"c-compound mean folio count: {c_mean:.1f}")
        print(f"Control mean folio count:    {ctrl_mean:.1f}")
        print(f"Ratio: {c_mean / ctrl_mean:.2f}x" if ctrl_mean > 0 else "Ratio: N/A")
        agg_pass = c_mean >= ctrl_mean
        print(f"c >= controls: {'YES' if agg_pass else 'NO'}")
    else:
        agg_pass = False
        print("Insufficient data for aggregate comparison")

    print()

    # Localization check
    print("=" * 72)
    print("LOCALIZATION CHECK")
    print("=" * 72)
    print()

    min_folios = float('inf')
    min_compound = None
    any_localized = False

    for mid in C_COMPOUNDS:
        n_fol = len(middle_folios.get(mid, set()))
        n_tok = middle_counts.get(mid, 0)
        if n_tok == 0:
            print(f"{mid}: no tokens (not in corpus)")
            continue

        localized = n_fol < 5
        if localized:
            any_localized = True

        if n_fol < min_folios:
            min_folios = n_fol
            min_compound = mid

        status = "LOCALIZED (<5)" if localized else "OK"
        print(f"  {mid}: {n_fol} folios ({n_fol/total_folios:.1%} coverage) - {status}")

    print()
    print(f"Minimum folio count: {min_compound} with {min_folios} folios")
    no_localization = not any_localized
    print(f"No localization (all >= 5 folios): {'YES' if no_localization else 'NO'}")
    print()

    # Prediction checks
    print("=" * 72)
    print("PREDICTION CHECKS")
    print("=" * 72)
    print()

    # P1: Major c-compounds >= 30 folios
    major_results = {}
    for mid in MAJOR_C_COMPOUNDS:
        n_fol = len(middle_folios.get(mid, set()))
        major_results[mid] = n_fol >= 30

    p1 = all(major_results.values())
    print(f"P1: Major c-compounds (ck, ckh, ct) each >= 30 folios")
    for mid, passed in major_results.items():
        n_fol = len(middle_folios.get(mid, set()))
        print(f"    {mid}: {n_fol} folios - {'PASS' if passed else 'FAIL'}")
    print(f"    Verdict: {'PASS' if p1 else 'FAIL'}")
    print()

    # P2: c-compound mean coverage >= controls
    p2 = agg_pass
    print(f"P2: c-compound mean folio coverage >= frequency-matched controls")
    print(f"    Verdict: {'PASS' if p2 else 'FAIL'}")
    print()

    # P3: No localization (all >= 5 folios)
    p3 = no_localization
    print(f"P3: No c-compound concentrated in < 5 folios")
    print(f"    Verdict: {'PASS' if p3 else 'FAIL'}")
    print()

    # Main pass criterion: major >= 30 AND no localization
    main_pass = p1 and p3
    all_pass = p1 and p2 and p3

    print("=" * 72)
    print(f"MAIN VERDICT (P1 AND P3): {'PASS' if main_pass else 'FAIL'}")
    print(f"FULL VERDICT (P1 AND P2 AND P3): {'PASS' if all_pass else 'FAIL'} "
          f"({sum([p1, p2, p3])}/3 predictions)")
    print("=" * 72)

    # Bonus: folio distribution histogram for major compounds
    print()
    print("FOLIO DISTRIBUTION FOR MAJOR c-COMPOUNDS")
    print("-" * 50)
    for mid in MAJOR_C_COMPOUNDS:
        folios = sorted(middle_folios.get(mid, set()))
        n = len(folios)
        if n == 0:
            continue
        # Show first few and last few
        if n <= 10:
            fol_str = ', '.join(folios)
        else:
            fol_str = (', '.join(folios[:5]) + ' ... ' + ', '.join(folios[-5:]))
        print(f"  {mid} ({n} folios): {fol_str}")


if __name__ == '__main__':
    main()
