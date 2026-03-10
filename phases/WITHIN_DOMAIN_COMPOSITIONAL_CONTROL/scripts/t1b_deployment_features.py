"""Phase 560b T1b: Deployment Feature Extraction

Loads Phase 560 T1 corpus. Computes 56 enhanced per-folio deployment
features in 5 categories: zone-conditioned (18), adjacency routing (12),
closure packaging (7), headless v2 (11), paragraph-conditioned (8).

Input: t1_domain_decomposition.json
Output: t1b_deployment_features.json
"""
import json
import math
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

RESULTS_DIR = Path(__file__).parent.parent / 'results'
DOMAINS = ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']
DOMAIN_KEYS = ['k', 't', 'a', 'e', 'o', 'hl']
HEADED_ATOMS = {'k', 't', 'a', 'e', 'o'}
OPAQUE_TERMS = {'m', 'n', 'y'}

# Feature name registry
ZONE_FEATURES = []
for dk in DOMAIN_KEYS:
    ZONE_FEATURES += [f'{dk}_spec_frac', f'{dk}_close_frac']
ZONE_FEATURES += [
    'e_ey_spec_enrichment', 'a_high_close_enrichment',
    'k_q1_fraction', 'k_q1_minus_q23',
    'o_dispatch_zone_skew', 'e_ey_q0q1_frac',
]

ADJ_FEATURES = [
    'r_to_a_enrichment', 'y_to_k_enrichment',
    'h_to_t_enrichment', 'm_to_o_enrichment',
    'domain_transition_entropy', 'domain_self_run_mean',
    'safe_to_thermal_onset', 'hazard_safe_recovery_rate',
    'active_close_continuation_rate',
    'q3q4_routing_break_strength', 'cross_line_routing_decay',
    'm_linefinal_rate',
]

CLOSURE_FEATURES = [
    'q4_opaque_terminal_rate', 'q4_m_terminal_rate',
    'q4_suffix_suppression_rate', 'q4_highhaz_fraction',
    'q3q4_head_jsd_local', 'post_highhaz_safe_anchor_rate',
    'line_close_selfcontainment',
]

HEADLESS_FEATURES = [
    'hl_d_frac', 'hl_i_frac', 'hl_l_frac', 'hl_cpf_frac', 'hl_other_frac',
    'hl_displaced_kt_rate', 'hl_displaced_eao_rate',
    'hl_displaced_suffix_transparency',
    'hl_zone_spec_frac', 'hl_zone_close_frac',
    'hl_header_enrichment',
]

PARA_FEATURES = [
    'para_thermal_emphasis_span', 'para_containment_emphasis_span',
    'para_iteration_emphasis_span', 'para_monitoring_emphasis_span',
    'within_folio_para_gradient_span', 'same_type_para_run_tendency',
    'header_body_domain_shift', 'para_close_hazard_span',
]

ALL_FEATURES = ZONE_FEATURES + ADJ_FEATURES + CLOSURE_FEATURES + HEADLESS_FEATURES + PARA_FEATURES


def load_t1():
    path = RESULTS_DIR / 't1_domain_decomposition.json'
    print(f"Loading T1 corpus from {path}...")
    t0 = time.time()
    with open(path) as f:
        data = json.load(f)
    print(f"  Loaded {len(data['corpus_tokens'])} tokens in {time.time()-t0:.1f}s")
    return data


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
    """Jensen-Shannon divergence between two count dicts."""
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


# ===================================================================
# Category A: Zone-conditioned deployment (18 features)
# ===================================================================
def compute_zone_features(folio_tokens):
    f = {}
    by_domain = defaultdict(list)
    for t in folio_tokens:
        by_domain[t['domain']].append(t)

    # Per-domain SPEC and CLOSE fractions (12 features)
    for dname, dk in zip(DOMAINS, DOMAIN_KEYS):
        d_toks = by_domain[dname]
        if len(d_toks) >= 5:
            f[f'{dk}_spec_frac'] = safe_frac(d_toks, lambda t: t['line_zone'] == 'SPEC')
            f[f'{dk}_close_frac'] = safe_frac(d_toks, lambda t: t['line_zone'] == 'CLOSE')
        else:
            f[f'{dk}_spec_frac'] = None
            f[f'{dk}_close_frac'] = None

    # e->y SPEC enrichment (C1459)
    e_toks = by_domain['STABILITY']
    ey_toks = [t for t in e_toks if t['frame'] == 'e->y']
    if len(ey_toks) >= 3:
        f['e_ey_spec_enrichment'] = safe_frac(ey_toks, lambda t: t['line_zone'] == 'SPEC')
    else:
        f['e_ey_spec_enrichment'] = None

    # HIGH-hazard ACTIVE at CLOSE (C1463)
    a_toks = by_domain['ACTIVE']
    a_high = [t for t in a_toks if t['frame_hazard'] == 'HIGH']
    if len(a_high) >= 3:
        f['a_high_close_enrichment'] = safe_frac(a_high, lambda t: t['line_zone'] == 'CLOSE')
    else:
        f['a_high_close_enrichment'] = None

    # THERMAL at Q1 (C1428)
    k_toks = by_domain['THERMAL']
    if len(k_toks) >= 5:
        f['k_q1_fraction'] = safe_frac(k_toks, lambda t: t['quintile'] == 1)
        # Q1 minus mean Q2-Q3 (work-interior shape)
        q1_rate = f['k_q1_fraction']
        q23_toks = [t for t in k_toks if t['quintile'] in (2, 3)]
        q23_rate = len(q23_toks) / len(k_toks) / 2  # average of Q2 and Q3
        f['k_q1_minus_q23'] = q1_rate - q23_rate
    else:
        f['k_q1_fraction'] = None
        f['k_q1_minus_q23'] = None

    # ARRANGEMENT SPEC vs CLOSE skew
    o_toks = by_domain['ARRANGEMENT']
    if len(o_toks) >= 5:
        o_spec = safe_frac(o_toks, lambda t: t['line_zone'] == 'SPEC')
        o_close = safe_frac(o_toks, lambda t: t['line_zone'] == 'CLOSE')
        f['o_dispatch_zone_skew'] = o_spec - o_close
    else:
        f['o_dispatch_zone_skew'] = None

    # e->y early bias (Q0-Q1 fraction)
    if len(ey_toks) >= 3:
        f['e_ey_q0q1_frac'] = safe_frac(ey_toks, lambda t: t['quintile'] <= 1)
    else:
        f['e_ey_q0q1_frac'] = None

    return f


# ===================================================================
# Category B: Adjacency routing motifs (12 features)
# ===================================================================
def compute_adjacency_features(folio_tokens):
    f = {}
    n = len(folio_tokens)
    if n == 0:
        return {k: None for k in ADJ_FEATURES}

    # Routing enrichments (folio-local observed/expected)
    adj_pairs = [(t['prev_term_same_line'], t['head'])
                 for t in folio_tokens
                 if t['prev_term_same_line'] is not None and t['head'] is not None]
    pair_ct = Counter(adj_pairs)
    term_mg = Counter(p[0] for p in adj_pairs)
    head_mg = Counter(p[1] for p in adj_pairs)
    n_pairs = len(adj_pairs)

    def folio_enr(term_val, head_val):
        obs = pair_ct.get((term_val, head_val), 0)
        tt = term_mg.get(term_val, 0)
        hh = head_mg.get(head_val, 0)
        if tt < 3 or n_pairs == 0:
            return None
        exp = tt * (hh / n_pairs)
        if exp == 0:
            return None
        return obs / exp

    f['r_to_a_enrichment'] = folio_enr('r', 'a')
    f['y_to_k_enrichment'] = folio_enr('y', 'k')
    f['h_to_t_enrichment'] = folio_enr('h', 't')
    f['m_to_o_enrichment'] = folio_enr('m', 'o')

    # Domain transition entropy
    bigrams = Counter()
    for t in folio_tokens:
        if t['next_domain_same_line'] is not None:
            bigrams[(t['domain'], t['next_domain_same_line'])] += 1
    f['domain_transition_entropy'] = safe_entropy(bigrams)

    # Domain self-run mean length
    line_groups = defaultdict(list)
    for t in folio_tokens:
        line_groups[t['line']].append(t['domain'])
    runs = []
    for line_domains in line_groups.values():
        run_len = 1
        for i in range(1, len(line_domains)):
            if line_domains[i] == line_domains[i - 1]:
                run_len += 1
            else:
                runs.append(run_len)
                run_len = 1
        runs.append(run_len)
    f['domain_self_run_mean'] = sum(runs) / len(runs) if runs else None

    # e->y followed by THERMAL on same line
    ey_with_next = [t for t in folio_tokens
                    if t['frame'] == 'e->y' and t['next_domain_same_line'] is not None]
    f['safe_to_thermal_onset'] = safe_frac(
        ey_with_next, lambda t: t['next_domain_same_line'] == 'THERMAL'
    ) if ey_with_next else None

    # HIGH-hazard -> STABILITY recovery
    high_haz = [t for t in folio_tokens
                if t['frame_hazard'] == 'HIGH' and t['next_domain_same_line'] is not None]
    f['hazard_safe_recovery_rate'] = safe_frac(
        high_haz, lambda t: t['next_domain_same_line'] == 'STABILITY'
    ) if high_haz else None

    # ACTIVE at CLOSE with continuation
    a_close_all = [t for t in folio_tokens
                   if t['domain'] == 'ACTIVE' and t['line_zone'] == 'CLOSE']
    a_close_cont = [t for t in a_close_all if t['next_domain_same_line'] is not None]
    f['active_close_continuation_rate'] = (
        len(a_close_cont) / len(a_close_all) if a_close_all else None
    )

    # Q3-Q4 routing break strength (C1566)
    # Routing enrichment at Q1-Q3 vs Q4
    pairs_q13 = [(t['prev_term_same_line'], t['head'])
                 for t in folio_tokens
                 if t['prev_term_same_line'] is not None and t['head'] is not None
                 and t['quintile'] in (1, 2, 3)]
    pairs_q4 = [(t['prev_term_same_line'], t['head'])
                for t in folio_tokens
                if t['prev_term_same_line'] is not None and t['head'] is not None
                and t['quintile'] == 4]
    # Use total routing pair count as strength proxy
    if pairs_q13 and pairs_q4:
        # Routing entropy at each zone
        q13_bigrams = Counter(pairs_q13)
        q4_bigrams = Counter(pairs_q4)
        q13_ent = safe_entropy(q13_bigrams)
        q4_ent = safe_entropy(q4_bigrams)
        f['q3q4_routing_break_strength'] = q13_ent - q4_ent  # positive = routing collapses at Q4
    else:
        f['q3q4_routing_break_strength'] = None

    # Cross-line routing decay (C1470-C1471)
    # Compare same-line routing pair entropy vs cross-line
    # Same-line pairs already computed; cross-line = consecutive line-final -> next line-initial
    # We can proxy this: tokens where prev_term is from same line (strong) vs None (line boundary)
    same_line_pair_count = n_pairs
    total_non_initial = sum(1 for t in folio_tokens if t['line_pos'] > 0)
    if total_non_initial > 0 and same_line_pair_count > 0:
        # Fraction of non-initial tokens that have valid same-line predecessor
        f['cross_line_routing_decay'] = same_line_pair_count / total_non_initial
    else:
        f['cross_line_routing_decay'] = None

    # m-terminal at line_pos > 0.9 (C1434-C1439)
    m_toks = [t for t in folio_tokens if t['term'] == 'm']
    f['m_linefinal_rate'] = safe_frac(m_toks, lambda t: t['line_pos'] > 0.9) if m_toks else None

    return f


# ===================================================================
# Category C: Closure packaging (7 features)
# ===================================================================
def compute_closure_features(folio_tokens):
    f = {}
    if not folio_tokens:
        return {k: None for k in CLOSURE_FEATURES}

    q4_toks = [t for t in folio_tokens if t['quintile'] == 4]
    non_q4 = [t for t in folio_tokens if t['quintile'] < 4]

    if len(q4_toks) >= 5:
        f['q4_opaque_terminal_rate'] = safe_frac(
            q4_toks, lambda t: t['term'] in OPAQUE_TERMS)
        f['q4_m_terminal_rate'] = safe_frac(q4_toks, lambda t: t['term'] == 'm')
        f['q4_suffix_suppression_rate'] = safe_frac(
            q4_toks, lambda t: not t['suffix'] or len(t['suffix']) == 0)
        # HIGH hazard fraction at Q4 vs overall
        overall_high = safe_frac(folio_tokens, lambda t: t['frame_hazard'] == 'HIGH')
        q4_high = safe_frac(q4_toks, lambda t: t['frame_hazard'] == 'HIGH')
        if overall_high and overall_high > 0:
            f['q4_highhaz_fraction'] = q4_high / overall_high
        else:
            f['q4_highhaz_fraction'] = None
    else:
        f['q4_opaque_terminal_rate'] = None
        f['q4_m_terminal_rate'] = None
        f['q4_suffix_suppression_rate'] = None
        f['q4_highhaz_fraction'] = None

    # Q3 vs Q4 HEAD JSD (per-folio closure cliff, C1566)
    q3_toks = [t for t in folio_tokens if t['quintile'] == 3]
    if len(q3_toks) >= 5 and len(q4_toks) >= 5:
        q3_heads = Counter(t['head'] if t['head'] else 'NONE' for t in q3_toks)
        q4_heads = Counter(t['head'] if t['head'] else 'NONE' for t in q4_toks)
        f['q3q4_head_jsd_local'] = jsd(q3_heads, q4_heads)
    else:
        f['q3q4_head_jsd_local'] = None

    # POST-HIGH-hazard safe anchor rate
    high_with_next = [t for t in folio_tokens
                      if t['frame_hazard'] == 'HIGH' and t['next_domain_same_line'] is not None]
    if high_with_next:
        f['post_highhaz_safe_anchor_rate'] = safe_frac(
            high_with_next,
            lambda t: t['next_domain_same_line'] in ('STABILITY', 'THERMAL'))
    else:
        f['post_highhaz_safe_anchor_rate'] = None

    # Line close self-containment: fraction of lines where last token is OPAQUE or no suffix
    line_groups = defaultdict(list)
    for t in folio_tokens:
        line_groups[t['line']].append(t)
    if line_groups:
        sealed = 0
        for line_key in line_groups:
            toks = sorted(line_groups[line_key], key=lambda t: t['line_pos'])
            last = toks[-1]
            if last['term'] in OPAQUE_TERMS or not last['suffix'] or len(last['suffix']) == 0:
                sealed += 1
        f['line_close_selfcontainment'] = sealed / len(line_groups)
    else:
        f['line_close_selfcontainment'] = None

    return f


# ===================================================================
# Category D: Headless v2 decomposition (11 features)
# ===================================================================
def compute_headless_features(folio_tokens):
    f = {}
    hl_toks = [t for t in folio_tokens if t['domain'] == 'HEADLESS']

    if len(hl_toks) < 10:
        return {k: None for k in HEADLESS_FEATURES}

    # Pseudo-HEAD atom distribution (5 fractions)
    pseudo_atoms = Counter(t['pseudo_head_atom'] for t in hl_toks if t['pseudo_head_atom'])
    total_pseudo = sum(pseudo_atoms.values())
    if total_pseudo > 0:
        f['hl_d_frac'] = pseudo_atoms.get('d', 0) / total_pseudo
        f['hl_i_frac'] = pseudo_atoms.get('i', 0) / total_pseudo
        f['hl_l_frac'] = pseudo_atoms.get('l', 0) / total_pseudo
        f['hl_cpf_frac'] = sum(pseudo_atoms.get(a, 0) for a in ('c', 'p', 'f')) / total_pseudo
        f['hl_other_frac'] = sum(v for k, v in pseudo_atoms.items()
                                 if k not in ('d', 'i', 'l', 'c', 'p', 'f')) / total_pseudo
    else:
        f['hl_d_frac'] = f['hl_i_frac'] = f['hl_l_frac'] = None
        f['hl_cpf_frac'] = f['hl_other_frac'] = None

    # Displaced HEAD terminal — split by atom type (C1494-C1498)
    hl_displaced = [t for t in hl_toks if t['has_displaced_head_terminal']]
    n_disp = len(hl_displaced)
    if n_disp >= 3:
        kt_disp = [t for t in hl_displaced
                    if any(c in ('k', 't') for c in t['middle'][1:] if c in HEADED_ATOMS)]
        eao_disp = [t for t in hl_displaced
                    if any(c in ('e', 'a', 'o') for c in t['middle'][1:] if c in HEADED_ATOMS)]
        f['hl_displaced_kt_rate'] = len(kt_disp) / len(hl_toks)
        f['hl_displaced_eao_rate'] = len(eao_disp) / len(hl_toks)
        # Suffix transparency among displaced kt
        if kt_disp:
            f['hl_displaced_suffix_transparency'] = safe_frac(
                kt_disp, lambda t: t['suffix'] is not None and len(t['suffix']) > 0)
        else:
            f['hl_displaced_suffix_transparency'] = None
    else:
        f['hl_displaced_kt_rate'] = len(hl_displaced) / len(hl_toks) if hl_toks else None
        f['hl_displaced_eao_rate'] = None
        f['hl_displaced_suffix_transparency'] = None

    # Zone deployment
    f['hl_zone_spec_frac'] = safe_frac(hl_toks, lambda t: t['line_zone'] == 'SPEC')
    f['hl_zone_close_frac'] = safe_frac(hl_toks, lambda t: t['line_zone'] == 'CLOSE')

    # Header enrichment: headless rate in HEADER minus BODY
    all_header = [t for t in folio_tokens if t['paragraph_zone'] == 'HEADER']
    all_body = [t for t in folio_tokens if t['paragraph_zone'] == 'BODY']
    hl_header = [t for t in all_header if t['domain'] == 'HEADLESS']
    hl_body = [t for t in all_body if t['domain'] == 'HEADLESS']
    if len(all_header) >= 5 and len(all_body) >= 5:
        f['hl_header_enrichment'] = len(hl_header) / len(all_header) - len(hl_body) / len(all_body)
    else:
        f['hl_header_enrichment'] = None

    return f


# ===================================================================
# Category E: Paragraph-conditioned deployment (8 features)
# ===================================================================
def compute_paragraph_features(folio_tokens, min_paras=3, min_tokens=15):
    f = {}

    # Group by paragraph_idx
    para_groups = defaultdict(list)
    for t in folio_tokens:
        para_groups[t['paragraph_idx']].append(t)

    qualifying = {pi: toks for pi, toks in para_groups.items() if len(toks) >= min_tokens}

    if len(qualifying) < min_paras:
        return {k: None for k in PARA_FEATURES}

    # Compute domain profiles per paragraph
    para_profiles = {}
    for pi, toks in qualifying.items():
        n = len(toks)
        profile = {}
        for dname in DOMAINS:
            profile[dname] = sum(1 for t in toks if t['domain'] == dname) / n
        para_profiles[pi] = profile

    # Operational gradient spans (C1398)
    k_fracs = [p['THERMAL'] for p in para_profiles.values()]
    f['para_thermal_emphasis_span'] = max(k_fracs) - min(k_fracs)

    # Containment = headless + CONTAINMENT-category tokens
    contain_fracs = []
    for pi, toks in qualifying.items():
        n = len(toks)
        cnt = sum(1 for t in toks
                  if t['domain'] == 'HEADLESS' or t['operational_category'] == 'CONTAINMENT')
        contain_fracs.append(cnt / n)
    f['para_containment_emphasis_span'] = max(contain_fracs) - min(contain_fracs)

    a_fracs = [p['ACTIVE'] for p in para_profiles.values()]
    f['para_iteration_emphasis_span'] = max(a_fracs) - min(a_fracs)

    e_fracs = [p['STABILITY'] for p in para_profiles.values()]
    f['para_monitoring_emphasis_span'] = max(e_fracs) - min(e_fracs)

    # Mean pairwise Euclidean of paragraph domain profiles
    pids = list(para_profiles.keys())
    pw_dists = []
    for i in range(len(pids)):
        for j in range(i + 1, len(pids)):
            pi, pj = para_profiles[pids[i]], para_profiles[pids[j]]
            d = math.sqrt(sum((pi[dm] - pj[dm]) ** 2 for dm in DOMAINS))
            pw_dists.append(d)
    f['within_folio_para_gradient_span'] = sum(pw_dists) / len(pw_dists) if pw_dists else None

    # Same-type paragraph run tendency (C1399 inertia)
    # Dominant domain per paragraph
    para_types = []
    for pi in sorted(qualifying.keys()):
        prof = para_profiles[pi]
        dominant = max(prof, key=prof.get)
        para_types.append(dominant)
    if len(para_types) >= 2:
        self_trans = sum(1 for i in range(1, len(para_types))
                        if para_types[i] == para_types[i - 1])
        f['same_type_para_run_tendency'] = self_trans / (len(para_types) - 1)
    else:
        f['same_type_para_run_tendency'] = None

    # Header-body domain shift
    header_toks = [t for toks in qualifying.values() for t in toks
                   if t['paragraph_zone'] == 'HEADER']
    body_toks = [t for toks in qualifying.values() for t in toks
                 if t['paragraph_zone'] == 'BODY']
    if len(header_toks) >= 10 and len(body_toks) >= 10:
        hn, bn = len(header_toks), len(body_toks)
        hp = [sum(1 for t in header_toks if t['domain'] == d) / hn for d in DOMAINS]
        bp = [sum(1 for t in body_toks if t['domain'] == d) / bn for d in DOMAINS]
        f['header_body_domain_shift'] = math.sqrt(sum((a - b) ** 2 for a, b in zip(hp, bp)))
    else:
        f['header_body_domain_shift'] = None

    # Paragraph close hazard span: range of CLOSE-zone HIGH-hazard rate across paragraphs
    close_haz_rates = []
    for pi, toks in qualifying.items():
        close_toks = [t for t in toks if t['line_zone'] == 'CLOSE']
        if len(close_toks) >= 3:
            rate = safe_frac(close_toks, lambda t: t['frame_hazard'] == 'HIGH')
            if rate is not None:
                close_haz_rates.append(rate)
    if len(close_haz_rates) >= 2:
        f['para_close_hazard_span'] = max(close_haz_rates) - min(close_haz_rates)
    else:
        f['para_close_hazard_span'] = None

    return f


# ===================================================================
# Main
# ===================================================================
def main():
    t_start = time.time()
    data = load_t1()
    corpus = data['corpus_tokens']

    # Group tokens by folio
    by_folio = defaultdict(list)
    for t in corpus:
        by_folio[t['folio']].append(t)

    folios = sorted(by_folio.keys())
    print(f"Computing deployment features for {len(folios)} folios...")

    folio_features = {}
    for fi, fol in enumerate(folios):
        toks = by_folio[fol]

        feats = {}
        feats.update(compute_zone_features(toks))
        feats.update(compute_adjacency_features(toks))
        feats.update(compute_closure_features(toks))
        feats.update(compute_headless_features(toks))
        feats.update(compute_paragraph_features(toks))

        folio_features[fol] = feats

        if (fi + 1) % 20 == 0 or fi == len(folios) - 1:
            print(f"  [{fi+1}/{len(folios)}] {fol}: {sum(1 for v in feats.values() if v is not None)}/{len(ALL_FEATURES)} features valid")

    # Feature statistics
    feature_stats = {}
    for fname in ALL_FEATURES:
        vals = [folio_features[f][fname] for f in folios if folio_features[f].get(fname) is not None]
        n_valid = len(vals)
        n_none = len(folios) - n_valid
        if vals:
            mean_v = sum(vals) / len(vals)
            if len(vals) > 1:
                var_v = sum((v - mean_v) ** 2 for v in vals) / (len(vals) - 1)
                std_v = math.sqrt(var_v)
            else:
                std_v = 0.0
            feature_stats[fname] = {
                'mean': round(mean_v, 6),
                'std': round(std_v, 6),
                'min': round(min(vals), 6),
                'max': round(max(vals), 6),
                'n_valid': n_valid,
                'n_none': n_none,
            }
        else:
            feature_stats[fname] = {
                'mean': None, 'std': None, 'min': None, 'max': None,
                'n_valid': 0, 'n_none': n_none,
            }

    # Validation
    all_have_features = all(
        any(v is not None for v in folio_features[f].values()) for f in folios
    )
    all_consistent = all(
        set(folio_features[f].keys()) == set(ALL_FEATURES) for f in folios
    )
    features_ge50 = sum(1 for fname in ALL_FEATURES
                        if feature_stats[fname]['n_valid'] >= len(folios) * 0.5)

    # Paragraph coverage
    para_qualifying = sum(1 for f in folios
                          if folio_features[f].get('para_thermal_emphasis_span') is not None)

    # Output
    output = {
        'metadata': {
            'phase': '560b',
            'task': 'T1b_deployment_features',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_features_zone': len(ZONE_FEATURES),
            'n_features_adjacency': len(ADJ_FEATURES),
            'n_features_closure': len(CLOSURE_FEATURES),
            'n_features_headless': len(HEADLESS_FEATURES),
            'n_features_paragraph': len(PARA_FEATURES),
            'n_features_total': len(ALL_FEATURES),
            'n_folios': len(folios),
            'n_qualifying_para_folios': para_qualifying,
        },
        'feature_names': {
            'zone': ZONE_FEATURES,
            'adjacency': ADJ_FEATURES,
            'closure': CLOSURE_FEATURES,
            'headless': HEADLESS_FEATURES,
            'paragraph': PARA_FEATURES,
            'all': ALL_FEATURES,
        },
        'folio_features': folio_features,
        'feature_stats': feature_stats,
        'validation': {
            'all_folios_have_features': all_have_features,
            'all_feature_names_consistent': all_consistent,
            'n_features_with_ge50pct_valid': features_ge50,
            'para_qualifying_folios': para_qualifying,
        },
    }

    out_path = RESULTS_DIR / 't1b_deployment_features.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"\nWrote {out_path} ({size_mb:.1f} MB)")

    # Summary
    print(f"\n{'='*60}")
    print(f"T1b SUMMARY")
    print(f"{'='*60}")
    print(f"  Folios: {len(folios)}")
    print(f"  Features: {len(ALL_FEATURES)}")
    print(f"    Zone: {len(ZONE_FEATURES)}")
    print(f"    Adjacency: {len(ADJ_FEATURES)}")
    print(f"    Closure: {len(CLOSURE_FEATURES)}")
    print(f"    Headless: {len(HEADLESS_FEATURES)}")
    print(f"    Paragraph: {len(PARA_FEATURES)}")
    print(f"  Para-qualifying folios: {para_qualifying}/{len(folios)}")
    print(f"  Features with >= 50% valid: {features_ge50}/{len(ALL_FEATURES)}")
    print(f"  All consistent: {all_consistent}")
    print(f"  Runtime: {time.time()-t_start:.1f}s")

    # Print NaN-heavy features
    high_nan = [(fname, feature_stats[fname]['n_none'])
                for fname in ALL_FEATURES
                if feature_stats[fname]['n_none'] > len(folios) * 0.3]
    if high_nan:
        print(f"\n  Features with >30% NaN:")
        for fname, nn in sorted(high_nan, key=lambda x: -x[1]):
            print(f"    {fname}: {nn}/{len(folios)} NaN")

    print(f"\n{'='*60}")
    print("T1b COMPLETE")


if __name__ == '__main__':
    main()
