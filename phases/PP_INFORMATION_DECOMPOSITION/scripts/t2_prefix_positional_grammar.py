"""
T2: PREFIX Positional Grammar
==============================
Phase: PP_INFORMATION_DECOMPOSITION

T1 showed PREFIX and MIDDLE carry equal information about line position.
This script maps the full PREFIX positional grammar:

Tests:
  2a: Per-PREFIX continuous position distributions (mean, std, skew)
      KS test: each PREFIX vs corpus-wide distribution
  2b: Pairwise PREFIX position separation (KS + effect size)
  2c: Position zones — do PREFIXes define line-initial / line-final grammar?
  2d: PP positional precision — does (PREFIX, MIDDLE) predict position
      more precisely than either alone? (variance decomposition)

Output: t2_prefix_positional_grammar.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

MIN_TOKENS = 30  # Minimum tokens for a PREFIX to be included in profile


def main():
    morph = Morphology()
    tx = Transcript()

    # ── Single corpus pass ───────────────────────────────
    print("Building positional data...")

    # Pre-compute morphology
    unique_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w and '*' not in w:
            unique_words.add(w)

    word_morph = {}
    for w in unique_words:
        word_morph[w] = morph.extract(w)

    # Group tokens by line
    line_tokens = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        line_tokens[(token.folio, token.line)].append(token)

    # Extract (prefix, middle, continuous_position) per token
    records = []
    for (folio, line), tokens in line_tokens.items():
        n = len(tokens)
        if n < 2:
            continue
        for i, tok in enumerate(tokens):
            w = tok.word.strip()
            m = word_morph.get(w)
            if m is None or not m.middle:
                continue
            prefix = m.prefix or 'BARE'
            middle = m.middle
            pos = i / (n - 1)  # Continuous [0, 1]
            records.append((prefix, middle, pos))

    all_positions = np.array([r[2] for r in records])
    print(f"  Total tokens: {len(records)}")
    print(f"  Mean position: {np.mean(all_positions):.3f}")

    # ══════════════════════════════════════════════════════
    # TEST 2a: PER-PREFIX POSITIONAL PROFILES
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T2a: PREFIX POSITIONAL PROFILES")
    print(f"{'='*70}")

    # Group positions by PREFIX
    prefix_positions = defaultdict(list)
    for prefix, middle, pos in records:
        prefix_positions[prefix].append(pos)

    # Convert to numpy, filter by min tokens
    prefix_arrays = {}
    for prefix, positions in prefix_positions.items():
        if len(positions) >= MIN_TOKENS:
            prefix_arrays[prefix] = np.array(positions)

    print(f"\n  PREFIXes with >={MIN_TOKENS} tokens: {len(prefix_arrays)}")

    print(f"\n  {'PREFIX':<10s} {'N':>6s} {'Mean':>7s} {'Std':>7s} {'Skew':>7s} "
          f"{'Init%':>7s} {'Final%':>7s} {'KS_D':>7s} {'KS_p':>10s}")
    print(f"  {'-'*10} {'-'*6} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*10}")

    prefix_profiles = {}
    for prefix in sorted(prefix_arrays.keys(),
                         key=lambda p: -len(prefix_arrays[p])):
        arr = prefix_arrays[prefix]
        n = len(arr)
        mean_pos = float(np.mean(arr))
        std_pos = float(np.std(arr))
        skew = float(stats.skew(arr))
        init_pct = float(np.mean(arr < 0.15)) * 100  # First 15% of line
        final_pct = float(np.mean(arr > 0.85)) * 100  # Last 15% of line

        # KS test vs corpus-wide distribution
        ks_stat, ks_p = stats.ks_2samp(arr, all_positions)

        prefix_profiles[prefix] = {
            'n': n,
            'mean_position': mean_pos,
            'std_position': std_pos,
            'skew': skew,
            'initial_pct': init_pct,
            'final_pct': final_pct,
            'ks_vs_corpus_D': float(ks_stat),
            'ks_vs_corpus_p': float(ks_p),
        }

        sig = '*' if ks_p < 0.001 else ''
        print(f"  {prefix:<10s} {n:>6d} {mean_pos:>7.3f} {std_pos:>7.3f} "
              f"{skew:>7.3f} {init_pct:>6.1f}% {final_pct:>6.1f}% "
              f"{ks_stat:>7.3f} {ks_p:>10.2e} {sig}")

    # Classify PREFIXes into positional zones
    print(f"\n  POSITIONAL ZONE CLASSIFICATION:")
    zones = {}
    for prefix, prof in prefix_profiles.items():
        if prof['ks_vs_corpus_p'] >= 0.05:
            zone = 'UNIFORM'
        elif prof['mean_position'] < 0.45:
            zone = 'INITIAL_BIASED'
        elif prof['mean_position'] > 0.55:
            zone = 'FINAL_BIASED'
        else:
            zone = 'CENTRAL'
        zones[prefix] = zone
        prefix_profiles[prefix]['zone'] = zone

    for zone_name in ['INITIAL_BIASED', 'CENTRAL', 'FINAL_BIASED', 'UNIFORM']:
        members = [p for p, z in zones.items() if z == zone_name]
        if members:
            print(f"    {zone_name:<18s}: {sorted(members)}")

    # ══════════════════════════════════════════════════════
    # TEST 2b: PAIRWISE PREFIX POSITION SEPARATION
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T2b: PAIRWISE PREFIX POSITION SEPARATION")
    print(f"{'='*70}")

    # Top PREFIXes for pairwise comparison (top 10 by count)
    top_prefixes = sorted(prefix_arrays.keys(),
                          key=lambda p: -len(prefix_arrays[p]))[:10]

    # Kruskal-Wallis across all PREFIXes
    kw_groups = [prefix_arrays[p] for p in top_prefixes]
    H_stat, kw_p = stats.kruskal(*kw_groups)
    N_total = sum(len(g) for g in kw_groups)
    k = len(kw_groups)
    eta_sq = (H_stat - k + 1) / (N_total - k) if N_total > k else 0.0
    eta_sq = max(0.0, eta_sq)

    print(f"\n  Kruskal-Wallis (top 10 PREFIXes): H={H_stat:.2f}, "
          f"p={kw_p:.2e}, eta²={eta_sq:.4f}")

    # Pairwise KS for top pairs
    print(f"\n  Pairwise KS (top 10 PREFIXes, significant only):")
    print(f"  {'A':<8s} {'B':<8s} {'D':>7s} {'p':>10s} {'Delta_mean':>11s}")
    print(f"  {'-'*8} {'-'*8} {'-'*7} {'-'*10} {'-'*11}")

    pairwise_results = {}
    sig_pairs = 0
    for i, p1 in enumerate(top_prefixes):
        for p2 in top_prefixes[i+1:]:
            ks_d, ks_p = stats.ks_2samp(prefix_arrays[p1], prefix_arrays[p2])
            delta_mean = np.mean(prefix_arrays[p1]) - np.mean(prefix_arrays[p2])
            key = f"{p1}_vs_{p2}"
            pairwise_results[key] = {
                'D': float(ks_d), 'p': float(ks_p),
                'delta_mean': float(delta_mean),
            }
            if ks_p < 0.001:
                sig_pairs += 1
                print(f"  {p1:<8s} {p2:<8s} {ks_d:>7.3f} {ks_p:>10.2e} "
                      f"{delta_mean:>+10.3f}")

    total_pairs = len(top_prefixes) * (len(top_prefixes) - 1) // 2
    print(f"\n  Significant pairs (p<0.001): {sig_pairs}/{total_pairs}")

    # ══════════════════════════════════════════════════════
    # TEST 2c: POSITION ZONE SHARPNESS
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T2c: PREFIX POSITION ZONE SHARPNESS")
    print(f"{'='*70}")

    # For each PREFIX, compute concentration in quintiles
    quintile_edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.01]
    quintile_labels = ['Q1(0-20%)', 'Q2(20-40%)', 'Q3(40-60%)',
                       'Q4(60-80%)', 'Q5(80-100%)']

    print(f"\n  {'PREFIX':<10s} {'N':>6s} "
          f"{'Q1':>7s} {'Q2':>7s} {'Q3':>7s} {'Q4':>7s} {'Q5':>7s} "
          f"{'Peak':>10s} {'Conc':>7s}")
    print(f"  {'-'*10} {'-'*6} "
          f"{'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*10} {'-'*7}")

    prefix_quintiles = {}
    for prefix in sorted(prefix_arrays.keys(),
                         key=lambda p: -len(prefix_arrays[p])):
        arr = prefix_arrays[prefix]
        n = len(arr)
        q_counts = np.histogram(arr, bins=quintile_edges)[0]
        q_pcts = q_counts / n * 100

        # Peak quintile and concentration (max% / 20%)
        peak_idx = np.argmax(q_pcts)
        peak_label = quintile_labels[peak_idx]
        concentration = float(q_pcts[peak_idx] / 20.0)  # 1.0 = uniform

        prefix_quintiles[prefix] = {
            'quintile_pcts': [float(p) for p in q_pcts],
            'peak_quintile': peak_label,
            'peak_concentration': concentration,
        }

        print(f"  {prefix:<10s} {n:>6d} "
              f"{q_pcts[0]:>6.1f}% {q_pcts[1]:>6.1f}% {q_pcts[2]:>6.1f}% "
              f"{q_pcts[3]:>6.1f}% {q_pcts[4]:>6.1f}% "
              f"{peak_label:>10s} {concentration:>6.2f}x")

    # ══════════════════════════════════════════════════════
    # TEST 2d: PP POSITIONAL PRECISION (VARIANCE DECOMPOSITION)
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T2d: PP POSITIONAL PRECISION (VARIANCE DECOMPOSITION)")
    print(f"{'='*70}")

    # Use one-hot encoding for PREFIX and MIDDLE
    # Compute R² for: position ~ PREFIX, position ~ MIDDLE, position ~ PP

    # Filter to PREFIXes and MIDDLEs with sufficient data
    prefix_filter = set(prefix_arrays.keys())
    middle_counts = Counter(r[1] for r in records)
    middle_filter = {m for m, c in middle_counts.items() if c >= MIN_TOKENS}

    filt_records = [(p, m, pos) for p, m, pos in records
                    if p in prefix_filter and m in middle_filter]
    print(f"\n  Filtered records: {len(filt_records)} "
          f"(PREFIXes>={MIN_TOKENS}, MIDDLEs>={MIN_TOKENS})")

    # Build vocab indices
    pre_list = sorted(prefix_filter)
    mid_list = sorted(middle_filter)
    pre_idx = {p: i for i, p in enumerate(pre_list)}
    mid_idx = {m: i for i, m in enumerate(mid_list)}

    n_rec = len(filt_records)
    y = np.array([r[2] for r in filt_records])
    y_centered = y - np.mean(y)
    ss_total = float(np.sum(y_centered ** 2))

    # Model 1: PREFIX only (one-hot)
    X_pre = np.zeros((n_rec, len(pre_list)))
    for i, (p, m, pos) in enumerate(filt_records):
        X_pre[i, pre_idx[p]] = 1.0

    # Solve via least squares
    coef_pre, res_pre, _, _ = np.linalg.lstsq(X_pre, y, rcond=None)
    pred_pre = X_pre @ coef_pre
    ss_res_pre = float(np.sum((y - pred_pre) ** 2))
    r2_prefix = 1.0 - ss_res_pre / ss_total

    # Model 2: MIDDLE only (one-hot)
    X_mid = np.zeros((n_rec, len(mid_list)))
    for i, (p, m, pos) in enumerate(filt_records):
        X_mid[i, mid_idx[m]] = 1.0

    coef_mid, res_mid, _, _ = np.linalg.lstsq(X_mid, y, rcond=None)
    pred_mid = X_mid @ coef_mid
    ss_res_mid = float(np.sum((y - pred_mid) ** 2))
    r2_middle = 1.0 - ss_res_mid / ss_total

    # Model 3: PREFIX + MIDDLE (additive, no interaction)
    X_add = np.hstack([X_pre, X_mid])
    coef_add, res_add, _, _ = np.linalg.lstsq(X_add, y, rcond=None)
    pred_add = X_add @ coef_add
    ss_res_add = float(np.sum((y - pred_add) ** 2))
    r2_additive = 1.0 - ss_res_add / ss_total

    # Model 4: Full PP (one indicator per (PREFIX, MIDDLE) pair)
    pp_pairs = sorted({(r[0], r[1]) for r in filt_records})
    pp_idx = {pp: i for i, pp in enumerate(pp_pairs)}
    X_pp = np.zeros((n_rec, len(pp_pairs)))
    for i, (p, m, pos) in enumerate(filt_records):
        if (p, m) in pp_idx:
            X_pp[i, pp_idx[(p, m)]] = 1.0

    coef_pp, res_pp, _, _ = np.linalg.lstsq(X_pp, y, rcond=None)
    pred_pp = X_pp @ coef_pp
    ss_res_pp = float(np.sum((y - pred_pp) ** 2))
    r2_pp = 1.0 - ss_res_pp / ss_total

    # Adjusted R² (penalize for model complexity)
    def adj_r2(r2, n, p):
        return 1 - (1 - r2) * (n - 1) / (n - p - 1) if n > p + 1 else r2

    r2_pre_adj = adj_r2(r2_prefix, n_rec, len(pre_list))
    r2_mid_adj = adj_r2(r2_middle, n_rec, len(mid_list))
    r2_add_adj = adj_r2(r2_additive, n_rec, len(pre_list) + len(mid_list))
    r2_pp_adj = adj_r2(r2_pp, n_rec, len(pp_pairs))

    # Interaction contribution
    r2_interaction = r2_pp - r2_additive

    print(f"\n  {'Model':<25s} {'Params':>7s} {'R²':>8s} {'Adj R²':>8s}")
    print(f"  {'-'*25} {'-'*7} {'-'*8} {'-'*8}")
    print(f"  {'PREFIX only':<25s} {len(pre_list):>7d} {r2_prefix:>8.4f} "
          f"{r2_pre_adj:>8.4f}")
    print(f"  {'MIDDLE only':<25s} {len(mid_list):>7d} {r2_middle:>8.4f} "
          f"{r2_mid_adj:>8.4f}")
    print(f"  {'PREFIX + MIDDLE':<25s} "
          f"{len(pre_list) + len(mid_list):>7d} {r2_additive:>8.4f} "
          f"{r2_add_adj:>8.4f}")
    print(f"  {'Full PP (interaction)':<25s} {len(pp_pairs):>7d} {r2_pp:>8.4f} "
          f"{r2_pp_adj:>8.4f}")

    print(f"\n  Variance decomposition:")
    print(f"    PREFIX alone:          {r2_prefix:.4f}")
    print(f"    MIDDLE alone:          {r2_middle:.4f}")
    print(f"    Additive (PRE+MID):    {r2_additive:.4f}")
    print(f"    + Interaction:         {r2_interaction:+.4f}")
    print(f"    Full PP:               {r2_pp:.4f}")
    print(f"    PREFIX unique:         {r2_additive - r2_middle:.4f}")
    print(f"    MIDDLE unique:         {r2_additive - r2_prefix:.4f}")

    # ── Summary ──────────────────────────────────────────
    non_uniform = sum(1 for p in prefix_profiles.values()
                      if p['ks_vs_corpus_p'] < 0.001)
    total_profiled = len(prefix_profiles)
    initial_biased = [p for p, z in zones.items() if z == 'INITIAL_BIASED']
    final_biased = [p for p, z in zones.items() if z == 'FINAL_BIASED']

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Non-uniform PREFIXes: {non_uniform}/{total_profiled}")
    print(f"  Initial-biased: {initial_biased}")
    print(f"  Final-biased: {final_biased}")
    print(f"  KW eta²: {eta_sq:.4f}")
    print(f"  Significant pairwise separations: {sig_pairs}/{total_pairs}")
    print(f"  R² PREFIX only: {r2_prefix:.4f}")
    print(f"  R² MIDDLE only: {r2_middle:.4f}")
    print(f"  R² Full PP: {r2_pp:.4f}")
    print(f"  Interaction R²: {r2_interaction:.4f}")

    # Verdict
    if non_uniform >= total_profiled * 0.6 and eta_sq > 0.02:
        pos_verdict = 'PREFIX_POSITIONAL_GRAMMAR_CONFIRMED'
        pos_detail = (f'{non_uniform}/{total_profiled} PREFIXes show non-uniform '
                      f'positional profiles (KW eta²={eta_sq:.4f}). '
                      f'PREFIX encodes line position.')
    elif non_uniform >= total_profiled * 0.3:
        pos_verdict = 'PREFIX_POSITIONAL_GRAMMAR_PARTIAL'
        pos_detail = (f'{non_uniform}/{total_profiled} PREFIXes deviate from '
                      f'uniform. Positional grammar exists but is not universal.')
    else:
        pos_verdict = 'NO_POSITIONAL_GRAMMAR'
        pos_detail = (f'Only {non_uniform}/{total_profiled} PREFIXes show '
                      f'non-uniform positions. PREFIX does not encode position.')

    print(f"\n  VERDICT: {pos_verdict}")
    print(f"  {pos_detail}")

    # ── Output ───────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'PP_INFORMATION_DECOMPOSITION',
            'test': 'T2_PREFIX_POSITIONAL_GRAMMAR',
            'min_tokens': MIN_TOKENS,
        },
        'corpus': {
            'total_tokens': len(records),
            'profiled_prefixes': total_profiled,
        },
        'prefix_profiles': prefix_profiles,
        'prefix_quintiles': prefix_quintiles,
        'zones': zones,
        'kruskal_wallis': {
            'H': float(H_stat), 'p': float(kw_p), 'eta_sq': eta_sq,
        },
        'pairwise_significant': sig_pairs,
        'pairwise_total': total_pairs,
        'variance_decomposition': {
            'r2_prefix': r2_prefix,
            'r2_middle': r2_middle,
            'r2_additive': r2_additive,
            'r2_pp': r2_pp,
            'r2_interaction': r2_interaction,
            'r2_prefix_adj': r2_pre_adj,
            'r2_middle_adj': r2_mid_adj,
            'r2_additive_adj': r2_add_adj,
            'r2_pp_adj': r2_pp_adj,
            'prefix_unique': r2_additive - r2_middle,
            'middle_unique': r2_additive - r2_prefix,
        },
        'verdict': pos_verdict,
        'verdict_detail': pos_detail,
    }

    out_path = RESULTS_DIR / 't2_prefix_positional_grammar.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
