"""Find the last remaining untranslated words."""
import json
import sys
sys.path.insert(0, '.')
from collections import Counter
from tools.parser.voynich_parser import load_corpus

with open('dictionary.json') as f:
    d = json.load(f)
entries = d['entries']

corpus = load_corpus('data/transcriptions')

missing = [w.text for w in corpus.words if w.text not in entries]
freq = Counter(missing)

print(f"REMAINING UNTRANSLATED WORDS: {len(freq)} unique, {len(missing)} total tokens")
print("=" * 60)
for word, count in freq.most_common():
    print(f"  {word}: {count}x")
