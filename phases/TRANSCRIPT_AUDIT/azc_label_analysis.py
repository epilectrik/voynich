"""
AZC LABEL ANALYSIS

What are the 68 label tokens in AZC? Do they affect our analyses?
"""

import os
from collections import Counter

os.chdir('C:/git/voynich')

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Get H-only AZC labels
labels = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if (row.get('transcriber', '').strip() == 'H' and
            row.get('language', '') == 'NA' and
            row.get('placement', '').startswith('L')):
            labels.append(row)

print(f"Total AZC labels (H-only): {len(labels)}")

# What words are they?
print("\n[1] Label tokens:")
word_counts = Counter(row['word'] for row in labels)
for word, count in word_counts.most_common(20):
    print(f"    '{word}': {count}")

# Which folios?
print("\n[2] Label folios:")
folio_counts = Counter(row['folio'] for row in labels)
for folio, count in sorted(folio_counts.items()):
    print(f"    {folio}: {count}")

# Compare label vocabulary to main AZC vocabulary
print("\n[3] Vocabulary comparison:")

# Main AZC (non-label)
main_azc = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        if (row.get('transcriber', '').strip() == 'H' and
            row.get('language', '') == 'NA' and
            not row.get('placement', '').startswith('L')):
            main_azc.append(row)

label_vocab = set(row['word'] for row in labels)
main_vocab = set(row['word'] for row in main_azc)

shared = label_vocab & main_vocab
label_only = label_vocab - main_vocab

print(f"    Label vocabulary: {len(label_vocab)}")
print(f"    Main AZC vocabulary: {len(main_vocab)}")
print(f"    Shared: {len(shared)}")
print(f"    Label-only words: {len(label_only)}")

if label_only:
    print(f"    Label-only tokens: {sorted(label_only)}")

# Impact assessment
print("\n[4] Impact assessment:")
print(f"    Labels are {100*len(labels)/(len(labels)+len(main_azc)):.1f}% of H-only AZC")
print(f"    Label-only vocabulary: {len(label_only)} words")
if len(label_only) == 0:
    print("    -> Labels use same vocabulary as main AZC text")
    print("    -> Impact likely MINIMAL - vocabulary overlap is complete")
else:
    print(f"    -> WARNING: {len(label_only)} label-specific words may affect analyses")
