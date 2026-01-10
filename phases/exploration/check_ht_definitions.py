"""Check different HT definitions for the 5.4x enrichment claim."""

import csv
from collections import Counter
from pathlib import Path

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# Load Currier B Herbal transcription
data = []
with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t', quotechar='"')
    for row in reader:
        if row.get('transcriber') != 'H':
            continue
        if row.get('language') != 'B':
            continue
        token = row.get('word', '')
        if not token or '*' in token:
            continue
        data.append(token.lower())

print(f'Total tokens: {len(data)}')

# Test various HT definitions
def test_definition(name, is_ht):
    ht_count = sum(1 for t in data if is_ht(t))
    ht_rate = ht_count / len(data)

    # Count HT-HT pairs
    ht_ht = sum(1 for i in range(len(data)-1) if is_ht(data[i]) and is_ht(data[i+1]))
    total_pairs = len(data) - 1
    expected = ht_rate * ht_rate * total_pairs
    enrichment = ht_ht / expected if expected > 0 else 0

    observed_rate = ht_ht / total_pairs * 100
    expected_rate = expected / total_pairs * 100

    print(f'\n{name}:')
    print(f'  HT tokens: {ht_count} ({ht_rate*100:.1f}%)')
    print(f'  Observed HT-HT: {ht_ht} ({observed_rate:.2f}%)')
    print(f'  Expected HT-HT: {expected:.1f} ({expected_rate:.2f}%)')
    print(f'  Enrichment: {enrichment:.2f}x')
    return enrichment

# Test definitions
test_definition('y-initial OR single y/f/d/r',
                lambda t: t.startswith('y') or t in {'y','f','d','r'})

test_definition('y-initial only',
                lambda t: t.startswith('y'))

test_definition('single chars y/f/d/r',
                lambda t: t in {'y','f','d','r'})

test_definition('y-initial + any single char',
                lambda t: t.startswith('y') or len(t) == 1)

test_definition('any y-containing token',
                lambda t: 'y' in t)

# Check the grammar file for "real" HT definition
import json
GRAMMAR = BASE / "results" / "canonical_grammar.json"
if GRAMMAR.exists():
    with open(GRAMMAR, 'r', encoding='utf-8') as f:
        grammar_data = json.load(f)

    grammar_tokens = set()
    terminals = grammar_data.get('terminals', {}).get('list', [])
    for term in terminals:
        grammar_tokens.add(term['symbol'].lower())

    print(f'\n\nGrammar tokens loaded: {len(grammar_tokens)}')

    # Test "not in grammar" definition
    test_definition('NOT in 479 grammar tokens',
                    lambda t: t not in grammar_tokens)
