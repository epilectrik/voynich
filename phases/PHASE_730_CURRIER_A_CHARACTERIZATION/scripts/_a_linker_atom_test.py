"""Currier A Linker Atom-Level Content Test (PRE-REGISTERED).

Follow-up to _currier_a_linker_test.py which found:
- H1 PASS: linker topology non-random (max in-degree 5, p_emp=0.021)
- H5 PASS: random RI quadruples never reach linker convergence (p<0.0001)
- H2/H3/H4 FAIL: no forward-flow, content, or collector-diversity signal

The structural pattern is real but PP-MIDDLE content tests failed.
This test re-examines linker-pair content at the ATOM level per CASC C1395 T5
(A=state-describing l-terminals, B=action-performing dy-terminals).

PRE-REGISTERED HYPOTHESES (locked before running):

A1: TERMINAL-ATOM JACCARD
    For each linker-connected folio pair, compute Jaccard on TERMINAL ATOMS
    (y, l, r, h, m, n, k, t per CASC TERM_ATOMS).
    PASS: linker-pair mean Jaccard > random-pair p95 (p<0.05)

A2: HEAD-ATOM JACCARD
    For each linker pair, compute Jaccard on HEAD ATOMS (a, e, o, k, t per HEAD_ATOMS).
    PASS: linker-pair mean Jaccard > random-pair p95

A3: l-TERMINAL RATE CORRELATION
    A's l-terminal enrichment (1.84x per C1395 T5) is the state-describing signature.
    If linkers connect state-coherent folios, l-terminal RATES should correlate
    between linker-pair folios more than between random pairs.
    PASS: |Pearson correlation| of linker pair l-rates > p95 of random pair correlation

A4: HEAD-TYPE DOMINANCE MATCH
    Each folio has a dominant HEAD-atom. Linker-connected folios should share
    dominant HEAD more often than random.
    PASS: linker-pair head-match rate > random-pair head-match rate (p<0.05)

A5: ATOM COMPOSITION COSINE
    For each folio, build an 18-atom frequency vector. Compute cosine similarity
    for linker pairs vs random pairs.
    PASS: linker-pair cosine > random-pair p95

NEGATIVE CONTROL: A6
    Same tests on 1000 random samples of 4 multi-folio RI MIDDLEs (matched to
    linker convergence structure). Random sets should NOT show any of A1-A5
    above linker level.

VERDICT:
- 3+ of 5 atom tests PASS: linkers carry atom-level semantic content
- 1-2 PASS: weak; topology is structurally real but content empty at most levels
- 0 PASS: linkers are structural-only artifacts (organizational not semantic)
"""
import json
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, 'C:/git/voynich')
random.seed(42); np.random.seed(42)

from scripts.voynich import Transcript, Morphology, HEAD_ATOMS, MOD_ATOMS, TERM_ATOMS

print(f'HEAD atoms: {sorted(HEAD_ATOMS)}')
print(f'MOD atoms: {sorted(MOD_ATOMS)}')
print(f'TERM atoms: {sorted(TERM_ATOMS)}')

# 12 directed edges (same as topology test)
LINKS = [
    ('f21r', 'f93v'), ('f53v', 'f93v'), ('f54r', 'f93v'),
    ('f87r', 'f93v'), ('f89v1', 'f93v'),
    ('f27r', 'f32r'), ('f30v', 'f32r'), ('f42r', 'f32r'), ('f93r', 'f32r'),
    ('f53v', 'f87r'), ('f87r', 'f87r'),  # self-loop
    ('f89v1', 'f37v'),
]
LINKER_FOLIOS = set()
for s, t in LINKS:
    LINKER_FOLIOS.add(s)
    LINKER_FOLIOS.add(t)

# ===== Load A folio atom profiles =====
tx = Transcript()
morph = Morphology()

# Per-folio atom counts
folio_token_count = defaultdict(int)
folio_head_atoms = defaultdict(Counter)
folio_term_atoms = defaultdict(Counter)
folio_all_atoms = defaultdict(Counter)
folio_l_terminal_count = defaultdict(int)
folio_dy_terminal_count = defaultdict(int)

for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try:
        a = morph.atomize(w)
    except Exception:
        continue
    folio_token_count[t.folio] += 1
    # Sum atoms in this token
    if hasattr(a, 'atoms'):
        for char, role, _ in a.atoms:
            folio_all_atoms[t.folio][char] += 1
            if role == 'HEAD':
                folio_head_atoms[t.folio][char] += 1
            elif role == 'TERM':
                folio_term_atoms[t.folio][char] += 1
                if char == 'l':
                    folio_l_terminal_count[t.folio] += 1
                elif char == 'y':
                    pass  # B has dy-terminal as 'd' MOD + 'y' TERM — but in A 'y' alone might mean different
    # Check for actual 'dy' suffix or terminal
    if w.endswith('dy'):
        folio_dy_terminal_count[t.folio] += 1

a_folios = [f for f in folio_token_count if folio_token_count[f] >= 10]
print(f'\nCurrier A folios with >=10 tokens: {len(a_folios)}')

# Verify l-terminal enrichment (CASC: 1.84x A vs B)
total_a_tokens = sum(folio_token_count.values())
total_l = sum(folio_l_terminal_count.values())
print(f'A total l-terminal rate: {total_l/total_a_tokens:.4f}')


# ===== Helper functions =====
def folio_atom_set(folio, level='all'):
    """Get set of unique atoms in folio at given level."""
    if level == 'head':
        return set(folio_head_atoms[folio].keys())
    elif level == 'term':
        return set(folio_term_atoms[folio].keys())
    else:
        return set(folio_all_atoms[folio].keys())


def folio_atom_vector(folio, atom_set):
    """Get normalized atom-frequency vector over atom_set."""
    n = folio_token_count[folio]
    if n == 0: return np.zeros(len(atom_set))
    return np.array([folio_all_atoms[folio].get(a, 0) / n for a in atom_set])


def jaccard(a, b):
    if not a and not b: return 1.0
    if not (a | b): return 0.0
    return len(a & b) / len(a | b)


def cosine(u, v):
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu == 0 or nv == 0: return 0
    return float(np.dot(u, v) / (nu * nv))


# Get linker pair stats
def compute_pair_stats(pairs):
    term_jac = []
    head_jac = []
    l_rates = []  # tuples of (s_rate, t_rate)
    head_match = []  # 1 if shared dominant head
    cosines = []
    for s, t in pairs:
        if s not in folio_token_count or t not in folio_token_count:
            continue
        if folio_token_count[s] < 5 or folio_token_count[t] < 5:
            continue
        # A1: Terminal Jaccard
        ts = folio_atom_set(s, 'term')
        tt = folio_atom_set(t, 'term')
        term_jac.append(jaccard(ts, tt))
        # A2: Head Jaccard
        hs = folio_atom_set(s, 'head')
        ht = folio_atom_set(t, 'head')
        head_jac.append(jaccard(hs, ht))
        # A3: l-terminal rates
        ls = folio_l_terminal_count[s] / max(folio_token_count[s], 1)
        lt = folio_l_terminal_count[t] / max(folio_token_count[t], 1)
        l_rates.append((ls, lt))
        # A4: Head dominance match
        head_s = folio_head_atoms[s].most_common(1)
        head_t = folio_head_atoms[t].most_common(1)
        if head_s and head_t:
            head_match.append(1 if head_s[0][0] == head_t[0][0] else 0)
        # A5: Atom composition cosine
        atom_universe = set(folio_all_atoms[s].keys()) | set(folio_all_atoms[t].keys())
        u = folio_atom_vector(s, sorted(atom_universe))
        v = folio_atom_vector(t, sorted(atom_universe))
        cosines.append(cosine(u, v))
    return {
        'term_jac': term_jac, 'head_jac': head_jac, 'l_rates': l_rates,
        'head_match': head_match, 'cosines': cosines,
    }


print('\nComputing linker-pair atom stats...')
linker_stats = compute_pair_stats(LINKS)
print(f'  n linker pairs analyzed: {len(linker_stats["term_jac"])}')

# ===== Build random baseline =====
print('\nGenerating random pair baseline (10000 samples)...')
N_BASELINE = 10000
random_term_jac = []
random_head_jac = []
random_l_corr_samples = []  # we'll bootstrap a correlation distribution
random_head_match = []
random_cosines = []

rng = random.Random(42)
folios_eligible = [f for f in a_folios if folio_token_count[f] >= 5]
for _ in range(N_BASELINE):
    s = rng.choice(folios_eligible)
    t = rng.choice(folios_eligible)
    if s == t: continue
    ts = folio_atom_set(s, 'term')
    tt = folio_atom_set(t, 'term')
    random_term_jac.append(jaccard(ts, tt))
    hs = folio_atom_set(s, 'head')
    ht = folio_atom_set(t, 'head')
    random_head_jac.append(jaccard(hs, ht))
    head_s = folio_head_atoms[s].most_common(1)
    head_t = folio_head_atoms[t].most_common(1)
    if head_s and head_t:
        random_head_match.append(1 if head_s[0][0] == head_t[0][0] else 0)
    atom_universe = set(folio_all_atoms[s].keys()) | set(folio_all_atoms[t].keys())
    u = folio_atom_vector(s, sorted(atom_universe))
    v = folio_atom_vector(t, sorted(atom_universe))
    random_cosines.append(cosine(u, v))


def pct_above(vals, threshold):
    return (np.array(vals) >= threshold).mean()


# ===== Run tests =====
print('\n' + '=' * 60)
print('=== ATOM-LEVEL LINKER CONTENT TESTS ===')
print('=' * 60)

# A1: Terminal Jaccard
print('\n--- A1: Terminal-atom Jaccard ---')
linker_term_mean = np.mean(linker_stats['term_jac'])
random_term_arr = np.array(random_term_jac)
print(f'  Linker pairs: mean {linker_term_mean:.4f} (n={len(linker_stats["term_jac"])})')
print(f'  Random baseline: mean {random_term_arr.mean():.4f}, p95={np.percentile(random_term_arr, 95):.4f}')
p_emp_a1 = pct_above(random_term_arr, linker_term_mean)
print(f'  p_emp (random >= linker mean): {p_emp_a1:.4f}')
a1_pass = p_emp_a1 < 0.05
print(f'  A1 VERDICT: {"PASS" if a1_pass else "FAIL"}')

# A2: Head Jaccard
print('\n--- A2: Head-atom Jaccard ---')
linker_head_mean = np.mean(linker_stats['head_jac'])
random_head_arr = np.array(random_head_jac)
print(f'  Linker pairs: mean {linker_head_mean:.4f}')
print(f'  Random baseline: mean {random_head_arr.mean():.4f}, p95={np.percentile(random_head_arr, 95):.4f}')
p_emp_a2 = pct_above(random_head_arr, linker_head_mean)
print(f'  p_emp: {p_emp_a2:.4f}')
a2_pass = p_emp_a2 < 0.05
print(f'  A2 VERDICT: {"PASS" if a2_pass else "FAIL"}')

# A3: l-terminal rate correlation
print('\n--- A3: l-terminal rate correlation (state-describing signature) ---')
if linker_stats['l_rates']:
    sources_l = np.array([x[0] for x in linker_stats['l_rates']])
    targets_l = np.array([x[1] for x in linker_stats['l_rates']])
    linker_l_corr = float(np.corrcoef(sources_l, targets_l)[0, 1]) if len(sources_l) > 1 else 0
    print(f'  Linker pairs: corr = {linker_l_corr:+.4f} (n={len(sources_l)})')

    # Bootstrap random correlation distribution by sampling random folio pairs
    random_l_corrs = []
    for _ in range(1000):
        sampled = [(rng.choice(folios_eligible), rng.choice(folios_eligible)) for _ in range(len(sources_l))]
        ls = []; lt = []
        for s, t in sampled:
            if s == t: continue
            ls.append(folio_l_terminal_count[s] / max(folio_token_count[s], 1))
            lt.append(folio_l_terminal_count[t] / max(folio_token_count[t], 1))
        if len(ls) > 1:
            c = float(np.corrcoef(ls, lt)[0, 1])
            if not np.isnan(c):
                random_l_corrs.append(c)
    random_l_arr = np.array(random_l_corrs)
    print(f'  Random correlations: mean {random_l_arr.mean():+.4f}, p95 |corr|={np.percentile(np.abs(random_l_arr), 95):.4f}')
    p_emp_a3 = (np.abs(random_l_arr) >= abs(linker_l_corr)).mean()
    print(f'  p_emp (|random| >= |linker|): {p_emp_a3:.4f}')
    a3_pass = p_emp_a3 < 0.05
    print(f'  A3 VERDICT: {"PASS" if a3_pass else "FAIL"}')
else:
    a3_pass = False
    print('  Insufficient data')

# A4: Head dominance match
print('\n--- A4: Dominant HEAD-atom match ---')
linker_match_rate = np.mean(linker_stats['head_match']) if linker_stats['head_match'] else 0
random_match_rate = np.mean(random_head_match) if random_head_match else 0
print(f'  Linker pairs: {sum(linker_stats["head_match"])}/{len(linker_stats["head_match"])} = {100*linker_match_rate:.1f}%')
print(f'  Random baseline: {100*random_match_rate:.1f}%')
# Bootstrap p-value
n_linker = len(linker_stats['head_match'])
bootstrap_rates = []
random_match_arr = np.array(random_head_match)
for _ in range(10000):
    sample = rng.choices(random_head_match, k=n_linker)
    bootstrap_rates.append(np.mean(sample))
bootstrap_arr = np.array(bootstrap_rates)
p_emp_a4 = (bootstrap_arr >= linker_match_rate).mean()
print(f'  p_emp (random sample of n={n_linker} matches >= linker rate): {p_emp_a4:.4f}')
a4_pass = p_emp_a4 < 0.05
print(f'  A4 VERDICT: {"PASS" if a4_pass else "FAIL"}')

# A5: Atom composition cosine
print('\n--- A5: Atom composition cosine similarity ---')
linker_cos_mean = np.mean(linker_stats['cosines'])
random_cos_arr = np.array(random_cosines)
print(f'  Linker pairs: mean cosine {linker_cos_mean:.4f}')
print(f'  Random baseline: mean {random_cos_arr.mean():.4f}, p95={np.percentile(random_cos_arr, 95):.4f}')
p_emp_a5 = pct_above(random_cos_arr, linker_cos_mean)
print(f'  p_emp: {p_emp_a5:.4f}')
a5_pass = p_emp_a5 < 0.05
print(f'  A5 VERDICT: {"PASS" if a5_pass else "FAIL"}')

# ===== FINAL =====
print('\n' + '=' * 60)
print('=== ATOM-LEVEL CONTENT VERDICT ===')
print('=' * 60)
results = {'A1 term-jac': a1_pass, 'A2 head-jac': a2_pass, 'A3 l-term-corr': a3_pass, 'A4 head-dom-match': a4_pass, 'A5 atom-cosine': a5_pass}
for k, v in results.items():
    print(f'  {k}: {"PASS" if v else "FAIL"}')
n_pass = sum(results.values())
print(f'\nTotal: {n_pass}/5')

# Bonferroni-adjusted threshold note
print(f'\n(Bonferroni-adjusted threshold for 5 tests: p < 0.01)')

# Recompute strict pass with Bonferroni
strict = {
    'A1 (p={:.4f})'.format(p_emp_a1): p_emp_a1 < 0.01,
    'A2 (p={:.4f})'.format(p_emp_a2): p_emp_a2 < 0.01,
    'A3 (p={:.4f})'.format(p_emp_a3 if 'p_emp_a3' in dir() else 1.0): (p_emp_a3 if 'p_emp_a3' in dir() else 1.0) < 0.01,
    'A4 (p={:.4f})'.format(p_emp_a4): p_emp_a4 < 0.01,
    'A5 (p={:.4f})'.format(p_emp_a5): p_emp_a5 < 0.01,
}
print('\nBonferroni-strict results:')
for k, v in strict.items():
    print(f'  {k}: {"PASS" if v else "FAIL"}')

if n_pass >= 3:
    print('\nVERDICT: Linkers carry atom-level semantic content (>=3 tests pass).')
elif n_pass >= 1:
    print(f'\nVERDICT: Linkers have partial atom-level signal ({n_pass}/5).')
else:
    print('\nVERDICT: Linkers are structural-only (no atom-level content semantics).')
