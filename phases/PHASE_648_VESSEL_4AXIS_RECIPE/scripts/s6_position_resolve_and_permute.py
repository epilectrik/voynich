"""
Phase 648 Step 6: Convergent test recommended by both experts.

Test 1: POSITION-RESOLUTION of o-prefixes within paragraphs.
  - If ol is paragraph-initial enriched (>2x baseline) → ol is SETUP-PHASE marker
  - If all four o-prefixes are positionally uniform → parallel runtime channels
  - This discriminates crazy-expert's ol-as-setup hypothesis vs runtime-channel hypothesis
  - Also addresses expert-advisor's C1811-C1812 paragraph-scale concern

Test 2: PERMUTATION NULL on the folio-level fire/vessel block differential.
  - Shuffle 7 prefixes into 2 blocks of size {3, 4} randomly 1000 times
  - Compute within-block / cross-block differential under shuffle
  - Compare real differential (+0.295) to null distribution

Test 3: PARAGRAPH-LEVEL replication of the block correlation (per C1811-C1812).
  - Compute prefix rates per paragraph (not per folio)
  - Pairwise correlation across paragraphs
  - Compare differential to folio-level result
"""
import sys
import json
import math
import random
sys.path.insert(0, '.')
from scripts.voynich import Transcript
from collections import defaultdict, Counter

tx = Transcript()

# ---- Build position-resolved data ----
# Group tokens by (folio, paragraph_id) — paragraph_id approximated by counting
# par_initial within folio, since explicit paragraph IDs aren't always available.

# Walk Currier B tokens, assign each a (folio, par_idx, pos_in_par)
paragraphs = defaultdict(list)  # key: (folio, par_idx) -> list of (token, idx_in_par)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

# Compute prefix membership for each token
def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        return 'o' + w[1]
    return None

# ============================================================
# Test 1: Position-resolution within paragraphs
# ============================================================
prefixes = ['ch','sh','qo','ok','ot','ol','or']
# bin counts: early (0-0.33), mid (0.33-0.67), late (0.67-1.0)
bin_counts = {p: {'early': 0, 'mid': 0, 'late': 0, 'total': 0} for p in prefixes}
bin_totals = {'early': 0, 'mid': 0, 'late': 0, 'total': 0}

for (f, par_idx), toks in paragraphs.items():
    n = len(toks)
    if n < 4:
        continue  # skip tiny paragraphs
    for i, t in enumerate(toks):
        pos_frac = i / max(n - 1, 1)
        if pos_frac < 0.33:
            bin_name = 'early'
        elif pos_frac < 0.67:
            bin_name = 'mid'
        else:
            bin_name = 'late'
        bin_totals[bin_name] += 1
        bin_totals['total'] += 1
        pref = prefix_of(t.word)
        if pref:
            bin_counts[pref][bin_name] += 1
            bin_counts[pref]['total'] += 1

print("="*72)
print("TEST 1: POSITION-RESOLUTION OF PREFIXES WITHIN PARAGRAPHS")
print("="*72)
print(f"Paragraph-position bins: early=[0,0.33], mid=[0.33,0.67], late=[0.67,1.0]")
print(f"Total tokens binned: {bin_totals['total']:,}")
print()
print(f"{'Prefix':6s}  {'Early%':>8s}  {'Mid%':>7s}  {'Late%':>7s}  "
      f"{'Early/Base':>11s}  {'Late/Base':>10s}  Verdict")
print("-"*82)

results_pos = {}
for p in prefixes:
    bc = bin_counts[p]
    if bc['total'] == 0:
        continue
    # Conditional rate of prefix in each bin = (prefix in bin) / (all tokens in bin)
    early_rate = bc['early'] / bin_totals['early']
    mid_rate = bc['mid'] / bin_totals['mid']
    late_rate = bc['late'] / bin_totals['late']
    base_rate = bc['total'] / bin_totals['total']

    early_enrich = early_rate / base_rate if base_rate > 0 else float('nan')
    late_enrich = late_rate / base_rate if base_rate > 0 else float('nan')

    # Verdict: is this prefix positionally biased?
    if early_enrich >= 1.5:
        verdict = 'EARLY-enriched (setup?)'
    elif late_enrich >= 1.5:
        verdict = 'LATE-enriched (closure?)'
    elif 0.85 <= early_enrich <= 1.15 and 0.85 <= late_enrich <= 1.15:
        verdict = 'UNIFORM'
    else:
        verdict = 'mixed'

    print(f"{p:6s}  {early_rate*100:7.2f}%  {mid_rate*100:6.2f}%  {late_rate*100:6.2f}%  "
          f"{early_enrich:>10.2f}x  {late_enrich:>9.2f}x  {verdict}")
    results_pos[p] = {
        'early_rate': early_rate, 'mid_rate': mid_rate, 'late_rate': late_rate,
        'base_rate': base_rate, 'early_enrich': early_enrich, 'late_enrich': late_enrich,
        'verdict': verdict, 'n_tokens': bc['total']
    }

print()

# ============================================================
# Test 2: Permutation null on fire/vessel folio-level differential
# ============================================================
print("="*72)
print("TEST 2: PERMUTATION NULL ON FIRE/VESSEL DIFFERENTIAL (+0.295)")
print("="*72)

# Compute per-folio prefix rates (Currier B, >=30 tokens)
folio_total = defaultdict(int)
folio_pref = defaultdict(lambda: Counter())
for t in tx.currier_b():
    folio_total[t.folio] += 1
    p = prefix_of(t.word)
    if p:
        folio_pref[t.folio][p] += 1

folio_rates = {}
for f, n in folio_total.items():
    if n < 30: continue
    folio_rates[f] = {p: folio_pref[f][p]/n for p in prefixes}

folios = list(folio_rates.keys())

def pearson(xs, ys):
    n = len(xs)
    if n < 2: return float('nan')
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs))
    dy = math.sqrt(sum((y-my)**2 for y in ys))
    if dx*dy == 0: return float('nan')
    return num/(dx*dy)

def block_diff(block_a, block_b):
    """Mean within-block correlation minus mean cross-block correlation."""
    def mean_corr(b1, b2):
        cs = []
        for p1 in b1:
            for p2 in b2:
                if p1 == p2: continue
                xs = [folio_rates[f][p1] for f in folios]
                ys = [folio_rates[f][p2] for f in folios]
                cs.append(pearson(xs, ys))
        return sum(cs)/len(cs) if cs else 0
    within = (mean_corr(block_a, block_a) + mean_corr(block_b, block_b)) / 2
    cross = mean_corr(block_a, block_b)
    return within - cross

# Real fire/vessel split
fire = ['ch','sh','qo']
vessel = ['ok','ot','ol','or']
real_diff = block_diff(fire, vessel)
print(f"Real fire/vessel differential: {real_diff:+.4f}")

# Permutation null: random splits of 7 prefixes into {3, 4}
rng = random.Random(42)
n_perm = 1000
null_diffs = []
for _ in range(n_perm):
    shuffled = list(prefixes)
    rng.shuffle(shuffled)
    a = shuffled[:3]
    b = shuffled[3:]
    null_diffs.append(block_diff(a, b))

null_diffs.sort()
n_above = sum(1 for d in null_diffs if d >= real_diff)
p_value = n_above / n_perm

mean_null = sum(null_diffs)/n_perm
median_null = null_diffs[n_perm//2]
p95 = null_diffs[int(n_perm*0.95)]
p99 = null_diffs[int(n_perm*0.99)]

print(f"Null distribution from {n_perm} random splits of 7 prefixes into (3,4):")
print(f"  mean: {mean_null:+.4f}")
print(f"  median: {median_null:+.4f}")
print(f"  95th percentile: {p95:+.4f}")
print(f"  99th percentile: {p99:+.4f}")
print(f"  Real value's percentile rank: 1 - {n_above}/{n_perm} = {(n_perm-n_above)/n_perm*100:.1f}%")
print(f"  p-value (one-sided): {p_value:.4f}")
print()

# ============================================================
# Test 3: Paragraph-level replication
# ============================================================
print("="*72)
print("TEST 3: PARAGRAPH-LEVEL REPLICATION (per C1811-C1812)")
print("="*72)

par_total = defaultdict(int)
par_pref = defaultdict(lambda: Counter())
for (f, par_idx), toks in paragraphs.items():
    if len(toks) < 15: continue  # skip tiny paragraphs
    key = (f, par_idx)
    par_total[key] = len(toks)
    for t in toks:
        p = prefix_of(t.word)
        if p:
            par_pref[key][p] += 1

par_rates = {k: {p: par_pref[k][p]/par_total[k] for p in prefixes}
             for k in par_total}
par_keys = list(par_rates.keys())
print(f"Paragraphs profiled (>=15 tokens): {len(par_keys)}")

# Override globals so block_diff uses paragraphs
folios_orig = folios
folio_rates_orig = folio_rates
folios = par_keys
folio_rates = par_rates

real_diff_par = block_diff(fire, vessel)
print(f"Paragraph-level fire/vessel differential: {real_diff_par:+.4f}")
print(f"Folio-level differential: {real_diff:+.4f}")
print()
if real_diff_par > 0.10:
    print("PARAGRAPH-LEVEL: differential survives — fire/vessel split is genuine")
    print("at paragraph scale. Not a folio-aggregation artifact.")
elif real_diff_par > 0:
    print("PARAGRAPH-LEVEL: differential is positive but weaker.")
    print("Folio-level result is partially aggregation-mediated.")
else:
    print("PARAGRAPH-LEVEL: differential disappears or reverses.")
    print("Folio-level finding is an aggregation artifact per C1811-C1812.")

# Run permutation at paragraph level too
null_diffs_par = []
for _ in range(n_perm):
    shuffled = list(prefixes)
    rng.shuffle(shuffled)
    null_diffs_par.append(block_diff(shuffled[:3], shuffled[3:]))
null_diffs_par.sort()
n_above_par = sum(1 for d in null_diffs_par if d >= real_diff_par)
p_par = n_above_par / n_perm
print(f"Paragraph-level permutation p-value: {p_par:.4f}")

# Save
folios = folios_orig
folio_rates = folio_rates_orig
out = {
    'test1_position': results_pos,
    'test2_permutation': {
        'real_differential': real_diff,
        'p_value': p_value,
        'null_mean': mean_null, 'null_median': median_null,
        'null_p95': p95, 'null_p99': p99,
    },
    'test3_paragraph_replication': {
        'real_differential_paragraph': real_diff_par,
        'real_differential_folio': real_diff,
        'p_value_paragraph': p_par,
        'n_paragraphs': len(par_keys),
    }
}
with open('phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/position_and_permutation.json', 'w') as f:
    json.dump(out, f, indent=2)
print()
print("Saved: phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/position_and_permutation.json")
