"""
HT-density partial-correlation test.

Three competing readings of HT (per project history):
1. Fluency practice (early Tier 4): HT consolidates uncommon character combos
2. Attention scaffolding (early Tier 4): HT keeps operator alert during long monitoring
3. Compound specification (current Tier 2 via C935): HT carries condensed specs

Test: per-folio partial correlations of HT density with three predictors.
- Compound complexity: distinct compounds operated on (proxy: distinct o-prefix count)
- Procedure-duration tier: vessel thermal-tier (balneum/sand/direct fire)
- Character-combination rarity: mean MIDDLE rarity of HT tokens

Multiple correlations could coexist if HT serves multiple functions.

Method:
- HT operationalization: Currier B tokens with COMPOUND MIDDLE per MiddleAnalyzer
  (compound = MIDDLE not in core/simple inventory; per HTSC C740 / C935)
- Per-folio metrics: HT_rate, compound_complexity, vessel_tier (matched only),
  char_combo_rarity
- Spearman correlations + partial correlations
"""
import sys
import json
import re
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

# Per-folio metrics
folio_total = defaultdict(int)
folio_ht = defaultdict(int)
folio_o_prefixes = defaultdict(set)  # distinct o-prefix tokens
folio_middle_freq_total = defaultdict(int)
folio_middle_rarity_sum = defaultdict(float)
folio_ht_middle_rarity_sum = defaultdict(float)
folio_ht_count_for_rarity = defaultdict(int)

# Build corpus-wide MIDDLE frequency for rarity computation
middle_corpus_freq = Counter()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m.middle:
        middle_corpus_freq[m.middle] += 1
total_middles = sum(middle_corpus_freq.values())

# For each token in Currier B
for t in tx.currier_b():
    f = t.folio
    folio_total[f] += 1
    m = morph.extract(t.word)

    # HT classification: compound MIDDLE
    is_ht = False
    if m.middle and len(m.middle) >= 2:
        try:
            is_ht = mid_analyzer.is_compound(m.middle)
        except Exception:
            is_ht = False
    if is_ht:
        folio_ht[f] += 1

    # o-prefix distinct counter (compound complexity proxy)
    w = t.word
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        folio_o_prefixes[f].add('o' + w[1])
    if w.startswith('qo'):
        folio_o_prefixes[f].add('qo')

    # MIDDLE rarity (lower frequency = more rare)
    if m.middle and m.middle in middle_corpus_freq:
        rarity = 1 - (middle_corpus_freq[m.middle] / total_middles)
        # Use log-rarity for numerical stability
        log_rarity = -math.log(middle_corpus_freq[m.middle] / total_middles)
        folio_middle_rarity_sum[f] += log_rarity
        folio_middle_freq_total[f] += 1
        if is_ht:
            folio_ht_middle_rarity_sum[f] += log_rarity
            folio_ht_count_for_rarity[f] += 1

# Vessel-thermal-tier from matched recipes (Phase 649 logic)
TIER_KEYWORDS = {
    4: ['podri', 'putrefa', 'fermenta'],
    3: ['bany', 'balne', 'mari'],
    2: ['cendr', 'cineri', 'arena'],
    1: ['foch', 'igne', 'calcin', 'sublim'],
}
def classify_text_tier(text):
    text_l = text.lower()
    for tier in (4, 3, 2, 1):
        for kw in TIER_KEYWORDS[tier]:
            if kw in text_l:
                return tier
    return 0

with open('phases/SISMEL_RECIPE_CORPUS/results/matched_recipes_status.json') as fp:
    matches = json.load(fp)
with open('phases/SISMEL_RECIPE_CORPUS/results/sismel_corpus.json', encoding='utf-8') as fp:
    corpus = json.load(fp)

def get_chapter(part, num):
    for ch in corpus['parts'][part]['chapters']:
        if ch['chapter_num'] == num:
            return ch
    return None

folio_vessel_tier = {}
for m in matches:
    f = m['folio']
    ch = get_chapter(m['part'], m['chapter_num'])
    if not ch: continue
    text = ' '.join((p.get('catalan') or '') + ' ' + (p.get('latin') or '')
                    for p in ch.get('paragraphs', []))
    tier = classify_text_tier(text)
    if tier > 0:
        folio_vessel_tier[f] = tier

# Compute per-folio metrics
folio_metrics = {}
for f in folio_total:
    if folio_total[f] < 30:
        continue
    ht_rate = folio_ht[f] / folio_total[f]
    compound_complexity = len(folio_o_prefixes[f])
    char_rarity = (folio_ht_middle_rarity_sum[f] / folio_ht_count_for_rarity[f]
                   if folio_ht_count_for_rarity[f] > 0 else float('nan'))
    body_rarity = ((folio_middle_rarity_sum[f] - folio_ht_middle_rarity_sum[f]) /
                   max(folio_middle_freq_total[f] - folio_ht_count_for_rarity[f], 1))
    rarity_diff = char_rarity - body_rarity if not math.isnan(char_rarity) else 0
    folio_metrics[f] = {
        'ht_rate': ht_rate,
        'total_tokens': folio_total[f],
        'compound_complexity': compound_complexity,
        'vessel_tier': folio_vessel_tier.get(f, None),
        'char_rarity_diff': rarity_diff,  # HT MIDDLE rarity minus body MIDDLE rarity
    }

print("="*78)
print("HT-DENSITY THREE-WAY TEST")
print("="*78)
print()
print(f"Folios with sufficient data: {len(folio_metrics)}")

# Spearman correlations
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

# Test 1: HT vs compound complexity (across all folios)
all_folios = list(folio_metrics.keys())
ht_rates = [folio_metrics[f]['ht_rate'] for f in all_folios]
complexities = [folio_metrics[f]['compound_complexity'] for f in all_folios]
char_rarities = [folio_metrics[f]['char_rarity_diff'] for f in all_folios]

rho_complexity = spearman_rho(ht_rates, complexities)
rho_rarity = spearman_rho(ht_rates, char_rarities)

print()
print(f"{'Predictor':<30s}  {'rho':>7s}  {'n':>4s}  Reading")
print("-"*68)
print(f"  {'compound_complexity':<28s}  {rho_complexity:>+7.3f}  {len(all_folios):>4d}  specification (#3, current)")
print(f"  {'char_rarity_diff (HT-body)':<28s}  {rho_rarity:>+7.3f}  {len(all_folios):>4d}  fluency_practice (#1)")

# Vessel-tier correlation only on matched folios
matched = [(f, folio_metrics[f]) for f in all_folios
           if folio_metrics[f]['vessel_tier'] is not None]
if len(matched) >= 5:
    ms_ht = [d['ht_rate'] for _, d in matched]
    ms_tier = [d['vessel_tier'] for _, d in matched]
    rho_tier = spearman_rho(ms_ht, ms_tier)
    print(f"  {'vessel_tier (matched only)':<28s}  {rho_tier:>+7.3f}  {len(matched):>4d}  attention_scaffolding (#2)")

# Top folios by each metric
print()
print("="*78)
print("Top 8 folios by HT rate:")
print("="*78)
sorted_by_ht = sorted(all_folios, key=lambda f: -folio_metrics[f]['ht_rate'])
print(f"{'Folio':>8s}  {'HT%':>5s}  {'tokens':>7s}  {'complexity':>11s}  {'tier':>5s}")
for f in sorted_by_ht[:8]:
    d = folio_metrics[f]
    tier_str = str(d['vessel_tier']) if d['vessel_tier'] else '-'
    print(f"  {f:>6s}  {d['ht_rate']*100:>5.1f}%  {d['total_tokens']:>7d}  {d['compound_complexity']:>11d}  {tier_str:>5s}")

# Bottom 8 folios by HT rate
print()
print("Bottom 8 folios by HT rate:")
print(f"{'Folio':>8s}  {'HT%':>5s}  {'tokens':>7s}  {'complexity':>11s}  {'tier':>5s}")
for f in sorted_by_ht[-8:]:
    d = folio_metrics[f]
    tier_str = str(d['vessel_tier']) if d['vessel_tier'] else '-'
    print(f"  {f:>6s}  {d['ht_rate']*100:>5.1f}%  {d['total_tokens']:>7d}  {d['compound_complexity']:>11d}  {tier_str:>5s}")

# Section-stratified
print()
print("="*78)
print("HT rate by section:")
print("="*78)
section_ht = defaultdict(list)
for f, d in folio_metrics.items():
    # Get section from any token of folio
    sec = next((t.section for t in tx.currier_b() if t.folio == f), '?')
    section_ht[sec].append(d['ht_rate'])
for sec in sorted(section_ht.keys()):
    rates = section_ht[sec]
    if rates:
        mean_rate = sum(rates) / len(rates)
        print(f"  Section {sec}: n={len(rates)}, mean HT rate = {mean_rate*100:.1f}%")

# Save
import os
os.makedirs('scratch', exist_ok=True)
with open('scratch/ht_density_test.json', 'w') as f:
    json.dump({
        'correlations': {
            'compound_complexity': rho_complexity,
            'char_rarity_diff': rho_rarity,
            'vessel_tier': rho_tier if len(matched) >= 5 else None,
        },
        'folio_metrics': folio_metrics,
    }, f, indent=2, default=str)
print()
print("Saved: scratch/ht_density_test.json")
