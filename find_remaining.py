"""Find remaining untranslated words in f5r and f6r-f10v."""
import json
import sys
sys.path.insert(0, '.')
from pathlib import Path
from tools.parser.voynich_parser import load_corpus
from collections import Counter
import re

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    d = json.load(f)
entries = d['entries']

corpus = load_corpus('data/transcriptions')

# Group by folio
folios = {}
for w in corpus.words:
    if w.folio not in folios:
        folios[w.folio] = []
    folios[w.folio].append(w.text)

def folio_sort_key(f):
    m = re.match(r'f(\d+)([rv]?)(\d*)', f)
    if m:
        return (int(m.group(1)), m.group(2), m.group(3))
    return (999, f, '')

folio_list = sorted(folios.keys(), key=folio_sort_key)

# Check f5r-f10v
print("REMAINING WORDS FOR f5r-f10v")
print("=" * 60)

for folio in folio_list:
    m = re.match(r'f(\d+)', folio)
    if m and 5 <= int(m.group(1)) <= 10:
        words = folios[folio]
        untranslated = [w for w in words if w not in entries]
        if untranslated:
            unique = list(dict.fromkeys(untranslated))
            freq = Counter(untranslated)
            total = len(words)
            done = total - len(untranslated)
            print(f"\n{folio} ({done}/{total} = {100*done/total:.1f}%)")
            print(f"Missing {len(unique)} unique words:")
            for w in unique[:20]:
                print(f"  {w} ({freq[w]}x)")
            if len(unique) > 20:
                print(f"  ... and {len(unique)-20} more")
