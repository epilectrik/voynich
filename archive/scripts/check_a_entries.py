"""Quick check of Currier A entry counts."""
from collections import defaultdict

entries = defaultdict(list)
with open('data/transcriptions/interlinear_full_words.txt', 'r') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 12:
            word = parts[0].strip('"')
            folio = parts[2].strip('"')
            language = parts[6].strip('"')
            line_num = parts[11].strip('"')
            if language == 'A':
                key = f'{folio}_{line_num}'
                entries[key].append(word)

print(f'Total Currier A entries (lines): {len(entries)}')

folio_counts = defaultdict(int)
for key in entries:
    folio = key.split('_')[0]
    folio_counts[folio] += 1

print(f'Folios with A entries: {len(folio_counts)}')
print(f'Mean entries per folio: {sum(folio_counts.values())/len(folio_counts):.1f}')
print(f'Max entries per folio: {max(folio_counts.values())}')

# Show distribution
print("\nSample folios:")
for folio in sorted(folio_counts.keys())[:5]:
    print(f'  {folio}: {folio_counts[folio]} entries')
