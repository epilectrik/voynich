"""
Currier A Payload Analysis

Question: What do the markers actually classify?
- What patterns exist in the payloads?
- Are there repetition patterns (counting/tally marks)?
- What distinguishes one marker class from another?
"""

from collections import defaultdict, Counter
from pathlib import Path
import json

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


def classify_by_marker(lines):
    """Classify lines by their marker prefix."""
    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    classified = {m: [] for m in marker_prefixes}
    classified['NONE'] = []

    for line_id, info in lines.items():
        tokens = info['tokens']

        # Find which marker(s) present
        markers_found = set()
        for token in tokens:
            if len(token) >= 2:
                prefix = token[:2]
                if prefix in marker_prefixes:
                    markers_found.add(prefix)

        if len(markers_found) == 1:
            marker = list(markers_found)[0]
            classified[marker].append({
                'line_id': line_id,
                'tokens': tokens,
                'section': info['section'],
                'folio': info['folio']
            })
        elif len(markers_found) == 0:
            classified['NONE'].append({
                'line_id': line_id,
                'tokens': tokens,
                'section': info['section'],
                'folio': info['folio']
            })

    return classified


def analyze_repetition_patterns(classified):
    """Analyze repetition patterns within entries."""
    print("\n" + "=" * 70)
    print("REPETITION PATTERN ANALYSIS")
    print("=" * 70)

    for marker, entries in classified.items():
        if not entries or marker == 'NONE':
            continue

        # Count consecutive repetitions
        repeat_counts = Counter()
        token_repeats = Counter()

        for entry in entries:
            tokens = entry['tokens']
            i = 0
            while i < len(tokens):
                # Count consecutive occurrences of same token
                count = 1
                while i + count < len(tokens) and tokens[i + count] == tokens[i]:
                    count += 1

                if count > 1:
                    repeat_counts[count] += 1
                    token_repeats[tokens[i]] += count

                i += count

        if repeat_counts:
            print(f"\n{marker}: Repetition patterns")
            print(f"  Consecutive runs: {dict(repeat_counts.most_common(10))}")
            print(f"  Most repeated tokens: {token_repeats.most_common(5)}")


def analyze_entry_structure(classified):
    """Analyze the structure of entries for each marker."""
    print("\n" + "=" * 70)
    print("ENTRY STRUCTURE ANALYSIS")
    print("=" * 70)

    for marker, entries in classified.items():
        if not entries:
            continue

        # Analyze entry lengths
        lengths = [len(e['tokens']) for e in entries]

        # Analyze token position patterns
        first_tokens = Counter()
        last_tokens = Counter()
        all_tokens = Counter()

        for entry in entries:
            tokens = entry['tokens']
            if tokens:
                first_tokens[tokens[0]] += 1
                last_tokens[tokens[-1]] += 1
                for t in tokens:
                    all_tokens[t] += 1

        print(f"\n{marker}: {len(entries)} entries")
        print(f"  Length: min={min(lengths)}, max={max(lengths)}, avg={sum(lengths)/len(lengths):.1f}")
        print(f"  First tokens: {first_tokens.most_common(5)}")
        print(f"  Last tokens: {last_tokens.most_common(5)}")
        print(f"  Most common overall: {all_tokens.most_common(5)}")


def analyze_payload_vocabulary(classified):
    """Analyze what vocabulary appears in each marker class (excluding the marker itself)."""
    print("\n" + "=" * 70)
    print("PAYLOAD VOCABULARY ANALYSIS (excluding markers)")
    print("=" * 70)

    marker_prefixes = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

    for marker, entries in classified.items():
        if not entries or marker == 'NONE':
            continue

        # Get payload tokens (tokens that don't start with a marker prefix)
        payload_tokens = Counter()

        for entry in entries:
            for token in entry['tokens']:
                # Is this a marker token or a payload token?
                is_marker = False
                if len(token) >= 2:
                    prefix = token[:2]
                    if prefix in marker_prefixes:
                        is_marker = True

                if not is_marker:
                    payload_tokens[token] += 1

        if payload_tokens:
            print(f"\n{marker}: Payload vocabulary")
            print(f"  Unique payload types: {len(payload_tokens)}")
            print(f"  Most common payloads: {payload_tokens.most_common(10)}")


def find_daiin_patterns(classified):
    """Special analysis of 'daiin' which appears heavily in Currier A."""
    print("\n" + "=" * 70)
    print("'DAIIN' PATTERN ANALYSIS")
    print("=" * 70)

    for marker, entries in classified.items():
        if not entries:
            continue

        # Count daiin occurrences and runs
        daiin_entries = 0
        daiin_runs = Counter()  # length of consecutive daiin runs

        for entry in entries:
            tokens = entry['tokens']
            has_daiin = False

            i = 0
            while i < len(tokens):
                if tokens[i] == 'daiin':
                    has_daiin = True
                    # Count run length
                    run_len = 1
                    while i + run_len < len(tokens) and tokens[i + run_len] == 'daiin':
                        run_len += 1
                    daiin_runs[run_len] += 1
                    i += run_len
                else:
                    i += 1

            if has_daiin:
                daiin_entries += 1

        if daiin_entries > 0:
            print(f"\n{marker}: {daiin_entries}/{len(entries)} entries have 'daiin' ({100*daiin_entries/len(entries):.1f}%)")
            print(f"  Run lengths: {dict(daiin_runs.most_common(10))}")


def show_example_entries(classified, n=5):
    """Show example entries for each marker class."""
    print("\n" + "=" * 70)
    print("EXAMPLE ENTRIES")
    print("=" * 70)

    for marker, entries in classified.items():
        if not entries or marker == 'NONE':
            continue

        print(f"\n{marker}: (showing {min(n, len(entries))} examples)")
        for entry in entries[:n]:
            tokens = ' '.join(entry['tokens'])
            print(f"  [{entry['folio']}] {tokens}")


def look_for_counting_patterns(classified):
    """Look for patterns that might indicate counting/tally behavior."""
    print("\n" + "=" * 70)
    print("COUNTING/TALLY PATTERN ANALYSIS")
    print("=" * 70)

    for marker, entries in classified.items():
        if not entries or marker == 'NONE':
            continue

        # Look for entries with many repeated tokens
        high_repeat_entries = []

        for entry in entries:
            tokens = entry['tokens']
            if len(tokens) >= 3:
                # Count unique vs total
                unique = len(set(tokens))
                total = len(tokens)
                repeat_ratio = 1 - (unique / total)

                if repeat_ratio > 0.5 and total >= 4:  # >50% repetition, at least 4 tokens
                    high_repeat_entries.append({
                        'line_id': entry['line_id'],
                        'tokens': tokens,
                        'repeat_ratio': repeat_ratio
                    })

        if high_repeat_entries:
            print(f"\n{marker}: {len(high_repeat_entries)} high-repetition entries (>50% repeated)")
            high_repeat_entries.sort(key=lambda x: -x['repeat_ratio'])
            for entry in high_repeat_entries[:5]:
                print(f"  {entry['repeat_ratio']:.1%}: {' '.join(entry['tokens'])}")


def main():
    print("=" * 70)
    print("CURRIER A PAYLOAD ANALYSIS")
    print("=" * 70)
    print("\nQuestion: What do the markers actually classify?")

    lines = load_currier_a_lines()
    print(f"\nLoaded {len(lines)} Currier A lines")

    classified = classify_by_marker(lines)

    # Summary
    print("\nClassification summary:")
    for marker, entries in classified.items():
        print(f"  {marker}: {len(entries)} entries")

    # Run analyses
    analyze_entry_structure(classified)
    analyze_payload_vocabulary(classified)
    find_daiin_patterns(classified)
    analyze_repetition_patterns(classified)
    look_for_counting_patterns(classified)
    show_example_entries(classified, n=8)

    return classified


if __name__ == '__main__':
    main()
