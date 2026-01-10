#!/usr/bin/env python
"""
DA Punctuation Analysis

Question: Is DA a structural punctuation marker rather than a content classifier?

Tests:
1. Position histogram - where does DA appear within entries?
2. Block interaction - does DA separate repetition blocks?
3. Co-occurrence patterns - what appears before/after DA?
4. Segmentation effect - what happens if we segment on DA?

Hypothesis: DA functions as record articulation punctuation,
like "new subrecord" or "register delimiter".
"""
import sys
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'


# =============================================================================
# DATA LOADING
# =============================================================================

def load_currier_a_entries():
    """Load Currier A entries as lists of tokens."""
    entries = []

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

                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None and current_entry['tokens']:
                        entries.append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries.append(current_entry)

    return entries


def get_prefix(token):
    """Extract marker prefix from token."""
    token_lower = token.lower()
    for prefix in sorted(MARKER_FAMILIES, key=len, reverse=True):
        if token_lower.startswith(prefix):
            return prefix
    return None


def is_da_token(token):
    """Check if token has DA prefix."""
    return token.lower().startswith('da')


# =============================================================================
# TEST 1: POSITION HISTOGRAM
# =============================================================================

def test_position_histogram(entries):
    """Where does DA appear within entries?"""

    print("=" * 70)
    print("TEST 1: DA POSITION WITHIN ENTRIES")
    print("=" * 70)

    # Track absolute and relative positions
    da_absolute_positions = []  # 0, 1, 2, ...
    da_relative_positions = []  # 0.0 to 1.0 (normalized)

    # Track first/last positions specifically
    da_first = 0
    da_last = 0
    da_middle = 0

    # Track by entry length
    position_by_length = defaultdict(list)

    total_entries = 0
    entries_with_da = 0

    for entry in entries:
        tokens = entry['tokens']
        if len(tokens) < 2:
            continue

        total_entries += 1
        entry_has_da = False

        for i, token in enumerate(tokens):
            if is_da_token(token):
                entry_has_da = True
                da_absolute_positions.append(i)
                da_relative_positions.append(i / (len(tokens) - 1) if len(tokens) > 1 else 0.5)
                position_by_length[len(tokens)].append(i)

                if i == 0:
                    da_first += 1
                elif i == len(tokens) - 1:
                    da_last += 1
                else:
                    da_middle += 1

        if entry_has_da:
            entries_with_da += 1

    total_da = len(da_absolute_positions)

    print(f"\nBasic counts:")
    print(f"  Total entries (len >= 2): {total_entries}")
    print(f"  Entries containing DA: {entries_with_da} ({100*entries_with_da/total_entries:.1f}%)")
    print(f"  Total DA tokens: {total_da}")

    print(f"\nPosition breakdown:")
    print(f"  First position (index 0): {da_first} ({100*da_first/total_da:.1f}%)")
    print(f"  Last position: {da_last} ({100*da_last/total_da:.1f}%)")
    print(f"  Middle positions: {da_middle} ({100*da_middle/total_da:.1f}%)")

    # Relative position distribution
    print(f"\nRelative position distribution (0=start, 1=end):")
    quartiles = [0, 0.25, 0.5, 0.75, 1.0]
    for i in range(len(quartiles) - 1):
        count = sum(1 for p in da_relative_positions if quartiles[i] <= p < quartiles[i+1])
        pct = 100 * count / total_da if total_da > 0 else 0
        print(f"  [{quartiles[i]:.2f}-{quartiles[i+1]:.2f}): {count} ({pct:.1f}%)")

    # Last quartile edge case
    count = sum(1 for p in da_relative_positions if p == 1.0)
    print(f"  [1.00]: {count} ({100*count/total_da:.1f}%)")

    # Compare to expected uniform distribution
    print(f"\nMean relative position: {np.mean(da_relative_positions):.3f} (uniform would be 0.5)")

    # Chi-square test against uniform
    observed = [
        sum(1 for p in da_relative_positions if 0 <= p < 0.33),
        sum(1 for p in da_relative_positions if 0.33 <= p < 0.67),
        sum(1 for p in da_relative_positions if 0.67 <= p <= 1.0),
    ]
    expected = [total_da / 3] * 3
    chi2, p_value = stats.chisquare(observed, expected)
    print(f"\nChi-square test (uniform across thirds):")
    print(f"  Observed: {observed}")
    print(f"  Expected: {[int(e) for e in expected]}")
    print(f"  Chi2: {chi2:.2f}, p-value: {p_value:.6f}")

    if p_value < 0.001:
        print("  -> SIGNIFICANT: DA position is NOT uniform")

    return {
        'total_da': total_da,
        'da_first': da_first,
        'da_last': da_last,
        'da_middle': da_middle,
        'mean_relative': np.mean(da_relative_positions),
        'position_chi2_p': p_value,
    }


# =============================================================================
# TEST 2: DA AND ADJACENT TOKENS
# =============================================================================

def test_adjacency_patterns(entries):
    """What appears immediately before and after DA?"""

    print("\n" + "=" * 70)
    print("TEST 2: DA ADJACENCY PATTERNS")
    print("=" * 70)

    before_da = Counter()  # prefix of token before DA
    after_da = Counter()   # prefix of token after DA

    # Also track specific tokens
    tokens_before_da = Counter()
    tokens_after_da = Counter()

    # DA-DA adjacency
    da_da_count = 0
    total_da_with_neighbors = 0

    for entry in entries:
        tokens = entry['tokens']

        for i, token in enumerate(tokens):
            if is_da_token(token):
                # Token before
                if i > 0:
                    prev_token = tokens[i-1]
                    prev_prefix = get_prefix(prev_token)
                    if prev_prefix:
                        before_da[prev_prefix] += 1
                    tokens_before_da[prev_token.lower()] += 1

                    if is_da_token(prev_token):
                        da_da_count += 1

                # Token after
                if i < len(tokens) - 1:
                    next_token = tokens[i+1]
                    next_prefix = get_prefix(next_token)
                    if next_prefix:
                        after_da[next_prefix] += 1
                    tokens_after_da[next_token.lower()] += 1
                    total_da_with_neighbors += 1

    print(f"\nPrefixes BEFORE DA:")
    total_before = sum(before_da.values())
    for prefix, count in before_da.most_common():
        print(f"  {prefix}: {count} ({100*count/total_before:.1f}%)")

    print(f"\nPrefixes AFTER DA:")
    total_after = sum(after_da.values())
    for prefix, count in after_da.most_common():
        print(f"  {prefix}: {count} ({100*count/total_after:.1f}%)")

    print(f"\nDA-DA adjacency: {da_da_count} pairs")

    print(f"\nMost common tokens BEFORE DA:")
    for token, count in tokens_before_da.most_common(10):
        print(f"  {token}: {count}")

    print(f"\nMost common tokens AFTER DA:")
    for token, count in tokens_after_da.most_common(10):
        print(f"  {token}: {count}")

    # Compare before/after distributions
    print(f"\nAsymmetry analysis:")
    for prefix in MARKER_FAMILIES:
        before_pct = 100 * before_da.get(prefix, 0) / total_before if total_before > 0 else 0
        after_pct = 100 * after_da.get(prefix, 0) / total_after if total_after > 0 else 0
        diff = after_pct - before_pct
        if abs(diff) > 3:  # Only show meaningful differences
            direction = "more after" if diff > 0 else "more before"
            print(f"  {prefix}: {direction} DA ({abs(diff):.1f}pp)")

    return {
        'before_da': dict(before_da),
        'after_da': dict(after_da),
        'da_da_count': da_da_count,
    }


# =============================================================================
# TEST 3: DA AND ENTRY STRUCTURE
# =============================================================================

def test_structural_role(entries):
    """Does DA mark structural boundaries within entries?"""

    print("\n" + "=" * 70)
    print("TEST 3: DA STRUCTURAL ROLE")
    print("=" * 70)

    # Look for patterns like: [block] DA [block] DA [block]
    # Where blocks are sequences of same-prefix tokens

    entries_with_da = [e for e in entries if any(is_da_token(t) for t in e['tokens'])]

    print(f"\nAnalyzing {len(entries_with_da)} entries containing DA")

    # Pattern analysis: DA between different prefix runs
    da_separates_prefixes = 0
    da_within_same_prefix = 0

    for entry in entries_with_da:
        tokens = entry['tokens']

        for i, token in enumerate(tokens):
            if is_da_token(token) and i > 0 and i < len(tokens) - 1:
                prev_prefix = get_prefix(tokens[i-1])
                next_prefix = get_prefix(tokens[i+1])

                if prev_prefix and next_prefix:
                    if prev_prefix != next_prefix:
                        da_separates_prefixes += 1
                    else:
                        da_within_same_prefix += 1

    total_internal_da = da_separates_prefixes + da_within_same_prefix

    print(f"\nDA as separator vs internal:")
    print(f"  DA between DIFFERENT prefix runs: {da_separates_prefixes} ({100*da_separates_prefixes/total_internal_da:.1f}%)" if total_internal_da > 0 else "  No internal DA")
    print(f"  DA within SAME prefix run: {da_within_same_prefix} ({100*da_within_same_prefix/total_internal_da:.1f}%)" if total_internal_da > 0 else "")

    # Segment on DA and analyze resulting sub-entries
    print(f"\nSegmentation analysis:")

    segment_lengths = []
    segment_prefix_diversity = []

    for entry in entries_with_da:
        tokens = entry['tokens']

        # Split on DA
        segments = []
        current_segment = []

        for token in tokens:
            if is_da_token(token):
                if current_segment:
                    segments.append(current_segment)
                current_segment = []
            else:
                current_segment.append(token)

        if current_segment:
            segments.append(current_segment)

        for seg in segments:
            if seg:
                segment_lengths.append(len(seg))
                prefixes = set(get_prefix(t) for t in seg if get_prefix(t))
                segment_prefix_diversity.append(len(prefixes))

    if segment_lengths:
        print(f"  Total segments: {len(segment_lengths)}")
        print(f"  Mean segment length: {np.mean(segment_lengths):.2f}")
        print(f"  Segment length distribution: min={min(segment_lengths)}, max={max(segment_lengths)}")
        print(f"  Mean prefix diversity per segment: {np.mean(segment_prefix_diversity):.2f}")

        # Distribution of segment lengths
        length_dist = Counter(segment_lengths)
        print(f"\n  Segment length counts:")
        for length in sorted(length_dist.keys())[:10]:
            print(f"    {length} tokens: {length_dist[length]}")

    return {
        'da_separates': da_separates_prefixes,
        'da_within': da_within_same_prefix,
        'mean_segment_length': np.mean(segment_lengths) if segment_lengths else 0,
    }


# =============================================================================
# TEST 4: DA TOKEN INVENTORY
# =============================================================================

def test_da_inventory(entries):
    """What specific DA tokens exist and how are they distributed?"""

    print("\n" + "=" * 70)
    print("TEST 4: DA TOKEN INVENTORY")
    print("=" * 70)

    da_tokens = Counter()
    da_by_section = defaultdict(Counter)
    da_by_position = {'first': Counter(), 'middle': Counter(), 'last': Counter()}

    for entry in entries:
        tokens = entry['tokens']
        section = entry['section']

        for i, token in enumerate(tokens):
            if is_da_token(token):
                token_lower = token.lower()
                da_tokens[token_lower] += 1
                da_by_section[section][token_lower] += 1

                if i == 0:
                    da_by_position['first'][token_lower] += 1
                elif i == len(tokens) - 1:
                    da_by_position['last'][token_lower] += 1
                else:
                    da_by_position['middle'][token_lower] += 1

    total_da = sum(da_tokens.values())

    print(f"\nDA token inventory ({len(da_tokens)} unique forms):")
    print(f"\nTop 20 DA tokens:")
    for token, count in da_tokens.most_common(20):
        pct = 100 * count / total_da
        print(f"  {token}: {count} ({pct:.1f}%)")

    # Concentration
    top1 = da_tokens.most_common(1)[0][1] if da_tokens else 0
    top3 = sum(c for _, c in da_tokens.most_common(3))
    print(f"\nConcentration:")
    print(f"  Top 1 token: {100*top1/total_da:.1f}% of all DA")
    print(f"  Top 3 tokens: {100*top3/total_da:.1f}% of all DA")

    # Position preference by token
    print(f"\nPosition preference for top DA tokens:")
    for token, count in da_tokens.most_common(5):
        first = da_by_position['first'].get(token, 0)
        middle = da_by_position['middle'].get(token, 0)
        last = da_by_position['last'].get(token, 0)
        print(f"  {token}: first={first}, middle={middle}, last={last}")

    # Section distribution
    print(f"\nDA by section:")
    for section in sorted(da_by_section.keys()):
        section_total = sum(da_by_section[section].values())
        top_token = da_by_section[section].most_common(1)[0] if da_by_section[section] else ('', 0)
        print(f"  {section}: {section_total} tokens, top='{top_token[0]}' ({top_token[1]})")

    return {
        'unique_da_tokens': len(da_tokens),
        'top_da_token': da_tokens.most_common(1)[0] if da_tokens else ('', 0),
        'concentration_top3': 100*top3/total_da if total_da > 0 else 0,
    }


# =============================================================================
# TEST 5: COMPARE DA TO OTHER MARKERS
# =============================================================================

def test_compare_markers(entries):
    """How does DA's positional behavior compare to other markers?"""

    print("\n" + "=" * 70)
    print("TEST 5: DA vs OTHER MARKERS (POSITION COMPARISON)")
    print("=" * 70)

    # Track relative positions for each marker
    marker_positions = {prefix: [] for prefix in MARKER_FAMILIES}
    marker_first_counts = Counter()
    marker_last_counts = Counter()
    marker_totals = Counter()

    for entry in entries:
        tokens = entry['tokens']
        if len(tokens) < 2:
            continue

        for i, token in enumerate(tokens):
            prefix = get_prefix(token)
            if prefix:
                rel_pos = i / (len(tokens) - 1) if len(tokens) > 1 else 0.5
                marker_positions[prefix].append(rel_pos)
                marker_totals[prefix] += 1

                if i == 0:
                    marker_first_counts[prefix] += 1
                elif i == len(tokens) - 1:
                    marker_last_counts[prefix] += 1

    print(f"\n{'Marker':<8} {'Count':<8} {'Mean Pos':<10} {'First %':<10} {'Last %':<10}")
    print("-" * 50)

    for prefix in sorted(MARKER_FAMILIES):
        if marker_totals[prefix] > 0:
            mean_pos = np.mean(marker_positions[prefix])
            first_pct = 100 * marker_first_counts[prefix] / marker_totals[prefix]
            last_pct = 100 * marker_last_counts[prefix] / marker_totals[prefix]
            print(f"{prefix:<8} {marker_totals[prefix]:<8} {mean_pos:<10.3f} {first_pct:<10.1f} {last_pct:<10.1f}")

    # Highlight DA specifically
    print(f"\nDA specifics:")
    da_mean = np.mean(marker_positions['da']) if marker_positions['da'] else 0
    other_means = [np.mean(marker_positions[p]) for p in MARKER_FAMILIES if p != 'da' and marker_positions[p]]
    avg_other = np.mean(other_means) if other_means else 0

    print(f"  DA mean position: {da_mean:.3f}")
    print(f"  Other markers avg: {avg_other:.3f}")
    print(f"  Difference: {da_mean - avg_other:.3f}")

    if da_mean < avg_other - 0.05:
        print("  -> DA appears EARLIER than other markers")
    elif da_mean > avg_other + 0.05:
        print("  -> DA appears LATER than other markers")
    else:
        print("  -> DA position similar to other markers")

    return marker_positions


# =============================================================================
# SYNTHESIS
# =============================================================================

def synthesize_findings(results):
    """Synthesize all findings about DA's role."""

    print("\n" + "=" * 70)
    print("SYNTHESIS: IS DA PUNCTUATION?")
    print("=" * 70)

    evidence_for = []
    evidence_against = []

    # Position analysis
    if results['position']['mean_relative'] < 0.45:
        evidence_for.append(f"DA appears earlier than expected (mean={results['position']['mean_relative']:.3f})")
    elif results['position']['mean_relative'] > 0.55:
        evidence_for.append(f"DA appears later than expected (mean={results['position']['mean_relative']:.3f})")

    if results['position']['position_chi2_p'] < 0.001:
        evidence_for.append("DA position is NOT uniformly distributed")

    # Structural role
    if results['structure']['da_separates'] > results['structure']['da_within']:
        ratio = results['structure']['da_separates'] / results['structure']['da_within'] if results['structure']['da_within'] > 0 else float('inf')
        evidence_for.append(f"DA more often SEPARATES prefix runs ({ratio:.1f}x)")
    else:
        evidence_against.append("DA appears within same-prefix runs, not just between them")

    # Inventory concentration
    if results['inventory']['concentration_top3'] > 70:
        evidence_for.append(f"DA is highly concentrated (top 3 = {results['inventory']['concentration_top3']:.0f}%)")

    print("\nEvidence FOR punctuation role:")
    for e in evidence_for:
        print(f"  + {e}")

    print("\nEvidence AGAINST punctuation role:")
    for e in evidence_against:
        print(f"  - {e}")

    if not evidence_against:
        print("  (none)")

    # Verdict
    print("\n" + "-" * 70)
    if len(evidence_for) >= 3 and len(evidence_against) <= 1:
        print("VERDICT: STRONG evidence that DA functions as structural punctuation")
    elif len(evidence_for) >= 2:
        print("VERDICT: MODERATE evidence for punctuation role")
    else:
        print("VERDICT: INCONCLUSIVE - DA may be a regular classifier")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("Loading Currier A entries...")
    entries = load_currier_a_entries()
    print(f"Loaded {len(entries)} entries")

    results = {}
    results['position'] = test_position_histogram(entries)
    results['adjacency'] = test_adjacency_patterns(entries)
    results['structure'] = test_structural_role(entries)
    results['inventory'] = test_da_inventory(entries)
    results['comparison'] = test_compare_markers(entries)

    synthesize_findings(results)
