#!/usr/bin/env python3
"""
Phase 486: PREFIX CATEGORY-POSITION DECOMPOSITION
===================================================
Decomposes the PREFIX confound identified in C1372. Tests whether the
"thermal arc" (C1371) is driven by positional specialist PREFIXes (H1),
distributed across all PREFIX families (H2), or a pure compositional
artifact of PREFIX mix changing across positions (H3).

Tests:
  T1: Within-PREFIX category-position gradient (ch and sh separately)
  T2: Specialist PREFIX contribution quantification
  T3: ch vs sh category profile at matched positions
  T4: ok/ot final-position category contribution
  T5: qo PREFIX thermal dominance across positions
  T6: BARE token category-position profile
  T7: Residual category gradient after full PREFIX stratification

Depends on: C1372, C1371, C1001, C1012, C1305, C1250, C1299, C1300, C1302
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr, chi2_contingency
from scipy.spatial.distance import jensenshannon

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}
N_CATS = len(CATEGORIES)
N_QUINTILES = 5

# Positional specialist PREFIXes (C1001: >60% at initial or final)
INITIAL_SPECIALISTS = {'po', 'pch', 'tch', 'dch', 'so'}
FINAL_SPECIALISTS = {'ar', 'al', 'or'}
ALL_SPECIALISTS = INITIAL_SPECIALISTS | FINAL_SPECIALISTS


def round_floats(obj, digits=6):
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(float(obj), digits)
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    if isinstance(obj, tuple):
        return [round_floats(v, digits) for v in obj]
    return obj


def quintile_index(pos, line_len):
    if line_len <= 1:
        return 2
    frac = pos / (line_len - 1)
    q = int(frac * N_QUINTILES)
    return min(q, N_QUINTILES - 1)


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load B tokens with category, quintile, prefix, section."""
    print("Loading data...")

    morph = Morphology()
    cc = CategoryClassifier()

    # Collect per-line token data
    line_tokens = defaultdict(list)

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue

        m = morph.extract(token.word)
        mid = m.middle if m else token.word
        cat = cc.classify(mid)
        if not cat:
            continue

        prefix = (m.prefix if m else '') or ''
        key = (token.folio, token.line)
        line_tokens[key].append((cat, prefix))

    # Build token records with quintile assignments
    records = []  # [(cat_idx, quintile, prefix)]
    n_lines = 0

    for key, tokens in line_tokens.items():
        line_len = len(tokens)
        if line_len < 2:
            continue
        n_lines += 1
        for pos, (cat, prefix) in enumerate(tokens):
            q = quintile_index(pos, line_len)
            ci = CAT_IDX[cat]
            records.append((ci, q, prefix))

    n_tokens = len(records)
    print(f"  Lines: {n_lines}, Tokens: {n_tokens}")

    # Pre-compute per-PREFIX quintile-category matrices
    prefix_counts = defaultdict(lambda: np.zeros((N_QUINTILES, N_CATS), dtype=int))
    global_counts = np.zeros((N_QUINTILES, N_CATS), dtype=int)

    for ci, q, prefix in records:
        prefix_counts[prefix][q, ci] += 1
        global_counts[q, ci] += 1

    # PREFIX token totals
    prefix_totals = {p: int(c.sum()) for p, c in prefix_counts.items()}
    print(f"  Unique PREFIXes: {len(prefix_counts)}")
    top = sorted(prefix_totals.items(), key=lambda x: -x[1])[:10]
    top_str = ', '.join(f'{(p if p else "BARE")}={n}' for p, n in top)
    print(f"  Top 10: {top_str}")

    return {
        'records': records,
        'prefix_counts': dict(prefix_counts),
        'global_counts': global_counts,
        'prefix_totals': prefix_totals,
        'n_lines': n_lines,
        'n_tokens': n_tokens,
    }


# ── Helpers ──────────────────────────────────────────────────────────

def thermal_gradient_rho(cat_counts):
    """Compute Spearman rho of THERMAL fraction across quintiles."""
    row_sums = cat_counts.sum(axis=1)
    if any(row_sums == 0):
        return 0.0, 1.0
    fracs = cat_counts[:, CAT_IDX['THERMAL']] / row_sums
    if np.std(fracs) < 1e-10:
        return 0.0, 1.0  # constant input
    rho, p = spearmanr(np.arange(N_QUINTILES), fracs)
    if math.isnan(rho):
        return 0.0, 1.0
    return rho, p


def category_fracs(cat_counts):
    """Compute category fraction per quintile. Returns (5, 8) array."""
    row_sums = cat_counts.sum(axis=1, keepdims=True)
    return cat_counts / np.maximum(row_sums, 1)


# ── Test Functions ───────────────────────────────────────────────────

def test1_within_prefix_gradient(data):
    """T1: Within-PREFIX category-position gradient (ch and sh)."""
    print("\n=== T1: Within-PREFIX Category-Position Gradient (ch, sh) ===")

    results = {}

    for prefix in ['ch', 'sh']:
        counts = data['prefix_counts'].get(prefix)
        if counts is None:
            print(f"  {prefix}: no data")
            results[prefix] = {'n': 0, 'verdict': 'NO_DATA'}
            continue

        n = int(counts.sum())
        print(f"\n  {prefix}: {n} tokens")

        # Chi-squared: category x quintile independence
        # Build contingency: quintiles x categories
        # Remove columns with all zeros
        valid_cols = counts.sum(axis=0) > 0
        ct = counts[:, valid_cols]
        valid_rows = ct.sum(axis=1) > 0
        ct = ct[valid_rows]

        if ct.shape[0] >= 2 and ct.shape[1] >= 2:
            chi2, p, dof, _ = chi2_contingency(ct)
            v = np.sqrt(chi2 / (ct.sum() * (min(ct.shape) - 1)))
        else:
            chi2, p, dof, v = 0, 1, 0, 0

        print(f"    Chi-squared: chi2={chi2:.1f}, dof={dof}, p={p:.6f}, V={v:.4f}")

        # THERMAL gradient
        rho_th, p_th = thermal_gradient_rho(counts)
        print(f"    THERMAL gradient: rho={rho_th:.3f}, p={p_th:.4f}")

        # FLOW gradient
        row_sums = counts.sum(axis=1)
        flow_fracs = counts[:, CAT_IDX['FLOW']] / np.maximum(row_sums, 1)
        rho_fl, p_fl = spearmanr(np.arange(N_QUINTILES), flow_fracs)
        print(f"    FLOW gradient:    rho={rho_fl:.3f}, p={p_fl:.4f}")

        # Category fractions per quintile
        fracs = category_fracs(counts)
        print(f"    {'Cat':12s} {'Q1':>6s} {'Q2':>6s} {'Q3':>6s} {'Q4':>6s} {'Q5':>6s}")
        for ci, cat in enumerate(CATEGORIES):
            vals = fracs[:, ci]
            if vals.sum() > 0:
                print(f"    {cat:12s} {vals[0]:6.3f} {vals[1]:6.3f} {vals[2]:6.3f} "
                      f"{vals[3]:6.3f} {vals[4]:6.3f}")

        # Bonferroni-corrected significance (2 tests)
        sig = p < 0.005  # 0.01/2

        results[prefix] = {
            'n': n,
            'chi2': float(chi2),
            'p': float(p),
            'dof': int(dof),
            'cramers_v': float(v),
            'thermal_rho': float(rho_th),
            'thermal_p': float(p_th),
            'flow_rho': float(rho_fl),
            'flow_p': float(p_fl),
            'significant_bonferroni': bool(sig),
            'quintile_fracs': {cat: [float(fracs[q, ci]) for q in range(N_QUINTILES)]
                               for ci, cat in enumerate(CATEGORIES)},
        }

    # H1/H2/H3 verdict
    ch_sig = results.get('ch', {}).get('significant_bonferroni', False)
    sh_sig = results.get('sh', {}).get('significant_bonferroni', False)
    ch_rho = abs(results.get('ch', {}).get('thermal_rho', 0))
    sh_rho = abs(results.get('sh', {}).get('thermal_rho', 0))

    if ch_sig and sh_sig:
        verdict = 'H2_SUPPORTED: both ch and sh show within-PREFIX gradient'
    elif ch_sig or sh_sig:
        verdict = 'MIXED: one of ch/sh shows gradient'
    else:
        verdict = 'H1_H3_VIABLE: neither ch nor sh shows significant gradient'

    print(f"\n  T1 verdict: {verdict}")
    results['verdict'] = verdict

    return results


def test2_specialist_contribution(data):
    """T2: Specialist PREFIX contribution quantification."""
    print("\n=== T2: Specialist PREFIX Contribution Quantification ===")

    # Full corpus
    full_counts = data['global_counts']
    rho_full, p_full = thermal_gradient_rho(full_counts)
    print(f"  Full corpus THERMAL rho: {rho_full:.3f}")

    # Specialists removed
    nonspec_counts = np.zeros((N_QUINTILES, N_CATS), dtype=int)
    for prefix, counts in data['prefix_counts'].items():
        if prefix not in ALL_SPECIALISTS:
            nonspec_counts += counts

    rho_nonspec, p_nonspec = thermal_gradient_rho(nonspec_counts)
    n_nonspec = int(nonspec_counts.sum())
    print(f"  Specialists removed: {n_nonspec} tokens, THERMAL rho={rho_nonspec:.3f}, p={p_nonspec:.4f}")

    # ch+sh only
    chsh_counts = np.zeros((N_QUINTILES, N_CATS), dtype=int)
    for prefix in ['ch', 'sh']:
        if prefix in data['prefix_counts']:
            chsh_counts += data['prefix_counts'][prefix]

    rho_chsh, p_chsh = thermal_gradient_rho(chsh_counts)
    n_chsh = int(chsh_counts.sum())
    print(f"  ch+sh only: {n_chsh} tokens, THERMAL rho={rho_chsh:.3f}, p={p_chsh:.4f}")

    # Attenuation ratios
    if abs(rho_full) > 1e-10:
        ratio_nonspec = rho_nonspec / rho_full
        ratio_chsh = rho_chsh / rho_full
    else:
        ratio_nonspec = 0.0
        ratio_chsh = 0.0

    print(f"\n  Attenuation ratios (relative to full corpus):")
    print(f"    Specialists removed: {ratio_nonspec:.3f}")
    print(f"    ch+sh only:          {ratio_chsh:.3f}")

    # Bootstrap CI for attenuation ratios
    records = data['records']
    rng = np.random.default_rng(42)
    boot_ratios_nonspec = []
    boot_ratios_chsh = []

    for _ in range(1000):
        idx = rng.choice(len(records), len(records), replace=True)
        b_full = np.zeros((N_QUINTILES, N_CATS), dtype=int)
        b_nonspec = np.zeros((N_QUINTILES, N_CATS), dtype=int)
        b_chsh = np.zeros((N_QUINTILES, N_CATS), dtype=int)

        for i in idx:
            ci, q, prefix = records[i]
            b_full[q, ci] += 1
            if prefix not in ALL_SPECIALISTS:
                b_nonspec[q, ci] += 1
            if prefix in ('ch', 'sh'):
                b_chsh[q, ci] += 1

        r_f, _ = thermal_gradient_rho(b_full)
        if abs(r_f) > 1e-10:
            r_ns, _ = thermal_gradient_rho(b_nonspec)
            r_cs, _ = thermal_gradient_rho(b_chsh)
            boot_ratios_nonspec.append(r_ns / r_f)
            boot_ratios_chsh.append(r_cs / r_f)

    if boot_ratios_nonspec:
        ci_nonspec = (float(np.percentile(boot_ratios_nonspec, 2.5)),
                      float(np.percentile(boot_ratios_nonspec, 97.5)))
        ci_chsh = (float(np.percentile(boot_ratios_chsh, 2.5)),
                   float(np.percentile(boot_ratios_chsh, 97.5)))
        print(f"    Specialists removed 95% CI: [{ci_nonspec[0]:.3f}, {ci_nonspec[1]:.3f}]")
        print(f"    ch+sh only 95% CI:          [{ci_chsh[0]:.3f}, {ci_chsh[1]:.3f}]")
    else:
        ci_nonspec = ci_chsh = (0.0, 0.0)

    # Specialist token counts
    spec_n = sum(data['prefix_totals'].get(p, 0) for p in ALL_SPECIALISTS)
    print(f"\n  Specialist tokens: {spec_n} ({100*spec_n/data['n_tokens']:.1f}%)")
    for p in sorted(ALL_SPECIALISTS):
        n = data['prefix_totals'].get(p, 0)
        if n > 0:
            zone = 'INITIAL' if p in INITIAL_SPECIALISTS else 'FINAL'
            print(f"    {p:6s}: {n:5d} ({zone})")

    # H1 vs H2 verdict
    if ratio_nonspec < 0.30:
        verdict = 'H1_SUPPORTED: specialists drive gradient'
    elif ratio_nonspec > 0.60:
        verdict = 'H2_SUPPORTED: gradient survives specialist removal'
    else:
        verdict = f'INTERMEDIATE: ratio={ratio_nonspec:.3f}'

    print(f"\n  T2 verdict: {verdict}")

    return {
        'rho_full': float(rho_full),
        'rho_specialists_removed': float(rho_nonspec),
        'p_specialists_removed': float(p_nonspec),
        'n_specialists_removed': n_nonspec,
        'rho_chsh_only': float(rho_chsh),
        'p_chsh_only': float(p_chsh),
        'n_chsh_only': n_chsh,
        'ratio_nonspec': float(ratio_nonspec),
        'ratio_chsh': float(ratio_chsh),
        'ci_nonspec': ci_nonspec,
        'ci_chsh': ci_chsh,
        'specialist_n': spec_n,
        'specialist_pct': float(100 * spec_n / data['n_tokens']),
        'verdict': verdict,
    }


def test3_ch_sh_matched_position(data):
    """T3: ch vs sh category profile at matched positions."""
    print("\n=== T3: ch vs sh Category Profile at Matched Positions ===")

    ch_counts = data['prefix_counts'].get('ch', np.zeros((N_QUINTILES, N_CATS), dtype=int))
    sh_counts = data['prefix_counts'].get('sh', np.zeros((N_QUINTILES, N_CATS), dtype=int))

    jsd_per_quintile = []
    v_per_quintile = []

    for q in range(N_QUINTILES):
        ch_q = ch_counts[q].astype(float)
        sh_q = sh_counts[q].astype(float)

        # JSD
        ch_norm = ch_q / max(ch_q.sum(), 1)
        sh_norm = sh_q / max(sh_q.sum(), 1)
        eps = 1e-10
        ch_norm = (ch_norm + eps) / (ch_norm + eps).sum()
        sh_norm = (sh_norm + eps) / (sh_norm + eps).sum()
        jsd = float(jensenshannon(ch_norm, sh_norm) ** 2)
        jsd_per_quintile.append(jsd)

        # Cramer's V (2 x N_CATS contingency)
        ct = np.array([ch_q, sh_q])
        valid_cols = ct.sum(axis=0) > 0
        ct = ct[:, valid_cols]
        if ct.shape[1] >= 2 and ct.sum() > 0:
            chi2, _, _, _ = chi2_contingency(ct)
            v = np.sqrt(chi2 / (ct.sum() * (min(ct.shape) - 1)))
        else:
            v = 0.0
        v_per_quintile.append(float(v))

        print(f"  Q{q+1}: JSD={jsd:.6f}, V={v:.4f}, ch_n={int(ch_q.sum())}, sh_n={int(sh_q.sum())}")

    # Permutation test for JSD significance at each quintile
    n_perm = 1000
    rng = np.random.default_rng(42)
    sig_count = 0

    for q in range(N_QUINTILES):
        observed_jsd = jsd_per_quintile[q]
        combined = ch_counts[q] + sh_counts[q]
        total_ch = int(ch_counts[q].sum())
        total_sh = int(sh_counts[q].sum())

        perm_jsds = []
        for _ in range(n_perm):
            # Shuffle: randomly assign tokens to ch/sh
            all_tokens = []
            for ci in range(N_CATS):
                all_tokens.extend([ci] * int(combined[ci]))
            rng.shuffle(all_tokens)

            fake_ch = np.zeros(N_CATS)
            fake_sh = np.zeros(N_CATS)
            for i, ci in enumerate(all_tokens):
                if i < total_ch:
                    fake_ch[ci] += 1
                else:
                    fake_sh[ci] += 1

            fc = (fake_ch + eps) / (fake_ch + eps).sum()
            fs = (fake_sh + eps) / (fake_sh + eps).sum()
            perm_jsds.append(jensenshannon(fc, fs) ** 2)

        p_perm = float(np.mean(np.array(perm_jsds) >= observed_jsd))
        sig = p_perm < 0.01
        if sig:
            sig_count += 1
        print(f"    Permutation p={p_perm:.4f} {'*' if sig else ''}")

    # Stability check: range/mean of JSD
    jsd_arr = np.array(jsd_per_quintile)
    jsd_range_mean = float((jsd_arr.max() - jsd_arr.min()) / max(jsd_arr.mean(), 1e-10))
    print(f"\n  JSD range/mean: {jsd_range_mean:.3f} (< 0.50 = stable)")
    print(f"  Significant at {sig_count}/5 quintiles")

    stable = jsd_range_mean < 0.50
    consistent = sig_count >= 4

    verdict = ('CONFIRMED: ch/sh diverge consistently at all positions'
               if consistent and stable else
               'PARTIAL: ch/sh diverge but not consistently' if consistent else
               'WEAK: ch/sh divergence is position-dependent or absent')
    print(f"  T3 verdict: {verdict}")

    return {
        'jsd_per_quintile': jsd_per_quintile,
        'v_per_quintile': v_per_quintile,
        'sig_count': sig_count,
        'jsd_range_mean': jsd_range_mean,
        'stable': stable,
        'consistent': consistent,
        'verdict': verdict,
    }


def test4_ok_ot_final(data):
    """T4: ok/ot final-position category contribution."""
    print("\n=== T4: ok/ot Final-Position Category Contribution ===")

    # Q5 with all tokens
    full_q5 = data['global_counts'][4].copy()
    full_total = full_q5.sum()
    full_fracs = full_q5 / max(full_total, 1)

    # Q5 without ok/ot
    removed_q5 = full_q5.copy()
    for prefix in ['ok', 'ot']:
        if prefix in data['prefix_counts']:
            removed_q5 = removed_q5 - data['prefix_counts'][prefix][4]
    removed_q5 = np.maximum(removed_q5, 0)
    removed_total = removed_q5.sum()
    removed_fracs = removed_q5 / max(removed_total, 1)

    # ok/ot token counts at Q5
    ok_q5 = int(data['prefix_counts'].get('ok', np.zeros((N_QUINTILES, N_CATS), dtype=int))[4].sum())
    ot_q5 = int(data['prefix_counts'].get('ot', np.zeros((N_QUINTILES, N_CATS), dtype=int))[4].sum())

    print(f"  Q5 total: {full_total}, ok at Q5: {ok_q5}, ot at Q5: {ot_q5}")
    print(f"  Q5 after removal: {removed_total}")

    print(f"\n  {'Category':12s} {'With':>8s} {'Without':>8s} {'Delta':>8s}")
    deltas = {}
    for ci, cat in enumerate(CATEGORIES):
        d = float(full_fracs[ci] - removed_fracs[ci])
        deltas[cat] = d
        print(f"  {cat:12s} {full_fracs[ci]:8.4f} {removed_fracs[ci]:8.4f} {d:+8.4f}")

    flow_trans_delta = deltas.get('FLOW', 0) + deltas.get('TRANSITION', 0)
    print(f"\n  FLOW+TRANSITION delta: {flow_trans_delta:+.4f} ({flow_trans_delta*100:+.1f} pp)")

    # ok and ot category profiles at Q5
    for prefix in ['ok', 'ot']:
        counts = data['prefix_counts'].get(prefix)
        if counts is not None:
            q5 = counts[4].astype(float)
            total = q5.sum()
            if total > 0:
                profile = q5 / total
                top_cats = sorted(enumerate(profile), key=lambda x: -x[1])[:3]
                top_str = ', '.join(f"{CATEGORIES[ci]}={v:.1%}" for ci, v in top_cats)
                print(f"  {prefix} Q5 profile (n={int(total)}): {top_str}")

    if abs(flow_trans_delta) < 0.01:
        verdict = 'NOT_DRIVER: ok/ot do not drive Q5 FLOW+TRANSITION'
    elif abs(flow_trans_delta) < 0.03:
        verdict = 'MINOR: ok/ot contribute modestly to Q5'
    else:
        verdict = 'SIGNIFICANT: ok/ot substantially shape Q5'

    print(f"  T4 verdict: {verdict}")

    return {
        'full_q5_n': int(full_total),
        'ok_q5_n': ok_q5,
        'ot_q5_n': ot_q5,
        'deltas': {cat: float(d) for cat, d in deltas.items()},
        'flow_trans_delta_pp': float(flow_trans_delta * 100),
        'verdict': verdict,
    }


def test5_qo_thermal(data):
    """T5: qo PREFIX thermal dominance across positions."""
    print("\n=== T5: qo THERMAL Dominance Across Positions ===")

    qo_counts = data['prefix_counts'].get('qo', np.zeros((N_QUINTILES, N_CATS), dtype=int))
    qo_total = int(qo_counts.sum())
    print(f"  qo total tokens: {qo_total}")

    # qo fraction per quintile
    full_row_sums = data['global_counts'].sum(axis=1)
    qo_row_sums = qo_counts.sum(axis=1)
    qo_frac_per_q = qo_row_sums / np.maximum(full_row_sums, 1)
    print(f"  qo fraction per quintile: {', '.join(f'Q{q+1}={qo_frac_per_q[q]:.4f}' for q in range(N_QUINTILES))}")

    # THERMAL with and without qo
    full_fracs = category_fracs(data['global_counts'])
    noqo_counts = data['global_counts'] - qo_counts
    noqo_counts = np.maximum(noqo_counts, 0)
    noqo_fracs = category_fracs(noqo_counts)

    thermal_full = full_fracs[:, CAT_IDX['THERMAL']]
    thermal_noqo = noqo_fracs[:, CAT_IDX['THERMAL']]
    thermal_qo_contrib = thermal_full - thermal_noqo

    print(f"\n  {'Quintile':>8s} {'THERMAL':>8s} {'no-qo':>8s} {'qo-attr':>8s}")
    for q in range(N_QUINTILES):
        print(f"  Q{q+1:>7d} {thermal_full[q]:8.4f} {thermal_noqo[q]:8.4f} {thermal_qo_contrib[q]:8.4f}")

    # THERMAL gradient with and without qo
    rho_full, p_full = thermal_gradient_rho(data['global_counts'])
    rho_noqo, p_noqo = thermal_gradient_rho(noqo_counts)

    print(f"\n  THERMAL rho full:  {rho_full:.3f}")
    print(f"  THERMAL rho no-qo: {rho_noqo:.3f}")

    if abs(rho_full) > 1e-10:
        ratio = rho_noqo / rho_full
    else:
        ratio = 0.0

    print(f"  Attenuation ratio: {ratio:.3f}")

    # qo category profile (should be near-pure THERMAL per C1300)
    qo_total_profile = qo_counts.sum(axis=0).astype(float)
    qo_total_sum = qo_total_profile.sum()
    if qo_total_sum > 0:
        qo_profile = qo_total_profile / qo_total_sum
        top_cats = sorted(enumerate(qo_profile), key=lambda x: -x[1])[:3]
        print(f"\n  qo category profile: {', '.join(f'{CATEGORIES[ci]}={v:.1%}' for ci, v in top_cats)}")

    if ratio > 0.70:
        verdict = 'MINOR: qo contributes little to THERMAL gradient'
    elif ratio < 0.30:
        verdict = 'DOMINANT: qo drives THERMAL gradient'
    else:
        verdict = f'SHARED: qo contributes moderately (ratio={ratio:.3f})'

    print(f"  T5 verdict: {verdict}")

    return {
        'qo_total': qo_total,
        'qo_frac_per_quintile': [float(v) for v in qo_frac_per_q],
        'thermal_full': [float(v) for v in thermal_full],
        'thermal_no_qo': [float(v) for v in thermal_noqo],
        'rho_full': float(rho_full),
        'rho_no_qo': float(rho_noqo),
        'attenuation_ratio': float(ratio),
        'verdict': verdict,
    }


def test6_bare_profile(data):
    """T6: BARE token category-position profile."""
    print("\n=== T6: BARE Token Category-Position Profile ===")

    bare_counts = data['prefix_counts'].get('', np.zeros((N_QUINTILES, N_CATS), dtype=int))
    bare_total = int(bare_counts.sum())
    print(f"  BARE total tokens: {bare_total}")

    # BARE fraction per quintile
    full_row_sums = data['global_counts'].sum(axis=1)
    bare_row_sums = bare_counts.sum(axis=1)
    bare_frac_per_q = bare_row_sums / np.maximum(full_row_sums, 1)
    print(f"  BARE fraction per quintile: {', '.join(f'Q{q+1}={bare_frac_per_q[q]:.4f}' for q in range(N_QUINTILES))}")

    # BARE positional gradient
    rho_bare_pos, p_bare_pos = spearmanr(np.arange(N_QUINTILES), bare_frac_per_q)
    print(f"  BARE position gradient: rho={rho_bare_pos:.3f}, p={p_bare_pos:.4f}")

    # BARE category profile per quintile
    bare_fracs = category_fracs(bare_counts)
    print(f"\n  {'Cat':12s} {'Q1':>6s} {'Q2':>6s} {'Q3':>6s} {'Q4':>6s} {'Q5':>6s}")
    for ci, cat in enumerate(CATEGORIES):
        vals = bare_fracs[:, ci]
        if vals.sum() > 0:
            print(f"  {cat:12s} {vals[0]:6.3f} {vals[1]:6.3f} {vals[2]:6.3f} "
                  f"{vals[3]:6.3f} {vals[4]:6.3f}")

    # Internal category gradient (chi-squared)
    valid_cols = bare_counts.sum(axis=0) > 0
    ct = bare_counts[:, valid_cols]
    valid_rows = ct.sum(axis=1) > 0
    ct = ct[valid_rows]

    if ct.shape[0] >= 2 and ct.shape[1] >= 2 and ct.sum() > 10:
        chi2, p, dof, _ = chi2_contingency(ct)
        v = np.sqrt(chi2 / (ct.sum() * (min(ct.shape) - 1)))
        print(f"\n  Internal gradient: chi2={chi2:.1f}, p={p:.6f}, V={v:.4f}")
    else:
        chi2, p, dof, v = 0, 1, 0, 0

    # THERMAL fraction for BARE
    rho_th, p_th = thermal_gradient_rho(bare_counts)
    print(f"  BARE THERMAL gradient: rho={rho_th:.3f}, p={p_th:.4f}")

    # Overall BARE category profile
    bare_overall = bare_counts.sum(axis=0).astype(float)
    if bare_overall.sum() > 0:
        bare_profile = bare_overall / bare_overall.sum()
        top_cats = sorted(enumerate(bare_profile), key=lambda x: -x[1])[:4]
        print(f"  BARE overall: {', '.join(f'{CATEGORIES[ci]}={v:.1%}' for ci, v in top_cats)}")

    return {
        'bare_total': bare_total,
        'bare_frac_per_quintile': [float(v) for v in bare_frac_per_q],
        'bare_position_rho': float(rho_bare_pos),
        'bare_position_p': float(p_bare_pos),
        'internal_chi2': float(chi2),
        'internal_p': float(p),
        'internal_v': float(v),
        'thermal_rho': float(rho_th),
        'thermal_p': float(p_th),
    }


def test7_within_prefix_stratification(data):
    """T7: Residual category gradient after full PREFIX stratification."""
    print("\n=== T7: Within-PREFIX Stratified Gradient ===")

    min_tokens = 100
    results_per_prefix = {}
    weighted_rho_sum = 0.0
    total_weight = 0

    print(f"  PREFIXes with >= {min_tokens} tokens:")
    print(f"  {'PREFIX':>8s} {'N':>6s} {'THERMAL_rho':>12s} {'p':>8s} {'|rho|>0.5':>10s}")

    qualifying_prefixes = []
    for prefix in sorted(data['prefix_counts'].keys(), key=lambda p: -data['prefix_totals'].get(p, 0)):
        counts = data['prefix_counts'][prefix]
        n = int(counts.sum())
        if n < min_tokens:
            continue

        rho, p = thermal_gradient_rho(counts)
        label = prefix or 'BARE'
        sig_marker = '*' if abs(rho) > 0.50 else ''
        print(f"  {label:>8s} {n:6d} {rho:12.3f} {p:8.4f} {sig_marker:>10s}")

        results_per_prefix[label] = {
            'n': n,
            'thermal_rho': float(rho),
            'thermal_p': float(p),
            'strong': bool(abs(rho) > 0.50),
        }

        weighted_rho_sum += rho * n
        total_weight += n
        qualifying_prefixes.append((label, n, rho))

    # Weighted average rho
    weighted_avg_rho = weighted_rho_sum / max(total_weight, 1)
    n_qualifying = len(qualifying_prefixes)
    n_strong = sum(1 for _, _, r in qualifying_prefixes if abs(r) > 0.50)

    print(f"\n  Qualifying PREFIXes: {n_qualifying}")
    print(f"  Weighted average THERMAL rho: {weighted_avg_rho:.4f}")
    print(f"  PREFIXes with |rho| > 0.50: {n_strong}/{n_qualifying}")

    # H1/H2/H3 verdict
    if abs(weighted_avg_rho) < 0.30:
        if n_strong <= 2:
            verdict = 'H3_SUPPORTED: gradient is compositional (PREFIX-mix only)'
        else:
            verdict = 'H1_SUPPORTED: concentrated in few specialist PREFIXes'
    elif abs(weighted_avg_rho) > 0.50 and n_strong > n_qualifying * 0.5:
        verdict = 'H2_SUPPORTED: gradient distributed across PREFIXes'
    elif abs(weighted_avg_rho) > 0.50:
        verdict = f'H1_PARTIAL: gradient from {n_strong} PREFIXes, not distributed'
    else:
        verdict = f'INTERMEDIATE: weighted rho={weighted_avg_rho:.3f}, {n_strong} strong'

    print(f"  T7 verdict: {verdict}")

    return {
        'per_prefix': results_per_prefix,
        'weighted_avg_rho': float(weighted_avg_rho),
        'n_qualifying': n_qualifying,
        'n_strong': n_strong,
        'total_weight': total_weight,
        'verdict': verdict,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    import time
    t0 = time.time()

    data = load_data()

    t1 = test1_within_prefix_gradient(data)
    t2 = test2_specialist_contribution(data)
    t3 = test3_ch_sh_matched_position(data)
    t4 = test4_ok_ot_final(data)
    t5 = test5_qo_thermal(data)
    t6 = test6_bare_profile(data)
    t7 = test7_within_prefix_stratification(data)

    # ── Overall Hypothesis Verdict ───────────────────────────────
    print(f"\n{'='*60}")
    print("HYPOTHESIS VERDICTS:")
    print(f"  T1 (ch/sh within-PREFIX gradient): {t1.get('verdict', '?')}")
    print(f"  T2 (specialist contribution):      {t2.get('verdict', '?')}")
    print(f"  T3 (ch/sh at matched positions):   {t3.get('verdict', '?')}")
    print(f"  T4 (ok/ot at Q5):                  {t4.get('verdict', '?')}")
    print(f"  T5 (qo THERMAL):                   {t5.get('verdict', '?')}")
    print(f"  T7 (full stratification):           {t7.get('verdict', '?')}")

    # Determine overall hypothesis
    t2_ratio = t2.get('ratio_nonspec', 0)
    t7_rho = abs(t7.get('weighted_avg_rho', 0))
    t7_strong = t7.get('n_strong', 0)
    t7_total = t7.get('n_qualifying', 1)

    if t7_rho < 0.30 and t2_ratio < 0.30:
        overall = 'H1: Specialist PREFIXes drive the thermal arc'
    elif t7_rho < 0.30:
        overall = 'H3: Gradient is pure compositional artifact (PREFIX mix)'
    elif t7_rho > 0.50 and t7_strong > t7_total * 0.5:
        overall = 'H2: Gradient is distributed across PREFIX families'
    elif t7_rho > 0.50:
        overall = 'H1+H2 HYBRID: gradient from subset of PREFIXes'
    else:
        overall = f'MIXED: weighted rho={t7_rho:.3f}, specialist ratio={t2_ratio:.3f}'

    print(f"\n  OVERALL: {overall}")
    print(f"{'='*60}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    results = {
        'metadata': {
            'phase': 486,
            'name': 'PREFIX_CATEGORY_POSITION_DECOMPOSITION',
            'n_tokens': data['n_tokens'],
            'n_lines': data['n_lines'],
            'elapsed_seconds': elapsed,
        },
        'T1_within_prefix_gradient': t1,
        'T2_specialist_contribution': t2,
        'T3_ch_sh_matched_position': t3,
        'T4_ok_ot_final': t4,
        'T5_qo_thermal': t5,
        'T6_bare_profile': t6,
        'T7_within_prefix_stratification': t7,
        'overall_hypothesis': overall,
    }

    out_path = RESULTS_DIR / 'prefix_category_position_decomposition.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
