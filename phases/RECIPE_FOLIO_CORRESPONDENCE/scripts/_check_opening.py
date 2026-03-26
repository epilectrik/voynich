"""Show f75r opening lines and any rare/unusual tokens."""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter

tx = Transcript()
morph = Morphology()
freq = Counter(t.word for t in tx.currier_b())

print('=== f75r OPENING LINES (P1) ===')
for line_num in ['1', '2', '3', '4', '5']:
    tokens = [t for t in tx.currier_b()
              if t.folio == 'f75r' and t.line == line_num and not t.is_label]
    if not tokens:
        continue
    print(f'\n--- Line {line_num} ---')
    for t in tokens:
        m = morph.extract(t.word)
        flag = ''
        if freq[t.word] == 1:
            flag = ' *** UNIQUE'
        elif freq[t.word] <= 5:
            flag = ' * RARE'
        elif not m.prefix and len(t.word) > 2:
            flag = ' ? NO PREFIX'
        print(f'  {t.word:20s} pre={m.prefix or "-":6s} mid={m.middle or "?":10s} '
              f'suf={m.suffix or "-":6s} freq={freq[t.word]:5d}{flag}')

# Also check: is there a third unusual token anywhere on the folio?
print('\n\n=== ALL TOKENS WITH freq <= 3 (not just uniques) ===')
seen = set()
for t in tx.currier_b():
    if t.folio == 'f75r' and not t.is_label and freq[t.word] <= 3:
        if t.word not in seen:
            seen.add(t.word)
            m = morph.extract(t.word)
            has_prefix = bool(m.prefix)
            print(f'  L{t.line:>3s} {t.word:20s} pre={m.prefix or "-":6s} '
                  f'mid={m.middle or "?":10s} suf={m.suffix or "-":6s} '
                  f'freq={freq[t.word]}  parseable={has_prefix}')
