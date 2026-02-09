"""
00_compute_brunschwig_signatures.py

GATE SCRIPT: Compute Voynich-compatible signatures for all 245 Brunschwig recipes.

For each recipe, compute predicted Voynich structural signature based on:
- Fire degree → REGIME mapping
- Material class → handling type
- Procedural steps → instruction pattern prediction
- Method → kernel expectations

This creates the comparison basis for multi-dimensional matching.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

# Paths
data_dir = Path(__file__).parent.parent.parent.parent / "data"
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

print("="*70)
print("BRUNSCHWIG SIGNATURE COMPUTATION")
print("="*70)

# Load Brunschwig recipes
with open(data_dir / "brunschwig_curated_v3.json", encoding='utf-8') as f:
    brunschwig = json.load(f)

recipes = brunschwig['recipes']
print(f"Loaded {len(recipes)} Brunschwig recipes")

# Fire Degree → REGIME Mapping (from BRSC)
FIRE_TO_REGIME = {
    1: 2,  # Gentle (balneum marie) → REGIME_2
    2: 1,  # Standard → REGIME_1
    3: 3,  # Intense → REGIME_3
    4: 4,  # Precision → REGIME_4
}

# Material class → expected handling
MATERIAL_HANDLING = {
    'herb': {'handling': 'standard', 'suffix_expectation': 'medium'},
    'hot_dry_herb': {'handling': 'careful', 'suffix_expectation': 'low'},
    'moderate_herb': {'handling': 'standard', 'suffix_expectation': 'medium'},
    'hot_flower': {'handling': 'gentle', 'suffix_expectation': 'high'},
    'cold_flower': {'handling': 'gentle', 'suffix_expectation': 'high'},
    'flower': {'handling': 'gentle', 'suffix_expectation': 'high'},
    'moist_root': {'handling': 'standard', 'suffix_expectation': 'medium'},
    'hot_dry_root': {'handling': 'careful', 'suffix_expectation': 'low'},
    'root': {'handling': 'standard', 'suffix_expectation': 'medium'},
    'animal': {'handling': 'precision', 'suffix_expectation': 'high'},
    'fruit': {'handling': 'standard', 'suffix_expectation': 'medium'},
    'gum_resin': {'handling': 'intense', 'suffix_expectation': 'low'},
    'unknown': {'handling': 'standard', 'suffix_expectation': 'medium'},
}

# Procedural action → expected instruction role
ACTION_TO_ROLE = {
    'GATHER': 'CC',      # Control/setup
    'STRIP': 'EN',       # Energy transformation
    'BREAK': 'EN',       # Energy transformation
    'BORE': 'EN',        # Energy extraction
    'CHOP': 'EN',        # Energy work
    'POUND': 'EN',       # Energy work
    'PLUCK': 'EN',       # Preparation (animal)
    'WASH': 'CC',        # Control/validation
    'DISTILL': 'FQ',     # Frequent operation
    'COLLECT': 'FL',     # Flow operation
    'STEEP': 'EN',       # Energy work
}

# Method → kernel expectations
METHOD_KERNELS = {
    'balneum marie': {'e': 0.6, 'h': 0.1, 'k': 0.3},   # High cooling/equilibration
    'per cinerem': {'e': 0.3, 'h': 0.3, 'k': 0.4},     # Balanced
    'per arenam': {'e': 0.2, 'h': 0.3, 'k': 0.5},      # Higher k
    'per ignem': {'e': 0.1, 'h': 0.4, 'k': 0.5},       # High k+h
    'per alembicum': {'e': 0.3, 'h': 0.3, 'k': 0.4},   # Standard
    'sonnenschein': {'e': 0.5, 'h': 0.2, 'k': 0.3},    # Gentle, e-dominant
    'ross mist': {'e': 0.5, 'h': 0.2, 'k': 0.3},       # Gentle sustained
}

def compute_signature(recipe):
    """Compute predicted Voynich signature for a Brunschwig recipe."""

    sig = {
        'recipe_id': recipe['id'],
        'name_english': recipe.get('name_english', 'unknown'),
        'material_class': recipe.get('material_class', 'unknown'),
    }

    # Fire degree → REGIME
    fire_degree = recipe.get('fire_degree')
    if fire_degree:
        sig['fire_degree'] = fire_degree
        sig['expected_regime'] = FIRE_TO_REGIME.get(fire_degree, 1)
    else:
        sig['fire_degree'] = None
        sig['expected_regime'] = 1  # Default

    # Material handling
    mat_class = recipe.get('material_class', 'unknown')
    handling = MATERIAL_HANDLING.get(mat_class, MATERIAL_HANDLING['unknown'])
    sig['handling_type'] = handling['handling']
    sig['suffix_expectation'] = handling['suffix_expectation']

    # Procedural steps → role pattern
    steps = recipe.get('procedural_steps') or []
    role_sequence = []
    role_counts = Counter()

    for step in steps:
        action = step.get('action', '')
        role = ACTION_TO_ROLE.get(action, 'AX')  # Default to AUX
        role_sequence.append(role)
        role_counts[role] += 1

    sig['role_sequence'] = role_sequence
    sig['role_counts'] = dict(role_counts)
    sig['n_steps'] = len(steps)

    # Compute role profile (proportions)
    total_steps = len(role_sequence) if role_sequence else 1
    sig['role_profile'] = {
        role: count / total_steps
        for role, count in role_counts.items()
    }

    # Method → kernel expectations
    method = recipe.get('method', '')
    if method:
        method_lower = method.lower()
        kernel_exp = None
        for method_key, kernels in METHOD_KERNELS.items():
            if method_key in method_lower:
                kernel_exp = kernels
                break
        if kernel_exp is None:
            kernel_exp = METHOD_KERNELS['per alembicum']  # Default
    else:
        kernel_exp = METHOD_KERNELS['per alembicum']

    sig['kernel_expectation'] = kernel_exp

    # Prefix profile prediction based on fire degree and handling
    prefix_profile = predict_prefix_profile(fire_degree, handling['handling'], mat_class)
    sig['prefix_profile'] = prefix_profile

    # LINK expectation based on fire degree
    if fire_degree == 1:
        sig['link_expectation'] = 'high'  # Continuous monitoring
    elif fire_degree == 2:
        sig['link_expectation'] = 'medium'
    elif fire_degree == 3:
        sig['link_expectation'] = 'low'  # Less monitoring needed
    else:
        sig['link_expectation'] = 'high'  # Precision requires monitoring

    return sig

def predict_prefix_profile(fire_degree, handling, material_class):
    """Predict expected PREFIX distribution based on Brunschwig parameters."""

    # Base profile (from BCSC role frequencies)
    profile = {
        'qo': 0.25,   # Common (escape + energy)
        'ch_sh': 0.20,  # Phase/hazard marking
        'ok_ot': 0.15,  # Auxiliary
        'da': 0.10,   # Flow redirect
        'ol_or': 0.10,  # LINK markers
        'other': 0.20,
    }

    # Adjust based on fire degree
    if fire_degree == 1:  # Gentle
        profile['qo'] = 0.20
        profile['ol_or'] = 0.25  # More monitoring
        profile['ch_sh'] = 0.15
    elif fire_degree == 3:  # Intense
        profile['qo'] = 0.30
        profile['ch_sh'] = 0.25  # More hazard marking
        profile['ol_or'] = 0.05
    elif fire_degree == 4:  # Precision (animal)
        profile['ok_ot'] = 0.25  # More auxiliary
        profile['qo'] = 0.25
        profile['ch_sh'] = 0.20

    # Adjust for animal materials (C536: ESCAPE+AUX pattern)
    if material_class == 'animal':
        profile['qo'] = 0.30  # High escape
        profile['ok_ot'] = 0.25  # High auxiliary
        profile['ch_sh'] = 0.15
        profile['ol_or'] = 0.15

    return profile

# Compute signatures for all recipes
print("\nComputing signatures for all recipes...")
signatures = []

for recipe in recipes:
    sig = compute_signature(recipe)
    signatures.append(sig)

# Summary statistics
print(f"\nComputed {len(signatures)} signatures")

# Distribution by fire degree
fire_dist = Counter(s['fire_degree'] for s in signatures if s['fire_degree'])
print("\nFire degree distribution:")
for degree, count in sorted(fire_dist.items()):
    regime = FIRE_TO_REGIME.get(degree, '?')
    print(f"  Degree {degree} -> REGIME_{regime}: {count} recipes ({100*count/len(signatures):.1f}%)")

# Distribution by material class
material_dist = Counter(s['material_class'] for s in signatures)
print("\nMaterial class distribution:")
for mat, count in material_dist.most_common(10):
    print(f"  {mat}: {count} ({100*count/len(signatures):.1f}%)")

# Distribution by handling type
handling_dist = Counter(s['handling_type'] for s in signatures)
print("\nHandling type distribution:")
for handling, count in handling_dist.most_common():
    print(f"  {handling}: {count} ({100*count/len(signatures):.1f}%)")

# Average role profile
print("\nAggregate role profile (from procedural steps):")
agg_roles = Counter()
total_steps = 0
for sig in signatures:
    for role, count in sig['role_counts'].items():
        agg_roles[role] += count
        total_steps += count

if total_steps > 0:
    for role, count in agg_roles.most_common():
        print(f"  {role}: {count} ({100*count/total_steps:.1f}%)")
else:
    print("  No procedural steps found")

# Animal materials detail
print("\n" + "="*70)
print("ANIMAL MATERIAL SIGNATURES (Priority for mapping)")
print("="*70)

animal_sigs = [s for s in signatures if s['material_class'] == 'animal']
for sig in animal_sigs:
    print(f"\n{sig['name_english']}:")
    print(f"  Fire degree: {sig['fire_degree']} -> REGIME_{sig['expected_regime']}")
    print(f"  Handling: {sig['handling_type']}")
    print(f"  Role sequence: {' -> '.join(sig['role_sequence']) if sig['role_sequence'] else 'none'}")
    print(f"  Kernel expectation: e={sig['kernel_expectation']['e']:.1f}, h={sig['kernel_expectation']['h']:.1f}, k={sig['kernel_expectation']['k']:.1f}")
    print(f"  PREFIX prediction: qo={sig['prefix_profile']['qo']:.2f}, ok_ot={sig['prefix_profile']['ok_ot']:.2f}")

# Save signatures
output = {
    'total_recipes': len(signatures),
    'fire_degree_mapping': FIRE_TO_REGIME,
    'material_handling': MATERIAL_HANDLING,
    'action_role_mapping': ACTION_TO_ROLE,
    'method_kernels': METHOD_KERNELS,
    'signatures': signatures,
    'distributions': {
        'fire_degree': dict(fire_dist),
        'material_class': dict(material_dist),
        'handling_type': dict(handling_dist),
        'aggregate_roles': dict(agg_roles),
    }
}

output_path = results_dir / "brunschwig_signatures.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {output_path}")

print("\n" + "="*70)
print("GATE COMPLETE - Signatures computed for multi-dimensional matching")
print("="*70)
