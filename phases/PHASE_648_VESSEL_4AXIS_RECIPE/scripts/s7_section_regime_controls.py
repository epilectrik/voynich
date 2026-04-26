"""
Phase 648 Step 7: Section + REGIME controls on paragraph-level fire/vessel differential.

Per expert-advisor's tier criteria, the +0.131 paragraph-level differential (p=0.024)
needs to survive:
1. Within-section restriction (rules out C1404 section-confounding)
2. Within-regime restriction (rules out C1300/C1547 regime-confounding)

Both must pass for Tier 2 promotion. Either failure → Tier 3.
"""
import sys
import json
import math
import random
sys.path.insert(0, '.')
from scripts.voynich import Transcript
from collections import defaultdict, Counter

tx = Transcript()

# Load regime assignments
with open('data/regime_folio_mapping.json') as f:
    regime_data = json.load(f)
regime_assignments = regime_data['regime_assignments']

# Group tokens into paragraphs
paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        return 'o' + w[1]
    return None

prefixes = ['ch','sh','qo','ok','ot','ol','or']
fire = ['ch','sh','qo']
vessel = ['ok','ot','ol','or']

# Build paragraph-level rate vectors with metadata
par_rates = {}
par_meta = {}  # section, regime
for (f, par_idx), toks in paragraphs.items():
    if len(toks) < 15: continue
    n = len(toks)
    counts = Counter()
    for t in toks:
        p = prefix_of(t.word)
        if p:
            counts[p] += 1
    par_rates[(f, par_idx)] = {p: counts[p]/n for p in prefixes}
    section = toks[0].section
    regime = regime_assignments.get(f, {}).get('regime', None)
    par_meta[(f, par_idx)] = {'section': section, 'regime': regime, 'folio': f}

def pearson(xs, ys):
    n = len(xs)
    if n < 3: return float('nan')
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs))
    dy = math.sqrt(sum((y-my)**2 for y in ys))
    if dx*dy == 0: return float('nan')
    return num/(dx*dy)

def block_diff(par_subset, block_a, block_b):
    """Mean within-block correlation minus mean cross-block correlation,
       computed across the paragraph subset."""
    keys = list(par_subset)
    if len(keys) < 10: return float('nan')
    def mean_corr(b1, b2):
        cs = []
        for p1 in b1:
            for p2 in b2:
                if p1 == p2: continue
                xs = [par_subset[k][p1] for k in keys]
                ys = [par_subset[k][p2] for k in keys]
                r = pearson(xs, ys)
                if not math.isnan(r):
                    cs.append(r)
        return sum(cs)/len(cs) if cs else float('nan')
    within = (mean_corr(block_a, block_a) + mean_corr(block_b, block_b)) / 2
    cross = mean_corr(block_a, block_b)
    if math.isnan(within) or math.isnan(cross): return float('nan')
    return within - cross

def perm_p(par_subset, real_diff, n_perm=1000, seed=42):
    rng = random.Random(seed)
    null = []
    for _ in range(n_perm):
        shuffled = list(prefixes)
        rng.shuffle(shuffled)
        d = block_diff(par_subset, shuffled[:3], shuffled[3:])
        if not math.isnan(d):
            null.append(d)
    if not null: return float('nan')
    n_above = sum(1 for d in null if d >= real_diff)
    return n_above / len(null)

# ---------- Baseline (all paragraphs) ----------
print("="*72)
print("BASELINE: all paragraphs (already established at Step 6)")
print("="*72)
all_diff = block_diff(par_rates, fire, vessel)
all_p = perm_p(par_rates, all_diff)
print(f"  Differential: {all_diff:+.4f}, p = {all_p:.4f}, n = {len(par_rates)}")

# ---------- Test A: within-section ----------
print()
print("="*72)
print("TEST A: WITHIN-SECTION CONTROLS (per C1404)")
print("="*72)
print("Filter paragraphs by section, recompute fire/vessel differential.")
print()

by_section = defaultdict(dict)
for k, m in par_meta.items():
    if m['section']:
        by_section[m['section']][k] = par_rates[k]

print(f"{'Section':>8s}  {'n':>4s}  {'Diff':>8s}  {'p-value':>8s}  Verdict")
print("-"*55)
section_results = {}
for sec, sub in sorted(by_section.items()):
    if len(sub) < 20:
        continue
    d = block_diff(sub, fire, vessel)
    if math.isnan(d):
        print(f"{sec:>8s}  {len(sub):>4d}   nan       —      insufficient data")
        continue
    p = perm_p(sub, d)
    if d > 0.05 and p < 0.10:
        v = 'SURVIVES'
    elif d > 0:
        v = 'directional'
    else:
        v = 'fails'
    print(f"{sec:>8s}  {len(sub):>4d}  {d:+.4f}  {p:>7.4f}   {v}")
    section_results[sec] = {'n': len(sub), 'diff': d, 'p': p, 'verdict': v}

# ---------- Test B: within-regime ----------
print()
print("="*72)
print("TEST B: WITHIN-REGIME CONTROLS (per C1300/C1547)")
print("="*72)
print("Filter paragraphs by REGIME assignment, recompute differential.")
print()

by_regime = defaultdict(dict)
for k, m in par_meta.items():
    if m['regime']:
        by_regime[m['regime']][k] = par_rates[k]

print(f"{'Regime':>10s}  {'n':>4s}  {'Diff':>8s}  {'p-value':>8s}  Verdict")
print("-"*55)
regime_results = {}
for reg, sub in sorted(by_regime.items()):
    if len(sub) < 20:
        continue
    d = block_diff(sub, fire, vessel)
    if math.isnan(d):
        print(f"{reg:>10s}  {len(sub):>4d}   nan       —      insufficient data")
        continue
    p = perm_p(sub, d)
    if d > 0.05 and p < 0.10:
        v = 'SURVIVES'
    elif d > 0:
        v = 'directional'
    else:
        v = 'fails'
    print(f"{reg:>10s}  {len(sub):>4d}  {d:+.4f}  {p:>7.4f}   {v}")
    regime_results[reg] = {'n': len(sub), 'diff': d, 'p': p, 'verdict': v}

# ---------- Synthesis ----------
print()
print("="*72)
print("SYNTHESIS")
print("="*72)
sec_survive = sum(1 for r in section_results.values() if r['verdict'] == 'SURVIVES')
sec_directional = sum(1 for r in section_results.values()
                      if r['verdict'] in ('SURVIVES','directional'))
sec_total = len(section_results)
reg_survive = sum(1 for r in regime_results.values() if r['verdict'] == 'SURVIVES')
reg_directional = sum(1 for r in regime_results.values()
                      if r['verdict'] in ('SURVIVES','directional'))
reg_total = len(regime_results)

print(f"Sections: {sec_survive}/{sec_total} survive at p<0.10, "
      f"{sec_directional}/{sec_total} directional")
print(f"Regimes:  {reg_survive}/{reg_total} survive at p<0.10, "
      f"{reg_directional}/{reg_total} directional")

print()
if sec_directional >= sec_total - 1 and reg_directional >= reg_total - 1:
    print("VERDICT: Architecture survives both controls in majority of strata.")
    print("→ Tier 2 promotion supported.")
elif sec_directional >= sec_total // 2 and reg_directional >= reg_total // 2:
    print("VERDICT: Architecture partially survives controls.")
    print("→ Tier 3 with documented section/regime modulation.")
else:
    print("VERDICT: Architecture fails majority of within-stratum controls.")
    print("→ Tier 3-4: likely a section/regime-confounded folio-level effect.")

with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/section_regime_controls.json', 'w') as f:
    json.dump({
        'baseline': {'diff': all_diff, 'p': all_p, 'n': len(par_rates)},
        'sections': section_results,
        'regimes': regime_results,
    }, f, indent=2)
print()
print("Saved: phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/section_regime_controls.json")
