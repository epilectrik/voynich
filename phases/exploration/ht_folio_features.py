#!/usr/bin/env python3
"""
HT-THREAD Phase 1: Per-Folio HT Feature Table

Builds comprehensive HT metrics for EVERY folio in the manuscript,
not just Currier B. This is the foundation for global threading analysis.

HT Definition: Tokens with HT-specific prefixes (disjoint from A/B prefixes).
Per context/ARCHITECTURE/human_track.md and archive/scripts/full_token_audit.py
"""

import json
import csv
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

BASE = Path(__file__).parent.parent.parent
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
RESULTS = BASE / "results"

# HT-specific prefixes (disjoint from A/B grammar)
# Source: context/ARCHITECTURE/human_track.md, C347
HT_PREFIXES = {
    'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc',
    'do', 'ta', 'ke', 'al', 'po', 'ko', 'yd', 'ysh',
    'ych', 'kch', 'ks'
}

# A/B prefixes (for comparison)
AB_PREFIXES = {'ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol'}

# HT suffixes (common)
HT_SUFFIXES = {'-dy', '-in', '-ey', '-ar', '-hy', '-y', '-iin', '-aiin'}

def is_ht_token(token):
    """
    Classify if a token belongs to HT layer.

    Per C347: HT has disjoint prefix vocabulary from A/B.
    A token is HT if it starts with an HT prefix.
    """
    if not token or len(token) < 2:
        return False

    # Check if starts with HT prefix
    for prefix in sorted(HT_PREFIXES, key=len, reverse=True):
        if token.startswith(prefix):
            return True

    return False

def get_ht_prefix(token):
    """Extract HT prefix from token, or None if not HT."""
    if not token or len(token) < 2:
        return None

    for prefix in sorted(HT_PREFIXES, key=len, reverse=True):
        if token.startswith(prefix):
            return prefix

    return None

def get_ht_suffix(token):
    """Extract suffix from HT token."""
    if not token or len(token) < 2:
        return None

    for suffix in sorted(HT_SUFFIXES, key=len, reverse=True):
        if token.endswith(suffix.lstrip('-')):
            return suffix

    return None

def load_transcription():
    """Load and parse the interlinear transcription."""
    folios = defaultdict(lambda: {
        'tokens': [],
        'ht_tokens': [],
        'section': None,
        'quire': None,
        'language_counts': {'A': 0, 'B': 0, 'NA': 0},  # Count per language
        'line_positions': []  # (token, line_initial, line_final)
    })

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')

        for row in reader:
            folio = row.get('folio', '').strip('"')
            token = row.get('word', '').strip('"')
            section = row.get('section', '').strip('"')
            quire = row.get('quire', '').strip('"')
            language = row.get('language', '').strip('"')
            line_initial = row.get('line_initial', '').strip('"')
            line_final = row.get('line_final', '').strip('"')

            if not folio or not token:
                continue

            # Skip damaged tokens
            if '*' in token:
                continue

            folios[folio]['tokens'].append(token)

            if is_ht_token(token):
                folios[folio]['ht_tokens'].append(token)

            # Store metadata (use first non-empty value)
            if section and not folios[folio]['section']:
                folios[folio]['section'] = section
            if quire and not folios[folio]['quire']:
                folios[folio]['quire'] = quire

            # Count language occurrences
            if language == 'A':
                folios[folio]['language_counts']['A'] += 1
            elif language == 'B':
                folios[folio]['language_counts']['B'] += 1
            else:
                folios[folio]['language_counts']['NA'] += 1

            # Track line position
            try:
                is_initial = int(line_initial) == 1 if line_initial and line_initial != 'NA' else False
                is_final = int(line_final) == 1 if line_final and line_final != 'NA' else False
            except ValueError:
                is_initial = False
                is_final = False

            folios[folio]['line_positions'].append((token, is_initial, is_final))

    return folios

def classify_system_from_counts(language_counts):
    """
    Classify folio into A, B, or AZC system based on dominant language.

    Per C300: Tokens with NA in language column = AZC (unclassified by Currier)

    Classification rules:
    - If >50% NA tokens → AZC
    - If >50% A tokens → Currier A
    - If >50% B tokens → Currier B
    - Otherwise → Mixed (use dominant)
    """
    total = sum(language_counts.values())
    if total == 0:
        return 'UNKNOWN'

    a_rate = language_counts['A'] / total
    b_rate = language_counts['B'] / total
    na_rate = language_counts['NA'] / total

    # Majority classification
    if na_rate > 0.5:
        return 'AZC'
    elif a_rate > b_rate:
        return 'A'
    elif b_rate > a_rate:
        return 'B'
    else:
        # Equal A and B, check NA
        if na_rate > 0:
            return 'AZC'
        return 'MIXED'

def compute_folio_features(folio_data):
    """Compute HT features for a single folio."""
    tokens = folio_data['tokens']
    ht_tokens = folio_data['ht_tokens']
    line_positions = folio_data['line_positions']

    n_total = len(tokens)
    n_ht = len(ht_tokens)

    if n_total == 0:
        return None

    # Basic metrics
    ht_density = n_ht / n_total
    ht_unique_types = len(set(ht_tokens))
    ht_ttr = ht_unique_types / n_ht if n_ht > 0 else 0.0

    # HT prefix distribution
    prefix_counts = Counter()
    for t in ht_tokens:
        prefix = get_ht_prefix(t)
        if prefix:
            prefix_counts[prefix] += 1

    # Normalize to distribution
    prefix_dist = {}
    if n_ht > 0:
        for p in HT_PREFIXES:
            prefix_dist[p] = prefix_counts.get(p, 0) / n_ht

    # HT suffix distribution
    suffix_counts = Counter()
    for t in ht_tokens:
        suffix = get_ht_suffix(t)
        if suffix:
            suffix_counts[suffix] += 1

    # Line position analysis
    ht_at_initial = 0
    ht_at_final = 0
    for token, is_initial, is_final in line_positions:
        if is_ht_token(token):
            if is_initial:
                ht_at_initial += 1
            if is_final:
                ht_at_final += 1

    line_initial_rate = ht_at_initial / n_ht if n_ht > 0 else 0.0
    line_final_rate = ht_at_final / n_ht if n_ht > 0 else 0.0

    return {
        'n_tokens': n_total,
        'n_ht': n_ht,
        'ht_density': ht_density,
        'ht_unique_types': ht_unique_types,
        'ht_ttr': ht_ttr,
        'ht_prefix_dist': prefix_dist,
        'ht_suffix_counts': dict(suffix_counts),
        'line_initial_rate': line_initial_rate,
        'line_final_rate': line_final_rate
    }

def main():
    print("=" * 70)
    print("HT-THREAD Phase 1: Per-Folio HT Feature Table")
    print("=" * 70)

    # Load transcription
    print("\n[1] Loading transcription...")
    folios = load_transcription()
    print(f"    Loaded {len(folios)} folios")

    # Compute features for each folio
    print("\n[2] Computing HT features per folio...")
    features = {}

    for folio in sorted(folios.keys()):
        data = folios[folio]
        feat = compute_folio_features(data)

        if feat is None:
            continue

        # Add metadata
        feat['section'] = data['section']
        feat['quire'] = data['quire']
        feat['language_counts'] = data['language_counts']
        feat['system'] = classify_system_from_counts(data['language_counts'])

        features[folio] = feat

    print(f"    Computed features for {len(features)} folios")

    # Summary statistics
    print("\n[3] Summary statistics...")

    # By system
    system_stats = defaultdict(lambda: {'count': 0, 'ht_density': []})
    for folio, feat in features.items():
        sys = feat['system']
        system_stats[sys]['count'] += 1
        system_stats[sys]['ht_density'].append(feat['ht_density'])

    print("\n    HT Density by System:")
    print("    " + "-" * 50)
    for sys in ['A', 'B', 'AZC']:
        if system_stats[sys]['count'] > 0:
            densities = system_stats[sys]['ht_density']
            mean_d = np.mean(densities)
            std_d = np.std(densities)
            print(f"    {sys:5s}: n={system_stats[sys]['count']:3d}, mean={mean_d:.3f}, std={std_d:.3f}")

    # By quire
    quire_stats = defaultdict(list)
    for folio, feat in features.items():
        quire = feat['quire']
        if quire:
            quire_stats[quire].append(feat['ht_density'])

    print("\n    HT Density by Quire (top 10 by count):")
    print("    " + "-" * 50)
    sorted_quires = sorted(quire_stats.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for quire, densities in sorted_quires:
        mean_d = np.mean(densities)
        print(f"    Quire {quire:3s}: n={len(densities):3d}, mean={mean_d:.3f}")

    # HT prefix usage
    print("\n    Global HT Prefix Usage (top 10):")
    print("    " + "-" * 50)
    global_prefix_counts = Counter()
    for folio, feat in features.items():
        for prefix, rate in feat['ht_prefix_dist'].items():
            global_prefix_counts[prefix] += feat['n_ht'] * rate

    for prefix, count in global_prefix_counts.most_common(10):
        print(f"    {prefix:5s}: {int(count):5d}")

    # Outlier detection (extreme HT density)
    all_densities = [f['ht_density'] for f in features.values()]
    mean_ht = np.mean(all_densities)
    std_ht = np.std(all_densities)

    print(f"\n    Global HT density: mean={mean_ht:.3f}, std={std_ht:.3f}")

    high_ht = [(f, features[f]['ht_density']) for f in features
               if features[f]['ht_density'] > mean_ht + 2*std_ht]
    low_ht = [(f, features[f]['ht_density']) for f in features
              if features[f]['ht_density'] < mean_ht - 2*std_ht]

    if high_ht:
        print(f"\n    High HT outliers (>2 std):")
        for folio, density in sorted(high_ht, key=lambda x: -x[1])[:5]:
            print(f"      {folio}: {density:.3f} ({features[folio]['system']})")

    if low_ht:
        print(f"\n    Low HT outliers (<2 std):")
        for folio, density in sorted(low_ht, key=lambda x: x[1])[:5]:
            print(f"      {folio}: {density:.3f} ({features[folio]['system']})")

    # Save results
    output = {
        'metadata': {
            'analysis': 'HT-THREAD Phase 1',
            'description': 'Per-folio HT features for global threading analysis',
            'n_folios': len(features),
            'ht_prefixes': list(HT_PREFIXES)
        },
        'summary': {
            'global_mean_ht_density': float(mean_ht),
            'global_std_ht_density': float(std_ht),
            'by_system': {
                sys: {
                    'count': stats['count'],
                    'mean_ht_density': float(np.mean(stats['ht_density'])) if stats['ht_density'] else 0,
                    'std_ht_density': float(np.std(stats['ht_density'])) if stats['ht_density'] else 0
                }
                for sys, stats in system_stats.items()
            }
        },
        'folios': features
    }

    output_path = RESULTS / "ht_folio_features.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n[SAVED] {output_path}")
    print("\n" + "=" * 70)
    print("Phase 1 complete. Ready for Phase 2: Distribution Analysis")
    print("=" * 70)

    return output

if __name__ == "__main__":
    main()
