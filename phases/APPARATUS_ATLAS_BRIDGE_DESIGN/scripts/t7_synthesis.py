"""T7: Synthesis for Phase 582.

Load T0-T6 results, write C1675-C1680, generate five output documents.
"""
import json
import os

PHASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PHASE_DIR, 'results')


def load_result(name):
    with open(os.path.join(RESULTS_DIR, name)) as f:
        return json.load(f)


def write_doc(filename, content):
    path = os.path.join(PHASE_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


def generate_apparatus_atlas(t0, t1, t5):
    """Output 1: APPARATUS_ATLAS.md"""
    knob_map = t1['knob_map']
    family_analogs = t1['family_analogs']
    landscape_classes = t1['landscape_classes']
    pc_clusters = t1['pc_knob_clusters']
    family_positions = t1['family_manifold_positions']
    level1 = t5['level_1_mvp']
    level2 = t5['level_2_recirculatory']
    level3 = t5['level_3_pelican']

    lines = []
    lines.append("# Apparatus Atlas\n")
    lines.append("**Phase 582: APPARATUS_ATLAS_BRIDGE_DESIGN**\n")
    lines.append("## Executive Summary\n")
    lines.append("This atlas maps the abstract apparatus response manifold (5.88 effective dimensions, "
                 "76 folios) to physical control surfaces and observable configurations. "
                 "The bridge is NOT instruction-to-action translation but rather:\n")
    lines.append("> **Manifold position / closure morphology / process metric regime "
                 "-> physical knob setting / observable response family**\n")
    lines.append("All physical mappings are Tier 3-4 interpretation. "
                 "Structural evidence underlying them is Tier 0-2.\n")

    # F1-F5 knob mapping table
    lines.append("## F-Axis to Physical Knob Mapping (Core)\n")
    lines.append("| Axis | Name | Physical Knob Candidates | Knob Class | Tier |")
    lines.append("|------|------|-------------------------|------------|------|")
    for f_key, info in knob_map.items():
        knobs = '; '.join(info['physical_knobs'][:3])
        lines.append(f"| {f_key} | {info['name']} | {knobs} | {info['knob_class']} | {info['tier']} |")
    lines.append("")

    lines.append("### Knob Classification\n")
    for cls, desc in t1['knob_classes'].items():
        lines.append(f"- **{cls}**: {desc}")
    lines.append("")

    # PC-to-knob clusters
    lines.append("## PC-to-Knob Cluster Mapping\n")
    lines.append("| PC | Variance | Top Feature | Loading | Physical Cluster |")
    lines.append("|----|----------|-------------|---------|-----------------|")
    for pc_key, cluster in pc_clusters.items():
        var = f"{cluster['variance_explained']:.1%}"
        if cluster['top_features']:
            feat, load = cluster['top_features'][0]
            knob_cluster = cluster['physical_knob_cluster']
            phys = knob_cluster[0]['physical_knobs'][0] if knob_cluster else 'N/A'
        else:
            feat, load, phys = 'N/A', 0, 'N/A'
        lines.append(f"| {pc_key} | {var} | {feat} | {load:+.4f} | {phys} |")
    lines.append("")

    # Family analog definitions
    lines.append("## Family Analog Definitions\n")
    for fname, fdef in family_analogs.items():
        lines.append(f"### {fname}\n")
        lines.append(f"**Physical analog:** {fdef['physical_analog']}\n")
        lines.append(f"**Dominant knob axis:** {fdef['dominant_knob_axis']}\n")
        lines.append(f"**CCS1 typical:** {fdef['ccs1_typical']}\n")
        lines.append("**Key differentiators:**\n")
        for diff in fdef['key_differentiators']:
            lines.append(f"- {diff}")
        lines.append("")
        if fname in family_positions:
            pos = family_positions[fname]
            lines.append(f"**Manifold position** ({pos['n_folios']} folios): "
                        f"{', '.join(f'{k}={v:+.3f}' for k, v in list(pos['mean_pc_coordinates'].items())[:3])}\n")

    # Landscape classes
    lines.append("## Landscape Class Physical Interpretations\n")
    lines.append("| Class | Name | Physical Regime | Observable Behavior |")
    lines.append("|-------|------|----------------|-------------------|")
    for lc_key, lc_def in landscape_classes.items():
        lines.append(f"| {lc_key} | {lc_def['name']} | {lc_def['physical_regime']} | "
                    f"{lc_def['observable_behavior']} |")
    lines.append("")

    # Per-folio assignment table (abbreviated)
    lines.append("## Per-Folio Apparatus Assignment\n")
    lines.append(f"Total folios: {len(t0['per_folio'])}\n")
    lines.append("| Folio | Family | Landscape | Section |")
    lines.append("|-------|--------|-----------|---------|")
    for folio, data in sorted(t0['per_folio'].items()):
        lines.append(f"| {folio} | {data['family']} | "
                    f"{data.get('landscape_class', '')} | {data.get('section', '')} |")
    lines.append("")

    # Equipment shopping list (embedded)
    lines.append("## Equipment Specification (3 Levels)\n")
    for level_name, level_data in [('Level 1: MVP', level1),
                                    ('Level 2: Recirculatory', level2),
                                    ('Level 3: Pelican', level3)]:
        lines.append(f"### {level_name} (~${level_data['est_total_cost_usd']})\n")
        lines.append(f"**Purpose:** {level_data['purpose']}\n")
        lines.append(f"**Build time:** {level_data['build_time']}\n")
        fc = level_data['family_coverage']
        families = [f for f in ['A1', 'A2', 'A3'] if fc.get(f'{f}_possible')]
        lines.append(f"**Family coverage:** {', '.join(families)}\n")

    # Monitoring
    lines.append("### Common Monitoring Equipment\n")
    for item in t5['common_monitoring']:
        req = "REQUIRED" if item['required'] else "optional"
        lines.append(f"- {item['item']} ({req}) -- {item['purpose']}")
    lines.append("")

    lines.append("---\n")
    lines.append("*All physical mappings are Tier 3-4 interpretation. "
                 "See constraint provenance for structural evidence tiers.*\n")

    return '\n'.join(lines)


def generate_intervention_packet_library(t2):
    """Output 2: INTERVENTION_PACKET_LIBRARY.md"""
    packets = t2['packet_types']
    atlas = t2['counterfeit_closure_atlas']
    spectrum = t2['closure_strength_spectrum']
    mapping = t2['packet_experiment_mapping']

    lines = []
    lines.append("# Intervention Packet Library\n")
    lines.append("**Phase 582: APPARATUS_ATLAS_BRIDGE_DESIGN**\n")
    lines.append("## Physical Packet Type Definitions\n")
    lines.append(f"{len(packets)} packet types defined, mapping grammar closure/intervention "
                 "packets to physical operations.\n")

    lines.append("| Packet Type | Closure Strength | Physical Analog | Tier |")
    lines.append("|-------------|-----------------|-----------------|------|")
    for name, info in packets.items():
        lines.append(f"| {name} | {info['closure_strength']} | "
                    f"{info['physical_analog'][:60]}... | {info['tier']} |")
    lines.append("")

    for name, info in packets.items():
        lines.append(f"### {name}\n")
        lines.append(f"**Grammar origin:** {info['grammar_origin']}\n")
        lines.append(f"**Physical analog:** {info['physical_analog']}\n")
        lines.append(f"**Expected effect:** {info['expected_effect']}\n")
        lines.append(f"**Closure strength:** {info['closure_strength']}\n")
        lines.append(f"**Constraint basis:** {', '.join(info['constraint_basis'])}\n")
        if name in mapping:
            lines.append(f"**Experiment:** {mapping[name]}\n")

    # Counterfeit closure atlas
    lines.append("## Counterfeit Closure Atlas\n")
    for family, fdata in atlas.items():
        lines.append(f"### {family}\n")
        lines.append(f"**Acceptance:** {fdata['acceptance']}\n")
        lines.append(f"**Minimum CTS_phys:** {fdata['minimum_cts_phys']}\n")
        lines.append(f"**Tuning direction:** {fdata['tuning_direction']}\n")
        lines.append("**Distinguishing sensors:**\n")
        for sensor in fdata['distinguishing_sensors']:
            lines.append(f"- {sensor}")
        lines.append("")

    # Closure strength spectrum
    lines.append("## Closure Strength Spectrum\n")
    lines.append("| Level | Packets | Expected DYE | A2 Productive? |")
    lines.append("|-------|---------|-------------|---------------|")
    for level in spectrum:
        pkts = ', '.join(level['packets'][:3])
        lines.append(f"| {level['level']} | {pkts} | "
                    f"{level['expected_dye']} | {level['a2_productive']} |")
    lines.append("")

    lines.append("---\n")
    lines.append("*All packet definitions are Tier 2-3. Grammar provenance is Tier 0-2.*\n")

    return '\n'.join(lines)


def generate_physical_metrics_schema(t3):
    """Output 3: PHYSICAL_METRICS_SCHEMA.md"""
    metrics = t3['metrics']
    nulls = t3['hardware_nulls']
    data_model = t3['data_model']

    lines = []
    lines.append("# Physical Metrics Schema\n")
    lines.append("**Phase 582: APPARATUS_ATLAS_BRIDGE_DESIGN**\n")
    lines.append("## Metric Definitions\n")
    lines.append(f"{len(metrics)} virtual process metrics mapped to physical analogs.\n")

    for name, defn in metrics.items():
        lines.append(f"### {name}: {defn['name']}\n")
        lines.append(f"**Virtual source:** {defn['virtual_source']}\n")
        lines.append(f"**Definition:** {defn['definition']}\n")
        lines.append(f"**Formula:** `{defn['formula']}`\n")
        lines.append(f"**Interpretation:** {defn['interpretation']}\n")
        lines.append(f"**Required sensors:** {', '.join(defn['required_sensors'])}\n")
        if defn['optional_sensors']:
            lines.append(f"**Optional sensors:** {', '.join(defn['optional_sensors'])}\n")
        if defn['components']:
            lines.append("**Components:**\n")
            for comp in defn['components']:
                lines.append(f"- {comp['channel']}: {comp['sensor']} "
                            f"({comp['unit']}, weight={comp['weight']})")
            lines.append("")
        lines.append(f"**Constraint basis:** {', '.join(defn['constraint_basis'])}\n")

    # Data model
    lines.append("## Data Model\n")
    lines.append(f"**Synchronization:** {data_model['synchronization']}\n")

    lines.append("### Raw Channels\n")
    lines.append("| Channel | Sensor | Rate | Unit | Required |")
    lines.append("|---------|--------|------|------|----------|")
    for ch in data_model['raw_channels']:
        lines.append(f"| {ch['name']} | {ch['sensor']} | {ch['rate_hz']} Hz | "
                    f"{ch['unit']} | {'Yes' if ch['required'] else 'No'} |")
    lines.append("")

    lines.append("### Derived Channels\n")
    lines.append("| Channel | Formula | Unit |")
    lines.append("|---------|---------|------|")
    for ch in data_model['derived_channels']:
        lines.append(f"| {ch['name']} | {ch['formula']} | {ch['unit']} |")
    lines.append("")

    lines.append("### Trigger Annotations\n")
    for ann in data_model['trigger_annotations']:
        lines.append(f"- `{ann}`")
    lines.append("")

    lines.append("### Event Windows\n")
    for window, desc in data_model['event_windows'].items():
        lines.append(f"- **{window}:** {desc}")
    lines.append("")

    # Hardware nulls
    lines.append("## Hardware Null Conditions\n")
    lines.append(f"{len(nulls)} null conditions for controlled experimentation.\n")
    lines.append("| Null | Controls For | Expected Result |")
    lines.append("|------|-------------|-----------------|")
    for name, null in nulls.items():
        lines.append(f"| {name} | {null['controls_for']} | {null['expected_result'][:60]}... |")
    lines.append("")

    for name, null in nulls.items():
        lines.append(f"### {name}\n")
        lines.append(f"**Description:** {null['description']}\n")
        lines.append(f"**Controls for:** {null['controls_for']}\n")
        lines.append(f"**Procedure:** {null['physical_procedure']}\n")
        lines.append(f"**Expected result:** {null['expected_result']}\n")

    lines.append("---\n")
    lines.append("*All metric definitions are Tier 3. Formula details are interpretive. "
                 "Sensor specifications are practical recommendations.*\n")

    return '\n'.join(lines)


def generate_operator_bridge_manual(t4):
    """Output 4: OPERATOR_BRIDGE_MANUAL.md"""
    lines = []
    lines.append("# Operator Bridge Manual\n")
    lines.append("**Phase 582: APPARATUS_ATLAS_BRIDGE_DESIGN**\n")
    lines.append("> **IMPORTANT:** This document is a SECONDARY HEURISTIC LAYER. "
                 "The primary bridge is the manifold-to-knob mapping (APPARATUS_ATLAS.md). "
                 "These interpretations are convenient operator-facing summaries, "
                 "NOT the load-bearing structural bridge.\n")

    # Line control cycle
    lines.append("## Line-Level Control Cycle (Heuristic)\n")
    lines.append("| Zone | Quintile | Physical Heuristic |")
    lines.append("|------|----------|-------------------|")
    for zone, info in t4['line_control_cycle'].items():
        lines.append(f"| {zone} | {info['quintile']} | {info['physical_heuristic']} |")
    lines.append("")

    # Macro-state modes
    lines.append("## Macro-State to Operator Mode (Heuristic)\n")
    lines.append("| Macro-State | Operator Mode | Physical Action |")
    lines.append("|-------------|---------------|----------------|")
    for ms, info in t4['macro_state_modes'].items():
        lines.append(f"| {ms} | {info['operator_mode']} | {info['physical_action'][:60]}... |")
    lines.append("")

    # REGIME fire mapping
    lines.append("## REGIME to Fire Degree (Heuristic)\n")
    lines.append("| REGIME | Brunschwig Degree | CEI | Setup |")
    lines.append("|--------|-------------------|-----|-------|")
    for reg, info in t4['regime_fire_mapping'].items():
        lines.append(f"| {reg} | {info['brunschwig_degree']} | {info['CEI']} | "
                    f"{info['setup_heuristic']} |")
    lines.append("")

    # Section apparatus style
    lines.append("## Section to Apparatus Style (Modulation Only)\n")
    for sec, info in t4['section_apparatus_style'].items():
        lines.append(f"- **Section {sec}:** {info['apparatus_relevance']} -- "
                    f"{info['physical_implication']}")
    lines.append("")

    # Softened labels
    lines.append("## Softened Semantic Labels\n")
    for label, info in t4['softened_labels'].items():
        lines.append(f"### {label}\n")
        lines.append(f"- **Old label:** {info['old_label']}")
        lines.append(f"- **Corrected label:** {info['corrected_label']}")
        lines.append(f"- **Reason:** {info['reason']}")
        lines.append("")

    # Safety architecture
    lines.append("## Safety Architecture (Three Levels)\n")
    for level, info in t4['safety_architecture'].items():
        lines.append(f"### {level}\n")
        lines.append(f"**Structural mechanism:** {info['structural_mechanism']}\n")
        lines.append(f"**Physical protocol:** {info['physical_protocol']}\n")
        lines.append(f"**Constraint basis:** {', '.join(info['constraint_basis'])}\n")

    # Hazard classes
    lines.append("## Five Hazard Classes\n")
    lines.append("| Class | Fraction | Physical Failure | Prevention |")
    lines.append("|-------|----------|-----------------|------------|")
    for hc, info in t4['hazard_classes'].items():
        lines.append(f"| {hc} | {info['fraction']:.0%} | "
                    f"{info['physical_failure']} | {info['prevention'][:50]}... |")
    lines.append("")

    # Judgment boundaries
    lines.append("## Operator Judgment Boundaries\n")
    lines.append(f"> {t4['judgment_boundaries']['interpretation']}\n")
    lines.append("### Encodable / Automatable\n")
    for item in t4['judgment_boundaries']['encodable_automatable']:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("### Non-Encodable / Operator-Judged\n")
    for item in t4['judgment_boundaries']['non_encodable_operator_judged']:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("---\n")
    lines.append("*All interpretations in this document are Tier 3 heuristics unless "
                 "otherwise noted. Safety protocols derive from Tier 2 constraints.*\n")

    return '\n'.join(lines)


def generate_validation_protocol(t6, t3):
    """Output 5: VALIDATION_PROTOCOL.md"""
    experiments = t6['experiments']

    lines = []
    lines.append("# Validation Protocol\n")
    lines.append("**Phase 582: APPARATUS_ATLAS_BRIDGE_DESIGN**\n")
    lines.append("## Experiment Order\n")
    lines.append("Order matters -- each experiment builds on the previous.\n")
    for i, exp_name in enumerate(t6['experiment_order']):
        lines.append(f"{i}. {exp_name}")
    lines.append("")

    # Overview table
    lines.append("## Overview\n")
    lines.append("| Experiment | Level | Min Runs | Priority | Constraints Tested |")
    lines.append("|------------|-------|----------|----------|--------------------|")
    for name, exp in experiments.items():
        constraints = ', '.join(exp['constraints_tested'][:3]) or 'N/A'
        lines.append(f"| {exp['name']} | {exp['equipment_level']} | "
                    f"{exp['minimum_runs']} | {exp['priority']} | {constraints} |")
    lines.append("")

    # Detailed experiments
    for name, exp in experiments.items():
        lines.append(f"## {exp['name']}\n")
        lines.append(f"**Priority:** {exp['priority']}\n")
        lines.append(f"**Purpose:** {exp['purpose']}\n")
        lines.append(f"**Equipment level:** {exp['equipment_level']}\n")
        lines.append(f"**Minimum runs:** {exp['minimum_runs']}\n")

        lines.append("### Measurements\n")
        for m in exp['measurements']:
            lines.append(f"- {m}")
        lines.append("")

        lines.append("### Procedure\n")
        for step in exp['procedure']:
            lines.append(f"{step}")
        lines.append("")

        lines.append("### Pass/Fail Criteria\n")
        for crit in exp['pass_criteria']:
            lines.append(f"- {crit}")
        lines.append("")

        if exp['hardware_nulls_used']:
            lines.append(f"**Hardware nulls:** {', '.join(exp['hardware_nulls_used'])}\n")
        if exp['constraints_tested']:
            lines.append(f"**Constraints tested:** {', '.join(exp['constraints_tested'])}\n")

    # Statistical notes
    lines.append("## Statistical Notes\n")
    for key, value in t6['statistical_notes'].items():
        lines.append(f"- **{key}:** {value}")
    lines.append("")

    # Safety
    lines.append("## Safety Precautions\n")
    for precaution in t6['safety_precautions']:
        lines.append(f"- {precaution}")
    lines.append("")

    lines.append("---\n")
    lines.append("*All experiments are Tier 3-4. Pass/fail criteria are interpretive "
                 "predictions, not structural guarantees.*\n")

    return '\n'.join(lines)


def main():
    # Load all results
    t0 = load_result('t0_data_assembly.json')
    t1 = load_result('t1_manifold_knob_mapping.json')
    t2 = load_result('t2_intervention_packet_library.json')
    t3 = load_result('t3_physical_metrics_schema.json')
    t4 = load_result('t4_operator_bridge.json')
    t5 = load_result('t5_equipment_specification.json')
    t6 = load_result('t6_validation_protocol.json')

    # Collect constraint verdicts
    c1675_n_components = len(t1['knob_map']) + len(t2['packet_types']) + len(t3['metrics'])
    if c1675_n_components >= 20:
        c1675_verdict = 'ATLAS_COMPLETE'
    elif c1675_n_components >= 12:
        c1675_verdict = 'ATLAS_PARTIAL'
    else:
        c1675_verdict = 'ATLAS_INSUFFICIENT'

    constraints = {
        'C1675': {
            'verdict': c1675_verdict,
            'claim': 'Component atlas coverage',
            'n_knob_axes': len(t1['knob_map']),
            'n_packet_types': len(t2['packet_types']),
            'n_metrics': len(t3['metrics']),
            'n_total_components': c1675_n_components,
            'rationale': (f'{c1675_n_components} total atlas components: '
                         f'{len(t1["knob_map"])} knob axes, '
                         f'{len(t2["packet_types"])} packet types, '
                         f'{len(t3["metrics"])} metrics'),
            'tier': 3,
        },
        'C1676': t4['C1676'],
        'C1677': t4['C1677'],
        'C1678': t6['C1678'],
        'C1679': t3['C1679'],
        'C1680': t1['C1680'],
    }

    # Generate output documents
    doc_paths = {}
    doc_paths['APPARATUS_ATLAS'] = write_doc(
        'APPARATUS_ATLAS.md', generate_apparatus_atlas(t0, t1, t5))
    doc_paths['INTERVENTION_PACKET_LIBRARY'] = write_doc(
        'INTERVENTION_PACKET_LIBRARY.md', generate_intervention_packet_library(t2))
    doc_paths['PHYSICAL_METRICS_SCHEMA'] = write_doc(
        'PHYSICAL_METRICS_SCHEMA.md', generate_physical_metrics_schema(t3))
    doc_paths['OPERATOR_BRIDGE_MANUAL'] = write_doc(
        'OPERATOR_BRIDGE_MANUAL.md', generate_operator_bridge_manual(t4))
    doc_paths['VALIDATION_PROTOCOL'] = write_doc(
        'VALIDATION_PROTOCOL.md', generate_validation_protocol(t6, t3))

    # Write synthesis JSON
    output = {
        'metadata': {
            'phase': '582',
            'script': 't7_synthesis.py',
            'n_documents_generated': len(doc_paths),
            'n_constraints_decided': len(constraints),
        },
        'constraints': constraints,
        'documents': {name: path for name, path in doc_paths.items()},
        'summary': {
            'knob_axes_mapped': f"{len(t1['knob_map'])}/5",
            'packet_types_defined': len(t2['packet_types']),
            'metrics_bridged': f"{t3['C1679']['n_metrics_defined']}/5",
            'experiments_feasible': f"{t6['C1678']['n_feasible']}/{t6['C1678']['n_total']}",
            'hazard_classes_mapped': t4['C1677']['n_hazard_classes_mapped'],
            'safety_levels': t4['C1677']['n_safety_levels'],
            'total_folios': len(t0['per_folio']),
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't7_synthesis.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print("T7: Synthesis complete")
    print(f"  Documents generated: {len(doc_paths)}")
    for name, path in doc_paths.items():
        print(f"    {name}: {path}")
    print(f"\n  Constraints decided:")
    for cid, cdata in constraints.items():
        print(f"    {cid}: {cdata['verdict']}")
    print(f"\n  Summary:")
    for key, value in output['summary'].items():
        print(f"    {key}: {value}")
    print(f"\n  Output: {out_path}")


if __name__ == '__main__':
    main()
