"""
Phase 650 Step 3: Closed-cycle filter test (corrected per direct-reading).

User correction on f75r: the right unit is the CLOSED CYCLE — a token
matching qok + ... + -dy (closure suffix). Tokens like 'qokey' lack the
-dy closure and represent transitional sub-states, not complete cycles.

Method (corrected):
1. For each matched folio, count tokens matching 'qok.*dy' per paragraph
2. Compare paragraph counts to recipe iteration counts
3. Account for: cycle = 1 initial + N redistillations (× N vegades)
   So expected closed-cycle count = N+1 for "× N redistillations"
4. Report exact-match findings and corpus-rarity context
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

# Iteration count extraction (vegades only)
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

# Closed-cycle filter
def is_closed_cycle(w):
    """qok + ... + -dy closure suffix indicates a complete cycle."""
    return w.startswith('qok') and w.endswith('dy')

# Walk Currier B grouped by paragraph
paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

# Per-paragraph closed-cycle counts
par_closed = {}
for (f, par_idx), toks in paragraphs.items():
    n = sum(1 for t in toks if is_closed_cycle(t.word))
    par_closed[(f, par_idx)] = n

# Corpus-wide distribution
all_par_counts = list(par_closed.values())
count_dist = Counter(all_par_counts)
print("="*78)
print("CORPUS-WIDE CLOSED-CYCLE COUNTS PER PARAGRAPH")
print("="*78)
print(f"\n{'count':>5s}  {'n_pars':>7s}  {'fraction':>10s}")
for n in sorted(count_dist.keys()):
    if n == 0: continue
    pct = count_dist[n] / len(all_par_counts) * 100
    print(f"  {n:>3d}    {count_dist[n]:>7d}  {pct:>9.2f}%")

# Per matched folio: extract recipe counts, find paragraph closed-cycle counts
print()
print("="*78)
print("MATCHED RECIPES: closed-cycle counts vs recipe iteration counts")
print("="*78)
print()
print("Hypothesis: 'redistill × N vegades' encodes as N+1 closed cycles")
print("            (1 initial distillation + N redistillations)")
print()

results = []
for m in matches:
    f = m['folio']
    ch = get_chapter(m['part'], m['chapter_num'])
    if not ch: continue
    counts = []
    for p_idx, p in enumerate(ch.get('paragraphs', [])):
        text = (p.get('catalan') or '') + ' ' + (p.get('latin') or '')
        for n in extract_iteration_counts(text):
            counts.append(n)
    if not counts: continue
    folio_pars = {(folio, par_idx): n for (folio, par_idx), n
                  in par_closed.items() if folio == f}
    if not folio_pars: continue

    print(f"--- {f}  [{m['tier']}]  {m['recipe_label']}")
    for n in counts:
        target_with_initial = n + 1
        # Find paragraph(s) with EXACTLY n+1 closed cycles
        exact_pars = [(p_idx, c) for (folio, p_idx), c in folio_pars.items() if c == target_with_initial]
        # Also check for exact n match (without +1)
        exact_pars_n = [(p_idx, c) for (folio, p_idx), c in folio_pars.items() if c == n]
        # All paragraph counts on this folio
        all_par_for_folio = sorted(folio_pars.values(), reverse=True)

        # Corpus-wide rarity of exact target
        n_pars_with_target = count_dist.get(target_with_initial, 0)
        n_pars_with_n = count_dist.get(n, 0)
        total_pars = sum(1 for v in all_par_counts if v > 0)

        print(f"    [x{n} vegades]  expected: {target_with_initial} cycles (n+1) or {n} (n alone)")
        print(f"      paragraph closed-cycle counts on folio: {all_par_for_folio[:5]}")
        if exact_pars:
            verdict_n1 = f"YES: paragraphs {[p[0] for p in exact_pars]} = {target_with_initial} cycles"
        else:
            verdict_n1 = f"no paragraph with {target_with_initial} cycles"
        if exact_pars_n:
            verdict_n = f"YES: paragraphs {[p[0] for p in exact_pars_n]} = {n} cycles"
        else:
            verdict_n = f"no paragraph with {n} cycles"
        print(f"      target {target_with_initial}: {verdict_n1}")
        print(f"      target {n}:  {verdict_n}")
        print(f"      corpus rarity: {n_pars_with_target} pars with {target_with_initial} cycles, {n_pars_with_n} pars with {n} cycles (out of {total_pars} non-empty)")

        results.append({
            'folio': f,
            'recipe_count': n,
            'target_n_plus_1': target_with_initial,
            'target_n': n,
            'exact_match_n_plus_1': len(exact_pars) > 0,
            'exact_match_n': len(exact_pars_n) > 0,
            'folio_par_counts': all_par_for_folio,
            'corpus_rarity_n_plus_1': n_pars_with_target,
            'corpus_rarity_n': n_pars_with_n,
        })
    print()

# Save
import os
os.makedirs('phases/PHASE_650_CYCLE_COUNTING_IDIOM/results', exist_ok=True)
with open('phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/closed_cycle_filter.json', 'w') as f:
    json.dump({'results': results, 'corpus_distribution': dict(count_dist)},
              f, indent=2, default=str)
print()
print("Saved: phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/closed_cycle_filter.json")
