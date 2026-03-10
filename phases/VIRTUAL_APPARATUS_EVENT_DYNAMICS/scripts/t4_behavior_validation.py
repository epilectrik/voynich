"""
T4: Behavior Validation Battery
Phase 564 - VIRTUAL_APPARATUS_EVENT_DYNAMICS

Reads T2 (coupled runs) and T3 (null/ablation runs) results, runs 9 tests
(P1-P9) plus 2 diagnostics (D1, D2), and outputs t4_behavior_validation.json.

Tests:
  P1: Viable Envelope Occupancy
  P2: Line Packet Shape Recovery
  P3: Bounded Work-Cycle Dynamics
  P4: Routing Consequence Fidelity (P4a buffered + P4b threshold-mediated)
  P5: Headless Configuration Consequence (P5a, P5b, P5c)
  P6: CTS Closure Value
  P7: Null Destruction
  P8: Preferred Profile Superiority
  P9: Section-Template Recovery (secondary, non-gating)

Diagnostics:
  D1: B7 threshold terms
  D2: B8 fixed law
"""

import json
import math
import sys
import time
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import kruskal, mannwhitneyu


class _NumpyEncoder(json.JSONEncoder):
    """Handle numpy types in JSON serialization."""
    def default(self, obj):
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATE_VARS = ['T', 'RC', 'S', 'C', 'TR', 'X', 'Y']
SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}
N_VARS = len(STATE_VARS)
PASS_THRESHOLD = 14  # out of 20 folios

# Routing target mappings for P4a: routing_terminal -> target SV
ROUTING_TARGET = {
    'r': 'X',
    'y': 'T',
    'h': 'TR',
    'm': 'C',
}
ROUTING_WINDOW = 7  # tokens after a routing event to check


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _round(v, n=5):
    """Round a value, handling None."""
    if v is None:
        return None
    return round(v, n)


def _safe_div(a, b, default=0.0):
    """Safe division."""
    return a / b if b != 0 else default


def _load_json(path):
    """Load a JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_all_data(project_root):
    """Load T2, T3, line_packets, and supervisory tokens."""
    phase_dir = project_root / 'phases' / 'VIRTUAL_APPARATUS_EVENT_DYNAMICS'
    results_dir = phase_dir / 'results'

    print("--- Loading data sources ---")

    # T2: event-gated runs
    t2_path = results_dir / 't2_event_gated_runs.json'
    print(f"  Loading T2: {t2_path}")
    t2 = _load_json(t2_path)
    print(f"    Runs: {len(t2['runs'])}, Config ablation: {len(t2['config_ablation_runs'])}")

    # T3: null/ablation runs
    t3_path = results_dir / 't3_null_ablation_runs.json'
    print(f"  Loading T3: {t3_path}")
    t3 = _load_json(t3_path)
    print(f"    Reference: {len(t3['reference'])}, Baselines: {len(t3['baselines'])}, "
          f"Nulls: {len(t3['nulls'])}")

    # Line packets (for P2: packet_phase per line)
    lp_path = (project_root / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR'
               / 'results' / 't3_line_packets.json')
    print(f"  Loading line packets: {lp_path}")
    lp_data = _load_json(lp_path)
    line_packets = lp_data['line_packets']
    print(f"    Line packets: {len(line_packets)}")

    # Supervisory tokens (for P2 packet_phase mapping and P4a routing events)
    t2b_path = (project_root / 'phases' / 'VIRTUAL_APPARATUS_COUPLING'
                / 'results' / 't2b_supervisory_interface_unrouted.json')
    print(f"  Loading supervisory tokens: {t2b_path}")
    t2b = _load_json(t2b_path)
    sup_tokens = t2b['token_signals']
    print(f"    Supervisory tokens: {len(sup_tokens)}")

    return t2, t3, line_packets, sup_tokens


# ---------------------------------------------------------------------------
# Build pilot folio metadata
# ---------------------------------------------------------------------------

def build_folio_metadata(t2, t3):
    """Extract pilot folio list and per-folio metadata from T2 runs."""
    pilot_folios = sorted(t3['reference'].keys())
    runs = t2['runs']

    folio_meta = {}
    for folio in pilot_folios:
        # Find preferred run
        pref_run = None
        all_profiles = []
        for run_key, run_data in runs.items():
            if run_data['folio'] == folio:
                all_profiles.append(run_data)
                if run_data['is_preferred']:
                    pref_run = run_data

        folio_meta[folio] = {
            'preferred_run_key': f"{folio}__{pref_run['profile']}" if pref_run else None,
            'preferred_profile': pref_run['profile'] if pref_run else None,
            'config_mode': pref_run['config_mode'] if pref_run else None,
            'section': pref_run['section'] if pref_run else None,
            'headless_rate': pref_run['headless_rate'] if pref_run else 0.0,
            'n_tokens': pref_run['summary']['n_tokens'] if pref_run else 0,
            'all_profiles': all_profiles,
        }

    return pilot_folios, folio_meta


# ---------------------------------------------------------------------------
# Build per-folio token lists (sorted by line, line_pos)
# ---------------------------------------------------------------------------

def build_folio_tokens(sup_tokens, pilot_folios, line_packets):
    """
    Build per-folio sorted token lists with packet_phase assigned.
    Returns dict: folio -> list of token dicts with 'packet_phase' field.
    """
    pilot_set = set(pilot_folios)
    tokens_by_folio = defaultdict(list)
    for tok in sup_tokens:
        if tok['folio'] in pilot_set:
            tokens_by_folio[tok['folio']].append(tok)

    def sort_key(tok):
        line = tok.get('line', '0')
        try:
            line_num = int(line)
        except (ValueError, TypeError):
            line_num = 99999
        return (line_num, tok.get('line_pos', 0.0))

    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)
        # Assign packet_phase from line_packets
        for tok in tokens_by_folio[folio]:
            lp_key = f"{tok['folio']}|{tok.get('line', '?')}"
            if lp_key in line_packets:
                tok['_packet_phase'] = line_packets[lp_key].get(
                    'packet_state', {}).get('packet_phase', 'WORK')
            else:
                tok['_packet_phase'] = 'WORK'

    return dict(tokens_by_folio)


# ---------------------------------------------------------------------------
# P1: Viable Envelope Occupancy
# ---------------------------------------------------------------------------

def test_p1(t2, t3, pilot_folios, folio_meta):
    """
    Compare preferred-profile viability vs B2 (folio-mean) and vs N1 (token shuffle).
    Pass: full>B2 for >=14/20 AND full>N1 for >=14/20.
    """
    print("\n  [P1] Viable Envelope Occupancy")
    runs = t2['runs']
    ref = t3['reference']
    b2 = t3['baselines']['B2_folio_mean']
    n1 = t3['nulls']['N1_token_shuffle']

    full_gt_b2 = 0
    full_gt_n1 = 0
    per_folio = {}

    for folio in pilot_folios:
        meta = folio_meta[folio]
        pref_key = meta['preferred_run_key']
        full_viab = runs[pref_key]['summary']['viability_fraction']
        b2_viab = b2[folio]['viability_fraction']
        n1_viab_mean = n1[folio]['viability_mean']

        gt_b2 = full_viab > b2_viab
        gt_n1 = full_viab > n1_viab_mean

        if gt_b2:
            full_gt_b2 += 1
        if gt_n1:
            full_gt_n1 += 1

        per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b2_viab': _round(b2_viab),
            'n1_viab_mean': _round(n1_viab_mean),
            'gt_b2': gt_b2,
            'gt_n1': gt_n1,
        }

    passed = full_gt_b2 >= PASS_THRESHOLD and full_gt_n1 >= PASS_THRESHOLD
    print(f"    full>B2: {full_gt_b2}/20, full>N1: {full_gt_n1}/20 -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'full_gt_B2': full_gt_b2,
        'full_gt_N1': full_gt_n1,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# P2: Line Packet Shape Recovery
# ---------------------------------------------------------------------------

def test_p2(t2, pilot_folios, folio_meta, folio_tokens):
    """
    Group trajectory states by packet_phase (SPEC/WORK/CLOSE) for each folio.
    Run Kruskal-Wallis on each SV across the 3 phases.
    Pass: >=4/7 significant SVs.
    """
    print("\n  [P2] Line Packet Shape Recovery")
    runs = t2['runs']

    # Collect all trajectory states grouped by packet_phase
    phase_states = {'SPEC': [], 'WORK': [], 'CLOSE': []}

    for folio in pilot_folios:
        meta = folio_meta[folio]
        pref_key = meta['preferred_run_key']
        trajectory = runs[pref_key].get('trajectory')
        if not trajectory:
            continue

        toks = folio_tokens.get(folio, [])
        if len(toks) != len(trajectory):
            # Mismatch: trajectory length should match token count
            # Use min of both
            n = min(len(toks), len(trajectory))
        else:
            n = len(trajectory)

        for i in range(n):
            pp = toks[i].get('_packet_phase', 'WORK')
            if pp in phase_states:
                phase_states[pp].append(trajectory[i])

    # Run Kruskal-Wallis per SV
    per_sv = {}
    n_significant = 0

    for sv_idx, sv in enumerate(STATE_VARS):
        groups = []
        for phase in ['SPEC', 'WORK', 'CLOSE']:
            vals = [s[sv_idx] for s in phase_states[phase]]
            groups.append(vals)

        # Need at least 2 groups with data
        valid_groups = [g for g in groups if len(g) >= 2]
        if len(valid_groups) < 2:
            per_sv[sv] = {'H': None, 'p': None, 'sig': False,
                          'group_sizes': [len(g) for g in groups]}
            continue

        try:
            H_stat, p_val = kruskal(*valid_groups)
        except ValueError:
            H_stat, p_val = 0.0, 1.0

        sig = p_val < 0.05
        if sig:
            n_significant += 1

        per_sv[sv] = {
            'H': _round(H_stat, 4),
            'p': _round(p_val, 6),
            'sig': sig,
            'group_sizes': [len(g) for g in groups],
            'group_means': [_round(sum(g) / len(g), 5) if g else None
                            for g in groups],
        }

    passed = n_significant >= 4
    print(f"    Significant SVs: {n_significant}/7 -> {'PASS' if passed else 'FAIL'}")
    for sv, info in per_sv.items():
        tag = "*" if info['sig'] else " "
        print(f"      {tag} {sv}: H={info['H']}, p={info['p']}")

    return {
        'pass': passed,
        'n_significant': n_significant,
        'per_sv': per_sv,
        'phase_sizes': {phase: len(states) for phase, states in phase_states.items()},
    }


# ---------------------------------------------------------------------------
# P3: Bounded Work-Cycle Dynamics
# ---------------------------------------------------------------------------

def test_p3(t2, pilot_folios, folio_meta):
    """
    Use T2 preferred-profile excursion_events.
    Pass: mean(n_cycles) > 3 AND mean(bounded_fraction) > 0.3 AND
          >=14/20 folios meet both (n_cycles >= 3 AND bounded_fraction >= 0.3).
    """
    print("\n  [P3] Bounded Work-Cycle Dynamics")
    runs = t2['runs']

    all_n_cycles = []
    all_bounded_fracs = []
    n_meeting_both = 0
    per_folio = {}

    for folio in pilot_folios:
        meta = folio_meta[folio]
        pref_key = meta['preferred_run_key']
        run = runs[pref_key]
        excursion_events = run.get('excursion_events', [])

        if excursion_events is None:
            excursion_events = []

        n_cycles = len(excursion_events)
        n_bounded = sum(1 for e in excursion_events if e.get('bounded', False))
        bounded_frac = _safe_div(n_bounded, n_cycles)
        n_phase_aligned = sum(1 for e in excursion_events
                              if e.get('packet_phase_at_start') == 'WORK')

        all_n_cycles.append(n_cycles)
        all_bounded_fracs.append(bounded_frac)

        meets_both = n_cycles >= 3 and bounded_frac >= 0.3
        if meets_both:
            n_meeting_both += 1

        per_folio[folio] = {
            'n_cycles': n_cycles,
            'n_bounded': n_bounded,
            'bounded_fraction': _round(bounded_frac, 4),
            'n_phase_aligned': n_phase_aligned,
            'meets_both': meets_both,
        }

    mean_n_cycles = _safe_div(sum(all_n_cycles), len(all_n_cycles))
    mean_bounded_frac = _safe_div(sum(all_bounded_fracs), len(all_bounded_fracs))

    passed = (mean_n_cycles > 3 and mean_bounded_frac > 0.3
              and n_meeting_both >= PASS_THRESHOLD)

    print(f"    mean_n_cycles={mean_n_cycles:.2f}, mean_bounded_frac={mean_bounded_frac:.4f}")
    print(f"    folios meeting both: {n_meeting_both}/20 -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'mean_n_cycles': _round(mean_n_cycles, 2),
        'mean_bounded_fraction': _round(mean_bounded_frac, 4),
        'n_folios_meeting_both': n_meeting_both,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# P4: Routing Consequence Fidelity
# ---------------------------------------------------------------------------

def test_p4(t2, t3, pilot_folios, folio_meta, folio_tokens):
    """
    P4a: Buffered state consequence - for each routing type, compare target SV
         in post-routing window vs non-routing tokens.
    P4b: Threshold-mediated consequence - full vs B4 on routing-targeted SVs.
    Pass: P4a >=3/4 correct, OR P4a >=2/4 + strong P4b support.
    """
    print("\n  [P4] Routing Consequence Fidelity")
    runs = t2['runs']

    # -----------------------------------------------------------------------
    # P4a: Buffered state consequence
    # -----------------------------------------------------------------------
    print("    [P4a] Buffered state consequence")

    # Build per-folio token lists with routing event positions
    # Then pair with trajectory states
    p4a_results = {}

    for rt, target_sv in ROUTING_TARGET.items():
        sv_idx = SV_INDEX[target_sv]

        # Collect group A (post-routing window) and group B (non-routing) states
        group_A = []  # target SV values from tokens 1-7 after routing event of type rt
        group_B = []  # target SV values from tokens NOT in any routing window

        for folio in pilot_folios:
            meta = folio_meta[folio]
            pref_key = meta['preferred_run_key']
            trajectory = runs[pref_key].get('trajectory')
            if not trajectory:
                continue

            toks = folio_tokens.get(folio, [])
            n = min(len(toks), len(trajectory))

            # Find all routing event positions (any routing type)
            all_routing_positions = set()
            rt_positions = []  # positions of THIS routing type
            for i in range(n):
                if (toks[i].get('routing_active')
                        and toks[i].get('routing_terminal')):
                    # Add window positions for ALL routing types
                    for w in range(1, ROUTING_WINDOW + 1):
                        if i + w < n:
                            all_routing_positions.add(i + w)
                    if toks[i]['routing_terminal'] == rt:
                        rt_positions.append(i)

            # Group A: positions 1-7 after THIS routing type
            for rp in rt_positions:
                for w in range(1, ROUTING_WINDOW + 1):
                    idx = rp + w
                    if idx < n:
                        group_A.append(trajectory[idx][sv_idx])

            # Group B: positions NOT in any routing window
            for i in range(n):
                if i not in all_routing_positions:
                    group_B.append(trajectory[i][sv_idx])

        # Run Mann-Whitney U
        if len(group_A) >= 5 and len(group_B) >= 5:
            try:
                U_stat, p_val = mannwhitneyu(group_A, group_B, alternative='two-sided')
            except ValueError:
                U_stat, p_val = 0.0, 1.0

            A_mean = sum(group_A) / len(group_A)
            B_mean = sum(group_B) / len(group_B)
            delta = A_mean - B_mean
            # For all routing types (r->X, y->T, h->TR, m->C), boost means
            # we expect A_mean > B_mean (positive delta)
            correct = p_val < 0.05 and delta > 0
        else:
            U_stat, p_val = None, None
            A_mean = sum(group_A) / len(group_A) if group_A else None
            B_mean = sum(group_B) / len(group_B) if group_B else None
            delta = (A_mean - B_mean) if (A_mean is not None and B_mean is not None) else None
            correct = False

        label = f"{rt}_{target_sv}"
        p4a_results[label] = {
            'A_mean': _round(A_mean),
            'B_mean': _round(B_mean),
            'A_n': len(group_A),
            'B_n': len(group_B),
            'delta': _round(delta),
            'U': _round(U_stat, 2),
            'p': _round(p_val, 6),
            'correct': correct,
        }

        tag = "CORRECT" if correct else "WRONG"
        print(f"      {label}: A_mean={_round(A_mean)}, B_mean={_round(B_mean)}, "
              f"delta={_round(delta)}, p={_round(p_val, 6)} -> {tag}")

    n_correct = sum(1 for v in p4a_results.values() if v['correct'])
    print(f"    P4a correct: {n_correct}/4")

    # -----------------------------------------------------------------------
    # P4b: Threshold-mediated consequence
    # -----------------------------------------------------------------------
    print("    [P4b] Threshold-mediated consequence (full vs B4)")
    b4 = t3['baselines']['B4_full_minus_routing']
    ref = t3['reference']

    p4b_results = {}
    for rt, target_sv in [('m', 'C'), ('h', 'TR')]:
        sv_idx = SV_INDEX[target_sv]
        n_positive = 0
        deltas = []
        for folio in pilot_folios:
            full_mean = ref[folio]['mean_state'][sv_idx]
            b4_mean = b4[folio]['mean_state'][sv_idx]
            delta = full_mean - b4_mean
            deltas.append(delta)
            if delta > 0:
                n_positive += 1

        mean_delta = sum(deltas) / len(deltas) if deltas else 0.0
        label = f"{rt}_{target_sv}"
        p4b_results[label] = {
            'mean_delta': _round(mean_delta),
            'n_positive': n_positive,
            'n_folios': len(pilot_folios),
        }
        print(f"      {label}: mean_delta={_round(mean_delta)}, "
              f"n_positive={n_positive}/20")

    # P4b "strong support": both show expected direction for majority
    p4b_strong = all(v['n_positive'] >= PASS_THRESHOLD
                     for v in p4b_results.values())

    # Overall P4 pass
    p4a_pass = n_correct >= 3
    p4_alt_pass = n_correct >= 2 and p4b_strong
    passed = p4a_pass or p4_alt_pass

    print(f"    P4a pass ({n_correct}>=3): {p4a_pass}")
    print(f"    P4 alt pass ({n_correct}>=2 + P4b strong={p4b_strong}): {p4_alt_pass}")
    print(f"    Overall P4: {'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'P4a': {
            'n_correct': n_correct,
            'pass': p4a_pass,
            'per_route': p4a_results,
        },
        'P4b': {
            'strong_support': p4b_strong,
            **p4b_results,
        },
    }


# ---------------------------------------------------------------------------
# P5: Headless Configuration Consequence
# ---------------------------------------------------------------------------

def test_p5(t2, t3, pilot_folios, folio_meta):
    """
    P5a: Full vs B5 (no config mode) - viability or state improvement.
    P5b: KW on mean C and mean S across config mode groups.
    P5c: Config ablation advantage (reported, non-gating).
    Overall pass: P5a OR P5b.
    """
    print("\n  [P5] Headless Configuration Consequence")
    runs = t2['runs']
    b5 = t3['baselines']['B5_full_minus_config']
    ref = t3['reference']

    # -----------------------------------------------------------------------
    # P5a: Full vs B5
    # -----------------------------------------------------------------------
    print("    [P5a] Full vs B5 (full minus config)")
    c_idx = SV_INDEX['C']
    s_idx = SV_INDEX['S']

    n_c_better = 0
    n_s_better = 0
    n_either = 0
    p5a_per_folio = {}

    for folio in pilot_folios:
        full_viab = ref[folio]['viability_fraction']
        b5_viab = b5[folio]['viability_fraction']
        full_mean_c = ref[folio]['mean_state'][c_idx]
        b5_mean_c = b5[folio]['mean_state'][c_idx]
        full_mean_s = ref[folio]['mean_state'][s_idx]
        b5_mean_s = b5[folio]['mean_state'][s_idx]

        # C_better: full has lower mean C OR higher viability than B5
        c_better = full_mean_c < b5_mean_c or full_viab > b5_viab
        # S_better: full has higher mean S than B5
        s_better = full_mean_s > b5_mean_s

        if c_better:
            n_c_better += 1
        if s_better:
            n_s_better += 1
        if c_better or s_better:
            n_either += 1

        p5a_per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b5_viab': _round(b5_viab),
            'full_mean_C': _round(full_mean_c),
            'b5_mean_C': _round(b5_mean_c),
            'full_mean_S': _round(full_mean_s),
            'b5_mean_S': _round(b5_mean_s),
            'c_better': c_better,
            's_better': s_better,
        }

    p5a_pass = n_either >= PASS_THRESHOLD
    print(f"      C_better: {n_c_better}/20, S_better: {n_s_better}/20, "
          f"either: {n_either}/20 -> {'PASS' if p5a_pass else 'FAIL'}")

    # -----------------------------------------------------------------------
    # P5b: KW across config mode groups
    # -----------------------------------------------------------------------
    print("    [P5b] KW across config mode groups")
    config_groups = defaultdict(list)
    for folio in pilot_folios:
        meta = folio_meta[folio]
        cm = meta['config_mode']
        pref_key = meta['preferred_run_key']
        summary = runs[pref_key]['summary']
        config_groups[cm].append({
            'folio': folio,
            'mean_C': summary['mean_state'][c_idx],
            'mean_S': summary['mean_state'][s_idx],
        })

    print(f"      Config groups: {', '.join(f'{k}({len(v)})' for k, v in sorted(config_groups.items()))}")

    p5b_results = {}
    p5b_pass = False

    for sv_name, sv_key in [('C', 'mean_C'), ('S', 'mean_S')]:
        groups = []
        group_labels = []
        for cm in sorted(config_groups.keys()):
            vals = [entry[sv_key] for entry in config_groups[cm]]
            if len(vals) >= 2:
                groups.append(vals)
                group_labels.append(cm)

        if len(groups) >= 2:
            try:
                H_stat, p_val = kruskal(*groups)
            except ValueError:
                H_stat, p_val = 0.0, 1.0
        else:
            H_stat, p_val = 0.0, 1.0

        sig = p_val < 0.05
        if sig:
            p5b_pass = True

        p5b_results[sv_name] = {
            'H': _round(H_stat, 4),
            'p': _round(p_val, 6),
            'sig': sig,
            'group_means': {
                cm: _round(sum(entry[sv_key] for entry in entries) / len(entries))
                for cm, entries in sorted(config_groups.items())
            },
        }
        tag = "*" if sig else " "
        print(f"      {tag} {sv_name}: H={_round(H_stat, 4)}, p={_round(p_val, 6)}")

    # -----------------------------------------------------------------------
    # P5c: Config ablation advantage
    # -----------------------------------------------------------------------
    print("    [P5c] Config ablation advantage")
    config_ablation = t2['config_ablation_runs']

    # Build per-folio config ablation data
    # Config ablation keys are "folio__configmode"
    ablation_folios = set()
    ablation_by_folio = defaultdict(dict)
    for abl_key, abl_data in config_ablation.items():
        folio = abl_data['folio']
        cm = abl_data['config_mode']
        ablation_folios.add(folio)
        ablation_by_folio[folio][cm] = abl_data['summary']

    advantages = []
    p5c_per_folio = {}
    for folio in sorted(ablation_folios):
        meta = folio_meta.get(folio, {})
        preferred_cm = meta.get('config_mode', None)
        if not preferred_cm or preferred_cm not in ablation_by_folio[folio]:
            continue

        pref_viab = ablation_by_folio[folio][preferred_cm]['viability_fraction']
        best_alt_viab = 0.0
        best_alt_cm = None
        for cm, summary in ablation_by_folio[folio].items():
            if cm != preferred_cm:
                v = summary['viability_fraction']
                if v > best_alt_viab:
                    best_alt_viab = v
                    best_alt_cm = cm

        advantage = pref_viab - best_alt_viab
        advantages.append(advantage)
        p5c_per_folio[folio] = {
            'preferred_cm': preferred_cm,
            'preferred_viab': _round(pref_viab),
            'best_alt_cm': best_alt_cm,
            'best_alt_viab': _round(best_alt_viab),
            'advantage': _round(advantage),
        }

    mean_advantage = sum(advantages) / len(advantages) if advantages else 0.0
    print(f"      Mean advantage (preferred vs best alt): {_round(mean_advantage)}")

    # Overall P5
    passed = p5a_pass or p5b_pass
    print(f"    Overall P5: {'PASS' if passed else 'FAIL'} "
          f"(P5a={p5a_pass}, P5b={p5b_pass})")

    return {
        'pass': passed,
        'P5a': {
            'pass': p5a_pass,
            'n_c_better': n_c_better,
            'n_s_better': n_s_better,
            'n_either': n_either,
            'per_folio': p5a_per_folio,
        },
        'P5b': {
            'pass': p5b_pass,
            **p5b_results,
        },
        'P5c': {
            'mean_advantage': _round(mean_advantage),
            'n_ablation_folios': len(ablation_folios),
            'per_folio': p5c_per_folio,
        },
    }


# ---------------------------------------------------------------------------
# P6: CTS Closure Value
# ---------------------------------------------------------------------------

def test_p6(t3, pilot_folios):
    """
    Full vs B3 (full minus CTS).
    Pass: full_viab > B3_viab for >=14/20 AND full_mean_C < B3_mean_C for >=14/20.
    """
    print("\n  [P6] CTS Closure Value")
    ref = t3['reference']
    b3 = t3['baselines']['B3_full_minus_cts']
    c_idx = SV_INDEX['C']

    n_viab_better = 0
    n_sep_positive = 0
    per_folio = {}

    for folio in pilot_folios:
        full_viab = ref[folio]['viability_fraction']
        b3_viab = b3[folio]['viability_fraction']
        full_mean_c = ref[folio]['mean_state'][c_idx]
        b3_mean_c = b3[folio]['mean_state'][c_idx]

        viab_better = full_viab > b3_viab
        sep_positive = full_mean_c < b3_mean_c

        if viab_better:
            n_viab_better += 1
        if sep_positive:
            n_sep_positive += 1

        per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b3_viab': _round(b3_viab),
            'viab_better': viab_better,
            'full_mean_C': _round(full_mean_c),
            'b3_mean_C': _round(b3_mean_c),
            'sep_positive': sep_positive,
        }

    passed = n_viab_better >= PASS_THRESHOLD and n_sep_positive >= PASS_THRESHOLD
    print(f"    viab_better: {n_viab_better}/20, sep_positive: {n_sep_positive}/20 -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'n_viab_better': n_viab_better,
        'n_sep_positive': n_sep_positive,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# P7: Null Destruction
# ---------------------------------------------------------------------------

def test_p7(t3, pilot_folios):
    """
    For each null type (N1-N4), for each folio, compute z-score of
    full_viab vs null_viab distribution.
    A null type passes if destroyed (z>2) for >=14/20 folios.
    Overall pass: >=3/4 null types pass.
    """
    print("\n  [P7] Null Destruction")
    ref = t3['reference']
    nulls = t3['nulls']

    null_types = ['N1_token_shuffle', 'N2_domain_preserve',
                  'N3_line_shuffle', 'N4_within_line']
    n_null_pass = 0
    per_null = {}

    for null_name in null_types:
        null_data = nulls[null_name]
        n_destroyed = 0
        per_folio = {}

        for folio in pilot_folios:
            full_viab = ref[folio]['viability_fraction']
            null_viab_mean = null_data[folio]['viability_mean']
            null_viab_std = null_data[folio]['viability_std']

            z = (full_viab - null_viab_mean) / max(null_viab_std, 1e-6)
            destroyed = z > 2.0

            if destroyed:
                n_destroyed += 1

            per_folio[folio] = {
                'full_viab': _round(full_viab),
                'null_viab_mean': _round(null_viab_mean),
                'null_viab_std': _round(null_viab_std),
                'z': _round(z, 3),
                'destroyed': destroyed,
            }

        null_pass = n_destroyed >= PASS_THRESHOLD
        if null_pass:
            n_null_pass += 1

        per_null[null_name] = {
            'pass': null_pass,
            'n_destroyed': n_destroyed,
            'per_folio': per_folio,
        }

        tag = "PASS" if null_pass else "FAIL"
        print(f"    {null_name}: destroyed {n_destroyed}/20 -> {tag}")

    passed = n_null_pass >= 3
    print(f"    Overall P7: {n_null_pass}/4 null types pass -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'n_null_types_pass': n_null_pass,
        'per_null': per_null,
    }


# ---------------------------------------------------------------------------
# P8: Preferred Profile Superiority
# ---------------------------------------------------------------------------

def test_p8(t2, pilot_folios, folio_meta):
    """
    For each folio, check if preferred profile is best on at least one metric
    (viability, hazard_count, Y_final) across all 3 profiles.
    Pass: preferred_best for >=14/20.
    """
    print("\n  [P8] Preferred Profile Superiority")
    runs = t2['runs']

    n_preferred_best = 0
    per_folio = {}

    for folio in pilot_folios:
        meta = folio_meta[folio]
        preferred_profile = meta['preferred_profile']
        all_profiles = meta['all_profiles']

        # Gather summaries for all 3 profiles
        viabilities = {}
        hazard_counts = {}
        y_finals = {}
        for run_data in all_profiles:
            p = run_data['profile']
            s = run_data['summary']
            viabilities[p] = s['viability_fraction']
            hazard_counts[p] = s['hazard_count']
            y_finals[p] = s['Y_final']

        pref_viab = viabilities.get(preferred_profile, 0.0)
        pref_hazard = hazard_counts.get(preferred_profile, 999)
        pref_y = y_finals.get(preferred_profile, 0.0)

        other_viabs = [v for p, v in viabilities.items() if p != preferred_profile]
        other_hazards = [v for p, v in hazard_counts.items() if p != preferred_profile]
        other_y_finals = [v for p, v in y_finals.items() if p != preferred_profile]

        best_on_viab = pref_viab >= max(other_viabs) if other_viabs else True
        best_on_hazard = pref_hazard <= min(other_hazards) if other_hazards else True
        best_on_y = pref_y >= max(other_y_finals) if other_y_finals else True

        preferred_best = best_on_viab or best_on_hazard or best_on_y
        if preferred_best:
            n_preferred_best += 1

        per_folio[folio] = {
            'preferred_profile': preferred_profile,
            'best_on_viab': best_on_viab,
            'best_on_hazard': best_on_hazard,
            'best_on_Y': best_on_y,
            'preferred_best': preferred_best,
            'viabilities': {k: _round(v) for k, v in viabilities.items()},
            'hazard_counts': hazard_counts,
            'Y_finals': {k: _round(v) for k, v in y_finals.items()},
        }

    passed = n_preferred_best >= PASS_THRESHOLD
    print(f"    preferred_best: {n_preferred_best}/20 -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'n_preferred_best': n_preferred_best,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# P9: Section-Template Recovery (secondary)
# ---------------------------------------------------------------------------

def test_p9(t2, pilot_folios, folio_meta):
    """
    Group preferred runs by section. KW on each SV across sections.
    Report number of significant SVs. Does not affect verdict.
    """
    print("\n  [P9] Section-Template Recovery (secondary)")
    runs = t2['runs']

    # Group by section
    section_groups = defaultdict(list)
    for folio in pilot_folios:
        meta = folio_meta[folio]
        section = meta['section']
        pref_key = meta['preferred_run_key']
        summary = runs[pref_key]['summary']
        section_groups[section].append({
            'folio': folio,
            'mean_state': summary['mean_state'],
        })

    print(f"    Sections: {', '.join(f'{k}({len(v)})' for k, v in sorted(section_groups.items()))}")

    per_sv = {}
    n_significant = 0

    for sv_idx, sv in enumerate(STATE_VARS):
        groups = []
        group_labels = []
        for section in sorted(section_groups.keys()):
            vals = [entry['mean_state'][sv_idx]
                    for entry in section_groups[section]]
            if len(vals) >= 2:
                groups.append(vals)
                group_labels.append(section)

        if len(groups) >= 2:
            try:
                H_stat, p_val = kruskal(*groups)
            except ValueError:
                H_stat, p_val = 0.0, 1.0
        else:
            H_stat, p_val = 0.0, 1.0

        sig = p_val < 0.05
        if sig:
            n_significant += 1

        per_sv[sv] = {
            'H': _round(H_stat, 4),
            'p': _round(p_val, 6),
            'sig': sig,
            'group_means': {
                section: _round(sum(entry['mean_state'][sv_idx]
                                    for entry in entries) / len(entries))
                for section, entries in sorted(section_groups.items())
            },
        }

        tag = "*" if sig else " "
        print(f"      {tag} {sv}: H={_round(H_stat, 4)}, p={_round(p_val, 6)}")

    # P9 is secondary; does not affect verdict
    print(f"    Significant SVs: {n_significant}/7 (non-gating)")

    return {
        'pass': None,  # secondary, non-gating
        'n_significant': n_significant,
        'per_sv': per_sv,
        'section_sizes': {s: len(v) for s, v in section_groups.items()},
    }


# ---------------------------------------------------------------------------
# D1: B7 Diagnostic (threshold terms)
# ---------------------------------------------------------------------------

def diag_d1(t3, pilot_folios):
    """
    Compare B7 (full minus thresholds) vs full (T3 reference).
    Report how many folios benefit from threshold terms.
    """
    print("\n  [D1] B7 Diagnostic (threshold terms)")
    ref = t3['reference']
    b7 = t3['baselines']['B7_full_minus_thresholds']

    n_viab_better = 0
    n_hazard_better = 0
    per_folio = {}

    for folio in pilot_folios:
        full_viab = ref[folio]['viability_fraction']
        b7_viab = b7[folio]['viability_fraction']
        full_haz = ref[folio]['hazard_count']
        b7_haz = b7[folio]['hazard_count']

        viab_better = full_viab > b7_viab
        hazard_better = full_haz < b7_haz

        if viab_better:
            n_viab_better += 1
        if hazard_better:
            n_hazard_better += 1

        per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b7_viab': _round(b7_viab),
            'viab_better': viab_better,
            'full_hazard': full_haz,
            'b7_hazard': b7_haz,
            'hazard_better': hazard_better,
        }

    print(f"    Full better viability: {n_viab_better}/20")
    print(f"    Full fewer hazards: {n_hazard_better}/20")

    return {
        'n_viab_better_with_thresholds': n_viab_better,
        'n_hazard_better_with_thresholds': n_hazard_better,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# D2: B8 Diagnostic (fixed law)
# ---------------------------------------------------------------------------

def diag_d2(t3, pilot_folios):
    """
    Compare B8 (fixed law / phase-specific laws removed) vs full (T3 reference).
    Report how many folios benefit from phase-specific laws.
    """
    print("\n  [D2] B8 Diagnostic (fixed law)")
    ref = t3['reference']
    b8 = t3['baselines']['B8_fixed_law']

    n_viab_better = 0
    n_hazard_better = 0
    viab_deltas = []
    per_folio = {}

    for folio in pilot_folios:
        full_viab = ref[folio]['viability_fraction']
        b8_viab = b8[folio]['viability_fraction']
        full_haz = ref[folio]['hazard_count']
        b8_haz = b8[folio]['hazard_count']

        viab_better = full_viab > b8_viab
        hazard_better = full_haz < b8_haz
        viab_delta = full_viab - b8_viab

        if viab_better:
            n_viab_better += 1
        if hazard_better:
            n_hazard_better += 1
        viab_deltas.append(viab_delta)

        per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b8_viab': _round(b8_viab),
            'viab_delta': _round(viab_delta),
            'viab_better': viab_better,
            'full_hazard': full_haz,
            'b8_hazard': b8_haz,
            'hazard_better': hazard_better,
        }

    mean_viab_delta = sum(viab_deltas) / len(viab_deltas) if viab_deltas else 0.0
    print(f"    Full better viability (phase-specific laws): {n_viab_better}/20")
    print(f"    Full fewer hazards: {n_hazard_better}/20")
    print(f"    Mean viability delta (full - B8): {_round(mean_viab_delta)}")

    return {
        'n_viab_better_with_phase_laws': n_viab_better,
        'n_hazard_better_with_phase_laws': n_hazard_better,
        'mean_viab_delta': _round(mean_viab_delta),
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t_start = time.time()
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    phase_dir = project_root / 'phases' / 'VIRTUAL_APPARATUS_EVENT_DYNAMICS'
    output_path = phase_dir / 'results' / 't4_behavior_validation.json'

    print("=" * 70)
    print("T4: Behavior Validation Battery")
    print("Phase 564 - VIRTUAL_APPARATUS_EVENT_DYNAMICS")
    print("=" * 70)

    # Load all data
    t2, t3, line_packets, sup_tokens = load_all_data(project_root)

    # Build folio metadata
    pilot_folios, folio_meta = build_folio_metadata(t2, t3)
    print(f"\n  Pilot folios: {len(pilot_folios)}")
    for f in pilot_folios:
        m = folio_meta[f]
        print(f"    {f}: {m['preferred_profile']}, {m['config_mode']}, "
              f"section={m['section']}, n_tokens={m['n_tokens']}")

    # Build per-folio token lists (for P2 and P4a)
    print("\n--- Building per-folio token lists ---")
    folio_tokens = build_folio_tokens(sup_tokens, pilot_folios, line_packets)
    for f in pilot_folios:
        n = len(folio_tokens.get(f, []))
        print(f"    {f}: {n} tokens")

    # Run tests
    print("\n" + "=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)

    results = {}

    results['P1_viable_envelope'] = test_p1(t2, t3, pilot_folios, folio_meta)
    results['P2_packet_shape'] = test_p2(t2, pilot_folios, folio_meta, folio_tokens)
    results['P3_bounded_cycles'] = test_p3(t2, pilot_folios, folio_meta)
    results['P4_routing_consequence'] = test_p4(t2, t3, pilot_folios, folio_meta,
                                                 folio_tokens)
    results['P5_headless_config'] = test_p5(t2, t3, pilot_folios, folio_meta)
    results['P6_cts_closure'] = test_p6(t3, pilot_folios)
    results['P7_null_destruction'] = test_p7(t3, pilot_folios)
    results['P8_profile_superiority'] = test_p8(t2, pilot_folios, folio_meta)
    results['P9_section_template'] = test_p9(t2, pilot_folios, folio_meta)

    # Diagnostics
    diagnostics = {}
    diagnostics['D1_threshold_terms'] = diag_d1(t3, pilot_folios)
    diagnostics['D2_phase_laws'] = diag_d2(t3, pilot_folios)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # P9 is secondary (pass=None), so exclude from pass/fail counts
    core_tests = {k: v for k, v in results.items() if v.get('pass') is not None}
    core_pass = [k for k, v in core_tests.items() if v['pass']]
    core_fail = [k for k, v in core_tests.items() if not v['pass']]

    n_pass = len(core_pass)
    n_fail = len(core_fail)
    n_core = len(core_tests)

    print(f"\n  Core tests: {n_pass}/{n_core} pass")
    print(f"    PASS: {', '.join(core_pass) if core_pass else '(none)'}")
    print(f"    FAIL: {', '.join(core_fail) if core_fail else '(none)'}")
    print(f"  P9 (secondary): {results['P9_section_template']['n_significant']}/7 "
          f"significant SVs")

    summary = {
        'n_pass': n_pass,
        'n_fail': n_fail,
        'n_core_tests': n_core,
        'core_pass': core_pass,
        'core_fail': core_fail,
        'P9_significant_svs': results['P9_section_template']['n_significant'],
    }

    elapsed = time.time() - t_start

    # Build output
    output = {
        'metadata': {
            'phase': '564',
            'task': 'T4_behavior_validation',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_tests': 9,
            'n_diagnostics': 2,
            'n_folios': len(pilot_folios),
            'threshold': PASS_THRESHOLD,
            'elapsed_seconds': round(elapsed, 2),
        },
        'tests': results,
        'diagnostics': diagnostics,
        'summary': summary,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, cls=_NumpyEncoder)

    file_size = output_path.stat().st_size
    print(f"\n  Output: {output_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print(f"  Elapsed: {elapsed:.2f}s")
    print("  DONE")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
