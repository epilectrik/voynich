"""Phase 560b T3b: Within-Section Folio Discriminability

Tests 6 feature sets for within-section folio discrimination:
HEAD, MARGINAL (560's 32), DEPLOYMENT (560b's 56), FULL_560, FULL_560b, COMBINED.

D3b: within-section pairwise distance (primary)
D4b: Ward linkage clustering ARI
D5b: gain test (LOO-NN + RF)
D7:  within-section variance decomposition

Input: t1_domain_decomposition.json, t1b_deployment_features.json
Output: t3b_discriminability.json
"""
import json
import math
import sys
import time
import random
from pathlib import Path
from collections import Counter, defaultdict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DOMAINS = ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']
N_NULL_SEEDS = 200
SEED_BASE = 42

# Phase 560 marginal feature names (32)
MARGINAL_NAMES = [
    'k_suffix_entropy', 'k_bare_term_frac', 'k_thermal_purity',
    't_mod_rate', 't_flow_purity',
    'a_i_rate', 'a_ii_rate', 'a_n_term_rate', 'a_hazard_rate',
    'e_ey_frac', 'e_d_mod_rate', 'e_ey_vocab', 'e_ey_zone_bias', 'e_edy_dominance',
    'o_l_frac', 'o_r_frac', 'o_exec_mod_rate',
    'hl_pseudo_entropy', 'hl_mod_rate', 'hl_core_ratio', 'hl_suffix_bifurc',
    'xd_r_to_a', 'xd_ey_of_total', 'xd_headless_frac',
    'zone_k_spec_bias', 'zone_a_close_rate', 'zone_ey_early_bias', 'zone_hl_close_surge',
    'adj_y_to_k_rate', 'adj_r_to_a_rate', 'adj_highhaz_to_safe_rate', 'adj_active_close_rate',
]

HEAD_NAMES = ['k_frac', 't_frac', 'a_frac', 'e_frac', 'o_frac', 'hl_frac']


def load_t1():
    path = RESULTS_DIR / 't1_domain_decomposition.json'
    with open(path) as f:
        return json.load(f)


def load_t1b():
    path = RESULTS_DIR / 't1b_deployment_features.json'
    with open(path) as f:
        return json.load(f)


def nan_euclidean(v1, v2):
    s = 0.0
    n = 0
    for a, b in zip(v1, v2):
        if a is not None and b is not None:
            s += (a - b) ** 2
            n += 1
    if n == 0:
        return float('inf')
    return math.sqrt(s)


def z_score(vectors, names, folio_list):
    """Z-score features across folios. vectors = {folio: [values]}."""
    n_feat = len(names)
    means = []
    stds = []
    for fi in range(n_feat):
        vals = [vectors[f][fi] for f in folio_list if vectors[f][fi] is not None]
        if len(vals) < 2:
            means.append(None)
            stds.append(None)
        else:
            m = sum(vals) / len(vals)
            v = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
            means.append(m)
            stds.append(math.sqrt(v) if v > 0 else 1e-10)

    z = {}
    for f in folio_list:
        z[f] = []
        for fi in range(n_feat):
            raw = vectors[f][fi]
            if raw is not None and means[fi] is not None:
                z[f].append((raw - means[fi]) / stds[fi])
            else:
                z[f].append(None)
    return z, means, stds


def leave_one_out_nn(z_vectors, folio_list, labels):
    correct = 0
    for i, f in enumerate(folio_list):
        best_dist = float('inf')
        best_label = None
        for j, g in enumerate(folio_list):
            if i == j:
                continue
            d = nan_euclidean(z_vectors[f], z_vectors[g])
            if d < best_dist:
                best_dist = d
                best_label = labels[j]
        if best_label == labels[i]:
            correct += 1
    return correct / len(folio_list) if folio_list else 0


def within_section_nn(z_vectors, folio_list, sections):
    """LOO-NN within each section: can we distinguish folios from their same-section peers?"""
    # Group by section
    sec_groups = defaultdict(list)
    for i, f in enumerate(folio_list):
        sec_groups[sections[i]].append((i, f))

    total = 0
    correct = 0
    for sec, items in sec_groups.items():
        if len(items) < 3:
            continue
        fols = [f for _, f in items]
        for i, fi in enumerate(fols):
            best_dist = float('inf')
            best_fol = None
            for j, fj in enumerate(fols):
                if i == j:
                    continue
                d = nan_euclidean(z_vectors[fi], z_vectors[fj])
                if d < best_dist:
                    best_dist = d
                    best_fol = fj
            # "Correct" = nearest neighbor is NOT the same folio (trivially true)
            # Actually for within-section, there's no label to classify against.
            # Instead: measure how distinguishable folios are via mean pairwise distance
            total += 1
    # Return mean pairwise distance within section (normalized)
    return None  # Placeholder - actual metric computed in D3b


def safe_entropy(counter):
    total = sum(counter.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counter.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def safe_frac(tokens, fn):
    if not tokens:
        return None
    return sum(1 for t in tokens if fn(t)) / len(tokens)


# ===================================================================
# Recompute Phase 560's 32 marginal features from tokens
# (needed for null model recomputation)
# ===================================================================
def compute_marginal_features(tokens, corpus_stats):
    """Phase 560's 32 features, minimal reimplementation."""
    f = {}
    n_total = len(tokens)
    if n_total == 0:
        return {k: None for k in MARGINAL_NAMES}

    by_domain = defaultdict(list)
    for t in tokens:
        by_domain[t['domain']].append(t)

    k_tok = by_domain['THERMAL']
    t_tok = by_domain['FLOW']
    a_tok = by_domain['ACTIVE']
    e_tok = by_domain['STABILITY']
    o_tok = by_domain['ARRANGEMENT']
    hl_tok = by_domain['HEADLESS']

    # THERMAL
    if len(k_tok) >= 5:
        sfx_chars = Counter()
        for t in k_tok:
            if t['suffix']:
                for ch in t['suffix']:
                    sfx_chars[ch] += 1
        f['k_suffix_entropy'] = safe_entropy(sfx_chars)
        f['k_bare_term_frac'] = safe_frac(k_tok, lambda t: t['term'] == 'bare')
        f['k_thermal_purity'] = safe_frac(k_tok, lambda t: t['operational_category'] == 'THERMAL')
    else:
        f['k_suffix_entropy'] = f['k_bare_term_frac'] = f['k_thermal_purity'] = None

    # FLOW
    if len(t_tok) >= 3:
        f['t_mod_rate'] = safe_frac(t_tok, lambda t: len(t['mods']) > 0)
        f['t_flow_purity'] = safe_frac(t_tok, lambda t: t['operational_category'] == 'FLOW')
    else:
        f['t_mod_rate'] = f['t_flow_purity'] = None

    # ACTIVE
    if len(a_tok) >= 5:
        f['a_i_rate'] = safe_frac(a_tok, lambda t: t['has_i_mod'])
        f['a_ii_rate'] = safe_frac(a_tok, lambda t: t['i_count'] >= 2)
        f['a_n_term_rate'] = safe_frac(a_tok, lambda t: t['term'] == 'n')
        f['a_hazard_rate'] = safe_frac(a_tok, lambda t: t['frame_hazard'] == 'HIGH')
    else:
        f['a_i_rate'] = f['a_ii_rate'] = f['a_n_term_rate'] = f['a_hazard_rate'] = None

    # STABILITY
    if len(e_tok) >= 10:
        ey = [t for t in e_tok if t['frame'] == 'e->y']
        non_ey = [t for t in e_tok if t['frame'] != 'e->y']
        f['e_ey_frac'] = len(ey) / len(e_tok)
        f['e_d_mod_rate'] = safe_frac(e_tok, lambda t: 'd' in t['mods'])
        f['e_ey_vocab'] = len(set(t['middle'] for t in ey)) if ey else 0
        if ey and non_ey:
            f['e_ey_zone_bias'] = (sum(t['line_pos'] for t in ey) / len(ey) -
                                    sum(t['line_pos'] for t in non_ey) / len(non_ey))
        else:
            f['e_ey_zone_bias'] = 0.0
        f['e_edy_dominance'] = sum(1 for t in ey if t['middle'] == 'edy') / len(ey) if ey else 0.0
    else:
        f['e_ey_frac'] = f['e_d_mod_rate'] = f['e_ey_vocab'] = None
        f['e_ey_zone_bias'] = f['e_edy_dominance'] = None

    # ARRANGEMENT
    if len(o_tok) >= 5:
        f['o_l_frac'] = safe_frac(o_tok, lambda t: t['term'] == 'l')
        f['o_r_frac'] = safe_frac(o_tok, lambda t: t['term'] == 'r')
        f['o_exec_mod_rate'] = safe_frac(o_tok, lambda t: 'p' in t['mods'] or 'f' in t['mods'])
    else:
        f['o_l_frac'] = f['o_r_frac'] = f['o_exec_mod_rate'] = None

    # HEADLESS
    if len(hl_tok) >= 10:
        pseudo_atoms = Counter(t['pseudo_head_atom'] for t in hl_tok if t['pseudo_head_atom'])
        f['hl_pseudo_entropy'] = safe_entropy(pseudo_atoms)
        f['hl_mod_rate'] = safe_frac(hl_tok, lambda t: len(t['mods']) > 0)
        f['hl_core_ratio'] = safe_frac(hl_tok, lambda t: t['headless_subtype'] == 'PSEUDO_HEAD_CORE')
        hl_di = [t for t in hl_tok if t['pseudo_head_atom'] in ('d', 'i')]
        hl_cpf = [t for t in hl_tok if t['pseudo_head_atom'] in ('c', 'p', 'f')]
        di_sfx = safe_frac(hl_di, lambda t: t['suffix'] is not None and len(t['suffix']) > 0)
        cpf_sfx = safe_frac(hl_cpf, lambda t: t['suffix'] is not None and len(t['suffix']) > 0)
        f['hl_suffix_bifurc'] = cpf_sfx - di_sfx if di_sfx is not None and cpf_sfx is not None else None
    else:
        f['hl_pseudo_entropy'] = f['hl_mod_rate'] = f['hl_core_ratio'] = f['hl_suffix_bifurc'] = None

    # Cross-domain
    adj_pairs = [(t['prev_term_same_line'], t['head'])
                 for t in tokens if t['prev_term_same_line'] is not None and t['head'] is not None]
    pair_ct = Counter(adj_pairs)
    term_mg = Counter(p[0] for p in adj_pairs)
    head_mg = Counter(p[1] for p in adj_pairs)
    n_pairs = len(adj_pairs)

    def folio_enr(tv, hv):
        obs = pair_ct.get((tv, hv), 0)
        tt = term_mg.get(tv, 0)
        hh = head_mg.get(hv, 0)
        if tt == 0 or n_pairs == 0:
            return None
        exp = tt * (hh / n_pairs)
        return obs / exp if exp > 0 else None

    f['xd_r_to_a'] = folio_enr('r', 'a')
    f['xd_ey_of_total'] = len([t for t in tokens if t['frame'] == 'e->y']) / n_total
    f['xd_headless_frac'] = len(hl_tok) / n_total

    # Zone
    k_spec = safe_frac(k_tok, lambda t: t['line_zone'] == 'SPEC') if k_tok else None
    cs_kspec = corpus_stats.get('k_spec_rate', 0)
    f['zone_k_spec_bias'] = (k_spec / cs_kspec if cs_kspec > 0 else None) if k_spec is not None else None
    f['zone_a_close_rate'] = safe_frac(a_tok, lambda t: t['line_zone'] == 'CLOSE') if a_tok else None
    ey_toks = [t for t in e_tok if t['frame'] == 'e->y']
    ey_early = safe_frac(ey_toks, lambda t: t['quintile'] <= 1) if ey_toks else None
    cs_ey = corpus_stats.get('ey_early_rate', 0)
    f['zone_ey_early_bias'] = (ey_early / cs_ey if cs_ey > 0 else None) if ey_early is not None else None
    hl_close_r = safe_frac(hl_tok, lambda t: t['line_zone'] == 'CLOSE') if hl_tok else None
    cs_hlc = corpus_stats.get('hl_close_rate', 0)
    f['zone_hl_close_surge'] = (hl_close_r / cs_hlc if cs_hlc > 0 else None) if hl_close_r is not None else None

    # Adjacency
    y_toks = [t for t in tokens if t['term'] == 'y' and t['next_domain_same_line'] is not None]
    f['adj_y_to_k_rate'] = safe_frac(y_toks, lambda t: t['next_domain_same_line'] == 'THERMAL') if y_toks else None
    r_toks = [t for t in tokens if t['term'] == 'r' and t['next_domain_same_line'] is not None]
    f['adj_r_to_a_rate'] = safe_frac(r_toks, lambda t: t['next_domain_same_line'] == 'ACTIVE') if r_toks else None
    hh = [t for t in tokens if t['frame_hazard'] == 'HIGH' and t['next_domain_same_line'] is not None]
    f['adj_highhaz_to_safe_rate'] = safe_frac(hh, lambda t: t['next_domain_same_line'] == 'STABILITY') if hh else None
    f['adj_active_close_rate'] = safe_frac(a_tok, lambda t: t['line_zone'] == 'CLOSE') if a_tok else None

    return f


# Import T1b's feature computation
sys.path.insert(0, str(Path(__file__).parent))
from t1b_deployment_features import (
    compute_zone_features, compute_adjacency_features,
    compute_closure_features, compute_headless_features,
    compute_paragraph_features, ALL_FEATURES as DEPLOY_NAMES
)


def compute_deployment_features(tokens):
    """Compute 560b's 56 deployment features from a token list."""
    f = {}
    f.update(compute_zone_features(tokens))
    f.update(compute_adjacency_features(tokens))
    f.update(compute_closure_features(tokens))
    f.update(compute_headless_features(tokens))
    f.update(compute_paragraph_features(tokens))
    return f


def to_vector(feat_dict, names):
    return [feat_dict.get(n) for n in names]


# ===================================================================
# Main
# ===================================================================
def main():
    t0 = time.time()
    print("=== Phase 560b T3b: Within-Section Folio Discriminability ===\n")

    # Load data
    data = load_t1()
    t1b = load_t1b()
    all_tokens = data['corpus_tokens']
    deploy_features = t1b['folio_features']
    print(f"  Loaded {len(all_tokens)} tokens, {len(deploy_features)} folio feature vectors")

    # Group tokens by folio
    folio_tokens = defaultdict(list)
    folio_sections = {}
    for t in all_tokens:
        folio_tokens[t['folio']].append(t)
        folio_sections[t['folio']] = t['section']

    qualifying = sorted(f for f, toks in folio_tokens.items() if len(toks) >= 20)
    labels = [folio_sections[f] for f in qualifying]
    print(f"  Qualifying folios: {len(qualifying)}")

    # Corpus stats for marginal feature computation
    k_all = [t for t in all_tokens if t['domain'] == 'THERMAL']
    ey_all = [t for t in all_tokens if t['frame'] == 'e->y']
    hl_all = [t for t in all_tokens if t['domain'] == 'HEADLESS']
    corpus_stats = {
        'k_spec_rate': sum(1 for t in k_all if t['line_zone'] == 'SPEC') / len(k_all) if k_all else 0,
        'ey_early_rate': sum(1 for t in ey_all if t['quintile'] <= 1) / len(ey_all) if ey_all else 0,
        'hl_close_rate': sum(1 for t in hl_all if t['line_zone'] == 'CLOSE') / len(hl_all) if hl_all else 0,
    }

    # ===================================================================
    # Build all feature vectors
    # ===================================================================
    print("  Building feature vectors...")

    # HEAD (6)
    head_raw = {}
    for f in qualifying:
        toks = folio_tokens[f]
        n = len(toks)
        head_raw[f] = [
            sum(1 for t in toks if t['domain'] == d) / n for d in DOMAINS
        ]

    # MARGINAL (32) - from T1 tokens directly
    marg_raw = {}
    for f in qualifying:
        feat = compute_marginal_features(folio_tokens[f], corpus_stats)
        marg_raw[f] = to_vector(feat, MARGINAL_NAMES)

    # DEPLOYMENT (56) - from precomputed T1b
    dep_raw = {}
    for f in qualifying:
        if f in deploy_features:
            dep_raw[f] = to_vector(deploy_features[f], DEPLOY_NAMES)
        else:
            dep_raw[f] = [None] * len(DEPLOY_NAMES)

    # Z-score each set
    z_head, _, _ = z_score(head_raw, HEAD_NAMES, qualifying)
    z_marg, _, _ = z_score(marg_raw, MARGINAL_NAMES, qualifying)
    z_dep, _, _ = z_score(dep_raw, DEPLOY_NAMES, qualifying)

    # Combined sets
    z_full560 = {f: z_head[f] + z_marg[f] for f in qualifying}   # 38
    z_full560b = {f: z_head[f] + z_dep[f] for f in qualifying}    # 62
    z_combined = {f: z_head[f] + z_marg[f] + z_dep[f] for f in qualifying}  # 94

    feature_sets = {
        'HEAD': (z_head, HEAD_NAMES),
        'MARGINAL': (z_marg, MARGINAL_NAMES),
        'DEPLOYMENT': (z_dep, DEPLOY_NAMES),
        'FULL_560': (z_full560, HEAD_NAMES + MARGINAL_NAMES),
        'FULL_560b': (z_full560b, HEAD_NAMES + DEPLOY_NAMES),
        'COMBINED': (z_combined, HEAD_NAMES + MARGINAL_NAMES + DEPLOY_NAMES),
    }

    # Section grouping
    sec_groups = defaultdict(list)
    for i, f in enumerate(qualifying):
        sec_groups[labels[i]].append(f)
    testable_secs = {s: fols for s, fols in sec_groups.items() if len(fols) >= 10}
    print(f"  Testable sections (>=10 folios): {list(testable_secs.keys())}")

    # ===================================================================
    # D3b: Within-section pairwise distance
    # ===================================================================
    print(f"\n{'='*60}")
    print("D3b: Within-Section Pairwise Distance")
    print(f"{'='*60}")

    d3b_results = {}
    for set_name, (z_vecs, fnames) in feature_sets.items():
        d3b_results[set_name] = {}
        for sec, fols in testable_secs.items():
            # Real mean pairwise distance (z-scored within section)
            sec_raw = {f: z_vecs[f] for f in fols}
            # Re-z-score within section for fair comparison
            sec_vals = {}
            n_feat = len(fnames)
            sec_means = []
            sec_stds = []
            for fi in range(n_feat):
                vals = [sec_raw[f][fi] for f in fols if sec_raw[f][fi] is not None]
                if len(vals) >= 2:
                    m = sum(vals) / len(vals)
                    v = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
                    sec_means.append(m)
                    sec_stds.append(math.sqrt(v) if v > 0 else 1e-10)
                else:
                    sec_means.append(None)
                    sec_stds.append(None)
            for f in fols:
                sec_vals[f] = []
                for fi in range(n_feat):
                    raw = sec_raw[f][fi]
                    if raw is not None and sec_means[fi] is not None:
                        sec_vals[f].append((raw - sec_means[fi]) / sec_stds[fi])
                    else:
                        sec_vals[f].append(None)

            dists = []
            for i in range(len(fols)):
                for j in range(i + 1, len(fols)):
                    dists.append(nan_euclidean(sec_vals[fols[i]], sec_vals[fols[j]]))
            real_mean = sum(dists) / len(dists) if dists else 0

            # Null: shuffle within-domain tokens across folios in this section
            null_means = []
            n_null = min(N_NULL_SEEDS, 100)
            for seed_idx in range(n_null):
                rng = random.Random(SEED_BASE * 3000 + seed_idx)
                sec_domain_pools = defaultdict(list)
                sec_folio_domain_ct = {}
                for f in fols:
                    sec_folio_domain_ct[f] = Counter(t['domain'] for t in folio_tokens[f])
                    for t in folio_tokens[f]:
                        sec_domain_pools[t['domain']].append(t)

                shuffled = {}
                for d, pool in sec_domain_pools.items():
                    sp = list(pool)
                    rng.shuffle(sp)
                    shuffled[d] = sp

                null_tokens = {}
                cursors = {d: 0 for d in sec_domain_pools}
                for f in fols:
                    toks = []
                    for d, ct in sec_folio_domain_ct[f].items():
                        c = cursors[d]
                        toks.extend(shuffled[d][c:c + ct])
                        cursors[d] = c + ct
                    null_tokens[f] = toks

                # Recompute features on shuffled tokens
                null_raw = {}
                if set_name == 'HEAD':
                    for f in fols:
                        n = len(null_tokens[f])
                        null_raw[f] = [sum(1 for t in null_tokens[f] if t['domain'] == d) / n for d in DOMAINS]
                elif set_name == 'MARGINAL':
                    for f in fols:
                        feat = compute_marginal_features(null_tokens[f], corpus_stats)
                        null_raw[f] = to_vector(feat, MARGINAL_NAMES)
                elif set_name == 'DEPLOYMENT':
                    for f in fols:
                        feat = compute_deployment_features(null_tokens[f])
                        null_raw[f] = to_vector(feat, DEPLOY_NAMES)
                elif set_name == 'FULL_560':
                    for f in fols:
                        n = len(null_tokens[f])
                        h = [sum(1 for t in null_tokens[f] if t['domain'] == d) / n for d in DOMAINS]
                        mfeat = compute_marginal_features(null_tokens[f], corpus_stats)
                        null_raw[f] = h + to_vector(mfeat, MARGINAL_NAMES)
                elif set_name == 'FULL_560b':
                    for f in fols:
                        n = len(null_tokens[f])
                        h = [sum(1 for t in null_tokens[f] if t['domain'] == d) / n for d in DOMAINS]
                        dfeat = compute_deployment_features(null_tokens[f])
                        null_raw[f] = h + to_vector(dfeat, DEPLOY_NAMES)
                elif set_name == 'COMBINED':
                    for f in fols:
                        n = len(null_tokens[f])
                        h = [sum(1 for t in null_tokens[f] if t['domain'] == d) / n for d in DOMAINS]
                        mfeat = compute_marginal_features(null_tokens[f], corpus_stats)
                        dfeat = compute_deployment_features(null_tokens[f])
                        null_raw[f] = h + to_vector(mfeat, MARGINAL_NAMES) + to_vector(dfeat, DEPLOY_NAMES)

                # Z-score within section
                n_feat_set = len(list(null_raw.values())[0]) if null_raw else 0
                nm = []
                ns = []
                for fi in range(n_feat_set):
                    vals = [null_raw[f][fi] for f in fols if null_raw[f][fi] is not None]
                    if len(vals) >= 2:
                        m = sum(vals) / len(vals)
                        v = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
                        nm.append(m)
                        ns.append(math.sqrt(v) if v > 0 else 1e-10)
                    else:
                        nm.append(None)
                        ns.append(None)

                null_z = {}
                for f in fols:
                    null_z[f] = []
                    for fi in range(n_feat_set):
                        raw = null_raw[f][fi]
                        if raw is not None and nm[fi] is not None:
                            null_z[f].append((raw - nm[fi]) / ns[fi])
                        else:
                            null_z[f].append(None)

                nd = []
                for i in range(len(fols)):
                    for j in range(i + 1, len(fols)):
                        nd.append(nan_euclidean(null_z[fols[i]], null_z[fols[j]]))
                null_means.append(sum(nd) / len(nd) if nd else 0)

            null_avg = sum(null_means) / len(null_means) if null_means else 0
            null_sd = math.sqrt(sum((x - null_avg) ** 2 for x in null_means) / (len(null_means) - 1)) if len(null_means) > 1 else 0
            passes = real_mean > null_avg + 2 * null_sd

            d3b_results[set_name][sec] = {
                'real_mean': round(real_mean, 4),
                'null_mean': round(null_avg, 4),
                'null_std': round(null_sd, 4),
                'threshold': round(null_avg + 2 * null_sd, 4),
                'n_folios': len(fols),
                'pass': passes,
            }
            status = 'PASS' if passes else 'FAIL'
            print(f"  {set_name:12s} {sec}: real={real_mean:.4f}, null={null_avg:.4f}+/-{null_sd:.4f}, thr={null_avg + 2*null_sd:.4f} {status}")

    # Summarize D3b
    d3b_summary = {}
    for set_name in feature_sets:
        passes = sum(1 for s in d3b_results[set_name].values() if s.get('pass'))
        d3b_summary[set_name] = {
            'sections_pass': passes,
            'total_sections': len(testable_secs),
            'pass': passes >= 2,
        }
        print(f"  {set_name:12s}: {passes}/{len(testable_secs)} sections pass -> {'PASS' if passes >= 2 else 'FAIL'}")

    # ===================================================================
    # D4b: Hierarchical clustering (Ward linkage)
    # ===================================================================
    print(f"\n{'='*60}")
    print("D4b: Hierarchical Clustering (Ward linkage)")
    print(f"{'='*60}")

    d4b_results = {}
    try:
        from scipy.cluster.hierarchy import ward, fcluster
        from scipy.spatial.distance import pdist
        from sklearn.metrics import adjusted_rand_score

        n_clusters = len(set(labels))
        for set_name, (z_vecs, fnames) in feature_sets.items():
            # Build distance matrix with NaN handling
            vecs = []
            for f in qualifying:
                v = z_vecs[f]
                # Replace None with 0 for scipy (imputation)
                vecs.append([x if x is not None else 0.0 for x in v])

            import numpy as np
            X = np.array(vecs)
            Z = ward(pdist(X))
            pred = fcluster(Z, t=n_clusters, criterion='maxclust')
            ari = float(adjusted_rand_score(labels, pred))

            d4b_results[set_name] = {
                'ari_ward': round(ari, 4),
                'n_clusters': n_clusters,
                'pass': ari > 0.10,
            }
            print(f"  {set_name:12s}: ARI={ari:.4f} {'PASS' if ari > 0.10 else 'FAIL'}")

    except ImportError:
        print("  scipy/sklearn not available, skipping D4b")
        for set_name in feature_sets:
            d4b_results[set_name] = {'ari_ward': None, 'pass': False, 'error': 'scipy not available'}

    # ===================================================================
    # D5b: Gain test (LOO-NN + RF)
    # ===================================================================
    print(f"\n{'='*60}")
    print("D5b: Gain Test")
    print(f"{'='*60}")

    # LOO-NN for each set
    d5b_nn = {}
    for set_name, (z_vecs, fnames) in feature_sets.items():
        acc = leave_one_out_nn(z_vecs, qualifying, labels)
        d5b_nn[set_name] = round(acc, 4)
        print(f"  NN {set_name:12s}: {acc:.4f}")

    nn_gain_560b = d5b_nn.get('FULL_560b', 0) - d5b_nn.get('FULL_560', 0)
    nn_gain_combined = d5b_nn.get('COMBINED', 0) - d5b_nn.get('FULL_560', 0)
    print(f"  NN gain: FULL_560b vs FULL_560 = {nn_gain_560b:+.4f}")
    print(f"  NN gain: COMBINED vs FULL_560 = {nn_gain_combined:+.4f}")

    # RF 5-fold CV
    d5b_rf = {}
    rf_importances = {}
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score
        import numpy as np

        for set_name, (z_vecs, fnames) in feature_sets.items():
            X = np.array([[x if x is not None else 0.0 for x in z_vecs[f]] for f in qualifying])
            y = np.array(labels)

            clf = RandomForestClassifier(n_estimators=200, max_depth=3, random_state=42)
            scores = cross_val_score(clf, X, y, cv=5)
            acc = float(scores.mean())
            d5b_rf[set_name] = round(acc, 4)
            print(f"  RF {set_name:12s}: {acc:.4f} (+/-{float(scores.std()):.4f})")

            # Feature importances for COMBINED
            if set_name == 'COMBINED':
                clf.fit(X, y)
                all_names = HEAD_NAMES + MARGINAL_NAMES + DEPLOY_NAMES
                imps = list(zip(all_names, clf.feature_importances_))
                imps.sort(key=lambda x: -x[1])
                rf_importances = {name: round(float(imp), 6) for name, imp in imps[:20]}
                print(f"\n  Top 20 RF importances (COMBINED):")
                for rank, (name, imp) in enumerate(imps[:20], 1):
                    print(f"    {rank:2d}. {name:35s} {imp:.4f}")

        rf_gain_560b = d5b_rf.get('FULL_560b', 0) - d5b_rf.get('FULL_560', 0)
        rf_gain_combined = d5b_rf.get('COMBINED', 0) - d5b_rf.get('FULL_560', 0)
        print(f"\n  RF gain: FULL_560b vs FULL_560 = {rf_gain_560b:+.4f}")
        print(f"  RF gain: COMBINED vs FULL_560 = {rf_gain_combined:+.4f}")

    except ImportError:
        print("  sklearn not available, skipping RF")
        rf_gain_560b = 0
        rf_gain_combined = 0

    d5b_pass = (nn_gain_560b >= 0.02 or rf_gain_560b >= 0.02 or
                nn_gain_combined >= 0.03 or rf_gain_combined >= 0.03)
    print(f"\n  D5b: {'PASS' if d5b_pass else 'FAIL'}")

    # ===================================================================
    # D7: Within-section variance decomposition
    # ===================================================================
    print(f"\n{'='*60}")
    print("D7: Within-Section Variance Decomposition")
    print(f"{'='*60}")

    all_feat_names = MARGINAL_NAMES + DEPLOY_NAMES
    all_feat_raw = {}
    for f in qualifying:
        all_feat_raw[f] = to_vector(
            {**dict(zip(MARGINAL_NAMES, marg_raw[f])),
             **dict(zip(DEPLOY_NAMES, dep_raw[f]))},
            all_feat_names
        )

    d7_results = {}
    marg_high = 0
    dep_high = 0
    for fi, fname in enumerate(all_feat_names):
        sec_vals = defaultdict(list)
        all_vals = []
        for f in qualifying:
            val = all_feat_raw[f][fi]
            if val is not None:
                sec_vals[folio_sections[f]].append(val)
                all_vals.append(val)

        if len(all_vals) < 10:
            d7_results[fname] = {'within_ratio': None, 'n_valid': len(all_vals)}
            continue

        grand_mean = sum(all_vals) / len(all_vals)
        total_var = sum((v - grand_mean) ** 2 for v in all_vals) / (len(all_vals) - 1)

        within_ss = 0
        within_df = 0
        for sec, vals in sec_vals.items():
            if len(vals) < 2:
                continue
            sec_mean = sum(vals) / len(vals)
            within_ss += sum((v - sec_mean) ** 2 for v in vals)
            within_df += len(vals) - 1

        within_var = within_ss / within_df if within_df > 0 else 0
        within_ratio = within_var / total_var if total_var > 0 else 0

        d7_results[fname] = {
            'total_var': round(total_var, 6),
            'within_var': round(within_var, 6),
            'within_ratio': round(within_ratio, 4),
            'n_valid': len(all_vals),
        }

        if within_ratio > 0.5:
            if fname in MARGINAL_NAMES:
                marg_high += 1
            else:
                dep_high += 1

    d7_pass = dep_high > marg_high or dep_high >= 20
    print(f"  Marginal features with within-section ratio > 0.5: {marg_high}/{len(MARGINAL_NAMES)}")
    print(f"  Deployment features with within-section ratio > 0.5: {dep_high}/{len(DEPLOY_NAMES)}")
    print(f"  D7: {'PASS' if d7_pass else 'FAIL'} (deployment > marginal or >= 20)")

    # Top within-section features
    sorted_d7 = sorted(
        [(fname, d7_results[fname]['within_ratio'])
         for fname in all_feat_names if d7_results[fname].get('within_ratio') is not None],
        key=lambda x: -x[1]
    )
    print(f"\n  Top 15 features by within-section variance ratio:")
    for rank, (fname, wr) in enumerate(sorted_d7[:15], 1):
        source = 'DEPLOY' if fname in DEPLOY_NAMES else 'MARGINAL'
        print(f"    {rank:2d}. {fname:40s} {wr:.4f} ({source})")

    # ===================================================================
    # OUTPUT
    # ===================================================================
    output = {
        'metadata': {
            'phase': '560b',
            'task': 'T3b_discriminability',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_folios': len(qualifying),
            'testable_sections': list(testable_secs.keys()),
            'feature_set_sizes': {name: len(fnames) for name, (_, fnames) in feature_sets.items()},
        },
        'D3b': {
            'per_set': d3b_results,
            'summary': d3b_summary,
        },
        'D4b': d4b_results,
        'D5b': {
            'nn_accuracies': d5b_nn,
            'rf_accuracies': d5b_rf,
            'nn_gain_560b': round(nn_gain_560b, 4),
            'nn_gain_combined': round(nn_gain_combined, 4),
            'rf_gain_560b': round(float(rf_gain_560b), 4) if rf_gain_560b else 0,
            'rf_gain_combined': round(float(rf_gain_combined), 4) if rf_gain_combined else 0,
            'rf_top20_importances': rf_importances,
            'pass': d5b_pass,
        },
        'D7': {
            'per_feature': d7_results,
            'marginal_high_ratio_count': marg_high,
            'deployment_high_ratio_count': dep_high,
            'pass': d7_pass,
        },
    }

    out_path = RESULTS_DIR / 't3b_discriminability.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1, default=lambda x: float(x) if hasattr(x, 'item') else x)
    print(f"\nWrote {out_path}")
    print(f"Runtime: {time.time()-t0:.1f}s")


if __name__ == '__main__':
    main()
