#!/usr/bin/env python3
"""
S-S7: sh compound family survey

Survey the sh compound family: sh, ksh, lsh, osh, tsh, esh, psh, and any
other Xsh compounds found in the corpus.

Sub-predictions:
P1: s appears before h in compounds (positional -- s is always immediately
    before h in the sh family). For every MIDDLE containing both 's' and 'h',
    check if s immediately precedes h. Report fraction where s->h adjacency holds.

P2: First atom in Xsh determines the compound's category. For each Xsh compound
    (ksh, lsh, osh, tsh, etc.), check if the primary category differs between
    compounds. Threshold: >= 2 distinct primary categories among Xsh compounds
    with N >= 5.

P3: MONITORING >= 20% in every sh-family compound with N >= 5.

P4: sh in compound-final position >= 60% of all sh occurrences in compounds.
    For MIDDLEs containing "sh" with len >= 3, check if "sh" is the last 2
    characters.

Pass: >= 3/4 sub-predictions pass.

KEY: This test reveals whether sh is a compound-suffix unit (like ch in
c-atom compounds) and whether the first atom modifies sh's function.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier


CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING', 'OPERATION',
              'TRANSITION', 'MARKING', 'MONITORING']


def main():
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    print("=" * 75)
    print("S-S7: sh compound family survey")
    print("=" * 75)

    # ---- PASS 1: Collect all MIDDLEs and classify ----
    middle_cats = defaultdict(Counter)  # middle -> {cat: count}
    middle_totals = Counter()           # middle -> total
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

        middle_cats[mid][cat] += 1
        middle_totals[mid] += 1
        global_cats[cat] += 1
        global_total += 1

    # ---- P1: s->h adjacency in MIDDLEs containing both s and h ----
    print()
    print("-" * 75)
    print("P1: s->h adjacency in MIDDLEs containing both 's' and 'h'")
    print("-" * 75)
    print()

    both_sh_middles = []
    sh_adjacent_count = 0
    sh_both_total = 0

    for mid, total in middle_totals.items():
        if 's' in mid and 'h' in mid:
            # Check if s immediately precedes h anywhere in MIDDLE
            has_adjacent_sh = False
            for i in range(len(mid) - 1):
                if mid[i] == 's' and mid[i + 1] == 'h':
                    has_adjacent_sh = True
                    break

            both_sh_middles.append((mid, total, has_adjacent_sh))
            sh_both_total += total
            if has_adjacent_sh:
                sh_adjacent_count += total

    both_sh_middles.sort(key=lambda x: -x[1])

    print(f"MIDDLEs containing both 's' and 'h': {len(both_sh_middles)}")
    print(f"Token-weighted s->h adjacency rate: {sh_adjacent_count}/{sh_both_total} "
          f"= {sh_adjacent_count/sh_both_total*100:.1f}%" if sh_both_total > 0 else "N/A")
    print()

    print(f"{'MIDDLE':<15} {'N':>5} {'s->h adj?':<10} {'Category':<15}")
    print("-" * 50)
    for mid, total, adjacent in both_sh_middles[:25]:
        adj_str = "YES" if adjacent else "NO"
        cat = cc.classify(mid)
        print(f"  {mid:<13} {total:>5} {adj_str:<10} {cat}")

    p1_pass = (sh_adjacent_count / sh_both_total >= 0.80) if sh_both_total > 0 else False
    print()
    print(f"  P1 verdict: {'PASS' if p1_pass else 'FAIL'} "
          f"(threshold: >= 80% adjacency, observed: "
          f"{sh_adjacent_count/sh_both_total*100:.1f}%)" if sh_both_total > 0 else "FAIL (no data)")

    # ---- Identify sh-family compounds: MIDDLEs containing "sh" substring ----
    print()
    print("-" * 75)
    print("sh-family compound census")
    print("-" * 75)
    print()

    # Group by what comes BEFORE "sh" (the prefix atom of the sh-compound)
    sh_family = defaultdict(lambda: {'cats': Counter(), 'total': 0, 'middles': Counter()})

    for mid, total in middle_totals.items():
        # Find all occurrences of "sh" in the MIDDLE
        idx = mid.find('sh')
        while idx >= 0:
            prefix_part = mid[:idx] if idx > 0 else ''
            suffix_part = mid[idx + 2:] if idx + 2 < len(mid) else ''

            # Classify compound type by first atom before "sh"
            if idx == 0:
                compound_name = 'sh'  # bare sh
            else:
                # Take the character immediately before "sh"
                compound_name = mid[idx - 1] + 'sh'

            cats = middle_cats[mid]
            for cat, n in cats.items():
                sh_family[compound_name]['cats'][cat] += n
            sh_family[compound_name]['total'] += total
            sh_family[compound_name]['middles'][mid] += total

            # Look for next occurrence
            idx = mid.find('sh', idx + 1)

    print(f"{'Compound':<10} {'N':>6} {'Primary':<15} {'MON%':>7} {'STAG%':>7} {'THERM%':>7}")
    print("-" * 60)
    for name in sorted(sh_family.keys(), key=lambda x: -sh_family[x]['total']):
        fam = sh_family[name]
        total = fam['total']
        cats = fam['cats']
        primary = cats.most_common(1)[0][0] if cats else 'N/A'
        mon_pct = cats.get('MONITORING', 0) / total * 100 if total > 0 else 0
        stag_pct = cats.get('STAGING', 0) / total * 100 if total > 0 else 0
        therm_pct = cats.get('THERMAL', 0) / total * 100 if total > 0 else 0
        n_marker = "*" if total >= 5 else " "
        print(f"  {name:<8}{n_marker} {total:>5} {primary:<15} {mon_pct:>6.1f}% {stag_pct:>6.1f}% {therm_pct:>6.1f}%")

    print()
    print("  * = N >= 5 (testable)")

    # Show MIDDLE detail for top compounds
    print()
    print("  Per-compound MIDDLE detail (top 5 compounds by N):")
    for name in sorted(sh_family.keys(), key=lambda x: -sh_family[x]['total'])[:5]:
        fam = sh_family[name]
        print(f"\n  {name} (N={fam['total']}):")
        for mid, n in sorted(fam['middles'].items(), key=lambda x: -x[1])[:8]:
            cat = cc.classify(mid)
            print(f"    {mid:<15} N={n:>4} cat={cat}")

    # ---- P2: First atom determines category ----
    print()
    print("-" * 75)
    print("P2: First atom in Xsh determines compound category")
    print("-" * 75)
    print()

    # Collect primary categories for Xsh compounds with N >= 5
    testable_compounds = {}
    for name, fam in sh_family.items():
        if fam['total'] >= 5 and name != 'sh':  # Exclude bare sh
            primary = fam['cats'].most_common(1)[0][0] if fam['cats'] else 'N/A'
            testable_compounds[name] = primary

    print(f"Testable Xsh compounds (N >= 5, excluding bare sh): {len(testable_compounds)}")
    for name, primary in sorted(testable_compounds.items()):
        print(f"  {name}: {primary}")

    distinct_categories = len(set(testable_compounds.values()))
    p2_pass = distinct_categories >= 2
    print()
    print(f"  Distinct primary categories: {distinct_categories}")
    print(f"  P2 verdict: {'PASS' if p2_pass else 'FAIL'} (threshold: >= 2 distinct)")

    # ---- P3: MONITORING >= 20% in every sh-family compound with N >= 5 ----
    print()
    print("-" * 75)
    print("P3: MONITORING >= 20% in every sh-family compound with N >= 5")
    print("-" * 75)
    print()

    all_testable = {name: fam for name, fam in sh_family.items() if fam['total'] >= 5}
    p3_failures = []
    p3_passes = []

    for name in sorted(all_testable.keys()):
        fam = all_testable[name]
        total = fam['total']
        mon_pct = fam['cats'].get('MONITORING', 0) / total * 100 if total > 0 else 0
        passed = mon_pct >= 20.0
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name} (N={total}): MONITORING = {mon_pct:.1f}%")
        if passed:
            p3_passes.append(name)
        else:
            p3_failures.append(name)

    p3_pass = len(p3_failures) == 0 and len(all_testable) > 0
    print()
    print(f"  P3 verdict: {'PASS' if p3_pass else 'FAIL'} "
          f"({len(p3_passes)}/{len(all_testable)} compounds pass)")
    if p3_failures:
        print(f"  Failures: {', '.join(p3_failures)}")

    # ---- P4: sh in compound-final position >= 60% ----
    print()
    print("-" * 75)
    print("P4: sh in compound-final position (last 2 chars) >= 60%")
    print("-" * 75)
    print()

    sh_final_tokens = 0
    sh_nonfinal_tokens = 0

    for mid, total in middle_totals.items():
        if len(mid) >= 3 and 'sh' in mid:
            if mid.endswith('sh'):
                sh_final_tokens += total
            else:
                sh_nonfinal_tokens += total

    sh_compound_total = sh_final_tokens + sh_nonfinal_tokens
    sh_final_rate = sh_final_tokens / sh_compound_total if sh_compound_total > 0 else 0

    print(f"Compound MIDDLEs (len >= 3) containing 'sh':")
    print(f"  sh-final tokens:     {sh_final_tokens}")
    print(f"  sh-non-final tokens: {sh_nonfinal_tokens}")
    print(f"  Total:               {sh_compound_total}")
    print(f"  Final rate:          {sh_final_rate*100:.1f}%")
    print()

    # Detail: show examples of final and non-final
    sh_final_examples = []
    sh_nonfinal_examples = []
    for mid, total in sorted(middle_totals.items(), key=lambda x: -x[1]):
        if len(mid) >= 3 and 'sh' in mid:
            if mid.endswith('sh'):
                if len(sh_final_examples) < 10:
                    sh_final_examples.append((mid, total))
            else:
                if len(sh_nonfinal_examples) < 10:
                    sh_nonfinal_examples.append((mid, total))

    print("  sh-FINAL examples:")
    for mid, n in sh_final_examples:
        cat = cc.classify(mid)
        print(f"    {mid:<15} N={n:>4} cat={cat}")

    print("  sh-NON-FINAL examples:")
    for mid, n in sh_nonfinal_examples:
        cat = cc.classify(mid)
        print(f"    {mid:<15} N={n:>4} cat={cat}")

    p4_pass = sh_final_rate >= 0.60
    print()
    print(f"  P4 verdict: {'PASS' if p4_pass else 'FAIL'} "
          f"(threshold: >= 60%, observed: {sh_final_rate*100:.1f}%)")

    # ---- OVERALL VERDICTS ----
    print()
    print("=" * 75)
    print("OVERALL VERDICTS")
    print("=" * 75)
    print()

    results = [
        ("P1: s->h adjacency >= 80% in MIDDLEs with both s and h",
         p1_pass),
        ("P2: >= 2 distinct primary categories among testable Xsh",
         p2_pass),
        ("P3: MONITORING >= 20% in ALL sh-family compounds (N>=5)",
         p3_pass),
        ("P4: sh compound-final position >= 60%",
         p4_pass),
    ]

    pass_count = 0
    for desc, passed in results:
        status = "PASS" if passed else "FAIL"
        if passed:
            pass_count += 1
        print(f"  [{status}] {desc}")

    print()
    print(f"  Sub-predictions passed: {pass_count}/4")
    overall = pass_count >= 3
    print(f"  OVERALL: {'PASS' if overall else 'FAIL'} (threshold: >= 3/4)")

    # Interpretation note
    print()
    print("-" * 75)
    print("INTERPRETATION")
    print("-" * 75)
    print()
    if p4_pass and p2_pass:
        print("  sh acts as a COMPOUND-SUFFIX unit: it occupies terminal position")
        print("  and the first atom modifies its function (different categories")
        print("  for different Xsh compounds). This parallels ch in c-atom compounds.")
    elif p4_pass:
        print("  sh occupies terminal position but first-atom modulation is weak.")
        print("  May be a fixed suffix with uniform function.")
    elif p2_pass:
        print("  First atom modulates sh but sh is NOT position-locked.")
        print("  sh may be a free-combining element rather than a suffix.")
    else:
        print("  Neither suffix behavior nor first-atom modulation confirmed.")
        print("  sh-family may not have clear compound-suffix structure.")


if __name__ == '__main__':
    main()
