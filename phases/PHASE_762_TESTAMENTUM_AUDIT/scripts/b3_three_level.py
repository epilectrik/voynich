"""PHASE_762 B3 as pre-registered: three-level partition Practica / Mercuriorum / Furnis (Theorica-part chapters with a
procedural family are excluded from B3 only). Reuses testamentum_audit.py functions."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import testamentum_audit as T

pl_par, pl_orig = T.pl_sources()
pages = sorted(p for p in T.OP if p in T.SEC)
V = T.v_matrix(pages)
res = {}
for name, src in (('PL_parity_3level', pl_par), ('PL_original_3level', pl_orig)):
    s3 = [c for c in src if c['part'] in ('Practica', 'Mercuriorum', 'Furnis')]
    r = T.b3(s3, pages, V, 762)
    r.pop('nearest_pages', None)
    r['n_chapters'] = len(s3)
    res[name] = r
    print(name, {k: v for k, v in r.items() if k != 'table'}, r['table'], flush=True)
json.dump(res, open(T.ROOT / 'phases/PHASE_762_TESTAMENTUM_AUDIT/results/b3_three_level.json', 'w'), indent=1)
