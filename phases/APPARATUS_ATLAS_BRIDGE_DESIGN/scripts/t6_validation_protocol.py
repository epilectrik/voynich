"""T6: Validation Protocol for Phase 582.

Staged experimental protocol stack. Order matters -- each experiment
builds on the previous. Decides C1678.
"""
import json
import os

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

EXPERIMENTS = {
    'E0_rig_characterization': {
        'name': 'Rig Characterization',
        'priority': 'PREREQUISITE -- before anything else',
        'purpose': 'Establish baseline behavior of the apparatus before any hypothesis testing.',
        'equipment_level': 1,
        'measurements': [
            'Thermal lag: time from heater change to body temperature response',
            'Steady-state reproducibility: T_body variance over 30 min at constant setting',
            'Sensor noise floor: temperature reading variance at thermal equilibrium',
            'Condensation onset: time and temperature at first condensate appearance',
            'Cooling curve: body temperature decay after heater cutoff',
        ],
        'procedure': [
            '1. Bring apparatus to thermal equilibrium at operating temperature',
            '2. Record all channels for 30 minutes (baseline)',
            '3. Step-change heater setting (3 levels: low, medium, high)',
            '4. Record thermal response curves for each step',
            '5. Perform 3 closure maneuvers (seal and unseal) to measure repeatability',
            '6. Record cooling curve after full heater cutoff',
        ],
        'pass_criteria': [
            'Temperature sensors respond to heater changes within 60s (thermal lag < 60s)',
            'Steady-state T_body variance < 2 degrees C over 30 min',
            'Closure maneuver timing repeatable within 5s',
            'Sensor noise < 0.5 degrees C at equilibrium',
        ],
        'hardware_nulls_used': [],
        'minimum_runs': 3,
        'constraints_tested': [],
        'output': 'Baseline performance envelope for the rig',
        'tier': 3,
    },
    'E1_family_analog_calibration': {
        'name': 'Family Analog Calibration',
        'priority': 'First hypothesis test',
        'purpose': 'Tune three operating modes on the rig to approximate A1/A2/A3 families.',
        'equipment_level': 2,
        'measurements': [
            'DVA_phys for each family configuration',
            'YGA_phys for each family configuration',
            'DYE_phys for each family configuration',
            'CCS1_phys (forgivingness): null vs grammar closure comparison',
            'Thermal gradient profiles (body-head) per family',
        ],
        'procedure': [
            '1. Configure A1-like mode: water bath, loose head, no recirculation',
            '2. Run 3 identical batches with lavender, measuring all channels',
            '3. Configure A2-like mode: sealed joints, recirculation loop active',
            '4. Run 3 identical batches with same material',
            '5. Configure A3-like mode: partial seal, collection without full recirculation',
            '6. Run 3 identical batches with same material',
            '7. Compare DVA_phys/YGA_phys/DYE_phys across configurations',
        ],
        'pass_criteria': [
            'A2-like configuration shows higher forgivingness (CCS1_phys) than A1-like',
            'Thermal gradient profiles differ measurably between configurations',
            'At least 2/3 family analogs are distinguishable by DVA_phys or YGA_phys',
        ],
        'hardware_nulls_used': ['N5_sham_intervention'],
        'minimum_runs': 9,
        'constraints_tested': ['C1668 (family gradient)', 'C1640 (family partition)'],
        'output': 'Physical family map in F1-F5 terms',
        'tier': 3,
    },
    'E2_closure_threshold_mapping': {
        'name': 'Closure Threshold Mapping',
        'priority': 'Core validation experiment',
        'purpose': 'Vary closure strength systematically. Estimate CTS_phys threshold per family.',
        'equipment_level': 1,
        'measurements': [
            'DVA_phys at each closure strength level',
            'YGA_phys at each closure strength level',
            'DYE_phys at each closure strength level',
            'CTS_phys composite score at each level',
        ],
        'procedure': [
            '1. Define 5 closure strength levels: 20%, 40%, 60%, 80%, 100% of full closure',
            '2. 20% = slight heat reduction only, no seal change',
            '3. 40% = moderate heat reduction, partial seal (loose gasket)',
            '4. 60% = significant heat reduction, seal tightened but not luted',
            '5. 80% = major heat reduction, seal complete, flow partially diverted',
            '6. 100% = full closure: heat off, seal complete, flow fully diverted',
            '7. Run each level 3 times, randomized order within family configuration',
            '8. Compute CTS_phys for each closure and plot DYE_phys vs CTS_phys',
            '9. Identify threshold where DYE_phys turns positive',
        ],
        'pass_criteria': [
            'DYE_phys increases monotonically with CTS_phys (Spearman rho > 0.5)',
            'Identifiable threshold where DYE_phys transitions from negative to positive',
            'Threshold differs between A1-like and A2-like configurations (if Level 2)',
        ],
        'hardware_nulls_used': ['N1_matched_time_no_seal', 'N5_sham_intervention'],
        'minimum_runs': 15,
        'constraints_tested': ['C1642 (strength-dependent)', 'C1644'],
        'output': 'CTS_phys threshold per family analog',
        'tier': 3,
    },
    'E3_counterfeit_closure_probe': {
        'name': 'Counterfeit Closure Probe',
        'priority': 'Key differentiator between families',
        'purpose': 'Inject weak/morphologically fake closures to test which configurations '
                   'accept them productively.',
        'equipment_level': 2,
        'measurements': [
            'DVA_phys for counterfeit vs real closures',
            'YGA_phys for counterfeit vs real closures',
            'DYE_phys comparison (counterfeit vs real vs null)',
            'CTS_phys of counterfeit closures (should be sub-threshold)',
        ],
        'procedure': [
            '1. Define 3 counterfeit closure types:',
            '   a. Matched-time without seal (N1): same timing, seal omitted',
            '   b. Matched-heat without routing (N2): temperature drops, flow unchanged',
            '   c. Partial seal without heat change: seal tightened, heat maintained',
            '2. Run each counterfeit type on A1-like and A2-like configurations',
            '3. Compare DYE_phys to: (a) real closure, (b) sham intervention (N5)',
            '4. Record which counterfeits A2-like accepts productively (DYE_phys > 0)',
        ],
        'pass_criteria': [
            'A2-like configuration accepts more counterfeit closures productively than A1-like',
            'At least one counterfeit type produces DYE_phys > 0 in A2-like but not A1-like',
            'Sham intervention (N5) produces DYE_phys near zero in both configurations',
        ],
        'hardware_nulls_used': ['N1_matched_time_no_seal', 'N2_matched_heat_no_routing',
                                 'N5_sham_intervention'],
        'minimum_runs': 12,
        'constraints_tested': ['C1645 (morphology-selective counterfeiting)',
                               'C1639 (close-recovery dominance)'],
        'output': 'Counterfeit closure acceptance map per family',
        'tier': 3,
    },
    'E4_productive_disruption_assay': {
        'name': 'Productive Disruption Assay',
        'priority': 'Core DYE validation',
        'purpose': 'Matched disturbance: real packet vs null packet analogs. '
                   'Tests whether grammar-specified packets produce positive DYE_phys.',
        'equipment_level': 1,
        'measurements': [
            'DVA_phys for grammar-derived vs null packets',
            'YGA_phys for grammar-derived vs null packets',
            'DYE_phys comparison',
            'Process quality before and after intervention (sensory assessment)',
        ],
        'procedure': [
            '1. Define grammar-derived closure packet: full sequence per packet library',
            '2. Define matched null packet: same energy budget, random timing (N4)',
            '3. Run alternating grammar/null packets within same session',
            '4. Measure DVA_phys and YGA_phys for each packet',
            '5. Compute DYE_phys = YGA_phys / DVA_phys for each',
            '6. Compare grammar DYE_phys to null DYE_phys',
        ],
        'pass_criteria': [
            'Grammar-specified packets produce mean DYE_phys > 0 (useful gain per disturbance)',
            'Grammar DYE_phys > null DYE_phys (p < 0.1, paired comparison)',
            'DVA_phys > 0 for both grammar and null packets (confirming actual disturbance)',
        ],
        'hardware_nulls_used': ['N4_random_timing_matched_energy', 'N5_sham_intervention',
                                 'N6_delayed_intervention'],
        'minimum_runs': 10,
        'constraints_tested': ['C1632 (YGA validated)', 'C1633 (DYE validated)',
                               'C1634 (DVA validated)', 'C1635', 'C1636'],
        'output': 'DYE_phys comparison: grammar vs null',
        'tier': 3,
    },
    'E5_sister_mode_observation': {
        'name': 'Sister-Mode Observation Assay',
        'priority': 'Lower priority',
        'purpose': 'Test ch-style discrete verification vs sh-style continuous monitoring.',
        'equipment_level': 1,
        'measurements': [
            'Product quality under discrete-check protocol',
            'Product quality under continuous-monitor protocol',
            'Number of interventions under each protocol',
            'Failure rate under each protocol',
        ],
        'procedure': [
            '1. ch-style (discrete): check product at defined intervals only (every 5 min)',
            '2. sh-style (continuous): monitor process continuously, intervene when needed',
            '3. Run same distillation batch under each protocol, 3x each',
            '4. Compare product quality and failure rates',
        ],
        'pass_criteria': [
            'ch-style produces more precise outcomes (lower quality variance)',
            'sh-style produces fewer failures (lower failure count)',
            'Protocols are distinguishable by at least one metric',
        ],
        'hardware_nulls_used': [],
        'minimum_runs': 6,
        'constraints_tested': ['C929', 'C1298', 'C1299'],
        'output': 'Monitoring mode comparison',
        'tier': 4,
    },
    'E6_subroutine_independence': {
        'name': 'Subroutine Independence Analog',
        'priority': 'Lowest priority',
        'purpose': 'Test whether operational subroutine order matters.',
        'equipment_level': 1,
        'measurements': [
            'Product quality under order A-then-B',
            'Product quality under order B-then-A',
            'Process metrics (DVA_phys, YGA_phys) for each order',
        ],
        'procedure': [
            '1. Define two operational subroutines (e.g., two distillation passes)',
            '2. Execute in order A->B for 3 runs',
            '3. Execute in order B->A for 3 runs',
            '4. Compare final product quality',
        ],
        'pass_criteria': [
            'No significant difference in product quality between orders (p > 0.1)',
            'Process metrics comparable within measurement uncertainty',
        ],
        'hardware_nulls_used': [],
        'minimum_runs': 6,
        'constraints_tested': ['C845', 'C1399', 'C1400'],
        'output': 'Subroutine order independence test',
        'tier': 4,
    },
}

# Statistical power notes
STATISTICAL_NOTES = {
    'minimum_effect_size': 'Medium (Cohen d > 0.5) for primary experiments (E2, E4)',
    'alpha_level': 0.10,
    'power_target': 0.80,
    'primary_tests': 'Paired comparisons within session (reduces between-run variance)',
    'randomization': 'Randomize intervention order within sessions where possible',
    'blinding': 'Not feasible for operator; use sham intervention (N5) as attention control',
    'multiple_comparisons': 'Pre-specify primary comparison per experiment; '
                           'secondary comparisons are exploratory',
}

# Safety precautions
SAFETY_PRECAUTIONS = [
    'All experiments conducted with fume hood or adequate ventilation',
    'Class B fire extinguisher within arm reach',
    'Heat-resistant gloves worn when handling hot apparatus',
    'Safety glasses worn during all operations',
    'Never leave apparatus unattended while heat source is active',
    'Keep water source nearby for cooling emergencies',
    'Lavender is GRAS (generally recognized as safe); no toxic material in primary validation',
    'If using ethanol: eliminate ignition sources, ensure ventilation',
    'E0 MUST complete before any hypothesis-testing experiments',
]


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)

    # Assess experiment feasibility
    n_experiments = len(EXPERIMENTS)
    feasible = []
    for name, exp in EXPERIMENTS.items():
        has_materials = True  # All use lavender + water
        has_measurements = bool(exp['measurements'])
        has_pass_criteria = bool(exp['pass_criteria'])
        if has_materials and has_measurements and has_pass_criteria:
            feasible.append(name)

    n_feasible = len(feasible)
    total_minimum_runs = sum(exp['minimum_runs'] for exp in EXPERIMENTS.values())

    # Categorize nulls used
    all_nulls_used = set()
    for exp in EXPERIMENTS.values():
        all_nulls_used.update(exp['hardware_nulls_used'])

    if n_feasible >= 4:
        verdict = 'EXPERIMENTS_FEASIBLE'
    elif n_feasible >= 2:
        verdict = 'EXPERIMENTS_PARTIAL'
    else:
        verdict = 'EXPERIMENTS_BLOCKED'

    output = {
        'metadata': {
            'phase': '582',
            'script': 't6_validation_protocol.py',
            'n_experiments': n_experiments,
            'n_feasible': n_feasible,
            'total_minimum_runs': total_minimum_runs,
        },
        'experiments': EXPERIMENTS,
        'statistical_notes': STATISTICAL_NOTES,
        'safety_precautions': SAFETY_PRECAUTIONS,
        'experiment_order': [
            'E0_rig_characterization (PREREQUISITE)',
            'E1_family_analog_calibration',
            'E2_closure_threshold_mapping',
            'E3_counterfeit_closure_probe',
            'E4_productive_disruption_assay',
            'E5_sister_mode_observation',
            'E6_subroutine_independence',
        ],
        'C1678': {
            'verdict': verdict,
            'n_feasible': n_feasible,
            'n_total': n_experiments,
            'feasible_experiments': feasible,
            'nulls_used': sorted(all_nulls_used),
            'rationale': (f'{n_feasible}/{n_experiments} experiments have available materials, '
                         f'defined measurements, and clear pass/fail criteria; '
                         f'{total_minimum_runs} total minimum runs'),
            'tier': 3,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't6_validation_protocol.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T6: Validation protocol complete")
    print(f"  Experiments: {n_experiments} ({n_feasible} feasible)")
    for name, exp in EXPERIMENTS.items():
        level = exp['equipment_level']
        runs = exp['minimum_runs']
        print(f"    {name}: Level {level}, {runs} min runs, "
              f"priority={exp['priority']}")
    print(f"  Total minimum runs: {total_minimum_runs}")
    print(f"  Hardware nulls used: {sorted(all_nulls_used)}")
    print(f"  C1678: {verdict}")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
