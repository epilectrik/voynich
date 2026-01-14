#!/usr/bin/env python3
"""
F-AZC-008: Boundary Asymmetry Test

Semantic Hypothesis: C and S positions are functionally asymmetric
- C = Intake/Initialization (entry into AZC processing zone)
- S = Release/Finalization (exit from AZC processing zone)

Structural Predictions:
1. SUFFIX entropy: C < S (C constrains, S permits)
2. MIDDLE universality: C > S (C uses core, S allows tail)
3. Escape prefix rate: C < S (already observed: 2.34% vs 4.36%)
4. Type overlap: Low Jaccard similarity (<50%)
5. Distributional difference: Chi-squared p < 0.05

Protocol: Name boldly. Test ruthlessly. Promote rarely.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from math import log2
import numpy as np
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token

# A/C family folios
AC_FAMILY = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

# Position classifications
C_POSITIONS = {'C', 'C1', 'C2'}  # Intake positions (early in line)
S_POSITIONS = {'S', 'S1', 'S2', 'S3'}  # Release positions (late in line)

# Universal MIDDLEs (from prior analysis)
UNIVERSAL_MIDDLES = {'ol', 'or', 'al', 'ar', 'y', 'o', 'a', 'chol', 'chor', 'sho', 'she'}

# Escape prefixes
ESCAPE_PREFIXES = {'qo', 'ct'}


def calculate_entropy(counts):
    """Calculate Shannon entropy from a Counter or dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * log2(p)
    return entropy


def load_ac_tokens():
    """Load all A/C family tokens with morphological decomposition."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 10:
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()
                    placement = parts[10].strip('"').strip()

                    if folio in AC_FAMILY and token and placement:
                        result = decompose_token(token)
                        if result[0]:  # Successfully decomposed
                            prefix, middle, suffix = result

                            is_escape = prefix in ESCAPE_PREFIXES
                            is_universal_middle = middle in UNIVERSAL_MIDDLES if middle else False

                            tokens.append({
                                'token': token,
                                'folio': folio,
                                'placement': placement,
                                'prefix': prefix,
                                'middle': middle or '',
                                'suffix': suffix or '',
                                'is_escape': is_escape,
                                'is_universal_middle': is_universal_middle
                            })
    return tokens


def analyze_slot_entropy(tokens, slot):
    """Calculate entropy for a specific morphological slot."""
    values = [t[slot] for t in tokens if t[slot]]
    counts = Counter(values)
    return {
        'entropy': calculate_entropy(counts),
        'n_tokens': len(values),
        'n_unique': len(counts),
        'top_values': counts.most_common(5)
    }


def compare_distributions(c_tokens, s_tokens, slot):
    """Chi-squared test comparing slot distributions between C and S."""
    c_values = Counter(t[slot] for t in c_tokens if t[slot])
    s_values = Counter(t[slot] for t in s_tokens if t[slot])

    # Get all unique values
    all_values = sorted(set(c_values.keys()) | set(s_values.keys()))

    if len(all_values) < 2:
        return {'insufficient_data': True}

    # Build contingency table
    c_counts = [c_values.get(v, 0) for v in all_values]
    s_counts = [s_values.get(v, 0) for v in all_values]

    # Filter out zero columns (required for chi-squared)
    valid_indices = [i for i in range(len(all_values)) if c_counts[i] > 0 or s_counts[i] > 0]
    c_counts = [c_counts[i] for i in valid_indices]
    s_counts = [s_counts[i] for i in valid_indices]

    if len(c_counts) < 2:
        return {'insufficient_data': True}

    # Chi-squared test
    contingency = np.array([c_counts, s_counts])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    # Cramér's V for effect size
    n = contingency.sum()
    min_dim = min(contingency.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

    return {
        'chi2': float(chi2),
        'p_value': float(p_value),
        'dof': int(dof),
        'cramers_v': float(cramers_v),
        'significant': bool(p_value < 0.05),
        'n_categories': len(c_counts)
    }


def calculate_jaccard_overlap(c_tokens, s_tokens):
    """Calculate Jaccard similarity for token types."""
    c_types = set(t['token'] for t in c_tokens)
    s_types = set(t['token'] for t in s_tokens)

    intersection = len(c_types & s_types)
    union = len(c_types | s_types)

    jaccard = intersection / union if union > 0 else 0

    return {
        'c_unique_types': len(c_types),
        's_unique_types': len(s_types),
        'shared_types': intersection,
        'total_types': union,
        'jaccard_similarity': float(jaccard),
        'distinct': bool(jaccard < 0.5)
    }


def analyze_universal_middle_rate(tokens):
    """Calculate rate of universal MIDDLE usage."""
    total = len(tokens)
    universal_count = sum(1 for t in tokens if t['is_universal_middle'])

    return {
        'universal_count': universal_count,
        'total': total,
        'rate': universal_count / total * 100 if total > 0 else 0
    }


def analyze_escape_rate(tokens):
    """Calculate escape prefix rate."""
    total = len(tokens)
    escape_count = sum(1 for t in tokens if t['is_escape'])

    return {
        'escape_count': escape_count,
        'total': total,
        'rate': escape_count / total * 100 if total > 0 else 0
    }


def test_entropy_difference(c_tokens, s_tokens, slot):
    """Test if entropy differs significantly between C and S positions."""
    c_entropy = analyze_slot_entropy(c_tokens, slot)
    s_entropy = analyze_slot_entropy(s_tokens, slot)

    entropy_delta = s_entropy['entropy'] - c_entropy['entropy']

    # For statistical test, we need to bootstrap or use permutation
    # Simple approach: compare the entropies directly
    return {
        'c_entropy': round(c_entropy['entropy'], 3),
        's_entropy': round(s_entropy['entropy'], 3),
        'delta': round(entropy_delta, 3),
        'c_unique': c_entropy['n_unique'],
        's_unique': s_entropy['n_unique'],
        'c_n': c_entropy['n_tokens'],
        's_n': s_entropy['n_tokens'],
        'significant_delta': abs(entropy_delta) > 0.3  # Threshold from plan
    }


def test_universal_difference(c_tokens, s_tokens):
    """Test if universal MIDDLE rate differs between C and S."""
    c_rate = analyze_universal_middle_rate(c_tokens)
    s_rate = analyze_universal_middle_rate(s_tokens)

    # Fisher's exact test
    contingency = [
        [c_rate['universal_count'], c_rate['total'] - c_rate['universal_count']],
        [s_rate['universal_count'], s_rate['total'] - s_rate['universal_count']]
    ]
    odds_ratio, fisher_p = stats.fisher_exact(contingency)

    return {
        'c_rate': round(c_rate['rate'], 2),
        's_rate': round(s_rate['rate'], 2),
        'delta': round(c_rate['rate'] - s_rate['rate'], 2),
        'odds_ratio': round(float(odds_ratio), 3),
        'fisher_p': float(fisher_p),
        'significant': bool(fisher_p < 0.05),
        'c_higher': c_rate['rate'] > s_rate['rate']
    }


def test_escape_difference(c_tokens, s_tokens):
    """Test if escape rate differs between C and S."""
    c_rate = analyze_escape_rate(c_tokens)
    s_rate = analyze_escape_rate(s_tokens)

    # Fisher's exact test
    contingency = [
        [c_rate['escape_count'], c_rate['total'] - c_rate['escape_count']],
        [s_rate['escape_count'], s_rate['total'] - s_rate['escape_count']]
    ]
    odds_ratio, fisher_p = stats.fisher_exact(contingency)

    return {
        'c_rate': round(c_rate['rate'], 2),
        's_rate': round(s_rate['rate'], 2),
        'delta': round(s_rate['rate'] - c_rate['rate'], 2),
        'odds_ratio': round(float(odds_ratio), 3),
        'fisher_p': float(fisher_p),
        'significant': bool(fisher_p < 0.05),
        's_higher': s_rate['rate'] > c_rate['rate']
    }


def main():
    print("=" * 60)
    print("F-AZC-008: Boundary Asymmetry Test")
    print("=" * 60)
    print()
    print("Hypothesis: C and S positions are functionally asymmetric")
    print("  - C = Intake/Initialization")
    print("  - S = Release/Finalization")
    print()

    # Load data
    tokens = load_ac_tokens()
    print(f"Total A/C tokens: {len(tokens)}")

    # Split by position
    c_tokens = [t for t in tokens if t['placement'] in C_POSITIONS]
    s_tokens = [t for t in tokens if t['placement'] in S_POSITIONS]

    print(f"C-position tokens: {len(c_tokens)}")
    print(f"S-position tokens: {len(s_tokens)}")
    print()

    # ==========================================
    # Test 1: Entropy by Slot
    # ==========================================
    print("=" * 60)
    print("TEST 1: Per-Slot Entropy Comparison")
    print("=" * 60)
    print()

    entropy_results = {}
    for slot in ['prefix', 'middle', 'suffix']:
        result = test_entropy_difference(c_tokens, s_tokens, slot)
        entropy_results[slot] = result

        print(f"{slot.upper()}:")
        print(f"  C entropy: {result['c_entropy']} bits ({result['c_unique']} unique)")
        print(f"  S entropy: {result['s_entropy']} bits ({result['s_unique']} unique)")
        print(f"  Delta (S-C): {result['delta']} bits")
        print(f"  Significant (>0.3 bits): {'YES' if result['significant_delta'] else 'NO'}")
        print()

    # ==========================================
    # Test 2: Distribution Comparison
    # ==========================================
    print("=" * 60)
    print("TEST 2: Distribution Comparison (Chi-Squared)")
    print("=" * 60)
    print()

    distribution_results = {}
    for slot in ['prefix', 'middle', 'suffix']:
        result = compare_distributions(c_tokens, s_tokens, slot)
        distribution_results[slot] = result

        if 'insufficient_data' not in result:
            print(f"{slot.upper()}:")
            print(f"  Chi-squared: {result['chi2']:.2f}")
            print(f"  p-value: {result['p_value']:.6f}")
            print(f"  Cramér's V: {result['cramers_v']:.3f}")
            print(f"  Significant: {'YES ***' if result['significant'] else 'NO'}")
            print()
        else:
            print(f"{slot.upper()}: Insufficient data")
            print()

    # ==========================================
    # Test 3: Type Overlap (Jaccard)
    # ==========================================
    print("=" * 60)
    print("TEST 3: Type Overlap (Jaccard Similarity)")
    print("=" * 60)
    print()

    jaccard_result = calculate_jaccard_overlap(c_tokens, s_tokens)

    print(f"C-position unique types: {jaccard_result['c_unique_types']}")
    print(f"S-position unique types: {jaccard_result['s_unique_types']}")
    print(f"Shared types: {jaccard_result['shared_types']}")
    print(f"Total types: {jaccard_result['total_types']}")
    print(f"Jaccard similarity: {jaccard_result['jaccard_similarity']:.3f}")
    print(f"Distinct (<0.5): {'YES' if jaccard_result['distinct'] else 'NO'}")
    print()

    # ==========================================
    # Test 4: Universal MIDDLE Rate
    # ==========================================
    print("=" * 60)
    print("TEST 4: Universal MIDDLE Usage")
    print("=" * 60)
    print()

    universal_result = test_universal_difference(c_tokens, s_tokens)

    print(f"C-position universal rate: {universal_result['c_rate']:.1f}%")
    print(f"S-position universal rate: {universal_result['s_rate']:.1f}%")
    print(f"Delta (C-S): {universal_result['delta']:.1f}pp")
    print(f"Fisher's exact p: {universal_result['fisher_p']:.6f}")
    print(f"Significant: {'YES ***' if universal_result['significant'] else 'NO'}")
    print(f"C uses more universals: {'YES' if universal_result['c_higher'] else 'NO'}")
    print()

    # ==========================================
    # Test 5: Escape Rate (Confirmation)
    # ==========================================
    print("=" * 60)
    print("TEST 5: Escape Rate Confirmation")
    print("=" * 60)
    print()

    escape_result = test_escape_difference(c_tokens, s_tokens)

    print(f"C-position escape rate: {escape_result['c_rate']:.1f}%")
    print(f"S-position escape rate: {escape_result['s_rate']:.1f}%")
    print(f"Delta (S-C): {escape_result['delta']:.1f}pp")
    print(f"Fisher's exact p: {escape_result['fisher_p']:.6f}")
    print(f"Significant: {'YES ***' if escape_result['significant'] else 'NO'}")
    print(f"S has more escapes: {'YES' if escape_result['s_higher'] else 'NO'}")
    print()

    # ==========================================
    # Evidence Summary
    # ==========================================
    print("=" * 60)
    print("EVIDENCE SUMMARY")
    print("=" * 60)
    print()

    evidence = {
        'entropy_asymmetry': any(r['significant_delta'] for r in entropy_results.values()),
        'distribution_difference': any(r.get('significant', False) for r in distribution_results.values()),
        'type_distinctiveness': jaccard_result['distinct'],
        'universal_asymmetry': universal_result['significant'] and universal_result['c_higher'],
        'escape_asymmetry': escape_result['significant'] and escape_result['s_higher']
    }

    criteria_met = sum(evidence.values())

    print(f"Criteria met: {criteria_met}/5")
    print()
    for criterion, met in evidence.items():
        status = "MET" if met else "NOT MET"
        print(f"  {criterion}: {status}")
    print()

    # Interpretation
    if criteria_met >= 3:
        conclusion = "C and S are FUNCTIONALLY ASYMMETRIC"
        mechanism = "C = constrained intake, S = permissive release"
        fit_tier = "F2"
    elif criteria_met == 2:
        conclusion = "C and S show WEAK asymmetry"
        mechanism = "Partial functional differentiation"
        fit_tier = "F3"
    else:
        conclusion = "C and S are FUNCTIONALLY EQUIVALENT"
        mechanism = "Positions are symmetric boundaries"
        fit_tier = "F4"

    print(f"CONCLUSION: {conclusion}")
    print(f"MECHANISM: {mechanism}")
    print(f"Fit tier: {fit_tier}")

    # Prepare output
    output = {
        'fit_id': 'F-AZC-008',
        'hypothesis': 'C and S positions are functionally asymmetric (C=intake, S=release)',
        'tier': 4,  # Exploratory hypothesis
        'metadata': {
            'total_ac_tokens': len(tokens),
            'c_tokens': len(c_tokens),
            's_tokens': len(s_tokens),
            'c_positions': list(C_POSITIONS),
            's_positions': list(S_POSITIONS)
        },
        'c_stats': {
            'n': len(c_tokens),
            'prefix_entropy': entropy_results['prefix']['c_entropy'],
            'middle_entropy': entropy_results['middle']['c_entropy'],
            'suffix_entropy': entropy_results['suffix']['c_entropy'],
            'universal_rate': universal_result['c_rate'],
            'escape_rate': escape_result['c_rate']
        },
        's_stats': {
            'n': len(s_tokens),
            'prefix_entropy': entropy_results['prefix']['s_entropy'],
            'middle_entropy': entropy_results['middle']['s_entropy'],
            'suffix_entropy': entropy_results['suffix']['s_entropy'],
            'universal_rate': universal_result['s_rate'],
            'escape_rate': escape_result['s_rate']
        },
        'entropy_tests': entropy_results,
        'distribution_tests': {k: {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in distribution_results.items()},
        'jaccard_overlap': jaccard_result,
        'universal_middle_test': universal_result,
        'escape_test': escape_result,
        'evidence': evidence,
        'interpretation': {
            'criteria_met': criteria_met,
            'conclusion': conclusion,
            'mechanism': mechanism,
            'fit_tier': fit_tier
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_boundary_asymmetry.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
