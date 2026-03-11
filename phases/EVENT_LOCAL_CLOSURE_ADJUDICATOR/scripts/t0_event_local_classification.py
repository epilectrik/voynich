"""
Phase 578 T0: Event-Local Feature Extraction + Burden-Resolution Classification

Computes execution-derived features for all 463 M1 CLOSE events from Phase 572
ungated runs. Classifies into 4 event-legitimacy tiers based on burden resolution
and event-level packet strength. Y_gain is NOT used in classification (outcome
leakage avoidance). Event-local packet anatomy stored for T3 analysis and future
Phase 579 use.

Classes:
  AUTHENTIC_RESOLVER:       burden_frac_resolved >= 0.20 AND n_strong_signals >= 1
  PARTIAL_RESOLVER:         burden_frac_resolved >= 0.05 AND NOT AUTHENTIC
  NONRESOLVING_COUNTERFEIT: burden_frac_resolved < 0.05 (includes negative + stagnant)
  INERT_PSEUDO:             dv_magnitude_sum <= 0.05
"""

import json
import os
import sys
from datetime import datetime, timezone
from collections import Counter

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')
PROJECT_ROOT = os.path.dirname(os.path.dirname(PHASE_DIR))

# SV indices
SV_INDEX = {'T': 0, 'RC': 1, 'S': 2, 'C': 3, 'TR': 4, 'X': 5, 'Y': 6}
EQUILIBRIUM = 0.5

# Classification thresholds
AUTHENTIC_BURDEN_THRESHOLD = 0.20   # burden_frac_resolved >= 0.20 for AUTHENTIC
PARTIAL_BURDEN_THRESHOLD = 0.05     # burden_frac_resolved >= 0.05 for PARTIAL
DV_ACTIVITY_FLOOR = 0.05            # dv_magnitude_sum <= 0.05 -> INERT_PSEUDO
LOW_BURDEN_FLOOR = 0.01             # burden_pre < 0.01 -> treat as non-resolving


def compute_burden_features(close_pre_state, line_end_state):
    """Compute burden resolution features from M1 ungated event states."""
    c_pre = abs(close_pre_state[SV_INDEX['C']] - EQUILIBRIUM)
    x_pre = abs(close_pre_state[SV_INDEX['X']] - EQUILIBRIUM)
    burden_pre = max(c_pre, x_pre)

    c_post = abs(line_end_state[SV_INDEX['C']] - EQUILIBRIUM)
    x_post = abs(line_end_state[SV_INDEX['X']] - EQUILIBRIUM)
    burden_post = max(c_post, x_post)

    burden_delta = burden_pre - burden_post  # positive = resolved

    # Handle trivially low burden
    if burden_pre < LOW_BURDEN_FLOOR:
        burden_frac_resolved = 0.0  # no meaningful burden to resolve
    else:
        burden_frac_resolved = burden_delta / burden_pre

    # Burden-direction coherence
    c_toward_eq = c_post < c_pre
    x_toward_eq = x_post < x_pre
    resolution_coherent = c_toward_eq and x_toward_eq

    return {
        'burden_pre': round(burden_pre, 6),
        'burden_post': round(burden_post, 6),
        'burden_delta': round(burden_delta, 6),
        'burden_frac_resolved': round(burden_frac_resolved, 6),
        'c_toward_eq': c_toward_eq,
        'x_toward_eq': x_toward_eq,
        'resolution_coherent': resolution_coherent,
    }


def classify_event(burden_frac_resolved, dv_magnitude, n_strong_signals):
    """Classify a CLOSE event into one of 4 legitimacy tiers.

    Classification order (priority):
    1. INERT_PSEUDO: dv <= 0.05
    2. NONRESOLVING_COUNTERFEIT: burden_frac_resolved < 0.05
    3. AUTHENTIC_RESOLVER: burden_frac_resolved >= 0.20 AND n_strong_signals >= 1
    4. PARTIAL_RESOLVER: everything else
    """
    if dv_magnitude <= DV_ACTIVITY_FLOOR:
        return 'INERT_PSEUDO'
    if burden_frac_resolved < PARTIAL_BURDEN_THRESHOLD:
        return 'NONRESOLVING_COUNTERFEIT'
    if burden_frac_resolved >= AUTHENTIC_BURDEN_THRESHOLD and n_strong_signals >= 1:
        return 'AUTHENTIC_RESOLVER'
    return 'PARTIAL_RESOLVER'


def main():
    t_start = datetime.now(timezone.utc)

    # --- Load data sources ---

    # Phase 572 M1 per_event_detail (close_pre_state, line_end_state)
    p572_path = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION',
                             'results', 't2_full_model_runs.json')
    print(f"Loading Phase 572 M1 runs...")
    with open(p572_path) as f:
        p572_data = json.load(f)

    # Phase 574 T0 m1_events (CRR, NRI, grammar_band, n_strong_signals, etc.)
    p574_path = os.path.join(PROJECT_ROOT, 'phases',
                             'COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP',
                             'results', 't0_event_feature_assembly.json')
    print(f"Loading Phase 574 T0 events...")
    with open(p574_path) as f:
        p574_data = json.load(f)

    # Phase 576 T0 per_line_classification (morphological classes, CTS)
    p576_path = os.path.join(PROJECT_ROOT, 'phases', 'CLOSURE_REGIME_ADMISSION_GATE',
                             'results', 't0_corpus_classification.json')
    print(f"Loading Phase 576 T0 classification...")
    with open(p576_path) as f:
        p576_data = json.load(f)

    # --- Build event lookup from Phase 574 ---
    p574_lookup = {}
    for ev in p574_data['m1_events']:
        p574_lookup[ev['line_key']] = ev

    # --- Extract M1 per_event_detail from Phase 572 ---
    m1_events = []
    for folio, folio_data in p572_data['primary_runs'].items():
        m1_detail = folio_data.get('M1', {}).get('per_event_detail', [])
        for ev in m1_detail:
            ev['folio'] = folio
            m1_events.append(ev)

    print(f"Loaded {len(m1_events)} M1 events from Phase 572")
    print(f"Phase 574 has {len(p574_lookup)} event records")

    # --- Classify events ---
    per_line_classification = {}
    class_counts = Counter()
    burden_frac_values = []
    cross_tab_class_vs_morph = Counter()
    cross_tab_class_vs_grammar = Counter()
    cross_tab_class_vs_coherence = Counter()
    burden_quartile_dye_adv = {'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []}

    classified_events = []

    for ev in m1_events:
        line_key = ev['line_key']
        close_pre_state = ev['close_pre_state']
        line_end_state = ev['line_end_state']
        dv_magnitude = ev['dv_magnitude_sum']
        y_gain = ev['y_gain_event']

        # Compute burden features
        bf = compute_burden_features(close_pre_state, line_end_state)
        burden_frac_values.append(bf['burden_frac_resolved'])

        # Get Phase 574 event features
        p574_ev = p574_lookup.get(line_key, {})
        n_strong_signals = p574_ev.get('n_strong_signals', 0)
        grammar_band = p574_ev.get('grammar_band', 'WEAK')

        # Classify
        event_class = classify_event(bf['burden_frac_resolved'], dv_magnitude,
                                     n_strong_signals)
        class_counts[event_class] += 1

        # Get Phase 576 morphological class
        p576_entry = p576_data['per_line_classification'].get(line_key, {})
        morph_class = p576_entry.get('class', 'UNKNOWN')
        cts = p576_entry.get('cts', p574_ev.get('CTS', 0.0))

        # Cross-tabulations
        cross_tab_class_vs_morph[(event_class, morph_class)] += 1
        cross_tab_class_vs_grammar[(event_class, grammar_band)] += 1
        cross_tab_class_vs_coherence[(event_class, bf['resolution_coherent'])] += 1

        # Build classification entry
        entry = {
            'class': event_class,
            'cts': round(cts, 4),
            # Burden features
            'burden_pre': bf['burden_pre'],
            'burden_post': bf['burden_post'],
            'burden_frac_resolved': bf['burden_frac_resolved'],
            'c_toward_eq': bf['c_toward_eq'],
            'x_toward_eq': bf['x_toward_eq'],
            'resolution_coherent': bf['resolution_coherent'],
            # Morphological cross-reference
            'morphological_class': morph_class,
            # Event-local packet anatomy (stored for T3/P579)
            'n_strong_signals': n_strong_signals,
            'grammar_band': grammar_band,
            'E_cts50': p574_ev.get('E_cts50', False),
            'E_mcb': p574_ev.get('E_mcb', False),
            'E_opaque': p574_ev.get('E_opaque', False),
            'E_armed': p574_ev.get('E_armed', False),
            'CRR': round(p574_ev.get('CRR', 0.0), 6),
            'NRI': round(p574_ev.get('NRI', 0.0), 6),
            # Evaluation-only (NOT used in classification)
            'y_gain_event': round(y_gain, 8),
            'dv_magnitude': round(dv_magnitude, 6),
            'dye_event': round(y_gain / dv_magnitude, 6) if dv_magnitude > 0.001 else 0.0,
            'DYE_adv_event': round(p574_ev.get('DYE_adv_event', 0.0), 6),
        }
        per_line_classification[line_key] = entry
        classified_events.append(entry)

    # --- Add non-CLOSE lines ---
    n_non_close = 0
    for line_key, p576_entry in p576_data['per_line_classification'].items():
        if line_key not in per_line_classification:
            per_line_classification[line_key] = {
                'class': 'NON_CLOSE',
                'cts': round(p576_entry.get('cts', 0.0), 4),
            }
            n_non_close += 1

    print(f"\nClassified {len(classified_events)} CLOSE events + {n_non_close} non-CLOSE lines")
    print(f"Total per_line_classification entries: {len(per_line_classification)}")

    # --- Distribution statistics ---
    burden_sorted = sorted(burden_frac_values)
    n = len(burden_sorted)
    percentiles = {}
    for p in [5, 10, 25, 50, 75, 90, 95]:
        idx = min(int(n * p / 100), n - 1)
        percentiles[f'p{p}'] = round(burden_sorted[idx], 4)

    print(f"\nBurden fraction resolved distribution:")
    print(f"  Min: {burden_sorted[0]:.4f}, Max: {burden_sorted[-1]:.4f}")
    for k, v in percentiles.items():
        print(f"  {k}: {v}")

    print(f"\nClass distribution:")
    for cls in ['AUTHENTIC_RESOLVER', 'PARTIAL_RESOLVER', 'NONRESOLVING_COUNTERFEIT', 'INERT_PSEUDO']:
        c = class_counts.get(cls, 0)
        pct = 100.0 * c / len(classified_events) if classified_events else 0
        print(f"  {cls}: {c} ({pct:.1f}%)")

    # --- Threshold calibration check ---
    auth_pct = 100.0 * class_counts.get('AUTHENTIC_RESOLVER', 0) / len(classified_events)
    if auth_pct < 15 or auth_pct > 70:
        print(f"\nWARNING: AUTHENTIC_RESOLVER at {auth_pct:.1f}% -- outside 15-70% range")
        print("  Adaptive threshold adjustment may be needed")

    # --- Cross-tabulation formatting ---
    # Class vs morphological class
    morph_classes = sorted(set(k[1] for k in cross_tab_class_vs_morph.keys()))
    event_classes = ['AUTHENTIC_RESOLVER', 'PARTIAL_RESOLVER', 'NONRESOLVING_COUNTERFEIT', 'INERT_PSEUDO']

    print(f"\nClass vs Morphological Class cross-tab:")
    header = f"{'EVENT_CLASS':<30s}" + "".join(f"{mc:<22s}" for mc in morph_classes)
    print(f"  {header}")
    for ec in event_classes:
        row = f"{ec:<30s}"
        for mc in morph_classes:
            row += f"{cross_tab_class_vs_morph.get((ec, mc), 0):<22d}"
        print(f"  {row}")

    # Class vs grammar band
    print(f"\nClass vs Grammar Band cross-tab:")
    for ec in event_classes:
        parts = []
        for gb in ['STRONG', 'MEDIUM', 'WEAK']:
            parts.append(f"{gb}={cross_tab_class_vs_grammar.get((ec, gb), 0)}")
        print(f"  {ec}: {', '.join(parts)}")

    # Class vs coherence
    print(f"\nClass vs Resolution Coherence:")
    for ec in event_classes:
        coh = cross_tab_class_vs_coherence.get((ec, True), 0)
        incoh = cross_tab_class_vs_coherence.get((ec, False), 0)
        total = coh + incoh
        pct = 100.0 * coh / total if total > 0 else 0
        print(f"  {ec}: coherent={coh}, incoherent={incoh} ({pct:.1f}% coherent)")

    # --- C1661 preliminary: burden quartile vs DYE_adv ---
    # Assign quartiles
    q_boundaries = [percentiles['p25'], percentiles['p50'], percentiles['p75']]
    dye_adv_by_quartile = {1: [], 2: [], 3: [], 4: []}
    for ev in classified_events:
        bfr = ev['burden_frac_resolved']
        dye_adv = ev['DYE_adv_event']
        if bfr < q_boundaries[0]:
            q = 1
        elif bfr < q_boundaries[1]:
            q = 2
        elif bfr < q_boundaries[2]:
            q = 3
        else:
            q = 4
        dye_adv_by_quartile[q].append(dye_adv)

    print(f"\nC1661 Preliminary: burden_frac_resolved quartile vs DYE_adv_event:")
    quartile_summary = {}
    for q in [1, 2, 3, 4]:
        vals = dye_adv_by_quartile[q]
        if vals:
            mean_adv = sum(vals) / len(vals)
            pos_count = sum(1 for v in vals if v > 0)
            pos_rate = 100.0 * pos_count / len(vals)
        else:
            mean_adv = 0.0
            pos_rate = 0.0
        quartile_summary[f'Q{q}'] = {
            'n': len(vals),
            'mean_dye_adv': round(mean_adv, 6),
            'positive_rate_pct': round(pos_rate, 1),
        }
        print(f"  Q{q} (n={len(vals)}): mean_DYE_adv={mean_adv:.6f}, positive_rate={pos_rate:.1f}%")

    # --- Per-class DYE_adv summary ---
    print(f"\nPer-class DYE_adv_event summary:")
    class_dye_adv = {}
    for ec in event_classes:
        vals = [ev['DYE_adv_event'] for ev in classified_events if ev['class'] == ec]
        if vals:
            mean_adv = sum(vals) / len(vals)
            pos_count = sum(1 for v in vals if v > 0)
            pos_rate = 100.0 * pos_count / len(vals)
        else:
            mean_adv = 0.0
            pos_rate = 0.0
        class_dye_adv[ec] = {
            'n': len(vals),
            'mean_dye_adv': round(mean_adv, 6),
            'positive_rate_pct': round(pos_rate, 1),
        }
        print(f"  {ec} (n={len(vals)}): mean_DYE_adv={mean_adv:.6f}, positive={pos_rate:.1f}%")

    # --- Verification ---
    print(f"\n--- Verification ---")
    n_events = len(classified_events)
    n_total = len(per_line_classification)
    checks = []

    # All 463 events classified
    check_463 = n_events == 463
    checks.append(('all_463_classified', check_463))
    print(f"All 463 events classified: {'PASS' if check_463 else f'FAIL ({n_events})'}")

    # All 4 classes populated
    all_populated = all(class_counts.get(c, 0) > 0 for c in event_classes)
    checks.append(('all_classes_populated', all_populated))
    print(f"All 4 classes populated: {'PASS' if all_populated else 'FAIL'}")

    # AUTHENTIC 15-60%
    auth_ok = 15 <= auth_pct <= 70
    checks.append(('authentic_range', auth_ok))
    print(f"AUTHENTIC_RESOLVER range: {auth_pct:.1f}% {'PASS' if auth_ok else 'WARNING'}")

    # COUNTERFEIT >= 15%
    cf_pct = 100.0 * class_counts.get('NONRESOLVING_COUNTERFEIT', 0) / n_events
    cf_ok = cf_pct >= 15
    checks.append(('counterfeit_meaningful', cf_ok))
    print(f"NONRESOLVING_COUNTERFEIT: {cf_pct:.1f}% {'PASS' if cf_ok else 'WARNING'}")

    # Total 2323
    total_ok = n_total == 2323
    checks.append(('total_2323', total_ok))
    print(f"Total entries = {n_total}: {'PASS' if total_ok else f'FAIL (expected 2323)'}")

    all_pass = all(ok for _, ok in checks)
    print(f"\nAll verification checks: {'PASS' if all_pass else 'SOME WARNINGS/FAILURES'}")

    # --- Format cross-tabs for JSON ---
    cross_tab_morph_json = {}
    for (ec, mc), count in cross_tab_class_vs_morph.items():
        cross_tab_morph_json[f"{ec}+{mc}"] = count

    cross_tab_grammar_json = {}
    for (ec, gb), count in cross_tab_class_vs_grammar.items():
        cross_tab_grammar_json[f"{ec}+{gb}"] = count

    cross_tab_coherence_json = {}
    for (ec, coh), count in cross_tab_class_vs_coherence.items():
        cross_tab_coherence_json[f"{ec}+{'coherent' if coh else 'incoherent'}"] = count

    # --- Save results ---
    elapsed = (datetime.now(timezone.utc) - t_start).total_seconds()

    output = {
        'metadata': {
            'phase': '578',
            'script': 't0_event_local_classification.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(elapsed, 2),
            'n_events': n_events,
            'n_non_close': n_non_close,
            'n_total_lines': n_total,
            'thresholds': {
                'authentic_burden': AUTHENTIC_BURDEN_THRESHOLD,
                'partial_burden': PARTIAL_BURDEN_THRESHOLD,
                'dv_activity_floor': DV_ACTIVITY_FLOOR,
                'low_burden_floor': LOW_BURDEN_FLOOR,
            },
        },
        'class_distribution': dict(class_counts),
        'distribution_stats': {
            'burden_frac_resolved': {
                'percentiles': percentiles,
                'min': round(burden_sorted[0], 6),
                'max': round(burden_sorted[-1], 6),
                'mean': round(sum(burden_frac_values) / len(burden_frac_values), 6),
            },
        },
        'cross_tabs': {
            'class_vs_morph': cross_tab_morph_json,
            'class_vs_grammar_band': cross_tab_grammar_json,
            'class_vs_coherence': cross_tab_coherence_json,
        },
        'burden_quartile_vs_dye_adv': quartile_summary,
        'per_class_dye_adv': class_dye_adv,
        'verification': {k: v for k, v in checks},
        'per_line_classification': per_line_classification,
    }

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, 't0_event_local_classification.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    print(f"\nSaved to {out_path} ({os.path.getsize(out_path):,} bytes)")
    print(f"Elapsed: {elapsed:.2f}s")


if __name__ == '__main__':
    main()
