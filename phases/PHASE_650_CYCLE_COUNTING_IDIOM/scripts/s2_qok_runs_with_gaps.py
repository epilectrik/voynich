"""
Phase 650 Step 2: qok-runs with small interrupting gaps, sequential walk.

User correction: my Step 1 test missed the real pattern because it required
(a) line-bounded clusters, (b) exact-identical tokens, and (c) no interruption.

The actual encoding (per direct folio reading): alternating qokeedy/qokedy
across line breaks, with occasional ol-prefix tokens (e.g., 'lol') as
vessel-state checkpoints between cycles.

Method:
1. Walk Currier B tokens in document order (ignoring line breaks)
2. Identify qok-runs: maximal sequences of qok-class tokens allowing
   up to K interrupting non-qok-class tokens (K=1 default)
3. Catalogue runs by length; test against recipe iteration counts
4. Permutation null: shuffle qok-class positions and recompute

This should catch:
- Cross-line runs (the line break is incidental)
- Alternating sub-types (qokeedy/qokedy alternation = same operational class)
- Single-token interruptions (lol = vessel-state checkpoint between cycles)
"""
import sys
import json
import re
import random
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

# Iteration-only count extraction
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
        if n and 2 <= n <= 50:
            out.append(n)
    return out

# Build sequential token streams per folio (in document order, ignoring lines)
folio_tokens = defaultdict(list)
for t in tx.currier_b():
    folio_tokens[t.folio].append(t)

def is_qok_class(w):
    return w.startswith('qok')

def find_qok_runs(tokens, max_gap=1):
    """Walk sequentially; find maximal runs of qok-class tokens
    with up to max_gap non-qok-class interruptions allowed inside the run.
    Returns list of (start_idx, end_idx, qok_count, run_string)."""
    runs = []
    i = 0
    n = len(tokens)
    while i < n:
        if not is_qok_class(tokens[i].word):
            i += 1
            continue
        # start a run
        start = i
        qok_count = 0
        gap_count = 0
        last_qok = i
        j = i
        while j < n:
            if is_qok_class(tokens[j].word):
                qok_count += 1
                last_qok = j
                gap_count = 0  # reset gap counter after a qok
                j += 1
            else:
                # try to absorb up to max_gap non-qok tokens
                gap_count += 1
                if gap_count > max_gap:
                    break
                j += 1
        # backtrack to last qok in the run
        run_tokens = [t.word for t in tokens[start:last_qok+1]]
        runs.append({'start': start, 'end': last_qok,
                     'qok_count': qok_count,
                     'span': last_qok - start + 1,
                     'tokens': run_tokens,
                     'start_line': tokens[start].line,
                     'end_line': tokens[last_qok].line})
        i = last_qok + 1
    return runs

# Test: distribution of qok-run lengths across all of Currier B
print("="*78)
print("QOK-RUN LENGTH DISTRIBUTION ACROSS ALL CURRIER B (max_gap=1)")
print("="*78)
all_runs = []
for f, toks in folio_tokens.items():
    runs = find_qok_runs(toks, max_gap=1)
    for r in runs:
        r['folio'] = f
        all_runs.append(r)

length_counts = Counter(r['qok_count'] for r in all_runs)
print(f"\nTotal qok-runs: {len(all_runs)}")
print(f"\n{'qok-count':>10s}  {'n_runs':>8s}  {'fraction':>10s}")
for n in sorted(length_counts.keys()):
    pct = length_counts[n] / len(all_runs) * 100
    bar = '#' * min(int(pct/2), 40)
    print(f"  {n:>8d}  {length_counts[n]:>8d}  {pct:>9.1f}%  {bar}")

# Test recipe iteration counts
print()
print("="*78)
print("RECIPE-ITERATION-COUNT vs QOK-RUN MATCHING")
print("="*78)
print()

results_by_folio = []
for m in matches:
    f = m['folio']
    if f not in folio_tokens: continue
    ch = get_chapter(m['part'], m['chapter_num'])
    if not ch: continue
    counts = []
    for p_idx, p in enumerate(ch.get('paragraphs', [])):
        text = (p.get('catalan') or '') + ' ' + (p.get('latin') or '')
        for n in extract_iteration_counts(text):
            counts.append(n)
    if not counts: continue

    folio_runs = [r for r in all_runs if r['folio'] == f]
    folio_runs_by_length = defaultdict(list)
    for r in folio_runs:
        folio_runs_by_length[r['qok_count']].append(r)

    print(f"--- {f}  [{m['tier']}]  {m['recipe_label']}")
    print(f"    Recipe iteration counts: {counts}")
    print(f"    qok-runs on this folio: {len(folio_runs)}")
    longest = max((r['qok_count'] for r in folio_runs), default=0)
    print(f"    Longest qok-run: {longest}")

    # For each count, check if a matching run exists ON THIS FOLIO and how rare it is corpus-wide
    for n in counts:
        exact_runs = folio_runs_by_length.get(n, [])
        gte_runs = [r for r in folio_runs if r['qok_count'] >= n]
        # Corpus-wide rarity
        corpus_n_with_count = sum(1 for r in all_runs if r['qok_count'] == n)
        corpus_n_with_gte = sum(1 for r in all_runs if r['qok_count'] >= n)
        n_folios_with_gte = len(set(r['folio'] for r in all_runs if r['qok_count'] >= n))

        print(f"    [x{n}]:")
        print(f"      exact match on folio: {'YES' if exact_runs else 'no'}  ({len(exact_runs)} runs)")
        print(f"      run >= {n} on folio: {'YES' if gte_runs else 'no'}  ({len(gte_runs)} runs)")
        print(f"      corpus-wide: runs of {n} = {corpus_n_with_count}; runs >= {n} = {corpus_n_with_gte} on {n_folios_with_gte} folios")
        if gte_runs:
            longest_on_folio = max(gte_runs, key=lambda r: r['qok_count'])
            print(f"      longest run on folio: count={longest_on_folio['qok_count']} at L{longest_on_folio['start_line']}-L{longest_on_folio['end_line']}")
            preview = ' '.join(longest_on_folio['tokens'][:12])
            if len(longest_on_folio['tokens']) > 12:
                preview += ' ...'
            print(f"      tokens: {preview}")

    results_by_folio.append({
        'folio': f, 'recipe': m['recipe_label'], 'counts': counts,
        'folio_runs': len(folio_runs), 'longest': longest,
    })
    print()

# Permutation null with the new test
print("="*78)
print("PERMUTATION NULL")
print("="*78)
print()
print("For each folio, shuffle qok-class token positions across folio-positions,")
print("recompute longest run. How rare are the long runs we observe?")

rng = random.Random(42)
n_perm = 500

def longest_run_from_mask(mask, max_gap=1):
    """Given a boolean array (True = qok-class), find longest qok-run with up to
    max_gap interrupting False's allowed inside the run."""
    n = len(mask)
    longest = 0
    i = 0
    while i < n:
        if not mask[i]:
            i += 1
            continue
        # start a run at i
        qok_count = 0
        gap_count = 0
        last_qok = i
        j = i
        while j < n:
            if mask[j]:
                qok_count += 1
                last_qok = j
                gap_count = 0
                j += 1
            else:
                gap_count += 1
                if gap_count > max_gap:
                    break
                j += 1
        if qok_count > longest:
            longest = qok_count
        i = last_qok + 1
    return longest

null_longest_by_folio = {}
for f, toks in folio_tokens.items():
    if len(toks) < 5: continue
    n_total = len(toks)
    real_mask = [is_qok_class(t.word) for t in toks]
    n_qok = sum(real_mask)
    if n_qok == 0: continue

    nulls = []
    indices = list(range(n_total))
    for trial in range(n_perm):
        # Pick n_qok positions at random
        positions = rng.sample(indices, n_qok)
        mask = [False] * n_total
        for p in positions: mask[p] = True
        nulls.append(longest_run_from_mask(mask, max_gap=1))
    null_longest_by_folio[f] = nulls

print()
print(f"{'Folio':>8s}  {'Real':>5s}  {'Null mean':>10s}  {'Null p95':>9s}  {'Null p99':>9s}  {'p-val':>6s}")
for r_data in results_by_folio:
    f = r_data['folio']
    if f not in null_longest_by_folio: continue
    null_distribution = null_longest_by_folio[f]
    null_mean = sum(null_distribution) / len(null_distribution)
    null_distribution.sort()
    p95 = null_distribution[int(len(null_distribution)*0.95)]
    p99 = null_distribution[int(len(null_distribution)*0.99)]
    n_above = sum(1 for x in null_distribution if x >= r_data['longest'])
    p_val = n_above / len(null_distribution)
    print(f"  {f:>6s}  {r_data['longest']:>5d}  {null_mean:>10.2f}  {p95:>9d}  {p99:>9d}  {p_val:>6.4f}")

# Save
import os
os.makedirs('phases/PHASE_650_CYCLE_COUNTING_IDIOM/results', exist_ok=True)
with open('phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/qok_runs_with_gaps.json', 'w') as f:
    json.dump({'recipe_results': results_by_folio,
               'corpus_run_distribution': dict(length_counts),
               'total_runs': len(all_runs)}, f, indent=2, default=str)
print()
print("Saved: phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/qok_runs_with_gaps.json")
