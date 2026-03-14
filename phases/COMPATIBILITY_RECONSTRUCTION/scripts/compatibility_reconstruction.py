#!/usr/bin/env python3
"""
Phase 586: COMPATIBILITY_RECONSTRUCTION
Manifold Attribution via A-Native Deployment Layers

Progressive reconstruction of the discrimination manifold's 0.873 clustering
by layering A-native structural constraints:

  D0: Global frequency sampling (baseline)
  D1: Section-conditioned frequency
  D2: Folio pool restriction (uniform within pool)
  D3: Per-folio frequency weighting
  D4: PREFIX->MIDDLE selectivity (HEAD compatibility)

Uses real 972 MIDDLEs and real Currier A line scaffolding. Each model
generates simulated lines by assigning MIDDLEs to lines under progressively
tighter constraints. The co-occurrence graph from simulated lines is compared
to the real manifold via clustering coefficient and edge Jaccard.
"""

import sys, json, functools, warnings, re, time
import numpy as np
import networkx as nx
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore', category=FutureWarning)

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

N_SEEDS = 10
t0 = time.time()

# ============================================================
# Section assignment for Currier A folios
# ============================================================

def get_section(folio):
    """Map folio to manuscript section (5 groups for Currier A)"""
    match = re.search(r'\d+', folio)
    if not match:
        return 'OTHER'
    num = int(match.group())
    if num <= 11:
        return 'HERBAL_1'     # Quires 1-2
    elif num <= 25:
        return 'HERBAL_2'     # Quires 3-4
    elif num <= 38:
        return 'HERBAL_3'     # Quires 5-6
    elif num <= 66:
        return 'HERBAL_4'     # Quires 7-8+
    else:
        return 'PHARMA'       # Quires 13-16 (f87-f102)


# ============================================================
# Step 0: Extract all data from Currier A
# ============================================================

print("=" * 70)
print("Phase 586: COMPATIBILITY_RECONSTRUCTION")
print("Manifold Attribution via A-Native Deployment Layers")
print("=" * 70)

tx = Transcript()
morph = Morphology()

print("\n  Extracting Currier A data...")
tokens_by_line = defaultdict(list)
for tok in tx.currier_a():
    w = tok.word.strip()
    if not w or '*' in w or tok.placement.startswith('L'):
        continue
    m = morph.extract(w)
    mid = m.middle
    if not mid or len(mid) < 1:
        continue
    head_atom, _, _, _ = decompose_middle_hmt(mid)
    key = (tok.folio, tok.line)
    tokens_by_line[key].append({
        'prefix': m.prefix,
        'middle': mid,
        'head': head_atom,
    })

# Build line scaffold
all_middles = set()
line_scaffold = []

for (folio, line_num), toks in sorted(tokens_by_line.items()):
    middles_on_line = set()
    prefixes_on_line = []
    for t in toks:
        middles_on_line.add(t['middle'])
        prefixes_on_line.append(t['prefix'])
        all_middles.add(t['middle'])
    section = get_section(folio)
    line_scaffold.append({
        'folio': folio,
        'section': section,
        'middles': middles_on_line,
        'prefixes': prefixes_on_line,
        'n_middles': len(middles_on_line),
    })

middles = sorted(all_middles)
N = len(middles)
mid_to_idx = {m: i for i, m in enumerate(middles)}

n_folios = len(set(ls['folio'] for ls in line_scaffold))
n_sections = len(set(ls['section'] for ls in line_scaffold))
print(f"  Unique MIDDLEs: {N}")
print(f"  Lines: {len(line_scaffold)}")
print(f"  Folios: {n_folios}")
print(f"  Sections: {n_sections}")

# Section distribution
sec_counts = Counter(ls['section'] for ls in line_scaffold)
for sec in sorted(sec_counts):
    print(f"    {sec}: {sec_counts[sec]} lines")

# ============================================================
# Step 0a: Build real co-occurrence matrix (target)
# ============================================================

print("\n  Building real co-occurrence matrix...")
compat_real = np.zeros((N, N), dtype=np.int8)
for ls in line_scaffold:
    mids_list = [mid_to_idx[m] for m in ls['middles'] if m in mid_to_idx]
    for i in range(len(mids_list)):
        for j in range(i + 1, len(mids_list)):
            compat_real[mids_list[i], mids_list[j]] = 1
            compat_real[mids_list[j], mids_list[i]] = 1

real_edges = int(compat_real.sum() // 2)
real_density = real_edges / (N * (N - 1) // 2)
G_real = nx.from_numpy_array(compat_real)
real_clustering = float(nx.average_clustering(G_real))
real_transitivity = float(nx.transitivity(G_real))
print(f"  Real edges: {real_edges}, density: {real_density:.4f}")
print(f"  Real clustering: {real_clustering:.4f}, transitivity: {real_transitivity:.4f}")

# ============================================================
# Step 0b: Pre-compute frequency distributions
# ============================================================

print("\n  Pre-computing frequency distributions...")

# --- Global MIDDLE frequency ---
global_counts = Counter()
for ls in line_scaffold:
    for m in ls['middles']:
        global_counts[m] += 1
total_count = sum(global_counts.values())
global_probs = np.array([global_counts.get(m, 0) for m in middles], dtype=np.float64)
global_probs /= global_probs.sum()

# --- Per-section MIDDLE frequency ---
section_lines = defaultdict(list)
for ls in line_scaffold:
    section_lines[ls['section']].append(ls)

section_probs = {}
for sec, lines in section_lines.items():
    counts = Counter()
    for ls in lines:
        for m in ls['middles']:
            counts[m] += 1
    probs = np.array([counts.get(m, 0) for m in middles], dtype=np.float64)
    probs = probs + 1e-10  # avoid zero
    probs /= probs.sum()
    section_probs[sec] = probs

# --- Per-folio MIDDLE pool and frequency ---
folio_lines = defaultdict(list)
for ls in line_scaffold:
    folio_lines[ls['folio']].append(ls)

folio_pool_indices = {}   # folio -> sorted list of MIDDLE indices in pool
folio_pool_probs = {}     # folio -> probability array over pool (same order)

for folio, lines in folio_lines.items():
    pool = set()
    counts = Counter()
    for ls in lines:
        for m in ls['middles']:
            pool.add(m)
            counts[m] += 1
    pool_sorted = sorted(pool)
    indices = [mid_to_idx[m] for m in pool_sorted]
    total = sum(counts[m] for m in pool_sorted)
    probs = np.array([counts[m] / total for m in pool_sorted], dtype=np.float64)
    folio_pool_indices[folio] = np.array(indices, dtype=np.int32)
    folio_pool_probs[folio] = probs

pool_sizes = [len(v) for v in folio_pool_indices.values()]
print(f"  Folio pool sizes: mean={np.mean(pool_sizes):.1f}, "
      f"median={np.median(pool_sizes):.0f}, range=[{min(pool_sizes)}, {max(pool_sizes)}]")

# --- Per-MIDDLE HEAD atom ---
middle_heads = {}
for m in middles:
    head, _, _, _ = decompose_middle_hmt(m)
    middle_heads[m] = head

# --- PREFIX -> HEAD compatibility (derived from real data) ---
print("  Computing PREFIX->HEAD compatibility...")
prefix_head_obs = defaultdict(set)
for key, toks in tokens_by_line.items():
    for t in toks:
        if t['prefix'] and t['head']:
            prefix_head_obs[t['prefix']].add(t['head'])

all_heads = set()
for v in prefix_head_obs.values():
    all_heads.update(v)
n_pfx = len(prefix_head_obs)
n_heads = len(all_heads)
n_allowed = sum(len(v) for v in prefix_head_obs.values())
n_max = n_pfx * n_heads
n_forbidden = n_max - n_allowed
print(f"  PREFIXes: {n_pfx}, HEAD atoms: {n_heads}")
print(f"  Allowed PREFIX*HEAD pairs: {n_allowed}/{n_max} "
      f"({n_forbidden} forbidden, {n_forbidden/n_max*100:.1f}%)")

# Pre-build: for each folio pool, which pool positions are compatible with each PREFIX
# folio_prefix_mask[folio][prefix] = boolean array over pool positions
folio_prefix_mask = {}
for folio, pool_idx in folio_pool_indices.items():
    pool_middles = [middles[i] for i in pool_idx]
    pool_heads = [middle_heads.get(m) for m in pool_middles]
    masks = {}
    for pfx, allowed in prefix_head_obs.items():
        mask = np.array([h in allowed for h in pool_heads], dtype=bool)
        masks[pfx] = mask
    folio_prefix_mask[folio] = masks

print(f"\n  Data extraction complete ({time.time()-t0:.1f}s)")

# ============================================================
# Step 1: Generation functions
# ============================================================

def generate_lines_d0(scaffold, rng):
    """D0: Global frequency sampling"""
    simulated = []
    for ls in scaffold:
        n = ls['n_middles']
        if n <= 0:
            simulated.append(set())
            continue
        n = min(n, N)
        chosen = rng.choice(N, size=n, replace=False, p=global_probs)
        simulated.append(set(int(x) for x in chosen))
    return simulated


def generate_lines_d1(scaffold, rng):
    """D1: Section-conditioned frequency"""
    simulated = []
    for ls in scaffold:
        n = ls['n_middles']
        if n <= 0:
            simulated.append(set())
            continue
        n = min(n, N)
        probs = section_probs.get(ls['section'], global_probs)
        chosen = rng.choice(N, size=n, replace=False, p=probs)
        simulated.append(set(int(x) for x in chosen))
    return simulated


def generate_lines_d2(scaffold, rng):
    """D2: Folio pool restriction (uniform within pool)"""
    simulated = []
    for ls in scaffold:
        n = ls['n_middles']
        folio = ls['folio']
        pool = folio_pool_indices.get(folio)
        if n <= 0 or pool is None or len(pool) == 0:
            simulated.append(set())
            continue
        n = min(n, len(pool))
        chosen_local = rng.choice(len(pool), size=n, replace=False)
        simulated.append(set(int(pool[i]) for i in chosen_local))
    return simulated


def generate_lines_d3(scaffold, rng):
    """D3: Folio pool restriction + per-folio frequency weighting"""
    simulated = []
    for ls in scaffold:
        n = ls['n_middles']
        folio = ls['folio']
        pool = folio_pool_indices.get(folio)
        probs = folio_pool_probs.get(folio)
        if n <= 0 or pool is None or len(pool) == 0:
            simulated.append(set())
            continue
        n = min(n, len(pool))
        chosen_local = rng.choice(len(pool), size=n, replace=False, p=probs)
        simulated.append(set(int(pool[i]) for i in chosen_local))
    return simulated


def generate_lines_d4(scaffold, rng):
    """D4: Folio pool + frequency + PREFIX selectivity"""
    simulated = []
    for ls in scaffold:
        n = ls['n_middles']
        folio = ls['folio']
        pool = folio_pool_indices.get(folio)
        base_probs = folio_pool_probs.get(folio)
        prefixes = ls['prefixes']
        masks = folio_prefix_mask.get(folio, {})

        if n <= 0 or pool is None or len(pool) == 0:
            simulated.append(set())
            continue
        n = min(n, len(pool))

        chosen = set()
        used_local = set()  # track used pool positions

        for pos in range(n):
            # Determine available pool positions (not yet used)
            available = np.array([i for i in range(len(pool)) if i not in used_local])
            if len(available) == 0:
                break

            # Get PREFIX for this position
            pfx = prefixes[pos] if pos < len(prefixes) else None

            # Apply PREFIX->HEAD filter
            if pfx and pfx in masks:
                mask = masks[pfx]
                compat_avail = np.array([i for i in available if mask[i]])
                if len(compat_avail) == 0:
                    compat_avail = available  # fallback
            else:
                compat_avail = available

            # Build probability distribution
            local_probs = np.array([base_probs[i] for i in compat_avail])
            s = local_probs.sum()
            if s > 0:
                local_probs /= s
            else:
                local_probs = np.ones(len(compat_avail)) / len(compat_avail)

            # Sample one
            chosen_local_idx = rng.choice(len(compat_avail), p=local_probs)
            pool_pos = compat_avail[chosen_local_idx]
            chosen.add(int(pool[pool_pos]))
            used_local.add(pool_pos)

        simulated.append(chosen)
    return simulated


# ============================================================
# Step 2: Metrics computation
# ============================================================

def compute_metrics(simulated_lines, compat_real, N):
    """Compute clustering, edge Jaccard, and other metrics."""
    compat = np.zeros((N, N), dtype=np.int8)
    for line_set in simulated_lines:
        mids_list = sorted(line_set)
        for i in range(len(mids_list)):
            for j in range(i + 1, len(mids_list)):
                compat[mids_list[i], mids_list[j]] = 1
                compat[mids_list[j], mids_list[i]] = 1

    edges = int(compat.sum() // 2)
    density = edges / (N * (N - 1) // 2)

    G = nx.from_numpy_array(compat)
    clustering = nx.average_clustering(G)
    transitivity = nx.transitivity(G)

    # Vectorized edge overlap
    upper = np.triu_indices(N, k=1)
    real_flat = compat_real[upper]
    pred_flat = compat[upper]

    tp = int(np.sum((real_flat == 1) & (pred_flat == 1)))
    fp = int(np.sum((real_flat == 0) & (pred_flat == 1)))
    fn = int(np.sum((real_flat == 1) & (pred_flat == 0)))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    jaccard = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0

    return {
        'edges': edges,
        'density': float(density),
        'clustering': float(clustering),
        'transitivity': float(transitivity),
        'tp': tp, 'fp': fp, 'fn': fn,
        'precision': float(precision),
        'recall': float(recall),
        'jaccard': float(jaccard),
    }


# ============================================================
# Step 3: Run all models
# ============================================================

models = [
    ('D0', 'Global frequency', generate_lines_d0),
    ('D1', '+Section conditioning', generate_lines_d1),
    ('D2', '+Folio pool (uniform)', generate_lines_d2),
    ('D3', '+Folio pool (weighted)', generate_lines_d3),
    ('D4', '+PREFIX selectivity', generate_lines_d4),
]

all_results = {}

for model_name, description, gen_func in models:
    t1 = time.time()
    print(f"\n{'='*70}")
    print(f"  Model {model_name}: {description}")
    print(f"{'='*70}")

    seed_results = []
    for seed in range(N_SEEDS):
        rng = np.random.RandomState(42 + seed)
        simulated = gen_func(line_scaffold, rng)
        metrics = compute_metrics(simulated, compat_real, N)
        seed_results.append(metrics)

        if seed == 0:
            print(f"    Seed 0: clustering={metrics['clustering']:.4f}, "
                  f"jaccard={metrics['jaccard']:.4f}, "
                  f"edges={metrics['edges']}, density={metrics['density']:.4f}")

    # Aggregate across seeds
    agg = {}
    for key in seed_results[0]:
        values = [r[key] for r in seed_results]
        agg[f'{key}_mean'] = float(np.mean(values))
        agg[f'{key}_std'] = float(np.std(values))

    all_results[model_name] = {
        'description': description,
        'aggregate': agg,
        'seeds': seed_results,
    }

    elapsed = time.time() - t1
    print(f"    Mean: clustering={agg['clustering_mean']:.4f} +/- {agg['clustering_std']:.4f}")
    print(f"    Mean: jaccard={agg['jaccard_mean']:.4f} +/- {agg['jaccard_std']:.4f}")
    print(f"    Mean: edges={agg['edges_mean']:.0f} +/- {agg['edges_std']:.0f}")
    print(f"    Mean: density={agg['density_mean']:.4f} +/- {agg['density_std']:.4f}")
    print(f"    Mean: precision={agg['precision_mean']:.4f}, recall={agg['recall_mean']:.4f}")
    print(f"    ({elapsed:.1f}s)")

# ============================================================
# Step 4: Summary and verdicts
# ============================================================

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

header = (f"  {'Model':<6s}  {'Rule':<28s}  {'Clustering':>11s}  "
          f"{'Jaccard':>9s}  {'Precision':>10s}  {'Recall':>8s}  "
          f"{'Edges':>7s}  {'Density':>8s}")
print(f"\n{header}")
sep = f"  {'-'*6}  {'-'*28}  {'-'*11}  {'-'*9}  {'-'*10}  {'-'*8}  {'-'*7}  {'-'*8}"
print(sep)
print(f"  {'Real':<6s}  {'---':<28s}  {real_clustering:11.4f}  "
      f"{'1.0000':>9s}  {'1.0000':>10s}  {'1.0000':>8s}  "
      f"{real_edges:7d}  {real_density:8.4f}")

for model_name, _, _ in models:
    r = all_results[model_name]
    a = r['aggregate']
    print(f"  {model_name:<6s}  {r['description']:<28s}  "
          f"{a['clustering_mean']:11.4f}  "
          f"{a['jaccard_mean']:9.4f}  "
          f"{a['precision_mean']:10.4f}  "
          f"{a['recall_mean']:8.4f}  "
          f"{a['edges_mean']:7.0f}  "
          f"{a['density_mean']:8.4f}")

# Progressive increments
print(f"\n  Progressive clustering increments:")
prev_name = None
prev_c = None
increments = {}
for model_name, desc, _ in models:
    c = all_results[model_name]['aggregate']['clustering_mean']
    if prev_c is not None:
        delta = c - prev_c
        increments[model_name] = delta
        print(f"    {prev_name} -> {model_name}: "
              f"delta_clustering = {delta:+.4f}, "
              f"delta_jaccard = {all_results[model_name]['aggregate']['jaccard_mean'] - all_results[prev_name]['aggregate']['jaccard_mean']:+.4f}")
    prev_name = model_name
    prev_c = c

# Identify dominant layer
if increments:
    dominant = max(increments, key=increments.get)
    max_delta = increments[dominant]
    print(f"\n  Dominant layer: {dominant} (delta clustering = {max_delta:+.4f})")
else:
    dominant = 'NONE'
    max_delta = 0.0

# Final verdicts
d4 = all_results['D4']['aggregate']
d4_clustering = d4['clustering_mean']
d4_jaccard = d4['jaccard_mean']

print(f"\n  Final model (D4):")
print(f"    Clustering: {d4_clustering:.4f} (real: {real_clustering:.4f})")
print(f"    Edge Jaccard: {d4_jaccard:.4f}")
print(f"    Precision: {d4['precision_mean']:.4f}, Recall: {d4['recall_mean']:.4f}")

if d4_jaccard >= 0.60:
    verdict = "MANIFOLD_CLOSED"
elif d4_jaccard >= 0.30:
    verdict = "MANIFOLD_MOSTLY_EXPLAINED"
else:
    verdict = "DEPLOYMENT_INSUFFICIENT"

if d4_clustering >= 0.85:
    topo_verdict = "TOPOLOGY_REPRODUCED"
elif d4_clustering >= 0.70:
    topo_verdict = "TOPOLOGY_MOSTLY_REPRODUCED"
else:
    topo_verdict = "TOPOLOGY_NOT_REPRODUCED"

print(f"    Edge verdict: {verdict}")
print(f"    Topology verdict: {topo_verdict}")

total_time = time.time() - t0
print(f"\n  Total runtime: {total_time:.1f}s")

# ============================================================
# Save results
# ============================================================

output = {
    'phase': 586,
    'test': 'COMPATIBILITY_RECONSTRUCTION',
    'real': {
        'clustering': real_clustering,
        'transitivity': real_transitivity,
        'density': real_density,
        'edges': real_edges,
        'N': N,
        'n_lines': len(line_scaffold),
        'n_folios': n_folios,
        'n_sections': n_sections,
    },
    'models': {k: {'description': v['description'], 'aggregate': v['aggregate']}
               for k, v in all_results.items()},
    'progressive_increments': {k: float(v) for k, v in increments.items()},
    'dominant_layer': dominant,
    'dominant_delta': float(max_delta),
    'edge_verdict': verdict,
    'topology_verdict': topo_verdict,
    'd4_clustering': d4_clustering,
    'd4_jaccard': d4_jaccard,
    'n_seeds': N_SEEDS,
    'runtime_seconds': total_time,
}

results_file = Path(__file__).parent.parent / 'results' / 'compatibility_reconstruction.json'
json.dump(output, open(results_file, 'w'), indent=2)
print(f"\n  Saved to {results_file}")
