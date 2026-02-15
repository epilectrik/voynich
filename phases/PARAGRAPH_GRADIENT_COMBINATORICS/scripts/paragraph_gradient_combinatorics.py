#!/usr/bin/env python3
"""
Phase 368: Paragraph Gradient x Combinatorial Grammar

Tests whether B paragraph spec-to-exec gradient (C932) operates through
the C475 MIDDLE incompatibility graph and respects paragraph combinatorial
grammar (C1039-C1041).

Hypotheses:
  H1: Gradient cluster trajectory (Q0 fewer clusters -> Q4 more)
  H2: Spec MIDDLEs constrain exec via C475 compatibility
  H3: Compound atom prediction mediated by C475
  H4: Gradient steepness x section funnel aperture (C1051)
  H5: B paragraph cluster selectivity + gradient decomposition

Output: results/paragraph_gradient_combinatorics.json
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from datetime import datetime
from scipy import stats
from sklearn.mixture import GaussianMixture

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

COMPAT_MATRIX_PATH = (PROJECT_ROOT / 'phases' / 'DISCRIMINATION_SPACE_DERIVATION'
                      / 'results' / 't1_compat_matrix.npy')

K_RESIDUAL = 99
N_PERM = 1000
RNG_SEED = 42
MIN_PARAGRAPH_LINES = 8  # C932 threshold

# C1051 funnel apertures (from Phase 367)
FUNNEL_APERTURE = {'B': 0.794, 'H': 0.813, 'S': 0.824}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


print("=" * 70)
print("Phase 368: Paragraph Gradient x Combinatorial Grammar")
print("=" * 70)

# ============================================================
# S1: Load Compatibility Matrix, Build Clusters, Identify Hubs
# ============================================================
print("\n--- S1: Load Compatibility Matrix & Build Clusters ---")

tx = Transcript()
morph = Morphology()

# Reconstruct MIDDLE list (same as Phase 364)
a_middles = set()
for token in tx.currier_a():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    if m.middle:
        a_middles.add(m.middle)
all_middles = sorted(a_middles)
mid_to_idx = {m: i for i, m in enumerate(all_middles)}
n_mid = len(all_middles)

# Load compatibility matrix
compat_matrix = np.load(COMPAT_MATRIX_PATH)
print(f"  Compatibility matrix: {compat_matrix.shape}")
print(f"  MIDDLEs in matrix: {n_mid}")

# Spectral embedding (same as Phase 364)
eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]
res_evals = eigenvalues[1:K_RESIDUAL + 1]
res_evecs = eigenvectors[:, 1:K_RESIDUAL + 1]
scaling = np.sqrt(np.maximum(res_evals, 0))
embedding = res_evecs * scaling[np.newaxis, :]

# GMM k=5 clustering (same parameters as Phase 364)
print("  Running GMM k=5 clustering...")
gmm = GaussianMixture(n_components=5, random_state=42, n_init=3,
                       covariance_type='diag', max_iter=300)
labels = gmm.fit_predict(embedding)
mid_to_cluster = {all_middles[i]: int(labels[i]) for i in range(n_mid)}
cluster_sizes = Counter(labels)
for c in sorted(cluster_sizes):
    print(f"    Cluster {c}: {cluster_sizes[c]} MIDDLEs")

# Identify hub MIDDLEs (top 10% by degree centrality)
degree = (compat_matrix > 0).sum(axis=1)
hub_threshold = np.percentile(degree, 90)
hub_indices = set(np.where(degree >= hub_threshold)[0])
hub_middles = set(all_middles[i] for i in hub_indices)
print(f"  Hub MIDDLEs (top 10% by degree): {len(hub_middles)}")
print(f"  Hub degree threshold: {hub_threshold:.0f}")

# ============================================================
# S2: Build B Paragraphs, Extract MIDDLEs, Assign Quintiles
# ============================================================
print("\n--- S2: Build B Paragraphs & Assign Quintiles ---")

# Group B tokens into folios -> lines -> paragraphs
b_data = defaultdict(lambda: defaultdict(list))  # folio -> line -> [tokens]
b_folio_section = {}
for token in tx.currier_b():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    b_data[token.folio][token.line].append(token)
    if token.folio not in b_folio_section:
        b_folio_section[token.folio] = token.section

# Build paragraphs per folio using par_initial
morph_cache = {}
def get_middle(word):
    if word not in morph_cache:
        m = morph.extract(word)
        morph_cache[word] = m.middle if m.middle else None
    return morph_cache[word]

paragraphs = []  # list of dicts: {folio, section, lines: [{line_num, middles}]}

for folio in sorted(b_data.keys()):
    section = b_folio_section.get(folio, '?')
    if section not in ('B', 'H', 'S'):
        continue  # Only B, H, S sections

    lines = sorted(b_data[folio].keys())
    if not lines:
        continue

    # Detect paragraph boundaries via par_initial
    current_para_lines = []
    for line_num in lines:
        tokens = b_data[folio][line_num]
        is_para_start = any(t.par_initial for t in tokens)

        if is_para_start and current_para_lines:
            # Save previous paragraph
            paragraphs.append({
                'folio': folio,
                'section': section,
                'lines': current_para_lines
            })
            current_para_lines = []

        # Extract MIDDLEs for this line
        line_middles = []
        for t in tokens:
            mid = get_middle(t.word)
            if mid:
                line_middles.append(mid)

        current_para_lines.append({
            'line_num': line_num,
            'middles': line_middles
        })

    # Save last paragraph
    if current_para_lines:
        paragraphs.append({
            'folio': folio,
            'section': section,
            'lines': current_para_lines
        })

print(f"  Total B paragraphs (B+H+S): {len(paragraphs)}")

# Filter to paragraphs with 8+ lines (C932 threshold)
long_paras = [p for p in paragraphs if len(p['lines']) >= MIN_PARAGRAPH_LINES]
print(f"  Paragraphs with {MIN_PARAGRAPH_LINES}+ lines: {len(long_paras)}")

section_counts = Counter(p['section'] for p in long_paras)
for s in ['B', 'H', 'S']:
    print(f"    Section {s}: {section_counts.get(s, 0)}")

# Assign quintiles to body lines (line 2+ = body)
# quintile = min(int(5 * body_line_index / n_body_lines), 4)
for para in long_paras:
    body_lines = para['lines'][1:]  # Skip header line
    n_body = len(body_lines)
    for bi, line in enumerate(body_lines):
        line['quintile'] = min(int(5 * bi / n_body), 4)
    para['body_lines'] = body_lines
    para['header_line'] = para['lines'][0]

# Track matrix coverage
all_b_middles_used = set()
b_middles_in_matrix = set()
for para in long_paras:
    for line in para['lines']:
        for mid in line['middles']:
            all_b_middles_used.add(mid)
            if mid in mid_to_idx:
                b_middles_in_matrix.add(mid)

coverage_rate = len(b_middles_in_matrix) / len(all_b_middles_used) if all_b_middles_used else 0
print(f"  B MIDDLEs used: {len(all_b_middles_used)}")
print(f"  In compat matrix: {len(b_middles_in_matrix)} ({coverage_rate:.1%})")

# Pre-compute per-quintile MIDDLE sets for each paragraph (matrix-covered only)
for para in long_paras:
    para['quintile_middles'] = defaultdict(set)
    para['quintile_middles_all'] = defaultdict(set)  # including non-matrix
    for line in para['body_lines']:
        q = line['quintile']
        for mid in line['middles']:
            para['quintile_middles_all'][q].add(mid)
            if mid in mid_to_idx:
                para['quintile_middles'][q].add(mid)

# ============================================================
# S3: H1 — Gradient Cluster Trajectory
# ============================================================
print("\n--- S3: H1 — Gradient Cluster Trajectory ---")

def cluster_entropy(middles_set):
    """Shannon entropy of cluster distribution for a set of MIDDLEs."""
    if not middles_set:
        return None
    clusters = [mid_to_cluster[m] for m in middles_set if m in mid_to_cluster]
    if not clusters:
        return None
    counts = Counter(clusters)
    total = sum(counts.values())
    probs = [c / total for c in counts.values()]
    return -sum(p * np.log2(p) for p in probs if p > 0)

# Per-quintile cluster entropy across paragraphs
quintile_entropies = defaultdict(list)  # q -> [entropy values]
for para in long_paras:
    for q in range(5):
        mids = para['quintile_middles'][q]
        ent = cluster_entropy(mids)
        if ent is not None:
            quintile_entropies[q].append(ent)

for q in range(5):
    vals = quintile_entropies[q]
    print(f"  Q{q}: n={len(vals)}, mean entropy={np.mean(vals):.4f}, "
          f"std={np.std(vals):.4f}")

# Kruskal-Wallis test
kw_arrays = [np.array(quintile_entropies[q]) for q in range(5)]
kw_stat, kw_p = stats.kruskal(*kw_arrays)
print(f"  Kruskal-Wallis: H={kw_stat:.2f}, p={kw_p:.4e}")

# Direction check: Spearman correlation of quintile mean entropy
q_means = [np.mean(quintile_entropies[q]) for q in range(5)]
rho_direction, p_direction = stats.spearmanr(list(range(5)), q_means)
increasing = rho_direction > 0
print(f"  Direction (mean entropy vs quintile): rho={rho_direction:.4f}, "
      f"increasing={increasing}")

h1_pass = (kw_p < 0.01) and increasing
print(f"  H1 PASS: {h1_pass}")

h1_results = {
    'quintile_means': {f'Q{q}': float(np.mean(quintile_entropies[q])) for q in range(5)},
    'quintile_ns': {f'Q{q}': len(quintile_entropies[q]) for q in range(5)},
    'kw_stat': float(kw_stat),
    'kw_p': float(kw_p),
    'direction_rho': float(rho_direction),
    'direction_increasing': bool(increasing),
    'pass': bool(h1_pass)
}

# ============================================================
# S4: H2 — Specification Constrains Execution via C475
# ============================================================
print("\n--- S4: H2 — Specification Constrains Execution via C475 ---")

rng = np.random.RandomState(RNG_SEED)

def compatibility_rate(spec_middles, exec_middles, exclude_hubs=False):
    """Fraction of exec MIDDLEs compatible with ANY spec MIDDLE."""
    if not spec_middles or not exec_middles:
        return None
    spec_set = set(spec_middles)
    exec_set = set(exec_middles)
    if exclude_hubs:
        spec_set -= hub_middles
        exec_set -= hub_middles
    if not spec_set or not exec_set:
        return None

    spec_indices = [mid_to_idx[m] for m in spec_set if m in mid_to_idx]
    n_compat = 0
    n_total = 0
    for m in exec_set:
        if m not in mid_to_idx:
            continue
        mi = mid_to_idx[m]
        n_total += 1
        for si in spec_indices:
            if compat_matrix[si, mi] > 0:
                n_compat += 1
                break
    return n_compat / n_total if n_total > 0 else None

# Observed: Q0 spec -> Q3+Q4 exec compatibility
observed_rates = []
observed_rates_nohub = []
valid_paras_h2 = []

for para in long_paras:
    spec = para['quintile_middles'][0]  # Q0
    exec_mids = para['quintile_middles'][3] | para['quintile_middles'][4]  # Q3+Q4
    rate = compatibility_rate(spec, exec_mids, exclude_hubs=False)
    rate_nh = compatibility_rate(spec, exec_mids, exclude_hubs=True)
    if rate is not None:
        observed_rates.append(rate)
        valid_paras_h2.append(para)
    if rate_nh is not None:
        observed_rates_nohub.append(rate_nh)

obs_mean = np.mean(observed_rates)
obs_mean_nh = np.mean(observed_rates_nohub) if observed_rates_nohub else 0.0
print(f"  Observed Q0->Q3Q4 compatibility: mean={obs_mean:.4f} (n={len(observed_rates)})")
print(f"  Hub-removed: mean={obs_mean_nh:.4f} (n={len(observed_rates_nohub)})")

# Null: permute Q0 assignments across paragraphs
all_q0_sets = [para['quintile_middles'][0] for para in valid_paras_h2]
all_exec_sets = [para['quintile_middles'][3] | para['quintile_middles'][4]
                 for para in valid_paras_h2]

null_means = []
null_means_nh = []
for perm_i in range(N_PERM):
    shuffled_q0 = list(all_q0_sets)
    rng.shuffle(shuffled_q0)
    perm_rates = []
    perm_rates_nh = []
    for sq0, exec_m in zip(shuffled_q0, all_exec_sets):
        r = compatibility_rate(sq0, exec_m, exclude_hubs=False)
        r_nh = compatibility_rate(sq0, exec_m, exclude_hubs=True)
        if r is not None:
            perm_rates.append(r)
        if r_nh is not None:
            perm_rates_nh.append(r_nh)
    if perm_rates:
        null_means.append(np.mean(perm_rates))
    if perm_rates_nh:
        null_means_nh.append(np.mean(perm_rates_nh))

null_means = np.array(null_means)
null_means_nh = np.array(null_means_nh)

p_full = np.mean(null_means >= obs_mean)
p_nohub = np.mean(null_means_nh >= obs_mean_nh) if len(null_means_nh) > 0 else 1.0

print(f"  Null mean (full): {np.mean(null_means):.4f} +/- {np.std(null_means):.4f}")
print(f"  p-value (full): {p_full:.4f}")
print(f"  Null mean (no-hub): {np.mean(null_means_nh):.4f} +/- {np.std(null_means_nh):.4f}")
print(f"  p-value (no-hub): {p_nohub:.4f}")

h2_pass = (p_full < 0.05) and (p_nohub < 0.05)
print(f"  H2 PASS (full p<0.05 AND no-hub p<0.05): {h2_pass}")

h2_results = {
    'observed_mean': float(obs_mean),
    'observed_mean_nohub': float(obs_mean_nh),
    'null_mean': float(np.mean(null_means)),
    'null_std': float(np.std(null_means)),
    'null_mean_nohub': float(np.mean(null_means_nh)) if len(null_means_nh) > 0 else None,
    'null_std_nohub': float(np.std(null_means_nh)) if len(null_means_nh) > 0 else None,
    'p_full': float(p_full),
    'p_nohub': float(p_nohub),
    'n_paragraphs': len(observed_rates),
    'n_paragraphs_nohub': len(observed_rates_nohub),
    'pass': bool(h2_pass)
}

# ============================================================
# S5: H3 — Compound Atom Prediction via C475
# ============================================================
print("\n--- S5: H3 — Compound Atom Prediction via C475 ---")

mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')

# For each paragraph with line-1 compound MIDDLEs:
# Extract atoms, check if compatible-atom compounds have higher body hit rate
compound_compat_hits = []  # (hit_rate for compatible atoms, hit_rate for incompatible)
all_hit_rates = []
all_n_atoms = []

for para in long_paras:
    header = para['header_line']
    body_middles = set()
    for line in para['body_lines']:
        body_middles.update(line['middles'])

    # Find compound MIDDLEs in header
    for mid in header['middles']:
        if not mid_analyzer.is_compound(mid):
            continue
        atoms = mid_analyzer.get_contained_atoms(mid)
        if len(atoms) < 2:
            continue

        # Classify atoms: compatible vs incompatible with each other
        compat_atoms = set()
        incompat_atoms = set()
        atom_list = sorted(atoms)
        for a in atom_list:
            if a not in mid_to_idx:
                continue
            # Check compatibility with all other atoms
            is_compat_with_any = False
            for b in atom_list:
                if a == b or b not in mid_to_idx:
                    continue
                if compat_matrix[mid_to_idx[a], mid_to_idx[b]] > 0:
                    is_compat_with_any = True
                    break
            if is_compat_with_any:
                compat_atoms.add(a)
            else:
                incompat_atoms.add(a)

        # Hit rates
        if compat_atoms:
            compat_hits = len(compat_atoms & body_middles) / len(compat_atoms)
        else:
            compat_hits = None
        if incompat_atoms:
            incompat_hits = len(incompat_atoms & body_middles) / len(incompat_atoms)
        else:
            incompat_hits = None

        if compat_hits is not None and incompat_hits is not None:
            compound_compat_hits.append((compat_hits, incompat_hits))

        # Overall hit rate
        all_atoms_in_matrix = [a for a in atoms if a in mid_to_idx]
        if all_atoms_in_matrix:
            overall_hit = len(set(all_atoms_in_matrix) & body_middles) / len(all_atoms_in_matrix)
            all_hit_rates.append(overall_hit)
            all_n_atoms.append(len(all_atoms_in_matrix))

print(f"  Compound MIDDLEs with both compat/incompat atoms: {len(compound_compat_hits)}")
print(f"  Total compound evaluations: {len(all_hit_rates)}")
if all_hit_rates:
    print(f"  Overall atom hit rate: {np.mean(all_hit_rates):.4f}")

if len(compound_compat_hits) >= 10:
    compat_rates = [c for c, _ in compound_compat_hits]
    incompat_rates = [i for _, i in compound_compat_hits]
    print(f"  Compatible atom hit rate: {np.mean(compat_rates):.4f}")
    print(f"  Incompatible atom hit rate: {np.mean(incompat_rates):.4f}")
    t_stat, h3_p = stats.wilcoxon([c - i for c, i in compound_compat_hits])
    print(f"  Wilcoxon: T={t_stat:.1f}, p={h3_p:.4f}")
    h3_pass = (h3_p < 0.05) and (np.mean(compat_rates) > np.mean(incompat_rates))
elif len(compound_compat_hits) >= 5:
    compat_rates = [c for c, _ in compound_compat_hits]
    incompat_rates = [i for _, i in compound_compat_hits]
    print(f"  Compatible atom hit rate: {np.mean(compat_rates):.4f}")
    print(f"  Incompatible atom hit rate: {np.mean(incompat_rates):.4f}")
    # Too few for Wilcoxon, use sign test
    n_positive = sum(1 for c, i in compound_compat_hits if c > i)
    n_negative = sum(1 for c, i in compound_compat_hits if c < i)
    print(f"  Sign test: {n_positive} compat > incompat, {n_negative} incompat > compat")
    h3_p = stats.binom_test(n_positive, n_positive + n_negative, 0.5) if (n_positive + n_negative) > 0 else 1.0
    h3_pass = (h3_p < 0.05) and (n_positive > n_negative)
else:
    print("  INSUFFICIENT DATA for H3 (need >= 5 compounds with both types)")
    h3_p = 1.0
    h3_pass = False
    compat_rates = []
    incompat_rates = []

print(f"  H3 PASS: {h3_pass}")

h3_results = {
    'n_compounds_both_types': len(compound_compat_hits),
    'n_total_compounds': len(all_hit_rates),
    'overall_hit_rate': float(np.mean(all_hit_rates)) if all_hit_rates else None,
    'compat_hit_rate': float(np.mean(compat_rates)) if compat_rates else None,
    'incompat_hit_rate': float(np.mean(incompat_rates)) if incompat_rates else None,
    'p_value': float(h3_p),
    'pass': bool(h3_pass)
}

# ============================================================
# S6: H4 — Gradient Steepness x Section Funnel Aperture
# ============================================================
print("\n--- S6: H4 — Gradient Steepness x Section Funnel Aperture ---")

# Per-section: compute universal MIDDLE fraction at each quintile
# "Universal" = appears in >= 3 B sections (same concept as C932's universal threshold)
# Count section appearances per MIDDLE in B
b_middle_section_spread = defaultdict(set)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w or token.section not in ('B', 'H', 'S'):
        continue
    mid = get_middle(w)
    if mid:
        b_middle_section_spread[mid].add(token.section)

universal_middles = set(m for m, secs in b_middle_section_spread.items() if len(secs) >= 3)
print(f"  Universal MIDDLEs (in >=3 sections): {len(universal_middles)}")

section_gradient = {}  # section -> {quintile -> universal_fraction}
for sect in ['B', 'H', 'S']:
    sect_paras = [p for p in long_paras if p['section'] == sect]
    if len(sect_paras) < 3:
        print(f"  Section {sect}: {len(sect_paras)} paragraphs (too few)")
        continue

    q_fracs = {}
    for q in range(5):
        total_tokens = 0
        universal_tokens = 0
        for para in sect_paras:
            for line in para['body_lines']:
                if line['quintile'] == q:
                    for mid in line['middles']:
                        total_tokens += 1
                        if mid in universal_middles:
                            universal_tokens += 1
        q_fracs[q] = universal_tokens / total_tokens if total_tokens > 0 else 0
    section_gradient[sect] = q_fracs

    # Gradient steepness: Q4 - Q0
    steepness = q_fracs[4] - q_fracs[0]
    print(f"  Section {sect}: Q0={q_fracs[0]:.4f}, Q4={q_fracs[4]:.4f}, "
          f"steepness={steepness:+.4f}, n_paras={len(sect_paras)}")

# Correlation with funnel aperture
if len(section_gradient) >= 3:
    sections_with_data = sorted(section_gradient.keys())
    apertures = [FUNNEL_APERTURE[s] for s in sections_with_data]
    steepnesses = [section_gradient[s][4] - section_gradient[s][0] for s in sections_with_data]
    if len(set(steepnesses)) > 1 and len(set(apertures)) > 1:
        rho_h4, p_h4 = stats.spearmanr(apertures, steepnesses)
    else:
        rho_h4, p_h4 = 0.0, 1.0
    print(f"  Aperture vs steepness: rho={rho_h4:.4f} (n={len(sections_with_data)})")
    # Prediction: negative correlation (tight funnel = steep gradient)
    h4_pass = (rho_h4 < 0) and (len(sections_with_data) >= 3)
    # Note: p-value unreliable with n=3, report direction only
    print(f"  H4 direction (negative = predicted): {rho_h4 < 0}")
    print(f"  H4 PASS (negative correlation, 3+ sections): {h4_pass}")
else:
    rho_h4 = 0.0
    p_h4 = 1.0
    h4_pass = False
    steepnesses = []
    apertures = []
    print("  INSUFFICIENT SECTIONS for H4")

h4_results = {
    'section_gradients': {},
    'steepness_by_section': {},
    'aperture_by_section': FUNNEL_APERTURE,
    'rho': float(rho_h4),
    'direction_negative': bool(rho_h4 < 0),
    'n_sections': len(section_gradient),
    'pass': bool(h4_pass),
    'note': 'p-value unreliable with n=3; direction-only test'
}

for s in section_gradient:
    h4_results['section_gradients'][s] = {f'Q{q}': float(v) for q, v in section_gradient[s].items()}
    h4_results['steepness_by_section'][s] = float(section_gradient[s][4] - section_gradient[s][0])

# ============================================================
# S7: H5 — B Paragraph Cluster Selectivity + Gradient Decomposition
# ============================================================
print("\n--- S7: H5 — B Paragraph Cluster Selectivity ---")

# Step 1: Validate B paragraph cluster selectivity (replication of C1039 on B)
para_entropies = []
para_middles_for_perm = []  # for permutation test

for para in long_paras:
    # All MIDDLEs in paragraph (body only, matrix-covered)
    all_mids = set()
    for line in para['body_lines']:
        for mid in line['middles']:
            if mid in mid_to_cluster:
                all_mids.add(mid)
    if len(all_mids) < 3:
        continue

    ent = cluster_entropy(all_mids)
    if ent is not None:
        para_entropies.append(ent)
        para_middles_for_perm.append(all_mids)

obs_mean_entropy = np.mean(para_entropies)
print(f"  B paragraphs tested: {len(para_entropies)}")
print(f"  Observed mean cluster entropy: {obs_mean_entropy:.4f}")

# Null: shuffle MIDDLE -> cluster mapping
null_entropies = []
for perm_i in range(N_PERM):
    # Shuffle the mid_to_cluster mapping
    shuffled_labels = list(mid_to_cluster.values())
    rng.shuffle(shuffled_labels)
    shuffled_map = {m: shuffled_labels[i] for i, m in enumerate(mid_to_cluster.keys())}

    perm_ents = []
    for mids_set in para_middles_for_perm:
        clusters = [shuffled_map[m] for m in mids_set if m in shuffled_map]
        if not clusters:
            continue
        counts = Counter(clusters)
        total = sum(counts.values())
        probs = [c / total for c in counts.values()]
        ent = -sum(p * np.log2(p) for p in probs if p > 0)
        perm_ents.append(ent)
    if perm_ents:
        null_entropies.append(np.mean(perm_ents))

null_entropies = np.array(null_entropies)
null_mean = np.mean(null_entropies)
z_score = (obs_mean_entropy - null_mean) / np.std(null_entropies) if np.std(null_entropies) > 0 else 0
p_selectivity = np.mean(null_entropies <= obs_mean_entropy)

print(f"  Null mean entropy: {null_mean:.4f} +/- {np.std(null_entropies):.4f}")
print(f"  z-score: {z_score:.4f}")
print(f"  p-value (selectivity): {p_selectivity:.4f}")

b_selective = (p_selectivity < 0.01) and (obs_mean_entropy < null_mean)
print(f"  B paragraphs cluster-selective: {b_selective}")

# Step 2: Gradient decomposition — spec-zone vs exec-zone
spec_entropies = []  # Q0-Q1
exec_entropies = []  # Q3-Q4

for para in long_paras:
    spec_mids = set()
    exec_mids = set()
    for q in [0, 1]:
        for mid in para['quintile_middles'].get(q, set()):
            if mid in mid_to_cluster:
                spec_mids.add(mid)
    for q in [3, 4]:
        for mid in para['quintile_middles'].get(q, set()):
            if mid in mid_to_cluster:
                exec_mids.add(mid)

    spec_ent = cluster_entropy(spec_mids)
    exec_ent = cluster_entropy(exec_mids)
    if spec_ent is not None:
        spec_entropies.append(spec_ent)
    if exec_ent is not None:
        exec_entropies.append(exec_ent)

if spec_entropies and exec_entropies:
    print(f"  Spec-zone (Q0-Q1) entropy: {np.mean(spec_entropies):.4f} (n={len(spec_entropies)})")
    print(f"  Exec-zone (Q3-Q4) entropy: {np.mean(exec_entropies):.4f} (n={len(exec_entropies)})")
    mw_stat, mw_p = stats.mannwhitneyu(spec_entropies, exec_entropies, alternative='less')
    print(f"  Mann-Whitney (spec < exec): U={mw_stat:.0f}, p={mw_p:.4f}")
    spec_less = np.mean(spec_entropies) < np.mean(exec_entropies)
else:
    mw_p = 1.0
    spec_less = False

h5_pass = b_selective and spec_less and (mw_p < 0.05)
print(f"  H5 PASS (selective AND spec < exec): {h5_pass}")

h5_results = {
    'b_paragraph_cluster_selectivity': {
        'n_paragraphs': len(para_entropies),
        'observed_mean_entropy': float(obs_mean_entropy),
        'null_mean_entropy': float(null_mean),
        'z_score': float(z_score),
        'p_selectivity': float(p_selectivity),
        'selective': bool(b_selective)
    },
    'gradient_decomposition': {
        'spec_zone_entropy': float(np.mean(spec_entropies)) if spec_entropies else None,
        'exec_zone_entropy': float(np.mean(exec_entropies)) if exec_entropies else None,
        'spec_n': len(spec_entropies),
        'exec_n': len(exec_entropies),
        'mw_p': float(mw_p),
        'spec_less_than_exec': bool(spec_less)
    },
    'pass': bool(h5_pass)
}

# ============================================================
# S8: Verdict Synthesis
# ============================================================
print("\n--- S8: Verdict Synthesis ---")

n_pass = sum([h1_pass, h2_pass, h3_pass, h4_pass, h5_pass])
print(f"\nResults: {n_pass}/5 hypotheses pass")
print(f"  H1 (cluster trajectory):          {'PASS' if h1_pass else 'FAIL'}")
print(f"  H2 (spec constrains exec):        {'PASS' if h2_pass else 'FAIL'}")
print(f"  H3 (compound atom via C475):       {'PASS' if h3_pass else 'FAIL'}")
print(f"  H4 (section x gradient):           {'PASS' if h4_pass else 'FAIL'}")
print(f"  H5 (B cluster selectivity):        {'PASS' if h5_pass else 'FAIL'}")

if h1_pass and h2_pass and h3_pass:
    verdict = 'FULL_INTEGRATION'
elif h1_pass and h2_pass:
    verdict = 'GRADIENT_COMPATIBILITY_LINKED'
elif h3_pass:
    verdict = 'COMPOUND_MEDIATED'
elif h4_pass and not h1_pass and not h2_pass:
    verdict = 'SECTION_MODULATED_ONLY'
elif not h1_pass and not h2_pass:
    verdict = 'GRADIENT_INDEPENDENT'
else:
    verdict = f'PARTIAL_{n_pass}_OF_5'

print(f"\nVerdict: {verdict} ({n_pass}/5)")

results = {
    'phase': 'PARAGRAPH_GRADIENT_COMBINATORICS',
    'phase_number': 368,
    'timestamp': datetime.now().isoformat(),
    'analysis_set': {
        'total_b_paragraphs': len(paragraphs),
        'long_paragraphs': len(long_paras),
        'min_lines': MIN_PARAGRAPH_LINES,
        'section_counts': dict(section_counts),
        'matrix_middles': n_mid,
        'b_middles_used': len(all_b_middles_used),
        'b_middles_in_matrix': len(b_middles_in_matrix),
        'coverage_rate': float(coverage_rate),
        'hub_middles': len(hub_middles),
        'gmm_cluster_sizes': {str(c): int(n) for c, n in sorted(cluster_sizes.items())}
    },
    'H1_cluster_trajectory': h1_results,
    'H2_spec_constrains_exec': h2_results,
    'H3_compound_atom_c475': h3_results,
    'H4_section_gradient': h4_results,
    'H5_b_cluster_selectivity': h5_results,
    'verdict': verdict,
    'verdict_score': f'{n_pass}/5'
}

out_path = RESULTS_DIR / 'paragraph_gradient_combinatorics.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)
print(f"\nResults written to {out_path}")
print("\nDone.")
