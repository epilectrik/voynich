"""Phase 592: PP Manifold Residual Characterization

Question: Is the 0.234 manifold gap (C1701) structured by HEAD domain,
category, terminal type, frame, or the bridge/dark partition?
Or is it genuinely irreducible content specificity?

Tests:
  T1: HEAD assortativity (two-gate, hub-removed, partial)
  T2: Category assortativity (two-gate, hub-removed, partial)
  T3: Terminal assortativity (two-gate, hub-removed)
  T3b: Frame (HEAD x TERMINAL) assortativity
  T4: Bridge/dark/non-pipeline edge + triangle partition
  T5: Residual edge characterization (frequency-stratified)
  T6: Community-attribute alignment (chi-squared, Cramer's V)
"""

import json, os, sys, time
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(SCRIPT_DIR, '..', '..', '..')
sys.path.insert(0, BASE)

from scripts.voynich import Transcript, Morphology, CategoryClassifier, decompose_middle_hmt

try:
    import networkx as nx
except ImportError:
    print("ERROR: networkx required")
    sys.exit(1)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def compute_assortativity(G, node_labels, attr_name='_assort_tmp'):
    """Newman's categorical assortativity coefficient."""
    nx.set_node_attributes(G, node_labels, attr_name)
    try:
        r = nx.attribute_assortativity_coefficient(G, attr_name)
    except (ZeroDivisionError, ValueError):
        r = 0.0
    return r


def permutation_null(G, node_labels, n_perm=1000, rng=None):
    """Label-permutation null for assortativity."""
    if rng is None:
        rng = np.random.default_rng(42)
    nodes = sorted(G.nodes())
    labels_array = np.array([node_labels[n] for n in nodes])
    null_values = []
    for _ in range(n_perm):
        shuffled = rng.permutation(labels_array)
        shuffled_dict = {nodes[i]: shuffled[i] for i in range(len(nodes))}
        r = compute_assortativity(G, shuffled_dict)
        null_values.append(r)
    return null_values


def hub_removed_subgraph(G, node_labels, percentile=95):
    """Remove top-percentile nodes by degree."""
    degrees = dict(G.degree())
    threshold = np.percentile(list(degrees.values()), percentile)
    keep = [n for n in G.nodes() if degrees[n] <= threshold]
    subG = G.subgraph(keep).copy()
    sub_labels = {n: node_labels[n] for n in keep}
    return subG, sub_labels


def partial_assortativity(G, primary_labels, condition_labels):
    """Weighted-average assortativity of primary within each condition group."""
    condition_groups = defaultdict(list)
    for n in G.nodes():
        condition_groups[condition_labels[n]].append(n)

    total_edges = 0
    weighted_sum = 0.0
    per_group = {}

    for cond, nodes in condition_groups.items():
        subG = G.subgraph(nodes)
        n_edges = subG.number_of_edges()
        if n_edges < 5:
            continue
        primary_set = set(primary_labels[n] for n in nodes)
        if len(primary_set) < 2:
            continue
        sub_primary = {n: primary_labels[n] for n in nodes}
        r = compute_assortativity(subG, sub_primary)
        per_group[cond] = {'r': float(r), 'n_edges': n_edges, 'n_nodes': len(nodes)}
        weighted_sum += r * n_edges
        total_edges += n_edges

    if total_edges == 0:
        return 0.0, per_group
    return weighted_sum / total_edges, per_group


def build_mixing_matrix(G, node_labels):
    """Build mixing matrix for categorical labels."""
    labels = sorted(set(node_labels[n] for n in G.nodes()))
    label_to_idx = {l: i for i, l in enumerate(labels)}
    n = len(labels)
    matrix = np.zeros((n, n), dtype=int)
    for u, v in G.edges():
        i = label_to_idx[node_labels[u]]
        j = label_to_idx[node_labels[v]]
        matrix[i, j] += 1
        matrix[j, i] += 1
    return labels, matrix


def find_triangles(G):
    """Find all triangles, return list of (u, v, w) tuples with u < v < w."""
    adj = defaultdict(set)
    for u, v in G.edges():
        adj[u].add(v)
        adj[v].add(u)

    triangles = []
    for u in G.nodes():
        for v in adj[u]:
            if v <= u:
                continue
            for w in adj[u] & adj[v]:
                if w <= v:
                    continue
                triangles.append((u, v, w))
    return triangles


def triangle_partition_analysis(G, node_classes):
    """Classify triangles by pipeline homogeneity."""
    triangles = find_triangles(G)
    homo_counts = Counter()
    mixed_count = 0
    for u, v, w in triangles:
        classes = {node_classes[u], node_classes[v], node_classes[w]}
        if len(classes) == 1:
            homo_counts[node_classes[u]] += 1
        else:
            mixed_count += 1

    total = len(triangles)
    return {
        'total_triangles': total,
        'homogeneous': dict(homo_counts),
        'homogeneous_total': sum(homo_counts.values()),
        'mixed': mixed_count,
        'homogeneous_fraction': sum(homo_counts.values()) / max(total, 1)
    }


def cramers_v(contingency_table):
    """Compute chi-squared and Cramer's V."""
    ct = np.array(contingency_table)
    # Remove all-zero rows/columns
    ct = ct[ct.sum(axis=1) > 0][:, ct.sum(axis=0) > 0]
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return 0.0, 1.0, 0.0
    chi2, p, dof, expected = chi2_contingency(ct)
    n_total = ct.sum()
    k = min(ct.shape)
    v = np.sqrt(chi2 / (n_total * max(k - 1, 1))) if n_total > 0 else 0
    return float(chi2), float(p), float(v)


def convert_numpy(obj):
    """Convert numpy types for JSON serialization."""
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj) if np.isfinite(obj) else str(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {str(k): convert_numpy(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [convert_numpy(v) for v in obj]
    return obj


# ============================================================
# MAIN
# ============================================================

def main():
    t0 = time.time()
    print("Phase 592: PP Manifold Residual Characterization")
    print("=" * 60)

    # ----------------------------------------------------------
    # 1. DATA LOADING
    # ----------------------------------------------------------
    print("\n[1] Loading data...")

    # 1a. Compatibility matrix
    compat_path = os.path.join(BASE, 'phases', 'DISCRIMINATION_SPACE_DERIVATION',
                               'results', 't1_compat_matrix.npy')
    compat = np.load(compat_path)
    N = compat.shape[0]
    print(f"  Compat matrix: {N}x{N}")

    # 1b. Build MIDDLE list + line scaffold from transcript
    tx = Transcript()
    morph = Morphology()
    all_middles = set()
    folio_line_middles = defaultdict(lambda: defaultdict(list))
    mid_freq = Counter()

    for token in tx.currier_a():
        if '*' in token.word or not token.word.strip():
            continue
        m = morph.extract(token.word)
        if m and m.middle:
            mid = m.middle
            all_middles.add(mid)
            folio_line_middles[token.folio][token.line].append(mid)
            mid_freq[mid] += 1

    middles = sorted(all_middles)
    mid_to_idx = {m: i for i, m in enumerate(middles)}
    print(f"  MIDDLEs: {len(middles)}")
    assert len(middles) == N, f"Expected {N}, got {len(middles)}"

    # Line scaffold for D3
    line_scaffold = []
    for folio in sorted(folio_line_middles):
        for line in sorted(folio_line_middles[folio], key=lambda x: (int(x) if x.isdigit() else 0, x)):
            mids_on_line = folio_line_middles[folio][line]
            unique_idx = set()
            for mid in mids_on_line:
                if mid in mid_to_idx:
                    unique_idx.add(mid_to_idx[mid])
            line_scaffold.append({'folio': folio, 'n_middles': len(unique_idx)})
    print(f"  Line scaffold: {len(line_scaffold)} lines")

    # Folio pools for D3
    folio_pool_indices = {}
    folio_pool_probs = {}
    for folio, lines_dict in folio_line_middles.items():
        counter = Counter()
        for line_num, mids_list in lines_dict.items():
            for mid in mids_list:
                if mid in mid_to_idx:
                    counter[mid_to_idx[mid]] += 1
        if counter:
            indices = sorted(counter.keys())
            counts = np.array([counter[i] for i in indices], dtype=float)
            probs = counts / counts.sum()
            folio_pool_indices[folio] = np.array(indices)
            folio_pool_probs[folio] = probs

    # Pre-compute MIDDLE -> folios mapping
    mid_to_folios = defaultdict(set)
    for folio, lines_dict in folio_line_middles.items():
        for line_num, mids_list in lines_dict.items():
            for mid in mids_list:
                if mid in mid_to_idx:
                    mid_to_folios[mid_to_idx[mid]].add(folio)

    mid_freq_by_idx = {i: mid_freq.get(middles[i], 0) for i in range(N)}

    # 1c. Decompose all MIDDLEs
    cc = CategoryClassifier()
    head_labels = {}
    cat_labels = {}
    term_labels = {}
    frame_labels = {}
    pipeline_labels = {}

    for i, mid in enumerate(middles):
        head, mods, term, frame = decompose_middle_hmt(mid)
        cat = cc.classify(mid)
        head_labels[i] = head if head else 'headless'
        cat_labels[i] = str(cat)
        term_labels[i] = term if term else 'bare'
        frame_labels[i] = f"{head if head else 'headless'}_{term if term else 'bare'}"

    # 1d. Bridge/dark partition
    bridge_path = os.path.join(BASE, 'phases', 'BRIDGE_MIDDLE_SELECTION_MECHANISM',
                               'results', 'bridge_selection.json')
    with open(bridge_path) as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

    dark_path = os.path.join(BASE, 'data', 'dark_pipeline_middles.json')
    with open(dark_path) as f:
        dark_data = json.load(f)
    dark_set = set(dark_data['middles'])

    for i, mid in enumerate(middles):
        if mid in bridge_set:
            pipeline_labels[i] = 'bridge'
        elif mid in dark_set:
            pipeline_labels[i] = 'dark'
        else:
            pipeline_labels[i] = 'non_pipeline'

    pipe_counts = Counter(pipeline_labels.values())
    head_counts = Counter(head_labels.values())
    cat_counts = Counter(cat_labels.values())
    term_counts = Counter(term_labels.values())
    print(f"  Pipeline: {dict(pipe_counts)}")
    print(f"  HEAD: {dict(head_counts)}")
    print(f"  Categories: {dict(cat_counts)}")
    print(f"  Terminals: {dict(term_counts)}")

    # Merge sparse frames (< 5 MIDDLEs)
    frame_counts = Counter(frame_labels.values())
    sparse_frames = {f for f, c in frame_counts.items() if c < 5}
    frame_labels_merged = {}
    for i in range(N):
        if frame_labels[i] in sparse_frames:
            frame_labels_merged[i] = 'RARE_FRAME'
        else:
            frame_labels_merged[i] = frame_labels[i]
    frame_merged_counts = Counter(frame_labels_merged.values())
    print(f"  Frames: {len(frame_counts)} raw, {len(frame_merged_counts)} after merging <5")

    # ----------------------------------------------------------
    # 2. GRAPH CONSTRUCTION
    # ----------------------------------------------------------
    print("\n[2] Building graphs...")

    # Real graph
    G_real = nx.Graph()
    G_real.add_nodes_from(range(N))
    rows, cols = np.nonzero(np.triu(compat, k=1))
    real_edge_list = list(zip(rows.tolist(), cols.tolist()))
    G_real.add_edges_from(real_edge_list)
    real_edges = set((r, c) for r, c in real_edge_list)
    n_real_edges = len(real_edges)
    real_clustering = nx.average_clustering(G_real)
    print(f"  Real graph: {n_real_edges} edges, clustering={real_clustering:.4f}")

    # D3 graph (10 seeds)
    print("  Building D3 (10 seeds)...")
    D3_SEEDS = 10
    d3_edge_counts = defaultdict(int)
    d3_assort_per_seed = {'HEAD': [], 'category': [], 'terminal': [], 'frame': []}

    axes_map = {
        'HEAD': head_labels,
        'category': cat_labels,
        'terminal': term_labels,
        'frame': frame_labels_merged
    }

    for seed in range(D3_SEEDS):
        rng = np.random.default_rng(seed + 100)
        d3_compat = np.zeros((N, N), dtype=np.int8)
        for ls in line_scaffold:
            folio = ls['folio']
            n_mid = ls['n_middles']
            pool = folio_pool_indices.get(folio)
            probs = folio_pool_probs.get(folio)
            if n_mid <= 0 or pool is None or len(pool) == 0:
                continue
            n_mid = min(n_mid, len(pool))
            chosen_local = rng.choice(len(pool), size=n_mid, replace=False, p=probs)
            selected = [int(pool[ci]) for ci in chosen_local]
            for a in range(len(selected)):
                for b in range(a + 1, len(selected)):
                    si, sj = selected[a], selected[b]
                    d3_compat[si, sj] = 1
                    d3_compat[sj, si] = 1

        # Extract edges
        r2, c2 = np.nonzero(np.triu(d3_compat, k=1))
        for r, c in zip(r2.tolist(), c2.tolist()):
            d3_edge_counts[(r, c)] += 1

        # Assortativity per seed
        G_d3_seed = nx.Graph()
        G_d3_seed.add_nodes_from(range(N))
        G_d3_seed.add_edges_from(zip(r2.tolist(), c2.tolist()))
        for axis_name, labels in axes_map.items():
            d3_assort_per_seed[axis_name].append(compute_assortativity(G_d3_seed, labels))

        print(f"    Seed {seed}: {len(r2)} edges")

    # D3 majority graph (>= 5/10 seeds)
    MAJORITY = D3_SEEDS // 2
    G_d3 = nx.Graph()
    G_d3.add_nodes_from(range(N))
    d3_edges = set()
    for (i, j), count in d3_edge_counts.items():
        if count >= MAJORITY:
            G_d3.add_edge(i, j)
            d3_edges.add((i, j))
    d3_n_edges = len(d3_edges)
    d3_clustering = nx.average_clustering(G_d3)
    print(f"  D3 majority graph: {d3_n_edges} edges, clustering={d3_clustering:.4f}")

    # Residual edges
    residual_edges = real_edges - d3_edges
    shared_edges = real_edges & d3_edges
    d3_only_edges = d3_edges - real_edges
    print(f"  Residual edges (real - D3): {len(residual_edges)}")
    print(f"  Shared edges: {len(shared_edges)}")
    print(f"  D3-only edges: {len(d3_only_edges)}")

    # Residual graph
    G_residual = nx.Graph()
    G_residual.add_nodes_from(range(N))
    G_residual.add_edges_from(residual_edges)

    # ----------------------------------------------------------
    # 3. T1-T3b: ASSORTATIVITY TESTS
    # ----------------------------------------------------------
    print("\n[3] Assortativity tests (T1-T3b)...")

    results_assort = {}
    rng_perm = np.random.default_rng(42)

    for axis_name, labels in axes_map.items():
        print(f"\n  --- {axis_name} ---")

        # Observed
        r_real = compute_assortativity(G_real, labels)
        print(f"  Real: {r_real:.4f}")

        # Gate 1: permutation null (1000 shuffles)
        null_values = permutation_null(G_real, labels, n_perm=1000, rng=rng_perm)
        null_p95 = float(np.percentile(null_values, 95))
        null_p99 = float(np.percentile(null_values, 99))
        null_mean = float(np.mean(null_values))
        null_std = float(np.std(null_values))
        p_value = float(np.mean(np.array(null_values) >= r_real))
        gate1_pass = bool(r_real > null_p95)
        print(f"  Null: mean={null_mean:.4f}, p95={null_p95:.4f}, p={p_value:.4f}")
        print(f"  Gate 1: {'PASS' if gate1_pass else 'FAIL'}")

        # Gate 2: real > max(D3 seeds)?
        d3_vals = d3_assort_per_seed[axis_name]
        d3_max = max(d3_vals)
        d3_mean = float(np.mean(d3_vals))
        d3_std = float(np.std(d3_vals))
        excess = r_real - d3_mean
        gate2_pass = bool(r_real > d3_max)
        print(f"  D3: mean={d3_mean:.4f}, max={d3_max:.4f}")
        print(f"  Excess: {excess:.4f}")
        print(f"  Gate 2 (real > D3 max): {'PASS' if gate2_pass else 'FAIL'}")

        # Hub-removed robustness
        G_hub, labels_hub = hub_removed_subgraph(G_real, labels)
        r_hub = compute_assortativity(G_hub, labels_hub) if G_hub.number_of_edges() > 0 else 0.0
        print(f"  Hub-removed: {r_hub:.4f} ({G_hub.number_of_nodes()} nodes, {G_hub.number_of_edges()} edges)")

        # Residual graph assortativity
        r_residual = compute_assortativity(G_residual, labels)
        print(f"  Residual graph: {r_residual:.4f}")

        # Mixing matrix
        mix_labels, mix_matrix = build_mixing_matrix(G_real, labels)

        results_assort[axis_name] = {
            'real_assortativity': float(r_real),
            'null_mean': null_mean, 'null_std': null_std,
            'null_p95': null_p95, 'null_p99': null_p99,
            'p_value': p_value,
            'gate1_pass': gate1_pass,
            'd3_mean': d3_mean, 'd3_std': d3_std, 'd3_max': float(d3_max),
            'excess_over_d3': float(excess),
            'gate2_pass': gate2_pass,
            'both_gates_pass': bool(gate1_pass and gate2_pass),
            'hub_removed_assortativity': float(r_hub),
            'hub_removed_nodes': G_hub.number_of_nodes(),
            'hub_removed_edges': G_hub.number_of_edges(),
            'residual_assortativity': float(r_residual),
            'mixing_labels': mix_labels,
            'mixing_matrix': mix_matrix.tolist()
        }

    # Partial assortativity
    print("\n  --- Partial assortativity ---")
    partial_head_given_cat, head_per_cat = partial_assortativity(G_real, head_labels, cat_labels)
    print(f"  HEAD | category: {partial_head_given_cat:.4f}")

    partial_cat_given_head, cat_per_head = partial_assortativity(G_real, cat_labels, head_labels)
    print(f"  Category | HEAD: {partial_cat_given_head:.4f}")

    results_assort['partial'] = {
        'head_given_category': float(partial_head_given_cat),
        'head_per_category_group': convert_numpy(head_per_cat),
        'category_given_head': float(partial_cat_given_head),
        'category_per_head_group': convert_numpy(cat_per_head)
    }

    # Frequency-stratified assortativity
    print("\n  --- Frequency stratification ---")
    freq_values = [mid_freq_by_idx[i] for i in range(N)]
    freq_median = float(np.median(freq_values))
    high_freq_nodes = [i for i in range(N) if mid_freq_by_idx[i] > freq_median]
    low_freq_nodes = [i for i in range(N) if mid_freq_by_idx[i] <= freq_median]

    freq_strat_assort = {}
    for stratum_name, nodes in [('high_freq', high_freq_nodes), ('low_freq', low_freq_nodes)]:
        subG = G_real.subgraph(nodes).copy()
        stratum_results = {'n_nodes': len(nodes), 'n_edges': subG.number_of_edges()}
        for axis_name, labels in axes_map.items():
            sub_labels = {n: labels[n] for n in nodes}
            if subG.number_of_edges() > 0 and len(set(sub_labels.values())) >= 2:
                r = compute_assortativity(subG, sub_labels)
            else:
                r = 0.0
            stratum_results[axis_name] = float(r)
        freq_strat_assort[stratum_name] = stratum_results
        print(f"  {stratum_name}: {stratum_results}")

    results_assort['frequency_stratified'] = freq_strat_assort

    # ----------------------------------------------------------
    # 4. T4: PIPELINE PARTITION
    # ----------------------------------------------------------
    print("\n[4] T4: Pipeline partition...")

    # Edge partition
    pair_type_counts = Counter()
    for i, j in real_edges:
        pair = tuple(sorted([pipeline_labels[i], pipeline_labels[j]]))
        pair_type_counts[pair] += 1

    d3_pair_counts = Counter()
    for i, j in d3_edges:
        pair = tuple(sorted([pipeline_labels[i], pipeline_labels[j]]))
        d3_pair_counts[pair] += 1

    residual_pair_counts = Counter()
    for i, j in residual_edges:
        pair = tuple(sorted([pipeline_labels[i], pipeline_labels[j]]))
        residual_pair_counts[pair] += 1

    print(f"  Real edge partition: {dict(pair_type_counts)}")
    print(f"  Residual edge partition: {dict(residual_pair_counts)}")

    # Triangle partition
    print("  Counting triangles...")
    tri_analysis = triangle_partition_analysis(G_real, pipeline_labels)
    print(f"  Triangles: {tri_analysis['total_triangles']} total, "
          f"{tri_analysis['homogeneous_total']} homo ({tri_analysis['homogeneous_fraction']:.3f})")
    print(f"  Homogeneous by class: {tri_analysis['homogeneous']}")

    # Expected pipeline partition under D0 (global frequency)
    # Just compare real vs D3 partition
    results_t4 = {
        'real_edge_partition': {str(k): v for k, v in pair_type_counts.items()},
        'd3_edge_partition': {str(k): v for k, v in d3_pair_counts.items()},
        'residual_edge_partition': {str(k): v for k, v in residual_pair_counts.items()},
        'triangle_analysis': tri_analysis,
        'pipeline_node_counts': dict(pipe_counts)
    }

    # ----------------------------------------------------------
    # 5. T5: RESIDUAL EDGE CHARACTERIZATION
    # ----------------------------------------------------------
    print("\n[5] T5: Residual edge characterization...")

    residual_same_head = 0
    residual_same_cat = 0
    residual_same_term = 0
    residual_head_pairs = Counter()
    residual_cat_pairs = Counter()
    residual_endpoint_freqs = []

    for i, j in residual_edges:
        hp = tuple(sorted([head_labels[i], head_labels[j]]))
        cp = tuple(sorted([cat_labels[i], cat_labels[j]]))
        residual_head_pairs[hp] += 1
        residual_cat_pairs[cp] += 1
        if head_labels[i] == head_labels[j]:
            residual_same_head += 1
        if cat_labels[i] == cat_labels[j]:
            residual_same_cat += 1
        if term_labels[i] == term_labels[j]:
            residual_same_term += 1
        residual_endpoint_freqs.append((mid_freq_by_idx[i] + mid_freq_by_idx[j]) / 2)

    # Same fractions for real graph
    real_same_head = sum(1 for i, j in real_edges if head_labels[i] == head_labels[j])
    real_same_cat = sum(1 for i, j in real_edges if cat_labels[i] == cat_labels[j])
    real_same_term = sum(1 for i, j in real_edges if term_labels[i] == term_labels[j])

    n_resid = len(residual_edges)
    print(f"  Residual: {n_resid} edges")
    print(f"  Same-HEAD: resid={residual_same_head / max(n_resid, 1):.3f} vs real={real_same_head / n_real_edges:.3f}")
    print(f"  Same-cat:  resid={residual_same_cat / max(n_resid, 1):.3f} vs real={real_same_cat / n_real_edges:.3f}")
    print(f"  Same-term: resid={residual_same_term / max(n_resid, 1):.3f} vs real={real_same_term / n_real_edges:.3f}")

    # Frequency-stratified residual
    if residual_endpoint_freqs:
        freq_quartiles = np.percentile(residual_endpoint_freqs, [25, 50, 75])
    else:
        freq_quartiles = np.array([0, 0, 0])

    freq_strata_edges = {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []}
    for idx, (i, j) in enumerate(residual_edges):
        avg_freq = residual_endpoint_freqs[idx]
        if avg_freq <= freq_quartiles[0]:
            freq_strata_edges['Q1'].append((i, j))
        elif avg_freq <= freq_quartiles[1]:
            freq_strata_edges['Q2'].append((i, j))
        elif avg_freq <= freq_quartiles[2]:
            freq_strata_edges['Q3'].append((i, j))
        else:
            freq_strata_edges['Q4'].append((i, j))

    freq_strata_results = {}
    for q, edges in freq_strata_edges.items():
        if not edges:
            continue
        same_h = sum(1 for i, j in edges if head_labels[i] == head_labels[j])
        same_c = sum(1 for i, j in edges if cat_labels[i] == cat_labels[j])
        same_t = sum(1 for i, j in edges if term_labels[i] == term_labels[j])
        n_e = len(edges)
        freq_strata_results[q] = {
            'n_edges': n_e,
            'same_head_frac': same_h / n_e,
            'same_cat_frac': same_c / n_e,
            'same_term_frac': same_t / n_e
        }
        print(f"  {q}: {n_e} edges, same_H={same_h / n_e:.3f}, same_cat={same_c / n_e:.3f}, same_T={same_t / n_e:.3f}")

    # Folio concentration
    folio_edge_counts = Counter()
    for i, j in residual_edges:
        shared_f = mid_to_folios[i] & mid_to_folios[j]
        for f in shared_f:
            folio_edge_counts[f] += 1
    top_folios = folio_edge_counts.most_common(10)
    print(f"  Top folios: {top_folios[:5]}")

    results_t5 = {
        'n_residual_edges': n_resid,
        'n_shared_edges': len(shared_edges),
        'n_d3_only_edges': len(d3_only_edges),
        'same_head_frac_residual': residual_same_head / max(n_resid, 1),
        'same_cat_frac_residual': residual_same_cat / max(n_resid, 1),
        'same_term_frac_residual': residual_same_term / max(n_resid, 1),
        'same_head_frac_real': real_same_head / n_real_edges,
        'same_cat_frac_real': real_same_cat / n_real_edges,
        'same_term_frac_real': real_same_term / n_real_edges,
        'head_pair_top20': {str(k): v for k, v in residual_head_pairs.most_common(20)},
        'cat_pair_top20': {str(k): v for k, v in residual_cat_pairs.most_common(20)},
        'mean_endpoint_freq': float(np.mean(residual_endpoint_freqs)) if residual_endpoint_freqs else 0,
        'median_endpoint_freq': float(np.median(residual_endpoint_freqs)) if residual_endpoint_freqs else 0,
        'frequency_quartiles': freq_quartiles.tolist(),
        'frequency_stratified': freq_strata_results,
        'top_folios': [[f, c] for f, c in top_folios]
    }

    # ----------------------------------------------------------
    # 6. T6: COMMUNITY-ATTRIBUTE ALIGNMENT
    # ----------------------------------------------------------
    print("\n[6] T6: Community-attribute alignment...")

    # Re-derive communities: config-model subtracted Louvain
    degrees = np.array([G_real.degree(i) for i in range(N)])
    m_edges = G_real.number_of_edges()

    G_mod = nx.Graph()
    G_mod.add_nodes_from(range(N))
    for i, j in real_edges:
        weight = 1.0 - degrees[i] * degrees[j] / (2 * m_edges)
        if weight > 0:
            G_mod.add_edge(i, j, weight=weight)
    print(f"  Modularity graph: {G_mod.number_of_edges()} edges")

    communities_raw = nx.community.louvain_communities(G_mod, weight='weight', seed=42, resolution=1.0)
    communities = sorted(communities_raw, key=len, reverse=True)
    community_sizes = [len(c) for c in communities]
    print(f"  Communities: {len(communities)} (sizes: {community_sizes[:6]})")

    community_labels = {}
    for cidx, comm in enumerate(communities):
        for node in comm:
            community_labels[node] = cidx

    n_communities = min(len(communities), 10)

    # Community x HEAD
    head_types = sorted(set(head_labels.values()))
    head_ct = np.zeros((n_communities, len(head_types)), dtype=int)
    for node in range(N):
        c = community_labels[node]
        if c < n_communities:
            head_ct[c, head_types.index(head_labels[node])] += 1
    chi2_h, p_h, v_h = cramers_v(head_ct)
    print(f"  Comm x HEAD: chi2={chi2_h:.1f}, p={p_h:.2e}, V={v_h:.3f}")

    # Community x category
    cat_types = sorted(set(cat_labels.values()))
    cat_ct = np.zeros((n_communities, len(cat_types)), dtype=int)
    for node in range(N):
        c = community_labels[node]
        if c < n_communities:
            cat_ct[c, cat_types.index(cat_labels[node])] += 1
    chi2_c, p_c, v_c = cramers_v(cat_ct)
    print(f"  Comm x category: chi2={chi2_c:.1f}, p={p_c:.2e}, V={v_c:.3f}")

    # Community x terminal
    term_types = sorted(set(term_labels.values()))
    term_ct = np.zeros((n_communities, len(term_types)), dtype=int)
    for node in range(N):
        c = community_labels[node]
        if c < n_communities:
            term_ct[c, term_types.index(term_labels[node])] += 1
    chi2_t, p_t, v_t = cramers_v(term_ct)
    print(f"  Comm x terminal: chi2={chi2_t:.1f}, p={p_t:.2e}, V={v_t:.3f}")

    # Community x pipeline
    pipe_types = sorted(set(pipeline_labels.values()))
    pipe_ct = np.zeros((n_communities, len(pipe_types)), dtype=int)
    for node in range(N):
        c = community_labels[node]
        if c < n_communities:
            pipe_ct[c, pipe_types.index(pipeline_labels[node])] += 1
    chi2_p, p_p, v_p = cramers_v(pipe_ct)
    print(f"  Comm x pipeline: chi2={chi2_p:.1f}, p={p_p:.2e}, V={v_p:.3f}")

    # Community x frame
    frame_types = sorted(set(frame_labels_merged.values()))
    frame_ct = np.zeros((n_communities, len(frame_types)), dtype=int)
    for node in range(N):
        c = community_labels[node]
        if c < n_communities:
            frame_ct[c, frame_types.index(frame_labels_merged[node])] += 1
    chi2_f, p_f, v_f = cramers_v(frame_ct)
    print(f"  Comm x frame: chi2={chi2_f:.1f}, p={p_f:.2e}, V={v_f:.3f}")

    results_t6 = {
        'n_communities': len(communities),
        'community_sizes': community_sizes,
        'head': {'chi2': chi2_h, 'p': p_h, 'cramers_v': v_h,
                 'contingency': head_ct.tolist(), 'types': head_types},
        'category': {'chi2': chi2_c, 'p': p_c, 'cramers_v': v_c,
                     'contingency': cat_ct.tolist(), 'types': cat_types},
        'terminal': {'chi2': chi2_t, 'p': p_t, 'cramers_v': v_t,
                     'contingency': term_ct.tolist(), 'types': term_types},
        'pipeline': {'chi2': chi2_p, 'p': p_p, 'cramers_v': v_p,
                     'contingency': pipe_ct.tolist(), 'types': pipe_types},
        'frame': {'chi2': chi2_f, 'p': p_f, 'cramers_v': v_f}
    }

    # ----------------------------------------------------------
    # 7. DECISION LOGIC
    # ----------------------------------------------------------
    print("\n[7] Decision logic...")

    passing_axes = []
    for axis_name in ['HEAD', 'category', 'terminal', 'frame']:
        res = results_assort[axis_name]
        g1 = 'PASS' if res['gate1_pass'] else 'FAIL'
        g2 = 'PASS' if res['gate2_pass'] else 'FAIL'
        both = res['both_gates_pass']
        print(f"  {axis_name}: G1={g1}, G2={g2}, real={res['real_assortativity']:.4f}, "
              f"null_p95={res['null_p95']:.4f}, D3_max={res['d3_max']:.4f}")
        if both:
            passing_axes.append(axis_name)

    partial = results_assort['partial']
    head_partial = partial['head_given_category']
    cat_partial = partial['category_given_head']
    print(f"  Partial: HEAD|cat={head_partial:.4f}, cat|HEAD={cat_partial:.4f}")

    # Verdict
    if len(passing_axes) == 0:
        verdict = 'CONTENT_IRREDUCIBLE'
        verdict_detail = 'No compositional axis passes both significance gates'
    elif len(passing_axes) == 1:
        axis = passing_axes[0]
        verdict = f'{axis.upper()}_STRUCTURED'
        verdict_detail = f'Single axis ({axis}) passes both gates'
    else:
        # Multiple axes -- use partial assortativity to decompose
        if 'HEAD' in passing_axes and 'category' in passing_axes:
            if abs(head_partial) > 0.01 and abs(cat_partial) <= 0.01:
                verdict = 'HEAD_STRUCTURED'
                verdict_detail = (f'HEAD drives category: HEAD|cat={head_partial:.4f} (independent), '
                                  f'cat|HEAD={cat_partial:.4f} (dependent)')
            elif abs(cat_partial) > 0.01 and abs(head_partial) <= 0.01:
                verdict = 'CATEGORY_STRUCTURED'
                verdict_detail = (f'Category independent of HEAD: cat|HEAD={cat_partial:.4f}, '
                                  f'HEAD|cat={head_partial:.4f}')
            else:
                # Both partials significant -- check frame
                if 'frame' in passing_axes:
                    frame_r = results_assort['frame']['real_assortativity']
                    head_r = results_assort['HEAD']['real_assortativity']
                    term_r = results_assort['terminal'].get('real_assortativity', 0)
                    if frame_r > head_r and frame_r > term_r:
                        verdict = 'FRAME_STRUCTURED'
                        verdict_detail = (f'Frame ({frame_r:.4f}) > HEAD ({head_r:.4f}) + '
                                          f'terminal ({term_r:.4f})')
                    else:
                        verdict = 'MULTI_AXIS'
                        verdict_detail = f'Axes: {passing_axes}, HEAD|cat={head_partial:.4f}, cat|HEAD={cat_partial:.4f}'
                else:
                    verdict = 'MULTI_AXIS'
                    verdict_detail = f'Axes: {passing_axes}, HEAD|cat={head_partial:.4f}, cat|HEAD={cat_partial:.4f}'
        else:
            if 'frame' in passing_axes:
                frame_r = results_assort['frame']['real_assortativity']
                head_r = results_assort.get('HEAD', {}).get('real_assortativity', 0)
                term_r = results_assort.get('terminal', {}).get('real_assortativity', 0)
                if frame_r > head_r and frame_r > term_r:
                    verdict = 'FRAME_STRUCTURED'
                    verdict_detail = f'Frame subsumes HEAD+terminal: {frame_r:.4f}'
                else:
                    verdict = 'MULTI_AXIS'
                    verdict_detail = f'Axes: {passing_axes}'
            else:
                verdict = 'MULTI_AXIS'
                verdict_detail = f'Axes: {passing_axes}'

    print(f"\n  VERDICT: {verdict}")
    print(f"  Detail: {verdict_detail}")

    # Bridge/dark assessment (independent of verdict)
    bridge_note = ""
    resid_pipe = results_t4['residual_edge_partition']
    total_resid_pipe = sum(resid_pipe.values())
    if total_resid_pipe > 0:
        np_frac = sum(v for k, v in resid_pipe.items() if 'non_pipeline' in k) / total_resid_pipe
        bridge_note = f"Non-pipeline edges carry {np_frac:.1%} of residual"
    print(f"  {bridge_note}")

    # ----------------------------------------------------------
    # 8. OUTPUT
    # ----------------------------------------------------------
    elapsed = time.time() - t0
    print(f"\nElapsed: {elapsed:.1f}s")

    results = {
        'phase': 'PP_MANIFOLD_RESIDUAL_CHARACTERIZATION',
        'phase_number': 592,
        'question': 'Is the 0.234 manifold gap structured by compositional axes?',
        'n_middles': N,
        'n_real_edges': n_real_edges,
        'real_clustering': float(real_clustering),
        'n_d3_edges': d3_n_edges,
        'd3_clustering': float(d3_clustering),
        'n_residual_edges': len(residual_edges),
        'n_shared_edges': len(shared_edges),
        'n_d3_only_edges': len(d3_only_edges),
        'assortativity_tests': results_assort,
        't4_pipeline_partition': results_t4,
        't5_residual_characterization': results_t5,
        't6_community_alignment': results_t6,
        'passing_axes': passing_axes,
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'bridge_dark_note': bridge_note,
        'atom_compositional_note': (
            'Phase 585 logistic model includes same_head, same_term, same_category '
            'features (AUC 0.745). HEAD/terminal/category assortativity is present '
            'by construction in the atom model, but with only 6.4% edge overlap. '
            'The residual assortativity here measures specific MIDDLE-MIDDLE patterns '
            'beyond general compositional statistics.'
        ),
        'elapsed_seconds': elapsed
    }

    out_path = os.path.join(SCRIPT_DIR, '..', 'results', 'pp_manifold_residual_results.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(convert_numpy(results), f, indent=2)
    print(f"\nResults -> {out_path}")


if __name__ == '__main__':
    main()
