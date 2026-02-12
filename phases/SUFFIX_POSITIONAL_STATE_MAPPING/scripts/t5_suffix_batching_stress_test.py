"""
T5: Suffix Batching Stress Test
================================
Phase: SUFFIX_POSITIONAL_STATE_MAPPING

Quick stress test: do suffix runs (especially edy-runs) alter execution dynamics?

Four tests:
  1. Hazard adjacency: do long suffix-runs increase/decrease hazard proximity?
  2. Lane switch: do suffix-runs alter EN↔AX lane switch probability?
  3. Recovery path: do suffix-runs change recovery class distribution?
  4. Regime effect: does clustering intensity differ by REGIME?

If all four are flat → close as MORPHOLOGICAL_BATCHING (non-executive).
If any shows significant effect → suffix batching is architecturally relevant.

Output: t5_suffix_batching_stress_test.json
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


def load_class_map():
    path = PROJECT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
    with open(path) as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    all_cls = sorted(set(token_to_class.values()))
    EN = ({8} | set(range(31, 50)) - {7, 30, 38, 40}) & set(all_cls)
    FL = {7, 30, 38, 40} & set(all_cls)
    CC = {10, 11, 12} & set(all_cls)
    FQ = {9, 13, 14, 23} & set(all_cls)
    AX = set(all_cls) - EN - FL - CC - FQ

    # Hazard classes from BCSC
    HAZARD = {7, 10, 11, 30, 38}

    class_to_role = {}
    for c in all_cls:
        if c in CC: class_to_role[c] = 'CC'
        elif c in FQ: class_to_role[c] = 'FQ'
        elif c in EN: class_to_role[c] = 'EN'
        elif c in FL: class_to_role[c] = 'FL'
        elif c in AX: class_to_role[c] = 'AX'
    return token_to_class, class_to_role, HAZARD


def main():
    morph = Morphology()
    tx = Transcript()
    token_to_class, class_to_role, HAZARD = load_class_map()

    with open(PROJECT / 'data' / 'regime_folio_mapping.json') as f:
        regime_data = json.load(f)
    folio_to_regime = {
        f: d['regime']
        for f, d in regime_data['regime_assignments'].items()
    }

    # ── Build line-level data ──────────────────────────────
    print("Building line data...")

    unique_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w and '*' not in w:
            unique_words.add(w)
    word_morph = {w: morph.extract(w) for w in unique_words}

    line_tokens = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        line_tokens[(token.folio, token.line)].append(token)

    # ── Annotate each line ─────────────────────────────────
    print("Annotating lines...")

    line_data = []
    for (folio, line), tokens in line_tokens.items():
        if len(tokens) < 3:
            continue

        regime = folio_to_regime.get(folio, 'UNKNOWN')
        suffixes = []
        roles = []
        classes = []

        for tok in tokens:
            w = tok.word.strip()
            m = word_morph.get(w)
            suf = (m.suffix or 'NONE') if m and m.middle else 'NONE'
            cls = token_to_class.get(w)
            role = class_to_role.get(cls, 'UNK') if cls is not None else 'UNK'

            suffixes.append(suf)
            roles.append(role)
            classes.append(cls)

        # Compute suffix runs
        runs = []
        current_suf = suffixes[0]
        current_len = 1
        for i in range(1, len(suffixes)):
            if suffixes[i] == current_suf:
                current_len += 1
            else:
                runs.append((current_suf, current_len))
                current_suf = suffixes[i]
                current_len = 1
        runs.append((current_suf, current_len))

        max_run = max(r[1] for r in runs)
        max_run_suf = max(runs, key=lambda r: r[1])[0]

        # Suffix-specific runs
        edy_runs = [r[1] for r in runs if r[0] == 'edy']
        max_edy_run = max(edy_runs) if edy_runs else 0

        # Hazard adjacency count
        hazard_adj = 0
        for i in range(len(classes) - 1):
            if classes[i] is not None and classes[i + 1] is not None:
                if (classes[i] in HAZARD) != (classes[i + 1] in HAZARD):
                    if classes[i] in HAZARD or classes[i + 1] in HAZARD:
                        hazard_adj += 1

        # Lane switches (EN↔AX transitions)
        lane_switches = 0
        for i in range(len(roles) - 1):
            if roles[i] in ('EN', 'AX') and roles[i + 1] in ('EN', 'AX'):
                if roles[i] != roles[i + 1]:
                    lane_switches += 1

        # Number of distinct roles
        role_set = set(r for r in roles if r != 'UNK')

        line_data.append({
            'folio': folio,
            'regime': regime,
            'n_tokens': len(tokens),
            'max_run': max_run,
            'max_run_suf': max_run_suf,
            'max_edy_run': max_edy_run,
            'hazard_adj': hazard_adj,
            'lane_switches': lane_switches,
            'n_runs': len(runs),
            'suffixes': suffixes,
            'roles': roles,
            'classes': classes,
        })

    print(f"  Lines: {len(line_data)}")

    # ── TEST 1: Hazard adjacency vs suffix run length ──────
    print(f"\n{'='*60}")
    print("TEST 1: Hazard adjacency vs max suffix run length")
    print(f"{'='*60}")

    max_runs = np.array([d['max_run'] for d in line_data])
    hazard_adj = np.array([d['hazard_adj'] for d in line_data])
    n_tokens = np.array([d['n_tokens'] for d in line_data])

    # Normalize hazard adjacency by line length
    hazard_rate = hazard_adj / (n_tokens - 1)

    # Correlate max run with hazard rate
    rho_haz, p_haz = stats.spearmanr(max_runs, hazard_rate)
    print(f"  Spearman rho(max_run, hazard_rate): {rho_haz:+.4f}, p={p_haz:.4f}")

    # Also: lines with long runs (>=3) vs short runs (1)
    long_mask = max_runs >= 3
    short_mask = max_runs == 1
    if long_mask.sum() > 10 and short_mask.sum() > 10:
        long_haz = hazard_rate[long_mask]
        short_haz = hazard_rate[short_mask]
        u_stat, u_p = stats.mannwhitneyu(long_haz, short_haz, alternative='two-sided')
        print(f"  Long-run lines (n={long_mask.sum()}): mean hazard rate = {long_haz.mean():.4f}")
        print(f"  Short-run lines (n={short_mask.sum()}): mean hazard rate = {short_haz.mean():.4f}")
        print(f"  Mann-Whitney U: p={u_p:.4f}")
    else:
        u_p = 1.0
        print(f"  Insufficient long/short lines for comparison")

    test1 = {
        'spearman_rho': float(rho_haz),
        'spearman_p': float(p_haz),
        'long_vs_short_p': float(u_p),
        'significant': bool(p_haz < 0.01 and abs(rho_haz) > 0.1),
    }

    # ── TEST 2: Lane switch probability vs suffix runs ─────
    print(f"\n{'='*60}")
    print("TEST 2: Lane switch rate vs max suffix run length")
    print(f"{'='*60}")

    lane_sw = np.array([d['lane_switches'] for d in line_data])
    # Count EN/AX pairs to normalize
    en_ax_pairs = []
    for d in line_data:
        pairs = 0
        for i in range(len(d['roles']) - 1):
            if d['roles'][i] in ('EN', 'AX') and d['roles'][i+1] in ('EN', 'AX'):
                pairs += 1
        en_ax_pairs.append(max(pairs, 1))
    en_ax_pairs = np.array(en_ax_pairs)
    lane_rate = lane_sw / en_ax_pairs

    rho_lane, p_lane = stats.spearmanr(max_runs, lane_rate)
    print(f"  Spearman rho(max_run, lane_switch_rate): {rho_lane:+.4f}, p={p_lane:.4f}")

    if long_mask.sum() > 10 and short_mask.sum() > 10:
        long_lane = lane_rate[long_mask]
        short_lane = lane_rate[short_mask]
        u_stat2, u_p2 = stats.mannwhitneyu(long_lane, short_lane, alternative='two-sided')
        print(f"  Long-run lines: mean lane rate = {long_lane.mean():.4f}")
        print(f"  Short-run lines: mean lane rate = {short_lane.mean():.4f}")
        print(f"  Mann-Whitney U: p={u_p2:.4f}")
    else:
        u_p2 = 1.0

    test2 = {
        'spearman_rho': float(rho_lane),
        'spearman_p': float(p_lane),
        'long_vs_short_p': float(u_p2),
        'significant': bool(p_lane < 0.01 and abs(rho_lane) > 0.1),
    }

    # ── TEST 3: Recovery path distribution vs suffix runs ──
    print(f"\n{'='*60}")
    print("TEST 3: Recovery class distribution in long vs short run lines")
    print(f"{'='*60}")

    # Recovery classes: classes that follow hazard classes
    recovery_long = Counter()
    recovery_short = Counter()

    for d in line_data:
        is_long = d['max_run'] >= 3
        for i in range(len(d['classes']) - 1):
            if d['classes'][i] is not None and d['classes'][i] in HAZARD:
                next_cls = d['classes'][i + 1]
                if next_cls is not None:
                    role = class_to_role.get(next_cls, 'UNK')
                    if is_long:
                        recovery_long[role] += 1
                    else:
                        recovery_short[role] += 1

    all_roles = sorted(set(list(recovery_long.keys()) + list(recovery_short.keys())))
    total_long = sum(recovery_long.values())
    total_short = sum(recovery_short.values())

    print(f"  Recovery events: long-run lines={total_long}, short-run lines={total_short}")
    print(f"  {'Role':<8s} {'Long%':>8s} {'Short%':>8s}")
    print(f"  {'-'*8} {'-'*8} {'-'*8}")
    for role in all_roles:
        lp = recovery_long[role] / total_long * 100 if total_long > 0 else 0
        sp = recovery_short[role] / total_short * 100 if total_short > 0 else 0
        print(f"  {role:<8s} {lp:>7.1f}% {sp:>7.1f}%")

    # Chi-squared test on recovery distributions
    if total_long >= 20 and total_short >= 20:
        obs_long = np.array([recovery_long.get(r, 0) for r in all_roles])
        obs_short = np.array([recovery_short.get(r, 0) for r in all_roles])
        # Pool and compute expected
        combined = obs_long + obs_short
        exp_long = combined * (total_long / (total_long + total_short))
        exp_short = combined * (total_short / (total_long + total_short))
        # Filter out zero-expected
        mask = (exp_long > 0) & (exp_short > 0)
        if mask.sum() >= 2:
            chi2_rec = float(np.sum((obs_long[mask] - exp_long[mask])**2 / exp_long[mask]) +
                            np.sum((obs_short[mask] - exp_short[mask])**2 / exp_short[mask]))
            df_rec = int(mask.sum() - 1)
            p_rec = float(1 - stats.chi2.cdf(chi2_rec, df_rec))
            print(f"  Chi-squared: {chi2_rec:.2f}, df={df_rec}, p={p_rec:.4f}")
        else:
            chi2_rec, p_rec = 0.0, 1.0
    else:
        chi2_rec, p_rec = 0.0, 1.0
        print(f"  Insufficient recovery events for test")

    test3 = {
        'recovery_long': dict(recovery_long),
        'recovery_short': dict(recovery_short),
        'chi2': chi2_rec,
        'chi2_p': p_rec,
        'significant': bool(p_rec < 0.01),
    }

    # ── TEST 4: Regime effect on clustering intensity ──────
    print(f"\n{'='*60}")
    print("TEST 4: Clustering intensity by REGIME")
    print(f"{'='*60}")

    regime_runs = defaultdict(list)
    for d in line_data:
        if d['regime'] != 'UNKNOWN':
            # Clustering intensity = max_run / n_tokens (normalized)
            intensity = d['max_run'] / d['n_tokens']
            regime_runs[d['regime']].append(intensity)

    print(f"  {'Regime':<20s} {'N':>6s} {'Mean':>8s} {'Std':>8s}")
    print(f"  {'-'*20} {'-'*6} {'-'*8} {'-'*8}")
    for regime in sorted(regime_runs.keys()):
        vals = regime_runs[regime]
        print(f"  {regime:<20s} {len(vals):>6d} {np.mean(vals):>8.4f} {np.std(vals):>8.4f}")

    # Kruskal-Wallis across regimes
    regime_groups = [np.array(regime_runs[r]) for r in sorted(regime_runs.keys()) if len(regime_runs[r]) >= 10]
    if len(regime_groups) >= 2:
        h_stat, h_p = stats.kruskal(*regime_groups)
        print(f"  Kruskal-Wallis: H={h_stat:.2f}, p={h_p:.4f}")
    else:
        h_stat, h_p = 0.0, 1.0

    test4 = {
        'regime_means': {r: float(np.mean(v)) for r, v in regime_runs.items()},
        'regime_n': {r: len(v) for r, v in regime_runs.items()},
        'kruskal_H': float(h_stat),
        'kruskal_p': float(h_p),
        'significant': bool(h_p < 0.01),
    }

    # ── COMPOSITE ──────────────────────────────────────────
    print(f"\n{'='*60}")
    print("COMPOSITE VERDICT")
    print(f"{'='*60}")

    sig_count = sum([
        test1['significant'],
        test2['significant'],
        test3['significant'],
        test4['significant'],
    ])

    print(f"  Test 1 (hazard adjacency):    {'SIG' if test1['significant'] else 'FLAT'}")
    print(f"  Test 2 (lane switch):          {'SIG' if test2['significant'] else 'FLAT'}")
    print(f"  Test 3 (recovery path):        {'SIG' if test3['significant'] else 'FLAT'}")
    print(f"  Test 4 (regime clustering):    {'SIG' if test4['significant'] else 'FLAT'}")
    print(f"  Significant: {sig_count}/4")

    if sig_count >= 2:
        verdict = 'SUFFIX_BATCHING_ARCHITECTURALLY_RELEVANT'
        detail = f'{sig_count}/4 execution dynamics altered by suffix runs.'
    elif sig_count == 1:
        verdict = 'SUFFIX_BATCHING_MARGINAL'
        detail = f'{sig_count}/4 test marginally significant. Likely compositional.'
    else:
        verdict = 'MORPHOLOGICAL_BATCHING_ONLY'
        detail = 'Suffix clustering does not alter hazard, lane, recovery, or regime dynamics. Non-executive compositional clustering.'

    print(f"\n  VERDICT: {verdict}")
    print(f"  {detail}")

    # ── Output ─────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'SUFFIX_POSITIONAL_STATE_MAPPING',
            'test': 'T5_SUFFIX_BATCHING_STRESS_TEST',
        },
        'corpus': {
            'n_lines': len(line_data),
        },
        'test1_hazard_adjacency': test1,
        'test2_lane_switch': test2,
        'test3_recovery_path': test3,
        'test4_regime_clustering': test4,
        'significant_count': sig_count,
        'verdict': verdict,
        'verdict_detail': detail,
    }

    out_path = RESULTS_DIR / 't5_suffix_batching_stress_test.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
