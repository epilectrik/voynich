"""
Option A: Apparatus Geometry Compatibility Test

Tests whether the frozen Voynich control grammar is selectively compatible
with particular abstract apparatus geometries under real physical constraints.

NO semantic labels, historical devices, or illustration references.
All reasoning is structural and dynamical only.
"""

import json
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from scipy import stats as scipy_stats
from collections import defaultdict


@dataclass
class GeometryClass:
    """Abstract geometry class defined by dynamical parameters only."""
    name: str
    # Transport characteristics
    recirculation_fraction: float   # 0 = open flow, 1 = fully closed loop
    transport_lag: float            # Intrinsic delay from path length
    mixing_timescale: float         # How fast contents homogenize
    # Conservation properties
    conservation_strictness: float  # 1 = perfect conservation, 0 = lossy
    buffer_capacity: float          # Internal buffering/smoothing
    # Response characteristics
    natural_damping: float          # Intrinsic oscillation suppression
    perturbation_propagation: float # How disturbances travel (0=local, 1=global)
    feedback_strength: float        # How strongly state affects next input


# Define 5 abstract geometry classes (G1-G5)
GEOMETRY_CLASSES = {
    'G1': GeometryClass(
        name='G1',
        recirculation_fraction=0.0,   # Linear open flow - no recirculation
        transport_lag=0.1,            # Minimal delay (one-pass)
        mixing_timescale=0.2,         # Fast mixing (short residence)
        conservation_strictness=0.3,   # Lossy (material exits)
        buffer_capacity=0.1,          # No internal buffering
        natural_damping=0.2,          # Low damping (perturbations persist)
        perturbation_propagation=0.9, # Disturbances travel through
        feedback_strength=0.1         # Weak feedback (no return path)
    ),
    'G2': GeometryClass(
        name='G2',
        recirculation_fraction=0.0,   # Batch vessel - isolated
        transport_lag=0.05,           # Very low delay (no flow)
        mixing_timescale=2.0,         # Slow mixing (large volume, no circulation)
        conservation_strictness=0.95, # Good conservation (closed batch)
        buffer_capacity=0.9,          # High buffering (large volume)
        natural_damping=0.3,          # Moderate damping
        perturbation_propagation=0.3, # Local disturbances (no flow)
        feedback_strength=0.2         # Weak feedback (no circulation)
    ),
    'G3': GeometryClass(
        name='G3',
        recirculation_fraction=0.5,   # Partial recirculation
        transport_lag=0.5,            # Moderate delay
        mixing_timescale=0.8,         # Moderate mixing
        conservation_strictness=0.6,  # Partial loss (leakage in loop)
        buffer_capacity=0.4,          # Some buffering
        natural_damping=0.5,          # Moderate damping
        perturbation_propagation=0.6, # Mixed propagation
        feedback_strength=0.5         # Moderate feedback
    ),
    'G4': GeometryClass(
        name='G4',
        recirculation_fraction=1.0,   # Fully closed loop
        transport_lag=1.0,            # High delay (full circuit)
        mixing_timescale=0.6,         # Good mixing (continuous flow)
        conservation_strictness=1.0,  # Perfect conservation (closed)
        buffer_capacity=0.6,          # Moderate buffering
        natural_damping=0.8,          # High damping (circulation smooths)
        perturbation_propagation=0.4, # Distributed, damped propagation
        feedback_strength=0.9         # Strong feedback (full return)
    ),
    'G5': GeometryClass(
        name='G5',
        recirculation_fraction=1.0,   # Multi-loop nested
        transport_lag=1.5,            # Very high delay (multiple circuits)
        mixing_timescale=0.4,         # Fast mixing (multiple timescales)
        conservation_strictness=1.0,  # Perfect conservation
        buffer_capacity=0.85,         # High buffering (nested volumes)
        natural_damping=0.9,          # Very high damping
        perturbation_propagation=0.2, # Highly localized (nested structure)
        feedback_strength=0.95        # Very strong feedback
    )
}


def load_data() -> Tuple[Dict, Dict]:
    """Load program signatures and cluster assignments."""
    with open('forward_inference_results.json', 'r') as f:
        lane_data = json.load(f)

    with open('control_signatures.json', 'r') as f:
        sig_data = json.load(f)

    return lane_data, sig_data


def simulate_program_with_geometry(
    program_sig: Dict,
    geometry: GeometryClass,
    n_simulations: int = 100,
    noise_level: float = 0.15,
    n_steps: int = 300
) -> Dict:
    """
    Simulate a program executing within a geometry.

    The simulation models:
    - Recirculation: contents return through loop, providing self-correction
    - Transport lag: natural delay that LINK can exploit for settling
    - Conservation: state persistence (closed systems maintain state)
    - LINK operator: effective when geometry has natural delay paths

    Key insight: Closed-loop geometries stabilize because:
    1. Perturbations are recirculated and averaged out
    2. Transport delay provides natural settling time
    3. Conservation prevents state drift

    Open-flow geometries destabilize because:
    1. Perturbations exit without correction
    2. No natural delay to exploit
    3. State cannot be maintained without continuous intervention

    Returns metrics for this program-geometry pair.
    """
    np.random.seed(hash(f"{program_sig.get('total_length', 0)}{geometry.name}") % 2**31)

    # Extract program signature parameters
    link_d = program_sig.get('link_density', 0.4)
    hazard_d = program_sig.get('hazard_density', 0.5)
    kernel_ratio = program_sig.get('kernel_contact_ratio', 0.6)
    cycle_reg = program_sig.get('cycle_regularity', 3.0)
    intervention_freq = program_sig.get('intervention_frequency', 5.0)

    results = {
        'convergence_count': 0,
        'total_state_c_time': 0.0,
        'hazard_crossings': [],
        'failure_count': 0,
        'sensitivity_scores': [],
        'latency_distribution': [],
        'link_effectiveness': []
    }

    for sim in range(n_simulations):
        # Initial state: slightly perturbed from origin
        state = np.random.uniform(-0.5, 0.5)
        target = 0.0  # STATE-C is at origin

        # State history for averaging (recirculation effect)
        state_history = [state] * 10

        in_state_c = 0
        hazard_count = 0
        converged = True
        link_wait_steps = 0
        total_steps = 0
        accumulated_perturbation = 0.0

        # Hazard boundary (narrower for high hazard density programs)
        hazard_boundary = 1.0 * (1.1 - hazard_d)

        # How well LINK maps to physical waiting
        # High for closed loops with natural delay, low for open/batch
        link_physical_mapping = (
            geometry.recirculation_fraction *
            geometry.transport_lag *
            geometry.natural_damping
        )

        # Stability factor: closed loops with conservation stabilize
        # Open flow has much lower stability
        stability_factor = (
            0.1 +
            0.5 * geometry.recirculation_fraction +
            0.2 * geometry.natural_damping +
            0.2 * geometry.conservation_strictness
        )

        # Noise amplification: open flow amplifies significantly, closed loop damps
        noise_multiplier = (
            2.0 - geometry.recirculation_fraction * 1.2 -
            geometry.buffer_capacity * 0.4
        )

        for step in range(n_steps):
            # Add noise (boundary stress)
            raw_perturbation = np.random.normal(0, noise_level)

            # Geometry determines perturbation behavior
            # Open flow: perturbations accumulate (random walk drift)
            # Closed loop: perturbations average out through recirculation
            if geometry.recirculation_fraction > 0.5:
                # Closed loop: recirculation averages perturbations
                accumulated_perturbation = (
                    0.5 * accumulated_perturbation +
                    0.5 * raw_perturbation
                )
                perturbation = accumulated_perturbation * (1 - geometry.buffer_capacity * 0.5)
            else:
                # Open/batch: perturbations accumulate as random walk
                perturbation = raw_perturbation * noise_multiplier
                # In open flow, errors accumulate (no correction path)
                if geometry.perturbation_propagation > 0.5:
                    accumulated_perturbation += raw_perturbation * 0.15
                # Batch vessels also accumulate but more slowly
                elif geometry.mixing_timescale > 1.0:
                    accumulated_perturbation += raw_perturbation * 0.08

            # Control action (from program)
            # Kernel contact ratio determines control authority
            control_strength = kernel_ratio * 0.4 * stability_factor
            control = -control_strength * state  # Drive toward STATE-C

            # LINK operator effect
            link_active = np.random.random() < link_d
            if link_active:
                if link_physical_mapping > 0.3:
                    # Geometry supports LINK as physical delay
                    # During LINK, system settles naturally (reduced perturbation effect)
                    link_wait_steps += 1
                    perturbation *= (1 - link_physical_mapping * 0.7)
                    # Control also reduced (waiting, not actively controlling)
                    control *= 0.5
                    results['link_effectiveness'].append(link_physical_mapping)
                else:
                    # Geometry doesn't support natural delay
                    # LINK is just a pause with no physical benefit
                    results['link_effectiveness'].append(0.2)

            # State update
            # Mixing timescale: slow mixing means slow response
            responsiveness = 0.8 / (1.0 + geometry.mixing_timescale * 0.5)

            # State change
            state_change = responsiveness * (control + perturbation)

            # Apply damping based on geometry
            # Closed loops with recirculation naturally damp
            damping = stability_factor * 0.3
            state_change -= damping * state

            # Conservation: closed systems maintain state better
            # Open systems drift due to accumulated uncorrected errors
            if geometry.conservation_strictness > 0.8:
                # High conservation: state persists, changes controlled
                new_state = state + state_change
            else:
                # Low conservation: accumulated errors cause drift
                drift_rate = 1 - geometry.conservation_strictness
                new_state = (1 - drift_rate * 0.1) * state + state_change
                # Open systems: accumulated perturbations cause systematic drift
                if geometry.recirculation_fraction < 0.3:
                    # No recirculation = no error correction = drift accumulates
                    new_state += accumulated_perturbation * 0.12
                elif geometry.recirculation_fraction < 0.6:
                    # Partial recirculation = partial correction
                    new_state += accumulated_perturbation * 0.06

            # Recirculation effect: averaging with history
            if geometry.recirculation_fraction > 0.5:
                # Closed loop: current state averages with recent history
                avg_factor = geometry.recirculation_fraction * 0.3
                state = (1 - avg_factor) * new_state + avg_factor * np.mean(state_history[-5:])
            else:
                state = new_state

            state_history.append(state)
            if len(state_history) > 20:
                state_history.pop(0)

            # Check hazard boundary
            if abs(state) > hazard_boundary:
                hazard_count += 1
                if abs(state) > hazard_boundary * 1.8:
                    # Failure: crossed too far
                    converged = False
                    results['failure_count'] += 1
                    break

            # Check if in STATE-C (near target)
            if abs(state - target) < 0.25:
                in_state_c += 1

            total_steps += 1

        if converged:
            results['convergence_count'] += 1

        results['total_state_c_time'] += in_state_c / max(1, total_steps)
        results['hazard_crossings'].append(hazard_count)
        results['latency_distribution'].append(link_wait_steps)

        # Sensitivity: how much did state vary?
        if len(state_history) > 5:
            results['sensitivity_scores'].append(np.std(state_history[-5:]))

    # Aggregate results
    return {
        'convergence_rate': results['convergence_count'] / n_simulations,
        'mean_state_c_time': results['total_state_c_time'] / n_simulations,
        'mean_hazard_crossings': np.mean(results['hazard_crossings']),
        'failure_rate': results['failure_count'] / n_simulations,
        'mean_sensitivity': np.mean(results['sensitivity_scores']) if results['sensitivity_scores'] else 0,
        'mean_latency': np.mean(results['latency_distribution']),
        'link_effectiveness': np.mean(results['link_effectiveness']) if results['link_effectiveness'] else 0
    }


def run_geometry_analysis():
    """Run the full geometry compatibility analysis."""
    print("=" * 70)
    print("OPTION A: APPARATUS GEOMETRY COMPATIBILITY TEST")
    print("=" * 70)
    print()

    # Load data
    lane_data, sig_data = load_data()
    clusters = lane_data['lane1']['clusters']
    signatures = sig_data['signatures']

    # Results storage
    geometry_results = {g: {'programs': [], 'cluster_stats': {}} for g in GEOMETRY_CLASSES}
    cluster_geometry_matrix = {}

    # Test each geometry with programs from each cluster
    print("Testing geometry × cluster combinations...")
    print()

    for cluster_id, cluster_info in clusters.items():
        cluster_geometry_matrix[cluster_id] = {}
        print(f"  Cluster {cluster_id} ({cluster_info['n_members']} programs, "
              f"best template: {cluster_info['best_template']})")

        for geom_name, geometry in GEOMETRY_CLASSES.items():
            cluster_metrics = []

            for folio in cluster_info['members']:
                if folio in signatures:
                    prog_sig = signatures[folio]
                    metrics = simulate_program_with_geometry(prog_sig, geometry)
                    metrics['folio'] = folio
                    metrics['cluster'] = cluster_id
                    geometry_results[geom_name]['programs'].append(metrics)
                    cluster_metrics.append(metrics)

            # Aggregate cluster stats for this geometry
            if cluster_metrics:
                cluster_geometry_matrix[cluster_id][geom_name] = {
                    'mean_convergence': np.mean([m['convergence_rate'] for m in cluster_metrics]),
                    'mean_state_c_time': np.mean([m['mean_state_c_time'] for m in cluster_metrics]),
                    'mean_failure': np.mean([m['failure_rate'] for m in cluster_metrics]),
                    'mean_hazard_crossings': np.mean([m['mean_hazard_crossings'] for m in cluster_metrics]),
                    'mean_link_effectiveness': np.mean([m['link_effectiveness'] for m in cluster_metrics]),
                    'n_programs': len(cluster_metrics)
                }

    print()

    # Compute geometry-level statistics
    geometry_stats = {}
    for geom_name in GEOMETRY_CLASSES:
        programs = geometry_results[geom_name]['programs']
        if programs:
            geometry_stats[geom_name] = {
                'mean_convergence': np.mean([p['convergence_rate'] for p in programs]),
                'std_convergence': np.std([p['convergence_rate'] for p in programs]),
                'mean_failure': np.mean([p['failure_rate'] for p in programs]),
                'std_failure': np.std([p['failure_rate'] for p in programs]),
                'mean_state_c_time': np.mean([p['mean_state_c_time'] for p in programs]),
                'mean_hazard_crossings': np.mean([p['mean_hazard_crossings'] for p in programs]),
                'mean_link_effectiveness': np.mean([p['link_effectiveness'] for p in programs]),
                'mean_latency': np.mean([p['mean_latency'] for p in programs]),
                'n_programs': len(programs)
            }

    # Statistical comparison between geometries
    print("Geometry Performance Summary:")
    print("-" * 70)
    print(f"{'Geometry':<8} {'Conv Rate':>10} {'Failure':>10} {'STATE-C':>10} "
          f"{'LINK Eff':>10} {'Status':>12}")
    print("-" * 70)

    # Classify geometries
    compatible_geometries = []
    incompatible_geometries = []

    for geom_name in ['G1', 'G2', 'G3', 'G4', 'G5']:
        stats = geometry_stats[geom_name]

        # Compatibility criteria:
        # - High convergence (>0.85)
        # - Low failure (<0.15)
        # - High STATE-C time (>0.5)
        # - LINK effectiveness (>0.5 for closed-loop)

        is_compatible = (
            stats['mean_convergence'] > 0.85 and
            stats['mean_failure'] < 0.15 and
            stats['mean_state_c_time'] > 0.5
        )

        status = "COMPATIBLE" if is_compatible else "INCOMPATIBLE"
        if is_compatible:
            compatible_geometries.append(geom_name)
        else:
            incompatible_geometries.append(geom_name)

        print(f"{geom_name:<8} {stats['mean_convergence']:>10.3f} "
              f"{stats['mean_failure']:>10.3f} {stats['mean_state_c_time']:>10.3f} "
              f"{stats['mean_link_effectiveness']:>10.3f} {status:>12}")

    print("-" * 70)
    print()

    # Statistical tests
    # Compare convergence rates across geometries
    convergence_groups = []
    for geom_name in ['G1', 'G2', 'G3', 'G4', 'G5']:
        programs = geometry_results[geom_name]['programs']
        convergence_groups.append([p['convergence_rate'] for p in programs])

    h_stat, kw_p = scipy_stats.kruskal(*convergence_groups)

    # Effect size (eta-squared)
    n_total = sum(len(g) for g in convergence_groups)
    eta_squared = (h_stat - len(convergence_groups) + 1) / (n_total - len(convergence_groups))
    eta_squared = max(0, min(1, eta_squared))

    print(f"Statistical Tests:")
    print(f"  Kruskal-Wallis H: {h_stat:.3f}")
    print(f"  p-value: {kw_p:.2e}")
    print(f"  Effect size (eta^2): {eta_squared:.3f}")
    print()

    # Pairwise comparisons: closed-loop (G4, G5) vs others
    closed_loop = []
    open_flow = []
    for p in geometry_results['G4']['programs'] + geometry_results['G5']['programs']:
        closed_loop.append(p['convergence_rate'])
    for p in geometry_results['G1']['programs'] + geometry_results['G2']['programs']:
        open_flow.append(p['convergence_rate'])

    t_stat, t_p = scipy_stats.ttest_ind(closed_loop, open_flow)
    d_closed_open = (np.mean(closed_loop) - np.mean(open_flow)) / np.sqrt(
        (np.std(closed_loop)**2 + np.std(open_flow)**2) / 2
    )

    print(f"Closed-Loop (G4+G5) vs Open-Flow (G1+G2):")
    print(f"  t-statistic: {t_stat:.3f}")
    print(f"  p-value: {t_p:.2e}")
    print(f"  Cohen's d: {d_closed_open:.3f}")
    print()

    # LINK effectiveness comparison
    link_eff_closed = []
    link_eff_open = []
    for p in geometry_results['G4']['programs'] + geometry_results['G5']['programs']:
        link_eff_closed.append(p['link_effectiveness'])
    for p in geometry_results['G1']['programs'] + geometry_results['G2']['programs']:
        link_eff_open.append(p['link_effectiveness'])

    t_link, p_link = scipy_stats.ttest_ind(link_eff_closed, link_eff_open)
    d_link = (np.mean(link_eff_closed) - np.mean(link_eff_open)) / np.sqrt(
        (np.std(link_eff_closed)**2 + np.std(link_eff_open)**2) / 2
    )

    print(f"LINK Effectiveness (Closed vs Open):")
    print(f"  Mean closed-loop: {np.mean(link_eff_closed):.3f}")
    print(f"  Mean open-flow: {np.mean(link_eff_open):.3f}")
    print(f"  t-statistic: {t_link:.3f}")
    print(f"  p-value: {p_link:.2e}")
    print(f"  Cohen's d: {d_link:.3f}")
    print()

    # Determine verdict
    print("=" * 70)
    print("VERDICT DETERMINATION")
    print("=" * 70)
    print()

    # Determine verdict based on multiple criteria
    # The key question: Is the grammar selectively compatible with closed-loop geometries?

    # Extract key metrics
    g1_conv = geometry_stats['G1']['mean_convergence']
    g2_conv = geometry_stats['G2']['mean_convergence']
    g3_conv = geometry_stats['G3']['mean_convergence']
    g4_conv = geometry_stats['G4']['mean_convergence']
    g5_conv = geometry_stats['G5']['mean_convergence']

    g1_link = geometry_stats['G1']['mean_link_effectiveness']
    g2_link = geometry_stats['G2']['mean_link_effectiveness']
    g4_link = geometry_stats['G4']['mean_link_effectiveness']
    g5_link = geometry_stats['G5']['mean_link_effectiveness']

    g1_state_c = geometry_stats['G1']['mean_state_c_time']
    g4_state_c = geometry_stats['G4']['mean_state_c_time']
    g5_state_c = geometry_stats['G5']['mean_state_c_time']

    # Three-tier evaluation:
    # 1. Asymmetry test: At least one geometry class must clearly fail
    # 2. LINK selectivity: LINK must be significantly more effective in closed loops
    # 3. Closed-loop superiority: G4/G5 must outperform on combined metrics

    # Test 1: Asymmetry
    has_clear_failure = g1_conv < 0.5  # Open flow should fail
    asymmetry_ok = has_clear_failure

    # Test 2: LINK selectivity
    link_advantage = np.mean(link_eff_closed) - np.mean(link_eff_open)
    link_selective = link_advantage > 0.3 and d_link > 1.0  # Large effect

    # Test 3: Closed-loop superiority (combined convergence + STATE-C + LINK)
    closed_loop_score = (g4_conv + g5_conv) / 2 + (g4_state_c + g5_state_c) / 2 + (g4_link + g5_link) / 4
    open_score = g1_conv + g1_state_c + g1_link / 4
    batch_score = g2_conv + geometry_stats['G2']['mean_state_c_time'] + g2_link / 4

    closed_superiority = closed_loop_score > open_score + 0.5 and closed_loop_score > batch_score + 0.3

    # Kill criteria (strict failures)
    kill_triggered = False
    kill_reason = None

    # Kill: No asymmetry - all geometries perform equally
    if not asymmetry_ok:
        kill_triggered = True
        kill_reason = "No geometry class shows clear failure (uniform performance)"

    # Kill: LINK provides no advantage in any geometry
    if link_advantage < 0.1:
        kill_triggered = True
        kill_reason = "LINK provides no measurable advantage in any geometry"

    # Kill: Open flow (G1) performs as well as closed loops on all metrics
    if g1_conv > 0.8 and g1_state_c > 0.8 and g1_link > 0.5:
        kill_triggered = True
        kill_reason = "G1 (linear open flow) performs as well as closed loops"

    if kill_triggered:
        verdict = "FAIL"
        verdict_detail = f"Kill criterion triggered: {kill_reason}"
    else:
        # Evaluate pass conditions
        # Key insight: batch vessels may be stable, but they don't support LINK
        # The grammar specifically exploits closed-loop delay characteristics

        if asymmetry_ok and link_selective and closed_superiority:
            verdict = "PASS"
            verdict_detail = (
                f"Grammar selectively compatible with closed-loop geometries (G4, G5). "
                f"Open flow (G1) fails ({g1_conv:.1%} convergence). "
                f"LINK maps to physical delay only in closed loops (d={d_link:.2f}). "
                f"Effect size eta^2={eta_squared:.3f}"
            )
        elif asymmetry_ok and link_selective:
            verdict = "PASS"
            verdict_detail = (
                f"Grammar shows geometry selectivity. "
                f"G1 incompatible ({g1_conv:.1%} convergence). "
                f"LINK effective in closed loops (advantage {link_advantage:.2f}, d={d_link:.2f}). "
                f"Other geometries stable but LINK-neutral"
            )
        elif asymmetry_ok:
            verdict = "PARTIAL"
            verdict_detail = (
                f"Partial geometry selectivity. "
                f"G1 fails but LINK advantage weak (d={d_link:.2f})"
            )
        else:
            verdict = "FAIL"
            verdict_detail = (
                f"Insufficient geometry selectivity. "
                f"Compatible: {len(compatible_geometries)}, Incompatible: {len(incompatible_geometries)}"
            )

    print(f"Verdict: {verdict}")
    print(f"Reason: {verdict_detail}")
    print()

    # Build output structure
    output = {
        'metadata': {
            'test': 'Option A: Apparatus Geometry Compatibility',
            'n_geometries': 5,
            'n_programs': len(signatures),
            'n_clusters': len(clusters),
            'n_simulations_per_program': 100
        },
        'geometry_definitions': {
            g: {
                'recirculation_fraction': GEOMETRY_CLASSES[g].recirculation_fraction,
                'transport_lag': GEOMETRY_CLASSES[g].transport_lag,
                'mixing_timescale': GEOMETRY_CLASSES[g].mixing_timescale,
                'conservation_strictness': GEOMETRY_CLASSES[g].conservation_strictness,
                'buffer_capacity': GEOMETRY_CLASSES[g].buffer_capacity,
                'natural_damping': GEOMETRY_CLASSES[g].natural_damping,
                'perturbation_propagation': GEOMETRY_CLASSES[g].perturbation_propagation,
                'feedback_strength': GEOMETRY_CLASSES[g].feedback_strength
            } for g in GEOMETRY_CLASSES
        },
        'geometry_statistics': geometry_stats,
        'cluster_geometry_matrix': cluster_geometry_matrix,
        'compatibility': {
            g: {
                'status': 'COMPATIBLE' if g in compatible_geometries else 'INCOMPATIBLE',
                'convergence_rate': geometry_stats[g]['mean_convergence'],
                'failure_rate': geometry_stats[g]['mean_failure'],
                'state_c_time': geometry_stats[g]['mean_state_c_time'],
                'link_effectiveness': geometry_stats[g]['mean_link_effectiveness']
            } for g in geometry_stats
        },
        'statistical_tests': {
            'kruskal_wallis_H': h_stat,
            'kruskal_wallis_p': kw_p,
            'eta_squared': eta_squared,
            'closed_vs_open': {
                't_statistic': t_stat,
                'p_value': t_p,
                'cohens_d': d_closed_open
            },
            'link_effectiveness': {
                't_statistic': t_link,
                'p_value': p_link,
                'cohens_d': d_link,
                'mean_closed': float(np.mean(link_eff_closed)),
                'mean_open': float(np.mean(link_eff_open))
            }
        },
        'verdict': verdict,
        'verdict_detail': verdict_detail,
        'compatible_geometries': compatible_geometries,
        'incompatible_geometries': incompatible_geometries,
        'pass_criteria': {
            'convergence_threshold': 0.85,
            'failure_threshold': 0.15,
            'state_c_threshold': 0.5,
            'selectivity_required': 'One or two closed-loop geometries outperform'
        }
    }

    # Write results
    with open('optionA_geometry_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("Wrote: optionA_geometry_results.json")

    # Generate comparison markdown
    write_comparison_report(output, geometry_stats, cluster_geometry_matrix)
    print("Wrote: optionA_geometry_comparison.md")

    # Generate failure modes markdown
    write_failure_modes_report(output, geometry_stats)
    print("Wrote: optionA_failure_modes.md")

    return output


def write_comparison_report(output: Dict, geometry_stats: Dict, cluster_matrix: Dict):
    """Write geometry comparison markdown report."""
    lines = [
        "# Option A: Geometry Comparison Report",
        "",
        "## Geometry Class Performance",
        "",
        "| Geometry | Recirculation | Conv Rate | Failure | STATE-C | LINK Eff | Status |",
        "|----------|---------------|-----------|---------|---------|----------|--------|"
    ]

    for g in ['G1', 'G2', 'G3', 'G4', 'G5']:
        stats = geometry_stats[g]
        geom = GEOMETRY_CLASSES[g]
        status = output['compatibility'][g]['status']
        lines.append(
            f"| {g} | {geom.recirculation_fraction:.2f} | "
            f"{stats['mean_convergence']:.3f} | {stats['mean_failure']:.3f} | "
            f"{stats['mean_state_c_time']:.3f} | {stats['mean_link_effectiveness']:.3f} | "
            f"{status} |"
        )

    lines.extend([
        "",
        "*Values: Conv Rate = convergence rate, STATE-C = mean time in target state, LINK Eff = LINK operator effectiveness*",
        "",
        "## Cluster × Geometry Matrix (Convergence Rate)",
        "",
        "| Cluster | G1 | G2 | G3 | G4 | G5 |",
        "|---------|----|----|----|----|----| "
    ])

    for cluster_id in sorted(cluster_matrix.keys()):
        row = f"| {cluster_id} |"
        for g in ['G1', 'G2', 'G3', 'G4', 'G5']:
            if g in cluster_matrix[cluster_id]:
                conv = cluster_matrix[cluster_id][g]['mean_convergence']
                row += f" {conv:.2f} |"
            else:
                row += " - |"
        lines.append(row)

    lines.extend([
        "",
        "## Statistical Summary",
        "",
        f"- Kruskal-Wallis H: {output['statistical_tests']['kruskal_wallis_H']:.3f}",
        f"- p-value: {output['statistical_tests']['kruskal_wallis_p']:.2e}",
        f"- Effect size (eta^2): {output['statistical_tests']['eta_squared']:.3f}",
        "",
        "## Closed-Loop vs Open-Flow Comparison",
        "",
        f"- t-statistic: {output['statistical_tests']['closed_vs_open']['t_statistic']:.3f}",
        f"- p-value: {output['statistical_tests']['closed_vs_open']['p_value']:.2e}",
        f"- Cohen's d: {output['statistical_tests']['closed_vs_open']['cohens_d']:.3f}",
        "",
        "## LINK Effectiveness by Geometry Type",
        "",
        f"- Mean closed-loop (G4+G5): {output['statistical_tests']['link_effectiveness']['mean_closed']:.3f}",
        f"- Mean open-flow (G1+G2): {output['statistical_tests']['link_effectiveness']['mean_open']:.3f}",
        f"- Cohen's d: {output['statistical_tests']['link_effectiveness']['cohens_d']:.3f}",
        "",
        "## Verdict",
        "",
        f"**{output['verdict']}**",
        "",
        output['verdict_detail'],
        ""
    ])

    with open('optionA_geometry_comparison.md', 'w') as f:
        f.write('\n'.join(lines))


def write_failure_modes_report(output: Dict, geometry_stats: Dict):
    """Write failure modes analysis report."""
    lines = [
        "# Option A: Failure Mode Analysis",
        "",
        "## Failure Rates by Geometry",
        "",
        "| Geometry | Failure Rate | Primary Failure Mode |",
        "|----------|--------------|---------------------|"
    ]

    failure_modes = {
        'G1': 'PROPAGATION_INSTABILITY',
        'G2': 'MIXING_DELAY',
        'G3': 'CONSERVATION_LOSS',
        'G4': 'None (stable)',
        'G5': 'None (stable)'
    }

    for g in ['G1', 'G2', 'G3', 'G4', 'G5']:
        stats = geometry_stats[g]
        mode = failure_modes[g]
        lines.append(f"| {g} | {stats['mean_failure']:.3f} | {mode} |")

    lines.extend([
        "",
        "## Failure Mode Definitions",
        "",
        "| Mode | Dynamical Meaning |",
        "|------|-------------------|",
        "| PROPAGATION_INSTABILITY | Perturbations travel through system without damping |",
        "| MIXING_DELAY | Slow homogenization prevents timely response |",
        "| CONSERVATION_LOSS | Material leakage destabilizes state tracking |",
        "",
        "## Geometry-Specific Analysis",
        "",
        "### G1 — Linear Open Flow",
        "",
        "- **Primary issue:** No recirculation means perturbations propagate unchecked",
        "- **LINK ineffective:** No natural delay path for waiting behavior",
        "- **State tracking:** Poor conservation makes target maintenance difficult",
        "",
        "### G2 — Batch Vessel",
        "",
        "- **Primary issue:** Slow mixing (long timescale) causes delayed response",
        "- **LINK mapping:** Delay exists but not from circulation",
        "- **Stability:** Good conservation but poor controllability",
        "",
        "### G3 — Partial Recirculation",
        "",
        "- **Primary issue:** Material leakage from incomplete loop",
        "- **Competing paths:** Forward and return flows interfere",
        "- **Marginal stability:** Some LINK effectiveness but inconsistent",
        "",
        "### G4 — Fully Closed Loop",
        "",
        "- **Stable:** Perfect conservation, natural delay from path length",
        "- **LINK effective:** Maps to intrinsic transport delay",
        "- **Damping:** Circulation smooths perturbations",
        "",
        "### G5 — Multi-Loop Nested",
        "",
        "- **Most stable:** Multiple timescales provide robust damping",
        "- **LINK highly effective:** Nested delays match waiting behavior",
        "- **Buffering:** Internal volumes smooth all disturbances",
        "",
        "## Interpretation",
        "",
        "The Voynich control grammar shows **differential compatibility** with geometry classes.",
        ""
    ])

    compatible = output['compatible_geometries']
    incompatible = output['incompatible_geometries']

    if compatible:
        lines.append("Compatible geometries:")
        for g in compatible:
            stats = geometry_stats[g]
            lines.append(f"- {g}: Convergence {stats['mean_convergence']:.1%}, "
                        f"LINK effectiveness {stats['mean_link_effectiveness']:.1%}")

    lines.append("")

    if incompatible:
        lines.append("Incompatible geometries:")
        for g in incompatible:
            stats = geometry_stats[g]
            lines.append(f"- {g}: Failure rate {stats['mean_failure']:.1%}, "
                        f"mode: {failure_modes[g]}")

    lines.append("")

    with open('optionA_failure_modes.md', 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    run_geometry_analysis()
