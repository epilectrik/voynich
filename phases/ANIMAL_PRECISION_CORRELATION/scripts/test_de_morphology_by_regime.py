#!/usr/bin/env python3
"""
Test D: PREFIX Distribution by REGIME
Test E: Singleton MIDDLE Density by REGIME

Test D - Pre-registered prediction P2 (Medium):
REGIME_4 folios will show ch-prefix enrichment >1.2x vs corpus baseline.

Test E - Exploratory:
REGIME_4 may require more unique discriminators (higher singleton rate).
"""

import json
import pandas as pd
import statistics
from pathlib import Path
from collections import Counter
from scipy import stats

PROJECT_ROOT = Path('C:/git/voynich')
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Load regime mapping
with open(PROJECT_ROOT / 'results' / 'regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

# Invert mapping
folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for f in folios:
        folio_to_regime[f] = regime

# Load transcript
df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_b = df[df['language'] == 'B'].copy()

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
    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
    if middle == '':
        middle = '_EMPTY_'
    return prefix, middle, suffix

df_b['prefix'], df_b['middle'], df_b['suffix'] = zip(*df_b['word'].apply(extract_morphology))
df_b['regime'] = df_b['folio'].map(folio_to_regime)

# Filter to only rows with valid regime
df_b = df_b[df_b['regime'].notna()]

print("=" * 70)
print("TEST D: PREFIX DISTRIBUTION BY REGIME")
print("=" * 70)
print()
print("P2 (Medium): REGIME_4 shows ch-prefix enrichment >1.2x vs baseline")
print()

# Compute global PREFIX distribution
global_prefix_counts = df_b['prefix'].value_counts()
global_total = global_prefix_counts.sum()

print("-" * 70)
print("GLOBAL PREFIX DISTRIBUTION (Currier B)")
print("-" * 70)
for prefix in ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']:
    count = global_prefix_counts.get(prefix, 0)
    pct = count / global_total * 100
    print(f"  {prefix:4s}: {count:5d} ({pct:5.1f}%)")

print()
print("-" * 70)
print("PREFIX DISTRIBUTION BY REGIME")
print("-" * 70)

regime_prefix_data = {}
for regime in sorted(regime_mapping.keys()):
    regime_df = df_b[df_b['regime'] == regime]
    prefix_counts = regime_df['prefix'].value_counts()
    total = prefix_counts.sum()

    regime_prefix_data[regime] = {
        'total': total,
        'counts': prefix_counts.to_dict()
    }

    print(f"\n{regime} (n={total} tokens):")
    for prefix in ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']:
        count = prefix_counts.get(prefix, 0)
        pct = count / total * 100 if total > 0 else 0
        global_pct = global_prefix_counts.get(prefix, 0) / global_total * 100
        ratio = pct / global_pct if global_pct > 0 else 0
        enriched = "+" if ratio > 1.2 else "-" if ratio < 0.8 else "="
        print(f"  {prefix:4s}: {count:4d} ({pct:5.1f}%) [{enriched} {ratio:.2f}x]")

# P2 evaluation: ch-prefix in REGIME_4
print()
print("=" * 70)
print("P2 EVALUATION: ch-prefix enrichment in REGIME_4")
print("=" * 70)

r4_data = regime_prefix_data['REGIME_4']
r4_ch_count = r4_data['counts'].get('ch', 0)
r4_total = r4_data['total']
r4_ch_pct = r4_ch_count / r4_total * 100 if r4_total > 0 else 0

global_ch_pct = global_prefix_counts.get('ch', 0) / global_total * 100
ch_ratio = r4_ch_pct / global_ch_pct if global_ch_pct > 0 else 0

p2_pass = ch_ratio > 1.2

print(f"REGIME_4 ch-prefix: {r4_ch_pct:.1f}%")
print(f"Global ch-prefix:   {global_ch_pct:.1f}%")
print(f"Enrichment ratio:   {ch_ratio:.2f}x")
print(f"P2 Result: {'PASS' if p2_pass else 'FAIL'} (threshold >1.2x)")

# Chi-square test for PREFIX distribution difference
print()
print("-" * 70)
print("CHI-SQUARE TEST: REGIME_4 vs Others PREFIX distribution")
print("-" * 70)

main_prefixes = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']

# Create contingency table: REGIME_4 vs Others
r4_counts = [r4_data['counts'].get(p, 0) for p in main_prefixes]
other_counts = []
for p in main_prefixes:
    other_total = sum(
        regime_prefix_data[r]['counts'].get(p, 0)
        for r in regime_prefix_data if r != 'REGIME_4'
    )
    other_counts.append(other_total)

contingency = [r4_counts, other_counts]
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

print(f"Chi-square: {chi2:.2f}")
print(f"p-value: {p_value:.6f}")
print(f"Significant (p<0.05): {'YES' if p_value < 0.05 else 'NO'}")

print()
print("=" * 70)
print("TEST E: SINGLETON MIDDLE DENSITY BY REGIME")
print("=" * 70)
print()

# Compute singleton MIDDLEs per REGIME
# Singleton = MIDDLE that appears in only one folio

# First, get global MIDDLE-folio mapping
middle_folio_sets = {}
for folio, group in df_b.groupby('folio'):
    for middle in group['middle'].dropna().unique():
        if middle not in middle_folio_sets:
            middle_folio_sets[middle] = set()
        middle_folio_sets[middle].add(folio)

# Identify singletons (appear in exactly 1 folio)
singleton_middles = {m for m, folios in middle_folio_sets.items() if len(folios) == 1}
print(f"Total singleton MIDDLEs in B: {len(singleton_middles)}")
print(f"Total unique MIDDLEs in B: {len(middle_folio_sets)}")
print(f"Global singleton rate: {len(singleton_middles)/len(middle_folio_sets)*100:.1f}%")
print()

print("-" * 70)
print("SINGLETON RATE BY REGIME")
print("-" * 70)

regime_singleton_data = {}
for regime in sorted(regime_mapping.keys()):
    regime_folios = regime_mapping[regime]
    regime_df = df_b[df_b['folio'].isin(regime_folios)]

    # Get unique MIDDLEs in this REGIME
    regime_middles = set(regime_df['middle'].dropna().unique())

    # Count how many are singletons
    regime_singletons = regime_middles & singleton_middles
    singleton_rate = len(regime_singletons) / len(regime_middles) * 100 if regime_middles else 0

    regime_singleton_data[regime] = {
        'total_middles': len(regime_middles),
        'singleton_count': len(regime_singletons),
        'singleton_rate': singleton_rate
    }

    print(f"{regime}: {len(regime_singletons):3d}/{len(regime_middles):3d} singletons ({singleton_rate:5.1f}%)")

# Compare REGIME_4 to others
print()
print("-" * 70)
print("REGIME_4 vs OTHER REGIMES - SINGLETON RATE")
print("-" * 70)

r4_singleton_rate = regime_singleton_data['REGIME_4']['singleton_rate']
other_rates = [regime_singleton_data[r]['singleton_rate'] for r in regime_singleton_data if r != 'REGIME_4']
mean_other_rate = statistics.mean(other_rates)

print(f"REGIME_4 singleton rate: {r4_singleton_rate:.1f}%")
print(f"Other REGIMEs mean:      {mean_other_rate:.1f}%")
print(f"Difference:              {r4_singleton_rate - mean_other_rate:+.1f}%")

# P5 evaluation (exploratory): escape density by REGIME
print()
print("=" * 70)
print("P5 EVALUATION (EXPLORATORY): Escape density by REGIME")
print("=" * 70)

# Load scaffold for escape/intervention data
with open(PROJECT_ROOT / 'results' / 'b_macro_scaffold_audit.json', 'r') as f:
    scaffold_data = json.load(f)

escape_by_regime = {}
for regime, folios in regime_mapping.items():
    escape_values = []
    for f in folios:
        if f in scaffold_data['features']:
            # Use near_miss as proxy for escape-related events
            escape_values.append(scaffold_data['features'][f].get('near_miss_count', 0))

    if escape_values:
        escape_by_regime[regime] = {
            'mean': statistics.mean(escape_values),
            'std': statistics.stdev(escape_values) if len(escape_values) > 1 else 0,
            'n': len(escape_values)
        }

print("\nNear-miss count by REGIME (proxy for escape density):")
for regime in sorted(escape_by_regime.keys()):
    data = escape_by_regime[regime]
    print(f"  {regime}: mean={data['mean']:.1f}, std={data['std']:.1f} (n={data['n']})")

# Check if REGIME_4 has lower escape (as predicted)
r4_escape = escape_by_regime['REGIME_4']['mean']
other_escape = statistics.mean([escape_by_regime[r]['mean'] for r in escape_by_regime if r != 'REGIME_4'])
print(f"\nREGIME_4 escape: {r4_escape:.1f}")
print(f"Other REGIMEs:   {other_escape:.1f}")
print(f"Ratio (R4/other): {r4_escape/other_escape:.2f}x")
print(f"P5 prediction (lower in R4): {'SUPPORTED' if r4_escape < other_escape else 'NOT SUPPORTED'}")

# Convert numpy types for JSON
def convert_for_json(obj):
    import numpy as np
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

# Save results
results = {
    'test_d_prefix_distribution': {
        'global_distribution': {p: int(global_prefix_counts.get(p, 0)) for p in main_prefixes},
        'by_regime': {
            regime: {
                'total': int(data['total']),
                'counts': {p: int(data['counts'].get(p, 0)) for p in main_prefixes}
            }
            for regime, data in regime_prefix_data.items()
        },
        'p2_evaluation': {
            'regime4_ch_pct': r4_ch_pct,
            'global_ch_pct': global_ch_pct,
            'enrichment_ratio': ch_ratio,
            'result': 'PASS' if p2_pass else 'FAIL'
        },
        'chi_square': {
            'chi2': chi2,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    },
    'test_e_singleton_density': {
        'global_singleton_rate': len(singleton_middles)/len(middle_folio_sets)*100,
        'by_regime': regime_singleton_data,
        'regime4_vs_others': {
            'regime4_rate': r4_singleton_rate,
            'other_mean_rate': mean_other_rate,
            'difference': r4_singleton_rate - mean_other_rate
        }
    },
    'p5_escape_density': {
        'by_regime': escape_by_regime,
        'regime4_vs_others': {
            'regime4': r4_escape,
            'other_mean': other_escape,
            'ratio': r4_escape/other_escape,
            'supported': r4_escape < other_escape
        }
    }
}

output_path = PROJECT_ROOT / 'phases' / 'ANIMAL_PRECISION_CORRELATION' / 'results' / 'test_de_morphology.json'

import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NpEncoder, self).default(obj)

with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)

print()
print(f"Results saved to {output_path}")
