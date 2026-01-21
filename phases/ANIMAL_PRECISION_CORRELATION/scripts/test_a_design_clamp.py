#!/usr/bin/env python3
"""
Test A: Design Clamp Validation

Per C458 (Execution Design Clamp):
- Hazard exposure CV should be 0.04-0.11 (clamped)
- Recovery CV should be 0.72-0.82 (free)

Test: Does REGIME_4 conform to this pattern, or does it differ?

Pre-registered prediction P1 (Strong):
REGIME_4 hazard CV will be within 0.04-0.11. If violated, C458 needs revision.
"""

import json
import statistics
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

# Load scaffold audit data
with open(PROJECT_ROOT / 'results' / 'b_macro_scaffold_audit.json', 'r') as f:
    scaffold_data = json.load(f)

features = scaffold_data['features']

# Group folios by REGIME
regime_groups = {}
for folio, feat in features.items():
    regime = feat['regime']
    if regime not in regime_groups:
        regime_groups[regime] = []
    regime_groups[regime].append({
        'folio': folio,
        'hazard_density': feat['hazard_density'],
        'recovery_ops_count': feat['recovery_ops_count'],
        'intervention_frequency': feat['intervention_frequency'],
        'near_miss_count': feat['near_miss_count'],
        'cei_total': feat['cei_total']
    })

print("=" * 70)
print("TEST A: DESIGN CLAMP VALIDATION (C458)")
print("=" * 70)
print()
print("C458 predicts:")
print("  - Hazard CV: 0.04-0.11 (clamped across all REGIMEs)")
print("  - Recovery CV: 0.72-0.82 (free to vary)")
print()
print("P1 (Strong): REGIME_4 hazard CV within 0.04-0.11")
print()

def compute_cv(values):
    """Compute coefficient of variation (std/mean)."""
    if len(values) < 2:
        return None
    mean = statistics.mean(values)
    if mean == 0:
        return None
    std = statistics.stdev(values)
    return std / mean

print("-" * 70)
print("HAZARD DENSITY BY REGIME")
print("-" * 70)

hazard_results = {}
for regime in sorted(regime_groups.keys()):
    folios = regime_groups[regime]
    hazard_values = [f['hazard_density'] for f in folios]

    cv = compute_cv(hazard_values)
    mean = statistics.mean(hazard_values)
    std = statistics.stdev(hazard_values) if len(hazard_values) > 1 else 0

    hazard_results[regime] = {
        'n': len(folios),
        'mean': mean,
        'std': std,
        'cv': cv,
        'min': min(hazard_values),
        'max': max(hazard_values)
    }

    in_range = 0.04 <= cv <= 0.11 if cv else False
    flag = "CLAMPED" if in_range else "OUTSIDE"

    print(f"{regime} (n={len(folios):2d}): mean={mean:.3f}, std={std:.3f}, CV={cv:.3f} [{flag}]")

print()
print("-" * 70)
print("RECOVERY OPS BY REGIME")
print("-" * 70)

recovery_results = {}
for regime in sorted(regime_groups.keys()):
    folios = regime_groups[regime]
    recovery_values = [f['recovery_ops_count'] for f in folios]

    cv = compute_cv(recovery_values)
    mean = statistics.mean(recovery_values)
    std = statistics.stdev(recovery_values) if len(recovery_values) > 1 else 0

    recovery_results[regime] = {
        'n': len(folios),
        'mean': mean,
        'std': std,
        'cv': cv,
        'min': min(recovery_values),
        'max': max(recovery_values)
    }

    in_range = 0.72 <= cv <= 0.82 if cv else False
    flag = "FREE" if in_range else "OUTSIDE"

    print(f"{regime} (n={len(folios):2d}): mean={mean:.1f}, std={std:.1f}, CV={cv:.3f} [{flag}]")

print()
print("-" * 70)
print("INTERVENTION FREQUENCY BY REGIME")
print("-" * 70)

intervention_results = {}
for regime in sorted(regime_groups.keys()):
    folios = regime_groups[regime]
    intervention_values = [f['intervention_frequency'] for f in folios]

    cv = compute_cv(intervention_values)
    mean = statistics.mean(intervention_values)
    std = statistics.stdev(intervention_values) if len(intervention_values) > 1 else 0

    intervention_results[regime] = {
        'n': len(folios),
        'mean': mean,
        'std': std,
        'cv': cv
    }

    print(f"{regime} (n={len(folios):2d}): mean={mean:.3f}, std={std:.3f}, CV={cv:.3f}")

print()
print("-" * 70)
print("NEAR-MISS COUNT BY REGIME")
print("-" * 70)

near_miss_results = {}
for regime in sorted(regime_groups.keys()):
    folios = regime_groups[regime]
    near_miss_values = [f['near_miss_count'] for f in folios]

    cv = compute_cv(near_miss_values)
    mean = statistics.mean(near_miss_values)
    std = statistics.stdev(near_miss_values) if len(near_miss_values) > 1 else 0

    near_miss_results[regime] = {
        'n': len(folios),
        'mean': mean,
        'std': std,
        'cv': cv
    }

    print(f"{regime} (n={len(folios):2d}): mean={mean:.1f}, std={std:.1f}, CV={cv:.3f}")

# Global CV calculation
print()
print("=" * 70)
print("GLOBAL CV (ALL REGIMES COMBINED)")
print("=" * 70)

all_hazard = [f['hazard_density'] for regime_folios in regime_groups.values() for f in regime_folios]
all_recovery = [f['recovery_ops_count'] for regime_folios in regime_groups.values() for f in regime_folios]
all_intervention = [f['intervention_frequency'] for regime_folios in regime_groups.values() for f in regime_folios]
all_near_miss = [f['near_miss_count'] for regime_folios in regime_groups.values() for f in regime_folios]

global_hazard_cv = compute_cv(all_hazard)
global_recovery_cv = compute_cv(all_recovery)
global_intervention_cv = compute_cv(all_intervention)
global_near_miss_cv = compute_cv(all_near_miss)

print(f"Hazard CV (global):       {global_hazard_cv:.3f} (C458 predicts 0.04-0.11)")
print(f"Recovery CV (global):     {global_recovery_cv:.3f} (C458 predicts 0.72-0.82)")
print(f"Intervention CV (global): {global_intervention_cv:.3f} (C458 predicts 0.04)")
print(f"Near-miss CV (global):    {global_near_miss_cv:.3f} (C458 predicts 0.72)")

# P1 Test: REGIME_4 hazard CV
print()
print("=" * 70)
print("P1 EVALUATION: REGIME_4 Hazard CV")
print("=" * 70)

r4_hazard_cv = hazard_results['REGIME_4']['cv']
p1_pass = 0.04 <= r4_hazard_cv <= 0.11 if r4_hazard_cv else False

print(f"REGIME_4 hazard CV: {r4_hazard_cv:.3f}")
print(f"Expected range: 0.04-0.11")
print(f"P1 Result: {'PASS' if p1_pass else 'FAIL'}")

if not p1_pass:
    print()
    print("NOTE: P1 FAILED - REGIME_4 hazard CV is outside the clamped range.")
    print("This suggests REGIME_4 may have different hazard characteristics.")

# Compare REGIME_4 to other REGIMEs
print()
print("=" * 70)
print("REGIME_4 vs OTHER REGIMES COMPARISON")
print("=" * 70)

r4_mean_hazard = hazard_results['REGIME_4']['mean']
r4_mean_recovery = recovery_results['REGIME_4']['mean']

other_hazard_means = [hazard_results[r]['mean'] for r in hazard_results if r != 'REGIME_4']
other_recovery_means = [recovery_results[r]['mean'] for r in recovery_results if r != 'REGIME_4']

avg_other_hazard = statistics.mean(other_hazard_means)
avg_other_recovery = statistics.mean(other_recovery_means)

print(f"REGIME_4 hazard mean:  {r4_mean_hazard:.3f}")
print(f"Other REGIMEs mean:    {avg_other_hazard:.3f}")
print(f"Ratio (R4/other):      {r4_mean_hazard/avg_other_hazard:.2f}x")
print()
print(f"REGIME_4 recovery mean:  {r4_mean_recovery:.1f}")
print(f"Other REGIMEs mean:      {avg_other_recovery:.1f}")
print(f"Ratio (R4/other):        {r4_mean_recovery/avg_other_recovery:.2f}x")

# CEI comparison
print()
print("-" * 70)
print("CEI BY REGIME (Control Efficiency Index)")
print("-" * 70)

for regime in sorted(regime_groups.keys()):
    folios = regime_groups[regime]
    cei_values = [f['cei_total'] for f in folios]
    mean = statistics.mean(cei_values)
    std = statistics.stdev(cei_values) if len(cei_values) > 1 else 0
    cv = compute_cv(cei_values)
    print(f"{regime} (n={len(folios):2d}): mean={mean:.3f}, std={std:.3f}, CV={cv:.3f}")

# Save results
results = {
    'test': 'A_DESIGN_CLAMP_VALIDATION',
    'c458_predictions': {
        'hazard_cv': '0.04-0.11 (clamped)',
        'recovery_cv': '0.72-0.82 (free)',
        'intervention_cv': '0.04 (clamped)',
        'near_miss_cv': '0.72 (free)'
    },
    'global_cv': {
        'hazard': global_hazard_cv,
        'recovery': global_recovery_cv,
        'intervention': global_intervention_cv,
        'near_miss': global_near_miss_cv
    },
    'by_regime': {
        'hazard': hazard_results,
        'recovery': recovery_results,
        'intervention': intervention_results,
        'near_miss': near_miss_results
    },
    'p1_evaluation': {
        'prediction': 'REGIME_4 hazard CV within 0.04-0.11',
        'actual_cv': r4_hazard_cv,
        'result': 'PASS' if p1_pass else 'FAIL'
    },
    'regime_4_comparison': {
        'hazard_mean': r4_mean_hazard,
        'hazard_ratio_vs_others': r4_mean_hazard / avg_other_hazard,
        'recovery_mean': r4_mean_recovery,
        'recovery_ratio_vs_others': r4_mean_recovery / avg_other_recovery
    }
}

output_path = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'test_a_design_clamp.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print()
print(f"Results saved to {output_path}")
