"""Phase 560 T3: Cross-Folio Domain Profile Discriminability

Builds 32-feature per-folio within-domain profiles, runs permutation nulls,
and tests D1-D6 discriminability.

Input: t1_domain_decomposition.json
Output: t3_cross_folio_discriminability.json
"""
import json
import math
import os
import sys
import time
import random
from pathlib import Path
from collections import Counter, defaultdict

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_NULL_SEEDS = 200
SEED_BASE = 42


def load_t1():
    path = RESULTS_DIR / 't1_domain_decomposition.json'
    with open(path) as f:
        return json.load(f)


def safe_frac(tokens, fn):
    if not tokens:
        return None
    return sum(1 for t in tokens if fn(t)) / len(tokens)


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


def jsd(dist_a, dist_b):
    """JSD between two count dicts."""
    all_keys = set(dist_a) | set(dist_b)
    ta = sum(dist_a.values()) or 1
    tb = sum(dist_b.values()) or 1
    m = {}
    for k in all_keys:
        m[k] = (dist_a.get(k, 0) / ta + dist_b.get(k, 0) / tb) / 2

    def kl(p, total, q):
        d = 0.0
        for k in all_keys:
            pk = p.get(k, 0) / total
            qk = q[k]
            if pk > 0 and qk > 0:
                d += pk * math.log2(pk / qk)
        return d

    return 0.5 * kl(dist_a, ta, m) + 0.5 * kl(dist_b, tb, m)


# ═══════════════════════════════════════════════════════════
# STEP 1: Feature extraction
# ═══════════════════════════════════════════════════════════
def compute_folio_features(tokens, corpus_stats):
    """Compute 32 within-domain features for a set of tokens (one folio).

    Returns dict with feature names -> float or None.
    """
    f = {}
    n_total = len(tokens)
    if n_total == 0:
        return {k: None for k in _FEATURE_NAMES}

    # Domain subsets
    by_domain = defaultdict(list)
    for t in tokens:
        by_domain[t['domain']].append(t)

    k_tok = by_domain['THERMAL']
    t_tok = by_domain['FLOW']
    a_tok = by_domain['ACTIVE']
    e_tok = by_domain['STABILITY']
    o_tok = by_domain['ARRANGEMENT']
    hl_tok = by_domain['HEADLESS']

    # --- THERMAL (3 features, requires >= 5) ---
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
        f['k_suffix_entropy'] = None
        f['k_bare_term_frac'] = None
        f['k_thermal_purity'] = None

    # --- FLOW (2 features, requires >= 3) ---
    if len(t_tok) >= 3:
        f['t_mod_rate'] = safe_frac(t_tok, lambda t: len(t['mods']) > 0)
        f['t_flow_purity'] = safe_frac(t_tok, lambda t: t['operational_category'] == 'FLOW')
    else:
        f['t_mod_rate'] = None
        f['t_flow_purity'] = None

    # --- ACTIVE (4 features, requires >= 5) ---
    if len(a_tok) >= 5:
        f['a_i_rate'] = safe_frac(a_tok, lambda t: t['has_i_mod'])
        f['a_ii_rate'] = safe_frac(a_tok, lambda t: t['i_count'] >= 2)
        f['a_n_term_rate'] = safe_frac(a_tok, lambda t: t['term'] == 'n')
        f['a_hazard_rate'] = safe_frac(a_tok, lambda t: t['frame_hazard'] == 'HIGH')
    else:
        f['a_i_rate'] = None
        f['a_ii_rate'] = None
        f['a_n_term_rate'] = None
        f['a_hazard_rate'] = None

    # --- STABILITY (5 features, requires >= 10) ---
    if len(e_tok) >= 10:
        ey = [t for t in e_tok if t['frame'] == 'e->y']
        non_ey = [t for t in e_tok if t['frame'] != 'e->y']
        f['e_ey_frac'] = len(ey) / len(e_tok)
        f['e_d_mod_rate'] = safe_frac(e_tok, lambda t: 'd' in t['mods'])
        f['e_ey_vocab'] = len(set(t['middle'] for t in ey)) if ey else 0
        # Zone bias: mean line_pos of ey minus mean line_pos of non-ey
        if ey and non_ey:
            ey_pos = sum(t['line_pos'] for t in ey) / len(ey)
            non_ey_pos = sum(t['line_pos'] for t in non_ey) / len(non_ey)
            f['e_ey_zone_bias'] = ey_pos - non_ey_pos
        else:
            f['e_ey_zone_bias'] = 0.0
        # edy dominance within e->y
        if ey:
            f['e_edy_dominance'] = sum(1 for t in ey if t['middle'] == 'edy') / len(ey)
        else:
            f['e_edy_dominance'] = 0.0
    else:
        f['e_ey_frac'] = None
        f['e_d_mod_rate'] = None
        f['e_ey_vocab'] = None
        f['e_ey_zone_bias'] = None
        f['e_edy_dominance'] = None

    # --- ARRANGEMENT (3 features, requires >= 5) ---
    if len(o_tok) >= 5:
        f['o_l_frac'] = safe_frac(o_tok, lambda t: t['term'] == 'l')
        f['o_r_frac'] = safe_frac(o_tok, lambda t: t['term'] == 'r')
        f['o_exec_mod_rate'] = safe_frac(o_tok, lambda t: 'p' in t['mods'] or 'f' in t['mods'])
    else:
        f['o_l_frac'] = None
        f['o_r_frac'] = None
        f['o_exec_mod_rate'] = None

    # --- HEADLESS (4 features, requires >= 10) ---
    if len(hl_tok) >= 10:
        pseudo_atoms = Counter(t['pseudo_head_atom'] for t in hl_tok if t['pseudo_head_atom'])
        f['hl_pseudo_entropy'] = safe_entropy(pseudo_atoms)
        f['hl_mod_rate'] = safe_frac(hl_tok, lambda t: len(t['mods']) > 0)
        f['hl_core_ratio'] = safe_frac(hl_tok, lambda t: t['headless_subtype'] == 'PSEUDO_HEAD_CORE')
        # Suffix bifurcation: cpf suffix rate minus di suffix rate
        hl_di = [t for t in hl_tok if t['pseudo_head_atom'] in ('d', 'i')]
        hl_cpf = [t for t in hl_tok if t['pseudo_head_atom'] in ('c', 'p', 'f')]
        di_sfx = safe_frac(hl_di, lambda t: t['suffix'] is not None and len(t['suffix']) > 0)
        cpf_sfx = safe_frac(hl_cpf, lambda t: t['suffix'] is not None and len(t['suffix']) > 0)
        if di_sfx is not None and cpf_sfx is not None:
            f['hl_suffix_bifurc'] = cpf_sfx - di_sfx
        else:
            f['hl_suffix_bifurc'] = None
    else:
        f['hl_pseudo_entropy'] = None
        f['hl_mod_rate'] = None
        f['hl_core_ratio'] = None
        f['hl_suffix_bifurc'] = None

    # --- Cross-domain routing (3 features) ---
    # r->a routing enrichment (folio vs corpus)
    adj_pairs = [(t['prev_term_same_line'], t['head'])
                 for t in tokens
                 if t['prev_term_same_line'] is not None and t['head'] is not None]
    pair_ct = Counter(adj_pairs)
    term_mg = Counter(p[0] for p in adj_pairs)
    head_mg = Counter(p[1] for p in adj_pairs)
    n_pairs = len(adj_pairs)

    def folio_enr(term_val, head_val):
        obs = pair_ct.get((term_val, head_val), 0)
        tt = term_mg.get(term_val, 0)
        hh = head_mg.get(head_val, 0)
        if tt == 0 or n_pairs == 0:
            return None
        exp = tt * (hh / n_pairs)
        if exp == 0:
            return None
        return obs / exp

    f['xd_r_to_a'] = folio_enr('r', 'a')
    f['xd_ey_of_total'] = len([t for t in tokens if t['frame'] == 'e->y']) / n_total
    f['xd_headless_frac'] = len(hl_tok) / n_total

    # --- Zone-deployment (4 features) ---
    # k in SPEC zone vs corpus rate
    k_in_spec = safe_frac(k_tok, lambda t: t['line_zone'] == 'SPEC') if k_tok else None
    corpus_k_spec = corpus_stats.get('k_spec_rate', 0)
    f['zone_k_spec_bias'] = (k_in_spec / corpus_k_spec if corpus_k_spec > 0 else None) if k_in_spec is not None else None

    # a in CLOSE zone
    f['zone_a_close_rate'] = safe_frac(a_tok, lambda t: t['line_zone'] == 'CLOSE') if a_tok else None

    # e->y in early zone (Q0-Q1)
    ey_toks = [t for t in e_tok if t['frame'] == 'e->y']
    ey_early = safe_frac(ey_toks, lambda t: t['quintile'] <= 1) if ey_toks else None
    corpus_ey_early = corpus_stats.get('ey_early_rate', 0)
    f['zone_ey_early_bias'] = (ey_early / corpus_ey_early if corpus_ey_early > 0 else None) if ey_early is not None else None

    # headless in CLOSE zone vs corpus
    hl_close = safe_frac(hl_tok, lambda t: t['line_zone'] == 'CLOSE') if hl_tok else None
    corpus_hl_close = corpus_stats.get('hl_close_rate', 0)
    f['zone_hl_close_surge'] = (hl_close / corpus_hl_close if corpus_hl_close > 0 else None) if hl_close is not None else None

    # --- Adjacency (4 features) ---
    # y-term followed by k-HEAD on same line
    y_term_toks = [t for t in tokens if t['term'] == 'y' and t['next_domain_same_line'] is not None]
    f['adj_y_to_k_rate'] = safe_frac(y_term_toks, lambda t: t['next_domain_same_line'] == 'THERMAL') if y_term_toks else None

    # r-term followed by a-HEAD
    r_term_toks = [t for t in tokens if t['term'] == 'r' and t['next_domain_same_line'] is not None]
    f['adj_r_to_a_rate'] = safe_frac(r_term_toks, lambda t: t['next_domain_same_line'] == 'ACTIVE') if r_term_toks else None

    # HIGH-hazard followed by safe pathway
    high_haz = [t for t in tokens if t['frame_hazard'] == 'HIGH' and t['next_domain_same_line'] is not None]
    # We don't have next token's is_safe_pathway directly, but we can check next domain
    # Use a proxy: next token is STABILITY domain (likely e->y)
    f['adj_highhaz_to_safe_rate'] = safe_frac(high_haz, lambda t: t['next_domain_same_line'] == 'STABILITY') if high_haz else None

    # ACTIVE domain tokens in CLOSE zone
    f['adj_active_close_rate'] = safe_frac(a_tok, lambda t: t['line_zone'] == 'CLOSE') if a_tok else None

    return f


# Feature name list (for consistent ordering)
_FEATURE_NAMES = [
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


def features_to_vector(feat_dict):
    """Convert feature dict to list, with None preserved."""
    return [feat_dict.get(name) for name in _FEATURE_NAMES]


def nan_euclidean(v1, v2):
    """Euclidean distance ignoring features where either is None."""
    s = 0.0
    n = 0
    for a, b in zip(v1, v2):
        if a is not None and b is not None:
            s += (a - b) ** 2
            n += 1
    if n == 0:
        return float('inf')
    return math.sqrt(s)


def z_score_matrix(folio_vectors, folio_names):
    """Z-score each feature across folios, ignoring None."""
    n_feat = len(_FEATURE_NAMES)
    n_fol = len(folio_names)

    # Compute mean and std per feature
    means = []
    stds = []
    for fi in range(n_feat):
        vals = [folio_vectors[f][fi] for f in folio_names
                if folio_vectors[f][fi] is not None]
        if len(vals) < 2:
            means.append(None)
            stds.append(None)
        else:
            m = sum(vals) / len(vals)
            v = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
            means.append(m)
            stds.append(math.sqrt(v) if v > 0 else 1e-10)

    # Z-score
    z_vectors = {}
    for f in folio_names:
        z = []
        for fi in range(n_feat):
            raw = folio_vectors[f][fi]
            if raw is not None and means[fi] is not None:
                z.append((raw - means[fi]) / stds[fi])
            else:
                z.append(None)
        z_vectors[f] = z

    return z_vectors, means, stds


def leave_one_out_nn(z_vectors, folio_names, labels):
    """Leave-one-out nearest neighbor classification. Returns accuracy."""
    correct = 0
    for i, f in enumerate(folio_names):
        best_dist = float('inf')
        best_label = None
        for j, g in enumerate(folio_names):
            if i == j:
                continue
            d = nan_euclidean(z_vectors[f], z_vectors[g])
            if d < best_dist:
                best_dist = d
                best_label = labels[j]
        if best_label == labels[i]:
            correct += 1
    return correct / len(folio_names)


def main():
    t0 = time.time()
    print("=== Phase 560 T3: Cross-Folio Domain Profile Discriminability ===")

    data = load_t1()
    all_tokens = data['corpus_tokens']
    print(f"  Loaded {len(all_tokens)} tokens")

    # ═══════════════════════════════════════════════════════════
    # Step 1: Corpus-wide stats for enrichment baselines
    # ═══════════════════════════════════════════════════════════
    print("  Computing corpus-wide stats...")
    k_all = [t for t in all_tokens if t['domain'] == 'THERMAL']
    k_spec_total = sum(1 for t in k_all if t['line_zone'] == 'SPEC')
    corpus_stats = {
        'k_spec_rate': k_spec_total / len(k_all) if k_all else 0,
    }
    ey_all = [t for t in all_tokens if t['frame'] == 'e->y']
    corpus_stats['ey_early_rate'] = (
        sum(1 for t in ey_all if t['quintile'] <= 1) / len(ey_all) if ey_all else 0)
    hl_all = [t for t in all_tokens if t['domain'] == 'HEADLESS']
    corpus_stats['hl_close_rate'] = (
        sum(1 for t in hl_all if t['line_zone'] == 'CLOSE') / len(hl_all) if hl_all else 0)

    # ═══════════════════════════════════════════════════════════
    # Step 2: Compute per-folio features
    # ═══════════════════════════════════════════════════════════
    print("  Computing per-folio features...")
    folio_tokens = defaultdict(list)
    folio_sections = {}
    for t in all_tokens:
        folio_tokens[t['folio']].append(t)
        folio_sections[t['folio']] = t['section']

    # Filter to folios with >= 20 tokens
    qualifying_folios = sorted(f for f, toks in folio_tokens.items() if len(toks) >= 20)
    print(f"  Qualifying folios (>=20 tokens): {len(qualifying_folios)}")

    folio_features = {}
    folio_vectors = {}
    for f in qualifying_folios:
        feat = compute_folio_features(folio_tokens[f], corpus_stats)
        folio_features[f] = feat
        folio_vectors[f] = features_to_vector(feat)

    # ═══════════════════════════════════════════════════════════
    # Step 3: Z-score and prepare for classification
    # ═══════════════════════════════════════════════════════════
    labels = [folio_sections[f] for f in qualifying_folios]
    z_vectors, z_means, z_stds = z_score_matrix(folio_vectors, qualifying_folios)

    # ═══════════════════════════════════════════════════════════
    # Step 4: HEAD-only baseline features (6 features)
    # ═══════════════════════════════════════════════════════════
    print("  Computing HEAD-only baseline features...")
    head_vectors = {}
    for f in qualifying_folios:
        toks = folio_tokens[f]
        n = len(toks)
        head_fracs = {
            'k_frac': sum(1 for t in toks if t['domain'] == 'THERMAL') / n,
            't_frac': sum(1 for t in toks if t['domain'] == 'FLOW') / n,
            'a_frac': sum(1 for t in toks if t['domain'] == 'ACTIVE') / n,
            'e_frac': sum(1 for t in toks if t['domain'] == 'STABILITY') / n,
            'o_frac': sum(1 for t in toks if t['domain'] == 'ARRANGEMENT') / n,
            'hl_frac': sum(1 for t in toks if t['domain'] == 'HEADLESS') / n,
        }
        head_vectors[f] = list(head_fracs.values())

    # Z-score HEAD-only
    head_feat_names = ['k_frac', 't_frac', 'a_frac', 'e_frac', 'o_frac', 'hl_frac']
    n_hf = len(head_feat_names)
    h_means = []
    h_stds = []
    for fi in range(n_hf):
        vals = [head_vectors[f][fi] for f in qualifying_folios]
        m = sum(vals) / len(vals)
        v = sum((x - m) ** 2 for x in vals) / (len(vals) - 1) if len(vals) > 1 else 0
        h_means.append(m)
        h_stds.append(math.sqrt(v) if v > 0 else 1e-10)

    z_head = {}
    for f in qualifying_folios:
        z_head[f] = [(head_vectors[f][fi] - h_means[fi]) / h_stds[fi]
                     for fi in range(n_hf)]

    # Full = HEAD + within-domain (38 features)
    z_full = {}
    for f in qualifying_folios:
        z_full[f] = z_head[f] + z_vectors[f]

    # ═══════════════════════════════════════════════════════════
    # Step 5: Null model — within-domain permutation
    # ═══════════════════════════════════════════════════════════
    print(f"  Generating {N_NULL_SEEDS} null permutations...")
    null_accuracies_full = []
    null_accuracies_head = []

    # For null: shuffle tokens across folios within each domain
    domain_pools = defaultdict(list)
    folio_domain_counts = {}
    for f in qualifying_folios:
        folio_domain_counts[f] = Counter(t['domain'] for t in folio_tokens[f])
        for t in folio_tokens[f]:
            domain_pools[t['domain']].append(t)

    for seed_idx in range(N_NULL_SEEDS):
        rng = random.Random(SEED_BASE + seed_idx)

        # Shuffle within each domain
        shuffled_pools = {}
        for d, pool in domain_pools.items():
            shuffled = list(pool)
            rng.shuffle(shuffled)
            shuffled_pools[d] = shuffled

        # Reconstruct folio token lists preserving domain counts
        null_folio_tokens = {}
        domain_cursors = {d: 0 for d in domain_pools}
        for f in qualifying_folios:
            toks = []
            for d, ct in folio_domain_counts[f].items():
                cursor = domain_cursors[d]
                toks.extend(shuffled_pools[d][cursor:cursor + ct])
                domain_cursors[d] = cursor + ct
            null_folio_tokens[f] = toks

        # Compute null features
        null_feat = {}
        null_vec = {}
        for f in qualifying_folios:
            feat = compute_folio_features(null_folio_tokens[f], corpus_stats)
            null_vec[f] = features_to_vector(feat)

        # Z-score null
        null_z, _, _ = z_score_matrix(null_vec, qualifying_folios)

        # Full null (head + within-domain)
        null_full = {}
        for f in qualifying_folios:
            null_full[f] = z_head[f] + null_z[f]  # HEAD stays real, within-domain is shuffled

        # LOO-NN on null full
        acc_full = leave_one_out_nn(null_full, qualifying_folios, labels)
        null_accuracies_full.append(acc_full)

        # LOO-NN on real HEAD-only (constant across nulls, but track for comparison)
        if seed_idx == 0:
            head_acc = leave_one_out_nn(z_head, qualifying_folios, labels)

        if (seed_idx + 1) % 50 == 0:
            print(f"    Null seed {seed_idx + 1}/{N_NULL_SEEDS}")

    null_mean_full = sum(null_accuracies_full) / len(null_accuracies_full)
    null_std_full = math.sqrt(sum((x - null_mean_full) ** 2 for x in null_accuracies_full)
                              / (len(null_accuracies_full) - 1)) if len(null_accuracies_full) > 1 else 0

    # ═══════════════════════════════════════════════════════════
    # D1: Section Classification (LOO-NN on z-scored full features)
    # ═══════════════════════════════════════════════════════════
    print("\n  === D1: Section Classification ===")
    real_acc = leave_one_out_nn(z_vectors, qualifying_folios, labels)
    d1_pass = real_acc > null_mean_full + 2 * null_std_full and real_acc > 0.40
    d1_result = {
        'accuracy': round(real_acc, 4),
        'null_mean': round(null_mean_full, 4),
        'null_std': round(null_std_full, 4),
        'threshold_2sigma': round(null_mean_full + 2 * null_std_full, 4),
        'pass': d1_pass,
    }
    print(f"  Accuracy: {real_acc:.4f} (null: {null_mean_full:.4f} +/- {null_std_full:.4f})")
    print(f"  Threshold: > {null_mean_full + 2*null_std_full:.4f} AND > 0.40 -> {'PASS' if d1_pass else 'FAIL'}")

    # ═══════════════════════════════════════════════════════════
    # D2: Feature-Level Variance Decomposition
    # ═══════════════════════════════════════════════════════════
    print("\n  === D2: Variance Decomposition ===")
    # One-way ANOVA by section for each feature
    section_folios = defaultdict(list)
    for f in qualifying_folios:
        section_folios[folio_sections[f]].append(f)

    d2_results = {}
    n_sig = 0
    for fi, fname in enumerate(_FEATURE_NAMES):
        # Get values by section (skip None)
        groups = {}
        for sec, fols in section_folios.items():
            vals = [folio_vectors[f][fi] for f in fols if folio_vectors[f][fi] is not None]
            if vals:
                groups[sec] = vals

        if len(groups) < 2:
            d2_results[fname] = {'F': None, 'p': None, 'n_groups': len(groups)}
            continue

        # Overall mean
        all_vals = [v for vs in groups.values() for v in vs]
        grand_mean = sum(all_vals) / len(all_vals)
        n_total_vals = len(all_vals)

        # Between-group SS
        ss_between = sum(len(vs) * (sum(vs)/len(vs) - grand_mean) ** 2
                        for vs in groups.values())
        df_between = len(groups) - 1

        # Within-group SS
        ss_within = sum(sum((v - sum(vs)/len(vs)) ** 2 for v in vs)
                       for vs in groups.values())
        df_within = n_total_vals - len(groups)

        if df_within > 0 and df_between > 0 and ss_within > 0:
            f_stat = (ss_between / df_between) / (ss_within / df_within)
            # Approximate p-value using F-distribution approximation
            # For simplicity, use the R^2 and flag significance based on F > threshold
            r2_section = ss_between / (ss_between + ss_within) if (ss_between + ss_within) > 0 else 0
            # F critical at p=0.01 for df_between~5, df_within~75 is ~3.2
            p_approx = 'sig' if f_stat > 3.2 else 'ns'
            if p_approx == 'sig':
                n_sig += 1
        else:
            f_stat = 0
            r2_section = 0
            p_approx = 'ns'

        d2_results[fname] = {
            'F': round(f_stat, 3),
            'R2_section': round(r2_section, 4),
            'significant': p_approx == 'sig',
        }

    d2_pass = n_sig >= 10
    print(f"  Features with significant section variance: {n_sig}/32 (threshold: >= 10)")
    print(f"  D2: {'PASS' if d2_pass else 'FAIL'}")

    # ═══════════════════════════════════════════════════════════
    # D3: Within-Section Folio Discriminability
    # ═══════════════════════════════════════════════════════════
    # Test: within each section with >= 10 folios, are individual folios
    # distinguishable by their within-domain profiles? Measured by
    # mean pairwise distance > permutation null (shuffled tokens within section).
    print("\n  === D3: Within-Section Folio Discriminability ===")
    d3_results = {}
    d3_pass_count = 0

    for sec, fols in section_folios.items():
        if len(fols) < 10:
            d3_results[sec] = {'n_folios': len(fols), 'skip': True}
            continue

        # Real mean pairwise distance (z-scored within section)
        sec_z, _, _ = z_score_matrix(
            {f: folio_vectors[f] for f in fols}, fols)
        dists = []
        for i in range(len(fols)):
            for j in range(i + 1, len(fols)):
                dists.append(nan_euclidean(sec_z[fols[i]], sec_z[fols[j]]))
        real_mean_dist = sum(dists) / len(dists) if dists else 0

        # Null: shuffle within-domain tokens across folios in this section
        sec_tokens = []
        sec_folio_sizes = {}
        for f in fols:
            sec_tokens.extend(folio_tokens[f])
            sec_folio_sizes[f] = len(folio_tokens[f])

        null_dists = []
        for seed_idx in range(min(N_NULL_SEEDS, 100)):  # 100 seeds for speed
            rng = random.Random(SEED_BASE * 2000 + seed_idx)
            # Build domain pools within this section
            sec_domain_pools = defaultdict(list)
            sec_folio_domain_ct = {}
            for f in fols:
                sec_folio_domain_ct[f] = Counter(t['domain'] for t in folio_tokens[f])
                for t in folio_tokens[f]:
                    sec_domain_pools[t['domain']].append(t)

            # Shuffle each domain pool
            for d in sec_domain_pools:
                rng.shuffle(sec_domain_pools[d])

            # Reassign to folios preserving domain counts
            domain_cursors = {d: 0 for d in sec_domain_pools}
            null_folio_toks = {}
            for f in fols:
                ftoks = []
                for d, ct in sec_folio_domain_ct[f].items():
                    c = domain_cursors[d]
                    ftoks.extend(sec_domain_pools[d][c:c + ct])
                    domain_cursors[d] = c + ct
                null_folio_toks[f] = ftoks

            # Compute null features
            null_vec = {}
            for f in fols:
                feat = compute_folio_features(null_folio_toks[f], corpus_stats)
                null_vec[f] = features_to_vector(feat)

            null_z, _, _ = z_score_matrix(null_vec, fols)
            nd = []
            for i in range(len(fols)):
                for j in range(i + 1, len(fols)):
                    nd.append(nan_euclidean(null_z[fols[i]], null_z[fols[j]]))
            null_dists.append(sum(nd) / len(nd) if nd else 0)

        null_mean = sum(null_dists) / len(null_dists) if null_dists else 0
        null_std = (math.sqrt(sum((x - null_mean) ** 2 for x in null_dists)
                             / (len(null_dists) - 1)) if len(null_dists) > 1 else 0)
        # Pass if real distance > null_mean + 2*std (folios are more different than expected)
        passes = real_mean_dist > null_mean + 2 * null_std and real_mean_dist > 0
        if passes:
            d3_pass_count += 1

        d3_results[sec] = {
            'n_folios': len(fols),
            'real_mean_dist': round(real_mean_dist, 4),
            'null_mean_dist': round(null_mean, 4),
            'null_std': round(null_std, 4),
            'threshold': round(null_mean + 2 * null_std, 4),
            'pass': passes,
        }
        print(f"  {sec}: real={real_mean_dist:.4f}, null={null_mean:.4f}+/-{null_std:.4f} "
              f"-> {'PASS' if passes else 'FAIL'}")

    d3_pass = d3_pass_count >= 2
    print(f"  D3: {d3_pass_count} sections pass (threshold: >= 2) -> {'PASS' if d3_pass else 'FAIL'}")

    # ═══════════════════════════════════════════════════════════
    # D4: Hierarchical Clustering (ARI)
    # ═══════════════════════════════════════════════════════════
    print("\n  === D4: Clustering Coherence ===")
    # Simple agglomerative clustering (single linkage for simplicity)
    # Use z-scored features
    from itertools import combinations

    # Build distance matrix
    n_fol = len(qualifying_folios)
    dist_matrix = {}
    for i in range(n_fol):
        for j in range(i + 1, n_fol):
            d = nan_euclidean(z_vectors[qualifying_folios[i]],
                             z_vectors[qualifying_folios[j]])
            dist_matrix[(i, j)] = d
            dist_matrix[(j, i)] = d

    # Single-linkage agglomerative to get ~6 clusters (number of sections)
    n_sections = len(set(labels))
    clusters = {i: {i} for i in range(n_fol)}
    cluster_labels = list(range(n_fol))

    while len(clusters) > n_sections:
        # Find closest pair of clusters
        best_dist = float('inf')
        best_pair = None
        cluster_ids = list(clusters.keys())
        for ci in range(len(cluster_ids)):
            for cj in range(ci + 1, len(cluster_ids)):
                a_id, b_id = cluster_ids[ci], cluster_ids[cj]
                # Single linkage: minimum distance
                min_d = min(dist_matrix.get((i, j), float('inf'))
                           for i in clusters[a_id] for j in clusters[b_id])
                if min_d < best_dist:
                    best_dist = min_d
                    best_pair = (a_id, b_id)

        if best_pair is None:
            break
        a_id, b_id = best_pair
        # Merge b into a
        clusters[a_id] |= clusters[b_id]
        del clusters[b_id]

    # Assign cluster labels
    pred_labels = [0] * n_fol
    for ci, (cid, members) in enumerate(clusters.items()):
        for m in members:
            pred_labels[m] = ci

    # Compute ARI
    def ari(labels_a, labels_b, n):
        """Adjusted Rand Index."""
        ct = defaultdict(int)
        a_ct = Counter(labels_a)
        b_ct = Counter(labels_b)
        for i in range(n):
            ct[(labels_a[i], labels_b[i])] += 1

        def comb2(n):
            return n * (n - 1) / 2

        index = sum(comb2(v) for v in ct.values())
        sum_a = sum(comb2(v) for v in a_ct.values())
        sum_b = sum(comb2(v) for v in b_ct.values())
        n_comb = comb2(n)
        expected = sum_a * sum_b / n_comb if n_comb > 0 else 0
        max_idx = (sum_a + sum_b) / 2
        if max_idx == expected:
            return 0.0
        return (index - expected) / (max_idx - expected)

    # Convert section labels to integers
    sec_to_int = {s: i for i, s in enumerate(sorted(set(labels)))}
    true_int = [sec_to_int[l] for l in labels]
    ari_val = ari(true_int, pred_labels, n_fol)
    d4_pass = ari_val > 0.10
    print(f"  ARI: {ari_val:.4f} (threshold: > 0.10) -> {'PASS' if d4_pass else 'FAIL'}")

    # ═══════════════════════════════════════════════════════════
    # D5a: HEAD-only vs Full (LOO-NN)
    # ═══════════════════════════════════════════════════════════
    print("\n  === D5: Within-Domain Improvement ===")
    head_only_acc = leave_one_out_nn(z_head, qualifying_folios, labels)
    full_acc = leave_one_out_nn(z_full, qualifying_folios, labels)
    d5a_gain = full_acc - head_only_acc
    d5a_pass = d5a_gain >= 0.05
    print(f"  D5a (NN): HEAD-only={head_only_acc:.4f}, Full={full_acc:.4f}, "
          f"gain={d5a_gain:.4f} (>= 0.05) -> {'PASS' if d5a_pass else 'FAIL'}")

    # ═══════════════════════════════════════════════════════════
    # D5b: HEAD-only vs Full (Random Forest via 5-fold CV)
    # ═══════════════════════════════════════════════════════════
    print("  D5b (Random Forest)...")
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import cross_val_score
        import numpy as np

        # Build feature matrices
        X_head = np.array([z_head[f] for f in qualifying_folios])
        X_full = np.array([z_full[f] for f in qualifying_folios])
        # Replace None with 0 in full features
        X_full = np.nan_to_num(X_full, nan=0.0)
        y = np.array(true_int)

        rf_head = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
        rf_full = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)

        cv_head = cross_val_score(rf_head, X_head, y, cv=5, scoring='accuracy')
        cv_full = cross_val_score(rf_full, X_full, y, cv=5, scoring='accuracy')

        rf_head_acc = cv_head.mean()
        rf_full_acc = cv_full.mean()
        d5b_gain = rf_full_acc - rf_head_acc
        d5b_pass = d5b_gain >= 0.05

        # Feature importance
        rf_full.fit(X_full, y)
        importances = rf_full.feature_importances_
        feat_names_full = head_feat_names + _FEATURE_NAMES
        imp_order = sorted(range(len(importances)), key=lambda i: -importances[i])
        top_features = [(feat_names_full[i], round(float(importances[i]), 4))
                       for i in imp_order[:10]]

        print(f"  D5b (RF): HEAD={rf_head_acc:.4f}, Full={rf_full_acc:.4f}, "
              f"gain={d5b_gain:.4f} (>= 0.05) -> {'PASS' if d5b_pass else 'FAIL'}")
        print(f"  Top features: {top_features[:5]}")

        d5b_result = {
            'head_acc': round(float(rf_head_acc), 4),
            'full_acc': round(float(rf_full_acc), 4),
            'gain': round(float(d5b_gain), 4),
            'pass': bool(d5b_pass),
            'top_features': top_features,
        }
    except ImportError:
        print("  D5b: sklearn not available, skipping RF test")
        d5b_pass = False
        d5b_result = {'error': 'sklearn not available', 'pass': False}

    d5_pass = d5a_pass or d5b_pass

    # ═══════════════════════════════════════════════════════════
    # D6: Paragraph-Conditioned Analysis
    # ═══════════════════════════════════════════════════════════
    print("\n  === D6: Paragraph Differentiation ===")

    # D6a: Does paragraph differentiation exist within folios?
    # For folios with >= 3 paragraphs, compute domain profile per paragraph
    para_diff_results = {}
    n_sig_folios = 0
    qualifying_para_folios = []

    for f in qualifying_folios:
        # Get paragraphs
        para_tokens = defaultdict(list)
        for t in folio_tokens[f]:
            para_tokens[t['paragraph_idx']].append(t)

        if len(para_tokens) < 3:
            continue

        qualifying_para_folios.append(f)

        # Compute domain profile per paragraph (6 domain fractions)
        para_profiles = {}
        for pi, toks in para_tokens.items():
            if len(toks) < 5:
                continue
            n = len(toks)
            profile = {
                'THERMAL': sum(1 for t in toks if t['domain'] == 'THERMAL') / n,
                'FLOW': sum(1 for t in toks if t['domain'] == 'FLOW') / n,
                'ACTIVE': sum(1 for t in toks if t['domain'] == 'ACTIVE') / n,
                'STABILITY': sum(1 for t in toks if t['domain'] == 'STABILITY') / n,
                'ARRANGEMENT': sum(1 for t in toks if t['domain'] == 'ARRANGEMENT') / n,
                'HEADLESS': sum(1 for t in toks if t['domain'] == 'HEADLESS') / n,
            }
            para_profiles[pi] = profile

        if len(para_profiles) < 3:
            continue

        # Mean pairwise JSD of paragraph domain profiles
        pids = list(para_profiles.keys())
        jsds = []
        for i in range(len(pids)):
            for j in range(i + 1, len(pids)):
                d = jsd(para_profiles[pids[i]], para_profiles[pids[j]])
                jsds.append(d)
        real_jsd = sum(jsds) / len(jsds) if jsds else 0

        # Permutation null: shuffle tokens into random paragraph-sized groups
        null_jsds = []
        para_sizes = {pi: len(toks) for pi, toks in para_tokens.items()
                     if pi in para_profiles}
        all_folio_toks = folio_tokens[f]

        for seed_idx in range(N_NULL_SEEDS):
            rng = random.Random(SEED_BASE * 1000 + seed_idx)
            shuffled = list(all_folio_toks)
            rng.shuffle(shuffled)
            cursor = 0
            null_profiles = {}
            for pi, sz in para_sizes.items():
                chunk = shuffled[cursor:cursor + sz]
                cursor += sz
                if len(chunk) < 5:
                    continue
                n = len(chunk)
                null_profiles[pi] = {
                    'THERMAL': sum(1 for t in chunk if t['domain'] == 'THERMAL') / n,
                    'FLOW': sum(1 for t in chunk if t['domain'] == 'FLOW') / n,
                    'ACTIVE': sum(1 for t in chunk if t['domain'] == 'ACTIVE') / n,
                    'STABILITY': sum(1 for t in chunk if t['domain'] == 'STABILITY') / n,
                    'ARRANGEMENT': sum(1 for t in chunk if t['domain'] == 'ARRANGEMENT') / n,
                    'HEADLESS': sum(1 for t in chunk if t['domain'] == 'HEADLESS') / n,
                }
            if len(null_profiles) >= 3:
                nids = list(null_profiles.keys())
                njsds = []
                for i in range(len(nids)):
                    for j in range(i + 1, len(nids)):
                        njsds.append(jsd(null_profiles[nids[i]], null_profiles[nids[j]]))
                null_jsds.append(sum(njsds) / len(njsds))

        # Permutation p-value
        if null_jsds:
            p_val = sum(1 for nj in null_jsds if nj >= real_jsd) / len(null_jsds)
        else:
            p_val = 1.0

        if p_val < 0.05:
            n_sig_folios += 1

        para_diff_results[f] = {
            'n_paragraphs': len(para_profiles),
            'mean_jsd': round(real_jsd, 6),
            'null_mean': round(sum(null_jsds)/len(null_jsds), 6) if null_jsds else None,
            'p_value': round(p_val, 4),
            'significant': p_val < 0.05,
        }

    n_qualifying = len(qualifying_para_folios)
    d6a_frac = n_sig_folios / n_qualifying if n_qualifying > 0 else 0
    d6a_pass = d6a_frac >= 0.30
    print(f"  D6a: {n_sig_folios}/{n_qualifying} folios significant ({d6a_frac:.2%})")
    print(f"  Threshold: >= 30% -> {'PASS' if d6a_pass else 'FAIL'}")

    # D6b: Gradient alignment (exploratory)
    # Test if significant folios show C1398 gradient axes
    d6b_results = {}
    if n_sig_folios > 0:
        sig_folios = [f for f in qualifying_para_folios
                     if para_diff_results.get(f, {}).get('significant', False)]
        # For each significant folio, compute paragraph-level gradient features
        # and test Spearman correlation with paragraph rank
        gradient_sigs = 0
        for f in sig_folios[:20]:  # Limit to avoid excessive computation
            para_tokens_f = defaultdict(list)
            for t in folio_tokens[f]:
                para_tokens_f[t['paragraph_idx']].append(t)

            # Compute per-paragraph: k-frac, headless-frac, e-non-ey-frac, suffix diversity
            para_features = {}
            for pi, toks in sorted(para_tokens_f.items()):
                if len(toks) < 5:
                    continue
                n = len(toks)
                k_frac = sum(1 for t in toks if t['domain'] == 'THERMAL') / n
                hl_frac = sum(1 for t in toks if t['domain'] == 'HEADLESS') / n
                e_nonEy = sum(1 for t in toks
                             if t['domain'] == 'STABILITY' and t['frame'] != 'e->y') / n
                sfx_types = len(set(t['suffix'] for t in toks if t['suffix']))
                para_features[pi] = {
                    'k_frac': k_frac, 'hl_frac': hl_frac,
                    'e_nonEy': e_nonEy, 'sfx_diversity': sfx_types
                }

            if len(para_features) >= 3:
                # Simple Spearman: rank correlation of paragraph index with each feature
                pis = sorted(para_features.keys())
                ranks = list(range(len(pis)))
                for axis in ['k_frac', 'hl_frac', 'e_nonEy', 'sfx_diversity']:
                    vals = [para_features[p][axis] for p in pis]
                    # Rank the values
                    val_ranks = [sorted(vals).index(v) for v in vals]
                    # Spearman = Pearson of ranks
                    n_r = len(ranks)
                    if n_r < 3:
                        continue
                    mean_r = sum(ranks) / n_r
                    mean_v = sum(val_ranks) / n_r
                    cov = sum((ranks[i] - mean_r) * (val_ranks[i] - mean_v) for i in range(n_r))
                    var_r = sum((r - mean_r) ** 2 for r in ranks)
                    var_v = sum((v - mean_v) ** 2 for v in val_ranks)
                    if var_r > 0 and var_v > 0:
                        rho = cov / math.sqrt(var_r * var_v)
                        if abs(rho) > 0.7:  # strong gradient
                            gradient_sigs += 1
                            break  # one axis is enough

        d6b_pass = gradient_sigs >= 1
        d6b_results = {
            'n_tested': min(len(sig_folios), 20),
            'n_gradient_significant': gradient_sigs,
            'pass': d6b_pass,
        }
        print(f"  D6b: {gradient_sigs} folios show strong gradient alignment -> {'PASS' if d6b_pass else 'FAIL'}")
    else:
        d6b_pass = False
        d6b_results = {'n_tested': 0, 'pass': False}
        print("  D6b: No significant folios, skipped")

    # ═══════════════════════════════════════════════════════════
    # Assemble results
    # ═══════════════════════════════════════════════════════════
    # T3 pass: D1 AND D5 AND >= 2 of {D2, D3, D4}
    d_secondary = sum([d2_pass, d3_pass, d4_pass])
    t3_pass = d1_result['pass'] and d5_pass and d_secondary >= 2

    results = {
        'metadata': {
            'phase': '560',
            'task': 'T3_cross_folio_discriminability',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_qualifying_folios': len(qualifying_folios),
            'n_features': len(_FEATURE_NAMES),
            'n_null_seeds': N_NULL_SEEDS,
        },
        'D1': d1_result,
        'D2': {
            'n_significant': n_sig,
            'threshold': 10,
            'pass': d2_pass,
            'per_feature': d2_results,
        },
        'D3': {
            'results': d3_results,
            'n_pass': d3_pass_count,
            'threshold': 2,
            'pass': d3_pass,
        },
        'D4': {
            'ari': round(ari_val, 4),
            'threshold': 0.10,
            'pass': d4_pass,
        },
        'D5': {
            'D5a': {
                'head_only_acc': round(head_only_acc, 4),
                'full_acc': round(full_acc, 4),
                'gain_pp': round(d5a_gain, 4),
                'pass': d5a_pass,
            },
            'D5b': d5b_result,
            'pass': d5_pass,
        },
        'D6': {
            'D6a': {
                'n_qualifying': n_qualifying,
                'n_significant': n_sig_folios,
                'fraction': round(d6a_frac, 4),
                'threshold': 0.30,
                'pass': d6a_pass,
                'per_folio': {k: v for k, v in list(para_diff_results.items())[:20]},
            },
            'D6b': d6b_results,
        },
        'folio_features': {f: folio_features[f] for f in qualifying_folios[:5]},
        'verdict': {
            'D1': d1_result['pass'],
            'D2': d2_pass,
            'D3': d3_pass,
            'D4': d4_pass,
            'D5': d5_pass,
            'D6a': d6a_pass,
            'D6b': d6b_pass,
            't3_pass': t3_pass,
        },
    }

    elapsed = time.time() - t0
    print(f"\n  === T3 VERDICT: {'PASS' if t3_pass else 'FAIL'} ===")
    print(f"  D1={d1_result['pass']}, D2={d2_pass}, D3={d3_pass}, D4={d4_pass}, D5={d5_pass}")
    print(f"  D6a={d6a_pass}, D6b={d6b_pass}")
    print(f"  Elapsed: {elapsed:.1f}s")

    out_path = RESULTS_DIR / 't3_cross_folio_discriminability.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=1)
    print(f"  Output: {out_path} ({os.path.getsize(out_path)/1024:.0f} KB)")
    print(f"\n=== T3 Complete ===")


if __name__ == '__main__':
    main()
