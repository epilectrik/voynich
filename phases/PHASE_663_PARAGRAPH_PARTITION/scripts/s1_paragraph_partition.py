"""
Phase 663 s1 — Paragraph-level thermal-iteration superclass partition

Locked methodology per PRE_REGISTRATION.md (commit 766b78a).

Test ke/ek ratio at paragraph level. Min paragraph size = 8 tokens (per C1961).
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

SUPER_POS = ['f75r', 'f112r', 'f82v', 'f76r', 'f84r', 'f79r', 'f82r', 'f103r',
             'f81v', 'f112v', 'f116r', 'f107r']
SUPER_NEG = ['f76v', 'f77v']

CONFIRMED = {'f75r', 'f76r', 'f84r'}
MIN_PARA = 8


def extract_paragraphs(folio_tokens):
    """Group tokens into paragraphs by par_initial markers; return list of token-word lists."""
    paras = []
    current = []
    for tok in folio_tokens:
        if tok.par_initial and current:
            paras.append(current)
            current = []
        current.append(tok.word)
    if current:
        paras.append(current)
    return paras


def ke_ek_ratio(words):
    ke = sum(1 for w in words if 'ke' in w)
    ek = sum(1 for w in words if 'ek' in w)
    return ke / max(1, ek)


def cohens_d(a, b):
    if not a or not b:
        return 0.0
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    sa = sum((x - ma) ** 2 for x in a) / max(1, len(a) - 1)
    sb = sum((x - mb) ** 2 for x in b) / max(1, len(b) - 1)
    pooled = ((len(a) - 1) * sa + (len(b) - 1) * sb) / max(1, len(a) + len(b) - 2)
    sd = math.sqrt(pooled) if pooled > 0 else 0
    return (ma - mb) / sd if sd > 0 else 0.0


def perm_test(pos, neg, n_perm=10000, seed=20260426):
    obs = sum(pos) / len(pos) - sum(neg) / len(neg)
    combined = pos + neg
    n_pos = len(pos)
    rng = random.Random(seed)
    n_ge = 0
    for _ in range(n_perm):
        s = combined[:]
        rng.shuffle(s)
        d = sum(s[:n_pos]) / n_pos - sum(s[n_pos:]) / (len(combined) - n_pos)
        if d >= obs:
            n_ge += 1
    return obs, n_ge / n_perm


def main():
    out_dir = REPO_ROOT / 'phases' / 'PHASE_663_PARAGRAPH_PARTITION' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('Loading Currier B tokens...')
    tx = Transcript()
    by_folio = defaultdict(list)
    target = set(SUPER_POS + SUPER_NEG)
    for tok in tx.currier_b():
        if tok.folio in target:
            by_folio[tok.folio].append(tok)

    # Extract paragraphs per folio, filter by MIN_PARA
    folio_paras = {}
    for f, toks in by_folio.items():
        paras = extract_paragraphs(toks)
        kept = [p for p in paras if len(p) >= MIN_PARA]
        folio_paras[f] = kept
        print(f'  {f}: {len(paras)} paragraphs raw, {len(kept)} >= {MIN_PARA} tokens')

    # Compute paragraph-level ke/ek ratios
    pos_ratios = []
    pos_meta = []
    for f in SUPER_POS:
        for i, para in enumerate(folio_paras.get(f, [])):
            r = ke_ek_ratio(para)
            pos_ratios.append(r)
            pos_meta.append({'folio': f, 'para_idx': i, 'ratio': r,
                             'n_tokens': len(para),
                             'is_confirmed': f in CONFIRMED})

    neg_ratios = []
    neg_meta = []
    for f in SUPER_NEG:
        for i, para in enumerate(folio_paras.get(f, [])):
            r = ke_ek_ratio(para)
            neg_ratios.append(r)
            neg_meta.append({'folio': f, 'para_idx': i, 'ratio': r,
                             'n_tokens': len(para)})

    print(f'\nPositive paragraphs: {len(pos_ratios)}')
    print(f'Negative paragraphs: {len(neg_ratios)}')

    pos_mean = sum(pos_ratios) / len(pos_ratios) if pos_ratios else 0
    neg_mean = sum(neg_ratios) / len(neg_ratios) if neg_ratios else 0
    print(f'\n  pos mean ke/ek: {pos_mean:.3f}')
    print(f'  neg mean ke/ek: {neg_mean:.3f}')

    d = cohens_d(pos_ratios, neg_ratios)
    print(f"  Cohen's d: {d:+.3f}")

    obs_diff, p_pred = perm_test(pos_ratios, neg_ratios)
    _, p_rev = perm_test(neg_ratios, pos_ratios)
    print(f'\n  observed diff: {obs_diff:+.3f}')
    print(f'  p(predicted)  = {p_pred:.4f}')
    print(f'  p(reversed)   = {p_rev:.4f}')

    # Verdict per pre-reg
    if obs_diff > 0 and p_pred <= 0.05 and d >= 0.3:
        verdict = 'SUPPORTED'
    elif obs_diff > 0 and p_pred <= 0.20 and d >= 0.2:
        verdict = 'DIRECTIONAL'
    elif obs_diff < 0 and p_rev <= 0.05:
        verdict = 'FALSIFIED'
    elif obs_diff < 0 and p_rev <= 0.10:
        verdict = 'REVERSED-NULL'
    else:
        verdict = 'INCONCLUSIVE'
    print(f'\nVERDICT: {verdict}')

    # Sensitivity: CONFIRMED-only paragraphs vs supported paragraphs (within positive)
    conf_ratios = [m['ratio'] for m in pos_meta if m['is_confirmed']]
    supp_ratios = [m['ratio'] for m in pos_meta if not m['is_confirmed']]
    if conf_ratios and supp_ratios:
        c_mean = sum(conf_ratios) / len(conf_ratios)
        s_mean = sum(supp_ratios) / len(supp_ratios)
        print(f'\nSensitivity check (within positive group):')
        print(f'  CONFIRMED ({len(conf_ratios)} paras): mean ke/ek = {c_mean:.3f}')
        print(f'  Supported ({len(supp_ratios)} paras): mean ke/ek = {s_mean:.3f}')

    out = {
        'phase': 663,
        'pre_registration_commit': '766b78a',
        'min_paragraph_tokens': MIN_PARA,
        'positive_folios': SUPER_POS,
        'negative_folios': SUPER_NEG,
        'n_positive_paragraphs': len(pos_ratios),
        'n_negative_paragraphs': len(neg_ratios),
        'pos_mean': pos_mean,
        'neg_mean': neg_mean,
        'cohens_d': d,
        'observed_diff': obs_diff,
        'p_predicted': p_pred,
        'p_reversed': p_rev,
        'verdict': verdict,
        'positive_paragraphs': pos_meta,
        'negative_paragraphs': neg_meta,
    }
    if conf_ratios and supp_ratios:
        out['sensitivity_within_positive'] = {
            'confirmed_n': len(conf_ratios),
            'confirmed_mean': sum(conf_ratios) / len(conf_ratios),
            'supported_n': len(supp_ratios),
            'supported_mean': sum(supp_ratios) / len(supp_ratios),
        }
    (out_dir / 'PARTITION_TEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'\nWrote results.')


if __name__ == '__main__':
    main()
