"""
Analyze folio-level repetition uniformity

Some folios have ALL entries with the same repetition count.
What does this tell us about the ratio hypothesis?
"""

from collections import defaultdict, Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

entries = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': ''})

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            lang = parts[6].strip('"').strip()
            if lang == 'A':
                word = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''
                if word:
                    key = f'{folio}_{line_num}'
                    entries[key]['tokens'].append(word)
                    entries[key]['section'] = section
                    entries[key]['folio'] = folio


def detect_repetition(tokens):
    n = len(tokens)
    if n < 4:
        return 0, 0, []
    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            count = n // block_size
            if count >= 2:
                block = tokens[:block_size]
                matches = True
                for i in range(1, count):
                    chunk = tokens[i * block_size:(i + 1) * block_size]
                    mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                    if mismatches > len(block) * 0.2:
                        matches = False
                        break
                if matches:
                    return block_size, count, block
    return 0, 0, []


# Group by folio
folio_reps = defaultdict(list)
for entry_id, data in entries.items():
    tokens = data['tokens']
    block_size, rep_count, block = detect_repetition(tokens)
    if rep_count >= 2:
        folio_reps[data['folio']].append({
            'rep_count': rep_count,
            'section': data['section']
        })

# Analyze folio patterns
print('FOLIO-LEVEL REPETITION PATTERNS')
print('=' * 70)

# Count folios by uniformity
uniform_folios = []
mixed_folios = []

for folio, entries_list in folio_reps.items():
    if len(entries_list) >= 5:
        counts = [e['rep_count'] for e in entries_list]
        unique_counts = set(counts)
        sections = set(e['section'] for e in entries_list)
        if len(unique_counts) == 1:
            uniform_folios.append((folio, counts[0], len(entries_list), list(sections)[0] if len(sections) == 1 else 'mixed'))
        else:
            mixed_folios.append((folio, unique_counts, len(entries_list), list(sections)[0] if len(sections) == 1 else 'mixed'))

print(f'\nUNIFORM FOLIOS (all entries same count): {len(uniform_folios)}')
print('-' * 50)
for folio, count, n, section in sorted(uniform_folios, key=lambda x: (x[1], x[0])):
    print(f'  {folio}: all {count}x ({n} entries) [{section}]')

print(f'\nMIXED FOLIOS (variable counts): {len(mixed_folios)}')
print('-' * 50)
for folio, counts, n, section in sorted(mixed_folios, key=lambda x: -x[2])[:15]:
    print(f'  {folio}: {sorted(counts)} ({n} entries) [{section}]')

# What sections are uniform vs mixed?
print('\n\nSECTION ANALYSIS')
print('=' * 70)

section_patterns = defaultdict(lambda: {'uniform': 0, 'mixed': 0, 'uniform_counts': []})
for folio, count, n, section in uniform_folios:
    section_patterns[section]['uniform'] += 1
    section_patterns[section]['uniform_counts'].append(count)

for folio, counts, n, section in mixed_folios:
    section_patterns[section]['mixed'] += 1

print(f'\n{"Section":<15} {"Uniform":>10} {"Mixed":>10} {"Ratio":>10} {"Uniform Counts"}')
print('-' * 70)
for section in sorted(section_patterns.keys()):
    u = section_patterns[section]['uniform']
    m = section_patterns[section]['mixed']
    ratio = u / (u + m) if (u + m) > 0 else 0
    counts = Counter(section_patterns[section]['uniform_counts'])
    count_str = ', '.join(f'{c}x:{n}' for c, n in sorted(counts.items()))
    print(f'{section:<15} {u:>10} {m:>10} {ratio:>10.2f}   {count_str}')

# Interpretation
print('\n\nINTERPRETATION')
print('=' * 70)

total_uniform = len(uniform_folios)
total_mixed = len(mixed_folios)
uniform_ratio = total_uniform / (total_uniform + total_mixed) if (total_uniform + total_mixed) > 0 else 0

print(f"""
FOLIO UNIFORMITY:
- {total_uniform} folios have ALL entries with same repetition count
- {total_mixed} folios have VARIABLE repetition counts
- Uniformity ratio: {uniform_ratio:.1%}

WHAT THIS MEANS FOR RATIO HYPOTHESIS:

IF uniform folios = "all components have same proportion":
- This would be unusual for real recipes (usually different amounts)
- But could represent "standard formulations" or "base recipes"

IF uniform folios = "folio-level metadata":
- The repetition count might be a property of the FOLIO, not the ENTRY
- E.g., "this folio documents 3x preparations"

IF uniform folios = "batch size or scale":
- All entries on a folio represent same-scale preparations
- 2x = small batch, 3x = standard, 4x = large batch

KEY OBSERVATION:
The high uniformity ratio ({uniform_ratio:.1%}) suggests the repetition count
may be FOLIO-LEVEL rather than ENTRY-LEVEL property in many cases.

This is COMPATIBLE with ratio interpretation where:
- Mixed folios = recipes with varying component proportions
- Uniform folios = recipes with equal proportions OR batch-size markers
""")
