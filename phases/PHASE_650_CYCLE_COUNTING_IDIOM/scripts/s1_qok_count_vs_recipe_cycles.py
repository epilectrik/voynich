"""
Phase 650 Step 1: Test the cycle-counting idiom.

Hypothesis (per user reasoning + f75r anchors):
- The Voynich grammar encodes cyclic-operation counts via repetition of
  qok-class tokens (qo+k = fire-application + heat HEAD).
- One qok-class token = one fire-restart = one operational cycle.
- Where a recipe specifies "do this N times," we should see N qok-class
  tokens at or near the line where the cycle is described.

Test on all matched recipes:
1. Extract explicit cycle counts from Catalan/Latin recipe text
   (Roman numerals like .iii., .ix.; Catalan number words like 'tres', 'nou')
2. For each match, count qok* tokens in the corresponding Voynich folio
   per-paragraph and per-line
3. Identify any line/paragraph with a qok-cluster matching the recipe count
4. Report: did the explicit-count recipe encode the count via qok-cluster?

Falsification:
- If multiple recipes have explicit counts and NO qok-cluster matches,
  the cycle-counting idiom doesn't generalize — f75r is sui generis
- If most explicit-count recipes have matching qok-clusters,
  the idiom is real and registerable
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

with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as f:
    matches = json.load(f)
with open('phases/SISMEL_RECIPE_CORPUS/results/sismel_corpus.json', encoding='utf-8') as fp:
    corpus = json.load(fp)

def get_chapter(part, num):
    for ch in corpus['parts'][part]['chapters']:
        if ch['chapter_num'] == num:
            return ch
    return None

# Extract explicit cycle counts from text
ROMAN_VALUES = {'i': 1, 'v': 5, 'x': 10, 'l': 50}
def parse_roman(s):
    s = s.lower()
    if not all(c in ROMAN_VALUES for c in s):
        return None
    total = 0
    prev = 0
    for c in reversed(s):
        v = ROMAN_VALUES[c]
        if v < prev:
            total -= v
        else:
            total += v
        prev = v
    return total if total > 0 else None

CATALAN_NUMBERS = {
    'una': 1, 'un': 1, 'dues': 2, 'dos': 2, 'tres': 3, 'quatre': 4,
    'cinch': 5, 'cinc': 5, 'sis': 6, 'set': 7, 'vuyt': 8, 'vuit': 8,
    'nou': 9, 'deu': 10, 'onze': 11, 'dotze': 12,
}

# Look for ITERATION words preceded by a count (NOT durations like "dies/jorns")
VEGADES_RE = re.compile(
    r'(?:per\s+)?'                                  # optional "per"
    r'(\.[ivxIVX]+\.?|[a-zçé]+)\s+'                 # numeral (roman or word)
    r'(?:vegades|vices|vegada|vice|cyclos|cyclis|reitera)',  # ITERATION only
    re.IGNORECASE
)

def extract_counts_from_text(text):
    """Return list of (count_int, context_string) found."""
    if not text: return []
    found = []
    for m in VEGADES_RE.finditer(text):
        token = m.group(1)
        cleaned = token.strip('.').lower()
        # Try roman first
        n = parse_roman(cleaned)
        if n is None and cleaned in CATALAN_NUMBERS:
            n = CATALAN_NUMBERS[cleaned]
        if n and 2 <= n <= 50:
            ctx_start = max(0, m.start() - 30)
            ctx_end = min(len(text), m.end() + 30)
            found.append((n, text[ctx_start:ctx_end].replace('\n', ' ')))
    return found

# Build paragraph token-streams per matched folio
paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

def is_qok_class(w):
    return w.startswith('qok')

# For each matched folio: extract recipe counts; count qok-class tokens per line
print("="*78)
print("CYCLE-COUNTING IDIOM TEST")
print("="*78)
print()
print("For each matched recipe with explicit count, search for matching qok-cluster")
print("in the corresponding Voynich folio.")
print()

results_by_folio = []
for m in matches:
    f = m['folio']
    ch = get_chapter(m['part'], m['chapter_num'])
    if not ch: continue
    # Extract counts from all paragraphs of the recipe
    all_counts = []
    for p_idx, p in enumerate(ch.get('paragraphs', [])):
        text = (p.get('catalan') or '') + ' ' + (p.get('latin') or '')
        for n, ctx in extract_counts_from_text(text):
            all_counts.append((p_idx, n, ctx))

    if not all_counts:
        continue

    # Get qok-class line counts in the Voynich folio
    by_line = defaultdict(int)
    by_par = defaultdict(int)
    folio_par_idx_to_lines = defaultdict(list)
    for (folio, par_idx), toks in paragraphs.items():
        if folio != f: continue
        for t in toks:
            if is_qok_class(t.word):
                by_line[t.line] += 1
                by_par[par_idx] += 1
                folio_par_idx_to_lines[par_idx].append(t.line)

    # Print findings
    print(f"--- {f}  [{m['tier']}]  {m['recipe_label']}")
    print(f"    Recipe explicit counts found:")
    for p_idx, n, ctx in all_counts:
        print(f"      P{p_idx}: ×{n}  context: \"{ctx.strip()}\"")
    if not by_line:
        print("    No qok-class tokens in folio.")
        print()
        continue

    line_clusters = sorted(by_line.items(), key=lambda x: -x[1])
    print(f"    qok-class clusters by line (top 5):")
    for ln, c in line_clusters[:5]:
        print(f"      L{ln}: {c} qok-class tokens")
    par_clusters = sorted(by_par.items(), key=lambda x: -x[1])
    print(f"    qok-class clusters by paragraph (top 3):")
    for p_idx, c in par_clusters[:3]:
        print(f"      P{p_idx}: {c} qok-class tokens")

    # Check matches: does any line, line-pair, or paragraph count match an explicit count?
    # Also check 2-line windows (e.g., L37-L38 spanning)
    line_pair_counts = {}
    sorted_lines = sorted(by_line.keys(), key=lambda x: int(re.sub(r'[^0-9]', '', str(x)) or 0))
    line_idx = {ln: i for i, ln in enumerate(sorted_lines)}
    for ln in sorted_lines:
        idx = line_idx[ln]
        if idx + 1 < len(sorted_lines):
            next_ln = sorted_lines[idx + 1]
            line_pair_counts[(ln, next_ln)] = by_line[ln] + by_line[next_ln]

    matches_found = []
    for p_idx_recipe, n, ctx in all_counts:
        line_match = any(c == n for ln, c in by_line.items())
        line_pair_match = any(c == n for k, c in line_pair_counts.items())
        par_match = any(c == n for pi, c in by_par.items())
        line_close = any(abs(c - n) <= 1 for ln, c in by_line.items())
        line_pair_close = any(abs(c - n) <= 1 for k, c in line_pair_counts.items())
        par_close = any(abs(c - n) <= 1 for pi, c in by_par.items())
        verdict = '--'
        if line_match: verdict = 'LINE EXACT'
        elif line_pair_match: verdict = '2-LINE EXACT'
        elif par_match: verdict = 'PARAGRAPH EXACT'
        elif line_close: verdict = 'line +/-1'
        elif line_pair_close: verdict = '2-line +/-1'
        elif par_close: verdict = 'paragraph +/-1'
        matches_found.append({'count': n, 'context': ctx.strip(), 'verdict': verdict})
        print(f"    [x{n}]: {verdict}")
    print()
    results_by_folio.append({'folio': f, 'recipe': m['recipe_label'],
                             'explicit_counts': all_counts,
                             'qok_by_line': dict(by_line),
                             'qok_by_par': dict(by_par),
                             'matches': matches_found})

# Summary
print("="*78)
print("SUMMARY")
print("="*78)
total_counts = sum(len(r['matches']) for r in results_by_folio)
exact_line = sum(1 for r in results_by_folio for m in r['matches'] if m['verdict'] == 'LINE EXACT')
exact_par = sum(1 for r in results_by_folio for m in r['matches'] if m['verdict'] == 'PARAGRAPH EXACT')
close_any = sum(1 for r in results_by_folio for m in r['matches']
                if m['verdict'] in ('line ±1', 'paragraph ±1'))
none = total_counts - exact_line - exact_par - close_any
print(f"Total explicit-count instances tested: {total_counts}")
print(f"  Line-exact match:      {exact_line}")
print(f"  Paragraph-exact match: {exact_par}")
print(f"  ±1 (line or par):      {close_any}")
print(f"  No match:              {none}")

if total_counts > 0:
    hit_rate = (exact_line + exact_par + close_any) / total_counts
    print(f"  Hit rate (exact or +/-1): {hit_rate*100:.1f}%")

# Permutation null: for each folio, shuffle qok-class positions across lines,
# recompute hit rate. How often does random distribution match real?
print()
print("="*78)
print("PERMUTATION NULL (qok-class positions shuffled across folio lines)")
print("="*78)

import random
rng = random.Random(42)
n_perm = 1000

# Build per-folio data structures
folio_qok_positions = defaultdict(list)
folio_lines_set = defaultdict(set)
for (folio, par_idx), toks in paragraphs.items():
    for t in toks:
        folio_lines_set[folio].add(t.line)
        if is_qok_class(t.word):
            folio_qok_positions[folio].append(t.line)

null_hit_rates = []
real_hits = exact_line + exact_par + close_any

for trial in range(n_perm):
    trial_hits = 0
    trial_total = 0
    for r in results_by_folio:
        f = r['folio']
        n_qok = len(folio_qok_positions[f])
        line_list = list(folio_lines_set[f])
        if not line_list or n_qok == 0:
            continue
        # Shuffle: assign each qok-class token to a random line
        shuffled = [rng.choice(line_list) for _ in range(n_qok)]
        sh_by_line = Counter(shuffled)
        # Build line-pair counts for shuffled version
        sorted_lns = sorted(sh_by_line.keys(),
                           key=lambda x: int(re.sub(r'[^0-9]', '', str(x)) or 0))
        sh_pairs = {}
        for i, ln in enumerate(sorted_lns):
            if i + 1 < len(sorted_lns):
                sh_pairs[(ln, sorted_lns[i+1])] = sh_by_line[ln] + sh_by_line[sorted_lns[i+1]]
        # Test each explicit count for this folio
        for m in r['matches']:
            n = m['count']
            trial_total += 1
            if any(c == n for c in sh_by_line.values()):
                trial_hits += 1
            elif any(c == n for c in sh_pairs.values()):
                trial_hits += 1
            elif any(abs(c - n) <= 1 for c in sh_by_line.values()):
                trial_hits += 1
    if trial_total > 0:
        null_hit_rates.append(trial_hits / trial_total)

if null_hit_rates:
    null_hit_rates.sort()
    mean_null = sum(null_hit_rates) / len(null_hit_rates)
    p95 = null_hit_rates[int(len(null_hit_rates) * 0.95)]
    p99 = null_hit_rates[int(len(null_hit_rates) * 0.99)]
    n_above = sum(1 for h in null_hit_rates if h >= hit_rate)
    p_value = n_above / len(null_hit_rates)
    print(f"Real hit rate: {hit_rate*100:.1f}%")
    print(f"Null hit rate (mean of {n_perm} shuffles): {mean_null*100:.1f}%")
    print(f"Null 95th percentile: {p95*100:.1f}%")
    print(f"Null 99th percentile: {p99*100:.1f}%")
    print(f"p-value (one-sided): {p_value:.4f}")

# Save
import os
os.makedirs('phases/PHASE_650_CYCLE_COUNTING_IDIOM/results', exist_ok=True)
with open('phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/cycle_count_test.json', 'w') as f:
    json.dump(results_by_folio, f, indent=2, default=str)
print()
print("Saved: phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/cycle_count_test.json")
