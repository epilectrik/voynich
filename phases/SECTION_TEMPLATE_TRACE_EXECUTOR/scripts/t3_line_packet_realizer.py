"""Phase 562 T3: Line Packet Realizer

Computes 15D continuous line profiles for each qualifying line (>=5 tokens)
and builds per-folio line packet inventories with packet state descriptors.

Per-line profile (15D continuous vector):
  0  head_k_frac         k-HEAD fraction
  1  head_t_frac         t-HEAD fraction
  2  head_a_frac         a-HEAD fraction
  3  head_e_frac         e-HEAD fraction
  4  head_o_frac         o-HEAD fraction
  5  headless_frac       HEADLESS fraction
  6  hazard_high_frac    HIGH-hazard fraction
  7  hazard_zero_frac    ZERO-hazard fraction (includes IMMUNE)
  8  q4_shift            Euclidean dist between Q1-Q3 mean domain dist and Q4
  9  close_m_rate        m-terminal fraction at Q4 (last quintile)
  10 safe_pathway_frac   safe pathway fraction
  11 k_q1_peak           k-HEAD at Q1 minus mean k-HEAD at Q2-Q4
  12 q0q4_hazard_slope   HIGH-hazard at Q4 minus ZERO-hazard at Q0
  13 routing_match_rate  C1563 routing match fraction
  14 q4_opaque_rate      OPAQUE-terminal fraction at Q4

Packet state descriptors per line:
  - packet_phase:       SPEC / WORK / CLOSE
  - hazard_envelope:    SAFE_OPEN / THERMAL_INTERIOR / DANGEROUS_CLOSE
  - closure_armed:      bool (q4_opaque > section median)
  - q4_shift_strength:  float (same as q4_shift feature)
  - close_opacity_bias: q4_opaque / mean_opaque across line
  - m_close_bias:       close_m_rate / section mean close_m_rate

Input:
  phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t1_domain_decomposition.json
  phases/SECTION_TEMPLATE_TRACE_EXECUTOR/results/t1_section_templates.json

Output:
  phases/SECTION_TEMPLATE_TRACE_EXECUTOR/results/t3_line_packets.json
"""
import json
import math
import time
import sys
from pathlib import Path
from collections import Counter, defaultdict

# ===================================================================
# Constants
# ===================================================================

DOMAINS = ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']
DOMAIN_ORDER = {d: i for i, d in enumerate(DOMAINS)}

HEADS = ['k', 't', 'a', 'e', 'o']

PRIMARY_ROUTE = {
    'r': 'ACTIVE',
    'y': 'THERMAL',
    'h': 'FLOW',
    'm': 'ARRANGEMENT',
    'n': 'ACTIVE',
    'l': 'STABILITY',
    'bare': 'NEUTRAL',
}

FEATURE_NAMES = [
    'head_k_frac', 'head_t_frac', 'head_a_frac', 'head_e_frac', 'head_o_frac',
    'headless_frac',
    'hazard_high_frac', 'hazard_zero_frac',
    'q4_shift', 'close_m_rate', 'safe_pathway_frac',
    'k_q1_peak', 'q0q4_hazard_slope',
    'routing_match_rate', 'q4_opaque_rate',
]

MIN_LINE_TOKENS = 5


# ===================================================================
# Hazard posture derivation (same as T1)
# ===================================================================

def derive_hazard_posture(token):
    """Derive hazard posture from token composition using Tier 2 rules."""
    if token.get('head') == 'k':
        return 'IMMUNE'
    if token.get('head') == 'e' and token.get('term') == 'y':
        return 'ZERO'
    if token.get('head') == 'a' and (token.get('i_count') or 0) >= 2:
        return 'ZERO'
    if token.get('has_quenching_mod') and token.get('head') in ('e', 'o', 't'):
        return 'ZERO'
    if token.get('is_safe_pathway'):
        return 'ZERO'
    if token.get('head') == 'a' and token.get('term') in ('l', 'r'):
        return 'HIGH'
    if not token.get('source_immune') and token.get('frame_hazard') == 'HIGH':
        return 'HIGH'
    return 'LOW'


# ===================================================================
# JSD utility
# ===================================================================

def jsd(p_vec, q_vec):
    """Jensen-Shannon divergence between two distributions (as lists)."""
    n = len(p_vec)
    m_vec = [(p_vec[i] + q_vec[i]) / 2.0 for i in range(n)]
    div = 0.0
    for i in range(n):
        if p_vec[i] > 0 and m_vec[i] > 0:
            div += p_vec[i] * math.log2(p_vec[i] / m_vec[i])
        if q_vec[i] > 0 and m_vec[i] > 0:
            div += q_vec[i] * math.log2(q_vec[i] / m_vec[i])
    return div / 2.0


# ===================================================================
# Per-line 15D profile computation
# ===================================================================

def compute_line_profile(tokens):
    """Compute the 15D continuous profile for a single qualifying line.

    Args:
        tokens: list of token dicts for this line (already filtered, >=5 tokens)

    Returns:
        list of 15 floats
    """
    n = len(tokens)

    # ------ Features 0-5: HEAD fracs ------
    head_counts = Counter(t.get('head') for t in tokens)
    head_k = head_counts.get('k', 0) / n
    head_t = head_counts.get('t', 0) / n
    head_a = head_counts.get('a', 0) / n
    head_e = head_counts.get('e', 0) / n
    head_o = head_counts.get('o', 0) / n
    # HEADLESS = domain == 'HEADLESS' (head is None)
    headless = sum(1 for t in tokens if t.get('domain') == 'HEADLESS') / n

    # ------ Features 6-7: Hazard fracs ------
    hazards = [derive_hazard_posture(t) for t in tokens]
    hazard_counter = Counter(hazards)
    hazard_high = hazard_counter.get('HIGH', 0) / n
    # ZERO includes both ZERO and IMMUNE
    hazard_zero = (hazard_counter.get('ZERO', 0) +
                   hazard_counter.get('IMMUNE', 0)) / n

    # ------ Feature 8: q4_shift ------
    # Partition tokens by quintile
    quintile_tokens = defaultdict(list)
    for t in tokens:
        q = t.get('quintile', 2)
        quintile_tokens[q].append(t)

    # Domain distribution per quintile
    def domain_dist(tok_list):
        if not tok_list:
            return [1.0 / 6] * 6
        c = Counter(t['domain'] for t in tok_list)
        total = len(tok_list)
        return [c.get(d, 0) / total for d in DOMAINS]

    q_dists = {q: domain_dist(quintile_tokens[q]) for q in range(5)}

    # Q1-Q3 mean domain dist
    q13_tokens = []
    for q in [1, 2, 3]:
        q13_tokens.extend(quintile_tokens[q])
    q13_dist = domain_dist(q13_tokens)

    q4_dist = q_dists[4]

    # Euclidean distance between Q1-Q3 mean and Q4
    q4_shift = math.sqrt(sum((q4_dist[i] - q13_dist[i]) ** 2 for i in range(6)))

    # ------ Feature 9: close_m_rate ------
    # m-terminal fraction at Q4
    q4_toks = quintile_tokens[4]
    if q4_toks:
        close_m = sum(1 for t in q4_toks if t.get('term') == 'm') / len(q4_toks)
    else:
        close_m = 0.0

    # ------ Feature 10: safe_pathway_frac ------
    safe_frac = sum(1 for t in tokens if t.get('is_safe_pathway')) / n

    # ------ Feature 11: k_q1_peak ------
    # k-HEAD at Q1 minus mean k-HEAD at Q2-Q4
    q1_toks = quintile_tokens[1]
    if q1_toks:
        k_q1 = sum(1 for t in q1_toks if t.get('head') == 'k') / len(q1_toks)
    else:
        k_q1 = 0.0

    q234_toks = []
    for q in [2, 3, 4]:
        q234_toks.extend(quintile_tokens[q])
    if q234_toks:
        k_q234 = sum(1 for t in q234_toks if t.get('head') == 'k') / len(q234_toks)
    else:
        k_q234 = 0.0

    k_q1_peak = k_q1 - k_q234

    # ------ Feature 12: q0q4_hazard_slope ------
    # HIGH-hazard at Q4 minus ZERO-hazard at Q0
    q4_hazards = Counter(derive_hazard_posture(t) for t in quintile_tokens[4])
    q0_hazards = Counter(derive_hazard_posture(t) for t in quintile_tokens[0])

    q4_n = len(quintile_tokens[4]) or 1
    q0_n = len(quintile_tokens[0]) or 1

    q4_high = q4_hazards.get('HIGH', 0) / q4_n
    q0_zero = (q0_hazards.get('ZERO', 0) + q0_hazards.get('IMMUNE', 0)) / q0_n

    q0q4_slope = q4_high - q0_zero

    # ------ Feature 13: routing_match_rate ------
    # A routing match: prev token's terminal maps via PRIMARY_ROUTE to current
    # token's domain
    matches = 0
    pair_count = 0
    for t in tokens:
        prev_term = t.get('prev_term_same_line')
        if prev_term is None:
            continue  # first token on line
        pair_count += 1
        route_target = PRIMARY_ROUTE.get(prev_term)
        if route_target is None:
            continue
        # NEUTRAL matches nothing specific
        if route_target == 'NEUTRAL':
            continue
        if route_target == t.get('domain'):
            matches += 1

    routing_match = matches / max(pair_count, 1)

    # ------ Feature 14: q4_opaque_rate ------
    if q4_toks:
        q4_opaque = sum(1 for t in q4_toks
                        if t.get('terminal_opacity') == 'OPAQUE') / len(q4_toks)
    else:
        q4_opaque = 0.0

    return [
        head_k, head_t, head_a, head_e, head_o,
        headless,
        hazard_high, hazard_zero,
        q4_shift, close_m, safe_frac,
        k_q1_peak, q0q4_slope,
        routing_match, q4_opaque,
    ]


# ===================================================================
# Packet state descriptors
# ===================================================================

def derive_packet_phase(tokens):
    """Determine packet_phase: SPEC, WORK, or CLOSE.

    Find which quintile has the most headed tokens (head != None).
    Q0/Q1 peak -> SPEC, Q3/Q4 peak -> CLOSE, else WORK.
    """
    quintile_headed_counts = Counter()
    for t in tokens:
        if t.get('head') is not None:
            q = t.get('quintile', 2)
            quintile_headed_counts[q] += 1

    if not quintile_headed_counts:
        return 'WORK'

    # Find quintile with peak headed count
    peak_q = max(quintile_headed_counts, key=quintile_headed_counts.get)
    peak_count = quintile_headed_counts[peak_q]

    # Check for ties or near-uniform distribution
    total_headed = sum(quintile_headed_counts.values())
    if total_headed > 0 and peak_count / total_headed < 0.25:
        # Very little quintile variation -> default WORK
        return 'WORK'

    if peak_q in (0, 1):
        return 'SPEC'
    elif peak_q in (3, 4):
        return 'CLOSE'
    else:
        return 'WORK'


def derive_hazard_envelope(hazard_zero_frac, hazard_high_frac, close_m_rate):
    """Determine hazard_envelope. NOT mutually exclusive; apply in order."""
    if hazard_zero_frac > 0.7:
        return 'SAFE_OPEN'
    elif hazard_high_frac < 0.15:
        return 'THERMAL_INTERIOR'
    elif hazard_high_frac > 0.3 and close_m_rate > 0.1:
        return 'DANGEROUS_CLOSE'
    else:
        return 'THERMAL_INTERIOR'


# ===================================================================
# Main
# ===================================================================

def main():
    t0 = time.time()
    print("=== Phase 562 T3: Line Packet Realizer ===")

    # ---------------------------------------------------------------
    # Load inputs
    # ---------------------------------------------------------------
    phases_root = Path(__file__).resolve().parents[2]

    corpus_path = (phases_root / 'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL' /
                   'results' / 't1_domain_decomposition.json')
    templates_path = (phases_root / 'SECTION_TEMPLATE_TRACE_EXECUTOR' /
                      'results' / 't1_section_templates.json')

    print(f"  Loading corpus from {corpus_path}...")
    with open(corpus_path) as f:
        corpus_data = json.load(f)
    corpus = corpus_data['corpus_tokens']
    print(f"  Loaded {len(corpus)} tokens")

    print(f"  Loading section templates from {templates_path}...")
    with open(templates_path) as f:
        templates_data = json.load(f)
    templates = templates_data['templates']
    print(f"  Loaded templates for sections: {list(templates.keys())}")

    # ---------------------------------------------------------------
    # Step 1: Group tokens by (folio, line)
    # ---------------------------------------------------------------
    print("  Grouping tokens by (folio, line)...")
    line_groups = defaultdict(list)
    for tok in corpus:
        key = (tok['folio'], tok['line'])
        line_groups[key].append(tok)

    total_lines = len(line_groups)
    qualifying_lines = {k: v for k, v in line_groups.items()
                        if len(v) >= MIN_LINE_TOKENS}
    print(f"  Total lines: {total_lines}")
    print(f"  Qualifying lines (>={MIN_LINE_TOKENS} tokens): {len(qualifying_lines)}")

    # ---------------------------------------------------------------
    # Step 2: Compute 15D profiles for all qualifying lines
    # ---------------------------------------------------------------
    print("  Computing 15D line profiles...")
    line_packets = {}

    for (folio, line), tokens in qualifying_lines.items():
        # Sort tokens by line_pos to ensure ordering
        tokens.sort(key=lambda t: t.get('line_pos', 0.0))

        # Determine section and paragraph_idx from first token
        section = tokens[0].get('section', '?')
        paragraph_idx = tokens[0].get('paragraph_idx', 0)

        profile = compute_line_profile(tokens)
        key = f"{folio}|{line}"
        line_packets[key] = {
            'folio': folio,
            'line': line,
            'section': section,
            'paragraph_idx': paragraph_idx,
            'n_tokens': len(tokens),
            'profile': [round(v, 5) for v in profile],
            'packet_state': None,  # filled in step 3
        }

    print(f"  Computed profiles for {len(line_packets)} lines")

    # ---------------------------------------------------------------
    # Step 3: Compute packet state descriptors
    # ---------------------------------------------------------------
    print("  Computing packet state descriptors...")

    # 3a: Compute per-section median q4_opaque_rate for closure_armed
    section_q4_opaque = defaultdict(list)
    for key, pkt in line_packets.items():
        section_q4_opaque[pkt['section']].append(pkt['profile'][14])

    section_median_q4_opaque = {}
    for sec, values in section_q4_opaque.items():
        sv = sorted(values)
        n = len(sv)
        if n % 2 == 0:
            section_median_q4_opaque[sec] = (sv[n // 2 - 1] + sv[n // 2]) / 2
        else:
            section_median_q4_opaque[sec] = sv[n // 2]

    print("  Section median q4_opaque_rate:")
    for sec, med in sorted(section_median_q4_opaque.items()):
        print(f"    {sec}: {med:.4f} (n={len(section_q4_opaque[sec])})")

    # 3b: Compute per-section mean close_m_rate for m_close_bias
    section_close_m = defaultdict(list)
    for key, pkt in line_packets.items():
        section_close_m[pkt['section']].append(pkt['profile'][9])

    section_mean_close_m = {}
    for sec, values in section_close_m.items():
        section_mean_close_m[sec] = sum(values) / len(values) if values else 0.0

    # 3c: Apply descriptors
    for (folio, line), tokens in qualifying_lines.items():
        key = f"{folio}|{line}"
        pkt = line_packets[key]
        prof = pkt['profile']
        section = pkt['section']

        # Extract features by index
        hazard_high_frac = prof[6]
        hazard_zero_frac = prof[7]
        close_m_rate = prof[9]
        q4_shift = prof[8]
        q4_opaque_rate = prof[14]

        # packet_phase
        tokens.sort(key=lambda t: t.get('line_pos', 0.0))
        packet_phase = derive_packet_phase(tokens)

        # hazard_envelope
        hazard_envelope = derive_hazard_envelope(
            hazard_zero_frac, hazard_high_frac, close_m_rate)

        # closure_armed
        sec_med = section_median_q4_opaque.get(section, 0.0)
        closure_armed = q4_opaque_rate > sec_med

        # q4_shift_strength
        q4_shift_strength = q4_shift

        # close_opacity_bias = q4_opaque / mean_opaque across whole line
        # Mean opaque rate across the whole line (all quintiles)
        n_total = pkt['n_tokens']
        n_opaque_all = sum(1 for t in tokens
                           if t.get('terminal_opacity') == 'OPAQUE')
        mean_opaque_line = n_opaque_all / max(n_total, 1)
        close_opacity_bias = q4_opaque_rate / max(mean_opaque_line, 0.01)

        # m_close_bias = close_m_rate / section_mean_close_m_rate
        sec_mean_cm = section_mean_close_m.get(section, 0.01)
        m_close_bias = close_m_rate / max(sec_mean_cm, 0.01)

        pkt['packet_state'] = {
            'packet_phase': packet_phase,
            'hazard_envelope': hazard_envelope,
            'closure_armed': bool(closure_armed),
            'q4_shift_strength': round(q4_shift_strength, 5),
            'close_opacity_bias': round(close_opacity_bias, 4),
            'm_close_bias': round(m_close_bias, 4),
        }

    print(f"  Packet states assigned for {len(line_packets)} lines")

    # ---------------------------------------------------------------
    # Step 4: Build per-folio line packet inventories
    # ---------------------------------------------------------------
    print("  Building per-folio inventories...")
    folio_packets = defaultdict(list)
    for key, pkt in line_packets.items():
        folio_packets[pkt['folio']].append(pkt)

    folio_inventories = {}
    for folio, pkts in sorted(folio_packets.items()):
        n_qual = len(pkts)

        # Mean and std of 15D profiles
        profiles = [p['profile'] for p in pkts]
        mean_profile = [0.0] * 15
        for prof in profiles:
            for i in range(15):
                mean_profile[i] += prof[i]
        mean_profile = [m / n_qual for m in mean_profile]

        std_profile = [0.0] * 15
        if n_qual > 1:
            for prof in profiles:
                for i in range(15):
                    std_profile[i] += (prof[i] - mean_profile[i]) ** 2
            std_profile = [math.sqrt(s / (n_qual - 1)) for s in std_profile]

        # Packet phase distribution
        phase_counter = Counter(p['packet_state']['packet_phase'] for p in pkts)
        phase_dist = {ph: round(phase_counter.get(ph, 0) / n_qual, 4)
                      for ph in ['SPEC', 'WORK', 'CLOSE']}

        # Hazard envelope distribution
        env_counter = Counter(p['packet_state']['hazard_envelope'] for p in pkts)
        env_labels = ['SAFE_OPEN', 'THERMAL_INTERIOR', 'DANGEROUS_CLOSE']
        env_dist = {e: round(env_counter.get(e, 0) / n_qual, 4)
                    for e in env_labels}

        # Closure armed rate
        armed_count = sum(1 for p in pkts if p['packet_state']['closure_armed'])
        closure_armed_rate = round(armed_count / n_qual, 4)

        folio_inventories[folio] = {
            'n_qualifying_lines': n_qual,
            'mean_profile': [round(v, 5) for v in mean_profile],
            'std_profile': [round(v, 5) for v in std_profile],
            'packet_phase_dist': phase_dist,
            'hazard_envelope_dist': env_dist,
            'closure_armed_rate': closure_armed_rate,
        }

    print(f"  Built inventories for {len(folio_inventories)} folios")

    # ---------------------------------------------------------------
    # Step 5: Validation
    # ---------------------------------------------------------------
    print("\n=== Validation ===")
    validations = {}
    all_pass = True

    # V1: >= 2000 qualifying lines
    v1 = len(line_packets) >= 2000
    validations['min_qualifying_lines'] = {
        'pass': v1,
        'n_qualifying': len(line_packets),
        'threshold': 2000,
    }
    print(f"  V1: >= 2000 qualifying lines: {len(line_packets)} -> "
          f"{'PASS' if v1 else 'FAIL'}")
    if not v1:
        all_pass = False

    # V2: Q4 opaque > Q0-Q3 opaque (pooled across all qualifying lines)
    q4_opaque_pool = 0
    q4_total_pool = 0
    q03_opaque_pool = 0
    q03_total_pool = 0

    for (folio, line), tokens in qualifying_lines.items():
        for t in tokens:
            q = t.get('quintile', 2)
            is_opaque = 1 if t.get('terminal_opacity') == 'OPAQUE' else 0
            if q == 4:
                q4_opaque_pool += is_opaque
                q4_total_pool += 1
            else:
                q03_opaque_pool += is_opaque
                q03_total_pool += 1

    q4_opaque_rate_pool = q4_opaque_pool / max(q4_total_pool, 1)
    q03_opaque_rate_pool = q03_opaque_pool / max(q03_total_pool, 1)
    v2 = q4_opaque_rate_pool > q03_opaque_rate_pool
    validations['q4_opaque_gt_q03'] = {
        'pass': v2,
        'q4_opaque_rate': round(q4_opaque_rate_pool, 5),
        'q03_opaque_rate': round(q03_opaque_rate_pool, 5),
    }
    print(f"  V2: Q4 opaque ({q4_opaque_rate_pool:.4f}) > Q0-Q3 opaque "
          f"({q03_opaque_rate_pool:.4f}) -> {'PASS' if v2 else 'FAIL'}")
    if not v2:
        all_pass = False

    # V3: Q3->Q4 HEAD JSD >> Q2->Q3 HEAD JSD (replicating C1566)
    # Compute pooled quintile domain distributions from qualifying lines
    quintile_domain_pool = defaultdict(lambda: Counter())
    quintile_n_pool = Counter()
    for (folio, line), tokens in qualifying_lines.items():
        for t in tokens:
            q = t.get('quintile', 2)
            quintile_domain_pool[q][t['domain']] += 1
            quintile_n_pool[q] += 1

    def pool_dist(q):
        total = quintile_n_pool[q]
        if total == 0:
            return [1.0 / 6] * 6
        c = quintile_domain_pool[q]
        return [c.get(d, 0) / total for d in DOMAINS]

    q2_dist = pool_dist(2)
    q3_dist = pool_dist(3)
    q4_dist_pool = pool_dist(4)

    jsd_q3q4 = jsd(q3_dist, q4_dist_pool)
    jsd_q2q3 = jsd(q2_dist, q3_dist)

    v3 = jsd_q3q4 > jsd_q2q3
    validations['q3q4_jsd_gt_q2q3'] = {
        'pass': v3,
        'q3q4_jsd': round(jsd_q3q4, 6),
        'q2q3_jsd': round(jsd_q2q3, 6),
        'ratio': round(jsd_q3q4 / max(jsd_q2q3, 1e-9), 3),
    }
    print(f"  V3: Q3->Q4 JSD ({jsd_q3q4:.5f}) > Q2->Q3 JSD "
          f"({jsd_q2q3:.5f}), ratio={jsd_q3q4 / max(jsd_q2q3, 1e-9):.2f}x -> "
          f"{'PASS' if v3 else 'FAIL'}")
    if not v3:
        all_pass = False

    # V4: Packet state descriptors populated for all qualifying lines
    missing_states = sum(1 for pkt in line_packets.values()
                         if pkt['packet_state'] is None)
    v4 = missing_states == 0
    validations['all_states_populated'] = {
        'pass': v4,
        'missing': missing_states,
    }
    print(f"  V4: All states populated: {missing_states} missing -> "
          f"{'PASS' if v4 else 'FAIL'}")
    if not v4:
        all_pass = False

    print(f"\n  Overall validation: {'PASS' if all_pass else 'FAIL'}")

    # ---------------------------------------------------------------
    # Step 6: Summary statistics
    # ---------------------------------------------------------------
    print("\n=== Summary ===")

    # Packet phase distribution (global)
    global_phase = Counter(p['packet_state']['packet_phase']
                           for p in line_packets.values())
    total_pkts = len(line_packets)
    print(f"  Packet phase distribution (n={total_pkts}):")
    for ph in ['SPEC', 'WORK', 'CLOSE']:
        cnt = global_phase.get(ph, 0)
        print(f"    {ph}: {cnt} ({cnt / total_pkts:.3f})")

    # Hazard envelope distribution (global)
    global_env = Counter(p['packet_state']['hazard_envelope']
                         for p in line_packets.values())
    print(f"  Hazard envelope distribution:")
    for env in ['SAFE_OPEN', 'THERMAL_INTERIOR', 'DANGEROUS_CLOSE']:
        cnt = global_env.get(env, 0)
        print(f"    {env}: {cnt} ({cnt / total_pkts:.3f})")

    # Closure armed rate (global)
    armed_total = sum(1 for p in line_packets.values()
                      if p['packet_state']['closure_armed'])
    print(f"  Closure armed rate: {armed_total}/{total_pkts} "
          f"({armed_total / total_pkts:.3f})")

    # Per-section summary
    section_lines = defaultdict(list)
    for pkt in line_packets.values():
        section_lines[pkt['section']].append(pkt)

    print(f"\n  Per-section breakdown:")
    for sec in sorted(section_lines.keys()):
        pkts = section_lines[sec]
        ns = len(pkts)
        sec_phase = Counter(p['packet_state']['packet_phase'] for p in pkts)
        sec_env = Counter(p['packet_state']['hazard_envelope'] for p in pkts)
        sec_armed = sum(1 for p in pkts if p['packet_state']['closure_armed'])

        mean_prof = [0.0] * 15
        for p in pkts:
            for i in range(15):
                mean_prof[i] += p['profile'][i]
        mean_prof = [m / ns for m in mean_prof]

        print(f"    Section {sec} ({ns} lines):")
        print(f"      Phase: " + " ".join(
            f"{ph}={sec_phase.get(ph, 0)}" for ph in ['SPEC', 'WORK', 'CLOSE']))
        print(f"      Envelope: " + " ".join(
            f"{e}={sec_env.get(e, 0)}"
            for e in ['SAFE_OPEN', 'THERMAL_INTERIOR', 'DANGEROUS_CLOSE']))
        print(f"      Armed: {sec_armed}/{ns} ({sec_armed / ns:.3f})")
        print(f"      Mean profile [k,t,a,e,o,hl]: "
              + " ".join(f"{v:.3f}" for v in mean_prof[:6]))
        print(f"      Mean profile [hzH,hzZ,q4s,cm,sp]: "
              + " ".join(f"{v:.3f}" for v in mean_prof[6:11]))
        print(f"      Mean profile [kq1,slope,route,q4op]: "
              + " ".join(f"{v:.3f}" for v in mean_prof[11:15]))

    # Folio count summary
    print(f"\n  Folio inventories: {len(folio_inventories)}")
    folio_sizes = [inv['n_qualifying_lines']
                   for inv in folio_inventories.values()]
    if folio_sizes:
        print(f"    Lines/folio: min={min(folio_sizes)}, "
              f"max={max(folio_sizes)}, "
              f"mean={sum(folio_sizes) / len(folio_sizes):.1f}")

    # ---------------------------------------------------------------
    # Step 7: Save output
    # ---------------------------------------------------------------
    output = {
        'metadata': {
            'phase': '562',
            'task': 'T3_line_packet_realizer',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'corpus_path': str(corpus_path),
            'templates_path': str(templates_path),
            'n_corpus_tokens': len(corpus),
            'n_total_lines': total_lines,
            'n_qualifying_lines': len(line_packets),
            'min_line_tokens': MIN_LINE_TOKENS,
        },
        'line_packets': line_packets,
        'folio_inventories': folio_inventories,
        'feature_names': FEATURE_NAMES,
        'validations': validations,
        'validation_pass': all_pass,
    }

    out_path = (Path(__file__).resolve().parent.parent / 'results' /
                't3_line_packets.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n  Writing to {out_path}...")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    import os
    size_kb = os.path.getsize(out_path) / 1024
    elapsed = time.time() - t0
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\n=== T3 Complete (validation: {'PASS' if all_pass else 'FAIL'}) ===")

    if not all_pass:
        sys.exit(1)


if __name__ == '__main__':
    main()
