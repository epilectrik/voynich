"""Merge fire degree extractions and update brunschwig_curated_v2.json."""
import json
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'PREP_POSTURE_DIVERGENCE' / 'results'

def load_batch(filename):
    """Load a batch file and return recipe fire degrees."""
    path = RESULTS_DIR / filename
    if not path.exists():
        print(f"Warning: {filename} not found")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle different possible structures
    recipes = data.get('recipes', data.get('fire_degrees', []))
    if isinstance(recipes, dict):
        # If it's a dict with recipe_id keys
        return {int(k): v.get('fire_degree', v) if isinstance(v, dict) else v
                for k, v in recipes.items()}
    elif isinstance(recipes, list):
        # If it's a list of recipe dicts
        result = {}
        for r in recipes:
            if isinstance(r, dict):
                rid = r.get('id', r.get('recipe_id'))
                fd = r.get('fire_degree')
                if rid is not None and fd is not None:
                    result[int(rid)] = int(fd)
        return result
    return {}

def main():
    print("Loading batch files...")

    # Load all batch files
    all_fire_degrees = {}
    for batch_file in ['fire_degrees_batch1.json', 'fire_degrees_batch2.json', 'fire_degrees_batch3.json']:
        batch_data = load_batch(batch_file)
        print(f"  {batch_file}: {len(batch_data)} recipes")
        all_fire_degrees.update(batch_data)

    print(f"\nTotal extracted: {len(all_fire_degrees)} fire degrees")

    # Distribution
    dist = Counter(all_fire_degrees.values())
    print("\nFire degree distribution from extraction:")
    for fd, count in sorted(dist.items()):
        print(f"  Degree {fd}: {count} recipes")

    # Load original JSON
    json_path = PROJECT_ROOT / 'data' / 'brunschwig_curated_v2.json'
    print(f"\nLoading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update fire degrees
    updated = 0
    kept = 0
    for recipe in data['recipes']:
        rid = recipe['id']
        current_fd = recipe.get('fire_degree', 0)

        if rid in all_fire_degrees:
            new_fd = all_fire_degrees[rid]
            if current_fd == 0:
                recipe['fire_degree'] = new_fd
                updated += 1
            else:
                # Keep existing non-zero value
                kept += 1
        elif current_fd != 0:
            kept += 1

    print(f"\nUpdated: {updated} recipes")
    print(f"Kept existing: {kept} recipes")

    # Final distribution
    final_dist = Counter(r.get('fire_degree', 0) for r in data['recipes'])
    print("\nFinal fire degree distribution:")
    for fd, count in sorted(final_dist.items()):
        print(f"  Degree {fd}: {count} recipes")

    # Save updated JSON
    print(f"\nSaving updated JSON...")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {json_path}")

if __name__ == '__main__':
    main()
