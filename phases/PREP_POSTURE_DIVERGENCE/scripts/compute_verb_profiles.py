"""
Compute verb profiles for each Brunschwig recipe.

For each recipe, extracts:
- dominant_verb: Most frequent prep action
- verb_distribution: Full distribution over all actions
- verb_category: Collection / Mechanical / Cleaning / Pre-treatment / Distillation
"""
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Verb category mappings (from BRUNSCHWIG_INSTRUCTION_TAXONOMY.md)
VERB_CATEGORIES = {
    # Collection/Gathering
    'GATHER': 'COLLECTION',
    'COLLECT': 'COLLECTION',
    'PLUCK': 'COLLECTION',
    'SELECT': 'COLLECTION',
    'OBTAIN': 'COLLECTION',

    # Mechanical Processing
    'CHOP': 'MECHANICAL',
    'POUND': 'MECHANICAL',
    'CRUSH': 'MECHANICAL',
    'BREAK': 'MECHANICAL',
    'BORE': 'MECHANICAL',
    'STRIP': 'MECHANICAL',
    'BUTCHER': 'MECHANICAL',

    # Cleaning/Purification
    'WASH': 'CLEANING',
    'CLEAN': 'CLEANING',
    'FILTER': 'CLEANING',

    # Pre-treatment
    'STEEP': 'PRETREATMENT',
    'MACERATE': 'PRETREATMENT',
    'MIX': 'PRETREATMENT',
    'DRY': 'PRETREATMENT',
    'KILL': 'PRETREATMENT',

    # Distillation
    'DISTILL': 'DISTILLATION',
    'REDISTILL': 'DISTILLATION',
    'REFINE': 'DISTILLATION',
}

def get_verb_category(verb):
    """Get the category for a verb, defaulting to UNKNOWN."""
    return VERB_CATEGORIES.get(verb, 'UNKNOWN')

def compute_verb_profiles():
    """Compute verb profiles for all recipes."""

    # Load curated recipes
    with open(PROJECT_ROOT / 'data' / 'brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes = data.get('recipes', [])
    print(f"Processing {len(recipes)} recipes...")

    profiles = []
    global_verb_counts = Counter()

    for recipe in recipes:
        recipe_id = recipe.get('id', 0)
        recipe_name = recipe.get('name_english', '')
        material_class = recipe.get('material_class', '')
        fire_degree = recipe.get('fire_degree', 0)
        steps = recipe.get('procedural_steps', []) or []

        # Count verbs in this recipe
        verb_counts = Counter()
        for step in steps:
            action = step.get('action', '')
            if action:
                verb_counts[action] += 1
                global_verb_counts[action] += 1

        if not verb_counts:
            # Skip recipes with no procedural steps
            continue

        # Compute profile
        total_verbs = sum(verb_counts.values())
        verb_distribution = {v: c/total_verbs for v, c in verb_counts.items()}
        dominant_verb = verb_counts.most_common(1)[0][0]
        dominant_category = get_verb_category(dominant_verb)

        # Compute category distribution
        category_counts = Counter()
        for verb, count in verb_counts.items():
            cat = get_verb_category(verb)
            category_counts[cat] += count
        category_distribution = {c: cnt/total_verbs for c, cnt in category_counts.items()}

        # Determine dominant category (excluding DISTILLATION for prep focus)
        prep_categories = {c: cnt for c, cnt in category_counts.items() if c != 'DISTILLATION'}
        if prep_categories:
            dominant_prep_category = max(prep_categories.items(), key=lambda x: x[1])[0]
        else:
            dominant_prep_category = 'NONE'

        profile = {
            'recipe_id': recipe_id,
            'recipe_name': recipe_name,
            'material_class': material_class,
            'fire_degree': fire_degree,
            'total_steps': len(steps),
            'total_verbs': total_verbs,
            'dominant_verb': dominant_verb,
            'dominant_verb_count': verb_counts[dominant_verb],
            'dominant_category': dominant_category,
            'dominant_prep_category': dominant_prep_category,
            'verb_counts': dict(verb_counts),
            'verb_distribution': verb_distribution,
            'category_counts': dict(category_counts),
            'category_distribution': category_distribution,
        }
        profiles.append(profile)

    # Summary statistics
    print(f"\nProcessed {len(profiles)} recipes with procedural steps")
    print(f"\nGlobal verb counts:")
    for verb, count in global_verb_counts.most_common():
        print(f"  {verb}: {count}")

    # Dominant verb distribution
    dominant_verbs = Counter(p['dominant_verb'] for p in profiles)
    print(f"\nDominant verb distribution:")
    for verb, count in dominant_verbs.most_common():
        print(f"  {verb}: {count} recipes ({100*count/len(profiles):.1f}%)")

    # Dominant prep category distribution
    dominant_categories = Counter(p['dominant_prep_category'] for p in profiles)
    print(f"\nDominant prep category distribution:")
    for cat, count in dominant_categories.most_common():
        print(f"  {cat}: {count} recipes ({100*count/len(profiles):.1f}%)")

    # Save results
    output = {
        'metadata': {
            'total_recipes': len(recipes),
            'recipes_with_steps': len(profiles),
            'global_verb_counts': dict(global_verb_counts),
            'dominant_verb_distribution': dict(dominant_verbs),
            'dominant_category_distribution': dict(dominant_categories),
        },
        'profiles': profiles
    }

    output_path = PROJECT_ROOT / 'phases' / 'PREP_POSTURE_DIVERGENCE' / 'results' / 'recipe_verb_profiles.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")
    return output

if __name__ == '__main__':
    compute_verb_profiles()
