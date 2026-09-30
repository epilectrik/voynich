#!/usr/bin/env python3
"""Lean-expert confirmation pass (v2) for the PHASE_771 lock.

Reads only synthetic data, paragraph-text references and the label LENGTH profile (cal771.label_length_profile).
Never reads the unit after a label's o, nor any break-adjacent word.

C1  L1 length mapping of S.references_by_length / S.label_o_items on synthetic words (incl. the 7+ stratum).
C2  E1 paragraph-edge exclusions: _word_keys, fit_edge_model, EdgeArm._prep and cal771.pools on synthetic lines.
C3  Spot reproduction of the recomputed fit-check section (cal771 --fitcheck-only, seed 7713, first cell only).
C4  RNG stream: does the fit-check alpha change the number of draws consumed (so later sections shift)?
C5  Estimator robustness: fit-check size when the folio clustering is SHARED across length strata.
"""
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import stats771 as S  # noqa: E402
import zl771 as Z  # noqa: E402
import cal771 as K  # noqa: E402  (top level only mkdirs results/calib, which exists)

T0 = time.time()


def say(*a):
    print(f'[{time.time() - T0:6.1f}s]', *a, flush=True)


# ---------------------------------------------------------------------------------------------------------------- C1
def c1():
    words = {'y': 1, 'ol': 2, 'qok': 3, 'daiin': 3, 'qoky': 4, 'ochckhy': 4, 'okeedy': 6, 'qokchdy': 6,
             'qokeedy': 7, 'okeeeeey': 8, 'qokeeedy': 8, 'qokeedykeedy': 12}
    for w, n in words.items():
        assert len(Z.units(w)) == n, (w, Z.units(w))
    ln = [{'folio': 'fX', 'lang': 'B', 'section': 'B', 'kind': 'P0', 'par_start': False, 'par_end': False,
           'segs': [list(words)]}]
    cnt = S.references_by_length(ln)
    exp = {L: {k: [] for k in S.REFS} for L in S.LSTRATA}
    for w, n in words.items():
        u = Z.units(w)
        exp[min(n + 1, 7)]['init'].append(S.cat(u[0]))           # words of L-1 units -> stratum L
        if w.startswith('qo') and n >= 3:
            exp[min(n - 1, 7)]['qo'].append(S.cat(u[2]))          # qo-words of L+1 units -> stratum L
        elif u[0] == 'o' and n >= 2:
            exp[min(n, 7)]['o'].append(S.cat(u[1]))               # o-words of L units -> stratum L
    for L in S.LSTRATA:
        for k in S.REFS:
            got = sorted(c for c, x in zip(S.CATS, cnt[L][k]) for _ in range(int(x)))
            assert got == sorted(exp[L][k]), (L, k, got, exp[L][k])
    # explicit spot values
    assert cnt[2]['qo'][S.CIDX['k']] == 1 and cnt[7]['qo'][S.CIDX['k']] == 2          # qok; qokeeedy + qokeedykeedy
    assert cnt[6]['qo'][S.CIDX['k']] == 1                                            # qokeedy (7 units) -> L = 6
    assert cnt[7]['o'][S.CIDX['k']] == 1 and cnt[6]['o'][S.CIDX['k']] == 1           # okeeeeey (8) -> 7; okeedy -> 6
    assert cnt[7]['init'].sum() == 6                                                 # words of >= 6 units: 6
    recs = [{'folio': 'fL', 'kind': 'Lf', 'lang': 'NA', 'section': 'Z',
             'segments': [[('okeedy', None), ('okeeeeey', '.'), ('ol', '.'), ('o', '.'), ('qoky', '.')]]}]
    items = S.label_o_items(recs)
    assert [(it[-2], it[-1]) for it in items] == [(6, 'k'), (7, 'k'), (2, 'l')], items
    fols, C = S.grouped_counts(items)
    assert C.shape == (1, 6, len(S.CATS)) and C[0, S.group_index(S.FINE)[7], S.CIDX['k']] == 1
    say('C1 L1 length mapping: PASS (L-1 init, L+1 qo, L o; 7+ = init >=6, qo >=8, o >=7 units)')


# ---------------------------------------------------------------------------------------------------------------- C2
def c2():
    L = lambda ws, ps=False, pe=False, f='f1': {'folio': f, 'lang': 'B', 'section': 'B', 'kind': 'P0',
                                                'par_start': ps, 'par_end': pe, 'segs': ws}
    lines = [L([['pchedy', 'okal', 'daiin', 'shey']], ps=True),     # paragraph-first line: 'p' start
             L([['sal', 'chol', 'qokain', 'dar']]),
             L([['tol', 'chey', 'okal', 'rolm']], pe=True, f='f2'),     # paragraph-last line: 'm' end (only m)
             L([['ykeey', 'chedy', 'lkain']], f='f2'),
             L([['qokedy', 'chedy'], ['otedy', 'dal']])]                # a broken line
    words, breaks = S.edge_tables(lines)
    assert len(breaks) == 1 and breaks[0]['post'] == 'otedy' and breaks[0]['pre'] == 'chedy'
    assert breaks[0]['post_i_start'] == 2 and breaks[0]['pre_i_end'] == 2
    wk = {w['word']: w for w in words}
    assert S._word_keys(wk['pchedy'], 'start') == (None, None)
    assert S._word_keys(wk['sal'], 'start') == (None, True)
    assert S._word_keys(wk['rolm'], 'end') == (None, None)
    assert S._word_keys(wk['dar'], 'end') == (None, True)
    assert S._word_keys(wk['pchedy'], 'end')[1] is False          # a par-first start is ordinary on the END side
    S.MIN_UNIT, keep_min = 0, S.MIN_UNIT
    try:
        ms = S.fit_edge_model(words, 'B', 'start')
        me = S.fit_edge_model(words, 'B', 'end')
    finally:
        S.MIN_UNIT = keep_min
    assert ms('p') == ms('ZZZ'), 'paragraph-first start counted in the start edge model'
    assert me('m') == me('ZZZ'), 'paragraph-last end counted in the end edge model'
    arm = S.EdgeArm(words, breaks, 'B', 'start', seed=1)
    for d in arm.dirs:
        assert int(d['CE'].sum()) <= 3                             # continuation starts only: sal, tol, ykeey
    n_edge = sum(int(d['CE'][:, 0].sum()) for d in arm.dirs)
    assert n_edge == 3, n_edge
    arm_e = S.EdgeArm(words, breaks, 'B', 'end', seed=1)
    assert sum(int(d['CE'][:, 0].sum()) for d in arm_e.dirs) == 3  # continuation ends: shey, dar, lkain
    (ef, es, el), (mf, ms_, ml) = K.pools(words, 'start')
    assert sorted(el[('B',)]) == sorted(['s', 't', 'y']), el
    assert not any('p' in v for v in mf.values())
    (ef, es, el), _ = K.pools(words, 'end')
    assert sorted(el[('B',)]) == sorted(['y', 'r', 'in']), el
    say('C2 E1 exclusions consistent in _word_keys, fit_edge_model, EdgeArm._prep, cal771.pools: PASS')


# ---------------------------------------------------------------------------------------------------------------- C3/4/5
def c345():
    recs = Z.load()
    lines = S.text_lines(recs)
    comps = S.comps_grouped(S.references_by_length(lines))
    nfg = K.label_length_profile(recs)                              # lengths only
    a_text = S.dirichlet_concentration(S.text_folio_matrix(lines, 'o'))[0]
    say('loaded; alpha_text', round(a_text, 2), 'nfg', nfg.sum(0).tolist())

    # C3: first cell of fitcheck_only (alpha_text | qo), seed 7713
    rng = np.random.default_rng(7713)
    rej, ests = 0, []
    for _ in range(K.NFIT):
        _, per = S.simulate_grouped(nfg, comps, K.TRUTHS['qo'], a_text, rng, 1)
        a_lab = S.label_alpha(per)
        ests.append(a_lab)
        rej += S.grouped_fit_check_p(per, comps, min(a_text, a_lab), rng, K.RFIT) < 0.01
    say(f'C3 fitcheck-only first cell: size {rej / K.NFIT} median label alpha {np.median(ests):.2f} '
        f'(JSON: 0.01, 19.76)')

    # C4: RNG consumption depends on the fit-check alpha
    rng0 = np.random.default_rng(5)
    _, per = S.simulate_grouped(nfg, comps, K.TRUTHS['init'], a_text / 4, rng0, 1)
    a_new = min(a_text, S.label_alpha(per))
    a_old = min(a_text, S.dirichlet_concentration(per.sum(1))[0])
    nxt = []
    for a in (a_old, a_new):
        r = np.random.default_rng(99)
        S.grouped_fit_check_p(per, comps, a, r, K.RFIT)
        nxt.append(r.integers(0, 2 ** 62))
    say(f'C4 alpha old {a_old:.2f} new {a_new:.2f}; next draw after one fit check: {nxt[0]} vs {nxt[1]} -> '
        f'{"STREAM DIVERGES" if nxt[0] != nxt[1] else "same stream"}')

    # C5: folio-SHARED clustering (one style draw per folio applied to every stratum), pure 'o' truth
    def shared(alpha_style, w, rng):
        F, G = nfg.shape
        q = np.einsum('k,gkc->gc', np.asarray(w, float), comps)
        qbar = q.mean(0)
        per = np.zeros((F, G, len(S.CATS)))
        for f in range(F):
            r = rng.dirichlet(alpha_style * qbar) / qbar
            for g in range(G):
                if nfg[f, g]:
                    p = q[g] * r
                    per[f, g] = rng.multinomial(int(nfg[f, g]), p / p.sum())
        return per
    for a_sty in (a_text, a_text / 4):
        for tname in ('o', 'qo'):
            rng = np.random.default_rng(771)
            rej, ests, n = 0, [], 40
            for _ in range(n):
                per = shared(a_sty, K.TRUTHS[tname], rng)
                a_lab = S.label_alpha(per)
                ests.append(a_lab)
                rej += S.grouped_fit_check_p(per, comps, min(a_text, a_lab), rng, 100) < 0.01
            say(f'C5 shared-style alpha {a_sty:.1f} truth {tname}: size {rej}/{n} at 0.01; '
                f'median label alpha {np.median(ests):.1f}')


def c6():
    """Reference sizes of every sensitivity analysis (paragraph / ring text only)."""
    recs = Z.load()
    lines = S.text_lines(recs)
    sets = {'primary': (S.references_by_length(lines), S.FINE),
            's1_A': (S.references_by_length(lines, lang='A'), S.FINE),
            's1_B': (S.references_by_length(lines, lang='B'), S.FINE),
            's2': (S.references_by_length(lines, line_initial_only=True, exclude_par_first=True), S.FINE),
            's3': (S.references_by_length(S.text_lines(recs, merge_uncertain=True)), S.FINE),
            's6': (S.references_by_length(lines, init_exclude_oq=True), S.FINE),
            's7': (S.references_by_length(S.text_lines(recs, kinds=('R', 'C'))), S.COARSE),
            's8': (S.references_by_length(lines, type_weighted=True), S.FINE)}
    for name, (cnt, groups) in sets.items():
        rs = S.ref_sizes(cnt, groups)
        low = sorted((v, f'{k}@{g}') for g, d in rs.items() for k, v in d.items())[:3]
        big = [g for g in rs if max(int(x) for x in g.split('+')) >= 4]      # groups holding L >= 4 labels
        low4 = min((v, f'{k}@{g}') for g in big for k, v in rs[g].items())
        say(f'C6 {name}: smallest components {low}; smallest in groups with L>=4: {low4}')


if __name__ == '__main__':
    if '--c6' in sys.argv:
        c6()
    else:
        c1()
        c2()
        c345()
        c6()
    say('done')
