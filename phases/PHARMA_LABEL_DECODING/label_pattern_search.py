"""Search for structural patterns in labeled lines and find matches in unlabeled Currier A.

If labels mark real categories, we should find:
1. Lines with same label share structural features
2. Similar structures exist in regular A pages (without labels)
"""
import csv
from collections import defaultdict, Counter
import re

print('Loading manuscript data...')
all_tokens = []
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber') == 'H':
            all_tokens.append(row)

# Build line-level data
lines = defaultdict(lambda: {'label': None, 'tokens': [], 'folio': None, 'language': None})

for t in all_tokens:
    folio = t.get('folio')
    line_num = t.get('line_number')
    placement = t.get('placement', '')
    word = t.get('word', '')
    language = t.get('language', '')

    key = (folio, line_num)
    lines[key]['folio'] = folio
    lines[key]['language'] = language

    if placement.startswith('L') and len(word) == 1:
        lines[key]['label'] = word
    elif placement.startswith('P') and word:
        lines[key]['tokens'].append(word)

# Extract structural features from a line
def get_line_features(tokens):
    if not tokens:
        return None

    features = {}

    # Length
    features['n_tokens'] = len(tokens)

    # First token
    features['first_token'] = tokens[0] if tokens else ''
    features['first_char'] = tokens[0][0] if tokens and tokens[0] else ''

    # Last token
    features['last_token'] = tokens[-1] if tokens else ''
    features['last_char'] = tokens[-1][-1] if tokens and tokens[-1] else ''

    # Common suffixes
    suffixes = []
    for t in tokens:
        if t.endswith('aiin'):
            suffixes.append('aiin')
        elif t.endswith('ain'):
            suffixes.append('ain')
        elif t.endswith('dy'):
            suffixes.append('dy')
        elif t.endswith('y'):
            suffixes.append('y')
        elif t.endswith('ol'):
            suffixes.append('ol')
        elif t.endswith('or'):
            suffixes.append('or')
        elif t.endswith('ar'):
            suffixes.append('ar')
        elif t.endswith('al'):
            suffixes.append('al')

    features['suffix_profile'] = Counter(suffixes)
    features['dominant_suffix'] = suffixes[0] if suffixes else None

    # PREFIX distribution
    def get_prefix(word):
        for p in ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da']:
            if word.startswith(p):
                return p
        return 'other'

    prefixes = [get_prefix(t) for t in tokens]
    features['prefix_profile'] = Counter(prefixes)
    features['dominant_prefix'] = max(features['prefix_profile'], key=features['prefix_profile'].get) if prefixes else None

    # Check for 'daiin' presence (common structural marker)
    features['has_daiin'] = any('daiin' in t for t in tokens)

    # Check for 'chol' or 'shol' (common tokens)
    features['has_chol'] = any(t in ['chol', 'shol', 'cthol', 'tchol'] for t in tokens)

    return features

# Analyze f49v labeled lines
print()
print('=' * 70)
print('f49v LABELED LINE STRUCTURAL ANALYSIS')
print('=' * 70)

f49v_lines = {k: v for k, v in lines.items() if v['folio'] == 'f49v' and v['tokens']}

# Group by label
by_label = defaultdict(list)
for key, data in f49v_lines.items():
    if data['label']:
        features = get_line_features(data['tokens'])
        by_label[data['label']].append({
            'line': key[1],
            'tokens': data['tokens'],
            'features': features
        })

print('\nStructural features by label:')
print()

for label in sorted(by_label.keys()):
    lines_data = by_label[label]
    if len(lines_data) >= 2:
        print(f'[{label}] - {len(lines_data)} lines:')

        # Aggregate features
        all_n_tokens = [l['features']['n_tokens'] for l in lines_data]
        all_first_chars = [l['features']['first_char'] for l in lines_data]
        all_last_chars = [l['features']['last_char'] for l in lines_data]
        all_dom_prefix = [l['features']['dominant_prefix'] for l in lines_data]
        all_has_daiin = [l['features']['has_daiin'] for l in lines_data]

        print(f'  Token counts: {all_n_tokens} (mean: {sum(all_n_tokens)/len(all_n_tokens):.1f})')
        print(f'  First chars: {all_first_chars}')
        print(f'  Last chars: {all_last_chars}')
        print(f'  Dominant PREFIX: {all_dom_prefix}')
        print(f'  Has daiin: {all_has_daiin}')

        # Check for consistency
        if len(set(all_dom_prefix)) == 1:
            print(f'  *** CONSISTENT dominant PREFIX: {all_dom_prefix[0]}')
        if len(set(all_first_chars)) == 1:
            print(f'  *** CONSISTENT first char: {all_first_chars[0]}')
        print()

# Now look for patterns that distinguish labels
print('=' * 70)
print('DISTINCTIVE PATTERNS BY LABEL')
print('=' * 70)

label_signatures = {}
for label, lines_data in by_label.items():
    if len(lines_data) >= 2:
        # What's consistent across lines with this label?
        dom_prefixes = Counter(l['features']['dominant_prefix'] for l in lines_data)
        first_chars = Counter(l['features']['first_char'] for l in lines_data)
        has_daiin = sum(1 for l in lines_data if l['features']['has_daiin'])

        label_signatures[label] = {
            'n_lines': len(lines_data),
            'dom_prefix': dom_prefixes.most_common(1)[0] if dom_prefixes else None,
            'first_char': first_chars.most_common(1)[0] if first_chars else None,
            'daiin_rate': has_daiin / len(lines_data)
        }

print('\nLabel signatures (from lines with 2+ occurrences):')
print(f'{"Label":<6} {"Lines":<6} {"Dom PREFIX":<15} {"First char":<15} {"daiin rate":<10}')
print('-' * 60)
for label, sig in sorted(label_signatures.items()):
    dp = f"{sig['dom_prefix'][0]}({sig['dom_prefix'][1]})" if sig['dom_prefix'] else '-'
    fc = f"{sig['first_char'][0]}({sig['first_char'][1]})" if sig['first_char'] else '-'
    print(f'{label:<6} {sig["n_lines"]:<6} {dp:<15} {fc:<15} {sig["daiin_rate"]:<10.1%}')

# Now search for similar patterns in OTHER Currier A pages
print()
print('=' * 70)
print('SEARCHING FOR SIMILAR PATTERNS IN UNLABELED CURRIER A')
print('=' * 70)

# Get all Currier A lines (excluding f49v)
a_lines = {k: v for k, v in lines.items()
           if v['language'] == 'A' and v['folio'] != 'f49v' and v['tokens']}

print(f'\nTotal Currier A lines (excluding f49v): {len(a_lines)}')

# For each distinctive label pattern, find matching lines in A
print('\nSearching for lines that match label signatures...')

for label, sig in label_signatures.items():
    if sig['dom_prefix']:
        target_prefix = sig['dom_prefix'][0]

        # Find A lines with same dominant PREFIX
        matching = []
        for key, data in a_lines.items():
            features = get_line_features(data['tokens'])
            if features and features['dominant_prefix'] == target_prefix:
                matching.append({
                    'folio': data['folio'],
                    'line': key[1],
                    'tokens': data['tokens'][:5],
                    'n_tokens': len(data['tokens'])
                })

        print(f'\n[{label}] signature (dominant PREFIX = {target_prefix}):')
        print(f'  Found {len(matching)} matching lines in other A folios')

        # Show distribution by folio
        folio_counts = Counter(m['folio'] for m in matching)
        top_folios = folio_counts.most_common(5)
        print(f'  Top folios: {top_folios}')

        # Show a few examples
        if matching[:3]:
            print(f'  Examples:')
            for m in matching[:3]:
                print(f'    {m["folio"]} line {m["line"]}: {" ".join(m["tokens"])}...')

# Check if certain folios are enriched for certain "label types"
print()
print('=' * 70)
print('FOLIO ENRICHMENT ANALYSIS')
print('=' * 70)

# For each A folio, calculate its "label profile" based on line signatures
folio_profiles = defaultdict(lambda: Counter())

for key, data in a_lines.items():
    folio = data['folio']
    features = get_line_features(data['tokens'])
    if features:
        dom_prefix = features['dominant_prefix']
        # Map prefix back to potential label
        # Based on f49v: k->ch(89%), o->sh(29%), etc.
        folio_profiles[folio][dom_prefix] += 1

print('\nFolio PREFIX profiles (would-be label distribution):')
print('If labels mark PREFIX-dominant categories, folios should cluster...')
print()

# Find folios that are strongly dominated by one PREFIX
dominated_folios = []
for folio, profile in folio_profiles.items():
    total = sum(profile.values())
    if total >= 5:  # At least 5 lines
        top_prefix, top_count = profile.most_common(1)[0]
        dominance = top_count / total
        if dominance >= 0.5:  # 50%+ dominated by one PREFIX
            dominated_folios.append({
                'folio': folio,
                'dominant': top_prefix,
                'dominance': dominance,
                'total': total
            })

print(f'Folios with 50%+ PREFIX dominance (potential "typed" folios):')
print(f'{"Folio":<10} {"Dominant":<10} {"Dominance":<12} {"Lines":<6}')
print('-' * 40)
for f in sorted(dominated_folios, key=lambda x: -x['dominance'])[:15]:
    print(f'{f["folio"]:<10} {f["dominant"]:<10} {f["dominance"]:<12.1%} {f["total"]:<6}')
