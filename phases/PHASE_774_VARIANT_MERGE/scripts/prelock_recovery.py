"""PHASE_774 pre-lock step 1 (controls only; nothing is computed on B's tokens).

How much of the hidden unit does each merge recover, and how much spelling noise does it leave?
For every control cipher: I(M;U), H(M|U), and the per-position collision rates k1 (a true unit repeat stays visible)
and k0 (chance collision), for the static merges and for exchange clustering at several sizes.
"""
import json
import os
import sys
import time
from pathlib import Path

os.environ['NUMBA_CACHE_DIR'] = str(Path(__file__).parent / '__pycache__' / 'numba')
try:
    import psutil
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
except Exception:
    pass
sys.path.insert(0, str(Path(__file__).parent))
import gen774 as G  # noqa: E402
import merge774 as M  # noqa: E402

OUT = Path(__file__).parent.parent / 'results'
T0 = time.time()


def log(*a):
    print(f'[{time.time() - T0:7.1f}s]', *a, flush=True)


def controls(sk):
    rec = G.plaintext_words('LAT_rec')
    la = G.plaintext_words('NT_la')
    yield 'NAIBBE_P-REC', G.naibbe('P-REC', sk, 77401)
    yield 'HRC-S_free_LATrec', G.hrc_stem(rec, sk, 77402, frames='free')
    yield 'HRC-S_rule_LATrec', G.hrc_stem(rec, sk, 77403, frames='rule')
    yield 'HRC-SE_rule_LATrec', G.hrc_stem(rec, sk, 77404, frames='rule', edial=True)
    yield 'CB-2_LATrec', G.codebook(rec, sk, 2, 77405)
    yield 'CB-4_LATrec', G.codebook(rec, sk, 4, 77406)
    yield 'HRC-S_rule_NTla', G.hrc_stem(la, sk, 77407, frames='rule')
    yield 'CB-4_NTla', G.codebook(la, sk, 4, 77408)


def main():
    sk = G.HR.b_skeleton()
    log('skeleton:', len(sk['lines']), 'lines,', G.HR.n_certain(sk), 'certain tokens')
    res = {}
    for name, (lines, units) in controls(sk):
        toks = [w for ln in lines for w in ln if w is not None]
        assert len(toks) == len(units)
        r = {}
        for mname, fn in M.STATIC_MERGES.items():
            r[mname] = M.recovery(toks, units, fn)
        for K in (64, 128, 256, 512):
            fn, info = M.brown_merge(lines, K, minc=3)
            r[f'BR{K}'] = dict(M.recovery(toks, units, fn), **info)
        r['ORACLE'] = {'H_U': r['TOK']['H_U'], 'units': len(set(units))}
        res[name] = r
        log(name, f"H_U {r['TOK']['H_U']:.2f} bits, {len(set(units))} units, {r['TOK']['types']} types")
        for mname in list(M.STATIC_MERGES) + [f'BR{K}' for K in (64, 128, 256, 512)]:
            x = r[mname]
            log(f'   {mname:6s} I {x["I"]:.2f}  H(M|U) {x["H_MgU"]:.2f}  k1 {x["k1"]:.3f}  k0 {x["k0"]:.4f}  '
                f'types {x["types"]}' + (f'  (clustered {x["types_clustered"]}, it {x["iterations"]})'
                                          if 'iterations' in x else ''))
        json.dump(res, open(OUT / 'prelock_recovery.json', 'w'), indent=1)
    log('done')


if __name__ == '__main__':
    main()
