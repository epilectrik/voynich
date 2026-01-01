"""Check coverage on botanical section folios (f1-f57)."""
import json
import sys
sys.path.insert(0, '.')
from tools.parser.voynich_parser import load_corpus

with open('dictionary.json') as f:
    d = json.load(f)
entries = d['entries']

corpus = load_corpus('data/transcriptions')

# Group by folio
folios = {}
for w in corpus.words:
    if w.folio not in folios:
        folios[w.folio] = []
    folios[w.folio].append(w.text)

# Natural sort for folios
import re
def folio_sort_key(f):
    # Extract number and suffix
    m = re.match(r'f(\d+)([rv]?)(\d*)', f)
    if m:
        return (int(m.group(1)), m.group(2), m.group(3))
    return (999, f, '')

folio_list = sorted(folios.keys(), key=folio_sort_key)

print("BOTANICAL SECTION COVERAGE (f1-f57)")
print("=" * 60)

total_words = 0
total_translated = 0
incomplete = []

for folio in folio_list:
    # Only botanical section
    m = re.match(r'f(\d+)', folio)
    if m and int(m.group(1)) <= 57:
        words = folios[folio]
        translated = sum(1 for w in words if w in entries)
        pct = 100 * translated / len(words) if words else 0
        total_words += len(words)
        total_translated += translated
        status = "COMPLETE" if pct == 100 else ""
        print(f"{folio}: {translated}/{len(words)} ({pct:.1f}%) {status}")
        if pct < 100:
            incomplete.append((folio, words, pct))

print("\n" + "=" * 60)
print(f"BOTANICAL SECTION TOTAL: {total_translated}/{total_words} ({100*total_translated/total_words:.1f}%)")
print("=" * 60)

# Show untranslated from first few incomplete folios
print("\nUNTRANSLATED WORDS (first 3 incomplete folios):")
for folio, words, pct in incomplete[:3]:
    untranslated = [w for w in words if w not in entries]
    unique = list(dict.fromkeys(untranslated))
    from collections import Counter
    freq = Counter(untranslated)
    print(f"\n{folio} ({len(unique)} unique, {100-pct:.1f}% missing):")
    for word in unique[:15]:
        print(f"  {word} ({freq[word]}x)")
