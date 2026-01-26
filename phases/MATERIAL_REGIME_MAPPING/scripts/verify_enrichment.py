"""
VERIFY REGIME_4 ENRICHMENT CALCULATION

The expert noted that both animal and herb showing exactly 1.87x enrichment
is "almost suspiciously exact." Let's verify this isn't a computational artifact.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json
import numpy as np

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("VERIFICATION: REGIME_4 ENRICHMENT CALCULATION")
print("=" * 70)

# Load REGIME mapping
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# Material markers
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

# Build A records
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

# Score all records
animal_scores = {rid: score(data, ANIMAL_MARKERS) for rid, data in a_records.items()}
herb_scores = {rid: score(data, HERB_MARKERS) for rid, data in a_records.items()}

# Classify with threshold
animal_vals = list(animal_scores.values())
herb_vals = list(herb_scores.values())
animal_thresh = np.mean(animal_vals) + 1.5 * np.std(animal_vals)
herb_thresh = np.mean(herb_vals) + 1.5 * np.std(herb_vals)

animal_high = {rid for rid, s in animal_scores.items() if s >= animal_thresh}
herb_high = {rid for rid, s in herb_scores.items() if s >= herb_thresh}

# Remove overlap
for rid in list(animal_high & herb_high):
    if animal_scores[rid] > herb_scores[rid]:
        herb_high.discard(rid)
    else:
        animal_high.discard(rid)

print(f"\nRecord counts:")
print(f"  Animal high-confidence: {len(animal_high)}")
print(f"  Herb high-confidence: {len(herb_high)}")
print(f"  Overlap removed: {len(animal_high & herb_high)}")

# Build A profiles for AZC
a_profiles = {}
for rid, data in a_records.items():
    a_profiles[rid] = {
        'middles': set(data['middles']),
        'prefixes': set(data['prefixes']) | {''},
        'suffixes': set(data['suffixes']) | {''},
    }

# Build B folio -> MIDDLE mapping
b_folio_middles = defaultdict(set)
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)

# Build B tokens for compatibility
b_tokens = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        b_tokens.append({
            'word': token.word,
            'middle': m.middle or '',
            'prefix': m.prefix or '',
            'suffix': m.suffix or '',
        })

# Get compatible middles for each class
def get_compatible_middles(records, a_profiles, b_tokens):
    compat = Counter()
    for rid in records:
        if rid in a_profiles:
            p = a_profiles[rid]
            for bt in b_tokens:
                if (bt['middle'] in p['middles'] and
                    bt['prefix'] in p['prefixes'] and
                    bt['suffix'] in p['suffixes']):
                    if bt['middle']:
                        compat[bt['middle']] += 1
    return compat

animal_middles = get_compatible_middles(animal_high, a_profiles, b_tokens)
herb_middles = get_compatible_middles(herb_high, a_profiles, b_tokens)

print(f"\nCompatible MIDDLEs:")
print(f"  Animal: {len(animal_middles)}")
print(f"  Herb: {len(herb_middles)}")

# Compute folio reception
def compute_reception(compat_middles, b_folio_middles):
    compat_set = set(compat_middles.keys())
    return {f: len(m & compat_set) / len(m) if m else 0 for f, m in b_folio_middles.items()}

animal_reception = compute_reception(animal_middles, b_folio_middles)
herb_reception = compute_reception(herb_middles, b_folio_middles)

# Get high-reception folios (top 25%)
def get_high_reception(reception, pct=75):
    rates = list(reception.values())
    thresh = np.percentile(rates, pct)
    return [f for f, r in reception.items() if r >= thresh], thresh

animal_high_folios, animal_thresh_r = get_high_reception(animal_reception)
herb_high_folios, herb_thresh_r = get_high_reception(herb_reception)

print(f"\nHigh-reception folios (top 25%):")
print(f"  Animal: {len(animal_high_folios)} (threshold: {animal_thresh_r:.4f})")
print(f"  Herb: {len(herb_high_folios)} (threshold: {herb_thresh_r:.4f})")

# Count REGIMEs
animal_regimes = Counter([folio_to_regime[f] for f in animal_high_folios if f in folio_to_regime])
herb_regimes = Counter([folio_to_regime[f] for f in herb_high_folios if f in folio_to_regime])

# Baseline
all_folios = [f for f in b_folio_middles.keys() if f in folio_to_regime]
baseline = Counter([folio_to_regime[f] for f in all_folios])

print(f"\n" + "=" * 70)
print("DETAILED REGIME COUNTS")
print("=" * 70)

print(f"\nBaseline ({len(all_folios)} folios):")
for r in sorted(baseline.keys()):
    pct = baseline[r] / len(all_folios)
    print(f"  {r}: {baseline[r]} ({pct:.4f})")

print(f"\nAnimal high-reception ({len([f for f in animal_high_folios if f in folio_to_regime])} folios with REGIME):")
for r in sorted(baseline.keys()):
    count = animal_regimes.get(r, 0)
    n_total = len([f for f in animal_high_folios if f in folio_to_regime])
    pct = count / n_total if n_total > 0 else 0
    base_pct = baseline[r] / len(all_folios)
    enrichment = pct / base_pct if base_pct > 0 else 0
    print(f"  {r}: {count} ({pct:.4f}) - enrichment: {enrichment:.4f}x")

print(f"\nHerb high-reception ({len([f for f in herb_high_folios if f in folio_to_regime])} folios with REGIME):")
for r in sorted(baseline.keys()):
    count = herb_regimes.get(r, 0)
    n_total = len([f for f in herb_high_folios if f in folio_to_regime])
    pct = count / n_total if n_total > 0 else 0
    base_pct = baseline[r] / len(all_folios)
    enrichment = pct / base_pct if base_pct > 0 else 0
    print(f"  {r}: {count} ({pct:.4f}) - enrichment: {enrichment:.4f}x")

# Detailed REGIME_4 calculation
print(f"\n" + "=" * 70)
print("REGIME_4 ENRICHMENT - DETAILED BREAKDOWN")
print("=" * 70)

base_r4_pct = baseline['REGIME_4'] / len(all_folios)
print(f"\nBaseline REGIME_4: {baseline['REGIME_4']}/{len(all_folios)} = {base_r4_pct:.6f}")

animal_r4_count = animal_regimes.get('REGIME_4', 0)
animal_n = len([f for f in animal_high_folios if f in folio_to_regime])
animal_r4_pct = animal_r4_count / animal_n if animal_n > 0 else 0
animal_r4_enrich = animal_r4_pct / base_r4_pct if base_r4_pct > 0 else 0

print(f"\nAnimal REGIME_4:")
print(f"  Count: {animal_r4_count}")
print(f"  Total high-reception with REGIME: {animal_n}")
print(f"  Proportion: {animal_r4_pct:.6f}")
print(f"  Enrichment: {animal_r4_enrich:.6f}x")

herb_r4_count = herb_regimes.get('REGIME_4', 0)
herb_n = len([f for f in herb_high_folios if f in folio_to_regime])
herb_r4_pct = herb_r4_count / herb_n if herb_n > 0 else 0
herb_r4_enrich = herb_r4_pct / base_r4_pct if base_r4_pct > 0 else 0

print(f"\nHerb REGIME_4:")
print(f"  Count: {herb_r4_count}")
print(f"  Total high-reception with REGIME: {herb_n}")
print(f"  Proportion: {herb_r4_pct:.6f}")
print(f"  Enrichment: {herb_r4_enrich:.6f}x")

print(f"\n" + "=" * 70)
print("VERIFICATION RESULT")
print("=" * 70)

diff = abs(animal_r4_enrich - herb_r4_enrich)
print(f"\nAnimal REGIME_4 enrichment: {animal_r4_enrich:.6f}x")
print(f"Herb REGIME_4 enrichment: {herb_r4_enrich:.6f}x")
print(f"Difference: {diff:.6f}")

if diff < 0.01:
    print(f"\nWARNING: Enrichments are IDENTICAL to 2 decimal places.")
    print("This could be:")
    print("  1. Coincidence (both happen to have same high-reception folio count in REGIME_4)")
    print("  2. Computational artifact (check if same folios selected)")

    # Check folio overlap
    animal_r4_folios = [f for f in animal_high_folios if folio_to_regime.get(f) == 'REGIME_4']
    herb_r4_folios = [f for f in herb_high_folios if folio_to_regime.get(f) == 'REGIME_4']

    overlap = set(animal_r4_folios) & set(herb_r4_folios)
    print(f"\nREGIME_4 folio overlap:")
    print(f"  Animal REGIME_4 folios: {len(animal_r4_folios)}")
    print(f"  Herb REGIME_4 folios: {len(herb_r4_folios)}")
    print(f"  Overlap: {len(overlap)}")
    print(f"  Jaccard: {len(overlap) / len(set(animal_r4_folios) | set(herb_r4_folios)) if (set(animal_r4_folios) | set(herb_r4_folios)) else 0:.3f}")
else:
    print(f"\nEnrichments are DIFFERENT. The earlier identical value was likely rounding.")

# List the actual folios
print(f"\nAnimal REGIME_4 folios: {sorted(animal_r4_folios)}")
print(f"Herb REGIME_4 folios: {sorted(herb_r4_folios)}")
