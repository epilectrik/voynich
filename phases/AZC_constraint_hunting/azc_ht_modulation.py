"""
F-AZC-013: HT Modulation by AZC Folio Identity

Question: Do different AZC folios correspond to different HT decay profiles?

This is descriptive only - not causal. We're checking whether AZC folio identity
correlates with HT characteristics (prefix distribution, escape rates, etc.)

Method:
1. For each AZC folio, calculate HT-relevant metrics:
   - Prefix distribution (which HT prefixes appear)
   - Escape rate (qo- prefix frequency)
   - Terminal patterns
2. Compare profiles across folios
3. Look for clustering or systematic variation
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
import csv
import math


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)


# Known HT-relevant prefixes
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
    'd': 'DENSE',
    's': 'SIGNAL'
}


def get_prefix(token):
    """Extract prefix from token."""
    if not token:
        return None

    # Check known prefixes in order of specificity
    for prefix in ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh']:
        if token.startswith(prefix):
            return prefix

    if token.startswith('d') and len(token) > 1:
        return 'd'
    if token.startswith('s') and len(token) > 1:
        return 's'

    return 'OTHER'


def load_azc_tokens_by_folio(filepath):
    """Load AZC tokens grouped by folio."""
    azc_folios = defaultdict(list)

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            section = row.get('section', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            is_azc = section in ('Z', 'A', 'C') or language not in ('A', 'B')

            if is_azc:
                azc_folios[folio].append(word)

    return dict(azc_folios)


def calculate_ht_profile(tokens):
    """Calculate HT-relevant metrics for a token list."""
    if not tokens:
        return None

    prefix_counts = Counter()
    phase_counts = Counter()

    for token in tokens:
        prefix = get_prefix(token)
        prefix_counts[prefix] += 1

        if prefix in HT_PREFIXES:
            phase_counts[HT_PREFIXES[prefix]] += 1

    total = len(tokens)

    # Calculate rates
    escape_rate = prefix_counts.get('qo', 0) / total * 100
    early_rate = sum(prefix_counts.get(p, 0) for p in ['ol', 'or', 'al', 'ar']) / total * 100
    core_rate = sum(prefix_counts.get(p, 0) for p in ['ch', 'sh']) / total * 100

    # Calculate prefix entropy
    prefix_probs = [c / total for c in prefix_counts.values()]
    prefix_entropy = -sum(p * math.log2(p) for p in prefix_probs if p > 0)

    return {
        'token_count': total,
        'escape_rate': round(escape_rate, 2),
        'early_rate': round(early_rate, 2),
        'core_rate': round(core_rate, 2),
        'prefix_entropy': round(prefix_entropy, 3),
        'prefix_distribution': dict(prefix_counts),
        'phase_distribution': dict(phase_counts)
    }


def calculate_profile_distance(p1, p2):
    """Calculate distance between two HT profiles."""
    # Use difference in key rates
    escape_diff = abs(p1['escape_rate'] - p2['escape_rate'])
    early_diff = abs(p1['early_rate'] - p2['early_rate'])
    core_diff = abs(p1['core_rate'] - p2['core_rate'])

    return (escape_diff + early_diff + core_diff) / 3


def cluster_by_profile(profiles, threshold=5.0):
    """Simple clustering by profile similarity."""
    folios = list(profiles.keys())
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

            dist = calculate_profile_distance(profiles[f1], profiles[f2])
            if dist < threshold:
                cluster.append(f2)
                assigned.add(f2)

        clusters.append(cluster)

    return clusters


def main():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    print("Loading AZC tokens by folio...")
    azc_folios = load_azc_tokens_by_folio(data_path)

    print(f"  AZC folios: {len(azc_folios)}")

    print("\n" + "="*60)
    print("ANALYSIS: HT Profile by AZC Folio")
    print("="*60)

    profiles = {}
    for folio, tokens in azc_folios.items():
        profile = calculate_ht_profile(tokens)
        if profile:
            profiles[folio] = profile

    # Summary table
    print(f"\n{'Folio':<10} {'Tokens':>7} {'Escape%':>8} {'Early%':>7} {'Core%':>6} {'Entropy':>8}")
    print("-"*55)

    escape_rates = []
    early_rates = []
    core_rates = []
    entropies = []

    for folio in sorted(profiles.keys()):
        p = profiles[folio]
        print(f"{folio:<10} {p['token_count']:>7} {p['escape_rate']:>8.2f} "
              f"{p['early_rate']:>7.2f} {p['core_rate']:>6.2f} {p['prefix_entropy']:>8.3f}")
        escape_rates.append(p['escape_rate'])
        early_rates.append(p['early_rate'])
        core_rates.append(p['core_rate'])
        entropies.append(p['prefix_entropy'])

    print("-"*55)
    print(f"{'MEAN':<10} {'':>7} {sum(escape_rates)/len(escape_rates):>8.2f} "
          f"{sum(early_rates)/len(early_rates):>7.2f} {sum(core_rates)/len(core_rates):>6.2f} "
          f"{sum(entropies)/len(entropies):>8.3f}")

    # Variance analysis
    escape_var = max(escape_rates) - min(escape_rates)
    early_var = max(early_rates) - min(early_rates)
    core_var = max(core_rates) - min(core_rates)

    print("\n" + "="*60)
    print("VARIANCE ANALYSIS")
    print("="*60)
    print(f"\nEscape rate range: {min(escape_rates):.2f}% - {max(escape_rates):.2f}% (variance: {escape_var:.2f}pp)")
    print(f"Early rate range: {min(early_rates):.2f}% - {max(early_rates):.2f}% (variance: {early_var:.2f}pp)")
    print(f"Core rate range: {min(core_rates):.2f}% - {max(core_rates):.2f}% (variance: {core_var:.2f}pp)")

    # Extreme folios
    sorted_by_escape = sorted(profiles.items(), key=lambda x: x[1]['escape_rate'])

    print("\nFolios with LOWEST escape rate:")
    for folio, p in sorted_by_escape[:5]:
        print(f"  {folio}: {p['escape_rate']:.2f}%")

    print("\nFolios with HIGHEST escape rate:")
    for folio, p in sorted_by_escape[-5:]:
        print(f"  {folio}: {p['escape_rate']:.2f}%")

    # Clustering
    print("\n" + "="*60)
    print("PROFILE CLUSTERING")
    print("="*60)

    clusters = cluster_by_profile(profiles, threshold=3.0)
    print(f"\nClusters found (threshold=3.0pp): {len(clusters)}")

    for i, cluster in enumerate(sorted(clusters, key=len, reverse=True)[:5]):
        if len(cluster) > 1:
            print(f"  Cluster {i+1} ({len(cluster)} folios): {', '.join(sorted(cluster)[:5])}...")

    # Build output
    output = {
        'fit_id': 'F-AZC-013',
        'question': 'Do different AZC folios have different HT profiles?',
        'aggregate': {
            'folio_count': len(profiles),
            'escape_rate': {
                'mean': round(sum(escape_rates)/len(escape_rates), 2),
                'min': round(min(escape_rates), 2),
                'max': round(max(escape_rates), 2),
                'variance': round(escape_var, 2)
            },
            'early_rate': {
                'mean': round(sum(early_rates)/len(early_rates), 2),
                'min': round(min(early_rates), 2),
                'max': round(max(early_rates), 2),
                'variance': round(early_var, 2)
            },
            'core_rate': {
                'mean': round(sum(core_rates)/len(core_rates), 2),
                'min': round(min(core_rates), 2),
                'max': round(max(core_rates), 2),
                'variance': round(core_var, 2)
            }
        },
        'cluster_count': len(clusters),
        'interpretation': {}
    }

    # Interpret
    significant_variance = escape_var > 5 or early_var > 10 or core_var > 10

    if significant_variance:
        output['interpretation']['conclusion'] = 'AZC folios show DISTINCT HT profiles'
        output['interpretation']['evidence'] = f"Escape variance: {escape_var:.1f}pp, Early variance: {early_var:.1f}pp"
        output['interpretation']['implication'] = 'Different AZC folios instantiate different orientation postures'
    else:
        output['interpretation']['conclusion'] = 'AZC folios show UNIFORM HT profiles'
        output['interpretation']['evidence'] = f"Low variance across all metrics"
        output['interpretation']['implication'] = 'AZC folios differ in vocabulary but not in HT structure'

    # Save
    results_path = Path(__file__).parent.parent.parent / 'results' / 'azc_ht_modulation.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    print(f"\n\nResults saved to {results_path}")
    print("\n" + "="*60)
    print("CONCLUSION")
    print("="*60)
    print(f"  {output['interpretation']['conclusion']}")
    print(f"  {output['interpretation']['evidence']}")
    print(f"  {output['interpretation']['implication']}")


if __name__ == '__main__':
    main()
