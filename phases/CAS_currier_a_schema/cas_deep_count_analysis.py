"""
CAS-DEEP Track 3: Count Significance Analysis

Question: Why do repetition counts peak at 2x (416) and 3x (424)?

Tests:
- T3.1: Count x marker contingency table
- T3.2: Count x section contingency table
- T3.3: Block vocabulary vs count (do higher counts = simpler blocks?)
- T3.4: Count distribution shape analysis
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy.stats import chi2_contingency, spearmanr

project_root = Path(__file__).parent.parent.parent


def load_currier_a_lines():
    """Load Currier A data grouped by line (PRIMARY transcriber H only)."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    lines = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': ''})

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                lang = parts[6].strip('"').strip()
                if lang == 'A':
                    word = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                    if word:
                        key = f"{folio}_{line_num}"
                        lines[key]['tokens'].append(word)
                        lines[key]['section'] = section
                        lines[key]['folio'] = folio

    return dict(lines)


def find_repeating_blocks(tokens):
    """Find the repeating block pattern in a sequence of tokens."""
    n = len(tokens)
    if n < 2:
        return tokens, 1

    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            block = tokens[:block_size]
            count = n // block_size

            matches = True
            for i in range(1, count):
                chunk = tokens[i * block_size:(i + 1) * block_size]
                mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                if mismatches > len(block) * 0.2:
                    matches = False
                    break

            if matches and count >= 2:
                return block, count

    for block_size in range(2, n // 2 + 1):
        block = tokens[:block_size]
        count = 1
        i = block_size

        while i + block_size <= n:
            chunk = tokens[i:i + block_size]
            mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
            if mismatches <= len(block) * 0.25:
                count += 1
                i += block_size
            else:
                break

        if count >= 2:
            return block, count

    return tokens, 1


def classify_entries(lines):
    """Classify entries with blocks, markers, and sections."""
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    entries = []

    for line_id, info in lines.items():
        tokens = info['tokens']
        if len(tokens) >= 4:
            block, count = find_repeating_blocks(tokens)

            if count >= 2:
                # Find marker
                marker = None
                for token in block:
                    if len(token) >= 2:
                        prefix = token[:2]
                        if prefix in marker_prefixes:
                            marker = prefix
                            break

                entries.append({
                    'line_id': line_id,
                    'folio': info['folio'],
                    'section': info['section'],
                    'tokens': tokens,
                    'block': block,
                    'count': count,
                    'block_size': len(block),
                    'marker': marker or 'NONE'
                })

    return entries


def test_3_1_count_marker_contingency(entries):
    """T3.1: Count x marker contingency table."""
    print("\n" + "=" * 70)
    print("T3.1: COUNT x MARKER CONTINGENCY")
    print("=" * 70)

    # Build contingency table
    count_marker = defaultdict(lambda: defaultdict(int))

    for entry in entries:
        marker = entry['marker']
        count = entry['count']
        if marker != 'NONE':
            # Group counts: 2, 3, 4, 5+
            count_cat = str(count) if count <= 4 else '5+'
            count_marker[count_cat][marker] += 1

    # Print table
    markers = sorted(set(m for entry in entries if entry['marker'] != 'NONE'
                        for m in [entry['marker']]))
    count_cats = ['2', '3', '4', '5+']

    print("\nContingency table (count x marker):")
    header = "Count   " + "  ".join(f"{m:>6}" for m in markers) + "   Total"
    print(header)
    print("-" * len(header))

    table = []
    for cc in count_cats:
        row = [count_marker[cc].get(m, 0) for m in markers]
        row_total = sum(row)
        table.append(row)
        print(f"{cc:>5}   " + "  ".join(f"{v:>6}" for v in row) + f"   {row_total:>5}")

    col_totals = [sum(count_marker[cc].get(m, 0) for cc in count_cats) for m in markers]
    print("-" * len(header))
    print(f"Total   " + "  ".join(f"{v:>6}" for v in col_totals) + f"   {sum(col_totals):>5}")

    # Chi-square test
    table_arr = np.array(table)
    if table_arr.min() >= 5:
        chi2, p, dof, expected = chi2_contingency(table_arr)
        print(f"\nChi-square test:")
        print(f"  Chi2 = {chi2:.2f}")
        print(f"  df = {dof}")
        print(f"  p = {p:.6f}")

        if p < 0.05:
            print("  -> Count distribution DEPENDS on marker")
            verdict = "MARKER_DEPENDENT"
        else:
            print("  -> Count distribution INDEPENDENT of marker")
            verdict = "MARKER_INDEPENDENT"
    else:
        print("\nSome cells too small for chi-square test")
        verdict = "INSUFFICIENT_DATA"

    return {
        'contingency': {cc: dict(count_marker[cc]) for cc in count_cats},
        'verdict': verdict
    }


def test_3_2_count_section_contingency(entries):
    """T3.2: Count x section contingency table."""
    print("\n" + "=" * 70)
    print("T3.2: COUNT x SECTION CONTINGENCY")
    print("=" * 70)

    # Build contingency table
    count_section = defaultdict(lambda: defaultdict(int))

    for entry in entries:
        section = entry['section']
        count = entry['count']
        if section:
            count_cat = str(count) if count <= 4 else '5+'
            count_section[count_cat][section] += 1

    # Get sections
    sections = sorted(set(entry['section'] for entry in entries if entry['section']))
    count_cats = ['2', '3', '4', '5+']

    print("\nContingency table (count x section):")
    header = "Count   " + "  ".join(f"{s:>6}" for s in sections) + "   Total"
    print(header)
    print("-" * len(header))

    table = []
    for cc in count_cats:
        row = [count_section[cc].get(s, 0) for s in sections]
        row_total = sum(row)
        table.append(row)
        print(f"{cc:>5}   " + "  ".join(f"{v:>6}" for v in row) + f"   {row_total:>5}")

    col_totals = [sum(count_section[cc].get(s, 0) for cc in count_cats) for s in sections]
    print("-" * len(header))
    print(f"Total   " + "  ".join(f"{v:>6}" for v in col_totals) + f"   {sum(col_totals):>5}")

    # Chi-square test
    table_arr = np.array(table)
    # Filter out columns with all zeros
    table_arr = table_arr[:, table_arr.sum(axis=0) > 0]

    if table_arr.size > 0 and table_arr.min() >= 1:
        try:
            chi2, p, dof, expected = chi2_contingency(table_arr)
            print(f"\nChi-square test:")
            print(f"  Chi2 = {chi2:.2f}")
            print(f"  df = {dof}")
            print(f"  p = {p:.6f}")

            if p < 0.05:
                print("  -> Count distribution DEPENDS on section")
                verdict = "SECTION_DEPENDENT"
            else:
                print("  -> Count distribution INDEPENDENT of section")
                verdict = "SECTION_INDEPENDENT"
        except Exception as e:
            print(f"\nChi-square test failed: {e}")
            verdict = "TEST_FAILED"
    else:
        print("\nInsufficient data for chi-square test")
        verdict = "INSUFFICIENT_DATA"

    return {
        'contingency': {cc: dict(count_section[cc]) for cc in count_cats},
        'verdict': verdict
    }


def test_3_3_count_complexity(entries):
    """T3.3: Do higher counts have simpler blocks?"""
    print("\n" + "=" * 70)
    print("T3.3: COUNT vs BLOCK COMPLEXITY")
    print("=" * 70)

    # Measure block complexity: vocabulary diversity (unique/total)
    count_complexity = defaultdict(list)

    for entry in entries:
        count = entry['count']
        block = entry['block']

        # Complexity = unique tokens / block size
        if len(block) > 0:
            complexity = len(set(block)) / len(block)
            count_complexity[count].append(complexity)

    print("\nBlock complexity by count:")
    print("(Complexity = unique tokens / block size)")
    print()

    counts = sorted(count_complexity.keys())
    complexities = []
    count_values = []

    for c in counts:
        values = count_complexity[c]
        mean_c = np.mean(values)
        std_c = np.std(values)
        complexities.extend(values)
        count_values.extend([c] * len(values))
        print(f"  {c}x: mean={mean_c:.3f}, std={std_c:.3f}, n={len(values)}")

    # Spearman correlation
    rho, p = spearmanr(count_values, complexities)
    print(f"\nSpearman correlation (count vs complexity):")
    print(f"  rho = {rho:.3f}")
    print(f"  p = {p:.6f}")

    if p < 0.05:
        if rho < 0:
            print("  -> Higher counts have SIMPLER blocks")
            verdict = "HIGHER_SIMPLER"
        else:
            print("  -> Higher counts have MORE COMPLEX blocks")
            verdict = "HIGHER_COMPLEX"
    else:
        print("  -> No significant relationship")
        verdict = "NO_RELATIONSHIP"

    return {
        'correlation': rho,
        'p_value': p,
        'verdict': verdict
    }


def test_3_4_distribution_shape(entries):
    """T3.4: Analyze the shape of count distribution."""
    print("\n" + "=" * 70)
    print("T3.4: COUNT DISTRIBUTION SHAPE ANALYSIS")
    print("=" * 70)

    counts = [entry['count'] for entry in entries]
    count_dist = Counter(counts)

    print("\nCount distribution:")
    total = len(counts)
    for c in sorted(count_dist.keys()):
        freq = count_dist[c]
        pct = 100 * freq / total
        bar = '*' * int(pct)
        print(f"  {c}x: {freq:>4} ({pct:>5.1f}%) {bar}")

    # Statistics
    mean_count = np.mean(counts)
    median_count = np.median(counts)
    mode_count = count_dist.most_common(1)[0][0]

    print(f"\nStatistics:")
    print(f"  Mean: {mean_count:.2f}")
    print(f"  Median: {median_count:.1f}")
    print(f"  Mode: {mode_count}")

    # Test for geometric distribution (expected for random stopping)
    # Geometric would have p(k) = (1-p)^(k-1) * p
    # Check if 2x and 3x being nearly equal suggests NOT geometric

    if 2 in count_dist and 3 in count_dist:
        ratio_2_3 = count_dist[2] / count_dist[3]
        print(f"\nRatio test:")
        print(f"  Count(2x) / Count(3x) = {ratio_2_3:.3f}")

        # For geometric, this ratio should be > 1 (declining)
        if 0.9 < ratio_2_3 < 1.1:
            print("  -> Nearly equal: suggests DELIBERATE balance, not random stopping")
            shape_verdict = "BALANCED"
        elif ratio_2_3 > 1.5:
            print("  -> 2x dominates: suggests random/early stopping")
            shape_verdict = "GEOMETRIC_LIKE"
        else:
            print("  -> 3x dominates: unusual pattern")
            shape_verdict = "UNUSUAL"
    else:
        shape_verdict = "INSUFFICIENT_DATA"

    # Check for special numbers (2, 3, 4 as significant)
    small_counts = sum(count_dist.get(c, 0) for c in [2, 3, 4])
    large_counts = sum(count_dist.get(c, 0) for c in range(5, max(count_dist.keys()) + 1))

    print(f"\nSmall (2-4) vs Large (5+):")
    print(f"  Small: {small_counts} ({100*small_counts/total:.1f}%)")
    print(f"  Large: {large_counts} ({100*large_counts/total:.1f}%)")

    # Overall verdict
    if shape_verdict == "BALANCED" and small_counts / total > 0.95:
        verdict = "SMALL_BALANCED"
        print(f"\nVerdict: {verdict}")
        print("  Distribution is concentrated in small counts (2-4)")
        print("  with 2x and 3x nearly balanced - suggests deliberate pattern")
    else:
        verdict = shape_verdict

    return {
        'distribution': dict(count_dist),
        'mean': float(mean_count),
        'median': float(median_count),
        'mode': int(mode_count),
        'ratio_2_3': ratio_2_3 if 2 in count_dist and 3 in count_dist else None,
        'verdict': verdict
    }


def main():
    print("=" * 70)
    print("CAS-DEEP TRACK 3: COUNT SIGNIFICANCE")
    print("=" * 70)

    lines = load_currier_a_lines()
    print(f"\nLoaded {len(lines)} Currier A lines")

    entries = classify_entries(lines)
    print(f"Entries with repeating blocks: {len(entries)}")

    # Early return if no blocks (H-only data has 0% block repetition)
    if len(entries) == 0:
        print("\nNo blocks found - block analysis not applicable with H-only data.")
        print("Block repetition (64.1%) was an artifact of transcriber interleaving.")

        results = {
            't3_1': {'verdict': 'NO_BLOCKS'},
            't3_2': {'verdict': 'NO_BLOCKS'},
            't3_3': {'verdict': 'NO_BLOCKS'},
            't3_4': {'verdict': 'NO_BLOCKS'},
            'note': 'Block repetition was artifact of transcriber interleaving; 0% with H-only'
        }

        output_path = Path(__file__).parent / 'cas_deep_track3_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")
        return results

    # Run tests
    results = {}
    results['t3_1'] = test_3_1_count_marker_contingency(entries)
    results['t3_2'] = test_3_2_count_section_contingency(entries)
    results['t3_3'] = test_3_3_count_complexity(entries)
    results['t3_4'] = test_3_4_distribution_shape(entries)

    # Summary
    print("\n" + "=" * 70)
    print("TRACK 3 SUMMARY")
    print("=" * 70)

    print(f"\nT3.1 Count x Marker: {results['t3_1']['verdict']}")
    print(f"T3.2 Count x Section: {results['t3_2']['verdict']}")
    print(f"T3.3 Count vs Complexity: {results['t3_3']['verdict']}")
    print(f"T3.4 Distribution Shape: {results['t3_4']['verdict']}")

    # Save results
    output_path = Path(__file__).parent / 'cas_deep_track3_results.json'

    def convert_for_json(obj):
        if isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_for_json(item) for item in obj]
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        else:
            return obj

    with open(output_path, 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
