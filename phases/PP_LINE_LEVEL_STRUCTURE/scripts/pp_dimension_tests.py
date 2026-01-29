"""
PP_LINE_LEVEL_STRUCTURE - Script 2: Dimension Tests (T4-T8)

Tests morphological dimensions of PP tokens within Currier A lines:
PREFIX-MIDDLE coupling, SUFFIX coherence, diversity scaling,
line-to-line volatility, and folio position trajectory.

Phase: PP_LINE_LEVEL_STRUCTURE
Constraints: C731-C735 (provisional)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import RecordAnalyzer

RESULTS_DIR = Path(__file__).resolve().parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

N_PERM = 1000
rng = np.random.RandomState(42)


def load_data():
    """Pre-compute per-folio, per-line PP structures in O(n)."""
    analyzer = RecordAnalyzer()
    folios = analyzer.get_folios()

    folio_records = {}
    folio_line_pp_mids = {}   # folio -> [[middles per line], ...]
    folio_line_pp_full = {}   # folio -> [[(prefix, middle, suffix), ...], ...]

    for fol in folios:
        records = analyzer.analyze_folio(fol)
        folio_records[fol] = records
        line_mids = []
        line_full = []
        for rec in records:
            mids = []
            full = []
            for t in rec.tokens:
                if t.is_pp and t.middle:
                    mids.append(t.middle)
                    full.append((t.prefix, t.middle, t.suffix))
            line_mids.append(mids)
            line_full.append(full)
        folio_line_pp_mids[fol] = line_mids
        folio_line_pp_full[fol] = line_full

    return folios, folio_records, folio_line_pp_mids, folio_line_pp_full


def shuffle_full_within_folio(folio_line_pp_full, rng):
    """Shuffle full PP token tuples within each folio, preserving line lengths."""
    shuffled = {}
    for fol, line_full_list in folio_line_pp_full.items():
        all_tokens = []
        line_lengths = []
        for line_tokens in line_full_list:
            all_tokens.extend(line_tokens)
            line_lengths.append(len(line_tokens))

        rng.shuffle(all_tokens)

        new_lines = []
        idx = 0
        for length in line_lengths:
            new_lines.append(all_tokens[idx:idx + length])
            idx += length
        shuffled[fol] = new_lines

    return shuffled


def shuffle_mids_within_folio(folio_line_pp_mids, rng):
    """Shuffle PP MIDDLEs within each folio, preserving line lengths."""
    shuffled = {}
    for fol, line_mid_list in folio_line_pp_mids.items():
        all_mids = []
        line_lengths = []
        for line_mids in line_mid_list:
            all_mids.extend(line_mids)
            line_lengths.append(len(line_mids))

        rng.shuffle(all_mids)

        new_lines = []
        idx = 0
        for length in line_lengths:
            new_lines.append(all_mids[idx:idx + length])
            idx += length
        shuffled[fol] = new_lines

    return shuffled


def compute_mi(pair_counts, margin_a, margin_b, total):
    """Compute mutual information from pair counts and marginals."""
    mi = 0.0
    for (a, b), count in pair_counts.items():
        if count == 0:
            continue
        pxy = count / total
        px = margin_a[a] / total
        py = margin_b[b] / total
        if px > 0 and py > 0 and pxy > 0:
            mi += pxy * np.log2(pxy / (px * py))
    return mi


def test_T4(folio_line_pp_full):
    """T4: PREFIX-MIDDLE Cross-Coupling Within Lines.

    Null: PREFIX of token i is independent of MIDDLE of token j (i!=j)
    within a line.
    """
    print("=== T4: PREFIX-MIDDLE Cross-Coupling ===")

    # Collect within-line cross-token (PREFIX_i, MIDDLE_j) pairs
    within_pairs = defaultdict(int)
    within_prefix_margin = defaultdict(int)
    within_middle_margin = defaultdict(int)
    within_total = 0

    for fol, line_full_list in folio_line_pp_full.items():
        for line_tokens in line_full_list:
            if len(line_tokens) < 2:
                continue
            for i, (pi, mi, si) in enumerate(line_tokens):
                for j, (pj, mj, sj) in enumerate(line_tokens):
                    if i == j:
                        continue
                    prefix = pi if pi else '_NONE_'
                    middle = mj
                    within_pairs[(prefix, middle)] += 1
                    within_prefix_margin[prefix] += 1
                    within_middle_margin[middle] += 1
                    within_total += 1

    obs_mi = compute_mi(within_pairs, within_prefix_margin, within_middle_margin, within_total)
    print(f"Within-line MI(PREFIX; MIDDLE): {obs_mi:.6f}")
    print(f"Within-line cross-token pairs: {within_total}")

    # Between-line baseline (same folio, different lines)
    between_pairs = defaultdict(int)
    between_prefix_margin = defaultdict(int)
    between_middle_margin = defaultdict(int)
    between_total = 0

    for fol, line_full_list in folio_line_pp_full.items():
        lines_with_pp = [l for l in line_full_list if len(l) >= 1]
        if len(lines_with_pp) < 2:
            continue
        # Sample pairs from different lines (up to 100 random pairings per folio)
        n_lines = len(lines_with_pp)
        n_sample = min(100, n_lines * (n_lines - 1) // 2)
        sampled = set()
        attempts = 0
        while len(sampled) < n_sample and attempts < n_sample * 5:
            i = rng.randint(n_lines)
            j = rng.randint(n_lines)
            if i != j and (i, j) not in sampled:
                sampled.add((i, j))
                for (pi, mi, si) in lines_with_pp[i]:
                    for (pj, mj, sj) in lines_with_pp[j]:
                        prefix = pi if pi else '_NONE_'
                        middle = mj
                        between_pairs[(prefix, middle)] += 1
                        between_prefix_margin[prefix] += 1
                        between_middle_margin[middle] += 1
                        between_total += 1
            attempts += 1

    between_mi = compute_mi(between_pairs, between_prefix_margin, between_middle_margin, between_total)
    mi_ratio = obs_mi / between_mi if between_mi > 0 else float('inf')
    print(f"Between-line MI(PREFIX; MIDDLE): {between_mi:.6f}")
    print(f"MI ratio (within/between): {mi_ratio:.4f}")

    # Permutation test: shuffle PP tokens across lines within folio
    null_mi = []
    for i in range(N_PERM):
        shuffled = shuffle_full_within_folio(folio_line_pp_full, rng)
        # Compute within-line MI on shuffled data
        perm_pairs = defaultdict(int)
        perm_prefix = defaultdict(int)
        perm_middle = defaultdict(int)
        perm_total = 0
        for fol, line_full_list in shuffled.items():
            for line_tokens in line_full_list:
                if len(line_tokens) < 2:
                    continue
                for ii, (pi, mi_tok, si) in enumerate(line_tokens):
                    for jj, (pj, mj, sj) in enumerate(line_tokens):
                        if ii == jj:
                            continue
                        prefix = pi if pi else '_NONE_'
                        middle = mj
                        perm_pairs[(prefix, middle)] += 1
                        perm_prefix[prefix] += 1
                        perm_middle[middle] += 1
                        perm_total += 1
        perm_mi = compute_mi(perm_pairs, perm_prefix, perm_middle, perm_total)
        null_mi.append(perm_mi)
        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    null_mi = np.array(null_mi)
    p_mi = float(np.mean(null_mi >= obs_mi))

    t4_pass = mi_ratio > 1.2 and p_mi < 0.01

    result = {
        'test': 'T4_prefix_middle_coupling',
        'within_line_MI': float(obs_mi),
        'between_line_MI': float(between_mi),
        'MI_ratio': float(mi_ratio),
        'within_total_pairs': within_total,
        'between_total_pairs': between_total,
        'null_MI_mean': float(np.mean(null_mi)),
        'null_MI_std': float(np.std(null_mi)),
        'p_MI': p_mi,
        'PASS': t4_pass,
        'verdict': 'PASS' if t4_pass else 'FAIL'
    }

    print(f"Null MI: {np.mean(null_mi):.6f} +/- {np.std(null_mi):.6f}")
    print(f"p_MI: {p_mi:.4f}")
    print(f"T4 verdict: {'PASS' if t4_pass else 'FAIL'}")

    return result


def test_T5(folio_line_pp_full):
    """T5: PP SUFFIX Coherence Within Lines.

    Null: PP SUFFIX distribution within lines matches folio-level expectation.
    """
    print("\n=== T5: PP SUFFIX Coherence ===")

    # For each line with 2+ PP tokens: pairwise SUFFIX match rate
    obs_matches = 0
    obs_pairs_total = 0

    # Also compute folio-level expected match rate
    folio_suffix_freqs = {}
    for fol, line_full_list in folio_line_pp_full.items():
        suffix_counts = Counter()
        total = 0
        for line_tokens in line_full_list:
            for (p, m, s) in line_tokens:
                suf = s if s else '_NONE_'
                suffix_counts[suf] += 1
                total += 1
        if total > 0:
            folio_suffix_freqs[fol] = {s: c / total for s, c in suffix_counts.items()}
        else:
            folio_suffix_freqs[fol] = {}

    # Compute observed pairwise match rate
    folio_obs_data = {}  # per-folio stats
    for fol, line_full_list in folio_line_pp_full.items():
        fol_matches = 0
        fol_pairs = 0
        for line_tokens in line_full_list:
            if len(line_tokens) < 2:
                continue
            suffixes = [s if s else '_NONE_' for (p, m, s) in line_tokens]
            for i in range(len(suffixes)):
                for j in range(i + 1, len(suffixes)):
                    fol_pairs += 1
                    obs_pairs_total += 1
                    if suffixes[i] == suffixes[j]:
                        fol_matches += 1
                        obs_matches += 1
        folio_obs_data[fol] = (fol_matches, fol_pairs)

    obs_match_rate = obs_matches / obs_pairs_total if obs_pairs_total > 0 else 0

    # Expected match rate: sum of squared folio-level suffix frequencies
    expected_rates = []
    for fol, freqs in folio_suffix_freqs.items():
        if freqs:
            expected_rates.append(sum(f ** 2 for f in freqs.values()))
    mean_expected = float(np.mean(expected_rates)) if expected_rates else 0

    ratio = obs_match_rate / mean_expected if mean_expected > 0 else 0
    print(f"Observed SUFFIX match rate: {obs_match_rate:.4f}")
    print(f"Expected (folio-level): {mean_expected:.4f}")
    print(f"Ratio: {ratio:.4f}")

    # Permutation test
    null_match_rates = []
    for i in range(N_PERM):
        shuffled = shuffle_full_within_folio(folio_line_pp_full, rng)
        perm_matches = 0
        perm_pairs = 0
        for fol, line_full_list in shuffled.items():
            for line_tokens in line_full_list:
                if len(line_tokens) < 2:
                    continue
                suffixes = [s if s else '_NONE_' for (p, m, s) in line_tokens]
                for ii in range(len(suffixes)):
                    for jj in range(ii + 1, len(suffixes)):
                        perm_pairs += 1
                        if suffixes[ii] == suffixes[jj]:
                            perm_matches += 1
        null_match_rates.append(perm_matches / perm_pairs if perm_pairs > 0 else 0)
        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    null_match_rates = np.array(null_match_rates)
    p_suffix = float(np.mean(null_match_rates >= obs_match_rate))

    t5_pass = ratio > 1.3 and p_suffix < 0.01

    result = {
        'test': 'T5_suffix_coherence',
        'observed_match_rate': float(obs_match_rate),
        'expected_match_rate': float(mean_expected),
        'ratio': float(ratio),
        'total_pairs': obs_pairs_total,
        'total_matches': obs_matches,
        'null_match_rate_mean': float(np.mean(null_match_rates)),
        'null_match_rate_std': float(np.std(null_match_rates)),
        'p_suffix': p_suffix,
        'PASS': t5_pass,
        'verdict': 'PASS' if t5_pass else 'FAIL'
    }

    print(f"Null match rate: {np.mean(null_match_rates):.4f} +/- {np.std(null_match_rates):.4f}")
    print(f"p_suffix: {p_suffix:.4f}")
    print(f"T5 verdict: {'PASS' if t5_pass else 'FAIL'}")

    return result


def test_T6(folio_line_pp_mids):
    """T6: PP Diversity Scaling.

    Null: Unique PP MIDDLEs per line follows hypergeometric expectation.
    """
    print("\n=== T6: PP Diversity Scaling ===")

    # For each line: total PP tokens (k), unique MIDDLEs (u)
    # For each folio: pool size N, each MIDDLE's frequency
    residuals = []

    for fol, line_mid_list in folio_line_pp_mids.items():
        # Folio pool
        all_mids = []
        for line_mids in line_mid_list:
            all_mids.extend(line_mids)

        if not all_mids:
            continue

        pool_total = len(all_mids)
        mid_counts = Counter(all_mids)
        pool_types = len(mid_counts)

        for line_mids in line_mid_list:
            k = len(line_mids)
            if k < 2:
                continue
            u = len(set(line_mids))

            # Expected unique count: E[unique in k draws without replacement from pool]
            # = N_types - sum_i (C(pool_total - count_i, k) / C(pool_total, k))
            # Approximation using inclusion-exclusion:
            # E[unique] = sum_i (1 - C(pool_total - count_i, k) / C(pool_total, k))
            # Use log-space for numerical stability
            from scipy.special import comb
            expected_u = 0.0
            for mid, count in mid_counts.items():
                # P(mid not drawn in k draws) = C(pool_total - count, k) / C(pool_total, k)
                not_drawn = comb(pool_total - count, k, exact=False) / comb(pool_total, k, exact=False)
                expected_u += (1.0 - not_drawn)

            residuals.append(u - expected_u)

    residuals = np.array(residuals)
    mean_residual = float(np.mean(residuals))
    std_residual = float(np.std(residuals))
    effect_size = abs(mean_residual) / std_residual if std_residual > 0 else 0

    print(f"Lines analyzed: {len(residuals)}")
    print(f"Mean residual (obs - expected): {mean_residual:.4f}")
    print(f"SD residual: {std_residual:.4f}")
    print(f"Effect size |mean|/SD: {effect_size:.4f}")

    # Bootstrap CI
    n_boot = 5000
    boot_means = []
    for i in range(n_boot):
        sample = rng.choice(residuals, size=len(residuals), replace=True)
        boot_means.append(float(np.mean(sample)))

    boot_means = np.array(boot_means)
    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))
    ci_excludes_zero = ci_lower > 0 or ci_upper < 0

    t6_pass = ci_excludes_zero and effect_size > 0.2

    result = {
        'test': 'T6_diversity_scaling',
        'n_lines': len(residuals),
        'mean_residual': mean_residual,
        'std_residual': std_residual,
        'effect_size': effect_size,
        'bootstrap_CI_95': [ci_lower, ci_upper],
        'CI_excludes_zero': ci_excludes_zero,
        'direction': 'MORE_DIVERSE' if mean_residual > 0 else 'LESS_DIVERSE',
        'PASS': t6_pass,
        'verdict': 'PASS' if t6_pass else 'FAIL'
    }

    print(f"Bootstrap 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    print(f"CI excludes zero: {ci_excludes_zero}")
    print(f"Direction: {'MORE diverse' if mean_residual > 0 else 'LESS diverse'} than expected")
    print(f"T6 verdict: {'PASS' if t6_pass else 'FAIL'}")

    return result


def test_T7(folio_line_pp_mids):
    """T7: Line-to-Line PP Volatility.

    Null: Adjacent lines have no more PP MIDDLE overlap than non-adjacent.
    """
    print("\n=== T7: Line-to-Line PP Volatility ===")

    # Compute pairwise Jaccard for all line pairs within each folio
    adjacent_jaccards = []
    nonadjacent_jaccards = []

    for fol, line_mid_list in folio_line_pp_mids.items():
        # Convert to frozensets, skip empty lines
        line_sets = []
        for line_mids in line_mid_list:
            s = frozenset(line_mids)
            line_sets.append(s)

        n = len(line_sets)
        if n < 2:
            continue

        for i in range(n):
            if not line_sets[i]:
                continue
            for j in range(i + 1, n):
                if not line_sets[j]:
                    continue
                intersection = len(line_sets[i] & line_sets[j])
                union = len(line_sets[i] | line_sets[j])
                if union == 0:
                    continue
                jacc = intersection / union
                if j == i + 1:
                    adjacent_jaccards.append(jacc)
                else:
                    nonadjacent_jaccards.append(jacc)

    adj_mean = float(np.mean(adjacent_jaccards)) if adjacent_jaccards else 0
    nonadj_mean = float(np.mean(nonadjacent_jaccards)) if nonadjacent_jaccards else 0
    ratio = adj_mean / nonadj_mean if nonadj_mean > 0 else float('inf')

    print(f"Adjacent line pairs: {len(adjacent_jaccards)}, mean Jaccard: {adj_mean:.4f}")
    print(f"Non-adjacent pairs: {len(nonadjacent_jaccards)}, mean Jaccard: {nonadj_mean:.4f}")
    print(f"Adjacent/non-adjacent ratio: {ratio:.4f}")

    # Permutation test: shuffle line order within folio
    null_ratios = []
    for i in range(N_PERM):
        perm_adj = []
        perm_nonadj = []
        for fol, line_mid_list in folio_line_pp_mids.items():
            line_sets = [frozenset(lm) for lm in line_mid_list]
            n = len(line_sets)
            if n < 2:
                continue
            # Shuffle line order
            perm_order = rng.permutation(n)
            shuffled_sets = [line_sets[idx] for idx in perm_order]
            for ii in range(n):
                if not shuffled_sets[ii]:
                    continue
                for jj in range(ii + 1, n):
                    if not shuffled_sets[jj]:
                        continue
                    intersection = len(shuffled_sets[ii] & shuffled_sets[jj])
                    union = len(shuffled_sets[ii] | shuffled_sets[jj])
                    if union == 0:
                        continue
                    jacc = intersection / union
                    if jj == ii + 1:
                        perm_adj.append(jacc)
                    else:
                        perm_nonadj.append(jacc)

        pa = float(np.mean(perm_adj)) if perm_adj else 0
        pna = float(np.mean(perm_nonadj)) if perm_nonadj else 0
        null_ratios.append(pa / pna if pna > 0 else 0)
        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    null_ratios = np.array(null_ratios)
    p_volatility = float(np.mean(null_ratios >= ratio))

    t7_pass = ratio > 1.1 and p_volatility < 0.05

    result = {
        'test': 'T7_pp_volatility',
        'adjacent_pairs': len(adjacent_jaccards),
        'nonadjacent_pairs': len(nonadjacent_jaccards),
        'adjacent_mean_jaccard': adj_mean,
        'nonadjacent_mean_jaccard': nonadj_mean,
        'ratio': float(ratio),
        'null_ratio_mean': float(np.mean(null_ratios)),
        'null_ratio_std': float(np.std(null_ratios)),
        'p_volatility': p_volatility,
        'PASS': t7_pass,
        'verdict': 'PASS' if t7_pass else 'FAIL'
    }

    print(f"Null ratio: {np.mean(null_ratios):.4f} +/- {np.std(null_ratios):.4f}")
    print(f"p_volatility: {p_volatility:.4f}")
    print(f"T7 verdict: {'PASS' if t7_pass else 'FAIL'}")

    return result


def test_T8(folio_line_pp_mids):
    """T8: PP Composition by Folio Position.

    Null: PP composition does not vary by position within a folio.
    """
    print("\n=== T8: PP Composition by Folio Position ===")

    def js_divergence(p, q):
        """Jensen-Shannon divergence between two distributions."""
        # Align keys
        all_keys = set(p.keys()) | set(q.keys())
        pv = np.array([p.get(k, 0) for k in all_keys], dtype=float)
        qv = np.array([q.get(k, 0) for k in all_keys], dtype=float)

        # Normalize
        pv_sum = pv.sum()
        qv_sum = qv.sum()
        if pv_sum == 0 or qv_sum == 0:
            return 0.0
        pv = pv / pv_sum
        qv = qv / qv_sum

        m = 0.5 * (pv + qv)
        # KL divergence with zero handling
        kl_pm = 0.0
        kl_qm = 0.0
        for i in range(len(pv)):
            if pv[i] > 0 and m[i] > 0:
                kl_pm += pv[i] * np.log2(pv[i] / m[i])
            if qv[i] > 0 and m[i] > 0:
                kl_qm += qv[i] * np.log2(qv[i] / m[i])
        return 0.5 * (kl_pm + kl_qm)

    def compute_folio_js(folio_line_pp_mids):
        """Compute early-late JS divergence for each folio."""
        early_late_js = []
        within_js = []

        for fol, line_mid_list in folio_line_pp_mids.items():
            n = len(line_mid_list)
            if n < 3:
                continue

            # Divide into thirds
            third = n // 3
            if third == 0:
                continue
            early = line_mid_list[:third]
            late = line_mid_list[-third:]

            # Build frequency vectors
            early_freq = Counter()
            for lm in early:
                early_freq.update(lm)
            late_freq = Counter()
            for lm in late:
                late_freq.update(lm)

            if not early_freq or not late_freq:
                continue

            el_js = js_divergence(early_freq, late_freq)
            early_late_js.append(el_js)

            # Within-third JS: compare first half vs second half of early third
            if third >= 2:
                half = third // 2
                if half > 0:
                    e1 = Counter()
                    for lm in early[:half]:
                        e1.update(lm)
                    e2 = Counter()
                    for lm in early[half:]:
                        e2.update(lm)
                    if e1 and e2:
                        within_js.append(js_divergence(e1, e2))

        return early_late_js, within_js

    obs_el_js, obs_within_js = compute_folio_js(folio_line_pp_mids)

    if not obs_el_js:
        print("Insufficient data for folio position analysis")
        return {
            'test': 'T8_folio_position',
            'PASS': False,
            'verdict': 'FAIL (insufficient data)'
        }

    obs_el_mean = float(np.mean(obs_el_js))
    obs_within_mean = float(np.mean(obs_within_js)) if obs_within_js else 0.001
    obs_ratio = obs_el_mean / obs_within_mean if obs_within_mean > 0 else float('inf')

    print(f"Early-late JS mean: {obs_el_mean:.6f}")
    print(f"Within-third JS mean: {obs_within_mean:.6f}")
    print(f"Ratio (early-late / within): {obs_ratio:.4f}")

    # Permutation test: shuffle line order within folio
    null_ratios = []
    for i in range(N_PERM):
        # Shuffle line order within each folio
        shuffled_mids = {}
        for fol, line_mid_list in folio_line_pp_mids.items():
            perm_order = rng.permutation(len(line_mid_list))
            shuffled_mids[fol] = [line_mid_list[idx] for idx in perm_order]

        perm_el, perm_within = compute_folio_js(shuffled_mids)
        if perm_el:
            pe = float(np.mean(perm_el))
            pw = float(np.mean(perm_within)) if perm_within else 0.001
            null_ratios.append(pe / pw if pw > 0 else 0)
        if (i + 1) % 100 == 0:
            print(f"  Permutation {i + 1}/{N_PERM}")

    null_ratios = np.array(null_ratios)
    p_position = float(np.mean(null_ratios >= obs_ratio))

    t8_pass = obs_ratio > 1.5 and p_position < 0.05

    result = {
        'test': 'T8_folio_position',
        'n_folios_analyzed': len(obs_el_js),
        'early_late_JS_mean': obs_el_mean,
        'within_third_JS_mean': obs_within_mean,
        'ratio': float(obs_ratio),
        'null_ratio_mean': float(np.mean(null_ratios)),
        'null_ratio_std': float(np.std(null_ratios)),
        'p_position': p_position,
        'PASS': t8_pass,
        'verdict': 'PASS' if t8_pass else 'FAIL'
    }

    print(f"Null ratio: {np.mean(null_ratios):.4f} +/- {np.std(null_ratios):.4f}")
    print(f"p_position: {p_position:.4f}")
    print(f"T8 verdict: {'PASS' if t8_pass else 'FAIL'}")

    return result


def main():
    print("PP_LINE_LEVEL_STRUCTURE - Script 2: Dimension Tests")
    print("=" * 60)

    print("\nLoading data...")
    folios, folio_records, folio_line_pp_mids, folio_line_pp_full = load_data()

    # Summary
    total_pp = sum(len(l) for v in folio_line_pp_mids.values() for l in v)
    print(f"Folios: {len(folios)}")
    print(f"Total PP token occurrences: {total_pp}")

    results = {}

    # T4: PREFIX-MIDDLE cross-coupling
    results['T4_prefix_middle_coupling'] = test_T4(folio_line_pp_full)

    # T5: SUFFIX coherence
    results['T5_suffix_coherence'] = test_T5(folio_line_pp_full)

    # T6: Diversity scaling
    results['T6_diversity_scaling'] = test_T6(folio_line_pp_mids)

    # T7: Line-to-line volatility
    results['T7_pp_volatility'] = test_T7(folio_line_pp_mids)

    # T8: Folio position trajectory
    results['T8_folio_position'] = test_T8(folio_line_pp_mids)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for key in ['T4_prefix_middle_coupling', 'T5_suffix_coherence',
                'T6_diversity_scaling', 'T7_pp_volatility', 'T8_folio_position']:
        r = results[key]
        print(f"  {key}: {r['verdict']}")

    # Save
    output_path = RESULTS_DIR / 'pp_dimension_tests.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
