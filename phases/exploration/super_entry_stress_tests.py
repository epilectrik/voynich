#!/usr/bin/env python
"""
C424 Stress Tests

Critical tests to determine if bimodal adjacency is:
- Genuine higher-order structure (-> mint C424)
- Variant pairing / copy proximity (-> refine C346.a)

Tests:
1. Section-controlled null model (REQUIRED)
2. Scale-invariance (multiple similarity metrics)
3. Cluster-size stability (size-2 collapse check)
"""
import sys
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
import random

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import MARKER_FAMILIES, A_UNIVERSAL_SUFFIXES, EXTENDED_PREFIX_MAP

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

# DA prefixes for filtering
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}


def load_currier_a_entries():
    """Load Currier A entries in sequential order."""
    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None:
                        entries.append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None:
            entries.append(current_entry)

    return entries


# =============================================================================
# SIMILARITY METRICS
# =============================================================================

def jaccard(set1, set2):
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def extract_prefix(token):
    """Extract marker prefix from token."""
    token_lower = token.lower()
    if len(token_lower) >= 3:
        prefix3 = token_lower[:3]
        if prefix3 in EXTENDED_PREFIX_MAP:
            return EXTENDED_PREFIX_MAP[prefix3]
    if len(token_lower) >= 2:
        prefix2 = token_lower[:2]
        if prefix2 in MARKER_FAMILIES:
            return prefix2
    return None


def extract_middle(token):
    """Extract middle component (strip prefix and suffix)."""
    token_lower = token.lower()

    # Strip prefix
    prefix_len = 0
    if len(token_lower) >= 3 and token_lower[:3] in EXTENDED_PREFIX_MAP:
        prefix_len = 3
    elif len(token_lower) >= 2 and token_lower[:2] in MARKER_FAMILIES:
        prefix_len = 2

    # Strip suffix
    suffix_len = 0
    for sl in range(min(5, len(token_lower) - prefix_len), 0, -1):
        if token_lower[-sl:] in A_UNIVERSAL_SUFFIXES:
            suffix_len = sl
            break

    if prefix_len + suffix_len < len(token_lower):
        return token_lower[prefix_len:-suffix_len] if suffix_len > 0 else token_lower[prefix_len:]
    return ''


def is_da(token):
    """Check if token is DA family."""
    token_lower = token.lower()
    if any(token_lower.startswith(p) for p in DA_PREFIXES):
        return True
    return False


# Multiple similarity representations
def token_jaccard(e1, e2):
    """Standard token-level Jaccard."""
    return jaccard(set(e1['tokens']), set(e2['tokens']))


def middle_only_jaccard(e1, e2):
    """MIDDLE-only Jaccard (strips prefix/suffix)."""
    m1 = set(extract_middle(t) for t in e1['tokens'] if extract_middle(t))
    m2 = set(extract_middle(t) for t in e2['tokens'] if extract_middle(t))
    return jaccard(m1, m2)


def token_minus_da_jaccard(e1, e2):
    """Token Jaccard excluding DA tokens."""
    t1 = set(t for t in e1['tokens'] if not is_da(t))
    t2 = set(t for t in e2['tokens'] if not is_da(t))
    return jaccard(t1, t2)


def prefix_stripped_jaccard(e1, e2):
    """Jaccard using tokens with prefix stripped."""
    def strip_prefix(t):
        tl = t.lower()
        if len(tl) >= 3 and tl[:3] in EXTENDED_PREFIX_MAP:
            return tl[3:]
        if len(tl) >= 2 and tl[:2] in MARKER_FAMILIES:
            return tl[2:]
        return tl

    s1 = set(strip_prefix(t) for t in e1['tokens'] if len(strip_prefix(t)) > 0)
    s2 = set(strip_prefix(t) for t in e2['tokens'] if len(strip_prefix(t)) > 0)
    return jaccard(s1, s2)


# =============================================================================
# TEST 1: SECTION-CONTROLLED NULL MODEL
# =============================================================================

def test_null_model(entries, n_permutations=100):
    """
    Null model: randomly permute entry order WITHIN each section,
    then measure adjacency statistics.

    If observed clustering is not stronger than null, bimodality is artifact.
    """
    print("\n" + "=" * 70)
    print("TEST 1: SECTION-CONTROLLED NULL MODEL")
    print("=" * 70)

    # Compute observed statistics
    observed_jaccards = []
    for i in range(len(entries) - 1):
        if entries[i]['section'] == entries[i+1]['section']:
            observed_jaccards.append(token_jaccard(entries[i], entries[i+1]))

    observed_jaccards = np.array(observed_jaccards)
    observed_zero_rate = np.mean(observed_jaccards == 0)
    observed_mean = np.mean(observed_jaccards)
    observed_autocorr = np.corrcoef(observed_jaccards[:-1], observed_jaccards[1:])[0, 1]

    print(f"\nObserved statistics:")
    print(f"  Zero-overlap rate: {100 * observed_zero_rate:.1f}%")
    print(f"  Mean Jaccard: {observed_mean:.4f}")
    print(f"  Autocorrelation (lag-1): {observed_autocorr:.4f}")

    # Group by section
    by_section = defaultdict(list)
    for e in entries:
        by_section[e['section']].append(e)

    # Generate null permutations
    null_zero_rates = []
    null_means = []
    null_autocorrs = []

    for _ in range(n_permutations):
        # Permute within sections
        permuted = []
        for section in sorted(by_section.keys()):
            sec_entries = by_section[section].copy()
            random.shuffle(sec_entries)
            permuted.extend(sec_entries)

        # Compute null adjacency
        null_jaccards = []
        for i in range(len(permuted) - 1):
            if permuted[i]['section'] == permuted[i+1]['section']:
                null_jaccards.append(token_jaccard(permuted[i], permuted[i+1]))

        null_jaccards = np.array(null_jaccards)
        null_zero_rates.append(np.mean(null_jaccards == 0))
        null_means.append(np.mean(null_jaccards))
        if len(null_jaccards) > 2:
            null_autocorrs.append(np.corrcoef(null_jaccards[:-1], null_jaccards[1:])[0, 1])

    # Compare
    print(f"\nNull model statistics (n={n_permutations} permutations):")
    print(f"  Zero-overlap rate: {100 * np.mean(null_zero_rates):.1f}% (std: {100 * np.std(null_zero_rates):.1f}%)")
    print(f"  Mean Jaccard: {np.mean(null_means):.4f} (std: {np.std(null_means):.4f})")
    print(f"  Autocorrelation: {np.mean(null_autocorrs):.4f} (std: {np.std(null_autocorrs):.4f})")

    # Statistical tests
    zero_rate_z = (observed_zero_rate - np.mean(null_zero_rates)) / np.std(null_zero_rates) if np.std(null_zero_rates) > 0 else 0
    mean_z = (observed_mean - np.mean(null_means)) / np.std(null_means) if np.std(null_means) > 0 else 0
    autocorr_z = (observed_autocorr - np.mean(null_autocorrs)) / np.std(null_autocorrs) if np.std(null_autocorrs) > 0 else 0

    print(f"\nDeviation from null (z-scores):")
    print(f"  Zero-overlap rate: z = {zero_rate_z:.2f} {'***' if abs(zero_rate_z) > 3 else '**' if abs(zero_rate_z) > 2 else '*' if abs(zero_rate_z) > 1.96 else ''}")
    print(f"  Mean Jaccard: z = {mean_z:.2f} {'***' if abs(mean_z) > 3 else '**' if abs(mean_z) > 2 else '*' if abs(mean_z) > 1.96 else ''}")
    print(f"  Autocorrelation: z = {autocorr_z:.2f} {'***' if abs(autocorr_z) > 3 else '**' if abs(autocorr_z) > 2 else '*' if abs(autocorr_z) > 1.96 else ''}")

    # Verdict
    print("\n--- VERDICT ---")
    if abs(autocorr_z) < 1.96 and abs(zero_rate_z) < 1.96:
        print("NULL MODEL EXPLAINS THE PATTERN")
        print("Bimodality is an artifact of section-isolated vocabulary + local pairing")
        print("-> C424 COLLAPSES to C346 refinement")
        return False
    else:
        print("OBSERVED EXCEEDS NULL MODEL")
        print(f"Autocorrelation z={autocorr_z:.2f} suggests genuine clustering beyond section isolation")
        return True


# =============================================================================
# TEST 2: SCALE-INVARIANCE
# =============================================================================

def test_scale_invariance(entries):
    """
    Test if bimodality persists across different similarity representations.
    """
    print("\n" + "=" * 70)
    print("TEST 2: SCALE-INVARIANCE (MULTIPLE REPRESENTATIONS)")
    print("=" * 70)

    metrics = {
        'token_jaccard': token_jaccard,
        'middle_only': middle_only_jaccard,
        'token_minus_da': token_minus_da_jaccard,
        'prefix_stripped': prefix_stripped_jaccard,
    }

    results = {}

    for name, metric_fn in metrics.items():
        jaccards = []
        for i in range(len(entries) - 1):
            if entries[i]['section'] == entries[i+1]['section']:
                jaccards.append(metric_fn(entries[i], entries[i+1]))

        jaccards = np.array(jaccards)
        zero_rate = np.mean(jaccards == 0)
        mean_j = np.mean(jaccards)

        # Autocorrelation
        if len(jaccards) > 2:
            autocorr = np.corrcoef(jaccards[:-1], jaccards[1:])[0, 1]
        else:
            autocorr = 0

        results[name] = {
            'zero_rate': zero_rate,
            'mean': mean_j,
            'autocorr': autocorr
        }

    print(f"\n{'Metric':<20} {'Zero Rate':<12} {'Mean J':<12} {'Autocorr':<12}")
    print("-" * 60)

    for name, data in results.items():
        print(f"{name:<20} {100*data['zero_rate']:<12.1f}% {data['mean']:<12.4f} {data['autocorr']:<12.4f}")

    # Check consistency
    autocorrs = [d['autocorr'] for d in results.values()]
    min_autocorr = min(autocorrs)
    max_autocorr = max(autocorrs)

    print(f"\nAutocorrelation range: {min_autocorr:.3f} to {max_autocorr:.3f}")

    if min_autocorr > 0.5:
        print("\n--- VERDICT ---")
        print("SCALE-INVARIANT: Clustering persists across all representations")
        print("-> Supports genuine structure")
        return True
    elif min_autocorr < 0.3:
        print("\n--- VERDICT ---")
        print("NOT SCALE-INVARIANT: Clustering collapses under some representations")
        print("-> Suggests artifact, not genuine structure")
        return False
    else:
        print("\n--- VERDICT ---")
        print("MIXED: Clustering partially persists")
        print("-> Needs careful interpretation")
        return None


# =============================================================================
# TEST 3: CLUSTER-SIZE DISTRIBUTION
# =============================================================================

def test_cluster_size_distribution(entries, threshold=0.0):
    """
    Analyze cluster size distribution.
    If clusters are ONLY size-2, this is variant pairing, not higher-order structure.
    """
    print("\n" + "=" * 70)
    print("TEST 3: CLUSTER-SIZE DISTRIBUTION")
    print("=" * 70)

    # Identify clusters (consecutive entries with J > threshold)
    clusters = []
    current_cluster = [0]

    for i in range(len(entries) - 1):
        if entries[i]['section'] != entries[i+1]['section']:
            # Section break - end cluster
            if len(current_cluster) >= 2:
                clusters.append(current_cluster)
            current_cluster = [i+1]
        else:
            j = token_jaccard(entries[i], entries[i+1])
            if j > threshold:
                current_cluster.append(i+1)
            else:
                if len(current_cluster) >= 2:
                    clusters.append(current_cluster)
                current_cluster = [i+1]

    if len(current_cluster) >= 2:
        clusters.append(current_cluster)

    # Analyze cluster sizes
    sizes = [len(c) for c in clusters]

    if not sizes:
        print("\nNo clusters found with threshold > 0")
        return False

    size_dist = Counter(sizes)

    print(f"\nTotal clusters found: {len(clusters)}")
    print(f"\nCluster size distribution:")
    for size in sorted(size_dist.keys()):
        count = size_dist[size]
        pct = 100 * count / len(clusters)
        bar = '#' * int(pct / 2)
        print(f"  Size {size}: {count:4d} ({pct:5.1f}%) {bar}")

    print(f"\nStatistics:")
    print(f"  Mean size: {np.mean(sizes):.2f}")
    print(f"  Median size: {np.median(sizes):.0f}")
    print(f"  Max size: {max(sizes)}")
    print(f"  Size-2 clusters: {100 * size_dist.get(2, 0) / len(clusters):.1f}%")
    print(f"  Size-3+ clusters: {100 * sum(c for s, c in size_dist.items() if s >= 3) / len(clusters):.1f}%")

    # Verdict
    print("\n--- VERDICT ---")
    size_2_rate = size_dist.get(2, 0) / len(clusters) if clusters else 0
    size_3plus_rate = sum(c for s, c in size_dist.items() if s >= 3) / len(clusters) if clusters else 0

    if size_2_rate > 0.8:
        print("CLUSTERS ARE DOMINATED BY PAIRS (size-2)")
        print("-> This is VARIANT PAIRING, not higher-order structure")
        print("-> C424 COLLAPSES to C346.a (pair-dominated adjacency)")
        return False
    elif size_3plus_rate > 0.3:
        print("SIGNIFICANT SIZE-3+ CLUSTERS EXIST")
        print("-> Genuine super-entry grouping detected")
        return True
    else:
        print("MIXED: Mostly pairs with occasional larger clusters")
        print("-> Likely variant pairing with some exceptions")
        return None


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("C424 STRESS TESTS")
    print("=" * 70)
    print("\nThese tests determine if bimodal adjacency is:")
    print("  - Genuine higher-order structure (-> mint C424)")
    print("  - Variant pairing / copy proximity (-> refine C346.a)")

    print("\nLoading entries...")
    entries = load_currier_a_entries()
    print(f"Loaded {len(entries)} entries")

    # Run tests
    null_passed = test_null_model(entries, n_permutations=100)
    scale_passed = test_scale_invariance(entries)
    cluster_passed = test_cluster_size_distribution(entries)

    # Final verdict
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    print(f"\nTest results:")
    print(f"  1. Null model test: {'PASSED' if null_passed else 'FAILED'}")
    print(f"  2. Scale-invariance: {'PASSED' if scale_passed else 'MIXED' if scale_passed is None else 'FAILED'}")
    print(f"  3. Cluster-size: {'PASSED' if cluster_passed else 'PAIR-DOMINATED' if cluster_passed is False else 'MIXED'}")

    passes = sum(1 for x in [null_passed, scale_passed, cluster_passed] if x is True)
    fails = sum(1 for x in [null_passed, scale_passed, cluster_passed] if x is False)

    print("\n" + "-" * 70)

    if passes >= 2 and fails == 0:
        print("RECOMMENDATION: MINT C424")
        print("Bimodal adjacency represents genuine higher-order structure.")
    elif fails >= 2:
        print("RECOMMENDATION: REFINE C346.a (do NOT mint C424)")
        print("Bimodality is variant pairing / local copy proximity.")
        print("\nProposed C346.a wording:")
        print("  'Adjacency coherence is pair-dominated: 69% of adjacent entries")
        print("   have zero overlap, while ~31% form variant pairs (size-2 clusters)'")
    else:
        print("RECOMMENDATION: INCONCLUSIVE - more investigation needed")
        print("Evidence is mixed; do not mint constraint yet.")


if __name__ == '__main__':
    main()
