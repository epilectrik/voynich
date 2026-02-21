#!/usr/bin/env python3
"""
Phase 418: LINK_FUNCTIONAL_ARCHITECTURE
========================================
Characterizes LINK tokens (13.2% of B, 3,047 tokens, 801 types) as the last
major uncharacterized token population. LINK = 'ol' in word (C609).

5-test battery:
  T1: LINK_VOCABULARY_STRATIFICATION (role × ol_position cross-tabulation)
  T2: LINK_CROSS_ROLE_CONSISTENCY (LINK vs non-LINK within each role)
  T3: LINK_SECTION_DECOMPOSITION (BIO 2× density decomposition)
  T4: LINK_MACRO_AUTOMATON_DYNAMICS (state occupancy, boundary enrichment)
  T5: LINK_BOUNDARY_ARCHITECTURE (zone enrichment, divergence correlation)

Depends on: C609, C805, C808, C804, C806, C1168, C334
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats as scipy_stats

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ─────────────────────────────────────────────────────

N_CLASSES = 49
N_STATES = 6
MIN_ZONE_TRANS = 10

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}
STATE_ORDER = ['AXM', 'AXm', 'FQ', 'CC', 'FL_HAZ', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}
CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state

MAJOR_ROLES = ['AUXILIARY', 'ENERGY_OPERATOR', 'CORE_CONTROL', 'UN']
OL_POSITIONS = ['MIDDLE', 'PREFIX', 'SUFFIX', 'SPAN']
ALL_ROLES = ['AUXILIARY', 'ENERGY_OPERATOR', 'CORE_CONTROL', 'FREQUENT_OPERATOR', 'FLOW_OPERATOR', 'UN']


# ── Pure-Python Statistics ────────────────────────────────────────

def round_floats(obj, digits=6):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def spearman_r(x, y):
    n = len(x)
    if n < 3:
        return 0.0, 1.0
    def _rank(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j]] == vals[indexed[j + 1]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx]] = avg_rank
            i = j + 1
        return ranks
    rx = _rank(list(x))
    ry = _rank(list(y))
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    sd_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    sd_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if sd_x == 0 or sd_y == 0:
        return 0.0, 1.0
    rho = cov / (sd_x * sd_y)
    rho = max(-1.0, min(1.0, rho))
    t_stat = rho * math.sqrt((n - 2) / (1 - rho ** 2 + 1e-12))
    df = n - 2
    x_val = df / (df + t_stat ** 2)
    p = 1.0 - _betainc(df / 2.0, 0.5, x_val)
    return rho, p


def _betainc(a, b, x, n_iter=200):
    if x <= 0: return 1.0
    if x >= 1: return 0.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) / a
    f, c, d = 1.0, 1.0, 0.0
    for m in range(n_iter):
        if m == 0:
            num = 1.0
        elif m % 2 == 0:
            k = m // 2
            num = (k * (b - k) * x) / ((a + 2*k - 1) * (a + 2*k))
        else:
            k = (m + 1) // 2
            num = -((a + k) * (a + b + k) * x) / ((a + 2*k) * (a + 2*k + 1))
        d = 1.0 + num * d
        if abs(d) < 1e-30: d = 1e-30
        d = 1.0 / d
        c = 1.0 + num / c
        if abs(c) < 1e-30: c = 1e-30
        delta = c * d
        f *= delta
        if abs(delta - 1.0) < 1e-10: break
    return 1.0 - front * f


def shannon_entropy(probs):
    return -sum(p * math.log2(p) for p in probs if p > 0)


def compute_jsd(p, q, epsilon=1e-10):
    p = np.array(p, dtype=float) + epsilon
    q = np.array(q, dtype=float) + epsilon
    p = p / p.sum()
    q = q / q.sum()
    m_arr = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log2(p / m_arr)) + 0.5 * np.sum(q * np.log2(q / m_arr)))


def cramers_v(chi2, n, min_dim):
    if n <= 0 or min_dim <= 1:
        return 0.0
    return math.sqrt(chi2 / (n * (min_dim - 1)))


def build_zone_matrix(transitions):
    m = np.zeros((N_CLASSES, N_CLASSES))
    for src, tgt in transitions:
        m[src - 1, tgt - 1] += 1
    return m


def matrix_to_6state(m49):
    m6 = np.zeros((N_STATES, N_STATES))
    for src_cls in range(1, N_CLASSES + 1):
        si = STATE_IDX[CLASS_TO_STATE[src_cls]]
        for tgt_cls in range(1, N_CLASSES + 1):
            ti = STATE_IDX[CLASS_TO_STATE[tgt_cls]]
            m6[si, ti] += m49[src_cls - 1, tgt_cls - 1]
    return m6


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.bool_): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)


# ── ol_position Computation ──────────────────────────────────────

def compute_ol_position(word, m):
    """Determine where 'ol' falls in the morphological decomposition."""
    ol_idx = word.find('ol')
    if ol_idx < 0:
        return None

    art_len = len(m.articulator) if m.articulator else 0
    prefix_len = (len(m.prefix) if m.prefix else 0) + art_len
    middle_start = prefix_len
    middle_end = middle_start + (len(m.middle) if m.middle else 0)

    if ol_idx >= middle_start and ol_idx + 2 <= middle_end:
        return 'MIDDLE'
    elif ol_idx + 2 <= middle_start:
        return 'PREFIX'
    elif ol_idx >= middle_end:
        return 'SUFFIX'
    else:
        return 'SPAN'


# ── Data Loading ──────────────────────────────────────────────────

def load_data():
    print("Loading data...")

    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' /
              'class_token_map.json', encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = cmap['token_to_class']
    class_to_role = cmap['class_to_role']

    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_data = axm_data['folio_data']

    morph = Morphology()

    # Single transcript pass
    all_tokens = []
    folio_lines = defaultdict(lambda: defaultdict(list))

    for t in Transcript().currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue

        cls = token_to_class.get(w)
        role = class_to_role.get(str(cls), 'UN') if cls else 'UN'
        state = CLASS_TO_STATE.get(cls) if cls else None

        m = morph.extract(w)
        is_link = 'ol' in w
        ol_pos = compute_ol_position(w, m) if is_link else None

        tok = {
            'word': w,
            'folio': t.folio,
            'line': t.line,
            'cls': cls,
            'state': state,
            'role': role,
            'is_link': is_link,
            'prefix': m.prefix if m else None,
            'middle': m.middle if m else None,
            'suffix': m.suffix if m else None,
            'ol_position': ol_pos,
        }
        all_tokens.append(tok)
        folio_lines[t.folio][t.line].append(tok)

    # Build folio line lists (ordered)
    folio_line_lists = defaultdict(list)
    for folio in sorted(folio_lines.keys()):
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            if len(tokens) >= 2:
                folio_line_lists[folio].append(tokens)

    # Pre-compute groupings
    link_tokens = [t for t in all_tokens if t['is_link']]
    nonlink_tokens = [t for t in all_tokens if not t['is_link']]

    # Per-folio section mapping
    folio_section = {}
    for folio in folio_line_lists:
        if folio in folio_data:
            folio_section[folio] = folio_data[folio]['section']

    # Per-token section (from folio)
    for tok in all_tokens:
        tok['section'] = folio_section.get(tok['folio'], 'UNKNOWN')

    print(f"  Total tokens: {len(all_tokens)}")
    print(f"  LINK tokens: {len(link_tokens)} ({100*len(link_tokens)/len(all_tokens):.1f}%)")
    print(f"  Non-LINK tokens: {len(nonlink_tokens)}")
    print(f"  Folios with lines: {len(folio_line_lists)}")

    return all_tokens, link_tokens, nonlink_tokens, folio_line_lists, folio_data, folio_section


# ── Test 1: LINK_VOCABULARY_STRATIFICATION ────────────────────────

def test1_vocabulary_stratification(link_tokens, all_tokens):
    print("\n── Test 1: LINK_VOCABULARY_STRATIFICATION ──")

    # 1a. Basic census
    type_counts = Counter(t['word'] for t in link_tokens)
    n_types = len(type_counts)
    n_tokens = len(link_tokens)
    hapax = sum(1 for c in type_counts.values() if c == 1)
    hapax_frac = hapax / n_types if n_types > 0 else 0

    top_20 = type_counts.most_common(20)
    print(f"  Types: {n_types}, Tokens: {n_tokens}")
    print(f"  Hapax legomena: {hapax} ({100*hapax_frac:.1f}%)")
    print(f"  Top 10: {[(w, c) for w, c in top_20[:10]]}")

    # 1b. Cross-tabulation: role × ol_position
    contingency = defaultdict(lambda: defaultdict(int))
    for t in link_tokens:
        role = t['role']
        ol_pos = t['ol_position'] or 'UNKNOWN'
        contingency[role][ol_pos] += 1

    # Build matrix for chi-square
    roles_present = sorted(set(t['role'] for t in link_tokens))
    positions_present = sorted(set(t['ol_position'] for t in link_tokens if t['ol_position']))

    print(f"\n  Cross-tabulation (role × ol_position):")
    header = f"  {'':20s}" + "".join(f"{p:>10s}" for p in positions_present) + f"{'TOTAL':>10s}"
    print(header)
    ct_matrix = []
    for role in roles_present:
        row = [contingency[role].get(p, 0) for p in positions_present]
        ct_matrix.append(row)
        total = sum(row)
        print(f"  {role:20s}" + "".join(f"{c:>10d}" for c in row) + f"{total:>10d}")

    ct_array = np.array(ct_matrix)
    # Remove rows/cols with all zeros
    row_sums = ct_array.sum(axis=1)
    col_sums = ct_array.sum(axis=0)
    valid_rows = row_sums > 0
    valid_cols = col_sums > 0
    ct_filtered = ct_array[valid_rows][:, valid_cols]

    if ct_filtered.shape[0] >= 2 and ct_filtered.shape[1] >= 2:
        chi2, p_chi2, dof, _ = scipy_stats.chi2_contingency(ct_filtered)
        min_dim = min(ct_filtered.shape)
        v = cramers_v(chi2, ct_filtered.sum(), min_dim)
        print(f"\n  Chi-square: chi2={chi2:.1f}, p={p_chi2:.2e}, dof={dof}, Cramér's V={v:.4f}")
    else:
        chi2, p_chi2, v = 0, 1, 0
        print(f"\n  Chi-square: insufficient dimensions")

    # 1c. Per-role diversity
    role_diversity = {}
    for role in roles_present:
        role_tokens = [t for t in link_tokens if t['role'] == role]
        role_types = Counter(t['word'] for t in role_tokens)
        n_rt = len(role_types)
        n_rtok = len(role_tokens)
        probs = [c / n_rtok for c in role_types.values()]
        ent = shannon_entropy(probs)
        ttr = n_rt / n_rtok if n_rtok > 0 else 0
        role_diversity[role] = {
            'n_types': n_rt, 'n_tokens': n_rtok,
            'entropy': float(ent), 'type_token_ratio': float(ttr),
        }
        print(f"  {role:20s}: types={n_rt}, tokens={n_rtok}, entropy={ent:.2f}, TTR={ttr:.3f}")

    # 1d. Top types with role and ol_position
    top_detail = []
    for word, count in top_20:
        # Find most common role and ol_position for this type
        type_tokens = [t for t in link_tokens if t['word'] == word]
        role_mode = Counter(t['role'] for t in type_tokens).most_common(1)[0][0]
        ol_mode = Counter(t['ol_position'] for t in type_tokens if t['ol_position']).most_common(1)[0][0]
        top_detail.append({'word': word, 'count': count, 'role': role_mode, 'ol_position': ol_mode})

    # Verdict
    if p_chi2 < 0.05 and v > 0.15:
        verdict = 'STRATIFIED'
    elif p_chi2 < 0.05:
        verdict = 'WEAKLY_STRATIFIED'
    else:
        verdict = 'HOMOGENEOUS'
    print(f"  Verdict: {verdict}")

    return {
        'n_types': n_types,
        'n_tokens': n_tokens,
        'hapax_count': hapax,
        'hapax_fraction': hapax_frac,
        'top_20': top_detail,
        'cross_tabulation': {role: dict(contingency[role]) for role in roles_present},
        'chi2': float(chi2),
        'chi2_p': float(p_chi2),
        'cramers_v': float(v),
        'per_role_diversity': role_diversity,
        'verdict': verdict,
    }


# ── Test 2: LINK_CROSS_ROLE_CONSISTENCY ──────────────────────────

def test2_cross_role_consistency(all_tokens, folio_line_lists):
    print("\n── Test 2: LINK_CROSS_ROLE_CONSISTENCY ──")

    # 2a. Positional comparison: LINK vs non-LINK within each role
    # Compute normalized line position for each token
    token_positions = []
    for folio in folio_line_lists:
        for tokens in folio_line_lists[folio]:
            n = len(tokens)
            for i, tok in enumerate(tokens):
                tok['norm_pos'] = i / (n - 1) if n > 1 else 0.5
                token_positions.append(tok)

    role_results = {}
    for role in MAJOR_ROLES:
        link_in_role = [t for t in token_positions if t['role'] == role and t['is_link']]
        nonlink_in_role = [t for t in token_positions if t['role'] == role and not t['is_link']]

        if len(link_in_role) < 30 or len(nonlink_in_role) < 30:
            print(f"  {role}: link={len(link_in_role)}, nonlink={len(nonlink_in_role)} (skipping)")
            continue

        link_pos = [t['norm_pos'] for t in link_in_role]
        nonlink_pos = [t['norm_pos'] for t in nonlink_in_role]

        u_stat, u_p = scipy_stats.mannwhitneyu(link_pos, nonlink_pos, alternative='two-sided')
        link_mean = np.mean(link_pos)
        nonlink_mean = np.mean(nonlink_pos)

        # Boundary rates
        link_first = sum(1 for t in link_in_role if t['norm_pos'] == 0) / len(link_in_role)
        nonlink_first = sum(1 for t in nonlink_in_role if t['norm_pos'] == 0) / len(nonlink_in_role)
        link_last = sum(1 for t in link_in_role if t['norm_pos'] == 1.0) / len(link_in_role)
        nonlink_last = sum(1 for t in nonlink_in_role if t['norm_pos'] == 1.0) / len(nonlink_in_role)

        print(f"  {role:20s}: link_pos={link_mean:.3f} vs nonlink={nonlink_mean:.3f}, MW p={u_p:.4f}")
        print(f"    first: link={link_first:.3f} nonlink={nonlink_first:.3f} | last: link={link_last:.3f} nonlink={nonlink_last:.3f}")

        role_results[role] = {
            'n_link': len(link_in_role),
            'n_nonlink': len(nonlink_in_role),
            'link_mean_pos': float(link_mean),
            'nonlink_mean_pos': float(nonlink_mean),
            'mw_u': float(u_stat),
            'mw_p': float(u_p),
            'link_first_rate': float(link_first),
            'nonlink_first_rate': float(nonlink_first),
            'link_last_rate': float(link_last),
            'nonlink_last_rate': float(nonlink_last),
        }

    # 2b. Cross-role LINK positional consistency
    # JSD of positional distributions (5-bin histograms) across roles
    role_pos_dists = {}
    for role in MAJOR_ROLES:
        link_in_role = [t['norm_pos'] for t in token_positions if t['role'] == role and t['is_link']]
        if len(link_in_role) >= 30:
            hist, _ = np.histogram(link_in_role, bins=5, range=(0, 1))
            role_pos_dists[role] = hist.astype(float)

    pairwise_jsd = {}
    roles_with_dist = list(role_pos_dists.keys())
    for i in range(len(roles_with_dist)):
        for j in range(i + 1, len(roles_with_dist)):
            r1, r2 = roles_with_dist[i], roles_with_dist[j]
            jsd = compute_jsd(role_pos_dists[r1], role_pos_dists[r2])
            pairwise_jsd[f"{r1}_vs_{r2}"] = jsd
            print(f"  LINK position JSD {r1} vs {r2}: {jsd:.4f}")

    mean_link_jsd = np.mean(list(pairwise_jsd.values())) if pairwise_jsd else 0

    # Same for non-LINK
    nonlink_pos_dists = {}
    for role in MAJOR_ROLES:
        nonlink_in_role = [t['norm_pos'] for t in token_positions if t['role'] == role and not t['is_link']]
        if len(nonlink_in_role) >= 30:
            hist, _ = np.histogram(nonlink_in_role, bins=5, range=(0, 1))
            nonlink_pos_dists[role] = hist.astype(float)

    nonlink_pairwise_jsd = {}
    roles_nl = list(nonlink_pos_dists.keys())
    for i in range(len(roles_nl)):
        for j in range(i + 1, len(roles_nl)):
            r1, r2 = roles_nl[i], roles_nl[j]
            jsd = compute_jsd(nonlink_pos_dists[r1], nonlink_pos_dists[r2])
            nonlink_pairwise_jsd[f"{r1}_vs_{r2}"] = jsd

    mean_nonlink_jsd = np.mean(list(nonlink_pairwise_jsd.values())) if nonlink_pairwise_jsd else 0
    print(f"\n  Mean cross-role JSD: LINK={mean_link_jsd:.4f}, non-LINK={mean_nonlink_jsd:.4f}")

    # 2c. Predecessor state comparison (LINK vs non-LINK within role)
    pred_jsd_by_role = {}
    for role in MAJOR_ROLES:
        if role not in role_results:
            continue
        link_preds = []
        nonlink_preds = []
        for folio in folio_line_lists:
            for tokens in folio_line_lists[folio]:
                for i in range(1, len(tokens)):
                    if tokens[i - 1]['state'] is not None:
                        pred_state = tokens[i - 1]['state']
                        if tokens[i]['role'] == role:
                            if tokens[i]['is_link']:
                                link_preds.append(pred_state)
                            else:
                                nonlink_preds.append(pred_state)

        if len(link_preds) >= 30 and len(nonlink_preds) >= 30:
            link_dist = np.zeros(N_STATES)
            nonlink_dist = np.zeros(N_STATES)
            for s in link_preds:
                link_dist[STATE_IDX[s]] += 1
            for s in nonlink_preds:
                nonlink_dist[STATE_IDX[s]] += 1
            jsd = compute_jsd(link_dist, nonlink_dist)
            pred_jsd_by_role[role] = jsd
            print(f"  Predecessor JSD (LINK vs non-LINK) in {role}: {jsd:.4f}")

    # Verdict
    n_consistent = sum(1 for r in role_results.values() if r['mw_p'] > 0.05)
    n_tested = len(role_results)
    if mean_link_jsd < mean_nonlink_jsd and n_consistent >= n_tested // 2:
        verdict = 'CROSS_ROLE_SUBSTRATE'
    elif n_consistent < n_tested // 2:
        verdict = 'ROLE_DOMINANT'
    else:
        verdict = 'MIXED'
    print(f"  Consistent (p>0.05): {n_consistent}/{n_tested}")
    print(f"  Verdict: {verdict}")

    return {
        'per_role_comparison': role_results,
        'link_pairwise_jsd': pairwise_jsd,
        'nonlink_pairwise_jsd': nonlink_pairwise_jsd,
        'mean_link_jsd': float(mean_link_jsd),
        'mean_nonlink_jsd': float(mean_nonlink_jsd),
        'predecessor_jsd_by_role': pred_jsd_by_role,
        'verdict': verdict,
    }


# ── Test 3: LINK_SECTION_DECOMPOSITION ───────────────────────────

def test3_section_decomposition(all_tokens, link_tokens):
    print("\n── Test 3: LINK_SECTION_DECOMPOSITION ──")

    # 3a. Per-section density
    section_total = Counter(t['section'] for t in all_tokens)
    section_link = Counter(t['section'] for t in link_tokens)
    sections = sorted(set(t['section'] for t in all_tokens if t['section'] != 'UNKNOWN'))

    section_densities = {}
    for sec in sections:
        total = section_total[sec]
        link_count = section_link.get(sec, 0)
        density = link_count / total if total > 0 else 0
        section_densities[sec] = {'n_total': total, 'n_link': link_count, 'density': density}
        print(f"  Section {sec}: {link_count}/{total} = {100*density:.1f}%")

    # 3b. Per-section role mix
    section_role_dist = {}
    for sec in sections:
        sec_link = [t for t in link_tokens if t['section'] == sec]
        if len(sec_link) < 10:
            continue
        role_counts = Counter(t['role'] for t in sec_link)
        total = sum(role_counts.values())
        role_fracs = {r: role_counts.get(r, 0) / total for r in ALL_ROLES}
        section_role_dist[sec] = role_fracs

    # Chi-square on section × role contingency
    sec_list = sorted(section_role_dist.keys())
    if len(sec_list) >= 2:
        ct_sr = []
        for sec in sec_list:
            row = [int(section_role_dist[sec].get(r, 0) * section_densities[sec]['n_link'])
                   for r in ALL_ROLES]
            ct_sr.append(row)
        ct_sr = np.array(ct_sr)
        # Remove zero columns
        col_sums = ct_sr.sum(axis=0)
        valid_cols = col_sums > 0
        ct_sr_f = ct_sr[:, valid_cols]
        if ct_sr_f.shape[0] >= 2 and ct_sr_f.shape[1] >= 2:
            chi2_sr, p_sr, dof_sr, _ = scipy_stats.chi2_contingency(ct_sr_f)
            print(f"\n  Section × role chi-square: chi2={chi2_sr:.1f}, p={p_sr:.2e}")
        else:
            chi2_sr, p_sr = 0, 1
    else:
        chi2_sr, p_sr = 0, 1

    # 3c. Pairwise JSD of role distributions
    section_jsd = {}
    for i in range(len(sec_list)):
        for j in range(i + 1, len(sec_list)):
            s1, s2 = sec_list[i], sec_list[j]
            d1 = [section_role_dist[s1].get(r, 0) for r in ALL_ROLES]
            d2 = [section_role_dist[s2].get(r, 0) for r in ALL_ROLES]
            jsd = compute_jsd(d1, d2)
            section_jsd[f"{s1}_vs_{s2}"] = jsd

    # 3d. BIO decomposition
    bio_sec = 'B'
    non_bio_link = [t for t in link_tokens if t['section'] != bio_sec and t['section'] != 'UNKNOWN']
    bio_link = [t for t in link_tokens if t['section'] == bio_sec]

    if len(bio_link) >= 10 and len(non_bio_link) >= 10:
        # Per role × ol_position: BIO enrichment
        bio_enrichment = {}
        for role in ALL_ROLES:
            for ol_pos in OL_POSITIONS:
                bio_count = sum(1 for t in bio_link if t['role'] == role and t['ol_position'] == ol_pos)
                non_bio_count = sum(1 for t in non_bio_link if t['role'] == role and t['ol_position'] == ol_pos)
                bio_total = len(bio_link)
                non_bio_total = len(non_bio_link)
                bio_rate = bio_count / bio_total if bio_total > 0 else 0
                non_bio_rate = non_bio_count / non_bio_total if non_bio_total > 0 else 0
                enrichment = bio_rate / non_bio_rate if non_bio_rate > 0 else 0
                if bio_count >= 5 or non_bio_count >= 5:
                    bio_enrichment[f"{role}_{ol_pos}"] = {
                        'bio_count': bio_count, 'non_bio_count': non_bio_count,
                        'bio_rate': bio_rate, 'non_bio_rate': non_bio_rate,
                        'enrichment': enrichment,
                    }

        # Top enriched cells
        sorted_enrich = sorted(bio_enrichment.items(), key=lambda x: x[1]['enrichment'], reverse=True)
        print(f"\n  BIO enrichment (top 5 cells):")
        for cell, data in sorted_enrich[:5]:
            print(f"    {cell:30s} enrich={data['enrichment']:.2f} (bio={data['bio_count']}, non-bio={data['non_bio_count']})")

        # Is enrichment uniform or targeted?
        enrichments = [d['enrichment'] for _, d in sorted_enrich if d['enrichment'] > 0]
        if enrichments:
            enrich_cv = np.std(enrichments) / np.mean(enrichments) if np.mean(enrichments) > 0 else 0
            print(f"  Enrichment CV: {enrich_cv:.3f}")
        else:
            enrich_cv = 0
    else:
        bio_enrichment = {}
        enrich_cv = 0

    # Verdict
    composition_shifted = p_sr < 0.05
    if composition_shifted:
        if enrich_cv > 0.5:
            verdict = 'BIO_TARGETED_ENRICHMENT'
        else:
            verdict = 'SECTION_COMPOSITION_SHIFT'
    else:
        verdict = 'BIO_UNIFORM_ENRICHMENT'
    print(f"  Verdict: {verdict}")

    return {
        'section_densities': {s: section_densities[s] for s in sections if s in section_densities},
        'section_role_distributions': section_role_dist,
        'section_role_chi2': float(chi2_sr),
        'section_role_p': float(p_sr),
        'section_role_jsd': section_jsd,
        'bio_enrichment': bio_enrichment,
        'enrichment_cv': float(enrich_cv),
        'verdict': verdict,
    }


# ── Test 4: LINK_MACRO_AUTOMATON_DYNAMICS ─────────────────────────

def test4_macro_automaton_dynamics(folio_line_lists):
    print("\n── Test 4: LINK_MACRO_AUTOMATON_DYNAMICS ──")

    # Collect classified LINK and non-LINK tokens with state info
    link_states = []
    nonlink_states = []
    link_incoming = []  # (predecessor_state, link_state)
    link_outgoing = []  # (link_state, successor_state)
    nonlink_transitions = []  # all non-LINK transitions
    link_at_boundary = 0
    link_total_with_context = 0
    nonlink_at_boundary = 0
    nonlink_total_with_context = 0

    # UN-LINK neighborhood
    un_link_pred_states = []
    un_link_succ_states = []

    # Class 11 vs class 29
    class11_positions = []
    class29_positions = []
    class11_preds = []
    class29_preds = []
    class11_succs = []
    class29_succs = []

    for folio in folio_line_lists:
        for tokens in folio_line_lists[folio]:
            n = len(tokens)
            for i, tok in enumerate(tokens):
                if tok['state'] is not None:
                    if tok['is_link']:
                        link_states.append(tok['state'])
                    else:
                        nonlink_states.append(tok['state'])

                # Transitions involving LINK
                if i > 0 and tokens[i - 1]['state'] is not None and tok['state'] is not None:
                    if tok['is_link'] and tok['state'] is not None:
                        link_incoming.append((tokens[i - 1]['state'], tok['state']))
                    elif not tok['is_link']:
                        nonlink_transitions.append((tokens[i - 1]['state'], tok['state']))

                if i < n - 1 and tok['state'] is not None and tokens[i + 1]['state'] is not None:
                    if tok['is_link'] and tok['state'] is not None:
                        link_outgoing.append((tok['state'], tokens[i + 1]['state']))

                # State boundary enrichment
                if i > 0 and tokens[i - 1]['state'] is not None and tok['state'] is not None:
                    is_boundary = tokens[i - 1]['state'] != tok['state']
                    if tok['is_link'] and tok['state'] is not None:
                        link_total_with_context += 1
                        if is_boundary:
                            link_at_boundary += 1
                    elif not tok['is_link']:
                        nonlink_total_with_context += 1
                        if is_boundary:
                            nonlink_at_boundary += 1

                # UN-LINK neighborhoods
                if tok['is_link'] and tok['cls'] is None:
                    if i > 0 and tokens[i - 1]['state'] is not None:
                        un_link_pred_states.append(tokens[i - 1]['state'])
                    if i < n - 1 and tokens[i + 1]['state'] is not None:
                        un_link_succ_states.append(tokens[i + 1]['state'])

                # Class 11 vs 29
                if tok['is_link'] and tok['cls'] is not None:
                    pos = i / (n - 1) if n > 1 else 0.5
                    if tok['cls'] == 11:
                        class11_positions.append(pos)
                        if i > 0 and tokens[i - 1]['state'] is not None:
                            class11_preds.append(tokens[i - 1]['state'])
                        if i < n - 1 and tokens[i + 1]['state'] is not None:
                            class11_succs.append(tokens[i + 1]['state'])
                    elif tok['cls'] == 29:
                        class29_positions.append(pos)
                        if i > 0 and tokens[i - 1]['state'] is not None:
                            class29_preds.append(tokens[i - 1]['state'])
                        if i < n - 1 and tokens[i + 1]['state'] is not None:
                            class29_succs.append(tokens[i + 1]['state'])

    # 4a. State occupancy
    link_state_dist = np.zeros(N_STATES)
    for s in link_states:
        link_state_dist[STATE_IDX[s]] += 1
    link_state_fracs = link_state_dist / link_state_dist.sum() if link_state_dist.sum() > 0 else link_state_dist

    nonlink_state_dist = np.zeros(N_STATES)
    for s in nonlink_states:
        nonlink_state_dist[STATE_IDX[s]] += 1
    nonlink_state_fracs = nonlink_state_dist / nonlink_state_dist.sum() if nonlink_state_dist.sum() > 0 else nonlink_state_dist

    print(f"  Classified LINK tokens: {int(link_state_dist.sum())}")
    print(f"  State occupancy (LINK vs baseline):")
    for si, state in enumerate(STATE_ORDER):
        print(f"    {state:10s}: LINK={link_state_fracs[si]:.3f}, baseline={nonlink_state_fracs[si]:.3f}")

    occupancy_jsd = compute_jsd(link_state_fracs, nonlink_state_fracs)
    print(f"  Occupancy JSD: {occupancy_jsd:.4f}")

    # 4b. Incoming/outgoing JSD
    link_in_matrix = np.zeros((N_STATES, N_STATES))
    for pred_s, link_s in link_incoming:
        link_in_matrix[STATE_IDX[pred_s], STATE_IDX[link_s]] += 1

    link_out_matrix = np.zeros((N_STATES, N_STATES))
    for link_s, succ_s in link_outgoing:
        link_out_matrix[STATE_IDX[link_s], STATE_IDX[succ_s]] += 1

    nonlink_matrix = np.zeros((N_STATES, N_STATES))
    for pred_s, succ_s in nonlink_transitions:
        nonlink_matrix[STATE_IDX[pred_s], STATE_IDX[succ_s]] += 1

    incoming_jsd = compute_jsd(link_in_matrix.flatten(), nonlink_matrix.flatten())
    outgoing_jsd = compute_jsd(link_out_matrix.flatten(), nonlink_matrix.flatten())
    print(f"  Incoming transition JSD (LINK vs baseline): {incoming_jsd:.4f}")
    print(f"  Outgoing transition JSD (LINK vs baseline): {outgoing_jsd:.4f}")

    # 4c. State boundary enrichment
    link_boundary_rate = link_at_boundary / link_total_with_context if link_total_with_context > 0 else 0
    nonlink_boundary_rate = nonlink_at_boundary / nonlink_total_with_context if nonlink_total_with_context > 0 else 0
    boundary_enrichment = link_boundary_rate / nonlink_boundary_rate if nonlink_boundary_rate > 0 else 0
    print(f"  State boundary rate: LINK={link_boundary_rate:.3f}, baseline={nonlink_boundary_rate:.3f}, enrichment={boundary_enrichment:.2f}x")

    # 4d. UN-LINK neighborhoods
    un_pred_dist = np.zeros(N_STATES)
    for s in un_link_pred_states:
        un_pred_dist[STATE_IDX[s]] += 1
    un_succ_dist = np.zeros(N_STATES)
    for s in un_link_succ_states:
        un_succ_dist[STATE_IDX[s]] += 1

    # Compare to classified LINK predecessor dist
    cl_pred_dist = np.zeros(N_STATES)
    for pred_s, _ in link_incoming:
        cl_pred_dist[STATE_IDX[pred_s]] += 1

    if un_pred_dist.sum() > 0 and cl_pred_dist.sum() > 0:
        un_vs_cl_jsd = compute_jsd(un_pred_dist, cl_pred_dist)
        print(f"  UN-LINK predecessor JSD vs classified-LINK: {un_vs_cl_jsd:.4f}")
    else:
        un_vs_cl_jsd = 0

    # 4e. Class 11 vs 29
    c11_n = len(class11_positions)
    c29_n = len(class29_positions)
    print(f"\n  Class 11 (ol→CC): n={c11_n}, mean_pos={np.mean(class11_positions):.3f}" if c11_n > 0 else "  Class 11: n=0")
    print(f"  Class 29 (LINK→AXM): n={c29_n}, mean_pos={np.mean(class29_positions):.3f}" if c29_n > 0 else "  Class 29: n=0")

    if c11_n >= 10 and c29_n >= 10:
        u_11_29, p_11_29 = scipy_stats.mannwhitneyu(class11_positions, class29_positions, alternative='two-sided')
        print(f"  Class 11 vs 29 position MW: U={u_11_29:.0f}, p={p_11_29:.4f}")

        # Predecessor JSD
        c11_pred = np.zeros(N_STATES)
        for s in class11_preds:
            c11_pred[STATE_IDX[s]] += 1
        c29_pred = np.zeros(N_STATES)
        for s in class29_preds:
            c29_pred[STATE_IDX[s]] += 1
        c11_29_jsd = compute_jsd(c11_pred, c29_pred) if c11_pred.sum() > 0 and c29_pred.sum() > 0 else 0
        print(f"  Class 11 vs 29 predecessor JSD: {c11_29_jsd:.4f}")
    else:
        u_11_29, p_11_29, c11_29_jsd = 0, 1, 0

    # Verdict
    if occupancy_jsd > 0.05 and boundary_enrichment > 1.2:
        verdict = 'LINK_MODULATES_DYNAMICS'
    elif max(link_state_fracs) > 0.70:
        verdict = 'LINK_STATE_SPECIALIZED'
    else:
        verdict = 'LINK_PASSIVE_PARTICIPANT'
    print(f"  Verdict: {verdict}")

    return {
        'n_classified_link': int(link_state_dist.sum()),
        'link_state_distribution': {STATE_ORDER[i]: float(link_state_fracs[i]) for i in range(N_STATES)},
        'baseline_state_distribution': {STATE_ORDER[i]: float(nonlink_state_fracs[i]) for i in range(N_STATES)},
        'occupancy_jsd': float(occupancy_jsd),
        'incoming_transition_jsd': float(incoming_jsd),
        'outgoing_transition_jsd': float(outgoing_jsd),
        'state_boundary_enrichment': {
            'link_rate': float(link_boundary_rate),
            'baseline_rate': float(nonlink_boundary_rate),
            'enrichment_ratio': float(boundary_enrichment),
        },
        'un_link_neighborhood': {
            'n_pred': int(un_pred_dist.sum()),
            'n_succ': int(un_succ_dist.sum()),
            'jsd_vs_classified': float(un_vs_cl_jsd),
        },
        'class11_vs_class29': {
            'class11_n': c11_n,
            'class29_n': c29_n,
            'class11_mean_pos': float(np.mean(class11_positions)) if c11_n > 0 else None,
            'class29_mean_pos': float(np.mean(class29_positions)) if c29_n > 0 else None,
            'position_mw_p': float(p_11_29),
            'predecessor_jsd': float(c11_29_jsd),
        },
        'verdict': verdict,
    }


# ── Test 5: LINK_BOUNDARY_ARCHITECTURE ───────────────────────────

def test5_boundary_architecture(folio_line_lists, folio_data):
    print("\n── Test 5: LINK_BOUNDARY_ARCHITECTURE ──")

    # 5a. Corpus-wide zone enrichment
    zone_link = Counter()
    zone_total = Counter()

    for folio in folio_line_lists:
        for tokens in folio_line_lists[folio]:
            n = len(tokens)
            for i, tok in enumerate(tokens):
                if i == 0:
                    zone = 'ENTRY'
                elif i == n - 1:
                    zone = 'EXIT'
                else:
                    zone = 'INTERIOR'
                zone_total[zone] += 1
                if tok['is_link']:
                    zone_link[zone] += 1

    print(f"  Zone LINK rates:")
    for zone in ['ENTRY', 'INTERIOR', 'EXIT']:
        rate = zone_link[zone] / zone_total[zone] if zone_total[zone] > 0 else 0
        print(f"    {zone}: {zone_link[zone]}/{zone_total[zone]} = {100*rate:.1f}%")

    interior_rate = zone_link['INTERIOR'] / zone_total['INTERIOR'] if zone_total['INTERIOR'] > 0 else 0
    entry_rate = zone_link['ENTRY'] / zone_total['ENTRY'] if zone_total['ENTRY'] > 0 else 0
    exit_rate = zone_link['EXIT'] / zone_total['EXIT'] if zone_total['EXIT'] > 0 else 0

    # Chi-square for zone dependence
    zone_ct = np.array([
        [zone_link['ENTRY'], zone_total['ENTRY'] - zone_link['ENTRY']],
        [zone_link['INTERIOR'], zone_total['INTERIOR'] - zone_link['INTERIOR']],
        [zone_link['EXIT'], zone_total['EXIT'] - zone_link['EXIT']],
    ])
    chi2_zone, p_zone, _, _ = scipy_stats.chi2_contingency(zone_ct)
    print(f"  Zone chi-square: chi2={chi2_zone:.1f}, p={p_zone:.2e}")

    # 5b. Per-folio enrichment
    folio_enrichments = {}
    valid_folios = set(folio_data.keys())

    for folio in sorted(folio_line_lists.keys()):
        if folio not in valid_folios:
            continue
        fz_link = Counter()
        fz_total = Counter()
        for tokens in folio_line_lists[folio]:
            n = len(tokens)
            for i, tok in enumerate(tokens):
                if i == 0:
                    zone = 'ENTRY'
                elif i == n - 1:
                    zone = 'EXIT'
                else:
                    zone = 'INTERIOR'
                fz_total[zone] += 1
                if tok['is_link']:
                    fz_link[zone] += 1

        f_int_rate = fz_link['INTERIOR'] / fz_total['INTERIOR'] if fz_total['INTERIOR'] > 10 else None
        if f_int_rate is not None and f_int_rate > 0:
            f_entry_rate = fz_link['ENTRY'] / fz_total['ENTRY'] if fz_total['ENTRY'] > 0 else 0
            f_exit_rate = fz_link['EXIT'] / fz_total['EXIT'] if fz_total['EXIT'] > 0 else 0
            folio_enrichments[folio] = {
                'entry_enrichment': f_entry_rate / f_int_rate,
                'exit_enrichment': f_exit_rate / f_int_rate,
                'link_density': (fz_link['ENTRY'] + fz_link['INTERIOR'] + fz_link['EXIT']) /
                                (fz_total['ENTRY'] + fz_total['INTERIOR'] + fz_total['EXIT']),
            }

    entry_enrich_vals = [v['entry_enrichment'] for v in folio_enrichments.values()]
    exit_enrich_vals = [v['exit_enrichment'] for v in folio_enrichments.values()]
    print(f"\n  Per-folio entry enrichment: mean={np.mean(entry_enrich_vals):.3f}, std={np.std(entry_enrich_vals):.3f}")
    print(f"  Per-folio exit enrichment: mean={np.mean(exit_enrich_vals):.3f}, std={np.std(exit_enrich_vals):.3f}")

    # 5c. Correlation with entry/exit divergence
    # Compute divergence (replicate Phase 416 pattern)
    div_data = {}
    for folio in sorted(valid_folios):
        if folio not in folio_line_lists:
            continue
        lines = folio_line_lists[folio]
        zone_trans = {'ENTRY': [], 'INTERIOR': [], 'EXIT': []}
        for tokens in lines:
            nk = len(tokens)
            for i in range(nk - 1):
                if tokens[i]['cls'] is not None and tokens[i + 1]['cls'] is not None:
                    src_cls = tokens[i]['cls']
                    tgt_cls = tokens[i + 1]['cls']
                    if i == 0:
                        z = 'ENTRY'
                    elif i + 1 == nk - 1:
                        z = 'EXIT'
                    else:
                        z = 'INTERIOR'
                    zone_trans[z].append((src_cls, tgt_cls))
        if all(len(zone_trans[z]) >= MIN_ZONE_TRANS for z in zone_trans):
            m6_e = matrix_to_6state(build_zone_matrix(zone_trans['ENTRY']))
            m6_i = matrix_to_6state(build_zone_matrix(zone_trans['INTERIOR']))
            m6_x = matrix_to_6state(build_zone_matrix(zone_trans['EXIT']))
            div_data[folio] = {
                'jsd_entry': compute_jsd(m6_e.flatten(), m6_i.flatten()),
                'jsd_exit': compute_jsd(m6_x.flatten(), m6_i.flatten()),
            }

    # Correlate enrichment with divergence
    common = sorted(f for f in folio_enrichments if f in div_data)
    entry_corr = exit_corr = {'rho': 0, 'p': 1}
    if len(common) >= 10:
        ee = [folio_enrichments[f]['entry_enrichment'] for f in common]
        xe = [folio_enrichments[f]['exit_enrichment'] for f in common]
        jsd_e = [div_data[f]['jsd_entry'] for f in common]
        jsd_x = [div_data[f]['jsd_exit'] for f in common]

        rho_ee, p_ee = spearman_r(ee, jsd_e)
        rho_xe, p_xe = spearman_r(xe, jsd_x)
        entry_corr = {'rho': rho_ee, 'p': p_ee}
        exit_corr = {'rho': rho_xe, 'p': p_xe}
        print(f"\n  LINK entry enrichment vs jsd_entry: rho={rho_ee:.4f}, p={p_ee:.4f} (n={len(common)})")
        print(f"  LINK exit enrichment vs jsd_exit:   rho={rho_xe:.4f}, p={p_xe:.4f}")

    # 5d. Per-section boundary behavior
    section_boundary = {}
    for sec in sorted(set(folio_data[f]['section'] for f in folio_data)):
        sec_folios = [f for f in folio_line_lists if folio_data.get(f, {}).get('section') == sec]
        sz_link = Counter()
        sz_total = Counter()
        for folio in sec_folios:
            for tokens in folio_line_lists[folio]:
                nk = len(tokens)
                for i, tok in enumerate(tokens):
                    if i == 0: zone = 'ENTRY'
                    elif i == nk - 1: zone = 'EXIT'
                    else: zone = 'INTERIOR'
                    sz_total[zone] += 1
                    if tok['is_link']:
                        sz_link[zone] += 1
        if sz_total['INTERIOR'] > 0:
            section_boundary[sec] = {
                z: sz_link[z] / sz_total[z] if sz_total[z] > 0 else 0
                for z in ['ENTRY', 'INTERIOR', 'EXIT']
            }
            print(f"  Section {sec}: entry={100*section_boundary[sec]['ENTRY']:.1f}%, interior={100*section_boundary[sec]['INTERIOR']:.1f}%, exit={100*section_boundary[sec]['EXIT']:.1f}%")

    # 5e. Boundary vs interior LINK sub-population
    boundary_link = [t for t in folio_enrichments]  # placeholder
    # Profile LINK tokens at boundaries vs interior by role
    bound_roles = Counter()
    int_roles = Counter()
    for folio in folio_line_lists:
        for tokens in folio_line_lists[folio]:
            nk = len(tokens)
            for i, tok in enumerate(tokens):
                if tok['is_link']:
                    if i == 0 or i == nk - 1:
                        bound_roles[tok['role']] += 1
                    else:
                        int_roles[tok['role']] += 1

    bound_total = sum(bound_roles.values())
    int_total = sum(int_roles.values())
    if bound_total > 0 and int_total > 0:
        bound_dist = [bound_roles.get(r, 0) / bound_total for r in ALL_ROLES]
        int_dist = [int_roles.get(r, 0) / int_total for r in ALL_ROLES]
        subpop_jsd = compute_jsd(bound_dist, int_dist)
        print(f"\n  Boundary vs interior LINK role JSD: {subpop_jsd:.4f}")
    else:
        subpop_jsd = 0

    # Verdict
    has_corr = (abs(entry_corr['rho']) > 0.25 and entry_corr['p'] < 0.05) or \
               (abs(exit_corr['rho']) > 0.25 and exit_corr['p'] < 0.05)
    if has_corr:
        verdict = 'BOUNDARY_CHOREOGRAPHY'
    elif p_zone < 0.05:
        verdict = 'BOUNDARY_ENRICHED_PASSIVE'
    else:
        verdict = 'BOUNDARY_NEUTRAL'
    print(f"  Verdict: {verdict}")

    return {
        'zone_rates': {
            'ENTRY': float(entry_rate),
            'INTERIOR': float(interior_rate),
            'EXIT': float(exit_rate),
        },
        'zone_chi2': float(chi2_zone),
        'zone_p': float(p_zone),
        'per_folio_enrichment_stats': {
            'n_folios': len(folio_enrichments),
            'entry_mean': float(np.mean(entry_enrich_vals)),
            'entry_std': float(np.std(entry_enrich_vals)),
            'exit_mean': float(np.mean(exit_enrich_vals)),
            'exit_std': float(np.std(exit_enrich_vals)),
        },
        'divergence_correlation': {
            'n_common': len(common),
            'entry_enrichment_vs_jsd_entry': entry_corr,
            'exit_enrichment_vs_jsd_exit': exit_corr,
        },
        'per_section_boundary': section_boundary,
        'boundary_subpopulation_jsd': float(subpop_jsd),
        'verdict': verdict,
    }


# ── Synthesis ────────────────────────────────────────────────────

def synthesize(t1, t2, t3, t4, t5):
    t1v = t1['verdict']
    t2v = t2['verdict']
    t4v = t4['verdict']

    if t1v == 'STRATIFIED' and t2v == 'CROSS_ROLE_SUBSTRATE' and t4v == 'LINK_MODULATES_DYNAMICS':
        overall = 'LINK_FUNCTIONAL_LAYER'
    elif t2v == 'ROLE_DOMINANT' and t4v == 'LINK_PASSIVE_PARTICIPANT':
        overall = 'LINK_MORPHOLOGICAL_ARTIFACT'
    elif t1v in ('STRATIFIED', 'WEAKLY_STRATIFIED') and t2v == 'ROLE_DOMINANT':
        overall = 'LINK_ROLE_MODULATED'
    elif t1v == 'HOMOGENEOUS' and t2v == 'CROSS_ROLE_SUBSTRATE':
        overall = 'LINK_UNIFORM_SUBSTRATE'
    else:
        overall = 'LINK_MIXED_SIGNAL'

    return overall


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 418: LINK_FUNCTIONAL_ARCHITECTURE")
    print("=" * 60)

    all_tokens, link_tokens, nonlink_tokens, folio_line_lists, folio_data, folio_section = load_data()

    t1 = test1_vocabulary_stratification(link_tokens, all_tokens)
    t2 = test2_cross_role_consistency(all_tokens, folio_line_lists)
    t3 = test3_section_decomposition(all_tokens, link_tokens)
    t4 = test4_macro_automaton_dynamics(folio_line_lists)
    t5 = test5_boundary_architecture(folio_line_lists, folio_data)

    overall = synthesize(t1, t2, t3, t4, t5)

    print(f"\n── SYNTHESIS ──")
    print(f"  T1={t1['verdict']}")
    print(f"  T2={t2['verdict']}")
    print(f"  T3={t3['verdict']}")
    print(f"  T4={t4['verdict']}")
    print(f"  T5={t5['verdict']}")
    print(f"  Overall: {overall}")

    output = {
        'phase': 'LINK_FUNCTIONAL_ARCHITECTURE',
        'phase_number': 418,
        'depends_on': ['C609', 'C805', 'C808', 'C804', 'C806', 'C1168', 'C334'],
        'population': {
            'n_tokens': len(link_tokens),
            'n_types': t1['n_types'],
            'density': len(link_tokens) / len(all_tokens) if all_tokens else 0,
        },
        'test1_vocabulary_stratification': t1,
        'test2_cross_role_consistency': t2,
        'test3_section_decomposition': t3,
        'test4_macro_automaton_dynamics': t4,
        'test5_boundary_architecture': t5,
        'synthesis': {
            'verdicts': {
                't1': t1['verdict'],
                't2': t2['verdict'],
                't3': t3['verdict'],
                't4': t4['verdict'],
                't5': t5['verdict'],
            },
            'overall': overall,
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'link_functional_architecture.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2, cls=NumpyEncoder)

    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
