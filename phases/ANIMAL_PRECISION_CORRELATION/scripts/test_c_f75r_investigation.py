#!/usr/bin/env python3
"""
Test C: f75r Investigation

The Tier 4 speculative mapping associated f75r with Puff Chapter 71 (Kudreck/cow dung).
However, our regime_folio_mapping.json shows f75r is in REGIME_1, not REGIME_4.

This test investigates:
1. Where is f75r actually classified?
2. Does f75r show any distinctive characteristics vs other REGIME_1 folios?
3. Is there evidence for f75r being procedurally different (animal-like)?

Pre-registered prediction P3 (Medium):
f75r will have higher B-exclusive MIDDLE rate than REGIME_4 mean.
NOTE: Since f75r is actually REGIME_1, we reframe to: f75r vs REGIME_1 mean.
"""

import json
import pandas as pd
import statistics
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load scaffold audit
with open(PROJECT_ROOT / 'results' / 'b_macro_scaffold_audit.json', 'r') as f:
    scaffold_data = json.load(f)

# Load regime mapping
with open(PROJECT_ROOT / 'results' / 'regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

print("=" * 70)
print("TEST C: f75r INVESTIGATION")
print("=" * 70)
print()

# Check f75r's regime
f75r_regime = None
for regime, folios in regime_mapping.items():
    if 'f75r' in folios:
        f75r_regime = regime
        break

print(f"f75r actual REGIME: {f75r_regime}")
print()

# Get f75r features
f75r_features = scaffold_data['features'].get('f75r', {})

print("-" * 70)
print("f75r FEATURES")
print("-" * 70)
print(f"CEI Total:              {f75r_features.get('cei_total', 'N/A'):.3f}")
print(f"Hazard Density:         {f75r_features.get('hazard_density', 'N/A'):.3f}")
print(f"Recovery Ops:           {f75r_features.get('recovery_ops_count', 'N/A')}")
print(f"Intervention Freq:      {f75r_features.get('intervention_frequency', 'N/A'):.3f}")
print(f"Near-miss Count:        {f75r_features.get('near_miss_count', 'N/A')}")
print(f"Kernel k Dominance:     {f75r_features.get('kernel_dominance_k', 'N/A'):.3f}")
print(f"Kernel e Dominance:     {f75r_features.get('kernel_dominance_e', 'N/A'):.3f}")
print()

# Compare f75r to its REGIME peers
print("-" * 70)
print(f"f75r vs {f75r_regime} PEERS")
print("-" * 70)

regime_folios = regime_mapping.get(f75r_regime, [])
regime_features = [scaffold_data['features'][f] for f in regime_folios if f in scaffold_data['features']]

metrics = ['cei_total', 'hazard_density', 'recovery_ops_count', 'intervention_frequency', 'near_miss_count']

for metric in metrics:
    values = [f[metric] for f in regime_features if metric in f]
    mean_val = statistics.mean(values)
    std_val = statistics.stdev(values) if len(values) > 1 else 0
    f75r_val = f75r_features.get(metric, 0)

    z_score = (f75r_val - mean_val) / std_val if std_val > 0 else 0
    outlier = abs(z_score) > 2

    print(f"{metric:25s}: f75r={f75r_val:7.2f}, mean={mean_val:7.2f}, z={z_score:+5.2f} {'<-- OUTLIER' if outlier else ''}")

print()

# Load transcript for MIDDLE analysis
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

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

def extract_middle(token):
    if pd.isna(token):
        return None
    token = str(token)
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break
    if not prefix:
        return None
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
    return middle

df['middle'] = df['word'].apply(extract_middle)
df_b = df[df['language'] == 'B']
df_a = df[df['language'] == 'A']

# Get B vocabulary by folio
b_middles_global = set(df_b['middle'].dropna().unique())
a_middles_global = set(df_a['middle'].dropna().unique())
b_exclusive_global = b_middles_global - a_middles_global

# Analyze f75r vocabulary
print("-" * 70)
print("f75r VOCABULARY ANALYSIS")
print("-" * 70)

# Note: f75r appears to be in Currier A based on language column
f75r_data = df[df['folio'] == 'f75r']
f75r_lang = f75r_data['language'].value_counts().to_dict()
print(f"f75r language distribution: {f75r_lang}")

f75r_middles = set(f75r_data['middle'].dropna().unique())
print(f"f75r unique MIDDLEs: {len(f75r_middles)}")

# Check which are B-exclusive
f75r_b_exclusive = f75r_middles & b_exclusive_global
print(f"f75r MIDDLEs that are B-exclusive globally: {len(f75r_b_exclusive)}")

if f75r_b_exclusive:
    print(f"  Examples: {list(f75r_b_exclusive)[:10]}")

# Compare to REGIME_1 peers
print()
print("-" * 70)
print("f75r vs REGIME_1 PEERS - B-EXCLUSIVE MIDDLE RATE")
print("-" * 70)

b_exclusive_rates = {}
for folio in regime_folios:
    folio_data = df[df['folio'] == folio]
    folio_middles = set(folio_data['middle'].dropna().unique())
    folio_b_excl = folio_middles & b_exclusive_global
    rate = len(folio_b_excl) / len(folio_middles) if folio_middles else 0
    b_exclusive_rates[folio] = {
        'total_middles': len(folio_middles),
        'b_exclusive': len(folio_b_excl),
        'rate': rate
    }

rates = [v['rate'] for v in b_exclusive_rates.values()]
mean_rate = statistics.mean(rates)
std_rate = statistics.stdev(rates) if len(rates) > 1 else 0

f75r_rate = b_exclusive_rates.get('f75r', {}).get('rate', 0)
z_score = (f75r_rate - mean_rate) / std_rate if std_rate > 0 else 0

print(f"f75r B-exclusive rate: {f75r_rate:.3f} ({b_exclusive_rates.get('f75r', {}).get('b_exclusive', 0)}/{b_exclusive_rates.get('f75r', {}).get('total_middles', 0)})")
print(f"REGIME_1 mean rate:    {mean_rate:.3f}")
print(f"REGIME_1 std:          {std_rate:.3f}")
print(f"f75r z-score:          {z_score:+.2f}")

# P3 evaluation (adjusted)
print()
print("=" * 70)
print("P3 EVALUATION (ADJUSTED)")
print("=" * 70)
print("Original: f75r will have higher B-exclusive MIDDLE rate than REGIME_4 mean")
print("Adjusted: f75r will show distinctive characteristics within REGIME_1")
print()
print(f"B-exclusive rate: f75r ({f75r_rate:.3f}) vs REGIME_1 mean ({mean_rate:.3f})")
print(f"Z-score: {z_score:+.2f}")
print(f"Distinctive (|z| > 1.5): {'YES' if abs(z_score) > 1.5 else 'NO'}")

# Top/bottom folios by B-exclusive rate
print()
print("-" * 70)
print("REGIME_1 FOLIOS BY B-EXCLUSIVE RATE")
print("-" * 70)
sorted_folios = sorted(b_exclusive_rates.items(), key=lambda x: x[1]['rate'], reverse=True)
print("Top 5:")
for f, v in sorted_folios[:5]:
    flag = " <-- f75r" if f == 'f75r' else ""
    print(f"  {f}: {v['rate']:.3f} ({v['b_exclusive']}/{v['total_middles']}){flag}")
print("Bottom 5:")
for f, v in sorted_folios[-5:]:
    flag = " <-- f75r" if f == 'f75r' else ""
    print(f"  {f}: {v['rate']:.3f} ({v['b_exclusive']}/{v['total_middles']}){flag}")

# Check if f75r is actually Currier B
print()
print("=" * 70)
print("f75r CURRIER CLASSIFICATION CHECK")
print("=" * 70)

# The regime mapping includes f75r in REGIME_1, which suggests it's treated as B
# Let's check the raw data
f75r_raw = df[df['folio'] == 'f75r']
print(f"f75r row count: {len(f75r_raw)}")
print(f"f75r language values: {f75r_raw['language'].value_counts().to_dict()}")
print(f"f75r in scaffold features: {'f75r' in scaffold_data['features']}")

# Save results
results = {
    'test': 'C_F75R_INVESTIGATION',
    'f75r_regime': f75r_regime,
    'f75r_features': f75r_features,
    'f75r_b_exclusive_rate': f75r_rate,
    'regime1_mean_b_exclusive_rate': mean_rate,
    'regime1_std': std_rate,
    'z_score': z_score,
    'p3_adjusted_result': 'DISTINCTIVE' if abs(z_score) > 1.5 else 'NOT_DISTINCTIVE',
    'b_exclusive_rates_by_folio': b_exclusive_rates
}

output_path = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'test_c_f75r_investigation.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print()
print(f"Results saved to {output_path}")
