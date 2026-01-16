#!/usr/bin/env python3
"""
AZC Constraint Hunt - Test 1.4: Prefix Distribution Compatibility

Question: Does AZC use the same prefix classes as A, or a filtered subset?

Expected (from NOTE-01):
- qo-prefix depleted in AZC (6.5% vs 18% in A)

Possible Constraints:
- "High-hazard prefixes (qo-family) are depleted in AZC"
- "AZC prefix profile matches A's M-C/M-D classes (low-hazard)"
- "Placement × prefix interaction exists"
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token, PREFIXES

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


def load_tokens_by_system():
    """Load tokens for both Currier A and AZC."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    a_tokens = []
    azc_tokens = []

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
                token = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip()
                placement = parts[10].strip('"').strip() if len(parts) > 10 else ''

                if not token:
                    continue

                if currier == 'A':
                    a_tokens.append({'token': token, 'folio': folio})
                elif currier == 'NA':  # AZC
                    azc_tokens.append({'token': token, 'folio': folio, 'placement': placement})

    return a_tokens, azc_tokens


def analyze_prefix_distribution():
    """Analyze prefix distribution in AZC vs A."""

    print("=" * 60)
    print("AZC Constraint Hunt - Test 1.4: Prefix Distribution")
    print("=" * 60)
    print()

    # Load data
    a_tokens, azc_tokens = load_tokens_by_system()

    print(f"Currier A tokens: {len(a_tokens)}")
    print(f"AZC tokens: {len(azc_tokens)}")
    print()

    # Count prefixes
    a_prefix_counts = Counter()
    azc_prefix_counts = Counter()
    azc_family_prefix = {
        'zodiac': Counter(),
        'ac': Counter()
    }

    a_decomposed = 0
    azc_decomposed = 0

    for item in a_tokens:
        result = decompose_token(item['token'])
        if result[0]:
            a_prefix_counts[result[0]] += 1
            a_decomposed += 1

    for item in azc_tokens:
        result = decompose_token(item['token'])
        if result[0]:
            azc_prefix_counts[result[0]] += 1
            azc_decomposed += 1

            if item['folio'] in ZODIAC_FAMILY:
                azc_family_prefix['zodiac'][result[0]] += 1
            elif item['folio'] in AC_FAMILY:
                azc_family_prefix['ac'][result[0]] += 1

    print(f"A decomposed: {a_decomposed}")
    print(f"AZC decomposed: {azc_decomposed}")
    print()

    # Calculate proportions
    print("Prefix Distribution Comparison:")
    print("-" * 60)
    print(f"{'Prefix':<8} {'A Count':>10} {'A %':>8} {'AZC Count':>10} {'AZC %':>8} {'Ratio':>8}")
    print("-" * 60)

    prefix_comparison = []
    for prefix in sorted(set(list(a_prefix_counts.keys()) + list(azc_prefix_counts.keys()))):
        a_count = a_prefix_counts.get(prefix, 0)
        azc_count = azc_prefix_counts.get(prefix, 0)
        a_pct = a_count / a_decomposed * 100 if a_decomposed > 0 else 0
        azc_pct = azc_count / azc_decomposed * 100 if azc_decomposed > 0 else 0
        ratio = azc_pct / a_pct if a_pct > 0 else float('inf')

        print(f"{prefix:<8} {a_count:>10} {a_pct:>7.1f}% {azc_count:>10} {azc_pct:>7.1f}% {ratio:>7.2f}x")

        prefix_comparison.append({
            'prefix': prefix,
            'a_count': a_count,
            'a_pct': a_pct,
            'azc_count': azc_count,
            'azc_pct': azc_pct,
            'ratio': ratio
        })
    print()

    # Focus on qo-prefix (expected depletion)
    qo_a = a_prefix_counts.get('qo', 0)
    qo_azc = azc_prefix_counts.get('qo', 0)
    qo_a_pct = qo_a / a_decomposed * 100
    qo_azc_pct = qo_azc / azc_decomposed * 100

    print("qo-Prefix Analysis (Expected: Depleted in AZC):")
    print("-" * 40)
    print(f"  A: {qo_a} ({qo_a_pct:.2f}%)")
    print(f"  AZC: {qo_azc} ({qo_azc_pct:.2f}%)")
    print(f"  Depletion: {qo_a_pct - qo_azc_pct:.2f} percentage points")
    print(f"  Ratio: {qo_azc_pct / qo_a_pct:.2f}x" if qo_a_pct > 0 else "  Ratio: N/A")
    print()

    # Chi-squared test for overall distribution difference
    # Aggregate to avoid zero cells
    prefixes_both = [p for p in a_prefix_counts if p in azc_prefix_counts]
    if len(prefixes_both) >= 2:
        a_obs = [a_prefix_counts[p] for p in prefixes_both]
        azc_obs = [azc_prefix_counts[p] for p in prefixes_both]

        # Scale A to AZC total for comparison
        a_scaled = [c * azc_decomposed / a_decomposed for c in a_obs]

        chi2, p_value = stats.chisquare(azc_obs, a_scaled)

        print("Chi-squared Test (AZC vs A distribution):")
        print(f"  Chi-squared: {chi2:.2f}")
        print(f"  p-value: {p_value:.10f}")
        print(f"  Result: {'SIGNIFICANT - Distributions differ' if p_value < 0.05 else 'NOT SIGNIFICANT'}")
        print()

    # Binomial test for qo specifically
    if qo_a_pct > 0:
        binom_result = stats.binomtest(qo_azc, azc_decomposed, p=qo_a_pct/100)
        print(f"Binomial Test (qo in AZC vs A rate {qo_a_pct:.2f}%):")
        print(f"  p-value: {binom_result.pvalue:.10f}")
        print(f"  Result: {'SIGNIFICANT - qo is depleted' if binom_result.pvalue < 0.05 and qo_azc_pct < qo_a_pct else 'NOT SIGNIFICANT'}")
        print()

    # Family comparison
    print("Prefix Distribution by AZC Family:")
    print("-" * 50)
    zodiac_total = sum(azc_family_prefix['zodiac'].values())
    ac_total = sum(azc_family_prefix['ac'].values())

    print(f"{'Prefix':<8} {'Zodiac %':>10} {'A/C %':>10}")
    print("-" * 30)
    for prefix in ['qo', 'ch', 'sh', 'ok', 'ot', 'da', 'ol', 'ct']:
        z_pct = azc_family_prefix['zodiac'].get(prefix, 0) / zodiac_total * 100 if zodiac_total > 0 else 0
        ac_pct = azc_family_prefix['ac'].get(prefix, 0) / ac_total * 100 if ac_total > 0 else 0
        print(f"{prefix:<8} {z_pct:>9.1f}% {ac_pct:>9.1f}%")
    print()

    # Prepare output
    output = {
        'metadata': {
            'test': '1.4',
            'question': 'Prefix distribution compatibility',
            'a_decomposed': a_decomposed,
            'azc_decomposed': azc_decomposed
        },
        'prefix_comparison': [
            {
                'prefix': p['prefix'],
                'a_count': p['a_count'],
                'a_pct': round(p['a_pct'], 2),
                'azc_count': p['azc_count'],
                'azc_pct': round(p['azc_pct'], 2),
                'ratio': round(p['ratio'], 3) if p['ratio'] != float('inf') else None
            }
            for p in prefix_comparison
        ],
        'qo_analysis': {
            'a_count': qo_a,
            'a_pct': round(qo_a_pct, 2),
            'azc_count': qo_azc,
            'azc_pct': round(qo_azc_pct, 2),
            'depletion_pp': round(qo_a_pct - qo_azc_pct, 2),
            'ratio': round(qo_azc_pct / qo_a_pct, 3) if qo_a_pct > 0 else None,
            'binomial_p': float(binom_result.pvalue) if qo_a_pct > 0 else None,
            'depleted': bool(binom_result.pvalue < 0.05 and qo_azc_pct < qo_a_pct) if qo_a_pct > 0 else False
        },
        'chi_squared_test': {
            'chi_squared': round(float(chi2), 2) if len(prefixes_both) >= 2 else None,
            'p_value': float(p_value) if len(prefixes_both) >= 2 else None,
            'significant': bool(p_value < 0.05) if len(prefixes_both) >= 2 else None
        },
        'family_distribution': {
            'zodiac': {p: round(c / zodiac_total * 100, 2) if zodiac_total > 0 else 0 for p, c in azc_family_prefix['zodiac'].items()},
            'ac': {p: round(c / ac_total * 100, 2) if ac_total > 0 else 0 for p, c in azc_family_prefix['ac'].items()}
        },
        'interpretation': {
            'finding': None,
            'possible_constraint': None,
            'semantic_ceiling': 'We measure prefix filtering, not prefix meaning'
        }
    }

    # Determine interpretation
    if qo_a_pct > 0 and binom_result.pvalue < 0.05 and qo_azc_pct < qo_a_pct:
        output['interpretation']['finding'] = f"qo-prefix depleted: {qo_azc_pct:.1f}% in AZC vs {qo_a_pct:.1f}% in A"
        output['interpretation']['possible_constraint'] = "AZC filters high-hazard qo-prefix; may prefer low-hazard material classes"
    else:
        output['interpretation']['finding'] = "No significant qo-prefix depletion"
        output['interpretation']['possible_constraint'] = "AZC does not filter by prefix hazard class"

    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()
    print(f"Finding: {output['interpretation']['finding']}")
    print(f"Possible constraint: {output['interpretation']['possible_constraint']}")

    return output


def main():
    output = analyze_prefix_distribution()

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_prefix_distribution.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
