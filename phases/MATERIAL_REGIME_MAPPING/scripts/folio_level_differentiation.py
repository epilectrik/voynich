"""
FOLIO-LEVEL DIFFERENTIATION

Both animal and herb route to REGIME_4. Do they route to the SAME folios?
This tests whether PP profiles provide finer-grained routing than REGIME level.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("FOLIO-LEVEL MATERIAL DIFFERENTIATION")
print("=" * 70)

# Load REGIME mapping
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

# Load v2 results to get classification
with open('phases/MATERIAL_REGIME_MAPPING/results/material_regime_mapping_v2.json', 'r') as f:
    v2_results = json.load(f)

# Rebuild classification (quick version using scores)
ANIMAL_MARKERS = {
    'pp_markers': {'pch': 43.0, 'opch': 18.0, 'octh': 9.0, 'cph': 3.7, 'kch': 3.7, 'ch': 2.9, 'ckh': 2.9, 'h': 2.5},
    'positive_suffixes': {'ey', 'ol'},
    'negative_suffixes': {'y', 'dy'},
}
HERB_MARKERS = {
    'pp_markers': {'keo': 66.0, 'eok': 52.0, 'ko': 33.0, 'cho': 33.0, 'to': 33.0, 'ry': 28.0, 'eo': 3.3},
    'positive_suffixes': {'y', 'dy'},
    'negative_suffixes': {'ey', 'ol'},
}

# Build records
a_records = defaultdict(lambda: {'middles': [], 'prefixes': [], 'suffixes': [], 'tokens': []})
for token in tx.currier_a():
    rid = f"{token.folio}:{token.line}"
    if token.word:
        m = morph.extract(token.word)
        a_records[rid]['tokens'].append(token.word)
        if m.middle: a_records[rid]['middles'].append(m.middle)
        if m.prefix: a_records[rid]['prefixes'].append(m.prefix)
        if m.suffix: a_records[rid]['suffixes'].append(m.suffix)

def score(record, markers):
    middles = record['middles']
    suffixes = record['suffixes']
    n = len(record['tokens']) or 1
    pp = sum(markers['pp_markers'].get(m, 0) for m in middles) / n
    suf = (sum(1 for s in suffixes if s in markers['positive_suffixes']) -
           sum(1 for s in suffixes if s in markers['negative_suffixes'])) / n
    return pp * 0.6 + suf * 0.4

animal_scores = {rid: score(data, ANIMAL_MARKERS) for rid, data in a_records.items()}
herb_scores = {rid: score(data, HERB_MARKERS) for rid, data in a_records.items()}

# Classify
animal_vals = list(animal_scores.values())
herb_vals = list(herb_scores.values())
animal_thresh = np.mean(animal_vals) + 1.5 * np.std(animal_vals)
herb_thresh = np.mean(herb_vals) + 1.5 * np.std(herb_vals)

animal_high = {rid for rid, s in animal_scores.items() if s >= animal_thresh}
herb_high = {rid for rid, s in herb_scores.items() if s >= herb_thresh}

# Remove overlap
overlap = animal_high & herb_high
for rid in overlap:
    if animal_scores[rid] > herb_scores[rid]:
        herb_high.discard(rid)
    else:
        animal_high.discard(rid)

print(f"Animal records: {len(animal_high)}")
print(f"Herb records: {len(herb_high)}")

# Build A profiles for AZC
a_profiles = {}
for rid, data in a_records.items():
    a_profiles[rid] = {
        'middles': set(data['middles']),
        'prefixes': set(data['prefixes']) | {''},
        'suffixes': set(data['suffixes']) | {''},
    }

# Build B data
b_tokens = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        b_tokens.append({'word': token.word, 'middle': m.middle or '', 'prefix': m.prefix or '', 'suffix': m.suffix or ''})

b_folio_middles = defaultdict(set)
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)

# Get compatible middles
def get_compatible(records, a_profiles, b_tokens):
    compat = Counter()
    for rid in records:
        if rid in a_profiles:
            p = a_profiles[rid]
            for bt in b_tokens:
                if bt['middle'] in p['middles'] and bt['prefix'] in p['prefixes'] and bt['suffix'] in p['suffixes']:
                    if bt['middle']:
                        compat[bt['middle']] += 1
    return compat

animal_middles = get_compatible(animal_high, a_profiles, b_tokens)
herb_middles = get_compatible(herb_high, a_profiles, b_tokens)

# Per-folio reception
def folio_reception(compat_middles, b_folio_middles):
    compat_set = set(compat_middles.keys())
    return {f: len(m & compat_set) / len(m) if m else 0 for f, m in b_folio_middles.items()}

animal_reception = folio_reception(animal_middles, b_folio_middles)
herb_reception = folio_reception(herb_middles, b_folio_middles)

# Focus on REGIME_4 folios
regime_4_folios = regime_mapping['REGIME_4']

print("\n" + "=" * 70)
print("REGIME_4 FOLIO RECEPTION COMPARISON")
print("=" * 70)

print(f"\n{'Folio':<12} {'Animal':<12} {'Herb':<12} {'Diff':<12} {'Dominant':<12}")
print("-" * 60)

animal_dominant = []
herb_dominant = []
neutral = []

for f in regime_4_folios:
    a = animal_reception.get(f, 0)
    h = herb_reception.get(f, 0)
    diff = a - h

    if diff > 0.05:
        dom = "ANIMAL"
        animal_dominant.append(f)
    elif diff < -0.05:
        dom = "HERB"
        herb_dominant.append(f)
    else:
        dom = "-"
        neutral.append(f)

    print(f"{f:<12} {a:.3f}        {h:.3f}        {diff:+.3f}       {dom}")

print(f"\nWithin REGIME_4 ({len(regime_4_folios)} folios):")
print(f"  Animal-dominant: {len(animal_dominant)} ({100*len(animal_dominant)/len(regime_4_folios):.1f}%)")
print(f"  Herb-dominant: {len(herb_dominant)} ({100*len(herb_dominant)/len(regime_4_folios):.1f}%)")
print(f"  Neutral: {len(neutral)} ({100*len(neutral)/len(regime_4_folios):.1f}%)")

# Statistical test: Are the reception profiles different?
animal_r4 = [animal_reception.get(f, 0) for f in regime_4_folios]
herb_r4 = [herb_reception.get(f, 0) for f in regime_4_folios]

# Paired t-test
t_stat, p_val = stats.ttest_rel(animal_r4, herb_r4)
print(f"\nPaired t-test (animal vs herb within REGIME_4):")
print(f"  t = {t_stat:.3f}, p = {p_val:.6f}")

# Correlation between animal and herb reception
corr, corr_p = stats.pearsonr(animal_r4, herb_r4)
print(f"\nCorrelation between animal and herb reception:")
print(f"  r = {corr:.3f}, p = {corr_p:.6f}")

# Check other REGIMEs for differentiation
print("\n" + "=" * 70)
print("DIFFERENTIATION BY REGIME")
print("=" * 70)

for regime, folios in sorted(regime_mapping.items()):
    animal_r = [animal_reception.get(f, 0) for f in folios]
    herb_r = [herb_reception.get(f, 0) for f in folios]

    diff = np.mean(animal_r) - np.mean(herb_r)

    # Count dominant
    a_dom = sum(1 for f in folios if animal_reception.get(f, 0) - herb_reception.get(f, 0) > 0.05)
    h_dom = sum(1 for f in folios if herb_reception.get(f, 0) - animal_reception.get(f, 0) > 0.05)

    print(f"\n{regime} ({len(folios)} folios):")
    print(f"  Mean animal: {np.mean(animal_r):.3f}, Mean herb: {np.mean(herb_r):.3f}")
    print(f"  Difference: {diff:+.3f}")
    print(f"  Animal-dominant: {a_dom}, Herb-dominant: {h_dom}")

# Summary
print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)

if corr > 0.8:
    print(f"""
Animal and herb reception patterns are HIGHLY CORRELATED (r={corr:.3f}).
This means they route to the SAME folios within REGIME_4.

Implications:
1. PP profiles may NOT differentiate material routing at folio level
2. Both material classes have similar operational requirements
3. The differentiation may be at a FINER level (token variants within folio)
   or may not exist at the folio/REGIME level
""")
else:
    print(f"""
Animal and herb reception patterns are DIFFERENTIATED (r={corr:.3f}).
This suggests they route to DIFFERENT folios within REGIME_4.

Animal-dominant REGIME_4 folios: {animal_dominant}
Herb-dominant REGIME_4 folios: {herb_dominant}
""")

# Save results
results = {
    'regime_4_analysis': {
        'correlation': corr,
        'correlation_p': corr_p,
        'paired_t': t_stat,
        'paired_p': p_val,
        'animal_dominant': animal_dominant,
        'herb_dominant': herb_dominant,
        'neutral': neutral,
    },
}
with open('phases/MATERIAL_REGIME_MAPPING/results/folio_level_diff.json', 'w') as f:
    json.dump(results, f, indent=2)
