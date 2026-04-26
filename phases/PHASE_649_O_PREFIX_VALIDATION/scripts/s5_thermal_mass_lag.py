"""
Phase 649 Step 5: Thermal-mass lag test.

Hypothesis: the qo->ok paragraph-level ordering at 73% encodes thermal-mass-
mediated control lag. If true, recipes using high-thermal-mass apparatus
(balneum mariae, putrefaction chambers) should have LARGER token-distance
between first-qo and first-ok than recipes using low-thermal-mass apparatus
(direct fire, calcination).

Method:
1. For each matched folio, get the SISMEL Catalan recipe text
2. Auto-classify thermal regime by keyword:
   - PUTREFACTION (Tier 4, longest lag): podri*, putrefa*, fermentar
   - BALNEUM (Tier 3, long lag):         bany, balne, marie
   - ASHES/SAND (Tier 2, medium lag):    cendr, cineri, arena
   - DIRECT FIRE (Tier 1, short lag):    foch (without bath context), calcin*, sublim*
3. For each paragraph in a matched folio, compute token-distance between
   first qo-token and first ok-token (in tokens; tokens without both = null)
4. Test rank correlation: vessel-thermal-tier vs qo->ok distance
5. Permutation null

Falsification:
- If correlation is null or negative, qo->ok ordering is procedural convention,
  not physically grounded
- If correlation is positive (rho > 0 with reasonable p), the encoding
  reflects thermal-mass lag — physics-grounded validation
"""
import sys
import json
import math
import random
sys.path.insert(0, '.')
from scripts.voynich import Transcript
from collections import defaultdict, Counter

tx = Transcript()

# Load matched recipes + corpus
with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as f:
    matches = json.load(f)
with open('phases/SISMEL_RECIPE_CORPUS/results/sismel_corpus.json', encoding='utf-8') as fp:
    corpus = json.load(fp)

def get_chapter(part, num):
    for ch in corpus['parts'][part]['chapters']:
        if ch['chapter_num'] == num:
            return ch
    return None

# Keyword tiers (case-insensitive, prefix match)
TIER_KEYWORDS = {
    4: ['podri', 'putrefa', 'fermentar', 'fermenta'],   # very long lag (hours-days)
    3: ['bany', 'balne', 'marie', 'mari'],               # balneum (long)
    2: ['cendr', 'cineri', 'arena'],                     # sand/ashes (medium)
    1: ['foch', 'fuoco', 'igne', 'ignis', 'calcin', 'sublim'],  # direct fire (short)
}

def classify_text_tier(text):
    """Return highest tier whose keywords appear; 0 if none."""
    text_l = text.lower()
    for tier in (4, 3, 2, 1):
        for kw in TIER_KEYWORDS[tier]:
            if kw in text_l:
                return tier
    return 0

# Per matched folio, classify each paragraph's recipe-text tier
folio_par_tier = {}  # (folio, par_idx_within_folio) -> tier
for m in matches:
    f = m['folio']
    ch = get_chapter(m['part'], m['chapter_num'])
    if not ch: continue
    paragraphs_text = ch.get('paragraphs', [])
    # Only one chapter per folio in matches; the recipe paragraphs are the chapter paragraphs
    # We treat recipe paragraphs as ordered, and assume they map 1:1 to folio paragraphs
    # by layout-order (per C1959 finding)
    for p_idx, p in enumerate(paragraphs_text):
        text = (p.get('catalan') or '') + ' ' + (p.get('latin') or '')
        tier = classify_text_tier(text)
        folio_par_tier[(f, p_idx)] = tier

# Walk Currier B tokens, group by paragraph
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

# For each MATCHED-folio paragraph, compute qo->ok token-distance
results = []  # list of (tier, distance, folio, par_idx)
for (f, par_idx), toks in paragraphs.items():
    if (f, par_idx) not in folio_par_tier:
        continue  # not a matched folio paragraph
    tier = folio_par_tier[(f, par_idx)]
    if tier == 0:
        continue  # untagged
    # Find first qo and first ok token positions
    first_qo = None
    first_ok = None
    for i, t in enumerate(toks):
        p = prefix_of(t.word)
        if p == 'qo' and first_qo is None:
            first_qo = i
        elif p == 'ok' and first_ok is None:
            first_ok = i
    if first_qo is None or first_ok is None:
        continue  # need both
    # Distance: ok-first minus qo-first (positive = qo before ok)
    distance = first_ok - first_qo
    results.append({
        'folio': f, 'par_idx': par_idx, 'tier': tier,
        'distance': distance, 'first_qo': first_qo, 'first_ok': first_ok,
        'par_len': len(toks),
    })

print("="*72)
print("THERMAL-MASS LAG TEST")
print("="*72)
print(f"\nMatched-folio paragraphs with both qo and ok: {len(results)}")

# Distribution by tier
print()
print(f"{'Tier':>5s}  {'Apparatus':<25s}  {'n':>3s}  {'mean dist':>10s}  {'median':>7s}")
print("-"*65)
TIER_NAMES = {
    4: 'Putrefaction (longest)',
    3: 'Balneum mariae',
    2: 'Ashes / sand',
    1: 'Direct fire (shortest)',
}
tier_dists = defaultdict(list)
for r in results:
    tier_dists[r['tier']].append(r['distance'])

for tier in sorted(TIER_NAMES.keys(), reverse=True):
    dists = tier_dists.get(tier, [])
    if not dists:
        print(f"  {tier}    {TIER_NAMES[tier]:<25s}  {0:>3d}  {'--':>10s}  {'--':>7s}")
        continue
    mean_d = sum(dists) / len(dists)
    dists_sorted = sorted(dists)
    median_d = dists_sorted[len(dists_sorted)//2]
    print(f"  {tier}    {TIER_NAMES[tier]:<25s}  {len(dists):>3d}  {mean_d:>+10.2f}  {median_d:>+7d}")

# Rank correlation: tier vs distance
def spearman_rho(x, y):
    n = len(x)
    if n < 3: return float('nan')
    # Rank
    def rank(arr):
        s = sorted(range(len(arr)), key=lambda i: arr[i])
        r = [0] * len(arr)
        for ri, idx in enumerate(s):
            r[idx] = ri + 1
        # Fix ties (average rank)
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
    rx = rank(x)
    ry = rank(y)
    n = len(x)
    mx = sum(rx)/n; my = sum(ry)/n
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    dx = math.sqrt(sum((r-mx)**2 for r in rx))
    dy = math.sqrt(sum((r-my)**2 for r in ry))
    if dx*dy == 0: return float('nan')
    return num/(dx*dy)

tiers = [r['tier'] for r in results]
dists = [r['distance'] for r in results]
rho = spearman_rho(tiers, dists)
print()
print(f"Spearman rank correlation (tier vs qo-ok distance): rho = {rho:+.4f}")

# Permutation null
rng = random.Random(42)
n_perm = 10000
null_rhos = []
for _ in range(n_perm):
    shuffled = list(dists)
    rng.shuffle(shuffled)
    null_rhos.append(spearman_rho(tiers, shuffled))
null_rhos.sort()
n_above = sum(1 for r in null_rhos if r >= rho)
p_value = n_above / n_perm
print(f"Permutation null (n={n_perm}):")
print(f"  Mean null rho: {sum(null_rhos)/n_perm:+.4f}")
print(f"  95th percentile: {null_rhos[int(n_perm*0.95)]:+.4f}")
print(f"  99th percentile: {null_rhos[int(n_perm*0.99)]:+.4f}")
print(f"  p-value (one-sided): {p_value:.4f}")
print()

# Verdict
print("="*72)
print("VERDICT")
print("="*72)
if rho > 0.3 and p_value < 0.05:
    print("STRONG positive correlation. Vessel thermal-mass tier predicts")
    print("qo->ok token-distance. Architecture encodes physical thermal lag.")
    print("This is direct empirical evidence of physics-grounded operational")
    print("encoding.")
elif rho > 0.15 and p_value < 0.10:
    print("Moderate positive correlation. Directional support for thermal-")
    print("mass-mediated encoding; effect is real but small. Requires larger")
    print("sample or more refined classification to lock in.")
elif rho > 0:
    print("Weak positive correlation; no significance. Encoding may track")
    print("thermal mass but signal is below detection threshold at this N.")
else:
    print("No correlation or negative. qo->ok ordering is procedural")
    print("convention, not thermal-mass-mediated. Physics-grounding hypothesis")
    print("not supported by this test.")

# Save
out = {
    'matched_folios_with_both_qo_ok': len(results),
    'tier_distribution': {tier: len(d) for tier, d in tier_dists.items()},
    'tier_means': {tier: sum(d)/len(d) for tier, d in tier_dists.items() if d},
    'spearman_rho': rho,
    'p_value': p_value,
    'n_perm': n_perm,
    'mean_null_rho': sum(null_rhos)/n_perm,
    'per_paragraph_results': results,
}
with open('phases/PHASE_649_O_PREFIX_VALIDATION/results/thermal_mass_lag.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)
print()
print("Saved: phases/PHASE_649_O_PREFIX_VALIDATION/results/thermal_mass_lag.json")
