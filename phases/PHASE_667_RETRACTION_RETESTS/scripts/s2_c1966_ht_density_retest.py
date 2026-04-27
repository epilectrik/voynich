"""
Phase 667 s2 — C1966 retest: HT density tracks compound-spec load

Original claim: rho=+0.602 between HT rate and distinct compound MIDDLEs.
Problem: type-token confound — more HT tokens mechanically sample more types.

Fix: partial Spearman correlation controlling for total HT token count.
If HT rate still correlates with compound MIDDLE diversity after removing
the effect of total HT count, the signal is real.
"""
import sys
import io
import json
import math
import random
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

tx = Transcript()
morph = Morphology()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')

folio_total = defaultdict(int)
folio_ht_count = defaultdict(int)
folio_compound_middles = defaultdict(set)

for t in tx.currier_b():
    f = t.folio
    folio_total[f] += 1
    m = morph.extract(t.word)
    if m.middle and len(m.middle) >= 2:
        try:
            if mid_analyzer.is_compound(m.middle):
                folio_ht_count[f] += 1
                folio_compound_middles[f].add(m.middle)
        except Exception:
            pass

folios = [f for f in folio_total if folio_total[f] >= 30]


def rank(values):
    sorted_pairs = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(sorted_pairs):
        j = i
        while j < len(sorted_pairs) - 1 and sorted_pairs[j+1][1] == sorted_pairs[i][1]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[sorted_pairs[k][0]] = avg
        i = j + 1
    return ranks


def spearman(a, b):
    n = len(a)
    if n < 3:
        return 0.0
    ra = rank(a)
    rb = rank(b)
    ma = sum(ra) / n
    mb = sum(rb) / n
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((x - mb) ** 2 for x in rb))
    return num / (da * db) if da * db > 0 else 0.0


def partial_spearman(x, y, z):
    """Partial Spearman correlation between x and y, controlling for z."""
    rxy = spearman(x, y)
    rxz = spearman(x, z)
    ryz = spearman(y, z)
    denom = math.sqrt((1 - rxz**2) * (1 - ryz**2))
    if denom <= 0:
        return 0.0
    return (rxy - rxz * ryz) / denom


def perm_test_partial(x, y, z, n_perm=10000, seed=20260427):
    obs = partial_spearman(x, y, z)
    rng = random.Random(seed)
    n_ge = 0
    for _ in range(n_perm):
        y_shuf = y[:]
        rng.shuffle(y_shuf)
        if partial_spearman(x, y_shuf, z) >= obs:
            n_ge += 1
    return obs, n_ge / n_perm


def perm_test_simple(x, y, n_perm=10000, seed=20260427):
    obs = spearman(x, y)
    rng = random.Random(seed)
    n_ge = 0
    for _ in range(n_perm):
        y_shuf = y[:]
        rng.shuffle(y_shuf)
        if spearman(x, y_shuf) >= obs:
            n_ge += 1
    return obs, n_ge / n_perm


ht_rate = [folio_ht_count[f] / folio_total[f] for f in folios]
ht_count = [folio_ht_count[f] for f in folios]
distinct_compounds = [len(folio_compound_middles[f]) for f in folios]

print('=== C1966 Retest: HT Density vs Compound-Spec Load ===')
print(f'Folios: {len(folios)}')

# Original test (reproduce)
rho_orig, p_orig = perm_test_simple(ht_rate, distinct_compounds)
print(f'\nOriginal (bivariate):')
print(f'  HT rate vs distinct compounds: rho = {rho_orig:+.3f}, p = {p_orig:.4f}')

# Confound check
rho_confound, _ = perm_test_simple(ht_count, distinct_compounds)
print(f'\nConfound check:')
print(f'  HT token COUNT vs distinct compounds: rho = {rho_confound:+.3f}')
print(f'  (type-token coupling — this should be strongly positive)')

# Partial correlation (the actual test)
print(f'\nPartial Spearman (controlling for HT token count):')
rho_partial, p_partial = perm_test_partial(ht_rate, distinct_compounds, ht_count)
print(f'  HT rate vs distinct compounds | HT count: rho = {rho_partial:+.3f}, p = {p_partial:.4f}')

# Verdict
print('\n=== VERDICT ===')
if rho_partial > 0 and p_partial <= 0.05:
    print(f'Signal SURVIVES confound control. HT rate tracks compound diversity')
    print(f'independently of total HT token count.')
    verdict = 'CONFIRMED'
elif rho_partial > 0 and p_partial <= 0.20:
    print(f'DIRECTIONAL signal after confound control, but not significant.')
    verdict = 'DIRECTIONAL'
elif rho_partial <= 0:
    print(f'Signal DOES NOT SURVIVE confound control. Original rho was type-token artifact.')
    verdict = 'FALSIFIED'
else:
    print(f'Inconclusive after confound control.')
    verdict = 'INCONCLUSIVE'
print(f'Verdict: {verdict}')

out = {
    'n_folios': len(folios),
    'original_rho': rho_orig,
    'original_p': p_orig,
    'confound_rho_count_vs_types': rho_confound,
    'partial_rho': rho_partial,
    'partial_p': p_partial,
    'verdict': verdict,
}

out_dir = REPO_ROOT / 'phases' / 'PHASE_667_RETRACTION_RETESTS' / 'results'
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / 'C1966_RETEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(f'\nWrote results.')
