#!/usr/bin/env python3
"""
PHASE 5: REGIME ASSIGNMENT AND PRODUCT TYPE CLASSIFICATION

Assign each recipe to REGIME and product type based on:
- Fire degree (from Brunschwig's distillation instructions)
- Precision requirement (from procedure complexity)
- Monitoring intensity (from LINK ratio)
- Recovery mentions (from RECOVERY class presence)

Based on C494: REGIME_4 = precision, not intensity

Assignment rules:
| Fire Degree | REGIME | Product Type | CEI Range |
|-------------|--------|--------------|-----------|
| 1st (balneum) | REGIME_2 | WATER_GENTLE | 0.30-0.40 |
| 2nd (warm) | REGIME_1 | WATER_STANDARD | 0.45-0.55 |
| 3rd (seething) | REGIME_3 | OIL_RESIN | 0.65-0.75 |
| 4th (precision) | REGIME_4 | PRECISION | 0.55-0.65 |
"""

import json
from pathlib import Path
from collections import defaultdict

# ============================================================
# REGIME ASSIGNMENT RULES
# ============================================================

# Base assignment from fire degree
FIRE_TO_REGIME = {
    1: ('REGIME_2', 'WATER_GENTLE'),
    2: ('REGIME_1', 'WATER_STANDARD'),
    3: ('REGIME_3', 'OIL_RESIN'),
    4: ('REGIME_4', 'PRECISION'),
}

# CEI ranges by REGIME (Constraint Energy Index)
CEI_RANGES = {
    'REGIME_1': (0.45, 0.55),
    'REGIME_2': (0.30, 0.40),
    'REGIME_3': (0.65, 0.75),
    'REGIME_4': (0.55, 0.65),
}

# Expected PREFIX profile by REGIME
PREFIX_PROFILES = {
    'REGIME_1': {'da': 0.35, 'ol': 0.25, 'qo': 0.20, 'other': 0.20},
    'REGIME_2': {'ol': 0.40, 'da': 0.30, 'qo': 0.15, 'other': 0.15},
    'REGIME_3': {'qo': 0.35, 'da': 0.30, 'ol': 0.20, 'other': 0.15},
    'REGIME_4': {'da': 0.40, 'qo': 0.30, 'ol': 0.20, 'other': 0.10},
}

# ============================================================
# DISCRIMINATOR FUNCTIONS
# ============================================================

def compute_monitoring_intensity(sequence):
    """Compute ratio of LINK operations to total."""
    if not sequence:
        return 0.0
    link_count = sum(1 for s in sequence if s == 'LINK')
    return link_count / len(sequence)

def compute_recovery_presence(sequence):
    """Check if recovery operations are present."""
    return 'RECOVERY' in sequence if sequence else False

def compute_hazard_ratio(sequence):
    """Compute ratio of hazard operations to total."""
    if not sequence:
        return 0.0
    hazard_count = sum(1 for s in sequence if s == 'h_HAZARD')
    return hazard_count / len(sequence)

def compute_energy_ratio(sequence):
    """Compute ratio of energy operations to total."""
    if not sequence:
        return 0.0
    energy_count = sum(1 for s in sequence if s == 'k_ENERGY')
    return energy_count / len(sequence)

def estimate_precision_requirement(material):
    """Estimate precision requirement based on procedure characteristics."""
    sequence = material.get('instruction_sequence', [])

    # Factors that increase precision requirement:
    # - High monitoring intensity
    # - Recovery presence
    # - Long procedure
    # - Multiple different instruction types

    score = 0

    # Monitoring intensity
    monitoring = compute_monitoring_intensity(sequence)
    if monitoring > 0.2:
        score += 2
    elif monitoring > 0.1:
        score += 1

    # Recovery presence
    if compute_recovery_presence(sequence):
        score += 1

    # Procedure length
    if len(sequence) >= 6:
        score += 1

    # Instruction variety
    unique_types = len(set(s for s in sequence if s != 'UNKNOWN'))
    if unique_types >= 4:
        score += 1

    # Classify
    if score >= 4:
        return 'CRITICAL'
    elif score >= 3:
        return 'HIGH'
    elif score >= 2:
        return 'MODERATE'
    else:
        return 'LOW'

def estimate_duration_class(material):
    """Estimate duration class from procedure length."""
    steps = len(material.get('procedural_steps', []))

    if steps >= 8:
        return 'EXTENDED'
    elif steps >= 5:
        return 'LONG'
    elif steps >= 3:
        return 'MEDIUM'
    else:
        return 'SHORT'

def compute_cei(material):
    """Compute estimated Constraint Energy Index."""
    sequence = material.get('instruction_sequence', [])

    if not sequence:
        return 0.5  # Default middle value

    # CEI correlates with:
    # - Energy/hazard operations (increases CEI)
    # - Escape operations (decreases CEI)
    # - Monitoring (slight decrease)

    energy_ratio = compute_energy_ratio(sequence)
    hazard_ratio = compute_hazard_ratio(sequence)
    monitoring = compute_monitoring_intensity(sequence)

    escape_count = sum(1 for s in sequence if s == 'e_ESCAPE')
    escape_ratio = escape_count / len(sequence) if sequence else 0

    # Simple CEI estimation
    cei = 0.5 + (energy_ratio * 0.3) + (hazard_ratio * 0.2) - (escape_ratio * 0.2) - (monitoring * 0.1)

    # Clamp to valid range
    return max(0.1, min(0.9, cei))

# ============================================================
# REGIME OVERRIDE LOGIC
# ============================================================

def assign_regime(material):
    """
    Assign REGIME based on fire degree with precision override.

    C494: REGIME_4 = precision, not intensity
    If precision requirement is HIGH or CRITICAL, override to REGIME_4
    regardless of fire degree.
    """
    fire_degree = material.get('fire_degree', 2)
    base_regime, base_product = FIRE_TO_REGIME.get(fire_degree, ('REGIME_1', 'WATER_STANDARD'))

    # Compute discriminators
    precision = estimate_precision_requirement(material)
    duration = estimate_duration_class(material)
    cei = compute_cei(material)
    monitoring = compute_monitoring_intensity(material.get('instruction_sequence', []))

    # Override logic: High precision moves to REGIME_4
    final_regime = base_regime
    final_product = base_product
    override_reason = None

    if precision in ['HIGH', 'CRITICAL'] and base_regime != 'REGIME_4':
        final_regime = 'REGIME_4'
        final_product = 'PRECISION'
        override_reason = f'precision_override ({precision})'

    # Compute predicted PREFIX profile
    predicted_prefix = PREFIX_PROFILES.get(final_regime, PREFIX_PROFILES['REGIME_1'])

    return {
        'base_regime': base_regime,
        'base_product_type': base_product,
        'final_regime': final_regime,
        'final_product_type': final_product,
        'override_reason': override_reason,
        'precision_requirement': precision,
        'duration_class': duration,
        'estimated_cei': round(cei, 3),
        'monitoring_intensity': round(monitoring, 3),
        'predicted_prefix_profile': predicted_prefix
    }

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PHASE 5: REGIME ASSIGNMENT")
print("=" * 70)
print()

# Load materials database
with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

materials = data['materials']
print(f"Loaded {len(materials)} materials")
print()

# ============================================================
# ASSIGN REGIMES
# ============================================================

print("=" * 70)
print("ASSIGNING REGIMES")
print("=" * 70)
print()

regime_counts = defaultdict(int)
product_counts = defaultdict(int)
override_count = 0
precision_dist = defaultdict(int)
duration_dist = defaultdict(int)

for material in materials:
    assignment = assign_regime(material)

    # Update material
    material['regime_assignment'] = assignment

    # Count
    regime_counts[assignment['final_regime']] += 1
    product_counts[assignment['final_product_type']] += 1
    precision_dist[assignment['precision_requirement']] += 1
    duration_dist[assignment['duration_class']] += 1

    if assignment['override_reason']:
        override_count += 1

print(f"Total materials assigned: {len(materials)}")
print(f"Precision overrides to REGIME_4: {override_count}")
print()

# ============================================================
# REGIME DISTRIBUTION
# ============================================================

print("=" * 70)
print("REGIME DISTRIBUTION")
print("=" * 70)
print()

print("By REGIME:")
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    count = regime_counts[regime]
    pct = 100 * count / len(materials)
    print(f"  {regime}: {count} ({pct:.1f}%)")

print()
print("By product type:")
for product in ['WATER_STANDARD', 'WATER_GENTLE', 'OIL_RESIN', 'PRECISION']:
    count = product_counts[product]
    pct = 100 * count / len(materials)
    print(f"  {product}: {count} ({pct:.1f}%)")

print()
print("By precision requirement:")
for prec in ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']:
    count = precision_dist[prec]
    pct = 100 * count / len(materials)
    print(f"  {prec}: {count} ({pct:.1f}%)")

print()
print("By duration class:")
for dur in ['SHORT', 'MEDIUM', 'LONG', 'EXTENDED']:
    count = duration_dist[dur]
    pct = 100 * count / len(materials)
    print(f"  {dur}: {count} ({pct:.1f}%)")

# ============================================================
# CEI ANALYSIS
# ============================================================

print()
print("=" * 70)
print("CEI ANALYSIS")
print("=" * 70)
print()

# Group CEI by REGIME
cei_by_regime = defaultdict(list)
for m in materials:
    regime = m['regime_assignment']['final_regime']
    cei = m['regime_assignment']['estimated_cei']
    cei_by_regime[regime].append(cei)

print("Mean CEI by REGIME:")
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    ceis = cei_by_regime[regime]
    if ceis:
        mean_cei = sum(ceis) / len(ceis)
        expected_low, expected_high = CEI_RANGES[regime]
        in_range = expected_low <= mean_cei <= expected_high
        status = "IN RANGE" if in_range else "OUT OF RANGE"
        print(f"  {regime}: {mean_cei:.3f} (expected {expected_low}-{expected_high}) - {status}")
    else:
        print(f"  {regime}: no materials")

# ============================================================
# CROSS-TABULATION: FIRE DEGREE vs REGIME
# ============================================================

print()
print("=" * 70)
print("FIRE DEGREE vs FINAL REGIME")
print("=" * 70)
print()

crosstab = defaultdict(lambda: defaultdict(int))
for m in materials:
    fd = m.get('fire_degree', 0)
    regime = m['regime_assignment']['final_regime']
    crosstab[fd][regime] += 1

print("Fire Degree  | REGIME_1 | REGIME_2 | REGIME_3 | REGIME_4")
print("-" * 60)
for fd in sorted(crosstab.keys()):
    row = crosstab[fd]
    print(f"    {fd}        |    {row['REGIME_1']:3d}   |    {row['REGIME_2']:3d}   |    {row['REGIME_3']:3d}   |    {row['REGIME_4']:3d}")

# ============================================================
# SAVE UPDATED DATABASE
# ============================================================

print()
print("=" * 70)
print("SAVING UPDATED DATABASE")
print("=" * 70)
print()

# Update summary
data['summary']['regime_assignment'] = {
    'by_regime': dict(regime_counts),
    'by_product_type': dict(product_counts),
    'by_precision': dict(precision_dist),
    'by_duration': dict(duration_dist),
    'precision_overrides': override_count
}

# Save
output_path = Path('data/brunschwig_materials_master.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated database saved to {output_path}")

# ============================================================
# SAMPLE OUTPUT
# ============================================================

print()
print("=" * 70)
print("SAMPLE REGIME ASSIGNMENTS")
print("=" * 70)
print()

# Sample from each regime
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    samples = [m for m in materials if m['regime_assignment']['final_regime'] == regime][:2]
    print(f"{regime}:")
    for m in samples:
        ra = m['regime_assignment']
        name = m['name_normalized']
        print(f"  {m['recipe_id']}: {name}")
        print(f"    Fire degree: {m['fire_degree']}, Product: {ra['final_product_type']}")
        print(f"    Precision: {ra['precision_requirement']}, Duration: {ra['duration_class']}")
        print(f"    CEI: {ra['estimated_cei']}, Monitoring: {ra['monitoring_intensity']}")
        if ra['override_reason']:
            print(f"    Override: {ra['override_reason']}")
    print()
