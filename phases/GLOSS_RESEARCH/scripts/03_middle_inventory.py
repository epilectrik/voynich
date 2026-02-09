"""Middle inventory: coverage check and heat-family analysis.

What middles need glosses? What do the K-family middles look like?
Can we distinguish heat sources?
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Count all middles in B tokens
middle_counts = Counter()
middle_tokens = defaultdict(set)
middle_folios = defaultdict(set)
middle_prefixes = defaultdict(Counter)
middle_suffixes = defaultdict(Counter)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m.middle:
        middle_counts[m.middle] += 1
        middle_tokens[m.middle].add(t.word)
        middle_folios[m.middle].add(t.folio)
        middle_prefixes[m.middle][m.prefix or '(none)'] += 1
        middle_suffixes[m.middle][m.suffix or '(none)'] += 1

# Load middle dictionary
md = json.load(open('data/middle_dictionary.json', encoding='utf-8'))
middles = md.get('middles', {})

glossed = sum(1 for m in middles.values() if m.get('gloss'))
print(f'Unique middles in B: {len(middle_counts)}')
print(f'Middle dict entries: {len(middles)}')
print(f'Glossed middles: {glossed}')

# Top 50
print(f'\n{"="*80}')
print(f'TOP 50 MIDDLES BY FREQUENCY')
print(f'{"="*80}')
print(f'{"Middle":<14} {"Count":>6} {"Folios":>6} {"Kernel":>6} {"Gloss":<25}')
print('-' * 70)
for mid, count in middle_counts.most_common(50):
    entry = middles.get(mid, {})
    gloss = entry.get('gloss', '')
    kernel = entry.get('kernel_type', entry.get('kernel', '')) or ''
    nfol = len(middle_folios[mid])
    mark = '*' if gloss else ' '
    print(f'{mark}{mid:<13} {count:>6} {nfol:>6} {kernel:>6} {(gloss or "-"):<25}')

# K-family deep dive
print(f'\n{"="*80}')
print(f'K-FAMILY (HEAT) MIDDLES - DETAILED')
print(f'{"="*80}')
print(f'These are the middles that contain k as a kernel operator.\n')

k_middles_list = []
for mid, count in middle_counts.most_common():
    entry = middles.get(mid, {})
    kernel = entry.get('kernel_type', entry.get('kernel', ''))
    # K kernel or starts with k or contains k as core
    if kernel in ('K', 'KE', 'KH') or mid == 'k':
        k_middles_list.append((mid, count, entry))

for mid, count, entry in sorted(k_middles_list, key=lambda x: -x[1]):
    if count < 5:
        continue
    gloss = entry.get('gloss', '')
    kernel = entry.get('kernel_type', entry.get('kernel', ''))
    nfol = len(middle_folios[mid])

    # What prefixes combine with this middle?
    top_pre = middle_prefixes[mid].most_common(5)
    pre_str = ', '.join(f'{p}({n})' for p, n in top_pre)

    # What suffixes?
    top_suf = middle_suffixes[mid].most_common(5)
    suf_str = ', '.join(f'{s}({n})' for s, n in top_suf)

    # Sample tokens
    samples = sorted(middle_tokens[mid], key=lambda x: -len(x))[:6]

    print(f'\n  {mid:<12} n={count:>5}  fol={nfol:>2}  K={kernel:<4}  gloss={gloss or "(none)"}')
    print(f'    prefixes: {pre_str}')
    print(f'    suffixes: {suf_str}')
    print(f'    tokens:   {", ".join(samples)}')

# What are the distinct "heat operations"?
print(f'\n{"="*80}')
print(f'HEAT OPERATION DIFFERENTIATION')
print(f'{"="*80}')
print(f'Can we distinguish heat source/method from the middle?')
print(f'Comparing k, kch, ckh, ksh, ek, ke as heat variants:\n')

heat_variants = ['k', 'kch', 'ckh', 'ksh', 'ek', 'ke', 'eckh', 'cth']
for mid in heat_variants:
    if mid not in middle_counts:
        continue
    count = middle_counts[mid]
    nfol = len(middle_folios[mid])
    entry = middles.get(mid, {})
    gloss = entry.get('gloss', '')

    # Prefix breakdown
    pre = middle_prefixes[mid]
    total_pre = sum(pre.values())
    qo_pct = pre.get('qo', 0) / total_pre * 100
    ch_pct = pre.get('ch', 0) / total_pre * 100
    sh_pct = pre.get('sh', 0) / total_pre * 100
    ol_pct = pre.get('ol', 0) / total_pre * 100
    ok_pct = pre.get('ok', 0) / total_pre * 100
    none_pct = pre.get('(none)', 0) / total_pre * 100

    # Suffix breakdown
    suf = middle_suffixes[mid]
    total_suf = sum(suf.values())
    dy_pct = suf.get('dy', 0) / total_suf * 100
    ey_pct = suf.get('ey', 0) / total_suf * 100
    y_pct = suf.get('y', 0) / total_suf * 100
    hy_pct = suf.get('hy', 0) / total_suf * 100
    edy_pct = suf.get('edy', 0) / total_suf * 100

    print(f'  {mid:<8} n={count:>5}  fol={nfol:>2}  gloss={gloss or "(none)"}')
    print(f'    PREFIX: qo={qo_pct:.0f}% ch={ch_pct:.0f}% sh={sh_pct:.0f}% ol={ol_pct:.0f}% ok={ok_pct:.0f}% none={none_pct:.0f}%')
    print(f'    SUFFIX: -dy={dy_pct:.0f}% -ey={ey_pct:.0f}% -y={y_pct:.0f}% -hy={hy_pct:.0f}% -edy={edy_pct:.0f}%')

# Unglossed high-frequency
print(f'\n{"="*80}')
print(f'TOP 30 UNGLOSSED MIDDLES (by frequency)')
print(f'{"="*80}')
unglossed = [(mid, count) for mid, count in middle_counts.most_common()
             if not middles.get(mid, {}).get('gloss')]
for mid, count in unglossed[:30]:
    entry = middles.get(mid, {})
    kernel = entry.get('kernel', entry.get('kernel_type', '?'))
    nfol = len(middle_folios[mid])
    samples = sorted(middle_tokens[mid])[:5]
    print(f'  {mid:<14} n={count:>5}  fol={nfol:>2}  K={kernel or "?":<4}  ex: {", ".join(samples)}')

print(f'\nDone.')
