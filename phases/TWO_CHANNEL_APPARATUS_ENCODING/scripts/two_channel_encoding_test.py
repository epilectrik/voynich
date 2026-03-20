"""
Phase 616: Two-Channel Apparatus Encoding Test
Tests whether vocabulary identity (WHAT MIDDLEs a folio uses) and paragraph
deployment architecture (HOW those MIDDLEs are arranged) are redundant or
complementary predictors of the apparatus manifold.

Produces: two_channel_encoding_results.json
"""
import sys; sys.path.insert(0, '.')
import json
import time
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.spatial.distance import pdist, squareform, jensenshannon
from scipy.stats import spearmanr
from numpy.linalg import lstsq
from sklearn.cluster import KMeans
from collections import Counter, defaultdict
from scripts.voynich import Transcript, BFolioDecoder, Morphology

t0 = time.time()
PROJECT_ROOT = Path('.')
tx = Transcript()
decoder = BFolioDecoder()
morph = Morphology()

# Constants
GALLOWS_SET = set('ktpf')
GALLOWS_TYPES = ['k', 't', 'p', 'f']
ATOMS = list('kethpfocda')
MANIFOLD_PCS = ['PC1', 'PC2', 'PC3', 'PC4', 'PC5']
SECTION_MAP = {'S': 'Stars', 'B': 'Bio', 'H': 'Herbal', 'T': 'Cosmo', 'C': 'Cosmo'}
PREFIXES = ['ch', 'sh', 'qo', 'o', 'd', 's', 'l', 'r', 'y', 'NONE']

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def mantel_test(dist_a, dist_b, n_perms=10000, seed=42):
    """Mantel test with z-score. Returns (r, p, z, null_mean, null_std)."""
    rng = np.random.default_rng(seed)
    n = dist_a.shape[0]
    idx = np.triu_indices(n, k=1)
    a_flat = dist_a[idx]
    b_flat = dist_b[idx]
    r_obs = float(np.corrcoef(a_flat, b_flat)[0, 1])
    r_nulls = np.empty(n_perms)
    for p in range(n_perms):
        perm = rng.permutation(n)
        b_perm = dist_b[np.ix_(perm, perm)]
        r_nulls[p] = np.corrcoef(a_flat, b_perm[idx])[0, 1]
    p_val = float((np.sum(r_nulls >= r_obs) + 1) / (n_perms + 1))
    z = float((r_obs - r_nulls.mean()) / (r_nulls.std() + 1e-10))
    return r_obs, p_val, z, float(r_nulls.mean()), float(r_nulls.std())


def partial_mantel(dist_a, dist_b, control_dists, n_perms=10000, seed=42):
    """Partial Mantel via OLS residualization."""
    n = dist_a.shape[0]
    idx = np.triu_indices(n, k=1)
    a_flat = dist_a[idx]
    b_flat = dist_b[idx]
    controls = np.column_stack([cd[idx] for cd in control_dists])
    A_mat = np.column_stack([controls, np.ones(len(a_flat))])
    res_a = a_flat - A_mat @ lstsq(A_mat, a_flat, rcond=None)[0]
    res_b = b_flat - A_mat @ lstsq(A_mat, b_flat, rcond=None)[0]
    r_obs = float(np.corrcoef(res_a, res_b)[0, 1])
    rng = np.random.default_rng(seed)
    r_nulls = np.empty(n_perms)
    for p in range(n_perms):
        perm = rng.permutation(len(res_a))
        r_nulls[p] = np.corrcoef(res_a, res_b[perm])[0, 1]
    p_val = float((np.sum(r_nulls >= r_obs) + 1) / (n_perms + 1))
    z = float((r_obs - r_nulls.mean()) / (r_nulls.std() + 1e-10))
    return r_obs, p_val, z


def build_jaccard_dist(folio_list, folio_sets):
    """Build Jaccard distance matrix."""
    n = len(folio_list)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            s_i = folio_sets[folio_list[i]]
            s_j = folio_sets[folio_list[j]]
            union = s_i | s_j
            jaccard = len(s_i & s_j) / len(union) if union else 0
            dist[i, j] = dist[j, i] = 1.0 - jaccard
    return dist


def atom_fracs_from_tokens(token_list):
    """Extract atom fraction vector from token list."""
    atoms = []
    for w in token_list:
        m = morph.extract(w)
        if m.middle:
            for c in m.middle:
                if c in ATOMS:
                    atoms.append(c)
    if len(atoms) < 3:
        return None
    counts = Counter(atoms)
    total = sum(counts.values())
    return np.array([counts.get(a, 0) / total for a in ATOMS])


def prefix_dist_from_tokens(token_list):
    """Extract PREFIX frequency distribution from token list."""
    prefixes = []
    for w in token_list:
        m = morph.extract(w)
        if m.middle:
            pfx = m.prefix if m.prefix else 'NONE'
            prefixes.append(pfx)
    if len(prefixes) < 3:
        return None
    counts = Counter(prefixes)
    total = sum(counts.values())
    return {pfx: counts.get(pfx, 0) / total for pfx in PREFIXES}


# ============================================================
# DATA LOADING
# ============================================================
print('Loading data...')

# Load manifold
mani_path = PROJECT_ROOT / 'phases' / 'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS' / 'results' / 't1_manifold_embedding.json'
with open(mani_path) as f:
    mani_data = json.load(f)
manifold_scores = mani_data['space_A']['folio_scores']
manifold_folios = set(manifold_scores.keys())
print(f'  Manifold folios: {len(manifold_folios)}')

# Load bridge/dark sets
bridge_path = PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
with open(bridge_path) as f:
    bridge_data = json.load(f)
bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])

dark_path = PROJECT_ROOT / 'data' / 'dark_pipeline_middles.json'
with open(dark_path) as f:
    dark_data = json.load(f)
dark_set = set(dark_data['middles'])

# Load B grammar class map for classified MIDDLE filter
class_map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_token_map = json.load(f)
# Extract set of classified MIDDLEs from class map
classified_middles = set()
token_class_map = class_token_map.get('token_to_class', class_token_map)
for token_str in token_class_map:
    m = morph.extract(token_str)
    if m.middle:
        classified_middles.add(m.middle)
print(f'  Classified MIDDLEs: {len(classified_middles)}')
print(f'  Bridge MIDDLEs: {len(bridge_set)}')
print(f'  Dark MIDDLEs: {len(dark_set)}')

# Load paragraph zone labels
zone_path = PROJECT_ROOT / 'phases' / 'PARAGRAPH_PROGRAM_TYPING' / 'results' / 'paragraph_program_typing.json'
with open(zone_path) as f:
    zone_data = json.load(f)
zone_labels = zone_data['paragraph_labels']

# Build zone counts per folio
folio_zone_counts = defaultdict(lambda: Counter())
for entry in zone_labels:
    folio_zone_counts[entry['folio']][entry['cluster']] += 1

# ============================================================
# BUILD B-FOLIO INVENTORIES
# ============================================================
print('\nBuilding B-folio MIDDLE inventories...')

folio_sections = {}
folio_all_middles = defaultdict(set)       # All MIDDLEs (for diagnostics)
folio_classified_middles = defaultdict(set)  # Classified only (vocab channel)
folio_bridge_middles = defaultdict(set)
folio_dark_middles = defaultdict(set)
folio_prefix_counts = defaultdict(lambda: Counter())

for tok in tx.currier_b():
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    if tok.folio not in folio_sections:
        folio_sections[tok.folio] = SECTION_MAP.get(tok.section, tok.section)
    m = morph.extract(w)
    if m.middle:
        folio_all_middles[tok.folio].add(m.middle)
        if m.middle in classified_middles:
            folio_classified_middles[tok.folio].add(m.middle)
        if m.middle in bridge_set:
            folio_bridge_middles[tok.folio].add(m.middle)
        if m.middle in dark_set:
            folio_dark_middles[tok.folio].add(m.middle)
        pfx = m.prefix if m.prefix else 'NONE'
        folio_prefix_counts[tok.folio][pfx] += 1

print(f'  B folios with vocab: {len(folio_classified_middles)}')

# ============================================================
# BUILD PARAGRAPH SHAPE VECTORS (replicate Phase 615 exactly)
# ============================================================
print('\nBuilding paragraph shape vectors...')

para_records = []
for fid in sorted(folio_sections.keys()):
    sec = folio_sections[fid]
    paras = decoder.analyze_folio_paragraphs(fid)
    n_paras = len(paras)
    for pi, p in enumerate(paras):
        bt = p.boundary_token
        if not bt or bt[0] not in GALLOWS_SET:
            continue
        if len(p.lines) < 2:
            continue
        hdr_all = [t.word.strip() for t in p.lines[0].tokens if t.word.strip() and '*' not in t.word]
        if len(hdr_all) < 2:
            continue
        hdr_non_bt = hdr_all[1:]
        body_toks = []
        body_line_lens = []
        for li in range(1, len(p.lines)):
            line_toks = [t.word.strip() for t in p.lines[li].tokens if t.word.strip() and '*' not in t.word]
            body_toks.extend(line_toks)
            body_line_lens.append(len(line_toks))
        hdr_fracs = atom_fracs_from_tokens(hdr_non_bt)
        body_fracs = atom_fracs_from_tokens(body_toks)
        if body_fracs is None:
            continue
        # Suffix mode A fraction
        mode_a_count = 0
        mode_total = 0
        for li in range(1, len(p.lines)):
            sm = p.lines[li].suffix_mode
            if sm in ('A', 'B'):
                mode_total += 1
                if sm == 'A':
                    mode_a_count += 1
        mode_a_frac = mode_a_count / mode_total if mode_total > 0 else 0.5
        para_records.append({
            'folio': fid, 'section': sec, 'ordinal': pi, 'n_paras': n_paras,
            'gallows': bt[0], 'hdr_fracs': hdr_fracs,
            'mean_body_line_len': np.mean(body_line_lens) if body_line_lens else 0,
            'mode_a_frac': mode_a_frac,
        })

# Group by folio
folio_para_groups = defaultdict(list)
for r in para_records:
    folio_para_groups[r['folio']].append(r)
for fid in folio_para_groups:
    folio_para_groups[fid].sort(key=lambda x: x['ordinal'])

print(f'  Total paragraphs: {len(para_records)}')
print(f'  Folios with paragraphs: {len(folio_para_groups)}')

# ============================================================
# COMPUTE FOLIO-LEVEL SHAPE VECTORS
# ============================================================

# Common folios: in manifold AND have >=2 paragraphs AND have vocab data
shape_eligible = {f for f, recs in folio_para_groups.items() if len(recs) >= 2}
common_folios = sorted(manifold_folios & shape_eligible & set(folio_classified_middles.keys()))
n_folios = len(common_folios)
print(f'\n  Common folios (manifold & shape & vocab, >=2 paras): {n_folios}')

folio_shapes_full = {}
folio_shapes_reduced = {}

for fid in common_folios:
    recs = folio_para_groups[fid]

    # Zone type proportions (4-dim)
    zc = folio_zone_counts.get(fid, Counter())
    z_total = sum(zc.values())
    zone_props = np.array([zc.get(i, 0) / max(z_total, 1) for i in range(4)])

    # Header atom profile mean (10-dim)
    hdr_vecs = [r['hdr_fracs'] for r in recs if r['hdr_fracs'] is not None]
    hdr_mean = np.mean(hdr_vecs, axis=0) if hdr_vecs else np.zeros(10)

    # Line-length gradient slope
    if len(recs) >= 3:
        ordinals = np.array([r['ordinal'] for r in recs], dtype=float)
        line_lens = np.array([r['mean_body_line_len'] for r in recs])
        ll_slope = float(spearmanr(ordinals, line_lens)[0]) if np.std(ordinals) > 0 else 0.0
    else:
        ll_slope = 0.0

    # Paragraph count
    n_paras = len(recs)

    # Gallows type distribution (4-dim)
    g_counts = Counter(r['gallows'] for r in recs)
    g_total = sum(g_counts.values())
    g_props = np.array([g_counts.get(g, 0) / max(g_total, 1) for g in GALLOWS_TYPES])

    # Specification intensity
    spec_scores = []
    for r in recs:
        if r['hdr_fracs'] is not None:
            spec_scores.append(r['hdr_fracs'][3] + r['hdr_fracs'][4] + r['hdr_fracs'][5] + r['hdr_fracs'][7])
    spec_intensity = np.mean(spec_scores) if spec_scores else 0

    # Suffix mode A fraction
    mode_a_vals = [r['mode_a_frac'] for r in recs]
    mode_a_mean = np.mean(mode_a_vals) if mode_a_vals else 0.5

    # Full shape vector (22-dim)
    full_vec = np.concatenate([
        zone_props, hdr_mean, [ll_slope], [n_paras], g_props, [spec_intensity], [mode_a_mean],
    ])
    # Reduced shape vector (10-dim, no atom features)
    reduced_vec = np.concatenate([
        zone_props, [ll_slope], [n_paras], g_props,
    ])

    folio_shapes_full[fid] = full_vec
    folio_shapes_reduced[fid] = reduced_vec

# ============================================================
# BLOCK 1: DISTANCE MATRIX CONSTRUCTION
# ============================================================
print('\n' + '='*60)
print('BLOCK 1: Distance Matrix Construction')

# Manifold distance
manifold_matrix = np.array([[manifold_scores[f][pc] for pc in MANIFOLD_PCS] for f in common_folios])
D_manifold = squareform(pdist(manifold_matrix, 'euclidean'))

# Shape distances (z-score then Euclidean)
full_matrix = np.array([folio_shapes_full[f] for f in common_folios])
reduced_matrix = np.array([folio_shapes_reduced[f] for f in common_folios])
full_z = (full_matrix - full_matrix.mean(axis=0)) / (full_matrix.std(axis=0) + 1e-10)
reduced_z = (reduced_matrix - reduced_matrix.mean(axis=0)) / (reduced_matrix.std(axis=0) + 1e-10)
D_shape_full = squareform(pdist(full_z, 'euclidean'))
D_shape_reduced = squareform(pdist(reduced_z, 'euclidean'))

# Vocabulary distances (Jaccard on classified MIDDLEs)
D_vocab = build_jaccard_dist(common_folios, folio_classified_middles)
D_bridge = build_jaccard_dist(common_folios, folio_bridge_middles)
D_dark = build_jaccard_dist(common_folios, folio_dark_middles)

# PREFIX distribution distance (JSD)
prefix_vectors = []
all_prefixes = sorted(set(p for f in common_folios for p in folio_prefix_counts[f].keys()))
for f in common_folios:
    total = sum(folio_prefix_counts[f].values())
    vec = np.array([folio_prefix_counts[f].get(p, 0) / max(total, 1) for p in all_prefixes])
    vec = vec + 1e-10  # avoid zero for JSD
    vec = vec / vec.sum()
    prefix_vectors.append(vec)
prefix_matrix = np.array(prefix_vectors)
D_prefix = squareform(pdist(prefix_matrix, jensenshannon))

# Section distance (0/1)
sections = [folio_sections[f] for f in common_folios]
D_section = np.zeros((n_folios, n_folios))
for i in range(n_folios):
    for j in range(n_folios):
        D_section[i, j] = 0 if sections[i] == sections[j] else 1

print(f'  Vocab Jaccard range: [{D_vocab[np.triu_indices(n_folios, k=1)].min():.3f}, {D_vocab[np.triu_indices(n_folios, k=1)].max():.3f}]')
print(f'  Shape full range: [{D_shape_full[np.triu_indices(n_folios, k=1)].min():.3f}, {D_shape_full[np.triu_indices(n_folios, k=1)].max():.3f}]')
print(f'  Manifold range: [{D_manifold[np.triu_indices(n_folios, k=1)].min():.3f}, {D_manifold[np.triu_indices(n_folios, k=1)].max():.3f}]')
print(f'  Block 1 complete ({time.time()-t0:.1f}s)')

results = {'n_folios': n_folios, 'folio_list': common_folios}

# ============================================================
# BLOCK 2: INDIVIDUAL CHANNEL MANTELS
# ============================================================
print('\n' + '='*60)
print('BLOCK 2: Individual Channel Mantels')

# T1: Vocabulary -> Manifold
print('\nT1: Vocabulary -> Manifold')
r, p, z, nm, ns = mantel_test(D_vocab, D_manifold)
pr, pp, pz = partial_mantel(D_vocab, D_manifold, [D_section])
print(f'  Mantel r={r:.4f}, p={p:.4f}, z={z:.2f}')
print(f'  Partial|section r={pr:.4f}, p={pp:.4f}, z={pz:.2f}')
results['T1'] = {'r': r, 'p': p, 'z': z, 'partial_r': pr, 'partial_p': pp, 'partial_z': pz}

# T2: Shape -> Manifold (replicate C1796)
print('\nT2: Paragraph shape -> Manifold')
r, p, z, nm, ns = mantel_test(D_shape_full, D_manifold)
pr, pp, pz = partial_mantel(D_shape_full, D_manifold, [D_section])
print(f'  Mantel r={r:.4f}, p={p:.4f}, z={z:.2f}')
print(f'  Partial|section r={pr:.4f}, p={pp:.4f}, z={pz:.2f}')
results['T2'] = {'r': r, 'p': p, 'z': z, 'partial_r': pr, 'partial_p': pp, 'partial_z': pz}

# T3: Vocabulary <-> Shape (channel independence)
print('\nT3: Vocabulary <-> Shape (channel independence)')
r, p, z, nm, ns = mantel_test(D_vocab, D_shape_full)
pr, pp, pz = partial_mantel(D_vocab, D_shape_full, [D_section])
print(f'  Mantel r={r:.4f}, p={p:.4f}, z={z:.2f}')
print(f'  Partial|section r={pr:.4f}, p={pp:.4f}, z={pz:.2f}')
interp = 'INDEPENDENT' if r < 0.20 else ('PARTIAL_OVERLAP' if r < 0.40 else 'REDUNDANT')
print(f'  Interpretation: {interp}')
results['T3'] = {'r': r, 'p': p, 'z': z, 'partial_r': pr, 'partial_p': pp, 'interpretation': interp}

# T3b: PREFIX confound diagnostic
print('\nT3b: PREFIX confound diagnostic')
idx = np.triu_indices(n_folios, k=1)
pfx_flat = D_prefix[idx]
vocab_flat = D_vocab[idx]
shape_flat = D_shape_full[idx]
pfx_vocab_r = float(np.corrcoef(pfx_flat, vocab_flat)[0, 1])
pfx_shape_r = float(np.corrcoef(pfx_flat, shape_flat)[0, 1])
print(f'  PREFIX-Vocab correlation: r={pfx_vocab_r:.4f}')
print(f'  PREFIX-Shape correlation: r={pfx_shape_r:.4f}')
pfx_confound = pfx_vocab_r > 0.50 and pfx_shape_r > 0.50
print(f'  PREFIX confound: {"YES" if pfx_confound else "NO"}')
results['T3b'] = {
    'prefix_vocab_r': pfx_vocab_r, 'prefix_shape_r': pfx_shape_r,
    'confounded': pfx_confound,
}

print(f'\n  Block 2 complete ({time.time()-t0:.1f}s)')

# ============================================================
# BLOCK 3: COMBINED CHANNEL TEST
# ============================================================
print('\n' + '='*60)
print('BLOCK 3: Combined Channel Test')

# Z-score distance matrices on upper triangle for combination
vocab_ut = D_vocab[idx]
shape_ut = D_shape_full[idx]
vocab_z = (vocab_ut - vocab_ut.mean()) / (vocab_ut.std() + 1e-10)
shape_z = (shape_ut - shape_ut.mean()) / (shape_ut.std() + 1e-10)

# T4: Combined at alpha=0.5 (pre-registered)
print('\nT4: Combined distance -> Manifold (alpha=0.5 pre-registered)')
combined_05 = 0.5 * vocab_z + 0.5 * shape_z
D_combined_05 = np.zeros((n_folios, n_folios))
D_combined_05[idx] = combined_05
D_combined_05 = D_combined_05 + D_combined_05.T

r_combined_05, p_05, z_05, nm_05, ns_05 = mantel_test(D_combined_05, D_manifold)
print(f'  alpha=0.5: r={r_combined_05:.4f}, p={p_05:.4f}, z={z_05:.2f}')

max_individual = max(results['T1']['r'], results['T2']['r'])
improvement = r_combined_05 - max_individual
print(f'  max(T1,T2) = {max_individual:.4f}, improvement = {improvement:+.4f}')
t4_pass = improvement > 0.05
print(f'  T4 PASS (>+0.05): {t4_pass}')

# Exploratory: alpha curve
print('\n  Alpha curve (exploratory):')
alpha_curve = {}
for alpha_10 in range(0, 11):
    alpha = alpha_10 / 10.0
    comb = alpha * vocab_z + (1 - alpha) * shape_z
    D_comb = np.zeros((n_folios, n_folios))
    D_comb[idx] = comb
    D_comb = D_comb + D_comb.T
    r_comb = float(np.corrcoef(D_comb[idx], D_manifold[idx])[0, 1])
    alpha_curve[f'{alpha:.1f}'] = round(r_comb, 4)
    print(f'    alpha={alpha:.1f}: r={r_comb:.4f}')

best_alpha = max(alpha_curve, key=alpha_curve.get)
best_r = alpha_curve[best_alpha]
print(f'  Best alpha={best_alpha}, r={best_r:.4f}')

results['T4'] = {
    'r_alpha05': r_combined_05, 'p_alpha05': p_05, 'z_alpha05': z_05,
    'max_individual': max_individual, 'improvement': improvement, 'pass': t4_pass,
    'alpha_curve': alpha_curve, 'best_alpha': float(best_alpha), 'best_r': best_r,
}

# T4-null: permutation null for combined improvement
print('\nT4-null: Permutation null for combined improvement')
n_null = 1000
rng = np.random.default_rng(42)
manifold_ut = D_manifold[idx]
null_improvements = []
for ni in range(n_null):
    # Permute one channel
    perm = rng.permutation(n_folios)
    D_vocab_perm = D_vocab[np.ix_(perm, perm)]
    vocab_perm_ut = D_vocab_perm[idx]
    vocab_perm_z = (vocab_perm_ut - vocab_perm_ut.mean()) / (vocab_perm_ut.std() + 1e-10)
    # Best alpha for permuted combination
    best_null_r = -1
    for alpha_10 in range(0, 11):
        alpha = alpha_10 / 10.0
        comb = alpha * vocab_perm_z + (1 - alpha) * shape_z
        r_c = float(np.corrcoef(comb, manifold_ut)[0, 1])
        if r_c > best_null_r:
            best_null_r = r_c
    # Individual channel rs for this permutation
    r_vocab_perm = float(np.corrcoef(vocab_perm_ut, manifold_ut)[0, 1])
    r_shape = results['T2']['r']  # shape unchanged
    max_indiv_null = max(r_vocab_perm, r_shape)
    null_improvements.append(best_null_r - max_indiv_null)

null_improvements = np.array(null_improvements)
frac_exceeding = float(np.mean(null_improvements >= improvement))
print(f'  Observed improvement: {improvement:+.4f}')
print(f'  Null improvement mean: {null_improvements.mean():+.4f}, std: {null_improvements.std():.4f}')
print(f'  Fraction of nulls >= observed: {frac_exceeding:.4f}')
t4_null_pass = frac_exceeding < 0.05
print(f'  T4-null PASS (<5%): {t4_null_pass}')

results['T4_null'] = {
    'frac_exceeding': frac_exceeding, 'null_mean': float(null_improvements.mean()),
    'null_std': float(null_improvements.std()), 'pass': t4_null_pass,
}

# T5: Partial Mantel: shape | vocabulary
print('\nT5: shape | vocabulary')
r5, p5, z5 = partial_mantel(D_shape_full, D_manifold, [D_vocab])
print(f'  Partial r={r5:.4f}, p={p5:.4f}, z={z5:.2f}')
t5_pass = r5 > 0.10 and p5 < 0.05
print(f'  T5 PASS (r>0.10, p<0.05): {t5_pass}')
results['T5'] = {'partial_r': r5, 'p': p5, 'z': z5, 'pass': t5_pass}

# T6: Partial Mantel: vocabulary | shape
print('\nT6: vocabulary | shape')
r6, p6, z6 = partial_mantel(D_vocab, D_manifold, [D_shape_full])
print(f'  Partial r={r6:.4f}, p={p6:.4f}, z={z6:.2f}')
t6_pass = r6 > 0.10 and p6 < 0.05
print(f'  T6 PASS (r>0.10, p<0.05): {t6_pass}')
results['T6'] = {'partial_r': r6, 'p': p6, 'z': z6, 'pass': t6_pass}

print(f'\n  Block 3 complete ({time.time()-t0:.1f}s)')

# ============================================================
# BLOCK 4: FEATURE DECOMPOSITION
# ============================================================
print('\n' + '='*60)
print('BLOCK 4: Feature Decomposition')

# T7: Bridge-only vocab -> Manifold
print('\nT7: Bridge-only vocab -> Manifold')
r7, p7, z7, _, _ = mantel_test(D_bridge, D_manifold)
print(f'  Mantel r={r7:.4f}, p={p7:.4f}, z={z7:.2f}')
results['T7'] = {'r': r7, 'p': p7, 'z': z7}

# T8: Dark-only vocab -> Manifold
print('\nT8: Dark-only vocab -> Manifold')
r8, p8, z8, _, _ = mantel_test(D_dark, D_manifold)
print(f'  Mantel r={r8:.4f}, p={p8:.4f}, z={z8:.2f}')
results['T8'] = {'r': r8, 'p': p8, 'z': z8}

print(f'  Bridge > Dark: {r7 > r8}')

# T9: Reduced shape (no atoms) | vocabulary
print('\nT9: Reduced shape (no atoms) | vocabulary')
r9, p9, z9 = partial_mantel(D_shape_reduced, D_manifold, [D_vocab])
print(f'  Partial r={r9:.4f}, p={p9:.4f}, z={z9:.2f}')
t9_pass = r9 > 0.05
print(f'  Reduced shape adds beyond vocab: {t9_pass}')
results['T9'] = {'partial_r': r9, 'p': p9, 'z': z9}

print(f'\n  Block 4 complete ({time.time()-t0:.1f}s)')

# ============================================================
# BLOCK 5: SECTION CONTROL (critical)
# ============================================================
print('\n' + '='*60)
print('BLOCK 5: Section Control')

# T10a: vocab | section -> manifold
print('\nT10a: vocab | section -> Manifold')
r10a, p10a, z10a = partial_mantel(D_vocab, D_manifold, [D_section])
retention_a = r10a / results['T1']['r'] if results['T1']['r'] > 0 else 0
print(f'  Partial r={r10a:.4f}, p={p10a:.4f} (retention: {retention_a:.1%})')
results['T10a'] = {'partial_r': r10a, 'p': p10a, 'z': z10a, 'retention': retention_a}

# T10b: shape | section -> manifold
print('\nT10b: shape | section -> Manifold')
r10b, p10b, z10b = partial_mantel(D_shape_full, D_manifold, [D_section])
retention_b = r10b / results['T2']['r'] if results['T2']['r'] > 0 else 0
print(f'  Partial r={r10b:.4f}, p={p10b:.4f} (retention: {retention_b:.1%})')
results['T10b'] = {'partial_r': r10b, 'p': p10b, 'z': z10b, 'retention': retention_b}

# T10c: combined | section -> manifold
print('\nT10c: combined | section -> Manifold')
r10c, p10c, z10c = partial_mantel(D_combined_05, D_manifold, [D_section])
retention_c = r10c / r_combined_05 if r_combined_05 > 0 else 0
print(f'  Partial r={r10c:.4f}, p={p10c:.4f} (retention: {retention_c:.1%})')
results['T10c'] = {'partial_r': r10c, 'p': p10c, 'z': z10c, 'retention': retention_c}

# T10d: Within-Herbal Mantel
print('\nT10d: Within-Herbal Mantels')
herbal_idx = [i for i, f in enumerate(common_folios) if folio_sections[f] == 'Herbal']
n_herbal = len(herbal_idx)
print(f'  Herbal folios: {n_herbal}')

if n_herbal >= 10:
    h_idx = np.array(herbal_idx)
    D_vocab_h = D_vocab[np.ix_(h_idx, h_idx)]
    D_shape_h = D_shape_full[np.ix_(h_idx, h_idx)]
    D_mani_h = D_manifold[np.ix_(h_idx, h_idx)]

    # Within-Herbal vocab
    r_hv, p_hv, z_hv, _, _ = mantel_test(D_vocab_h, D_mani_h, n_perms=5000)
    # Within-Herbal shape
    r_hs, p_hs, z_hs, _, _ = mantel_test(D_shape_h, D_mani_h, n_perms=5000)
    # Within-Herbal combined
    vocab_h_ut = D_vocab_h[np.triu_indices(n_herbal, k=1)]
    shape_h_ut = D_shape_h[np.triu_indices(n_herbal, k=1)]
    vocab_hz = (vocab_h_ut - vocab_h_ut.mean()) / (vocab_h_ut.std() + 1e-10)
    shape_hz = (shape_h_ut - shape_h_ut.mean()) / (shape_h_ut.std() + 1e-10)
    comb_h = 0.5 * vocab_hz + 0.5 * shape_hz
    D_comb_h = np.zeros((n_herbal, n_herbal))
    D_comb_h[np.triu_indices(n_herbal, k=1)] = comb_h
    D_comb_h = D_comb_h + D_comb_h.T
    r_hc, p_hc, z_hc, _, _ = mantel_test(D_comb_h, D_mani_h, n_perms=5000)

    print(f'  Vocab: r={r_hv:.4f}, p={p_hv:.4f}')
    print(f'  Shape: r={r_hs:.4f}, p={p_hs:.4f}')
    print(f'  Combined: r={r_hc:.4f}, p={p_hc:.4f}')
    results['T10d'] = {
        'n_herbal': n_herbal,
        'vocab': {'r': r_hv, 'p': p_hv, 'z': z_hv},
        'shape': {'r': r_hs, 'p': p_hs, 'z': z_hs},
        'combined': {'r': r_hc, 'p': p_hc, 'z': z_hc},
    }
else:
    print(f'  Herbal too small ({n_herbal}), skipping')
    results['T10d'] = {'n_herbal': n_herbal, 'skipped': True}

# Section control pass/fail
t10_pass = (retention_a > 0.50 and retention_b > 0.50 and retention_c > 0.50)
print(f'\n  Section retention: vocab={retention_a:.1%}, shape={retention_b:.1%}, combined={retention_c:.1%}')
print(f'  T10 PASS (>50% retention): {t10_pass}')
results['T10_pass'] = t10_pass

print(f'\n  Block 5 complete ({time.time()-t0:.1f}s)')

# ============================================================
# BLOCK 6: PREFIX MEDIATION ANALYSIS
# ============================================================
print('\n' + '='*60)
print('BLOCK 6: PREFIX Mediation Analysis')

# T11a: vocab|PREFIX -> manifold (does vocab carry signal beyond PREFIX?)
print('\nT11a: vocab | PREFIX -> Manifold')
r11a, p11a, z11a = partial_mantel(D_vocab, D_manifold, [D_prefix])
print(f'  Partial r={r11a:.4f}, p={p11a:.4f}, z={z11a:.2f}')
results['T11a'] = {'partial_r': r11a, 'p': p11a, 'z': z11a}

# T11b: shape|PREFIX -> manifold (does shape carry signal beyond PREFIX?)
print('\nT11b: shape | PREFIX -> Manifold')
r11b, p11b, z11b = partial_mantel(D_shape_full, D_manifold, [D_prefix])
print(f'  Partial r={r11b:.4f}, p={p11b:.4f}, z={z11b:.2f}')
results['T11b'] = {'partial_r': r11b, 'p': p11b, 'z': z11b}

# T11c: vocab|(PREFIX+shape) -> manifold (does vocab add ANYTHING after PREFIX and shape?)
print('\nT11c: vocab | (PREFIX + shape) -> Manifold')
r11c, p11c, z11c = partial_mantel(D_vocab, D_manifold, [D_prefix, D_shape_full])
print(f'  Partial r={r11c:.4f}, p={p11c:.4f}, z={z11c:.2f}')
vocab_survives = r11c > 0.05 and p11c < 0.05
print(f'  Vocab survives PREFIX+shape control: {vocab_survives}')
results['T11c'] = {'partial_r': r11c, 'p': p11c, 'z': z11c, 'survives': vocab_survives}

# T11d: shape|(PREFIX+vocab) -> manifold (does shape add beyond PREFIX and vocab?)
print('\nT11d: shape | (PREFIX + vocab) -> Manifold')
r11d, p11d, z11d = partial_mantel(D_shape_full, D_manifold, [D_prefix, D_vocab])
print(f'  Partial r={r11d:.4f}, p={p11d:.4f}, z={z11d:.2f}')
shape_survives = r11d > 0.05 and p11d < 0.05
print(f'  Shape survives PREFIX+vocab control: {shape_survives}')
results['T11d'] = {'partial_r': r11d, 'p': p11d, 'z': z11d, 'survives': shape_survives}

# T11e: PREFIX -> manifold (how much does PREFIX itself predict?)
print('\nT11e: PREFIX -> Manifold (baseline)')
r11e, p11e, z11e, _, _ = mantel_test(D_prefix, D_manifold)
pr11e, pp11e, pz11e = partial_mantel(D_prefix, D_manifold, [D_section])
print(f'  Mantel r={r11e:.4f}, p={p11e:.4f}, z={z11e:.2f}')
print(f'  Partial|section r={pr11e:.4f}, p={pp11e:.4f}')
results['T11e'] = {'r': r11e, 'p': p11e, 'z': z11e, 'partial_r': pr11e, 'partial_p': pp11e}

# T11f: Within-Herbal PREFIX mediation
print('\nT11f: Within-Herbal PREFIX mediation')
if n_herbal >= 10:
    h_idx_arr = np.array(herbal_idx)
    D_prefix_h = D_prefix[np.ix_(h_idx_arr, h_idx_arr)]
    D_vocab_h = D_vocab[np.ix_(h_idx_arr, h_idx_arr)]
    D_shape_h = D_shape_full[np.ix_(h_idx_arr, h_idx_arr)]
    D_mani_h = D_manifold[np.ix_(h_idx_arr, h_idx_arr)]

    # vocab|PREFIX within Herbal
    r_hva, p_hva, z_hva = partial_mantel(D_vocab_h, D_mani_h, [D_prefix_h], n_perms=5000)
    # shape|PREFIX within Herbal
    r_hsa, p_hsa, z_hsa = partial_mantel(D_shape_h, D_mani_h, [D_prefix_h], n_perms=5000)
    print(f'  Herbal vocab|PREFIX: r={r_hva:.4f}, p={p_hva:.4f}')
    print(f'  Herbal shape|PREFIX: r={r_hsa:.4f}, p={p_hsa:.4f}')
    results['T11f'] = {
        'herbal_vocab_pfx': {'partial_r': r_hva, 'p': p_hva, 'z': z_hva},
        'herbal_shape_pfx': {'partial_r': r_hsa, 'p': p_hsa, 'z': z_hsa},
    }
else:
    print('  Herbal too small, skipping')
    results['T11f'] = {'skipped': True}

# Summary
print(f'\n  PREFIX mediation summary:')
print(f'    PREFIX -> manifold: r={r11e:.4f}')
print(f'    vocab|PREFIX: r={r11a:.4f} (raw vocab r={results["T1"]["r"]:.4f}, drop={results["T1"]["r"]-r11a:.4f})')
print(f'    shape|PREFIX: r={r11b:.4f} (raw shape r={results["T2"]["r"]:.4f}, drop={results["T2"]["r"]-r11b:.4f})')
print(f'    vocab|(PREFIX+shape): r={r11c:.4f} {"SURVIVES" if vocab_survives else "ABSORBED"}')
print(f'    shape|(PREFIX+vocab): r={r11d:.4f} {"SURVIVES" if shape_survives else "ABSORBED"}')

print(f'\n  Block 6 complete ({time.time()-t0:.1f}s)')

# ============================================================
# VERDICT
# ============================================================
print('\n' + '='*60)
print('VERDICT')

t3_pass = results['T3']['r'] < 0.30
t3b_pass = not results['T3b']['confounded']

# Updated verdict logic incorporating PREFIX mediation (Block 6)
if results['T3b']['confounded'] or not t10_pass:
    verdict = 'CONFOUNDED'
    reason = 'PREFIX confound' if results['T3b']['confounded'] else 'section collapse'
elif shape_survives and not vocab_survives:
    verdict = 'DEPLOYMENT_DOMINANT'
    reason = f'shape survives PREFIX+vocab (r={r11d:.3f}), vocab absorbed (r={r11c:.3f})'
elif shape_survives and vocab_survives:
    if t4_null_pass and t5_pass and t6_pass and t10_pass:
        verdict = 'TWO_CHANNEL_PARTIAL'
        reason = f'both survive PREFIX mediation, combined improvement real (p={frac_exceeding:.3f})'
    else:
        verdict = 'PARTIAL'
        reason = f'both survive PREFIX but combination weak'
elif not shape_survives and vocab_survives:
    verdict = 'VOCABULARY_DOMINANT'
    reason = f'vocab survives (r={r11c:.3f}), shape absorbed (r={r11d:.3f})'
else:
    verdict = 'PREFIX_MEDIATED'
    reason = 'neither channel survives PREFIX+other control'

print(f'\n  VERDICT: {verdict} ({reason})')
print(f'\n  T1 vocab->manifold: r={results["T1"]["r"]:.4f}')
print(f'  T2 shape->manifold: r={results["T2"]["r"]:.4f}')
print(f'  T3 vocab<->shape:   r={results["T3"]["r"]:.4f} ({results["T3"]["interpretation"]})')
print(f'  T3b PREFIX confound: vocab={results["T3b"]["prefix_vocab_r"]:.3f}, shape={results["T3b"]["prefix_shape_r"]:.3f}')
print(f'  T4 combined(0.5):   r={r_combined_05:.4f} (improvement={improvement:+.4f}, pass={t4_pass})')
print(f'  T4-null:            frac={frac_exceeding:.4f} (pass={t4_null_pass})')
print(f'  T5 shape|vocab:     r={r5:.4f} (pass={t5_pass})')
print(f'  T6 vocab|shape:     r={r6:.4f} (pass={t6_pass})')
print(f'  T7 bridge:          r={r7:.4f}')
print(f'  T8 dark:            r={r8:.4f}')
print(f'  T10 section retention: {retention_a:.1%}/{retention_b:.1%}/{retention_c:.1%}')

results['verdict'] = verdict
results['reason'] = reason
results['runtime_s'] = round(time.time() - t0, 1)

# Save results
out_path = PROJECT_ROOT / 'phases' / 'TWO_CHANNEL_APPARATUS_ENCODING' / 'results' / 'two_channel_encoding_results.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f'\nResults saved to {out_path}')
print(f'Total runtime: {time.time()-t0:.1f}s')
