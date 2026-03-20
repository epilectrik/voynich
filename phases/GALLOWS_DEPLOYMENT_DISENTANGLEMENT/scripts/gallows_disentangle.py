"""Phase 612: Gallows Deployment Disentanglement

Asks whether gallows contribute unique deployment-posture information
beyond block position, paragraph archetype, and ambient context.

Test blocks:
  T1: Incremental variance partition (full controls)
  T2: Header vs body signal decay (3 zones)
  T3: Within-archetype gallows effects (context-controlled)
  T4: Hierarchical model comparison (4-way / 2-axis / flat)
  T5: Section stability under bootstrap uncertainty

Output: gallows_disentangle_results.json
"""
import sys, json, warnings
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy.stats import chi2_contingency, kruskal
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture

warnings.filterwarnings('ignore')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, BFolioDecoder, Morphology, CategoryClassifier
from phases.STARS_FOLIO_CLOSE_READING.scripts.paragraph_archetypes import (
    extract_paragraph_features, features_to_vector, SECTION_MAP
)

tx = Transcript()
decoder = BFolioDecoder()
morph = Morphology()
cc = CategoryClassifier()

ALL_ATOMS = sorted('kehtpfdscigolamynr')
FOCUS_ATOMS = list('kehtpfocda')  # 10 atoms for variance analysis
GALLOWS_SET = set('ktpf')

# ============================================================
# DATA COLLECTION
# ============================================================
print("Collecting paragraph data...")

folio_sections = {}
for tok in tx.currier_b():
    if tok.folio not in folio_sections:
        folio_sections[tok.folio] = tok.section

folios = sorted(folio_sections.keys())
folio_sec_mapped = {f: SECTION_MAP.get(folio_sections[f], folio_sections[f]) for f in folios}

# Build line-level state series for ambient context computation
folio_lines = {}
for fid in folios:
    paragraphs = decoder.analyze_folio_paragraphs(fid)
    lines_list = []
    for pi, para in enumerate(paragraphs):
        bt = para.boundary_token or ''
        gtype = bt[0] if bt and bt[0] in GALLOWS_SET else 'none'
        for li, line in enumerate(para.lines):
            k_c = h_c = e_c = 0
            cat_counts = Counter()
            n_tok = 0
            for tok in line.tokens:
                if li == 0 and n_tok == 0 and pi > 0:
                    n_tok += 1
                    continue
                n_tok += 1
                if tok.morph and tok.morph.middle:
                    mid = tok.morph.middle
                    for ch in mid:
                        if ch == 'k': k_c += 1
                        elif ch == 'h': h_c += 1
                        elif ch == 'e': e_c += 1
                    cat = cc.classify(mid)
                    if cat: cat_counts[cat] += 1
            total_a = k_c + h_c + e_c + sum(1 for tok in line.tokens
                for ch in (tok.morph.middle or '') if ch not in 'khe' and ch in set('kehtpfdscigolamynr'))
            # Simpler: count all atoms
            total_a = 0
            for tok in line.tokens:
                if tok.morph and tok.morph.middle:
                    total_a += sum(1 for ch in tok.morph.middle if ch in set('kehtpfdscigolamynr'))
            total_c = sum(cat_counts.values())
            lines_list.append({
                'para_idx': pi, 'line_idx': li,
                'is_boundary': (li == 0),
                'gallows': gtype if li == 0 else None,
                'k_frac': k_c / total_a if total_a > 0 else 0,
                'h_frac': h_c / total_a if total_a > 0 else 0,
                'e_frac': e_c / total_a if total_a > 0 else 0,
                'thermal_frac': cat_counts.get('THERMAL', 0) / total_c if total_c > 0 else 0,
                'monitoring_frac': (cat_counts.get('MONITORING', 0) + cat_counts.get('MARKING', 0)) / total_c if total_c > 0 else 0,
                'total_atoms': total_a,
            })
    folio_lines[fid] = lines_list

# Collect rich paragraph records
records = []  # Each: gallows, section, folio, ordinal, block features, archetype, ambient context, zone atoms
para_features_all = []
para_meta_all = []

for fid in folios:
    sec = folio_sec_mapped[fid]
    paragraphs = decoder.analyze_folio_paragraphs(fid)
    fa = decoder.analyze_folio(fid)
    reg = fa.regime if fa and hasattr(fa, 'regime') and fa.regime else 'UNK'

    # Extract archetype features
    pf_list = list(extract_paragraph_features(decoder, fid, sec, reg))

    # Identify block boundaries (gallows-initial paragraphs start new blocks)
    block_idx = 0
    block_ordinal = 0
    n_paras = len(paragraphs)

    for pi, para in enumerate(paragraphs):
        bt = para.boundary_token or ''
        gtype = bt[0] if bt and bt[0] in GALLOWS_SET else 'none'

        # Block tracking
        if gtype in GALLOWS_SET and pi > 0:
            block_idx += 1
            block_ordinal = 0
        elif pi == 0:
            block_ordinal = 0

        is_block_initial = (block_ordinal == 0)
        rel_position = pi / max(n_paras - 1, 1)

        # Ambient context: preceding 3 lines from folio_lines
        lines = folio_lines[fid]
        # Find the line index of this paragraph boundary
        boundary_line_idx = None
        for li_idx, ln in enumerate(lines):
            if ln['para_idx'] == pi and ln['line_idx'] == 0:
                boundary_line_idx = li_idx
                break

        ctx_thermal = ctx_monitoring = ctx_e = ctx_h = 0
        if boundary_line_idx is not None and boundary_line_idx >= 1:
            window = [lines[j] for j in range(max(0, boundary_line_idx - 3), boundary_line_idx)
                       if lines[j]['total_atoms'] >= 3]
            if window:
                ctx_thermal = np.mean([l['thermal_frac'] for l in window])
                ctx_monitoring = np.mean([l['monitoring_frac'] for l in window])
                ctx_e = np.mean([l['e_frac'] for l in window])
                ctx_h = np.mean([l['h_frac'] for l in window])

        if gtype not in GALLOWS_SET:
            block_ordinal += 1
            continue

        # Body atom counts by zone
        z1_atoms = Counter()  # gallows token only
        z2_atoms = Counter()  # rest of first line
        z3_atoms = Counter()  # all non-first lines
        body_atoms = Counter()  # all body (excl gallows token)
        n_body_tokens = 0
        first_tok_done = False

        for line_i, line in enumerate(para.lines):
            for tok_i, tok in enumerate(line.tokens):
                if not first_tok_done:
                    # This is the gallows token - Z1
                    first_tok_done = True
                    if tok.morph and tok.morph.middle:
                        for ch in tok.morph.middle:
                            if ch in set(ALL_ATOMS):
                                z1_atoms[ch] += 1
                    continue

                n_body_tokens += 1
                if tok.morph and tok.morph.middle:
                    for ch in tok.morph.middle:
                        if ch in set(ALL_ATOMS):
                            body_atoms[ch] += 1
                            if line_i == 0:
                                z2_atoms[ch] += 1
                            else:
                                z3_atoms[ch] += 1

        if n_body_tokens < 3:
            block_ordinal += 1
            continue

        body_total = sum(body_atoms.values())
        if body_total == 0:
            block_ordinal += 1
            continue

        # Body atom fractions for the 10 focus atoms
        atom_fracs = {a: body_atoms.get(a, 0) / body_total for a in FOCUS_ATOMS}

        records.append({
            'gallows': gtype, 'section': sec, 'folio': fid,
            'ordinal': pi, 'block_idx': block_idx,
            'block_ordinal': block_ordinal,
            'is_block_initial': is_block_initial,
            'rel_position': rel_position,
            'ctx_thermal': ctx_thermal, 'ctx_monitoring': ctx_monitoring,
            'ctx_e': ctx_e, 'ctx_h': ctx_h,
            'atom_fracs': atom_fracs,
            'body_atoms': dict(body_atoms),
            'body_total': body_total,
            'z1_atoms': dict(z1_atoms), 'z1_total': sum(z1_atoms.values()),
            'z2_atoms': dict(z2_atoms), 'z2_total': sum(z2_atoms.values()),
            'z3_atoms': dict(z3_atoms), 'z3_total': sum(z3_atoms.values()),
            'n_body_tokens': n_body_tokens,
        })

        # Match to archetype features
        if pi < len(pf_list):
            para_features_all.append(features_to_vector(pf_list[pi]))
            para_meta_all.append({'idx': len(records) - 1})

        block_ordinal += 1

n_by_g = Counter(r['gallows'] for r in records)
print(f"  {len(records)} gallows paragraphs: k={n_by_g['k']} t={n_by_g['t']} p={n_by_g['p']} f={n_by_g['f']}")

# Fit GMM archetypes
X_arch = np.array(para_features_all[:len(records)])
if len(X_arch) < len(records):
    # Pad with zeros for any unmatched paragraphs
    X_arch = np.vstack([X_arch, np.zeros((len(records) - len(X_arch), X_arch.shape[1]))])
Xs = StandardScaler().fit_transform(X_arch)
gmm = GaussianMixture(n_components=5, n_init=10, random_state=42, max_iter=300)
gmm.fit(Xs)
archetype_labels = gmm.predict(Xs)
archetype_probs = gmm.predict_proba(Xs)

for i, r in enumerate(records):
    r['archetype'] = int(archetype_labels[i])
    r['archetype_probs'] = archetype_probs[i].tolist()

results = {
    'phase': '612_GALLOWS_DEPLOYMENT_DISENTANGLEMENT',
    'meta': {
        'total_paragraphs': len(records),
        'by_gallows': dict(n_by_g),
        'by_section': dict(Counter(r['section'] for r in records)),
        'archetype_counts': dict(Counter(r['archetype'] for r in records)),
    },
    'tests': {},
}

# ============================================================
# T1: INCREMENTAL VARIANCE PARTITION
# ============================================================
print("\n=== T1: Incremental Variance Partition ===")

# Build feature matrix: n_paragraphs x 10 atoms
Y = np.array([[r['atom_fracs'][a] for a in FOCUS_ATOMS] for r in records])

# Build group IDs
section_ids = np.array([hash(r['section']) % 10000 for r in records])
folio_ids = np.array([hash(r['folio']) % 100000 for r in records])
# Encode sections as integers
sec_list = sorted(set(r['section'] for r in records))
sec_map = {s: i for i, s in enumerate(sec_list)}
section_int = np.array([sec_map[r['section']] for r in records])

# Gallows integer encoding
g_map = {'k': 0, 't': 1, 'p': 2, 'f': 3}
gallows_int = np.array([g_map[r['gallows']] for r in records])
archetype_int = np.array([r['archetype'] for r in records])

# Position features
pos_features = np.array([[r['ordinal'], r['block_ordinal'],
                           float(r['is_block_initial']), r['rel_position']]
                          for r in records])

# Context features
ctx_features = np.array([[r['ctx_thermal'], r['ctx_monitoring'],
                           r['ctx_e'], r['ctx_h']] for r in records])


def sequential_ss_partition(Y, group_list, labels):
    """Compute nested sequential sum-of-squares partition.

    Y: (n, d) feature matrix
    group_list: list of (n,) integer group arrays in nesting order
    labels: names for each level

    Returns dict of {label: variance_share} summing to ~1.0
    """
    n, d = Y.shape
    ss_total = np.sum((Y - Y.mean(0)) ** 2)
    if ss_total == 0:
        return {lab: 0.0 for lab in labels + ['residual']}

    # Build nested means
    prev_means = np.tile(Y.mean(0), (n, 1))  # grand mean
    shares = {}

    for level_idx, (groups, label) in enumerate(zip(group_list, labels)):
        # Compute group means
        unique_groups = np.unique(groups)
        current_means = np.zeros_like(Y)
        for g in unique_groups:
            mask = groups == g
            if mask.sum() > 0:
                current_means[mask] = Y[mask].mean(0)

        ss_level = np.sum((current_means - prev_means) ** 2)
        shares[label] = ss_level / ss_total
        prev_means = current_means.copy()

    # Residual
    ss_resid = np.sum((Y - prev_means) ** 2)
    shares['residual'] = ss_resid / ss_total

    return shares

# For nested groups, we need composite group keys at each level
def make_nested_groups(records, level_keys):
    """Build integer group IDs for nested factors."""
    groups = []
    for keys in level_keys:
        combo_map = {}
        ids = []
        for r in records:
            key = tuple(r[k] if isinstance(r[k], (str, int, float, bool)) else str(r[k]) for k in keys)
            if key not in combo_map:
                combo_map[key] = len(combo_map)
            ids.append(combo_map[key])
        groups.append(np.array(ids))
    return groups

# Create nested groups: section, section+folio, +position_bin, +archetype, +context_bin, +gallows
# Bin position features for group-based analysis
pos_bin = np.array([0 if r['is_block_initial'] else
                     (1 if r['rel_position'] < 0.33 else 2 if r['rel_position'] < 0.67 else 3)
                     for r in records])

# Bin context features (tertiles)
ctx_thermal_arr = np.array([r['ctx_thermal'] for r in records])
ctx_mon_arr = np.array([r['ctx_monitoring'] for r in records])
ctx_t_terts = np.digitize(ctx_thermal_arr, np.percentile(ctx_thermal_arr[ctx_thermal_arr > 0], [33, 67]) if (ctx_thermal_arr > 0).sum() > 2 else [0.1, 0.3])
ctx_m_terts = np.digitize(ctx_mon_arr, np.percentile(ctx_mon_arr[ctx_mon_arr > 0], [33, 67]) if (ctx_mon_arr > 0).sum() > 2 else [0.1, 0.3])

# Augment records with binned features
for i, r in enumerate(records):
    r['pos_bin'] = int(pos_bin[i])
    r['ctx_t_bin'] = int(ctx_t_terts[i])
    r['ctx_m_bin'] = int(ctx_m_terts[i])

# Forward order: section -> folio -> position -> archetype -> context -> gallows
level_keys_fwd = [
    ['section'],
    ['section', 'folio'],
    ['section', 'folio', 'pos_bin'],
    ['section', 'folio', 'pos_bin', 'archetype'],
    ['section', 'folio', 'pos_bin', 'archetype', 'ctx_t_bin', 'ctx_m_bin'],
    ['section', 'folio', 'pos_bin', 'archetype', 'ctx_t_bin', 'ctx_m_bin', 'gallows'],
]
level_names_fwd = ['section', 'folio|section', 'position|folio',
                    'archetype|position', 'context|archetype', 'gallows|context']

groups_fwd = make_nested_groups(records, level_keys_fwd)
shares_fwd = sequential_ss_partition(Y, groups_fwd, level_names_fwd)

print("  Forward order (gallows LAST):")
for k, v in shares_fwd.items():
    marker = ' <<<' if k == 'gallows|context' else ''
    print(f"    {k:25s}: {v:.4f} ({v*100:.1f}%){marker}")

# Reverse order: gallows first
level_keys_rev = [
    ['gallows'],
    ['gallows', 'section'],
    ['gallows', 'section', 'folio'],
    ['gallows', 'section', 'folio', 'pos_bin'],
    ['gallows', 'section', 'folio', 'pos_bin', 'archetype'],
    ['gallows', 'section', 'folio', 'pos_bin', 'archetype', 'ctx_t_bin', 'ctx_m_bin'],
]
level_names_rev = ['gallows', 'section|gallows', 'folio|section',
                    'position|folio', 'archetype|position', 'context|archetype']

groups_rev = make_nested_groups(records, level_keys_rev)
shares_rev = sequential_ss_partition(Y, groups_rev, level_names_rev)

print("  Reverse order (gallows FIRST):")
for k, v in shares_rev.items():
    marker = ' <<<' if k == 'gallows' else ''
    print(f"    {k:25s}: {v:.4f} ({v*100:.1f}%){marker}")

# Permutation null: shuffle gallows within section, 200 times
print("  Running 200 permutation null (shuffle gallows within section)...")
null_gallows_shares = []
rng = np.random.RandomState(42)
for perm in range(200):
    shuffled = records.copy()
    shuffled = [dict(r) for r in records]  # deep copy
    for sec in sec_list:
        sec_idx = [i for i, r in enumerate(shuffled) if r['section'] == sec]
        sec_gallows = [shuffled[i]['gallows'] for i in sec_idx]
        rng.shuffle(sec_gallows)
        for i, idx in enumerate(sec_idx):
            shuffled[idx]['gallows'] = sec_gallows[i]

    groups_null = make_nested_groups(shuffled, level_keys_fwd)
    shares_null = sequential_ss_partition(Y, groups_null, level_names_fwd)
    null_gallows_shares.append(shares_null.get('gallows|context', 0))

null_mean = np.mean(null_gallows_shares)
null_std = np.std(null_gallows_shares) if np.std(null_gallows_shares) > 0 else 1e-10
observed = shares_fwd.get('gallows|context', 0)
z_score = (observed - null_mean) / null_std
p_perm = np.mean(np.array(null_gallows_shares) >= observed)

print(f"  Gallows|context: observed={observed:.4f}  null_mean={null_mean:.4f}  z={z_score:.2f}  p_perm={p_perm:.4f}")

# Mediation: context-only vs context+gallows
# Use OLS R-squared as simple variance metric
from numpy.linalg import lstsq

def multivariate_r2(X_pred, Y_resp):
    """R-squared of multivariate linear regression X -> Y."""
    n = X_pred.shape[0]
    X1 = np.column_stack([np.ones(n), X_pred])
    ss_total = np.sum((Y_resp - Y_resp.mean(0)) ** 2)
    if ss_total == 0:
        return 0
    betas, _, _, _ = lstsq(X1, Y_resp, rcond=None)
    Y_hat = X1 @ betas
    ss_resid = np.sum((Y_resp - Y_hat) ** 2)
    return 1 - ss_resid / ss_total

# Model A: context only -> body
X_ctx = ctx_features
r2_ctx_only = multivariate_r2(X_ctx, Y)

# Model B: context + gallows dummies -> body
G_dummies = np.zeros((len(records), 3))  # k=ref, t/p/f dummies
for i, r in enumerate(records):
    if r['gallows'] == 't': G_dummies[i, 0] = 1
    elif r['gallows'] == 'p': G_dummies[i, 1] = 1
    elif r['gallows'] == 'f': G_dummies[i, 2] = 1

X_ctx_g = np.column_stack([X_ctx, G_dummies])
r2_ctx_gallows = multivariate_r2(X_ctx_g, Y)

delta_r2 = r2_ctx_gallows - r2_ctx_only
print(f"  Mediation: R2_context={r2_ctx_only:.4f}  R2_context+gallows={r2_ctx_gallows:.4f}  delta={delta_r2:.4f}")

results['tests']['T1_variance_partition'] = {
    'forward_order': {k: round(v, 6) for k, v in shares_fwd.items()},
    'reverse_order': {k: round(v, 6) for k, v in shares_rev.items()},
    'gallows_net_vs': round(observed, 6),
    'gallows_gross_vs': round(shares_rev.get('gallows', 0), 6),
    'permutation_null': {
        'n_perms': 200,
        'null_mean': round(null_mean, 6),
        'null_std': round(null_std, 6),
        'z_score': round(z_score, 3),
        'p_perm': round(p_perm, 4),
    },
    'mediation': {
        'r2_context_only': round(r2_ctx_only, 5),
        'r2_context_plus_gallows': round(r2_ctx_gallows, 5),
        'delta_r2': round(delta_r2, 5),
    },
}

# ============================================================
# T2: HEADER VS BODY SIGNAL DECAY
# ============================================================
print("\n=== T2: Header vs Body Signal Decay ===")

def zone_cramers_v(records, zone_key, zone_total_key):
    """Compute Cramer's V for gallows x atom association in a zone."""
    # Build contingency: 4 gallows x len(ALL_ATOMS)
    atom_list = sorted(set(ALL_ATOMS))
    ct = np.zeros((4, len(atom_list)), dtype=int)
    for r in records:
        gi = g_map[r['gallows']]
        for ai, a in enumerate(atom_list):
            ct[gi, ai] += r[zone_key].get(a, 0)

    # Remove zero columns
    col_mask = ct.sum(0) > 0
    ct_clean = ct[:, col_mask]
    row_mask = ct_clean.sum(1) > 0
    ct_clean = ct_clean[row_mask]

    if ct_clean.shape[0] < 2 or ct_clean.shape[1] < 2 or ct_clean.sum() < 20:
        return 0, 1, 0

    chi2, p, dof, exp = chi2_contingency(ct_clean)
    v = np.sqrt(chi2 / (ct_clean.sum() * (min(ct_clean.shape) - 1)))
    return round(v, 4), round(p, 8), int(ct_clean.sum())

# Only include paragraphs with enough data in each zone
v_z1, p_z1, n_z1 = zone_cramers_v(records, 'z1_atoms', 'z1_total')
v_z2, p_z2, n_z2 = zone_cramers_v([r for r in records if r['z2_total'] >= 5], 'z2_atoms', 'z2_total')
v_z3, p_z3, n_z3 = zone_cramers_v([r for r in records if r['z3_total'] >= 10], 'z3_atoms', 'z3_total')

print(f"  Z1 (gallows token):    V={v_z1:.4f}  p={p_z1:.6f}  n_atoms={n_z1}")
print(f"  Z2 (first-line resid): V={v_z2:.4f}  p={p_z2:.6f}  n_atoms={n_z2}")
print(f"  Z3 (body lines 2+):   V={v_z3:.4f}  p={p_z3:.6f}  n_atoms={n_z3}")

if v_z1 > 0 and v_z3 > 0:
    attenuation_ratio = v_z3 / v_z1
    print(f"  Attenuation ratio V_Z3/V_Z1 = {attenuation_ratio:.3f}")
else:
    attenuation_ratio = None

results['tests']['T2_header_body_decay'] = {
    'Z1_gallows_token': {'V': v_z1, 'p': p_z1, 'n_atoms': n_z1},
    'Z2_first_line_residual': {'V': v_z2, 'p': p_z2, 'n_atoms': n_z2,
                                'caveat': 'confounded with generic first-line specification effects (C1426/C1729)'},
    'Z3_body_lines_2plus': {'V': v_z3, 'p': p_z3, 'n_atoms': n_z3},
    'attenuation_ratio_Z3_Z1': round(attenuation_ratio, 4) if attenuation_ratio else None,
}

# ============================================================
# T3: WITHIN-ARCHETYPE GALLOWS EFFECTS
# ============================================================
print("\n=== T3: Within-Archetype Gallows Effects ===")

t3_results = {}
for arch in range(5):
    arch_recs = [r for r in records if r['archetype'] == arch]
    n_arch = len(arch_recs)
    n_by_g_arch = Counter(r['gallows'] for r in arch_recs)

    if n_arch < 20 or sum(1 for v in n_by_g_arch.values() if v >= 3) < 2:
        t3_results[f'A{arch}'] = {'status': 'insufficient_data', 'n': n_arch,
                                    'gallows_dist': dict(n_by_g_arch)}
        print(f"  A{arch} (n={n_arch}): insufficient data")
        continue

    # p self-enrichment within this archetype
    p_self = p_other = p_total_self = p_total_other = 0
    for r in arch_recs:
        if r['gallows'] == 'p':
            p_self += r['body_atoms'].get('p', 0)
            p_total_self += r['body_total']
        else:
            p_other += r['body_atoms'].get('p', 0)
            p_total_other += r['body_total']

    p_oe = (p_self / p_total_self) / (p_other / p_total_other) if p_total_self > 0 and p_total_other > 0 and p_other > 0 else 0

    # k e-bias within this archetype
    k_e_self = k_e_other = k_total_self = k_total_other = 0
    for r in arch_recs:
        if r['gallows'] == 'k':
            k_e_self += r['body_atoms'].get('e', 0)
            k_total_self += r['body_total']
        else:
            k_e_other += r['body_atoms'].get('e', 0)
            k_total_other += r['body_total']

    k_e_oe = (k_e_self / k_total_self) / (k_e_other / k_total_other) if k_total_self > 0 and k_total_other > 0 and k_e_other > 0 else 0

    # Full contingency within archetype
    ct = np.zeros((4, len(FOCUS_ATOMS)), dtype=int)
    for r in arch_recs:
        gi = g_map[r['gallows']]
        for ai, a in enumerate(FOCUS_ATOMS):
            ct[gi, ai] += r['body_atoms'].get(a, 0)
    row_mask = ct.sum(1) > 0
    col_mask = ct.sum(0) > 0
    ct_clean = ct[row_mask][:, col_mask]
    if ct_clean.shape[0] >= 2 and ct_clean.shape[1] >= 2 and ct_clean.sum() > 50:
        chi2, p_chi, dof, _ = chi2_contingency(ct_clean)
        v_arch = np.sqrt(chi2 / (ct_clean.sum() * (min(ct_clean.shape) - 1)))
    else:
        chi2, p_chi, v_arch = 0, 1, 0

    # Context-controlled: split by thermal median
    thermal_vals = [r['ctx_thermal'] for r in arch_recs]
    thermal_med = np.median(thermal_vals)
    hi_recs = [r for r in arch_recs if r['ctx_thermal'] >= thermal_med]
    lo_recs = [r for r in arch_recs if r['ctx_thermal'] < thermal_med]

    def p_oe_in_subset(subset):
        ps = po = pts = pto = 0
        for r in subset:
            if r['gallows'] == 'p':
                ps += r['body_atoms'].get('p', 0); pts += r['body_total']
            else:
                po += r['body_atoms'].get('p', 0); pto += r['body_total']
        return (ps / pts) / (po / pto) if pts > 0 and pto > 0 and po > 0 else 0

    p_oe_hi = p_oe_in_subset(hi_recs)
    p_oe_lo = p_oe_in_subset(lo_recs)

    t3_results[f'A{arch}'] = {
        'n': n_arch, 'gallows_dist': dict(n_by_g_arch),
        'p_self_oe': round(p_oe, 4),
        'k_e_oe': round(k_e_oe, 4),
        'full_chi2': round(chi2, 2), 'full_p': round(p_chi, 6),
        'full_V': round(v_arch, 4),
        'context_controlled': {
            'p_oe_hi_thermal': round(p_oe_hi, 4),
            'p_oe_lo_thermal': round(p_oe_lo, 4),
            'n_hi': len(hi_recs), 'n_lo': len(lo_recs),
            'survives': p_oe_hi > 1.05 and p_oe_lo > 1.05,
        },
    }
    sig = '***' if p_chi < 0.001 else '**' if p_chi < 0.01 else '*' if p_chi < 0.05 else ''
    print(f"  A{arch} (n={n_arch}): V={v_arch:.4f} p={p_chi:.4f}{sig}  p_OE={p_oe:.3f}  k_e_OE={k_e_oe:.3f}  ctx_ctrl={p_oe_hi:.2f}/{p_oe_lo:.2f}")

results['tests']['T3_within_archetype'] = t3_results

# ============================================================
# T4: HIERARCHICAL MODEL COMPARISON
# ============================================================
print("\n=== T4: Hierarchical Model Comparison ===")

# Model 1: 4-way flat (k/t/p/f)
# Already have full contingency from Phase 611
ct_4way = np.zeros((4, len(FOCUS_ATOMS)), dtype=int)
for r in records:
    gi = g_map[r['gallows']]
    for ai, a in enumerate(FOCUS_ATOMS):
        ct_4way[gi, ai] += r['body_atoms'].get(a, 0)
chi2_m1, p_m1, dof_m1, _ = chi2_contingency(ct_4way)
v_m1 = np.sqrt(chi2_m1 / (ct_4way.sum() * (min(ct_4way.shape) - 1)))

# Model 3: flat opener/mode (k/f vs p/t)
opener_map = {'k': 'opener', 'f': 'opener', 'p': 'mode', 't': 'mode'}
ct_2way = np.zeros((2, len(FOCUS_ATOMS)), dtype=int)
for r in records:
    gi = 0 if opener_map[r['gallows']] == 'opener' else 1
    for ai, a in enumerate(FOCUS_ATOMS):
        ct_2way[gi, ai] += r['body_atoms'].get(a, 0)
chi2_m3, p_m3, dof_m3, _ = chi2_contingency(ct_2way)
v_m3 = np.sqrt(chi2_m3 / (ct_2way.sum() * (min(ct_2way.shape) - 1)))

# Model 2: within-family splits
# Within openers: k vs f
opener_recs = [r for r in records if r['gallows'] in ('k', 'f')]
ct_kf = np.zeros((2, len(FOCUS_ATOMS)), dtype=int)
for r in opener_recs:
    gi = 0 if r['gallows'] == 'k' else 1
    for ai, a in enumerate(FOCUS_ATOMS):
        ct_kf[gi, ai] += r['body_atoms'].get(a, 0)
col_mask = ct_kf.sum(0) > 0
ct_kf_clean = ct_kf[:, col_mask]
if ct_kf_clean.shape[0] >= 2 and ct_kf_clean.shape[1] >= 2:
    chi2_kf, p_kf, dof_kf, _ = chi2_contingency(ct_kf_clean)
    v_kf = np.sqrt(chi2_kf / (ct_kf_clean.sum() * (min(ct_kf_clean.shape) - 1)))
else:
    chi2_kf, p_kf, v_kf = 0, 1, 0

# Within modes: p vs t
mode_recs = [r for r in records if r['gallows'] in ('p', 't')]
ct_pt = np.zeros((2, len(FOCUS_ATOMS)), dtype=int)
for r in mode_recs:
    gi = 0 if r['gallows'] == 'p' else 1
    for ai, a in enumerate(FOCUS_ATOMS):
        ct_pt[gi, ai] += r['body_atoms'].get(a, 0)
chi2_pt, p_pt, dof_pt, _ = chi2_contingency(ct_pt)
v_pt = np.sqrt(chi2_pt / (ct_pt.sum() * (min(ct_pt.shape) - 1)))

# R2 comparison: how much body variance does each model explain?
r2_m1 = multivariate_r2(G_dummies, Y)  # 3 dummies for 4-way

# 2-axis model: opener dummy + within-opener dummy + within-mode dummy
opener_dummy = np.array([1 if r['gallows'] in ('k', 'f') else 0 for r in records]).reshape(-1, 1)
within_opener = np.array([1 if r['gallows'] == 'f' else 0 for r in records]).reshape(-1, 1)
within_mode = np.array([1 if r['gallows'] == 't' else 0 for r in records]).reshape(-1, 1)
X_m2 = np.column_stack([opener_dummy, within_opener, within_mode])
r2_m2 = multivariate_r2(X_m2, Y)

# Flat opener/mode
r2_m3 = multivariate_r2(opener_dummy, Y)

# Positional opener/mode test
opener_positions = [r['rel_position'] for r in records if r['gallows'] in ('k', 'f')]
mode_positions = [r['rel_position'] for r in records if r['gallows'] in ('p', 't')]
if opener_positions and mode_positions:
    from scipy.stats import mannwhitneyu
    u_stat, p_pos = mannwhitneyu(opener_positions, mode_positions, alternative='two-sided')
    pos_opener_mean = np.mean(opener_positions)
    pos_mode_mean = np.mean(mode_positions)
else:
    u_stat, p_pos, pos_opener_mean, pos_mode_mean = 0, 1, 0, 0

print(f"  Model 1 (4-way flat):     V={v_m1:.4f}  R2={r2_m1:.5f}  dof={dof_m1}")
print(f"  Model 2 (2-axis factor):  R2={r2_m2:.5f}")
print(f"  Model 3 (opener/mode):    V={v_m3:.4f}  R2={r2_m3:.5f}  dof={dof_m3}")
print(f"  Within k vs f:            V={v_kf:.4f}  p={p_kf:.4f}  (n={len(opener_recs)})")
print(f"  Within p vs t:            V={v_pt:.4f}  p={p_pt:.4f}  (n={len(mode_recs)})")
print(f"  Position: opener={pos_opener_mean:.3f} mode={pos_mode_mean:.3f} p={p_pos:.4f}")

results['tests']['T4_hierarchical_model'] = {
    'model_1_4way': {'V': round(v_m1, 4), 'R2': round(r2_m1, 5), 'chi2': round(chi2_m1, 2), 'p': round(p_m1, 8), 'dof': int(dof_m1)},
    'model_2_2axis': {'R2': round(r2_m2, 5)},
    'model_3_opener_mode': {'V': round(v_m3, 4), 'R2': round(r2_m3, 5), 'chi2': round(chi2_m3, 2), 'p': round(p_m3, 8), 'dof': int(dof_m3)},
    'within_k_vs_f': {'V': round(v_kf, 4), 'p': round(p_kf, 4), 'n': len(opener_recs),
                       'caveat': 'k=35, f=20: low power'},
    'within_p_vs_t': {'V': round(v_pt, 4), 'p': round(p_pt, 8), 'n': len(mode_recs)},
    'positional_split': {
        'opener_mean_position': round(pos_opener_mean, 4),
        'mode_mean_position': round(pos_mode_mean, 4),
        'mann_whitney_p': round(p_pos, 4),
    },
    'r2_comparison': {
        'M1_4way': round(r2_m1, 5),
        'M2_2axis': round(r2_m2, 5),
        'M3_flat': round(r2_m3, 5),
        'M3_captures_pct_of_M1': round(r2_m3 / r2_m1 * 100, 1) if r2_m1 > 0 else 0,
    },
}

# ============================================================
# T5: SECTION STABILITY UNDER BOOTSTRAP
# ============================================================
print("\n=== T5: Section Stability Under Bootstrap ===")

def compute_oe_vector(subset_records, reference_records):
    """Compute O/E vector for a subset relative to reference."""
    obs = Counter()
    obs_total = 0
    ref = Counter()
    ref_total = 0
    for r in subset_records:
        for a in FOCUS_ATOMS:
            obs[a] += r['body_atoms'].get(a, 0)
        obs_total += r['body_total']
    for r in reference_records:
        for a in FOCUS_ATOMS:
            ref[a] += r['body_atoms'].get(a, 0)
        ref_total += r['body_total']
    oe = []
    for a in FOCUS_ATOMS:
        obs_frac = obs[a] / obs_total if obs_total > 0 else 0
        ref_frac = ref[a] / ref_total if ref_total > 0 else 0
        oe.append(obs_frac / ref_frac if ref_frac > 0 else 1.0)
    return np.array(oe)

def cosine_sim(a, b):
    """Cosine similarity of two vectors."""
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return np.dot(a, b) / denom if denom > 0 else 0

# Global O/E for p-gallows vs others (the baseline pattern)
p_recs = [r for r in records if r['gallows'] == 'p']
not_p_recs = [r for r in records if r['gallows'] != 'p']
global_p_oe = compute_oe_vector(p_recs, not_p_recs)

# Per-section O/E vectors
section_oes = {}
sections_test = [s for s in sec_list if sum(1 for r in records if r['section'] == s) >= 30]

for sec in sections_test:
    sec_p = [r for r in records if r['section'] == sec and r['gallows'] == 'p']
    sec_not_p = [r for r in records if r['section'] == sec and r['gallows'] != 'p']
    if len(sec_p) >= 5 and len(sec_not_p) >= 10:
        section_oes[sec] = compute_oe_vector(sec_p, sec_not_p)

# Bootstrap stability
print("  Bootstrapping section O/E vectors (200 resamples)...")
bootstrap_cosines = {sec: [] for sec in section_oes}
rng = np.random.RandomState(123)

for _ in range(200):
    for sec in section_oes:
        sec_all = [r for r in records if r['section'] == sec]
        boot_idx = rng.choice(len(sec_all), size=len(sec_all), replace=True)
        boot_recs = [sec_all[i] for i in boot_idx]
        boot_p = [r for r in boot_recs if r['gallows'] == 'p']
        boot_not_p = [r for r in boot_recs if r['gallows'] != 'p']
        if len(boot_p) >= 3 and len(boot_not_p) >= 5:
            boot_oe = compute_oe_vector(boot_p, boot_not_p)
            cos = cosine_sim(boot_oe - 1, global_p_oe - 1)  # direction relative to null (1.0)
            bootstrap_cosines[sec].append(cos)

t5_results = {}
for sec in section_oes:
    cos_global = cosine_sim(section_oes[sec] - 1, global_p_oe - 1)
    boot_cos = bootstrap_cosines.get(sec, [])
    ci_lo = np.percentile(boot_cos, 5) if boot_cos else 0
    ci_hi = np.percentile(boot_cos, 95) if boot_cos else 0
    boot_mean = np.mean(boot_cos) if boot_cos else 0

    n_sec = sum(1 for r in records if r['section'] == sec)
    n_p_sec = sum(1 for r in records if r['section'] == sec and r['gallows'] == 'p')

    t5_results[sec] = {
        'n_total': n_sec, 'n_p': n_p_sec,
        'cosine_to_global': round(cos_global, 4),
        'bootstrap_mean_cosine': round(boot_mean, 4),
        'bootstrap_ci_90': [round(ci_lo, 4), round(ci_hi, 4)],
        'oe_vector': {a: round(v, 4) for a, v in zip(FOCUS_ATOMS, section_oes[sec])},
    }
    print(f"  {sec:8s} (n={n_sec}, p={n_p_sec}): cos={cos_global:.3f}  boot_mean={boot_mean:.3f}  CI=[{ci_lo:.3f}, {ci_hi:.3f}]")

# Section-to-section correlation matrix
sec_keys = sorted(section_oes.keys())
if len(sec_keys) >= 2:
    sec_corr = {}
    for i in range(len(sec_keys)):
        for j in range(i+1, len(sec_keys)):
            s1, s2 = sec_keys[i], sec_keys[j]
            cos = cosine_sim(section_oes[s1] - 1, section_oes[s2] - 1)
            sec_corr[f'{s1}_vs_{s2}'] = round(cos, 4)
    print(f"  Section-to-section cosines: {sec_corr}")
else:
    sec_corr = {}

t5_results['section_cross_cosines'] = sec_corr
t5_results['global_p_oe_vector'] = {a: round(v, 4) for a, v in zip(FOCUS_ATOMS, global_p_oe)}

results['tests']['T5_section_stability'] = t5_results

# ============================================================
# CONSTRAINT EVIDENCE SUMMARY
# ============================================================
print("\n=== Constraint Evidence Summary ===")

results['constraint_evidence'] = {
    'C1778_incremental_variance': {
        'gallows_net_vs': round(observed, 6),
        'z_score': round(z_score, 3),
        'p_perm': round(p_perm, 4),
        'mediation_delta_r2': round(delta_r2, 5),
        'verdict': 'SIGNIFICANT' if z_score > 2.0 else 'MARGINAL' if z_score > 1.5 else 'NULL',
    },
    'C1779_header_body_signal': {
        'V_header_token': v_z1,
        'V_body_lines2plus': v_z3,
        'attenuation_ratio': round(attenuation_ratio, 4) if attenuation_ratio else None,
        'verdict': 'ATTENUATION' if attenuation_ratio and attenuation_ratio < 0.5 else
                   'PERSISTENCE' if attenuation_ratio and attenuation_ratio > 0.7 else 'MODERATE',
    },
    'C1780_archetype_orthogonality': {
        'archetypes_tested': [k for k, v in t3_results.items() if isinstance(v, dict) and 'full_V' in v],
        'significant_within': [k for k, v in t3_results.items() if isinstance(v, dict) and v.get('full_p', 1) < 0.05],
        'context_controlled_survives': [k for k, v in t3_results.items()
                                         if isinstance(v, dict) and v.get('context_controlled', {}).get('survives', False)],
    },
    'C1781_opener_mode': {
        'M3_flat_R2': round(r2_m3, 5),
        'M1_4way_R2': round(r2_m1, 5),
        'M3_captures_pct': round(r2_m3 / r2_m1 * 100, 1) if r2_m1 > 0 else 0,
        'within_k_f_V': round(v_kf, 4),
        'within_p_t_V': round(v_pt, 4),
        'positional_p': round(p_pos, 4),
    },
    'C1782_posture_stability': {
        'sections_tested': list(section_oes.keys()),
        'mean_cosine_to_global': round(np.mean([v['cosine_to_global'] for v in t5_results.values()
                                                 if isinstance(v, dict) and 'cosine_to_global' in v]), 4) if section_oes else 0,
        'cross_section_cosines': sec_corr,
    },
}

# Print verdicts
for cid, ev in results['constraint_evidence'].items():
    v = ev.get('verdict', '')
    print(f"  {cid}: {v}" if v else f"  {cid}: see details")

# ============================================================
# WRITE JSON
# ============================================================
outpath = ROOT / 'phases' / 'GALLOWS_DEPLOYMENT_DISENTANGLEMENT' / 'results' / 'gallows_disentangle_results.json'
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults written to {outpath}")
print("Done.")
