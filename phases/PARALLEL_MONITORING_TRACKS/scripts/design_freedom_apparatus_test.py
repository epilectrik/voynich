"""
Phase 494 Extension: Design Freedom vs Input Parameters
========================================================
Tests whether the ~27% irreducible AXM residual (C1169) correlates with
apparatus profile similarity.

Structural basis: C1035, C1168, C1169, C1247, C1248, C1249
"""

import json
import sys
import os
import math
import random
import functools
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

import numpy as np

APPARATUS_MARKERS = {
    'DISTILLATION': ['t', 'od', 'te', 'eol'],
    'SEALED_VESSEL': ['aii', 'ok', 'ee', 'eey', 'eeol'],
    'SUSTAINED_HEAT': ['ke', 'eeo', 'eeol', 'ee'],
    'PRECISION': ['ek', 's', 'm', 'ep'],
    'DIRECT_FIRE': ['ck', 'kc', 'te'],
}
PROFILE_NAMES = sorted(APPARATUS_MARKERS.keys())
N_PERMS = 5000

# ============================================================
# LOAD
# ============================================================
print("Loading transcript...")
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

folio_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        cat = cc.classify(m.middle)
        folio_tokens[token.folio].append({
            'middle': m.middle,
            'category': cat,
            'section': token.section,
            'line': token.line,
        })

print(f"Loaded {sum(len(v) for v in folio_tokens.values())} tokens across {len(folio_tokens)} folios")

# ============================================================
# COMPUTE PER-FOLIO: apparatus profile + self-transition rate
# ============================================================
folio_profiles = {}
folio_self_rates = {}
folio_sections = {}

for folio, toks in folio_tokens.items():
    n = len(toks)
    if n < 20:
        continue

    # Apparatus profile
    mid_counts = Counter(t['middle'] for t in toks)
    profile = {}
    for pname, markers in APPARATUS_MARKERS.items():
        marker_count = sum(mid_counts.get(m, 0) for m in markers)
        profile[pname] = marker_count / n
    folio_profiles[folio] = profile

    # Self-transition rate (within lines)
    line_cats = defaultdict(list)
    for t in toks:
        line_cats[t['line']].append(t['category'])

    n_trans = 0
    n_self = 0
    for line, cats in line_cats.items():
        for i in range(len(cats) - 1):
            n_trans += 1
            if cats[i] == cats[i+1]:
                n_self += 1

    if n_trans >= 10:
        folio_self_rates[folio] = n_self / n_trans
        folio_sections[folio] = toks[0]['section']

common_folios = sorted(set(folio_self_rates.keys()) & set(folio_profiles.keys()))
n_folios = len(common_folios)
print(f"Common folios: {n_folios}")

# ============================================================
# COMPUTE RESIDUALS (section-mean baseline)
# ============================================================
section_rates = defaultdict(list)
for f in common_folios:
    section_rates[folio_sections[f]].append(folio_self_rates[f])

section_means = {s: np.mean(v) for s, v in section_rates.items()}
print(f"\nSection mean self-transition rates:")
for sec in sorted(section_means):
    print(f"  {sec}: {section_means[sec]:.4f} (n={len(section_rates[sec])})")

residuals = np.array([folio_self_rates[f] - section_means[folio_sections[f]] for f in common_folios])
print(f"Residual std: {residuals.std():.4f}")

# ============================================================
# BUILD DISTANCE MATRICES (numpy, fast)
# ============================================================
print("\nBuilding distance matrices...")

# Apparatus profile matrix: n_folios x 5
prof_matrix = np.array([[folio_profiles[f].get(p, 0) for p in PROFILE_NAMES] for f in common_folios])

# Pairwise Euclidean distances
from scipy.spatial.distance import pdist, squareform

app_dists = pdist(prof_matrix, metric='euclidean')
res_dists = pdist(residuals.reshape(-1, 1), metric='cityblock')  # |r_i - r_j|
raw_dists = pdist(np.array([folio_self_rates[f] for f in common_folios]).reshape(-1, 1), metric='cityblock')

# ============================================================
# T3: MANTEL TEST (apparatus distance vs residual distance)
# ============================================================
print("\n" + "=" * 70)
print("T3: MANTEL TEST (apparatus ~ residual distance)")
print("=" * 70)

def mantel_r(d1, d2):
    return np.corrcoef(d1, d2)[0, 1]

observed_r = mantel_r(app_dists, res_dists)
print(f"Mantel r: {observed_r:.4f}")

# Permutation: shuffle folio labels in one matrix
rng = np.random.RandomState(42)
perm_rs = np.zeros(N_PERMS)
for i in range(N_PERMS):
    perm_idx = rng.permutation(n_folios)
    perm_res = residuals[perm_idx]
    perm_d = pdist(perm_res.reshape(-1, 1), metric='cityblock')
    perm_rs[i] = mantel_r(app_dists, perm_d)

p_mantel = np.mean(perm_rs >= observed_r)
print(f"Permutation p: {p_mantel:.4f} ({N_PERMS} perms)")
print(f"Null mean: {perm_rs.mean():.4f}, std: {perm_rs.std():.4f}")

# ============================================================
# T4: WITHIN vs BETWEEN apparatus group
# ============================================================
print("\n" + "=" * 70)
print("T4: WITHIN vs BETWEEN (dominant apparatus group)")
print("=" * 70)

dominant = [max(folio_profiles[f], key=folio_profiles[f].get) for f in common_folios]
group_labels = np.array(dominant)
unique_groups = np.unique(group_labels)

group_counts = Counter(dominant)
print(f"Groups: {dict(group_counts)}")

# Compute eta-squared
total_var = residuals.var(ddof=1)
within_ss = 0
within_n = 0
for g in unique_groups:
    mask = group_labels == g
    g_resids = residuals[mask]
    if len(g_resids) >= 2:
        within_ss += g_resids.var(ddof=1) * (len(g_resids) - 1)
        within_n += len(g_resids) - 1

within_var = within_ss / within_n if within_n > 0 else 0
eta_sq = 1 - (within_var / total_var) if total_var > 0 else 0

print(f"Total variance: {total_var:.6f}")
print(f"Within-group variance: {within_var:.6f}")
print(f"Eta-squared: {eta_sq:.4f}")

# Permutation
perm_etas = np.zeros(N_PERMS)
for i in range(N_PERMS):
    perm_labels = group_labels[rng.permutation(n_folios)]
    p_within_ss = 0
    p_within_n = 0
    for g in unique_groups:
        mask = perm_labels == g
        g_r = residuals[mask]
        if len(g_r) >= 2:
            p_within_ss += g_r.var(ddof=1) * (len(g_r) - 1)
            p_within_n += len(g_r) - 1
    pv = p_within_ss / p_within_n if p_within_n > 0 else 0
    perm_etas[i] = 1 - (pv / total_var) if total_var > 0 else 0

p_eta = np.mean(perm_etas >= eta_sq)
print(f"Permutation p: {p_eta:.4f}")

# Per-group stats
print(f"\nPer-group residual stats:")
for g in sorted(unique_groups):
    mask = group_labels == g
    g_r = residuals[mask]
    print(f"  {g:<20}: mean={g_r.mean():+.4f}, std={g_r.std():.4f}, n={len(g_r)}")

# ============================================================
# T5: RAW SELF-RATE (no residualization)
# ============================================================
print("\n" + "=" * 70)
print("T5: RAW SELF-RATE (no section residualization)")
print("=" * 70)

raw_r = mantel_r(app_dists, raw_dists)
print(f"Raw Mantel r: {raw_r:.4f}")

raw_rates = np.array([folio_self_rates[f] for f in common_folios])
perm_raw_rs = np.zeros(N_PERMS)
for i in range(N_PERMS):
    perm = raw_rates[rng.permutation(n_folios)]
    perm_d = pdist(perm.reshape(-1, 1), metric='cityblock')
    perm_raw_rs[i] = mantel_r(app_dists, perm_d)

p_raw = np.mean(perm_raw_rs >= raw_r)
print(f"Permutation p: {p_raw:.4f}")

# ============================================================
# SYNTHESIS
# ============================================================
print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)

any_pass = (p_mantel < 0.05) or (p_eta < 0.05) or (p_raw < 0.05)
verdict = 'PASS' if any_pass else 'NULL'

print(f"""
T3 MANTEL (apparatus ~ residual):  r={observed_r:.4f}, p={p_mantel:.4f} {'PASS' if p_mantel < 0.05 else 'FAIL'}
T4 WITHIN/BETWEEN (dominant group): eta²={eta_sq:.4f}, p={p_eta:.4f} {'PASS' if p_eta < 0.05 else 'FAIL'}
T5 RAW MANTEL (no residualization): r={raw_r:.4f}, p={p_raw:.4f} {'PASS' if p_raw < 0.05 else 'FAIL'}

VERDICT: {verdict}
""")

if verdict == 'NULL':
    print("Design freedom is NOT explained by apparatus profile.")
    print("C1169 stands: the residual is genuine design freedom, not input parameterization.")
else:
    print("Apparatus profile explains some residual structure!")

results = {
    'phase': '494_extension',
    'name': 'DESIGN_FREEDOM_APPARATUS_TEST',
    'n_folios': n_folios,
    'T3_mantel': {'r': round(float(observed_r), 4), 'p': round(float(p_mantel), 4),
                  'verdict': 'PASS' if p_mantel < 0.05 else 'FAIL'},
    'T4_within_between': {'eta_sq': round(float(eta_sq), 4), 'p': round(float(p_eta), 4),
                          'groups': dict(group_counts),
                          'verdict': 'PASS' if p_eta < 0.05 else 'FAIL'},
    'T5_raw_mantel': {'r': round(float(raw_r), 4), 'p': round(float(p_raw), 4),
                      'verdict': 'PASS' if p_raw < 0.05 else 'FAIL'},
    'overall_verdict': verdict,
}

output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'design_freedom_apparatus_test.json')
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Results written to {output_path}")
