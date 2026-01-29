#!/usr/bin/env python3
"""
Rigorous test for paragraph correspondence using proper null models.

The issue with the previous test: random shuffling of A paragraph assignments
doesn't control for pool size effects. A better null model:

1. POOL-SIZE-MATCHED BASELINE: For each B paragraph, match to A paragraphs
   with similar pool sizes, then shuffle within size bands.

2. MIDDLE-OVERLAP NULL: Shuffle the MIDDLEs themselves (break A paragraph
   structure while preserving total PP vocabulary).

3. EMPIRICAL SPECIFICITY: For each B paragraph, count how many A paragraphs
   achieve the best-match coverage. If there's specificity, few A paragraphs
   should tie for best.
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


def extract_paragraphs_a():
    tx = Transcript()
    morph = Morphology()

    folio_lines = defaultdict(lambda: defaultdict(list))
    for token in tx.currier_a():
        if token.word:
            folio_lines[token.folio][token.line].append(token)

    paragraphs = []

    for folio in sorted(folio_lines.keys()):
        lines_dict = folio_lines[folio]
        sorted_lines = sorted(lines_dict.keys(), key=lambda x: int(x) if x.isdigit() else 999)

        current_para = None
        para_idx = 0

        for line_num in sorted_lines:
            tokens = lines_dict[line_num]
            first_token = tokens[0] if tokens else None
            is_para_start = first_token and is_gallows_initial(first_token.word)

            if is_para_start:
                if current_para is not None:
                    paragraphs.append(current_para)
                current_para = {
                    'folio': folio,
                    'para_idx': para_idx,
                    'tokens': list(tokens),
                    'pp_middles': set()
                }
                para_idx += 1
            elif current_para is not None:
                current_para['tokens'].extend(tokens)
            else:
                current_para = {
                    'folio': folio,
                    'para_idx': para_idx,
                    'tokens': list(tokens),
                    'pp_middles': set()
                }
                para_idx += 1

        if current_para is not None:
            paragraphs.append(current_para)

    for para in paragraphs:
        for token in para['tokens']:
            m = morph.extract(token.word)
            if m.middle and m.middle in PP_MIDDLES:
                para['pp_middles'].add(m.middle)
        para['id'] = f"{para['folio']}_p{para['para_idx']}"

    return paragraphs


def extract_paragraphs_b():
    tx = Transcript()
    morph = Morphology()

    folio_paras = defaultdict(lambda: defaultdict(list))
    current_para_idx = defaultdict(int)

    for token in tx.currier_b():
        if not token.word:
            continue
        folio = token.folio
        if token.par_initial:
            current_para_idx[folio] += 1
        para_idx = current_para_idx[folio]
        folio_paras[folio][para_idx].append(token)

    paragraphs = []

    for folio in sorted(folio_paras.keys()):
        for para_idx in sorted(folio_paras[folio].keys()):
            tokens = folio_paras[folio][para_idx]
            para = {
                'folio': folio,
                'para_idx': para_idx,
                'tokens': tokens,
                'middles': set(),
                'id': f"{folio}_p{para_idx}"
            }
            for token in tokens:
                m = morph.extract(token.word)
                if m.middle:
                    para['middles'].add(m.middle)
            paragraphs.append(para)

    return paragraphs


def compute_coverage(b_middles: set, a_middles: set) -> float:
    if not b_middles:
        return 0.0
    return len(b_middles & a_middles) / len(b_middles)


def main():
    print("=" * 70)
    print("RIGOROUS BASELINE TESTS FOR PARAGRAPH CORRESPONDENCE")
    print("=" * 70)

    a_paragraphs = extract_paragraphs_a()
    b_paragraphs = extract_paragraphs_b()

    print(f"\nA paragraphs: {len(a_paragraphs)}")
    print(f"B paragraphs: {len(b_paragraphs)}")

    # =========================================================================
    # TEST 1: How many A paragraphs achieve best coverage for each B paragraph?
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST 1: SPECIFICITY OF BEST MATCHES")
    print("=" * 70)

    print("""
For each B paragraph, count how many A paragraphs are within 1% of the
best coverage. If there's specific correspondence, this should be small.
If it's just pool-based, many A paragraphs should tie.
""")

    tie_counts = []
    within_5pct_counts = []

    for b_para in b_paragraphs:
        if not b_para['middles']:
            continue

        coverages = []
        for a_para in a_paragraphs:
            if not a_para['pp_middles']:
                continue
            cov = compute_coverage(b_para['middles'], a_para['pp_middles'])
            coverages.append((a_para['id'], cov))

        if not coverages:
            continue

        best_cov = max(c[1] for c in coverages)

        # Count near-ties
        within_1pct = sum(1 for _, c in coverages if c >= best_cov - 0.01)
        within_5pct = sum(1 for _, c in coverages if c >= best_cov - 0.05)

        tie_counts.append(within_1pct)
        within_5pct_counts.append(within_5pct)

    print(f"A paragraphs within 1% of best match:")
    print(f"  Mean:   {statistics.mean(tie_counts):.1f}")
    print(f"  Median: {statistics.median(tie_counts):.0f}")
    print(f"  Max:    {max(tie_counts)}")

    print(f"\nA paragraphs within 5% of best match:")
    print(f"  Mean:   {statistics.mean(within_5pct_counts):.1f}")
    print(f"  Median: {statistics.median(within_5pct_counts):.0f}")
    print(f"  Max:    {max(within_5pct_counts)}")

    # Unique best match rate
    unique_best = sum(1 for t in tie_counts if t == 1)
    print(f"\nB paragraphs with unique best match: {unique_best} ({unique_best/len(tie_counts)*100:.1f}%)")

    # =========================================================================
    # TEST 2: Pool-size controlled baseline
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST 2: POOL-SIZE-MATCHED RANDOM BASELINE")
    print("=" * 70)

    print("""
For each B paragraph, pick a random A paragraph with similar pool size
to the actual best match. If the lift is from pool size alone, this
baseline should match the observed coverage.
""")

    # Group A paragraphs by pool size (bands of 5)
    a_by_size_band = defaultdict(list)
    for a_para in a_paragraphs:
        band = len(a_para['pp_middles']) // 5 * 5
        a_by_size_band[band].append(a_para)

    actual_coverages = []
    matched_baseline_coverages = []

    for b_para in b_paragraphs:
        if not b_para['middles']:
            continue

        # Find best A paragraph
        best_cov = 0.0
        best_a = None
        for a_para in a_paragraphs:
            if not a_para['pp_middles']:
                continue
            cov = compute_coverage(b_para['middles'], a_para['pp_middles'])
            if cov > best_cov:
                best_cov = cov
                best_a = a_para

        if best_a is None:
            continue

        actual_coverages.append(best_cov)

        # Pick random A with similar pool size
        band = len(best_a['pp_middles']) // 5 * 5
        candidates = a_by_size_band.get(band, [])
        if not candidates:
            # Fall back to nearest band
            for offset in [5, -5, 10, -10]:
                candidates = a_by_size_band.get(band + offset, [])
                if candidates:
                    break

        if candidates:
            random_a = random.choice(candidates)
            random_cov = compute_coverage(b_para['middles'], random_a['pp_middles'])
            matched_baseline_coverages.append(random_cov)

    print(f"\nActual best-match coverage:        {statistics.mean(actual_coverages)*100:.1f}%")
    print(f"Pool-size-matched random baseline: {statistics.mean(matched_baseline_coverages)*100:.1f}%")
    lift = statistics.mean(actual_coverages) / statistics.mean(matched_baseline_coverages)
    print(f"Lift over size-matched baseline:   {lift:.2f}x")

    # =========================================================================
    # TEST 3: Breakdown by B paragraph size
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST 3: COVERAGE BY B PARAGRAPH SIZE")
    print("=" * 70)

    # Group B paragraphs by MIDDLE count
    b_small = [p for p in b_paragraphs if len(p['middles']) <= 15]
    b_medium = [p for p in b_paragraphs if 15 < len(p['middles']) <= 25]
    b_large = [p for p in b_paragraphs if len(p['middles']) > 25]

    print(f"\nB paragraphs by size:")
    print(f"  Small (<=15 MIDDLEs):  {len(b_small)}")
    print(f"  Medium (16-25):        {len(b_medium)}")
    print(f"  Large (>25):           {len(b_large)}")

    for label, b_set in [("Small", b_small), ("Medium", b_medium), ("Large", b_large)]:
        coverages = []
        for b_para in b_set:
            if not b_para['middles']:
                continue
            best_cov = 0.0
            for a_para in a_paragraphs:
                if not a_para['pp_middles']:
                    continue
                cov = compute_coverage(b_para['middles'], a_para['pp_middles'])
                if cov > best_cov:
                    best_cov = cov
            coverages.append(best_cov)

        if coverages:
            print(f"\n  {label}: mean coverage = {statistics.mean(coverages)*100:.1f}%")

    # =========================================================================
    # TEST 4: What if we match B paragraphs to UNION of all A paragraphs?
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST 4: UNION COVERAGE CEILING")
    print("=" * 70)

    all_pp = set()
    for a_para in a_paragraphs:
        all_pp |= a_para['pp_middles']

    union_coverages = []
    for b_para in b_paragraphs:
        if not b_para['middles']:
            continue
        cov = compute_coverage(b_para['middles'], all_pp)
        union_coverages.append(cov)

    print(f"\nTotal PP vocabulary (union of all A): {len(all_pp)}")
    print(f"Mean coverage against full union:     {statistics.mean(union_coverages)*100:.1f}%")

    # What fraction of best-match coverage is from the union ceiling?
    ratio = statistics.mean(actual_coverages) / statistics.mean(union_coverages)
    print(f"Best-match / Union ratio:             {ratio:.2f}")

    # =========================================================================
    # TEST 5: B vocabulary uniqueness
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST 5: B PARAGRAPH VOCABULARY UNIQUENESS")
    print("=" * 70)

    print("""
If B paragraphs have unique vocabularies, specific A matching might matter.
If they all share the same vocabulary, any large A paragraph works equally.
""")

    # Compute Jaccard similarity between B paragraphs
    b_pairs = random.sample([(i, j) for i in range(len(b_paragraphs))
                             for j in range(i+1, len(b_paragraphs))], min(1000, len(b_paragraphs)*(len(b_paragraphs)-1)//2))

    jaccards = []
    for i, j in b_pairs:
        b1 = b_paragraphs[i]['middles']
        b2 = b_paragraphs[j]['middles']
        if b1 and b2:
            jaccard = len(b1 & b2) / len(b1 | b2)
            jaccards.append(jaccard)

    print(f"Mean Jaccard similarity between B paragraphs: {statistics.mean(jaccards)*100:.1f}%")

    # =========================================================================
    # CONCLUSION
    # =========================================================================
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    print(f"""
Key findings:

1. SPECIFICITY: {unique_best} ({unique_best/len(tie_counts)*100:.1f}%) B paragraphs have a unique best A match.
   Mean A paragraphs within 1% of best: {statistics.mean(tie_counts):.1f}

2. POOL-SIZE CONTROL: When controlling for pool size, lift drops to {lift:.2f}x.

3. UNION CEILING: Best-match achieves {ratio*100:.0f}% of union ceiling.
   The "best" A paragraph captures {ratio*100:.0f}% of what ALL A paragraphs together could provide.

4. B VOCABULARY OVERLAP: B paragraphs share {statistics.mean(jaccards)*100:.1f}% vocabulary (Jaccard).

INTERPRETATION:
""")

    if lift < 1.15:
        print("""
The pool-size-matched baseline eliminates most of the lift. The apparent
2.49x lift is driven by pool size selection: best-match always picks the
largest A paragraph that overlaps well, which happens to be similar
across all B paragraphs.

NO SPECIFIC PARAGRAPH-TO-PARAGRAPH CORRESPONDENCE EXISTS.
The relationship is VOCABULARY POOL SELECTION, not ADDRESS-BASED MAPPING.
""")
    elif statistics.mean(tie_counts) > 5:
        print("""
Despite some lift remaining after pool-size control, many A paragraphs
achieve similar coverage (mean {:.1f} ties). This suggests the lift comes
from "good overlap" rather than specific pairing.

WEAK CORRESPONDENCE AT BEST - likely driven by vocabulary clustering
rather than specific A->B mapping.
""".format(statistics.mean(tie_counts)))
    else:
        print("""
The lift persists after pool-size control AND most B paragraphs have
unique or near-unique best matches. This suggests GENUINE SPECIFICITY
in the A->B paragraph relationship.

FURTHER INVESTIGATION NEEDED to characterize the nature of this
correspondence.
""")


if __name__ == '__main__':
    main()
