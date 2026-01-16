#!/usr/bin/env python3
"""
AZC Constraint Hunt - Test 1.1: MIDDLE Universality in AZC

Question: When A-vocabulary tokens appear in AZC, are universal MIDDLEs
preserved, suppressed, or enriched?

Baseline (from Currier A):
- Universal MIDDLEs: 2.48% of types → 43.74% of tokens
- Universal mean suffix entropy: 2.371 bits
- Other mean suffix entropy: 1.382 bits

Possible Constraints:
- "AZC preferentially admits universal MIDDLEs" (filtering)
- "AZC preserves A's MIDDLE distribution" (passthrough)
- "AZC suppresses tail MIDDLEs" (gating)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token


def load_azc_tokens():
    """Load all AZC tokens (Currier = NA)."""
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
                    placement = parts[10].strip('"').strip() if len(parts) > 10 else ''
                    if token:
                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'placement': placement
                        })
    return tokens


def load_middle_taxonomy():
    """Load universal/bridging/exclusive MIDDLE classification from A analysis."""
    filepath = Path(__file__).parent.parent.parent / 'results' / 'middle_class_sharing.json'

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Extract universal MIDDLEs
    universal_middles = set()
    for item in data.get('universal_analysis', {}).get('details', []):
        universal_middles.add(item['middle'])

    # For now, we don't have explicit bridging/exclusive lists
    # So we'll classify as: universal, tri-class, bi-class, exclusive
    # But the main test is universal vs other

    return universal_middles, data


def analyze_middle_distribution():
    """Analyze MIDDLE universality in AZC tokens."""

    print("=" * 60)
    print("AZC Constraint Hunt - Test 1.1: MIDDLE Universality")
    print("=" * 60)
    print()

    # Load data
    azc_tokens = load_azc_tokens()
    universal_middles, taxonomy_data = load_middle_taxonomy()

    print(f"AZC tokens loaded: {len(azc_tokens)}")
    print(f"Universal MIDDLEs from A taxonomy: {len(universal_middles)}")
    print(f"Universal MIDDLEs: {sorted(universal_middles)[:10]}...")
    print()

    # Decompose AZC tokens and classify MIDDLEs
    middle_counts = Counter()
    universal_token_count = 0
    other_token_count = 0
    decomposed_count = 0
    failed_count = 0

    middle_categories = {
        'universal': [],
        'other': []
    }

    for item in azc_tokens:
        token = item['token']
        result = decompose_token(token)

        if result[0]:  # Has valid prefix
            prefix, middle, suffix = result
            decomposed_count += 1
            middle_counts[middle] += 1

            if middle in universal_middles:
                universal_token_count += 1
                middle_categories['universal'].append(middle)
            else:
                other_token_count += 1
                middle_categories['other'].append(middle)
        else:
            failed_count += 1

    # Calculate statistics
    total_decomposed = decomposed_count
    universal_pct = (universal_token_count / total_decomposed * 100) if total_decomposed > 0 else 0

    # Baseline from A
    a_universal_pct = 43.74

    print("Results:")
    print("-" * 40)
    print(f"Tokens decomposed: {decomposed_count} ({decomposed_count/len(azc_tokens)*100:.1f}%)")
    print(f"Decomposition failed: {failed_count}")
    print()
    print(f"Universal MIDDLE tokens: {universal_token_count} ({universal_pct:.2f}%)")
    print(f"Other MIDDLE tokens: {other_token_count} ({100-universal_pct:.2f}%)")
    print()
    print(f"A baseline universal: {a_universal_pct:.2f}%")
    print(f"AZC universal: {universal_pct:.2f}%")
    print(f"Difference: {universal_pct - a_universal_pct:+.2f} percentage points")
    print()

    # Chi-squared test: AZC vs A distribution
    # Observed: [universal_in_azc, other_in_azc]
    # Expected: based on A proportions
    observed = [universal_token_count, other_token_count]
    expected_universal = total_decomposed * (a_universal_pct / 100)
    expected_other = total_decomposed * (1 - a_universal_pct / 100)
    expected = [expected_universal, expected_other]

    chi2, p_value = stats.chisquare(observed, expected)

    print("Statistical Test (vs A baseline):")
    print("-" * 40)
    print(f"Chi-squared: {chi2:.2f}")
    print(f"p-value: {p_value:.6f}")

    if p_value < 0.05:
        if universal_pct > a_universal_pct:
            direction = "ENRICHED"
            constraint = "AZC enriches universal MIDDLEs relative to A baseline"
        else:
            direction = "DEPLETED"
            constraint = "AZC depletes universal MIDDLEs relative to A baseline"
    else:
        direction = "PASSTHROUGH"
        constraint = "AZC preserves A's MIDDLE universality distribution"

    print(f"Direction: {direction}")
    print()

    # Analyze MIDDLE frequency distribution
    print("Top 10 MIDDLEs in AZC:")
    print("-" * 40)
    for middle, count in middle_counts.most_common(10):
        is_universal = "UNIVERSAL" if middle in universal_middles else ""
        print(f"  '{middle}': {count} ({count/total_decomposed*100:.1f}%) {is_universal}")
    print()

    # Count unique MIDDLEs by category
    unique_universal = len([m for m in set(middle_categories['universal'])])
    unique_other = len(set(middle_categories['other']))

    print("MIDDLE Type Distribution:")
    print("-" * 40)
    print(f"Unique universal MIDDLEs used: {unique_universal} / {len(universal_middles)}")
    print(f"Unique other MIDDLEs: {unique_other}")
    print()

    # Prepare output
    output = {
        'metadata': {
            'test': '1.1',
            'question': 'MIDDLE universality in AZC',
            'total_azc_tokens': len(azc_tokens),
            'decomposed_tokens': decomposed_count,
            'decomposition_rate': decomposed_count / len(azc_tokens)
        },
        'results': {
            'universal_tokens': universal_token_count,
            'universal_pct': round(universal_pct, 2),
            'other_tokens': other_token_count,
            'other_pct': round(100 - universal_pct, 2),
            'unique_middles': len(middle_counts),
            'unique_universal_used': unique_universal,
            'unique_other_used': unique_other
        },
        'comparison_to_a': {
            'a_universal_pct': a_universal_pct,
            'azc_universal_pct': round(universal_pct, 2),
            'difference_pp': round(universal_pct - a_universal_pct, 2),
            'chi_squared': round(chi2, 2),
            'p_value': p_value,
            'direction': direction
        },
        'top_middles': [
            {
                'middle': m,
                'count': c,
                'pct': round(c / total_decomposed * 100, 2),
                'is_universal': m in universal_middles
            }
            for m, c in middle_counts.most_common(20)
        ],
        'interpretation': {
            'finding': direction,
            'possible_constraint': constraint,
            'semantic_ceiling': 'We measure filtering, not meaning'
        }
    }

    # Print interpretation
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()
    print(f"Finding: {direction}")
    print(f"Possible constraint: {constraint}")
    print()

    if direction == "ENRICHED":
        print("AZC preferentially admits universal MIDDLEs.")
        print("This suggests AZC gates legality based on material-independence.")
    elif direction == "DEPLETED":
        print("AZC filters out universal MIDDLEs.")
        print("This suggests AZC prefers material-specific recognition.")
    else:
        print("AZC acts as a passthrough for A's MIDDLE distribution.")
        print("No significant filtering detected.")

    return output


def main():
    output = analyze_middle_distribution()

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_middle_universality.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
