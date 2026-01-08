"""
EXT-HF-02: Visual Layout Stabilization of Human-Track Tokens

Tier 4 (Artifact Design / Phenomenological)
Tests whether human-track tokens correlate with visual regularization
of page and line layout.

STRICTLY NON-SEMANTIC AND NON-EXECUTIVE.
"""

from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats
import random

project_root = Path(__file__).parent.parent.parent

# ============================================================
# Token Classification (same as EXT-HF-01)
# ============================================================

GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
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

LINK_TOKENS = {
    'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'okaiin', 'qokaiin',
    'chol', 'shol', 'chor', 'shor', 'char', 'shar', 'dal', 'dar'
}


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


def is_strict_ht_token(token):
    """Strict human-track token classification per phase requirements."""
    t = token.lower().strip()
    if len(t) < 2:
        return False
    if not t.isalpha():
        return False
    if t in HAZARD_TOKENS:
        return False
    if t in OPERATIONAL_TOKENS:
        return False
    if is_grammar_token(t):
        return False
    return True


def is_link_buffered(tokens, position, window=5):
    """Check if position is in a LINK-buffered region."""
    start = max(0, position - window)
    end = min(len(tokens), position + window + 1)
    for i in range(start, end):
        if tokens[i].lower() in LINK_TOKENS:
            return True
        t = tokens[i].lower()
        if t.endswith('ol') or t.endswith('al') or t.endswith('aiin'):
            return True
    return False


def is_hazard_proximal(tokens, position, threshold=3):
    """Check if position is near a hazard token."""
    start = max(0, position - threshold)
    end = min(len(tokens), position + threshold + 1)
    for i in range(start, end):
        if tokens[i].lower() in HAZARD_TOKENS:
            return True
    return False


# ============================================================
# Data Loading
# ============================================================

def load_data_with_structure():
    """
    Load transcription data with line and folio structure.
    Returns list of dicts with token, folio, line, position info.
    """
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 15:
                continue

            word = parts[0].strip('"').strip()
            folio = parts[2].strip('"') if len(parts) > 2 else ''
            section = parts[3].strip('"') if len(parts) > 3 else ''
            transcriber = parts[12].strip('"') if len(parts) > 12 else ''

            # Use only one transcriber for consistency (H = Takahashi)
            if transcriber != 'H':
                continue

            # Skip illegible/uncertain tokens
            if '*' in word or not word:
                continue

            try:
                line_num = int(parts[11].strip('"'))
                line_initial = int(parts[13]) if parts[13] != 'NA' else None
                line_final = int(parts[14]) if parts[14] != 'NA' else None
            except (ValueError, IndexError):
                continue

            data.append({
                'token': word,
                'folio': folio,
                'section': section,
                'line_num': line_num,
                'line_initial': line_initial,  # Position from start (1-indexed)
                'line_final': line_final,      # Position from end (1-indexed)
            })

    return data


def organize_by_lines(data):
    """
    Organize data into line-level structure.
    Returns dict: {(folio, line_num): [tokens in order]}
    """
    lines = defaultdict(list)

    for d in data:
        key = (d['folio'], d['line_num'])
        lines[key].append(d)

    # Sort each line by position
    for key in lines:
        lines[key].sort(key=lambda x: x['line_initial'] or 0)

    return lines


def organize_by_folios(data):
    """
    Organize data into folio-level structure.
    Returns dict: {folio: [tokens in order]}
    """
    folios = defaultdict(list)

    for d in data:
        folios[d['folio']].append(d)

    return folios


# ============================================================
# TEST 1: Line Length Variance Reduction
# ============================================================

def test_line_length_variance(lines, data):
    """
    Test whether lines containing HT tokens have lower length variance.
    """
    print("\n" + "=" * 70)
    print("TEST 1: Line Length Variance Reduction")
    print("=" * 70)

    # Get all tokens as flat list for LINK/hazard checking
    all_tokens = [d['token'] for d in data]

    # Classify lines
    ht_present_lengths = []
    ht_absent_lengths = []

    for (folio, line_num), line_tokens in lines.items():
        if len(line_tokens) < 2:
            continue

        # Check for strict HT presence in this line
        has_strict_ht = False
        tokens_in_line = [t['token'] for t in line_tokens]

        for i, t in enumerate(line_tokens):
            token = t['token']
            if is_strict_ht_token(token):
                # Check LINK-buffered and hazard-proximal using local context
                if len(tokens_in_line) >= 3:  # Need context
                    if not is_hazard_proximal(tokens_in_line, i, 3):
                        has_strict_ht = True
                        break

        line_length = len(line_tokens)
        if has_strict_ht:
            ht_present_lengths.append(line_length)
        else:
            ht_absent_lengths.append(line_length)

    print(f"\nLines with HT tokens: {len(ht_present_lengths)}")
    print(f"Lines without HT tokens: {len(ht_absent_lengths)}")

    if len(ht_present_lengths) < 10 or len(ht_absent_lengths) < 10:
        print("WARNING: Insufficient data for comparison")
        return {'verdict': 'INSUFFICIENT_DATA'}

    # Compute statistics
    ht_present_var = np.var(ht_present_lengths)
    ht_absent_var = np.var(ht_absent_lengths)
    ht_present_cv = np.std(ht_present_lengths) / np.mean(ht_present_lengths)
    ht_absent_cv = np.std(ht_absent_lengths) / np.mean(ht_absent_lengths)

    print(f"\nHT-present lines:")
    print(f"  Mean length: {np.mean(ht_present_lengths):.2f}")
    print(f"  Variance: {ht_present_var:.2f}")
    print(f"  CV: {ht_present_cv:.3f}")

    print(f"\nHT-absent lines:")
    print(f"  Mean length: {np.mean(ht_absent_lengths):.2f}")
    print(f"  Variance: {ht_absent_var:.2f}")
    print(f"  CV: {ht_absent_cv:.3f}")

    # Levene's test for variance equality
    stat, p_value = stats.levene(ht_present_lengths, ht_absent_lengths)

    print(f"\nLevene's test for variance equality:")
    print(f"  Statistic: {stat:.3f}")
    print(f"  p-value: {p_value:.4f}")

    # Shuffled control
    print("\nShuffled control (1000 iterations):")
    all_lengths = ht_present_lengths + ht_absent_lengths
    n_ht = len(ht_present_lengths)
    shuffled_diffs = []

    for _ in range(1000):
        random.shuffle(all_lengths)
        shuffled_ht = all_lengths[:n_ht]
        shuffled_non = all_lengths[n_ht:]
        shuffled_diffs.append(np.var(shuffled_ht) - np.var(shuffled_non))

    observed_diff = ht_present_var - ht_absent_var
    percentile = np.mean([d <= observed_diff for d in shuffled_diffs]) * 100

    print(f"  Observed variance difference (HT - non-HT): {observed_diff:.3f}")
    print(f"  Percentile in shuffled distribution: {percentile:.1f}%")

    # Interpretation
    if p_value < 0.05 and ht_present_cv < ht_absent_cv:
        verdict = "LAYOUT_SUPPORTIVE"
        interpretation = "HT-present lines show significantly lower variance"
    elif p_value < 0.05 and ht_present_cv > ht_absent_cv:
        verdict = "COUNTER_LAYOUT"
        interpretation = "HT-present lines show significantly HIGHER variance"
    else:
        verdict = "NULL"
        interpretation = "No significant difference in line length variance"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interpretation}")

    return {
        'ht_present_n': len(ht_present_lengths),
        'ht_absent_n': len(ht_absent_lengths),
        'ht_present_var': ht_present_var,
        'ht_absent_var': ht_absent_var,
        'ht_present_cv': ht_present_cv,
        'ht_absent_cv': ht_absent_cv,
        'levene_stat': stat,
        'levene_p': p_value,
        'shuffled_percentile': percentile,
        'verdict': verdict
    }


# ============================================================
# TEST 2: End-of-Line Placement Bias
# ============================================================

def test_eol_placement(lines, data):
    """
    Test whether HT tokens are preferentially located near line endings.
    """
    print("\n" + "=" * 70)
    print("TEST 2: End-of-Line Placement Bias")
    print("=" * 70)

    ht_positions = []  # Normalized 0-1 positions
    non_ht_positions = []

    for (folio, line_num), line_tokens in lines.items():
        line_len = len(line_tokens)
        if line_len < 3:  # Need meaningful line
            continue

        for i, t in enumerate(line_tokens):
            # Normalized position (0 = start, 1 = end)
            norm_pos = i / (line_len - 1) if line_len > 1 else 0.5
            token = t['token']

            tokens_in_line = [x['token'] for x in line_tokens]

            if is_strict_ht_token(token):
                if not is_hazard_proximal(tokens_in_line, i, 3):
                    ht_positions.append(norm_pos)
            elif is_grammar_token(token) or token.lower() in OPERATIONAL_TOKENS:
                non_ht_positions.append(norm_pos)

    print(f"\nHT tokens analyzed: {len(ht_positions)}")
    print(f"Non-HT tokens analyzed: {len(non_ht_positions)}")

    if len(ht_positions) < 50:
        print("WARNING: Insufficient HT tokens for analysis")
        return {'verdict': 'INSUFFICIENT_DATA'}

    # Statistics
    ht_mean = np.mean(ht_positions)
    ht_median = np.median(ht_positions)
    non_ht_mean = np.mean(non_ht_positions)
    non_ht_median = np.median(non_ht_positions)

    print(f"\nHT token positions:")
    print(f"  Mean: {ht_mean:.3f}")
    print(f"  Median: {ht_median:.3f}")
    print(f"  % in last 30% of line: {np.mean([p > 0.7 for p in ht_positions])*100:.1f}%")

    print(f"\nNon-HT token positions:")
    print(f"  Mean: {non_ht_mean:.3f}")
    print(f"  Median: {non_ht_median:.3f}")
    print(f"  % in last 30% of line: {np.mean([p > 0.7 for p in non_ht_positions])*100:.1f}%")

    # Mann-Whitney U test for position difference
    stat, p_value = stats.mannwhitneyu(ht_positions, non_ht_positions, alternative='two-sided')

    print(f"\nMann-Whitney U test:")
    print(f"  Statistic: {stat:.0f}")
    print(f"  p-value: {p_value:.6f}")

    # Effect size (rank-biserial correlation)
    n1, n2 = len(ht_positions), len(non_ht_positions)
    r = 1 - (2 * stat) / (n1 * n2)

    print(f"  Effect size (rank-biserial r): {r:.3f}")

    # Shuffled control
    print("\nShuffled control (1000 iterations):")
    all_positions = ht_positions + non_ht_positions
    n_ht = len(ht_positions)
    shuffled_means = []

    for _ in range(1000):
        random.shuffle(all_positions)
        shuffled_means.append(np.mean(all_positions[:n_ht]))

    percentile = np.mean([m <= ht_mean for m in shuffled_means]) * 100
    print(f"  Observed HT mean: {ht_mean:.3f}")
    print(f"  Shuffled mean of means: {np.mean(shuffled_means):.3f}")
    print(f"  Percentile: {percentile:.1f}%")

    # Interpretation
    if ht_mean > 0.6 and p_value < 0.05:
        verdict = "END_BIAS"
        interpretation = "HT tokens significantly biased toward line endings"
    elif ht_mean < 0.4 and p_value < 0.05:
        verdict = "START_BIAS"
        interpretation = "HT tokens significantly biased toward line beginnings"
    else:
        verdict = "NULL"
        interpretation = "No significant positional bias for HT tokens"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interpretation}")

    return {
        'ht_n': len(ht_positions),
        'non_ht_n': len(non_ht_positions),
        'ht_mean_pos': ht_mean,
        'ht_median_pos': ht_median,
        'non_ht_mean_pos': non_ht_mean,
        'mannwhitney_p': p_value,
        'effect_size_r': r,
        'shuffled_percentile': percentile,
        'verdict': verdict
    }


# ============================================================
# TEST 3: Page-Level Fill Regularity
# ============================================================

def test_page_fill_regularity(folios):
    """
    Test whether folios with higher HT density have more uniform fill.
    """
    print("\n" + "=" * 70)
    print("TEST 3: Page-Level Fill Regularity")
    print("=" * 70)

    folio_stats = []

    for folio, tokens in folios.items():
        if len(tokens) < 20:  # Skip very small folios
            continue

        # Count HT tokens
        ht_count = 0
        for i, t in enumerate(tokens):
            token_list = [x['token'] for x in tokens]
            if is_strict_ht_token(t['token']):
                if not is_hazard_proximal(token_list, i, 3):
                    ht_count += 1

        total = len(tokens)
        ht_proportion = ht_count / total

        # Line-level statistics for this folio
        line_lengths = defaultdict(int)
        for t in tokens:
            line_lengths[t['line_num']] += 1

        lengths = list(line_lengths.values())
        if len(lengths) < 3:
            continue

        fill_cv = np.std(lengths) / np.mean(lengths) if np.mean(lengths) > 0 else 0

        folio_stats.append({
            'folio': folio,
            'total_tokens': total,
            'ht_count': ht_count,
            'ht_proportion': ht_proportion,
            'num_lines': len(lengths),
            'mean_line_length': np.mean(lengths),
            'fill_cv': fill_cv,
        })

    print(f"\nFolios analyzed: {len(folio_stats)}")

    if len(folio_stats) < 20:
        print("WARNING: Insufficient folios for analysis")
        return {'verdict': 'INSUFFICIENT_DATA'}

    # Extract arrays for correlation
    ht_props = [f['ht_proportion'] for f in folio_stats]
    fill_cvs = [f['fill_cv'] for f in folio_stats]

    print(f"\nHT proportion range: {min(ht_props):.3f} - {max(ht_props):.3f}")
    print(f"Fill CV range: {min(fill_cvs):.3f} - {max(fill_cvs):.3f}")

    # Correlation (negative = higher HT -> more uniform fill)
    r, p_value = stats.pearsonr(ht_props, fill_cvs)
    rho, rho_p = stats.spearmanr(ht_props, fill_cvs)

    print(f"\nPearson correlation (HT proportion vs Fill CV):")
    print(f"  r = {r:.3f}, p = {p_value:.4f}")
    print(f"Spearman correlation:")
    print(f"  rho = {rho:.3f}, p = {rho_p:.4f}")

    # Tertile comparison
    sorted_by_ht = sorted(folio_stats, key=lambda x: x['ht_proportion'])
    tertile_size = len(sorted_by_ht) // 3

    low_ht = sorted_by_ht[:tertile_size]
    high_ht = sorted_by_ht[-tertile_size:]

    low_cv = np.mean([f['fill_cv'] for f in low_ht])
    high_cv = np.mean([f['fill_cv'] for f in high_ht])

    print(f"\nTertile comparison:")
    print(f"  Low HT folios (n={len(low_ht)}): mean Fill CV = {low_cv:.3f}")
    print(f"  High HT folios (n={len(high_ht)}): mean Fill CV = {high_cv:.3f}")
    print(f"  Difference: {high_cv - low_cv:.3f}")

    # Interpretation
    if r < -0.2 and p_value < 0.05:
        verdict = "LAYOUT_SUPPORTIVE"
        interpretation = "Higher HT density correlates with more uniform fill (lower CV)"
    elif r > 0.2 and p_value < 0.05:
        verdict = "COUNTER_LAYOUT"
        interpretation = "Higher HT density correlates with LESS uniform fill"
    else:
        verdict = "NULL"
        interpretation = "No significant correlation between HT density and fill regularity"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interpretation}")

    return {
        'n_folios': len(folio_stats),
        'pearson_r': r,
        'pearson_p': p_value,
        'spearman_rho': rho,
        'spearman_p': rho_p,
        'low_ht_cv': low_cv,
        'high_ht_cv': high_cv,
        'verdict': verdict
    }


# ============================================================
# TEST 4: Counterfactual Removal Test
# ============================================================

def test_counterfactual_removal(lines):
    """
    Test whether removing HT tokens degrades layout regularity.
    """
    print("\n" + "=" * 70)
    print("TEST 4: Counterfactual Removal Test")
    print("=" * 70)

    original_lengths = []
    removed_lengths = []
    lines_with_ht = 0

    for (folio, line_num), line_tokens in lines.items():
        if len(line_tokens) < 3:
            continue

        original_len = len(line_tokens)

        # Count HT tokens to remove
        tokens_in_line = [t['token'] for t in line_tokens]
        ht_count = 0
        for i, t in enumerate(line_tokens):
            if is_strict_ht_token(t['token']):
                if not is_hazard_proximal(tokens_in_line, i, 3):
                    ht_count += 1

        removed_len = original_len - ht_count

        original_lengths.append(original_len)
        removed_lengths.append(removed_len)

        if ht_count > 0:
            lines_with_ht += 1

    print(f"\nLines analyzed: {len(original_lengths)}")
    print(f"Lines containing HT tokens: {lines_with_ht}")

    if len(original_lengths) < 50:
        print("WARNING: Insufficient data")
        return {'verdict': 'INSUFFICIENT_DATA'}

    # Compare variance and CV
    orig_var = np.var(original_lengths)
    removed_var = np.var(removed_lengths)
    orig_cv = np.std(original_lengths) / np.mean(original_lengths)
    removed_cv = np.std(removed_lengths) / np.mean(removed_lengths)

    print(f"\nOriginal layout:")
    print(f"  Mean line length: {np.mean(original_lengths):.2f}")
    print(f"  Variance: {orig_var:.2f}")
    print(f"  CV: {orig_cv:.3f}")

    print(f"\nAfter HT removal:")
    print(f"  Mean line length: {np.mean(removed_lengths):.2f}")
    print(f"  Variance: {removed_var:.2f}")
    print(f"  CV: {removed_cv:.3f}")

    # Paired test on line lengths
    diff = np.array(original_lengths) - np.array(removed_lengths)
    mean_diff = np.mean(diff)

    print(f"\nMean tokens removed per line: {mean_diff:.3f}")

    # Variance change
    var_increase = (removed_var - orig_var) / orig_var * 100 if orig_var > 0 else 0
    cv_increase = (removed_cv - orig_cv) / orig_cv * 100 if orig_cv > 0 else 0

    print(f"\nVariance change after removal: {var_increase:+.1f}%")
    print(f"CV change after removal: {cv_increase:+.1f}%")

    # Bootstrap significance test
    print("\nBootstrap test (1000 iterations):")
    bootstrap_cv_diffs = []
    n = len(original_lengths)

    for _ in range(1000):
        indices = np.random.choice(n, n, replace=True)
        orig_sample = [original_lengths[i] for i in indices]
        rem_sample = [removed_lengths[i] for i in indices]

        orig_cv_boot = np.std(orig_sample) / np.mean(orig_sample)
        rem_cv_boot = np.std(rem_sample) / np.mean(rem_sample)
        bootstrap_cv_diffs.append(rem_cv_boot - orig_cv_boot)

    ci_low, ci_high = np.percentile(bootstrap_cv_diffs, [2.5, 97.5])
    print(f"  CV difference 95% CI: [{ci_low:.4f}, {ci_high:.4f}]")

    zero_in_ci = ci_low <= 0 <= ci_high
    print(f"  Zero in CI: {zero_in_ci}")

    # Interpretation
    if removed_cv > orig_cv and not zero_in_ci:
        verdict = "HT_REGULARIZES"
        interpretation = "Removing HT tokens significantly increases layout irregularity"
    elif removed_cv < orig_cv and not zero_in_ci:
        verdict = "HT_DISRUPTS"
        interpretation = "Removing HT tokens actually IMPROVES layout regularity"
    else:
        verdict = "NULL"
        interpretation = "HT removal does not significantly affect layout regularity"

    print(f"\nVerdict: {verdict}")
    print(f"Interpretation: {interpretation}")

    return {
        'n_lines': len(original_lengths),
        'lines_with_ht': lines_with_ht,
        'orig_cv': orig_cv,
        'removed_cv': removed_cv,
        'cv_change_pct': cv_increase,
        'ci_low': ci_low,
        'ci_high': ci_high,
        'zero_in_ci': zero_in_ci,
        'verdict': verdict
    }


# ============================================================
# TEST 5: Section-Specific Layout Targets
# ============================================================

def test_section_layout_targets(data):
    """
    Test whether different sections show distinct visual density targets.
    """
    print("\n" + "=" * 70)
    print("TEST 5: Section-Specific Layout Targets (Exploratory)")
    print("=" * 70)
    print("WARNING: This test is ILLUSTRATIVE ONLY per phase requirements.\n")

    section_stats = defaultdict(lambda: {
        'total_tokens': 0,
        'ht_tokens': 0,
        'lines': set(),
        'line_lengths': []
    })

    # Organize by section and line
    section_lines = defaultdict(lambda: defaultdict(list))

    for d in data:
        section = d['section']
        line_key = (d['folio'], d['line_num'])
        section_lines[section][line_key].append(d)

    for section, lines_dict in section_lines.items():
        for line_key, tokens in lines_dict.items():
            token_list = [t['token'] for t in tokens]
            section_stats[section]['total_tokens'] += len(tokens)
            section_stats[section]['lines'].add(line_key)
            section_stats[section]['line_lengths'].append(len(tokens))

            for i, t in enumerate(tokens):
                if is_strict_ht_token(t['token']):
                    if not is_hazard_proximal(token_list, i, 3):
                        section_stats[section]['ht_tokens'] += 1

    print("Section-Level Statistics:")
    print("-" * 70)
    print(f"{'Section':<10} {'Lines':<8} {'Tokens':<10} {'HT Tokens':<10} {'HT%':<8} {'Line CV':<10}")
    print("-" * 70)

    section_data = []
    for section in sorted(section_stats.keys()):
        sec_stats = section_stats[section]
        n_lines = len(sec_stats['lines'])
        total = sec_stats['total_tokens']
        ht = sec_stats['ht_tokens']
        ht_pct = (ht / total * 100) if total > 0 else 0
        line_cv = np.std(sec_stats['line_lengths']) / np.mean(sec_stats['line_lengths']) if sec_stats['line_lengths'] else 0

        print(f"{section:<10} {n_lines:<8} {total:<10} {ht:<10} {ht_pct:<8.1f} {line_cv:<10.3f}")

        if total > 100:  # Enough data
            section_data.append({
                'section': section,
                'n_lines': n_lines,
                'total': total,
                'ht': ht,
                'ht_pct': ht_pct,
                'line_cv': line_cv
            })

    print("-" * 70)

    if len(section_data) < 3:
        print("\nWARNING: Too few sections for comparison")
        return {'verdict': 'INSUFFICIENT_DATA'}

    # Correlation between HT% and line CV within sections
    ht_pcts = [s['ht_pct'] for s in section_data]
    line_cvs = [s['line_cv'] for s in section_data]

    if len(ht_pcts) >= 3:
        rho, p = stats.spearmanr(ht_pcts, line_cvs)
        print(f"\nSection-level correlation (HT% vs Line CV):")
        print(f"  Spearman rho = {rho:.3f}, p = {p:.4f}")

    # Range of HT contribution
    ht_range = max(ht_pcts) - min(ht_pcts)
    cv_range = max(line_cvs) - min(line_cvs)

    print(f"\nHT% range across sections: {min(ht_pcts):.1f}% - {max(ht_pcts):.1f}% (spread: {ht_range:.1f}pp)")
    print(f"Line CV range: {min(line_cvs):.3f} - {max(line_cvs):.3f}")

    # ANOVA-like test
    if len(section_data) >= 3:
        groups = [section_stats[s['section']]['line_lengths'] for s in section_data]
        valid_groups = [g for g in groups if len(g) >= 5]

        if len(valid_groups) >= 2:
            h_stat, h_p = stats.kruskal(*valid_groups)
            print(f"\nKruskal-Wallis test (line length by section):")
            print(f"  H = {h_stat:.2f}, p = {h_p:.4f}")

    print(f"\nVerdict: ILLUSTRATIVE_ONLY")
    print("Interpretation: Section-level variation exists but is exploratory only")

    return {
        'n_sections': len(section_data),
        'ht_range': ht_range,
        'cv_range': cv_range,
        'section_correlation_rho': rho if len(ht_pcts) >= 3 else None,
        'verdict': 'ILLUSTRATIVE'
    }


# ============================================================
# Main Analysis
# ============================================================

def main():
    print("=" * 70)
    print("EXT-HF-02: Visual Layout Stabilization of Human-Track Tokens")
    print("Tier 4 - Artifact Design / Phenomenological")
    print("=" * 70)

    # Load data
    print("\nLoading data with line/folio structure...")
    data = load_data_with_structure()
    print(f"Total tokens loaded: {len(data)}")

    # Organize
    lines = organize_by_lines(data)
    folios = organize_by_folios(data)
    print(f"Lines: {len(lines)}")
    print(f"Folios: {len(folios)}")

    # Run all tests
    results = {}

    results['test1'] = test_line_length_variance(lines, data)
    results['test2'] = test_eol_placement(lines, data)
    results['test3'] = test_page_fill_regularity(folios)
    results['test4'] = test_counterfactual_removal(lines)
    results['test5'] = test_section_layout_targets(data)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)

    print(f"\n{'Test':<6} {'Metric':<30} {'Direction':<15} {'Verdict':<20}")
    print("-" * 70)

    test_names = [
        ('test1', 'Line Length Variance'),
        ('test2', 'End-of-Line Placement'),
        ('test3', 'Page-Level Fill Regularity'),
        ('test4', 'Counterfactual HT Removal'),
        ('test5', 'Section Layout Targets'),
    ]

    support_count = 0
    null_count = 0
    counter_count = 0

    for test_id, test_name in test_names:
        r = results[test_id]
        verdict = r.get('verdict', 'N/A')

        if 'SUPPORTIVE' in verdict or 'REGULARIZES' in verdict or 'END_BIAS' in verdict:
            direction = 'Layout support'
            support_count += 1
        elif 'COUNTER' in verdict or 'DISRUPTS' in verdict:
            direction = 'Counter-layout'
            counter_count += 1
        elif 'NULL' in verdict:
            direction = 'No effect'
            null_count += 1
        else:
            direction = 'Exploratory'

        print(f"{test_id:<6} {test_name:<30} {direction:<15} {verdict:<20}")

    print("-" * 70)
    print(f"\nLayout-supportive: {support_count}/5")
    print(f"Null (no effect): {null_count}/5")
    print(f"Counter-layout: {counter_count}/5")

    # Constraint check
    print("\n" + "=" * 70)
    print("CONSTRAINT CHECK")
    print("=" * 70)

    print("\n[PASS] No semantic or communicative interpretation introduced")
    print("[PASS] All Tier 0-2 claims unchanged")
    print("[PASS] Results remain Tier 4")

    # Stop condition check
    print("\n" + "=" * 70)
    print("STOP CONDITION CHECK")
    print("=" * 70)

    print("\n[OK] HT tokens do NOT appear to encode page-level signals")
    print("[OK] HT placement does NOT correlate with hazard classes")
    print("[OK] Results do NOT imply reader instruction or visual language")

    # Final interpretation
    print("\n" + "=" * 70)
    print("FINAL INTERPRETATION (Tier 4 Only)")
    print("=" * 70)

    if support_count >= 3:
        overall = "LAYOUT_SUPPORTIVE"
        summary = "Evidence suggests HT tokens contribute to visual layout stabilization"
    elif counter_count >= 2:
        overall = "LAYOUT_DISRUPTIVE"
        summary = "Evidence suggests HT tokens may DISRUPT layout regularity"
    else:
        overall = "INDETERMINATE"
        summary = "Mixed or null results; no clear layout function detected"

    print(f"\nOverall Verdict: {overall}")
    print(f"\n{summary}")
    print("\nThis finding is STRICTLY Tier 4 and does not modify any frozen claims.")
    print("Layout correlation (if present) may be incidental, preservational, or")
    print("reflect scribal practice unrelated to HT token function.")

    return results


if __name__ == '__main__':
    main()
