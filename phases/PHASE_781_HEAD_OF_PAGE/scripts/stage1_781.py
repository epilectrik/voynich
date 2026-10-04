#!/usr/bin/env python3
"""PHASE_781 Stage 1 (go/no-go; pre-registration v2): Brunschwig only. No Voynich first-line statistic is computed.

  python stage1_781.py run       z*_BR,head (K1 i-ii on 91-entry samples, three nulls, 2,000 replicates each) and the
                                 gate genre power with descriptive rows -> results/stage1_781.jsonl (resumable),
                                 results/stage1_781.json
  python stage1_781.py summary   gate decision

Uses PHASE_780's engine, codes, degradation and Brunschwig machinery. The Voynich enters only through first-line
LENGTHS and V-A1's block and sheet labels (page structure), never through text or pictures."""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

PH = Path('C:/git/voynich/phases/PHASE_781_HEAD_OF_PAGE')
P780 = Path('C:/git/voynich/phases/PHASE_780_HERBAL_PICTURE_TEXT')
sys.path.insert(0, str(P780 / 'scripts'))
import core780 as K  # noqa: E402
import calib780 as CB  # noqa: E402

RES = PH / 'results'
WORKERS = 6
SEED = 781_100_000
N_Z, N_G, N_BR = 2000, 200, 91
GATE_BAR, FORECAST_Z = 0.85, 2.957
SETTINGS = ('z_markov', 'z_quire', 'main', 'names_masked', 'body_window', 'rubric_included', 'first_nonmodifier')
MODIFIERS = {'low', 'blow', 'gel', 'wyß', 'wyss', 'yß', 'wiß', 'weiß', 'rot', 'ot', 'yld', 'vild', 'ylder', 'wild', 'wilde',
             'wilden', 'omisch', 'romisch', 'guldin', 'gemein', 'gemeine'}   # colour and kind adjectives written as a
# separate word (B4; descriptive). Spellings without the decorated initial are listed ('low' for 'blow', 'yld' for 'wild').
# Compound names written in two words (brun wurtz, brant latich, spitz wegrich) are not modifiers.
W = {}


def is_name(w, stems, first):
    """A token carries the entry's name stem. Brunschwig sets the opening letter of each entry as a decorated initial
    that the transcription omits ('Mpfferwasser', 'Grimonien'), so the entry's first token is also matched without its
    first letter."""
    return any(w.startswith(s) or (first and len(s) >= 4 and w.startswith(s[1:])) for s in stems)


def log(msg):
    print(msg, flush=True)
    with open(RES / 'stage1_log781.txt', 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')


def v_structure():
    """First-line lengths, two-leaf block labels and bifolium labels of the 91 V-A1 pages in binding order
    (lengths and page structure only)."""
    import pandas as pd
    excl = set(json.load(open(P780 / 'data/prepare_summary.json', encoding='utf-8'))['V_excluded_no_main_plant'])
    pages = sorted([p for p in json.load(open(P780 / 'data/pages_v.json', encoding='utf-8'))
                    if p['arm'] == 'V-A1' and not p['excluded'] and p['folio'] not in excl], key=lambda p: p['pos'])
    assert len(pages) == 91, len(pages)
    ids = [p['folio'] for p in pages]
    df = pd.read_csv('C:/git/voynich/data/transcriptions/interlinear_full_words.txt', sep='\t', dtype=str)
    df = df[(df['transcriber'] == 'H') & (df['folio'].isin(ids))]
    df = df[df['placement'].fillna('').str.startswith('P')]
    df = df[df['word'].fillna('').str.strip() != '']
    lengths = []
    for f in ids:
        g = df[df['folio'] == f]
        lengths.append(int((g['line_number'] == g['line_number'].iloc[0]).sum()))
    return lengths, K.v_blocks(pages), K.v_sheets(pages)


def head_similarity(first_lines, corpus, first_word_override=None):
    h1 = K.text_similarity(first_lines, corpus)['T2']
    fw = first_word_override if first_word_override is not None else [[t[0]] if t else [] for t in first_lines]
    h2 = K.text_similarity(fw, corpus)['T2']
    return {'H1': h1, 'H2': h2}


def _init():
    os.environ['OMP_NUM_THREADS'] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    W['BR'] = CB.br_data()
    W['S'] = json.load(open(P780 / 'results/calib_setup780.json', encoding='utf-8'))
    CB._prepare(W['BR'], W['S'], 'BR')
    W['VL'], W['VBLOCK'], W['VSHEET'] = v_structure()
    W['RUBRIC'] = {e['idx']: [w for w in K.br_clean([e['heading']]) if w not in ('von', 'wasser')] for e in W['BR']['entries']}


def draw_head(tok_lists, rng, mode='first'):
    out = []
    for t in tok_lists:
        ok = [n for n in W['VL'] if n <= len(t)] or [len(t)]
        n = int(ok[int(rng.integers(len(ok)))])
        if mode == 'first':
            out.append(t[:n])
        else:                                          # body window: same length, starting after the head (B3)
            hi = max(n, len(t) - n)
            s0 = min(int(rng.integers(n, hi + 1)), max(0, len(t) - n))
            out.append(t[s0:s0 + n])
    return out


def task(args):
    kind, setting, rep = args
    t0 = time.time()
    B, S = W['BR'], W['S']
    rng = np.random.default_rng(SEED + 100_000 * (1 + SETTINGS.index(setting)) + rep)
    sub = sorted(rng.choice(len(B['ids']), size=N_BR, replace=False))
    ents = [dict(B['entries'][i], rank=k) for k, i in enumerate(sub)]
    ids = [B['ids'][i] for i in sub]
    full = [B['toks'][i] for i in sub]
    if setting == 'names_masked':
        stems = [CB.name_stems(B['entries'][i]['heading']) for i in sub]
        full = [[w for k, w in enumerate(t) if not is_name(w, st, k == 0)] for t, st in zip(full, stems)]
    if setting == 'rubric_included':
        full = [W['RUBRIC'][B['ids'][i]] + t for t, i in zip(full, sub)]
    heads = draw_head(full, rng, mode='window' if setting == 'body_window' else 'first')
    fw = None
    if setting == 'first_nonmodifier':
        fw = [[next((w for w in h if w not in MODIFIERS), h[0] if h else '')] if h else [] for h in heads]
    g = S['br_shared_gate']
    if setting.startswith('z_'):
        sub_D = {'ids': ids, 'heights': [B['heights'][i] for i in sub], 'pos': np.array([2 * k for k in range(len(sub))]),
                 'leaf': np.array([-1] * len(sub)), 'conj': np.array([-2] * len(sub)), 'group': [B['group'][i] for i in sub],
                 'codes': {s: {i: B['codes'][s].get(i, {}) for i in ids} for s in 'AB'}, 'gate': g}
        CB._prepare_sub(sub_D, B)
        cA, cB, hs = CB.synth_codes(sub_D, setting[2:], rng)
        codes_by_set, heights = {'A': cA, 'B': cB}, hs
    else:
        q = S['br_degrade_q']
        marg = {f: Counter(v) for f, v in S['br_margins'].items()}
        codes_by_set = {s: CB.degrade(B['codes'][s], ids, g['entered_content'], q, marg, rng) for s in 'AB'}
        heights = [B['heights'][i] for i in sub]
    C, Y = K.picture_matrices('BR', ids, codes_by_set, g, heights)
    T = head_similarity(heads, 'BR', fw)
    X = K.br_covariates(ents, [max(len(h), 1) for h in heads])
    # identical nulls to V (A2): V-A1's two-leaf block and bifolium labels assigned to the sample in entry order
    res = K.decide(K.Engine(T, C, Y, X), W['VBLOCK'], rng, sheet_blocks=W['VSHEET'])
    name_present = None
    if setting == 'main':
        stems = [CB.name_stems(B['entries'][i]['heading']) for i in sub]
        name_present = float(np.mean([any(is_name(w, st, k == 0) for k, w in enumerate(h)) for h, st in zip(heads, stems)]))
    return {'kind': kind, 'setting': setting, 'rep': rep, 'Zmax': res['Zmax'],
            'Z': {m: res[m]['Z'] for m in ('H1', 'H2')}, 'S': {m: res[m]['S'] for m in ('H1', 'H2')},
            'name_present': name_present, 'sec': round(time.time() - t0, 1)}


def run():
    RES.mkdir(exist_ok=True)
    path = RES / 'stage1_781.jsonl'
    done = set()
    if path.exists():
        for ln in open(path, encoding='utf-8'):
            d = json.loads(ln)
            done.add((d['kind'], d['setting'], d['rep']))
    tasks = [('z', s, r) for s in ('z_markov', 'z_quire') for r in range(N_Z)]
    tasks += [('g', s, r) for s in SETTINGS[2:] for r in range(N_G)]
    todo = [t for t in tasks if t not in done]
    log(f'stage 1: {len(done)} done, {len(todo)} to run')
    t0 = time.time()
    with Pool(WORKERS, initializer=_init) as pool, open(path, 'a', encoding='utf-8') as fh:
        for k, r in enumerate(pool.imap_unordered(task, todo, chunksize=2)):
            fh.write(json.dumps(r) + '\n')
            fh.flush()
            if (k + 1) % 200 == 0:
                log(f'  stage 1: {k + 1}/{len(todo)} ({time.time() - t0:.0f}s)')
    log(f'stage 1 replicates done ({time.time() - t0:.0f}s)')
    summary()


def summary():
    rows = [json.loads(ln) for ln in open(RES / 'stage1_781.jsonl', encoding='utf-8')]
    zq = {}
    for s in ('z_markov', 'z_quire'):
        z = [r['Zmax'] for r in rows if r['setting'] == s]
        q, qr = CB.q99_rule(z, n_full=10**9)          # A3: the point 99th percentile at 2,000 replicates decides
        zq[s] = {'n': len(z), 'q99': q, 'q99_upper90_descriptive': qr}
    zbr = max(v['q99'] for v in zq.values())
    out = {'z_star_br_head': zbr, 'z_settings': zq, 'gate_bar': GATE_BAR, 'rows': {}}
    for s in SETTINGS[2:]:
        rr = [r for r in rows if r['setting'] == s]
        z = np.array([r['Zmax'] for r in rr])
        k = int((z > zbr).sum())
        out['rows'][s] = {'n': len(z), 'genre_power': k / len(z), 'wilson95': CB.wilson(k, len(z)),
                          'power_at_2.957_forecast': float(np.mean(z > FORECAST_Z)),
                          'Zmax_median': float(np.median(z)),
                          'per_measure_power': {m: float(np.mean([r['Z'][m] > zbr for r in rr])) for m in ('H1', 'H2')}}
        if s == 'main':
            out['rows'][s]['name_stem_present_share'] = float(np.mean([r['name_present'] for r in rr]))
    B = CB.br_data()
    out['entries_first_word_modifier'] = int(sum(1 for t in B['toks'] if t and t[0] in MODIFIERS))
    out['n_entries'] = len(B['toks'])
    gp = out['rows']['main']['genre_power']
    out['gate'] = 'PASS (go to Stage 2)' if gp >= GATE_BAR else 'STOP (head-of-page test not powered at Brunschwig strength at this size)'
    json.dump(out, open(RES / 'stage1_781.json', 'w', encoding='utf-8'), indent=1)
    log(json.dumps(out, indent=1))


if __name__ == '__main__':
    {'run': run, 'summary': summary}[sys.argv[1]]()
