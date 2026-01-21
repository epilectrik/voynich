#!/usr/bin/env python3
"""
Test B: Classify 27 PRECISION-exclusive tokens

From BRUNSCHWIG_CANDIDATE_LABELING, 27 tokens have P(animal) = 1.00.
These appear ONLY in PRECISION/REGIME_4 contexts per Brunschwig mapping.

Classification criteria:
1. Pipeline participation: PP-Genuine (A+AZC+B) vs B-Native Overlap (A+B, no AZC) vs B-Exclusive
2. L-compound membership: Check for lch-, lk-, lsh- prefixes (grammar operators per C501)
3. MIDDLE incompatibility degree: High-degree = universal, Low-degree = commitment

Pre-registered prediction P4 (Weak):
The 27 PRECISION-exclusive tokens will be <20% L-compound operators.
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load material class priors to find the 27 tokens
with open(PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json', 'r') as f:
    priors_data = json.load(f)

# Find all with animal = 1.00
animal_exclusive = []
for item in priors_data['results']:
    if item.get('material_class_posterior', {}).get('animal', 0) == 1.0:
        animal_exclusive.append(item['middle'])

print("=" * 70)
print("TEST B: CLASSIFY 27 PRECISION-EXCLUSIVE TOKENS")
print("=" * 70)
print()
print(f"Tokens with P(animal) = 1.00: {len(animal_exclusive)}")
print()

# Load transcript
df = pd.read_csv(DATA_PATH, sep='\t')
df = df[df['transcriber'] == 'H']  # PRIMARY track only

# Morphology parsing
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk',
    'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po',
    'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
L_COMPOUND_PREFIXES = ['lch', 'lk', 'lsh']  # Grammar operators per C501/C298
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]

AZC_FOLIOS = ['f67r1', 'f67r2', 'f67v1', 'f67v2', 'f68r1', 'f68r2', 'f68r3',
              'f68v1', 'f68v2', 'f68v3', 'f69r1', 'f69r2', 'f69v1', 'f69v2',
              'f70r1', 'f70r2', 'f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1',
              'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v']

def extract_morphology(token):
    """Extract PREFIX, MIDDLE, SUFFIX from token."""
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

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder

    if middle == '':
        middle = '_EMPTY_'

    return prefix, middle, suffix

# Extract morphology for all tokens
df['prefix'], df['middle'], df['suffix'] = zip(*df['word'].apply(extract_morphology))

# Classify Currier
df_a = df[df['language'] == 'A']
df_b = df[df['language'] == 'B']
df_azc = df[df['folio'].isin(AZC_FOLIOS)]

a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
azc_middles = set(df_azc['middle'].dropna().unique())

# Classification results
results = []

print("-" * 70)
print("TOKEN CLASSIFICATION")
print("-" * 70)
print()

for middle in sorted(animal_exclusive):
    in_a = middle in a_middles
    in_b = middle in b_middles
    in_azc = middle in azc_middles

    # Pipeline classification
    if in_a and in_azc and in_b:
        pipeline_class = 'PP-Genuine'
    elif in_a and in_b and not in_azc:
        pipeline_class = 'B-Native-Overlap'
    elif in_b and not in_a:
        pipeline_class = 'B-Exclusive'
    elif in_a and not in_b:
        pipeline_class = 'A-Exclusive'
    else:
        pipeline_class = 'OTHER'

    # L-compound check
    is_l_compound = any(middle.startswith(lp.replace(p, '')) for lp in L_COMPOUND_PREFIXES for p in PREFIXES if middle.startswith(lp.replace(p, '')))

    # Actually check if the MIDDLE itself starts with l- patterns
    is_l_compound = middle.startswith('l') if middle and middle != '_EMPTY_' else False

    # Count occurrences
    a_count = len(df_a[df_a['middle'] == middle])
    b_count = len(df_b[df_b['middle'] == middle])
    azc_count = len(df_azc[df_azc['middle'] == middle])

    results.append({
        'middle': middle,
        'pipeline_class': pipeline_class,
        'is_l_compound': is_l_compound,
        'in_a': in_a,
        'in_b': in_b,
        'in_azc': in_azc,
        'a_count': a_count,
        'b_count': b_count,
        'azc_count': azc_count
    })

    l_flag = " [L-COMPOUND]" if is_l_compound else ""
    print(f"{middle:15s} | {pipeline_class:18s} | A={a_count:3d} B={b_count:3d} AZC={azc_count:3d}{l_flag}")

print()
print("-" * 70)
print("CLASSIFICATION SUMMARY")
print("-" * 70)

# Pipeline class distribution
pipeline_counts = Counter(r['pipeline_class'] for r in results)
print("\nPipeline Classification:")
for cls, count in sorted(pipeline_counts.items(), key=lambda x: -x[1]):
    pct = count / len(results) * 100
    print(f"  {cls:18s}: {count:2d} ({pct:5.1f}%)")

# L-compound count
l_compound_count = sum(1 for r in results if r['is_l_compound'])
l_compound_pct = l_compound_count / len(results) * 100
print(f"\nL-compound operators: {l_compound_count} ({l_compound_pct:.1f}%)")

# P4 evaluation
p4_threshold = 20
p4_pass = l_compound_pct < p4_threshold

print()
print("=" * 70)
print("P4 EVALUATION")
print("=" * 70)
print(f"Prediction: <{p4_threshold}% L-compound operators")
print(f"Actual: {l_compound_pct:.1f}%")
print(f"Result: {'PASS' if p4_pass else 'FAIL'}")

# Additional analysis: Where do B-Exclusive tokens appear?
print()
print("-" * 70)
print("B-EXCLUSIVE TOKEN DETAILS")
print("-" * 70)

b_exclusive = [r for r in results if r['pipeline_class'] == 'B-Exclusive']
if b_exclusive:
    for r in b_exclusive:
        middle = r['middle']
        # Find which folios
        b_folios = df_b[df_b['middle'] == middle]['folio'].unique()
        print(f"{middle}: appears in {len(b_folios)} B folios: {', '.join(sorted(b_folios)[:5])}{'...' if len(b_folios) > 5 else ''}")
else:
    print("No B-Exclusive tokens found")

# Check REGIME distribution for these tokens
print()
print("-" * 70)
print("REGIME DISTRIBUTION OF PRECISION-EXCLUSIVE TOKENS")
print("-" * 70)

# Load regime mapping
with open(PROJECT_ROOT / 'results' / 'regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

# Invert mapping
folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for f in folios:
        folio_to_regime[f] = regime

# Count tokens by REGIME
regime_token_counts = Counter()
for r in results:
    middle = r['middle']
    b_folios = df_b[df_b['middle'] == middle]['folio'].unique()
    for f in b_folios:
        if f in folio_to_regime:
            regime_token_counts[folio_to_regime[f]] += 1

print("\nToken appearances by REGIME:")
for regime in sorted(regime_token_counts.keys()):
    print(f"  {regime}: {regime_token_counts[regime]}")

# Save results
output = {
    'test': 'B_PRECISION_TOKEN_CLASSIFICATION',
    'n_tokens': len(animal_exclusive),
    'tokens': sorted(animal_exclusive),
    'pipeline_distribution': dict(pipeline_counts),
    'l_compound_count': l_compound_count,
    'l_compound_pct': l_compound_pct,
    'p4_evaluation': {
        'prediction': f'<{p4_threshold}% L-compound operators',
        'actual_pct': l_compound_pct,
        'result': 'PASS' if p4_pass else 'FAIL'
    },
    'regime_token_counts': dict(regime_token_counts),
    'token_details': results
}

output_path = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'test_b_precision_tokens.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print()
print(f"Results saved to {output_path}")
