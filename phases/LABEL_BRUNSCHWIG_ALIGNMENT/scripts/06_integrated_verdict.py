"""
06_integrated_verdict.py - Synthesize results from all 5 tests

Success Criteria:
| Level | Criteria |
|-------|----------|
| STRONG | 4-5 tests show significant non-uniform distribution |
| MODERATE | 2-3 tests show significant effects |
| WEAK | 1 test shows significant effect |
| NULL | No tests show significant effects |
"""
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = PROJECT_ROOT / 'phases' / 'LABEL_BRUNSCHWIG_ALIGNMENT' / 'results'

print("="*70)
print("LABEL_BRUNSCHWIG_ALIGNMENT: INTEGRATED VERDICT")
print("="*70)

# ============================================================
# LOAD ALL RESULTS
# ============================================================
print("\n--- Loading Test Results ---")

results = {}

# Test 1: Jar Product Type
try:
    with open(RESULTS_DIR / 'jar_product_type.json', 'r') as f:
        results['test1'] = json.load(f)
    print("Test 1 (jar_product_type): Loaded")
except FileNotFoundError:
    print("Test 1 (jar_product_type): NOT FOUND")
    results['test1'] = None

# Test 2: Content Material Category
try:
    with open(RESULTS_DIR / 'content_material_category.json', 'r') as f:
        results['test2'] = json.load(f)
    print("Test 2 (content_material_category): Loaded")
except FileNotFoundError:
    print("Test 2 (content_material_category): NOT FOUND")
    results['test2'] = None

# Test 3: Label Folio Recipe Cluster
try:
    with open(RESULTS_DIR / 'label_folio_recipe_cluster.json', 'r') as f:
        results['test3'] = json.load(f)
    print("Test 3 (label_folio_recipe_cluster): Loaded")
except FileNotFoundError:
    print("Test 3 (label_folio_recipe_cluster): NOT FOUND")
    results['test3'] = None

# Test 4: Section Label Differentiation
try:
    with open(RESULTS_DIR / 'section_label_differentiation.json', 'r') as f:
        results['test4'] = json.load(f)
    print("Test 4 (section_label_differentiation): Loaded")
except FileNotFoundError:
    print("Test 4 (section_label_differentiation): NOT FOUND")
    results['test4'] = None

# Test 5: Prep Operation Co-occurrence
try:
    with open(RESULTS_DIR / 'prep_operation_cooccurrence.json', 'r') as f:
        results['test5'] = json.load(f)
    print("Test 5 (prep_operation_cooccurrence): Loaded")
except FileNotFoundError:
    print("Test 5 (prep_operation_cooccurrence): NOT FOUND")
    results['test5'] = None

# ============================================================
# EXTRACT SIGNIFICANCE
# ============================================================
print("\n--- Test Results Summary ---")

test_results = []

# Test 1
if results['test1']:
    sig = results['test1']['summary']['significant']
    p = results['test1']['summary']['p_value']
    chi2 = results['test1']['summary']['chi2']
    test_results.append({
        'test': 'Test 1: Jar Product Type Clustering',
        'significant': sig,
        'p_value': p,
        'effect': f"Chi2={chi2:.2f}",
        'finding': "81.2% of jar labels cluster with PRECISION product type"
    })
    print(f"\nTest 1: Jar Product Type Clustering")
    print(f"  Significant: {sig}")
    print(f"  p-value: {p:.4f}")
    print(f"  Finding: 81.2% map to PRECISION (chi2={chi2:.2f})")

# Test 2
if results['test2']:
    sig = results['test2']['statistics']['significant']
    p = results['test2']['statistics']['p_value']
    v = results['test2']['statistics']['cramers_v']
    test_results.append({
        'test': 'Test 2: Root vs Leaf Handling Profiles',
        'significant': sig,
        'p_value': p,
        'effect': f"V={v:.3f}",
        'finding': "Root and leaf labels show similar handling profiles"
    })
    print(f"\nTest 2: Root vs Leaf Handling Profiles")
    print(f"  Significant: {sig}")
    print(f"  p-value: {p:.4f}")
    print(f"  Finding: No significant difference (V={v:.3f})")

# Test 3
if results['test3']:
    sig = results['test3']['concentration']['significant']
    p = results['test3']['concentration']['p_value']
    test_results.append({
        'test': 'Test 3: Label-Rich Folio B Concentration',
        'significant': sig,
        'p_value': p,
        'effect': "Gini comparison",
        'finding': "Label-rich folios do not show more concentrated B connections"
    })
    print(f"\nTest 3: Label-Rich Folio B Concentration")
    print(f"  Significant: {sig}")
    print(f"  p-value: {p:.4f}")
    print(f"  Finding: No concentration difference")

# Test 4
if results['test4']:
    sig = results['test4']['statistics']['significant']
    p = results['test4']['statistics']['p_value']
    v = results['test4']['statistics']['cramers_v']
    test_results.append({
        'test': 'Test 4: Section-Level Label Differentiation',
        'significant': sig,
        'p_value': p,
        'effect': f"V={v:.3f}",
        'finding': "Labels do not differ by section in handling profile"
    })
    print(f"\nTest 4: Section-Level Label Differentiation")
    print(f"  Significant: {sig}")
    print(f"  p-value: {p:.4f}")
    print(f"  Finding: No section differentiation (V={v:.3f})")

# Test 5
if results['test5']:
    sig = results['test5']['overall_statistics']['significant']
    p = results['test5']['overall_statistics']['p_value']
    bru_support = results['test5']['brunschwig_prediction']['supports_prediction']
    test_results.append({
        'test': 'Test 5: Label-Prep Operation Co-occurrence',
        'significant': sig,
        'p_value': p,
        'effect': "prep op distribution",
        'finding': f"No prep op differentiation; Brunschwig prediction NOT supported"
    })
    print(f"\nTest 5: Label-Prep Operation Co-occurrence")
    print(f"  Significant: {sig}")
    print(f"  p-value: {p:.4f}")
    print(f"  Finding: No differentiation; Brunschwig prediction: {bru_support}")

# ============================================================
# VERDICT DETERMINATION
# ============================================================
print("\n" + "="*70)
print("OVERALL VERDICT")
print("="*70)

significant_count = sum(1 for t in test_results if t['significant'])
total_tests = len(test_results)

if significant_count >= 4:
    verdict = 'STRONG'
elif significant_count >= 2:
    verdict = 'MODERATE'
elif significant_count >= 1:
    verdict = 'WEAK'
else:
    verdict = 'NULL'

print(f"\nSignificant tests: {significant_count}/{total_tests}")
print(f"Verdict: {verdict}")

print(f"""
Success Criteria:
  STRONG (4-5 sig): Labels clearly cluster by Brunschwig material categories
  MODERATE (2-3 sig): Partial alignment with Brunschwig dimensions
  WEAK (1 sig): Minimal Brunschwig alignment
  NULL (0 sig): No evidence of Brunschwig material alignment

Result: {verdict}

Summary:
""")

for t in test_results:
    status = "PASS" if t['significant'] else "FAIL"
    print(f"  [{status}] {t['test']}: {t['finding']}")

# ============================================================
# KEY INSIGHTS
# ============================================================
print("\n" + "-"*70)
print("KEY INSIGHTS")
print("-"*70)

print("""
1. JAR LABEL CLUSTERING (SIGNIFICANT)
   - Jar labels strongly cluster with PRECISION product type (81.2%)
   - This aligns with C928 (jar AX_FINAL concentration)
   - Suggests jars identify specific output products

2. VOCABULARY UBIQUITY PROBLEM
   - Label PP bases appear in nearly ALL B lines (96-100%)
   - This dilutes any signal from prep operation co-occurrence
   - Root/leaf distinction does not translate to handling profiles

3. LIMITED BRUNSCHWIG ALIGNMENT
   - Root/leaf handling prediction NOT supported
   - Section differentiation NOT found
   - B folio concentration NOT significant

4. INTERPRETATION
   - Labels identify WHAT (materials) not HOW (processing)
   - The label->B pipeline exists but is vocabulary-level, not semantic
   - Brunschwig material categories may not map to label categories
""")

# ============================================================
# SAVE VERDICT
# ============================================================
output = {
    'phase': 'LABEL_BRUNSCHWIG_ALIGNMENT',
    'date': '2026-02-05',
    'verdict': verdict,
    'significant_count': significant_count,
    'total_tests': total_tests,
    'test_results': test_results,
    'interpretation': {
        'jar_clustering': 'Jar labels cluster with PRECISION product type - suggests output product identification',
        'vocabulary_ubiquity': 'Label PP bases are ubiquitous in B (96-100% of lines) - dilutes semantic signal',
        'brunschwig_alignment': 'Limited - only jar clustering is significant',
        'conclusion': 'Labels identify materials at vocabulary level but do not encode Brunschwig processing categories'
    }
}

output_path = RESULTS_DIR / 'integrated_verdict.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nVerdict saved to: {output_path}")

# ============================================================
# CONSTRAINT RECOMMENDATIONS
# ============================================================
print("\n" + "="*70)
print("CONSTRAINT RECOMMENDATIONS")
print("="*70)

print("""
Based on these results:

1. NO NEW CONSTRAINTS RECOMMENDED
   - Test 1 (jar clustering) reinforces existing C928, not a new constraint
   - Other tests are null results

2. NEGATIVE FINDINGS TO DOCUMENT:
   - Root/leaf labels do NOT show different handling profiles
   - Label vocabulary ubiquity prevents semantic differentiation
   - Section does not predict label handling profile

3. INTERPRETATION REFINEMENT:
   - C928 interpretation confirmed: jar labels identify output products
   - Label->B pipeline is vocabulary-level, not semantic-level
   - Brunschwig material categories do not map directly to label types
""")
