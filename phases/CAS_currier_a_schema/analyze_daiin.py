"""Analyze daiin usage patterns in Currier A."""
from pathlib import Path
from collections import Counter

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

lines_data = {}

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                folio = parts[1].strip('"').strip() if len(parts) > 1 else ''
                line_num = parts[2].strip('"').strip() if len(parts) > 2 else ''
                key = f'{folio}_{line_num}'
                if key not in lines_data:
                    lines_data[key] = []
                if word:
                    lines_data[key].append(word)

daiin_lines = [(k, v) for k, v in lines_data.items() if 'daiin' in v]

print(f'Lines containing daiin: {len(daiin_lines)}')
print(f'Total A lines: {len(lines_data)}')
print(f'Percentage: {100*len(daiin_lines)/len(lines_data):.1f}%')
print()

daiin_only = 0
daiin_with_others = 0
other_tokens_with_daiin = Counter()

for key, tokens in daiin_lines:
    non_daiin = [t for t in tokens if t != 'daiin']
    if len(non_daiin) == 0:
        daiin_only += 1
    else:
        daiin_with_others += 1
        for t in non_daiin:
            other_tokens_with_daiin[t] += 1

print(f'Lines with ONLY daiin: {daiin_only} ({100*daiin_only/len(daiin_lines):.1f}%)')
print(f'Lines with daiin + others: {daiin_with_others} ({100*daiin_with_others/len(daiin_lines):.1f}%)')
print()
print('Top 15 tokens appearing WITH daiin:')
for tok, ct in other_tokens_with_daiin.most_common(15):
    print(f'  {tok}: {ct}')

print()
print('Daiin repetition counts per line:')
daiin_counts = Counter()
for key, tokens in daiin_lines:
    ct = tokens.count('daiin')
    daiin_counts[ct] += 1

for ct in sorted(daiin_counts.keys()):
    print(f'  {ct}x daiin: {daiin_counts[ct]} lines')

# Also check: what markers accompany daiin?
print()
print('Markers on lines containing daiin:')
markers = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
marker_counts = Counter()
for key, tokens in daiin_lines:
    for tok in tokens:
        for m in markers:
            if tok.startswith(m) and tok != 'daiin':
                marker_counts[m] += 1
                break

for m, ct in marker_counts.most_common():
    print(f'  {m}: {ct}')
