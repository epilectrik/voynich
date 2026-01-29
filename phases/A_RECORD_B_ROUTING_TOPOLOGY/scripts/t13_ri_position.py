"""
T13: RI Positional Analysis

Where does RI appear within paragraphs?
- Beginning (identity first, then operations)?
- End (operations first, then context)?
- Scattered throughout?
- First line only vs distributed across lines?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("T13: RI POSITIONAL ANALYSIS")
print("=" * 70)

# Build B vocabulary for PP/RI classification
b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    if not word:
        return False
    w = word.strip()
    return bool(w) and w[0] in GALLOWS

# Collect A tokens by line
a_tokens_by_line = defaultdict(list)
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    is_ri = m.middle not in b_middles if m.middle else False
    a_tokens_by_line[(token.folio, token.line)].append({
        'word': w,
        'middle': m.middle,
        'is_ri': is_ri,
        'is_pp': not is_ri and m.middle is not None,
    })

# Build paragraphs with line structure preserved
paragraphs = []
a_folios = defaultdict(list)
for (folio, line), tokens in sorted(a_tokens_by_line.items()):
    a_folios[folio].append((line, tokens))

for folio in sorted(a_folios.keys()):
    lines_data = a_folios[folio]
    current_para = {'folio': folio, 'lines': [], 'all_tokens': []}

    for line, tokens in lines_data:
        if tokens and starts_with_gallows(tokens[0]['word']):
            if current_para['lines']:
                paragraphs.append(current_para)
            current_para = {'folio': folio, 'lines': [], 'all_tokens': []}

        current_para['lines'].append({'line': line, 'tokens': tokens})
        current_para['all_tokens'].extend(tokens)

    if current_para['lines']:
        paragraphs.append(current_para)

paras_with_ri = [p for p in paragraphs if any(t['is_ri'] for t in p['all_tokens'])]
print(f"\nTotal paragraphs: {len(paragraphs)}")
print(f"Paragraphs with RI: {len(paras_with_ri)}")

# Test 1: RI position within paragraph (token-level)
print("\n" + "=" * 70)
print("TEST 1: RI POSITION WITHIN PARAGRAPH (TOKEN-LEVEL)")
print("=" * 70)

ri_positions = []  # relative position 0-1
pp_positions = []

for p in paras_with_ri:
    tokens = p['all_tokens']
    n = len(tokens)
    if n < 2:
        continue

    for i, t in enumerate(tokens):
        rel_pos = i / (n - 1)
        if t['is_ri']:
            ri_positions.append(rel_pos)
        elif t['is_pp']:
            pp_positions.append(rel_pos)

print(f"\nMean relative position (0=start, 1=end):")
print(f"  RI: {np.mean(ri_positions):.3f} (n={len(ri_positions)})")
print(f"  PP: {np.mean(pp_positions):.3f} (n={len(pp_positions)})")

# Position buckets
def bucket(pos):
    if pos < 0.2:
        return 'INITIAL'
    elif pos < 0.4:
        return 'EARLY'
    elif pos < 0.6:
        return 'MIDDLE'
    elif pos < 0.8:
        return 'LATE'
    else:
        return 'FINAL'

ri_buckets = Counter(bucket(p) for p in ri_positions)
pp_buckets = Counter(bucket(p) for p in pp_positions)

print(f"\nPosition distribution:")
print(f"  {'Position':<10} {'RI':>8} {'RI%':>8} {'PP':>8} {'PP%':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
for pos in ['INITIAL', 'EARLY', 'MIDDLE', 'LATE', 'FINAL']:
    ri_n = ri_buckets.get(pos, 0)
    pp_n = pp_buckets.get(pos, 0)
    ri_pct = ri_n / len(ri_positions) * 100 if ri_positions else 0
    pp_pct = pp_n / len(pp_positions) * 100 if pp_positions else 0
    print(f"  {pos:<10} {ri_n:>8} {ri_pct:>7.1f}% {pp_n:>8} {pp_pct:>7.1f}%")

# Statistical test
from scipy.stats import mannwhitneyu
stat, p = mannwhitneyu(ri_positions, pp_positions)
print(f"\nMann-Whitney U test (RI vs PP position): p={p:.2e}")

# Test 2: RI position by line within paragraph
print("\n" + "=" * 70)
print("TEST 2: RI DISTRIBUTION BY LINE WITHIN PARAGRAPH")
print("=" * 70)

ri_in_line = defaultdict(int)  # line index -> count
pp_in_line = defaultdict(int)
line_counts = defaultdict(int)  # line index -> total paragraphs with that line

for p in paras_with_ri:
    n_lines = len(p['lines'])
    for i, line_data in enumerate(p['lines']):
        line_counts[i] += 1
        for t in line_data['tokens']:
            if t['is_ri']:
                ri_in_line[i] += 1
            elif t['is_pp']:
                pp_in_line[i] += 1

print(f"\nRI tokens by line position:")
print(f"  {'Line':>6} {'RI':>8} {'RI/para':>10} {'PP':>8} {'PP/para':>10}")
print(f"  {'-'*6} {'-'*8} {'-'*10} {'-'*8} {'-'*10}")
for i in range(min(10, max(line_counts.keys()) + 1)):
    if line_counts[i] > 0:
        ri_per_para = ri_in_line[i] / line_counts[i]
        pp_per_para = pp_in_line[i] / line_counts[i]
        print(f"  {i:>6} {ri_in_line[i]:>8} {ri_per_para:>10.2f} {pp_in_line[i]:>8} {pp_per_para:>10.2f}")

# Test 3: First RI position vs first PP position
print("\n" + "=" * 70)
print("TEST 3: FIRST RI vs FIRST PP POSITION")
print("=" * 70)

first_ri_pos = []
first_pp_pos = []

for p in paras_with_ri:
    tokens = p['all_tokens']
    n = len(tokens)
    if n < 2:
        continue

    first_ri = None
    first_pp = None
    for i, t in enumerate(tokens):
        if t['is_ri'] and first_ri is None:
            first_ri = i / (n - 1)
        if t['is_pp'] and first_pp is None:
            first_pp = i / (n - 1)

    if first_ri is not None:
        first_ri_pos.append(first_ri)
    if first_pp is not None:
        first_pp_pos.append(first_pp)

print(f"\nMean position of FIRST occurrence:")
print(f"  First RI: {np.mean(first_ri_pos):.3f}")
print(f"  First PP: {np.mean(first_pp_pos):.3f}")

if np.mean(first_ri_pos) < np.mean(first_pp_pos):
    print(f"  --> RI tends to appear BEFORE PP")
else:
    print(f"  --> PP tends to appear BEFORE RI")

# Test 4: Is RI concentrated in first line?
print("\n" + "=" * 70)
print("TEST 4: RI IN FIRST LINE vs REST")
print("=" * 70)

ri_first_line = 0
ri_other_lines = 0
total_first_line = 0
total_other_lines = 0

for p in paras_with_ri:
    if len(p['lines']) < 1:
        continue

    first_line_tokens = p['lines'][0]['tokens']
    other_tokens = []
    for line_data in p['lines'][1:]:
        other_tokens.extend(line_data['tokens'])

    ri_first_line += sum(1 for t in first_line_tokens if t['is_ri'])
    total_first_line += len(first_line_tokens)

    ri_other_lines += sum(1 for t in other_tokens if t['is_ri'])
    total_other_lines += len(other_tokens)

ri_rate_first = ri_first_line / total_first_line if total_first_line else 0
ri_rate_other = ri_other_lines / total_other_lines if total_other_lines else 0

print(f"\nRI density:")
print(f"  First line: {ri_first_line} RI / {total_first_line} tokens = {ri_rate_first:.1%}")
print(f"  Other lines: {ri_other_lines} RI / {total_other_lines} tokens = {ri_rate_other:.1%}")
print(f"  Ratio: {ri_rate_first/ri_rate_other:.2f}x" if ri_rate_other > 0 else "  (no RI in other lines)")

# Test 5: RI position within LINE
print("\n" + "=" * 70)
print("TEST 5: RI POSITION WITHIN LINE")
print("=" * 70)

ri_line_positions = []
pp_line_positions = []

for (folio, line), tokens in a_tokens_by_line.items():
    n = len(tokens)
    if n < 2:
        continue

    for i, t in enumerate(tokens):
        rel_pos = i / (n - 1)
        if t['is_ri']:
            ri_line_positions.append(rel_pos)
        elif t['is_pp']:
            pp_line_positions.append(rel_pos)

print(f"\nMean position within LINE (0=start, 1=end):")
print(f"  RI: {np.mean(ri_line_positions):.3f}")
print(f"  PP: {np.mean(pp_line_positions):.3f}")

ri_line_buckets = Counter(bucket(p) for p in ri_line_positions)
print(f"\nRI within-line distribution:")
for pos in ['INITIAL', 'EARLY', 'MIDDLE', 'LATE', 'FINAL']:
    n = ri_line_buckets.get(pos, 0)
    pct = n / len(ri_line_positions) * 100 if ri_line_positions else 0
    bar = '#' * int(pct / 2)
    print(f"  {pos:<10} {n:>5} ({pct:>5.1f}%) {bar}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY: RI POSITIONAL RULES")
print("=" * 70)

print(f"""
PARAGRAPH-LEVEL:
- RI mean position: {np.mean(ri_positions):.3f} vs PP: {np.mean(pp_positions):.3f}
- First RI at: {np.mean(first_ri_pos):.3f} vs First PP at: {np.mean(first_pp_pos):.3f}
- RI density in first line: {ri_rate_first:.1%} vs other lines: {ri_rate_other:.1%}

LINE-LEVEL:
- RI mean position within line: {np.mean(ri_line_positions):.3f}
- PP mean position within line: {np.mean(pp_line_positions):.3f}
""")

if np.mean(ri_positions) < 0.45:
    print("FINDING: RI is EARLY-biased in paragraphs (identity first)")
elif np.mean(ri_positions) > 0.55:
    print("FINDING: RI is LATE-biased in paragraphs (context at end)")
else:
    print("FINDING: RI is NEUTRAL in paragraphs (scattered throughout)")

if ri_rate_first > ri_rate_other * 1.5:
    print("FINDING: RI concentrates in FIRST LINE of paragraph")
elif ri_rate_first < ri_rate_other * 0.7:
    print("FINDING: RI avoids first line, appears later")
else:
    print("FINDING: RI distributed across lines")

# Save results
results = {
    'ri_mean_para_position': float(np.mean(ri_positions)),
    'pp_mean_para_position': float(np.mean(pp_positions)),
    'first_ri_mean_position': float(np.mean(first_ri_pos)),
    'first_pp_mean_position': float(np.mean(first_pp_pos)),
    'ri_rate_first_line': float(ri_rate_first),
    'ri_rate_other_lines': float(ri_rate_other),
    'ri_mean_line_position': float(np.mean(ri_line_positions)),
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't13_ri_position.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
