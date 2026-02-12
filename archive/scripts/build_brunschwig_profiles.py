"""Build operational profiles for all 245 Brunschwig recipes.

Converts each recipe's action sequence into a predicted Voynich operational
vector using F-BRU-012/013 action-to-MIDDLE mappings.

Output: results/brunschwig_operational_profiles.json
"""
import json
import sys
from collections import Counter

sys.path.insert(0, '.')

# --- Action-to-Voynich mapping (from F-BRU-012, F-BRU-013, F-BRU-020) ---
# Maps Brunschwig actions to predicted Voynich operational dimensions

ACTION_TO_PREP = {
    'GATHER': 'te',
    'SELECT': 'te',      # Selection is part of gathering
    'CHOP': 'pch',
    'STRIP': 'lch',
    'POUND': 'tch',
    'CRUSH': 'tch',      # Similar to POUND
    'BREAK': 'lch',      # Similar to STRIP
    'GRIND': 'tch',      # Similar to POUND
    'POWDER': 'tch',     # Reduction to powder ~ POUND
}

ACTION_TO_KERNEL = {
    # k-kernel (heat operations)
    'DISTILL': 'k',
    'REDISTILL': 'k',
    'DRY': 'k',
    'FERMENT': 'k',
    'DIGEST': 'k',
    'MELT': 'k',
    # h-kernel (monitoring/hazard)
    'MONITOR_DRIPS': 'h',
    'MONITOR_TEMP': 'h',
    'REGULATE': 'h',
    'SEAL': 'h',         # Sealing prevents hazard
    # e-kernel (cooling/settling/escape)
    'COOL': 'e',
    'FILTER': 'e',
    'STRAIN': 'e',
    'SETTLE': 'e',
    'RECTIFY': 'e',
    'COLLECT': 'e',
}

# Fire degree determines thermal MIDDLE type
# Degree 1 (gentle) → ke (sustained heat cycles)
# Degree 2 (standard) → ke (standard distillation)
# Degree 3 (intense) → kch (precision monitoring needed)

# --- Load recipes ---
with open('data/brunschwig_curated_v3.json', encoding='utf-8') as f:
    data = json.load(f)

recipes = data['recipes']
print(f"Loaded {len(recipes)} Brunschwig recipes")

# --- Build profiles ---
profiles = []

for recipe in recipes:
    rid = recipe['id']
    name = recipe.get('name_english', recipe.get('name_german', f'recipe_{rid}'))
    fire_degree = recipe.get('fire_degree', 2)
    material_class = recipe.get('material_class', 'unknown')
    has_procedure = recipe.get('has_procedure', False)
    steps = recipe.get('procedural_steps') or []
    sensory = recipe.get('sensory_modality', ['NONE'])

    # Count actions
    action_counts = Counter()
    for step in steps:
        action = step.get('action', 'UNKNOWN')
        action_counts[action] += 1

    total_actions = sum(action_counts.values()) or 1

    # Map to prep MIDDLE rates
    prep_counts = Counter()
    for action, count in action_counts.items():
        if action in ACTION_TO_PREP:
            prep_counts[ACTION_TO_PREP[action]] += count

    # Map to kernel predictions
    kernel_counts = Counter()
    for action, count in action_counts.items():
        if action in ACTION_TO_KERNEL:
            kernel_counts[ACTION_TO_KERNEL[action]] += count

    k_total = sum(kernel_counts.values()) or 1
    k_ratio = kernel_counts.get('k', 0) / k_total
    h_ratio = kernel_counts.get('h', 0) / k_total
    e_ratio = kernel_counts.get('e', 0) / k_total

    # Thermo MIDDLE prediction based on fire degree
    has_distill = action_counts.get('DISTILL', 0) + action_counts.get('REDISTILL', 0)
    thermo_ke = 0
    thermo_kch = 0
    if has_distill > 0:
        if fire_degree >= 3:
            thermo_kch = has_distill / total_actions
        else:
            thermo_ke = has_distill / total_actions

    # Iteration prediction: REDISTILL implies iteration
    has_redistill = action_counts.get('REDISTILL', 0)
    iteration_rate = has_redistill / total_actions if has_redistill else 0

    # Checkpoint prediction: MONITOR_* implies checkpoints
    monitors = action_counts.get('MONITOR_DRIPS', 0) + action_counts.get('MONITOR_TEMP', 0)
    checkpoint_rate = monitors / total_actions if monitors else 0

    # Terminal prediction: STORE/SEAL_VESSEL/LABEL imply terminals
    terminals = (action_counts.get('STORE', 0) + action_counts.get('SEAL_VESSEL', 0)
                 + action_counts.get('LABEL', 0) + action_counts.get('COLLECT', 0))
    terminal_rate = terminals / total_actions if terminals else 0

    # Prep rates (normalize to proportion of total actions)
    profile = {
        'recipe_id': rid,
        'name': name,
        'name_german': recipe.get('name_german', ''),
        'material_class': material_class,
        'fire_degree': fire_degree,
        'step_count': len(steps),
        'has_procedure': has_procedure,
        # Prep MIDDLEs (predicted rates)
        'prep_te': prep_counts.get('te', 0) / total_actions,
        'prep_pch': prep_counts.get('pch', 0) / total_actions,
        'prep_lch': prep_counts.get('lch', 0) / total_actions,
        'prep_tch': prep_counts.get('tch', 0) / total_actions,
        # Thermo MIDDLEs (predicted)
        'thermo_ke': round(thermo_ke, 4),
        'thermo_kch': round(thermo_kch, 4),
        # Kernel ratios (predicted)
        'k_ratio': round(k_ratio, 4),
        'h_ratio': round(h_ratio, 4),
        'e_ratio': round(e_ratio, 4),
        # Control-flow rates (predicted)
        'iteration_rate': round(iteration_rate, 4),
        'checkpoint_rate': round(checkpoint_rate, 4),
        'terminal_rate': round(terminal_rate, 4),
        # Categorical
        'sensory_modality': sensory,
        # Raw for reference
        'raw_action_counts': dict(action_counts),
    }
    profiles.append(profile)

# --- Output ---
output = {
    'title': 'Brunschwig Recipe Operational Profiles (Predicted Voynich Vectors)',
    'recipe_count': len(profiles),
    'mapping_source': 'F-BRU-012, F-BRU-013, F-BRU-020',
    'dimensions': [
        'prep_te', 'prep_pch', 'prep_lch', 'prep_tch',
        'thermo_ke', 'thermo_kch',
        'k_ratio', 'h_ratio', 'e_ratio',
        'iteration_rate', 'checkpoint_rate', 'terminal_rate',
    ],
    'profiles': profiles,
}

with open('results/brunschwig_operational_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nWrote {len(profiles)} recipe profiles to results/brunschwig_operational_profiles.json")

# --- Quick summary ---
classes = Counter(p['material_class'] for p in profiles)
degrees = Counter(p['fire_degree'] for p in profiles)
has_proc = sum(1 for p in profiles if p['has_procedure'])
print(f"\nMaterial classes: {dict(classes)}")
print(f"Fire degrees: {dict(degrees)}")
print(f"With procedures: {has_proc}/{len(profiles)}")

# Mean predicted rates
for dim in ['prep_te', 'prep_pch', 'prep_lch', 'prep_tch', 'thermo_ke', 'thermo_kch']:
    vals = [p[dim] for p in profiles]
    mean_val = sum(vals) / len(vals) if vals else 0
    nonzero = sum(1 for v in vals if v > 0)
    print(f"  {dim}: mean={mean_val:.4f}, nonzero={nonzero}/{len(profiles)}")

# Recipes with no procedure get zero vectors — flag them
no_proc = [p['name'] for p in profiles if not p['has_procedure']]
print(f"\nRecipes without procedure (zero vectors): {len(no_proc)}")
if no_proc:
    print(f"  Examples: {', '.join(no_proc[:5])}")
