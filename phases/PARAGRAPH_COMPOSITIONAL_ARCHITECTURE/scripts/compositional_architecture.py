"""
Phase 615: Paragraph Compositional Architecture
Tests how paragraphs compose into folio-level programs via two approaches:
  Block A: Header specification transition grammar (sequential)
  Block B: Paragraph shape -> apparatus manifold (aggregate)

Produces: compositional_architecture_results.json
"""
import sys; sys.path.insert(0, '.')
import json
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.spatial.distance import pdist, squareform
from scipy.stats import chi2_contingency, spearmanr
from numpy.linalg import lstsq
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from collections import Counter, defaultdict
from scripts.voynich import Transcript, BFolioDecoder, Morphology

PROJECT_ROOT = Path('.')
tx = Transcript()
decoder = BFolioDecoder()
morph = Morphology()

folio_sections = {}
for tok in tx.currier_b():
    if tok.folio not in folio_sections:
        folio_sections[tok.folio] = tok.section

SECTION_MAP = {'S': 'Stars', 'B': 'Bio', 'H': 'Herbal', 'T': 'Cosmo', 'C': 'Cosmo'}
GALLOWS_SET = set('ktpf')
ATOMS = list('kethpfocda')

ATOM_CATEGORY = {
    'k': 'THERMAL', 'e': 'THERMAL', 'q': 'THERMAL',
    'h': 'MONITORING', 'c': 'MONITORING',
    'd': 'CONTAINMENT', 'y': 'CONTAINMENT',
    't': 'TRANSITION',
    'n': 'OPERATION', 'i': 'OPERATION', 'g': 'OPERATION', 'x': 'OPERATION',
    'a': 'STAGING', 'o': 'STAGING', 's': 'STAGING',
    'l': 'FLOW', 'r': 'FLOW',
    'm': 'MARKING', 'p': 'MARKING', 'f': 'MARKING',
}
CATEGORIES = ['THERMAL', 'CONTAINMENT', 'MONITORING', 'TRANSITION',
              'OPERATION', 'STAGING', 'FLOW', 'MARKING']

def atom_fracs_from_tokens(token_list):
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

def assign_category(middle):
    if not middle:
        return None
    votes = Counter()
    for ch in middle:
        cat = ATOM_CATEGORY.get(ch)
        if cat:
            votes[cat] += 1
    return votes.most_common(1)[0][0] if votes else None

def category_fracs_from_tokens(token_list):
    cats = []
    for w in token_list:
        m = morph.extract(w)
        cat = assign_category(m.middle)
        if cat:
            cats.append(cat)
    if len(cats) < 3:
        return None
    counts = Counter(cats)
    total = sum(counts.values())
    return np.array([counts.get(c, 0) / total for c in CATEGORIES])

def cosine_sim(a, b):
    dot = np.dot(a, b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0
    return dot / (na * nb)

def mantel_test(D1, D2, n_perm=1000):
    """Mantel test: correlation between two distance matrices."""
    n = D1.shape[0]
    idx = np.triu_indices(n, k=1)
    v1 = D1[idx]
    v2 = D2[idx]
    r_obs, _ = stats.pearsonr(v1, v2)
    rng = np.random.default_rng(42)
    null_rs = []
    for _ in range(n_perm):
        perm = rng.permutation(n)
        D2_perm = D2[np.ix_(perm, perm)]
        null_rs.append(stats.pearsonr(v1, D2_perm[idx])[0])
    null_rs = np.array(null_rs)
    p_val = float(np.mean(null_rs >= r_obs))
    z = float((r_obs - np.mean(null_rs)) / (np.std(null_rs) + 1e-10))
    return float(r_obs), p_val, z

def partial_mantel(D1, D2, D_control, n_perm=1000):
    """Partial Mantel: D1 vs D2 controlling for D_control."""
    n = D1.shape[0]
    idx = np.triu_indices(n, k=1)
    v1, v2, vc = D1[idx], D2[idx], D_control[idx]
    # Residualize v1 and v2 on vc
    def resid(y, x):
        slope = np.cov(y, x)[0, 1] / (np.var(x) + 1e-10)
        return y - slope * x
    r1 = resid(v1, vc)
    r2 = resid(v2, vc)
    r_obs = float(stats.pearsonr(r1, r2)[0])
    rng = np.random.default_rng(42)
    null_rs = []
    for _ in range(n_perm):
        perm = rng.permutation(n)
        D2_perm = D2[np.ix_(perm, perm)]
        r2_perm = resid(D2_perm[idx], vc)
        null_rs.append(stats.pearsonr(r1, r2_perm)[0])
    null_rs = np.array(null_rs)
    p_val = float(np.mean(null_rs >= r_obs))
    z = float((r_obs - np.mean(null_rs)) / (np.std(null_rs) + 1e-10))
    return r_obs, p_val, z

# ============================================================
# DATA EXTRACTION
# ============================================================
print('Extracting paragraph data...')

records = []  # per-paragraph records
for fid in sorted(folio_sections.keys()):
    sec = SECTION_MAP.get(folio_sections[fid], folio_sections[fid])
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
        body_cats = category_fracs_from_tokens(body_toks)
        if body_fracs is None:
            continue

        # Suffix mode A fraction (count mode A lines / total body lines)
        mode_a_count = 0
        mode_total = 0
        for li in range(1, len(p.lines)):
            sm = p.lines[li].suffix_mode
            if sm in ('A', 'B'):
                mode_total += 1
                if sm == 'A':
                    mode_a_count += 1
        mode_a_frac = mode_a_count / mode_total if mode_total > 0 else 0.5

        records.append({
            'folio': fid,
            'section': sec,
            'ordinal': pi,
            'rel_pos': pi / max(n_paras - 1, 1),
            'n_paras': n_paras,
            'gallows': bt[0],
            'hdr_fracs': hdr_fracs,
            'body_fracs': body_fracs,
            'body_cats': body_cats,
            'n_body_lines': len(body_line_lens),
            'mean_body_line_len': np.mean(body_line_lens) if body_line_lens else 0,
            'mode_a_frac': mode_a_frac,
            'n_header_tokens': len(hdr_all),
        })

print(f'  Paragraphs extracted: {len(records)}')

# Group by folio for sequential tests
folio_groups = defaultdict(list)
for r in records:
    folio_groups[r['folio']].append(r)
for fid in folio_groups:
    folio_groups[fid].sort(key=lambda x: x['ordinal'])

results = {'n_paragraphs': len(records), 'n_folios': len(folio_groups)}

# ============================================================
# BLOCK A: HEADER SPECIFICATION TRANSITION GRAMMAR
# ============================================================
print('\n' + '='*60)
print('BLOCK A: Header Specification Transition Grammar')

# --- A1.5: Cluster-gallows independence ---
print('\nA1.5: Cluster-gallows independence check')
hdr_valid = [r for r in records if r['hdr_fracs'] is not None]
hdr_matrix = np.array([r['hdr_fracs'] for r in hdr_valid])

km = KMeans(n_clusters=3, random_state=42, n_init=10)
cluster_labels = km.fit_predict(hdr_matrix)
gallows_labels = [r['gallows'] for r in hdr_valid]

# Map gallows to integers for ARI
g_map = {'k': 0, 't': 1, 'p': 2, 'f': 3}
gallows_int = [g_map[g] for g in gallows_labels]
ari = adjusted_rand_score(gallows_int, cluster_labels)
print(f'  ARI(gallows, header_cluster) = {ari:.4f}')
print(f'  {"PASS: clusters independent" if ari < 0.5 else "FAIL: clusters are gallows-determined"}')

# Assign cluster labels to valid records
cluster_map = {}
for i, r in enumerate(hdr_valid):
    cluster_map[id(r)] = int(cluster_labels[i])
for r in records:
    r['hdr_cluster'] = cluster_map.get(id(r), -1)

results['A1_5'] = {'ari': float(ari), 'pass': ari < 0.5}

# --- A1: Full header transition matrix ---
print('\nA1: Full header transition matrix')
GALLOWS_TYPES = ['k', 't', 'p', 'f']

# Gallows-only transitions (baseline)
g_trans = np.zeros((4, 4), dtype=int)
# Expanded: (gallows, cluster) transitions
n_states = 4 * 3  # 12 states
exp_trans = np.zeros((n_states, n_states), dtype=int)

def state_idx(gallows, cluster):
    return GALLOWS_TYPES.index(gallows) * 3 + cluster

all_transitions = 0
for fid, recs in folio_groups.items():
    valid = [r for r in recs if r['hdr_cluster'] >= 0]
    for j in range(len(valid) - 1):
        r1, r2 = valid[j], valid[j + 1]
        gi1, gi2 = GALLOWS_TYPES.index(r1['gallows']), GALLOWS_TYPES.index(r2['gallows'])
        g_trans[gi1, gi2] += 1
        si1 = state_idx(r1['gallows'], r1['hdr_cluster'])
        si2 = state_idx(r2['gallows'], r2['hdr_cluster'])
        exp_trans[si1, si2] += 1
        all_transitions += 1

print(f'  Total transitions: {all_transitions}')

# Chi-squared for gallows-only
if g_trans.sum() > 0:
    chi2_g, p_g, _, _ = chi2_contingency(g_trans)
    V_g = float(np.sqrt(chi2_g / (g_trans.sum() * 3)))
    print(f'  Gallows-only: chi2={chi2_g:.2f}, V={V_g:.3f}, p={p_g:.6f}')
else:
    chi2_g, V_g, p_g = 0, 0, 1

# Chi-squared for expanded (remove zero-sum rows/cols)
mask_r = exp_trans.sum(axis=1) > 0
mask_c = exp_trans.sum(axis=0) > 0
mask = mask_r & mask_c
exp_sub = exp_trans[np.ix_(mask, mask)]
if exp_sub.shape[0] >= 2 and exp_sub.sum() > 0:
    chi2_e, p_e, dof_e, _ = chi2_contingency(exp_sub)
    V_e = float(np.sqrt(chi2_e / (exp_sub.sum() * (min(exp_sub.shape) - 1))))
    print(f'  Expanded (gallows x cluster): chi2={chi2_e:.2f}, V={V_e:.3f}, p={p_e:.6f}, states={exp_sub.shape[0]}')
else:
    chi2_e, V_e, p_e = 0, 0, 1

# Permutation null: shuffle within-folio paragraph order
n_perm = 500
rng = np.random.default_rng(42)
null_chi2_e = []
for _ in range(n_perm):
    perm_trans = np.zeros((n_states, n_states), dtype=int)
    for fid, recs in folio_groups.items():
        valid = [r for r in recs if r['hdr_cluster'] >= 0]
        if len(valid) < 2:
            continue
        perm_order = rng.permutation(len(valid))
        for j in range(len(perm_order) - 1):
            r1, r2 = valid[perm_order[j]], valid[perm_order[j + 1]]
            si1 = state_idx(r1['gallows'], r1['hdr_cluster'])
            si2 = state_idx(r2['gallows'], r2['hdr_cluster'])
            perm_trans[si1, si2] += 1
    pm_r = perm_trans.sum(axis=1) > 0
    pm_c = perm_trans.sum(axis=0) > 0
    pm = pm_r & pm_c
    ps = perm_trans[np.ix_(pm, pm)]
    if ps.shape[0] >= 2 and ps.sum() > 0:
        null_chi2_e.append(chi2_contingency(ps)[0])
    else:
        null_chi2_e.append(0)

null_chi2_e = np.array(null_chi2_e)
perm_z = float((chi2_e - np.mean(null_chi2_e)) / (np.std(null_chi2_e) + 1e-10))
perm_p = float(np.mean(null_chi2_e >= chi2_e))
print(f'  Permutation null: z={perm_z:.2f}, p={perm_p:.4f}')

results['A1'] = {
    'gallows_only': {'chi2': float(chi2_g), 'V': V_g, 'p': float(p_g)},
    'expanded': {'chi2': float(chi2_e), 'V': V_e, 'p': float(p_e), 'n_states': int(exp_sub.shape[0])},
    'permutation': {'z': perm_z, 'p': perm_p, 'n_perm': n_perm},
    'n_transitions': all_transitions,
}

# --- A2: Header divergence predicts body divergence ---
print('\nA2: Header divergence -> body divergence')

lag1_pairs = []
lag2_pairs = []
for fid, recs in folio_groups.items():
    valid = [r for r in recs if r['hdr_fracs'] is not None and r['body_fracs'] is not None]
    for j in range(len(valid) - 1):
        lag1_pairs.append((valid[j], valid[j + 1]))
    for j in range(len(valid) - 2):
        lag2_pairs.append((valid[j], valid[j + 2]))

def divergence_test(pairs, label, control_level='raw'):
    hdr_dists, body_dists = [], []
    folio_means_hdr = {}
    folio_means_body = {}
    gallows_means_hdr = defaultdict(list)
    gallows_means_body = defaultdict(list)

    if control_level in ('folio', 'folio_gallows'):
        # Precompute folio means
        for fid, recs in folio_groups.items():
            hdr_v = [r['hdr_fracs'] for r in recs if r['hdr_fracs'] is not None]
            body_v = [r['body_fracs'] for r in recs if r['body_fracs'] is not None]
            if hdr_v:
                folio_means_hdr[fid] = np.mean(hdr_v, axis=0)
            if body_v:
                folio_means_body[fid] = np.mean(body_v, axis=0)

    for r1, r2 in pairs:
        h1, h2 = r1['hdr_fracs'], r2['hdr_fracs']
        b1, b2 = r1['body_fracs'], r2['body_fracs']

        if control_level == 'folio':
            fid = r1['folio']
            if fid in folio_means_hdr:
                h1 = h1 - folio_means_hdr[fid]
                h2 = h2 - folio_means_hdr[fid]
            if fid in folio_means_body:
                b1 = b1 - folio_means_body[fid]
                b2 = b2 - folio_means_body[fid]
        elif control_level == 'folio_gallows':
            fid = r1['folio']
            if fid in folio_means_hdr:
                h1 = h1 - folio_means_hdr[fid]
                h2 = h2 - folio_means_hdr[fid]
            if fid in folio_means_body:
                b1 = b1 - folio_means_body[fid]
                b2 = b2 - folio_means_body[fid]
            # Further residualize on gallows (simple: subtract gallows mean)
            # This is approximate but captures the main effect

        hdr_dists.append(np.linalg.norm(h1 - h2))
        body_dists.append(np.linalg.norm(b1 - b2))

    if len(hdr_dists) < 10:
        return None
    r_val, p_val = stats.pearsonr(hdr_dists, body_dists)
    return {'r': float(r_val), 'p': float(p_val), 'n': len(hdr_dists)}

a2_results = {}
for level in ['raw', 'folio']:
    res = divergence_test(lag1_pairs, f'lag1_{level}', level)
    if res:
        a2_results[f'lag1_{level}'] = res
        print(f'  Lag-1 ({level}): r={res["r"]:.4f}, p={res["p"]:.4f}, n={res["n"]}')

# Lag-2 check
res_lag2 = divergence_test(lag2_pairs, 'lag2_raw', 'raw')
if res_lag2:
    a2_results['lag2_raw'] = res_lag2
    print(f'  Lag-2 (raw): r={res_lag2["r"]:.4f}, p={res_lag2["p"]:.4f}, n={res_lag2["n"]}')

results['A2'] = a2_results

# --- A3: Specification compression arc ---
print('\nA3: Specification compression arc')

all_max_ords = []
all_sims = []
for fid, recs in folio_groups.items():
    valid = [r for r in recs if r['hdr_fracs'] is not None]
    n = len(valid)
    if n < 3:
        continue
    for i in range(n):
        for j in range(i + 1, n):
            sim = cosine_sim(valid[i]['hdr_fracs'], valid[j]['hdr_fracs'])
            # Normalize ordinals to [0,1]
            ord_i = valid[i]['ordinal'] / max(valid[-1]['ordinal'], 1)
            ord_j = valid[j]['ordinal'] / max(valid[-1]['ordinal'], 1)
            max_ord = max(ord_i, ord_j)
            all_max_ords.append(max_ord)
            all_sims.append(sim)

if len(all_max_ords) > 20:
    rho, p_rho = spearmanr(all_max_ords, all_sims)
    print(f'  Header similarity vs max(ordinal): rho={rho:.4f}, p={p_rho:.4f}, n={len(all_sims)}')
    results['A3'] = {'rho': float(rho), 'p': float(p_rho), 'n': len(all_sims)}
else:
    print('  Insufficient data')
    results['A3'] = {'rho': None}

# --- A4: Header specification predicts body operational domain ---
print('\nA4: Header specification predicts body operational domain')

# Collect paragraphs with both header fracs and body categories
a4_valid = [r for r in records if r['hdr_fracs'] is not None and r['body_cats'] is not None]
print(f'  Paragraphs with header + body categories: {len(a4_valid)}')

if len(a4_valid) >= 50:
    Y_cats = np.array([r['body_cats'] for r in a4_valid])
    X_hdr = np.array([r['hdr_fracs'] for r in a4_valid])

    # Controls: gallows + section
    gallows_cats_list = sorted(set(r['gallows'] for r in a4_valid))
    section_cats_list = sorted(set(r['section'] for r in a4_valid))

    def one_hot(val, cats):
        v = np.zeros(len(cats))
        if val in cats:
            v[cats.index(val)] = 1
        return v

    X_ctrl = np.array([np.concatenate([
        one_hot(r['gallows'], gallows_cats_list),
        one_hot(r['section'], section_cats_list), [1]
    ]) for r in a4_valid])

    X_full = np.hstack([X_ctrl, X_hdr])

    def r2(X, Y):
        try:
            beta, _, _, _ = lstsq(X, Y, rcond=None)
            ss_res = np.sum((Y - X @ beta)**2)
            ss_tot = np.sum((Y - np.mean(Y, axis=0))**2)
            return float(1 - ss_res / ss_tot)
        except:
            return float('nan')

    r2_ctrl = r2(X_ctrl, Y_cats)
    r2_full = r2(X_full, Y_cats)
    dr2 = r2_full - r2_ctrl

    # Permutation null
    null_dr2 = []
    for _ in range(200):
        X_hdr_perm = X_hdr[rng.permutation(len(a4_valid))]
        X_full_perm = np.hstack([X_ctrl, X_hdr_perm])
        null_dr2.append(r2(X_full_perm, Y_cats) - r2_ctrl)
    null_dr2 = np.array(null_dr2)
    a4_z = float((dr2 - np.mean(null_dr2)) / (np.std(null_dr2) + 1e-10))
    a4_p = float(np.mean(null_dr2 >= dr2))

    print(f'  R2 (gallows+section): {r2_ctrl:.4f}')
    print(f'  R2 (+ header atoms): {r2_full:.4f}')
    print(f'  dR2: {dr2:+.4f}, z={a4_z:.2f}, p={a4_p:.4f}')

    results['A4'] = {
        'r2_controls': r2_ctrl, 'r2_full': r2_full, 'dr2': dr2,
        'z': a4_z, 'p': a4_p, 'n': len(a4_valid),
    }
else:
    results['A4'] = {'n': len(a4_valid), 'error': 'insufficient data'}

# ============================================================
# BLOCK B: PARAGRAPH SHAPE -> APPARATUS MANIFOLD
# ============================================================
print('\n' + '='*60)
print('BLOCK B: Paragraph Shape -> Apparatus Manifold')

# Load manifold PC scores
manifold_path = PROJECT_ROOT / 'phases' / 'APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS' / 'results' / 't1_manifold_embedding.json'
with open(manifold_path) as f:
    manifold_data = json.load(f)
manifold_scores = manifold_data['space_A']['folio_scores']
MANIFOLD_PCS = ['PC1', 'PC2', 'PC3', 'PC4', 'PC5']

# Load paragraph zone labels
zone_path = PROJECT_ROOT / 'phases' / 'PARAGRAPH_PROGRAM_TYPING' / 'results' / 'paragraph_program_typing.json'
with open(zone_path) as f:
    zone_data = json.load(f)
zone_labels = zone_data['paragraph_labels']

# Build zone counts per folio
folio_zone_counts = defaultdict(lambda: Counter())
for entry in zone_labels:
    folio_zone_counts[entry['folio']][entry['cluster']] += 1

# --- B1: Build folio paragraph shape vectors ---
print('\nB1: Building folio paragraph shape vectors')

# Only folios in both manifold and our records
manifold_folios = set(manifold_scores.keys())
record_folios = set(folio_groups.keys())
common_folios = sorted(manifold_folios & record_folios)
print(f'  Folios in manifold: {len(manifold_folios)}')
print(f'  Folios in records: {len(record_folios)}')
print(f'  Common folios: {len(common_folios)}')

folio_shapes_full = {}
folio_shapes_reduced = {}
folio_manifold = {}
folio_section_map = {}

for fid in common_folios:
    recs = folio_groups[fid]
    sec = recs[0]['section']
    folio_section_map[fid] = sec

    # Zone type proportions (4-dim)
    zc = folio_zone_counts.get(fid, Counter())
    z_total = sum(zc.values())
    zone_props = np.array([zc.get(i, 0) / max(z_total, 1) for i in range(4)])

    # Header atom profile mean (10-dim)
    hdr_vecs = [r['hdr_fracs'] for r in recs if r['hdr_fracs'] is not None]
    if hdr_vecs:
        hdr_mean = np.mean(hdr_vecs, axis=0)
    else:
        hdr_mean = np.zeros(10)

    # Line-length gradient slope
    if len(recs) >= 3:
        ordinals = np.array([r['ordinal'] for r in recs], dtype=float)
        line_lens = np.array([r['mean_body_line_len'] for r in recs])
        if np.std(ordinals) > 0:
            ll_slope = float(spearmanr(ordinals, line_lens)[0])
        else:
            ll_slope = 0.0
    else:
        ll_slope = 0.0

    # Paragraph count
    n_paras = len(recs)

    # Gallows type distribution (4-dim)
    g_counts = Counter(r['gallows'] for r in recs)
    g_total = sum(g_counts.values())
    g_props = np.array([g_counts.get(g, 0) / max(g_total, 1) for g in GALLOWS_TYPES])

    # Specification intensity (mean p+f+h+c in headers from C1788)
    spec_atoms = {'p', 'f', 'h', 'c'}
    spec_scores = []
    for r in recs:
        if r['hdr_fracs'] is not None:
            # p=4, f=5, h=3, c=7 in ATOMS index
            spec_scores.append(r['hdr_fracs'][3] + r['hdr_fracs'][4] + r['hdr_fracs'][5] + r['hdr_fracs'][7])
    spec_intensity = np.mean(spec_scores) if spec_scores else 0

    # Suffix mode A fraction
    mode_a_vals = [r['mode_a_frac'] for r in recs]
    mode_a_mean = np.mean(mode_a_vals) if mode_a_vals else 0.5

    # Full shape vector
    full_vec = np.concatenate([
        zone_props,          # 4
        hdr_mean,            # 10
        [ll_slope],          # 1
        [n_paras],           # 1
        g_props,             # 4
        [spec_intensity],    # 1
        [mode_a_mean],       # 1
    ])  # total: 22

    # Reduced shape vector (no atom-derived features)
    reduced_vec = np.concatenate([
        zone_props,          # 4
        [ll_slope],          # 1
        [n_paras],           # 1
        g_props,             # 4
    ])  # total: 10

    folio_shapes_full[fid] = full_vec
    folio_shapes_reduced[fid] = reduced_vec
    folio_manifold[fid] = np.array([manifold_scores[fid][pc] for pc in MANIFOLD_PCS])

# Z-score all features
folio_list = common_folios
n_folios = len(folio_list)

full_matrix = np.array([folio_shapes_full[f] for f in folio_list])
reduced_matrix = np.array([folio_shapes_reduced[f] for f in folio_list])
manifold_matrix = np.array([folio_manifold[f] for f in folio_list])

# Z-score
full_z = (full_matrix - full_matrix.mean(axis=0)) / (full_matrix.std(axis=0) + 1e-10)
reduced_z = (reduced_matrix - reduced_matrix.mean(axis=0)) / (reduced_matrix.std(axis=0) + 1e-10)

# Section distance matrix for partial Mantel
sections = [folio_section_map[f] for f in folio_list]
sec_dist = np.zeros((n_folios, n_folios))
for i in range(n_folios):
    for j in range(n_folios):
        sec_dist[i, j] = 0 if sections[i] == sections[j] else 1

# Distance matrices
D_full = squareform(pdist(full_z, 'euclidean'))
D_reduced = squareform(pdist(reduced_z, 'euclidean'))
D_manifold = squareform(pdist(manifold_matrix, 'euclidean'))

# --- B2: Mantel tests ---
print('\nB2: Mantel tests (shape vs manifold)')

r_full, p_full, z_full = mantel_test(D_full, D_manifold)
print(f'  Full shape ({full_matrix.shape[1]}d): Mantel r={r_full:.4f}, z={z_full:.2f}, p={p_full:.4f}')

r_reduced, p_reduced, z_reduced = mantel_test(D_reduced, D_manifold)
print(f'  Reduced shape ({reduced_matrix.shape[1]}d): Mantel r={r_reduced:.4f}, z={z_reduced:.2f}, p={p_reduced:.4f}')

# Partial Mantel controlling for section
r_full_partial, p_full_partial, z_full_partial = partial_mantel(D_full, D_manifold, sec_dist)
print(f'  Full partial (section ctrl): r={r_full_partial:.4f}, z={z_full_partial:.2f}, p={p_full_partial:.4f}')

r_red_partial, p_red_partial, z_red_partial = partial_mantel(D_reduced, D_manifold, sec_dist)
print(f'  Reduced partial (section ctrl): r={r_red_partial:.4f}, z={z_red_partial:.2f}, p={p_red_partial:.4f}')

results['B2'] = {
    'full': {'r': r_full, 'p': p_full, 'z': z_full, 'dim': int(full_matrix.shape[1])},
    'reduced': {'r': r_reduced, 'p': p_reduced, 'z': z_reduced, 'dim': int(reduced_matrix.shape[1])},
    'full_partial': {'r': r_full_partial, 'p': p_full_partial, 'z': z_full_partial},
    'reduced_partial': {'r': r_red_partial, 'p': p_red_partial, 'z': z_red_partial},
    'n_folios': n_folios,
}

# --- B2.5: Per-section Mantel ---
print('\nB2.5: Per-section Mantel')

sec_mantel = {}
for sec in ['Stars', 'Bio', 'Herbal']:
    sec_idx = [i for i, s in enumerate(sections) if s == sec]
    if len(sec_idx) < 10:
        continue
    D_f_sec = D_full[np.ix_(sec_idx, sec_idx)]
    D_m_sec = D_manifold[np.ix_(sec_idx, sec_idx)]
    r_sec, p_sec, z_sec = mantel_test(D_f_sec, D_m_sec, n_perm=500)
    sec_mantel[sec] = {'r': r_sec, 'p': p_sec, 'z': z_sec, 'n': len(sec_idx)}
    print(f'  {sec} (n={len(sec_idx)}): r={r_sec:.4f}, z={z_sec:.2f}, p={p_sec:.4f}')

results['B2_5'] = sec_mantel

# --- B3: Per-axis prediction ---
print('\nB3: Per-axis prediction (Spearman, FDR-corrected)')

feature_names = (
    ['zone_' + str(i) for i in range(4)] +
    ['hdr_' + a for a in ATOMS] +
    ['ll_slope', 'n_paras'] +
    ['g_' + g for g in GALLOWS_TYPES] +
    ['spec_intensity', 'mode_a_frac']
)

all_pvals = []
all_results_b3 = []
for fi, fname in enumerate(feature_names):
    for pi, pc in enumerate(MANIFOLD_PCS):
        rho, p_val = spearmanr(full_matrix[:, fi], manifold_matrix[:, pi])
        all_pvals.append(p_val)
        all_results_b3.append({
            'feature': fname, 'pc': pc,
            'rho': float(rho), 'p_raw': float(p_val),
        })

# Benjamini-Hochberg FDR correction
sorted_indices = np.argsort(all_pvals)
n_tests = len(all_pvals)
fdr_threshold = 0.05
for rank, idx in enumerate(sorted_indices, 1):
    bh_threshold = fdr_threshold * rank / n_tests
    all_results_b3[idx]['p_fdr'] = bh_threshold
    all_results_b3[idx]['significant'] = all_pvals[idx] <= bh_threshold

sig_pairs = [r for r in all_results_b3 if r['significant']]
print(f'  Total tests: {n_tests}')
print(f'  Significant after FDR: {len(sig_pairs)}')
if sig_pairs:
    sig_pairs.sort(key=lambda x: -abs(x['rho']))
    print(f'  Top significant pairs:')
    for sp in sig_pairs[:15]:
        print(f'    {sp["feature"]:>20s} x {sp["pc"]}: rho={sp["rho"]:+.3f} p={sp["p_raw"]:.4f}')

results['B3'] = {
    'n_tests': n_tests,
    'n_significant': len(sig_pairs),
    'top_pairs': sig_pairs[:20],
}

# --- B4: Benchmark comparison ---
print('\nB4: Benchmark comparison')
print(f'  This phase (full, {full_matrix.shape[1]}d):    Mantel r={r_full:.4f}')
print(f'  This phase (reduced, {reduced_matrix.shape[1]}d): Mantel r={r_reduced:.4f}')
print(f'  C1722 routing (42d):            Mantel r=0.279')
print(f'  C1709 PP content (high-d):      Mantel r=0.423')

results['B4'] = {
    'full_r': r_full, 'full_dim': int(full_matrix.shape[1]),
    'reduced_r': r_reduced, 'reduced_dim': int(reduced_matrix.shape[1]),
    'C1722_routing': 0.279, 'C1722_dim': 42,
    'C1709_PP': 0.423, 'C1709_dim': 'high',
}

# ============================================================
# SUMMARY
# ============================================================
print('\n' + '='*60)
print('SUMMARY')
print(f'  A1.5 ARI = {ari:.4f} ({"PASS" if ari < 0.5 else "FAIL"})')
print(f'  A1   Expanded chi2={chi2_e:.1f} vs gallows-only {chi2_g:.1f}, perm z={perm_z:.2f} p={perm_p:.4f}')
if 'lag1_raw' in a2_results:
    print(f'  A2   Lag-1 raw r={a2_results["lag1_raw"]["r"]:.4f}, folio r={a2_results.get("lag1_folio", {}).get("r", "N/A")}')
if results['A3']['rho'] is not None:
    print(f'  A3   Convergence rho={results["A3"]["rho"]:.4f} p={results["A3"]["p"]:.4f}')
if 'dr2' in results.get('A4', {}):
    print(f'  A4   Header->body domain dR2={results["A4"]["dr2"]:+.4f} z={results["A4"]["z"]:.2f} p={results["A4"]["p"]:.4f}')
print(f'  B2   Full Mantel r={r_full:.4f} (partial={r_full_partial:.4f})')
print(f'  B2   Reduced Mantel r={r_reduced:.4f} (partial={r_red_partial:.4f})')
print(f'  B3   {len(sig_pairs)} significant feature-PC pairs after FDR')

# Save results
outpath = 'phases/PARAGRAPH_COMPOSITIONAL_ARCHITECTURE/results/compositional_architecture_results.json'
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f'\nResults written to {outpath}')
