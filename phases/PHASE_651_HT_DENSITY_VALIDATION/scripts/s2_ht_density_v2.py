"""
HT-density test v2: better metrics, four-way partial correlation.

The first test had bad metrics. This version tests four predictors:
1. Distinct compound MIDDLE count (uncapped) — better specification metric
2. Folio token count — condensation-pressure metric (short = compress)
3. sh-rate — passive-monitoring intensity (attention-maintenance proxy)
4. qo-rate — active heat-application (inverse of passive monitoring)

Expected patterns by reading:
- Specification (C935): HT positively correlates with distinct compound MIDDLEs
- Condensation: HT INVERSELY correlates with folio length
- Attention: HT positively correlates with sh-rate
- Active vs passive: HT inversely correlates with qo-rate (more active fire = less HT)
"""
import sys
import json
import math
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')

# Build per-folio metrics
folio_total = defaultdict(int)
folio_ht = defaultdict(int)
folio_compound_middles = defaultdict(set)  # distinct compound MIDDLEs
folio_sh = defaultdict(int)
folio_qo = defaultdict(int)

for t in tx.currier_b():
    f = t.folio
    folio_total[f] += 1
    w = t.word

    if w.startswith('sh'):
        folio_sh[f] += 1
    if w.startswith('qo'):
        folio_qo[f] += 1

    m = morph.extract(w)
    if m.middle and len(m.middle) >= 2:
        try:
            if mid_analyzer.is_compound(m.middle):
                folio_ht[f] += 1
                folio_compound_middles[f].add(m.middle)
        except Exception:
            pass

# Per-folio metrics dict
folio_metrics = {}
for f in folio_total:
    if folio_total[f] < 30: continue
    folio_metrics[f] = {
        'total': folio_total[f],
        'ht_rate': folio_ht[f] / folio_total[f],
        'distinct_compound_middles': len(folio_compound_middles[f]),
        'sh_rate': folio_sh[f] / folio_total[f],
        'qo_rate': folio_qo[f] / folio_total[f],
    }

print("="*78)
print("HT-DENSITY TEST v2 (improved metrics)")
print("="*78)
print(f"\nFolios: {len(folio_metrics)}")

# Spearman
def spearman_rho(x, y):
    n = len(x)
    if n < 3: return float('nan')
    def rank(arr):
        s = sorted(range(len(arr)), key=lambda i: arr[i])
        r = [0] * len(arr)
        for ri, idx in enumerate(s):
            r[idx] = ri + 1
        i = 0
        while i < len(arr):
            j = i
            while j + 1 < len(arr) and arr[s[j+1]] == arr[s[i]]:
                j += 1
            if j > i:
                avg = (i + j + 2) / 2
                for k in range(i, j+1):
                    r[s[k]] = avg
            i = j + 1
        return r
    rx = rank(x); ry = rank(y)
    n = len(x)
    mx = sum(rx)/n; my = sum(ry)/n
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    dx = math.sqrt(sum((r-mx)**2 for r in rx))
    dy = math.sqrt(sum((r-my)**2 for r in ry))
    if dx*dy == 0: return float('nan')
    return num/(dx*dy)

# Permutation p-value
import random
def perm_p(x, y, real_rho, n_perm=2000, seed=42):
    rng = random.Random(seed)
    nulls = []
    for _ in range(n_perm):
        sh = list(y)
        rng.shuffle(sh)
        r = spearman_rho(x, sh)
        if not math.isnan(r):
            nulls.append(r)
    n_above = sum(1 for r in nulls if r >= real_rho)
    n_below = sum(1 for r in nulls if r <= real_rho)
    return min(n_above, n_below) / len(nulls) * 2  # two-sided

folios = list(folio_metrics.keys())
ht = [folio_metrics[f]['ht_rate'] for f in folios]

print()
print("Pairwise Spearman correlations with HT rate:")
print(f"{'Predictor':<35s}  {'rho':>7s}  {'p (two-sided)':>14s}")
print("-"*60)

predictors = {
    'distinct_compound_middles (specification)': [folio_metrics[f]['distinct_compound_middles'] for f in folios],
    'total tokens (condensation - inverse)':     [folio_metrics[f]['total'] for f in folios],
    'sh_rate (passive monitoring)':              [folio_metrics[f]['sh_rate'] for f in folios],
    'qo_rate (active fire)':                     [folio_metrics[f]['qo_rate'] for f in folios],
}

results = {}
for name, vals in predictors.items():
    rho = spearman_rho(ht, vals)
    p = perm_p(ht, vals, rho)
    results[name] = {'rho': rho, 'p': p}
    sig = '*' if p < 0.05 else (' ' if p > 0.10 else '+')
    print(f"  {name:<35s}  {rho:>+7.3f}  {p:>14.4f}{sig}")

# Within-section to control for section confound
print()
print("="*78)
print("WITHIN-SECTION: HT vs total tokens (condensation hypothesis)")
print("="*78)
section_folios = defaultdict(list)
for f in folios:
    sec = next((t.section for t in tx.currier_b() if t.folio == f), '?')
    section_folios[sec].append(f)

for sec, sec_folios in sorted(section_folios.items()):
    if len(sec_folios) < 6: continue
    s_ht = [folio_metrics[f]['ht_rate'] for f in sec_folios]
    s_tot = [folio_metrics[f]['total'] for f in sec_folios]
    s_compounds = [folio_metrics[f]['distinct_compound_middles'] for f in sec_folios]
    rho_tot = spearman_rho(s_ht, s_tot)
    rho_comp = spearman_rho(s_ht, s_compounds)
    print(f"\n  Section {sec} (n={len(sec_folios)}):")
    print(f"    HT vs total tokens:        rho = {rho_tot:+.3f}")
    print(f"    HT vs distinct compounds:  rho = {rho_comp:+.3f}")

# Save
import os
os.makedirs('scratch', exist_ok=True)
with open('scratch/ht_density_v2.json', 'w') as f:
    json.dump({'predictors': results, 'folio_metrics': folio_metrics}, f, indent=2, default=str)
print()
print("Saved: scratch/ht_density_v2.json")
