#!/usr/bin/env python
"""
Super-Entry Grouping Analysis

Question: Do Currier A entries cluster into "super-groups" beyond pairwise adjacency?

Tests:
1. Similarity run analysis - Do high-similarity entries cluster into runs?
2. Extended window analysis - Does coherence persist beyond pairs?
3. Cliff detection - Are there sharp vocabulary drops marking group boundaries?

Goal: Determine the organizational grain size of Currier A.
"""
import sys
from collections import defaultdict
import numpy as np
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')

# =============================================================================
# DATA LOADING
# =============================================================================

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'


def load_currier_a_entries():
    """Load Currier A entries in sequential order (preserving folio/line sequence)."""

    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

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

                # Only Currier A
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

        # Don't forget last entry
        if current_entry is not None:
            entries.append(current_entry)

    return entries


# =============================================================================
# SIMILARITY METRICS
# =============================================================================

def jaccard(set1, set2):
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def entry_similarity(e1, e2):
    """Calculate token-level Jaccard between two entries."""
    return jaccard(set(e1['tokens']), set(e2['tokens']))


# =============================================================================
# PHASE 1: SIMILARITY RUN ANALYSIS
# =============================================================================

def compute_adjacent_jaccards(entries):
    """Compute J(i, i+1) for all adjacent pairs within same section."""

    jaccards = []
    section_breaks = []  # Indices where section changes

    for i in range(len(entries) - 1):
        e1 = entries[i]
        e2 = entries[i + 1]

        # Track section breaks
        if e1['section'] != e2['section']:
            section_breaks.append(i)
            jaccards.append(0.0)  # Mark section boundary with 0
        else:
            j = entry_similarity(e1, e2)
            jaccards.append(j)

    return np.array(jaccards), section_breaks


def test_autocorrelation(jaccards, section_breaks, max_lag=5):
    """Test for autocorrelation in Jaccard sequence."""

    # Remove section boundary values for autocorrelation test
    mask = np.ones(len(jaccards), dtype=bool)
    for idx in section_breaks:
        if idx < len(mask):
            mask[idx] = False

    clean_jaccards = jaccards[mask]

    if len(clean_jaccards) < max_lag + 10:
        return None

    results = {}

    for lag in range(1, max_lag + 1):
        # Compute autocorrelation at this lag
        n = len(clean_jaccards)
        x = clean_jaccards[:-lag]
        y = clean_jaccards[lag:]

        if len(x) < 10:
            continue

        corr, p_value = stats.pearsonr(x, y)
        results[lag] = {'correlation': corr, 'p_value': p_value, 'n': len(x)}

    return results


def runs_test(jaccards, section_breaks):
    """Perform Wald-Wolfowitz runs test for randomness."""

    # Remove section boundary values
    mask = np.ones(len(jaccards), dtype=bool)
    for idx in section_breaks:
        if idx < len(mask):
            mask[idx] = False

    clean_jaccards = jaccards[mask]

    if len(clean_jaccards) < 20:
        return None

    median = np.median(clean_jaccards)

    # Convert to binary: above/below median
    binary = clean_jaccards > median

    # Count runs
    runs = 1
    for i in range(1, len(binary)):
        if binary[i] != binary[i-1]:
            runs += 1

    # Expected runs under randomness
    n_above = np.sum(binary)
    n_below = len(binary) - n_above

    if n_above == 0 or n_below == 0:
        return None

    expected_runs = (2 * n_above * n_below) / len(binary) + 1
    variance = (2 * n_above * n_below * (2 * n_above * n_below - len(binary))) / \
               (len(binary)**2 * (len(binary) - 1))

    if variance <= 0:
        return None

    z = (runs - expected_runs) / np.sqrt(variance)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    return {
        'runs': runs,
        'expected_runs': expected_runs,
        'z_score': z,
        'p_value': p_value,
        'n': len(clean_jaccards),
        'n_above_median': int(n_above),
        'n_below_median': int(n_below)
    }


# =============================================================================
# PHASE 2: EXTENDED WINDOW ANALYSIS
# =============================================================================

def compute_decay_curve(entries, max_distance=10):
    """Compute mean Jaccard at each distance."""

    results = {d: [] for d in range(1, max_distance + 1)}

    for section in set(e['section'] for e in entries):
        # Get entries for this section in order
        section_entries = [e for e in entries if e['section'] == section]

        for i in range(len(section_entries)):
            for d in range(1, max_distance + 1):
                j = i + d
                if j < len(section_entries):
                    sim = entry_similarity(section_entries[i], section_entries[j])
                    results[d].append(sim)

    # Compute statistics
    decay_stats = {}
    for d, values in results.items():
        if values:
            decay_stats[d] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'n': len(values),
                'median': np.median(values)
            }

    return decay_stats


def compute_random_baseline(entries, n_samples=5000):
    """Compute baseline Jaccard for random pairs within same section."""

    by_section = defaultdict(list)
    for e in entries:
        by_section[e['section']].append(e)

    random_jaccards = []

    for section, sec_entries in by_section.items():
        if len(sec_entries) < 10:
            continue

        # Sample random pairs
        n_pairs = min(n_samples // len(by_section), len(sec_entries) * (len(sec_entries) - 1) // 2)

        for _ in range(n_pairs):
            i, j = np.random.choice(len(sec_entries), 2, replace=False)
            if abs(i - j) > 3:  # Non-adjacent
                random_jaccards.append(entry_similarity(sec_entries[i], sec_entries[j]))

    if random_jaccards:
        return {
            'mean': np.mean(random_jaccards),
            'std': np.std(random_jaccards),
            'n': len(random_jaccards)
        }
    return None


# =============================================================================
# PHASE 3: CLIFF DETECTION
# =============================================================================

def detect_cliffs(jaccards, section_breaks, threshold_percentile=25):
    """Identify cliffs (sharp drops in similarity)."""

    # Remove section boundaries
    mask = np.ones(len(jaccards), dtype=bool)
    for idx in section_breaks:
        if idx < len(mask):
            mask[idx] = False

    clean_jaccards = jaccards[mask]

    if len(clean_jaccards) < 20:
        return None

    # Find threshold
    threshold = np.percentile(clean_jaccards, threshold_percentile)

    # Identify cliffs
    cliff_indices = []
    original_indices = np.where(mask)[0]

    for i, j in enumerate(clean_jaccards):
        if j <= threshold:
            cliff_indices.append(original_indices[i])

    # Compute segment sizes
    all_boundaries = sorted(set(cliff_indices) | set(section_breaks))
    segment_sizes = []

    prev = 0
    for boundary in all_boundaries:
        if boundary > prev:
            segment_sizes.append(boundary - prev)
        prev = boundary + 1
    if prev < len(jaccards):
        segment_sizes.append(len(jaccards) - prev + 1)

    return {
        'threshold': threshold,
        'n_cliffs': len(cliff_indices),
        'cliff_rate': len(cliff_indices) / len(clean_jaccards) if clean_jaccards.size > 0 else 0,
        'segment_sizes': segment_sizes,
        'mean_segment_size': np.mean(segment_sizes) if segment_sizes else 0,
        'median_segment_size': np.median(segment_sizes) if segment_sizes else 0,
        'std_segment_size': np.std(segment_sizes) if segment_sizes else 0
    }


def analyze_segments(entries, jaccards, section_breaks, threshold_percentile=25):
    """Validate segments by comparing within vs between similarity."""

    cliffs = detect_cliffs(jaccards, section_breaks, threshold_percentile)

    if cliffs is None or cliffs['n_cliffs'] < 5:
        return None

    # Get cliff indices (from jaccards, not entries)
    mask = np.ones(len(jaccards), dtype=bool)
    for idx in section_breaks:
        if idx < len(mask):
            mask[idx] = False

    clean_jaccards = jaccards[mask]
    threshold = cliffs['threshold']

    original_indices = np.where(mask)[0]
    cliff_indices = set()
    for i, j in enumerate(clean_jaccards):
        if j <= threshold:
            cliff_indices.add(original_indices[i])

    # Build segments
    all_boundaries = sorted(cliff_indices | set(section_breaks))

    segments = []
    prev = 0
    for boundary in all_boundaries:
        if boundary > prev:
            segments.append(list(range(prev, boundary + 1)))
        prev = boundary + 1
    if prev < len(entries):
        segments.append(list(range(prev, len(entries))))

    # Filter segments to minimum size
    segments = [s for s in segments if len(s) >= 2]

    if len(segments) < 3:
        return None

    # Compute within-segment similarity
    within_sims = []
    for segment in segments:
        for i in range(len(segment)):
            for j in range(i + 1, len(segment)):
                if segment[i] < len(entries) and segment[j] < len(entries):
                    within_sims.append(entry_similarity(entries[segment[i]], entries[segment[j]]))

    # Compute between-segment similarity (sample)
    between_sims = []
    n_samples = min(5000, len(segments) * (len(segments) - 1) * 10)

    for _ in range(n_samples):
        seg1_idx, seg2_idx = np.random.choice(len(segments), 2, replace=False)
        i = np.random.choice(segments[seg1_idx])
        j = np.random.choice(segments[seg2_idx])
        if i < len(entries) and j < len(entries):
            between_sims.append(entry_similarity(entries[i], entries[j]))

    if not within_sims or not between_sims:
        return None

    within_mean = np.mean(within_sims)
    between_mean = np.mean(between_sims)
    ratio = within_mean / between_mean if between_mean > 0 else 0

    _, p_value = stats.mannwhitneyu(within_sims, between_sims, alternative='greater')

    return {
        'n_segments': len(segments),
        'within_segment_mean': within_mean,
        'between_segment_mean': between_mean,
        'ratio': ratio,
        'p_value': p_value,
        'segment_sizes': [len(s) for s in segments]
    }


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    print("=" * 70)
    print("SUPER-ENTRY GROUPING ANALYSIS")
    print("=" * 70)

    print("\nLoading Currier A entries...")
    entries = load_currier_a_entries()
    print(f"Loaded {len(entries)} entries")

    # Compute adjacent Jaccards
    print("\nComputing adjacent similarities...")
    jaccards, section_breaks = compute_adjacent_jaccards(entries)
    print(f"Computed {len(jaccards)} adjacent pairs")
    print(f"Section breaks: {len(section_breaks)}")

    # ==========================================================================
    # PHASE 1: SIMILARITY RUN ANALYSIS
    # ==========================================================================

    print("\n" + "=" * 70)
    print("PHASE 1: SIMILARITY RUN ANALYSIS")
    print("=" * 70)

    # Autocorrelation test
    print("\n--- Autocorrelation Test ---")
    autocorr = test_autocorrelation(jaccards, section_breaks, max_lag=5)

    if autocorr:
        print(f"\n{'Lag':<6} {'Correlation':<15} {'p-value':<15} {'Significant':<12}")
        print("-" * 50)

        significant_lags = []
        for lag, data in sorted(autocorr.items()):
            sig = "***" if data['p_value'] < 0.001 else "**" if data['p_value'] < 0.01 else "*" if data['p_value'] < 0.05 else ""
            print(f"{lag:<6} {data['correlation']:<15.4f} {data['p_value']:<15.6f} {sig}")
            if data['p_value'] < 0.05:
                significant_lags.append(lag)

        if significant_lags:
            print(f"\nSIGNAL: Autocorrelation detected at lags {significant_lags}")
            print("-> High-similarity entries tend to cluster into RUNS")
        else:
            print(f"\nNULL: No significant autocorrelation detected")
            print("-> Similarity values appear randomly dispersed")
    else:
        print("Insufficient data for autocorrelation test")

    # Runs test
    print("\n--- Wald-Wolfowitz Runs Test ---")
    runs_result = runs_test(jaccards, section_breaks)

    if runs_result:
        print(f"\nObserved runs:  {runs_result['runs']}")
        print(f"Expected runs:  {runs_result['expected_runs']:.1f}")
        print(f"Z-score:        {runs_result['z_score']:.3f}")
        print(f"P-value:        {runs_result['p_value']:.6f}")

        if runs_result['p_value'] < 0.05:
            if runs_result['z_score'] < 0:
                print(f"\nSIGNAL: Fewer runs than expected (p={runs_result['p_value']:.4f})")
                print("-> Similarity values CLUSTER (runs of high/low values)")
            else:
                print(f"\nSIGNAL: More runs than expected (p={runs_result['p_value']:.4f})")
                print("-> Similarity values ALTERNATE (anti-clustering)")
        else:
            print(f"\nNULL: Run count consistent with randomness")
    else:
        print("Insufficient data for runs test")

    # ==========================================================================
    # PHASE 2: EXTENDED WINDOW ANALYSIS
    # ==========================================================================

    print("\n" + "=" * 70)
    print("PHASE 2: EXTENDED WINDOW ANALYSIS")
    print("=" * 70)

    print("\n--- Similarity Decay Curve ---")
    decay_stats = compute_decay_curve(entries, max_distance=10)
    baseline = compute_random_baseline(entries)

    print(f"\n{'Distance':<10} {'Mean J':<12} {'Std':<12} {'N':<10} {'vs Baseline':<15}")
    print("-" * 60)

    baseline_mean = baseline['mean'] if baseline else 0

    coherence_radius = None
    for d in sorted(decay_stats.keys()):
        data = decay_stats[d]
        vs_baseline = data['mean'] / baseline_mean if baseline_mean > 0 else 0
        marker = "*" if vs_baseline > 1.1 else ""
        print(f"{d:<10} {data['mean']:<12.4f} {data['std']:<12.4f} {data['n']:<10} {vs_baseline:<12.2f}x {marker}")

        if coherence_radius is None and vs_baseline <= 1.1:
            coherence_radius = d - 1

    print(f"\nBaseline (random same-section pairs): {baseline_mean:.4f}")

    if coherence_radius:
        print(f"\nCOHERENCE RADIUS: {coherence_radius} entries")
        print(f"-> Similarity remains elevated for ~{coherence_radius} entries before dropping to baseline")
    else:
        print("\nCOHERENCE RADIUS: Not detected (similarity persists beyond tested range)")

    # ==========================================================================
    # PHASE 3: CLIFF DETECTION
    # ==========================================================================

    print("\n" + "=" * 70)
    print("PHASE 3: CLIFF DETECTION")
    print("=" * 70)

    print("\n--- Cliff Detection (25th percentile threshold) ---")
    cliffs = detect_cliffs(jaccards, section_breaks, threshold_percentile=25)

    if cliffs:
        print(f"\nThreshold Jaccard: {cliffs['threshold']:.4f}")
        print(f"Number of cliffs: {cliffs['n_cliffs']}")
        print(f"Cliff rate: {100 * cliffs['cliff_rate']:.1f}%")
        print(f"Mean segment size: {cliffs['mean_segment_size']:.1f} entries")
        print(f"Median segment size: {cliffs['median_segment_size']:.1f} entries")
        print(f"Std segment size: {cliffs['std_segment_size']:.1f} entries")

        # Segment size distribution
        sizes = cliffs['segment_sizes']
        if sizes:
            print(f"\nSegment size distribution:")
            print(f"  Min: {min(sizes)}")
            print(f"  25th percentile: {np.percentile(sizes, 25):.0f}")
            print(f"  Median: {np.median(sizes):.0f}")
            print(f"  75th percentile: {np.percentile(sizes, 75):.0f}")
            print(f"  Max: {max(sizes)}")
    else:
        print("Insufficient data for cliff detection")

    # Segment validation
    print("\n--- Segment Validation ---")
    segment_analysis = analyze_segments(entries, jaccards, section_breaks, threshold_percentile=25)

    if segment_analysis:
        print(f"\nNumber of segments: {segment_analysis['n_segments']}")
        print(f"Within-segment mean J: {segment_analysis['within_segment_mean']:.4f}")
        print(f"Between-segment mean J: {segment_analysis['between_segment_mean']:.4f}")
        print(f"Ratio: {segment_analysis['ratio']:.2f}x")
        print(f"P-value: {segment_analysis['p_value']:.6f}")

        if segment_analysis['p_value'] < 0.05 and segment_analysis['ratio'] > 1.1:
            print(f"\nSIGNAL: Segments are meaningful (within > between by {segment_analysis['ratio']:.2f}x)")
        else:
            print(f"\nNULL: Segments not significantly more coherent than random grouping")
    else:
        print("Insufficient data for segment validation")

    # ==========================================================================
    # SYNTHESIS
    # ==========================================================================

    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    # Collect signals
    signals = []

    if autocorr:
        sig_lags = [lag for lag, data in autocorr.items() if data['p_value'] < 0.05]
        if sig_lags:
            signals.append(f"Autocorrelation at lags {sig_lags}")

    if runs_result and runs_result['p_value'] < 0.05:
        if runs_result['z_score'] < 0:
            signals.append("Fewer runs than random (clustering)")
        else:
            signals.append("More runs than random (alternation)")

    if coherence_radius:
        signals.append(f"Coherence radius ~{coherence_radius} entries")

    if segment_analysis and segment_analysis['p_value'] < 0.05 and segment_analysis['ratio'] > 1.1:
        signals.append(f"Segments validated ({segment_analysis['ratio']:.2f}x)")

    if signals:
        print("\nDETECTED SIGNALS:")
        for s in signals:
            print(f"  - {s}")

        print("\nINTERPRETATION:")
        print("Currier A entries show SUPER-ENTRY STRUCTURE.")
        print("High-similarity entries cluster into groups beyond pairwise adjacency.")
        if cliffs and coherence_radius:
            print(f"Estimated group size: ~{cliffs['mean_segment_size']:.0f} entries (coherence radius: {coherence_radius})")
    else:
        print("\nNO SIGNALS DETECTED")
        print("\nINTERPRETATION:")
        print("The 1.31x adjacent similarity is UNIFORMLY DISTRIBUTED.")
        print("No super-entry grouping structure beyond pairwise adjacency.")
        print("Organization is purely local (entry-to-entry) without higher-level clustering.")

    # Constraint recommendation
    print("\n" + "-" * 70)
    print("CONSTRAINT RECOMMENDATION")
    print("-" * 70)

    if len(signals) >= 2:
        print("\nPotential new constraint:")
        print("  C424 - Currier A shows multi-entry coherence clustering")
        if cliffs:
            print(f"  Organizational grain size: ~{cliffs['mean_segment_size']:.0f} entries")
    else:
        print("\nNo new constraint warranted.")
        print("Document null result: Super-entry grouping NOT detected.")


if __name__ == '__main__':
    main()
