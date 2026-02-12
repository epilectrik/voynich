"""
T4: PREFIX Positional Stability Across Regimes
================================================
Phase: PP_INFORMATION_DECOMPOSITION

Tests whether PREFIX positional grammar is a universal feature of B grammar
or varies by regime. If positional profiles are regime-invariant, PREFIX
position encoding is a deep grammar feature. If they vary, regimes use
different positional rules.

Tests:
  4a: Per-PREFIX positional profiles split by regime
      JSD between regime-specific profiles for each PREFIX
  4b: Interaction test: does REGIME moderate the PREFIX→position relationship?
      (Two-way ANOVA: position ~ PREFIX * REGIME)
  4c: Per-folio PREFIX positional entropy
      Do individual folios (programs) show the same PREFIX ordering?

Output: t4_prefix_regime_positional_stability.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

MIN_TOKENS_PER_CELL = 10  # Minimum for regime × prefix cell


def positional_distribution(positions, n_bins=5):
    """Convert position array to histogram distribution."""
    edges = np.linspace(0, 1.001, n_bins + 1)
    counts, _ = np.histogram(positions, bins=edges)
    total = counts.sum()
    if total == 0:
        return np.ones(n_bins) / n_bins
    return counts / total


def main():
    morph = Morphology()
    tx = Transcript()

    # ── Load regime mapping ──────────────────────────────
    with open(PROJECT / 'data' / 'regime_folio_mapping.json') as f:
        regime_data = json.load(f)
    folio_to_regime = {
        f: d['regime']
        for f, d in regime_data['regime_assignments'].items()
    }

    # ── Single corpus pass ───────────────────────────────
    print("Building regime-stratified positional data...")

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

    # Extract records with regime
    records = []
    for (folio, line), tokens in line_tokens.items():
        n = len(tokens)
        if n < 2:
            continue
        regime = folio_to_regime.get(folio, 'UNKNOWN')
        if regime == 'UNKNOWN':
            continue
        for i, tok in enumerate(tokens):
            w = tok.word.strip()
            m = word_morph.get(w)
            if m and m.middle:
                prefix = m.prefix or 'BARE'
                pos = i / (n - 1)
                records.append((prefix, m.middle, pos, regime, folio))

    print(f"  Total records: {len(records)}")

    # ══════════════════════════════════════════════════════
    # TEST 4a: REGIME-STRATIFIED POSITIONAL PROFILES
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T4a: REGIME-STRATIFIED PREFIX POSITIONAL PROFILES")
    print(f"{'='*70}")

    # Group positions by (prefix, regime)
    prefix_regime_positions = defaultdict(lambda: defaultdict(list))
    for prefix, middle, pos, regime, folio in records:
        prefix_regime_positions[prefix][regime].append(pos)

    # Get PREFIXes with enough data across regimes
    regimes = sorted({r[3] for r in records})
    testable_prefixes = []
    for prefix in prefix_regime_positions:
        counts = {reg: len(prefix_regime_positions[prefix][reg])
                  for reg in regimes}
        if all(c >= MIN_TOKENS_PER_CELL for c in counts.values()):
            testable_prefixes.append(prefix)

    testable_prefixes.sort(key=lambda p: -sum(
        len(prefix_regime_positions[p][r]) for r in regimes))

    print(f"\n  Testable PREFIXes (>={MIN_TOKENS_PER_CELL} per regime): "
          f"{len(testable_prefixes)}")

    N_BINS = 5
    print(f"\n  {'PREFIX':<8s} ", end='')
    for reg in regimes:
        print(f"{'mean_'+reg[-1]:>10s}", end='')
    print(f"  {'Max JSD':>8s} {'Min JSD':>8s} {'Mean JSD':>8s} {'Stable?':>8s}")

    print(f"  {'-'*8} " + "".join(f"{'-'*10} " for _ in regimes)
          + f"  {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    prefix_stability = {}
    for prefix in testable_prefixes:
        regime_dists = {}
        regime_means = {}
        for reg in regimes:
            positions = np.array(prefix_regime_positions[prefix][reg])
            regime_dists[reg] = positional_distribution(positions, N_BINS)
            regime_means[reg] = float(np.mean(positions))

        # Pairwise JSD between regimes
        jsds = []
        for i, r1 in enumerate(regimes):
            for r2 in regimes[i+1:]:
                jsd = float(jensenshannon(regime_dists[r1], regime_dists[r2]))
                jsds.append(jsd)

        max_jsd = max(jsds) if jsds else 0.0
        min_jsd = min(jsds) if jsds else 0.0
        mean_jsd = float(np.mean(jsds)) if jsds else 0.0
        stable = max_jsd < 0.15  # Threshold for stability

        prefix_stability[prefix] = {
            'regime_means': regime_means,
            'regime_dists': {r: d.tolist() for r, d in regime_dists.items()},
            'pairwise_jsds': jsds,
            'max_jsd': max_jsd,
            'min_jsd': min_jsd,
            'mean_jsd': mean_jsd,
            'stable': stable,
            'n_per_regime': {r: len(prefix_regime_positions[prefix][r])
                            for r in regimes},
        }

        print(f"  {prefix:<8s} ", end='')
        for reg in regimes:
            print(f"{regime_means[reg]:>10.3f}", end='')
        stable_mark = 'YES' if stable else 'NO'
        print(f"  {max_jsd:>8.3f} {min_jsd:>8.3f} {mean_jsd:>8.3f} "
              f"{stable_mark:>8s}")

    n_stable = sum(1 for v in prefix_stability.values() if v['stable'])
    n_tested = len(prefix_stability)
    print(f"\n  Stable PREFIXes: {n_stable}/{n_tested} "
          f"({n_stable/n_tested*100:.1f}%)")

    # ══════════════════════════════════════════════════════
    # TEST 4b: REGIME × PREFIX INTERACTION ON POSITION
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T4b: REGIME × PREFIX INTERACTION ON POSITION")
    print(f"{'='*70}")

    # Use top 8 PREFIXes for balanced comparison
    top_prefixes = testable_prefixes[:8]
    print(f"\n  Using top {len(top_prefixes)} PREFIXes: {top_prefixes}")

    # Build position array grouped by (prefix, regime)
    # Test: 2-way Kruskal-Wallis-style analysis
    # Since scipy doesn't have 2-way nonparametric, use:
    # 1. KW on PREFIX (main effect)
    # 2. KW on REGIME (main effect)
    # 3. Interaction: KW on PREFIX within each regime, compare H values

    filt = [(p, pos, reg) for p, mid, pos, reg, f in records
            if p in top_prefixes]

    # Main effect: PREFIX
    pre_groups = defaultdict(list)
    for p, pos, reg in filt:
        pre_groups[p].append(pos)
    H_pre, p_pre = stats.kruskal(
        *[np.array(pre_groups[p]) for p in top_prefixes])
    print(f"\n  Main effect PREFIX: H={H_pre:.2f}, p={p_pre:.2e}")

    # Main effect: REGIME
    reg_groups = defaultdict(list)
    for p, pos, reg in filt:
        reg_groups[reg].append(pos)
    H_reg, p_reg = stats.kruskal(
        *[np.array(reg_groups[r]) for r in regimes if r in reg_groups])
    print(f"  Main effect REGIME: H={H_reg:.2f}, p={p_reg:.2e}")

    # Interaction: PREFIX effect within each regime
    print(f"\n  PREFIX effect WITHIN each regime:")
    interaction_H = {}
    for reg in regimes:
        reg_filt = [(p, pos) for p, pos, r in filt if r == reg]
        if not reg_filt:
            continue
        groups = defaultdict(list)
        for p, pos in reg_filt:
            groups[p].append(pos)
        valid = [np.array(groups[p]) for p in top_prefixes
                 if len(groups[p]) >= 5]
        if len(valid) >= 2:
            H_within, p_within = stats.kruskal(*valid)
            interaction_H[reg] = {'H': float(H_within), 'p': float(p_within)}
            print(f"    {reg}: H={H_within:.2f}, p={p_within:.2e}")

    # Compare H values across regimes (should be similar if no interaction)
    H_values = [v['H'] for v in interaction_H.values()]
    if len(H_values) >= 2:
        H_cv = float(np.std(H_values) / np.mean(H_values))
        print(f"\n  H-statistic CV across regimes: {H_cv:.3f}")
        print(f"  (Low CV = consistent PREFIX effect = no interaction)")

    # ══════════════════════════════════════════════════════
    # TEST 4c: PER-FOLIO PREFIX POSITIONAL ENTROPY
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T4c: PER-FOLIO PREFIX POSITIONAL CONSISTENCY")
    print(f"{'='*70}")

    # For each folio, compute mean position per PREFIX
    # Then measure how consistent these are across folios
    folio_prefix_positions = defaultdict(lambda: defaultdict(list))
    for prefix, middle, pos, regime, folio in records:
        folio_prefix_positions[folio][prefix].append(pos)

    # For each PREFIX, get per-folio mean positions
    prefix_folio_means = defaultdict(list)
    for folio in folio_prefix_positions:
        for prefix in testable_prefixes[:10]:
            positions = folio_prefix_positions[folio].get(prefix, [])
            if len(positions) >= 5:
                prefix_folio_means[prefix].append(float(np.mean(positions)))

    print(f"\n  {'PREFIX':<8s} {'Folios':>7s} {'Grand':>7s} {'FolioStd':>9s} "
          f"{'IQR':>7s} {'Consistent':>11s}")
    print(f"  {'-'*8} {'-'*7} {'-'*7} {'-'*9} {'-'*7} {'-'*11}")

    folio_consistency = {}
    for prefix in testable_prefixes[:10]:
        means = prefix_folio_means.get(prefix, [])
        if len(means) < 3:
            continue
        means_arr = np.array(means)
        grand_mean = float(np.mean(means_arr))
        folio_std = float(np.std(means_arr))
        iqr = float(np.percentile(means_arr, 75) - np.percentile(means_arr, 25))
        consistent = folio_std < 0.10

        folio_consistency[prefix] = {
            'n_folios': len(means),
            'grand_mean': grand_mean,
            'folio_std': folio_std,
            'iqr': iqr,
            'consistent': consistent,
        }

        mark = 'YES' if consistent else 'NO'
        print(f"  {prefix:<8s} {len(means):>7d} {grand_mean:>7.3f} "
              f"{folio_std:>9.4f} {iqr:>7.3f} {mark:>11s}")

    n_consistent = sum(1 for v in folio_consistency.values() if v['consistent'])
    n_tested_fc = len(folio_consistency)

    # ── Summary ──────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Regime-stable PREFIXes: {n_stable}/{n_tested}")
    print(f"  Folio-consistent PREFIXes: {n_consistent}/{n_tested_fc}")
    print(f"  PREFIX main effect: H={H_pre:.2f}, p={p_pre:.2e}")
    print(f"  REGIME main effect: H={H_reg:.2f}, p={p_reg:.2e}")
    if H_values:
        print(f"  Interaction CV: {H_cv:.3f}")

    # Verdict
    if n_stable >= n_tested * 0.6 and n_consistent >= n_tested_fc * 0.5:
        stab_verdict = 'POSITIONAL_GRAMMAR_UNIVERSAL'
        stab_detail = (f'{n_stable}/{n_tested} PREFIXes are regime-stable, '
                       f'{n_consistent}/{n_tested_fc} folio-consistent. '
                       f'PREFIX positional grammar is a universal feature '
                       f'of B grammar, not regime-dependent.')
    elif n_stable >= n_tested * 0.3:
        stab_verdict = 'POSITIONAL_GRAMMAR_MOSTLY_STABLE'
        stab_detail = (f'{n_stable}/{n_tested} regime-stable, '
                       f'{n_consistent}/{n_tested_fc} folio-consistent. '
                       f'Most PREFIX positions are stable across regimes '
                       f'with some variation.')
    else:
        stab_verdict = 'POSITIONAL_GRAMMAR_REGIME_DEPENDENT'
        stab_detail = (f'Only {n_stable}/{n_tested} regime-stable. '
                       f'PREFIX positional grammar varies by regime.')

    print(f"\n  VERDICT: {stab_verdict}")
    print(f"  {stab_detail}")

    # ── Output ───────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'PP_INFORMATION_DECOMPOSITION',
            'test': 'T4_PREFIX_REGIME_POSITIONAL_STABILITY',
            'min_tokens_per_cell': MIN_TOKENS_PER_CELL,
        },
        'regimes': regimes,
        'prefix_stability': prefix_stability,
        'n_stable': n_stable,
        'n_tested': n_tested,
        'main_effects': {
            'prefix_H': float(H_pre), 'prefix_p': float(p_pre),
            'regime_H': float(H_reg), 'regime_p': float(p_reg),
        },
        'interaction_within_regime': interaction_H,
        'folio_consistency': folio_consistency,
        'n_consistent': n_consistent,
        'n_tested_folio': n_tested_fc,
        'verdict': stab_verdict,
        'verdict_detail': stab_detail,
    }

    out_path = RESULTS_DIR / 't4_prefix_regime_positional_stability.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
