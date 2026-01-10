#!/usr/bin/env python
"""
Adjacent Entry Analysis: Decomposing C346

Question: What drives the 1.31x vocabulary overlap between adjacent entries?

Decomposes the similarity into:
1. Marker continuity (same prefix family)
2. Suffix overlap (shared suffixes)
3. Middle component overlap
4. Token-level overlap (full vocabulary)

Goal: Reveal the organizational logic of the Currier A catalog.
"""
import sys
from collections import defaultdict, Counter
from itertools import combinations
import numpy as np
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import MARKER_FAMILIES, A_UNIVERSAL_SUFFIXES, EXTENDED_PREFIX_MAP

# =============================================================================
# DATA LOADING
# =============================================================================

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

def load_currier_a_entries():
    """Load Currier A entries grouped by folio."""

    entries_by_folio = defaultdict(list)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                # Only Currier A
                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None:
                        entries_by_folio[current_entry['folio']].append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        # Don't forget last entry
        if current_entry is not None:
            entries_by_folio[current_entry['folio']].append(current_entry)

    return entries_by_folio


# =============================================================================
# MORPHOLOGICAL EXTRACTION
# =============================================================================

def extract_prefix(token):
    """Extract marker prefix from token."""
    token_lower = token.lower()

    # Check extended prefixes first (3-char)
    if len(token_lower) >= 3:
        prefix3 = token_lower[:3]
        if prefix3 in EXTENDED_PREFIX_MAP:
            return EXTENDED_PREFIX_MAP[prefix3]  # Map to base family

    # Check standard 2-char prefixes
    if len(token_lower) >= 2:
        prefix2 = token_lower[:2]
        if prefix2 in MARKER_FAMILIES:
            return prefix2

    return None


def extract_suffix(token):
    """Extract suffix from token (longest match from A_UNIVERSAL_SUFFIXES)."""
    token_lower = token.lower()

    for suffix_len in range(min(5, len(token_lower)), 0, -1):
        candidate = token_lower[-suffix_len:]
        if candidate in A_UNIVERSAL_SUFFIXES:
            return candidate

    # Fallback: last 2 chars
    if len(token_lower) >= 2:
        return token_lower[-2:]
    return token_lower


def extract_middle(token, prefix, suffix):
    """Extract middle component between prefix and suffix."""
    token_lower = token.lower()

    prefix_len = len(prefix) if prefix else 0
    suffix_len = len(suffix) if suffix else 0

    if prefix_len + suffix_len < len(token_lower):
        return token_lower[prefix_len:-suffix_len] if suffix_len > 0 else token_lower[prefix_len:]
    return ''


def decompose_entry(entry):
    """Decompose an entry into morphological components."""
    prefixes = []
    suffixes = []
    middles = []

    for token in entry['tokens']:
        prefix = extract_prefix(token)
        suffix = extract_suffix(token)
        middle = extract_middle(token, prefix, suffix)

        if prefix:
            prefixes.append(prefix)
        if suffix:
            suffixes.append(suffix)
        if middle:
            middles.append(middle)

    return {
        'prefixes': set(prefixes),
        'suffixes': set(suffixes),
        'middles': set(middles),
        'tokens': set(entry['tokens']),
        'prefix_counter': Counter(prefixes),
    }


# =============================================================================
# SIMILARITY METRICS
# =============================================================================

def jaccard(set1, set2):
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def marker_continuity(decomp1, decomp2):
    """Check if entries share any marker prefix."""
    shared = decomp1['prefixes'] & decomp2['prefixes']
    return 1.0 if shared else 0.0


def dominant_marker_match(decomp1, decomp2):
    """Check if dominant marker is the same."""
    if not decomp1['prefix_counter'] or not decomp2['prefix_counter']:
        return 0.0

    dom1 = decomp1['prefix_counter'].most_common(1)[0][0]
    dom2 = decomp2['prefix_counter'].most_common(1)[0][0]

    return 1.0 if dom1 == dom2 else 0.0


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def analyze_adjacent_similarity(entries_by_folio):
    """Analyze what drives adjacent entry similarity."""

    print("=" * 70)
    print("ADJACENT ENTRY DECOMPOSITION ANALYSIS")
    print("=" * 70)

    # Collect metrics for adjacent vs non-adjacent pairs
    adjacent = {
        'token_jaccard': [],
        'prefix_jaccard': [],
        'suffix_jaccard': [],
        'middle_jaccard': [],
        'marker_continuity': [],
        'dominant_marker_match': [],
    }

    nonadjacent = {
        'token_jaccard': [],
        'prefix_jaccard': [],
        'suffix_jaccard': [],
        'middle_jaccard': [],
        'marker_continuity': [],
        'dominant_marker_match': [],
    }

    # Track marker transitions
    marker_transitions = {'adjacent': [], 'nonadjacent': []}

    for folio, entries in entries_by_folio.items():
        if len(entries) < 3:
            continue

        # Sort by line number
        sorted_entries = sorted(entries, key=lambda e: int(e['line']) if e['line'].isdigit() else 0)

        # Decompose all entries
        decomposed = [decompose_entry(e) for e in sorted_entries]

        for i in range(len(decomposed)):
            d1 = decomposed[i]
            if len(d1['tokens']) < 2:
                continue

            for j in range(i+1, len(decomposed)):
                d2 = decomposed[j]
                if len(d2['tokens']) < 2:
                    continue

                # Calculate all metrics
                metrics = {
                    'token_jaccard': jaccard(d1['tokens'], d2['tokens']),
                    'prefix_jaccard': jaccard(d1['prefixes'], d2['prefixes']),
                    'suffix_jaccard': jaccard(d1['suffixes'], d2['suffixes']),
                    'middle_jaccard': jaccard(d1['middles'], d2['middles']),
                    'marker_continuity': marker_continuity(d1, d2),
                    'dominant_marker_match': dominant_marker_match(d1, d2),
                }

                # Categorize
                is_adjacent = (j == i + 1)
                target = adjacent if is_adjacent else nonadjacent

                for key, value in metrics.items():
                    target[key].append(value)

                # Track marker transition
                if d1['prefix_counter'] and d2['prefix_counter']:
                    dom1 = d1['prefix_counter'].most_common(1)[0][0]
                    dom2 = d2['prefix_counter'].most_common(1)[0][0]
                    transition = (dom1, dom2)
                    if is_adjacent:
                        marker_transitions['adjacent'].append(transition)
                    else:
                        marker_transitions['nonadjacent'].append(transition)

    # Print results
    print(f"\nSample sizes:")
    print(f"  Adjacent pairs:     {len(adjacent['token_jaccard'])}")
    print(f"  Non-adjacent pairs: {len(nonadjacent['token_jaccard'])}")

    print("\n" + "-" * 70)
    print("SIMILARITY DECOMPOSITION")
    print("-" * 70)

    print(f"\n{'Component':<25} {'Adjacent':<12} {'Non-adj':<12} {'Ratio':<10} {'p-value':<12}")
    print("-" * 70)

    results = {}

    for metric in ['token_jaccard', 'prefix_jaccard', 'suffix_jaccard',
                   'middle_jaccard', 'marker_continuity', 'dominant_marker_match']:

        adj_vals = adjacent[metric]
        nonadj_vals = nonadjacent[metric]

        adj_mean = np.mean(adj_vals) if adj_vals else 0
        nonadj_mean = np.mean(nonadj_vals) if nonadj_vals else 0

        ratio = adj_mean / nonadj_mean if nonadj_mean > 0 else float('inf')

        if adj_vals and nonadj_vals:
            _, p_value = stats.mannwhitneyu(adj_vals, nonadj_vals, alternative='greater')
        else:
            p_value = 1.0

        sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""

        print(f"{metric:<25} {adj_mean:<12.4f} {nonadj_mean:<12.4f} {ratio:<10.2f} {p_value:<10.6f} {sig}")

        results[metric] = {
            'adjacent_mean': adj_mean,
            'nonadjacent_mean': nonadj_mean,
            'ratio': ratio,
            'p_value': p_value,
        }

    # Marker transition analysis
    print("\n" + "-" * 70)
    print("MARKER TRANSITION ANALYSIS")
    print("-" * 70)

    adj_transitions = Counter(marker_transitions['adjacent'])
    nonadj_transitions = Counter(marker_transitions['nonadjacent'])

    # Same-marker transitions
    adj_same = sum(c for (m1, m2), c in adj_transitions.items() if m1 == m2)
    adj_total = sum(adj_transitions.values())
    nonadj_same = sum(c for (m1, m2), c in nonadj_transitions.items() if m1 == m2)
    nonadj_total = sum(nonadj_transitions.values())

    adj_same_pct = 100 * adj_same / adj_total if adj_total > 0 else 0
    nonadj_same_pct = 100 * nonadj_same / nonadj_total if nonadj_total > 0 else 0

    print(f"\nSame-marker transitions:")
    print(f"  Adjacent:     {adj_same}/{adj_total} ({adj_same_pct:.1f}%)")
    print(f"  Non-adjacent: {nonadj_same}/{nonadj_total} ({nonadj_same_pct:.1f}%)")
    print(f"  Ratio: {adj_same_pct / nonadj_same_pct:.2f}x" if nonadj_same_pct > 0 else "  Ratio: N/A")

    # Top adjacent marker sequences
    print(f"\nTop 10 adjacent marker transitions:")
    for (m1, m2), count in adj_transitions.most_common(10):
        arrow = "->" if m1 != m2 else "=="
        print(f"  {m1} {arrow} {m2}: {count}")

    # Sister pair analysis
    print("\n" + "-" * 70)
    print("SISTER PAIR ANALYSIS")
    print("-" * 70)

    sister_pairs = [('ch', 'sh'), ('ok', 'ot')]

    for pair in sister_pairs:
        m1, m2 = pair

        # Adjacent transitions between sisters
        adj_sister = adj_transitions.get((m1, m2), 0) + adj_transitions.get((m2, m1), 0)
        nonadj_sister = nonadj_transitions.get((m1, m2), 0) + nonadj_transitions.get((m2, m1), 0)

        # Same-marker for these families
        adj_m1_same = adj_transitions.get((m1, m1), 0)
        adj_m2_same = adj_transitions.get((m2, m2), 0)

        print(f"\n{m1}-{m2} pair:")
        print(f"  Adjacent same {m1}: {adj_m1_same}")
        print(f"  Adjacent same {m2}: {adj_m2_same}")
        print(f"  Adjacent {m1}<->{m2}: {adj_sister}")

    # Synthesis
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    # Find dominant driver
    drivers = []
    for metric, data in results.items():
        if data['p_value'] < 0.05 and data['ratio'] > 1.1:
            drivers.append((metric, data['ratio'], data['p_value']))

    drivers.sort(key=lambda x: x[1], reverse=True)

    print("\nSignificant drivers of adjacent similarity (sorted by ratio):")
    for metric, ratio, p in drivers:
        print(f"  {metric}: {ratio:.2f}x (p={p:.6f})")

    if drivers:
        primary_driver = drivers[0][0]
        print(f"\nPRIMARY DRIVER: {primary_driver}")

        if 'prefix' in primary_driver or 'marker' in primary_driver:
            print("\nINTERPRETATION: Catalog is organized by MARKER FAMILY")
            print("Adjacent entries tend to share the same prefix category.")
        elif 'suffix' in primary_driver:
            print("\nINTERPRETATION: Catalog is organized by PROPERTY/SUFFIX")
            print("Adjacent entries tend to share the same suffix/property.")
        elif 'middle' in primary_driver:
            print("\nINTERPRETATION: Catalog is organized by SUB-TYPE/MIDDLE")
            print("Adjacent entries tend to share middle components (variants grouped).")
        elif 'token' in primary_driver:
            print("\nINTERPRETATION: Catalog has VOCABULARY CLUSTERING")
            print("Adjacent entries share full tokens (possibly continuing/related content).")
    else:
        print("\nNo significant drivers found - adjacent similarity may be weak or uniform.")

    return results, marker_transitions


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("\nLoading Currier A entries...")
    entries_by_folio = load_currier_a_entries()

    total_entries = sum(len(e) for e in entries_by_folio.values())
    print(f"Loaded {total_entries} entries across {len(entries_by_folio)} folios")

    results, transitions = analyze_adjacent_similarity(entries_by_folio)
