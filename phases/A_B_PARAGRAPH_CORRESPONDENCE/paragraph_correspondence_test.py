#!/usr/bin/env python3
"""
Test whether specific Currier A paragraphs have vocabulary correspondence
to specific Currier B paragraphs.

Context:
- A paragraphs: ~285, gallows-initial, RI header + PP body, ~5 lines each
- B paragraphs: ~535-585, gallows-initial, HT header + classified body, ~4.5 lines each
- Earlier line-to-line test showed no correspondence (just shared vocabulary, 1.02x lift)
- Now testing at paragraph level since both systems use paragraphs as operational units

Using scripts/voynich.py and class_token_map.json for classification.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import random
import statistics

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# CONFIGURATION
# ============================================================
GALLOWS = {'k', 't', 'p', 'f'}  # Paragraph boundary markers

# Load class token map for B classification
CLASS_MAP_PATH = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'

with open(CLASS_MAP_PATH) as f:
    CLASS_DATA = json.load(f)

# HT tokens are those in specific role categories (excluding body vocabulary)
# For this analysis, we want to EXCLUDE HT from B paragraph vocabulary
# HT roles are: CORE_CONTROL, FLOW_OPERATOR, ENERGY_OPERATOR based on C404
# Actually, for coverage, let's just extract MIDDLEs from all B tokens
# and compare to PP MIDDLEs from A paragraphs

# Load RI/PP classification for A tokens
RI_PP_PATH = PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json'
with open(RI_PP_PATH) as f:
    ri_pp_data = json.load(f)

RI_MIDDLES = set(ri_pp_data['a_exclusive_middles'])
PP_MIDDLES = set(ri_pp_data['a_shared_middles'])


def is_gallows_initial(word: str) -> bool:
    """Check if word starts with a gallows character."""
    return word and word[0] in GALLOWS


def extract_paragraphs_a():
    """
    Extract Currier A paragraphs as defined by C827:
    A paragraph starts with a gallows-initial line and continues until
    the next gallows-initial line.

    Returns list of dicts with:
    - folio: str
    - para_idx: int (0-indexed within folio)
    - lines: list of line numbers
    - tokens: list of Token objects
    - pp_middles: set of PP MIDDLEs (excluding RI)
    """
    tx = Transcript()
    morph = Morphology()

    # Group tokens by folio and line
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

            # Check if line is gallows-initial
            first_token = tokens[0] if tokens else None
            is_para_start = first_token and is_gallows_initial(first_token.word)

            if is_para_start:
                # Save current paragraph if exists
                if current_para is not None:
                    paragraphs.append(current_para)

                # Start new paragraph
                current_para = {
                    'folio': folio,
                    'para_idx': para_idx,
                    'lines': [line_num],
                    'tokens': list(tokens),
                    'pp_middles': set()
                }
                para_idx += 1
            elif current_para is not None:
                # Add to current paragraph
                current_para['lines'].append(line_num)
                current_para['tokens'].extend(tokens)
            else:
                # Before first gallows-initial line - create implicit paragraph
                current_para = {
                    'folio': folio,
                    'para_idx': para_idx,
                    'lines': [line_num],
                    'tokens': list(tokens),
                    'pp_middles': set()
                }
                para_idx += 1

        # Don't forget last paragraph
        if current_para is not None:
            paragraphs.append(current_para)

    # Extract PP MIDDLEs for each paragraph
    for para in paragraphs:
        for token in para['tokens']:
            m = morph.extract(token.word)
            if m.middle and m.middle in PP_MIDDLES:
                para['pp_middles'].add(m.middle)

    return paragraphs


def extract_paragraphs_b():
    """
    Extract Currier B paragraphs using par_initial/par_final flags.

    Returns list of dicts with:
    - folio: str
    - para_idx: int (0-indexed within folio)
    - lines: list of line numbers
    - tokens: list of Token objects
    - middles: set of all MIDDLEs (we'll compare against A's PP MIDDLEs)
    """
    tx = Transcript()
    morph = Morphology()

    # Group tokens by folio and paragraph
    folio_paras = defaultdict(lambda: defaultdict(list))
    current_para_idx = defaultdict(int)

    for token in tx.currier_b():
        if not token.word:
            continue

        folio = token.folio

        if token.par_initial:
            # Start new paragraph
            current_para_idx[folio] += 1

        para_idx = current_para_idx[folio]
        folio_paras[folio][para_idx].append(token)

    paragraphs = []

    for folio in sorted(folio_paras.keys()):
        for para_idx in sorted(folio_paras[folio].keys()):
            tokens = folio_paras[folio][para_idx]
            lines = sorted(set(t.line for t in tokens))

            para = {
                'folio': folio,
                'para_idx': para_idx,
                'lines': lines,
                'tokens': tokens,
                'middles': set()
            }

            # Extract all MIDDLEs
            for token in tokens:
                m = morph.extract(token.word)
                if m.middle:
                    para['middles'].add(m.middle)

            paragraphs.append(para)

    return paragraphs


def compute_coverage(b_middles: set, a_middles: set) -> float:
    """
    Compute coverage: what fraction of B paragraph's middles are
    found in the A paragraph's PP middles.
    """
    if not b_middles:
        return 0.0
    return len(b_middles & a_middles) / len(b_middles)


def compute_best_matches(a_paragraphs, b_paragraphs):
    """
    For each B paragraph, find the best matching A paragraph.

    Returns:
    - List of (b_para, best_a_para, coverage) tuples
    - Dict mapping A paragraph ID to count of B paragraphs it best-matches
    """
    results = []
    a_match_counts = defaultdict(int)

    for b_para in b_paragraphs:
        if not b_para['middles']:
            continue

        best_coverage = 0.0
        best_a = None

        for a_para in a_paragraphs:
            if not a_para['pp_middles']:
                continue

            coverage = compute_coverage(b_para['middles'], a_para['pp_middles'])
            if coverage > best_coverage:
                best_coverage = coverage
                best_a = a_para

        if best_a is not None:
            a_id = f"{best_a['folio']}_p{best_a['para_idx']}"
            a_match_counts[a_id] += 1
            results.append((b_para, best_a, best_coverage))

    return results, a_match_counts


def compute_random_baseline(a_paragraphs, b_paragraphs, n_trials=100):
    """
    Compute random baseline by shuffling A paragraph assignments.
    """
    coverages = []

    for _ in range(n_trials):
        # Shuffle A paragraphs
        shuffled_a = list(a_paragraphs)
        random.shuffle(shuffled_a)

        trial_coverages = []
        for i, b_para in enumerate(b_paragraphs):
            if not b_para['middles']:
                continue
            # Random A paragraph
            a_para = shuffled_a[i % len(shuffled_a)]
            coverage = compute_coverage(b_para['middles'], a_para['pp_middles'])
            trial_coverages.append(coverage)

        if trial_coverages:
            coverages.append(statistics.mean(trial_coverages))

    return statistics.mean(coverages) if coverages else 0.0


def analyze_match_clustering(match_results, a_match_counts):
    """
    Analyze whether best matches cluster on specific A paragraphs.
    """
    total_b_matched = len(match_results)
    total_a_used = len(a_match_counts)

    # Distribution statistics
    counts = list(a_match_counts.values())
    if not counts:
        return None

    return {
        'total_b_paragraphs_matched': total_b_matched,
        'unique_a_paragraphs_used': total_a_used,
        'mean_b_per_a': statistics.mean(counts),
        'median_b_per_a': statistics.median(counts),
        'max_b_per_a': max(counts),
        'a_with_single_match': sum(1 for c in counts if c == 1),
        'a_with_5plus_matches': sum(1 for c in counts if c >= 5),
        'a_with_10plus_matches': sum(1 for c in counts if c >= 10),
        'concentration_ratio': sum(sorted(counts, reverse=True)[:10]) / total_b_matched if total_b_matched else 0
    }


def main():
    print("=" * 70)
    print("PARAGRAPH-TO-PARAGRAPH VOCABULARY CORRESPONDENCE TEST")
    print("=" * 70)

    # Extract paragraphs
    print("\nExtracting Currier A paragraphs...")
    a_paragraphs = extract_paragraphs_a()
    print(f"  Found {len(a_paragraphs)} A paragraphs")

    # Statistics on A paragraphs
    a_with_pp = [p for p in a_paragraphs if p['pp_middles']]
    mean_pp_per_a = statistics.mean(len(p['pp_middles']) for p in a_paragraphs)
    print(f"  {len(a_with_pp)} have PP MIDDLEs")
    print(f"  Mean PP MIDDLEs per paragraph: {mean_pp_per_a:.1f}")

    print("\nExtracting Currier B paragraphs...")
    b_paragraphs = extract_paragraphs_b()
    print(f"  Found {len(b_paragraphs)} B paragraphs")

    b_with_middles = [p for p in b_paragraphs if p['middles']]
    mean_middles_per_b = statistics.mean(len(p['middles']) for p in b_paragraphs if p['middles'])
    print(f"  {len(b_with_middles)} have MIDDLEs")
    print(f"  Mean unique MIDDLEs per paragraph: {mean_middles_per_b:.1f}")

    # Compute best matches
    print("\nComputing best matches...")
    match_results, a_match_counts = compute_best_matches(a_paragraphs, b_paragraphs)

    # Coverage statistics
    coverages = [r[2] for r in match_results]

    print("\n" + "=" * 70)
    print("COVERAGE RESULTS")
    print("=" * 70)

    print(f"\nMatched {len(match_results)} B paragraphs to best A paragraphs")
    print(f"\nBest-match coverage statistics:")
    print(f"  Mean:   {statistics.mean(coverages)*100:.1f}%")
    print(f"  Median: {statistics.median(coverages)*100:.1f}%")
    print(f"  Std:    {statistics.stdev(coverages)*100:.1f}%")
    print(f"  Min:    {min(coverages)*100:.1f}%")
    print(f"  Max:    {max(coverages)*100:.1f}%")

    # Coverage thresholds
    above_50 = sum(1 for c in coverages if c > 0.5)
    above_70 = sum(1 for c in coverages if c > 0.7)
    above_90 = sum(1 for c in coverages if c > 0.9)

    print(f"\n  B paragraphs with >50% coverage: {above_50} ({above_50/len(coverages)*100:.1f}%)")
    print(f"  B paragraphs with >70% coverage: {above_70} ({above_70/len(coverages)*100:.1f}%)")
    print(f"  B paragraphs with >90% coverage: {above_90} ({above_90/len(coverages)*100:.1f}%)")

    # Random baseline
    print("\nComputing random baseline (100 trials)...")
    random_baseline = compute_random_baseline(a_paragraphs, b_paragraphs, n_trials=100)
    print(f"  Random baseline mean coverage: {random_baseline*100:.1f}%")

    lift = statistics.mean(coverages) / random_baseline if random_baseline > 0 else float('inf')
    print(f"\n  LIFT over random: {lift:.2f}x")

    # Clustering analysis
    print("\n" + "=" * 70)
    print("MATCH CLUSTERING ANALYSIS")
    print("=" * 70)

    clustering = analyze_match_clustering(match_results, a_match_counts)
    if clustering:
        print(f"\nUnique A paragraphs used as best-match: {clustering['unique_a_paragraphs_used']}")
        print(f"Ratio (B paragraphs / unique A matches): {clustering['total_b_paragraphs_matched'] / clustering['unique_a_paragraphs_used']:.1f}")
        print(f"\nB paragraphs per A paragraph:")
        print(f"  Mean:   {clustering['mean_b_per_a']:.1f}")
        print(f"  Median: {clustering['median_b_per_a']:.0f}")
        print(f"  Max:    {clustering['max_b_per_a']}")
        print(f"\nA paragraphs with single B match: {clustering['a_with_single_match']}")
        print(f"A paragraphs with 5+ B matches:   {clustering['a_with_5plus_matches']}")
        print(f"A paragraphs with 10+ B matches:  {clustering['a_with_10plus_matches']}")
        print(f"\nTop-10 A concentration ratio: {clustering['concentration_ratio']*100:.1f}% of B matches")

    # Folio analysis
    print("\n" + "=" * 70)
    print("FOLIO-LEVEL ANALYSIS")
    print("=" * 70)

    # Do best-matching A paragraphs come from specific folios?
    a_folio_counts = defaultdict(int)
    for a_id, count in a_match_counts.items():
        folio = a_id.split('_p')[0]
        a_folio_counts[folio] += count

    top_a_folios = sorted(a_folio_counts.items(), key=lambda x: -x[1])[:10]
    print("\nTop 10 A folios by B paragraph matches:")
    for folio, count in top_a_folios:
        pct = count / len(match_results) * 100
        print(f"  {folio}: {count} matches ({pct:.1f}%)")

    # Line-level comparison context
    print("\n" + "=" * 70)
    print("COMPARISON TO LINE-LEVEL RESULTS")
    print("=" * 70)

    print("""
Previous line-level analysis (C734):
  Best-match coverage: 71.4%
  Random baseline:     70.2%
  Lift:                1.02x

Current paragraph-level results:
  Best-match coverage: {mean:.1f}%
  Random baseline:     {baseline:.1f}%
  Lift:                {lift:.2f}x
""".format(
        mean=statistics.mean(coverages)*100,
        baseline=random_baseline*100,
        lift=lift
    ))

    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)

    if lift < 1.1:
        print("""
CONCLUSION: NO PARAGRAPH-TO-PARAGRAPH CORRESPONDENCE

Like line-level analysis, paragraph-level matching shows minimal lift
over random baseline. This means:

1. A and B share vocabulary (PP MIDDLEs appear in both systems)
2. But there's no SPECIFIC correspondence between A paragraphs and B paragraphs
3. Any A paragraph with sufficient PP vocabulary can cover any B paragraph equally well
4. The relationship is POOL-BASED, not ADDRESS-BASED

The shared vocabulary creates high absolute coverage, but the lack of lift
indicates no structured A->B paragraph mapping exists.
""")
    else:
        print(f"""
FINDING: POSSIBLE PARAGRAPH-LEVEL CORRESPONDENCE

Lift of {lift:.2f}x over random baseline suggests some paragraph-level
specificity beyond shared vocabulary. Further investigation needed to
characterize the nature of this correspondence.
""")

    # Save results
    results = {
        'a_paragraph_count': len(a_paragraphs),
        'b_paragraph_count': len(b_paragraphs),
        'matched_b_count': len(match_results),
        'coverage_mean': statistics.mean(coverages),
        'coverage_median': statistics.median(coverages),
        'coverage_std': statistics.stdev(coverages),
        'coverage_above_50_pct': above_50 / len(coverages),
        'coverage_above_70_pct': above_70 / len(coverages),
        'coverage_above_90_pct': above_90 / len(coverages),
        'random_baseline': random_baseline,
        'lift_over_random': lift,
        'clustering': clustering,
        'top_a_folios': dict(top_a_folios)
    }

    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / 'paragraph_correspondence.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_dir / 'paragraph_correspondence.json'}")


if __name__ == '__main__':
    main()
