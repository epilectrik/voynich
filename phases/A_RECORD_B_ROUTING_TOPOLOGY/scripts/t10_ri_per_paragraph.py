"""
T10: RI Content Per Paragraph

How many RI tokens does a typical paragraph contain?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

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

# Collect tokens by line
a_tokens_by_line = defaultdict(list)
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    a_tokens_by_line[(token.folio, token.line)].append({
        'word': w,
        'middle': m.middle,
        'is_pp': m.middle in b_middles if m.middle else False,
        'is_ri': m.middle not in b_middles if m.middle else False,
    })

# Build paragraphs
paragraphs = []
a_folios = defaultdict(list)
for (folio, line), tokens in sorted(a_tokens_by_line.items()):
    a_folios[folio].append((line, tokens))

for folio in sorted(a_folios.keys()):
    lines = a_folios[folio]
    current_para_tokens = []

    for line, tokens in lines:
        # Check if gallows-initial
        if tokens and starts_with_gallows(tokens[0]['word']):
            if current_para_tokens:
                paragraphs.append(current_para_tokens)
            current_para_tokens = []
        current_para_tokens.extend(tokens)

    if current_para_tokens:
        paragraphs.append(current_para_tokens)

# Analyze RI content
ri_counts = []
pp_counts = []
total_counts = []
ri_unique_counts = []
pp_unique_counts = []

for para in paragraphs:
    ri = sum(1 for t in para if t['is_ri'])
    pp = sum(1 for t in para if t['is_pp'])
    ri_unique = len(set(t['middle'] for t in para if t['is_ri'] and t['middle']))
    pp_unique = len(set(t['middle'] for t in para if t['is_pp'] and t['middle']))

    ri_counts.append(ri)
    pp_counts.append(pp)
    total_counts.append(len(para))
    ri_unique_counts.append(ri_unique)
    pp_unique_counts.append(pp_unique)

print('=' * 60)
print('RI CONTENT PER PARAGRAPH')
print('=' * 60)
print(f'Total paragraphs: {len(paragraphs)}')
print()
print('RI tokens per paragraph:')
print(f'  Mean: {np.mean(ri_counts):.1f}')
print(f'  Median: {np.median(ri_counts):.0f}')
print(f'  Std: {np.std(ri_counts):.1f}')
print(f'  Min: {min(ri_counts)}, Max: {max(ri_counts)}')
print()
print('Unique RI MIDDLEs per paragraph:')
print(f'  Mean: {np.mean(ri_unique_counts):.1f}')
print(f'  Median: {np.median(ri_unique_counts):.0f}')
print()
print('PP tokens per paragraph:')
print(f'  Mean: {np.mean(pp_counts):.1f}')
print(f'  Median: {np.median(pp_counts):.0f}')
print()
print('Unique PP MIDDLEs per paragraph:')
print(f'  Mean: {np.mean(pp_unique_counts):.1f}')
print(f'  Median: {np.median(pp_unique_counts):.0f}')
print()
print('Total tokens per paragraph:')
print(f'  Mean: {np.mean(total_counts):.1f}')
print(f'  Median: {np.median(total_counts):.0f}')
print()
print('RI as fraction of paragraph:')
ri_fracs = [r/t if t > 0 else 0 for r, t in zip(ri_counts, total_counts)]
print(f'  Mean: {np.mean(ri_fracs):.1%}')
print(f'  Median: {np.median(ri_fracs):.1%}')
print()
print('=' * 60)
print('DISTRIBUTION OF RI COUNT PER PARAGRAPH')
print('=' * 60)
ri_dist = Counter(ri_counts)
for count in sorted(ri_dist.keys())[:15]:
    pct = ri_dist[count] / len(paragraphs) * 100
    bar = '#' * int(pct)
    print(f'  {count:2} RI: {ri_dist[count]:3} paras ({pct:4.1f}%) {bar}')
if max(ri_counts) > 14:
    print(f'  15+: {sum(v for k,v in ri_dist.items() if k >= 15)} paras')

print()
print('=' * 60)
print('PARAGRAPHS WITH 0 RI vs 1+ RI')
print('=' * 60)
zero_ri = sum(1 for r in ri_counts if r == 0)
one_plus_ri = sum(1 for r in ri_counts if r >= 1)
print(f'  0 RI:  {zero_ri} ({zero_ri/len(paragraphs)*100:.1f}%)')
print(f'  1+ RI: {one_plus_ri} ({one_plus_ri/len(paragraphs)*100:.1f}%)')
print()
print('Paragraphs with exactly 1 unique RI (single substance?):')
single_ri = sum(1 for r in ri_unique_counts if r == 1)
print(f'  {single_ri} ({single_ri/len(paragraphs)*100:.1f}%)')
