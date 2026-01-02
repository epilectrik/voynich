"""
Lane 3: Material-Class Compatibility Test

Tests whether abstract physical material behavior classes interact coherently
or incoherently with Voynich operational programs.

Hypothesis: If the manuscript is a real control manual, only SOME material classes
will remain operable inside STATE-C under the grammar, while others destabilize.

DISCIPLINE: No semantic interpretations, no substance identification, no chemical names.
Classes are defined ONLY by physical transport/mechanical behavior.
"""

import json
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
from scipy import stats as scipy_stats
import os

np.random.seed(42)

# =============================================================================
# MATERIAL CLASS DEFINITIONS (Abstract Physical Behavior Only)
# =============================================================================

@dataclass
class MaterialClass:
    """Abstract material class defined by physical behavior parameters."""
    name: str

    # Transport properties (0-1 scale, higher = faster/easier)
    porosity: float           # How easily substances penetrate
    diffusion_rate: float     # Speed of mass transfer
    thermal_conductivity: float  # Speed of heat transfer

    # Mechanical properties (0-1 scale)
    swelling_tendency: float  # Response to solvent absorption
    phase_stability: float    # Resistance to phase transitions
    boundary_sharpness: float # How well-defined interfaces remain

    # Process coupling (0-1 scale)
    latency_sensitivity: float  # How much delays affect stability
    perturbation_damping: float # Natural damping of disturbances


MATERIAL_CLASSES = {
    'CLASS_A': MaterialClass(
        name='CLASS_A',
        porosity=0.85,           # High porosity
        diffusion_rate=0.25,     # Slow diffusion
        thermal_conductivity=0.4,
        swelling_tendency=0.9,   # Strong swelling under immersion
        phase_stability=0.6,     # Moderate phase stability
        boundary_sharpness=0.3,  # Diffuse boundaries
        latency_sensitivity=0.7, # Sensitive to timing
        perturbation_damping=0.4 # Low damping
    ),
    'CLASS_B': MaterialClass(
        name='CLASS_B',
        porosity=0.2,            # Low porosity
        diffusion_rate=0.3,      # Slow release
        thermal_conductivity=0.5,
        swelling_tendency=0.1,   # Minimal swelling
        phase_stability=0.85,    # High phase stability
        boundary_sharpness=0.8,  # Sharp hydrophobic boundaries
        latency_sensitivity=0.3, # Tolerant of delays
        perturbation_damping=0.7 # Good damping
    ),
    'CLASS_C': MaterialClass(
        name='CLASS_C',
        porosity=0.5,            # Moderate
        diffusion_rate=0.6,      # Moderate diffusion
        thermal_conductivity=0.3,
        swelling_tendency=0.5,   # Variable swelling
        phase_stability=0.15,    # Phase-change prone
        boundary_sharpness=0.2,  # Emulsion-forming, diffuse
        latency_sensitivity=0.9, # Very sensitive to timing
        perturbation_damping=0.2 # Poor damping
    ),
    'CLASS_D': MaterialClass(
        name='CLASS_D',
        porosity=0.3,            # Low surface area
        diffusion_rate=0.9,      # Rapid diffusion
        thermal_conductivity=0.85,
        swelling_tendency=0.05,  # Non-swelling
        phase_stability=0.9,     # Highly stable
        boundary_sharpness=0.9,  # Well-defined
        latency_sensitivity=0.2, # Insensitive to delays
        perturbation_damping=0.8 # Strong damping
    ),
    'CLASS_E': MaterialClass(
        name='CLASS_E',
        porosity=1.0,            # Homogeneous (no barriers)
        diffusion_rate=0.95,     # Very fast
        thermal_conductivity=0.9,
        swelling_tendency=0.0,   # No solid to swell
        phase_stability=0.7,     # Single phase
        boundary_sharpness=0.95, # No internal boundaries
        latency_sensitivity=0.1, # Very tolerant
        perturbation_damping=0.5 # Moderate damping
    )
}


# =============================================================================
# SIMULATION ENGINE
# =============================================================================

def simulate_program_with_material(
    program_sig: Dict,
    material: MaterialClass,
    n_simulations: int = 100,
    noise_level: float = 0.1
) -> Dict:
    """
    Simulate program execution with material-class-specific behavior.

    The simulation models:
    1. How material properties affect process dynamics
    2. Whether STATE-C can be maintained
    3. Hazard boundary crossings
    4. Failure modes
    """

    # Extract program control signature features
    link_d = program_sig.get('link_density', 0.4)
    hazard_d = program_sig.get('hazard_density', 0.6)
    kernel_contact = program_sig.get('kernel_contact_ratio', 0.6)
    cycle_reg = program_sig.get('cycle_regularity', 3.5)
    intervention_freq = program_sig.get('intervention_frequency', 6.0)

    # Material-adjusted parameters
    # Material affects how the control grammar interacts with the process

    # Effective damping: program LINK + material damping
    effective_damping = 0.5 + 0.3 * link_d + 0.2 * material.perturbation_damping

    # Transport delay factor: low diffusion = longer delays
    transport_delay = 1.0 + 2.0 * (1 - material.diffusion_rate)

    # Hazard boundary adjustment: phase instability narrows safe zone
    adjusted_hazard_boundary = 2.0 * (1 - hazard_d) * material.phase_stability

    # Perturbation amplification: low damping materials amplify disturbances
    perturbation_amp = 1.0 + 1.5 * (1 - material.perturbation_damping)

    # Latency penalty: sensitive materials fail under LINK delays
    latency_penalty = material.latency_sensitivity * link_d

    # Run simulations
    convergence_count = 0
    hazard_crossings = []
    failure_count = 0
    time_in_state_c = []
    reconvergence_times = []
    failure_modes = []

    for _ in range(n_simulations):
        # State variables
        state = 0.0  # Distance from STATE-C (0 = at STATE-C)
        velocity = 0.0
        in_state_c = True
        state_c_time = 0
        hazard_cross = 0
        failed = False
        steps_to_reconverge = 0

        # Simulate process steps (proportional to cycle regularity)
        n_steps = int(50 * cycle_reg)

        for step in range(n_steps):
            # Apply control action (modulated by material response)
            control_strength = kernel_contact * material.diffusion_rate
            control_action = -control_strength * state

            # Add material-specific noise
            material_noise = noise_level * perturbation_amp

            # Porosity affects how noise couples into system
            noise_coupling = 0.5 + 0.5 * material.porosity
            external_noise = np.random.randn() * material_noise * noise_coupling

            # Transport delay causes lagged response
            if np.random.random() < 0.1 * transport_delay:
                control_action *= 0.5  # Delayed control

            # Latency penalty: LINK-heavy programs suffer if material is sensitive
            if np.random.random() < latency_penalty * 0.2:
                external_noise *= 2  # Amplified disturbance during LINK

            # Update dynamics (damped oscillator with control)
            acceleration = control_action - effective_damping * velocity + external_noise
            velocity += acceleration * 0.1
            state += velocity * 0.1

            # Check STATE-C membership (|state| < 0.5)
            if abs(state) < 0.5:
                if not in_state_c:
                    # Just reconverged
                    reconvergence_times.append(steps_to_reconverge)
                    steps_to_reconverge = 0
                in_state_c = True
                state_c_time += 1
            else:
                if in_state_c:
                    steps_to_reconverge = 0
                in_state_c = False
                steps_to_reconverge += 1

            # Check hazard boundary crossing
            if abs(state) > adjusted_hazard_boundary:
                hazard_cross += 1

                # Catastrophic failure if boundary severely exceeded
                if abs(state) > adjusted_hazard_boundary * 1.5:
                    failed = True
                    # Determine failure mode based on material properties
                    if material.phase_stability < 0.3:
                        failure_modes.append('PHASE_COLLAPSE')
                    elif material.swelling_tendency > 0.7:
                        failure_modes.append('BOUNDARY_RUPTURE')
                    elif material.latency_sensitivity > 0.7:
                        failure_modes.append('TIMING_FAILURE')
                    elif material.perturbation_damping < 0.3:
                        failure_modes.append('OSCILLATION_DIVERGENCE')
                    else:
                        failure_modes.append('GENERIC_OVERSHOOT')
                    break

        # Record results
        if not failed and in_state_c:
            convergence_count += 1
        if failed:
            failure_count += 1
        hazard_crossings.append(hazard_cross)
        time_in_state_c.append(state_c_time / n_steps if n_steps > 0 else 0)

    # Aggregate metrics
    convergence_rate = convergence_count / n_simulations
    failure_rate = failure_count / n_simulations
    mean_hazard_crossings = np.mean(hazard_crossings)
    mean_time_in_state_c = np.mean(time_in_state_c)
    mean_reconvergence = np.mean(reconvergence_times) if reconvergence_times else 0

    # Count failure modes
    failure_mode_counts = {}
    for mode in failure_modes:
        failure_mode_counts[mode] = failure_mode_counts.get(mode, 0) + 1

    return {
        'convergence_rate': float(convergence_rate),
        'failure_rate': float(failure_rate),
        'mean_hazard_crossings': float(mean_hazard_crossings),
        'mean_time_in_state_c': float(mean_time_in_state_c),
        'mean_reconvergence_time': float(mean_reconvergence),
        'failure_mode_counts': failure_mode_counts,
        'link_sensitivity': float(latency_penalty),
        'effective_damping': float(effective_damping)
    }


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    # Load Lane 1 results for cluster assignments
    with open('forward_inference_results.json', 'r') as f:
        lane1_data = json.load(f)

    # Load control signatures for all programs
    with open('control_signatures.json', 'r') as f:
        sig_data = json.load(f)

    signatures = sig_data['signatures']
    clusters = lane1_data['lane1']['clusters']

    # Select representative programs from each cluster
    # Take 3-5 programs from each cluster
    representatives = {}
    for cluster_id, cluster_info in clusters.items():
        members = cluster_info['members']
        # Take up to 5 representatives
        n_reps = min(5, len(members))
        representatives[cluster_id] = {
            'folios': members[:n_reps],
            'template': cluster_info['best_template']
        }

    print("Lane 3: Material-Class Compatibility Test")
    print("=" * 60)
    print(f"Material classes: {list(MATERIAL_CLASSES.keys())}")
    print(f"Clusters: {list(representatives.keys())}")
    print()

    # Run simulations for each (program x material class)
    results = {}
    stability_matrix = {}  # material -> cluster -> metrics

    for mat_name, material in MATERIAL_CLASSES.items():
        print(f"Testing {mat_name}...")
        results[mat_name] = {}
        stability_matrix[mat_name] = {}

        for cluster_id, cluster_data in representatives.items():
            cluster_results = []

            for folio in cluster_data['folios']:
                if folio not in signatures:
                    continue

                sig = signatures[folio]
                sim_result = simulate_program_with_material(sig, material)
                sim_result['folio'] = folio
                sim_result['cluster'] = cluster_id
                sim_result['template'] = cluster_data['template']
                cluster_results.append(sim_result)

            # Aggregate cluster-level metrics
            if cluster_results:
                stability_matrix[mat_name][cluster_id] = {
                    'template': cluster_data['template'],
                    'mean_convergence': np.mean([r['convergence_rate'] for r in cluster_results]),
                    'mean_failure': np.mean([r['failure_rate'] for r in cluster_results]),
                    'mean_hazard_crossings': np.mean([r['mean_hazard_crossings'] for r in cluster_results]),
                    'mean_state_c_time': np.mean([r['mean_time_in_state_c'] for r in cluster_results]),
                    'programs': cluster_results
                }

            results[mat_name][cluster_id] = cluster_results

    # Compute material-class-level aggregate statistics
    material_stats = {}
    for mat_name in MATERIAL_CLASSES:
        all_convergence = []
        all_failure = []
        all_hazard = []
        all_state_c = []
        all_failure_modes = {}

        for cluster_id, cluster_metrics in stability_matrix[mat_name].items():
            all_convergence.append(cluster_metrics['mean_convergence'])
            all_failure.append(cluster_metrics['mean_failure'])
            all_hazard.append(cluster_metrics['mean_hazard_crossings'])
            all_state_c.append(cluster_metrics['mean_state_c_time'])

            for prog in cluster_metrics['programs']:
                for mode, count in prog.get('failure_mode_counts', {}).items():
                    all_failure_modes[mode] = all_failure_modes.get(mode, 0) + count

        material_stats[mat_name] = {
            'mean_convergence': float(np.mean(all_convergence)),
            'std_convergence': float(np.std(all_convergence)),
            'mean_failure': float(np.mean(all_failure)),
            'std_failure': float(np.std(all_failure)),
            'mean_hazard_crossings': float(np.mean(all_hazard)),
            'mean_state_c_time': float(np.mean(all_state_c)),
            'failure_modes': all_failure_modes,
            'n_clusters': len(all_convergence)
        }

    # Classify materials as COMPATIBLE or INCOMPATIBLE
    # Threshold: mean_failure < 0.15 and mean_convergence > 0.70
    compatibility = {}
    for mat_name, stats in material_stats.items():
        compatible = stats['mean_failure'] < 0.15 and stats['mean_convergence'] > 0.70
        compatibility[mat_name] = {
            'status': 'COMPATIBLE' if compatible else 'INCOMPATIBLE',
            'failure_rate': stats['mean_failure'],
            'convergence_rate': stats['mean_convergence'],
            'dominant_failure_mode': max(stats['failure_modes'].items(), key=lambda x: x[1])[0] if stats['failure_modes'] else None
        }

    # Statistical test: is there significant variation between material classes?
    failure_rates_by_class = [material_stats[m]['mean_failure'] for m in MATERIAL_CLASSES]
    convergence_by_class = [material_stats[m]['mean_convergence'] for m in MATERIAL_CLASSES]

    # One-way ANOVA to test if material class matters
    # We need per-program failure rates for proper ANOVA
    per_program_failures = {mat: [] for mat in MATERIAL_CLASSES}
    for mat_name, clusters in results.items():
        for cluster_id, programs in clusters.items():
            for prog in programs:
                per_program_failures[mat_name].append(prog['failure_rate'])

    # Perform Kruskal-Wallis (non-parametric) since we may not have normality
    failure_groups = [per_program_failures[m] for m in MATERIAL_CLASSES]
    kw_stat, kw_p = scipy_stats.kruskal(*failure_groups)

    # Compute effect size (eta-squared approximation)
    total_n = sum(len(g) for g in failure_groups)
    eta_squared = (kw_stat - len(failure_groups) + 1) / (total_n - len(failure_groups))

    # Apply pass/kill criteria
    compatible_count = sum(1 for v in compatibility.values() if v['status'] == 'COMPATIBLE')
    incompatible_count = sum(1 for v in compatibility.values() if v['status'] == 'INCOMPATIBLE')

    # PASS: Asymmetry exists (some compatible, some incompatible)
    # KILL: All material classes behave equivalently
    asymmetry_exists = compatible_count > 0 and incompatible_count > 0
    significant_variation = kw_p < 0.05

    if asymmetry_exists and significant_variation:
        verdict = 'PASS'
        verdict_reason = f'Material classes differentially compatible (p={kw_p:.4f}, eta^2={eta_squared:.3f})'
    elif not significant_variation:
        verdict = 'FAIL'
        verdict_reason = 'Stability differences not statistically significant'
    else:
        verdict = 'FAIL'
        verdict_reason = 'No asymmetry: all classes behave similarly'

    print()
    print("=" * 60)
    print(f"VERDICT: {verdict}")
    print(f"Reason: {verdict_reason}")
    print()
    print("Material Class Compatibility:")
    for mat, compat in compatibility.items():
        print(f"  {mat}: {compat['status']} (failure={compat['failure_rate']:.3f}, convergence={compat['convergence_rate']:.3f})")
    print()
    print(f"Kruskal-Wallis H={kw_stat:.3f}, p={kw_p:.6f}")
    print(f"Effect size (eta^2) = {eta_squared:.3f}")

    # =============================================================================
    # OUTPUT FILES
    # =============================================================================

    # 1. lane3_material_class_results.json
    output = {
        'metadata': {
            'test': 'Lane 3: Material-Class Compatibility',
            'n_material_classes': len(MATERIAL_CLASSES),
            'n_clusters': len(representatives),
            'n_simulations_per_program': 100
        },
        'material_classes': {
            name: {
                'porosity': mc.porosity,
                'diffusion_rate': mc.diffusion_rate,
                'thermal_conductivity': mc.thermal_conductivity,
                'swelling_tendency': mc.swelling_tendency,
                'phase_stability': mc.phase_stability,
                'boundary_sharpness': mc.boundary_sharpness,
                'latency_sensitivity': mc.latency_sensitivity,
                'perturbation_damping': mc.perturbation_damping
            }
            for name, mc in MATERIAL_CLASSES.items()
        },
        'material_statistics': material_stats,
        'compatibility': compatibility,
        'statistical_tests': {
            'kruskal_wallis_H': float(kw_stat),
            'kruskal_wallis_p': float(kw_p),
            'eta_squared': float(eta_squared),
            'significant': bool(significant_variation)
        },
        'verdict': verdict,
        'verdict_reason': verdict_reason,
        'pass_criteria': {
            'asymmetry_required': True,
            'statistical_significance_threshold': 0.05,
            'compatible_threshold_failure': 0.15,
            'compatible_threshold_convergence': 0.70
        }
    }

    with open('lane3_material_class_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("\nWrote lane3_material_class_results.json")

    # 2. lane3_stability_matrix.md
    with open('lane3_stability_matrix.md', 'w', encoding='utf-8') as f:
        f.write("# Lane 3: Stability Matrix\n\n")
        f.write("## Material Class vs Cluster Stability\n\n")

        # Header row
        f.write("| Material | ")
        for cid in sorted(representatives.keys()):
            f.write(f"Cluster {cid} | ")
        f.write("Overall |\n")

        f.write("|" + "----|" * (len(representatives) + 2) + "\n")

        # Data rows
        for mat_name in MATERIAL_CLASSES:
            f.write(f"| {mat_name} | ")
            for cid in sorted(representatives.keys()):
                if cid in stability_matrix[mat_name]:
                    fail = stability_matrix[mat_name][cid]['mean_failure']
                    f.write(f"{fail:.2f} | ")
                else:
                    f.write("N/A | ")
            f.write(f"{material_stats[mat_name]['mean_failure']:.2f} |\n")

        f.write("\n*Values show failure rate (lower = more compatible)*\n\n")

        f.write("## Convergence Rate by Material Class\n\n")
        f.write("| Material | Mean Convergence | Mean Failure | Status |\n")
        f.write("|----------|------------------|--------------|--------|\n")
        for mat_name in MATERIAL_CLASSES:
            stats = material_stats[mat_name]
            status = compatibility[mat_name]['status']
            f.write(f"| {mat_name} | {stats['mean_convergence']:.3f} | {stats['mean_failure']:.3f} | {status} |\n")

        f.write(f"\n## Statistical Summary\n\n")
        f.write(f"- Kruskal-Wallis H: {kw_stat:.3f}\n")
        f.write(f"- p-value: {kw_p:.6f}\n")
        f.write(f"- Effect size (eta^2): {eta_squared:.3f}\n")
        f.write(f"- Compatible classes: {compatible_count}\n")
        f.write(f"- Incompatible classes: {incompatible_count}\n")

        f.write(f"\n## Verdict: **{verdict}**\n\n")
        f.write(f"{verdict_reason}\n")

    print("Wrote lane3_stability_matrix.md")

    # 3. lane3_failure_modes.md
    with open('lane3_failure_modes.md', 'w', encoding='utf-8') as f:
        f.write("# Lane 3: Failure Mode Analysis\n\n")

        f.write("## Failure Modes by Material Class\n\n")

        all_modes = set()
        for mat_name in MATERIAL_CLASSES:
            all_modes.update(material_stats[mat_name]['failure_modes'].keys())
        all_modes = sorted(all_modes)

        # Header
        f.write("| Material | ")
        for mode in all_modes:
            f.write(f"{mode} | ")
        f.write("Total |\n")

        f.write("|" + "----|" * (len(all_modes) + 2) + "\n")

        # Data rows
        for mat_name in MATERIAL_CLASSES:
            modes = material_stats[mat_name]['failure_modes']
            total = sum(modes.values())
            f.write(f"| {mat_name} | ")
            for mode in all_modes:
                count = modes.get(mode, 0)
                f.write(f"{count} | ")
            f.write(f"{total} |\n")

        f.write("\n## Dominant Failure Modes\n\n")
        for mat_name, compat in compatibility.items():
            dom_mode = compat['dominant_failure_mode']
            f.write(f"- **{mat_name}**: {dom_mode if dom_mode else 'None'}\n")

        f.write("\n## Failure Mode Definitions\n\n")
        f.write("| Mode | Physical Meaning |\n")
        f.write("|------|------------------|\n")
        f.write("| PHASE_COLLAPSE | Material phase transition destabilizes system |\n")
        f.write("| BOUNDARY_RUPTURE | Swelling causes containment failure |\n")
        f.write("| TIMING_FAILURE | Latency-sensitive material cannot track control |\n")
        f.write("| OSCILLATION_DIVERGENCE | Undamped perturbations grow without bound |\n")
        f.write("| GENERIC_OVERSHOOT | State exceeds hazard boundary |\n")

        f.write("\n## Interpretation\n\n")
        if verdict == 'PASS':
            f.write("The Voynich control grammar shows **differential compatibility** with material classes.\n\n")
            f.write("Compatible classes:\n")
            for mat, compat in compatibility.items():
                if compat['status'] == 'COMPATIBLE':
                    f.write(f"- {mat}: Maintains stability (failure rate {compat['failure_rate']:.2%})\n")
            f.write("\nIncompatible classes:\n")
            for mat, compat in compatibility.items():
                if compat['status'] == 'INCOMPATIBLE':
                    f.write(f"- {mat}: Destabilizes (failure rate {compat['failure_rate']:.2%}, mode: {compat['dominant_failure_mode']})\n")
        else:
            f.write("The Voynich control grammar does **not** show differential compatibility with material classes.\n")
            f.write("All material classes behave similarly under the grammar.\n")

    print("Wrote lane3_failure_modes.md")

    return verdict, compatibility


if __name__ == '__main__':
    main()
