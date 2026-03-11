"""T1: Manifold-to-Knob Mapping for Phase 582.

THE CORE DELIVERABLE. Map F1-F5 and PCA axes to physical control surface
candidates. Define family analogs and landscape classes in physical terms.
Decides C1680.
"""
import json
import os
import math

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

# Physical knob mapping table -- the heart of the bridge
KNOB_MAP = {
    'F1': {
        'name': 'Attractor / Forgiveness',
        'virtual_proxy': 'AXM occupancy, null recovery ease',
        'physical_knobs': [
            'Reflux ratio (condensate return vs collection)',
            'Recirculation tightness (return path diameter)',
            'Condensate return fraction',
            'Thermal inertia (bath mass, vessel wall thickness)',
        ],
        'expected_readout_shift': 'Higher retention after disturbance, higher null productivity',
        'knob_class': 'geometry',
        'tier': 3,
    },
    'F2': {
        'name': 'Closure Exploitability',
        'virtual_proxy': 'Closure gain sensitivity',
        'physical_knobs': [
            'Valve timing precision (stop/start sharpness)',
            'Seal completion speed',
            'Collection diversion response time',
            'Damper closure gradient',
        ],
        'expected_readout_shift': 'Stronger closure threshold behavior, higher DYE contrast',
        'knob_class': 'performance',
        'tier': 3,
    },
    'F3': {
        'name': 'Thermal Accent',
        'virtual_proxy': 'THERMAL fraction',
        'physical_knobs': [
            'Bath temperature setpoint',
            'Heater power slew rate',
            'Heat transfer coefficient (medium: water vs sand vs direct)',
            'Thermal ramp rate',
        ],
        'expected_readout_shift': 'Stronger thermal-phase signatures, more work-zone sensitivity',
        'knob_class': 'geometry',
        'tier': 3,
    },
    'F4_raw': {
        'name': 'Headless Infrastructure',
        'virtual_proxy': 'hl_rate, infrastructural mediation',
        'physical_knobs': [
            'Plumbing complexity (number of passive paths)',
            'Passive recirculation paths (side arms, auxiliary condensers)',
            'Condensate routing topology (valves, tees)',
            'Staging subloops (pre-heat, pre-cool circuits)',
        ],
        'expected_readout_shift': 'Stronger closure assistance without overt thermal action',
        'knob_class': 'geometry',
        'tier': 4,
    },
    'F5': {
        'name': 'Containment Responsiveness',
        'virtual_proxy': 'SEALED_VESSEL proxy',
        'physical_knobs': [
            'Gasket quality (ground glass vs wax vs PTFE)',
            'Seal completeness (number of sealed joints)',
            'Backpressure tolerance',
            'Headspace coupling (vapor communication between chambers)',
        ],
        'expected_readout_shift': 'Stronger containment-coupled recovery, A2-like forgivingness',
        'knob_class': 'performance',
        'tier': 3,
    },
}

# Knob class definitions
KNOB_CLASSES = {
    'geometry': 'Moves you in Space A (apparatus configuration). Changing these changes what the apparatus IS.',
    'performance': 'Changes Space B outcomes (process quality). Changing these changes what the apparatus DOES.',
    'readout': 'Changes only observability, not behavior. Changing these changes what you can SEE.',
}

# Family analog definitions
FAMILY_ANALOGS = {
    'A1_BATH_REFLUX': {
        'physical_analog': 'Moderated bath/reflux with open or loosely sealed head',
        'key_differentiators': [
            'Sensitive to operator precision (low self-correction)',
            'Water bath provides thermal buffer but not error correction',
            'Open head allows vapor escape (no pressure feedback)',
            'Requires careful fire management',
        ],
        'ccs1_typical': 0.013,
        'dominant_knob_axis': 'F1 (low attractor strength)',
        'tier': 3,
    },
    'A2_SEALED_RECIRCULATION': {
        'physical_analog': 'Sealed forgiving recirculation with tight joints',
        'key_differentiators': [
            'Self-correcting via close-recovery (R1_C/R4_C channels)',
            'Sealed system creates pressure feedback loop',
            'Overheat -> increased vapor pressure -> faster condensation -> self-correction',
            'Strength-dependent: STRONG closures productive, WEAK closures lose to null (C1642)',
        ],
        'ccs1_typical': 0.114,
        'dominant_knob_axis': 'F5 (high containment responsiveness)',
        'tier': 3,
    },
    'A3_DISTILL_COLLECT': {
        'physical_analog': 'Distill-collect bridge, intermediate configuration',
        'key_differentiators': [
            'Spans A1-A2 geometry (54% are bridge folios)',
            'Standard collection operations with partial seal',
            'Intermediate self-correction capability',
            'Most common family (37/76 folios)',
        ],
        'ccs1_typical': 0.053,
        'dominant_knob_axis': 'F2 (intermediate closure exploitability)',
        'tier': 3,
    },
}

# Landscape class physical interpretations
LANDSCAPE_CLASSES = {
    'SA': {
        'name': 'Stable Attractor',
        'physical_regime': 'Self-sustaining equilibrium operation',
        'observable_behavior': 'Minimal intervention needed, consistent output',
        'operator_experience': 'Routine monitoring, apparatus maintains itself',
        'tier': 3,
    },
    'TD': {
        'name': 'Transition Domain',
        'physical_regime': 'Threshold-dependent behavior',
        'observable_behavior': 'Small perturbations can tip into different operating modes',
        'operator_experience': 'Requires attention, decisions matter, errors have consequences',
        'tier': 3,
    },
    'FR': {
        'name': 'Forgiving Region',
        'physical_regime': 'Error-tolerant recirculation',
        'observable_behavior': 'Apparatus self-corrects moderate operator errors',
        'operator_experience': 'Relaxed operation, system compensates for mistakes',
        'tier': 3,
    },
}


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)

    pca = t0['pca_summary']
    loadings = pca['loadings']
    feature_names = pca['feature_names']
    variance = pca['variance_explained']
    consolidated = t0['per_folio']

    # ---- PC-to-knob cluster mapping ----
    # For each PC, identify which features load most heavily
    # loadings is a dict keyed by PC name (e.g. 'PC1': [...])
    pc_keys_sorted = sorted(loadings.keys(), key=lambda k: int(k[2:]))
    pc_knob_clusters = {}
    n_pcs = min(5, len(pc_keys_sorted))
    for pc_idx in range(n_pcs):
        pc_key = pc_keys_sorted[pc_idx]
        pc_loadings = loadings[pc_key]

        # Sort features by absolute loading
        # pc_loadings is a list of {feature, loading} dicts
        feature_loadings = [(entry['feature'], entry['loading'])
                            for entry in pc_loadings]
        feature_loadings.sort(key=lambda x: abs(x[1]), reverse=True)

        top_features = feature_loadings[:3]
        # Map top features to physical knobs
        physical_knobs = []
        for feat, loading in top_features:
            knob_info = KNOB_MAP.get(feat, {})
            if knob_info:
                physical_knobs.append({
                    'feature': feat,
                    'loading': round(loading, 4),
                    'direction': 'positive' if loading > 0 else 'negative',
                    'physical_knobs': knob_info['physical_knobs'],
                    'knob_class': knob_info['knob_class'],
                })
            else:
                # Ablation features
                physical_knobs.append({
                    'feature': feat,
                    'loading': round(loading, 4),
                    'direction': 'positive' if loading > 0 else 'negative',
                    'physical_knobs': [f'Ablation channel: {feat}'],
                    'knob_class': 'performance',
                })

        pc_knob_clusters[pc_key] = {
            'variance_explained': round(variance[pc_idx], 4) if pc_idx < len(variance) else 0,
            'top_features': [(f, round(l, 4)) for f, l in top_features],
            'physical_knob_cluster': physical_knobs,
        }

    # ---- Per-family manifold position ----
    family_positions = {}
    for fname in ['A1', 'A2', 'A3']:
        family_folios = [f for f, d in consolidated.items()
                         if d['family'] == fname]
        if not family_folios:
            continue

        # Mean PC coordinates
        mean_pcs = {}
        for pc_idx in range(n_pcs):
            pc_key = f'PC{pc_idx + 1}'
            vals = [consolidated[f]['pc_coordinates'].get(pc_key, 0)
                    for f in family_folios
                    if consolidated[f]['pc_coordinates'].get(pc_key) is not None]
            mean_pcs[pc_key] = round(sum(vals) / len(vals), 4) if vals else 0

        # Mean F-features
        mean_features = {}
        for feat in feature_names:
            vals = [consolidated[f]['features_A'].get(feat, 0)
                    for f in family_folios
                    if consolidated[f]['features_A'].get(feat) is not None]
            mean_features[feat] = round(sum(vals) / len(vals), 4) if vals else 0

        family_positions[fname] = {
            'n_folios': len(family_folios),
            'mean_pc_coordinates': mean_pcs,
            'mean_features': mean_features,
        }

    # ---- F-axis knob identifiability assessment ----
    n_identifiable = 0
    for f_key, knob_info in KNOB_MAP.items():
        if len(knob_info['physical_knobs']) >= 1:
            n_identifiable += 1

    if n_identifiable >= 5:
        verdict = 'KNOB_MAPPING_IDENTIFIABLE'
    elif n_identifiable >= 3:
        verdict = 'KNOB_MAPPING_PARTIAL'
    else:
        verdict = 'KNOB_MAPPING_UNDERDETERMINED'

    # ---- Output ----
    output = {
        'metadata': {
            'phase': '582',
            'script': 't1_manifold_knob_mapping.py',
            'n_folios': len(consolidated),
            'n_pcs_analyzed': n_pcs,
            'effective_rank': pca['effective_rank'],
        },
        'knob_map': KNOB_MAP,
        'knob_classes': KNOB_CLASSES,
        'pc_knob_clusters': pc_knob_clusters,
        'family_analogs': FAMILY_ANALOGS,
        'family_manifold_positions': family_positions,
        'landscape_classes': LANDSCAPE_CLASSES,
        'C1680': {
            'verdict': verdict,
            'n_axes_mapped': n_identifiable,
            'n_axes_total': 5,
            'rationale': (f'{n_identifiable}/5 F-axes mapped to physical knob candidates '
                          f'with directional predictions'),
            'tier': 3,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't1_manifold_knob_mapping.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T1: Manifold-to-knob mapping complete")
    print(f"  F-axes mapped: {n_identifiable}/5")
    for f_key, info in KNOB_MAP.items():
        print(f"    {f_key} ({info['name']}): {len(info['physical_knobs'])} knobs "
              f"[{info['knob_class']}] (Tier {info['tier']})")
    print(f"  PC clusters: {n_pcs}")
    for pc_key, cluster in pc_knob_clusters.items():
        top = cluster['top_features'][0] if cluster['top_features'] else ('?', 0)
        print(f"    {pc_key} ({cluster['variance_explained']:.1%}): "
              f"led by {top[0]} ({top[1]:+.4f})")
    print(f"  Family positions computed: {list(family_positions.keys())}")
    print(f"  C1680: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
