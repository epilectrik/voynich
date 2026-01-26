#!/usr/bin/env python3
"""
BRUNSCHWIG PP/RI PREDICTION TEST
================================

Now that we understand PP (pipeline-participating) vs RI (registry-internal):
- PP = shared A∩B vocabulary, marks standard/processed materials (interchangeable)
- RI = A-exclusive vocabulary, marks unique specimens needing specific identification

This test validates specific predictions against Brunschwig recipe properties.

PREDICTIONS:
1. has_procedure=false -> Higher RI ratio (reference-only needs specific ID)
2. material_class=animal -> Higher RI ratio (unique specimens)
3. material_class=herb (common) -> Higher PP ratio (standard processing)
4. fire_degree=4 (extreme) -> Higher RI ratio (can't substitute)
5. Multiple parts_used -> Higher RI ratio (complex specification)
6. High use_count -> Higher PP ratio (versatile = standardized)
7. Morphological: Animal folios should have specific MIDDLEs (chald, cthso, etc.)
8. PREFIX patterns: PP-dominant folios -> more qo-; RI-dominant -> more o-

Phase: BRUNSCHWIG_PP_RI_TEST
Date: 2026-01-24
"""

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
import statistics

PROJECT_ROOT = Path(__file__).parent.parent.parent

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['y', 'dy', 'edy', 'eedy', 'ey', 'aiy', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

# Animal-associated MIDDLEs with 100% probability (from material_class_summary.json)
ANIMAL_MIDDLES = {'chald', 'cthso', 'eeees', 'eoc', 'eoschso', 'eso', 'eyd', 'ha',
                  'hdaoto', 'hyd', 'iil', 'ofy', 'olfcho', 'opcho', 'pchypcho',
                  'tchyf', 'tea', 'techoep'}

def extract_prefix(token):
    """Extract PREFIX from token."""
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return p
    return None

def extract_middle(token):
    """Extract MIDDLE from token (after removing PREFIX and SUFFIX)."""
    original = token

    # Remove PREFIX
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            token = token[len(p):]
            break

    # Remove SUFFIX
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            token = token[:-len(s)]
            break

    return token if token else None

# ============================================================
# DATA LOADING
# ============================================================

def load_brunschwig_recipes():
    """Load full Brunschwig recipe database."""
    with open(PROJECT_ROOT / 'data' / 'brunschwig_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['recipes']

def load_2track_classification():
    """Load PP vs RI MIDDLE classification."""
    try:
        with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
            data = json.load(f)
        ri_middles = set(data['a_exclusive_middles'])
        pp_middles = set(data['a_shared_middles'])
        return pp_middles, ri_middles
    except FileNotFoundError:
        print("WARNING: middle_classes.json not found, computing from scratch")
        return compute_pp_ri_from_transcript()

def compute_pp_ri_from_transcript():
    """Compute PP/RI classification directly from transcript."""
    a_middles = set()
    b_middles = set()

    with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip() != 'H':
                continue

            word = row.get('word', '').strip()
            language = row.get('language', '').strip()
            placement = row.get('placement', '').strip()

            if not word or '*' in word:
                continue
            if placement.startswith('L'):  # Exclude labels
                continue

            middle = extract_middle(word)
            if middle and len(middle) > 1:
                if language == 'A':
                    a_middles.add(middle)
                elif language == 'B':
                    b_middles.add(middle)

    pp_middles = a_middles & b_middles
    ri_middles = a_middles - b_middles
    return pp_middles, ri_middles

def load_folio_classifications():
    """Load product type classification for A folios."""
    try:
        with open(PROJECT_ROOT / 'results' / 'exclusive_middle_backprop.json', 'r') as f:
            data = json.load(f)
        return data['a_folio_classifications']
    except FileNotFoundError:
        print("WARNING: exclusive_middle_backprop.json not found")
        return {}

def load_transcript():
    """Load transcript and compute per-folio statistics."""
    folio_data = defaultdict(lambda: {
        'tokens': [],
        'middles': [],
        'prefixes': [],
        'pp_count': 0,
        'ri_count': 0
    })

    pp_middles, ri_middles = load_2track_classification()

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
            if placement.startswith('L'):  # Exclude labels for text analysis
                continue

            middle = extract_middle(word)
            prefix = extract_prefix(word)

            folio_data[folio]['tokens'].append(word)
            if middle:
                folio_data[folio]['middles'].append(middle)
                if middle in pp_middles:
                    folio_data[folio]['pp_count'] += 1
                elif middle in ri_middles:
                    folio_data[folio]['ri_count'] += 1
            if prefix:
                folio_data[folio]['prefixes'].append(prefix)

    return dict(folio_data), pp_middles, ri_middles

# ============================================================
# STATISTICAL HELPERS
# ============================================================

def mann_whitney_u(group1, group2):
    """Simple Mann-Whitney U test."""
    combined = [(x, 0) for x in group1] + [(x, 1) for x in group2]
    combined.sort(key=lambda x: x[0])

    # Assign ranks
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2
        for k in range(i, j):
            if combined[k] not in ranks:
                ranks[combined[k]] = []
            ranks[combined[k]].append(avg_rank)
        i = j

    # Sum ranks for group 1
    r1 = sum(avg_rank for (x, g), avg_rank in zip(combined, range(1, len(combined)+1)) if g == 0)

    # Recalculate properly
    r1 = 0
    for i, (val, group) in enumerate(combined):
        if group == 0:
            r1 += i + 1

    n1, n2 = len(group1), len(group2)
    u1 = r1 - n1 * (n1 + 1) / 2
    u2 = n1 * n2 - u1

    u = min(u1, u2)

    # Normal approximation for p-value
    mu = n1 * n2 / 2
    sigma = ((n1 * n2 * (n1 + n2 + 1)) / 12) ** 0.5

    if sigma == 0:
        return u, 0, 1.0

    z = (u - mu) / sigma

    # Approximate p-value (two-tailed)
    import math
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))

    return u, z, p

def effect_size_r(z, n):
    """Calculate effect size r from z-score."""
    return abs(z) / (n ** 0.5)

# ============================================================
# TEST 1: has_procedure vs RI ratio
# ============================================================

def test_has_procedure(recipes, folio_classifications, folio_data):
    """Test: has_procedure=false -> Higher RI ratio"""
    print("\n" + "="*70)
    print("TEST 1: has_procedure vs RI Ratio")
    print("="*70)
    print("Prediction: Recipes WITHOUT procedures should correlate with higher RI ratios")
    print("Mechanism: Reference-only materials need specific identification, not standard processing\n")

    # Group folios by product type, then by has_procedure
    type_to_procedure = defaultdict(lambda: {'has': [], 'no': []})

    for recipe in recipes:
        product_type = None
        fire_degree = recipe.get('fire_degree', 2)
        material_class = recipe.get('material_class', 'herb')

        # Map to product types
        if fire_degree == 4 or material_class == 'animal':
            product_type = 'PRECISION'
        elif fire_degree == 3:
            product_type = 'OIL_RESIN'
        elif fire_degree == 1:
            product_type = 'WATER_GENTLE'
        else:
            product_type = 'WATER_STANDARD'

        if recipe.get('has_procedure', False):
            type_to_procedure[product_type]['has'].append(recipe)
        else:
            type_to_procedure[product_type]['no'].append(recipe)

    # Get RI ratios for folios by product type
    has_procedure_ratios = []
    no_procedure_ratios = []

    for folio, data in folio_data.items():
        total = data['pp_count'] + data['ri_count']
        if total < 5:  # Skip sparse folios
            continue

        ri_ratio = data['ri_count'] / total
        folio_type = folio_classifications.get(folio, 'UNKNOWN')

        # Check if this type has more has_procedure or no_procedure recipes
        if folio_type in type_to_procedure:
            has_count = len(type_to_procedure[folio_type]['has'])
            no_count = len(type_to_procedure[folio_type]['no'])

            if has_count > no_count:
                has_procedure_ratios.append(ri_ratio)
            elif no_count > has_count:
                no_procedure_ratios.append(ri_ratio)

    if has_procedure_ratios and no_procedure_ratios:
        u, z, p = mann_whitney_u(has_procedure_ratios, no_procedure_ratios)

        print(f"Folios with procedure-rich types: n={len(has_procedure_ratios)}, mean RI={statistics.mean(has_procedure_ratios):.3f}")
        print(f"Folios with reference-only types: n={len(no_procedure_ratios)}, mean RI={statistics.mean(no_procedure_ratios):.3f}")
        print(f"\nMann-Whitney U: z={z:.3f}, p={p:.4f}")

        if p < 0.05 and statistics.mean(no_procedure_ratios) > statistics.mean(has_procedure_ratios):
            print("RESULT: SUPPORTS prediction (reference-only -> higher RI)")
            return True, p, z
        elif p < 0.05:
            print("RESULT: CONTRADICTS prediction (procedure -> higher RI)")
            return False, p, z
        else:
            print("RESULT: NO SIGNIFICANT DIFFERENCE")
            return None, p, z
    else:
        print("RESULT: Insufficient data for comparison")
        return None, None, None

# ============================================================
# TEST 2: material_class=animal vs RI ratio
# ============================================================

def test_animal_class(recipes, folio_data, pp_middles, ri_middles):
    """Test: Animal materials should show higher RI and specific MIDDLEs"""
    print("\n" + "="*70)
    print("TEST 2: Animal Materials vs RI Ratio")
    print("="*70)
    print("Prediction: Animal-associated folios should have higher RI ratios")
    print("Mechanism: Animals are unique specimens, not interchangeable\n")

    # Find animal-associated folios based on MIDDLE presence
    animal_folios = set()
    herb_folios = set()

    for folio, data in folio_data.items():
        has_animal = any(m in ANIMAL_MIDDLES for m in data['middles'])
        if has_animal:
            animal_folios.add(folio)
        else:
            herb_folios.add(folio)

    # Compare RI ratios
    animal_ratios = []
    herb_ratios = []

    for folio in animal_folios:
        data = folio_data[folio]
        total = data['pp_count'] + data['ri_count']
        if total >= 5:
            animal_ratios.append(data['ri_count'] / total)

    for folio in herb_folios:
        data = folio_data[folio]
        total = data['pp_count'] + data['ri_count']
        if total >= 5:
            herb_ratios.append(data['ri_count'] / total)

    print(f"Animal-associated folios: n={len(animal_ratios)}")
    print(f"  Mean RI ratio: {statistics.mean(animal_ratios):.3f}" if animal_ratios else "  No data")
    print(f"  Animal MIDDLEs found: {len(ANIMAL_MIDDLES)}")

    print(f"\nHerb-only folios: n={len(herb_ratios)}")
    print(f"  Mean RI ratio: {statistics.mean(herb_ratios):.3f}" if herb_ratios else "  No data")

    if animal_ratios and herb_ratios:
        u, z, p = mann_whitney_u(animal_ratios, herb_ratios)
        print(f"\nMann-Whitney U: z={z:.3f}, p={p:.4f}")

        if p < 0.05 and statistics.mean(animal_ratios) > statistics.mean(herb_ratios):
            print("RESULT: SUPPORTS prediction (animal -> higher RI)")
            return True, p, z
        elif p < 0.05:
            print("RESULT: CONTRADICTS prediction")
            return False, p, z
        else:
            print("RESULT: NO SIGNIFICANT DIFFERENCE")
            return None, p, z

    return None, None, None

# ============================================================
# TEST 3: fire_degree=4 vs RI ratio
# ============================================================

def test_fire_degree(recipes, folio_classifications, folio_data):
    """Test: Extreme fire degrees should correlate with higher RI"""
    print("\n" + "="*70)
    print("TEST 3: Fire Degree Extremes vs RI Ratio")
    print("="*70)
    print("Prediction: PRECISION (fire=4) folios should have higher RI ratios")
    print("Mechanism: Special handling materials can't be substituted\n")

    precision_ratios = []
    standard_ratios = []

    for folio, data in folio_data.items():
        total = data['pp_count'] + data['ri_count']
        if total < 5:
            continue

        ri_ratio = data['ri_count'] / total
        folio_type = folio_classifications.get(folio, 'UNKNOWN')

        if folio_type == 'PRECISION':
            precision_ratios.append(ri_ratio)
        elif folio_type in ['WATER_STANDARD', 'WATER_GENTLE']:
            standard_ratios.append(ri_ratio)

    print(f"PRECISION folios: n={len(precision_ratios)}")
    if precision_ratios:
        print(f"  Mean RI ratio: {statistics.mean(precision_ratios):.3f}")

    print(f"\nSTANDARD folios: n={len(standard_ratios)}")
    if standard_ratios:
        print(f"  Mean RI ratio: {statistics.mean(standard_ratios):.3f}")

    if precision_ratios and standard_ratios:
        u, z, p = mann_whitney_u(precision_ratios, standard_ratios)
        print(f"\nMann-Whitney U: z={z:.3f}, p={p:.4f}")

        if p < 0.05 and statistics.mean(precision_ratios) > statistics.mean(standard_ratios):
            print("RESULT: SUPPORTS prediction (precision -> higher RI)")
            return True, p, z
        elif p < 0.05:
            print("RESULT: CONTRADICTS prediction")
            return False, p, z
        else:
            print("RESULT: NO SIGNIFICANT DIFFERENCE")
            return None, p, z

    return None, None, None

# ============================================================
# TEST 4: use_count (versatility) vs PP ratio
# ============================================================

def test_use_count(recipes, folio_classifications, folio_data):
    """Test: High use_count materials should correlate with higher PP"""
    print("\n" + "="*70)
    print("TEST 4: Versatility (use_count) vs PP Ratio")
    print("="*70)
    print("Prediction: High-use materials (versatile) should correlate with higher PP ratios")
    print("Mechanism: Versatile materials are standardized, interchangeable\n")

    # Categorize recipes by use_count
    high_use = [r for r in recipes if r.get('use_count', 0) >= 10]
    low_use = [r for r in recipes if r.get('use_count', 0) < 5]

    print(f"High-use recipes (>=10 uses): {len(high_use)}")
    print(f"Low-use recipes (<5 uses): {len(low_use)}")

    # Map to product types
    high_use_types = Counter(
        'PRECISION' if r.get('fire_degree') == 4 or r.get('material_class') == 'animal'
        else 'OIL_RESIN' if r.get('fire_degree') == 3
        else 'WATER_GENTLE' if r.get('fire_degree') == 1
        else 'WATER_STANDARD'
        for r in high_use
    )

    low_use_types = Counter(
        'PRECISION' if r.get('fire_degree') == 4 or r.get('material_class') == 'animal'
        else 'OIL_RESIN' if r.get('fire_degree') == 3
        else 'WATER_GENTLE' if r.get('fire_degree') == 1
        else 'WATER_STANDARD'
        for r in low_use
    )

    print(f"\nHigh-use type distribution: {dict(high_use_types)}")
    print(f"Low-use type distribution: {dict(low_use_types)}")

    # Get PP ratios for folios
    high_use_pp_ratios = []
    low_use_pp_ratios = []

    high_use_dominant_types = {t for t, c in high_use_types.items() if c > low_use_types.get(t, 0)}
    low_use_dominant_types = {t for t, c in low_use_types.items() if c > high_use_types.get(t, 0)}

    for folio, data in folio_data.items():
        total = data['pp_count'] + data['ri_count']
        if total < 5:
            continue

        pp_ratio = data['pp_count'] / total
        folio_type = folio_classifications.get(folio, 'UNKNOWN')

        if folio_type in high_use_dominant_types:
            high_use_pp_ratios.append(pp_ratio)
        elif folio_type in low_use_dominant_types:
            low_use_pp_ratios.append(pp_ratio)

    if high_use_pp_ratios and low_use_pp_ratios:
        print(f"\nHigh-use type folios: mean PP={statistics.mean(high_use_pp_ratios):.3f}, n={len(high_use_pp_ratios)}")
        print(f"Low-use type folios: mean PP={statistics.mean(low_use_pp_ratios):.3f}, n={len(low_use_pp_ratios)}")

        u, z, p = mann_whitney_u(high_use_pp_ratios, low_use_pp_ratios)
        print(f"\nMann-Whitney U: z={z:.3f}, p={p:.4f}")

        if p < 0.05 and statistics.mean(high_use_pp_ratios) > statistics.mean(low_use_pp_ratios):
            print("RESULT: SUPPORTS prediction (high-use -> higher PP)")
            return True, p, z
        elif p < 0.05:
            print("RESULT: CONTRADICTS prediction")
            return False, p, z
        else:
            print("RESULT: NO SIGNIFICANT DIFFERENCE")
            return None, p, z
    else:
        print("RESULT: Insufficient data")
        return None, None, None

# ============================================================
# TEST 5: PREFIX distribution by PP/RI dominance
# ============================================================

def test_prefix_distribution(folio_data):
    """Test: PP-dominant folios -> more qo-; RI-dominant -> more o-"""
    print("\n" + "="*70)
    print("TEST 5: PREFIX Distribution by PP/RI Dominance")
    print("="*70)
    print("Prediction: PP-dominant folios should have more qo- prefix (escape routes)")
    print("           RI-dominant folios should have more o- prefix (like labels)\n")

    pp_dominant_prefixes = []
    ri_dominant_prefixes = []

    for folio, data in folio_data.items():
        total = data['pp_count'] + data['ri_count']
        if total < 10:  # Need enough data
            continue

        pp_ratio = data['pp_count'] / total

        if pp_ratio > 0.5:
            pp_dominant_prefixes.extend(data['prefixes'])
        else:
            ri_dominant_prefixes.extend(data['prefixes'])

    pp_prefix_dist = Counter(pp_dominant_prefixes)
    ri_prefix_dist = Counter(ri_dominant_prefixes)

    pp_total = sum(pp_prefix_dist.values())
    ri_total = sum(ri_prefix_dist.values())

    print("PREFIX distribution:")
    print(f"\n{'PREFIX':<8} {'PP-dominant':<15} {'RI-dominant':<15} {'Difference':<15}")
    print("-" * 55)

    key_prefixes = ['qo', 'o', 'c', 's', 'd', 'y']
    for p in key_prefixes:
        pp_pct = 100 * pp_prefix_dist.get(p, 0) / pp_total if pp_total else 0
        ri_pct = 100 * ri_prefix_dist.get(p, 0) / ri_total if ri_total else 0
        diff = pp_pct - ri_pct
        direction = "PP higher" if diff > 0 else "RI higher"
        print(f"{p:<8} {pp_pct:>6.1f}%         {ri_pct:>6.1f}%         {diff:>+5.1f}% ({direction})")

    # Check qo specifically
    qo_pp = pp_prefix_dist.get('qo', 0) / pp_total if pp_total else 0
    qo_ri = ri_prefix_dist.get('qo', 0) / ri_total if ri_total else 0

    # Check o specifically
    o_pp = pp_prefix_dist.get('o', 0) / pp_total if pp_total else 0
    o_ri = ri_prefix_dist.get('o', 0) / ri_total if ri_total else 0

    print(f"\nKey findings:")
    print(f"  qo- prefix: PP-dominant={100*qo_pp:.1f}%, RI-dominant={100*qo_ri:.1f}%")
    print(f"  o-  prefix: PP-dominant={100*o_pp:.1f}%, RI-dominant={100*o_ri:.1f}%")

    qo_supports = qo_pp > qo_ri
    o_supports = o_ri > o_pp

    if qo_supports and o_supports:
        print("\nRESULT: SUPPORTS both predictions (qo->PP, o->RI)")
        return True, None, None
    elif qo_supports or o_supports:
        print("\nRESULT: PARTIAL SUPPORT")
        return None, None, None
    else:
        print("\nRESULT: CONTRADICTS predictions")
        return False, None, None

# ============================================================
# TEST 6: Processing state correlation
# ============================================================

def test_processing_state(recipes, folio_data, pp_middles, ri_middles):
    """Test: Chopped/processed -> PP; Whole/raw -> RI"""
    print("\n" + "="*70)
    print("TEST 6: Processing State Correlation")
    print("="*70)
    print("Prediction: Recipes with 'chopped/pounded' -> PP correlation")
    print("           Recipes with 'whole' specifications -> RI correlation\n")

    # Extract processing indicators from procedure_summary
    processed_recipes = []
    whole_recipes = []

    processing_terms = ['chop', 'pound', 'cut', 'crush', 'grind', 'press']
    whole_terms = ['whole', 'fresh', 'uncut']

    for recipe in recipes:
        summary = (recipe.get('procedure_summary') or '').lower()

        if any(term in summary for term in processing_terms):
            processed_recipes.append(recipe)
        elif any(term in summary for term in whole_terms):
            whole_recipes.append(recipe)

    print(f"Processed recipes (chop/pound/cut/crush): {len(processed_recipes)}")
    print(f"Whole recipes (whole/fresh): {len(whole_recipes)}")

    if processed_recipes:
        print(f"\nExamples of processed:")
        for r in processed_recipes[:3]:
            print(f"  - {r.get('name_english', 'Unknown')}: {r.get('procedure_summary', '')[:60]}...")

    if whole_recipes:
        print(f"\nExamples of whole:")
        for r in whole_recipes[:3]:
            print(f"  - {r.get('name_english', 'Unknown')}: {r.get('procedure_summary', '')[:60]}...")

    # Map to product types and compare PP ratios
    # This is a structural correlation test
    print("\nNote: Direct folio-level correlation requires manual pharma label mapping")
    print("      (See C523-C525 for label-level validation)")

    return None, None, None

# ============================================================
# TEST 7: parts_used complexity vs RI
# ============================================================

def test_parts_complexity(recipes, folio_classifications, folio_data):
    """Test: Multiple parts_used -> Higher RI"""
    print("\n" + "="*70)
    print("TEST 7: Parts Complexity vs RI Ratio")
    print("="*70)
    print("Prediction: Recipes using multiple parts should correlate with higher RI")
    print("Mechanism: Complex specifications need specific identification\n")

    # Count parts per recipe
    simple_recipes = []  # 1 part
    complex_recipes = []  # 2+ parts

    for recipe in recipes:
        parts = recipe.get('parts_used', [])
        if len(parts) <= 1:
            simple_recipes.append(recipe)
        else:
            complex_recipes.append(recipe)

    print(f"Simple recipes (1 part): {len(simple_recipes)}")
    print(f"Complex recipes (2+ parts): {len(complex_recipes)}")

    # Map to product types
    simple_types = Counter(
        'PRECISION' if r.get('fire_degree') == 4 or r.get('material_class') == 'animal'
        else 'OIL_RESIN' if r.get('fire_degree') == 3
        else 'WATER_GENTLE' if r.get('fire_degree') == 1
        else 'WATER_STANDARD'
        for r in simple_recipes
    )

    complex_types = Counter(
        'PRECISION' if r.get('fire_degree') == 4 or r.get('material_class') == 'animal'
        else 'OIL_RESIN' if r.get('fire_degree') == 3
        else 'WATER_GENTLE' if r.get('fire_degree') == 1
        else 'WATER_STANDARD'
        for r in complex_recipes
    )

    print(f"\nSimple type distribution: {dict(simple_types)}")
    print(f"Complex type distribution: {dict(complex_types)}")

    return None, None, None

# ============================================================
# MAIN
# ============================================================

def main():
    print("BRUNSCHWIG PP/RI PREDICTION TEST")
    print("="*70)
    print("Testing predictions from new PP/RI understanding against Brunschwig data")
    print("="*70)

    # Load all data
    print("\nLoading data...")
    recipes = load_brunschwig_recipes()
    folio_classifications = load_folio_classifications()
    folio_data, pp_middles, ri_middles = load_transcript()

    print(f"  Brunschwig recipes: {len(recipes)}")
    print(f"  Voynich A folios: {len(folio_data)}")
    print(f"  PP MIDDLEs: {len(pp_middles)}")
    print(f"  RI MIDDLEs: {len(ri_middles)}")
    print(f"  Folio classifications: {len(folio_classifications)}")

    # Run all tests
    results = {}

    results['test1_has_procedure'] = test_has_procedure(recipes, folio_classifications, folio_data)
    results['test2_animal_class'] = test_animal_class(recipes, folio_data, pp_middles, ri_middles)
    results['test3_fire_degree'] = test_fire_degree(recipes, folio_classifications, folio_data)
    results['test4_use_count'] = test_use_count(recipes, folio_classifications, folio_data)
    results['test5_prefix_dist'] = test_prefix_distribution(folio_data)
    results['test6_processing'] = test_processing_state(recipes, folio_data, pp_middles, ri_middles)
    results['test7_parts_complexity'] = test_parts_complexity(recipes, folio_classifications, folio_data)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    supports = 0
    contradicts = 0
    inconclusive = 0

    for test_name, (result, p, z) in results.items():
        status = "SUPPORTS" if result == True else "CONTRADICTS" if result == False else "INCONCLUSIVE"
        p_str = f"p={p:.4f}" if p is not None else "N/A"
        print(f"  {test_name}: {status} ({p_str})")

        if result == True:
            supports += 1
        elif result == False:
            contradicts += 1
        else:
            inconclusive += 1

    print(f"\nOverall: {supports} support, {contradicts} contradict, {inconclusive} inconclusive")

    # Save results
    output = {
        'phase': 'BRUNSCHWIG_PP_RI_TEST',
        'date': '2026-01-24',
        'summary': {
            'supports': supports,
            'contradicts': contradicts,
            'inconclusive': inconclusive
        },
        'tests': {
            name: {
                'result': 'supports' if r == True else 'contradicts' if r == False else 'inconclusive',
                'p_value': p,
                'z_score': z
            }
            for name, (r, p, z) in results.items()
        }
    }

    output_dir = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_PP_RI_TEST' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / 'pp_ri_prediction_test.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_dir / 'pp_ri_prediction_test.json'}")

if __name__ == '__main__':
    main()
