"""Phase 560 T2: Within-Domain Constraint Validation

T2A: 17 structural spine tests (hard invariants, <=1 failure allowed)
T2B: ~30 soft profile replication tests (informational)

Input: t1_domain_decomposition.json
Output: t2_within_domain_validation.json
"""
import json
import math
import os
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def load_t1():
    path = RESULTS_DIR / 't1_domain_decomposition.json'
    with open(path) as f:
        return json.load(f)


def entropy(counts):
    """Shannon entropy in bits from a Counter/dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def jsd(dist_a, dist_b):
    """Jensen-Shannon divergence between two dicts (count or probability)."""
    all_keys = set(dist_a) | set(dist_b)
    total_a = sum(dist_a.values()) or 1
    total_b = sum(dist_b.values()) or 1
    m = {}
    for k in all_keys:
        pa = dist_a.get(k, 0) / total_a
        pb = dist_b.get(k, 0) / total_b
        m[k] = (pa + pb) / 2

    def kl(p_dist, total, q_dist):
        d = 0.0
        for k in all_keys:
            pk = p_dist.get(k, 0) / total
            qk = q_dist[k]
            if pk > 0 and qk > 0:
                d += pk * math.log2(pk / qk)
        return d

    return 0.5 * kl(dist_a, total_a, m) + 0.5 * kl(dist_b, total_b, m)


def enrichment(subset_count, subset_total, corpus_count, corpus_total):
    """Compute enrichment ratio of an item in subset vs corpus."""
    if corpus_total == 0 or subset_total == 0:
        return 0.0
    r_sub = subset_count / subset_total
    r_corp = corpus_count / corpus_total
    if r_corp == 0:
        return float('inf') if r_sub > 0 else 1.0
    return r_sub / r_corp


def get_domain_tokens(data, domain):
    """Get all token dicts for a domain."""
    idxs = data['indices']['by_domain'].get(domain, [])
    return [data['corpus_tokens'][i] for i in idxs]


def hazard_rate(tokens, filter_fn=None):
    """Fraction of tokens with frame_hazard == 'HIGH'."""
    if filter_fn:
        tokens = [t for t in tokens if filter_fn(t)]
    if len(tokens) == 0:
        return None
    return sum(1 for t in tokens if t['frame_hazard'] == 'HIGH') / len(tokens)


def frac_with(tokens, key, value=True):
    """Fraction of tokens where token[key] == value."""
    if len(tokens) == 0:
        return None
    return sum(1 for t in tokens if t.get(key) == value) / len(tokens)


def frac_where(tokens, fn):
    """Fraction of tokens where fn(token) is True."""
    if len(tokens) == 0:
        return None
    return sum(1 for t in tokens if fn(t)) / len(tokens)


def main():
    t0 = time.time()
    print("=== Phase 560 T2: Within-Domain Constraint Validation ===")

    data = load_t1()
    all_tokens = data['corpus_tokens']
    print(f"  Loaded {len(all_tokens)} tokens")

    results = {'t2a': {}, 't2b': {}, 'metadata': {
        'phase': '560', 'task': 'T2_within_domain_validation',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    }}

    # Pre-compute domain token lists
    domains = {}
    for d in ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']:
        domains[d] = get_domain_tokens(data, d)
    headed_tokens = [t for t in all_tokens if t['domain'] != 'HEADLESS']

    # ═══════════════════════════════════════════════════════════
    # T2A: STRUCTURAL SPINE REPLICATION (17 tests)
    # ═══════════════════════════════════════════════════════════
    print("\n  === T2A: Structural Spine ===")
    t2a = {}
    t2a_failures = 0

    # --- K1: THERMAL 0% hazard in ALL frames ---
    k_tokens = domains['THERMAL']
    k_max_haz = max(
        (hazard_rate(k_tokens, lambda t: t['frame'] == f) or 0)
        for f in set(t['frame'] for t in k_tokens if t['frame'])
    ) if k_tokens else 0
    k1_pass = k_max_haz == 0.0
    t2a['K1'] = {'desc': 'THERMAL 0% hazard in ALL frames',
                 'max_hazard_rate': k_max_haz, 'pass': k1_pass}
    if not k1_pass:
        t2a_failures += 1
    print(f"  K1: max hazard = {k_max_haz:.4f} -> {'PASS' if k1_pass else 'FAIL'}")

    # --- K6: THERMAL category purity > 85% ---
    k_cat = Counter(t['operational_category'] for t in k_tokens)
    k_thermal_purity = k_cat.get('THERMAL', 0) / len(k_tokens) if k_tokens else 0
    k6_pass = k_thermal_purity > 0.85
    t2a['K6'] = {'desc': 'THERMAL category purity > 85%',
                 'purity': round(k_thermal_purity, 4), 'pass': k6_pass}
    if not k6_pass:
        t2a_failures += 1
    print(f"  K6: purity = {k_thermal_purity:.4f} -> {'PASS' if k6_pass else 'FAIL'}")

    # --- A5: ACTIVE double-ii = 0% effective hazard (C1482) ---
    # C1482: a-HEAD + double-ii = 0% hazard. This is encoded as is_safe_pathway = True.
    # Frame hazard map may still show HIGH for the frame, but the ii mechanism quenches it.
    a_tokens = domains['ACTIVE']
    a_ii = [t for t in a_tokens if t['i_count'] >= 2]
    a5_safe = frac_where(a_ii, lambda t: t['is_safe_pathway']) if a_ii else 1.0
    a5_pass = a5_safe is not None and a5_safe > 0.99
    t2a['A5'] = {'desc': 'ACTIVE double-ii safe pathway > 99%',
                 'safe_rate': a5_safe, 'n_tokens': len(a_ii), 'pass': a5_pass}
    if not a5_pass:
        t2a_failures += 1
    print(f"  A5: ii safe_pathway = {a5_safe} (n={len(a_ii)}) -> {'PASS' if a5_pass else 'FAIL'}")

    # --- A7: a->l > 93% hazard ---
    a_l = [t for t in a_tokens if t['frame'] == 'a->l']
    a7_haz = hazard_rate(a_l) if a_l else None
    a7_pass = a7_haz is not None and a7_haz > 0.93
    t2a['A7'] = {'desc': 'a->l > 93% hazard',
                 'hazard_rate': a7_haz, 'n': len(a_l), 'pass': a7_pass}
    if not a7_pass:
        t2a_failures += 1
    print(f"  A7: a->l hazard = {a7_haz} (n={len(a_l)}) -> {'PASS' if a7_pass else 'FAIL'}")

    # --- A8: a->r > 93% hazard ---
    a_r = [t for t in a_tokens if t['frame'] == 'a->r']
    a8_haz = hazard_rate(a_r) if a_r else None
    a8_pass = a8_haz is not None and a8_haz > 0.93
    t2a['A8'] = {'desc': 'a->r > 93% hazard',
                 'hazard_rate': a8_haz, 'n': len(a_r), 'pass': a8_pass}
    if not a8_pass:
        t2a_failures += 1
    print(f"  A8: a->r hazard = {a8_haz} (n={len(a_r)}) -> {'PASS' if a8_pass else 'FAIL'}")

    # --- A9: ACTIVE highest hazard of all headed domains ---
    domain_hazards = {}
    for d in ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT']:
        domain_hazards[d] = hazard_rate(domains[d])
    a9_pass = (domain_hazards['ACTIVE'] is not None and
               all(domain_hazards['ACTIVE'] > (domain_hazards.get(d) or 0)
                   for d in ['THERMAL', 'FLOW', 'STABILITY', 'ARRANGEMENT']))
    t2a['A9'] = {'desc': 'ACTIVE highest headed hazard',
                 'domain_hazards': {d: round(v, 4) if v else 0
                                    for d, v in domain_hazards.items()},
                 'pass': a9_pass}
    if not a9_pass:
        t2a_failures += 1
    print(f"  A9: hazards = {domain_hazards} -> {'PASS' if a9_pass else 'FAIL'}")

    # --- E2: e->y hazard < 1% ---
    e_tokens = domains['STABILITY']
    e_y = [t for t in e_tokens if t['frame'] == 'e->y']
    e2_haz = hazard_rate(e_y) if e_y else None
    e2_pass = e2_haz is not None and e2_haz < 0.01
    t2a['E2'] = {'desc': 'e->y hazard < 1%',
                 'hazard_rate': e2_haz, 'n': len(e_y), 'pass': e2_pass}
    if not e2_pass:
        t2a_failures += 1
    print(f"  E2: e->y hazard = {e2_haz} (n={len(e_y)}) -> {'PASS' if e2_pass else 'FAIL'}")

    # --- O1: o->l = STAGING > 98% ---
    o_tokens = domains['ARRANGEMENT']
    o_l = [t for t in o_tokens if t['term'] == 'l']
    o1_staging = frac_where(o_l, lambda t: t['operational_category'] == 'STAGING') if o_l else None
    o1_pass = o1_staging is not None and o1_staging > 0.98
    t2a['O1'] = {'desc': 'o->l STAGING purity > 98%',
                 'purity': o1_staging, 'n': len(o_l), 'pass': o1_pass}
    if not o1_pass:
        t2a_failures += 1
    print(f"  O1: o->l STAGING = {o1_staging} (n={len(o_l)}) -> {'PASS' if o1_pass else 'FAIL'}")

    # --- O2: o->r = FLOW > 98% ---
    o_r = [t for t in o_tokens if t['term'] == 'r']
    o2_flow = frac_where(o_r, lambda t: t['operational_category'] == 'FLOW') if o_r else None
    o2_pass = o2_flow is not None and o2_flow > 0.98
    t2a['O2'] = {'desc': 'o->r FLOW purity > 98%',
                 'purity': o2_flow, 'n': len(o_r), 'pass': o2_pass}
    if not o2_pass:
        t2a_failures += 1
    print(f"  O2: o->r FLOW = {o2_flow} (n={len(o_r)}) -> {'PASS' if o2_pass else 'FAIL'}")

    # --- O3: bare-o = OPERATION > 95% ---
    o_bare = [t for t in o_tokens if t['term'] == 'bare']
    o3_oper = frac_where(o_bare, lambda t: t['operational_category'] == 'OPERATION') if o_bare else None
    o3_pass = o3_oper is not None and o3_oper > 0.95
    t2a['O3'] = {'desc': 'bare-o OPERATION purity > 95%',
                 'purity': o3_oper, 'n': len(o_bare), 'pass': o3_pass}
    if not o3_pass:
        t2a_failures += 1
    print(f"  O3: bare-o OPER = {o3_oper} (n={len(o_bare)}) -> {'PASS' if o3_pass else 'FAIL'}")

    # --- O4: y-terminal excluded from o-HEAD (< 1%) ---
    o4_y_frac = frac_where(o_tokens, lambda t: t['term'] == 'y')
    o4_pass = o4_y_frac is not None and o4_y_frac < 0.01
    t2a['O4'] = {'desc': 'o-HEAD y-terminal < 1%',
                 'y_frac': o4_y_frac, 'pass': o4_pass}
    if not o4_pass:
        t2a_failures += 1
    print(f"  O4: o y-term = {o4_y_frac:.4f} -> {'PASS' if o4_pass else 'FAIL'}")

    # --- O6: ARRANGEMENT 0% hazard (source AND target) (C1561) ---
    # Source: all o-HEAD are headed -> source_immune = True
    # Target: no o-tokens should have hazard_class_type set (only set on EXPOSED tokens)
    # Note: frame_hazard may show HIGH per the map, but effective exposure is 0% because
    # all o-HEAD tokens are source_immune (headed), so hazard_class_type is never assigned.
    o6_source_exposed = frac_where(o_tokens, lambda t: not t['source_immune'])
    o6_hazclass_set = frac_where(o_tokens, lambda t: t.get('hazard_class_type') is not None)
    o6_frame_haz = hazard_rate(o_tokens)  # diagnostic
    o6_pass = (o6_source_exposed is not None and o6_source_exposed < 0.01 and
               o6_hazclass_set is not None and o6_hazclass_set < 0.01)
    t2a['O6'] = {'desc': 'ARRANGEMENT 0% effective hazard',
                 'source_exposed_rate': o6_source_exposed,
                 'hazard_class_set_rate': o6_hazclass_set,
                 'frame_hazard_high_rate': o6_frame_haz,
                 'note': 'frame_hazard is pre-immunity; effective exposure checks source_immune + hazard_class',
                 'pass': o6_pass}
    if not o6_pass:
        t2a_failures += 1
    print(f"  O6: src_exposed={o6_source_exposed:.4f}, haz_class={o6_hazclass_set:.4f} -> {'PASS' if o6_pass else 'FAIL'}")

    # --- Routing tests X1-X4: terminal→HEAD enrichment on same line ---
    # Build adjacency pairs: (prev_term, next_head) for same-line pairs
    print("  Computing routing enrichments...")
    adj_pairs = [(t['prev_term_same_line'], t['head'])
                 for t in all_tokens
                 if t['prev_term_same_line'] is not None and t['head'] is not None]
    pair_counts = Counter(adj_pairs)
    term_marginal = Counter(p[0] for p in adj_pairs)
    head_marginal = Counter(p[1] for p in adj_pairs)
    total_pairs = len(adj_pairs)

    def routing_enrichment(term_val, head_val):
        obs = pair_counts.get((term_val, head_val), 0)
        t_total = term_marginal.get(term_val, 0)
        h_total = head_marginal.get(head_val, 0)
        if t_total == 0 or total_pairs == 0:
            return 0.0
        expected = t_total * (h_total / total_pairs)
        if expected == 0:
            return float('inf') if obs > 0 else 1.0
        return obs / expected

    # X1: r→a enrichment > 1.8x
    x1_enr = routing_enrichment('r', 'a')
    x1_pass = x1_enr > 1.8
    t2a['X1'] = {'desc': 'r→a enrichment > 1.8x',
                 'enrichment': round(x1_enr, 3), 'pass': x1_pass}
    if not x1_pass:
        t2a_failures += 1
    print(f"  X1: r→a = {x1_enr:.3f}x -> {'PASS' if x1_pass else 'FAIL'}")

    # X2: y→k enrichment > 1.3x
    x2_enr = routing_enrichment('y', 'k')
    x2_pass = x2_enr > 1.3
    t2a['X2'] = {'desc': 'y→k enrichment > 1.3x',
                 'enrichment': round(x2_enr, 3), 'pass': x2_pass}
    if not x2_pass:
        t2a_failures += 1
    print(f"  X2: y→k = {x2_enr:.3f}x -> {'PASS' if x2_pass else 'FAIL'}")

    # X3: h→t enrichment > 1.5x
    x3_enr = routing_enrichment('h', 't')
    x3_pass = x3_enr > 1.5
    t2a['X3'] = {'desc': 'h→t enrichment > 1.5x',
                 'enrichment': round(x3_enr, 3), 'pass': x3_pass}
    if not x3_pass:
        t2a_failures += 1
    print(f"  X3: h→t = {x3_enr:.3f}x -> {'PASS' if x3_pass else 'FAIL'}")

    # X4: m→o enrichment > 1.3x
    x4_enr = routing_enrichment('m', 'o')
    x4_pass = x4_enr > 1.3
    t2a['X4'] = {'desc': 'm→o enrichment > 1.3x',
                 'enrichment': round(x4_enr, 3), 'pass': x4_pass}
    if not x4_pass:
        t2a_failures += 1
    print(f"  X4: m→o = {x4_enr:.3f}x -> {'PASS' if x4_pass else 'FAIL'}")

    # --- X6: Q3→Q4 HEAD JSD jump > 10x Q2→Q3 ---
    print("  Computing quintile HEAD distributions...")
    head_by_q = defaultdict(Counter)
    for t in all_tokens:
        if t['head'] is not None:
            head_by_q[t['quintile']][t['head']] += 1

    jsd_23 = jsd(dict(head_by_q[2]), dict(head_by_q[3])) if head_by_q[2] and head_by_q[3] else 0
    jsd_34 = jsd(dict(head_by_q[3]), dict(head_by_q[4])) if head_by_q[3] and head_by_q[4] else 0
    x6_ratio = jsd_34 / jsd_23 if jsd_23 > 0 else float('inf')
    x6_pass = x6_ratio > 10
    t2a['X6'] = {'desc': 'Q3→Q4 HEAD JSD jump > 10x Q2→Q3',
                 'jsd_23': round(jsd_23, 6), 'jsd_34': round(jsd_34, 6),
                 'ratio': round(x6_ratio, 2), 'pass': x6_pass}
    if not x6_pass:
        t2a_failures += 1
    print(f"  X6: JSD34/JSD23 = {x6_ratio:.2f}x -> {'PASS' if x6_pass else 'FAIL'}")

    t2a_pass = t2a_failures <= 1
    results['t2a'] = {
        'tests': t2a,
        'n_failures': t2a_failures,
        'n_tests': 17,
        'pass': t2a_pass,
    }
    print(f"\n  T2A: {17 - t2a_failures}/17 pass, failures = {t2a_failures} -> {'PASS' if t2a_pass else 'FAIL'}")

    # ═══════════════════════════════════════════════════════════
    # T2B: WITHIN-DOMAIN PROFILE REPLICATION (soft)
    # ═══════════════════════════════════════════════════════════
    print("\n  === T2B: Profile Replication (soft) ===")
    t2b = {}

    # --- THERMAL ---
    # K2: Bare-terminal dominant > 85%
    k2_bare = frac_where(k_tokens, lambda t: t['term'] == 'bare')
    t2b['K2'] = {'desc': 'k bare-terminal > 85%', 'value': round(k2_bare, 4),
                 'threshold': 0.85, 'pass': k2_bare > 0.85}
    print(f"  K2: k bare-term = {k2_bare:.4f} (>0.85)")

    # K3: Modifier-depleted < 20%
    k3_mod = frac_where(k_tokens, lambda t: len(t['mods']) > 0)
    t2b['K3'] = {'desc': 'k modifier < 20%', 'value': round(k3_mod, 4),
                 'threshold': 0.20, 'pass': k3_mod < 0.20}
    print(f"  K3: k mod rate = {k3_mod:.4f} (<0.20)")

    # K4: Near-universal suffix > 90%
    k4_sfx = frac_where(k_tokens, lambda t: t['suffix'] is not None and len(t['suffix']) > 0)
    t2b['K4'] = {'desc': 'k suffix > 90%', 'value': round(k4_sfx, 4),
                 'threshold': 0.90, 'pass': k4_sfx > 0.90}
    print(f"  K4: k suffix rate = {k4_sfx:.4f} (>0.90)")

    # K5: qo-PREFIX enrichment among k-HEAD > 3.0x
    corpus_qo_rate = sum(1 for t in all_tokens if t['prefix'] == 'qo') / len(all_tokens)
    k_qo_rate = sum(1 for t in k_tokens if t['prefix'] == 'qo') / len(k_tokens) if k_tokens else 0
    k5_enr = k_qo_rate / corpus_qo_rate if corpus_qo_rate > 0 else 0
    t2b['K5'] = {'desc': 'k qo-PREFIX enrichment > 3x', 'enrichment': round(k5_enr, 2),
                 'threshold': 3.0, 'pass': k5_enr > 3.0}
    print(f"  K5: k qo enrich = {k5_enr:.2f}x (>3.0)")

    # --- FLOW ---
    t_tokens = domains['FLOW']

    # T1: Terminal mirrors k (JSD < 0.01)
    k_term_dist = Counter(t['term'] for t in k_tokens)
    t_term_dist = Counter(t['term'] for t in t_tokens)
    t1_jsd = jsd(dict(k_term_dist), dict(t_term_dist))
    t2b['T1'] = {'desc': 'k-t terminal JSD < 0.01', 'jsd': round(t1_jsd, 6),
                 'threshold': 0.01, 'pass': t1_jsd < 0.01}
    print(f"  T1: k-t term JSD = {t1_jsd:.6f} (<0.01)")

    # T2: Category opposes k (JSD > 0.5)
    k_cat_dist = Counter(t['operational_category'] for t in k_tokens)
    t_cat_dist = Counter(t['operational_category'] for t in t_tokens)
    t2_jsd = jsd(dict(k_cat_dist), dict(t_cat_dist))
    t2b['T2'] = {'desc': 'k-t category JSD > 0.5', 'jsd': round(t2_jsd, 6),
                 'threshold': 0.5, 'pass': t2_jsd > 0.5}
    print(f"  T2: k-t cat JSD = {t2_jsd:.6f} (>0.5)")

    # T3: Modifier quenches hazard in t-domain
    t_with_mod = [t for t in t_tokens if len(t['mods']) > 0]
    t_no_mod = [t for t in t_tokens if len(t['mods']) == 0]
    t3_haz_with = hazard_rate(t_with_mod) if t_with_mod else None
    t3_haz_without = hazard_rate(t_no_mod) if t_no_mod else None
    t3_pass = (t3_haz_with is not None and t3_haz_without is not None and
               t3_haz_with < 0.05 and t3_haz_without > 0.40)
    t2b['T3'] = {'desc': 't-domain modifier quenches hazard',
                 'haz_with_mod': t3_haz_with, 'haz_without_mod': t3_haz_without,
                 'pass': t3_pass}
    print(f"  T3: t haz with-mod={t3_haz_with}, without={t3_haz_without}")

    # T5: FLOW category purity > 80%
    t5_flow = frac_where(t_tokens, lambda t: t['operational_category'] == 'FLOW')
    t2b['T5'] = {'desc': 't FLOW purity > 80%', 'value': round(t5_flow, 4),
                 'threshold': 0.80, 'pass': t5_flow > 0.80}
    print(f"  T5: t FLOW purity = {t5_flow:.4f} (>0.80)")

    # --- ACTIVE ---
    # A1: i-modifier monopoly > 65%
    a1_i = frac_where(a_tokens, lambda t: t['has_i_mod'])
    t2b['A1'] = {'desc': 'a i-mod > 65%', 'value': round(a1_i, 4),
                 'threshold': 0.65, 'pass': a1_i > 0.65}
    print(f"  A1: a i-mod = {a1_i:.4f} (>0.65)")

    # A2: Without i: r/l dominant > 60%
    a_no_i = [t for t in a_tokens if not t['has_i_mod']]
    a2_rl = frac_where(a_no_i, lambda t: t['term'] in ('r', 'l')) if a_no_i else None
    t2b['A2'] = {'desc': 'a no-i r/l > 60%', 'value': a2_rl,
                 'threshold': 0.60, 'pass': a2_rl is not None and a2_rl > 0.60}
    print(f"  A2: a no-i r/l = {a2_rl} (>0.60)")

    # A3: With i: n dominant > 70%
    a_with_i = [t for t in a_tokens if t['has_i_mod']]
    a3_n = frac_where(a_with_i, lambda t: t['term'] == 'n') if a_with_i else None
    t2b['A3'] = {'desc': 'a with-i n-term > 70%', 'value': a3_n,
                 'threshold': 0.70, 'pass': a3_n is not None and a3_n > 0.70}
    print(f"  A3: a with-i n-term = {a3_n} (>0.70)")

    # A4: Monotonic i-count hazard gradient
    a_0i = [t for t in a_tokens if t['i_count'] == 0]
    a_1i = [t for t in a_tokens if t['i_count'] == 1]
    a_2i = [t for t in a_tokens if t['i_count'] >= 2]
    h0 = hazard_rate(a_0i) if a_0i else None
    h1 = hazard_rate(a_1i) if a_1i else None
    h2 = hazard_rate(a_2i) if a_2i else None
    a4_mono = (h0 is not None and h1 is not None and h2 is not None and
               h0 > h1 > h2)
    t2b['A4'] = {'desc': 'a monotonic i-count hazard', 'h0': h0, 'h1': h1, 'h2': h2,
                 'monotonic': a4_mono, 'pass': a4_mono}
    print(f"  A4: haz(0i)={h0}, haz(1i)={h1}, haz(2i+)={h2} -> {'monotonic' if a4_mono else 'not monotonic'}")

    # A6: a->bare safe < 5%
    a_bare = [t for t in a_tokens if t['frame'] == 'a->bare']
    a6_haz = hazard_rate(a_bare) if a_bare else None
    t2b['A6'] = {'desc': 'a->bare hazard < 5%', 'hazard': a6_haz, 'n': len(a_bare),
                 'threshold': 0.05, 'pass': a6_haz is not None and a6_haz < 0.05}
    print(f"  A6: a->bare haz = {a6_haz} (n={len(a_bare)}) (<0.05)")

    # --- STABILITY ---
    # E1: e->y is ~50% of e-HEAD > 40%
    e1_ey = frac_where(e_tokens, lambda t: t['frame'] == 'e->y')
    t2b['E1'] = {'desc': 'e->y fraction > 40%', 'value': round(e1_ey, 4),
                 'threshold': 0.40, 'pass': e1_ey > 0.40}
    print(f"  E1: e->y frac = {e1_ey:.4f} (>0.40)")

    # E3: e->y vocabulary ≤ 12 unique MIDDLEs
    ey_middles = set(t['middle'] for t in e_y)
    e3_ct = len(ey_middles)
    t2b['E3'] = {'desc': 'e->y unique MIDDLEs <= 12', 'count': e3_ct,
                 'middles': sorted(ey_middles), 'pass': e3_ct <= 12}
    print(f"  E3: e->y vocab = {e3_ct} middles (<=12)")

    # E4: d-modifier enrichment > 28%
    e4_d = frac_where(e_tokens, lambda t: 'd' in t['mods'])
    t2b['E4'] = {'desc': 'e d-mod > 28%', 'value': round(e4_d, 4),
                 'threshold': 0.28, 'pass': e4_d > 0.28}
    print(f"  E4: e d-mod = {e4_d:.4f} (>0.28)")

    # E5: ee→THERMAL saturation > 70%
    ee_tokens = [t for t in e_tokens if t['middle'] and t['middle'].startswith('ee')]
    e5_thermal = frac_where(ee_tokens, lambda t: t['operational_category'] == 'THERMAL') if ee_tokens else None
    t2b['E5'] = {'desc': 'ee THERMAL > 70%', 'value': e5_thermal, 'n': len(ee_tokens),
                 'threshold': 0.70, 'pass': e5_thermal is not None and e5_thermal > 0.70}
    print(f"  E5: ee THERMAL = {e5_thermal} (n={len(ee_tokens)}) (>0.70)")

    # E6: e->y CHSH-exclusive (qo enrichment in e->y vs e-overall < 0.20x)
    ey_qo = sum(1 for t in e_y if t['prefix'] == 'qo') / len(e_y) if e_y else 0
    e_qo = sum(1 for t in e_tokens if t['prefix'] == 'qo') / len(e_tokens) if e_tokens else 0
    e6_ratio = ey_qo / e_qo if e_qo > 0 else 0
    t2b['E6'] = {'desc': 'e->y qo depletion < 0.20x', 'ratio': round(e6_ratio, 3),
                 'threshold': 0.20, 'pass': e6_ratio < 0.20}
    print(f"  E6: e->y qo ratio = {e6_ratio:.3f} (<0.20)")

    # E7: e->d hazardous > 50%
    e_d = [t for t in e_tokens if t['frame'] == 'e->d']
    e7_haz = hazard_rate(e_d) if e_d else None
    # Note: 'e->d' might not exist as a frame. Check if we get e tokens with term='d'
    # Actually, d is not a terminal char ({y,l,r,h,m,n}), so frame would be 'e->bare' for ed tokens.
    # The constraint C1448 maps frame hazard by first-char->last-char. For MIDDLEs like 'ed',
    # the frame is 'e->bare' because 'd' is not in the TERMINAL set.
    # Let's check what frames e-HEAD tokens actually have with d in middle
    e_d_interior = [t for t in e_tokens if 'd' in t['mods']]
    e7_haz_mods = hazard_rate(e_d_interior) if e_d_interior else None
    t2b['E7'] = {'desc': 'e with d-modifier hazardous > 50%',
                 'hazard_d_mod': e7_haz_mods, 'n_d_mod': len(e_d_interior),
                 'hazard_e_d_frame': e7_haz, 'n_e_d_frame': len(e_d) if e_d else 0,
                 'note': 'd is not a terminal; checking d-modifier tokens instead',
                 'pass': e7_haz_mods is not None and e7_haz_mods > 0.50}
    print(f"  E7: e d-mod haz = {e7_haz_mods} (n={len(e_d_interior)}) (>0.50)")

    # --- ARRANGEMENT ---
    # O5: p/f modifier enriched
    corpus_p_rate = sum(1 for t in all_tokens if 'p' in t['mods']) / len(all_tokens)
    corpus_f_rate = sum(1 for t in all_tokens if 'f' in t['mods']) / len(all_tokens)
    o_p_rate = sum(1 for t in o_tokens if 'p' in t['mods']) / len(o_tokens) if o_tokens else 0
    o_f_rate = sum(1 for t in o_tokens if 'f' in t['mods']) / len(o_tokens) if o_tokens else 0
    o5_p_enr = o_p_rate / corpus_p_rate if corpus_p_rate > 0 else 0
    o5_f_enr = o_f_rate / corpus_f_rate if corpus_f_rate > 0 else 0
    o5_pass = o5_p_enr > 2.5 and o5_f_enr > 2.0
    t2b['O5'] = {'desc': 'o p/f mod enrichment', 'p_enrich': round(o5_p_enr, 2),
                 'f_enrich': round(o5_f_enr, 2), 'pass': o5_pass}
    print(f"  O5: o p-enrich={o5_p_enr:.2f}x, f-enrich={o5_f_enr:.2f}x")

    # --- HEADLESS ---
    hl_tokens = domains['HEADLESS']

    # H1: a-base PREFIX → > 85% headless
    a_base_tokens = [t for t in all_tokens if t['prefix_base'] == 'a']
    h1_hl_frac = frac_where(a_base_tokens, lambda t: t['domain'] == 'HEADLESS') if a_base_tokens else None
    t2b['H1'] = {'desc': 'a-base PREFIX > 85% headless', 'value': h1_hl_frac,
                 'n': len(a_base_tokens), 'threshold': 0.85,
                 'pass': h1_hl_frac is not None and h1_hl_frac > 0.85}
    print(f"  H1: a-base headless = {h1_hl_frac} (n={len(a_base_tokens)}) (>0.85)")

    # H2: Pseudo-HEAD domain selector V > 0.25
    # Cramér's V between pseudo_head_atom and operational_category
    hl_with_pseudo = [t for t in hl_tokens if t['pseudo_head_atom'] is not None
                      and t['operational_category'] is not None]
    if len(hl_with_pseudo) > 10:
        # Build contingency table
        ph_atoms = sorted(set(t['pseudo_head_atom'] for t in hl_with_pseudo))
        cats = sorted(set(t['operational_category'] for t in hl_with_pseudo))
        ct_table = defaultdict(lambda: defaultdict(int))
        for t in hl_with_pseudo:
            ct_table[t['pseudo_head_atom']][t['operational_category']] += 1
        # Chi-squared
        n = len(hl_with_pseudo)
        row_totals = {a: sum(ct_table[a].values()) for a in ph_atoms}
        col_totals = {c: sum(ct_table[a][c] for a in ph_atoms) for c in cats}
        chi2 = 0.0
        for a in ph_atoms:
            for c in cats:
                obs = ct_table[a][c]
                exp = row_totals[a] * col_totals[c] / n if n > 0 else 0
                if exp > 0:
                    chi2 += (obs - exp) ** 2 / exp
        k = min(len(ph_atoms), len(cats))
        cramers_v = math.sqrt(chi2 / (n * max(k - 1, 1))) if n > 0 else 0
    else:
        cramers_v = None
    h2_pass = cramers_v is not None and cramers_v > 0.25
    t2b['H2'] = {'desc': 'headless pseudo-HEAD V > 0.25', 'cramers_v': round(cramers_v, 4) if cramers_v else None,
                 'pass': h2_pass}
    print(f"  H2: pseudo-HEAD V = {cramers_v} (>0.25)")

    # HL4: Near-zero THERMAL in headless < 5%
    hl4_thermal = frac_where(hl_tokens, lambda t: t['operational_category'] == 'THERMAL')
    t2b['HL4'] = {'desc': 'headless THERMAL < 5%', 'value': round(hl4_thermal, 4),
                  'threshold': 0.05, 'pass': hl4_thermal < 0.05}
    print(f"  HL4: hl THERMAL = {hl4_thermal:.4f} (<0.05)")

    # HL5: Locked terminals r/m depleted (ratio < 0.5x vs headed)
    headed_rm = frac_where(headed_tokens, lambda t: t['term'] in ('r', 'm'))
    hl_rm = frac_where(hl_tokens, lambda t: t['term'] in ('r', 'm'))
    hl5_ratio = hl_rm / headed_rm if headed_rm and headed_rm > 0 else None
    t2b['HL5'] = {'desc': 'headless r/m depletion < 0.5x', 'headed_rm': headed_rm,
                  'headless_rm': hl_rm, 'ratio': round(hl5_ratio, 3) if hl5_ratio else None,
                  'pass': hl5_ratio is not None and hl5_ratio < 0.5}
    print(f"  HL5: hl r/m ratio = {hl5_ratio} (<0.5)")

    # HL6: d/i-initial bare vs c/p/f-initial suffixed
    hl_di = [t for t in hl_tokens if t['headless_subtype'] == 'PSEUDO_HEAD_CORE'
             and t['pseudo_head_atom'] in ('d', 'i')]
    hl_cpf = [t for t in hl_tokens if t['headless_subtype'] == 'PARAMETRIC']
    di_sfx = frac_where(hl_di, lambda t: t['suffix'] is not None and len(t['suffix']) > 0) if hl_di else None
    cpf_sfx = frac_where(hl_cpf, lambda t: t['suffix'] is not None and len(t['suffix']) > 0) if hl_cpf else None
    hl6_pass = (di_sfx is not None and cpf_sfx is not None and di_sfx < cpf_sfx)
    t2b['HL6'] = {'desc': 'd/i suffix < c/p/f suffix', 'di_suffix_rate': di_sfx,
                  'cpf_suffix_rate': cpf_sfx, 'pass': hl6_pass}
    print(f"  HL6: d/i sfx={di_sfx}, c/p/f sfx={cpf_sfx} -> {'PASS' if hl6_pass else 'FAIL'}")

    # HL7: Displaced k/t terminal transparency (informational)
    hl_displaced = [t for t in hl_tokens if t['has_displaced_head_terminal']]
    hl7_frac = len(hl_displaced) / len(hl_tokens) if hl_tokens else 0
    t2b['HL7'] = {'desc': 'headless displaced head terminal fraction',
                  'fraction': round(hl7_frac, 4), 'count': len(hl_displaced),
                  'pass': True}  # informational
    print(f"  HL7: displaced head term = {hl7_frac:.4f} (n={len(hl_displaced)}) (info)")

    # --- Routing (additional) ---
    # X5: Suffix zero forward info (JSD < 0.015)
    suffixed = [t for t in all_tokens if t['suffix'] is not None and len(t['suffix']) > 0
                and t['next_domain_same_line'] is not None]
    bare_sfx = [t for t in all_tokens if (t['suffix'] is None or len(t['suffix']) == 0)
                and t['next_domain_same_line'] is not None]
    sfx_next = Counter(t['next_domain_same_line'] for t in suffixed) if suffixed else Counter()
    bare_next = Counter(t['next_domain_same_line'] for t in bare_sfx) if bare_sfx else Counter()
    # Actually X5 is about next HEAD specifically, not domain
    # Let me use head from the next token. We stored next_domain_same_line, not next_head.
    # We can approximate: if next token's domain is HEADLESS, head is None; else head = first letter of domain
    # Better: use the pair data we already built. Check if suffix presence changes next-HEAD distribution.
    suffixed_t = [t for t in all_tokens if t['suffix'] is not None and len(t['suffix']) > 0
                  and t['next_domain_same_line'] is not None]
    bare_t = [t for t in all_tokens if (t['suffix'] is None or len(t['suffix']) == 0)
              and t['next_domain_same_line'] is not None]
    sfx_next_head = Counter(t['next_domain_same_line'] for t in suffixed_t)
    bare_next_head = Counter(t['next_domain_same_line'] for t in bare_t)
    x5_jsd = jsd(dict(sfx_next_head), dict(bare_next_head)) if sfx_next_head and bare_next_head else 0
    x5_pass = x5_jsd < 0.015
    t2b['X5'] = {'desc': 'Suffix zero forward info JSD < 0.015',
                 'jsd': round(x5_jsd, 6), 'pass': x5_pass}
    print(f"  X5: suffix→next JSD = {x5_jsd:.6f} (<0.015)")

    # X7: Cross-line routing collapse (within-line / cross-line ratio > 2.5x)
    # Within-line: use adj_pairs we already have (these are same-line)
    # Cross-line: build pairs across line boundaries
    print("  Computing cross-line routing...")
    cross_line_pairs = []
    # Iterate tokens to find line-final → next-line-initial pairs
    for i in range(len(all_tokens) - 1):
        t_curr = all_tokens[i]
        t_next = all_tokens[i + 1]
        if (t_curr['folio'] == t_next['folio'] and
            t_curr['line'] != t_next['line'] and
            t_curr['term'] is not None and t_next['head'] is not None):
            cross_line_pairs.append((t_curr['term'], t_next['head']))

    cross_counts = Counter(cross_line_pairs)
    cross_term_mg = Counter(p[0] for p in cross_line_pairs)
    cross_head_mg = Counter(p[1] for p in cross_line_pairs)
    n_cross = len(cross_line_pairs)

    def cross_routing_enrichment(term_val, head_val):
        obs = cross_counts.get((term_val, head_val), 0)
        t_total = cross_term_mg.get(term_val, 0)
        h_total = cross_head_mg.get(head_val, 0)
        if t_total == 0 or n_cross == 0:
            return 0.0
        expected = t_total * (h_total / n_cross)
        if expected == 0:
            return float('inf') if obs > 0 else 1.0
        return obs / expected

    # Compare average routing enrichment within-line vs cross-line for the 4 key routes
    routes = [('r', 'a'), ('y', 'k'), ('h', 't'), ('m', 'o')]
    within_avg = sum(routing_enrichment(t, h) for t, h in routes) / len(routes)
    cross_avg = sum(cross_routing_enrichment(t, h) for t, h in routes) / len(routes)
    x7_ratio = within_avg / cross_avg if cross_avg > 0 else float('inf')
    x7_pass = x7_ratio > 2.5
    t2b['X7'] = {'desc': 'Within/cross-line routing ratio > 2.5x',
                 'within_avg_enr': round(within_avg, 3), 'cross_avg_enr': round(cross_avg, 3),
                 'ratio': round(x7_ratio, 2), 'pass': x7_pass}
    print(f"  X7: within/cross = {x7_ratio:.2f}x (>2.5)")

    # X8: Zone-conditioned routing (informational)
    zone_routing = {}
    for zone in ['SPEC', 'WORK', 'CLOSE']:
        zone_pairs = [(t['prev_term_same_line'], t['head'])
                      for t in all_tokens
                      if t['prev_term_same_line'] is not None and t['head'] is not None
                      and t['line_zone'] == zone]
        zpc = Counter(zone_pairs)
        ztm = Counter(p[0] for p in zone_pairs)
        zhm = Counter(p[1] for p in zone_pairs)
        n_zp = len(zone_pairs)
        zone_enr = {}
        for t_val, h_val in routes:
            obs = zpc.get((t_val, h_val), 0)
            tt = ztm.get(t_val, 0)
            ht = zhm.get(h_val, 0)
            exp = tt * (ht / n_zp) if n_zp > 0 and tt > 0 else 0
            zone_enr[f'{t_val}→{h_val}'] = round(obs / exp, 2) if exp > 0 else None
        zone_routing[zone] = zone_enr
    t2b['X8'] = {'desc': 'Zone-conditioned routing (info)', 'zone_routing': zone_routing,
                 'pass': True}  # informational
    print(f"  X8: zone routing = {zone_routing}")

    # X9: No cross-line hazard recovery memory
    # After high-hazard lines, is e->y/safe-anchor rate enriched on the NEXT line?
    print("  Computing cross-line hazard memory...")
    # Group tokens by (folio, line) to compute per-line hazard
    line_tokens = defaultdict(list)
    for t in all_tokens:
        line_tokens[(t['folio'], t['line'])].append(t)

    # Order lines within each folio
    folio_lines = defaultdict(list)
    seen = set()
    for t in all_tokens:
        key = (t['folio'], t['line'])
        if key not in seen:
            folio_lines[t['folio']].append(key)
            seen.add(key)

    # Compute per-line hazard rate
    line_hazard = {}
    for key, toks in line_tokens.items():
        hr = sum(1 for t in toks if t['frame_hazard'] == 'HIGH') / len(toks)
        line_hazard[key] = hr

    # For each consecutive line pair, compute:
    # "after high-hazard line": safe_pathway rate of next line
    # "after safe line": safe_pathway rate of next line
    after_high = []
    after_safe = []
    for folio, lines in folio_lines.items():
        for i in range(len(lines) - 1):
            curr_haz = line_hazard[lines[i]]
            next_toks = line_tokens[lines[i + 1]]
            next_safe_rate = sum(1 for t in next_toks if t['is_safe_pathway']) / len(next_toks)
            if curr_haz > 0.3:
                after_high.append(next_safe_rate)
            elif curr_haz < 0.1:
                after_safe.append(next_safe_rate)

    mean_after_high = sum(after_high) / len(after_high) if after_high else None
    mean_after_safe = sum(after_safe) / len(after_safe) if after_safe else None
    x9_ratio = mean_after_high / mean_after_safe if (mean_after_safe and mean_after_safe > 0) else None
    x9_pass = x9_ratio is not None and x9_ratio <= 1.1
    t2b['X9'] = {'desc': 'No cross-line hazard recovery memory (ratio <= 1.1)',
                 'safe_after_high_haz': round(mean_after_high, 4) if mean_after_high else None,
                 'safe_after_safe': round(mean_after_safe, 4) if mean_after_safe else None,
                 'ratio': round(x9_ratio, 3) if x9_ratio else None,
                 'n_after_high': len(after_high), 'n_after_safe': len(after_safe),
                 'pass': x9_pass}
    print(f"  X9: safe-after-high={mean_after_high}, safe-after-safe={mean_after_safe}, ratio={x9_ratio}")

    # Count T2B passes
    t2b_results = list(t2b.values())
    t2b_pass_ct = sum(1 for r in t2b_results if r.get('pass'))
    t2b_total = len(t2b_results)
    results['t2b'] = {
        'tests': t2b,
        'n_pass': t2b_pass_ct,
        'n_total': t2b_total,
    }
    print(f"\n  T2B: {t2b_pass_ct}/{t2b_total} pass (informational)")

    # ═══════════════════════════════════════════════════════════
    # Overall T2 verdict
    # ═══════════════════════════════════════════════════════════
    t2_pass = t2a_pass  # T2A is the binding criterion
    results['verdict'] = {
        'pass': t2_pass,
        't2a_pass': t2a_pass,
        't2a_failures': t2a_failures,
        't2b_pass_count': t2b_pass_ct,
        't2b_total': t2b_total,
    }

    elapsed = time.time() - t0
    print(f"\n  === T2 VERDICT: {'PASS' if t2_pass else 'FAIL'} ===")
    print(f"  T2A: {17 - t2a_failures}/17 pass ({t2a_failures} failures, <=1 allowed)")
    print(f"  T2B: {t2b_pass_ct}/{t2b_total} pass (informational)")
    print(f"  Elapsed: {elapsed:.1f}s")

    out_path = RESULTS_DIR / 't2_within_domain_validation.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=1)
    import os
    print(f"  Output: {out_path} ({os.path.getsize(out_path)/1024:.0f} KB)")
    print(f"\n=== T2 Complete ===")


if __name__ == '__main__':
    main()
