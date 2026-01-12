#!/usr/bin/env python3
"""
F-AZC-004: Δ-Option-Space Compression Fit

Question: By how much does AZC reduce the operator's available option space compared to Currier A?

Method:
- Measure entropy / cardinality differences across:
  - PREFIX choices
  - MIDDLE universality (core vs tail access)
  - SUFFIX entropy
  - qo availability
- Compare: A baseline vs AZC-Z vs AZC-A/C

Success Criteria:
- Quantifiable entropy reduction (e.g., 30-50%)
- Strong suppression of escape logic (qo, ct)
- Preservation of infrastructure roles

Why This Matters:
Makes AZC's role quantifiable:
"AZC is a cognitive load reducer and legality sieve at transition zones."
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from math import log2
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token

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

# High-hazard prefixes (escape logic)
ESCAPE_PREFIXES = {'qo', 'ct'}


def load_universal_middles():
    """Load universal MIDDLE classification from prior analysis."""
    filepath = Path(__file__).parent.parent.parent / 'results' / 'middle_class_sharing.json'

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        universal_middles = set()
        for item in data.get('universal_analysis', {}).get('details', []):
            universal_middles.add(item['middle'])
        return universal_middles
    except FileNotFoundError:
        return set()


def load_tokens_by_system():
    """Load tokens for both Currier A and AZC with morphological decomposition."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    a_tokens = []
    azc_z_tokens = []
    azc_ac_tokens = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                currier = parts[6].strip('"').strip()
                token = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip()

                if not token:
                    continue

                result = decompose_token(token)
                if not result[0]:  # Couldn't decompose
                    continue

                prefix, middle, suffix = result

                token_data = {
                    'token': token,
                    'folio': folio,
                    'prefix': prefix,
                    'middle': middle,
                    'suffix': suffix
                }

                if currier == 'A':
                    a_tokens.append(token_data)
                elif currier == 'NA':  # AZC
                    if folio in ZODIAC_FAMILY:
                        azc_z_tokens.append(token_data)
                    elif folio in AC_FAMILY:
                        azc_ac_tokens.append(token_data)

    return a_tokens, azc_z_tokens, azc_ac_tokens


def calculate_entropy(counts):
    """Calculate Shannon entropy from count dict or list."""
    if isinstance(counts, dict):
        counts = list(counts.values())

    total = sum(counts)
    if total == 0:
        return 0.0

    entropy = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            entropy -= p * log2(p)
    return entropy


def calculate_option_metrics(tokens, label, universal_middles=None):
    """Calculate option space metrics for a token set."""

    prefix_counts = Counter(t['prefix'] for t in tokens)
    middle_counts = Counter(t['middle'] for t in tokens)
    suffix_counts = Counter(t['suffix'] for t in tokens)

    # Cardinality
    n_prefixes = len(prefix_counts)
    n_middles = len(middle_counts)
    n_suffixes = len(suffix_counts)
    n_types = len(set(t['token'] for t in tokens))

    # Entropy
    prefix_entropy = calculate_entropy(prefix_counts)
    middle_entropy = calculate_entropy(middle_counts)
    suffix_entropy = calculate_entropy(suffix_counts)

    # Escape prefix proportion
    total_tokens = len(tokens)
    escape_count = sum(1 for t in tokens if t['prefix'] in ESCAPE_PREFIXES)
    escape_pct = escape_count / total_tokens * 100 if total_tokens > 0 else 0

    # Universal MIDDLE proportion
    if universal_middles:
        universal_count = sum(1 for t in tokens if t['middle'] in universal_middles)
        universal_pct = universal_count / total_tokens * 100 if total_tokens > 0 else 0
    else:
        universal_pct = None

    return {
        'label': label,
        'n_tokens': total_tokens,
        'n_types': n_types,
        'type_token_ratio': n_types / total_tokens if total_tokens > 0 else 0,
        'cardinality': {
            'prefixes': n_prefixes,
            'middles': n_middles,
            'suffixes': n_suffixes
        },
        'entropy': {
            'prefix': prefix_entropy,
            'middle': middle_entropy,
            'suffix': suffix_entropy,
            'total': prefix_entropy + middle_entropy + suffix_entropy
        },
        'escape_pct': escape_pct,
        'universal_pct': universal_pct,
        'prefix_distribution': dict(prefix_counts.most_common(10)),
        'suffix_distribution': dict(suffix_counts.most_common(10))
    }


def calculate_compression(baseline, target, metric_path):
    """Calculate compression ratio (reduction) from baseline to target."""
    baseline_val = baseline
    target_val = target

    for key in metric_path:
        baseline_val = baseline_val[key]
        target_val = target_val[key]

    if baseline_val == 0:
        return None

    compression = (baseline_val - target_val) / baseline_val * 100
    return compression


def main():
    print("=" * 60)
    print("F-AZC-004: Option-Space Compression Fit")
    print("=" * 60)
    print()

    # Load data
    universal_middles = load_universal_middles()
    a_tokens, azc_z_tokens, azc_ac_tokens = load_tokens_by_system()

    print(f"Currier A tokens: {len(a_tokens)}")
    print(f"AZC Zodiac tokens: {len(azc_z_tokens)}")
    print(f"AZC A/C tokens: {len(azc_ac_tokens)}")
    print(f"Universal MIDDLEs loaded: {len(universal_middles)}")
    print()

    # Calculate metrics for each system
    a_metrics = calculate_option_metrics(a_tokens, 'Currier A', universal_middles)
    z_metrics = calculate_option_metrics(azc_z_tokens, 'AZC-Zodiac', universal_middles)
    ac_metrics = calculate_option_metrics(azc_ac_tokens, 'AZC-A/C', universal_middles)

    # Display results
    print("=" * 60)
    print("Option Space Metrics")
    print("=" * 60)
    print()

    print(f"{'Metric':<30} {'Currier A':>12} {'AZC-Z':>12} {'AZC-A/C':>12}")
    print("-" * 66)
    print(f"{'Tokens':<30} {a_metrics['n_tokens']:>12} {z_metrics['n_tokens']:>12} {ac_metrics['n_tokens']:>12}")
    print(f"{'Types':<30} {a_metrics['n_types']:>12} {z_metrics['n_types']:>12} {ac_metrics['n_types']:>12}")
    print(f"{'Type/Token Ratio':<30} {a_metrics['type_token_ratio']:>12.3f} {z_metrics['type_token_ratio']:>12.3f} {ac_metrics['type_token_ratio']:>12.3f}")
    print()
    print(f"{'PREFIX cardinality':<30} {a_metrics['cardinality']['prefixes']:>12} {z_metrics['cardinality']['prefixes']:>12} {ac_metrics['cardinality']['prefixes']:>12}")
    print(f"{'MIDDLE cardinality':<30} {a_metrics['cardinality']['middles']:>12} {z_metrics['cardinality']['middles']:>12} {ac_metrics['cardinality']['middles']:>12}")
    print(f"{'SUFFIX cardinality':<30} {a_metrics['cardinality']['suffixes']:>12} {z_metrics['cardinality']['suffixes']:>12} {ac_metrics['cardinality']['suffixes']:>12}")
    print()
    print(f"{'PREFIX entropy (bits)':<30} {a_metrics['entropy']['prefix']:>12.2f} {z_metrics['entropy']['prefix']:>12.2f} {ac_metrics['entropy']['prefix']:>12.2f}")
    print(f"{'MIDDLE entropy (bits)':<30} {a_metrics['entropy']['middle']:>12.2f} {z_metrics['entropy']['middle']:>12.2f} {ac_metrics['entropy']['middle']:>12.2f}")
    print(f"{'SUFFIX entropy (bits)':<30} {a_metrics['entropy']['suffix']:>12.2f} {z_metrics['entropy']['suffix']:>12.2f} {ac_metrics['entropy']['suffix']:>12.2f}")
    print(f"{'TOTAL entropy (bits)':<30} {a_metrics['entropy']['total']:>12.2f} {z_metrics['entropy']['total']:>12.2f} {ac_metrics['entropy']['total']:>12.2f}")
    print()
    print(f"{'Escape prefix % (qo, ct)':<30} {a_metrics['escape_pct']:>11.1f}% {z_metrics['escape_pct']:>11.1f}% {ac_metrics['escape_pct']:>11.1f}%")
    if a_metrics['universal_pct'] is not None:
        print(f"{'Universal MIDDLE %':<30} {a_metrics['universal_pct']:>11.1f}% {z_metrics['universal_pct']:>11.1f}% {ac_metrics['universal_pct']:>11.1f}%")
    print()

    # Compression calculations
    print("=" * 60)
    print("Compression Analysis (vs Currier A baseline)")
    print("=" * 60)
    print()

    compressions = {
        'zodiac': {},
        'ac': {}
    }

    # Total entropy compression
    z_total_comp = calculate_compression(a_metrics, z_metrics, ['entropy', 'total'])
    ac_total_comp = calculate_compression(a_metrics, ac_metrics, ['entropy', 'total'])

    print(f"{'Metric':<30} {'AZC-Z vs A':>15} {'AZC-A/C vs A':>15}")
    print("-" * 60)

    # Entropy compressions
    for metric in ['prefix', 'middle', 'suffix', 'total']:
        z_comp = calculate_compression(a_metrics, z_metrics, ['entropy', metric])
        ac_comp = calculate_compression(a_metrics, ac_metrics, ['entropy', metric])
        compressions['zodiac'][f'{metric}_entropy'] = z_comp
        compressions['ac'][f'{metric}_entropy'] = ac_comp
        z_str = f"{z_comp:+.1f}%" if z_comp is not None else "N/A"
        ac_str = f"{ac_comp:+.1f}%" if ac_comp is not None else "N/A"
        print(f"{metric.upper() + ' entropy':<30} {z_str:>15} {ac_str:>15}")

    print()

    # Escape suppression
    z_escape_supp = (a_metrics['escape_pct'] - z_metrics['escape_pct']) / a_metrics['escape_pct'] * 100 if a_metrics['escape_pct'] > 0 else None
    ac_escape_supp = (a_metrics['escape_pct'] - ac_metrics['escape_pct']) / a_metrics['escape_pct'] * 100 if a_metrics['escape_pct'] > 0 else None

    compressions['zodiac']['escape_suppression'] = z_escape_supp
    compressions['ac']['escape_suppression'] = ac_escape_supp

    z_str = f"{z_escape_supp:+.1f}%" if z_escape_supp is not None else "N/A"
    ac_str = f"{ac_escape_supp:+.1f}%" if ac_escape_supp is not None else "N/A"
    print(f"{'Escape prefix suppression':<30} {z_str:>15} {ac_str:>15}")

    # Universal enrichment
    if a_metrics['universal_pct'] is not None:
        z_univ_enrich = z_metrics['universal_pct'] - a_metrics['universal_pct']
        ac_univ_enrich = ac_metrics['universal_pct'] - a_metrics['universal_pct']
        compressions['zodiac']['universal_enrichment'] = z_univ_enrich
        compressions['ac']['universal_enrichment'] = ac_univ_enrich
        print(f"{'Universal MIDDLE enrichment':<30} {z_univ_enrich:>+14.1f}pp {ac_univ_enrich:>+14.1f}pp")

    print()

    # Interpretation
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()

    # Check success criteria
    significant_compression = (z_total_comp is not None and z_total_comp > 20) or (ac_total_comp is not None and ac_total_comp > 20)
    strong_escape_suppression = (z_escape_supp is not None and z_escape_supp > 50) or (ac_escape_supp is not None and ac_escape_supp > 50)
    universal_preserved = (a_metrics['universal_pct'] is not None and
                           z_metrics['universal_pct'] >= a_metrics['universal_pct'] * 0.8 and
                           ac_metrics['universal_pct'] >= a_metrics['universal_pct'] * 0.8)

    success_count = sum([significant_compression, strong_escape_suppression, universal_preserved])

    print(f"Success criteria met: {success_count}/3")
    print(f"  - Significant entropy compression (>20%): {'YES' if significant_compression else 'NO'}")
    print(f"  - Strong escape suppression (>50%): {'YES' if strong_escape_suppression else 'NO'}")
    print(f"  - Universal MIDDLEs preserved (>80%): {'YES' if universal_preserved else 'NO'}")
    print()

    if success_count >= 2:
        interpretation = "AZC is a COGNITIVE LOAD REDUCER and LEGALITY SIEVE at transition zones"
        fit_tier = "F2"
    elif success_count == 1:
        interpretation = "AZC shows PARTIAL option space compression"
        fit_tier = "F3"
    else:
        interpretation = "AZC does NOT significantly compress option space"
        fit_tier = "F4"

    print(f"Finding: {interpretation}")
    print(f"Fit tier: {fit_tier}")
    print()

    # Key insight
    print("KEY INSIGHT:")
    if z_escape_supp is not None and z_escape_supp > 50:
        print(f"  Zodiac suppresses escape logic by {z_escape_supp:.0f}%")
    if ac_escape_supp is not None and ac_escape_supp > 50:
        print(f"  A/C suppresses escape logic by {ac_escape_supp:.0f}%")
    if z_total_comp is not None:
        if z_total_comp > 0:
            print(f"  Zodiac compresses total entropy by {z_total_comp:.1f}%")
        else:
            print(f"  Zodiac EXPANDS total entropy by {-z_total_comp:.1f}%")
    if ac_total_comp is not None:
        if ac_total_comp > 0:
            print(f"  A/C compresses total entropy by {ac_total_comp:.1f}%")
        else:
            print(f"  A/C EXPANDS total entropy by {-ac_total_comp:.1f}%")

    # Prepare output
    output = {
        'fit_id': 'F-AZC-004',
        'question': 'By how much does AZC reduce the operators available option space vs Currier A?',
        'metadata': {
            'a_tokens': len(a_tokens),
            'azc_z_tokens': len(azc_z_tokens),
            'azc_ac_tokens': len(azc_ac_tokens),
            'universal_middles': len(universal_middles)
        },
        'metrics': {
            'currier_a': {
                'n_tokens': a_metrics['n_tokens'],
                'n_types': a_metrics['n_types'],
                'type_token_ratio': round(a_metrics['type_token_ratio'], 4),
                'cardinality': a_metrics['cardinality'],
                'entropy': {k: round(v, 3) for k, v in a_metrics['entropy'].items()},
                'escape_pct': round(a_metrics['escape_pct'], 2),
                'universal_pct': round(a_metrics['universal_pct'], 2) if a_metrics['universal_pct'] else None
            },
            'azc_zodiac': {
                'n_tokens': z_metrics['n_tokens'],
                'n_types': z_metrics['n_types'],
                'type_token_ratio': round(z_metrics['type_token_ratio'], 4),
                'cardinality': z_metrics['cardinality'],
                'entropy': {k: round(v, 3) for k, v in z_metrics['entropy'].items()},
                'escape_pct': round(z_metrics['escape_pct'], 2),
                'universal_pct': round(z_metrics['universal_pct'], 2) if z_metrics['universal_pct'] else None
            },
            'azc_ac': {
                'n_tokens': ac_metrics['n_tokens'],
                'n_types': ac_metrics['n_types'],
                'type_token_ratio': round(ac_metrics['type_token_ratio'], 4),
                'cardinality': ac_metrics['cardinality'],
                'entropy': {k: round(v, 3) for k, v in ac_metrics['entropy'].items()},
                'escape_pct': round(ac_metrics['escape_pct'], 2),
                'universal_pct': round(ac_metrics['universal_pct'], 2) if ac_metrics['universal_pct'] else None
            }
        },
        'compression': {
            'zodiac_vs_a': {k: round(v, 2) if v is not None else None for k, v in compressions['zodiac'].items()},
            'ac_vs_a': {k: round(v, 2) if v is not None else None for k, v in compressions['ac'].items()}
        },
        'success_criteria': {
            'significant_compression': significant_compression,
            'strong_escape_suppression': strong_escape_suppression,
            'universal_preserved': universal_preserved,
            'met_count': success_count,
            'total': 3
        },
        'interpretation': {
            'finding': interpretation,
            'fit_tier': fit_tier
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_option_compression.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
