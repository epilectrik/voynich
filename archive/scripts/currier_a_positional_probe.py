"""
Probe: Does Currier A encode positional/locational data?

Hypothesis: If A is a plant/material registry, it might encode:
- Row/column positions (grid structure)
- Sequential locations (planting order)
- Spatial relationships

Looking for:
1. Numeric-like incrementing patterns in token structure
2. Grid structure (systematic row × column variation)
3. Positional encoding in morphology (prefix = row? suffix = column?)
4. Repeating structural units that suggest spatial layout
"""

import csv
import json
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import spearmanr, chi2_contingency
from pathlib import Path

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

def load_currier_a():
    """Load Currier A data."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('language') == 'A' and row.get('transcriber') == 'H':
                data.append(row)
    return data

def extract_morphology(token):
    """Extract prefix/middle/suffix from token."""
    # Known prefixes from CAS-MORPH
    prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
    # Common suffixes
    suffixes = ['aiin', 'ain', 'ar', 'or', 'al', 'ol', 'dy', 'ey', 'y', 'r', 'l', 's', 'd']

    prefix = ''
    suffix = ''
    middle = token

    for p in sorted(prefixes, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            middle = token[len(p):]
            break

    for s in sorted(suffixes, key=len, reverse=True):
        if middle.endswith(s) and len(middle) > len(s):
            suffix = s
            middle = middle[:-len(s)]
            break

    return prefix, middle, suffix

def test_grid_structure(data):
    """
    Test 1: Do prefix × suffix combinations suggest grid structure?
    If A encodes positions, we might see systematic prefix × suffix patterns.
    """
    print("\n" + "="*70)
    print("TEST 1: GRID STRUCTURE (PREFIX × SUFFIX)")
    print("="*70)
    print("\nQuestion: Do prefix × suffix combinations form a grid?")

    # Extract morphology for each token
    prefix_suffix_counts = defaultdict(lambda: defaultdict(int))
    prefix_counts = Counter()
    suffix_counts = Counter()

    for row in data:
        token = row.get('word', '')
        if not token:
            continue
        prefix, middle, suffix = extract_morphology(token)
        if prefix and suffix:
            prefix_suffix_counts[prefix][suffix] += 1
            prefix_counts[prefix] += 1
            suffix_counts[suffix] += 1

    # Build contingency table
    prefixes = sorted(prefix_counts.keys())
    suffixes = sorted(suffix_counts.keys())

    print(f"\nPrefixes found: {prefixes}")
    print(f"Suffixes found: {suffixes}")

    # Check if all combinations exist (grid property)
    total_cells = len(prefixes) * len(suffixes)
    filled_cells = sum(1 for p in prefixes for s in suffixes if prefix_suffix_counts[p][s] > 0)
    fill_rate = filled_cells / total_cells if total_cells > 0 else 0

    print(f"\nGrid fill rate: {filled_cells}/{total_cells} = {fill_rate:.1%}")

    # Chi-square test for independence
    if len(prefixes) >= 2 and len(suffixes) >= 2:
        table = [[prefix_suffix_counts[p][s] for s in suffixes] for p in prefixes]
        table = np.array(table)

        # Only use cells with data
        row_sums = table.sum(axis=1)
        col_sums = table.sum(axis=0)
        valid_rows = row_sums > 0
        valid_cols = col_sums > 0

        if valid_rows.sum() >= 2 and valid_cols.sum() >= 2:
            filtered = table[valid_rows][:, valid_cols]
            chi2, p_val, dof, expected = chi2_contingency(filtered)

            print(f"\nChi-square test for prefix × suffix independence:")
            print(f"  Chi2 = {chi2:.1f}, p = {p_val:.2e}")

            if p_val < 0.001:
                print("  -> DEPENDENT: Prefix constrains suffix choice (NOT a simple grid)")
            else:
                print("  -> INDEPENDENT: Could be grid-like (any prefix with any suffix)")

    # Show the actual grid
    print("\nPrefix × Suffix frequency matrix:")
    print("       ", end="")
    for s in suffixes[:8]:
        print(f"{s:>8}", end="")
    print()

    for p in prefixes[:8]:
        print(f"{p:>6} ", end="")
        for s in suffixes[:8]:
            c = prefix_suffix_counts[p][s]
            print(f"{c:>8}", end="")
        print()

    return fill_rate

def test_sequential_numbering(data):
    """
    Test 2: Are there incrementing/decrementing patterns in middle components?
    If positions are encoded, middles might show systematic variation.
    """
    print("\n" + "="*70)
    print("TEST 2: SEQUENTIAL PATTERNS IN MIDDLE COMPONENTS")
    print("="*70)
    print("\nQuestion: Do middle components show sequential variation?")

    # Group by folio and line to see if middles vary systematically
    line_middles = defaultdict(list)

    for row in data:
        token = row.get('word', '')
        folio = row['folio']
        line = row.get('line_number', '1')
        if not token:
            continue
        prefix, middle, suffix = extract_morphology(token)
        if middle:
            line_middles[(folio, line)].append(middle)

    # Check for patterns in middle sequences within lines
    # If positional, middles might increment (a, b, c, ...) or show pattern

    # Look for repeated middles within lines (suggests enumeration)
    lines_with_repeats = 0
    total_lines = 0
    repeat_patterns = Counter()

    for key, middles in line_middles.items():
        if len(middles) >= 3:
            total_lines += 1
            middle_counts = Counter(middles)
            if max(middle_counts.values()) > 1:
                lines_with_repeats += 1
                # Get the repeat pattern
                for m, c in middle_counts.items():
                    if c > 1:
                        repeat_patterns[m] += 1

    repeat_rate = lines_with_repeats / total_lines if total_lines > 0 else 0
    print(f"\nLines with repeated middles: {lines_with_repeats}/{total_lines} = {repeat_rate:.1%}")

    print("\nMost common repeated middles:")
    for middle, count in repeat_patterns.most_common(10):
        print(f"  '{middle}': repeated in {count} lines")

    # Check for length-based ordering (shorter middles first?)
    length_orders = []
    for key, middles in line_middles.items():
        if len(middles) >= 4:
            lengths = [len(m) for m in middles]
            # Is length monotonic?
            increasing = all(lengths[i] <= lengths[i+1] for i in range(len(lengths)-1))
            decreasing = all(lengths[i] >= lengths[i+1] for i in range(len(lengths)-1))
            if increasing or decreasing:
                length_orders.append(1)
            else:
                length_orders.append(0)

    if length_orders:
        monotonic_rate = sum(length_orders) / len(length_orders)
        print(f"\nLines with monotonic middle length: {sum(length_orders)}/{len(length_orders)} = {monotonic_rate:.1%}")
        # Expected by chance for 4+ items
        print(f"  (expected by chance: ~{2/(24):.1%} for 4 items)")

    return repeat_rate

def test_row_column_markers(data):
    """
    Test 3: Are there tokens that might mark rows vs columns?
    Look for tokens that appear at regular intervals.
    """
    print("\n" + "="*70)
    print("TEST 3: ROW/COLUMN MARKER TOKENS")
    print("="*70)
    print("\nQuestion: Are there tokens that appear at regular intervals (markers)?")

    # Group by folio
    folio_tokens = defaultdict(list)
    for row in data:
        token = row.get('word', '')
        if token:
            folio_tokens[row['folio']].append(token)

    # For each folio, find tokens that appear at regular intervals
    marker_candidates = Counter()

    for folio, tokens in folio_tokens.items():
        if len(tokens) < 10:
            continue

        # Find positions of each token type
        token_positions = defaultdict(list)
        for i, t in enumerate(tokens):
            token_positions[t].append(i)

        # Check for regular spacing
        for token, positions in token_positions.items():
            if len(positions) >= 3:
                gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                if len(gaps) >= 2:
                    # Check if gaps are consistent (CV < 0.3)
                    mean_gap = np.mean(gaps)
                    std_gap = np.std(gaps)
                    cv = std_gap / mean_gap if mean_gap > 0 else 1
                    if cv < 0.3 and mean_gap > 2:  # Regular and not adjacent
                        marker_candidates[token] += 1

    print("\nTokens appearing at regular intervals across folios:")
    for token, count in marker_candidates.most_common(15):
        print(f"  '{token}': regular in {count} folios")

    return len(marker_candidates)

def test_section_layout_patterns(data):
    """
    Test 4: Do different sections show different layout patterns?
    Farming hypothesis: different beds/areas might have different structures.
    """
    print("\n" + "="*70)
    print("TEST 4: SECTION-SPECIFIC LAYOUT PATTERNS")
    print("="*70)
    print("\nQuestion: Do sections show different structural patterns?")

    # Compare sections H, P, T
    section_stats = defaultdict(lambda: {
        'tokens_per_line': [],
        'unique_prefixes_per_line': [],
        'lines': 0
    })

    # Group by section and line
    section_lines = defaultdict(lambda: defaultdict(list))

    for row in data:
        section = row.get('section', '')
        folio = row['folio']
        line = row.get('line_number', '1')
        token = row.get('word', '')
        if section and token:
            section_lines[section][(folio, line)].append(token)

    for section, lines in section_lines.items():
        for key, tokens in lines.items():
            section_stats[section]['lines'] += 1
            section_stats[section]['tokens_per_line'].append(len(tokens))

            prefixes = set()
            for t in tokens:
                p, m, s = extract_morphology(t)
                if p:
                    prefixes.add(p)
            section_stats[section]['unique_prefixes_per_line'].append(len(prefixes))

    print("\nSection statistics:")
    print(f"{'Section':<10} {'Lines':<8} {'Tok/Line':<12} {'Prefix/Line':<12}")
    print("-" * 45)

    for section in sorted(section_stats.keys()):
        stats = section_stats[section]
        mean_tok = np.mean(stats['tokens_per_line']) if stats['tokens_per_line'] else 0
        mean_pre = np.mean(stats['unique_prefixes_per_line']) if stats['unique_prefixes_per_line'] else 0
        print(f"{section:<10} {stats['lines']:<8} {mean_tok:<12.1f} {mean_pre:<12.1f}")

    # Test if sections differ in structure
    sections = list(section_stats.keys())
    if len(sections) >= 2:
        # Compare tokens per line across sections
        from scipy.stats import kruskal
        groups = [section_stats[s]['tokens_per_line'] for s in sections if section_stats[s]['tokens_per_line']]
        if len(groups) >= 2:
            stat, p_val = kruskal(*groups)
            print(f"\nKruskal-Wallis test (tokens/line across sections):")
            print(f"  H = {stat:.1f}, p = {p_val:.2e}")
            if p_val < 0.001:
                print("  -> Sections have DIFFERENT layout structures")
            else:
                print("  -> Sections have SIMILAR layout structures")

    return len(section_stats)

def test_numeric_suffixes(data):
    """
    Test 5: Do suffixes show numeric-like variation?
    If encoding positions 1,2,3..., suffixes might vary systematically.
    """
    print("\n" + "="*70)
    print("TEST 5: NUMERIC-LIKE SUFFIX VARIATION")
    print("="*70)
    print("\nQuestion: Do suffixes show systematic variation (like 1st, 2nd, 3rd)?")

    # Look for suffix patterns that might be ordinal
    suffix_by_position = defaultdict(list)

    for row in data:
        token = row.get('word', '')
        if not token:
            continue

        # Position within line
        try:
            pos = int(row.get('line_initial', 0)) * 10 + int(row.get('line_final', 0))
        except:
            pos = 0

        prefix, middle, suffix = extract_morphology(token)
        if suffix:
            suffix_by_position[pos].append(suffix)

    print("\nSuffix distribution by line position:")
    for pos in sorted(suffix_by_position.keys()):
        suffixes = suffix_by_position[pos]
        top = Counter(suffixes).most_common(5)
        top_str = ", ".join(f"{s}:{c}" for s, c in top)
        print(f"  Position {pos}: n={len(suffixes)}, top: {top_str}")

    # Check if line-initial vs line-final have different suffixes
    initial_suffixes = []
    final_suffixes = []

    for row in data:
        token = row.get('word', '')
        if not token:
            continue
        prefix, middle, suffix = extract_morphology(token)
        if not suffix:
            continue

        if row.get('line_initial') == '1':
            initial_suffixes.append(suffix)
        if row.get('line_final') == '1':
            final_suffixes.append(suffix)

    initial_dist = Counter(initial_suffixes)
    final_dist = Counter(final_suffixes)

    print("\nLine-initial suffix distribution:")
    for s, c in initial_dist.most_common(5):
        print(f"  {s}: {c} ({c/len(initial_suffixes):.1%})")

    print("\nLine-final suffix distribution:")
    for s, c in final_dist.most_common(5):
        print(f"  {s}: {c} ({c/len(final_suffixes):.1%})")

    return True

def main():
    print("="*70)
    print("CURRIER A POSITIONAL/LOCATIONAL ENCODING PROBE")
    print("="*70)
    print("\nHypothesis: Currier A might encode positional data (rows/columns,")
    print("planting positions, storage locations) if it's a plant registry.")

    data = load_currier_a()
    print(f"\nLoaded {len(data)} Currier A tokens")

    # Run tests
    fill_rate = test_grid_structure(data)
    repeat_rate = test_sequential_numbering(data)
    n_markers = test_row_column_markers(data)
    n_sections = test_section_layout_patterns(data)
    test_numeric_suffixes(data)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    print(f"""
Grid fill rate: {fill_rate:.1%}
Lines with repeated middles: {repeat_rate:.1%}
Regular-interval marker candidates: {n_markers}
Sections with distinct patterns: {n_sections}

Assessment:
""")

    if fill_rate > 0.8:
        print("- HIGH grid fill rate suggests combinatorial structure")
    else:
        print("- PARTIAL grid fill rate - not a simple row×column system")

    if repeat_rate > 0.5:
        print("- HIGH repeat rate suggests enumeration (consistent with CAS findings)")
    else:
        print("- MODERATE repeat rate")

    if n_markers > 10:
        print("- MANY regular-interval tokens - possible structural markers")
    else:
        print("- FEW regular-interval tokens - no obvious row/column markers")

if __name__ == '__main__':
    main()
