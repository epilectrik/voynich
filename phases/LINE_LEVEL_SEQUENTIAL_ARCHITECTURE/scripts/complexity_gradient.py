"""
Phase 623: LINE_LEVEL_SEQUENTIAL_ARCHITECTURE -- Script 3: Complexity Gradient

9-feature complexity gradient across paragraph body lines.
Extends C1782 (specification compression), C1574 (headless), C1206 (kernel).

Features computed per body line:
  1. mod_density        -- mean modifier length per token
  2. mod_entropy        -- H(char distribution of modifier chars in line)
  3. headless_rate      -- fraction of headless tokens
  4. compound_rate      -- fraction of compound tokens
  5. mean_middle_len    -- mean MIDDLE length
  6. atom_diversity     -- distinct atom chars in MIDDLEs / line token count
  7. distinct_frames    -- distinct (head, term) pairs / line token count
  8. atom_variance      -- std dev of per-token MIDDLE char entropies
  9. cond_entropy_rate  -- H(category_t | category_{t-1}) over consecutive pairs
"""
import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from phases.LINE_LEVEL_SEQUENTIAL_ARCHITECTURE.scripts.shared import (
    build_corpus, extract_line_features, compute_folio_prefix_dists,
    CHANNEL_NAMES, RESULTS_DIR, round_floats, CATEGORIES,
)


# ============================================================
# Statistical helpers
# ============================================================

def _rank(values):
    """Assign ranks to values (average rank for ties)."""
    n = len(values)
    indexed = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n - 1 and values[indexed[j + 1]] == values[indexed[j]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0  # 1-based average rank
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def compute_spearman_rho(x, y):
    """Compute Spearman rank correlation coefficient."""
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    rx = _rank(x)
    ry = _rank(y)
    n = len(x)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    std_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    std_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if std_x == 0 or std_y == 0:
        return 0.0
    return cov / (std_x * std_y)


def _partial_spearman(feature_vals, position_vals, length_vals):
    """
    Partial Spearman correlation between feature and position,
    controlling for line length.

    Uses rank-based partial correlation:
      r_xy.z = (r_xy - r_xz * r_yz) / sqrt((1 - r_xz^2)(1 - r_yz^2))
    """
    r_fp = compute_spearman_rho(feature_vals, position_vals)
    r_fl = compute_spearman_rho(feature_vals, length_vals)
    r_pl = compute_spearman_rho(position_vals, length_vals)

    denom = math.sqrt(max(0, (1 - r_fl ** 2)) * max(0, (1 - r_pl ** 2)))
    if denom < 1e-12:
        return 0.0
    return (r_fp - r_fl * r_pl) / denom


def wilcoxon_signed_rank(values):
    """
    One-sample Wilcoxon signed-rank test (H0: median = 0).

    Returns (W_statistic, p_value_approx).
    Uses normal approximation for n >= 10, exact sign-test fallback otherwise.
    """
    # Remove zeros
    nonzero = [v for v in values if v != 0.0]
    n = len(nonzero)
    if n < 3:
        return (0.0, 1.0)

    # Rank absolute values
    abs_vals = [abs(v) for v in nonzero]
    ranks = _rank(abs_vals)

    # Sum of positive ranks and negative ranks
    w_plus = sum(ranks[i] for i in range(n) if nonzero[i] > 0)
    w_minus = sum(ranks[i] for i in range(n) if nonzero[i] < 0)
    W = min(w_plus, w_minus)

    if n < 10:
        # Sign test fallback for very small samples
        n_pos = sum(1 for v in nonzero if v > 0)
        # Two-sided p-value from sign test (binomial under H0: p=0.5)
        p_value = 0.0
        for k in range(min(n_pos, n - n_pos) + 1):
            # C(n,k) * 0.5^n
            p_value += _binom_coeff(n, k) * (0.5 ** n)
        p_value *= 2  # two-sided
        p_value = min(p_value, 1.0)
        return (W, p_value)

    # Normal approximation
    mean_W = n * (n + 1) / 4.0
    var_W = n * (n + 1) * (2 * n + 1) / 24.0
    if var_W <= 0:
        return (W, 1.0)
    z = (W - mean_W) / math.sqrt(var_W)
    # Two-sided p-value from normal approximation
    p_value = 2.0 * _normal_cdf(-abs(z))
    return (W, p_value)


def _binom_coeff(n, k):
    """Binomial coefficient C(n, k)."""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def _normal_cdf(z):
    """Approximation of standard normal CDF using Abramowitz & Stegun."""
    if z < -8.0:
        return 0.0
    if z > 8.0:
        return 1.0
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1.0
    if z < 0:
        sign = -1.0
    z_abs = abs(z) / math.sqrt(2.0)
    t = 1.0 / (1.0 + p * z_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs)
    return 0.5 * (1.0 + sign * y)


def _one_way_anova_f(groups):
    """
    One-way ANOVA F-statistic and approximate p-value.
    groups: list of lists of values.
    Returns (F, p_approx). Uses F-distribution normal approximation.
    """
    groups = [g for g in groups if len(g) >= 2]
    k = len(groups)
    if k < 2:
        return (0.0, 1.0)

    all_vals = [v for g in groups for v in g]
    N = len(all_vals)
    if N <= k:
        return (0.0, 1.0)

    grand_mean = sum(all_vals) / N

    # Between-group sum of squares
    ss_between = sum(len(g) * (sum(g) / len(g) - grand_mean) ** 2 for g in groups)
    # Within-group sum of squares
    ss_within = sum(sum((v - sum(g) / len(g)) ** 2 for v in g) for g in groups)

    df_between = k - 1
    df_within = N - k

    if df_within <= 0 or ss_within == 0:
        return (0.0, 1.0)

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    F = ms_between / ms_within

    # Approximate p-value using normal approximation of log(F)
    # For large df_within this is reasonable
    # More accurate: use the F-distribution survival function
    # Fallback: use a rough chi-squared approximation
    # p ~ P(chi2(df_between) > df_between * F * df_within / (df_within + df_between * F))
    # Simplified: use the relationship F ~ chi2/df for large df_within
    chi2_approx = F * df_between
    p_value = _chi2_survival(chi2_approx, df_between)
    return (F, p_value)


def _chi2_survival(x, df):
    """Approximate survival function for chi-squared distribution."""
    if df <= 0 or x <= 0:
        return 1.0
    # Use Wilson-Hilferty normal approximation
    z = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return 1.0 - _normal_cdf(z)


# ============================================================
# Feature computation helpers
# ============================================================

def _char_entropy(chars):
    """Shannon entropy of character distribution in bits."""
    if not chars:
        return 0.0
    counts = Counter(chars)
    total = sum(counts.values())
    if total <= 1:
        return 0.0
    H = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            H -= p * math.log2(p)
    return H


def _token_middle_entropy(middle):
    """Shannon entropy of character distribution in a single MIDDLE."""
    if not middle:
        return 0.0
    return _char_entropy(list(middle))


def _conditional_entropy(categories):
    """
    Compute H(category_t | category_{t-1}) from a sequence of categories.

    Uses the empirical conditional distribution over consecutive pairs.
    H(Y|X) = -sum_x P(x) sum_y P(y|x) log2 P(y|x)
    """
    if len(categories) < 2:
        return 0.0

    # Count transitions
    pair_counts = Counter()
    prev_counts = Counter()
    for i in range(len(categories) - 1):
        prev = categories[i]
        curr = categories[i + 1]
        pair_counts[(prev, curr)] += 1
        prev_counts[prev] += 1

    total_pairs = sum(pair_counts.values())
    if total_pairs == 0:
        return 0.0

    H = 0.0
    for (prev, curr), count in pair_counts.items():
        p_joint = count / total_pairs
        p_cond = count / prev_counts[prev]  # P(curr | prev)
        if p_cond > 0:
            H -= p_joint * math.log2(p_cond)
    return H


# ============================================================
# Block 1: Per-line complexity features
# ============================================================

FEATURE_NAMES = [
    'mod_density', 'mod_entropy', 'headless_rate', 'compound_rate',
    'mean_middle_len', 'atom_diversity', 'distinct_frames',
    'atom_variance', 'cond_entropy_rate',
]


def compute_line_complexity_features(line_dict):
    """
    Compute the 9 complexity features for a single body line.

    Returns dict: feature_name -> float value.
    """
    tokens = line_dict['tokens']
    n = len(tokens)
    if n == 0:
        return {f: 0.0 for f in FEATURE_NAMES}

    # 1. Modifier density: mean len(mods) across tokens
    mod_density = sum(len(t['mods']) for t in tokens) / n

    # 2. Modifier entropy: H(char distribution of all mod chars in line)
    all_mod_chars = []
    for t in tokens:
        all_mod_chars.extend(list(t['mods']))
    mod_entropy = _char_entropy(all_mod_chars)

    # 3. Headless rate
    headless_rate = sum(1 for t in tokens if t['is_headless']) / n

    # 4. Compound rate
    compound_rate = sum(1 for t in tokens if t['is_compound']) / n

    # 5. Mean MIDDLE length
    mean_middle_len = sum(len(t['middle']) for t in tokens) / n

    # 6. Atom diversity: distinct atom chars in all MIDDLEs / line length
    all_middle_chars = set()
    for t in tokens:
        all_middle_chars.update(set(t['middle']))
    atom_diversity = len(all_middle_chars) / n

    # 7. Distinct frames: distinct (head, term) pairs / line length
    frames = set()
    for t in tokens:
        frames.add((t['head'], t['term']))
    distinct_frames = len(frames) / n

    # 8. Within-line atom variance: std dev of per-token MIDDLE char entropies
    per_token_entropies = [_token_middle_entropy(t['middle']) for t in tokens]
    if n >= 2:
        mean_ent = sum(per_token_entropies) / n
        var_ent = sum((e - mean_ent) ** 2 for e in per_token_entropies) / n
        atom_variance = math.sqrt(var_ent)
    else:
        atom_variance = 0.0

    # 9. Conditional entropy rate: H(category_t | category_{t-1})
    categories = [t['category'] for t in tokens]
    cond_entropy_rate = _conditional_entropy(categories)

    return {
        'mod_density': mod_density,
        'mod_entropy': mod_entropy,
        'headless_rate': headless_rate,
        'compound_rate': compound_rate,
        'mean_middle_len': mean_middle_len,
        'atom_diversity': atom_diversity,
        'distinct_frames': distinct_frames,
        'atom_variance': atom_variance,
        'cond_entropy_rate': cond_entropy_rate,
    }


# ============================================================
# Block 2: Per-paragraph slopes
# ============================================================

MIN_BODY_LINES = 5  # Minimum body lines for gradient analysis


def compute_paragraph_slopes(corpus):
    """
    For each paragraph with >= MIN_BODY_LINES body lines:
      - Compute 9 features per body line
      - Compute Spearman rho(feature, position) for each feature
      - Also record line lengths for length control

    Returns list of dicts, one per qualifying paragraph.
    """
    paragraphs_data = []

    for folio, fdata in sorted(corpus.items()):
        section = fdata['section']
        for para in fdata['paragraphs']:
            body = para['body_lines']
            n_body = len(body)
            if n_body < MIN_BODY_LINES:
                continue

            # Compute features per body line
            positions = []
            lengths = []
            feature_vectors = {f: [] for f in FEATURE_NAMES}

            for idx, line_dict in enumerate(body):
                pos = idx / (n_body - 1) if n_body > 1 else 0.0
                positions.append(pos)
                lengths.append(line_dict['length'])

                feats = compute_line_complexity_features(line_dict)
                for f in FEATURE_NAMES:
                    feature_vectors[f].append(feats[f])

            # Compute Spearman rho per feature
            slopes = {}
            partial_slopes = {}
            for f in FEATURE_NAMES:
                rho = compute_spearman_rho(feature_vectors[f], positions)
                slopes[f] = rho
                # Length-controlled partial Spearman
                partial_rho = _partial_spearman(feature_vectors[f], positions, lengths)
                partial_slopes[f] = partial_rho

            paragraphs_data.append({
                'folio': folio,
                'para_id': para['id'],
                'section': section,
                'n_body_lines': n_body,
                'slopes': slopes,
                'partial_slopes': partial_slopes,
            })

    return paragraphs_data


# ============================================================
# Block 3: Statistical tests
# ============================================================

def run_feature_tests(paragraphs_data):
    """
    For each feature:
      - Collect per-paragraph slopes
      - One-sample Wilcoxon test (slopes != 0)
      - Length-controlled partial slopes + Wilcoxon
      - Return summary dict
    """
    results = {}

    for f in FEATURE_NAMES:
        slopes = [p['slopes'][f] for p in paragraphs_data]
        partial_slopes = [p['partial_slopes'][f] for p in paragraphs_data]

        n = len(slopes)
        mean_slope = sum(slopes) / n if n > 0 else 0.0
        sorted_slopes = sorted(slopes)
        median_slope = sorted_slopes[n // 2] if n > 0 else 0.0

        W, p_value = wilcoxon_signed_rank(slopes)

        # Length-controlled
        mean_partial = sum(partial_slopes) / n if n > 0 else 0.0
        W_lc, p_lc = wilcoxon_signed_rank(partial_slopes)

        results[f] = {
            'mean_slope': mean_slope,
            'median_slope': median_slope,
            'wilcoxon_W': W,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'length_controlled_rho': mean_partial,
            'length_controlled_p': p_lc,
            'survives_length_control': p_lc < 0.05,
        }

    return results


# ============================================================
# Block 4: Kernel gradient novelty
# ============================================================

def compute_kernel_gradient(corpus, paragraphs_data):
    """
    Beyond C1206: kernel (k, h, e) fraction gradients.
    - Compute per-paragraph slopes for k_frac, h_frac, e_frac
    - ANOVA: do slopes differ by section?
    - Threshold test: short (3-4 lines) vs long (6+) paragraphs
    """
    # We need to compute kernel slopes for ALL paragraphs with 3+ body lines
    # (broader than the 5+ threshold used for the main analysis)
    kernel_features = ['k_frac', 'h_frac', 'e_frac']
    all_para_kernel = []

    for folio, fdata in sorted(corpus.items()):
        section = fdata['section']
        for para in fdata['paragraphs']:
            body = para['body_lines']
            n_body = len(body)
            if n_body < 3:
                continue

            positions = []
            kf_vals, hf_vals, ef_vals = [], [], []

            for idx, line_dict in enumerate(body):
                pos = idx / (n_body - 1) if n_body > 1 else 0.0
                positions.append(pos)

                tokens = line_dict['tokens']
                n_tok = len(tokens)
                if n_tok == 0:
                    kf_vals.append(0.0)
                    hf_vals.append(0.0)
                    ef_vals.append(0.0)
                    continue

                k_count = sum(1 for t in tokens for c in t['kernels'] if c == 'k')
                h_count = sum(1 for t in tokens for c in t['kernels'] if c == 'h')
                e_count = sum(1 for t in tokens for c in t['kernels'] if c == 'e')
                khe_total = k_count + h_count + e_count
                kf_vals.append(k_count / khe_total if khe_total > 0 else 0.0)
                hf_vals.append(h_count / khe_total if khe_total > 0 else 0.0)
                ef_vals.append(e_count / khe_total if khe_total > 0 else 0.0)

            k_slope = compute_spearman_rho(kf_vals, positions)
            h_slope = compute_spearman_rho(hf_vals, positions)
            e_slope = compute_spearman_rho(ef_vals, positions)

            all_para_kernel.append({
                'folio': folio,
                'section': section,
                'n_body_lines': n_body,
                'k_slope': k_slope,
                'h_slope': h_slope,
                'e_slope': e_slope,
            })

    # Overall mean slopes
    result = {}
    for kf in kernel_features:
        slope_key = kf.replace('_frac', '_slope')
        slopes = [p[slope_key] for p in all_para_kernel]
        n = len(slopes)
        mean_slope = sum(slopes) / n if n > 0 else 0.0

        # ANOVA by section
        section_groups = defaultdict(list)
        for p in all_para_kernel:
            section_groups[p['section']].append(p[slope_key])
        groups = [v for v in section_groups.values() if len(v) >= 2]
        F, p_anova = _one_way_anova_f(groups)

        result[kf] = {
            'mean_slope': mean_slope,
            'n_paragraphs': n,
            'section_anova_F': F,
            'section_anova_p': p_anova,
        }

    # Threshold test: short (3-4) vs long (6+)
    short = [p for p in all_para_kernel if 3 <= p['n_body_lines'] <= 4]
    long = [p for p in all_para_kernel if p['n_body_lines'] >= 6]

    short_para_signal = {}
    for length_label, group in [('3_4_lines', short), ('6_plus', long)]:
        entry = {'n': len(group)}
        for kf in kernel_features:
            slope_key = kf.replace('_frac', '_slope')
            slopes = [p[slope_key] for p in group]
            if slopes:
                entry[f'{kf.replace("_frac", "")}_slope'] = sum(slopes) / len(slopes)
                _, p_val = wilcoxon_signed_rank(slopes)
                entry[f'{kf.replace("_frac", "")}_p'] = p_val
            else:
                entry[f'{kf.replace("_frac", "")}_slope'] = 0.0
                entry[f'{kf.replace("_frac", "")}_p'] = 1.0
        short_para_signal[length_label] = entry

    result['short_para_signal'] = short_para_signal
    return result


# ============================================================
# Block 5: Section stratification
# ============================================================

def section_stratification(paragraphs_data):
    """
    Repeat feature gradient tests per section.
    Returns dict: feature -> section -> {mean_slope, n, p_value}.
    """
    # Group paragraphs by section
    by_section = defaultdict(list)
    for p in paragraphs_data:
        by_section[p['section']].append(p)

    section_results = {}
    for f in FEATURE_NAMES:
        section_results[f] = {}
        for sec in sorted(by_section.keys()):
            paras = by_section[sec]
            slopes = [p['slopes'][f] for p in paras]
            n = len(slopes)
            if n < 3:
                section_results[f][sec] = {
                    'mean_slope': sum(slopes) / n if n > 0 else 0.0,
                    'n': n,
                    'p_value': 1.0,
                }
                continue
            mean_s = sum(slopes) / n
            _, p_val = wilcoxon_signed_rank(slopes)
            section_results[f][sec] = {
                'mean_slope': mean_s,
                'n': n,
                'p_value': p_val,
            }

    return section_results


# ============================================================
# Block 6: Verdict
# ============================================================

def determine_verdict(feature_results):
    """
    Determine overall verdict based on feature gradient significance.

    MULTI_FEATURE_GRADIENT: >= 4 features significant and survive length control
    PARTIAL_GRADIENT: >= 2 features significant (any), fewer survive length control
    FLAT_COMPLEXITY: < 2 features significant
    """
    n_sig = sum(1 for f in feature_results.values() if f['significant'])
    n_survive = sum(1 for f in feature_results.values() if f['survives_length_control'])

    if n_survive >= 4:
        return 'MULTI_FEATURE_GRADIENT'
    elif n_sig >= 2:
        return 'PARTIAL_GRADIENT'
    else:
        return 'FLAT_COMPLEXITY'


def build_predictions(feature_results, kernel_results, verdict):
    """Build predictions for downstream testing."""
    predictions = {}

    # Identify strongest gradient features
    sig_features = {f: r for f, r in feature_results.items() if r['significant']}
    surviving = {f: r for f, r in feature_results.items() if r['survives_length_control']}

    predictions['n_significant_features'] = len(sig_features)
    predictions['n_length_controlled'] = len(surviving)
    predictions['gradient_features'] = sorted(sig_features.keys())
    predictions['length_robust_features'] = sorted(surviving.keys())

    # Direction summary
    increasing = [f for f, r in sig_features.items() if r['mean_slope'] > 0]
    decreasing = [f for f, r in sig_features.items() if r['mean_slope'] < 0]
    predictions['increasing_with_position'] = increasing
    predictions['decreasing_with_position'] = decreasing

    # Kernel gradient prediction
    if kernel_results.get('h_frac', {}).get('section_anova_p', 1.0) < 0.05:
        predictions['kernel_gradient_section_dependent'] = True
    else:
        predictions['kernel_gradient_section_dependent'] = False

    # Short paragraph signal
    short_sig = kernel_results.get('short_para_signal', {})
    short_34 = short_sig.get('3_4_lines', {})
    predictions['short_para_gradient_present'] = any(
        short_34.get(f'{kf}_p', 1.0) < 0.05 for kf in ['k', 'h', 'e']
    )

    return predictions


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 623, Script 3: Complexity Gradient")
    print("=" * 55)

    # Build corpus
    print("\n[1/6] Building corpus...")
    corpus = build_corpus()
    n_folios = len(corpus)
    n_paras_total = sum(len(f['paragraphs']) for f in corpus.values())
    print(f"  {n_folios} folios, {n_paras_total} paragraphs total")

    # Block 2: Compute per-paragraph slopes
    print("\n[2/6] Computing per-paragraph complexity slopes...")
    paragraphs_data = compute_paragraph_slopes(corpus)
    n_qualified = len(paragraphs_data)
    print(f"  {n_qualified} paragraphs with >= {MIN_BODY_LINES} body lines")

    if n_qualified < 10:
        print("  ERROR: Too few qualifying paragraphs for analysis. Aborting.")
        return

    # Block 3: Statistical tests
    print("\n[3/6] Running statistical tests (9 features)...")
    feature_results = run_feature_tests(paragraphs_data)

    for f in FEATURE_NAMES:
        r = feature_results[f]
        sig_mark = '*' if r['significant'] else ' '
        lc_mark = '+' if r['survives_length_control'] else ' '
        print(f"  {sig_mark}{lc_mark} {f:22s}  rho={r['mean_slope']:+.4f}  "
              f"p={r['p_value']:.4f}  lc_p={r['length_controlled_p']:.4f}")

    n_sig = sum(1 for r in feature_results.values() if r['significant'])
    n_lc = sum(1 for r in feature_results.values() if r['survives_length_control'])
    print(f"\n  Summary: {n_sig}/9 significant, {n_lc}/9 survive length control")

    # Block 4: Kernel gradient novelty
    print("\n[4/6] Kernel gradient novelty analysis...")
    kernel_results = compute_kernel_gradient(corpus, paragraphs_data)
    for kf in ['k_frac', 'h_frac', 'e_frac']:
        kr = kernel_results[kf]
        print(f"  {kf}: mean_slope={kr['mean_slope']:+.4f}  "
              f"ANOVA F={kr['section_anova_F']:.2f}  p={kr['section_anova_p']:.4f}")

    sps = kernel_results.get('short_para_signal', {})
    for label in ['3_4_lines', '6_plus']:
        entry = sps.get(label, {})
        print(f"  {label}: n={entry.get('n', 0)}  "
              f"h_slope={entry.get('h_slope', 0):.4f}  "
              f"h_p={entry.get('h_p', 1):.4f}")

    # Block 5: Section stratification
    print("\n[5/6] Section stratification...")
    section_data = section_stratification(paragraphs_data)
    # Merge into feature_results
    for f in FEATURE_NAMES:
        feature_results[f]['by_section'] = section_data[f]

    # Print section summary for most interesting features
    sections = sorted(set(p['section'] for p in paragraphs_data))
    print(f"  Sections: {sections}")
    for f in FEATURE_NAMES:
        sig_secs = [s for s, d in section_data[f].items() if d['p_value'] < 0.05]
        if sig_secs:
            print(f"  {f}: significant in sections {sig_secs}")

    # Block 6: Verdict
    print("\n[6/6] Determining verdict...")
    verdict = determine_verdict(feature_results)
    predictions = build_predictions(feature_results, kernel_results, verdict)
    print(f"  VERDICT: {verdict}")

    # Assemble output
    output = {
        'phase': 623,
        'name': 'complexity_gradient',
        'n_paragraphs': n_qualified,
        'features': round_floats(feature_results),
        'kernel_gradient': round_floats(kernel_results),
        'verdict': verdict,
        'predictions': round_floats(predictions),
    }

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'complexity_gradient.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()
