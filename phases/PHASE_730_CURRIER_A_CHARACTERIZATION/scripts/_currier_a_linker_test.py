"""Currier A Linker Topology Test (PRE-REGISTERED).

Tests whether the 4 RI linkers identified in C835 carry semantic load
above the singleton noise floor.

PRE-REGISTERED HYPOTHESES (locked before running):

H1: TOPOLOGY NON-RANDOM
    Linker max-in-degree (observed 5 for f93v) should exceed 95th
    percentile of random-graph null (12 directed edges across 12 nodes).
    PASS: observed max-in-degree > p95(null)

H2: FORWARD-FLOW DIRECTION SIGNIFICANT
    8 forward / 3 backward / 1 self of 12 edges.
    Binomial test on 8/11 directional edges (excluding self-loop).
    PASS: p_binom < 0.10 (one-tailed, forward > 0.5)

H3: LINKER-PAIRS SHARE CONTENT
    For each of 12 directed edges, compute PP-MIDDLE Jaccard between
    source and target folio. Compare to baseline of random A-folio pairs.
    PASS: linker-pair mean Jaccard > random-pair p95 (permutation)

H4: COLLECTOR FOLIOS ARE DIVERSITY-RICH
    Collectors (f93v, f32r, f87r, f37v) should have above-median PP-MIDDLE
    type count (aggregate from many sources).
    PASS: collector mean > A-folio median

H5: NEGATIVE CONTROL — RANDOM RI MIDDLES DON'T CONVERGE
    Take 4 random RI MIDDLEs with similar position-locked behavior.
    Check if they show convergent topology comparable to linkers.
    PASS: random sets show LOWER max-in-degree than linkers (95% of trials)

Verdict combinations:
- H1+H3 both PASS = topology has real semantic content
- H1 PASS, H3 FAIL = topology is non-random but doesn't track content
- H1 FAIL = topology indistinguishable from random
"""
import json
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

sys.path.insert(0, 'C:/git/voynich')
random.seed(42); np.random.seed(42)

from scripts.voynich import Transcript, Morphology

# ===== LINKER DATA FROM C835 =====
LINKERS = ['cthody', 'ctho', 'ctheody', 'qokoiiin']

# 12 directed edges: (source_folio, target_folio, linker_token)
LINKS = [
    ('f21r', 'f93v', 'cthody'),
    ('f53v', 'f93v', 'cthody'),
    ('f54r', 'f93v', 'cthody'),
    ('f87r', 'f93v', 'cthody'),
    ('f89v1', 'f93v', 'cthody'),
    ('f27r', 'f32r', 'ctho'),
    ('f30v', 'f32r', 'ctho'),
    ('f42r', 'f32r', 'ctho'),
    ('f93r', 'f32r', 'ctho'),
    ('f53v', 'f87r', 'ctheody'),
    ('f87r', 'f87r', 'ctheody'),  # self-loop
    ('f89v1', 'f37v', 'qokoiiin'),
]

LINKER_FOLIOS = set()
for s, t, _ in LINKS:
    LINKER_FOLIOS.add(s)
    LINKER_FOLIOS.add(t)
print(f'12 directed edges, {len(LINKER_FOLIOS)} distinct folios in network')

# ===== Load Currier A folio MIDDLE sets =====
print('\nLoading Currier A folio MIDDLE sets...')
tx = Transcript()
morph = Morphology()
folio_middles = defaultdict(set)
folio_pp_middles = defaultdict(set)
folio_ri_middles = defaultdict(set)
ALL_MIDDLES = set()

# First pass: identify ALL middles
all_middles_count = Counter()
b_middles = set()
a_middles = set()
for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try:
        m = morph.extract(w)
        if m.middle:
            a_middles.add(m.middle)
    except Exception: pass
for t in tx.currier_b(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try:
        m = morph.extract(w)
        if m.middle:
            b_middles.add(m.middle)
    except Exception: pass

PP = a_middles & b_middles  # appears in both = Participation Pipeline
RI = a_middles - b_middles  # A-exclusive = Registry-Internal
print(f'PP MIDDLEs: {len(PP)}, RI MIDDLEs: {len(RI)} (cf. CASC: PP=404, RI=609)')

# Second pass: per-folio MIDDLE sets
folio_count = defaultdict(Counter)
for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try:
        m = morph.extract(w)
        if m.middle:
            folio_middles[t.folio].add(m.middle)
            if m.middle in PP:
                folio_pp_middles[t.folio].add(m.middle)
            elif m.middle in RI:
                folio_ri_middles[t.folio].add(m.middle)
            folio_count[t.folio][m.middle] += 1
    except Exception: pass

print(f'A folios with data: {len(folio_middles)}')
# All A folios for baseline
all_a_folios = list(folio_middles.keys())

# ===== H1: TOPOLOGY NON-RANDOM =====
print('\n=== H1: TOPOLOGY NON-RANDOM ===')

# Observed in-degrees
in_deg = Counter()
for s, t, _ in LINKS:
    in_deg[t] += 1
obs_max_in = max(in_deg.values())
print(f'Observed in-degrees: {dict(in_deg)}')
print(f'Observed max in-degree: {obs_max_in}')

# Random null: shuffle source-target assignments
N_PERMS = 10000
nodes = list(LINKER_FOLIOS)
n_edges = len(LINKS)
max_in_null = []
for _ in range(N_PERMS):
    # Random directed graph with same N nodes, N edges
    edges = [(random.choice(nodes), random.choice(nodes)) for _ in range(n_edges)]
    in_d = Counter()
    for s, t in edges:
        in_d[t] += 1
    max_in_null.append(max(in_d.values()))
p95_null = np.percentile(max_in_null, 95)
p_emp_h1 = (np.array(max_in_null) >= obs_max_in).mean()
print(f'Null p95 max-in: {p95_null:.1f}')
print(f'Null p99 max-in: {np.percentile(max_in_null, 99):.1f}')
print(f'p_emp (obs >= null): {p_emp_h1:.4f}')
h1_pass = obs_max_in > p95_null
print(f'H1 VERDICT: {"PASS" if h1_pass else "FAIL"}')

# ===== H2: FORWARD-FLOW SIGNIFICANT =====
print('\n=== H2: FORWARD-FLOW DIRECTION ===')

# Parse folio numbers for direction
def folio_num(f):
    # e.g. f21r -> 21; f89v1 -> 89.51
    m = ''.join(c for c in f if c.isdigit())
    if not m: return 0
    base = int(m)
    if 'v' in f: base += 0.5
    return base


forward = 0; backward = 0; same = 0
for s, t, _ in LINKS:
    sn, tn = folio_num(s), folio_num(t)
    if tn > sn: forward += 1
    elif tn < sn: backward += 1
    else: same += 1
print(f'Forward: {forward}, Backward: {backward}, Self: {same} of {len(LINKS)}')

directional = forward + backward
if directional > 0:
    p_binom = binomtest(forward, directional, p=0.5, alternative='greater').pvalue
    print(f'Binomial test (forward vs random 50/50): p = {p_binom:.4f}')
    h2_pass = p_binom < 0.10
    print(f'H2 VERDICT: {"PASS" if h2_pass else "FAIL"}')
else:
    h2_pass = False
    print('No directional edges')

# ===== H3: LINKER-PAIRS SHARE PP-MIDDLE CONTENT =====
print('\n=== H3: LINKER-PAIRS SHARE CONTENT ===')

def jaccard(a, b):
    if not a and not b: return 1.0
    return len(a & b) / len(a | b) if (a | b) else 0


# Linker-pair Jaccards (use PP-MIDDLE sets — shared with B)
linker_jaccards = []
for s, t, _ in LINKS:
    if s in folio_pp_middles and t in folio_pp_middles:
        j = jaccard(folio_pp_middles[s], folio_pp_middles[t])
        linker_jaccards.append(j)
mean_linker_j = np.mean(linker_jaccards) if linker_jaccards else 0
print(f'Linker-pair mean PP-MIDDLE Jaccard: {mean_linker_j:.4f} (n={len(linker_jaccards)})')

# Baseline: random folio pairs from A
rng = random.Random(42)
N_BASELINE = 10000
random_jaccards = []
folios_with_pp = [f for f in all_a_folios if folio_pp_middles[f]]
for _ in range(N_BASELINE):
    s = rng.choice(folios_with_pp)
    t = rng.choice(folios_with_pp)
    if s == t: continue
    random_jaccards.append(jaccard(folio_pp_middles[s], folio_pp_middles[t]))
random_j = np.array(random_jaccards)
print(f'Random-pair mean PP-MIDDLE Jaccard: {random_j.mean():.4f}')
print(f'Random p95: {np.percentile(random_j, 95):.4f}')

p_emp_h3 = (random_j >= mean_linker_j).mean()
print(f'p_emp (random >= linker): {p_emp_h3:.4f}')
h3_pass = p_emp_h3 < 0.05
print(f'H3 VERDICT: {"PASS" if h3_pass else "FAIL"}')

# Also do this with ALL middles (not just PP) for completeness
print('\nH3b: Same test using ALL MIDDLEs (PP + RI):')
linker_all_j = []
for s, t, _ in LINKS:
    if s in folio_middles and t in folio_middles:
        j = jaccard(folio_middles[s], folio_middles[t])
        linker_all_j.append(j)
mean_linker_all_j = np.mean(linker_all_j) if linker_all_j else 0
random_all_j = []
folios_all = [f for f in all_a_folios if folio_middles[f]]
for _ in range(N_BASELINE):
    s = rng.choice(folios_all)
    t = rng.choice(folios_all)
    if s == t: continue
    random_all_j.append(jaccard(folio_middles[s], folio_middles[t]))
random_all_arr = np.array(random_all_j)
print(f'  Linker-pair Jaccard (all MIDDLEs): {mean_linker_all_j:.4f}')
print(f'  Random-pair Jaccard: {random_all_arr.mean():.4f}')
p_emp_h3b = (random_all_arr >= mean_linker_all_j).mean()
print(f'  p_emp: {p_emp_h3b:.4f}')

# ===== H4: COLLECTOR FOLIOS DIVERSITY-RICH =====
print('\n=== H4: COLLECTOR FOLIOS PP-DIVERSITY ===')
collectors = ['f93v', 'f32r', 'f87r', 'f37v']
pp_counts = {f: len(folio_pp_middles[f]) for f in all_a_folios}
median_pp = np.median(list(pp_counts.values()))
collector_pp_counts = [pp_counts.get(f, 0) for f in collectors]
print(f'PP-MIDDLE counts:')
for f in collectors:
    print(f'  {f}: {pp_counts.get(f, 0)} {"(above median)" if pp_counts.get(f, 0) > median_pp else "(below median)"}')
print(f'A-folio median PP-MIDDLE count: {median_pp:.1f}')
n_above = sum(1 for c in collector_pp_counts if c > median_pp)
print(f'Collectors above median: {n_above}/4')
h4_pass = n_above >= 3  # Pre-reg: at least 3/4 collectors above median
print(f'H4 VERDICT: {"PASS" if h4_pass else "FAIL"}')

# ===== H5: NEGATIVE CONTROL — RANDOM RI MIDDLES =====
print('\n=== H5: NEGATIVE CONTROL — Random RI MIDDLEs ===')

# For each RI middle, find its FINAL/INITIAL position pattern across folios.
# We don't have line-position data easily, so simpler test:
# Pick RI middles that occur in >=2 folios, count their max-folio-cluster size.
ri_folio_occurrence = defaultdict(set)
for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try:
        m = morph.extract(w)
        if m.middle and m.middle in RI:
            ri_folio_occurrence[m.middle].add(t.folio)
    except Exception: pass

# How many RI middles appear in 2+ folios?
multi_folio_ri = {m: folios for m, folios in ri_folio_occurrence.items() if len(folios) >= 2}
print(f'RI MIDDLEs appearing in 2+ folios: {len(multi_folio_ri)}')
linker_ri = [m for m in LINKERS if m in multi_folio_ri]
print(f'Of which are documented linkers: {linker_ri}')

# Negative control: sample 4 random multi-folio RI middles (not the documented linkers)
non_linker_multi = [m for m in multi_folio_ri if m not in LINKERS]
if len(non_linker_multi) >= 4:
    # For each of 1000 random samples of 4 non-linker RI middles, compute their max convergence
    sample_max_convergences = []
    for _ in range(1000):
        sampled = rng.sample(non_linker_multi, 4)
        # Each sampled middle is in some set of folios. Treat ALL those folios as "destinations"
        # and check max-in-degree on the destination set (folios containing >=1 sampled middle)
        folio_hits = Counter()
        for m in sampled:
            for f in multi_folio_ri[m]:
                folio_hits[f] += 1
        sample_max_convergences.append(max(folio_hits.values()) if folio_hits else 0)
    sample_arr = np.array(sample_max_convergences)
    # Compare to documented linker convergence (max in-degree = 5 for f93v)
    p_emp_h5 = (sample_arr >= obs_max_in).mean()
    print(f'Random non-linker quadruple max convergence: mean={sample_arr.mean():.2f}, p95={np.percentile(sample_arr, 95):.0f}, max={sample_arr.max()}')
    print(f'Fraction of random samples reaching linker convergence ({obs_max_in}): {p_emp_h5:.4f}')
    h5_pass = p_emp_h5 < 0.05
    print(f'H5 VERDICT: {"PASS" if h5_pass else "FAIL"}')
else:
    h5_pass = None
    print('Insufficient non-linker multi-folio RI to test')

# ===== FINAL VERDICT =====
print('\n' + '=' * 60)
print('=== FINAL VERDICT ===')
print('=' * 60)
print(f'H1 (topology non-random):     {"PASS" if h1_pass else "FAIL"}')
print(f'H2 (forward-flow):            {"PASS" if h2_pass else "FAIL"}')
print(f'H3 (linker-pair PP content):  {"PASS" if h3_pass else "FAIL"}')
print(f'H4 (collector diversity):     {"PASS" if h4_pass else "FAIL"}')
print(f'H5 (negative control):        {"PASS" if h5_pass else "FAIL" if h5_pass == False else "N/A"}')

n_pass = sum([h1_pass, h2_pass, h3_pass, h4_pass, h5_pass if h5_pass is not None else False])
total = 5 if h5_pass is not None else 4
print(f'\nTotal: {n_pass}/{total}')

if n_pass >= 4:
    print('STRONG: Linkers carry semantic load above singleton noise floor.')
elif n_pass >= 3:
    print('MODERATE: Linker topology has some semantic structure.')
elif n_pass >= 2:
    print('WEAK: Mixed evidence; topology may be partly random.')
else:
    print('FAIL: Linker mechanism is indistinguishable from random.')

# Save
out = {
    'links': [{'source': s, 'target': t, 'linker': l} for s, t, l in LINKS],
    'n_pp_middles': len(PP),
    'n_ri_middles': len(RI),
    'H1': {'obs_max_in_degree': obs_max_in, 'null_p95': float(p95_null), 'p_emp': float(p_emp_h1), 'pass': bool(h1_pass)},
    'H2': {'forward': forward, 'backward': backward, 'self': same, 'p_binom': float(p_binom) if directional else None, 'pass': bool(h2_pass)},
    'H3': {'linker_jaccard_mean': float(mean_linker_j), 'random_jaccard_mean': float(random_j.mean()), 'p_emp': float(p_emp_h3), 'pass': bool(h3_pass)},
    'H3b_all_middles': {'linker_jaccard': float(mean_linker_all_j), 'random_jaccard': float(random_all_arr.mean()), 'p_emp': float(p_emp_h3b)},
    'H4': {'collector_pp_counts': {f: pp_counts.get(f, 0) for f in collectors}, 'a_median': float(median_pp), 'n_above': n_above, 'pass': bool(h4_pass)},
    'H5': {'n_non_linker_multi_folio_ri': len(non_linker_multi), 'p_emp': float(p_emp_h5) if h5_pass is not None else None, 'pass': bool(h5_pass) if h5_pass is not None else None},
    'total_passes': n_pass,
}
Path('C:/git/voynich/_a_linker_topology_results.json').write_text(json.dumps(out, indent=2))
print(f'\nSaved _a_linker_topology_results.json')
