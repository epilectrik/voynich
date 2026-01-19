#!/usr/bin/env python3
"""
PCC INTEGRATION TESTS (Track 4)

Test whether PCC findings (closure patterns, breadth, clusters) correlate with
Brunschwig product types.

Tests:
  BRU-A-4.1: Product Type x Closure Pattern
  BRU-A-4.2: Product Type x Breadth (hub-dominant vs tail-dominant)
  BRU-A-4.3: Product Type x Cluster Membership
"""

import csv
import json
from collections import defaultdict, Counter
from scipy import stats
import math

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

# Closure suffixes from PCC findings
CLOSURE_SUFFIXES = {
    'y': 'y-closure',
    'n': 'n-closure',
    'm': 'm-closure',
    'in': 'in-closure',
    'iin': 'iin-closure',
    'aiin': 'aiin-closure'
}

def get_middle(token):
    """Extract MIDDLE from token."""
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

def get_closure_type(token):
    """Identify closure suffix type."""
    for suffix, name in sorted(CLOSURE_SUFFIXES.items(), key=lambda x: -len(x[0])):
        if token.endswith(suffix):
            return name
    return 'other'

# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """Load A tokens with H-only filter and product classifications."""

    # Load product classifications
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    classifications = data['a_folio_classifications']

    # Load A tokens
    folio_tokens = defaultdict(list)
    folio_lines = defaultdict(lambda: defaultdict(list))

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            line_num = row.get('line', '').strip()

            if language != 'A' or not word:
                continue
            if word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            folio_tokens[folio].append(word)
            folio_lines[folio][line_num].append(word)

    return folio_tokens, folio_lines, classifications

# ============================================================
# TEST 4.1: PRODUCT TYPE x CLOSURE PATTERN
# ============================================================

def test_closure_pattern(folio_tokens, folio_lines, classifications):
    """Test if product types show different closure morphology."""

    print("=" * 70)
    print("TEST BRU-A-4.1: PRODUCT TYPE x CLOSURE PATTERN")
    print("=" * 70)
    print()
    print("Question: Do product types show different closure morphology in A entries?")
    print()

    # Group folios by product type
    product_folios = defaultdict(list)
    for folio, product in classifications.items():
        product_folios[product].append(folio)

    # Calculate closure distribution by product type
    product_closure = {}

    for product, folios in product_folios.items():
        closure_counts = Counter()
        final_tokens = []

        for folio in folios:
            for line_num, tokens in folio_lines[folio].items():
                if tokens:
                    final_token = tokens[-1]  # Last token in line
                    final_tokens.append(final_token)
                    closure_type = get_closure_type(final_token)
                    closure_counts[closure_type] += 1

        total = sum(closure_counts.values())
        if total > 0:
            product_closure[product] = {
                'counts': dict(closure_counts),
                'total': total,
                'ratios': {k: v/total for k, v in closure_counts.items()}
            }

    # Display results
    print("Closure distribution at line-final position:")
    print()

    closure_types = ['y-closure', 'n-closure', 'm-closure', 'in-closure', 'other']

    print(f"{'Product':<20} " + " ".join(f"{ct:<12}" for ct in closure_types))
    print("-" * 80)

    for product in sorted(product_closure.keys()):
        data = product_closure[product]
        row = f"{product:<20} "
        for ct in closure_types:
            pct = 100 * data['ratios'].get(ct, 0)
            row += f"{pct:>10.1f}% "
        print(row)

    print()

    # Statistical test: chi-square for independence
    products = sorted(product_closure.keys())
    contingency = []
    for product in products:
        row = [product_closure[product]['counts'].get(ct, 0) for ct in closure_types]
        contingency.append(row)

    if len(contingency) >= 2:
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        print(f"Chi-square test for independence:")
        print(f"  chi2 = {chi2:.2f}, df = {dof}, p = {p_value:.4f}")

        if p_value < 0.05:
            print("  -> SIGNIFICANT: Product types have different closure patterns")
            result = "SIGNIFICANT"
        else:
            print("  -> NOT SIGNIFICANT: Closure patterns similar across types")
            result = "NOT_SIGNIFICANT"
    else:
        result = "INSUFFICIENT_DATA"
        p_value = 1.0

    print()

    # Specific comparisons
    print("Notable differences:")
    if 'PRECISION' in product_closure and 'OIL_RESIN' in product_closure:
        prec_y = 100 * product_closure['PRECISION']['ratios'].get('y-closure', 0)
        oil_y = 100 * product_closure['OIL_RESIN']['ratios'].get('y-closure', 0)
        diff = prec_y - oil_y
        print(f"  y-closure: PRECISION={prec_y:.1f}% vs OIL_RESIN={oil_y:.1f}% (diff={diff:+.1f}%)")

    if 'WATER_GENTLE' in product_closure and 'WATER_STANDARD' in product_closure:
        gentle_y = 100 * product_closure['WATER_GENTLE']['ratios'].get('y-closure', 0)
        std_y = 100 * product_closure['WATER_STANDARD']['ratios'].get('y-closure', 0)
        diff = gentle_y - std_y
        print(f"  y-closure: WATER_GENTLE={gentle_y:.1f}% vs WATER_STANDARD={std_y:.1f}% (diff={diff:+.1f}%)")

    print()

    return {
        'test': 'BRU-A-4.1',
        'question': 'Product Type x Closure Pattern',
        'result': result,
        'p_value': p_value,
        'data': {p: product_closure[p]['ratios'] for p in product_closure}
    }

# ============================================================
# TEST 4.2: PRODUCT TYPE x BREADTH
# ============================================================

def test_breadth(folio_tokens, classifications):
    """Test if product types align with hub-dominant vs tail-dominant."""

    print("=" * 70)
    print("TEST BRU-A-4.2: PRODUCT TYPE x BREADTH")
    print("=" * 70)
    print()
    print("Question: Do product types align with A-AZC breadth categories?")
    print("Hypothesis: PRECISION entries may be more tail-dominant (narrow breadth)")
    print()

    # Calculate MIDDLE frequency across all A folios
    all_middles = Counter()
    for folio, tokens in folio_tokens.items():
        for token in tokens:
            middle = get_middle(token)
            if middle and len(middle) > 1:
                all_middles[middle] += 1

    # Define hub vs tail threshold (top 10% = hub)
    total_middle_types = len(all_middles)
    sorted_middles = sorted(all_middles.items(), key=lambda x: -x[1])
    hub_threshold = int(total_middle_types * 0.10)
    hub_middles = set(m for m, _ in sorted_middles[:hub_threshold])
    tail_middles = set(m for m, _ in sorted_middles[int(total_middle_types * 0.50):])

    print(f"MIDDLE classification:")
    print(f"  Total unique MIDDLEs: {total_middle_types}")
    print(f"  Hub MIDDLEs (top 10%): {len(hub_middles)}")
    print(f"  Tail MIDDLEs (bottom 50%): {len(tail_middles)}")
    print()

    # Calculate hub/tail ratio per folio
    folio_breadth = {}
    for folio, tokens in folio_tokens.items():
        middles = [get_middle(t) for t in tokens]
        middles = [m for m in middles if m and len(m) > 1]

        hub_count = sum(1 for m in middles if m in hub_middles)
        tail_count = sum(1 for m in middles if m in tail_middles)
        total = len(middles)

        if total > 0:
            folio_breadth[folio] = {
                'hub_ratio': hub_count / total,
                'tail_ratio': tail_count / total,
                'total': total
            }

    # Group by product type
    product_folios = defaultdict(list)
    for folio, product in classifications.items():
        if folio in folio_breadth:
            product_folios[product].append(folio)

    # Calculate mean breadth per product type
    product_breadth = {}
    for product, folios in product_folios.items():
        hub_ratios = [folio_breadth[f]['hub_ratio'] for f in folios]
        tail_ratios = [folio_breadth[f]['tail_ratio'] for f in folios]

        product_breadth[product] = {
            'mean_hub': sum(hub_ratios) / len(hub_ratios) if hub_ratios else 0,
            'mean_tail': sum(tail_ratios) / len(tail_ratios) if tail_ratios else 0,
            'n_folios': len(folios),
            'hub_ratios': hub_ratios,
            'tail_ratios': tail_ratios
        }

    # Display results
    print("Product type breadth profiles:")
    print()
    print(f"{'Product':<20} {'Hub Ratio':<12} {'Tail Ratio':<12} {'N Folios':<10}")
    print("-" * 60)

    for product in sorted(product_breadth.keys()):
        data = product_breadth[product]
        print(f"{product:<20} {data['mean_hub']:>10.1%}   {data['mean_tail']:>10.1%}   {data['n_folios']:>8}")

    print()

    # Statistical test: ANOVA on tail ratios
    groups = [product_breadth[p]['tail_ratios'] for p in sorted(product_breadth.keys())
              if len(product_breadth[p]['tail_ratios']) >= 2]

    if len(groups) >= 2 and all(len(g) >= 2 for g in groups):
        f_stat, p_value = stats.f_oneway(*groups)
        print(f"ANOVA on tail ratios:")
        print(f"  F = {f_stat:.2f}, p = {p_value:.4f}")

        if p_value < 0.05:
            print("  -> SIGNIFICANT: Product types have different tail ratios")
            result = "SIGNIFICANT"
        else:
            print("  -> NOT SIGNIFICANT: Tail ratios similar across types")
            result = "NOT_SIGNIFICANT"
    else:
        result = "INSUFFICIENT_DATA"
        p_value = 1.0
        print("  Insufficient data for ANOVA")

    print()

    # Specific hypothesis: Is PRECISION more tail-dominant?
    if 'PRECISION' in product_breadth:
        prec_tail = product_breadth['PRECISION']['mean_tail']
        other_tails = [product_breadth[p]['mean_tail'] for p in product_breadth if p != 'PRECISION']
        mean_other = sum(other_tails) / len(other_tails) if other_tails else 0

        print(f"Hypothesis test: Is PRECISION more tail-dominant?")
        print(f"  PRECISION tail ratio: {prec_tail:.1%}")
        print(f"  Other types mean: {mean_other:.1%}")
        print(f"  Difference: {prec_tail - mean_other:+.1%}")

        if prec_tail > mean_other:
            print("  -> SUPPORTED: PRECISION is more tail-dominant")
        else:
            print("  -> NOT SUPPORTED: PRECISION is not more tail-dominant")

    print()

    return {
        'test': 'BRU-A-4.2',
        'question': 'Product Type x Breadth',
        'result': result,
        'p_value': p_value,
        'data': {p: {'hub': product_breadth[p]['mean_hub'],
                     'tail': product_breadth[p]['mean_tail']}
                 for p in product_breadth}
    }

# ============================================================
# TEST 4.3: PRODUCT TYPE x CLUSTER MEMBERSHIP
# ============================================================

def test_cluster_membership(folio_tokens, folio_lines, classifications):
    """Test if product types cluster spatially or interleave."""

    print("=" * 70)
    print("TEST BRU-A-4.3: PRODUCT TYPE x CLUSTER MEMBERSHIP")
    print("=" * 70)
    print()
    print("Question: Do product types cluster spatially or interleave in A?")
    print("Hypothesis: Clusters may be product-homogeneous (same process)")
    print()

    # Build adjacency clusters based on MIDDLE overlap (from PCC)
    # Two folios are adjacent if they share significant MIDDLE vocabulary

    folio_middle_sets = {}
    for folio, tokens in folio_tokens.items():
        middles = set(get_middle(t) for t in tokens)
        middles = set(m for m in middles if m and len(m) > 1)
        folio_middle_sets[folio] = middles

    # Calculate Jaccard similarity between all folio pairs
    def jaccard(s1, s2):
        if not s1 or not s2:
            return 0
        return len(s1 & s2) / len(s1 | s2)

    # Find clusters (folios with Jaccard > 0.10)
    MIN_JACCARD = 0.10
    clusters = []
    used = set()

    classified_folios = list(classifications.keys())

    for i, f1 in enumerate(classified_folios):
        if f1 in used or f1 not in folio_middle_sets:
            continue

        cluster = [f1]
        for f2 in classified_folios[i+1:]:
            if f2 in used or f2 not in folio_middle_sets:
                continue

            j = jaccard(folio_middle_sets[f1], folio_middle_sets[f2])
            if j >= MIN_JACCARD:
                cluster.append(f2)

        if len(cluster) >= 2:
            clusters.append(cluster)
            used.update(cluster)

    print(f"Found {len(clusters)} clusters (Jaccard >= {MIN_JACCARD})")
    print()

    # Analyze cluster composition
    homogeneous = 0
    mixed = 0
    cluster_details = []

    for cluster in clusters:
        products = [classifications.get(f, 'UNKNOWN') for f in cluster]
        unique_products = set(products)

        is_homogeneous = len(unique_products) == 1
        if is_homogeneous:
            homogeneous += 1
        else:
            mixed += 1

        cluster_details.append({
            'folios': cluster,
            'products': products,
            'homogeneous': is_homogeneous
        })

    total_clusters = len(clusters)

    print(f"Cluster composition:")
    print(f"  Homogeneous (single product type): {homogeneous} ({100*homogeneous/total_clusters:.1f}%)" if total_clusters > 0 else "  No clusters found")
    print(f"  Mixed (multiple product types): {mixed} ({100*mixed/total_clusters:.1f}%)" if total_clusters > 0 else "")
    print()

    # Show example clusters
    print("Example clusters:")
    for i, cd in enumerate(cluster_details[:5]):
        status = "HOMOGENEOUS" if cd['homogeneous'] else "MIXED"
        print(f"  Cluster {i+1}: {cd['folios'][:3]}... -> {set(cd['products'])} [{status}]")

    print()

    # Statistical test: is homogeneity higher than expected by chance?
    # Under null hypothesis (random), expected homogeneity depends on product distribution
    product_counts = Counter(classifications.values())
    total_folios = sum(product_counts.values())

    # Expected homogeneity under random = sum(p_i^2) for cluster of size 2
    expected_homog = sum((c/total_folios)**2 for c in product_counts.values())
    observed_homog = homogeneous / total_clusters if total_clusters > 0 else 0

    print(f"Homogeneity analysis:")
    print(f"  Observed homogeneity: {observed_homog:.1%}")
    print(f"  Expected under random: {expected_homog:.1%}")
    print(f"  Ratio: {observed_homog/expected_homog:.2f}x" if expected_homog > 0 else "  N/A")

    # Binomial test
    if total_clusters > 0:
        # Use binomtest (scipy >= 1.7) or fallback
        try:
            result_obj = stats.binomtest(homogeneous, total_clusters, expected_homog, alternative='greater')
            result_binom = result_obj.pvalue
        except AttributeError:
            # Fallback for older scipy
            result_binom = stats.binom_test(homogeneous, total_clusters, expected_homog, alternative='greater')
        print(f"  Binomial test p-value: {result_binom:.4f}")

        if result_binom < 0.05:
            print("  -> SIGNIFICANT: Clusters are more homogeneous than expected")
            result = "SIGNIFICANT"
        else:
            print("  -> NOT SIGNIFICANT: Cluster homogeneity consistent with random")
            result = "NOT_SIGNIFICANT"
        p_value = result_binom
    else:
        result = "INSUFFICIENT_DATA"
        p_value = 1.0

    print()

    return {
        'test': 'BRU-A-4.3',
        'question': 'Product Type x Cluster Membership',
        'result': result,
        'p_value': p_value,
        'data': {
            'total_clusters': total_clusters,
            'homogeneous': homogeneous,
            'mixed': mixed,
            'observed_homogeneity': observed_homog,
            'expected_homogeneity': expected_homog
        }
    }

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("PCC INTEGRATION TESTS (Track 4)")
    print("=" * 70)
    print()
    print("Testing correlation between PCC findings and Brunschwig product types")
    print()

    # Load data
    folio_tokens, folio_lines, classifications = load_data()

    print(f"Loaded {len(folio_tokens)} A folios")
    print(f"Product classifications: {len(classifications)} folios")
    print()

    # Run tests
    results = []

    results.append(test_closure_pattern(folio_tokens, folio_lines, classifications))
    results.append(test_breadth(folio_tokens, classifications))
    results.append(test_cluster_membership(folio_tokens, folio_lines, classifications))

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    print(f"{'Test':<40} {'Result':<20} {'p-value':<10}")
    print("-" * 70)
    for r in results:
        print(f"{r['question']:<40} {r['result']:<20} {r['p_value']:.4f}")

    print()

    # Overall verdict
    significant = sum(1 for r in results if r['result'] == 'SIGNIFICANT')
    print(f"Significant correlations: {significant}/{len(results)}")

    if significant >= 2:
        print("\nVERDICT: PCC findings CORRELATE with product types")
    elif significant == 1:
        print("\nVERDICT: WEAK correlation between PCC and product types")
    else:
        print("\nVERDICT: NO significant correlation between PCC and product types")

    # Save results
    output = {
        'tests': results,
        'summary': {
            'significant_count': significant,
            'total_tests': len(results)
        }
    }

    with open('phases/BRU_AUDIT/pcc_integration_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to phases/BRU_AUDIT/pcc_integration_results.json")

if __name__ == '__main__':
    main()
