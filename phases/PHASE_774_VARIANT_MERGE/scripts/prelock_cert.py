"""PHASE_774 certification on fresh seeds (controls only), after thresholds774.json was fixed.

None of these runs informs a threshold. Criteria (fixed before this script was run):
  C1  held-out whole-word codes (CBB, 6 plaintexts x 2 new seeds): at least 10 of 12 PRESENT on the T arm, and every
      run on Mesue, Rupescissa, the German NT and the Turkish NT PRESENT (pharmacy and alchemy prose must be seen;
      the misses allowed are the Italian verse and the Spanish NT);
  C2  held-out stem codes of New Testaments (HRCB-lem; NT_de, NT_es, TUR_nt x 2 new seeds): all PRESENT on the M arm;
  C3  fresh no-message generators (20 new seeds): none PRESENT on either arm; at most 2 INDETERMINATE;
  C4  fresh twins (4): none PRESENT on either arm.
Writes results/prelock_cert.json.
"""
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import prelock_calib as PC  # noqa: E402

OUT = HERE.parent / 'results'
TH = json.load(open(OUT / 'thresholds774.json', encoding='utf-8'))['thresholds']


def specs():
    S = []
    for i, pt in enumerate(PC.HELDOUT):
        for j in range(2):
            S.append(('POS', 'cert', 'CBB', pt, 9100 + 10 * i + j))
    for i, pt in enumerate(('NT_de', 'NT_es', 'TUR_nt')):
        for j in range(2):
            S.append(('POS', 'cert', 'HRCB-lem', pt, 9200 + 10 * i + j))
    for gen, seeds in (('habit3', 8), ('habit3b', 8), ('habit2', 2), ('M1', 2)):
        for j in range(seeds):
            S.append(('NEG', 'cert', gen, None, 9300 + 10 * j + len(gen)))
    for i, (fam, pt) in enumerate((('CBB', 'LAT_rupescissa'), ('CBB', 'NT_es'), ('HRCB-lem', 'NT_de'),
                                   ('HRCB-lem', 'LAT_mesue'))):
        S.append(('TWIN', 'cert', fam, pt, 9400 + i))
    return S


def call(stat, p, tau, neg):
    if stat >= tau and p <= 0.01:
        return 'PRESENT'
    if stat <= neg or p > 0.05:
        return 'NONE'
    return 'INDETERMINATE'


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    T0 = time.time()
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(PC.run_one, s): s for s in specs()}
        for f in as_completed(futs):
            name, r = f.result()
            t = r['reps']['TOK']['RPT5']
            m = r['reps']['MID']['RPT5']
            r['T'] = call(t['obs'] - t['null_mean'], t['p'], TH['tau_T'], TH['NEG_T'])
            r['M'] = call(m['X'], m['p'], TH['tau_M'], TH['NEG_M'])
            out[name] = r
            print(f'[{time.time() - T0:7.1f}s] {name}: T {r["T"]} (D5 {t["obs"] - t["null_mean"]:.1f}) | '
                  f'M {r["M"]} (X5 {m["X"]:.2f})', flush=True)
    rows = list(out.values())
    cbb = [r for r in rows if r['kind'] == 'POS' and r['family'] == 'CBB']
    prose = [r for r in cbb if r['plaintext'] in ('LAT_mesue', 'LAT_rupescissa', 'TUR_nt', 'NT_de')]
    crit = {
        'C1': sum(r['T'] == 'PRESENT' for r in cbb) >= 10 and all(r['T'] == 'PRESENT' for r in prose),
        'C1_count': f'{sum(r["T"] == "PRESENT" for r in cbb)}/{len(cbb)}',
        'C2': all(r['M'] == 'PRESENT' for r in rows if r['kind'] == 'POS' and r['family'] == 'HRCB-lem'),
        'C3': (not any('PRESENT' in (r['T'], r['M']) for r in rows if r['kind'] == 'NEG')
               and sum('INDETERMINATE' in (r['T'], r['M']) for r in rows if r['kind'] == 'NEG') <= 2),
        'C3_indeterminate': sum('INDETERMINATE' in (r['T'], r['M']) for r in rows if r['kind'] == 'NEG'),
        'C4': not any('PRESENT' in (r['T'], r['M']) for r in rows if r['kind'] == 'TWIN'),
    }
    crit['PASS'] = crit['C1'] and crit['C2'] and crit['C3'] and crit['C4']
    print(json.dumps(crit, indent=1), flush=True)
    json.dump({'criteria': crit, 'thresholds': TH, 'runs': out}, open(OUT / 'prelock_cert.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
