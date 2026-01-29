#!/usr/bin/env python3
"""
A-B Line MIDDLE Coverage Test

Test whether specific Currier A lines have unexpectedly strong vocabulary
coverage of specific Currier B lines.

Methodology:
1. For each A line, extract the set of token MIDDLEs
2. For each B line, extract the set of token MIDDLEs (using classified tokens)
3. Compute coverage: |B_line_middles AND A_line_middles| / |B_line_middles|
4. Find best-matching A line for each B line
5. Compare to random baseline

Key question: Are there B lines where a single A line provides >50% MIDDLE coverage?
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import random
from collections import defaultdict
from scripts.voynich import Transcript, Morphology

def main():
    print("=" * 70)
    print("A-B LINE MIDDLE COVERAGE TEST")
    print("=" * 70)

    # Load transcript and morphology
    tx = Transcript()
    morph = Morphology()

    # Load classified B tokens
    class_map_path = Path(__file__).parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        class_map = json.load(f)

    classified_tokens = set(class_map['token_to_class'].keys())
    print(f"Loaded {len(classified_tokens)} classified B tokens")

    # Step 1: Build A line -> MIDDLE set mapping
    print("\n1. Building A line vocabulary...")
    a_line_middles = defaultdict(set)  # (folio, line) -> set of middles
    a_line_tokens = defaultdict(list)

    for token in tx.currier_a():
        key = (token.folio, token.line)
        m = morph.extract(token.word)
        if m.middle:
            a_line_middles[key].add(m.middle)
            a_line_tokens[key].append(token.word)

    # Filter to lines with at least 2 middles (meaningful coverage test)
    a_line_middles = {k: v for k, v in a_line_middles.items() if len(v) >= 2}
    print(f"   A lines with 2+ MIDDLEs: {len(a_line_middles)}")

    # Step 2: Build B line -> MIDDLE set mapping (classified tokens only)
    print("\n2. Building B line vocabulary (classified tokens)...")
    b_line_middles = defaultdict(set)
    b_line_tokens = defaultdict(list)
    b_line_all_middles = defaultdict(set)  # Including unclassified

    for token in tx.currier_b():
        key = (token.folio, token.line)
        m = morph.extract(token.word)
        if m.middle:
            b_line_all_middles[key].add(m.middle)
            # Only include classified tokens in primary analysis
            if token.word in classified_tokens:
                b_line_middles[key].add(m.middle)
                b_line_tokens[key].append(token.word)

    # Filter B lines with at least 3 middles for meaningful coverage
    b_line_middles = {k: v for k, v in b_line_middles.items() if len(v) >= 3}
    print(f"   B lines with 3+ classified MIDDLEs: {len(b_line_middles)}")

    # Step 3: Sample B lines and compute coverage
    print("\n3. Computing coverage for first 200 B lines...")

    # Get first 200 B lines (sorted by folio, line)
    b_lines_sorted = sorted(b_line_middles.keys())[:200]
    print(f"   Testing {len(b_lines_sorted)} B lines")

    a_lines_list = list(a_line_middles.keys())

    # For each B line, find best matching A line
    results = []
    best_a_line_usage = defaultdict(int)  # Count how often each A line is best match

    for b_key in b_lines_sorted:
        b_middles = b_line_middles[b_key]
        b_size = len(b_middles)

        best_coverage = 0
        best_a_line = None
        best_overlap = set()
        all_coverages = []

        for a_key in a_lines_list:
            a_middles = a_line_middles[a_key]
            overlap = b_middles & a_middles
            coverage = len(overlap) / b_size
            all_coverages.append(coverage)

            if coverage > best_coverage:
                best_coverage = coverage
                best_a_line = a_key
                best_overlap = overlap

        best_a_line_usage[best_a_line] += 1

        results.append({
            'b_line': b_key,
            'b_middles': b_middles,
            'best_a_line': best_a_line,
            'best_coverage': best_coverage,
            'overlap': best_overlap,
            'mean_coverage': sum(all_coverages) / len(all_coverages) if all_coverages else 0,
            'max_coverage': max(all_coverages) if all_coverages else 0,
        })

    # Step 4: Compute random baseline
    print("\n4. Computing random baseline (100 iterations)...")
    random_best_coverages = []

    for _ in range(100):
        # Shuffle A line assignments
        shuffled_a_middles = list(a_line_middles.values())
        random.shuffle(shuffled_a_middles)

        for i, b_key in enumerate(b_lines_sorted[:100]):  # Use subset for speed
            b_middles = b_line_middles[b_key]
            b_size = len(b_middles)

            # Find best match in shuffled set
            best_cov = 0
            for a_middles in shuffled_a_middles:
                overlap = b_middles & a_middles
                coverage = len(overlap) / b_size
                if coverage > best_cov:
                    best_cov = coverage

            random_best_coverages.append(best_cov)

    random_mean = sum(random_best_coverages) / len(random_best_coverages)
    random_sorted = sorted(random_best_coverages)
    random_p95 = random_sorted[int(0.95 * len(random_sorted))]
    random_p99 = random_sorted[int(0.99 * len(random_sorted))]

    # Step 5: Analyze results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    # Distribution of best coverage rates
    best_coverages = [r['best_coverage'] for r in results]

    over_30 = sum(1 for c in best_coverages if c >= 0.30)
    over_50 = sum(1 for c in best_coverages if c >= 0.50)
    over_70 = sum(1 for c in best_coverages if c >= 0.70)

    print(f"\n5. Distribution of best-match coverage rates (N={len(best_coverages)}):")
    print(f"   Mean best coverage:    {sum(best_coverages)/len(best_coverages):.1%}")
    print(f"   Median best coverage:  {sorted(best_coverages)[len(best_coverages)//2]:.1%}")
    print(f"   Max best coverage:     {max(best_coverages):.1%}")
    print(f"   Min best coverage:     {min(best_coverages):.1%}")

    print(f"\n6. Coverage thresholds:")
    print(f"   B lines with >30% coverage from single A line: {over_30} ({over_30/len(best_coverages):.1%})")
    print(f"   B lines with >50% coverage from single A line: {over_50} ({over_50/len(best_coverages):.1%})")
    print(f"   B lines with >70% coverage from single A line: {over_70} ({over_70/len(best_coverages):.1%})")

    print(f"\n7. Random baseline comparison:")
    print(f"   Random mean best coverage: {random_mean:.1%}")
    print(f"   Random 95th percentile:    {random_p95:.1%}")
    print(f"   Random 99th percentile:    {random_p99:.1%}")
    print(f"   Observed mean:             {sum(best_coverages)/len(best_coverages):.1%}")
    print(f"   Lift over random:          {sum(best_coverages)/len(best_coverages) / random_mean:.2f}x")

    # Check if best matches cluster or spread
    print(f"\n8. Best-match A line distribution:")
    unique_best_a = len(best_a_line_usage)
    max_usage = max(best_a_line_usage.values()) if best_a_line_usage else 0
    print(f"   Unique A lines serving as best match: {unique_best_a}")
    print(f"   Max times single A line is best:      {max_usage}")

    # Top A lines
    top_a_lines = sorted(best_a_line_usage.items(), key=lambda x: -x[1])[:10]
    print(f"\n   Top 10 most-used A lines as best match:")
    for a_key, count in top_a_lines:
        a_middles = a_line_middles[a_key]
        print(f"      {a_key[0]} line {a_key[1]}: {count} times, {len(a_middles)} MIDDLEs: {sorted(a_middles)[:5]}...")

    # Show top coverage examples
    print(f"\n9. Highest coverage examples:")
    top_results = sorted(results, key=lambda x: -x['best_coverage'])[:10]
    for r in top_results:
        b_key = r['b_line']
        a_key = r['best_a_line']
        print(f"\n   B line {b_key[0]} line {b_key[1]} ({len(r['b_middles'])} MIDDLEs)")
        print(f"      Best match: A line {a_key[0]} line {a_key[1]}")
        print(f"      Coverage: {r['best_coverage']:.1%}")
        print(f"      Overlap: {sorted(r['overlap'])}")
        print(f"      B MIDDLEs: {sorted(r['b_middles'])}")
        print(f"      A MIDDLEs: {sorted(a_line_middles[a_key])}")

    # Check for clustering: do certain A folios dominate?
    print(f"\n10. A folio distribution in best matches:")
    a_folio_counts = defaultdict(int)
    for a_key, count in best_a_line_usage.items():
        a_folio_counts[a_key[0]] += count

    top_a_folios = sorted(a_folio_counts.items(), key=lambda x: -x[1])[:10]
    for folio, count in top_a_folios:
        print(f"      {folio}: {count} best matches")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if over_50 > 0:
        print(f"\nFINDING: {over_50} B lines have >50% MIDDLE coverage from a single A line.")
        print("This suggests potential line-level correspondence.")
    elif over_30 / len(best_coverages) > 0.1:
        print(f"\nFINDING: {over_30/len(best_coverages):.1%} of B lines have >30% coverage.")
        print("Moderate line-level correspondence detected.")
    else:
        print(f"\nFINDING: Low line-level correspondence.")
        print("Best matches are likely driven by shared common vocabulary, not direct pairing.")

    lift = sum(best_coverages)/len(best_coverages) / random_mean
    if lift > 1.5:
        print(f"\nThe {lift:.2f}x lift over random suggests some structural relationship,")
        print("but likely at folio/section level rather than line-to-line.")
    else:
        print(f"\nThe {lift:.2f}x lift over random is modest, suggesting coverage is")
        print("driven primarily by shared core vocabulary.")

    # Unique A line analysis
    if unique_best_a < len(b_lines_sorted) * 0.3:
        print(f"\nOnly {unique_best_a} unique A lines serve as best matches for {len(b_lines_sorted)} B lines.")
        print("This indicates a small pool of A lines with high coverage potential,")
        print("rather than one-to-one line correspondence.")

if __name__ == '__main__':
    main()
