"""Discriminating test (v2, CORRECTED): o-HEAD rate vs plant morphology
for CURRIER A herbal folios using PIAA classification.

The PPC morphology file covers Currier B folios — wrong system.
PIAA covers 29 Currier A herbal folios with morphological "Key Features" descriptions.

PRE-REGISTERED:
HYPOTHESIS: If o-HEAD 'arrange' encodes botanical spatial structure, folios whose
illustrations show MORE distinct plant structures should have higher o-HEAD rate.

COMPLEXITY PROXY: count of distinct plant-structure terms in PIAA Key Features
(leaf, root, flower, stem, spike, branch, head, bulb, pod, frond, etc.).

TEST: Spearman correlation (complexity, o-HEAD rate). PASS: rho>0, p<0.05.
CONFOUND CHECK: token count vs o-rate.
CAVEAT: N=29, underpowered. Key-Features complexity is a crude proxy.
"""
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ===== Parse PIAA Key Features =====
piaa = Path('C:/git/voynich/phases/PIAA_plant_illustration/plant_class_assignments.md').read_text(encoding='utf-8')

# Structure terms to count as complexity
STRUCT_TERMS = ['leaf', 'leaves', 'root', 'flower', 'stem', 'spike', 'branch', 'branching',
                'head', 'bulb', 'pod', 'frond', 'rosette', 'palmate', 'lobed', 'serrated',
                'divided', 'feathery', 'cluster', 'tuber', 'rhizome', 'calyx', 'inflorescence',
                'seed', 'fruit', 'bushy', 'creeping', 'spreading']

folio_complexity = {}
folio_class = {}
for line in piaa.split('\n'):
    m = re.match(r'\|\s*\*\*(f\d+[rv]\d?)\*\*\s*\|\s*([A-Z]+)\s*\|\s*([^|]*)\|\s*([A-Z]+)\s*\|\s*([^|]*)\|', line)
    if m:
        folio = m.group(1)
        pclass = m.group(2).strip()
        features = m.group(5).lower()
        # Count distinct structure terms
        terms_found = set()
        for term in STRUCT_TERMS:
            if re.search(r'\b' + term, features):
                terms_found.add(term)
        folio_complexity[folio] = len(terms_found)
        folio_class[folio] = pclass

print(f'Parsed PIAA: {len(folio_complexity)} folios with complexity scores')
print(f'Complexity range: {min(folio_complexity.values())}-{max(folio_complexity.values())}')

# ===== o-HEAD rate per Currier A folio =====
tx = Transcript(); morph = Morphology()
folio_head = defaultdict(Counter)
folio_total = Counter()
for t in tx.currier_a(exclude_labels=True, exclude_uncertain=True):
    w = t.word.strip()
    if not w: continue
    try:
        a = morph.atomize(w)
    except Exception:
        continue
    folio_total[t.folio] += 1
    head = None
    if hasattr(a, 'atoms'):
        for c, r, _ in a.atoms:
            if r == 'HEAD':
                head = c
                break
    if head:
        folio_head[t.folio][head] += 1

# ===== Build paired data =====
data = []
for folio, complexity in folio_complexity.items():
    if folio_total.get(folio, 0) < 15:
        continue
    o_rate = folio_head[folio].get('o', 0) / folio_total[folio]
    data.append({'folio': folio, 'complexity': complexity, 'o_rate': o_rate,
                 'n_tokens': folio_total[folio], 'class': folio_class.get(folio, '?')})

print(f'Folios with morphology + >=15 A tokens: {len(data)}')

if len(data) < 5:
    print('Insufficient data')
    sys.exit()

complexity = np.array([d['complexity'] for d in data])
o_rates = np.array([d['o_rate'] for d in data])
toks = np.array([d['n_tokens'] for d in data])

# ===== TEST: complexity vs o-rate =====
print('\n=== TEST: plant structural complexity vs o-HEAD rate ===')
rho, p = spearmanr(complexity, o_rates)
print(f'  Spearman rho = {rho:+.3f}, p = {p:.4f} (n={len(data)})')
test_pass = rho > 0 and p < 0.05
print(f'  VERDICT: {"PASS" if test_pass else "FAIL"}')

# Confound check
rho_c, p_c = spearmanr(toks, o_rates)
print(f'\n  CONFOUND: token count vs o-rate: rho={rho_c:+.3f}, p={p_c:.4f}')
rho_ct, p_ct = spearmanr(toks, complexity)
print(f'  CONFOUND: token count vs complexity: rho={rho_ct:+.3f}, p={p_ct:.4f}')

# Partial correlation controlling for token count (if confound present)
if abs(rho_c) > 0.3:
    # Residualize o_rate and complexity on token count, then correlate residuals
    from numpy.polynomial import polynomial as P
    def residualize(y, x):
        coef = np.polyfit(x, y, 1)
        return y - np.polyval(coef, x)
    o_resid = residualize(o_rates, toks)
    c_resid = residualize(complexity.astype(float), toks)
    rho_partial, p_partial = spearmanr(c_resid, o_resid)
    print(f'  Partial corr (controlling token count): rho={rho_partial:+.3f}, p={p_partial:.4f}')

# ===== Show data =====
print('\n=== Per-folio data (sorted by o-rate) ===')
data.sort(key=lambda d: -d['o_rate'])
print(f'{"Folio":<8} {"o-rate":>7} {"complex":>8} {"class":>6} {"toks":>5}')
for d in data:
    print(f'{d["folio"]:<8} {d["o_rate"]:>7.3f} {d["complexity"]:>8} {d["class"]:>6} {d["n_tokens"]:>5}')

# ===== Verdict =====
print('\n' + '=' * 60)
print('=== VERDICT ===')
print('=' * 60)
if test_pass:
    print('SUPPORTED: o-HEAD "arrange" rate tracks plant structural complexity.')
    print('Currier A herbal folios with more-complex plants have more arrangement vocabulary.')
    print('The "A describes botanical spatial structure" hypothesis gains real support.')
else:
    print('NOT SUPPORTED: o-HEAD rate does not track plant complexity (this proxy).')
    print(f'rho={rho:+.3f}, p={p:.3f}. "Arrangement" is more likely staging/organization')
    print('than literal botanical spatial-structure description.')
