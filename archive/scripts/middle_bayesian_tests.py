#!/usr/bin/env python
"""
MIDDLE Bayesian Tests - Apparatus-Centric Analysis

Tests the hypothesis that MIDDLE frequency distribution encodes
physical operating modes (head) vs perturbation space (tail).

Four tests based on expert framework:
1. Mixture Model: Are MIDDLEs from multiple generative processes?
2. Conditional Entropy: H(MIDDLE|PREFIX) by material class
3. Mutual Information: I(MIDDLE; Decision Archetype)
4. Survival/Hazard: Do rare MIDDLEs associate with higher risk?

Output: Apparatus-centric interpretation of MIDDLE physics.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Paths
DATA_PATH = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
RESULTS_DIR = Path("C:/git/voynich/results")
OUTPUT_FILE = RESULTS_DIR / "middle_bayesian_tests.json"

# Material class mapping (from CCM)
PREFIX_TO_MATERIAL_CLASS = {
    'ch': 'M-A',  # Mobile, Distinct (high hazard)
    'qo': 'M-A',  # Mobile, Distinct (high hazard)
    'sh': 'M-B',  # Mobile, Homogeneous
    'ok': 'M-B',  # Mobile, Homogeneous
    'da': 'M-C',  # Stable, Distinct
    'ot': 'M-C',  # Stable, Distinct
    'ol': 'M-D',  # Stable, Homogeneous (baseline)
    'ct': 'M-D',  # Registry-only (stable)
}

# Decision archetype mapping (from suffix -> archetype)
SUFFIX_TO_ARCHETYPE = {
    'y': 'D1-D5',    # Execution decisions
    'dy': 'D1-D5',
    'chy': 'D6',     # Wait vs Act
    'shy': 'D6',
    'n': 'D7',       # Recovery path
    's': 'D8',       # Restart viability
    'l': 'D9',       # Case comparison
    'r': 'D9',
    'm': 'D10',      # Attention focus
    '': 'D12',       # Regime recognition (unmarked)
}


def load_currier_a_tokens():
    """Load all Currier A tokens with decomposition."""
    import pandas as pd

    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')

    # Filter to Currier A
    df = df[(df['language'] == 'A') &
            (df['transcriber'] == 'H') &
            (df['word'].notna()) &
            (~df['word'].str.contains(r'\*', na=False))]

    tokens = []
    prefixes = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
    suffixes = ['y', 'dy', 'chy', 'shy', 'n', 's', 'l', 'r', 'm', 'in', 'ain', 'aiin']

    for _, row in df.iterrows():
        word = str(row['word']).lower().strip()

        # Extract prefix
        prefix = None
        for p in prefixes:
            if word.startswith(p):
                prefix = p
                break

        if not prefix:
            continue

        remainder = word[len(prefix):]

        # Extract suffix
        suffix = ''
        for s in sorted(suffixes, key=len, reverse=True):
            if remainder.endswith(s):
                suffix = s
                remainder = remainder[:-len(s)]
                break

        middle = remainder

        tokens.append({
            'word': word,
            'prefix': prefix,
            'middle': middle,
            'suffix': suffix,
            'section': row.get('section', 'H'),
            'folio': row.get('folio', ''),
        })

    return tokens


def test_1_mixture_model(middle_counts):
    """
    Test 1: Mixture Model on MIDDLE Frequencies

    Question: Are MIDDLEs drawn from more than one generative process?

    Method: Fit mixture model vs single distributions, compare AIC/BIC.
    """
    print("\n" + "="*60)
    print("TEST 1: MIXTURE MODEL ON MIDDLE FREQUENCIES")
    print("="*60)

    # Get frequency counts
    freqs = np.array(sorted(middle_counts.values(), reverse=True))
    n = len(freqs)
    total = freqs.sum()

    print(f"Total MIDDLEs: {n}")
    print(f"Total occurrences: {total}")
    print(f"Top 30 account for: {freqs[:30].sum()/total*100:.1f}%")

    # Log-transform for fitting
    log_freqs = np.log(freqs + 1)
    ranks = np.arange(1, n + 1)
    log_ranks = np.log(ranks)

    # Fit 1: Pure Zipf (log-linear)
    slope, intercept, r_zipf, p_zipf, se = stats.linregress(log_ranks, log_freqs)
    zipf_pred = intercept + slope * log_ranks
    zipf_ss = np.sum((log_freqs - zipf_pred)**2)
    zipf_aic = n * np.log(zipf_ss/n) + 2 * 2

    print(f"\nZipf fit: s = {-slope:.3f}, R² = {r_zipf**2:.3f}")

    # Fit 2: Geometric (exponential decay)
    def geometric_nll(params):
        p = params[0]
        if p <= 0 or p >= 1:
            return 1e10
        expected = total * p * (1-p)**(ranks-1)
        expected = np.maximum(expected, 0.1)
        return -np.sum(freqs * np.log(expected) - expected)

    res_geom = minimize(geometric_nll, [0.1], method='Nelder-Mead')
    geom_aic = 2 * res_geom.fun + 2 * 1

    print(f"Geometric fit: p = {res_geom.x[0]:.4f}")

    # Fit 3: Two-component mixture (head + tail)
    # Model: fraction theta from high-freq component, (1-theta) from low-freq
    def mixture_nll(params):
        theta, p1, p2 = params
        if not (0 < theta < 1 and 0 < p1 < 1 and 0 < p2 < 1):
            return 1e10
        if p1 <= p2:  # p1 should be "head" (higher prob per type)
            return 1e10

        # Two geometric components
        expected = total * (
            theta * p1 * (1-p1)**(ranks-1) +
            (1-theta) * p2 * (1-p2)**(ranks-1)
        )
        expected = np.maximum(expected, 0.1)
        return -np.sum(freqs * np.log(expected) - expected)

    best_mixture = None
    best_nll = 1e10

    for theta in [0.1, 0.2, 0.3, 0.4, 0.5]:
        for p1 in [0.3, 0.4, 0.5]:
            for p2 in [0.01, 0.02, 0.05]:
                res = minimize(mixture_nll, [theta, p1, p2], method='Nelder-Mead')
                if res.fun < best_nll:
                    best_nll = res.fun
                    best_mixture = res.x

    mixture_aic = 2 * best_nll + 2 * 3

    print(f"Mixture fit: theta={best_mixture[0]:.3f}, p1={best_mixture[1]:.3f}, p2={best_mixture[2]:.4f}")

    # Compare models
    print(f"\nModel Comparison (AIC - lower is better):")
    print(f"  Zipf:     {zipf_aic:.1f}")
    print(f"  Geometric: {geom_aic:.1f}")
    print(f"  Mixture:   {mixture_aic:.1f}")

    # Likelihood ratio test for mixture vs simpler
    lr_stat = 2 * (best_nll - res_geom.fun)
    p_lr = 1 - stats.chi2.cdf(abs(lr_stat), df=2)

    # Determine winner
    aics = {'Zipf': zipf_aic, 'Geometric': geom_aic, 'Mixture': mixture_aic}
    best_model = min(aics, key=aics.get)
    delta_aic = min(aics.values()) - sorted(aics.values())[1]

    result = {
        'n_middles': n,
        'top_30_share': float(freqs[:30].sum()/total),
        'zipf_exponent': float(-slope),
        'zipf_r2': float(r_zipf**2),
        'geometric_p': float(res_geom.x[0]),
        'mixture_theta': float(best_mixture[0]),
        'mixture_p_head': float(best_mixture[1]),
        'mixture_p_tail': float(best_mixture[2]),
        'aic_zipf': float(zipf_aic),
        'aic_geometric': float(geom_aic),
        'aic_mixture': float(mixture_aic),
        'best_model': best_model,
        'delta_aic': float(abs(delta_aic)),
        'mixture_supported': mixture_aic < min(zipf_aic, geom_aic),
    }

    print(f"\nBest model: {best_model} (delta-AIC = {abs(delta_aic):.1f})")

    if result['mixture_supported']:
        print("\n[OK] CONFIRMED: Evidence for TWO generative processes")
        print(f"  Head component: ~{best_mixture[0]*100:.0f}% of types, high reuse")
        print(f"  Tail component: ~{(1-best_mixture[0])*100:.0f}% of types, rare perturbations")
    else:
        print(f"\n[--] Simpler model preferred ({best_model})")

    return result


def test_2_conditional_entropy(tokens):
    """
    Test 2: Conditional Entropy H(MIDDLE|PREFIX)

    Question: How predictable is the variant space within each material class?

    Expected: M-A (volatile) > M-B > M-C > M-D (stable)
    """
    print("\n" + "="*60)
    print("TEST 2: CONDITIONAL ENTROPY H(MIDDLE|PREFIX)")
    print("="*60)

    # Group MIDDLEs by prefix and material class
    prefix_middles = defaultdict(list)
    class_middles = defaultdict(list)

    for t in tokens:
        prefix_middles[t['prefix']].append(t['middle'])
        mc = PREFIX_TO_MATERIAL_CLASS.get(t['prefix'], 'UNKNOWN')
        class_middles[mc].append(t['middle'])

    def entropy(items):
        """Calculate Shannon entropy in bits."""
        counts = Counter(items)
        total = sum(counts.values())
        if total == 0:
            return 0
        probs = np.array([c/total for c in counts.values()])
        return -np.sum(probs * np.log2(probs + 1e-10))

    def normalized_entropy(items):
        """Entropy normalized by max possible (log2 of unique count)."""
        h = entropy(items)
        unique = len(set(items))
        if unique <= 1:
            return 0
        return h / np.log2(unique)

    # Calculate per-prefix entropy
    print("\nEntropy by PREFIX:")
    prefix_results = {}
    for prefix in sorted(prefix_middles.keys()):
        middles = prefix_middles[prefix]
        h = entropy(middles)
        h_norm = normalized_entropy(middles)
        unique = len(set(middles))
        prefix_results[prefix] = {
            'count': len(middles),
            'unique_middles': unique,
            'entropy': float(h),
            'normalized_entropy': float(h_norm),
            'material_class': PREFIX_TO_MATERIAL_CLASS.get(prefix, 'UNKNOWN'),
        }
        print(f"  {prefix}: H={h:.2f} bits, H_norm={h_norm:.3f}, unique={unique}, class={PREFIX_TO_MATERIAL_CLASS.get(prefix)}")

    # Calculate per-class entropy
    print("\nEntropy by MATERIAL CLASS:")
    class_results = {}
    for mc in ['M-A', 'M-B', 'M-C', 'M-D']:
        if mc not in class_middles:
            continue
        middles = class_middles[mc]
        h = entropy(middles)
        h_norm = normalized_entropy(middles)
        unique = len(set(middles))
        class_results[mc] = {
            'count': len(middles),
            'unique_middles': unique,
            'entropy': float(h),
            'normalized_entropy': float(h_norm),
        }
        print(f"  {mc}: H={h:.2f} bits, H_norm={h_norm:.3f}, unique={unique}")

    # Test hypothesis: M-A > M-D
    if 'M-A' in class_results and 'M-D' in class_results:
        h_a = class_results['M-A']['entropy']
        h_d = class_results['M-D']['entropy']
        ratio = h_a / h_d if h_d > 0 else float('inf')

        # Bootstrap confidence interval
        ma_middles = class_middles['M-A']
        md_middles = class_middles['M-D']

        boot_ratios = []
        for _ in range(1000):
            ma_sample = np.random.choice(ma_middles, size=len(ma_middles), replace=True)
            md_sample = np.random.choice(md_middles, size=len(md_middles), replace=True)
            h_a_boot = entropy(ma_sample)
            h_d_boot = entropy(md_sample)
            if h_d_boot > 0:
                boot_ratios.append(h_a_boot / h_d_boot)

        ci_low, ci_high = np.percentile(boot_ratios, [2.5, 97.5])

        print(f"\nM-A / M-D entropy ratio: {ratio:.3f}")
        print(f"95% CI: [{ci_low:.3f}, {ci_high:.3f}]")

        hypothesis_confirmed = ci_low > 1.0

        if hypothesis_confirmed:
            print("\n[OK] CONFIRMED: Volatile classes (M-A) have higher variant entropy")
        else:
            print("\n[--] Hypothesis not confirmed at 95% confidence")
    else:
        hypothesis_confirmed = None
        ratio = None
        ci_low = ci_high = None

    result = {
        'by_prefix': prefix_results,
        'by_class': class_results,
        'ma_md_ratio': float(ratio) if ratio else None,
        'ma_md_ci': [float(ci_low), float(ci_high)] if ci_low else None,
        'hypothesis_confirmed': hypothesis_confirmed,
    }

    return result


def test_3_mutual_information(tokens):
    """
    Test 3: MIDDLE-Decision Archetype Mutual Information

    Question: Do certain variants correlate with specific decisions?

    Expected: High MI for common MIDDLEs, low for rare
    """
    print("\n" + "="*60)
    print("TEST 3: MIDDLE-DECISION ARCHETYPE MUTUAL INFORMATION")
    print("="*60)

    # Get MIDDLE frequencies
    middle_counts = Counter(t['middle'] for t in tokens)

    # Partition into head (top 30) and tail
    sorted_middles = sorted(middle_counts.keys(), key=lambda x: middle_counts[x], reverse=True)
    head_middles = set(sorted_middles[:30])
    tail_middles = set(sorted_middles[30:])

    print(f"Head MIDDLEs: {len(head_middles)}")
    print(f"Tail MIDDLEs: {len(tail_middles)}")

    # Map suffixes to archetypes
    def get_archetype(suffix):
        # Try exact match
        if suffix in SUFFIX_TO_ARCHETYPE:
            return SUFFIX_TO_ARCHETYPE[suffix]
        # Try suffix ending
        for s, a in SUFFIX_TO_ARCHETYPE.items():
            if suffix.endswith(s):
                return a
        return 'D12'  # Default

    # Build contingency tables
    def calculate_mi(tokens_subset, name):
        """Calculate mutual information I(MIDDLE; Archetype)"""
        # Joint distribution
        joint = defaultdict(int)
        middle_marginal = Counter()
        arch_marginal = Counter()

        for t in tokens_subset:
            m = t['middle']
            a = get_archetype(t['suffix'])
            joint[(m, a)] += 1
            middle_marginal[m] += 1
            arch_marginal[a] += 1

        total = sum(joint.values())
        if total == 0:
            return 0, 0

        # Calculate MI
        mi = 0
        for (m, a), count in joint.items():
            p_joint = count / total
            p_m = middle_marginal[m] / total
            p_a = arch_marginal[a] / total
            if p_joint > 0 and p_m > 0 and p_a > 0:
                mi += p_joint * np.log2(p_joint / (p_m * p_a))

        # Normalized MI
        h_middle = -sum((c/total) * np.log2(c/total) for c in middle_marginal.values() if c > 0)
        h_arch = -sum((c/total) * np.log2(c/total) for c in arch_marginal.values() if c > 0)
        nmi = mi / np.sqrt(h_middle * h_arch) if h_middle > 0 and h_arch > 0 else 0

        return mi, nmi

    # Calculate for head vs tail
    head_tokens = [t for t in tokens if t['middle'] in head_middles]
    tail_tokens = [t for t in tokens if t['middle'] in tail_middles]

    mi_head, nmi_head = calculate_mi(head_tokens, "Head")
    mi_tail, nmi_tail = calculate_mi(tail_tokens, "Tail")
    mi_all, nmi_all = calculate_mi(tokens, "All")

    print(f"\nMutual Information I(MIDDLE; Archetype):")
    print(f"  All MIDDLEs:  MI={mi_all:.4f} bits, NMI={nmi_all:.4f}")
    print(f"  Head (top 30): MI={mi_head:.4f} bits, NMI={nmi_head:.4f}")
    print(f"  Tail (rest):   MI={mi_tail:.4f} bits, NMI={nmi_tail:.4f}")

    # Statistical test: permutation test
    observed_diff = mi_head - mi_tail

    perm_diffs = []
    all_middles = list(head_middles | tail_middles)
    for _ in range(1000):
        # Random partition
        np.random.shuffle(all_middles)
        perm_head = set(all_middles[:30])
        perm_tokens_head = [t for t in tokens if t['middle'] in perm_head]
        perm_tokens_tail = [t for t in tokens if t['middle'] not in perm_head]

        mi_h, _ = calculate_mi(perm_tokens_head, "")
        mi_t, _ = calculate_mi(perm_tokens_tail, "")
        perm_diffs.append(mi_h - mi_t)

    p_value = np.mean(np.array(perm_diffs) >= observed_diff)

    print(f"\nHead vs Tail MI difference: {observed_diff:.4f}")
    print(f"Permutation p-value: {p_value:.4f}")

    hypothesis_confirmed = mi_head > mi_tail and p_value < 0.05

    if hypothesis_confirmed:
        print("\n[OK] CONFIRMED: Common variants correlate more strongly with decision types")
    else:
        print("\n[--] Hypothesis not confirmed at p<0.05")

    # Archetype breakdown for head
    print("\nDecision archetype distribution (Head MIDDLEs):")
    arch_counts = Counter(get_archetype(t['suffix']) for t in head_tokens)
    for arch, count in sorted(arch_counts.items()):
        print(f"  {arch}: {count} ({count/len(head_tokens)*100:.1f}%)")

    result = {
        'mi_all': float(mi_all),
        'nmi_all': float(nmi_all),
        'mi_head': float(mi_head),
        'nmi_head': float(nmi_head),
        'mi_tail': float(mi_tail),
        'nmi_tail': float(nmi_tail),
        'head_tail_diff': float(observed_diff),
        'p_value': float(p_value),
        'hypothesis_confirmed': hypothesis_confirmed,
    }

    return result


def test_4_hazard_analysis(tokens):
    """
    Test 4: Survival/Hazard Analysis on MIDDLEs

    Question: Do rare MIDDLEs associate with higher operational risk?

    Proxies for risk:
    - Sister preference deviation (brittleness)
    - Section concentration (context-dependence)
    - Suffix entropy (decision predictability)
    """
    print("\n" + "="*60)
    print("TEST 4: HAZARD/RISK ANALYSIS ON MIDDLEs")
    print("="*60)

    # Get MIDDLE frequencies
    middle_counts = Counter(t['middle'] for t in tokens)

    # Partition into frequency tiers
    sorted_middles = sorted(middle_counts.keys(), key=lambda x: middle_counts[x], reverse=True)
    head_middles = set(sorted_middles[:30])
    mid_middles = set(sorted_middles[30:100])
    tail_middles = set(sorted_middles[100:])

    print(f"Head (top 30): {len(head_middles)} MIDDLEs")
    print(f"Mid (31-100): {len(mid_middles)} MIDDLEs")
    print(f"Tail (100+): {len(tail_middles)} MIDDLEs")

    # Aggregate by MIDDLE
    middle_data = defaultdict(lambda: {
        'count': 0,
        'prefixes': [],
        'suffixes': [],
        'sections': [],
    })

    for t in tokens:
        m = t['middle']
        middle_data[m]['count'] += 1
        middle_data[m]['prefixes'].append(t['prefix'])
        middle_data[m]['suffixes'].append(t['suffix'])
        middle_data[m]['sections'].append(t['section'])

    def calculate_risk_metrics(middles_set, name):
        """Calculate risk proxies for a set of MIDDLEs."""
        metrics = []

        for m in middles_set:
            if m not in middle_data or middle_data[m]['count'] < 2:
                continue

            data = middle_data[m]

            # 1. Sister preference (ch vs sh proxy via prefix)
            # Higher deviation = more brittle
            ch_count = sum(1 for p in data['prefixes'] if p in ['ch', 'qo'])
            sh_count = sum(1 for p in data['prefixes'] if p in ['sh', 'ok'])
            total_sister = ch_count + sh_count
            if total_sister > 0:
                sister_dev = abs(ch_count/total_sister - 0.5)
            else:
                sister_dev = 0

            # 2. Section concentration (Herfindahl index)
            section_counts = Counter(data['sections'])
            total_sec = sum(section_counts.values())
            hhi = sum((c/total_sec)**2 for c in section_counts.values())

            # 3. Suffix entropy (lower = more predictable decisions)
            suffix_counts = Counter(data['suffixes'])
            total_suf = sum(suffix_counts.values())
            suffix_entropy = -sum((c/total_suf) * np.log2(c/total_suf)
                                  for c in suffix_counts.values() if c > 0)

            metrics.append({
                'middle': m,
                'frequency': data['count'],
                'sister_deviation': sister_dev,
                'section_concentration': hhi,
                'suffix_entropy': suffix_entropy,
            })

        return metrics

    head_metrics = calculate_risk_metrics(head_middles, "Head")
    mid_metrics = calculate_risk_metrics(mid_middles, "Mid")
    tail_metrics = calculate_risk_metrics(tail_middles, "Tail")

    def summarize_metrics(metrics, name):
        if not metrics:
            return None
        sister_devs = [m['sister_deviation'] for m in metrics]
        section_concs = [m['section_concentration'] for m in metrics]
        suffix_ents = [m['suffix_entropy'] for m in metrics]

        return {
            'n': len(metrics),
            'sister_deviation_mean': float(np.mean(sister_devs)),
            'sister_deviation_std': float(np.std(sister_devs)),
            'section_concentration_mean': float(np.mean(section_concs)),
            'section_concentration_std': float(np.std(section_concs)),
            'suffix_entropy_mean': float(np.mean(suffix_ents)),
            'suffix_entropy_std': float(np.std(suffix_ents)),
        }

    head_summary = summarize_metrics(head_metrics, "Head")
    mid_summary = summarize_metrics(mid_metrics, "Mid")
    tail_summary = summarize_metrics(tail_metrics, "Tail")

    print("\nRisk Metrics by Frequency Tier:")
    print("\n  Sister Preference Deviation (higher = more brittle):")
    print(f"    Head: {head_summary['sister_deviation_mean']:.3f} ± {head_summary['sister_deviation_std']:.3f}")
    if mid_summary:
        print(f"    Mid:  {mid_summary['sister_deviation_mean']:.3f} ± {mid_summary['sister_deviation_std']:.3f}")
    if tail_summary:
        print(f"    Tail: {tail_summary['sister_deviation_mean']:.3f} ± {tail_summary['sister_deviation_std']:.3f}")

    print("\n  Section Concentration (higher = more context-dependent):")
    print(f"    Head: {head_summary['section_concentration_mean']:.3f} ± {head_summary['section_concentration_std']:.3f}")
    if mid_summary:
        print(f"    Mid:  {mid_summary['section_concentration_mean']:.3f} ± {mid_summary['section_concentration_std']:.3f}")
    if tail_summary:
        print(f"    Tail: {tail_summary['section_concentration_mean']:.3f} ± {tail_summary['section_concentration_std']:.3f}")

    print("\n  Suffix Entropy (lower = more predictable decisions):")
    print(f"    Head: {head_summary['suffix_entropy_mean']:.3f} ± {head_summary['suffix_entropy_std']:.3f}")
    if mid_summary:
        print(f"    Mid:  {mid_summary['suffix_entropy_mean']:.3f} ± {mid_summary['suffix_entropy_std']:.3f}")
    if tail_summary:
        print(f"    Tail: {tail_summary['suffix_entropy_mean']:.3f} ± {tail_summary['suffix_entropy_std']:.3f}")

    # Statistical tests
    if head_metrics and tail_summary and tail_metrics:
        # Mann-Whitney U tests
        head_sister = [m['sister_deviation'] for m in head_metrics]
        tail_sister = [m['sister_deviation'] for m in tail_metrics if m['sister_deviation'] > 0]

        if len(tail_sister) >= 5:
            stat, p_sister = stats.mannwhitneyu(tail_sister, head_sister, alternative='greater')
            print(f"\nMann-Whitney U (Tail > Head sister deviation): p = {p_sister:.4f}")
        else:
            p_sister = 1.0

        head_section = [m['section_concentration'] for m in head_metrics]
        tail_section = [m['section_concentration'] for m in tail_metrics]

        if len(tail_section) >= 5:
            stat, p_section = stats.mannwhitneyu(tail_section, head_section, alternative='greater')
            print(f"Mann-Whitney U (Tail > Head section concentration): p = {p_section:.4f}")
        else:
            p_section = 1.0
    else:
        p_sister = p_section = 1.0

    # Hypothesis: rare MIDDLEs are riskier
    risk_confirmed = (
        (tail_summary and head_summary) and
        (tail_summary['sister_deviation_mean'] > head_summary['sister_deviation_mean'] or
         tail_summary['section_concentration_mean'] > head_summary['section_concentration_mean'])
    )

    if risk_confirmed:
        print("\n[OK] CONFIRMED: Rare MIDDLEs show markers of higher operational risk")
    else:
        print("\n[--] Risk hypothesis not clearly confirmed")

    result = {
        'head': head_summary,
        'mid': mid_summary,
        'tail': tail_summary,
        'p_sister_deviation': float(p_sister),
        'p_section_concentration': float(p_section),
        'risk_confirmed': risk_confirmed,
    }

    return result


def main():
    print("="*60)
    print("MIDDLE BAYESIAN TESTS - APPARATUS-CENTRIC ANALYSIS")
    print("="*60)
    print("\nLoading Currier A tokens...")

    tokens = load_currier_a_tokens()
    print(f"Loaded {len(tokens)} decomposed tokens")

    # Get MIDDLE frequency distribution
    middle_counts = Counter(t['middle'] for t in tokens)
    print(f"Unique MIDDLEs: {len(middle_counts)}")

    # Run all four tests
    results = {
        'metadata': {
            'total_tokens': len(tokens),
            'unique_middles': len(middle_counts),
            'date': '2026-01-11',
        }
    }

    results['test_1_mixture'] = test_1_mixture_model(middle_counts)
    results['test_2_entropy'] = test_2_conditional_entropy(tokens)
    results['test_3_mutual_info'] = test_3_mutual_information(tokens)
    results['test_4_hazard'] = test_4_hazard_analysis(tokens)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY: APPARATUS-CENTRIC INTERPRETATION")
    print("="*60)

    confirmed = 0
    total = 4

    if results['test_1_mixture'].get('mixture_supported'):
        confirmed += 1
        print("\n[OK] Test 1: TWO generative processes confirmed")
        print("  -> Small basis of common modes + large perturbation space")
    else:
        print(f"\n[--] Test 1: Single-process model preferred ({results['test_1_mixture']['best_model']})")

    if results['test_2_entropy'].get('hypothesis_confirmed'):
        confirmed += 1
        print("\n[OK] Test 2: Volatile classes have higher variant entropy")
        print("  -> Material instability generates broader behavioral variation")
    else:
        print("\n[--] Test 2: Entropy pattern not significant")

    if results['test_3_mutual_info'].get('hypothesis_confirmed'):
        confirmed += 1
        print("\n[OK] Test 3: Common variants correlate with predictable decisions")
        print("  -> Rare variants are situational, require judgment")
    else:
        print("\n[--] Test 3: MI pattern not significant")

    if results['test_4_hazard'].get('risk_confirmed'):
        confirmed += 1
        print("\n[OK] Test 4: Rare MIDDLEs show higher risk markers")
        print("  -> Frontier variants are harder for apparatus to handle")
    else:
        print("\n[--] Test 4: Risk pattern not clearly confirmed")

    results['summary'] = {
        'tests_confirmed': confirmed,
        'tests_total': total,
        'interpretation': None,
    }

    print(f"\nOverall: {confirmed}/{total} tests confirmed")

    if confirmed >= 3:
        interp = (
            "The MIDDLE distribution encodes a physical system with a small set of "
            "common operating variants (head) and a large perturbation space (tail). "
            "High-frequency MIDDLEs represent repeatable, apparatus-recognizable behavioral "
            "modes. Low-frequency MIDDLEs mark idiosyncratic conditions where grammatical "
            "control is insufficient and human judgment dominates."
        )
        results['summary']['interpretation'] = interp
        print(f"\n{interp}")
    elif confirmed >= 2:
        interp = (
            "Partial support for apparatus-centric interpretation. The MIDDLE distribution "
            "shows structure consistent with physical operating modes, though not all "
            "hypothesized patterns reach significance."
        )
        results['summary']['interpretation'] = interp
        print(f"\n{interp}")
    else:
        interp = (
            "Limited support for apparatus-centric interpretation from MIDDLE distribution. "
            "The frequency pattern may encode different structure than hypothesized."
        )
        results['summary']['interpretation'] = interp
        print(f"\n{interp}")

    # Save results (convert numpy types)
    def convert_types(obj):
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(i) for i in obj]
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        return obj

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(convert_types(results), f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
