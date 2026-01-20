"""Investigate A tokens that never appear in B."""

import json
from collections import defaultdict, Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

# Load data
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
data = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 13:
            word = parts[0].strip('"').strip()
            folio = parts[2].strip('"') if len(parts) > 2 else ''
            language = parts[6].strip('"') if len(parts) > 6 else ''
            transcriber = parts[12].strip('"').strip()
            if transcriber == 'H' and word and folio:
                data.append({
                    'token': word.lower(),
                    'folio': folio,
                    'currier': language
                })

# Get vocabulary by system
a_tokens = set(d['token'] for d in data if d['currier'] == 'A')
b_tokens = set(d['token'] for d in data if d['currier'] == 'B')

a_only = a_tokens - b_tokens
b_only = b_tokens - a_tokens
shared = a_tokens & b_tokens

print("Vocabulary Distribution:")
print("=" * 50)
print(f"  A-only vocabulary: {len(a_only):5} tokens")
print(f"  B-only vocabulary: {len(b_only):5} tokens")
print(f"  Shared vocabulary: {len(shared):5} tokens")
print()

# Frequency of A-only tokens within A
a_token_freq = Counter(d['token'] for d in data if d['currier'] == 'A')

a_only_freqs = [a_token_freq[t] for t in a_only]
shared_freqs = [a_token_freq[t] for t in shared]

print("A-only token frequency distribution:")
print("=" * 50)
freq_dist = Counter(a_only_freqs)
for freq in sorted(freq_dist.keys())[:15]:
    count = freq_dist[freq]
    print(f"  Occurs {freq}x in A: {count} tokens")
if max(freq_dist.keys()) > 15:
    print(f"  ... up to {max(a_only_freqs)}x")

print()
print(f"A-only tokens: mean freq = {sum(a_only_freqs)/len(a_only_freqs):.2f}")
print(f"Shared tokens: mean freq = {sum(shared_freqs)/len(shared_freqs):.2f}")

# Most frequent A-only tokens
print()
print("Most frequent A-only tokens (top 20):")
print("=" * 50)
a_only_by_freq = sorted([(t, a_token_freq[t]) for t in a_only], key=lambda x: -x[1])
for token, freq in a_only_by_freq[:20]:
    print(f"  {token:20} : {freq:4}x")

# Check if A-only tokens have unusual morphology
print()
print("A-only tokens by length:")
print("=" * 50)
a_only_lengths = Counter(len(t) for t in a_only)
shared_lengths = Counter(len(t) for t in shared)
for length in sorted(set(a_only_lengths.keys()) | set(shared_lengths.keys())):
    a_pct = 100 * a_only_lengths.get(length, 0) / len(a_only) if len(a_only) > 0 else 0
    s_pct = 100 * shared_lengths.get(length, 0) / len(shared) if len(shared) > 0 else 0
    print(f"  Length {length:2}: A-only {a_pct:5.1f}%, Shared {s_pct:5.1f}%")
