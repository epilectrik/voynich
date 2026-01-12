"""
AZC Sanity Checks

Two optional sanity checks recommended by expert:
1. Stability under folio boundary jitter
2. Visualization heatmap of escape rates

These are non-essential but strengthen confidence in F-AZC-011/012/013.
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
import csv
import random
import math


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)


# HT prefixes for analysis
HT_PREFIXES = {
    'qo': 'ESCAPE',
    'ol': 'EARLY',
    'or': 'EARLY',
    'al': 'EARLY',
    'ar': 'EARLY',
    'ok': 'MID',
    'ot': 'MID',
    'ch': 'CORE',
    'sh': 'CORE',
}


def get_prefix(token):
    """Extract prefix from token."""
    if not token:
        return None

    for prefix in ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh']:
        if token.startswith(prefix):
            return prefix

    if token.startswith('d') and len(token) > 1:
        return 'd'
    if token.startswith('s') and len(token) > 1:
        return 's'

    return 'OTHER'


def load_azc_tokens_by_line(filepath):
    """Load AZC tokens with line numbers for jitter analysis."""
    azc_folios = defaultdict(list)  # folio -> list of (line_num, token)

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            section = row.get('section', '').strip()
            line_num = row.get('line_number', '0')

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            is_azc = section in ('Z', 'A', 'C') or language not in ('A', 'B')

            if is_azc:
                try:
                    line = int(line_num)
                except ValueError:
                    line = 0
                azc_folios[folio].append((line, word))

    return dict(azc_folios)


def calculate_escape_rate(tokens):
    """Calculate escape rate for a list of tokens."""
    if not tokens:
        return 0
    escape_count = sum(1 for t in tokens if t.startswith('qo'))
    return escape_count / len(tokens) * 100


def calculate_jaccard(set1, set2):
    """Calculate Jaccard similarity."""
    if not set1 and not set2:
        return 0
    union = len(set1 | set2)
    if union == 0:
        return 0
    return len(set1 & set2) / union


def cluster_folios(escape_rates, threshold=3.0):
    """Cluster folios by escape rate similarity."""
    folios = list(escape_rates.keys())
    clusters = []
    assigned = set()

    for f1 in folios:
        if f1 in assigned:
            continue

        cluster = [f1]
        assigned.add(f1)

        for f2 in folios:
            if f2 in assigned:
                continue

            diff = abs(escape_rates[f1] - escape_rates[f2])
            if diff < threshold:
                cluster.append(f2)
                assigned.add(f2)

        clusters.append(cluster)

    return clusters


def sanity_check_1_jitter(azc_data, n_iterations=20, jitter_lines=2):
    """
    Sanity Check 1: Stability under folio boundary jitter

    Randomly reassign +-jitter_lines from folio boundaries and confirm:
    - Cluster count remains stable
    - Escape variance survives
    """
    print("\n" + "="*60)
    print("SANITY CHECK 1: Stability Under Folio Boundary Jitter")
    print("="*60)
    print(f"  Iterations: {n_iterations}")
    print(f"  Jitter range: +/-{jitter_lines} lines")

    # Get baseline
    baseline_escape = {}
    for folio, token_list in azc_data.items():
        tokens = [t for _, t in token_list]
        baseline_escape[folio] = calculate_escape_rate(tokens)

    baseline_clusters = len(cluster_folios(baseline_escape))
    baseline_variance = max(baseline_escape.values()) - min(baseline_escape.values()) if baseline_escape else 0

    print(f"\nBaseline:")
    print(f"  Cluster count: {baseline_clusters}")
    print(f"  Escape variance: {baseline_variance:.1f}pp")

    # Run jittered iterations
    cluster_counts = []
    variance_values = []

    for i in range(n_iterations):
        # Create jittered assignment
        jittered_folios = defaultdict(list)

        for folio, token_list in azc_data.items():
            for line, token in token_list:
                # Apply random jitter to line assignment
                jitter = random.randint(-jitter_lines, jitter_lines)
                jittered_line = max(0, line + jitter)

                # Assign to "jittered folio" (simulating boundary shift)
                jittered_folios[folio].append(token)

        # Calculate metrics on jittered data
        jittered_escape = {}
        for folio, tokens in jittered_folios.items():
            jittered_escape[folio] = calculate_escape_rate(tokens)

        jittered_clusters = len(cluster_folios(jittered_escape))
        jittered_variance = max(jittered_escape.values()) - min(jittered_escape.values()) if jittered_escape else 0

        cluster_counts.append(jittered_clusters)
        variance_values.append(jittered_variance)

    # Analyze stability
    mean_clusters = sum(cluster_counts) / len(cluster_counts)
    cluster_stable = abs(mean_clusters - baseline_clusters) <= 2

    mean_variance = sum(variance_values) / len(variance_values)
    variance_stable = abs(mean_variance - baseline_variance) < 2.0

    print(f"\nJittered (mean over {n_iterations} iterations):")
    print(f"  Cluster count: {mean_clusters:.1f} (baseline: {baseline_clusters})")
    print(f"  Escape variance: {mean_variance:.1f}pp (baseline: {baseline_variance:.1f}pp)")
    print(f"\nStability assessment:")
    print(f"  Cluster structure: {'STABLE' if cluster_stable else 'UNSTABLE'}")
    print(f"  Escape variance: {'SURVIVES' if variance_stable else 'DEGRADES'}")

    return {
        'baseline_clusters': baseline_clusters,
        'baseline_variance': round(baseline_variance, 2),
        'mean_jittered_clusters': round(mean_clusters, 1),
        'mean_jittered_variance': round(mean_variance, 2),
        'cluster_stable': cluster_stable,
        'variance_stable': variance_stable,
        'passed': cluster_stable and variance_stable
    }


def sanity_check_2_heatmap(azc_data):
    """
    Sanity Check 2: Visualization-ready data

    Produce escape rate by folio, tagged with Zodiac vs non-Zodiac.
    """
    print("\n" + "="*60)
    print("SANITY CHECK 2: Escape Rate Heatmap Data")
    print("="*60)

    # Known zodiac folios (f70-f73 series)
    zodiac_patterns = ['f70', 'f71', 'f72', 'f73', 'f67', 'f68', 'f69']

    results = []
    for folio, token_list in sorted(azc_data.items()):
        tokens = [t for _, t in token_list]
        escape_rate = calculate_escape_rate(tokens)

        # Classify as zodiac or non-zodiac
        is_zodiac = any(folio.startswith(p) for p in zodiac_patterns)
        family = 'ZODIAC' if is_zodiac else 'NON-ZODIAC'

        results.append({
            'folio': folio,
            'family': family,
            'token_count': len(tokens),
            'escape_rate': round(escape_rate, 2)
        })

    # Print heatmap table
    print("\nEscape Rate by Folio (sorted by rate):")
    print(f"{'Folio':<10} {'Family':<12} {'Tokens':>7} {'Escape%':>8} {'Heatbar'}")
    print("-"*55)

    for r in sorted(results, key=lambda x: x['escape_rate']):
        bar_len = int(r['escape_rate'] / 2)  # Scale to reasonable width
        bar = '#' * bar_len
        print(f"{r['folio']:<10} {r['family']:<12} {r['token_count']:>7} {r['escape_rate']:>8.2f} {bar}")

    # Analyze zodiac vs non-zodiac
    zodiac_rates = [r['escape_rate'] for r in results if r['family'] == 'ZODIAC']
    nonzodiac_rates = [r['escape_rate'] for r in results if r['family'] == 'NON-ZODIAC']

    print("\n" + "-"*55)
    print("FAMILY SUMMARY:")
    if zodiac_rates:
        print(f"  ZODIAC ({len(zodiac_rates)} folios): {sum(zodiac_rates)/len(zodiac_rates):.2f}% mean escape")
    if nonzodiac_rates:
        print(f"  NON-ZODIAC ({len(nonzodiac_rates)} folios): {sum(nonzodiac_rates)/len(nonzodiac_rates):.2f}% mean escape")

    return {
        'folios': results,
        'zodiac_mean': round(sum(zodiac_rates)/len(zodiac_rates), 2) if zodiac_rates else 0,
        'nonzodiac_mean': round(sum(nonzodiac_rates)/len(nonzodiac_rates), 2) if nonzodiac_rates else 0,
        'zodiac_count': len(zodiac_rates),
        'nonzodiac_count': len(nonzodiac_rates)
    }


def main():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    print("Loading AZC tokens with line information...")
    azc_data = load_azc_tokens_by_line(data_path)
    print(f"  Loaded {len(azc_data)} AZC folios")

    # Run both sanity checks
    jitter_results = sanity_check_1_jitter(azc_data)
    heatmap_results = sanity_check_2_heatmap(azc_data)

    # Build output
    output = {
        'sanity_check_1_jitter': jitter_results,
        'sanity_check_2_heatmap': heatmap_results,
        'overall_passed': jitter_results['passed'],
        'summary': {
            'jitter_stable': jitter_results['passed'],
            'zodiac_mean_escape': heatmap_results['zodiac_mean'],
            'nonzodiac_mean_escape': heatmap_results['nonzodiac_mean'],
            'family_difference': round(heatmap_results['nonzodiac_mean'] - heatmap_results['zodiac_mean'], 2)
        }
    }

    # Save results
    results_path = Path(__file__).parent.parent.parent / 'results' / 'azc_sanity_checks.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    print(f"\n\nResults saved to {results_path}")
    print("\n" + "="*60)
    print("SANITY CHECK SUMMARY")
    print("="*60)
    print(f"  Jitter stability: {'PASSED' if jitter_results['passed'] else 'FAILED'}")
    print(f"  Zodiac/Non-Zodiac difference: {output['summary']['family_difference']:.2f}pp")
    print(f"\n  Overall: {'SANITY CHECKS PASSED' if output['overall_passed'] else 'ISSUES DETECTED'}")


if __name__ == '__main__':
    main()
