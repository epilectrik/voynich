"""
T3: Null and Ablation Executor
===============================
Phase 564 - EVENT_GATED_APPARATUS_DYNAMICS

Runs 8 baselines + 4 null models (50 perms each) for the 20 pilot folios
through the event-gated apparatus.

Total: 8 baselines x 20 folios + 4 nulls x 20 folios x 50 perms
     = 160 + 4000 = 4,160 runs

Input:
  - t2b_supervisory_interface_unrouted.json  (per-token supervisory contributions)
  - t1_event_gated_apparatus.json            (apparatus spec, folio assignments)
  - t3_line_packets.json                     (line-level packet_phase, hazard_envelope)

Output:
  - t3_null_ablation_runs.json
"""

import json
import sys
import time
import math
import random
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Import event-gated apparatus
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t1_event_gated_apparatus import (
    EventGatedApparatus, STATE_VARS, HAZARD_BOUNDARIES, N_VARS, EQUILIBRIUM,
    SV_INDEX, PROFILES, CONFIG_MODES, PILOT_FOLIOS, assign_config_mode,
    build_configured_apparatus
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PHASE_DIR.parent.parent

T2B_PATH = (PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'results'
            / 't2b_supervisory_interface_unrouted.json')
T1_PATH = PHASE_DIR / 'results' / 't1_event_gated_apparatus.json'
PACKETS_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                / 'results' / 't3_line_packets.json')
OUTPUT_PATH = PHASE_DIR / 'results' / 't3_null_ablation_runs.json'

# ---------------------------------------------------------------------------
# Routing constants (same as T2)
# ---------------------------------------------------------------------------
ROUTING_EFFECTS = {
    'r': {'boost': {'X': 1.4}, 'suppress': {'S': 0.6, 'C': 0.7, 'Y': 0.7}},
    'y': {'boost': {'T': 1.4}, 'suppress': {'X': 0.7, 'C': 0.7}},
    'h': {'boost': {'TR': 1.4, 'RC': 1.3}, 'suppress': {'X': 0.7, 'T': 0.7}},
    'm': {'boost': {'C': 1.4}, 'suppress': {'T': 0.7, 'X': 0.7, 'TR': 0.7}},
    'n': {'boost': {'S': 1.2}, 'suppress': {'X': 0.8, 'T': 0.8}},
    'l': {'boost': {'TR': 1.2, 'S': 1.2}, 'suppress': {'X': 0.8}},
}

ROUTING_THRESH_EFFECTS = {
    'r': {'X_collapse_level': +0.04},
    'y': {'T_reversal_level': +0.04},
    'h': {'C_relief_level': -0.04},
    'm': {'C_relief_level': +0.04, 'CTS_discharge_strength': +0.3},
    'n': {'S_erosion_strength': -0.3},
    'l': {'C_relief_level': -0.02},
}

ROUTING_CONTRIB_GAIN = 0.3
ROUTING_DECAY = 0.7


# ---------------------------------------------------------------------------
# Sort key
# ---------------------------------------------------------------------------
def sort_key(tok):
    try:
        ln = int(tok['line'])
    except (ValueError, TypeError):
        ln = 0
    lp = tok.get('line_pos', 0.0)
    if not isinstance(lp, (int, float)):
        lp = 0.0
    return (ln, lp)


# ---------------------------------------------------------------------------
# Hazard check
# ---------------------------------------------------------------------------
def is_in_bounds(state):
    """Check if state is within all hazard boundaries."""
    for i, sv in enumerate(STATE_VARS):
        lo, hi = HAZARD_BOUNDARIES[sv]
        if lo is not None and state[i] < lo:
            return False
        if hi is not None and state[i] > hi:
            return False
    return True


# ---------------------------------------------------------------------------
# Core execution: run_coupled_trace (SAME as T2)
# ---------------------------------------------------------------------------
def run_coupled_trace(apparatus, tokens, line_packets, store_trajectory=False):
    """
    Run a single folio through the event-gated apparatus with dual-channel
    routing buffer.

    Dual-channel routing logic:
      Channel 1 (contribution buffer): multiplicative bias on dV
      Channel 2 (threshold shift buffer): additive shifts on threshold levels

    Execution loop per token:
      1. Line boundary -> reset both routing buffers
      2. Routing event -> update both buffers from ROUTING_EFFECTS/ROUTING_THRESH_EFFECTS
      3. Look up packet_phase from line_packets (default WORK)
      4. Compute buffered dV: sensitivity * contribution * (1 + contrib_buffer[i])
      5. Call apparatus.update(state, dV, packet_phase, cts, threshold_shifts)
      6. Decay both buffers by ROUTING_DECAY

    Parameters
    ----------
    apparatus : EventGatedApparatus
    tokens : list[dict]  (sorted by line, line_pos)
    line_packets : dict   (line_key -> packet dict)
    store_trajectory : bool

    Returns
    -------
    dict with summary (and optionally trajectory)
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return {
            'viability_fraction': 1.0,
            'hazard_count': 0,
            'Y_final': 0.5,
            'max_T': 0.5, 'min_S': 0.5, 'max_C': 0.5, 'max_X': 0.5,
            'mean_state': [0.5] * N_VARS,
        }

    state = [EQUILIBRIUM] * N_VARS
    routing_contrib_buffer = [0.0] * N_VARS
    routing_thresh_buffer = {}
    prev_line = None

    trajectory = [] if store_trajectory else None

    # Accumulators
    n_viable = 0
    hazard_count = 0
    state_sum = [0.0] * N_VARS
    max_T = 0.0
    min_S = 1.0
    max_C = 0.0
    max_X = 0.0

    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok.get('folio', '')

        # 1. Reset routing buffers at line boundaries
        if current_line != prev_line:
            routing_contrib_buffer = [0.0] * N_VARS
            routing_thresh_buffer = {}
            prev_line = current_line

        # 2. Routing event -> update both buffers
        if tok.get('routing_active') and tok.get('routing_terminal'):
            rt = tok['routing_terminal']
            if rt in ROUTING_EFFECTS:
                effects = ROUTING_EFFECTS[rt]
                for sv, mult in effects.get('boost', {}).items():
                    routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN
                for sv, mult in effects.get('suppress', {}).items():
                    routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN
            if rt in ROUTING_THRESH_EFFECTS:
                for key, shift in ROUTING_THRESH_EFFECTS[rt].items():
                    routing_thresh_buffer[key] = routing_thresh_buffer.get(key, 0.0) + shift

        # 3. Look up packet_phase from line_packets
        line_key = f"{folio}|{current_line}"
        packet = line_packets.get(line_key)
        if packet and 'packet_state' in packet:
            packet_phase = packet['packet_state'].get('packet_phase', 'WORK')
        else:
            packet_phase = tok.get('packet_phase', 'WORK')

        cts = tok.get('cts', 0.0)

        # 4. Compute buffered dV
        contributions = tok['contributions']
        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            base_sens = apparatus.sensitivity(sv)
            dV[i] = contributions[i] * base_sens * (1.0 + routing_contrib_buffer[i])

        # 5. Update state via apparatus
        threshold_shifts = routing_thresh_buffer if routing_thresh_buffer else None
        state = apparatus.update(state, dV, packet_phase, cts, threshold_shifts)

        # 6. Decay both buffers
        routing_contrib_buffer = [a * ROUTING_DECAY for a in routing_contrib_buffer]
        new_thresh = {}
        for k, v in routing_thresh_buffer.items():
            decayed = v * ROUTING_DECAY
            if abs(decayed) > 1e-10:
                new_thresh[k] = decayed
        routing_thresh_buffer = new_thresh

        # --- Check hazards ---
        if is_in_bounds(state):
            n_viable += 1
        else:
            hazard_count += 1

        # --- Accumulate stats ---
        for i in range(N_VARS):
            state_sum[i] += state[i]
        if state[0] > max_T:
            max_T = state[0]
        if state[2] < min_S:
            min_S = state[2]
        if state[3] > max_C:
            max_C = state[3]
        if state[5] > max_X:
            max_X = state[5]

        # --- Trajectory ---
        if store_trajectory:
            trajectory.append({
                'state': [round(v, 6) for v in state],
                'word': tok.get('word', ''),
                'line': current_line,
            })

    # --- Build summary ---
    mean_state = [state_sum[i] / n_tokens for i in range(N_VARS)]

    result = {
        'viability_fraction': round(n_viable / n_tokens, 6),
        'hazard_count': hazard_count,
        'Y_final': round(state[SV_INDEX['Y']], 6),
        'max_T': round(max_T, 6),
        'min_S': round(min_S, 6),
        'max_C': round(max_C, 6),
        'max_X': round(max_X, 6),
        'mean_state': [round(v, 6) for v in mean_state],
    }

    if store_trajectory:
        result['trajectory'] = trajectory

    return result


# ---------------------------------------------------------------------------
# Null model generators
# ---------------------------------------------------------------------------

def null_n1_token_shuffle(tokens, rng):
    """N1: Shuffle all token positions randomly within the folio.
    Same token inventory, random order. Positional info reassigned from original."""
    shuffled = list(tokens)
    rng.shuffle(shuffled)
    # Reassign positional info from original order
    for i, orig in enumerate(tokens):
        shuffled[i] = dict(shuffled[i])
        shuffled[i]['line'] = orig['line']
        shuffled[i]['line_pos'] = orig['line_pos']
    return shuffled


def null_n2_domain_preserve_shuffle(tokens, rng):
    """N2: Within each domain group, shuffle contribution vectors and routing info.
    Preserves domain sequence, destroys within-domain compositional structure."""
    domain_groups = {}
    for i, tok in enumerate(tokens):
        d = tok.get('domain', 'UNKNOWN')
        if d not in domain_groups:
            domain_groups[d] = []
        domain_groups[d].append(i)

    shuffled = [dict(t) for t in tokens]
    for domain, indices in domain_groups.items():
        contrib_data = [
            (tokens[i]['contributions'],
             tokens[i].get('routing_active', False),
             tokens[i].get('routing_terminal'),
             tokens[i].get('cts', 0.0),
             tokens[i].get('hazard_posture', 'LOW'),
             tokens[i].get('headless_subtype', 'HEADED'))
            for i in indices
        ]
        rng.shuffle(contrib_data)
        for j, idx in enumerate(indices):
            shuffled[idx]['contributions'] = contrib_data[j][0]
            shuffled[idx]['routing_active'] = contrib_data[j][1]
            shuffled[idx]['routing_terminal'] = contrib_data[j][2]
            shuffled[idx]['cts'] = contrib_data[j][3]
            shuffled[idx]['hazard_posture'] = contrib_data[j][4]
            shuffled[idx]['headless_subtype'] = contrib_data[j][5]
    return shuffled


def null_n3_line_shuffle(folio, tokens, section_line_pool, rng):
    """N3: Shuffle whole lines between folios within the same section.
    For each line in this folio, replace with a randomly drawn line from
    other folios in the same section."""
    # Get this folio's line keys
    folio_lines = {}
    for tok in tokens:
        ln = tok['line']
        if ln not in folio_lines:
            folio_lines[ln] = []
        folio_lines[ln].append(tok)

    # Available donor lines (from other folios in same section)
    other_lines = [k for k in section_line_pool.keys()
                   if not k.startswith(folio + '|')]

    new_tokens = []
    for line_key in sorted(folio_lines.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        # Pick a random line from the pool
        if other_lines:
            donor_key = rng.choice(other_lines)
        else:
            donor_key = f"{folio}|{line_key}"
        donor_tokens = section_line_pool.get(donor_key, [])
        # Map donor tokens into this line's position
        for i, dtok in enumerate(donor_tokens):
            t = dict(dtok)
            t['line'] = line_key
            t['folio'] = folio  # keep folio attribution
            new_tokens.append(t)
    return new_tokens


def null_n4_within_line_shuffle(tokens, rng):
    """N4: Shuffle token positions within each line. Destroys within-line
    sequence while keeping line membership."""
    line_groups = {}
    for tok in tokens:
        ln = tok['line']
        if ln not in line_groups:
            line_groups[ln] = []
        line_groups[ln].append(tok)

    shuffled = []
    for ln in sorted(line_groups.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        line_toks = line_groups[ln]
        content = [
            (t['contributions'],
             t.get('routing_active', False),
             t.get('routing_terminal'),
             t.get('cts', 0.0),
             t.get('domain', 'UNKNOWN'),
             t.get('hazard_posture', 'LOW'),
             t.get('headless_subtype', 'HEADED'))
            for t in line_toks
        ]
        rng.shuffle(content)
        for i, t in enumerate(line_toks):
            nt = dict(t)
            nt['contributions'] = content[i][0]
            nt['routing_active'] = content[i][1]
            nt['routing_terminal'] = content[i][2]
            nt['cts'] = content[i][3]
            nt['domain'] = content[i][4]
            nt['hazard_posture'] = content[i][5]
            nt['headless_subtype'] = content[i][6]
            shuffled.append(nt)
    return shuffled


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("T3: Null and Ablation Executor")
    print("Phase 564 - EVENT_GATED_APPARATUS_DYNAMICS")
    print("=" * 70)

    # --- Load inputs ---
    print("\nLoading inputs...")

    with open(T2B_PATH, 'r', encoding='utf-8') as f:
        t2b_data = json.load(f)
    all_tokens = t2b_data['token_signals']
    print(f"  T2b tokens: {len(all_tokens)}")

    with open(T1_PATH, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)
    folio_assignments = t1_data['folio_assignments']
    config_assignments = t1_data['config_assignments']
    print(f"  T1 folio assignments: {len(folio_assignments)}")
    print(f"  T1 config assignments: {len(config_assignments)}")

    with open(PACKETS_PATH, 'r', encoding='utf-8') as f:
        packets_data = json.load(f)
    line_packets = packets_data['line_packets']
    print(f"  Line packets: {len(line_packets)}")

    # --- Group tokens by folio ---
    tokens_by_folio = defaultdict(list)
    for tok in all_tokens:
        tokens_by_folio[tok['folio']].append(tok)

    # Sort tokens within each folio
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    print(f"  Unique folios in T2b: {len(tokens_by_folio)}")

    # --- Build folio -> section mapping ---
    folio_section = {}
    for folio, info in folio_assignments.items():
        folio_section[folio] = info.get('section', 'UNKNOWN')

    # --- Pre-compute section/folio means for baselines ---
    print("\nPre-computing baseline data...")

    # Section mean contributions
    section_contrib_sums = defaultdict(lambda: [0.0] * N_VARS)
    section_contrib_counts = defaultdict(int)
    for tok in all_tokens:
        sec = tok.get('section', 'UNKNOWN')
        contribs = tok['contributions']
        for i in range(N_VARS):
            section_contrib_sums[sec][i] += contribs[i]
        section_contrib_counts[sec] += 1

    section_mean_contribs = {}
    for sec in section_contrib_sums:
        n = section_contrib_counts[sec]
        section_mean_contribs[sec] = [section_contrib_sums[sec][i] / n for i in range(N_VARS)]
    print(f"  Section mean contribs: {len(section_mean_contribs)} sections")

    # Folio mean contributions and folio mean CTS
    folio_contrib_sums = defaultdict(lambda: [0.0] * N_VARS)
    folio_contrib_counts = defaultdict(int)
    folio_cts_sums = defaultdict(float)
    folio_cts_counts = defaultdict(int)
    for tok in all_tokens:
        fid = tok['folio']
        contribs = tok['contributions']
        for i in range(N_VARS):
            folio_contrib_sums[fid][i] += contribs[i]
        folio_contrib_counts[fid] += 1
        folio_cts_sums[fid] += tok.get('cts', 0.0)
        folio_cts_counts[fid] += 1

    folio_mean_contribs = {}
    folio_mean_cts = {}
    for fid in folio_contrib_sums:
        n = folio_contrib_counts[fid]
        folio_mean_contribs[fid] = [folio_contrib_sums[fid][i] / n for i in range(N_VARS)]
        folio_mean_cts[fid] = folio_cts_sums[fid] / folio_cts_counts[fid]
    print(f"  Folio mean contribs: {len(folio_mean_contribs)} folios")

    # Section line pool (for N3 null) - built from ALL folios, not just pilot
    section_line_pool_by_section = defaultdict(dict)  # section -> {line_key -> [tokens]}
    for fid, toks in tokens_by_folio.items():
        sec = folio_section.get(fid, 'UNKNOWN')
        for tok in toks:
            line_key = f"{fid}|{tok['line']}"
            if line_key not in section_line_pool_by_section[sec]:
                section_line_pool_by_section[sec][line_key] = []
            section_line_pool_by_section[sec][line_key].append(tok)
    total_pool_lines = sum(len(pool) for pool in section_line_pool_by_section.values())
    print(f"  Section line pool: {total_pool_lines} lines across "
          f"{len(section_line_pool_by_section)} sections")

    # --- Determine preferred profile and config mode for each pilot folio ---
    pilot_folio_list = sorted(PILOT_FOLIOS.keys())
    print(f"\nPilot folios: {len(pilot_folio_list)}")

    folio_profile = {}
    folio_config_mode = {}
    for folio in pilot_folio_list:
        # Preferred profile from T1 folio assignments
        assignment = folio_assignments.get(folio, {})
        profile = assignment.get('preferred_profile', 'A2_SEALED_RECIRCULATION')
        folio_profile[folio] = profile

        # Config mode from T1 config assignments
        cfg = config_assignments.get(folio, {})
        config_mode = cfg.get('config_mode', 'H1_MEDIUM_INFRA')
        folio_config_mode[folio] = config_mode

        print(f"  {folio}: profile={profile}, config={config_mode}, "
              f"n_tokens={len(tokens_by_folio.get(folio, []))}")

    # === REFERENCE RUNS ===
    print("\n" + "=" * 70)
    print("REFERENCE RUNS (full model, 20 folios)")
    print("=" * 70)

    reference = {}
    run_count = 0
    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            print(f"  WARNING: {folio} has no tokens, skipping")
            continue

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]
        apparatus = EventGatedApparatus(PROFILES[profile], config_mode)

        result = run_coupled_trace(apparatus, toks, line_packets, store_trajectory=False)
        reference[folio] = result
        run_count += 1

    print(f"  Reference runs: {run_count}")
    for folio in pilot_folio_list:
        if folio in reference:
            r = reference[folio]
            print(f"    {folio}: viab={r['viability_fraction']:.4f}, "
                  f"haz={r['hazard_count']}, Y={r['Y_final']:.4f}")

    # === BASELINES (8 types x 20 folios = 160 runs) ===
    print("\n" + "=" * 70)
    print("BASELINES (8 types x 20 folios = 160 runs)")
    print("=" * 70)

    baselines = {
        'B1_section_mean': {},
        'B2_folio_mean': {},
        'B3_full_minus_cts': {},
        'B4_full_minus_routing': {},
        'B5_full_minus_config': {},
        'B6_full_minus_all_headless': {},
        'B7_full_minus_thresholds': {},
        'B8_fixed_law': {},
    }

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]
        sec = folio_section.get(folio, 'UNKNOWN')

        # --- B1: Section-Mean Contributions ---
        sec_mean = section_mean_contribs.get(sec, [0.0] * N_VARS)
        b1_toks = []
        for t in toks:
            nt = dict(t)
            nt['contributions'] = list(sec_mean)
            b1_toks.append(nt)
        apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
        baselines['B1_section_mean'][folio] = run_coupled_trace(
            apparatus, b1_toks, line_packets)
        run_count += 1

        # --- B2: Folio-Mean Contributions ---
        fol_mean = folio_mean_contribs.get(folio, [0.0] * N_VARS)
        b2_toks = []
        for t in toks:
            nt = dict(t)
            nt['contributions'] = list(fol_mean)
            b2_toks.append(nt)
        apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
        baselines['B2_folio_mean'][folio] = run_coupled_trace(
            apparatus, b2_toks, line_packets)
        run_count += 1

        # --- B3: Full Minus CTS ---
        b3_toks = []
        for t in toks:
            nt = dict(t)
            nt['cts'] = 0.0
            b3_toks.append(nt)
        apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
        baselines['B3_full_minus_cts'][folio] = run_coupled_trace(
            apparatus, b3_toks, line_packets)
        run_count += 1

        # --- B4: Full Minus Routing Buffers ---
        # Run with routing buffers permanently disabled.
        # We achieve this by clearing routing_active on all tokens.
        b4_toks = []
        for t in toks:
            nt = dict(t)
            nt['routing_active'] = False
            nt['routing_terminal'] = None
            b4_toks.append(nt)
        apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
        baselines['B4_full_minus_routing'][folio] = run_coupled_trace(
            apparatus, b4_toks, line_packets)
        run_count += 1

        # --- B5: Full Minus Config Mode ---
        # Force H1_MEDIUM_INFRA regardless of HL rate
        apparatus = EventGatedApparatus(PROFILES[profile], 'H1_MEDIUM_INFRA')
        baselines['B5_full_minus_config'][folio] = run_coupled_trace(
            apparatus, toks, line_packets)
        run_count += 1

        # --- B6: Full Minus All Headless ---
        # Replace headless tokens' contributions with section mean,
        # set routing_active=False, set cts to folio mean cts.
        fol_cts_mean = folio_mean_cts.get(folio, 0.3)
        b6_toks = []
        for t in toks:
            nt = dict(t)
            if nt.get('headless_subtype', 'HEADED') != 'HEADED':
                nt['contributions'] = list(sec_mean)
                nt['routing_active'] = False
                nt['cts'] = fol_cts_mean
            b6_toks.append(nt)
        apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
        baselines['B6_full_minus_all_headless'][folio] = run_coupled_trace(
            apparatus, b6_toks, line_packets)
        run_count += 1

        # --- B7: Full Minus Threshold Terms ---
        no_thresh = {
            'thresh_T_strength': 0.0,
            'thresh_X_strength': 0.0,
            'thresh_C_strength': 0.0,
            'thresh_S_strength': 0.0,
            'thresh_cts_strength': 0.0,
        }
        apparatus = EventGatedApparatus(PROFILES[profile], config_mode,
                                        threshold_params=no_thresh)
        baselines['B7_full_minus_thresholds'][folio] = run_coupled_trace(
            apparatus, toks, line_packets)
        run_count += 1

        # --- B8: Fixed Law ---
        # Override packet_phase to 'WORK' for ALL tokens
        b8_toks = []
        for t in toks:
            nt = dict(t)
            nt['packet_phase'] = 'WORK'
            b8_toks.append(nt)
        # Also need to ensure line_packets won't override this.
        # We pass an empty line_packets dict so the fallback uses tok['packet_phase'].
        apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
        baselines['B8_fixed_law'][folio] = run_coupled_trace(
            apparatus, b8_toks, {})
        run_count += 1

        if run_count % 200 == 0:
            print(f"  Progress: {run_count} runs completed...")

    print(f"  Baseline runs completed: {run_count - len(reference)}")

    # Print baseline summary
    for bname, bdata in baselines.items():
        viabs = [bdata[f]['viability_fraction'] for f in bdata]
        if viabs:
            mean_v = sum(viabs) / len(viabs)
            print(f"  {bname}: mean_viab={mean_v:.4f}, n_folios={len(viabs)}")

    # === NULL MODELS (4 types x 20 folios x 50 perms = 4,000 runs) ===
    print("\n" + "=" * 70)
    print("NULL MODELS (4 types x 20 folios x 50 perms = 4,000 runs)")
    print("=" * 70)

    N_PERMS = 50
    nulls = {
        'N1_token_shuffle': {},
        'N2_domain_preserve': {},
        'N3_line_shuffle': {},
        'N4_within_line': {},
    }

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]
        sec = folio_section.get(folio, 'UNKNOWN')
        section_pool = section_line_pool_by_section.get(sec, {})

        # Initialize null result containers
        for null_name in nulls:
            nulls[null_name][folio] = {
                'per_perm': [],
            }

        for perm_idx in range(N_PERMS):
            rng = random.Random(42 + perm_idx)

            # --- N1: Token Shuffle Within Folio ---
            n1_toks = null_n1_token_shuffle(toks, rng)
            apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
            r1 = run_coupled_trace(apparatus, n1_toks, line_packets)
            nulls['N1_token_shuffle'][folio]['per_perm'].append({
                'viability_fraction': r1['viability_fraction'],
                'hazard_count': r1['hazard_count'],
                'Y_final': r1['Y_final'],
                'mean_state': r1['mean_state'],
            })
            run_count += 1

            # --- N2: Domain-Preserving Form Shuffle ---
            rng2 = random.Random(42 + perm_idx)
            n2_toks = null_n2_domain_preserve_shuffle(toks, rng2)
            apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
            r2 = run_coupled_trace(apparatus, n2_toks, line_packets)
            nulls['N2_domain_preserve'][folio]['per_perm'].append({
                'viability_fraction': r2['viability_fraction'],
                'hazard_count': r2['hazard_count'],
                'Y_final': r2['Y_final'],
                'mean_state': r2['mean_state'],
            })
            run_count += 1

            # --- N3: Line Shuffle Within Section ---
            rng3 = random.Random(42 + perm_idx)
            n3_toks = null_n3_line_shuffle(folio, toks, section_pool, rng3)
            apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
            r3 = run_coupled_trace(apparatus, n3_toks, line_packets)
            nulls['N3_line_shuffle'][folio]['per_perm'].append({
                'viability_fraction': r3['viability_fraction'],
                'hazard_count': r3['hazard_count'],
                'Y_final': r3['Y_final'],
                'mean_state': r3['mean_state'],
            })
            run_count += 1

            # --- N4: Within-Line Token Position Shuffle ---
            rng4 = random.Random(42 + perm_idx)
            n4_toks = null_n4_within_line_shuffle(toks, rng4)
            apparatus = EventGatedApparatus(PROFILES[profile], config_mode)
            r4 = run_coupled_trace(apparatus, n4_toks, line_packets)
            nulls['N4_within_line'][folio]['per_perm'].append({
                'viability_fraction': r4['viability_fraction'],
                'hazard_count': r4['hazard_count'],
                'Y_final': r4['Y_final'],
                'mean_state': r4['mean_state'],
            })
            run_count += 1

            if run_count % 200 == 0:
                elapsed = time.time() - t0
                print(f"  Progress: {run_count} runs completed ({elapsed:.1f}s)...")

    # Compute null summaries
    for null_name in nulls:
        for folio in nulls[null_name]:
            perms = nulls[null_name][folio]['per_perm']
            n_p = len(perms)
            if n_p == 0:
                continue
            viabs = [p['viability_fraction'] for p in perms]
            hazards = [p['hazard_count'] for p in perms]
            y_finals = [p['Y_final'] for p in perms]

            viab_mean = sum(viabs) / n_p
            viab_std = math.sqrt(sum((v - viab_mean) ** 2 for v in viabs) / n_p)
            haz_mean = sum(hazards) / n_p
            y_mean = sum(y_finals) / n_p

            # Compute mean state across permutations
            mean_state_avg = [0.0] * N_VARS
            for p in perms:
                ms = p.get('mean_state', [0.5] * N_VARS)
                for i in range(N_VARS):
                    mean_state_avg[i] += ms[i]
            mean_state_avg = [round(v / n_p, 6) for v in mean_state_avg]

            nulls[null_name][folio]['viability_mean'] = round(viab_mean, 6)
            nulls[null_name][folio]['viability_std'] = round(viab_std, 6)
            nulls[null_name][folio]['hazard_count_mean'] = round(haz_mean, 2)
            nulls[null_name][folio]['Y_final_mean'] = round(y_mean, 6)
            nulls[null_name][folio]['mean_state'] = mean_state_avg

    # Print null summary
    for null_name in nulls:
        viab_means = [nulls[null_name][f]['viability_mean']
                      for f in nulls[null_name]
                      if 'viability_mean' in nulls[null_name][f]]
        if viab_means:
            overall_mean = sum(viab_means) / len(viab_means)
            print(f"  {null_name}: overall_mean_viab={overall_mean:.4f}, "
                  f"n_folios={len(viab_means)}")

    # === Assemble output ===
    elapsed = time.time() - t0
    print(f"\nTotal runs: {run_count} in {elapsed:.1f}s")

    output = {
        'metadata': {
            'phase': '564',
            'task': 'T3_null_and_ablation_executor',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_baselines': 8,
            'n_null_types': 4,
            'n_perms': N_PERMS,
            'n_pilot_folios': len(pilot_folio_list),
            'n_total_runs': run_count,
            'elapsed_seconds': round(elapsed, 2),
        },
        'reference': reference,
        'baselines': baselines,
        'nulls': nulls,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"Size: {file_size_mb:.1f} MB")

    # === FINAL SUMMARY ===
    print(f"\n{'=' * 70}")
    print("FINAL SUMMARY")
    print(f"{'=' * 70}")

    # Reference vs baseline comparison
    print(f"\n  {'Folio':<8} {'Ref':>7} | "
          f"{'B1':>7} {'B2':>7} {'B3':>7} {'B4':>7} "
          f"{'B5':>7} {'B6':>7} {'B7':>7} {'B8':>7} | "
          f"{'N1':>7} {'N2':>7} {'N3':>7} {'N4':>7}")
    print(f"  {'-' * 8} {'-' * 7} | "
          f"{'-' * 7} {'-' * 7} {'-' * 7} {'-' * 7} "
          f"{'-' * 7} {'-' * 7} {'-' * 7} {'-' * 7} | "
          f"{'-' * 7} {'-' * 7} {'-' * 7} {'-' * 7}")

    bnames = ['B1_section_mean', 'B2_folio_mean', 'B3_full_minus_cts',
              'B4_full_minus_routing', 'B5_full_minus_config',
              'B6_full_minus_all_headless', 'B7_full_minus_thresholds',
              'B8_fixed_law']
    nnames = ['N1_token_shuffle', 'N2_domain_preserve',
              'N3_line_shuffle', 'N4_within_line']

    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        ref_v = reference[folio]['viability_fraction']
        b_vals = []
        for bn in bnames:
            v = baselines[bn].get(folio, {}).get('viability_fraction', 0.0)
            b_vals.append(f"{v:>7.4f}")
        n_vals = []
        for nn in nnames:
            v = nulls[nn].get(folio, {}).get('viability_mean', 0.0)
            n_vals.append(f"{v:>7.4f}")
        print(f"  {folio:<8} {ref_v:>7.4f} | {' '.join(b_vals)} | {' '.join(n_vals)}")

    print(f"\n  Total runs: {run_count}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("  Done.")


if __name__ == '__main__':
    main()
