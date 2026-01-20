"""Full manuscript search for L-placement label patterns.

Tests whether single-character labels correlate with PREFIX patterns,
as suggested by the f49v analysis.
"""
import csv
from collections import defaultdict, Counter
from scipy import stats
import numpy as np

# Load all H-transcriber data
print('Loading manuscript data (H-transcriber only)...')
all_tokens = []
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber') == 'H':
            all_tokens.append(row)

print(f'Total H-track tokens: {len(all_tokens)}')

# Separate L-placement from P-placement
l_tokens = [t for t in all_tokens if t.get('placement', '').startswith('L')]
p_tokens = [t for t in all_tokens if t.get('placement', '').startswith('P')]

print(f'L-placement (labels): {len(l_tokens)}')
print(f'P-placement (text): {len(p_tokens)}')

# Focus on single-character labels
single_char_labels = [t for t in l_tokens if len(t.get('word', '')) == 1]
print(f'Single-character labels: {len(single_char_labels)}')

# Group by folio
labels_by_folio = defaultdict(list)
for t in single_char_labels:
    labels_by_folio[t.get('folio')].append(t)

print(f'\nFolios with single-char labels: {len(labels_by_folio)}')
for folio, tokens in sorted(labels_by_folio.items(), key=lambda x: -len(x[1])):
    chars = [t.get('word') for t in tokens]
    lang = tokens[0].get('language', '?')
    section = tokens[0].get('section', '?')
    print(f'  {folio:8} [{lang}] ({section}): {len(tokens):2} labels - {" ".join(chars[:12])}{"..." if len(chars) > 12 else ""}')

# For each folio with single-char labels, analyze the relationship
# between label and line content
print()
print('=' * 70)
print('PREFIX PATTERN ANALYSIS BY LABEL')
print('=' * 70)

def get_prefix(word):
    """Extract PREFIX family from token."""
    prefixes = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'or', 'ar', 'al', 'da', 'ct']
    for p in prefixes:
        if word.startswith(p):
            return p
    return 'other'

# Build a mapping of (folio, line_number) -> (label_char, line_tokens)
line_data = defaultdict(lambda: {'label': None, 'tokens': []})

for t in all_tokens:
    folio = t.get('folio')
    line = t.get('line_number')
    placement = t.get('placement', '')
    word = t.get('word', '')

    key = (folio, line)

    if placement.startswith('L') and len(word) == 1:
        line_data[key]['label'] = word
    elif placement.startswith('P') and word:
        line_data[key]['tokens'].append(word)

# Now analyze: for lines with single-char labels, what's the PREFIX distribution?
label_prefix_data = defaultdict(list)  # label -> list of prefix counts

for (folio, line), data in line_data.items():
    if data['label'] and data['tokens']:
        label = data['label']
        prefixes = [get_prefix(w) for w in data['tokens']]
        prefix_counts = Counter(prefixes)
        label_prefix_data[label].append(prefix_counts)

print('\nAggregate PREFIX distribution by label (all folios combined):')
print()
print(f'{"Label":<6} {"Lines":<6} {"ch%":<8} {"sh%":<8} {"qo%":<8} {"da%":<8} {"other%":<8}')
print('-' * 60)

# Aggregate all prefix counts per label
label_totals = {}
for label in sorted(label_prefix_data.keys()):
    all_counts = Counter()
    for counts in label_prefix_data[label]:
        all_counts.update(counts)
    total = sum(all_counts.values())
    if total > 0:
        label_totals[label] = {
            'n_lines': len(label_prefix_data[label]),
            'n_tokens': total,
            'ch': all_counts.get('ch', 0) / total * 100,
            'sh': all_counts.get('sh', 0) / total * 100,
            'qo': all_counts.get('qo', 0) / total * 100,
            'da': all_counts.get('da', 0) / total * 100,
            'other': all_counts.get('other', 0) / total * 100,
            'counts': all_counts
        }
        t = label_totals[label]
        print(f'{label:<6} {t["n_lines"]:<6} {t["ch"]:<8.1f} {t["sh"]:<8.1f} {t["qo"]:<8.1f} {t["da"]:<8.1f} {t["other"]:<8.1f}')

# Statistical test: Chi-square for independence of label and PREFIX
print()
print('=' * 70)
print('STATISTICAL TEST: Label-PREFIX Independence')
print('=' * 70)

# Build contingency table (labels x prefixes)
all_labels = sorted(label_totals.keys())
prefix_categories = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'other']

# Filter to labels with sufficient data (>5 tokens)
valid_labels = [l for l in all_labels if label_totals[l]['n_tokens'] >= 5]

if len(valid_labels) >= 2:
    contingency = []
    for label in valid_labels:
        row = [label_totals[label]['counts'].get(p, 0) for p in prefix_categories]
        contingency.append(row)

    contingency = np.array(contingency)

    # Chi-square test
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    print(f'\nContingency table shape: {contingency.shape}')
    print(f'Labels tested: {valid_labels}')
    print(f'PREFIX categories: {prefix_categories}')
    print()
    print(f'Chi-square statistic: {chi2:.2f}')
    print(f'Degrees of freedom: {dof}')
    print(f'P-value: {p_value:.6f}')

    if p_value < 0.05:
        print('\n*** SIGNIFICANT: Labels are NOT independent of PREFIX (p < 0.05) ***')
        print('This supports the hypothesis that labels mark PREFIX-domain categories.')
    else:
        print('\n*** NOT SIGNIFICANT: Cannot reject independence (p >= 0.05) ***')
        print('Labels may be randomly distributed with respect to PREFIX.')
else:
    print('Insufficient data for chi-square test (need at least 2 labels with 5+ tokens)')

# Compare f49v to other folios
print()
print('=' * 70)
print('f49v vs OTHER FOLIOS COMPARISON')
print('=' * 70)

f49v_labels = [t for t in single_char_labels if t.get('folio') == 'f49v']
other_labels = [t for t in single_char_labels if t.get('folio') != 'f49v']

print(f'f49v single-char labels: {len(f49v_labels)}')
print(f'Other folios single-char labels: {len(other_labels)}')

if other_labels:
    print('\nLabel character distribution:')
    f49v_chars = Counter(t.get('word') for t in f49v_labels)
    other_chars = Counter(t.get('word') for t in other_labels)

    all_chars = set(f49v_chars.keys()) | set(other_chars.keys())
    print(f'{"Char":<6} {"f49v":<8} {"Other":<8}')
    print('-' * 25)
    for char in sorted(all_chars):
        print(f'{char:<6} {f49v_chars.get(char, 0):<8} {other_chars.get(char, 0):<8}')

# Check if the "numeral" characters (o, r, y, e) behave differently
print()
print('=' * 70)
print('NUMERAL CANDIDATE ANALYSIS (o, r, y, e)')
print('=' * 70)

numeral_chars = {'o', 'r', 'y', 'e'}
non_numeral_chars = {'f', 'k', 's', 'p', 'd'}

numeral_labels = [l for l in valid_labels if l in numeral_chars]
non_numeral_labels = [l for l in valid_labels if l in non_numeral_chars]

if numeral_labels:
    print('\n"Numeral" labels (o, r, y, e):')
    for label in numeral_labels:
        t = label_totals[label]
        print(f'  {label}: {t["n_lines"]} lines, {t["n_tokens"]} tokens')
        print(f'      ch:{t["ch"]:.1f}% sh:{t["sh"]:.1f}% qo:{t["qo"]:.1f}% da:{t["da"]:.1f}% other:{t["other"]:.1f}%')

if non_numeral_labels:
    print('\n"Non-numeral" labels (f, k, s, p, d):')
    for label in non_numeral_labels:
        t = label_totals[label]
        print(f'  {label}: {t["n_lines"]} lines, {t["n_tokens"]} tokens')
        print(f'      ch:{t["ch"]:.1f}% sh:{t["sh"]:.1f}% qo:{t["qo"]:.1f}% da:{t["da"]:.1f}% other:{t["other"]:.1f}%')

# Summary
print()
print('=' * 70)
print('SUMMARY')
print('=' * 70)
print(f'Total single-char labels in manuscript: {len(single_char_labels)}')
print(f'Folios with single-char labels: {len(labels_by_folio)}')
print(f'f49v contains {len(f49v_labels)}/{len(single_char_labels)} ({len(f49v_labels)/len(single_char_labels)*100:.1f}%) of all single-char labels')
print()
if p_value < 0.05:
    print('FINDING: Single-char labels show statistically significant PREFIX correlation.')
    print('This suggests labels function as categorical markers for PREFIX domains.')
else:
    print('FINDING: No significant PREFIX correlation detected.')
    print('Labels may be positional markers without PREFIX-specific meaning.')
