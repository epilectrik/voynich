"""Which REGIMEs have exclusive A vocabulary?"""

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

# Load REGIME mapping
with open(project_root / 'results' / 'regime_folio_mapping.json', 'r') as f:
    regime_folios = json.load(f)
folio_to_regime = {}
for regime, folios in regime_folios.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# Get A vocabulary
a_tokens = set(d['token'] for d in data if d['currier'] == 'A')

# For each A token, find which REGIMEs it appears in
b_data = [d for d in data if d['currier'] == 'B']
token_regimes = defaultdict(set)
for d in b_data:
    regime = folio_to_regime.get(d['folio'])
    if regime:
        token_regimes[d['token']].add(regime)

# Find single-REGIME tokens and count by REGIME
single_regime_tokens = defaultdict(list)
for token in a_tokens:
    regimes = token_regimes.get(token, set())
    if len(regimes) == 1:
        regime = list(regimes)[0]
        single_regime_tokens[regime].append(token)

print("Single-REGIME A tokens by REGIME:")
print("=" * 50)
for regime in sorted(single_regime_tokens.keys()):
    tokens = single_regime_tokens[regime]
    print(f"  {regime}: {len(tokens)} exclusive tokens")

# Get frequency of these tokens in A
a_token_freq = Counter(d['token'] for d in data if d['currier'] == 'A')

print()
print("Examples of single-REGIME tokens (most frequent):")
print("=" * 50)
for regime in sorted(single_regime_tokens.keys()):
    print(f"\n{regime}:")
    tokens = single_regime_tokens[regime]
    by_freq = sorted([(t, a_token_freq[t]) for t in tokens], key=lambda x: -x[1])
    for token, freq in by_freq[:5]:
        print(f"    {token:20} : {freq:4}x in A")

# Also check: are these high-frequency or low-frequency tokens?
print()
print("Frequency distribution of single-REGIME tokens:")
print("=" * 50)
for regime in sorted(single_regime_tokens.keys()):
    tokens = single_regime_tokens[regime]
    freqs = [a_token_freq[t] for t in tokens]
    mean_freq = sum(freqs) / len(freqs) if freqs else 0
    hapax = sum(1 for f in freqs if f == 1)
    print(f"  {regime}: mean freq = {mean_freq:.2f}, hapax = {hapax}/{len(tokens)} ({100*hapax/len(tokens):.0f}%)")
