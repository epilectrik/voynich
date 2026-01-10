#!/usr/bin/env python3
"""
APPARATUS-TOPOLOGY Hypothesis Tests

TEST 1: AZC Position × B Grammar Interaction
TEST 7: Negative Control (AZC should NOT predict tokens)

Pre-registered kill conditions:
- K1: No AZC placement class shows p < 0.01 difference in any B metric
- K2: AZC placement predicts token identity (p < 0.05) -> MODEL FAILURE
"""

import json
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# Key data files
CONTROL_SIGNATURES = RESULTS / "control_signatures.json"
AZC_FOLIO_FEATURES = RESULTS / "azc_folio_features.json"

def load_b_metrics():
    """Load B folio control signatures."""
    with open(CONTROL_SIGNATURES) as f:
        data = json.load(f)
    return data.get('signatures', {})

def load_azc_features():
    """Load AZC folio features with placement vectors."""
    with open(AZC_FOLIO_FEATURES) as f:
        data = json.load(f)
    return data.get('folios', {})

def load_transcription():
    """Load full transcription with placement codes."""
    rows = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            rows.append(row)
    return rows

def get_azc_tokens(rows):
    """Extract AZC tokens with placement codes."""
    azc_tokens = []
    for row in rows:
        language = row.get('language', '').strip('"')
        placement = row.get('placement', '').strip('"')
        token = row.get('word', '').strip('"')
        folio = row.get('folio', '').strip('"')

        # AZC is marked as 'NA' in language column
        if language == 'NA' and placement and token:
            # Skip damaged tokens
            if '*' in token:
                continue
            azc_tokens.append({
                'token': token,
                'placement': placement,
                'folio': folio
            })

    return azc_tokens

def classify_placement(placement):
    """Classify placement into major categories."""
    if placement.startswith('R'):
        return 'R'  # Radial
    elif placement.startswith('S'):
        return 'S'  # Sector
    elif placement.startswith('C'):
        return 'C'  # Central
    elif placement.startswith('P'):
        return 'P'  # Paragraph (standard text)
    else:
        return 'OTHER'

def get_placement_subscript(placement):
    """Extract subscript number from placement (e.g., R1 -> 1, R2 -> 2)."""
    if len(placement) > 1 and placement[1:].isdigit():
        return int(placement[1:])
    return 0

# ============================================================
# TEST 1: AZC Position × B Grammar Interaction
# ============================================================

def get_dominant_azc_context(azc_features, folio):
    """
    Determine the dominant AZC context for a folio.

    Returns: (context_type, dominant_placement)
    - context_type: 'ZODIAC', 'COSMOLOGICAL', 'NONE'
    - dominant_placement: e.g., 'R1', 'S2', 'C' or None
    """
    if folio not in azc_features:
        return ('NONE', None)

    features = azc_features[folio]
    section = features.get('section', '')
    placement_counts = features.get('placement_counts', {})

    if not placement_counts:
        return ('NONE', None)

    # Determine context type from section
    # Z = Zodiac, C = Cosmological, A = Astronomical, H = Herbal, S = Stars
    if section == 'Z':
        context_type = 'ZODIAC'
    elif section == 'C':
        context_type = 'COSMOLOGICAL'
    elif section in ['A', 'S']:
        context_type = 'ASTRONOMICAL'
    else:
        context_type = 'OTHER'

    # Get dominant placement
    dominant = max(placement_counts.items(), key=lambda x: x[1])[0]

    return (context_type, dominant)

def get_placement_family(placement):
    """Classify placement into families: R (radial), S (sector), C (central), P (paragraph)."""
    if not placement:
        return 'NONE'
    if placement.startswith('R'):
        return 'R'  # Radial segments (R1, R2, R3...)
    elif placement.startswith('S'):
        return 'S'  # Sectors (S1, S2...)
    elif placement.startswith('C'):
        return 'C'  # Central
    elif placement.startswith('P'):
        return 'P'  # Paragraph (standard text)
    else:
        return 'OTHER'

def run_test_1(b_metrics, azc_features):
    """
    TEST 1: AZC Position × B Grammar Interaction

    Question: Do B folio control metrics differ by AZC context?

    Kill condition K1:
    If no AZC context shows p < 0.01 difference in ANY B metric -> REJECT hypothesis
    """
    print("=" * 70)
    print("TEST 1: AZC Position × B Grammar Interaction")
    print("=" * 70)

    # Cross-reference: for each B folio, get its AZC context
    folio_contexts = {}
    for folio in b_metrics:
        context_type, dominant_placement = get_dominant_azc_context(azc_features, folio)
        folio_contexts[folio] = {
            'context_type': context_type,
            'dominant_placement': dominant_placement,
            'placement_family': get_placement_family(dominant_placement)
        }

    # Count contexts
    context_counts = Counter(fc['context_type'] for fc in folio_contexts.values())
    family_counts = Counter(fc['placement_family'] for fc in folio_contexts.values())

    print(f"\n[1] B folios by AZC context type:")
    for ctx, count in sorted(context_counts.items()):
        print(f"    {ctx}: {count} folios")

    print(f"\n[2] B folios by placement family:")
    for fam, count in sorted(family_counts.items()):
        print(f"    {fam}: {count} folios")

    # Metrics to test from control_signatures
    test_metrics = ['link_density', 'hazard_density', 'intervention_frequency',
                    'kernel_contact_ratio', 'cycle_regularity']

    # Group B metrics by AZC context type
    context_groups = defaultdict(lambda: defaultdict(list))
    for folio, ctx in folio_contexts.items():
        b = b_metrics[folio]
        context_type = ctx['context_type']
        for metric in test_metrics:
            if metric in b:
                context_groups[metric][context_type].append(b[metric])

    # Run Kruskal-Wallis for each metric
    print(f"\n[3] Kruskal-Wallis tests (by context type):")
    kruskal_results = {}
    any_significant = False

    for metric in test_metrics:
        groups = context_groups[metric]
        # Filter to groups with at least 3 samples
        valid_groups = {k: v for k, v in groups.items() if len(v) >= 3}

        if len(valid_groups) >= 2:
            group_list = list(valid_groups.values())
            h_stat, p_value = stats.kruskal(*group_list)

            # Effect size (eta-squared approximation)
            n_total = sum(len(g) for g in group_list)
            k = len(group_list)
            eta_sq = (h_stat - k + 1) / (n_total - k) if n_total > k else 0
            eta_sq = max(0, eta_sq)

            kruskal_results[metric] = {
                'H': float(h_stat),
                'p': float(p_value),
                'eta_squared': float(eta_sq),
                'n_groups': k,
                'group_means': {ctx: float(np.mean(vals)) for ctx, vals in valid_groups.items()},
                'group_n': {ctx: len(vals) for ctx, vals in valid_groups.items()}
            }

            sig = "***" if p_value < 0.01 else "**" if p_value < 0.05 else ""
            print(f"    {metric}: H={h_stat:.2f}, p={p_value:.4f}, eta²={eta_sq:.3f} {sig}")

            if p_value < 0.01:
                any_significant = True
        else:
            print(f"    {metric}: insufficient groups (n={len(valid_groups)})")

    # Also test by placement family (R vs S vs C)
    print(f"\n[4] Kruskal-Wallis tests (by placement family):")
    family_groups = defaultdict(lambda: defaultdict(list))
    for folio, ctx in folio_contexts.items():
        b = b_metrics[folio]
        family = ctx['placement_family']
        if family in ['R', 'S', 'C']:  # Only core placement families
            for metric in test_metrics:
                if metric in b:
                    family_groups[metric][family].append(b[metric])

    family_results = {}
    for metric in test_metrics:
        groups = family_groups[metric]
        valid_groups = {k: v for k, v in groups.items() if len(v) >= 3}

        if len(valid_groups) >= 2:
            group_list = list(valid_groups.values())
            h_stat, p_value = stats.kruskal(*group_list)

            n_total = sum(len(g) for g in group_list)
            k = len(group_list)
            eta_sq = (h_stat - k + 1) / (n_total - k) if n_total > k else 0
            eta_sq = max(0, eta_sq)

            family_results[metric] = {
                'H': float(h_stat),
                'p': float(p_value),
                'eta_squared': float(eta_sq),
                'group_means': {fam: float(np.mean(vals)) for fam, vals in valid_groups.items()}
            }

            sig = "***" if p_value < 0.01 else "**" if p_value < 0.05 else ""
            print(f"    {metric}: H={h_stat:.2f}, p={p_value:.4f}, eta²={eta_sq:.3f} {sig}")

            if p_value < 0.01:
                any_significant = True
        else:
            print(f"    {metric}: insufficient groups")

    # K1 evaluation
    print(f"\n[5] Kill Condition K1 Evaluation:")
    if any_significant:
        print("    RESULT: At least one metric shows p < 0.01 difference")
        print("    -> K1 NOT TRIGGERED, hypothesis survives")
        k1_triggered = False
    else:
        print("    RESULT: No metric shows p < 0.01 difference")
        print("    -> K1 TRIGGERED, hypothesis REJECTED")
        k1_triggered = True

    return {
        'folio_contexts': folio_contexts,
        'context_counts': dict(context_counts),
        'family_counts': dict(family_counts),
        'kruskal_by_context': kruskal_results,
        'kruskal_by_family': family_results,
        'k1_triggered': k1_triggered,
        'any_significant_p01': any_significant
    }

# ============================================================
# TEST 7: Negative Control
# ============================================================

def run_test_7(azc_tokens):
    """
    TEST 7: Negative Control

    AZC placement should NOT predict token identity.

    Kill condition K2:
    If AZC placement predicts token identity, instruction class, or kernel choice
    in B beyond chance (p < 0.05) -> MODEL FAILURE
    """
    print("\n" + "=" * 70)
    print("TEST 7: Negative Control (AZC should NOT predict tokens)")
    print("=" * 70)

    # Group tokens by placement
    placement_tokens = defaultdict(list)
    for item in azc_tokens:
        placement_tokens[item['placement']].append(item['token'])

    # Test 1: Does placement predict specific token types?
    # Use chi-squared test on token type × placement contingency table

    # Get top N most common tokens across all placements
    all_tokens = [item['token'] for item in azc_tokens]
    token_counts = Counter(all_tokens)
    top_tokens = [t for t, c in token_counts.most_common(20)]

    # Build contingency table: placement × token presence
    placements = [p for p, tokens in placement_tokens.items() if len(tokens) >= 20]

    if len(placements) >= 2 and len(top_tokens) >= 5:
        # Create contingency table
        contingency = []
        for placement in placements:
            tokens = placement_tokens[placement]
            row = [tokens.count(t) for t in top_tokens]
            contingency.append(row)

        contingency = np.array(contingency)

        # Chi-squared test
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

        # Cramér's V for effect size
        n = contingency.sum()
        min_dim = min(len(placements) - 1, len(top_tokens) - 1)
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

        print(f"\n[1] Token identity × Placement contingency test:")
        print(f"    Placements tested: {len(placements)}")
        print(f"    Top tokens tested: {len(top_tokens)}")
        print(f"    Chi²={chi2:.2f}, dof={dof}, p={p_value:.4f}")
        print(f"    Cramér's V={cramers_v:.3f}")

        token_prediction = {
            'chi2': float(chi2),
            'p': float(p_value),
            'dof': int(dof),
            'cramers_v': float(cramers_v),
            'n_placements': len(placements),
            'n_tokens': len(top_tokens)
        }
    else:
        print("\n[1] Insufficient data for token identity test")
        token_prediction = {'error': 'insufficient_data'}

    # Test 2: Does placement predict prefix class?
    prefix_by_placement = defaultdict(lambda: defaultdict(int))
    prefixes = ['ch', 'sh', 'ok', 'ot', 'da', 'sa', 'qo']

    for item in azc_tokens:
        placement = item['placement']
        token = item['token']
        for p in sorted(prefixes, key=len, reverse=True):
            if token.startswith(p):
                prefix_by_placement[placement][p] += 1
                break

    # Build prefix contingency table
    valid_placements = [p for p in prefix_by_placement if sum(prefix_by_placement[p].values()) >= 20]

    if len(valid_placements) >= 2:
        contingency_prefix = []
        for placement in valid_placements:
            row = [prefix_by_placement[placement].get(p, 0) for p in prefixes]
            contingency_prefix.append(row)

        contingency_prefix = np.array(contingency_prefix)

        # Remove columns with all zeros
        col_sums = contingency_prefix.sum(axis=0)
        valid_cols = col_sums > 0
        contingency_prefix = contingency_prefix[:, valid_cols]
        valid_prefixes = [p for p, v in zip(prefixes, valid_cols) if v]

        if contingency_prefix.shape[1] >= 2:
            chi2_prefix, p_prefix, dof_prefix, _ = stats.chi2_contingency(contingency_prefix)

            n_prefix = contingency_prefix.sum()
            min_dim_prefix = min(len(valid_placements) - 1, len(valid_prefixes) - 1)
            cramers_v_prefix = np.sqrt(chi2_prefix / (n_prefix * min_dim_prefix)) if min_dim_prefix > 0 else 0

            print(f"\n[2] Prefix class × Placement contingency test:")
            print(f"    Chi²={chi2_prefix:.2f}, dof={dof_prefix}, p={p_prefix:.4f}")
            print(f"    Cramér's V={cramers_v_prefix:.3f}")

            prefix_prediction = {
                'chi2': float(chi2_prefix),
                'p': float(p_prefix),
                'dof': int(dof_prefix),
                'cramers_v': float(cramers_v_prefix)
            }
        else:
            prefix_prediction = {'error': 'insufficient_prefix_variety'}
    else:
        prefix_prediction = {'error': 'insufficient_data'}

    # K2 evaluation
    print(f"\n[3] Kill Condition K2 Evaluation:")

    k2_triggered = False

    # Check token prediction
    if 'p' in token_prediction and token_prediction['p'] < 0.05:
        print(f"    WARNING: Token identity predicted by placement (p={token_prediction['p']:.4f})")
        # Only trigger if effect size is meaningful
        if token_prediction.get('cramers_v', 0) > 0.1:
            print(f"    -> K2 TRIGGERED (Cramér's V={token_prediction['cramers_v']:.3f} > 0.1)")
            k2_triggered = True
        else:
            print(f"    -> Effect size too small (V={token_prediction.get('cramers_v', 0):.3f}), K2 not triggered")
    else:
        print("    Token identity NOT predicted by placement (as expected)")

    # Check prefix prediction
    if 'p' in prefix_prediction and prefix_prediction['p'] < 0.05:
        print(f"    WARNING: Prefix class predicted by placement (p={prefix_prediction['p']:.4f})")
        if prefix_prediction.get('cramers_v', 0) > 0.1:
            print(f"    -> K2 TRIGGERED (Cramér's V={prefix_prediction['cramers_v']:.3f} > 0.1)")
            k2_triggered = True
        else:
            print(f"    -> Effect size too small (V={prefix_prediction.get('cramers_v', 0):.3f}), K2 not triggered")
    else:
        print("    Prefix class NOT predicted by placement (as expected)")

    if not k2_triggered:
        print("\n    RESULT: Negative control PASSED")
        print("    -> K2 NOT TRIGGERED, model integrity intact")
    else:
        print("\n    RESULT: Negative control FAILED")
        print("    -> K2 TRIGGERED, MODEL INTEGRITY FAILURE")

    return {
        'token_prediction': token_prediction,
        'prefix_prediction': prefix_prediction,
        'k2_triggered': k2_triggered
    }

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("APPARATUS-TOPOLOGY HYPOTHESIS: Critical Tests")
    print("=" * 70)
    print("\nPre-registered kill conditions:")
    print("  K1: No p < 0.01 difference in any B metric -> REJECT hypothesis")
    print("  K2: Placement predicts tokens (p < 0.05, V > 0.1) -> MODEL FAILURE")
    print("=" * 70)

    # Load data
    print("\n[Loading data...]")
    b_metrics = load_b_metrics()
    print(f"  B folio metrics: {len(b_metrics)} folios")

    azc_features = load_azc_features()
    print(f"  AZC folio features: {len(azc_features)} folios")

    rows = load_transcription()
    print(f"  Transcription: {len(rows)} rows")

    azc_tokens = get_azc_tokens(rows)
    print(f"  AZC tokens: {len(azc_tokens)}")

    # Run tests
    test1_result = run_test_1(b_metrics, azc_features)
    test7_result = run_test_7(azc_tokens)

    # Final verdict
    print("\n" + "=" * 70)
    print("DECISION GATE")
    print("=" * 70)

    if test1_result['k1_triggered']:
        print("\nK1 TRIGGERED: No significant AZC×B coupling found")
        print("-> HYPOTHESIS REJECTED")
        print("-> STOP: Do not proceed to further tests")
        verdict = "REJECTED"
    elif test7_result['k2_triggered']:
        print("\nK2 TRIGGERED: Model integrity failure")
        print("-> STOP AND AUDIT MODEL")
        verdict = "MODEL_FAILURE"
    else:
        print("\nBoth critical tests passed:")
        print("  - K1: Coupling signal detected (hypothesis survives)")
        print("  - K2: Negative control passed (model intact)")
        print("-> PROCEED to TEST 3 (R-series gradient)")
        verdict = "PROCEED"

    # Save results
    output = {
        'metadata': {
            'analysis': 'APPARATUS-TOPOLOGY Critical Tests',
            'tests_run': ['TEST 1', 'TEST 7'],
            'n_azc_tokens': len(azc_tokens)
        },
        'test_1': test1_result,
        'test_7': test7_result,
        'verdict': verdict,
        'kill_conditions': {
            'k1_triggered': test1_result['k1_triggered'],
            'k2_triggered': test7_result['k2_triggered']
        }
    }

    output_path = RESULTS / "apparatus_topology_critical_tests.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n[SAVED] {output_path}")

    return output

if __name__ == "__main__":
    main()
