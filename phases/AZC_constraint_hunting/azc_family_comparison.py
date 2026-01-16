#!/usr/bin/env python3
"""
AZC Constraint Hunt - Stage 3: Zodiac vs Non-Zodiac Family Comparison

Test 3.1: Vocabulary Overlap by Family
Test 3.2: Placement Grammar Differences
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
from math import log2

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token

# AZC family assignments
ZODIAC_FAMILY = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FAMILY = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}


def load_azc_tokens():
    """Load all AZC tokens with family and placement information."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()
                    placement = parts[10].strip('"').strip()

                    if token:
                        if folio in ZODIAC_FAMILY:
                            family = 'zodiac'
                        elif folio in AC_FAMILY:
                            family = 'ac'
                        else:
                            family = 'unknown'

                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'family': family,
                            'placement': placement
                        })
    return tokens


def jaccard_similarity(set1, set2):
    """Calculate Jaccard similarity between two sets."""
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0


def calculate_entropy(counts):
    """Calculate Shannon entropy from count dict."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * log2(p)
    return entropy


def analyze_family_comparison():
    """Analyze Zodiac vs A/C family differences."""

    print("=" * 60)
    print("AZC Constraint Hunt - Stage 3: Family Comparison")
    print("=" * 60)
    print()

    # Load data
    tokens = load_azc_tokens()

    zodiac_tokens = [t for t in tokens if t['family'] == 'zodiac']
    ac_tokens = [t for t in tokens if t['family'] == 'ac']

    print(f"Zodiac tokens: {len(zodiac_tokens)}")
    print(f"A/C tokens: {len(ac_tokens)}")
    print()

    # ==========================================
    # Test 3.1: Vocabulary Overlap by Family
    # ==========================================
    print("=" * 60)
    print("Test 3.1: Vocabulary Overlap by Family")
    print("=" * 60)
    print()

    # Get vocabulary sets
    zodiac_vocab = set(t['token'] for t in zodiac_tokens)
    ac_vocab = set(t['token'] for t in ac_tokens)

    shared_vocab = zodiac_vocab & ac_vocab
    zodiac_exclusive = zodiac_vocab - ac_vocab
    ac_exclusive = ac_vocab - zodiac_vocab

    jaccard = jaccard_similarity(zodiac_vocab, ac_vocab)

    print("Vocabulary Statistics:")
    print("-" * 40)
    print(f"Zodiac unique types: {len(zodiac_vocab)}")
    print(f"A/C unique types: {len(ac_vocab)}")
    print(f"Shared types: {len(shared_vocab)}")
    print(f"Zodiac exclusive: {len(zodiac_exclusive)}")
    print(f"A/C exclusive: {len(ac_exclusive)}")
    print(f"Jaccard similarity: {jaccard:.3f}")
    print()

    # Compare to within-family baselines (from C430)
    print("Comparison to known baselines:")
    print(f"  Within-Zodiac consistency: 0.964 (from C430)")
    print(f"  Within-A/C consistency: 0.340 (from C430)")
    print(f"  Zodiac-to-A/C Jaccard: {jaccard:.3f}")
    print()

    if jaccard < 0.340:
        vocab_finding = "Families are vocabulary-distinct (Jaccard < within-A/C consistency)"
    else:
        vocab_finding = "Families share substantial vocabulary"
    print(f"Finding: {vocab_finding}")
    print()

    # ==========================================
    # Test 3.2: Placement Grammar Differences
    # ==========================================
    print("=" * 60)
    print("Test 3.2: Placement Grammar Differences")
    print("=" * 60)
    print()

    # Collect morphology by family and placement
    family_placement_suffix = defaultdict(lambda: defaultdict(Counter))
    family_placement_prefix = defaultdict(lambda: defaultdict(Counter))
    family_placement_counts = defaultdict(Counter)

    for t in tokens:
        result = decompose_token(t['token'])
        if result[0]:
            prefix, middle, suffix = result
            family = t['family']
            placement = t['placement']

            family_placement_suffix[family][placement][suffix] += 1
            family_placement_prefix[family][placement][prefix] += 1
            family_placement_counts[family][placement] += 1

    # Compare placement distributions
    print("Placement Distribution by Family:")
    print("-" * 50)
    print(f"{'Placement':<10} {'Zodiac %':>10} {'A/C %':>10} {'Difference':>12}")
    print("-" * 50)

    zodiac_total = sum(family_placement_counts['zodiac'].values())
    ac_total = sum(family_placement_counts['ac'].values())

    all_placements = set(family_placement_counts['zodiac'].keys()) | set(family_placement_counts['ac'].keys())

    placement_diffs = []
    for placement in sorted(all_placements):
        z_pct = family_placement_counts['zodiac'][placement] / zodiac_total * 100 if zodiac_total > 0 else 0
        ac_pct = family_placement_counts['ac'][placement] / ac_total * 100 if ac_total > 0 else 0
        diff = z_pct - ac_pct
        placement_diffs.append((placement, z_pct, ac_pct, diff))
        print(f"{placement:<10} {z_pct:>9.1f}% {ac_pct:>9.1f}% {diff:>+11.1f}pp")
    print()

    # Chi-squared test for family × placement association
    placements_both = [p for p in all_placements if family_placement_counts['zodiac'][p] >= 5 and family_placement_counts['ac'][p] >= 5]
    if len(placements_both) >= 2:
        contingency = []
        for p in placements_both:
            contingency.append([family_placement_counts['zodiac'][p], family_placement_counts['ac'][p]])

        # Transpose for chi2_contingency
        contingency_t = list(map(list, zip(*contingency)))
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_t)

        print("Chi-squared Test (Family × Placement):")
        print(f"  Chi-squared: {chi2:.2f}")
        print(f"  p-value: {p_value:.10f}")
        print(f"  Result: {'SIGNIFICANT - Placement distribution differs' if p_value < 0.05 else 'NOT SIGNIFICANT'}")
        print()

    # Suffix entropy by family for common placements
    print("Suffix Entropy by Family (for R-series placements):")
    print("-" * 50)

    r_placements = ['R', 'R1', 'R2', 'R3']
    for placement in r_placements:
        z_suffixes = family_placement_suffix['zodiac'][placement]
        ac_suffixes = family_placement_suffix['ac'][placement]

        z_ent = calculate_entropy(z_suffixes)
        ac_ent = calculate_entropy(ac_suffixes)

        z_n = sum(z_suffixes.values())
        ac_n = sum(ac_suffixes.values())

        if z_n >= 10 or ac_n >= 10:
            print(f"  {placement}: Zodiac={z_ent:.2f} bits (N={z_n}), A/C={ac_ent:.2f} bits (N={ac_n})")
    print()

    # Prefix distribution by family for common placements
    print("Key Prefix Differences (ot, ok, qo):")
    print("-" * 50)

    for prefix in ['ot', 'ok', 'qo', 'ch']:
        z_count = sum(family_placement_prefix['zodiac'][p][prefix] for p in all_placements)
        ac_count = sum(family_placement_prefix['ac'][p][prefix] for p in all_placements)

        z_pct = z_count / zodiac_total * 100 if zodiac_total > 0 else 0
        ac_pct = ac_count / ac_total * 100 if ac_total > 0 else 0

        print(f"  {prefix}: Zodiac={z_pct:.1f}%, A/C={ac_pct:.1f}%, diff={z_pct-ac_pct:+.1f}pp")
    print()

    # ==========================================
    # Summary Output
    # ==========================================
    output = {
        'metadata': {
            'tests': ['3.1', '3.2'],
            'zodiac_tokens': len(zodiac_tokens),
            'ac_tokens': len(ac_tokens)
        },
        'test_3_1': {
            'question': 'Vocabulary overlap by family',
            'zodiac_types': len(zodiac_vocab),
            'ac_types': len(ac_vocab),
            'shared_types': len(shared_vocab),
            'zodiac_exclusive': len(zodiac_exclusive),
            'ac_exclusive': len(ac_exclusive),
            'jaccard_similarity': round(jaccard, 3),
            'finding': vocab_finding
        },
        'test_3_2': {
            'question': 'Placement grammar differences',
            'placement_distribution': {
                'zodiac': {p: round(c / zodiac_total * 100, 2) for p, c in family_placement_counts['zodiac'].items()},
                'ac': {p: round(c / ac_total * 100, 2) for p, c in family_placement_counts['ac'].items()}
            },
            'chi_squared': round(float(chi2), 2) if len(placements_both) >= 2 else None,
            'p_value': float(p_value) if len(placements_both) >= 2 else None,
            'significant': bool(p_value < 0.05) if len(placements_both) >= 2 else None
        },
        'interpretation': {
            'test_3_1': vocab_finding,
            'test_3_2': 'Families show different placement distributions' if len(placements_both) >= 2 and p_value < 0.05 else 'Insufficient evidence for placement grammar differences',
            'overall': None
        }
    }

    # Overall interpretation
    if jaccard < 0.340 or (len(placements_both) >= 2 and p_value < 0.05):
        output['interpretation']['overall'] = "Zodiac and A/C families implement distinct scaffolding strategies"
    else:
        output['interpretation']['overall'] = "Families share more structure than expected"

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"Test 3.1: {output['interpretation']['test_3_1']}")
    print(f"Test 3.2: {output['interpretation']['test_3_2']}")
    print(f"Overall: {output['interpretation']['overall']}")

    return output


def main():
    output = analyze_family_comparison()

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_family_comparison.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
