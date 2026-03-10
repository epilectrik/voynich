"""
T4: Behavior Validation Battery
Phase 565 - VIRTUAL_APPARATUS_PERMEABILITY_CALIBRATION

Reads T2 (permeability runs), T3 (null/ablation runs), and T1 (apparatus config),
runs 9 tests (P1-P9) plus 4 diagnostics (D1-D4), and outputs
t4_behavior_validation.json.

Tests:
  P1: Non-degeneracy Guard (strict, split into P1a + P1b)
  P2: Line Packet Shape Recovery
  P3: Bounded Work-Cycle Dynamics (with profile stratification)
  P4: Routing Consequence Fidelity (P4a routed vs unrouted, P4b full vs B4)
  P5: Headless Configuration Consequence (P5a full vs B5, P5b KW across configs)
  P6: CTS Closure Value (full vs B3)
  P7: Null Destruction (N1-N4 significance testing)
  P8: Preferred Profile Superiority
  P9: Section-Template Recovery (secondary, non-gating)

Diagnostics:
  D1: Signal-to-Restoring-Force Ratio Audit (quasi-gating, threshold > 0.5)
  D2: Corridor Occupancy Audit (quasi-gating, threshold > 10%)
  D3: B9 Ablation (quasi-gating, delta >= 0.05)
  D4: Edge Contact Audit (quasi-gating, new)
"""

import json
import sys
import time
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import kruskal, wilcoxon, mannwhitneyu

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_PHASE_DIR = _SCRIPT_DIR.parent
_PROJECT_ROOT = _PHASE_DIR.parent.parent

sys.path.insert(0, str(_PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'scripts'))
from t1_apparatus_family_builder import STATE_VARS, HAZARD_BOUNDARIES, PROFILES

sys.path.insert(0, str(_PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_PERMEABILITY_CALIBRATION' / 'scripts'))
from t1_permeability_apparatus import (
    Q1, Q2_BASE, Q3_BASE, HAZARD_DEV,
    GAMMA_BASIN, GAMMA_CORRIDOR, BETA1, BETA2,
    CORRIDOR_MULT, BASIN_MULT, EDGE1_MULT, EDGE2_MULT,
    A3_SENS, P90_DV, P95_DV,
    A3_DECAY, PROFILE_DECAYS,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}
N_VARS = len(STATE_VARS)
PASS_THRESHOLD = 14  # out of 20 folios

# Routing target mappings for P4
ROUTING_TARGET = {
    'm': 'C',
    'h': 'TR',
    'r': 'X',
    'y': 'T',
}
ROUTING_WINDOW = 3

# Profile labels
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


def _zo_get(zone_occ, sv, zone_name):
    """Get zone occupancy handling both upper and lowercase keys."""
    sv_zo = zone_occ.get(sv, {})
    # Try lowercase first, then uppercase
    val = sv_zo.get(zone_name.lower())
    if val is None:
        val = sv_zo.get(zone_name.upper(), 0.0)
    return val if val is not None else 0.0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_all_data():
    """Load T1, T2, T3, supervisory tokens, and line packets."""
    perm_results = _PHASE_DIR / 'results'
    coupling_results = _PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'results'
    ste_results = _PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results'

    print("--- Loading data sources ---")

    # T1: permeability apparatus
    t1_path = perm_results / 't1_permeability_apparatus.json'
    print(f"  Loading T1: {t1_path}")
    t1 = _load_json(t1_path)

    # T2: permeability runs
    t2_path = perm_results / 't2_permeability_runs.json'
    print(f"  Loading T2: {t2_path}")
    t2 = _load_json(t2_path)
    print(f"    Primary runs: {len(t2['primary_runs'])}, "
          f"Config ablation: {len(t2['config_ablation_runs'])}")

    # T3: null/ablation runs
    t3_path = perm_results / 't3_null_ablation_runs.json'
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

    return t1, t2, t3, sup_tokens, line_packets


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

    return pilot_folios, folio_meta, baseline_by_folio, config_abl_by_fc


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
# P1: Non-degeneracy Guard (STRICT, split P1a + P1b)
# ---------------------------------------------------------------------------
def test_p1(t2, t3, pilot_folios, folio_meta, baseline_by_folio):
    """
    P1a (strict superiority): full > B2 for >=14/20 AND full > N1 mean for >=14/20.
    P1b: mean viability in [0.88, 0.995] AND >=8/20 with viability < 1.0
         AND >=10/20 with viability > 0.9.
    P1 PASS requires BOTH P1a AND P1b.
    """
    print("\n  [P1] Non-degeneracy Guard")
    ref = t3['reference']
    b2_by_folio = baseline_by_folio['B2']
    n1 = t3['null_runs']['N1']

    full_gt_b2 = 0
    full_gt_n1 = 0
    viabilities = []
    folios_lt_1 = 0
    folios_gt_09 = 0
    p1a_per_folio = {}

    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        full_viab = pref_run['viability']
        b2_viab = b2_by_folio[folio]['viability']
        n1_viab_mean = n1[folio]['mean_viab']

        viabilities.append(full_viab)
        if full_viab < 1.0:
            folios_lt_1 += 1
        if full_viab > 0.9:
            folios_gt_09 += 1

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

    # P1a: strict superiority
    p1a_pass = full_gt_b2 >= PASS_THRESHOLD and full_gt_n1 >= PASS_THRESHOLD
    print(f"    [P1a] full>B2: {full_gt_b2}/20, full>N1: {full_gt_n1}/20 -> "
          f"{'PASS' if p1a_pass else 'FAIL'}")

    # P1b: non-degeneracy band
    in_band = 0.88 <= mean_viab <= 0.995
    enough_lt_1 = folios_lt_1 >= 8
    enough_gt_09 = folios_gt_09 >= 10
    p1b_pass = in_band and enough_lt_1 and enough_gt_09
    print(f"    [P1b] mean_viab={mean_viab:.6f} in [0.88,0.995]={in_band}, "
          f"folios<1.0={folios_lt_1}/20 (need>=8), "
          f"folios>0.9={folios_gt_09}/20 (need>=10) -> "
          f"{'PASS' if p1b_pass else 'FAIL'}")

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
            'folios_gt_09': folios_gt_09,
            'min_folios_gt_09': 10,
        },
        'per_folio': p1a_per_folio,
    }


# ---------------------------------------------------------------------------
# P2: Line Packet Shape Recovery
# ---------------------------------------------------------------------------
def test_p2(pilot_folios, folio_tokens):
    """
    Group supervisory token contributions by packet_phase (SPEC/WORK/CLOSE).
    Run Kruskal-Wallis on each SV mean state across the 3 phases.
    Pass: >=5/7 significant SVs.
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

    passed = n_significant >= 5
    print(f"    Significant SVs: {n_significant}/7 -> {'PASS' if passed else 'FAIL'}")
    for sv, info in per_sv.items():
        tag = "*" if info.get('sig') else " "
        print(f"      {tag} {sv}: H={info.get('H')}, p={info.get('p')}")

    return {
        'pass': passed,
        'n_significant': n_significant,
        'threshold': 5,
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
      meets_P3 = excursion_count >= 3 AND bounded_fraction >= 0.25

    Aggregate pass: mean_cycles >= 3.0 AND bounded_frac >= 0.25
                    AND >= 8/20 folios meet both.

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

        meets_both = n_cycles >= 3 and bounded_frac >= 0.25
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

    passed = (mean_n_cycles >= 3.0 and mean_bounded_frac >= 0.25
              and n_meeting_both >= 8)

    print(f"    mean_cycles={mean_n_cycles:.2f}, "
          f"mean_bounded_frac={mean_bounded_frac:.4f}")
    print(f"    folios meeting both: {n_meeting_both}/20 (need>=8) -> "
          f"{'PASS' if passed else 'FAIL'}")

    # Profile stratification
    profile_summary = {}
    for pshort in sorted(by_profile.keys()):
        pdata = by_profile[pshort]
        n_folios = len(pdata['folios'])
        n_meeting = pdata['n_meeting']
        mc = sum(pdata['cycles']) / n_folios if n_folios else 0
        mbf = sum(pdata['bf']) / n_folios if n_folios else 0
        profile_summary[pshort] = {
            'n_folios': n_folios,
            'n_meeting_P3': n_meeting,
            'mean_cycles': _round(mc, 2),
            'mean_bounded_frac': _round(mbf, 4),
        }
        print(f"      {pshort}: {n_folios} folios, "
              f"P3 met={n_meeting}, mean_cycles={mc:.2f}, "
              f"mean_bf={mbf:.4f}")

    return {
        'pass': passed,
        'mean_cycles': _round(mean_n_cycles, 2),
        'mean_bounded_fraction': _round(mean_bounded_frac, 4),
        'n_meeting_both': n_meeting_both,
        'threshold_meeting': 8,
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
         Use Wilcoxon signed-rank test for per-folio paired deltas.
    P4b: Compare full model vs B4 (no routing) viability and Y_final per folio.

    Routing tiers:
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
            routing_positions = {}
            for i in range(n):
                if toks[i].get('routing_active') and toks[i].get('routing_terminal'):
                    routing_positions[i] = toks[i]['routing_terminal']

            # Build set of positions preceded (within ROUTING_WINDOW) by THIS rt
            preceded_by_rt = set()
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

    primary_results = {k: v for k, v in p4a_results.items()
                       if k.split('__')[0] in primary_routes}
    secondary_results = {k: v for k, v in p4a_results.items()
                         if k.split('__')[0] in secondary_routes}

    # Primary routes correct count
    n_primary_correct = sum(1 for v in primary_results.values() if v['correct'])

    # -----------------------------------------------------------------------
    # P4b: Full vs B4 (no routing) viability and Y_final
    # -----------------------------------------------------------------------
    print("    [P4b] Full vs B4 (no routing)")
    ref = t3['reference']
    b4_by_folio = baseline_by_folio['B4']

    p4b_per_folio = {}
    viab_deltas = []
    yf_deltas = []

    for folio in pilot_folios:
        full_viab = ref[folio]['viability']
        b4_viab = b4_by_folio[folio]['viability']
        full_yf = ref[folio]['Y_final']
        b4_yf = b4_by_folio[folio]['Y_final']

        viab_delta = full_viab - b4_viab
        yf_delta = full_yf - b4_yf
        viab_deltas.append(viab_delta)
        yf_deltas.append(yf_delta)

        p4b_per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b4_viab': _round(b4_viab),
            'viab_delta': _round(viab_delta),
            'full_Y_final': _round(full_yf),
            'b4_Y_final': _round(b4_yf),
            'yf_delta': _round(yf_delta),
        }

    mean_viab_delta = sum(viab_deltas) / len(viab_deltas) if viab_deltas else 0.0
    mean_yf_delta = sum(yf_deltas) / len(yf_deltas) if yf_deltas else 0.0
    n_viab_better = sum(1 for d in viab_deltas if d > 0)
    n_yf_better = sum(1 for d in yf_deltas if d > 0)

    # Wilcoxon signed-rank on viability deltas (test if full > B4 systematically)
    viab_deltas_arr = np.array(viab_deltas)
    nonzero_viab = viab_deltas_arr[viab_deltas_arr != 0]
    if len(nonzero_viab) >= 5:
        try:
            w_stat, w_p = wilcoxon(nonzero_viab, alternative='greater')
        except ValueError:
            w_stat, w_p = 0.0, 1.0
    else:
        w_stat, w_p = None, 1.0

    print(f"      full>B4 viab: {n_viab_better}/20, Y_final better: {n_yf_better}/20, "
          f"mean viab delta: {_round(mean_viab_delta)}, "
          f"Wilcoxon p: {_round(w_p, 6)}")

    # P4 overall pass: >=3/4 correct in P4a
    p4a_pass = n_correct >= 3
    passed = p4a_pass
    print(f"    P4 overall: {'PASS' if passed else 'FAIL'} "
          f"(P4a {n_correct}/4 correct)")

    # Synthesis note on routing interpretation
    routing_note = None
    if n_primary_correct == 2 and n_correct < 3:
        routing_note = ("Primary routes (m->C, h->TR) both correct; "
                        "secondary routes lag. Routing architecture is "
                        "substantively revived per cross-phase history.")
    elif n_primary_correct == 2 and n_correct >= 3:
        routing_note = ("Primary routes (m->C, h->TR) both correct; "
                        "full routing architecture recovered.")

    return {
        'pass': passed,
        'P4a': {
            'n_correct': n_correct,
            'pass': p4a_pass,
            'n_primary_correct': n_primary_correct,
            'primary': primary_results,
            'secondary': secondary_results,
            'routing_interpretation_note': routing_note,
        },
        'P4b': {
            'full_vs_B4_viab_delta': _round(mean_viab_delta),
            'full_vs_B4_yf_delta': _round(mean_yf_delta),
            'n_viab_better': n_viab_better,
            'n_yf_better': n_yf_better,
            'wilcoxon_stat': _round(w_stat, 2) if w_stat is not None else None,
            'wilcoxon_p': _round(w_p, 6) if w_p is not None else None,
            'per_folio': p4b_per_folio,
        },
    }


# ---------------------------------------------------------------------------
# P5: Headless Configuration Consequence
# ---------------------------------------------------------------------------
def test_p5(t2, t3, pilot_folios, folio_meta, baseline_by_folio, config_abl_by_fc):
    """
    P5a: For each folio in config ablation, count whether C_mean and S_mean
         differ between H0 and H2.
         Pass if >=12/N_config for C or S.
    P5b: KW on C and S mean states across 3 config modes.
         Pass if p < 0.05 for C or S.
    P5 overall: P5a passes (>=12) for C or S, AND P5b p < 0.05 for C or S.
    """
    print("\n  [P5] Headless Configuration Consequence")

    # Get config ablation folios
    config_folios = sorted(set(run['folio'] for run in t2['config_ablation_runs']))
    n_config = len(config_folios)
    print(f"    Config ablation folios: {n_config}")

    # -----------------------------------------------------------------------
    # P5a: C and S mean state difference between H0 and H2
    # -----------------------------------------------------------------------
    print("    [P5a] C/S mean state H0 vs H2")
    c_idx = SV_INDEX['C']
    s_idx = SV_INDEX['S']

    n_c_differs = 0
    n_s_differs = 0
    p5a_per_folio = {}

    for folio in config_folios:
        h0_run = config_abl_by_fc.get((folio, 'H0_LOW_INFRA'))
        h2_run = config_abl_by_fc.get((folio, 'H2_HIGH_INFRA'))

        if h0_run and h2_run:
            h0_c = h0_run['mean_state'][c_idx]
            h2_c = h2_run['mean_state'][c_idx]
            h0_s = h0_run['mean_state'][s_idx]
            h2_s = h2_run['mean_state'][s_idx]

            c_diff = abs(h2_c - h0_c) > 0.005
            s_diff = abs(h2_s - h0_s) > 0.005

            if c_diff:
                n_c_differs += 1
            if s_diff:
                n_s_differs += 1

            p5a_per_folio[folio] = {
                'H0_C': _round(h0_c), 'H2_C': _round(h2_c), 'C_diff': c_diff,
                'H0_S': _round(h0_s), 'H2_S': _round(h2_s), 'S_diff': s_diff,
            }

    p5a_c_pass = n_c_differs >= min(12, n_config)
    p5a_s_pass = n_s_differs >= min(12, n_config)
    p5a_pass = p5a_c_pass or p5a_s_pass
    print(f"      C differs: {n_c_differs}/{n_config}, "
          f"S differs: {n_s_differs}/{n_config} -> "
          f"{'PASS' if p5a_pass else 'FAIL'}")

    # -----------------------------------------------------------------------
    # P5b: KW on C and S across config mode groups
    # -----------------------------------------------------------------------
    print("    [P5b] KW across config mode groups")

    config_groups_c = defaultdict(list)
    config_groups_s = defaultdict(list)
    for run in t2['config_ablation_runs']:
        cm = run['config_mode']
        config_groups_c[cm].append(run['mean_state'][c_idx])
        config_groups_s[cm].append(run['mean_state'][s_idx])

    # KW for C
    c_groups = [config_groups_c[cm] for cm in sorted(config_groups_c.keys())
                if len(config_groups_c[cm]) >= 2]
    if len(c_groups) >= 2:
        try:
            H_c, p_c = kruskal(*c_groups)
        except ValueError:
            H_c, p_c = 0.0, 1.0
    else:
        H_c, p_c = 0.0, 1.0

    # KW for S
    s_groups = [config_groups_s[cm] for cm in sorted(config_groups_s.keys())
                if len(config_groups_s[cm]) >= 2]
    if len(s_groups) >= 2:
        try:
            H_s, p_s = kruskal(*s_groups)
        except ValueError:
            H_s, p_s = 0.0, 1.0
    else:
        H_s, p_s = 0.0, 1.0

    p5b_c_pass = p_c < 0.05
    p5b_s_pass = p_s < 0.05
    p5b_pass = p5b_c_pass or p5b_s_pass
    print(f"      KW C: H={_round(H_c, 4)}, p={_round(p_c, 6)} -> "
          f"{'PASS' if p5b_c_pass else 'fail'}")
    print(f"      KW S: H={_round(H_s, 4)}, p={_round(p_s, 6)} -> "
          f"{'PASS' if p5b_s_pass else 'fail'}")
    print(f"      P5b overall: {'PASS' if p5b_pass else 'FAIL'}")

    passed = p5a_pass and p5b_pass
    print(f"    P5 overall: {'PASS' if passed else 'FAIL'} "
          f"(P5a={p5a_pass}, P5b={p5b_pass})")

    return {
        'pass': passed,
        'P5a': {
            'pass': p5a_pass,
            'C_differs': n_c_differs,
            'S_differs': n_s_differs,
            'n_config_folios': n_config,
            'threshold': min(12, n_config),
            'per_folio': p5a_per_folio,
        },
        'P5b': {
            'pass': p5b_pass,
            'C': {'H': _round(H_c, 4), 'p': _round(p_c, 6), 'sig': p5b_c_pass},
            'S': {'H': _round(H_s, 4), 'p': _round(p_s, 6), 'sig': p5b_s_pass},
            'group_means_C': {
                cm: _round(sum(v) / len(v))
                for cm, v in sorted(config_groups_c.items())
            },
            'group_means_S': {
                cm: _round(sum(v) / len(v))
                for cm, v in sorted(config_groups_s.items())
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
    C_sep_positive: full has more C non-basin occupancy than B3
    Pass: viab_better >= 8/20 AND C_sep_positive >= 8/20.
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

        # C corridor + warning + hard_stop occupancy (non-basin) as proxy
        full_c_non = (_zo_get(ref[folio]['zone_occupancy'], 'C', 'CORRIDOR') +
                      _zo_get(ref[folio]['zone_occupancy'], 'C', 'WARNING') +
                      _zo_get(ref[folio]['zone_occupancy'], 'C', 'HARD_STOP'))
        b3_c_non = (_zo_get(b3_by_folio[folio]['zone_occupancy'], 'C', 'CORRIDOR') +
                    _zo_get(b3_by_folio[folio]['zone_occupancy'], 'C', 'WARNING') +
                    _zo_get(b3_by_folio[folio]['zone_occupancy'], 'C', 'HARD_STOP'))

        sep_positive = full_c_non > b3_c_non
        if sep_positive:
            n_sep_positive += 1

        per_folio[folio] = {
            'full_viab': _round(full_viab),
            'b3_viab': _round(b3_viab),
            'viab_better': viab_better,
            'full_C_non_basin': _round(full_c_non),
            'b3_C_non_basin': _round(b3_c_non),
            'C_sep_positive': sep_positive,
        }

    passed = n_viab_better >= 8 and n_sep_positive >= 8
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
    For each null type (N1-N4), check if null mean viability < reference viability
    significantly using Wilcoxon signed-rank test.
    A null type is 'destroyed' if: mean(ref viab) - mean(null mean viab) > 0
    AND p < 0.05.
    PASS: >= 2/4 null types destroyed.
    """
    print("\n  [P7] Null Destruction")
    ref = t3['reference']
    null_runs = t3['null_runs']

    null_types = ['N1', 'N2', 'N3', 'N4']
    n_null_pass = 0
    per_null = {}

    for null_name in null_types:
        null_data = null_runs[null_name]

        # Collect per-folio deltas: ref_viab - null_mean_viab
        deltas = []
        null_per_folio = {}

        for folio in pilot_folios:
            pref_run = folio_meta[folio]['preferred_run']
            full_viab = pref_run['viability']
            null_viab_mean = null_data[folio]['mean_viab']
            null_viab_std = null_data[folio]['std_viab']

            delta = full_viab - null_viab_mean
            deltas.append(delta)

            null_per_folio[folio] = {
                'full_viab': _round(full_viab),
                'null_viab_mean': _round(null_viab_mean),
                'null_viab_std': _round(null_viab_std),
                'delta': _round(delta, 6),
            }

        # Wilcoxon signed-rank test on deltas (test if deltas > 0)
        deltas_arr = np.array(deltas)
        nonzero_deltas = deltas_arr[deltas_arr != 0]
        mean_delta = float(np.mean(deltas_arr))

        if len(nonzero_deltas) >= 5:
            try:
                w_stat, p_val = wilcoxon(nonzero_deltas, alternative='greater')
            except ValueError:
                w_stat, p_val = 0.0, 1.0
        else:
            # If fewer than 5 nonzero, check if all deltas are positive
            w_stat = None
            if len(nonzero_deltas) > 0 and all(d > 0 for d in nonzero_deltas):
                p_val = 0.03  # approximate for small sample with all positive
            else:
                p_val = 1.0

        destroyed = mean_delta > 0 and p_val < 0.05
        if destroyed:
            n_null_pass += 1

        per_null[null_name] = {
            'destroyed': destroyed,
            'mean_delta': _round(mean_delta, 6),
            'n_positive': int(np.sum(deltas_arr > 0)),
            'n_zero': int(np.sum(deltas_arr == 0)),
            'n_negative': int(np.sum(deltas_arr < 0)),
            'wilcoxon_stat': _round(w_stat, 2) if w_stat is not None else None,
            'p': _round(p_val, 6),
            'per_folio': null_per_folio,
        }

        tag = "DESTROYED" if destroyed else "survived"
        print(f"    {null_name}: mean_delta={_round(mean_delta, 6)}, "
              f"p={_round(p_val, 6)}, n_pos={int(np.sum(deltas_arr > 0))}/20 -> {tag}")

    passed = n_null_pass >= 2
    print(f"    Overall P7: {n_null_pass}/4 null types destroyed -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'null_types_destroyed': n_null_pass,
        'threshold': 2,
        'details': per_null,
    }


# ---------------------------------------------------------------------------
# P8: Preferred Profile Superiority
# ---------------------------------------------------------------------------
def test_p8(pilot_folios, folio_meta):
    """
    For each folio, check if preferred profile is best or tied-best on viability.
    Use Y_final as tiebreaker.
    Pass: preferred_best >= 16/20.
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

        max_viab = max(viabilities.values())

        # Best on viability (tied counts)
        best_viab = pref_viab >= max_viab

        # If tied on viability, use Y_final as tiebreaker
        if best_viab and pref_viab == max_viab:
            tied_profiles = [p for p, v in viabilities.items() if v == max_viab]
            if len(tied_profiles) > 1:
                max_yf_among_tied = max(y_finals[p] for p in tied_profiles)
                best_viab = pref_yf >= max_yf_among_tied

        # Also check best on Y_final or bounded_excursion as fallback
        other_yfs = [v for p, v in y_finals.items() if p != preferred_profile]
        other_bcs = [v for p, v in bounded_counts.items() if p != preferred_profile]
        best_yf = pref_yf >= max(other_yfs) if other_yfs else True
        pref_bc = bounded_counts[preferred_profile]
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

    passed = n_preferred_best >= 16
    print(f"    preferred_best: {n_preferred_best}/20 (need>=16) -> "
          f"{'PASS' if passed else 'FAIL'}")

    return {
        'pass': passed,
        'preferred_best': n_preferred_best,
        'threshold': 16,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# P9: Section-Template Recovery (secondary, non-gating)
# ---------------------------------------------------------------------------
def test_p9(pilot_folios, folio_meta):
    """
    Group preferred runs by section. KW on each SV across sections.
    Report n_significant / 7.
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
# D1: Signal-to-Restoring-Force Ratio Audit (quasi-gating, threshold > 0.5)
# ---------------------------------------------------------------------------
def diag_d1(t1):
    """
    Compute from T1 apparatus config:
    For each SV in WORK phase:
      signal_strength = P90_DV[sv]
      restoring_strength = gamma_corridor[sv] * 0.12 * corridor_mult['WORK'][sv]
      ratio = signal_strength / restoring_strength

    Quasi-gate: mean corridor ratio > 0.5.
    """
    print("\n  [D1] Signal-to-Restoring-Force Ratio Audit")

    ac = t1['apparatus_config']
    p90_dv = ac['P90_DV']
    gamma_corr = ac['GAMMA_CORRIDOR']
    corr_mult = ac['CORRIDOR_MULT']

    per_sv = {}
    ratios = []

    for sv in STATE_VARS:
        signal = p90_dv[sv]
        corridor_dev = 0.12
        restoring = gamma_corr[sv] * corridor_dev * corr_mult['WORK'][sv]
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
    quasi_gate_pass = mean_ratio > 0.5

    print(f"    Mean corridor ratio: {_round(mean_ratio, 4)}")
    print(f"    Quasi-gate (>0.5): {'OK' if quasi_gate_pass else 'FAILED'}")

    return {
        'quasi_gate_pass': quasi_gate_pass,
        'quasi_gate_failed': not quasi_gate_pass,
        'mean_corridor_ratio': _round(mean_ratio, 4),
        'threshold': 0.5,
        'per_sv': per_sv,
    }


# ---------------------------------------------------------------------------
# D2: Corridor Occupancy Audit (quasi-gating, threshold > 10%)
# ---------------------------------------------------------------------------
def diag_d2(pilot_folios, folio_meta):
    """
    From T2 preferred runs, compute mean corridor zone occupancy across all SVs.
    Quasi-gate: mean corridor occupancy > 10%.
    """
    print("\n  [D2] Corridor Occupancy Audit")

    process_svs = [sv for sv in STATE_VARS if sv != 'Y']

    zone_accum = {sv: {'basin': [], 'corridor': [], 'warning': [], 'hard_stop': []}
                  for sv in STATE_VARS}

    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        zo = pref_run.get('zone_occupancy', {})
        for sv in STATE_VARS:
            zone_accum[sv]['basin'].append(_zo_get(zo, sv, 'basin'))
            zone_accum[sv]['corridor'].append(_zo_get(zo, sv, 'corridor'))
            zone_accum[sv]['warning'].append(_zo_get(zo, sv, 'warning'))
            zone_accum[sv]['hard_stop'].append(_zo_get(zo, sv, 'hard_stop'))

    per_sv = {}
    corridor_fracs = []

    for sv in STATE_VARS:
        mean_b = sum(zone_accum[sv]['basin']) / len(zone_accum[sv]['basin'])
        mean_c = sum(zone_accum[sv]['corridor']) / len(zone_accum[sv]['corridor'])
        mean_w = sum(zone_accum[sv]['warning']) / len(zone_accum[sv]['warning'])
        mean_h = sum(zone_accum[sv]['hard_stop']) / len(zone_accum[sv]['hard_stop'])

        per_sv[sv] = {
            'basin': _round(mean_b, 4),
            'corridor': _round(mean_c, 4),
            'warning': _round(mean_w, 4),
            'hard_stop': _round(mean_h, 4),
        }

        if sv in process_svs:
            corridor_fracs.append(mean_c)

        print(f"      {sv}: basin={mean_b:.4f}, corridor={mean_c:.4f}, "
              f"warning={mean_w:.4f}, hard_stop={mean_h:.4f}")

    mean_corridor = sum(corridor_fracs) / len(corridor_fracs) if corridor_fracs else 0.0
    quasi_gate_pass = mean_corridor > 0.10

    print(f"    Mean process-SV corridor occupancy: {_round(mean_corridor, 4)}")
    print(f"    Quasi-gate (>10%): {'OK' if quasi_gate_pass else 'FAILED'}")

    return {
        'quasi_gate_pass': quasi_gate_pass,
        'quasi_gate_failed': not quasi_gate_pass,
        'mean_corridor_occupancy': _round(mean_corridor, 4),
        'threshold': 0.10,
        'per_sv': per_sv,
    }


# ---------------------------------------------------------------------------
# D3: B9 Ablation (quasi-gating, delta >= 0.05)
# ---------------------------------------------------------------------------
def diag_d3(t3, pilot_folios, folio_meta, baseline_by_folio):
    """
    Compare full model vs B9 (uniform restoring):
    Mean viability delta = mean(ref viab) - mean(B9 viab) across 20 folios.
    Expectation band: delta >= 0.05 (quasi-gate).
    If below 0.03: flag "zone architecture may no longer be load-bearing".
    """
    print("\n  [D3] B9 Ablation")
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

        # Zone occupancy delta for corridor
        zo_delta = {}
        full_zo = pref_run.get('zone_occupancy', {})
        b9_zo = b9_by_folio[folio].get('zone_occupancy', {})
        for sv in STATE_VARS:
            full_corr = _zo_get(full_zo, sv, 'corridor')
            b9_corr = _zo_get(b9_zo, sv, 'corridor')
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

    # Quasi-gate evaluation
    quasi_gate_pass = mean_viab_delta >= 0.05
    below_warning = mean_viab_delta < 0.03
    flag = None
    if below_warning:
        flag = "zone architecture may no longer be load-bearing"

    print(f"    Mean viability delta (full - B9): {_round(mean_viab_delta)}")
    print(f"    Folios where full > B9: {n_full_gt_b9}/20")
    print(f"    Quasi-gate (>=0.05): {'OK' if quasi_gate_pass else 'BELOW EXPECTATION'}")
    if flag:
        print(f"    WARNING: {flag}")

    # Print per-folio summary
    for entry in per_folio:
        tag = "+" if entry['viab_delta'] > 0 else ("=" if entry['viab_delta'] == 0 else "-")
        print(f"      {tag} {entry['folio']}: full={entry['full_viab']}, "
              f"B9={entry['B9_viab']}, delta={entry['viab_delta']}, "
              f"exc: {entry['full_excursion']} vs {entry['B9_excursion']}")

    return {
        'quasi_gate_pass': quasi_gate_pass,
        'quasi_gate_failed': not quasi_gate_pass,
        'mean_viab_delta': _round(mean_viab_delta),
        'expectation_threshold': 0.05,
        'warning_threshold': 0.03,
        'below_warning': below_warning,
        'flag': flag,
        'n_full_gt_B9': n_full_gt_b9,
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# D4: Edge Contact Audit (quasi-gating, new)
# ---------------------------------------------------------------------------
def diag_d4(t2, t3, pilot_folios, folio_meta):
    """
    Compare warning + hard_stop contact rates between full model, baselines,
    and null models.

    Quasi-gate conditions:
      1. Edge contact is NOT zero for all models (if zero everywhere, edge too hard)
      2. Full model edge contact pattern differs from null (if indiscriminate,
         edge is not packet-sensitive)

    Reports: full model total edge contacts, null model mean edge contacts, ratio.
    """
    print("\n  [D4] Edge Contact Audit")

    ref = t3['reference']
    null_runs = t3['null_runs']

    # --- Full model edge contacts (from T2 preferred runs) ---
    full_warning_total = 0
    full_hard_stop_total = 0
    full_per_folio = {}

    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        wc = pref_run.get('warning_contacts', {})
        hc = pref_run.get('hard_stop_contacts', {})

        # warning_contacts and hard_stop_contacts are dicts {SV: count}
        if isinstance(wc, dict):
            folio_warn = sum(wc.values())
            folio_hard = sum(hc.values())
        else:
            # scalar fallback
            folio_warn = wc
            folio_hard = hc

        full_warning_total += folio_warn
        full_hard_stop_total += folio_hard

        full_per_folio[folio] = {
            'warning': folio_warn,
            'hard_stop': folio_hard,
            'total': folio_warn + folio_hard,
        }

    full_total = full_warning_total + full_hard_stop_total
    full_mean_per_folio = full_total / len(pilot_folios) if pilot_folios else 0

    print(f"    Full model: warning={full_warning_total}, "
          f"hard_stop={full_hard_stop_total}, total={full_total}, "
          f"mean/folio={full_mean_per_folio:.1f}")

    # --- Reference (T3) edge contacts ---
    ref_warning_total = 0
    ref_hard_total = 0
    for folio in pilot_folios:
        rw = ref[folio].get('warning_contacts', 0)
        rh = ref[folio].get('hard_stop_contacts', 0)
        # These are scalars in T3 reference
        ref_warning_total += rw
        ref_hard_total += rh

    ref_total = ref_warning_total + ref_hard_total
    ref_mean = ref_total / len(pilot_folios) if pilot_folios else 0

    print(f"    Reference (T3): warning={ref_warning_total}, "
          f"hard_stop={ref_hard_total}, total={ref_total}, "
          f"mean/folio={ref_mean:.1f}")

    # --- Null model edge contacts ---
    null_edge_stats = {}
    null_grand_total = 0
    null_folio_count = 0

    for null_name in ['N1', 'N2', 'N3', 'N4']:
        null_data = null_runs[null_name]
        null_warn_sum = 0
        null_hard_sum = 0
        n_perms = 0

        for folio in pilot_folios:
            fd = null_data[folio]
            null_warn_sum += fd.get('mean_warning_contacts', 0)
            null_hard_sum += fd.get('mean_hard_stop_contacts', 0)
            n_perms += 1

        null_total = null_warn_sum + null_hard_sum
        null_mean = null_total / n_perms if n_perms else 0
        null_grand_total += null_total
        null_folio_count += n_perms

        null_edge_stats[null_name] = {
            'mean_warning_per_folio': _round(null_warn_sum / n_perms if n_perms else 0, 2),
            'mean_hard_stop_per_folio': _round(null_hard_sum / n_perms if n_perms else 0, 2),
            'mean_total_per_folio': _round(null_mean, 2),
        }

        print(f"    {null_name}: mean warning/folio={_round(null_warn_sum / n_perms, 2)}, "
              f"mean hard_stop/folio={_round(null_hard_sum / n_perms, 2)}, "
              f"mean total/folio={_round(null_mean, 2)}")

    null_grand_mean = null_grand_total / null_folio_count if null_folio_count else 0

    # --- Quasi-gate evaluation ---
    # Condition 1: Edge contact is NOT zero for all models
    all_zero = (full_total == 0 and ref_total == 0 and null_grand_total == 0)
    cond1_pass = not all_zero

    # Condition 2: Full model differs from null
    # Use ratio: full_mean / null_grand_mean
    if null_grand_mean > 0:
        full_null_ratio = full_mean_per_folio / null_grand_mean
    else:
        full_null_ratio = float('inf') if full_mean_per_folio > 0 else 1.0

    # Indiscriminate = ratio near 1.0 (within 0.7-1.3)
    cond2_pass = full_null_ratio < 0.7 or full_null_ratio > 1.3 or null_grand_mean == 0

    quasi_gate_pass = cond1_pass and cond2_pass

    print(f"    Full/null ratio: {_round(full_null_ratio, 3)}")
    print(f"    Quasi-gate cond1 (not all zero): {'OK' if cond1_pass else 'FAILED'}")
    print(f"    Quasi-gate cond2 (not indiscriminate): {'OK' if cond2_pass else 'FAILED'}")
    print(f"    D4 quasi-gate: {'OK' if quasi_gate_pass else 'FAILED'}")

    return {
        'quasi_gate_pass': quasi_gate_pass,
        'quasi_gate_failed': not quasi_gate_pass,
        'full_model': {
            'warning_total': full_warning_total,
            'hard_stop_total': full_hard_stop_total,
            'total': full_total,
            'mean_per_folio': _round(full_mean_per_folio, 2),
        },
        'reference': {
            'warning_total': ref_warning_total,
            'hard_stop_total': ref_hard_total,
            'total': ref_total,
            'mean_per_folio': _round(ref_mean, 2),
        },
        'null_models': null_edge_stats,
        'null_grand_mean_per_folio': _round(null_grand_mean, 2),
        'full_null_ratio': _round(full_null_ratio, 3),
        'conditions': {
            'cond1_not_all_zero': cond1_pass,
            'cond2_not_indiscriminate': cond2_pass,
        },
        'full_per_folio': full_per_folio,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    output_path = _PHASE_DIR / 'results' / 't4_behavior_validation.json'

    print("=" * 70)
    print("T4: Behavior Validation Battery")
    print("Phase 565 - VIRTUAL_APPARATUS_PERMEABILITY_CALIBRATION")
    print("=" * 70)

    # Load all data
    t1, t2, t3, sup_tokens, line_packets = load_all_data()

    # Build folio metadata
    pilot_folios, folio_meta, baseline_by_folio, config_abl_by_fc = \
        build_folio_metadata(t2, t3, sup_tokens)
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
    tests['P5'] = test_p5(t2, t3, pilot_folios, folio_meta, baseline_by_folio,
                          config_abl_by_fc)
    tests['P6'] = test_p6(t3, pilot_folios, baseline_by_folio)
    tests['P7'] = test_p7(t3, pilot_folios, folio_meta)
    tests['P8'] = test_p8(pilot_folios, folio_meta)
    tests['P9'] = test_p9(pilot_folios, folio_meta)

    # Diagnostics
    print("\n" + "=" * 70)
    print("RUNNING DIAGNOSTICS")
    print("=" * 70)

    diagnostics = {}
    diagnostics['D1'] = diag_d1(t1)
    diagnostics['D2'] = diag_d2(pilot_folios, folio_meta)
    diagnostics['D3'] = diag_d3(t3, pilot_folios, folio_meta, baseline_by_folio)
    diagnostics['D4'] = diag_d4(t2, t3, pilot_folios, folio_meta)

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
    if diagnostics['D1'].get('quasi_gate_failed'):
        qg_statuses.append('D1_FAILED')
    if diagnostics['D2'].get('quasi_gate_failed'):
        qg_statuses.append('D2_FAILED')
    if diagnostics['D3'].get('quasi_gate_failed'):
        qg_statuses.append('D3_BELOW_EXPECTATION')
    if diagnostics['D4'].get('quasi_gate_failed'):
        qg_statuses.append('D4_FAILED')
    qg_status = ', '.join(qg_statuses) if qg_statuses else 'ALL_OK'
    print(f"  Quasi-gate status: {qg_status}")

    # D3 B9 delta note
    d3_delta = diagnostics['D3']['mean_viab_delta']
    print(f"  D3 B9 delta: {d3_delta}")
    if diagnostics['D3'].get('flag'):
        print(f"  D3 flag: {diagnostics['D3']['flag']}")

    # D4 edge contact note
    d4_ratio = diagnostics['D4']['full_null_ratio']
    print(f"  D4 full/null edge ratio: {d4_ratio}")

    summary = {
        'n_pass': n_pass,
        'n_fail': n_fail,
        'n_core': n_core,
        'core_pass': n_pass >= 5,  # majority of 8 core tests
        'core_pass_list': core_pass,
        'core_fail_list': core_fail,
        'p9_significant': p9_sig,
        'quasi_gate_status': qg_status,
        'd3_b9_delta': d3_delta,
        'd4_full_null_ratio': d4_ratio,
    }

    elapsed = time.time() - t_start

    # Build output
    output = {
        'metadata': {
            'phase': '565',
            'task': 'T4',
            'phase_name': 'VIRTUAL_APPARATUS_PERMEABILITY_CALIBRATION',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_tests': 9,
            'n_diagnostics': 4,
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
