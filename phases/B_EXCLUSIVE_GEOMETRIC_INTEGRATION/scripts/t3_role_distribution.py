#!/usr/bin/env python3
"""
T3: Role Distribution
B_EXCLUSIVE_GEOMETRIC_INTEGRATION phase

Classify B-exclusive MIDDLEs by frequency, morphological complexity,
sub-component overlap, and compound status. Confirm C792/C610/C618 predictions.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


def get_a_middles():
    tx = Transcript()
    morph = Morphology()
    a_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            a_set.add(m.middle)
    return a_set


def main():
    print("=" * 60)
    print("T3: Role Distribution")
    print("=" * 60)

    # Setup
    print("\n[1] Building inventories...")
    a_set = get_a_middles()
    tx = Transcript()
    morph = Morphology()

    # Collect B MIDDLE data
    b_mid_counts = Counter()
    b_mid_folios = defaultdict(set)
    b_mid_lines = defaultdict(set)
    b_token_prefixes = defaultdict(Counter)  # MIDDLE -> prefix distribution

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            b_mid_counts[m.middle] += 1
            b_mid_folios[m.middle].add(token.folio)
            b_mid_lines[m.middle].add((token.folio, token.line))
            if m.prefix:
                b_token_prefixes[m.middle][m.prefix] += 1

    all_b = set(b_mid_counts.keys())
    shared = all_b & a_set
    exclusive = all_b - a_set

    print(f"  B MIDDLEs: {len(all_b)} (shared: {len(shared)}, exclusive: {len(exclusive)})")

    # Build MiddleAnalyzer for atom detection
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # Step 2: Frequency distribution
    print("\n[2] Frequency distribution...")
    exc_counts = sorted([b_mid_counts[m] for m in exclusive], reverse=True)
    sha_counts = sorted([b_mid_counts[m] for m in shared], reverse=True)

    freq_bins = [(1, 1), (2, 2), (3, 5), (6, 10), (11, 50), (51, 100), (101, 10000)]
    freq_labels = ['1', '2', '3-5', '6-10', '11-50', '51-100', '101+']

    print(f"  {'Freq':>8s} {'Exclusive':>10s} {'Shared':>10s}")
    exc_freq_dist = {}
    sha_freq_dist = {}
    for (lo, hi), label in zip(freq_bins, freq_labels):
        n_exc = sum(1 for c in exc_counts if lo <= c <= hi)
        n_sha = sum(1 for c in sha_counts if lo <= c <= hi)
        exc_freq_dist[label] = n_exc
        sha_freq_dist[label] = n_sha
        print(f"  {label:>8s} {n_exc:>10d} {n_sha:>10d}")

    # Hapax (count=1)
    exc_hapax = sum(1 for m in exclusive if b_mid_counts[m] == 1)
    sha_hapax = sum(1 for m in shared if b_mid_counts[m] == 1)
    print(f"\n  Hapax legomena: exclusive={exc_hapax} ({exc_hapax/len(exclusive):.1%}), "
          f"shared={sha_hapax} ({sha_hapax/len(shared):.1%})")

    # Step 3: Length distribution
    print("\n[3] Length distribution...")
    exc_lens = [len(m) for m in exclusive]
    sha_lens = [len(m) for m in shared]

    len_bins = range(1, max(max(exc_lens), max(sha_lens)) + 2)
    print(f"  {'Len':>4s} {'Exclusive':>10s} {'Shared':>10s}")
    for l in range(1, 10):
        n_exc = sum(1 for x in exc_lens if x == l)
        n_sha = sum(1 for x in sha_lens if x == l)
        if n_exc + n_sha > 0:
            print(f"  {l:>4d} {n_exc:>10d} {n_sha:>10d}")
    n_exc_long = sum(1 for x in exc_lens if x >= 10)
    n_sha_long = sum(1 for x in sha_lens if x >= 10)
    if n_exc_long + n_sha_long > 0:
        print(f"  {'10+':>4s} {n_exc_long:>10d} {n_sha_long:>10d}")

    print(f"\n  Mean length: exclusive={np.mean(exc_lens):.1f}, shared={np.mean(sha_lens):.1f}")

    # Step 4: Compound status
    print("\n[4] Compound MIDDLE analysis...")
    # Use A-space MIDDLEs as atoms (build from A)
    a_core = {m for m in a_set if len(m) <= 3}

    exc_compound = 0
    exc_atoms_found = []
    for m in exclusive:
        atoms = [a for a in a_core if a in m and a != m and len(a) >= 2]
        if atoms:
            exc_compound += 1
            exc_atoms_found.append(len(atoms))
        else:
            exc_atoms_found.append(0)

    sha_compound = 0
    for m in shared:
        atoms = [a for a in a_core if a in m and a != m and len(a) >= 2]
        if atoms:
            sha_compound += 1

    exc_compound_rate = exc_compound / len(exclusive)
    sha_compound_rate = sha_compound / len(shared)
    print(f"  Exclusive compound rate: {exc_compound}/{len(exclusive)} ({exc_compound_rate:.1%})")
    print(f"  Shared compound rate: {sha_compound}/{len(shared)} ({sha_compound_rate:.1%})")
    print(f"  C610 prediction: 90.7% of UN MIDDLEs contain PP atoms")

    # Step 5: Folio spread
    print("\n[5] Folio spread distribution...")
    exc_folio_counts = [len(b_mid_folios[m]) for m in exclusive]
    sha_folio_counts = [len(b_mid_folios[m]) for m in shared]

    exc_single_folio = sum(1 for c in exc_folio_counts if c == 1)
    sha_single_folio = sum(1 for c in sha_folio_counts if c == 1)

    print(f"  Single-folio: exclusive={exc_single_folio} ({exc_single_folio/len(exclusive):.1%}), "
          f"shared={sha_single_folio} ({sha_single_folio/len(shared):.1%})")
    print(f"  Mean folios: exclusive={np.mean(exc_folio_counts):.1f}, "
          f"shared={np.mean(sha_folio_counts):.1f}")

    # Step 6: Prefix distribution — what operations use exclusive MIDDLEs?
    print("\n[6] Prefix distribution of B-exclusive MIDDLEs...")
    exc_prefix_total = Counter()
    for m in exclusive:
        for prefix, count in b_token_prefixes[m].items():
            exc_prefix_total[prefix] += count

    sha_prefix_total = Counter()
    for m in shared:
        for prefix, count in b_token_prefixes[m].items():
            sha_prefix_total[prefix] += count

    print(f"  Top exclusive prefixes:")
    for prefix, count in exc_prefix_total.most_common(10):
        print(f"    {prefix:>6s}: {count:>5d}")

    print(f"\n  Top shared prefixes:")
    for prefix, count in sha_prefix_total.most_common(10):
        print(f"    {prefix:>6s}: {count:>5d}")

    # Verdict
    print("\n" + "=" * 60)

    is_rare = np.median([b_mid_counts[m] for m in exclusive]) <= 2
    is_long = np.mean(exc_lens) > np.mean(sha_lens)
    is_compound = exc_compound_rate > 0.70
    is_folio_specific = exc_single_folio / len(exclusive) > 0.50

    if is_rare and is_compound and is_folio_specific:
        verdict = "MORPHOLOGICAL_TAIL"
        explanation = (
            f"B-exclusive MIDDLEs are rare (median count={np.median([b_mid_counts[m] for m in exclusive]):.0f}), "
            f"compound ({exc_compound_rate:.0%} contain A atoms), "
            f"and folio-specific ({exc_single_folio/len(exclusive):.0%} single-folio). "
            f"They are the morphological periphery, not an independent system."
        )
    elif is_rare and is_compound:
        verdict = "ELABORATION_TAIL"
        explanation = (
            f"Rare and compound but not maximally folio-specific. "
            f"Elaboration of A vocabulary, not independent."
        )
    elif is_compound:
        verdict = "COMPOUND_EXTENSION"
        explanation = (
            f"Compound ({exc_compound_rate:.0%}) but not necessarily rare. "
            f"Productive compounding beyond A's inventory."
        )
    else:
        verdict = "POTENTIALLY_INDEPENDENT"
        explanation = (
            f"Only {exc_compound_rate:.0%} contain A atoms. "
            f"Substantial novel vocabulary."
        )

    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")

    results = {
        'test': 'T3_role_distribution',
        'n_exclusive': len(exclusive),
        'n_shared': len(shared),
        'frequency': {
            'exclusive_dist': exc_freq_dist,
            'shared_dist': sha_freq_dist,
            'exclusive_median': float(np.median([b_mid_counts[m] for m in exclusive])),
            'shared_median': float(np.median([b_mid_counts[m] for m in shared])),
            'exclusive_hapax_rate': float(exc_hapax / len(exclusive)),
        },
        'length': {
            'exclusive_mean': float(np.mean(exc_lens)),
            'shared_mean': float(np.mean(sha_lens)),
        },
        'compound': {
            'exclusive_rate': float(exc_compound_rate),
            'shared_rate': float(sha_compound_rate),
        },
        'folio_spread': {
            'exclusive_single_folio_rate': float(exc_single_folio / len(exclusive)),
            'shared_single_folio_rate': float(sha_single_folio / len(shared)),
            'exclusive_mean_folios': float(np.mean(exc_folio_counts)),
            'shared_mean_folios': float(np.mean(sha_folio_counts)),
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 't3_role_distribution.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_DIR / 't3_role_distribution.json'}")


if __name__ == '__main__':
    main()
