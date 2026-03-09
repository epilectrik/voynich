"""
T2: Trace to Supervisory Interface
===================================
Phase 563 — VIRTUAL_APPARATUS_COUPLING

Converts Phase 560/562/562b per-token data into apparatus-facing supervisory
signals using a two-stage architecture: supervisory intent -> plant legality filter.

Stage 1: Each token produces a supervisory intent vector based on its domain.
Stage 2: Four multiplicative gating layers (phase, hazard posture, envelope, CTS)
         modulate the intent into final contributions.

Routing effects (C1563) modify the next token's permissions based on
the previous token's terminal atom.

Input files:
  - t1_domain_decomposition.json  (23,096 tokens with domain, frame, etc.)
  - t3_line_packets.json          (line-level packet_phase, hazard_envelope)
  - t7_closure_cts.json           (CTS per line)
  - t2_folio_budgets.json         (folio headless regime / hl_rate)

Output:
  - t2_supervisory_interface.json (per-token supervisory contributions)
"""

import json
import time
import math
from pathlib import Path
from collections import defaultdict

# ── Paths ────────────────────────────────────────────────────────────────────

BASE = Path(__file__).resolve().parent.parent.parent
DOMAIN_INPUT = BASE / "WITHIN_DOMAIN_COMPOSITIONAL_CONTROL" / "results" / "t1_domain_decomposition.json"
PACKETS_INPUT = BASE / "SECTION_TEMPLATE_TRACE_EXECUTOR" / "results" / "t3_line_packets.json"
CTS_INPUT = BASE / "SECTION_TEMPLATE_TRACE_EXECUTOR" / "results" / "t7_closure_cts.json"
BUDGETS_INPUT = BASE / "SECTION_TEMPLATE_TRACE_EXECUTOR" / "results" / "t2_folio_budgets.json"
OUTPUT = Path(__file__).resolve().parent.parent / "results" / "t2_supervisory_interface.json"

# ── Constants ────────────────────────────────────────────────────────────────

STATE_VARS = ['T', 'RC', 'S', 'C', 'TR', 'X', 'Y']
SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}
BASE_STEP = 0.05

# ── Stage 1: Domain Intent Maps ──────────────────────────────────────────────

DOMAIN_INTENT = {
    'THERMAL': {
        'T':  {'permission': 0.9, 'direction': +1},
        'RC': {'permission': 0.2, 'direction': +1},
        'S':  {'permission': 0.1, 'direction': -1},
        'C':  {'permission': 0.1, 'direction': +1},
        'X':  {'permission': 0.3, 'direction': +1},
        'Y':  {'permission': 0.1, 'direction': +1},
    },
    'FLOW': {
        'TR': {'permission': 0.9, 'direction': +1},
        'RC': {'permission': 0.6, 'direction': +1},
        'S':  {'permission': 0.1, 'direction': +1},
        'C':  {'permission': 0.1, 'direction': -1},
        'Y':  {'permission': 0.3, 'direction': +1},
    },
    'ACTIVE': {
        'X':  {'permission': 0.9, 'direction': +1},
        'T':  {'permission': 0.2, 'direction': +1},
        'S':  {'permission': 0.2, 'direction': -1},
        'C':  {'permission': 0.2, 'direction': +1},
        'Y':  {'permission': 0.1, 'direction': +1},
    },
    'STABILITY': {
        'S':  {'permission': 0.9, 'direction': +1},
        'T':  {'permission': 0.4, 'direction': -1},
        'X':  {'permission': 0.3, 'direction': -1},
        'C':  {'permission': 0.1, 'direction': -1},
        'Y':  {'permission': 0.1, 'direction': +1},
    },
    'ARRANGEMENT': {
        'C':  {'permission': 0.8, 'direction': +1},
        'TR': {'permission': 0.2, 'direction': -1},
        'S':  {'permission': 0.2, 'direction': +1},
        'RC': {'permission': 0.2, 'direction': -1},
        'Y':  {'permission': 0.1, 'direction': +1},
    },
    'HEADLESS': None,  # handled by headless_intent()
}

# ── Stage 2: Gating Layers ──────────────────────────────────────────────────

# Gate 1: Packet Phase Admissibility
PHASE_ADMISSIBILITY = {
    'SPEC':  {'T': 0.5, 'RC': 0.3, 'S': 1.0, 'C': 0.3, 'TR': 0.3, 'X': 0.3, 'Y': 0.2},
    'WORK':  {'T': 1.0, 'RC': 1.0, 'S': 1.0, 'C': 1.0, 'TR': 1.0, 'X': 1.0, 'Y': 1.0},
    'CLOSE': {'T': 0.4, 'RC': 0.4, 'S': 1.3, 'C': 1.3, 'TR': 0.4, 'X': 0.2, 'Y': 1.3},
}

# Gate 2: Hazard Posture Priority
HAZARD_PRIORITY = {
    'IMMUNE': {'T': 1.2, 'RC': 1.0, 'S': 1.0, 'C': 1.0, 'TR': 1.0, 'X': 0.5, 'Y': 1.0},
    'ZERO':   {'T': 0.5, 'RC': 1.0, 'S': 1.5, 'C': 0.8, 'TR': 1.0, 'X': 0.3, 'Y': 1.0},
    'LOW':    {'T': 1.0, 'RC': 1.0, 'S': 1.0, 'C': 1.0, 'TR': 1.0, 'X': 1.0, 'Y': 1.0},
    'HIGH':   {'T': 1.5, 'RC': 0.5, 'S': 0.5, 'C': 1.5, 'TR': 0.5, 'X': 1.5, 'Y': 0.5},
}

# Gate 3: Hazard Envelope Context
ENVELOPE_CONTEXT = {
    'SAFE_OPEN':        {'T': 0.7, 'RC': 1.0, 'S': 1.3, 'C': 0.7, 'TR': 1.2, 'X': 0.7, 'Y': 1.2},
    'THERMAL_INTERIOR': {'T': 1.0, 'RC': 1.0, 'S': 1.0, 'C': 1.0, 'TR': 1.0, 'X': 1.0, 'Y': 1.0},
    'DANGEROUS_CLOSE':  {'T': 1.3, 'RC': 0.7, 'S': 0.7, 'C': 1.3, 'TR': 0.7, 'X': 1.3, 'Y': 0.7},
}

# Routing Effects (C1563)
ROUTING_EFFECTS = {
    'r': {'boost': {'X': 1.4}, 'suppress': {'S': 0.6, 'C': 0.7, 'Y': 0.7}},
    'y': {'boost': {'T': 1.4}, 'suppress': {'X': 0.7, 'C': 0.7}},
    'h': {'boost': {'TR': 1.4, 'RC': 1.3}, 'suppress': {'X': 0.7, 'T': 0.7}},
    'm': {'boost': {'C': 1.4}, 'suppress': {'T': 0.7, 'X': 0.7, 'TR': 0.7}},
    # Exploratory: weaker levels
    'n': {'boost': {'S': 1.2}, 'suppress': {'X': 0.8, 'T': 0.8}},
    'l': {'boost': {'TR': 1.2, 'S': 1.2}, 'suppress': {'X': 0.8}},
}


# ── Derive Functions ─────────────────────────────────────────────────────────

def derive_hazard_posture(token):
    """Determine hazard posture from token fields."""
    if token.get('head') == 'k' and token.get('source_immune'):
        return 'IMMUNE'
    if token.get('domain') == 'HEADLESS':
        return 'ZERO'
    if token.get('is_safe_pathway'):
        return 'ZERO'
    if token.get('head') == 'a' and token.get('term') in ('l', 'r'):
        return 'HIGH'
    if not token.get('source_immune') and token.get('frame_hazard') == 'HIGH':
        return 'HIGH'
    return 'LOW'


def derive_headless_subtype(token):
    """Determine headless subtype from token fields."""
    if token.get('domain') != 'HEADLESS':
        return 'HEADED'
    ph = token.get('pseudo_head_atom')
    if ph == 'd':
        return 'PSEUDO_D'
    if ph == 'i':
        return 'PSEUDO_I'
    if ph == 'l':
        return 'PSEUDO_L'
    if ph in ('c', 'p', 'f'):
        return 'PARAMETRIC_CPF'
    return 'OTHER_HEADLESS'


# ── Gate 4: CTS Closure Modulation ───────────────────────────────────────────

def cts_modulation(cts, state_var):
    """Multiplicative CTS gate for closure-relevant state variables."""
    if state_var == 'C':
        return 1.0 + 0.3 * cts
    if state_var == 'S':
        return 1.0 + 0.2 * cts
    if state_var == 'Y':
        return 1.0 + 0.4 * cts
    return 1.0


# ── Headless Intent Function ─────────────────────────────────────────────────

def headless_intent(subtype, packet_phase, folio_hl_rate):
    """
    Headless tokens do NOT use DOMAIN_INTENT.
    Instead, produce intent scaled by folio headless-heaviness.
    """
    intent = {}
    # Scale with headless-heaviness (normalized to 0.25 as reference)
    hl_norm = folio_hl_rate / 0.25 if folio_hl_rate > 0 else 0.0
    base_c = 0.3 * hl_norm
    base_s = 0.2 * hl_norm

    if packet_phase == 'CLOSE':
        intent['C'] = {'permission': min(base_c * 1.5, 0.8), 'direction': +1}
        intent['S'] = {'permission': min(base_s * 1.5, 0.6), 'direction': +1}
        intent['Y'] = {'permission': 0.2, 'direction': +1}
    elif packet_phase == 'SPEC':
        intent['C'] = {'permission': base_c * 0.5, 'direction': +1}
        intent['S'] = {'permission': base_s * 0.8, 'direction': +1}
    else:  # WORK
        intent['C'] = {'permission': base_c, 'direction': +1}
        intent['S'] = {'permission': base_s, 'direction': +1}

    # Subtype-specific additions
    if subtype == 'PSEUDO_D':
        intent['X'] = {'permission': 0.15, 'direction': -1}
    elif subtype == 'PSEUDO_L':
        intent['TR'] = {'permission': 0.15, 'direction': +1}
    elif subtype == 'PARAMETRIC_CPF':
        cur_c = intent.get('C', {}).get('permission', 0)
        intent['C'] = {'permission': min(cur_c + 0.15, 0.8), 'direction': +1}

    return intent


# ── Main Processing ──────────────────────────────────────────────────────────

def main():
    t_start = time.time()
    print("=" * 70)
    print("T2: Trace to Supervisory Interface")
    print("=" * 70)

    # ── Load inputs ──────────────────────────────────────────────────────
    print("\nLoading input files...")

    with open(DOMAIN_INPUT, 'r') as f:
        domain_data = json.load(f)
    tokens = domain_data['corpus_tokens']
    n_tokens = len(tokens)
    print(f"  Tokens: {n_tokens}")

    with open(PACKETS_INPUT, 'r') as f:
        packets_data = json.load(f)
    line_packets = packets_data['line_packets']
    print(f"  Line packets: {len(line_packets)}")

    with open(CTS_INPUT, 'r') as f:
        cts_data = json.load(f)
    line_cts = cts_data['line_cts']
    print(f"  CTS entries: {len(line_cts)}")

    with open(BUDGETS_INPUT, 'r') as f:
        budgets_data = json.load(f)
    folio_budgets = budgets_data['folio_budgets']
    print(f"  Folio budgets: {len(folio_budgets)}")

    # ── Pre-compute folio hl_rate lookup ─────────────────────────────────
    folio_hl_rate = {}
    for fid, fb in folio_budgets.items():
        hr = fb.get('headless_regime', {})
        folio_hl_rate[fid] = hr.get('hl_rate', 0.20)  # fallback to ~mean

    # ── Process tokens ───────────────────────────────────────────────────
    print("\nProcessing tokens...")

    # Defaults for lines without packets
    DEFAULT_PHASE = 'WORK'
    DEFAULT_ENVELOPE = 'THERMAL_INTERIOR'
    DEFAULT_CTS = 0.3

    # Pilot folios for per-folio summary
    pilot_folios = {'f78r', 'f41v', 'f103r', 'f46r', 'f83v', 'f26r'}

    # Accumulators
    n_routing_events = 0
    n_headless_tokens = 0
    token_signals = []

    # Per-section accumulators
    section_accum = defaultdict(lambda: {
        'n_tokens': 0,
        'contributions_sum': [0.0] * 7,
        'domain_counts': defaultdict(int),
        'hazard_counts': defaultdict(int),
        'routing_count': 0,
    })

    # Per-folio accumulators (pilot only)
    folio_accum = defaultdict(lambda: {
        'n_tokens': 0,
        'contributions_sum': [0.0] * 7,
        'routing_count': 0,
    })

    # Per-domain accumulators (for mean contribution printout)
    domain_accum = defaultdict(lambda: {
        'n_tokens': 0,
        'contributions_sum': [0.0] * 7,
    })

    for idx, tok in enumerate(tokens):
        word = tok.get('word', '')
        folio = tok.get('folio', '')
        line = tok.get('line', '')
        line_pos = tok.get('line_pos', 0.0)
        section = tok.get('section', '')
        domain = tok.get('domain', 'STABILITY')
        prev_term = tok.get('prev_term_same_line')

        # ── Look up line-level context ───────────────────────────────
        line_key = f"{folio}|{line}"

        packet = line_packets.get(line_key)
        if packet and 'packet_state' in packet:
            ps = packet['packet_state']
            packet_phase = ps.get('packet_phase', DEFAULT_PHASE)
            hazard_envelope = ps.get('hazard_envelope', DEFAULT_ENVELOPE)
        else:
            packet_phase = DEFAULT_PHASE
            hazard_envelope = DEFAULT_ENVELOPE

        cts_entry = line_cts.get(line_key)
        if cts_entry:
            cts = cts_entry.get('cts', DEFAULT_CTS)
        else:
            cts = DEFAULT_CTS

        hl_rate = folio_hl_rate.get(folio, 0.20)

        # ── Derive posture and subtype ───────────────────────────────
        hazard_posture = derive_hazard_posture(tok)
        hdl_subtype = derive_headless_subtype(tok)
        is_headless = (domain == 'HEADLESS')
        if is_headless:
            n_headless_tokens += 1

        # ── Stage 1: Build raw intent ────────────────────────────────
        if is_headless:
            raw_intent = headless_intent(hdl_subtype, packet_phase, hl_rate)
        else:
            domain_map = DOMAIN_INTENT.get(domain)
            if domain_map is not None:
                # Deep copy so we don't mutate the template
                raw_intent = {sv: dict(vals) for sv, vals in domain_map.items()}
            else:
                # Unknown domain — treat as empty
                raw_intent = {}

        # ── Apply routing effects (C1563) ────────────────────────────
        routing_active = False
        routing_terminal = None
        if prev_term and prev_term in ROUTING_EFFECTS:
            routing_active = True
            routing_terminal = prev_term
            n_routing_events += 1
            effects = ROUTING_EFFECTS[prev_term]
            for sv, mult in effects.get('boost', {}).items():
                if sv in raw_intent:
                    raw_intent[sv]['permission'] *= mult
                # If the SV isn't in raw_intent, routing has nothing to boost
            for sv, mult in effects.get('suppress', {}).items():
                if sv in raw_intent:
                    raw_intent[sv]['permission'] *= mult

        # ── Stage 2: Apply 4 gating layers ───────────────────────────
        # For each state variable in raw_intent, multiply permission
        # by all 4 gates.

        contributions = [0.0] * 7

        for sv, intent_vals in raw_intent.items():
            perm = intent_vals['permission']
            direction = intent_vals['direction']

            # Gate 1: Phase admissibility
            phase_gate = PHASE_ADMISSIBILITY.get(packet_phase, PHASE_ADMISSIBILITY['WORK'])
            perm *= phase_gate.get(sv, 1.0)

            # Gate 2: Hazard posture
            haz_gate = HAZARD_PRIORITY.get(hazard_posture, HAZARD_PRIORITY['LOW'])
            perm *= haz_gate.get(sv, 1.0)

            # Gate 3: Envelope context
            env_gate = ENVELOPE_CONTEXT.get(hazard_envelope, ENVELOPE_CONTEXT['THERMAL_INTERIOR'])
            perm *= env_gate.get(sv, 1.0)

            # Gate 4: CTS closure modulation
            perm *= cts_modulation(cts, sv)

            # Compute contribution
            sv_idx = SV_INDEX.get(sv)
            if sv_idx is not None:
                contributions[sv_idx] = perm * direction * BASE_STEP

        # ── Build output record ──────────────────────────────────────
        record = {
            'word': word,
            'folio': folio,
            'line': line,
            'line_pos': round(line_pos, 4) if isinstance(line_pos, float) else line_pos,
            'section': section,
            'domain': domain,
            'hazard_posture': hazard_posture,
            'packet_phase': packet_phase,
            'hazard_envelope': hazard_envelope,
            'cts': round(cts, 5),
            'routing_active': routing_active,
            'routing_terminal': routing_terminal,
            'headless_subtype': hdl_subtype,
            'contributions': [round(c, 6) for c in contributions],
        }
        token_signals.append(record)

        # ── Accumulate for summaries ─────────────────────────────────
        sa = section_accum[section]
        sa['n_tokens'] += 1
        for i in range(7):
            sa['contributions_sum'][i] += contributions[i]
        sa['domain_counts'][domain] += 1
        sa['hazard_counts'][hazard_posture] += 1
        if routing_active:
            sa['routing_count'] += 1

        if folio in pilot_folios:
            fa = folio_accum[folio]
            fa['n_tokens'] += 1
            for i in range(7):
                fa['contributions_sum'][i] += contributions[i]
            if routing_active:
                fa['routing_count'] += 1

        da = domain_accum[domain]
        da['n_tokens'] += 1
        for i in range(7):
            da['contributions_sum'][i] += contributions[i]

    # ── Build summary ────────────────────────────────────────────────
    print("\nBuilding summary...")

    per_section = {}
    for sec in sorted(section_accum.keys()):
        sa = section_accum[sec]
        n = sa['n_tokens']
        mean_c = [sa['contributions_sum'][i] / n for i in range(7)] if n > 0 else [0.0] * 7
        domain_dist = {d: cnt / n for d, cnt in sa['domain_counts'].items()} if n > 0 else {}
        hazard_dist = {h: cnt / n for h, cnt in sa['hazard_counts'].items()} if n > 0 else {}
        per_section[sec] = {
            'n_tokens': n,
            'mean_contributions': [round(v, 6) for v in mean_c],
            'domain_dist': {k: round(v, 4) for k, v in sorted(domain_dist.items())},
            'hazard_dist': {k: round(v, 4) for k, v in sorted(hazard_dist.items())},
            'routing_rate': round(sa['routing_count'] / n, 4) if n > 0 else 0.0,
        }

    per_folio_sample = {}
    for fid in sorted(folio_accum.keys()):
        fa = folio_accum[fid]
        n = fa['n_tokens']
        mean_c = [fa['contributions_sum'][i] / n for i in range(7)] if n > 0 else [0.0] * 7
        per_folio_sample[fid] = {
            'n_tokens': n,
            'mean_contributions': [round(v, 6) for v in mean_c],
            'routing_rate': round(fa['routing_count'] / n, 4) if n > 0 else 0.0,
        }

    # ── Write output ─────────────────────────────────────────────────
    print(f"\nWriting output to {OUTPUT}...")

    output = {
        'metadata': {
            'phase': '563',
            'task': 'T2_trace_to_supervisory_interface',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_tokens': n_tokens,
            'base_step': BASE_STEP,
            'n_routing_events': n_routing_events,
            'n_headless_tokens': n_headless_tokens,
            'state_variables': STATE_VARS,
        },
        'token_signals': token_signals,
        'summary': {
            'per_section': per_section,
            'per_folio_sample': per_folio_sample,
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        json.dump(output, f, indent=1)

    file_size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"  Output size: {file_size_mb:.1f} MB")

    # ── Print summary statistics ─────────────────────────────────────
    elapsed = time.time() - t_start
    print(f"\n{'=' * 70}")
    print(f"SUMMARY (elapsed: {elapsed:.1f}s)")
    print(f"{'=' * 70}")
    print(f"  Total tokens:     {n_tokens}")
    print(f"  Routing events:   {n_routing_events} ({100*n_routing_events/n_tokens:.1f}%)")
    print(f"  Headless tokens:  {n_headless_tokens} ({100*n_headless_tokens/n_tokens:.1f}%)")

    print(f"\n  State variable order: {STATE_VARS}")

    print(f"\n  Mean contribution per DOMAIN:")
    print(f"  {'Domain':<15} {'n':>6}  {'T':>8} {'RC':>8} {'S':>8} {'C':>8} {'TR':>8} {'X':>8} {'Y':>8}")
    print(f"  {'-'*15} {'-'*6}  {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for dom in ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']:
        da = domain_accum.get(dom)
        if da and da['n_tokens'] > 0:
            n = da['n_tokens']
            means = [da['contributions_sum'][i] / n for i in range(7)]
            vals = ' '.join(f"{v:>8.5f}" for v in means)
            print(f"  {dom:<15} {n:>6}  {vals}")

    print(f"\n  Per-section summary:")
    print(f"  {'Section':<8} {'n':>6}  {'T':>8} {'RC':>8} {'S':>8} {'C':>8} {'TR':>8} {'X':>8} {'Y':>8}  {'Rte%':>5}")
    print(f"  {'-'*8} {'-'*6}  {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}  {'-'*5}")
    for sec in sorted(per_section.keys()):
        ps = per_section[sec]
        n = ps['n_tokens']
        mc = ps['mean_contributions']
        vals = ' '.join(f"{v:>8.5f}" for v in mc)
        rr = ps['routing_rate'] * 100
        print(f"  {sec:<8} {n:>6}  {vals}  {rr:>5.1f}")

    print(f"\n  Per-folio sample:")
    for fid in sorted(per_folio_sample.keys()):
        pf = per_folio_sample[fid]
        n = pf['n_tokens']
        mc = pf['mean_contributions']
        vals = ' '.join(f"{v:>8.5f}" for v in mc)
        rr = pf['routing_rate'] * 100
        print(f"    {fid:<8} n={n:>4}  {vals}  rte={rr:.1f}%")

    print(f"\n  Hazard posture distribution (global):")
    global_haz = defaultdict(int)
    for sec, sa in section_accum.items():
        for h, cnt in sa['hazard_counts'].items():
            global_haz[h] += cnt
    for h in ['IMMUNE', 'ZERO', 'LOW', 'HIGH']:
        cnt = global_haz.get(h, 0)
        print(f"    {h:<10} {cnt:>6} ({100*cnt/n_tokens:.1f}%)")

    print(f"\nDone.")


if __name__ == '__main__':
    main()
