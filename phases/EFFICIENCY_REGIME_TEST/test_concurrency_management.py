#!/usr/bin/env python3
"""
Concurrency Management Probe

Tests whether Zodiac vs A/C encodes parallel-instance management patterns.

Method:
1. Cluster A entries by contextual overlap signatures (which AZC folios they appear in)
2. Determine A/C vs Zodiac bias for each entry
3. Compute HT oscillation density for contexts where each bias class appears
4. Compare oscillation patterns

Prediction (concurrency hypothesis):
- Zodiac-biased entries -> higher HT oscillation (frequent batch-checking)
- A/C-biased entries -> lower oscillation, more sustained (deep attention)

If confirmed: Zodiac = parallel batch management, A/C = single batch deep attention
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
import statistics

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "concurrency_management_probe.json"

# AZC Family definitions
ZODIAC_FOLIOS = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}

AC_FOLIOS = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}

ALL_AZC_FOLIOS = ZODIAC_FOLIOS | AC_FOLIOS

# HT markers (from existing constraints)
HT_MARKERS = {'s', 'd', 'm'}  # Common HT-associated tokens


def load_a_entries_with_azc_context() -> Dict[str, Dict]:
    """
    Load Currier A entries and their AZC folio appearances.

    Returns: {token: {azc_folios: set, ac_count: int, zodiac_count: int, total_a: int}}
    """
    a_entries = defaultdict(lambda: {
        'azc_folios': set(),
        'ac_count': 0,
        'zodiac_count': 0,
        'total_a': 0,
        'b_folios': set()
    })

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            language = row.get('language', '').strip()
            section = row.get('section', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Track A entries
            if language == 'A':
                a_entries[word]['total_a'] += 1

            # Track B appearances
            if language == 'B':
                a_entries[word]['b_folios'].add(folio)

            # Track AZC appearances
            is_azc = section in {'Z', 'A', 'C'} or language not in ('A', 'B')
            if is_azc and folio in ALL_AZC_FOLIOS:
                a_entries[word]['azc_folios'].add(folio)
                if folio in AC_FOLIOS:
                    a_entries[word]['ac_count'] += 1
                elif folio in ZODIAC_FOLIOS:
                    a_entries[word]['zodiac_count'] += 1

    # Filter to entries that appear in both A and AZC
    result = {}
    for token, data in a_entries.items():
        if data['total_a'] > 0 and len(data['azc_folios']) > 0:
            result[token] = {
                'azc_folios': data['azc_folios'],
                'ac_count': data['ac_count'],
                'zodiac_count': data['zodiac_count'],
                'total_a': data['total_a'],
                'b_folios': data['b_folios']
            }

    return result


def compute_family_bias(entry_data: Dict) -> Tuple[str, float]:
    """
    Compute family bias for an A entry.

    Returns: (bias_class, bias_strength)
    - bias_class: 'AC_BIASED', 'ZODIAC_BIASED', or 'BALANCED'
    - bias_strength: 0-1, how strongly biased
    """
    ac = entry_data['ac_count']
    zodiac = entry_data['zodiac_count']
    total = ac + zodiac

    if total == 0:
        return 'NO_AZC', 0.0

    ac_fraction = ac / total

    if ac_fraction > 0.7:
        return 'AC_BIASED', ac_fraction
    elif ac_fraction < 0.3:
        return 'ZODIAC_BIASED', 1 - ac_fraction
    else:
        return 'BALANCED', 0.5


def compute_contextual_overlap_signature(entry_data: Dict) -> Tuple:
    """
    Compute a contextual overlap signature for clustering.

    Returns tuple of (n_azc_folios, n_ac_folios, n_zodiac_folios, ac_fraction)
    """
    azc_folios = entry_data['azc_folios']
    ac_folios = azc_folios & AC_FOLIOS
    zodiac_folios = azc_folios & ZODIAC_FOLIOS

    n_total = len(azc_folios)
    n_ac = len(ac_folios)
    n_zodiac = len(zodiac_folios)

    ac_fraction = n_ac / n_total if n_total > 0 else 0

    return (n_total, n_ac, n_zodiac, round(ac_fraction, 2))


def load_ht_data_by_folio() -> Dict[str, Dict]:
    """
    Load HT token data by folio.

    Returns: {folio: {ht_count: int, total_tokens: int, ht_positions: list}}
    """
    folio_data = defaultdict(lambda: {
        'ht_count': 0,
        'total_tokens': 0,
        'ht_positions': [],
        'token_index': 0
    })

    current_folio = None
    token_index = 0

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()

            if not word or word.startswith('[') or word.startswith('<'):
                continue

            # Reset index on new folio
            if folio != current_folio:
                current_folio = folio
                token_index = 0

            folio_data[folio]['total_tokens'] += 1

            # Check if HT marker
            is_ht = any(word.startswith(m) or word == m for m in HT_MARKERS)
            if is_ht:
                folio_data[folio]['ht_count'] += 1
                folio_data[folio]['ht_positions'].append(token_index)

            token_index += 1

    return dict(folio_data)


def compute_ht_oscillation_density(ht_positions: List[int], total_tokens: int) -> Dict:
    """
    Compute HT oscillation metrics.

    Returns:
    - density: HT per token
    - mean_interval: average tokens between HT markers
    - interval_variance: how regular is the rhythm
    - oscillation_score: combined metric
    """
    if len(ht_positions) < 2:
        return {
            'density': len(ht_positions) / total_tokens if total_tokens > 0 else 0,
            'mean_interval': None,
            'interval_variance': None,
            'oscillation_score': 0
        }

    # Compute intervals
    intervals = [ht_positions[i+1] - ht_positions[i] for i in range(len(ht_positions)-1)]

    density = len(ht_positions) / total_tokens if total_tokens > 0 else 0
    mean_interval = statistics.mean(intervals)

    if len(intervals) > 1:
        interval_variance = statistics.stdev(intervals) / mean_interval if mean_interval > 0 else 0
    else:
        interval_variance = 0

    # Oscillation score: high density + regular rhythm = high oscillation
    # Low density or irregular rhythm = low oscillation (sustained attention)
    regularity = 1 / (1 + interval_variance)  # 0-1, higher = more regular
    oscillation_score = density * regularity

    return {
        'density': round(density, 4),
        'mean_interval': round(mean_interval, 2),
        'interval_variance': round(interval_variance, 3),
        'regularity': round(regularity, 3),
        'oscillation_score': round(oscillation_score, 4)
    }


def analyze_ht_by_family_bias(a_entries: Dict, ht_data: Dict) -> Dict:
    """
    Analyze HT oscillation patterns by family bias.
    """
    # Group entries by bias
    bias_groups = defaultdict(list)

    for token, data in a_entries.items():
        bias_class, bias_strength = compute_family_bias(data)
        if bias_class in ['AC_BIASED', 'ZODIAC_BIASED']:
            bias_groups[bias_class].append({
                'token': token,
                'bias_strength': bias_strength,
                'b_folios': data['b_folios'],
                'azc_folios': data['azc_folios']
            })

    # For each bias group, compute HT oscillation in their B folio contexts
    results = {}

    for bias_class, entries in bias_groups.items():
        # Collect all B folios where this bias class appears
        all_b_folios = set()
        for entry in entries:
            all_b_folios.update(entry['b_folios'])

        # Compute HT oscillation for these folios
        oscillations = []
        for folio in all_b_folios:
            if folio in ht_data and ht_data[folio]['total_tokens'] > 20:
                osc = compute_ht_oscillation_density(
                    ht_data[folio]['ht_positions'],
                    ht_data[folio]['total_tokens']
                )
                if osc['oscillation_score'] > 0:
                    oscillations.append(osc)

        if oscillations:
            results[bias_class] = {
                'n_entries': len(entries),
                'n_b_folios': len(all_b_folios),
                'n_folios_analyzed': len(oscillations),
                'mean_density': round(statistics.mean([o['density'] for o in oscillations]), 4),
                'mean_oscillation': round(statistics.mean([o['oscillation_score'] for o in oscillations]), 4),
                'mean_regularity': round(statistics.mean([o['regularity'] for o in oscillations]), 3),
                'oscillations': oscillations[:5]  # Sample
            }
        else:
            results[bias_class] = {
                'n_entries': len(entries),
                'n_b_folios': len(all_b_folios),
                'n_folios_analyzed': 0,
                'mean_density': 0,
                'mean_oscillation': 0,
                'mean_regularity': 0
            }

    return results


def analyze_ht_in_azc_folios(ht_data: Dict) -> Dict:
    """
    Analyze HT oscillation directly in AZC folios by family.
    """
    zodiac_oscillations = []
    ac_oscillations = []

    for folio in ZODIAC_FOLIOS:
        if folio in ht_data and ht_data[folio]['total_tokens'] > 10:
            osc = compute_ht_oscillation_density(
                ht_data[folio]['ht_positions'],
                ht_data[folio]['total_tokens']
            )
            zodiac_oscillations.append({
                'folio': folio,
                **osc
            })

    for folio in AC_FOLIOS:
        if folio in ht_data and ht_data[folio]['total_tokens'] > 10:
            osc = compute_ht_oscillation_density(
                ht_data[folio]['ht_positions'],
                ht_data[folio]['total_tokens']
            )
            ac_oscillations.append({
                'folio': folio,
                **osc
            })

    results = {
        'zodiac': {
            'n_folios': len(zodiac_oscillations),
            'mean_density': round(statistics.mean([o['density'] for o in zodiac_oscillations]), 4) if zodiac_oscillations else 0,
            'mean_oscillation': round(statistics.mean([o['oscillation_score'] for o in zodiac_oscillations]), 4) if zodiac_oscillations else 0,
            'mean_regularity': round(statistics.mean([o['regularity'] for o in zodiac_oscillations]), 3) if zodiac_oscillations else 0,
            'folios': zodiac_oscillations
        },
        'ac': {
            'n_folios': len(ac_oscillations),
            'mean_density': round(statistics.mean([o['density'] for o in ac_oscillations]), 4) if ac_oscillations else 0,
            'mean_oscillation': round(statistics.mean([o['oscillation_score'] for o in ac_oscillations]), 4) if ac_oscillations else 0,
            'mean_regularity': round(statistics.mean([o['regularity'] for o in ac_oscillations]), 3) if ac_oscillations else 0,
            'folios': ac_oscillations
        }
    }

    return results


def cluster_by_contextual_overlap(a_entries: Dict) -> Dict:
    """
    Cluster A entries by their contextual overlap signatures.
    """
    # Group by signature
    signature_groups = defaultdict(list)

    for token, data in a_entries.items():
        sig = compute_contextual_overlap_signature(data)
        # Bin by ac_fraction: 0-0.3, 0.3-0.7, 0.7-1.0
        ac_frac = sig[3]
        if ac_frac < 0.3:
            bin_label = 'ZODIAC_DOMINANT'
        elif ac_frac > 0.7:
            bin_label = 'AC_DOMINANT'
        else:
            bin_label = 'MIXED'

        # Also bin by coverage: narrow (1-3 folios), medium (4-8), broad (9+)
        n_folios = sig[0]
        if n_folios <= 3:
            coverage = 'NARROW'
        elif n_folios <= 8:
            coverage = 'MEDIUM'
        else:
            coverage = 'BROAD'

        cluster_key = f"{bin_label}_{coverage}"
        signature_groups[cluster_key].append({
            'token': token,
            'signature': sig,
            **data
        })

    # Summarize clusters
    cluster_summary = {}
    for cluster_key, entries in signature_groups.items():
        cluster_summary[cluster_key] = {
            'n_entries': len(entries),
            'mean_azc_folios': round(statistics.mean([len(e['azc_folios']) for e in entries]), 2),
            'mean_ac_count': round(statistics.mean([e['ac_count'] for e in entries]), 2),
            'mean_zodiac_count': round(statistics.mean([e['zodiac_count'] for e in entries]), 2),
            'sample_tokens': [e['token'] for e in entries[:5]]
        }

    return cluster_summary


def main():
    print("=" * 70)
    print("CONCURRENCY MANAGEMENT PROBE")
    print("=" * 70)
    print("\nHypothesis: Zodiac vs A/C encodes parallel-instance management")
    print("Prediction: Zodiac = high HT oscillation (batch-checking)")
    print("            A/C = low oscillation (sustained attention)")
    print()

    # Load A entries with AZC context
    print("1. Loading A entries with AZC context...")
    a_entries = load_a_entries_with_azc_context()
    print(f"   Found {len(a_entries)} A entries appearing in AZC folios")

    # Classify by family bias
    bias_counts = Counter()
    for token, data in a_entries.items():
        bias_class, _ = compute_family_bias(data)
        bias_counts[bias_class] += 1

    print(f"\n   Bias distribution:")
    for bias, count in sorted(bias_counts.items()):
        print(f"     {bias}: {count}")

    # Cluster by contextual overlap
    print("\n2. Clustering by contextual overlap signatures...")
    clusters = cluster_by_contextual_overlap(a_entries)
    print(f"   Found {len(clusters)} clusters")
    for cluster_key, summary in sorted(clusters.items()):
        print(f"     {cluster_key}: {summary['n_entries']} entries, mean {summary['mean_azc_folios']:.1f} AZC folios")

    # Load HT data
    print("\n3. Loading HT oscillation data...")
    ht_data = load_ht_data_by_folio()
    print(f"   Loaded HT data for {len(ht_data)} folios")

    # Analyze HT directly in AZC folios
    print("\n4. Analyzing HT oscillation in AZC folios...")
    azc_ht = analyze_ht_in_azc_folios(ht_data)

    print(f"\n   ZODIAC folios (n={azc_ht['zodiac']['n_folios']}):")
    print(f"     Mean HT density: {azc_ht['zodiac']['mean_density']}")
    print(f"     Mean oscillation score: {azc_ht['zodiac']['mean_oscillation']}")
    print(f"     Mean regularity: {azc_ht['zodiac']['mean_regularity']}")

    print(f"\n   A/C folios (n={azc_ht['ac']['n_folios']}):")
    print(f"     Mean HT density: {azc_ht['ac']['mean_density']}")
    print(f"     Mean oscillation score: {azc_ht['ac']['mean_oscillation']}")
    print(f"     Mean regularity: {azc_ht['ac']['mean_regularity']}")

    # Analyze HT by family bias in B contexts
    print("\n5. Analyzing HT in B folios by vocabulary family bias...")
    bias_ht = analyze_ht_by_family_bias(a_entries, ht_data)

    for bias_class, data in bias_ht.items():
        print(f"\n   {bias_class} vocabulary in B:")
        print(f"     N entries: {data['n_entries']}")
        print(f"     N B folios: {data['n_b_folios']}")
        print(f"     Mean HT density: {data['mean_density']}")
        print(f"     Mean oscillation: {data['mean_oscillation']}")

    # Interpret results
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    # Compare Zodiac vs A/C oscillation in AZC folios
    zodiac_osc = azc_ht['zodiac']['mean_oscillation']
    ac_osc = azc_ht['ac']['mean_oscillation']

    zodiac_reg = azc_ht['zodiac']['mean_regularity']
    ac_reg = azc_ht['ac']['mean_regularity']

    print(f"\n--- Direct AZC Comparison ---")
    print(f"Zodiac oscillation: {zodiac_osc:.4f}, regularity: {zodiac_reg:.3f}")
    print(f"A/C oscillation: {ac_osc:.4f}, regularity: {ac_reg:.3f}")

    if zodiac_osc > ac_osc * 1.2:
        osc_verdict = 'ZODIAC_HIGHER_OSCILLATION'
        osc_interp = 'Zodiac shows higher HT oscillation (supports batch-checking)'
    elif ac_osc > zodiac_osc * 1.2:
        osc_verdict = 'AC_HIGHER_OSCILLATION'
        osc_interp = 'A/C shows higher HT oscillation (opposite of prediction)'
    else:
        osc_verdict = 'NO_DIFFERENCE'
        osc_interp = 'No significant oscillation difference between families'

    print(f"\nOscillation verdict: {osc_verdict}")
    print(f"  {osc_interp}")

    if zodiac_reg > ac_reg * 1.1:
        reg_verdict = 'ZODIAC_MORE_REGULAR'
        reg_interp = 'Zodiac shows more regular HT rhythm (supports periodic checking)'
    elif ac_reg > zodiac_reg * 1.1:
        reg_verdict = 'AC_MORE_REGULAR'
        reg_interp = 'A/C shows more regular HT rhythm'
    else:
        reg_verdict = 'SIMILAR_REGULARITY'
        reg_interp = 'Similar HT rhythm regularity'

    print(f"\nRegularity verdict: {reg_verdict}")
    print(f"  {reg_interp}")

    # Overall verdict
    print("\n" + "=" * 70)
    print("OVERALL VERDICT")
    print("=" * 70)

    if osc_verdict == 'ZODIAC_HIGHER_OSCILLATION' and reg_verdict == 'ZODIAC_MORE_REGULAR':
        overall = 'CONCURRENCY_SUPPORTED'
        interpretation = 'Zodiac shows higher, more regular HT oscillation - consistent with parallel batch monitoring'
    elif osc_verdict == 'AC_HIGHER_OSCILLATION':
        overall = 'CONCURRENCY_FALSIFIED'
        interpretation = 'A/C shows higher oscillation - opposite of prediction'
    elif osc_verdict == 'NO_DIFFERENCE':
        overall = 'INCONCLUSIVE'
        interpretation = 'No oscillation difference - concurrency hypothesis not supported by HT patterns'
    else:
        overall = 'PARTIAL'
        interpretation = 'Mixed signals - some support for concurrency hypothesis'

    print(f"\n>>> {overall} <<<")
    print(f"    {interpretation}")

    # Save results
    results = {
        'probe_id': 'CONCURRENCY_MANAGEMENT',
        'hypothesis': 'Zodiac = parallel batch management, A/C = single batch attention',
        'prediction': 'Zodiac should show higher, more regular HT oscillation',
        'a_entry_analysis': {
            'n_entries': len(a_entries),
            'bias_distribution': dict(bias_counts),
            'clusters': clusters
        },
        'azc_ht_analysis': azc_ht,
        'bias_ht_analysis': {k: {kk: vv for kk, vv in v.items() if kk != 'oscillations'}
                            for k, v in bias_ht.items()},
        'verdicts': {
            'oscillation': osc_verdict,
            'regularity': reg_verdict,
            'overall': overall
        },
        'interpretation': interpretation
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return results


if __name__ == "__main__":
    main()
