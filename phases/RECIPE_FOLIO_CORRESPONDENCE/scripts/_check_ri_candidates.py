"""Look for potential material/RI tokens on f75r.
RI tokens should: parse poorly, appear rarely, cluster at specific positions,
and NOT follow standard operational grammar patterns."""
import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()

# Standard operational prefixes
KNOWN_PREFIXES = {'qo','ch','sh','da','sa','ok','ot','ol','so','po','ke','ko',
                  'pch','tch','dch','lch','lk','lsh','to','do','ar','al','or',
                  'ka','ta','te'}

# Get f75r text tokens
f75r = []
for t in tx.currier_b():
    if t.folio == 'f75r' and not t.is_label:
        f75r.append(t)

# Also get labels
f75r_labels = []
for t in tx.all():
    if t.folio == 'f75r' and t.is_label:
        f75r_labels.append(t)

# Get corpus-wide frequency for each word
corpus_freq = Counter()
for t in tx.currier_b():
    corpus_freq[t.word] += 1

print("=" * 70)
print("f75r TOKEN ANALYSIS: Looking for material/RI candidates")
print("=" * 70)

# 1. Tokens that parse poorly (no recognized prefix, unusual middle)
print("\n--- TOKENS WITH NO RECOGNIZED PREFIX ---")
no_prefix = []
for t in f75r:
    m = morph.extract(t.word)
    if m.prefix and m.prefix not in KNOWN_PREFIXES:
        if t.word not in [x[0] for x in no_prefix]:
            no_prefix.append((t.word, m.prefix, m.middle, m.suffix, t.line))
    elif not m.prefix and not m.articulator and len(t.word) > 2:
        if t.word not in [x[0] for x in no_prefix]:
            no_prefix.append((t.word, '(none)', m.middle, m.suffix, t.line))

for w, pre, mid, suf, line in sorted(set(no_prefix)):
    freq = corpus_freq[w]
    print(f"  {w:20s}  pre={pre:8s} mid={mid or '?':10s} suf={suf or '-':6s}  "
          f"corpus_freq={freq:4d}  line={line}")

# 2. Very rare tokens (appear 1-3 times in entire corpus) on f75r
print("\n--- RARE TOKENS (corpus freq <= 3) ---")
rare = []
for t in f75r:
    if corpus_freq[t.word] <= 3 and t.word not in [r[0] for r in rare]:
        m = morph.extract(t.word)
        rare.append((t.word, m.prefix or '-', m.middle or '?', m.suffix or '-',
                     corpus_freq[t.word], t.line))

for w, pre, mid, suf, freq, line in sorted(rare, key=lambda x: x[4]):
    print(f"  {w:20s}  pre={pre:6s} mid={mid:10s} suf={suf:6s}  "
          f"freq={freq}  line={line}")

# 3. Labels (these label the illustration - could name materials/apparatus)
print("\n--- LABELS (illustration annotations) ---")
label_lines = defaultdict(list)
for t in f75r_labels:
    label_lines[t.line].append(t.word)

for line in sorted(label_lines.keys(), key=lambda x: int(x) if x.isdigit() else 0):
    words = label_lines[line]
    label_text = ' '.join(words)
    # Parse each word
    parts = []
    for w in words:
        m = morph.extract(w)
        freq = corpus_freq.get(w, 0)
        # Also check frequency across ALL tokens (including labels, A, AZC)
        all_freq = sum(1 for t2 in tx.all() if t2.word == w)
        parts.append(f"{w}(B:{freq}/all:{all_freq})")
    print(f"  Label L{line}: {label_text}")
    print(f"    freqs: {', '.join(parts)}")
    for w in words:
        m = morph.extract(w)
        print(f"    {w:15s} -> pre={m.prefix or '-':6s} mid={m.middle or '?':8s} suf={m.suffix or '-':5s}")

# 4. Tokens near paragraph boundaries that could be material specs
print("\n--- PARAGRAPH-INITIAL SEQUENCES (first 3 tokens of each paragraph) ---")
# Build paragraph structure
lines_by_num = defaultdict(list)
for t in f75r:
    lines_by_num[int(t.line)].append(t)

gallows_lines = []
for line_num in sorted(lines_by_num.keys()):
    tokens = lines_by_num[line_num]
    if tokens and tokens[0].word[0] in 'tkpf':
        gallows_lines.append(line_num)

for gl in gallows_lines:
    tokens = lines_by_num[gl][:4]
    print(f"  L{gl}: {' '.join(t.word for t in tokens)}")
    for t in tokens:
        m = morph.extract(t.word)
        freq = corpus_freq[t.word]
        print(f"    {t.word:18s} pre={m.prefix or '-':6s} mid={m.middle or '?':8s} "
              f"suf={m.suffix or '-':5s} freq={freq}")

# 5. Tokens with unusual letter combinations (potential RI markers)
print("\n--- TOKENS WITH UNUSUAL STRUCTURE ---")
unusual = []
for t in f75r:
    w = t.word
    # Check for double consonants, unusual bigrams, etc.
    has_double_sh = 'ssh' in w or 'cch' in w
    has_q_not_qo = 'q' in w and 'qo' not in w and w[0] != 'q'
    has_consecutive_rare = any(bg in w for bg in ['mp','mb','nk','ng','tz','zz','ck'])

    if (has_q_not_qo or has_double_sh) and w not in [u[0] for u in unusual]:
        m = morph.extract(w)
        unusual.append((w, m.prefix or '-', m.middle or '?', m.suffix or '-',
                       corpus_freq[w], t.line))

if unusual:
    for w, pre, mid, suf, freq, line in sorted(set(unusual)):
        print(f"  {w:20s}  pre={pre:6s} mid={mid:10s} suf={suf:6s}  "
              f"freq={freq}  line={line}")
