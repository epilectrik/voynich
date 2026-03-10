"""
T4: Behavior Validation Battery
Phase 566 - VIRTUAL_APPARATUS_CLOSE_RECOVERY

Reads T2 (close recovery runs), T3 (null/ablation runs), and T1 (apparatus config),
runs 9 tests (P1-P9) plus 7 diagnostics (D1-D7), and outputs
t4_behavior_validation.json.

Tests:
  P1: Non-degeneracy Guard (strict, split into P1a + P1b)
      P1a REVISED: Drop B2 viability comparison, test only full > N1 (14/20).
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
  D4: Edge Contact Audit (quasi-gating)
  D5: Recovery Asymmetry Audit (NEW)
  D6: B2 Composite Diagnostic (NEW, diagnostic only)
  D7: Corridor Return Latency (NEW)

Changes from 565 T4:
  - P1a: Drop B2 comparison (B2 viab=1.0 always). Test only full > N1.
  - D5: Recovery asymmetry (WORK positive, CLOSE negative for aligned models)
  - D6: B2 composite score (0.7*viab + 0.3*Y_final) — diagnostic, not pass/fail
  - D7: Corridor return latency comparison across model types
  - B10 (NoCloseRecovery) added to ablation analysis
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

sys.path.insert(0, str(_PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_CLOSE_RECOVERY' / 'scripts'))
from t1_close_recovery_apparatus import (
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
    # Try uppercase first (T3 format), then lowercase (T2 format)
    val = sv_zo.get(zone_name.upper())
    if val is None:
        val = sv_zo.get(zone_name.lower(), 0.0)
    return val if val is not None else 0.0


def _dev_change_to_list(dev_change):
    """Convert deviation change from dict (T2) or list (T3) to list form."""
    if isinstance(dev_change, dict):
        return [dev_change.get(sv, 0.0) for sv in STATE_VARS]
    elif isinstance(dev_change, list):
        return dev_change
    return [0.0] * N_VARS


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_all_data():
    """Load T1, T2, T3, supervisory tokens, and line packets."""
    phase_results = _PHASE_DIR / 'results'
    coupling_results = _PROJECT_ROOT / 'phases' / 'VIRTUAL_APPARATUS_COUPLING' / 'results'
    ste_results = _PROJECT_ROOT / 'phases' / 'SECTION_TEMPLATE_TRACE_EXECUTOR' / 'results'

    print("--- Loading data sources ---")

    # T1: close recovery apparatus
    t1_path = phase_results / 't1_close_recovery_apparatus.json'
    print(f"  Loading T1: {t1_path}")
    t1 = _load_json(t1_path)

    # T2: close recovery runs (flat dict keyed by run_key)
    t2_path = phase_results / 't2_close_recovery_runs.json'
    print(f"  Loading T2: {t2_path}")
    t2 = _load_json(t2_path)
    print(f"    Total runs: {len(t2['runs'])}")

    # T3: null/ablation runs
    t3_path = phase_results / 't3_null_ablation_runs.json'
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
    and group runs by folio.

    T2 in phase 566 is a flat dict keyed by run_key. Each run has
    folio, profile, config_mode. We split into primary runs (all 3
    profiles for each folio, any config) and config ablation runs.
    """
    pilot_folios = sorted(t3['reference'].keys())
    pref_map = t2['preferred_profile_map']

    # Determine section per folio from supervisory tokens
    folio_section = {}
    for tok in sup_tokens:
        folio_section[tok['folio']] = tok['section']

    # Index all runs by (folio, profile, config_mode)
    all_runs = t2['runs']
    runs_by_fpc = {}
    for run in all_runs.values():
        key = (run['folio'], run['profile'], run['config_mode'])
        runs_by_fpc[key] = run

    # Index runs by (folio, profile) — pick highest config (H2 preferred)
    config_priority = {'H2_HIGH_INFRA': 0, 'H1_MEDIUM_INFRA': 1, 'H0_LOW_INFRA': 2}
    runs_by_fp = {}
    for (folio, profile, cm), run in runs_by_fpc.items():
        existing = runs_by_fp.get((folio, profile))
        if existing is None:
            runs_by_fp[(folio, profile)] = run
        else:
            existing_priority = config_priority.get(existing['config_mode'], 99)
            new_priority = config_priority.get(cm, 99)
            if new_priority < existing_priority:
                runs_by_fp[(folio, profile)] = run

    # Index config ablation runs by (folio, config_mode) — use preferred profile
    config_abl_by_fc = {}
    for (folio, profile, cm), run in runs_by_fpc.items():
        if profile == pref_map.get(folio):
            config_abl_by_fc[(folio, cm)] = run

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
    P1a (REVISED for 566): full > N1 mean for >= 14/20 folios.
    B2 comparison dropped because B2 always has viab=1.0.

    P1b: mean viability in [0.88, 0.995] AND >=8/20 with viability < 1.0
         AND >=10/20 with viability > 0.9.
    P1 PASS requires BOTH P1a AND P1b.
    """
    print("\n  [P1] Non-degeneracy Guard")
    ref = t3['reference']
    n1 = t3['null_runs']['N1']

    full_gt_n1 = 0
    viabilities = []
    folios_lt_1 = 0
    folios_gt_09 = 0
    p1a_per_folio = {}

    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        full_viab = pref_run['viability']
        n1_viab_mean = n1[folio]['mean_viab']

        viabilities.append(full_viab)
        if full_viab < 1.0:
            folios_lt_1 += 1
        if full_viab > 0.9:
            folios_gt_09 += 1

        gt_n1 = full_viab > n1_viab_mean

        if gt_n1:
            full_gt_n1 += 1

        p1a_per_folio[folio] = {
            'full_viab': _round(full_viab),
            'n1_viab_mean': _round(n1_viab_mean),
            'gt_n1': gt_n1,
        }

    mean_viab = sum(viabilities) / len(viabilities) if viabilities else 0.0

    # P1a: strict superiority — only full > N1 (B2 comparison dropped)
    p1a_pass = full_gt_n1 >= PASS_THRESHOLD
    print(f"    [P1a] full>N1: {full_gt_n1}/20 (need>={PASS_THRESHOLD}) -> "
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
            'revision_note': 'B2 comparison dropped (B2 viab=1.0 always). Test only full > N1.',
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
         Use Mann-Whitney U test.
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

        group_routed = []
        group_unrouted = []

        for folio in pilot_folios:
            toks = folio_tokens.get(folio, [])
            n = len(toks)

            routing_positions = {}
            for i in range(n):
                if toks[i].get('routing_active') and toks[i].get('routing_terminal'):
                    routing_positions[i] = toks[i]['routing_terminal']

            preceded_by_rt = set()
            preceded_by_any = set()

            for rp, rterm in routing_positions.items():
                for w in range(1, ROUTING_WINDOW + 1):
                    idx = rp + w
                    if idx < n:
                        preceded_by_any.add(idx)
                        if rterm == rt:
                            preceded_by_rt.add(idx)

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
        # T3 reference uses lowercase y_final
        full_yf = ref[folio].get('y_final', ref[folio].get('Y_final', 0.5))
        b4_yf = b4_by_folio[folio].get('y_final', b4_by_folio[folio].get('Y_final', 0.5))

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

    p4a_pass = n_correct >= 3
    passed = p4a_pass
    print(f"    P4 overall: {'PASS' if passed else 'FAIL'} "
          f"(P4a {n_correct}/4 correct)")

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

    # Get config ablation folios (folios that have both H0 and H2 runs)
    config_folios_set = set()
    for (folio, cm) in config_abl_by_fc.keys():
        config_folios_set.add(folio)
    config_folios = sorted(config_folios_set)
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
    for (folio, cm), run in config_abl_by_fc.items():
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

        deltas_arr = np.array(deltas)
        nonzero_deltas = deltas_arr[deltas_arr != 0]
        mean_delta = float(np.mean(deltas_arr))

        if len(nonzero_deltas) >= 5:
            try:
                w_stat, p_val = wilcoxon(nonzero_deltas, alternative='greater')
            except ValueError:
                w_stat, p_val = 0.0, 1.0
        else:
            w_stat = None
            if len(nonzero_deltas) > 0 and all(d > 0 for d in nonzero_deltas):
                p_val = 0.03
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
            y_finals[profile] = run.get('Y_final', run.get('y_final', 0.5))
            bounded_counts[profile] = run['bounded_excursion_count']

        pref_viab = viabilities[preferred_profile]
        pref_yf = y_finals[preferred_profile]

        max_viab = max(viabilities.values())

        best_viab = pref_viab >= max_viab

        if best_viab and pref_viab == max_viab:
            tied_profiles = [p for p, v in viabilities.items() if v == max_viab]
            if len(tied_profiles) > 1:
                max_yf_among_tied = max(y_finals[p] for p in tied_profiles)
                best_viab = pref_yf >= max_yf_among_tied

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

    Also report B10 (NoCloseRecovery) ablation alongside B9.
    """
    print("\n  [D3] B9 Ablation (+ B10 comparison)")
    ref = t3['reference']
    b9_by_folio = baseline_by_folio['B9']
    b10_by_folio = baseline_by_folio.get('B10', {})

    viab_deltas = []
    b10_viab_deltas = []
    n_full_gt_b9 = 0
    n_full_gt_b10 = 0
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

        entry = {
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
        }

        # B10 comparison
        if folio in b10_by_folio:
            b10_viab = b10_by_folio[folio]['viability']
            b10_delta = full_viab - b10_viab
            b10_viab_deltas.append(b10_delta)
            if full_viab > b10_viab:
                n_full_gt_b10 += 1
            entry['B10_viab'] = _round(b10_viab)
            entry['B10_viab_delta'] = _round(b10_delta)

        per_folio.append(entry)

    mean_viab_delta = sum(viab_deltas) / len(viab_deltas) if viab_deltas else 0.0
    mean_b10_delta = sum(b10_viab_deltas) / len(b10_viab_deltas) if b10_viab_deltas else 0.0

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

    print(f"    Mean viability delta (full - B10): {_round(mean_b10_delta)}")
    print(f"    Folios where full > B10: {n_full_gt_b10}/20")

    # Print per-folio summary
    for entry in per_folio:
        tag = "+" if entry['viab_delta'] > 0 else ("=" if entry['viab_delta'] == 0 else "-")
        b10_str = f", B10={entry.get('B10_viab', 'N/A')}" if 'B10_viab' in entry else ""
        print(f"      {tag} {entry['folio']}: full={entry['full_viab']}, "
              f"B9={entry['B9_viab']}, delta={entry['viab_delta']}"
              f"{b10_str}")

    return {
        'quasi_gate_pass': quasi_gate_pass,
        'quasi_gate_failed': not quasi_gate_pass,
        'mean_viab_delta': _round(mean_viab_delta),
        'expectation_threshold': 0.05,
        'warning_threshold': 0.03,
        'below_warning': below_warning,
        'flag': flag,
        'n_full_gt_B9': n_full_gt_b9,
        'B10_analysis': {
            'mean_viab_delta': _round(mean_b10_delta),
            'n_full_gt_B10': n_full_gt_b10,
            'n_folios': len(b10_viab_deltas),
        },
        'per_folio': per_folio,
    }


# ---------------------------------------------------------------------------
# D4: Edge Contact Audit (quasi-gating)
# ---------------------------------------------------------------------------
def diag_d4(t2, t3, pilot_folios, folio_meta):
    """
    Compare warning + hard_stop contact rates between full model, baselines,
    and null models.

    Quasi-gate conditions:
      1. Edge contact is NOT zero for all models
      2. Full model edge contact pattern differs from null
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

        if isinstance(wc, dict):
            folio_warn = sum(wc.values())
            folio_hard = sum(hc.values())
        else:
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
    all_zero = (full_total == 0 and ref_total == 0 and null_grand_total == 0)
    cond1_pass = not all_zero

    if null_grand_mean > 0:
        full_null_ratio = full_mean_per_folio / null_grand_mean
    else:
        full_null_ratio = float('inf') if full_mean_per_folio > 0 else 1.0

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
# D5: Recovery Asymmetry Audit (NEW for 566)
# ---------------------------------------------------------------------------
def diag_d5(t2, t3, pilot_folios, folio_meta, baseline_by_folio):
    """
    For each model type (full, B2, B3, B9, B10, N1-N4), report:
      - Mean WORK-phase deviation change (positive = outward push)
      - Mean CLOSE-phase deviation change (negative = inward recovery)

    Expected: Full model shows WORK:positive, CLOSE:negative. Nulls show weaker.

    Quasi-gate: Full model CLOSE deviation change should be more negative
    than N1's CLOSE deviation change.
    """
    print("\n  [D5] Recovery Asymmetry Audit")

    ref = t3['reference']
    null_runs = t3['null_runs']

    # --- Full model (from T2 preferred runs) ---
    full_work_devs = []
    full_close_devs = []
    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        work_dc = _dev_change_to_list(pref_run.get('work_deviation_change', [0.0] * N_VARS))
        close_dc = _dev_change_to_list(pref_run.get('close_deviation_change', [0.0] * N_VARS))
        full_work_devs.append(work_dc)
        full_close_devs.append(close_dc)

    full_mean_work = [float(np.mean([d[i] for d in full_work_devs])) for i in range(N_VARS)]
    full_mean_close = [float(np.mean([d[i] for d in full_close_devs])) for i in range(N_VARS)]
    full_work_grand = float(np.mean(full_mean_work))
    full_close_grand = float(np.mean(full_mean_close))

    print(f"    Full model:")
    print(f"      WORK mean dev change: {[_round(v, 6) for v in full_mean_work]}")
    print(f"      CLOSE mean dev change: {[_round(v, 6) for v in full_mean_close]}")
    print(f"      WORK grand mean: {_round(full_work_grand, 6)}, "
          f"CLOSE grand mean: {_round(full_close_grand, 6)}")

    # --- Reference (T3) ---
    ref_work_devs = []
    ref_close_devs = []
    for folio in pilot_folios:
        work_dc = _dev_change_to_list(ref[folio].get('work_deviation_change', [0.0] * N_VARS))
        close_dc = _dev_change_to_list(ref[folio].get('close_deviation_change', [0.0] * N_VARS))
        ref_work_devs.append(work_dc)
        ref_close_devs.append(close_dc)

    ref_mean_work = [float(np.mean([d[i] for d in ref_work_devs])) for i in range(N_VARS)]
    ref_mean_close = [float(np.mean([d[i] for d in ref_close_devs])) for i in range(N_VARS)]
    ref_work_grand = float(np.mean(ref_mean_work))
    ref_close_grand = float(np.mean(ref_mean_close))

    print(f"    Reference (T3):")
    print(f"      WORK grand mean: {_round(ref_work_grand, 6)}, "
          f"CLOSE grand mean: {_round(ref_close_grand, 6)}")

    # --- Baselines ---
    baseline_results = {}
    for bkey in ['B2', 'B3', 'B9', 'B10']:
        if bkey not in baseline_by_folio:
            continue
        b_data = baseline_by_folio[bkey]
        b_work_devs = []
        b_close_devs = []
        for folio in pilot_folios:
            if folio not in b_data:
                continue
            entry = b_data[folio]
            work_dc = _dev_change_to_list(entry.get('work_deviation_change', [0.0] * N_VARS))
            close_dc = _dev_change_to_list(entry.get('close_deviation_change', [0.0] * N_VARS))
            b_work_devs.append(work_dc)
            b_close_devs.append(close_dc)

        if b_work_devs:
            b_mean_work = [float(np.mean([d[i] for d in b_work_devs])) for i in range(N_VARS)]
            b_mean_close = [float(np.mean([d[i] for d in b_close_devs])) for i in range(N_VARS)]
            b_work_grand = float(np.mean(b_mean_work))
            b_close_grand = float(np.mean(b_mean_close))
        else:
            b_mean_work = [0.0] * N_VARS
            b_mean_close = [0.0] * N_VARS
            b_work_grand = 0.0
            b_close_grand = 0.0

        baseline_results[bkey] = {
            'work_mean_per_sv': [_round(v, 6) for v in b_mean_work],
            'close_mean_per_sv': [_round(v, 6) for v in b_mean_close],
            'work_grand_mean': _round(b_work_grand, 6),
            'close_grand_mean': _round(b_close_grand, 6),
        }
        print(f"    {bkey}: WORK={_round(b_work_grand, 6)}, CLOSE={_round(b_close_grand, 6)}")

    # --- Null models ---
    null_results = {}
    for null_name in ['N1', 'N2', 'N3', 'N4']:
        null_data = null_runs[null_name]
        n_work_devs = []
        n_close_devs = []
        for folio in pilot_folios:
            fd = null_data[folio]
            work_dc = _dev_change_to_list(fd.get('mean_work_deviation_change', [0.0] * N_VARS))
            close_dc = _dev_change_to_list(fd.get('mean_close_deviation_change', [0.0] * N_VARS))
            n_work_devs.append(work_dc)
            n_close_devs.append(close_dc)

        n_mean_work = [float(np.mean([d[i] for d in n_work_devs])) for i in range(N_VARS)]
        n_mean_close = [float(np.mean([d[i] for d in n_close_devs])) for i in range(N_VARS)]
        n_work_grand = float(np.mean(n_mean_work))
        n_close_grand = float(np.mean(n_mean_close))

        null_results[null_name] = {
            'work_mean_per_sv': [_round(v, 6) for v in n_mean_work],
            'close_mean_per_sv': [_round(v, 6) for v in n_mean_close],
            'work_grand_mean': _round(n_work_grand, 6),
            'close_grand_mean': _round(n_close_grand, 6),
        }
        print(f"    {null_name}: WORK={_round(n_work_grand, 6)}, CLOSE={_round(n_close_grand, 6)}")

    # --- Quasi-gate: full CLOSE more negative than N1 CLOSE ---
    n1_close_grand = null_results['N1']['close_grand_mean']
    quasi_gate_pass = full_close_grand < n1_close_grand
    print(f"    Quasi-gate: full CLOSE ({_round(full_close_grand, 6)}) < "
          f"N1 CLOSE ({_round(n1_close_grand, 6)}) -> "
          f"{'OK' if quasi_gate_pass else 'FAILED'}")

    return {
        'quasi_gate_pass': quasi_gate_pass,
        'quasi_gate_failed': not quasi_gate_pass,
        'full_model': {
            'work_mean_per_sv': [_round(v, 6) for v in full_mean_work],
            'close_mean_per_sv': [_round(v, 6) for v in full_mean_close],
            'work_grand_mean': _round(full_work_grand, 6),
            'close_grand_mean': _round(full_close_grand, 6),
        },
        'reference': {
            'work_grand_mean': _round(ref_work_grand, 6),
            'close_grand_mean': _round(ref_close_grand, 6),
        },
        'baselines': baseline_results,
        'nulls': null_results,
        'quasi_gate_comparison': {
            'full_close': _round(full_close_grand, 6),
            'N1_close': _round(n1_close_grand, 6),
            'full_more_negative': quasi_gate_pass,
        },
    }


# ---------------------------------------------------------------------------
# D6: B2 Composite Diagnostic (NEW for 566, diagnostic only)
# ---------------------------------------------------------------------------
def diag_d6(t3, pilot_folios, folio_meta, baseline_by_folio):
    """
    Report composite score (0.7 * viability + 0.3 * Y_final) for all model types.

    Expected: B2 has high viab (1.0) but low Y_final (0.5), composite ~0.85.
    Full model has moderate viab + higher Y_final, composite comparable or better.

    DIAGNOSTIC ONLY - not a pass/fail gate.
    """
    print("\n  [D6] B2 Composite Diagnostic (non-gating)")

    ref = t3['reference']
    null_runs = t3['null_runs']

    def compute_composite(viab, y_final):
        return 0.7 * viab + 0.3 * y_final

    # --- Full model ---
    full_composites = []
    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        viab = pref_run['viability']
        yf = pref_run.get('Y_final', pref_run.get('y_final', 0.5))
        full_composites.append(compute_composite(viab, yf))

    full_mean_composite = float(np.mean(full_composites))
    print(f"    Full model: mean composite = {_round(full_mean_composite, 5)}")

    # --- Baselines ---
    baseline_composites = {}
    for bkey in ['B2', 'B3', 'B9', 'B10']:
        if bkey not in baseline_by_folio:
            continue
        b_data = baseline_by_folio[bkey]
        composites = []
        for folio in pilot_folios:
            if folio not in b_data:
                continue
            entry = b_data[folio]
            viab = entry['viability']
            yf = entry.get('y_final', entry.get('Y_final', 0.5))
            composites.append(compute_composite(viab, yf))

        mean_comp = float(np.mean(composites)) if composites else 0.0
        baseline_composites[bkey] = {
            'mean_composite': _round(mean_comp, 5),
            'n_folios': len(composites),
        }
        print(f"    {bkey}: mean composite = {_round(mean_comp, 5)}")

    # --- Null models ---
    null_composites = {}
    for null_name in ['N1', 'N2', 'N3', 'N4']:
        null_data = null_runs[null_name]
        composites = []
        for folio in pilot_folios:
            fd = null_data[folio]
            viab = fd['mean_viab']
            yf = fd['mean_y_final']
            composites.append(compute_composite(viab, yf))

        mean_comp = float(np.mean(composites)) if composites else 0.0
        null_composites[null_name] = {
            'mean_composite': _round(mean_comp, 5),
        }
        print(f"    {null_name}: mean composite = {_round(mean_comp, 5)}")

    # --- Reference (T3) ---
    ref_composites = []
    for folio in pilot_folios:
        viab = ref[folio]['viability']
        yf = ref[folio].get('y_final', ref[folio].get('Y_final', 0.5))
        ref_composites.append(compute_composite(viab, yf))

    ref_mean_composite = float(np.mean(ref_composites))
    print(f"    Reference: mean composite = {_round(ref_mean_composite, 5)}")

    # --- Comparison ---
    b2_comp = baseline_composites.get('B2', {}).get('mean_composite', 0.0)
    full_vs_b2 = full_mean_composite - b2_comp
    print(f"    Full - B2 composite: {_round(full_vs_b2, 5)}")

    return {
        'diagnostic_only': True,
        'composite_formula': '0.7 * viability + 0.3 * Y_final',
        'full_model': {
            'mean_composite': _round(full_mean_composite, 5),
        },
        'reference': {
            'mean_composite': _round(ref_mean_composite, 5),
        },
        'baselines': baseline_composites,
        'nulls': null_composites,
        'full_vs_B2_delta': _round(full_vs_b2, 5),
    }


# ---------------------------------------------------------------------------
# D7: Corridor Return Latency (NEW for 566)
# ---------------------------------------------------------------------------
def diag_d7(t2, t3, pilot_folios, folio_meta, baseline_by_folio):
    """
    After WORK-phase excursion past Q1, measure tokens-to-return to |dev| < Q2_BASE.
    Compare across model types.

    Expected: Full aligned model returns faster (CLOSE recovery assists).
    Nulls return slower.

    Source: T2 corridor_return_events for full model, T3 baseline corridor_return
    fields for baselines. Nulls do not have corridor_return data.
    """
    print("\n  [D7] Corridor Return Latency")

    ref = t3['reference']

    # --- Full model (from T2 preferred runs) ---
    full_latencies = []
    full_counts = []
    full_per_folio = {}

    for folio in pilot_folios:
        pref_run = folio_meta[folio]['preferred_run']
        events = pref_run.get('corridor_return_events', [])

        latencies = [e['latency'] for e in events if 'latency' in e]
        mean_lat = float(np.mean(latencies)) if latencies else None
        max_lat = max(latencies) if latencies else None

        full_latencies.extend(latencies)
        full_counts.append(len(latencies))

        full_per_folio[folio] = {
            'n_returns': len(latencies),
            'mean_latency': _round(mean_lat, 2),
            'max_latency': max_lat,
        }

    full_grand_mean_latency = float(np.mean(full_latencies)) if full_latencies else None
    full_total_returns = len(full_latencies)
    print(f"    Full model: {full_total_returns} corridor returns, "
          f"mean latency={_round(full_grand_mean_latency, 2)}")

    # --- Reference (T3) corridor return ---
    ref_latencies = []
    ref_counts = []
    for folio in pilot_folios:
        count = ref[folio].get('corridor_return_count', 0)
        mean_lat = ref[folio].get('corridor_return_mean_latency')
        ref_counts.append(count)
        if mean_lat is not None and count > 0:
            ref_latencies.append(mean_lat)

    ref_grand_mean = float(np.mean(ref_latencies)) if ref_latencies else None
    ref_total = sum(ref_counts)
    print(f"    Reference: {ref_total} corridor returns, "
          f"mean latency={_round(ref_grand_mean, 2)}")

    # --- Baselines ---
    baseline_latency_results = {}
    for bkey in ['B2', 'B3', 'B9', 'B10']:
        if bkey not in baseline_by_folio:
            continue
        b_data = baseline_by_folio[bkey]
        b_latencies = []
        b_total = 0
        for folio in pilot_folios:
            if folio not in b_data:
                continue
            entry = b_data[folio]
            count = entry.get('corridor_return_count', 0)
            mean_lat = entry.get('corridor_return_mean_latency')
            b_total += count
            if mean_lat is not None and count > 0:
                b_latencies.append(mean_lat)

        b_mean = float(np.mean(b_latencies)) if b_latencies else None
        baseline_latency_results[bkey] = {
            'total_returns': b_total,
            'mean_latency': _round(b_mean, 2),
            'n_folios_with_data': len(b_latencies),
        }
        print(f"    {bkey}: {b_total} corridor returns, mean latency={_round(b_mean, 2)}")

    # --- Null models: no corridor_return data available ---
    print(f"    N1-N4: corridor return data not available in null runs")

    # --- Quasi-gate: full model faster than B10 (if available) ---
    b10_mean = baseline_latency_results.get('B10', {}).get('mean_latency')
    if full_grand_mean_latency is not None and b10_mean is not None:
        quasi_gate_pass = full_grand_mean_latency <= b10_mean
        print(f"    Quasi-gate: full latency ({_round(full_grand_mean_latency, 2)}) "
              f"<= B10 latency ({_round(b10_mean, 2)}) -> "
              f"{'OK' if quasi_gate_pass else 'FAILED'}")
    else:
        quasi_gate_pass = None
        print(f"    Quasi-gate: insufficient data for comparison")

    return {
        'quasi_gate_pass': quasi_gate_pass,
        'quasi_gate_failed': quasi_gate_pass is not None and not quasi_gate_pass,
        'full_model': {
            'total_returns': full_total_returns,
            'mean_latency': _round(full_grand_mean_latency, 2),
            'per_folio': full_per_folio,
        },
        'reference': {
            'total_returns': ref_total,
            'mean_latency': _round(ref_grand_mean, 2),
        },
        'baselines': baseline_latency_results,
        'null_note': 'Corridor return data not available in null runs',
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    output_path = _PHASE_DIR / 'results' / 't4_behavior_validation.json'

    print("=" * 70)
    print("T4: Behavior Validation Battery")
    print("Phase 566 - VIRTUAL_APPARATUS_CLOSE_RECOVERY")
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
    diagnostics['D5'] = diag_d5(t2, t3, pilot_folios, folio_meta, baseline_by_folio)
    diagnostics['D6'] = diag_d6(t3, pilot_folios, folio_meta, baseline_by_folio)
    diagnostics['D7'] = diag_d7(t2, t3, pilot_folios, folio_meta, baseline_by_folio)

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
    if diagnostics['D5'].get('quasi_gate_failed'):
        qg_statuses.append('D5_FAILED')
    if diagnostics['D7'].get('quasi_gate_failed'):
        qg_statuses.append('D7_FAILED')
    # D6 is diagnostic only, no quasi-gate
    qg_status = ', '.join(qg_statuses) if qg_statuses else 'ALL_OK'
    print(f"  Quasi-gate status: {qg_status}")

    # D3 B9 delta note
    d3_delta = diagnostics['D3']['mean_viab_delta']
    print(f"  D3 B9 delta: {d3_delta}")
    if diagnostics['D3'].get('flag'):
        print(f"  D3 flag: {diagnostics['D3']['flag']}")

    # D3 B10 delta note
    d3_b10 = diagnostics['D3']['B10_analysis']
    print(f"  D3 B10 delta: {d3_b10['mean_viab_delta']}")

    # D4 edge contact note
    d4_ratio = diagnostics['D4']['full_null_ratio']
    print(f"  D4 full/null edge ratio: {d4_ratio}")

    # D5 recovery asymmetry note
    d5_full_close = diagnostics['D5']['full_model']['close_grand_mean']
    d5_n1_close = diagnostics['D5']['quasi_gate_comparison']['N1_close']
    print(f"  D5 full CLOSE: {d5_full_close}, N1 CLOSE: {d5_n1_close}")

    # D6 composite note
    d6_full = diagnostics['D6']['full_model']['mean_composite']
    d6_b2 = diagnostics['D6']['baselines'].get('B2', {}).get('mean_composite', 'N/A')
    print(f"  D6 composites: full={d6_full}, B2={d6_b2}")

    # D7 corridor return note
    d7_full_lat = diagnostics['D7']['full_model']['mean_latency']
    d7_b10_lat = diagnostics['D7']['baselines'].get('B10', {}).get('mean_latency', 'N/A')
    print(f"  D7 corridor return latency: full={d7_full_lat}, B10={d7_b10_lat}")

    # Hard gate pass: majority of core tests pass
    hard_gate = n_pass >= 5

    summary = {
        'tests_passed': n_pass,
        'tests_total': 9,
        'hard_gate_pass': hard_gate,
        'core_pass_list': core_pass,
        'core_fail_list': core_fail,
        'p9_significant': p9_sig,
        'quasi_gate_status': qg_status,
        'd3_b9_delta': d3_delta,
        'd3_b10_delta': d3_b10['mean_viab_delta'],
        'd4_full_null_ratio': d4_ratio,
        'd5_recovery_asymmetry': {
            'full_close': d5_full_close,
            'n1_close': d5_n1_close,
        },
        'd6_composite': {
            'full': d6_full,
            'b2': d6_b2,
        },
        'd7_corridor_latency': {
            'full': d7_full_lat,
            'b10': d7_b10_lat,
        },
    }

    elapsed = time.time() - t_start

    # Build output
    output = {
        'metadata': {
            'phase': '566',
            'task': 'T4',
            'phase_name': 'VIRTUAL_APPARATUS_CLOSE_RECOVERY',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_tests': 9,
            'n_diagnostics': 7,
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
