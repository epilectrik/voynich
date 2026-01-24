#!/usr/bin/env python3
"""
Control Test: Does the animal-RI signal appear in ALL B folios,
or is it specific to REGIME_4/precision candidates?

Compare f43v (REGIME_4, low-recovery high-escape) vs
f103v (REGIME_1, typical simple procedure)
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load transcript
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

# Morphology parsing
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk',
    'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po',
    'sa', 'ka', 'ta', 'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)
SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy', 'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey', 'chol', 'shol', 'kol', 'tol', 'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el', 'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]

def extract_morphology(token):
    if pd.isna(token):
        return None, None, None
    token = str(token)
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break
    if not prefix:
        return None, None, None
    remainder = token[len(prefix):]
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break
    middle = remainder[:-len(suffix)] if suffix else remainder
    if middle == '':
        middle = '_EMPTY_'
    return prefix, middle, suffix

df_a['prefix'], df_a['middle'], df_a['suffix'] = zip(*df_a['word'].apply(extract_morphology))
df_b['prefix'], df_b['middle'], df_b['suffix'] = zip(*df_b['word'].apply(extract_morphology))

# Precompute A entries and shared MIDDLEs
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(lambda x: set(x.dropna())).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

# Load material-class priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)
priors_lookup = {item['middle']: item.get('material_class_posterior', {}) for item in priors_data['results']}

def analyze_folio(folio_name, df_b, a_entries, shared_middles, b_middles, priors_lookup, overlap_threshold=3):
    """Analyze animal-RI signal for a single B folio."""
    folio_tokens = df_b[df_b['folio'] == folio_name]
    folio_middles = set(folio_tokens['middle'].dropna().unique())
    folio_shared = folio_middles & shared_middles

    # Find A entries with overlap
    def calc_overlap(entry_middles):
        if not entry_middles or not folio_shared:
            return 0
        return len(entry_middles & folio_shared)

    a_entries['overlap'] = a_entries['middles'].apply(calc_overlap)
    high_overlap = a_entries[a_entries['overlap'] >= overlap_threshold]

    # Collect RI MIDDLEs from high-overlap entries
    high_overlap_middles = set()
    for _, row in high_overlap.iterrows():
        high_overlap_middles.update(row['middles'])

    ri_middles = high_overlap_middles - b_middles

    # Count animal-associated RIs
    ri_with_animal = []
    animal_1_count = 0
    for middle in ri_middles:
        if middle in priors_lookup:
            animal_p = priors_lookup[middle].get('animal', 0)
            if animal_p > 0:
                ri_with_animal.append((middle, animal_p))
                if animal_p == 1.0:
                    animal_1_count += 1

    return {
        'folio': folio_name,
        'unique_middles': len(folio_middles),
        'shared_middles': len(folio_shared),
        'high_overlap_entries': len(high_overlap),
        'ri_middles': len(ri_middles),
        'ri_with_animal': len(ri_with_animal),
        'ri_animal_1.0': animal_1_count,
        'animal_middles': ri_with_animal
    }

# Test folios from different REGIMEs
test_folios = {
    'REGIME_4_precision': ['f43v', 'f39v', 'f55r'],  # Low recovery, high escape
    'REGIME_4_other': ['f34v', 'f94r', 'f95v1'],      # Low recovery, low escape
    'REGIME_1': ['f103v', 'f104r', 'f75r'],           # Simple procedures
    'REGIME_3': ['f103r', 'f33r', 'f77r']             # Standard procedures
}

print("=" * 70)
print("CONTROL TEST: Animal-RI Signal by REGIME")
print("=" * 70)
print()

results = {}
for regime_type, folios in test_folios.items():
    print(f"\n{regime_type}:")
    print("-" * 50)
    regime_results = []
    for folio in folios:
        result = analyze_folio(folio, df_b, a_entries.copy(), shared_middles, b_middles, priors_lookup)
        regime_results.append(result)
        print(f"  {folio}: shared={result['shared_middles']}, "
              f"high_overlap_entries={result['high_overlap_entries']}, "
              f"RI_animal={result['ri_with_animal']} (P=1.0: {result['ri_animal_1.0']})")
    results[regime_type] = regime_results

print()
print("=" * 70)
print("SUMMARY: Mean animal-RI count by REGIME type")
print("=" * 70)
print()

for regime_type, regime_results in results.items():
    mean_animal = sum(r['ri_with_animal'] for r in regime_results) / len(regime_results)
    mean_animal_1 = sum(r['ri_animal_1.0'] for r in regime_results) / len(regime_results)
    print(f"{regime_type:25s}: mean RI_animal={mean_animal:.1f}, mean P=1.0={mean_animal_1:.1f}")

print()
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)
print()

# Compare REGIME_4_precision vs others
r4_precision = results['REGIME_4_precision']
r4_other = results['REGIME_4_other']
r1 = results['REGIME_1']

r4p_mean = sum(r['ri_with_animal'] for r in r4_precision) / len(r4_precision)
r4o_mean = sum(r['ri_with_animal'] for r in r4_other) / len(r4_other)
r1_mean = sum(r['ri_with_animal'] for r in r1) / len(r1)

if r4p_mean > r4o_mean * 1.2 and r4p_mean > r1_mean * 1.2:
    print("POSITIVE: REGIME_4 precision candidates (low-recovery, high-escape)")
    print("show ELEVATED animal-RI signal compared to other folios.")
    print()
    print("This supports the hypothesis that timing-critical REGIME_4 folios")
    print("are more likely to trace back to animal-associated A entries.")
elif r4p_mean > r1_mean * 1.2:
    print("PARTIAL: REGIME_4 precision candidates show elevated signal vs REGIME_1,")
    print("but not clearly different from other REGIME_4 folios.")
else:
    print("NEGATIVE: No clear difference in animal-RI signal by REGIME type.")
    print("The animal association may be diffuse across all B folios.")

# Save results
output = {
    'test_results': results,
    'summary': {
        regime: {
            'mean_ri_animal': sum(r['ri_with_animal'] for r in res) / len(res),
            'mean_ri_animal_1': sum(r['ri_animal_1.0'] for r in res) / len(res)
        }
        for regime, res in results.items()
    }
}

output_path = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'reverse_trace_control.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=str)

print()
print(f"Results saved to {output_path}")
