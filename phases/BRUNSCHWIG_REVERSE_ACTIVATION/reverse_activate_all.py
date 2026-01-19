#!/usr/bin/env python3
"""
BRUNSCHWIG REVERSE ACTIVATION

Process ALL 197 Brunschwig recipes through AZC/Currier A reverse activation pipeline.

Valid mapping path (respecting C384 - no entry-level A-B coupling):
    Recipe -> REGIME -> Zone Compatibility -> MIDDLE Vocabulary -> Statistical A Profile

Outputs:
    - Zone affinity (C/P/R/S) per recipe
    - Legal MIDDLE vocabulary per recipe
    - Vocabulary fingerprint (hub_ratio, tail_pressure)
    - Aggregate folio distribution prediction
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

# ============================================================
# LOAD ALL DATA SOURCES
# ============================================================

print("=" * 70)
print("BRUNSCHWIG REVERSE ACTIVATION - COMPREHENSIVE")
print("=" * 70)
print()

print("Loading data sources...")

# 1. Brunschwig recipes
with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
    brunschwig = json.load(f)

materials = brunschwig['materials']
recipes = [m for m in materials if m.get('procedural_steps')]
print(f"  Brunschwig recipes with procedures: {len(recipes)}")

# 2. MIDDLE zone legality
with open('results/middle_zone_legality.json', 'r') as f:
    zone_legality = json.load(f)
print(f"  MIDDLEs with zone data: {len(zone_legality)}")

# 3. MIDDLE zone survival clusters
with open('results/middle_zone_survival.json', 'r') as f:
    zone_survival = json.load(f)
print(f"  Zone survival clusters: {len(zone_survival['clustering']['clusters'])}")

# 4. MIDDLE incompatibility graph
with open('results/middle_incompatibility.json', 'r') as f:
    incompatibility = json.load(f)
print(f"  Total MIDDLEs in incompatibility graph: {incompatibility['summary']['total_middles']}")
print(f"  Illegal pairs: {incompatibility['summary']['illegal_pairs']} ({incompatibility['summary']['sparsity']*100:.1f}% sparsity)")

# 5. Unified folio profiles
with open('results/unified_folio_profiles.json', 'r') as f:
    folio_profiles = json.load(f)
profiles = folio_profiles['profiles']
b_folios = {k: v for k, v in profiles.items() if v.get('system') == 'B'}
print(f"  B folios: {len(b_folios)}")

# 6. AZC escape by position
with open('results/azc_escape_by_position.json', 'r') as f:
    escape_rates = json.load(f)
print(f"  Escape rate positions: {len(escape_rates)}")

# Extract hub MIDDLEs from incompatibility graph (high-connectivity nodes)
# The giant component contains the most connected MIDDLEs
giant_component = incompatibility['graph_analysis']['components'][0]
hub_middles = set(giant_component[:50])  # Top 50 in giant component are hubs
print(f"  Hub MIDDLEs identified: {len(hub_middles)}")

print()

# ============================================================
# EXTRACT ZONE SURVIVAL CLUSTER PROFILES
# ============================================================

# Build cluster profiles for zone affinity matching
cluster_profiles = {}
for cluster_id, cluster_data in zone_survival['clustering']['clusters'].items():
    cluster_profiles[cluster_id] = {
        'dominant_zone': cluster_data['dominant_zone'],
        'profile': cluster_data['mean_profile'],
        'middles': set(cluster_data['example_middles'])
    }

# Zone reference escape rates (from azc_escape_by_position)
zone_escape_ref = {
    'C': 0.0234,   # Entry zone, suppressed
    'P': 0.1587,   # Highest escape (permissive)
    'R': 0.053,    # Moderate (interior)
    'S': 0.0       # Boundary, zero escape
}

# ============================================================
# CORE FUNCTIONS
# ============================================================

def compute_recipe_metrics(recipe):
    """
    Extract metrics from each recipe's procedural steps.
    """
    steps = recipe.get('procedural_steps', [])
    n_steps = len(steps)

    if n_steps == 0:
        return None

    hazard_count = 0
    escape_count = 0
    link_count = 0
    intervention_count = 0
    recovery_count = 0

    instruction_profile = Counter()
    sensory_profile = Counter()
    hazard_classes = set()

    for step in steps:
        # Instruction class
        inst_class = step.get('instruction_class', 'UNKNOWN')
        instruction_profile[inst_class] += 1

        # Map to metric components
        if 'HAZARD' in inst_class or inst_class == 'h_HAZARD':
            hazard_count += 1
        if inst_class == 'e_ESCAPE':
            escape_count += 1
        if inst_class == 'LINK':
            link_count += 1
        if inst_class == 'RECOVERY':
            recovery_count += 1

        # Hazard exposure
        hazard = step.get('hazard_exposure', 'NONE')
        if hazard and hazard != 'NONE':
            hazard_classes.add(hazard)
            hazard_count += 1

        # Intervention required
        if step.get('intervention_required'):
            intervention_count += 1

        # Sensory content
        sensory = step.get('sensory_content', {})
        if sensory:
            for modality in ['SIGHT', 'SOUND', 'SMELL', 'TOUCH', 'TASTE']:
                if modality in sensory and sensory[modality]:
                    score = sensory[modality].get('score', 1)
                    if score > 0:
                        sensory_profile[modality] += score

    # Compute densities
    hazard_density = hazard_count / n_steps
    escape_density = escape_count / n_steps
    link_density = link_count / n_steps
    intervention_rate = intervention_count / n_steps
    recovery_rate = recovery_count / n_steps

    # SLI formula: hazard / (escape + link + epsilon)
    sli = hazard_density / (escape_density + link_density + 0.01)

    return {
        'n_steps': n_steps,
        'hazard_density': hazard_density,
        'escape_density': escape_density,
        'link_density': link_density,
        'intervention_rate': intervention_rate,
        'recovery_rate': recovery_rate,
        'sli': sli,
        'instruction_profile': dict(instruction_profile),
        'sensory_profile': dict(sensory_profile),
        'hazard_classes': list(hazard_classes)
    }


def compute_zone_affinity(recipe, metrics):
    """
    Map recipe characteristics to zone affinity scores.

    Zones:
      - C: Interior, rotation-tolerant, escape=2.34%
      - P: Interior, intervention-permitting, escape=15.87%
      - R: Ordered interior, progressive restriction, escape=5.3%-0%
      - S: Boundary, no intervention, escape=0%
    """
    regime = recipe.get('predicted_regime', 'REGIME_1')
    product = recipe.get('predicted_product_type', 'WATER_STANDARD')
    fire_degree = recipe.get('fire_degree', 2)

    # Base zone affinity (uniform)
    affinity = {'C': 0.25, 'P': 0.25, 'R': 0.25, 'S': 0.25}

    # 1. Adjust by intervention rate
    if metrics['intervention_rate'] > 0.5:
        affinity['P'] += 0.20  # Needs permissive zone
        affinity['S'] -= 0.10
    elif metrics['intervention_rate'] < 0.2:
        affinity['S'] += 0.15  # Can handle locked grammar
        affinity['P'] -= 0.10

    # 2. Adjust by SLI (constraint pressure)
    if metrics['sli'] > 2.0:  # High constraint pressure
        affinity['R'] += 0.15  # Sequential processing
        affinity['C'] -= 0.10
    elif metrics['sli'] < 0.5:  # Forgiving process
        affinity['C'] += 0.15  # Setup-focused
        affinity['R'] -= 0.10

    # 3. Adjust by product type
    if product == 'PRECISION':
        affinity['S'] += 0.15  # Boundary control
        affinity['P'] += 0.10  # Needs intervention
        affinity['C'] -= 0.10
    elif product == 'OIL_RESIN':
        affinity['R'] += 0.20  # Sequential processing
        affinity['C'] -= 0.10
    elif product == 'WATER_GENTLE':
        affinity['C'] += 0.15  # Setup-focused
        affinity['R'] -= 0.05

    # 4. Adjust by REGIME
    if regime == 'REGIME_3':  # Full execution (recovery completeness)
        affinity['R'] += 0.10
        affinity['S'] += 0.10
        affinity['P'] -= 0.10
    elif regime == 'REGIME_4':  # Precision (monitoring completeness)
        affinity['P'] += 0.15  # High monitoring needs
        affinity['S'] += 0.10
        affinity['C'] -= 0.10
    elif regime == 'REGIME_2':  # Learn basics (simple)
        affinity['C'] += 0.15
        affinity['R'] -= 0.10

    # 5. Adjust by fire degree
    if fire_degree == 4:  # Most intense
        affinity['S'] += 0.10  # Boundary critical
        affinity['C'] -= 0.10
    elif fire_degree == 1:  # Gentle
        affinity['C'] += 0.10
        affinity['S'] -= 0.05

    # Normalize to sum=1
    total = sum(affinity.values())
    affinity = {z: max(0, v/total) for z, v in affinity.items()}

    return affinity


def compute_vocabulary_fingerprint(zone_affinity):
    """
    Filter legal MIDDLE vocabulary by zone affinity and compute fingerprint.
    """
    # Score each MIDDLE by zone compatibility
    middle_scores = {}
    for middle, data in zone_legality.items():
        counts = data['counts']
        total = data['total']
        if total < 3:  # Skip very low frequency
            continue

        # Weighted score based on zone affinity
        score = sum(
            zone_affinity.get(zone, 0) * counts.get(zone, 0) / total
            for zone in ['C', 'P', 'R', 'S']
        )
        middle_scores[middle] = score

    # Threshold for "legal"
    threshold = 0.10  # At least 10% weighted compatibility
    legal_middles = {m for m, s in middle_scores.items() if s >= threshold}

    # Compute fingerprint
    n_legal = len(legal_middles)
    if n_legal == 0:
        return set(), {
            'n_legal': 0,
            'hub_ratio': 0,
            'tail_pressure': 1.0,
            'zone_specificity': 0
        }

    n_hubs = len(legal_middles & hub_middles)

    # Tail pressure: proportion of rare/isolated MIDDLEs
    # More hubs = lower tail pressure (common vocabulary)
    # Fewer hubs = higher tail pressure (specialized vocabulary)
    fingerprint = {
        'n_legal': n_legal,
        'hub_ratio': n_hubs / n_legal,
        'tail_pressure': 1.0 - (n_hubs / n_legal),
        'zone_specificity': max(zone_affinity.values()) - min(zone_affinity.values())
    }

    return legal_middles, fingerprint


def predict_folio_distribution(recipe, zone_affinity, fingerprint, metrics):
    """
    Predict which B folios this recipe might activate.
    Uses AGGREGATE matching, not entry-level (per C384).
    """
    regime = recipe.get('predicted_regime', 'REGIME_1')

    folio_scores = {}
    for folio_id, profile in b_folios.items():
        b_metrics = profile.get('b_metrics', {})
        if not b_metrics:
            continue

        folio_regime = b_metrics.get('regime', 'UNKNOWN')

        # Base score from regime match
        score = 1.0 if folio_regime == regime else 0.3

        # Adjust by SLI similarity
        recipe_sli = metrics['sli']
        folio_hazard = b_metrics.get('hazard_density', 0.5)
        folio_escape = b_metrics.get('escape_density', 0.1)
        folio_link = b_metrics.get('link_density', 0.1)
        folio_sli = folio_hazard / (folio_escape + folio_link + 0.01)

        sli_diff = abs(recipe_sli - folio_sli)
        score *= max(0.1, 1.0 - sli_diff / 10.0)

        # Adjust by zone affinity alignment
        # P-affinity recipes should match high-escape folios
        if zone_affinity.get('P', 0) > 0.3:
            score *= (1 + folio_escape * 2)

        # S-affinity recipes should match low-escape, boundary folios
        if zone_affinity.get('S', 0) > 0.3:
            score *= max(0.1, 1.0 - folio_link)

        # R-affinity should match moderate folios
        if zone_affinity.get('R', 0) > 0.4:
            score *= (1 + folio_hazard)

        folio_scores[folio_id] = score

    # Normalize to distribution
    total = sum(folio_scores.values())
    if total > 0:
        folio_scores = {k: v/total for k, v in folio_scores.items()}

    # Get top 10 predicted folios
    top_folios = sorted(folio_scores.items(), key=lambda x: -x[1])[:10]

    return {
        'regime_match': regime,
        'top_predicted_folios': dict(top_folios),
        'n_folios_scored': len(folio_scores)
    }


# ============================================================
# PROCESS ALL 197 RECIPES
# ============================================================

print("=" * 70)
print("PROCESSING ALL RECIPES")
print("=" * 70)
print()

results = []
skipped = 0

for i, recipe in enumerate(recipes):
    recipe_id = recipe.get('recipe_id', f'BRU-{i+1:03d}')
    name = recipe.get('name_normalized', recipe.get('name_german', 'unknown'))

    # Step 1: Compute recipe metrics
    metrics = compute_recipe_metrics(recipe)
    if metrics is None:
        skipped += 1
        continue

    # Step 2: Compute zone affinity
    zone_affinity = compute_zone_affinity(recipe, metrics)

    # Step 3: Compute legal vocabulary and fingerprint
    legal_middles, fingerprint = compute_vocabulary_fingerprint(zone_affinity)

    # Step 4: Predict folio distribution
    folio_prediction = predict_folio_distribution(recipe, zone_affinity, fingerprint, metrics)

    results.append({
        'recipe_id': recipe_id,
        'name': name,
        'predicted_regime': recipe.get('predicted_regime'),
        'predicted_product': recipe.get('predicted_product_type'),
        'fire_degree': recipe.get('fire_degree'),
        'n_steps': metrics['n_steps'],
        'metrics': {
            'sli': metrics['sli'],
            'hazard_density': metrics['hazard_density'],
            'escape_density': metrics['escape_density'],
            'link_density': metrics['link_density'],
            'intervention_rate': metrics['intervention_rate'],
            'recovery_rate': metrics['recovery_rate']
        },
        'sensory_profile': metrics['sensory_profile'],
        'instruction_profile': metrics['instruction_profile'],
        'zone_affinity': zone_affinity,
        'vocabulary_fingerprint': fingerprint,
        'folio_prediction': folio_prediction
    })

    if (i + 1) % 50 == 0:
        print(f"  Processed {i + 1}/{len(recipes)} recipes...")

print()
print(f"Total recipes processed: {len(results)}")
print(f"Recipes skipped (no steps): {skipped}")

# ============================================================
# COMPUTE SUMMARY STATISTICS
# ============================================================

print()
print("=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)
print()

# SLI statistics
sli_values = [r['metrics']['sli'] for r in results]
print(f"SLI Statistics (n={len(sli_values)}):")
print(f"  Mean: {np.mean(sli_values):.3f}")
print(f"  Std:  {np.std(sli_values):.3f}")
print(f"  Min:  {np.min(sli_values):.3f}")
print(f"  Max:  {np.max(sli_values):.3f}")

# Zone affinity statistics
zone_means = defaultdict(list)
for r in results:
    for zone, aff in r['zone_affinity'].items():
        zone_means[zone].append(aff)

print()
print("Zone Affinity Means:")
for zone in ['C', 'P', 'R', 'S']:
    values = zone_means[zone]
    print(f"  {zone}: {np.mean(values):.3f} +/- {np.std(values):.3f}")

# Vocabulary fingerprint statistics
fingerprint_stats = {
    'n_legal': [r['vocabulary_fingerprint']['n_legal'] for r in results],
    'hub_ratio': [r['vocabulary_fingerprint']['hub_ratio'] for r in results],
    'tail_pressure': [r['vocabulary_fingerprint']['tail_pressure'] for r in results]
}

print()
print("Vocabulary Fingerprint Statistics:")
for metric, values in fingerprint_stats.items():
    print(f"  {metric}: {np.mean(values):.3f} +/- {np.std(values):.3f}")

# By REGIME
regime_groups = defaultdict(list)
for r in results:
    regime_groups[r['predicted_regime']].append(r)

print()
print("By REGIME:")
for regime in sorted(regime_groups.keys()):
    group = regime_groups[regime]
    sli_vals = [r['metrics']['sli'] for r in group]
    tail_vals = [r['vocabulary_fingerprint']['tail_pressure'] for r in group]
    print(f"  {regime}: n={len(group)}, SLI={np.mean(sli_vals):.2f}, tail_pressure={np.mean(tail_vals):.2f}")

# Sensory profile statistics
sensory_counts = Counter()
for r in results:
    for modality, score in r['sensory_profile'].items():
        if score > 0:
            sensory_counts[modality] += 1

print()
print("Recipes by Sensory Modality:")
for modality, count in sensory_counts.most_common():
    print(f"  {modality}: {count} recipes ({count/len(results)*100:.1f}%)")

# ============================================================
# CORRELATION TESTS
# ============================================================

print()
print("=" * 70)
print("CORRELATION TESTS")
print("=" * 70)
print()

# Test 1: SLI vs tail_pressure
sli_vals = [r['metrics']['sli'] for r in results]
tail_vals = [r['vocabulary_fingerprint']['tail_pressure'] for r in results]
r_sli_tail, p_sli_tail = stats.pearsonr(sli_vals, tail_vals)
print(f"SLI vs tail_pressure: r={r_sli_tail:.4f}, p={p_sli_tail:.4f}")

# Test 2: SLI vs P-zone affinity
p_aff = [r['zone_affinity']['P'] for r in results]
r_sli_p, p_sli_p = stats.pearsonr(sli_vals, p_aff)
print(f"SLI vs P-affinity: r={r_sli_p:.4f}, p={p_sli_p:.4f}")

# Test 3: SLI vs R-zone affinity
r_aff = [r['zone_affinity']['R'] for r in results]
r_sli_r, p_sli_r = stats.pearsonr(sli_vals, r_aff)
print(f"SLI vs R-affinity: r={r_sli_r:.4f}, p={p_sli_r:.4f}")

# Test 4: tail_pressure vs predicted HT
predicted_ht = []
for r in results:
    top_folios = r['folio_prediction']['top_predicted_folios']
    avg_ht = sum(
        profiles.get(f, {}).get('ht_density', 0) * w
        for f, w in top_folios.items()
    )
    predicted_ht.append(avg_ht)

r_tail_ht, p_tail_ht = stats.pearsonr(tail_vals, predicted_ht)
print(f"tail_pressure vs predicted_HT: r={r_tail_ht:.4f}, p={p_tail_ht:.4f}")

# ============================================================
# SAVE RESULTS
# ============================================================

print()
print("=" * 70)
print("SAVING RESULTS")
print("=" * 70)
print()

output = {
    'phase': 'BRUNSCHWIG_REVERSE_ACTIVATION',
    'tier': 3,
    'n_recipes_processed': len(results),
    'n_recipes_total': len(recipes),
    'n_skipped': skipped,
    'processing_date': '2026-01-19',

    'summary_statistics': {
        'sli': {
            'mean': float(np.mean(sli_values)),
            'std': float(np.std(sli_values)),
            'min': float(np.min(sli_values)),
            'max': float(np.max(sli_values))
        },
        'zone_affinity_means': {
            zone: float(np.mean(zone_means[zone]))
            for zone in ['C', 'P', 'R', 'S']
        },
        'vocabulary_fingerprint_means': {
            metric: float(np.mean(values))
            for metric, values in fingerprint_stats.items()
        }
    },

    'by_regime': {
        regime: {
            'n': len(group),
            'mean_sli': float(np.mean([r['metrics']['sli'] for r in group])),
            'mean_tail_pressure': float(np.mean([r['vocabulary_fingerprint']['tail_pressure'] for r in group])),
            'zone_affinity_means': {
                zone: float(np.mean([r['zone_affinity'][zone] for r in group]))
                for zone in ['C', 'P', 'R', 'S']
            }
        }
        for regime, group in regime_groups.items()
    },

    'sensory_modality_counts': dict(sensory_counts),

    'correlation_tests': {
        'sli_tail_pressure': {'r': float(r_sli_tail), 'p': float(p_sli_tail)},
        'sli_P_affinity': {'r': float(r_sli_p), 'p': float(p_sli_p)},
        'sli_R_affinity': {'r': float(r_sli_r), 'p': float(p_sli_r)},
        'tail_pressure_predicted_HT': {'r': float(r_tail_ht), 'p': float(p_tail_ht)}
    },

    'recipes': results
}

output_path = Path('results/brunschwig_reverse_activation.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"Results saved to {output_path}")
print(f"  Total recipes: {len(results)}")
print(f"  File size: ~{output_path.stat().st_size // 1024} KB")

# ============================================================
# CONCLUSION
# ============================================================

print()
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
print()

print(f"REVERSE ACTIVATION COMPLETE")
print(f"  Recipes processed: {len(results)}/{len(recipes)} (100%)")
print()
print("Key Findings:")
print(f"  SLI range: {np.min(sli_values):.2f} - {np.max(sli_values):.2f}")
print(f"  SLI-tail_pressure: r={r_sli_tail:.3f} (p={p_sli_tail:.4f})")
print(f"  tail_pressure-HT: r={r_tail_ht:.3f} (p={p_tail_ht:.4f})")
print()
print("Zone Affinity Patterns by REGIME:")
for regime in sorted(regime_groups.keys()):
    group = regime_groups[regime]
    zone_aff = {z: np.mean([r['zone_affinity'][z] for r in group]) for z in ['C', 'P', 'R', 'S']}
    dominant = max(zone_aff, key=zone_aff.get)
    print(f"  {regime}: dominant={dominant} ({zone_aff[dominant]:.2f})")

print()
print("Next: Run sensory_granularity_test.py for detailed sensory analysis")
