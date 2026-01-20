#!/usr/bin/env python3
"""
STRATIFIED PRODUCT-EXCLUSIVITY ANALYSIS

Question: Does the 2-track classification (C498) affect F-BRU-005's finding
          that 75% of MIDDLEs are type-specific?

Hypothesis:
- Registry-internal MIDDLEs (56.6%) are folio-localized (1.34 folios avg)
- Folio-localization might artificially inflate type-specific rates
- If registry-internal shows higher type-specificity than pipeline-participating,
  the original 75% figure is confounded

Method:
1. Load 2-track classification (registry-internal vs pipeline-participating)
2. For each track, count MIDDLEs by product-type coverage (1, 2, 3, 4 types)
3. Chi-square test: Track x Type-Coverage
4. Compare type-specific rates between tracks
"""

import csv
import json
from collections import defaultdict, Counter
import math

# ============================================================
# CONFIGURATION
# ============================================================

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']

def get_middle(token):
    """Extract MIDDLE from token by removing known prefix."""
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            return token[len(p):]
    return token

# ============================================================
# DATA LOADING
# ============================================================

def load_2track_classification():
    """Load the 2-track MIDDLE classification from C498."""
    with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
        data = json.load(f)

    a_exclusive = set(data['a_exclusive_middles'])  # Registry-internal (349)
    a_shared = set(data['a_shared_middles'])        # Pipeline-participating (268)

    return a_exclusive, a_shared

def load_folio_classifications():
    """Load product type classification for each A folio."""
    with open('results/exclusive_middle_backprop.json', 'r') as f:
        data = json.load(f)
    return data['a_folio_classifications']

def load_folio_middles():
    """Load MIDDLEs per folio from transcript (H-track, language=A only)."""
    folio_middles = defaultdict(set)

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only
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
                folio_middles[folio].add(middle)

    return folio_middles

# ============================================================
# ANALYSIS
# ============================================================

def compute_type_coverage(folio_middles, folio_classifications):
    """For each MIDDLE, compute which product types it appears in."""
    middle_types = defaultdict(set)

    for folio, middles in folio_middles.items():
        if folio not in folio_classifications:
            continue
        ptype = folio_classifications[folio]
        for middle in middles:
            middle_types[middle].add(ptype)

    return middle_types

def stratified_analysis(middle_types, a_exclusive, a_shared):
    """Stratify type-coverage by 2-track classification."""

    # For each track, count by type coverage
    registry_internal = defaultdict(int)  # type_count -> n_middles
    pipeline_participating = defaultdict(int)

    registry_internal_list = []
    pipeline_participating_list = []

    for middle, types in middle_types.items():
        n_types = len(types)

        if middle in a_exclusive:
            registry_internal[n_types] += 1
            registry_internal_list.append((middle, n_types, types))
        elif middle in a_shared:
            pipeline_participating[n_types] += 1
            pipeline_participating_list.append((middle, n_types, types))
        # else: MIDDLE not in either track (shouldn't happen for A vocabulary)

    return {
        'registry_internal': dict(registry_internal),
        'pipeline_participating': dict(pipeline_participating),
        'registry_internal_list': registry_internal_list,
        'pipeline_participating_list': pipeline_participating_list,
    }

def chi_square_test(reg_counts, pipe_counts):
    """Chi-square test of independence: Track x Type-Coverage."""
    # Build contingency table
    all_n_types = sorted(set(reg_counts.keys()) | set(pipe_counts.keys()))

    observed = []
    for n in all_n_types:
        observed.append([
            reg_counts.get(n, 0),
            pipe_counts.get(n, 0)
        ])

    # Row totals
    row_totals = [sum(row) for row in observed]
    col_totals = [
        sum(observed[i][0] for i in range(len(observed))),
        sum(observed[i][1] for i in range(len(observed)))
    ]
    grand_total = sum(row_totals)

    if grand_total == 0:
        return None, None, None

    # Expected values
    expected = []
    for i, row in enumerate(observed):
        exp_row = []
        for j in range(2):
            exp = (row_totals[i] * col_totals[j]) / grand_total
            exp_row.append(exp)
        expected.append(exp_row)

    # Chi-square statistic
    chi_sq = 0
    for i in range(len(observed)):
        for j in range(2):
            if expected[i][j] > 0:
                chi_sq += ((observed[i][j] - expected[i][j]) ** 2) / expected[i][j]

    # Degrees of freedom
    df = (len(all_n_types) - 1) * (2 - 1)

    # Approximate p-value using chi-square distribution
    # (for df=3, chi_sq > 7.81 means p < 0.05)
    # Simple approximation:
    if df == 1:
        critical_05 = 3.84
    elif df == 2:
        critical_05 = 5.99
    elif df == 3:
        critical_05 = 7.81
    else:
        critical_05 = df * 2  # Rough approximation

    return chi_sq, df, observed, expected, critical_05

def cramers_v(chi_sq, n, min_dim):
    """Compute Cramer's V effect size."""
    if n == 0 or min_dim <= 1:
        return 0
    return math.sqrt(chi_sq / (n * (min_dim - 1)))

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("STRATIFIED PRODUCT-EXCLUSIVITY ANALYSIS")
    print("=" * 70)
    print()
    print("Question: Does the 2-track classification (C498) affect")
    print("          the type-specific rate from F-BRU-005?")
    print()

    # Load data
    print("Loading data...")
    a_exclusive, a_shared = load_2track_classification()
    folio_classifications = load_folio_classifications()
    folio_middles = load_folio_middles()

    print(f"  Registry-internal MIDDLEs (C498): {len(a_exclusive)}")
    print(f"  Pipeline-participating MIDDLEs (C498): {len(a_shared)}")
    print(f"  A folios with product types: {len(folio_classifications)}")
    print(f"  A folios with MIDDLEs: {len(folio_middles)}")
    print()

    # Compute type coverage
    print("Computing product-type coverage per MIDDLE...")
    middle_types = compute_type_coverage(folio_middles, folio_classifications)
    print(f"  MIDDLEs with type coverage computed: {len(middle_types)}")
    print()

    # Stratified analysis
    print("Stratifying by 2-track classification...")
    results = stratified_analysis(middle_types, a_exclusive, a_shared)

    reg = results['registry_internal']
    pipe = results['pipeline_participating']

    reg_total = sum(reg.values())
    pipe_total = sum(pipe.values())

    print()
    print("=" * 70)
    print("RESULTS: Type-Coverage Distribution by Track")
    print("=" * 70)
    print()

    print("Registry-Internal (A-exclusive MIDDLEs):")
    for n in sorted(reg.keys()):
        pct = 100 * reg[n] / reg_total if reg_total > 0 else 0
        label = {1: "type-specific", 2: "2-type", 3: "3-type", 4: "universal"}.get(n, f"{n}-type")
        print(f"  {n} type(s): {reg[n]:4d} ({pct:5.1f}%)  [{label}]")
    print(f"  TOTAL: {reg_total}")
    print()

    print("Pipeline-Participating (A/B-shared MIDDLEs):")
    for n in sorted(pipe.keys()):
        pct = 100 * pipe[n] / pipe_total if pipe_total > 0 else 0
        label = {1: "type-specific", 2: "2-type", 3: "3-type", 4: "universal"}.get(n, f"{n}-type")
        print(f"  {n} type(s): {pipe[n]:4d} ({pct:5.1f}%)  [{label}]")
    print(f"  TOTAL: {pipe_total}")
    print()

    # Key comparison: type-specific rate
    reg_type_specific = reg.get(1, 0)
    pipe_type_specific = pipe.get(1, 0)
    reg_type_specific_pct = 100 * reg_type_specific / reg_total if reg_total > 0 else 0
    pipe_type_specific_pct = 100 * pipe_type_specific / pipe_total if pipe_total > 0 else 0

    print("=" * 70)
    print("KEY COMPARISON: Type-Specific Rate")
    print("=" * 70)
    print()
    print(f"  Registry-Internal:      {reg_type_specific_pct:5.1f}% ({reg_type_specific}/{reg_total})")
    print(f"  Pipeline-Participating: {pipe_type_specific_pct:5.1f}% ({pipe_type_specific}/{pipe_total})")
    print(f"  Difference:             {reg_type_specific_pct - pipe_type_specific_pct:+5.1f} percentage points")
    print()

    # Chi-square test
    print("=" * 70)
    print("STATISTICAL TEST: Chi-Square Independence")
    print("=" * 70)
    print()

    chi_result = chi_square_test(reg, pipe)
    if chi_result[0] is not None:
        chi_sq, df, observed, expected, critical = chi_result
        n_total = reg_total + pipe_total
        v = cramers_v(chi_sq, n_total, min(4, 2))  # 4 type levels, 2 tracks

        print(f"  Chi-square: {chi_sq:.2f}")
        print(f"  Degrees of freedom: {df}")
        print(f"  Critical value (p=0.05): {critical:.2f}")
        print(f"  Cramer's V: {v:.3f}")
        print()

        if chi_sq > critical:
            print(f"  RESULT: SIGNIFICANT (chi-sq {chi_sq:.2f} > {critical:.2f})")
            print(f"          Track and type-coverage are NOT independent")
        else:
            print(f"  RESULT: NOT SIGNIFICANT (chi-sq {chi_sq:.2f} < {critical:.2f})")
            print(f"          Track and type-coverage are independent")
    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if reg_type_specific_pct > pipe_type_specific_pct + 10:
        print("FINDING: Registry-internal MIDDLEs show HIGHER type-specificity")
        print()
        print("Interpretation:")
        print("  The original F-BRU-005 finding (75% type-specific) is CONFOUNDED.")
        print("  Registry-internal vocabulary (folio-localized) artificially inflates")
        print("  the type-specific rate because these MIDDLEs appear in fewer folios")
        print("  (avg 1.34) and thus naturally span fewer product types.")
        print()
        print("  Pipeline-participating vocabulary (which actually flows through")
        print("  A->AZC->B) shows a lower type-specific rate, suggesting product-type")
        print("  encoding is weaker than originally estimated.")
        print()
        print("ACTION: Revise F-BRU-005 to report stratified rates")

    elif pipe_type_specific_pct > reg_type_specific_pct + 10:
        print("FINDING: Pipeline-participating MIDDLEs show HIGHER type-specificity")
        print()
        print("Interpretation:")
        print("  Product-type encoding is CONCENTRATED in pipeline-participating")
        print("  vocabulary. This STRENGTHENS F-BRU-001/005: the vocabulary that")
        print("  actually participates in execution is strongly product-typed.")
        print()
        print("  Registry-internal vocabulary may encode within-category fine")
        print("  distinctions that cross product types (sub-variety markers).")
        print()
        print("ACTION: Add stratification note to F-BRU-005, link to C498")

    else:
        print("FINDING: Similar type-specificity across both tracks")
        print()
        print("Interpretation:")
        print("  The 2-track classification is ORTHOGONAL to product-type encoding.")
        print("  Both registry-internal and pipeline-participating vocabulary show")
        print("  similar type-specificity rates.")
        print()
        print("ACTION: Note 2-track orthogonality in F-BRU-005")
    print()

    # Save results
    output = {
        'test': 'STRATIFIED_PRODUCT_EXCLUSIVITY',
        'date': '2026-01-20',
        'provenance': 'C498 (2-track), F-BRU-005 (type-specific)',
        'counts': {
            'registry_internal': {
                'total': reg_total,
                'by_type_count': reg,
                'type_specific_pct': reg_type_specific_pct
            },
            'pipeline_participating': {
                'total': pipe_total,
                'by_type_count': pipe,
                'type_specific_pct': pipe_type_specific_pct
            }
        },
        'difference_pct_points': reg_type_specific_pct - pipe_type_specific_pct,
        'chi_square': chi_sq if chi_result[0] else None,
        'cramers_v': v if chi_result[0] else None,
        'significant': chi_sq > critical if chi_result[0] else None
    }

    with open('phases/BRUNSCHWIG_2TRACK_STRATIFICATION/results/stratified_product_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to phases/BRUNSCHWIG_2TRACK_STRATIFICATION/results/stratified_product_analysis.json")

if __name__ == '__main__':
    main()
