#!/usr/bin/env python3
"""
F-F7: fch compound family survey

Survey the fch compound family: MIDDLEs containing both 'f' and 'c' atoms.
The dominant compound is fch (23 tokens, glossed "note"). Most multi-atom
f-compounds contain the c+h chain (fch, ofch, cfh, efch), suggesting the
f+c junction is structurally important.

Sub-predictions:
P1: f->c adjacency >= 80% in MIDDLEs containing both 'f' and 'c'.
    For every MIDDLE containing both 'f' and 'c', check if f immediately
    precedes c. Report fraction where f->c adjacency holds.

P2: First atom in Xfc/Xfch determines the compound's category. For each
    Xfch/Xfc compound, check if the primary category differs between
    compounds. Threshold: >= 2 distinct primary categories among testable
    compounds with N >= 5.

P3: MARKING >= 20% in every fch-family compound with N >= 5.

P4: fch/fc appears in compound-final position >= 50% of all fc occurrences
    in compounds. For MIDDLEs containing "fc" with len >= 3, check if "fc"
    is in the last 2-3 characters.

Pass: >= 3/4 sub-predictions pass.

KEY: This test reveals whether fc/fch is a compound-suffix unit (like ch in
c-atom compounds) and whether the first atom modifies its function.
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
    print("F-F7: fch compound family survey")
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

    # ---- P1: f->c adjacency in MIDDLEs containing both 'f' and 'c' ----
    print()
    print("-" * 75)
    print("P1: f->c adjacency in MIDDLEs containing both 'f' and 'c'")
    print("-" * 75)
    print()

    both_fc_middles = []
    fc_adjacent_count = 0
    fc_both_total = 0

    for mid, total in middle_totals.items():
        if 'f' in mid and 'c' in mid:
            # Check if f immediately precedes c anywhere in MIDDLE
            has_adjacent_fc = False
            for i in range(len(mid) - 1):
                if mid[i] == 'f' and mid[i + 1] == 'c':
                    has_adjacent_fc = True
                    break

            both_fc_middles.append((mid, total, has_adjacent_fc))
            fc_both_total += total
            if has_adjacent_fc:
                fc_adjacent_count += total

    both_fc_middles.sort(key=lambda x: -x[1])

    print(f"MIDDLEs containing both 'f' and 'c': {len(both_fc_middles)}")
    fc_adj_rate = fc_adjacent_count / fc_both_total if fc_both_total > 0 else 0
    print(f"Token-weighted f->c adjacency rate: {fc_adjacent_count}/{fc_both_total} "
          f"= {fc_adj_rate*100:.1f}%" if fc_both_total > 0 else "N/A")
    print()

    print(f"{'MIDDLE':<15} {'N':>5} {'f->c adj?':<10} {'Category':<15}")
    print("-" * 50)
    for mid, total, adjacent in both_fc_middles[:25]:
        adj_str = "YES" if adjacent else "NO"
        cat = cc.classify(mid)
        print(f"  {mid:<13} {total:>5} {adj_str:<10} {cat}")

    p1_pass = (fc_adj_rate >= 0.80) if fc_both_total > 0 else False
    print()
    if fc_both_total > 0:
        print(f"  P1 verdict: {'PASS' if p1_pass else 'FAIL'} "
              f"(threshold: >= 80% adjacency, observed: {fc_adj_rate*100:.1f}%)")
    else:
        print(f"  P1 verdict: FAIL (no MIDDLEs with both f and c)")

    # ---- Identify fc-family compounds: MIDDLEs containing "fc" substring ----
    # Also include "fch" as a compound unit
    print()
    print("-" * 75)
    print("fc/fch-family compound census")
    print("-" * 75)
    print()

    # Group by what comes BEFORE the fc/fch substring
    fc_family = defaultdict(lambda: {'cats': Counter(), 'total': 0, 'middles': Counter()})

    for mid, total in middle_totals.items():
        # Find "fc" in the MIDDLE
        idx = mid.find('fc')
        while idx >= 0:
            # Determine compound name from character before fc
            if idx == 0:
                # Check if it's fch or just fc
                if len(mid) > 2 and mid[2] == 'h':
                    compound_name = 'fch'
                else:
                    compound_name = 'fc'
            else:
                prefix_char = mid[idx - 1]
                if idx + 2 < len(mid) and mid[idx + 2] == 'h':
                    compound_name = prefix_char + 'fch'
                else:
                    compound_name = prefix_char + 'fc'

            cats = middle_cats[mid]
            for cat, n in cats.items():
                fc_family[compound_name]['cats'][cat] += n
            fc_family[compound_name]['total'] += total
            fc_family[compound_name]['middles'][mid] += total

            # Look for next occurrence
            idx = mid.find('fc', idx + 1)

    # Also check for 'f' followed by 'c' with 'h' (cfh pattern -- c before f then h)
    # These are f-containing MIDDLEs that also have c but not in f->c order
    for mid, total in middle_totals.items():
        if 'f' in mid and 'c' in mid and 'fc' not in mid:
            # This is a non-fc-adjacent compound (e.g., cfh)
            cats = middle_cats[mid]
            compound_name = f"({mid})*"  # Mark as non-adjacent
            for cat, n in cats.items():
                fc_family[compound_name]['cats'][cat] += n
            fc_family[compound_name]['total'] += total
            fc_family[compound_name]['middles'][mid] += total

    print(f"{'Compound':<12} {'N':>6} {'Primary':<15} {'MARK%':>7} {'MON%':>7} {'THERM%':>7}")
    print("-" * 62)
    for name in sorted(fc_family.keys(), key=lambda x: -fc_family[x]['total']):
        fam = fc_family[name]
        total = fam['total']
        cats = fam['cats']
        primary = cats.most_common(1)[0][0] if cats else 'N/A'
        mark_pct = cats.get('MARKING', 0) / total * 100 if total > 0 else 0
        mon_pct = cats.get('MONITORING', 0) / total * 100 if total > 0 else 0
        therm_pct = cats.get('THERMAL', 0) / total * 100 if total > 0 else 0
        n_marker = "*" if total >= 5 else " "
        print(f"  {name:<10}{n_marker} {total:>5} {primary:<15} {mark_pct:>6.1f}% {mon_pct:>6.1f}% {therm_pct:>6.1f}%")

    print()
    print("  * = N >= 5 (testable)")
    print("  Names ending in * = non-adjacent f...c pattern")

    # Show MIDDLE detail for top compounds
    print()
    print("  Per-compound MIDDLE detail (top 5 compounds by N):")
    for name in sorted(fc_family.keys(), key=lambda x: -fc_family[x]['total'])[:5]:
        fam = fc_family[name]
        print(f"\n  {name} (N={fam['total']}):")
        for mid, n in sorted(fam['middles'].items(), key=lambda x: -x[1])[:8]:
            cat = cc.classify(mid)
            print(f"    {mid:<15} N={n:>4} cat={cat}")

    # ---- P2: First atom determines category ----
    print()
    print("-" * 75)
    print("P2: First atom in Xfc/Xfch determines compound category")
    print("-" * 75)
    print()

    # Collect primary categories for compounds with N >= 5 (excluding bare fc/fch)
    testable_compounds = {}
    for name, fam in fc_family.items():
        if fam['total'] >= 5 and name not in ('fc', 'fch') and not name.endswith('*'):
            primary = fam['cats'].most_common(1)[0][0] if fam['cats'] else 'N/A'
            testable_compounds[name] = primary

    # Also include bare fc/fch as reference
    for name in ('fc', 'fch'):
        if name in fc_family and fc_family[name]['total'] >= 5:
            primary = fc_family[name]['cats'].most_common(1)[0][0]
            testable_compounds[name] = primary

    print(f"Testable compounds (N >= 5): {len(testable_compounds)}")
    for name, primary in sorted(testable_compounds.items()):
        total = fc_family[name]['total']
        print(f"  {name}: {primary} (N={total})")

    # Count distinct categories among testable Xfc/Xfch only (not bare)
    xfc_compounds = {n: c for n, c in testable_compounds.items() if n not in ('fc', 'fch')}
    distinct_categories = len(set(xfc_compounds.values())) if xfc_compounds else 0
    # If too few Xfc compounds, use all testable
    if len(xfc_compounds) < 2:
        distinct_categories = len(set(testable_compounds.values()))
        print(f"\n  (Too few Xfc compounds; using all testable including bare fc/fch)")

    p2_pass = distinct_categories >= 2
    print()
    print(f"  Distinct primary categories: {distinct_categories}")
    print(f"  P2 verdict: {'PASS' if p2_pass else 'FAIL'} (threshold: >= 2 distinct)")

    # ---- P3: MARKING >= 20% in every fch-family compound with N >= 5 ----
    print()
    print("-" * 75)
    print("P3: MARKING >= 20% in every fc/fch-family compound with N >= 5")
    print("-" * 75)
    print()

    all_testable = {name: fam for name, fam in fc_family.items() if fam['total'] >= 5}
    p3_failures = []
    p3_passes = []

    for name in sorted(all_testable.keys()):
        fam = all_testable[name]
        total = fam['total']
        mark_pct = fam['cats'].get('MARKING', 0) / total * 100 if total > 0 else 0
        passed = mark_pct >= 20.0
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name} (N={total}): MARKING = {mark_pct:.1f}%")
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
    if not all_testable:
        print(f"  WARNING: No compounds with N >= 5 found")

    # ---- P4: fc/fch in compound-final position >= 50% ----
    print()
    print("-" * 75)
    print("P4: fc/fch in compound-final position (last 2-3 chars) >= 50%")
    print("-" * 75)
    print()

    fc_final_tokens = 0
    fc_nonfinal_tokens = 0

    for mid, total in middle_totals.items():
        if len(mid) >= 3 and 'fc' in mid:
            # Check if fc or fch is at the end
            if mid.endswith('fc') or mid.endswith('fch'):
                fc_final_tokens += total
            else:
                fc_nonfinal_tokens += total

    fc_compound_total = fc_final_tokens + fc_nonfinal_tokens
    fc_final_rate = fc_final_tokens / fc_compound_total if fc_compound_total > 0 else 0

    print(f"Compound MIDDLEs (len >= 3) containing 'fc':")
    print(f"  fc/fch-final tokens:     {fc_final_tokens}")
    print(f"  fc/fch-non-final tokens: {fc_nonfinal_tokens}")
    print(f"  Total:                   {fc_compound_total}")
    print(f"  Final rate:              {fc_final_rate*100:.1f}%")
    print()

    # Detail: show examples of final and non-final
    fc_final_examples = []
    fc_nonfinal_examples = []
    for mid, total in sorted(middle_totals.items(), key=lambda x: -x[1]):
        if len(mid) >= 3 and 'fc' in mid:
            if mid.endswith('fc') or mid.endswith('fch'):
                if len(fc_final_examples) < 10:
                    fc_final_examples.append((mid, total))
            else:
                if len(fc_nonfinal_examples) < 10:
                    fc_nonfinal_examples.append((mid, total))

    print("  fc/fch-FINAL examples:")
    for mid, n in fc_final_examples:
        cat = cc.classify(mid)
        print(f"    {mid:<15} N={n:>4} cat={cat}")
    if not fc_final_examples:
        print("    (none found)")

    print("  fc/fch-NON-FINAL examples:")
    for mid, n in fc_nonfinal_examples:
        cat = cc.classify(mid)
        print(f"    {mid:<15} N={n:>4} cat={cat}")
    if not fc_nonfinal_examples:
        print("    (none found)")

    p4_pass = fc_final_rate >= 0.50
    print()
    if fc_compound_total > 0:
        print(f"  P4 verdict: {'PASS' if p4_pass else 'FAIL'} "
              f"(threshold: >= 50%, observed: {fc_final_rate*100:.1f}%)")
    else:
        p4_pass = False
        print(f"  P4 verdict: FAIL (no compound MIDDLEs with fc found)")

    # ---- Also survey all f-containing MIDDLEs (broader census) ----
    print()
    print("-" * 75)
    print("Broader f-MIDDLE census (all MIDDLEs containing 'f')")
    print("-" * 75)
    print()

    f_middles = [(mid, total) for mid, total in middle_totals.items() if 'f' in mid]
    f_middles.sort(key=lambda x: -x[1])

    f_total = sum(t for _, t in f_middles)
    print(f"Total f-containing MIDDLEs: {len(f_middles)} types, {f_total} tokens")
    print()
    print(f"{'MIDDLE':<15} {'N':>5} {'Category':<15} {'MARKING%':>9}")
    print("-" * 50)
    for mid, total in f_middles[:30]:
        cats = middle_cats[mid]
        cat = cc.classify(mid)
        mark_pct = cats.get('MARKING', 0) / total * 100 if total > 0 else 0
        print(f"  {mid:<13} {total:>5} {cat:<15} {mark_pct:>8.1f}%")

    # ---- OVERALL VERDICTS ----
    print()
    print("=" * 75)
    print("OVERALL VERDICTS")
    print("=" * 75)
    print()

    results = [
        ("P1: f->c adjacency >= 80% in MIDDLEs with both f and c",
         p1_pass),
        ("P2: >= 2 distinct primary categories among testable compounds",
         p2_pass),
        ("P3: MARKING >= 20% in ALL fc/fch-family compounds (N>=5)",
         p3_pass),
        ("P4: fc/fch compound-final position >= 50%",
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
        print("  fc/fch acts as a COMPOUND-SUFFIX unit: it occupies terminal position")
        print("  and the first atom modifies its function (different categories")
        print("  for different Xfch compounds). This parallels ch in c-atom compounds.")
    elif p4_pass:
        print("  fc/fch occupies terminal position but first-atom modulation is weak.")
        print("  May be a fixed suffix with uniform MARKING function.")
    elif p2_pass:
        print("  First atom modulates fc/fch but it is NOT position-locked.")
        print("  fc/fch may be a free-combining element rather than a suffix.")
    else:
        print("  Neither suffix behavior nor first-atom modulation confirmed.")
        print("  The fc/fch cluster may not have clear compound-suffix structure.")
    if p3_pass:
        print("  MARKING floor maintained across all compounds -- consistent with")
        print("  f's 'flag' gloss contributing annotation/marking flavor.")


if __name__ == '__main__':
    main()
