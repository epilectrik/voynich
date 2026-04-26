"""
Phase 650 Step 4: Line-window closed-cycle test (corrected granularity).

User correction confirmed: the f75r 10-cycle anchor is at L36-L38 (3 lines)
within a larger 17-cycle paragraph. The right unit is the operational block
= consecutive lines, not the whole paragraph.

Method:
1. Compute closed-cycle (qok+...+dy) count per LINE
2. For each matched folio, find the line-window (1-5 consecutive lines)
   with the closed-cycle count matching the recipe's iteration count (or n+1
   accounting for initial distillation)
3. Compare match-quality across the matched corpus
"""
import sys
import json
import re
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript
from collections import defaultdict, Counter

tx = Transcript()

with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as fp:
    matches = json.load(fp)
with open('phases/SISMEL_RECIPE_CORPUS/results/sismel_corpus.json', encoding='utf-8') as fp:
    corpus = json.load(fp)

def get_chapter(part, num):
    for ch in corpus['parts'][part]['chapters']:
        if ch['chapter_num'] == num:
            return ch
    return None

ROMAN_VALUES = {'i': 1, 'v': 5, 'x': 10, 'l': 50}
def parse_roman(s):
    s = s.lower()
    if not all(c in ROMAN_VALUES for c in s): return None
    total, prev = 0, 0
    for c in reversed(s):
        v = ROMAN_VALUES[c]
        total -= v if v < prev else -v
        prev = v
    return total if total > 0 else None

CATALAN_NUMBERS = {'una': 1, 'un': 1, 'dues': 2, 'dos': 2, 'tres': 3, 'quatre': 4,
                   'cinch': 5, 'cinc': 5, 'sis': 6, 'set': 7, 'vuyt': 8, 'vuit': 8,
                   'nou': 9, 'deu': 10}
ITER_RE = re.compile(
    r'(?:per\s+)?(\.[ivxIVX]+\.?|[a-zçé]+)\s+(?:vegades|vices|vegada|vice|reitera)',
    re.IGNORECASE)

def extract_iteration_counts(text):
    if not text: return []
    out = []
    for m in ITER_RE.finditer(text):
        token = m.group(1).strip('.').lower()
        n = parse_roman(token) or CATALAN_NUMBERS.get(token)
        if n and 2 <= n <= 50: out.append(n)
    return out

def is_closed_cycle(w):
    return w.startswith('qok') and w.endswith('dy')

# Per-line closed-cycle count
line_closed = defaultdict(int)
folio_lines = defaultdict(list)
for t in tx.currier_b():
    line_closed[(t.folio, t.line)] += 1 if is_closed_cycle(t.word) else 0
for (f, ln), c in line_closed.items():
    folio_lines[f].append((ln, c))

def line_num(ln):
    """Convert line label to int for sorting."""
    s = re.sub(r'[^0-9]', '', str(ln))
    return int(s) if s else 0

def best_window_match(line_counts, target):
    """Find the consecutive-line window where total closed-cycles = target.
    Returns (start_line, end_line, count) or None."""
    sorted_lines = sorted(line_counts, key=lambda x: line_num(x[0]))
    n = len(sorted_lines)
    best = None
    for i in range(n):
        cum = 0
        for j in range(i, min(i + 6, n)):  # up to 5-line windows
            cum += sorted_lines[j][1]
            if cum == target:
                window_size = j - i + 1
                if best is None or window_size < best[3]:
                    best = (sorted_lines[i][0], sorted_lines[j][0], cum, window_size)
            if cum > target:
                break
    return best

# Corpus-wide: how rare are exact target counts in 1-5 line windows?
def all_window_counts(line_counts, max_window=5):
    """Yield all (window_size, count) tuples."""
    sorted_lines = sorted(line_counts, key=lambda x: line_num(x[0]))
    n = len(sorted_lines)
    for i in range(n):
        cum = 0
        for j in range(i, min(i + max_window, n)):
            cum += sorted_lines[j][1]
            yield (j - i + 1, cum)

corpus_window_counts = Counter()
for f, line_counts in folio_lines.items():
    for sz, cnt in all_window_counts(line_counts, max_window=5):
        if cnt > 0:
            corpus_window_counts[(sz, cnt)] += 1

print("="*78)
print("LINE-WINDOW CLOSED-CYCLE TEST")
print("="*78)
print()
print("Hypothesis: 'redistill x N vegades' encodes as N+1 closed cycles")
print("            within a small (1-5 line) operational block")
print()

results = []
for m in matches:
    f = m['folio']
    if f not in folio_lines: continue
    ch = get_chapter(m['part'], m['chapter_num'])
    if not ch: continue
    counts = []
    for p_idx, p in enumerate(ch.get('paragraphs', [])):
        text = (p.get('catalan') or '') + ' ' + (p.get('latin') or '')
        for n in extract_iteration_counts(text):
            counts.append(n)
    if not counts: continue

    print(f"--- {f}  [{m['tier']}]  {m['recipe_label']}")
    line_counts = folio_lines[f]
    sorted_line = sorted(line_counts, key=lambda x: line_num(x[0]))
    nonzero = [(ln, c) for ln, c in sorted_line if c > 0]
    print(f"    Lines with closed cycles (>0): {[(str(ln), c) for ln, c in nonzero[:8]]}{'...' if len(nonzero) > 8 else ''}")

    for n in counts:
        for target in (n+1, n):  # try both interpretations
            best = best_window_match(line_counts, target)
            label = f"{target}=n+1" if target == n+1 else f"{target}=n"
            # Corpus-wide rarity
            rarity_1line = corpus_window_counts.get((1, target), 0)
            rarity_2line = corpus_window_counts.get((2, target), 0)
            rarity_3line = corpus_window_counts.get((3, target), 0)
            if best:
                start, end, cnt, sz = best
                print(f"    [x{n} -> target {label}]: MATCH at L{start}-L{end} ({sz}-line window, {cnt} cycles)")
                print(f"      corpus rarity at this window size: ~{[rarity_1line, rarity_2line, rarity_3line][min(sz,3)-1]} other folio-windows of that size with same count")
            else:
                print(f"    [x{n} -> target {label}]: NO MATCH in any 1-5 line window")

        results.append({
            'folio': f, 'recipe_count': n,
            'best_n_plus_1': best_window_match(line_counts, n+1),
            'best_n': best_window_match(line_counts, n),
        })
    print()

# Save
import os
os.makedirs('phases/PHASE_650_CYCLE_COUNTING_IDIOM/results', exist_ok=True)
with open('phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/line_window_closed_cycles.json', 'w') as f:
    json.dump({'results': results, 'corpus_window_distribution':
               {f"{k[0]}line_{k[1]}cycles": v for k, v in corpus_window_counts.items()}},
              f, indent=2, default=str)
print("Saved: phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/line_window_closed_cycles.json")
