"""Lock audit (controls only): plaintext lengths, to see which texts allow fresh non-overlapping segments of B's size.
Touches B only through the skeleton size (number of certain tokens)."""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCR = HERE.parent
os.environ['NUMBA_CACHE_DIR'] = str(HERE / '__pycache__' / 'numba')
try:
    import psutil
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
except Exception:
    pass
sys.path.insert(0, str(SCR))
import gen774 as G  # noqa: E402

sk = G.HR.b_skeleton()
n = G.HR.n_certain(sk)
print('B certain tokens (skeleton size):', n, flush=True)
for name in ('LAT_rec', 'LAT_pha', 'ITA_dante', 'LAT_mesue', 'LAT_rupescissa', 'LAT_sismel', 'TUR_nt',
             'NT_la', 'NT_it', 'NT_en', 'NT_de', 'NT_es'):
    try:
        w = G.plaintext_words(name)
        print(f'{name:15s} {len(w):8d} words  segments of B size: {len(w) // n}', flush=True)
    except Exception as e:  # noqa: BLE001
        print(f'{name:15s} ERROR {e!r}', flush=True)
