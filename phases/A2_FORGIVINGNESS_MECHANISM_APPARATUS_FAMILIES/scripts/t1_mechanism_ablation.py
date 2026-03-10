"""
T1: Counterfactual Mechanism Ablation
Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES

For each CLOSE event, re-runs the simulation with specific physics channels
removed.  The difference between full and ablated DYE gives the causal
contribution of each channel to forgivingness.

Five ablation conditions:
  NO_CROSS_COUPLING     : all alpha_* = 0 (removes inter-SV coupling)
  NO_CLOSE_RECOVERY     : R1-R5 disabled  (removes CLOSE recovery channels)
  NO_CONTAINMENT        : alpha_XC=0, alpha_FC=0, R1-C=0, R3=0
  NO_TR_TO_Y            : alpha_FY = 0    (removes TR->Y flow)
  NO_Y_SENSITIVITY      : sensitivity_Y=0 (removes direct Y token push)

Also computes non-ablation diagnostics:
  CRR : Containment-Retained Displacement (C/X/TR subspace retention)
  NRI : Null Recapture Index (Y-gain per unit pre-existing displacement)
"""

import json
import sys
import os
import copy
import time
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from phases.DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR.scripts.t1_enhanced_event_trace import (
    run_enhanced_event_trace,
    FolioSpecificApparatus,
    sort_key,
    assign_folio_profiles, compute_infra_scores,
    STATE_VARS, N_VARS, EQUILIBRIUM,
)
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    build_demand_matched_assignments,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')

ABLATION_NAMES = [
    'NO_CROSS_COUPLING',
    'NO_CLOSE_RECOVERY',
    'NO_CONTAINMENT',
    'NO_TR_TO_Y',
    'NO_Y_SENSITIVITY',
]

N_NULL_PERMS = 5  # Fewer than Phase 572's 20, sufficient for ablation comparison

SV_INDEX = {sv: i for i, sv in enumerate(STATE_VARS)}
CONTAINMENT_SVS = ['C', 'X', 'TR']  # Subspace for CRR
PROCESS_SVS = ['T', 'RC', 'S', 'C', 'TR', 'X']  # For NRI denominator


# ---------------------------------------------------------------------------
# Ablation factory
# ---------------------------------------------------------------------------
def create_ablated_apparatus(apparatus, ablation_name):
    """Create a deep copy with specific channel ablated."""
    app = copy.deepcopy(apparatus)

    if ablation_name == 'NO_CROSS_COUPLING':
        for key in list(app.profile_params.keys()):
            if key.startswith('alpha_'):
                app.profile_params[key] = 0.0
        # Re-compute equil bias with zeroed cross-coupling
        equil_state = [EQUILIBRIUM] * N_VARS
        for phase in ['SPEC', 'WORK', 'CLOSE']:
            cc_eq = app._cross_coupling(equil_state, phase)
            app.equil_bias[phase] = list(cc_eq)

    elif ablation_name == 'NO_CLOSE_RECOVERY':
        app.enable_close_recovery = False

    elif ablation_name == 'NO_CONTAINMENT':
        # Zero containment cross-coupling
        app.profile_params['alpha_XC'] = 0.0
        app.profile_params['alpha_FC'] = 0.0
        # Zero R1-C drawdown
        if hasattr(app, 'k_close'):
            app.k_close['C'] = 0.0
        # Zero R3 containment-TR relief
        app.k_relief_close = 0.0
        # Re-compute equil bias
        equil_state = [EQUILIBRIUM] * N_VARS
        for phase in ['SPEC', 'WORK', 'CLOSE']:
            cc_eq = app._cross_coupling(equil_state, phase)
            app.equil_bias[phase] = list(cc_eq)

    elif ablation_name == 'NO_TR_TO_Y':
        app.profile_params['alpha_FY'] = 0.0
        equil_state = [EQUILIBRIUM] * N_VARS
        for phase in ['SPEC', 'WORK', 'CLOSE']:
            cc_eq = app._cross_coupling(equil_state, phase)
            app.equil_bias[phase] = list(cc_eq)

    elif ablation_name == 'NO_Y_SENSITIVITY':
        app.sensitivities['Y'] = 0.0

    return app


# ---------------------------------------------------------------------------
# Metric computation from stored event data
# ---------------------------------------------------------------------------
def compute_crr(close_pre_state, line_end_state):
    """Containment-Retained Displacement: C/X/TR displacement at end / entry."""
    entry_disp = sum(abs(close_pre_state[SV_INDEX[sv]] - EQUILIBRIUM)
                     for sv in CONTAINMENT_SVS)
    exit_disp = sum(abs(line_end_state[SV_INDEX[sv]] - EQUILIBRIUM)
                    for sv in CONTAINMENT_SVS)
    if entry_disp < 0.001:
        return 1.0  # No displacement at entry → neutral retention
    return exit_disp / entry_disp


def compute_nri(y_gain_event, close_pre_state):
    """Null Recapture Index: Y gained per unit pre-existing process displacement."""
    process_disp = sum(abs(close_pre_state[SV_INDEX[sv]] - EQUILIBRIUM)
                       for sv in PROCESS_SVS)
    if process_disp < 0.001:
        return 0.0
    return y_gain_event / process_disp


def compute_event_dye(events, min_dv=0.001):
    """Compute mean DYE from list of per_event_detail dicts."""
    dyes = []
    for ev in events:
        dv = ev.get('dv_magnitude_sum', 0.0)
        yg = ev.get('y_gain_event', 0.0)
        if dv > min_dv:
            dyes.append(yg / dv)
    return sum(dyes) / len(dyes) if dyes else 0.0


def select_events(events):
    """Select events using same logic as Phase 572 T5: work_preceded >= 2,
    else demanded >= 2, else all."""
    wp = [e for e in events if 'work_preceded' in e.get('demand_qualifiers', [])]
    if len(wp) >= 2:
        return wp
    dem = [e for e in events if 'demanded' in e.get('demand_qualifiers', [])]
    if len(dem) >= 2:
        return dem
    return events


# ---------------------------------------------------------------------------
# Helpers for null execution
# ---------------------------------------------------------------------------
def override_line_phases(line_packets, shuffled_phases):
    """Create line_packets copy with overridden phases."""
    modified = {}
    for key, lp in line_packets.items():
        if key in shuffled_phases:
            new_lp = dict(lp)
            new_ps = dict(lp.get('packet_state', {}))
            new_ps['packet_phase'] = shuffled_phases[key]
            new_lp['packet_state'] = new_ps
            modified[key] = new_lp
        else:
            modified[key] = lp
    return modified


def build_demand_shuffled_phases(line_states, assignment):
    """Build shuffled_phases dict from a demand-matched assignment."""
    shuffled = {}
    for ls in line_states:
        shuffled[ls['line_key']] = ls['packet_phase']
    for real_idx, matched_idx in assignment:
        real_lk = line_states[real_idx]['line_key']
        matched_lk = line_states[matched_idx]['line_key']
        matched_orig_phase = line_states[matched_idx]['packet_phase']
        shuffled[matched_lk] = 'CLOSE'
        shuffled[real_lk] = matched_orig_phase
    return shuffled


def build_shuffled_event_map(original_event_map, shuffled_phases, line_packets):
    """Build event map for shuffled phases."""
    new_map = {}
    for line_key, phase in shuffled_phases.items():
        if phase == 'CLOSE':
            if line_key in original_event_map:
                new_map[line_key] = original_event_map[line_key]
            else:
                lp = line_packets.get(line_key, {})
                section = lp.get('section', 'B')
                new_map[line_key] = {
                    'packet_types_global': ['E_any'],
                    'packet_types_section': ['E_any'],
                    'has_work_predecessor': False,
                    'work_predecessor_key': None,
                    'section': section,
                    'cts': 0.0, 'mcb': 0.0, 'cob': 0.0, 'q4o': 0.0,
                    'armed': False, 'is_pilot': True,
                }
    # Recalculate work predecessors
    folio_lines = {}
    for lk in shuffled_phases:
        parts = lk.split('|')
        if len(parts) != 2:
            continue
        folio = parts[0]
        lid = parts[1]
        try:
            line_num = int(lid)
            line_frac = 0.0
        except ValueError:
            digits = ''.join(c for c in lid if c.isdigit())
            line_num = int(digits) if digits else 9999
            line_frac = 0.1
        folio_lines.setdefault(folio, []).append((line_num + line_frac, lk))
    for folio, flines in folio_lines.items():
        flines.sort()
        for i, (ln, lk) in enumerate(flines):
            if lk in new_map and shuffled_phases.get(lk) == 'CLOSE':
                if i > 0:
                    prev_lk = flines[i - 1][1]
                    prev_phase = shuffled_phases.get(prev_lk, 'WORK')
                    new_map[lk]['has_work_predecessor'] = (prev_phase == 'WORK')
                else:
                    new_map[lk]['has_work_predecessor'] = False
    return new_map


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_all_data():
    """Load Phase 572 stored data + raw simulation data."""
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')

    # Phase 572 stored results
    print("  Loading Phase 572 T1 setup...")
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json'), 'r', encoding='utf-8') as f:
        t1_setup = json.load(f)

    print("  Loading Phase 572 T2 model runs...")
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json'), 'r', encoding='utf-8') as f:
        t2_runs = json.load(f)

    print("  Loading Phase 572 T3 null runs...")
    with open(os.path.join(P572_RESULTS, 't3_null_runs.json'), 'r', encoding='utf-8') as f:
        t3_nulls = json.load(f)

    # Raw data for re-running simulations
    print("  Loading line packets...")
    lp_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't3_line_packets.json')
    with open(lp_path, 'r', encoding='utf-8') as f:
        lp_raw = json.load(f)
    line_packets = lp_raw['line_packets']

    print("  Loading CTS data...")
    cts_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                            'results', 't7_closure_cts.json')
    with open(cts_path, 'r', encoding='utf-8') as f:
        cts_raw = json.load(f)
    cts_data = {}
    if 'line_cts' in cts_raw:
        for key, val in cts_raw['line_cts'].items():
            cts_data[key] = val.get('cts', 0.0) if isinstance(val, dict) else float(val)
    elif 'cts_scores' in cts_raw:
        for key, val in cts_raw['cts_scores'].items():
            cts_data[key] = (val.get('cts', val.get('score', 0.0))
                             if isinstance(val, dict) else float(val))

    print("  Loading supervisory tokens...")
    sup_path = os.path.join(phases_dir, 'VIRTUAL_APPARATUS_COUPLING',
                            'results', 't2b_supervisory_interface_unrouted.json')
    with open(sup_path, 'r', encoding='utf-8') as f:
        sup_raw = json.load(f)
    all_tokens = sup_raw['token_signals']

    print("  Loading folio budgets...")
    budget_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                               'results', 't2_folio_budgets.json')

    print("  Loading event taxonomy...")
    event_path = os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                              'results', 't1_event_taxonomy.json')
    with open(event_path, 'r', encoding='utf-8') as f:
        event_taxonomy = json.load(f)
    event_map = event_taxonomy['event_map']

    regime_path = os.path.join(PROJECT_ROOT, 'data', 'regime_folio_mapping.json')

    return (t1_setup, t2_runs, t3_nulls,
            line_packets, cts_data, all_tokens, budget_path,
            event_map, regime_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    print("=" * 70)
    print("T1: Counterfactual Mechanism Ablation")
    print("Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")
    (t1_setup, t2_runs, t3_nulls,
     line_packets, cts_data, all_tokens, budget_path,
     event_map, regime_path) = load_all_data()

    eligible_folios = t1_setup['eligible_folios']
    all_folios = t1_setup['all_folios']
    folio_configs = t1_setup['folio_configs']
    primary_runs = t2_runs['primary_runs']
    m0_line_states = t2_runs['m0_line_states']
    null_data = t3_nulls['m4f_demand_matched']

    print(f"  Eligible folios: {len(eligible_folios)}")

    # ---- Setup ----
    print("\n--- Resolving profiles and config modes ---")
    folio_assignments = assign_folio_profiles(regime_path, budget_path)
    folio_infra = compute_infra_scores(all_folios)

    eligible_set = set(eligible_folios)
    tokens_by_folio = {f: [] for f in eligible_set}
    for tok in all_tokens:
        if tok['folio'] in eligible_set:
            tokens_by_folio[tok['folio']].append(tok)
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    # ================================================================
    # STEP 1: Compute CRR and NRI from stored Phase 572 data
    # ================================================================
    print("\n--- Step 1: CRR + NRI from stored data ---")

    baseline_metrics = {}  # folio -> {m1_dye, m4f_dye, crr_m1, crr_m4f, nri_m1, nri_m4f}

    for folio in eligible_folios:
        fc = folio_configs[folio]
        m1_events = primary_runs[folio]['M1']['per_event_detail']
        selected_m1 = select_events(m1_events)

        # M1 baseline DYE
        m1_dye = compute_event_dye(selected_m1)

        # M1 CRR and NRI
        crr_m1_vals = []
        nri_m1_vals = []
        for ev in selected_m1:
            cps = ev.get('close_pre_state', [0.5] * 7)
            les = ev.get('line_end_state', [0.5] * 7)
            crr_m1_vals.append(compute_crr(cps, les))
            nri_m1_vals.append(compute_nri(ev.get('y_gain_event', 0.0), cps))

        # M4f baseline DYE, CRR, NRI (mean over perms)
        null_perms = null_data.get(folio, {}).get('all_perms', [])
        perm_dyes = []
        perm_crrs = []
        perm_nris = []
        for perm in null_perms:
            matched = perm.get('matched_events', [])
            sel = select_events(matched)
            perm_dyes.append(compute_event_dye(sel))
            crrs = []
            nris = []
            for ev in sel:
                cps = ev.get('close_pre_state', [0.5] * 7)
                les = ev.get('line_end_state', [0.5] * 7)
                crrs.append(compute_crr(cps, les))
                nris.append(compute_nri(ev.get('y_gain_event', 0.0), cps))
            perm_crrs.append(sum(crrs) / len(crrs) if crrs else 1.0)
            perm_nris.append(sum(nris) / len(nris) if nris else 0.0)

        baseline_metrics[folio] = {
            'm1_dye': m1_dye,
            'm4f_dye': sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0,
            'crr_m1': sum(crr_m1_vals) / len(crr_m1_vals) if crr_m1_vals else 1.0,
            'crr_m4f': sum(perm_crrs) / len(perm_crrs) if perm_crrs else 1.0,
            'nri_m1': sum(nri_m1_vals) / len(nri_m1_vals) if nri_m1_vals else 0.0,
            'nri_m4f': sum(perm_nris) / len(perm_nris) if perm_nris else 0.0,
            'profile': fc['profile'],
            'section': fc['section'],
        }

    # Print CRR/NRI summary by profile
    for profile in sorted(set(fc['profile'] for fc in folio_configs.values())):
        pf = [v for v in baseline_metrics.values() if v['profile'] == profile]
        if not pf:
            continue
        n = len(pf)
        print(f"  {profile} (n={n}):")
        print(f"    CRR_M1  = {sum(v['crr_m1'] for v in pf)/n:.4f}")
        print(f"    CRR_M4f = {sum(v['crr_m4f'] for v in pf)/n:.4f}")
        print(f"    NRI_M1  = {sum(v['nri_m1'] for v in pf)/n:.4f}")
        print(f"    NRI_M4f = {sum(v['nri_m4f'] for v in pf)/n:.4f}")

    # ================================================================
    # STEP 2: Run ablated M1 simulations
    # ================================================================
    print("\n--- Step 2: Ablated M1 runs ---")

    ablated_m1_dye = {abl: {} for abl in ABLATION_NAMES}
    run_count = 0
    total_m1 = len(eligible_folios) * len(ABLATION_NAMES)

    for folio in eligible_folios:
        fc = folio_configs[folio]
        toks = tokens_by_folio[folio]
        if not toks:
            continue

        profile = fc['profile']
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        f1, f2, f3, f4, f5 = fc['F1'], fc['F2'], fc['F3'], fc['F4_raw'], fc['F5']

        # Build full apparatus
        full_app = FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4, f5)

        for abl_name in ABLATION_NAMES:
            abl_app = create_ablated_apparatus(full_app, abl_name)
            result = run_enhanced_event_trace(abl_app, toks, line_packets,
                                              cts_data, event_map)
            result.pop('line_states', None)
            events = result['per_event_detail']
            selected = select_events(events)
            dye = compute_event_dye(selected)
            ablated_m1_dye[abl_name][folio] = dye

            run_count += 1
            if run_count % 50 == 0:
                print(f"  [{run_count}/{total_m1}] M1 ablation runs...")

    print(f"  M1 ablation runs completed: {run_count}")

    # ================================================================
    # STEP 3: Run ablated M4f null simulations (5 perms)
    # ================================================================
    print(f"\n--- Step 3: Ablated M4f runs ({N_NULL_PERMS} perms) ---")

    ablated_m4f_dye = {abl: {} for abl in ABLATION_NAMES}
    run_count = 0
    total_m4f = len(eligible_folios) * len(ABLATION_NAMES) * N_NULL_PERMS

    for folio in eligible_folios:
        fc = folio_configs[folio]
        toks = tokens_by_folio[folio]
        if not toks:
            continue

        profile = fc['profile']
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        f1, f2, f3, f4, f5 = fc['F1'], fc['F2'], fc['F3'], fc['F4_raw'], fc['F5']

        # Build demand-matched assignments
        line_states = m0_line_states[folio]
        close_indices = [i for i, ls in enumerate(line_states)
                         if ls['packet_phase'] == 'CLOSE']
        assignments = build_demand_matched_assignments(
            line_states, close_indices,
            n_permutations=N_NULL_PERMS, k_neighbors=5, seed=42
        )

        if not assignments:
            for abl_name in ABLATION_NAMES:
                ablated_m4f_dye[abl_name][folio] = 0.0
            continue

        full_app = FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4, f5)

        for abl_name in ABLATION_NAMES:
            abl_app = create_ablated_apparatus(full_app, abl_name)
            perm_dyes = []

            for perm_idx, assignment in enumerate(assignments):
                shuffled_phases = build_demand_shuffled_phases(line_states, assignment)
                shuffled_lp = override_line_phases(line_packets, shuffled_phases)
                shuffled_em = build_shuffled_event_map(event_map, shuffled_phases, line_packets)

                result = run_enhanced_event_trace(abl_app, toks, shuffled_lp,
                                                  cts_data, shuffled_em)
                result.pop('line_states', None)
                events = result['per_event_detail']
                selected = select_events(events)
                perm_dyes.append(compute_event_dye(selected))

                run_count += 1
                if run_count % 200 == 0:
                    print(f"  [{run_count}/{total_m4f}] M4f ablation runs...")

            ablated_m4f_dye[abl_name][folio] = (
                sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0
            )

    print(f"  M4f ablation runs completed: {run_count}")

    # ================================================================
    # STEP 4: Compute ablation effects
    # ================================================================
    print("\n--- Step 4: Computing ablation effects ---")

    # Per-folio ablation effects
    per_folio = {}
    for folio in eligible_folios:
        bm = baseline_metrics[folio]
        folio_effects = {
            'profile': bm['profile'],
            'section': bm['section'],
            'baseline_m1_dye': bm['m1_dye'],
            'baseline_m4f_dye': bm['m4f_dye'],
            'crr_m1': bm['crr_m1'],
            'crr_m4f': bm['crr_m4f'],
            'nri_m1': bm['nri_m1'],
            'nri_m4f': bm['nri_m4f'],
            'ablations': {},
        }

        for abl_name in ABLATION_NAMES:
            abl_m1 = ablated_m1_dye[abl_name].get(folio, bm['m1_dye'])
            abl_m4f = ablated_m4f_dye[abl_name].get(folio, bm['m4f_dye'])

            # Channel contribution to M1 DYE
            delta_m1_dye = bm['m1_dye'] - abl_m1
            # Channel contribution to M4f DYE (= FI)
            delta_m4f_dye = bm['m4f_dye'] - abl_m4f
            # Channel contribution to DYE advantage
            dye_adv_full = bm['m1_dye'] - bm['m4f_dye']
            dye_adv_abl = abl_m1 - abl_m4f
            delta_dye_adv = dye_adv_full - dye_adv_abl

            folio_effects['ablations'][abl_name] = {
                'abl_m1_dye': abl_m1,
                'abl_m4f_dye': abl_m4f,
                'delta_m1_dye': delta_m1_dye,
                'delta_m4f_dye': delta_m4f_dye,
                'delta_dye_advantage': delta_dye_adv,
            }

        per_folio[folio] = folio_effects

    # Per-profile summary
    profile_summary = {}
    profiles_seen = set()
    for folio, fe in per_folio.items():
        p = fe['profile']
        profiles_seen.add(p)
        if p not in profile_summary:
            profile_summary[p] = {
                'folios': [],
                'baseline_m1_dye': [],
                'baseline_m4f_dye': [],
                'crr_m1': [],
                'crr_m4f': [],
                'nri_m1': [],
                'nri_m4f': [],
                'ablations': {abl: {'delta_m1': [], 'delta_m4f': [], 'delta_adv': []}
                              for abl in ABLATION_NAMES},
            }
        ps = profile_summary[p]
        ps['folios'].append(folio)
        ps['baseline_m1_dye'].append(fe['baseline_m1_dye'])
        ps['baseline_m4f_dye'].append(fe['baseline_m4f_dye'])
        ps['crr_m1'].append(fe['crr_m1'])
        ps['crr_m4f'].append(fe['crr_m4f'])
        ps['nri_m1'].append(fe['nri_m1'])
        ps['nri_m4f'].append(fe['nri_m4f'])
        for abl_name in ABLATION_NAMES:
            abl_data = fe['ablations'][abl_name]
            ps['ablations'][abl_name]['delta_m1'].append(abl_data['delta_m1_dye'])
            ps['ablations'][abl_name]['delta_m4f'].append(abl_data['delta_m4f_dye'])
            ps['ablations'][abl_name]['delta_adv'].append(abl_data['delta_dye_advantage'])

    # Compute means and excess shares
    profile_results = {}
    # Compute non-A2 baseline FI for excess calculation
    non_a2_m4f = []
    for p, ps in profile_summary.items():
        if 'A2' not in p:
            non_a2_m4f.extend(ps['baseline_m4f_dye'])
    non_a2_fi = sum(non_a2_m4f) / len(non_a2_m4f) if non_a2_m4f else 0.0

    for p in sorted(profiles_seen):
        ps = profile_summary[p]
        n = len(ps['folios'])
        fi = sum(ps['baseline_m4f_dye']) / n

        result = {
            'n_folios': n,
            'mean_m1_dye': sum(ps['baseline_m1_dye']) / n,
            'mean_m4f_dye': fi,
            'mean_crr_m1': sum(ps['crr_m1']) / n,
            'mean_crr_m4f': sum(ps['crr_m4f']) / n,
            'mean_nri_m1': sum(ps['nri_m1']) / n,
            'mean_nri_m4f': sum(ps['nri_m4f']) / n,
            'ablation_effects': {},
        }

        fi_excess = fi - non_a2_fi  # How much this profile's FI exceeds non-A2

        for abl_name in ABLATION_NAMES:
            ad = ps['ablations'][abl_name]
            mean_delta_m1 = sum(ad['delta_m1']) / n
            mean_delta_m4f = sum(ad['delta_m4f']) / n
            mean_delta_adv = sum(ad['delta_adv']) / n

            # Excess share: what fraction of this profile's FI excess is
            # explained by this channel?
            # Compute non-A2 mean delta_m4f for this ablation
            non_a2_delta_m4f = []
            for op, ops in profile_summary.items():
                if 'A2' not in op:
                    non_a2_delta_m4f.extend(ops['ablations'][abl_name]['delta_m4f'])
            non_a2_mean_delta = (sum(non_a2_delta_m4f) / len(non_a2_delta_m4f)
                                 if non_a2_delta_m4f else 0.0)
            excess_delta = mean_delta_m4f - non_a2_mean_delta
            excess_share = excess_delta / fi_excess if abs(fi_excess) > 0.001 else 0.0

            result['ablation_effects'][abl_name] = {
                'mean_delta_m1_dye': round(mean_delta_m1, 6),
                'mean_delta_m4f_dye': round(mean_delta_m4f, 6),
                'mean_delta_dye_advantage': round(mean_delta_adv, 6),
                'excess_fi_share': round(excess_share, 4),
            }

        profile_results[p] = result

    # ================================================================
    # Print results
    # ================================================================
    print(f"\n{'=' * 70}")
    print("ABLATION RESULTS BY PROFILE")
    print(f"{'=' * 70}")

    for p in sorted(profile_results):
        pr = profile_results[p]
        print(f"\n  {p} (n={pr['n_folios']}):")
        print(f"    Baseline M1 DYE  = {pr['mean_m1_dye']:.4f}")
        print(f"    Baseline M4f DYE = {pr['mean_m4f_dye']:.4f} (CCS1/FI)")
        print(f"    CRR M1/M4f       = {pr['mean_crr_m1']:.4f} / {pr['mean_crr_m4f']:.4f}")
        print(f"    NRI M1/M4f       = {pr['mean_nri_m1']:.4f} / {pr['mean_nri_m4f']:.4f}")
        print(f"    Ablation effects (positive = channel contributes to DYE):")
        for abl_name in ABLATION_NAMES:
            ae = pr['ablation_effects'][abl_name]
            print(f"      {abl_name:<24s}  dM1={ae['mean_delta_m1_dye']:+.4f}  "
                  f"dM4f={ae['mean_delta_m4f_dye']:+.4f}  "
                  f"dAdv={ae['mean_delta_dye_advantage']:+.4f}  "
                  f"A2excess_share={ae['excess_fi_share']:+.2%}")

    # ================================================================
    # Write output
    # ================================================================
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output = {
        'metadata': {
            'phase': '573',
            'script': 't1_mechanism_ablation.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_folios': len(eligible_folios),
            'n_ablations': len(ABLATION_NAMES),
            'ablation_names': ABLATION_NAMES,
            'n_null_perms': N_NULL_PERMS,
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'profile_results': profile_results,
        'per_folio': per_folio,
        'non_a2_baseline_fi': non_a2_fi,
    }

    out_path = os.path.join(RESULTS_DIR, 't1_mechanism_ablation.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    file_size = os.path.getsize(out_path)
    print(f"\n  Output: {out_path}")
    print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    print(f"\n  Total time: {time.time() - t_start:.1f}s")
    print("  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
