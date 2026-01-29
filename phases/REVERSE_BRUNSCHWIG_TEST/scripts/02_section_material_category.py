"""
02_section_material_category.py

Test 3: Do Voynich sections specialize by Brunschwig material category?

Hypothesis:
- HERBAL_B enriched for herb/flower materials
- BIO enriched for animal materials
- Different sections have different material profiles

Method:
1. Classify Brunschwig recipes by material (herb, flower, root, animal)
2. Extract MIDDLEs associated with each material category
3. Check if those MIDDLEs concentrate in specific sections
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

# Add scripts to path for voynich library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

print("="*70)
print("SECTION -> MATERIAL CATEGORY ANALYSIS")
print("="*70)

# Load Brunschwig data
with open('data/brunschwig_curated_v3.json', encoding='utf-8') as f:
    brunschwig = json.load(f)

# Load transcript
tx = Transcript()

# Build folio-grouped tokens for B
folio_tokens = defaultdict(list)
for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_tokens[token.folio].append(token)

# Load morphology for MIDDLE extraction
try:
    morph = Morphology()
    has_morph = True
    print("Loaded Morphology class")
except:
    has_morph = False
    print("Morphology not available, using simple MIDDLE extraction")

def extract_middle(word):
    """Extract MIDDLE from word."""
    if has_morph:
        try:
            m = morph.extract(word)
            return m.middle
        except:
            return None
    else:
        # Simple heuristic: remove common prefixes/suffixes
        # This is approximate
        w = word
        for prefix in ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct', 'lch', 'lk', 'lsh']:
            if w.startswith(prefix):
                w = w[len(prefix):]
                break
        for suffix in ['y', 'dy', 'ey', 'ly', 'ry', 'ol', 'or', 'ar', 'al', 'ain', 'aiin']:
            if w.endswith(suffix) and len(w) > len(suffix):
                w = w[:-len(suffix)]
                break
        return w if w else None

# Group Brunschwig recipes by material category
material_categories = defaultdict(list)
for recipe in brunschwig['recipes']:
    material = recipe.get('material_class', 'unknown')
    # Normalize categories
    if 'herb' in material.lower():
        cat = 'HERB'
    elif 'flower' in material.lower():
        cat = 'FLOWER'
    elif 'root' in material.lower():
        cat = 'ROOT'
    elif 'animal' in material.lower():
        cat = 'ANIMAL'
    elif 'fruit' in material.lower():
        cat = 'FRUIT'
    else:
        cat = 'OTHER'
    material_categories[cat].append(recipe)

print("\nBrunschwig material categories:")
for cat, recipes in sorted(material_categories.items()):
    print(f"  {cat}: {len(recipes)} recipes")

# For each material category, extract associated German names
# These can help identify which Voynich vocabulary might correspond

print("\n" + "="*70)
print("SECTION PROFILES")
print("="*70)

# Compute section profiles
section_middles = defaultdict(Counter)
section_tokens = defaultdict(int)

for folio, tokens in folio_tokens.items():
    section = tokens[0].section if hasattr(tokens[0], 'section') else 'unknown'

    for token in tokens:
        word = token.word
        if not word or not word.strip():
            continue
        middle = extract_middle(word)
        if middle:
            section_middles[section][middle] += 1
            section_tokens[section] += 1

print("\nMIDDLE counts by section:")
for section in sorted(section_middles.keys()):
    n_unique = len(section_middles[section])
    n_total = section_tokens[section]
    print(f"  {section}: {n_unique} unique MIDDLEs, {n_total} tokens")

# Compute section-specific vocabulary
print("\n" + "="*70)
print("SECTION-SPECIFIC VOCABULARY")
print("="*70)

# Find MIDDLEs that are enriched in specific sections
all_middles = Counter()
for section, counts in section_middles.items():
    all_middles.update(counts)

section_enrichment = defaultdict(list)

for section, counts in section_middles.items():
    section_total = section_tokens[section]
    overall_total = sum(section_tokens.values())

    for middle, count in counts.items():
        if count < 5:  # Minimum frequency
            continue

        # Expected count if evenly distributed
        overall_count = all_middles[middle]
        expected = overall_count * (section_total / overall_total)

        if expected > 0:
            enrichment = count / expected
            if enrichment > 1.5:  # At least 1.5x enriched
                section_enrichment[section].append({
                    'middle': middle,
                    'count': count,
                    'enrichment': enrichment
                })

for section in sorted(section_enrichment.keys()):
    enriched = sorted(section_enrichment[section], key=lambda x: -x['enrichment'])[:10]
    print(f"\n{section} enriched MIDDLEs:")
    for item in enriched:
        print(f"  {item['middle']}: {item['enrichment']:.2f}x ({item['count']} occurrences)")

# Cross-reference with Brunschwig material categories
print("\n" + "="*70)
print("BRUNSCHWIG MATERIAL -> SECTION HYPOTHESIS")
print("="*70)

# Based on ANIMAL_RECIPE_TRACE, we know animal materials route to REGIME_4
# Let's check if BIO section (balneological figures) shows animal-compatible vocabulary

# Load animal signature data if available
try:
    with open('phases/ANIMAL_RECIPE_TRACE/results/animal_signatures.json') as f:
        animal_data = json.load(f)
    print("\nLoaded animal signature data")

    # Check which sections receive animal-compatible vocabulary
    animal_middles = set()
    for record in animal_data.get('high_confidence_records', []):
        # This would need the actual MIDDLE data
        pass

except FileNotFoundError:
    print("\nAnimal signature data not found")

# Compute section similarity to Brunschwig material profiles
print("\n" + "="*70)
print("SECTION-MATERIAL CORRESPONDENCE TEST")
print("="*70)

# Hypothesis mapping
hypotheses = {
    'herbal_b': 'HERB/FLOWER',
    'bio': 'ANIMAL',
    'pharma': 'ROOT',
    'recipe_b': 'MIXED'
}

# For each section, compute a "material signature" based on vocabulary
# This is exploratory - we're looking for patterns

# Check if any sections have significantly different profiles
sections = list(section_middles.keys())
if len(sections) >= 2:
    # Compare MIDDLE distributions between sections
    print("\nSection vocabulary overlap (Jaccard similarity):")

    for i, s1 in enumerate(sections):
        for s2 in sections[i+1:]:
            set1 = set(section_middles[s1].keys())
            set2 = set(section_middles[s2].keys())
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            jaccard = intersection / union if union > 0 else 0
            print(f"  {s1} vs {s2}: {jaccard:.3f}")

# Save results
results = {
    'material_categories': {cat: len(recipes) for cat, recipes in material_categories.items()},
    'section_profiles': {
        section: {
            'unique_middles': len(counts),
            'total_tokens': section_tokens[section],
            'top_middles': [m for m, c in counts.most_common(20)]
        }
        for section, counts in section_middles.items()
    },
    'section_enrichment': {
        section: items[:20]
        for section, items in section_enrichment.items()
    },
    'hypothesis_mapping': hypotheses,
    'note': 'This test checks if sections specialize by material type'
}

output_path = results_dir / "section_material_mapping.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to {output_path}")
