#!/usr/bin/env python3
"""
Human-Track Ordering vs Program Risk Analysis

Tests whether the manuscript's ordering and sectioning are deliberately
structured to manage operator risk, learning, and recovery.

All system-track structures are LOCKED. This analyzes human-track only:
- folio order
- sectioning
- Currier A/B
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import random
from collections import defaultdict
import math

# Statistical helpers
def mean(vals):
    if not vals:
        return 0
    return sum(vals) / len(vals)

def stdev(vals):
    if len(vals) < 2:
        return 0
    m = mean(vals)
    return math.sqrt(sum((x - m) ** 2 for x in vals) / (len(vals) - 1))

def spearman_rank(x, y):
    """Compute Spearman's rho and approximate p-value."""
    if len(x) != len(y) or len(x) < 3:
        return 0, 1.0

    # Rank both arrays with tie handling
    def rank_data(data):
        n = len(data)
        sorted_pairs = sorted(enumerate(data), key=lambda p: p[1])
        ranks = [0.0] * n

        i = 0
        while i < n:
            j = i
            # Find ties
            while j < n - 1 and sorted_pairs[j+1][1] == sorted_pairs[j][1]:
                j += 1
            # Assign average rank to ties
            avg_rank = (i + j + 2) / 2  # +2 because ranks are 1-based
            for k in range(i, j + 1):
                ranks[sorted_pairs[k][0]] = avg_rank
            i = j + 1
        return ranks

    rx = rank_data(x)
    ry = rank_data(y)

    n = len(x)

    # Compute Pearson correlation of ranks
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n

    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))

    if den_x == 0 or den_y == 0:
        return 0, 1.0

    rho = num / (den_x * den_y)

    # Approximate p-value using t-distribution approximation
    if abs(rho) >= 0.9999:
        p = 0.0001
    else:
        t = rho * math.sqrt((n - 2) / (1 - rho**2))
        # Use normal approximation for large n
        # Two-tailed p-value
        z = abs(t) / math.sqrt(1 + t*t/(n-2)) if n > 10 else abs(t)
        # Approximate using standard normal CDF
        p = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
        p = max(0.0001, min(p, 1.0))

    return rho, p

def kendall_tau(x, y):
    """Compute Kendall's tau-b."""
    if len(x) != len(y) or len(x) < 2:
        return 0, 1.0

    n = len(x)
    concordant = 0
    discordant = 0

    for i in range(n):
        for j in range(i + 1, n):
            xi, xj = x[i], x[j]
            yi, yj = y[i], y[j]

            if (xi < xj and yi < yj) or (xi > xj and yi > yj):
                concordant += 1
            elif (xi < xj and yi > yj) or (xi > xj and yi < yj):
                discordant += 1

    total = concordant + discordant
    if total == 0:
        return 0, 1.0

    tau = (concordant - discordant) / total

    # Approximate p-value using normal approximation
    var = (2 * (2 * n + 5)) / (9 * n * (n - 1))
    if var > 0:
        z = tau / math.sqrt(var)
        # Use standard normal CDF approximation
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        p = max(0.0001, min(p, 1.0))
    else:
        p = 1.0

    return tau, p

def cliffs_delta(group1, group2):
    """Compute Cliff's delta effect size."""
    if not group1 or not group2:
        return 0

    n1, n2 = len(group1), len(group2)
    dominance = 0

    for x in group1:
        for y in group2:
            if x > y:
                dominance += 1
            elif x < y:
                dominance -= 1

    return dominance / (n1 * n2)

def permutation_test(observed, null_samples, alternative='two-sided'):
    """Compute p-value from permutation distribution."""
    if not null_samples:
        return 1.0

    if alternative == 'greater':
        count = sum(1 for s in null_samples if s >= observed)
    elif alternative == 'less':
        count = sum(1 for s in null_samples if s <= observed)
    else:
        count = sum(1 for s in null_samples if abs(s) >= abs(observed))

    return count / len(null_samples)

def mann_whitney_u(group1, group2):
    """Compute Mann-Whitney U test statistic and approximate p-value."""
    if not group1 or not group2:
        return 0, 1.0

    n1, n2 = len(group1), len(group2)

    # Combine and rank
    combined = [(v, 0, i) for i, v in enumerate(group1)]
    combined += [(v, 1, i) for i, v in enumerate(group2)]
    combined.sort()

    ranks = {}
    for rank, (val, group, idx) in enumerate(combined, 1):
        ranks[(group, idx)] = rank

    R1 = sum(ranks[(0, i)] for i in range(n1))
    U1 = R1 - n1 * (n1 + 1) / 2
    U2 = n1 * n2 - U1
    U = min(U1, U2)

    # Normal approximation for p-value
    mu = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    if sigma == 0:
        return U, 1.0

    z = (U - mu) / sigma
    # Two-tailed approximation
    p = 2 * (1 - min(0.9999, abs(z) / (abs(z) + 3)))

    return U, p


@dataclass
class ProgramData:
    """Program (folio) with all metrics."""
    folio_id: str
    folio_order: int
    currier: str
    section: str

    # Risk metrics
    hazard_density: float = 0.0
    near_miss_count: int = 0
    hazard_adjacency_count: int = 0

    # LINK metrics
    link_density: float = 0.0
    max_consecutive_link: int = 0

    # Recovery metrics
    recovery_ops_count: int = 0
    reset_present: bool = False

    # Other metrics
    kernel_contact_ratio: float = 0.0
    intervention_frequency: float = 0.0
    cycle_regularity: float = 0.0
    total_length: int = 0

    # Derived role classifications
    stability_class: str = "MODERATE"
    waiting_class: str = "LINK_MODERATE"
    is_restart_capable: bool = False
    is_high_intervention: bool = False
    is_extended: bool = False

    def risk_score(self) -> float:
        """Composite risk score (higher = more risky)."""
        # Normalize components
        hazard_contrib = self.hazard_density * 2  # 0-1.5 range typically
        near_miss_norm = min(self.near_miss_count / 50, 1.0)  # Normalize to 0-1
        link_penalty = 1 - self.link_density  # Low LINK = higher risk

        return hazard_contrib + near_miss_norm + link_penalty * 0.5


def extract_folio_number(folio_id: str) -> Tuple[int, str]:
    """Extract numeric part and suffix from folio ID for ordering."""
    match = re.match(r'f(\d+)([rv]?\d*)', folio_id)
    if match:
        num = int(match.group(1))
        suffix = match.group(2) or ''
        return (num, suffix)
    return (999, folio_id)


def load_data():
    """Load all required data files."""

    # Load control signatures
    with open('control_signatures.json', 'r', encoding='utf-8') as f:
        signatures = json.load(f)['signatures']

    # Load folio database for Currier/section info
    with open('folio_feature_database.json', 'r', encoding='utf-8') as f:
        folio_db = json.load(f)

    # Build Currier and section lookup
    currier_lookup = {}
    section_lookup = {}

    for folio_id, data in folio_db.get('currier_a', {}).items():
        currier_lookup[folio_id] = 'A'
        section_lookup[folio_id] = data.get('section', 'unknown')

    for folio_id, data in folio_db.get('currier_b', {}).items():
        currier_lookup[folio_id] = 'B'
        section_lookup[folio_id] = data.get('section', 'unknown')

    # Known restart-capable programs
    restart_capable = {'f50v', 'f57r', 'f82v'}

    # High-intervention programs
    high_intervention = {
        'f33r', 'f33v', 'f39r', 'f55r', 'f66v',
        'f86v4', 'f94v', 'f95r2', 'f95v2', 'f116r'
    }

    # Extended programs (length > 800)
    extended_programs = {
        'f66r', 'f75r', 'f75v', 'f76r', 'f76v', 'f77r', 'f77v',
        'f78r', 'f78v', 'f79r', 'f79v', 'f80r', 'f80v', 'f81r',
        'f81v', 'f82r', 'f82v', 'f83r', 'f83v', 'f84r', 'f84v',
        'f86v6', 'f103r', 'f103v', 'f104r', 'f104v', 'f105v',
        'f106r', 'f106v', 'f107r', 'f107v', 'f108r', 'f108v',
        'f111r', 'f111v', 'f112r', 'f112v', 'f113r', 'f113v',
        'f114r', 'f115r', 'f115v', 'f116r'
    }

    # Build program list
    programs = []

    # Sort folios by their natural order
    folio_ids = sorted(signatures.keys(), key=extract_folio_number)

    for order, folio_id in enumerate(folio_ids):
        sig = signatures[folio_id]

        # Classify stability
        link_d = sig.get('link_density', 0.4)
        hazard_d = sig.get('hazard_density', 0.5)
        near_miss = sig.get('near_miss_count', 20)

        if link_d > 0.45 and hazard_d < 0.52:
            stability = 'ULTRA_CONSERVATIVE'
        elif link_d > 0.40 and hazard_d < 0.56:
            stability = 'CONSERVATIVE'
        elif hazard_d > 0.65 or near_miss > 35:
            stability = 'AGGRESSIVE'
        else:
            stability = 'MODERATE'

        # Classify waiting
        max_link = sig.get('max_consecutive_link', 5)
        if link_d > 0.45 and max_link >= 6:
            waiting = 'LINK_HEAVY_EXTENDED'
        elif link_d > 0.40:
            waiting = 'LINK_HEAVY'
        elif link_d < 0.30:
            waiting = 'LINK_SPARSE'
        else:
            waiting = 'LINK_MODERATE'

        program = ProgramData(
            folio_id=folio_id,
            folio_order=order,
            currier=currier_lookup.get(folio_id, 'U'),
            section=section_lookup.get(folio_id, 'unknown'),
            hazard_density=hazard_d,
            near_miss_count=near_miss,
            hazard_adjacency_count=sig.get('hazard_adjacency_count', 0),
            link_density=link_d,
            max_consecutive_link=max_link,
            recovery_ops_count=sig.get('recovery_ops_count', 0),
            reset_present=sig.get('reset_present', False),
            kernel_contact_ratio=sig.get('kernel_contact_ratio', 0.6),
            intervention_frequency=sig.get('intervention_frequency', 6),
            cycle_regularity=sig.get('cycle_regularity', 3),
            total_length=sig.get('total_length', 500),
            stability_class=stability,
            waiting_class=waiting,
            is_restart_capable=folio_id in restart_capable,
            is_high_intervention=folio_id in high_intervention,
            is_extended=folio_id in extended_programs
        )
        programs.append(program)

    return programs


def test_1_order_vs_risk_gradient(programs: List[ProgramData], n_permutations=10000):
    """TEST 1: Correlate folio order with risk metrics."""

    print("\n" + "="*60)
    print("TEST 1: ORDER vs RISK GRADIENT")
    print("="*60)

    results = {
        'test_name': 'Order vs Risk Gradient',
        'correlations': {},
        'permutation_tests': {},
        'monotonicity': {},
        'verdict': None
    }

    orders = [p.folio_order for p in programs]

    # Metrics to test
    metrics = {
        'hazard_density': [p.hazard_density for p in programs],
        'near_miss_count': [p.near_miss_count for p in programs],
        'risk_score': [p.risk_score() for p in programs],
        'link_density': [p.link_density for p in programs],
        'recovery_ops': [p.recovery_ops_count for p in programs]
    }

    print("\n--- Spearman Correlations with Folio Order ---")

    for metric_name, values in metrics.items():
        rho, p_spearman = spearman_rank(orders, values)
        tau, p_kendall = kendall_tau(orders, values)

        results['correlations'][metric_name] = {
            'spearman_rho': rho,
            'spearman_p': p_spearman,
            'kendall_tau': tau,
            'kendall_p': p_kendall
        }

        print(f"\n{metric_name}:")
        print(f"  Spearman rho = {rho:.4f}, p = {p_spearman:.4f}")
        print(f"  Kendall tau  = {tau:.4f}, p = {p_kendall:.4f}")

    # Permutation test for risk score gradient
    print("\n--- Permutation Test for Risk Gradient ---")

    risk_scores = [p.risk_score() for p in programs]
    observed_rho, _ = spearman_rank(orders, risk_scores)

    null_rhos = []
    for _ in range(n_permutations):
        shuffled = risk_scores.copy()
        random.shuffle(shuffled)
        null_rho, _ = spearman_rank(orders, shuffled)
        null_rhos.append(null_rho)

    perm_p = permutation_test(observed_rho, null_rhos)
    results['permutation_tests']['risk_score'] = {
        'observed_rho': observed_rho,
        'null_mean': mean(null_rhos),
        'null_std': stdev(null_rhos),
        'p_value': perm_p,
        'percentile': sum(1 for r in null_rhos if r < observed_rho) / len(null_rhos) * 100
    }

    print(f"Observed risk-order rho: {observed_rho:.4f}")
    print(f"Null distribution: mean={mean(null_rhos):.4f}, std={stdev(null_rhos):.4f}")
    print(f"Permutation p-value: {perm_p:.4f}")

    # Test for staged drift (divide into thirds)
    print("\n--- Staged Risk Analysis (Thirds) ---")

    n = len(programs)
    third = n // 3

    first_third = programs[:third]
    middle_third = programs[third:2*third]
    last_third = programs[2*third:]

    first_risk = mean([p.risk_score() for p in first_third])
    middle_risk = mean([p.risk_score() for p in middle_third])
    last_risk = mean([p.risk_score() for p in last_third])

    results['monotonicity']['thirds'] = {
        'first_third_risk': first_risk,
        'middle_third_risk': middle_risk,
        'last_third_risk': last_risk,
        'is_monotonic_increase': first_risk < middle_risk < last_risk,
        'is_monotonic_decrease': first_risk > middle_risk > last_risk
    }

    print(f"First third mean risk:  {first_risk:.4f}")
    print(f"Middle third mean risk: {middle_risk:.4f}")
    print(f"Last third mean risk:   {last_risk:.4f}")

    if first_risk < middle_risk < last_risk:
        print("-> MONOTONIC INCREASE detected")
    elif first_risk > middle_risk > last_risk:
        print("-> MONOTONIC DECREASE detected")
    else:
        print("-> NO monotonic trend")

    # Verdict - use permutation test as primary evidence
    perm_significant = perm_p < 0.01  # Strong permutation evidence
    monotonic = results['monotonicity']['thirds']['is_monotonic_increase'] or results['monotonicity']['thirds']['is_monotonic_decrease']

    any_corr_significant = any(
        abs(r['spearman_rho']) > 0.25 and r['spearman_p'] < 0.05
        for r in results['correlations'].values()
    )

    if perm_significant and monotonic:
        results['verdict'] = 'SIGNAL: Non-random risk ordering with monotonic gradient'
        print("\n** VERDICT: SIGNAL - Non-random correlation with folio order **")
    elif perm_significant or any_corr_significant:
        results['verdict'] = 'WEAK: Some non-random ordering detected'
        print("\n** VERDICT: WEAK - Some correlation with folio order **")
    else:
        results['verdict'] = 'NULL: No significant risk gradient'
        print("\n** VERDICT: NULL - Risk metrics independent of ordering **")

    return results


def test_2_boundary_clustering(programs: List[ProgramData], n_permutations=10000):
    """TEST 2: Test clustering of special programs near boundaries."""

    print("\n" + "="*60)
    print("TEST 2: CLUSTERING AROUND BOUNDARIES")
    print("="*60)

    results = {
        'test_name': 'Boundary Clustering',
        'boundaries': {},
        'clustering_tests': {},
        'verdict': None
    }

    n = len(programs)

    # Identify boundaries
    section_boundaries = []
    currier_transitions = []

    for i in range(1, n):
        if programs[i].section != programs[i-1].section:
            section_boundaries.append(i)
        if programs[i].currier != programs[i-1].currier:
            currier_transitions.append(i)

    # Combined boundaries
    all_boundaries = sorted(set(section_boundaries + currier_transitions))

    results['boundaries'] = {
        'section_boundaries': section_boundaries,
        'currier_transitions': currier_transitions,
        'all_boundaries': all_boundaries,
        'n_boundaries': len(all_boundaries)
    }

    print(f"\nIdentified {len(section_boundaries)} section boundaries")
    print(f"Identified {len(currier_transitions)} Currier A/B transitions")
    print(f"Total unique boundaries: {len(all_boundaries)}")

    # Distance to nearest boundary
    def distance_to_boundary(idx, boundaries):
        if not boundaries:
            return n  # Max distance
        return min(abs(idx - b) for b in boundaries)

    # Test special program types
    restart_positions = [p.folio_order for p in programs if p.is_restart_capable]
    high_link_positions = [p.folio_order for p in programs if p.waiting_class in ['LINK_HEAVY', 'LINK_HEAVY_EXTENDED']]
    conservative_positions = [p.folio_order for p in programs if p.stability_class in ['CONSERVATIVE', 'ULTRA_CONSERVATIVE']]
    aggressive_positions = [p.folio_order for p in programs if p.stability_class == 'AGGRESSIVE']

    program_types = {
        'restart_capable': restart_positions,
        'high_link': high_link_positions,
        'conservative': conservative_positions,
        'aggressive': aggressive_positions
    }

    print("\n--- Distance to Boundaries Analysis ---")

    for prog_type, positions in program_types.items():
        if not positions or not all_boundaries:
            continue

        # Observed mean distance
        observed_distances = [distance_to_boundary(p, all_boundaries) for p in positions]
        observed_mean = mean(observed_distances)

        # Null distribution (random positions)
        null_means = []
        for _ in range(n_permutations):
            random_positions = random.sample(range(n), len(positions))
            null_distances = [distance_to_boundary(p, all_boundaries) for p in random_positions]
            null_means.append(mean(null_distances))

        perm_p = permutation_test(observed_mean, null_means, 'less')  # Test if closer than random
        percentile = sum(1 for nm in null_means if nm > observed_mean) / len(null_means) * 100

        results['clustering_tests'][prog_type] = {
            'n_programs': len(positions),
            'observed_mean_distance': observed_mean,
            'null_mean': mean(null_means),
            'null_std': stdev(null_means),
            'p_value': perm_p,
            'percentile': percentile,
            'is_clustered': perm_p < 0.05
        }

        print(f"\n{prog_type} ({len(positions)} programs):")
        print(f"  Mean distance to boundary: {observed_mean:.2f}")
        print(f"  Null expectation: {mean(null_means):.2f} +/- {stdev(null_means):.2f}")
        print(f"  Percentile (closer than): {percentile:.1f}%")
        print(f"  p-value (clustering): {perm_p:.4f}")

        if perm_p < 0.05:
            print(f"  -> SIGNIFICANT clustering near boundaries")

    # Verdict
    n_clustered = sum(1 for t in results['clustering_tests'].values() if t.get('is_clustered', False))

    if n_clustered >= 2:
        results['verdict'] = 'SIGNAL: Multiple program types cluster near boundaries'
        print("\n** VERDICT: SIGNAL - Systematic boundary clustering detected **")
    elif n_clustered == 1:
        results['verdict'] = 'WEAK: One program type clusters near boundaries'
        print("\n** VERDICT: WEAK - Partial boundary clustering **")
    else:
        results['verdict'] = 'NULL: No boundary clustering detected'
        print("\n** VERDICT: NULL - Programs randomly distributed relative to boundaries **")

    return results


def test_3_currier_role_asymmetry(programs: List[ProgramData]):
    """TEST 3: Compare role distributions between Currier A and B."""

    print("\n" + "="*60)
    print("TEST 3: CURRIER A/B vs ROLE ASYMMETRY")
    print("="*60)

    results = {
        'test_name': 'Currier Role Asymmetry',
        'counts': {},
        'metric_comparisons': {},
        'role_distributions': {},
        'verdict': None
    }

    currier_a = [p for p in programs if p.currier == 'A']
    currier_b = [p for p in programs if p.currier == 'B']

    results['counts'] = {
        'currier_a': len(currier_a),
        'currier_b': len(currier_b),
        'unknown': len([p for p in programs if p.currier not in ['A', 'B']])
    }

    print(f"\nCurrier A: {len(currier_a)} programs")
    print(f"Currier B: {len(currier_b)} programs")

    if not currier_a or not currier_b:
        print("Insufficient data for Currier A/B comparison")
        print("Note: Control signatures may only cover one Currier type")
        results['verdict'] = 'INSUFFICIENT DATA: All programs are Currier B'
        results['note'] = 'Control signatures cover only Currier B folios'
        return results

    # Compare metric distributions
    metrics_to_compare = [
        ('hazard_density', lambda p: p.hazard_density),
        ('link_density', lambda p: p.link_density),
        ('near_miss_count', lambda p: p.near_miss_count),
        ('recovery_ops', lambda p: p.recovery_ops_count),
        ('risk_score', lambda p: p.risk_score()),
        ('intervention_frequency', lambda p: p.intervention_frequency)
    ]

    print("\n--- Metric Comparisons ---")

    for metric_name, extractor in metrics_to_compare:
        a_vals = [extractor(p) for p in currier_a]
        b_vals = [extractor(p) for p in currier_b]

        a_mean, a_std = mean(a_vals), stdev(a_vals)
        b_mean, b_std = mean(b_vals), stdev(b_vals)

        U, p_val = mann_whitney_u(a_vals, b_vals)
        delta = cliffs_delta(a_vals, b_vals)

        results['metric_comparisons'][metric_name] = {
            'a_mean': a_mean,
            'a_std': a_std,
            'b_mean': b_mean,
            'b_std': b_std,
            'mann_whitney_U': U,
            'p_value': p_val,
            'cliffs_delta': delta,
            'significant': p_val < 0.05
        }

        print(f"\n{metric_name}:")
        print(f"  A: {a_mean:.4f} +/- {a_std:.4f}")
        print(f"  B: {b_mean:.4f} +/- {b_std:.4f}")
        print(f"  Mann-Whitney p = {p_val:.4f}, Cliff's delta = {delta:.3f}")

        if p_val < 0.05:
            print(f"  -> SIGNIFICANT difference")

    # Compare role distributions
    print("\n--- Role Distribution Comparison ---")

    for role_attr in ['stability_class', 'waiting_class']:
        a_roles = defaultdict(int)
        b_roles = defaultdict(int)

        for p in currier_a:
            a_roles[getattr(p, role_attr)] += 1
        for p in currier_b:
            b_roles[getattr(p, role_attr)] += 1

        all_roles = sorted(set(a_roles.keys()) | set(b_roles.keys()))

        results['role_distributions'][role_attr] = {
            'a': dict(a_roles),
            'b': dict(b_roles)
        }

        print(f"\n{role_attr}:")
        print(f"  {'Role':<25} {'A (%)':<12} {'B (%)':<12}")
        print(f"  {'-'*25} {'-'*12} {'-'*12}")

        for role in all_roles:
            a_pct = a_roles[role] / len(currier_a) * 100
            b_pct = b_roles[role] / len(currier_b) * 100
            print(f"  {role:<25} {a_pct:>6.1f}%      {b_pct:>6.1f}%")

    # Special markers comparison
    print("\n--- Special Marker Comparison ---")

    a_restart = sum(1 for p in currier_a if p.is_restart_capable)
    b_restart = sum(1 for p in currier_b if p.is_restart_capable)
    a_extended = sum(1 for p in currier_a if p.is_extended)
    b_extended = sum(1 for p in currier_b if p.is_extended)
    a_high_int = sum(1 for p in currier_a if p.is_high_intervention)
    b_high_int = sum(1 for p in currier_b if p.is_high_intervention)

    results['role_distributions']['special_markers'] = {
        'restart_a': a_restart, 'restart_b': b_restart,
        'extended_a': a_extended, 'extended_b': b_extended,
        'high_intervention_a': a_high_int, 'high_intervention_b': b_high_int
    }

    print(f"  Restart-capable: A={a_restart}, B={b_restart}")
    print(f"  Extended:        A={a_extended}, B={b_extended}")
    print(f"  High-intervention: A={a_high_int}, B={b_high_int}")

    # Verdict
    n_significant = sum(1 for m in results['metric_comparisons'].values() if m.get('significant', False))

    interpretation_notes = []

    # Check if differences align with "operator documentation" hypothesis
    a_risk = mean([p.risk_score() for p in currier_a])
    b_risk = mean([p.risk_score() for p in currier_b])

    if a_risk < b_risk:
        interpretation_notes.append("A is less risky (may be introductory)")
    elif a_risk > b_risk:
        interpretation_notes.append("A is more risky (may be advanced)")

    results['interpretation'] = {
        'a_mean_risk': a_risk,
        'b_mean_risk': b_risk,
        'notes': interpretation_notes
    }

    if n_significant >= 3:
        results['verdict'] = 'SIGNAL: Strong systematic differences between A and B'
        print("\n** VERDICT: SIGNAL - Currier A/B show different operational profiles **")
    elif n_significant >= 1:
        results['verdict'] = 'WEAK: Some differences between A and B'
        print("\n** VERDICT: WEAK - Partial differences between A and B **")
    else:
        results['verdict'] = 'NULL: A and B have similar role distributions'
        print("\n** VERDICT: NULL - No significant A/B asymmetry **")

    return results


def test_4_local_neighborhood_safety(programs: List[ProgramData], k=2, n_permutations=10000):
    """TEST 4: Analyze local neighborhood for risk buffering."""

    print("\n" + "="*60)
    print("TEST 4: LOCAL NEIGHBORHOOD SAFETY")
    print("="*60)

    results = {
        'test_name': 'Local Neighborhood Safety',
        'k_neighbors': k,
        'jump_analysis': {},
        'buffering_analysis': {},
        'verdict': None
    }

    n = len(programs)

    # Calculate risk jumps between adjacent folios
    risk_scores = [p.risk_score() for p in programs]
    risk_jumps = [abs(risk_scores[i] - risk_scores[i-1]) for i in range(1, n)]

    mean_jump = mean(risk_jumps)
    std_jump = stdev(risk_jumps)
    max_jump = max(risk_jumps) if risk_jumps else 0

    print(f"\n--- Risk Jump Analysis ---")
    print(f"Mean risk jump between adjacent folios: {mean_jump:.4f}")
    print(f"Std of risk jumps: {std_jump:.4f}")
    print(f"Maximum jump: {max_jump:.4f}")

    # Compare to null (shuffled order)
    null_mean_jumps = []
    for _ in range(n_permutations):
        shuffled = risk_scores.copy()
        random.shuffle(shuffled)
        null_jumps = [abs(shuffled[i] - shuffled[i-1]) for i in range(1, n)]
        null_mean_jumps.append(mean(null_jumps))

    perm_p = permutation_test(mean_jump, null_mean_jumps, 'less')

    results['jump_analysis'] = {
        'observed_mean_jump': mean_jump,
        'observed_std_jump': std_jump,
        'observed_max_jump': max_jump,
        'null_mean': mean(null_mean_jumps),
        'null_std': stdev(null_mean_jumps),
        'p_value': perm_p,
        'percentile': sum(1 for nm in null_mean_jumps if nm > mean_jump) / len(null_mean_jumps) * 100
    }

    print(f"\nNull expectation: {mean(null_mean_jumps):.4f} +/- {stdev(null_mean_jumps):.4f}")
    print(f"Permutation p-value (lower than null): {perm_p:.4f}")
    print(f"Percentile (smoother than): {results['jump_analysis']['percentile']:.1f}%")

    if perm_p < 0.05:
        print("-> SIGNIFICANT: Ordering minimizes risk jumps")

    # Aggressive program buffering analysis
    print(f"\n--- Aggressive Program Buffering (k={k}) ---")

    aggressive_indices = [i for i, p in enumerate(programs) if p.stability_class == 'AGGRESSIVE']
    conservative_indices = [i for i, p in enumerate(programs) if p.stability_class in ['CONSERVATIVE', 'ULTRA_CONSERVATIVE']]

    # For each aggressive program, check if neighbors are more conservative
    buffered_count = 0
    total_aggressive = len(aggressive_indices)

    neighbor_risks = []
    for idx in aggressive_indices:
        neighbors = []
        for offset in range(-k, k+1):
            if offset == 0:
                continue
            ni = idx + offset
            if 0 <= ni < n:
                neighbors.append(risk_scores[ni])

        if neighbors:
            neighbor_risk = mean(neighbors)
            own_risk = risk_scores[idx]
            neighbor_risks.append(neighbor_risk)

            if neighbor_risk < own_risk:
                buffered_count += 1

    buffering_rate = buffered_count / total_aggressive if total_aggressive > 0 else 0

    # Null model: random positions
    null_buffering_rates = []
    for _ in range(n_permutations):
        shuffled_risks = risk_scores.copy()
        random.shuffle(shuffled_risks)

        null_buffered = 0
        for idx in aggressive_indices:
            neighbors = []
            for offset in range(-k, k+1):
                if offset == 0:
                    continue
                ni = idx + offset
                if 0 <= ni < n:
                    neighbors.append(shuffled_risks[ni])

            if neighbors:
                if mean(neighbors) < shuffled_risks[idx]:
                    null_buffered += 1

        null_buffering_rates.append(null_buffered / total_aggressive if total_aggressive > 0 else 0)

    buffer_p = permutation_test(buffering_rate, null_buffering_rates, 'greater')

    results['buffering_analysis'] = {
        'n_aggressive': total_aggressive,
        'n_buffered': buffered_count,
        'buffering_rate': buffering_rate,
        'null_mean': mean(null_buffering_rates),
        'null_std': stdev(null_buffering_rates),
        'p_value': buffer_p,
        'percentile': sum(1 for nr in null_buffering_rates if nr < buffering_rate) / len(null_buffering_rates) * 100
    }

    print(f"Aggressive programs: {total_aggressive}")
    print(f"Buffered by safer neighbors: {buffered_count} ({buffering_rate*100:.1f}%)")
    print(f"Null expectation: {mean(null_buffering_rates)*100:.1f}% +/- {stdev(null_buffering_rates)*100:.1f}%")
    print(f"Percentile (more buffered than): {results['buffering_analysis']['percentile']:.1f}%")
    print(f"p-value (buffering): {buffer_p:.4f}")

    if buffer_p < 0.05:
        print("-> SIGNIFICANT: Aggressive programs systematically buffered")

    # Verdict
    jump_signal = results['jump_analysis']['p_value'] < 0.05
    buffer_signal = results['buffering_analysis']['p_value'] < 0.05

    if jump_signal and buffer_signal:
        results['verdict'] = 'SIGNAL: Risk-aware local ordering with buffering'
        print("\n** VERDICT: SIGNAL - Both smooth transitions and buffering detected **")
    elif jump_signal or buffer_signal:
        results['verdict'] = 'WEAK: Partial local safety structuring'
        print("\n** VERDICT: WEAK - Partial local safety patterns **")
    else:
        results['verdict'] = 'NULL: No local safety structuring'
        print("\n** VERDICT: NULL - Local ordering appears random **")

    return results


def test_5_restart_placement(programs: List[ProgramData], n_permutations=10000):
    """TEST 5: Analyze placement of restart-capable programs."""

    print("\n" + "="*60)
    print("TEST 5: RESTART PROGRAM PLACEMENT")
    print("="*60)

    results = {
        'test_name': 'Restart Program Placement',
        'restart_programs': {},
        'placement_tests': {},
        'verdict': None
    }

    n = len(programs)
    restart_indices = [i for i, p in enumerate(programs) if p.is_restart_capable]
    restart_programs = [programs[i] for i in restart_indices]

    results['restart_programs'] = {
        'count': len(restart_programs),
        'folios': [p.folio_id for p in restart_programs],
        'positions': restart_indices,
        'position_percentiles': [i/n*100 for i in restart_indices]
    }

    print(f"\nRestart-capable programs: {len(restart_programs)}")
    for p in restart_programs:
        pos_pct = restart_indices[restart_programs.index(p)] / n * 100
        print(f"  {p.folio_id}: position {restart_indices[restart_programs.index(p)]}/{n} ({pos_pct:.1f}%)")

    if len(restart_indices) < 2:
        print("\nInsufficient restart programs for statistical analysis")
        results['verdict'] = 'INSUFFICIENT DATA'
        return results

    # Test 1: Are restart programs at section starts?
    section_starts = [0]  # First folio is always a section start
    for i in range(1, n):
        if programs[i].section != programs[i-1].section:
            section_starts.append(i)

    restarts_at_start = sum(1 for i in restart_indices if i in section_starts or i-1 in section_starts)

    # Null: random positions
    null_at_starts = []
    for _ in range(n_permutations):
        random_positions = random.sample(range(n), len(restart_indices))
        null_count = sum(1 for i in random_positions if i in section_starts or i-1 in section_starts)
        null_at_starts.append(null_count)

    p_section = permutation_test(restarts_at_start, null_at_starts, 'greater')

    results['placement_tests']['section_start_alignment'] = {
        'observed': restarts_at_start,
        'null_mean': mean(null_at_starts),
        'null_std': stdev(null_at_starts),
        'p_value': p_section,
        'significant': p_section < 0.05
    }

    print(f"\n--- Section Start Alignment ---")
    print(f"Restart programs near section starts: {restarts_at_start}/{len(restart_indices)}")
    print(f"Null expectation: {mean(null_at_starts):.2f} +/- {stdev(null_at_starts):.2f}")
    print(f"p-value: {p_section:.4f}")

    # Test 2: Are restart programs placed after high-risk clusters?
    risk_scores = [p.risk_score() for p in programs]

    # High-risk zone = top 25% by risk
    risk_threshold = sorted(risk_scores, reverse=True)[len(risk_scores)//4]
    high_risk_zones = [i for i, r in enumerate(risk_scores) if r >= risk_threshold]

    # Count restarts that follow high-risk zones (within 3 positions)
    restarts_after_risk = 0
    for ri in restart_indices:
        # Check if there's a high-risk program in positions ri-3 to ri-1
        for offset in range(1, 4):
            if ri - offset >= 0 and ri - offset in high_risk_zones:
                restarts_after_risk += 1
                break

    # Null model
    null_after_risk = []
    for _ in range(n_permutations):
        random_positions = sorted(random.sample(range(n), len(restart_indices)))
        null_count = 0
        for ri in random_positions:
            for offset in range(1, 4):
                if ri - offset >= 0 and ri - offset in high_risk_zones:
                    null_count += 1
                    break
        null_after_risk.append(null_count)

    p_risk = permutation_test(restarts_after_risk, null_after_risk, 'greater')

    results['placement_tests']['high_risk_cluster_following'] = {
        'observed': restarts_after_risk,
        'null_mean': mean(null_after_risk),
        'null_std': stdev(null_after_risk),
        'p_value': p_risk,
        'significant': p_risk < 0.05
    }

    print(f"\n--- High-Risk Cluster Following ---")
    print(f"Restart programs following high-risk zones: {restarts_after_risk}/{len(restart_indices)}")
    print(f"Null expectation: {mean(null_after_risk):.2f} +/- {stdev(null_after_risk):.2f}")
    print(f"p-value: {p_risk:.4f}")

    # Test 3: Spacing regularity
    if len(restart_indices) >= 2:
        spacings = [restart_indices[i+1] - restart_indices[i] for i in range(len(restart_indices)-1)]
        spacing_cv = stdev(spacings) / mean(spacings) if mean(spacings) > 0 else float('inf')

        # Null: random spacings
        null_cvs = []
        for _ in range(n_permutations):
            random_positions = sorted(random.sample(range(n), len(restart_indices)))
            null_spacings = [random_positions[i+1] - random_positions[i] for i in range(len(random_positions)-1)]
            if mean(null_spacings) > 0:
                null_cvs.append(stdev(null_spacings) / mean(null_spacings))

        p_spacing = permutation_test(spacing_cv, null_cvs, 'less')  # Lower CV = more regular

        results['placement_tests']['spacing_regularity'] = {
            'spacings': spacings,
            'mean_spacing': mean(spacings),
            'coefficient_of_variation': spacing_cv,
            'null_mean_cv': mean(null_cvs) if null_cvs else None,
            'p_value': p_spacing,
            'significant': p_spacing < 0.05
        }

        print(f"\n--- Spacing Regularity ---")
        print(f"Spacings: {spacings}")
        print(f"Coefficient of variation: {spacing_cv:.3f}")
        print(f"Null CV: {mean(null_cvs):.3f} +/- {stdev(null_cvs):.3f}")
        print(f"p-value (more regular than random): {p_spacing:.4f}")

    # Verdict
    n_significant = sum(1 for t in results['placement_tests'].values() if t.get('significant', False))

    if n_significant >= 2:
        results['verdict'] = 'SIGNAL: Restart programs strategically placed'
        print("\n** VERDICT: SIGNAL - Non-random restart program placement **")
    elif n_significant == 1:
        results['verdict'] = 'WEAK: Partial restart placement structure'
        print("\n** VERDICT: WEAK - Some structure in restart placement **")
    else:
        results['verdict'] = 'NULL: Restart programs randomly placed'
        print("\n** VERDICT: NULL - Restart placement appears random **")

    return results


def generate_reports(test_results: Dict):
    """Generate all output markdown files."""

    # 1. human_track_ordering_vs_risk.md
    with open('human_track_ordering_vs_risk.md', 'w', encoding='utf-8') as f:
        f.write("# Human-Track Ordering vs Risk Analysis\n\n")
        f.write("> Structural analysis of folio ordering relative to program risk metrics\n\n")
        f.write("---\n\n")

        t1 = test_results['test_1']
        f.write("## TEST 1: Order vs Risk Gradient\n\n")
        f.write(f"**Verdict:** {t1['verdict']}\n\n")

        f.write("### Correlations with Folio Order\n\n")
        f.write("| Metric | Spearman rho | p-value | Kendall tau | p-value |\n")
        f.write("|--------|--------------|---------|-------------|----------|\n")
        for metric, vals in t1['correlations'].items():
            f.write(f"| {metric} | {vals['spearman_rho']:.4f} | {vals['spearman_p']:.4f} | {vals['kendall_tau']:.4f} | {vals['kendall_p']:.4f} |\n")

        f.write("\n### Permutation Test\n\n")
        perm = t1['permutation_tests']['risk_score']
        f.write(f"- Observed risk-order correlation: rho = {perm['observed_rho']:.4f}\n")
        f.write(f"- Null distribution: mean = {perm['null_mean']:.4f}, std = {perm['null_std']:.4f}\n")
        f.write(f"- Permutation p-value: {perm['p_value']:.4f}\n")
        f.write(f"- Percentile: {perm['percentile']:.1f}%\n")

        f.write("\n### Staged Risk (Thirds)\n\n")
        thirds = t1['monotonicity']['thirds']
        f.write(f"| Segment | Mean Risk Score |\n")
        f.write(f"|---------|----------------|\n")
        f.write(f"| First third | {thirds['first_third_risk']:.4f} |\n")
        f.write(f"| Middle third | {thirds['middle_third_risk']:.4f} |\n")
        f.write(f"| Last third | {thirds['last_third_risk']:.4f} |\n")

        if thirds['is_monotonic_increase']:
            f.write("\n**Pattern:** MONOTONIC INCREASE\n")
        elif thirds['is_monotonic_decrease']:
            f.write("\n**Pattern:** MONOTONIC DECREASE\n")
        else:
            f.write("\n**Pattern:** NO MONOTONIC TREND\n")

    # 2. boundary_clustering_analysis.md
    with open('boundary_clustering_analysis.md', 'w', encoding='utf-8') as f:
        f.write("# Boundary Clustering Analysis\n\n")
        f.write("> Testing whether special programs cluster near section/Currier boundaries\n\n")
        f.write("---\n\n")

        t2 = test_results['test_2']
        f.write(f"**Verdict:** {t2['verdict']}\n\n")

        f.write("## Identified Boundaries\n\n")
        f.write(f"- Section boundaries: {len(t2['boundaries']['section_boundaries'])}\n")
        f.write(f"- Currier transitions: {len(t2['boundaries']['currier_transitions'])}\n")
        f.write(f"- Total unique: {t2['boundaries']['n_boundaries']}\n\n")

        f.write("## Clustering Tests\n\n")
        f.write("| Program Type | N | Observed Mean Dist | Null Mean | p-value | Clustered? |\n")
        f.write("|--------------|---|-------------------|-----------|---------|------------|\n")
        for ptype, vals in t2['clustering_tests'].items():
            clustered = "YES" if vals.get('is_clustered', False) else "NO"
            f.write(f"| {ptype} | {vals['n_programs']} | {vals['observed_mean_distance']:.2f} | {vals['null_mean']:.2f} | {vals['p_value']:.4f} | {clustered} |\n")

    # 3. Currier_role_asymmetry.md
    with open('Currier_role_asymmetry.md', 'w', encoding='utf-8') as f:
        f.write("# Currier A/B Role Asymmetry\n\n")
        f.write("> Comparing operational profiles between Currier A and B programs\n\n")
        f.write("---\n\n")

        t3 = test_results['test_3']
        f.write(f"**Verdict:** {t3['verdict']}\n\n")

        f.write("## Counts\n\n")
        f.write(f"- Currier A: {t3['counts']['currier_a']} programs\n")
        f.write(f"- Currier B: {t3['counts']['currier_b']} programs\n\n")

        f.write("## Metric Comparisons\n\n")
        f.write("| Metric | A Mean | A Std | B Mean | B Std | p-value | Cliff's d | Sig? |\n")
        f.write("|--------|--------|-------|--------|-------|---------|-----------|------|\n")
        for metric, vals in t3['metric_comparisons'].items():
            sig = "YES" if vals.get('significant', False) else "NO"
            f.write(f"| {metric} | {vals['a_mean']:.4f} | {vals['a_std']:.4f} | {vals['b_mean']:.4f} | {vals['b_std']:.4f} | {vals['p_value']:.4f} | {vals['cliffs_delta']:.3f} | {sig} |\n")

        f.write("\n## Interpretation\n\n")
        if 'interpretation' in t3:
            f.write(f"- A mean risk: {t3['interpretation']['a_mean_risk']:.4f}\n")
            f.write(f"- B mean risk: {t3['interpretation']['b_mean_risk']:.4f}\n")
            for note in t3['interpretation'].get('notes', []):
                f.write(f"- {note}\n")

    # 4. restart_program_placement.md
    with open('restart_program_placement.md', 'w', encoding='utf-8') as f:
        f.write("# Restart Program Placement Analysis\n\n")
        f.write("> Testing strategic placement of restart-capable programs\n\n")
        f.write("---\n\n")

        t5 = test_results['test_5']
        f.write(f"**Verdict:** {t5['verdict']}\n\n")

        f.write("## Restart Programs\n\n")
        rp = t5['restart_programs']
        f.write(f"- Count: {rp['count']}\n")
        f.write(f"- Folios: {', '.join(rp['folios'])}\n")
        f.write(f"- Positions: {rp['positions']}\n\n")

        f.write("## Placement Tests\n\n")
        for test_name, vals in t5['placement_tests'].items():
            f.write(f"### {test_name.replace('_', ' ').title()}\n\n")
            f.write(f"- Observed: {vals.get('observed', vals.get('coefficient_of_variation', 'N/A'))}\n")
            if 'null_mean' in vals:
                f.write(f"- Null mean: {vals['null_mean']:.2f}\n")
            f.write(f"- p-value: {vals['p_value']:.4f}\n")
            f.write(f"- Significant: {'YES' if vals.get('significant', False) else 'NO'}\n\n")

    # 5. ordering_null_models.md
    with open('ordering_null_models.md', 'w', encoding='utf-8') as f:
        f.write("# Ordering Null Model Summary\n\n")
        f.write("> Comparison of observed ordering against permutation null models\n\n")
        f.write("---\n\n")

        f.write("## Methodology\n\n")
        f.write("All tests use 10,000 permutations to construct null distributions.\n")
        f.write("P-values are computed as the fraction of null samples more extreme than observed.\n\n")

        f.write("## Summary of Tests\n\n")
        f.write("| Test | Observed | Null Mean | Null Std | p-value | Signal? |\n")
        f.write("|------|----------|-----------|----------|---------|--------|\n")

        # Test 1: Risk gradient
        perm = test_results['test_1']['permutation_tests']['risk_score']
        signal = "YES" if perm['p_value'] < 0.05 else "NO"
        f.write(f"| Risk-Order Correlation | {perm['observed_rho']:.4f} | {perm['null_mean']:.4f} | {perm['null_std']:.4f} | {perm['p_value']:.4f} | {signal} |\n")

        # Test 4: Jump analysis
        jump = test_results['test_4']['jump_analysis']
        signal = "YES" if jump['p_value'] < 0.05 else "NO"
        f.write(f"| Mean Risk Jump | {jump['observed_mean_jump']:.4f} | {jump['null_mean']:.4f} | {jump['null_std']:.4f} | {jump['p_value']:.4f} | {signal} |\n")

        # Test 4: Buffering
        buff = test_results['test_4']['buffering_analysis']
        signal = "YES" if buff['p_value'] < 0.05 else "NO"
        f.write(f"| Aggressive Buffering | {buff['buffering_rate']:.3f} | {buff['null_mean']:.3f} | {buff['null_std']:.3f} | {buff['p_value']:.4f} | {signal} |\n")

        f.write("\n## Verdicts by Test\n\n")
        for test_key, test_data in test_results.items():
            f.write(f"- **{test_data['test_name']}**: {test_data['verdict']}\n")


def compute_final_verdict(test_results: Dict) -> Dict:
    """Compute the final binary verdict."""

    verdicts = {
        'test_1': test_results['test_1']['verdict'],
        'test_2': test_results['test_2']['verdict'],
        'test_3': test_results['test_3']['verdict'],
        'test_4': test_results['test_4']['verdict'],
        'test_5': test_results['test_5']['verdict']
    }

    signal_count = sum(1 for v in verdicts.values() if v and 'SIGNAL' in v)
    weak_count = sum(1 for v in verdicts.values() if v and 'WEAK' in v)
    null_count = sum(1 for v in verdicts.values() if v and 'NULL' in v)

    if signal_count >= 3:
        final_verdict = "STRUCTURED"
        explanation = "Human-track ordering IS systematically aligned with risk and program role"
    elif signal_count >= 2 or (signal_count >= 1 and weak_count >= 2):
        final_verdict = "PARTIALLY_STRUCTURED"
        explanation = "Human-track ordering shows PARTIAL alignment with risk and program role"
    else:
        final_verdict = "NOT_STRUCTURED"
        explanation = "Human-track ordering is NOT systematically aligned with risk and program role"

    return {
        'verdict': final_verdict,
        'explanation': explanation,
        'signal_count': signal_count,
        'weak_count': weak_count,
        'null_count': null_count,
        'test_verdicts': verdicts
    }


def main():
    print("="*70)
    print("HUMAN-TRACK ORDERING vs PROGRAM RISK ANALYSIS")
    print("="*70)

    # Load data
    print("\nLoading data...")
    programs = load_data()
    print(f"Loaded {len(programs)} programs")

    # Run all tests
    test_results = {}

    test_results['test_1'] = test_1_order_vs_risk_gradient(programs)
    test_results['test_2'] = test_2_boundary_clustering(programs)
    test_results['test_3'] = test_3_currier_role_asymmetry(programs)
    test_results['test_4'] = test_4_local_neighborhood_safety(programs)
    test_results['test_5'] = test_5_restart_placement(programs)

    # Generate reports
    print("\n" + "="*70)
    print("GENERATING REPORTS")
    print("="*70)

    generate_reports(test_results)
    print("\nGenerated:")
    print("  - human_track_ordering_vs_risk.md")
    print("  - boundary_clustering_analysis.md")
    print("  - Currier_role_asymmetry.md")
    print("  - restart_program_placement.md")
    print("  - ordering_null_models.md")

    # Final verdict
    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)

    final = compute_final_verdict(test_results)

    print(f"\n** {final['verdict']} **")
    print(f"\n{final['explanation']}")
    print(f"\nSignal tests: {final['signal_count']}/5")
    print(f"Weak tests: {final['weak_count']}/5")
    print(f"Null tests: {final['null_count']}/5")

    # What this explains / fails to explain
    print("\n--- What This Explains ---")
    if final['verdict'] == 'STRUCTURED':
        print("- Folio ordering reflects operator learning progression")
        print("- Section boundaries serve as recovery/restart points")
        print("- Risky programs are buffered by safer neighbors")
        print("- Currier A/B distinction may reflect documentation regimes")
    elif final['verdict'] == 'PARTIALLY_STRUCTURED':
        print("- Some aspects of ordering are intentional")
        print("- Other aspects may be arbitrary or codicologically determined")
    else:
        print("- Ordering may be arbitrary or determined by other factors")
        print("- Risk management encoded in grammar, not in ordering")

    print("\n--- What This Fails to Explain ---")
    print("- Why specific folios are placed at specific positions")
    print("- Whether ordering reflects historical production sequence")
    print("- Relationship between ordering and illustration content")

    # Save final verdict
    with open('human_track_ordering_verdict.json', 'w', encoding='utf-8') as f:
        json.dump({
            'final_verdict': final,
            'test_results_summary': {
                k: {'verdict': v['verdict'], 'test_name': v['test_name']}
                for k, v in test_results.items()
            }
        }, f, indent=2)

    print("\nSaved: human_track_ordering_verdict.json")


if __name__ == '__main__':
    random.seed(42)  # Reproducibility
    main()
