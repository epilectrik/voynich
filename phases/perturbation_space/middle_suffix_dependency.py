#!/usr/bin/env python3
"""
MIDDLE -> Suffix Dependency Analysis

Framing: How recognition hands off to control.
Question: Which MIDDLEs collapse to fixed decision archetypes vs which allow flexibility?

This is the final axis that genuinely deepens the internal model.
We are mapping dependencies, not naming decisions.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from math import log2

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import load_currier_a_tokens, decompose_token

# Known suffix patterns (decision archetypes)
SUFFIX_PATTERNS = {
    'y': 'terminal',
    'dy': 'terminal',
    'ey': 'terminal',
    'chy': 'terminal',
    'shy': 'terminal',
    'n': 'continuation',
    'in': 'continuation',
    'an': 'continuation',
    'r': 'redirect',
    'ir': 'redirect',
    'ar': 'redirect',
    's': 'stabilize',
    'l': 'link',
    'al': 'link',
    'ol': 'link',
    'm': 'modifier',
    'am': 'modifier',
    '': 'null'
}


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


def analyze_middle_suffix_dependency():
    """Map MIDDLE -> suffix dependencies."""

    # Load Currier A data
    tokens = load_currier_a_tokens()

    # Collect MIDDLE -> suffix mappings
    middle_suffixes = defaultdict(lambda: defaultdict(int))
    middle_tokens = defaultdict(int)

    for token in tokens:
        result = decompose_token(token)
        if result[0]:  # Has valid prefix
            prefix, middle, suffix = result
            middle_suffixes[middle][suffix] += 1
            middle_tokens[middle] += 1

    # Load material class sharing data
    sharing_path = Path(__file__).parent.parent.parent / 'results' / 'middle_class_sharing.json'
    with open(sharing_path, 'r') as f:
        sharing_data = json.load(f)

    # Build MIDDLE -> sharing category lookup
    middle_category = {}

    # Universal MIDDLEs from universal_analysis.details
    universal_details = sharing_data.get('universal_analysis', {}).get('details', [])
    for middle_info in universal_details:
        middle_category[middle_info['middle']] = 'universal'

    # For now, classify everything else as 'other' (includes bridging + exclusive)
    # We can refine this if we have explicit bridging data

    # Calculate entropy for each MIDDLE
    results = []
    for middle, suffix_counts in middle_suffixes.items():
        if middle_tokens[middle] < 5:  # Minimum threshold
            continue

        entropy = calculate_entropy(suffix_counts)
        n_suffixes = len([s for s, c in suffix_counts.items() if c > 0])
        max_entropy = log2(n_suffixes) if n_suffixes > 1 else 0

        # Dominant suffix
        dominant_suffix = max(suffix_counts.items(), key=lambda x: x[1])
        dominance_rate = dominant_suffix[1] / middle_tokens[middle]

        category = middle_category.get(middle, 'other')

        results.append({
            'middle': middle,
            'category': category,
            'total_tokens': middle_tokens[middle],
            'n_suffixes': n_suffixes,
            'entropy': entropy,
            'max_entropy': max_entropy,
            'efficiency': entropy / max_entropy if max_entropy > 0 else 0,
            'dominant_suffix': dominant_suffix[0],
            'dominance_rate': dominance_rate,
            'suffix_distribution': dict(suffix_counts)
        })

    # Sort by entropy
    results.sort(key=lambda x: x['entropy'], reverse=True)

    # Aggregate by category
    category_stats = defaultdict(lambda: {
        'count': 0,
        'total_tokens': 0,
        'entropy_sum': 0,
        'high_entropy_count': 0,  # entropy > 1.5 bits
        'rigid_count': 0  # dominance > 0.8
    })

    for r in results:
        cat = r['category']
        category_stats[cat]['count'] += 1
        category_stats[cat]['total_tokens'] += r['total_tokens']
        category_stats[cat]['entropy_sum'] += r['entropy']
        if r['entropy'] > 1.5:
            category_stats[cat]['high_entropy_count'] += 1
        if r['dominance_rate'] > 0.8:
            category_stats[cat]['rigid_count'] += 1

    # Calculate means
    for cat, stats in category_stats.items():
        if stats['count'] > 0:
            stats['mean_entropy'] = stats['entropy_sum'] / stats['count']
            stats['high_entropy_rate'] = stats['high_entropy_count'] / stats['count']
            stats['rigid_rate'] = stats['rigid_count'] / stats['count']

    # Identify decision-rigid vs decision-flexible MIDDLEs
    rigid_middles = [r for r in results if r['dominance_rate'] > 0.8]
    flexible_middles = [r for r in results if r['entropy'] > 2.0 and r['total_tokens'] >= 20]

    output = {
        'metadata': {
            'total_middles_analyzed': len(results),
            'min_token_threshold': 5,
            'framing': 'recognition -> decision handoff'
        },
        'category_summary': {
            cat: {
                'count': stats['count'],
                'mean_entropy': round(stats.get('mean_entropy', 0), 3),
                'high_entropy_rate': round(stats.get('high_entropy_rate', 0), 3),
                'rigid_rate': round(stats.get('rigid_rate', 0), 3)
            }
            for cat, stats in category_stats.items()
        },
        'decision_rigid': {
            'count': len(rigid_middles),
            'description': 'MIDDLEs that collapse to single decision (dominance > 80%)',
            'by_category': {
                'universal': len([r for r in rigid_middles if r['category'] == 'universal']),
                'other': len([r for r in rigid_middles if r['category'] == 'other'])
            },
            'top_examples': [
                {
                    'middle': r['middle'],
                    'category': r['category'],
                    'tokens': r['total_tokens'],
                    'dominant_suffix': r['dominant_suffix'],
                    'dominance': round(r['dominance_rate'], 3)
                }
                for r in sorted(rigid_middles, key=lambda x: x['total_tokens'], reverse=True)[:10]
            ]
        },
        'decision_flexible': {
            'count': len(flexible_middles),
            'description': 'MIDDLEs with high suffix entropy (>2.0 bits, N>=20)',
            'by_category': {
                'universal': len([r for r in flexible_middles if r['category'] == 'universal']),
                'other': len([r for r in flexible_middles if r['category'] == 'other'])
            },
            'examples': [
                {
                    'middle': r['middle'],
                    'category': r['category'],
                    'tokens': r['total_tokens'],
                    'entropy': round(r['entropy'], 3),
                    'n_suffixes': r['n_suffixes']
                }
                for r in flexible_middles[:10]
            ]
        },
        'interpretation': {
            'framing': 'How recognition hands off to control',
            'finding': None,  # Will be filled after analysis
            'semantic_ceiling': 'We map dependencies, not meanings'
        }
    }

    # Generate interpretation
    universal_stats = category_stats.get('universal', {})
    other_stats = category_stats.get('other', {})

    if universal_stats.get('mean_entropy', 0) > other_stats.get('mean_entropy', 0):
        output['interpretation']['finding'] = (
            'Universal MIDDLEs have HIGHER suffix entropy than other MIDDLEs. '
            'Recognition points shared across material classes hand off to MORE decision options.'
        )
    else:
        output['interpretation']['finding'] = (
            'Universal MIDDLEs have LOWER or EQUAL suffix entropy to other MIDDLEs. '
            'Material class sharing does not predict decision flexibility.'
        )

    return output, results


def main():
    print("=" * 60)
    print("MIDDLE -> Suffix Dependency Analysis")
    print("Framing: How recognition hands off to control")
    print("=" * 60)
    print()

    output, details = analyze_middle_suffix_dependency()

    # Print summary
    print("Category Summary:")
    print("-" * 40)
    for cat, stats in output['category_summary'].items():
        print(f"  {cat}:")
        print(f"    Count: {stats['count']}")
        print(f"    Mean entropy: {stats['mean_entropy']:.3f} bits")
        print(f"    High-entropy rate: {stats['high_entropy_rate']:.1%}")
        print(f"    Rigid rate: {stats['rigid_rate']:.1%}")
        print()

    print("Decision-Rigid MIDDLEs (collapse to single decision):")
    print("-" * 40)
    print(f"  Total: {output['decision_rigid']['count']}")
    print(f"  By category: {output['decision_rigid']['by_category']}")
    print()

    print("Decision-Flexible MIDDLEs (multiple decision options):")
    print("-" * 40)
    print(f"  Total: {output['decision_flexible']['count']}")
    print(f"  By category: {output['decision_flexible']['by_category']}")
    print()

    print("Interpretation:")
    print("-" * 40)
    print(f"  {output['interpretation']['finding']}")
    print()
    print(f"  Semantic ceiling: {output['interpretation']['semantic_ceiling']}")

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'middle_suffix_dependency.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == '__main__':
    main()
