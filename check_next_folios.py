"""Check coverage on folios beyond our 100% set."""
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

# Check each folio
print("FOLIO COVERAGE ANALYSIS")
print("=" * 60)

folio_list = sorted(folios.keys())
for folio in folio_list[:20]:  # First 20 folios
    words = folios[folio]
    translated = sum(1 for w in words if w in entries)
    pct = 100 * translated / len(words) if words else 0
    status = "DONE" if pct == 100 else ""
    print(f"{folio}: {translated}/{len(words)} ({pct:.1f}%) {status}")

# Show untranslated words from next incomplete folio
print("\n" + "=" * 60)
print("UNTRANSLATED WORDS IN NEXT INCOMPLETE FOLIOS:")
print("=" * 60)

for folio in folio_list:
    words = folios[folio]
    untranslated = [w for w in words if w not in entries]
    if untranslated:
        unique_untranslated = list(dict.fromkeys(untranslated))  # preserve order, unique
        print(f"\n{folio} ({len(unique_untranslated)} unique untranslated):")
        # Show with frequency
        from collections import Counter
        freq = Counter(untranslated)
        for word in unique_untranslated[:30]:  # First 30
            print(f"  {word} ({freq[word]}x)")
        if len(unique_untranslated) > 30:
            print(f"  ... and {len(unique_untranslated) - 30} more")
        break  # Only show first incomplete folio
