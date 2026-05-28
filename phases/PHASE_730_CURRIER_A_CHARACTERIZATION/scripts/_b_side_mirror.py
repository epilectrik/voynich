"""B-side mirror test (crazy-expert's load-bearing recommendation).

QUESTION: Does Currier B ALSO show selective dy-permission by o-content?

If B shows the same o-preference as A → o-selectivity is substrate-level/manuscript-wide,
NOT A-specific. The "A=setup, B=execute" framing collapses.

If B is symmetric in dy across o-containing vs non-o MIDDLEs → the A asymmetry is real
and worth a properly-designed pre-registered test (with terminal-atom-matched null,
HEAD-position decomposition, held-out validation).

This is exploratory characterization. NO registration target — just diagnostic.

Also runs:
- Terminal-atom decomposition: separate o-HEAD from o-elsewhere
- C1557 cross-check: are dy-permissive MIDDLEs in A actually o-HEAD?
- Honest descriptive split: count violations at the descriptive level
"""
import sys
from collections import defaultdict, Counter

import numpy as np
from scipy.stats import mannwhitneyu

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

tx = Transcript(); morph = Morphology()

# Re-derive the 54 dy-eligible MIDDLEs (yesterday's locked filter)
b_mid_total = Counter(); b_mid_dy = Counter()
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try: m = morph.extract(w)
    except Exception: continue
    if not m.middle: continue
    b_mid_total[m.middle] += 1
    if m.suffix == 'dy': b_mid_dy[m.middle] += 1

dy_eligible = [mid for mid in b_mid_total if b_mid_total[mid] >= 10 and b_mid_dy[mid] / b_mid_total[mid] >= 0.20]
print(f'Dy-eligible MIDDLEs: {len(dy_eligible)}')

# A dy-rates
a_mid_total = Counter(); a_mid_dy = Counter()
for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try: m = morph.extract(w)
    except Exception: continue
    if not m.middle: continue
    a_mid_total[m.middle] += 1
    if m.suffix == 'dy': a_mid_dy[m.middle] += 1

# Classifications
def has_o(mid): return 'o' in mid
def starts_o(mid): return mid.startswith('o')
def has_o_head(mid):
    # o is HEAD if it's the first non-prefix atom; for simplicity here, starts_o
    return starts_o(mid)
def o_count(mid): return mid.count('o')
def ends_in(mid, chars): return any(mid.endswith(c) for c in chars)

# Build table
rows = []
for mid in dy_eligible:
    a_tot = a_mid_total.get(mid, 0)
    a_dy = a_mid_dy.get(mid, 0)
    b_tot = b_mid_total[mid]
    b_dy = b_mid_dy[mid]
    rows.append({
        'mid': mid,
        'has_o': has_o(mid),
        'starts_o': starts_o(mid),
        'o_count': o_count(mid),
        'last': mid[-1] if mid else '',
        'a_tot': a_tot, 'a_dy': a_dy,
        'a_rate': a_dy/a_tot if a_tot else None,
        'b_tot': b_tot, 'b_dy': b_dy,
        'b_rate': b_dy/b_tot,
    })

# Honest descriptive split — count violations at >=10% A dy-rate threshold
print('\n=== Honest descriptive split at A dy-rate >= 10% ===')
dy_perm_a = [r for r in rows if r['a_rate'] is not None and r['a_rate'] >= 0.10]
dy_supp_a = [r for r in rows if r['a_rate'] is not None and r['a_rate'] < 0.05]
print(f'  A dy-permissive (rate >= 10%, has A occ): {len(dy_perm_a)}')
print(f'    o-containing: {sum(1 for r in dy_perm_a if r["has_o"])} / {len(dy_perm_a)}')
print(f'    non-o (violations of "all permissive have o"): {[r["mid"] for r in dy_perm_a if not r["has_o"]]}')
print(f'  A dy-suppressed (rate < 5%, has A occ): {len(dy_supp_a)}')
print(f'    non-o: {sum(1 for r in dy_supp_a if not r["has_o"])} / {len(dy_supp_a)}')
print(f'    o-containing (violations of "all suppressed lack o"): {[r["mid"] for r in dy_supp_a if r["has_o"]]}')

# ===== TEST 1: B-side mirror — does B show o-preference too? =====
print('\n' + '='*60)
print('=== TEST 1: B-side mirror — does B also show o-preference? ===')
print('='*60)
b_rates_o = [r['b_rate'] for r in rows if r['has_o']]
b_rates_noo = [r['b_rate'] for r in rows if not r['has_o']]
print(f'  B dy-rate on o-containing dy-eligible MIDDLEs (n={len(b_rates_o)}):')
print(f'    median={np.median(b_rates_o):.3f}, mean={np.mean(b_rates_o):.3f}')
print(f'  B dy-rate on non-o dy-eligible MIDDLEs (n={len(b_rates_noo)}):')
print(f'    median={np.median(b_rates_noo):.3f}, mean={np.mean(b_rates_noo):.3f}')
u, p = mannwhitneyu(b_rates_o, b_rates_noo, alternative='two-sided')
print(f'  Mann-Whitney (two-sided): U={u:.0f}, p={p:.4f}')
u1, p1 = mannwhitneyu(b_rates_o, b_rates_noo, alternative='greater')
print(f'  Mann-Whitney (B-o > B-noo): p={p1:.4f}')

# ===== Also: A vs B asymmetry test =====
print('\n=== TEST 2: A asymmetry (for comparison) ===')
a_rates_o = [r['a_rate'] for r in rows if r['has_o'] and r['a_rate'] is not None]
a_rates_noo = [r['a_rate'] for r in rows if not r['has_o'] and r['a_rate'] is not None]
print(f'  A dy-rate on o-containing (n={len(a_rates_o)}): median={np.median(a_rates_o):.3f}, mean={np.mean(a_rates_o):.3f}')
print(f'  A dy-rate on non-o (n={len(a_rates_noo)}): median={np.median(a_rates_noo):.3f}, mean={np.mean(a_rates_noo):.3f}')
ua, pa = mannwhitneyu(a_rates_o, a_rates_noo, alternative='greater')
print(f'  Mann-Whitney (A-o > A-noo): p={pa:.4f}')

# ===== TEST 3: terminal-atom-matched check =====
print('\n=== TEST 3: terminal-atom decomposition ===')
# For each MIDDLE, what is its last character (terminal atom)?
print(f'  Terminal-atom distribution among dy-eligible MIDDLEs:')
term_counter = Counter(r['last'] for r in rows)
for term, n in sorted(term_counter.items(), key=lambda x: -x[1]):
    print(f'    "{term}": {n} MIDDLEs')

# Group by terminal-atom: do MIDDLEs with same terminal atom show o-difference in A dy?
print(f'\n  Within-terminal-atom A dy-rate by o-content:')
print(f'  {"term":>5} {"o_n":>4} {"o_rate":>8} {"noo_n":>5} {"noo_rate":>9} {"diff":>8}')
for term in sorted(term_counter):
    o_in = [r['a_rate'] for r in rows if r['last']==term and r['has_o'] and r['a_rate'] is not None]
    no_in = [r['a_rate'] for r in rows if r['last']==term and not r['has_o'] and r['a_rate'] is not None]
    if o_in and no_in:
        diff = np.mean(o_in) - np.mean(no_in)
        print(f'  {term:>5} {len(o_in):>4} {np.mean(o_in):>8.3f} {len(no_in):>5} {np.mean(no_in):>9.3f} {diff:>+8.3f}')
    elif o_in:
        print(f'  {term:>5} {len(o_in):>4} {np.mean(o_in):>8.3f}     -        -        -    (only o)')
    elif no_in:
        print(f'  {term:>5}    -        -    {len(no_in):>5} {np.mean(no_in):>9.3f}        -    (only non-o)')

# ===== TEST 4: starts-with-o (HEAD position) vs o-elsewhere =====
print('\n=== TEST 4: o at HEAD-position vs o-elsewhere (per C1556/C1559) ===')
a_rates_ohead = [r['a_rate'] for r in rows if r['starts_o'] and r['a_rate'] is not None]
a_rates_omid = [r['a_rate'] for r in rows if r['has_o'] and not r['starts_o'] and r['a_rate'] is not None]
a_rates_noo_v = [r['a_rate'] for r in rows if not r['has_o'] and r['a_rate'] is not None]
print(f'  A dy-rate, o-HEAD MIDDLEs (n={len(a_rates_ohead)}): mean={np.mean(a_rates_ohead) if a_rates_ohead else 0:.3f}')
print(f'  A dy-rate, o-non-HEAD MIDDLEs (n={len(a_rates_omid)}): mean={np.mean(a_rates_omid) if a_rates_omid else 0:.3f}')
print(f'  A dy-rate, no-o MIDDLEs (n={len(a_rates_noo_v)}): mean={np.mean(a_rates_noo_v):.3f}')

# ===== TEST 5: terminal-atom-matched null (proper confound control) =====
print('\n=== TEST 5: terminal-atom-matched permutation null ===')
# Within terminal-atom strata, do o-containing MIDDLEs in A really differ from non-o?
# Stratified permutation: shuffle o-labels WITHIN each terminal-atom stratum, recompute
# the Mann-Whitney on A dy-rates.
np.random.seed(42)
strata = defaultdict(list)
for r in rows:
    if r['a_rate'] is not None:
        strata[r['last']].append(r)

# Observed stratified statistic: weighted mean of within-stratum (o_mean - noo_mean)
def stratified_diff(rows_in, perm_labels=None):
    """Mean A dy-rate difference (o - non-o) summed across strata, weighted by stratum size."""
    diffs = []
    weights = []
    by_stratum = defaultdict(list)
    if perm_labels is None:
        for r in rows_in:
            by_stratum[r['last']].append((r['has_o'], r['a_rate']))
    else:
        for r, lab in zip(rows_in, perm_labels):
            by_stratum[r['last']].append((lab, r['a_rate']))
    for term, items in by_stratum.items():
        o_vals = [x[1] for x in items if x[0]]
        no_vals = [x[1] for x in items if not x[0]]
        if o_vals and no_vals:
            diffs.append(np.mean(o_vals) - np.mean(no_vals))
            weights.append(len(items))
    if not diffs: return 0
    return np.average(diffs, weights=weights)

# Need rows that have A data
rows_with_a = [r for r in rows if r['a_rate'] is not None]
observed = stratified_diff(rows_with_a)
print(f'  Observed stratified diff (A o-rate - A non-o-rate, terminal-matched): {observed:+.4f}')

# Permute o-labels within strata
n_perm = 1000
null_stats = []
labels = np.array([r['has_o'] for r in rows_with_a])
terms = np.array([r['last'] for r in rows_with_a])
for _ in range(n_perm):
    perm_labels = labels.copy()
    for term in set(terms):
        mask = (terms == term)
        sub = perm_labels[mask].copy()
        np.random.shuffle(sub)
        perm_labels[mask] = sub
    null_stats.append(stratified_diff(rows_with_a, perm_labels=list(perm_labels)))
null_stats = np.array(null_stats)
p_perm = (null_stats >= observed).mean()
print(f'  Terminal-atom-matched permutation null:')
print(f'    null mean={null_stats.mean():+.4f}, std={null_stats.std():.4f}')
print(f'    p (one-sided): {p_perm:.4f}')

# ===== Summary =====
print('\n' + '='*60)
print('=== SUMMARY (diagnostic, no registration target) ===')
print('='*60)
print(f'1. Honest descriptive split: {sum(1 for r in dy_perm_a if not r["has_o"])} non-o MIDDLEs violate "permissive=o-only"')
print(f'2. B-side mirror: B-o vs B-noo Mann-Whitney one-sided p={p1:.4f}')
print(f'   {"B shows o-preference too (substrate-level)" if p1<0.05 else "B is symmetric (asymmetry could be A-specific)"}')
print(f'3. A asymmetry: p={pa:.4f}')
print(f'4. Terminal-atom-matched null: stratified diff observed {observed:+.4f}, p={p_perm:.4f}')
print(f'   {"Effect survives terminal-atom control" if p_perm<0.05 else "Effect DOES NOT survive terminal-atom control"}')
print(f'5. o-HEAD vs o-elsewhere vs no-o means: {np.mean(a_rates_ohead) if a_rates_ohead else 0:.3f} / {np.mean(a_rates_omid) if a_rates_omid else 0:.3f} / {np.mean(a_rates_noo_v):.3f}')
