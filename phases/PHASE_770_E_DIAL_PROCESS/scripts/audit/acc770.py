import glob
import json

import numpy as np

SP = r'C:\Users\EPILEC~1\AppData\Local\Temp\claude\C--git-voynich\e451f3a8-445d-45a0-bf5f-3a967a8e452a\scratchpad'
V = {}
for f in glob.glob(SP + r'\sim770v2_out_*.json'):
    V.update(json.load(open(f))['variants'])
for n, v in V.items():
    s3, sf = np.array(v['s3']), np.array(v['s3far'])
    w3 = np.abs(s3 - 0.32) <= 0.03
    both = w3 & (np.abs(sf - 0.095) <= 0.03)
    print('%-6s n %d  S3 sd %.3f  S3far mean %.3f sd %.3f  P(S3 win) %.2f  P(S3far win | S3 win) %.3f  corr(S3,S3far) %.2f'
          % (n, len(s3), s3.std(), sf.mean(), sf.std(), w3.mean(), both.sum() / max(w3.sum(), 1),
             np.corrcoef(s3, sf)[0, 1]))
