"""Show HT tokens on f75r with surrounding line context."""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Get ALL f75r tokens with positions
tokens = []
for t in tx.currier_b():
    if t.folio == 'f75r' and not t.is_label:
        m = morph.extract(t.word)
        tokens.append((t.line, t.word, m.has_articulator, m.articulator or '-',
                       m.prefix or '-', m.middle or '?', m.suffix or '-'))

# Find which lines have HT tokens
ht_lines = set()
for line, word, is_ht, art, pre, mid, suf in tokens:
    if is_ht:
        ht_lines.add(line)

print('=== HT TOKENS ON f75r WITH LINE CONTEXT ===')
print()
for line in sorted(ht_lines, key=lambda x: int(x) if x.isdigit() else 0):
    print(f'--- Line {line} ---')
    for ln, word, is_ht, art, pre, mid, suf in tokens:
        if ln == line:
            marker = ' <<< HT' if is_ht else ''
            print(f'  {word:20s} art={art:4s} pre={pre:6s} mid={mid:10s} suf={suf:6s}{marker}')
    print()

# Summary
print('=== HT TOKEN SUMMARY ===')
total = len(tokens)
ht_count = sum(1 for _, _, is_ht, _, _, _, _ in tokens if is_ht)
print(f'Total tokens: {total}')
print(f'HT tokens: {ht_count} ({100*ht_count/total:.1f}%)')
print()

# Show just the HT tokens with their position in the paragraph
print('=== HT TOKEN POSITIONS ===')
# Build paragraph map (gallows-initial lines start new paragraphs)
lines_by_num = {}
for ln, word, is_ht, art, pre, mid, suf in tokens:
    n = int(ln) if ln.isdigit() else 0
    if n not in lines_by_num:
        lines_by_num[n] = []
    lines_by_num[n].append((word, is_ht, art, pre, mid, suf))

para_num = 0
para_map = {}
for n in sorted(lines_by_num.keys()):
    first_word = lines_by_num[n][0][0] if lines_by_num[n] else ''
    if first_word and first_word[0] in 'tkpf':
        para_num += 1
    para_map[n] = para_num

for ln, word, is_ht, art, pre, mid, suf in tokens:
    if is_ht:
        n = int(ln) if ln.isdigit() else 0
        pos_in_line = [i for i, (w, _, _, _, _, _) in enumerate(lines_by_num[n]) if w == word]
        para = para_map.get(n, '?')
        print(f'  P{para} L{ln:>3s} pos={pos_in_line}  {word:20s}  art={art}  base={word.lstrip("sdpfy")}')
