"""Phase 400: Lifecycle Domain Test

Tests whether individual B programs (paragraphs) show within-paragraph domain
progression (lifecycle: grow → harvest → prepare → distill) or maintain stable
domain character (single-domain model).

5-test battery:
  T1: Within-paragraph Bio-score trend (PRIMARY)
  T2: C932-controlled Bio-score trend (CRITICAL CONTROL)
  T3: Within-paragraph domain mixing stability (DIAGNOSTIC)
  T4: Folio domain purity vs paragraph variance (SUPPORTING)
  T5: REGIME-controlled section effect (NULL MODEL)

Bio-score per token: average of PREFIX, kernel, and macro-state components.
  PREFIX:  qo → +1 (Bio), ok → -1 (Stars), else → 0
  Kernel:  k → +1 (Bio), e → -1 (Stars), both → 0, h → 0
  Macro:   CC → +1 (Bio), FQ → -1 (Stars), AXM → +0.5 (Bio-enriched), else → 0

References: C1116, C932, C963, C961, C964, C1022, C1054
"""

import json
import math
import random
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer
RESULTS_DIR = PROJECT / 'phases' / 'LIFECYCLE_DOMAIN_TEST' / 'results'

MIN_BODY_LINES = 4  # Minimum body lines for paragraph to qualify


# ---------------------------------------------------------------------------
# Statistics helpers (no scipy dependency)
# ---------------------------------------------------------------------------

def spearman_rho(x, y):
    """Spearman rank correlation. Returns (rho, n)."""
    n = len(x)
    if n < 3:
        return 0.0, n
    # Rank with average ties
    def rank(vals):
        indexed = sorted(enumerate(vals), key=lambda p: p[1])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and indexed[j][1] == indexed[i][1]:
                j += 1
            avg_rank = (i + j - 1) / 2.0 + 1.0
            for k in range(i, j):
                ranks[indexed[k][0]] = avg_rank
            i = j
        return ranks
    rx = rank(x)
    ry = rank(y)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx)**2 for a in rx))
    dy = math.sqrt(sum((b - my)**2 for b in ry))
    if dx == 0 or dy == 0:
        return 0.0, n
    return num / (dx * dy), n


def wilcoxon_signed_rank(values):
    """One-sample Wilcoxon signed-rank test (two-sided).
    Returns (W_statistic, z_score, p_approx, n_nonzero).
    Uses normal approximation for n >= 10."""
    nonzero = [(abs(v), 1 if v > 0 else -1) for v in values if v != 0]
    n = len(nonzero)
    if n < 5:
        return 0, 0.0, 1.0, n
    # Rank by absolute value
    nonzero.sort(key=lambda p: p[0])
    ranks = []
    i = 0
    while i < n:
        j = i
        while j < n and nonzero[j][0] == nonzero[i][0]:
            j += 1
        avg_rank = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            ranks.append((avg_rank, nonzero[k][1]))
        i = j
    W_plus = sum(r for r, s in ranks if s > 0)
    W_minus = sum(r for r, s in ranks if s < 0)
    W = min(W_plus, W_minus)
    # Normal approximation
    mu = n * (n + 1) / 4.0
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    if sigma == 0:
        return W, 0.0, 1.0, n
    z = (W - mu) / sigma
    # Two-sided p from normal approximation
    p = 2 * normal_cdf(-abs(z))
    return W, z, p, n


def normal_cdf(x):
    """Standard normal CDF approximation (Abramowitz & Stegun)."""
    if x < -8:
        return 0.0
    if x > 8:
        return 1.0
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1 if x >= 0 else -1
    x_abs = abs(x)
    t = 1.0 / (1.0 + p * x_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x_abs * x_abs / 2)
    return 0.5 * (1.0 + sign * y)


def linear_regression(x, y):
    """Simple OLS. Returns (slope, intercept, r_squared)."""
    n = len(x)
    if n < 2:
        return 0, 0, 0
    mx = sum(x) / n
    my = sum(y) / n
    ss_xy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    ss_xx = sum((xi - mx)**2 for xi in x)
    ss_yy = sum((yi - my)**2 for yi in y)
    if ss_xx == 0:
        return 0, my, 0
    slope = ss_xy / ss_xx
    intercept = my - slope * mx
    r_sq = (ss_xy**2 / (ss_xx * ss_yy)) if ss_yy > 0 else 0
    return slope, intercept, r_sq


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    """Load B tokens, build paragraphs, load all mappings."""
    tx = Transcript()
    morph = Morphology()

    # Class mapping
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json') as f:
        class_data = json.load(f)
    token_to_class = class_data['token_to_class']

    # Macro-state mapping
    with open(PROJECT / 'data' / 'decoder_maps.json') as f:
        decoder_data = json.load(f)
    macro_map = {int(k): v['value'] for k, v in decoder_data['maps']['macro_state']['entries'].items()}

    # REGIME mapping
    with open(PROJECT / 'data' / 'regime_folio_mapping.json') as f:
        regime_data = json.load(f)
    folio_regime = {f: v['regime'] for f, v in regime_data['regime_assignments'].items()}

    # MIDDLE frequency data
    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # Build per-folio-line token lists
    lines = defaultdict(list)
    folio_section = {}
    for tok in tx.currier_b():
        word = tok.word.strip()
        if not word or '*' in word:
            continue
        lines[(tok.folio, tok.line)].append(tok)
        folio_section[tok.folio] = tok.section

    # Build paragraphs using par_initial
    folio_lines = defaultdict(list)
    for (f, l), toks in sorted(lines.items()):
        folio_lines[f].append((l, toks))

    paragraphs = []
    for f in sorted(folio_lines):
        curr_par = []
        for l, toks in folio_lines[f]:
            if toks[0].par_initial and curr_par:
                paragraphs.append({'folio': f, 'lines': curr_par})
                curr_par = []
            curr_par.append((l, toks))
        if curr_par:
            paragraphs.append({'folio': f, 'lines': curr_par})

    print(f"Loaded {len(paragraphs)} B paragraphs across {len(folio_lines)} folios")

    return (paragraphs, folio_regime, folio_section, token_to_class,
            macro_map, morph, mid_analyzer)


# ---------------------------------------------------------------------------
# Bio-score computation
# ---------------------------------------------------------------------------

def compute_bio_score(word, morph, token_to_class, macro_map):
    """Compute per-token Bio-score from 3 components.
    Returns (bio_score, components_dict)."""
    m = morph.extract(word)
    components = []

    # PREFIX component
    prefix_score = 0
    if m.prefix == 'qo':
        prefix_score = 1.0
    elif m.prefix == 'ok':
        prefix_score = -1.0
    if prefix_score != 0:
        components.append(prefix_score)

    # Kernel component (from MIDDLE characters)
    kernel_score = 0
    if m.middle:
        has_k = 'k' in m.middle
        has_e = 'e' in m.middle
        if has_k and not has_e:
            kernel_score = 1.0
        elif has_e and not has_k:
            kernel_score = -1.0
        # both or neither → 0
    if kernel_score != 0:
        components.append(kernel_score)

    # Macro-state component
    macro_score = 0
    cls = token_to_class.get(word)
    if cls is not None:
        macro = macro_map.get(cls)
        if macro == 'CC':
            macro_score = 1.0
        elif macro == 'FQ':
            macro_score = -1.0
        elif macro == 'AXM':
            macro_score = 0.5
    if macro_score != 0:
        components.append(macro_score)

    # Average of non-zero components (or 0 if all neutral)
    if components:
        bio_score = sum(components) / len(components)
    else:
        bio_score = 0.0

    return bio_score, {
        'prefix': prefix_score,
        'kernel': kernel_score,
        'macro': macro_score,
        'n_components': len(components)
    }


# ---------------------------------------------------------------------------
# Paragraph Bio-score profiles
# ---------------------------------------------------------------------------

def build_profiles(paragraphs, morph, token_to_class, macro_map, mid_analyzer):
    """Build Bio-score profiles for qualifying paragraphs."""
    profiles = []

    for para in paragraphs:
        folio = para['folio']
        all_lines = para['lines']
        if len(all_lines) < 2:
            continue  # Need at least header + 1 body line

        body_lines = all_lines[1:]  # Skip header (line 1)
        if len(body_lines) < MIN_BODY_LINES:
            continue

        line_scores = []
        all_token_data = []

        for li, (line_id, toks) in enumerate(body_lines):
            line_bio_scores = []
            for tok in toks:
                word = tok.word.strip()
                if not word or '*' in word:
                    continue
                bio, comps = compute_bio_score(word, morph, token_to_class, macro_map)

                # Get MIDDLE frequency for T2
                m = morph.extract(word)
                mid_freq = 0
                if m.middle:
                    stats = mid_analyzer.get_stats(m.middle)
                    if stats:
                        mid_freq = stats.token_count

                line_bio_scores.append(bio)
                all_token_data.append({
                    'word': word,
                    'bio_score': bio,
                    'body_line_idx': li,
                    'middle': m.middle,
                    'mid_freq': mid_freq,
                    'components': comps,
                })

            if line_bio_scores:
                line_scores.append({
                    'body_line_idx': li,
                    'mean_bio': sum(line_bio_scores) / len(line_bio_scores),
                    'n_tokens': len(line_bio_scores),
                    'bio_scores': line_bio_scores,
                })

        if len(line_scores) >= MIN_BODY_LINES:
            profiles.append({
                'folio': folio,
                'n_body_lines': len(line_scores),
                'line_scores': line_scores,
                'token_data': all_token_data,
            })

    print(f"Built {len(profiles)} qualifying paragraph profiles "
          f"(>= {MIN_BODY_LINES} body lines)")
    return profiles


# ---------------------------------------------------------------------------
# T1: Within-Paragraph Bio-Score Trend
# ---------------------------------------------------------------------------

def t1_within_paragraph_trend(profiles):
    """Spearman rho of mean Bio-score vs body-line position per paragraph.
    One-sample Wilcoxon signed-rank test on rho distribution."""
    print("\n=== T1: Within-Paragraph Bio-Score Trend ===")

    rhos = []
    for p in profiles:
        positions = [ls['body_line_idx'] for ls in p['line_scores']]
        bio_means = [ls['mean_bio'] for ls in p['line_scores']]
        rho, n = spearman_rho(positions, bio_means)
        rhos.append(rho)

    if not rhos:
        print("  No qualifying paragraphs!")
        return {'verdict': 'NO_DATA', 'n_paragraphs': 0}

    mean_rho = sum(rhos) / len(rhos)
    median_rho = sorted(rhos)[len(rhos) // 2]
    n_positive = sum(1 for r in rhos if r > 0)
    n_negative = sum(1 for r in rhos if r < 0)
    n_zero = sum(1 for r in rhos if r == 0)

    W, z, p_val, n_nz = wilcoxon_signed_rank(rhos)

    print(f"  N paragraphs: {len(rhos)}")
    print(f"  Mean rho: {mean_rho:.4f}")
    print(f"  Median rho: {median_rho:.4f}")
    print(f"  Positive/Negative/Zero: {n_positive}/{n_negative}/{n_zero}")
    print(f"  Wilcoxon W={W:.0f}, z={z:.2f}, p={p_val:.4f} (n_nonzero={n_nz})")

    if p_val < 0.05 and mean_rho > 0:
        verdict = 'LIFECYCLE_SIGNAL_DETECTED'
    elif p_val < 0.05 and mean_rho < 0:
        verdict = 'REVERSE_LIFECYCLE_SIGNAL'
    else:
        verdict = 'LIFECYCLE_FALSIFIED_PRIMARY'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_paragraphs': len(rhos),
        'mean_rho': round(mean_rho, 4),
        'median_rho': round(median_rho, 4),
        'n_positive': n_positive,
        'n_negative': n_negative,
        'n_zero': n_zero,
        'wilcoxon_W': round(W, 1),
        'wilcoxon_z': round(z, 3),
        'wilcoxon_p': round(p_val, 6),
        'n_nonzero': n_nz,
        'rho_distribution': {
            'q25': round(sorted(rhos)[len(rhos) // 4], 4),
            'q75': round(sorted(rhos)[3 * len(rhos) // 4], 4),
            'min': round(min(rhos), 4),
            'max': round(max(rhos), 4),
        },
    }


# ---------------------------------------------------------------------------
# T2: C932-Controlled Bio-Score Trend
# ---------------------------------------------------------------------------

def t2_c932_controlled_trend(profiles):
    """Residualize Bio-score against log(MIDDLE frequency), then re-run T1."""
    print("\n=== T2: C932-Controlled Bio-Score Trend ===")

    # Collect all token (bio_score, log_freq) pairs
    all_bio = []
    all_log_freq = []
    for p in profiles:
        for td in p['token_data']:
            if td['mid_freq'] > 0:
                all_bio.append(td['bio_score'])
                all_log_freq.append(math.log(td['mid_freq']))

    if len(all_bio) < 10:
        print("  Insufficient token data for residualization!")
        return {'verdict': 'NO_DATA'}

    # Fit regression: bio_score ~ log_freq
    slope, intercept, r_sq = linear_regression(all_log_freq, all_bio)
    print(f"  Regression: bio_score = {slope:.4f} * log_freq + {intercept:.4f}")
    print(f"  R² (frequency explains bio-score): {r_sq:.4f}")

    # Residualize per-token bio-scores
    rhos = []
    for p in profiles:
        # Compute residualized per-line means
        line_residuals = defaultdict(list)
        for td in p['token_data']:
            if td['mid_freq'] > 0:
                predicted = slope * math.log(td['mid_freq']) + intercept
                residual = td['bio_score'] - predicted
            else:
                residual = td['bio_score'] - intercept
            line_residuals[td['body_line_idx']].append(residual)

        positions = sorted(line_residuals.keys())
        if len(positions) < MIN_BODY_LINES:
            continue
        means = [sum(line_residuals[pos]) / len(line_residuals[pos])
                 for pos in positions]
        rho, n = spearman_rho(list(positions), means)
        rhos.append(rho)

    if not rhos:
        print("  No qualifying paragraphs after residualization!")
        return {'verdict': 'NO_DATA'}

    mean_rho = sum(rhos) / len(rhos)
    median_rho = sorted(rhos)[len(rhos) // 2]
    W, z, p_val, n_nz = wilcoxon_signed_rank(rhos)

    print(f"  N paragraphs: {len(rhos)}")
    print(f"  Mean residual rho: {mean_rho:.4f}")
    print(f"  Median residual rho: {median_rho:.4f}")
    print(f"  Wilcoxon W={W:.0f}, z={z:.2f}, p={p_val:.4f}")

    if p_val < 0.05:
        verdict = 'GENUINE_LIFECYCLE_SIGNAL'
    else:
        verdict = 'LIFECYCLE_FALSIFIED_CONTROLLED'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_paragraphs': len(rhos),
        'regression_slope': round(slope, 4),
        'regression_intercept': round(intercept, 4),
        'regression_r_squared': round(r_sq, 4),
        'mean_residual_rho': round(mean_rho, 4),
        'median_residual_rho': round(median_rho, 4),
        'wilcoxon_W': round(W, 1),
        'wilcoxon_z': round(z, 3),
        'wilcoxon_p': round(p_val, 6),
        'n_nonzero': n_nz,
    }


# ---------------------------------------------------------------------------
# T3: Within-Paragraph Domain Mixing Stability
# ---------------------------------------------------------------------------

def t3_domain_mixing_stability(profiles):
    """First-half vs second-half Bio-fraction, permutation test."""
    print("\n=== T3: Within-Paragraph Domain Mixing Stability ===")

    random.seed(42)
    N_PERM = 1000

    real_deltas = []
    for p in profiles:
        scores = [td['bio_score'] for td in p['token_data']]
        n = len(scores)
        if n < 4:
            continue

        # Assign tokens to halves by body line index
        mid_line = p['n_body_lines'] // 2
        first_half = [td['bio_score'] for td in p['token_data']
                      if td['body_line_idx'] < mid_line]
        second_half = [td['bio_score'] for td in p['token_data']
                       if td['body_line_idx'] >= mid_line]

        if not first_half or not second_half:
            continue

        frac_first = sum(1 for s in first_half if s > 0) / len(first_half)
        frac_second = sum(1 for s in second_half if s > 0) / len(second_half)
        real_deltas.append(abs(frac_first - frac_second))

    if not real_deltas:
        print("  No qualifying paragraphs!")
        return {'verdict': 'NO_DATA'}

    real_mean_delta = sum(real_deltas) / len(real_deltas)

    # Permutation null: shuffle token positions within each paragraph
    perm_mean_deltas = []
    for _ in range(N_PERM):
        perm_deltas = []
        for p in profiles:
            scores = [td['bio_score'] for td in p['token_data']]
            n = len(scores)
            if n < 4:
                continue

            mid_line = p['n_body_lines'] // 2
            n_first = sum(1 for td in p['token_data']
                          if td['body_line_idx'] < mid_line)
            n_second = n - n_first
            if n_first == 0 or n_second == 0:
                continue

            shuffled = scores[:]
            random.shuffle(shuffled)
            first_shuf = shuffled[:n_first]
            second_shuf = shuffled[n_first:]

            frac_first = sum(1 for s in first_shuf if s > 0) / len(first_shuf)
            frac_second = sum(1 for s in second_shuf if s > 0) / len(second_shuf)
            perm_deltas.append(abs(frac_first - frac_second))

        if perm_deltas:
            perm_mean_deltas.append(sum(perm_deltas) / len(perm_deltas))

    perm_mean = sum(perm_mean_deltas) / len(perm_mean_deltas)
    perm_95 = sorted(perm_mean_deltas)[int(0.95 * len(perm_mean_deltas))]
    p_val = sum(1 for d in perm_mean_deltas if d >= real_mean_delta) / len(perm_mean_deltas)

    print(f"  N paragraphs: {len(real_deltas)}")
    print(f"  Real mean |delta|: {real_mean_delta:.4f}")
    print(f"  Permutation mean |delta|: {perm_mean:.4f}")
    print(f"  Permutation 95th percentile: {perm_95:.4f}")
    print(f"  p-value (real >= perm): {p_val:.4f}")

    if p_val < 0.05:
        verdict = 'DOMAIN_SHIFT_WITHIN_PARAGRAPH'
    else:
        verdict = 'STABLE_DOMAIN_WITHIN_PARAGRAPH'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_paragraphs': len(real_deltas),
        'real_mean_delta': round(real_mean_delta, 4),
        'perm_mean_delta': round(perm_mean, 4),
        'perm_95th': round(perm_95, 4),
        'p_value': round(p_val, 4),
        'n_permutations': N_PERM,
    }


# ---------------------------------------------------------------------------
# T4: Folio Domain Purity vs Paragraph Variance
# ---------------------------------------------------------------------------

def t4_folio_domain_purity(profiles, folio_regime):
    """ANOVA and ICC of folio on paragraph Bio-score."""
    print("\n=== T4: Folio Domain Purity vs Paragraph Variance ===")

    # Per-paragraph mean Bio-score
    folio_para_scores = defaultdict(list)
    for p in profiles:
        all_scores = [td['bio_score'] for td in p['token_data']]
        if all_scores:
            mean_bio = sum(all_scores) / len(all_scores)
            folio_para_scores[p['folio']].append(mean_bio)

    # Need folios with 2+ paragraphs for within-folio variance
    folios_multi = {f: scores for f, scores in folio_para_scores.items()
                    if len(scores) >= 2}
    all_folios = {f: scores for f, scores in folio_para_scores.items()}

    print(f"  Total folios with paragraphs: {len(all_folios)}")
    print(f"  Folios with 2+ paragraphs: {len(folios_multi)}")

    if len(folios_multi) < 3:
        print("  Insufficient multi-paragraph folios!")
        return {'verdict': 'NO_DATA'}

    # One-way ANOVA (between-folio vs within-folio)
    all_scores_flat = []
    group_labels = []
    for f, scores in folios_multi.items():
        for s in scores:
            all_scores_flat.append(s)
            group_labels.append(f)

    grand_mean = sum(all_scores_flat) / len(all_scores_flat)
    k = len(folios_multi)  # number of groups
    n_total = len(all_scores_flat)

    # Between-group SS
    ss_between = sum(len(scores) * (sum(scores) / len(scores) - grand_mean)**2
                     for scores in folios_multi.values())
    # Within-group SS
    ss_within = sum(sum((s - sum(scores) / len(scores))**2 for s in scores)
                    for scores in folios_multi.values())

    df_between = k - 1
    df_within = n_total - k

    if df_within == 0 or ss_within == 0:
        f_ratio = float('inf')
    else:
        ms_between = ss_between / df_between
        ms_within = ss_within / df_within
        f_ratio = ms_between / ms_within

    # ICC(1) = (MS_between - MS_within) / (MS_between + (n0 - 1) * MS_within)
    # where n0 is average group size
    n0 = n_total / k
    if df_within > 0 and ss_within > 0:
        ms_b = ss_between / df_between
        ms_w = ss_within / df_within
        icc = (ms_b - ms_w) / (ms_b + (n0 - 1) * ms_w)
    else:
        icc = 1.0

    # Per-folio summary
    folio_means = {f: sum(s) / len(s) for f, s in all_folios.items()}
    folio_mean_values = list(folio_means.values())
    global_mean_bio = sum(folio_mean_values) / len(folio_mean_values)

    print(f"  Grand mean Bio-score: {grand_mean:.4f}")
    print(f"  ANOVA F({df_between},{df_within}) = {f_ratio:.2f}")
    print(f"  ICC(1) = {icc:.3f}")
    print(f"  Mean folio-level Bio-score: {global_mean_bio:.4f}")

    if icc > 0.3:
        verdict = 'FOLIO_DETERMINES_DOMAIN'
    elif icc > 0.1:
        verdict = 'MODERATE_FOLIO_EFFECT'
    else:
        verdict = 'PARAGRAPH_INDEPENDENT'

    print(f"  Verdict: {verdict}")

    return {
        'verdict': verdict,
        'n_folios_multi': len(folios_multi),
        'n_paragraphs': n_total,
        'grand_mean_bio': round(grand_mean, 4),
        'f_ratio': round(f_ratio, 2),
        'df_between': df_between,
        'df_within': df_within,
        'icc': round(icc, 3),
        'folio_bio_score_range': {
            'min': round(min(folio_mean_values), 4),
            'max': round(max(folio_mean_values), 4),
            'mean': round(global_mean_bio, 4),
        },
    }


# ---------------------------------------------------------------------------
# T5: REGIME-Controlled Section Effect
# ---------------------------------------------------------------------------

def t5_regime_controlled_section(profiles, folio_regime, folio_section):
    """Within REGIME_1: section effect on Bio-score, within-paragraph rho by section."""
    print("\n=== T5: REGIME-Controlled Section Effect ===")

    # Identify REGIME_1 paragraphs by section
    r1_profiles = defaultdict(list)
    for p in profiles:
        regime = folio_regime.get(p['folio'])
        section = folio_section.get(p['folio'])
        if regime == 'REGIME_1' and section in ('B', 'S', 'H'):
            r1_profiles[section].append(p)

    section_counts = {s: len(ps) for s, ps in r1_profiles.items()}
    print(f"  REGIME_1 paragraphs by section: {section_counts}")

    if not r1_profiles:
        print("  No REGIME_1 paragraphs found!")
        return {'verdict': 'NO_DATA'}

    # Per-section mean Bio-score
    section_bio_means = {}
    for section, ps in r1_profiles.items():
        all_scores = []
        for p in ps:
            for td in p['token_data']:
                all_scores.append(td['bio_score'])
        if all_scores:
            section_bio_means[section] = sum(all_scores) / len(all_scores)

    print(f"  Section mean Bio-scores: {', '.join(f'{s}={v:.4f}' for s, v in sorted(section_bio_means.items()))}")

    # Section effect: do Bio-section folios have higher Bio-score than Stars?
    bio_mean = section_bio_means.get('B', 0)
    stars_mean = section_bio_means.get('S', 0)
    section_diff = bio_mean - stars_mean
    print(f"  Bio - Stars mean difference: {section_diff:.4f}")

    # Within-paragraph rho by section (re-run T1 logic per section)
    section_rhos = {}
    for section, ps in r1_profiles.items():
        rhos = []
        for p in ps:
            positions = [ls['body_line_idx'] for ls in p['line_scores']]
            bio_means_list = [ls['mean_bio'] for ls in p['line_scores']]
            rho, n = spearman_rho(positions, bio_means_list)
            rhos.append(rho)

        if rhos:
            mean_rho = sum(rhos) / len(rhos)
            W, z, p_val, n_nz = wilcoxon_signed_rank(rhos)
            section_rhos[section] = {
                'n_paragraphs': len(rhos),
                'mean_rho': round(mean_rho, 4),
                'wilcoxon_z': round(z, 3),
                'wilcoxon_p': round(p_val, 6),
            }
            print(f"  Section {section}: mean_rho={mean_rho:.4f}, z={z:.2f}, p={p_val:.4f} (n={len(rhos)})")

    # Determine verdict
    any_section_lifecycle = any(
        v['wilcoxon_p'] < 0.05 and v['mean_rho'] > 0
        for v in section_rhos.values()
    )

    if section_diff > 0.01:
        section_verdict = 'SECTION_PARAMETERIZATION_CONFIRMED'
    else:
        section_verdict = 'SECTION_EFFECT_WEAK'

    if any_section_lifecycle:
        lifecycle_verdict = 'LIFECYCLE_TRANSCENDS_SECTION'
    else:
        lifecycle_verdict = 'LIFECYCLE_FALSIFIED_CROSS_SECTION'

    combined = f"{section_verdict}_{lifecycle_verdict}"
    print(f"  Section verdict: {section_verdict}")
    print(f"  Lifecycle verdict: {lifecycle_verdict}")

    return {
        'verdict': combined,
        'section_verdict': section_verdict,
        'lifecycle_verdict': lifecycle_verdict,
        'regime_1_section_counts': section_counts,
        'section_bio_means': {s: round(v, 4) for s, v in section_bio_means.items()},
        'bio_stars_diff': round(section_diff, 4),
        'section_within_paragraph_rhos': section_rhos,
    }


# ---------------------------------------------------------------------------
# Bio-score diagnostics
# ---------------------------------------------------------------------------

def bio_score_diagnostics(profiles):
    """Summary statistics on the Bio-score distribution."""
    print("\n=== Bio-Score Diagnostics ===")

    all_scores = []
    component_counts = Counter()
    for p in profiles:
        for td in p['token_data']:
            all_scores.append(td['bio_score'])
            nc = td['components']['n_components']
            component_counts[nc] += 1

    if not all_scores:
        return {}

    mean_bio = sum(all_scores) / len(all_scores)
    n_pos = sum(1 for s in all_scores if s > 0)
    n_neg = sum(1 for s in all_scores if s < 0)
    n_zero = sum(1 for s in all_scores if s == 0)

    sorted_scores = sorted(all_scores)
    n = len(sorted_scores)

    print(f"  Total tokens scored: {n}")
    print(f"  Mean Bio-score: {mean_bio:.4f}")
    print(f"  Positive/Negative/Zero: {n_pos}/{n_neg}/{n_zero}")
    print(f"  Component counts: {dict(sorted(component_counts.items()))}")
    print(f"  Range: [{sorted_scores[0]:.3f}, {sorted_scores[-1]:.3f}]")
    print(f"  Q25={sorted_scores[n//4]:.3f}, Median={sorted_scores[n//2]:.3f}, "
          f"Q75={sorted_scores[3*n//4]:.3f}")

    return {
        'n_tokens': n,
        'mean': round(mean_bio, 4),
        'median': round(sorted_scores[n // 2], 4),
        'n_positive': n_pos,
        'n_negative': n_neg,
        'n_zero': n_zero,
        'component_distribution': dict(sorted(component_counts.items())),
        'range': [round(sorted_scores[0], 4), round(sorted_scores[-1], 4)],
    }


# ---------------------------------------------------------------------------
# Combined verdict
# ---------------------------------------------------------------------------

def combined_verdict(results):
    """Apply verdict framework from plan."""
    print("\n" + "=" * 60)
    print("COMBINED VERDICT")
    print("=" * 60)

    t1 = results['t1']
    t2 = results['t2']
    t3 = results['t3']
    t4 = results['t4']
    t5 = results['t5']

    votes = {
        't1': t1['verdict'],
        't2': t2['verdict'],
        't3': t3['verdict'],
        't4': t4['verdict'],
        't5_section': t5.get('section_verdict', 'NO_DATA'),
        't5_lifecycle': t5.get('lifecycle_verdict', 'NO_DATA'),
    }

    print(f"\n  Per-test verdicts:")
    for test, verdict in votes.items():
        print(f"    {test}: {verdict}")

    # Determine overall
    t1_lifecycle = 'LIFECYCLE_SIGNAL' in t1['verdict']
    t2_lifecycle = t2['verdict'] == 'GENUINE_LIFECYCLE_SIGNAL'
    t3_shift = t3['verdict'] == 'DOMAIN_SHIFT_WITHIN_PARAGRAPH'
    t4_folio = 'FOLIO_DETERMINES' in t4['verdict']
    t5_lifecycle = t5.get('lifecycle_verdict') == 'LIFECYCLE_TRANSCENDS_SECTION'

    if not t1_lifecycle:
        overall = 'LIFECYCLE_FALSIFIED'
        reasoning = ('T1 (primary test) shows no significant within-paragraph '
                     'Bio-score trend. Lifecycle hypothesis falsified.')
    elif t1_lifecycle and not t2_lifecycle:
        overall = 'RARITY_ARTIFACT'
        reasoning = ('T1 shows Bio-score trend but T2 (after C932 frequency control) '
                     'does not. Signal is a rarity-gradient artifact.')
    elif t1_lifecycle and t2_lifecycle:
        supporting = sum([t3_shift, not t4_folio, t5_lifecycle])
        if supporting >= 2:
            overall = 'LIFECYCLE_SUPPORTED'
            reasoning = (f'T1+T2 both significant, {supporting}/3 supporting tests align. '
                         'Lifecycle hypothesis supported (pending Tier 2 validation).')
        else:
            overall = 'LIFECYCLE_AMBIGUOUS'
            reasoning = (f'T1+T2 significant but only {supporting}/3 supporting tests. '
                         'Lifecycle signal present but contradicted by other evidence.')
    else:
        overall = 'INDETERMINATE'
        reasoning = 'Unexpected combination of results.'

    print(f"\n  OVERALL: {overall}")
    print(f"  Reasoning: {reasoning}")

    return {
        'overall': overall,
        'reasoning': reasoning,
        'per_test_verdicts': votes,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Phase 400: Lifecycle Domain Test")
    print("=" * 50)

    (paragraphs, folio_regime, folio_section, token_to_class,
     macro_map, morph, mid_analyzer) = load_data()

    profiles = build_profiles(paragraphs, morph, token_to_class,
                              macro_map, mid_analyzer)

    # Diagnostics
    diag = bio_score_diagnostics(profiles)

    # Run 5-test battery
    results = {}
    results['diagnostics'] = diag
    results['t1'] = t1_within_paragraph_trend(profiles)
    results['t2'] = t2_c932_controlled_trend(profiles)
    results['t3'] = t3_domain_mixing_stability(profiles)
    results['t4'] = t4_folio_domain_purity(profiles, folio_regime)
    results['t5'] = t5_regime_controlled_section(profiles, folio_regime, folio_section)

    # Combined verdict
    results['combined'] = combined_verdict(results)

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / 'lifecycle_domain_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
