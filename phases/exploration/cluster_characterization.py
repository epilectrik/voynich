#!/usr/bin/env python
"""
Cluster Characterization Analysis

Given C424 (Clustered Adjacency), compare structural properties of:
- CLUSTERED entries (31% that appear in vocabulary-sharing runs)
- SINGLETON entries (69% with zero overlap to neighbors)

Research Questions:
1. Do clustered entries differ structurally from singletons?
2. Is block repetition (C250) enriched or depleted in clusters?
3. Do clusters show more or less prefix diversity?
4. Are rare MIDDLEs enriched in clusters or singletons?
5. Do first-in-run entries differ from last-in-run entries?

Hard Boundary: All analyses treat clusters as statistical phenomena in ordering,
NOT as entities with identity or semantics.
"""
import sys
from collections import defaultdict, Counter
from enum import Enum
import numpy as np
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import MARKER_FAMILIES, A_UNIVERSAL_SUFFIXES, EXTENDED_PREFIX_MAP

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'

# DA prefixes for filtering
DA_PREFIXES = {'da', 'dal', 'dam', 'dan', 'dar'}


class EntryClass(Enum):
    SINGLETON = "SINGLETON"
    RUN_START = "RUN_START"
    RUN_INTERNAL = "RUN_INTERNAL"
    RUN_END = "RUN_END"


# =============================================================================
# DATA LOADING (reused from super_entry_grouping.py)
# =============================================================================

def load_currier_a_entries():
    """Load Currier A entries in sequential order."""
    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
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
# SIMILARITY METRICS (reused from stress_tests.py)
# =============================================================================

def jaccard(set1, set2):
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def token_jaccard(e1, e2):
    return jaccard(set(e1['tokens']), set(e2['tokens']))


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
    return any(token_lower.startswith(p) for p in DA_PREFIXES)


# =============================================================================
# PHASE 1: ENTRY CLASSIFICATION
# =============================================================================

def classify_entries(entries, threshold=0.0):
    """
    Classify each entry as SINGLETON, RUN_START, RUN_INTERNAL, or RUN_END.

    Returns: dict mapping entry index -> {
        'class': EntryClass,
        'run_id': int or None,
        'run_size': int or None
    }
    """
    n = len(entries)

    # First compute adjacent Jaccards (within same section only)
    adj_j = []
    for i in range(n - 1):
        if entries[i]['section'] == entries[i+1]['section']:
            adj_j.append(token_jaccard(entries[i], entries[i+1]))
        else:
            adj_j.append(-1)  # Section break marker

    # Identify runs (consecutive entries with J > threshold and same section)
    runs = []
    current_run = [0]

    for i in range(n - 1):
        j = adj_j[i]
        if j > threshold:  # Connected to next
            current_run.append(i + 1)
        else:  # Not connected or section break
            if len(current_run) >= 2:
                runs.append(current_run)
            current_run = [i + 1]

    # Don't forget last run
    if len(current_run) >= 2:
        runs.append(current_run)

    # Build classification
    classification = {}
    for i in range(n):
        classification[i] = {
            'class': EntryClass.SINGLETON,
            'run_id': None,
            'run_size': None,
            'position_in_run': None
        }

    for run_id, run in enumerate(runs):
        run_size = len(run)
        for pos, idx in enumerate(run):
            if pos == 0:
                entry_class = EntryClass.RUN_START
            elif pos == run_size - 1:
                entry_class = EntryClass.RUN_END
            else:
                entry_class = EntryClass.RUN_INTERNAL

            classification[idx] = {
                'class': entry_class,
                'run_id': run_id,
                'run_size': run_size,
                'position_in_run': pos
            }

    return classification, runs, adj_j


# =============================================================================
# PHASE 2: STRUCTURAL METRICS PER ENTRY
# =============================================================================

def build_middle_frequency_map(entries):
    """Build global MIDDLE frequency map for rarity detection."""
    middle_counts = Counter()
    for e in entries:
        for t in e['tokens']:
            m = extract_middle(t)
            if m:
                middle_counts[m] += 1
    return middle_counts


def compute_entry_metrics(entry, middle_freq_map, rare_threshold_pct=10):
    """Compute structural metrics for a single entry."""
    tokens = entry['tokens']

    # Basic counts
    token_count = len(tokens)

    # DA-based block count
    da_positions = [i for i, t in enumerate(tokens) if is_da(t)]
    if not da_positions:
        block_count = 1
    else:
        # Count segments separated by DA tokens
        block_count = len(da_positions) + 1

    # Repetition detection (simplified - check for repeated token patterns)
    # C250 defines repetition as [BLOCK] x N structure
    # Simple proxy: count repeated tokens / total tokens
    token_counts = Counter(tokens)
    repeated_tokens = sum(c for c in token_counts.values() if c > 1)
    has_repetition = repeated_tokens > 0
    repetition_depth = max(token_counts.values()) if token_counts else 1

    # Prefix diversity
    prefixes = set(extract_prefix(t) for t in tokens)
    prefixes.discard(None)
    prefix_count = len(prefixes)

    # MIDDLE analysis
    middles = [extract_middle(t) for t in tokens]
    middles = [m for m in middles if m]
    middle_count = len(set(middles))

    # Rare MIDDLE count (bottom 10% by frequency)
    if middle_freq_map:
        total_middles = sum(middle_freq_map.values())
        cumulative = 0
        rare_threshold = 0
        for m, c in sorted(middle_freq_map.items(), key=lambda x: x[1]):
            cumulative += c
            if cumulative >= total_middles * (rare_threshold_pct / 100):
                rare_threshold = c
                break
        rare_middles = [m for m in middles if middle_freq_map.get(m, 0) <= rare_threshold]
        rare_middle_count = len(set(rare_middles))
    else:
        rare_middle_count = 0

    # DA count
    da_count = len(da_positions)

    return {
        'token_count': token_count,
        'block_count': block_count,
        'has_repetition': has_repetition,
        'repetition_depth': repetition_depth,
        'prefix_count': prefix_count,
        'middle_count': middle_count,
        'rare_middle_count': rare_middle_count,
        'da_count': da_count
    }


# =============================================================================
# PHASE 3: COMPARISON TESTS
# =============================================================================

def compare_groups(metric_name, clustered_values, singleton_values, alpha=0.05):
    """Compare metric between clustered and singleton entries."""

    clustered = np.array(clustered_values)
    singleton = np.array(singleton_values)

    # Mann-Whitney U test
    if len(clustered) > 1 and len(singleton) > 1:
        u_stat, p_value = stats.mannwhitneyu(clustered, singleton, alternative='two-sided')
    else:
        u_stat, p_value = np.nan, 1.0

    # Effect size (rank-biserial correlation)
    n1, n2 = len(clustered), len(singleton)
    if n1 > 0 and n2 > 0:
        r = 1 - (2 * u_stat) / (n1 * n2)
    else:
        r = 0

    # Means and medians
    clustered_mean = np.mean(clustered) if len(clustered) > 0 else np.nan
    singleton_mean = np.mean(singleton) if len(singleton) > 0 else np.nan
    clustered_median = np.median(clustered) if len(clustered) > 0 else np.nan
    singleton_median = np.median(singleton) if len(singleton) > 0 else np.nan

    # Direction
    if clustered_mean > singleton_mean:
        direction = "CLUSTERED > SINGLETON"
    elif clustered_mean < singleton_mean:
        direction = "CLUSTERED < SINGLETON"
    else:
        direction = "EQUAL"

    significant = p_value < alpha

    return {
        'metric': metric_name,
        'clustered_n': n1,
        'singleton_n': n2,
        'clustered_mean': clustered_mean,
        'singleton_mean': singleton_mean,
        'clustered_median': clustered_median,
        'singleton_median': singleton_median,
        'u_stat': u_stat,
        'p_value': p_value,
        'effect_size': r,
        'direction': direction,
        'significant': significant
    }


# =============================================================================
# PHASE 4: POSITION EFFECTS
# =============================================================================

def analyze_position_effects(entries, classification, all_metrics):
    """Compare RUN_START vs RUN_END vs RUN_INTERNAL entries."""

    # Filter to runs of size 3+ only
    by_position = {
        'RUN_START': [],
        'RUN_END': [],
        'RUN_INTERNAL': []
    }

    for i, clf in classification.items():
        if clf['run_size'] is not None and clf['run_size'] >= 3:
            pos_name = clf['class'].value
            if pos_name in by_position:
                by_position[pos_name].append(all_metrics[i])

    results = {}

    if len(by_position['RUN_START']) < 5 or len(by_position['RUN_END']) < 5:
        return None  # Not enough data

    # Compare START vs END for each metric
    for metric_name in ['token_count', 'block_count', 'prefix_count', 'middle_count']:
        start_vals = [m[metric_name] for m in by_position['RUN_START']]
        end_vals = [m[metric_name] for m in by_position['RUN_END']]

        if len(start_vals) > 1 and len(end_vals) > 1:
            u_stat, p_value = stats.mannwhitneyu(start_vals, end_vals, alternative='two-sided')
        else:
            u_stat, p_value = np.nan, 1.0

        results[metric_name] = {
            'start_mean': np.mean(start_vals),
            'end_mean': np.mean(end_vals),
            'start_n': len(start_vals),
            'end_n': len(end_vals),
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    return results


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    print("=" * 70)
    print("CLUSTER CHARACTERIZATION ANALYSIS")
    print("=" * 70)
    print("\nContext: C424 established that 31% of adjacent entries form")
    print("vocabulary-sharing runs. This analysis compares clustered vs singleton")
    print("entries on structural metrics.")

    print("\n" + "-" * 70)
    print("PHASE 1: ENTRY CLASSIFICATION")
    print("-" * 70)

    entries = load_currier_a_entries()
    print(f"\nLoaded {len(entries)} Currier A entries")

    classification, runs, adj_j = classify_entries(entries, threshold=0.0)

    # Count by class
    class_counts = Counter(clf['class'] for clf in classification.values())

    print(f"\nEntry classification (threshold J > 0):")
    for ec in EntryClass:
        count = class_counts.get(ec, 0)
        pct = 100 * count / len(entries)
        print(f"  {ec.value:<15}: {count:4d} ({pct:5.1f}%)")

    n_clustered = sum(1 for clf in classification.values() if clf['class'] != EntryClass.SINGLETON)
    n_singleton = class_counts.get(EntryClass.SINGLETON, 0)
    print(f"\n  CLUSTERED total: {n_clustered} ({100*n_clustered/len(entries):.1f}%)")
    print(f"  SINGLETON total: {n_singleton} ({100*n_singleton/len(entries):.1f}%)")

    print(f"\nNumber of runs: {len(runs)}")
    run_sizes = [len(r) for r in runs]
    print(f"Run size stats: mean={np.mean(run_sizes):.2f}, median={np.median(run_sizes):.0f}, max={max(run_sizes)}")

    print("\n" + "-" * 70)
    print("PHASE 2: STRUCTURAL METRICS COMPUTATION")
    print("-" * 70)

    # Build MIDDLE frequency map
    middle_freq = build_middle_frequency_map(entries)
    print(f"\nBuilt MIDDLE frequency map: {len(middle_freq)} unique MIDDLEs")

    # Compute metrics for all entries
    all_metrics = {}
    for i, e in enumerate(entries):
        all_metrics[i] = compute_entry_metrics(e, middle_freq)

    print(f"Computed metrics for {len(all_metrics)} entries")

    # Split by classification
    clustered_metrics = [all_metrics[i] for i, clf in classification.items() if clf['class'] != EntryClass.SINGLETON]
    singleton_metrics = [all_metrics[i] for i, clf in classification.items() if clf['class'] == EntryClass.SINGLETON]

    print(f"\nClustered entries: {len(clustered_metrics)}")
    print(f"Singleton entries: {len(singleton_metrics)}")

    print("\n" + "-" * 70)
    print("PHASE 3: COMPARISON TESTS")
    print("-" * 70)

    metrics_to_test = [
        'token_count',
        'block_count',
        'has_repetition',
        'repetition_depth',
        'prefix_count',
        'middle_count',
        'rare_middle_count',
        'da_count'
    ]

    comparison_results = []

    for metric in metrics_to_test:
        clustered_vals = [m[metric] for m in clustered_metrics]
        singleton_vals = [m[metric] for m in singleton_metrics]

        # Convert bools to ints for has_repetition
        if metric == 'has_repetition':
            clustered_vals = [int(v) for v in clustered_vals]
            singleton_vals = [int(v) for v in singleton_vals]

        result = compare_groups(metric, clustered_vals, singleton_vals)
        comparison_results.append(result)

    # Apply Bonferroni correction
    n_tests = len(comparison_results)
    corrected_alpha = 0.05 / n_tests

    print(f"\nResults (Bonferroni-corrected alpha = {corrected_alpha:.4f}):\n")
    print(f"{'Metric':<20} {'Clust Mean':<12} {'Sing Mean':<12} {'p-value':<12} {'Effect':<10} {'Sig':<5}")
    print("-" * 75)

    significant_findings = []

    for r in comparison_results:
        sig = "***" if r['p_value'] < corrected_alpha else ""
        if r['p_value'] < corrected_alpha:
            significant_findings.append(r)

        print(f"{r['metric']:<20} {r['clustered_mean']:<12.3f} {r['singleton_mean']:<12.3f} {r['p_value']:<12.6f} {r['effect_size']:<10.3f} {sig}")

    print("\n" + "-" * 70)
    print("PHASE 4: POSITION EFFECTS (Runs size 3+)")
    print("-" * 70)

    position_results = analyze_position_effects(entries, classification, all_metrics)

    if position_results:
        print(f"\nComparing RUN_START vs RUN_END entries:\n")
        print(f"{'Metric':<15} {'Start Mean':<12} {'End Mean':<12} {'p-value':<12} {'Sig':<5}")
        print("-" * 55)

        for metric, data in position_results.items():
            sig = "***" if data['significant'] else ""
            print(f"{metric:<15} {data['start_mean']:<12.3f} {data['end_mean']:<12.3f} {data['p_value']:<12.6f} {sig}")
    else:
        print("\nInsufficient data for position effects (need runs of size 3+)")

    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    print(f"\nTested {n_tests} metrics with Bonferroni correction.")
    print(f"Significant findings (p < {corrected_alpha:.4f}): {len(significant_findings)}")

    if significant_findings:
        print("\nSignificant structural differences detected:")
        for r in significant_findings:
            direction = "higher" if r['clustered_mean'] > r['singleton_mean'] else "lower"
            print(f"  - {r['metric']}: Clustered entries have {direction} values")
            print(f"    (Clustered: {r['clustered_mean']:.3f}, Singleton: {r['singleton_mean']:.3f}, effect={r['effect_size']:.3f})")
    else:
        print("\nNO significant structural differences detected.")
        print("Clustering appears to be vocabulary-driven, not structure-driven.")

    # Section breakdown
    print("\n" + "-" * 70)
    print("SECTION BREAKDOWN (Control)")
    print("-" * 70)

    by_section = defaultdict(lambda: {'clustered': [], 'singleton': []})
    for i, clf in classification.items():
        section = entries[i]['section']
        if clf['class'] == EntryClass.SINGLETON:
            by_section[section]['singleton'].append(all_metrics[i])
        else:
            by_section[section]['clustered'].append(all_metrics[i])

    print(f"\n{'Section':<10} {'Clust N':<10} {'Sing N':<10} {'Clust Tokens':<15} {'Sing Tokens':<15}")
    print("-" * 60)

    for section in sorted(by_section.keys()):
        data = by_section[section]
        c_n = len(data['clustered'])
        s_n = len(data['singleton'])
        c_tok = np.mean([m['token_count'] for m in data['clustered']]) if c_n > 0 else 0
        s_tok = np.mean([m['token_count'] for m in data['singleton']]) if s_n > 0 else 0
        print(f"{section:<10} {c_n:<10} {s_n:<10} {c_tok:<15.2f} {s_tok:<15.2f}")

    # Constraint recommendation
    print("\n" + "=" * 70)
    print("CONSTRAINT IMPLICATIONS")
    print("=" * 70)

    if len(significant_findings) >= 2:
        print("\nPotential refinement to C424:")
        print("  C424.a - Structural correlates of clustered adjacency")
        for r in significant_findings:
            direction = "more" if r['clustered_mean'] > r['singleton_mean'] else "fewer"
            print(f"    - Entries in runs have {direction} {r['metric'].replace('_', ' ')}")
    elif len(significant_findings) == 1:
        print("\nSingle significant finding - document as observation, not constraint.")
    else:
        print("\nNo structural differences found.")
        print("  -> C424 is PURE ORDERING STRUCTURE")
        print("  -> Clustering is vocabulary-driven, not complexity-driven")
        print("  -> No refinement needed")


# =============================================================================
# CONFOUND CHECK: ENTRY LENGTH
# =============================================================================

def confound_check_entry_length(entries, classification, all_metrics):
    """
    Check if clustering is just an artifact of entry length.

    Concern: Longer entries have more tokens, so mechanically they have
    higher probability of sharing at least one token with neighbors.

    Test: Within length-matched groups, is clustering rate still elevated?
    """
    print("\n" + "-" * 70)
    print("CONFOUND CHECK: ENTRY LENGTH")
    print("-" * 70)

    # Bin entries by token count
    bins = [(1, 10), (11, 20), (21, 30), (31, 50), (51, 100)]

    print(f"\nLength-stratified clustering rates:\n")
    print(f"{'Token Range':<15} {'Total':<10} {'Clustered':<12} {'Singleton':<12} {'Clust %':<10}")
    print("-" * 60)

    for low, high in bins:
        bin_entries = []
        for i, m in all_metrics.items():
            if low <= m['token_count'] <= high:
                bin_entries.append((i, classification[i]))

        if len(bin_entries) < 10:
            continue

        n_total = len(bin_entries)
        n_clustered = sum(1 for _, clf in bin_entries if clf['class'] != EntryClass.SINGLETON)
        n_singleton = n_total - n_clustered
        pct = 100 * n_clustered / n_total if n_total > 0 else 0

        print(f"{low}-{high:<10} {n_total:<10} {n_clustered:<12} {n_singleton:<12} {pct:<10.1f}%")

    # Test: Expected J > 0 rate by entry length
    print("\n\nExpected vs observed clustering by entry length:")
    print("(If clustering is just length-driven, expected should match observed)\n")

    for low, high in bins:
        bin_indices = [i for i, m in all_metrics.items() if low <= m['token_count'] <= high]

        if len(bin_indices) < 20:
            continue

        # Compute expected J > 0 rate for random pairs in this length bin
        # Sample random pairs and compute Jaccard
        n_samples = min(1000, len(bin_indices) * (len(bin_indices) - 1) // 2)
        random_jaccards = []

        for _ in range(n_samples):
            i, j = np.random.choice(bin_indices, 2, replace=False)
            random_jaccards.append(token_jaccard(entries[i], entries[j]))

        expected_nonzero = np.mean(np.array(random_jaccards) > 0) if random_jaccards else 0

        # Actual observed rate for adjacent pairs in this length bin
        observed_nonzero = sum(1 for i in bin_indices
                               if classification[i]['class'] != EntryClass.SINGLETON) / len(bin_indices)

        ratio = observed_nonzero / expected_nonzero if expected_nonzero > 0 else 0

        print(f"  Length {low}-{high}: Expected={100*expected_nonzero:.1f}%, Observed={100*observed_nonzero:.1f}%, Ratio={ratio:.2f}x")

    print("\n--- CONFOUND CHECK INTERPRETATION ---")
    print("If 'Ratio' is consistently > 1.0 across length bins,")
    print("clustering is NOT purely a length artifact - adjacent entries")
    print("share more vocabulary than length-matched random pairs.")


if __name__ == '__main__':
    main()

    # Run confound check
    print("\n" + "=" * 70)
    print("ADDITIONAL ANALYSIS: CONFOUND CHECK")
    print("=" * 70)

    entries = load_currier_a_entries()
    classification, runs, adj_j = classify_entries(entries, threshold=0.0)
    middle_freq = build_middle_frequency_map(entries)
    all_metrics = {i: compute_entry_metrics(e, middle_freq) for i, e in enumerate(entries)}

    confound_check_entry_length(entries, classification, all_metrics)
