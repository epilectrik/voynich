#!/usr/bin/env python3
"""
Test 8: P-text Paragraph Structure

Question: How is P-text organized on its folios?
- Does it form multi-line paragraphs like Currier A?
- Or isolated labels/annotations like AZC diagram text?

Key indicators:
- Lines per "paragraph" (consecutive P-placement lines)
- Line continuity (do lines connect or are they isolated?)
- Position on folio (concentrated or scattered?)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict
import numpy as np

# Load transcript
filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

# Collect P-text by folio and line
ptext_by_folio_line = defaultdict(lambda: defaultdict(list))
azc_by_folio_line = defaultdict(lambda: defaultdict(list))

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            if currier != 'NA':
                continue

            folio = parts[2].strip('"').strip()
            line_num = parts[3].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if placement == 'P' or placement.startswith('P'):
                ptext_by_folio_line[folio][line_num].append(token)
            else:
                azc_by_folio_line[folio][line_num].append(token)

print("=" * 70)
print("TEST 8: P-TEXT PARAGRAPH STRUCTURE")
print("=" * 70)
print()

# 1. Lines per folio
print("1. P-TEXT LINES PER FOLIO")
print("-" * 50)

folio_stats = []
for folio in sorted(ptext_by_folio_line.keys()):
    lines = ptext_by_folio_line[folio]
    n_lines = len(lines)
    total_tokens = sum(len(tokens) for tokens in lines.values())
    line_nums = sorted([int(l) if l.isdigit() else 0 for l in lines.keys()])

    # Check for consecutive lines (paragraph-like)
    consecutive_runs = []
    if line_nums:
        run = [line_nums[0]]
        for i in range(1, len(line_nums)):
            if line_nums[i] == line_nums[i-1] + 1:
                run.append(line_nums[i])
            else:
                consecutive_runs.append(len(run))
                run = [line_nums[i]]
        consecutive_runs.append(len(run))

    max_run = max(consecutive_runs) if consecutive_runs else 0
    mean_run = np.mean(consecutive_runs) if consecutive_runs else 0

    folio_stats.append({
        'folio': folio,
        'n_lines': n_lines,
        'total_tokens': total_tokens,
        'max_consecutive': max_run,
        'mean_consecutive': mean_run,
        'line_range': f"{min(line_nums) if line_nums else 0}-{max(line_nums) if line_nums else 0}"
    })

    print(f"{folio:<10} {n_lines:>3} lines, {total_tokens:>4} tokens, max_run={max_run}, range={folio_stats[-1]['line_range']}")

print()

# 2. Paragraph-like structure assessment
print("2. PARAGRAPH STRUCTURE ASSESSMENT")
print("-" * 50)

total_lines = sum(s['n_lines'] for s in folio_stats)
total_tokens = sum(s['total_tokens'] for s in folio_stats)
mean_lines_per_folio = np.mean([s['n_lines'] for s in folio_stats])
mean_max_run = np.mean([s['max_consecutive'] for s in folio_stats])

print(f"Total P-text lines: {total_lines}")
print(f"Total P-text tokens: {total_tokens}")
print(f"Mean lines per folio: {mean_lines_per_folio:.1f}")
print(f"Mean max consecutive run: {mean_max_run:.1f}")
print()

# 3. Compare to AZC diagram structure
print("3. COMPARISON TO AZC DIAGRAM STRUCTURE")
print("-" * 50)

azc_lines_per_folio = []
for folio in azc_by_folio_line:
    azc_lines_per_folio.append(len(azc_by_folio_line[folio]))

if azc_lines_per_folio:
    print(f"AZC diagram mean lines per folio: {np.mean(azc_lines_per_folio):.1f}")
    print(f"P-text mean lines per folio: {mean_lines_per_folio:.1f}")
print()

# 4. Line number distribution (where on folio does P-text appear?)
print("4. LINE NUMBER DISTRIBUTION")
print("-" * 50)
print("Where does P-text appear on folios?")
print()

all_ptext_line_nums = []
for folio, lines in ptext_by_folio_line.items():
    for line_num in lines.keys():
        try:
            all_ptext_line_nums.append(int(line_num))
        except:
            pass

if all_ptext_line_nums:
    print(f"P-text line number range: {min(all_ptext_line_nums)}-{max(all_ptext_line_nums)}")
    print(f"Mean line number: {np.mean(all_ptext_line_nums):.1f}")
    print(f"Median line number: {np.median(all_ptext_line_nums):.1f}")

    # Distribution
    early = sum(1 for l in all_ptext_line_nums if l <= 5)
    mid = sum(1 for l in all_ptext_line_nums if 6 <= l <= 15)
    late = sum(1 for l in all_ptext_line_nums if l > 15)
    total = len(all_ptext_line_nums)

    print(f"\nPosition distribution:")
    print(f"  Early (1-5): {early} ({early/total*100:.1f}%)")
    print(f"  Middle (6-15): {mid} ({mid/total*100:.1f}%)")
    print(f"  Late (16+): {late} ({late/total*100:.1f}%)")

print()

# 5. f65v special analysis
print("5. f65v SPECIAL ANALYSIS")
print("-" * 50)

if 'f65v' in ptext_by_folio_line:
    f65v_lines = ptext_by_folio_line['f65v']
    f65v_tokens = sum(len(tokens) for tokens in f65v_lines.values())
    f65v_line_nums = sorted([int(l) if l.isdigit() else 0 for l in f65v_lines.keys()])

    print(f"f65v P-text lines: {len(f65v_lines)}")
    print(f"f65v P-text tokens: {f65v_tokens}")
    print(f"f65v line range: {min(f65v_line_nums)}-{max(f65v_line_nums)}")

    # Is it paragraph-like?
    if len(f65v_line_nums) > 1:
        gaps = [f65v_line_nums[i+1] - f65v_line_nums[i] for i in range(len(f65v_line_nums)-1)]
        mean_gap = np.mean(gaps)
        print(f"f65v mean line gap: {mean_gap:.2f}")
        if mean_gap < 1.5:
            print("=> f65v P-text is PARAGRAPH-LIKE (consecutive lines)")
        else:
            print("=> f65v P-text is SCATTERED (non-consecutive lines)")

print()

# Verdict
print("=" * 70)
print("VERDICT")
print("=" * 70)

if mean_max_run >= 3:
    structure_verdict = "PARAGRAPH-LIKE"
    print(f"P-text forms multi-line blocks (mean max consecutive run: {mean_max_run:.1f})")
    print("This is characteristic of CURRIER A paragraph structure")
else:
    structure_verdict = "LABEL-LIKE"
    print(f"P-text is mostly isolated lines (mean max consecutive run: {mean_max_run:.1f})")
    print("This is characteristic of AZC DIAGRAM labels")

print(f"\nStructure verdict: {structure_verdict}")
