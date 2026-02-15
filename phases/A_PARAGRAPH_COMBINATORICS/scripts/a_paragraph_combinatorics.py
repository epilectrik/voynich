#!/usr/bin/env python3
"""
Phase 364: Currier A Paragraph-Level Combinatorial Grammar

Tests whether paragraph membership imposes MIDDLE compatibility constraints
beyond line-level incompatibility (C475/C729).

Tests:
  T1: Paragraph compatibility density (H1, H2)
  T2: Paragraph cluster composition (H3, H4)
  T3: Within-folio paragraph compatibility (H5, H6)
  T4: RI linker topology validation (H7)
  T5: B execution prediction (H8)

Global pass: >= 5/8 hypotheses confirmed.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from scipy import stats
from sklearn.mixture import GaussianMixture

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# === Paths ===
RESULTS_DIR = Path(__file__).parent.parent / 'results'
COMPAT_MATRIX_PATH = (Path(__file__).resolve().parents[2]
                      / 'DISCRIMINATION_SPACE_DERIVATION' / 'results' / 't1_compat_matrix.npy')
PAR_TOKENS_PATH = (Path(__file__).resolve().parents[2]
                   / 'PARAGRAPH_INTERNAL_PROFILING' / 'results' / 'a_paragraph_tokens.json')
PAR_INVENTORY_PATH = (Path(__file__).resolve().parents[2]
                      / 'PARAGRAPH_INTERNAL_PROFILING' / 'results' / 'a_paragraph_inventory.json')
MIDDLE_CLASSES_PATH = (Path(__file__).resolve().parents[2]
                       / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json')

# === Constants ===
K_RESIDUAL = 99
N_PERM = 1000
RNG_SEED = 42

# RI Linker topology (C835)
RI_LINKS = [
    {'linker': 'cthody', 'sources': ['f21r', 'f53v', 'f54r', 'f87r', 'f89v1'], 'target': 'f93v'},
    {'linker': 'ctho', 'sources': ['f27r', 'f30v', 'f42r', 'f93r'], 'target': 'f32r'},
    {'linker': 'ctheody', 'sources': ['f53v', 'f87r'], 'target': 'f87r'},
    {'linker': 'qokoiiin', 'sources': ['f89v1'], 'target': 'f37v'},
]


def reconstruct_middle_list():
    """Sorted unique MIDDLEs from Currier A (same as t4 topology)."""
    tx = Transcript()
    morph = Morphology()
    middles = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            middles.add(m.middle)
    return sorted(middles)


def build_residual_embedding(compat_matrix):
    """Spectral embedding from compatibility matrix (same as t4 topology)."""
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    res_evals = eigenvalues[1:K_RESIDUAL + 1]
    res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
    scaling = np.sqrt(np.maximum(res_evals, 0))
    return res_evecs * scaling[np.newaxis, :]


def compute_compatibility_density(middles_set, mid_to_idx, compat_matrix):
    """Fraction of MIDDLE pairs that are compatible (in compat_matrix)."""
    indexed = [mid_to_idx[m] for m in middles_set if m in mid_to_idx]
    if len(indexed) < 2:
        return None
    n_compat = 0
    n_total = 0
    for i in range(len(indexed)):
        for j in range(i + 1, len(indexed)):
            n_total += 1
            if compat_matrix[indexed[i], indexed[j]] > 0:
                n_compat += 1
    return n_compat / n_total if n_total > 0 else None


def compute_cluster_vector(middles_set, mid_to_cluster, n_clusters=5):
    """Compute cluster composition vector for a set of MIDDLEs."""
    counts = np.zeros(n_clusters)
    n_mapped = 0
    for m in middles_set:
        if m in mid_to_cluster:
            counts[mid_to_cluster[m]] += 1
            n_mapped += 1
    if n_mapped == 0:
        return None
    return counts / n_mapped


def shannon_entropy(vec):
    """Shannon entropy of a probability vector."""
    vec = vec[vec > 0]
    return -np.sum(vec * np.log2(vec))


def cosine_similarity(a, b):
    """Cosine similarity between two vectors."""
    dot = np.dot(a, b)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def main():
    print("=" * 60)
    print("Phase 364: Currier A Paragraph-Level Combinatorial Grammar")
    print("=" * 60)

    # ================================================================
    # S1: Build paragraph MIDDLE inventories
    # ================================================================
    print("\n[S1] Building paragraph MIDDLE inventories...")
    morph = Morphology()

    with open(PAR_TOKENS_PATH, 'r', encoding='utf-8') as f:
        par_tokens = json.load(f)

    with open(PAR_INVENTORY_PATH, 'r', encoding='utf-8') as f:
        par_inventory = json.load(f)

    par_meta = {p['par_id']: p for p in par_inventory['paragraphs']}

    # Build per-paragraph, per-line MIDDLE sets
    paragraphs = {}  # par_id -> {folio, section, lines: {line_id: set(middles)}, all_middles: set}
    for par_id, tokens in par_tokens.items():
        meta = par_meta.get(par_id, {})
        lines = defaultdict(set)
        all_middles = set()
        for tok in tokens:
            word = tok['word'].strip()
            if not word or '*' in word:
                continue
            m = morph.extract(word)
            if m.middle:
                lines[tok['line']].add(m.middle)
                all_middles.add(m.middle)
        paragraphs[par_id] = {
            'folio': meta.get('folio', tokens[0]['folio'] if tokens else ''),
            'section': meta.get('section', tokens[0]['section'] if tokens else ''),
            'ordinal': meta.get('paragraph_ordinal', 0),
            'lines': dict(lines),
            'all_middles': all_middles,
        }

    print(f"  Paragraphs loaded: {len(paragraphs)}")
    total_middles = sum(len(p['all_middles']) for p in paragraphs.values())
    print(f"  Total unique MIDDLEs across paragraphs: {total_middles}")

    # ================================================================
    # S2: Load compatibility data + cluster assignments
    # ================================================================
    print("\n[S2] Loading compatibility data...")
    compat_matrix = np.load(COMPAT_MATRIX_PATH)
    all_middles = reconstruct_middle_list()
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    n_mid = len(all_middles)
    print(f"  Compatibility matrix: {compat_matrix.shape[0]}x{compat_matrix.shape[1]}")
    print(f"  Unique MIDDLEs in matrix: {n_mid}")

    # Reproduce GMM k=5 clustering (same as t4 topology)
    print("  Running GMM k=5 clustering...")
    embedding = build_residual_embedding(compat_matrix)
    gmm = GaussianMixture(n_components=5, random_state=42, n_init=3,
                          covariance_type='diag', max_iter=300)
    labels = gmm.fit_predict(embedding)
    mid_to_cluster = {all_middles[i]: int(labels[i]) for i in range(n_mid)}
    cluster_sizes = Counter(labels)
    for c in sorted(cluster_sizes):
        print(f"    Cluster {c}: {cluster_sizes[c]} MIDDLEs")

    # Load RI/PP classification
    with open(MIDDLE_CLASSES_PATH, 'r', encoding='utf-8') as f:
        mc_data = json.load(f)
    ri_middles = set(mc_data['a_exclusive_middles'])
    pp_middles = set(mc_data['a_shared_middles'])
    print(f"  RI MIDDLEs: {len(ri_middles)}, PP MIDDLEs: {len(pp_middles)}")

    # ================================================================
    # S3: T1 - Paragraph compatibility density
    # ================================================================
    print("\n[S3] T1: Paragraph compatibility density...")
    rng = np.random.RandomState(RNG_SEED)

    # For each paragraph, compute compatibility density of cross-line MIDDLE pairs
    par_densities = {}
    par_pp_densities = {}
    for par_id, pdata in paragraphs.items():
        # Cross-line pairs: pairs where the two MIDDLEs come from different lines
        line_sets = list(pdata['lines'].values())
        if len(line_sets) < 2:
            continue

        cross_pairs_all = set()
        cross_pairs_pp = set()
        for i in range(len(line_sets)):
            for j in range(i + 1, len(line_sets)):
                for m1 in line_sets[i]:
                    for m2 in line_sets[j]:
                        if m1 != m2 and m1 in mid_to_idx and m2 in mid_to_idx:
                            pair = (min(m1, m2), max(m1, m2))
                            cross_pairs_all.add(pair)
                            if m1 in pp_middles and m2 in pp_middles:
                                cross_pairs_pp.add(pair)

        if cross_pairs_all:
            n_compat = sum(1 for m1, m2 in cross_pairs_all
                          if compat_matrix[mid_to_idx[m1], mid_to_idx[m2]] > 0)
            par_densities[par_id] = n_compat / len(cross_pairs_all)

        if cross_pairs_pp:
            n_compat_pp = sum(1 for m1, m2 in cross_pairs_pp
                             if compat_matrix[mid_to_idx[m1], mid_to_idx[m2]] > 0)
            par_pp_densities[par_id] = n_compat_pp / len(cross_pairs_pp)

    obs_mean_all = np.mean(list(par_densities.values()))
    obs_mean_pp = np.mean(list(par_pp_densities.values())) if par_pp_densities else 0
    print(f"  Paragraphs with cross-line pairs: {len(par_densities)}")
    print(f"  Observed mean compatibility density (all): {obs_mean_all:.4f}")
    print(f"  Observed mean compatibility density (PP only): {obs_mean_pp:.4f}")

    # Permutation test: shuffle lines across paragraphs within folio
    print(f"  Running permutation test ({N_PERM} perms)...")
    folio_lines = defaultdict(list)  # folio -> [(par_id, line_id, middles_set)]
    for par_id, pdata in paragraphs.items():
        if len(pdata['lines']) < 2:
            continue
        for line_id, middles in pdata['lines'].items():
            folio_lines[pdata['folio']].append((par_id, line_id, middles))

    # Pre-compute paragraph line counts for shuffling
    par_line_counts = {}
    for par_id, pdata in paragraphs.items():
        if len(pdata['lines']) >= 2:
            par_line_counts[par_id] = len(pdata['lines'])

    null_means_all = []
    null_means_pp = []
    for perm_i in range(N_PERM):
        perm_densities = []
        perm_pp_densities = []

        for folio, lines_list in folio_lines.items():
            if len(lines_list) < 2:
                continue

            # Shuffle lines within this folio
            shuffled = list(lines_list)
            rng.shuffle(shuffled)

            # Reassign to paragraphs maintaining original paragraph sizes
            folio_pars = [pid for pid in par_line_counts
                          if paragraphs[pid]['folio'] == folio]
            idx = 0
            for par_id in folio_pars:
                n_lines = par_line_counts[par_id]
                if idx + n_lines > len(shuffled):
                    break
                par_lines = [shuffled[idx + k][2] for k in range(n_lines)]
                idx += n_lines

                # Compute cross-line compatibility
                cross_all = set()
                cross_pp = set()
                for i in range(len(par_lines)):
                    for j in range(i + 1, len(par_lines)):
                        for m1 in par_lines[i]:
                            for m2 in par_lines[j]:
                                if m1 != m2 and m1 in mid_to_idx and m2 in mid_to_idx:
                                    pair = (min(m1, m2), max(m1, m2))
                                    cross_all.add(pair)
                                    if m1 in pp_middles and m2 in pp_middles:
                                        cross_pp.add(pair)

                if cross_all:
                    n_c = sum(1 for m1, m2 in cross_all
                             if compat_matrix[mid_to_idx[m1], mid_to_idx[m2]] > 0)
                    perm_densities.append(n_c / len(cross_all))

                if cross_pp:
                    n_c = sum(1 for m1, m2 in cross_pp
                             if compat_matrix[mid_to_idx[m1], mid_to_idx[m2]] > 0)
                    perm_pp_densities.append(n_c / len(cross_pp))

        if perm_densities:
            null_means_all.append(np.mean(perm_densities))
        if perm_pp_densities:
            null_means_pp.append(np.mean(perm_pp_densities))

        if (perm_i + 1) % 200 == 0:
            print(f"    Permutation {perm_i + 1}/{N_PERM}")

    null_mean_all = np.mean(null_means_all)
    null_std_all = np.std(null_means_all)
    p_all = np.mean([n >= obs_mean_all for n in null_means_all])
    z_all = (obs_mean_all - null_mean_all) / null_std_all if null_std_all > 0 else 0

    null_mean_pp = np.mean(null_means_pp) if null_means_pp else 0
    null_std_pp = np.std(null_means_pp) if null_means_pp else 0
    p_pp = np.mean([n >= obs_mean_pp for n in null_means_pp]) if null_means_pp else 1
    z_pp = (obs_mean_pp - null_mean_pp) / null_std_pp if null_std_pp > 0 else 0

    h1_pass = p_all < 0.05 and obs_mean_all > null_mean_all
    h2_pass = h1_pass and z_pp > z_all  # PP excess > all excess (only meaningful if H1 passes)

    print(f"\n  H1: Paragraphs have higher compatibility than random?")
    print(f"    Observed: {obs_mean_all:.4f}, Null: {null_mean_all:.4f} +/- {null_std_all:.4f}")
    print(f"    z = {z_all:.3f}, p = {p_all:.4f}")
    print(f"    H1: {'PASS' if h1_pass else 'FAIL'}")

    print(f"\n  H2: Excess driven by PP MIDDLEs?")
    print(f"    PP observed: {obs_mean_pp:.4f}, PP null: {null_mean_pp:.4f}")
    print(f"    z_pp = {z_pp:.3f} vs z_all = {z_all:.3f}")
    print(f"    H2: {'PASS' if h2_pass else 'FAIL'}")

    t1_results = {
        'observed_density_all': float(obs_mean_all),
        'null_density_all': float(null_mean_all),
        'null_std_all': float(null_std_all),
        'z_all': float(z_all),
        'p_all': float(p_all),
        'observed_density_pp': float(obs_mean_pp),
        'null_density_pp': float(null_mean_pp),
        'null_std_pp': float(null_std_pp),
        'z_pp': float(z_pp),
        'p_pp': float(p_pp),
        'n_paragraphs_tested': len(par_densities),
        'h1_pass': bool(h1_pass),
        'h2_pass': bool(h2_pass),
    }

    # ================================================================
    # S4: T2 - Cluster composition analysis
    # ================================================================
    print("\n[S4] T2: Cluster composition analysis...")

    par_cluster_vecs = {}
    par_entropies = {}
    for par_id, pdata in paragraphs.items():
        if len(pdata['all_middles']) < 3:
            continue
        vec = compute_cluster_vector(pdata['all_middles'], mid_to_cluster)
        if vec is not None:
            par_cluster_vecs[par_id] = vec
            par_entropies[par_id] = shannon_entropy(vec)

    obs_mean_entropy = np.mean(list(par_entropies.values()))
    print(f"  Paragraphs with cluster vectors: {len(par_cluster_vecs)}")
    print(f"  Observed mean entropy: {obs_mean_entropy:.4f}")

    # Null: random assignment of MIDDLEs to clusters (maintaining cluster proportions)
    cluster_probs = np.zeros(5)
    for c in range(5):
        cluster_probs[c] = cluster_sizes[c] / n_mid
    max_entropy = shannon_entropy(cluster_probs)
    print(f"  Maximum entropy (uniform by cluster size): {max_entropy:.4f}")

    # Permutation null: shuffle MIDDLE-to-cluster mapping
    null_entropies = []
    all_cluster_labels = list(mid_to_cluster.values())
    all_cluster_keys = list(mid_to_cluster.keys())
    for perm_i in range(N_PERM):
        perm_labels = list(all_cluster_labels)
        rng.shuffle(perm_labels)
        perm_map = {all_cluster_keys[i]: perm_labels[i] for i in range(len(all_cluster_keys))}

        perm_ents = []
        for par_id, pdata in paragraphs.items():
            if len(pdata['all_middles']) < 3:
                continue
            vec = compute_cluster_vector(pdata['all_middles'], perm_map)
            if vec is not None:
                perm_ents.append(shannon_entropy(vec))
        if perm_ents:
            null_entropies.append(np.mean(perm_ents))

    null_mean_ent = np.mean(null_entropies)
    null_std_ent = np.std(null_entropies)
    p_entropy = np.mean([n <= obs_mean_entropy for n in null_entropies])
    z_entropy = (obs_mean_entropy - null_mean_ent) / null_std_ent if null_std_ent > 0 else 0

    h3_pass = p_entropy < 0.05 and obs_mean_entropy < null_mean_ent

    print(f"\n  H3: Paragraph cluster composition has lower entropy than random?")
    print(f"    Observed: {obs_mean_entropy:.4f}, Null: {null_mean_ent:.4f} +/- {null_std_ent:.4f}")
    print(f"    z = {z_entropy:.3f}, p = {p_entropy:.4f}")
    print(f"    H3: {'PASS' if h3_pass else 'FAIL'}")

    # H4: Adjacent paragraphs more similar than non-adjacent
    print(f"\n  H4: Adjacent paragraph similarity...")
    folio_pars = defaultdict(list)
    for par_id, pdata in paragraphs.items():
        if par_id in par_cluster_vecs:
            folio_pars[pdata['folio']].append(par_id)

    # Sort within each folio by ordinal
    for folio in folio_pars:
        folio_pars[folio].sort(key=lambda pid: paragraphs[pid]['ordinal'])

    adjacent_sims = []
    nonadjacent_sims = []
    for folio, pids in folio_pars.items():
        if len(pids) < 2:
            continue
        for i in range(len(pids)):
            for j in range(i + 1, len(pids)):
                sim = cosine_similarity(par_cluster_vecs[pids[i]],
                                       par_cluster_vecs[pids[j]])
                if j == i + 1:
                    adjacent_sims.append(sim)
                else:
                    nonadjacent_sims.append(sim)

    if adjacent_sims and nonadjacent_sims:
        h4_stat, h4_p = stats.mannwhitneyu(adjacent_sims, nonadjacent_sims,
                                           alternative='greater')
        h4_pass = h4_p < 0.05
        adj_median = np.median(adjacent_sims)
        nonadj_median = np.median(nonadjacent_sims)
        print(f"    Adjacent pairs: {len(adjacent_sims)}, median sim = {adj_median:.4f}")
        print(f"    Non-adjacent pairs: {len(nonadjacent_sims)}, median sim = {nonadj_median:.4f}")
        print(f"    Mann-Whitney U = {h4_stat:.1f}, p = {h4_p:.4f}")
        print(f"    H4: {'PASS' if h4_pass else 'FAIL'}")
    else:
        h4_pass = False
        adj_median = 0
        nonadj_median = 0
        h4_p = 1.0
        h4_stat = 0
        print(f"    Insufficient data for adjacency test")
        print(f"    H4: FAIL (insufficient data)")

    t2_results = {
        'observed_mean_entropy': float(obs_mean_entropy),
        'null_mean_entropy': float(null_mean_ent),
        'null_std_entropy': float(null_std_ent),
        'z_entropy': float(z_entropy),
        'p_entropy': float(p_entropy),
        'max_entropy': float(max_entropy),
        'n_paragraphs_tested': len(par_cluster_vecs),
        'h3_pass': bool(h3_pass),
        'adjacent_pairs': len(adjacent_sims),
        'nonadjacent_pairs': len(nonadjacent_sims),
        'adjacent_median_sim': float(adj_median),
        'nonadjacent_median_sim': float(nonadj_median),
        'h4_mw_U': float(h4_stat),
        'h4_p': float(h4_p),
        'h4_pass': bool(h4_pass),
    }

    # ================================================================
    # S5: T3 - Within-folio paragraph compatibility
    # ================================================================
    print("\n[S5] T3: Within-folio paragraph compatibility...")

    # For each paragraph, get set of PP MIDDLEs that are in the compat matrix
    par_pp_sets = {}
    for par_id, pdata in paragraphs.items():
        pp_in_matrix = pdata['all_middles'] & pp_middles & set(mid_to_idx.keys())
        if pp_in_matrix:
            par_pp_sets[par_id] = pp_in_matrix

    # Compute pairwise paragraph compatibility: fraction of cross-paragraph
    # MIDDLE pairs that are compatible
    def paragraph_compatibility(set_a, set_b):
        """Fraction of cross-paragraph PP MIDDLE pairs that are compatible."""
        n_compat = 0
        n_total = 0
        for m1 in set_a:
            for m2 in set_b:
                if m1 != m2:
                    n_total += 1
                    if compat_matrix[mid_to_idx[m1], mid_to_idx[m2]] > 0:
                        n_compat += 1
        return n_compat / n_total if n_total > 0 else None

    # Build within-folio and between-folio pairs
    within_folio_compats = []
    between_folio_compats = []
    section_map = {}  # folio -> section
    for par_id, pdata in paragraphs.items():
        section_map[pdata['folio']] = pdata['section']

    folio_par_ids = defaultdict(list)
    for par_id in par_pp_sets:
        folio_par_ids[paragraphs[par_id]['folio']].append(par_id)

    # Within-folio pairs
    for folio, pids in folio_par_ids.items():
        if len(pids) < 2:
            continue
        for i in range(len(pids)):
            for j in range(i + 1, len(pids)):
                c = paragraph_compatibility(par_pp_sets[pids[i]], par_pp_sets[pids[j]])
                if c is not None:
                    within_folio_compats.append(c)

    # Between-folio pairs (sample to keep tractable)
    all_par_ids = list(par_pp_sets.keys())
    n_between_target = min(5000, len(all_par_ids) * (len(all_par_ids) - 1) // 2)
    between_pairs_sampled = set()
    while len(between_pairs_sampled) < n_between_target:
        i, j = rng.choice(len(all_par_ids), 2, replace=False)
        pid_a, pid_b = all_par_ids[i], all_par_ids[j]
        if paragraphs[pid_a]['folio'] != paragraphs[pid_b]['folio']:
            pair = (min(pid_a, pid_b), max(pid_a, pid_b))
            if pair not in between_pairs_sampled:
                between_pairs_sampled.add(pair)
                c = paragraph_compatibility(par_pp_sets[pid_a], par_pp_sets[pid_b])
                if c is not None:
                    between_folio_compats.append(c)

    within_median = np.median(within_folio_compats) if within_folio_compats else 0
    between_median = np.median(between_folio_compats) if between_folio_compats else 0
    if within_folio_compats and between_folio_compats:
        h5_stat, h5_p = stats.mannwhitneyu(within_folio_compats, between_folio_compats,
                                           alternative='greater')
    else:
        h5_stat, h5_p = 0, 1.0

    h5_pass = h5_p < 0.05

    print(f"  Within-folio pairs: {len(within_folio_compats)}, median = {within_median:.4f}")
    print(f"  Between-folio pairs: {len(between_folio_compats)}, median = {between_median:.4f}")
    print(f"  Mann-Whitney U = {h5_stat:.1f}, p = {h5_p:.6f}")
    print(f"  H5: {'PASS' if h5_pass else 'FAIL'}")

    # H6: Section-matched control
    print(f"\n  H6: Section-matched control...")
    section_between = defaultdict(list)
    for pid_a, pid_b in between_pairs_sampled:
        sec_a = paragraphs[pid_a]['section']
        sec_b = paragraphs[pid_b]['section']
        if sec_a == sec_b:
            c = paragraph_compatibility(par_pp_sets[pid_a], par_pp_sets[pid_b])
            if c is not None:
                section_between[sec_a].append(c)

    same_section_between = []
    for sec, vals in section_between.items():
        same_section_between.extend(vals)

    if within_folio_compats and same_section_between:
        h6_stat, h6_p = stats.mannwhitneyu(within_folio_compats, same_section_between,
                                           alternative='greater')
        same_sec_median = np.median(same_section_between)
    else:
        h6_stat, h6_p = 0, 1.0
        same_sec_median = 0

    h6_pass = h6_p < 0.05

    print(f"    Same-section between-folio pairs: {len(same_section_between)}, "
          f"median = {same_sec_median:.4f}")
    print(f"    Within-folio median: {within_median:.4f}")
    print(f"    Mann-Whitney U = {h6_stat:.1f}, p = {h6_p:.6f}")
    print(f"    H6: {'PASS' if h6_pass else 'FAIL'}")

    t3_results = {
        'within_folio_n': len(within_folio_compats),
        'within_folio_median': float(within_median),
        'between_folio_n': len(between_folio_compats),
        'between_folio_median': float(between_median),
        'h5_mw_U': float(h5_stat),
        'h5_p': float(h5_p),
        'h5_pass': bool(h5_pass),
        'same_section_between_n': len(same_section_between),
        'same_section_between_median': float(same_sec_median),
        'h6_mw_U': float(h6_stat),
        'h6_p': float(h6_p),
        'h6_pass': bool(h6_pass),
    }

    # ================================================================
    # S6: T4 - RI linker topology validation
    # ================================================================
    print("\n[S6] T4: RI linker topology validation...")

    # Build folio-level cluster composition vectors
    folio_cluster_vecs = {}
    for folio, pids in folio_par_ids.items():
        all_mids = set()
        for pid in pids:
            all_mids.update(paragraphs[pid]['all_middles'])
        vec = compute_cluster_vector(all_mids, mid_to_cluster)
        if vec is not None:
            folio_cluster_vecs[folio] = vec

    # Get all linked folio pairs
    linked_pairs = set()
    linked_folios = set()
    for link in RI_LINKS:
        target = link['target']
        for src in link['sources']:
            if src != target:
                pair = tuple(sorted([src, target]))
                linked_pairs.add(pair)
                linked_folios.add(src)
                linked_folios.add(target)

    # Also add source-source pairs within same linker group
    for link in RI_LINKS:
        sources = list(link['sources'])
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                pair = tuple(sorted([sources[i], sources[j]]))
                linked_pairs.add(pair)

    # Compute similarities for linked vs unlinked pairs
    linked_sims = []
    for f1, f2 in linked_pairs:
        if f1 in folio_cluster_vecs and f2 in folio_cluster_vecs:
            sim = cosine_similarity(folio_cluster_vecs[f1], folio_cluster_vecs[f2])
            linked_sims.append(sim)

    # Compute for all A folio pairs (sample)
    a_folios = list(folio_cluster_vecs.keys())
    unlinked_sims = []
    for i in range(len(a_folios)):
        for j in range(i + 1, len(a_folios)):
            pair = tuple(sorted([a_folios[i], a_folios[j]]))
            if pair not in linked_pairs:
                sim = cosine_similarity(folio_cluster_vecs[a_folios[i]],
                                       folio_cluster_vecs[a_folios[j]])
                unlinked_sims.append(sim)

    linked_median = np.median(linked_sims) if linked_sims else 0
    unlinked_median = np.median(unlinked_sims) if unlinked_sims else 0

    # Permutation test: randomly select same number of folio pairs
    n_linked = len(linked_sims)
    null_linked_means = []
    for _ in range(N_PERM):
        perm_sims = rng.choice(unlinked_sims, size=min(n_linked, len(unlinked_sims)),
                               replace=False)
        null_linked_means.append(np.mean(perm_sims))

    obs_linked_mean = np.mean(linked_sims) if linked_sims else 0
    null_mean_linked = np.mean(null_linked_means) if null_linked_means else 0
    null_std_linked = np.std(null_linked_means) if null_linked_means else 0
    p_linked = np.mean([n >= obs_linked_mean for n in null_linked_means]) if null_linked_means else 1
    z_linked = ((obs_linked_mean - null_mean_linked) / null_std_linked
                if null_std_linked > 0 else 0)

    h7_pass = p_linked < 0.05

    print(f"  Linked folio pairs in data: {n_linked}")
    print(f"  Linked median similarity: {linked_median:.4f}")
    print(f"  Unlinked median similarity: {unlinked_median:.4f}")
    print(f"  Linked mean: {obs_linked_mean:.4f}, Null mean: {null_mean_linked:.4f}")
    print(f"  z = {z_linked:.3f}, p = {p_linked:.4f}")
    print(f"  H7: {'PASS' if h7_pass else 'FAIL'}")

    t4_results = {
        'linked_pairs_in_data': n_linked,
        'linked_median_sim': float(linked_median),
        'unlinked_median_sim': float(unlinked_median),
        'linked_mean': float(obs_linked_mean),
        'null_mean': float(null_mean_linked),
        'null_std': float(null_std_linked),
        'z': float(z_linked),
        'p': float(p_linked),
        'h7_pass': bool(h7_pass),
    }

    # ================================================================
    # S7: T5 - B execution prediction
    # ================================================================
    print("\n[S7] T5: B execution prediction...")

    # Build per-A-folio features
    tx = Transcript()

    # Get B MIDDLE inventory per folio
    b_folio_middles = defaultdict(set)
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)

    # Get per-A-folio PP MIDDLE pool
    a_folio_pp = defaultdict(set)
    for par_id, pdata in paragraphs.items():
        for m in pdata['all_middles']:
            if m in pp_middles:
                a_folio_pp[pdata['folio']].add(m)

    # Compute A-folio -> B-folio coverage (aggregate over all B folios)
    # Build B paragraph PP MIDDLE sets
    b_par_pp_sets = []
    current_b_par = set()
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            if token.par_initial and current_b_par:
                b_par_pp_sets.append(current_b_par)
                current_b_par = set()
            continue
        if token.par_initial and current_b_par:
            b_par_pp_sets.append(current_b_par)
            current_b_par = set()
        m = morph.extract(word)
        if m.middle and m.middle in pp_middles:
            current_b_par.add(m.middle)
    if current_b_par:
        b_par_pp_sets.append(current_b_par)

    # Filter to B paragraphs with >= 5 PP MIDDLEs
    b_par_pp_sets = [s for s in b_par_pp_sets if len(s) >= 5]

    # For each A folio, compute mean coverage over B paragraphs
    # Coverage = |A_folio_PP ∩ B_para_PP| / |B_para_PP|
    a_folio_coverage = {}
    for a_folio, a_pp_set in a_folio_pp.items():
        if not a_pp_set:
            continue
        coverages = []
        for b_set in b_par_pp_sets:
            overlap = a_pp_set & b_set
            coverages.append(len(overlap) / len(b_set))
        a_folio_coverage[a_folio] = np.mean(coverages) if coverages else 0

    # Build feature matrix
    feature_folios = sorted(f for f in a_folio_pp if f in a_folio_coverage
                            and f in folio_cluster_vecs)

    if len(feature_folios) >= 10:
        X_pool = np.array([len(a_folio_pp[f]) for f in feature_folios]).reshape(-1, 1)
        y = np.array([a_folio_coverage[f] for f in feature_folios])

        # Baseline: PP pool size only
        from numpy.linalg import lstsq
        X_base = np.column_stack([X_pool, np.ones(len(feature_folios))])
        beta_base, residuals_base, _, _ = lstsq(X_base, y, rcond=None)
        y_pred_base = X_base @ beta_base
        ss_res_base = np.sum((y - y_pred_base) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2_base = 1 - ss_res_base / ss_tot if ss_tot > 0 else 0

        # Extended: PP pool size + paragraph composition features
        cluster_entropy_feature = np.array([
            np.mean([par_entropies.get(pid, max_entropy)
                     for pid in folio_par_ids.get(f, []) if pid in par_entropies])
            if any(pid in par_entropies for pid in folio_par_ids.get(f, []))
            else max_entropy
            for f in feature_folios
        ])

        compat_density_feature = np.array([
            np.mean([par_densities.get(pid, obs_mean_all)
                     for pid in folio_par_ids.get(f, []) if pid in par_densities])
            if any(pid in par_densities for pid in folio_par_ids.get(f, []))
            else obs_mean_all
            for f in feature_folios
        ])

        has_linker_feature = np.array([
            1.0 if f in linked_folios else 0.0
            for f in feature_folios
        ])

        X_ext = np.column_stack([X_pool, cluster_entropy_feature,
                                 compat_density_feature, has_linker_feature,
                                 np.ones(len(feature_folios))])
        beta_ext, residuals_ext, _, _ = lstsq(X_ext, y, rcond=None)
        y_pred_ext = X_ext @ beta_ext
        ss_res_ext = np.sum((y - y_pred_ext) ** 2)
        r2_ext = 1 - ss_res_ext / ss_tot if ss_tot > 0 else 0

        delta_r2 = r2_ext - r2_base

        # Adjusted R-squared
        n = len(feature_folios)
        p_base = 1  # 1 predictor
        p_ext = 4   # 4 predictors
        adj_r2_base = 1 - (1 - r2_base) * (n - 1) / (n - p_base - 1) if n > p_base + 1 else r2_base
        adj_r2_ext = 1 - (1 - r2_ext) * (n - 1) / (n - p_ext - 1) if n > p_ext + 1 else r2_ext

        # Pool size correlation
        pool_rho, pool_p = stats.spearmanr(X_pool.ravel(), y)
        if np.isnan(pool_rho):
            pool_rho = 0.0
        if np.isnan(pool_p):
            pool_p = 1.0

        h8_pass = delta_r2 > 0.05 and adj_r2_ext > adj_r2_base

        print(f"  Feature folios: {n}")
        print(f"  Pool size -> coverage: rho = {pool_rho:.3f}, p = {pool_p:.4f}")
        print(f"  Baseline R2 (pool size only): {r2_base:.4f} (adj: {adj_r2_base:.4f})")
        print(f"  Extended R2 (+ composition): {r2_ext:.4f} (adj: {adj_r2_ext:.4f})")
        print(f"  Delta R2: {delta_r2:.4f}")
        print(f"  H8: {'PASS' if h8_pass else 'FAIL'}")
    else:
        h8_pass = False
        r2_base = 0
        r2_ext = 0
        adj_r2_base = 0
        adj_r2_ext = 0
        delta_r2 = 0
        pool_rho = 0
        pool_p = 1
        n = len(feature_folios)
        print(f"  Insufficient folios for regression: {n}")
        print(f"  H8: FAIL (insufficient data)")

    t5_results = {
        'n_folios': n,
        'pool_rho': float(pool_rho),
        'pool_p': float(pool_p),
        'r2_base': float(r2_base),
        'r2_ext': float(r2_ext),
        'adj_r2_base': float(adj_r2_base),
        'adj_r2_ext': float(adj_r2_ext),
        'delta_r2': float(delta_r2),
        'h8_pass': bool(h8_pass),
    }

    # ================================================================
    # S8: Summary + verdict
    # ================================================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    hypotheses = [
        ('H1', 'Paragraphs have higher compatibility than random', h1_pass),
        ('H2', 'Excess compatibility driven by PP MIDDLEs', h2_pass),
        ('H3', 'Paragraph cluster entropy lower than random', h3_pass),
        ('H4', 'Adjacent paragraphs more similar', h4_pass),
        ('H5', 'Within-folio > between-folio compatibility', h5_pass),
        ('H6', 'Within-folio > section-matched between-folio', h6_pass),
        ('H7', 'Linked folios closer in composition space', h7_pass),
        ('H8', 'Paragraph composition improves B prediction', h8_pass),
    ]

    n_pass = sum(1 for _, _, p in hypotheses if p)
    for hid, desc, passed in hypotheses:
        print(f"  {hid}: {'PASS' if passed else 'FAIL'} - {desc}")

    global_pass = n_pass >= 5
    if n_pass >= 7:
        verdict = "STRONG_COMBINATORIAL_GRAMMAR"
    elif n_pass >= 5:
        verdict = "COMBINATORIAL_GRAMMAR_CONFIRMED"
    elif n_pass >= 3:
        verdict = "PARTIAL_COMBINATORIAL_STRUCTURE"
    else:
        verdict = "NO_COMBINATORIAL_GRAMMAR"

    print(f"\n  Hypotheses passed: {n_pass}/8")
    print(f"  VERDICT: {verdict}")

    # Save results
    results = {
        'phase': 364,
        'title': 'Currier A Paragraph-Level Combinatorial Grammar',
        'n_paragraphs': len(paragraphs),
        'n_middles_in_matrix': n_mid,
        'n_clusters': 5,
        'cluster_sizes': {str(c): int(cluster_sizes[c]) for c in sorted(cluster_sizes)},
        'T1_compatibility_density': t1_results,
        'T2_cluster_composition': t2_results,
        'T3_within_folio_compatibility': t3_results,
        'T4_linker_topology': t4_results,
        'T5_b_prediction': t5_results,
        'hypotheses': {h: bool(p) for h, _, p in hypotheses},
        'n_pass': n_pass,
        'verdict': verdict,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / 'a_paragraph_combinatorics.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
