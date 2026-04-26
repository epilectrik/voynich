"""
Symmetric test to C1967 supplement: do paragraph headers have HIGHER
HT density than paragraph bodies?

C1967 supplement found bodies > headers in e_depth (thermal commitment
lives in body). The architectural reading: headers = compound specification
(high HT per C1966), bodies = thermal execution (high e_depth per C1967).

Symmetric prediction: headers > bodies in HT density.

If both hold, the what-vs-how header-body division is empirically anchored
on both dimensions:
- Header: high HT (compound spec) + low e_depth (less thermal commitment)
- Body: low HT (less compound spec) + high e_depth (thermal execution)
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

# Group tokens into paragraphs
paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

FIRE = {'ch', 'sh', 'qo'}
VESSEL = {'ok', 'ot', 'ol', 'or'}

def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        return 'o' + w[1]
    return None

def block_of(p):
    if p in FIRE: return 'F'
    if p in VESSEL: return 'V'
    return None

def split_header_body(toks):
    if not toks: return [], []
    first_line = toks[0].line
    header = [t for t in toks if t.line == first_line]
    body = [t for t in toks if t.line != first_line]
    return header, body

def ht_rate(toks):
    if not toks: return None
    n_ht = 0
    for t in toks:
        m = morph.extract(t.word)
        if m.middle and len(m.middle) >= 2:
            try:
                if mid_analyzer.is_compound(m.middle):
                    n_ht += 1
            except Exception:
                pass
    return n_ht / len(toks)

# Same paragraph filtering as C1967 supplement
results_by_class = defaultdict(list)
for (folio, par_idx), toks in paragraphs.items():
    if len(toks) < 8: continue
    lines = set(t.line for t in toks)
    if len(lines) < 2: continue

    prefix_counts = Counter()
    block_counts = Counter()
    for t in toks:
        p = prefix_of(t.word)
        if p:
            prefix_counts[p] += 1
            block_counts[block_of(p)] += 1
    target_total = sum(prefix_counts.values())
    if target_total < 4: continue

    fire_frac = block_counts.get('F', 0) / target_total
    vessel_frac = block_counts.get('V', 0) / target_total
    block_pure = max(fire_frac, vessel_frac) > 0.70
    if not block_pure: continue

    dominant_block = 'F' if fire_frac > vessel_frac else 'V'
    block_prefixes = (FIRE if dominant_block == 'F' else VESSEL)
    dom_channel = max(block_prefixes, key=lambda p: prefix_counts.get(p, 0))

    header, body = split_header_body(toks)
    if len(header) < 2 or len(body) < 2: continue

    h_ht = ht_rate(header)
    b_ht = ht_rate(body)
    if h_ht is None or b_ht is None: continue

    results_by_class[dom_channel].append({
        'folio': folio, 'par_idx': par_idx,
        'header_ht': h_ht, 'body_ht': b_ht,
        'gap': h_ht - b_ht,
        'header_n': len(header), 'body_n': len(body),
    })

# Print summary
print("="*78)
print("HEADER vs BODY HT density (block-pure paragraphs, 2+ lines)")
print("="*78)
print()
print("Prediction (symmetric to C1967 supplement):")
print("  Headers should have HIGHER HT density than bodies")
print("  (compound specification lives in header, per C1966)")
print()
print(f"{'Class':>6s}  {'n':>4s}  {'Mean Header':>12s}  {'Mean Body':>10s}  {'Gap (H-B)':>10s}")
print("-"*60)

import math, random
def paired_t(diffs):
    if len(diffs) < 3: return None
    n = len(diffs)
    mean = sum(diffs)/n
    var = sum((d - mean)**2 for d in diffs) / (n - 1)
    if var <= 0: return None
    se = math.sqrt(var / n)
    t = mean / se
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    return {'mean': mean, 't': t, 'p': p, 'n': n}

for ch in ('qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'or'):
    par_list = results_by_class.get(ch, [])
    if len(par_list) < 5:
        if par_list:
            print(f"  {ch:>4s}  {len(par_list):>4d}  --  --  --  (too few)")
        continue
    h_means = [d['header_ht'] for d in par_list]
    b_means = [d['body_ht'] for d in par_list]
    gaps = [d['gap'] for d in par_list]
    mh = sum(h_means)/len(h_means)
    mb = sum(b_means)/len(b_means)
    mg = sum(gaps)/len(gaps)
    print(f"  {ch:>4s}  {len(par_list):>4d}  {mh:>12.3f}  {mb:>10.3f}  {mg:>+10.3f}")

print()
print("Significance tests (paired, header vs body):")
for ch in ('qo', 'ch', 'sh'):
    par_list = results_by_class.get(ch, [])
    if len(par_list) < 5: continue
    gaps = [d['gap'] for d in par_list]
    res = paired_t(gaps)
    if res:
        sig = ' *' if res['p'] < 0.05 else (' +' if res['p'] < 0.10 else '')
        print(f"  {ch}-class: mean gap = {res['mean']:+.3f}, t={res['t']:+.2f}, p={res['p']:.4f}, n={res['n']}{sig}")

# Cross-class: is gap-magnitude monotonic across classes?
print()
print("Cross-class gap pattern:")
qo_gaps = [d['gap'] for d in results_by_class.get('qo', [])]
ch_gaps = [d['gap'] for d in results_by_class.get('ch', [])]
sh_gaps = [d['gap'] for d in results_by_class.get('sh', [])]
if qo_gaps and ch_gaps and sh_gaps:
    qm = sum(qo_gaps)/len(qo_gaps)
    cm = sum(ch_gaps)/len(ch_gaps)
    sm = sum(sh_gaps)/len(sh_gaps)
    print(f"  qo gap: {qm:+.3f}  ch gap: {cm:+.3f}  sh gap: {sm:+.3f}")
    # Permutation test qo vs sh
    rng = random.Random(42)
    real_diff = qm - sm
    combined = qo_gaps + sh_gaps
    n_qo = len(qo_gaps)
    null_diffs = []
    for _ in range(2000):
        c = list(combined); rng.shuffle(c)
        nq = c[:n_qo]; ns = c[n_qo:]
        null_diffs.append(sum(nq)/len(nq) - sum(ns)/len(ns))
    p = sum(1 for d in null_diffs if abs(d) >= abs(real_diff)) / 2000
    print(f"  qo gap vs sh gap difference: {real_diff:+.3f}, perm p (two-sided) = {p:.4f}")

import os
with open('scratch/header_body_ht_density.json', 'w') as f:
    json.dump({ch: lst for ch, lst in results_by_class.items()}, f, indent=2, default=str)
print()
print("Saved: scratch/header_body_ht_density.json")
