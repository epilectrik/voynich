#!/usr/bin/env python3
"""
bc_01_explanation_extraction.py - Extract explanation density metrics from Brunschwig

Extracts 6 pedagogical density metrics from brunschwig_text fields:
- M1: Warning phrase density
- M2: Conditional clause density
- M3: Sensory modifier density
- M4: Quantification density
- M5: Medical outcome density
- M6: Aggregate explanation density
"""

import json
import re
from pathlib import Path
from collections import defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# Early modern German OCR normalization
def normalize_text(text):
    """Normalize early modern German OCR characters."""
    if not text:
        return ""
    text = text.lower()
    # Common ligatures and variants
    text = text.replace('ſ', 's')
    text = text.replace('ꝛ', 'r')
    text = text.replace('ů', 'u')
    text = text.replace('ũ', 'um')
    text = text.replace('ẽ', 'en')
    text = text.replace('ā', 'an')
    text = text.replace('ō', 'on')
    text = text.replace('ē', 'en')
    text = text.replace('ÿ', 'y')
    text = text.replace('ꝑ', 'per')
    text = text.replace('ꝓ', 'con')
    return text


# Keyword sets for each metric
WARNING_KEYWORDS = [
    'hut', 'huet', 'acht', 'gefahr', 'gift', 'gifft', 'pruf', 'pruef',
    'vorsicht', 'warnung', 'schad', 'vermeide', 'meid', 'lass', 'nit',
    'sorg', 'gefehrlich', 'todt', 'tod'
]

CONDITIONAL_KEYWORDS = [
    'wenn', 'wan', 'aber', 'doch', 'sonst', 'falls', 'gesetzt',
    'wofern', 'so', 'ob', 'oder', 'es sei', 'ausser', 'ohne'
]

QUANTIFICATION_PATTERNS = [
    r'\d+',  # digits
    r'\blot\b', r'\blott\b', r'\bmass\b', r'\bmas\b', r'\bmaß\b',
    r'\btag\b', r'\btage\b', r'\bwoch\b', r'\bstund\b', r'\bjar\b',
    r'\bpfund\b', r'\buntz\b', r'\bunz\b', r'\bquentlin\b',
    r'\bhalb\b', r'\bganz\b', r'\bviel\b', r'\bwenig\b', r'\bgenug\b'
]

MEDICAL_OUTCOME_KEYWORDS = [
    'hilft', 'hilff', 'gut', 'heilt', 'heilet', 'schadet', 'totet',
    'giftig', 'gesund', 'kreftig', 'stercket', 'lindert', 'stillt',
    'treibt', 'bricht', 'loset', 'reiniget', 'werm', 'kult', 'kulet'
]

# Sensory keywords (supplement what's already extracted)
SENSORY_KEYWORDS = [
    # Sight
    'farb', 'rot', 'gelb', 'grun', 'schwarz', 'weiss', 'blau', 'braun',
    'klar', 'trub', 'hell', 'dunkel', 'schein',
    # Smell
    'riech', 'geruch', 'gestank', 'wol riechend', 'ubel riechend',
    # Sound
    'sied', 'wall', 'braus', 'rausch', 'knister',
    # Touch
    'warm', 'heiss', 'kalt', 'kuhl', 'weich', 'hart', 'dick', 'dunn',
    # Taste
    'suss', 'bitter', 'sauer', 'scharf', 'saltz'
]


def count_keyword_matches(text, keywords):
    """Count keyword occurrences in text."""
    count = 0
    for keyword in keywords:
        # Use word boundary matching
        pattern = r'\b' + re.escape(keyword)
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def count_pattern_matches(text, patterns):
    """Count regex pattern occurrences in text."""
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def get_word_count(text):
    """Count words in text."""
    if not text:
        return 0
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def extract_explanation_density(recipe):
    """Extract all density metrics for a recipe."""
    # Concatenate all brunschwig_text from procedural steps
    all_text = ""
    step_count = 0

    procedural_steps = recipe.get('procedural_steps', [])
    if not procedural_steps:
        return None

    for step in procedural_steps:
        step_text = step.get('brunschwig_text', '')
        if step_text:
            all_text += " " + step_text
            step_count += 1

    if not all_text.strip():
        return None

    # Normalize text
    normalized = normalize_text(all_text)
    word_count = get_word_count(normalized)

    if word_count < 5:  # Too short to analyze
        return None

    # Extract metrics
    m1_warning = count_keyword_matches(normalized, WARNING_KEYWORDS)
    m2_conditional = count_keyword_matches(normalized, CONDITIONAL_KEYWORDS)
    m3_sensory = count_keyword_matches(normalized, SENSORY_KEYWORDS)
    m4_quantification = count_pattern_matches(normalized, QUANTIFICATION_PATTERNS)
    m5_medical = count_keyword_matches(normalized, MEDICAL_OUTCOME_KEYWORDS)

    # Compute densities (per 100 words for readability)
    m1_density = (m1_warning / word_count) * 100
    m2_density = (m2_conditional / word_count) * 100
    m3_density = (m3_sensory / word_count) * 100
    m4_density = (m4_quantification / word_count) * 100
    m5_density = (m5_medical / word_count) * 100

    # M6: Aggregate (mean of all densities)
    m6_aggregate = np.mean([m1_density, m2_density, m3_density, m4_density, m5_density])

    return {
        'recipe_id': recipe.get('recipe_id'),
        'name': recipe.get('name_normalized', recipe.get('name_german', '')),
        'predicted_regime': recipe.get('predicted_regime'),
        'product_type': recipe.get('predicted_product_type'),
        'fire_degree': recipe.get('fire_degree'),
        'step_count': step_count,
        'word_count': word_count,
        'raw_text_length': len(all_text),
        'metrics': {
            'M1_warning_count': m1_warning,
            'M1_warning_density': round(m1_density, 4),
            'M2_conditional_count': m2_conditional,
            'M2_conditional_density': round(m2_density, 4),
            'M3_sensory_count': m3_sensory,
            'M3_sensory_density': round(m3_density, 4),
            'M4_quantification_count': m4_quantification,
            'M4_quantification_density': round(m4_density, 4),
            'M5_medical_count': m5_medical,
            'M5_medical_density': round(m5_density, 4),
            'M6_aggregate_density': round(m6_aggregate, 4)
        }
    }


def main():
    print("=" * 70)
    print("BC_EXPLANATION_ENFORCEMENT: bc_01 - Explanation Density Extraction")
    print("=" * 70)
    print()

    # Load Brunschwig materials
    materials_path = DATA_DIR / "brunschwig_materials_master.json"
    if not materials_path.exists():
        print(f"ERROR: Could not find {materials_path}")
        return None

    with open(materials_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    materials = data.get('materials', [])
    print(f"Loaded {len(materials)} materials from Brunschwig")

    # Extract density for each recipe with procedures
    results = []
    by_regime = defaultdict(list)
    by_product = defaultdict(list)

    for recipe in materials:
        density = extract_explanation_density(recipe)
        if density:
            results.append(density)
            regime = density['predicted_regime']
            product = density['product_type']
            if regime:
                by_regime[regime].append(density['metrics']['M6_aggregate_density'])
            if product:
                by_product[product].append(density['metrics']['M6_aggregate_density'])

    print(f"\nExtracted density metrics for {len(results)} recipes with procedures")

    # Summary statistics
    print("\n" + "-" * 70)
    print("AGGREGATE DENSITY BY REGIME")
    print("-" * 70)

    for regime in sorted(by_regime.keys()):
        densities = by_regime[regime]
        print(f"\n{regime}: n={len(densities)}")
        print(f"  Mean M6: {np.mean(densities):.4f}")
        print(f"  Std M6:  {np.std(densities):.4f}")

    print("\n" + "-" * 70)
    print("AGGREGATE DENSITY BY PRODUCT TYPE")
    print("-" * 70)

    for product in sorted(by_product.keys()):
        densities = by_product[product]
        print(f"\n{product}: n={len(densities)}")
        print(f"  Mean M6: {np.mean(densities):.4f}")
        print(f"  Std M6:  {np.std(densities):.4f}")

    # Individual metric summaries
    print("\n" + "-" * 70)
    print("METRIC DISTRIBUTIONS (all recipes)")
    print("-" * 70)

    all_m1 = [r['metrics']['M1_warning_density'] for r in results]
    all_m2 = [r['metrics']['M2_conditional_density'] for r in results]
    all_m3 = [r['metrics']['M3_sensory_density'] for r in results]
    all_m4 = [r['metrics']['M4_quantification_density'] for r in results]
    all_m5 = [r['metrics']['M5_medical_density'] for r in results]
    all_m6 = [r['metrics']['M6_aggregate_density'] for r in results]

    print(f"\nM1 Warning:       mean={np.mean(all_m1):.4f}, std={np.std(all_m1):.4f}")
    print(f"M2 Conditional:   mean={np.mean(all_m2):.4f}, std={np.std(all_m2):.4f}")
    print(f"M3 Sensory:       mean={np.mean(all_m3):.4f}, std={np.std(all_m3):.4f}")
    print(f"M4 Quantification: mean={np.mean(all_m4):.4f}, std={np.std(all_m4):.4f}")
    print(f"M5 Medical:       mean={np.mean(all_m5):.4f}, std={np.std(all_m5):.4f}")
    print(f"M6 Aggregate:     mean={np.mean(all_m6):.4f}, std={np.std(all_m6):.4f}")

    # Save results
    output = {
        'phase': 'BC_EXPLANATION_ENFORCEMENT',
        'script': 'bc_01_explanation_extraction',
        'total_recipes_analyzed': len(results),
        'by_regime': {
            regime: {
                'count': len(densities),
                'mean_m6': round(float(np.mean(densities)), 4),
                'std_m6': round(float(np.std(densities)), 4)
            }
            for regime, densities in by_regime.items()
        },
        'by_product': {
            product: {
                'count': len(densities),
                'mean_m6': round(float(np.mean(densities)), 4),
                'std_m6': round(float(np.std(densities)), 4)
            }
            for product, densities in by_product.items()
        },
        'metric_distributions': {
            'M1_warning': {'mean': round(float(np.mean(all_m1)), 4), 'std': round(float(np.std(all_m1)), 4)},
            'M2_conditional': {'mean': round(float(np.mean(all_m2)), 4), 'std': round(float(np.std(all_m2)), 4)},
            'M3_sensory': {'mean': round(float(np.mean(all_m3)), 4), 'std': round(float(np.std(all_m3)), 4)},
            'M4_quantification': {'mean': round(float(np.mean(all_m4)), 4), 'std': round(float(np.std(all_m4)), 4)},
            'M5_medical': {'mean': round(float(np.mean(all_m5)), 4), 'std': round(float(np.std(all_m5)), 4)},
            'M6_aggregate': {'mean': round(float(np.mean(all_m6)), 4), 'std': round(float(np.std(all_m6)), 4)},
        },
        'recipes': results
    }

    output_path = RESULTS_DIR / "bc_explanation_density.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    main()
