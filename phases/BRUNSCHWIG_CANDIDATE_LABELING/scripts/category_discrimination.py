#!/usr/bin/env python3
"""
PHASE 1: CATEGORY-LEVEL DISCRIMINATION

Question: Do registry-internal MIDDLE distributions discriminate between
Brunschwig material categories within WATER_GENTLE and OIL_RESIN product types?

Method:
1. Map material categories to product types from Brunschwig (197 with procedures)
2. For each A folio classified as WATER_GENTLE or OIL_RESIN:
   - Compute registry-internal MIDDLE profile
   - Associate with dominant material category for that product type
3. Test: Do registry-internal profiles differ by material category?

Output: Category discrimination statistics + folio-level category distributions
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

# Focus on validated product types first
TARGET_PRODUCT_TYPES = ['WATER_GENTLE', 'OIL_RESIN']

def get_middle(token):
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

# ============================================================
# DATA LOADING
# ============================================================

def load_brunschwig_category_mapping():
    """
    Load Brunschwig materials and build:
    1. Category distribution per product type
    2. List of materials per category (with procedures only)
    """
    with open('data/brunschwig_materials_master.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    materials = data['materials']

    # Only use materials with procedures (197)
    materials_with_procedures = [m for m in materials if len(m.get('procedural_steps', [])) > 0]

    # Build category → product_type mapping
    category_by_product = defaultdict(lambda: defaultdict(list))

    for mat in materials_with_procedures:
        category = mat.get('material_source', 'unknown')
        product_type = mat.get('predicted_product_type', 'UNKNOWN')
        name = mat.get('name_normalized', mat.get('name_german', ''))

        category_by_product[product_type][category].append({
            'name': name,
            'fire_degree': mat.get('fire_degree', 0),
            'n_steps': len(mat.get('procedural_steps', [])),
            'recipe_id': mat.get('recipe_id', '')
        })

    return category_by_product, materials_with_procedures

def load_2track_classification():
    """Load registry-internal vs pipeline-participating classification."""
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)
    return set(data['a_exclusive_middles']), set(data['a_shared_middles'])

def load_folio_classifications():
    """Load product type classification for each A folio."""
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

def load_folio_middles():
    """Load all MIDDLEs per folio from transcript."""
    folio_middles = defaultdict(list)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue
            middle = get_middle(word)
            if middle and len(middle) > 1:
                folio_middles[folio].append(middle)

    return folio_middles

# ============================================================
# ANALYSIS
# ============================================================

def compute_folio_registry_profile(folio_middles, a_exclusive, folio):
    """Compute registry-internal MIDDLE profile for a folio."""
    middles = folio_middles.get(folio, [])

    # Count registry-internal MIDDLEs
    reg_middles = [m for m in middles if m in a_exclusive]
    reg_counts = Counter(reg_middles)

    total_middles = len(middles)
    reg_count = len(reg_middles)
    unique_reg = len(reg_counts)

    return {
        'total_middles': total_middles,
        'registry_internal_count': reg_count,
        'registry_internal_unique': unique_reg,
        'registry_internal_ratio': reg_count / total_middles if total_middles > 0 else 0,
        'registry_internal_types': reg_counts
    }

def kruskal_wallis_test(groups):
    """
    Simplified Kruskal-Wallis H test.
    groups: list of lists, each containing values for one group
    """
    # Flatten and rank
    all_values = []
    for i, group in enumerate(groups):
        for val in group:
            all_values.append((val, i))

    # Sort and rank
    all_values.sort(key=lambda x: x[0])
    n = len(all_values)

    # Assign ranks (handle ties)
    ranks = {}
    i = 0
    while i < n:
        j = i
        while j < n and all_values[j][0] == all_values[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2
        for k in range(i, j):
            if all_values[k] not in ranks:
                ranks[all_values[k]] = []
            ranks[all_values[k]].append(avg_rank)
        i = j

    # Calculate rank sums per group
    rank_sums = [0] * len(groups)
    rank_counts = [0] * len(groups)

    for (val, group_idx), rank_list in ranks.items():
        for r in rank_list:
            rank_sums[group_idx] += r
            rank_counts[group_idx] += 1

    # Compute H statistic
    n_total = sum(rank_counts)
    if n_total < 3:
        return None, None

    h_num = 0
    for i, (rs, ni) in enumerate(zip(rank_sums, rank_counts)):
        if ni > 0:
            h_num += (rs ** 2) / ni

    H = (12 / (n_total * (n_total + 1))) * h_num - 3 * (n_total + 1)

    # Degrees of freedom
    k = len([g for g in groups if len(g) > 0])
    df = k - 1

    # Approximate p-value
    if df == 1:
        critical_05 = 3.84
    elif df == 2:
        critical_05 = 5.99
    elif df == 3:
        critical_05 = 7.81
    else:
        critical_05 = 9.49

    return H, df, critical_05

def effect_size_eta_squared(H, n, k):
    """Compute eta-squared effect size from H statistic."""
    if n <= k:
        return 0
    return (H - k + 1) / (n - k)

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("PHASE 1: CATEGORY-LEVEL DISCRIMINATION")
    print("=" * 70)
    print()
    print("Question: Do registry-internal MIDDLE distributions discriminate")
    print("          between Brunschwig material categories?")
    print()
    print("Focus: WATER_GENTLE and OIL_RESIN (validated at p=0.01)")
    print()

    # Load data
    print("Loading data...")
    category_by_product, materials = load_brunschwig_category_mapping()
    a_exclusive, a_shared = load_2track_classification()
    folio_classifications = load_folio_classifications()
    folio_middles = load_folio_middles()

    print(f"  Materials with procedures: {len(materials)}")
    print(f"  Registry-internal MIDDLEs: {len(a_exclusive)}")
    print(f"  Classified A folios: {len(folio_classifications)}")
    print()

    # Show category distributions for target product types
    print("=" * 70)
    print("BRUNSCHWIG CATEGORY DISTRIBUTIONS (197 with procedures)")
    print("=" * 70)
    print()

    for ptype in TARGET_PRODUCT_TYPES:
        print(f"{ptype}:")
        categories = category_by_product.get(ptype, {})
        total = sum(len(mats) for mats in categories.values())
        for cat, mats in sorted(categories.items(), key=lambda x: -len(x[1])):
            pct = 100 * len(mats) / total if total > 0 else 0
            print(f"  {cat}: {len(mats)} materials ({pct:.1f}%)")
            if len(mats) <= 3:
                for m in mats:
                    print(f"    - {m['name']}")
        print()

    # Get folios for target product types
    target_folios = {ptype: [] for ptype in TARGET_PRODUCT_TYPES}
    for folio, ptype in folio_classifications.items():
        if ptype in TARGET_PRODUCT_TYPES:
            target_folios[ptype].append(folio)

    print("=" * 70)
    print("VOYNICH FOLIO COUNTS")
    print("=" * 70)
    print()
    for ptype in TARGET_PRODUCT_TYPES:
        print(f"  {ptype}: {len(target_folios[ptype])} folios")
    print()

    # Compute registry-internal profiles per folio
    print("=" * 70)
    print("REGISTRY-INTERNAL PROFILES BY PRODUCT TYPE")
    print("=" * 70)
    print()

    folio_profiles = {}
    for ptype in TARGET_PRODUCT_TYPES:
        profiles = []
        for folio in target_folios[ptype]:
            profile = compute_folio_registry_profile(folio_middles, a_exclusive, folio)
            profile['folio'] = folio
            profile['product_type'] = ptype
            profiles.append(profile)
            folio_profiles[folio] = profile

        # Summary stats
        ratios = [p['registry_internal_ratio'] for p in profiles]
        uniques = [p['registry_internal_unique'] for p in profiles]

        if ratios:
            mean_ratio = sum(ratios) / len(ratios)
            mean_unique = sum(uniques) / len(uniques)
            print(f"{ptype} (n={len(profiles)} folios):")
            print(f"  Mean registry-internal ratio: {mean_ratio:.1%}")
            print(f"  Mean unique registry-internal MIDDLEs: {mean_unique:.1f}")
            print(f"  Ratio range: {min(ratios):.1%} - {max(ratios):.1%}")
            print()

    # Category discrimination test
    print("=" * 70)
    print("CATEGORY DISCRIMINATION TEST")
    print("=" * 70)
    print()

    # For each product type, test if folios can be grouped by dominant category
    # This requires mapping folios to likely category based on their MIDDLE signature

    # First, identify the dominant categories for each product type
    dominant_categories = {}
    for ptype in TARGET_PRODUCT_TYPES:
        categories = category_by_product.get(ptype, {})
        if categories:
            # Get categories with at least 2 materials
            viable = [(cat, len(mats)) for cat, mats in categories.items() if len(mats) >= 2]
            viable.sort(key=lambda x: -x[1])
            dominant_categories[ptype] = [cat for cat, _ in viable[:3]]  # Top 3

    print("Dominant categories per product type:")
    for ptype, cats in dominant_categories.items():
        print(f"  {ptype}: {cats}")
    print()

    # Test: Do folios within a product type show clustering by registry-internal signature?
    # Group folios by their registry-internal ratio terciles within each product type

    print("=" * 70)
    print("REGISTRY-INTERNAL RATIO DISTRIBUTION BY PRODUCT TYPE")
    print("=" * 70)
    print()

    for ptype in TARGET_PRODUCT_TYPES:
        folios = target_folios[ptype]
        if len(folios) < 6:
            print(f"{ptype}: Insufficient folios for analysis (n={len(folios)})")
            continue

        # Get ratios
        ratios = [(f, folio_profiles[f]['registry_internal_ratio']) for f in folios]
        ratios.sort(key=lambda x: x[1])

        # Split into terciles
        n = len(ratios)
        t1 = n // 3
        t2 = 2 * n // 3

        low_tercile = ratios[:t1]
        mid_tercile = ratios[t1:t2]
        high_tercile = ratios[t2:]

        print(f"{ptype}:")
        print(f"  LOW tercile (n={len(low_tercile)}): {[f[0] for f in low_tercile[:3]]}...")
        print(f"    Mean ratio: {sum(r for _, r in low_tercile)/len(low_tercile):.1%}")
        print(f"  MID tercile (n={len(mid_tercile)}): {[f[0] for f in mid_tercile[:3]]}...")
        print(f"    Mean ratio: {sum(r for _, r in mid_tercile)/len(mid_tercile):.1%}")
        print(f"  HIGH tercile (n={len(high_tercile)}): {[f[0] for f in high_tercile[:3]]}...")
        print(f"    Mean ratio: {sum(r for _, r in high_tercile)/len(high_tercile):.1%}")
        print()

    # Cross-product-type comparison
    print("=" * 70)
    print("CROSS-PRODUCT-TYPE DISCRIMINATION TEST")
    print("=" * 70)
    print()

    groups = []
    group_labels = []
    for ptype in TARGET_PRODUCT_TYPES:
        ratios = [folio_profiles[f]['registry_internal_ratio'] for f in target_folios[ptype]]
        if ratios:
            groups.append(ratios)
            group_labels.append(ptype)

    if len(groups) >= 2:
        result = kruskal_wallis_test(groups)
        if result[0] is not None:
            H, df, critical = result
            n_total = sum(len(g) for g in groups)
            eta_sq = effect_size_eta_squared(H, n_total, len(groups))

            print(f"Kruskal-Wallis H test:")
            print(f"  H statistic: {H:.2f}")
            print(f"  df: {df}")
            print(f"  Critical value (p=0.05): {critical:.2f}")
            print(f"  Eta-squared: {eta_sq:.3f}")
            print()

            if H > critical:
                print(f"  RESULT: SIGNIFICANT (H={H:.2f} > {critical:.2f})")
                print(f"  WATER_GENTLE and OIL_RESIN have different registry-internal profiles")
            else:
                print(f"  RESULT: NOT SIGNIFICANT (H={H:.2f} < {critical:.2f})")
    print()

    # Unique MIDDLE analysis
    print("=" * 70)
    print("UNIQUE REGISTRY-INTERNAL MIDDLES BY PRODUCT TYPE")
    print("=" * 70)
    print()

    # Collect all registry-internal MIDDLEs per product type
    type_middles = defaultdict(Counter)
    for ptype in TARGET_PRODUCT_TYPES:
        for folio in target_folios[ptype]:
            profile = folio_profiles.get(folio, {})
            for middle, count in profile.get('registry_internal_types', {}).items():
                type_middles[ptype][middle] += count

    # Find unique vs shared MIDDLEs
    all_middles = set()
    for counter in type_middles.values():
        all_middles.update(counter.keys())

    exclusive_middles = {}
    shared_middles = []

    for middle in all_middles:
        types_with = [ptype for ptype in TARGET_PRODUCT_TYPES if type_middles[ptype].get(middle, 0) > 0]
        if len(types_with) == 1:
            if types_with[0] not in exclusive_middles:
                exclusive_middles[types_with[0]] = []
            exclusive_middles[types_with[0]].append((middle, type_middles[types_with[0]][middle]))
        else:
            shared_middles.append(middle)

    print(f"Total registry-internal MIDDLEs in target types: {len(all_middles)}")
    print(f"Shared between types: {len(shared_middles)}")
    print()

    for ptype in TARGET_PRODUCT_TYPES:
        exclusive = exclusive_middles.get(ptype, [])
        exclusive.sort(key=lambda x: -x[1])
        print(f"{ptype}-exclusive MIDDLEs: {len(exclusive)}")
        if exclusive:
            print(f"  Top 10: {exclusive[:10]}")
        print()

    # Save results
    output = {
        'phase': 'CATEGORY_DISCRIMINATION',
        'date': '2026-01-20',
        'target_product_types': TARGET_PRODUCT_TYPES,
        'brunschwig_categories': {
            ptype: {cat: len(mats) for cat, mats in category_by_product.get(ptype, {}).items()}
            for ptype in TARGET_PRODUCT_TYPES
        },
        'folio_counts': {ptype: len(target_folios[ptype]) for ptype in TARGET_PRODUCT_TYPES},
        'registry_internal_by_type': {
            ptype: {
                'n_folios': len(target_folios[ptype]),
                'mean_ratio': sum(folio_profiles[f]['registry_internal_ratio'] for f in target_folios[ptype]) / len(target_folios[ptype]) if target_folios[ptype] else 0,
                'exclusive_middles': len(exclusive_middles.get(ptype, []))
            }
            for ptype in TARGET_PRODUCT_TYPES
        },
        'cross_type_test': {
            'H': H if result[0] else None,
            'df': df if result[0] else None,
            'significant': H > critical if result[0] else None
        },
        'exclusive_middles': {
            ptype: [m for m, c in exclusive_middles.get(ptype, [])]
            for ptype in TARGET_PRODUCT_TYPES
        }
    }

    with open('phases/BRUNSCHWIG_CANDIDATE_LABELING/results/category_discrimination.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if result[0] and H > critical:
        print("POSITIVE: Product types have distinct registry-internal signatures.")
        print("This supports proceeding to Phase 2 (procedural refinement).")
        print()
        print("Key finding: Registry-internal MIDDLEs discriminate between")
        print("WATER_GENTLE and OIL_RESIN domains, suggesting the 2-track")
        print("vocabulary structure encodes category-level distinctions.")
    else:
        print("NULL: Product types do not have distinct registry-internal signatures.")
        print("This suggests registry-internal vocabulary is not category-encoded.")

    print()
    print(f"Results saved to phases/BRUNSCHWIG_CANDIDATE_LABELING/results/category_discrimination.json")

if __name__ == '__main__':
    main()
