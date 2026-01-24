"""
Extract fire_degree values for Brunschwig recipes 91-170.

Fire Degree Scale:
- Degree 1: Gentle fire, balneum mariae (water bath), delicate materials
- Degree 2: Standard/moderate fire, typical herb distillation
- Degree 3: Strong fire, per alembicum, harder materials (roots, bark, resins)
- Degree 4: Very strong fire, mineral/metal distillation (rare)
"""

import json
import re
from pathlib import Path

# Paths
BASE = Path("C:/git/voynich")
JSON_PATH = BASE / "data" / "brunschwig_curated_v2.json"
SOURCE_PATH = BASE / "sources" / "brunschwig_1500_text.txt"
OUTPUT_PATH = BASE / "phases" / "PREP_POSTURE_DIVERGENCE" / "results" / "fire_degrees_batch2.json"

# Load source text
with open(SOURCE_PATH, 'r', encoding='utf-8') as f:
    source_lines = f.readlines()

# Load recipe data
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Keywords for fire degree detection
DEGREE_1_KEYWORDS = [
    'balneum', 'balneo', 'marie', 'maria',
    'sanfft', 'sanft', 'gelind', 'klein feuer', 'kleinem feuer',
    'lind feuer', 'lindem feuer', 'gemach feuer',
    'wasser bad', 'wasserbad'
]

DEGREE_3_KEYWORDS = [
    'starck', 'stark', 'groß feuer', 'grossem feuer', 'großem feuer',
    'per alembicum', 'alembic'
]

# Material indicators
GENTLE_MATERIALS = ['blumen', 'blüt', 'bluet', 'blat', 'bletter', 'rosen', 'viol', 'lili']
TOUGH_MATERIALS = ['wurtzel', 'wurtz', 'rind', 'holtz', 'holz', 'samen', 'samen', 'hartz', 'wachs']

def determine_fire_degree(text, recipe):
    """Determine fire degree from source text and recipe metadata."""
    text_lower = text.lower()

    reasoning_parts = []

    # Check for explicit degree 1 indicators
    for kw in DEGREE_1_KEYWORDS:
        if kw in text_lower:
            reasoning_parts.append(f"'{kw}' found")
            return 1, "; ".join(reasoning_parts) + " -> gentle fire"

    # Check for explicit degree 3 indicators
    for kw in DEGREE_3_KEYWORDS:
        if kw in text_lower:
            reasoning_parts.append(f"'{kw}' found")
            return 3, "; ".join(reasoning_parts) + " -> strong fire"

    # Check material type from recipe metadata
    material_type = recipe.get('material_type', '')
    latin_name = recipe.get('latin_name', '').lower()
    german_name = recipe.get('german_name', '').lower()

    # Animal products typically gentle
    if material_type == 'animal':
        return 1, "animal material -> gentle fire"

    # Check for gentle materials
    for mat in GENTLE_MATERIALS:
        if mat in text_lower or mat in latin_name or mat in german_name:
            reasoning_parts.append(f"gentle material '{mat}'")
            return 1, "; ".join(reasoning_parts) + " -> degree 1"

    # Check for tough materials
    for mat in TOUGH_MATERIALS:
        if mat in text_lower or mat in latin_name or mat in german_name:
            reasoning_parts.append(f"tough material '{mat}'")
            return 3, "; ".join(reasoning_parts) + " -> degree 3"

    # Default to degree 2 for standard herb distillation
    return 2, "standard herb distillation (default)"


def process_recipes():
    """Process recipes 91-170 and extract fire degrees."""
    results = []

    for recipe in data['recipes']:
        rid = recipe['id']
        if not (91 <= rid <= 170):
            continue

        # Get source lines
        sl = recipe.get('source_lines', {})
        start = sl.get('start')
        end = sl.get('end')

        # Check if fire_degree already exists
        existing_fd = recipe.get('fire_degree')

        if start and end:
            # Extract text (adjust for 1-indexed lines)
            text = ''.join(source_lines[start-1:end])
        else:
            text = ""

        # Determine fire degree
        fire_degree, reasoning = determine_fire_degree(text, recipe)

        # If already has a valid fire_degree (1-4), note it but still show our analysis
        if existing_fd is not None and existing_fd > 0:
            reasoning = f"existing value {existing_fd}; our analysis: {reasoning}"
            fire_degree = existing_fd

        results.append({
            "id": rid,
            "fire_degree": fire_degree,
            "reasoning": reasoning,
            "source_lines": f"{start}-{end}" if start and end else "N/A"
        })

        print(f"Recipe {rid:3d}: degree {fire_degree}, {reasoning[:60]}")

    return results


if __name__ == "__main__":
    print("Extracting fire degrees for recipes 91-170...\n")

    results = process_recipes()

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save results
    output = {"recipes": results}
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n\nSaved {len(results)} recipes to {OUTPUT_PATH}")

    # Summary
    from collections import Counter
    degrees = Counter(r['fire_degree'] for r in results)
    print("\nDegree distribution:")
    for d in sorted(degrees.keys()):
        print(f"  Degree {d}: {degrees[d]} recipes")
