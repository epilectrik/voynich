#!/usr/bin/env python3
"""
HT_MORPHOLOGICAL_CURRICULUM Phase

Tests whether HT morphological patterns follow a curriculum structure.

Constraint Compliance:
- C404-C405: Tests examine patterns, not execution effects
- C413: Controls for grammar triggering
- C477: Curriculum operates within tail correlation envelope

Data Loading:
- H-track only (PRIMARY transcriber)
- TEXT placement only (P*) - excludes labels, rings, circles
- Filters asterisk tokens
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats
from scipy.stats import spearmanr, ks_2samp
import json
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
OUTPUT_PATH = PROJECT_ROOT / 'phases' / 'HT_MORPHOLOGICAL_CURRICULUM' / 'results'
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# HT Prefixes (from C347)
HT_PREFIXES_LONG = ['ykch', 'yche', 'ypch', 'ytch', 'ysh', 'ych', 'ypc', 'yph', 'yth']
HT_PREFIXES_SHORT = ['yk', 'yt', 'yp', 'yd', 'yf', 'yr', 'ys', 'yo', 'y']
HT_PREFIXES_OTHER = ['op', 'sa', 'so', 'ka', 'dc', 'pc', 'do', 'ta']
ALL_HT_PREFIXES = sorted(HT_PREFIXES_LONG + HT_PREFIXES_SHORT + HT_PREFIXES_OTHER, key=len, reverse=True)

# A/B Prefixes (for exclusion check)
AB_PREFIXES = {'ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol', 'al', 'ar', 'or'}

# =============================================================================
# DATA LOADING (Optimized)
# =============================================================================

def load_data():
    """Load transcript with H-only filter and TEXT placement."""
    print("=" * 70)
    print("HT MORPHOLOGICAL CURRICULUM ANALYSIS")
    print("=" * 70)
    print()

    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)

    # PRIMARY track only
    df = df[df['transcriber'] == 'H'].copy()
    print(f"H-track tokens: {len(df)}")

    # TEXT placement only (P*) - exclude labels, rings, circles
    df = df[df['placement'].fillna('').str.startswith('P')]
    print(f"TEXT placement tokens: {len(df)}")

    # Clean tokens
    df = df[df['word'].notna()]
    df = df[~df['word'].str.contains(r'\*', regex=True, na=False)]
    df = df[df['word'].str.len() > 0]

    # Reset index for sequential position
    df = df.reset_index(drop=True)
    df['global_position'] = df.index
    df['normalized_position'] = df['global_position'] / len(df)

    print(f"Clean tokens: {len(df)}")
    print(f"Unique words: {df['word'].nunique()}")
    print(f"Folios: {df['folio'].nunique()}")

    return df

# =============================================================================
# HT IDENTIFICATION (Vectorized)
# =============================================================================

def identify_ht_tokens(df):
    """Identify HT tokens using vectorized operations."""
    words = df['word'].str.lower().str.strip()

    # Single-char HT atoms
    is_atom = words.isin({'y', 'f', 'd', 'r', 's'})

    # Starts with y
    starts_y = words.str.startswith('y', na=False)

    # Non-y HT prefixes (excluding those that overlap with A/B)
    starts_other = pd.Series(False, index=df.index)
    for prefix in HT_PREFIXES_OTHER:
        mask = words.str.startswith(prefix, na=False)
        # Check not A/B prefix
        for ab in AB_PREFIXES:
            if prefix.startswith(ab[:2]):
                mask = mask & ~words.str.startswith(ab, na=False)
        starts_other = starts_other | mask

    return is_atom | starts_y | starts_other

def get_ht_family(word):
    """Extract HT family from token."""
    if pd.isna(word):
        return 'other'
    word = str(word).lower().strip()

    if word in ('y', 'f', 'd', 'r', 's'):
        return word

    for prefix in ALL_HT_PREFIXES:
        if word.startswith(prefix):
            if prefix.startswith('y') and len(prefix) >= 2:
                return prefix[:2]
            return prefix

    return 'other'

def prepare_ht_data(df):
    """Extract and prepare HT tokens."""
    print("\n" + "=" * 70)
    print("STEP 1: IDENTIFY HT TOKENS")
    print("=" * 70)

    df['is_ht'] = identify_ht_tokens(df)
    ht_df = df[df['is_ht']].copy()

    print(f"\nHT tokens: {len(ht_df)} ({100*len(ht_df)/len(df):.2f}%)")
    print(f"Unique HT types: {ht_df['word'].nunique()}")

    # Add family
    ht_df['family'] = ht_df['word'].apply(get_ht_family)

    # Token frequency and difficulty
    token_counts = ht_df['word'].value_counts()
    ht_df['token_freq'] = ht_df['word'].map(token_counts)
    ht_df['difficulty'] = -np.log(ht_df['token_freq'] / len(ht_df))

    # Complexity: length + rarity (normalized)
    ht_df['length'] = ht_df['word'].str.len()
    max_diff = ht_df['difficulty'].max()
    max_len = ht_df['length'].max()
    ht_df['complexity'] = (ht_df['difficulty']/max_diff + ht_df['length']/max_len) / 2

    # Family stats
    print(f"\nFamily distribution:")
    for fam, count in ht_df['family'].value_counts().head(10).items():
        print(f"  {fam}: {count} ({100*count/len(ht_df):.1f}%)")

    return df, ht_df

# =============================================================================
# TEST 1: INTRODUCTION SEQUENCING
# =============================================================================

def test_introduction_sequencing(ht_df):
    """Test whether families are introduced at structured intervals."""
    print("\n" + "=" * 70)
    print("TEST 1: INTRODUCTION SEQUENCING")
    print("=" * 70)

    # First appearance for each family
    first_pos = ht_df.groupby('family')['normalized_position'].min().sort_values()
    positions = first_pos.values
    n = len(positions)

    print(f"\nFamilies: {n}")
    for fam, pos in first_pos.head(10).items():
        print(f"  {fam}: {pos:.4f}")

    # KS test vs uniform
    ks_stat, ks_pval = ks_2samp(positions, np.linspace(0, 1, n))

    # Spacing regularity
    spacings = np.diff(positions)
    spacing_cv = np.std(spacings) / np.mean(spacings) if len(spacings) > 1 else 0

    print(f"\n--- Results ---")
    print(f"KS statistic: {ks_stat:.4f}, p-value: {ks_pval:.4f}")
    print(f"Spacing CV: {spacing_cv:.4f}")

    if ks_stat > 0.35 and ks_pval < 0.01:
        verdict = "STRONG PASS"
    elif ks_stat > 0.20 and ks_pval < 0.05:
        verdict = "WEAK PASS"
    else:
        verdict = "FAIL"

    print(f"Verdict: {verdict}")
    return {'test': 'introduction_sequencing', 'n_families': n,
            'ks_statistic': float(ks_stat), 'ks_pvalue': float(ks_pval),
            'spacing_cv': float(spacing_cv), 'verdict': verdict}

# =============================================================================
# TEST 2: SPACED REPETITION
# =============================================================================

def test_spaced_repetition(ht_df):
    """Test whether rare forms show spaced repetition pattern."""
    print("\n" + "=" * 70)
    print("TEST 2: SPACED REPETITION")
    print("=" * 70)

    token_counts = ht_df['word'].value_counts()

    # Rare tokens with enough occurrences for interval analysis
    rare_tokens = token_counts[(token_counts >= 4) & (token_counts <= token_counts.quantile(0.3))].index[:30]

    print(f"\nRare tokens (4+ occurrences, bottom 30%): {len(rare_tokens)}")

    if len(rare_tokens) < 5:
        return {'test': 'spaced_repetition', 'verdict': 'UNDERPOWERED', 'n_tokens': len(rare_tokens)}

    # Compute interval autocorrelations
    autocorrs = []
    growth_slopes = []

    for token in rare_tokens:
        positions = ht_df[ht_df['word'] == token]['global_position'].values
        if len(positions) < 4:
            continue

        intervals = np.diff(positions)

        # Lag-1 autocorrelation
        if len(intervals) >= 3:
            ac = np.corrcoef(intervals[:-1], intervals[1:])[0, 1]
            if not np.isnan(ac):
                autocorrs.append(ac)

        # Growth slope
        if len(intervals) >= 3:
            slope, _, _, _, _ = stats.linregress(range(len(intervals)), intervals)
            growth_slopes.append(slope)

    if not autocorrs:
        return {'test': 'spaced_repetition', 'verdict': 'UNDERPOWERED', 'n_tokens': len(rare_tokens)}

    mean_ac = np.mean(autocorrs)
    mean_growth = np.mean(growth_slopes) if growth_slopes else 0

    # T-test: is mean autocorr > 0?
    t_stat, t_pval = stats.ttest_1samp(autocorrs, 0)

    print(f"\n--- Results ---")
    print(f"Tokens analyzed: {len(autocorrs)}")
    print(f"Mean autocorrelation: {mean_ac:.4f}")
    print(f"T-test p-value: {t_pval:.4f}")
    print(f"Mean growth slope: {mean_growth:.2f}")

    if mean_ac > 0.2 and t_pval < 0.01:
        verdict = "STRONG PASS"
    elif (mean_ac > 0.1 and t_pval < 0.05) or mean_growth > 0:
        verdict = "WEAK PASS"
    else:
        verdict = "FAIL"

    print(f"Verdict: {verdict}")
    return {'test': 'spaced_repetition', 'n_analyzed': len(autocorrs),
            'mean_autocorr': float(mean_ac), 'pvalue': float(t_pval),
            'mean_growth': float(mean_growth), 'verdict': verdict}

# =============================================================================
# TEST 3: BLOCK COMPLEXITY GRADIENT
# =============================================================================

def test_block_complexity(ht_df, full_df):
    """Test complexity gradients within HT runs."""
    print("\n" + "=" * 70)
    print("TEST 3: BLOCK COMPLEXITY GRADIENT")
    print("=" * 70)

    GAP_THRESHOLD = 3
    MIN_BLOCK = 5

    # Find HT blocks using vectorized approach
    ht_positions = ht_df['global_position'].values

    # Identify block boundaries (gaps > threshold)
    gaps = np.diff(ht_positions)
    break_points = np.where(gaps > GAP_THRESHOLD + 1)[0] + 1

    # Split into blocks
    block_starts = np.concatenate([[0], break_points])
    block_ends = np.concatenate([break_points, [len(ht_positions)]])

    blocks = []
    for start, end in zip(block_starts, block_ends):
        if end - start >= MIN_BLOCK:
            blocks.append(ht_positions[start:end])

    print(f"\nBlocks (min size {MIN_BLOCK}): {len(blocks)}")

    if len(blocks) < 15:
        return {'test': 'block_complexity', 'verdict': 'UNDERPOWERED', 'n_blocks': len(blocks)}

    # Classify trajectories
    trajectories = {'increasing': 0, 'decreasing': 0, 'flat': 0}
    rhos = []

    for block_pos in blocks:
        block_data = ht_df[ht_df['global_position'].isin(block_pos)].sort_values('global_position')
        if len(block_data) < MIN_BLOCK:
            continue

        complexity = block_data['complexity'].values
        rho, _ = spearmanr(range(len(complexity)), complexity)
        rhos.append(rho)

        if rho > 0.25:
            trajectories['increasing'] += 1
        elif rho < -0.25:
            trajectories['decreasing'] += 1
        else:
            trajectories['flat'] += 1

    total = sum(trajectories.values())

    print(f"\n--- Trajectories ---")
    for traj, count in sorted(trajectories.items(), key=lambda x: -x[1]):
        print(f"  {traj}: {count} ({100*count/total:.1f}%)")

    # Chi-square vs uniform
    observed = list(trajectories.values())
    expected = [total/3] * 3
    chi2, chi2_p = stats.chisquare(observed, expected)

    dominant = max(trajectories, key=trajectories.get)
    dominant_pct = 100 * trajectories[dominant] / total
    mean_rho = np.mean(rhos)

    print(f"\nChi-square: {chi2:.2f}, p={chi2_p:.4f}")
    print(f"Dominant: {dominant} ({dominant_pct:.1f}%)")
    print(f"Mean rho: {mean_rho:.4f}")

    if dominant_pct > 40 and chi2_p < 0.001:
        verdict = "STRONG PASS"
    elif dominant_pct > 30 and chi2_p < 0.01:
        verdict = "WEAK PASS"
    else:
        verdict = "FAIL"

    print(f"Verdict: {verdict}")
    return {'test': 'block_complexity', 'n_blocks': len(blocks),
            'trajectories': trajectories, 'chi2': float(chi2), 'chi2_p': float(chi2_p),
            'dominant': dominant, 'dominant_pct': float(dominant_pct),
            'mean_rho': float(mean_rho), 'verdict': verdict}

# =============================================================================
# TEST 4: FAMILY ROTATION
# =============================================================================

def test_family_rotation(ht_df):
    """Test family switching periodicity."""
    print("\n" + "=" * 70)
    print("TEST 4: FAMILY ROTATION")
    print("=" * 70)

    families = ht_df.sort_values('global_position')['family'].values
    n = len(families)

    # Compute recurrence times (vectorized)
    family_indices = defaultdict(list)
    for i, fam in enumerate(families):
        family_indices[fam].append(i)

    all_recurrence = []
    for fam, indices in family_indices.items():
        if len(indices) >= 2:
            recurrence = np.diff(indices)
            all_recurrence.extend(recurrence)

    if not all_recurrence:
        return {'test': 'family_rotation', 'verdict': 'UNDERPOWERED'}

    mean_rec = np.mean(all_recurrence)
    rec_cv = np.std(all_recurrence) / mean_rec

    print(f"\nMean recurrence: {mean_rec:.2f}")
    print(f"Recurrence CV: {rec_cv:.4f}")

    # ACF at various lags (vectorized)
    unique_fams = list(set(families))
    fam_to_int = {f: i for i, f in enumerate(unique_fams)}
    int_seq = np.array([fam_to_int[f] for f in families])
    n_fams = len(unique_fams)
    expected_match = 1 / n_fams

    acf = []
    max_lag = min(30, n // 20)
    for lag in range(1, max_lag + 1):
        matches = np.mean(int_seq[:-lag] == int_seq[lag:])
        acf.append(matches - expected_match)

    # Find peaks
    acf_arr = np.array(acf)
    peaks = []
    for i in range(1, len(acf_arr) - 1):
        if acf_arr[i] > acf_arr[i-1] and acf_arr[i] > acf_arr[i+1] and acf_arr[i] > 0.01:
            peaks.append(i + 1)

    print(f"ACF peaks at lags: {peaks[:5] if peaks else 'None'}")

    # Compare CV to random expectation (~1.0 for geometric)
    cv_ratio = rec_cv / 1.0

    print(f"CV ratio vs geometric: {cv_ratio:.4f}")

    if cv_ratio < 0.8 and len(peaks) >= 2:
        verdict = "STRONG PASS"
    elif cv_ratio < 0.9 or len(peaks) >= 1:
        verdict = "WEAK PASS"
    else:
        verdict = "FAIL"

    print(f"Verdict: {verdict}")
    return {'test': 'family_rotation', 'mean_recurrence': float(mean_rec),
            'recurrence_cv': float(rec_cv), 'cv_ratio': float(cv_ratio),
            'acf_peaks': peaks[:5], 'verdict': verdict}

# =============================================================================
# TEST 5: DIFFICULTY GRADIENT
# =============================================================================

def test_difficulty_gradient(ht_df):
    """Test temporal scaffolding of difficulty."""
    print("\n" + "=" * 70)
    print("TEST 5: DIFFICULTY GRADIENT")
    print("=" * 70)

    # Mean position per token
    token_stats = ht_df.groupby('word').agg({
        'normalized_position': 'mean',
        'difficulty': 'first'
    })

    print(f"\nUnique tokens: {len(token_stats)}")

    # Correlation
    rho, rho_p = spearmanr(token_stats['difficulty'], token_stats['normalized_position'])

    print(f"\nSpearman rho: {rho:.4f}, p={rho_p:.4f}")

    # Zone analysis
    token_stats['zone'] = pd.cut(token_stats['normalized_position'],
                                  bins=[0, 0.33, 0.67, 1.0],
                                  labels=['early', 'middle', 'late'])

    zone_diff = token_stats.groupby('zone')['difficulty'].mean()

    print("\nMean difficulty by zone:")
    for z, d in zone_diff.items():
        print(f"  {z}: {d:.4f}")

    # Kruskal-Wallis
    groups = [token_stats[token_stats['zone'] == z]['difficulty'] for z in ['early', 'middle', 'late']]
    h_stat, h_p = stats.kruskal(*groups)

    print(f"\nKruskal-Wallis H={h_stat:.2f}, p={h_p:.4f}")

    if (abs(rho) > 0.3 and rho_p < 0.01) or (h_stat > 10 and h_p < 0.01):
        verdict = "STRONG PASS"
    elif (abs(rho) > 0.15 and rho_p < 0.05) or (h_stat > 6 and h_p < 0.05):
        verdict = "WEAK PASS"
    else:
        verdict = "FAIL"

    print(f"Verdict: {verdict}")
    return {'test': 'difficulty_gradient', 'n_tokens': len(token_stats),
            'spearman_rho': float(rho), 'spearman_p': float(rho_p),
            'kruskal_h': float(h_stat), 'kruskal_p': float(h_p),
            'zone_difficulties': {str(k): float(v) for k, v in zone_diff.items()},
            'verdict': verdict}

# =============================================================================
# TEST 6: PREREQUISITE STRUCTURE (Optimized)
# =============================================================================

def test_prerequisite_structure(ht_df):
    """Test for precedence relationships between forms."""
    print("\n" + "=" * 70)
    print("TEST 6: PREREQUISITE STRUCTURE")
    print("=" * 70)

    # Use families instead of individual tokens for efficiency
    # This reduces from O(n² tokens) to O(n² families) where n_families << n_tokens

    folios = ht_df['folio'].unique()
    families = ht_df['family'].unique()
    n_fams = len(families)

    print(f"\nFolios: {len(folios)}, Families: {n_fams}")

    # Build first-occurrence matrix: for each folio, which family appears first?
    precedence = defaultdict(lambda: defaultdict(int))
    cooccurrence = defaultdict(lambda: defaultdict(int))

    for folio in folios:
        folio_df = ht_df[ht_df['folio'] == folio].sort_values('global_position')
        fam_order = folio_df['family'].drop_duplicates().values

        # Record precedence for all pairs
        for i, fam_a in enumerate(fam_order):
            for fam_b in fam_order[i+1:]:
                precedence[fam_a][fam_b] += 1
                cooccurrence[fam_a][fam_b] += 1
                cooccurrence[fam_b][fam_a] += 1

    # Find significant precedence pairs
    significant = []
    for fam_a in precedence:
        for fam_b, count in precedence[fam_a].items():
            total = cooccurrence[fam_a][fam_b]
            if total >= 5:
                ratio = count / total
                if ratio > 0.75:
                    significant.append((fam_a, fam_b, ratio, total))

    print(f"\nSignificant precedence pairs (>75%, min 5 co-occur): {len(significant)}")

    if significant:
        print("\nTop relationships:")
        for a, b, r, n in sorted(significant, key=lambda x: -x[2])[:8]:
            print(f"  {a} -> {b}: {r:.2f} (n={n})")

    # Simple null expectation: ~50% A before B by chance
    # Significant pairs should be rare under null
    n_possible_pairs = n_fams * (n_fams - 1) // 2
    expected_by_chance = n_possible_pairs * 0.05  # ~5% expected at 75% threshold by chance

    print(f"\nExpected by chance (~5%): {expected_by_chance:.1f}")
    print(f"Observed: {len(significant)}")

    # Compute transitivity
    trans_count = 0
    trans_tests = 0
    sig_dict = {(a, b): r for a, b, r, _ in significant}

    for a, b, _, _ in significant:
        for _, c, _, _ in significant:
            if b == _:  # A->B and B->C
                trans_tests += 1
                if (a, c) in sig_dict:
                    trans_count += 1

    trans_rate = trans_count / trans_tests if trans_tests > 0 else 0
    print(f"Transitivity: {trans_count}/{trans_tests} = {trans_rate:.2f}")

    if len(significant) > expected_by_chance * 2 and trans_rate > 0.4:
        verdict = "STRONG PASS"
    elif len(significant) > expected_by_chance * 1.5 or trans_rate > 0.25:
        verdict = "WEAK PASS"
    else:
        verdict = "FAIL"

    print(f"Verdict: {verdict}")
    return {'test': 'prerequisite_structure', 'n_families': n_fams,
            'significant_pairs': len(significant), 'expected_by_chance': float(expected_by_chance),
            'transitivity': float(trans_rate), 'verdict': verdict}

# =============================================================================
# MAIN
# =============================================================================

def main():
    full_df = load_data()
    full_df, ht_df = prepare_ht_data(full_df)

    results = {}
    results['test_1'] = test_introduction_sequencing(ht_df)
    results['test_2'] = test_spaced_repetition(ht_df)
    results['test_3'] = test_block_complexity(ht_df, full_df)
    results['test_4'] = test_family_rotation(ht_df)
    results['test_5'] = test_difficulty_gradient(ht_df)
    results['test_6'] = test_prerequisite_structure(ht_df)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    verdicts = [r.get('verdict', 'N/A') for r in results.values()]
    for name, r in results.items():
        print(f"{r.get('test', name)}: {r.get('verdict', 'N/A')}")

    strong = sum(1 for v in verdicts if v == 'STRONG PASS')
    weak = sum(1 for v in verdicts if v == 'WEAK PASS')
    fail = sum(1 for v in verdicts if v == 'FAIL')

    print(f"\nSTRONG: {strong}, WEAK: {weak}, FAIL: {fail}")

    total_pass = strong + weak
    if total_pass >= 4:
        overall = "CURRICULUM STRUCTURE CONFIRMED"
    elif total_pass >= 3:
        overall = "PARTIAL CURRICULUM EVIDENCE"
    else:
        overall = "CURRICULUM HYPOTHESIS NOT SUPPORTED"

    print(f"\n*** {overall} ***")

    results['summary'] = {'strong': strong, 'weak': weak, 'fail': fail, 'overall': overall}

    with open(OUTPUT_PATH / 'ht_curriculum_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nSaved: {OUTPUT_PATH / 'ht_curriculum_results.json'}")
    return results

if __name__ == '__main__':
    main()
