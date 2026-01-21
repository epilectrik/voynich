#!/usr/bin/env python3
"""Check for adjacent RI tokens in A records."""

import json
from collections import defaultdict

with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
    tokens = json.load(f)

# Group by line
lines = defaultdict(list)
for t in tokens:
    line_key = f"{t['folio']}.{t['line']}"
    lines[line_key].append(t)

# Find adjacent RI pairs
adjacent_ri_pairs = []

for line_key, line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        if (line_tokens[i]['middle_class'] == 'exclusive' and
            line_tokens[i+1]['middle_class'] == 'exclusive'):
            adjacent_ri_pairs.append({
                'line': line_key,
                'pos': i,
                'token1': line_tokens[i]['token'],
                'middle1': line_tokens[i]['middle'],
                'token2': line_tokens[i+1]['token'],
                'middle2': line_tokens[i+1]['middle'],
                'context': [t['token'] for t in line_tokens]
            })

print(f"Adjacent RI-RI pairs found: {len(adjacent_ri_pairs)}")
print()

if adjacent_ri_pairs:
    for pair in adjacent_ri_pairs:
        print(f"Line {pair['line']}, position {pair['pos']}:")
        print(f"  {pair['token1']} ({pair['middle1']}) + {pair['token2']} ({pair['middle2']})")
        # Show context with markers
        context = pair['context']
        pos = pair['pos']
        marked = []
        for i, tok in enumerate(context):
            if i == pos or i == pos + 1:
                marked.append(f"[{tok}]")
            else:
                marked.append(tok)
        print(f"  Context: {' '.join(marked)}")
        print()
else:
    print("No adjacent RI-RI pairs found.")

# Also check: how many lines have 2+ RI tokens?
lines_with_multiple_ri = []
for line_key, line_tokens in lines.items():
    ri_positions = [i for i, t in enumerate(line_tokens) if t['middle_class'] == 'exclusive']
    if len(ri_positions) >= 2:
        lines_with_multiple_ri.append({
            'line': line_key,
            'ri_count': len(ri_positions),
            'ri_positions': ri_positions,
            'line_length': len(line_tokens),
            'tokens': [t['token'] for t in line_tokens],
            'ri_tokens': [line_tokens[i]['token'] for i in ri_positions]
        })

print("=" * 60)
print(f"Lines with 2+ RI tokens: {len(lines_with_multiple_ri)}")
print()

if lines_with_multiple_ri:
    print("Examples:")
    for line in lines_with_multiple_ri[:10]:
        gaps = [line['ri_positions'][i+1] - line['ri_positions'][i]
                for i in range(len(line['ri_positions'])-1)]
        print(f"  {line['line']}: {line['ri_count']} RI at positions {line['ri_positions']} (gaps: {gaps})")
        print(f"    RI tokens: {line['ri_tokens']}")
        print()
