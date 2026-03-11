"""
T4: Post-Gate Landscape Remapping
Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE

Remaps Phase 574 T4 landscape using best gate config from T3 (by SSI).
Computes transition matrix, pole analysis, and classification shifts.
"""

import json
import sys
import os
import math
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')


def classify_folio(z_margin, positive_event_fraction):
    """Classify folio using same rules as Phase 574 T4.

    STABLE_AMPLIFIER: z_margin > 0.5 and positive_event_fraction >= 0.9
    FORGIVING_RECIRCULATOR: z_margin < -1.0 or positive_event_fraction < 0.35
    THRESHOLD_DEPENDENT: everything else
    """
    if z_margin > 0.5 and positive_event_fraction >= 0.9:
        return 'STABLE_AMPLIFIER'
    if z_margin < -1.0 or positive_event_fraction < 0.35:
        return 'FORGIVING_RECIRCULATOR'
    return 'THRESHOLD_DEPENDENT'


def main():
    t_start = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 70)
    print("T4: Post-Gate Landscape Remapping")
    print("Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")

    # Phase 574 T4 ungated landscape
    t4_574_path = os.path.join(PROJECT_ROOT, 'phases',
        'COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP', 'results',
        't4_landscape_model.json')
    with open(t4_574_path) as f:
        t4_574 = json.load(f)

    ungated_landscape = t4_574['per_folio_landscape']
    global_margin_mean = t4_574['metadata']['global_margin_mean']
    global_margin_sd = t4_574['metadata']['global_margin_sd']

    # Phase 575 T2 gated results
    with open(os.path.join(RESULTS_DIR, 't2_gated_simulation.json')) as f:
        t2_gated = json.load(f)

    # Phase 575 T3 results (for best config)
    with open(os.path.join(RESULTS_DIR, 't3_packet_authentication_anatomy.json')) as f:
        t3_anatomy = json.load(f)

    best_config = t3_anatomy['best_config_by_SSI']
    print(f"  Best config by SSI: {best_config}")
    print(f"  Ungated folios: {len(ungated_landscape)}")

    gated_folio_results = t2_gated['per_config'].get(best_config, {})

    # ================================================================
    # Remap landscape
    # ================================================================
    print("\n--- Remapping landscape ---")
    per_folio_gated = {}
    transition_matrix = defaultdict(lambda: defaultdict(int))

    for folio, ungated in ungated_landscape.items():
        gated = gated_folio_results.get(folio)

        ungated_class = ungated['classification']
        ungated_margin = ungated['margin']

        if gated is None:
            # No gated result — keep ungated classification
            per_folio_gated[folio] = {
                'ungated_margin': round(ungated_margin, 6),
                'gated_margin': round(ungated_margin, 6),
                'ungated_classification': ungated_class,
                'gated_classification': ungated_class,
                'changed': False,
                'profile': ungated['profile'],
                'gated_advantage': round(ungated_margin, 6),
                'delta_margin': 0.0,
            }
            transition_matrix[ungated_class][ungated_class] += 1
            continue

        # Recompute margin from gated advantage
        gated_advantage = gated['gated_advantage']

        # Recompute positive_event_fraction from band info
        band_info = gated.get('by_band', {})
        total_events = sum(b.get('n_events', 0) for b in band_info.values())
        # Approximate: count events with positive gated DYE as positive
        # We use the gated_advantage as a proxy for the folio-level margin
        gated_margin = gated_advantage

        # z_margin: standardize using global stats from Phase 574
        if global_margin_sd > 0:
            gated_z_margin = (gated_margin - global_margin_mean) / global_margin_sd
        else:
            gated_z_margin = 0.0

        # Use ungated positive_event_fraction as baseline + gated advantage shift
        # Since we can't recompute per-event positive fraction exactly from T2 summary,
        # use the ratio of gated to ungated advantage to adjust
        ungated_pef = ungated['positive_event_fraction']
        if ungated_margin > 0 and gated_margin > 0:
            pef_ratio = min(1.0, gated_margin / max(ungated_margin, 0.001))
            gated_pef = min(1.0, ungated_pef * pef_ratio)
        elif gated_margin <= 0:
            gated_pef = max(0.0, ungated_pef - 0.1)
        else:
            gated_pef = ungated_pef

        gated_class = classify_folio(gated_z_margin, gated_pef)
        changed = gated_class != ungated_class

        per_folio_gated[folio] = {
            'ungated_margin': round(ungated_margin, 6),
            'gated_margin': round(gated_margin, 6),
            'gated_z_margin': round(gated_z_margin, 4),
            'ungated_classification': ungated_class,
            'gated_classification': gated_class,
            'changed': changed,
            'profile': ungated['profile'],
            'gated_advantage': round(gated_advantage, 6),
            'gated_pef': round(gated_pef, 4),
            'delta_margin': round(gated_margin - ungated_margin, 6),
        }
        transition_matrix[ungated_class][gated_class] += 1

    # ================================================================
    # Classification summary
    # ================================================================
    print("\n--- Classification summary ---")
    classes = ['STABLE_AMPLIFIER', 'THRESHOLD_DEPENDENT', 'FORGIVING_RECIRCULATOR']
    classification_summary = {}

    for cls in classes:
        n_ungated = sum(1 for f in per_folio_gated.values()
                        if f['ungated_classification'] == cls)
        n_gated = sum(1 for f in per_folio_gated.values()
                      if f['gated_classification'] == cls)
        classification_summary[cls] = {
            'n_ungated': n_ungated,
            'n_gated': n_gated,
            'delta': n_gated - n_ungated,
        }
        print(f"  {cls}: ungated={n_ungated}, gated={n_gated}, delta={n_gated - n_ungated}")

    # Transition matrix
    print("\n--- Transition matrix ---")
    tm_serializable = {}
    for from_cls in classes:
        tm_serializable[from_cls] = {}
        for to_cls in classes:
            n = transition_matrix[from_cls][to_cls]
            tm_serializable[from_cls][to_cls] = n
            if n > 0:
                print(f"  {from_cls} -> {to_cls}: {n}")

    # ================================================================
    # A2 pole analysis
    # ================================================================
    print("\n--- A2 pole analysis ---")
    a2_forgiving_ungated = sum(
        1 for f in per_folio_gated.values()
        if 'A2' in f['profile'] and f['ungated_classification'] == 'FORGIVING_RECIRCULATOR')
    a2_forgiving_gated = sum(
        1 for f in per_folio_gated.values()
        if 'A2' in f['profile'] and f['gated_classification'] == 'FORGIVING_RECIRCULATOR')
    a1a3_new_forgiving = sum(
        1 for f in per_folio_gated.values()
        if 'A2' not in f['profile']
        and f['ungated_classification'] != 'FORGIVING_RECIRCULATOR'
        and f['gated_classification'] == 'FORGIVING_RECIRCULATOR')

    if a2_forgiving_ungated > 0:
        pole_reduction_pct = (a2_forgiving_ungated - a2_forgiving_gated) / a2_forgiving_ungated * 100
    else:
        pole_reduction_pct = 0.0

    a2_pole_analysis = {
        'n_forgiving_ungated': a2_forgiving_ungated,
        'n_forgiving_gated': a2_forgiving_gated,
        'pole_reduction_pct': round(pole_reduction_pct, 1),
        'a1a3_new_forgiving': a1a3_new_forgiving,
    }
    print(f"  A2 FORGIVING: ungated={a2_forgiving_ungated}, gated={a2_forgiving_gated}, "
          f"reduction={pole_reduction_pct:.1f}%")
    print(f"  A1/A3 new FORGIVING: {a1a3_new_forgiving}")

    # ================================================================
    # Verification
    # ================================================================
    n_total = len(per_folio_gated)
    all_classified = n_total == len(ungated_landscape)
    no_a1a3_forgiving = a1a3_new_forgiving == 0
    forgiving_reduced = (classification_summary['FORGIVING_RECIRCULATOR']['n_gated'] <=
                         classification_summary['FORGIVING_RECIRCULATOR']['n_ungated'])

    verification = {
        'n_folios_classified': n_total,
        'all_classified': all_classified,
        'no_new_a1a3_forgiving': no_a1a3_forgiving,
        'forgiving_reduced_or_stable': forgiving_reduced,
    }
    print(f"\n  Verification: all={all_classified}, no_new_a1a3={no_a1a3_forgiving}, "
          f"forgiving_stable={forgiving_reduced}")

    # ================================================================
    # Output
    # ================================================================
    output = {
        'metadata': {
            'phase': '575',
            'script': 't4_landscape_remap.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
            'best_config_used': best_config,
            'n_folios': n_total,
        },
        'per_folio_gated_landscape': per_folio_gated,
        'transition_matrix': tm_serializable,
        'classification_summary': classification_summary,
        'a2_pole_analysis': a2_pole_analysis,
        'verification': verification,
    }

    out_path = os.path.join(RESULTS_DIR, 't4_landscape_remap.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")
    print(f"Total elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
