#!/usr/bin/env python3
"""
AZC Constraint Hunt - Test 1.2: Suffix Entropy by AZC Placement

Question: Does AZC placement constrain which decision archetypes are legal?

Baseline (from Currier A):
- Universal MIDDLE suffix entropy: 2.371 bits
- Other MIDDLE suffix entropy: 1.382 bits

Possible Constraints:
- "Interior placements (R-series) permit higher suffix entropy"
- "Boundary placements (S-series) constrain to rigid suffixes"
- "Placement code gates decision archetype availability"
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from math import log2
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token


def load_azc_tokens_with_placement():
    """Load all AZC tokens with placement information."""
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
                    if token and placement:
                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'placement': placement
                        })
    return tokens


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


def aggregate_placement(placement):
    """Aggregate placement codes into families."""
    if placement.startswith('R'):
        return 'R-series'
    elif placement.startswith('S'):
        return 'S-series'
    elif placement in ['C', 'P']:
        return placement
    else:
        return 'OTHER'


def analyze_suffix_entropy():
    """Analyze suffix entropy by AZC placement."""

    print("=" * 60)
    print("AZC Constraint Hunt - Test 1.2: Suffix Entropy by Placement")
    print("=" * 60)
    print()

    # Load data
    azc_tokens = load_azc_tokens_with_placement()

    print(f"AZC tokens loaded: {len(azc_tokens)}")
    print()

    # Group by placement and collect suffixes
    placement_suffixes = defaultdict(list)
    placement_middles = defaultdict(lambda: defaultdict(list))  # placement -> middle -> [suffixes]
    placement_counts = Counter()

    for item in azc_tokens:
        token = item['token']
        placement = item['placement']
        result = decompose_token(token)

        if result[0]:  # Has valid prefix
            prefix, middle, suffix = result
            placement_suffixes[placement].append(suffix)
            placement_middles[placement][middle].append(suffix)
            placement_counts[placement] += 1

    print("Placement Distribution:")
    print("-" * 40)
    for placement, count in sorted(placement_counts.items(), key=lambda x: -x[1]):
        print(f"  {placement}: {count} tokens")
    print()

    # Calculate suffix entropy per placement (overall)
    placement_entropy = {}
    for placement, suffixes in placement_suffixes.items():
        suffix_counts = Counter(suffixes)
        entropy = calculate_entropy(suffix_counts)
        n_unique = len(suffix_counts)
        placement_entropy[placement] = {
            'entropy': entropy,
            'n_tokens': len(suffixes),
            'n_unique_suffixes': n_unique,
            'top_suffixes': suffix_counts.most_common(5)
        }

    print("Suffix Entropy by Placement:")
    print("-" * 40)
    print(f"{'Placement':<10} {'N':>6} {'Entropy':>8} {'Unique':>8}")
    print("-" * 40)
    for placement in sorted(placement_entropy.keys()):
        data = placement_entropy[placement]
        print(f"{placement:<10} {data['n_tokens']:>6} {data['entropy']:>8.3f} {data['n_unique_suffixes']:>8}")
    print()

    # Calculate MIDDLE->suffix entropy per placement (more fine-grained)
    print("MIDDLE->Suffix Entropy by Placement (aggregated):")
    print("-" * 40)

    # Aggregate by placement family
    family_middle_entropy = defaultdict(list)
    family_token_count = defaultdict(int)

    for placement, middle_data in placement_middles.items():
        family = aggregate_placement(placement)
        for middle, suffixes in middle_data.items():
            if len(suffixes) >= 3:  # Minimum threshold
                suffix_counts = Counter(suffixes)
                entropy = calculate_entropy(suffix_counts)
                family_middle_entropy[family].append(entropy)
        family_token_count[family] += placement_counts[placement]

    family_stats = {}
    for family in ['C', 'P', 'R-series', 'S-series', 'OTHER']:
        if family in family_middle_entropy:
            entropies = family_middle_entropy[family]
            if entropies:
                mean_ent = sum(entropies) / len(entropies)
                family_stats[family] = {
                    'mean_entropy': mean_ent,
                    'n_middles': len(entropies),
                    'n_tokens': family_token_count[family]
                }

    print(f"{'Family':<12} {'N Tokens':>10} {'N MIDDLEs':>10} {'Mean Entropy':>12}")
    print("-" * 50)
    for family in ['C', 'P', 'R-series', 'S-series', 'OTHER']:
        if family in family_stats:
            s = family_stats[family]
            print(f"{family:<12} {s['n_tokens']:>10} {s['n_middles']:>10} {s['mean_entropy']:>12.3f}")
    print()

    # Compare baselines
    print("Comparison to A baseline:")
    print("-" * 40)
    print(f"  A universal MIDDLE entropy: 2.371 bits")
    print(f"  A other MIDDLE entropy: 1.382 bits")
    print()

    # Statistical test: Kruskal-Wallis for entropy differences across families
    groups = []
    labels = []
    for family in ['C', 'P', 'R-series', 'S-series']:
        if family in family_middle_entropy:
            groups.append(family_middle_entropy[family])
            labels.append(family)

    if len(groups) >= 2:
        h_stat, kw_p_value = stats.kruskal(*groups)
        print("Kruskal-Wallis Test (entropy across placement families):")
        print(f"  H-statistic: {h_stat:.2f}")
        print(f"  p-value: {kw_p_value:.6f}")

        if kw_p_value < 0.05:
            print("  Result: SIGNIFICANT - Placement family affects suffix entropy")
        else:
            print("  Result: NOT SIGNIFICANT - Uniform entropy across placements")
    print()

    # Prepare output
    output = {
        'metadata': {
            'test': '1.2',
            'question': 'Suffix entropy by AZC placement',
            'total_tokens': len(azc_tokens)
        },
        'placement_distribution': dict(placement_counts),
        'placement_entropy': {
            p: {
                'entropy': round(v['entropy'], 3),
                'n_tokens': v['n_tokens'],
                'n_unique_suffixes': v['n_unique_suffixes'],
                'top_suffixes': [(s, c) for s, c in v['top_suffixes']]
            }
            for p, v in placement_entropy.items()
        },
        'family_stats': {
            f: {
                'mean_entropy': round(s['mean_entropy'], 3),
                'n_middles': s['n_middles'],
                'n_tokens': s['n_tokens']
            }
            for f, s in family_stats.items()
        },
        'statistical_test': {
            'test': 'Kruskal-Wallis',
            'h_statistic': round(float(h_stat), 2) if len(groups) >= 2 else None,
            'p_value': float(kw_p_value) if len(groups) >= 2 else None,
            'significant': bool(kw_p_value < 0.05) if len(groups) >= 2 else None
        },
        'comparison_to_a': {
            'a_universal_entropy': 2.371,
            'a_other_entropy': 1.382
        },
        'interpretation': {
            'finding': None,
            'possible_constraint': None,
            'semantic_ceiling': 'We measure decision space, not decision content'
        }
    }

    # Determine interpretation
    if len(groups) >= 2 and kw_p_value < 0.05:
        # Find direction
        r_entropy = family_stats.get('R-series', {}).get('mean_entropy', 0)
        s_entropy = family_stats.get('S-series', {}).get('mean_entropy', 0)

        if r_entropy > s_entropy:
            output['interpretation']['finding'] = "R-series has higher entropy than S-series"
            output['interpretation']['possible_constraint'] = "Interior placements (R-series) permit wider decision space than boundary placements (S-series)"
        else:
            output['interpretation']['finding'] = "S-series has higher or equal entropy to R-series"
            output['interpretation']['possible_constraint'] = "Boundary placements do not constrain decision space"
    else:
        output['interpretation']['finding'] = "No significant entropy difference across placements"
        output['interpretation']['possible_constraint'] = "Placement does not gate decision archetype availability"

    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()
    print(f"Finding: {output['interpretation']['finding']}")
    print(f"Possible constraint: {output['interpretation']['possible_constraint']}")

    return output


def main():
    output = analyze_suffix_entropy()

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_suffix_entropy.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
