#!/usr/bin/env python3
"""
PREPARATION STATE ENCODING TEST
===============================

Question: Do RI MIDDLEs encode preparation state?

We observed:
- PP labels correlate with processed/cut materials
- RI labels correlate with unique/whole specimens

This test checks if specific MIDDLEs correlate with Brunschwig preparation terms.

Hypothesis: If RI encodes preparation state, we should see:
- Specific MIDDLEs appearing more in recipes with specific preparation terms
- Different MIDDLE distributions for "chopped" vs "whole" vs "pressed" etc.

Phase: BRUNSCHWIG_PP_RI_TEST
Date: 2026-01-24
"""

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent.parent.parent

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

# Preparation action categories
PREP_CATEGORIES = {
    'CHOP': ['chop', 'cut', 'hack', 'slice'],
    'POUND': ['pound', 'crush', 'grind', 'bruise', 'beat'],
    'PRESS': ['press', 'squeeze', 'express'],
    'WHOLE': ['whole', 'entire', 'complete'],
    'DRY': ['dry', 'dried', 'desiccate'],
    'FRESH': ['fresh', 'green', 'new'],
    'SOAK': ['soak', 'steep', 'macerate', 'infuse'],
    'BOIL': ['boil', 'decoct', 'simmer'],
}

# Parts used categories
PARTS_CATEGORIES = {
    'ROOT_ONLY': ['root'],
    'HERB_ONLY': ['herb'],
    'MULTIPLE': ['root', 'herb', 'stem', 'leaf', 'flower'],
    'SEED': ['seed', 'grain'],
    'FLOWER': ['flower', 'blossom'],
    'FRUIT': ['fruit', 'berry'],
}

def extract_middle(token):
    original = token
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break
    return token if token else None

def categorize_preparation(procedure_summary):
    """Extract preparation categories from procedure summary."""
    if not procedure_summary:
        return set()

    text = procedure_summary.lower()
    categories = set()

    for cat, terms in PREP_CATEGORIES.items():
        if any(term in text for term in terms):
            categories.add(cat)

    return categories

def categorize_parts(parts_used):
    """Categorize parts used."""
    if not parts_used:
        return 'UNKNOWN'

    parts_lower = [p.lower() for p in parts_used]

    if len(parts_used) == 1:
        if 'root' in parts_lower:
            return 'ROOT_ONLY'
        elif 'herb' in parts_lower:
            return 'HERB_ONLY'
        elif any(p in parts_lower for p in ['seed', 'grain']):
            return 'SEED'
        elif any(p in parts_lower for p in ['flower', 'blossom']):
            return 'FLOWER'
        elif any(p in parts_lower for p in ['fruit', 'berry']):
            return 'FRUIT'
        else:
            return 'OTHER_SINGLE'
    else:
        return 'MULTIPLE_PARTS'

def load_data():
    """Load Brunschwig recipes and Voynich MIDDLEs."""

    # Load Brunschwig
    with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
        brunschwig = json.load(f)
    recipes = brunschwig['recipes']

    # Load folio classifications
    try:
        with open(PROJECT_ROOT / 'results' / 'exclusive_middle_backprop.json', 'r') as f:
            backprop = json.load(f)
        folio_classifications = backprop['a_folio_classifications']
    except FileNotFoundError:
        folio_classifications = {}

    # Load PP/RI classification
    try:
        with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
            data = json.load(f)
        pp_middles = set(data['a_shared_middles'])
        ri_middles = set(data['a_exclusive_middles'])
    except FileNotFoundError:
        pp_middles, ri_middles = set(), set()

    # Load folio MIDDLEs
    folio_middles = defaultdict(list)

    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip() != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            placement = row.get('placement', '').strip()

            if language != 'A' or not word or '*' in word:
                continue
            if placement.startswith('L'):  # Skip labels for this test
                continue

            middle = extract_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio].append(middle)

    return recipes, folio_classifications, pp_middles, ri_middles, dict(folio_middles)

def test_preparation_middle_correlation(recipes, folio_classifications, pp_middles, ri_middles, folio_middles):
    """Test if preparation actions correlate with specific MIDDLEs."""

    print("\n" + "="*70)
    print("TEST: Preparation Action -> MIDDLE Correlation")
    print("="*70)
    print("Do specific preparation actions correlate with specific MIDDLEs?")

    # Group recipes by preparation category
    prep_to_types = defaultdict(list)
    for recipe in recipes:
        preps = categorize_preparation(recipe.get('procedure_summary'))

        # Map recipe to product type
        fire_degree = recipe.get('fire_degree', 2)
        material_class = recipe.get('material_class', 'herb')

        if fire_degree == 4 or material_class == 'animal':
            product_type = 'PRECISION'
        elif fire_degree == 3:
            product_type = 'OIL_RESIN'
        elif fire_degree == 1:
            product_type = 'WATER_GENTLE'
        else:
            product_type = 'WATER_STANDARD'

        for prep in preps:
            prep_to_types[prep].append(product_type)

    print("\nRecipes by preparation category:")
    for prep, types in sorted(prep_to_types.items(), key=lambda x: -len(x[1])):
        print(f"  {prep}: {len(types)} recipes")

    # Get MIDDLEs for folios associated with each prep category
    prep_to_middles = defaultdict(list)

    for prep, product_types in prep_to_types.items():
        type_counts = Counter(product_types)
        dominant_type = type_counts.most_common(1)[0][0] if type_counts else None

        # Find folios of this type
        for folio, ftype in folio_classifications.items():
            if ftype == dominant_type and folio in folio_middles:
                prep_to_middles[prep].extend(folio_middles[folio])

    # Analyze MIDDLE distributions by prep category
    print("\n" + "-"*70)
    print("MIDDLE distribution by preparation category:")
    print("-"*70)

    all_middles = []
    for middles in prep_to_middles.values():
        all_middles.extend(middles)
    baseline = Counter(all_middles)
    baseline_total = sum(baseline.values())

    for prep in ['CHOP', 'POUND', 'WHOLE', 'FRESH', 'DRY']:
        if prep not in prep_to_middles:
            continue

        middles = prep_to_middles[prep]
        if len(middles) < 50:
            continue

        dist = Counter(middles)
        total = sum(dist.values())

        print(f"\n{prep} ({total} tokens):")

        # Find MIDDLEs that are over/under-represented
        enriched = []
        depleted = []

        for middle, count in dist.most_common(20):
            observed_pct = 100 * count / total
            expected_pct = 100 * baseline.get(middle, 0) / baseline_total

            if expected_pct > 0:
                ratio = observed_pct / expected_pct
                if ratio > 1.5:
                    pp_ri = "PP" if middle in pp_middles else "RI" if middle in ri_middles else "?"
                    enriched.append((middle, ratio, pp_ri))
                elif ratio < 0.5:
                    pp_ri = "PP" if middle in pp_middles else "RI" if middle in ri_middles else "?"
                    depleted.append((middle, ratio, pp_ri))

        if enriched:
            print(f"  Enriched MIDDLEs (>1.5x baseline):")
            for m, r, pp_ri in enriched[:5]:
                print(f"    {m} ({pp_ri}): {r:.1f}x")

        if depleted:
            print(f"  Depleted MIDDLEs (<0.5x baseline):")
            for m, r, pp_ri in depleted[:5]:
                print(f"    {m} ({pp_ri}): {r:.1f}x")

def test_parts_middle_correlation(recipes, folio_classifications, pp_middles, ri_middles, folio_middles):
    """Test if parts_used correlates with specific MIDDLEs."""

    print("\n" + "="*70)
    print("TEST: Parts Used -> MIDDLE Correlation")
    print("="*70)
    print("Do different plant parts correlate with different MIDDLEs?")

    # Group recipes by parts category
    parts_to_types = defaultdict(list)
    for recipe in recipes:
        parts_cat = categorize_parts(recipe.get('parts_used', []))

        fire_degree = recipe.get('fire_degree', 2)
        material_class = recipe.get('material_class', 'herb')

        if fire_degree == 4 or material_class == 'animal':
            product_type = 'PRECISION'
        elif fire_degree == 3:
            product_type = 'OIL_RESIN'
        elif fire_degree == 1:
            product_type = 'WATER_GENTLE'
        else:
            product_type = 'WATER_STANDARD'

        parts_to_types[parts_cat].append(product_type)

    print("\nRecipes by parts category:")
    for parts, types in sorted(parts_to_types.items(), key=lambda x: -len(x[1])):
        print(f"  {parts}: {len(types)} recipes")

    # Compare ROOT_ONLY vs HERB_ONLY vs MULTIPLE
    parts_to_middles = defaultdict(list)

    for parts_cat, product_types in parts_to_types.items():
        type_counts = Counter(product_types)

        for folio, ftype in folio_classifications.items():
            if ftype in type_counts and folio in folio_middles:
                # Weight by how common this type is in this parts category
                weight = type_counts[ftype] / len(product_types)
                if weight > 0.3:  # Only include if significant
                    parts_to_middles[parts_cat].extend(folio_middles[folio])

    print("\n" + "-"*70)
    print("PP/RI ratio by parts category:")
    print("-"*70)

    for parts_cat in ['ROOT_ONLY', 'HERB_ONLY', 'MULTIPLE_PARTS', 'FLOWER', 'SEED']:
        if parts_cat not in parts_to_middles:
            continue

        middles = parts_to_middles[parts_cat]
        if len(middles) < 100:
            continue

        pp_count = sum(1 for m in middles if m in pp_middles)
        ri_count = sum(1 for m in middles if m in ri_middles)
        total = pp_count + ri_count

        if total > 0:
            pp_pct = 100 * pp_count / total
            ri_pct = 100 * ri_count / total
            print(f"  {parts_cat}: PP={pp_pct:.1f}%, RI={ri_pct:.1f}% (n={total})")

def test_direct_middle_prep_mapping(recipes, pp_middles, ri_middles):
    """Test if specific MIDDLEs appear in specific preparation contexts."""

    print("\n" + "="*70)
    print("TEST: Direct MIDDLE -> Preparation Mapping")
    print("="*70)
    print("Do specific MIDDLEs from material_class_priors correlate with preparation?")

    # Load material class priors (MIDDLEs with high animal/herb probability)
    try:
        with open(PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_summary.json', 'r') as f:
            priors = json.load(f)
    except FileNotFoundError:
        print("  Material class priors not found")
        return

    # Get concentrated MIDDLEs (high probability for one class)
    concentrated = priors.get('most_concentrated', [])

    print(f"\nAnalyzing {len(concentrated)} concentrated MIDDLEs:")

    # Group by dominant class
    class_middles = defaultdict(list)
    for item in concentrated:
        class_middles[item['top_class']].append(item['middle'])

    for mat_class, middles in class_middles.items():
        pp_count = sum(1 for m in middles if m in pp_middles)
        ri_count = sum(1 for m in middles if m in ri_middles)

        print(f"\n  {mat_class} ({len(middles)} MIDDLEs):")
        print(f"    PP: {pp_count}, RI: {ri_count}")

        # Check if this class has specific prep patterns in Brunschwig
        class_recipes = [r for r in recipes if r.get('material_class') == mat_class]
        if class_recipes:
            preps = set()
            for r in class_recipes:
                preps.update(categorize_preparation(r.get('procedure_summary')))
            print(f"    Common preparations: {preps if preps else 'none specified'}")

def test_ri_specificity():
    """Test if RI MIDDLEs are more specific to certain contexts."""

    print("\n" + "="*70)
    print("TEST: RI Specificity Analysis")
    print("="*70)
    print("Are RI MIDDLEs more context-specific than PP MIDDLEs?")

    # Load folio appearances for each MIDDLE
    middle_folios = defaultdict(set)

    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip() != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()

            if language != 'A' or not word or '*' in word:
                continue

            middle = extract_middle(word)
            if middle and len(middle) > 1:
                middle_folios[middle].add(folio)

    # Load PP/RI classification
    try:
        with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
            data = json.load(f)
        pp_middles = set(data['a_shared_middles'])
        ri_middles = set(data['a_exclusive_middles'])
    except FileNotFoundError:
        return

    # Calculate folio spread for PP vs RI
    pp_spreads = [len(middle_folios[m]) for m in pp_middles if m in middle_folios]
    ri_spreads = [len(middle_folios[m]) for m in ri_middles if m in middle_folios]

    import statistics

    print(f"\nFolio spread (# folios each MIDDLE appears in):")
    print(f"  PP MIDDLEs: mean={statistics.mean(pp_spreads):.2f}, median={statistics.median(pp_spreads):.1f}")
    print(f"  RI MIDDLEs: mean={statistics.mean(ri_spreads):.2f}, median={statistics.median(ri_spreads):.1f}")

    # RI should be more localized (fewer folios) if it encodes specific properties
    if statistics.mean(ri_spreads) < statistics.mean(pp_spreads):
        print("\n  -> RI MIDDLEs are MORE LOCALIZED (appear in fewer folios)")
        print("     Consistent with encoding specific properties/preparations")
    else:
        print("\n  -> RI MIDDLEs are NOT more localized")
        print("     Does not support preparation encoding hypothesis")

def main():
    print("PREPARATION STATE ENCODING TEST")
    print("="*70)
    print("Testing if RI MIDDLEs encode preparation state")
    print("="*70)

    recipes, folio_classifications, pp_middles, ri_middles, folio_middles = load_data()

    print(f"\nData loaded:")
    print(f"  Brunschwig recipes: {len(recipes)}")
    print(f"  Folio classifications: {len(folio_classifications)}")
    print(f"  PP MIDDLEs: {len(pp_middles)}")
    print(f"  RI MIDDLEs: {len(ri_middles)}")

    test_preparation_middle_correlation(recipes, folio_classifications, pp_middles, ri_middles, folio_middles)
    test_parts_middle_correlation(recipes, folio_classifications, pp_middles, ri_middles, folio_middles)
    test_direct_middle_prep_mapping(recipes, pp_middles, ri_middles)
    test_ri_specificity()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nKey question: Does RI encode preparation state?")
    print("\nEvidence needed:")
    print("  1. RI MIDDLEs should be more localized (context-specific)")
    print("  2. Specific prep actions should correlate with specific MIDDLEs")
    print("  3. Material classes with complex prep should have more RI")

if __name__ == '__main__':
    main()
