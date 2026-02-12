"""
T5b: Line-length confound check for suffix batching stress test.

The key confound: longer lines → longer suffix runs (trivially) AND longer lines →
more complex hazard dynamics. If max_run is just a proxy for line length,
the T5 results are artifacts.

Test: partial correlation of max_run with hazard rate, CONTROLLING for line length.
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
    HAZARD = {7, 10, 11, 30, 38}

    class_to_role = {}
    for c in all_cls:
        if c in CC: class_to_role[c] = 'CC'
        elif c in FQ: class_to_role[c] = 'FQ'
        elif c in EN: class_to_role[c] = 'EN'
        elif c in FL: class_to_role[c] = 'FL'
        elif c in AX: class_to_role[c] = 'AX'
    return token_to_class, class_to_role, HAZARD


def partial_spearman(x, y, z):
    """Partial Spearman correlation of x and y controlling for z."""
    rho_xz, _ = stats.spearmanr(x, z)
    rho_yz, _ = stats.spearmanr(y, z)
    rho_xy, _ = stats.spearmanr(x, y)

    denom = np.sqrt((1 - rho_xz**2) * (1 - rho_yz**2))
    if denom < 1e-10:
        return 0.0, 1.0
    partial_rho = (rho_xy - rho_xz * rho_yz) / denom
    # Approximate t-test
    n = len(x)
    t_stat = partial_rho * np.sqrt((n - 3) / (1 - partial_rho**2 + 1e-10))
    p_val = 2 * (1 - stats.t.cdf(abs(t_stat), n - 3))
    return float(partial_rho), float(p_val)


def main():
    morph = Morphology()
    tx = Transcript()
    token_to_class, class_to_role, HAZARD = load_class_map()

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

    # Build arrays
    max_runs = []
    hazard_rates = []
    lane_rates = []
    n_tokens_arr = []
    # Also: normalized run = max_run / n_tokens
    norm_runs = []

    for (folio, line), tokens in line_tokens.items():
        if len(tokens) < 3:
            continue

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

        # Runs
        runs_list = []
        current_suf = suffixes[0]
        current_len = 1
        for i in range(1, len(suffixes)):
            if suffixes[i] == current_suf:
                current_len += 1
            else:
                runs_list.append((current_suf, current_len))
                current_suf = suffixes[i]
                current_len = 1
        runs_list.append((current_suf, current_len))

        max_run = max(r[1] for r in runs_list)
        n = len(tokens)

        # Hazard rate
        hazard_adj = 0
        for i in range(len(classes) - 1):
            if classes[i] is not None and classes[i + 1] is not None:
                if (classes[i] in HAZARD) != (classes[i + 1] in HAZARD):
                    hazard_adj += 1
        haz_rate = hazard_adj / (n - 1)

        # Lane switch rate
        lane_sw = 0
        en_ax_pairs = 0
        for i in range(len(roles) - 1):
            if roles[i] in ('EN', 'AX') and roles[i+1] in ('EN', 'AX'):
                en_ax_pairs += 1
                if roles[i] != roles[i+1]:
                    lane_sw += 1
        lane_rate = lane_sw / max(en_ax_pairs, 1)

        max_runs.append(max_run)
        hazard_rates.append(haz_rate)
        lane_rates.append(lane_rate)
        n_tokens_arr.append(n)
        norm_runs.append(max_run / n)

    max_runs = np.array(max_runs)
    hazard_rates = np.array(hazard_rates)
    lane_rates = np.array(lane_rates)
    n_tokens_arr = np.array(n_tokens_arr)
    norm_runs = np.array(norm_runs)

    print(f"Lines: {len(max_runs)}")
    print(f"\nCorrelation of max_run with n_tokens:")
    rho_rn, p_rn = stats.spearmanr(max_runs, n_tokens_arr)
    print(f"  rho = {rho_rn:+.4f}, p = {p_rn:.4e}")

    # ── Raw correlations ───────────────────────────────────
    print(f"\n{'='*60}")
    print(f"RAW vs CONTROLLED CORRELATIONS")
    print(f"{'='*60}")

    rho_raw_haz, p_raw_haz = stats.spearmanr(max_runs, hazard_rates)
    rho_partial_haz, p_partial_haz = partial_spearman(max_runs, hazard_rates, n_tokens_arr)

    print(f"\n  HAZARD ADJACENCY RATE:")
    print(f"    Raw:     rho = {rho_raw_haz:+.4f}, p = {p_raw_haz:.4e}")
    print(f"    Partial: rho = {rho_partial_haz:+.4f}, p = {p_partial_haz:.4e} (controlling for n_tokens)")

    rho_raw_lane, p_raw_lane = stats.spearmanr(max_runs, lane_rates)
    rho_partial_lane, p_partial_lane = partial_spearman(max_runs, lane_rates, n_tokens_arr)

    print(f"\n  LANE SWITCH RATE:")
    print(f"    Raw:     rho = {rho_raw_lane:+.4f}, p = {p_raw_lane:.4e}")
    print(f"    Partial: rho = {rho_partial_lane:+.4f}, p = {p_partial_lane:.4e} (controlling for n_tokens)")

    # ── Normalized run (max_run/n_tokens) ──────────────────
    print(f"\n{'='*60}")
    print(f"USING NORMALIZED RUN LENGTH (max_run / n_tokens)")
    print(f"{'='*60}")

    rho_norm_haz, p_norm_haz = stats.spearmanr(norm_runs, hazard_rates)
    rho_norm_lane, p_norm_lane = stats.spearmanr(norm_runs, lane_rates)

    print(f"  Hazard rate:  rho = {rho_norm_haz:+.4f}, p = {p_norm_haz:.4e}")
    print(f"  Lane rate:    rho = {rho_norm_lane:+.4f}, p = {p_norm_lane:.4e}")

    # ── Matched line-length comparison ─────────────────────
    print(f"\n{'='*60}")
    print(f"MATCHED COMPARISON: Same line length, high vs low run clustering")
    print(f"{'='*60}")

    # Focus on lines of length 8-12 (common range)
    for target_len in [8, 9, 10, 11, 12]:
        mask = n_tokens_arr == target_len
        if mask.sum() < 40:
            continue
        mr = max_runs[mask]
        hr = hazard_rates[mask]
        lr = lane_rates[mask]

        median_run = np.median(mr)
        high = mr > median_run
        low = mr <= median_run

        if high.sum() < 10 or low.sum() < 10:
            continue

        hr_high = hr[high].mean()
        hr_low = hr[low].mean()
        _, p_mw = stats.mannwhitneyu(hr[high], hr[low], alternative='two-sided')

        print(f"  n_tokens={target_len} (N={mask.sum()}):")
        print(f"    High-clustering hazard rate: {hr_high:.4f}")
        print(f"    Low-clustering hazard rate:  {hr_low:.4f}")
        print(f"    Mann-Whitney p={p_mw:.4f}")

    # ── Summary ────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"CONFOUND CHECK SUMMARY")
    print(f"{'='*60}")

    survives_haz = abs(rho_partial_haz) > 0.05 and p_partial_haz < 0.01
    survives_lane = abs(rho_partial_lane) > 0.05 and p_partial_lane < 0.01

    print(f"  max_run correlates with n_tokens: rho={rho_rn:+.3f} (confound exists)")
    print(f"  Hazard-rate partial correlation survives:  {'YES' if survives_haz else 'NO'} "
          f"(rho={rho_partial_haz:+.3f})")
    print(f"  Lane-rate partial correlation survives:    {'YES' if survives_lane else 'NO'} "
          f"(rho={rho_partial_lane:+.3f})")

    if survives_haz:
        print(f"\n  RESULT: Suffix batching signal SURVIVES line-length control for hazard adjacency")
    else:
        print(f"\n  RESULT: Suffix batching signal is a LINE-LENGTH ARTIFACT")


if __name__ == '__main__':
    main()
