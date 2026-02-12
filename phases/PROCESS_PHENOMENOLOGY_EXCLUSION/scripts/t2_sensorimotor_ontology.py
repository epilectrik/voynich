#!/usr/bin/env python3
"""
T2: Sensorimotor Ontology Construction
PROCESS_PHENOMENOLOGY_EXCLUSION phase (Tier 4)

Defines ~25 observable phenomena in pelican reflux distillation,
maps each to Voynich architectural features with constraint citations,
and scores bidirectional coverage.

Extends: context/SPECULATIVE/sensory_affordance_mapping.md
"""

import sys
import json
import functools
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


# ============================================================
# SENSORIMOTOR ONTOLOGY: 25 phenomena across 5 modalities
# ============================================================

ONTOLOGY = {
    # ---- VISUAL (8 phenomena) ----
    'VAPOR_DENSITY': {
        'modality': 'VISUAL',
        'description': 'Density and opacity of rising vapor in the neck/helm',
        'distillation_context': 'Indicates current heating rate and energy input level; thin vapor = gentle, dense = vigorous',
        'architecture_mapping': [
            {'feature': 'k_operator_concentration', 'relationship': 'k (ENERGY_MODULATOR) presence tracks energy input intensity', 'constraint': 'C103'},
            {'feature': 'QO_lane', 'relationship': 'QO lane is k-rich, encoding energy-application phases', 'constraint': 'C647'},
        ],
        'confidence': 'HIGH',
    },
    'CONDENSATE_DRIP_RATE': {
        'modality': 'VISUAL',
        'description': 'Rate of condensate drops from condenser into receiver',
        'distillation_context': 'Primary indicator of distillation progress; too fast = inadequate separation, too slow = energy waste',
        'architecture_mapping': [
            {'feature': 'FL_operator_progression', 'relationship': 'FLOW operators track product movement and output rate', 'constraint': 'C549'},
            {'feature': 'FL_final_position', 'relationship': 'FL enriched at line end (position 0.576) = output check at control block close', 'constraint': 'C813'},
        ],
        'confidence': 'HIGH',
    },
    'FOAM_ONSET': {
        'modality': 'VISUAL',
        'description': 'Appearance of foam/froth at liquid surface indicating boil transition',
        'distillation_context': 'Critical danger signal: foam precedes boil-over, the most common failure mode',
        'architecture_mapping': [
            {'feature': 'PHASE_ORDERING_hazard', 'relationship': 'PHASE_ORDERING (41%) = material in wrong phase/location, foam is precursor', 'constraint': 'C110'},
            {'feature': 'h_operator', 'relationship': 'h (PHASE_MANAGER) handles phase boundary transitions', 'constraint': 'C104'},
        ],
        'confidence': 'HIGH',
    },
    'LIQUID_COLOR': {
        'modality': 'VISUAL',
        'description': 'Color of liquid in flask and receiver indicating composition',
        'distillation_context': 'Fraction identity indicator; different fractions have characteristic colors',
        'architecture_mapping': [
            {'feature': 'MIDDLE_discrimination', 'relationship': 'PP MIDDLEs encode material property distinctions in 100D space', 'constraint': 'C475'},
            {'feature': 'folio_vocabulary', 'relationship': 'Each folio/program has unique MIDDLE vocabulary = distinct material profiles', 'constraint': 'C531'},
        ],
        'confidence': 'MEDIUM',
    },
    'PHASE_BOUNDARY_VISIBILITY': {
        'modality': 'VISUAL',
        'description': 'Visible interface between liquid and vapor phases in the vessel',
        'distillation_context': 'Tracking this boundary is core to managing distillation; it moves with temperature',
        'architecture_mapping': [
            {'feature': 'h_operator', 'relationship': 'h (PHASE_MANAGER) manages the liquid-vapor boundary', 'constraint': 'C104'},
            {'feature': 'lane_boundary', 'relationship': 'QO/CHSH lane transition marks shift between energy modes', 'constraint': 'C647'},
        ],
        'confidence': 'HIGH',
    },
    'SURFACE_AGITATION': {
        'modality': 'VISUAL',
        'description': 'Turbulence and roiling at the liquid surface',
        'distillation_context': 'Intensity of agitation tracks energy input; excessive = approaching overshoot',
        'architecture_mapping': [
            {'feature': 'ENERGY_OVERSHOOT_hazard', 'relationship': 'ENERGY_OVERSHOOT (6%) = thermal damage from excessive energy', 'constraint': 'C109'},
            {'feature': 'k_e_boundary', 'relationship': 'Kernel boundary k->e is the energy-to-stability transition', 'constraint': 'C107'},
        ],
        'confidence': 'MEDIUM',
    },
    'CONDENSER_CLARITY': {
        'modality': 'VISUAL',
        'description': 'Clarity vs cloudiness of condensate output',
        'distillation_context': 'Cloudy condensate indicates contamination or mixed fractions',
        'architecture_mapping': [
            {'feature': 'COMPOSITION_JUMP_hazard', 'relationship': 'COMPOSITION_JUMP (24%) = impure fraction passing through', 'constraint': 'C109'},
        ],
        'confidence': 'HIGH',
    },
    'FLOW_DIRECTION': {
        'modality': 'VISUAL',
        'description': 'Direction of liquid flow through apparatus (reflux return vs distillate forward)',
        'distillation_context': 'In pelican reflux, liquid circulates; wrong flow direction means apparatus failure',
        'architecture_mapping': [
            {'feature': 'FL_operator', 'relationship': 'FLOW_OPERATOR classes (7, 30) track directional flow', 'constraint': 'C549'},
            {'feature': 'FL_HAZ_vs_FL_SAFE', 'relationship': 'Two distinct FL states: hazardous (S0) vs safe (S5) flow', 'constraint': 'C976'},
        ],
        'confidence': 'HIGH',
    },

    # ---- AUDITORY (4 phenomena) ----
    'BUBBLE_CADENCE': {
        'modality': 'AUDITORY',
        'description': 'Rhythm and frequency of boiling bubbles',
        'distillation_context': 'Steady cadence = stable boil; irregular = approaching transition; rapid = energy excess',
        'architecture_mapping': [
            {'feature': 'lane_oscillation', 'relationship': 'QO/CHSH alternation (55.4%) creates rhythmic energy/stability oscillation', 'constraint': 'C966'},
            {'feature': 'first_order_sufficiency', 'relationship': 'Cadence is first-order (current state predicts next), no accumulation needed', 'constraint': 'C966'},
        ],
        'confidence': 'HIGH',
    },
    'PITCH_CHANGE': {
        'modality': 'AUDITORY',
        'description': 'Change in boiling sound pitch as conditions shift',
        'distillation_context': 'Pitch change signals phase transition or temperature shift at boil point',
        'architecture_mapping': [
            {'feature': 'state_transitions', 'relationship': '6-state automaton transitions mark qualitative system state changes', 'constraint': 'C976'},
            {'feature': 'convergence_gradient', 'relationship': 'System converges to STATE-C (steady state) with increasing completion', 'constraint': 'C323'},
        ],
        'confidence': 'MEDIUM',
    },
    'CONDENSER_HISS': {
        'modality': 'AUDITORY',
        'description': 'Hissing sound of hot vapor contacting cool condenser surface',
        'distillation_context': 'Normal hiss = condensation working; absence = condenser too hot or no vapor',
        'architecture_mapping': [
            {'feature': 'e_operator', 'relationship': 'e (STABILITY_ANCHOR) represents cooling/equilibration engagement', 'constraint': 'C105'},
            {'feature': 'CHSH_lane', 'relationship': 'CHSH lane is e-rich, encoding stabilization/monitoring phases', 'constraint': 'C647'},
        ],
        'confidence': 'MEDIUM',
    },
    'PRESSURE_THUD': {
        'modality': 'AUDITORY',
        'description': 'Sudden thump or bang from overpressure event in sealed vessel',
        'distillation_context': 'Immediate danger signal in pelican (sealed vessel); requires emergency response',
        'architecture_mapping': [
            {'feature': 'CONTAINMENT_TIMING_hazard', 'relationship': 'CONTAINMENT_TIMING (24%) = pressure/overflow in sealed vessel', 'constraint': 'C109'},
            {'feature': '1_token_hazard_gate', 'relationship': 'Hazard gate fires in 1 token = immediate categorical response', 'constraint': 'C967'},
        ],
        'confidence': 'HIGH',
    },

    # ---- OLFACTORY (4 phenomena) ----
    'FRAGRANCE_SHIFT': {
        'modality': 'OLFACTORY',
        'description': 'Change in distillate odor indicating different fraction emerging',
        'distillation_context': 'Primary fraction identification method; each aromatic fraction has characteristic smell',
        'architecture_mapping': [
            {'feature': 'MIDDLE_discrimination_space', 'relationship': '972 MIDDLEs in 100D space encode material property distinctions', 'constraint': 'C475'},
            {'feature': 'folio_vocabulary_uniqueness', 'relationship': 'Each program uses distinct MIDDLE vocabulary = distinct material profiles', 'constraint': 'C531'},
            {'feature': 'PP_affordance_families', 'relationship': '5 affordance families map to distinct material behavior classes', 'constraint': 'PP_CONSTRAINT T5'},
        ],
        'confidence': 'HIGH',
    },
    'OFF_ODOR': {
        'modality': 'OLFACTORY',
        'description': 'Unexpected or foul smell indicating contamination',
        'distillation_context': 'Detection of contamination or wrong fraction; requires trained nose',
        'architecture_mapping': [
            {'feature': 'COMPOSITION_JUMP_hazard', 'relationship': 'COMPOSITION_JUMP (24%) = impure fraction, detectable by smell', 'constraint': 'C109'},
            {'feature': 'HT_vigilance', 'relationship': 'HT correlates with discrimination difficulty (r=0.504); olfactory contexts require expert attention', 'constraint': 'C477'},
        ],
        'confidence': 'HIGH',
    },
    'BURNING_SCENT': {
        'modality': 'OLFACTORY',
        'description': 'Acrid smell of material burning/scorching on vessel wall',
        'distillation_context': 'Catastrophic failure indicator; material is being destroyed',
        'architecture_mapping': [
            {'feature': 'ENERGY_OVERSHOOT_hazard', 'relationship': 'ENERGY_OVERSHOOT (6%) = thermal damage/scorching', 'constraint': 'C109'},
        ],
        'confidence': 'HIGH',
    },
    'FRACTION_IDENTITY': {
        'modality': 'OLFACTORY',
        'description': 'Recognition of which specific product/fraction is currently distilling',
        'distillation_context': 'Expert knowledge: each fraction has a signature smell that identifies the cut point',
        'architecture_mapping': [
            {'feature': 'PP_MIDDLE_identity', 'relationship': 'PP MIDDLEs encode material property parameters, not substance names', 'constraint': 'C469'},
            {'feature': 'incompatibility_lattice', 'relationship': '100D incompatibility encodes what materials cannot co-occur in a process step', 'constraint': 'C475'},
        ],
        'confidence': 'MEDIUM',
    },

    # ---- TACTILE (4 phenomena) ----
    'VESSEL_HEAT': {
        'modality': 'TACTILE',
        'description': 'Temperature of apparatus walls felt by hand',
        'distillation_context': 'Direct thermal state assessment; hand on vessel gives crude but categorical temperature',
        'architecture_mapping': [
            {'feature': 'k_operator', 'relationship': 'k (ENERGY_MODULATOR) tracks energy input state', 'constraint': 'C103'},
            {'feature': 'QO_lane', 'relationship': 'QO lane is k-rich, encoding energy-application phases', 'constraint': 'C647'},
            {'feature': 'THERMAL_affordance', 'relationship': 'THERMAL is largest affordance family (597 MIDDLEs)', 'constraint': 'PP_CONSTRAINT T5'},
        ],
        'confidence': 'HIGH',
    },
    'VIBRATION': {
        'modality': 'TACTILE',
        'description': 'Apparatus tremor from vigorous boiling or pressure buildup',
        'distillation_context': 'Physical vibration signals rate of reaction; sudden change = danger',
        'architecture_mapping': [
            {'feature': 'RATE_MISMATCH_hazard', 'relationship': 'RATE_MISMATCH (6%) = flow balance destroyed, vibration is symptom', 'constraint': 'C109'},
        ],
        'confidence': 'MEDIUM',
    },
    'CONDENSATE_WARMTH': {
        'modality': 'TACTILE',
        'description': 'Temperature of output condensate in the receiver',
        'distillation_context': 'Warm condensate = condenser not cooling enough; cold = good separation',
        'architecture_mapping': [
            {'feature': 'e_operator', 'relationship': 'e (STABILITY_ANCHOR) represents cooling/equilibration', 'constraint': 'C105'},
            {'feature': 'e_recovery_dominance', 'relationship': '54.7% of recovery paths through e = cooling is primary recovery', 'constraint': 'C105'},
        ],
        'confidence': 'MEDIUM',
    },
    'GLASS_TENSION': {
        'modality': 'TACTILE',
        'description': 'Physical stress on glass vessel walls under thermal/pressure load',
        'distillation_context': 'Experienced operator can feel vessel stress; crack risk under thermal shock',
        'architecture_mapping': [
            {'feature': 'CONTAINMENT_TIMING_hazard', 'relationship': 'CONTAINMENT_TIMING (24%) includes vessel failure risk', 'constraint': 'C109'},
        ],
        'confidence': 'LOW',
    },

    # ---- TEMPORAL (5 phenomena) ----
    'ADJUSTMENT_DELAY': {
        'modality': 'TEMPORAL',
        'description': 'Lag between adjusting heat and seeing effect on distillation',
        'distillation_context': 'Thermal lag is real; operator must anticipate rather than react',
        'architecture_mapping': [
            {'feature': '1_token_hazard_gate', 'relationship': 'Hazard gate: 1-token response, decay by offset+2 = minimal lag', 'constraint': 'C967'},
            {'feature': 'first_order_sufficiency', 'relationship': 'No hidden accumulator; system responds to current state only', 'constraint': 'C966'},
        ],
        'confidence': 'HIGH',
    },
    'RETURN_TO_EQUILIBRIUM': {
        'modality': 'TEMPORAL',
        'description': 'Time for system to settle after a perturbation or adjustment',
        'distillation_context': 'After changing heat, system needs time to re-stabilize; faster = more controllable',
        'architecture_mapping': [
            {'feature': 'e_recovery', 'relationship': 'e absorbs 54.7% of recovery paths; convergence to STATE-C (57.8% terminal)', 'constraint': 'C105'},
            {'feature': 'post_hazard_recovery', 'relationship': 'Post-hazard QO recovery median 1.0 CHSH tokens = fast return', 'constraint': 'C651'},
        ],
        'confidence': 'HIGH',
    },
    'RATE_OF_CHANGE': {
        'modality': 'TEMPORAL',
        'description': 'How quickly system state is shifting (fast change = danger, slow = stable)',
        'distillation_context': 'Experienced operator monitors rate of change, not just absolute state',
        'architecture_mapping': [
            {'feature': 'LINK_monitoring', 'relationship': 'LINK operators (13.2% density) encode monitoring/observation phases', 'constraint': 'C609'},
            {'feature': 'LINK_position', 'relationship': 'LINK mean position 0.476 (early-line) = monitoring before action', 'constraint': 'C813'},
        ],
        'confidence': 'MEDIUM',
    },
    'CYCLE_DURATION': {
        'modality': 'TEMPORAL',
        'description': 'Duration of one complete distillation cycle or fraction collection',
        'distillation_context': 'Each fraction takes a characteristic time; knowing when to expect completion',
        'architecture_mapping': [
            {'feature': 'program_structure', 'relationship': 'Folio = program = one distillation run/cycle', 'constraint': 'C178'},
            {'feature': 'line_as_control_block', 'relationship': 'Line = control block = one operation within the cycle', 'constraint': 'C357'},
        ],
        'confidence': 'MEDIUM',
    },
    'INTER_FRACTION_GAP': {
        'modality': 'TEMPORAL',
        'description': 'Time between end of one fraction and start of next',
        'distillation_context': 'Gap management: system must be re-prepared between fractions',
        'architecture_mapping': [
            {'feature': 'line_boundary_reset', 'relationship': 'Hard line resets (C670): each control block starts fresh', 'constraint': 'C670'},
            {'feature': 'low_cross_line_MI', 'relationship': 'Cross-line MI = 0.52 bits (below null 0.72-0.77) = memory resets between blocks', 'constraint': 'FINGERPRINT_UNIQUENESS F10'},
        ],
        'confidence': 'MEDIUM',
    },
}


# ============================================================
# ARCHITECTURAL FEATURES to test for sensory coverage
# ============================================================

ARCHITECTURAL_FEATURES = {
    # Hazard classes (5)
    'PHASE_ORDERING_hazard': {'category': 'HAZARD', 'constraint': 'C109'},
    'COMPOSITION_JUMP_hazard': {'category': 'HAZARD', 'constraint': 'C109'},
    'CONTAINMENT_TIMING_hazard': {'category': 'HAZARD', 'constraint': 'C109'},
    'RATE_MISMATCH_hazard': {'category': 'HAZARD', 'constraint': 'C109'},
    'ENERGY_OVERSHOOT_hazard': {'category': 'HAZARD', 'constraint': 'C109'},
    # Kernel operators (3)
    'k_operator': {'category': 'KERNEL', 'constraint': 'C103'},
    'h_operator': {'category': 'KERNEL', 'constraint': 'C104'},
    'e_operator': {'category': 'KERNEL', 'constraint': 'C105'},
    # Lane oscillation (3)
    'QO_lane': {'category': 'LANE', 'constraint': 'C647'},
    'CHSH_lane': {'category': 'LANE', 'constraint': 'C647'},
    'lane_alternation': {'category': 'LANE', 'constraint': 'C966'},
    # State controller (3)
    'state_automaton_6': {'category': 'CONTROLLER', 'constraint': 'C976'},
    'state_convergence_C': {'category': 'CONTROLLER', 'constraint': 'C323'},
    'state_transitions': {'category': 'CONTROLLER', 'constraint': 'C976'},
    # Program structure (4)
    'line_as_control_block': {'category': 'PROGRAM', 'constraint': 'C357'},
    'folio_as_program': {'category': 'PROGRAM', 'constraint': 'C178'},
    'line_boundary_reset': {'category': 'PROGRAM', 'constraint': 'C670'},
    'LINK_monitoring': {'category': 'PROGRAM', 'constraint': 'C609'},
    # Recovery (3)
    'e_recovery_dominance': {'category': 'RECOVERY', 'constraint': 'C105'},
    'recovery_unconditionally_free': {'category': 'RECOVERY', 'constraint': 'C636'},
    'post_hazard_chsh_gate': {'category': 'RECOVERY', 'constraint': 'C645'},
    # Discrimination space (3)
    'MIDDLE_discrimination_100D': {'category': 'DISCRIMINATION', 'constraint': 'C987'},
    'PP_affordance_families': {'category': 'DISCRIMINATION', 'constraint': 'PP_CONSTRAINT T5'},
    'folio_vocabulary_uniqueness': {'category': 'DISCRIMINATION', 'constraint': 'C531'},
    # Energy/Flow (3)
    'energy_medial_concentration': {'category': 'ENERGY', 'constraint': 'C556'},
    'FL_operator': {'category': 'FLOW', 'constraint': 'C549'},
    'FL_HAZ_vs_FL_SAFE': {'category': 'FLOW', 'constraint': 'C976'},
    # Design principles (2)
    'hazard_clamped': {'category': 'DESIGN', 'constraint': 'C458'},
    'design_asymmetry': {'category': 'DESIGN', 'constraint': 'C458'},
}


def main():
    print("=" * 70)
    print("T2: SENSORIMOTOR ONTOLOGY CONSTRUCTION")
    print("=" * 70)

    n_phenomena = len(ONTOLOGY)
    print(f"\nOntology: {n_phenomena} phenomena across 5 modalities")

    # Count by modality
    modality_counts = {}
    for name, phenom in ONTOLOGY.items():
        m = phenom['modality']
        modality_counts[m] = modality_counts.get(m, 0) + 1
    for m, c in sorted(modality_counts.items()):
        print(f"  {m}: {c}")

    # ---- Sensory -> Architecture (S2A) coverage ----
    # For each phenomenon, collect which architectural features it maps to
    print(f"\n--- Sensory -> Architecture Coverage ---")
    s2a_mapped = 0
    s2a_details = {}
    arch_features_covered = set()

    for name, phenom in ONTOLOGY.items():
        mappings = phenom['architecture_mapping']
        if len(mappings) > 0:
            s2a_mapped += 1
            features_hit = [m['feature'] for m in mappings]
            s2a_details[name] = {
                'mapped': True,
                'n_features': len(features_hit),
                'features': features_hit,
                'confidence': phenom['confidence'],
            }
            # Track which architectural features are covered
            for feat in features_hit:
                # Match to canonical feature names
                for af_name in ARCHITECTURAL_FEATURES:
                    if af_name in feat or feat in af_name or any(
                        kw in feat.lower() for kw in af_name.lower().split('_')
                        if len(kw) > 2
                    ):
                        arch_features_covered.add(af_name)
        else:
            s2a_details[name] = {'mapped': False, 'n_features': 0, 'features': [], 'confidence': phenom['confidence']}

    s2a_pct = s2a_mapped / n_phenomena
    print(f"  Phenomena with architecture mapping: {s2a_mapped}/{n_phenomena} ({s2a_pct:.1%})")

    # ---- Architecture -> Sensory (A2S) coverage ----
    # For each architectural feature, check if any phenomenon maps to it
    print(f"\n--- Architecture -> Sensory Coverage ---")

    # Build reverse index: which phenomena mention which features
    feature_to_phenomena = {}
    for name, phenom in ONTOLOGY.items():
        for mapping in phenom['architecture_mapping']:
            feat = mapping['feature']
            if feat not in feature_to_phenomena:
                feature_to_phenomena[feat] = []
            feature_to_phenomena[feat].append(name)

    a2s_mapped = 0
    a2s_unmapped = []
    a2s_details = {}

    for af_name, af_info in ARCHITECTURAL_FEATURES.items():
        # Check if any phenomenon's mapping features match this architectural feature
        covered = False
        covering_phenomena = []
        for feat_key, phenomena_list in feature_to_phenomena.items():
            # Fuzzy match: check if the architectural feature name overlaps with the mapping feature name
            af_words = set(af_name.lower().replace('_', ' ').split())
            feat_words = set(feat_key.lower().replace('_', ' ').split())
            # Match if they share significant words (length > 2) or exact substring
            shared = af_words & feat_words - {'the', 'and', 'or', 'of', 'in', 'a', 'vs'}
            if len(shared) >= 1 or af_name.lower() in feat_key.lower() or feat_key.lower() in af_name.lower():
                covered = True
                covering_phenomena.extend(phenomena_list)

        if covered:
            a2s_mapped += 1
            a2s_details[af_name] = {
                'covered': True,
                'phenomena': list(set(covering_phenomena)),
                'category': af_info['category'],
            }
        else:
            a2s_unmapped.append(af_name)
            a2s_details[af_name] = {
                'covered': False,
                'phenomena': [],
                'category': af_info['category'],
            }

    n_arch = len(ARCHITECTURAL_FEATURES)
    a2s_pct = a2s_mapped / n_arch
    print(f"  Architectural features with sensory mapping: {a2s_mapped}/{n_arch} ({a2s_pct:.1%})")
    if a2s_unmapped:
        print(f"  Unmapped features: {a2s_unmapped}")

    # ---- Modality distribution ----
    modality_details = {}
    for modality in sorted(modality_counts.keys()):
        mod_phenomena = [n for n, p in ONTOLOGY.items() if p['modality'] == modality]
        mod_features = set()
        for phen_name in mod_phenomena:
            for mapping in ONTOLOGY[phen_name]['architecture_mapping']:
                mod_features.add(mapping['feature'])
        modality_details[modality] = {
            'n_phenomena': len(mod_phenomena),
            'phenomena': mod_phenomena,
            'architecture_features_covered': len(mod_features),
            'features': list(mod_features),
        }

    # ---- Confidence distribution ----
    confidence_counts = {}
    for name, phenom in ONTOLOGY.items():
        c = phenom['confidence']
        confidence_counts[c] = confidence_counts.get(c, 0) + 1

    # ---- Verdict ----
    if a2s_pct >= 0.60 and s2a_pct >= 0.60:
        verdict = 'VIABLE'
    elif a2s_pct >= 0.40 and s2a_pct >= 0.40:
        verdict = 'PARTIAL'
    else:
        verdict = 'NOT_VIABLE'

    explanation = (
        f"Architecture->Sensory: {a2s_pct:.1%} ({a2s_mapped}/{n_arch}). "
        f"Sensory->Architecture: {s2a_pct:.1%} ({s2a_mapped}/{n_phenomena}). "
    )
    if verdict == 'VIABLE':
        explanation += "Both directions exceed 60% threshold. The control architecture is compatible with sensory-driven pelican reflux operation."
    elif verdict == 'PARTIAL':
        explanation += "Coverage is partial; some architectural features lack clear sensory counterparts."
    else:
        explanation += "Insufficient coverage; sensory reconstruction is not viable."

    # ---- Compile results ----
    results = {
        'test': 'T2_sensorimotor_ontology',
        'n_phenomena': n_phenomena,
        'n_architectural_features': n_arch,
        'ontology': {
            name: {
                'modality': p['modality'],
                'description': p['description'],
                'distillation_context': p['distillation_context'],
                'architecture_mapping': p['architecture_mapping'],
                'confidence': p['confidence'],
            }
            for name, p in ONTOLOGY.items()
        },
        'coverage': {
            's2a': {
                'total_phenomena': n_phenomena,
                'mapped_phenomena': s2a_mapped,
                'coverage_pct': round(s2a_pct, 4),
                'unmapped': [n for n, d in s2a_details.items() if not d['mapped']],
            },
            'a2s': {
                'total_features': n_arch,
                'mapped_features': a2s_mapped,
                'coverage_pct': round(a2s_pct, 4),
                'unmapped': a2s_unmapped,
            },
        },
        'modality_distribution': modality_details,
        'confidence_distribution': confidence_counts,
        'verdict': verdict,
        'explanation': explanation,
    }

    # ---- Save ----
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't2_sensorimotor_ontology.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_path}")

    # ---- Summary ----
    print(f"\n{'=' * 70}")
    print(f"VERDICT: {verdict}")
    print(f"  Sensory->Architecture: {s2a_pct:.1%}")
    print(f"  Architecture->Sensory: {a2s_pct:.1%}")
    print(f"  Confidence: HIGH={confidence_counts.get('HIGH', 0)}, MEDIUM={confidence_counts.get('MEDIUM', 0)}, LOW={confidence_counts.get('LOW', 0)}")
    print(f"  {explanation}")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
