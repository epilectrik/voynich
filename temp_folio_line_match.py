#!/usr/bin/env python3
"""Find Voynich folios with line counts matching Brunschwig entry structure."""
import csv
from collections import defaultdict

# Count lines per B folio
folio_lines = defaultdict(set)
folio_tokens = defaultdict(int)

with open('data/transcriptions/interlinear_full_words.txt', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row['language'] == 'B':
            folio = row['folio']
            folio_lines[folio].add(row['line_number'])
            folio_tokens[folio] += 1

# Find folios with 10-20 lines (matching Brunschwig 10-26 uses)
print("Voynich folios with 10-20 lines (Brunschwig entry range):")
print("-" * 60)
matching = []
for folio in sorted(folio_lines.keys()):
    n_lines = len(folio_lines[folio])
    n_tokens = folio_tokens[folio]
    if 10 <= n_lines <= 20:
        tokens_per_line = n_tokens / n_lines
        matching.append((folio, n_lines, n_tokens, tokens_per_line))
        print(f"  {folio}: {n_lines} lines, {n_tokens} tokens ({tokens_per_line:.1f} tokens/line)")

print(f"\nTotal matching folios: {len(matching)}")
print(f"\nBrunschwig comparison:")
print(f"  Brunschwig: 16 uses (A-P), ~25 words per use")
print(f"  Voynich match: {len(matching)} folios with 10-20 lines, ~30 tokens/line")
