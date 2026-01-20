"""
A_REGIME_STRATIFICATION PHASE

Investigates whether A vocabulary stratifies by REGIME compatibility
and whether morphological markers (PREFIX/SUFFIX) predict REGIME exclusivity.

Tests:
  T1: Morphological analysis - do PREFIX/SUFFIX predict REGIME compatibility?
  T2: Frequency analysis - are REGIME-specific tokens rare artifacts?
  T3: AZC cross-reference - do REGIME-specific tokens have distinct AZC profiles?
  T4: Folio clustering - do REGIME constraints cluster on certain A folios?

Background:
  From A_ORCHESTRATION_TEST, we found:
  - 39.3% of A tokens appearing in B are REGIME-specific (single REGIME)
  - 22.0% are universal (all 4 REGIMEs)
  - Hint of morphological patterning (d- for REGIME_1, -ol for REGIME_4)
"""

import json
import re
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats

project_root = Path(__file__).parent.parent.parent

# ============================================================================
# DATA LOADING (shared across all tests)
# ============================================================================

def load_transcript_data():
    """Load H-track transcription data."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"') if len(parts) > 2 else ''
                language = parts[6].strip('"') if len(parts) > 6 else ''
                transcriber = parts[12].strip('"').strip()
                if transcriber == 'H' and word and folio:
                    data.append({
                        'token': word.lower(),
                        'folio': folio,
                        'currier': language
                    })
    return data


def load_regime_mapping():
    """Load REGIME to folio mapping."""
    filepath = project_root / 'results' / 'regime_folio_mapping.json'
    with open(filepath, 'r') as f:
        regime_folios = json.load(f)
    folio_to_regime = {}
    for regime, folios in regime_folios.items():
        for folio in folios:
            folio_to_regime[folio] = regime
    return folio_to_regime


def get_token_regimes(data, folio_to_regime):
    """For each token, find which REGIMEs it appears in (via B folios)."""
    b_data = [d for d in data if d['currier'] == 'B']
    token_regimes = defaultdict(set)
    for d in b_data:
        regime = folio_to_regime.get(d['folio'])
        if regime:
            token_regimes[d['token']].add(regime)
    return token_regimes


def classify_tokens_by_regime_count(a_tokens, token_regimes):
    """Classify A tokens by how many REGIMEs they're compatible with."""
    single_regime = {}  # token -> regime
    multi_regime = {}   # token -> set of regimes
    universal = []      # tokens in all 4 REGIMEs
    no_b_presence = []  # A-only tokens

    for token in a_tokens:
        regimes = token_regimes.get(token, set())
        if len(regimes) == 0:
            no_b_presence.append(token)
        elif len(regimes) == 1:
            single_regime[token] = list(regimes)[0]
        elif len(regimes) == 4:
            universal.append(token)
        else:
            multi_regime[token] = regimes

    return single_regime, multi_regime, universal, no_b_presence


# ============================================================================
# MORPHOLOGY HELPERS
# ============================================================================

# Common PREFIX patterns (from CASC and existing morphology analysis)
PREFIXES = ['qok', 'qo', 'ok', 'ot', 'ch', 'sh', 'ck', 'ct', 'cth', 'yk', 'yt',
            'dch', 'kch', 'pch', 'tch', 'fch', 'lch', 's', 'k', 'd', 'l', 'r', 'y']

# Common SUFFIX patterns
SUFFIXES = ['aiin', 'ain', 'iin', 'in', 'ol', 'al', 'or', 'ar', 'dy', 'chy',
            'ky', 'ty', 'y', 'o', 'l', 'n', 'r', 'd', 'g', 'm', 's']


def extract_morphology(token):
    """Extract PREFIX, MIDDLE, SUFFIX from token."""
    # Try prefixes (longest match first)
    prefix = ''
    remainder = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p) and len(token) > len(p):
            prefix = p
            remainder = token[len(p):]
            break

    # Try suffixes (longest match first)
    suffix = ''
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break

    middle = remainder
    return prefix, middle, suffix


# ============================================================================
# T1: MORPHOLOGICAL ANALYSIS
# ============================================================================

def test_morphological_prediction(single_regime, multi_regime, universal, a_token_freq):
    """
    T1: Do PREFIX/SUFFIX components predict REGIME exclusivity?

    Compare morphological profiles of:
    - REGIME-specific tokens (single_regime)
    - Universal tokens (all 4 REGIMEs)
    - Partial compatibility tokens (2-3 REGIMEs)
    """
    print("\n" + "=" * 70)
    print("T1: MORPHOLOGICAL ANALYSIS")
    print("Do PREFIX/SUFFIX predict REGIME compatibility?")
    print("=" * 70)

    results = {'test': 'T1_morphological_prediction'}

    # Extract morphology for each category
    def get_morphology_profile(tokens):
        prefixes = Counter()
        suffixes = Counter()
        middles = Counter()
        for token in tokens:
            p, m, s = extract_morphology(token)
            if p: prefixes[p] += 1
            if s: suffixes[s] += 1
            if m: middles[m] += 1
        return prefixes, suffixes, middles

    # Profiles by compatibility category
    single_p, single_s, single_m = get_morphology_profile(single_regime.keys())
    universal_p, universal_s, universal_m = get_morphology_profile(universal)
    partial_p, partial_s, partial_m = get_morphology_profile(multi_regime.keys())

    print("\n[1] PREFIX distribution by compatibility category:")
    print("-" * 60)

    all_prefixes = set(single_p.keys()) | set(universal_p.keys()) | set(partial_p.keys())
    top_prefixes = sorted(all_prefixes, key=lambda x: single_p[x] + universal_p[x] + partial_p[x], reverse=True)[:10]

    print(f"    {'PREFIX':<8} {'Single%':<10} {'Partial%':<10} {'Universal%':<10}")
    print("    " + "-" * 40)

    prefix_data = []
    for p in top_prefixes:
        s_count = single_p[p]
        p_count = partial_p[p]
        u_count = universal_p[p]
        total = s_count + p_count + u_count
        if total >= 5:  # Only show if sufficient data
            s_pct = 100 * s_count / len(single_regime) if single_regime else 0
            p_pct = 100 * p_count / len(multi_regime) if multi_regime else 0
            u_pct = 100 * u_count / len(universal) if universal else 0
            print(f"    {p:<8} {s_pct:<10.1f} {p_pct:<10.1f} {u_pct:<10.1f}")
            prefix_data.append({'prefix': p, 'single': s_count, 'partial': p_count, 'universal': u_count})

    results['prefix_distribution'] = prefix_data

    # Chi-square test: PREFIX x Compatibility
    print("\n[2] Chi-square test: PREFIX x Compatibility category")

    # Build contingency table for top 5 prefixes
    contingency_prefix = []
    for p in top_prefixes[:5]:
        row = [single_p[p], partial_p[p], universal_p[p]]
        if sum(row) >= 5:
            contingency_prefix.append(row)

    if len(contingency_prefix) >= 2:
        contingency_prefix = np.array(contingency_prefix)
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency_prefix)
        n = contingency_prefix.sum()
        min_dim = min(contingency_prefix.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n * min_dim > 0 else 0

        print(f"    Chi-squared: {chi2:.4f}")
        print(f"    p-value: {p_val:.6f}")
        print(f"    Cramer's V: {cramers_v:.4f}")

        results['prefix_chi2'] = chi2
        results['prefix_p_value'] = p_val
        results['prefix_cramers_v'] = cramers_v

        if p_val < 0.01 and cramers_v > 0.1:
            print("    -> PREFIX PREDICTS compatibility (moderate effect)")
        elif p_val < 0.01:
            print("    -> Significant but negligible effect")
        else:
            print("    -> PREFIX does NOT predict compatibility")

    # SUFFIX analysis
    print("\n[3] SUFFIX distribution by compatibility category:")
    print("-" * 60)

    all_suffixes = set(single_s.keys()) | set(universal_s.keys()) | set(partial_s.keys())
    top_suffixes = sorted(all_suffixes, key=lambda x: single_s[x] + universal_s[x] + partial_s[x], reverse=True)[:10]

    print(f"    {'SUFFIX':<8} {'Single%':<10} {'Partial%':<10} {'Universal%':<10}")
    print("    " + "-" * 40)

    suffix_data = []
    for s in top_suffixes:
        s_count = single_s[s]
        p_count = partial_s[s]
        u_count = universal_s[s]
        total = s_count + p_count + u_count
        if total >= 5:
            s_pct = 100 * s_count / len(single_regime) if single_regime else 0
            p_pct = 100 * p_count / len(multi_regime) if multi_regime else 0
            u_pct = 100 * u_count / len(universal) if universal else 0
            print(f"    {s:<8} {s_pct:<10.1f} {p_pct:<10.1f} {u_pct:<10.1f}")
            suffix_data.append({'suffix': s, 'single': s_count, 'partial': p_count, 'universal': u_count})

    results['suffix_distribution'] = suffix_data

    # Chi-square test: SUFFIX x Compatibility
    print("\n[4] Chi-square test: SUFFIX x Compatibility category")

    contingency_suffix = []
    for s in top_suffixes[:5]:
        row = [single_s[s], partial_s[s], universal_s[s]]
        if sum(row) >= 5:
            contingency_suffix.append(row)

    if len(contingency_suffix) >= 2:
        contingency_suffix = np.array(contingency_suffix)
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency_suffix)
        n = contingency_suffix.sum()
        min_dim = min(contingency_suffix.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n * min_dim > 0 else 0

        print(f"    Chi-squared: {chi2:.4f}")
        print(f"    p-value: {p_val:.6f}")
        print(f"    Cramer's V: {cramers_v:.4f}")

        results['suffix_chi2'] = chi2
        results['suffix_p_value'] = p_val
        results['suffix_cramers_v'] = cramers_v

        if p_val < 0.01 and cramers_v > 0.1:
            print("    -> SUFFIX PREDICTS compatibility (moderate effect)")
        elif p_val < 0.01:
            print("    -> Significant but negligible effect")
        else:
            print("    -> SUFFIX does NOT predict compatibility")

    # Per-REGIME morphology breakdown
    print("\n[5] PREFIX distribution by specific REGIME (single-REGIME tokens only):")
    print("-" * 60)

    regime_prefixes = defaultdict(Counter)
    for token, regime in single_regime.items():
        p, m, s = extract_morphology(token)
        if p:
            regime_prefixes[regime][p] += 1

    all_regime_prefixes = set()
    for r in regime_prefixes:
        all_regime_prefixes.update(regime_prefixes[r].keys())

    top_regime_prefixes = sorted(all_regime_prefixes,
        key=lambda x: sum(regime_prefixes[r][x] for r in regime_prefixes), reverse=True)[:8]

    print(f"    {'PREFIX':<8} {'R1':<8} {'R2':<8} {'R3':<8} {'R4':<8}")
    print("    " + "-" * 35)

    regime_prefix_data = []
    for p in top_regime_prefixes:
        r1 = regime_prefixes['REGIME_1'][p]
        r2 = regime_prefixes['REGIME_2'][p]
        r3 = regime_prefixes['REGIME_3'][p]
        r4 = regime_prefixes['REGIME_4'][p]
        if r1 + r2 + r3 + r4 >= 3:
            print(f"    {p:<8} {r1:<8} {r2:<8} {r3:<8} {r4:<8}")
            regime_prefix_data.append({'prefix': p, 'R1': r1, 'R2': r2, 'R3': r3, 'R4': r4})

    results['regime_prefix_distribution'] = regime_prefix_data

    # Chi-square: PREFIX x REGIME
    print("\n[6] Chi-square test: PREFIX x REGIME (single-REGIME tokens)")

    contingency_regime = []
    for p in top_regime_prefixes[:5]:
        row = [regime_prefixes['REGIME_1'][p], regime_prefixes['REGIME_2'][p],
               regime_prefixes['REGIME_3'][p], regime_prefixes['REGIME_4'][p]]
        if sum(row) >= 3:
            contingency_regime.append(row)

    if len(contingency_regime) >= 2:
        contingency_regime = np.array(contingency_regime)
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency_regime)
        n = contingency_regime.sum()
        min_dim = min(contingency_regime.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n * min_dim > 0 else 0

        print(f"    Chi-squared: {chi2:.4f}")
        print(f"    p-value: {p_val:.6f}")
        print(f"    Cramer's V: {cramers_v:.4f}")

        results['regime_prefix_chi2'] = chi2
        results['regime_prefix_p_value'] = p_val
        results['regime_prefix_cramers_v'] = cramers_v

        if p_val < 0.01 and cramers_v > 0.15:
            print("    -> PREFIX PREDICTS which REGIME (moderate+ effect)")
        elif p_val < 0.01 and cramers_v > 0.1:
            print("    -> PREFIX weakly predicts REGIME")
        else:
            print("    -> PREFIX does NOT predict specific REGIME")

    return results


# ============================================================================
# T2: FREQUENCY ANALYSIS
# ============================================================================

def test_frequency_distribution(single_regime, multi_regime, universal, a_token_freq):
    """
    T2: Are REGIME-specific tokens rare artifacts?

    Compare frequency distributions of single-REGIME vs multi-REGIME vs universal tokens.
    If single-REGIME tokens are predominantly hapax, the finding may be artifact.
    """
    print("\n" + "=" * 70)
    print("T2: FREQUENCY ANALYSIS")
    print("Are REGIME-specific tokens rare artifacts?")
    print("=" * 70)

    results = {'test': 'T2_frequency_analysis'}

    # Get frequencies for each category
    single_freqs = [a_token_freq[t] for t in single_regime.keys()]
    partial_freqs = [a_token_freq[t] for t in multi_regime.keys()]
    universal_freqs = [a_token_freq[t] for t in universal]

    print("\n[1] Frequency statistics by compatibility category:")
    print("-" * 60)

    def freq_stats(freqs, name):
        if not freqs:
            return
        mean_f = np.mean(freqs)
        median_f = np.median(freqs)
        hapax = sum(1 for f in freqs if f == 1)
        hapax_pct = 100 * hapax / len(freqs)
        print(f"    {name}:")
        print(f"        N = {len(freqs)}")
        print(f"        Mean frequency: {mean_f:.2f}")
        print(f"        Median frequency: {median_f:.1f}")
        print(f"        Hapax legomena: {hapax} ({hapax_pct:.1f}%)")
        return {'n': len(freqs), 'mean': mean_f, 'median': median_f,
                'hapax_count': hapax, 'hapax_pct': hapax_pct}

    results['single_regime_stats'] = freq_stats(single_freqs, "Single-REGIME tokens")
    results['partial_stats'] = freq_stats(partial_freqs, "Partial (2-3 REGIMEs)")
    results['universal_stats'] = freq_stats(universal_freqs, "Universal (4 REGIMEs)")

    # Mann-Whitney U test: single vs universal
    print("\n[2] Mann-Whitney U test: Single-REGIME vs Universal")

    if single_freqs and universal_freqs:
        stat, p_val = stats.mannwhitneyu(single_freqs, universal_freqs, alternative='two-sided')
        print(f"    U-statistic: {stat:.1f}")
        print(f"    p-value: {p_val:.6f}")

        # Effect size (rank-biserial correlation)
        n1, n2 = len(single_freqs), len(universal_freqs)
        r = 1 - (2 * stat) / (n1 * n2)
        print(f"    Effect size (r): {r:.4f}")

        results['single_vs_universal_U'] = stat
        results['single_vs_universal_p'] = p_val
        results['single_vs_universal_r'] = r

        if p_val < 0.01 and abs(r) > 0.3:
            if r > 0:
                print("    -> Single-REGIME tokens are LESS frequent (moderate effect)")
            else:
                print("    -> Single-REGIME tokens are MORE frequent (moderate effect)")
        elif p_val < 0.01:
            print("    -> Significant difference but small effect")
        else:
            print("    -> No significant frequency difference")

    # Frequency-stratified analysis
    print("\n[3] Compatibility by frequency tier:")
    print("-" * 60)

    # Categorize all tokens by frequency tier
    all_tokens = list(single_regime.keys()) + list(multi_regime.keys()) + universal

    tiers = {
        'hapax (1x)': [],
        'rare (2-5x)': [],
        'common (6-20x)': [],
        'frequent (>20x)': []
    }

    for token in all_tokens:
        freq = a_token_freq[token]
        if freq == 1:
            tiers['hapax (1x)'].append(token)
        elif freq <= 5:
            tiers['rare (2-5x)'].append(token)
        elif freq <= 20:
            tiers['common (6-20x)'].append(token)
        else:
            tiers['frequent (>20x)'].append(token)

    print(f"    {'Tier':<18} {'Single%':<10} {'Partial%':<10} {'Univ%':<10} {'N':<8}")
    print("    " + "-" * 55)

    tier_data = []
    for tier_name, tier_tokens in tiers.items():
        if not tier_tokens:
            continue
        single_in_tier = sum(1 for t in tier_tokens if t in single_regime)
        partial_in_tier = sum(1 for t in tier_tokens if t in multi_regime)
        univ_in_tier = sum(1 for t in tier_tokens if t in universal)
        total = len(tier_tokens)

        s_pct = 100 * single_in_tier / total
        p_pct = 100 * partial_in_tier / total
        u_pct = 100 * univ_in_tier / total

        print(f"    {tier_name:<18} {s_pct:<10.1f} {p_pct:<10.1f} {u_pct:<10.1f} {total:<8}")
        tier_data.append({'tier': tier_name, 'single_pct': s_pct, 'partial_pct': p_pct,
                         'universal_pct': u_pct, 'n': total})

    results['tier_breakdown'] = tier_data

    # Chi-square: Frequency tier x Compatibility
    print("\n[4] Chi-square test: Frequency tier x Compatibility")

    contingency = []
    for tier_name, tier_tokens in tiers.items():
        if len(tier_tokens) >= 10:
            single_in_tier = sum(1 for t in tier_tokens if t in single_regime)
            partial_in_tier = sum(1 for t in tier_tokens if t in multi_regime)
            univ_in_tier = sum(1 for t in tier_tokens if t in universal)
            contingency.append([single_in_tier, partial_in_tier, univ_in_tier])

    if len(contingency) >= 2:
        contingency = np.array(contingency)
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
        n = contingency.sum()
        min_dim = min(contingency.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n * min_dim > 0 else 0

        print(f"    Chi-squared: {chi2:.4f}")
        print(f"    p-value: {p_val:.6f}")
        print(f"    Cramer's V: {cramers_v:.4f}")

        results['tier_chi2'] = chi2
        results['tier_p_value'] = p_val
        results['tier_cramers_v'] = cramers_v

        if p_val < 0.01 and cramers_v > 0.15:
            print("    -> Compatibility DEPENDS on frequency (artifact risk)")
        elif p_val < 0.01 and cramers_v > 0.1:
            print("    -> Weak frequency dependence")
        else:
            print("    -> Compatibility is INDEPENDENT of frequency (robust)")

    return results


# ============================================================================
# T3: AZC CROSS-REFERENCE
# ============================================================================

def test_azc_cross_reference(data, single_regime, multi_regime, universal):
    """
    T3: Do REGIME-specific tokens have distinct AZC zone profiles?

    Check if single-REGIME tokens appear in different AZC positions than
    universal tokens.
    """
    print("\n" + "=" * 70)
    print("T3: AZC CROSS-REFERENCE")
    print("Do REGIME-specific tokens have distinct AZC profiles?")
    print("=" * 70)

    results = {'test': 'T3_azc_cross_reference'}

    # Define AZC zone patterns (simplified - first token of line, etc.)
    # Since we don't have direct AZC zone data, we'll use position proxies

    # Group A data by folio and line, tracking token positions
    a_data = [d for d in data if d['currier'] == 'A']

    # Build position profile for each token
    token_positions = defaultdict(list)  # token -> list of positions (1st, 2nd, etc.)

    folio_line_tokens = defaultdict(list)
    for d in a_data:
        key = (d['folio'], d.get('line_number', ''))
        folio_line_tokens[key].append(d['token'])

    for (folio, line), tokens in folio_line_tokens.items():
        for pos, token in enumerate(tokens):
            if pos == 0:
                token_positions[token].append('P1')  # First position (C-zone proxy)
            elif pos == len(tokens) - 1:
                token_positions[token].append('FINAL')  # Final position
            else:
                token_positions[token].append('MIDDLE')  # Middle positions

    # Compare position profiles
    def get_position_profile(tokens):
        positions = Counter()
        for token in tokens:
            for pos in token_positions.get(token, []):
                positions[pos] += 1
        total = sum(positions.values())
        if total > 0:
            return {k: 100 * v / total for k, v in positions.items()}, total
        return {}, 0

    single_pos, single_n = get_position_profile(single_regime.keys())
    partial_pos, partial_n = get_position_profile(multi_regime.keys())
    univ_pos, univ_n = get_position_profile(universal)

    print("\n[1] Position profile by compatibility category:")
    print("-" * 60)
    print(f"    {'Position':<12} {'Single%':<12} {'Partial%':<12} {'Univ%':<12}")
    print("    " + "-" * 45)

    for pos in ['P1', 'MIDDLE', 'FINAL']:
        s_pct = single_pos.get(pos, 0)
        p_pct = partial_pos.get(pos, 0)
        u_pct = univ_pos.get(pos, 0)
        print(f"    {pos:<12} {s_pct:<12.1f} {p_pct:<12.1f} {u_pct:<12.1f}")

    results['position_profiles'] = {
        'single': single_pos, 'partial': partial_pos, 'universal': univ_pos
    }

    # Chi-square test
    print("\n[2] Chi-square test: Position x Compatibility")

    # Build contingency
    contingency = []
    for pos in ['P1', 'MIDDLE', 'FINAL']:
        # Get raw counts
        s_count = sum(1 for t in single_regime.keys() for p in token_positions.get(t, []) if p == pos)
        p_count = sum(1 for t in multi_regime.keys() for p in token_positions.get(t, []) if p == pos)
        u_count = sum(1 for t in universal for p in token_positions.get(t, []) if p == pos)
        contingency.append([s_count, p_count, u_count])

    contingency = np.array(contingency)
    chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
    n = contingency.sum()
    min_dim = min(contingency.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if n * min_dim > 0 else 0

    print(f"    Chi-squared: {chi2:.4f}")
    print(f"    p-value: {p_val:.6f}")
    print(f"    Cramer's V: {cramers_v:.4f}")

    results['position_chi2'] = chi2
    results['position_p_value'] = p_val
    results['position_cramers_v'] = cramers_v

    if p_val < 0.01 and cramers_v > 0.1:
        print("    -> Position profile DIFFERS by compatibility")
    else:
        print("    -> Position profile is UNIFORM across compatibility categories")

    # First-position (C-zone) enrichment test
    print("\n[3] C-zone (first position) enrichment test:")

    single_p1 = sum(1 for t in single_regime.keys() if 'P1' in token_positions.get(t, []))
    single_total = len(single_regime)
    univ_p1 = sum(1 for t in universal if 'P1' in token_positions.get(t, []))
    univ_total = len(universal)

    if single_total > 0 and univ_total > 0:
        single_p1_rate = 100 * single_p1 / single_total
        univ_p1_rate = 100 * univ_p1 / univ_total

        print(f"    Single-REGIME tokens in P1: {single_p1}/{single_total} ({single_p1_rate:.1f}%)")
        print(f"    Universal tokens in P1: {univ_p1}/{univ_total} ({univ_p1_rate:.1f}%)")

        # Fisher's exact test
        contingency_2x2 = [[single_p1, single_total - single_p1],
                          [univ_p1, univ_total - univ_p1]]
        odds_ratio, p_fisher = stats.fisher_exact(contingency_2x2)

        print(f"    Fisher's exact: OR={odds_ratio:.2f}, p={p_fisher:.4f}")

        results['p1_enrichment'] = {
            'single_rate': single_p1_rate, 'universal_rate': univ_p1_rate,
            'odds_ratio': odds_ratio, 'p_value': p_fisher
        }

    return results


# ============================================================================
# T4: FOLIO CLUSTERING
# ============================================================================

def test_folio_clustering(data, single_regime, multi_regime, universal):
    """
    T4: Do REGIME constraints cluster on certain A folios?

    Check if single-REGIME tokens are concentrated on specific A folios.
    """
    print("\n" + "=" * 70)
    print("T4: FOLIO CLUSTERING")
    print("Do REGIME constraints cluster on certain A folios?")
    print("=" * 70)

    results = {'test': 'T4_folio_clustering'}

    # Get A folio list
    a_data = [d for d in data if d['currier'] == 'A']
    a_folios = sorted(set(d['folio'] for d in a_data))

    print(f"\n[1] A folios analyzed: {len(a_folios)}")

    # For each A folio, calculate proportion of single-REGIME tokens
    folio_profiles = {}
    for folio in a_folios:
        folio_tokens = set(d['token'] for d in a_data if d['folio'] == folio)

        single_count = sum(1 for t in folio_tokens if t in single_regime)
        partial_count = sum(1 for t in folio_tokens if t in multi_regime)
        univ_count = sum(1 for t in folio_tokens if t in universal)
        total_in_b = single_count + partial_count + univ_count

        if total_in_b >= 5:  # Only count folios with enough B-shared tokens
            folio_profiles[folio] = {
                'single': single_count,
                'partial': partial_count,
                'universal': univ_count,
                'total': total_in_b,
                'single_pct': 100 * single_count / total_in_b
            }

    # Sort by single-REGIME proportion
    sorted_folios = sorted(folio_profiles.items(), key=lambda x: x[1]['single_pct'], reverse=True)

    print("\n[2] A folios by single-REGIME token proportion:")
    print("-" * 60)
    print(f"    {'Folio':<12} {'Single%':<10} {'Partial%':<10} {'Univ%':<10} {'N':<6}")
    print("    " + "-" * 50)

    # Show top 10 and bottom 10
    folio_data = []
    for folio, profile in sorted_folios[:10]:
        s_pct = profile['single_pct']
        p_pct = 100 * profile['partial'] / profile['total']
        u_pct = 100 * profile['universal'] / profile['total']
        print(f"    {folio:<12} {s_pct:<10.1f} {p_pct:<10.1f} {u_pct:<10.1f} {profile['total']:<6}")
        folio_data.append({'folio': folio, 'single_pct': s_pct, 'n': profile['total']})

    if len(sorted_folios) > 20:
        print("    ...")

    for folio, profile in sorted_folios[-5:]:
        s_pct = profile['single_pct']
        p_pct = 100 * profile['partial'] / profile['total']
        u_pct = 100 * profile['universal'] / profile['total']
        print(f"    {folio:<12} {s_pct:<10.1f} {p_pct:<10.1f} {u_pct:<10.1f} {profile['total']:<6}")
        folio_data.append({'folio': folio, 'single_pct': s_pct, 'n': profile['total']})

    results['folio_profiles'] = folio_data

    # Test for clustering: is variance in single_pct greater than expected?
    single_pcts = [p['single_pct'] for p in folio_profiles.values()]

    print(f"\n[3] Single-REGIME proportion across folios:")
    print(f"    Mean: {np.mean(single_pcts):.1f}%")
    print(f"    Std: {np.std(single_pcts):.1f}%")
    print(f"    Range: {min(single_pcts):.1f}% - {max(single_pcts):.1f}%")

    results['single_pct_stats'] = {
        'mean': np.mean(single_pcts),
        'std': np.std(single_pcts),
        'min': min(single_pcts),
        'max': max(single_pcts)
    }

    # Coefficient of variation
    cv = np.std(single_pcts) / np.mean(single_pcts) if np.mean(single_pcts) > 0 else 0
    print(f"    Coefficient of variation: {cv:.3f}")

    results['coefficient_of_variation'] = cv

    if cv > 0.3:
        print("    -> HIGH variance - REGIME constraints cluster by folio")
    elif cv > 0.15:
        print("    -> MODERATE variance - some clustering")
    else:
        print("    -> LOW variance - REGIME constraints are evenly distributed")

    # Chi-square test: Folio x Compatibility
    print("\n[4] Chi-square test: Folio x Compatibility")

    contingency = []
    for folio, profile in folio_profiles.items():
        if profile['total'] >= 10:
            contingency.append([profile['single'], profile['partial'], profile['universal']])

    if len(contingency) >= 5:
        contingency = np.array(contingency)
        chi2, p_val, dof, expected = stats.chi2_contingency(contingency)
        n = contingency.sum()
        min_dim = min(contingency.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n * min_dim > 0 else 0

        print(f"    Chi-squared: {chi2:.4f}")
        print(f"    Degrees of freedom: {dof}")
        print(f"    p-value: {p_val:.6f}")
        print(f"    Cramer's V: {cramers_v:.4f}")

        results['folio_chi2'] = chi2
        results['folio_p_value'] = p_val
        results['folio_cramers_v'] = cramers_v

        if p_val < 0.01 and cramers_v > 0.15:
            print("    -> Compatibility profile VARIES by folio (clustering)")
        elif p_val < 0.01:
            print("    -> Significant but weak clustering")
        else:
            print("    -> Compatibility profile is UNIFORM across folios")

    return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("A_REGIME_STRATIFICATION PHASE")
    print("Investigating A vocabulary stratification by REGIME compatibility")
    print("=" * 70)

    # Load data
    print("\n[SETUP] Loading data...")
    data = load_transcript_data()
    folio_to_regime = load_regime_mapping()
    token_regimes = get_token_regimes(data, folio_to_regime)

    # Get A vocabulary
    a_tokens = set(d['token'] for d in data if d['currier'] == 'A')
    a_token_freq = Counter(d['token'] for d in data if d['currier'] == 'A')

    print(f"    Total A tokens (types): {len(a_tokens)}")
    print(f"    B folios with REGIME: {len(folio_to_regime)}")

    # Classify tokens
    single_regime, multi_regime, universal, no_b = classify_tokens_by_regime_count(
        a_tokens, token_regimes
    )

    print(f"\n[SETUP] Token classification:")
    print(f"    Single-REGIME: {len(single_regime)} ({100*len(single_regime)/len(a_tokens):.1f}%)")
    print(f"    Partial (2-3): {len(multi_regime)} ({100*len(multi_regime)/len(a_tokens):.1f}%)")
    print(f"    Universal (4): {len(universal)} ({100*len(universal)/len(a_tokens):.1f}%)")
    print(f"    No B presence: {len(no_b)} ({100*len(no_b)/len(a_tokens):.1f}%)")

    # Run all tests
    all_results = {}

    # T1: Morphological Analysis
    all_results['T1'] = test_morphological_prediction(
        single_regime, multi_regime, universal, a_token_freq
    )

    # T2: Frequency Analysis
    all_results['T2'] = test_frequency_distribution(
        single_regime, multi_regime, universal, a_token_freq
    )

    # T3: AZC Cross-Reference
    all_results['T3'] = test_azc_cross_reference(
        data, single_regime, multi_regime, universal
    )

    # T4: Folio Clustering
    all_results['T4'] = test_folio_clustering(
        data, single_regime, multi_regime, universal
    )

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\n[T1] Morphological Analysis:")
    if 'prefix_cramers_v' in all_results['T1']:
        v = all_results['T1']['prefix_cramers_v']
        print(f"    PREFIX predicts compatibility: Cramer's V = {v:.4f}")
    if 'regime_prefix_cramers_v' in all_results['T1']:
        v = all_results['T1']['regime_prefix_cramers_v']
        print(f"    PREFIX predicts specific REGIME: Cramer's V = {v:.4f}")

    print("\n[T2] Frequency Analysis:")
    if 'tier_cramers_v' in all_results['T2']:
        v = all_results['T2']['tier_cramers_v']
        print(f"    Frequency tier x Compatibility: Cramer's V = {v:.4f}")
        if v < 0.15:
            print("    -> Finding is ROBUST to frequency artifacts")
        else:
            print("    -> WARNING: Frequency may confound results")

    print("\n[T3] AZC Cross-Reference:")
    if 'position_cramers_v' in all_results['T3']:
        v = all_results['T3']['position_cramers_v']
        print(f"    Position x Compatibility: Cramer's V = {v:.4f}")

    print("\n[T4] Folio Clustering:")
    if 'coefficient_of_variation' in all_results['T4']:
        cv = all_results['T4']['coefficient_of_variation']
        print(f"    Coefficient of variation: {cv:.3f}")
        if cv > 0.3:
            print("    -> REGIME constraints CLUSTER by A folio")
        else:
            print("    -> REGIME constraints are distributed uniformly")

    # Save results
    output_path = project_root / 'results' / 'regime_stratification_tests.json'
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=float)

    print(f"\n    Results saved to: {output_path}")

    return all_results


if __name__ == '__main__':
    main()
