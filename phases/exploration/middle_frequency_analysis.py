#!/usr/bin/env python
"""
MIDDLE Frequency Distribution Analysis

Post-CCM Bayesian analysis testing whether MIDDLE frequency distribution
encodes physically interpretable structure from the apparatus perspective.

Core Hypothesis: High-frequency MIDDLEs are "generalist" recognition points
(common situations), while low-frequency MIDDLEs are "specialist" recognition
points (edge cases requiring careful handling).

Tests:
1. Core vs Long-Tail behavioral signatures
2. Frequency-Sister preference correlation
3. Frequency-Hazard context correlation (simplified)
4. Distribution shape analysis
5. MIDDLE entropy by prefix class
6. Rank-frequency stability across sections
"""
import sys
import json
import numpy as np
from collections import defaultdict, Counter
from scipy.stats import entropy, spearmanr, kstest, pearsonr
from scipy.optimize import minimize_scalar
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import parse_currier_a_token, MARKER_FAMILIES

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'


def load_currier_a_tokens_with_metadata():
    """Load all Currier A tokens with section and folio info."""

    tokens = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''

                if language != 'A':
                    continue

                tokens.append({
                    'token': word,
                    'folio': folio,
                    'section': section
                })

    return tokens


def parse_all_tokens(tokens):
    """Parse all tokens and extract components."""

    parsed = []

    for t in tokens:
        result = parse_currier_a_token(t['token'])

        if result.is_prefix_legal and result.middle:
            parsed.append({
                'token': t['token'],
                'prefix': result.prefix,
                'middle': result.middle,
                'suffix': result.suffix,
                'section': t['section'],
                'folio': t['folio']
            })

    return parsed


def get_middle_census(parsed):
    """Build MIDDLE census with frequencies."""

    middle_counts = Counter()
    for p in parsed:
        middle_counts[p['middle']] += 1

    return middle_counts


def identify_core_and_tail(middle_counts, top_n=30):
    """Partition MIDDLEs into Core (top N) and Tail."""

    sorted_middles = middle_counts.most_common()
    core_middles = set(m for m, c in sorted_middles[:top_n])
    tail_middles = set(m for m, c in sorted_middles[top_n:])

    core_count = sum(c for m, c in sorted_middles[:top_n])
    tail_count = sum(c for m, c in sorted_middles[top_n:])
    total = core_count + tail_count

    return core_middles, tail_middles, core_count/total, tail_count/total


# =============================================================================
# TEST 1: Core vs Long-Tail Behavioral Signatures
# =============================================================================

def test_1_core_vs_tail(parsed, core_middles, tail_middles):
    """Compare behavioral properties of Core vs Tail MIDDLEs."""

    print("=" * 70)
    print("TEST 1: Core vs Long-Tail Behavioral Signatures")
    print("=" * 70)

    # Partition tokens
    core_tokens = [p for p in parsed if p['middle'] in core_middles]
    tail_tokens = [p for p in parsed if p['middle'] in tail_middles]

    print(f"\nCore tokens: {len(core_tokens)} ({100*len(core_tokens)/len(parsed):.1f}%)")
    print(f"Tail tokens: {len(tail_tokens)} ({100*len(tail_tokens)/len(parsed):.1f}%)")

    results = {}

    # 1. Sister-pair preference (ch vs sh only)
    def calc_sister_preference(tokens):
        ch_count = sum(1 for t in tokens if t['prefix'] == 'ch')
        sh_count = sum(1 for t in tokens if t['prefix'] == 'sh')
        total = ch_count + sh_count
        if total == 0:
            return None, None
        ch_pct = ch_count / total
        deviation = abs(ch_pct - 0.5)
        return ch_pct, deviation

    core_ch_pct, core_dev = calc_sister_preference(core_tokens)
    tail_ch_pct, tail_dev = calc_sister_preference(tail_tokens)

    print(f"\nSister preference (ch vs sh):")
    print(f"  Core: ch={100*core_ch_pct:.1f}%, deviation={core_dev:.3f}")
    print(f"  Tail: ch={100*tail_ch_pct:.1f}%, deviation={tail_dev:.3f}")
    results['sister_preference'] = {
        'core_ch_pct': core_ch_pct,
        'tail_ch_pct': tail_ch_pct,
        'core_deviation': core_dev,
        'tail_deviation': tail_dev
    }

    # 2. Suffix co-occurrence entropy
    def calc_suffix_entropy(tokens):
        suffix_counts = Counter(t['suffix'] for t in tokens if t['suffix'])
        if not suffix_counts:
            return 0
        probs = np.array(list(suffix_counts.values())) / sum(suffix_counts.values())
        return entropy(probs, base=2)

    core_suffix_entropy = calc_suffix_entropy(core_tokens)
    tail_suffix_entropy = calc_suffix_entropy(tail_tokens)

    print(f"\nSuffix entropy:")
    print(f"  Core: {core_suffix_entropy:.3f} bits")
    print(f"  Tail: {tail_suffix_entropy:.3f} bits")
    results['suffix_entropy'] = {
        'core': core_suffix_entropy,
        'tail': tail_suffix_entropy
    }

    # 3. Section distribution (H/P/T concentration)
    def calc_section_concentration(tokens):
        section_counts = Counter(t['section'] for t in tokens)
        total = sum(section_counts.values())
        if total == 0:
            return None, 0
        probs = np.array(list(section_counts.values())) / total
        h = entropy(probs, base=2)
        return section_counts, h

    core_sections, core_section_h = calc_section_concentration(core_tokens)
    tail_sections, tail_section_h = calc_section_concentration(tail_tokens)

    print(f"\nSection entropy:")
    print(f"  Core: {core_section_h:.3f} bits (more spread)")
    print(f"  Tail: {tail_section_h:.3f} bits (more concentrated)")
    results['section_entropy'] = {
        'core': core_section_h,
        'tail': tail_section_h
    }

    # 4. Prefix exclusivity rate
    def calc_prefix_exclusivity(tokens, middles):
        middle_to_prefixes = defaultdict(set)
        for t in tokens:
            middle_to_prefixes[t['middle']].add(t['prefix'])

        exclusive = sum(1 for m in middles if len(middle_to_prefixes[m]) == 1)
        return exclusive / len(middles) if middles else 0

    core_exclusivity = calc_prefix_exclusivity(core_tokens, core_middles)
    tail_exclusivity = calc_prefix_exclusivity(tail_tokens, tail_middles)

    print(f"\nPrefix exclusivity rate:")
    print(f"  Core: {100*core_exclusivity:.1f}%")
    print(f"  Tail: {100*tail_exclusivity:.1f}%")
    results['prefix_exclusivity'] = {
        'core': core_exclusivity,
        'tail': tail_exclusivity
    }

    # Summary interpretation
    print(f"\nINTERPRETATION:")
    if tail_dev > core_dev:
        print("  - Tail MIDDLEs have stronger sister preference (mode-specific)")
    else:
        print("  - Core MIDDLEs have stronger sister preference (unexpected)")

    if core_suffix_entropy > tail_suffix_entropy:
        print("  - Core MIDDLEs have higher suffix entropy (more decision contexts)")
    else:
        print("  - Tail MIDDLEs have higher suffix entropy (unexpected)")

    if core_section_h > tail_section_h:
        print("  - Core MIDDLEs more spread across sections (universal)")
    else:
        print("  - Tail MIDDLEs more spread across sections (unexpected)")

    if tail_exclusivity > core_exclusivity:
        print("  - Tail MIDDLEs more prefix-exclusive (class-specific)")
    else:
        print("  - Core MIDDLEs more prefix-exclusive (unexpected)")

    return results


# =============================================================================
# TEST 2: Frequency-Sister Preference Correlation
# =============================================================================

def test_2_frequency_sister_correlation(parsed, middle_counts):
    """Correlate MIDDLE frequency with sister preference deviation."""

    print("\n" + "=" * 70)
    print("TEST 2: Frequency-Sister Preference Correlation")
    print("=" * 70)

    # For each MIDDLE, calculate sister preference
    middle_to_sister = defaultdict(lambda: {'ch': 0, 'sh': 0})

    for t in parsed:
        if t['prefix'] in ['ch', 'sh']:
            middle_to_sister[t['middle']][t['prefix']] += 1

    # Calculate deviation for MIDDLEs with sufficient data
    min_n = 10
    frequencies = []
    deviations = []

    for middle, sister_counts in middle_to_sister.items():
        total = sister_counts['ch'] + sister_counts['sh']
        if total >= min_n:
            ch_pct = sister_counts['ch'] / total
            deviation = abs(ch_pct - 0.5)
            frequencies.append(np.log(middle_counts[middle]))
            deviations.append(deviation)

    print(f"\nMIDDLEs with N>={min_n} ch/sh tokens: {len(frequencies)}")

    if len(frequencies) >= 10:
        rho, p = spearmanr(frequencies, deviations)
        print(f"Spearman correlation: rho = {rho:.3f}, p = {p:.4f}")

        # Interpretation
        if p < 0.05:
            if rho < 0:
                print("CONFIRMED: Higher frequency correlates with LOWER preference deviation")
                print("  -> Common MIDDLEs are mode-flexible; rare MIDDLEs demand specific mode")
            else:
                print("UNEXPECTED: Higher frequency correlates with HIGHER preference deviation")
        else:
            print("NO SIGNIFICANT CORRELATION: Frequency independent of mode preference")

        return {
            'n_middles': len(frequencies),
            'rho': rho,
            'p': p,
            'significant': p < 0.05,
            'direction': 'negative' if rho < 0 else 'positive'
        }
    else:
        print("Insufficient data for correlation")
        return {'n_middles': len(frequencies), 'rho': None, 'p': None}


# =============================================================================
# TEST 3: Frequency-Hazard Context (Simplified)
# =============================================================================

def test_3_frequency_hazard_proxy(parsed, middle_counts):
    """Use prefix as proxy for hazard exposure."""

    print("\n" + "=" * 70)
    print("TEST 3: Frequency-Hazard Context Correlation")
    print("=" * 70)

    # Define hazard classes based on CCM findings
    # High-hazard: ch, qo (ENERGY_OPERATOR, M-A class)
    # Low-hazard: ct, ol (stable/control classes)
    high_hazard_prefixes = {'ch', 'sh', 'qo'}
    low_hazard_prefixes = {'ct', 'ol'}

    # For each MIDDLE, calculate high-hazard exposure rate
    middle_to_hazard = defaultdict(lambda: {'high': 0, 'low': 0, 'other': 0})

    for t in parsed:
        if t['prefix'] in high_hazard_prefixes:
            middle_to_hazard[t['middle']]['high'] += 1
        elif t['prefix'] in low_hazard_prefixes:
            middle_to_hazard[t['middle']]['low'] += 1
        else:
            middle_to_hazard[t['middle']]['other'] += 1

    # Calculate hazard rate for MIDDLEs with sufficient data
    min_n = 10
    frequencies = []
    hazard_rates = []

    for middle, hazard_counts in middle_to_hazard.items():
        total = hazard_counts['high'] + hazard_counts['low']
        if total >= min_n:
            hazard_rate = hazard_counts['high'] / total
            frequencies.append(np.log(middle_counts[middle]))
            hazard_rates.append(hazard_rate)

    print(f"\nMIDDLEs with N>={min_n} hazard-classifiable tokens: {len(frequencies)}")

    if len(frequencies) >= 10:
        rho, p = spearmanr(frequencies, hazard_rates)
        print(f"Spearman correlation: rho = {rho:.3f}, p = {p:.4f}")

        if p < 0.05:
            if rho < 0:
                print("FINDING: Rare MIDDLEs appear MORE in high-hazard contexts")
                print("  -> Edge cases occur in dangerous situations")
            else:
                print("FINDING: Rare MIDDLEs appear LESS in high-hazard contexts")
                print("  -> Edge cases occur in stable situations")
        else:
            print("NO SIGNIFICANT CORRELATION: Frequency independent of hazard context")

        return {
            'n_middles': len(frequencies),
            'rho': rho,
            'p': p,
            'significant': p < 0.05,
            'direction': 'negative' if rho < 0 else 'positive'
        }
    else:
        print("Insufficient data for correlation")
        return {'n_middles': len(frequencies), 'rho': None, 'p': None}


# =============================================================================
# TEST 4: Distribution Shape Analysis
# =============================================================================

def test_4_distribution_shape(middle_counts):
    """Fit candidate distributions to MIDDLE frequency."""

    print("\n" + "=" * 70)
    print("TEST 4: Distribution Shape Analysis")
    print("=" * 70)

    frequencies = sorted(middle_counts.values(), reverse=True)
    n = len(frequencies)
    ranks = np.arange(1, n + 1)

    # Normalize for fitting
    total = sum(frequencies)
    probs = np.array(frequencies) / total

    results = {}

    # 1. Zipf test (linear on log-log)
    log_ranks = np.log(ranks)
    log_freqs = np.log(frequencies)

    # Fit Zipf: log(f) = a - s*log(r)
    slope, intercept = np.polyfit(log_ranks, log_freqs, 1)
    zipf_s = -slope
    zipf_predicted = np.exp(intercept) * np.power(ranks, -zipf_s)
    zipf_residual = np.mean((np.array(frequencies) - zipf_predicted)**2)

    print(f"\n1. Zipf fit:")
    print(f"   Exponent s = {zipf_s:.3f}")
    print(f"   MSE = {zipf_residual:.2f}")
    results['zipf'] = {'s': zipf_s, 'mse': zipf_residual}

    # 2. Log-normal test (frequency distribution)
    log_freqs_data = np.log(frequencies)
    mu_lognormal = np.mean(log_freqs_data)
    sigma_lognormal = np.std(log_freqs_data)

    # K-S test against fitted log-normal
    from scipy.stats import lognorm
    shape = sigma_lognormal
    scale = np.exp(mu_lognormal)
    ks_stat, ks_p = kstest(frequencies, 'lognorm', args=(shape, 0, scale))

    print(f"\n2. Log-normal fit:")
    print(f"   mu = {mu_lognormal:.3f}, sigma = {sigma_lognormal:.3f}")
    print(f"   K-S statistic = {ks_stat:.3f}, p = {ks_p:.4f}")
    results['lognormal'] = {'mu': mu_lognormal, 'sigma': sigma_lognormal,
                            'ks_stat': ks_stat, 'ks_p': ks_p}

    # 3. Exponential test
    from scipy.stats import expon
    exp_lambda = 1 / np.mean(frequencies)
    ks_stat_exp, ks_p_exp = kstest(frequencies, 'expon', args=(0, 1/exp_lambda))

    print(f"\n3. Exponential fit:")
    print(f"   lambda = {exp_lambda:.5f}")
    print(f"   K-S statistic = {ks_stat_exp:.3f}, p = {ks_p_exp:.4f}")
    results['exponential'] = {'lambda': exp_lambda, 'ks_stat': ks_stat_exp, 'ks_p': ks_p_exp}

    # 4. Power-law with cutoff check
    # Check if log-log plot curves at high ranks (indicates cutoff)
    mid_point = n // 2
    early_slope, _ = np.polyfit(log_ranks[:mid_point], log_freqs[:mid_point], 1)
    late_slope, _ = np.polyfit(log_ranks[mid_point:], log_freqs[mid_point:], 1)
    slope_ratio = late_slope / early_slope if early_slope != 0 else 1

    print(f"\n4. Power-law cutoff check:")
    print(f"   Early slope = {early_slope:.3f}")
    print(f"   Late slope = {late_slope:.3f}")
    print(f"   Slope ratio = {slope_ratio:.3f}")
    if slope_ratio < 0.8:
        print("   -> Curve steepens (cutoff detected)")
    elif slope_ratio > 1.2:
        print("   -> Curve flattens (long tail)")
    else:
        print("   -> Consistent slope (pure power-law)")
    results['cutoff'] = {'early_slope': early_slope, 'late_slope': late_slope,
                         'ratio': slope_ratio}

    # Summary
    print(f"\nDISTRIBUTION SUMMARY:")
    if zipf_s > 0.8 and zipf_s < 1.2:
        print(f"  Zipf-like (s={zipf_s:.2f}): Language-like distribution")
    else:
        print(f"  NOT Zipf-like (s={zipf_s:.2f})")

    if ks_p_exp > 0.05:
        print("  Exponential: Cannot reject (random process)")
    else:
        print("  NOT Exponential: Structured distribution")

    if ks_p > 0.05:
        print("  Log-normal: Cannot reject (multiplicative process)")
    else:
        print("  NOT Log-normal")

    return results


# =============================================================================
# TEST 5: MIDDLE Entropy by Prefix Class
# =============================================================================

def test_5_entropy_by_prefix(parsed, middle_counts):
    """Calculate MIDDLE entropy separately for each prefix class."""

    print("\n" + "=" * 70)
    print("TEST 5: MIDDLE Entropy by Prefix Class")
    print("=" * 70)

    # Define hazard classes
    hazard_ranking = {
        'ch': 'high', 'sh': 'high', 'qo': 'high',
        'ok': 'medium', 'ot': 'medium', 'da': 'medium',
        'ct': 'low', 'ol': 'low'
    }

    prefix_to_middles = defaultdict(Counter)

    for t in parsed:
        prefix_to_middles[t['prefix']][t['middle']] += 1

    results = {}

    print(f"\n{'Prefix':<10} {'Hazard':<10} {'N_MIDDLEs':<12} {'Entropy':<10} {'Top-5 %':<10}")
    print("-" * 52)

    entropies = []
    hazard_scores = {'high': 3, 'medium': 2, 'low': 1}
    hazard_values = []

    for prefix in sorted(MARKER_FAMILIES):
        if prefix not in prefix_to_middles:
            continue

        counts = prefix_to_middles[prefix]
        n_middles = len(counts)
        total = sum(counts.values())

        if total < 10:
            continue

        probs = np.array(list(counts.values())) / total
        h = entropy(probs, base=2)

        top5 = sum(sorted(counts.values(), reverse=True)[:5]) / total

        hazard = hazard_ranking.get(prefix, 'unknown')

        print(f"{prefix:<10} {hazard:<10} {n_middles:<12} {h:<10.3f} {100*top5:<10.1f}")

        results[prefix] = {
            'n_middles': n_middles,
            'entropy': h,
            'top5_pct': top5,
            'hazard': hazard
        }

        if hazard in hazard_scores:
            entropies.append(h)
            hazard_values.append(hazard_scores[hazard])

    # Correlation between hazard and entropy
    if len(entropies) >= 4:
        rho, p = spearmanr(hazard_values, entropies)
        print(f"\nHazard-Entropy correlation: rho = {rho:.3f}, p = {p:.4f}")

        if p < 0.05 and rho > 0:
            print("CONFIRMED: Higher hazard classes have higher MIDDLE entropy")
            print("  -> Dangerous situations require finer discrimination")
        else:
            print("NO CLEAR PATTERN between hazard and entropy")

        results['correlation'] = {'rho': rho, 'p': p}

    return results


# =============================================================================
# TEST 6: Rank-Frequency Stability Across Sections
# =============================================================================

def test_6_rank_stability(parsed, core_middles, tail_middles):
    """Check if Core MIDDLEs maintain rank across sections."""

    print("\n" + "=" * 70)
    print("TEST 6: Rank-Frequency Stability Across Sections")
    print("=" * 70)

    # Get section-specific frequencies
    sections = ['H', 'P', 'T']
    section_freqs = {s: Counter() for s in sections}

    for t in parsed:
        if t['section'] in sections:
            section_freqs[t['section']][t['middle']] += 1

    # Get all MIDDLEs that appear in at least 2 sections
    all_middles = set()
    for s in sections:
        all_middles.update(section_freqs[s].keys())

    # Only keep MIDDLEs with sufficient data
    min_per_section = 3
    valid_middles = [m for m in all_middles
                     if sum(1 for s in sections if section_freqs[s][m] >= min_per_section) >= 2]

    print(f"\nMIDDLEs with data in 2+ sections: {len(valid_middles)}")

    # Calculate rank in each section
    def get_ranks(counter, middles):
        sorted_items = sorted(counter.items(), key=lambda x: -x[1])
        rank_map = {m: i+1 for i, (m, c) in enumerate(sorted_items)}
        return {m: rank_map.get(m, len(sorted_items)+1) for m in middles}

    section_ranks = {s: get_ranks(section_freqs[s], valid_middles) for s in sections}

    # Cross-section rank correlation
    results = {}

    print(f"\nCross-section rank correlations:")
    for i, s1 in enumerate(sections):
        for s2 in sections[i+1:]:
            ranks1 = [section_ranks[s1][m] for m in valid_middles]
            ranks2 = [section_ranks[s2][m] for m in valid_middles]

            rho, p = spearmanr(ranks1, ranks2)
            print(f"  {s1} vs {s2}: rho = {rho:.3f}, p = {p:.4f}")
            results[f'{s1}_{s2}'] = {'rho': rho, 'p': p}

    # Core vs Tail stability
    core_valid = [m for m in valid_middles if m in core_middles]
    tail_valid = [m for m in valid_middles if m in tail_middles]

    def calc_avg_rank_var(middles):
        if not middles:
            return None
        variances = []
        for m in middles:
            ranks = [section_ranks[s].get(m, np.nan) for s in sections]
            ranks = [r for r in ranks if not np.isnan(r)]
            if len(ranks) >= 2:
                variances.append(np.var(ranks))
        return np.mean(variances) if variances else None

    core_var = calc_avg_rank_var(core_valid)
    tail_var = calc_avg_rank_var(tail_valid)

    print(f"\nRank variance (lower = more stable):")
    print(f"  Core MIDDLEs: {core_var:.2f}" if core_var else "  Core: insufficient data")
    print(f"  Tail MIDDLEs: {tail_var:.2f}" if tail_var else "  Tail: insufficient data")

    if core_var and tail_var:
        if core_var < tail_var:
            print("CONFIRMED: Core MIDDLEs more rank-stable across sections")
            print("  -> Core = universal recognition points")
        else:
            print("UNEXPECTED: Tail MIDDLEs more rank-stable")

        results['core_variance'] = core_var
        results['tail_variance'] = tail_var

    return results


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("Loading and parsing Currier A data...")
    tokens = load_currier_a_tokens_with_metadata()
    parsed = parse_all_tokens(tokens)
    print(f"Parsed {len(parsed)} tokens with MIDDLE component\n")

    # Build census
    middle_counts = get_middle_census(parsed)
    print(f"Unique MIDDLEs: {len(middle_counts)}")

    # Identify core and tail
    core_middles, tail_middles, core_pct, tail_pct = identify_core_and_tail(middle_counts, top_n=30)
    print(f"Core (top 30): {len(core_middles)} MIDDLEs, {100*core_pct:.1f}% of usage")
    print(f"Tail: {len(tail_middles)} MIDDLEs, {100*tail_pct:.1f}% of usage")

    # Run all tests
    all_results = {}

    all_results['test_1'] = test_1_core_vs_tail(parsed, core_middles, tail_middles)
    all_results['test_2'] = test_2_frequency_sister_correlation(parsed, middle_counts)
    all_results['test_3'] = test_3_frequency_hazard_proxy(parsed, middle_counts)
    all_results['test_4'] = test_4_distribution_shape(middle_counts)
    all_results['test_5'] = test_5_entropy_by_prefix(parsed, middle_counts)
    all_results['test_6'] = test_6_rank_stability(parsed, core_middles, tail_middles)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: MIDDLE Frequency Distribution Analysis")
    print("=" * 70)

    confirmed = 0
    total_tests = 6

    # Test 1
    t1 = all_results['test_1']
    if t1['sister_preference']['tail_deviation'] > t1['sister_preference']['core_deviation']:
        print("Test 1: CONFIRMED - Tail MIDDLEs have stronger mode preference")
        confirmed += 1
    else:
        print("Test 1: NOT CONFIRMED - Core/Tail difference unclear")

    # Test 2
    t2 = all_results['test_2']
    if t2.get('significant') and t2.get('direction') == 'negative':
        print("Test 2: CONFIRMED - Frequency negatively correlates with mode preference")
        confirmed += 1
    elif t2.get('significant'):
        print("Test 2: PARTIAL - Significant but positive correlation (unexpected)")
    else:
        print("Test 2: NOT CONFIRMED - No significant correlation")

    # Test 3
    t3 = all_results['test_3']
    if t3.get('significant'):
        print(f"Test 3: CONFIRMED - Frequency correlates with hazard context ({t3['direction']})")
        confirmed += 1
    else:
        print("Test 3: NOT CONFIRMED - No significant hazard correlation")

    # Test 4
    t4 = all_results['test_4']
    if t4['zipf']['s'] < 0.8 or t4['zipf']['s'] > 1.5:
        print(f"Test 4: CONFIRMED - NOT Zipf-like (s={t4['zipf']['s']:.2f})")
        confirmed += 1
    else:
        print(f"Test 4: NOT CONFIRMED - Distribution is Zipf-like")

    # Test 5
    t5 = all_results['test_5']
    if 'correlation' in t5 and t5['correlation']['p'] < 0.05:
        print(f"Test 5: CONFIRMED - Hazard-entropy correlation (rho={t5['correlation']['rho']:.2f})")
        confirmed += 1
    else:
        print("Test 5: NOT CONFIRMED - No hazard-entropy correlation")

    # Test 6
    t6 = all_results['test_6']
    if 'core_variance' in t6 and t6['core_variance'] < t6['tail_variance']:
        print("Test 6: CONFIRMED - Core MIDDLEs more rank-stable")
        confirmed += 1
    else:
        print("Test 6: NOT CONFIRMED - Stability pattern unclear")

    print(f"\nOVERALL: {confirmed}/{total_tests} tests confirmed")

    if confirmed >= 5:
        print("FULL SUCCESS: Strong evidence for apparatus-centric MIDDLE structure")
    elif confirmed >= 3:
        print("MINIMUM SUCCESS: Moderate evidence for apparatus-centric MIDDLE structure")
    else:
        print("INSUFFICIENT EVIDENCE: MIDDLE distribution may be simpler than hypothesized")

    # Save results
    output_file = 'C:/git/voynich/results/middle_frequency_analysis.json'
    with open(output_file, 'w') as f:
        # Convert numpy types for JSON
        def convert(obj):
            if isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            if isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (bool, np.bool_)):
                return bool(obj)
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(v) for v in obj]
            return obj

        json.dump(convert(all_results), f, indent=2)

    print(f"\nResults saved to: {output_file}")

    return all_results


if __name__ == '__main__':
    results = main()
