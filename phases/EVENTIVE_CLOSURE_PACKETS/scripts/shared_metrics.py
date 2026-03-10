"""
shared_metrics.py — Phase 569: Single source of truth for all metric definitions.

Eliminates T1/T2 implementation divergence from Phase 568.
This is a LIBRARY MODULE — no main(), no output file.
Imported by T1 (event taxonomy), T2 (full executor), T3 (null executor).
"""

# =============================================================================
# CONSTANTS
# =============================================================================

STATE_VARS = ["T", "RC", "S", "C", "TR", "X", "Y"]
N_VARS = len(STATE_VARS)  # 7
EQUILIBRIUM = 0.5

HAZARD_BOUNDARIES = {
    "T":  [0.15, 0.85],
    "RC": [0.10, 0.90],
    "S":  [0.15, None],
    "C":  [None, 0.85],
    "TR": [0.10, 0.90],
    "X":  [None, 0.80],
    "Y":  [None, None],
}

SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}
S_IDX = SV_INDEX['S']   # 2
Y_IDX = SV_INDEX['Y']   # 6

Q1 = 0.08  # Universal basin boundary

Q2_BASE = {
    'T': 0.24, 'RC': 0.28, 'S': 0.24, 'C': 0.24,
    'TR': 0.28, 'X': 0.21, 'Y': 0.35,
}

Q3_BASE = {sv: Q2_BASE[sv] + 0.05 for sv in STATE_VARS}

HAZARD_DEV = {
    'T': 0.35, 'RC': 0.40, 'S': 0.35, 'C': 0.35,
    'TR': 0.40, 'X': 0.30, 'Y': 1.0,
}

# Process SVs: those with at least one hazard boundary (excludes Y)
PROCESS_SVS = [sv for sv in STATE_VARS
               if HAZARD_BOUNDARIES[sv][0] is not None
               or HAZARD_BOUNDARIES[sv][1] is not None]
# => ['T', 'RC', 'S', 'C', 'TR', 'X']

PROCESS_IDX = [SV_INDEX[sv] for sv in PROCESS_SVS]

# PCV process SVs: excludes S (handled asymmetrically)
PCV_PROCESS_SVS = ['T', 'RC', 'C', 'TR', 'X']

PCV_ZONE_SCORES = {
    'SPEC':  {'BASIN': 1.0, 'CORRIDOR': 0.85, 'WARNING': 0.5, 'HARD_STOP': 0.1, 'HAZARD': 0.0},
    'WORK':  {'BASIN': 0.3, 'CORRIDOR': 1.0,  'WARNING': 0.8, 'HARD_STOP': 0.3, 'HAZARD': 0.0},
    'CLOSE': {'BASIN': 1.0, 'CORRIDOR': 0.6,  'WARNING': 0.2, 'HARD_STOP': 0.0, 'HAZARD': 0.0},
}

PCV_S_HIGH_SCORES = {
    'SPEC':  0.9,
    'WORK':  1.0,
    'CLOSE': 0.9,
}

SAHB_WARNING_WEIGHT = 1.0
SAHB_HARDSTOP_WEIGHT = 3.0
SAHB_OUTSIDE_CORRIDOR_WEIGHT = 0.5
SAHB_MAX_EXCURSION_WEIGHT = 2.0

WCU_ZONE_SCORES = {
    'BASIN': 0.3,
    'CORRIDOR': 1.0,
    'WARNING': 0.1,
    'HARD_STOP': -1.0,
    'HAZARD': -2.0,
}
WCU_S_HIGH_SCORE = 1.0

# Event improvement epsilon (minimum aggregate dev decrease to count as improvement)
EIR_EPSILON = 0.005


# =============================================================================
# ZONE CLASSIFICATION
# =============================================================================

def classify_zone(sv, dev_abs):
    """Classify a deviation into one of the 5 zones: BASIN, CORRIDOR, WARNING, HARD_STOP, HAZARD."""
    q2 = Q2_BASE[sv]
    q3 = q2 + 0.05
    q3 = min(q3, HAZARD_DEV[sv] - 0.01)

    if dev_abs < Q1:
        return 'BASIN'
    elif dev_abs < q2:
        return 'CORRIDOR'
    elif dev_abs < q3:
        return 'WARNING'
    elif dev_abs < HAZARD_DEV[sv]:
        return 'HARD_STOP'
    else:
        return 'HAZARD'


def is_in_bounds(state):
    """Check if state is within all hazard boundaries."""
    for i, sv in enumerate(STATE_VARS):
        lo, hi = HAZARD_BOUNDARIES[sv]
        if lo is not None and state[i] < lo:
            return False
        if hi is not None and state[i] > hi:
            return False
    return True


# =============================================================================
# PER-TOKEN FUNCTIONS
# =============================================================================

def pcv_token_score(state, packet_phase):
    """Compute PCV score for one token. Process SVs + S asymmetric. Y excluded.
    Returns (score_sum, count)."""
    score_sum = 0.0
    count = 0
    phase_scores = PCV_ZONE_SCORES.get(packet_phase, PCV_ZONE_SCORES['WORK'])

    for sv in PCV_PROCESS_SVS:  # T, RC, C, TR, X (no S)
        i = SV_INDEX[sv]
        dev = abs(state[i] - EQUILIBRIUM)
        zone = classify_zone(sv, dev)
        if dev >= HAZARD_DEV[sv]:
            score_sum += phase_scores.get('HAZARD', 0.0)
        else:
            score_sum += phase_scores.get(zone, 0.0)
        count += 1

    # S: asymmetric handling
    s_val = state[S_IDX]
    s_dev = abs(s_val - EQUILIBRIUM)
    if s_val > EQUILIBRIUM:
        score_sum += PCV_S_HIGH_SCORES.get(packet_phase, 1.0)
    else:
        zone = classify_zone('S', s_dev)
        if s_dev >= HAZARD_DEV['S']:
            score_sum += phase_scores.get('HAZARD', 0.0)
        else:
            score_sum += phase_scores.get(zone, 0.0)
    count += 1

    return score_sum, count


def sahb_token(state, packet_phase):
    """Compute SAHB components for one token. Skip S penalty when S > EQ.
    Returns (warnings, hardstops, outside_corridor, max_excursion)."""
    warnings = 0
    hardstops = 0
    outside_corridor = 0
    max_excursion = 0.0

    for sv in PROCESS_SVS:
        i = SV_INDEX[sv]
        dev = abs(state[i] - EQUILIBRIUM)
        zone = classify_zone(sv, dev)

        if sv == 'S' and state[S_IDX] > EQUILIBRIUM:
            continue

        if zone == 'WARNING':
            warnings += 1
        elif zone == 'HARD_STOP':
            hardstops += 1

        if zone in ('WARNING', 'HARD_STOP'):
            outside_corridor += 1

        if dev > max_excursion:
            max_excursion = dev

    return warnings, hardstops, outside_corridor, max_excursion


def wcu_token(state, packet_phase):
    """Compute WCU score for one token. Only meaningful for WORK phase.
    Returns (score, n_pairs)."""
    if packet_phase != 'WORK':
        return 0.0, 0

    score = 0.0
    n_pairs = 0
    for sv in PROCESS_SVS:
        i = SV_INDEX[sv]
        dev = abs(state[i] - EQUILIBRIUM)

        if sv == 'S' and state[i] > EQUILIBRIUM:
            score += WCU_S_HIGH_SCORE
        else:
            zone = classify_zone(sv, dev)
            if dev >= HAZARD_DEV[sv]:
                score += WCU_ZONE_SCORES['HAZARD']
            else:
                score += WCU_ZONE_SCORES.get(zone, 0.0)
        n_pairs += 1

    return score, n_pairs


def wcp_token_quality(state, packet_phase):
    """Compute per-token zone quality for WCP (same logic as PCV).
    Returns normalized quality score in [0, 1]."""
    score, count = pcv_token_score(state, packet_phase)
    return score / count if count > 0 else 0.0


# =============================================================================
# PER-LINE FUNCTIONS
# =============================================================================

def compute_wcp_line(spec_scores, work_scores, close_scores,
                     has_spec, has_work, has_close):
    """Compute WCP score for one line with phase-presence masking.
    Each *_scores is a list of per-token quality values for that phase.
    Returns (wcp_val, is_full_packet) or (None, False) if no scores."""
    w_spec, w_work, w_close = 0.2, 0.5, 0.3

    spec_score = sum(spec_scores) / len(spec_scores) if spec_scores else None
    work_score = sum(work_scores) / len(work_scores) if work_scores else None
    close_score = sum(close_scores) / len(close_scores) if close_scores else None

    present = []
    scores = []
    weights = []

    if has_spec and spec_score is not None:
        present.append('SPEC')
        scores.append(spec_score)
        weights.append(w_spec)
    if has_work and work_score is not None:
        present.append('WORK')
        scores.append(work_score)
        weights.append(w_work)
    if has_close and close_score is not None:
        present.append('CLOSE')
        scores.append(close_score)
        weights.append(w_close)

    if not scores:
        return None, False

    total_w = sum(weights)
    wcp_val = sum(s * w for s, w in zip(scores, weights)) / total_w
    is_full_packet = len(present) == 3
    return wcp_val, is_full_packet


def compute_slr_line(work_end_dev, close_end_dev, corridor_return, work_quality):
    """Compute SLR for one line.
    work_end_dev: mean |dev| across non-Y SVs at WORK end
    close_end_dev: mean |dev| across non-Y SVs at CLOSE end
    corridor_return: fraction of excursion SVs resolved (0-1)
    work_quality: fraction of WORK tokens in corridor (0-1)
    Returns SLR value clamped to [-1, 1], or None if ineligible."""
    if work_end_dev <= Q1:
        return None  # ineligible

    resolution = 1.0 - (close_end_dev / work_end_dev) if work_end_dev > 1e-10 else 0.0
    slr_val = 0.5 * resolution + 0.3 * corridor_return + 0.2 * work_quality
    return max(-1.0, min(1.0, slr_val))


def compute_aggregate_dev(state):
    """Compute mean |dev| across non-Y SVs."""
    return sum(abs(state[i] - EQUILIBRIUM) for i in range(N_VARS) if i != Y_IDX) / (N_VARS - 1)


def compute_process_dev_list(state):
    """Return list of |dev| for each process SV (T, RC, S, C, TR, X). S-asymmetry NOT applied."""
    return [abs(state[SV_INDEX[sv]] - EQUILIBRIUM) for sv in PROCESS_SVS]


# =============================================================================
# EVENT SUCCESS METRICS (four-metric stack)
# =============================================================================

def compute_event_success(line_start_state, line_end_state, close_start_state,
                          work_peak_dev=None):
    """Compute the four-metric success stack for one closure event.

    Args:
        line_start_state: state at start of the line (list of 7 floats)
        line_end_state: state at end of the line (list of 7 floats)
        close_start_state: state at start of CLOSE phase within the line
        work_peak_dev: aggregate dev at work peak (for CLR), or None

    Returns dict with:
        EIR: 1 if aggregate dev decreased by >= epsilon, else 0
        ERM: fractional reduction in aggregate dev: (start - end) / start
        ESQ: PCV-style zone score at line end (CLOSE phase)
        EW: 1 if any process SV in warning/hard_stop/hazard at line end, else 0
        CA: fraction of process SVs with |dev| < Q2 at line end
        YG: Y gain during this line
        CLR: cross-line resolution if work_peak_dev provided, else None
    """
    start_dev = compute_aggregate_dev(close_start_state)
    end_dev = compute_aggregate_dev(line_end_state)

    # EIR: binary improvement with epsilon threshold
    eir = 1 if (start_dev - end_dev) >= EIR_EPSILON else 0

    # ERM: fractional resolution magnitude
    erm = (start_dev - end_dev) / start_dev if start_dev > 1e-10 else 0.0

    # ESQ: PCV-style end-state quality at CLOSE phase
    esq_score, esq_count = pcv_token_score(line_end_state, 'CLOSE')
    esq = esq_score / esq_count if esq_count > 0 else 0.0

    # EW: event waste — any process SV in warning/hard_stop/hazard at line end
    ew = 0
    for sv in PROCESS_SVS:
        i = SV_INDEX[sv]
        if sv == 'S' and line_end_state[i] > EQUILIBRIUM:
            continue
        dev = abs(line_end_state[i] - EQUILIBRIUM)
        zone = classify_zone(sv, dev)
        if zone in ('WARNING', 'HARD_STOP', 'HAZARD'):
            ew = 1
            break

    # CA: corridor achievement — fraction of process SVs below Q2 at line end
    n_below_q2 = 0
    n_checked = 0
    for sv in PROCESS_SVS:
        i = SV_INDEX[sv]
        if sv == 'S' and line_end_state[i] > EQUILIBRIUM:
            continue  # S above EQ is fine, don't count
        dev = abs(line_end_state[i] - EQUILIBRIUM)
        n_checked += 1
        if dev < Q2_BASE[sv]:
            n_below_q2 += 1
    ca = n_below_q2 / n_checked if n_checked > 0 else 0.0

    # YG: Y gain during this line
    yg = line_end_state[Y_IDX] - line_start_state[Y_IDX]

    # CLR: cross-line resolution (only if work_peak_dev provided)
    clr = None
    if work_peak_dev is not None and work_peak_dev > 1e-10:
        clr = 1.0 - (end_dev / work_peak_dev)

    return {
        'EIR': eir,
        'ERM': round(erm, 6),
        'ESQ': round(esq, 6),
        'EW': ew,
        'CA': round(ca, 6),
        'YG': round(yg, 6),
        'CLR': round(clr, 6) if clr is not None else None,
    }


# =============================================================================
# FOLIO-LEVEL FUNCTIONS
# =============================================================================

def compute_ueb(close_warnings, close_hardstops, unresolved_fractions,
                line_final_hardstop_count, post_line_residual_above_q2):
    """Compute Unresolved Excursion Burden.
    UEB = 1.0*warnings + 3.0*hardstops + 2.0*mean(unresolved_frac) + 5.0*line_final + 1.5*post_line
    Raw accumulation (not normalized by tokens). S above EQ excluded upstream."""
    mean_uf = (sum(unresolved_fractions) / len(unresolved_fractions)
               if unresolved_fractions else 0.0)
    return round(
        1.0 * close_warnings
        + 3.0 * close_hardstops
        + 2.0 * mean_uf
        + 5.0 * line_final_hardstop_count
        + 1.5 * post_line_residual_above_q2,
        6
    )


def compute_ewp(prolonged_hardstop, unresolved_warning,
                post_close_residual, edge_persistence):
    """Compute Edge Waste Penalty.
    EWP = 1.0*prolonged + 2.0*unresolved_warn + 3.0*post_close + 5.0*edge_persist"""
    return round(
        1.0 * prolonged_hardstop
        + 2.0 * unresolved_warning
        + 3.0 * post_close_residual
        + 5.0 * edge_persistence,
        6
    )


def compute_ref(line_work_end_devs, line_close_end_devs):
    """Compute Resolved Excursion Fraction.
    line_work_end_devs: {line_key: [dev_per_sv]}
    line_close_end_devs: {line_key: [dev_per_sv]}
    Returns (ref_mean, ref_elig_frac)."""
    ref_eligible = 0
    ref_resolved_sum = 0.0

    for lk in line_work_end_devs:
        if lk not in line_close_end_devs:
            continue
        work_devs = line_work_end_devs[lk]
        close_devs = line_close_end_devs[lk]
        for i in range(N_VARS):
            if i == Y_IDX:
                continue
            wed = work_devs[i]
            ced = close_devs[i]
            if wed > Q1:
                ref_eligible += 1
                ref_val = 1.0 - (ced / wed) if wed > 1e-10 else 0.0
                ref_resolved_sum += ref_val

    ref_mean = round(ref_resolved_sum / ref_eligible, 6) if ref_eligible > 0 else 0.0
    total_lines_with_both = sum(1 for lk in line_work_end_devs if lk in line_close_end_devs)
    total_possible_ref = total_lines_with_both * (N_VARS - 1)
    ref_elig_frac = round(ref_eligible / total_possible_ref, 6) if total_possible_ref > 0 else 0.0

    return ref_mean, ref_elig_frac


def compute_sahb(warnings, hardstops, outside_corridor, max_excursion, n_tokens):
    """Compute SAHB (folio-level, normalized by n_tokens)."""
    sahb_raw = (SAHB_WARNING_WEIGHT * warnings
                + SAHB_HARDSTOP_WEIGHT * hardstops
                + SAHB_OUTSIDE_CORRIDOR_WEIGHT * outside_corridor
                + SAHB_MAX_EXCURSION_WEIGHT * max_excursion)
    return round(sahb_raw / n_tokens, 6) if n_tokens > 0 else 0.0


# =============================================================================
# EVENT TYPE CLASSIFICATION
# =============================================================================

def classify_packet_identity(cts, mcb, cob, q4o, armed,
                             global_thresholds, section_thresholds, section):
    """Classify a CLOSE line into packet identity event types under both threshold regimes.

    Args:
        cts: Closure Tendency Score (0-1)
        mcb: m_close_bias (spike-like, 87.7% zero)
        cob: close_opacity_bias
        q4o: q4_opaque_rate (profile[14])
        armed: boolean, closure_armed
        global_thresholds: dict with fixed thresholds
        section_thresholds: dict with per-section P75 thresholds for this section
        section: section identifier (e.g. 'H', 'S', 'B', 'C')

    Returns dict:
        {"global": set of event type strings, "section_norm": set of event type strings}
    """
    global_types = set()
    section_types = set()

    # --- Global regime ---
    gt = global_thresholds
    if cts > gt.get('cts_high', 0.5):
        global_types.add('E_cts50')
    if mcb > 0:
        global_types.add('E_mcb')
    if armed:
        global_types.add('E_armed')

    # E_opaque (global): use section P75 thresholds even in global regime
    # because opacity is inherently section-dependent
    q4o_thresh = section_thresholds.get('q4_opaque_rate_p75', 0.5)
    cob_thresh = section_thresholds.get('close_opacity_bias_p75', 0.1)
    g_opaque = (q4o > q4o_thresh) or (cob > cob_thresh)
    if g_opaque:
        global_types.add('E_opaque')

    # E_compound: CTS > 0.3 AND (mcb > 0 OR armed OR opaque)
    if cts > gt.get('cts_compound', 0.3) and (mcb > 0 or armed or g_opaque):
        global_types.add('E_compound')

    # E_decisive: CTS > 0.5 AND mcb > 0 AND armed
    if cts > gt.get('cts_high', 0.5) and mcb > 0 and armed:
        global_types.add('E_decisive')

    # E_opaque_decisive: opaque AND (mcb > 0 OR armed)
    if g_opaque and (mcb > 0 or armed):
        global_types.add('E_opaque_decisive')

    # E_any is always present for CLOSE lines
    global_types.add('E_any')

    # --- Section-normalized regime ---
    st = section_thresholds
    if cts > st.get('cts_p75', gt.get('cts_high', 0.5)):
        section_types.add('E_cts50')
    if mcb > st.get('mcb_p75', 0.0):
        section_types.add('E_mcb')
    if armed:
        section_types.add('E_armed')

    s_opaque = (q4o > st.get('q4_opaque_rate_p75', 0.5)) or (cob > st.get('close_opacity_bias_p75', 0.1))
    if s_opaque:
        section_types.add('E_opaque')

    if cts > st.get('cts_compound_p75', gt.get('cts_compound', 0.3)) and \
       (mcb > st.get('mcb_p75', 0.0) or armed or s_opaque):
        section_types.add('E_compound')

    if cts > st.get('cts_p75', gt.get('cts_high', 0.5)) and \
       mcb > st.get('mcb_p75', 0.0) and armed:
        section_types.add('E_decisive')

    if s_opaque and (mcb > st.get('mcb_p75', 0.0) or armed):
        section_types.add('E_opaque_decisive')

    section_types.add('E_any')

    return {"global": global_types, "section_norm": section_types}


def classify_closure_demand(close_start_state, same_line_max_dev,
                            has_work_predecessor, work_peak_dev=None):
    """Classify closure demand qualifiers for a CLOSE line.

    Args:
        close_start_state: state at start of CLOSE phase (list of 7 floats)
        same_line_max_dev: max aggregate process dev during same line before CLOSE
        has_work_predecessor: whether preceding line is WORK
        work_peak_dev: aggregate dev at work peak of preceding line (or None)

    Returns set of demand qualifier strings.
    """
    qualifiers = set()

    # demanded: same-line max dev exceeds Q1
    if same_line_max_dev > Q1:
        qualifiers.add('demanded')

    # residualized: at least 1 process SV above corridor at CLOSE start
    for sv in PROCESS_SVS:
        i = SV_INDEX[sv]
        if sv == 'S' and close_start_state[i] > EQUILIBRIUM:
            continue
        dev = abs(close_start_state[i] - EQUILIBRIUM)
        if dev >= Q2_BASE[sv]:
            qualifiers.add('residualized')
            break

    # hard_demanded: at least 1 process SV in warning or hard_stop at CLOSE start
    for sv in PROCESS_SVS:
        i = SV_INDEX[sv]
        if sv == 'S' and close_start_state[i] > EQUILIBRIUM:
            continue
        dev = abs(close_start_state[i] - EQUILIBRIUM)
        zone = classify_zone(sv, dev)
        if zone in ('WARNING', 'HARD_STOP', 'HAZARD'):
            qualifiers.add('hard_demanded')
            break

    # work_preceded: preceding line is WORK with excursion > Q1
    if has_work_predecessor and work_peak_dev is not None and work_peak_dev > Q1:
        qualifiers.add('work_preceded')

    return qualifiers


# Global thresholds (defaults, used by classify_packet_identity)
DEFAULT_GLOBAL_THRESHOLDS = {
    'cts_high': 0.5,
    'cts_compound': 0.3,
}

# Frozen event-type priority order for PT tests
EVENT_TYPE_PRIORITY = [
    'E_decisive',
    'E_opaque_decisive',
    'E_compound',
    'E_mcb',
    'E_cts50',
    'E_opaque',
    'E_armed',
    'E_any',
]

# Canonical 20 pilot folios (from t1_close_recovery_apparatus.py)
PILOT_FOLIOS = [
    'f78r', 'f84r', 'f79r', 'f81v', 'f55r', 'f40v', 'f43v', 'f34r',
    'f31r', 'f39v', 'f95r1', 'f104r', 'f111r', 'f116r', 'f105r',
    'f108v', 'f66r', 'f85r1', 'f86v5', 'f86v6',
]
