"""
Gloss Injectivity Audit
=======================

Tests whether the auto-composed gloss system preserves behavioral distinctions.

A gloss is "injective" if no two tokens with significantly different behavior
share the same rendered string. This script:

1. Collects all Currier B tokens and their interpretive() glosses
2. Groups by gloss string to find collisions
3. For each collision group, computes behavioral variance using:
   - Instruction class membership
   - Kernel profile (middle_kernel)
   - Regime (middle_regime)
   - Prefix role
4. Flags groups with high behavioral variance as needing signature splits
5. Reports collision stats (before/after comparison possible)

Usage:
    python scripts/gloss_injectivity_audit.py
    python scripts/gloss_injectivity_audit.py --top 50     # Show top 50 collisions
    python scripts/gloss_injectivity_audit.py --verbose     # Show all collision members
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.voynich import BFolioDecoder, Transcript


def audit_glosses(top_n=30, verbose=False):
    dec = BFolioDecoder()
    tx = Transcript()

    # Collect unique tokens and their analyses
    token_data = {}  # word -> {gloss, middle_kernel, middle_regime, prefix_role, ...}
    word_counts = Counter()

    for token in tx.currier_b():
        if '*' in token.word or not token.word.strip():
            continue
        word = token.word
        word_counts[word] += 1
        if word in token_data:
            continue

        analysis = dec.analyze_token(word)
        token_data[word] = {
            'gloss': analysis.interpretive(),
            'middle_kernel': analysis.middle_kernel,
            'middle_regime': analysis.middle_regime,
            'middle_section': analysis.middle_section,
            'prefix_role': analysis.prefix_role,
            'suffix_role': analysis.suffix_role,
            'kernels': tuple(sorted(analysis.kernels)),
            'is_ht': analysis.is_ht,
            'is_fl_role': analysis.is_fl_role,
            'middle': analysis.morph.middle if analysis.morph else None,
            'prefix': analysis.morph.prefix if analysis.morph else None,
            'suffix': analysis.morph.suffix if analysis.morph else None,
        }

    # Group by gloss
    gloss_groups = defaultdict(list)
    for word, data in token_data.items():
        gloss_groups[data['gloss']].append(word)

    # Identify collisions
    collisions = {g: words for g, words in gloss_groups.items() if len(words) > 1}
    collision_words = sum(len(w) for w in collisions.values())
    total_words = len(token_data)
    total_glosses = len(gloss_groups)

    # Compute behavioral variance for each collision group
    collision_analysis = []
    for gloss, words in collisions.items():
        group_data = [token_data[w] for w in words]

        # Count distinct values per dimension
        kernels = set(d['middle_kernel'] for d in group_data if d['middle_kernel'])
        regimes = set(d['middle_regime'] for d in group_data if d['middle_regime'])
        prefix_roles = set(d['prefix_role'] for d in group_data if d['prefix_role'])
        middles = set(d['middle'] for d in group_data if d['middle'])
        suffixes = set(d['suffix'] for d in group_data if d['suffix'])
        kernel_tuples = set(d['kernels'] for d in group_data)

        # Behavioral variance score: how many dimensions differ?
        variance = 0
        if len(kernels) > 1:
            variance += 2  # kernel divergence is high-weight
        if len(regimes) > 1:
            variance += 1
        if len(prefix_roles) > 1:
            variance += 1
        if len(middles) > 1:
            variance += 1
        if len(kernel_tuples) > 1:
            variance += 1

        # Token frequency weight
        total_freq = sum(word_counts[w] for w in words)

        collision_analysis.append({
            'gloss': gloss,
            'words': words,
            'n_words': len(words),
            'total_freq': total_freq,
            'variance': variance,
            'distinct_kernels': kernels,
            'distinct_regimes': regimes,
            'distinct_prefix_roles': prefix_roles,
            'distinct_middles': middles,
            'distinct_suffixes': suffixes,
            'is_ht': all(d['is_ht'] for d in group_data),
        })

    # Sort by variance * frequency (worst offenders first)
    collision_analysis.sort(key=lambda x: -(x['variance'] * x['total_freq']))

    # Report
    print("=" * 70)
    print("GLOSS INJECTIVITY AUDIT")
    print("=" * 70)
    print(f"  Unique words analyzed:     {total_words:,}")
    print(f"  Unique glosses produced:   {total_glosses:,}")
    print(f"  Collision glosses (2+):    {len(collisions):,}")
    print(f"  Words in collisions:       {collision_words:,}")
    print(f"  Collision rate:            {collision_words / total_words:.1%}")
    print(f"  Injection ratio:           {total_glosses / total_words:.3f}")
    print()

    # HT vs non-HT breakdown
    ht_collisions = [c for c in collision_analysis if c['is_ht']]
    non_ht_collisions = [c for c in collision_analysis if not c['is_ht']]
    ht_collision_words = sum(c['n_words'] for c in ht_collisions)
    non_ht_collision_words = sum(c['n_words'] for c in non_ht_collisions)

    ht_total = sum(1 for d in token_data.values() if d['is_ht'])
    non_ht_total = total_words - ht_total

    print(f"  HT tokens:   {ht_total:,} total, {ht_collision_words:,} in collisions "
          f"({ht_collision_words / max(ht_total, 1):.1%})")
    print(f"  Non-HT:      {non_ht_total:,} total, {non_ht_collision_words:,} in collisions "
          f"({non_ht_collision_words / max(non_ht_total, 1):.1%})")
    print()

    # High-variance collisions (behavioral divergence within same gloss)
    high_var = [c for c in collision_analysis if c['variance'] >= 2]
    print(f"  HIGH-VARIANCE collisions (variance >= 2): {len(high_var)}")
    print(f"  Words in high-variance groups: "
          f"{sum(c['n_words'] for c in high_var)}")
    print()

    # Top collisions
    print(f"Top {top_n} collision groups (by variance * frequency):")
    print("-" * 70)
    for i, c in enumerate(collision_analysis[:top_n]):
        var_bar = "*" * c['variance']
        ht_tag = " [HT]" if c['is_ht'] else ""
        print(f"  {i+1:3d}. [{c['n_words']:2d} words, {c['total_freq']:4d} occ, "
              f"var={c['variance']}] {c['gloss'][:50]}{ht_tag}")

        # Show divergence dimensions
        if c['distinct_kernels']:
            print(f"       kernels: {c['distinct_kernels']}")
        if c['distinct_regimes']:
            print(f"       regimes: {c['distinct_regimes']}")
        if len(c['distinct_prefix_roles']) > 1:
            print(f"       prefix_roles: {c['distinct_prefix_roles']}")

        if verbose or c['n_words'] <= 6:
            for w in c['words'][:8]:
                d = token_data[w]
                print(f"       {w:20s}  mk={str(d['middle_kernel']):5s} "
                      f"mr={str(d['middle_regime']):12s} "
                      f"mid={str(d['middle']):8s} "
                      f"pr={str(d['prefix_role'])}")
            if c['n_words'] > 8:
                print(f"       ... and {c['n_words'] - 8} more")
        print()

    # Summary stats by variance level
    print("=" * 70)
    print("VARIANCE DISTRIBUTION")
    print("-" * 70)
    var_dist = Counter(c['variance'] for c in collision_analysis)
    for v in sorted(var_dist.keys()):
        groups = [c for c in collision_analysis if c['variance'] == v]
        words = sum(c['n_words'] for c in groups)
        print(f"  variance={v}: {var_dist[v]:3d} groups, {words:4d} words")

    return {
        'total_words': total_words,
        'total_glosses': total_glosses,
        'collision_glosses': len(collisions),
        'collision_words': collision_words,
        'collision_rate': collision_words / total_words,
        'ht_collision_words': ht_collision_words,
        'non_ht_collision_words': non_ht_collision_words,
        'high_variance_groups': len(high_var),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gloss Injectivity Audit')
    parser.add_argument('--top', type=int, default=30, help='Show top N collisions')
    parser.add_argument('--verbose', action='store_true', help='Show all collision members')
    args = parser.parse_args()

    audit_glosses(top_n=args.top, verbose=args.verbose)
