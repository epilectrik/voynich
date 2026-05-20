"""PHASE_714 follow-up: within-folio shuffle null for R5 folio-consistency.

Per expert-advisor scrutiny: R5's 94.9% folio-level CHSH-rate-above-baseline could
reflect folio composition (folios with hazards happen to also have CHSH-dominant EN
populations) rather than substrate-level post-hazard rule.

Test: shuffle EN-subfamily labels WITHIN each folio (preserves per-folio EN
composition, breaks the post-hazard ordering), recompute post-hazard CHSH rate
1000 times. If observed effect survives, R5 is substrate-level. If it collapses
to null, the "consistency" is composition shadow.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

HAZ_CLASSES = {7, 30}
N_PERM = 1000


def load_data():
    with open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    with open(ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
        en_census = json.load(f)
    qo_classes = set(en_census['prefix_families']['QO'])
    chsh_classes = set(en_census['prefix_families']['CH_SH'])
    all_en_classes = qo_classes | chsh_classes
    tx = Transcript()
    morph = Morphology()
    lines = defaultdict(list)
    for token in tx.currier_b():
        cls = token_to_class.get(token.word)
        m = morph.extract(token.word)
        en_subfamily = None
        if cls is not None and cls in all_en_classes:
            if m.prefix == 'qo':
                en_subfamily = 'QO'
            elif m.prefix in ('ch', 'sh'):
                en_subfamily = 'CHSH'
        is_haz = cls in HAZ_CLASSES if cls is not None else False
        lines[(token.folio, token.line)].append({
            'class': cls, 'en_subfamily': en_subfamily, 'is_haz': is_haz,
        })
    return lines


def compute_post_hazard_chsh_rate(lines):
    """Returns global post-hazard CHSH rate."""
    qo, chsh, total = 0, 0, 0
    for key, toks in lines.items():
        for i, t in enumerate(toks):
            if not t['is_haz']:
                continue
            for j in range(i + 1, len(toks)):
                if toks[j]['en_subfamily'] is not None:
                    if toks[j]['en_subfamily'] == 'CHSH':
                        chsh += 1
                    else:
                        qo += 1
                    total += 1
                    break
    return chsh / max(total, 1), total


def shuffle_en_within_folio(lines, rng):
    """Return a new lines dict with EN labels shuffled within each folio."""
    # Collect EN positions per folio
    folio_to_lines = defaultdict(list)
    for key in lines:
        folio_to_lines[key[0]].append(key)

    shuffled_lines = {}
    for folio, line_keys in folio_to_lines.items():
        # Collect all EN-typed tokens in this folio (preserve order)
        en_positions = []  # list of (line_key, token_idx)
        en_labels = []  # list of EN subfamily
        for lk in line_keys:
            for ti, t in enumerate(lines[lk]):
                if t['en_subfamily'] is not None:
                    en_positions.append((lk, ti))
                    en_labels.append(t['en_subfamily'])

        # Shuffle the EN labels
        shuffled_labels = en_labels.copy()
        rng.shuffle(shuffled_labels)

        # Apply shuffled labels back
        for lk in line_keys:
            new_toks = [dict(t) for t in lines[lk]]
            shuffled_lines[lk] = new_toks

        for (lk, ti), lab in zip(en_positions, shuffled_labels):
            shuffled_lines[lk][ti]['en_subfamily'] = lab

    return shuffled_lines


def compute_per_folio_chsh_rates(lines):
    """For each folio with hazards+EN, compute the post-hazard CHSH rate."""
    per_folio = defaultdict(lambda: {'CHSH': 0, 'QO': 0, 'total': 0})
    for (folio, line_num), toks in lines.items():
        for i, t in enumerate(toks):
            if not t['is_haz']:
                continue
            for j in range(i + 1, len(toks)):
                if toks[j]['en_subfamily'] is not None:
                    per_folio[folio][toks[j]['en_subfamily']] += 1
                    per_folio[folio]['total'] += 1
                    break
    rates = []
    for folio, d in per_folio.items():
        if d['total'] >= 3:
            rates.append(d['CHSH'] / d['total'])
    return rates


def main():
    print("=" * 80)
    print("WITHIN-FOLIO SHUFFLE NULL FOR R5 (FOLIO CONSISTENCY)")
    print("=" * 80)

    lines = load_data()
    print(f"\nLoading: {len(lines)} Currier B lines")

    # Observed global rate
    obs_global_rate, n_haz_events = compute_post_hazard_chsh_rate(lines)
    print(f"Observed post-hazard CHSH rate (global): {obs_global_rate:.4f} (n={n_haz_events})")

    # Observed per-folio fraction above baseline
    baseline_chsh = 0.553  # from PHASE_714 main
    obs_folio_rates = compute_per_folio_chsh_rates(lines)
    obs_n_folios = len(obs_folio_rates)
    obs_frac_above = sum(1 for r in obs_folio_rates if r > 0.447) / max(obs_n_folios, 1)
    obs_mean_folio_rate = float(np.mean(obs_folio_rates)) if obs_folio_rates else 0
    print(f"Observed: {obs_n_folios} folios with ≥3 events, "
          f"{obs_frac_above:.2%} above baseline CHSH 0.447, "
          f"mean folio rate {obs_mean_folio_rate:.4f}")

    # Within-folio shuffle null
    print(f"\nRunning {N_PERM} within-folio shuffles...")
    rng = np.random.default_rng(42)
    null_global = []
    null_frac_above = []
    null_mean_rate = []
    for trial in range(N_PERM):
        shuf = shuffle_en_within_folio(lines, rng)
        g_rate, _ = compute_post_hazard_chsh_rate(shuf)
        f_rates = compute_per_folio_chsh_rates(shuf)
        if f_rates:
            f_above = sum(1 for r in f_rates if r > 0.447) / len(f_rates)
            f_mean = float(np.mean(f_rates))
        else:
            f_above = 0
            f_mean = 0
        null_global.append(g_rate)
        null_frac_above.append(f_above)
        null_mean_rate.append(f_mean)
        if (trial + 1) % 100 == 0:
            print(f"  ... trial {trial + 1}/{N_PERM}")

    null_global = np.array(null_global)
    null_frac_above = np.array(null_frac_above)
    null_mean_rate = np.array(null_mean_rate)

    print(f"\nGLOBAL CHSH RATE (R5 main test):")
    print(f"  Observed: {obs_global_rate:.4f}")
    print(f"  Null mean: {null_global.mean():.4f}, p95={np.percentile(null_global, 95):.4f}, "
          f"p99={np.percentile(null_global, 99):.4f}")
    p_emp_global = float(np.mean(null_global >= obs_global_rate))
    print(f"  p_empirical: {p_emp_global:.4f}")
    print(f"  Passes within-folio shuffle null: {obs_global_rate > np.percentile(null_global, 99)}")

    print(f"\nFRACTION OF FOLIOS ABOVE BASELINE (R5 specific):")
    print(f"  Observed: {obs_frac_above:.4f}")
    print(f"  Null mean: {null_frac_above.mean():.4f}, p95={np.percentile(null_frac_above, 95):.4f}, "
          f"p99={np.percentile(null_frac_above, 99):.4f}")
    p_emp_frac = float(np.mean(null_frac_above >= obs_frac_above))
    print(f"  p_empirical: {p_emp_frac:.4f}")
    print(f"  Passes within-folio shuffle null: {obs_frac_above > np.percentile(null_frac_above, 99)}")

    print(f"\nMEAN ACROSS-FOLIO CHSH RATE:")
    print(f"  Observed: {obs_mean_folio_rate:.4f}")
    print(f"  Null mean: {null_mean_rate.mean():.4f}, p95={np.percentile(null_mean_rate, 95):.4f}, "
          f"p99={np.percentile(null_mean_rate, 99):.4f}")
    p_emp_mean = float(np.mean(null_mean_rate >= obs_mean_folio_rate))
    print(f"  p_empirical: {p_emp_mean:.4f}")
    print(f"  Passes within-folio shuffle null: {obs_mean_folio_rate > np.percentile(null_mean_rate, 99)}")

    # Save
    out = {
        'method': 'PHASE_714 within-folio shuffle null for R5',
        'n_permutations': N_PERM,
        'observed_global_chsh_rate': obs_global_rate,
        'observed_frac_folios_above_baseline': obs_frac_above,
        'observed_mean_across_folio_rate': obs_mean_folio_rate,
        'n_folios_with_data': obs_n_folios,
        'null_global_chsh_rate': {
            'mean': float(null_global.mean()),
            'p95': float(np.percentile(null_global, 95)),
            'p99': float(np.percentile(null_global, 99)),
            'p_empirical': p_emp_global,
            'passes_p99': obs_global_rate > float(np.percentile(null_global, 99)),
        },
        'null_frac_folios_above_baseline': {
            'mean': float(null_frac_above.mean()),
            'p95': float(np.percentile(null_frac_above, 95)),
            'p99': float(np.percentile(null_frac_above, 99)),
            'p_empirical': p_emp_frac,
            'passes_p99': obs_frac_above > float(np.percentile(null_frac_above, 99)),
        },
        'null_mean_across_folio_rate': {
            'mean': float(null_mean_rate.mean()),
            'p95': float(np.percentile(null_mean_rate, 95)),
            'p99': float(np.percentile(null_mean_rate, 99)),
            'p_empirical': p_emp_mean,
            'passes_p99': obs_mean_folio_rate > float(np.percentile(null_mean_rate, 99)),
        },
    }
    out_path = ROOT / 'phases' / 'PHASE_714_POSTHAZARD_REFINEMENT' / 'results' / 'within_folio_shuffle_null.json'
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {out_path.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
