"""
Phase 662 s1 — Thermal-iteration superclass folio-binary partition test

Locked methodology per PRE_REGISTRATION.md (commit d3fb478).

Superclass = DISTILLATION + PUTREFACTION + IMBIBITION + REFINEMENT.
Single candidate: ke/ek ratio. Cohen's d >= 0.5 required for SUPPORTED.
"""

import io
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from scripts.voynich import Transcript

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SUPERCLASS_CATS = {'DISTILLATION', 'PUTREFACTION', 'IMBIBITION', 'REFINEMENT'}

MATCHED_TABLE = {
    'III.19': 'f75r', 'III.11': 'f112r', 'III.28': 'f82v',
    'II.18':  'f76r', 'II.14':  'f84r',  'III.12': 'f79r',
    'III.22': 'f82r', 'III.16': 'f103r', 'III.15': 'f76v',
    'III.27': 'f77v', 'III.18': 'f81v',  'III.1':  'f112v',
    'III.4':  'f116r','III.44': 'f107r',
}


def chapter_id(s):
    return '.'.join(s.split('.')[:2])


def folio_ke_ek_ratio(toks):
    ke = sum(1 for t in toks if 'ke' in t)
    ek = sum(1 for t in toks if 'ek' in t)
    return ke / max(1, ek)


def cohens_d(a, b):
    """Cohen's d for two independent samples."""
    if not a or not b:
        return 0.0
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    if len(a) > 1:
        sa = sum((x - ma) ** 2 for x in a) / (len(a) - 1)
    else:
        sa = 0
    if len(b) > 1:
        sb = sum((x - mb) ** 2 for x in b) / (len(b) - 1)
    else:
        sb = 0
    pooled_var = ((len(a) - 1) * sa + (len(b) - 1) * sb) / max(1, len(a) + len(b) - 2)
    pooled_sd = math.sqrt(pooled_var) if pooled_var > 0 else 0
    return (ma - mb) / pooled_sd if pooled_sd > 0 else 0.0


def perm_test(pos_vals, neg_vals, n_perm=10000, seed=20260426):
    obs_diff = sum(pos_vals) / len(pos_vals) - sum(neg_vals) / len(neg_vals)
    combined = pos_vals + neg_vals
    n_pos = len(pos_vals)
    rng = random.Random(seed)
    n_ge = 0
    for _ in range(n_perm):
        shuffled = combined[:]
        rng.shuffle(shuffled)
        d = sum(shuffled[:n_pos]) / n_pos - sum(shuffled[n_pos:]) / (len(combined) - n_pos)
        if d >= obs_diff:
            n_ge += 1
    return obs_diff, n_ge / n_perm


def main():
    out_dir = REPO_ROOT / 'phases' / 'PHASE_662_THERMAL_ITERATION_SUPERCLASS' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load verb corpus
    verb_path = REPO_ROOT / 'phases' / 'PHASE_660_OPERATOR_VERB_INVENTORY' / 'results' / 'VERB_CORPUS.json'
    v = json.loads(verb_path.read_text(encoding='utf-8'))

    # Build chapter -> set of categories present
    chapter_cats = defaultdict(set)
    chapter_verb_counts = defaultdict(lambda: defaultdict(int))
    for r in v['instances']:
        ch = chapter_id(r['subrecipe_id'])
        chapter_cats[ch].add(r['category'])
        chapter_verb_counts[ch][r['category']] += 1

    # Compute partition per locked rule
    superclass_pos = []
    superclass_neg = []
    for ch, folio in MATCHED_TABLE.items():
        cats_in_ch = chapter_cats.get(ch, set())
        has_superclass = bool(cats_in_ch & SUPERCLASS_CATS)
        cat_counts = {c: chapter_verb_counts[ch].get(c, 0) for c in SUPERCLASS_CATS}
        if has_superclass:
            superclass_pos.append((ch, folio, cat_counts))
        else:
            superclass_neg.append((ch, folio, cat_counts))

    print('Locked partition (computed deterministically from verb corpus):')
    print()
    print(f'SUPERCLASS-POSITIVE (n={len(superclass_pos)}):')
    for ch, folio, counts in superclass_pos:
        active = {c: n for c, n in counts.items() if n > 0}
        print(f'  {ch:>8} -> {folio:>6}  : {active}')
    print()
    print(f'SUPERCLASS-NEGATIVE (n={len(superclass_neg)}):')
    for ch, folio, counts in superclass_neg:
        print(f'  {ch:>8} -> {folio:>6}  : (no thermal-iteration verbs)')

    # Load tokens
    target_folios = [f for _, f, _ in superclass_pos] + [f for _, f, _ in superclass_neg]
    tx = Transcript()
    by_folio = defaultdict(list)
    for tok in tx.currier_b():
        if tok.folio in set(target_folios):
            by_folio[tok.folio].append(tok.word)

    pos_folios = [f for _, f, _ in superclass_pos]
    neg_folios = [f for _, f, _ in superclass_neg]
    pos_ratios = [folio_ke_ek_ratio(by_folio[f]) for f in pos_folios]
    neg_ratios = [folio_ke_ek_ratio(by_folio[f]) for f in neg_folios]

    print(f'\nke/ek ratios:')
    print(f'  positive: {dict(zip(pos_folios, [f"{r:.2f}" for r in pos_ratios]))}')
    print(f'  negative: {dict(zip(neg_folios, [f"{r:.2f}" for r in neg_ratios]))}')

    pos_mean = sum(pos_ratios) / len(pos_ratios) if pos_ratios else 0
    neg_mean = sum(neg_ratios) / len(neg_ratios) if neg_ratios else 0

    print(f'\n  pos mean: {pos_mean:.3f}')
    print(f'  neg mean: {neg_mean:.3f}')

    # Cohen's d
    d = cohens_d(pos_ratios, neg_ratios)
    print(f"  Cohen's d (pos - neg): {d:+.3f}")

    # Permutation
    if pos_ratios and neg_ratios:
        obs_diff, p_pos_gt = perm_test(pos_ratios, neg_ratios)
        _, p_neg_gt = perm_test(neg_ratios, pos_ratios)
    else:
        obs_diff = 0
        p_pos_gt = 1.0
        p_neg_gt = 1.0

    print(f'\n  Observed pos-neg diff: {obs_diff:+.3f}')
    print(f'  p(pos >= neg)  = {p_pos_gt:.4f}  [predicted]')
    print(f'  p(neg >= pos)  = {p_neg_gt:.4f}  [reversed]')

    # Verdict per pre-reg (effect-size bar locked)
    if obs_diff > 0 and p_pos_gt <= 0.05 and d >= 0.5:
        verdict = 'SUPPORTED'
    elif obs_diff > 0 and p_pos_gt <= 0.20 and d >= 0.3:
        verdict = 'DIRECTIONAL'
    elif obs_diff < 0 and p_neg_gt <= 0.05:
        verdict = 'FALSIFIED'
    elif obs_diff < 0 and p_neg_gt <= 0.10:
        verdict = 'REVERSED-NULL'
    else:
        verdict = 'INCONCLUSIVE'

    print(f'\nVERDICT: {verdict}')

    out = {
        'phase': 662,
        'pre_registration_commit': 'd3fb478',
        'superclass_categories': sorted(SUPERCLASS_CATS),
        'partition': {
            'superclass_positive': [(ch, f) for ch, f, _ in superclass_pos],
            'superclass_negative': [(ch, f) for ch, f, _ in superclass_neg],
        },
        'pos_values': dict(zip(pos_folios, pos_ratios)),
        'neg_values': dict(zip(neg_folios, neg_ratios)),
        'pos_mean': pos_mean,
        'neg_mean': neg_mean,
        'observed_diff': obs_diff,
        'cohens_d': d,
        'p_predicted': p_pos_gt,
        'p_reversed': p_neg_gt,
        'verdict': verdict,
    }
    (out_dir / 'PARTITION_TEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'\nWrote results.')


if __name__ == '__main__':
    main()
