"""
Phase 661 s1 — DISTILLATION verb folio-binary partition test

Locked methodology per PRE_REGISTRATION.md (commit 780a509).

Single candidate: ke/ek ratio. Mann-Whitney U one-sided (positive > negative).
"""

import io
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from scripts.voynich import Transcript

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DISTILL_POS = ['f75r', 'f112r', 'f84r', 'f79r', 'f103r', 'f81v', 'f112v', 'f116r', 'f107r']
DISTILL_NEG = ['f82v', 'f76r', 'f82r', 'f76v', 'f77v']


def folio_ke_ek_ratio(toks):
    ke = sum(1 for t in toks if 'ke' in t)
    ek = sum(1 for t in toks if 'ek' in t)
    return ke / max(1, ek)


def folio_edy_pct(toks):
    if not toks:
        return 0
    return 100 * sum(1 for t in toks if t.endswith('edy')) / len(toks)


def mann_whitney_perm(pos_vals, neg_vals, n_perm=10000, seed=20260426):
    """One-sided permutation test: pos > neg."""
    obs_diff = sum(pos_vals) / len(pos_vals) - sum(neg_vals) / len(neg_vals)
    combined = pos_vals + neg_vals
    n_pos = len(pos_vals)
    rng = random.Random(seed)
    n_ge = 0
    for _ in range(n_perm):
        shuffled = combined[:]
        rng.shuffle(shuffled)
        p = shuffled[:n_pos]
        n = shuffled[n_pos:]
        d = sum(p) / len(p) - sum(n) / len(n)
        if d >= obs_diff:
            n_ge += 1
    return obs_diff, n_ge / n_perm


def main():
    out_dir = REPO_ROOT / 'phases' / 'PHASE_661_DISTILLATION_VERB_PARTITION' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('Loading Currier B tokens...')
    tx = Transcript()
    by_folio = defaultdict(list)
    target = set(DISTILL_POS + DISTILL_NEG)
    for tok in tx.currier_b():
        if tok.folio in target:
            by_folio[tok.folio].append(tok.word)

    pos_ratios = [folio_ke_ek_ratio(by_folio[f]) for f in DISTILL_POS]
    neg_ratios = [folio_ke_ek_ratio(by_folio[f]) for f in DISTILL_NEG]
    pos_edy = [folio_edy_pct(by_folio[f]) for f in DISTILL_POS]
    neg_edy = [folio_edy_pct(by_folio[f]) for f in DISTILL_NEG]

    print(f'\nDISTILL-POSITIVE (n={len(pos_ratios)}):')
    for f, r, e in zip(DISTILL_POS, pos_ratios, pos_edy):
        print(f'  {f}: ke/ek={r:.2f}  edy%={e:.2f}')
    print(f'\nDISTILL-NEGATIVE (n={len(neg_ratios)}):')
    for f, r, e in zip(DISTILL_NEG, neg_ratios, neg_edy):
        print(f'  {f}: ke/ek={r:.2f}  edy%={e:.2f}')

    print(f'\nMeans:')
    print(f'  ke/ek pos mean: {sum(pos_ratios)/len(pos_ratios):.2f}')
    print(f'  ke/ek neg mean: {sum(neg_ratios)/len(neg_ratios):.2f}')
    print(f'  edy%  pos mean: {sum(pos_edy)/len(pos_edy):.2f}')
    print(f'  edy%  neg mean: {sum(neg_edy)/len(neg_edy):.2f}')

    # Permutation test - primary endpoint
    obs_diff_ratio, p_pos_gt_neg = mann_whitney_perm(pos_ratios, neg_ratios)
    obs_diff_neg_gt_pos, p_neg_gt_pos = mann_whitney_perm(neg_ratios, pos_ratios)

    print(f'\nPrimary endpoint (ke/ek ratio):')
    print(f'  Observed pos-neg diff: {obs_diff_ratio:+.3f}')
    print(f'  p(pos >= neg)     = {p_pos_gt_neg:.4f}  [predicted direction]')
    print(f'  p(neg >= pos)     = {p_neg_gt_pos:.4f}  [reversed direction]')

    # Verdict per pre-reg
    if obs_diff_ratio > 0 and p_pos_gt_neg <= 0.05:
        verdict = 'SUPPORTED'
    elif obs_diff_ratio > 0 and p_pos_gt_neg <= 0.20:
        verdict = 'DIRECTIONAL'
    elif obs_diff_ratio < 0 and p_neg_gt_pos <= 0.05:
        verdict = 'FALSIFIED'
    elif obs_diff_ratio < 0 and p_neg_gt_pos <= 0.10:
        verdict = 'REVERSED-NULL'
    else:
        verdict = 'INCONCLUSIVE'
    print(f'\nVERDICT: {verdict}')

    out = {
        'phase': 661,
        'pre_registration_commit': '780a509',
        'partition': {
            'distill_positive': DISTILL_POS,
            'distill_negative': DISTILL_NEG,
        },
        'pos_values_ke_ek': dict(zip(DISTILL_POS, pos_ratios)),
        'neg_values_ke_ek': dict(zip(DISTILL_NEG, neg_ratios)),
        'pos_values_edy': dict(zip(DISTILL_POS, pos_edy)),
        'neg_values_edy': dict(zip(DISTILL_NEG, neg_edy)),
        'pos_mean_ke_ek': sum(pos_ratios)/len(pos_ratios),
        'neg_mean_ke_ek': sum(neg_ratios)/len(neg_ratios),
        'observed_diff_ke_ek': obs_diff_ratio,
        'p_predicted_direction': p_pos_gt_neg,
        'p_reversed_direction': p_neg_gt_pos,
        'verdict': verdict,
    }
    (out_dir / 'PARTITION_TEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'\nWrote results.')


if __name__ == '__main__':
    main()
