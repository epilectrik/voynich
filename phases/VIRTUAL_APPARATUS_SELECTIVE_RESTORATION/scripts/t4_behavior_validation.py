"""
T4: Behavior Validation Battery
Phase 564b - VIRTUAL_APPARATUS_SELECTIVE_RESTORATION

Reads T2 (selective restoration runs) and T3 (null/ablation runs) results,
runs 9 tests (P1-P9) plus 3 diagnostics (D1-D3), and outputs
t4_behavior_validation.json.

Tests:
  P1: Viable Envelope Occupancy (with non-degeneracy guard)
  P2: Line Packet Shape Recovery
  P3: Bounded Work-Cycle Dynamics (with profile stratification)
  P4: Routing Consequence Fidelity (P4a routed vs unrouted, P4b full vs B4)
  P5: Headless Configuration Consequence (P5a full vs B5, P5b KW across configs)
  P6: CTS Closure Value (full vs B3)
  P7: Null Destruction (N1-N4 z-score separation)
  P8: Preferred Profile Superiority
  P9: Section-Template Recovery (secondary, non-gating)

Diagnostics:
  D1: Signal-to-Restoring-Force Ratio Audit (quasi-gating)
  D2: State-Space Occupancy Audit (quasi-gating)
  D3: B9 vs Full Comparison
"""

import json
import sys
import time
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import kruskal, mannwhitneyu

# ---------------------------------------------------------------------------
# Add parent phase scripts to path for constants
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_PHASE_DIR = _SCRIPT_DIR.parent
_PROJECT_ROOT = _PHASE_DIR.parent.parent

sys.path.insert(0, str(_PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'scripts'))
from t1_apparatus_family_builder import STATE_VARS, HAZARD_BOUNDARIES, PROFILES

sys.path.insert(0, str(_PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_SELECTIVE_RESTORATION' / 'scripts'))
from t1_selective_restoration_apparatus import (
    Q1, Q2_BASE, GAMMA_BASIN, GAMMA_CORRIDOR, GAMMA_CORRIDOR as _GC,
    CORRIDOR_MULT, BASIN_MULT, EDGE_MULT,
    A3_SENS, P90_DV, A3_DECAY, PROFILE_DECAYS,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}
N_VARS = len(STATE_VARS)
PASS_THRESHOLD = 14  # out of 20 folios

# Routing target mappings for P4a
ROUTING_TARGET = {
    'm': 'C',
    'h': 'TR',
    'r': 'X',
    'y': 'T',
}
ROUTING_WINDOW = 3  # tokens preceding a target to check for routing terminal

# Profile labels for P3 stratification
PROFILE_SHORT = {
    'A1_BATH_REFLUX': 'A1',
    'A2_SEALED_RECIRCULATION': 'A2',
    'A3_DISTILL_COLLECT': 'A3',
}


# ---------------------------------------------------------------------------
# JSON encoder for numpy types
# ---------------------------------------------------------------------------
class _NumpyEncoder(json.JSONEncoder):
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
# Helpers
# ---------------------------------------------------------------------------
def _round(v, n=5):
    if v is None:
        return None
    return round(v, n)


def _safe_div(a, b, default=0.0):
    return a / b if b != 0 else default


def _load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_all_data():
    """Load T2, T3, supervisory tokens, and line packets."""
    sr_results = _PHASE_DIR / 'results'
    coupling_results = _PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'results'
    ste_results = _PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results'

    print("--- Loading data sources ---")

    # T2: selective restoration runs
    t2_path = sr_results / 't2_selective_restoration_runs.json'
    print(f"  Loading T2: {t2_path}")
    t2 = _load_json(t2_path)
    print(f"    Primary runs: {len(t2['primary_runs'])}, "
          f"Config ablation: {len(t2['config_ablation_runs'])}")

    # T3: null/ablation runs
    t3_path = sr_results / 't3_null_ablation_runs.json'
    print(f"  Loading T3: {t3_path}")
    t3 = _load_json(t3_path)
    print(f"    Reference: {len(t3['reference'])}, "
          f"Baselines: {list(t3['baseline_runs'].keys())}, "
          f"Nulls: {list(t3['null_runs'].keys())}")

    # Supervisory tokens (for P2 and P4a)
    t2b_path = coupling_results / 't2b_supervisory_interface_unrouted.json'
    print(f"  Loading supervisory tokens: {t2b_path}")
    t2b = _load_json(t2b_path)
    sup_tokens = t2b['token_signals']
    print(f"    Supervisory tokens: {len(sup_tokens)}")

    # Line packets (for P2 packet_phase mapping)
    lp_path = ste_results / 't3_line_packets.json'
    print(f"  Loading line packets: {lp_path}")
    lp_data = _load_json(lp_path)
    line_packets = lp_data['line_packets']
    print(f"    Line packets: {len(line_packets)}")

    return t2, t3, sup_tokens, line_packets


# ---------------------------------------------------------------------------
# Build folio metadata from T2 and T3
# ---------------------------------------------------------------------------
def build_folio_metadata(t2, t3, sup_tokens):
    """
    Extract pilot folio list, preferred profile, config_mode, section,
    and group primary runs by folio.
    """
    pilot_folios = sorted(t3['reference'].keys())
    pref_map = t2['preferred_profile_map']

    # Determine section per folio from supervisory tokens
    folio_section = {}
    for tok in sup_tokens:
        folio_section[tok['folio']] = tok['section']

    # Index primary runs by (folio, profile)
    runs_by_fp = {}
    for run in t2['primary_runs']:
        key = (run['folio'], run['profile'])
        runs_by_fp[key] = run

    # Index config ablation runs by (folio, config_mode)
    config_abl_by_fc = {}
    for run in t2['config_ablation_runs']:
        key = (run['folio'], run['config_mode'])
        config_abl_by_fc[key] = run

    # Build baseline lookups: baseline_runs are lists, index by folio
    baseline_by_folio = {}
    for bkey, blist in t3['baseline_runs'].items():
        baseline_by_folio[bkey] = {}
        for entry in blist:
            baseline_by_folio[bkey][entry['folio']] = entry

    folio_meta = {}
    for folio in pilot_folios:
        pref_profile = pref_map.get(folio)
        pref_run = runs_by_fp.get((folio, pref_profile))

        # Collect all 3 profile runs for this folio
        all_profiles = {}
        for profile in ['A1_BATH_REFLUX', 'A2_SEALED_RECIRCULATION', 'A3_DISTILL_COLLECT']:
            run = runs_by_fp.get((folio, profile))
            if run:
                all_profiles[profile] = run

        folio_meta[folio] = {
            'preferred_profile': pref_profile,
            'preferred_run': pref_run,
            'config_mode': pref_run['config_mode'] if pref_run else None,
            'section': folio_section.get(folio, 'UNK'),
            'n_tokens': pref_run['n_tokens'] if pref_run else 0,
            'all_profiles': all_profiles,
        }

    return pilot_folios, folio_meta, baseline_by_folio


# ---------------------------------------------------------------------------
# Build per-folio token lists
# ---------------------------------------------------------------------------
def build_folio_tokens(sup_tokens, pilot_folios, line_packets):
    """
    Build per-folio sorted token lists with packet_phase assigned.
    Returns dict: folio -> list of token dicts.
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
# P1: Viable Envelope Occupancy (with non-degeneracy guard)
# ---------------------------------------------------------------------------
def test_p1(t2, t3, pilot_folios, folio_meta, baseline_by_folio):
    """
    P1a: full > B2 AND full > N1 mean for >=14/20 folios.
    P1b: mean viability in [0.88, 0.995] AND >=8/20 < 1.0.
    P1 overall: BOTH P1a and P1b pass.
    """
    print("\n  [P1] Viable Envelope Occupancy")
    ref = t3['reference']
    b2_by_folio = baseline_by_folio['B2']
    n1 = t3['null_runs']['N1']

    full_gt_b2 = 0
    full_gt_n1 = 0
    viabilities = []
    folios_lt_1 = 0
    p1a_per_folio = {}

    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        full_viab = pref_run['viability']
        b2_viab = b2_by_folio[folio]['viability']
        n1_viab_mean = n1[folio]['mean_viab']

        viabilities.append(full_viab)
        if full_viab < 1.0:
            folios_lt_1 += 1

        gt_b2 = full_viab > b2_viab
        gt_n1 = full_viab > n1_viab_mean

        if gt_b2:
            full_gt_b2 += 1
        if gt_n1:
            full_gt_n1 += 1

        p1a_per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b2_viab': _round(b2_viab),
            'n1_viab_mean': _round(n1_viab_mean),
            'gt_b2': gt_b2,
            'gt_n1': gt_n1,
        }

    mean_viab = sum(viabilities) / len(viabilities) if viabilities else 0.0

    # P1a: superiority
    p1a_pass = full_gt_b2 >= PASS_THRESHOLD and full_gt_n1 >= PASS_THRESHOLD
    print(f"    [P1a] full>B2: {full_gt_b2}/20, full>N1: {full_gt_n1}/20 -> "
          f"{'PASS' if p1a_pass else 'FAIL'}")

    # P1b: non-degeneracy
    in_band = 0.88 <= mean_viab <= 0.995
    enough_lt_1 = folios_lt_1 >= 8
    p1b_pass = in_band and enough_lt_1
    print(f"    [P1b] mean_viab={mean_viab:.6f} in [0.88,0.995]={in_band}, "
          f"folios<1.0={folios_lt_1}/20 (need>=8) -> {'PASS' if p1b_pass else 'FAIL'}")

    passed = p1a_pass and p1b_pass
    print(f"    P1 overall: {'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'P1a': {
            'pass': p1a_pass,
            'full_gt_B2': full_gt_b2,
            'full_gt_N1': full_gt_n1,
            'threshold': PASS_THRESHOLD,
        },
        'P1b': {
            'pass': p1b_pass,
            'mean_viability': _round(mean_viab, 6),
            'band': [0.88, 0.995],
            'folios_lt_1': folios_lt_1,
            'min_folios_lt_1': 8,
        },
        'per_folio': p1a_per_folio,
    }


# ---------------------------------------------------------------------------
# P2: Line Packet Shape Recovery
# ---------------------------------------------------------------------------
def test_p2(pilot_folios, folio_tokens):
    """
    Group supervisory token contributions by packet_phase (SPEC/WORK/CLOSE).
    Run Kruskal-Wallis on each SV across the 3 phases.
    Pass: >=4/7 significant SVs.
    """
    print("\n  [P2] Line Packet Shape Recovery")

    # Collect contribution magnitudes grouped by packet_phase
    phase_contribs = {'SPEC': [], 'WORK': [], 'CLOSE': []}

    for folio in pilot_folios:
        toks = folio_tokens.get(folio, [])
        for tok in toks:
            pp = tok.get('_packet_phase', 'WORK')
            if pp in phase_contribs:
                contribs = tok.get('contributions', [0.0] * N_VARS)
                phase_contribs[pp].append(contribs)

    print(f"    Phase sizes: SPEC={len(phase_contribs['SPEC'])}, "
          f"WORK={len(phase_contribs['WORK'])}, "
          f"CLOSE={len(phase_contribs['CLOSE'])}")

    per_sv = {}
    n_significant = 0

    for sv_idx, sv in enumerate(STATE_VARS):
        groups = []
        for phase in ['SPEC', 'WORK', 'CLOSE']:
            vals = [abs(c[sv_idx]) for c in phase_contribs[phase] if len(c) > sv_idx]
            groups.append(vals)

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
        tag = "*" if info.get('sig') else " "
        print(f"      {tag} {sv}: H={info.get('H')}, p={info.get('p')}")

    return {
        'pass': passed,
        'n_significant': n_significant,
        'per_sv': per_sv,
        'phase_sizes': {phase: len(states) for phase, states in phase_contribs.items()},
    }


# ---------------------------------------------------------------------------
# P3: Bounded Work-Cycle Dynamics (with profile stratification)
# ---------------------------------------------------------------------------
def test_p3(pilot_folios, folio_meta):
    """
    For each preferred-profile run:
      bounded_fraction = bounded_excursion_count / max(excursion_count, 1)
      meets_P3 = excursion_count >= 3 AND bounded_fraction >= 0.3

    Aggregate pass: mean_cycles > 3 AND mean_bounded_fraction > 0.3
                    AND >=14/20 folios meet both.

    Also report P3 success rates by profile (A1, A2, A3).
    """
    print("\n  [P3] Bounded Work-Cycle Dynamics")

    all_n_cycles = []
    all_bounded_fracs = []
    n_meeting_both = 0
    per_folio = {}
    by_profile = defaultdict(lambda: {'folios': [], 'n_meeting': 0,
                                       'cycles': [], 'bf': []})

    for folio in pilot_folios:
        meta = folio_meta[folio]
        pref_run = meta['preferred_run']
        profile = meta['preferred_profile']
        profile_short = PROFILE_SHORT.get(profile, profile)

        n_cycles = pref_run['excursion_count']
        n_bounded = pref_run['bounded_excursion_count']
        bounded_frac = _safe_div(n_bounded, max(n_cycles, 1))

        all_n_cycles.append(n_cycles)
        all_bounded_fracs.append(bounded_frac)

        meets_both = n_cycles >= 3 and bounded_frac >= 0.3
        if meets_both:
            n_meeting_both += 1

        per_folio[folio] = {
            'profile': profile_short,
            'n_cycles': n_cycles,
            'n_bounded': n_bounded,
            'bounded_fraction': _round(bounded_frac, 4),
            'meets_both': meets_both,
        }

        by_profile[profile_short]['folios'].append(folio)
        by_profile[profile_short]['cycles'].append(n_cycles)
        by_profile[profile_short]['bf'].append(bounded_frac)
        if meets_both:
            by_profile[profile_short]['n_meeting'] += 1

    mean_n_cycles = _safe_div(sum(all_n_cycles), len(all_n_cycles))
    mean_bounded_frac = _safe_div(sum(all_bounded_fracs), len(all_bounded_fracs))

    passed = (mean_n_cycles > 3 and mean_bounded_frac > 0.3
              and n_meeting_both >= PASS_THRESHOLD)

    print(f"    mean_cycles={mean_n_cycles:.2f}, "
          f"mean_bounded_frac={mean_bounded_frac:.4f}")
    print(f"    folios meeting both: {n_meeting_both}/20 -> "
          f"{'PASS' if passed else 'FAIL'}")

    # Profile stratification
    profile_summary = {}
    for pshort in sorted(by_profile.keys()):
        pdata = by_profile[pshort]
        n_folios = len(pdata['folios'])
        n_meeting = pdata['n_meeting']
        mc = sum(pdata['cycles']) / n_folios if n_folios else 0
        profile_summary[pshort] = {
            'n_folios': n_folios,
            'n_meeting_P3': n_meeting,
            'mean_cycles': _round(mc, 2),
        }
        print(f"      {pshort}: {n_folios} folios, "
              f"P3 met={n_meeting}, mean_cycles={mc:.2f}")

    # Note if A3+A2 pass strongly but A1 drags
    a1_n = profile_summary.get('A1', {}).get('n_meeting_P3', 0)
    a2_n = profile_summary.get('A2', {}).get('n_meeting_P3', 0)
    a3_n = profile_summary.get('A3', {}).get('n_meeting_P3', 0)
    total_a2a3 = a2_n + a3_n
    if total_a2a3 >= PASS_THRESHOLD and n_meeting_both < PASS_THRESHOLD:
        print(f"    NOTE: A2+A3 alone meet threshold ({total_a2a3}), "
              f"A1 drags aggregate ({a1_n} meet)")

    return {
        'pass': passed,
        'mean_cycles': _round(mean_n_cycles, 2),
        'mean_bounded_fraction': _round(mean_bounded_frac, 4),
        'n_meeting_both': n_meeting_both,
        'by_profile': profile_summary,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# P4: Routing Consequence Fidelity
# ---------------------------------------------------------------------------
def test_p4(t3, pilot_folios, folio_meta, folio_tokens, baseline_by_folio):
    """
    P4a: For each routing pair, compare target SV contribution magnitude
         between tokens preceded by routing terminal vs tokens NOT preceded.
    P4b: Compare full model vs B4 (no routing) viability per folio.

    P4 routing tiers:
      Primary: m->C, h->TR
      Secondary: r->X, y->T
    """
    print("\n  [P4] Routing Consequence Fidelity")

    # -----------------------------------------------------------------------
    # P4a: Routed vs unrouted comparison
    # -----------------------------------------------------------------------
    print("    [P4a] Routed vs unrouted state consequence")

    p4a_results = {}
    primary_routes = {'m': 'C', 'h': 'TR'}
    secondary_routes = {'r': 'X', 'y': 'T'}

    for rt, target_sv in ROUTING_TARGET.items():
        sv_idx = SV_INDEX[target_sv]

        group_routed = []    # target SV contributions for tokens preceded by routing
        group_unrouted = []  # target SV contributions for tokens NOT preceded

        for folio in pilot_folios:
            toks = folio_tokens.get(folio, [])
            n = len(toks)

            # Find positions of each routing terminal type
            routing_positions = {}  # position -> routing_terminal
            for i in range(n):
                if toks[i].get('routing_active') and toks[i].get('routing_terminal'):
                    routing_positions[i] = toks[i]['routing_terminal']

            # Build set of positions preceded (within ROUTING_WINDOW) by THIS rt
            preceded_by_rt = set()
            # Build set of positions preceded by ANY routing terminal
            preceded_by_any = set()

            for rp, rterm in routing_positions.items():
                for w in range(1, ROUTING_WINDOW + 1):
                    idx = rp + w
                    if idx < n:
                        preceded_by_any.add(idx)
                        if rterm == rt:
                            preceded_by_rt.add(idx)

            # Collect groups
            for i in range(n):
                contribs = toks[i].get('contributions', [])
                if len(contribs) <= sv_idx:
                    continue
                val = abs(contribs[sv_idx])
                if i in preceded_by_rt:
                    group_routed.append(val)
                elif i not in preceded_by_any:
                    group_unrouted.append(val)

        # Run Mann-Whitney U
        if len(group_routed) >= 5 and len(group_unrouted) >= 5:
            try:
                U_stat, p_val = mannwhitneyu(group_routed, group_unrouted,
                                              alternative='two-sided')
            except ValueError:
                U_stat, p_val = 0.0, 1.0

            r_mean = sum(group_routed) / len(group_routed)
            u_mean = sum(group_unrouted) / len(group_unrouted)
            delta = r_mean - u_mean
            # Routing should widen the corridor -> larger |contribution|
            correct = p_val < 0.05 and delta > 0
        else:
            U_stat, p_val = None, None
            r_mean = sum(group_routed) / len(group_routed) if group_routed else None
            u_mean = sum(group_unrouted) / len(group_unrouted) if group_unrouted else None
            delta = (r_mean - u_mean) if (r_mean is not None and u_mean is not None) else None
            correct = False

        label = f"{rt}__{target_sv}"
        p4a_results[label] = {
            'routed_mean': _round(r_mean),
            'unrouted_mean': _round(u_mean),
            'routed_n': len(group_routed),
            'unrouted_n': len(group_unrouted),
            'delta': _round(delta),
            'U': _round(U_stat, 2) if U_stat is not None else None,
            'p': _round(p_val, 6) if p_val is not None else None,
            'correct': correct,
        }

        tag = "CORRECT" if correct else "wrong"
        tier = "PRIMARY" if rt in primary_routes else "secondary"
        print(f"      [{tier}] {rt}->{target_sv}: routed_mean={_round(r_mean)}, "
              f"unrouted_mean={_round(u_mean)}, delta={_round(delta)}, "
              f"p={_round(p_val, 6)} -> {tag}")

    n_correct = sum(1 for v in p4a_results.values() if v['correct'])
    print(f"    P4a correct: {n_correct}/4")

    # Split into primary and secondary
    primary_results = {k: v for k, v in p4a_results.items()
                       if k.split('__')[0] in primary_routes}
    secondary_results = {k: v for k, v in p4a_results.items()
                         if k.split('__')[0] in secondary_routes}

    # -----------------------------------------------------------------------
    # P4b: Full vs B4 (no routing)
    # -----------------------------------------------------------------------
    print("    [P4b] Full vs B4 (no routing)")
    ref = t3['reference']
    b4_by_folio = baseline_by_folio['B4']

    p4b_per_folio = {}
    n_viab_diff = 0
    n_yfinal_diff = 0
    viab_deltas = []

    for folio in pilot_folios:
        full_viab = ref[folio]['viability']
        b4_viab = b4_by_folio[folio]['viability']
        full_yf = ref[folio]['Y_final']
        b4_yf = b4_by_folio[folio]['Y_final']

        viab_delta = full_viab - b4_viab
        yf_delta = full_yf - b4_yf
        viab_deltas.append(viab_delta)

        viab_better = full_viab > b4_viab
        yf_different = abs(yf_delta) > 0.001

        if viab_better:
            n_viab_diff += 1
        if yf_different:
            n_yfinal_diff += 1

        p4b_per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b4_viab': _round(b4_viab),
            'viab_delta': _round(viab_delta),
            'full_Y_final': _round(full_yf),
            'b4_Y_final': _round(b4_yf),
            'yf_delta': _round(yf_delta),
        }

    mean_viab_delta = sum(viab_deltas) / len(viab_deltas) if viab_deltas else 0.0
    print(f"      full>B4 viab: {n_viab_diff}/20, Y_final differs: {n_yfinal_diff}/20, "
          f"mean viab delta: {_round(mean_viab_delta)}")

    # P4 overall pass: >=3/4 correct in P4a
    p4a_pass = n_correct >= 3
    passed = p4a_pass
    print(f"    P4 overall: {'PASS' if passed else 'FAIL'} "
          f"(P4a {n_correct}/4 correct)")

    return {
        'pass': passed,
        'P4a': {
            'n_correct': n_correct,
            'pass': p4a_pass,
            'primary': primary_results,
            'secondary': secondary_results,
        },
        'P4b': {
            'full_vs_B4_viab_delta': _round(mean_viab_delta),
            'n_viab_better': n_viab_diff,
            'n_yfinal_different': n_yfinal_diff,
            'per_folio': p4b_per_folio,
        },
    }


# ---------------------------------------------------------------------------
# P5: Headless Configuration Consequence
# ---------------------------------------------------------------------------
def test_p5(t3, pilot_folios, folio_meta, baseline_by_folio):
    """
    P5a: Full vs B5 (forced H1). Count folios where full viability > B5.
         Pass if C_better >= 14/20.
    P5b: KW on viability across config mode groups (H0, H1, H2).
         Pass if p < 0.05.
    P5 overall: P5a OR P5b.
    """
    print("\n  [P5] Headless Configuration Consequence")
    ref = t3['reference']
    b5_by_folio = baseline_by_folio['B5']

    # -----------------------------------------------------------------------
    # P5a: Full vs B5
    # -----------------------------------------------------------------------
    print("    [P5a] Full vs B5 (forced H1)")
    n_c_better = 0
    n_s_better = 0
    p5a_per_folio = {}

    for folio in pilot_folios:
        full_viab = ref[folio]['viability']
        b5_viab = b5_by_folio[folio]['viability']

        c_better = full_viab > b5_viab
        if c_better:
            n_c_better += 1

        # Also check if Y_final improves
        full_yf = ref[folio]['Y_final']
        b5_yf = b5_by_folio[folio]['Y_final']
        s_better = full_yf > b5_yf
        if s_better:
            n_s_better += 1

        p5a_per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b5_viab': _round(b5_viab),
            'c_better': c_better,
            'full_Y_final': _round(full_yf),
            'b5_Y_final': _round(b5_yf),
            's_better': s_better,
        }

    p5a_pass = n_c_better >= PASS_THRESHOLD
    print(f"      full>B5 viability: {n_c_better}/20, "
          f"full>B5 Y_final: {n_s_better}/20 -> "
          f"{'PASS' if p5a_pass else 'FAIL'}")

    # -----------------------------------------------------------------------
    # P5b: KW across config mode groups
    # -----------------------------------------------------------------------
    print("    [P5b] KW across config mode groups")
    config_groups = defaultdict(list)
    for folio in pilot_folios:
        cm = folio_meta[folio]['config_mode']
        pref_run = folio_meta[folio]['preferred_run']
        config_groups[cm].append(pref_run['viability'])

    print(f"      Groups: {', '.join(f'{k}({len(v)})' for k, v in sorted(config_groups.items()))}")

    groups = []
    group_labels = []
    for cm in sorted(config_groups.keys()):
        vals = config_groups[cm]
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

    p5b_pass = p_val < 0.05
    print(f"      KW viability: H={_round(H_stat, 4)}, p={_round(p_val, 6)} -> "
          f"{'PASS' if p5b_pass else 'FAIL'}")

    passed = p5a_pass or p5b_pass
    print(f"    P5 overall: {'PASS' if passed else 'FAIL'} "
          f"(P5a={p5a_pass}, P5b={p5b_pass})")

    return {
        'pass': passed,
        'P5a': {
            'pass': p5a_pass,
            'C_better': n_c_better,
            'S_better': n_s_better,
            'per_folio': p5a_per_folio,
        },
        'P5b': {
            'pass': p5b_pass,
            'H': _round(H_stat, 4),
            'p': _round(p_val, 6),
            'group_means': {
                cm: _round(sum(v) / len(v))
                for cm, v in sorted(config_groups.items())
            },
        },
    }


# ---------------------------------------------------------------------------
# P6: CTS Closure Value
# ---------------------------------------------------------------------------
def test_p6(t3, pilot_folios, baseline_by_folio):
    """
    Full vs B3 (no CTS).
    viab_better: full viability > B3 viability
    C_sep_positive: full has more C corridor occupancy than B3
                    (proxy for containment separation since mean_state unavailable)
    Pass: viab_better >= 14/20 AND C_sep_positive >= 14/20
    """
    print("\n  [P6] CTS Closure Value")
    ref = t3['reference']
    b3_by_folio = baseline_by_folio['B3']

    n_viab_better = 0
    n_sep_positive = 0
    per_folio = {}

    for folio in pilot_folios:
        full_viab = ref[folio]['viability']
        b3_viab = b3_by_folio[folio]['viability']

        viab_better = full_viab > b3_viab
        if viab_better:
            n_viab_better += 1

        # Use C corridor + edge occupancy as proxy for containment separation
        # (higher C occupancy outside basin = more containment activity)
        full_c_out = (ref[folio]['zone_occupancy']['C'].get('CORRIDOR', 0.0) +
                      ref[folio]['zone_occupancy']['C'].get('EDGE', 0.0))
        b3_c_out = (b3_by_folio[folio]['zone_occupancy']['C'].get('CORRIDOR', 0.0) +
                    b3_by_folio[folio]['zone_occupancy']['C'].get('EDGE', 0.0))

        # Full model mean C > B3 mean C means full uses more containment
        # Proxy: full has higher C non-basin occupancy
        sep_positive = full_c_out > b3_c_out
        if sep_positive:
            n_sep_positive += 1

        per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b3_viab': _round(b3_viab),
            'viab_better': viab_better,
            'full_C_non_basin': _round(full_c_out),
            'b3_C_non_basin': _round(b3_c_out),
            'C_sep_positive': sep_positive,
        }

    passed = n_viab_better >= PASS_THRESHOLD and n_sep_positive >= PASS_THRESHOLD
    print(f"    viab_better: {n_viab_better}/20, C_sep_positive: {n_sep_positive}/20 -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'viab_better': n_viab_better,
        'C_sep_positive': n_sep_positive,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# P7: Null Destruction
# ---------------------------------------------------------------------------
def test_p7(t3, pilot_folios, folio_meta):
    """
    For each null type (N1-N4), for each folio:
      z = (full_viab - null_mean_viab) / max(null_std_viab, 0.001)
      destroyed = z > 2.0

    Per null type: passes if destroyed >= 14/20.
    Overall: >= 3/4 null types pass.
    """
    print("\n  [P7] Null Destruction")
    ref = t3['reference']
    null_runs = t3['null_runs']

    null_types = ['N1', 'N2', 'N3', 'N4']
    n_null_pass = 0
    per_null = {}

    for null_name in null_types:
        null_data = null_runs[null_name]
        n_destroyed = 0
        null_per_folio = {}

        for folio in pilot_folios:
            pref_run = folio_meta[folio]['preferred_run']
            full_viab = pref_run['viability']
            null_viab_mean = null_data[folio]['mean_viab']
            null_viab_std = null_data[folio]['std_viab']

            z = (full_viab - null_viab_mean) / max(null_viab_std, 0.001)
            destroyed = z > 2.0

            if destroyed:
                n_destroyed += 1

            null_per_folio[folio] = {
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
            'per_folio': null_per_folio,
        }

        tag = "PASS" if null_pass else "FAIL"
        print(f"    {null_name}: destroyed {n_destroyed}/20 -> {tag}")

    passed = n_null_pass >= 3
    print(f"    Overall P7: {n_null_pass}/4 null types pass -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'null_types_pass': n_null_pass,
        'details': per_null,
    }


# ---------------------------------------------------------------------------
# P8: Preferred Profile Superiority
# ---------------------------------------------------------------------------
def test_p8(pilot_folios, folio_meta):
    """
    For each folio, check if preferred profile is best on at least one metric
    (viability, Y_final, bounded_excursion_count) across all 3 profiles.
    Pass: preferred_best >= 14/20.
    """
    print("\n  [P8] Preferred Profile Superiority")

    n_preferred_best = 0
    per_folio = {}

    for folio in pilot_folios:
        meta = folio_meta[folio]
        preferred_profile = meta['preferred_profile']
        all_profiles = meta['all_profiles']

        if not all_profiles or preferred_profile not in all_profiles:
            per_folio[folio] = {'preferred_best': False, 'reason': 'missing_data'}
            continue

        viabilities = {}
        y_finals = {}
        bounded_counts = {}

        for profile, run in all_profiles.items():
            viabilities[profile] = run['viability']
            y_finals[profile] = run['Y_final']
            bounded_counts[profile] = run['bounded_excursion_count']

        pref_viab = viabilities[preferred_profile]
        pref_yf = y_finals[preferred_profile]
        pref_bc = bounded_counts[preferred_profile]

        other_viabs = [v for p, v in viabilities.items() if p != preferred_profile]
        other_yfs = [v for p, v in y_finals.items() if p != preferred_profile]
        other_bcs = [v for p, v in bounded_counts.items() if p != preferred_profile]

        best_viab = pref_viab >= max(other_viabs) if other_viabs else True
        best_yf = pref_yf >= max(other_yfs) if other_yfs else True
        best_bc = pref_bc >= max(other_bcs) if other_bcs else True

        preferred_best = best_viab or best_yf or best_bc
        if preferred_best:
            n_preferred_best += 1

        per_folio[folio] = {
            'preferred_profile': PROFILE_SHORT.get(preferred_profile, preferred_profile),
            'best_on_viab': best_viab,
            'best_on_Y_final': best_yf,
            'best_on_bounded': best_bc,
            'preferred_best': preferred_best,
            'viabilities': {PROFILE_SHORT.get(k, k): _round(v)
                            for k, v in viabilities.items()},
            'Y_finals': {PROFILE_SHORT.get(k, k): _round(v)
                         for k, v in y_finals.items()},
            'bounded_counts': {PROFILE_SHORT.get(k, k): v
                               for k, v in bounded_counts.items()},
        }

    passed = n_preferred_best >= PASS_THRESHOLD
    print(f"    preferred_best: {n_preferred_best}/20 -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'preferred_best': n_preferred_best,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# P9: Section-Template Recovery (secondary)
# ---------------------------------------------------------------------------
def test_p9(pilot_folios, folio_meta):
    """
    Group preferred runs by section (B, H, S, T, C). KW on each SV across
    sections. Pass: >=4/7 significant.
    P9 is secondary and non-gating.
    """
    print("\n  [P9] Section-Template Recovery (secondary)")

    section_groups = defaultdict(list)
    for folio in pilot_folios:
        meta = folio_meta[folio]
        section = meta['section']
        pref_run = meta['preferred_run']
        section_groups[section].append(pref_run['mean_state'])

    print(f"    Sections: {', '.join(f'{k}({len(v)})' for k, v in sorted(section_groups.items()))}")

    per_sv = {}
    n_significant = 0

    for sv_idx, sv in enumerate(STATE_VARS):
        groups = []
        group_labels = []
        for section in sorted(section_groups.keys()):
            vals = [ms[sv_idx] for ms in section_groups[section]]
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
                section: _round(
                    sum(ms[sv_idx] for ms in section_groups[section])
                    / len(section_groups[section])
                )
                for section in sorted(section_groups.keys())
            },
        }

        tag = "*" if sig else " "
        print(f"      {tag} {sv}: H={_round(H_stat, 4)}, p={_round(p_val, 6)}")

    print(f"    Significant SVs: {n_significant}/7 (non-gating)")

    return {
        'pass': None,  # secondary, non-gating
        'n_significant': n_significant,
        'secondary': True,
        'per_sv': per_sv,
        'section_sizes': {s: len(v) for s, v in section_groups.items()},
    }


# ---------------------------------------------------------------------------
# D1: Signal-to-Restoring-Force Ratio Audit (quasi-gating)
# ---------------------------------------------------------------------------
def diag_d1():
    """
    Compute analytically from T1 parameters:
    For each SV in WORK phase:
      signal_strength = P90_contribution[sv] * A3_sensitivity[sv]
      restoring_strength = gamma_corridor[sv] * 0.12 * corridor_mult['WORK'][sv]
      ratio = signal_strength / restoring_strength

    Quasi-gate: If mean corridor ratio < 0.5 across all SVs -> structurally compromised.
    """
    print("\n  [D1] Signal-to-Restoring-Force Ratio Audit")

    per_sv = {}
    ratios = []

    for sv in STATE_VARS:
        # P90 contribution magnitude (already scaled by sensitivity in P90_DV)
        signal = P90_DV[sv]

        # Restoring strength in corridor at mid-corridor deviation (0.12)
        corridor_dev = 0.12
        restoring = GAMMA_CORRIDOR[sv] * corridor_dev * CORRIDOR_MULT['WORK'][sv]

        ratio = signal / restoring if restoring > 1e-10 else float('inf')
        ratios.append(ratio)

        per_sv[sv] = {
            'signal': _round(signal, 6),
            'restoring': _round(restoring, 6),
            'ratio': _round(ratio, 4),
        }

        print(f"      {sv}: signal={_round(signal, 6)}, "
              f"restoring={_round(restoring, 6)}, ratio={_round(ratio, 4)}")

    mean_ratio = sum(ratios) / len(ratios) if ratios else 0.0
    quasi_gate_failed = mean_ratio < 0.5

    print(f"    Mean corridor ratio: {_round(mean_ratio, 4)}")
    print(f"    Quasi-gate: {'FAILED' if quasi_gate_failed else 'OK'}")

    return {
        'quasi_gate_failed': quasi_gate_failed,
        'mean_corridor_ratio': _round(mean_ratio, 4),
        'per_sv': per_sv,
    }


# ---------------------------------------------------------------------------
# D2: State-Space Occupancy Audit (quasi-gating)
# ---------------------------------------------------------------------------
def diag_d2(pilot_folios, folio_meta):
    """
    From T2 preferred runs, extract zone_occupancy per SV:
    Mean fraction in BASIN, CORRIDOR, EDGE across 20 folios.
    Quasi-gate: If mean corridor occupancy < 10% across ALL process SVs.
    """
    print("\n  [D2] State-Space Occupancy Audit")

    # Process SVs: those with hazard boundaries (exclude Y which is output accumulator)
    process_svs = [sv for sv in STATE_VARS if sv != 'Y']

    zone_accum = {sv: {'basin': [], 'corridor': [], 'edge': []} for sv in STATE_VARS}

    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        zo = pref_run.get('zone_occupancy', {})
        for sv in STATE_VARS:
            sv_zo = zo.get(sv, {})
            zone_accum[sv]['basin'].append(sv_zo.get('basin', 0.0))
            zone_accum[sv]['corridor'].append(sv_zo.get('corridor', 0.0))
            zone_accum[sv]['edge'].append(sv_zo.get('edge', 0.0))

    per_sv = {}
    corridor_fracs = []

    for sv in STATE_VARS:
        mean_b = sum(zone_accum[sv]['basin']) / len(zone_accum[sv]['basin'])
        mean_c = sum(zone_accum[sv]['corridor']) / len(zone_accum[sv]['corridor'])
        mean_e = sum(zone_accum[sv]['edge']) / len(zone_accum[sv]['edge'])

        per_sv[sv] = {
            'basin': _round(mean_b, 4),
            'corridor': _round(mean_c, 4),
            'edge': _round(mean_e, 4),
        }

        if sv in process_svs:
            corridor_fracs.append(mean_c)

        print(f"      {sv}: basin={mean_b:.4f}, corridor={mean_c:.4f}, edge={mean_e:.4f}")

    mean_corridor = sum(corridor_fracs) / len(corridor_fracs) if corridor_fracs else 0.0
    quasi_gate_failed = mean_corridor < 0.10

    print(f"    Mean process-SV corridor occupancy: {_round(mean_corridor, 4)}")
    print(f"    Quasi-gate: {'FAILED' if quasi_gate_failed else 'OK'}")

    return {
        'quasi_gate_failed': quasi_gate_failed,
        'mean_corridor_occupancy': _round(mean_corridor, 4),
        'per_sv': per_sv,
    }


# ---------------------------------------------------------------------------
# D3: B9 vs Full Comparison
# ---------------------------------------------------------------------------
def diag_d3(t3, pilot_folios, folio_meta, baseline_by_folio):
    """
    Compare full model vs B9 (uniform restoring):
    - Viability delta per folio
    - Excursion count delta
    - Bounded excursion delta
    - Zone occupancy delta
    - Mean viability delta
    - Count of folios where full > B9
    """
    print("\n  [D3] B9 vs Full Comparison")
    ref = t3['reference']
    b9_by_folio = baseline_by_folio['B9']

    viab_deltas = []
    n_full_gt_b9 = 0
    per_folio = []

    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        full_viab = pref_run['viability']
        b9_viab = b9_by_folio[folio]['viability']
        viab_delta = full_viab - b9_viab
        viab_deltas.append(viab_delta)

        if full_viab > b9_viab:
            n_full_gt_b9 += 1

        full_exc = pref_run['excursion_count']
        b9_exc = b9_by_folio[folio]['excursion_count']
        full_bec = pref_run['bounded_excursion_count']
        b9_bec = b9_by_folio[folio]['bounded_excursion_count']

        # Zone occupancy delta for corridor: how much does piecewise change it
        zo_delta = {}
        full_zo = pref_run.get('zone_occupancy', {})
        b9_zo = b9_by_folio[folio].get('zone_occupancy', {})
        for sv in STATE_VARS:
            full_corr = full_zo.get(sv, {}).get('corridor', 0.0)
            b9_corr = b9_zo.get(sv, {}).get('CORRIDOR', 0.0)
            zo_delta[sv] = _round(full_corr - b9_corr, 4)

        per_folio.append({
            'folio': folio,
            'full_viab': _round(full_viab),
            'B9_viab': _round(b9_viab),
            'viab_delta': _round(viab_delta),
            'full_excursion': full_exc,
            'B9_excursion': b9_exc,
            'exc_delta': full_exc - b9_exc,
            'full_bounded': full_bec,
            'B9_bounded': b9_bec,
            'bounded_delta': full_bec - b9_bec,
            'corridor_occ_delta': zo_delta,
        })

    mean_viab_delta = sum(viab_deltas) / len(viab_deltas) if viab_deltas else 0.0

    print(f"    Mean viability delta (full - B9): {_round(mean_viab_delta)}")
    print(f"    Folios where full > B9: {n_full_gt_b9}/20")

    # Print per-folio summary
    for entry in per_folio:
        tag = "+" if entry['viab_delta'] > 0 else ("=" if entry['viab_delta'] == 0 else "-")
        print(f"      {tag} {entry['folio']}: full={entry['full_viab']}, "
              f"B9={entry['B9_viab']}, delta={entry['viab_delta']}, "
              f"exc: {entry['full_excursion']} vs {entry['B9_excursion']}")

    return {
        'mean_viab_delta': _round(mean_viab_delta),
        'n_full_gt_B9': n_full_gt_b9,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    output_path = _PHASE_DIR / 'results' / 't4_behavior_validation.json'

    print("=" * 70)
    print("T4: Behavior Validation Battery")
    print("Phase 564b - VIRTUAL_APPARATUS_SELECTIVE_RESTORATION")
    print("=" * 70)

    # Load all data
    t2, t3, sup_tokens, line_packets = load_all_data()

    # Build folio metadata
    pilot_folios, folio_meta, baseline_by_folio = build_folio_metadata(
        t2, t3, sup_tokens)
    print(f"\n  Pilot folios: {len(pilot_folios)}")
    for f in pilot_folios:
        m = folio_meta[f]
        print(f"    {f}: {PROFILE_SHORT.get(m['preferred_profile'], m['preferred_profile'])}, "
              f"{m['config_mode']}, section={m['section']}, n_tokens={m['n_tokens']}")

    # Build per-folio token lists
    print("\n--- Building per-folio token lists ---")
    folio_tokens = build_folio_tokens(sup_tokens, pilot_folios, line_packets)
    for f in pilot_folios:
        n = len(folio_tokens.get(f, []))
        print(f"    {f}: {n} tokens")

    # Run tests
    print("\n" + "=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)

    tests = {}

    tests['P1'] = test_p1(t2, t3, pilot_folios, folio_meta, baseline_by_folio)
    tests['P2'] = test_p2(pilot_folios, folio_tokens)
    tests['P3'] = test_p3(pilot_folios, folio_meta)
    tests['P4'] = test_p4(t3, pilot_folios, folio_meta, folio_tokens,
                          baseline_by_folio)
    tests['P5'] = test_p5(t3, pilot_folios, folio_meta, baseline_by_folio)
    tests['P6'] = test_p6(t3, pilot_folios, baseline_by_folio)
    tests['P7'] = test_p7(t3, pilot_folios, folio_meta)
    tests['P8'] = test_p8(pilot_folios, folio_meta)
    tests['P9'] = test_p9(pilot_folios, folio_meta)

    # Diagnostics
    print("\n" + "=" * 70)
    print("RUNNING DIAGNOSTICS")
    print("=" * 70)

    diagnostics = {}
    diagnostics['D1'] = diag_d1()
    diagnostics['D2'] = diag_d2(pilot_folios, folio_meta)
    diagnostics['D3'] = diag_d3(t3, pilot_folios, folio_meta, baseline_by_folio)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # P9 is secondary (pass=None), exclude from core counts
    core_tests = {k: v for k, v in tests.items() if v.get('pass') is not None}
    core_pass = [k for k, v in core_tests.items() if v['pass']]
    core_fail = [k for k, v in core_tests.items() if not v['pass']]

    n_pass = len(core_pass)
    n_fail = len(core_fail)
    n_core = len(core_tests)

    print(f"\n  Core tests: {n_pass}/{n_core} pass")
    print(f"    PASS: {', '.join(core_pass) if core_pass else '(none)'}")
    print(f"    FAIL: {', '.join(core_fail) if core_fail else '(none)'}")

    p9_sig = tests['P9']['n_significant']
    print(f"  P9 (secondary): {p9_sig}/7 significant SVs")

    # Quasi-gate status
    qg_statuses = []
    if diagnostics['D1']['quasi_gate_failed']:
        qg_statuses.append('D1_FAILED')
    if diagnostics['D2']['quasi_gate_failed']:
        qg_statuses.append('D2_FAILED')
    qg_status = ', '.join(qg_statuses) if qg_statuses else 'ALL_OK'
    print(f"  Quasi-gate status: {qg_status}")

    summary = {
        'n_pass': n_pass,
        'n_fail': n_fail,
        'core_pass': n_pass >= 5,  # majority of 8 core tests
        'core_pass_list': core_pass,
        'core_fail_list': core_fail,
        'quasi_gate_status': qg_status,
    }

    elapsed = time.time() - t_start

    # Build output
    output = {
        'metadata': {
            'phase': '564b',
            'task': 'T4',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_tests': 9,
            'n_diagnostics': 3,
            'n_folios': len(pilot_folios),
            'threshold': PASS_THRESHOLD,
            'elapsed_seconds': round(elapsed, 2),
        },
        'tests': tests,
        'diagnostics': diagnostics,
        'summary': summary,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as fout:
        json.dump(output, fout, indent=1, cls=_NumpyEncoder)

    file_size = output_path.stat().st_size
    print(f"\n  Output: {output_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print(f"  Elapsed: {elapsed:.2f}s")
    print("  DONE")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
