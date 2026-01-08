"""
CAS Phase 1: Atomicity Redefinition

Question: What is the smallest complete unit in Currier A?

Tests:
1. Are entries line-bounded?
2. Do tokens interact across lines?
3. Do tokens interact across folios?
4. Are there entry-internal structure patterns?

This determines whether A is a record system (entry-atomic)
or a higher-order schema (cross-entry dependencies).
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy import stats as sp_stats

project_root = Path(__file__).parent.parent.parent


def load_currier_a_data():
    """Load Currier A tokens with line-level granularity."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        # Find column indices
        word_idx = 0
        folio_idx = header.index('folio') if 'folio' in header else 1
        line_idx = header.index('line') if 'line' in header else 2
        lang_idx = 6  # language column (A/B/NA)
        section_idx = header.index('section') if 'section' in header else 3

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > lang_idx:
                lang = parts[lang_idx].strip('"').strip()
                if lang == 'A':
                    word = parts[word_idx].strip('"').strip().lower()
                    folio = parts[folio_idx].strip('"').strip() if len(parts) > folio_idx else ''
                    line_num = parts[line_idx].strip('"').strip() if len(parts) > line_idx else ''
                    section = parts[section_idx].strip('"').strip() if len(parts) > section_idx else ''

                    if word:
                        data.append({
                            'token': word,
                            'folio': folio,
                            'line': line_num,
                            'section': section,
                            'folio_line': f"{folio}_{line_num}"
                        })

    return data


def compute_mutual_information(seq1, seq2):
    """Compute mutual information between two token sequences."""
    if not seq1 or not seq2:
        return 0.0

    # Create joint and marginal distributions
    vocab1 = set(seq1)
    vocab2 = set(seq2)

    if len(vocab1) < 2 or len(vocab2) < 2:
        return 0.0

    # Count occurrences
    count1 = Counter(seq1)
    count2 = Counter(seq2)

    # Simple MI approximation: shared vocabulary weighted by frequency
    shared = vocab1 & vocab2
    if not shared:
        return 0.0

    n1, n2 = len(seq1), len(seq2)
    mi = 0.0
    for token in shared:
        p1 = count1[token] / n1
        p2 = count2[token] / n2
        # Joint probability approximation
        p_joint = min(p1, p2) * 0.5  # Conservative estimate
        if p_joint > 0 and p1 > 0 and p2 > 0:
            mi += p_joint * np.log2(p_joint / (p1 * p2) + 1e-10)

    return max(0, mi)


def test_line_atomicity(data):
    """
    Test 1: Are entries line-bounded?

    If lines are atomic units, we expect:
    - Low cross-line MI
    - High within-line structure
    """
    print("\n" + "=" * 70)
    print("TEST 1: LINE ATOMICITY")
    print("=" * 70)

    # Group tokens by folio_line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Filter to lines with multiple tokens
    multi_token_lines = {k: v for k, v in lines.items() if len(v) >= 2}

    print(f"\nTotal lines with A text: {len(lines)}")
    print(f"Lines with 2+ tokens: {len(multi_token_lines)}")

    # Line length distribution
    lengths = [len(v) for v in lines.values()]
    print(f"\nLine length distribution:")
    print(f"  Mean: {np.mean(lengths):.2f}")
    print(f"  Median: {np.median(lengths):.2f}")
    print(f"  Max: {max(lengths)}")
    print(f"  Single-token lines: {sum(1 for l in lengths if l == 1)} ({100*sum(1 for l in lengths if l == 1)/len(lengths):.1f}%)")

    # Line length histogram
    bins = [1, 2, 3, 4, 5, 10, 20, 50, 100]
    hist = defaultdict(int)
    for l in lengths:
        for i, b in enumerate(bins):
            if l <= b:
                hist[bins[i]] += 1
                break
        else:
            hist['>100'] += 1

    print(f"\n  Length distribution:")
    for b in bins:
        if hist[b] > 0:
            print(f"    <={b}: {hist[b]} ({100*hist[b]/len(lengths):.1f}%)")
    if hist['>100'] > 0:
        print(f"    >100: {hist['>100']} ({100*hist['>100']/len(lengths):.1f}%)")

    return {
        'total_lines': len(lines),
        'multi_token_lines': len(multi_token_lines),
        'mean_length': np.mean(lengths),
        'median_length': np.median(lengths),
        'single_token_pct': sum(1 for l in lengths if l == 1) / len(lengths)
    }


def test_cross_line_dependency(data):
    """
    Test 2: Do tokens interact across lines?

    Compute MI between adjacent lines within same folio.
    Low MI = line-atomic
    High MI = cross-line dependencies
    """
    print("\n" + "=" * 70)
    print("TEST 2: CROSS-LINE DEPENDENCY")
    print("=" * 70)

    # Group by folio, then by line
    folio_lines = defaultdict(lambda: defaultdict(list))
    for d in data:
        folio_lines[d['folio']][d['line']].append(d['token'])

    # Compute MI between adjacent lines
    adjacent_mis = []
    non_adjacent_mis = []

    for folio, lines_dict in folio_lines.items():
        sorted_lines = sorted(lines_dict.keys())

        for i in range(len(sorted_lines) - 1):
            line1 = lines_dict[sorted_lines[i]]
            line2 = lines_dict[sorted_lines[i + 1]]

            if len(line1) >= 2 and len(line2) >= 2:
                mi = compute_mutual_information(line1, line2)
                adjacent_mis.append(mi)

        # Non-adjacent comparison (skip 1)
        for i in range(len(sorted_lines) - 2):
            line1 = lines_dict[sorted_lines[i]]
            line3 = lines_dict[sorted_lines[i + 2]]

            if len(line1) >= 2 and len(line3) >= 2:
                mi = compute_mutual_information(line1, line3)
                non_adjacent_mis.append(mi)

    print(f"\nAdjacent line pairs analyzed: {len(adjacent_mis)}")
    print(f"Non-adjacent pairs analyzed: {len(non_adjacent_mis)}")

    if adjacent_mis and non_adjacent_mis:
        print(f"\nMutual Information:")
        print(f"  Adjacent lines:     mean={np.mean(adjacent_mis):.4f}, median={np.median(adjacent_mis):.4f}")
        print(f"  Non-adjacent lines: mean={np.mean(non_adjacent_mis):.4f}, median={np.median(non_adjacent_mis):.4f}")

        # Statistical test
        if len(adjacent_mis) >= 5 and len(non_adjacent_mis) >= 5:
            t_stat, p_val = sp_stats.ttest_ind(adjacent_mis, non_adjacent_mis)
            print(f"\n  t-test (adjacent vs non-adjacent): t={t_stat:.3f}, p={p_val:.4f}")

            if np.mean(adjacent_mis) > np.mean(non_adjacent_mis) * 1.5 and p_val < 0.05:
                print("  -> CROSS-LINE DEPENDENCY DETECTED (adjacent lines more similar)")
            elif p_val > 0.05:
                print("  -> NO SIGNIFICANT CROSS-LINE DEPENDENCY (lines appear independent)")
            else:
                print("  -> WEAK/AMBIGUOUS cross-line relationship")

    return {
        'adjacent_mi_mean': np.mean(adjacent_mis) if adjacent_mis else 0,
        'non_adjacent_mi_mean': np.mean(non_adjacent_mis) if non_adjacent_mis else 0,
        'adjacent_count': len(adjacent_mis),
        'non_adjacent_count': len(non_adjacent_mis)
    }


def test_cross_folio_dependency(data):
    """
    Test 3: Do tokens interact across folios?

    Compare vocabulary overlap between adjacent vs distant folios.
    """
    print("\n" + "=" * 70)
    print("TEST 3: CROSS-FOLIO DEPENDENCY")
    print("=" * 70)

    # Group by folio
    folio_tokens = defaultdict(list)
    for d in data:
        folio_tokens[d['folio']].append(d['token'])

    folios = sorted(folio_tokens.keys())
    print(f"\nTotal folios with A text: {len(folios)}")

    # Compute vocabulary overlap between adjacent folios
    adjacent_overlaps = []
    distant_overlaps = []

    for i in range(len(folios) - 1):
        vocab1 = set(folio_tokens[folios[i]])
        vocab2 = set(folio_tokens[folios[i + 1]])

        if vocab1 and vocab2:
            overlap = len(vocab1 & vocab2) / len(vocab1 | vocab2)
            adjacent_overlaps.append(overlap)

    # Distant folios (5+ apart)
    for i in range(len(folios) - 5):
        vocab1 = set(folio_tokens[folios[i]])
        vocab2 = set(folio_tokens[folios[i + 5]])

        if vocab1 and vocab2:
            overlap = len(vocab1 & vocab2) / len(vocab1 | vocab2)
            distant_overlaps.append(overlap)

    print(f"\nVocabulary Overlap (Jaccard):")
    print(f"  Adjacent folios:  mean={np.mean(adjacent_overlaps):.4f}, median={np.median(adjacent_overlaps):.4f}")
    print(f"  Distant folios:   mean={np.mean(distant_overlaps):.4f}, median={np.median(distant_overlaps):.4f}")

    if len(adjacent_overlaps) >= 5 and len(distant_overlaps) >= 5:
        t_stat, p_val = sp_stats.ttest_ind(adjacent_overlaps, distant_overlaps)
        print(f"\n  t-test: t={t_stat:.3f}, p={p_val:.4f}")

        if np.mean(adjacent_overlaps) > np.mean(distant_overlaps) * 1.3 and p_val < 0.05:
            print("  -> CROSS-FOLIO DEPENDENCY DETECTED (adjacent folios share more vocabulary)")
        else:
            print("  -> NO SIGNIFICANT CROSS-FOLIO DEPENDENCY")

    return {
        'adjacent_overlap_mean': np.mean(adjacent_overlaps),
        'distant_overlap_mean': np.mean(distant_overlaps),
        'adjacent_count': len(adjacent_overlaps),
        'distant_count': len(distant_overlaps)
    }


def test_entry_internal_structure(data):
    """
    Test 4: Is there internal structure within entries?

    If A is a record system, entries should have:
    - Consistent first/last token patterns
    - Position-dependent token distributions
    """
    print("\n" + "=" * 70)
    print("TEST 4: ENTRY-INTERNAL STRUCTURE")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Only analyze multi-token lines
    multi_lines = {k: v for k, v in lines.items() if len(v) >= 3}

    print(f"\nLines with 3+ tokens: {len(multi_lines)}")

    # Collect tokens by position
    first_tokens = []
    middle_tokens = []
    last_tokens = []

    for line_tokens in multi_lines.values():
        first_tokens.append(line_tokens[0])
        last_tokens.append(line_tokens[-1])
        middle_tokens.extend(line_tokens[1:-1])

    # Vocabulary analysis by position
    first_vocab = set(first_tokens)
    middle_vocab = set(middle_tokens)
    last_vocab = set(last_tokens)

    print(f"\nPosition-specific vocabulary:")
    print(f"  First position:  {len(first_vocab)} unique types")
    print(f"  Middle positions: {len(middle_vocab)} unique types")
    print(f"  Last position:   {len(last_vocab)} unique types")

    # Exclusivity analysis
    first_only = first_vocab - middle_vocab - last_vocab
    last_only = last_vocab - middle_vocab - first_vocab

    print(f"\n  First-only tokens: {len(first_only)} ({100*len(first_only)/len(first_vocab):.1f}% of first vocab)")
    print(f"  Last-only tokens:  {len(last_only)} ({100*len(last_only)/len(last_vocab):.1f}% of last vocab)")

    # Show examples
    if first_only:
        print(f"\n  Sample first-only: {list(first_only)[:10]}")
    if last_only:
        print(f"\n  Sample last-only: {list(last_only)[:10]}")

    # Concentration analysis
    first_counts = Counter(first_tokens)
    last_counts = Counter(last_tokens)

    top_first = first_counts.most_common(5)
    top_last = last_counts.most_common(5)

    print(f"\nTop 5 first-position tokens:")
    for tok, count in top_first:
        pct = 100 * count / len(first_tokens)
        print(f"    {tok}: {count} ({pct:.1f}%)")

    print(f"\nTop 5 last-position tokens:")
    for tok, count in top_last:
        pct = 100 * count / len(last_tokens)
        print(f"    {tok}: {count} ({pct:.1f}%)")

    # Test: Is position-vocabulary binding stronger than chance?
    # If tokens are randomly distributed, first/last should look like middle
    first_concentration = sum(c for _, c in top_first) / len(first_tokens) if first_tokens else 0
    last_concentration = sum(c for _, c in top_last) / len(last_tokens) if last_tokens else 0
    middle_concentration = sum(c for _, c in Counter(middle_tokens).most_common(5)) / len(middle_tokens) if middle_tokens else 0

    print(f"\nTop-5 concentration:")
    print(f"  First:  {first_concentration:.3f}")
    print(f"  Middle: {middle_concentration:.3f}")
    print(f"  Last:   {last_concentration:.3f}")

    if first_concentration > middle_concentration * 1.3 or last_concentration > middle_concentration * 1.3:
        print("\n  -> POSITIONAL STRUCTURE DETECTED (boundary positions more constrained)")
    else:
        print("\n  -> NO CLEAR POSITIONAL STRUCTURE")

    return {
        'first_vocab_size': len(first_vocab),
        'middle_vocab_size': len(middle_vocab),
        'last_vocab_size': len(last_vocab),
        'first_only_pct': len(first_only) / len(first_vocab) if first_vocab else 0,
        'last_only_pct': len(last_only) / len(last_vocab) if last_vocab else 0,
        'first_concentration': first_concentration,
        'middle_concentration': middle_concentration,
        'last_concentration': last_concentration
    }


def synthesize_atomicity(results):
    """Determine atomicity verdict."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: ATOMICITY DETERMINATION")
    print("=" * 70)

    # Scoring
    scores = {
        'LINE_ATOMIC': 0,
        'FOLIO_ATOMIC': 0,
        'CROSS_ENTRY': 0
    }

    # Test 1: Line structure
    if results['line']['single_token_pct'] > 0.3:
        scores['LINE_ATOMIC'] += 1
        print("\n[+] High single-token line rate -> supports LINE_ATOMIC")

    if results['line']['median_length'] <= 3:
        scores['LINE_ATOMIC'] += 1
        print("[+] Short median line length -> supports LINE_ATOMIC")

    # Test 2: Cross-line MI
    if results['cross_line']['adjacent_mi_mean'] < 0.1:
        scores['LINE_ATOMIC'] += 1
        print("[+] Low cross-line MI -> supports LINE_ATOMIC")
    elif results['cross_line']['adjacent_mi_mean'] > 0.2:
        scores['CROSS_ENTRY'] += 1
        print("[-] High cross-line MI -> supports CROSS_ENTRY")

    # Test 3: Cross-folio overlap
    if results['cross_folio']['adjacent_overlap_mean'] < 0.15:
        scores['LINE_ATOMIC'] += 1
        print("[+] Low adjacent folio overlap -> supports LINE_ATOMIC")
    elif results['cross_folio']['adjacent_overlap_mean'] > 0.3:
        scores['FOLIO_ATOMIC'] += 1
        print("[+] High adjacent folio overlap -> supports FOLIO_ATOMIC")

    # Test 4: Internal structure
    if results['internal']['first_concentration'] > results['internal']['middle_concentration'] * 1.3:
        scores['LINE_ATOMIC'] += 1
        print("[+] First-position concentration -> supports LINE_ATOMIC (record structure)")

    if results['internal']['last_concentration'] > results['internal']['middle_concentration'] * 1.3:
        scores['LINE_ATOMIC'] += 1
        print("[+] Last-position concentration -> supports LINE_ATOMIC (record structure)")

    # Determine verdict
    print(f"\nScores: LINE_ATOMIC={scores['LINE_ATOMIC']}, FOLIO_ATOMIC={scores['FOLIO_ATOMIC']}, CROSS_ENTRY={scores['CROSS_ENTRY']}")

    if scores['LINE_ATOMIC'] >= 3:
        verdict = 'LINE_ATOMIC'
        interpretation = "Currier A entries are line-bounded. Each line is an atomic unit (record)."
    elif scores['FOLIO_ATOMIC'] >= 2:
        verdict = 'FOLIO_ATOMIC'
        interpretation = "Currier A entries span lines but not folios. Folio is the atomic unit."
    elif scores['CROSS_ENTRY'] >= 2:
        verdict = 'CROSS_ENTRY'
        interpretation = "Currier A shows cross-entry dependencies. Higher-order schema."
    else:
        verdict = 'AMBIGUOUS'
        interpretation = "Atomicity level unclear. May be mixed."

    print(f"\n{'='*70}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*70}")
    print(f"\n{interpretation}")

    return verdict, interpretation


def main():
    print("=" * 70)
    print("CAS PHASE 1: ATOMICITY REDEFINITION")
    print("=" * 70)
    print("\nQuestion: What is the smallest complete unit in Currier A?")

    data = load_currier_a_data()
    print(f"\nLoaded {len(data)} Currier A tokens")

    results = {
        'line': test_line_atomicity(data),
        'cross_line': test_cross_line_dependency(data),
        'cross_folio': test_cross_folio_dependency(data),
        'internal': test_entry_internal_structure(data)
    }

    verdict, interpretation = synthesize_atomicity(results)

    results['verdict'] = verdict
    results['interpretation'] = interpretation

    # Save results
    output_path = Path(__file__).parent / 'cas_phase1_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
