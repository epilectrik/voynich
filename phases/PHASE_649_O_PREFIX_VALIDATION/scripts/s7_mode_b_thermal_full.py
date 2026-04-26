"""
Phase 649 Step 7: Mode-B-fraction vs thermal-mass tier across all matched
paragraphs (not just qo+ok subset).

Hypothesis: thermal-mass apparatus encodes more sustained execution between
operator interventions. If true, Mode B fraction (per C1230/C1246: bare-suffix
heavy = sustained / passive monitoring) should correlate with vessel-thermal
tier across all matched-folio paragraphs.

Method:
1. For each matched-folio paragraph, classify thermal-tier from recipe text
2. Compute Mode B fraction of the paragraph's lines (lines below 30% terminal-suffix)
3. Spearman rho: tier vs Mode B fraction
4. Permutation null
5. Within-section restriction (control for section confound)

This uses the full matched-paragraph set (no qo+ok filter), expanding N.
"""
import sys
import json
import math
import random
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as fp:
    matches = json.load(fp)
with open('phases/SISMEL_RECIPE_CORPUS/results/sismel_corpus.json', encoding='utf-8') as fp:
    corpus = json.load(fp)

def get_chapter(part, num):
    for ch in corpus['parts'][part]['chapters']:
        if ch['chapter_num'] == num:
            return ch
    return None

TIER_KEYWORDS = {
    4: ['podri', 'putrefa', 'fermenta'],
    3: ['bany', 'balne', 'mari'],
    2: ['cendr', 'cineri', 'arena'],
    1: ['foch', 'igne', 'calcin', 'sublim'],
}
TIER_NAMES = {4: 'Putrefaction', 3: 'Balneum mariae',
              2: 'Ashes/sand', 1: 'Direct fire'}

def classify_text_tier(text):
    text_l = text.lower()
    for tier in (4, 3, 2, 1):
        for kw in TIER_KEYWORDS[tier]:
            if kw in text_l:
                return tier
    return 0

# Map matched paragraphs to tiers
folio_par_tier = {}
for m in matches:
    f = m['folio']
    ch = get_chapter(m['part'], m['chapter_num'])
    if not ch: continue
    for p_idx, p in enumerate(ch.get('paragraphs', [])):
        text = (p.get('catalan') or '') + ' ' + (p.get('latin') or '')
        folio_par_tier[(f, p_idx)] = classify_text_tier(text)

# Walk Currier B tokens, group by paragraph + line
paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

# Mode B classifier
TERMINAL_SUFFIXES = {'dy','edy','eedy','y','ey','ody','eody'}
def line_is_mode_b(toks_in_line):
    if len(toks_in_line) < 3: return None
    n_term = sum(1 for t in toks_in_line
                 if morph.extract(t.word).suffix in TERMINAL_SUFFIXES)
    return (n_term / len(toks_in_line)) < 0.30

# For each matched-folio paragraph, compute Mode B fraction
results = []
for (f, par_idx), toks in paragraphs.items():
    if (f, par_idx) not in folio_par_tier: continue
    tier = folio_par_tier[(f, par_idx)]
    if tier == 0: continue
    if len(toks) < 8: continue  # need enough for line classification

    # Group tokens by line
    by_line = defaultdict(list)
    for t in toks:
        by_line[t.line].append(t)
    if len(by_line) < 2: continue

    # Mode B fraction: lines classified Mode B / lines with classification
    classifications = [line_is_mode_b(line_toks) for line_toks in by_line.values()]
    valid = [c for c in classifications if c is not None]
    if len(valid) < 2: continue
    mode_b_frac = sum(1 for c in valid if c) / len(valid)

    section = toks[0].section
    results.append({
        'folio': f, 'par_idx': par_idx, 'tier': tier,
        'mode_b_frac': mode_b_frac,
        'n_lines': len(valid),
        'n_tokens': len(toks),
        'section': section,
    })

print("="*72)
print("MODE B FRACTION vs THERMAL TIER (all matched paragraphs)")
print("="*72)
print(f"\nMatched-folio paragraphs analyzed: {len(results)}")

# Tier distribution
print()
print(f"{'Tier':>5s}  {'Apparatus':<22s}  {'n':>3s}  {'Mode B mean':>12s}  {'Mode B median':>14s}")
print("-"*65)
tier_data = defaultdict(list)
for r in results:
    tier_data[r['tier']].append(r['mode_b_frac'])

for tier in (4, 3, 2, 1):
    vals = tier_data.get(tier, [])
    if not vals:
        print(f"  {tier}    {TIER_NAMES[tier]:<22s}  {0:>3d}  --    --")
        continue
    mean_v = sum(vals) / len(vals)
    median_v = sorted(vals)[len(vals)//2]
    print(f"  {tier}    {TIER_NAMES[tier]:<22s}  {len(vals):>3d}  "
          f"{mean_v:>12.3f}  {median_v:>14.3f}")

# Spearman correlation
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

tiers = [r['tier'] for r in results]
mode_b = [r['mode_b_frac'] for r in results]
rho = spearman_rho(tiers, mode_b)
print(f"\nSpearman rho (tier vs Mode B fraction): {rho:+.4f}")

# Permutation null
rng = random.Random(42)
n_perm = 10000
null_rhos = []
for _ in range(n_perm):
    s = list(mode_b)
    rng.shuffle(s)
    null_rhos.append(spearman_rho(tiers, s))
null_rhos.sort()
n_above = sum(1 for r in null_rhos if not math.isnan(r) and r >= rho)
p_value = n_above / n_perm
print(f"Permutation null (n={n_perm}):")
print(f"  Mean: {sum(null_rhos)/n_perm:+.4f}")
print(f"  95th percentile: {null_rhos[int(n_perm*0.95)]:+.4f}")
print(f"  99th percentile: {null_rhos[int(n_perm*0.99)]:+.4f}")
print(f"  p-value (one-sided): {p_value:.4f}")

# Within-section restriction
print()
print("="*72)
print("WITHIN-SECTION CONTROL")
print("="*72)
print()
section_results = defaultdict(list)
for r in results:
    section_results[r['section']].append(r)

for sec in sorted(section_results.keys()):
    sub = section_results[sec]
    if len(sub) < 8:
        continue
    ts = [r['tier'] for r in sub]
    mb = [r['mode_b_frac'] for r in sub]
    if len(set(ts)) < 2:
        continue  # no tier variation
    sub_rho = spearman_rho(ts, mb)
    sub_nulls = []
    for _ in range(2000):
        s = list(mb)
        rng.shuffle(s)
        sub_nulls.append(spearman_rho(ts, s))
    sub_p = sum(1 for r in sub_nulls if not math.isnan(r) and r >= sub_rho) / 2000
    print(f"  Section {sec}: n={len(sub):3d}  rho={sub_rho:+.4f}  p={sub_p:.4f}")

# Direct comparison: balneum (Tier 3) vs direct fire (Tier 1)
print()
print("="*72)
print("DIRECT BALNEUM vs DIRECT-FIRE COMPARISON")
print("="*72)
balneum = tier_data.get(3, [])
fire = tier_data.get(1, [])
if balneum and fire:
    print(f"Balneum (Tier 3): n={len(balneum)}, Mode B fraction = {sum(balneum)/len(balneum):.3f}")
    print(f"Direct fire (Tier 1): n={len(fire)}, Mode B fraction = {sum(fire)/len(fire):.3f}")
    diff = sum(balneum)/len(balneum) - sum(fire)/len(fire)
    print(f"Difference: {diff:+.3f}")
    # Permutation test on the difference
    combined = balneum + fire
    n_b = len(balneum)
    null_diffs = []
    rng2 = random.Random(7)
    for _ in range(10000):
        c = list(combined)
        rng2.shuffle(c)
        nb = c[:n_b]; nf = c[n_b:]
        null_diffs.append(sum(nb)/len(nb) - sum(nf)/len(nf))
    n_above = sum(1 for d in null_diffs if d >= diff)
    p_two = (sum(1 for d in null_diffs if abs(d) >= abs(diff))) / 10000
    print(f"Permutation p (one-sided, balneum > fire): {n_above/10000:.4f}")
    print(f"Permutation p (two-sided, |diff|): {p_two:.4f}")

# Save
out = {
    'n_paragraphs': len(results),
    'tier_means': {tier: sum(v)/len(v) for tier, v in tier_data.items() if v},
    'tier_counts': {tier: len(v) for tier, v in tier_data.items()},
    'spearman_rho': rho,
    'p_value': p_value,
    'within_section': {
        sec: {'n': len(sub),
              'rho': spearman_rho([r['tier'] for r in sub], [r['mode_b_frac'] for r in sub])}
        for sec, sub in section_results.items() if len(sub) >= 8
    },
}
with open('phases/PHASE_649_O_PREFIX_VALIDATION/results/mode_b_thermal_full.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)
print()
print("Saved: phases/PHASE_649_O_PREFIX_VALIDATION/results/mode_b_thermal_full.json")
