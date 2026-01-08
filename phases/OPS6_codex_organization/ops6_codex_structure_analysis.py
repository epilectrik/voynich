#!/usr/bin/env python3
"""
OPS-6: Program Library Topology & Codex Organization Analysis

Tests whether codex structure supports human-factors goals such as:
- Risk buffering
- Escalation damping
- Recovery accessibility
- Expert navigation through dangerous control space

Question: "Is the ordering and grouping of programs consistent with intentional
management of Control Engagement Intensity (CEI) for human operators?"

This phase is DESCRIPTIVE and FALSIFICATION-ORIENTED.
"""

import json
import csv
import re
import random
import statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent.parent.parent
OPS5_DIR = BASE_DIR / "phases" / "OPS5_control_engagement_intensity"
OPS6_DIR = Path(__file__).parent

# Quire boundaries (folio AFTER the boundary is the first of new quire)
# From CLAUDE.md: f25v→f26r = Herbal A/B boundary; f32v→f33r, f48v→f49r = quire changes
QUIRE_BOUNDARIES = ["f26r", "f33r", "f49r"]

# Restart-capable folios (from CLAUDE.md)
RESTART_CAPABLE = ["f50v", "f57r", "f82v"]

# Number of randomizations for null model
N_RANDOMIZATIONS = 1000

# High-CEI threshold (upper tercile)
HIGH_CEI_THRESHOLD = 0.60

# ============================================================
# DATA LOADING
# ============================================================

def load_cei_data() -> Dict[str, Dict]:
    """Load CEI data from OPS-5 outputs."""
    # Load placement CSV
    placement_file = OPS5_DIR / "ops5_cei_placement.csv"
    folios = {}

    with open(placement_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            folios[row['folio_id']] = {
                'regime': row['regime_id'],
                'cei': float(row['cei_value']),
                'band': row['band_id']
            }

    return folios


def get_folio_sort_key(folio_id: str) -> Tuple[int, int, int]:
    """
    Extract sort key from folio ID for manuscript ordering.

    Format: f#[rv][#] where # is folio number, r/v is recto/verso, optional suffix
    Examples: f26r, f86v3, f95r1
    """
    match = re.match(r'f(\d+)([rv])(\d*)', folio_id)
    if not match:
        return (999, 0, 0)

    folio_num = int(match.group(1))
    side = 0 if match.group(2) == 'r' else 1
    suffix = int(match.group(3)) if match.group(3) else 0

    return (folio_num, side, suffix)


def get_ordered_folios(folios: Dict) -> List[str]:
    """Return folio IDs in manuscript order."""
    return sorted(folios.keys(), key=get_folio_sort_key)


# ============================================================
# HYPOTHESIS 3.1: CEI SMOOTHING
# ============================================================

def compute_local_cei_gradient(folios: Dict, ordered: List[str]) -> List[float]:
    """Compute absolute CEI jumps between adjacent folios."""
    gradients = []
    for i in range(1, len(ordered)):
        prev_cei = folios[ordered[i-1]]['cei']
        curr_cei = folios[ordered[i]]['cei']
        gradients.append(abs(curr_cei - prev_cei))
    return gradients


def compute_neighborhood_variance(folios: Dict, ordered: List[str],
                                   window: int = 3) -> List[float]:
    """Compute local CEI variance in sliding window."""
    variances = []
    cei_values = [folios[f]['cei'] for f in ordered]

    for i in range(len(ordered)):
        start = max(0, i - window // 2)
        end = min(len(ordered), i + window // 2 + 1)
        local_ceis = cei_values[start:end]
        if len(local_ceis) > 1:
            variances.append(statistics.variance(local_ceis))
        else:
            variances.append(0)

    return variances


def test_cei_smoothing(folios: Dict, ordered: List[str],
                       n_random: int = N_RANDOMIZATIONS) -> Dict:
    """
    Test whether manuscript ordering reduces CEI jumps compared to random.
    """
    print("\n" + "="*60)
    print("HYPOTHESIS 3.1: CEI SMOOTHING")
    print("="*60)

    # Observed metrics
    observed_gradients = compute_local_cei_gradient(folios, ordered)
    observed_mean_jump = statistics.mean(observed_gradients)
    observed_max_jump = max(observed_gradients)
    observed_variances = compute_neighborhood_variance(folios, ordered)
    observed_mean_variance = statistics.mean(observed_variances)

    # Null model: randomized orderings
    null_mean_jumps = []
    null_max_jumps = []
    null_mean_variances = []

    for _ in range(n_random):
        shuffled = list(ordered)
        random.shuffle(shuffled)

        gradients = compute_local_cei_gradient(folios, shuffled)
        null_mean_jumps.append(statistics.mean(gradients))
        null_max_jumps.append(max(gradients))

        variances = compute_neighborhood_variance(folios, shuffled)
        null_mean_variances.append(statistics.mean(variances))

    # Compute percentiles
    mean_jump_percentile = sum(1 for x in null_mean_jumps if x <= observed_mean_jump) / n_random * 100
    max_jump_percentile = sum(1 for x in null_max_jumps if x <= observed_max_jump) / n_random * 100
    variance_percentile = sum(1 for x in null_mean_variances if x <= observed_mean_variance) / n_random * 100

    # Compute effect sizes
    null_mean_jump_mean = statistics.mean(null_mean_jumps)
    null_mean_jump_std = statistics.stdev(null_mean_jumps)
    effect_size_jump = (null_mean_jump_mean - observed_mean_jump) / null_mean_jump_std if null_mean_jump_std > 0 else 0

    null_variance_mean = statistics.mean(null_mean_variances)
    null_variance_std = statistics.stdev(null_mean_variances)
    effect_size_variance = (null_variance_mean - observed_mean_variance) / null_variance_std if null_variance_std > 0 else 0

    # Determine status
    # Significant smoothing if observed is lower than 95% of null
    smoothing_detected = mean_jump_percentile < 5.0
    status = "SUPPORTED" if smoothing_detected else ("INCONCLUSIVE" if mean_jump_percentile < 25 else "REJECTED")

    results = {
        "hypothesis": "CEI Smoothing",
        "observed": {
            "mean_cei_jump": round(observed_mean_jump, 4),
            "max_cei_jump": round(observed_max_jump, 4),
            "mean_neighborhood_variance": round(observed_mean_variance, 6)
        },
        "null_distribution": {
            "mean_jump_mean": round(null_mean_jump_mean, 4),
            "mean_jump_std": round(null_mean_jump_std, 4),
            "variance_mean": round(null_variance_mean, 6),
            "variance_std": round(null_variance_std, 6)
        },
        "percentiles": {
            "mean_jump_percentile": round(mean_jump_percentile, 2),
            "max_jump_percentile": round(max_jump_percentile, 2),
            "variance_percentile": round(variance_percentile, 2)
        },
        "effect_sizes": {
            "jump_reduction_cohen_d": round(effect_size_jump, 3),
            "variance_reduction_cohen_d": round(effect_size_variance, 3)
        },
        "status": status,
        "interpretation": f"Observed mean CEI jump ({observed_mean_jump:.4f}) is at {mean_jump_percentile:.1f}th percentile of null distribution"
    }

    print(f"\nObserved mean CEI jump: {observed_mean_jump:.4f}")
    print(f"Null mean: {null_mean_jump_mean:.4f} ± {null_mean_jump_std:.4f}")
    print(f"Percentile: {mean_jump_percentile:.1f}%")
    print(f"Effect size (Cohen's d): {effect_size_jump:.3f}")
    print(f"Status: {status}")

    return results


# ============================================================
# HYPOTHESIS 3.2: HIGH-CEI ISOLATION
# ============================================================

def find_high_cei_clusters(folios: Dict, ordered: List[str],
                           threshold: float = HIGH_CEI_THRESHOLD) -> List[List[str]]:
    """Find clusters of consecutive high-CEI folios."""
    clusters = []
    current_cluster = []

    for folio in ordered:
        if folios[folio]['cei'] >= threshold:
            current_cluster.append(folio)
        else:
            if current_cluster:
                clusters.append(current_cluster)
                current_cluster = []

    if current_cluster:
        clusters.append(current_cluster)

    return clusters


def compute_high_cei_isolation_metrics(folios: Dict, ordered: List[str],
                                        threshold: float = HIGH_CEI_THRESHOLD) -> Dict:
    """Compute isolation metrics for high-CEI folios."""
    high_cei_folios = [f for f in ordered if folios[f]['cei'] >= threshold]
    clusters = find_high_cei_clusters(folios, ordered, threshold)

    # Compute gaps between high-CEI folios
    high_cei_indices = [ordered.index(f) for f in high_cei_folios]
    gaps = []
    for i in range(1, len(high_cei_indices)):
        gaps.append(high_cei_indices[i] - high_cei_indices[i-1])

    # Compute neighbor CEI average for high-CEI folios
    neighbor_ceis = []
    for folio in high_cei_folios:
        idx = ordered.index(folio)
        neighbors = []
        if idx > 0:
            neighbors.append(folios[ordered[idx-1]]['cei'])
        if idx < len(ordered) - 1:
            neighbors.append(folios[ordered[idx+1]]['cei'])
        if neighbors:
            neighbor_ceis.append(statistics.mean(neighbors))

    return {
        "n_high_cei": len(high_cei_folios),
        "n_clusters": len(clusters),
        "cluster_sizes": [len(c) for c in clusters],
        "max_cluster_size": max([len(c) for c in clusters]) if clusters else 0,
        "mean_gap_between_high_cei": statistics.mean(gaps) if gaps else 0,
        "mean_neighbor_cei": statistics.mean(neighbor_ceis) if neighbor_ceis else 0
    }


def test_high_cei_isolation(folios: Dict, ordered: List[str],
                             n_random: int = N_RANDOMIZATIONS) -> Dict:
    """
    Test whether high-CEI folios are isolated/buffered.
    """
    print("\n" + "="*60)
    print("HYPOTHESIS 3.2: HIGH-CEI ISOLATION")
    print("="*60)

    # Observed metrics
    observed = compute_high_cei_isolation_metrics(folios, ordered)

    # Null model
    null_max_cluster_sizes = []
    null_mean_neighbor_ceis = []
    null_mean_gaps = []

    for _ in range(n_random):
        shuffled = list(ordered)
        random.shuffle(shuffled)

        metrics = compute_high_cei_isolation_metrics(folios, shuffled)
        null_max_cluster_sizes.append(metrics['max_cluster_size'])
        null_mean_neighbor_ceis.append(metrics['mean_neighbor_cei'])
        if metrics['mean_gap_between_high_cei'] > 0:
            null_mean_gaps.append(metrics['mean_gap_between_high_cei'])

    # Percentiles
    cluster_percentile = sum(1 for x in null_max_cluster_sizes if x >= observed['max_cluster_size']) / n_random * 100
    neighbor_percentile = sum(1 for x in null_mean_neighbor_ceis if x <= observed['mean_neighbor_cei']) / n_random * 100

    # Effect sizes
    null_cluster_mean = statistics.mean(null_max_cluster_sizes)
    null_cluster_std = statistics.stdev(null_max_cluster_sizes) if len(null_max_cluster_sizes) > 1 else 1
    effect_cluster = (null_cluster_mean - observed['max_cluster_size']) / null_cluster_std if null_cluster_std > 0 else 0

    # Buffering: are high-CEI neighbors lower than expected?
    null_neighbor_mean = statistics.mean(null_mean_neighbor_ceis) if null_mean_neighbor_ceis else 0
    null_neighbor_std = statistics.stdev(null_mean_neighbor_ceis) if len(null_mean_neighbor_ceis) > 1 else 1
    effect_buffering = (null_neighbor_mean - observed['mean_neighbor_cei']) / null_neighbor_std if null_neighbor_std > 0 else 0

    # Determine status
    # Isolation supported if clusters are smaller than expected AND neighbors are lower-CEI
    isolation_detected = cluster_percentile > 50 and neighbor_percentile < 25
    status = "SUPPORTED" if isolation_detected else ("INCONCLUSIVE" if cluster_percentile > 25 else "REJECTED")

    results = {
        "hypothesis": "High-CEI Isolation",
        "threshold": HIGH_CEI_THRESHOLD,
        "observed": {
            "n_high_cei_folios": observed['n_high_cei'],
            "n_clusters": observed['n_clusters'],
            "cluster_sizes": observed['cluster_sizes'],
            "max_cluster_size": observed['max_cluster_size'],
            "mean_neighbor_cei": round(observed['mean_neighbor_cei'], 4),
            "mean_gap_between_high_cei": round(observed['mean_gap_between_high_cei'], 2)
        },
        "null_distribution": {
            "max_cluster_mean": round(null_cluster_mean, 2),
            "max_cluster_std": round(null_cluster_std, 2),
            "neighbor_cei_mean": round(null_neighbor_mean, 4),
            "neighbor_cei_std": round(null_neighbor_std, 4)
        },
        "percentiles": {
            "cluster_size_percentile": round(cluster_percentile, 2),
            "neighbor_cei_percentile": round(neighbor_percentile, 2)
        },
        "effect_sizes": {
            "cluster_isolation_cohen_d": round(effect_cluster, 3),
            "neighbor_buffering_cohen_d": round(effect_buffering, 3)
        },
        "status": status,
        "interpretation": f"Max cluster size ({observed['max_cluster_size']}) at {cluster_percentile:.1f}th percentile; neighbor CEI ({observed['mean_neighbor_cei']:.3f}) at {neighbor_percentile:.1f}th percentile"
    }

    print(f"\nHigh-CEI folios: {observed['n_high_cei']}")
    print(f"Clusters: {observed['n_clusters']}, sizes: {observed['cluster_sizes']}")
    print(f"Max cluster size: {observed['max_cluster_size']} (null mean: {null_cluster_mean:.2f})")
    print(f"Mean neighbor CEI: {observed['mean_neighbor_cei']:.4f} (null mean: {null_neighbor_mean:.4f})")
    print(f"Status: {status}")

    return results


# ============================================================
# HYPOTHESIS 3.3: RESTART PLACEMENT
# ============================================================

def test_restart_placement(folios: Dict, ordered: List[str],
                            n_random: int = N_RANDOMIZATIONS) -> Dict:
    """
    Test whether restart-capable folios are strategically placed.
    """
    print("\n" + "="*60)
    print("HYPOTHESIS 3.3: RESTART PLACEMENT")
    print("="*60)

    # Get restart folio positions and CEI values
    restart_positions = []
    restart_ceis = []
    for folio in RESTART_CAPABLE:
        if folio in folios:
            idx = ordered.index(folio)
            restart_positions.append(idx)
            restart_ceis.append(folios[folio]['cei'])

    if not restart_positions:
        return {
            "hypothesis": "Restart Placement",
            "status": "NO_DATA",
            "interpretation": "No restart-capable folios found in dataset"
        }

    # Compute metrics
    # 1. Distance to nearest high-CEI folio (after restart)
    high_cei_indices = [i for i, f in enumerate(ordered) if folios[f]['cei'] >= HIGH_CEI_THRESHOLD]

    distances_to_high_cei = []
    for restart_idx in restart_positions:
        # Find nearest high-CEI folio before restart
        before = [i for i in high_cei_indices if i < restart_idx]
        if before:
            distances_to_high_cei.append(restart_idx - max(before))

    # 2. Local CEI gradient around restart
    cei_drops_after_restart = []
    for restart_idx in restart_positions:
        if restart_idx > 0 and restart_idx < len(ordered) - 1:
            before_cei = folios[ordered[restart_idx - 1]]['cei']
            restart_cei = folios[ordered[restart_idx]]['cei']
            after_cei = folios[ordered[restart_idx + 1]]['cei']
            # Does restart create a local minimum?
            if restart_cei < before_cei:
                cei_drops_after_restart.append(before_cei - restart_cei)

    # 3. Average CEI of restart folios
    mean_restart_cei = statistics.mean(restart_ceis)
    overall_mean_cei = statistics.mean([folios[f]['cei'] for f in ordered])

    # Null model: random placement of 3 "restart" markers
    null_mean_restart_ceis = []
    null_distances_to_high = []

    for _ in range(n_random):
        random_positions = random.sample(range(len(ordered)), len(restart_positions))
        random_ceis = [folios[ordered[p]]['cei'] for p in random_positions]
        null_mean_restart_ceis.append(statistics.mean(random_ceis))

        # Distance to nearest high-CEI
        for pos in random_positions:
            before = [i for i in high_cei_indices if i < pos]
            if before:
                null_distances_to_high.append(pos - max(before))

    # Percentiles
    cei_percentile = sum(1 for x in null_mean_restart_ceis if x <= mean_restart_cei) / n_random * 100

    observed_mean_dist = statistics.mean(distances_to_high_cei) if distances_to_high_cei else 0
    null_mean_dist = statistics.mean(null_distances_to_high) if null_distances_to_high else 0
    null_std_dist = statistics.stdev(null_distances_to_high) if len(null_distances_to_high) > 1 else 1

    # Effect size for CEI
    null_cei_mean = statistics.mean(null_mean_restart_ceis)
    null_cei_std = statistics.stdev(null_mean_restart_ceis) if len(null_mean_restart_ceis) > 1 else 1
    effect_size_cei = (null_cei_mean - mean_restart_cei) / null_cei_std if null_cei_std > 0 else 0

    # Strategic placement if restart folios have lower CEI than random
    strategic = cei_percentile < 25
    status = "SUPPORTED" if strategic else ("INCONCLUSIVE" if cei_percentile < 50 else "REJECTED")

    results = {
        "hypothesis": "Restart Placement",
        "restart_folios": RESTART_CAPABLE,
        "observed": {
            "restart_positions": dict(zip(RESTART_CAPABLE, restart_positions)),
            "restart_ceis": dict(zip(RESTART_CAPABLE, [round(c, 4) for c in restart_ceis])),
            "mean_restart_cei": round(mean_restart_cei, 4),
            "overall_mean_cei": round(overall_mean_cei, 4),
            "mean_distance_to_high_cei_before": round(observed_mean_dist, 2),
            "cei_drops_after_restart": [round(d, 4) for d in cei_drops_after_restart]
        },
        "null_distribution": {
            "mean_random_cei": round(null_cei_mean, 4),
            "std_random_cei": round(null_cei_std, 4),
            "mean_random_distance": round(null_mean_dist, 2)
        },
        "percentiles": {
            "restart_cei_percentile": round(cei_percentile, 2)
        },
        "effect_sizes": {
            "cei_placement_cohen_d": round(effect_size_cei, 3)
        },
        "status": status,
        "interpretation": f"Restart folios have mean CEI {mean_restart_cei:.4f} ({cei_percentile:.1f}th percentile of random)"
    }

    print(f"\nRestart folios: {RESTART_CAPABLE}")
    print(f"Restart CEI values: {dict(zip(RESTART_CAPABLE, [round(c, 4) for c in restart_ceis]))}")
    print(f"Mean restart CEI: {mean_restart_cei:.4f} (overall mean: {overall_mean_cei:.4f})")
    print(f"Percentile: {cei_percentile:.1f}%")
    print(f"Status: {status}")

    return results


# ============================================================
# HYPOTHESIS 3.4: QUIRE BOUNDARY INTERACTION
# ============================================================

def test_quire_boundary_interaction(folios: Dict, ordered: List[str],
                                      n_random: int = N_RANDOMIZATIONS) -> Dict:
    """
    Test whether quire boundaries interact with CEI structure.
    """
    print("\n" + "="*60)
    print("HYPOTHESIS 3.4: QUIRE BOUNDARY INTERACTION")
    print("="*60)

    # Find quire boundary positions
    boundary_positions = []
    for boundary in QUIRE_BOUNDARIES:
        if boundary in ordered:
            boundary_positions.append(ordered.index(boundary))

    if not boundary_positions:
        return {
            "hypothesis": "Quire Boundary Interaction",
            "status": "NO_DATA",
            "interpretation": "No quire boundaries found in ordered folio list"
        }

    # Metrics at boundaries
    boundary_ceis = []
    cei_before_boundary = []
    cei_after_boundary = []
    cei_jumps_at_boundary = []

    for pos in boundary_positions:
        boundary_ceis.append(folios[ordered[pos]]['cei'])

        if pos > 0:
            cei_before_boundary.append(folios[ordered[pos-1]]['cei'])
            cei_jumps_at_boundary.append(abs(folios[ordered[pos]]['cei'] - folios[ordered[pos-1]]['cei']))

        # CEI variance in window after boundary
        window_after = [folios[ordered[i]]['cei'] for i in range(pos, min(pos+5, len(ordered)))]
        if len(window_after) > 1:
            cei_after_boundary.append(statistics.variance(window_after))

    mean_boundary_cei = statistics.mean(boundary_ceis) if boundary_ceis else 0
    mean_jump_at_boundary = statistics.mean(cei_jumps_at_boundary) if cei_jumps_at_boundary else 0
    mean_variance_after = statistics.mean(cei_after_boundary) if cei_after_boundary else 0

    # Compare to non-boundary positions
    non_boundary_jumps = []
    for i in range(1, len(ordered)):
        if i not in boundary_positions:
            non_boundary_jumps.append(abs(folios[ordered[i]]['cei'] - folios[ordered[i-1]]['cei']))

    mean_non_boundary_jump = statistics.mean(non_boundary_jumps) if non_boundary_jumps else 0

    # Null model: random boundary placement
    null_boundary_ceis = []
    null_boundary_jumps = []

    for _ in range(n_random):
        random_positions = random.sample(range(1, len(ordered)), len(boundary_positions))

        null_ceis = [folios[ordered[p]]['cei'] for p in random_positions]
        null_boundary_ceis.append(statistics.mean(null_ceis))

        null_jumps = [abs(folios[ordered[p]]['cei'] - folios[ordered[p-1]]['cei']) for p in random_positions]
        null_boundary_jumps.append(statistics.mean(null_jumps))

    # Percentiles
    cei_percentile = sum(1 for x in null_boundary_ceis if x <= mean_boundary_cei) / n_random * 100
    jump_percentile = sum(1 for x in null_boundary_jumps if x >= mean_jump_at_boundary) / n_random * 100

    # Effect sizes
    null_cei_mean = statistics.mean(null_boundary_ceis)
    null_cei_std = statistics.stdev(null_boundary_ceis) if len(null_boundary_ceis) > 1 else 1
    effect_cei = (mean_boundary_cei - null_cei_mean) / null_cei_std if null_cei_std > 0 else 0

    # CEI reset: boundaries should have lower CEI than average
    cei_reset_detected = cei_percentile < 25
    # Jump suppression: boundaries should NOT have larger jumps
    jump_suppressed = jump_percentile < 75

    status = "SUPPORTED" if (cei_reset_detected and jump_suppressed) else "INCONCLUSIVE" if (cei_reset_detected or jump_suppressed) else "REJECTED"

    results = {
        "hypothesis": "Quire Boundary Interaction",
        "quire_boundaries": QUIRE_BOUNDARIES,
        "boundary_positions": boundary_positions,
        "observed": {
            "boundary_ceis": dict(zip(QUIRE_BOUNDARIES[:len(boundary_ceis)], [round(c, 4) for c in boundary_ceis])),
            "mean_boundary_cei": round(mean_boundary_cei, 4),
            "mean_jump_at_boundary": round(mean_jump_at_boundary, 4),
            "mean_non_boundary_jump": round(mean_non_boundary_jump, 4),
            "mean_variance_after_boundary": round(mean_variance_after, 6)
        },
        "null_distribution": {
            "mean_random_boundary_cei": round(null_cei_mean, 4),
            "std_random_boundary_cei": round(null_cei_std, 4),
            "mean_random_boundary_jump": round(statistics.mean(null_boundary_jumps), 4)
        },
        "percentiles": {
            "boundary_cei_percentile": round(cei_percentile, 2),
            "boundary_jump_percentile": round(jump_percentile, 2)
        },
        "effect_sizes": {
            "boundary_cei_cohen_d": round(effect_cei, 3)
        },
        "status": status,
        "interpretation": f"Boundary CEI at {cei_percentile:.1f}th percentile; boundary jumps at {jump_percentile:.1f}th percentile"
    }

    print(f"\nQuire boundaries: {QUIRE_BOUNDARIES}")
    print(f"Boundary CEIs: {dict(zip(QUIRE_BOUNDARIES[:len(boundary_ceis)], [round(c, 4) for c in boundary_ceis]))}")
    print(f"Mean boundary CEI: {mean_boundary_cei:.4f} (null: {null_cei_mean:.4f})")
    print(f"Mean jump at boundary: {mean_jump_at_boundary:.4f} (non-boundary: {mean_non_boundary_jump:.4f})")
    print(f"Status: {status}")

    return results


# ============================================================
# HYPOTHESIS 3.5: NAVIGATION TOPOLOGY
# ============================================================

def compute_navigation_metrics(folios: Dict, ordered: List[str]) -> Dict:
    """
    Compute navigation topology metrics.

    Treat codex as linear navigation graph. Test:
    - Reachability of low-CEI basins from any location
    - Maximum steps to retreat from high-CEI region
    - Existence of "trap" regions
    """
    # Define low-CEI threshold (lower tercile)
    cei_values = [folios[f]['cei'] for f in ordered]
    low_threshold = sorted(cei_values)[len(cei_values) // 3]

    low_cei_positions = [i for i, f in enumerate(ordered) if folios[f]['cei'] < low_threshold]
    high_cei_positions = [i for i, f in enumerate(ordered) if folios[f]['cei'] >= HIGH_CEI_THRESHOLD]

    # Distance to nearest low-CEI from each position
    distances_to_low = []
    for i in range(len(ordered)):
        min_dist = min([abs(i - lp) for lp in low_cei_positions]) if low_cei_positions else len(ordered)
        distances_to_low.append(min_dist)

    # Maximum distance to low-CEI (worst case)
    max_distance_to_low = max(distances_to_low)
    mean_distance_to_low = statistics.mean(distances_to_low)

    # Steps to retreat from high-CEI regions
    retreat_distances = []
    for hp in high_cei_positions:
        # Distance to nearest low-CEI
        min_dist = min([abs(hp - lp) for lp in low_cei_positions]) if low_cei_positions else len(ordered)
        retreat_distances.append(min_dist)

    max_retreat = max(retreat_distances) if retreat_distances else 0
    mean_retreat = statistics.mean(retreat_distances) if retreat_distances else 0

    # Trap regions: contiguous high-CEI regions with no nearby low-CEI
    trap_threshold = 5  # More than 5 steps to low-CEI = potential trap
    trap_positions = [i for i in high_cei_positions if distances_to_low[i] > trap_threshold]

    return {
        "low_cei_threshold": low_threshold,
        "n_low_cei_positions": len(low_cei_positions),
        "n_high_cei_positions": len(high_cei_positions),
        "max_distance_to_low_cei": max_distance_to_low,
        "mean_distance_to_low_cei": mean_distance_to_low,
        "max_retreat_distance": max_retreat,
        "mean_retreat_distance": mean_retreat,
        "n_trap_positions": len(trap_positions),
        "trap_positions": trap_positions
    }


def test_navigation_topology(folios: Dict, ordered: List[str],
                               n_random: int = N_RANDOMIZATIONS) -> Dict:
    """
    Test whether navigation topology supports safe retreat.
    """
    print("\n" + "="*60)
    print("HYPOTHESIS 3.5: NAVIGATION TOPOLOGY")
    print("="*60)

    # Observed metrics
    observed = compute_navigation_metrics(folios, ordered)

    # Null model
    null_max_retreats = []
    null_mean_retreats = []
    null_trap_counts = []

    for _ in range(n_random):
        shuffled = list(ordered)
        random.shuffle(shuffled)

        metrics = compute_navigation_metrics(folios, shuffled)
        null_max_retreats.append(metrics['max_retreat_distance'])
        null_mean_retreats.append(metrics['mean_retreat_distance'])
        null_trap_counts.append(metrics['n_trap_positions'])

    # Percentiles
    max_retreat_percentile = sum(1 for x in null_max_retreats if x >= observed['max_retreat_distance']) / n_random * 100
    mean_retreat_percentile = sum(1 for x in null_mean_retreats if x >= observed['mean_retreat_distance']) / n_random * 100
    trap_percentile = sum(1 for x in null_trap_counts if x >= observed['n_trap_positions']) / n_random * 100

    # Effect sizes
    null_max_retreat_mean = statistics.mean(null_max_retreats)
    null_max_retreat_std = statistics.stdev(null_max_retreats) if len(null_max_retreats) > 1 else 1
    effect_retreat = (null_max_retreat_mean - observed['max_retreat_distance']) / null_max_retreat_std if null_max_retreat_std > 0 else 0

    null_trap_mean = statistics.mean(null_trap_counts)
    null_trap_std = statistics.stdev(null_trap_counts) if len(null_trap_counts) > 1 else 1
    effect_trap = (null_trap_mean - observed['n_trap_positions']) / null_trap_std if null_trap_std > 0 else 0

    # Good topology if retreat distances are shorter than random AND no/few traps
    good_retreat = max_retreat_percentile > 50
    few_traps = trap_percentile > 50

    status = "SUPPORTED" if (good_retreat and few_traps) else "INCONCLUSIVE" if (good_retreat or few_traps) else "REJECTED"

    results = {
        "hypothesis": "Navigation Topology",
        "observed": {
            "low_cei_threshold": round(observed['low_cei_threshold'], 4),
            "n_low_cei_positions": observed['n_low_cei_positions'],
            "n_high_cei_positions": observed['n_high_cei_positions'],
            "max_retreat_distance": observed['max_retreat_distance'],
            "mean_retreat_distance": round(observed['mean_retreat_distance'], 2),
            "n_trap_positions": observed['n_trap_positions']
        },
        "null_distribution": {
            "mean_max_retreat": round(null_max_retreat_mean, 2),
            "std_max_retreat": round(null_max_retreat_std, 2),
            "mean_trap_count": round(null_trap_mean, 2),
            "std_trap_count": round(null_trap_std, 2)
        },
        "percentiles": {
            "max_retreat_percentile": round(max_retreat_percentile, 2),
            "mean_retreat_percentile": round(mean_retreat_percentile, 2),
            "trap_count_percentile": round(trap_percentile, 2)
        },
        "effect_sizes": {
            "retreat_reduction_cohen_d": round(effect_retreat, 3),
            "trap_reduction_cohen_d": round(effect_trap, 3)
        },
        "status": status,
        "interpretation": f"Max retreat {observed['max_retreat_distance']} steps ({max_retreat_percentile:.1f}th percentile); {observed['n_trap_positions']} trap positions ({trap_percentile:.1f}th percentile)"
    }

    print(f"\nMax retreat distance: {observed['max_retreat_distance']} (null mean: {null_max_retreat_mean:.2f})")
    print(f"Mean retreat distance: {observed['mean_retreat_distance']:.2f}")
    print(f"Trap positions: {observed['n_trap_positions']} (null mean: {null_trap_mean:.2f})")
    print(f"Status: {status}")

    return results


# ============================================================
# SUPPLEMENTARY: CEI BUFFERING ANALYSIS
# ============================================================

def analyze_cei_buffering(folios: Dict, ordered: List[str]) -> Dict:
    """
    Detailed analysis of high-CEI neighbor buffering.
    """
    print("\n" + "="*60)
    print("SUPPLEMENTARY: CEI NEIGHBOR BUFFERING")
    print("="*60)

    # For each folio, compute how much its neighbors dampen or amplify CEI
    buffering_scores = []
    amplification_cases = 0
    damping_cases = 0

    high_cei_folios = [f for f in ordered if folios[f]['cei'] >= HIGH_CEI_THRESHOLD]

    for folio in high_cei_folios:
        idx = ordered.index(folio)
        folio_cei = folios[folio]['cei']

        neighbors = []
        if idx > 0:
            neighbors.append(folios[ordered[idx-1]]['cei'])
        if idx < len(ordered) - 1:
            neighbors.append(folios[ordered[idx+1]]['cei'])

        if neighbors:
            mean_neighbor = statistics.mean(neighbors)
            buffering = folio_cei - mean_neighbor  # Positive = neighbors dampen
            buffering_scores.append({
                'folio': folio,
                'cei': folio_cei,
                'mean_neighbor_cei': mean_neighbor,
                'buffering': buffering
            })

            if mean_neighbor < folio_cei:
                damping_cases += 1
            else:
                amplification_cases += 1

    return {
        "n_high_cei_analyzed": len(high_cei_folios),
        "damping_cases": damping_cases,
        "amplification_cases": amplification_cases,
        "damping_rate": damping_cases / len(high_cei_folios) if high_cei_folios else 0,
        "details": buffering_scores
    }


# ============================================================
# OUTPUT GENERATION
# ============================================================

def generate_structural_summary(results: Dict) -> List[Dict]:
    """Generate summary CSV data."""
    summary = []

    for key, data in results.items():
        if key == 'metadata' or key == 'buffering_analysis':
            continue

        row = {
            'hypothesis': data.get('hypothesis', key),
            'status': data.get('status', 'UNKNOWN'),
            'effect_size': 'N/A',
            'p_value_proxy': 'N/A'
        }

        if 'effect_sizes' in data:
            # Get primary effect size
            effect_sizes = data['effect_sizes']
            if effect_sizes:
                first_key = list(effect_sizes.keys())[0]
                row['effect_size'] = effect_sizes[first_key]

        if 'percentiles' in data:
            percentiles = data['percentiles']
            if percentiles:
                first_key = list(percentiles.keys())[0]
                pct = percentiles[first_key]
                # Convert to p-value proxy (lower percentile = more significant)
                row['p_value_proxy'] = f"{min(pct, 100-pct)/100:.3f}"

        summary.append(row)

    return summary


def generate_markdown_report(results: Dict, folios: Dict, ordered: List[str]) -> str:
    """Generate comprehensive markdown report."""
    lines = []

    lines.append("# Phase OPS-6: Codex Structure Analysis Report")
    lines.append("")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")

    # Count results
    supported = sum(1 for k, v in results.items() if k not in ['metadata', 'buffering_analysis'] and v.get('status') == 'SUPPORTED')
    rejected = sum(1 for k, v in results.items() if k not in ['metadata', 'buffering_analysis'] and v.get('status') == 'REJECTED')
    inconclusive = sum(1 for k, v in results.items() if k not in ['metadata', 'buffering_analysis'] and v.get('status') == 'INCONCLUSIVE')

    lines.append(f"| Result | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| SUPPORTED | {supported} |")
    lines.append(f"| REJECTED | {rejected} |")
    lines.append(f"| INCONCLUSIVE | {inconclusive} |")
    lines.append("")

    # Summary table
    lines.append("### Hypothesis Summary")
    lines.append("")
    lines.append("| Hypothesis | Status | Effect Size | Key Finding |")
    lines.append("|------------|--------|-------------|-------------|")

    for key in ['smoothing', 'isolation', 'restart', 'quire', 'navigation']:
        if key in results:
            data = results[key]
            effect = list(data.get('effect_sizes', {}).values())[0] if data.get('effect_sizes') else 'N/A'
            interpretation = data.get('interpretation', '')[:60] + '...' if len(data.get('interpretation', '')) > 60 else data.get('interpretation', '')
            lines.append(f"| {data.get('hypothesis', key)} | {data.get('status', 'UNKNOWN')} | {effect} | {interpretation} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Detailed sections
    for key, data in results.items():
        if key in ['metadata', 'buffering_analysis']:
            continue

        lines.append(f"## {data.get('hypothesis', key)}")
        lines.append("")

        if 'observed' in data:
            lines.append("### Observed Metrics")
            lines.append("")
            for k, v in data['observed'].items():
                lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
            lines.append("")

        if 'null_distribution' in data:
            lines.append("### Null Distribution")
            lines.append("")
            for k, v in data['null_distribution'].items():
                lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
            lines.append("")

        if 'percentiles' in data:
            lines.append("### Statistical Results")
            lines.append("")
            for k, v in data['percentiles'].items():
                lines.append(f"- **{k.replace('_', ' ').title()}:** {v}%")
            lines.append("")

        if 'effect_sizes' in data:
            lines.append("### Effect Sizes")
            lines.append("")
            for k, v in data['effect_sizes'].items():
                lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
            lines.append("")

        lines.append(f"**Status:** {data.get('status', 'UNKNOWN')}")
        lines.append("")
        lines.append(f"**Interpretation:** {data.get('interpretation', 'No interpretation available')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Buffering analysis
    if 'buffering_analysis' in results:
        ba = results['buffering_analysis']
        lines.append("## Supplementary: CEI Neighbor Buffering")
        lines.append("")
        lines.append(f"- **High-CEI folios analyzed:** {ba['n_high_cei_analyzed']}")
        lines.append(f"- **Damping cases:** {ba['damping_cases']} ({ba['damping_rate']*100:.1f}%)")
        lines.append(f"- **Amplification cases:** {ba['amplification_cases']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Final verdict
    lines.append("## Verdict")
    lines.append("")

    if supported > rejected and supported >= 2:
        verdict = "PARTIAL STRUCTURAL ORGANIZATION DETECTED"
        explanation = "Multiple hypotheses supported suggest intentional CEI management in codex organization."
    elif rejected > supported:
        verdict = "STRUCTURAL ORGANIZATION NOT DETECTED"
        explanation = "Most hypotheses rejected; codex organization appears random with respect to CEI."
    else:
        verdict = "MIXED EVIDENCE"
        explanation = "Some structural organization detected, but not consistently across all hypotheses."

    lines.append(f"> **{verdict}**")
    lines.append(f"> {explanation}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> **\"OPS-6 is complete. Codex organization has been evaluated against control-engagement and human-factors hypotheses using purely structural evidence. No new control logic or semantic interpretation has been introduced.\"**")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().isoformat()}*")

    return "\n".join(lines)


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("="*70)
    print("OPS-6: PROGRAM LIBRARY TOPOLOGY & CODEX ORGANIZATION")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"Randomizations per test: {N_RANDOMIZATIONS}")

    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)

    # Load data
    print("\nLoading CEI data...")
    folios = load_cei_data()
    ordered = get_ordered_folios(folios)

    print(f"Loaded {len(folios)} folios")
    print(f"Folio order: {ordered[:5]}...{ordered[-5:]}")

    # Run all hypothesis tests
    results = {'metadata': {
        'phase': 'OPS-6',
        'title': 'Codex Structure Analysis',
        'timestamp': datetime.now().isoformat(),
        'n_folios': len(folios),
        'n_randomizations': N_RANDOMIZATIONS
    }}

    results['smoothing'] = test_cei_smoothing(folios, ordered)
    results['isolation'] = test_high_cei_isolation(folios, ordered)
    results['restart'] = test_restart_placement(folios, ordered)
    results['quire'] = test_quire_boundary_interaction(folios, ordered)
    results['navigation'] = test_navigation_topology(folios, ordered)

    # Supplementary analysis
    results['buffering_analysis'] = analyze_cei_buffering(folios, ordered)

    # Generate outputs
    print("\n" + "="*60)
    print("GENERATING OUTPUTS")
    print("="*60)

    # 1. JSON topology metrics
    json_output = {
        'metadata': results['metadata'],
        'cei_jump_distribution': {
            'observed_mean': results['smoothing']['observed']['mean_cei_jump'],
            'observed_max': results['smoothing']['observed']['max_cei_jump'],
            'null_mean': results['smoothing']['null_distribution']['mean_jump_mean'],
            'null_std': results['smoothing']['null_distribution']['mean_jump_std']
        },
        'neighborhood_buffering': {
            'observed_variance': results['smoothing']['observed']['mean_neighborhood_variance'],
            'null_variance': results['smoothing']['null_distribution']['variance_mean'],
            'damping_rate': results['buffering_analysis']['damping_rate']
        },
        'high_cei_isolation': {
            'n_clusters': results['isolation']['observed']['n_clusters'],
            'max_cluster_size': results['isolation']['observed']['max_cluster_size'],
            'mean_neighbor_cei': results['isolation']['observed']['mean_neighbor_cei']
        },
        'restart_placement': {
            'restart_folios': results['restart'].get('restart_folios', []),
            'mean_restart_cei': results['restart']['observed'].get('mean_restart_cei', 0) if 'observed' in results['restart'] else 0,
            'percentile': results['restart']['percentiles'].get('restart_cei_percentile', 'N/A') if 'percentiles' in results['restart'] else 'N/A'
        },
        'navigation': {
            'max_retreat_distance': results['navigation']['observed']['max_retreat_distance'],
            'n_trap_positions': results['navigation']['observed']['n_trap_positions']
        },
        'hypothesis_results': {
            key: data.get('status', 'UNKNOWN')
            for key, data in results.items()
            if key not in ['metadata', 'buffering_analysis']
        }
    }

    json_file = OPS6_DIR / "ops6_topology_metrics.json"
    with open(json_file, 'w') as f:
        json.dump(json_output, f, indent=2)
    print(f"Wrote: {json_file}")

    # 2. Summary CSV
    summary = generate_structural_summary(results)
    csv_file = OPS6_DIR / "ops6_structural_summary.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['hypothesis', 'status', 'effect_size', 'p_value_proxy'])
        writer.writeheader()
        writer.writerows(summary)
    print(f"Wrote: {csv_file}")

    # 3. Markdown report
    report = generate_markdown_report(results, folios, ordered)
    md_file = OPS6_DIR / "ops6_codex_structure_analysis.md"
    with open(md_file, 'w') as f:
        f.write(report)
    print(f"Wrote: {md_file}")

    # Final summary
    print("\n" + "="*70)
    print("OPS-6 SUMMARY")
    print("="*70)

    for key, data in results.items():
        if key in ['metadata', 'buffering_analysis']:
            continue
        print(f"\n{data.get('hypothesis', key)}: {data.get('status', 'UNKNOWN')}")

    print("\n" + "="*70)
    print("OPS-6 is complete. Codex organization has been evaluated against")
    print("control-engagement and human-factors hypotheses using purely")
    print("structural evidence. No new control logic or semantic interpretation")
    print("has been introduced.")
    print("="*70)


if __name__ == "__main__":
    main()
