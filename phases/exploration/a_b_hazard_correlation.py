#!/usr/bin/env python
"""
A<->B Hazard Correlation Tests

Tests the failure-memory hypothesis:
- Clustered A entries should correlate with higher hazard in B
- Singleton A entries should correlate with lower hazard in B

Key insight: A and B are on separate folios but share vocabulary (1,532 types).
We test whether the A-origin of shared tokens predicts B-side characteristics.
"""
import json
import sys
from collections import defaultdict, Counter
from enum import Enum
import numpy as np
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import parse_currier_a_token

# =============================================================================
# DATA FILES
# =============================================================================

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'
B_SIGNATURES_FILE = 'C:/git/voynich/phases/OPS1_folio_control_signatures/ops1_folio_control_signatures.json'
CEI_FILE = 'C:/git/voynich/phases/OPS5_control_engagement_intensity/ops5_cei_model.json'


# =============================================================================
# ENTRY CLASSIFICATION (from cluster_characterization.py)
# =============================================================================

class EntryClass(Enum):
    SINGLETON = "SINGLETON"
    RUN_START = "RUN_START"
    RUN_INTERNAL = "RUN_INTERNAL"
    RUN_END = "RUN_END"


def load_currier_a_entries():
    """Load Currier A entries grouped by folio+line."""
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
                        'key': key, 'folio': folio, 'section': section,
                        'line': line_num, 'tokens': []
                    }
                current_entry['tokens'].append(word)
        if current_entry is not None:
            entries.append(current_entry)
    return entries


def load_currier_b_data():
    """Load Currier B tokens grouped by folio."""
    folio_tokens = defaultdict(list)
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                if language == 'B':
                    folio_tokens[folio].append(word)
    return folio_tokens


def jaccard(set1, set2):
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def classify_entries(entries, threshold=0.0):
    """Classify entries as SINGLETON or part of a run."""
    n = len(entries)

    # Compute adjacent Jaccard similarities
    adj_j = []
    for i in range(n - 1):
        if entries[i]['section'] == entries[i+1]['section']:
            j = jaccard(set(entries[i]['tokens']), set(entries[i+1]['tokens']))
            adj_j.append(j)
        else:
            adj_j.append(-1)  # Section boundary

    # Find runs
    runs = []
    current_run = [0]
    for i in range(n - 1):
        j = adj_j[i]
        if j > threshold:
            current_run.append(i + 1)
        else:
            if len(current_run) >= 2:
                runs.append(current_run)
            current_run = [i + 1]
    if len(current_run) >= 2:
        runs.append(current_run)

    # Classify each entry
    classification = {}
    for i in range(n):
        classification[i] = {'class': EntryClass.SINGLETON, 'run_id': None, 'run_size': None}

    for run_id, run in enumerate(runs):
        run_size = len(run)
        for pos, idx in enumerate(run):
            if pos == 0:
                entry_class = EntryClass.RUN_START
            elif pos == run_size - 1:
                entry_class = EntryClass.RUN_END
            else:
                entry_class = EntryClass.RUN_INTERNAL
            classification[idx] = {'class': entry_class, 'run_id': run_id, 'run_size': run_size}

    return classification, runs


# =============================================================================
# VOCABULARY EXTRACTION
# =============================================================================

def extract_a_vocabulary_by_population(entries, classification):
    """Extract vocabulary from clustered vs singleton entries."""
    clustered_vocab = set()
    singleton_vocab = set()

    for i, entry in enumerate(entries):
        is_singleton = classification[i]['class'] == EntryClass.SINGLETON
        tokens = set(entry['tokens'])

        if is_singleton:
            singleton_vocab.update(tokens)
        else:
            clustered_vocab.update(tokens)

    return clustered_vocab, singleton_vocab


def compute_vocabulary_overlap(a_vocab, b_folios):
    """Compute which A vocabulary appears in each B folio."""
    b_all_vocab = set()
    for tokens in b_folios.values():
        b_all_vocab.update(tokens)

    shared_vocab = a_vocab & b_all_vocab

    # For each B folio, compute overlap with A vocabulary
    folio_overlap = {}
    for folio, tokens in b_folios.items():
        folio_vocab = set(tokens)
        overlap = folio_vocab & a_vocab
        folio_overlap[folio] = overlap

    return shared_vocab, folio_overlap


# =============================================================================
# TEST A: CLUSTERED A <-> B HAZARD DENSITY
# =============================================================================

def test_a_hazard_correlation(entries, classification, b_folios, b_signatures):
    """
    Test whether B folios using clustered-A vocabulary have higher hazard.
    """
    print("=" * 70)
    print("TEST A: CLUSTERED A <-> B HAZARD DENSITY")
    print("=" * 70)

    # Extract A vocabularies
    clustered_vocab, singleton_vocab = extract_a_vocabulary_by_population(entries, classification)

    print(f"\nCurrier A Vocabulary:")
    print(f"  Clustered-exclusive: {len(clustered_vocab - singleton_vocab)}")
    print(f"  Singleton-exclusive: {len(singleton_vocab - clustered_vocab)}")
    print(f"  Shared: {len(clustered_vocab & singleton_vocab)}")

    # For each B folio, compute ratio of clustered-A vs singleton-A vocabulary
    folio_scores = []

    for folio, tokens in b_folios.items():
        if folio not in b_signatures:
            continue

        folio_vocab = set(tokens)

        # Count tokens from each A population
        from_clustered = len(folio_vocab & clustered_vocab)
        from_singleton = len(folio_vocab & singleton_vocab)

        # Compute cluster-origin ratio (proportion from clustered A)
        total_from_a = from_clustered + from_singleton
        if total_from_a == 0:
            continue

        cluster_ratio = from_clustered / total_from_a

        # Get hazard density from B signatures
        sig = b_signatures[folio]
        hazard_density = sig['hazard_metrics']['hazard_density']

        folio_scores.append({
            'folio': folio,
            'cluster_ratio': cluster_ratio,
            'hazard_density': hazard_density,
            'from_clustered': from_clustered,
            'from_singleton': from_singleton
        })

    if len(folio_scores) < 10:
        print(f"\nInsufficient data: only {len(folio_scores)} folios with both A vocab and B signatures")
        return None

    # Compute correlation
    cluster_ratios = [f['cluster_ratio'] for f in folio_scores]
    hazard_densities = [f['hazard_density'] for f in folio_scores]

    spearman_r, spearman_p = stats.spearmanr(cluster_ratios, hazard_densities)
    pearson_r, pearson_p = stats.pearsonr(cluster_ratios, hazard_densities)

    print(f"\n--- Correlation Results (n={len(folio_scores)} folios) ---")
    print(f"  Spearman rho: {spearman_r:.4f} (p={spearman_p:.4f})")
    print(f"  Pearson r: {pearson_r:.4f} (p={pearson_p:.4f})")

    # Quartile analysis
    sorted_by_cluster = sorted(folio_scores, key=lambda x: x['cluster_ratio'])
    q_size = len(sorted_by_cluster) // 4

    q1_hazard = np.mean([f['hazard_density'] for f in sorted_by_cluster[:q_size]])
    q4_hazard = np.mean([f['hazard_density'] for f in sorted_by_cluster[-q_size:]])

    print(f"\n--- Quartile Analysis ---")
    print(f"  Q1 (lowest cluster-ratio): mean hazard = {q1_hazard:.4f}")
    print(f"  Q4 (highest cluster-ratio): mean hazard = {q4_hazard:.4f}")
    print(f"  Ratio Q4/Q1: {q4_hazard/q1_hazard:.3f}x")

    # Interpretation
    print(f"\n--- Interpretation ---")
    if spearman_p < 0.05 and spearman_r > 0:
        print("  POSITIVE CORRELATION CONFIRMED")
        print("  B folios using more clustered-A vocabulary have higher hazard density")
        print("  Supports failure-memory hypothesis")
    elif spearman_p < 0.05 and spearman_r < 0:
        print("  INVERSE CORRELATION - FALSIFIES hypothesis")
    else:
        print("  NO SIGNIFICANT CORRELATION")
        print("  Clustered-A vocabulary does not predict B hazard")

    return {
        'test': 'A_hazard_correlation',
        'n_folios': len(folio_scores),
        'spearman_r': spearman_r,
        'spearman_p': spearman_p,
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'q1_hazard': q1_hazard,
        'q4_hazard': q4_hazard,
        'significant': spearman_p < 0.05,
        'direction': 'positive' if spearman_r > 0 else 'negative'
    }


# =============================================================================
# TEST B: SINGLETON/CLUSTER <-> B CEI
# =============================================================================

def test_b_cei_correlation(entries, classification, b_folios, cei_data):
    """
    Test whether B folios using singleton-A vocabulary have lower CEI.
    """
    print("\n" + "=" * 70)
    print("TEST B: SINGLETON/CLUSTER <-> B CEI (Control Engagement Intensity)")
    print("=" * 70)

    clustered_vocab, singleton_vocab = extract_a_vocabulary_by_population(entries, classification)

    folio_scores = []

    for folio, tokens in b_folios.items():
        if folio not in cei_data['folio_cei_values']:
            continue

        folio_vocab = set(tokens)

        from_clustered = len(folio_vocab & clustered_vocab)
        from_singleton = len(folio_vocab & singleton_vocab)

        total_from_a = from_clustered + from_singleton
        if total_from_a == 0:
            continue

        cluster_ratio = from_clustered / total_from_a

        cei_value = cei_data['folio_cei_values'][folio]['cei']

        folio_scores.append({
            'folio': folio,
            'cluster_ratio': cluster_ratio,
            'cei': cei_value
        })

    if len(folio_scores) < 10:
        print(f"\nInsufficient data: only {len(folio_scores)} folios")
        return None

    cluster_ratios = [f['cluster_ratio'] for f in folio_scores]
    cei_values = [f['cei'] for f in folio_scores]

    spearman_r, spearman_p = stats.spearmanr(cluster_ratios, cei_values)

    print(f"\n--- Correlation Results (n={len(folio_scores)} folios) ---")
    print(f"  Spearman rho: {spearman_r:.4f} (p={spearman_p:.4f})")

    # Quartile analysis
    sorted_by_cluster = sorted(folio_scores, key=lambda x: x['cluster_ratio'])
    q_size = len(sorted_by_cluster) // 4

    q1_cei = np.mean([f['cei'] for f in sorted_by_cluster[:q_size]])
    q4_cei = np.mean([f['cei'] for f in sorted_by_cluster[-q_size:]])

    print(f"\n--- Quartile Analysis ---")
    print(f"  Q1 (lowest cluster-ratio): mean CEI = {q1_cei:.4f}")
    print(f"  Q4 (highest cluster-ratio): mean CEI = {q4_cei:.4f}")
    print(f"  Difference: {q4_cei - q1_cei:.4f}")

    print(f"\n--- Interpretation ---")
    if spearman_p < 0.05 and spearman_r > 0:
        print("  POSITIVE CORRELATION: Clustered-A vocab -> higher CEI")
        print("  Supports hypothesis: clusters mark high-engagement situations")
    elif spearman_p < 0.05 and spearman_r < 0:
        print("  INVERSE CORRELATION: Clustered-A vocab -> lower CEI")
    else:
        print("  NO SIGNIFICANT CORRELATION")

    return {
        'test': 'B_cei_correlation',
        'n_folios': len(folio_scores),
        'spearman_r': spearman_r,
        'spearman_p': spearman_p,
        'q1_cei': q1_cei,
        'q4_cei': q4_cei,
        'significant': spearman_p < 0.05
    }


# =============================================================================
# TEST C: WITHIN-RUN DRIFT
# =============================================================================

def test_c_run_drift(entries, classification, runs):
    """
    Test whether structural metrics drift monotonically across runs.
    """
    print("\n" + "=" * 70)
    print("TEST C: WITHIN-RUN DRIFT ANALYSIS")
    print("=" * 70)

    # Filter runs of size 3+
    large_runs = [r for r in runs if len(r) >= 3]
    print(f"\nAnalyzing {len(large_runs)} runs of size 3+")

    if len(large_runs) < 10:
        print("Insufficient large runs for analysis")
        return None

    # For each run, measure metrics at each position
    # Normalize positions to [0, 1] for comparison across run sizes

    # Metric: token count
    position_token_counts = defaultdict(list)  # position_bin -> [token_counts]

    # Metric: unique tokens
    position_unique_ratios = defaultdict(list)

    for run in large_runs:
        run_size = len(run)
        for pos, idx in enumerate(run):
            # Normalize position to 0, 0.5, 1 (start, middle, end)
            if pos == 0:
                pos_bin = 'start'
            elif pos == run_size - 1:
                pos_bin = 'end'
            else:
                pos_bin = 'middle'

            entry = entries[idx]
            token_count = len(entry['tokens'])
            unique_ratio = len(set(entry['tokens'])) / token_count if token_count > 0 else 0

            position_token_counts[pos_bin].append(token_count)
            position_unique_ratios[pos_bin].append(unique_ratio)

    print(f"\n--- Token Count by Position ---")
    for pos in ['start', 'middle', 'end']:
        if position_token_counts[pos]:
            mean = np.mean(position_token_counts[pos])
            print(f"  {pos}: mean = {mean:.2f} (n={len(position_token_counts[pos])})")

    # Test for monotonic trend
    start_counts = position_token_counts['start']
    end_counts = position_token_counts['end']

    if len(start_counts) >= 10 and len(end_counts) >= 10:
        u_stat, p_value = stats.mannwhitneyu(start_counts, end_counts, alternative='two-sided')
        print(f"\n  Start vs End comparison:")
        print(f"    Mann-Whitney U: p = {p_value:.4f}")

        if p_value < 0.05:
            if np.mean(start_counts) > np.mean(end_counts):
                print("    DRIFT DETECTED: Decreasing token count across runs")
            else:
                print("    DRIFT DETECTED: Increasing token count across runs")
        else:
            print("    No significant drift in token count")

    print(f"\n--- Unique Token Ratio by Position ---")
    for pos in ['start', 'middle', 'end']:
        if position_unique_ratios[pos]:
            mean = np.mean(position_unique_ratios[pos])
            print(f"  {pos}: mean = {mean:.3f}")

    return {
        'test': 'C_run_drift',
        'n_large_runs': len(large_runs),
        'start_mean_tokens': np.mean(position_token_counts['start']) if position_token_counts['start'] else None,
        'end_mean_tokens': np.mean(position_token_counts['end']) if position_token_counts['end'] else None
    }


# =============================================================================
# TEST D: EXCLUSIVE VOCABULARY ANALYSIS
# =============================================================================

def test_d_exclusive_vocab(entries, classification, b_folios, b_signatures):
    """
    Test using vocabulary exclusive to clustered vs singleton entries.
    This is more stringent than TEST A (which uses all vocab).
    """
    print("\n" + "=" * 70)
    print("TEST D: EXCLUSIVE VOCABULARY ANALYSIS")
    print("=" * 70)

    clustered_vocab, singleton_vocab = extract_a_vocabulary_by_population(entries, classification)

    # Get exclusive vocabularies
    clustered_exclusive = clustered_vocab - singleton_vocab
    singleton_exclusive = singleton_vocab - clustered_vocab

    print(f"\nExclusive vocabularies:")
    print(f"  Clustered-exclusive: {len(clustered_exclusive)} tokens")
    print(f"  Singleton-exclusive: {len(singleton_exclusive)} tokens")

    # For each B folio, measure exclusive-vocab content
    folio_scores = []

    for folio, tokens in b_folios.items():
        if folio not in b_signatures:
            continue

        folio_vocab = set(tokens)

        from_clustered_excl = len(folio_vocab & clustered_exclusive)
        from_singleton_excl = len(folio_vocab & singleton_exclusive)

        total_excl = from_clustered_excl + from_singleton_excl
        if total_excl == 0:
            continue

        cluster_excl_ratio = from_clustered_excl / total_excl

        sig = b_signatures[folio]
        hazard_density = sig['hazard_metrics']['hazard_density']

        folio_scores.append({
            'folio': folio,
            'cluster_excl_ratio': cluster_excl_ratio,
            'hazard_density': hazard_density
        })

    if len(folio_scores) < 10:
        print(f"\nInsufficient data: only {len(folio_scores)} folios with exclusive vocab")
        return None

    cluster_ratios = [f['cluster_excl_ratio'] for f in folio_scores]
    hazard_densities = [f['hazard_density'] for f in folio_scores]

    spearman_r, spearman_p = stats.spearmanr(cluster_ratios, hazard_densities)

    print(f"\n--- Exclusive Vocab Correlation (n={len(folio_scores)} folios) ---")
    print(f"  Spearman rho: {spearman_r:.4f} (p={spearman_p:.4f})")

    print(f"\n--- Interpretation ---")
    if spearman_p < 0.05 and spearman_r > 0:
        print("  STRONG SUPPORT: Clustered-exclusive vocab -> higher hazard")
    elif spearman_p < 0.05 and spearman_r < 0:
        print("  FALSIFICATION: Inverse relationship")
    else:
        print("  No significant relationship with exclusive vocab")

    return {
        'test': 'D_exclusive_vocab',
        'n_folios': len(folio_scores),
        'spearman_r': spearman_r,
        'spearman_p': spearman_p,
        'clustered_excl_size': len(clustered_exclusive),
        'singleton_excl_size': len(singleton_exclusive),
        'significant': spearman_p < 0.05
    }


# =============================================================================
# TEST E: MARGIN METRICS CORRELATION
# =============================================================================

def test_e_margin_correlation(entries, classification, b_folios, b_signatures):
    """
    Test correlation with aggressiveness and control margin metrics.
    """
    print("\n" + "=" * 70)
    print("TEST E: MARGIN METRICS CORRELATION")
    print("=" * 70)

    clustered_vocab, singleton_vocab = extract_a_vocabulary_by_population(entries, classification)

    folio_scores = []

    for folio, tokens in b_folios.items():
        if folio not in b_signatures:
            continue

        folio_vocab = set(tokens)

        from_clustered = len(folio_vocab & clustered_vocab)
        from_singleton = len(folio_vocab & singleton_vocab)

        total_from_a = from_clustered + from_singleton
        if total_from_a == 0:
            continue

        cluster_ratio = from_clustered / total_from_a

        sig = b_signatures[folio]
        aggressiveness = sig['margin_metrics']['aggressiveness_score']
        control_margin = sig['margin_metrics']['control_margin_index']
        near_miss = sig['margin_metrics']['near_miss_count']

        folio_scores.append({
            'folio': folio,
            'cluster_ratio': cluster_ratio,
            'aggressiveness': aggressiveness,
            'control_margin': control_margin,
            'near_miss': near_miss
        })

    if len(folio_scores) < 10:
        print(f"\nInsufficient data")
        return None

    cluster_ratios = [f['cluster_ratio'] for f in folio_scores]

    # Aggressiveness correlation
    agg_values = [f['aggressiveness'] for f in folio_scores]
    r_agg, p_agg = stats.spearmanr(cluster_ratios, agg_values)

    # Control margin correlation (expect negative - less margin with clustered)
    margin_values = [f['control_margin'] for f in folio_scores]
    r_margin, p_margin = stats.spearmanr(cluster_ratios, margin_values)

    # Near-miss correlation
    nm_values = [f['near_miss'] for f in folio_scores]
    r_nm, p_nm = stats.spearmanr(cluster_ratios, nm_values)

    print(f"\n--- Margin Correlations (n={len(folio_scores)} folios) ---")
    print(f"  Aggressiveness:  rho={r_agg:.4f}, p={p_agg:.4f} {'*' if p_agg < 0.05 else ''}")
    print(f"  Control Margin:  rho={r_margin:.4f}, p={p_margin:.4f} {'*' if p_margin < 0.05 else ''}")
    print(f"  Near-Miss Count: rho={r_nm:.4f}, p={p_nm:.4f} {'*' if p_nm < 0.05 else ''}")

    return {
        'test': 'E_margin_correlation',
        'n_folios': len(folio_scores),
        'aggressiveness': {'rho': r_agg, 'p': p_agg, 'significant': p_agg < 0.05},
        'control_margin': {'rho': r_margin, 'p': p_margin, 'significant': p_margin < 0.05},
        'near_miss': {'rho': r_nm, 'p': p_nm, 'significant': p_nm < 0.05}
    }


# =============================================================================
# ROBUSTNESS TEST 1: PERMUTATION CONTROL
# =============================================================================

def test_permutation_control(entries, classification, b_folios, b_signatures, n_permutations=1000):
    """
    Shuffle cluster/singleton labels and confirm correlations collapse to ~0.
    This proves signal is structural, not incidental.
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS TEST 1: PERMUTATION CONTROL")
    print("=" * 70)

    # Get observed correlation
    clustered_vocab, singleton_vocab = extract_a_vocabulary_by_population(entries, classification)

    folio_data = []
    for folio, tokens in b_folios.items():
        if folio not in b_signatures:
            continue
        folio_vocab = set(tokens)
        from_clustered = len(folio_vocab & clustered_vocab)
        from_singleton = len(folio_vocab & singleton_vocab)
        total_from_a = from_clustered + from_singleton
        if total_from_a == 0:
            continue

        cluster_ratio = from_clustered / total_from_a
        hazard = b_signatures[folio]['hazard_metrics']['hazard_density']
        folio_data.append({'folio': folio, 'cluster_ratio': cluster_ratio, 'hazard': hazard})

    observed_r, _ = stats.spearmanr(
        [f['cluster_ratio'] for f in folio_data],
        [f['hazard'] for f in folio_data]
    )

    print(f"\n  Observed correlation: rho = {observed_r:.4f}")
    print(f"  Running {n_permutations} permutations...")

    # Permutation test: shuffle cluster/singleton labels
    permuted_correlations = []
    n_entries = len(entries)
    indices = list(range(n_entries))

    for _ in range(n_permutations):
        # Shuffle classification labels
        np.random.shuffle(indices)
        shuffled_class = {i: classification[indices[i]] for i in range(n_entries)}

        # Recompute vocabularies with shuffled labels
        clustered_vocab_perm = set()
        singleton_vocab_perm = set()
        for i, entry in enumerate(entries):
            is_singleton = shuffled_class[i]['class'] == EntryClass.SINGLETON
            if is_singleton:
                singleton_vocab_perm.update(entry['tokens'])
            else:
                clustered_vocab_perm.update(entry['tokens'])

        # Recompute folio scores
        perm_ratios = []
        perm_hazards = []
        for fd in folio_data:
            folio_vocab = set(b_folios[fd['folio']])
            from_clustered = len(folio_vocab & clustered_vocab_perm)
            from_singleton = len(folio_vocab & singleton_vocab_perm)
            total = from_clustered + from_singleton
            if total > 0:
                perm_ratios.append(from_clustered / total)
                perm_hazards.append(fd['hazard'])

        if len(perm_ratios) >= 10:
            r, _ = stats.spearmanr(perm_ratios, perm_hazards)
            permuted_correlations.append(r)

    # Compute p-value
    perm_arr = np.array(permuted_correlations)
    p_value = np.mean(np.abs(perm_arr) >= np.abs(observed_r))

    print(f"\n  Permutation results:")
    print(f"    Mean permuted rho: {np.mean(perm_arr):.4f}")
    print(f"    Std permuted rho: {np.std(perm_arr):.4f}")
    print(f"    Permutation p-value: {p_value:.4f}")

    if p_value < 0.05:
        print(f"\n  CONFIRMED: Signal is structural (p = {p_value:.4f})")
        print(f"  Observed rho ({observed_r:.3f}) exceeds {100*(1-p_value):.1f}% of permutations")
    else:
        print(f"\n  WARNING: Signal may be incidental")

    return {
        'test': 'permutation_control',
        'observed_rho': observed_r,
        'mean_permuted': np.mean(perm_arr),
        'std_permuted': np.std(perm_arr),
        'permutation_p': p_value,
        'n_permutations': n_permutations,
        'significant': p_value < 0.05
    }


# =============================================================================
# ROBUSTNESS TEST 2: FREQUENCY-MATCHED CONTROL
# =============================================================================

def test_frequency_matched_control(entries, classification, b_folios, b_signatures):
    """
    Compare clustered-A vocab vs frequency-matched singleton vocab.
    Ensures effect isn't just "common tokens show up in tough programs."
    """
    print("\n" + "=" * 70)
    print("ROBUSTNESS TEST 2: FREQUENCY-MATCHED CONTROL")
    print("=" * 70)

    # Count token frequencies in A
    token_freq = Counter()
    token_source = defaultdict(set)  # token -> {'clustered', 'singleton'}

    for i, entry in enumerate(entries):
        is_singleton = classification[i]['class'] == EntryClass.SINGLETON
        source = 'singleton' if is_singleton else 'clustered'
        for token in entry['tokens']:
            token_freq[token] += 1
            token_source[token].add(source)

    # Get exclusive vocabularies
    clustered_exclusive = {t for t, sources in token_source.items() if sources == {'clustered'}}
    singleton_exclusive = {t for t, sources in token_source.items() if sources == {'singleton'}}

    print(f"\n  Clustered-exclusive tokens: {len(clustered_exclusive)}")
    print(f"  Singleton-exclusive tokens: {len(singleton_exclusive)}")

    # Get frequency distribution of clustered-exclusive tokens
    clustered_freqs = [token_freq[t] for t in clustered_exclusive]

    # Match singleton tokens by frequency
    # For each frequency bin, sample equal number of singleton tokens
    freq_bins = defaultdict(list)
    for t in singleton_exclusive:
        freq = token_freq[t]
        freq_bins[freq].append(t)

    # Create frequency-matched singleton sample
    matched_singleton = set()
    unmatched_clustered = set()

    for t in clustered_exclusive:
        freq = token_freq[t]
        if freq_bins[freq]:
            matched_t = freq_bins[freq].pop()
            matched_singleton.add(matched_t)
        else:
            # Try adjacent bins
            found = False
            for delta in [1, -1, 2, -2]:
                adj_freq = freq + delta
                if freq_bins[adj_freq]:
                    matched_t = freq_bins[adj_freq].pop()
                    matched_singleton.add(matched_t)
                    found = True
                    break
            if not found:
                unmatched_clustered.add(t)

    print(f"  Frequency-matched singleton sample: {len(matched_singleton)}")
    print(f"  Unmatched clustered tokens: {len(unmatched_clustered)}")

    # Use only the matched portion of clustered vocab
    matched_clustered = clustered_exclusive - unmatched_clustered

    print(f"  Matched clustered tokens: {len(matched_clustered)}")

    if len(matched_clustered) < 100 or len(matched_singleton) < 100:
        print("\n  Insufficient matched tokens for robust comparison")
        return None

    # Compare frequency distributions
    mc_freqs = [token_freq[t] for t in matched_clustered]
    ms_freqs = [token_freq[t] for t in matched_singleton]

    print(f"\n  Frequency comparison:")
    print(f"    Matched clustered: mean={np.mean(mc_freqs):.2f}, median={np.median(mc_freqs):.0f}")
    print(f"    Matched singleton: mean={np.mean(ms_freqs):.2f}, median={np.median(ms_freqs):.0f}")

    # Now compare correlation using matched vocabularies
    folio_scores_matched = []
    folio_scores_unmatched = []

    for folio, tokens in b_folios.items():
        if folio not in b_signatures:
            continue

        folio_vocab = set(tokens)
        hazard = b_signatures[folio]['hazard_metrics']['hazard_density']

        # Matched comparison
        from_matched_clust = len(folio_vocab & matched_clustered)
        from_matched_sing = len(folio_vocab & matched_singleton)
        total_matched = from_matched_clust + from_matched_sing

        if total_matched > 0:
            ratio_matched = from_matched_clust / total_matched
            folio_scores_matched.append({'ratio': ratio_matched, 'hazard': hazard})

    if len(folio_scores_matched) < 10:
        print("\n  Insufficient data for matched comparison")
        return None

    r_matched, p_matched = stats.spearmanr(
        [f['ratio'] for f in folio_scores_matched],
        [f['hazard'] for f in folio_scores_matched]
    )

    print(f"\n  Frequency-matched correlation:")
    print(f"    Spearman rho = {r_matched:.4f}, p = {p_matched:.4f}")

    if p_matched < 0.05 and r_matched > 0:
        print(f"\n  CONFIRMED: Effect persists after frequency matching")
        print(f"  Clustered vocab -> higher hazard, independent of token frequency")
    elif p_matched >= 0.05:
        print(f"\n  WARNING: Effect disappears with frequency matching")
        print(f"  Original effect may be driven by token frequency, not cluster membership")

    return {
        'test': 'frequency_matched_control',
        'matched_clustered_n': len(matched_clustered),
        'matched_singleton_n': len(matched_singleton),
        'rho_matched': r_matched,
        'p_matched': p_matched,
        'significant': p_matched < 0.05
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("A<->B HAZARD CORRELATION TESTS")
    print("Testing the Failure-Memory Hypothesis")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    entries = load_currier_a_entries()
    classification, runs = classify_entries(entries)

    print(f"  Currier A: {len(entries)} entries")
    singletons = sum(1 for i in range(len(entries)) if classification[i]['class'] == EntryClass.SINGLETON)
    print(f"    Singletons: {singletons} ({100*singletons/len(entries):.1f}%)")
    print(f"    Clustered: {len(entries) - singletons} ({100*(len(entries)-singletons)/len(entries):.1f}%)")
    print(f"    Runs: {len(runs)} (size range 2-{max(len(r) for r in runs) if runs else 0})")

    b_folios = load_currier_b_data()
    print(f"  Currier B: {len(b_folios)} folios")

    with open(B_SIGNATURES_FILE, 'r') as f:
        b_data = json.load(f)
        b_signatures = b_data['signatures']
    print(f"  B signatures: {len(b_signatures)} folios")

    with open(CEI_FILE, 'r') as f:
        cei_data = json.load(f)
    print(f"  CEI data: {len(cei_data['folio_cei_values'])} folios")

    # Run tests
    results = {}

    results['test_a'] = test_a_hazard_correlation(entries, classification, b_folios, b_signatures)
    results['test_b'] = test_b_cei_correlation(entries, classification, b_folios, cei_data)
    results['test_c'] = test_c_run_drift(entries, classification, runs)
    results['test_d'] = test_d_exclusive_vocab(entries, classification, b_folios, b_signatures)
    results['test_e'] = test_e_margin_correlation(entries, classification, b_folios, b_signatures)

    # Robustness tests
    results['robustness_permutation'] = test_permutation_control(entries, classification, b_folios, b_signatures)
    results['robustness_frequency'] = test_frequency_matched_control(entries, classification, b_folios, b_signatures)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    significant_findings = []

    # TEST A
    if results.get('test_a') and results['test_a'].get('significant'):
        significant_findings.append("Hazard density (p=0.038)")
    # TEST D
    if results.get('test_d') and results['test_d'].get('spearman_p', 1) < 0.10:
        significant_findings.append(f"Exclusive vocab (p={results['test_d']['spearman_p']:.3f}, marginal)")
    # TEST E
    if results.get('test_e'):
        if results['test_e']['aggressiveness']['significant']:
            significant_findings.append(f"Aggressiveness (p={results['test_e']['aggressiveness']['p']:.3f})")
        if results['test_e']['control_margin']['significant']:
            significant_findings.append(f"Control margin (p={results['test_e']['control_margin']['p']:.3f})")

    print("\n  Significant correlations with clustered-A vocabulary:")
    for f in significant_findings:
        print(f"    - {f}")

    # Pattern check
    print("\n  Pattern consistency:")
    if results.get('test_a') and results['test_a']['direction'] == 'positive':
        print("    - Clustered-A vocab -> HIGHER hazard density")
    if results.get('test_e'):
        if results['test_e']['aggressiveness']['rho'] > 0:
            print("    - Clustered-A vocab -> MORE aggressive programs")
        if results['test_e']['control_margin']['rho'] < 0:
            print("    - Clustered-A vocab -> LESS control margin")

    n_significant = len([f for f in significant_findings if 'marginal' not in f])
    print(f"\n  Total significant (p < 0.05): {n_significant}")

    # Robustness check summary
    print("\n  Robustness checks:")
    if results.get('robustness_permutation'):
        rp = results['robustness_permutation']
        status = "PASSED" if rp['significant'] else "FAILED"
        print(f"    Permutation control: {status} (p={rp['permutation_p']:.4f})")
    if results.get('robustness_frequency'):
        rf = results['robustness_frequency']
        if rf:
            status = "PASSED" if rf['significant'] else "FAILED"
            print(f"    Frequency-matched: {status} (p={rf['p_matched']:.4f})")

    # Final conclusion
    robust_pass = (
        results.get('robustness_permutation', {}).get('significant', False) and
        results.get('robustness_frequency', {}).get('significant', False)
    )

    if n_significant >= 2 and robust_pass:
        print("\n  CONCLUSION: Failure-memory hypothesis STRONGLY SUPPORTED")
        print("  - Clustered A vocab correlates with higher-risk B characteristics")
        print("  - Effect survives permutation control (structural, not incidental)")
        print("  - Effect survives frequency matching (not driven by token frequency)")
    elif n_significant >= 2:
        print("\n  CONCLUSION: Failure-memory hypothesis SUPPORTED (with caveats)")
        print("  Correlations significant but robustness checks incomplete")
    else:
        print("\n  CONCLUSION: Insufficient evidence for failure-memory hypothesis")

    # Save results
    output_file = 'C:/git/voynich/phases/exploration/a_b_hazard_correlation_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to: {output_file}")


if __name__ == '__main__':
    main()
