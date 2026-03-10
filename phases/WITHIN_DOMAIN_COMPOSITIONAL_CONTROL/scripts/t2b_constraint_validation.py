"""Phase 560b T2b: Deployment Pattern Constraint Validation

Split into T2bA (12 constraint replication checks) and T2bB (8 instrument
sanity checks). Validates deployment features against known constraints.

Input: t1_domain_decomposition.json
Output: t2b_constraint_validation.json
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
HEADED_ATOMS = {'k', 't', 'a', 'e', 'o'}
OPAQUE_TERMS = {'m', 'n', 'y'}


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


def corpus_enrichment(tokens, filter_fn, zone_fn):
    """Compute enrichment of filter_fn tokens at zone_fn zone vs overall."""
    filtered = [t for t in tokens if filter_fn(t)]
    if not filtered:
        return None
    zone_rate_filtered = safe_frac(filtered, zone_fn)
    zone_rate_all = safe_frac(tokens, zone_fn)
    if zone_rate_all and zone_rate_all > 0:
        return zone_rate_filtered / zone_rate_all
    return None


def main():
    t_start = time.time()
    data = load_t1()
    corpus = data['corpus_tokens']
    print(f"Loaded {len(corpus)} tokens")

    results_a = []  # T2bA: Constraint replication checks
    results_b = []  # T2bB: Instrument sanity checks

    # ================================================================
    # T2bA: CONSTRAINT REPLICATION CHECKS (12 tests)
    # ================================================================
    print("\n" + "=" * 60)
    print("T2bA: CONSTRAINT REPLICATION CHECKS")
    print("=" * 60)

    # Z1: ZERO-hazard enriched at SPEC > 1.1x (C1463)
    enr = corpus_enrichment(
        corpus,
        lambda t: t['frame_hazard'] == 'ZERO' or t['is_safe_pathway'],
        lambda t: t['line_zone'] == 'SPEC'
    )
    z1 = {'test': 'Z1', 'constraint': 'C1463', 'description': 'ZERO-hazard enriched at SPEC > 1.1x',
           'value': round(enr, 4) if enr else None, 'threshold': 1.1,
           'pass': enr is not None and enr > 1.1}
    results_a.append(z1)
    print(f"  Z1: ZERO/safe at SPEC enrichment = {z1['value']} (> 1.1) {'PASS' if z1['pass'] else 'FAIL'}")

    # Z2: IMMUNE enriched at WORK > 1.1x (C1463)
    enr = corpus_enrichment(
        corpus,
        lambda t: t['frame_hazard'] == 'IMMUNE' or t['source_immune'],
        lambda t: t['line_zone'] == 'WORK'
    )
    z2 = {'test': 'Z2', 'constraint': 'C1463', 'description': 'IMMUNE enriched at WORK > 1.1x',
           'value': round(enr, 4) if enr else None, 'threshold': 1.1,
           'pass': enr is not None and enr > 1.1}
    results_a.append(z2)
    print(f"  Z2: IMMUNE at WORK enrichment = {z2['value']} (> 1.1) {'PASS' if z2['pass'] else 'FAIL'}")

    # Z3: HIGH enriched at CLOSE > 1.05x (C1463)
    enr = corpus_enrichment(
        corpus,
        lambda t: t['frame_hazard'] == 'HIGH',
        lambda t: t['line_zone'] == 'CLOSE'
    )
    z3 = {'test': 'Z3', 'constraint': 'C1463', 'description': 'HIGH enriched at CLOSE > 1.05x',
           'value': round(enr, 4) if enr else None, 'threshold': 1.05,
           'pass': enr is not None and enr > 1.05}
    results_a.append(z3)
    print(f"  Z3: HIGH at CLOSE enrichment = {z3['value']} (> 1.05) {'PASS' if z3['pass'] else 'FAIL'}")

    # Z4: THERMAL concentrated at Q1 above overall Q1 rate (C1464)
    k_toks = [t for t in corpus if t['domain'] == 'THERMAL']
    all_q1_rate = safe_frac(corpus, lambda t: t['quintile'] == 1)
    k_q1_rate = safe_frac(k_toks, lambda t: t['quintile'] == 1)
    z4_pass = k_q1_rate is not None and all_q1_rate is not None and k_q1_rate > all_q1_rate
    z4 = {'test': 'Z4', 'constraint': 'C1464', 'description': 'THERMAL at Q1 > overall Q1 rate',
           'value': round(k_q1_rate, 4) if k_q1_rate else None,
           'baseline': round(all_q1_rate, 4) if all_q1_rate else None,
           'pass': z4_pass}
    results_a.append(z4)
    print(f"  Z4: THERMAL Q1={z4['value']} vs overall Q1={z4['baseline']} {'PASS' if z4['pass'] else 'FAIL'}")

    # Z5: Zone-hazard interaction V stable across line-length tertiles (C1466)
    # Split folios by median line length, compare zone-hazard Cramer's V
    from collections import Counter
    line_lengths = defaultdict(list)
    line_groups = defaultdict(list)
    for t in corpus:
        line_groups[(t['folio'], t['line'])].append(t)
    all_line_lens = [len(toks) for toks in line_groups.values()]
    median_ll = sorted(all_line_lens)[len(all_line_lens) // 2]

    short_toks = []
    long_toks = []
    for key, toks in line_groups.items():
        if len(toks) <= median_ll:
            short_toks.extend(toks)
        else:
            long_toks.extend(toks)

    def zone_hazard_v(tokens):
        ct = Counter()
        for t in tokens:
            hz = t['frame_hazard'] or 'NONE'
            ct[(t['line_zone'], hz)] += 1
        # Simplified Cramer's V from contingency
        zones = sorted(set(k[0] for k in ct))
        hazards = sorted(set(k[1] for k in ct))
        n = sum(ct.values())
        if n == 0 or len(zones) <= 1 or len(hazards) <= 1:
            return 0
        row_sums = {z: sum(ct.get((z, h), 0) for h in hazards) for z in zones}
        col_sums = {h: sum(ct.get((z, h), 0) for z in zones) for h in hazards}
        chi2 = 0
        for z in zones:
            for h in hazards:
                obs = ct.get((z, h), 0)
                exp = row_sums[z] * col_sums[h] / n
                if exp > 0:
                    chi2 += (obs - exp) ** 2 / exp
        k_min = min(len(zones), len(hazards)) - 1
        if k_min == 0:
            return 0
        return math.sqrt(chi2 / (n * k_min))

    v_short = zone_hazard_v(short_toks)
    v_long = zone_hazard_v(long_toks)
    v_ratio = min(v_short, v_long) / max(v_short, v_long) if max(v_short, v_long) > 0 else 0
    z5 = {'test': 'Z5', 'constraint': 'C1466',
           'description': 'Zone-hazard V stable across line-length halves (ratio > 0.7)',
           'v_short': round(v_short, 4), 'v_long': round(v_long, 4),
           'ratio': round(v_ratio, 4),
           'pass': v_ratio > 0.7}
    results_a.append(z5)
    print(f"  Z5: V_short={z5['v_short']}, V_long={z5['v_long']}, ratio={z5['ratio']} {'PASS' if z5['pass'] else 'FAIL'}")

    # M1: m-terminal mean line_pos > 0.85 (C1486)
    m_toks = [t for t in corpus if t['term'] == 'm']
    m_mean_pos = sum(t['line_pos'] for t in m_toks) / len(m_toks) if m_toks else None
    m1 = {'test': 'M1', 'constraint': 'C1486', 'description': 'm-terminal mean line_pos > 0.85',
           'value': round(m_mean_pos, 4) if m_mean_pos else None, 'n': len(m_toks),
           'pass': m_mean_pos is not None and m_mean_pos > 0.85}
    results_a.append(m1)
    print(f"  M1: m-terminal mean line_pos = {m1['value']} (N={m1['n']}) {'PASS' if m1['pass'] else 'FAIL'}")

    # M2: m-terminal line_pos > 0.9 rate > 60% (C1486)
    m_late = safe_frac(m_toks, lambda t: t['line_pos'] > 0.9) if m_toks else None
    m2 = {'test': 'M2', 'constraint': 'C1486', 'description': 'm-terminal line_pos > 0.9 rate > 60%',
           'value': round(m_late, 4) if m_late else None,
           'pass': m_late is not None and m_late > 0.60}
    results_a.append(m2)
    print(f"  M2: m-terminal line_pos > 0.9 rate = {m2['value']} {'PASS' if m2['pass'] else 'FAIL'}")

    # R1-R4: Routing enrichments (C1563)
    adj_pairs = [(t['prev_term_same_line'], t['head'])
                 for t in corpus
                 if t['prev_term_same_line'] is not None and t['head'] is not None]
    pair_ct = Counter(adj_pairs)
    term_mg = Counter(p[0] for p in adj_pairs)
    head_mg = Counter(p[1] for p in adj_pairs)
    n_pairs = len(adj_pairs)

    def corpus_enr(term_val, head_val):
        obs = pair_ct.get((term_val, head_val), 0)
        tt = term_mg.get(term_val, 0)
        hh = head_mg.get(head_val, 0)
        if tt == 0 or n_pairs == 0:
            return None
        exp = tt * (hh / n_pairs)
        return obs / exp if exp > 0 else None

    for rid, (tv, hv, thresh) in enumerate([
        ('r', 'a', 1.8), ('y', 'k', 1.3), ('h', 't', 1.5), ('m', 'o', 1.3)
    ], 1):
        enr_val = corpus_enr(tv, hv)
        r = {'test': f'R{rid}', 'constraint': 'C1563',
             'description': f'{tv}->{hv} enrichment > {thresh}x',
             'value': round(enr_val, 3) if enr_val else None,
             'threshold': thresh,
             'pass': enr_val is not None and enr_val > thresh}
        results_a.append(r)
        print(f"  R{rid}: {tv}->{hv} = {r['value']}x (> {thresh}x) {'PASS' if r['pass'] else 'FAIL'}")

    a_pass = sum(1 for r in results_a if r['pass'])
    a_total = len(results_a)
    t2ba_pass = a_pass >= 10
    print(f"\n  T2bA: {a_pass}/{a_total} PASS (need >= 10) -> {'PASS' if t2ba_pass else 'FAIL'}")

    # ================================================================
    # T2bB: INSTRUMENT SANITY CHECKS (8 tests)
    # ================================================================
    print("\n" + "=" * 60)
    print("T2bB: INSTRUMENT SANITY CHECKS")
    print("=" * 60)

    # H1: Headless CLOSE rate > SPEC rate corpus-wide
    hl_toks = [t for t in corpus if t['domain'] == 'HEADLESS']
    hl_spec = safe_frac(hl_toks, lambda t: t['line_zone'] == 'SPEC')
    hl_close = safe_frac(hl_toks, lambda t: t['line_zone'] == 'CLOSE')
    h1 = {'test': 'H1', 'description': 'Headless CLOSE > SPEC rate',
           'spec': round(hl_spec, 4) if hl_spec else None,
           'close': round(hl_close, 4) if hl_close else None,
           'pass': hl_close is not None and hl_spec is not None and hl_close > hl_spec}
    results_b.append(h1)
    print(f"  H1: Headless SPEC={h1['spec']}, CLOSE={h1['close']} {'PASS' if h1['pass'] else 'FAIL'}")

    # P1: HEADER LOW-hazard enrichment > 1.0x (C1467)
    header_toks = [t for t in corpus if t['paragraph_zone'] == 'HEADER']
    header_low_rate = safe_frac(header_toks, lambda t: t['frame_hazard'] in ('LOW', 'ZERO') or t['is_safe_pathway'])
    overall_low_rate = safe_frac(corpus, lambda t: t['frame_hazard'] in ('LOW', 'ZERO') or t['is_safe_pathway'])
    p1_enr = header_low_rate / overall_low_rate if overall_low_rate and overall_low_rate > 0 and header_low_rate else None
    p1 = {'test': 'P1', 'description': 'HEADER LOW/ZERO enrichment > 1.0x (C1467)',
           'value': round(p1_enr, 4) if p1_enr else None,
           'pass': p1_enr is not None and p1_enr > 1.0}
    results_b.append(p1)
    print(f"  P1: HEADER LOW enrichment = {p1['value']} {'PASS' if p1['pass'] else 'FAIL'}")

    # P2: TAIL HIGH-hazard enrichment > 1.0x (C1467)
    tail_toks = [t for t in corpus if t['paragraph_zone'] == 'TAIL']
    tail_high_rate = safe_frac(tail_toks, lambda t: t['frame_hazard'] == 'HIGH')
    overall_high_rate = safe_frac(corpus, lambda t: t['frame_hazard'] == 'HIGH')
    p2_enr = tail_high_rate / overall_high_rate if overall_high_rate and overall_high_rate > 0 and tail_high_rate else None
    p2 = {'test': 'P2', 'description': 'TAIL HIGH enrichment > 1.0x (C1467)',
           'value': round(p2_enr, 4) if p2_enr else None,
           'pass': p2_enr is not None and p2_enr > 1.0}
    results_b.append(p2)
    print(f"  P2: TAIL HIGH enrichment = {p2['value']} {'PASS' if p2['pass'] else 'FAIL'}")

    # P3: Headless rate differs HEADER vs BODY
    body_toks = [t for t in corpus if t['paragraph_zone'] == 'BODY']
    header_hl = safe_frac(header_toks, lambda t: t['domain'] == 'HEADLESS')
    body_hl = safe_frac(body_toks, lambda t: t['domain'] == 'HEADLESS')
    p3_diff = abs(header_hl - body_hl) if header_hl is not None and body_hl is not None else None
    p3 = {'test': 'P3', 'description': 'Headless rate differs HEADER vs BODY (diff > 0.02)',
           'header_rate': round(header_hl, 4) if header_hl else None,
           'body_rate': round(body_hl, 4) if body_hl else None,
           'diff': round(p3_diff, 4) if p3_diff else None,
           'pass': p3_diff is not None and p3_diff > 0.02}
    results_b.append(p3)
    print(f"  P3: Headless HEADER={p3['header_rate']}, BODY={p3['body_rate']}, diff={p3['diff']} {'PASS' if p3['pass'] else 'FAIL'}")

    # P4: No paragraph ordering preference (C1399)
    # Test: rank correlation of paragraph dominant type with paragraph index, across folios
    import random
    by_folio = defaultdict(list)
    for t in corpus:
        by_folio[t['folio']].append(t)

    type_orders = []
    for fol, toks in by_folio.items():
        para_groups = defaultdict(list)
        for t in toks:
            para_groups[t['paragraph_idx']].append(t)
        if len(para_groups) < 3:
            continue
        # Dominant domain per paragraph
        for pi in sorted(para_groups.keys()):
            domain_cts = Counter(t['domain'] for t in para_groups[pi])
            if domain_cts:
                dominant = domain_cts.most_common(1)[0][0]
                thermal_frac = domain_cts.get('THERMAL', 0) / sum(domain_cts.values())
                type_orders.append((pi, thermal_frac))

    if len(type_orders) >= 20:
        # Spearman rank correlation of paragraph index vs thermal fraction
        n_ord = len(type_orders)
        xs = [x[0] for x in type_orders]
        ys = [x[1] for x in type_orders]
        x_rank = [sorted(xs).index(v) for v in xs]
        y_rank = [sorted(ys).index(v) for v in ys]
        mean_xr = sum(x_rank) / n_ord
        mean_yr = sum(y_rank) / n_ord
        num = sum((x_rank[i] - mean_xr) * (y_rank[i] - mean_yr) for i in range(n_ord))
        den_x = sum((x_rank[i] - mean_xr) ** 2 for i in range(n_ord))
        den_y = sum((y_rank[i] - mean_yr) ** 2 for i in range(n_ord))
        rho = num / math.sqrt(den_x * den_y) if den_x > 0 and den_y > 0 else 0
        p4_pass = abs(rho) < 0.15  # Weak/no ordering
    else:
        rho = None
        p4_pass = False
    p4 = {'test': 'P4', 'description': 'No paragraph ordering preference (|rho| < 0.15, C1399)',
           'rho': round(rho, 4) if rho is not None else None,
           'pass': p4_pass}
    results_b.append(p4)
    print(f"  P4: Para ordering rho = {p4['rho']} {'PASS' if p4['pass'] else 'FAIL'}")

    # CL1: Q4 OPAQUE terminal rate > Q1-Q3 OPAQUE rate
    q4_toks = [t for t in corpus if t['quintile'] == 4]
    q13_toks = [t for t in corpus if t['quintile'] in (1, 2, 3)]
    q4_opaque = safe_frac(q4_toks, lambda t: t['term'] in OPAQUE_TERMS)
    q13_opaque = safe_frac(q13_toks, lambda t: t['term'] in OPAQUE_TERMS)
    cl1 = {'test': 'CL1', 'description': 'Q4 OPAQUE terminal rate > Q1-Q3 rate',
            'q4': round(q4_opaque, 4) if q4_opaque else None,
            'q13': round(q13_opaque, 4) if q13_opaque else None,
            'pass': q4_opaque is not None and q13_opaque is not None and q4_opaque > q13_opaque}
    results_b.append(cl1)
    print(f"  CL1: Q4 OPAQUE={cl1['q4']}, Q1-Q3 OPAQUE={cl1['q13']} {'PASS' if cl1['pass'] else 'FAIL'}")

    # CL2: Q3->Q4 HEAD JSD > Q2->Q3 HEAD JSD corpus-wide
    q2_toks = [t for t in corpus if t['quintile'] == 2]
    q3_toks = [t for t in corpus if t['quintile'] == 3]
    q2_heads = Counter(t['head'] if t['head'] else 'NONE' for t in q2_toks)
    q3_heads = Counter(t['head'] if t['head'] else 'NONE' for t in q3_toks)
    q4_heads = Counter(t['head'] if t['head'] else 'NONE' for t in q4_toks)
    jsd_23 = jsd(q2_heads, q3_heads)
    jsd_34 = jsd(q3_heads, q4_heads)
    cl2 = {'test': 'CL2', 'description': 'Q3->Q4 HEAD JSD > Q2->Q3 HEAD JSD',
            'jsd_q2q3': round(jsd_23, 6), 'jsd_q3q4': round(jsd_34, 6),
            'ratio': round(jsd_34 / jsd_23, 2) if jsd_23 > 0 else None,
            'pass': jsd_34 > jsd_23}
    results_b.append(cl2)
    print(f"  CL2: JSD Q2-Q3={cl2['jsd_q2q3']}, Q3-Q4={cl2['jsd_q3q4']}, ratio={cl2['ratio']} {'PASS' if cl2['pass'] else 'FAIL'}")

    # CL3: m-terminal type diversity <= 15 (C1434)
    m_middles = set(t['middle'] for t in m_toks)
    cl3 = {'test': 'CL3', 'description': 'm-terminal type diversity <= 15 (C1434)',
            'n_types': len(m_middles),
            'pass': len(m_middles) <= 15}
    results_b.append(cl3)
    print(f"  CL3: m-terminal unique MIDDLEs = {cl3['n_types']} {'PASS' if cl3['pass'] else 'FAIL'}")

    b_pass = sum(1 for r in results_b if r['pass'])
    b_total = len(results_b)
    t2bb_pass = b_pass >= 6
    print(f"\n  T2bB: {b_pass}/{b_total} PASS (need >= 6) -> {'PASS' if t2bb_pass else 'FAIL'}")

    # ================================================================
    # OUTPUT
    # ================================================================
    output = {
        'metadata': {
            'phase': '560b',
            'task': 'T2b_constraint_validation',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        },
        'T2bA': {
            'tests': results_a,
            'pass_count': a_pass,
            'total': a_total,
            'threshold': 10,
            'pass': t2ba_pass,
        },
        'T2bB': {
            'tests': results_b,
            'pass_count': b_pass,
            'total': b_total,
            'threshold': 6,
            'pass': t2bb_pass,
        },
        'overall_pass': t2ba_pass and t2bb_pass,
    }

    out_path = RESULTS_DIR / 't2b_constraint_validation.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")

    print(f"\n{'='*60}")
    print(f"T2b SUMMARY: T2bA {a_pass}/{a_total}, T2bB {b_pass}/{b_total}")
    print(f"Overall: {'PASS' if output['overall_pass'] else 'FAIL'}")
    print(f"Runtime: {time.time()-t_start:.1f}s")


if __name__ == '__main__':
    main()
