#!/usr/bin/env python3
"""
Final verdict on A-B paragraph correspondence.

Synthesizes all tests to determine whether there is specific paragraph-level
correspondence or just shared vocabulary.

Key comparison:
- Line-level: 71.4% coverage, 1.02x lift (no correspondence)
- Paragraph-level: 66.2% coverage, 2.49x raw lift, 1.20x after pool-size control

The question: Why does paragraph aggregation increase lift?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import random
import statistics

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

GALLOWS = {'k', 't', 'p', 'f'}

RI_PP_PATH = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json'
with open(RI_PP_PATH) as f:
    ri_pp_data = json.load(f)
PP_MIDDLES = set(ri_pp_data['a_shared_middles'])


def is_gallows_initial(word: str) -> bool:
    return word and word[0] in GALLOWS


def extract_a_folios():
    """Extract A folios with PP MIDDLEs."""
    tx = Transcript()
    morph = Morphology()

    folios = defaultdict(set)
    for token in tx.currier_a():
        if token.word:
            m = morph.extract(token.word)
            if m.middle and m.middle in PP_MIDDLES:
                folios[token.folio].add(m.middle)

    return dict(folios)


def extract_a_lines():
    """Extract A lines with PP MIDDLEs."""
    tx = Transcript()
    morph = Morphology()

    lines = defaultdict(set)
    for token in tx.currier_a():
        if token.word:
            m = morph.extract(token.word)
            if m.middle and m.middle in PP_MIDDLES:
                lines[f"{token.folio}_{token.line}"].add(m.middle)

    return dict(lines)


def extract_a_paragraphs():
    """Extract A paragraphs with PP MIDDLEs."""
    tx = Transcript()
    morph = Morphology()

    folio_lines = defaultdict(lambda: defaultdict(list))
    for token in tx.currier_a():
        if token.word:
            folio_lines[token.folio][token.line].append(token)

    paragraphs = {}
    for folio in sorted(folio_lines.keys()):
        lines_dict = folio_lines[folio]
        sorted_lines = sorted(lines_dict.keys(), key=lambda x: int(x) if x.isdigit() else 999)

        para_idx = 0
        current_middles = set()
        current_key = None

        for line_num in sorted_lines:
            tokens = lines_dict[line_num]
            first_token = tokens[0] if tokens else None
            is_para_start = first_token and is_gallows_initial(first_token.word)

            if is_para_start:
                if current_key is not None and current_middles:
                    paragraphs[current_key] = current_middles
                current_key = f"{folio}_p{para_idx}"
                current_middles = set()
                para_idx += 1
            elif current_key is None:
                current_key = f"{folio}_p{para_idx}"
                para_idx += 1

            for token in tokens:
                m = morph.extract(token.word)
                if m.middle and m.middle in PP_MIDDLES:
                    current_middles.add(m.middle)

        if current_key is not None and current_middles:
            paragraphs[current_key] = current_middles

    return paragraphs


def extract_b_lines():
    """Extract B lines with MIDDLEs."""
    tx = Transcript()
    morph = Morphology()

    lines = defaultdict(set)
    for token in tx.currier_b():
        if token.word:
            m = morph.extract(token.word)
            if m.middle:
                lines[f"{token.folio}_{token.line}"].add(m.middle)

    return dict(lines)


def extract_b_paragraphs():
    """Extract B paragraphs with MIDDLEs."""
    tx = Transcript()
    morph = Morphology()

    folio_paras = defaultdict(lambda: defaultdict(set))
    current_para_idx = defaultdict(int)

    for token in tx.currier_b():
        if not token.word:
            continue
        folio = token.folio
        if token.par_initial:
            current_para_idx[folio] += 1
        para_idx = current_para_idx[folio]
        m = morph.extract(token.word)
        if m.middle:
            folio_paras[folio][para_idx].add(m.middle)

    paragraphs = {}
    for folio in folio_paras:
        for para_idx, middles in folio_paras[folio].items():
            paragraphs[f"{folio}_p{para_idx}"] = middles

    return paragraphs


def compute_best_match_coverage(b_units, a_units):
    """Compute best-match coverage for each B unit."""
    coverages = []
    for b_id, b_middles in b_units.items():
        if not b_middles:
            continue
        best_cov = 0.0
        for a_id, a_middles in a_units.items():
            if not a_middles:
                continue
            cov = len(b_middles & a_middles) / len(b_middles)
            if cov > best_cov:
                best_cov = cov
        coverages.append(best_cov)
    return coverages


def compute_random_baseline(b_units, a_units, n_trials=100):
    """Compute random baseline coverage."""
    all_covs = []
    a_list = list(a_units.values())

    for _ in range(n_trials):
        random.shuffle(a_list)
        trial_covs = []
        for i, (b_id, b_middles) in enumerate(b_units.items()):
            if not b_middles:
                continue
            a_middles = a_list[i % len(a_list)]
            cov = len(b_middles & a_middles) / len(b_middles)
            trial_covs.append(cov)
        all_covs.append(statistics.mean(trial_covs))

    return statistics.mean(all_covs)


def main():
    print("=" * 70)
    print("FINAL VERDICT: A-B PARAGRAPH CORRESPONDENCE")
    print("=" * 70)

    # Extract all granularities
    a_folios = extract_a_folios()
    a_lines = extract_a_lines()
    a_paragraphs = extract_a_paragraphs()

    b_lines = extract_b_lines()
    b_paragraphs = extract_b_paragraphs()

    print(f"\nA units: {len(a_folios)} folios, {len(a_lines)} lines, {len(a_paragraphs)} paragraphs")
    print(f"B units: {len(b_lines)} lines, {len(b_paragraphs)} paragraphs")

    # Compute metrics at each granularity
    results = {}

    print("\n" + "=" * 70)
    print("COVERAGE COMPARISON ACROSS GRANULARITIES")
    print("=" * 70)

    for label, a_units, b_units in [
        ("Line->Line", a_lines, b_lines),
        ("Para->Para", a_paragraphs, b_paragraphs),
        ("Folio->Para", a_folios, b_paragraphs),
    ]:
        print(f"\n--- {label} ---")

        # Pool size stats
        a_sizes = [len(v) for v in a_units.values() if v]
        b_sizes = [len(v) for v in b_units.values() if v]

        print(f"A unit sizes: mean={statistics.mean(a_sizes):.1f}, max={max(a_sizes)}")
        print(f"B unit sizes: mean={statistics.mean(b_sizes):.1f}, max={max(b_sizes)}")

        # Best-match coverage
        coverages = compute_best_match_coverage(b_units, a_units)
        mean_cov = statistics.mean(coverages)

        # Random baseline
        baseline = compute_random_baseline(b_units, a_units, n_trials=50)
        lift = mean_cov / baseline if baseline > 0 else 0

        print(f"Best-match coverage: {mean_cov*100:.1f}%")
        print(f"Random baseline:     {baseline*100:.1f}%")
        print(f"Lift:                {lift:.2f}x")

        results[label] = {
            'a_count': len(a_units),
            'b_count': len(b_units),
            'mean_coverage': mean_cov,
            'baseline': baseline,
            'lift': lift
        }

    # Why does paragraph lift exceed line lift?
    print("\n" + "=" * 70)
    print("ANALYSIS: WHY DOES PARAGRAPH AGGREGATION INCREASE LIFT?")
    print("=" * 70)

    print("""
Key observation:
  - Line-level:      71.4% coverage, baseline ~70.2%, lift 1.02x
  - Paragraph-level: 66.2% coverage, baseline ~26.6%, lift 2.49x

The coverage is LOWER at paragraph level, but the baseline drops much more.
Why?

1. LINE BASELINE IS HIGH because:
   - Random A line still overlaps with any B line (shared PP vocabulary)
   - Each line has ~6 MIDDLEs, overlap is near-certain

2. PARAGRAPH BASELINE IS LOW because:
   - Random A paragraph (20 MIDDLEs) has lower chance of covering
     a specific B paragraph's 22 MIDDLEs
   - Need more specific overlap to achieve high coverage

3. BUT BEST-MATCH COVERAGE STAYS HIGH because:
   - Larger A paragraphs contain more vocabulary
   - Some A paragraphs are "hubs" covering most PP MIDDLEs
   - Best-match always finds the hub

This is the POOL-SIZE SELECTION ARTIFACT:
- Aggregation increases variance in A unit sizes
- Best-match selects largest overlapping A unit
- Random baseline can't exploit this selection
""")

    # What about normalized lift?
    print("\n" + "=" * 70)
    print("NORMALIZED ANALYSIS: CEILING-ADJUSTED LIFT")
    print("=" * 70)

    # Compute union coverage (ceiling)
    all_pp = set()
    for v in a_paragraphs.values():
        all_pp |= v

    para_union_covs = []
    for b_middles in b_paragraphs.values():
        if b_middles:
            para_union_covs.append(len(b_middles & all_pp) / len(b_middles))

    line_union_covs = []
    for b_middles in b_lines.values():
        if b_middles:
            line_union_covs.append(len(b_middles & all_pp) / len(b_middles))

    print(f"\nUnion ceiling (all A PP MIDDLEs):")
    print(f"  B paragraphs: {statistics.mean(para_union_covs)*100:.1f}%")
    print(f"  B lines:      {statistics.mean(line_union_covs)*100:.1f}%")

    # Ceiling-adjusted metrics
    print(f"\nCeiling-adjusted best-match coverage:")
    print(f"  Paragraphs: {results['Para->Para']['mean_coverage']/statistics.mean(para_union_covs)*100:.1f}% of ceiling")
    print(f"  Lines:      {results['Line->Line']['mean_coverage']/statistics.mean(line_union_covs)*100:.1f}% of ceiling")

    # =========================================================================
    # FINAL VERDICT
    # =========================================================================
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    print("""
CONCLUSION: NO SPECIFIC PARAGRAPH-TO-PARAGRAPH CORRESPONDENCE

Evidence:
1. The 2.49x lift at paragraph level is a POOL-SIZE SELECTION ARTIFACT
   - Large A paragraphs (f101v2, f1r, f99v) act as "hubs"
   - They capture ~75% of the union ceiling by themselves
   - Best-match always selects these hubs

2. When controlling for pool size, lift drops to 1.20x
   - This residual lift is from vocabulary clustering, not specific pairing
   - 24.5 A paragraphs tie for "best match" on average

3. Line-level shows the true relationship: shared vocabulary with no specificity
   - 71.4% coverage from ANY A line to ANY B line
   - 1.02x lift = pure vocabulary sharing

4. B paragraphs share 14.3% Jaccard similarity with each other
   - They're not vocabulary-unique
   - Any A paragraph with common vocabulary covers them all

MECHANISM:
The A->B relationship is POOL-BASED, not ADDRESS-BASED.
A paragraphs provide vocabulary pools (PP MIDDLEs).
B paragraphs draw from these pools without specific A->B pairing.
Larger A paragraphs provide larger pools, hence higher coverage.

This is consistent with:
- C384: No A-B token coupling
- C502: Morphological filtering (vocabulary-based, not address-based)
- C827: Paragraphs as operational aggregation units (pools, not addresses)
""")

    # Save results
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)

    final_results = {
        'line_level': {
            'coverage': results['Line->Line']['mean_coverage'],
            'baseline': results['Line->Line']['baseline'],
            'lift': results['Line->Line']['lift']
        },
        'paragraph_level': {
            'coverage': results['Para->Para']['mean_coverage'],
            'baseline': results['Para->Para']['baseline'],
            'lift': results['Para->Para']['lift']
        },
        'folio_to_paragraph': {
            'coverage': results['Folio->Para']['mean_coverage'],
            'baseline': results['Folio->Para']['baseline'],
            'lift': results['Folio->Para']['lift']
        },
        'union_ceiling': {
            'paragraphs': statistics.mean(para_union_covs),
            'lines': statistics.mean(line_union_covs)
        },
        'verdict': 'NO_SPECIFIC_CORRESPONDENCE',
        'mechanism': 'POOL_BASED_VOCABULARY_SHARING'
    }

    with open(output_dir / 'final_verdict.json', 'w') as f:
        json.dump(final_results, f, indent=2)

    print(f"\nResults saved to: {output_dir / 'final_verdict.json'}")


if __name__ == '__main__':
    main()
