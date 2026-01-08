"""
CAS-XREF: Cross-Reference Structure Analysis

Research Question: How do Currier A (catalog) and Currier B (procedures)
structurally relate?

Hypotheses:
H1: 161 balanced tokens serve as cross-reference points
H2: CT-in-B represents material references to catalog
H3: B folios contain embedded A-references in predictable patterns
H4: A sections (H, P, T) map to B folio clusters
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

project_root = Path(__file__).parent.parent.parent
MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Known Currier A sections
A_SECTIONS = {'H', 'P', 'T'}

def load_full_data():
    """Load all data with folio, section, line, and position information."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    a_data = []  # (token, folio, section, line, word_pos)
    b_data = []

    line_positions = defaultdict(int)  # Track position within each line

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                lang = parts[6].strip('"').strip()
                word = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if word:
                    key = (folio, line_num)
                    pos = line_positions[key]
                    line_positions[key] += 1

                    entry = (word, folio, section, line_num, pos)
                    if lang == 'A':
                        a_data.append(entry)
                    elif lang == 'B':
                        b_data.append(entry)

    return a_data, b_data


def get_balanced_tokens(a_data, b_data, min_count=10, ratio_range=(0.5, 2.0)):
    """Identify tokens balanced between A and B."""
    a_tokens = Counter(t for t, f, s, l, p in a_data)
    b_tokens = Counter(t for t, f, s, l, p in b_data)

    balanced = []
    for token in set(a_tokens.keys()) & set(b_tokens.keys()):
        a_c = a_tokens[token]
        b_c = b_tokens[token]
        if a_c >= min_count and b_c >= min_count:
            ratio = b_c / a_c
            if ratio_range[0] <= ratio <= ratio_range[1]:
                balanced.append((token, a_c, b_c, ratio))

    return sorted(balanced, key=lambda x: -(x[1] + x[2]))


def test_h1_balanced_positions(a_data, b_data):
    """
    H1: Balanced tokens as cross-reference points

    Test: Do balanced tokens appear in predictable positions
    (line-initial, section boundaries) suggesting indexing function?
    """
    print("\n" + "=" * 80)
    print("H1: BALANCED TOKENS AS CROSS-REFERENCE POINTS")
    print("=" * 80)

    balanced = get_balanced_tokens(a_data, b_data)
    balanced_set = {t for t, a, b, r in balanced}

    print(f"\nBalanced tokens: {len(balanced)}")

    # Group data by lines
    a_lines = defaultdict(list)
    b_lines = defaultdict(list)

    for t, f, s, l, p in a_data:
        a_lines[(f, l)].append((t, p))
    for t, f, s, l, p in b_data:
        b_lines[(f, l)].append((t, p))

    # Analyze position of balanced tokens
    results = {'A': {'line_initial': 0, 'line_middle': 0, 'line_final': 0, 'total': 0},
               'B': {'line_initial': 0, 'line_middle': 0, 'line_final': 0, 'total': 0}}

    # Background rates (all tokens)
    bg_results = {'A': {'line_initial': 0, 'total': 0},
                  'B': {'line_initial': 0, 'total': 0}}

    for (f, l), tokens in a_lines.items():
        if len(tokens) < 2:
            continue
        for t, p in tokens:
            bg_results['A']['total'] += 1
            if p == 0:
                bg_results['A']['line_initial'] += 1

            if t in balanced_set:
                results['A']['total'] += 1
                if p == 0:
                    results['A']['line_initial'] += 1
                elif p == len(tokens) - 1:
                    results['A']['line_final'] += 1
                else:
                    results['A']['line_middle'] += 1

    for (f, l), tokens in b_lines.items():
        if len(tokens) < 2:
            continue
        for t, p in tokens:
            bg_results['B']['total'] += 1
            if p == 0:
                bg_results['B']['line_initial'] += 1

            if t in balanced_set:
                results['B']['total'] += 1
                if p == 0:
                    results['B']['line_initial'] += 1
                elif p == len(tokens) - 1:
                    results['B']['line_final'] += 1
                else:
                    results['B']['line_middle'] += 1

    print(f"\n## POSITION ANALYSIS")
    print(f"\nBalanced token positions in A:")
    for pos in ['line_initial', 'line_middle', 'line_final']:
        pct = 100 * results['A'][pos] / results['A']['total'] if results['A']['total'] > 0 else 0
        print(f"  {pos}: {results['A'][pos]} ({pct:.1f}%)")

    print(f"\nBalanced token positions in B:")
    for pos in ['line_initial', 'line_middle', 'line_final']:
        pct = 100 * results['B'][pos] / results['B']['total'] if results['B']['total'] > 0 else 0
        print(f"  {pos}: {results['B'][pos]} ({pct:.1f}%)")

    # Compare to background rate
    a_bg_rate = bg_results['A']['line_initial'] / bg_results['A']['total'] if bg_results['A']['total'] > 0 else 0
    b_bg_rate = bg_results['B']['line_initial'] / bg_results['B']['total'] if bg_results['B']['total'] > 0 else 0
    a_bal_rate = results['A']['line_initial'] / results['A']['total'] if results['A']['total'] > 0 else 0
    b_bal_rate = results['B']['line_initial'] / results['B']['total'] if results['B']['total'] > 0 else 0

    print(f"\n## LINE-INITIAL ENRICHMENT")
    print(f"  A background rate: {100*a_bg_rate:.1f}%")
    print(f"  A balanced rate: {100*a_bal_rate:.1f}%")
    print(f"  A enrichment: {a_bal_rate/a_bg_rate:.2f}x" if a_bg_rate > 0 else "  A enrichment: N/A")
    print(f"\n  B background rate: {100*b_bg_rate:.1f}%")
    print(f"  B balanced rate: {100*b_bal_rate:.1f}%")
    print(f"  B enrichment: {b_bal_rate/b_bg_rate:.2f}x" if b_bg_rate > 0 else "  B enrichment: N/A")

    # Chi-square test for line-initial enrichment
    for system, res, bg in [('A', results['A'], bg_results['A']), ('B', results['B'], bg_results['B'])]:
        observed = [res['line_initial'], res['total'] - res['line_initial']]
        expected_initial = res['total'] * (bg['line_initial'] / bg['total']) if bg['total'] > 0 else 0
        expected = [expected_initial, res['total'] - expected_initial]

        if expected_initial > 5:  # Chi-square validity
            chi2, p = stats.chisquare(observed, expected)
            print(f"\n  {system} chi-square: chi2={chi2:.2f}, p={p:.4f}")

    # Analyze by prefix
    print(f"\n## BALANCED TOKENS BY PREFIX")
    prefix_counts = defaultdict(lambda: {'A_initial': 0, 'A_total': 0, 'B_initial': 0, 'B_total': 0})

    for t, a_c, b_c, ratio in balanced:
        prefix = 'other'
        for p in MARKER_PREFIXES:
            if t.startswith(p):
                prefix = p
                break

        # Count in A
        for tok, fol, sec, lin, pos in a_data:
            if tok == t:
                prefix_counts[prefix]['A_total'] += 1
                if pos == 0:
                    prefix_counts[prefix]['A_initial'] += 1

        # Count in B
        for tok, fol, sec, lin, pos in b_data:
            if tok == t:
                prefix_counts[prefix]['B_total'] += 1
                if pos == 0:
                    prefix_counts[prefix]['B_initial'] += 1

    print(f"{'Prefix':<10} {'A_init%':>10} {'B_init%':>10} {'A_total':>10} {'B_total':>10}")
    print("-" * 50)
    for prefix in MARKER_PREFIXES + ['other']:
        c = prefix_counts[prefix]
        if c['A_total'] > 0 or c['B_total'] > 0:
            a_pct = 100 * c['A_initial'] / c['A_total'] if c['A_total'] > 0 else 0
            b_pct = 100 * c['B_initial'] / c['B_total'] if c['B_total'] > 0 else 0
            print(f"{prefix:<10} {a_pct:>9.1f}% {b_pct:>9.1f}% {c['A_total']:>10} {c['B_total']:>10}")

    return {
        'balanced_count': len(balanced),
        'A_initial_rate': a_bal_rate,
        'B_initial_rate': b_bal_rate,
        'A_enrichment': a_bal_rate / a_bg_rate if a_bg_rate > 0 else None,
        'B_enrichment': b_bal_rate / b_bg_rate if b_bg_rate > 0 else None
    }


def test_h2_ct_in_b(a_data, b_data):
    """
    H2: CT-in-B = Material Reference

    Test: Are CT tokens in B clustered at specific positions,
    co-located with specific instruction classes, or more common
    in certain program types?
    """
    print("\n" + "=" * 80)
    print("H2: CT-IN-B AS MATERIAL REFERENCES")
    print("=" * 80)

    # Get CT tokens in B
    ct_in_b = [(t, f, s, l, p) for t, f, s, l, p in b_data if t.startswith('ct')]

    print(f"\nCT occurrences in B: {len(ct_in_b)}")

    # Group B by lines
    b_lines = defaultdict(list)
    for t, f, s, l, p in b_data:
        b_lines[(f, l)].append((t, p))

    # Position within line
    ct_rel_positions = []
    for t, f, s, l, p in ct_in_b:
        line_tokens = b_lines[(f, l)]
        if len(line_tokens) > 1:
            rel_pos = p / (len(line_tokens) - 1)
            ct_rel_positions.append(rel_pos)

    print(f"\n## CT POSITION WITHIN B LINES")
    if ct_rel_positions:
        print(f"  Mean relative position: {np.mean(ct_rel_positions):.3f}")
        print(f"  Std: {np.std(ct_rel_positions):.3f}")
        print(f"  (0.0 = line start, 1.0 = line end)")

        # Distribution bins
        bins = [0, 0.25, 0.5, 0.75, 1.0]
        hist, _ = np.histogram(ct_rel_positions, bins=bins)
        print(f"\n  Position distribution:")
        for i, count in enumerate(hist):
            print(f"    {bins[i]:.2f}-{bins[i+1]:.2f}: {count:4d} ({100*count/len(ct_rel_positions):5.1f}%)")

    # What precedes CT in B?
    print(f"\n## TOKENS IMMEDIATELY BEFORE CT IN B")
    preceding = []
    for t, f, s, l, p in ct_in_b:
        line_tokens = b_lines[(f, l)]
        if p > 0:
            prev_token = line_tokens[p-1][0]
            preceding.append(prev_token)

    preceding_counts = Counter(preceding)
    print(f"  Most common preceding tokens:")
    for tok, count in preceding_counts.most_common(10):
        print(f"    {tok}: {count}")

    # What follows CT in B?
    print(f"\n## TOKENS IMMEDIATELY AFTER CT IN B")
    following = []
    for t, f, s, l, p in ct_in_b:
        line_tokens = b_lines[(f, l)]
        if p < len(line_tokens) - 1:
            next_token = line_tokens[p+1][0]
            following.append(next_token)

    following_counts = Counter(following)
    print(f"  Most common following tokens:")
    for tok, count in following_counts.most_common(10):
        print(f"    {tok}: {count}")

    # CT by B folio
    ct_folios = Counter(f for t, f, s, l, p in ct_in_b)
    print(f"\n## CT DISTRIBUTION ACROSS B FOLIOS")
    print(f"  CT appears in {len(ct_folios)} B folios")
    print(f"  Top 10 folios by CT count:")
    for folio, count in ct_folios.most_common(10):
        total_in_folio = sum(1 for t, f, s, l, p in b_data if f == folio)
        pct = 100 * count / total_in_folio if total_in_folio > 0 else 0
        print(f"    {folio}: {count} CT ({pct:.2f}% of folio)")

    return {
        'ct_in_b': len(ct_in_b),
        'ct_folios': len(ct_folios),
        'mean_position': np.mean(ct_rel_positions) if ct_rel_positions else None,
        'top_preceding': preceding_counts.most_common(5),
        'top_following': following_counts.most_common(5)
    }


def test_h3_a_vocabulary_in_b(a_data, b_data):
    """
    H3: B Folios Have A-References

    Test: Can we identify a consistent "reference pattern" where
    A-enriched vocabulary appears in B grammar?
    """
    print("\n" + "=" * 80)
    print("H3: A-ENRICHED VOCABULARY IN B GRAMMAR")
    print("=" * 80)

    # Compute A/B ratios for all tokens
    a_counts = Counter(t for t, f, s, l, p in a_data)
    b_counts = Counter(t for t, f, s, l, p in b_data)

    all_tokens = set(a_counts.keys()) | set(b_counts.keys())

    # Classify tokens by enrichment
    a_enriched = set()  # > 2x more common in A
    b_enriched = set()  # > 2x more common in B

    for token in all_tokens:
        a_c = a_counts.get(token, 0)
        b_c = b_counts.get(token, 0)

        if a_c >= 10 or b_c >= 10:
            if a_c > 0 and b_c > 0:
                ratio = b_c / a_c
                if ratio < 0.5:
                    a_enriched.add(token)
                elif ratio > 2.0:
                    b_enriched.add(token)
            elif a_c > 0 and b_c == 0:
                a_enriched.add(token)
            elif b_c > 0 and a_c == 0:
                b_enriched.add(token)

    print(f"\nA-enriched tokens (>2x in A): {len(a_enriched)}")
    print(f"B-enriched tokens (>2x in B): {len(b_enriched)}")

    # Find A-enriched tokens appearing in B
    a_enriched_in_b = [(t, f, s, l, p) for t, f, s, l, p in b_data if t in a_enriched]
    print(f"\nA-enriched occurrences in B: {len(a_enriched_in_b)}")

    # Group by line
    b_lines = defaultdict(list)
    for t, f, s, l, p in b_data:
        b_lines[(f, l)].append((t, p))

    # Position analysis
    positions = []
    for t, f, s, l, p in a_enriched_in_b:
        line_tokens = b_lines[(f, l)]
        if len(line_tokens) > 1:
            rel_pos = p / (len(line_tokens) - 1)
            positions.append(rel_pos)

    print(f"\n## A-ENRICHED TOKEN POSITIONS IN B")
    if positions:
        print(f"  Mean relative position: {np.mean(positions):.3f}")
        print(f"  Std: {np.std(positions):.3f}")

        # Is it line-initial enriched?
        initial_count = sum(1 for t, f, s, l, p in a_enriched_in_b if p == 0)
        initial_rate = initial_count / len(a_enriched_in_b) if len(a_enriched_in_b) > 0 else 0

        # Background line-initial rate
        bg_initial = sum(1 for t, f, s, l, p in b_data if p == 0)
        bg_rate = bg_initial / len(b_data) if len(b_data) > 0 else 0

        print(f"\n  Line-initial rate: {100*initial_rate:.1f}%")
        print(f"  Background rate: {100*bg_rate:.1f}%")
        print(f"  Enrichment: {initial_rate/bg_rate:.2f}x" if bg_rate > 0 else "  Enrichment: N/A")

    # By prefix
    print(f"\n## A-ENRICHED IN B BY PREFIX")
    prefix_in_b = defaultdict(int)
    for t, f, s, l, p in a_enriched_in_b:
        for prefix in MARKER_PREFIXES:
            if t.startswith(prefix):
                prefix_in_b[prefix] += 1
                break
        else:
            prefix_in_b['other'] += 1

    for prefix, count in sorted(prefix_in_b.items(), key=lambda x: -x[1]):
        print(f"  {prefix}: {count}")

    # Which B folios have most A-enriched vocabulary?
    print(f"\n## B FOLIOS WITH MOST A-ENRICHED VOCABULARY")
    folio_a_vocab = Counter(f for t, f, s, l, p in a_enriched_in_b)
    for folio, count in folio_a_vocab.most_common(15):
        total_in_folio = sum(1 for t, f, s, l, p in b_data if f == folio)
        pct = 100 * count / total_in_folio if total_in_folio > 0 else 0
        print(f"  {folio}: {count} A-enriched tokens ({pct:.2f}% of folio)")

    return {
        'a_enriched_count': len(a_enriched),
        'a_enriched_in_b': len(a_enriched_in_b),
        'mean_position': np.mean(positions) if positions else None,
        'initial_rate': initial_rate if positions else None,
        'top_folios': folio_a_vocab.most_common(10)
    }


def test_h4_section_mapping(a_data, b_data):
    """
    H4: Section Mapping

    Test: Do B folios cluster by which A-vocabulary they contain?
    """
    print("\n" + "=" * 80)
    print("H4: A-SECTION TO B-FOLIO MAPPING")
    print("=" * 80)

    # Get section-specific A tokens
    section_tokens = defaultdict(set)
    for t, f, s, l, p in a_data:
        if s in A_SECTIONS:
            section_tokens[s].add(t)

    print(f"\n## A SECTION VOCABULARY SIZES")
    for section, tokens in sorted(section_tokens.items()):
        print(f"  Section {section}: {len(tokens)} unique tokens")

    # Find section-exclusive tokens
    section_exclusive = {}
    for section in A_SECTIONS:
        other_tokens = set()
        for other_sec in A_SECTIONS:
            if other_sec != section:
                other_tokens |= section_tokens[other_sec]
        section_exclusive[section] = section_tokens[section] - other_tokens

    print(f"\n## SECTION-EXCLUSIVE TOKENS")
    for section, tokens in sorted(section_exclusive.items()):
        print(f"  Section {section}: {len(tokens)} exclusive tokens")

    # For each B folio, count section-exclusive tokens
    b_folios = set(f for t, f, s, l, p in b_data)

    folio_section_scores = {}
    for folio in b_folios:
        folio_tokens = set(t for t, f, s, l, p in b_data if f == folio)
        scores = {}
        for section, exclusive in section_exclusive.items():
            overlap = len(folio_tokens & exclusive)
            scores[section] = overlap
        folio_section_scores[folio] = scores

    # Classify B folios by dominant A-section
    print(f"\n## B FOLIO CLASSIFICATION BY A-SECTION VOCABULARY")
    classification = defaultdict(list)

    for folio, scores in folio_section_scores.items():
        total = sum(scores.values())
        if total > 0:
            dominant = max(scores.keys(), key=lambda k: scores[k])
            dominance = scores[dominant] / total
            classification[dominant].append((folio, scores[dominant], total, dominance))
        else:
            classification['NONE'].append((folio, 0, 0, 0))

    for section in list(A_SECTIONS) + ['NONE']:
        folios = classification.get(section, [])
        print(f"\n  {section}-dominant folios: {len(folios)}")
        if folios and section != 'NONE':
            # Show top 5
            sorted_folios = sorted(folios, key=lambda x: -x[1])[:5]
            for folio, score, total, dom in sorted_folios:
                print(f"    {folio}: {score}/{total} ({100*dom:.1f}% {section})")

    # Statistical test: is classification non-random?
    section_counts = [len(classification.get(s, [])) for s in A_SECTIONS]
    total_classified = sum(section_counts)

    if total_classified > 0:
        expected = [total_classified / len(A_SECTIONS)] * len(A_SECTIONS)
        chi2, p = stats.chisquare(section_counts, expected)
        print(f"\n## UNIFORMITY TEST")
        print(f"  Distribution: H={section_counts[0]}, P={section_counts[1]}, T={section_counts[2]}")
        print(f"  Chi-square: chi2={chi2:.2f}, p={p:.4f}")
        if p < 0.05:
            print(f"  RESULT: Non-uniform distribution (suggests section mapping)")
        else:
            print(f"  RESULT: Uniform distribution (no section mapping signal)")

    return {
        'section_exclusive_counts': {s: len(t) for s, t in section_exclusive.items()},
        'classification': {s: len(f) for s, f in classification.items()},
        'chi2_p': p if total_classified > 0 else None
    }


def main():
    print("=" * 80)
    print("CAS-XREF: Cross-Reference Structure Analysis")
    print("=" * 80)

    print("\nLoading data...")
    a_data, b_data = load_full_data()
    print(f"  A tokens: {len(a_data)}")
    print(f"  B tokens: {len(b_data)}")

    results = {}

    # Run all hypothesis tests
    results['H1_balanced'] = test_h1_balanced_positions(a_data, b_data)
    results['H2_ct_in_b'] = test_h2_ct_in_b(a_data, b_data)
    results['H3_a_vocab_in_b'] = test_h3_a_vocabulary_in_b(a_data, b_data)
    results['H4_section_mapping'] = test_h4_section_mapping(a_data, b_data)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\n## H1: Balanced Tokens as Cross-Reference Points")
    h1 = results['H1_balanced']
    if h1['A_enrichment'] and h1['A_enrichment'] > 1.5:
        print(f"  SIGNAL: Line-initial enrichment {h1['A_enrichment']:.2f}x in A")
    if h1['B_enrichment'] and h1['B_enrichment'] > 1.5:
        print(f"  SIGNAL: Line-initial enrichment {h1['B_enrichment']:.2f}x in B")
    if (not h1['A_enrichment'] or h1['A_enrichment'] <= 1.5) and \
       (not h1['B_enrichment'] or h1['B_enrichment'] <= 1.5):
        print(f"  NO SIGNAL: No significant positional enrichment")

    print("\n## H2: CT-in-B as Material References")
    h2 = results['H2_ct_in_b']
    if h2['mean_position'] is not None:
        if h2['mean_position'] < 0.3:
            print(f"  SIGNAL: CT clustered early in lines (pos={h2['mean_position']:.3f})")
        elif h2['mean_position'] > 0.7:
            print(f"  SIGNAL: CT clustered late in lines (pos={h2['mean_position']:.3f})")
        else:
            print(f"  NO SIGNAL: CT evenly distributed (pos={h2['mean_position']:.3f})")

    print("\n## H3: A-Vocabulary Patterns in B")
    h3 = results['H3_a_vocab_in_b']
    if h3['initial_rate'] and h3['initial_rate'] > 0.3:
        print(f"  SIGNAL: A-enriched tokens line-initial ({100*h3['initial_rate']:.1f}%)")
    else:
        print(f"  NO SIGNAL: A-enriched tokens not positionally distinct")

    print("\n## H4: Section Mapping")
    h4 = results['H4_section_mapping']
    if h4['chi2_p'] and h4['chi2_p'] < 0.05:
        print(f"  SIGNAL: Non-uniform section distribution (p={h4['chi2_p']:.4f})")
    else:
        print(f"  NO SIGNAL: Uniform section distribution")

    # Save results
    output_path = project_root / 'phases' / 'CAS_XREF_cross_reference_structure' / 'cas_xref_results.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to JSON-serializable
    json_results = {}
    for k, v in results.items():
        json_results[k] = {}
        for k2, v2 in v.items():
            if isinstance(v2, (list, tuple)):
                json_results[k][k2] = [list(x) if isinstance(x, tuple) else x for x in v2]
            elif isinstance(v2, np.floating):
                json_results[k][k2] = float(v2)
            elif isinstance(v2, dict):
                json_results[k][k2] = {str(k3): v3 for k3, v3 in v2.items()}
            else:
                json_results[k][k2] = v2

    with open(output_path, 'w') as f:
        json.dump(json_results, f, indent=2)

    print(f"\n\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
