"""PHASE_774 pre-lock step 2 (controls only; nothing is computed on B's tokens).

Repeat statistics under the exact edge-frame null (EF) for ciphers with known plaintext (message present), their
shuffled-plaintext twins (same spelling machinery, no word order) and no-message generators. Representations: TOK,
MID, MIDn1, MIDn2 and, for ciphers, ORACLE (the hidden unit). B supplies its skeleton; the habit generators also use
B's transition frequencies (declared, as in PHASE_768).
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
T0 = time.time()
LOG = open(OUT / 'prelock_power_log.txt', 'w', encoding='utf-8')


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
    mes = G.plaintext_words('LAT_mesue')
    s_rec = G.plain_stream(rec, sk)
    s_la = G.plain_stream(la, sk)
    s_mes = G.plain_stream(mes, sk)
    tw_rec = G.twin_stream(s_rec, sk, 77451)
    # message present
    yield 'POS', 'CB-1_LATrec', G.codebook(rec, sk, 1, 77410, stream=s_rec)
    yield 'POS', 'CB-2_LATrec', G.codebook(rec, sk, 2, 77411, stream=s_rec)
    yield 'POS', 'HRC-S_free_LATrec', G.hrc_stem(rec, sk, 77412, frames='free', stream=s_rec)
    yield 'POS', 'HRC-S_rule_LATrec', G.hrc_stem(rec, sk, 77413, frames='rule', stream=s_rec)
    yield 'POS', 'HRC-SE_rule_LATrec', G.hrc_stem(rec, sk, 77414, frames='rule', edial=True, stream=s_rec)
    yield 'POS', 'HRC-L3_rule_LATrec', G.hrc_lemma(rec, sk, 77415, n_frames=3, stream=s_rec)
    yield 'POS', 'HRC-L3_rule_LATmesue', G.hrc_lemma(mes, sk, 77416, n_frames=3, stream=s_mes)
    yield 'POS', 'HRC-S_rule_NTla', G.hrc_stem(la, sk, 77417, frames='rule', stream=s_la)
    yield 'POS', 'HRC-L3_rule_NTla', G.hrc_lemma(la, sk, 77418, n_frames=3, stream=s_la)
    yield 'POS', 'NAIBBE_P-REC', G.naibbe('P-REC', sk, 77419)
    # twins: same machinery, plaintext order shuffled within folio
    yield 'TWIN', 'CB-1_LATrec_twin', G.codebook(rec, sk, 1, 77410, stream=tw_rec)
    yield 'TWIN', 'HRC-S_rule_LATrec_twin', G.hrc_stem(rec, sk, 77413, frames='rule', stream=tw_rec)
    yield 'TWIN', 'HRC-L3_rule_LATrec_twin', G.hrc_lemma(rec, sk, 77415, n_frames=3, stream=tw_rec)
    # no message
    yield 'NEG', 'habit_s1', (G.HR.habit_lines(sk, 77420), None)
    yield 'NEG', 'habit2_s1', (G.HR.habit2_lines(sk, 77421), None)
    yield 'NEG', 'habit3_s1', (G.HR.habit3_lines(sk, 77422), None)
    yield 'NEG', 'habit3_s2', (G.HR.habit3_lines(sk, 77423), None)
    yield 'NEG', 'habit3b_s1', (G.HR2.habit3b_lines(sk, 77424), None)
    yield 'NEG', 'timm_s1', (G.HR.timm_lines(sk, 77425), None)


def main():
    sk = G.HR.b_skeleton()
    log('skeleton:', len(sk['lines']), 'lines,', G.HR.n_certain(sk), 'certain tokens; R =', R)
    res = {}
    for kind, name, obj in corpora(sk):
        if obj is None:
            continue
        lines, units = obj
        C = E.Corpus(lines, sk['folios'], sig=E.sig_fl)
        reps = {k: C.rep_array(f) for k, f in M.STATIC_MERGES.items()}
        extra = {}
        if units is not None:
            fn, pur = oracle_fn(lines, units)
            reps['ORACLE'] = C.rep_array(fn)
            extra['oracle_purity'] = pur
        r = E.ef_test(C, reps, R, 774000 + len(res))
        res[name] = {'kind': kind, 'types': len(C.vocab), 'cells': C.n_cells, 'frac_movable': C.frac_movable,
                     **extra, 'reps': r}
        log(f'{kind} {name}: types {len(C.vocab)}, cells {C.n_cells}, movable {C.frac_movable:.3f}'
            + (f', oracle purity {extra["oracle_purity"]:.4f}' if extra else ''))
        for k in reps:
            x = r[k]
            log(f'    {k:6s} RPT3 {x["RPT3"]["obs"]:5d}/{x["RPT3"]["null_mean"]:7.1f} X {x["RPT3"]["X"]:5.2f} '
                f'z {x["RPT3"]["z"]:6.1f} | RPT4 {x["RPT4"]["obs"]:4d}/{x["RPT4"]["null_mean"]:6.1f} '
                f'X {x["RPT4"]["X"]:5.2f} z {x["RPT4"]["z"]:6.1f} | RPTx4 X {x["RPTx4"]["X"]:5.2f} '
                f'z {x["RPTx4"]["z"]:6.1f} | DIST4 X {x["DIST4"]["X"]:5.2f}')
        json.dump(res, open(OUT / 'prelock_power.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
