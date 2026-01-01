"""Show translation statistics."""
import json
from pathlib import Path
import sys
sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

# Load dictionary
with open('dictionary.json') as f:
    d = json.load(f)

entries = len(d['entries'])

# Load corpus
corpus = load_corpus('data/transcriptions')
total_tokens = len(corpus.words)
unique_words = len(set(w.text for w in corpus.words))

print('TRANSLATION STATISTICS')
print('=' * 50)
print(f'Dictionary entries:        {entries}')
print(f'')
print(f'Full corpus:')
print(f'  Total word tokens:       {total_tokens:,}')
print(f'  Unique words:            {unique_words:,}')
print(f'  Dictionary coverage:     {entries}/{unique_words} ({100*entries/unique_words:.1f}%)')
print(f'')
print(f'If we apply our dictionary to the full corpus:')
translated = sum(1 for w in corpus.words if w.text in d['entries'])
print(f'  Words translated:        {translated:,}/{total_tokens:,} ({100*translated/total_tokens:.1f}%)')
