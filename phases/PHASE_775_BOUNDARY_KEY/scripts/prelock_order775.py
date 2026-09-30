"""PHASE_775: plaintext word-order index O for the design positives (plaintext property; no B statistic)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen775 as GK  # noqa: E402

OUT = HERE.parent / 'results'
d = json.load(open(OUT / 'prelock_calib775_design.json', encoding='utf-8'))
sk = GK.G.HR.b_skeleton()
cache = {}
rows = []
for name, v in sorted(d.items()):
    if v['kind'] not in ('POS', 'TWIN'):
        continue
    key = (v['plaintext'], v['segment'])
    if key not in cache:
        words = GK.G.plaintext_words(v['plaintext'])
        cache[key] = GK.plaintext_order_index(GK.G.segment_stream(words, sk, v['segment']), sk)
    r = v['res']
    rows.append((v['kind'], v['family'], v['plaintext'], v['segment'], v['true_key'], v['homophones'], cache[key],
                 r['K1']['G'], r['K1']['G_p'], r['K2']['G'], r['K2']['G_p']))
for row in sorted(rows, key=lambda x: (x[0], x[1], x[6])):
    print(f'{row[0]:4s} {row[1]:4s} {row[2]:11s} seg {row[3]} key {row[4]} h {row[5]} | O {row[6]:.4f} | '
          f'G1 {row[7]:+.4f} p {row[8]:.3f} | G2 {row[9]:+.4f} p {row[10]:.3f}')
json.dump({f'{k[0]}|{k[1]}': o for k, o in cache.items()}, open(OUT / 'prelock_order775_design.json', 'w'), indent=1)
