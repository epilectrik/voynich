"""Test 01: Section B complement analysis + all section-specific prefix deep-dives.

C930 showed lk is 81.7% in section S (fire-method monitoring).
Question: What is the balneum mariae equivalent in section B?
Candidate: ol (1.53x enriched in B, 45.3% of ol tokens).

Method: For each section-concentrated prefix, compute:
1. Section distribution
2. MIDDLE selectivity (enrichment/depletion vs baseline)
3. Positional behavior (line-initial/mid/final)
4. Co-occurrence with other prefixes
5. Compare MIDDLE profiles to identify functional clusters
"""
import sys
from pathlib import Path
from collections import Counter, defaultdict
import json
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology
from scipy.stats import spearmanr

morph = Morphology()
tx = Transcript()

# Load decoder maps
maps = json.load(open('data/decoder_maps.json', 'r', encoding='utf-8'))
def get_map(name):
    raw = maps.get(name, {})
    if 'entries' in raw:
        return {k: v.get('value', v) for k, v in raw['entries'].items()}
    return {k: v for k, v in raw.items() if isinstance(v, str)}

prefix_actions = get_map('prefix_actions')

# Collect all B tokens
all_tokens = []
for tok in tx.currier_b():
    w = tok.word
    if not w.strip() or '*' in w:
        continue
    m = morph.extract(w)
    all_tokens.append({
        'word': w, 'morph': m, 'folio': tok.folio, 'line': tok.line,
        'section': tok.section, 'line_initial': tok.line_initial,
        'line_final': tok.line_final, 'par_initial': tok.par_initial,
    })

# Build line groupings
lines = defaultdict(list)
for tok in all_tokens:
    lines[(tok['folio'], tok['line'])].append(tok)

# Global prefix statistics
pfx_total = Counter()
pfx_section = defaultdict(Counter)
pfx_mid = defaultdict(Counter)
pfx_position = defaultdict(Counter)  # INIT/MID/FINAL
mid_by_pfx_total = Counter()

for tok in all_tokens:
    m = tok['morph']
    if not m.prefix:
        continue
    pfx_total[m.prefix] += 1
    pfx_section[m.prefix][tok['section']] += 1
    if m.middle:
        pfx_mid[m.prefix][m.middle] += 1
        mid_by_pfx_total[m.middle] += 1

    if tok['line_initial']:
        pfx_position[m.prefix]['INIT'] += 1
    elif tok['line_final']:
        pfx_position[m.prefix]['FINAL'] += 1
    else:
        pfx_position[m.prefix]['MID'] += 1

section_total = Counter()
for tok in all_tokens:
    if tok['morph'].prefix:
        section_total[tok['section']] += 1

all_pfx_total = sum(pfx_total.values())
sections = sorted(section_total.keys())

# =============================================
# TARGET PREFIXES: all with significant section bias
# =============================================
target_prefixes = ['ol', 'lk', 'da', 'sh', 'qo', 'ch', 'ok', 'ot', 'sa', 'te', 'ke', 'pch', 'lch', 'tch']

print("=" * 80)
print("TEST 01: SECTION-SPECIFIC PREFIX PROFILES")
print("=" * 80)

results = {}

for pfx in target_prefixes:
    total = pfx_total.get(pfx, 0)
    if total < 20:
        continue

    print(f"\n{'='*70}")
    print(f"PREFIX: {pfx}  (n={total}, action={prefix_actions.get(pfx, '?')})")
    print(f"{'='*70}")

    pfx_share = total / all_pfx_total

    # Section distribution
    print(f"\n  SECTION DISTRIBUTION:")
    sec_enrichments = {}
    peak_sec = None
    peak_enrich = 0
    for sec in sections:
        c = pfx_section[pfx].get(sec, 0)
        share = c / total if total > 0 else 0
        expected = section_total[sec] / all_pfx_total if all_pfx_total > 0 else 0
        enrich = share / expected if expected > 0 else 0
        sec_enrichments[sec] = enrich
        marker = " ***" if enrich > 1.5 else " *" if enrich > 1.2 else " ." if enrich < 0.5 else ""
        print(f"    {sec:<6} {c:>5} ({share:.1%})  expected={expected:.1%}  enrichment={enrich:.2f}x{marker}")
        if enrich > peak_enrich:
            peak_enrich = enrich
            peak_sec = sec

    # Positional
    init_c = pfx_position[pfx].get('INIT', 0)
    mid_c = pfx_position[pfx].get('MID', 0)
    final_c = pfx_position[pfx].get('FINAL', 0)
    init_rate = init_c / total if total > 0 else 0
    final_rate = final_c / total if total > 0 else 0
    init_final_ratio = init_rate / final_rate if final_rate > 0 else 999

    print(f"\n  POSITIONAL:")
    print(f"    LINE_INIT:  {init_c:>5} ({init_rate:.1%})")
    print(f"    LINE_MID:   {mid_c:>5} ({mid_c/total:.1%})")
    print(f"    LINE_FINAL: {final_c:>5} ({final_rate:.1%})")
    print(f"    init/final ratio: {init_final_ratio:.2f}x")

    # MIDDLE selectivity - top enriched and top depleted
    pfx_mid_total = sum(pfx_mid[pfx].values())
    mid_enriched = []
    mid_depleted = []

    for mid, mid_total in mid_by_pfx_total.most_common():
        if mid_total < 30:
            continue
        pfx_mid_c = pfx_mid[pfx].get(mid, 0)
        actual_share = pfx_mid_c / mid_total if mid_total > 0 else 0
        ratio = actual_share / pfx_share if pfx_share > 0 else 0
        if ratio > 2.0 and pfx_mid_c >= 3:
            mid_enriched.append((mid, pfx_mid_c, mid_total, ratio))
        if mid_total >= 100 and ratio < 0.3:
            mid_depleted.append((mid, pfx_mid_c, mid_total, ratio))

    mid_enriched.sort(key=lambda x: -x[3])
    mid_depleted.sort(key=lambda x: x[3])

    print(f"\n  MIDDLE SELECTIVITY (enriched >2x):")
    for mid, c, mt, ratio in mid_enriched[:8]:
        print(f"    {mid:<12} {c:>3}/{mt:>5}  {ratio:.1f}x enriched")

    print(f"  MIDDLE AVOIDANCE (depleted, common MIDDLEs):")
    for mid, c, mt, ratio in mid_depleted[:5]:
        print(f"    {mid:<12} {c:>3}/{mt:>5}  {ratio:.1f}x ({('ZERO' if c==0 else 'low')})")

    results[pfx] = {
        'total': total,
        'action': prefix_actions.get(pfx, '?'),
        'peak_section': peak_sec,
        'peak_enrichment': round(peak_enrich, 2),
        'section_enrichments': {s: round(v, 2) for s, v in sec_enrichments.items()},
        'init_final_ratio': round(init_final_ratio, 2),
        'positional': {'INIT': init_rate, 'MID': mid_c/total, 'FINAL': final_rate},
        'enriched_middles': [(m, r) for m, _, _, r in mid_enriched[:8]],
        'depleted_middles': [(m, r) for m, _, _, r in mid_depleted[:5]],
    }

# =============================================
# COMPARATIVE: MIDDLE PROFILE SIMILARITY
# =============================================
print(f"\n\n{'='*70}")
print("MIDDLE PROFILE SIMILARITY (Jaccard on top-10 MIDDLEs)")
print(f"{'='*70}")

top10_mids = {}
for pfx in target_prefixes:
    if pfx_total.get(pfx, 0) < 20:
        continue
    top10_mids[pfx] = set(m for m, _ in pfx_mid[pfx].most_common(10))

from itertools import combinations
print(f"\n{'Pair':<12} {'Jaccard':>8} {'Overlap':>8}  Shared MIDDLEs")
pair_similarities = []
for p1, p2 in combinations(target_prefixes, 2):
    if p1 not in top10_mids or p2 not in top10_mids:
        continue
    s1, s2 = top10_mids[p1], top10_mids[p2]
    jaccard = len(s1 & s2) / len(s1 | s2) if s1 | s2 else 0
    pair_similarities.append((p1, p2, jaccard, s1 & s2))

pair_similarities.sort(key=lambda x: -x[2])
for p1, p2, j, shared in pair_similarities[:20]:
    if j > 0.3:
        print(f"  {p1}-{p2:<8} {j:>7.2f} {len(shared):>6}    {', '.join(sorted(shared))}")

print(f"\n\nLowest similarities (most distinct profiles):")
for p1, p2, j, shared in pair_similarities[-10:]:
    print(f"  {p1}-{p2:<8} {j:>7.2f} {len(shared):>6}    {', '.join(sorted(shared)) if shared else '(none)'}")

# =============================================
# OL DEEP-DIVE (primary target)
# =============================================
print(f"\n\n{'='*70}")
print("OL DEEP-DIVE: BALNEUM MARIAE CANDIDATE")
print(f"{'='*70}")

# Folio-level distribution
folio_ol = Counter()
folio_total = Counter()
folio_sec = {}
for tok in all_tokens:
    folio_total[tok['folio']] += 1
    folio_sec[tok['folio']] = tok['section']
    if tok['morph'].prefix == 'ol':
        folio_ol[tok['folio']] += 1

print(f"\nTop 15 ol folios:")
for folio in sorted(folio_total.keys(), key=lambda f: -(folio_ol.get(f,0)/folio_total[f]*100 if folio_total[f]>50 else 0))[:15]:
    if folio_total[folio] < 50:
        continue
    ol_rate = folio_ol.get(folio, 0) / folio_total[folio] * 100
    lk_c = sum(1 for t in all_tokens if t['folio']==folio and t['morph'].prefix=='lk')
    lk_rate = lk_c / folio_total[folio] * 100
    print(f"  {folio:<10} {folio_sec[folio]:<4} ol={folio_ol.get(folio,0):>3} ({ol_rate:>4.1f}%)  lk={lk_c:>3} ({lk_rate:>4.1f}%)")

# OL vs LK: are they anti-correlated across folios?
folio_list = [f for f in folio_total if folio_total[f] > 50]
ol_rates = [folio_ol.get(f, 0) / folio_total[f] * 100 for f in folio_list]
lk_rates = [sum(1 for t in all_tokens if t['folio']==f and t['morph'].prefix=='lk') / folio_total[f] * 100 for f in folio_list]

rho, p = spearmanr(ol_rates, lk_rates)
print(f"\nOL vs LK folio-level correlation: rho={rho:+.3f}  p={p:.4f}")
print(f"  (Negative = anti-correlated = different apparatus)")

# OL MIDDLE selectivity in B vs S sections
print(f"\nOL MIDDLE profile by section:")
ol_mid_by_sec = defaultdict(Counter)
for tok in all_tokens:
    if tok['morph'].prefix == 'ol' and tok['morph'].middle:
        ol_mid_by_sec[tok['section']][tok['morph'].middle] += 1

for sec in sections:
    total = sum(ol_mid_by_sec[sec].values())
    if total < 10:
        continue
    top5 = ol_mid_by_sec[sec].most_common(5)
    top_str = ', '.join(f"{m}({c})" for m, c in top5)
    print(f"  {sec:<6} n={total:>4}  top: {top_str}")

# OL co-occurrence
ol_lines = 0
ol_cooccur = Counter()
total_lines_pfx = 0

for key, line_tokens in lines.items():
    pfx_in_line = set(t['morph'].prefix for t in line_tokens if t['morph'].prefix)
    if not pfx_in_line:
        continue
    total_lines_pfx += 1
    if 'ol' in pfx_in_line:
        ol_lines += 1
        for p in pfx_in_line:
            if p != 'ol':
                ol_cooccur[p] += 1

baseline_rates = Counter()
for key, line_tokens in lines.items():
    pfx_in_line = set(t['morph'].prefix for t in line_tokens if t['morph'].prefix)
    for p in pfx_in_line:
        baseline_rates[p] += 1

print(f"\nOL co-occurrence (ol appears on {ol_lines}/{total_lines_pfx} lines = {ol_lines/total_lines_pfx:.1%}):")
for p in ['qo', 'ch', 'sh', 'ok', 'ot', 'da', 'lk', 'sa', 'ke', 'lch']:
    with_ol = ol_cooccur.get(p, 0)
    ol_rate = with_ol / ol_lines if ol_lines > 0 else 0
    base_rate = baseline_rates.get(p, 0) / total_lines_pfx if total_lines_pfx > 0 else 0
    enrich = ol_rate / base_rate if base_rate > 0 else 0
    marker = " <--" if enrich > 1.3 or enrich < 0.7 else ""
    print(f"  {p:<8} {with_ol:>5} ({ol_rate:.1%})  baseline={base_rate:.1%}  enrichment={enrich:.2f}x{marker}")

# Save results
out_path = Path(r'C:\git\voynich\phases\BRUNSCHWIG_APPARATUS_MAPPING\results\01_section_complement.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\n\nResults saved to {out_path}")
