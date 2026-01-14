#!/usr/bin/env python3
"""
F-AZC-010: Cross-System Alignment by Family

Hypothesis (Synthesis):
- Zodiac = seasonal/material gating -> should align with Currier A (material registry)
- A/C = operation-type gating -> should align with Currier B (procedures)

Predictions:
P1: Zodiac types overlap MORE with Currier A than A/C types do
P2: A/C types overlap MORE with Currier B than Zodiac types do
P3: Zodiac types are more "A-endemic" (appear in A, not B)
P4: A/C types are more "B-endemic" (appear in B, not A)

If confirmed: Zodiac and A/C gate different domains (materials vs operations)
If refuted: Both families gate the same domain, just parameterized differently
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# Family assignments
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


def load_all_tokens():
    """Load all tokens grouped by system and AZC family."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens_by_system = {
        'A': [],
        'B': [],
        'zodiac': [],
        'ac': []
    }

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 10:
                token = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip()
                currier = parts[6].strip('"').strip()

                if not token:
                    continue

                if currier == 'A':
                    tokens_by_system['A'].append(token)
                elif currier == 'B':
                    tokens_by_system['B'].append(token)
                elif currier == 'NA':  # AZC
                    if folio in ZODIAC_FAMILY:
                        tokens_by_system['zodiac'].append(token)
                    elif folio in AC_FAMILY:
                        tokens_by_system['ac'].append(token)

    return tokens_by_system


def get_unique_types(tokens_by_system):
    """Get unique types for each system."""
    return {
        system: set(tokens)
        for system, tokens in tokens_by_system.items()
    }


def calculate_overlap_metrics(family_types, a_types, b_types):
    """Calculate overlap metrics between a family and Currier A/B."""

    # Overlap with A
    overlap_a = len(family_types & a_types)
    overlap_a_rate = overlap_a / len(family_types) * 100 if family_types else 0

    # Overlap with B
    overlap_b = len(family_types & b_types)
    overlap_b_rate = overlap_b / len(family_types) * 100 if family_types else 0

    # A-endemic: appears in A but not B
    a_only = a_types - b_types
    family_a_endemic = len(family_types & a_only)
    a_endemic_rate = family_a_endemic / len(family_types) * 100 if family_types else 0

    # B-endemic: appears in B but not A
    b_only = b_types - a_types
    family_b_endemic = len(family_types & b_only)
    b_endemic_rate = family_b_endemic / len(family_types) * 100 if family_types else 0

    # Shared (appears in both A and B)
    shared = a_types & b_types
    family_shared = len(family_types & shared)
    shared_rate = family_shared / len(family_types) * 100 if family_types else 0

    # AZC-only (doesn't appear in A or B)
    azc_only = family_types - a_types - b_types
    azc_only_rate = len(azc_only) / len(family_types) * 100 if family_types else 0

    return {
        'total_types': len(family_types),
        'overlap_a': overlap_a,
        'overlap_a_rate': round(overlap_a_rate, 1),
        'overlap_b': overlap_b,
        'overlap_b_rate': round(overlap_b_rate, 1),
        'a_endemic': family_a_endemic,
        'a_endemic_rate': round(a_endemic_rate, 1),
        'b_endemic': family_b_endemic,
        'b_endemic_rate': round(b_endemic_rate, 1),
        'shared': family_shared,
        'shared_rate': round(shared_rate, 1),
        'azc_only': len(azc_only),
        'azc_only_rate': round(azc_only_rate, 1)
    }


def test_alignment_difference(zodiac_metrics, ac_metrics, a_types, b_types, zodiac_types, ac_types):
    """Test if alignment differences are significant."""

    # P1: Zodiac->A > A/C->A
    # Fisher's exact: compare overlap rates
    zodiac_a_overlap = len(zodiac_types & a_types)
    zodiac_a_non = len(zodiac_types) - zodiac_a_overlap
    ac_a_overlap = len(ac_types & a_types)
    ac_a_non = len(ac_types) - ac_a_overlap

    contingency_p1 = [
        [zodiac_a_overlap, zodiac_a_non],
        [ac_a_overlap, ac_a_non]
    ]
    _, p1_fisher = stats.fisher_exact(contingency_p1)
    p1_direction = zodiac_metrics['overlap_a_rate'] > ac_metrics['overlap_a_rate']

    # P2: A/C->B > Zodiac->B
    zodiac_b_overlap = len(zodiac_types & b_types)
    zodiac_b_non = len(zodiac_types) - zodiac_b_overlap
    ac_b_overlap = len(ac_types & b_types)
    ac_b_non = len(ac_types) - ac_b_overlap

    contingency_p2 = [
        [ac_b_overlap, ac_b_non],
        [zodiac_b_overlap, zodiac_b_non]
    ]
    _, p2_fisher = stats.fisher_exact(contingency_p2)
    p2_direction = ac_metrics['overlap_b_rate'] > zodiac_metrics['overlap_b_rate']

    # P3: Zodiac more A-endemic
    a_only = a_types - b_types
    zodiac_a_endemic = len(zodiac_types & a_only)
    zodiac_a_non_endemic = len(zodiac_types) - zodiac_a_endemic
    ac_a_endemic = len(ac_types & a_only)
    ac_a_non_endemic = len(ac_types) - ac_a_endemic

    contingency_p3 = [
        [zodiac_a_endemic, zodiac_a_non_endemic],
        [ac_a_endemic, ac_a_non_endemic]
    ]
    _, p3_fisher = stats.fisher_exact(contingency_p3)
    p3_direction = zodiac_metrics['a_endemic_rate'] > ac_metrics['a_endemic_rate']

    # P4: A/C more B-endemic
    b_only = b_types - a_types
    zodiac_b_endemic = len(zodiac_types & b_only)
    zodiac_b_non_endemic = len(zodiac_types) - zodiac_b_endemic
    ac_b_endemic = len(ac_types & b_only)
    ac_b_non_endemic = len(ac_types) - ac_b_endemic

    contingency_p4 = [
        [ac_b_endemic, ac_b_non_endemic],
        [zodiac_b_endemic, zodiac_b_non_endemic]
    ]
    _, p4_fisher = stats.fisher_exact(contingency_p4)
    p4_direction = ac_metrics['b_endemic_rate'] > zodiac_metrics['b_endemic_rate']

    return {
        'p1_zodiac_more_a': {
            'direction_correct': bool(p1_direction),
            'fisher_p': float(p1_fisher),
            'significant': bool(p1_fisher < 0.05),
            'zodiac_rate': zodiac_metrics['overlap_a_rate'],
            'ac_rate': ac_metrics['overlap_a_rate']
        },
        'p2_ac_more_b': {
            'direction_correct': bool(p2_direction),
            'fisher_p': float(p2_fisher),
            'significant': bool(p2_fisher < 0.05),
            'ac_rate': ac_metrics['overlap_b_rate'],
            'zodiac_rate': zodiac_metrics['overlap_b_rate']
        },
        'p3_zodiac_a_endemic': {
            'direction_correct': bool(p3_direction),
            'fisher_p': float(p3_fisher),
            'significant': bool(p3_fisher < 0.05),
            'zodiac_rate': zodiac_metrics['a_endemic_rate'],
            'ac_rate': ac_metrics['a_endemic_rate']
        },
        'p4_ac_b_endemic': {
            'direction_correct': bool(p4_direction),
            'fisher_p': float(p4_fisher),
            'significant': bool(p4_fisher < 0.05),
            'ac_rate': ac_metrics['b_endemic_rate'],
            'zodiac_rate': zodiac_metrics['b_endemic_rate']
        }
    }


def main():
    print("=" * 60)
    print("F-AZC-010: Cross-System Alignment by Family")
    print("=" * 60)
    print()
    print("Hypothesis (Synthesis):")
    print("  Zodiac = seasonal/material gating -> aligns with Currier A")
    print("  A/C = operation-type gating -> aligns with Currier B")
    print()
    print("PRE-REGISTERED PREDICTIONS:")
    print("  P1: Zodiac types overlap MORE with A than A/C types do")
    print("  P2: A/C types overlap MORE with B than Zodiac types do")
    print("  P3: Zodiac types are more A-endemic (in A, not B)")
    print("  P4: A/C types are more B-endemic (in B, not A)")
    print()

    # Load data
    tokens_by_system = load_all_tokens()
    types = get_unique_types(tokens_by_system)

    print(f"Currier A tokens: {len(tokens_by_system['A'])} ({len(types['A'])} types)")
    print(f"Currier B tokens: {len(tokens_by_system['B'])} ({len(types['B'])} types)")
    print(f"Zodiac tokens: {len(tokens_by_system['zodiac'])} ({len(types['zodiac'])} types)")
    print(f"A/C tokens: {len(tokens_by_system['ac'])} ({len(types['ac'])} types)")
    print()

    # Calculate overlap metrics
    zodiac_metrics = calculate_overlap_metrics(types['zodiac'], types['A'], types['B'])
    ac_metrics = calculate_overlap_metrics(types['ac'], types['A'], types['B'])

    # ==========================================
    # Zodiac Alignment
    # ==========================================
    print("=" * 60)
    print("ZODIAC FAMILY ALIGNMENT")
    print("=" * 60)
    print()
    print(f"Total unique types: {zodiac_metrics['total_types']}")
    print()
    print(f"Overlap with Currier A: {zodiac_metrics['overlap_a']} ({zodiac_metrics['overlap_a_rate']}%)")
    print(f"Overlap with Currier B: {zodiac_metrics['overlap_b']} ({zodiac_metrics['overlap_b_rate']}%)")
    print()
    print(f"A-endemic (in A, not B): {zodiac_metrics['a_endemic']} ({zodiac_metrics['a_endemic_rate']}%)")
    print(f"B-endemic (in B, not A): {zodiac_metrics['b_endemic']} ({zodiac_metrics['b_endemic_rate']}%)")
    print(f"Shared (in both A and B): {zodiac_metrics['shared']} ({zodiac_metrics['shared_rate']}%)")
    print(f"AZC-only (not in A or B): {zodiac_metrics['azc_only']} ({zodiac_metrics['azc_only_rate']}%)")
    print()

    # ==========================================
    # A/C Alignment
    # ==========================================
    print("=" * 60)
    print("A/C FAMILY ALIGNMENT")
    print("=" * 60)
    print()
    print(f"Total unique types: {ac_metrics['total_types']}")
    print()
    print(f"Overlap with Currier A: {ac_metrics['overlap_a']} ({ac_metrics['overlap_a_rate']}%)")
    print(f"Overlap with Currier B: {ac_metrics['overlap_b']} ({ac_metrics['overlap_b_rate']}%)")
    print()
    print(f"A-endemic (in A, not B): {ac_metrics['a_endemic']} ({ac_metrics['a_endemic_rate']}%)")
    print(f"B-endemic (in B, not A): {ac_metrics['b_endemic']} ({ac_metrics['b_endemic_rate']}%)")
    print(f"Shared (in both A and B): {ac_metrics['shared']} ({ac_metrics['shared_rate']}%)")
    print(f"AZC-only (not in A or B): {ac_metrics['azc_only']} ({ac_metrics['azc_only_rate']}%)")
    print()

    # ==========================================
    # Statistical Tests
    # ==========================================
    print("=" * 60)
    print("PREDICTION TESTS")
    print("=" * 60)
    print()

    tests = test_alignment_difference(
        zodiac_metrics, ac_metrics,
        types['A'], types['B'],
        types['zodiac'], types['ac']
    )

    print("P1: Zodiac overlaps MORE with A than A/C does")
    print(f"    Zodiac-A: {tests['p1_zodiac_more_a']['zodiac_rate']}%")
    print(f"    A/C-A: {tests['p1_zodiac_more_a']['ac_rate']}%")
    print(f"    Direction correct: {'YES' if tests['p1_zodiac_more_a']['direction_correct'] else 'NO'}")
    print(f"    Fisher's p: {tests['p1_zodiac_more_a']['fisher_p']:.6f}")
    print(f"    Significant: {'YES ***' if tests['p1_zodiac_more_a']['significant'] else 'NO'}")
    print()

    print("P2: A/C overlaps MORE with B than Zodiac does")
    print(f"    A/C-B: {tests['p2_ac_more_b']['ac_rate']}%")
    print(f"    Zodiac-B: {tests['p2_ac_more_b']['zodiac_rate']}%")
    print(f"    Direction correct: {'YES' if tests['p2_ac_more_b']['direction_correct'] else 'NO'}")
    print(f"    Fisher's p: {tests['p2_ac_more_b']['fisher_p']:.6f}")
    print(f"    Significant: {'YES ***' if tests['p2_ac_more_b']['significant'] else 'NO'}")
    print()

    print("P3: Zodiac is more A-endemic than A/C")
    print(f"    Zodiac A-endemic: {tests['p3_zodiac_a_endemic']['zodiac_rate']}%")
    print(f"    A/C A-endemic: {tests['p3_zodiac_a_endemic']['ac_rate']}%")
    print(f"    Direction correct: {'YES' if tests['p3_zodiac_a_endemic']['direction_correct'] else 'NO'}")
    print(f"    Fisher's p: {tests['p3_zodiac_a_endemic']['fisher_p']:.6f}")
    print(f"    Significant: {'YES ***' if tests['p3_zodiac_a_endemic']['significant'] else 'NO'}")
    print()

    print("P4: A/C is more B-endemic than Zodiac")
    print(f"    A/C B-endemic: {tests['p4_ac_b_endemic']['ac_rate']}%")
    print(f"    Zodiac B-endemic: {tests['p4_ac_b_endemic']['zodiac_rate']}%")
    print(f"    Direction correct: {'YES' if tests['p4_ac_b_endemic']['direction_correct'] else 'NO'}")
    print(f"    Fisher's p: {tests['p4_ac_b_endemic']['fisher_p']:.6f}")
    print(f"    Significant: {'YES ***' if tests['p4_ac_b_endemic']['significant'] else 'NO'}")
    print()

    # ==========================================
    # Summary
    # ==========================================
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()

    predictions = {
        'p1': tests['p1_zodiac_more_a']['direction_correct'] and tests['p1_zodiac_more_a']['significant'],
        'p2': tests['p2_ac_more_b']['direction_correct'] and tests['p2_ac_more_b']['significant'],
        'p3': tests['p3_zodiac_a_endemic']['direction_correct'] and tests['p3_zodiac_a_endemic']['significant'],
        'p4': tests['p4_ac_b_endemic']['direction_correct'] and tests['p4_ac_b_endemic']['significant']
    }

    predictions_met = sum(predictions.values())

    print(f"Predictions met: {predictions_met}/4")
    print(f"  P1 (Zodiac->A > A/C->A): {'MET' if predictions['p1'] else 'NOT MET'}")
    print(f"  P2 (A/C->B > Zodiac->B): {'MET' if predictions['p2'] else 'NOT MET'}")
    print(f"  P3 (Zodiac A-endemic): {'MET' if predictions['p3'] else 'NOT MET'}")
    print(f"  P4 (A/C B-endemic): {'MET' if predictions['p4'] else 'NOT MET'}")
    print()

    # Interpretation
    if predictions_met >= 3:
        conclusion = "SYNTHESIS CONFIRMED"
        interpretation = "Zodiac and A/C gate DIFFERENT domains (materials vs operations)"
        fit_tier = "F3"
    elif predictions_met >= 2:
        conclusion = "WEAK SUPPORT for synthesis"
        interpretation = "Partial differentiation between families"
        fit_tier = "F4"
    else:
        conclusion = "SYNTHESIS NOT SUPPORTED"
        interpretation = "Both families gate the SAME domain, just parameterized differently"
        fit_tier = "F4"

    print(f"CONCLUSION: {conclusion}")
    print(f"INTERPRETATION: {interpretation}")
    print(f"Fit tier: {fit_tier}")

    # Prepare output
    output = {
        'fit_id': 'F-AZC-010',
        'hypothesis': 'Zodiac gates materials (A-aligned), A/C gates operations (B-aligned)',
        'tier': 4,
        'metadata': {
            'a_tokens': len(tokens_by_system['A']),
            'a_types': len(types['A']),
            'b_tokens': len(tokens_by_system['B']),
            'b_types': len(types['B']),
            'zodiac_tokens': len(tokens_by_system['zodiac']),
            'zodiac_types': len(types['zodiac']),
            'ac_tokens': len(tokens_by_system['ac']),
            'ac_types': len(types['ac'])
        },
        'zodiac_metrics': zodiac_metrics,
        'ac_metrics': ac_metrics,
        'tests': tests,
        'predictions': predictions,
        'predictions_met': predictions_met,
        'interpretation': {
            'conclusion': conclusion,
            'interpretation': interpretation,
            'fit_tier': fit_tier
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_cross_system_alignment.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
