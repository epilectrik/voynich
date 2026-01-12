#!/usr/bin/env python3
"""
Probe 2: MIDDLE -> AZC Exclusivity Test

Question: Do PREFIX-exclusive MIDDLEs map to specific AZC folios?

Method:
1. Parse tokens to extract MIDDLE components
2. Identify which MIDDLEs are PREFIX-exclusive vs shared across prefixes
3. For each MIDDLE, measure AZC folio concentration
4. Compare: exclusive MIDDLEs vs shared MIDDLEs AZC concentration

Prediction: Exclusive MIDDLEs should show higher AZC folio concentration
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional
import numpy as np

DATA_FILE = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
OUTPUT_FILE = Path("C:/git/voynich/results/integration_probe_middle_azc.json")

# PREFIX and SUFFIX patterns for parsing
PREFIXES = ['ch', 'sh', 'ok', 'ot', 'da', 'qo', 'ol', 'ct']
SUFFIXES = ['dy', 'ol', 'or', 'ar', 'al', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'ey', 'eey', 'chy', 'shy']

# AZC sections
AZC_SECTIONS = {'Z', 'A', 'C'}


def parse_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse token into PREFIX, MIDDLE, SUFFIX components.
    Returns (prefix, middle, suffix) or (None, None, None) if unparseable.
    """
    # Find prefix
    prefix = None
    for p in PREFIXES:
        if token.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]

    # Find suffix (try longest first)
    suffix = None
    sorted_suffixes = sorted(SUFFIXES, key=len, reverse=True)
    for s in sorted_suffixes:
        if remainder.endswith(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
        suffix = ''

    # If middle is empty, return the whole remainder as middle
    if not middle:
        middle = '_EMPTY_'

    return prefix, middle, suffix


def load_azc_data(filepath: Path) -> Tuple[Dict, Set]:
    """Load AZC token data."""
    token_data = defaultdict(lambda: {'folios': defaultdict(int), 'count': 0})
    azc_folios = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            is_azc = section in AZC_SECTIONS or language not in ('A', 'B')
            if is_azc:
                azc_folios.add(folio)
                token_data[word]['folios'][folio] += 1
                token_data[word]['count'] += 1

    return dict(token_data), azc_folios


def analyze_middle_exclusivity(token_data: Dict) -> Dict:
    """Analyze which MIDDLEs are PREFIX-exclusive vs shared."""

    # Build MIDDLE -> PREFIX mapping
    middle_to_prefixes = defaultdict(set)
    middle_to_tokens = defaultdict(list)

    for token in token_data.keys():
        prefix, middle, suffix = parse_token(token)
        if prefix and middle:
            middle_to_prefixes[middle].add(prefix)
            middle_to_tokens[middle].append(token)

    # Classify MIDDLEs
    exclusive_middles = {}  # MIDDLE -> owning prefix
    shared_middles = {}     # MIDDLE -> set of prefixes

    for middle, prefixes in middle_to_prefixes.items():
        if len(prefixes) == 1:
            exclusive_middles[middle] = list(prefixes)[0]
        else:
            shared_middles[middle] = prefixes

    return {
        'exclusive_count': len(exclusive_middles),
        'shared_count': len(shared_middles),
        'exclusive_middles': exclusive_middles,
        'shared_middles': {m: list(p) for m, p in shared_middles.items()},
        'middle_to_tokens': {m: list(t) for m, t in middle_to_tokens.items()}
    }


def analyze_middle_azc_concentration(
    token_data: Dict,
    azc_folios: Set[str],
    middle_info: Dict
) -> Dict:
    """Analyze AZC concentration for exclusive vs shared MIDDLEs."""

    n_folios = len(azc_folios)
    all_folios = sorted(azc_folios)

    def calc_concentration(tokens: List[str]) -> Dict:
        """Calculate concentration metrics for a set of tokens."""
        folio_counts = defaultdict(int)
        total = 0

        for token in tokens:
            if token not in token_data:
                continue
            for folio, count in token_data[token]['folios'].items():
                folio_counts[folio] += count
                total += count

        if total == 0:
            return {'entropy': 0, 'coverage': 0, 'top_share': 0, 'folios': 0}

        # Calculate metrics
        counts = [folio_counts.get(f, 0) for f in all_folios]
        probs = np.array(counts) / total
        probs = probs[probs > 0]
        entropy = -np.sum(probs * np.log2(probs)) if len(probs) > 0 else 0
        norm_entropy = entropy / np.log2(n_folios) if n_folios > 1 else 0

        covered = len([c for c in counts if c > 0])

        sorted_counts = sorted(folio_counts.items(), key=lambda x: -x[1])
        top_3_share = sum(c for _, c in sorted_counts[:3]) / total if total > 0 else 0

        return {
            'entropy': round(norm_entropy, 3),
            'coverage': round(covered / n_folios * 100, 1),
            'top_share': round(top_3_share * 100, 1),
            'folios': covered,
            'total': total,
            'top_3': sorted_counts[:3]
        }

    # Analyze exclusive MIDDLEs
    exclusive_results = {}
    for middle, prefix in middle_info['exclusive_middles'].items():
        tokens = middle_info['middle_to_tokens'].get(middle, [])
        if tokens:
            exclusive_results[middle] = {
                'prefix': prefix,
                **calc_concentration(tokens)
            }

    # Analyze shared MIDDLEs
    shared_results = {}
    for middle, prefixes in middle_info['shared_middles'].items():
        tokens = middle_info['middle_to_tokens'].get(middle, [])
        if tokens:
            shared_results[middle] = {
                'prefixes': prefixes,
                **calc_concentration(tokens)
            }

    # Calculate aggregate statistics
    exc_entropies = [r['entropy'] for r in exclusive_results.values() if r['total'] > 0]
    sha_entropies = [r['entropy'] for r in shared_results.values() if r['total'] > 0]

    exc_coverages = [r['coverage'] for r in exclusive_results.values() if r['total'] > 0]
    sha_coverages = [r['coverage'] for r in shared_results.values() if r['total'] > 0]

    return {
        'exclusive': exclusive_results,
        'shared': shared_results,
        'aggregate': {
            'exclusive': {
                'count': len(exc_entropies),
                'mean_entropy': round(np.mean(exc_entropies), 3) if exc_entropies else 0,
                'mean_coverage': round(np.mean(exc_coverages), 1) if exc_coverages else 0,
                'median_entropy': round(np.median(exc_entropies), 3) if exc_entropies else 0
            },
            'shared': {
                'count': len(sha_entropies),
                'mean_entropy': round(np.mean(sha_entropies), 3) if sha_entropies else 0,
                'mean_coverage': round(np.mean(sha_coverages), 1) if sha_coverages else 0,
                'median_entropy': round(np.median(sha_entropies), 3) if sha_entropies else 0
            }
        }
    }


def main():
    print("=" * 60)
    print("PROBE 2: MIDDLE -> AZC EXCLUSIVITY TEST")
    print("=" * 60)

    # Load data
    print("\n1. Loading AZC token data...")
    token_data, azc_folios = load_azc_data(DATA_FILE)
    print(f"   Loaded {len(token_data)} tokens from {len(azc_folios)} AZC folios")

    # Analyze MIDDLE exclusivity
    print("\n2. Analyzing MIDDLE exclusivity...")
    middle_info = analyze_middle_exclusivity(token_data)
    print(f"   PREFIX-exclusive MIDDLEs: {middle_info['exclusive_count']}")
    print(f"   Shared MIDDLEs: {middle_info['shared_count']}")
    exclusive_pct = middle_info['exclusive_count'] / (middle_info['exclusive_count'] + middle_info['shared_count']) * 100
    print(f"   Exclusivity rate: {exclusive_pct:.1f}% (cf. C423 = 80%)")

    # Analyze AZC concentration
    print("\n3. Analyzing AZC concentration...")
    concentration = analyze_middle_azc_concentration(token_data, azc_folios, middle_info)

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    agg = concentration['aggregate']
    print("\n--- Aggregate Comparison ---")
    print(f"\nEXCLUSIVE MIDDLEs (n={agg['exclusive']['count']}):")
    print(f"  Mean normalized entropy: {agg['exclusive']['mean_entropy']}")
    print(f"  Median normalized entropy: {agg['exclusive']['median_entropy']}")
    print(f"  Mean AZC folio coverage: {agg['exclusive']['mean_coverage']}%")

    print(f"\nSHARED MIDDLEs (n={agg['shared']['count']}):")
    print(f"  Mean normalized entropy: {agg['shared']['mean_entropy']}")
    print(f"  Median normalized entropy: {agg['shared']['median_entropy']}")
    print(f"  Mean AZC folio coverage: {agg['shared']['mean_coverage']}%")

    # Interpretation
    entropy_diff = agg['shared']['mean_entropy'] - agg['exclusive']['mean_entropy']
    coverage_diff = agg['shared']['mean_coverage'] - agg['exclusive']['mean_coverage']

    print("\n--- Interpretation ---")
    if entropy_diff > 0.05:
        print(f"[+] Exclusive MIDDLEs are MORE CONCENTRATED than shared")
        print(f"    (entropy difference: {entropy_diff:.3f})")
        entropy_confirms = True
    elif entropy_diff < -0.05:
        print(f"[-] Exclusive MIDDLEs are LESS concentrated than shared")
        print(f"    (entropy difference: {entropy_diff:.3f})")
        entropy_confirms = False
    else:
        print(f"[~] Entropy difference is small ({entropy_diff:.3f})")
        entropy_confirms = None

    if coverage_diff > 5:
        print(f"[+] Exclusive MIDDLEs cover FEWER folios than shared")
        print(f"    (coverage difference: {coverage_diff:.1f}pp)")
        coverage_confirms = True
    elif coverage_diff < -5:
        print(f"[-] Exclusive MIDDLEs cover MORE folios than shared")
        print(f"    (coverage difference: {coverage_diff:.1f}pp)")
        coverage_confirms = False
    else:
        print(f"[~] Coverage difference is small ({coverage_diff:.1f}pp)")
        coverage_confirms = None

    # Show examples
    print("\n--- Examples of Highly Concentrated Exclusive MIDDLEs ---")
    concentrated = sorted(
        [(m, r) for m, r in concentration['exclusive'].items() if r['total'] >= 5],
        key=lambda x: x[1]['entropy']
    )[:10]

    for middle, r in concentrated:
        top = ', '.join([f"{f}({c})" for f, c in r['top_3']])
        print(f"  -{middle}- ({r['prefix']}-): entropy={r['entropy']}, coverage={r['coverage']}%, top: {top}")

    print("\n--- Examples of Highly Concentrated Shared MIDDLEs ---")
    concentrated_shared = sorted(
        [(m, r) for m, r in concentration['shared'].items() if r['total'] >= 5],
        key=lambda x: x[1]['entropy']
    )[:10]

    for middle, r in concentrated_shared:
        top = ', '.join([f"{f}({c})" for f, c in r['top_3']])
        pfx = '/'.join(r['prefixes'])
        print(f"  -{middle}- ({pfx}): entropy={r['entropy']}, coverage={r['coverage']}%, top: {top}")

    # Final verdict
    print("\n" + "=" * 60)
    print("HYPOTHESIS VERDICT")
    print("=" * 60)

    if entropy_confirms and coverage_confirms:
        print("\n>>> HYPOTHESIS CONFIRMED: Exclusive MIDDLEs are more AZC-concentrated <<<")
        verdict = "CONFIRMED"
    elif entropy_confirms or coverage_confirms:
        print("\n>>> HYPOTHESIS PARTIALLY CONFIRMED <<<")
        verdict = "PARTIAL"
    else:
        print("\n>>> HYPOTHESIS NOT CONFIRMED <<<")
        verdict = "NOT_CONFIRMED"

    # Save results
    output = {
        'probe': 'MIDDLE_AZC_EXCLUSIVITY',
        'middle_info': {
            'exclusive_count': middle_info['exclusive_count'],
            'shared_count': middle_info['shared_count']
        },
        'aggregate': agg,
        'entropy_diff': entropy_diff,
        'coverage_diff': coverage_diff,
        'verdict': verdict
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
