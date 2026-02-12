"""
T1: Full Suffix Positional Census
=================================
Phase: SUFFIX_POSITIONAL_STATE_MAPPING

Maps all 38 suffixes to continuous line-position distributions.
Parallels C1001 T2 (PREFIX positional grammar) for SUFFIX.

Tests:
  1a: Per-suffix positional profiles (mean, std, skew, KS vs corpus)
  1b: Kruskal-Wallis across top suffixes + pairwise separation
  1c: Quintile concentration (zone classification)
  1d: Variance decomposition: SUFFIX vs PREFIX vs MIDDLE for position

Pass criterion: 15+ suffixes non-uniform (KS p<0.001/38)
Fail criterion: <8 non-uniform

Output: t1_suffix_positional_census.json
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

MIN_TOKENS = 30
BONFERRONI_ALPHA = 0.001  # Base alpha before correction


def main():
    morph = Morphology()
    tx = Transcript()

    # ── Single corpus pass ───────────────────────────────
    print("Building positional data...")

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

    # Extract (prefix, middle, suffix, continuous_position) per token
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
            suffix = m.suffix or 'NONE'
            pos = i / (n - 1)
            records.append((prefix, middle, suffix, pos))

    all_positions = np.array([r[3] for r in records])
    print(f"  Total tokens: {len(records)}")
    print(f"  Mean position: {np.mean(all_positions):.3f}")

    # ══════════════════════════════════════════════════════
    # TEST 1a: PER-SUFFIX POSITIONAL PROFILES
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T1a: SUFFIX POSITIONAL PROFILES")
    print(f"{'='*70}")

    suffix_positions = defaultdict(list)
    for prefix, middle, suffix, pos in records:
        suffix_positions[suffix].append(pos)

    suffix_arrays = {}
    for suffix, positions in suffix_positions.items():
        if len(positions) >= MIN_TOKENS:
            suffix_arrays[suffix] = np.array(positions)

    n_testable = len(suffix_arrays)
    bonf_threshold = BONFERRONI_ALPHA / n_testable
    print(f"\n  Suffixes with >={MIN_TOKENS} tokens: {n_testable}")
    print(f"  Bonferroni threshold: p < {bonf_threshold:.2e}")

    print(f"\n  {'SUFFIX':<10s} {'N':>6s} {'Mean':>7s} {'Std':>7s} {'Skew':>7s} "
          f"{'Init%':>7s} {'Final%':>7s} {'KS_D':>7s} {'KS_p':>10s}")
    print(f"  {'-'*10} {'-'*6} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*10}")

    suffix_profiles = {}
    non_uniform_count = 0
    for suffix in sorted(suffix_arrays.keys(),
                         key=lambda s: -len(suffix_arrays[s])):
        arr = suffix_arrays[suffix]
        n = len(arr)
        mean_pos = float(np.mean(arr))
        std_pos = float(np.std(arr))
        skew = float(stats.skew(arr))
        init_pct = float(np.mean(arr < 0.15)) * 100
        final_pct = float(np.mean(arr > 0.85)) * 100

        ks_stat, ks_p = stats.ks_2samp(arr, all_positions)
        is_non_uniform = ks_p < bonf_threshold
        if is_non_uniform:
            non_uniform_count += 1

        suffix_profiles[suffix] = {
            'n': n,
            'mean_position': mean_pos,
            'std_position': std_pos,
            'skew': skew,
            'initial_pct': init_pct,
            'final_pct': final_pct,
            'ks_vs_corpus_D': float(ks_stat),
            'ks_vs_corpus_p': float(ks_p),
            'non_uniform': bool(is_non_uniform),
        }

        sig = '*' if is_non_uniform else ''
        print(f"  {suffix:<10s} {n:>6d} {mean_pos:>7.3f} {std_pos:>7.3f} "
              f"{skew:>7.3f} {init_pct:>6.1f}% {final_pct:>6.1f}% "
              f"{ks_stat:>7.3f} {ks_p:>10.2e} {sig}")

    print(f"\n  Non-uniform suffixes: {non_uniform_count}/{n_testable}")

    # Zone classification
    zones = {}
    for suffix, prof in suffix_profiles.items():
        if not prof['non_uniform']:
            zone = 'UNIFORM'
        elif prof['mean_position'] < 0.45:
            zone = 'INITIAL_BIASED'
        elif prof['mean_position'] > 0.55:
            zone = 'FINAL_BIASED'
        else:
            zone = 'CENTRAL'
        zones[suffix] = zone
        suffix_profiles[suffix]['zone'] = zone

    print(f"\n  POSITIONAL ZONE CLASSIFICATION:")
    for zone_name in ['INITIAL_BIASED', 'CENTRAL', 'FINAL_BIASED', 'UNIFORM']:
        members = sorted([s for s, z in zones.items() if z == zone_name],
                         key=lambda s: suffix_profiles[s]['mean_position'])
        if members:
            display = [f"{s}({suffix_profiles[s]['mean_position']:.2f})" for s in members]
            print(f"    {zone_name:<18s}: {', '.join(display)}")

    # ══════════════════════════════════════════════════════
    # TEST 1b: KRUSKAL-WALLIS + PAIRWISE SEPARATION
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T1b: PAIRWISE SUFFIX POSITION SEPARATION")
    print(f"{'='*70}")

    top_suffixes = sorted(suffix_arrays.keys(),
                          key=lambda s: -len(suffix_arrays[s]))[:10]

    kw_groups = [suffix_arrays[s] for s in top_suffixes]
    H_stat, kw_p = stats.kruskal(*kw_groups)
    N_total = sum(len(g) for g in kw_groups)
    k = len(kw_groups)
    eta_sq = max(0.0, (H_stat - k + 1) / (N_total - k)) if N_total > k else 0.0

    print(f"\n  Kruskal-Wallis (top 10 suffixes): H={H_stat:.2f}, "
          f"p={kw_p:.2e}, eta²={eta_sq:.4f}")

    # Pairwise KS
    sig_pairs = 0
    total_pairs = k * (k - 1) // 2
    pairwise_results = {}

    print(f"\n  Pairwise KS (top 10, significant only):")
    print(f"  {'A':<8s} {'B':<8s} {'D':>7s} {'p':>10s} {'Delta_mean':>11s}")
    print(f"  {'-'*8} {'-'*8} {'-'*7} {'-'*10} {'-'*11}")

    for i, s1 in enumerate(top_suffixes):
        for s2 in top_suffixes[i+1:]:
            ks_d, ks_p_val = stats.ks_2samp(suffix_arrays[s1], suffix_arrays[s2])
            delta_mean = np.mean(suffix_arrays[s1]) - np.mean(suffix_arrays[s2])
            key = f"{s1}_vs_{s2}"
            pairwise_results[key] = {
                'D': float(ks_d), 'p': float(ks_p_val),
                'delta_mean': float(delta_mean),
            }
            if ks_p_val < 0.001:
                sig_pairs += 1
                print(f"  {s1:<8s} {s2:<8s} {ks_d:>7.3f} {ks_p_val:>10.2e} "
                      f"{delta_mean:>+10.3f}")

    print(f"\n  Significant pairs (p<0.001): {sig_pairs}/{total_pairs}")

    # ══════════════════════════════════════════════════════
    # TEST 1c: QUINTILE CONCENTRATION
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T1c: SUFFIX QUINTILE CONCENTRATION")
    print(f"{'='*70}")

    quintile_edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.01]
    quintile_labels = ['Q1(0-20%)', 'Q2(20-40%)', 'Q3(40-60%)',
                       'Q4(60-80%)', 'Q5(80-100%)']

    print(f"\n  {'SUFFIX':<10s} {'N':>6s} "
          f"{'Q1':>7s} {'Q2':>7s} {'Q3':>7s} {'Q4':>7s} {'Q5':>7s} "
          f"{'Peak':>10s} {'Conc':>7s}")
    print(f"  {'-'*10} {'-'*6} "
          f"{'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*10} {'-'*7}")

    suffix_quintiles = {}
    for suffix in sorted(suffix_arrays.keys(),
                         key=lambda s: -len(suffix_arrays[s])):
        arr = suffix_arrays[suffix]
        n = len(arr)
        q_counts = np.histogram(arr, bins=quintile_edges)[0]
        q_pcts = q_counts / n * 100

        peak_idx = int(np.argmax(q_pcts))
        peak_label = quintile_labels[peak_idx]
        concentration = float(q_pcts[peak_idx] / 20.0)

        suffix_quintiles[suffix] = {
            'quintile_pcts': [float(p) for p in q_pcts],
            'peak_quintile': peak_label,
            'peak_concentration': concentration,
        }

        print(f"  {suffix:<10s} {n:>6d} "
              f"{q_pcts[0]:>6.1f}% {q_pcts[1]:>6.1f}% {q_pcts[2]:>6.1f}% "
              f"{q_pcts[3]:>6.1f}% {q_pcts[4]:>6.1f}% "
              f"{peak_label:>10s} {concentration:>6.2f}x")

    # ══════════════════════════════════════════════════════
    # TEST 1d: VARIANCE DECOMPOSITION (SUFFIX vs PREFIX vs MIDDLE)
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T1d: POSITION VARIANCE DECOMPOSITION")
    print(f"{'='*70}")

    prefix_counts = Counter(r[0] for r in records)
    middle_counts = Counter(r[1] for r in records)
    suffix_count_map = Counter(r[2] for r in records)

    prefix_filter = {p for p, c in prefix_counts.items() if c >= MIN_TOKENS}
    middle_filter = {m for m, c in middle_counts.items() if c >= MIN_TOKENS}
    suffix_filter = {s for s, c in suffix_count_map.items() if c >= MIN_TOKENS}

    filt_records = [(p, m, s, pos) for p, m, s, pos in records
                    if p in prefix_filter and m in middle_filter and s in suffix_filter]
    print(f"\n  Filtered records: {len(filt_records)}")

    pre_list = sorted(prefix_filter)
    mid_list = sorted(middle_filter)
    suf_list = sorted(suffix_filter)
    pre_idx = {p: i for i, p in enumerate(pre_list)}
    mid_idx = {m: i for i, m in enumerate(mid_list)}
    suf_idx = {s: i for i, s in enumerate(suf_list)}

    n_rec = len(filt_records)
    y = np.array([r[3] for r in filt_records])
    y_mean = np.mean(y)
    ss_total = float(np.sum((y - y_mean) ** 2))

    def compute_r2(X, y_arr, ss_tot):
        coef, _, _, _ = np.linalg.lstsq(X, y_arr, rcond=None)
        pred = X @ coef
        ss_res = float(np.sum((y_arr - pred) ** 2))
        return 1.0 - ss_res / ss_tot

    def adj_r2(r2, n, p):
        return 1 - (1 - r2) * (n - 1) / (n - p - 1) if n > p + 1 else r2

    # Model: PREFIX only
    X_pre = np.zeros((n_rec, len(pre_list)))
    for i, (p, m, s, pos) in enumerate(filt_records):
        X_pre[i, pre_idx[p]] = 1.0
    r2_prefix = compute_r2(X_pre, y, ss_total)

    # Model: MIDDLE only
    X_mid = np.zeros((n_rec, len(mid_list)))
    for i, (p, m, s, pos) in enumerate(filt_records):
        X_mid[i, mid_idx[m]] = 1.0
    r2_middle = compute_r2(X_mid, y, ss_total)

    # Model: SUFFIX only
    X_suf = np.zeros((n_rec, len(suf_list)))
    for i, (p, m, s, pos) in enumerate(filt_records):
        X_suf[i, suf_idx[s]] = 1.0
    r2_suffix = compute_r2(X_suf, y, ss_total)

    # Model: PREFIX + SUFFIX (additive)
    X_ps = np.hstack([X_pre, X_suf])
    r2_pre_suf = compute_r2(X_ps, y, ss_total)

    # Model: PREFIX + MIDDLE (additive) -- C1001 baseline
    X_pm = np.hstack([X_pre, X_mid])
    r2_pre_mid = compute_r2(X_pm, y, ss_total)

    # Model: SUFFIX + MIDDLE (additive)
    X_sm = np.hstack([X_suf, X_mid])
    r2_suf_mid = compute_r2(X_sm, y, ss_total)

    # Model: PREFIX + MIDDLE + SUFFIX (additive)
    X_all = np.hstack([X_pre, X_mid, X_suf])
    r2_all = compute_r2(X_all, y, ss_total)

    print(f"\n  {'Model':<30s} {'Params':>7s} {'R²':>8s}")
    print(f"  {'-'*30} {'-'*7} {'-'*8}")
    print(f"  {'PREFIX only':<30s} {len(pre_list):>7d} {r2_prefix:>8.4f}")
    print(f"  {'MIDDLE only':<30s} {len(mid_list):>7d} {r2_middle:>8.4f}")
    print(f"  {'SUFFIX only':<30s} {len(suf_list):>7d} {r2_suffix:>8.4f}")
    print(f"  {'PREFIX + MIDDLE':<30s} {len(pre_list)+len(mid_list):>7d} {r2_pre_mid:>8.4f}")
    print(f"  {'PREFIX + SUFFIX':<30s} {len(pre_list)+len(suf_list):>7d} {r2_pre_suf:>8.4f}")
    print(f"  {'MIDDLE + SUFFIX':<30s} {len(mid_list)+len(suf_list):>7d} {r2_suf_mid:>8.4f}")
    print(f"  {'PREFIX + MIDDLE + SUFFIX':<30s} {len(pre_list)+len(mid_list)+len(suf_list):>7d} {r2_all:>8.4f}")

    # Unique contributions
    suf_unique = r2_all - r2_pre_mid
    pre_unique = r2_all - r2_suf_mid
    mid_unique = r2_all - r2_pre_suf

    print(f"\n  Unique contributions to position:")
    print(f"    PREFIX unique:  {pre_unique:+.4f}")
    print(f"    MIDDLE unique:  {mid_unique:+.4f}")
    print(f"    SUFFIX unique:  {suf_unique:+.4f}")
    print(f"    C1001 baseline: PREFIX+MIDDLE R²={r2_pre_mid:.4f} "
          f"(C1001 reported 0.118)")

    # ── Summary & Verdict ─────────────────────────────────
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Non-uniform suffixes: {non_uniform_count}/{n_testable}")
    print(f"  KW eta² (top 10): {eta_sq:.4f}")
    print(f"  Significant pairwise: {sig_pairs}/{total_pairs}")
    print(f"  R² SUFFIX alone: {r2_suffix:.4f}")
    print(f"  R² added by SUFFIX: {suf_unique:+.4f}")

    # Pass/fail: 15+ non-uniform = PASS, <8 = FAIL
    if non_uniform_count >= 15:
        verdict = 'SUFFIX_POSITIONAL_GRAMMAR_CONFIRMED'
        detail = (f'{non_uniform_count}/{n_testable} suffixes show non-uniform '
                  f'positional profiles. SUFFIX encodes line position '
                  f'(KW eta²={eta_sq:.4f}).')
    elif non_uniform_count >= 8:
        verdict = 'SUFFIX_POSITIONAL_GRAMMAR_PARTIAL'
        detail = (f'{non_uniform_count}/{n_testable} suffixes deviate from uniform. '
                  f'Positional grammar exists but weaker than PREFIX.')
    else:
        verdict = 'NO_SUFFIX_POSITIONAL_GRAMMAR'
        detail = (f'Only {non_uniform_count}/{n_testable} suffixes non-uniform. '
                  f'SUFFIX does not encode line position.')

    print(f"\n  VERDICT: {verdict}")
    print(f"  {detail}")

    # ── Output ────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'SUFFIX_POSITIONAL_STATE_MAPPING',
            'test': 'T1_SUFFIX_POSITIONAL_CENSUS',
            'min_tokens': MIN_TOKENS,
            'bonferroni_threshold': bonf_threshold,
        },
        'corpus': {
            'total_tokens': len(records),
            'testable_suffixes': n_testable,
        },
        'suffix_profiles': suffix_profiles,
        'suffix_quintiles': suffix_quintiles,
        'zones': zones,
        'kruskal_wallis': {
            'H': float(H_stat), 'p': float(kw_p), 'eta_sq': eta_sq,
            'top_suffixes_tested': top_suffixes,
        },
        'pairwise_significant': sig_pairs,
        'pairwise_total': total_pairs,
        'variance_decomposition': {
            'r2_prefix': r2_prefix,
            'r2_middle': r2_middle,
            'r2_suffix': r2_suffix,
            'r2_prefix_middle': r2_pre_mid,
            'r2_prefix_suffix': r2_pre_suf,
            'r2_middle_suffix': r2_suf_mid,
            'r2_all_three': r2_all,
            'prefix_unique': pre_unique,
            'middle_unique': mid_unique,
            'suffix_unique': suf_unique,
        },
        'non_uniform_count': non_uniform_count,
        'verdict': verdict,
        'verdict_detail': detail,
    }

    out_path = RESULTS_DIR / 't1_suffix_positional_census.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
