#!/usr/bin/env python3
"""Analyze RI token positions within lines - corrected version."""

import json
from collections import defaultdict, Counter

with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
    tokens = json.load(f)

# Group by line
lines = defaultdict(list)
for t in tokens:
    line_key = f"{t['folio']}.{t['line']}"
    lines[line_key].append(t)

print("=" * 70)
print("RI POSITION ANALYSIS (Corrected)")
print("=" * 70)
print()

# 1. Absolute position of RI tokens
print("1. ABSOLUTE POSITION OF RI TOKENS")
print("-" * 40)

ri_positions = []
for line_key, line_tokens in lines.items():
    for i, t in enumerate(line_tokens):
        if t['middle_class'] == 'exclusive':
            ri_positions.append(i)

pos_dist = Counter(ri_positions)
print("Position distribution (0 = first token):")
for pos in sorted(pos_dist.keys())[:15]:
    count = pos_dist[pos]
    pct = 100 * count / len(ri_positions)
    bar = '#' * int(pct)
    print(f"  Position {pos:2d}: {count:3d} ({pct:5.1f}%) {bar}")

print()
print(f"Total RI tokens: {len(ri_positions)}")
print(f"Mean position: {sum(ri_positions)/len(ri_positions):.2f}")
print()

# 2. Normalized position (0.0 = start, 1.0 = end)
print("2. NORMALIZED POSITION (0=start, 1=end)")
print("-" * 40)

norm_positions = []
for line_key, line_tokens in lines.items():
    line_len = len(line_tokens)
    if line_len < 2:
        continue
    for i, t in enumerate(line_tokens):
        if t['middle_class'] == 'exclusive':
            norm_pos = i / (line_len - 1)  # 0 to 1
            norm_positions.append(norm_pos)

# Bin into deciles
bins = {f"{i*10}-{(i+1)*10}%": 0 for i in range(10)}
for np in norm_positions:
    bin_idx = min(int(np * 10), 9)
    bin_name = f"{bin_idx*10}-{(bin_idx+1)*10}%"
    bins[bin_name] += 1

print("Normalized position distribution:")
for bin_name, count in bins.items():
    pct = 100 * count / len(norm_positions)
    bar = '#' * int(pct / 2)
    print(f"  {bin_name}: {count:3d} ({pct:5.1f}%) {bar}")

print()
mean_norm = sum(norm_positions) / len(norm_positions)
print(f"Mean normalized position: {mean_norm:.3f}")
print(f"(0.5 = perfectly uniform, <0.5 = front-biased, >0.5 = end-biased)")
print()

# 3. First vs Last token analysis
print("3. FIRST/LAST TOKEN ANALYSIS")
print("-" * 40)

ri_first = 0
ri_last = 0
ri_middle = 0
total_ri_in_multitoken = 0

for line_key, line_tokens in lines.items():
    if len(line_tokens) < 2:
        continue
    for i, t in enumerate(line_tokens):
        if t['middle_class'] == 'exclusive':
            total_ri_in_multitoken += 1
            if i == 0:
                ri_first += 1
            elif i == len(line_tokens) - 1:
                ri_last += 1
            else:
                ri_middle += 1

print(f"RI as FIRST token: {ri_first} ({100*ri_first/total_ri_in_multitoken:.1f}%)")
print(f"RI as LAST token:  {ri_last} ({100*ri_last/total_ri_in_multitoken:.1f}%)")
print(f"RI in MIDDLE:      {ri_middle} ({100*ri_middle/total_ri_in_multitoken:.1f}%)")
print()

# Expected if uniform
n_lines_with_ri = sum(1 for lk, lt in lines.items()
                      if len(lt) >= 2 and any(t['middle_class'] == 'exclusive' for t in lt))
avg_line_len = sum(len(lt) for lk, lt in lines.items() if len(lt) >= 2) / sum(1 for lt in lines.values() if len(lt) >= 2)
expected_first_pct = 1 / avg_line_len * 100
print(f"Expected if uniform (avg line {avg_line_len:.1f} tokens): ~{expected_first_pct:.1f}% first, ~{expected_first_pct:.1f}% last")
print()

# 4. Position of multi-RI and high-RI lines within folios
print("4. MULTI-RI / HIGH-RI LINES: POSITION WITHIN FOLIO")
print("-" * 40)

# Get all lines per folio with their line numbers
folio_lines = defaultdict(list)
for line_key in lines.keys():
    folio, line_num = line_key.rsplit('.', 1)
    folio_lines[folio].append(int(line_num) if line_num.isdigit() else 0)

# For multi-RI lines, where are they in the folio?
multi_ri_line_positions = []
for line_key, line_tokens in lines.items():
    ri_count = sum(1 for t in line_tokens if t['middle_class'] == 'exclusive')
    if ri_count >= 2:
        folio, line_num = line_key.rsplit('.', 1)
        line_num = int(line_num) if line_num.isdigit() else 0
        all_lines = sorted(folio_lines[folio])
        if len(all_lines) > 1:
            norm_line_pos = all_lines.index(line_num) / (len(all_lines) - 1)
        else:
            norm_line_pos = 0.5
        multi_ri_line_positions.append({
            'line_key': line_key,
            'line_num': line_num,
            'folio': folio,
            'norm_pos': norm_line_pos,
            'ri_count': ri_count,
            'is_first': line_num == min(all_lines),
            'is_last': line_num == max(all_lines)
        })

print(f"Multi-RI lines analyzed: {len(multi_ri_line_positions)}")

first_line = sum(1 for m in multi_ri_line_positions if m['is_first'])
last_line = sum(1 for m in multi_ri_line_positions if m['is_last'])
print(f"  On FIRST line of folio: {first_line} ({100*first_line/len(multi_ri_line_positions):.1f}%)")
print(f"  On LAST line of folio:  {last_line} ({100*last_line/len(multi_ri_line_positions):.1f}%)")

mean_folio_pos = sum(m['norm_pos'] for m in multi_ri_line_positions) / len(multi_ri_line_positions)
print(f"  Mean normalized folio position: {mean_folio_pos:.3f}")
print()

# 5. Lines that START with RI
print("5. LINES THAT START WITH RI TOKEN")
print("-" * 40)

lines_starting_ri = []
for line_key, line_tokens in lines.items():
    if len(line_tokens) > 0 and line_tokens[0]['middle_class'] == 'exclusive':
        ri_count = sum(1 for t in line_tokens if t['middle_class'] == 'exclusive')
        lines_starting_ri.append({
            'line_key': line_key,
            'first_token': line_tokens[0]['token'],
            'first_middle': line_tokens[0]['middle'],
            'line_length': len(line_tokens),
            'ri_count': ri_count,
            'all_tokens': [t['token'] for t in line_tokens]
        })

print(f"Lines starting with RI: {len(lines_starting_ri)} ({100*len(lines_starting_ri)/len(lines):.1f}% of all lines)")
print()

# What MIDDLEs start lines?
starting_middles = Counter(l['first_middle'] for l in lines_starting_ri)
print("MIDDLEs that START lines (top 10):")
for middle, count in starting_middles.most_common(10):
    print(f"  {middle}: {count}")
print()

# Show examples
print("Examples of RI-starting lines:")
for l in lines_starting_ri[:10]:
    print(f"  {l['line_key']}: [{l['first_token']}] {' '.join(l['all_tokens'][1:])}")
print()

# 6. Lines that END with RI
print("6. LINES THAT END WITH RI TOKEN")
print("-" * 40)

lines_ending_ri = []
for line_key, line_tokens in lines.items():
    if len(line_tokens) > 0 and line_tokens[-1]['middle_class'] == 'exclusive':
        ri_count = sum(1 for t in line_tokens if t['middle_class'] == 'exclusive')
        lines_ending_ri.append({
            'line_key': line_key,
            'last_token': line_tokens[-1]['token'],
            'last_middle': line_tokens[-1]['middle'],
            'line_length': len(line_tokens),
            'ri_count': ri_count,
            'all_tokens': [t['token'] for t in line_tokens]
        })

print(f"Lines ending with RI: {len(lines_ending_ri)} ({100*len(lines_ending_ri)/len(lines):.1f}% of all lines)")
print()

ending_middles = Counter(l['last_middle'] for l in lines_ending_ri)
print("MIDDLEs that END lines (top 10):")
for middle, count in ending_middles.most_common(10):
    print(f"  {middle}: {count}")
print()

print("Examples of RI-ending lines:")
for l in lines_ending_ri[:10]:
    print(f"  {l['line_key']}: {' '.join(l['all_tokens'][:-1])} [{l['last_token']}]")
