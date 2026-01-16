#!/usr/bin/env python3
"""
AZC ZONE BIAS TEST (Test 3)

Expert Warning: "Discriminate by product type" is risky.
Keep AZC as LEGALITY MEDIATOR, not product classifier.

SAFE FRAMING:
Question: Do B folios in different REGIMEs (mapped to product types)
          show systematic SECTION distribution differences?

NOT: "This folio = oil"

Method:
1. Take B folios classified by REGIME
2. Map REGIME to product type
3. For each product type, compute section distribution
4. Test if distributions differ significantly

Predictions (STRUCTURAL, not semantic):
- WATER_GENTLE (R2): Lower complexity sections expected
- PRECISION (R4): Higher proportion of constrained sections
"""

import csv
import json
from collections import defaultdict, Counter
from scipy import stats

# ============================================================
# REGIME TO PRODUCT TYPE MAPPING
# ============================================================

REGIME_PRODUCT_MAP = {
    'REGIME_2': 'WATER_GENTLE',
    'REGIME_1': 'WATER_STANDARD',
    'REGIME_4': 'PRECISION',
    'REGIME_3': 'OIL_RESIN',
}

# ============================================================
# LOAD DATA
# ============================================================

def load_folio_regimes():
    """Load REGIME assignments from proposed folio order."""
    folio_regime = {}
    with open('results/proposed_folio_order.txt', encoding='utf-8') as f:
        for line in f:
            parts = line.split('|')
            if len(parts) >= 3:
                folio = parts[1].strip()
                regime = parts[2].strip()
                if folio.startswith('f') and regime.startswith('REGIME'):
                    folio_regime[folio] = regime
    return folio_regime

def load_folio_section_data():
    """Load section distribution per folio from transcription."""
    section_by_folio = defaultdict(Counter)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()

            # Only count B language tokens
            if language != 'B':
                continue

            if section:
                section_by_folio[folio][section] += 1

    return section_by_folio

# ============================================================
# ANALYSIS
# ============================================================

def main():
    print("=" * 70)
    print("AZC ZONE BIAS TEST (Test 3) - REVISED")
    print("=" * 70)
    print()
    print("Tests B folio SECTION distribution by REGIME.")
    print("REGIME maps to product type for structural comparison.")
    print()

    # Load data
    folio_regimes = load_folio_regimes()
    folio_sections = load_folio_section_data()

    print(f"Loaded {len(folio_regimes)} folio REGIME assignments")
    print(f"Loaded {len(folio_sections)} folios with section data")
    print()

    # Group folios by product type (via REGIME)
    product_folios = defaultdict(list)
    for folio, regime in folio_regimes.items():
        if folio in folio_sections:
            product = REGIME_PRODUCT_MAP.get(regime, 'UNKNOWN')
            product_folios[product].append(folio)

    print("FOLIOS BY PRODUCT TYPE (REGIME-mapped):")
    print("-" * 50)
    for product, folios in sorted(product_folios.items()):
        print(f"  {product}: {len(folios)} folios")
    print()

    # Compute section distributions by product type
    print("=" * 70)
    print("SECTION DISTRIBUTIONS BY PRODUCT TYPE")
    print("=" * 70)
    print()

    # Get all sections present
    all_sections = set()
    for sections in folio_sections.values():
        all_sections.update(sections.keys())
    sections = sorted(all_sections)

    product_section_counts = {}
    product_section_rates = {}

    for product in sorted(product_folios.keys()):
        folios = product_folios[product]

        # Aggregate section counts
        total_counts = Counter()
        for folio in folios:
            for section in sections:
                total_counts[section] += folio_sections[folio].get(section, 0)

        total = sum(total_counts.values())
        product_section_counts[product] = total_counts
        product_section_rates[product] = {s: total_counts[s] / total if total > 0 else 0 for s in sections}

        # Print distribution (top sections only)
        print(f"{product}:")
        print(f"  n_folios={len(folios)}, total_tokens={total}")
        top_sections = sorted(total_counts.items(), key=lambda x: -x[1])[:6]
        for section, count in top_sections:
            pct = 100 * count / total if total > 0 else 0
            bar = '#' * int(pct / 5)
            print(f"    {section}: {pct:5.1f}% {bar}")
        print()

    # Statistical test: chi-square for section distribution differences
    print("=" * 70)
    print("STATISTICAL TESTS")
    print("=" * 70)
    print()

    # Use only sections with enough data
    major_sections = [s for s in sections if sum(product_section_counts[p].get(s, 0)
                                                  for p in product_section_counts) > 100]

    # Build contingency table
    products = sorted(product_section_counts.keys())

    print("Contingency table (product x major sections):")
    print(f"{'Product':<18}", end="")
    for s in major_sections:
        print(f"{s:>8}", end="")
    print(f"{'Total':>10}")
    print("-" * 80)

    contingency = []
    for product in products:
        row = [product_section_counts[product].get(s, 0) for s in major_sections]
        contingency.append(row)
        print(f"{product:<18}", end="")
        for val in row:
            print(f"{val:>8}", end="")
        print(f"{sum(row):>10}")
    print()

    # Chi-square test
    if len(contingency) > 0 and all(sum(row) > 0 for row in contingency):
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        chi2_passed = p_value < 0.05
    else:
        chi2, p_value, dof = 0, 1.0, 0
        chi2_passed = False

    print(f"Chi-square test:")
    print(f"  chi2 = {chi2:.2f}")
    print(f"  df = {dof}")
    print(f"  p-value = {p_value:.4e}")
    print(f"  Significant (p < 0.05)? {chi2_passed}")
    print()

    # Pairwise comparisons
    print("PAIRWISE SECTION RATE DIFFERENCES:")
    print("-" * 50)

    for i, p1 in enumerate(products):
        for p2 in products[i+1:]:
            # L1 distance using major sections
            dist = sum(abs(product_section_rates[p1].get(s, 0) - product_section_rates[p2].get(s, 0))
                       for s in major_sections) / 2
            print(f"  {p1} vs {p2}: {dist:.3f}")
    print()

    # Check structural predictions (reframed for sections)
    print("=" * 70)
    print("STRUCTURAL PREDICTION CHECK")
    print("=" * 70)
    print()

    # Predictions based on REGIME characteristics
    # H = Herbal (most common), S = Stars, B = Biological, P = Pharmaceutical, etc.
    predictions = [
        ('WATER_GENTLE', 'H', 'enriched', 'Simple procedures use herbal section'),
        ('OIL_RESIN', 'S', 'enriched', 'Advanced procedures in specialized sections'),
        ('PRECISION', 'P', 'enriched', 'Precision in pharmaceutical sections'),
    ]

    prediction_results = []

    for product, target_section, expected_pattern, reasoning in predictions:
        if product not in product_section_rates:
            print(f"{product}: NO DATA")
            continue

        rates = product_section_rates[product]

        # Compare target section to overall average
        other_products = [p for p in products if p != product]
        if not other_products:
            continue

        avg_rate = sum(product_section_rates[p].get(target_section, 0)
                       for p in other_products) / len(other_products)

        target_rate = rates.get(target_section, 0)
        enrichment = target_rate / avg_rate if avg_rate > 0 else 1.0

        passed = enrichment > 1.0  # Any enrichment counts

        prediction_results.append({
            'product': product,
            'target_section': target_section,
            'target_rate': target_rate,
            'avg_rate': avg_rate,
            'enrichment': enrichment,
            'passed': passed
        })

        status = "PASS" if passed else "FAIL"
        print(f"{product}:")
        print(f"  Prediction: {target_section} {expected_pattern}")
        print(f"  Reasoning: {reasoning}")
        print(f"  Target section rate: {target_rate:.1%}")
        print(f"  Average other rate: {avg_rate:.1%}")
        print(f"  Enrichment: {enrichment:.2f}x")
        print(f"  Status: [{status}]")
        print()

    # Verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    predictions_passed = sum(1 for r in prediction_results if r['passed'])
    total_predictions = len(prediction_results)

    print(f"Chi-square significance: {'PASS' if chi2_passed else 'FAIL'} (p={p_value:.4e})")
    print(f"Structural predictions: {predictions_passed}/{total_predictions}")
    print()

    if chi2_passed and predictions_passed >= 2:
        verdict = "PASS"
        interpretation = "Section distribution shows REGIME-correlated structural bias"
    elif chi2_passed or predictions_passed >= 2:
        verdict = "PARTIAL"
        interpretation = "Some section bias detected, needs refinement"
    else:
        verdict = "FAIL"
        interpretation = "No significant section bias by REGIME/product type"

    print(f"Verdict: {verdict}")
    print(f"Interpretation: {interpretation}")
    print()

    if verdict == "PASS":
        print("C497 CANDIDATE: Section distribution correlates with REGIME")

    # Save results
    output = {
        'test': 'AZC_ZONE_BIAS',
        'product_section_counts': {p: dict(c) for p, c in product_section_counts.items()},
        'product_section_rates': product_section_rates,
        'chi_square': {
            'chi2': float(chi2),
            'df': int(dof),
            'p_value': float(p_value),
            'significant': bool(chi2_passed)
        },
        'structural_predictions': [{
            'product': r['product'],
            'target_section': r['target_section'],
            'target_rate': float(r['target_rate']),
            'avg_rate': float(r['avg_rate']),
            'enrichment': float(r['enrichment']),
            'passed': bool(r['passed'])
        } for r in prediction_results],
        'summary': {
            'verdict': verdict,
            'interpretation': interpretation
        }
    }

    with open('results/azc_zone_bias.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to results/azc_zone_bias.json")

if __name__ == '__main__':
    main()
