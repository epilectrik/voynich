"""
Phase BVP: B-Folio Vocabulary Patterns

Core Question: How do B folios relate to each other vocabularily?

Tests:
- BVP-1: Adjacent vs non-adjacent vocabulary sharing
- BVP-2: Regime-based vocabulary clustering
- BVP-3: Stability profile vocabulary clustering
- BVP-4: Vocabulary uniqueness distribution
"""

import json
import csv
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
import random

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
REGIME_FILE = BASE / "phases" / "OPS2_control_strategy_clustering" / "ops2_folio_cluster_assignments.json"
CONTROL_SIGS = BASE / "results" / "control_signatures.json"
OPS3_FILE = BASE / "phases" / "OPS3_risk_time_stability_tradeoffs" / "ops3_tradeoff_models.json"

def load_transcription():
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            data.append(row)
    return data

def load_regimes():
    with open(REGIME_FILE, 'r') as f:
        data = json.load(f)
    return data['assignments']

def load_control_signatures():
    with open(CONTROL_SIGS, 'r') as f:
        data = json.load(f)
    return data['signatures']

def load_stability_data():
    with open(OPS3_FILE, 'r') as f:
        data = json.load(f)
    return data['folio_normalized_axes']

def get_b_folios(data):
    """Get Currier B data with transcriber H."""
    b_data = []
    for row in data:
        if row.get('language') == 'B' and row.get('transcriber') == 'H':
            b_data.append(row)
    return b_data

def build_folio_vocabularies(b_data):
    """Build vocabulary set for each B folio."""
    folio_vocab = defaultdict(set)
    for row in b_data:
        folio = row['folio']
        word = row['word']
        if word and word.strip():
            folio_vocab[folio].add(word)
    return dict(folio_vocab)

def jaccard(set1, set2):
    """Compute Jaccard similarity."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def get_folio_order(folios):
    """Sort folios in manuscript order."""
    def folio_key(f):
        # Extract number and suffix
        import re
        match = re.match(r'f(\d+)([rv]?)(\d*)', f)
        if match:
            num = int(match.group(1))
            side = 0 if match.group(2) == 'r' else 1
            sub = int(match.group(3)) if match.group(3) else 0
            return (num, side, sub)
        return (999, 0, 0)
    return sorted(folios, key=folio_key)

def test_bvp1_adjacent_sharing(folio_vocab):
    """BVP-1: Test if adjacent folios share more vocabulary."""
    print("\n" + "="*60)
    print("BVP-1: ADJACENT VS NON-ADJACENT VOCABULARY SHARING")
    print("="*60)

    folios = get_folio_order(list(folio_vocab.keys()))
    n = len(folios)

    # Compute adjacent similarities
    adjacent_sims = []
    for i in range(n - 1):
        f1, f2 = folios[i], folios[i+1]
        if f1 in folio_vocab and f2 in folio_vocab:
            sim = jaccard(folio_vocab[f1], folio_vocab[f2])
            adjacent_sims.append(sim)

    # Compute non-adjacent similarities (random sample)
    non_adjacent_sims = []
    random.seed(42)
    for _ in range(1000):
        i, j = random.sample(range(n), 2)
        if abs(i - j) > 1:  # Non-adjacent
            f1, f2 = folios[i], folios[j]
            if f1 in folio_vocab and f2 in folio_vocab:
                sim = jaccard(folio_vocab[f1], folio_vocab[f2])
                non_adjacent_sims.append(sim)

    adj_mean = np.mean(adjacent_sims)
    non_adj_mean = np.mean(non_adjacent_sims)

    # Mann-Whitney U test
    stat, p_value = stats.mannwhitneyu(adjacent_sims, non_adjacent_sims, alternative='greater')

    # Effect size (Cohen's d)
    pooled_std = np.sqrt((np.std(adjacent_sims)**2 + np.std(non_adjacent_sims)**2) / 2)
    effect_d = (adj_mean - non_adj_mean) / pooled_std if pooled_std > 0 else 0

    print(f"\nAdjacent pairs: {len(adjacent_sims)}")
    print(f"Non-adjacent samples: {len(non_adjacent_sims)}")
    print(f"\nMean Jaccard similarity:")
    print(f"  Adjacent:     {adj_mean:.4f}")
    print(f"  Non-adjacent: {non_adj_mean:.4f}")
    print(f"  Ratio:        {adj_mean/non_adj_mean:.2f}x")
    print(f"\nMann-Whitney U p-value: {p_value:.6f}")
    print(f"Effect size (Cohen's d): {effect_d:.3f}")

    if p_value < 0.01 and effect_d > 0.3:
        verdict = "SIGNAL - Adjacent folios share MORE vocabulary"
    elif p_value < 0.05:
        verdict = "WEAK SIGNAL - Some sequential sharing detected"
    else:
        verdict = "NULL - No sequential vocabulary pattern"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'BVP-1',
        'adjacent_pairs': len(adjacent_sims),
        'non_adjacent_samples': len(non_adjacent_sims),
        'adjacent_mean': adj_mean,
        'non_adjacent_mean': non_adj_mean,
        'ratio': adj_mean / non_adj_mean if non_adj_mean > 0 else 0,
        'mann_whitney_p': p_value,
        'effect_d': effect_d,
        'verdict': verdict
    }

def test_bvp2_regime_clustering(folio_vocab, regimes):
    """BVP-2: Test if same-regime folios share more vocabulary."""
    print("\n" + "="*60)
    print("BVP-2: REGIME-BASED VOCABULARY CLUSTERING")
    print("="*60)

    # Map folios to regimes
    folio_regime = {f: regimes[f]['cluster_id'] for f in folio_vocab if f in regimes}
    regime_folios = defaultdict(list)
    for f, r in folio_regime.items():
        regime_folios[r].append(f)

    print(f"\nRegime distribution:")
    for r in sorted(regime_folios.keys()):
        print(f"  {r}: {len(regime_folios[r])} folios")

    # Within-regime similarities
    within_sims = []
    for regime, folios in regime_folios.items():
        if len(folios) >= 2:
            for i in range(len(folios)):
                for j in range(i+1, len(folios)):
                    sim = jaccard(folio_vocab[folios[i]], folio_vocab[folios[j]])
                    within_sims.append(sim)

    # Between-regime similarities
    between_sims = []
    regimes_list = list(regime_folios.keys())
    for i in range(len(regimes_list)):
        for j in range(i+1, len(regimes_list)):
            r1_folios = regime_folios[regimes_list[i]]
            r2_folios = regime_folios[regimes_list[j]]
            for f1 in r1_folios:
                for f2 in r2_folios:
                    sim = jaccard(folio_vocab[f1], folio_vocab[f2])
                    between_sims.append(sim)

    within_mean = np.mean(within_sims)
    between_mean = np.mean(between_sims)
    ratio = within_mean / between_mean if between_mean > 0 else 0

    # Permutation test
    all_folios = list(folio_regime.keys())
    null_ratios = []
    random.seed(42)
    for _ in range(1000):
        # Shuffle regime assignments
        shuffled_regimes = list(folio_regime.values())
        random.shuffle(shuffled_regimes)
        temp_regime = dict(zip(all_folios, shuffled_regimes))

        temp_within = []
        temp_between = []
        temp_regime_folios = defaultdict(list)
        for f, r in temp_regime.items():
            temp_regime_folios[r].append(f)

        for r, folios in temp_regime_folios.items():
            if len(folios) >= 2:
                for i in range(min(3, len(folios))):  # Sample for speed
                    for j in range(i+1, min(4, len(folios))):
                        sim = jaccard(folio_vocab[folios[i]], folio_vocab[folios[j]])
                        temp_within.append(sim)

        for i in range(len(regimes_list)):
            for j in range(i+1, len(regimes_list)):
                r1_folios = temp_regime_folios[regimes_list[i]][:3]
                r2_folios = temp_regime_folios[regimes_list[j]][:3]
                for f1 in r1_folios:
                    for f2 in r2_folios:
                        if f1 in folio_vocab and f2 in folio_vocab:
                            sim = jaccard(folio_vocab[f1], folio_vocab[f2])
                            temp_between.append(sim)

        if temp_within and temp_between:
            null_ratio = np.mean(temp_within) / np.mean(temp_between)
            null_ratios.append(null_ratio)

    p_value = sum(1 for r in null_ratios if r >= ratio) / len(null_ratios) if null_ratios else 1.0

    print(f"\nWithin-regime pairs: {len(within_sims)}")
    print(f"Between-regime pairs: {len(between_sims)}")
    print(f"\nMean Jaccard similarity:")
    print(f"  Within-regime:  {within_mean:.4f}")
    print(f"  Between-regime: {between_mean:.4f}")
    print(f"  Ratio:          {ratio:.3f}")
    print(f"\nPermutation test p-value: {p_value:.4f}")

    if ratio > 1.2 and p_value < 0.01:
        verdict = "SIGNAL - Regimes have vocabulary fingerprints"
    elif ratio > 1.1 and p_value < 0.05:
        verdict = "WEAK SIGNAL - Some regime vocabulary clustering"
    else:
        verdict = "NULL - Regimes not defined by vocabulary"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'BVP-2',
        'within_pairs': len(within_sims),
        'between_pairs': len(between_sims),
        'within_mean': within_mean,
        'between_mean': between_mean,
        'ratio': ratio,
        'permutation_p': p_value,
        'verdict': verdict
    }

def test_bvp3_stability_clustering(folio_vocab, stability_data, control_sigs):
    """BVP-3: Test if similar stability profiles share vocabulary."""
    print("\n" + "="*60)
    print("BVP-3: STABILITY PROFILE VOCABULARY CLUSTERING")
    print("="*60)

    # Bin folios by stability (quartiles)
    stabilities = {}
    for f in folio_vocab:
        if f in stability_data:
            stabilities[f] = stability_data[f]['stability']

    if not stabilities:
        print("No stability data available")
        return {'test': 'BVP-3', 'verdict': 'SKIP - No data'}

    # Create stability bins
    stability_values = list(stabilities.values())
    q25, q50, q75 = np.percentile(stability_values, [25, 50, 75])

    def get_bin(s):
        if s <= q25:
            return 'LOW'
        elif s <= q50:
            return 'MED_LOW'
        elif s <= q75:
            return 'MED_HIGH'
        else:
            return 'HIGH'

    stability_bins = {f: get_bin(s) for f, s in stabilities.items()}
    bin_folios = defaultdict(list)
    for f, b in stability_bins.items():
        bin_folios[b].append(f)

    print(f"\nStability quartile distribution:")
    for b in ['LOW', 'MED_LOW', 'MED_HIGH', 'HIGH']:
        if b in bin_folios:
            print(f"  {b}: {len(bin_folios[b])} folios")

    # Within-bin similarities
    within_sims = []
    for bin_name, folios in bin_folios.items():
        if len(folios) >= 2:
            for i in range(len(folios)):
                for j in range(i+1, len(folios)):
                    if folios[i] in folio_vocab and folios[j] in folio_vocab:
                        sim = jaccard(folio_vocab[folios[i]], folio_vocab[folios[j]])
                        within_sims.append(sim)

    # Between-bin similarities
    between_sims = []
    bins_list = list(bin_folios.keys())
    for i in range(len(bins_list)):
        for j in range(i+1, len(bins_list)):
            b1_folios = bin_folios[bins_list[i]]
            b2_folios = bin_folios[bins_list[j]]
            for f1 in b1_folios:
                for f2 in b2_folios:
                    if f1 in folio_vocab and f2 in folio_vocab:
                        sim = jaccard(folio_vocab[f1], folio_vocab[f2])
                        between_sims.append(sim)

    within_mean = np.mean(within_sims) if within_sims else 0
    between_mean = np.mean(between_sims) if between_sims else 0
    ratio = within_mean / between_mean if between_mean > 0 else 0

    # Also test LINK profile
    print("\n--- LINK Profile Analysis ---")
    link_densities = {}
    for f in folio_vocab:
        if f in control_sigs:
            link_densities[f] = control_sigs[f].get('link_density', 0)

    if link_densities:
        link_values = list(link_densities.values())
        lq25, lq50, lq75 = np.percentile(link_values, [25, 50, 75])

        def get_link_bin(l):
            if l <= lq25:
                return 'SPARSE'
            elif l <= lq75:
                return 'MODERATE'
            else:
                return 'HEAVY'

        link_bins = {f: get_link_bin(l) for f, l in link_densities.items()}
        link_bin_folios = defaultdict(list)
        for f, b in link_bins.items():
            link_bin_folios[b].append(f)

        print(f"\nLINK density distribution:")
        for b in ['SPARSE', 'MODERATE', 'HEAVY']:
            if b in link_bin_folios:
                print(f"  {b}: {len(link_bin_folios[b])} folios")

        # Within-link-bin similarities
        link_within = []
        for bin_name, folios in link_bin_folios.items():
            if len(folios) >= 2:
                for i in range(len(folios)):
                    for j in range(i+1, len(folios)):
                        if folios[i] in folio_vocab and folios[j] in folio_vocab:
                            sim = jaccard(folio_vocab[folios[i]], folio_vocab[folios[j]])
                            link_within.append(sim)

        link_between = []
        link_bins_list = list(link_bin_folios.keys())
        for i in range(len(link_bins_list)):
            for j in range(i+1, len(link_bins_list)):
                b1 = link_bin_folios[link_bins_list[i]]
                b2 = link_bin_folios[link_bins_list[j]]
                for f1 in b1:
                    for f2 in b2:
                        if f1 in folio_vocab and f2 in folio_vocab:
                            sim = jaccard(folio_vocab[f1], folio_vocab[f2])
                            link_between.append(sim)

        link_within_mean = np.mean(link_within) if link_within else 0
        link_between_mean = np.mean(link_between) if link_between else 0
        link_ratio = link_within_mean / link_between_mean if link_between_mean > 0 else 0

        print(f"\nLINK profile vocabulary sharing:")
        print(f"  Within-profile:  {link_within_mean:.4f}")
        print(f"  Between-profile: {link_between_mean:.4f}")
        print(f"  Ratio:           {link_ratio:.3f}")
    else:
        link_ratio = 0

    print(f"\n--- Stability Profile Summary ---")
    print(f"Within-bin pairs: {len(within_sims)}")
    print(f"Between-bin pairs: {len(between_sims)}")
    print(f"\nMean Jaccard similarity:")
    print(f"  Within-stability:  {within_mean:.4f}")
    print(f"  Between-stability: {between_mean:.4f}")
    print(f"  Ratio:             {ratio:.3f}")

    if ratio > 1.2 or link_ratio > 1.2:
        verdict = "SIGNAL - Operational profiles share vocabulary"
    elif ratio > 1.1 or link_ratio > 1.1:
        verdict = "WEAK SIGNAL - Some operational vocabulary clustering"
    else:
        verdict = "NULL - Vocabulary independent of operational profile"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'BVP-3',
        'stability_within_mean': within_mean,
        'stability_between_mean': between_mean,
        'stability_ratio': ratio,
        'link_ratio': link_ratio,
        'verdict': verdict
    }

def test_bvp4_uniqueness_distribution(folio_vocab):
    """BVP-4: Analyze vocabulary uniqueness distribution."""
    print("\n" + "="*60)
    print("BVP-4: VOCABULARY UNIQUENESS DISTRIBUTION")
    print("="*60)

    n_folios = len(folio_vocab)

    # Count token occurrences across folios
    token_folio_count = Counter()
    for folio, vocab in folio_vocab.items():
        for token in vocab:
            token_folio_count[token] += 1

    # For each folio, compute metrics
    folio_metrics = {}
    for folio, vocab in folio_vocab.items():
        vocab_size = len(vocab)

        # Core vocabulary: appears in >= 50% of folios
        core_count = sum(1 for t in vocab if token_folio_count[t] >= n_folios * 0.5)
        core_pct = core_count / vocab_size if vocab_size > 0 else 0

        # Unique vocabulary: appears only in this folio
        unique_count = sum(1 for t in vocab if token_folio_count[t] == 1)
        unique_pct = unique_count / vocab_size if vocab_size > 0 else 0

        folio_metrics[folio] = {
            'vocab_size': vocab_size,
            'core_count': core_count,
            'core_pct': core_pct,
            'unique_count': unique_count,
            'unique_pct': unique_pct
        }

    # Summary statistics
    vocab_sizes = [m['vocab_size'] for m in folio_metrics.values()]
    core_pcts = [m['core_pct'] for m in folio_metrics.values()]
    unique_pcts = [m['unique_pct'] for m in folio_metrics.values()]

    print(f"\nFolios analyzed: {n_folios}")
    print(f"Total unique tokens across all B folios: {len(token_folio_count)}")

    print(f"\nVocabulary size per folio:")
    print(f"  Mean: {np.mean(vocab_sizes):.1f}")
    print(f"  Std:  {np.std(vocab_sizes):.1f}")
    print(f"  Min:  {min(vocab_sizes)}")
    print(f"  Max:  {max(vocab_sizes)}")

    print(f"\nCore vocabulary (tokens in >= 50% of folios):")
    print(f"  Mean % per folio: {np.mean(core_pcts)*100:.1f}%")
    print(f"  Total core tokens: {sum(1 for t, c in token_folio_count.items() if c >= n_folios * 0.5)}")

    print(f"\nUnique vocabulary (tokens in only 1 folio):")
    print(f"  Mean % per folio: {np.mean(unique_pcts)*100:.1f}%")
    print(f"  Total unique tokens: {sum(1 for t, c in token_folio_count.items() if c == 1)}")

    # Find outliers
    vocab_z = [(f, (m['vocab_size'] - np.mean(vocab_sizes)) / np.std(vocab_sizes))
               for f, m in folio_metrics.items()]
    unique_z = [(f, (m['unique_pct'] - np.mean(unique_pcts)) / np.std(unique_pcts))
                for f, m in folio_metrics.items()]

    high_vocab_outliers = [(f, z) for f, z in vocab_z if z > 2]
    low_vocab_outliers = [(f, z) for f, z in vocab_z if z < -2]
    high_unique_outliers = [(f, z) for f, z in unique_z if z > 2]

    print(f"\nOutliers (|z| > 2):")
    if high_vocab_outliers:
        print(f"  Large vocabulary: {[f for f, z in high_vocab_outliers]}")
    if low_vocab_outliers:
        print(f"  Small vocabulary: {[f for f, z in low_vocab_outliers]}")
    if high_unique_outliers:
        print(f"  High uniqueness:  {[f for f, z in high_unique_outliers]}")

    if not high_vocab_outliers and not low_vocab_outliers and not high_unique_outliers:
        print("  None detected")

    # Check distribution shape
    vocab_skew = stats.skew(vocab_sizes)
    unique_skew = stats.skew(unique_pcts)

    print(f"\nDistribution shape:")
    print(f"  Vocabulary size skewness: {vocab_skew:.3f}")
    print(f"  Uniqueness % skewness:    {unique_skew:.3f}")

    # Determine verdict
    if len(high_vocab_outliers) > 0 or len(high_unique_outliers) > 0:
        verdict = "SIGNAL - Vocabulary hubs detected"
    elif abs(vocab_skew) > 1 or abs(unique_skew) > 1:
        verdict = "WEAK SIGNAL - Non-uniform distribution"
    else:
        verdict = "NULL - Uniform vocabulary distribution"

    print(f"\nVERDICT: {verdict}")

    return {
        'test': 'BVP-4',
        'n_folios': n_folios,
        'total_unique_tokens': len(token_folio_count),
        'mean_vocab_size': np.mean(vocab_sizes),
        'core_tokens': sum(1 for t, c in token_folio_count.items() if c >= n_folios * 0.5),
        'unique_tokens': sum(1 for t, c in token_folio_count.items() if c == 1),
        'vocab_skewness': vocab_skew,
        'unique_skewness': unique_skew,
        'high_vocab_outliers': [f for f, z in high_vocab_outliers],
        'high_unique_outliers': [f for f, z in high_unique_outliers],
        'verdict': verdict
    }

def main():
    print("="*60)
    print("Phase BVP: B-Folio Vocabulary Patterns")
    print("="*60)
    print("\nCore Question: How do B folios relate to each other vocabularily?")

    # Load data
    data = load_transcription()
    regimes = load_regimes()
    control_sigs = load_control_signatures()
    stability_data = load_stability_data()

    # Get B folios
    b_data = get_b_folios(data)
    print(f"\nB tokens loaded: {len(b_data)}")

    # Build vocabularies
    folio_vocab = build_folio_vocabularies(b_data)
    print(f"B folios with vocabulary: {len(folio_vocab)}")

    # Run tests
    results = []

    r1 = test_bvp1_adjacent_sharing(folio_vocab)
    results.append(r1)

    r2 = test_bvp2_regime_clustering(folio_vocab, regimes)
    results.append(r2)

    r3 = test_bvp3_stability_clustering(folio_vocab, stability_data, control_sigs)
    results.append(r3)

    r4 = test_bvp4_uniqueness_distribution(folio_vocab)
    results.append(r4)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    signals = sum(1 for r in results if 'SIGNAL' in r['verdict'] and 'WEAK' not in r['verdict'])
    weak_signals = sum(1 for r in results if 'WEAK SIGNAL' in r['verdict'])
    nulls = sum(1 for r in results if 'NULL' in r['verdict'])

    print(f"\nResults: {signals} SIGNAL, {weak_signals} WEAK SIGNAL, {nulls} NULL")

    for r in results:
        print(f"\n{r['test']}: {r['verdict']}")

    if signals >= 2:
        conclusion = "B folios show STRUCTURED vocabulary patterns"
    elif signals >= 1 or weak_signals >= 2:
        conclusion = "B folios show SOME vocabulary structure"
    else:
        conclusion = "B folios are vocabularily UNIFORM"

    print(f"\n{conclusion}")

    # Save results
    output = {
        'phase': 'BVP',
        'tests': results,
        'signals': signals,
        'weak_signals': weak_signals,
        'nulls': nulls,
        'conclusion': conclusion
    }

    output_path = BASE / "archive" / "reports" / "b_vocabulary_patterns.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")

if __name__ == '__main__':
    main()
