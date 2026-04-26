"""
Phase 649 Step 6: Multi-granularity thermal-mass lag test.

Token-distance came back null (Step 5). The user's empirical observation:
in real distillation, you adjust the fire and then DON'T check for tens of
minutes. The lag isn't encoded as filler tokens between qo and ok — it's
encoded as line gaps, iteration markers, or cross-paragraph delays.

Test four metrics for each matched-folio paragraph with both qo and ok:

1. TOKEN-DISTANCE   (re-run from Step 5 for comparison)
2. LINE-DISTANCE    (number of lines between first-qo and first-ok)
3. ITERATION-DENSITY between qo and ok (count of daiin/aiin/ain/iin)
4. MODE-B FRACTION  (fraction of intervening lines that are Mode B / bare-heavy)

If thermal-mass is encoded, balneum recipes should show LARGER values on
the granularity that captures it. Token-distance failed (Step 5 null).
Line-distance, iteration-density, or Mode-B fraction may carry the signal.

Also test: cross-paragraph lag (qo in paragraph N, ok appears in N+1 or
later within the same folio).
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

with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as f:
    matches = json.load(f)
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

# Per matched folio paragraph -> tier
folio_par_tier = {}
for m in matches:
    f = m['folio']
    ch = get_chapter(m['part'], m['chapter_num'])
    if not ch: continue
    for p_idx, p in enumerate(ch.get('paragraphs', [])):
        text = (p.get('catalan') or '') + ' ' + (p.get('latin') or '')
        folio_par_tier[(f, p_idx)] = classify_text_tier(text)

# Build paragraph token-streams
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

ITERATION_MIDDLES = {'iin', 'ain', 'aiin'}
def is_iteration_token(t):
    """Check if token has iin/ain/aiin in middle, or is 'daiin'."""
    w = t.word
    if w == 'daiin' or w == 'daiiin': return True
    m = morph.extract(w)
    if m.middle in ITERATION_MIDDLES: return True
    return False

# Mode B classifier (per Step 3)
TERMINAL_SUFFIXES = {'dy','edy','eedy','y','ey','ody','eody'}
def line_is_mode_b(toks_in_line):
    n_term = sum(1 for t in toks_in_line if morph.extract(t.word).suffix in TERMINAL_SUFFIXES)
    return (n_term / max(len(toks_in_line), 1)) < 0.30

# For each matched-folio paragraph, compute all four metrics
results = []
for (f, par_idx), toks in paragraphs.items():
    if (f, par_idx) not in folio_par_tier: continue
    tier = folio_par_tier[(f, par_idx)]
    if tier == 0: continue
    first_qo = first_ok = None
    for i, t in enumerate(toks):
        p = prefix_of(t.word)
        if p == 'qo' and first_qo is None: first_qo = i
        elif p == 'ok' and first_ok is None: first_ok = i
    if first_qo is None or first_ok is None: continue
    if first_ok <= first_qo: continue  # only forward direction

    # Token distance
    tok_dist = first_ok - first_qo

    # Line distance
    line_qo = toks[first_qo].line
    line_ok = toks[first_ok].line
    # Convert to ordinal: number of distinct lines between
    lines_seen = []
    for j in range(first_qo, first_ok + 1):
        ln = toks[j].line
        if not lines_seen or lines_seen[-1] != ln:
            lines_seen.append(ln)
    line_dist = len(lines_seen) - 1  # 0 if same line

    # Iteration density between qo and ok (exclusive)
    n_between = first_ok - first_qo - 1
    n_iter = sum(1 for j in range(first_qo+1, first_ok) if is_iteration_token(toks[j]))
    iter_density = n_iter / max(n_between, 1)

    # Mode-B fraction of intervening lines
    inter_lines = defaultdict(list)
    for j in range(first_qo+1, first_ok):
        inter_lines[toks[j].line].append(toks[j])
    if inter_lines:
        n_mode_b = sum(1 for line_toks in inter_lines.values()
                       if line_is_mode_b(line_toks))
        mode_b_frac = n_mode_b / len(inter_lines)
    else:
        mode_b_frac = float('nan')

    results.append({
        'folio': f, 'par_idx': par_idx, 'tier': tier,
        'tok_dist': tok_dist, 'line_dist': line_dist,
        'iter_density': iter_density, 'mode_b_frac': mode_b_frac,
        'n_between': n_between, 'n_iter': n_iter,
    })

print("="*72)
print("MULTI-GRANULARITY THERMAL-MASS LAG TEST")
print("="*72)
print(f"\nMatched-folio paragraphs with qo before ok: {len(results)}")

# Bin by tier
print()
print(f"{'Tier':>5s}  {'Apparatus':<22s}  {'n':>3s}  "
      f"{'tok_d':>7s}  {'line_d':>7s}  {'iter_dens':>10s}  {'mode_b':>8s}")
print("-"*78)
tier_metrics = defaultdict(lambda: {'tok': [], 'line': [], 'iter': [], 'mode_b': []})
for r in results:
    tier_metrics[r['tier']]['tok'].append(r['tok_dist'])
    tier_metrics[r['tier']]['line'].append(r['line_dist'])
    tier_metrics[r['tier']]['iter'].append(r['iter_density'])
    if not math.isnan(r['mode_b_frac']):
        tier_metrics[r['tier']]['mode_b'].append(r['mode_b_frac'])

def m(arr): return (sum(arr)/len(arr)) if arr else float('nan')

for tier in (4, 3, 2, 1):
    tm = tier_metrics[tier]
    n = len(tm['tok'])
    if n == 0:
        print(f"  {tier}    {TIER_NAMES[tier]:<22s}  {0:>3d}  --    --    --    --")
        continue
    print(f"  {tier}    {TIER_NAMES[tier]:<22s}  {n:>3d}  "
          f"{m(tm['tok']):>7.2f}  {m(tm['line']):>7.2f}  "
          f"{m(tm['iter']):>10.3f}  {m(tm['mode_b']):>8.3f}")

# Spearman per metric
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

def perm_p(tiers, vals, real_rho, n_perm=10000):
    rng = random.Random(42)
    nulls = []
    for _ in range(n_perm):
        s = list(vals)
        rng.shuffle(s)
        nulls.append(spearman_rho(tiers, s))
    n_above = sum(1 for r in nulls if not math.isnan(r) and r >= real_rho)
    return n_above / n_perm

tiers_arr = [r['tier'] for r in results]
print()
print("Rank correlation tier vs each metric (positive = balneum has more):")
for metric_name in ('tok_dist', 'line_dist', 'iter_density', 'mode_b_frac'):
    if metric_name == 'mode_b_frac':
        valid = [(r['tier'], r[metric_name]) for r in results
                 if not math.isnan(r[metric_name])]
        if not valid:
            continue
        ts, vs = zip(*valid)
        ts = list(ts); vs = list(vs)
    else:
        ts = tiers_arr; vs = [r[metric_name] for r in results]
    rho = spearman_rho(ts, vs)
    p = perm_p(ts, vs, rho)
    print(f"  {metric_name:>15s}: rho = {rho:+.4f}  p = {p:.4f}  n = {len(vs)}")

# Cross-paragraph lag test
print()
print("="*72)
print("CROSS-PARAGRAPH LAG TEST")
print("="*72)
print("For each matched paragraph with qo but NO ok, find the next paragraph")
print("(same folio) and check whether ok appears there. Count paragraph-gap.")
print()

# Build index of (folio -> sorted par_idx list)
folio_paragraphs = defaultdict(list)
for (f, par_idx) in paragraphs:
    folio_paragraphs[f].append(par_idx)
for f in folio_paragraphs:
    folio_paragraphs[f].sort()

cross_results = []
for (f, par_idx) in paragraphs:
    if (f, par_idx) not in folio_par_tier: continue
    tier = folio_par_tier[(f, par_idx)]
    if tier == 0: continue
    toks = paragraphs[(f, par_idx)]
    has_qo = any(prefix_of(t.word) == 'qo' for t in toks)
    has_ok = any(prefix_of(t.word) == 'ok' for t in toks)
    if not has_qo or has_ok: continue  # only paragraphs with qo and NO ok
    # Look forward for ok
    par_list = folio_paragraphs[f]
    if par_idx not in par_list: continue
    idx_in_list = par_list.index(par_idx)
    for offset in range(1, 5):  # check next 4 paragraphs
        if idx_in_list + offset >= len(par_list): break
        next_par_idx = par_list[idx_in_list + offset]
        next_toks = paragraphs[(f, next_par_idx)]
        if any(prefix_of(t.word) == 'ok' for t in next_toks):
            cross_results.append({'folio': f, 'par_idx': par_idx, 'tier': tier,
                                  'paragraph_gap': offset})
            break

print(f"Paragraphs with qo, no ok within paragraph: {len(cross_results)}")
if cross_results:
    print(f"\n{'Tier':>5s}  {'Apparatus':<22s}  {'n':>3s}  {'mean par-gap':>14s}")
    print("-"*55)
    cross_tier = defaultdict(list)
    for r in cross_results:
        cross_tier[r['tier']].append(r['paragraph_gap'])
    for tier in (4, 3, 2, 1):
        if cross_tier[tier]:
            mg = sum(cross_tier[tier])/len(cross_tier[tier])
            print(f"  {tier}    {TIER_NAMES[tier]:<22s}  {len(cross_tier[tier]):>3d}  {mg:>14.2f}")

    # Combined test: total qo->ok distance accounting for cross-paragraph
    if len(cross_results) >= 5:
        ts2 = [r['tier'] for r in cross_results]
        gs = [r['paragraph_gap'] for r in cross_results]
        rho2 = spearman_rho(ts2, gs)
        p2 = perm_p(ts2, gs, rho2)
        print(f"\nCross-paragraph rho (tier vs paragraph-gap): {rho2:+.4f}  p={p2:.4f}")

# Save
out = {
    'within_paragraph': {
        'n': len(results),
        'tier_means': {tier: {k: m(v) for k, v in tier_metrics[tier].items()}
                       for tier in tier_metrics},
        'correlations': {
            metric_name: spearman_rho(tiers_arr,
                                      [r[metric_name] for r in results
                                       if not (metric_name == 'mode_b_frac' and math.isnan(r[metric_name]))])
            for metric_name in ('tok_dist', 'line_dist', 'iter_density')
        },
    },
    'cross_paragraph': {
        'n': len(cross_results),
        'tier_means': {tier: sum(cross_tier[tier])/len(cross_tier[tier])
                       for tier in cross_tier if cross_tier[tier]} if cross_results else {},
    },
}
with open('phases/PHASE_649_O_PREFIX_VALIDATION/results/thermal_mass_multigrain.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)
