"""Analyze daiin usage patterns in Currier A - CORRECTED COLUMN INDICES."""
from pathlib import Path
from collections import Counter, defaultdict

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Correct column indices based on header:
# "word"(0) "complex_word"(1) "folio"(2) "section"(3) "quire"(4) "panel"(5)
# "language"(6) "hand"(7) "misc"(8) "d.hand"(9) "placement"(10) "line_number"(11) "transcriber"(12)

lines_data = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            # Filter to PRIMARY transcriber (H) only
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip()
            section = parts[3].strip('"').strip()
            lang = parts[6].strip('"').strip()
            line_num = parts[11].strip('"').strip()

            if lang == 'A' and word:
                key = f'{folio}_{line_num}'
                lines_data[key].append({
                    'word': word,
                    'folio': folio,
                    'section': section,
                    'line': line_num
                })

# Group tokens by line
line_tokens = {}
for key, entries in lines_data.items():
    tokens = [e['word'] for e in entries]
    line_tokens[key] = {
        'tokens': tokens,
        'folio': entries[0]['folio'],
        'section': entries[0]['section'],
        'line': entries[0]['line']
    }

print(f"Total Currier A lines: {len(line_tokens)}")
print()

# Find lines containing daiin
daiin_lines = {k: v for k, v in line_tokens.items() if 'daiin' in v['tokens']}
print(f"Lines containing daiin: {len(daiin_lines)}")

# Analyze daiin patterns
pure_daiin = 0
daiin_with_others = 0
other_tokens = Counter()

for key, data in daiin_lines.items():
    tokens = data['tokens']
    non_daiin = [t for t in tokens if t != 'daiin']
    if len(non_daiin) == 0:
        pure_daiin += 1
    else:
        daiin_with_others += 1
        for t in non_daiin:
            other_tokens[t] += 1

print(f"\nLines with ONLY daiin: {pure_daiin} ({100*pure_daiin/len(daiin_lines):.1f}%)")
print(f"Lines with daiin + others: {daiin_with_others} ({100*daiin_with_others/len(daiin_lines):.1f}%)")

print(f"\nTop 20 tokens appearing WITH daiin:")
for tok, ct in other_tokens.most_common(20):
    print(f"  {tok}: {ct}")

# daiin count distribution
print("\n" + "=" * 60)
print("DAIIN REPETITION COUNTS")
print("=" * 60)
daiin_counts = Counter()
for key, data in daiin_lines.items():
    ct = data['tokens'].count('daiin')
    daiin_counts[ct] += 1

print("\nDistribution of daiin count per line:")
for ct in sorted(daiin_counts.keys())[:20]:
    print(f"  {ct}x daiin: {daiin_counts[ct]} lines")
if len(daiin_counts) > 20:
    print(f"  ... (max = {max(daiin_counts.keys())}x)")

# Show some example lines
print("\n" + "=" * 60)
print("EXAMPLE LINES CONTAINING DAIIN")
print("=" * 60)

examples = list(daiin_lines.items())[:15]
for key, data in examples:
    tokens = data['tokens']
    daiin_ct = tokens.count('daiin')
    other = [t for t in tokens if t != 'daiin']
    print(f"\n{data['folio']} line {data['line']} [{data['section']}]:")
    print(f"  daiin x{daiin_ct}")
    if other:
        print(f"  other: {' '.join(other[:10])}{'...' if len(other) > 10 else ''}")

# Check if daiin appears in repeated sequences or mixed
print("\n" + "=" * 60)
print("DAIIN PATTERN ANALYSIS")
print("=" * 60)

consecutive_daiin = 0
scattered_daiin = 0

for key, data in daiin_lines.items():
    tokens = data['tokens']
    # Check if all daiins are consecutive
    daiin_indices = [i for i, t in enumerate(tokens) if t == 'daiin']
    if len(daiin_indices) > 1:
        is_consecutive = all(daiin_indices[i+1] - daiin_indices[i] == 1
                            for i in range(len(daiin_indices)-1))
        if is_consecutive:
            consecutive_daiin += 1
        else:
            scattered_daiin += 1

print(f"Lines where daiin tokens are consecutive: {consecutive_daiin}")
print(f"Lines where daiin tokens are scattered: {scattered_daiin}")

# Look at position of daiin within lines
print("\n" + "=" * 60)
print("POSITION OF DAIIN WITHIN LINES")
print("=" * 60)

position_start = 0  # daiin at start
position_end = 0    # daiin at end
position_middle = 0 # daiin in middle only

for key, data in daiin_lines.items():
    tokens = data['tokens']
    if tokens[0] == 'daiin':
        position_start += 1
    if tokens[-1] == 'daiin':
        position_end += 1
    if tokens[0] != 'daiin' and tokens[-1] != 'daiin':
        position_middle += 1

print(f"Lines starting with daiin: {position_start} ({100*position_start/len(daiin_lines):.1f}%)")
print(f"Lines ending with daiin: {position_end} ({100*position_end/len(daiin_lines):.1f}%)")
print(f"Lines with daiin only in middle: {position_middle} ({100*position_middle/len(daiin_lines):.1f}%)")
