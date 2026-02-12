#!/usr/bin/env python3
"""
T1: Structural Fingerprint Compilation
PROCESS_PHENOMENOLOGY_EXCLUSION phase (Tier 4)

Aggregates all quantitative metrics from completed phases into a single
reference JSON + 20-feature binary vector for domain exclusion testing.
"""

import sys
import json
import functools
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
PHASES_DIR = Path(__file__).resolve().parents[2]

# Source directories
DISC = PHASES_DIR / 'DISCRIMINATION_SPACE_DERIVATION' / 'results'
LANE = PHASES_DIR / 'LANE_OSCILLATION_CONTROL_LAW' / 'results'
HAZ = PHASES_DIR / 'HAZARD_CLASS_VULNERABILITY' / 'results'
PP = PHASES_DIR / 'PP_CONSTRAINT_AFFORDANCE_MAP' / 'results'
FP = PHASES_DIR / 'FINGERPRINT_UNIQUENESS' / 'results'


def load_json(path):
    """Load JSON file, return (data, True) or (None, False)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f), True
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  WARNING: Could not load {path}: {e}")
        return None, False


def main():
    print("=" * 70)
    print("T1: STRUCTURAL FINGERPRINT COMPILATION")
    print("=" * 70)

    sources = {}
    missing = []

    # ---- Load all upstream results ----
    source_files = {
        'disc_t1': DISC / 't1_definitive_matrix.json',
        'disc_t2': DISC / 't2_dimensionality_convergence.json',
        'disc_t3': DISC / 't3_structural_decomposition.json',
        'disc_t5': DISC / 't5_synthesis.json',
        'disc_t11': DISC / 't11_hub_residual_structure.json',
        'lane_t1': LANE / 't1_transition_matrices.json',
        'lane_t2': LANE / 't2_hazard_gate.json',
        'lane_t6': LANE / 't6_model_validation.json',
        'lane_t7': LANE / 't7_generative_simulation.json',
        'haz_boundary': HAZ / 'hazard_boundary_architecture.json',
        'haz_exposure': HAZ / 'hazard_exposure_anatomy.json',
        'pp_t1': PP / 't1_eigenvector_property_atlas.json',
        'pp_t2': PP / 't2_geometric_region_profiling.json',
        'pp_t4': PP / 't4_incompatibility_topology.json',
        'pp_t5': PP / 't5_physical_affordance_mapping.json',
        'pp_t6': PP / 't6_c3c4_discriminant_anatomy.json',
        'pp_t7': PP / 't7_contextual_eigenvector_annotation.json',
        'fp_t5': FP / 't5_joint.json',
    }

    for key, path in source_files.items():
        data, ok = load_json(path)
        if ok:
            sources[key] = data
            print(f"  Loaded: {key}")
        else:
            missing.append(key)

    print(f"\nLoaded {len(sources)}/{len(source_files)} source files")
    if missing:
        print(f"Missing: {missing}")

    # ---- Build structured fingerprint ----
    fingerprint = {}

    # Automaton structure
    fingerprint['automaton'] = {
        'instruction_classes': 49,
        'states': 6,
        'state_compression': '8.2x (49 -> 6)',
        'forbidden_transitions': 17,
        'hazard_classes': 5,
        'hazard_distribution': {
            'PHASE_ORDERING': 0.41,
            'COMPOSITION_JUMP': 0.24,
            'CONTAINMENT_TIMING': 0.24,
            'RATE_MISMATCH': 0.06,
            'ENERGY_OVERSHOOT': 0.06,
        },
        'hazard_involved_classes': '6/49 (12.2%)',
        'hazard_compliance_rate': 1.0,
        'hazard_asymmetry_rate': 0.65,
        'convergence_target': 'STATE-C',
        'terminal_state_c_pct': 0.578,
        'provenance': ['C109', 'C110', 'C111', 'C121', 'C124', 'C541', 'C789', 'C976'],
    }

    # Kernel structure
    fingerprint['kernel'] = {
        'operators': {
            'k': 'ENERGY_MODULATOR',
            'h': 'PHASE_MANAGER',
            'e': 'STABILITY_ANCHOR',
        },
        'e_recovery_rate': 0.547,
        'k_to_e_elevation': 4.32,
        'h_to_e_elevation': 7.00,
        'e_to_h_suppressed': True,
        'e_to_k_suppressed': True,
        'kernel_boundary_adjacent': True,
        'provenance': ['C089', 'C103', 'C104', 'C105', 'C107', 'C521', 'C522'],
    }

    # Lane oscillation
    lane_data = {}
    if 'lane_t1' in sources:
        lt1 = sources['lane_t1']
        lane_data['alternation_rate'] = lt1.get('alternation_rate', 0.554)
        filt = lt1.get('filtered_matrix', {})
        lane_data['qo_to_chsh'] = filt.get('QO_to_CHSH', 0.578)
        lane_data['chsh_to_qo'] = filt.get('CHSH_to_QO', 0.535)
    if 'lane_t2' in sources:
        lt2 = sources['lane_t2']
        lane_data['hazard_gate_chsh_fraction'] = lt2.get('post_hazard_CHSH_fraction', 0.752)
        lane_data['hazard_gate_decay_tokens'] = 1
    if 'lane_t6' in sources:
        lt6 = sources['lane_t6']
        agg = lt6.get('aggregate_BIC', {})
        lane_data['bic_best_model'] = 'markov_haz'
        lane_data['model_parameters'] = 12
        lane_data['bic_markov_haz'] = agg.get('markov_haz', 9166.3)
    fingerprint['lane_oscillation'] = {
        'model_type': 'first_order_markov_plus_hazard_gate',
        'parameters': 12,
        'alternation_rate': lane_data.get('alternation_rate', 0.554),
        'hazard_gate_chsh_fraction': lane_data.get('hazard_gate_chsh_fraction', 0.752),
        'hazard_gate_decay_tokens': 1,
        'bic_best_model': 'markov_haz',
        'section_variation': True,
        'provenance': ['C643', 'C644', 'C645', 'C650', 'C966'],
    }

    # Discrimination space
    disc_data = {}
    if 'disc_t1' in sources:
        dt1 = sources['disc_t1']
        disc_data['n_compatible_pct'] = dt1.get('n_compatible_pct', 2.2)
        eig = dt1.get('eigenspectrum', {})
        disc_data['leading_eigenvalue'] = eig.get('leading', 81.98)
    if 'disc_t5' in sources:
        dt5 = sources['disc_t5']
        disc_data['dimensionality'] = dt5.get('recommended_D', 101)
        disc_data['effective_rank'] = dt5.get('effective_rank', 344)
    if 'disc_t3' in sources:
        dt3 = sources['disc_t3']
        disc_data['prefix_enrichment'] = dt3.get('prefix_block_enrichment', 3.92)
    fingerprint['discrimination_space'] = {
        'n_middles': 972,
        'dimensionality': disc_data.get('dimensionality', 101),
        'effective_rank': disc_data.get('effective_rank', 344),
        'leading_eigenvalue': disc_data.get('leading_eigenvalue', 81.98),
        'compatibility_pct': disc_data.get('n_compatible_pct', 2.2),
        'prefix_enrichment': disc_data.get('prefix_enrichment', 3.92),
        'opaque_eigenvectors': 27,
        'total_analyzed_eigenvectors': 29,
        'provenance': ['C475', 'C506', 'C983', 'C987', 'C991'],
    }

    # Transitivity
    fingerprint['transitivity'] = {
        'clustering_coefficient': 0.873,
        'z_score_vs_config_model': 136.9,
        'z_score_vs_erdos_renyi': 286.7,
        'provenance': ['C983'],
    }

    # Affordance mapping
    if 'pp_t5' in sources:
        pt5 = sources['pp_t5']
        fingerprint['affordance_mapping'] = {
            'n_clusters': pt5.get('n_clusters', 5),
            'families': list(pt5.get('family_distribution', {}).keys()),
            'med_plus_coverage': pt5.get('med_plus_coverage_pct', 0.639),
            'exclusion_explanation_rate': pt5.get('exclusion_explanation_rate', 1.0),
            'mapping_verdict': pt5.get('verdict', 'COHERENT_MAPPING'),
        }

    # Uniqueness
    if 'fp_t5' in sources:
        fpt5 = sources['fp_t5']
        fingerprint['uniqueness'] = {
            'discriminating_features': [
                k for k, v in fpt5.get('properties', {}).items()
                if v.get('discriminating', False)
            ],
            'non_discriminating_features': [
                k for k, v in fpt5.get('properties', {}).items()
                if not v.get('discriminating', False)
            ],
            'fisher_p': fpt5.get('joint_probability', {}).get('fisher_p', 7.67e-8),
            'overall_verdict': fpt5.get('overall_verdict', 'UNCOMMON'),
        }

    # Program structure
    fingerprint['program_structure'] = {
        'folio_is_program': True,
        'line_is_control_block': True,
        'link_density': 0.132,
        'energy_initial_enrichment': 0.45,
        'energy_final_enrichment': 0.50,
        'flow_final_enrichment': 1.65,
        'design_asymmetry': 'hazard_clamped_recovery_free',
        'recovery_free_features': '10/12',
        'provenance': ['C178', 'C357', 'C458', 'C556', 'C636'],
    }

    # Hazard details
    if 'haz_boundary' in sources:
        hb = sources['haz_boundary']
        fingerprint['hazard_enforcement'] = {
            'forbidden_observed': hb.get('forbidden_neighbors_actual_occurrences', 0),
            'near_misses': hb.get('near_miss_total', 114),
            'buffer_positions': hb.get('buffer_positions_total', 481),
            'hazard_density_mean': hb.get('hazard_density_mean', 0.251),
        }

    # ---- Build 20-feature binary vector for T4 ----
    feature_vector = {
        'F01_1token_response_time': {
            'value': True,
            'evidence': 'Hazard gate KL returns to baseline at offset+2, gate duration 1 token',
            'source': 'LANE_OSCILLATION T2, C967',
        },
        'F02_first_order_markov_sufficient': {
            'value': True,
            'evidence': 'BIC selects markov_haz (12 params) over full model (18 params)',
            'source': 'LANE_OSCILLATION T6, C966',
        },
        'F03_categorical_not_numeric': {
            'value': True,
            'evidence': 'No ratio encoding (C287-C290), no magnitude encoding, discrete MIDDLE variants',
            'source': 'C287, C288, C289, C290, C469',
        },
        'F04_high_dimensional_incompatibility': {
            'value': True,
            'evidence': '101D discrimination space, effective rank 344, 972 MIDDLEs',
            'source': 'DISCRIMINATION_SPACE T1/T5, C987',
        },
        'F05_strong_transitivity': {
            'value': True,
            'evidence': 'Clustering coefficient 0.873, z=+136.9 vs configuration model',
            'source': 'C983',
        },
        'F06_hazard_asymmetry': {
            'value': True,
            'evidence': '65% of forbidden transitions are asymmetric (directed hazards)',
            'source': 'C111, C789',
        },
        'F07_absorbing_stabilization_state': {
            'value': True,
            'evidence': 'e-operator absorbs 54.7% of recovery paths, one-way valve k,h->e',
            'source': 'C105, C521',
        },
        'F08_lane_oscillation': {
            'value': True,
            'evidence': 'QO/CHSH alternation at 55.4%, post-hazard CHSH spike to 75.2%',
            'source': 'C643, C645, C966',
        },
        'F09_energy_medial_concentration': {
            'value': True,
            'evidence': 'ENERGY operators 0.45x at initial, 0.50x at final (boundary avoidance)',
            'source': 'C556',
        },
        'F10_recovery_unconditionally_free': {
            'value': True,
            'evidence': '10/12 recovery features REGIME-independent, escape is folio-specific design',
            'source': 'C636, C635',
        },
        'F11_universal_grammar': {
            'value': True,
            'evidence': '49 classes, 100% coverage across 83 folios, 0 exceptions',
            'source': 'C124',
        },
        'F12_phase_ordering_dominant_hazard': {
            'value': True,
            'evidence': 'PHASE_ORDERING is 41% of hazard transitions (7/17), largest class',
            'source': 'C109, C110',
        },
        'F13_convergent_monostate': {
            'value': True,
            'evidence': '57.8% of programs terminate in STATE-C, convergent attractor',
            'source': 'C079, C323',
        },
        'F14_exactly_5_hazard_classes': {
            'value': True,
            'evidence': '5 failure classes covering 17 forbidden transitions in 6 instruction classes',
            'source': 'C109, C541',
        },
        'F15_closed_loop_not_batch': {
            'value': True,
            'evidence': 'Circulatory: line resets (C670), no long-range carry, mixing time 1.1 tokens',
            'source': 'C670, C966',
        },
        'F16_line_boundary_memory_reset': {
            'value': True,
            'evidence': 'Hard line resets, cross-line MI = 0.52 bits (below null Markov 0.72-0.77)',
            'source': 'C670, FINGERPRINT_UNIQUENESS F10',
        },
        'F17_link_monitoring_phase': {
            'value': True,
            'evidence': 'LINK density 13.2%, LINK mean position 0.476 (early-line bias)',
            'source': 'C609, C813',
        },
        'F18_e_recovery_dominance': {
            'value': True,
            'evidence': '54.7% recovery paths through e, kernel exit rate 98-100%',
            'source': 'C105, C634',
        },
        'F19_folio_vocabulary_uniqueness': {
            'value': True,
            'evidence': 'Each folio has unique MIDDLE vocabulary, program = folio',
            'source': 'C178, C531',
        },
        'F20_design_asymmetry': {
            'value': True,
            'evidence': 'Hazard topology clamped (same 17 in all folios), recovery free (varies per folio)',
            'source': 'C458, C636',
        },
    }

    # ---- Compile result ----
    verdict = 'COMPILED' if len(missing) == 0 else 'INCOMPLETE'

    results = {
        'test': 'T1_structural_fingerprint_compilation',
        'n_source_files_loaded': len(sources),
        'n_source_files_total': len(source_files),
        'missing_sources': missing,
        'fingerprint': fingerprint,
        'feature_vector': feature_vector,
        'n_features': len(feature_vector),
        'verdict': verdict,
    }

    # ---- Save ----
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't1_structural_fingerprint.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_path}")

    # ---- Summary ----
    print(f"\n{'=' * 70}")
    print(f"VERDICT: {verdict}")
    print(f"Sources: {len(sources)}/{len(source_files)} loaded")
    print(f"Fingerprint sections: {list(fingerprint.keys())}")
    print(f"Feature vector: {len(feature_vector)} features (all True for distillation)")
    if missing:
        print(f"Missing: {missing}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
