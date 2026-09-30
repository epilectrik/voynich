"""PHASE_774 pre-lock step 3 (controls only; nothing is computed on B's token order).

Step 2 showed that stem codes built on A's forms have far fewer chance MIDDLE repeats than B-form text, so their
excess ratios do not transfer to B. Here the message-present controls are written in B's forms: plaintext units are
mapped onto B's MIDDLE (or token) frequency profile, and frames come from B's P(frame | MIDDLE) and frame
transitions (B marginals only, declared). Windows n = 4, 5, 6; rarity-filtered repeats (>= 2 symbols outside the
K most frequent).
"""
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

os.environ['NUMBA_CACHE_DIR'] = str(Path(__file__).parent / '__pycache__' / 'numba')
try:
    import psutil
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
except Exception:
    pass
sys.path.insert(0, str(Path(__file__).parent))
import ef774 as E  # noqa: E402
import gen774 as G  # noqa: E402
import merge774 as M  # noqa: E402

OUT = Path(__file__).parent.parent / 'results'
R = int(os.environ.get('R774', 200))
NS = (4, 5, 6)
REPS = ('TOK', 'MID', 'MIDn1')
T0 = time.time()
LOG = open(OUT / 'prelock_power2_log.txt', 'w', encoding='utf-8')


def log(*a):
    s = f'[{time.time() - T0:7.1f}s] ' + ' '.join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + '\n')
    LOG.flush()


def oracle_fn(lines, units):
    toks = [w for ln in lines for w in ln if w is not None]
    by = {}
    for t, u in zip(toks, units):
        by.setdefault(t, Counter())[u] += 1
    mp = {t: c.most_common(1)[0][0] for t, c in by.items()}
    purity = sum(c.most_common(1)[0][1] for c in by.values()) / len(toks)
    return (lambda w: mp[w]), purity


def corpora(sk):
    rec = G.plaintext_words('LAT_rec')
    la = G.plaintext_words('NT_la')
    en = G.plaintext_words('NT_en')
    mes = G.plaintext_words('LAT_mesue')
    s_rec, s_la, s_en, s_mes = (G.plain_stream(x, sk) for x in (rec, la, en, mes))
    tw_rec = G.twin_stream(s_rec, sk, 77551)
    yield 'POS', 'HRCB-lem-rule_LATrec', G.bform_stem(rec, sk, 77501, 'rule', 'lemma', s_rec)
    yield 'POS', 'HRCB-lem-free_LATrec', G.bform_stem(rec, sk, 77502, 'free', 'lemma', s_rec)
    yield 'POS', 'HRCB-word-rule_LATrec', G.bform_stem(rec, sk, 77503, 'rule', 'word', s_rec)
    yield 'POS', 'HRCB-lem-rule_LATmesue', G.bform_stem(mes, sk, 77504, 'rule', 'lemma', s_mes)
    yield 'POS', 'HRCB-lem-rule_NTla', G.bform_stem(la, sk, 77505, 'rule', 'lemma', s_la)
    yield 'POS', 'HRCB-lem-rule_NTen', G.bform_stem(en, sk, 77506, 'rule', 'lemma', s_en)
    yield 'POS', 'CBB_LATrec', G.bform_codebook(rec, sk, 77507, s_rec)
    yield 'POS', 'CBB_NTla', G.bform_codebook(la, sk, 77508, s_la)
    yield 'TWIN', 'HRCB-lem-rule_LATrec_twin', G.bform_stem(rec, sk, 77501, 'rule', 'lemma', tw_rec)
    yield 'TWIN', 'CBB_LATrec_twin', G.bform_codebook(rec, sk, 77507, tw_rec)
    yield 'NEG', 'habit_s1', (G.HR.habit_lines(sk, 77520), None)
    yield 'NEG', 'habit2_s1', (G.HR.habit2_lines(sk, 77521), None)
    yield 'NEG', 'habit3_s1', (G.HR.habit3_lines(sk, 77522), None)
    yield 'NEG', 'habit3_s2', (G.HR.habit3_lines(sk, 77523), None)
    yield 'NEG', 'habit3b_s1', (G.HR2.habit3b_lines(sk, 77524), None)
    yield 'NEG', 'timm_s1', (G.HR.timm_lines(sk, 77525), None)


def main():
    sk = G.HR.b_skeleton()
    log('skeleton:', len(sk['lines']), 'lines,', G.HR.n_certain(sk), 'certain tokens; R =', R)
    res = {}
    for kind, name, (lines, units) in corpora(sk):
        C = E.Corpus(lines, sk['folios'], sig=E.sig_fl, ns=NS)
        reps = {k: C.rep_array(M.STATIC_MERGES[k]) for k in REPS}
        extra = {}
        if units is not None:
            fn, pur = oracle_fn(lines, units)
            reps['ORACLE'] = C.rep_array(fn)
            extra['oracle_purity'] = pur
            toks = [w for ln in lines for w in ln if w is not None]
            extra['recovery_MID'] = M.recovery(toks, units, M.STATIC_MERGES['MID'])
        r = E.ef_test(C, reps, R, 775000 + len(res))
        res[name] = {'kind': kind, 'types': len(C.vocab), 'cells': C.n_cells, 'frac_movable': C.frac_movable,
                     **extra, 'reps': r}
        log(f'{kind} {name}: types {len(C.vocab)}, mid types {len(set(reps["MID"]))}, movable {C.frac_movable:.3f}'
            + (f', MID k1 {extra["recovery_MID"]["k1"]:.3f} k0 {extra["recovery_MID"]["k0"]:.4f}' if extra else ''))
        for k in reps:
            x = r[k]
            log(f'    {k:6s} ' + ' | '.join(
                f'n{nn} {x[f"RPT{nn}"]["obs"]}/{x[f"RPT{nn}"]["null_mean"]:.1f} X {x[f"RPT{nn}"]["X"]:.2f} '
                f'r20 X {x[f"RPT{nn}_r20"]["X"]:.2f} r50 X {x[f"RPT{nn}_r50"]["X"]:.2f}' for nn in NS))
        json.dump(res, open(OUT / 'prelock_power2.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
