"""
CAS-DEEP Track 4: Section Correlation Analysis

Question: Does multiplicity vary meaningfully by section?

Tests:
- T4.1: Mean count by section
- T4.2: Block vocabulary overlap between sections
- T4.3: Marker x section distribution
- T4.4: Section-exclusive patterns
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy.stats import kruskal, chi2_contingency

project_root = Path(__file__).parent.parent.parent


def load_currier_a_lines():
    """Load Currier A data grouped by line."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    lines = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': ''})

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
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


def test_4_1_mean_count_by_section(entries):
    """T4.1: Mean count by section."""
    print("\n" + "=" * 70)
    print("T4.1: MEAN COUNT BY SECTION")
    print("=" * 70)

    section_counts = defaultdict(list)

    for entry in entries:
        section = entry['section']
        if section:
            section_counts[section].append(entry['count'])

    print("\nCount statistics by section:")
    print()

    sections = sorted(section_counts.keys())
    for section in sections:
        counts = section_counts[section]
        print(f"  Section {section}:")
        print(f"    n = {len(counts)}")
        print(f"    mean = {np.mean(counts):.2f}")
        print(f"    median = {np.median(counts):.1f}")
        print(f"    std = {np.std(counts):.2f}")
        print(f"    range = {min(counts)}-{max(counts)}")

    # Kruskal-Wallis test (non-parametric ANOVA)
    groups = [section_counts[s] for s in sections if len(section_counts[s]) >= 5]
    if len(groups) >= 2:
        stat, p = kruskal(*groups)
        print(f"\nKruskal-Wallis test:")
        print(f"  H = {stat:.2f}")
        print(f"  p = {p:.6f}")

        if p < 0.05:
            print("  -> Sections have DIFFERENT count distributions")
            verdict = "SECTION_DIFFERENT"
        else:
            print("  -> Sections have SIMILAR count distributions")
            verdict = "SECTION_SIMILAR"
    else:
        print("\nInsufficient sections for statistical test")
        verdict = "INSUFFICIENT_DATA"

    return {
        'section_stats': {s: {
            'n': len(section_counts[s]),
            'mean': float(np.mean(section_counts[s])),
            'median': float(np.median(section_counts[s])),
            'std': float(np.std(section_counts[s]))
        } for s in sections},
        'verdict': verdict
    }


def test_4_2_vocabulary_overlap(entries):
    """T4.2: Block vocabulary overlap between sections."""
    print("\n" + "=" * 70)
    print("T4.2: BLOCK VOCABULARY OVERLAP BETWEEN SECTIONS")
    print("=" * 70)

    section_vocab = defaultdict(set)

    for entry in entries:
        section = entry['section']
        if section:
            for token in entry['block']:
                section_vocab[section].add(token)

    sections = sorted(section_vocab.keys())

    print("\nVocabulary size by section:")
    for section in sections:
        print(f"  Section {section}: {len(section_vocab[section])} unique tokens")

    print("\nJaccard overlap matrix:")
    header = "        " + "  ".join(f"{s:>6}" for s in sections)
    print(header)

    overlaps = {}
    for s1 in sections:
        row = []
        for s2 in sections:
            if s1 == s2:
                row.append("--")
            else:
                v1, v2 = section_vocab[s1], section_vocab[s2]
                if v1 and v2:
                    jaccard = len(v1 & v2) / len(v1 | v2)
                    row.append(f"{jaccard:.3f}")
                    overlaps[f"{s1}-{s2}"] = jaccard
                else:
                    row.append("N/A")
        print(f"    {s1}   " + "  ".join(f"{r:>6}" for r in row))

    if overlaps:
        mean_overlap = np.mean(list(overlaps.values()))
        print(f"\nMean Jaccard overlap: {mean_overlap:.3f}")

        if mean_overlap < 0.2:
            print("  -> Sections have HIGHLY DISTINCT vocabularies")
            verdict = "HIGHLY_DISTINCT"
        elif mean_overlap < 0.4:
            print("  -> Sections have MODERATELY DISTINCT vocabularies")
            verdict = "MODERATELY_DISTINCT"
        else:
            print("  -> Sections have OVERLAPPING vocabularies")
            verdict = "OVERLAPPING"
    else:
        verdict = "INSUFFICIENT_DATA"

    return {
        'vocab_sizes': {s: len(section_vocab[s]) for s in sections},
        'overlaps': overlaps,
        'verdict': verdict
    }


def test_4_3_marker_section_distribution(entries):
    """T4.3: Marker x section distribution."""
    print("\n" + "=" * 70)
    print("T4.3: MARKER x SECTION DISTRIBUTION")
    print("=" * 70)

    marker_section = defaultdict(lambda: defaultdict(int))

    for entry in entries:
        marker = entry['marker']
        section = entry['section']
        if marker != 'NONE' and section:
            marker_section[marker][section] += 1

    markers = sorted(set(entry['marker'] for entry in entries if entry['marker'] != 'NONE'))
    sections = sorted(set(entry['section'] for entry in entries if entry['section']))

    print("\nContingency table (marker x section):")
    header = "Marker  " + "  ".join(f"{s:>6}" for s in sections) + "   Total"
    print(header)
    print("-" * len(header))

    table = []
    for marker in markers:
        row = [marker_section[marker].get(s, 0) for s in sections]
        row_total = sum(row)
        table.append(row)
        print(f"{marker:>6}  " + "  ".join(f"{v:>6}" for v in row) + f"   {row_total:>5}")

    col_totals = [sum(marker_section[m].get(s, 0) for m in markers) for s in sections]
    print("-" * len(header))
    print(f" Total  " + "  ".join(f"{v:>6}" for v in col_totals) + f"   {sum(col_totals):>5}")

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

            if p < 0.001:
                print("  -> Marker distribution STRONGLY DEPENDS on section")
                verdict = "STRONGLY_DEPENDENT"
            elif p < 0.05:
                print("  -> Marker distribution DEPENDS on section")
                verdict = "DEPENDENT"
            else:
                print("  -> Marker distribution INDEPENDENT of section")
                verdict = "INDEPENDENT"
        except Exception as e:
            print(f"\nChi-square test failed: {e}")
            verdict = "TEST_FAILED"
    else:
        print("\nInsufficient data for chi-square test")
        verdict = "INSUFFICIENT_DATA"

    # Calculate marker concentration by section
    print("\nMarker concentration by section:")
    for section in sections:
        section_markers = [(m, marker_section[m].get(section, 0)) for m in markers]
        section_markers.sort(key=lambda x: -x[1])
        total = sum(v for _, v in section_markers)
        if total > 0:
            top_markers = section_markers[:3]
            top_pct = 100 * sum(v for _, v in top_markers) / total
            print(f"  Section {section}: top 3 = {', '.join(f'{m}({v})' for m, v in top_markers)} ({top_pct:.1f}%)")

    return {
        'contingency': {m: dict(marker_section[m]) for m in markers},
        'verdict': verdict
    }


def test_4_4_section_exclusive_patterns(entries):
    """T4.4: Section-exclusive patterns."""
    print("\n" + "=" * 70)
    print("T4.4: SECTION-EXCLUSIVE PATTERNS")
    print("=" * 70)

    # Find block patterns unique to each section
    section_blocks = defaultdict(set)
    block_sections = defaultdict(set)

    for entry in entries:
        section = entry['section']
        if section:
            # Create a normalized block signature
            block_sig = ' '.join(entry['block'])
            section_blocks[section].add(block_sig)
            block_sections[block_sig].add(section)

    sections = sorted(section_blocks.keys())

    # Count section-exclusive blocks
    print("\nBlock exclusivity by section:")
    section_exclusive = {}

    for section in sections:
        blocks = section_blocks[section]
        exclusive = sum(1 for b in blocks if len(block_sections[b]) == 1)
        pct = 100 * exclusive / len(blocks) if blocks else 0
        section_exclusive[section] = pct
        print(f"  Section {section}: {exclusive}/{len(blocks)} exclusive ({pct:.1f}%)")

    # Overall exclusivity
    total_blocks = sum(len(section_blocks[s]) for s in sections)
    total_exclusive = sum(1 for b, sections_set in block_sections.items()
                         if len(sections_set) == 1)

    overall_exclusivity = 100 * total_exclusive / total_blocks if total_blocks > 0 else 0

    print(f"\nOverall: {total_exclusive}/{total_blocks} blocks are section-exclusive ({overall_exclusivity:.1f}%)")

    # Show some cross-section blocks
    cross_section_blocks = [(b, sects) for b, sects in block_sections.items() if len(sects) > 1]
    if cross_section_blocks:
        print(f"\nCross-section blocks ({len(cross_section_blocks)} found):")
        for block, sects in cross_section_blocks[:5]:
            print(f"  [{', '.join(sorted(sects))}]: {block[:50]}...")

    if overall_exclusivity > 90:
        verdict = "HIGHLY_EXCLUSIVE"
    elif overall_exclusivity > 70:
        verdict = "MOSTLY_EXCLUSIVE"
    else:
        verdict = "MIXED"

    print(f"\nVerdict: {verdict}")

    return {
        'section_exclusivity': section_exclusive,
        'overall_exclusivity': overall_exclusivity,
        'cross_section_count': len(cross_section_blocks),
        'verdict': verdict
    }


def main():
    print("=" * 70)
    print("CAS-DEEP TRACK 4: SECTION CORRELATION")
    print("=" * 70)

    lines = load_currier_a_lines()
    print(f"\nLoaded {len(lines)} Currier A lines")

    entries = classify_entries(lines)
    print(f"Entries with repeating blocks: {len(entries)}")

    # Run tests
    results = {}
    results['t4_1'] = test_4_1_mean_count_by_section(entries)
    results['t4_2'] = test_4_2_vocabulary_overlap(entries)
    results['t4_3'] = test_4_3_marker_section_distribution(entries)
    results['t4_4'] = test_4_4_section_exclusive_patterns(entries)

    # Summary
    print("\n" + "=" * 70)
    print("TRACK 4 SUMMARY")
    print("=" * 70)

    print(f"\nT4.1 Mean count by section: {results['t4_1']['verdict']}")
    print(f"T4.2 Vocabulary overlap: {results['t4_2']['verdict']}")
    print(f"T4.3 Marker x Section: {results['t4_3']['verdict']}")
    print(f"T4.4 Block exclusivity: {results['t4_4']['verdict']}")

    # Save results
    output_path = Path(__file__).parent / 'cas_deep_track4_results.json'

    def convert_for_json(obj):
        if isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_for_json(item) for item in obj]
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, set):
            return list(obj)
        else:
            return obj

    with open(output_path, 'w') as f:
        json.dump(convert_for_json(results), f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
