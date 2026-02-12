"""
T5c: Final suffix batching test — hold EN density constant.

If hazard adjacency differs at constant EN density between high/low suffix-run lines:
  → suffix composition within EN matters structurally.
If not:
  → batching is epiphenomenal. Close permanently.
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'


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

    # Build per-line features
    records = []
    for (folio, line), tokens in line_tokens.items():
        if len(tokens) < 5:
            continue
        n = len(tokens)
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

        # EN density
        en_count = sum(1 for r in roles if r == 'EN')
        en_frac = en_count / n

        # Max suffix run
        max_run = 1
        cur = 1
        for i in range(1, len(suffixes)):
            if suffixes[i] == suffixes[i-1]:
                cur += 1
                max_run = max(max_run, cur)
            else:
                cur = 1
        norm_run = max_run / n

        # Hazard adjacency rate
        haz_adj = 0
        for i in range(len(classes) - 1):
            if classes[i] is not None and classes[i+1] is not None:
                if (classes[i] in HAZARD) != (classes[i+1] in HAZARD):
                    haz_adj += 1
        haz_rate = haz_adj / (n - 1)

        records.append({
            'n': n, 'en_frac': en_frac, 'norm_run': norm_run,
            'haz_rate': haz_rate, 'max_run': max_run,
        })

    print(f"Lines (n>=5): {len(records)}")

    en_fracs = np.array([r['en_frac'] for r in records])
    norm_runs = np.array([r['norm_run'] for r in records])
    haz_rates = np.array([r['haz_rate'] for r in records])
    n_tokens = np.array([r['n'] for r in records])

    # Partial correlation: norm_run vs haz_rate, controlling for BOTH n_tokens AND en_frac
    def partial_corr_2(x, y, z1, z2):
        """Partial Spearman of x,y controlling for z1 and z2 via residualization."""
        from scipy.stats import rankdata
        rx = rankdata(x)
        ry = rankdata(y)
        rz1 = rankdata(z1)
        rz2 = rankdata(z2)
        # Regress out z1, z2 from rx and ry
        Z = np.column_stack([rz1, rz2, np.ones(len(x))])
        beta_x = np.linalg.lstsq(Z, rx, rcond=None)[0]
        beta_y = np.linalg.lstsq(Z, ry, rcond=None)[0]
        res_x = rx - Z @ beta_x
        res_y = ry - Z @ beta_y
        rho, p = stats.pearsonr(res_x, res_y)
        return float(rho), float(p)

    rho_raw, p_raw = stats.spearmanr(norm_runs, haz_rates)
    rho_ctrl_len, p_ctrl_len = partial_corr_2(norm_runs, haz_rates, n_tokens, n_tokens)  # just length
    rho_ctrl_both, p_ctrl_both = partial_corr_2(norm_runs, haz_rates, n_tokens, en_fracs)

    print(f"\n{'='*60}")
    print(f"SUFFIX CLUSTERING vs HAZARD ADJACENCY")
    print(f"{'='*60}")
    print(f"  Raw:                          rho = {rho_raw:+.4f}, p = {p_raw:.4e}")
    print(f"  Controlling line length:      rho = {rho_ctrl_len:+.4f}, p = {p_ctrl_len:.4e}")
    print(f"  Controlling length + EN frac: rho = {rho_ctrl_both:+.4f}, p = {p_ctrl_both:.4e}")

    # Matched comparison: bin by EN fraction, compare high/low clustering
    print(f"\n{'='*60}")
    print(f"MATCHED EN-DENSITY COMPARISON")
    print(f"{'='*60}")

    en_bins = [(0.3, 0.5), (0.5, 0.7), (0.7, 0.9)]
    all_high_haz = []
    all_low_haz = []

    for lo, hi in en_bins:
        mask = (en_fracs >= lo) & (en_fracs < hi)
        if mask.sum() < 40:
            continue
        nr = norm_runs[mask]
        hr = haz_rates[mask]
        median_nr = np.median(nr)
        high = nr > median_nr
        low = nr <= median_nr
        if high.sum() < 10 or low.sum() < 10:
            continue

        hr_high = hr[high]
        hr_low = hr[low]
        _, mw_p = stats.mannwhitneyu(hr_high, hr_low, alternative='two-sided')

        all_high_haz.extend(hr_high)
        all_low_haz.extend(hr_low)

        print(f"  EN frac [{lo:.1f}, {hi:.1f}): N={mask.sum()}")
        print(f"    High clustering: mean haz = {hr_high.mean():.4f} (n={high.sum()})")
        print(f"    Low clustering:  mean haz = {hr_low.mean():.4f} (n={low.sum()})")
        print(f"    Mann-Whitney p = {mw_p:.4f}")

    # Pooled matched
    if all_high_haz and all_low_haz:
        _, pool_p = stats.mannwhitneyu(all_high_haz, all_low_haz, alternative='two-sided')
        print(f"\n  Pooled matched:")
        print(f"    High clustering: mean haz = {np.mean(all_high_haz):.4f} (n={len(all_high_haz)})")
        print(f"    Low clustering:  mean haz = {np.mean(all_low_haz):.4f} (n={len(all_low_haz)})")
        print(f"    Mann-Whitney p = {pool_p:.4f}")

    # Verdict
    print(f"\n{'='*60}")
    print(f"VERDICT")
    print(f"{'='*60}")

    survives = abs(rho_ctrl_both) > 0.05 and p_ctrl_both < 0.01
    if survives:
        print(f"  Signal SURVIVES EN density control (rho={rho_ctrl_both:+.3f})")
        print(f"  Suffix composition within EN matters for hazard adjacency")
        verdict = 'SURVIVES_EN_CONTROL'
    else:
        print(f"  Signal COLLAPSES under EN density control (rho={rho_ctrl_both:+.3f})")
        print(f"  Batching is epiphenomenal — downstream of EN density")
        verdict = 'EPIPHENOMENAL'

    output = {
        'raw_rho': rho_raw, 'raw_p': p_raw,
        'ctrl_length_rho': rho_ctrl_len, 'ctrl_length_p': p_ctrl_len,
        'ctrl_both_rho': rho_ctrl_both, 'ctrl_both_p': p_ctrl_both,
        'verdict': verdict,
    }
    out_path = RESULTS_DIR / 't5c_en_density_control.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
