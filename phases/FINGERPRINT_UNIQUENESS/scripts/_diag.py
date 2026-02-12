import sys, time
sys.stdout.reconfigure(encoding='utf-8')
print('Starting...', flush=True)
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
print('Imports OK', flush=True)
from scipy.stats import chi2_contingency
print('Scipy OK', flush=True)
tx = Transcript()
morph = Morphology()
t0 = time.time()
tokens = list(tx.currier_b())
print(f'Loaded {len(tokens)} B tokens in {time.time()-t0:.1f}s', flush=True)
t0 = time.time()
for tok in tokens[:500]:
    m = morph.extract(tok.word.strip())
print(f'500 morphs in {time.time()-t0:.2f}s', flush=True)
