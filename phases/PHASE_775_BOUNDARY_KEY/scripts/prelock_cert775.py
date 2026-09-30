"""PHASE_775 certification on plaintext segments not used in the design (controls only). Criteria fixed here and in
PRE_REGISTRATION.md before this script was run:

Set (fresh seeds throughout):
  context-keyed ciphers, one spelling per unit and context:
    true key K1: NT_de 1, NT_es 2, NT_en 3, TUR_nt 1, LAT_mesue 2, LAT_mesue 3, LAT_sismel 1, LAT_rupescissa 0,
                 NT_es 4, NT_it 3  (no segment overlaps a design segment);
    true key K2: NT_de 2, NT_it 2, LAT_mesue 4, LAT_sismel 2, TUR_nt 3, NT_en 4;
  two spellings per unit and context: K1 NT_en 2, K2 NT_es 3, K1 LAT_mesue 5;
  twins (plaintext order shuffled within folio): K1 NT_de 1, K2 NT_it 2, K1 LAT_mesue 2;
  plain one-spelling word codes (no key): NT_es 2, LAT_mesue 3;
  no-message generators: habit3 x5, habit3b x5, section-fitted habit3 x3 and habit3b x3, habit2 x2, M1 x2.
For every keyed or plain positive, O = the plaintext segment's word-order index (gen775.plaintext_order_index).

Calls: results/thresholds775.json (per arm K: PRESENT if G_K >= tau_K and p_G <= 0.005; NONE if G_K <= NEG_K or
p_G > 0.05; else INDETERMINATE).

Criteria:
  R1  every one-spelling keyed cipher whose segment has O >= 0.04 is PRESENT on its true key's arm;
  R2  no two-spelling keyed cipher whose segment has O >= 0.04 is NONE on its true key's arm;
  R3  no no-message run, twin or plain code is PRESENT on either arm, and at most 2 of them are INDETERMINATE on
      either arm.
PASS = R1 and R2 and R3; a FAIL means redesign (no re-tuning on these segments). Writes results/prelock_cert775.json.
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'results'
sys.path.insert(0, str(HERE))
import prelock_calib775 as PC  # noqa: E402

TH = json.load(open(OUT / 'thresholds775.json', encoding='utf-8'))


def specs():
    S = []
    k1 = [('NT_de', 1), ('NT_es', 2), ('NT_en', 3), ('TUR_nt', 1), ('LAT_mesue', 2), ('LAT_mesue', 3),
          ('LAT_sismel', 1), ('LAT_rupescissa', 0), ('NT_es', 4), ('NT_it', 3)]
    k2 = [('NT_de', 2), ('NT_it', 2), ('LAT_mesue', 4), ('LAT_sismel', 2), ('TUR_nt', 3), ('NT_en', 4)]
    for i, (pt, seg) in enumerate(k1):
        S.append(('POS', 'key', pt, seg, 1, 1, 9100 + i))
    for i, (pt, seg) in enumerate(k2):
        S.append(('POS', 'key', pt, seg, 2, 1, 9120 + i))
    for i, (pt, seg, key) in enumerate((('NT_en', 2, 1), ('NT_es', 3, 2), ('LAT_mesue', 5, 1))):
        S.append(('POS', 'key', pt, seg, key, 2, 9140 + i))
    for i, (pt, seg, key) in enumerate((('NT_de', 1, 1), ('NT_it', 2, 2), ('LAT_mesue', 2, 1))):
        S.append(('TWIN', 'key', pt, seg, key, 1, 9150 + i))
    for i, (pt, seg) in enumerate((('NT_es', 2), ('LAT_mesue', 3))):
        S.append(('POS', 'CBB', pt, seg, 0, 1, 9160 + i))
    for gen, seeds in (('habit3', 5), ('habit3b', 5), ('habit3_sec', 3), ('habit3b_sec', 3), ('habit2', 2), ('M1', 2)):
        for j in range(seeds):
            S.append(('NEG', gen, None, None, None, None, 9200 + 10 * j + len(gen)))
    return S


def call(G, p, K):
    if G >= TH[f'tau_{K}'] and p <= 0.005:
        return 'PRESENT'
    if G <= TH[f'NEG_{K}'] or p > 0.05:
        return 'NONE'
    return 'INDETERMINATE'


def run_one(spec):
    name, r = PC.run_one(spec)
    if r['kind'] in ('POS', 'TWIN'):
        sys.path.insert(0, str(HERE))
        import gen775 as GK
        sk = GK.G.HR.b_skeleton()
        words = GK.G.plaintext_words(r['plaintext'])
        r['O'] = GK.plaintext_order_index(GK.G.segment_stream(words, sk, r['segment']), sk)
    for K in ('K1', 'K2'):
        r[f'call_{K}'] = call(r['res'][K]['G'], r['res'][K]['G_p'], K)
    return name, r


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    T0 = time.time()
    out = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, s): s for s in specs()}
        for f in as_completed(futs):
            name, r = f.result()
            out[name] = r
            x = r['res']
            print(f'[{time.time() - T0:6.1f}s] {name:44s} O {r.get("O", float("nan")):.4f} | '
                  f'K1 G {x["K1"]["G"]:+.4f} p {x["K1"]["G_p"]:.3f} {r["call_K1"]:13s} | '
                  f'K2 G {x["K2"]["G"]:+.4f} p {x["K2"]["G_p"]:.3f} {r["call_K2"]}', flush=True)
    rows = list(out.values())
    one = [r for r in rows if r['kind'] == 'POS' and r['family'] == 'key' and r['homophones'] == 1
           and r['O'] >= TH['O_S']]
    two = [r for r in rows if r['kind'] == 'POS' and r['family'] == 'key' and r['homophones'] == 2
           and r['O'] >= TH['O_S']]
    nokey = [r for r in rows if r['kind'] in ('NEG', 'TWIN') or r['family'] == 'CBB']
    crit = {
        'R1': all(r[f'call_K{r["true_key"]}'] == 'PRESENT' for r in one),
        'R1_n': len(one),
        'R2': not any(r[f'call_K{r["true_key"]}'] == 'NONE' for r in two),
        'R2_n': len(two),
        'R3': (not any('PRESENT' in (r['call_K1'], r['call_K2']) for r in nokey)
               and sum('INDETERMINATE' in (r['call_K1'], r['call_K2']) for r in nokey) <= 2),
        'R3_indeterminate': sum('INDETERMINATE' in (r['call_K1'], r['call_K2']) for r in nokey),
        'nokey_max_G': {K: max(r['res'][K]['G'] for r in nokey) for K in ('K1', 'K2')},
    }
    crit['PASS'] = crit['R1'] and crit['R2'] and crit['R3']
    print(json.dumps(crit, indent=1), flush=True)
    json.dump({'criteria': crit, 'thresholds': TH, 'runs': out}, open(OUT / 'prelock_cert775.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
