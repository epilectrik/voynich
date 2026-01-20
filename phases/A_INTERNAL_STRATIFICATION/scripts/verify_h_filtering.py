#!/usr/bin/env python3
"""
Verify H-only filtering is correctly applied.

The expert flagged that C250 invalidation noted "0% block repetition" with H-only data,
but we found 16% multi-token entries. Need to verify our filtering.
"""

import csv
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

print("=" * 70)
print("H-ONLY FILTERING VERIFICATION")
print("=" * 70)

# Load raw data and check transcriber distribution
print("\n1. Checking transcriber distribution in raw data...")

transcriber_counts = Counter()
total_rows = 0

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        total_rows += 1
        transcriber = row.get('transcriber', 'UNKNOWN')
        transcriber_counts[transcriber] += 1

print(f"\n   Total rows: {total_rows:,}")
print(f"\n   Transcriber distribution:")
for t, count in transcriber_counts.most_common():
    print(f"     {t}: {count:,} ({100*count/total_rows:.1f}%)")

# Now check what we get with H-only filtering for Currier A
print("\n2. Checking Currier A with H-only filter...")

h_only_a_tokens = []
h_only_a_lines = defaultdict(list)

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        # H-only filter
        if row.get('transcriber') != 'H':
            continue

        # Currier A only
        if row.get('language') != 'A':
            continue

        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        folio = row.get('folio', '')
        line_num = row.get('line_number', '')

        h_only_a_tokens.append({
            'word': word,
            'folio': folio,
            'line': line_num
        })

        h_only_a_lines[(folio, line_num)].append(word)

print(f"\n   H-only Currier A tokens: {len(h_only_a_tokens):,}")
print(f"   H-only Currier A lines: {len(h_only_a_lines):,}")

# Check line token counts
line_sizes = Counter(len(tokens) for tokens in h_only_a_lines.values())
print(f"\n   Line token counts (H-only Currier A):")
for size, count in sorted(line_sizes.items())[:15]:
    print(f"     {size} tokens: {count} lines ({100*count/len(h_only_a_lines):.1f}%)")

multi_token_lines = sum(1 for tokens in h_only_a_lines.values() if len(tokens) >= 2)
print(f"\n   Multi-token lines: {multi_token_lines} ({100*multi_token_lines/len(h_only_a_lines):.1f}%)")

# Check if multi-token lines are same-token repetitions
print("\n3. Checking if multi-token lines are same-token repetitions...")

same_token_count = 0
diff_token_count = 0
diff_token_examples = []

for (folio, line), tokens in h_only_a_lines.items():
    if len(tokens) >= 2:
        unique_tokens = set(tokens)
        if len(unique_tokens) == 1:
            same_token_count += 1
        else:
            diff_token_count += 1
            if len(diff_token_examples) < 10:
                diff_token_examples.append((folio, line, tokens))

print(f"\n   Same token repeated: {same_token_count} ({100*same_token_count/multi_token_lines:.1f}%)")
print(f"   Different tokens: {diff_token_count} ({100*diff_token_count/multi_token_lines:.1f}%)")

if diff_token_examples:
    print(f"\n   Examples of lines with different tokens:")
    for folio, line, tokens in diff_token_examples:
        print(f"     {folio} L{line}: {tokens}")

# Compare with what our prep script produced
print("\n4. Comparing with prep script output...")

import json
RESULTS_DIR = Path(__file__).parent.parent / 'results'

with open(RESULTS_DIR / 'entry_data.json') as f:
    prep_entries = json.load(f)

print(f"\n   Prep script entries: {len(prep_entries)}")
print(f"   Direct H-only lines: {len(h_only_a_lines)}")

# Check multi-token counts
prep_multi = sum(1 for e in prep_entries if e['n_tokens'] >= 2)
print(f"\n   Prep script multi-token: {prep_multi}")
print(f"   Direct count multi-token: {multi_token_lines}")

# Discrepancy analysis
if len(prep_entries) != len(h_only_a_lines):
    print(f"\n   DISCREPANCY: Entry counts differ!")
    print(f"   Difference: {abs(len(prep_entries) - len(h_only_a_lines))}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
