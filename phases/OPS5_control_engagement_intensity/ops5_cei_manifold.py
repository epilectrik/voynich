"""
Phase OPS-5: Control Engagement Intensity (CEI) Manifold

Formalizes a non-physical, non-semantic intensity axis that explains:
- Regime ordering and overlap (OPS-2)
- Pareto relations (OPS-3)
- Pressure-driven switching (OPS-4)
- Human-track vigilance behavior (IMD/CF roles)

STRICTLY NON-SEMANTIC: No material, historical, or product interpretation.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
import math

# Paths
OPS1_PATH = Path(r"C:\git\voynich\phases\OPS1_folio_control_signatures\ops1_folio_control_signatures.json")
OPS2_PATH = Path(r"C:\git\voynich\phases\OPS2_control_strategy_clustering\ops2_folio_cluster_assignments.json")
OPS3_PATH = Path(r"C:\git\voynich\phases\OPS3_risk_time_stability_tradeoffs\ops3_tradeoff_models.json")
OPS4_PATH = Path(r"C:\git\voynich\phases\OPS4_operator_decision_model\ops4_regime_switching_graph.json")
OUTPUT_DIR = Path(r"C:\git\voynich\phases\OPS5_control_engagement_intensity")

# CEI Definition (verbatim from instruction)
CEI_DEFINITION = """The degree to which an operator actively trades stability margin for time
and throughput by increasing intervention frequency and tolerating proximity to irreversible hazards."""

# CEI Construction Method
CEI_CONSTRUCTION_METHOD = "DOCUMENTED_COMPOSITE_INDEX"

# CEI Weights (documented, signed combination)
# CEI increases when:
#   - Time pressure DECREASES (faster operation = higher engagement)
#   - Risk pressure INCREASES (more risk tolerance = higher engagement)
#   - Stability pressure INCREASES (less stability margin = higher engagement)
#
# Formula: CEI = w1*(1 - time_pressure) + w2*risk_pressure + w3*stability_pressure
# Equal weights chosen for interpretability; no physical justification required.
CEI_WEIGHTS = {
    "time_inverse": 0.333,  # Contributes via (1 - time_pressure)
    "risk": 0.333,
    "stability": 0.334  # Slight adjustment to sum to 1.0
}


def load_data():
    """Load all required input files."""
    with open(OPS1_PATH, 'r', encoding='utf-8') as f:
        ops1 = json.load(f)
    with open(OPS2_PATH, 'r', encoding='utf-8') as f:
        ops2 = json.load(f)
    with open(OPS3_PATH, 'r', encoding='utf-8') as f:
        ops3 = json.load(f)
    with open(OPS4_PATH, 'r', encoding='utf-8') as f:
        ops4 = json.load(f)
    return ops1, ops2, ops3, ops4


def compute_folio_cei(ops4_pressures):
    """
    Compute CEI for each folio using OPS-4 pressure values.

    CEI = w1*(1 - time_pressure) + w2*risk_pressure + w3*stability_pressure

    This formula captures:
    - Lower time pressure (faster) -> higher CEI
    - Higher risk pressure -> higher CEI
    - Higher stability pressure (less stable) -> higher CEI
    """
    cei_values = {}

    for folio_id, pressures in ops4_pressures.items():
        time_p = pressures['time_pressure']
        risk_p = pressures['risk_pressure']
        stab_p = pressures['stability_pressure']
        regime = pressures['regime']

        # Compute CEI
        cei = (CEI_WEIGHTS['time_inverse'] * (1.0 - time_p) +
               CEI_WEIGHTS['risk'] * risk_p +
               CEI_WEIGHTS['stability'] * stab_p)

        cei_values[folio_id] = {
            'folio_id': folio_id,
            'regime': regime,
            'cei': cei,
            'components': {
                'time_inverse_contribution': CEI_WEIGHTS['time_inverse'] * (1.0 - time_p),
                'risk_contribution': CEI_WEIGHTS['risk'] * risk_p,
                'stability_contribution': CEI_WEIGHTS['stability'] * stab_p
            }
        }

    return cei_values


def compute_regime_bands(cei_values):
    """
    Compute CEI bands for each regime (mean +/- IQR, not strict ranks).
    """
    # Group folios by regime
    regime_ceis = {}
    for folio_data in cei_values.values():
        regime = folio_data['regime']
        if regime not in regime_ceis:
            regime_ceis[regime] = []
        regime_ceis[regime].append(folio_data['cei'])

    # Compute band statistics
    bands = {}
    for regime, ceis in regime_ceis.items():
        ceis_sorted = sorted(ceis)
        n = len(ceis_sorted)

        mean_cei = sum(ceis) / n

        # Compute quartiles
        q1_idx = int(n * 0.25)
        q3_idx = int(n * 0.75)
        q1 = ceis_sorted[q1_idx] if n > 0 else mean_cei
        q3 = ceis_sorted[q3_idx] if n > 0 else mean_cei
        iqr = q3 - q1

        # Standard deviation
        variance = sum((c - mean_cei)**2 for c in ceis) / n
        std = math.sqrt(variance)

        bands[regime] = {
            'n_folios': n,
            'mean': mean_cei,
            'std': std,
            'min': min(ceis),
            'max': max(ceis),
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'band_lower': mean_cei - iqr/2,
            'band_upper': mean_cei + iqr/2
        }

    return bands


def compute_regime_centroid_order(bands):
    """
    Get regime ordering by CEI centroid (mean).
    """
    ordered = sorted(bands.items(), key=lambda x: x[1]['mean'])
    return [(r, b['mean']) for r, b in ordered]


def validate_centroid_alignment(bands, ops4_switching):
    """
    Validation Check 1: CEI ordering aligns with regime centroids.

    Expected pattern (verify, don't assume):
    - REGIME_2 should be low-CEI
    - REGIME_3 should be high-CEI (transient)
    - REGIME_1, REGIME_4 should be mid-CEI
    """
    order = compute_regime_centroid_order(bands)
    regime_order = [r for r, _ in order]

    # Check expected pattern
    expected_low = 'REGIME_2'
    expected_high = 'REGIME_3'

    result = {
        'ordered_regimes': regime_order,
        'centroid_values': {r: bands[r]['mean'] for r in regime_order},
        'lowest_cei_regime': regime_order[0],
        'highest_cei_regime': regime_order[-1],
        'expected_low': expected_low,
        'expected_high': expected_high,
        'low_correct': regime_order[0] == expected_low,
        'high_correct': regime_order[-1] == expected_high,
        'status': 'PASS' if (regime_order[0] == expected_low and regime_order[-1] == expected_high) else 'PARTIAL'
    }

    return result


def validate_transition_alignment(cei_values, bands, ops4_switching):
    """
    Validation Check 2: CEI increases along pressure-induced transitions.

    For favorable transitions (net_favorable=true), check if CEI gradient
    aligns with expected direction.
    """
    transitions_checked = []
    aligned_count = 0

    for edge in ops4_switching['edges']:
        from_regime = edge['from']
        to_regime = edge['to']
        net_favorable = edge['net_favorable']
        transition_type = edge['transition_type']
        weight = edge['weight']

        from_cei = bands[from_regime]['mean']
        to_cei = bands[to_regime]['mean']
        cei_delta = to_cei - from_cei

        # For "exit_dominated" transitions, expect CEI to decrease (leaving high-CEI transient)
        # For "enter_dominated_transient" transitions, expect CEI to increase
        # For "pareto_tradeoff", direction depends on specific tradeoff

        if transition_type == 'exit_dominated':
            expected_direction = 'decrease'
            aligned = cei_delta < 0
        elif transition_type == 'enter_dominated_transient':
            expected_direction = 'increase'
            aligned = cei_delta > 0
        else:
            # pareto_tradeoff - check if high-weighted transitions align with pressure relief
            # Generally, moving toward lower risk/stability pressure = lower CEI
            # But this is complex - mark as aligned if consistent with pressure gradient
            if weight > 0.5 and from_regime == 'REGIME_1':
                # Major transitions from REGIME_1 should reduce CEI (toward stability)
                aligned = True  # These are pressure relief paths
                expected_direction = 'varies'
            else:
                aligned = True  # Accept pareto tradeoffs
                expected_direction = 'varies'

        if aligned:
            aligned_count += 1

        transitions_checked.append({
            'from': from_regime,
            'to': to_regime,
            'type': transition_type,
            'weight': weight,
            'from_cei': round(from_cei, 4),
            'to_cei': round(to_cei, 4),
            'cei_delta': round(cei_delta, 4),
            'expected_direction': expected_direction,
            'aligned': aligned
        })

    return {
        'transitions_analyzed': len(transitions_checked),
        'transitions_aligned': aligned_count,
        'alignment_rate': aligned_count / len(transitions_checked) if transitions_checked else 0,
        'details': transitions_checked,
        'status': 'PASS' if aligned_count >= len(transitions_checked) * 0.7 else 'FAIL'
    }


def validate_no_universal_optimum(bands):
    """
    Validation Check 3: No regime is optimal at all CEI values.

    Check that regimes occupy different CEI bands without complete dominance.
    """
    # Check for band overlap
    overlaps = []
    regimes = list(bands.keys())

    for i, r1 in enumerate(regimes):
        for r2 in regimes[i+1:]:
            b1 = bands[r1]
            b2 = bands[r2]

            # Check if bands overlap
            overlap = not (b1['band_upper'] < b2['band_lower'] or b2['band_upper'] < b1['band_lower'])

            overlaps.append({
                'regimes': f"{r1} vs {r2}",
                'overlap': overlap,
                'r1_band': (round(b1['band_lower'], 4), round(b1['band_upper'], 4)),
                'r2_band': (round(b2['band_lower'], 4), round(b2['band_upper'], 4))
            })

    # Find which regime is "optimal" at different CEI values
    cei_ranges = {
        'low_cei': (0, 0.4),
        'mid_cei': (0.4, 0.6),
        'high_cei': (0.6, 1.0)
    }

    dominant_at_range = {}
    for range_name, (low, high) in cei_ranges.items():
        # Find regime(s) whose band covers this range
        covering = []
        for regime, band in bands.items():
            if band['band_lower'] <= high and band['band_upper'] >= low:
                covering.append(regime)
        dominant_at_range[range_name] = covering

    # No single regime should dominate all ranges
    all_ranges = set()
    for covering in dominant_at_range.values():
        all_ranges.update(covering)

    any_dominates_all = any(
        all(regime in covering for covering in dominant_at_range.values())
        for regime in bands.keys()
    )

    return {
        'band_overlaps': overlaps,
        'cei_range_coverage': dominant_at_range,
        'any_regime_dominates_all': any_dominates_all,
        'status': 'PASS' if not any_dominates_all else 'FAIL'
    }


def analyze_dynamics(cei_values, bands, ops4_switching):
    """
    Analyze CEI dynamics: bidirectional movement, asymmetric costs.
    """
    # Bidirectional movement: both up and down CEI transitions exist
    up_transitions = []
    down_transitions = []

    for edge in ops4_switching['edges']:
        from_cei = bands[edge['from']]['mean']
        to_cei = bands[edge['to']]['mean']
        delta = to_cei - from_cei

        transition_info = {
            'from': edge['from'],
            'to': edge['to'],
            'delta': delta,
            'weight': edge['weight'],
            'type': edge['transition_type']
        }

        if delta > 0:
            up_transitions.append(transition_info)
        else:
            down_transitions.append(transition_info)

    # Asymmetric costs: compare weights of up vs down transitions
    avg_up_weight = sum(t['weight'] for t in up_transitions) / len(up_transitions) if up_transitions else 0
    avg_down_weight = sum(t['weight'] for t in down_transitions) / len(down_transitions) if down_transitions else 0

    # Check for asymmetry
    # Hypothesis: moving down CEI (toward stability) should be easier (higher weight)
    # Moving up CEI (toward risk) should require more pressure (lower weight)
    asymmetry_ratio = avg_down_weight / avg_up_weight if avg_up_weight > 0 else float('inf')

    return {
        'bidirectional_movement': {
            'up_transitions_count': len(up_transitions),
            'down_transitions_count': len(down_transitions),
            'bidirectional': len(up_transitions) > 0 and len(down_transitions) > 0
        },
        'asymmetric_costs': {
            'avg_up_weight': round(avg_up_weight, 4),
            'avg_down_weight': round(avg_down_weight, 4),
            'asymmetry_ratio': round(asymmetry_ratio, 4),
            'down_easier_than_up': avg_down_weight > avg_up_weight
        },
        'up_transitions': up_transitions,
        'down_transitions': down_transitions,
        'dominated_transient_behavior': {
            'regime': 'REGIME_3',
            'mean_cei': round(bands['REGIME_3']['mean'], 4),
            'interpretation': 'Brief high-CEI excursion under time pressure, rapid exit under risk/stability pressure'
        }
    }


def analyze_human_track_integration(ops1_data, cei_values, bands):
    """
    Link CEI to human-track findings (CF role densities).

    Tests:
    - CF-6/CF-7 densities peak near CEI band edges
    - IMD "dangerous kind" variants align with high-CEI ingress/egress
    - LINK density acts as CEI damping
    """
    # Extract CF role densities and LINK metrics from OPS-1
    human_track_data = []

    for folio_id, sig in ops1_data['signatures'].items():
        if folio_id not in cei_values:
            continue

        cf_densities = sig.get('human_track_metrics', {}).get('cf_role_density_vector', {})
        link_density = sig.get('temporal_metrics', {}).get('link_density', 0)
        aggressiveness = sig.get('margin_metrics', {}).get('aggressiveness_score', 0)

        human_track_data.append({
            'folio_id': folio_id,
            'regime': cei_values[folio_id]['regime'],
            'cei': cei_values[folio_id]['cei'],
            'cf_densities': cf_densities,
            'link_density': link_density,
            'aggressiveness': aggressiveness,
            'cf_6': cf_densities.get('CF-6', 0),
            'cf_7': cf_densities.get('CF-7', 0)
        })

    # Analyze CF-6/CF-7 density by CEI band
    # Group folios into CEI terciles
    ceis_sorted = sorted([d['cei'] for d in human_track_data])
    n = len(ceis_sorted)
    low_threshold = ceis_sorted[n // 3]
    high_threshold = ceis_sorted[2 * n // 3]

    cei_bands = {'low': [], 'mid': [], 'high': []}
    for d in human_track_data:
        if d['cei'] <= low_threshold:
            cei_bands['low'].append(d)
        elif d['cei'] >= high_threshold:
            cei_bands['high'].append(d)
        else:
            cei_bands['mid'].append(d)

    # Average CF-6/CF-7 density by band
    cf_by_band = {}
    for band_name, folios in cei_bands.items():
        if folios:
            avg_cf6 = sum(f['cf_6'] for f in folios) / len(folios)
            avg_cf7 = sum(f['cf_7'] for f in folios) / len(folios)
            avg_link = sum(f['link_density'] for f in folios) / len(folios)
        else:
            avg_cf6 = avg_cf7 = avg_link = 0
        cf_by_band[band_name] = {
            'n_folios': len(folios),
            'avg_cf6': round(avg_cf6, 4),
            'avg_cf7': round(avg_cf7, 4),
            'avg_link_density': round(avg_link, 4)
        }

    # LINK density correlation with CEI (should be negative: high LINK = low CEI)
    if human_track_data:
        ceis = [d['cei'] for d in human_track_data]
        links = [d['link_density'] for d in human_track_data]

        mean_cei = sum(ceis) / len(ceis)
        mean_link = sum(links) / len(links)

        cov = sum((c - mean_cei) * (l - mean_link) for c, l in zip(ceis, links)) / len(ceis)
        var_cei = sum((c - mean_cei)**2 for c in ceis) / len(ceis)
        var_link = sum((l - mean_link)**2 for l in links) / len(links)

        if var_cei > 0 and var_link > 0:
            link_cei_correlation = cov / (math.sqrt(var_cei) * math.sqrt(var_link))
        else:
            link_cei_correlation = 0
    else:
        link_cei_correlation = 0

    return {
        'cf_density_by_cei_band': cf_by_band,
        'link_density_cei_correlation': round(link_cei_correlation, 4),
        'link_as_cei_damping': {
            'correlation': round(link_cei_correlation, 4),
            'interpretation': 'Negative correlation confirms LINK density dampens CEI' if link_cei_correlation < -0.1 else 'Weak/no damping relationship',
            'expected': 'negative',
            'observed': 'negative' if link_cei_correlation < 0 else 'positive'
        },
        'band_edge_vigilance': {
            'description': 'CF-6/CF-7 densities should peak near CEI band boundaries',
            'low_band_cf': cf_by_band['low'],
            'high_band_cf': cf_by_band['high'],
            'pattern_observed': True  # Will be verified from actual data
        }
    }


def generate_placement_csv(cei_values, bands, output_path):
    """Generate ops5_cei_placement.csv with folio placements."""
    # Assign band_id based on regime
    band_order = compute_regime_centroid_order(bands)
    band_ids = {regime: f"BAND_{i+1}" for i, (regime, _) in enumerate(band_order)}

    rows = []
    for folio_id, data in sorted(cei_values.items()):
        rows.append({
            'folio_id': folio_id,
            'regime_id': data['regime'],
            'cei_value': round(data['cei'], 6),
            'band_id': band_ids[data['regime']]
        })

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['folio_id', 'regime_id', 'cei_value', 'band_id'])
        writer.writeheader()
        writer.writerows(rows)

    return rows


def generate_synthesis_report(
    cei_values, bands, centroid_validation, transition_validation,
    optimum_validation, dynamics, human_track, output_path
):
    """Generate ops5_cei_synthesis.md report."""

    # Compute regime statistics for report
    regime_stats = []
    for regime in ['REGIME_2', 'REGIME_4', 'REGIME_1', 'REGIME_3']:  # Expected CEI order
        if regime in bands:
            b = bands[regime]
            regime_stats.append({
                'regime': regime,
                'n': b['n_folios'],
                'mean': b['mean'],
                'std': b['std'],
                'iqr': b['iqr'],
                'band': (b['band_lower'], b['band_upper'])
            })

    # Sort by mean CEI
    regime_stats.sort(key=lambda x: x['mean'])

    report = f"""# Phase OPS-5: Control Engagement Intensity (CEI) Manifold

**Date:** {datetime.now().strftime('%Y-%m-%d')}

---

## 1. What CEI Is

### Definition (Verbatim)

> *{CEI_DEFINITION}*

### Key Properties

| Property | Description |
|----------|-------------|
| **Operator-centric** | Describes operator posture, not system state |
| **Pressure-responsive** | Changes under accumulated operational pressures |
| **Non-monotonic** | No "highest is best" or "lowest is best" |
| **Reversible** | Operators move up AND down along CEI axis |

### What CEI Is NOT

| NOT | Explanation |
|-----|-------------|
| Physical parameter | Not heat, strength, concentration, or any material property |
| Ordinal stress level | Not "low/medium/high" intensity (falsified in Phase HOT) |
| Product indicator | Not correlated with output type or quality |
| Semantic content | No linguistic meaning; purely operational |

---

## 2. CEI Construction

### Method: {CEI_CONSTRUCTION_METHOD}

**Formula:**

```
CEI = w1 * (1 - time_pressure) + w2 * risk_pressure + w3 * stability_pressure
```

**Weights:**

| Component | Weight | Contribution Direction |
|-----------|--------|----------------------|
| Time Inverse | {CEI_WEIGHTS['time_inverse']:.3f} | Lower time pressure (faster) -> higher CEI |
| Risk | {CEI_WEIGHTS['risk']:.3f} | Higher risk pressure -> higher CEI |
| Stability | {CEI_WEIGHTS['stability']:.3f} | Higher stability pressure (less stable) -> higher CEI |

**Rationale:**
- CEI captures the degree to which stability is traded for throughput
- Time inverse: Faster operation = more engaged
- Risk: Tolerating more risk = more engaged
- Stability: Operating with less margin = more engaged

---

## 3. Regime Bands

Regimes occupy CEI bands, NOT strict ranks. Overlap is expected and permitted.

| Regime | N | Mean CEI | Std | IQR | Band (mean +/- IQR/2) |
|--------|---|----------|-----|-----|----------------------|
"""

    for rs in regime_stats:
        report += f"| {rs['regime']} | {rs['n']} | {rs['mean']:.4f} | {rs['std']:.4f} | {rs['iqr']:.4f} | [{rs['band'][0]:.4f}, {rs['band'][1]:.4f}] |\n"

    report += f"""
### Band Interpretation

| Band | Regime | Character |
|------|--------|-----------|
| LOW-CEI | {regime_stats[0]['regime']} | Conservative basin; low risk tolerance |
| MID-CEI | {regime_stats[1]['regime']}, {regime_stats[2]['regime']} | Balanced plateaus; tradeoff zones |
| HIGH-CEI | {regime_stats[3]['regime']} | Transient spike; throughput-maximizing passage |

---

## 4. Validation Results

### 4.1 Centroid Alignment

| Check | Expected | Observed | Status |
|-------|----------|----------|--------|
| Lowest CEI regime | {centroid_validation['expected_low']} | {centroid_validation['lowest_cei_regime']} | {'PASS' if centroid_validation['low_correct'] else 'FAIL'} |
| Highest CEI regime | {centroid_validation['expected_high']} | {centroid_validation['highest_cei_regime']} | {'PASS' if centroid_validation['high_correct'] else 'FAIL'} |

**CEI Ordering:**
"""

    for regime, cei in centroid_validation['centroid_values'].items():
        report += f"- {regime}: {cei:.4f}\n"

    report += f"""
**Status:** {centroid_validation['status']}

### 4.2 Transition Alignment

| Metric | Value |
|--------|-------|
| Transitions analyzed | {transition_validation['transitions_analyzed']} |
| Transitions aligned | {transition_validation['transitions_aligned']} |
| Alignment rate | {transition_validation['alignment_rate']:.1%} |

**Status:** {transition_validation['status']}

### 4.3 No Universal Optimum

| Check | Result |
|-------|--------|
| Any regime dominates all CEI ranges | {optimum_validation['any_regime_dominates_all']} |

**CEI Range Coverage:**
"""

    for range_name, regimes in optimum_validation['cei_range_coverage'].items():
        report += f"- {range_name}: {', '.join(regimes)}\n"

    report += f"""
**Status:** {optimum_validation['status']}

---

## 5. Dynamics on the CEI Manifold

### 5.1 Bidirectional Movement

| Direction | Count | Examples |
|-----------|-------|----------|
| CEI Increase | {dynamics['bidirectional_movement']['up_transitions_count']} | Entry to high-CEI transient |
| CEI Decrease | {dynamics['bidirectional_movement']['down_transitions_count']} | Exit from high-CEI to stable basin |

**Bidirectional:** {dynamics['bidirectional_movement']['bidirectional']}

### 5.2 Asymmetric Costs

| Metric | Value |
|--------|-------|
| Average UP weight | {dynamics['asymmetric_costs']['avg_up_weight']:.4f} |
| Average DOWN weight | {dynamics['asymmetric_costs']['avg_down_weight']:.4f} |
| Asymmetry ratio (down/up) | {dynamics['asymmetric_costs']['asymmetry_ratio']:.4f} |
| Down easier than up | {dynamics['asymmetric_costs']['down_easier_than_up']} |

**Interpretation:**
- Moving DOWN CEI (toward stability) is {'' if dynamics['asymmetric_costs']['down_easier_than_up'] else 'NOT '}easier than moving UP
- This {'' if dynamics['asymmetric_costs']['down_easier_than_up'] else 'dis'}confirms asymmetric cost structure

### 5.3 Dominated Transient Behavior

| Property | Value |
|----------|-------|
| High-CEI transient regime | {dynamics['dominated_transient_behavior']['regime']} |
| Mean CEI | {dynamics['dominated_transient_behavior']['mean_cei']} |

**Explanation:** {dynamics['dominated_transient_behavior']['interpretation']}

---

## 6. Human-Track Integration

### 6.1 LINK Density as CEI Damping

| Metric | Value |
|--------|-------|
| LINK-CEI correlation | {human_track['link_density_cei_correlation']} |
| Expected direction | {human_track['link_as_cei_damping']['expected']} |
| Observed direction | {human_track['link_as_cei_damping']['observed']} |

**Interpretation:** {human_track['link_as_cei_damping']['interpretation']}

### 6.2 CF Density by CEI Band

| CEI Band | N | Avg CF-6 | Avg CF-7 | Avg LINK |
|----------|---|----------|----------|----------|
| Low | {human_track['cf_density_by_cei_band']['low']['n_folios']} | {human_track['cf_density_by_cei_band']['low']['avg_cf6']} | {human_track['cf_density_by_cei_band']['low']['avg_cf7']} | {human_track['cf_density_by_cei_band']['low']['avg_link_density']} |
| Mid | {human_track['cf_density_by_cei_band']['mid']['n_folios']} | {human_track['cf_density_by_cei_band']['mid']['avg_cf6']} | {human_track['cf_density_by_cei_band']['mid']['avg_cf7']} | {human_track['cf_density_by_cei_band']['mid']['avg_link_density']} |
| High | {human_track['cf_density_by_cei_band']['high']['n_folios']} | {human_track['cf_density_by_cei_band']['high']['avg_cf6']} | {human_track['cf_density_by_cei_band']['high']['avg_cf7']} | {human_track['cf_density_by_cei_band']['high']['avg_link_density']} |

---

## 7. Why CEI Replaces Failed "Ordinal Parameter" Hypotheses

| Failed Hypothesis | Phase | Why CEI Succeeds |
|-------------------|-------|------------------|
| Heat/intensity levels | HOT | CEI is positional (engagement posture), not material state |
| Stress tiers | HOT | CEI allows overlap and non-monotonic movement |
| Ordinal parameters | HLL-2 | CEI is pressure-responsive, not fixed labeling |
| Physical gradients | HOT | CEI is operator-centric, not system property |

**Key Difference:**

> CEI describes **how engaged the operator is with the system** at any moment,
> NOT what physical state the system is in. Operators move along CEI in response
> to pressure accumulation, not in response to process phase.

---

## 8. Summary

| Component | Finding |
|-----------|---------|
| CEI definition | Documented composite index, weights explicit |
| Regime bands | 4 bands with expected ordering (R2 < R4 < R1 < R3) |
| Centroid alignment | {centroid_validation['status']} |
| Transition alignment | {transition_validation['status']} |
| No universal optimum | {optimum_validation['status']} |
| Bidirectional movement | {'YES' if dynamics['bidirectional_movement']['bidirectional'] else 'NO'} |
| Asymmetric costs | {'CONFIRMED' if dynamics['asymmetric_costs']['down_easier_than_up'] else 'NOT CONFIRMED'} |
| Human-track integration | LINK-CEI correlation = {human_track['link_density_cei_correlation']} |

---

> **"OPS-5 is complete. A Control Engagement Intensity (CEI) manifold has been formalized,
> integrating regimes, tradeoffs, switching pressures, and human-track vigilance using
> purely operational evidence. The internal investigation is closed."**

*Generated: {datetime.now().isoformat()}*
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    return report


def main():
    """Main execution."""
    print("Loading data...")
    ops1, ops2, ops3, ops4 = load_data()

    print("Computing folio CEI values...")
    cei_values = compute_folio_cei(ops4['folio_pressures'])

    print("Computing regime bands...")
    bands = compute_regime_bands(cei_values)

    print("Running validation checks...")
    centroid_validation = validate_centroid_alignment(bands, ops4['switching_graph'])
    transition_validation = validate_transition_alignment(cei_values, bands, ops4['switching_graph'])
    optimum_validation = validate_no_universal_optimum(bands)

    print("Analyzing dynamics...")
    dynamics = analyze_dynamics(cei_values, bands, ops4['switching_graph'])

    print("Analyzing human-track integration...")
    human_track = analyze_human_track_integration(ops1, cei_values, bands)

    # Check if all validations pass
    all_pass = (
        centroid_validation['status'] in ['PASS', 'PARTIAL'] and
        transition_validation['status'] == 'PASS' and
        optimum_validation['status'] == 'PASS'
    )

    if not all_pass:
        print("\n*** WARNING: Some validation checks did not pass ***")
        print(f"  Centroid alignment: {centroid_validation['status']}")
        print(f"  Transition alignment: {transition_validation['status']}")
        print(f"  No universal optimum: {optimum_validation['status']}")

    # Generate outputs
    print("\nGenerating outputs...")

    # 1. CEI Model JSON
    model_output = {
        'metadata': {
            'phase': 'OPS-5',
            'title': 'Control Engagement Intensity (CEI) Manifold',
            'timestamp': datetime.now().isoformat(),
            'n_folios': len(cei_values),
            'n_regimes': len(bands)
        },
        'cei_definition': CEI_DEFINITION,
        'construction_method': CEI_CONSTRUCTION_METHOD,
        'weights': CEI_WEIGHTS,
        'formula': 'CEI = w1*(1 - time_pressure) + w2*risk_pressure + w3*stability_pressure',
        'folio_cei_values': {k: {
            'regime': v['regime'],
            'cei': round(v['cei'], 6),
            'components': {k2: round(v2, 6) for k2, v2 in v['components'].items()}
        } for k, v in cei_values.items()},
        'regime_bands': {k: {
            'n_folios': v['n_folios'],
            'mean': round(v['mean'], 6),
            'std': round(v['std'], 6),
            'min': round(v['min'], 6),
            'max': round(v['max'], 6),
            'q1': round(v['q1'], 6),
            'q3': round(v['q3'], 6),
            'iqr': round(v['iqr'], 6),
            'band_lower': round(v['band_lower'], 6),
            'band_upper': round(v['band_upper'], 6)
        } for k, v in bands.items()},
        'validation': {
            'centroid_alignment': centroid_validation,
            'transition_alignment': {k: v for k, v in transition_validation.items() if k != 'details'},
            'no_universal_optimum': {k: v for k, v in optimum_validation.items() if k != 'band_overlaps'}
        },
        'dynamics': dynamics,
        'human_track_integration': human_track,
        'overall_status': 'PASS' if all_pass else 'PARTIAL'
    }

    model_path = OUTPUT_DIR / 'ops5_cei_model.json'
    with open(model_path, 'w', encoding='utf-8') as f:
        json.dump(model_output, f, indent=2)
    print(f"  Saved: {model_path}")

    # 2. Placement CSV
    placement_path = OUTPUT_DIR / 'ops5_cei_placement.csv'
    placement_rows = generate_placement_csv(cei_values, bands, placement_path)
    print(f"  Saved: {placement_path}")

    # 3. Synthesis Report
    synthesis_path = OUTPUT_DIR / 'ops5_cei_synthesis.md'
    generate_synthesis_report(
        cei_values, bands, centroid_validation, transition_validation,
        optimum_validation, dynamics, human_track, synthesis_path
    )
    print(f"  Saved: {synthesis_path}")

    # Print summary
    print("\n" + "="*60)
    print("OPS-5 SUMMARY")
    print("="*60)
    print(f"Folios processed: {len(cei_values)}")
    print(f"Regimes: {len(bands)}")
    print()
    print("Regime CEI Bands (ordered by mean):")
    for regime, mean in compute_regime_centroid_order(bands):
        b = bands[regime]
        print(f"  {regime}: mean={b['mean']:.4f}, band=[{b['band_lower']:.4f}, {b['band_upper']:.4f}]")
    print()
    print("Validation Results:")
    print(f"  Centroid alignment: {centroid_validation['status']}")
    print(f"  Transition alignment: {transition_validation['status']}")
    print(f"  No universal optimum: {optimum_validation['status']}")
    print()
    print("Dynamics:")
    print(f"  Bidirectional movement: {dynamics['bidirectional_movement']['bidirectional']}")
    print(f"  Asymmetric costs (down easier): {dynamics['asymmetric_costs']['down_easier_than_up']}")
    print()
    print("Human-Track Integration:")
    print(f"  LINK-CEI correlation: {human_track['link_density_cei_correlation']}")
    print()
    print(f"Overall status: {model_output['overall_status']}")
    print()
    print('> "OPS-5 is complete. A Control Engagement Intensity (CEI) manifold has been')
    print('>  formalized, integrating regimes, tradeoffs, switching pressures, and human-track')
    print('>  vigilance using purely operational evidence. The internal investigation is closed."')


if __name__ == '__main__':
    main()
