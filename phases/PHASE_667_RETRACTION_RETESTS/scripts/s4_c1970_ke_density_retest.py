"""
Phase 667 s4 — C1970 retest: ke-density balneum signature

Original claim: CONFIRMED ke/ek ratio = 9.74 vs supported = 5.03, d=+1.04.
Problem 1: ke/max(1,ek) has inconsistent units (ratio when ek>0, count when ek=0).
Problem 2: Pre-reg said Mann-Whitney U, code did mean-difference permutation.
Problem 3: LOO came from unincluded script.

Fix: Use ke/(ke+ek) proportion (bounded 0-1, consistent units).
Proper permutation test with LOO included in same script.
"""
import sys
import io
import json
import math
import random
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scripts.voynich import Transcript

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


def ke_proportion(words):
    """ke/(ke+ek) proportion. Returns 0.5 if both are 0 (neutral)."""
    ke = sum(1 for w in words if 'ke' in w)
    ek = sum(1 for w in words if 'ek' in w)
    total = ke + ek
    if total == 0:
        return 0.5
    return ke / total


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


def perm_test(pos, neg, n_perm=10000, seed=20260427):
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
    out_dir = REPO_ROOT / 'phases' / 'PHASE_667_RETRACTION_RETESTS' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    tx = Transcript()
    by_folio = defaultdict(list)
    for tok in tx.currier_b():
        by_folio[tok.folio].append(tok)

    folio_paras = {}
    for f, toks in by_folio.items():
        folio_paras[f] = extract_paragraphs(toks)

    # Build groups
    confirmed_vals = []
    confirmed_meta = []
    for f in CONFIRMED:
        for i, p in enumerate(folio_paras.get(f, [])):
            v = ke_proportion(p)
            confirmed_vals.append(v)
            confirmed_meta.append({'folio': f, 'idx': i, 'n_tokens': len(p), 'ke_prop': v})

    supported_vals = []
    for f in SUPPORTED_POS:
        for i, p in enumerate(folio_paras.get(f, [])):
            supported_vals.append(ke_proportion(p))

    # Corpus baseline (excluding CONFIRMED)
    excluded = set(CONFIRMED)
    corpus_vals = []
    for f in sorted(by_folio.keys()):
        if f in excluded:
            continue
        for p in folio_paras.get(f, []):
            corpus_vals.append(ke_proportion(p))

    print('=== C1970 Retest: ke-Density Balneum Signature ===')
    print(f'Metric: ke/(ke+ek) proportion (bounded 0-1)')
    print()

    c_mean = sum(confirmed_vals) / len(confirmed_vals)
    s_mean = sum(supported_vals) / len(supported_vals)
    corpus_mean = sum(corpus_vals) / len(corpus_vals)

    # T1: CONFIRMED vs supported
    d_t1 = cohens_d(confirmed_vals, supported_vals)
    obs_t1, p_t1 = perm_test(confirmed_vals, supported_vals)
    print(f'T1: CONFIRMED (n={len(confirmed_vals)}) vs supported (n={len(supported_vals)})')
    print(f'  CONFIRMED mean: {c_mean:.4f}')
    print(f'  Supported mean: {s_mean:.4f}')
    print(f'  Cohen d: {d_t1:+.3f}')
    print(f'  Perm p: {p_t1:.4f}')

    # T2: CONFIRMED vs corpus
    d_t2 = cohens_d(confirmed_vals, corpus_vals)
    obs_t2, p_t2 = perm_test(confirmed_vals, corpus_vals)
    print(f'\nT2: CONFIRMED (n={len(confirmed_vals)}) vs corpus (n={len(corpus_vals)})')
    print(f'  Corpus mean: {corpus_mean:.4f}')
    print(f'  Cohen d: {d_t2:+.3f}')
    print(f'  Perm p: {p_t2:.4f}')

    # LOO (drop each CONFIRMED folio)
    print(f'\n=== LOO: drop each CONFIRMED folio ===')
    loo_results = []
    for drop_folio in CONFIRMED:
        loo_confirmed = [v for v, m in zip(confirmed_vals, confirmed_meta)
                         if m['folio'] != drop_folio]
        if not loo_confirmed:
            continue
        d_loo = cohens_d(loo_confirmed, supported_vals)
        _, p_loo = perm_test(loo_confirmed, supported_vals)
        loo_results.append({'drop': drop_folio, 'd': d_loo, 'p': p_loo,
                            'n': len(loo_confirmed)})
        print(f'  Drop {drop_folio}: n={len(loo_confirmed)}, d={d_loo:+.3f}, p={p_loo:.4f}')

    min_loo_d = min(r['d'] for r in loo_results) if loo_results else 0

    # Paragraph-level LOO (drop each paragraph)
    print(f'\n=== Paragraph LOO: drop each CONFIRMED paragraph ===')
    par_loo_min_d = float('inf')
    for drop_idx in range(len(confirmed_vals)):
        loo = [v for i, v in enumerate(confirmed_vals) if i != drop_idx]
        d_loo = cohens_d(loo, supported_vals)
        if d_loo < par_loo_min_d:
            par_loo_min_d = d_loo
            par_loo_worst = confirmed_meta[drop_idx]
    print(f'  Min d across paragraph drops: {par_loo_min_d:+.3f}')
    print(f'  Worst drop: {par_loo_worst["folio"]} idx={par_loo_worst["idx"]} '
          f'(ke_prop={par_loo_worst["ke_prop"]:.3f}, n={par_loo_worst["n_tokens"]})')

    # Verdict
    print(f'\n=== VERDICT ===')
    if d_t1 >= 0.5 and p_t1 <= 0.05 and min_loo_d >= 0.3:
        verdict = 'SUPPORTED'
        print(f'SUPPORTED: d={d_t1:+.3f}, p={p_t1:.4f}, min LOO d={min_loo_d:+.3f}')
    elif d_t1 >= 0.3 and p_t1 <= 0.20:
        verdict = 'DIRECTIONAL'
        print(f'DIRECTIONAL: d={d_t1:+.3f}, p={p_t1:.4f}')
    elif d_t1 <= 0:
        verdict = 'FALSIFIED'
        print(f'FALSIFIED: d={d_t1:+.3f}')
    else:
        verdict = 'INCONCLUSIVE'
        print(f'INCONCLUSIVE: d={d_t1:+.3f}, p={p_t1:.4f}')

    # Report confirmed paragraph details
    print(f'\nCONFIRMED paragraph details:')
    for m in confirmed_meta:
        print(f'  {m["folio"]} par {m["idx"]}: ke_prop={m["ke_prop"]:.3f} (n={m["n_tokens"]})')

    out = {
        'metric': 'ke/(ke+ek) proportion',
        'T1': {
            'confirmed_n': len(confirmed_vals),
            'supported_n': len(supported_vals),
            'confirmed_mean': c_mean,
            'supported_mean': s_mean,
            'cohens_d': d_t1,
            'perm_p': p_t1,
        },
        'T2_sanity': {
            'corpus_n': len(corpus_vals),
            'corpus_mean': corpus_mean,
            'cohens_d': d_t2,
            'perm_p': p_t2,
        },
        'loo_folio': loo_results,
        'min_loo_d': min_loo_d,
        'loo_paragraph_min_d': par_loo_min_d,
        'loo_paragraph_worst': par_loo_worst,
        'confirmed_meta': confirmed_meta,
        'verdict': verdict,
    }
    (out_dir / 'C1970_RETEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f'\nWrote results.')


if __name__ == '__main__':
    main()
