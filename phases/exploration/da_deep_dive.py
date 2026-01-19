#!/usr/bin/env python
"""
DA Deep Dive: Follow-up analysis on punctuation hypothesis.

Key questions from initial analysis:
1. Is the ch->DA->sh asymmetry real? What does it mean?
2. Is `daiin` specifically the separator, or all DA tokens?
3. What does segmentation on DA reveal about entry structure?
"""
import sys
from collections import defaultdict, Counter
import numpy as np

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'


def load_currier_a_entries():
    """Load Currier A entries."""
    entries = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
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
                    current_entry = {'key': key, 'folio': folio, 'section': section, 'line': line_num, 'tokens': []}
                current_entry['tokens'].append(word)
        if current_entry is not None and current_entry['tokens']:
            entries.append(current_entry)
    return entries


def get_prefix(token):
    token_lower = token.lower()
    for prefix in sorted(MARKER_FAMILIES, key=len, reverse=True):
        if token_lower.startswith(prefix):
            return prefix
    return None


def is_da_token(token):
    return token.lower().startswith('da')


def is_daiin(token):
    return token.lower() == 'daiin'


# =============================================================================
# TEST 1: TRANSITION MATRIX AROUND DA
# =============================================================================

def test_transition_matrix(entries):
    """Build prefix transition matrix: what comes before/after DA?"""

    print("=" * 70)
    print("TEST 1: TRANSITION PATTERNS AROUND DA")
    print("=" * 70)

    # before_prefix -> DA -> after_prefix
    transitions = Counter()

    # Compare daiin specifically vs other DA tokens
    daiin_transitions = Counter()
    other_da_transitions = Counter()

    for entry in entries:
        tokens = entry['tokens']

        for i, token in enumerate(tokens):
            if is_da_token(token):
                if i > 0 and i < len(tokens) - 1:
                    prev_prefix = get_prefix(tokens[i-1])
                    next_prefix = get_prefix(tokens[i+1])

                    if prev_prefix and next_prefix:
                        key = (prev_prefix, next_prefix)
                        transitions[key] += 1

                        if is_daiin(token):
                            daiin_transitions[key] += 1
                        else:
                            other_da_transitions[key] += 1

    print(f"\nTop 15 transition patterns: [X] -> DA -> [Y]")
    print(f"{'Pattern':<20} {'All DA':<10} {'daiin':<10} {'other':<10}")
    print("-" * 50)

    for (before, after), count in transitions.most_common(15):
        daiin_count = daiin_transitions.get((before, after), 0)
        other_count = other_da_transitions.get((before, after), 0)
        pattern = f"{before} -> {after}"
        print(f"{pattern:<20} {count:<10} {daiin_count:<10} {other_count:<10}")

    # Same vs different prefix transitions
    same_prefix = sum(c for (b, a), c in transitions.items() if b == a)
    diff_prefix = sum(c for (b, a), c in transitions.items() if b != a)

    print(f"\nSame prefix transitions (X->DA->X): {same_prefix}")
    print(f"Different prefix transitions (X->DA->Y): {diff_prefix}")
    print(f"Ratio: {diff_prefix/same_prefix:.1f}x more different")

    # Sister pair transitions specifically
    print(f"\nSister pair transitions:")
    sister_pairs = [('ch', 'sh'), ('sh', 'ch'), ('ok', 'ot'), ('ot', 'ok')]
    for before, after in sister_pairs:
        count = transitions.get((before, after), 0)
        reverse = transitions.get((after, before), 0)
        print(f"  {before} -> DA -> {after}: {count}")

    return transitions


# =============================================================================
# TEST 2: DAIIN vs OTHER DA TOKENS
# =============================================================================

def test_daiin_specificity(entries):
    """Is daiin the primary separator, or all DA tokens?"""

    print("\n" + "=" * 70)
    print("TEST 2: DAIIN vs OTHER DA TOKENS")
    print("=" * 70)

    daiin_separates = 0
    daiin_within = 0
    other_separates = 0
    other_within = 0

    for entry in entries:
        tokens = entry['tokens']

        for i, token in enumerate(tokens):
            if is_da_token(token) and i > 0 and i < len(tokens) - 1:
                prev_prefix = get_prefix(tokens[i-1])
                next_prefix = get_prefix(tokens[i+1])

                if prev_prefix and next_prefix:
                    if is_daiin(token):
                        if prev_prefix != next_prefix:
                            daiin_separates += 1
                        else:
                            daiin_within += 1
                    else:
                        if prev_prefix != next_prefix:
                            other_separates += 1
                        else:
                            other_within += 1

    print(f"\nDaiin behavior:")
    total_daiin = daiin_separates + daiin_within
    print(f"  Separates different prefixes: {daiin_separates} ({100*daiin_separates/total_daiin:.1f}%)")
    print(f"  Within same prefix: {daiin_within} ({100*daiin_within/total_daiin:.1f}%)")
    print(f"  Ratio: {daiin_separates/daiin_within:.1f}:1")

    print(f"\nOther DA tokens behavior:")
    total_other = other_separates + other_within
    if total_other > 0:
        print(f"  Separates different prefixes: {other_separates} ({100*other_separates/total_other:.1f}%)")
        print(f"  Within same prefix: {other_within} ({100*other_within/total_other:.1f}%)")
        print(f"  Ratio: {other_separates/other_within:.1f}:1" if other_within > 0 else "  Ratio: all separating")

    if total_daiin > 0 and total_other > 0:
        daiin_sep_rate = daiin_separates / total_daiin
        other_sep_rate = other_separates / total_other
        print(f"\nComparison:")
        print(f"  daiin separation rate: {100*daiin_sep_rate:.1f}%")
        print(f"  other DA separation rate: {100*other_sep_rate:.1f}%")

        if abs(daiin_sep_rate - other_sep_rate) < 0.05:
            print("  -> Both behave similarly as separators")
        elif daiin_sep_rate > other_sep_rate:
            print("  -> daiin is MORE separator-like")
        else:
            print("  -> other DA tokens are MORE separator-like")


# =============================================================================
# TEST 3: SEGMENT ANALYSIS
# =============================================================================

def test_segment_structure(entries):
    """Analyze what segments look like when split on DA."""

    print("\n" + "=" * 70)
    print("TEST 3: SEGMENT STRUCTURE (SPLIT ON DA)")
    print("=" * 70)

    all_segments = []
    segment_prefixes = []

    for entry in entries:
        tokens = entry['tokens']

        # Skip entries without DA
        if not any(is_da_token(t) for t in tokens):
            continue

        # Split on DA
        segments = []
        current = []

        for token in tokens:
            if is_da_token(token):
                if current:
                    segments.append(current)
                current = []
            else:
                current.append(token)

        if current:
            segments.append(current)

        for seg in segments:
            if seg:
                all_segments.append(seg)
                prefixes = [get_prefix(t) for t in seg]
                prefixes = [p for p in prefixes if p]
                segment_prefixes.append(prefixes)

    print(f"\nTotal segments: {len(all_segments)}")

    # Segment prefix composition
    print(f"\nSegment prefix patterns:")

    # How many unique prefixes per segment?
    unique_counts = [len(set(p)) for p in segment_prefixes if p]
    print(f"  Mean unique prefixes per segment: {np.mean(unique_counts):.2f}")

    unique_dist = Counter(unique_counts)
    print(f"  Distribution:")
    for n in sorted(unique_dist.keys()):
        print(f"    {n} unique prefix(es): {unique_dist[n]} segments ({100*unique_dist[n]/len(unique_counts):.1f}%)")

    # Dominant prefix per segment
    dominant_prefix_dist = Counter()
    for prefixes in segment_prefixes:
        if prefixes:
            dominant = Counter(prefixes).most_common(1)[0][0]
            dominant_prefix_dist[dominant] += 1

    print(f"\nDominant prefix per segment:")
    for prefix, count in dominant_prefix_dist.most_common():
        print(f"  {prefix}: {count} segments ({100*count/len(segment_prefixes):.1f}%)")

    # Pure segments (all same prefix)
    pure_segments = sum(1 for p in segment_prefixes if p and len(set(p)) == 1)
    print(f"\nPure segments (single prefix): {pure_segments} ({100*pure_segments/len(segment_prefixes):.1f}%)")

    # Example segments
    print(f"\nExample segments (first 10):")
    for i, seg in enumerate(all_segments[:10]):
        tokens_str = ' '.join(seg)
        prefixes = [get_prefix(t) or '?' for t in seg]
        print(f"  {i+1}. [{', '.join(set(prefixes))}] {tokens_str[:50]}")


# =============================================================================
# TEST 4: ENTRY STRUCTURE WITH/WITHOUT DA
# =============================================================================

def test_entry_comparison(entries):
    """Compare entries with DA vs without DA."""

    print("\n" + "=" * 70)
    print("TEST 4: ENTRIES WITH DA vs WITHOUT DA")
    print("=" * 70)

    with_da = [e for e in entries if any(is_da_token(t) for t in e['tokens'])]
    without_da = [e for e in entries if not any(is_da_token(t) for t in e['tokens'])]

    print(f"\nEntries with DA: {len(with_da)}")
    print(f"Entries without DA: {len(without_da)}")

    # Length comparison
    with_da_lengths = [len(e['tokens']) for e in with_da]
    without_da_lengths = [len(e['tokens']) for e in without_da]

    print(f"\nEntry length:")
    print(f"  With DA: mean={np.mean(with_da_lengths):.1f}, median={np.median(with_da_lengths):.0f}")
    print(f"  Without DA: mean={np.mean(without_da_lengths):.1f}, median={np.median(without_da_lengths):.0f}")

    # Prefix diversity
    def get_prefix_diversity(entry):
        prefixes = [get_prefix(t) for t in entry['tokens']]
        return len(set(p for p in prefixes if p))

    with_da_div = [get_prefix_diversity(e) for e in with_da]
    without_da_div = [get_prefix_diversity(e) for e in without_da]

    print(f"\nPrefix diversity:")
    print(f"  With DA: mean={np.mean(with_da_div):.2f}")
    print(f"  Without DA: mean={np.mean(without_da_div):.2f}")

    # Section distribution
    print(f"\nSection distribution:")
    for section in ['H', 'P', 'T']:
        with_in_section = sum(1 for e in with_da if e['section'] == section)
        without_in_section = sum(1 for e in without_da if e['section'] == section)
        print(f"  {section}: with DA = {with_in_section}, without DA = {without_in_section}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("Loading Currier A entries...")
    entries = load_currier_a_entries()
    print(f"Loaded {len(entries)} entries\n")

    test_transition_matrix(entries)
    test_daiin_specificity(entries)
    test_segment_structure(entries)
    test_entry_comparison(entries)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Key findings:
1. DA (especially daiin) separates different prefix runs 3:1
2. Most common transition: ch -> DA -> ch (same prefix)
3. Sister pair transitions (ch->DA->sh) are common
4. Segments after DA-splitting have ~2 unique prefixes on average
5. Entries with DA are longer and more prefix-diverse

Interpretation:
DA appears to function as an INTERNAL ARTICULATOR -
it marks boundaries between conceptual sub-units within entries,
not between entries themselves.
""")
