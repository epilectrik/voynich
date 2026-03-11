"""T3: Physical Metrics Schema for Phase 582.

Define physical analogs of the winning virtual process metrics:
DVA_phys, YGA_phys, DYE_phys, CTS_phys, forgivingness_phys.
Also define hardware null conditions and data model.
Decides C1679.
"""
import json
import os

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

# Physical metric definitions
METRICS = {
    'DVA_phys': {
        'name': 'Disruption Value Analog (physical)',
        'virtual_source': 'DVA: magnitude of grammar-induced process disturbance',
        'definition': 'Magnitude of induced process disturbance during intervention window',
        'formula': 'DVA_phys = sqrt(delta_T_body^2 + delta_T_head^2 + '
                   'delta_flow_rate^2 + delta_gradient^2) over intervention window',
        'components': [
            {'channel': 'delta_T_body', 'sensor': 'K-type thermocouple at body',
             'unit': 'degrees C', 'weight': 1.0},
            {'channel': 'delta_T_head', 'sensor': 'K-type thermocouple at head',
             'unit': 'degrees C', 'weight': 1.0},
            {'channel': 'delta_flow_rate', 'sensor': 'Condensate mass/time (manual or drip counter)',
             'unit': 'ml/min', 'weight': 0.5},
            {'channel': 'delta_gradient', 'sensor': 'FLIR body-head gradient',
             'unit': 'degrees C', 'weight': 0.5},
        ],
        'required_sensors': ['temp_body', 'temp_head'],
        'optional_sensors': ['flow_meter', 'FLIR'],
        'interpretation': 'How much did the intervention actually disturb the process?',
        'constraint_basis': ['C1634 (DVA validated)'],
        'tier': 3,
    },
    'YGA_phys': {
        'name': 'Y-Gain Analog (physical)',
        'virtual_source': 'YGA: useful product/quality gain during/after intervention',
        'definition': 'Useful product or quality gain during or immediately after intervention window',
        'formula': 'YGA_phys = delta_condensate_rate * quality_score over observation window',
        'components': [
            {'channel': 'delta_condensate_rate', 'sensor': 'Condensate collection mass/time',
             'unit': 'ml/min', 'weight': 1.0},
            {'channel': 'quality_score', 'sensor': 'Sensory assessment (clarity, scent intensity)',
             'unit': 'ordinal 0-5', 'weight': 1.0},
            {'channel': 'fraction_purity', 'sensor': 'Visual clarity check or refractometer',
             'unit': 'binary or index', 'weight': 0.5},
        ],
        'required_sensors': ['condensate_mass', 'quality_assessment'],
        'optional_sensors': ['refractometer'],
        'interpretation': 'Did the intervention produce useful product improvement?',
        'constraint_basis': ['C1632 (YGA validated)'],
        'tier': 3,
    },
    'DYE_phys': {
        'name': 'Disruption-to-Y Efficiency (physical)',
        'virtual_source': 'DYE: useful gain per unit disturbance',
        'definition': 'Ratio of YGA_phys to DVA_phys',
        'formula': 'DYE_phys = YGA_phys / DVA_phys (undefined if DVA_phys = 0)',
        'components': [],
        'required_sensors': ['(all DVA_phys sensors)', '(all YGA_phys sensors)'],
        'optional_sensors': [],
        'interpretation': 'How efficiently does disturbance convert to useful output? '
                         'DYE_phys > 0 means the intervention was productive.',
        'constraint_basis': ['C1633 (DYE validated)', 'C1637 (WCP demoted, DYE primary)'],
        'tier': 3,
    },
    'CTS_phys': {
        'name': 'Closure Threshold Strength (physical)',
        'virtual_source': 'CTS: continuous closure strength index',
        'definition': 'Composite closure strength from observable closure state variables',
        'formula': 'CTS_phys = w1*seal_completion + w2*heat_reduction_slope + '
                   'w3*gradient_collapse_rate + w4*flow_change_magnitude',
        'components': [
            {'channel': 'seal_completion', 'sensor': 'Manual event annotation (binary or timed)',
             'unit': 'fraction 0-1', 'weight': 0.35,
             'note': 'Highest weight: containment-coupled recovery dominates A2 (C1639)'},
            {'channel': 'heat_reduction_slope', 'sensor': 'Temperature probe derivative',
             'unit': 'degrees C/s', 'weight': 0.25},
            {'channel': 'gradient_collapse_rate', 'sensor': 'FLIR body-head delta derivative',
             'unit': 'degrees C/s', 'weight': 0.25},
            {'channel': 'flow_change_magnitude', 'sensor': 'Condensate rate change',
             'unit': 'ml/min', 'weight': 0.15},
        ],
        'required_sensors': ['temp_body', 'temp_head', 'event_annotation'],
        'optional_sensors': ['FLIR', 'flow_meter'],
        'interpretation': 'How strong is this closure? Above threshold -> productive in A2. '
                         'Below threshold -> loses to null in A2 (C1642).',
        'constraint_basis': ['C1642 (strength-dependent)', 'C1644', 'C1639 (close-recovery 159.5%)'],
        'tier': 3,
    },
    'forgivingness_phys': {
        'name': 'Forgivingness Index (physical)',
        'virtual_source': 'CCS1: null vs grammar closure performance retention',
        'definition': 'Ratio of process quality under null (random) closure to process quality '
                     'under grammar-specified closure',
        'formula': 'Forgivingness_phys = mean(YGA_phys under null_closures) / '
                   'mean(YGA_phys under grammar_closures)',
        'components': [],
        'required_sensors': ['(all YGA_phys sensors)', 'controlled null conditions'],
        'optional_sensors': [],
        'interpretation': 'How much does the apparatus compensate for random (non-optimal) closures? '
                         'Values near 1.0 = highly forgiving (A2-like). '
                         'Values near 0 = unforgiving (A1-like).',
        'constraint_basis': ['C1639 (A2 CCS1=0.114)', 'C1642 (STRONG vs WEAK)'],
        'tier': 3,
    },
}

# Hardware null / control conditions
HARDWARE_NULLS = {
    'N1_matched_time_no_seal': {
        'description': 'Same timing as closure, but sealing step omitted/incomplete',
        'controls_for': 'Separates seal effect from timing effect',
        'physical_procedure': 'At the closure trigger point, reduce heat on the same schedule '
                             'but do not seal the vessel. Leave joints open.',
        'expected_result': 'Lower CTS_phys; lower YGA_phys than real closure in A2',
    },
    'N2_matched_heat_no_routing': {
        'description': 'Temperature drops on same schedule but flow path unchanged',
        'controls_for': 'Separates thermal from routing effects',
        'physical_procedure': 'Reduce heat to target, but do not divert collection or '
                             'change condensate routing. Material continues same path.',
        'expected_result': 'Partial DVA_phys (thermal only); attenuated YGA_phys',
    },
    'N3_matched_routing_no_seal': {
        'description': 'Divert flow but do not seal body',
        'controls_for': 'Separates routing from containment effects',
        'physical_procedure': 'Switch collection flask or divert condensate, but leave '
                             'the body/head junction open.',
        'expected_result': 'Flow disruption without pressure change; tests routing contribution',
    },
    'N4_random_timing_matched_energy': {
        'description': 'Same total energy budget but random intervention timing',
        'controls_for': 'Total energy vs timing precision',
        'physical_procedure': 'Same heat reduction magnitude, applied at random point in '
                             'the operation cycle rather than at grammar-specified position.',
        'expected_result': 'Tests whether WHEN matters or only HOW MUCH',
    },
    'N5_sham_intervention': {
        'description': 'Go through motions without physical effect',
        'controls_for': 'Operator attention bias',
        'physical_procedure': 'Touch the apparatus, log an event, but do not actually change '
                             'any setting. Controls for Hawthorne-type effects.',
        'expected_result': 'No DVA_phys, no YGA_phys (if the process is physics-driven)',
    },
    'N6_delayed_intervention': {
        'description': 'Same closure, delayed by T seconds',
        'controls_for': 'Timing sensitivity',
        'physical_procedure': 'Execute the full closure procedure, but start T seconds '
                             'after the grammar-specified trigger point.',
        'expected_result': 'Tests how rapidly DYE_phys degrades with timing error',
    },
    'N7_phase_misaligned': {
        'description': 'Closure at wrong phase state',
        'controls_for': 'Phase-ordering hazard (41% of hazard topology)',
        'physical_procedure': 'Execute closure when material is in wrong phase '
                             '(e.g., still actively boiling, or already cooled).',
        'expected_result': 'Tests C109 PHASE_ORDERING: should produce the most dangerous failure mode',
    },
}

# Data model specification
DATA_MODEL = {
    'synchronization': 'All sensors on common clock (NTP or manual sync)',
    'raw_channels': [
        {'name': 'temp_body', 'sensor': 'K-type thermocouple', 'rate_hz': 1.0,
         'unit': 'degrees C', 'required': True},
        {'name': 'temp_head', 'sensor': 'K-type thermocouple', 'rate_hz': 1.0,
         'unit': 'degrees C', 'required': True},
        {'name': 'temp_bath', 'sensor': 'K-type thermocouple', 'rate_hz': 1.0,
         'unit': 'degrees C', 'required': False},
        {'name': 'temp_collection', 'sensor': 'K-type thermocouple', 'rate_hz': 1.0,
         'unit': 'degrees C', 'required': False},
        {'name': 'flir_frame', 'sensor': 'FLIR thermal camera', 'rate_hz': 0.5,
         'unit': 'thermal image', 'required': False},
        {'name': 'condensate_mass', 'sensor': 'Scale under receiving flask', 'rate_hz': 0.1,
         'unit': 'grams', 'required': True},
        {'name': 'heater_state', 'sensor': 'Relay state log', 'rate_hz': 1.0,
         'unit': 'binary on/off', 'required': False},
    ],
    'derived_channels': [
        {'name': 'thermal_gradient', 'formula': 'temp_body - temp_head', 'unit': 'degrees C'},
        {'name': 'gradient_slope', 'formula': 'd(thermal_gradient)/dt', 'unit': 'degrees C/s'},
        {'name': 'condensate_rate', 'formula': 'd(condensate_mass)/dt', 'unit': 'g/min'},
        {'name': 'CTS_phys_running', 'formula': 'weighted composite (see CTS_phys definition)',
         'unit': 'composite index'},
        {'name': 'DVA_phys_running', 'formula': 'euclidean disturbance magnitude',
         'unit': 'composite index'},
    ],
    'trigger_annotations': [
        'packet_start', 'packet_end',
        'seal_start', 'seal_complete',
        'heat_change_start', 'heat_change_complete',
        'collection_divert_start', 'collection_divert_complete',
        'sensory_check', 'quality_assessment',
    ],
    'event_windows': {
        'intervention_window': 'From packet_start to process stabilization (thermal gradient < threshold)',
        'observation_window': 'From stabilization to next packet_start (or end of run)',
        'stabilization_criterion': 'abs(gradient_slope) < 0.1 C/s for 30 consecutive seconds',
    },
}


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)

    # Assess metric bridge adequacy
    n_metrics_defined = 0
    for name, defn in METRICS.items():
        has_formula = bool(defn['formula'])
        has_sensors = bool(defn['required_sensors'])
        if has_formula and has_sensors:
            n_metrics_defined += 1

    if n_metrics_defined >= 5:
        verdict = 'METRIC_BRIDGE_COMPLETE'
    elif n_metrics_defined >= 3:
        verdict = 'METRIC_BRIDGE_PARTIAL'
    else:
        verdict = 'METRIC_BRIDGE_INSUFFICIENT'

    output = {
        'metadata': {
            'phase': '582',
            'script': 't3_physical_metrics_schema.py',
            'n_metrics': len(METRICS),
            'n_nulls': len(HARDWARE_NULLS),
            'n_raw_channels': len(DATA_MODEL['raw_channels']),
            'n_derived_channels': len(DATA_MODEL['derived_channels']),
        },
        'metrics': METRICS,
        'hardware_nulls': HARDWARE_NULLS,
        'data_model': DATA_MODEL,
        'C1679': {
            'verdict': verdict,
            'n_metrics_defined': n_metrics_defined,
            'n_metrics_total': 5,
            'rationale': (f'{n_metrics_defined}/5 virtual metrics have operational '
                          f'physical definitions with sensors and formulas'),
            'tier': 3,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't3_physical_metrics_schema.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T3: Physical metrics schema complete")
    print(f"  Metrics defined: {n_metrics_defined}/5")
    for name, defn in METRICS.items():
        req = ', '.join(defn['required_sensors'][:3])
        print(f"    {name}: {req}")
    print(f"  Hardware nulls: {len(HARDWARE_NULLS)}")
    for name, null in HARDWARE_NULLS.items():
        print(f"    {name}: {null['controls_for']}")
    print(f"  Raw channels: {len(DATA_MODEL['raw_channels'])} "
          f"({sum(1 for c in DATA_MODEL['raw_channels'] if c['required'])} required)")
    print(f"  Derived channels: {len(DATA_MODEL['derived_channels'])}")
    print(f"  C1679: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
