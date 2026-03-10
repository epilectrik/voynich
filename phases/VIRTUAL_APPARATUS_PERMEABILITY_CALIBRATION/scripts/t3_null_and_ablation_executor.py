"""
T3: Null and Ablation Executor
===============================
Phase 565 - VIRTUAL_APPARATUS_PERMEABILITY_CALIBRATION

Runs 9 baselines (B1-B9) + 4 null models (N1-N4, 50 perms each) for the
20 pilot folios through the permeability calibration apparatus.

Total: 9 baselines x 20 folios + 4 nulls x 20 folios x 50 perms
     = 180 + 4000 = 4,180 runs

Input:
  - t2b_supervisory_interface_unrouted.json  (per-token supervisory contributions)
  - t1_permeability_apparatus.json           (apparatus spec, folio infra scores)
  - t3_line_packets.json                     (line-level packet_phase)
  - regime_folio_mapping.json                (regime assignments for profile)
  - t2_folio_budgets.json                    (folio budgets for profile assignment)

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
from datetime import datetime

# ---------------------------------------------------------------------------
# Import permeability apparatus (Phase 565 T1)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = PHASE_DIR.parent.parent

sys.path.insert(0, str(SCRIPT_DIR))
from t1_permeability_apparatus import (
    PermeabilityApparatus, build_configured_apparatus,
    STATE_VARS, HAZARD_BOUNDARIES, N_VARS, EQUILIBRIUM, SV_INDEX,
    PILOT_FOLIOS, GAMMA_CORRIDOR, CORRIDOR_MULT, Q1, Q2_BASE, Q3_BASE,
    GAMMA_BASIN, BETA1, BETA2, BASIN_MULT, EDGE1_MULT, EDGE2_MULT,
    PROFILE_DECAYS, A3_DECAY, CONFIG_MODES, K_RELIEF, HAZARD_DEV,
    compute_infra_scores
)

# Import PROFILES and assign_folio_profiles from the coupling phase
sys.path.insert(0, str(PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'scripts'))
from t1_apparatus_family_builder import PROFILES, assign_folio_profiles

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
T2B_PATH = (PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'results'
            / 't2b_supervisory_interface_unrouted.json')
T1_565_PATH = PHASE_DIR / 'results' / 't1_permeability_apparatus.json'
PACKETS_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
                / 'results' / 't3_line_packets.json')
REGIME_PATH = PROJECT_ROOT / 'data' / 'regime_folio_mapping.json'
BUDGET_PATH = (PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
               / 'results' / 't2_folio_budgets.json')
OUTPUT_PATH = PHASE_DIR / 'results' / 't3_null_ablation_runs.json'

# ---------------------------------------------------------------------------
# Routing constants (same as Phase 564 T2/T3)
# ---------------------------------------------------------------------------
ROUTING_EFFECTS = {
    'r': {'boost': {'X': 1.4}, 'suppress': {'S': 0.6, 'C': 0.7, 'Y': 0.7}},
    'y': {'boost': {'T': 1.4}, 'suppress': {'X': 0.7, 'C': 0.7}},
    'h': {'boost': {'TR': 1.4, 'RC': 1.3}, 'suppress': {'X': 0.7, 'T': 0.7}},
    'm': {'boost': {'C': 1.4}, 'suppress': {'T': 0.7, 'X': 0.7, 'TR': 0.7}},
    'n': {'boost': {'S': 1.2}, 'suppress': {'X': 0.8, 'T': 0.8}},
    'l': {'boost': {'TR': 1.2, 'S': 1.2}, 'suppress': {'X': 0.8}},
}

ROUTING_CONTRIB_GAIN = 0.3
ROUTING_DECAY = 0.7

# Excursion tracking thresholds
QUIET_LO, QUIET_HI = 0.4, 0.6
EXCURSION_LO, EXCURSION_HI = 0.35, 0.65
MAX_CYCLE_DURATION = 50

# Process SVs (those with at least one hazard boundary, excludes Y)
PROCESS_SVS = [sv for sv in STATE_VARS
               if HAZARD_BOUNDARIES[sv][0] is not None
               or HAZARD_BOUNDARIES[sv][1] is not None]
PROCESS_IDX = [SV_INDEX[sv] for sv in PROCESS_SVS]

# Profile rotation for B6
PROFILE_ROTATION = {
    'A1_BATH_REFLUX': 'A2_SEALED_RECIRCULATION',
    'A2_SEALED_RECIRCULATION': 'A3_DISTILL_COLLECT',
    'A3_DISTILL_COLLECT': 'A1_BATH_REFLUX',
}


# ---------------------------------------------------------------------------
# UniformRestoringApparatus for B9 (4-zone version)
# ---------------------------------------------------------------------------
class UniformRestoringApparatus:
    """
    Wraps PermeabilityApparatus but replaces the 4-zone piecewise
    restoring force with uniform corridor-level restoring everywhere.

    No basin weakness, no warning band, no hard-stop.
    rf = gamma_corridor[sv] * dev * corridor_mult[phase][sv]
    for ALL deviations regardless of magnitude.
    """

    def __init__(self, base_apparatus):
        self.base = base_apparatus
        self.sensitivity = base_apparatus.sensitivity
        self.profile_name = base_apparatus.profile_name
        self.config_mode = base_apparatus.config_mode

    def _uniform_restoring_force(self, state, packet_phase='WORK'):
        """Uniform corridor restoring: no zones, just gamma_corridor * dev * corridor_mult."""
        rf = [0.0] * N_VARS
        zones = ['CORRIDOR'] * N_VARS  # Always report CORRIDOR

        for i, sv in enumerate(STATE_VARS):
            dev = state[i] - EQUILIBRIUM
            abs_dev = abs(dev)
            sign_dev = 1.0 if dev >= 0 else -1.0

            # Apply config mode corridor multipliers for CLOSE phase on C and S
            corridor_mult_extra = 1.0
            if packet_phase == 'CLOSE':
                if sv == 'C':
                    corridor_mult_extra = self.base.config['close_corridor_C_mult']
                elif sv == 'S':
                    corridor_mult_extra = self.base.config['close_corridor_S_mult']

            rf[i] = (self.base.gamma_corridor[sv] * dev
                     * CORRIDOR_MULT[packet_phase][sv]
                     * corridor_mult_extra)

            # Stability limiter (same as base apparatus)
            if abs_dev > 1e-10:
                max_rf = 0.8 * abs_dev * sign_dev
                if abs(rf[i]) > abs(max_rf):
                    rf[i] = max_rf

        return rf, zones

    def update(self, state, dV, packet_phase='WORK', cts=0.0, permissivity=None):
        """
        Same as PermeabilityApparatus.update but with uniform restoring.
        """
        # 1. Cross-coupling (use base apparatus method)
        cc_raw = self.base._cross_coupling(state, packet_phase)
        bias = self.base.equil_bias[packet_phase]
        cc = [cc_raw[i] - bias[i] for i in range(N_VARS)]

        # 2. Uniform restoring force (replaces piecewise zones)
        rf, zones = self._uniform_restoring_force(state, packet_phase)

        # 3. Discharge events (same as base)
        discharge, events = self.base._discharge_events(state, packet_phase, cts)

        # 4. State update
        new_state = []
        for i in range(N_VARS):
            v = state[i] + dV[i] + cc[i] - rf[i] + discharge[i]
            new_state.append(max(0.0, min(1.0, v)))

        diagnostics = {
            'zones': {STATE_VARS[i]: zones[i] for i in range(N_VARS)},
            'discharge_events': events,
        }

        return new_state, diagnostics


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
# Excursion tracking helpers
# ---------------------------------------------------------------------------
def _is_quiet(state):
    """All process SVs in [QUIET_LO, QUIET_HI]."""
    return all(QUIET_LO <= state[i] <= QUIET_HI for i in PROCESS_IDX)


def _is_excursion(state):
    """Any process SV outside [EXCURSION_LO, EXCURSION_HI]."""
    return any(state[i] < EXCURSION_LO or state[i] > EXCURSION_HI
               for i in PROCESS_IDX)


def _excursion_peak(state):
    """Maximum deviation from equilibrium among process SVs."""
    return max(abs(state[i] - EQUILIBRIUM) for i in PROCESS_IDX)


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
# Zone classification for 4-zone tracking
# ---------------------------------------------------------------------------
def _classify_zone(sv, dev_abs):
    """Classify a deviation into one of the 4 zones for tracking."""
    q2 = Q2_BASE[sv]
    q3 = q2 + 0.05
    q3 = min(q3, HAZARD_DEV[sv] - 0.01)

    if dev_abs < Q1:
        return 'BASIN'
    elif dev_abs < q2:
        return 'CORRIDOR'
    elif dev_abs < q3:
        return 'WARNING'
    else:
        return 'HARD_STOP'


# ---------------------------------------------------------------------------
# Core execution function (adapted for PermeabilityApparatus with 4-zone)
# ---------------------------------------------------------------------------
def run_permeability_trace(apparatus, tokens, line_packets,
                           disable_routing=False, disable_cts=False,
                           disable_discharge=False, force_phase=None,
                           override_contributions=None,
                           override_permissivity=None):
    """
    Run one folio through the permeability apparatus with routing buffer.

    Parameters
    ----------
    apparatus : PermeabilityApparatus or UniformRestoringApparatus
    tokens : list of token dicts, pre-sorted by (line, line_pos)
    line_packets : dict mapping "folio|line" -> packet info
    disable_routing : bool - if True, ignore all routing events
    disable_cts : bool - if True, force cts=0 for all tokens
    disable_discharge : bool - if True, skip discharge events
    force_phase : str or None - if set, override all packet_phase values
    override_contributions : list or None - if set, replace all token contributions
    override_permissivity : str - 'zero' to zero out permissivity buffer

    Returns
    -------
    dict with viability, Y_final, hazard counts, excursion tracking,
    zone occupancy, warning_contacts, hard_stop_contacts
    """
    n_tokens = len(tokens)
    if n_tokens == 0:
        return {
            'viability': 1.0,
            'Y_final': 0.5,
            'n_hazard_events': 0,
            'excursion_count': 0,
            'bounded_excursion_count': 0,
            'zone_occupancy': {},
            'warning_contacts': 0,
            'hard_stop_contacts': 0,
        }

    state = [EQUILIBRIUM] * N_VARS
    routing_contrib_buffer = [0.0] * N_VARS
    permissivity_buffer = {}
    prev_line = None

    # Accumulators
    n_viable = 0
    hazard_count = 0

    # Zone occupancy tracking: per SV count how many tokens in each zone (4-zone)
    zone_counts = {sv: {'BASIN': 0, 'CORRIDOR': 0, 'WARNING': 0, 'HARD_STOP': 0}
                   for sv in STATE_VARS}

    # Edge contact tracking (WARNING and HARD_STOP contacts across any SV)
    warning_contacts = 0
    hard_stop_contacts = 0

    # Excursion cycle tracking
    excursion_events = []
    in_excursion = False
    excursion_start = None
    excursion_peak_dev = 0.0

    for tok_idx, tok in enumerate(tokens):
        current_line = tok.get('line', '?')
        folio = tok.get('folio', '')

        # 1. Reset routing buffers at line boundaries
        if current_line != prev_line:
            routing_contrib_buffer = [0.0] * N_VARS
            permissivity_buffer = {}
            prev_line = current_line

        # 2. Routing event -> update both buffers (unless disabled)
        if not disable_routing:
            if tok.get('routing_active') and tok.get('routing_terminal'):
                rt = tok['routing_terminal']
                if rt in ROUTING_EFFECTS:
                    effects = ROUTING_EFFECTS[rt]
                    for sv, mult in effects.get('boost', {}).items():
                        routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN
                    for sv, mult in effects.get('suppress', {}).items():
                        routing_contrib_buffer[SV_INDEX[sv]] += (mult - 1.0) * ROUTING_CONTRIB_GAIN

        # 3. Look up packet_phase from line_packets
        if force_phase is not None:
            packet_phase = force_phase
        else:
            line_key = f"{folio}|{current_line}"
            packet = line_packets.get(line_key)
            if packet and 'packet_state' in packet:
                packet_phase = packet['packet_state'].get('packet_phase', 'WORK')
            else:
                packet_phase = tok.get('packet_phase', 'WORK')

        # 4. Get CTS from token (unless disabled)
        cts = 0.0 if disable_cts else tok.get('cts', 0.0)

        # 5. Compute buffered dV
        if override_contributions is not None:
            contributions = override_contributions
        else:
            contributions = tok['contributions']

        dV = [0.0] * N_VARS
        for i, sv in enumerate(STATE_VARS):
            base_sens = apparatus.sensitivity[sv]
            dV[i] = contributions[i] * base_sens * (1.0 + routing_contrib_buffer[i])

        # 6. Build permissivity for this step
        if override_permissivity == 'zero':
            perm = None
        elif not disable_routing and permissivity_buffer:
            # Map routing-induced threshold shifts to per-SV permissivity
            perm = {}
            for key, val in permissivity_buffer.items():
                # Map threshold effect keys to SV permissivity shifts
                if 'X' in key:
                    perm['X'] = perm.get('X', 0.0) + val * 0.5
                elif 'T' in key:
                    perm['T'] = perm.get('T', 0.0) + val * 0.5
                elif 'C' in key:
                    perm['C'] = perm.get('C', 0.0) + val * 0.5
                elif 'S' in key:
                    perm['S'] = perm.get('S', 0.0) + val * 0.5
            if not perm:
                perm = None
        else:
            perm = None

        # 7. Update state via apparatus
        if disable_discharge:
            # Run update but zero out discharge contribution
            if hasattr(apparatus, 'base'):
                # UniformRestoringApparatus
                cc_raw = apparatus.base._cross_coupling(state, packet_phase)
                bias = apparatus.base.equil_bias[packet_phase]
                cc = [cc_raw[i] - bias[i] for i in range(N_VARS)]
                rf, zones = apparatus._uniform_restoring_force(state, packet_phase)
            else:
                cc_raw = apparatus._cross_coupling(state, packet_phase)
                bias = apparatus.equil_bias[packet_phase]
                cc = [cc_raw[i] - bias[i] for i in range(N_VARS)]
                rf, zones = apparatus._restoring_force(state, packet_phase, perm)
            # No discharge
            new_state = []
            for i in range(N_VARS):
                v = state[i] + dV[i] + cc[i] - rf[i]
                new_state.append(max(0.0, min(1.0, v)))
            state = new_state
            diagnostics = {
                'zones': {STATE_VARS[i]: zones[i] for i in range(N_VARS)},
                'discharge_events': [],
            }
        else:
            state, diagnostics = apparatus.update(state, dV, packet_phase, cts, perm)

        # 8. Decay routing buffers
        if not disable_routing:
            routing_contrib_buffer = [a * ROUTING_DECAY for a in routing_contrib_buffer]
            new_perm = {}
            for k, v in permissivity_buffer.items():
                decayed = v * ROUTING_DECAY
                if abs(decayed) > 1e-10:
                    new_perm[k] = decayed
            permissivity_buffer = new_perm

        # 9. Track zone occupancy (4-zone classification)
        zones = diagnostics.get('zones', {})
        token_has_warning = False
        token_has_hard_stop = False
        for sv in STATE_VARS:
            z = zones.get(sv, 'CORRIDOR')
            if z in zone_counts[sv]:
                zone_counts[sv][z] += 1
            if z == 'WARNING':
                token_has_warning = True
            elif z == 'HARD_STOP':
                token_has_hard_stop = True

        # Track edge contacts (any SV in WARNING or HARD_STOP for this token)
        if token_has_warning:
            warning_contacts += 1
        if token_has_hard_stop:
            hard_stop_contacts += 1

        # 10. Check hazards
        if is_in_bounds(state):
            n_viable += 1
        else:
            hazard_count += 1

        # 11. Excursion cycle tracking
        quiet_now = _is_quiet(state)
        peak_dev = _excursion_peak(state)

        if not in_excursion:
            if not quiet_now:
                in_excursion = True
                excursion_start = tok_idx
                excursion_peak_dev = peak_dev
        else:
            if peak_dev > excursion_peak_dev:
                excursion_peak_dev = peak_dev
            if quiet_now:
                duration = tok_idx - excursion_start
                bounded = (excursion_peak_dev > (EQUILIBRIUM - EXCURSION_LO)
                           and duration <= MAX_CYCLE_DURATION)
                excursion_events.append({
                    'start_idx': excursion_start,
                    'end_idx': tok_idx,
                    'duration': duration,
                    'peak_deviation': round(excursion_peak_dev, 5),
                    'bounded': bounded,
                })
                in_excursion = False
                excursion_start = None
                excursion_peak_dev = 0.0

    # Build zone occupancy summary (fractions) - 4-zone
    zone_occupancy = {}
    for sv in STATE_VARS:
        total = sum(zone_counts[sv].values())
        if total > 0:
            zone_occupancy[sv] = {
                z: round(c / total, 4) for z, c in zone_counts[sv].items()
            }
        else:
            zone_occupancy[sv] = {'BASIN': 0.0, 'CORRIDOR': 0.0,
                                  'WARNING': 0.0, 'HARD_STOP': 0.0}

    n_excursion = len(excursion_events)
    n_bounded = sum(1 for e in excursion_events if e['bounded'])

    return {
        'viability': round(n_viable / n_tokens, 6) if n_tokens > 0 else 1.0,
        'Y_final': round(state[SV_INDEX['Y']], 6),
        'n_hazard_events': hazard_count,
        'excursion_count': n_excursion,
        'bounded_excursion_count': n_bounded,
        'zone_occupancy': zone_occupancy,
        'warning_contacts': warning_contacts,
        'hard_stop_contacts': hard_stop_contacts,
    }


# ---------------------------------------------------------------------------
# Null model generators
# ---------------------------------------------------------------------------

def null_n1_token_shuffle(tokens, rng):
    """N1: Shuffle ALL tokens within a folio (across lines).
    Destroys line structure, token sequence, and routing context."""
    shuffled = list(tokens)
    rng.shuffle(shuffled)
    # Reassign positional info from original order
    for i, orig in enumerate(tokens):
        shuffled[i] = dict(shuffled[i])
        shuffled[i]['line'] = orig['line']
        shuffled[i]['line_pos'] = orig['line_pos']
        shuffled[i]['folio'] = orig['folio']
    return shuffled


def null_n2_domain_preserve_shuffle(tokens, rng):
    """N2: Shuffle tokens within each domain (HEADED/HEADLESS) separately
    within a folio. Preserves domain proportions but destroys within-domain
    sequence."""
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


def null_n3_line_shuffle(tokens, rng):
    """N3: Shuffle entire lines within a folio. Keep tokens within each line
    intact, but randomize line order. Destroys line sequence but preserves
    intra-line structure."""
    # Group tokens by line
    line_groups = {}
    for tok in tokens:
        ln = tok['line']
        if ln not in line_groups:
            line_groups[ln] = []
        line_groups[ln].append(tok)

    # Get original line order
    line_order = list(line_groups.keys())
    # Shuffle the line order
    shuffled_order = list(line_order)
    rng.shuffle(shuffled_order)

    # Rebuild token list with shuffled line order but reassigned line numbers
    new_tokens = []
    for new_line, old_line in zip(line_order, shuffled_order):
        for tok in line_groups[old_line]:
            nt = dict(tok)
            nt['line'] = new_line  # Assign to the new position
            new_tokens.append(nt)
    return new_tokens


def null_n4_within_line_shuffle(tokens, rng):
    """N4: For each line, shuffle token order within the line.
    Preserves line boundaries but destroys intra-line sequence."""
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
    print("Phase 565 - VIRTUAL_APPARATUS_PERMEABILITY_CALIBRATION")
    print("=" * 70)

    # --- Load inputs ---
    print("\nLoading inputs...")

    with open(T2B_PATH, 'r', encoding='utf-8') as f:
        t2b_data = json.load(f)
    all_tokens = t2b_data['token_signals']
    print(f"  T2b tokens: {len(all_tokens)}")

    with open(T1_565_PATH, 'r', encoding='utf-8') as f:
        t1_data = json.load(f)
    infra_scores = t1_data['folio_infra_scores']
    print(f"  565 infra scores: {len(infra_scores)} folios")

    with open(PACKETS_PATH, 'r', encoding='utf-8') as f:
        packets_data = json.load(f)
    line_packets = packets_data['line_packets']
    print(f"  Line packets: {len(line_packets)}")

    # --- Load folio profile assignments from assign_folio_profiles ---
    print("\n  Loading folio profile assignments...")
    folio_assignments = assign_folio_profiles(REGIME_PATH, BUDGET_PATH)
    print(f"  Folio assignments: {len(folio_assignments)}")

    # --- Group tokens by folio ---
    tokens_by_folio = defaultdict(list)
    for tok in all_tokens:
        tokens_by_folio[tok['folio']].append(tok)

    # Sort tokens within each folio
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    print(f"  Unique folios in T2b: {len(tokens_by_folio)}")

    # --- Pre-compute folio mean contributions ---
    print("\nPre-computing folio means...")
    folio_contrib_sums = defaultdict(lambda: [0.0] * N_VARS)
    folio_contrib_counts = defaultdict(int)
    for tok in all_tokens:
        fid = tok['folio']
        contribs = tok['contributions']
        for i in range(N_VARS):
            folio_contrib_sums[fid][i] += contribs[i]
        folio_contrib_counts[fid] += 1

    folio_mean_contribs = {}
    for fid in folio_contrib_sums:
        n = folio_contrib_counts[fid]
        folio_mean_contribs[fid] = [folio_contrib_sums[fid][i] / n for i in range(N_VARS)]
    print(f"  Folio mean contribs: {len(folio_mean_contribs)} folios")

    # --- Determine preferred profile and config mode for each pilot folio ---
    pilot_folio_list = sorted(PILOT_FOLIOS)
    print(f"\nPilot folios: {len(pilot_folio_list)}")

    folio_profile = {}
    folio_config_mode = {}
    for folio in pilot_folio_list:
        # Preferred profile from assign_folio_profiles
        assignment = folio_assignments.get(folio, {})
        profile = assignment.get('preferred_profile', 'A2_SEALED_RECIRCULATION')
        folio_profile[folio] = profile

        # Config mode from 565 T1 infra scores
        infra = infra_scores.get(folio, {})
        config_mode = infra.get('config_mode', 'H1_MEDIUM_INFRA')
        folio_config_mode[folio] = config_mode

        n_toks = len(tokens_by_folio.get(folio, []))
        print(f"  {folio}: profile={profile}, config={config_mode}, "
              f"n_tokens={n_toks}")

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
        apparatus = build_configured_apparatus(profile, config_mode)

        result = run_permeability_trace(apparatus, toks, line_packets)
        reference[folio] = result
        run_count += 1

        print(f"  {folio}: viab={result['viability']:.4f}, "
              f"haz={result['n_hazard_events']}, Y={result['Y_final']:.4f}, "
              f"exc={result['excursion_count']}, "
              f"bnd={result['bounded_excursion_count']}, "
              f"warn={result['warning_contacts']}, "
              f"hard={result['hard_stop_contacts']}")

    # === BASELINES (9 types x 20 folios = 180 runs) ===
    print("\n" + "=" * 70)
    print("BASELINES (9 types x 20 folios = 180 runs)")
    print("=" * 70)

    baseline_runs = {f'B{i}': [] for i in range(1, 10)}

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]
        folio_mean = folio_mean_contribs.get(folio, [0.0] * N_VARS)

        # --- B1: Folio-mean contributions ---
        b1_toks = []
        for t in toks:
            nt = dict(t)
            nt['contributions'] = list(folio_mean)
            b1_toks.append(nt)
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_permeability_trace(apparatus, b1_toks, line_packets)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B1'].append(r)
        run_count += 1
        print(f"  B1 {folio}... done (viab={r['viability']:.4f})")

        # --- B2: Zero contributions ---
        b2_toks = []
        for t in toks:
            nt = dict(t)
            nt['contributions'] = [0.0] * N_VARS
            b2_toks.append(nt)
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_permeability_trace(apparatus, b2_toks, line_packets)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B2'].append(r)
        run_count += 1
        print(f"  B2 {folio}... done (viab={r['viability']:.4f})")

        # --- B3: No CTS ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_permeability_trace(apparatus, toks, line_packets, disable_cts=True)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B3'].append(r)
        run_count += 1
        print(f"  B3 {folio}... done (viab={r['viability']:.4f})")

        # --- B4: No routing ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_permeability_trace(apparatus, toks, line_packets, disable_routing=True)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B4'].append(r)
        run_count += 1
        print(f"  B4 {folio}... done (viab={r['viability']:.4f})")

        # --- B5: No config mode (force H1_MEDIUM_INFRA) ---
        apparatus = build_configured_apparatus(profile, 'H1_MEDIUM_INFRA')
        r = run_permeability_trace(apparatus, toks, line_packets)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B5'].append(r)
        run_count += 1
        print(f"  B5 {folio}... done (viab={r['viability']:.4f})")

        # --- B6: Shuffle profiles (rotate: A1->A2->A3->A1) ---
        wrong_profile = PROFILE_ROTATION.get(profile, 'A2_SEALED_RECIRCULATION')
        apparatus = build_configured_apparatus(wrong_profile, config_mode)
        r = run_permeability_trace(apparatus, toks, line_packets)
        r['folio'] = folio
        r['profile'] = wrong_profile
        r['original_profile'] = profile
        baseline_runs['B6'].append(r)
        run_count += 1
        print(f"  B6 {folio}... done (viab={r['viability']:.4f}) "
              f"[{profile}->{wrong_profile}]")

        # --- B7: No discharge events ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_permeability_trace(apparatus, toks, line_packets,
                                   disable_discharge=True)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B7'].append(r)
        run_count += 1
        print(f"  B7 {folio}... done (viab={r['viability']:.4f})")

        # --- B8: No phase-specific multipliers (force WORK phase everywhere) ---
        apparatus = build_configured_apparatus(profile, config_mode)
        r = run_permeability_trace(apparatus, toks, line_packets,
                                   force_phase='WORK')
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B8'].append(r)
        run_count += 1
        print(f"  B8 {folio}... done (viab={r['viability']:.4f})")

        # --- B9: Uniform restoring (no piecewise zones) ---
        base_apparatus = build_configured_apparatus(profile, config_mode)
        uniform_apparatus = UniformRestoringApparatus(base_apparatus)
        r = run_permeability_trace(uniform_apparatus, toks, line_packets)
        r['folio'] = folio
        r['profile'] = profile
        baseline_runs['B9'].append(r)
        run_count += 1
        print(f"  B9 {folio}... done (viab={r['viability']:.4f})")

    # Print baseline summary
    print("\n  Baseline summary:")
    for bname in sorted(baseline_runs.keys()):
        bdata = baseline_runs[bname]
        if bdata:
            viabs = [r['viability'] for r in bdata]
            mean_v = sum(viabs) / len(viabs)
            print(f"    {bname}: mean_viab={mean_v:.4f}, n_folios={len(viabs)}")

    # === NULL MODELS (4 types x 20 folios x 50 perms = 4,000 runs) ===
    print("\n" + "=" * 70)
    print("NULL MODELS (4 types x 20 folios x 50 perms = 4,000 runs)")
    print("=" * 70)

    N_PERMS = 50
    null_runs = {
        'N1': {},
        'N2': {},
        'N3': {},
        'N4': {},
    }

    for folio in pilot_folio_list:
        toks = tokens_by_folio.get(folio, [])
        if not toks:
            continue

        profile = folio_profile[folio]
        config_mode = folio_config_mode[folio]

        # Initialize null result containers
        for null_name in null_runs:
            null_runs[null_name][folio] = {
                'viabilities': [],
                'Y_finals': [],
                'warning_contacts': [],
                'hard_stop_contacts': [],
            }

        for perm_idx in range(N_PERMS):
            # --- N1: Token shuffle ---
            rng1 = random.Random(42 + perm_idx)
            n1_toks = null_n1_token_shuffle(toks, rng1)
            apparatus = build_configured_apparatus(profile, config_mode)
            r1 = run_permeability_trace(apparatus, n1_toks, line_packets)
            null_runs['N1'][folio]['viabilities'].append(r1['viability'])
            null_runs['N1'][folio]['Y_finals'].append(r1['Y_final'])
            null_runs['N1'][folio]['warning_contacts'].append(r1['warning_contacts'])
            null_runs['N1'][folio]['hard_stop_contacts'].append(r1['hard_stop_contacts'])
            run_count += 1

            # --- N2: Domain-preserving shuffle ---
            rng2 = random.Random(42 + perm_idx)
            n2_toks = null_n2_domain_preserve_shuffle(toks, rng2)
            apparatus = build_configured_apparatus(profile, config_mode)
            r2 = run_permeability_trace(apparatus, n2_toks, line_packets)
            null_runs['N2'][folio]['viabilities'].append(r2['viability'])
            null_runs['N2'][folio]['Y_finals'].append(r2['Y_final'])
            null_runs['N2'][folio]['warning_contacts'].append(r2['warning_contacts'])
            null_runs['N2'][folio]['hard_stop_contacts'].append(r2['hard_stop_contacts'])
            run_count += 1

            # --- N3: Line shuffle ---
            rng3 = random.Random(42 + perm_idx)
            n3_toks = null_n3_line_shuffle(toks, rng3)
            apparatus = build_configured_apparatus(profile, config_mode)
            r3 = run_permeability_trace(apparatus, n3_toks, line_packets)
            null_runs['N3'][folio]['viabilities'].append(r3['viability'])
            null_runs['N3'][folio]['Y_finals'].append(r3['Y_final'])
            null_runs['N3'][folio]['warning_contacts'].append(r3['warning_contacts'])
            null_runs['N3'][folio]['hard_stop_contacts'].append(r3['hard_stop_contacts'])
            run_count += 1

            # --- N4: Within-line shuffle ---
            rng4 = random.Random(42 + perm_idx)
            n4_toks = null_n4_within_line_shuffle(toks, rng4)
            apparatus = build_configured_apparatus(profile, config_mode)
            r4 = run_permeability_trace(apparatus, n4_toks, line_packets)
            null_runs['N4'][folio]['viabilities'].append(r4['viability'])
            null_runs['N4'][folio]['Y_finals'].append(r4['Y_final'])
            null_runs['N4'][folio]['warning_contacts'].append(r4['warning_contacts'])
            null_runs['N4'][folio]['hard_stop_contacts'].append(r4['hard_stop_contacts'])
            run_count += 1

            if perm_idx % 10 == 9:
                elapsed = time.time() - t0
                print(f"  N1-N4 {folio} perm {perm_idx + 1}/50... "
                      f"({run_count} total runs, {elapsed:.1f}s)")

    # Compute null summaries
    for null_name in null_runs:
        for folio in null_runs[null_name]:
            entry = null_runs[null_name][folio]
            viabs = entry['viabilities']
            y_finals = entry['Y_finals']
            warn_contacts = entry['warning_contacts']
            hard_contacts = entry['hard_stop_contacts']
            n_p = len(viabs)
            if n_p == 0:
                continue

            viab_mean = sum(viabs) / n_p
            viab_std = math.sqrt(
                sum((v - viab_mean) ** 2 for v in viabs) / n_p)
            y_mean = sum(y_finals) / n_p
            warn_mean = sum(warn_contacts) / n_p
            hard_mean = sum(hard_contacts) / n_p

            entry['mean_viab'] = round(viab_mean, 6)
            entry['std_viab'] = round(viab_std, 6)
            entry['mean_Y_final'] = round(y_mean, 6)
            entry['mean_warning_contacts'] = round(warn_mean, 2)
            entry['mean_hard_stop_contacts'] = round(hard_mean, 2)
            # Round raw arrays for storage
            entry['viabilities'] = [round(v, 6) for v in viabs]
            entry['Y_finals'] = [round(v, 6) for v in y_finals]
            # Keep warning/hard_stop contact arrays as integers (no rounding needed)

    # Print null summary
    print("\n  Null summary:")
    for null_name in sorted(null_runs.keys()):
        viab_means = [null_runs[null_name][f].get('mean_viab', 0.0)
                      for f in null_runs[null_name]
                      if 'mean_viab' in null_runs[null_name][f]]
        if viab_means:
            overall_mean = sum(viab_means) / len(viab_means)
            print(f"    {null_name}: overall_mean_viab={overall_mean:.4f}, "
                  f"n_folios={len(viab_means)}")

    # === Assemble output ===
    elapsed = time.time() - t0
    print(f"\nTotal runs: {run_count} in {elapsed:.1f}s")

    output = {
        'metadata': {
            'phase': '565',
            'task': 'T3',
            'timestamp': datetime.now().isoformat(),
            'n_baselines': sum(len(v) for v in baseline_runs.values()),
            'n_nulls': sum(
                len(null_runs[nn][f].get('viabilities', []))
                for nn in null_runs for f in null_runs[nn]
            ),
            'n_total': run_count,
            'elapsed_seconds': round(elapsed, 2),
            'n_perms': N_PERMS,
            'n_pilot_folios': len(pilot_folio_list),
        },
        'reference': reference,
        'baseline_runs': baseline_runs,
        'null_runs': null_runs,
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

    # Build per-folio baseline lookup
    baseline_by_folio = {f'B{i}': {} for i in range(1, 10)}
    for bname, blist in baseline_runs.items():
        for entry in blist:
            baseline_by_folio[bname][entry['folio']] = entry['viability']

    # Reference vs baseline vs null comparison
    bnames = [f'B{i}' for i in range(1, 10)]
    nnames = ['N1', 'N2', 'N3', 'N4']

    header_b = ' '.join(f'{b:>7}' for b in bnames)
    header_n = ' '.join(f'{n:>7}' for n in nnames)
    print(f"\n  {'Folio':<8} {'Ref':>7} | {header_b} | {header_n}")
    divider_b = ' '.join('-' * 7 for _ in bnames)
    divider_n = ' '.join('-' * 7 for _ in nnames)
    print(f"  {'-' * 8} {'-' * 7} | {divider_b} | {divider_n}")

    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        ref_v = reference[folio]['viability']
        b_vals = []
        for bn in bnames:
            v = baseline_by_folio[bn].get(folio, 0.0)
            b_vals.append(f"{v:>7.4f}")
        n_vals = []
        for nn in nnames:
            v = null_runs[nn].get(folio, {}).get('mean_viab', 0.0)
            n_vals.append(f"{v:>7.4f}")
        print(f"  {folio:<8} {ref_v:>7.4f} | {' '.join(b_vals)} | "
              f"{' '.join(n_vals)}")

    # --- B9 Delta Analysis ---
    print(f"\n  B9 Deltas (Reference - B9):")
    print(f"  {'Folio':<8} {'Ref':>7} {'B9':>7} {'Delta':>7}")
    print(f"  {'-' * 8} {'-' * 7} {'-' * 7} {'-' * 7}")
    b9_deltas = []
    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        ref_v = reference[folio]['viability']
        b9_v = baseline_by_folio['B9'].get(folio, 0.0)
        delta = ref_v - b9_v
        b9_deltas.append(delta)
        print(f"  {folio:<8} {ref_v:>7.4f} {b9_v:>7.4f} {delta:>+7.4f}")
    if b9_deltas:
        mean_delta = sum(b9_deltas) / len(b9_deltas)
        min_delta = min(b9_deltas)
        max_delta = max(b9_deltas)
        print(f"  {'MEAN':<8} {'':>7} {'':>7} {mean_delta:>+7.4f}")
        print(f"  {'MIN':<8} {'':>7} {'':>7} {min_delta:>+7.4f}")
        print(f"  {'MAX':<8} {'':>7} {'':>7} {max_delta:>+7.4f}")

    # --- Edge Contact Comparison ---
    print(f"\n  Edge Contact Comparison (full vs null):")
    print(f"  {'Folio':<8} {'Ref_W':>6} {'Ref_H':>6} | "
          f"{'N1_W':>6} {'N1_H':>6} {'N2_W':>6} {'N2_H':>6} "
          f"{'N3_W':>6} {'N3_H':>6} {'N4_W':>6} {'N4_H':>6}")
    for folio in pilot_folio_list:
        if folio not in reference:
            continue
        ref_w = reference[folio]['warning_contacts']
        ref_h = reference[folio]['hard_stop_contacts']
        n_vals = []
        for nn in nnames:
            entry = null_runs[nn].get(folio, {})
            w = entry.get('mean_warning_contacts', 0.0)
            h = entry.get('mean_hard_stop_contacts', 0.0)
            n_vals.append(f"{w:>6.1f} {h:>6.1f}")
        print(f"  {folio:<8} {ref_w:>6} {ref_h:>6} | {' '.join(n_vals)}")

    print(f"\n  Total runs: {run_count}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("  Done.")


if __name__ == '__main__':
    main()
