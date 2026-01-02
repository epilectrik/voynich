"""
Exploratory Process Mapping Analysis
Post-lock speculative process alignment for Voynich control programs
"""

import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple
import statistics

# Load data
with open('control_signatures.json', 'r') as f:
    sig_data = json.load(f)
    signatures = sig_data['signatures']

with open('forward_inference_results.json', 'r') as f:
    inference_data = json.load(f)
    clusters = inference_data['lane1']['clusters']
    templates = inference_data['lane1']['templates']

with open('lane3_material_class_results.json', 'r') as f:
    material_data = json.load(f)

with open('optionA_geometry_results.json', 'r') as f:
    geometry_data = json.load(f)

# ============================================================================
# TASK 1: PROGRAM ROLE TAXONOMY
# ============================================================================

@dataclass
class ProgramProfile:
    folio: str
    link_density: float
    kernel_contact_ratio: float
    hazard_density: float
    cycle_regularity: float
    intervention_frequency: float
    recovery_ops_count: int
    near_miss_count: int
    total_length: int
    reset_present: bool
    terminal_state: str
    max_consecutive_link: int
    cluster: str
    template: str

def classify_program(p: ProgramProfile) -> Dict[str, str]:
    """Classify program into operational roles based on signature metrics."""
    roles = {}

    # Stability role
    if p.link_density > 0.45 and p.near_miss_count < 10:
        roles['stability'] = 'ULTRA_CONSERVATIVE'
    elif p.link_density > 0.35 and p.hazard_density < 0.55:
        roles['stability'] = 'CONSERVATIVE'
    elif p.hazard_density > 0.62 and p.near_miss_count > 15:
        roles['stability'] = 'AGGRESSIVE'
    else:
        roles['stability'] = 'MODERATE'

    # Waiting behavior
    if p.link_density > 0.5 and p.max_consecutive_link > 6:
        roles['waiting'] = 'LINK_HEAVY_EXTENDED'
    elif p.link_density > 0.4:
        roles['waiting'] = 'LINK_HEAVY'
    elif p.link_density < 0.32:
        roles['waiting'] = 'LINK_SPARSE'
    else:
        roles['waiting'] = 'LINK_MODERATE'

    # Convergence behavior
    if p.cycle_regularity > 4.0 and p.terminal_state == 'STATE-C':
        roles['convergence'] = 'FAST_STABLE'
    elif p.cycle_regularity < 2.5:
        roles['convergence'] = 'IRREGULAR'
    elif p.terminal_state == 'STATE-C':
        roles['convergence'] = 'REGULAR_STABLE'
    else:
        roles['convergence'] = 'REGULAR_OPEN'

    # Recovery posture
    if p.recovery_ops_count > 15:
        roles['recovery'] = 'HIGHLY_RECOVERABLE'
    elif p.recovery_ops_count > 5:
        roles['recovery'] = 'RECOVERABLE'
    else:
        roles['recovery'] = 'LOW_RECOVERY'

    # Program scale
    if p.total_length > 800:
        roles['scale'] = 'EXTENDED'
    elif p.total_length < 280:
        roles['scale'] = 'COMPACT'
    else:
        roles['scale'] = 'STANDARD'

    # Special markers
    if p.reset_present:
        roles['special'] = 'RESTART_CAPABLE'
    elif p.intervention_frequency > 8:
        roles['special'] = 'HIGH_INTERVENTION'
    else:
        roles['special'] = 'NONE'

    return roles

# Build cluster membership lookup
folio_to_cluster = {}
for cluster_id, cluster_info in clusters.items():
    for folio in cluster_info['members']:
        folio_to_cluster[folio] = {
            'cluster': cluster_id,
            'template': cluster_info['best_template']
        }

# Analyze all programs
programs = []
for folio, sig in signatures.items():
    cluster_info = folio_to_cluster.get(folio, {'cluster': 'unknown', 'template': 'unknown'})
    p = ProgramProfile(
        folio=folio,
        link_density=sig['link_density'],
        kernel_contact_ratio=sig['kernel_contact_ratio'],
        hazard_density=sig['hazard_density'],
        cycle_regularity=sig['cycle_regularity'],
        intervention_frequency=sig['intervention_frequency'],
        recovery_ops_count=sig['recovery_ops_count'],
        near_miss_count=sig['near_miss_count'],
        total_length=sig['total_length'],
        reset_present=sig['reset_present'],
        terminal_state=sig['terminal_state'],
        max_consecutive_link=sig['max_consecutive_link'],
        cluster=cluster_info['cluster'],
        template=cluster_info['template']
    )
    programs.append(p)

# Classify all programs
program_classifications = {}
for p in programs:
    program_classifications[p.folio] = {
        'profile': p,
        'roles': classify_program(p)
    }

# Aggregate role statistics
role_counts = defaultdict(lambda: defaultdict(int))
for folio, data in program_classifications.items():
    for dimension, role in data['roles'].items():
        role_counts[dimension][role] += 1

# Find representative programs for each role
representatives = {}
for dimension in ['stability', 'waiting', 'convergence', 'recovery', 'scale', 'special']:
    representatives[dimension] = {}
    for folio, data in program_classifications.items():
        role = data['roles'][dimension]
        if role not in representatives[dimension]:
            representatives[dimension][role] = []
        representatives[dimension][role].append(data['profile'])

# ============================================================================
# TASK 2: PROCESS FAMILY ALIGNMENT
# ============================================================================

process_families = {
    'CONTINUOUS_EXTRACTION': {
        'description': 'Gradual removal of mobile fractions through circulation',
        'required_traits': ['closed_loop', 'continuous', 'no_phase_change', 'gradual'],
        'fits': [
            'LINK encodes waiting for mobility-limited transport',
            'High kernel contact = active driving of flow',
            'Low hazard density = avoidance of concentration spikes',
            'Explains program diversity: different substrates need different extraction rates'
        ],
        'fails_to_explain': [
            'Why some programs have very high intervention frequencies',
            'The specific meaning of recovery operations'
        ],
        'alignment_strength': 'STRONG'
    },
    'CIRCULATION_CONDITIONING': {
        'description': 'Continuous circulation to maintain material in target state',
        'required_traits': ['closed_loop', 'indefinite', 'stability_focused'],
        'fits': [
            'LINK-heavy programs = extended waiting for equilibration',
            'STATE-C convergence = target state maintenance',
            'Low LINK programs = faster refresh cycles',
            'Explains 100% convergence: all programs reach stable maintenance'
        ],
        'fails_to_explain': [
            'Why 6 extended runs are structurally necessary',
            'The specific distinction between recovery operations'
        ],
        'alignment_strength': 'STRONG'
    },
    'REDISTRIBUTION_PROCESS': {
        'description': 'Progressive movement of components between regions',
        'required_traits': ['closed_loop', 'gradual', 'no_endpoint'],
        'fits': [
            'Cycle regularity = periodic refresh of concentration gradients',
            'Hazard topology = preventing runaway concentration',
            'Near-miss counts = operating near concentration limits',
            'Explains compact vs extended: different redistribution depths'
        ],
        'fails_to_explain': [
            'Why material CLASS_C fails specifically',
            'The role of reset-present programs'
        ],
        'alignment_strength': 'MODERATE'
    },
    'BREAKDOWN_DIGESTION': {
        'description': 'Gradual transformation of material through circulation',
        'required_traits': ['continuous', 'cumulative', 'irreversible_direction'],
        'fits': [
            'Long programs = extended processing time',
            'Recovery ops = handling intermediate states',
            'Kernel contact = driving transformation',
            'Explains LINK: allowing time for slow transformations'
        ],
        'fails_to_explain': [
            'Perfect reversibility of hazard boundaries (all bidirectional)',
            'Why CLASS_C (phase-unstable) fails but swelling materials work'
        ],
        'alignment_strength': 'WEAK'
    },
    'SEPARATION_BY_MOBILITY': {
        'description': 'Differential movement of fractions based on transport properties',
        'required_traits': ['circulation', 'differential_rates', 'stability'],
        'fits': [
            'Template diversity = different mobility profiles',
            'LINK = waiting for slower fractions to equilibrate',
            'Geometry selectivity = needs defined flow paths',
            'Explains CLASS_D compatibility: rapid diffusion enables separation'
        ],
        'fails_to_explain': [
            'Why no endpoint signals exist in the grammar',
            'The specific role of near-miss operations'
        ],
        'alignment_strength': 'MODERATE'
    },
    'MAINTENANCE_HOLDING': {
        'description': 'Keeping material in stable operating regime indefinitely',
        'required_traits': ['indefinite', 'stability', 'low_change_rate'],
        'fits': [
            'Ultra-conservative programs = pure maintenance',
            'LINK-heavy = minimal intervention needed',
            'Low intervention frequency = stable holding',
            '100% STATE-C convergence = all programs can maintain'
        ],
        'fails_to_explain': [
            'High hazard density in some programs',
            'Extended run programs (12.6% envelope gap)'
        ],
        'alignment_strength': 'MODERATE'
    }
}

# ============================================================================
# TASK 3: OUTCOME-LEVEL PATTERNS
# ============================================================================

outcome_patterns = {
    'INCREASED_HOMOGENEITY': {
        'evidence': [
            'STRUCTURALLY SUPPORTED: 100% convergence to STATE-C',
            'STRUCTURALLY SUPPORTED: Cycle regularity decreases variance',
            'SPECULATIVE BUT CONSISTENT: Circulation averaging perturbations'
        ],
        'mechanism': 'Repeated circulation through controlled path reduces spatial variation',
        'metric_support': {
            'convergence_rate': '100% across all compatible geometries',
            'state_c_time': '>99.8% in G4/G5 geometries'
        }
    },
    'INCREASED_MOBILITY': {
        'evidence': [
            'SPECULATIVE BUT CONSISTENT: CLASS_D (rapid diffusion) most compatible',
            'SPECULATIVE BUT CONSISTENT: LINK effectiveness higher in closed loops',
            'WEAK: Extended programs might allow greater mobility change'
        ],
        'mechanism': 'Circulation increases effective diffusion paths',
        'metric_support': {
            'class_d_convergence': '100%',
            'link_effectiveness_g5': '1.35 (highest)'
        }
    },
    'PROGRESSIVE_CONCENTRATION': {
        'evidence': [
            'SPECULATIVE BUT CONSISTENT: Hazard boundaries = concentration limits',
            'SPECULATIVE BUT CONSISTENT: Near-miss counts = operating near limits',
            'WEAK: No direct evidence of concentration endpoint'
        ],
        'mechanism': 'Selective retention/release at circulation boundaries',
        'metric_support': {
            'mean_near_miss': '~15 per program',
            'hazard_density_range': '0.40-0.67'
        }
    },
    'GRADUAL_STABILIZATION': {
        'evidence': [
            'STRUCTURALLY SUPPORTED: LINK-heavy programs = safer (d=1.60)',
            'STRUCTURALLY SUPPORTED: Slower reconvergence with high LINK',
            'STRUCTURALLY SUPPORTED: All programs reach STATE-C eventually'
        ],
        'mechanism': 'Repeated damped cycles reduce excursions from target',
        'metric_support': {
            'link_stability_advantage': 'p<0.0001, d=1.60',
            'convergence': '100%'
        }
    },
    'MAINTENANCE_OF_TARGET_STATE': {
        'evidence': [
            'STRUCTURALLY SUPPORTED: STATE-C is universal endpoint',
            'STRUCTURALLY SUPPORTED: Kernel contact ratio ~60% (sustained control)',
            'STRUCTURALLY SUPPORTED: No drift detected in extended programs'
        ],
        'mechanism': 'Continuous feedback maintains operating point',
        'metric_support': {
            'kernel_contact_mean': '62%',
            'state_c_fraction': '100% convergence'
        }
    }
}

# ============================================================================
# TASK 4: NEGATIVE PROCESS MATCHES
# ============================================================================

negative_matches = {
    'PHASE_CHANGE_PROCESSES': {
        'incompatibility': 'STRONG',
        'evidence': [
            'CLASS_C (phase-unstable) = only failing material class',
            '480/480 CLASS_C failures = PHASE_COLLAPSE mode',
            '17 forbidden transitions include phase-ordering violations'
        ],
        'why_fails': 'Grammar explicitly avoids phase transitions. No reset-from-phase-change available.',
        'examples': 'Crystallization, condensation, evaporation, freezing'
    },
    'ONE_PASS_EXTRACTION': {
        'incompatibility': 'STRONG',
        'evidence': [
            'G1 (linear open flow) = 93.5% failure rate',
            'Grammar requires recirculation for stability',
            'No endpoint signals = incompatible with single-pass logic'
        ],
        'why_fails': 'Open flow cannot satisfy LINK operator physics. Perturbations propagate unchecked.',
        'examples': 'Column chromatography, single-pass filtration, flow-through extraction'
    },
    'ENDPOINT_DEFINED_RECIPES': {
        'incompatibility': 'STRONG',
        'evidence': [
            '0 identifier tokens in grammar',
            '0 translation-eligible zones',
            'No completion signals detected'
        ],
        'why_fails': 'Grammar encodes indefinite operation, not termination conditions.',
        'examples': 'Batch synthesis, reaction completion, titer testing'
    },
    'HIGH_YIELD_BATCH': {
        'incompatibility': 'STRONG',
        'evidence': [
            'G2 batch vessel = 20% LINK effectiveness (vs 135% for G5)',
            'Batch lacks intrinsic transport delay',
            'Conservation-focused grammar incompatible with draw-off'
        ],
        'why_fails': 'Batch operation lacks circulation feedback. LINK maps to nothing.',
        'examples': 'Batch fermentation, reaction vessels, holding tanks'
    },
    'RAPID_THERMAL_RAMPING': {
        'incompatibility': 'MODERATE',
        'evidence': [
            'ENERGY_OVERSHOOT = hazard class (6/17 forbidden transitions)',
            'Kernel k (energy modulator) is most central',
            'High intervention frequency programs still rare (11/83)'
        ],
        'why_fails': 'Grammar prioritizes stability over speed. Rapid ramps trigger hazards.',
        'examples': 'Flash heating, rapid quench, thermal shock protocols'
    },
    'EMULSION_PROCESSES': {
        'incompatibility': 'STRONG',
        'evidence': [
            'CLASS_C = emulsion-forming materials = 19.8% failure',
            'Failure mode = PHASE_COLLAPSE exclusively',
            'Boundary_sharpness 0.2 = lowest of failing class'
        ],
        'why_fails': 'Phase instability at boundaries defeats control logic.',
        'examples': 'Emulsification, foam formation, micelle creation'
    },
    'DISCRETE_PRODUCT_RECIPES': {
        'incompatibility': 'MODERATE',
        'evidence': [
            'Programs are continuous state maintenance, not production',
            'No batch-start or batch-end patterns detected',
            '9.8x compression = highly regular cycling, not discrete steps'
        ],
        'why_fails': 'Grammar describes operation, not product creation.',
        'examples': 'Pharmaceutical synthesis, defined-product protocols'
    }
}

# ============================================================================
# OUTPUT GENERATION
# ============================================================================

def generate_program_roles_report():
    """Generate exploratory_program_roles.md"""
    lines = []
    lines.append("# Exploratory Program Roles\n")
    lines.append("## Program Role Taxonomy\n")
    lines.append("Classification based on control signature metrics. Each program assigned roles across 6 dimensions.\n")

    # Role dimension definitions
    lines.append("### Role Dimensions\n")
    lines.append("| Dimension | Description | Metric Basis |\n")
    lines.append("|-----------|-------------|---------------|\n")
    lines.append("| Stability | How conservative vs aggressive | link_density, hazard_density, near_miss_count |\n")
    lines.append("| Waiting | LINK operator usage pattern | link_density, max_consecutive_link |\n")
    lines.append("| Convergence | Cycle behavior and terminal state | cycle_regularity, terminal_state |\n")
    lines.append("| Recovery | Error recovery posture | recovery_ops_count |\n")
    lines.append("| Scale | Program length/complexity | total_length |\n")
    lines.append("| Special | Unique markers | reset_present, intervention_frequency |\n")

    # Role distribution
    lines.append("\n### Role Distribution\n")
    for dimension in ['stability', 'waiting', 'convergence', 'recovery', 'scale', 'special']:
        lines.append(f"\n**{dimension.upper()}**\n")
        lines.append("| Role | Count | Percentage |\n")
        lines.append("|------|-------|------------|\n")
        total = sum(role_counts[dimension].values())
        for role, count in sorted(role_counts[dimension].items(), key=lambda x: -x[1]):
            pct = 100 * count / total
            lines.append(f"| {role} | {count} | {pct:.1f}% |\n")

    # Representative programs
    lines.append("\n## Representative Programs by Role\n")

    # Stability representatives
    lines.append("\n### Stability Dimension\n")
    for role in ['ULTRA_CONSERVATIVE', 'CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
        if role in representatives['stability'] and representatives['stability'][role]:
            progs = representatives['stability'][role][:3]
            prog_list = ', '.join([p.folio for p in progs])
            lines.append(f"- **{role}**: {prog_list}\n")
            if progs:
                p = progs[0]
                lines.append(f"  - Sample ({p.folio}): link_density={p.link_density:.3f}, hazard_density={p.hazard_density:.3f}, near_miss={p.near_miss_count}\n")

    # Waiting representatives
    lines.append("\n### Waiting Dimension\n")
    for role in ['LINK_HEAVY_EXTENDED', 'LINK_HEAVY', 'LINK_MODERATE', 'LINK_SPARSE']:
        if role in representatives['waiting'] and representatives['waiting'][role]:
            progs = representatives['waiting'][role][:3]
            prog_list = ', '.join([p.folio for p in progs])
            lines.append(f"- **{role}**: {prog_list}\n")
            if progs:
                p = progs[0]
                lines.append(f"  - Sample ({p.folio}): link_density={p.link_density:.3f}, max_consecutive_link={p.max_consecutive_link}\n")

    # Metric ranges
    lines.append("\n## Quantitative Metric Summary\n")
    metrics = {
        'link_density': [p.link_density for p in programs],
        'hazard_density': [p.hazard_density for p in programs],
        'kernel_contact_ratio': [p.kernel_contact_ratio for p in programs],
        'cycle_regularity': [p.cycle_regularity for p in programs],
        'intervention_frequency': [p.intervention_frequency for p in programs],
        'near_miss_count': [p.near_miss_count for p in programs],
        'recovery_ops_count': [p.recovery_ops_count for p in programs],
        'total_length': [p.total_length for p in programs]
    }

    lines.append("| Metric | Min | Max | Mean | Stdev |\n")
    lines.append("|--------|-----|-----|------|-------|\n")
    for name, values in metrics.items():
        mn, mx = min(values), max(values)
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        lines.append(f"| {name} | {mn:.3f} | {mx:.3f} | {mean:.3f} | {std:.3f} |\n")

    # Cluster-role correlation
    lines.append("\n## Cluster-Role Correlation\n")
    lines.append("How do Lane 1 template clusters map to program roles?\n")

    cluster_role_matrix = defaultdict(lambda: defaultdict(int))
    for folio, data in program_classifications.items():
        cluster = data['profile'].cluster
        stability_role = data['roles']['stability']
        cluster_role_matrix[cluster][stability_role] += 1

    lines.append("\n| Cluster | Template | ULTRA_CONS | CONSERVATIVE | MODERATE | AGGRESSIVE |\n")
    lines.append("|---------|----------|------------|--------------|----------|------------|\n")
    for cluster_id, cluster_info in sorted(clusters.items()):
        template = cluster_info['best_template']
        row = f"| {cluster_id} | {template} |"
        for role in ['ULTRA_CONSERVATIVE', 'CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
            count = cluster_role_matrix[cluster_id].get(role, 0)
            row += f" {count} |"
        lines.append(row + "\n")

    # Special programs
    lines.append("\n## Special Program Markers\n")

    reset_programs = [p.folio for p in programs if p.reset_present]
    high_intervention = [p.folio for p in programs if p.intervention_frequency > 8]
    extended_programs = [p.folio for p in programs if p.total_length > 800]

    lines.append(f"\n**RESTART_CAPABLE** ({len(reset_programs)}): {', '.join(reset_programs)}\n")
    lines.append("- These programs can return to initial state\n")
    lines.append("- **SPECULATIVE**: May represent full reset protocols or error recovery starting points\n")

    lines.append(f"\n**HIGH_INTERVENTION** ({len(high_intervention)}): {', '.join(high_intervention[:10])}{'...' if len(high_intervention) > 10 else ''}\n")
    lines.append("- Intervention frequency > 8 operations per cycle\n")
    lines.append("- **SPECULATIVE**: May handle rapidly-changing conditions or sensitive substrates\n")

    lines.append(f"\n**EXTENDED** ({len(extended_programs)}): {', '.join(extended_programs)}\n")
    lines.append("- Program length > 800 instructions\n")
    lines.append("- **STRUCTURALLY SUPPORTED**: Required for complete operational envelope (12.6% gap without)\n")

    return ''.join(lines)

def generate_process_alignment_report():
    """Generate speculative_process_alignment.md"""
    lines = []
    lines.append("# Speculative Process Family Alignment\n")
    lines.append("> **FRAMING**: This is explicitly speculative. The grammar is locked. These are pattern-matches, not claims.\n\n")

    lines.append("## Available Constraints (Facts Respected)\n")
    lines.append("- Closed-loop, self-circulating geometry required (G1 open flow = 93.5% failure)\n")
    lines.append("- Continuous operation, not batch-finite\n")
    lines.append("- Phase transitions avoided (CLASS_C = 19.8% failure, all PHASE_COLLAPSE)\n")
    lines.append("- Expert-operated (no definitions, no remedial instruction)\n")
    lines.append("- Enumerated safe programs (not continuous tuning)\n")
    lines.append("- Stability and containment prioritized over speed/yield\n")
    lines.append("- Waiting/damping explicitly encoded (LINK operator)\n")
    lines.append("- Compatible with: porous solids, non-swelling solids, homogeneous fluids\n")
    lines.append("- Incompatible with: emulsions, phase-unstable materials\n\n")

    lines.append("## Process Family Alignment Matrix\n\n")

    for family_name, family_data in process_families.items():
        lines.append(f"### {family_name}\n")
        lines.append(f"**Description**: {family_data['description']}\n\n")
        lines.append(f"**Alignment Strength**: {family_data['alignment_strength']}\n\n")

        lines.append("**What it fits**:\n")
        for fit in family_data['fits']:
            lines.append(f"- {fit}\n")

        lines.append("\n**What it fails to explain**:\n")
        for fail in family_data['fails_to_explain']:
            lines.append(f"- {fail}\n")

        lines.append("\n---\n\n")

    # Alignment summary table
    lines.append("## Alignment Summary\n")
    lines.append("| Process Family | Alignment | Key Support | Key Gap |\n")
    lines.append("|----------------|-----------|-------------|----------|\n")
    for family_name, family_data in process_families.items():
        support = family_data['fits'][0][:50] + '...' if len(family_data['fits'][0]) > 50 else family_data['fits'][0]
        gap = family_data['fails_to_explain'][0][:40] + '...' if len(family_data['fails_to_explain'][0]) > 40 else family_data['fails_to_explain'][0]
        lines.append(f"| {family_name} | {family_data['alignment_strength']} | {support} | {gap} |\n")

    lines.append("\n## Most Consistent Interpretations\n")
    lines.append("Based on constraint satisfaction, the following process families show strongest alignment:\n\n")

    strong = [k for k, v in process_families.items() if v['alignment_strength'] == 'STRONG']
    moderate = [k for k, v in process_families.items() if v['alignment_strength'] == 'MODERATE']
    weak = [k for k, v in process_families.items() if v['alignment_strength'] == 'WEAK']

    lines.append(f"**STRONG**: {', '.join(strong)}\n")
    lines.append(f"**MODERATE**: {', '.join(moderate)}\n")
    lines.append(f"**WEAK**: {', '.join(weak)}\n\n")

    lines.append("## Common Thread Analysis\n")
    lines.append("All STRONG-aligned process families share:\n")
    lines.append("1. **Circulation as primary mechanism** - Material moves in loops, not straight paths\n")
    lines.append("2. **Time-dependent outcomes** - Longer circulation = greater effect\n")
    lines.append("3. **No discrete endpoint** - Operation continues until externally terminated\n")
    lines.append("4. **Stability priority** - Avoiding runaways more important than speed\n")
    lines.append("5. **Damping as control** - LINK maps to physical waiting/settling time\n\n")

    lines.append("## What Would Distinguish Between STRONG Candidates\n")
    lines.append("| Discriminator | CONTINUOUS_EXTRACTION | CIRCULATION_CONDITIONING |\n")
    lines.append("|---------------|----------------------|-------------------------|\n")
    lines.append("| Irreversibility | YES (removal) | NO (maintenance) |\n")
    lines.append("| Cumulative change | YES | NO |\n")
    lines.append("| Extended runs needed | To extract more | To maintain longer |\n")
    lines.append("| Reset meaning | Start fresh extraction | Return to initial state |\n\n")

    lines.append("**SPECULATIVE CONCLUSION**: The grammar is *equally consistent* with extraction-type and conditioning-type processes. ")
    lines.append("Internal analysis cannot distinguish between them.\n")

    return ''.join(lines)

def generate_outcome_patterns_report():
    """Generate process_outcome_patterns.md"""
    lines = []
    lines.append("# Process Outcome Patterns\n")
    lines.append("> **SCOPE**: State-change level descriptions only. No substances, products, or stopping conditions.\n\n")

    lines.append("## Outcome Pattern Inventory\n\n")

    for pattern_name, pattern_data in outcome_patterns.items():
        lines.append(f"### {pattern_name}\n")
        lines.append(f"**Mechanism**: {pattern_data['mechanism']}\n\n")

        lines.append("**Evidence**:\n")
        for ev in pattern_data['evidence']:
            lines.append(f"- {ev}\n")

        lines.append("\n**Metric Support**:\n")
        for metric, value in pattern_data['metric_support'].items():
            lines.append(f"- {metric}: {value}\n")

        lines.append("\n---\n\n")

    lines.append("## Evidence Classification\n")
    lines.append("| Pattern | STRUCTURAL | SPECULATIVE | WEAK |\n")
    lines.append("|---------|------------|-------------|------|\n")
    for pattern_name, pattern_data in outcome_patterns.items():
        struct = sum(1 for e in pattern_data['evidence'] if 'STRUCTURALLY' in e)
        spec = sum(1 for e in pattern_data['evidence'] if 'SPECULATIVE' in e)
        weak = sum(1 for e in pattern_data['evidence'] if 'WEAK' in e)
        lines.append(f"| {pattern_name} | {struct} | {spec} | {weak} |\n")

    lines.append("\n## Outcome Patterns by Program Role\n")
    lines.append("How do program roles correlate with expected outcomes?\n\n")

    lines.append("| Program Role | Primary Outcome | Secondary Outcome |\n")
    lines.append("|--------------|-----------------|-------------------|\n")
    lines.append("| ULTRA_CONSERVATIVE | MAINTENANCE_OF_TARGET_STATE | GRADUAL_STABILIZATION |\n")
    lines.append("| CONSERVATIVE | GRADUAL_STABILIZATION | INCREASED_HOMOGENEITY |\n")
    lines.append("| MODERATE | INCREASED_HOMOGENEITY | PROGRESSIVE_CONCENTRATION |\n")
    lines.append("| AGGRESSIVE | PROGRESSIVE_CONCENTRATION | INCREASED_MOBILITY |\n")
    lines.append("| LINK_HEAVY | GRADUAL_STABILIZATION | MAINTENANCE_OF_TARGET_STATE |\n")
    lines.append("| LINK_SPARSE | INCREASED_MOBILITY | PROGRESSIVE_CONCENTRATION |\n")
    lines.append("| EXTENDED | All patterns with greater magnitude | - |\n")

    lines.append("\n## What These Patterns Do NOT Imply\n")
    lines.append("- NO specific substances or feedstocks\n")
    lines.append("- NO product identities\n")
    lines.append("- NO stopping conditions (outcomes are ongoing, not completed)\n")
    lines.append("- NO yield or production rates\n")
    lines.append("- NO quality metrics beyond stability\n")

    return ''.join(lines)

def generate_negative_matches_report():
    """Generate negative_process_matches.md"""
    lines = []
    lines.append("# Negative Process Matches\n")
    lines.append("> **SCOPE**: Process classes that are INCONSISTENT with the grammar constraints.\n\n")

    lines.append("## Strongly Incompatible Process Classes\n\n")

    strong_neg = {k: v for k, v in negative_matches.items() if v['incompatibility'] == 'STRONG'}
    moderate_neg = {k: v for k, v in negative_matches.items() if v['incompatibility'] == 'MODERATE'}

    for proc_name, proc_data in strong_neg.items():
        lines.append(f"### {proc_name}\n")
        lines.append(f"**Incompatibility**: {proc_data['incompatibility']}\n\n")
        lines.append(f"**Why it fails**: {proc_data['why_fails']}\n\n")

        lines.append("**Evidence**:\n")
        for ev in proc_data['evidence']:
            lines.append(f"- {ev}\n")

        lines.append(f"\n**Examples excluded**: {proc_data['examples']}\n")
        lines.append("\n---\n\n")

    lines.append("## Moderately Incompatible Process Classes\n\n")

    for proc_name, proc_data in moderate_neg.items():
        lines.append(f"### {proc_name}\n")
        lines.append(f"**Incompatibility**: {proc_data['incompatibility']}\n\n")
        lines.append(f"**Why it fails**: {proc_data['why_fails']}\n\n")

        lines.append("**Evidence**:\n")
        for ev in proc_data['evidence']:
            lines.append(f"- {ev}\n")

        lines.append(f"\n**Examples excluded**: {proc_data['examples']}\n")
        lines.append("\n---\n\n")

    lines.append("## Negative Match Summary\n")
    lines.append("| Process Class | Incompatibility | Primary Reason |\n")
    lines.append("|---------------|-----------------|----------------|\n")
    for proc_name, proc_data in negative_matches.items():
        reason = proc_data['why_fails'][:60] + '...' if len(proc_data['why_fails']) > 60 else proc_data['why_fails']
        lines.append(f"| {proc_name} | {proc_data['incompatibility']} | {reason} |\n")

    lines.append("\n## Discriminative Power of Negatives\n")
    lines.append("The negative matches collectively rule out:\n")
    lines.append("- All batch processes (no circulation feedback)\n")
    lines.append("- All endpoint-defined recipes (no termination signals)\n")
    lines.append("- All phase-transition processes (explicit hazard class)\n")
    lines.append("- All single-pass operations (geometry incompatibility)\n")
    lines.append("- All rapid-change protocols (stability priority)\n\n")

    lines.append("This leaves a relatively narrow space of:\n")
    lines.append("- **Closed-loop circulation processes**\n")
    lines.append("- **Continuous indefinite operation**\n")
    lines.append("- **Gradual cumulative change OR maintenance**\n")
    lines.append("- **Phase-stable substrates only**\n")

    return ''.join(lines)

# Generate all reports
print("Generating program roles report...")
roles_report = generate_program_roles_report()
with open('exploratory_program_roles.md', 'w', encoding='utf-8') as f:
    f.write(roles_report)

print("Generating process alignment report...")
alignment_report = generate_process_alignment_report()
with open('speculative_process_alignment.md', 'w', encoding='utf-8') as f:
    f.write(alignment_report)

print("Generating outcome patterns report...")
outcomes_report = generate_outcome_patterns_report()
with open('process_outcome_patterns.md', 'w', encoding='utf-8') as f:
    f.write(outcomes_report)

print("Generating negative matches report...")
negative_report = generate_negative_matches_report()
with open('negative_process_matches.md', 'w', encoding='utf-8') as f:
    f.write(negative_report)

print("\n" + "="*70)
print("EXPLORATORY PROCESS MAPPING COMPLETE")
print("="*70)

# Final reflection
print("""
REFLECTION:

If the Voynich manuscript were a control manual for closed-loop
circulation processes, here is what would most surprise a modern
practitioner - and here is what would not.

WOULD SURPRISE:
1. Complete absence of endpoint signals. Modern process control nearly
   always includes termination conditions. This grammar operates
   indefinitely until external intervention.

2. 9.8x vocabulary compression. Modern control languages are typically
   more verbose, not less. The extreme compression suggests either
   highly expert users or highly constrained operations.

3. Explicit enumeration of forbidden transitions. Most modern systems
   rely on alarms and interlocks, not pre-computed exclusion lists
   embedded in the control sequence itself.

4. LINK operator as deliberate non-action. Modern systems typically
   fill waiting time with monitoring or secondary operations. Pure
   waiting coded as first-class operation is unusual.

WOULD NOT SURPRISE:
1. Closed-loop requirement. Any circulation-based process needs this.

2. Phase stability constraint. Multiphase systems are notoriously
   difficult to control; avoiding them is sensible.

3. Three-point kernel control (k, h, e). Energy, phase, and stability
   are universal control axes for continuous processes.

4. 100% convergence to stable state. Well-designed control programs
   should always reach stability.

5. Extended programs for complete envelope. Complex operations need
   more instructions; this is expected.

The most falsifiable prediction: if this grammar is ever tested on a
real closed-loop apparatus, it should converge to steady state
without operator intervention, provided the apparatus geometry
matches G4 or G5 classes and the substrate is phase-stable.

END REFLECTION
""")
