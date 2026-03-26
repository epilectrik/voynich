"""Find all tokens unique to f75r in Currier B."""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter

tx = Transcript()
morph = Morphology()

# Corpus-wide frequency
freq = Counter()
for t in tx.currier_b():
    freq[t.word] += 1

# f75r tokens with line numbers
f75r_by_word = {}
for t in tx.currier_b():
    if t.folio == 'f75r' and not t.is_label:
        if t.word not in f75r_by_word:
            f75r_by_word[t.word] = t.line

# Unique to f75r (appear exactly once in ALL of Currier B)
unique = [(w, f75r_by_word[w]) for w in f75r_by_word if freq[w] == 1]
unique.sort(key=lambda x: int(x[1]) if x[1].isdigit() else 0)

print(f'Tokens unique to f75r (freq=1 in all Currier B): {len(unique)}')
print(f'{"TOKEN":20s} {"LINE":>4s}  {"PREFIX":8s} {"MIDDLE":12s} {"SUFFIX":6s}')
print('-' * 60)
for w, line in unique:
    m = morph.extract(w)
    print(f'{w:20s} L{line:>3s}  {m.prefix or "-":8s} {m.middle or "?":12s} {m.suffix or "-":6s}')

# Also check: how many unique tokens do OTHER folios have?
print(f'\n--- For comparison: unique token counts per folio (top 15) ---')
folio_words = {}
for t in tx.currier_b():
    if not t.is_label:
        if t.folio not in folio_words:
            folio_words[t.folio] = set()
        folio_words[t.folio].add(t.word)

folio_unique = {}
for folio, words in folio_words.items():
    folio_unique[folio] = sum(1 for w in words if freq[w] == 1)

for folio, count in sorted(folio_unique.items(), key=lambda x: -x[1])[:15]:
    total = len(folio_words[folio])
    pct = 100 * count / total if total else 0
    print(f'  {folio:8s}: {count:3d} unique / {total:3d} total ({pct:.1f}%)')
