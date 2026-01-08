"""
CAS Phase 3: Marker Taxonomy

Question: What marker categories exist (without meaning)?

Key insight from CAS-2: Strong mutual exclusion detected.
ch/da/qo/sh/ok/ot NEVER co-occur in same entry.

This suggests CATEGORY MARKERS - each entry is tagged with ONE class.

Tests:
1. Identify mutually exclusive marker sets
2. Test whether markers partition vocabulary cleanly
3. Determine if markers are hierarchical or flat
4. Map marker coverage across corpus
"""

from collections import defaultdict, Counter
from pathlib import Path
import json
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

project_root = Path(__file__).parent.parent.parent


def load_currier_a_data():
    """Load Currier A tokens with line-level granularity."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        word_idx = 0
        folio_idx = header.index('folio') if 'folio' in header else 1
        line_idx = header.index('line') if 'line' in header else 2
        lang_idx = 6
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


def build_cooccurrence_matrix(data):
    """Build prefix co-occurrence matrix."""
    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Count prefix occurrences and co-occurrences
    prefix_counts = Counter()
    cooccurrence = defaultdict(lambda: defaultdict(int))

    for line_tokens in lines.values():
        line_prefixes = set()
        for token in line_tokens:
            if len(token) >= 2:
                line_prefixes.add(token[:2])

        for p in line_prefixes:
            prefix_counts[p] += 1

        for p1 in line_prefixes:
            for p2 in line_prefixes:
                cooccurrence[p1][p2] += 1

    return prefix_counts, cooccurrence, len(lines)


def test_mutual_exclusion_sets(data):
    """
    Test 1: Identify mutually exclusive marker sets

    Find groups of prefixes that NEVER co-occur.
    """
    print("\n" + "=" * 70)
    print("TEST 1: MUTUAL EXCLUSION SET IDENTIFICATION")
    print("=" * 70)

    prefix_counts, cooccurrence, total_lines = build_cooccurrence_matrix(data)

    # Focus on frequent prefixes (>50 occurrences)
    freq_prefixes = [p for p, c in prefix_counts.most_common() if c >= 50]
    print(f"\nFrequent prefixes (>=50 occurrences): {len(freq_prefixes)}")
    print(f"Top 20: {freq_prefixes[:20]}")

    # Build exclusion matrix
    # exclusion[i][j] = 1 if prefixes i and j NEVER co-occur, 0 otherwise
    n = len(freq_prefixes)
    exclusion = np.zeros((n, n))

    for i, p1 in enumerate(freq_prefixes):
        for j, p2 in enumerate(freq_prefixes):
            if i != j:
                obs = cooccurrence[p1][p2]
                # Expected under independence
                exp = (prefix_counts[p1] / total_lines) * (prefix_counts[p2] / total_lines) * total_lines

                if obs == 0 and exp > 5:
                    exclusion[i][j] = 1
                elif obs < exp * 0.1 and exp > 10:  # <10% of expected
                    exclusion[i][j] = 0.8

    # Find cliques of mutual exclusion
    print(f"\nMutual exclusion patterns (observed=0, expected>5):")

    # Group prefixes by their exclusion pattern
    exclusion_groups = defaultdict(list)
    for i, p in enumerate(freq_prefixes):
        # Get exclusion signature
        sig = tuple(exclusion[i, :])
        exclusion_groups[sig].append(p)

    # Find largest exclusion groups
    print(f"\nNumber of distinct exclusion patterns: {len(exclusion_groups)}")

    # Find the dominant exclusion cluster
    # These are prefixes that exclude EACH OTHER
    dominant_cluster = []
    for i, p1 in enumerate(freq_prefixes):
        is_exclusive = True
        exclude_count = 0
        for j, p2 in enumerate(freq_prefixes):
            if i != j and exclusion[i][j] > 0.5:
                exclude_count += 1

        if exclude_count >= 5:  # Excludes at least 5 other prefixes
            dominant_cluster.append((p1, exclude_count, prefix_counts[p1]))

    dominant_cluster.sort(key=lambda x: -x[1])

    print(f"\nPrefixes with strong mutual exclusion (exclude >= 5 others):")
    for p, exc_count, total in dominant_cluster[:15]:
        print(f"  {p}: excludes {exc_count} prefixes, appears {total}x")

    # Extract marker candidates (prefixes that are mutually exclusive with each other)
    marker_candidates = [p for p, _, _ in dominant_cluster[:10]]

    # Verify they actually exclude each other
    print(f"\nCo-occurrence matrix for top marker candidates:")
    print(f"{'':>6}", end='')
    for p in marker_candidates[:8]:
        print(f"{p:>6}", end='')
    print()

    for i, p1 in enumerate(marker_candidates[:8]):
        print(f"{p1:>6}", end='')
        for j, p2 in enumerate(marker_candidates[:8]):
            if p1 == p2:
                print(f"{'--':>6}", end='')
            else:
                obs = cooccurrence[p1][p2]
                print(f"{obs:>6}", end='')
        print()

    return {
        'freq_prefixes': freq_prefixes,
        'dominant_cluster': dominant_cluster,
        'marker_candidates': marker_candidates
    }


def test_vocabulary_partitioning(data, marker_candidates):
    """
    Test 2: Do markers partition vocabulary cleanly?

    Check if each entry belongs to exactly one marker class.
    """
    print("\n" + "=" * 70)
    print("TEST 2: VOCABULARY PARTITIONING")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Classify each entry by marker
    entry_markers = defaultdict(list)
    unclassified = 0
    multi_classified = 0

    for line_id, tokens in lines.items():
        markers_present = []
        for token in tokens:
            if len(token) >= 2:
                prefix = token[:2]
                if prefix in marker_candidates:
                    markers_present.append(prefix)

        markers_present = list(set(markers_present))

        if len(markers_present) == 0:
            unclassified += 1
        elif len(markers_present) == 1:
            entry_markers[markers_present[0]].append(line_id)
        else:
            multi_classified += 1
            # Record the multi-classification
            entry_markers['MULTI'].append((line_id, markers_present))

    total_entries = len(lines)

    print(f"\nEntry classification by marker:")
    print(f"  Total entries: {total_entries}")
    print(f"  Unclassified (no marker): {unclassified} ({100*unclassified/total_entries:.1f}%)")
    print(f"  Multi-classified (conflict): {multi_classified} ({100*multi_classified/total_entries:.1f}%)")
    print(f"  Cleanly classified: {total_entries - unclassified - multi_classified} ({100*(total_entries - unclassified - multi_classified)/total_entries:.1f}%)")

    print(f"\nEntries per marker:")
    for marker in marker_candidates:
        count = len(entry_markers.get(marker, []))
        pct = 100 * count / total_entries
        print(f"  {marker}: {count} ({pct:.1f}%)")

    # Coverage quality
    classified_pct = (total_entries - unclassified) / total_entries
    clean_pct = (total_entries - unclassified - multi_classified) / total_entries

    print(f"\nPartitioning quality:")
    print(f"  Coverage (any marker): {classified_pct:.1%}")
    print(f"  Clean partitioning: {clean_pct:.1%}")

    if clean_pct > 0.8:
        print("  -> CLEAN PARTITION (markers partition entries cleanly)")
    elif clean_pct > 0.6:
        print("  -> MODERATE partition (some overlap)")
    else:
        print("  -> WEAK partition (significant overlap or gaps)")

    return {
        'total_entries': total_entries,
        'unclassified': unclassified,
        'multi_classified': multi_classified,
        'entry_markers': {k: len(v) for k, v in entry_markers.items() if k != 'MULTI'},
        'classified_pct': classified_pct,
        'clean_pct': clean_pct
    }


def test_marker_hierarchy(data, marker_candidates):
    """
    Test 3: Are markers hierarchical or flat?

    Test for:
    - Nesting (marker A entries always contain marker B features)
    - Subsumption (marker A vocabulary subset of marker B)
    """
    print("\n" + "=" * 70)
    print("TEST 3: MARKER HIERARCHY TEST")
    print("=" * 70)

    # Group by line
    lines = defaultdict(list)
    for d in data:
        lines[d['folio_line']].append(d['token'])

    # Get vocabulary for each marker class
    marker_vocab = defaultdict(set)

    for line_id, tokens in lines.items():
        markers_present = set()
        for token in tokens:
            if len(token) >= 2:
                prefix = token[:2]
                if prefix in marker_candidates:
                    markers_present.add(prefix)

        # If exactly one marker, all tokens belong to that marker's vocabulary
        if len(markers_present) == 1:
            marker = list(markers_present)[0]
            for token in tokens:
                marker_vocab[marker].add(token)

    print(f"\nVocabulary size per marker:")
    for marker in marker_candidates:
        size = len(marker_vocab[marker])
        print(f"  {marker}: {size} unique tokens")

    # Test for subsumption
    print(f"\nVocabulary overlap matrix (Jaccard index):")
    print(f"{'':>6}", end='')
    for m in marker_candidates[:8]:
        print(f"{m:>6}", end='')
    print()

    for m1 in marker_candidates[:8]:
        print(f"{m1:>6}", end='')
        for m2 in marker_candidates[:8]:
            if m1 == m2:
                print(f"{'--':>6}", end='')
            else:
                v1 = marker_vocab[m1]
                v2 = marker_vocab[m2]
                if v1 and v2:
                    jaccard = len(v1 & v2) / len(v1 | v2)
                    print(f"{jaccard:>6.2f}", end='')
                else:
                    print(f"{'?':>6}", end='')
        print()

    # Check for subsumption
    subsumption = []
    for m1 in marker_candidates:
        for m2 in marker_candidates:
            if m1 != m2:
                v1 = marker_vocab[m1]
                v2 = marker_vocab[m2]
                if v1 and v2:
                    # Is v1 subset of v2?
                    if len(v1 - v2) == 0:
                        subsumption.append((m1, m2, 'subset'))
                    elif len(v1 - v2) / len(v1) < 0.1:
                        subsumption.append((m1, m2, 'near-subset'))

    if subsumption:
        print(f"\nSubsumption relationships detected:")
        for m1, m2, rel in subsumption:
            print(f"  {m1} is {rel} of {m2}")
        print("  -> HIERARCHICAL structure")
    else:
        print(f"\nNo subsumption relationships detected")
        print("  -> FLAT structure (markers are peers)")

    return {
        'marker_vocab_sizes': {m: len(v) for m, v in marker_vocab.items()},
        'subsumption': subsumption,
        'is_hierarchical': len(subsumption) > 0
    }


def test_marker_section_distribution(data, marker_candidates):
    """
    Test 4: How are markers distributed across sections?
    """
    print("\n" + "=" * 70)
    print("TEST 4: MARKER-SECTION DISTRIBUTION")
    print("=" * 70)

    # Group by line with section
    lines = defaultdict(lambda: {'tokens': [], 'section': ''})
    for d in data:
        lines[d['folio_line']]['tokens'].append(d['token'])
        lines[d['folio_line']]['section'] = d['section']

    # Count marker occurrences by section
    section_markers = defaultdict(lambda: defaultdict(int))
    section_totals = defaultdict(int)

    for line_id, info in lines.items():
        section = info['section']
        section_totals[section] += 1

        markers_present = set()
        for token in info['tokens']:
            if len(token) >= 2:
                prefix = token[:2]
                if prefix in marker_candidates:
                    markers_present.add(prefix)

        for marker in markers_present:
            section_markers[section][marker] += 1

    sections = sorted(section_totals.keys())

    print(f"\nMarker distribution by section:")
    print(f"{'Section':<8} {'Total':<8}", end='')
    for m in marker_candidates[:8]:
        print(f"{m:>6}", end='')
    print()
    print("-" * 60)

    for section in sections:
        if section_totals[section] > 0:
            print(f"{section:<8} {section_totals[section]:<8}", end='')
            for m in marker_candidates[:8]:
                count = section_markers[section][m]
                pct = 100 * count / section_totals[section]
                print(f"{pct:>5.0f}%", end='')
            print()

    # Chi-square test for section-marker independence
    print(f"\nSection-marker independence test:")

    # Build contingency table
    observed = []
    for section in sections:
        if section_totals[section] >= 50:  # Only sections with enough data
            row = [section_markers[section].get(m, 0) for m in marker_candidates[:8]]
            if sum(row) > 0:
                observed.append(row)

    if len(observed) >= 3:
        from scipy import stats as sp_stats
        observed = np.array(observed)
        chi2, p, dof, expected = sp_stats.chi2_contingency(observed)
        print(f"  Chi2 = {chi2:.2f}, df = {dof}, p = {p:.6f}")

        if p < 0.01:
            print("  -> STRONG section-marker dependence (markers are section-specific)")
        elif p < 0.05:
            print("  -> MODERATE section-marker dependence")
        else:
            print("  -> NO significant section-marker dependence (markers distributed evenly)")

    return {
        'section_markers': {s: dict(m) for s, m in section_markers.items()},
        'section_totals': dict(section_totals)
    }


def synthesize_markers(results):
    """Synthesize marker taxonomy results."""
    print("\n" + "=" * 70)
    print("SYNTHESIS: MARKER TAXONOMY")
    print("=" * 70)

    marker_candidates = results['exclusion']['marker_candidates']

    print(f"\nIdentified marker prefixes: {marker_candidates[:8]}")

    # Partitioning quality
    clean_pct = results['partition']['clean_pct']

    print(f"\nPartitioning quality: {clean_pct:.1%} cleanly classified")

    # Hierarchy
    is_hier = results['hierarchy']['is_hierarchical']
    print(f"Structure: {'HIERARCHICAL' if is_hier else 'FLAT'}")

    # Final characterization
    if clean_pct > 0.7 and not is_hier:
        verdict = 'CATEGORICAL_TAGS'
        interpretation = """
Currier A uses a FLAT CATEGORICAL TAGGING system:
- Each entry is marked with ONE category prefix (ch, qo, sh, da, etc.)
- Categories are mutually exclusive (never co-occur)
- Categories partition entries cleanly (>70%)
- No hierarchical nesting between categories
- Categories may be section-specific

This is a CLASSIFICATION SCHEMA, not a grammar.
        """
    elif clean_pct > 0.5 and is_hier:
        verdict = 'HIERARCHICAL_TAXONOMY'
        interpretation = "Currier A uses a hierarchical taxonomy with subsumption relationships."
    elif clean_pct > 0.5:
        verdict = 'WEAK_TAGGING'
        interpretation = "Currier A shows weak categorical tagging with significant overlap."
    else:
        verdict = 'UNSTRUCTURED'
        interpretation = "Currier A does not show clear marker structure."

    print(f"\n{'='*70}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*70}")
    print(interpretation)

    return verdict, interpretation


def main():
    print("=" * 70)
    print("CAS PHASE 3: MARKER TAXONOMY")
    print("=" * 70)
    print("\nQuestion: What marker categories exist (without meaning)?")

    data = load_currier_a_data()
    print(f"\nLoaded {len(data)} Currier A tokens")

    # Test 1: Find mutually exclusive markers
    exclusion_results = test_mutual_exclusion_sets(data)
    marker_candidates = exclusion_results['marker_candidates']

    # Test 2: Vocabulary partitioning
    partition_results = test_vocabulary_partitioning(data, marker_candidates)

    # Test 3: Hierarchy test
    hierarchy_results = test_marker_hierarchy(data, marker_candidates)

    # Test 4: Section distribution
    section_results = test_marker_section_distribution(data, marker_candidates)

    results = {
        'exclusion': exclusion_results,
        'partition': partition_results,
        'hierarchy': hierarchy_results,
        'section': section_results
    }

    verdict, interpretation = synthesize_markers(results)

    results['verdict'] = verdict
    results['interpretation'] = interpretation

    # Save results
    output_path = Path(__file__).parent / 'cas_phase3_results.json'

    # Convert for JSON
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
