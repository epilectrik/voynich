import sys

import numpy as np

sys.argv = ['x', '4']
sys.path.insert(0, r'C:\Users\EPILEC~1\AppData\Local\Temp\claude\C--git-voynich\e451f3a8-445d-45a0-bf5f-3a967a8e452a\scratchpad')
import sim770v2 as V  # noqa: E402

rng = np.random.default_rng(8)
for m in (10, 20):
    for a in (0.7, 1.0, 1.5, 2.0, 3.0, 5.0):
        print('M8 m=%d amp %.1f  mean S3 %.3f' % (m, a, V.mean_s3('M8', {'m': m}, a, rng, n=40)), flush=True)
