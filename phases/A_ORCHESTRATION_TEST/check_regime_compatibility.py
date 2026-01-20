"""Quick check: How many REGIMEs is each A token compatible with?"""

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
print(f"Total unique A tokens: {len(a_tokens)}")

# For each A token, find which REGIMEs it appears in (via B folios)
b_data = [d for d in data if d['currier'] == 'B']
token_regimes = defaultdict(set)
for d in b_data:
    regime = folio_to_regime.get(d['folio'])
    if regime:
        token_regimes[d['token']].add(regime)

# Count how many REGIMEs each A token is compatible with
regime_counts = Counter()
a_tokens_in_b = 0
for token in a_tokens:
    if token in token_regimes:
        a_tokens_in_b += 1
        n_regimes = len(token_regimes[token])
        regime_counts[n_regimes] += 1

print(f"A tokens that also appear in B: {a_tokens_in_b}")
print(f"A tokens with NO B presence: {len(a_tokens) - a_tokens_in_b}")

print("\nA tokens by number of compatible REGIMEs:")
print("=" * 50)
for n in sorted(regime_counts.keys()):
    count = regime_counts[n]
    pct = 100 * count / sum(regime_counts.values())
    print(f"  {n} REGIME(s): {count:5} tokens ({pct:5.1f}%)")

# Show which REGIME combinations are common for multi-REGIME tokens
print("\nREGIME combination patterns (tokens compatible with 2+ REGIMEs):")
print("=" * 50)
combo_counts = Counter()
for token in a_tokens:
    if token in token_regimes and len(token_regimes[token]) >= 2:
        combo = tuple(sorted(token_regimes[token]))
        combo_counts[combo] += 1

for combo, count in combo_counts.most_common(10):
    print(f"  {combo}: {count} tokens")
