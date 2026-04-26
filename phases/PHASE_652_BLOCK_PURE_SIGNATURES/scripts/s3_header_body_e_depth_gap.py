"""
Test C1967 Tier 3 candidate: e_depth as attentional commitment.

If e_depth indexes attentional commitment to thermal specification:
- Paragraph HEADERS (specification, MARKING-enriched per C1287) should have
  HIGHER e_depth than paragraph BODIES
- The gap should be LARGEST in qo-class paragraphs (drivers commit most
  thermal precision at setup)
- The gap should be SMALLEST in sh-class paragraphs (passive monitors
  don't commit thermal precision at all)

Header definition: tokens in the first line of the paragraph (par_initial=True
through line_initial=True boundary, until line break).
Body: rest of the paragraph.

If the prediction holds: Tier 3 reframing promoted from candidate to
established interpretation. If not: C1967 stays narrow.
"""
import sys
import json
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

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
    """Header = tokens on the first line of the paragraph.
    Body = tokens on subsequent lines."""
    if not toks: return [], []
    first_line = toks[0].line
    header = [t for t in toks if t.line == first_line]
    body = [t for t in toks if t.line != first_line]
    return header, body

def mean_e_depth(toks):
    if not toks: return None
    depths = []
    for t in toks:
        try:
            a = morph.atomize(t.word)
            depths.append(a.e_depth)
        except Exception:
            pass
    if not depths: return None
    return sum(depths) / len(depths)

# Classify paragraphs and compute header/body e_depth
results_by_class = defaultdict(list)
for (folio, par_idx), toks in paragraphs.items():
    if len(toks) < 8: continue
    # Need at least 2 lines for header/body split
    lines = set(t.line for t in toks)
    if len(lines) < 2: continue

    # Classify dominant channel
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

    # Split header/body
    header, body = split_header_body(toks)
    if len(header) < 2 or len(body) < 2: continue

    h_e = mean_e_depth(header)
    b_e = mean_e_depth(body)
    if h_e is None or b_e is None: continue

    results_by_class[dom_channel].append({
        'folio': folio, 'par_idx': par_idx,
        'header_e_depth': h_e, 'body_e_depth': b_e,
        'gap': h_e - b_e,
        'header_n': len(header), 'body_n': len(body),
    })

print("="*78)
print("HEADER vs BODY e_depth GAP (block-pure paragraphs, 2+ lines)")
print("="*78)
print()
print(f"{'Class':>6s}  {'n':>4s}  {'Mean Header':>12s}  {'Mean Body':>10s}  {'Gap (H-B)':>10s}")
print("-"*60)

# Compute means per class
for ch in ('qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'or'):
    par_list = results_by_class.get(ch, [])
    if len(par_list) < 5:
        if par_list:
            print(f"  {ch:>4s}  {len(par_list):>4d}  --  --  --  (too few)")
        continue
    h_means = [d['header_e_depth'] for d in par_list]
    b_means = [d['body_e_depth'] for d in par_list]
    gaps = [d['gap'] for d in par_list]
    mh = sum(h_means)/len(h_means)
    mb = sum(b_means)/len(b_means)
    mg = sum(gaps)/len(gaps)
    print(f"  {ch:>4s}  {len(par_list):>4d}  {mh:>12.3f}  {mb:>10.3f}  {mg:>+10.3f}")

# Significance tests
print()
print("="*78)
print("SIGNIFICANCE TESTS")
print("="*78)
import math
import random

def paired_t_approx(diffs):
    """Paired t-test approximation. Returns (mean_diff, t-stat, p-value approx)."""
    if len(diffs) < 3: return None
    n = len(diffs)
    mean = sum(diffs)/n
    var = sum((d - mean)**2 for d in diffs) / (n - 1)
    if var <= 0: return None
    se = math.sqrt(var / n)
    t = mean / se
    # Two-sided p-value approx (normal approximation for large n)
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    return {'mean': mean, 't': t, 'p': p, 'n': n}

print()
print("Paired test (header > body within paragraph):")
for ch in ('qo', 'ch', 'sh'):
    par_list = results_by_class.get(ch, [])
    if len(par_list) < 5: continue
    gaps = [d['gap'] for d in par_list]
    result = paired_t_approx(gaps)
    if result:
        sig = ' *' if result['p'] < 0.05 else ('+' if result['p'] < 0.10 else '')
        print(f"  {ch}-class:  mean gap = {result['mean']:+.3f}, t={result['t']:+.2f}, p={result['p']:.4f}, n={result['n']}{sig}")

# Cross-class comparison: is qo-gap > sh-gap?
print()
print("Cross-class: does qo-gap differ from sh-gap?")
qo_gaps = [d['gap'] for d in results_by_class.get('qo', [])]
sh_gaps = [d['gap'] for d in results_by_class.get('sh', [])]
ch_gaps = [d['gap'] for d in results_by_class.get('ch', [])]
if qo_gaps and sh_gaps:
    qo_mean = sum(qo_gaps)/len(qo_gaps)
    sh_mean = sum(sh_gaps)/len(sh_gaps)
    diff = qo_mean - sh_mean
    print(f"  qo mean gap: {qo_mean:+.3f} (n={len(qo_gaps)})")
    print(f"  ch mean gap: {sum(ch_gaps)/len(ch_gaps):+.3f} (n={len(ch_gaps)})")
    print(f"  sh mean gap: {sh_mean:+.3f} (n={len(sh_gaps)})")
    print(f"  qo - sh = {diff:+.3f}")

    # Permutation test: shuffle class labels, recompute difference
    rng = random.Random(42)
    combined = qo_gaps + sh_gaps
    n_qo = len(qo_gaps)
    null_diffs = []
    for _ in range(2000):
        c = list(combined)
        rng.shuffle(c)
        nq = c[:n_qo]
        ns = c[n_qo:]
        null_diffs.append(sum(nq)/len(nq) - sum(ns)/len(ns))
    n_above = sum(1 for d in null_diffs if d >= diff)
    p = n_above / 2000
    print(f"  Permutation p (qo > sh, one-sided): {p:.4f}")

# Save
import os
os.makedirs('scratch', exist_ok=True)
with open('scratch/header_body_e_depth_gap.json', 'w') as f:
    json.dump({ch: [{k: v for k, v in d.items()} for d in lst]
               for ch, lst in results_by_class.items()}, f, indent=2, default=str)
print()
print("Saved: scratch/header_body_e_depth_gap.json")
