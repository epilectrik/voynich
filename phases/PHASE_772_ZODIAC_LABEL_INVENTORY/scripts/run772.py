#!/usr/bin/env python3
"""PHASE_772 locked run (see ../PRE_REGISTRATION.md; v2 after the lean-expert lock audit).

  python run772.py              verify the lock; R and W on the real labels (N0 descriptive, N1, N2), 10,000
                                permutations; the pre-registered verdict; descriptives
  python run772.py --checksums  write results/input_checksums.json (before the lock commit)
  python run772.py --dry        every code path on DECOY labels (real label forms replaced by random Currier A
                                words; H-track descriptive skipped); writes results/dryrun/
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import zod772 as Z  # noqa: E402

LOCK = 'phase772-lock'
PHASE = 'phases/PHASE_772_ZODIAC_LABEL_INVENTORY'
OUT = Z.ROOT / PHASE / 'results'
NPERM, NPERM_ADJ, SEED = 10000, 2000, 7722
INPUTS = ('data/transcriptions/reference/ZL_official.txt', 'data/transcriptions/interlinear_full_words.txt')
LOCKED = ('PRE_REGISTRATION.md', 'results/cal772.json', 'results/input_checksums.json', 'scripts/zod772.py',
          'scripts/cal772.py', 'scripts/run772.py', 'results/cal772_v1_smoke_LEAK_DISCLOSED.json')
LOGF = None
DRY = '--dry' in sys.argv


def log(*a):
    msg = ' '.join(str(x) for x in a)
    print(msg, flush=True)
    if LOGF is not None:
        LOGF.write(msg + '\n')
        LOGF.flush()


def sha256(p):
    return hashlib.sha256((Z.ROOT / p).read_bytes()).hexdigest()


def verify_lock():
    root = Z.ROOT
    r = subprocess.run(['git', 'rev-parse', '--verify', LOCK], cwd=root, capture_output=True, text=True)
    assert r.returncode == 0, f'lock tag {LOCK} not found'
    for p in LOCKED:
        r = subprocess.run(['git', 'cat-file', '-e', f'{LOCK}:{PHASE}/{p}'], cwd=root)
        assert r.returncode == 0, f'{p} is not in the lock tag'
        r = subprocess.run(['git', 'diff', '--quiet', LOCK, '--', f'{PHASE}/{p}'], cwd=root)
        assert r.returncode == 0, f'{p} changed since the lock tag'
    r = subprocess.run(['git', 'diff', '--quiet', LOCK, '--', f'{PHASE}/scripts'], cwd=root)
    assert r.returncode == 0, 'scripts/ (including audit/) changed since the lock tag'
    r = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', '--', f'{PHASE}/scripts'], cwd=root,
                       capture_output=True, text=True)
    assert not r.stdout.strip(), f'untracked files under scripts/: {r.stdout.split()}'
    sums = json.loads((OUT / 'input_checksums.json').read_text())
    for p in INPUTS:
        assert sha256(p) == sums[p], f'input changed since the lock: {p}'


def lev(a, b):
    a, b = Z.units(a), Z.units(b)
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def sim(a, b):
    n = max(len(Z.units(a)), len(Z.units(b)))
    return 1.0 - lev(a, b) / n if n else 1.0


def adjacency(all_labels, f, rng):
    """Within each ring (or top-row arc), labels ordered by clock position linearly from the largest circular gap
    (no wrap); adjacent pairs of readable labels that do not straddle an unreadable label, against all other
    within-ring pairs of readable labels. Null: readable labels permuted within their ring. Effect = observed minus
    null mean (descriptive)."""
    rings = defaultdict(list)
    for r in all_labels:
        rings[(r['folio'], r['ring'])].append(r)
    seqs = []
    for rs in rings.values():
        rs = sorted(rs, key=lambda r: r['clock'])
        if len(rs) < 4:
            continue
        clocks = [r['clock'] for r in rs]
        gaps = [(clocks[(i + 1) % len(rs)] - clocks[i]) % 12 for i in range(len(rs))]
        cut = int(np.argmax(gaps))
        seqs.append(rs[cut + 1:] + rs[:cut + 1])

    def stat(seq_forms):
        adj, non = [], []
        for seq in seq_forms:
            idx = [i for i, w in enumerate(seq) if w is not None]
            for a in range(len(idx)):
                for b in range(a + 1, len(idx)):
                    i, j = idx[a], idx[b]
                    s = sim(seq[i], seq[j])
                    (adj if j == i + 1 else non).append(s)
        return float(np.mean(adj) - np.mean(non))
    base = [[f(r['form']) if r['readable'] else None for r in seq] for seq in seqs]
    obs = stat(base)
    null = []
    for _ in range(NPERM_ADJ):
        perm = []
        for seq in base:
            vals = [w for w in seq if w is not None]
            vals = list(rng.permutation(vals))
            it = iter(vals)
            perm.append([next(it) if w is not None else None for w in seq])
        null.append(stat(perm))
    null = np.array(null)
    return {'effect_obs_minus_null_mean': round(obs - float(null.mean()), 4), 'obs': round(obs, 4),
            'p_one_sided_high': round(float((1 + np.sum(null >= obs)) / (len(null) + 1)), 4), 'n_arcs': len(seqs)}


def rw_block(labels, f, rng, nperm):
    forms = [f(r['form']) for r in labels]
    st = Z.w_test(forms, [r['sign'] for r in labels], rng, nperm)
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in st.items()}


def main():
    global LOGF
    if '--checksums' in sys.argv:
        (OUT / 'input_checksums.json').write_text(json.dumps({p: sha256(p) for p in INPUTS}, indent=1))
        print('wrote input checksums')
        return
    t0 = time.time()
    out_dir = OUT / 'dryrun' if DRY else OUT
    out_dir.mkdir(exist_ok=True)
    if not DRY:
        verify_lock()
    LOGF = open(out_dir / 'run_log.txt', 'w', encoding='utf-8')
    log('DRY RUN on decoy labels' if DRY else 'lock verified: ' + LOCK + ' (tag, files, untracked scripts, inputs)')
    rng = np.random.default_rng(SEED)
    cal = json.loads((OUT / 'cal772.json').read_text())
    thr2 = {lam: cal['R_thresholds'][lam]['N2'] for lam in cal['R_thresholds']}
    labels = Z.load_labels()
    all_labels = Z.load_labels(include_unreadable=True)
    if DRY:
        drng = np.random.default_rng(99)
        pool = Z.currier_a_words()
        for r in all_labels:
            if r['readable']:
                w = pool[drng.integers(len(pool))]
                r['form'], r['words'] = w, [w]
        labels = [r for r in all_labels if r['readable']]
    signs = [r['sign'] for r in labels]
    res = {'n_labels': len(labels), 'norms': {}}
    for k, f in Z.NORMS.items():
        forms = [f(r['form']) for r in labels]
        st = Z.w_test(forms, signs, rng, NPERM)
        top = Counter(forms).most_common(12)
        st['top_forms'] = [[w, c, len({s for fw, s in zip(forms, signs) if fw == w})] for w, c in top]
        res['norms'][k] = st
        log(f'{k}{" (descriptive)" if k == "N0" else ""}: R {st["R"]:.4f} | W {st["W"]:.4f} (exchangeable '
            f'{st["W_exp"]:.4f}; null mean {st["W_null_mean"]:.4f}) | p_low {st["p_low"]:.4f} p_high '
            f'{st["p_high"]:.4f} (min attainable {st["p_min"]:.4f}) | types {st["n_types"]} | D_w {st["D_w"]} '
            f'D_a {st["D_a"]}')
    rw2 = Z.r_words([[Z.n2(w) for w in r['words']] for r in labels], signs)
    res['R_words_N2'] = rw2
    log(f'conservative word-level R (N2): {rw2:.4f}')
    v, lam_star = Z.verdict(res['norms']['N1'], res['norms']['N2'], res['norms']['N2']['R'], rw2, thr2)
    res['verdict'] = v
    res['lam_star'] = lam_star
    if lam_star is not None:
        res['visible_change_share_at_lam_star'] = cal['visible_change_share_N2'][str(lam_star)]
    log('VERDICT:', v, '| lam* =', lam_star,
        '| visibly changed copies at lam*:', res.get('visible_change_share_at_lam_star'))
    # descriptives
    desc = {}
    by_page = [dict(r, sign=r['folio']) for r in labels]
    desc['W_by_page_N1'] = rw_block(by_page, Z.n1, rng, 2000)
    no_top = [r for r in labels if r['ring'] != 0]
    desc['without_top_rows_N1'] = rw_block(no_top, Z.n1, rng, 2000)
    desc['without_top_rows_N2'] = rw_block(no_top, Z.n2, rng, 2000)
    stripped = [dict(r, form=''.join(Z.units(Z.n2(r['form']))[1:])) for r in labels]
    desc['N2_first_unit_stripped'] = rw_block(stripped, lambda w: w, rng, 2000)
    if not DRY:
        h = Z.load_labels_h()
        desc['H_track'] = {'n_labels': len(h), 'N1': rw_block(h, Z.n1, rng, 2000),
                           'N2': rw_block(h, Z.n2, rng, 2000)}
    desc['adjacency_N1'] = adjacency(all_labels, Z.n1, rng)
    res['descriptive'] = desc
    for k, v2 in desc.items():
        log(f'  {k}: {json.dumps(v2)[:400]}')
    res['runtime_s'] = round(time.time() - t0, 1)
    (out_dir / 'phase772_results.json').write_text(json.dumps(res, indent=1))
    log('done', res['runtime_s'], 's')
    LOGF.close()


if __name__ == '__main__':
    main()
