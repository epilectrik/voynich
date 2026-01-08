"""Check token coverage between Grammar and transcription."""
from vee.app.core.grammar import Grammar
from collections import Counter

# Load grammar
g = Grammar()
known = set(g._by_symbol.keys())
print(f'Known tokens in grammar: {len(known)}')

# Load transcription and count
with open('data/transcriptions/interlinear_full_words.txt', 'r') as f:
    lines = f.readlines()[1:]  # skip header

total_occurrences = 0
known_occurrences = 0
unknown_types = Counter()

for line in lines:
    parts = line.strip().split('\t')
    if parts:
        token = parts[0].strip('"').lower()
        if token:
            total_occurrences += 1
            if token in known:
                known_occurrences += 1
            else:
                unknown_types[token] += 1

print(f'Total token occurrences: {total_occurrences}')
print(f'Known token occurrences: {known_occurrences} ({100*known_occurrences/total_occurrences:.1f}%)')
print(f'Unknown unique types: {len(unknown_types)}')
print(f'\nTop 20 unknown tokens by frequency:')
for tok, cnt in unknown_types.most_common(20):
    print(f'  {tok}: {cnt}')
