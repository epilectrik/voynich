"""
Extract grammar posture metrics for each Brunschwig recipe.

Maps recipes to REGIMEs via fire_degree, then computes posture metrics
from the B corpus averaged by REGIME.

Metrics:
- prefix_entropy: Diversity of PREFIX distribution
- kernel_proximity: Mean distance to k/h/e operators (approximated)
- infrastructure_density: AUXILIARY-role token density
- link_density: LINK operator frequency
- escape_frequency: e_ESCAPE operator rate
- sli: Sensory Load Index (hazard/(escape+link))
- zone_affinity: C/P/R/S distribution
"""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Fire degree to REGIME mapping (based on F-BRU-002 Degree-REGIME Boundary Asymmetry)
FIRE_DEGREE_TO_REGIME = {
    1: 'REGIME_2',  # Gentle waters (low fire)
    2: 'REGIME_1',  # Standard (moderate fire)
    3: 'REGIME_3',  # Oil/resin (higher fire)
    4: 'REGIME_4',  # Precision (highest fire)
    0: 'REGIME_1',  # Default for missing fire degree
}

# Kernel operators (k, h, e)
KERNEL_PREFIXES = {'ch', 'sh', 'qo', 'da'}  # Energy/hazard/escape/flow approximations

# LINK prefix
LINK_PREFIX = 'ol'

# Infrastructure (AUXILIARY) approximations - ok/ot family
AUXILIARY_PREFIXES = {'ok', 'ot', 'ol'}

def entropy(dist):
    """Compute Shannon entropy of a distribution."""
    total = sum(dist.values())
    if total == 0:
        return 0
    h = 0
    for v in dist.values():
        if v > 0:
            p = v / total
            h -= p * math.log2(p)
    return h

def get_prefix(word):
    """Extract first 2 characters as prefix approximation."""
    if pd.isna(word):
        return ''
    word = str(word)
    if len(word) >= 2:
        return word[:2]
    return word

def load_transcript():
    """Load H-track B corpus transcript."""
    df = pd.read_csv(
        PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
        sep='\t'
    )
    # Filter to H transcriber, language B
    df = df[df['transcriber'] == 'H']
    df = df[df['language'] == 'B']
    # Exclude labels
    df = df[~df['placement'].str.startswith('L')]
    # Remove empty words
    df = df[df['word'].str.strip() != '']
    return df

def compute_regime_postures(df, regime_mapping):
    """Compute posture metrics per REGIME."""
    # Create folio->REGIME mapping
    folio_to_regime = {}
    for regime, folios in regime_mapping.items():
        for folio in folios:
            folio_to_regime[folio] = regime

    # Add REGIME column
    df['regime'] = df['folio'].map(folio_to_regime)

    # Filter to folios with known REGIME
    df_regime = df[df['regime'].notna()].copy()

    postures = {}
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        regime_df = df_regime[df_regime['regime'] == regime]
        if len(regime_df) == 0:
            continue

        tokens = regime_df['word'].tolist()
        total = len(tokens)

        # Prefix distribution
        prefix_counts = Counter(get_prefix(w) for w in tokens)
        prefix_ent = entropy(prefix_counts)

        # Infrastructure (AUXILIARY) density
        aux_count = sum(1 for w in tokens if get_prefix(w) in AUXILIARY_PREFIXES)
        aux_density = aux_count / total if total > 0 else 0

        # LINK density
        link_count = sum(1 for w in tokens if get_prefix(w) == LINK_PREFIX)
        link_density = link_count / total if total > 0 else 0

        # Escape frequency (qo prefix as proxy for escape)
        escape_count = sum(1 for w in tokens if get_prefix(w) == 'qo')
        escape_freq = escape_count / total if total > 0 else 0

        # Hazard frequency (ch/sh as proxy for energy/hazard)
        hazard_count = sum(1 for w in tokens if get_prefix(w) in {'ch', 'sh'})
        hazard_freq = hazard_count / total if total > 0 else 0

        # SLI = hazard / (escape + link)
        denominator = escape_freq + link_density
        sli = hazard_freq / denominator if denominator > 0 else 0

        # Kernel proximity approximation (% of tokens that ARE kernel-adjacent prefixes)
        kernel_adjacent = sum(1 for w in tokens if get_prefix(w) in KERNEL_PREFIXES)
        kernel_proximity = kernel_adjacent / total if total > 0 else 0

        # Zone affinity - requires placement parsing
        zone_counts = Counter()
        for _, row in regime_df.iterrows():
            placement = str(row.get('placement', ''))
            if placement.startswith('C'):
                zone_counts['C'] += 1
            elif placement.startswith('P'):
                zone_counts['P'] += 1
            elif placement.startswith('R'):
                zone_counts['R'] += 1
            elif placement.startswith('S'):
                zone_counts['S'] += 1
            else:
                zone_counts['OTHER'] += 1

        total_zones = sum(zone_counts.values())
        zone_affinity = {z: c/total_zones for z, c in zone_counts.items()} if total_zones > 0 else {}

        postures[regime] = {
            'token_count': total,
            'prefix_entropy': prefix_ent,
            'auxiliary_density': aux_density,
            'link_density': link_density,
            'escape_frequency': escape_freq,
            'hazard_frequency': hazard_freq,
            'sli': sli,
            'kernel_proximity': kernel_proximity,
            'zone_affinity': zone_affinity,
        }

    return postures

def assign_recipe_postures(verb_profiles, regime_postures):
    """Assign REGIME posture metrics to each recipe based on fire_degree."""
    recipe_postures = []

    for profile in verb_profiles:
        fire_degree = profile.get('fire_degree', 0)
        regime = FIRE_DEGREE_TO_REGIME.get(fire_degree, 'REGIME_1')

        if regime not in regime_postures:
            # Skip if REGIME not found
            continue

        posture = regime_postures[regime].copy()
        posture['recipe_id'] = profile['recipe_id']
        posture['recipe_name'] = profile['recipe_name']
        posture['fire_degree'] = fire_degree
        posture['regime'] = regime
        posture['dominant_verb'] = profile['dominant_verb']
        posture['dominant_prep_category'] = profile['dominant_prep_category']
        posture['material_class'] = profile['material_class']

        recipe_postures.append(posture)

    return recipe_postures

def main():
    print("Loading verb profiles...")
    with open(PROJECT_ROOT / 'phases' / 'PREP_POSTURE_DIVERGENCE' / 'results' / 'recipe_verb_profiles.json', 'r') as f:
        verb_data = json.load(f)
    profiles = verb_data['profiles']
    print(f"  Loaded {len(profiles)} recipe profiles")

    print("\nLoading REGIME mapping...")
    with open(PROJECT_ROOT / 'results' / 'regime_folio_mapping.json', 'r') as f:
        regime_mapping = json.load(f)
    for regime, folios in regime_mapping.items():
        print(f"  {regime}: {len(folios)} folios")

    print("\nLoading B corpus transcript...")
    df = load_transcript()
    print(f"  Loaded {len(df)} B tokens (H-track)")

    print("\nComputing REGIME postures...")
    regime_postures = compute_regime_postures(df, regime_mapping)
    for regime, posture in regime_postures.items():
        print(f"\n  {regime}:")
        print(f"    tokens: {posture['token_count']}")
        print(f"    prefix_entropy: {posture['prefix_entropy']:.3f}")
        print(f"    auxiliary_density: {posture['auxiliary_density']:.4f}")
        print(f"    link_density: {posture['link_density']:.4f}")
        print(f"    escape_frequency: {posture['escape_frequency']:.4f}")
        print(f"    hazard_frequency: {posture['hazard_frequency']:.4f}")
        print(f"    sli: {posture['sli']:.4f}")
        print(f"    kernel_proximity: {posture['kernel_proximity']:.4f}")

    print("\nAssigning postures to recipes...")
    recipe_postures = assign_recipe_postures(profiles, regime_postures)
    print(f"  Assigned postures to {len(recipe_postures)} recipes")

    # Summary by dominant verb
    print("\nPosture summary by dominant verb:")
    verb_groups = defaultdict(list)
    for p in recipe_postures:
        verb_groups[p['dominant_verb']].append(p)

    for verb in ['GATHER', 'CHOP', 'STRIP', 'POUND', 'COLLECT', 'WASH']:
        group = verb_groups.get(verb, [])
        if len(group) < 2:
            continue
        avg_aux = sum(p['auxiliary_density'] for p in group) / len(group)
        avg_escape = sum(p['escape_frequency'] for p in group) / len(group)
        avg_sli = sum(p['sli'] for p in group) / len(group)
        print(f"  {verb} (n={len(group)}): aux={avg_aux:.4f}, escape={avg_escape:.4f}, sli={avg_sli:.3f}")

    # Save results
    output = {
        'metadata': {
            'fire_degree_to_regime': FIRE_DEGREE_TO_REGIME,
            'regime_postures': regime_postures,
        },
        'recipe_postures': recipe_postures
    }

    output_path = PROJECT_ROOT / 'phases' / 'PREP_POSTURE_DIVERGENCE' / 'results' / 'recipe_grammar_postures.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")

if __name__ == '__main__':
    main()
