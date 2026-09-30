#!/usr/bin/env python3
"""PHASE_771 calibration (before lock; v2 after the lean-expert lock audit). Uses paragraph-text references, the
per-folio LENGTH profile of the label o-words and break POSITIONS only; the glyph after a label's 'o' and the glyphs of
break-adjacent words are never read here.

Arm L: grouped (length-stratified) rule under folio-clustered draws (Dirichlet-multinomial per folio x length cell,
       concentration alpha from text o-word continuations, and alpha/4): pure references, 50/50 mixtures and 2/3
       boundary truths; size of the grouped fit check with alpha = min(alpha_text, alpha estimated from the labels).
Arm E: E-seg draws from continuation-line edges (paragraph-first line starts / paragraph-last line ends excluded),
       E-line draws from position-matched mid-line words, same folio where possible; a 50/50 plant.
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402

OUT = Z.ROOT / 'phases/PHASE_771_LABEL_O_AND_DRAWING_BREAKS/results/calib'
OUT.mkdir(parents=True, exist_ok=True)
SEED = 7711
NSIM_L, BOOT_L = 200, 500
NSIM_E, BOOT_E = 500, 300
NFIT, RFIT = 100, 200
SMOKE = '--smoke' in sys.argv
if SMOKE:
    NSIM_L, BOOT_L, NSIM_E, BOOT_E, NFIT, RFIT = 3, 50, 3, 50, 3, 20
OUTFILE = OUT / ('cal771_smoke.json' if SMOKE else 'cal771.json')

TRUTHS = {'qo': [1, 0, 0], 'o': [0, 1, 0], 'init': [0, 0, 1],
          'qo+o': [.5, .5, 0], 'o+init': [0, .5, .5], 'qo+init': [.5, 0, .5],
          '2/3qo+o': [2 / 3, 1 / 3, 0], '2/3o+qo': [1 / 3, 2 / 3, 0], '2/3o+init': [0, 2 / 3, 1 / 3],
          '2/3init+o': [0, 1 / 3, 2 / 3], '2/3qo+init': [2 / 3, 0, 1 / 3], '2/3init+qo': [1 / 3, 0, 2 / 3]}


def log(*a):
    print(*a, flush=True)


def label_length_profile(recs):
    """Folio x length-stratum counts of readable o-initial label words (lengths only)."""
    c = defaultdict(Counter)
    for r in recs:
        if not r['kind'].startswith('L'):
            continue
        for ws in S.words_of(r):
            for w in ws:
                if Z.readable(w) and w.startswith('o') and not w.startswith('qo') and len(Z.units(w)) >= 2:
                    c[r['folio']][S.lstratum(len(Z.units(w)))] += 1
    fols = sorted(c)
    gi = S.group_index(S.FINE)
    nfg = np.zeros((len(fols), len(S.FINE)), int)
    for i, f in enumerate(fols):
        for L, n in c[f].items():
            nfg[i, gi[L]] += n
    return nfg


def arm_l(recs, lines, rng):
    cnt = S.references_by_length(lines)
    comps = S.comps_grouped(cnt)
    nfg = label_length_profile(recs)
    alpha_text = S.dirichlet_concentration(S.text_folio_matrix(lines, 'o'))[0]
    res = {'n_label_folios': int(nfg.shape[0]), 'n_label_words': int(nfg.sum()),
           'length_profile': dict(zip(map(str, S.LSTRATA), nfg.sum(0).tolist())),
           'ref_sizes': S.ref_sizes(cnt), 'alpha_text_o': round(alpha_text, 2)}
    log('Arm L: label folios', nfg.shape[0], 'words', int(nfg.sum()), 'length profile', res['length_profile'],
        'alpha_text', round(alpha_text, 2))
    for alabel, alpha in (('alpha_text_o', alpha_text), ('alpha_quarter', alpha_text / 4)):
        res[alabel + '_calls'] = S.power_grouped(nfg, comps, alpha, rng, NSIM_L, BOOT_L, TRUTHS)
        for t, v in res[alabel + '_calls'].items():
            log(f'  {alabel} truth {t}: {v}')
    # size of the grouped fit check; its alpha = min(alpha_text, alpha estimated from the (simulated) labels)
    size = {}
    for alabel, alpha in (('alpha_text_o', alpha_text), ('alpha_quarter', alpha_text / 4)):
        for t in ('qo', 'o', 'init'):
            rej = 0
            for _ in range(NFIT):
                _, per = S.simulate_grouped(nfg, comps, TRUTHS[t], alpha, rng, 1)
                a_lab = S.label_alpha(per)
                rej += S.grouped_fit_check_p(per, comps, min(alpha_text, a_lab), rng, RFIT) < 0.01
            size[f'{alabel}|{t}'] = rej / NFIT
    res['fit_check_size_at_0.01'] = size
    log('  fit-check size', size)
    return res


def pools(words, side):
    """Unit pools: continuation-line edge words, and position-matched mid-line words, by folio / section / language."""
    ukey = 'first' if side == 'start' else 'last'
    edge_f, edge_s, edge_l = defaultdict(list), defaultdict(list), defaultdict(list)
    mid_f, mid_s, mid_l = defaultdict(list), defaultdict(list), defaultdict(list)
    for w in words:
        k, is_edge = S._word_keys(w, side)
        if is_edge is None:
            continue
        u = w[ukey]
        if is_edge:
            edge_f[(w['folio'],)].append(u)
            edge_s[(w['lang'], w['section'])].append(u)
            edge_l[(w['lang'],)].append(u)
        else:
            mid_f[(w['folio'],) + k].append(u)
            mid_s[(w['lang'], w['section']) + k].append(u)
            mid_l[(w['lang'],) + k].append(u)
    return (edge_f, edge_s, edge_l), (mid_f, mid_s, mid_l)


def draw(b, side, kind, P, rng):
    (ef, es, el), (mf, ms, ml) = P
    if kind == 'seg':
        for pool in (ef.get((b['folio'],), []), es.get((b['lang'], b['section']), []), el.get((b['lang'],), [])):
            if len(pool) >= 3:
                return pool[rng.integers(len(pool))]
    k = S.break_key(b, side)
    for pool in (mf.get((b['folio'],) + k, []), ms.get((b['lang'], b['section']) + k, []), ml.get((b['lang'],) + k, [])):
        if len(pool) >= 3:
            return pool[rng.integers(len(pool))]
    pool = el.get((b['lang'],), [])
    return pool[rng.integers(len(pool))]


def arm_e(lines, rng):
    words, breaks = S.edge_tables(lines)
    res = {'n_breaks': {l: sum(b['lang'] == l for b in breaks) for l in ('A', 'B')}}
    for lang in ('A', 'B'):
        for side in ('start', 'end'):
            arm = S.EdgeArm(words, breaks, lang, side, seed=771)
            P = pools([w for w in words if w['lang'] == lang], side)
            out = {'fallback': [d['fallback'] for d in arm.dirs]}
            for truth in ('seg', 'line', 'half'):
                calls, Is = Counter(), []
                for _ in range(NSIM_E):
                    kinds = [truth if truth != 'half' else ('seg' if rng.random() < 0.5 else 'line') for _ in arm.breaks]
                    units = [draw(b, side, k, P, rng) for b, k in zip(arm.breaks, kinds)]
                    r = arm.evaluate(units, B=BOOT_E, rng=rng)
                    calls[r['call']] += 1
                    Is.append(r['I'])
                out[truth] = {'calls': {k: round(v / NSIM_E, 3) for k, v in calls.items()},
                              'I_mean': round(float(np.mean(Is)), 3), 'I_sd': round(float(np.std(Is)), 3)}
                log(f'  Arm E {lang} {side} truth {truth}: {out[truth]}')
            res[f'{lang}_{side}'] = out
    return res


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    recs = Z.load()
    lines = S.text_lines(recs)
    res = {'arm_L': arm_l(recs, lines, rng)}
    OUTFILE.write_text(json.dumps(res, indent=1))
    res['arm_E'] = arm_e(lines, rng)
    res['runtime_s'] = round(time.time() - t0, 1)
    OUTFILE.write_text(json.dumps(res, indent=1))
    log('done', res['runtime_s'], 's')


if __name__ == '__main__':
    main()
