"""
T1: Recovery Gate Decomposition
Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP

Decomposes the NO_CLOSE_RECOVERY effect (C1639) into individual R1-R5
sub-channels to identify which recovery stage makes fake closure acceptable
in A2.

Seven sub-ablation conditions:
  NO_R1          : all k_close[sv] = 0 (kills entire per-SV drawdown)
  NO_R2          : k_cts_close = 0      (kills CTS X->Y transfer)
  NO_R3          : k_relief_close = 0   (kills containment-TR relief)
  NO_R4          : R4_X_TO_Y = R4_C_TO_Y = 0 (kills quality-conditioned Y)
  NO_R5          : r5_bonus = 0         (kills multi-SV coherence bonus)
  NO_R1_C_ONLY   : k_close['C'] = 0    (kills containment drawdown only)
  NO_R4_C_ONLY   : R4_C_TO_Y = 0       (kills C recovery->Y only)

Expert's 4 diagnostic questions:
  1. Too-early recovery?      -> NO_R1 >> NO_R4
  2. Too-undiscriminating?    -> NO_R1_C_ONLY explains most of NO_R1
  3. Too-strong recovery?     -> parameter sensitivity of R1_C_MULT
  4. Too-containment-coupled? -> NO_R4_C_ONLY share
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
    R4_X_TO_Y, R4_C_TO_Y,
    R5_CTS_THRESHOLD,
    SV_INDEX, CTS_WEIGHTED_SVS, PROFILE_CLOSE_MULT, K_CLOSE,
)
from phases.VIRTUAL_APPARATUS_CLOSE_RECOVERY.scripts.t1_close_recovery_apparatus import (
    K_RELIEF,
)
from phases.A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES.scripts.t1_mechanism_ablation import (
    compute_event_dye, select_events,
    override_line_phases, build_demand_shuffled_phases, build_shuffled_event_map,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')
P573_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES', 'results')

SUB_ABLATION_NAMES = [
    'NO_R1', 'NO_R2', 'NO_R3', 'NO_R4', 'NO_R5',
    'NO_R1_C_ONLY', 'NO_R4_C_ONLY',
]

N_NULL_PERMS = 5


# ---------------------------------------------------------------------------
# R4-ablatable apparatus subclass
# ---------------------------------------------------------------------------
class R4AblatedApparatus(FolioSpecificApparatus):
    """FolioSpecificApparatus with overridable R4 coefficients.

    The parent class reads module-level R4_X_TO_Y and R4_C_TO_Y in
    _apply_close_recovery. This subclass stores them as instance vars.
    """

    def __init__(self, *args, r4_x_to_y=None, r4_c_to_y=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._r4_x_to_y = r4_x_to_y if r4_x_to_y is not None else R4_X_TO_Y
        self._r4_c_to_y = r4_c_to_y if r4_c_to_y is not None else R4_C_TO_Y

    def _apply_close_recovery(self, state, packet_phase, cts, dv_magnitude=0.0):
        """Identical to FolioSpecificApparatus._apply_close_recovery except
        R4 computation uses instance-level coefficients."""
        recovery = [0.0] * N_VARS
        details = {'R1': {}, 'R2': {}, 'R3': {}, 'R4': {}, 'R5': {}}

        if packet_phase != 'CLOSE' or not self.enable_close_recovery:
            return recovery, details

        # R1: Per-SV CLOSE drawdown (identical to parent)
        active_svs = []
        moving_toward_eq = []

        for sv in ['T', 'RC', 'S', 'C', 'TR', 'X']:
            i = SV_INDEX[sv]
            dev = state[i] - EQUILIBRIUM
            abs_dev = abs(dev)
            if abs_dev < 1e-10:
                continue
            if sv == 'S' and dev > 0:
                continue
            k = self.k_close.get(sv, 0.0) * self.r1_scale
            profile_mult = PROFILE_CLOSE_MULT[self.profile_name].get(sv, 1.0)
            cts_weight = 1.0
            if sv in CTS_WEIGHTED_SVS:
                cts_weight = 0.5 + 0.5 * max(0.0, min(1.0, cts))
            r1_amount = k * profile_mult * cts_weight * abs_dev
            r1_amount = min(r1_amount, abs_dev)
            sign = 1.0 if dev > 0 else -1.0
            recovery[i] -= r1_amount * sign
            details['R1'][sv] = round(r1_amount, 6)
            from phases.VIRTUAL_APPARATUS_CLOSE_RECOVERY.scripts.t1_close_recovery_apparatus import Q1
            if abs_dev > Q1:
                active_svs.append(sv)
                moving_toward_eq.append(sv)

        clean_close_mult = 1.0 / (1.0 + 10.0 * dv_magnitude)

        # R2: CTS X->Y transfer (identical)
        if cts > 0.3:
            x_idx = SV_INDEX['X']
            x_dev = abs(state[x_idx] - EQUILIBRIUM)
            if x_dev > Q1:
                rate = self.k_cts_close * (cts - 0.3) * max(x_dev - Q1, 0.0)
                rate *= self.config.get('cts_discharge_mult', 1.0)
                x_sign = 1.0 if state[x_idx] > EQUILIBRIUM else -1.0
                recovery[x_idx] -= rate * x_sign
                recovery[SV_INDEX['Y']] += rate * 0.7 * clean_close_mult
                c_idx = SV_INDEX['C']
                c_sign = 1.0 if state[c_idx] > EQUILIBRIUM else -1.0
                recovery[c_idx] -= rate * 0.3 * c_sign
                details['R2'] = {'rate': round(rate, 6), 'cts': round(cts, 4)}

        # R3: Containment-TR relief (identical)
        c_idx = SV_INDEX['C']
        tr_idx = SV_INDEX['TR']
        c_dev = abs(state[c_idx] - EQUILIBRIUM)
        tr_dev = abs(state[tr_idx] - EQUILIBRIUM)
        if c_dev > Q1 and tr_dev > Q1:
            rate = self.k_relief_close * max(c_dev - Q1, 0.0) * max(tr_dev - Q1, 0.0)
            c_sign = 1.0 if state[c_idx] > EQUILIBRIUM else -1.0
            recovery[c_idx] -= rate * c_sign
            recovery[tr_idx] += rate * 0.3 * (1.0 if state[tr_idx] < EQUILIBRIUM else -1.0)
            if 'A3' in self.profile_name:
                recovery[SV_INDEX['Y']] += rate * 0.15 * clean_close_mult
            details['R3'] = {'rate': round(rate, 6)}

        # R4: Quality-conditioned Y accumulation — USES INSTANCE VARS
        x_recovery = abs(details['R1'].get('X', 0.0))
        c_recovery = abs(details['R1'].get('C', 0.0))
        r4_y = cts * (self._r4_x_to_y * x_recovery + self._r4_c_to_y * c_recovery) * clean_close_mult
        if r4_y > 0:
            recovery[SV_INDEX['Y']] += r4_y
            details['R4'] = {'y_gain': round(r4_y, 6)}

        # R5: Coherence bonus (identical)
        n_coherent = len(moving_toward_eq)
        if cts > R5_CTS_THRESHOLD and n_coherent >= 2:
            bonus = 1.0 + self.r5_bonus * (n_coherent - 1)
            for sv in moving_toward_eq:
                i = SV_INDEX[sv]
                r1_val = details['R1'].get(sv, 0.0)
                if r1_val > 0:
                    additional = r1_val * (bonus - 1.0)
                    sign = 1.0 if state[i] > EQUILIBRIUM else -1.0
                    recovery[i] -= additional * sign
            details['R5'] = {
                'n_coherent': n_coherent,
                'bonus': round(bonus, 4),
                'svs': moving_toward_eq,
            }

        return recovery, details


# ---------------------------------------------------------------------------
# Sub-ablation factory
# ---------------------------------------------------------------------------
def create_sub_ablated_apparatus(apparatus, sub_abl_name):
    """Create an apparatus with a specific R sub-channel ablated."""
    if sub_abl_name in ('NO_R4', 'NO_R4_C_ONLY'):
        # Need R4-ablated subclass — reconstruct from apparatus attributes
        base_k_relief = K_RELIEF.get(apparatus.profile_name, 1.0)
        k_relief_scale = apparatus.k_relief_close / max(base_k_relief, 0.001)
        app = R4AblatedApparatus(
            apparatus.profile_name,
            apparatus.original_config_mode,
            apparatus.folio,
            apparatus.f1, apparatus.f2, apparatus.f3,
            apparatus.f4_raw, apparatus.f5,
            r1_scale=apparatus.r1_scale,
            k_cts=apparatus.k_cts_close,
            k_relief_scale=k_relief_scale,
        )
        if sub_abl_name == 'NO_R4':
            app._r4_x_to_y = 0.0
            app._r4_c_to_y = 0.0
        else:  # NO_R4_C_ONLY
            app._r4_c_to_y = 0.0
        return app

    # For all other sub-ablations, deep-copy and patch instance vars
    app = copy.deepcopy(apparatus)

    if sub_abl_name == 'NO_R1':
        for sv in list(app.k_close.keys()):
            app.k_close[sv] = 0.0
    elif sub_abl_name == 'NO_R2':
        app.k_cts_close = 0.0
    elif sub_abl_name == 'NO_R3':
        app.k_relief_close = 0.0
    elif sub_abl_name == 'NO_R5':
        app.r5_bonus = 0.0
    elif sub_abl_name == 'NO_R1_C_ONLY':
        app.k_close['C'] = 0.0

    return app


# ---------------------------------------------------------------------------
# Data loading (mirrors Phase 573 T1)
# ---------------------------------------------------------------------------
def load_all_data():
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')

    print("  Loading Phase 572 T1 setup...")
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json'), 'r', encoding='utf-8') as f:
        t1_setup = json.load(f)

    print("  Loading Phase 572 T2 model runs...")
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json'), 'r', encoding='utf-8') as f:
        t2_runs = json.load(f)

    print("  Loading Phase 572 T3 null runs...")
    with open(os.path.join(P572_RESULTS, 't3_null_runs.json'), 'r', encoding='utf-8') as f:
        t3_nulls = json.load(f)

    print("  Loading Phase 573 T1 ablation (for NO_CLOSE_RECOVERY baseline)...")
    with open(os.path.join(P573_RESULTS, 't1_mechanism_ablation.json'), 'r', encoding='utf-8') as f:
        p573_t1 = json.load(f)

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

    budget_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                               'results', 't2_folio_budgets.json')

    print("  Loading event taxonomy...")
    event_path = os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                              'results', 't1_event_taxonomy.json')
    with open(event_path, 'r', encoding='utf-8') as f:
        event_taxonomy = json.load(f)
    event_map = event_taxonomy['event_map']

    regime_path = os.path.join(PROJECT_ROOT, 'data', 'regime_folio_mapping.json')

    return (t1_setup, t2_runs, t3_nulls, p573_t1,
            line_packets, cts_data, all_tokens, budget_path,
            event_map, regime_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t_start = time.time()
    print("=" * 70)
    print("T1: Recovery Gate Decomposition")
    print("Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")
    (t1_setup, t2_runs, t3_nulls, p573_t1,
     line_packets, cts_data, all_tokens, budget_path,
     event_map, regime_path) = load_all_data()

    eligible_folios = t1_setup['eligible_folios']
    all_folios = t1_setup['all_folios']
    folio_configs = t1_setup['folio_configs']
    primary_runs = t2_runs['primary_runs']
    m0_line_states = t2_runs['m0_line_states']
    null_data = t3_nulls['m4f_demand_matched']

    # Phase 573 NO_CLOSE_RECOVERY baseline for additivity check
    p573_per_folio = p573_t1['per_folio']

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
    # STEP 1: Compute baseline M1/M4f DYE from stored data
    # ================================================================
    print("\n--- Step 1: Baseline DYE from stored data ---")
    baseline_metrics = {}
    for folio in eligible_folios:
        fc = folio_configs[folio]
        m1_events = primary_runs[folio]['M1']['per_event_detail']
        selected_m1 = select_events(m1_events)
        m1_dye = compute_event_dye(selected_m1)

        null_perms = null_data.get(folio, {}).get('all_perms', [])
        perm_dyes = []
        for perm in null_perms:
            matched = perm.get('matched_events', [])
            sel = select_events(matched)
            perm_dyes.append(compute_event_dye(sel))
        m4f_dye = sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0

        baseline_metrics[folio] = {
            'm1_dye': m1_dye,
            'm4f_dye': m4f_dye,
            'profile': fc['profile'],
            'section': fc['section'],
        }

    # Print baseline summary
    for profile in sorted(set(fc['profile'] for fc in folio_configs.values())):
        pf = [v for v in baseline_metrics.values() if v['profile'] == profile]
        if not pf:
            continue
        n = len(pf)
        print(f"  {profile} (n={n}): M1_DYE={sum(v['m1_dye'] for v in pf)/n:.4f}, "
              f"M4f_DYE={sum(v['m4f_dye'] for v in pf)/n:.4f}")

    # ================================================================
    # STEP 2: Run ablated M1 simulations
    # ================================================================
    print(f"\n--- Step 2: Ablated M1 runs ({len(SUB_ABLATION_NAMES)} sub-ablations) ---")
    ablated_m1_dye = {abl: {} for abl in SUB_ABLATION_NAMES}
    run_count = 0
    total_m1 = len(eligible_folios) * len(SUB_ABLATION_NAMES)

    for folio in eligible_folios:
        fc = folio_configs[folio]
        toks = tokens_by_folio[folio]
        if not toks:
            continue

        profile = fc['profile']
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        f1, f2, f3, f4, f5 = fc['F1'], fc['F2'], fc['F3'], fc['F4_raw'], fc['F5']

        full_app = FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4, f5)

        for abl_name in SUB_ABLATION_NAMES:
            abl_app = create_sub_ablated_apparatus(full_app, abl_name)
            result = run_enhanced_event_trace(abl_app, toks, line_packets,
                                              cts_data, event_map)
            result.pop('line_states', None)
            events = result['per_event_detail']
            selected = select_events(events)
            dye = compute_event_dye(selected)
            ablated_m1_dye[abl_name][folio] = dye

            run_count += 1
            if run_count % 100 == 0:
                print(f"  [{run_count}/{total_m1}] M1 sub-ablation runs...")

    print(f"  M1 sub-ablation runs completed: {run_count}")

    # ================================================================
    # STEP 3: Run ablated M4f null simulations
    # ================================================================
    print(f"\n--- Step 3: Ablated M4f runs ({N_NULL_PERMS} perms) ---")
    ablated_m4f_dye = {abl: {} for abl in SUB_ABLATION_NAMES}
    run_count = 0
    total_m4f = len(eligible_folios) * len(SUB_ABLATION_NAMES) * N_NULL_PERMS

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
            for abl_name in SUB_ABLATION_NAMES:
                ablated_m4f_dye[abl_name][folio] = 0.0
            continue

        full_app = FolioSpecificApparatus(profile, config_mode, folio, f1, f2, f3, f4, f5)

        for abl_name in SUB_ABLATION_NAMES:
            abl_app = create_sub_ablated_apparatus(full_app, abl_name)
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
                if run_count % 500 == 0:
                    print(f"  [{run_count}/{total_m4f}] M4f sub-ablation runs...")

            ablated_m4f_dye[abl_name][folio] = (
                sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0
            )

    print(f"  M4f sub-ablation runs completed: {run_count}")

    # ================================================================
    # STEP 4: Compute per-folio sub-ablation effects
    # ================================================================
    print("\n--- Step 4: Computing sub-ablation effects ---")
    per_folio = {}
    for folio in eligible_folios:
        bm = baseline_metrics[folio]
        folio_effects = {
            'profile': bm['profile'],
            'section': bm['section'],
            'baseline_m1_dye': round(bm['m1_dye'], 6),
            'baseline_m4f_dye': round(bm['m4f_dye'], 6),
            'sub_ablations': {},
        }
        for abl_name in SUB_ABLATION_NAMES:
            abl_m1 = ablated_m1_dye[abl_name].get(folio, bm['m1_dye'])
            abl_m4f = ablated_m4f_dye[abl_name].get(folio, bm['m4f_dye'])
            delta_m1 = bm['m1_dye'] - abl_m1
            delta_m4f = bm['m4f_dye'] - abl_m4f
            dye_adv_full = bm['m1_dye'] - bm['m4f_dye']
            dye_adv_abl = abl_m1 - abl_m4f
            delta_adv = dye_adv_full - dye_adv_abl
            folio_effects['sub_ablations'][abl_name] = {
                'abl_m1_dye': round(abl_m1, 6),
                'abl_m4f_dye': round(abl_m4f, 6),
                'delta_m1_dye': round(delta_m1, 6),
                'delta_m4f_dye': round(delta_m4f, 6),
                'delta_dye_advantage': round(delta_adv, 6),
            }
        per_folio[folio] = folio_effects

    # ================================================================
    # STEP 5: Per-profile summary with excess FI shares
    # ================================================================
    print("\n--- Step 5: Profile summary ---")
    profile_summary = {}
    for folio, fe in per_folio.items():
        p = fe['profile']
        if p not in profile_summary:
            profile_summary[p] = {
                'folios': [],
                'baseline_m4f_dye': [],
                'sub_ablations': {abl: {'delta_m4f': []} for abl in SUB_ABLATION_NAMES},
            }
        ps = profile_summary[p]
        ps['folios'].append(folio)
        ps['baseline_m4f_dye'].append(fe['baseline_m4f_dye'])
        for abl_name in SUB_ABLATION_NAMES:
            ps['sub_ablations'][abl_name]['delta_m4f'].append(
                fe['sub_ablations'][abl_name]['delta_m4f_dye'])

    non_a2_m4f = []
    for p, ps in profile_summary.items():
        if 'A2' not in p:
            non_a2_m4f.extend(ps['baseline_m4f_dye'])
    non_a2_fi = sum(non_a2_m4f) / len(non_a2_m4f) if non_a2_m4f else 0.0

    sub_ablation_effects = {}
    for p in sorted(profile_summary.keys()):
        ps = profile_summary[p]
        n = len(ps['folios'])
        fi = sum(ps['baseline_m4f_dye']) / n
        excess_fi = fi - non_a2_fi

        sub_ablation_effects[p] = {'n_folios': n, 'mean_fi': round(fi, 6)}
        for abl_name in SUB_ABLATION_NAMES:
            deltas = ps['sub_ablations'][abl_name]['delta_m4f']
            mean_delta = sum(deltas) / len(deltas) if deltas else 0.0
            # Non-A2 mean delta for excess calculation
            non_a2_deltas = []
            for p2, ps2 in profile_summary.items():
                if 'A2' not in p2:
                    non_a2_deltas.extend(ps2['sub_ablations'][abl_name]['delta_m4f'])
            non_a2_mean_delta = sum(non_a2_deltas) / len(non_a2_deltas) if non_a2_deltas else 0.0
            excess_delta = mean_delta - non_a2_mean_delta
            share = excess_delta / excess_fi if abs(excess_fi) > 0.001 else 0.0

            sub_ablation_effects[p][abl_name] = {
                'mean_delta_m4f': round(mean_delta, 6),
                'excess_fi_share': round(share, 4),
            }

        print(f"  {p} (n={n}, FI={fi:.4f}):")
        for abl in SUB_ABLATION_NAMES:
            d = sub_ablation_effects[p][abl_name]
            print(f"    {abl}: delta_m4f={sub_ablation_effects[p][abl]['mean_delta_m4f']:.4f}, "
                  f"excess_share={sub_ablation_effects[p][abl]['excess_fi_share']:.1%}")

    # ================================================================
    # STEP 6: Additivity check
    # ================================================================
    print("\n--- Step 6: Additivity check ---")
    additivity = {}
    core_subs = ['NO_R1', 'NO_R2', 'NO_R3', 'NO_R4', 'NO_R5']
    for p in sorted(profile_summary.keys()):
        ps = profile_summary[p]
        n = len(ps['folios'])
        # Per-folio additivity
        folio_interactions = []
        for folio in ps['folios']:
            sum_sub = sum(per_folio[folio]['sub_ablations'][abl]['delta_m4f_dye']
                          for abl in core_subs)
            no_cr = p573_per_folio.get(folio, {}).get('ablations', {}).get(
                'NO_CLOSE_RECOVERY', {}).get('delta_m4f_dye', 0.0)
            interaction = 1.0 - sum_sub / no_cr if abs(no_cr) > 0.001 else 0.0
            folio_interactions.append(interaction)

        mean_interaction = sum(folio_interactions) / len(folio_interactions) if folio_interactions else 0.0
        # Classify
        if abs(mean_interaction) < 0.1:
            verdict = 'ADDITIVE'
        elif abs(mean_interaction) < 0.3:
            verdict = 'WEAKLY_INTERACTIVE'
        else:
            verdict = 'STRONGLY_INTERACTIVE'

        additivity[p] = {
            'mean_interaction_fraction': round(mean_interaction, 4),
            'interaction_verdict': verdict,
        }
        print(f"  {p}: interaction={mean_interaction:.4f} ({verdict})")

    # ================================================================
    # STEP 7: Parameter sensitivity (A2 folios only)
    # ================================================================
    print("\n--- Step 7: Parameter sensitivity (A2 only) ---")
    a2_folios = [f for f in eligible_folios if folio_configs[f]['profile'] == 'A2_SEALED_RECIRCULATION']
    print(f"  A2 folios: {len(a2_folios)}")

    param_sensitivity = {}
    # We test 3 parameters; for each we need custom apparatus construction
    param_configs = {
        'R1_C_MULT': {
            'baseline': PROFILE_CLOSE_MULT.get('A2_SEALED_RECIRCULATION', {}).get('C', 1.5),
            'plus': None,  # computed below
            'minus': None,
        },
        'R4_C_TO_Y': {
            'baseline': R4_C_TO_Y,
            'plus': None,
            'minus': None,
        },
        'CLEAN_CLOSE_GAIN': {
            'baseline': 10.0,
            'plus': None,
            'minus': None,
        },
    }
    for pname, pc in param_configs.items():
        pc['plus'] = pc['baseline'] * 1.1
        pc['minus'] = pc['baseline'] * 0.9

    sens_run_count = 0
    for pname, pc in param_configs.items():
        param_sensitivity[pname] = {}
        print(f"  Parameter: {pname} (baseline={pc['baseline']:.4f})")

        for folio in a2_folios:
            fc = folio_configs[folio]
            toks = tokens_by_folio[folio]
            if not toks:
                continue
            profile = fc['profile']
            config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
            f1, f2, f3, f4, f5 = fc['F1'], fc['F2'], fc['F3'], fc['F4_raw'], fc['F5']

            folio_sens = {}
            for direction, val in [('plus', pc['plus']), ('minus', pc['minus'])]:
                # Build modified apparatus
                if pname == 'R4_C_TO_Y':
                    app = R4AblatedApparatus(profile, config_mode, folio,
                                            f1, f2, f3, f4, f5,
                                            r4_c_to_y=val)
                elif pname == 'R1_C_MULT':
                    app = FolioSpecificApparatus(profile, config_mode, folio,
                                                f1, f2, f3, f4, f5)
                    # Patch R1-C multiplier: k_close['C'] is already scaled by F2,
                    # so we scale the profile_close_mult effect via k_close
                    ratio = val / pc['baseline']
                    app.k_close['C'] = app.k_close['C'] * ratio
                else:  # CLEAN_CLOSE_GAIN — can't easily patch, skip for now
                    # This would require modifying _apply_close_recovery's hardcoded 10.0
                    # Skip this parameter — too invasive for instance patching
                    continue

                # M1 run
                result = run_enhanced_event_trace(app, toks, line_packets,
                                                  cts_data, event_map)
                result.pop('line_states', None)
                m1_dye = compute_event_dye(select_events(result['per_event_detail']))

                # M4f runs
                line_states = m0_line_states[folio]
                close_indices = [i for i, ls in enumerate(line_states)
                                 if ls['packet_phase'] == 'CLOSE']
                assignments = build_demand_matched_assignments(
                    line_states, close_indices,
                    n_permutations=N_NULL_PERMS, k_neighbors=5, seed=42)
                perm_dyes = []
                if assignments:
                    for assignment in assignments:
                        shuffled_phases = build_demand_shuffled_phases(line_states, assignment)
                        shuffled_lp = override_line_phases(line_packets, shuffled_phases)
                        shuffled_em = build_shuffled_event_map(event_map, shuffled_phases, line_packets)
                        r = run_enhanced_event_trace(app, toks, shuffled_lp, cts_data, shuffled_em)
                        r.pop('line_states', None)
                        perm_dyes.append(compute_event_dye(select_events(r['per_event_detail'])))
                m4f_dye = sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0

                bm = baseline_metrics[folio]
                folio_sens[direction] = {
                    'value': val,
                    'delta_m1': round(bm['m1_dye'] - m1_dye, 6),
                    'delta_m4f': round(bm['m4f_dye'] - m4f_dye, 6),
                }
                sens_run_count += 1 + len(perm_dyes)

            if folio_sens:
                param_sensitivity[pname][folio] = folio_sens

        if sens_run_count > 0:
            print(f"    Sensitivity runs so far: {sens_run_count}")

    # ================================================================
    # Recovery gate diagnosis
    # ================================================================
    print("\n--- Recovery gate diagnosis ---")
    recovery_diagnosis = {}
    for p in sorted(profile_summary.keys()):
        sae = sub_ablation_effects[p]
        # Find dominant sub-channel by excess share
        shares = {}
        for abl in SUB_ABLATION_NAMES:
            shares[abl] = sae[abl]['excess_fi_share']

        # Sort by absolute share
        ranked = sorted(shares.items(), key=lambda x: abs(x[1]), reverse=True)
        dominant = ranked[0][0]
        dominant_share = ranked[0][1]

        # Check R1_C + R4_C coupling
        r1c_share = shares.get('NO_R1_C_ONLY', 0.0)
        r4c_share = shares.get('NO_R4_C_ONLY', 0.0)
        joint = abs(r1c_share) + abs(r4c_share)

        if abs(r1c_share) > 0.4:
            interp = 'R1_C_DOMINANT'
        elif abs(r4c_share) > 0.4:
            interp = 'R4_C_DOMINANT'
        elif joint > 0.6 and abs(r1c_share) > 0.2 and abs(r4c_share) > 0.2:
            interp = 'R1_R4_COUPLED'
        else:
            interp = 'DISTRIBUTED'

        recovery_diagnosis[p] = {
            'dominant_sub_channel': dominant,
            'dominant_share': round(dominant_share, 4),
            'r1c_share': round(r1c_share, 4),
            'r4c_share': round(r4c_share, 4),
            'r1c_r4c_joint': round(joint, 4),
            'interpretation': interp,
            'ranked_shares': [(k, round(v, 4)) for k, v in ranked],
        }
        print(f"  {p}: {interp} (R1_C={r1c_share:.4f}, R4_C={r4c_share:.4f}, "
              f"joint={joint:.4f})")

    # ================================================================
    # Save output
    # ================================================================
    print("\n--- Saving output ---")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    output = {
        'metadata': {
            'phase': '574',
            'script': 't1_recovery_gate_decomposition.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
            'n_folios': len(eligible_folios),
            'n_sub_ablations': len(SUB_ABLATION_NAMES),
            'sub_ablation_names': SUB_ABLATION_NAMES,
            'n_null_perms': N_NULL_PERMS,
            'n_a2_folios': len(a2_folios),
        },
        'sub_ablation_effects': sub_ablation_effects,
        'per_folio_sub_ablation': per_folio,
        'additivity_check': additivity,
        'parameter_sensitivity': param_sensitivity,
        'recovery_gate_diagnosis': recovery_diagnosis,
        'non_a2_baseline_fi': round(non_a2_fi, 6),
    }

    out_path = os.path.join(RESULTS_DIR, 't1_recovery_gate_decomposition.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, default=str)
    print(f"  Written: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\nDone in {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
