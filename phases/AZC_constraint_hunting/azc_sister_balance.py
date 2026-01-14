#!/usr/bin/env python3
"""
AZC Constraint Hunt - Test 1.3: Sister Balance by AZC Family

Question: Do Zodiac and A/C families show different sister-pair preferences?

Baseline (from Currier A):
- Universal MIDDLE sister preference: 51.0% precision (balanced)
- Exclusive MIDDLE sister preference: 87.3% precision (biased)

Possible Constraints:
- "Zodiac family shows mode-balanced sister preferences"
- "A/C family shows precision-biased preferences"
- "AZC inherits A's universal mode-balance pattern"
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token

# AZC family assignments (from azc_folio_clusters.json)
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

# Sister pairs
SISTER_PAIRS = [
    ('ch', 'sh'),
    ('che', 'she'),
    ('cho', 'sho'),
    ('cha', 'sha'),
    ('cth', 'sth'),
    ('ckh', 'skh'),
]


def load_azc_tokens():
    """Load all AZC tokens with folio information."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                currier = parts[6].strip('"').strip()
                if currier == 'NA':  # AZC tokens
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip()
                    if token:
                        tokens.append({
                            'token': token,
                            'folio': folio
                        })
    return tokens


def identify_sister_class(token):
    """Identify if token belongs to ch-family (precision) or sh-family (tolerance)."""
    # Check for ch-family prefixes
    ch_prefixes = ['ch', 'cth', 'ckh', 'ct']
    # Check for sh-family prefixes
    sh_prefixes = ['sh', 'sth', 'skh']

    token_lower = token.lower()

    for prefix in ch_prefixes:
        if token_lower.startswith(prefix):
            return 'precision'

    for prefix in sh_prefixes:
        if token_lower.startswith(prefix):
            return 'tolerance'

    return None


def analyze_sister_balance():
    """Analyze sister-pair balance by AZC family."""

    print("=" * 60)
    print("AZC Constraint Hunt - Test 1.3: Sister Balance by Family")
    print("=" * 60)
    print()

    # Load data
    azc_tokens = load_azc_tokens()

    print(f"AZC tokens loaded: {len(azc_tokens)}")
    print()

    # Classify tokens by family and sister class
    family_sister_counts = {
        'zodiac': {'precision': 0, 'tolerance': 0},
        'ac': {'precision': 0, 'tolerance': 0}
    }

    for item in azc_tokens:
        token = item['token']
        folio = item['folio']

        sister_class = identify_sister_class(token)
        if sister_class is None:
            continue

        if folio in ZODIAC_FAMILY:
            family_sister_counts['zodiac'][sister_class] += 1
        elif folio in AC_FAMILY:
            family_sister_counts['ac'][sister_class] += 1

    # Calculate proportions
    results = {}
    for family, counts in family_sister_counts.items():
        total = counts['precision'] + counts['tolerance']
        if total > 0:
            precision_pct = counts['precision'] / total * 100
            results[family] = {
                'precision': counts['precision'],
                'tolerance': counts['tolerance'],
                'total': total,
                'precision_pct': precision_pct
            }

    print("Results by Family:")
    print("-" * 50)
    print(f"{'Family':<15} {'Precision':>10} {'Tolerance':>10} {'Total':>8} {'Prec%':>8}")
    print("-" * 50)
    for family, r in results.items():
        print(f"{family:<15} {r['precision']:>10} {r['tolerance']:>10} {r['total']:>8} {r['precision_pct']:>7.1f}%")
    print()

    # Baseline comparison
    print("Comparison to A baseline:")
    print("-" * 40)
    print("  A universal MIDDLE: 51.0% precision (balanced)")
    print("  A exclusive MIDDLE: 87.3% precision (biased)")
    print()

    # Statistical test: chi-squared for family × sister association
    if 'zodiac' in results and 'ac' in results:
        contingency = [
            [results['zodiac']['precision'], results['zodiac']['tolerance']],
            [results['ac']['precision'], results['ac']['tolerance']]
        ]

        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

        print("Chi-squared Test (family × sister association):")
        print(f"  Chi-squared: {chi2:.2f}")
        print(f"  p-value: {p_value:.6f}")
        print(f"  Degrees of freedom: {dof}")

        if p_value < 0.05:
            print("  Result: SIGNIFICANT - Family affects sister preference")
            if results['zodiac']['precision_pct'] < results['ac']['precision_pct']:
                direction = "Zodiac is more mode-balanced than A/C"
            else:
                direction = "A/C is more mode-balanced than Zodiac"
        else:
            print("  Result: NOT SIGNIFICANT - No family effect")
            direction = "Both families have similar sister balance"
        print()

    # Test against A baseline (51% = balanced)
    print("Test against 51% balanced baseline:")
    print("-" * 40)
    for family, r in results.items():
        # Binomial test: is this significantly different from 51%?
        binom_result = stats.binomtest(r['precision'], r['total'], p=0.51)
        sig = "***" if binom_result.pvalue < 0.001 else "**" if binom_result.pvalue < 0.01 else "*" if binom_result.pvalue < 0.05 else ""
        print(f"  {family}: {r['precision_pct']:.1f}% (p={binom_result.pvalue:.4f}) {sig}")
    print()

    # Prepare output
    output = {
        'metadata': {
            'test': '1.3',
            'question': 'Sister balance by AZC family',
            'zodiac_folios': len(ZODIAC_FAMILY),
            'ac_folios': len(AC_FAMILY)
        },
        'family_results': {
            f: {
                'precision_count': r['precision'],
                'tolerance_count': r['tolerance'],
                'total': r['total'],
                'precision_pct': round(r['precision_pct'], 2)
            }
            for f, r in results.items()
        },
        'chi_squared_test': {
            'chi_squared': round(float(chi2), 2) if 'zodiac' in results and 'ac' in results else None,
            'p_value': float(p_value) if 'zodiac' in results and 'ac' in results else None,
            'significant': bool(p_value < 0.05) if 'zodiac' in results and 'ac' in results else None,
            'direction': direction if 'zodiac' in results and 'ac' in results else None
        },
        'comparison_to_a': {
            'a_universal_precision': 51.0,
            'a_exclusive_precision': 87.3
        },
        'interpretation': {
            'finding': None,
            'possible_constraint': None,
            'semantic_ceiling': 'We measure mode balance, not mode meaning'
        }
    }

    # Determine interpretation
    if 'zodiac' in results and 'ac' in results:
        zodiac_balance = abs(results['zodiac']['precision_pct'] - 50)
        ac_balance = abs(results['ac']['precision_pct'] - 50)

        if p_value < 0.05:
            if zodiac_balance < ac_balance:
                output['interpretation']['finding'] = f"Zodiac more balanced ({results['zodiac']['precision_pct']:.1f}%) than A/C ({results['ac']['precision_pct']:.1f}%)"
                output['interpretation']['possible_constraint'] = "Zodiac family maintains mode balance; A/C family shows mode bias"
            else:
                output['interpretation']['finding'] = f"A/C more balanced ({results['ac']['precision_pct']:.1f}%) than Zodiac ({results['zodiac']['precision_pct']:.1f}%)"
                output['interpretation']['possible_constraint'] = "A/C family maintains mode balance; Zodiac family shows mode bias"
        else:
            output['interpretation']['finding'] = f"Both families similar: Zodiac={results['zodiac']['precision_pct']:.1f}%, A/C={results['ac']['precision_pct']:.1f}%"
            output['interpretation']['possible_constraint'] = "AZC does not differentiate families by sister balance"

    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()
    print(f"Finding: {output['interpretation']['finding']}")
    print(f"Possible constraint: {output['interpretation']['possible_constraint']}")

    return output


def main():
    output = analyze_sister_balance()

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_sister_balance.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
