"""
Phase 664 s1 — CONFIRMED vs supported match-tier paragraph stratification

Locked methodology per PRE_REGISTRATION.md (commit b9b16da).

T1: CONFIRMED paragraphs (f75r,f76r,f84r) vs supported superclass-positive paragraphs.
T2 (sanity check): CONFIRMED paragraphs vs full corpus paragraphs.
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

CONFIRMED = ['f75r', 'f76r', 'f84r']
SUPPORTED_POS = ['f112r', 'f82v', 'f79r', 'f82r', 'f103r', 'f81v', 'f112v', 'f116r', 'f107r']

MIN_PARA = 8


def extract_paragraphs(folio_tokens):
    paras = []
    current = []
    for tok in folio_tokens:
        if tok.par_initial and current:
            paras.append(current)
            current = []
        current.append(tok.word)
    if current:
        paras.append(current)
    return [p for p in paras if len(p) >= MIN_PARA]


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
    out_dir = REPO_ROOT / 'phases' / 'PHASE_664_CONFIRMED_TIER_STRATIFICATION' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('Loading Currier B tokens...')
    tx = Transcript()
    by_folio = defaultdict(list)
    for tok in tx.currier_b():
        by_folio[tok.folio].append(tok)
    all_folios = sorted(by_folio.keys())

    # Build per-folio paragraphs
    folio_paras = {}
    for f, toks in by_folio.items():
        folio_paras[f] = extract_paragraphs(toks)

    # T1 groups
    confirmed_paras = []
    confirmed_meta = []
    for f in CONFIRMED:
        for i, p in enumerate(folio_paras.get(f, [])):
            r = ke_ek_ratio(p)
            confirmed_paras.append(r)
            confirmed_meta.append({'folio': f, 'idx': i, 'n_tokens': len(p), 'ratio': r})

    supported_paras = []
    supported_meta = []
    for f in SUPPORTED_POS:
        for i, p in enumerate(folio_paras.get(f, [])):
            r = ke_ek_ratio(p)
            supported_paras.append(r)
            supported_meta.append({'folio': f, 'idx': i, 'n_tokens': len(p), 'ratio': r})

    # T2: full corpus paragraphs (excluding CONFIRMED)
    corpus_paras = []
    excluded = set(CONFIRMED)
    for f in all_folios:
        if f in excluded:
            continue
        for p in folio_paras.get(f, []):
            corpus_paras.append(ke_ek_ratio(p))

    print(f'\nT1: CONFIRMED paragraphs = {len(confirmed_paras)}')
    print(f'    supported paragraphs = {len(supported_paras)}')
    print(f'\nT2: corpus-wide paragraphs (excluding CONFIRMED) = {len(corpus_paras)}')

    # T1 stats
    c_mean = sum(confirmed_paras) / len(confirmed_paras)
    s_mean = sum(supported_paras) / len(supported_paras)
    d_t1 = cohens_d(confirmed_paras, supported_paras)
    obs_t1, p_t1_pred = perm_test(confirmed_paras, supported_paras)
    _, p_t1_rev = perm_test(supported_paras, confirmed_paras)

    print(f'\n=== T1: CONFIRMED vs supported ===')
    print(f'  CONFIRMED mean ke/ek: {c_mean:.3f}')
    print(f'  supported mean ke/ek: {s_mean:.3f}')
    print(f"  Cohen's d: {d_t1:+.3f}")
    print(f'  observed diff: {obs_t1:+.3f}')
    print(f'  p(predicted)  = {p_t1_pred:.4f}')
    print(f'  p(reversed)   = {p_t1_rev:.4f}')

    # T1 verdict per pre-reg
    if obs_t1 > 0 and p_t1_pred <= 0.05 and d_t1 >= 0.5:
        verdict_t1 = 'SUPPORTED'
    elif obs_t1 > 0 and p_t1_pred <= 0.20 and d_t1 >= 0.3:
        verdict_t1 = 'DIRECTIONAL'
    elif obs_t1 < 0 and p_t1_rev <= 0.05:
        verdict_t1 = 'FALSIFIED'
    elif obs_t1 < 0 and p_t1_rev <= 0.10:
        verdict_t1 = 'REVERSED-NULL'
    else:
        verdict_t1 = 'INCONCLUSIVE'
    print(f'\n  T1 VERDICT: {verdict_t1}')

    # T2 sanity check
    corpus_mean = sum(corpus_paras) / len(corpus_paras)
    d_t2 = cohens_d(confirmed_paras, corpus_paras)
    obs_t2, p_t2_pred = perm_test(confirmed_paras, corpus_paras)

    print(f'\n=== T2: CONFIRMED vs full corpus (excluding CONFIRMED) ===')
    print(f'  CONFIRMED mean ke/ek: {c_mean:.3f}')
    print(f'  corpus mean ke/ek:    {corpus_mean:.3f}')
    print(f"  Cohen's d: {d_t2:+.3f}")
    print(f'  observed diff: {obs_t2:+.3f}')
    print(f'  p(CONFIRMED >= corpus) = {p_t2_pred:.4f}')

    # Interpretation
    print(f'\n=== Interpretation ===')
    if c_mean > corpus_mean and c_mean > s_mean:
        print('  CONFIRMED elevated above BOTH corpus and supported')
        print('  -> match-tier signature interpretation supported')
    elif c_mean > s_mean and c_mean <= corpus_mean:
        print('  CONFIRMED above supported but at/below corpus mean')
        print('  -> supported tier is below-average, not CONFIRMED elevated')
    elif c_mean <= s_mean:
        print('  CONFIRMED not above supported -- T1 falsifies sensitivity finding')

    out = {
        'phase': 664,
        'pre_registration_commit': 'b9b16da',
        'T1': {
            'confirmed_n': len(confirmed_paras),
            'supported_n': len(supported_paras),
            'confirmed_mean': c_mean,
            'supported_mean': s_mean,
            'cohens_d': d_t1,
            'observed_diff': obs_t1,
            'p_predicted': p_t1_pred,
            'p_reversed': p_t1_rev,
            'verdict': verdict_t1,
        },
        'T2_sanity': {
            'corpus_n': len(corpus_paras),
            'corpus_mean': corpus_mean,
            'cohens_d': d_t2,
            'observed_diff': obs_t2,
            'p_predicted': p_t2_pred,
        },
        'confirmed_meta': confirmed_meta,
        'supported_meta': supported_meta,
    }
    (out_dir / 'STRATIFICATION_TEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'\nWrote results.')


if __name__ == '__main__':
    main()
