"""
Test: Does line-1 HT use more folio-exclusive MIDDLEs than working HT?

Question: Are line-1 HT MIDDLEs more likely to appear only in that folio?

Method:
1. For each B folio, identify line-1 HT tokens and working HT tokens
2. Extract MIDDLEs from each group
3. Check: what fraction of MIDDLEs appear ONLY in that folio (folio-unique)?
4. Compare folio-uniqueness rate between line-1 HT and working HT
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# First pass: build global MIDDLE -> folios mapping for all B tokens
middle_to_folios = defaultdict(set)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        middle_to_folios[m.middle].add(token.folio)

# Count folio-unique vs multi-folio MIDDLEs overall
folio_unique_middles = {mid for mid, folios in middle_to_folios.items() if len(folios) == 1}
print(f"Global MIDDLE Statistics:")
print(f"  Total unique MIDDLEs in B: {len(middle_to_folios)}")
print(f"  Folio-unique MIDDLEs: {len(folio_unique_middles)} ({100*len(folio_unique_middles)/len(middle_to_folios):.1f}%)")
print()

# Second pass: collect HT tokens by folio and line position
folio_data = defaultdict(lambda: {'line1_ht': [], 'working_ht': []})

folio_lines = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    folio_lines[token.folio][token.line].append({
        'word': w,
        'is_ht': w not in classified_tokens
    })

for folio, lines in folio_lines.items():
    sorted_lines = sorted(lines.keys())
    if not sorted_lines:
        continue
    first_line = sorted_lines[0]

    for line_num in sorted_lines:
        for tok in lines[line_num]:
            if tok['is_ht']:
                m = morph.extract(tok['word'])
                if m.middle:
                    if line_num == first_line:
                        folio_data[folio]['line1_ht'].append(m.middle)
                    else:
                        folio_data[folio]['working_ht'].append(m.middle)

# Analyze folio-uniqueness for each group
line1_total = 0
line1_folio_unique = 0
working_total = 0
working_folio_unique = 0

# Also track per-folio rates
folio_rates = []

for folio, data in folio_data.items():
    line1_mids = data['line1_ht']
    working_mids = data['working_ht']

    # Count folio-unique MIDDLEs in each group
    l1_unique = sum(1 for mid in line1_mids if mid in folio_unique_middles)
    w_unique = sum(1 for mid in working_mids if mid in folio_unique_middles)

    line1_total += len(line1_mids)
    line1_folio_unique += l1_unique
    working_total += len(working_mids)
    working_folio_unique += w_unique

    if len(line1_mids) >= 3 and len(working_mids) >= 10:
        l1_rate = 100 * l1_unique / len(line1_mids)
        w_rate = 100 * w_unique / len(working_mids)
        folio_rates.append({
            'folio': folio,
            'line1_count': len(line1_mids),
            'line1_unique': l1_unique,
            'line1_rate': l1_rate,
            'working_count': len(working_mids),
            'working_unique': w_unique,
            'working_rate': w_rate,
            'delta': l1_rate - w_rate
        })

print(f"Folio-Uniqueness Analysis:")
print(f"\nLine-1 HT:")
print(f"  Total MIDDLEs: {line1_total}")
print(f"  Folio-unique: {line1_folio_unique} ({100*line1_folio_unique/line1_total:.1f}%)")

print(f"\nWorking HT:")
print(f"  Total MIDDLEs: {working_total}")
print(f"  Folio-unique: {working_folio_unique} ({100*working_folio_unique/working_total:.1f}%)")

line1_rate = 100 * line1_folio_unique / line1_total
working_rate = 100 * working_folio_unique / working_total
delta = line1_rate - working_rate

print(f"\nDifference: {delta:+.1f}pp")

# Statistical test
from scipy import stats
# Chi-squared test
contingency = [[line1_folio_unique, line1_total - line1_folio_unique],
               [working_folio_unique, working_total - working_folio_unique]]
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-squared test: chi2={chi2:.2f}, p={p_value:.6f}")

# Per-folio analysis
print("\n" + "="*60)
print("Per-Folio Breakdown (folios with >=3 line-1 HT, >=10 working HT)")
print("="*60)

folio_rates.sort(key=lambda x: x['delta'], reverse=True)

n_positive = sum(1 for f in folio_rates if f['delta'] > 0)
n_negative = sum(1 for f in folio_rates if f['delta'] < 0)
n_zero = sum(1 for f in folio_rates if f['delta'] == 0)

print(f"\nDirection count: {n_positive} positive, {n_negative} negative, {n_zero} zero")
print(f"Mean delta: {sum(f['delta'] for f in folio_rates)/len(folio_rates):.1f}pp")

# Show top examples
print("\nTop 10 folios with highest line-1 folio-uniqueness elevation:")
for f in folio_rates[:10]:
    print(f"  {f['folio']}: Line-1 {f['line1_rate']:.0f}% vs Working {f['working_rate']:.0f}% (delta: {f['delta']:+.1f}pp)")

# Verdict
print("\n" + "="*60)
print("VERDICT")
print("="*60)

if delta > 10 and p_value < 0.01:
    verdict = "FOLIO_UNIQUE_ELEVATED"
    explanation = f"Line-1 HT uses significantly more folio-unique MIDDLEs (+{delta:.1f}pp, p={p_value:.6f})"
elif delta > 5:
    verdict = "FOLIO_UNIQUE_MODERATE"
    explanation = f"Line-1 HT uses moderately more folio-unique MIDDLEs (+{delta:.1f}pp)"
elif delta < -5:
    verdict = "FOLIO_UNIQUE_REDUCED"
    explanation = f"Line-1 HT uses fewer folio-unique MIDDLEs ({delta:.1f}pp)"
else:
    verdict = "FOLIO_UNIQUE_SIMILAR"
    explanation = f"Line-1 HT and working HT have similar folio-uniqueness rates ({delta:+.1f}pp)"

print(f"\n{verdict}: {explanation}")

# Save results
results = {
    'global_stats': {
        'total_middles_in_b': len(middle_to_folios),
        'folio_unique_middles': len(folio_unique_middles),
        'folio_unique_pct': 100 * len(folio_unique_middles) / len(middle_to_folios)
    },
    'line1_ht': {
        'total_middles': line1_total,
        'folio_unique': line1_folio_unique,
        'folio_unique_pct': line1_rate
    },
    'working_ht': {
        'total_middles': working_total,
        'folio_unique': working_folio_unique,
        'folio_unique_pct': working_rate
    },
    'comparison': {
        'delta_pp': delta,
        'chi2': chi2,
        'p_value': p_value,
        'n_folios_analyzed': len(folio_rates),
        'n_positive': n_positive,
        'n_negative': n_negative
    },
    'verdict': verdict,
    'explanation': explanation
}

out_path = PROJECT_ROOT / 'phases' / 'B_LINE_POSITION_HT' / 'results' / 'ht_folio_uniqueness.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
