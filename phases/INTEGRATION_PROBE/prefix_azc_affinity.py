#!/usr/bin/env python3
"""
Probe 1: PREFIX -> AZC Folio Affinity Analysis

Question: Do different PREFIX families have different AZC folio affinity patterns?

Method:
1. For each PREFIX (ch, sh, ok, ot, da, qo, ol, ct), collect all tokens from AZC folios
2. For each PREFIX, aggregate which AZC folios its vocabulary appears in
3. Measure: is PREFIX -> AZC folio distribution non-uniform?

Key test: ct- is 85.9% Section H (C273). Does it also concentrate in specific AZC folios?

Prediction:
- If hypothesis true: PREFIX families have distinct AZC folio profiles
- If hypothesis false: PREFIX -> AZC distribution is uniform
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List, Tuple
import numpy as np
from scipy import stats

# Configuration
DATA_FILE = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
OUTPUT_FILE = Path("C:/git/voynich/results/integration_probe_prefix_azc.json")

# PREFIX families (from C235)
PREFIX_PATTERNS = {
    'ch': r'^ch',
    'sh': r'^sh',
    'ok': r'^ok',
    'ot': r'^ot',
    'da': r'^da',
    'qo': r'^qo',
    'ol': r'^ol',
    'ct': r'^ct'
}

# AZC sections
AZC_SECTIONS = {'Z', 'A', 'C'}


def load_azc_data(filepath: Path) -> Dict[str, Dict]:
    """Load AZC token data with folio information."""
    token_data = defaultdict(lambda: {'folios': set(), 'count': 0, 'sections': set()})
    azc_folios = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()

            # Skip invalid tokens
            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Identify AZC folios
            is_azc = section in AZC_SECTIONS or language not in ('A', 'B')

            if is_azc:
                azc_folios.add(folio)
                token_data[word]['folios'].add(folio)
                token_data[word]['count'] += 1
                token_data[word]['sections'].add(section)

    print(f"Loaded {len(token_data)} unique tokens from {len(azc_folios)} AZC folios")
    return dict(token_data), azc_folios


def extract_prefix(token: str) -> str:
    """Extract PREFIX family from token."""
    for prefix_name, pattern in PREFIX_PATTERNS.items():
        if re.match(pattern, token):
            return prefix_name
    return 'OTHER'


def analyze_prefix_azc_affinity(token_data: Dict, azc_folios: Set[str]) -> Dict:
    """Analyze PREFIX -> AZC folio affinity patterns."""

    # Build PREFIX -> AZC folio mapping
    prefix_to_folios = defaultdict(lambda: defaultdict(int))  # prefix -> folio -> count
    prefix_token_counts = defaultdict(int)
    prefix_tokens = defaultdict(list)

    for token, data in token_data.items():
        prefix = extract_prefix(token)
        prefix_token_counts[prefix] += data['count']
        prefix_tokens[prefix].append(token)

        for folio in data['folios']:
            prefix_to_folios[prefix][folio] += data['count']

    # Calculate distribution metrics for each PREFIX
    results = {}
    all_folios = sorted(azc_folios)
    n_folios = len(all_folios)

    for prefix in PREFIX_PATTERNS.keys():
        folio_dist = prefix_to_folios[prefix]
        total_count = sum(folio_dist.values())

        if total_count == 0:
            continue

        # Calculate folio coverage
        covered_folios = len([f for f in folio_dist if folio_dist[f] > 0])
        coverage = covered_folios / n_folios

        # Calculate distribution entropy
        counts = [folio_dist.get(f, 0) for f in all_folios]
        probs = np.array(counts) / sum(counts) if sum(counts) > 0 else np.zeros(len(counts))
        probs = probs[probs > 0]  # Remove zeros for entropy calc
        entropy = -np.sum(probs * np.log2(probs)) if len(probs) > 0 else 0
        max_entropy = np.log2(n_folios)
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        # Find top folios
        sorted_folios = sorted(folio_dist.items(), key=lambda x: -x[1])
        top_5 = sorted_folios[:5]
        top_5_share = sum(c for _, c in top_5) / total_count if total_count > 0 else 0

        # Calculate Gini coefficient (inequality measure)
        counts_sorted = sorted(counts)
        n = len(counts_sorted)
        cumsum = np.cumsum(counts_sorted)
        gini = (2 * np.sum((np.arange(1, n+1) * counts_sorted))) / (n * np.sum(counts_sorted)) - (n + 1) / n if np.sum(counts_sorted) > 0 else 0

        results[prefix] = {
            'total_tokens': total_count,
            'unique_types': len(prefix_tokens[prefix]),
            'folios_covered': covered_folios,
            'coverage_pct': round(coverage * 100, 1),
            'entropy': round(entropy, 3),
            'normalized_entropy': round(normalized_entropy, 3),
            'gini_coefficient': round(gini, 3),
            'top_5_folios': [(f, c, round(c/total_count*100, 1)) for f, c in top_5],
            'top_5_share_pct': round(top_5_share * 100, 1)
        }

    return results


def compare_prefix_distributions(results: Dict) -> Dict:
    """Compare PREFIX distributions to test for non-uniformity."""

    comparisons = {}

    # Extract normalized entropy for comparison
    entropies = {p: r['normalized_entropy'] for p, r in results.items()}
    mean_entropy = np.mean(list(entropies.values()))
    std_entropy = np.std(list(entropies.values()))

    # Extract Gini coefficients
    ginis = {p: r['gini_coefficient'] for p, r in results.items()}
    mean_gini = np.mean(list(ginis.values()))
    std_gini = np.std(list(ginis.values()))

    # Overall uniformity test
    # If all PREFIX distributions were uniform, entropy would be near 1.0
    # If all PREFIX distributions were identical, std would be near 0

    comparisons['mean_normalized_entropy'] = round(mean_entropy, 3)
    comparisons['std_normalized_entropy'] = round(std_entropy, 3)
    comparisons['mean_gini'] = round(mean_gini, 3)
    comparisons['std_gini'] = round(std_gini, 3)

    # Interpretation
    if mean_entropy < 0.7:
        comparisons['entropy_interpretation'] = 'LOW - PREFIX distributions are concentrated'
    elif mean_entropy < 0.85:
        comparisons['entropy_interpretation'] = 'MODERATE - some concentration'
    else:
        comparisons['entropy_interpretation'] = 'HIGH - near-uniform distribution'

    if std_entropy > 0.1:
        comparisons['variation_interpretation'] = 'HIGH - PREFIX families differ from each other'
    else:
        comparisons['variation_interpretation'] = 'LOW - PREFIX families behave similarly'

    return comparisons


def test_ct_hypothesis(token_data: Dict, azc_folios: Set[str]) -> Dict:
    """
    Specific test: ct- is 85.9% Section H (C273).
    Does it also concentrate in specific AZC folios?
    """
    ct_folios = defaultdict(int)
    ct_total = 0

    for token, data in token_data.items():
        if token.startswith('ct'):
            ct_total += data['count']
            for folio in data['folios']:
                ct_folios[folio] += data['count']

    if ct_total == 0:
        return {'status': 'NO CT TOKENS FOUND'}

    # How concentrated is ct- in AZC folios?
    sorted_folios = sorted(ct_folios.items(), key=lambda x: -x[1])

    # Top folio concentration
    top_folio, top_count = sorted_folios[0] if sorted_folios else (None, 0)
    top_share = top_count / ct_total if ct_total > 0 else 0

    # Top 3 folios concentration
    top_3_share = sum(c for _, c in sorted_folios[:3]) / ct_total if ct_total > 0 else 0

    return {
        'ct_total_tokens': ct_total,
        'ct_folios_covered': len(ct_folios),
        'top_folio': top_folio,
        'top_folio_share_pct': round(top_share * 100, 1),
        'top_3_share_pct': round(top_3_share * 100, 1),
        'all_folios': [(f, c, round(c/ct_total*100, 1)) for f, c in sorted_folios]
    }


def main():
    print("=" * 60)
    print("PROBE 1: PREFIX -> AZC FOLIO AFFINITY ANALYSIS")
    print("=" * 60)

    # Load data
    print("\n1. Loading AZC token data...")
    token_data, azc_folios = load_azc_data(DATA_FILE)

    # Analyze PREFIX -> AZC affinity
    print("\n2. Analyzing PREFIX -> AZC folio affinity...")
    prefix_results = analyze_prefix_azc_affinity(token_data, azc_folios)

    # Compare distributions
    print("\n3. Comparing PREFIX distributions...")
    comparisons = compare_prefix_distributions(prefix_results)

    # Test ct- hypothesis
    print("\n4. Testing ct- concentration hypothesis...")
    ct_test = test_ct_hypothesis(token_data, azc_folios)

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print("\n--- PREFIX -> AZC Folio Affinity ---")
    for prefix, data in sorted(prefix_results.items()):
        print(f"\n{prefix.upper()}:")
        print(f"  Tokens: {data['total_tokens']:,} ({data['unique_types']} types)")
        print(f"  Folios covered: {data['folios_covered']}/{len(azc_folios)} ({data['coverage_pct']}%)")
        print(f"  Normalized entropy: {data['normalized_entropy']} (1.0 = uniform)")
        print(f"  Gini coefficient: {data['gini_coefficient']} (0 = equal, 1 = concentrated)")
        print(f"  Top 5 folios: {', '.join([f'{f} ({pct}%)' for f, _, pct in data['top_5_folios']])}")
        print(f"  Top 5 share: {data['top_5_share_pct']}%")

    print("\n--- Distribution Comparison ---")
    print(f"Mean normalized entropy: {comparisons['mean_normalized_entropy']}")
    print(f"Std normalized entropy: {comparisons['std_normalized_entropy']}")
    print(f"Mean Gini: {comparisons['mean_gini']}")
    print(f"Interpretation: {comparisons['entropy_interpretation']}")
    print(f"Variation: {comparisons['variation_interpretation']}")

    print("\n--- ct- Concentration Test ---")
    if ct_test.get('status') != 'NO CT TOKENS FOUND':
        print(f"ct- total tokens: {ct_test['ct_total_tokens']}")
        print(f"ct- folios covered: {ct_test['ct_folios_covered']}")
        print(f"Top folio: {ct_test['top_folio']} ({ct_test['top_folio_share_pct']}%)")
        print(f"Top 3 share: {ct_test['top_3_share_pct']}%")
    else:
        print("No ct- tokens found in AZC")

    # Hypothesis verdict
    print("\n" + "=" * 60)
    print("HYPOTHESIS VERDICT")
    print("=" * 60)

    # Check if distributions are non-uniform
    if comparisons['mean_normalized_entropy'] < 0.85:
        print("\n[+] PREFIX -> AZC distributions are NON-UNIFORM")
        print("    (mean entropy < 0.85)")
        signal = True
    else:
        print("\n[-] PREFIX -> AZC distributions are approximately UNIFORM")
        print("    (mean entropy >= 0.85)")
        signal = False

    # Check if PREFIX families differ
    if comparisons['std_normalized_entropy'] > 0.05:
        print("\n[+] PREFIX families show DIFFERENT AZC profiles")
        print(f"    (std = {comparisons['std_normalized_entropy']})")
        variation = True
    else:
        print("\n[-] PREFIX families have SIMILAR AZC profiles")
        print(f"    (std = {comparisons['std_normalized_entropy']})")
        variation = False

    if signal and variation:
        print("\n>>> HYPOTHESIS SUPPORTED: PREFIX determines AZC affinity <<<")
        verdict = "SUPPORTED"
    elif signal and not variation:
        print("\n>>> PARTIAL: All PREFIX families concentrate similarly <<<")
        verdict = "PARTIAL"
    else:
        print("\n>>> HYPOTHESIS NOT SUPPORTED: Distribution is uniform <<<")
        verdict = "NOT_SUPPORTED"

    # Save results
    output = {
        'probe': 'PREFIX_AZC_AFFINITY',
        'n_azc_folios': len(azc_folios),
        'n_token_types': len(token_data),
        'prefix_results': prefix_results,
        'comparisons': comparisons,
        'ct_test': ct_test,
        'verdict': verdict
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # Convert sets to lists for JSON serialization
        def convert_sets(obj):
            if isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, dict):
                return {k: convert_sets(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_sets(v) for v in obj]
            return obj

        json.dump(convert_sets(output), f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")

    return output


if __name__ == "__main__":
    main()
