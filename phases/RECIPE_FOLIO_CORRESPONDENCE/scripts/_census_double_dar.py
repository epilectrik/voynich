"""Double-dar corpus census: find all consecutive identical token runs
starting with 'dar' across all Currier B folios. Also census all
consecutive identical token pairs (any word) to contextualize."""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()

# ============================================================
# 1. Build per-folio, per-line token lists
# ============================================================
folio_line_tokens = defaultdict(lambda: defaultdict(list))
for t in tx.currier_b():
    folio_line_tokens[t.folio][t.line].append(t.word)

# ============================================================
# 2. Find ALL consecutive identical token runs (any word)
# ============================================================
# A "run" is N consecutive identical tokens within a single line

all_runs = []  # (folio, line, word, run_length, position_in_line)

for folio in sorted(folio_line_tokens):
    for line in sorted(folio_line_tokens[folio], key=lambda x: (int(x) if x.isdigit() else 0)):
        words = folio_line_tokens[folio][line]
        if len(words) < 2:
            continue
        i = 0
        while i < len(words):
            run_len = 1
            while i + run_len < len(words) and words[i + run_len] == words[i]:
                run_len += 1
            if run_len >= 2:
                all_runs.append((folio, line, words[i], run_len, i))
            i += run_len

# ============================================================
# 3. Summarize run-length distribution
# ============================================================
print("=" * 70)
print("CONSECUTIVE IDENTICAL TOKEN RUNS IN CURRIER B")
print("=" * 70)

run_by_length = defaultdict(list)
for folio, line, word, rlen, pos in all_runs:
    run_by_length[rlen].append((folio, line, word, pos))

for rlen in sorted(run_by_length):
    entries = run_by_length[rlen]
    print(f"\n  Run length {rlen}: {len(entries)} occurrences")
    if rlen >= 3:
        for folio, line, word, pos in entries:
            print(f"    {folio} L{line} pos={pos}: '{word}' x{rlen}")
    elif rlen == 2:
        # Show first 20 and summarize
        word_counts = Counter(word for _, _, word, _ in entries)
        print(f"    Most common doubled words:")
        for word, cnt in word_counts.most_common(15):
            print(f"      '{word}' x2: {cnt} times")

# ============================================================
# 4. Focus on 'dar' specifically
# ============================================================
print("\n" + "=" * 70)
print("'dar' CONSECUTIVE RUNS")
print("=" * 70)

dar_runs = [(f, l, w, r, p) for f, l, w, r, p in all_runs if w == 'dar']
if dar_runs:
    for folio, line, word, rlen, pos in dar_runs:
        context = folio_line_tokens[folio][line]
        print(f"\n  {folio} L{line}: '{word}' x{rlen} at position {pos}")
        print(f"    Full line: {' '.join(context)}")
else:
    print("  No consecutive 'dar' runs found in Currier B!")

# Also check: where does 'dar' appear at all?
print("\n" + "=" * 70)
print("'dar' OCCURRENCES BY FOLIO")
print("=" * 70)

dar_folios = defaultdict(list)
for folio in sorted(folio_line_tokens):
    for line in sorted(folio_line_tokens[folio], key=lambda x: (int(x) if x.isdigit() else 0)):
        words = folio_line_tokens[folio][line]
        for i, w in enumerate(words):
            if w == 'dar':
                dar_folios[folio].append((line, i, words))

total_dar = sum(len(v) for v in dar_folios.values())
print(f"\nTotal 'dar' tokens in Currier B: {total_dar}")
print(f"Folios with 'dar': {len(dar_folios)}")

for folio in sorted(dar_folios):
    entries = dar_folios[folio]
    print(f"\n  {folio}: {len(entries)} occurrences")
    for line, pos, words in entries:
        # Show context: 2 words before and after
        start = max(0, pos - 2)
        end = min(len(words), pos + 3)
        context = words[start:end]
        marker_pos = pos - start
        context_str = ' '.join(
            f'[{w}]' if i == marker_pos else w
            for i, w in enumerate(context)
        )
        print(f"    L{line} pos={pos}: ...{context_str}...")

# ============================================================
# 5. Paragraph-initial analysis
# ============================================================
print("\n" + "=" * 70)
print("PARAGRAPH-INITIAL 'dar' (first 3 tokens of line 1 of each paragraph)")
print("=" * 70)

# Paragraphs start at lines that follow a gap or are line 1
# We approximate: line 1 of each folio + any line where previous line
# number is not consecutive
para_initial_dar = []
for folio in sorted(folio_line_tokens):
    lines = sorted(folio_line_tokens[folio].keys(),
                   key=lambda x: (int(x) if x.isdigit() else 0))
    for idx, line in enumerate(lines):
        line_num = int(line) if line.isdigit() else 0
        is_para_start = False
        if idx == 0:
            is_para_start = True
        else:
            prev_num = int(lines[idx-1]) if lines[idx-1].isdigit() else 0
            if line_num - prev_num > 1:
                is_para_start = True  # gap in line numbers = new paragraph

        if is_para_start:
            words = folio_line_tokens[folio][line]
            for i, w in enumerate(words[:5]):  # check first 5 tokens
                if w == 'dar':
                    para_initial_dar.append((folio, line, i, words[:8]))

print(f"\nParagraph-initial 'dar' occurrences: {len(para_initial_dar)}")
for folio, line, pos, context in para_initial_dar:
    print(f"  {folio} L{line} pos={pos}: {' '.join(context)}")

# Check for double-dar at paragraph starts
print("\n--- Double-dar at paragraph starts ---")
for folio, line, pos, context in para_initial_dar:
    if pos + 1 < len(context) and context[pos + 1] == 'dar':
        print(f"  {folio} L{line}: DOUBLE DAR at pos {pos}-{pos+1}: {' '.join(context)}")

# ============================================================
# 6. Uniqueness of doubled tokens per folio
# ============================================================
print("\n" + "=" * 70)
print("DOUBLED TOKENS (x2) PER FOLIO - TOP FOLIOS")
print("=" * 70)

folio_doubles = defaultdict(list)
for folio, line, word, rlen, pos in all_runs:
    if rlen == 2:
        folio_doubles[folio].append((line, word))

folio_double_counts = {f: len(v) for f, v in folio_doubles.items()}
for folio, count in sorted(folio_double_counts.items(), key=lambda x: -x[1])[:20]:
    words = Counter(w for _, w in folio_doubles[folio])
    top = ', '.join(f'{w}x{c}' for w, c in words.most_common(5))
    print(f"  {folio:8s}: {count:3d} doubled pairs  ({top})")

# Where does f75r rank?
f75r_count = folio_double_counts.get('f75r', 0)
rank = sum(1 for c in folio_double_counts.values() if c >= f75r_count)
total_folios = len(set(t.folio for t in tx.currier_b()))
print(f"\n  f75r: {f75r_count} doubled pairs (rank {rank}/{len(folio_double_counts)})")
