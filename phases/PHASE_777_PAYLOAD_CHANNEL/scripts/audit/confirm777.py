"""PHASE_777 lock audit confirmation pass (controls only): does the v3 EFq/EFpar gate label a no-payload LINE palette
as payload-level, and what does the composition line-entropy figure show for it? Uses chan777 v3 functions."""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / 'results' / 'audit'


def one(spec):
    import audit777 as A
    X = A._setup()
    kind, a, seed = spec
    sk = X.HR.b_skeleton()
    lines = X.palette_plant(sk, 'F1', a, seed, kind=kind)
    assert lines != sk['lines']
    TH = json.load(open(HERE.parent.parent / 'results' / 'thresholds777.json', encoding='utf-8'))
    r = X.run(lines, X.GK.ef_groups(sk), R=200, seed=seed + 1, channels=('F1',), refined=X.par_groups(sk))['F1']
    comp = X.composition_figures(lines, sk, 'F1', seed + 2)
    t = TH['F1']['tau']
    present = r['RPT7']['p'] <= 0.005 and r['RPT7']['z'] >= t
    gate = all(r[nm]['z'] >= t / 2 and r[nm]['p'] <= 0.005 for nm in ('EFq', 'EFpar'))
    return {'spec': list(map(str, spec)), 'EF_z7': r['RPT7']['z'], 'EF_p': r['RPT7']['p'], 'EFq_z7': r['EFq']['z'],
            'EFpar_z7': r['EFpar']['z'], 'present': present, 'gate_payload_level': present and gate, **comp}


if __name__ == '__main__':
    sys.path.insert(0, str(HERE))
    specs = [('PALLINE', 10.0, 9700), ('PALLINE', 10.0, 9701), ('PALLINE', 7.0, 9702), ('PALLINE', 7.0, 9703)]
    with ProcessPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(one, specs))
    for r in res:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    json.dump(res, open(OUT / 'confirm777.json', 'w'), indent=1)
