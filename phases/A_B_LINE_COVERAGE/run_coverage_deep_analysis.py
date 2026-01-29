#!/usr/bin/env python3
"""
A-B Line MIDDLE Coverage - Deep Analysis

The initial test showed 97% of B lines have >50% coverage from a single A line,
but only 1.02x lift over random. This suggests coverage is driven by shared
core vocabulary rather than true line-level correspondence.

This script investigates:
1. What MIDDLEs drive coverage (are they just core shared vocabulary?)
2. Does coverage differ when we exclude high-frequency MIDDLEs?
3. Is coverage better explained at folio level than line level?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import random
from collections import defaultdict, Counter
from scripts.voynich import Transcript, Morphology

def main():
    print("=" * 70)
    print("A-B LINE COVERAGE - DEEP ANALYSIS")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()

    # Load classified B tokens
    class_map_path = Path(__file__).parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        class_map = json.load(f)

    classified_tokens = set(class_map['token_to_class'].keys())

    # Build global MIDDLE frequency distributions
    print("\n1. Building MIDDLE frequency distributions...")

    a_middle_counts = Counter()
    b_middle_counts = Counter()

    # Build per-line data
    a_line_middles = defaultdict(set)
    b_line_middles = defaultdict(set)
    a_line_raw_middles = defaultdict(list)  # With frequency
    b_line_raw_middles = defaultdict(list)

    for token in tx.currier_a():
        key = (token.folio, token.line)
        m = morph.extract(token.word)
        if m.middle:
            a_middle_counts[m.middle] += 1
            a_line_middles[key].add(m.middle)
            a_line_raw_middles[key].append(m.middle)

    for token in tx.currier_b():
        key = (token.folio, token.line)
        m = morph.extract(token.word)
        if m.middle:
            b_middle_counts[m.middle] += 1
            if token.word in classified_tokens:
                b_line_middles[key].add(m.middle)
                b_line_raw_middles[key].append(m.middle)

    # Identify high-frequency shared MIDDLEs
    shared_middles = set(a_middle_counts.keys()) & set(b_middle_counts.keys())
    print(f"   Total unique A MIDDLEs: {len(a_middle_counts)}")
    print(f"   Total unique B MIDDLEs: {len(b_middle_counts)}")
    print(f"   Shared MIDDLEs: {len(shared_middles)}")

    # Top 20 most frequent in both
    print(f"\n2. Top 20 shared MIDDLEs by combined frequency:")
    combined_freq = [(m, a_middle_counts[m] + b_middle_counts[m])
                     for m in shared_middles]
    top_shared = sorted(combined_freq, key=lambda x: -x[1])[:20]
    core_middles = set()
    for m, freq in top_shared:
        core_middles.add(m)
        print(f"      {m:10s}  A: {a_middle_counts[m]:4d}  B: {b_middle_counts[m]:4d}  Total: {freq:5d}")

    # Filter to usable lines
    a_line_middles = {k: v for k, v in a_line_middles.items() if len(v) >= 2}
    b_line_middles = {k: v for k, v in b_line_middles.items() if len(v) >= 3}

    # Select test B lines
    b_lines_sorted = sorted(b_line_middles.keys())[:200]
    a_lines_list = list(a_line_middles.keys())

    # Analysis 1: Coverage with core MIDDLEs excluded
    print("\n" + "=" * 70)
    print("3. Coverage analysis EXCLUDING top 10 core MIDDLEs")
    print("=" * 70)

    top10_core = set(m for m, _ in top_shared[:10])
    print(f"   Excluding: {sorted(top10_core)}")

    coverage_no_core = []
    for b_key in b_lines_sorted:
        b_mids = b_line_middles[b_key] - top10_core
        if len(b_mids) < 2:
            continue

        best_cov = 0
        for a_key in a_lines_list:
            a_mids = a_line_middles[a_key] - top10_core
            if len(a_mids) == 0:
                continue
            overlap = b_mids & a_mids
            coverage = len(overlap) / len(b_mids)
            if coverage > best_cov:
                best_cov = coverage

        coverage_no_core.append(best_cov)

    if coverage_no_core:
        over_30 = sum(1 for c in coverage_no_core if c >= 0.30)
        over_50 = sum(1 for c in coverage_no_core if c >= 0.50)
        print(f"\n   With core excluded (N={len(coverage_no_core)} B lines with 2+ non-core MIDDLEs):")
        print(f"   Mean best coverage:    {sum(coverage_no_core)/len(coverage_no_core):.1%}")
        print(f"   B lines >30% coverage: {over_30} ({over_30/len(coverage_no_core):.1%})")
        print(f"   B lines >50% coverage: {over_50} ({over_50/len(coverage_no_core):.1%})")

    # Analysis 2: Folio-level vs Line-level coverage
    print("\n" + "=" * 70)
    print("4. Folio-level vs Line-level coverage comparison")
    print("=" * 70)

    # Build folio-level MIDDLE sets for A
    a_folio_middles = defaultdict(set)
    for (folio, line), mids in a_line_middles.items():
        a_folio_middles[folio].update(mids)

    folio_coverages = []
    line_coverages = []
    same_folio_best = 0

    for b_key in b_lines_sorted:
        b_mids = b_line_middles[b_key]
        b_folio = b_key[0]

        # Best A line coverage
        best_line_cov = 0
        best_line_a = None
        for a_key in a_lines_list:
            a_mids = a_line_middles[a_key]
            overlap = b_mids & a_mids
            coverage = len(overlap) / len(b_mids)
            if coverage > best_line_cov:
                best_line_cov = coverage
                best_line_a = a_key

        # Best A folio coverage
        best_folio_cov = 0
        best_folio_a = None
        for a_folio, a_mids in a_folio_middles.items():
            overlap = b_mids & a_mids
            coverage = len(overlap) / len(b_mids)
            if coverage > best_folio_cov:
                best_folio_cov = coverage
                best_folio_a = a_folio

        line_coverages.append(best_line_cov)
        folio_coverages.append(best_folio_cov)

        if best_line_a and best_line_a[0] == best_folio_a:
            same_folio_best += 1

    print(f"\n   Line-level best coverage:  {sum(line_coverages)/len(line_coverages):.1%} mean")
    print(f"   Folio-level best coverage: {sum(folio_coverages)/len(folio_coverages):.1%} mean")
    print(f"   Lift from folio-level:     {sum(folio_coverages)/sum(line_coverages):.2f}x")
    print(f"   Best A line is from best A folio: {same_folio_best}/{len(line_coverages)} ({same_folio_best/len(line_coverages):.1%})")

    # Analysis 3: Coverage composition - what fraction from core vs rare?
    print("\n" + "=" * 70)
    print("5. Coverage composition analysis")
    print("=" * 70)

    core_driven = []  # Fraction of overlap from core MIDDLEs
    rare_driven = []

    rare_threshold = 5  # MIDDLEs appearing in fewer than 5 A lines
    a_middle_line_count = Counter()
    for mids in a_line_middles.values():
        for m in mids:
            a_middle_line_count[m] += 1

    rare_middles = {m for m, c in a_middle_line_count.items() if c <= rare_threshold}
    print(f"   'Rare' MIDDLEs (appearing in <=5 A lines): {len(rare_middles)}")

    for b_key in b_lines_sorted:
        b_mids = b_line_middles[b_key]

        # Find best A line
        best_cov = 0
        best_overlap = set()
        for a_key in a_lines_list:
            a_mids = a_line_middles[a_key]
            overlap = b_mids & a_mids
            coverage = len(overlap) / len(b_mids)
            if coverage > best_cov:
                best_cov = coverage
                best_overlap = overlap

        if best_overlap:
            core_in_overlap = len(best_overlap & top10_core)
            rare_in_overlap = len(best_overlap & rare_middles)
            core_driven.append(core_in_overlap / len(best_overlap))
            rare_driven.append(rare_in_overlap / len(best_overlap))

    print(f"\n   Mean fraction of overlap from top-10 core: {sum(core_driven)/len(core_driven):.1%}")
    print(f"   Mean fraction of overlap from rare MIDDLEs: {sum(rare_driven)/len(rare_driven):.1%}")

    # Analysis 4: Check for specific B lines with RARE MIDDLE matches
    print("\n" + "=" * 70)
    print("6. B lines with RARE MIDDLE matches (potential true correspondence)")
    print("=" * 70)

    rare_match_examples = []
    for b_key in b_lines_sorted:
        b_mids = b_line_middles[b_key]
        b_rare = b_mids & rare_middles

        if len(b_rare) < 2:
            continue

        # Find A lines with best rare MIDDLE overlap
        best_rare_cov = 0
        best_a = None
        best_rare_overlap = set()
        for a_key in a_lines_list:
            a_mids = a_line_middles[a_key]
            a_rare = a_mids & rare_middles
            overlap = b_rare & a_rare
            if len(overlap) > len(best_rare_overlap):
                best_rare_overlap = overlap
                best_a = a_key
                best_rare_cov = len(overlap) / len(b_rare) if b_rare else 0

        if len(best_rare_overlap) >= 2:
            rare_match_examples.append({
                'b_key': b_key,
                'a_key': best_a,
                'b_rare': b_rare,
                'overlap': best_rare_overlap,
                'coverage': best_rare_cov
            })

    print(f"\n   B lines with 2+ rare MIDDLE matches: {len(rare_match_examples)}")

    if rare_match_examples:
        print(f"\n   Examples of rare MIDDLE correspondence:")
        for ex in sorted(rare_match_examples, key=lambda x: -len(x['overlap']))[:10]:
            b_key = ex['b_key']
            a_key = ex['a_key']
            print(f"\n      B: {b_key[0]} line {b_key[1]}")
            print(f"      A: {a_key[0]} line {a_key[1]}")
            print(f"      Rare overlap: {sorted(ex['overlap'])} ({len(ex['overlap'])}/{len(ex['b_rare'])} = {ex['coverage']:.0%})")

    # Analysis 5: Are there ANY B lines completely covered by a SINGLE A line?
    print("\n" + "=" * 70)
    print("7. Perfect coverage analysis")
    print("=" * 70)

    perfect_matches = []
    for b_key in b_lines_sorted:
        b_mids = b_line_middles[b_key]

        for a_key in a_lines_list:
            a_mids = a_line_middles[a_key]
            if b_mids.issubset(a_mids):
                perfect_matches.append({
                    'b_key': b_key,
                    'a_key': a_key,
                    'b_mids': b_mids,
                    'a_mids': a_mids,
                    'b_size': len(b_mids),
                    'a_size': len(a_mids)
                })
                break  # Just find first perfect match

    print(f"\n   B lines perfectly covered by some A line: {len(perfect_matches)}/{len(b_lines_sorted)}")

    # Analyze perfect matches
    if perfect_matches:
        b_sizes = [p['b_size'] for p in perfect_matches]
        print(f"   Size distribution of perfectly covered B lines:")
        print(f"      Mean: {sum(b_sizes)/len(b_sizes):.1f} MIDDLEs")
        print(f"      Max:  {max(b_sizes)} MIDDLEs")
        print(f"      Min:  {min(b_sizes)} MIDDLEs")

        # Large B line examples
        large_perfect = [p for p in perfect_matches if p['b_size'] >= 5]
        print(f"\n   Perfectly covered B lines with 5+ MIDDLEs: {len(large_perfect)}")
        for p in sorted(large_perfect, key=lambda x: -x['b_size'])[:5]:
            print(f"      B: {p['b_key']} ({p['b_size']} MIDDLEs) <- A: {p['a_key']} ({p['a_size']} MIDDLEs)")
            print(f"         B MIDDLEs: {sorted(p['b_mids'])}")

    # Summary
    print("\n" + "=" * 70)
    print("CONCLUSIONS")
    print("=" * 70)

    print(f"""
1. HIGH COVERAGE IS DRIVEN BY SHARED CORE VOCABULARY
   - {sum(core_driven)/len(core_driven):.0%} of coverage overlap comes from top-10 MIDDLEs
   - Only {sum(rare_driven)/len(rare_driven):.0%} from rare MIDDLEs

2. FOLIO LEVEL PROVIDES ONLY MARGINAL IMPROVEMENT
   - Line-level mean:  {sum(line_coverages)/len(line_coverages):.1%}
   - Folio-level mean: {sum(folio_coverages)/len(folio_coverages):.1%}
   - This suggests neither line nor folio is the true unit

3. RARE MIDDLE CORRESPONDENCE IS LIMITED
   - Only {len(rare_match_examples)} B lines have 2+ rare MIDDLE matches
   - This is {len(rare_match_examples)/len(b_lines_sorted):.1%} of tested B lines

4. CONCLUSION: Coverage is driven by shared operational vocabulary (core MIDDLEs
   appearing in both A and B), NOT by direct line-level mapping. A and B share
   a common grammatical substrate, but individual A lines do not "template"
   individual B lines.
""")

if __name__ == '__main__':
    main()
