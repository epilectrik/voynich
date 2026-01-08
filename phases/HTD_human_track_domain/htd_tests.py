"""
HTD Phase: Human-Track Domain Analysis

Tests whether human-track distribution reveals single vs multi-domain operation.

Core Tests:
- HTD-1: Run Length Distribution (dual baseline: shuffle + exponential)
- HTD-2: LINK-HT Folio-Level Coupling
- HTD-4: Program-Type HT Association

Tier Target: 2 (structural inference)
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
from scipy.stats import expon, kstest, kruskal, spearmanr

# =============================================================================
# CONSTANTS (from ext_hf_01)
# =============================================================================

GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc', 'ol'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}

OPERATIONAL_TOKENS = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol', 's', 'o', 'd', 'y',
    'a', 'e', 'l', 'r', 'k', 'h', 'c', 't', 'n', 'p', 'm', 'g', 'f',
    'dain', 'chain', 'shain', 'ain', 'in', 'an', 'dan',
}

LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'oiin', 'aiiin'}

# =============================================================================
# TOKEN CLASSIFICATION
# =============================================================================

def is_grammar_token(token):
    """Check if token matches grammar patterns."""
    t = token.lower()
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True
    return False


def is_strict_ht(token):
    """Strict human-track classification per ext_hf_01 approach."""
    t = token.lower().strip()

    # Length >= 2
    if len(t) < 2:
        return False

    # Alpha only
    if not t.isalpha():
        return False

    # Not hazard token
    if t in HAZARD_TOKENS:
        return False

    # Not operational token
    if t in OPERATIONAL_TOKENS:
        return False

    # Not grammar token
    if is_grammar_token(t):
        return False

    return True


def is_link_token(token):
    """Check if token is LINK-indicative."""
    t = token.lower()
    if t in LINK_TOKENS:
        return True
    # Also check suffixes
    if t.endswith('ol') or t.endswith('al') or t.endswith('aiin'):
        return True
    return False


# =============================================================================
# DATA LOADING
# =============================================================================

def load_currier_b_tokens():
    """Load Currier B tokens with folio and position info."""
    data_path = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")

    folio_tokens = defaultdict(list)

    with open(data_path, 'r', encoding='utf-8') as f:
        header = next(f)
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"') if parts[0] else ''
                folio = parts[2].strip('"') if len(parts) > 2 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''
                language = parts[6].strip('"') if len(parts) > 6 else ''

                # Currier B only
                if language == 'B':
                    if word and word != '.' and word != '=' and word != 'NA':
                        folio_tokens[folio].append({
                            'word': word,
                            'section': section,
                            'is_ht': is_strict_ht(word),
                            'is_link': is_link_token(word)
                        })

    return folio_tokens


def load_ops1_signatures():
    """Load OPS-1 folio signatures for program classifications."""
    ops1_path = Path("C:/git/voynich/phases/OPS1_folio_control_signatures/ops1_folio_control_signatures.json")

    with open(ops1_path, 'r') as f:
        data = json.load(f)

    return data['signatures']


# =============================================================================
# HTD-1: RUN LENGTH DISTRIBUTION
# =============================================================================

def compute_run_lengths(is_ht_sequence):
    """Compute consecutive HT run lengths from binary sequence."""
    runs = []
    current_run = 0

    for is_ht in is_ht_sequence:
        if is_ht:
            current_run += 1
        elif current_run > 0:
            runs.append(current_run)
            current_run = 0

    if current_run > 0:
        runs.append(current_run)

    return runs


def shuffle_baseline(is_ht_sequence, n_shuffles=1000):
    """Generate shuffled baselines preserving HT count."""
    is_ht_array = np.array(is_ht_sequence, dtype=bool)
    observed_runs = compute_run_lengths(is_ht_sequence)

    shuffled_mean_lengths = []
    shuffled_max_lengths = []

    for _ in range(n_shuffles):
        shuffled = np.random.permutation(is_ht_array)
        s_runs = compute_run_lengths(shuffled)
        if s_runs:
            shuffled_mean_lengths.append(np.mean(s_runs))
            shuffled_max_lengths.append(np.max(s_runs))

    return {
        'observed_runs': observed_runs,
        'observed_mean': np.mean(observed_runs) if observed_runs else 0,
        'observed_max': np.max(observed_runs) if observed_runs else 0,
        'shuffled_mean_dist': shuffled_mean_lengths,
        'shuffled_max_dist': shuffled_max_lengths
    }


def test_exponential_fit(run_lengths):
    """Test if run lengths follow exponential distribution."""
    if len(run_lengths) < 10:
        return {'ks_stat': None, 'ks_pvalue': None, 'verdict': 'INSUFFICIENT_DATA'}

    # Fit exponential
    loc, scale = expon.fit(run_lengths, floc=0)  # Force loc=0 for pure exponential

    # KS test
    stat, pvalue = kstest(run_lengths, 'expon', args=(0, scale))

    # Check for heavy tail
    observed_tail = np.percentile(run_lengths, 95)
    expected_tail = expon.ppf(0.95, 0, scale)
    tail_ratio = observed_tail / expected_tail if expected_tail > 0 else 1

    return {
        'ks_stat': stat,
        'ks_pvalue': pvalue,
        'scale': scale,
        'observed_p95': observed_tail,
        'expected_p95': expected_tail,
        'tail_ratio': tail_ratio,
        'verdict': 'EXPONENTIAL' if pvalue > 0.05 else 'NON_EXPONENTIAL'
    }


def run_htd1(folio_tokens):
    """HTD-1: Run Length Distribution with dual baseline."""
    print("\n=== HTD-1: Run Length Distribution ===\n")

    # Aggregate all HT sequences across folios
    all_runs = []
    folio_results = {}

    for folio, tokens in folio_tokens.items():
        is_ht_seq = [t['is_ht'] for t in tokens]
        runs = compute_run_lengths(is_ht_seq)
        all_runs.extend(runs)

        if runs:
            folio_results[folio] = {
                'n_runs': len(runs),
                'mean_run': np.mean(runs),
                'max_run': np.max(runs),
                'n_tokens': len(tokens),
                'ht_density': sum(is_ht_seq) / len(tokens) if tokens else 0
            }

    # Global run length statistics
    print(f"Total HT runs: {len(all_runs)}")
    print(f"Mean run length: {np.mean(all_runs):.2f}")
    print(f"Median run length: {np.median(all_runs):.2f}")
    print(f"Max run length: {np.max(all_runs)}")
    print(f"Std run length: {np.std(all_runs):.2f}")

    # Run length distribution
    run_counts = Counter(all_runs)
    print("\nRun length distribution:")
    for length in sorted(run_counts.keys())[:10]:
        print(f"  Length {length}: {run_counts[length]} ({100*run_counts[length]/len(all_runs):.1f}%)")

    # Baseline 1: Shuffle test (aggregate)
    print("\n--- Shuffle Baseline Test ---")

    # Concatenate all tokens for global shuffle test
    all_ht_flags = []
    for folio in sorted(folio_tokens.keys()):
        all_ht_flags.extend([t['is_ht'] for t in folio_tokens[folio]])

    shuffle_result = shuffle_baseline(all_ht_flags, n_shuffles=1000)

    observed_mean = shuffle_result['observed_mean']
    shuffled_means = shuffle_result['shuffled_mean_dist']

    # Compute p-value (one-tailed: observed > shuffled?)
    p_longer = np.mean([sm >= observed_mean for sm in shuffled_means])

    print(f"Observed mean run length: {observed_mean:.3f}")
    print(f"Shuffled mean (median): {np.median(shuffled_means):.3f}")
    print(f"Shuffled mean (95% CI): [{np.percentile(shuffled_means, 2.5):.3f}, {np.percentile(shuffled_means, 97.5):.3f}]")
    print(f"P(shuffled >= observed): {p_longer:.4f}")

    shuffle_verdict = "LONGER_THAN_SHUFFLE" if p_longer < 0.05 else "SAME_AS_SHUFFLE"
    print(f"Shuffle verdict: {shuffle_verdict}")

    # Baseline 2: Exponential fit test
    print("\n--- Exponential Fit Test ---")
    exp_result = test_exponential_fit(all_runs)

    print(f"KS statistic: {exp_result['ks_stat']:.4f}" if exp_result['ks_stat'] else "KS statistic: N/A")
    print(f"KS p-value: {exp_result['ks_pvalue']:.4f}" if exp_result['ks_pvalue'] else "KS p-value: N/A")
    print(f"Tail ratio (obs p95 / exp p95): {exp_result['tail_ratio']:.2f}" if exp_result['tail_ratio'] else "")
    print(f"Exponential verdict: {exp_result['verdict']}")

    # Combined interpretation
    print("\n--- Dual Baseline Interpretation ---")

    if shuffle_verdict == "LONGER_THAN_SHUFFLE" and exp_result['verdict'] == 'NON_EXPONENTIAL':
        outcome = "A"
        meaning = "Intentional extended writing (strong HT signal)"
    elif shuffle_verdict == "LONGER_THAN_SHUFFLE" and exp_result['verdict'] == 'EXPONENTIAL':
        outcome = "B"
        meaning = "Opportunistic but clustered (weak HT)"
    elif shuffle_verdict == "SAME_AS_SHUFFLE" and exp_result['verdict'] == 'EXPONENTIAL':
        outcome = "C"
        meaning = "Noise / scribal artifact (threatens HT hypothesis)"
    else:
        outcome = "D"
        meaning = "Multiple waiting regimes or complex structure"

    print(f"Outcome: {outcome}")
    print(f"Meaning: {meaning}")

    # Check for multimodality
    print("\n--- Multimodality Check ---")
    from scipy.stats import gaussian_kde

    if len(all_runs) > 50:
        kde = gaussian_kde(all_runs)
        x_range = np.linspace(1, max(all_runs), 100)
        kde_values = kde(x_range)

        # Find local maxima
        peaks = []
        for i in range(1, len(kde_values)-1):
            if kde_values[i] > kde_values[i-1] and kde_values[i] > kde_values[i+1]:
                peaks.append(x_range[i])

        print(f"KDE peaks at: {[f'{p:.1f}' for p in peaks[:5]]}")
        is_multimodal = len(peaks) > 1
        print(f"Multimodal: {is_multimodal}")
    else:
        is_multimodal = False
        print("Insufficient data for KDE")

    return {
        'test': 'HTD-1',
        'total_runs': len(all_runs),
        'mean_run_length': float(np.mean(all_runs)),
        'median_run_length': float(np.median(all_runs)),
        'max_run_length': int(np.max(all_runs)),
        'std_run_length': float(np.std(all_runs)),
        'run_distribution': dict(run_counts),
        'shuffle_verdict': shuffle_verdict,
        'shuffle_p_longer': float(p_longer),
        'observed_mean': float(observed_mean),
        'shuffled_median': float(np.median(shuffled_means)),
        'exponential_verdict': exp_result['verdict'],
        'ks_pvalue': float(exp_result['ks_pvalue']) if exp_result['ks_pvalue'] else None,
        'tail_ratio': float(exp_result['tail_ratio']) if exp_result['tail_ratio'] else None,
        'outcome': outcome,
        'outcome_meaning': meaning,
        'is_multimodal': is_multimodal,
        'folio_results': folio_results
    }


# =============================================================================
# HTD-2: LINK-HT FOLIO-LEVEL COUPLING
# =============================================================================

def run_htd2(folio_tokens, ops1_signatures):
    """HTD-2: LINK-HT Folio-Level Coupling."""
    print("\n=== HTD-2: LINK-HT Folio-Level Coupling ===\n")

    folio_metrics = []

    for folio, tokens in folio_tokens.items():
        n_tokens = len(tokens)
        if n_tokens < 10:
            continue

        n_ht = sum(1 for t in tokens if t['is_ht'])
        n_link = sum(1 for t in tokens if t['is_link'])

        ht_density = n_ht / n_tokens
        link_density = n_link / n_tokens

        # Get OPS-1 classification if available
        waiting_profile = None
        if folio in ops1_signatures:
            sig = ops1_signatures[folio]
            if 'classifications' in sig:
                waiting_profile = sig['classifications'].get('waiting_profile')

        folio_metrics.append({
            'folio': folio,
            'n_tokens': n_tokens,
            'ht_density': ht_density,
            'link_density': link_density,
            'n_ht': n_ht,
            'n_link': n_link,
            'waiting_profile': waiting_profile
        })

    # Compute correlation
    ht_densities = [fm['ht_density'] for fm in folio_metrics]
    link_densities = [fm['link_density'] for fm in folio_metrics]

    # Pearson correlation
    r_pearson, p_pearson = stats.pearsonr(ht_densities, link_densities)

    # Spearman correlation (more robust)
    r_spearman, p_spearman = spearmanr(ht_densities, link_densities)

    print(f"Folios analyzed: {len(folio_metrics)}")
    print(f"Mean HT density: {np.mean(ht_densities):.3f}")
    print(f"Mean LINK density: {np.mean(link_densities):.3f}")
    print(f"\nPearson r: {r_pearson:.4f} (p={p_pearson:.4f})")
    print(f"Spearman rho: {r_spearman:.4f} (p={p_spearman:.4f})")

    # Interpret correlation strength
    abs_r = abs(r_spearman)
    if abs_r > 0.8:
        correlation_verdict = "TIGHT"
        correlation_meaning = "Single domain: HT = waiting behavior"
    elif abs_r > 0.5:
        correlation_verdict = "MODERATE"
        correlation_meaning = "Partial coupling: HT partially explained by LINK"
    else:
        correlation_verdict = "LOOSE"
        correlation_meaning = "Multi-domain or complex relationship"

    print(f"\nCorrelation verdict: {correlation_verdict}")
    print(f"Meaning: {correlation_meaning}")

    # Identify outliers (residual > 2 std)
    from scipy.stats import linregress
    slope, intercept, _, _, _ = linregress(link_densities, ht_densities)
    predicted = [slope * ld + intercept for ld in link_densities]
    residuals = [fm['ht_density'] - pred for fm, pred in zip(folio_metrics, predicted)]
    residual_std = np.std(residuals)

    outliers = []
    for fm, resid in zip(folio_metrics, residuals):
        if abs(resid) > 2 * residual_std:
            outliers.append({
                'folio': fm['folio'],
                'ht_density': fm['ht_density'],
                'link_density': fm['link_density'],
                'residual': resid,
                'type': 'HIGH_HT' if resid > 0 else 'LOW_HT',
                'waiting_profile': fm['waiting_profile']
            })

    print(f"\nOutliers (|residual| > 2 std): {len(outliers)}")
    for ol in outliers[:5]:
        print(f"  {ol['folio']}: HT={ol['ht_density']:.3f}, LINK={ol['link_density']:.3f}, type={ol['type']}, profile={ol['waiting_profile']}")

    return {
        'test': 'HTD-2',
        'n_folios': len(folio_metrics),
        'mean_ht_density': float(np.mean(ht_densities)),
        'mean_link_density': float(np.mean(link_densities)),
        'pearson_r': float(r_pearson),
        'pearson_p': float(p_pearson),
        'spearman_rho': float(r_spearman),
        'spearman_p': float(p_spearman),
        'correlation_verdict': correlation_verdict,
        'correlation_meaning': correlation_meaning,
        'n_outliers': len(outliers),
        'outliers': outliers,
        'folio_metrics': folio_metrics
    }


# =============================================================================
# HTD-4: PROGRAM-TYPE HT ASSOCIATION
# =============================================================================

def run_htd4(folio_tokens, ops1_signatures):
    """HTD-4: Program-Type HT Association."""
    print("\n=== HTD-4: Program-Type HT Association ===\n")

    # Group folios by waiting_profile
    profile_groups = defaultdict(list)

    for folio, tokens in folio_tokens.items():
        if folio not in ops1_signatures:
            continue

        sig = ops1_signatures[folio]
        if 'classifications' not in sig:
            continue

        waiting_profile = sig['classifications'].get('waiting_profile', 'UNKNOWN')

        n_tokens = len(tokens)
        if n_tokens < 10:
            continue

        # Compute HT metrics
        is_ht_seq = [t['is_ht'] for t in tokens]
        runs = compute_run_lengths(is_ht_seq)

        ht_density = sum(is_ht_seq) / n_tokens
        mean_run = np.mean(runs) if runs else 0

        profile_groups[waiting_profile].append({
            'folio': folio,
            'ht_density': ht_density,
            'mean_run_length': mean_run,
            'n_runs': len(runs),
            'n_tokens': n_tokens
        })

    print("Folios by waiting profile:")
    for profile, folios in sorted(profile_groups.items()):
        print(f"  {profile}: {len(folios)} folios")

    # Compare HT density across groups
    print("\n--- HT Density by Waiting Profile ---")

    group_densities = {}
    for profile, folios in profile_groups.items():
        densities = [f['ht_density'] for f in folios]
        group_densities[profile] = densities
        print(f"  {profile}: mean={np.mean(densities):.4f}, std={np.std(densities):.4f}, n={len(folios)}")

    # Kruskal-Wallis test (non-parametric ANOVA)
    if len(group_densities) >= 2:
        groups = [d for d in group_densities.values() if len(d) >= 3]
        if len(groups) >= 2:
            h_stat, kw_p = kruskal(*groups)
            print(f"\nKruskal-Wallis H: {h_stat:.4f}, p={kw_p:.4f}")
            density_significant = kw_p < 0.05
        else:
            h_stat, kw_p = None, None
            density_significant = False
    else:
        h_stat, kw_p = None, None
        density_significant = False

    # Compare mean run length across groups
    print("\n--- Mean Run Length by Waiting Profile ---")

    group_runs = {}
    for profile, folios in profile_groups.items():
        run_lengths = [f['mean_run_length'] for f in folios if f['mean_run_length'] > 0]
        group_runs[profile] = run_lengths
        if run_lengths:
            print(f"  {profile}: mean={np.mean(run_lengths):.4f}, std={np.std(run_lengths):.4f}, n={len(run_lengths)}")

    # Kruskal-Wallis for run length
    if len(group_runs) >= 2:
        groups_run = [r for r in group_runs.values() if len(r) >= 3]
        if len(groups_run) >= 2:
            h_stat_run, kw_p_run = kruskal(*groups_run)
            print(f"\nKruskal-Wallis H (run length): {h_stat_run:.4f}, p={kw_p_run:.4f}")
            run_significant = kw_p_run < 0.05
        else:
            h_stat_run, kw_p_run = None, None
            run_significant = False
    else:
        h_stat_run, kw_p_run = None, None
        run_significant = False

    # Overall verdict
    print("\n--- Verdict ---")

    if density_significant or run_significant:
        verdict = "SIGNIFICANT"
        meaning = "Different programs = different waiting rhythms"
    else:
        verdict = "UNIFORM"
        meaning = "Single domain: program type doesn't affect HT"

    print(f"Verdict: {verdict}")
    print(f"Meaning: {meaning}")

    # Additional: Test intervention_style groups
    print("\n--- Intervention Style Analysis ---")

    intervention_groups = defaultdict(list)
    for folio, tokens in folio_tokens.items():
        if folio not in ops1_signatures:
            continue
        sig = ops1_signatures[folio]
        if 'classifications' not in sig:
            continue

        style = sig['classifications'].get('intervention_style', 'UNKNOWN')

        n_tokens = len(tokens)
        if n_tokens < 10:
            continue

        is_ht_seq = [t['is_ht'] for t in tokens]
        ht_density = sum(is_ht_seq) / n_tokens
        intervention_groups[style].append(ht_density)

    for style, densities in sorted(intervention_groups.items()):
        print(f"  {style}: mean HT={np.mean(densities):.4f}, n={len(densities)}")

    # KW test for intervention style
    style_groups = [d for d in intervention_groups.values() if len(d) >= 3]
    if len(style_groups) >= 2:
        h_style, p_style = kruskal(*style_groups)
        print(f"Kruskal-Wallis H (intervention style): {h_style:.4f}, p={p_style:.4f}")
    else:
        h_style, p_style = None, None

    return {
        'test': 'HTD-4',
        'profile_groups': {k: len(v) for k, v in profile_groups.items()},
        'density_by_profile': {k: {'mean': float(np.mean(v)), 'std': float(np.std(v)), 'n': len(v)}
                               for k, v in group_densities.items()},
        'run_by_profile': {k: {'mean': float(np.mean(v)) if v else 0, 'std': float(np.std(v)) if len(v) > 1 else 0, 'n': len(v)}
                          for k, v in group_runs.items()},
        'kw_density_h': float(h_stat) if h_stat else None,
        'kw_density_p': float(kw_p) if kw_p else None,
        'kw_run_h': float(h_stat_run) if h_stat_run else None,
        'kw_run_p': float(kw_p_run) if kw_p_run else None,
        'density_significant': density_significant,
        'run_significant': run_significant,
        'verdict': verdict,
        'verdict_meaning': meaning,
        'intervention_style_analysis': {k: float(np.mean(v)) for k, v in intervention_groups.items()},
        'kw_intervention_h': float(h_style) if h_style else None,
        'kw_intervention_p': float(p_style) if p_style else None
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("HTD Phase: Human-Track Domain Analysis")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    folio_tokens = load_currier_b_tokens()
    ops1_signatures = load_ops1_signatures()

    print(f"Loaded {len(folio_tokens)} Currier B folios")
    total_tokens = sum(len(tokens) for tokens in folio_tokens.values())
    total_ht = sum(sum(1 for t in tokens if t['is_ht']) for tokens in folio_tokens.values())
    print(f"Total tokens: {total_tokens}")
    print(f"Total strict HT tokens: {total_ht} ({100*total_ht/total_tokens:.1f}%)")

    # Run tests
    results = {}

    results['HTD-1'] = run_htd1(folio_tokens)
    results['HTD-2'] = run_htd2(folio_tokens, ops1_signatures)
    results['HTD-4'] = run_htd4(folio_tokens, ops1_signatures)

    # Overall summary
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)

    print(f"\nHTD-1 Outcome: {results['HTD-1']['outcome']} ({results['HTD-1']['outcome_meaning']})")
    print(f"HTD-2 Verdict: {results['HTD-2']['correlation_verdict']} (r={results['HTD-2']['spearman_rho']:.3f})")
    print(f"HTD-4 Verdict: {results['HTD-4']['verdict']} ({results['HTD-4']['verdict_meaning']})")

    # Save results
    output_path = Path("C:/git/voynich/phases/HTD_human_track_domain/htd_results.json")

    # Clean up non-serializable items
    clean_results = {}
    for test_name, test_results in results.items():
        clean_results[test_name] = {}
        for k, v in test_results.items():
            if k == 'folio_results' or k == 'folio_metrics':
                # Keep abbreviated version
                clean_results[test_name][k] = {folio: data for folio, data in list(v.items())[:10]} if isinstance(v, dict) else v[:10] if isinstance(v, list) else v
            elif k == 'run_distribution':
                # Keep top 10 run lengths
                clean_results[test_name][k] = dict(sorted(v.items(), key=lambda x: int(x[0]))[:10])
            else:
                clean_results[test_name][k] = v

    with open(output_path, 'w') as f:
        json.dump(clean_results, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")

    return results


if __name__ == "__main__":
    main()
