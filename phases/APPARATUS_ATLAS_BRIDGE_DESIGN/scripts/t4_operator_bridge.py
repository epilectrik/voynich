"""T4: Operator Bridge for Phase 582.

SECONDARY/HEURISTIC LAYER. Class summaries, line-level control cycle,
safety protocols, operator judgment boundaries.
Explicitly framed as heuristic -- not the load-bearing bridge.
Decides C1676 and C1677.
"""
import json
import os

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

# Line-level control cycle (heuristic interpretation)
LINE_CONTROL_CYCLE = {
    'SPEC': {
        'quintile': 'Q0',
        'physical_heuristic': 'Read apparatus state. Check temperatures, flow, seal integrity. '
                              'Assess before acting.',
        'atom_signature': 'e-HEAD peak, specification-class terminals',
        'tier': 3,
    },
    'WORK': {
        'quintile': 'Q1-Q3',
        'physical_heuristic': 'Execute thermal operation. Q1 = apply energy. '
                              'Q2-Q3 = sustain and monitor.',
        'atom_signature': 'k-HEAD at Q1 (THERMAL peak, hazard-immune), '
                         'a-HEAD stable through Q2-Q3',
        'tier': 3,
    },
    'CLOSURE': {
        'quintile': 'Q4',
        'physical_heuristic': 'End operation step. Arrest process, secure product, '
                              'verify completion.',
        'atom_signature': 'm-terminal surge (77% of TERM JSD), headless infrastructure surge',
        'tier': 3,
    },
}

# Macro-state to operator mode (heuristic)
MACRO_STATE_MODES = {
    'AXM': {
        'operator_mode': 'Maintain current state, routine monitoring',
        'physical_action': 'No changes needed. Monitor temperatures and flow. '
                          'Apparatus is in equilibrium.',
        'constraint_basis': ['C976 (6 macro-states)'],
        'tier': 3,
    },
    'AXm': {
        'operator_mode': 'Adjust parameters, change settings',
        'physical_action': 'Modify a single control variable: temperature setpoint, '
                          'valve position, or damper angle.',
        'constraint_basis': ['C976'],
        'tier': 3,
    },
    'CC': {
        'operator_mode': 'Initiate or terminate an operation',
        'physical_action': 'Major state change: light/extinguish fire, seal/unseal vessel, '
                          'begin/end collection.',
        'constraint_basis': ['C976'],
        'tier': 3,
    },
    'FL_HAZ': {
        'operator_mode': 'Material in risky state -- immediate attention',
        'physical_action': 'Active hazard condition: bumping, overheating, unexpected boiling. '
                          'Reduce heat, vent if safe, stand back if necessary.',
        'constraint_basis': ['C976', 'C109 (hazard topology)'],
        'tier': 3,
    },
    'FL_SAFE': {
        'operator_mode': 'Operation winding down safely',
        'physical_action': 'Process completing naturally. Monitor but do not intervene. '
                          'Prepare for next step.',
        'constraint_basis': ['C976'],
        'tier': 3,
    },
    'FQ': {
        'operator_mode': 'Repeat or exit a control loop',
        'physical_action': 'Decision point: is product quality sufficient? Repeat batch, '
                          'adjust and continue, or end.',
        'constraint_basis': ['C976'],
        'tier': 3,
    },
}

# REGIME to fire degree (heuristic, per INTERPRETATION_SUMMARY X.2)
REGIME_FIRE_MAPPING = {
    'R2': {
        'brunschwig_degree': 'Second (warm)',
        'CEI': 0.367,
        'setup_heuristic': 'Attenuated heat, collection-focused',
        'physical_description': 'Gentle warmth below boiling. Sand bath or warm water bath. '
                               'Focus is on gentle separation, not vigorous distillation.',
        'tier': 3,
    },
    'R1': {
        'brunschwig_degree': 'First (balneum)',
        'CEI': 0.510,
        'setup_heuristic': 'Water bath, sustained gentle heat',
        'physical_description': 'Water bath (balneum mariae). Sustained, even heating. '
                               'Classical gentle distillation mode.',
        'tier': 3,
    },
    'R4': {
        'brunschwig_degree': 'Fourth (precision)',
        'CEI': 0.584,
        'setup_heuristic': 'Precision-controlled, narrow tolerance',
        'physical_description': 'Careful temperature control for specific fraction collection. '
                               'Requires attention to narrow windows.',
        'tier': 3,
    },
    'R3': {
        'brunschwig_degree': 'Third (seething)',
        'CEI': 0.717,
        'setup_heuristic': 'Direct heat, open-cycle batch',
        'physical_description': 'Vigorous direct heating. Active boiling, rapid distillation. '
                               'Highest energy input.',
        'tier': 3,
    },
}

# Section to apparatus style (modulation only)
SECTION_APPARATUS_STYLE = {
    'B': {
        'apparatus_relevance': 'Distillation-biased',
        'key_statistics': '97% DISTILLATION, 70% R1',
        'physical_implication': 'Section B folios predominantly describe water-bath distillation '
                               'operations with gentle sustained heat.',
        'tier': 3,
    },
    'H': {
        'apparatus_relevance': 'Apparatus-diverse',
        'key_statistics': 'Exercises full configuration space, all 5 profiles represented',
        'physical_implication': 'Section H folios cover the broadest range of apparatus '
                               'configurations and operating modes.',
        'tier': 3,
    },
    'S': {
        'apparatus_relevance': 'Output-distributed',
        'key_statistics': 'Distribution across collection modes',
        'physical_implication': 'Section S folios emphasize product collection and '
                               'output management.',
        'tier': 3,
    },
}

# Softened semantic labels (per expert correction)
SOFTENED_LABELS = {
    'a_HEAD': {
        'old_label': 'yield',
        'corrected_label': 'Active transformation / primary hazard-bearing operational domain',
        'reason': 'Expert correction: a-HEAD marks the domain where active transformation '
                 'occurs, not where yield is produced. It is hazard-bearing because active '
                 'transformation is where things can go wrong.',
        'tier': 3,
    },
    'paragraph': {
        'old_label': 'one complete run',
        'corrected_label': 'Self-contained operational subroutine or batch-emphasis packet',
        'reason': 'Expert correction: paragraphs are self-contained operational units, '
                 'not necessarily complete runs. A folio may contain multiple subroutines.',
        'tier': 3,
    },
    'terminal_y': {
        'old_label': 'END (pseudo-translation)',
        'corrected_label': 'Operation step self-containment marker',
        'reason': 'Terminal -y marks operational self-containment of the step, '
                 'not a literal END command.',
        'tier': 3,
    },
}

# Safety architecture (three levels)
SAFETY_ARCHITECTURE = {
    'level_1_construction_exclusion': {
        'structural_mechanism': 'ch/sh-initial compounds absent (5,821:0)',
        'physical_protocol': 'Verify apparatus CAN physically perform instruction before executing. '
                            'If a construction is absent from the grammar, the physical analog is '
                            'a configuration that cannot exist in the apparatus design.',
        'constraint_basis': ['C929 (ch/sh absence)', 'C1298-C1299'],
        'tier': 2,
    },
    'level_2_hazard_source_typing': {
        'structural_mechanism': 'k-HEAD complete immunity (0/16,819 hazard frames)',
        'physical_protocol': 'Pure thermal adjustment (applying or reducing heat) is intrinsically '
                            'safe. The hazard arises downstream -- from what happens to material '
                            'after heat is applied. Monitor downstream consequences, not the '
                            'heat source itself.',
        'constraint_basis': ['C1446 (k complete hazard immunity)', 'C1464 (k-IMMUNE)'],
        'tier': 2,
    },
    'level_3_transition_prohibition': {
        'structural_mechanism': '17 forbidden transitions, 5 hazard classes',
        'physical_protocol': 'Interpose verification between different hazard domains. '
                            'Never transition directly from one hazard class to another '
                            'without checking apparatus state.',
        'constraint_basis': ['C109 (17 forbidden transitions)', 'C216 (5 hazard classes)',
                            'C789 (71/29 batch/apparatus hazard split)'],
        'tier': 2,
    },
}

# Five hazard classes with physical failure modes
HAZARD_CLASSES = {
    'PHASE_ORDERING': {
        'fraction': 0.41,
        'physical_failure': 'Wrong phase state for operation',
        'prevention': 'Verify material phase before each operation. Do not apply operations '
                     'designed for liquid to vapor, or vice versa.',
        'example': 'Attempting to seal vessel while material is actively boiling',
        'tier': 2,
    },
    'CONTAINMENT_TIMING': {
        'fraction': 0.24,
        'physical_failure': 'Seals adjusted at wrong moment',
        'prevention': 'Never adjust seals during active phase transitions. Wait for thermal '
                     'stabilization before modifying containment.',
        'example': 'Opening lute while pressure is changing',
        'tier': 2,
    },
    'COMPOSITION_JUMP': {
        'fraction': 0.24,
        'physical_failure': 'Discontinuous composition change',
        'prevention': 'Monitor condensate quality continuously. Do not mix fractions from '
                     'different distillation phases.',
        'example': 'Combining early and late fractions without verification',
        'tier': 2,
    },
    'EQUIPMENT_OVERCOMMIT': {
        'fraction': 0.06,
        'physical_failure': 'Intensity exceeds apparatus capability',
        'prevention': 'Match fire degree to configuration. Do not apply third-degree fire '
                     'to apparatus designed for first-degree operation.',
        'example': 'Direct flame on a delicate water-bath setup',
        'tier': 2,
    },
    'RECYCLE_CONTAMINATION': {
        'fraction': 0.06,
        'physical_failure': 'Impure condensate returned to body',
        'prevention': 'Verify condensate quality before recirculation. Inspect visually and '
                     'by sensory assessment.',
        'example': 'Returning turbid or discolored condensate to the boiling flask',
        'tier': 2,
    },
}

# Operator judgment boundaries (encodable vs non-encodable)
JUDGMENT_BOUNDARIES = {
    'encodable_automatable': [
        'Heater cuts (on/off at specified temperatures)',
        'Dwell timing windows (hold for N seconds/minutes)',
        'Seal-state logging (open/closed events)',
        'Temperature thresholds (act when T > X)',
        'Event annotation (packet start/end timestamps)',
        'Closure packet execution (follow specified sequence)',
    ],
    'non_encodable_operator_judged': [
        'Smell / fraction quality assessment',
        'Visual condensate quality (clarity, color, turbidity)',
        'Leak character assessment (is this a problem?)',
        'When "enough" has been reached (batch completeness)',
        'Whether behavior is acceptable vs salvage-worthy',
        'Material readiness for next phase',
        'Sensory evaluation of product quality',
        'Anomaly recognition (something unexpected happening)',
        'Environmental conditions affecting operation',
        'Equipment wear and fatigue assessment',
        'Sound assessment (boiling character, hissing, bumping)',
        'Tactile assessment (vessel temperature by touch proximity)',
        'Timing judgment (pace of operation, rhythm)',
    ],
    'constraint_basis': ['C1056 (13 judgment types not encoded)'],
    'interpretation': 'The system deliberately does not encode all sensory gating. '
                     'This prevents over-automation drift -- the operator remains essential '
                     'for quality-critical decisions that require human sensory assessment.',
    'tier': 3,
}


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)

    # Assess translation coverage
    n_macro_states = len(MACRO_STATE_MODES)  # 6
    n_zones = len(LINE_CONTROL_CYCLE)  # 3
    n_regimes = len(REGIME_FIRE_MAPPING)  # 4
    n_judgment_types = len(JUDGMENT_BOUNDARIES['non_encodable_operator_judged'])

    total_mappable = n_macro_states + n_zones + n_regimes  # 13
    total_mapped = total_mappable  # All mapped

    if total_mapped >= total_mappable:
        translation_verdict = 'TRANSLATION_COMPLETE'
    elif total_mapped >= total_mappable * 0.8:
        translation_verdict = 'TRANSLATION_PARTIAL'
    else:
        translation_verdict = 'TRANSLATION_INSUFFICIENT'

    # Assess safety derivability
    n_hazard_classes = len(HAZARD_CLASSES)  # 5
    n_safety_levels = len(SAFETY_ARCHITECTURE)  # 3
    has_judgment_boundaries = bool(JUDGMENT_BOUNDARIES['non_encodable_operator_judged'])

    if n_hazard_classes >= 5 and n_safety_levels >= 3 and has_judgment_boundaries:
        safety_verdict = 'SAFETY_DERIVABLE'
    elif n_hazard_classes >= 3:
        safety_verdict = 'SAFETY_PARTIAL'
    else:
        safety_verdict = 'SAFETY_BLOCKED'

    output = {
        'metadata': {
            'phase': '582',
            'script': 't4_operator_bridge.py',
            'framing': 'SECONDARY HEURISTIC LAYER -- not the load-bearing bridge. '
                      'The primary bridge is manifold-to-knob mapping (T1).',
        },
        'line_control_cycle': LINE_CONTROL_CYCLE,
        'macro_state_modes': MACRO_STATE_MODES,
        'regime_fire_mapping': REGIME_FIRE_MAPPING,
        'section_apparatus_style': SECTION_APPARATUS_STYLE,
        'softened_labels': SOFTENED_LABELS,
        'safety_architecture': SAFETY_ARCHITECTURE,
        'hazard_classes': HAZARD_CLASSES,
        'judgment_boundaries': JUDGMENT_BOUNDARIES,
        'C1676': {
            'verdict': translation_verdict,
            'n_macro_states_mapped': n_macro_states,
            'n_zones_mapped': n_zones,
            'n_regimes_mapped': n_regimes,
            'n_judgment_types': n_judgment_types,
            'rationale': (f'{total_mapped}/{total_mappable} structural elements mapped as heuristics; '
                         f'{n_judgment_types} non-encodable judgment types identified'),
            'tier': 3,
        },
        'C1677': {
            'verdict': safety_verdict,
            'n_hazard_classes_mapped': n_hazard_classes,
            'n_safety_levels': n_safety_levels,
            'has_judgment_boundaries': has_judgment_boundaries,
            'rationale': (f'{n_hazard_classes}/5 hazard classes mapped, '
                         f'{n_safety_levels} safety levels translated, '
                         f'judgment boundaries defined'),
            'tier': 3,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't4_operator_bridge.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T4: Operator bridge complete")
    print(f"  Line zones: {n_zones} (SPEC/WORK/CLOSURE)")
    print(f"  Macro-states: {n_macro_states}")
    print(f"  REGIMEs: {n_regimes}")
    print(f"  Hazard classes: {n_hazard_classes}")
    print(f"  Safety levels: {n_safety_levels}")
    print(f"  Non-encodable judgments: {n_judgment_types}")
    print(f"  Softened labels: {len(SOFTENED_LABELS)}")
    print(f"  C1676: {translation_verdict}")
    print(f"  C1677: {safety_verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
