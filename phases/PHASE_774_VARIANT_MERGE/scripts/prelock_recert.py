"""PHASE_774 re-certification on plaintext segments no one has scored (lock-audit edit E4). Controls only.

Why: the v1 certification re-drew codebooks on the same plaintext segment (offset 0) that the design had used. The
lock audit scored other segments (Mesue 1-6, SISMEL 1-2, Codicillus/Rupescissa/Dante 'last', Latin NT 2/5/8, German
NT 3/6, Turkish NT 2/4) and found the scopes overstated. Everything below uses segments outside all of those.

Segment k of a plaintext = words [k*n, (k+1)*n), n = 21,610 (B's certain tokens).

Set (fixed before this script was run):
  whole-word codes (CBB) and stem codes (HRCB-lem) on: Mesue 7-12; Latin NT 1, 3, 4, 6, 7; German NT 1, 2, 4, 5;
    Spanish, Italian and English NT 1-6; Turkish NT 1, 3  (35 segments each family);
  no-message: section-fitted habit3 x5 and habit3b x5 (B's adjacent pairs within section), corpus-wide habit3 x5 and
    habit3b x5 (fresh seeds);
  twins (plaintext order shuffled within folio): CBB Mesue 7, CBB Latin NT 1, HRCB-lem German NT 1, HRCB-lem Spanish
    NT 2.
For every positive, P5 = the plaintext's own repeated 5-word windows in B's layout (gen774.plaintext_p5).

Calls use results/thresholds774.json v2 (E3): T arm PRESENT if D5 >= 7.5 and p <= 0.01, NONE if D5 < 4.5 or p > 0.05;
M arm PRESENT if X5 >= 7.60 and p <= 0.01, NONE if X5 <= 2.82 or p > 0.05.

Criteria (written into this docstring and PRE_REGISTRATION v2 before the run):
  R1a  every whole-word-code segment with P5 >= 12 is PRESENT on the T arm;
  R1b  no whole-word-code segment with P5 >= 8 is NONE on the T arm;
  R2   no New-Testament stem-code segment is NONE on the M arm (the NONE scope "excludes NT-like repetition");
       the share PRESENT is reported (PRESENT is certified only at the level of the Gospel opening);
  R3   none of the 20 no-message runs is PRESENT on either arm, and at most 2 are INDETERMINATE on either arm;
  R4   no twin is PRESENT on either arm.
PASS = R1a and R1b and R2 and R3 and R4. A FAIL means redesign (no re-tuning on these segments).
Writes results/prelock_recert.json.
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / 'results'
R = 300
NS = (5,)
TH = json.load(open(OUT / 'thresholds774.json', encoding='utf-8'))['thresholds']
SEGMENTS = [('LAT_mesue', k) for k in range(7, 13)] + [('NT_la', k) for k in (1, 3, 4, 6, 7)] + \
           [('NT_de', k) for k in (1, 2, 4, 5)] + [(pt, k) for pt in ('NT_es', 'NT_it', 'NT_en') for k in range(1, 7)] + \
           [('TUR_nt', k) for k in (1, 3)]


def specs():
    S = []
    for i, (pt, k) in enumerate(SEGMENTS):
        S.append(('POS', 'CBB', pt, k, 12000 + i))
        S.append(('POS', 'HRCB-lem', pt, k, 12100 + i))
    for j in range(5):
        S.append(('NEG', 'habit3_sec', None, None, 12200 + j))
        S.append(('NEG', 'habit3b_sec', None, None, 12210 + j))
        S.append(('NEG', 'habit3', None, None, 12220 + j))
        S.append(('NEG', 'habit3b', None, None, 12230 + j))
    for i, (fam, pt, k) in enumerate((('CBB', 'LAT_mesue', 7), ('CBB', 'NT_la', 1), ('HRCB-lem', 'NT_de', 1),
                                      ('HRCB-lem', 'NT_es', 2))):
        S.append(('TWIN', fam, pt, k, 12300 + i))
    return S


def call_T(d5, p):
    if d5 >= TH['tau_T'] and p <= 0.01:
        return 'PRESENT'
    if d5 < TH['NONE_T_lt'] or p > 0.05:
        return 'NONE'
    return 'INDETERMINATE'


def call_M(x5, p):
    if x5 >= TH['tau_M'] and p <= 0.01:
        return 'PRESENT'
    if x5 <= TH['NEG_M'] or p > 0.05:
        return 'NONE'
    return 'INDETERMINATE'


def run_one(spec):
    os.environ['NUMBA_CACHE_DIR'] = str(HERE / '__pycache__' / 'numba')
    for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[v] = '1'
    try:
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    except Exception:
        pass
    sys.path.insert(0, str(HERE))
    import ef774 as E
    import gen774 as G
    import merge774 as M
    kind, fam, pt, k, seed = spec
    t0 = time.time()
    sk = G.HR.b_skeleton()
    info = {}
    if kind in ('POS', 'TWIN'):
        words = G.plaintext_words(pt)
        stream = G.segment_stream(words, sk, k)
        info['P5'] = G.plaintext_p5(stream, sk)
        if kind == 'TWIN':
            stream = G.twin_stream(stream, sk, seed + 1000)
        if fam == 'CBB':
            lines, _ = G.bform_codebook(words, sk, seed, stream)
        else:
            lines, _ = G.bform_stem(words, sk, seed, 'rule', 'lemma', stream)
    else:
        gen = {'habit3': G.HR.habit3_lines, 'habit3b': G.HR2.habit3b_lines,
               'habit3_sec': G.HR.habit3_lines, 'habit3b_sec': G.HR2.habit3b_lines}[fam]
        lines = G.section_fitted(gen, sk, seed) if fam.endswith('_sec') else gen(sk, seed)
    assert lines != sk['lines'], 'refusing to score B'
    C = E.Corpus(lines, sk['folios'], sig=E.sig_fl, ns=NS)
    reps = {r: C.rep_array(M.STATIC_MERGES[r]) for r in ('TOK', 'MID')}
    res = E.ef_test(C, reps, R, seed * 7 + 3)
    t, m = res['TOK']['RPT5'], res['MID']['RPT5']
    d5 = t['obs'] - t['null_mean']
    out = {'kind': kind, 'family': fam, 'plaintext': pt, 'segment': k, 'seed': seed, **info,
           'TOK5_obs': t['obs'], 'TOK5_null': t['null_mean'], 'D5': d5, 'pT': t['p'], 'T': call_T(d5, t['p']),
           'MID5_obs': m['obs'], 'MID5_null': m['null_mean'], 'X5': m['X'], 'pM': m['p'], 'M': call_M(m['X'], m['p']),
           'runtime_s': time.time() - t0}
    return '|'.join(str(x) for x in spec), out


def main():
    workers = min(5, int(sys.argv[1]) if len(sys.argv) > 1 else 5)
    T0 = time.time()
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, s): s for s in specs()}
        for f in as_completed(futs):
            name, r = f.result()
            out[name] = r
            print(f'[{time.time() - T0:7.1f}s] {name}: P5 {r.get("P5", "-")} | T {r["T"]} D5 {r["D5"]:.2f} '
                  f'({r["TOK5_obs"]}/{r["TOK5_null"]:.2f}) | M {r["M"]} X5 {r["X5"]:.2f} ({r["MID5_obs"]}/'
                  f'{r["MID5_null"]:.1f})', flush=True)
    rows = list(out.values())
    cbb = [r for r in rows if r['kind'] == 'POS' and r['family'] == 'CBB']
    nt_stem = [r for r in rows if r['kind'] == 'POS' and r['family'] == 'HRCB-lem' and r['plaintext'] != 'LAT_mesue']
    neg = [r for r in rows if r['kind'] == 'NEG']
    crit = {
        'R1a': all(r['T'] == 'PRESENT' for r in cbb if r['P5'] >= 12),
        'R1a_n': sum(r['P5'] >= 12 for r in cbb),
        'R1b': not any(r['T'] == 'NONE' for r in cbb if r['P5'] >= 8),
        'R1b_n': sum(r['P5'] >= 8 for r in cbb),
        'R2': not any(r['M'] == 'NONE' for r in nt_stem),
        'R2_present_share': f'{sum(r["M"] == "PRESENT" for r in nt_stem)}/{len(nt_stem)}',
        'R3': (not any('PRESENT' in (r['T'], r['M']) for r in neg)
               and sum('INDETERMINATE' in (r['T'], r['M']) for r in neg) <= 2),
        'R3_indeterminate': sum('INDETERMINATE' in (r['T'], r['M']) for r in neg),
        'R4': not any('PRESENT' in (r['T'], r['M']) for r in rows if r['kind'] == 'TWIN'),
        'mesue_stem_calls': sorted((r['segment'], r['M'], round(r['X5'], 2)) for r in rows
                                   if r['kind'] == 'POS' and r['family'] == 'HRCB-lem' and r['plaintext'] == 'LAT_mesue'),
        'neg_max_D5': max(r['D5'] for r in neg), 'neg_max_X5': max(r['X5'] for r in neg),
        'neg_MID5_null_range': [min(r['MID5_null'] for r in neg), max(r['MID5_null'] for r in neg)],
    }
    crit['PASS'] = crit['R1a'] and crit['R1b'] and crit['R2'] and crit['R3'] and crit['R4']
    print(json.dumps(crit, indent=1), flush=True)
    json.dump({'criteria': crit, 'thresholds': TH, 'runs': out}, open(OUT / 'prelock_recert.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
