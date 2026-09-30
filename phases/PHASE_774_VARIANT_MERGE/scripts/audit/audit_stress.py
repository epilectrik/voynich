"""PHASE_774 lock audit, controls only (nothing is computed on Currier B's token order).

Experiments, each scored with the locked EF machinery (R = 300 as in calibration, n = 5, TOK and MID) and with
C1790-style descriptive counts (duplicate lines, token 3-/4-grams in >= 3 folios):
  SEG   whole-word (CBB) and stem (HRCB-lem) codes on FRESH plaintext segments (offsets > 0), to measure the spread
        that the certification (which reused offset 0 with new codebook seeds) did not sample;
  LEAK  habit3 / habit3b fitted to a MESSAGE-BEARING control instead of B, to measure how much of a corpus's own
        phrase repeats a first-order generator fitted to it inherits (the B-fitted ceiling could inherit B's);
  HET   habit3 / habit3b fitted separately within each of B's sections (B's adjacent-pair transitions within
        section; declared exposure class), a no-message process with section-level heterogeneity;
  REF   the design-type references re-run here for comparability.
A guard refuses to score any corpus identical to B's lines (EF is never run on B).

Usage: python audit_stress.py [workers]   -> results/audit/audit_stress.json, audit_stress_log.txt
"""
import json
import os
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCR = HERE.parent
OUT = SCR.parent / 'results' / 'audit'
R = 300
NS = (5,)


def c1790_stats(lines, folios):
    """Duplicate lines (>= 3 certain tokens, no blocker), distinct token 3-/4-grams in >= 3 folios, distinct 5-grams
    in >= 2 folios (all within lines, no blocker inside)."""
    full = Counter(tuple(ln) for ln in lines if len(ln) >= 3 and all(w is not None for w in ln))
    dup_lines = sum(c for c in full.values() if c >= 2)
    out = {'dup_lines': int(dup_lines)}
    for n, fmin in ((3, 3), (4, 3), (5, 2)):
        fol = defaultdict(set)
        for ln, f in zip(lines, folios):
            for i in range(len(ln) - n + 1):
                w = ln[i:i + n]
                if any(x is None for x in w):
                    continue
                fol[tuple(w)].add(f)
        out[f'ngram{n}_in_{fmin}plus_folios'] = int(sum(len(v) >= fmin for v in fol.values()))
    return out


def section_fitted(gen, sk, seed):
    """Fit a generator separately within each section of the skeleton; reassemble in the original line order."""
    by = defaultdict(list)
    for i, s in enumerate(sk['sections']):
        by[s].append(i)
    out = [None] * len(sk['lines'])
    for j, (s, idx) in enumerate(sorted(by.items())):
        sub = {'lines': [sk['lines'][i] for i in idx], 'sections': [sk['sections'][i] for i in idx],
               'folios': [sk['folios'][i] for i in idx]}
        gl = gen(sub, seed + 101 * j)
        for i, ln in zip(idx, gl):
            out[i] = ln
    return out


def specs():
    S = []
    # fresh segments, whole-word codes (T arm)
    for k in range(1, 7):
        S.append(('SEG', 'CBB', 'LAT_mesue', k, 9500 + k))
    for k in (1, 2):
        S.append(('SEG', 'CBB', 'LAT_sismel', k, 9510 + k))
    for pt in ('ITA_dante', 'LAT_rupescissa', 'LAT_rec'):
        S.append(('SEG', 'CBB', pt, 'last', 9520 + len(pt)))
    # fresh segments, stem codes of NTs (M arm): later books
    for pt, ks in (('NT_la', (2, 5, 8)), ('NT_de', (3, 6)), ('TUR_nt', (2, 4))):
        for k in ks:
            S.append(('SEG', 'HRCB-lem', pt, k, 9600 + 10 * k + len(pt)))
    # leak: generators fitted to message-bearing controls
    for gen, seeds in (('habit3b', 3), ('habit3', 2)):
        for j in range(seeds):
            S.append(('LEAK', gen, 'CBB:LAT_mesue', 0, 9700 + 10 * j + len(gen)))
    for j in range(2):
        S.append(('LEAK', 'habit3b', 'HRCB-lem:NT_de', 0, 9750 + j))
    # heterogeneity: section-fitted generators fitted to B (adjacent pairs within section)
    for j in range(6):
        S.append(('HET', 'habit3b_sec', None, 0, 9800 + j))
    for j in range(3):
        S.append(('HET', 'habit3_sec', None, 0, 9850 + j))
    # references (offset 0, as in design) for comparability
    S.append(('REF', 'CBB', 'LAT_mesue', 0, 9900))
    S.append(('REF', 'HRCB-lem', 'NT_de', 0, 9901))
    S.append(('REF', 'habit3b', None, 0, 9902))
    return S


def build(spec, sk, G):
    kind, fam, pt, k, seed = spec
    n = G.HR.n_certain(sk)
    if kind in ('SEG', 'REF') and fam in ('CBB', 'HRCB-lem'):
        words = G.plaintext_words(pt)
        off = len(words) - n if k == 'last' else k * n
        stream = list(words[off:off + n])
        assert len(stream) == n
        if fam == 'CBB':
            lines, _ = G.bform_codebook(words, sk, seed, stream)
        else:
            lines, _ = G.bform_stem(words, sk, seed, 'rule', 'lemma', stream)
        return lines, {'offset': off}
    if kind == 'REF' and fam == 'habit3b':
        return G.HR2.habit3b_lines(sk, seed), {}
    if kind == 'LEAK':
        src_fam, src_pt = pt.split(':')
        words = G.plaintext_words(src_pt)
        stream = G.plain_stream(words, sk)
        if src_fam == 'CBB':
            src, _ = G.bform_codebook(words, sk, 99000 + seed, stream)
        else:
            src, _ = G.bform_stem(words, sk, 99000 + seed, 'rule', 'lemma', stream)
        fake = {'lines': src, 'sections': sk['sections'], 'folios': sk['folios']}
        genf = G.HR2.habit3b_lines if fam == 'habit3b' else G.HR.habit3_lines
        return genf(fake, seed), {'source_name': pt, 'source_lines': src}
    if kind == 'HET':
        genf = G.HR2.habit3b_lines if fam == 'habit3b_sec' else G.HR.habit3_lines
        return section_fitted(genf, sk, seed), {}
    raise ValueError(spec)


def score(lines, folios, E, M, seed):
    C = E.Corpus(lines, folios, sig=E.sig_fl, ns=NS)
    reps = {k: C.rep_array(M.STATIC_MERGES[k]) for k in ('TOK', 'MID')}
    res = E.ef_test(C, reps, R, seed)
    t, m = res['TOK']['RPT5'], res['MID']['RPT5']
    return {'TOK5_obs': t['obs'], 'TOK5_null': t['null_mean'], 'D5': t['obs'] - t['null_mean'], 'pT': t['p'],
            'MID5_obs': m['obs'], 'MID5_null': m['null_mean'], 'X5': m['X'], 'pM': m['p'],
            'movable': C.frac_movable, 'types': len(C.vocab)}


def run_one(spec):
    os.environ['NUMBA_CACHE_DIR'] = str(HERE / '__pycache__' / 'numba')
    for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[v] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    sys.path.insert(0, str(SCR))
    import ef774 as E
    import gen774 as G
    import merge774 as M
    t0 = time.time()
    sk = G.HR.b_skeleton()
    lines, info = build(spec, sk, G)
    # guard: never score B itself (identity check only; no statistic of B's order is computed)
    assert lines is not sk['lines'] and lines != sk['lines'], 'refusing to score B'
    th = json.load(open(SCR.parent / 'results' / 'thresholds774.json', encoding='utf-8'))['thresholds']
    r = score(lines, sk['folios'], E, M, spec[4] * 7 + 1)
    r.update(c1790_stats(lines, sk['folios']))
    if 'source_lines' in info:
        src = info.pop('source_lines')
        rs = score(src, sk['folios'], E, M, spec[4] * 7 + 2)
        r['source'] = {'D5': rs['D5'], 'X5': rs['X5'], 'TOK5_obs': rs['TOK5_obs'], 'MID5_obs': rs['MID5_obs']}
    r.update(info)

    def call(stat, p, tau, neg):
        if stat >= tau and p <= 0.01:
            return 'PRESENT'
        if stat <= neg or p > 0.05:
            return 'NONE'
        return 'INDETERMINATE'
    r['T'] = call(r['D5'], r['pT'], th['tau_T'], th['NEG_T'])
    r['M'] = call(r['X5'], r['pM'], th['tau_M'], th['NEG_M'])
    r['spec'] = [str(x) for x in spec]
    r['runtime_s'] = time.time() - t0
    return '|'.join(str(x) for x in spec), r


def main():
    workers = min(4, int(sys.argv[1]) if len(sys.argv) > 1 else 4)
    kinds = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None
    OUT.mkdir(parents=True, exist_ok=True)
    prev = OUT / 'audit_stress.json'
    out = json.load(open(prev, encoding='utf-8')) if (kinds and prev.exists()) else {}
    log = open(OUT / 'audit_stress_log.txt', 'a' if kinds else 'w', encoding='utf-8')
    T0 = time.time()
    todo = [s for s in specs() if kinds is None or s[0] in kinds]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, s): s for s in todo}
        for f in as_completed(futs):
            try:
                name, r = f.result()
            except Exception as e:  # noqa: BLE001
                msg = f'[{time.time() - T0:7.1f}s] FAILED {futs[f]}: {e!r}'
                print(msg, flush=True)
                log.write(msg + '\n')
                log.flush()
                continue
            out[name] = r
            src = r.get('source')
            msg = (f'[{time.time() - T0:7.1f}s] {name}: T {r["T"]} D5 {r["D5"]:.2f} ({r["TOK5_obs"]}/'
                   f'{r["TOK5_null"]:.2f}, p {r["pT"]:.3f}) | M {r["M"]} X5 {r["X5"]:.2f} ({r["MID5_obs"]}/'
                   f'{r["MID5_null"]:.1f}, p {r["pM"]:.3f}) | dup {r["dup_lines"]} 3g3f '
                   f'{r["ngram3_in_3plus_folios"]} 4g3f {r["ngram4_in_3plus_folios"]} 5g2f '
                   f'{r["ngram5_in_2plus_folios"]}'
                   + (f' | source D5 {src["D5"]:.2f} X5 {src["X5"]:.2f}' if src else ''))
            print(msg, flush=True)
            log.write(msg + '\n')
            log.flush()
            json.dump(out, open(OUT / 'audit_stress.json', 'w'), indent=1)
    log.write(f'done {len(out)}\n')
    log.close()


if __name__ == '__main__':
    main()
