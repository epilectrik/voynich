"""
Phase 623: LINE_LEVEL_SEQUENTIAL_ARCHITECTURE -- Script 5: Grammar Temperature

Per-folio composite rule compliance metric across 5 structural rule sets.
Tests for compositional drift via correlation with quire position.

Metrics:
  1. Forbidden buffer proximity (C997, C1027) -- nearness to 17 forbidden transitions
  2. Modifier avoidance (C1472) -- 8 modifier atom pairs that never co-occur
  3. Terminal opacity compliance (C1440-C1445) -- suffix rate by terminal tier
  4. PREFIX-MIDDLE HEAD surprisal (C1415) -- 83 forbidden prefix x head combos
  5. PREFIX-MIDDLE surprisal (C911) -- 102 forbidden prefix x middle combos
"""
import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from phases.LINE_LEVEL_SEQUENTIAL_ARCHITECTURE.scripts.shared import (
    build_corpus, RNG, RESULTS_DIR, round_floats,
)

N_SHUFFLE = 200  # Token-shuffle null iterations per folio


# ============================================================
# Block 0: Constants
# ============================================================

# The 17 forbidden MIDDLE pairs (C109), grouped by hazard class
FORBIDDEN_MIDDLE_PAIRS = [
    # PHASE_ORDERING (7)
    ('chey', 'chedy'), ('chey', 'shedy'), ('chedy', 'ee'),
    ('shedy', 'aiin'), ('shedy', 'o'), ('shey', 'aiin'), ('shey', 'al'),
    # COMPOSITION_JUMP (4)
    ('dy', 'aiin'), ('dy', 'chey'), ('ar', 'dal'), ('or', 'dal'),
    # CONTAINMENT_TIMING (4)
    ('he', 't'), ('he', 'or'), ('l', 'chol'), ('shey', 'c'),
    # RATE_MISMATCH (1)
    ('c', 'ee'),
    # ENERGY_OVERSHOOT (1)
    ('chol', 'r'),
]

# Expand to category-level forbidden pairs for proximity computation.
# Each MIDDLE maps to a category via the classifier. We also need the
# set of forbidden (source_cat, target_cat) pairs and adjacent pairs.

# 8 modifier atom pairs that NEVER co-occur in compound MIDDLEs (C1472)
AVOIDED_MOD_PAIRS = {
    frozenset({'c', 'd'}), frozenset({'c', 'f'}), frozenset({'c', 's'}),
    frozenset({'d', 'f'}), frozenset({'d', 's'}), frozenset({'f', 'p'}),
    frozenset({'f', 's'}), frozenset({'p', 's'}),
}

# Terminal opacity tiers (C1440-C1445)
# Corpus-wide suffix rates by terminal tier
CORPUS_SUFFIX_RATES = {
    'OPAQUE_y':   0.0161,   # y: 1.61%
    'OPAQUE_m':   0.0415,   # m: 4.15%
    'OPAQUE_n':   0.0084,   # n: 0.84%
    'SEMI_l':     0.1678,   # l: 16.78%
    'SEMI_r':     0.1952,   # r: 19.52%
    'TRANSPARENT_h': 0.9868,  # h: 98.68%
}

TERM_TO_TIER_KEY = {
    'y': 'OPAQUE_y', 'm': 'OPAQUE_m', 'n': 'OPAQUE_n',
    'l': 'SEMI_l', 'r': 'SEMI_r', 'h': 'TRANSPARENT_h',
}


# ============================================================
# Block 1: Statistical helpers
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
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_rho(x, y):
    """Compute Spearman rank correlation."""
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


def _normal_cdf(z):
    """Approximation of standard normal CDF (Abramowitz & Stegun)."""
    if z < -8.0:
        return 0.0
    if z > 8.0:
        return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1.0 if z >= 0 else -1.0
    z_abs = abs(z) / math.sqrt(2.0)
    t = 1.0 / (1.0 + p * z_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z_abs * z_abs)
    return 0.5 * (1.0 + sign * y)


def spearman_p_value(rho, n):
    """Approximate p-value for Spearman rho using t-distribution normal approx."""
    if n < 4:
        return 1.0
    t_stat = rho * math.sqrt((n - 2) / max(1e-12, 1 - rho ** 2))
    p = 2.0 * (1.0 - _normal_cdf(abs(t_stat)))
    return p


# ============================================================
# Block 2: Pre-compute corpus-wide distributions
# ============================================================

def build_folio_token_sequences(corpus):
    """
    Extract flat token sequence per folio (preserving line order).

    Returns: {folio: [token_dict, ...], ...}
    """
    folio_seqs = {}
    for folio, fdata in sorted(corpus.items()):
        tokens = []
        for para in fdata['paragraphs']:
            for line in para['header_lines'] + para['body_lines']:
                tokens.extend(line['tokens'])
        if tokens:
            folio_seqs[folio] = tokens
    return folio_seqs


def build_corpus_prefix_head_rates(folio_seqs):
    """
    Compute corpus-wide (prefix, head) pair frequencies.
    Returns: {(prefix, head): rate, ...}
    """
    pair_counts = Counter()
    total = 0
    for tokens in folio_seqs.values():
        for t in tokens:
            if t['prefix'] and t['head']:
                pair_counts[(t['prefix'], t['head'])] += 1
                total += 1
    if total == 0:
        return {}
    return {pair: count / total for pair, count in pair_counts.items()}


def build_corpus_prefix_middle_rates(folio_seqs):
    """
    Compute corpus-wide (prefix, middle) pair frequencies.
    Returns: {(prefix, middle): rate, ...}
    """
    pair_counts = Counter()
    total = 0
    for tokens in folio_seqs.values():
        for t in tokens:
            if t['prefix'] and t['middle']:
                pair_counts[(t['prefix'], t['middle'])] += 1
                total += 1
    if total == 0:
        return {}
    return {pair: count / total for pair, count in pair_counts.items()}


def build_forbidden_category_pairs(folio_seqs):
    """
    Expand the 17 MIDDLE-level forbidden pairs to category-level.
    Also compute the set of category pairs adjacent to forbidden pairs
    (sharing a source or target category).

    Returns: (forbidden_cat_pairs, adjacent_cat_pairs)
    Both are sets of (source_cat, target_cat) tuples.
    """
    # Build MIDDLE -> category mapping from the corpus
    from scripts.voynich import CategoryClassifier
    cc = CategoryClassifier()

    forbidden_cat_pairs = set()
    for src, tgt in FORBIDDEN_MIDDLE_PAIRS:
        src_cat = cc.classify(src)
        tgt_cat = cc.classify(tgt)
        if src_cat and tgt_cat:
            forbidden_cat_pairs.add((src_cat, tgt_cat))

    # Adjacent = shares source or target with any forbidden pair
    forbidden_sources = {p[0] for p in forbidden_cat_pairs}
    forbidden_targets = {p[1] for p in forbidden_cat_pairs}

    from phases.LINE_LEVEL_SEQUENTIAL_ARCHITECTURE.scripts.shared import CATEGORIES
    adjacent_cat_pairs = set()
    for s in CATEGORIES:
        for t in CATEGORIES:
            if (s, t) in forbidden_cat_pairs:
                continue
            # Adjacent if s is a forbidden source or t is a forbidden target
            if s in forbidden_sources or t in forbidden_targets:
                adjacent_cat_pairs.add((s, t))

    return forbidden_cat_pairs, adjacent_cat_pairs


# ============================================================
# Block 3: Five rule-compliance metrics
# ============================================================

def metric_buffer_proximity(tokens, forbidden_cat_pairs, adjacent_cat_pairs):
    """
    Metric 1: Forbidden buffer proximity (C997, C1027).

    Count forbidden-adjacent category bigrams / total category bigrams.
    Forbidden-adjacent = bigram whose (cat_i, cat_j) is in the forbidden
    set OR adjacent set (one hop from forbidden).

    Lower rate = colder grammar (staying further from forbidden zone).
    """
    if len(tokens) < 2:
        return 0.0

    categories = [t['category'] for t in tokens]
    n_bigrams = 0
    n_near_forbidden = 0

    for i in range(len(categories) - 1):
        pair = (categories[i], categories[i + 1])
        n_bigrams += 1
        if pair in forbidden_cat_pairs or pair in adjacent_cat_pairs:
            n_near_forbidden += 1

    if n_bigrams == 0:
        return 0.0
    return n_near_forbidden / n_bigrams


def metric_modifier_avoidance(tokens):
    """
    Metric 2: Modifier avoidance (C1472).

    For tokens with 2+ modifier atoms, check if any avoided pair
    both appear in the modifier string.

    Rate = violations / total_tokens_with_2plus_mods.
    Lower rate = colder grammar (stricter avoidance).
    """
    n_eligible = 0
    n_violations = 0

    for t in tokens:
        mods = t['mods']
        if len(mods) < 2:
            continue
        n_eligible += 1
        mod_chars = set(mods)
        for pair in AVOIDED_MOD_PAIRS:
            if pair.issubset(mod_chars):
                n_violations += 1
                break  # one violation per token is enough

    if n_eligible == 0:
        return 0.0
    return n_violations / n_eligible


def metric_opacity_deviation(tokens):
    """
    Metric 3: Terminal opacity compliance (C1440-C1445).

    For each terminal tier, compute actual suffix rate per folio.
    Deviation = sum of |folio_rate - corpus_rate| across terminal tiers.

    Lower deviation = colder grammar (tighter compliance).
    """
    tier_counts = defaultdict(lambda: {'total': 0, 'with_suffix': 0})

    for t in tokens:
        term = t['term']
        if term == 'bare' or not term:
            continue
        tier_key = TERM_TO_TIER_KEY.get(term)
        if not tier_key:
            continue
        tier_counts[tier_key]['total'] += 1
        if t['suffix']:
            tier_counts[tier_key]['with_suffix'] += 1

    deviation = 0.0
    n_tiers_measured = 0

    for tier_key, corpus_rate in CORPUS_SUFFIX_RATES.items():
        counts = tier_counts.get(tier_key)
        if counts and counts['total'] >= 3:  # need minimum tokens
            folio_rate = counts['with_suffix'] / counts['total']
            deviation += abs(folio_rate - corpus_rate)
            n_tiers_measured += 1

    if n_tiers_measured == 0:
        return 0.0
    # Normalize by number of tiers measured
    return deviation / n_tiers_measured


def metric_prefix_head_surprisal(tokens, corpus_ph_rates):
    """
    Metric 4: PREFIX-MIDDLE HEAD surprisal (C1415).

    For each token with prefix and head, compute -log2(corpus_rate).
    Return mean surprisal across folio tokens.

    Higher surprisal = hotter grammar (more unusual prefix-head combos).
    """
    if not corpus_ph_rates:
        return 0.0

    surprisals = []
    # Use a small floor to avoid infinite surprisal
    floor = 1e-6

    for t in tokens:
        if t['prefix'] and t['head']:
            pair = (t['prefix'], t['head'])
            rate = corpus_ph_rates.get(pair, floor)
            surprisals.append(-math.log2(max(rate, floor)))

    if not surprisals:
        return 0.0
    return sum(surprisals) / len(surprisals)


def metric_prefix_middle_surprisal(tokens, corpus_pm_rates):
    """
    Metric 5: PREFIX-MIDDLE surprisal (C911).

    For each token with prefix and middle, compute -log2(corpus_rate).
    Return mean surprisal across folio tokens.

    Higher surprisal = hotter grammar (more unusual prefix-middle combos).
    """
    if not corpus_pm_rates:
        return 0.0

    surprisals = []
    floor = 1e-6

    for t in tokens:
        if t['prefix'] and t['middle']:
            pair = (t['prefix'], t['middle'])
            rate = corpus_pm_rates.get(pair, floor)
            surprisals.append(-math.log2(max(rate, floor)))

    if not surprisals:
        return 0.0
    return sum(surprisals) / len(surprisals)


def compute_all_metrics(tokens, forbidden_cat_pairs, adjacent_cat_pairs,
                        corpus_ph_rates, corpus_pm_rates):
    """Compute all 5 metrics for a token sequence."""
    return {
        'buffer': metric_buffer_proximity(tokens, forbidden_cat_pairs, adjacent_cat_pairs),
        'modifier': metric_modifier_avoidance(tokens),
        'opacity': metric_opacity_deviation(tokens),
        'pfx_head': metric_prefix_head_surprisal(tokens, corpus_ph_rates),
        'pfx_mid': metric_prefix_middle_surprisal(tokens, corpus_pm_rates),
    }


# ============================================================
# Block 4: Token-shuffle null and temperature computation
# ============================================================

def compute_folio_temperature(tokens, forbidden_cat_pairs, adjacent_cat_pairs,
                              corpus_ph_rates, corpus_pm_rates, rng, n_shuffle=N_SHUFFLE):
    """
    Compute grammar temperature for a folio's token sequence.

    T_metric = real_metric / mean_shuffled_metric for "hot" metrics (buffer, pfx_head, pfx_mid)
    T_metric = mean_shuffled_metric / real_metric for "cold" metrics (modifier, opacity)
    -- actually, we want T > 1 = MORE compliant, so:
    -- For metrics where LOWER = more compliant: T = mean_shuffled / real
    -- For metrics where HIGHER = more compliant: T = real / mean_shuffled

    All 5 metrics: lower value = more compliant (colder):
      buffer: lower = fewer near-forbidden bigrams = more compliant
      modifier: lower = fewer avoidance violations = more compliant
      opacity: lower = closer to corpus rates = more compliant
      pfx_head: LOWER surprisal would mean LESS unusual... but we want compliance.
                Actually, lower surprisal = more typical = more compliant? No.
                The grammar FORBIDS certain combos (C1415), so HIGH surprisal means
                using rare/forbidden combos = LESS compliant.
                But shuffling preserves token vocabulary, just reorders.
                So surprisal for individual tokens doesn't change -- only ORDER changes.
                Actually: shuffling DOES change which prefix pairs with which head because
                different tokens get shuffled to different positions. But each token retains
                its own prefix and head. So token-level prefix-head surprisal is unchanged!

    CORRECTION: Token shuffle preserves each token intact (word, prefix, middle, etc.)
    but destroys sequential order. So:
      - buffer (sequential bigram metric): shuffle destroys order -> changes metric
      - modifier (per-token metric): shuffle preserves each token -> UNCHANGED
      - opacity (per-token metric): shuffle preserves each token -> UNCHANGED
      - pfx_head (per-token metric): shuffle preserves each token -> UNCHANGED
      - pfx_mid (per-token metric): shuffle preserves each token -> UNCHANGED

    Only metric 1 (buffer) is truly sequential. The others are bag-of-tokens metrics.
    For bag-of-tokens metrics, T = real/shuffled = 1.0 always.

    REVISED APPROACH: For non-sequential metrics (2-5), use a VOCABULARY-SHUFFLE null
    instead: randomly reassign token properties by sampling from the folio's vocabulary
    with replacement. This breaks the internal consistency of tokens.

    Actually, a cleaner approach: for metrics 2-5, shuffle the MIDDLE assignments
    among tokens (keeping prefix/suffix fixed). This tests whether the specific
    prefix-middle pairing and modifier composition is more rule-compliant than random.

    FINAL DESIGN:
    - For metric 1 (buffer): token-position shuffle (destroys sequence)
    - For metrics 2-5: property-shuffle (shuffle middles among tokens independently,
      also shuffle prefixes independently). This preserves marginal distributions
      but breaks specific token-level pairings.
    """
    real_metrics = compute_all_metrics(
        tokens, forbidden_cat_pairs, adjacent_cat_pairs,
        corpus_ph_rates, corpus_pm_rates
    )

    # Collect shuffled metrics
    null_metrics = {k: [] for k in real_metrics}

    # Pre-extract shuffleable properties
    n_tok = len(tokens)
    if n_tok < 5:
        # Too few tokens for meaningful temperature
        return {f'T_{k}': 1.0 for k in real_metrics}, real_metrics

    # Properties to shuffle
    all_middles = [t['middle'] for t in tokens]
    all_heads = [t['head'] for t in tokens]
    all_mods = [t['mods'] for t in tokens]
    all_terms = [t['term'] for t in tokens]
    all_categories = [t['category'] for t in tokens]
    all_prefixes = [t['prefix'] for t in tokens]
    all_suffixes = [t['suffix'] for t in tokens]

    for _ in range(n_shuffle):
        # Create shuffled token copies

        # For metric 1 (buffer): shuffle token ORDER (categories change sequence)
        shuffled_order = list(range(n_tok))
        rng.shuffle(shuffled_order)
        reordered_tokens = [tokens[i] for i in shuffled_order]

        # For metrics 2-5: shuffle properties across tokens
        shuf_middles = list(all_middles)
        shuf_heads = list(all_heads)
        shuf_mods = list(all_mods)
        shuf_terms = list(all_terms)
        shuf_cats = list(all_categories)
        shuf_prefixes = list(all_prefixes)
        shuf_suffixes = list(all_suffixes)

        rng.shuffle(shuf_middles)
        rng.shuffle(shuf_heads)
        rng.shuffle(shuf_mods)
        rng.shuffle(shuf_terms)
        rng.shuffle(shuf_cats)
        rng.shuffle(shuf_prefixes)
        rng.shuffle(shuf_suffixes)

        # Build synthetic tokens for property-shuffled null
        synth_tokens = []
        for i in range(n_tok):
            synth = dict(tokens[i])  # shallow copy
            synth['middle'] = shuf_middles[i]
            synth['head'] = shuf_heads[i]
            synth['mods'] = shuf_mods[i]
            synth['term'] = shuf_terms[i]
            synth['category'] = shuf_cats[i]
            synth['prefix'] = shuf_prefixes[i]
            synth['suffix'] = shuf_suffixes[i]
            synth_tokens.append(synth)

        # Metric 1: uses reordered_tokens (sequential)
        null_buffer = metric_buffer_proximity(
            reordered_tokens, forbidden_cat_pairs, adjacent_cat_pairs
        )
        null_metrics['buffer'].append(null_buffer)

        # Metrics 2-5: uses synth_tokens (property-shuffled)
        null_metrics['modifier'].append(metric_modifier_avoidance(synth_tokens))
        null_metrics['opacity'].append(metric_opacity_deviation(synth_tokens))
        null_metrics['pfx_head'].append(
            metric_prefix_head_surprisal(synth_tokens, corpus_ph_rates)
        )
        null_metrics['pfx_mid'].append(
            metric_prefix_middle_surprisal(synth_tokens, corpus_pm_rates)
        )

    # Compute T for each metric
    # All metrics: lower = more rule-compliant
    # T = mean_null / real (T > 1 means real is more compliant than shuffled)
    T_values = {}
    for key in real_metrics:
        real_val = real_metrics[key]
        null_vals = null_metrics[key]
        null_mean = sum(null_vals) / len(null_vals) if null_vals else 0.0

        if real_val > 0 and null_mean > 0:
            T_values[f'T_{key}'] = null_mean / real_val
        elif real_val == 0 and null_mean > 0:
            # Perfect compliance (real=0), set T to high value
            T_values[f'T_{key}'] = null_mean / 1e-6  # cap at large
            T_values[f'T_{key}'] = min(T_values[f'T_{key}'], 100.0)
        elif real_val == 0 and null_mean == 0:
            T_values[f'T_{key}'] = 1.0  # metric not informative
        else:
            # null_mean == 0 but real > 0: grammar is WORSE than random
            T_values[f'T_{key}'] = 0.01  # cap at low

    return T_values, real_metrics


def composite_temperature(T_values):
    """
    Compute composite temperature as geometric mean of individual T values.
    Excludes metrics with T == 1.0 exactly (non-informative).
    """
    valid_Ts = [v for v in T_values.values() if v > 0 and v != 1.0]
    if not valid_Ts:
        # Fall back to arithmetic mean if all are 1.0
        all_Ts = list(T_values.values())
        return sum(all_Ts) / len(all_Ts) if all_Ts else 1.0

    # Geometric mean via log
    log_sum = sum(math.log(t) for t in valid_Ts)
    return math.exp(log_sum / len(valid_Ts))


# ============================================================
# Block 5: Analysis: quire correlation, section stratification
# ============================================================

def section_z_scores(per_folio_data, corpus):
    """
    Section-residualize T_composite: z-score within section.
    Returns: {folio: z_score, ...}
    """
    section_groups = defaultdict(list)
    for folio, data in per_folio_data.items():
        sec = corpus[folio]['section']
        section_groups[sec].append((folio, data['T_composite']))

    z_scores = {}
    for sec, items in section_groups.items():
        vals = [v for _, v in items]
        n = len(vals)
        if n < 2:
            for folio, _ in items:
                z_scores[folio] = 0.0
            continue
        mean = sum(vals) / n
        std = math.sqrt(sum((v - mean) ** 2 for v in vals) / n)
        if std < 1e-12:
            for folio, _ in items:
                z_scores[folio] = 0.0
        else:
            for folio, val in items:
                z_scores[folio] = (val - mean) / std

    return z_scores


def quire_correlation(per_folio_data, corpus, z_scores):
    """
    Compute Spearman rho of T_composite vs quire number.
    Also compute within-section correlations.
    """
    # All folios
    folios = sorted(per_folio_data.keys())
    T_vals = [per_folio_data[f]['T_composite'] for f in folios]
    quires = [corpus[f]['quire'] for f in folios]
    z_vals = [z_scores[f] for f in folios]

    # Global: T vs quire
    rho_all = spearman_rho(T_vals, quires)
    p_all = spearman_p_value(rho_all, len(folios))

    # Global: z-scored T vs quire
    rho_z = spearman_rho(z_vals, quires)
    p_z = spearman_p_value(rho_z, len(folios))

    # Within-section
    section_groups = defaultdict(list)
    for f in folios:
        section_groups[corpus[f]['section']].append(f)

    by_section = {}
    for sec, sec_folios in sorted(section_groups.items()):
        if len(sec_folios) < 4:
            by_section[sec] = {'rho': 0.0, 'p': 1.0, 'n': len(sec_folios)}
            continue
        sec_T = [per_folio_data[f]['T_composite'] for f in sec_folios]
        sec_q = [corpus[f]['quire'] for f in sec_folios]
        rho_sec = spearman_rho(sec_T, sec_q)
        p_sec = spearman_p_value(rho_sec, len(sec_folios))
        by_section[sec] = {'rho': round(rho_sec, 4), 'p': round(p_sec, 6), 'n': len(sec_folios)}

    return {
        'all': {'rho': round(rho_all, 4), 'p_value': round(p_all, 6)},
        'z_residualized': {'rho': round(rho_z, 4), 'p_value': round(p_z, 6)},
        'by_section': by_section,
    }


# ============================================================
# Block 6: Verdict
# ============================================================

def determine_verdict(quire_corr, global_stats, per_folio):
    """
    QUIRE_GRADIENT: z-residualized quire correlation survives (|rho| > 0.25 and p < 0.05)
    SECTION_STRATIFIED: raw quire correlation significant but z-residualized is not
                        (section confound), OR large section T range (> 0.15)
    UNIFORM_TEMPERATURE: no gradient at any level
    """
    rho_all = abs(quire_corr['all']['rho'])
    p_all = quire_corr['all']['p_value']
    rho_z = abs(quire_corr['z_residualized']['rho'])
    p_z = quire_corr['z_residualized']['p_value']

    # Check section stratification
    section_means = global_stats.get('by_section', {})
    if section_means:
        sec_vals = [v['mean'] for v in section_means.values()
                    if 'mean' in v and v.get('n', 0) >= 3]
        if sec_vals:
            sec_range = max(sec_vals) - min(sec_vals)
        else:
            sec_range = 0.0
    else:
        sec_range = 0.0

    # Check within-section gradients
    n_sec_sig = sum(
        1 for sec_data in quire_corr['by_section'].values()
        if sec_data['p'] < 0.05 and abs(sec_data['rho']) > 0.25
    )

    # Priority: z-residualized test is definitive for quire gradient
    if rho_z > 0.25 and p_z < 0.05:
        return 'QUIRE_GRADIENT'
    elif (rho_all > 0.25 and p_all < 0.05 and rho_z < 0.15) or sec_range > 0.15:
        # Raw correlation significant but vanishes after section residualization
        # => section composition drives the apparent gradient
        return 'SECTION_STRATIFIED'
    elif n_sec_sig >= 2:
        return 'SECTION_STRATIFIED'
    else:
        return 'UNIFORM_TEMPERATURE'


def build_predictions(verdict, quire_corr, global_stats):
    """Build predictions dict for downstream use."""
    predictions = {
        'grammar_pre_crystallized': verdict == 'UNIFORM_TEMPERATURE',
        'compositional_drift': verdict == 'QUIRE_GRADIENT',
        'section_drives_temperature': verdict == 'SECTION_STRATIFIED',
        'quire_rho': quire_corr['all']['rho'],
        'quire_p': quire_corr['all']['p_value'],
        'z_residualized_rho': quire_corr['z_residualized']['rho'],
        'z_residualized_p': quire_corr['z_residualized']['p_value'],
    }

    # Mean T across all folios
    T_stats = global_stats.get('T_composite', {})
    predictions['mean_T_composite'] = T_stats.get('mean', 1.0)
    predictions['std_T_composite'] = T_stats.get('std', 0.0)

    # Per-metric mean T
    for key in ['T_buffer', 'T_modifier', 'T_opacity', 'T_pfx_head', 'T_pfx_mid']:
        metric_stats = global_stats.get(key, {})
        predictions[f'mean_{key}'] = metric_stats.get('mean', 1.0)

    return predictions


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 623, Script 5: Grammar Temperature")
    print("=" * 55)

    # Build corpus
    print("\n[1/6] Building corpus...")
    corpus = build_corpus()
    n_folios = len(corpus)
    print(f"  {n_folios} folios")

    # Build per-folio token sequences
    print("\n[2/6] Building per-folio token sequences...")
    folio_seqs = build_folio_token_sequences(corpus)
    total_tokens = sum(len(seq) for seq in folio_seqs.values())
    print(f"  {len(folio_seqs)} folios with tokens, {total_tokens} total tokens")

    # Pre-compute corpus-wide distributions
    print("  Computing corpus-wide prefix-head and prefix-middle rates...")
    corpus_ph_rates = build_corpus_prefix_head_rates(folio_seqs)
    corpus_pm_rates = build_corpus_prefix_middle_rates(folio_seqs)
    print(f"  {len(corpus_ph_rates)} prefix-head pairs, {len(corpus_pm_rates)} prefix-middle pairs")

    print("  Building forbidden category pairs...")
    forbidden_cat_pairs, adjacent_cat_pairs = build_forbidden_category_pairs(folio_seqs)
    print(f"  {len(forbidden_cat_pairs)} forbidden cat pairs, {len(adjacent_cat_pairs)} adjacent cat pairs")

    # Compute temperature per folio
    print(f"\n[3/6] Computing grammar temperature ({N_SHUFFLE} shuffles per folio)...")
    per_folio = {}
    folio_list = sorted(folio_seqs.keys())

    for idx, folio in enumerate(folio_list):
        tokens = folio_seqs[folio]
        T_values, raw_metrics = compute_folio_temperature(
            tokens, forbidden_cat_pairs, adjacent_cat_pairs,
            corpus_ph_rates, corpus_pm_rates, RNG, N_SHUFFLE
        )
        T_comp = composite_temperature(T_values)

        per_folio[folio] = {
            'T_composite': T_comp,
            **T_values,
            'raw_buffer': raw_metrics['buffer'],
            'raw_modifier': raw_metrics['modifier'],
            'raw_opacity': raw_metrics['opacity'],
            'raw_pfx_head': raw_metrics['pfx_head'],
            'raw_pfx_mid': raw_metrics['pfx_mid'],
            'section': corpus[folio]['section'],
            'regime': corpus[folio]['regime'],
            'quire': corpus[folio]['quire'],
            'n_tokens': len(tokens),
        }

        if (idx + 1) % 10 == 0 or idx == 0:
            print(f"  [{idx + 1}/{len(folio_list)}] {folio}: T_composite={T_comp:.3f}")

    # Global statistics
    print(f"\n[4/6] Computing global statistics...")
    metric_keys = ['T_composite', 'T_buffer', 'T_modifier', 'T_opacity', 'T_pfx_head', 'T_pfx_mid']
    global_stats = {}

    for key in metric_keys:
        vals = [per_folio[f][key] for f in folio_list]
        n = len(vals)
        mean_val = sum(vals) / n
        std_val = math.sqrt(sum((v - mean_val) ** 2 for v in vals) / n) if n > 1 else 0.0
        global_stats[key] = {
            'mean': round(mean_val, 4),
            'std': round(std_val, 4),
            'min': round(min(vals), 4),
            'max': round(max(vals), 4),
        }
        print(f"  {key}: mean={mean_val:.4f}, std={std_val:.4f}, "
              f"range=[{min(vals):.4f}, {max(vals):.4f}]")

    # By section
    section_groups = defaultdict(list)
    for f in folio_list:
        section_groups[corpus[f]['section']].append(f)

    by_section = {}
    for sec in sorted(section_groups.keys()):
        sec_folios = section_groups[sec]
        sec_T = [per_folio[f]['T_composite'] for f in sec_folios]
        n = len(sec_T)
        mean_T = sum(sec_T) / n
        std_T = math.sqrt(sum((v - mean_T) ** 2 for v in sec_T) / n) if n > 1 else 0.0
        by_section[sec] = {'mean': round(mean_T, 4), 'std': round(std_T, 4), 'n': n}
        print(f"  Section {sec}: mean={mean_T:.4f}, std={std_T:.4f}, n={n}")

    global_stats['by_section'] = by_section

    # By regime
    regime_groups = defaultdict(list)
    for f in folio_list:
        regime_groups[corpus[f]['regime']].append(f)

    by_regime = {}
    for reg in sorted(regime_groups.keys()):
        reg_folios = regime_groups[reg]
        reg_T = [per_folio[f]['T_composite'] for f in reg_folios]
        n = len(reg_T)
        mean_T = sum(reg_T) / n
        std_T = math.sqrt(sum((v - mean_T) ** 2 for v in reg_T) / n) if n > 1 else 0.0
        by_regime[reg] = {'mean': round(mean_T, 4), 'std': round(std_T, 4), 'n': n}
        print(f"  Regime {reg}: mean={mean_T:.4f}, std={std_T:.4f}, n={n}")

    global_stats['by_regime'] = by_regime

    # Quire correlation
    print(f"\n[5/6] Quire correlation analysis...")
    z_scores = section_z_scores(per_folio, corpus)
    quire_corr = quire_correlation(per_folio, corpus, z_scores)

    print(f"  All folios: rho={quire_corr['all']['rho']}, p={quire_corr['all']['p_value']}")
    print(f"  Z-residualized: rho={quire_corr['z_residualized']['rho']}, "
          f"p={quire_corr['z_residualized']['p_value']}")
    for sec, data in sorted(quire_corr['by_section'].items()):
        print(f"  Section {sec}: rho={data['rho']}, p={data['p']}, n={data['n']}")

    # Verdict
    print(f"\n[6/6] Determining verdict...")
    verdict = determine_verdict(quire_corr, global_stats, per_folio)
    predictions = build_predictions(verdict, quire_corr, global_stats)
    print(f"  VERDICT: {verdict}")

    # Assemble output
    output = {
        'phase': 623,
        'name': 'grammar_temperature',
        'n_folios': len(folio_list),
        'n_shuffle': N_SHUFFLE,
        'forbidden_cat_pairs': len(forbidden_cat_pairs),
        'adjacent_cat_pairs': len(adjacent_cat_pairs),
        'per_folio': round_floats(per_folio),
        'global_stats': round_floats(global_stats),
        'quire_correlation': round_floats(quire_corr),
        'verdict': verdict,
        'predictions': round_floats(predictions),
    }

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'grammar_temperature.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()
