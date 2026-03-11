"""
T3: Packet Authentication Anatomy — Surgical Selectivity Analysis
Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE

Decomposes gate effects per packet signature, builds confusion matrix,
computes Surgical Selectivity Index (SSI), and performs layer decomposition.
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from phases.DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR.scripts.t1_enhanced_event_trace import (
    run_enhanced_event_trace, sort_key,
    assign_folio_profiles, compute_infra_scores,
)
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    build_demand_matched_assignments,
)
from phases.A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES.scripts.t1_mechanism_ablation import (
    compute_event_dye, select_events,
    override_line_phases, build_demand_shuffled_phases, build_shuffled_event_map,
)
from phases.SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE.scripts.t0_acs_assembly import (
    SIGNATURE_OFFSET_TABLE, SIGNATURE_CLASSES,
)
from phases.SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE.scripts.t1_authenticated_apparatus import (
    create_authenticated_apparatus,
    run_authenticated_event_trace,
)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')

N_NULL_PERMS = 5


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T3: Packet Authentication Anatomy")
    print("Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')

    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json')) as f:
        t1_setup = json.load(f)
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json')) as f:
        t2_runs = json.load(f)
    with open(os.path.join(P572_RESULTS, 't3_null_runs.json')) as f:
        t3_nulls = json.load(f)

    # Line packets, CTS, tokens, event map
    with open(os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't3_line_packets.json')) as f:
        line_packets = json.load(f)['line_packets']
    with open(os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't7_closure_cts.json')) as f:
        cts_raw = json.load(f)
    cts_data = {}
    if 'line_cts' in cts_raw:
        for key, val in cts_raw['line_cts'].items():
            cts_data[key] = val.get('cts', 0.0) if isinstance(val, dict) else float(val)
    elif 'cts_scores' in cts_raw:
        for key, val in cts_raw['cts_scores'].items():
            cts_data[key] = (val.get('cts', val.get('score', 0.0))
                             if isinstance(val, dict) else float(val))

    with open(os.path.join(phases_dir, 'VIRTUAL_APPARATUS_COUPLING',
                           'results', 't2b_supervisory_interface_unrouted.json')) as f:
        all_tokens = json.load(f)['token_signals']
    with open(os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                           'results', 't1_event_taxonomy.json')) as f:
        event_map = json.load(f)['event_map']

    # Phase 575 T0 + T2 results
    with open(os.path.join(RESULTS_DIR, 't0_acs_assembly.json')) as f:
        t0_acs = json.load(f)
    with open(os.path.join(RESULTS_DIR, 't2_gated_simulation.json')) as f:
        t2_gated = json.load(f)

    # Phase 574 T0 events (for band classification)
    with open(os.path.join(phases_dir,
        'COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP', 'results',
        't0_event_feature_assembly.json')) as f:
        t0_574 = json.load(f)

    acs_lookup = t0_acs['per_line_acs']
    empirical_thresholds = t0_acs['empirical_thresholds']
    per_event_acs = t0_acs['per_event_acs']

    eligible_folios = t1_setup['eligible_folios']
    folio_configs = t1_setup['folio_configs']
    m0_line_states = t2_runs['m0_line_states']
    primary_runs = t2_runs['primary_runs']
    null_data = t3_nulls['m4f_demand_matched']
    all_folios = t1_setup['all_folios']

    budget_path = os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                               'results', 't2_folio_budgets.json')
    regime_path = os.path.join(PROJECT_ROOT, 'data', 'regime_folio_mapping.json')

    folio_assignments = assign_folio_profiles(regime_path, budget_path)
    folio_infra = compute_infra_scores(all_folios)

    eligible_set = set(eligible_folios)
    tokens_by_folio = {f: [] for f in eligible_set}
    for tok in all_tokens:
        if tok['folio'] in eligible_set:
            tokens_by_folio[tok['folio']].append(tok)
    for folio in tokens_by_folio:
        tokens_by_folio[folio].sort(key=sort_key)

    # Build event-level band + signature lookup
    event_bands = {}
    event_sigs = {}
    for ev in per_event_acs:
        lk = ev['line_key']
        event_sigs[lk] = ev['signature']
    for ev in t0_574['m1_events']:
        event_bands[ev['line_key']] = ev.get('n_strong_signals', 0)

    # ================================================================
    # Part 1: Per-signature gate effect (MODERATE config)
    # ================================================================
    print("\n--- Part 1: Per-signature gate effect ---")
    moderate_results = t2_gated['per_config'].get('MODERATE', {})

    # Compute baseline DYE per folio (from stored data)
    baseline = {}
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
        baseline[folio] = {
            'm1_dye': m1_dye, 'm4f_dye': m4f_dye,
            'advantage': m1_dye - m4f_dye,
            'profile': fc['profile'],
        }

    # Per-signature: aggregate gated vs ungated DYE_adv from T2 gated results
    # We need per-event info — use the T0 ACS data per line to match signatures
    # and compute auth_mult per line for MODERATE config
    per_sig_stats = {}
    for sig in list(SIGNATURE_OFFSET_TABLE.keys()) + ['bare']:
        per_sig_stats[sig] = {
            'class': SIGNATURE_CLASSES.get(sig, 'UNKNOWN'),
            'acs_values': [],
            'auth_mults': [],
            'ungated_dye_advs': [],
            'gated_dye_advs': [],
        }

    # For each event, compute auth_mult under MODERATE
    for ev_acs in per_event_acs:
        sig = ev_acs['signature']
        if sig not in per_sig_stats:
            per_sig_stats[sig] = {
                'class': SIGNATURE_CLASSES.get(sig, 'UNKNOWN'),
                'acs_values': [], 'auth_mults': [],
                'ungated_dye_advs': [], 'gated_dye_advs': [],
            }

        profile = ev_acs['profile']
        if 'A1' in profile:
            thresh = empirical_thresholds['MODERATE'].get('A1', 0.05)
        elif 'A2' in profile:
            thresh = empirical_thresholds['MODERATE'].get('A2', 0.35)
        else:
            thresh = empirical_thresholds['MODERATE'].get('A3', 0.10)

        acs_val = ev_acs['ACS']
        auth_mult = max(0.0, min(1.0, acs_val / thresh)) if thresh > 0 else 1.0

        per_sig_stats[sig]['acs_values'].append(acs_val)
        per_sig_stats[sig]['auth_mults'].append(auth_mult)
        per_sig_stats[sig]['ungated_dye_advs'].append(ev_acs.get('DYE_adv_event', 0))

    # Build per-signature summary
    per_signature = {}
    for sig, stats in per_sig_stats.items():
        if not stats['acs_values']:
            continue
        n = len(stats['acs_values'])
        mean_acs = sum(stats['acs_values']) / n
        mean_am = sum(stats['auth_mults']) / n
        mean_ungated = sum(stats['ungated_dye_advs']) / n

        sig_class = stats['class']
        if sig_class == 'RESISTANT':
            correctly_gated = mean_am > 0.7
        elif sig_class == 'A2_COUNTERFEITABLE':
            correctly_gated = mean_am < 0.5
        else:
            correctly_gated = None  # can't classify

        per_signature[sig] = {
            'class': sig_class,
            'n_events': n,
            'mean_acs': round(mean_acs, 6),
            'mean_auth_mult': round(mean_am, 6),
            'ungated_mean_dye_adv': round(mean_ungated, 6),
            'correctly_gated': correctly_gated,
        }

        print(f"  {sig[:50]:50s} | class={sig_class:20s} | am={mean_am:.3f} | "
              f"correct={correctly_gated}")

    # ================================================================
    # Part 2: Confusion matrix per config
    # ================================================================
    print("\n--- Part 2: Confusion matrix ---")
    confusion_matrices = {}

    for config_name in t2_gated['gate_configs']:
        thresholds = t2_gated['gate_configs'][config_name]['thresholds']
        tp, tn, fp, fn = 0, 0, 0, 0

        for sig, stats in per_sig_stats.items():
            if not stats['acs_values']:
                continue
            sig_class = SIGNATURE_CLASSES.get(sig)
            if sig_class is None:
                continue

            # Compute auth_mult for this config
            config_ams = []
            for ev_acs in per_event_acs:
                if ev_acs['signature'] != sig:
                    continue
                profile = ev_acs['profile']
                if 'A1' in profile:
                    thresh = thresholds.get('A1', 0.05)
                elif 'A2' in profile:
                    thresh = thresholds.get('A2', 0.35)
                else:
                    thresh = thresholds.get('A3', 0.10)
                am = max(0.0, min(1.0, ev_acs['ACS'] / thresh)) if thresh > 0 else 1.0
                config_ams.append(am)

            if not config_ams:
                continue
            mean_am = sum(config_ams) / len(config_ams)

            is_counterfeitable = sig_class == 'A2_COUNTERFEITABLE'
            predicted_counterfeit = mean_am < 0.5

            if is_counterfeitable and predicted_counterfeit:
                tp += 1
            elif not is_counterfeitable and not predicted_counterfeit:
                tn += 1
            elif not is_counterfeitable and predicted_counterfeit:
                fp += 1
            elif is_counterfeitable and not predicted_counterfeit:
                fn += 1

        confusion_matrices[config_name] = {'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn}
        print(f"  {config_name}: TP={tp}, TN={tn}, FP={fp}, FN={fn}")

    # ================================================================
    # Part 3: Surgical Selectivity Index (SSI) per config
    # ================================================================
    print("\n--- Part 3: Surgical Selectivity Index ---")
    surgical_selectivity = {}

    for config_name, folio_results in t2_gated['per_config'].items():
        # Compute per-band deltas for A2 folios
        a2_band_deltas = {'STRONG': [], 'MEDIUM': [], 'WEAK': []}

        for folio, r in folio_results.items():
            if 'A2' not in r.get('profile', ''):
                continue
            bl = baseline.get(folio, {})
            bl_adv = bl.get('advantage', 0)
            gated_adv = r.get('gated_advantage', 0)

            # Use band info from T2
            for band_name in ['STRONG', 'MEDIUM', 'WEAK']:
                bd = r.get('by_band', {}).get(band_name, {})
                if bd.get('n_events', 0) > 0:
                    a2_band_deltas[band_name].append(bd.get('gated_mean_dye', 0))

        # For SSI: need weak-band FI reduction and strong-band DYE loss
        # Use profile-level summary from T2
        ps = t2_gated['profile_summary'].get(config_name, {})
        a2_summary = ps.get('A2_SEALED_RECIRCULATION', {})

        # Weak band FI reduction: how much the weak-band M4f (false intelligence)
        # component is reduced. Approximate from delta_m4f_dye / baseline_m4f
        mean_delta_m4f = a2_summary.get('mean_delta_m4f_dye', 0)
        mean_baseline_adv = a2_summary.get('mean_baseline_advantage', 0)
        mean_delta_adv = a2_summary.get('mean_delta_advantage', 0)

        # Weak band: lower DYE_adv means less false reward
        weak_band_info = a2_summary.get('by_band', {}).get('WEAK', {})
        strong_band_info = a2_summary.get('by_band', {}).get('STRONG', {})
        medium_band_info = a2_summary.get('by_band', {}).get('MEDIUM', {})

        # SSI = weak_band_FI_reduction / (strong_band_DYE_loss + 0.001)
        # Use mean_delta_adv as a proxy: negative delta = reduction
        # For proper SSI, we compare band-specific changes
        # Weak reduction = absolute reduction in weak-band gated DYE (good if negative)
        # Strong loss = reduction in strong-band gated DYE (bad if negative)
        weak_gated_dye = weak_band_info.get('mean_gated_dye', 0)
        strong_gated_dye = strong_band_info.get('mean_gated_dye', 0)

        # Since we're comparing gated to ungated, and we have delta_advantage:
        # SSI measures selectivity: how much weak improves vs how much strong degrades
        # Simplify: use CCS1 reduction as weak indicator, delta_adv as strong indicator
        ccs1_red = abs(a2_summary.get('ccs1_reduction_pct', 0))
        fi_reduction = abs(mean_delta_m4f) if mean_delta_m4f < 0 else 0
        strong_loss = abs(mean_delta_adv) if mean_delta_adv < 0 else 0

        # Better SSI: ratio of absolute FI reduction to strong band degradation
        ssi = fi_reduction / (strong_loss + 0.001)

        surgical_selectivity[config_name] = {
            'SSI': round(ssi, 4),
            'fi_reduction': round(fi_reduction, 6),
            'strong_loss': round(strong_loss, 6),
            'ccs1_reduction_pct': round(ccs1_red, 2),
            'mean_delta_advantage': round(mean_delta_adv, 6),
            'weak_band_mean_gated_dye': round(weak_gated_dye, 6),
            'strong_band_mean_gated_dye': round(strong_gated_dye, 6),
        }
        print(f"  {config_name}: SSI={ssi:.4f}, FI_red={fi_reduction:.6f}, "
              f"strong_loss={strong_loss:.6f}")

    # Find best config by SSI
    best_config = max(surgical_selectivity, key=lambda c: surgical_selectivity[c]['SSI'])
    print(f"\n  Best config by SSI: {best_config} (SSI={surgical_selectivity[best_config]['SSI']:.4f})")

    # ================================================================
    # Part 4: Repair pattern check
    # ================================================================
    print("\n--- Part 4: Repair pattern ---")

    # For MODERATE config: compute delta(gated - ungated DYE_adv) per signature class
    delta_counterfeitable = []
    delta_resistant = []

    for ev_acs in per_event_acs:
        if 'A2' not in ev_acs.get('profile', ''):
            continue
        sig = ev_acs['signature']
        sig_class = SIGNATURE_CLASSES.get(sig)
        if sig_class is None:
            continue

        ungated_adv = ev_acs.get('DYE_adv_event', 0)

        if sig_class == 'A2_COUNTERFEITABLE':
            delta_counterfeitable.append(ungated_adv)
        elif sig_class == 'RESISTANT':
            delta_resistant.append(ungated_adv)

    mean_delta_cf = sum(delta_counterfeitable) / len(delta_counterfeitable) if delta_counterfeitable else 0
    mean_delta_res = sum(delta_resistant) / len(delta_resistant) if delta_resistant else 0

    # The gate should reduce counterfeit DYE_adv MORE than it reduces resistant DYE_adv
    # Since gated runs are in T2, we approximate repair delta from auth_mult effects
    repair_pattern = {
        'mean_ungated_dye_adv_counterfeitable': round(mean_delta_cf, 6),
        'mean_ungated_dye_adv_resistant': round(mean_delta_res, 6),
        'resistant_minus_counterfeitable': round(mean_delta_res - mean_delta_cf, 6),
        'n_counterfeitable': len(delta_counterfeitable),
        'n_resistant': len(delta_resistant),
    }
    print(f"  Counterfeitable mean ungated DYE_adv: {mean_delta_cf:.6f}")
    print(f"  Resistant mean ungated DYE_adv: {mean_delta_res:.6f}")
    print(f"  Gap (resistant - counterfeitable): {mean_delta_res - mean_delta_cf:.6f}")

    # ================================================================
    # Part 5: Layer decomposition (A2 folios, MODERATE threshold)
    # ================================================================
    print("\n--- Part 5: Layer decomposition ---")

    a2_folios = [f for f in eligible_folios
                 if 'A2' in folio_configs[f].get('profile', '')]
    print(f"  A2 folios: {len(a2_folios)}")

    mod_thresh = empirical_thresholds['MODERATE']
    layer_results = {'layer1_only': [], 'layer2_proxy': [], 'both': []}

    run_count = 0
    for folio in a2_folios:
        fc = folio_configs[folio]
        toks = tokens_by_folio[folio]
        if not toks:
            continue

        profile = fc['profile']
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        thresh = mod_thresh.get('A2', 0.35)

        f_params = {
            'config_mode': config_mode,
            'f1': fc['F1'], 'f2': fc['F2'], 'f3': fc['F3'],
            'f4_raw': fc['F4_raw'], 'f5': fc['F5'],
        }

        # Layer 1 only: threshold active, penalty=0
        l1_app = create_authenticated_apparatus(
            folio, profile, f_params,
            acs_threshold=thresh,
            cleanliness_penalty=0.0,
            acs_lookup=acs_lookup)
        l1_result = run_authenticated_event_trace(
            l1_app, toks, line_packets, cts_data, event_map)
        l1_result.pop('line_states', None)
        l1_events = select_events(l1_result['per_event_detail'])
        l1_dye = compute_event_dye(l1_events)
        run_count += 1

        # Both layers: threshold active, penalty=10
        both_app = create_authenticated_apparatus(
            folio, profile, f_params,
            acs_threshold=thresh,
            cleanliness_penalty=10.0,
            acs_lookup=acs_lookup)
        both_result = run_authenticated_event_trace(
            both_app, toks, line_packets, cts_data, event_map)
        both_result.pop('line_states', None)
        both_events = select_events(both_result['per_event_detail'])
        both_dye = compute_event_dye(both_events)
        run_count += 1

        # Layer 2 proxy: use high threshold (so auth_mult is low, but we only
        # get the combined effect). Compare with zero-gated baseline to isolate
        # We can also compute layer2 effect as: both - layer1
        bl = baseline.get(folio, {})
        bl_m1_dye = bl.get('m1_dye', 0)

        l1_delta = bl_m1_dye - l1_dye
        both_delta = bl_m1_dye - both_dye
        l2_incremental = both_delta - l1_delta

        layer_results['layer1_only'].append(l1_delta)
        layer_results['layer2_proxy'].append(l2_incremental)
        layer_results['both'].append(both_delta)

        if run_count % 20 == 0:
            print(f"  [{run_count}] runs completed...")

    # Summarize layer decomposition
    def mean_list(lst):
        return sum(lst) / len(lst) if lst else 0.0

    l1_mean = mean_list(layer_results['layer1_only'])
    l2_mean = mean_list(layer_results['layer2_proxy'])
    both_mean = mean_list(layer_results['both'])

    synergy = both_mean > max(l1_mean, l2_mean)
    l2_contributes = l2_mean > 0.0001
    l1_contributes = l1_mean > 0.0001

    layer_decomposition = {
        'layer1_only_mean_delta': round(l1_mean, 6),
        'layer2_incremental_mean_delta': round(l2_mean, 6),
        'both_mean_delta': round(both_mean, 6),
        'synergy': synergy,
        'layer1_contributes': l1_contributes,
        'layer2_contributes': l2_contributes,
        'n_folios': len(a2_folios),
        'total_runs': run_count,
    }
    print(f"\n  Layer 1 only: mean delta = {l1_mean:.6f}")
    print(f"  Layer 2 incremental: mean delta = {l2_mean:.6f}")
    print(f"  Both layers: mean delta = {both_mean:.6f}")
    print(f"  Synergy (both > max(individual)): {synergy}")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '575',
            'script': 't3_packet_authentication_anatomy.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'per_signature': per_signature,
        'confusion_matrix': confusion_matrices,
        'surgical_selectivity': surgical_selectivity,
        'best_config_by_SSI': best_config,
        'repair_pattern': repair_pattern,
        'layer_decomposition': layer_decomposition,
    }

    out_path = os.path.join(RESULTS_DIR, 't3_packet_authentication_anatomy.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Total elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
