"""T5: Equipment Specification for Phase 582.

Three-level rig specification. Optimize for apparatus-response
observability, not iconographic romance.
"""
import json
import os

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')

# Common monitoring equipment (all levels)
COMMON_MONITORING = [
    {'item': 'K-type thermocouple (body)', 'purpose': 'Body temperature measurement',
     'required': True, 'est_cost_usd': 15},
    {'item': 'K-type thermocouple (head)', 'purpose': 'Head temperature measurement',
     'required': True, 'est_cost_usd': 15},
    {'item': 'K-type thermocouple (bath/source)', 'purpose': 'Heat source monitoring',
     'required': False, 'est_cost_usd': 15},
    {'item': 'K-type thermocouple (collection)', 'purpose': 'Collection point temperature',
     'required': False, 'est_cost_usd': 15},
    {'item': 'Thermocouple reader/logger (4-channel)', 'purpose': 'Temperature logging',
     'required': True, 'est_cost_usd': 50},
    {'item': 'FLIR thermal camera', 'purpose': 'Body-head gradient, gradient collapse timing',
     'required': False, 'est_cost_usd': 250},
    {'item': 'Digital scale (0.1g resolution)', 'purpose': 'Condensate mass measurement',
     'required': True, 'est_cost_usd': 30},
    {'item': 'Timer / event logger', 'purpose': 'Event annotation timestamps',
     'required': True, 'est_cost_usd': 0},
    {'item': 'Notebook + annotation protocol', 'purpose': 'Manual event logging',
     'required': True, 'est_cost_usd': 5},
]

# Common safety equipment
COMMON_SAFETY = [
    {'item': 'Class B fire extinguisher', 'purpose': 'Fire suppression', 'required': True},
    {'item': 'Heat-resistant gloves', 'purpose': 'Thermal protection', 'required': True},
    {'item': 'Safety glasses', 'purpose': 'Eye protection', 'required': True},
    {'item': 'Ventilation (fume hood or open air)', 'purpose': 'Vapor management',
     'required': True},
    {'item': 'Fire-resistant work surface', 'purpose': 'Thermal safety', 'required': True},
    {'item': 'First aid kit', 'purpose': 'Minor injury response', 'required': True},
]

# Common consumables
COMMON_CONSUMABLES = [
    {'item': 'Lavender (Lavandula angustifolia, dried flowers)',
     'purpose': 'Primary validation material -- safe, clear sensory checkpoints, '
                'Brunschwig-aligned',
     'quantity': '500g per experiment series', 'est_cost_usd': 25},
    {'item': 'Clean water', 'purpose': 'Distillation medium, bath medium',
     'quantity': '10L per session', 'est_cost_usd': 0},
    {'item': 'Grain ethanol (optional)', 'purpose': 'Alternative distillation medium',
     'quantity': '1L', 'est_cost_usd': 20},
]

# Level 1: MVP Functional Rig
LEVEL_1 = {
    'name': 'MVP Functional Rig',
    'build_time': 'Buildable in a week with existing/readily available equipment',
    'purpose': 'Validate process-quality behavior. Map forgivingness / closure thresholds. '
               'Test productive disruption. Compute DVA_phys/YGA_phys/DYE_phys.',
    'experiments_enabled': ['E0 (rig characterization)', 'E1 (family analog calibration, partial)',
                            'E2 (closure threshold mapping)', 'E4 (productive disruption assay)'],
    'equipment': [
        {'item': 'Hydrodistiller / steam distiller', 'type': 'Standard kitchen or lab unit',
         'purpose': 'Base distillation apparatus', 'est_cost_usd': 80,
         'sourcing': 'Kitchen supply, lab supply, Amazon'},
        {'item': 'Receiving flask(s) (2-3)', 'type': 'Glass, 250-500 ml',
         'purpose': 'Condensate collection', 'est_cost_usd': 20,
         'sourcing': 'Lab supply'},
        {'item': 'Controllable heat source', 'type': 'Electric hotplate with adjustable dial',
         'purpose': 'Heat control', 'est_cost_usd': 40,
         'sourcing': 'Kitchen/lab supply'},
        {'item': 'Smart relay (optional)', 'type': 'Wi-Fi relay or Arduino-controlled relay',
         'purpose': 'Heater state logging and optional automated control',
         'est_cost_usd': 15, 'sourcing': 'Electronics supplier'},
    ],
    'family_coverage': {
        'A1_possible': True,
        'A1_notes': 'Water bath mode with loose head fitting',
        'A2_possible': False,
        'A2_notes': 'No recirculation path; cannot reproduce A2 geometry',
        'A3_possible': True,
        'A3_notes': 'Standard distill-collect operation',
    },
    'est_total_cost_usd': 560,
}

# Level 2: Recirculatory Analog Rig
LEVEL_2 = {
    'name': 'Recirculatory Analog Rig',
    'build_time': 'Add to Level 1; requires glass connectors and variable-path plumbing',
    'purpose': 'Reproduce A1/A2/A3 family geometry. Test F1-F5 knob mappings. '
               'Closure threshold mapping under recirculation. Counterfeit closure testing.',
    'experiments_enabled': ['E0-E5 (all except E6)'],
    'additions_over_level_1': [
        {'item': 'Glass recirculation loop', 'type': 'Borosilicate tubing + connectors',
         'purpose': 'True return path for condensate recirculation',
         'est_cost_usd': 60, 'sourcing': 'Lab glass supplier'},
        {'item': 'Ground glass joints (3-4 joints)', 'type': '24/40 standard taper',
         'purpose': 'Configurable seal quality for F5 knob testing',
         'est_cost_usd': 40, 'sourcing': 'Lab glass supplier'},
        {'item': 'Variable gaskets (set)', 'type': 'PTFE, silicone, wax lute',
         'purpose': 'Seal quality variation for A1 vs A2 mode',
         'est_cost_usd': 20, 'sourcing': 'Lab supply'},
        {'item': 'Adjustable valve / stopcock', 'type': 'Glass or PTFE stopcock',
         'purpose': 'Variable condensate return for F1 (reflux ratio) testing',
         'est_cost_usd': 25, 'sourcing': 'Lab glass supplier'},
        {'item': 'Collection diversion tee', 'type': 'Glass Y-connector with stopcocks',
         'purpose': 'Condensate routing for packet execution',
         'est_cost_usd': 30, 'sourcing': 'Lab glass supplier'},
    ],
    'family_coverage': {
        'A1_possible': True,
        'A1_notes': 'Open head, no recirculation, bath heating',
        'A2_possible': True,
        'A2_notes': 'Sealed joints + recirculation loop active',
        'A3_possible': True,
        'A3_notes': 'Intermediate: partial seal, collection without full recirculation',
    },
    'est_additional_cost_usd': 175,
    'est_total_cost_usd': 735,
}

# Level 3: Pelican-Faithful Analog
LEVEL_3 = {
    'name': 'Pelican-Faithful Analog',
    'build_time': 'Commissioned or custom glass; weeks to months for fabrication',
    'purpose': 'Historical-physical convergence. Not required for initial validation. '
               'Provides closest match to manuscript iconography.',
    'experiments_enabled': ['E0-E6 (all)'],
    'additions_over_level_2': [
        {'item': 'Pelican body with side arms', 'type': 'Custom borosilicate',
         'purpose': 'Historical pelican geometry with recirculatory return',
         'est_cost_usd': 300, 'sourcing': 'Scientific glass blower'},
        {'item': 'Interchangeable head configurations', 'type': 'Open head, sealed head, '
         'collection adapter', 'purpose': 'Switch between A1/A2/A3 modes on same body',
         'est_cost_usd': 150, 'sourcing': 'Scientific glass blower'},
        {'item': 'Bath container', 'type': 'Glass or copper vessel',
         'purpose': 'Water bath for A1 balneum mode',
         'est_cost_usd': 50, 'sourcing': 'Lab supply or coppersmith'},
    ],
    'family_coverage': {
        'A1_possible': True,
        'A1_notes': 'Bath mode with open head',
        'A2_possible': True,
        'A2_notes': 'Full pelican recirculation with sealed head',
        'A3_possible': True,
        'A3_notes': 'Collection adapter with partial recirculation',
    },
    'est_additional_cost_usd': 500,
    'est_total_cost_usd': 1235,
}

# Optional data pipeline (all levels)
DATA_PIPELINE = {
    'compute': {
        'item': 'Jetson Xavier or Raspberry Pi 4',
        'purpose': 'Data logging, sensor fusion, real-time CTS_phys computation',
        'est_cost_usd': 100,
        'notes': 'Jetson preferred for FLIR integration; RPi sufficient for thermocouple-only',
    },
    'software': {
        'item': 'Python data pipeline',
        'purpose': 'Sensor ingestion, derived channel computation, event annotation',
        'est_cost_usd': 0,
        'notes': 'Custom scripts using this project framework',
    },
    'storage': {
        'item': 'USB SSD or SD card',
        'purpose': 'Local data storage for experiment sessions',
        'est_cost_usd': 20,
    },
}


def main():
    with open(os.path.join(RESULTS_DIR, 't0_data_assembly.json')) as f:
        t0 = json.load(f)

    # Count required vs optional monitoring items
    n_required_monitoring = sum(1 for item in COMMON_MONITORING if item['required'])
    n_optional_monitoring = sum(1 for item in COMMON_MONITORING if not item['required'])
    monitoring_cost = sum(item['est_cost_usd'] for item in COMMON_MONITORING)
    consumable_cost = sum(item['est_cost_usd'] for item in COMMON_CONSUMABLES)

    output = {
        'metadata': {
            'phase': '582',
            'script': 't5_equipment_specification.py',
            'n_levels': 3,
        },
        'common_monitoring': COMMON_MONITORING,
        'common_safety': COMMON_SAFETY,
        'common_consumables': COMMON_CONSUMABLES,
        'level_1_mvp': LEVEL_1,
        'level_2_recirculatory': LEVEL_2,
        'level_3_pelican': LEVEL_3,
        'data_pipeline': DATA_PIPELINE,
        'cost_summary': {
            'monitoring_equipment': monitoring_cost,
            'consumables_per_series': consumable_cost,
            'level_1_total': LEVEL_1['est_total_cost_usd'],
            'level_2_total': LEVEL_2['est_total_cost_usd'],
            'level_3_total': LEVEL_3['est_total_cost_usd'],
            'notes': 'All costs approximate USD. FLIR camera is largest single cost. '
                    'Level 1 is functional without FLIR.',
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't5_equipment_specification.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("T5: Equipment specification complete")
    print(f"  Monitoring items: {n_required_monitoring} required, "
          f"{n_optional_monitoring} optional")
    print(f"  Safety items: {len(COMMON_SAFETY)}")
    print(f"  Rig levels:")
    for level in [LEVEL_1, LEVEL_2, LEVEL_3]:
        families = [f for f in ['A1', 'A2', 'A3']
                    if level['family_coverage'].get(f'{f}_possible')]
        print(f"    {level['name']}: ~${level['est_total_cost_usd']} "
              f"(families: {', '.join(families)})")
    print(f"  Output: {out_path}")


if __name__ == '__main__':
    main()
